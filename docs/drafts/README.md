# Entry drafts (delete each script once its entry is appended)

Convention: an entry that carries numbers is appended by an ordering-guarded script that runs
the relevant fail-closed summarizer IN-PROCESS first and pulls every figure from its verified
output — the script refuses to run out of order and runs `ledger_check` after appending. Run
from the repo root with `.venv/Scripts/python.exe`.

Current state: **no drafts pending.** Entries 0013–0021 are all appended and their scripts
deleted. The next expected entry is **0022 — the H-E9 verdict**, written from a clean
`summarize_e9` run after the A100 day (`docs/2026-09-02-e9-gpu-runbook.md`); its script gets
staged here when the E9 results are synced back.
