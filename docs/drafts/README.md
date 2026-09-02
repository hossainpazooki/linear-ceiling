# Entry drafts (delete each script once its entry is appended)

Convention: an entry that carries numbers is appended by an ordering-guarded script that runs
the relevant fail-closed summarizer IN-PROCESS first and pulls every figure from its verified
output — the script refuses to run out of order and runs `ledger_check` after appending. Run
from the repo root with `.venv/Scripts/python.exe`.

Current state: **one draft pending — `append_0024.py`** (Track B recon: manifest, selection rule,
overlap nulls, cache-aware readings; changes no verdict cell). It refuses until entry 0023
(Track A) is in the ledger and the E7 gate passes; `--preview` prints the text, `--number`
renumbers. Entries 0013–0023 are appended and their scripts deleted (0023's pulled every figure
from `results/e9/calibration/tau.json`, written by `summarize_e9 --calibrate-tau`). The H-E9
verdict entry is Track A's, written from a clean `summarize_e9` run after the A100 day
(`docs/2026-09-02-e9-gpu-runbook.md`); its script gets staged here when the E9 results are synced
back. **Number collision:** both drafts claim 0024 — whichever appends second takes the next free
number. From 0024 on a verdict-changing entry must carry a `verdict: H-XX = <VERDICT>` line
(`ledger_check`).
