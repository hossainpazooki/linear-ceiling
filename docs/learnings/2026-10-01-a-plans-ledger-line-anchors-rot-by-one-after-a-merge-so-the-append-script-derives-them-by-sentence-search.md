# A plan's ledger line anchors rotted by one after the PR 5 merge; the append script derives each anchor by sentence search inside its entry

ts: 2026-10-01T19:41:00Z
commit: 36e0621
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: The 09-30 plan for the corrective entry cites 0029:1787, 0036:2208, 0020:1113, 0030:1853 as "verified 2026-09-30". On the 10-01 ledger each is one line off (1787 and 1853 are blank; the sentences sit at 1788, 2209, 1114, 1854). Typed anchors cannot survive an entry inserted above them, so `docs/drafts/append_0045.py` locates every quoted sentence inside the named entry's block and refuses on zero or more than one hit; the eleven anchors it writes are computed at append time.
basis: at 36e0621 (ledger identical through 20a4e71), ~19:41Z: `sed -n 1787p ledger/ledger.md` printed an empty line and `sed -n 1788p` printed `**Band outcome, against the rule as written: HOLDS.** Not one included handoff has a single matched token...`; `1113p` printed the table rule `|---|---|---|---|---|` and `1114p` the k = 1 row carrying `0.5629 / 0.3418`; `anchors()` later returned `{'0029_sentence': 1788, '0036_sentence': 2209, '0020_r2': 1114, '0030_r2': 1854, ...}`. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: git show 20a4e71:ledger/ledger.md | sed -n '1787p;1788p' | cut -c1-40   # expect an empty line, then `**Band outcome, against the rule as`
