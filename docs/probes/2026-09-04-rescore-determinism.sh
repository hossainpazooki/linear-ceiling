#!/bin/bash
# Is the cross-arm re-score difference hardware or thread nondeterminism?
# (a) WSL run vs the Windows home run (same machine, different OS/BLAS); (b) two identical WSL runs;
# (c) a single-thread WSL run vs the box and vs the multi-thread WSL run.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd ~/kvt-wsl
R=/mnt/c/Users/hossa/dev/linear-ceiling/results/e9
STEM=20241016_composio_swekit__astropy__astropy-14182_traj_sw68
score() {  # $1 = out prefix, rest = env
  env "${@:2}" .venv/bin/python scripts/score_positions.py --same-src $R/scratch/$STEM/same_src --same-tgt $R/scratch/$STEM/same_tgt \
    --cross-src $R/scratch/$STEM/cross_src --mapper mappers/qwen3-0.6b-to-1.7b/k1 --pairs $R/align/$STEM.npz \
    --out ~/wsl-recheck/$1.json --per-token ~/wsl-recheck/$1.tokens.npz >/dev/null
}
echo "== run2 (default threads) $(date -u +%H:%M:%S)"; score run2 X=1
echo "== run-1thread $(date -u +%H:%M:%S)"; score t1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "== compare $(date -u +%H:%M:%S)"
.venv/bin/python - <<EOF
import numpy as np, torch
print("torch threads default:", torch.get_num_threads())
H="$HOME/wsl-recheck"; R="$R"; S="$STEM"
sets = {"box": np.load(f"{R}/tokens/{S}.tokens.npz"), "win": np.load(f"{R}/recheck/{S}.tokens.npz"),
        "wsl1": np.load(f"{H}/{S}.tokens.npz"), "wsl2": np.load(f"{H}/run2.tokens.npz"), "wsl_t1": np.load(f"{H}/t1.tokens.npz")}
def cmp(a, b, arm):
    x, y = sets[a][arm].astype(np.float64), sets[b][arm].astype(np.float64)
    rel = np.abs(x-y)/np.maximum(np.abs(x),1e-30); return f"eq={(x==y).mean():.4f} maxrel={rel.max():.1e}"
for arm in ("same_K", "cross_K", "cross_V"):
    print(arm)
    for a, b in (("wsl1","wsl2"), ("wsl1","wsl_t1"), ("wsl1","win"), ("wsl_t1","box"), ("wsl1","box"), ("win","box")):
        print(f"   {a:6s} vs {b:6s}: {cmp(a,b,arm)}")
EOF
echo "DETERMINISM-DONE $(date -u +%H:%M:%S)"
