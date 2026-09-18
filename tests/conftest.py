import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
import torch
from safetensors.torch import save_file

from linear_ceiling.config import ArtifactRoot, SealConfig

GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.com"]

# A Qwen3-shaped config: head_dim declared, no rope_scaling, and (via tiny_snapshot's default)
# the per-head q_norm/k_norm tensors Qwen3 carries.
CFG = {"hidden_size": 32, "num_hidden_layers": 2, "num_attention_heads": 4, "num_key_value_heads": 2,
       "head_dim": 8, "rope_theta": 10000.0, "vocab_size": 16}

# Llama-3-shaped configs, scaled down to the same toy dims as CFG so either family can stand in
# anywhere a snapshot is needed. The fields follow the shape of the real pair
# meta-llama/Llama-3.2-3B (source) -> meta-llama/Llama-3.1-8B (receiver), which IS matched-KV --
# same n_kv and same head_dim on both sides, here 2 x 8 -- and the three ways the two sides
# nonetheless differ on disk, each of which is a thing a reader can get wrong:
#   * the receiver declares NO head_dim (the real 8B does not either; 128 comes from
#     hidden_size // num_attention_heads), the source declares one;
#   * both carry rope_type "llama3" but with DIFFERENT factors, so a check that asserts the two
#     sides' rope_scaling are equal would refuse a correct pair;
#   * tie_word_embeddings differs (true on the source, false on the receiver).
# Only those differences are load-bearing here. The literal factors below are placeholders for
# the real ones, which are the gated repos' to state and tools/preflight_pair.py's to read --
# nothing in this file is evidence about a released checkpoint. Neither config gets q_norm or
# k_norm: Llama-3 has no QK-norm at all (see WeightReader.k_norm).
LLAMA_SRC_CFG = {"hidden_size": 24, "num_hidden_layers": 2, "num_attention_heads": 3,
                 "num_key_value_heads": 2, "head_dim": 8, "rope_theta": 500000.0, "vocab_size": 16,
                 "max_position_embeddings": 131072, "tie_word_embeddings": True,
                 "rope_scaling": {"rope_type": "llama3", "factor": 32.0, "low_freq_factor": 1.0,
                                  "high_freq_factor": 4.0, "original_max_position_embeddings": 8192}}
LLAMA_TGT_CFG = {"hidden_size": 32, "num_hidden_layers": 2, "num_attention_heads": 4,
                 "num_key_value_heads": 2, "rope_theta": 500000.0, "vocab_size": 16,
                 "max_position_embeddings": 131072, "tie_word_embeddings": False,
                 "rope_scaling": {"rope_type": "llama3", "factor": 8.0, "low_freq_factor": 1.0,
                                  "high_freq_factor": 4.0, "original_max_position_embeddings": 8192}}


