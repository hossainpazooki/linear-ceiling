# A substitution in a handed-off commit block that was not executed first left main red

kills: (nothing)
ts: 2026-09-01T23:54:12Z
commit: 0316b8105f1461a4c863a8b361f9b57ab10671fd
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: The commit block handed to the operator carried a `sed` meant to shorten the prior
upstream pin's full sha in UPSTREAM.md after the new sha was substituted in. Its pattern was
written against the NEW sha, matched nothing, and the `&&`-chained gate (`test_imports` then
`e9 --check`) stopped at the first failure -- but the git commands that followed were not
chained to it, so four commits were pushed with `test_imports` red on main for one commit.
Rule for this repo: any substitution in a handed-off block is executed against a scratch copy
of the file first and its output shown, and gate commands are chained INTO the commit, not
placed beside it.
basis: operator's pasted terminal, 2026-09-01T23:54Z: `FAILED tests/test_imports.py::
  test_upstream_pin_matches_upstream_md - AssertionError: {'36d73b3f...', '7e41f792...'}`;
  `1 failed, 4 passed`; then `[main 0a0f066] ... [main 0316b81] ... f48b536..0316b81 main ->
  main`. Fixed by 7fc1b5b.
re-verify: git show 0316b81:UPSTREAM.md | grep -c 7e41f792df0a03caa745a52de0ad2bd930e52a47
