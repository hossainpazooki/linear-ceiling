# 0023's pipeline-identity control scores one dump against itself, so its zero is the scorer's arithmetic and cannot fail on the box

kills: (nothing)
ts: 2026-09-03T04:04:22Z
commit: 5960c20
session: linear-ceiling-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: verified
fact: `run_controls` calls `score_pairs(..., same_tgt="same_src")` at pairs (p, p), and the upstream
`score_same` reads `K_stripped` / `V` rows from `src` and `tgt`, which are then the same `KVDump`
loaded twice. Identical rows subtracted give exactly zero whatever the GPU did, so the control
proves only that the dump loads, the shapes agree and the per-token record sums. It cannot detect a
non-deterministic or wrong prefill. Entry 0025 keeps it and adds the prefix-invariance control
(prefill S followed by R's first token; rows 0..|S|−1 vs the S dump, max centered δ ≤ 1e-4, HALT
above), which is a statement about the box. Independent review finding 3 (2026-09-02); confirmed at
source before it was written down.
basis: `grep -n 'same_tgt="same_src"' src/linear_ceiling/e9.py` -> `176: cross=False, same_tgt="same_src", runner=runner)`;
`grep -n -A4 '^def score_same' ../kv-transfer-replication/scripts/score_positions.py` -> `Yhat = _rows(src, kind, l, p_s)` against `tgt` rows at `p_r`, both dumps supplied by path.
re-verify: `grep -n 'same_tgt="same_src"' src/linear_ceiling/e9.py && grep -n 'same_src_plus1' src/linear_ceiling/e9.py | head -2` (expect the identity call and the S+1 dump beside it).
