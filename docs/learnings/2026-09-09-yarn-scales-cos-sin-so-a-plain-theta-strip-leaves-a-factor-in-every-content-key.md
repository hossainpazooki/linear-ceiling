# YaRN multiplies cos/sin by an attention factor, so a plain-θ RoPE strip leaves a wrong rotation AND a factor m in every content-space K

kills: (nothing)
ts: 2026-09-09T21:22:00Z
commit: 407a38e (linear-ceiling) / 4633718 + uncommitted RoPE-spec change (upstream)
session: dev-47 (9c42735d)
status: verified
fact: The seed said "YaRN is an upstream code change" and meant the inverse frequencies. It is two changes.
transformers 5.15.1 `Qwen3RotaryEmbedding.forward` returns `cos = emb.cos() * self.attention_scaling` with
attention_scaling = 0.1·ln(factor) + 1 (1.0916 at factor 2.5), so the K a scaled model writes into its cache is
m·R_yarn(pos)·k_content. The upstream's `strip_rope_tokens_first(K, positions, theta)` would then (a) rotate by
the wrong frequencies and (b) leave the factor m in every content-space K, and the mapper fit on native content
K would read a 9% norm change as content shift. The fix that survived refutation reads the spec from the model's
own rotary embedding (`inv_freq` + `attention_scaling`, never a formula), records it in the dump's meta.json,
halt-checks it against the model at every dumped position before the first forward (atol 1e-5), and strips as
R^T/m. Measured: divide-once residual 9.5e-7; zero or two divisions ~0.5; spec cos/sin bitwise equal to HF over
all 81,920 positions of the real Qwen3-0.6B config; archived dumps strip bit-identically. Still plain-θ, by
design and named in entry 0035: `kvt/mapper.py::apply_mapper` (the live-cache eval path), which E9 never calls.
basis: `.venv/Scripts/python.exe -c "from transformers.models.qwen3.modeling_qwen3 import Qwen3RotaryEmbedding;
  from transformers import Qwen3Config; c=Qwen3Config(hidden_size=64,num_attention_heads=4,num_key_value_heads=2,
  head_dim=16,rope_theta=1e6,max_position_embeddings=40960,rope_scaling={'rope_type':'yarn','factor':2.5,
  'original_max_position_embeddings':32768}); print(Qwen3RotaryEmbedding(c).attention_scaling)"` in the upstream
  venv -> 1.0916290731874154; skeptic-verifier report 2026-09-09 (four attacks, numbers above).
re-verify: cd ../kv-transfer-replication && .venv/Scripts/python.exe -m pytest -q tests/test_rope_spec.py   # 8 passed; test_yarn_spec_strip_is_exact_inverse_at_scaled_positions asserts the plain-theta strip is wrong
