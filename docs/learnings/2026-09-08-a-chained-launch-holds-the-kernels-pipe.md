ts: 2026-09-08T20:57:00Z
commit: 4fdc50a
session: Claude Code session 878feb6f, second box setup launch
status: verified
fact: On a JupyterHub kernel exec (`subprocess.run(..., capture_output=True)`), `a && b && setsid nohup c > log 2>&1 &` backgrounds the WHOLE `&&` chain in a subshell whose stdout is the kernel's captured pipe, so the cell blocks until `c` finishes and the websocket times out (the detached process itself runs fine). The launch line must stand alone: `a; b; setsid nohup c > log 2>&1 < /dev/null &`.
basis: `jh.py exec 'cd ~ && rm -f ~/setup.rc && mv ... && setsid nohup bash ~/setup2.sh > ~/setup.log 2>&1 < /dev/null & sleep 2; ...' 20` raised `websocket._exceptions.WebSocketTimeoutException: Connection timed out` at home while a fresh kernel showed `3463028 bash /home/jupyter-rrhs-66f0/setup2.sh` running and `setup.log` advancing.
re-verify: grep -n "setsid nohup" tools/jupyterhub/README.md docs/2026-09-08-n420-target-dump-runbook.md | head -3
