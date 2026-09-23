# The bridge value-R² median 0.8603 printed in the manuscript is a summary-file figure that no ledger entry or paper outline states

kills: (nothing)
ts: 2026-09-14T09:29:08.304Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: `results/e9l/summary.json` gives the three 0036 bridge handoffs' value R² as 0.8682, 0.8489 and 0.8603, median 0.8603.
The 2026-09-14 manuscript prints that median as `\bridgeRtwoV`. `grep` finds 0.8603 in neither `ledger/ledger.md` nor
`docs/paper/*.md`. Outline v3's gate admits a figure only when a numbered entry states it, so this number is correct and
still ungated. `results/` is gitignored: the summary exists on this machine and in the E9-long HF backup, not in git.
basis: `python -c "...bridge per_handoff..."` printed `bridge r2_V per handoff [0.8682, 0.8489, 0.8603] median 0.8603`;
  `grep -n "0\.8603" ledger/ledger.md docs/paper/*.md` printed nothing, `rc=1`.
re-verify: .venv/Scripts/python.exe -c "import json,statistics as s;b=json.load(open('results/e9l/summary.json'))['bridge']['per_handoff'];print(round(s.median(v['r2_V'] for v in b.values()),4))"; grep -n "0\.8603" ledger/ledger.md docs/paper/*.md   # 0.8603, then no grep output
