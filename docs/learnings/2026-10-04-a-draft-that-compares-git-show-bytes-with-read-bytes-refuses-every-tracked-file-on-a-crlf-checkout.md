# A draft that compares `git show HEAD:` bytes with `read_bytes()` refuses every tracked text file on a CRLF checkout

ts: 2026-10-04T09:49:21Z
commit: 9e5249b
session: main-branch dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: `append_0050.py` guarded its inputs with `committed.stdout == path.read_bytes()` against `git show HEAD:<file>`. Under
`core.autocrlf=true` git stores LF and checks out CRLF, so the raw comparison is false for any tracked text file even when
`git diff --quiet HEAD -- <file>` (which normalizes) is clean. The operator's 0050 append refused with "config/e9fl.toml is not
byte-identical to HEAD" on an unmodified file; rewriting the worktree copy with HEAD's bytes let it append (`cff787f`). Six
tracked configs on this clone carry the same CRLF gap (e9fl, e9f, e9t-full/l65/l49/l32). Draft guards must compare
newline-normalized bytes (`sha256_text_file`, as the frozen-file checks of 0046-0049 do since `5c8d438`) or rely on
`git diff --quiet` alone.
basis: at 9e5249b, 2026-10-04T09:49:21Z: `git show HEAD:config/e9fl.toml | sha256sum` -> `2f8d9545e1f3` with 0 CRLF;
  the same content CRLF-converted hashes `1d1a7322dc54` (174 lines), the worktree hash the refusal saw; `git diff --quiet
  HEAD -- config/e9fl.toml` rc=0. Operator-pasted traceback (~09:40Z): `append_0050.py, line 169 ... AssertionError:
  config/e9fl.toml is not byte-identical to HEAD`.
re-verify: .venv/Scripts/python.exe -c "import subprocess;h=subprocess.run(['git','show','HEAD:config/e9t-full.toml'],capture_output=True).stdout;w=open('config/e9t-full.toml','rb').read();print(h==w, h.replace(b'\r\n',b'\n')==w.replace(b'\r\n',b'\n'))"   # False True on a CRLF Windows clone; True True on LF
