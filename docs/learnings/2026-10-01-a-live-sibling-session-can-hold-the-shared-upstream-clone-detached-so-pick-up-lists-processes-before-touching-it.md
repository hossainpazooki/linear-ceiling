# A live sibling session can hold the shared upstream clone detached; pick-up lists processes before touching it

ts: 2026-10-01T18:03:00Z
commit: a6a746d
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: Both 10-01 briefs said `../kv-transfer-replication` sits on `main`. At pick-up it was `HEAD (no branch)` at `06f8d55`, because another Claude session on this machine ("Carryover: MLSys NeurIPS Sprint") had detached it at 14:00:20 local and was running `summarize_e9 --config config/e9f.toml` plus the upstream `score_mapper.py` subprocess. One clone means one cell at a time ACROSS SESSIONS too: a brief's clone-state claim is true only for the session that wrote it, and a pick-up that read the gate then would have refused for a reason the brief could not know.
basis: at a6a746d, ~18:03Z (the `date -u` call that followed printed 18:02Z): `git -C ../kv-transfer-replication status --short --branch` printed `## HEAD (no branch)`; `git reflog --date=iso -1` printed `06f8d55 HEAD@{2026-10-01 14:00:20 -0400}: checkout: moving from main to 06f8d55...`; `Get-CimInstance Win32_Process` listed PID 30656 `...python.exe -m linear_ceiling.summarize_e9 --config config/e9f.toml` created 2:01:37 PM; ListAgents showed the sibling session in state `shell`. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: git -C ../kv-transfer-replication reflog --date=iso -4 | grep -c '06f8d55'   # expect >= 2: the 14:00 detach and the later return to main
