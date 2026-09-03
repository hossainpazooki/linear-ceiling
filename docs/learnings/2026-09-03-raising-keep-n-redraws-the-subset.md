# Raising the keep-subset n under the same seed draws a different set, not a superset

kills: (nothing)
ts: 2026-09-03T04:04:20Z
commit: 5960c20
session: linear-ceiling-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: verified
fact: `e9.keep_subset` draws with `rng.choice(len(ids), size=n, replace=False)` from one seeded
generator. numpy's without-replacement draw is not nested across sizes: the n = 3 and n = 8 draws
from the same seed over the same sorted ids share only what chance gives them (1 of 3 on the real
25 included handoffs; 1 of 3 on a synthetic 25). So "raise n" means "replace the set", and any doc
that named the old handoffs (the GPU runbook did) is stale the moment n changes. Entry 0025 states
both draws for that reason; `tests/test_e9.py::test_keep_subset_redraw_at_a_larger_n_is_not_nested`
pins it. If a future amendment must PRESERVE a draw, it needs a second seeded draw from the
remainder, not a larger n.
basis: `python -c "from linear_ceiling.e9 import keep_subset; ids=[f'h{i:02d}' for i in range(25)]; a,b=keep_subset(ids,9,3),keep_subset(ids,9,8); print(a); print(b); print('nested:', set(a)<=set(b))"` ->
`['h09', 'h20', 'h24']` / `['h02', 'h06', 'h07', 'h13', 'h16', 'h19', 'h23', 'h24']` / `nested: False`.
re-verify: `.venv/Scripts/python.exe -c "from linear_ceiling.e9 import keep_subset; ids=[f'h{i:02d}' for i in range(25)]; print(set(keep_subset(ids,9,3))<=set(keep_subset(ids,9,8)))"` (expect False).
