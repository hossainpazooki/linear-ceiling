# An allocated entry number is a claim, not a reservation: re-read the allocator at HEAD and `git status` the target path before writing a draft

ts: 2026-10-04T09:40:00Z
commit: a2742b9
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: The 2026-10-04 seed allocated 0052 to the E-TRUNC registration and the pick-up verified "next free 0052" at 8e53eac. While this session built, another session on the same tree staged 0052/0053 (the second family's E8 amendment, 4ab54ae at 03:36 local) and appended 0054 (a2742b9, 03:48). This session then wrote `docs/drafts/append_0052.py` with the Write tool, overwriting the other session's TRACKED file in the working tree (restored with `git restore`), and its preview refused on its own ordering guard. The registration moved to 0055 and the four configs' `[e9.gate]` with it. Two rules follow: the allocator is re-read from HEAD immediately before a number is written into any file, and a Write to a path under docs/drafts/ or config/ is preceded by `git status -- <path>` so a tracked file is never clobbered.
basis: `git log --oneline 8e53eac..a2742b9` (four commits by the other session); `git status --short docs/drafts/append_0052.py` printed ` M` after this session's Write and nothing after `git restore`; `git show HEAD:docs/drafts/README.md | grep 'Next free number'` ends at **0055**.
re-verify: git log --format='%h %ci %s' 8e53eac..a2742b9 | grep -c .   # expect 4; and: git show a2742b9:docs/drafts/README.md | grep -o 'Next free number: \*\*00[0-9][0-9]\*\*' | tail -1   # expect **0055**
