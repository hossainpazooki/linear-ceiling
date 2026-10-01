# A hardlinked R8 staging tree keeps mutating with the live results tree, so any later summarizer run silently diverges the stage from the published dataset — and a stage-vs-live diff cannot detect it, because it is the same inode

kills: (nothing)
ts: 2026-10-01T04:53:08Z
commit: bf75008b95990237c84906d4f9bfeecb7f2ec870
session: e9l-aws-run (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl)
status: verified
fact: `tools/hf_backup.sh`'s stage recipe hardlinks `results/<exp>/` into `~/dev/hf-staging/<dataset>/`, and
`summarize_e9` writes `summary.json` in place rather than through a temp file plus `os.replace`. So the stage is not
a snapshot: it is the same inode as the live file, and every later reader run rewrites the staged bytes too, long
after `BACKUP VERIFIED`. The e9_tail work of 2026-10-01 re-ran the summarizer on all three Qwen cells and moved
`results/e9s/summary.json` from `2f562aca…` to `859a8c98…` and `results/e9l/summary.json` from `be136307…` to
`64e64e93…`, so **both** R8 stages now disagree with their published datasets on that one path and
`tools/hf_verify_backup.py` would fail there. Two consequences. (1) A `sha256sum` re-verify line in a handoff brief
that cites a summary hash **rots** the next time any reader runs — `docs/handoff/2026-10-01-e9l-aws-run-refresh.md`
asserts `2f562aca` and is now wrong. (2) A local stage-vs-live comparison is **vacuous**: both paths resolve to one
inode, so a field-by-field diff reports zero differences no matter what changed. The only valid reference for a
published artifact is the **published bytes**, fetched from the Hub. Fetched here, the divergence is one added key
(`dump_rope`, null) with **zero values changed**, so no registered figure moved and 0036/0038 stand — but that was
established by downloading the Hub copy, not by reading the stage. Do not re-push: the Hub still holds the bytes
those entries cite. Copy into a stage instead of linking, or delete the stage once the push verifies.
basis: at bf75008, 2026-10-01T04:53:08Z: `stat -c '%i %h %n'` on `results/e9s/summary.json` and
  `~/dev/hf-staging/linear-ceiling-e9s-2026-09-13/results/e9s/summary.json` both printed inode
  `3377699722457348` with link count `2`; `sha256sum` of the live file gave `859a8c98e1cd0e6b` against the brief's
  asserted `2f562aca`; `curl` of
  `https://huggingface.co/datasets/hossainpazooki/linear-ceiling-e9s-2026-09-13/resolve/main/results/e9s/summary.json`
  returned `2f562aca66e4cf87` (81,392 bytes). A flattened field-by-field diff of the Hub copy against the live file
  printed `keys only on the Hub: 0 / keys only live: 1 ['/dump_rope'] / values that CHANGED: 0`; the same diff for
  e9l (`be136307cdfad17b` on the Hub vs `64e64e9318d442ec` live) printed the identical shape. The earlier
  stage-vs-live run of that same diff reported `0 / 0 / 0` — the vacuous result this entry exists to flag.
re-verify: .venv/Scripts/python.exe -c "import os; a=os.stat('results/e9s/summary.json'); b=os.stat(os.path.expanduser('~/dev/hf-staging/linear-ceiling-e9s-2026-09-13/results/e9s/summary.json')); print('same inode:', (a.st_ino,a.st_dev)==(b.st_ino,b.st_dev), '| links:', a.st_nlink)"   # same inode: True | links: 2
