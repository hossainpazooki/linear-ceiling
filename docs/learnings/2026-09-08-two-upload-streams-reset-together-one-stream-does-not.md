ts: 2026-09-08T22:01:30Z
commit: a71c3b4
session: Claude Code session 878feb6f, pushing the n = 420 dumps to the box through /api/contents
status: verified
fact: Two parallel base64 upload streams of 60 MB parts through the JupyterHub `/api/contents` endpoint both received `ConnectionResetError(10054)` at the same instant after ~1 GB and exhausted 4 retries in 20 s; one stream with 32 MB parts, `Connection: close`, and 10 retries with 10 s linear backoff moved 24.7 GB (60 files) at 13-17 MB/s per file with zero errors. The reset is concurrency-induced, not a dead server (`api/status` answered 200 throughout).
basis: `push_source.log` / `push_target.log`: `put error ... ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))` x4 each, then `upload failed`; `push2.log`: 60 x `sha OK`, `PUSH_DONE ['source', 'target']`, `grep -c 'put error'` = 0. Logs in the session scratch; the runbook's 21:43-22:33 entries quote them.
re-verify: grep -n "ConnectionResetError" docs/2026-09-08-n420-target-dump-runbook.md | head -2
