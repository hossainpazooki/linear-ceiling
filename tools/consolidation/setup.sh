#!/usr/bin/env bash
# Run on the existing A100 host. Repeated setup validates the same locked environment.
set -euo pipefail
repo=$(cd "$(dirname "$0")/../.." && pwd)
uv_bin=${UV_BIN:-$HOME/.local/bin/uv}
venv=${CARRYOVER_VENV:-$HOME/carryover-venv}
[ -x "$uv_bin" ] || python3 -m pip install --user uv==0.8.22
[ -x "$venv/bin/python" ] || "$uv_bin" venv --python 3.12 "$venv"
"$uv_bin" pip sync --python "$venv/bin/python" "$repo/tools/consolidation/requirements-linux.lock"
"$uv_bin" pip install --python "$venv/bin/python" --no-deps -e "$repo"
"$venv/bin/python" - <<'PY'
import torch, transformers, numpy
assert torch.cuda.is_available()
x = torch.ones((32,32),device="cuda")
assert (x@x).sum().item()==32768
print({"torch":torch.__version__,"transformers":transformers.__version__,"numpy":numpy.__version__,
       "cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name()})
PY
