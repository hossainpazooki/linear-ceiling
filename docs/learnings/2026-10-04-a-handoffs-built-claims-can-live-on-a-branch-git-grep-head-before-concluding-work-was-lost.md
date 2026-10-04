# A handoff's "built" claims can live on a branch; `git grep HEAD` says main lacks it, `git log --all -- <file>` says where it is

ts: 2026-10-04T09:24:26Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: The E-TRUNC close (brief `2026-10-04-e-trunc-rulings-taken-under-supervision-…`) listed configs, a comparator, a draft and tests
as built. At `a4fa30f` none of those paths existed on main, `git grep sender_head_truncate HEAD` was empty, and `git stash list` was
empty, which read as lost work after a stash-around-rebase. It was not lost: the session had committed on a local branch `e-trunc`
(`799349d`, `2cf654a`, `0e0f8a0`), pushed to origin, which PR #17 (`c37f626`) later merged. Before calling work lost, run
`git log --all --oneline -- <a named path>`; a path that was ever committed anywhere shows up, and the reflog's
"moving from <branch> to main" lines name the branch.
basis: at 0c5ec15, 2026-10-04T09:24:26Z, `git log --oneline --all -- config/e9t-full.toml | tail -1` printed `2cf654a feat(e9t): four
  truncation-level configs and the paired comparator`; `git log --oneline main..e-trunc | wc -l` printed `0` (now merged);
  `git log --merges --grep="#17"` printed `c37f626 Merge pull request #17 from hossainpazooki/e-trunc`. The earlier miss was at
  `a4fa30f` (~08:33Z): `git grep -n sender_head_truncate HEAD -- src config tests` printed nothing.
re-verify: git log --oneline --all -- config/e9t-full.toml | tail -1 | cut -c1-7   # expect 2cf654a (the file's first commit, on e-trunc)
