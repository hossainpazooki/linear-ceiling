# Entry 0054 cites PR #12, which GitHub now returns 404; the review record is on main at 7544f7f, merged as 1752c82

ts: 2026-10-13T13:59:29Z
commit: 5c4e645
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: Entry 0054 (immutable) rests its Condition 1 ruling on issue #7 plus PR #12 and an issue-comment URL on the PR. The
PR no longer resolves on GitHub. The files it carried are on `main`: `docs/reviews/2026-10-01-cache-refutation-0025-0029.md`
last touched by `7544f7f` (2026-10-04, "review: record the Condition 1 ruling…"), merged by `1752c82` ("Merge PR #12
(content already on main at 7544f7f)"). Issue #7 is CLOSED (2026-10-04T08:14Z), so 0054's "remain open work under
issue #7" (rows R2, R5/R6, R11/R12, the long and scaled-short attack pass) names a tracker that is shut; those rows need a
new home (operator's call; see the 2026-10-13 reply).
basis: `gh pr view 12 --json state` = "GraphQL: Could not resolve to a PullRequest with the number of 12"; `gh issue view 7
  --json state,closedAt` = `CLOSED 2026-10-04T08:14:18Z`; `git log -1 --format=%h -- docs/reviews/2026-10-01-cache-refutation-0025-0029.md`
  = `7544f7f`; `git log --all --grep='#12'` = `1752c82 Merge PR #12 (content already on main at 7544f7f)` (captured 2026-10-13T13:59:29Z at 5c4e645).
re-verify: git log --oneline -1 -- docs/reviews/2026-10-01-cache-refutation-0025-0029.md   # 7544f7f
