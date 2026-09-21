# A PID taken from `$!` after `setsid nohup bash -c '…'` is the wrapper's: SIGTERM to it leaves the driver running

ts: 2026-09-21T02:38:05Z
commit: 3d2fbb14d3919cd2e798f4ffbe5132506cef1c7b
session: carryover-iclr-pickup-drift-wrapup (e7805827; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\e7805827-47f9-400a-a107-71d2eeb94fb2.jsonl)
status: verified
fact: On branch `llama-second-family` at 7f83cea (PR #5, not on main), the sitting launcher starts the E9 driver as a
foreground CHILD of a `bash -c` wrapper and records `$!`, which is the wrapper's PID. The stop command sends SIGTERM to
that one PID, and the partial-close check then treats "that PID is dead" as "the driver stopped". On Linux a bash
wrapper with no trap dies on SIGTERM at once and its foreground child keeps running, re-parented. So the stop protocol
entry 0043 registers ("stop the driver, then close the partial") is not what the code does: a partial can be certified
while the driver is still writing. It did not bear on 0044, which scored 28 of 28. Fix by `exec`-ing the driver in the
wrapper, or by signalling and probing the process group.
basis: at main 3d2fbb1, 2026-09-21T02:38:05Z, `git show 7f83cea:tools/runpod/sitting_b.sh | grep -n …` printed
  `696:setsid nohup bash -c '`, `712:  "$lc_py" -u -m linear_ceiling.e9 --config "config/$exp.toml" || rc=$?`,
  `770:pid=$!`; `git show 7f83cea:tools/runpod/rp.py | grep -n 'kill -TERM "\$p"'` printed line 611. Reproduction under
  WSL (Linux semantics; the pod is Linux, and Git Bash on Windows does not reproduce it): a `setsid nohup bash -c "sleep
  40; echo done"` wrapper, `kill -TERM <wrapper>`, then `kill -0` on each printed `wrapper dead` and
  `child STILL RUNNING`. First found by an outside review of PR #5; posted to the PR as issuecomment-5754565968.
re-verify: git show 7f83cea:tools/runpod/sitting_b.sh | grep -n "setsid nohup bash -c\|^pid=\$!"   # expect: 696 and 770 (needs origin/llama-second-family fetched; once the branch is fixed, check its new head instead)
