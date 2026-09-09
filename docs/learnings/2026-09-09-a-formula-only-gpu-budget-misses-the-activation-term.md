# A formula-only GPU memory budget (KV bytes + weights) undercounts the real peak by an activation term that grows with length

kills: (nothing)
ts: 2026-09-09T03:57:39.516Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: The E9-long seed's first budget was KV bytes per token (28 layers × 2 × 8 KV heads × 128 × 4 B =
229,376 B in float32) times T, plus 6.8 GiB of float32 weights: 13.8 GiB at T = 32,768. The R2 ladder
measured on the same pinned path (`sdpa_repeat_kv`, `logits_to_keep=1`, memory-efficient kernel) gave
16.72 GiB at T = 32,768, so about 3 GiB of activations and workspace sit on top of the formula at 32K,
and the 0.6B ladder's slope (10.91 → 13.07 GiB over 8,192 tokens, ≈ 283 KB/token against 229 KB/token
of KV) shows the extra term grows with T. Protocol R2 already says "budget the forward, not the
parameters"; this is the same lesson one level down: the KV formula is a floor, not a budget, and the
slice request must carry a measured peak at the real T. The seed's §1 now labels its 29 GiB figure at
T = 80,111 as an extrapolation from the ladder, pending the probe at that T.
basis: `docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.out` (committed 7202c90) ->
  `{"model": "Qwen/Qwen3-1.7B", "T": 32768, "peak_GiB": 16.72, "s": 22.5, "ok": true}`; formula recomputed at
  4eafe40: `formula_GiB_at_32768 7.0 +6.8 weights = 13.8`.
re-verify: grep -c '"T": 32768, "peak_GiB": 16.72' docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.out   # 1
