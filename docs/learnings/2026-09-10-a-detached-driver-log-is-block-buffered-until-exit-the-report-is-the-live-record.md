# A detached driver's stdout log is block-buffered until exit when python runs without `-u`; the per-handoff checkpoint file, not the log, is the live record

kills: (nothing)
ts: 2026-09-10T00:10:31Z
commit: 3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806
session: linear-ceiling-e9l-box (018fwd195AS7uS2tvJdgSoYP)
status: verified
fact: `tools/ec2/run.sh` launched `python -m linear_ceiling.e9 … > ~/e9l.log` detached with stdout to a file. CPython
block-buffers stdout when it is not a tty, and the driver prints with `print(…)` (no `flush=True`), so `~/e9l.log`
held nothing but the tokenizer's stderr progress bar for the whole 80-minute run while `report.json` on the box
advanced handoff by handoff (the home puller reported `scored 6/35` at 00:08:58Z; a box-side wait keyed on
`grep -c '^\[bridge\]' ~/e9l.log` saw 0 lines at 00:10:31Z and timed out). All 38 lines (`[bridge]` × 3, `[i/35]`
× 35) appeared together at exit (01:13:09Z). A liveness or progress check keyed on the log would have read a healthy
run as hung; the checkpointed `report.json`, mirrored every round, is the live record. The launcher now passes
`-u`; the stderr half (tqdm) was never buffered, which is why the log was not empty and looked alive.
basis: `results/e9l/logs/pull.log` line `== 00:08:58 scored 6/35; bridge done; complete=False`; the box-side wait's
  output at 00:10:31Z showed no `[bridge]` line (session transcript; the runbook's 00:00–00:10 log entry); the
  pulled `results/e9l/logs/box/e9l.log` (mtime 01:13:09Z) carries all 38 lines.
re-verify: grep -c "^\[" results/e9l/logs/box/e9l.log   # 38 (3 bridge + 35 handoffs), a single flush at exit; and `grep -c "python -u" tools/ec2/run.sh` → 1 after the fix
