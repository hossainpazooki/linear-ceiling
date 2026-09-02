# `git rebase --continue` accepts staged conflict markers, and no gate in this repo refuses them

kills: (nothing)
ts: 2026-09-02T02:45:07Z
commit: 84f2ed29cbc35b90c8e2386344094a7ed9c1d7ca
session: linear-ceiling track-b (session_01RRk8euGRszMDP4z12wDdJz)
status: verified
fact: Rebasing the six Track B commits onto main paused three times; the conflicted files were
staged with their `<<<<<<<` / `=======` / `>>>>>>>` blocks still inside and `rebase --continue`
committed them, so three replayed commits carry markers in CLAUDE.md, docs/handoff/HANDOFF.md
and docs/drafts/README.md. pytest, lint_scope and ledger_check all passed on that tip and CI
went green: the markers sat outside the ledger's entry blocks and outside every tested file.
`git diff --check` before each `rebase --continue` is the one-line guard; b44b4f6 removed the
markers by a structural merge of both sides.
basis: on the rebased tip, `grep -n -E '^(<<<<<<<|=======|>>>>>>>)' CLAUDE.md docs/handoff/HANDOFF.md docs/drafts/README.md`
  printed 12 marker lines, e.g. `CLAUDE.md:78:>>>>>>> b0e35d9 (feat(ledger_check): block diff vs base revision ...)`
  and `CLAUDE.md:106:>>>>>>> 0c8b44c (docs: scope H-E7a to public benchmark traces ...)`; the
  worktree reflog showed `rebase (continue)` three times then `rebase (finish): returning to
  refs/heads/track-b` with no rebase-merge state left. The `ts:` is the rebase-finish moment
  (epoch 1788317107) at which the markers became committed; the grep was captured after it and
  before the fix commit at 2026-09-02T02:59:19Z.
re-verify: git show b44b4f6~1:CLAUDE.md | grep -c '^<<<<<<< '   # 2
