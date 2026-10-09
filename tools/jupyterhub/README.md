# tools/jupyterhub — driving a JupyterHub-only GPU box from home

Two scripts, both configured from the environment only (`JH_URL`, `JH_USER`, `JH_TOKEN`, optional
`JH_STATE_DIR`), used on the E9 GPU day 2026-09-04 against an Algoverse TLJH grant with no ssh.
The protocol they implement is `docs/gpu-experiment-protocol.md`; the run they served is
`docs/2026-09-02-e9-gpu-runbook.md` and entries 0026–0029.

| script | what it does |
|---|---|
| `jh.py` | `exec` a shell command on the box through a python3 kernel; `up`/`down` single files; `ls` a dir; `stop` the server and read it back |
| `pull.py [exp]` | the pull → verify (sha256 vs `report.json` `kept_dumps`) → delete loop, every two minutes, until `complete: true` and every kept dump is home |
| `launch.sh` | home, one command for a multi-level sitting (E-TRUNC by default): prerequisites, upload, `go.sh` detached, then `tools/ec2/pull.py` per level over this transport (it handles bridge dumps; prefer it to `pull.py` here) |
| `go.sh` | box: mapper from the public e9 dataset, `setup.sh` + alignment per level (sha must equal home's), the R2 probe, the levels in order with a free-disk gate; status in `~/go.status` |

A multi-level E9 sitting on an Algoverse slice (built 2026-10-05 for E-TRUNC, which then ran on RunPod as 0057; kept
for the next Qwen cell that fits a slice — Qwen3-1.7B fp32 measured 16.72 GiB at 32,768 on a 1g.20gb slice and 31.56 GiB
at 80,111 on an L40S, so a 40 GB slice should take 80K; `go.sh`'s probe decides):

```bash
export JH_URL=https://<hub> JH_USER=<user> JH_TOKEN=<token from the hub's /hub/token page>
LEVELS="<exp> ..." tools/jupyterhub/launch.sh      # MAX_S = the run's longest prefill; MIN_FREE_GIB = box disk gate (70)
# release (R7), after every puller exited and verify_mirror.py passed per level; LAUNCH_UTC from ~/lc-sitting-launch-utc.txt:
for e in $LEVELS; do .venv/bin/python tools/jupyterhub/jh.py exec "cd ~ && EXP=$e LEVELS='$LEVELS' LAUNCH_UTC='<YYYY-MM-DD HH:MM>' bash ~/release_sweep.sh > ~/release.$e.log 2>&1; tail -3 ~/release.$e.log" 120; done
.venv/bin/python tools/jupyterhub/jh.py stop        # R7 step 6 on a hub: stop the server and read it back
```

Before a window: the home mirror must hold every level's kept + bridge dumps at once (E-TRUNC was 213 GB over four
levels); any Qwen summary needs τ, which needs the n = 50 generic dumps under `../kv-transfer-replication/data/kv/` and
`results/e8/report.json` (in no public dataset); the box writes LF, so pass coverage shas of LF files; the machine is
wiped at the end of the window, so the pullers must be running from launch.

Requirements on the local machine: `requests`, `websocket-client` (both in the repo `.venv`).

```bash
export JH_URL=http://<hub-ip> JH_USER=<hub-user> JH_TOKEN=<token from POST /hub/api/users/<user>/tokens>
.venv/Scripts/python.exe tools/jupyterhub/jh.py exec 'nvidia-smi --query-gpu=name,memory.total --format=csv' 30
.venv/Scripts/python.exe tools/jupyterhub/pull.py e9        # long-running; on Windows start it hidden, not from a 10-min Bash
```

Rotate the run log before every relaunch (`mv e9.log "e9.$(date -u +%Y%m%dT%H%M%SZ).halt.log"`) and
pull the rotated file home before launching again; a `> e9.log` redirect on relaunch is a silent
delete of the previous attempt's halt log (learnings 2026-09-04).
