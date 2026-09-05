# tools/jupyterhub — driving a JupyterHub-only GPU box from home

Two scripts, both configured from the environment only (`JH_URL`, `JH_USER`, `JH_TOKEN`, optional
`JH_STATE_DIR`), used on the E9 GPU day 2026-09-04 against an Algoverse TLJH grant with no ssh.
The protocol they implement is `docs/gpu-experiment-protocol.md`; the run they served is
`docs/2026-09-02-e9-gpu-runbook.md` and entries 0026–0029.

| script | what it does |
|---|---|
| `jh.py` | `exec` a shell command on the box through a python3 kernel; `up`/`down` single files; `ls` a dir |
| `pull.py [exp]` | the pull → verify (sha256 vs `report.json` `kept_dumps`) → delete loop, every two minutes, until `complete: true` and every kept dump is home |

Requirements on the local machine: `requests`, `websocket-client` (both in the repo `.venv`).

```bash
export JH_URL=http://<hub-ip> JH_USER=<hub-user> JH_TOKEN=<token from POST /hub/api/users/<user>/tokens>
.venv/Scripts/python.exe tools/jupyterhub/jh.py exec 'nvidia-smi --query-gpu=name,memory.total --format=csv' 30
.venv/Scripts/python.exe tools/jupyterhub/pull.py e9        # long-running; on Windows start it hidden, not from a 10-min Bash
```

Rotate the run log before every relaunch (`mv e9.log "e9.$(date -u +%Y%m%dT%H%M%SZ).halt.log"`) and
pull the rotated file home before launching again; a `> e9.log` redirect on relaunch is a silent
delete of the previous attempt's halt log (learnings 2026-09-04).
