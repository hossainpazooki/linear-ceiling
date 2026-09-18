"""Read a decoder's projection weights straight from safetensors -- no model object, no forward
pass. Family-neutral over Qwen3 and Llama-3: both lay the tensors out as
`model.layers.<l>.self_attn.*`, and the one place they differ is QK-norm, which Qwen3 has and
Llama-3 does not carry at all (see `k_norm`/`q_norm`/`has_qk_norm`). bf16 is read through torch
(numpy has no bf16) and returned as float32."""
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from safetensors import safe_open

_K = "model.layers.{l}.self_attn.k_proj.weight"
_V = "model.layers.{l}.self_attn.v_proj.weight"
_KN = "model.layers.{l}.self_attn.k_norm.weight"   # Qwen3 only; absent from every Llama-3 checkpoint
_QN = "model.layers.{l}.self_attn.q_norm.weight"   # Qwen3 only, same
_LN = "model.layers.{l}.input_layernorm.weight"
_EMB = "model.embed_tokens.weight"


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    hidden: int
    n_layers: int
    n_heads: int
    n_kv: int
    d_h: int
    rope_theta: float
    vocab: int
    # Every RoPE key the config declares except the theta itself, verbatim, or None when it
    # declares none. Recorded because rope_theta alone is TRUE but INSUFFICIENT once
    # rope_type != "default": Llama-3's "llama3" scaling rescales the low-frequency bands, so
    # two models can share theta = 5e5 and still build different inverse-frequency vectors.
    # Recorded, never interpreted here -- the authority on a dump's actual frequencies is the
    # RopeSpec the upstream reads off the loaded model. Defaulted so the field is additive.
    # (A dict makes the frozen spec unhashable; nothing hashes a ModelSpec.)
    rope_scaling: dict | None = None


def spec_from_config(cfg: dict, model_id: str) -> ModelSpec:
    """Provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/pairs.py (kv_shape,
    _rope_theta), commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: head_dim if present
    else hidden/heads; rope_theta may live under rope_parameters (transformers 5); a missing
    theta raises rather than defaults.

    The scaling block travels with the theta, so it is read from whichever form the config uses:
    transformers 4 keeps it in `rope_scaling`, transformers 5 folds it into `rope_parameters`
    beside the theta. Note that the transformers 5 form states the unscaled case explicitly, so
    an un-scaled model records `{"rope_type": "default"}` rather than None -- a caller asking
    "is this model scaled?" must test rope_type, not None-ness."""
    d_h = cfg.get("head_dim") or cfg["hidden_size"] // cfg["num_attention_heads"]
    rp = cfg.get("rope_parameters")
    if isinstance(rp, dict) and "rope_theta" in rp:
        theta = float(rp["rope_theta"])
        scaling = {k: v for k, v in rp.items() if k != "rope_theta"} or None
    elif cfg.get("rope_theta") is not None:
        theta = float(cfg["rope_theta"])
        scaling = dict(cfg["rope_scaling"]) if isinstance(cfg.get("rope_scaling"), dict) else None
    else:
        raise ValueError("cannot determine rope_theta from config")
    return ModelSpec(model_id, int(cfg["hidden_size"]), int(cfg["num_hidden_layers"]),
                     int(cfg["num_attention_heads"]), int(cfg["num_key_value_heads"]), int(d_h),
                     theta, int(cfg["vocab_size"]), scaling)


def snapshot(model_id: str, cache_dir: Path | None = None) -> Path:
    from huggingface_hub import snapshot_download   # the package's only network call
    return Path(snapshot_download(model_id, cache_dir=cache_dir, allow_patterns=["*.safetensors", "*.json"]))


class WeightReader:
    def __init__(self, snapshot_dir: Path, model_id: str | None = None):
        self.dir = Path(snapshot_dir)
        cfg = json.loads((self.dir / "config.json").read_text(encoding="utf-8"))
        self.spec = spec_from_config(cfg, model_id or cfg.get("_name_or_path", self.dir.name))
        index = self.dir / "model.safetensors.index.json"
        if index.exists():
            wm = json.loads(index.read_text(encoding="utf-8"))["weight_map"]
            self._shard = {k: self.dir / v for k, v in wm.items()}
        else:
            single = self.dir / "model.safetensors"
            if not single.exists():
                raise FileNotFoundError(f"no model.safetensors or index in {self.dir}")
            with safe_open(str(single), framework="pt") as f:
                self._shard = {k: single for k in f.keys()}

    def _get(self, name: str) -> np.ndarray:
        if name not in self._shard:
            raise KeyError(f"{name} not in checkpoint {self.dir}")
        with safe_open(str(self._shard[name]), framework="pt") as f:
            return f.get_tensor(name).float().numpy()

    def _layer(self, l: int) -> int:
        if not 0 <= l < self.spec.n_layers:
            raise IndexError(f"layer {l} out of range for {self.spec.n_layers} layers")
        return l

    def _qk_norm(self, tmpl: str, which: str, l: int) -> np.ndarray:
        """Qwen3 normalises Q and K per head; Llama-3 has no such tensors anywhere in the
        checkpoint. That is a statement about the architecture, not a missing key or a typo, so
        say which family the caller is holding rather than raising a bare KeyError from _get --
        and never fall back to an identity gain, which would return a silently wrong answer."""
        name = tmpl.format(l=self._layer(l))
        if name not in self._shard:
            raise ValueError(
                f"model {self.spec.model_id} has no self_attn.{which} (QK-norm is a Qwen3 "
                f"feature; Llama-3 checkpoints carry neither q_norm nor k_norm): {name} is not "
                f"in {self.dir}")
        return self._get(name)

    def has_qk_norm(self) -> bool:
        """Whether this checkpoint carries per-head Q/K norms at all (Qwen3 yes, Llama-3 no).
        Reads the shard map, not the tensors."""
        return _QN.format(l=0) in self._shard and _KN.format(l=0) in self._shard

    def k_proj(self, l: int) -> np.ndarray: return self._get(_K.format(l=self._layer(l)))
    def v_proj(self, l: int) -> np.ndarray: return self._get(_V.format(l=self._layer(l)))
    def k_norm(self, l: int) -> np.ndarray: return self._qk_norm(_KN, "k_norm", l)
    def q_norm(self, l: int) -> np.ndarray: return self._qk_norm(_QN, "q_norm", l)
    def input_layernorm(self, l: int) -> np.ndarray: return self._get(_LN.format(l=self._layer(l)))
    def embed(self) -> np.ndarray: return self._get(_EMB)

    def heads(self, W: np.ndarray) -> np.ndarray:
        """[n_kv*d_h, hidden] -> [n_kv, d_h, hidden]; head h owns rows h*d_h:(h+1)*d_h."""
        return W.reshape(self.spec.n_kv, self.spec.d_h, self.spec.hidden)

    def vocab_map(self) -> dict[str, int]:
        tok = json.loads((self.dir / "tokenizer.json").read_text(encoding="utf-8"))
        return tok["model"]["vocab"]


def assert_shared_vocab(a: WeightReader, b: WeightReader) -> None:
    """Provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/models.py
    (assert_shared_tokenizer), commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: compare
    the vocab maps, not tokenizer names."""
    va, vb = a.vocab_map(), b.vocab_map()
    if va != vb:
        raise ValueError(f"vocab maps differ: {len(va)} vs {len(vb)} entries or different mapping")
