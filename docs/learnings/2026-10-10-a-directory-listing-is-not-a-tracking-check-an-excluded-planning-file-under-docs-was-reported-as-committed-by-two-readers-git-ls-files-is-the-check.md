# A directory listing is not a tracking check: an excluded planning file under `docs/` was reported as committed by two readers; `git ls-files` is the check

ts: 2026-10-10T21:40:00Z
commit: 5cedd54
session: pr19-agent-docs-audit (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `docs/superpowers/plans/2026-08-26-linear-ceiling-w1.md` exists in the operator's working tree and is kept out of
history by `.git/info/exclude` (local-only, per house policy that planning documents never enter a repo). An audit agent
ran `ls docs`, saw the file, and reported "a committed superpowers plan"; the session lead repeated it to the operator as
a policy breach and added a row for it to the PR's architecture table before checking. `git ls-files docs/superpowers`
returns nothing; the file was never tracked. A tree listing shows what is on disk, which includes excluded and ignored
paths; only `git ls-files` (or `git ls-tree` on a revision) shows what a commit carries. Reporting a file as committed is a
claim about history and takes the history command. The wrong table row is removed from the PR branch in a follow-up
commit.
basis: `git ls-files docs/superpowers | wc -l` = 0 at `5cedd54`; `git check-ignore -v docs/superpowers/plans/2026-08-26-linear-ceiling-w1.md`
  = `.git/info/exclude:7:docs/superpowers/plans/`; `.git/sdd/OPERATOR-COMMITS.md` line 14 ("excluded via .git/info/exclude");
  the audit report and the lead's message of 2026-10-10 (this session's transcript); `docs/agent/repo-architecture.md` on the
  PR branch at `561bc05` (the row).
re-verify: git ls-files docs/superpowers | wc -l   # 0
