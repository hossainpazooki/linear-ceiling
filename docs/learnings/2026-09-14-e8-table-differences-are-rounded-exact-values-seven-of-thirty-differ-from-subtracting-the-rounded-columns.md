# The E8 tables' drop and change cells are rounded exact differences; seven of thirty differ by one unit from subtracting the rounded columns

ts: 2026-09-14T01:27:20Z
commit: cf4047fa946f10998697facaa70f7b63247b6575
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: Three E8 tables were checked: 0020 (ledger 1111–1115), 0031 (1891–1895) and 0034 (2030–2034). Every drop and
change cell equals the summarizer's full-precision value rounded to four places, 30 of 30. Seven of the 30 differ by
one unit in the last place from subtracting the two displayed four-place columns:
- 0020: k = 4 V drop, k = 8 K drop.
- 0031: k = 1 V change, k = 4 V drop, k = 8 V change.
- 0034: k = 1 V drop, k = 8 K change.
A co-author recomputing from the displayed columns reported four of the seven as ledger inconsistencies. The ledger is
right. An appendix table built from these entries needs a note that differences are computed at full precision and then
rounded, or it should be generated from `results/e8{,a,c}/` rather than retyped.
basis: session script at cf4047f (with uncommitted outline edits that touch neither the ledger nor `results/`),
  2026-09-14T01:27Z. It read the ledger rows plus `results/e8/report.json` `per_k[k].drop`, `results/e8a/summary.json`
  `per_k[k].change_from_prior` and `recomputed[k].drop`, and `results/e8c/summary.json` likewise, and printed:
  `cells checked: 30`; `displayed != round(summarizer full-precision value, 4): 0 []`; `displayed != (rounded col a) -
  (rounded col b): 7`:
  `0020 k=4 V drop: entry +0.4158 | columns give +0.4157 | full precision +0.41576694`,
  `0020 k=8 K drop: entry +0.7263 | columns give +0.7264 | full precision +0.72634913`,
  `0031 k=1 V change: entry -0.0189 | columns give -0.0188 | full precision -0.01886482`,
  `0031 k=4 V drop: entry +0.4344 | columns give +0.4343 | full precision +0.43437931`,
  `0031 k=8 V change: entry -0.0075 | columns give -0.0076 | full precision -0.00753474`,
  `0034 k=1 V drop: entry +0.1459 | columns give +0.1458 | full precision +0.14586360`,
  `0034 k=8 K change: entry +1.1601 | columns give +1.1602 | full precision +1.16014181`.
re-verify: .venv/Scripts/python.exe -c "import json; d=json.load(open('results/e8/report.json'))['per_k']['8']; g,a=d['generic']['K'],d['agent']['K']; print(round(g-a,4), round(round(g,4)-round(a,4),4), d['drop']['K'])"   # needs the gitignored results/e8; expect: 0.7263 0.7264 0.7263491288189993
