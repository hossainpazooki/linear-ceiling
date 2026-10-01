# The per-token mean equals 1 − R² only to the float32 sum tolerance; a 1e-9 gate refuses a correct record

ts: 2026-10-01T04:47:28Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: Entry 0023 states that the token mean of the centered deviation is exactly 1 − the recorded layer-mean R². In
the record it is exact only in float64 arithmetic over float32 squares: the per-token file stores float32 squares and
the report stores float64 moments, so the identity holds to the summarizer's own `_SUM_TOL` (1e-5 relative), not to
the last bit. On the synthetic fixture the mismatch was 8e-9 relative (0.375000008 vs 0.375000000) and a 1e-9 gate in
the first `e9_tail` refused a correct record; on the real long cell the worst mismatch over 35 handoffs is 1.0e-10.
`e9_tail` now checks the identity at `_SUM_TOL`, the tolerance `_check_tokens` already uses for the same reason.
basis: at 0a51275, 2026-10-01T04:47:28Z, a read of `results/e9l/tail.json` against `results/e9l/report.json` printed
  `worst rel diff over 35 handoffs: 1.02e-10 (SUM_TOL 1e-5)`. The fixture failure was captured under the WSL venv
  earlier in the session (pre-commit tree of the same module): `ValueError: 20241016_composio_x/a_traj#1: same_K token
  mean 0.375000008 != 1 - recorded R^2 0.375000000`.
re-verify: grep -n "rel_tol=_SUM_TOL" src/linear_ceiling/e9_tail.py   # expect one hit; the identity is gated at the summarizer's sum tolerance
