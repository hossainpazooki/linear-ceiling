#!/bin/bash
# E9-long box setup on a rented EC2 g6e (1x L40S 48 GB), Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04).
# Idempotent; writes EXIT=<rc> to ~/setup.rc on exit (the home poller keys on that file, never on pgrep).
# Inputs uploaded to ~ before this runs: k1.json, k1.safetensors (the mapper, R3), traces.tar.gz (the manifest's bytes).
# Pins below are entry 0035's; the mapper and manifest shas are the R3 table of docs/2026-09-10-e9l-gpu-runbook.md.
trap 'echo "EXIT=$?" > ~/setup.rc' EXIT
set -euo pipefail
LC_SHA=3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806          # linear-ceiling: 0035 on the ledger, e9l instrument, runbook commit's parent
UP_SHA=063f4023fdde67dedbee01a92518ce7f83f6cf5d          # upstream: the RoPE-spec commit (config/e9l.toml upstream_sha)
MAPPER_JSON_SHA=2fd05c333156607436af128ccd7a009f175f13138d27e4126588c24f515cc86e
MAPPER_ST_SHA=cd6a8d939b36db901f50e13bae446aef833f5d2ea7276658f499e993e63607f2
HOME_COVERAGE_SHA12=492d8f0db8d0                          # results/e9l/align/coverage.json at home (0035 cites it)
cd ~
echo "== $(date -u +%FT%TZ) host"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
df -h / | tail -1; nproc; free -g | head -2
echo "== uv"
[ -x ~/.local/bin/uv ] || curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null
export PATH=$HOME/.local/bin:$PATH; uv --version
echo "== clones at the pins (detached)"
[ -d ~/kv-transfer-replication/.git ] || git clone -q https://github.com/hossainpazooki/kv-transfer-replication.git
git -C ~/kv-transfer-replication fetch -q origin && git -C ~/kv-transfer-replication checkout -q --detach "$UP_SHA"
[ -d ~/linear-ceiling/.git ] || git clone -q https://github.com/hossainpazooki/linear-ceiling.git
git -C ~/linear-ceiling fetch -q origin && git -C ~/linear-ceiling checkout -q --detach "$LC_SHA"
git -C ~/kv-transfer-replication log --oneline -1; git -C ~/linear-ceiling log --oneline -1
echo "== upstream env: python 3.12, torch 2.11.0+cu128 (the 09-04 / 09-08 stack), transformers 5.15.1, numpy 2.5.2"
cd ~/kv-transfer-replication
[ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv
uv pip install -q --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu128 torch==2.11.0
uv pip install -q --python .venv/bin/python -e . transformers==5.15.1 numpy==2.5.2
echo "== linear-ceiling env (CPU torch; the driver calls the upstream by subprocess in its own venv)"
cd ~/linear-ceiling
[ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv
uv pip install -q --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch
uv pip install -q --python .venv/bin/python -e ".[dev]" numpy==2.5.2
echo "== mapper by sha (R3; gitignored upstream artifact, the 2026-09-04 launch died without it)"
MD=~/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b; mkdir -p "$MD"
for f in k1.json k1.safetensors; do [ -f "$MD/$f" ] || mv ~/"$f" "$MD/$f"; done
echo "$MAPPER_JSON_SHA  $MD/k1.json" | sha256sum -c -
echo "$MAPPER_ST_SHA  $MD/k1.safetensors" | sha256sum -c -
echo "== traces: the home tarball, checked against the committed manifest (both directions + bytes)"
[ -d ~/linear-ceiling/traces ] || tar -xzf ~/traces.tar.gz -C ~/linear-ceiling
.venv/bin/python -m linear_ceiling.e7_manifest check | tail -1 | tee ~/manifest_check.out | grep -q "^manifest ok"
echo "== gate"
.venv/bin/python -m linear_ceiling.e9 --check --config config/e9l.toml
echo "== alignment on the box (expected to reproduce home's coverage.json sha $HOME_COVERAGE_SHA12; a mismatch is reported, not fatal here)"
.venv/bin/python -m linear_ceiling.e9 --align-only --config config/e9l.toml | tail -2
sha256sum results/e9l/align/coverage.json
echo "== versions"
~/kv-transfer-replication/.venv/bin/python -c "import torch,transformers,numpy;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.cuda.get_device_name(0));print('transformers',transformers.__version__,'numpy',numpy.__version__)"
.venv/bin/python -c "import sys,torch,numpy;print('lc python',sys.version.split()[0],'torch',torch.__version__,'numpy',numpy.__version__)"
echo "== safety: the box halts itself in 24 h (shutdown behaviour = stop: billing ends, the volume stays); cancel with sudo shutdown -c"
sudo shutdown -h +1440 > /dev/null 2>&1 || true
echo "SETUP_DONE $(date -u +%FT%TZ)"
