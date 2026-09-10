# tools/ec2 — driving a rented EC2 GPU instance from home over ssh

The ssh form of `tools/jupyterhub/` (which drives a JupyterHub-only box). First used for the E9-long sitting,
2026-09-10 (runbook `docs/2026-09-10-e9l-gpu-runbook.md`). The protocol is `docs/gpu-experiment-protocol.md`
R1–R12 unchanged; the only thing a rented instance changes is the release step (R7 step 6: terminate and prove
it, instead of stopping a hub server) and that nobody else shares the login (R7 step 0 still runs and is expected
to find only us).

| script | runs | what |
|---|---|---|
| `box.sh` | home | `up` / `status` / `ssh` / `put` / `stop` / `terminate` for ONE instance; pinned AMI, key, security group; state in `~/.lc-e9l-box.json` |
| `setup.sh` | box | idempotent: uv, both clones at the pins (detached), the two venvs (upstream torch cu128 2.11.0, linear-ceiling CPU), mapper by sha, traces from the home tarball checked against the manifest, `e9 --check`, `--align-only`, versions, a 24 h self-halt (stop, not terminate) |
| `probe_e9l.py` | box | R2: peak CUDA memory of the pinned scaled forward at T = 32,768 / 65,536 / 80,111, both models |
| `run.sh` | box | R4: rotate the log, launch the driver detached with `python -u` (a buffered stdout showed nothing until exit on 09-10), exit code to `~/e9l.rc` |
| `verify_mirror.py` | home | R6: re-hash every fingerprinted file of the mirror from raw bytes against `report.json`, independently of the puller; prints the report sha (R7 step 1) |
| `release_sweep.sh` | box | R7 steps 0/2/3/4/5 in order, stop at the first failure; deletes only the HF cache, and only after the listings pass |
| `pull.py` | home | R5/R6: mirror small records + box logs every two minutes; stream each kept directory home with tar-over-ssh, verify every fingerprint against `report.json`, only then delete it on the box; exits when complete and everything is home |

```bash
tools/ec2/box.sh up                                   # prints BOX=ubuntu@<ip>
tools/ec2/box.sh put "$MAPPER/k1.json" k1.json && tools/ec2/box.sh put "$MAPPER/k1.safetensors" k1.safetensors
tools/ec2/box.sh put traces.tar.gz traces.tar.gz      # tar -czf traces.tar.gz traces  from the linear-ceiling root
for f in setup.sh run.sh probe_e9l.py; do tools/ec2/box.sh put tools/ec2/$f $f; done
tools/ec2/box.sh ssh 'setsid nohup bash ~/setup.sh > ~/setup.log 2>&1 < /dev/null &'      # then poll ~/setup.rc
tools/ec2/box.sh ssh '~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py > ~/probe.log 2>&1; tail -3 ~/probe.log'
tools/ec2/box.sh ssh 'bash ~/run.sh'                  # or: bash ~/run.sh --resume
BOX=ubuntu@<ip> .venv/Scripts/python.exe tools/ec2/pull.py e9l   # long-running; on Windows start it hidden
tools/ec2/box.sh terminate                            # R7 step 6, after the release checklist
```

Box scripts must be LF; `git config core.autocrlf` on a Windows clone can hand you CRLF copies, so `put` them
after `sed -i 's/\r$//'` or from a `--eol=lf` checkout. The instance halts itself 24 h after setup (behaviour
"stop": the volume and everything on it survive, compute billing ends); `sudo shutdown -c` cancels that.
