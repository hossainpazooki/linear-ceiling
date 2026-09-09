# An unattended run needs a stopping rule the summarizer can check after the fact: a registered order and a prefix property, not a wall-clock cutoff

kills: (nothing)
ts: 2026-09-09T22:05:00Z
commit: 407a38e
session: dev-47 (9c42735d)
status: verified
fact: An overnight sitting that may end before every handoff is scored cannot be read under 0023's "never change
the set after a score file exists" unless the partial set was determined before the run. A wall-clock cutoff
("whatever is scored by 07:00 UTC") is not checkable afterwards: the report's timestamps are self-reported and
the set could be edited to any subset. What IS checkable: the run order is registered in config and re-derived
by the summarizer from the alignment records (|S| ascending, ties by id; there are none among the 35), and the
scored set must be a PREFIX of it. `e9 --close-partial` refuses on a non-prefix, stamps the close, names the
unscored; `summarize_e9` re-derives the order and refuses a partial report whose scored set is not the prefix
or whose config registers no partial close. The cutoff's reason is the operator's and goes into the verdict
entry by a required argument, where "it may not depend on any score" is a stated rule, not a mechanism. A second
consequence found by test: with a partial close every KEPT handoff may be unscored, so the summary's
keep-subset re-score line must print "nothing to read", never format a None and never a zero.
basis: tests/test_e9_long.py::test_close_partial_needs_the_registration_a_prefix_and_names_the_unscored and
  tests/test_summarize_e9_long.py::test_partial_close_summarizes_the_prefix_and_names_the_unscored at the
  uncommitted tree (the None-format crash was the first failure of the second test, fixed in
  summarize_e9.py `_fe`).
re-verify: .venv/Scripts/python.exe -m pytest -q tests/test_e9_long.py tests/test_summarize_e9_long.py -k partial   # 2 passed
