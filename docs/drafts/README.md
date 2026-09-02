# Entry drafts (delete each script once its entry is appended)

Convention: an entry that carries numbers is appended by an ordering-guarded script that runs
the relevant fail-closed summarizer IN-PROCESS first and pulls every figure from its verified
output — the script refuses to run out of order and runs `ledger_check` after appending. Run
from the repo root with `.venv/Scripts/python.exe`.

Current state: **no drafts pending.** Entries 0013–0024 are appended and their scripts deleted
(0023 pulled every figure from `results/e9/calibration/tau.json` via `summarize_e9 --calibrate-tau`;
0024 from `results/e7/recon.json` via `summarize_e7 --overlap-null --cache-aware-ratio`, behind
`e7.assert_ready`). The next expected entry is **0025 — the H-E9 verdict** (Track A), written from a
clean `summarize_e9` run after the A100 day (`docs/2026-09-02-e9-gpu-runbook.md`); it must carry a
`verdict: H-E9 = <VERDICT>` line (`ledger_check`). Its script gets staged here when the E9 results
are synced back.
