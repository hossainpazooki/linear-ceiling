# A scaled-RoPE (YaRN) receiver is an upstream code change, not a config change: the RoPE strip is plain-θ

kills: (nothing)
ts: 2026-09-09T03:57:39.378Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: The E8/E9 mapper works in content space (`K_stripped`), which the upstream produces by rotating RoPE
off the dumped K with `kvt/rope.py::rope_cos_sin(positions, d_h, theta)`. That function computes
`inv_freq` from `theta` alone, i.e. plain RoPE. Under YaRN (the only way Qwen3-1.7B, native cap 40,960,
reaches 80K positions) the model's own rotary embedding uses per-dimension interpolated frequencies and
an attention factor, so stripping with the plain-θ cos/sin would leave a position-dependent residual in
"content space" and the mapper would be scored against the wrong tensor. `kvt/models.py::load_model`
also passes no `rope_scaling`. Reaching the long half therefore needs an upstream commit (cos/sin taken
from the model's `rotary_emb` or re-derived and halt-tested against it, plus a `load_model` argument and
a `dump_kv` flag), a registration entry and a re-pin, before any request for hardware. A `context_cap`
edit in `config/e9l.toml` alone would run the model outside its trained range and strip incorrectly.
basis: at upstream HEAD 4633718: `grep -n "inv_freq\|^def rope_cos_sin" kvt/rope.py` ->
  `5:def rope_cos_sin(positions: torch.Tensor, d_h: int, theta: float, dtype=torch.float32):` /
  `6:    inv_freq = 1.0 / (theta ** (torch.arange(0, d_h, 2, dtype=torch.float32) / d_h))`;
  `grep -c rope_scaling kvt/models.py` -> `0`. Hub configs (curl 2026-09-08): both Qwen3-0.6B and 1.7B have
  `max_position_embeddings 40960`, `rope_scaling null`.
re-verify: cd ~/dev/kv-transfer-replication && grep -c "inv_freq = 1.0 / (theta" kvt/rope.py && grep -c rope_scaling kvt/models.py   # 1 then 0 until the YaRN commit lands
