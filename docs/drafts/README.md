# Entry drafts (delete each script once its entry is appended)

Ordering approved by the operator 2026-09-01: **0015** (taxonomy verdicts, written only from the
first real `summarize_e7` run) → **0016** (E8 amendment; `python docs/drafts/append_0016.py <upstream_sha> <date>`
after `scripts/score_mapper.py` is committed upstream) → **0017** (E9 registration;
`python docs/drafts/append_0017.py <date>`). Each script refuses to run out of order and runs
`ledger_check` after appending. Run from the repo root with `.venv/Scripts/python.exe`.
