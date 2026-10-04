# `ledger_check` chains by file order, so a staged number can append before lower numbers land; the drafts README allocates, the file orders

ts: 2026-10-04T09:24:24Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: refuted-assumption
fact: I had read the ordering guards (`### {PREV} present, ### {NUM} absent`, PREV = NUM − 1) as a contiguity rule and advised that
0052 (ready, CPU-only) must wait behind 0048–0051 (unrun GPU figures), or be renumbered. Wrong: `ledger_check` chains the
`prior-entries-sha256` by FILE order and never requires consecutive numbers. The ledger's tail now reads 0047, 0054, 0052, 0056,
0055, 0053, with `ledger ok` and CI green at every step. A draft's guard should name the entry it must follow in the file, not
NUM − 1; the README stays the sole allocator and numbers are permanent once staged (0054's Numbering paragraph is the precedent).
basis: at 0c5ec15, 2026-10-04T09:24:24Z, `grep -n '^### 00' ledger/ledger.md | tail -6` printed `3208 0047 · 3287 0054 · 3330 0052 ·
  3372 0056 · 3406 0055 · 3522 0053`; `python -m linear_ceiling.ledger_check` printed `ledger ok (blocks unchanged vs HEAD)`;
  `gh run list --branch main --limit 1` printed `completed success 0c5ec15` (09:21Z).
re-verify: grep -o '^### 00[0-9][0-9]' ledger/ledger.md | tail -6 | tr '\n' ' '   # expect "### 0047 ### 0054 ### 0052 ### 0056 ### 0055 ### 0053" (non-consecutive, chain ok)
