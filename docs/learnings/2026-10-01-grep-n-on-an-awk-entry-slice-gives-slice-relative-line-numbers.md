# `grep -n` on an awk entry slice gives slice-relative line numbers; two docs cited 0025:86 for file line 1535

ts: 2026-10-01T04:47:35Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `awk '/^### 0025/,0' ledger/ledger.md | grep -n <needle>` numbers lines from 1 at the slice's start. On
2026-09-30 this session wrote `0025:86` and `0026:112` as ledger anchors into the review response map and two design
drafts; the file lines are 1535 and 1561, inside the right entries but at numbers that `sed -n 86p` resolves to
entry 0005. A per-anchor refutation (does the cited line contain the cited figure?) caught it before commit; the
docs on main carry the corrected lines. Anchor with `grep -n` on the whole file, or print `NR` from awk.
basis: at 0a51275, 2026-10-01T04:47:35Z, `awk '/^### 0025/,0' ledger/ledger.md | grep -n '114,688 B per token' |
  cut -d: -f1` printed 86 and `grep -n '114,688 B per token' ledger/ledger.md | cut -d: -f1` printed 1535.
re-verify: grep -n "114,688 B per token" ledger/ledger.md | cut -d: -f1; awk '/^### 0025/,0' ledger/ledger.md | grep -n "114,688 B per token" | cut -d: -f1   # expect 1535 then 86