def tiny_snapshot(tmp_path, name="m", *, sharded=False, cfg=CFG, vocab_words=None, seed=0,
                  k_proj=None, v_proj=None, embed=None, qk_norm=True):
    """A minimal on-disk safetensors snapshot for WeightReader, shared by every test module
    that needs one. `k_proj`/`v_proj` are optional dicts {layer: ndarray[n_kv*d_h, hidden]}
    overriding the random tensors; `embed` is an optional ndarray[vocab, hidden] overriding
    the random embedding table. All overrides are rounded and cast to bf16 on save, so pass
    bf16-representable values (the float32 read-back is then exact).

    `qk_norm=False` writes no q_norm/k_norm tensors, which is the Llama-3 layout (pass it with
    cfg=LLAMA_*_CFG). head_dim is derived exactly as spec_from_config derives it, so a config
    that declares none -- the real Llama-3.1-8B does not -- still builds the right shapes."""
    d = tmp_path / name
    d.mkdir()
    (d / "config.json").write_text(json.dumps(cfg))
    words = vocab_words or [f"t{i}" for i in range(cfg["vocab_size"])]
    (d / "tokenizer.json").write_text(json.dumps({"model": {"vocab": {w: i for i, w in enumerate(words)}}}))
    g = torch.Generator().manual_seed(seed)
    d_h = cfg.get("head_dim") or cfg["hidden_size"] // cfg["num_attention_heads"]
    kvd = cfg["num_key_value_heads"] * d_h
    def _from_array(a):
        # .T-derived overrides are non-contiguous and may alias another override's memory
        # (e.g. the same array passed for every layer); safetensors requires contiguous,
        # independently-owned storage per tensor.
        return torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32).copy())

    if embed is not None:
        emb = _from_array(embed)
    else:
        emb = torch.randn(cfg["vocab_size"], cfg["hidden_size"], generator=g)
    t = {"model.embed_tokens.weight": emb}
    for l in range(cfg["num_hidden_layers"]):
        if k_proj is not None and l in k_proj:
            t[f"model.layers.{l}.self_attn.k_proj.weight"] = _from_array(k_proj[l])
        else:
            t[f"model.layers.{l}.self_attn.k_proj.weight"] = torch.randn(kvd, cfg["hidden_size"], generator=g)
        if v_proj is not None and l in v_proj:
            t[f"model.layers.{l}.self_attn.v_proj.weight"] = _from_array(v_proj[l])
        else:
            t[f"model.layers.{l}.self_attn.v_proj.weight"] = torch.randn(kvd, cfg["hidden_size"], generator=g)
        if qk_norm:
            t[f"model.layers.{l}.self_attn.k_norm.weight"] = torch.ones(d_h) * 0.5
            t[f"model.layers.{l}.self_attn.q_norm.weight"] = torch.ones(d_h) * 0.25
        t[f"model.layers.{l}.input_layernorm.weight"] = torch.ones(cfg["hidden_size"]) * 2.0
    # round to bf16-representable values so the float32 read-back is exact
    t = {k: v.to(torch.bfloat16) for k, v in t.items()}
    if not sharded:
        save_file(t, str(d / "model.safetensors"))
    else:
        keys = sorted(t)
        a, b = {k: t[k] for k in keys[: len(keys) // 2]}, {k: t[k] for k in keys[len(keys) // 2:]}
        save_file(a, str(d / "model-00001-of-00002.safetensors"))
        save_file(b, str(d / "model-00002-of-00002.safetensors"))
        wm = {k: "model-00001-of-00002.safetensors" for k in a} | {k: "model-00002-of-00002.safetensors" for k in b}
        (d / "model.safetensors.index.json").write_text(json.dumps({"weight_map": wm}))
    return d, {k: v.float().numpy() for k, v in t.items()}


@pytest.fixture
def llama_snapshots(tmp_path):
    """The (source, receiver) pair of Llama-shaped snapshots as two directories: no QK-norm
    tensors, the receiver's head_dim undeclared, different rope_scaling factors, matched KV
    geometry, and -- since both take tiny_snapshot's default vocabulary -- one shared vocab
    map, so assert_shared_vocab passes over the pair."""
    s, _ = tiny_snapshot(tmp_path, "llama_src", cfg=LLAMA_SRC_CFG, qk_norm=False, seed=0)
    t, _ = tiny_snapshot(tmp_path, "llama_tgt", cfg=LLAMA_TGT_CFG, qk_norm=False, seed=1)
    return s, t


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *GIT_ID, *args], cwd=repo, check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path) -> Path:
    """A fresh git repo with one commit, plus the artifact roots the seal config points at."""
    r = tmp_path / "repo"
    (r / "ledger" / "predictions").mkdir(parents=True)
    (r / "mappers").mkdir()
    (r / "results" / "mapper").mkdir(parents=True)
    up = tmp_path / "upstream"
    (up / "mappers").mkdir(parents=True)
    (up / "results" / "mapper").mkdir(parents=True)
    git(r, "init", "-q", "-b", "main")
    (r / "README.md").write_text("x\n")
    git(r, "add", "README.md")
    git(r, "commit", "-q", "-m", "init")
    return r


@pytest.fixture
def seal_cfg(repo) -> SealConfig:
    up = repo.parent / "upstream"
    return SealConfig(
        predictions_dir=repo / "ledger" / "predictions",
        upstream_path=up,
        artifact_roots=(
            ArtifactRoot(repo / "mappers", "{pair}/**/k*.safetensors"),
            ArtifactRoot(repo / "results" / "mapper", "{pair}/**/r2.json"),
            ArtifactRoot(up / "mappers", "{pair}/**/k*.safetensors"),
            ArtifactRoot(up / "results" / "mapper", "{pair}/**/r2.json"),
        ),
    )


def commit_all(repo: Path, msg: str = "seal") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
