ts: 2026-09-08T20:44:30Z
commit: 4fdc50a
session: Claude Code session 878feb6f (n = 420 target dump on the Algoverse grant), box setup attempt 1
status: verified
fact: `download.pytorch.org/whl/cu128` carries torch 2.7.0 through 2.11.0 only, so a home pin of `torch==2.13.0` (the CPU build at home) cannot be matched on a CUDA 12.8 driver (570.148.08); the box run pins 2.11.0+cu128, which is also what E9 ran on 2026-09-04 (entry 0028). Version parity with home is not available for GPU runs and must not be claimed.
basis: `~/venv/bin/pip install -q --index-url https://download.pytorch.org/whl/cu128 torch==2.13.0` on the box printed `ERROR: Could not find a version that satisfies the requirement torch==2.13.0 (from versions: 2.7.0+cu128, 2.7.1+cu128, 2.8.0+cu128, 2.9.0+cu128, 2.9.1+cu128, 2.10.0+cu128, 2.11.0+cu128)`; the log is `data/kv/qwen3-0.6b-to-1.7b-n420/box-logs-2026-09-08/setup.attempt1.log` in the upstream mirror and in the HF backup.
re-verify: grep -n "torch==2.11.0" docs/2026-09-08-n420-target-dump-runbook.md | head -2
