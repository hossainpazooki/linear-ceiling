# The WSL suite on the /mnt/c checkout fails the four bash-exec tests through a CRLF shebang; "Windows-only red" is the wrong label

ts: 2026-10-01T18:06:00Z
commit: a6a746d
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: Running the suite in the Linux venv against the Windows checkout gives 548 passed / 4 failed / 1 skipped, and all four failures are `tests/test_runpod_*` executing `tools/runpod/*.sh`, which the checkout holds as CRLF (`i/lf w/crlf`), so `/usr/bin/env` looks for `bash\r`. The audit's "Windows suite red, Linux CI green" is true of the gate of record but not of WSL on this tree: the red is a property of the worktree's line endings, not of the interpreter.
basis: at a6a746d, 18:01Z (suite) and ~18:06Z (ending check): `pytest -q` under `~/lc-wsl-venv` printed `4 failed, 548 passed, 1 skipped`; the failing tests' stderr printed `/usr/bin/env: 'bash\r': No such file or directory`; `git ls-files --eol tools/runpod/` printed `i/lf    w/crlf` for `driver_child.sh`, `resume_a_fit.sh`, `rp.py`. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: git ls-files --eol tools/runpod/driver_child.sh   # expect i/lf w/crlf on a Windows checkout; LF index means CI is unaffected
