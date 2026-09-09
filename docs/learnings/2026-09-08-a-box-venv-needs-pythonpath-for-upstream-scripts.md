ts: 2026-09-08T22:28:20Z
commit: a71c3b4
session: Claude Code session 878feb6f, first fit launch on the box
status: verified
fact: The upstream's `scripts/*.py` import `kvt` from the checkout root; home's upstream venv has `kvt` installed, a fresh box venv does not, so a launcher without `export PYTHONPATH=$PWD` dies at import. The E9 dump launcher carried the export; a new launcher written from scratch forgot it. `fit.sh`'s pre-checks (pin, clean tree, 60/60 input hashes) all passed before the import failed, so the halt was cheap only because the launch was the last step.
basis: `~/kv-transfer-replication/fit.log` (rotated to `fit.20260908T222836Z.halt.log`): `File "/home/jupyter-rrhs-66f0/kv-transfer-replication/scripts/fit_mapper.py", line 8, in <module> / from kvt.data import KVDump / ModuleNotFoundError: No module named 'kvt'`; `~/fit.rc` = `EXIT=1`. The halt log is in the mirror's `box-logs-2026-09-08/` and the HF backup.
re-verify: grep -c "PYTHONPATH" tools/jupyterhub/README.md docs/2026-09-08-n420-target-dump-runbook.md
