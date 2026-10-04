# Two sessions editing one working tree collided within the hour; a seed must name the isolation boundary

ts: 2026-10-04T09:49:35Z
commit: 9e5249b
session: main-branch dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: The 2026-10-04 E-TRUNC seed told a second session to edit `config.py`, `e9.py`, `e9_align.py` and `summarize_e9.py` in
the main working tree while this session and the Llama session were live in it. Within the hour this session wrote a draft
over the Llama lane's committed `docs/drafts/append_0052.py` (restored from HEAD, byte-identical), the E-TRUNC session's
unstaged edits blocked the operator's rebase, and a third lane's commits rode in a push unreviewed. The work was rescued by
moving it to branch `e-trunc` and a worktree; it merged as PR #17. Operator: "you should have kept the other session
constrained to cloud runs instead of rerunning and modifying code." Seeds now carry a boundary section first.
basis: at 9e5249b, 2026-10-04T09:49:35Z: `git log --diff-filter=A --format='%h %ci' -- docs/drafts/append_0052.py` ->
  `4ab54ae 2026-10-04 03:36:07 -0400` (the Llama lane's commit, before this session's overwrite and restore);
  `git merge-base --is-ancestor e-trunc main` -> yes (tip `f2e4829`, merged at `c37f626`); the seed
  `~/dev/briefs/linear-ceiling/2026-10-04-seed-e-trunc-rulings-1-3.md` line 8 reads `## 0a. Boundary (added 2026-10-04 after a collision)`.
re-verify: git log --diff-filter=A --format='%h %ci' -- docs/drafts/append_0052.py   # 4ab54ae 2026-10-04 03:36:07 -0400
