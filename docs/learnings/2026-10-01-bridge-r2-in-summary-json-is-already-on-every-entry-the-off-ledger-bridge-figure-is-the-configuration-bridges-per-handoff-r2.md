# `bridge_r2` in summary.json is Bridge R² (A5), already on every cell's entry; the off-ledger "bridge R² 0.8932 / 0.8603" is the configuration bridge's per-handoff R²

ts: 2026-10-01T20:05:00Z
commit: 36e0621
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: The audit's off-ledger manuscript figure "bridge R² K 0.8932 / V 0.8603" is not `summary.json`'s `bridge_r2` (that key is the A5 head- and layer-averaged Bridge R² over all scored handoffs, which 0029, 0036, 0038 and 0044 each already state). It is `summary.json` `bridge.per_handoff[<hid>].r2_K / r2_V` on the three configuration-bridge handoffs of e9l (K 0.8992 / 0.8821 / 0.8932, V 0.8682 / 0.8489 / 0.8603), which no entry states: 0036 gives those handoffs' f* and median delta only. The corrective entry states the per-handoff values and leaves `bridge_r2` alone.
basis: at 36e0621, ~20:05Z: a python read of `results/e9l/summary.json` printed `bridge.per_handoff` with `r2_K 0.8992 / r2_V 0.8682`, `0.8821 / 0.8489`, `0.8932 / 0.8603` for the three handoffs and `bridge_r2 same_K (35, 0.8894)`; `grep -n -E "0\.8992|0\.8821|0\.8932|0\.8603" ledger/ledger.md` printed nothing; `awk 'NR>=2174 && NR<=2233' ledger/ledger.md | grep -c -i "Bridge R²"` printed 1 for 0036 (likewise 1 for 0038 and 0044; 0029 at line 1799). (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: git show 20a4e71:ledger/ledger.md | awk '/0\.8932/{n++} END{print n+0}'   # expect 0 on the pre-0045 ledger
