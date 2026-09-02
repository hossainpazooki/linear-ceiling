# A worktree carrying a junction into main's gitignored traces emptied them when the worktree was deleted

kills: (nothing)
ts: 2026-09-02T03:11:58Z
commit: 264174e04e65ca8be580a84aedf12b22254ac48c
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: suspected
fact: `traces/` on the main checkout (188 files, 151 MB, gitignored, acquired 2026-09-01) was
emptied at 2026-09-02T03:11:58Z, leaving the directory itself in place. The Track B worktrees
reached main's traces through a directory junction (Track B's own memory: "`traces` junction to
main's gitignored tree"), and the `~/dev/lc-track-b` worktree disappeared inside the same
ten-minute window (present at 264174e, gone by 13b8128). A recursive delete of a tree that
contains a junction on Windows deletes THROUGH the junction and leaves the target directory
empty -- which is the exact shape observed. The actor is not established (the operator did
not run a removal; this session's removal commands were emitted after 13b8128; the Track B
session was cleaning up at the time). Recorded as suspected on the mechanism, not on who.
Rule: before deleting any worktree or tree, list its reparse points (`fsutil reparsepoint
query`, or `find . -type l`, or `dir /AL /S`) and unlink junctions first; never share a
gitignored data tree by junction -- copy it, or point the config at one absolute path.
basis: `stat traces` -> `birth 2026-09-01 01:27:18 -0400 | mtime 2026-09-01 23:11:58 -0400`,
  empty; `git worktree list` at 264174e showed `~/dev/lc-track-b 6725488 [track-b]` and
  `.claude/worktrees/track-b-recon f48b536 locked`; at 13b8128 lc-track-b was absent and
  track-b-recon still present with 25 changed files; `grep -c junction
  ~/.claude/projects/C--Users-hossa-dev/memory/linear-ceiling-track-b.md` -> 1.
re-verify: stat -c '%y' "$HOME/dev/linear-ceiling/traces" | grep -c '2026-09-01 23:11:58'
