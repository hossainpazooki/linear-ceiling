# A preview that prints the entry dies on the cp1252 console before showing anything; a draft must reconfigure stdout

ts: 2026-10-04T09:49:25Z
commit: 9e5249b
session: main-branch dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: On this Windows clone Python's stdout encoding is cp1252, so `print(ENTRY)` raises `UnicodeEncodeError` at the first
tau, arrow or minus sign and the preview shows nothing. `append_0050.py --preview` failed this way (reproduced 2026-10-04);
with `PYTHONIOENCODING=utf-8` the same preview rendered. Drafts written this session call `sys.stdout.reconfigure(encoding=
"utf-8")` before printing; `append_0051.py` lacked it and was patched in this close. The append path itself printed only
ASCII, which is why a missing preview can look like a successful no-op.
basis: at 9e5249b, 2026-10-04T09:49:25Z: `python -c "import sys;print(sys.stdout.encoding)"` -> `cp1252`; `python -c
  "print('\u03c4')"` -> `UnicodeEncodeError: 'charmap' codec can't encode character '\u03c4'`; with PYTHONIOENCODING=utf-8 ->
  `b'\xcf\x84\r\n'`; `grep -c "sys.stdout.reconfigure"` -> append_0048.py 1, append_0049.py 1, append_0051.py 0.
re-verify: python -c "import sys;print(sys.stdout.encoding)"   # cp1252 in Git Bash on this machine; the drafts' preview branches must not depend on it
