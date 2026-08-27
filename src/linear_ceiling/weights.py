"""Read Qwen3 projection weights straight from safetensors -- no model object, no forward
pass. bf16 is read through torch (numpy has no bf16) and returned as float32."""
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from safetensors import safe_open

_K = "model.layers.{l}.self_attn.k_proj.weight"
_V = "model.layers.{l}.self_attn.v_proj.weight"
_KN = "model.layers.{l}.self_attn.k_norm.weight"
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


def spec_from_config(cfg: dict, model_id: str) -> ModelSpec:
    """Provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/pairs.py (kv_shape,
    _rope_theta), commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: head_dim if present
    else hidden/heads; rope_theta may live under rope_parameters (transformers 5); a missing
    theta raises rather than defaults."""
    d_h = cfg.get("head_dim") or cfg["hidden_size"] // cfg["num_attention_heads"]
    rp = cfg.get("rope_parameters")
    if isinstance(rp, dict) and "rope_theta" in rp:
        theta = float(rp["rope_theta"])
    elif cfg.get("rope_theta") is not None:
        theta = float(cfg["rope_theta"])
    else:
        raise ValueError("cannot determine rope_theta from config")
    return ModelSpec(model_id, int(cfg["hidden_size"]), int(cfg["num_hidden_layers"]),
                     int(cfg["num_attention_heads"]), int(cfg["num_key_value_heads"]), int(d_h),
                     theta, int(cfg["vocab_size"]))


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

    def k_proj(self, l: int) -> np.ndarray: return self._get(_K.format(l=self._layer(l)))
    def v_proj(self, l: int) -> np.ndarray: return self._get(_V.format(l=self._layer(l)))
    def k_norm(self, l: int) -> np.ndarray: return self._get(_KN.format(l=self._layer(l)))
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
