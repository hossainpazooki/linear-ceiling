#!/bin/bash
# Break the circle: re-score one kept dump on a Linux platform matching the box (torch 2.11.0+cu128 CPU path,
# python 3.12, latest numpy) and compare per-token squares to the box record bit-for-bit.
set -euo pipefail
cd ~
if [ ! -d kvt-wsl ]; then git clone -q /mnt/c/Users/hossa/dev/kv-transfer-replication kvt-wsl; fi
cd kvt-wsl && git checkout -q d5786df91f55629933067e3c4bb14f1288c4bef2
if [ ! -x ~/.local/bin/uv ]; then curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; fi
export PATH="$HOME/.local/bin:$PATH"
if true; then
  rm -rf .venv
  uv venv --python /usr/bin/python3.12 .venv
  uv pip install --python .venv/bin/python torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
  uv pip install --python .venv/bin/python -e .
fi
.venv/bin/python -c "import torch, numpy; print('wsl torch', torch.__version__, 'numpy', numpy.__version__)"
mkdir -p mappers/qwen3-0.6b-to-1.7b
cp /mnt/c/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.json /mnt/c/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.safetensors mappers/qwen3-0.6b-to-1.7b/
R=/mnt/c/Users/hossa/dev/linear-ceiling/results/e9
STEM=20241016_composio_swekit__astropy__astropy-14182_traj_sw68
mkdir -p ~/wsl-recheck
echo "== scoring $STEM $(date -u +%H:%M:%S)"
.venv/bin/python scripts/score_positions.py --same-src $R/scratch/$STEM/same_src --same-tgt $R/scratch/$STEM/same_tgt \
  --cross-src $R/scratch/$STEM/cross_src --mapper mappers/qwen3-0.6b-to-1.7b/k1 --pairs $R/align/$STEM.npz \
  --out ~/wsl-recheck/$STEM.json --per-token ~/wsl-recheck/$STEM.tokens.npz
.venv/bin/python - <<EOF
import numpy as np, json
box = np.load("$R/tokens/$STEM.tokens.npz"); wsl = np.load("$HOME/wsl-recheck/$STEM.tokens.npz")
for arm in box.files:
    a, b = box[arm].astype(np.float64), wsl[arm].astype(np.float64)
    rel = np.abs(a-b)/np.maximum(np.abs(a),1e-30)
    print(f"{arm:8s} bit-identical frac={(a==b).mean():.4f} max rel={rel.max():.1e} max abs={np.abs(a-b).max():.1e}")
bj = json.load(open("$R/scores/$STEM.json")); wj = json.load(open("$HOME/wsl-recheck/$STEM.json"))
print("layer-mean max |d|:", max(abs(bj[k]-wj[k]) for k in ("same_K_r2_layer_mean","same_V_r2_layer_mean","cross_K_r2_layer_mean","cross_V_r2_layer_mean")))
EOF
echo "WSL-RESCORE-DONE $(date -u +%H:%M:%S)"
