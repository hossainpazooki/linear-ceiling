# When a PR's content already landed on main, `merge -s ours` records the PR as merged without changing a file

ts: 2026-10-04T09:49:31Z
commit: 9e5249b
session: main-branch dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: PR #12's resolved files were committed directly on main (`7544f7f`) instead of on the PR branch, so GitHub showed the
PR as conflicting with the very content it proposed. A `merge -s ours` of the PR head 8100414 on main (`1752c82`) made it an
ancestor of main with a zero-file diff, and GitHub marked #12 MERGED on push, keeping the co-author's commits in history.
Closing the PR would have given the same tree but left authorship only in a comment.
basis: at 9e5249b, 2026-10-04T09:49:31Z: `git merge-base --is-ancestor 8100414 7544f7f` -> no; `... 8100414 1752c82` -> yes;
  `git diff --stat 1752c82^1 1752c82 | wc -l` -> 0; `gh pr view 12 --json state,mergeCommit` -> `MERGED 1752c82`.
re-verify: git merge-base --is-ancestor 8100414 1752c82 && git diff --stat 1752c82^1 1752c82 | wc -l   # exit 0, then 0
