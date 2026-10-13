# Entry 0045 attributes 0044's E7 report hash 27dc922e to "the box"; 0044 places the regeneration on the summarizing machine at home, and T04 reproduces it there

ts: 2026-10-13T14:15:45Z
commit: 01b2aea
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: 0045 (line 3126) says 0044 "records the E7 report regenerated on the box as 27dc922e" and (line 3131) "the box
value is the outlier". 0044 itself (lines 2920, 2924) says the E7 report was rebuilt on the summarizing machine, AT HOME,
under an 8-thread cap, because `results/e7/` was absent there. T04 (approved 2026-10-13) regenerated the report from a
fresh clone on that same machine and got 27dc922e again, while the Windows mirror and the Mac mini summary carry
0aba0fbe. So the value belongs to the second family's summarizing machine, not the GPU box, and it reproduces. The
cause is not established; the figure feeds only the descriptive coverage comparison. Ruling 2026-10-13: no entry now;
a one-line correction rides in the next entry that touches 0045, and Emerson is asked on issue #21 for a key-by-key diff.
basis: `grep -n "summarizing machine\|AT HOME\|regenerated on the box\|box value is the outlier" ledger/ledger.md` =
  lines 2920 ("AT HOME the summarizer ran under an **8**-thread cap"), 2924 ("summarizing machine (results/ is
  gitignored and E7 ran elsewhere)"), 3126 ("records the E7 report regenerated on the box as"), 3131 ("The box value is
  the outlier"); T04 lines 84, 92–93 carry 27dc922e for the fresh regeneration (captured 2026-10-13T14:15:45Z at 01b2aea).
re-verify: grep -c "regenerated on the box" ledger/ledger.md   # 1, the sentence a later entry corrects
