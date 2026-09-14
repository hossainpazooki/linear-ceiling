# `e9 --check` prints ready for a new E9 cell that has no `calibration/tau.json` of its own; only `summarize_e9` refuses on it, and only after the GPU run

kills: (nothing)
ts: 2026-09-14T03:09:12Z
commit: 12c113c2f9b0e32e6e74e340e266ff9e2a5f5acd
session: e9l-aws-run (01VDywUv8N146LzzLgRDTihm)
status: verified
fact: `summarize_e9` requires `<results_dir>/calibration/tau.json` for the cell it summarizes (`_check_calibration`,
0023) and tells the operator to write it "before the GPU run". The pre-run gate does not look for it: `e9.py` has no
calibration or tau.json check, so the E9 scaled short cell's gate printed `E9 gate: ready (… config/e9s.toml)` at
home and again from a fresh clone on the box, the run finished 25 of 25, and the first reader refused with
`results\e9s\calibration\tau.json does not exist`. E9-long had passed only because its sitting ran
`summarize_e9 --calibrate-tau --config config/e9l.toml` on 09-09 as a separate step (`results/e9l/calibration/`,
dated the day before its run); the e9s runbook copied the sitting's shape from that runbook's steps, which do not
name the calibration. The ordering slip moves no figure: `calibrate_tau` reads only the upstream mapper, the archived
generic dumps, the archived `r2.json` and E8's report, and the summarizer recomputes it and refuses unless it equals
the τ committed in config. A new cell's checklist names `--calibrate-tau --config config/<exp>.toml` before launch,
or the gate learns to refuse without it.
basis: `results/e9s/logs/summarize_e9.20260914T030912Z.log` (`E9 SUMMARY REFUSED: …tau.json does not exist; run
  summarize_e9 --calibrate-tau before the GPU run (0023)`, rc 1); the fresh-clone gate line in
  `results/e9s/logs/box/setup.log`; `ls results/e9l/calibration/` (tau.json 2026-09-09 18:56 local).
re-verify: grep -c "calibration\|tau.json" src/linear_ceiling/e9.py   # 0: the gate never looks; and `grep -c "does not exist; run \`summarize_e9 --calibrate-tau\`" src/linear_ceiling/summarize_e9.py` → 1
