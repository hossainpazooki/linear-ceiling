# Every upstream re-pin trips UPSTREAM.md's one-full-sha rule unless the parent sha is shortened in the same edit

kills: (nothing)
ts: 2026-09-04T17:10:33Z
commit: 498bacc048044bf831e9641e16680c92705b90bb
session: qwen-kv-cache-oom-debug (8e4ab089-ff2e-43bc-9d6a-4da8ea00ce04)
status: verified
fact: tests/test_imports.py::test_upstream_pin_matches_upstream_md requires that the set of 40-hex
shas in UPSTREAM.md equal {linear_ceiling.UPSTREAM_SHA}. A re-pin edit that writes the new pin in
full and leaves the previous pin's full sha in the "its parent is" clause leaves TWO full shas and
CI fails on the first push after the operator's sed. The 0026 re-pin failed CI exactly this way
(entry chain intact, instrument correct, docs wrong). Rule: a re-pin edit is three moves in one
commit -- new full sha in config + UPSTREAM.md, parent sha to 8 chars, package constant bumped --
and the suite runs AFTER the sed, not before it.
basis: CI run 33899087599 on 498bacc, job "Run pytest -q": "assert shas == {linear_ceiling.UPSTREAM_SHA}, shas
  / AssertionError: {'36d73b3f29d9b1f3a7c5148525de92b0b1b8ff5b', 'd5786df91f55629933067e3c4bb14f1288c4bef2'}"
  (2026-09-04T17:10:33Z); fixed by b300eb9. The 0030 re-pin block hands the operator all three seds.
re-verify: grep -cE '[0-9a-f]{40}' UPSTREAM.md; grep -n "^UPSTREAM_SHA" src/linear_ceiling/__init__.py   # after any re-pin: the count is 1 and the sha matches
