# A figures append script re-runs the summarizer as its gate: budget ten minutes; an interrupt writes nothing

ts: 2026-10-04T09:24:29Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: Every figures draft (`append_0049.py`, `append_0051.py`, `append_0053.py`) calls the cell's summarizer in-process before building
the entry, and for E8 that means the upstream scorer re-runs on every fingerprinted dump for k = 1, 4, 8. On this machine that took
9 min 51 s standalone and 10 min 13 s inside `append_0053.py --preview`; the operator's first append attempt was interrupted at the
same call and, because the ledger write comes after the gate and the `git rm` is chained with `&&`, nothing was written or removed.
Run figure appends with ten minutes uninterrupted, or in the background with the clone detached at the pin and restored by a trap.
basis: at 0c5ec15, 2026-10-04T09:24:29Z, the run log printed `== 08:46:11Z summarize` … `== 08:56:17Z preview 0053` … `== 09:06:30Z
  done` (one summarizer pass each); `grep -n "summarize(cfg)" docs/drafts/append_0051.py` printed line 55; the operator's pasted
  traceback (~09:15Z) ends in `summarize_e8.py line 92 … KeyboardInterrupt` with the ledger unchanged, and `git log -1 --
  ledger/ledger.md` now prints `0c5ec15 ledger: 0053 …` from the uninterrupted second run.
re-verify: grep -c "summarize(cfg" docs/drafts/append_0051.py   # expect 1 (the in-process gate; same shape in every figures draft)
