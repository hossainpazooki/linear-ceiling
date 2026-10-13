# A branch block run over a dirty main tree carries the dirt into the branch commit: 59182a4 took three main-side edits with the superpowers row

ts: 2026-10-11T02:55:00Z
commit: 2fcf985
session: pr19-agent-docs-audit (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The branch-fix block for PR #19 (checkout the branch, drop one table row, commit, push, checkout main) was handed
over while main's working tree held three uncommitted edits (the drafts README allocator block, three LEARNINGS.md
index rows, the trunc docstring). The files were identical on both branches, so the checkout carried the edits across,
the commit took them, and the checkout back to main left main without them; the later main commit c0fc82c then held
only the three new learning files although its subject claimed the docstring. The branch needed a revert commit
(a2c34e5) and main a re-apply (91064ee). A block that switches branches must start from a clean tree, or stage by
explicit path and never `-a`; the hand-over order was wrong, not the commands.
basis: `git show --stat --format= 59182a4 | tail -1` = " 4 files changed, 17 insertions(+), 2 deletions(-)" with
  docs/agent/repo-architecture.md, docs/drafts/README.md, docs/learnings/LEARNINGS.md,
  src/linear_ceiling/summarize_e9_trunc.py; `git show --stat c0fc82c` = 3 files, all docs/learnings/2026-10-10-*.md;
  reflog 2026-10-10 16:58:09 -0400 checkout → commit → checkout (captured at 2fcf985, before 91064ee)
re-verify: git show --stat --format= 59182a4 | tail -1   # 4 files changed, 17 insertions(+), 2 deletions(-)
