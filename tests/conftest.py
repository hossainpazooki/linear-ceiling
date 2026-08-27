import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
import torch
from safetensors.torch import save_file

from linear_ceiling.config import ArtifactRoot, SealConfig

GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.com"]

CFG = {"hidden_size": 32, "num_hidden_layers": 2, "num_attention_heads": 4, "num_key_value_heads": 2,
       "head_dim": 8, "rope_theta": 10000.0, "vocab_size": 16}


def tiny_snapshot(tmp_path, name="m", *, sharded=False, cfg=CFG, vocab_words=None, seed=0,
                  k_proj=None, v_proj=None, embed=None):
    """A minimal on-disk safetensors snapshot for WeightReader, shared by every test module
    that needs one. `k_proj`/`v_proj` are optional dicts {layer: ndarray[n_kv*d_h, hidden]}
    overriding the random tensors; `embed` is an optional ndarray[vocab, hidden] overriding
    the random embedding table. All overrides are rounded and cast to bf16 on save, so pass
    bf16-representable values (the float32 read-back is then exact)."""
    d = tmp_path / name
    d.mkdir()
    (d / "config.json").write_text(json.dumps(cfg))
    words = vocab_words or [f"t{i}" for i in range(cfg["vocab_size"])]
    (d / "tokenizer.json").write_text(json.dumps({"model": {"vocab": {w: i for i, w in enumerate(words)}}}))
    g = torch.Generator().manual_seed(seed)
    kvd = cfg["num_key_value_heads"] * cfg["head_dim"]
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
        t[f"model.layers.{l}.self_attn.k_norm.weight"] = torch.ones(cfg["head_dim"]) * 0.5
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
