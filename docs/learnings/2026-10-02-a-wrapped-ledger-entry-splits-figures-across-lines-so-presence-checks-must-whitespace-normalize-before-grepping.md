# A wrapped ledger entry splits figures across lines, so a presence check against it must whitespace-normalize before matching

ts: 2026-10-02T03:35:00Z
commit: 470133e
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: Entry 0045 is wrapped at 112 columns. Two of its figures straddle a line break: `19,094 (11.3%)` is written as `**19,094` at the end of one line and `(11.3%)` at the start of the next, and `(0 of 28 over it)` likewise. A line-oriented grep for either returns 0 although both are on the ledger; joining the entry on whitespace first returns 1 for each. The same defeated two draft tests until they compared against `" ".join(entry.split())`. Any gate that checks a figure is "on the ledger" by grep must normalize whitespace or it will refuse true figures.
basis: at 470133e, ~03:35Z: a python count of `"19,094 (11.3%)"` in the raw 0045 block printed 0 and `"(0 of 28 over it)"` printed 0; on `" ".join(" ".join(lines).split())` both printed 1. Re-captured at write (04:37Z) against `git show 470133e:ledger/ledger.md`: `awk '/19,094 \(11\.3%\)/{n++} END{print n+0}'` → 0; `tr '\n' ' ' | tr -s ' ' | grep -o "19,094 (11.3%)" | wc -l` → 1.
re-verify: git show 470133e:ledger/ledger.md | tr '\n' ' ' | tr -s ' ' | grep -o "19,094 (11.3%)" | wc -l   # expect 1, while a line-wise grep for the same string gives 0
