# Entry drafts (delete each script once its entry is appended)

Convention: an entry that carries numbers is appended by an ordering-guarded script that runs
the relevant fail-closed summarizer IN-PROCESS first and pulls every figure from its verified
output — the script refuses to run out of order and runs `ledger_check` after appending. Run
from the repo root with `.venv/Scripts/python.exe`.

<<<<<<< HEAD
Current state: **no drafts pending.** Entries 0013–0023 are all appended and their scripts
deleted (0023's pulled every figure from `results/e9/calibration/tau.json`, written by
`summarize_e9 --calibrate-tau`). The next expected entry is **0024 — the H-E9 verdict**, written
from a clean `summarize_e9` run after the A100 day (`docs/2026-09-02-e9-gpu-runbook.md`); its
script gets staged here when the E9 results are synced back.
=======
Current state: **one draft pending — `append_0024.py`** (Track B recon: manifest, selection rule,
overlap nulls, cache-aware readings; changes no verdict cell). It refuses until entry 0023
(Track A) is in the ledger and the E7 gate passes; `--preview` prints the text, `--number`
renumbers if 0024 was taken by a rebase. Entries 0013–0022 are appended and their scripts
deleted. The H-E9 verdict entry is Track A's, written from a clean `summarize_e9` run after the
A100 day (`docs/2026-09-02-e9-gpu-runbook.md`); from 0024 on a verdict-changing entry must
carry a `verdict: H-XX = <VERDICT>` line (`ledger_check`).
>>>>>>> c7ce3d8 (docs: Track B handoff brief and drafts state)
