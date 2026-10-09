# `MSYS_NO_PATHCONV=1` is per argument: a path the LOCAL Python opens must be a Windows path, or it lands under `C:\c\…` — the `--verify-file` that blocked `terminate`

ts: 2026-10-07T06:46:00Z
commit: d4d48a1
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The 0047 sitting's fix for Git Bash mangling remote paths (`MSYS_NO_PATHCONV=1` on every `rp.py` call) has a mirror
failure: with the override on, a `$HOME/…` argument reaches Python as the POSIX `/c/Users/…`, which Windows Python
resolves relative to the current drive as `C:\c\Users\…`. `rp.py up --verify-file $HOME/.cache/linear-ceiling/cons-verified.json`
therefore stored `C:\c\Users\hossa\.cache\…` in the state file, and `terminate` refused the receipt written at the real
`~/.cache/…` path. The rule has two halves: arguments the POD consumes (`--dest /workspace/`, remote tar paths) need the
override; arguments the local Python OPENS (`--verify-file`, `--evidence`, `--output`) need a Windows path (`C:/…`) or
the override off. Same mechanism as the `pull --force-tar` extraction into `C:\c\Users\…` (learning of the same day).
basis: 2026-10-07 06:41:30Z `rp REFUSED: verification interlock C:\c\Users\hossa\.cache\linear-ceiling\cons-verified.json does not
  exist`; receipt copied to that path, `terminate` sent 06:43:06Z, PROVEN GONE; stray `C:\c` tree removed. The 0047
  sitting's `up` had passed `~/.cache/…` without the override and stored the correct path. Also hit at 04:10Z by
  `summarize.py --evidence ~/dev/…` (`'\\c\\Users\\…\\SHA256SUMS'` not found) — fixed by passing `C:/Users/…`.
re-verify: MSYS_NO_PATHCONV=1 .venv/Scripts/python.exe -c "import pathlib,sys;print(pathlib.Path(sys.argv[1]).resolve())" /c/Users/hossa   # prints C:\c\Users\hossa — the wrong drive-relative resolution
