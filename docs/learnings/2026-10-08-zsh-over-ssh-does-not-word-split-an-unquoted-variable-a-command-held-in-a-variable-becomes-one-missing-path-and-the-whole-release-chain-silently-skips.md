# zsh over ssh does not word-split an unquoted variable: a command held in a variable becomes one missing path, and a whole release chain can silently skip

ts: 2026-10-08T01:39:00Z
commit: 8696e83
session: llama-long-cell-0051-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The 0051 release was first driven from Windows over ssh to the Mac as `RP=".venv/bin/python tools/runpod/rp.py" …
$RP ssh "…"`. The Mac's login shell is zsh, which (unlike bash) does not split an unquoted `$RP` into words, so every call
became `zsh: no such file or directory: .venv/bin/python tools/runpod/rp.py`: the four pulled wrapper outputs were 0-byte
files, the token sweep, weight-cache removal and `terminate` never ran, and the `&&` chain's early members had already
"succeeded" (the `for` loop's redirects), so nothing stopped. The pod kept billing for three more minutes and the mirror
briefly held empty evidence files; both were caught because the output was read, not because anything refused. Rules:
over ssh to a zsh host write the full command path each time (or `${=RP}` / a shell function), and treat a 0-byte
"pulled" file as a failed pull, never as an empty log.
basis: runbook `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6 20:02 entry ("a first attempt at 19:59 ran nothing");
  Mac mirror `results/e9fl/logs/box/wrappers/*` (8,706 / 1,128 / 1,028 / 1,048 B after the second attempt).
re-verify: grep -n "unquoted zsh variable" docs/2026-10-07-llama-long-cell-runpod-runbook.md   # the release log names the cause
