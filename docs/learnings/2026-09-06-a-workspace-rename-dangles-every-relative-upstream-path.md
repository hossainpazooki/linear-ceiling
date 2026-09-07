# A workspace rename dangles every relative upstream path at once, and the gate crashed instead of refusing

kills: (nothing)
ts: 2026-09-06T23:35:00Z
commit: 7ce63cf7366d9b2a5fee40d0f00380ea78c1f4e0
session: lcfm-sprint-pickup (e992199e-cc8f-4335-bce4-fa177630087c)
status: verified
fact: the upstream checkout is addressed by ONE relative name in six configs (`upstream_path =
"../kv-transfer-replication"` in e8/e8a/e8c/e9/e9c/seal), in UPSTREAM.md, CLAUDE.md and the runbook, and
by an absolute path baked into the upstream's own editable install (`__editable___*_finder.py` MAPPING).
Renaming the directory (`~/dev/kv-transfer-replication` -> `~/dev/kv-transfer`, 2026-09-06 12:49:13 local,
actor not established) therefore broke every gate and summarizer that reads the upstream in one stroke,
AND broke the upstream's own subprocess-launched scripts (`ModuleNotFoundError: No module named 'kvt'`
in 7 of its tests). `upstream_gate.check_upstream` did not refuse: it handed the missing path to `git`
as `cwd` and died with `NotADirectoryError` -- a crash, not a `{who} REFUSED` line, so `e8 --check`
produced a traceback with exit 0 from the shell's point of view. Renaming back was refused with
`Permission denied` because running Claude Code sessions hold handles on every depth-1 repo. Rule: a
gate that reads a foreign path checks the path exists before it shells out, and a workspace-level rename
is a change to every repo that names the old name relatively -- grep the workspace for the old name
before renaming, and rename only with every session closed.
basis: `ls -d ~/dev/kv-transfer-replication` -> "No such file or directory" and `ls -d ~/dev/kv-transfer` present
  at 2026-09-06 16:53Z; `stat ~/dev` modify time 12:49:13.33 -0400 equal to the birth of `~/dev/traverse/`;
  `.venv/Lib/site-packages/__editable___kv_transfer_replication_0_0_1_finder.py` in the upstream venv maps
  `kvt` to `C:\Users\hossa\dev\kv-transfer-replication\kvt`; upstream `pytest -q` -> `7 failed, 138 passed`, every
  failure `No module named 'kvt'` from a `scripts/*.py --help` subprocess; `e8 --check --config config/e8a.toml`
  at 7ce63cf ended in `NotADirectoryError: [WinError 267]` from `upstream_gate.py` line 26; `mv kv-transfer
  kv-transfer-replication` -> `Permission denied`, tree intact on both sides afterwards (HEAD 223f469, 0/0).
  Fixed the crash in this commit set (`upstream_gate.check_upstream` refuses by name when the path is not a
  directory; `tests/test_upstream_gate.py`).
re-verify: cd ~/dev/linear-ceiling && .venv/Scripts/python.exe -c "from linear_ceiling.upstream_gate import check_upstream; from pathlib import Path; check_upstream(Path('no-such-dir'), 'a'*40, ('kvt',), who='E8')"   # RuntimeError "E8 REFUSED: upstream checkout ... does not exist", not NotADirectoryError
