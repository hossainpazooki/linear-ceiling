# Entry drafts (delete each script once its entry is appended)

Ordering (operator-approved 2026-09-02): ~~0017 correction~~ **APPENDED** (chain `41982f56…`) →
**0018** the corrected figures (`append_0018.py <date>`; run order: commit 0017 →
`python -m linear_ceiling.e7` → the script; it refuses unless 0017 is in HEAD and pulls every
number from the report after an in-process `summarize_e7` pass) → **0019** E9 registration
(`append_0019.py <date>`, band approved 2026-09-01) → **0020** H-E8 verdict (`append_0020.py <date>`; re-runs `summarize_e8` in-process, ~25 min, and refuses unless it passes; flips H-E8's cell). Each script refuses to run out of order
and runs `ledger_check` after appending. Run from the repo root with `.venv/Scripts/python.exe`.
