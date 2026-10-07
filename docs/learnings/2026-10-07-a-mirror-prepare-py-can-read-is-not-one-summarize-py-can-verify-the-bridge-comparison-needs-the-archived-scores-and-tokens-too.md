# A mirror `prepare.py` can read is not one `summarize.py` can verify: the bridge comparison needs the archived `scores/` and `tokens/` too

ts: 2026-10-07T06:46:00Z
commit: d4d48a1
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `tools/consolidation/prepare.py` reconstructs the texts from `archive/records/<cohort>/report.json` + `align/`, so a
mirror built for it has only those. `tools/consolidation/summarize.py`'s bridge comparison for `qwen17_bridge` then opens
`archive/records/<cohort>/scores/<score_file>` and `tokens/<tokens_file>` through `verified()` to re-derive the archived
per-token deltas it compares against, and refuses with `FileNotFoundError` on the first missing score file. The mirror
0048 reads must carry all four (`report.json`, `align/`, `scores/`, `tokens/`) per cohort, and `SHA256SUMS` must list them.
basis: 2026-10-07 04:11Z second `--bridge-only` attempt: `FileNotFoundError: …archive\records\e9l\scores\20241016_…_sw152.json`;
  after copying `results/{e9s,e9l}/{scores,tokens}` (25 + 35 files each) and rewriting `SHA256SUMS` (536 files), the same
  command passed (rc 0, 12 bridge rows, max relative mean gap 1.2e-5). Runbook `docs/2026-10-07-consolidation-runpod-runbook.md` §6.
re-verify: grep -n -E 'old/"scores"|old/"tokens"' tools/consolidation/summarize.py   # two hits: the bridge comparison's archive reads
