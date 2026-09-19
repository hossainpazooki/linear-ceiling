#!/usr/bin/env bash
# RunPod-native Sitting B orchestration: E9 short, from exact pins through a detached run.
#
# This script deliberately does NOT create, stop, or terminate a pod. RunPod container storage is
# ephemeral, so normal completion is: this launcher writes SITTING_B_OK -> the home puller verifies
# every byte -> the HOME side terminates and reads absence back from the API. `shutdown`, `halt`,
# runpodctl and provider credentials have no place here.
#
# Required environment:
#   PAIR UP_REPO UP_SHA LC_REPO LC_SHA
#   MAPPER_JSON_SHA MAPPER_ST_SHA COVERAGE_SHA256
#
# Required staged inputs (paths may be overridden):
#   /workspace/k1.json, /workspace/k1.safetensors
#   /workspace/traces.tar.gz
#   /workspace/tau.json                 (the home calibration that §8 requires before renting)
#   either /workspace/hf-cache.tar.gz, an already-populated HF_HOME, or HF_TOKEN for a process-only
#   snapshot download. The token is unexported before logging, passed only to snapshot_download,
#   never saved, and erased from the shell variable immediately afterward.
#
# Optional environment:
#   EXP=e9f WORK=/workspace HF_HOME=$WORK/hf WEIGHTS_TGZ=$WORK/hf-cache.tar.gz
#   MAPPER_JSON=$WORK/k1.json MAPPER_ST=$WORK/k1.safetensors
#   TRACES_TGZ=$WORK/traces.tar.gz CALIBRATION_JSON=$WORK/tau.json CALIBRATION_SHA256=<64 hex>
#   MIN_GPU_MARGIN_GIB=4 REMOVE_WEIGHTS_TGZ=1
#
# Relaunch semantics are automatic and fail closed:
#   no report       -> plain E9 run
#   incomplete      -> --resume, but only after the recorded controls still hash correctly
#   complete:true   -> skip the driver and only produce terminal state + the final small-file manifest
# A partial close IS registered for this cell (entry 0042, [e9.order] allow_partial = true) but it
# never happens on the box: box disk is ephemeral, and after a hard kill it is gone exactly when a
# close is needed. The close is home-side on the verified mirror -- `pull_verify_b.py --final-partial`
# proves the last fully verified checkpoint and writes the terminate receipt, then `e9 --close-partial`
# stamps it. A report arriving HERE already carrying a partial is therefore out of order and refused.
set -euo pipefail

PAIR="${PAIR:?PAIR is required}"
UP_REPO="${UP_REPO:?UP_REPO is required}"
UP_SHA="${UP_SHA:?UP_SHA is required (40 lowercase hex)}"
LC_REPO="${LC_REPO:?LC_REPO is required}"
LC_SHA="${LC_SHA:?LC_SHA is required (40 lowercase hex)}"
MAPPER_JSON_SHA="${MAPPER_JSON_SHA:?MAPPER_JSON_SHA is required}"
MAPPER_ST_SHA="${MAPPER_ST_SHA:?MAPPER_ST_SHA is required}"
COVERAGE_SHA256="${COVERAGE_SHA256:?COVERAGE_SHA256 is required (the full home coverage.json sha256)}"

EXP="${EXP:-e9f}"
REHEARSAL="${REHEARSAL:-0}"          # 1 = $0 dry run: clone, venvs, traces, mapper, gate; stop before weights
WORK="${WORK:-/workspace}"
HF_HOME="${HF_HOME:-$WORK/hf}"
WEIGHTS_TGZ="${WEIGHTS_TGZ:-$WORK/hf-cache.tar.gz}"
TRACES_TGZ="${TRACES_TGZ:-$WORK/traces.tar.gz}"
MAPPER_JSON="${MAPPER_JSON:-$WORK/k1.json}"
MAPPER_ST="${MAPPER_ST:-$WORK/k1.safetensors}"
CALIBRATION_JSON="${CALIBRATION_JSON:-$WORK/tau.json}"
CALIBRATION_SHA256="${CALIBRATION_SHA256:-}"
MIN_GPU_MARGIN_GIB="${MIN_GPU_MARGIN_GIB:-4}"
REMOVE_WEIGHTS_TGZ="${REMOVE_WEIGHTS_TGZ:-1}"

LC_DIR="$WORK/linear-ceiling"
UP_DIR="$WORK/kv-transfer-replication"
SETUP_LOG="$WORK/sitting_b.setup.log"
PROBE_LOG="$WORK/sitting_b.probe.log"
RUN_LOG="$WORK/$EXP.log"
RC_FILE="$WORK/$EXP.rc"
STATUS_FILE="$WORK/$EXP.status"
SETUP_STATUS="$WORK/sitting_b.setup.status"
LAUNCH_LOG="$WORK/sitting_b.launches.log"
PID_FILE="$WORK/$EXP.pid"
READY_FILE="$WORK/$EXP.launch.ready"
FINAL_MANIFEST="$WORK/$EXP.final.sha256"
EVIDENCE_DIR="$WORK/sitting_b.evidence"

# Do this before spawning tee: a secret inherited as HF_TOKEN must not remain in any helper's
# environment. This private, non-exported shell value exists only until the download block.
HF_DOWNLOAD_TOKEN="${HF_TOKEN-}"
unset HF_TOKEN

mkdir -p "$WORK"
exec > >(tee -a "$SETUP_LOG") 2>&1

STEP="init"
say() { echo "[$(date -u +%FT%TZ)] $*"; }
step() { STEP="$1"; say "== $1"; }
refuse() { say "REFUSED: $*"; return 1; }
atomic_line() {
  local path="$1" line="$2" tmp="${1}.tmp.$$"
  printf '%s\n' "$line" > "$tmp"
  mv -f -- "$tmp" "$path"
}
on_exit() {
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    trap - EXIT
    say "SITTING_B_SETUP_FAILED step=$STEP rc=$rc"
    atomic_line "$SETUP_STATUS" "SITTING_B_SETUP_FAILED step=$STEP rc=$rc"
  fi
}
trap on_exit EXIT

for value in "$UP_SHA" "$LC_SHA"; do
  [[ "$value" =~ ^[0-9a-f]{40}$ ]] || refuse "git pins must be full lowercase commit shas: $value"
done
for value in "$MAPPER_JSON_SHA" "$MAPPER_ST_SHA" "$COVERAGE_SHA256"; do
  [[ "$value" =~ ^[0-9a-f]{64}$ ]] || refuse "artifact pins must be full lowercase sha256 values: $value"
done
if [ -n "$CALIBRATION_SHA256" ]; then
  [[ "$CALIBRATION_SHA256" =~ ^[0-9a-f]{64}$ ]] || refuse "CALIBRATION_SHA256 must be 64 lowercase hex"
fi
[[ "$EXP" =~ ^[A-Za-z0-9._-]+$ ]] || refuse "EXP contains unsafe path characters: $EXP"
[ "$REMOVE_WEIGHTS_TGZ" = 0 ] || [ "$REMOVE_WEIGHTS_TGZ" = 1 ] \
  || refuse "REMOVE_WEIGHTS_TGZ must be 0 or 1"
python3 - "$MIN_GPU_MARGIN_GIB" <<'PY'
import sys
x = float(sys.argv[1])
assert x > 0, "MIN_GPU_MARGIN_GIB must be a real positive margin"
PY

# Refuse a second launcher while the known detached session is still alive. A stale/reused PID is
# treated conservatively: this script never signals any process, ours or otherwise.
if [ -s "$PID_FILE" ]; then
  old_pid="$(tr -cd '0-9' < "$PID_FILE")"
  if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null && [ ! -f "$RC_FILE" ]; then
    refuse "pid $old_pid is still alive and $RC_FILE is absent; refusing a duplicate E9 launch"
  fi
fi

step "host facts"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>&1 \
  | sed 's/^/  gpu: /' || say "  nvidia-smi unavailable (the CUDA gate will refuse later)"
say "  vcpu: $(nproc 2>/dev/null || echo '?')"
for f in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory/memory.limit_in_bytes; do
  [ -r "$f" ] && { say "  cgroup mem ($f): $(<"$f")"; break; }
done
say "  disk: $(df -h "$WORK" | awk 'NR==2{print $4" free of "$2}')"

# Thread cap from the CGROUP QUOTA, never nproc. Sitting A reported nproc 96 against a 7.65-CPU quota
# and ran 111 threads with ~50k throttle events; capping at 8 turned a projected ~55-minute fit into
# 11. nproc on a container host is the HOST's core count and is actively misleading here.
LC_THREADS=""
if [ -r /sys/fs/cgroup/cpu.max ]; then                      # cgroup v2: "<quota> <period>" or "max <period>"
  read -r _q _p < /sys/fs/cgroup/cpu.max || true
  [ "${_q:-max}" != "max" ] && [ "${_p:-0}" -gt 0 ] && LC_THREADS=$(( _q / _p ))
elif [ -r /sys/fs/cgroup/cpu/cpu.cfs_quota_us ] && [ -r /sys/fs/cgroup/cpu/cpu.cfs_period_us ]; then
  _q=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us); _p=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)
  [ "$_q" -gt 0 ] && [ "$_p" -gt 0 ] && LC_THREADS=$(( _q / _p ))
fi
[ -z "$LC_THREADS" ] || [ "$LC_THREADS" -lt 1 ] && LC_THREADS=$(nproc 2>/dev/null || echo 8)
[ "$LC_THREADS" -gt 16 ] && LC_THREADS=16                   # beyond this the reductions thrash, not speed up
export OMP_NUM_THREADS="$LC_THREADS" OPENBLAS_NUM_THREADS="$LC_THREADS" \
       MKL_NUM_THREADS="$LC_THREADS" NUMEXPR_NUM_THREADS="$LC_THREADS" \
       VECLIB_MAXIMUM_THREADS="$LC_THREADS"
if [ -r /sys/fs/cgroup/cpu.max ] || [ -r /sys/fs/cgroup/cpu/cpu.cfs_quota_us ]; then
  say "  thread cap: $LC_THREADS (from the cgroup CPU quota, NOT nproc=$(nproc 2>/dev/null || echo '?'))"
else
  say "  thread cap: $LC_THREADS (NO cgroup quota readable here -- fell back; on the box it is cgroup-derived)"
fi
say "  NOTE: BLAS threading changes float32 reduction order at the last ULP -- the class entry 0028"
say "        registered a cross-platform tolerance for. No registered parameter changes."
say "sitting B pair=$PAIR exp=$EXP"
say "up=$UP_REPO@${UP_SHA:0:12} lc=$LC_REPO@${LC_SHA:0:12}"
say "launcher sha256 $(sha256sum "$0" | awk '{print $1}')"

clone_exact() {
  local dir="$1" repo="$2" sha="$3" label="$4" got dirty
  if [ -e "$dir" ] && [ ! -d "$dir/.git" ]; then
    refuse "$dir exists but is not a git checkout"
  fi
  if [ ! -d "$dir/.git" ]; then
    git clone --quiet "$repo" "$dir"
  fi
  dirty="$(git -C "$dir" status --porcelain --untracked-files=no)"
  [ -z "$dirty" ] || refuse "$label has tracked changes before checkout: $dirty"
  git -C "$dir" fetch --quiet origin "$sha" 2>/dev/null || git -C "$dir" fetch --quiet --all
  git -C "$dir" checkout --quiet --detach "$sha"
  got="$(git -C "$dir" rev-parse HEAD)"
  [ "$got" = "$sha" ] || refuse "$label is at $got, not $sha"
  dirty="$(git -C "$dir" status --porcelain --untracked-files=no)"
  [ -z "$dirty" ] || refuse "$label is tracked-dirty at the requested pin: $dirty"
  say "  $label at $got (detached; tracked files clean)"
}

step "clone at exact shas"
clone_exact "$UP_DIR" "$UP_REPO" "$UP_SHA" upstream
clone_exact "$LC_DIR" "$LC_REPO" "$LC_SHA" linear-ceiling
ROPE_SPEC=063f4023fdde67dedbee01a92518ce7f83f6cf5d
git -C "$UP_DIR" merge-base --is-ancestor "$ROPE_SPEC" HEAD \
  || refuse "UP_SHA does not descend from the RoPE-spec commit $ROPE_SPEC"
say "  upstream descends from the RoPE spec"

step "pinned virtual environments"
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --quiet uv
fi
# The pinned stack is torch 2.11.0+cu128, which has wheels only for manylinux/win -- so a REHEARSAL on
# any other platform (a macOS laptop, say) cannot build it and would stop here, before the traces,
# mapper and gate checks that the rehearsal exists to exercise. In rehearsal mode the torch pin is
# therefore relaxed to whatever the platform has.
# THIS IS A REAL NARROWING, stated rather than hidden: a rehearsal does NOT validate the pinned CUDA
# build. What validates that is the CUDA smoke test on the real box, which runs before the weight pull
# and refuses a card under 70 GiB. Everything else -- shas, clone integrity, RoPE ancestry, tau
# binding, traces vs the committed manifest, the mapper by sha, and the E9 gate -- is exercised for
# real, on freshly cloned bytes.
TORCH_PIN=(--index-url https://download.pytorch.org/whl/cu128 'torch==2.11.0')
if [ "$REHEARSAL" = "1" ]; then
  TORCH_PIN=('torch')
  say "  REHEARSAL: torch pin relaxed to the platform default; the pinned cu128 build is NOT validated here"
fi
( cd "$UP_DIR"
  [ -x .venv/bin/python ] || uv venv --python 3.12 .venv >/dev/null
  uv pip install --quiet --python .venv/bin/python "${TORCH_PIN[@]}"
  uv pip install --quiet --python .venv/bin/python -e . \
    'transformers==5.15.1' 'numpy==2.5.2' )
( cd "$LC_DIR"
  [ -x .venv/bin/python ] || uv venv --python 3.12 .venv >/dev/null
  uv pip install --quiet --python .venv/bin/python \
    --index-url https://download.pytorch.org/whl/cpu 'torch==2.11.0'
  uv pip install --quiet --python .venv/bin/python -e '.[dev]' 'numpy==2.5.2' )
UP_PY="$UP_DIR/.venv/bin/python"
LC_PY="$LC_DIR/.venv/bin/python"
say "  upstream python: $UP_PY"
say "  linear-ceiling python: $LC_PY"

if [ "$REHEARSAL" = "1" ]; then
  say "== CUDA smoke test: SKIPPED (rehearsal; no GPU expected)"
else
step "CUDA smoke test (before any download)"
# Here, not at the first dump: a driver/CUDA mismatch against the pinned cu128 build otherwise
# surfaces ~25 billed minutes in instead of ~8. allowedCudaVersions on the create call should prevent
# it; this proves the filter worked, and refuses cheaply if it did not.
"$UP_PY" -c "
import torch
print(f'  torch {torch.__version__} cuda_available={torch.cuda.is_available()}')
assert torch.cuda.is_available(), 'torch.cuda.is_available() is False'
torch.zeros(1).cuda()
free, total = torch.cuda.mem_get_info()
print(f'  device: {torch.cuda.get_device_name(0)}')
print(f'  gpu memory: {free/2**30:.2f} GiB free of {total/2**30:.2f} GiB')
assert total/2**30 >= 70, f'sitting B needs an 80 GB card; this one reports {total/2**30:.1f} GiB'
" || refuse "torch cannot reach a large-enough GPU on this host"
fi

step "home tau calibration present and bound to this config"
CFG="$LC_DIR/config/$EXP.toml"
[ -f "$CFG" ] || refuse "config/$EXP.toml is absent at LC_SHA"
CAL_DEST="$LC_DIR/results/$EXP/calibration/tau.json"
if [ -f "$CALIBRATION_JSON" ]; then
  mkdir -p "$(dirname "$CAL_DEST")"
  if [ "$CALIBRATION_JSON" != "$CAL_DEST" ]; then
    cp -- "$CALIBRATION_JSON" "$CAL_DEST"
  fi
elif [ ! -f "$CAL_DEST" ]; then
  refuse "$CALIBRATION_JSON is absent; §8 requires home tau calibration before renting the pod"
fi
if [ -n "$CALIBRATION_SHA256" ]; then
  printf '%s  %s\n' "$CALIBRATION_SHA256" "$CAL_DEST" | sha256sum -c -
fi
"$LC_PY" - "$LC_DIR" "$CFG" "$CAL_DEST" "$PAIR" "$UP_SHA" \
  "$MAPPER_JSON_SHA" "$MAPPER_ST_SHA" <<'PY'
import json, math, sys
from pathlib import Path
from linear_ceiling.config import load_e9_config

root, cfg_path, cal_path = map(Path, sys.argv[1:4])
pair, up_sha, mapper_json_sha, mapper_st_sha = sys.argv[4:]
cfg = load_e9_config(cfg_path, root)
assert cfg.pair == pair, f"config pair {cfg.pair!r} != requested {pair!r}"
assert cfg.upstream_sha == up_sha, f"config upstream pin {cfg.upstream_sha} != requested exact pin {up_sha}"
assert cfg.mapper_k == 1, f"Sitting B requires its registered verdict mapper k=1, got {cfg.mapper_k}"
assert cfg.context_floor == 0, f"short cell must have context_floor=0, got {cfg.context_floor}"
# Entry 0042 REGISTERS the stopping rule for this cell, so the opposite is now required: without
# it a budget kill yields no verdict at all. This assertion was written when the short cell
# forbade a partial close and would refuse the correctly-registered config outright.
assert cfg.allow_partial, "entry 0042 registers allow_partial for this cell; the config does not"
assert cfg.order_by == "n_sender_asc", f"entry 0042 registers n_sender_asc; config has {cfg.order_by!r}"
assert cfg.rope is None and cfg.bridge is None, "native short cell must register neither rope nor bridge"
cal = json.loads(cal_path.read_text(encoding="utf-8"))
assert cal.get("pair") == pair, f"calibration is for {cal.get('pair')!r}, not {pair!r}"
mapper = cal.get("mapper") or {}
assert mapper.get("k") == cfg.mapper_k, "calibration mapper k differs from config"
assert mapper.get("json_sha256") == mapper_json_sha, "calibration names another mapper json"
assert mapper.get("safetensors_sha256") == mapper_st_sha, "calibration names another mapper safetensors"
assert cal.get("upstream_pin_check") == "held", "home calibration did not hold its upstream pin check"
assert all((cal.get("generic_dumps_match_e8_fingerprints") or {}).values()), \
    "calibration did not match both generic dumps to E8"
for ck, rk in (("K", "tau_K"), ("V", "tau_V"), ("agent_K", "tau_agent_K")):
    got, want = float(cal["tau"][ck]), float(cfg.rule[rk])
    assert math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-9), \
        f"calibration {ck}={got} != config {rk}={want}"
print(f"  pair={cfg.pair} cap={cfg.context_cap} floor={cfg.context_floor} "
      f"mapper_k={cfg.mapper_k} allow_partial={cfg.allow_partial}")
PY
say "  calibration sha256 $(sha256sum "$CAL_DEST" | awk '{print $1}')"

step "traces and manifest"
cd "$LC_DIR"
if [ ! -d traces ]; then
  [ -f "$TRACES_TGZ" ] || refuse "$TRACES_TGZ not uploaded"
  tar -xzf "$TRACES_TGZ"
fi
"$LC_PY" -m linear_ceiling.e7_manifest check | tail -1 | tee "$WORK/manifest_check.out" \
  | grep -q '^manifest ok' || refuse "traces do not match the committed manifest"
say "  $(<"$WORK/manifest_check.out")"

step "mapper by sha256"
MD="$UP_DIR/mappers/$PAIR"
mkdir -p "$MD"
if [ ! -f "$MD/k1.json" ]; then
  [ -f "$MAPPER_JSON" ] || refuse "$MAPPER_JSON not uploaded"
  cp -- "$MAPPER_JSON" "$MD/k1.json"
fi
if [ ! -f "$MD/k1.safetensors" ]; then
  [ -f "$MAPPER_ST" ] || refuse "$MAPPER_ST not uploaded"
  cp -- "$MAPPER_ST" "$MD/k1.safetensors"
fi
printf '%s  %s\n' "$MAPPER_JSON_SHA" "$MD/k1.json" | sha256sum -c -
printf '%s  %s\n' "$MAPPER_ST_SHA" "$MD/k1.safetensors" | sha256sum -c -

# Free-space floor on the box. Sitting B writes ~12.4 GB of dumps PER HANDOFF (same_src 4.30 +
# same_tgt 4.30 + cross_src 3.76 at the cap) and the driver deletes each set only after the home side
# has pulled and verified it, so a stalled puller fills a 250 GB disk in about twenty handoffs. This
# refuses BEFORE the weights rather than dying mid-run with a half-written dump.
need_free_gib() {                       # need_free_gib <gib> <why>
  local want="$1" why="$2" have
  # `df -B` is GNU-only and fails on BSD/macOS, so this used to crash the rehearsal. POSIX `df -Pk`
  # works on both; convert 1K blocks to GiB in awk.
  have=$(df -Pk "$WORK" | awk 'NR==2{printf "%d", $4/1048576}')
  say "  free space: ${have} GiB (need ${want} GiB for $why)"
  [ "${have:-0}" -ge "$want" ] || refuse "only ${have} GiB free at $WORK; $why needs ${want} GiB"
}
# REHEARSAL=1 stops at the E9 gate: it downloads no weights and writes no dump, so the 60 GiB floor
# is guarding against bytes it will never write. Refusing on it would mean the rehearsal cannot run on
# a home disk that is legitimately full of the very weight cache waiting to be uploaded -- which is
# exactly when it is most worth running. The floor is reduced to what the rehearsal DOES use (the two
# clones and their venvs) and the log says plainly that the real floor went unchecked.
if [ "$REHEARSAL" = 1 ]; then
  need_free_gib 5 "the rehearsal clones and venvs"
  say "  REHEARSAL: the 60 GiB weights+dumps floor was NOT checked; it is a box-disk property and this"
  say "             run writes neither. On the box it is checked in full."
else
  need_free_gib 60 "the weight cache plus several handoffs of dumps"
fi

step "fresh-pin E9 gate before weights"
cd "$LC_DIR"
"$LC_PY" -m linear_ceiling.e9 --check --config "config/$EXP.toml"
say "  config sha256 $(sha256sum "$CFG" | awk '{print $1}')"

if [ "$REHEARSAL" = "1" ]; then
  say "REHEARSAL COMPLETE: shas, venvs, tau binding, traces, mapper and the E9 gate all agree."
  say "  Nothing downloaded, no GPU touched, no cost. The next step on a real box is the weights."
  say "SITTING_B_OK"
  exit 0
fi

step "weights (pre-staged, or token passed to download processes only)"
export HF_HOME HF_HUB_DISABLE_IMPLICIT_TOKEN=1
mkdir -p "$HF_HOME"

# Validate the archive before extraction: only hub/, no token files, no path escape. HF cache
# snapshots legitimately use relative symlinks back to their model's blobs/ directory.
if [ -f "$WEIGHTS_TGZ" ]; then
  "$LC_PY" - "$WEIGHTS_TGZ" <<'PY'
import pathlib, posixpath, sys, tarfile

p = pathlib.Path(sys.argv[1])
with tarfile.open(p, "r:gz") as tf:
    members = tf.getmembers()
    assert members, "weight archive is empty"
    for m in members:
        name = m.name
        while name.startswith("./"):
            name = name[2:]
        parts = pathlib.PurePosixPath(name).parts
        assert parts and parts[0] == "hub", f"archive member outside hub/: {m.name!r}"
        assert not pathlib.PurePosixPath(name).is_absolute() and ".." not in parts, \
            f"unsafe archive member: {m.name!r}"
        assert pathlib.PurePosixPath(name).name not in {"token", "stored_tokens"} \
            and not name.endswith(".token"), f"token file in weight archive: {m.name!r}"
        if m.issym():
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), m.linkname))
            assert target == "hub" or target.startswith("hub/"), f"escaping symlink: {m.name!r} -> {m.linkname!r}"
        elif m.islnk():
            target = posixpath.normpath(m.linkname.lstrip("./"))
            assert target == "hub" or target.startswith("hub/"), f"escaping hardlink: {m.name!r} -> {m.linkname!r}"
print(f"  archive validated: {len(members)} members, hub/ only, no token files")
PY
  tar --no-same-owner -xzf "$WEIGHTS_TGZ" -C "$HF_HOME"
  if [ "$REMOVE_WEIGHTS_TGZ" = 1 ]; then
    rm -f -- "$WEIGHTS_TGZ"
    say "  extracted and removed the duplicate weight archive"
  else
    say "  extracted weight archive; retained by request"
  fi
fi

read -r SRC_ID TGT_ID < <("$UP_PY" - "$PAIR" <<'PY'
import sys
from kvt.pairs import PAIRS
p = PAIRS[sys.argv[1]]
print(p.source, p.target)
PY
)
say "  source=$SRC_ID target=$TGT_ID"

cache_complete() {
  local mid="$1" d="$HF_HOME/hub/models--${1//\//--}"
  [ -d "$d/snapshots" ] || return 1
  find -L "$d/snapshots" -maxdepth 2 -name config.json -print -quit | grep -q . || return 1
  find -L "$d/snapshots" -maxdepth 2 -name tokenizer.json -print -quit | grep -q . || return 1
  find -L "$d/snapshots" -maxdepth 2 -name '*.safetensors' -print -quit | grep -q . || return 1
}

missing=()
for mid in "$SRC_ID" "$TGT_ID"; do
  if cache_complete "$mid"; then
    say "  staged $mid -> $(du -sh "$HF_HOME/hub/models--${mid//\//--}" | cut -f1)"
  else
    missing+=("$mid")
  fi
done
if [ "${#missing[@]}" -gt 0 ]; then
  [ -n "$HF_DOWNLOAD_TOKEN" ] \
    || refuse "incomplete staged cache for: ${missing[*]}; upload hub-only weights or stream HF_TOKEN"
  for mid in "${missing[@]}"; do
    say "  downloading $mid with a process-only token (the token value is never logged or saved)"
    HF_TOKEN="$HF_DOWNLOAD_TOKEN" "$LC_PY" - "$mid" <<'PY'
import os, sys
from huggingface_hub import snapshot_download

token = os.environ.pop("HF_TOKEN")
p = snapshot_download(sys.argv[1], token=token,
                      allow_patterns=["*.json", "*.safetensors", "tokenizer*"])
print("  ->", p)
PY
  done
fi
HF_DOWNLOAD_TOKEN=""
unset HF_DOWNLOAD_TOKEN

for mid in "$SRC_ID" "$TGT_ID"; do
  cache_complete "$mid" || refuse "cache remains incomplete after staging/download: $mid"
done
token_file_count="$({
  find "$HF_HOME" -maxdepth 4 -type f \( -name token -o -name stored_tokens -o -name '*.token' \) -print
  [ ! -f "$HOME/.cache/huggingface/token" ] || printf '%s\n' "$HOME/.cache/huggingface/token"
  [ ! -f "$HOME/.cache/huggingface/stored_tokens" ] || printf '%s\n' "$HOME/.cache/huggingface/stored_tokens"
} | tee /dev/stderr | awk 'END{print NR}')"
[ "$token_file_count" = 0 ] || refuse "token persistence detected in the Hugging Face cache (listed above)"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
say "  offline mode enabled; token-file count = 0"

step "box alignment and exact home sha verification"
cd "$LC_DIR"
"$LC_PY" -m linear_ceiling.e9 --align-only --config "config/$EXP.toml"
COVERAGE="$LC_DIR/results/$EXP/align/coverage.json"
[ -s "$COVERAGE" ] || refuse "$COVERAGE was not written"
got_coverage_sha="$(sha256sum "$COVERAGE" | awk '{print $1}')"
[ "$got_coverage_sha" = "$COVERAGE_SHA256" ] \
  || refuse "box coverage sha $got_coverage_sha != home $COVERAGE_SHA256"
say "  coverage sha256 $got_coverage_sha (exact home match)"

# This is both the real R2 top rung and a pre-score kill-shot. score_positions cannot score an empty
# pair array, and the first handoff's seeded derangement requires at least two matched positions.
read -r COVERAGE_MAX MAX_PREFILL < <("$LC_PY" - "$COVERAGE" <<'PY'
import json, sys

c = json.load(open(sys.argv[1], encoding="utf-8"))
rows = {r["handoff_id"]: r for r in c["alignments"] if not r["excluded"]}
order = list(c["run_order"])
assert rows, "coverage includes no handoffs"
assert len(order) == len(rows) and set(order) == set(rows), "run_order is not exactly the included set"
empty = sorted(h for h, r in rows.items() if int(r["n_matched"]) < 1)
assert not empty, f"included handoffs with n_matched < 1 cannot be scored: {empty}"
first = rows[order[0]]
assert int(first["n_matched"]) >= 2, \
    f"first run-order handoff {order[0]} has n_matched={first['n_matched']}; null control needs >=2"
coverage_max = max(max(int(r["n_sender"]), int(r["n_receiver"])) for r in rows.values())
# The first-handoff prefix control performs one extra receiver token. It is normally below the cohort
# maximum, but the memory authorization must cover it even if ordering changes in a future short cell.
probe_max = max(coverage_max, int(first["n_sender"]) + 1)
assert coverage_max > 0 and probe_max <= int(c["context_cap"]) + 1
print(coverage_max, probe_max)
PY
)
say "  coverage max = $COVERAGE_MAX = max(max(n_sender,n_receiver)) over included alignments"
say "  R2 top rung = $MAX_PREFILL (also covers first-handoff S+1 prefix control)"
say "  every included n_matched >= 1; first run-order n_matched >= 2"

step "checkpoint classification (plain, validated resume, or already complete)"
REPORT="$LC_DIR/results/$EXP/report.json"
# NOTE for editors: this heredoc sits inside a $( ) command substitution, and bash re-parses quotes
# there even though the delimiter is quoted. A lone apostrophe in a Python comment below -- in a word
# like "launchers" written possessively -- makes the whole script fail to parse with "unexpected EOF".
# Keep apostrophes out of this block; `bash -n` catches it, so run that after editing.
RUN_MODE="$("$LC_PY" - "$REPORT" "$CFG" "$UP_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path
from linear_ceiling.hashing import sha256_text_file

report, cfg_path = map(Path, sys.argv[1:3])
up_sha = sys.argv[3]
if not report.exists():
    # M2. Files without a checkpoint mean the driver died during the FIRST handoff, before it had
    # written anything to resume from. Refusing here (as this did) leaves the sitting stuck on a
    # billing card until someone cleans up by hand, and a plain relaunch over half-written score or
    # tensor files is worse than that. So: move them aside, never delete them, and run plain. The
    # quarantine is timestamped so a second crash cannot overwrite the evidence of the first, and it
    # is listed on stderr so the setup log records exactly what was displaced.
    import shutil, time
    leftovers = [p for name in ("scores", "tokens", "controls", "scratch")
                 if (p := report.parent / name).exists() and any(p.iterdir())]
    if leftovers:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        # Two crashes inside one second collide on a second-resolution stamp, and mkdir then raises --
        # which would make the SECOND crash unrecoverable in the name of preserving the first. Take the
        # next free suffix instead. exist_ok would be wrong here: it would merge the two crashes.
        q = report.parent / f"quarantine.{stamp}"
        n = 2
        while q.exists():
            q = report.parent / f"quarantine.{stamp}.{n}"
            n += 1
        q.mkdir(parents=True)
        for src in leftovers:
            shutil.move(str(src), str(q / src.name))
            print(f"QUARANTINED {src.name} -> {q.name}/ (no checkpoint existed; nothing deleted)",
                  file=sys.stderr)
    print("plain")
    raise SystemExit
r = json.loads(report.read_text(encoding="utf-8"))
assert not r.get("partial"), (
    "this checkpoint is an already-CLOSED partial; a closed run is not resumable, and the close is "
    "home-side by design (pull_verify_b --final-partial, then e9 --close-partial)")
assert r.get("config_sha256") == sha256_text_file(cfg_path), "checkpoint was written under another config"
assert r.get("upstream_sha") == up_sha, "checkpoint was written under another upstream pin"
if r.get("complete") is True:
    print("complete")
    raise SystemExit

# _resumable validates each score + per-token pair. It deliberately trusts the controls block, so
# validate that block here before allowing --resume. If controls is None, the driver reruns the first
# handoff and all controls; a partially present/malformed block is a refusal, never trusted.
controls = r.get("controls")
if controls is not None:
    assert set(("identity", "prefix", "null")) <= set(controls), "checkpoint controls block is incomplete"
    order = r.get("run_order") or []
    assert order and controls.get("handoff_id") == order[0], "controls are not attached to the first handoff"
    cdir = report.parent / "controls"
    def digest(path):
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    for name in ("identity", "prefix", "null"):
        rec = controls[name]
        for file_key, sha_key in (("score_file", "score_sha256"),
                                  ("tokens_file", "tokens_sha256"),
                                  ("pairs_file", "pairs_sha256")):
            p = cdir / rec[file_key]
            assert p.is_file(), f"resume control {name} is missing {p}"
            assert digest(p) == rec[sha_key], f"resume control {name} hash mismatch: {p.name}"
print("resume")
PY
)"
say "  run mode: $RUN_MODE"

if [ "$RUN_MODE" != complete ]; then
  step "CUDA smoke test (before the measured forward)"
  "$UP_PY" - <<'PY'
import torch
print(f"  torch {torch.__version__} cuda_available={torch.cuda.is_available()}")
assert torch.cuda.is_available(), "torch.cuda.is_available() is False"
torch.zeros(1, device="cuda")
free, total = torch.cuda.mem_get_info()
print(f"  device={torch.cuda.get_device_name(0)} free={free/2**30:.2f} GiB total={total/2**30:.2f} GiB")
PY

  step "R2 probe at the run's real longest prefill (both models)"
  : > "$PROBE_LOG"
  LC_DIR="$LC_DIR" UP_DIR="$UP_DIR" EXP="$EXP" PAIR="$PAIR" MAX_PREFILL="$MAX_PREFILL" \
    COVERAGE_MAX="$COVERAGE_MAX" MIN_GPU_MARGIN_GIB="$MIN_GPU_MARGIN_GIB" "$UP_PY" - <<'PY' | tee -a "$PROBE_LOG"
import gc, json, os, sys, time, tomllib
from pathlib import Path

import torch

up = Path(os.environ["UP_DIR"])
lc = Path(os.environ["LC_DIR"])
sys.path.insert(0, str(up))
from kvt.models import ATTN_IMPLEMENTATION, load_model  # noqa: E402
from kvt.pairs import PAIRS  # noqa: E402

exp, requested_pair = os.environ["EXP"], os.environ["PAIR"]
cfg = tomllib.loads((lc / "config" / f"{exp}.toml").read_text(encoding="utf-8"))["e9"]
assert cfg["pair"] == requested_pair
pair = PAIRS[requested_pair]
rope = dict(cfg.get("rope") or {}) or None
top = int(os.environ["MAX_PREFILL"])
coverage_max = int(os.environ["COVERAGE_MAX"])
margin = float(os.environ["MIN_GPU_MARGIN_GIB"])
free0, total = torch.cuda.mem_get_info()
print(json.dumps({"event": "probe_start", "card": torch.cuda.get_device_name(0),
                  "total_GiB": round(total / 2**30, 3), "free_GiB": round(free0 / 2**30, 3),
                  "torch": torch.__version__, "pair": pair.name, "rope": rope,
                  "coverage_max_max_sender_receiver": coverage_max, "T": top,
                  "top_rung_from": "coverage maximum, raised only if first-handoff S+1 control is longer",
                  "required_margin_GiB": margin}), flush=True)
failed = False
for which in ("target", "source"):
    mid = getattr(pair, which)
    free_before, _ = torch.cuda.mem_get_info()
    row = {"model": mid, "role": which, "T": top,
           "free_before_GiB": round(free_before / 2**30, 3)}
    m = ids = out = None
    try:
        m = load_model(mid, rope_scaling=rope)
        attn = getattr(m.config, "_attn_implementation", None)
        if attn != ATTN_IMPLEMENTATION:
            raise RuntimeError(f"attention backend {attn!r} != required {ATTN_IMPLEMENTATION!r}")
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        vocab = int(m.config.vocab_size)
        ids = torch.randint(0, min(vocab, 20000), (1, top), device="cuda")
        t0 = time.time()
        with torch.no_grad():
            out = m(input_ids=ids, use_cache=True, logits_to_keep=1)
        torch.cuda.synchronize()
        peak = torch.cuda.max_memory_allocated() / 2**30
        reserved = torch.cuda.max_memory_reserved() / 2**30
        headroom = free_before / 2**30 - reserved
        margin_ok = headroom >= margin
        row.update(attn=attn, dtype=str(next(m.parameters()).dtype),
                   peak_GiB=round(peak, 3), peak_reserved_GiB=round(reserved, 3),
                   headroom_GiB=round(headroom, 3), required_margin_GiB=margin,
                   margin_ok=margin_ok, seconds=round(time.time() - t0, 2), ok=margin_ok)
        if not margin_ok:
            row["refusal"] = "measured peak reserved memory leaves less than the required real margin"
            failed = True
    except torch.cuda.OutOfMemoryError as e:
        row.update(ok=False, margin_ok=False, oom=str(e).split(".")[0][:200],
                   peak_GiB=round(torch.cuda.max_memory_allocated() / 2**30, 3),
                   peak_reserved_GiB=round(torch.cuda.max_memory_reserved() / 2**30, 3))
        failed = True
    except Exception as e:
        row.update(ok=False, error=f"{type(e).__name__}: {e}")
        failed = True
    finally:
        del out, ids, m
        gc.collect()
        torch.cuda.empty_cache()
    print(json.dumps(row), flush=True)
print("PROBE_SITTING_B_FAILED" if failed else "PROBE_SITTING_B_OK", flush=True)
raise SystemExit(2 if failed else 0)
PY
else
  step "R2 probe"
  [ -s "$PROBE_LOG" ] || refuse "complete report has no retained $PROBE_LOG; cannot finalize the required evidence set"
  grep -q '^PROBE_SITTING_B_OK$' "$PROBE_LOG" \
    || refuse "complete report's probe log has no terminal PROBE_SITTING_B_OK"
  say "  report is already complete; preserved successful probe accepted, driver will be skipped"
fi

step "immutable evidence capture"
mkdir -p "$EVIDENCE_DIR"
cp -- "$0" "$EVIDENCE_DIR/sitting_b.sh"
cp -- "$LC_DIR/tools/ec2/setup.sh" "$EVIDENCE_DIR/ec2_setup.reference.sh"
cp -- "$LC_DIR/tools/ec2/run.sh" "$EVIDENCE_DIR/ec2_run.reference.sh"
cp -- "$LC_DIR/tools/ec2/probe_e9l.py" "$EVIDENCE_DIR/probe_e9l.reference.py"
cp -- "$WORK/manifest_check.out" "$EVIDENCE_DIR/manifest_check.out"
{
  printf 'captured_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'launcher_sha256=%s\n' "$(sha256sum "$0" | awk '{print $1}')"
  printf 'linear_ceiling_sha=%s\n' "$(git -C "$LC_DIR" rev-parse HEAD)"
  printf 'upstream_sha=%s\n' "$(git -C "$UP_DIR" rev-parse HEAD)"
  printf 'pair=%s\nexp=%s\ncoverage_sha256=%s\ncoverage_max=%s\nprobe_max=%s\n' \
    "$PAIR" "$EXP" "$got_coverage_sha" "$COVERAGE_MAX" "$MAX_PREFILL"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
  "$UP_PY" -c "import sys,torch,transformers,numpy;print('up_python',sys.version.split()[0]);print('torch',torch.__version__,'cuda',torch.version.cuda);print('transformers',transformers.__version__,'numpy',numpy.__version__)"
  "$LC_PY" -c "import sys,torch,numpy;print('lc_python',sys.version.split()[0]);print('torch',torch.__version__,'numpy',numpy.__version__)"
} > "$EVIDENCE_DIR/versions.txt"

step "detached E9 launch/finalization"
command -v setsid >/dev/null 2>&1 || refuse "setsid is unavailable"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
for spec in "$RUN_LOG|log" "$RC_FILE|rc" "$STATUS_FILE|status"; do
  IFS='|' read -r old ext <<< "$spec"
  [ ! -e "$old" ] || mv -- "$old" "$WORK/$EXP.$timestamp.halt.$ext"
done
rm -f -- "$READY_FILE" "$FINAL_MANIFEST"

# The child waits on READY_FILE so setup.log and launches.log have reached their final bytes before
# it can eventually hash them. On success, its last write to stdout is SITTING_B_OK; manifest
# generation is silent, atomic, and therefore hashes a closed log.
setsid nohup bash -c '
set -uo pipefail
work=$1; exp=$2; mode=$3; lc_py=$4; ready=$5
status="$work/$exp.status"; rc_file="$work/$exp.rc"; manifest="$work/$exp.final.sha256"
for _ in $(seq 1 600); do [ -f "$ready" ] && break; sleep 0.1; done
if [ ! -f "$ready" ]; then
  printf "EXIT=97\n" > "$rc_file"
  printf "SITTING_B_FAILED rc=97 ready-barrier-timeout\n" > "$status"
  echo "[$(date -u +%FT%TZ)] SITTING_B_FAILED rc=97 ready-barrier-timeout"
  exit 97
fi
rm -f -- "$ready"
printf "RUNNING mode=%s started=%s\n" "$mode" "$(date -u +%FT%TZ)" > "$status"
cd "$work/linear-ceiling" || exit 98
rc=0
if [ "$mode" = plain ]; then
  "$lc_py" -u -m linear_ceiling.e9 --config "config/$exp.toml" || rc=$?
elif [ "$mode" = resume ]; then
  "$lc_py" -u -m linear_ceiling.e9 --config "config/$exp.toml" --resume || rc=$?
elif [ "$mode" = complete ]; then
  echo "[$(date -u +%FT%TZ)] report already complete; E9 driver skipped"
else
  echo "unknown run mode: $mode" >&2; rc=96
fi
if [ "$rc" -eq 0 ]; then
  "$lc_py" - "$work/linear-ceiling/results/$exp/report.json" <<"PY" || rc=95
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
assert r.get("complete") is True, "driver returned zero without complete:true"
# A COMPLETE report cannot also be partial -- that is a contradiction, not a policy. Entry 0042
# registers partial closes for this cell, but they are stamped AT HOME on the verified mirror and
# never through this block, which only validates a driver rc == 0 / complete: true.
assert not r.get("partial"), "a report claiming complete:true also carries a partial close"
assert list(r.get("scores", {})) == list(r.get("run_order", [])), \
    "complete report scores are not exactly the registered order"
assert r.get("bridge") is None, "native short cell unexpectedly recorded a bridge"
PY
fi
if [ "$rc" -ne 0 ]; then
  rm -f -- "$manifest"
  printf "EXIT=%s\n" "$rc" > "$rc_file"
  printf "SITTING_B_FAILED rc=%s\n" "$rc" > "$status"
  echo "[$(date -u +%FT%TZ)] SITTING_B_FAILED rc=$rc"
  exit "$rc"
fi

# Write terminal bytes before hashing them. Nothing writes stdout/stderr after a successful mv.
printf "EXIT=0\n" > "$rc_file"
printf "SITTING_B_OK\n" > "$status"
echo "[$(date -u +%FT%TZ)] SITTING_B_OK"
tmp="$manifest.tmp.$$"; err="$manifest.err.$$"
if (
  cd "$work"
  {
    find "linear-ceiling/results/$exp" -type f ! -path "*"/scratch/"*" -print0
    find "sitting_b.evidence" -type f -print0
    printf "%s\0" "manifest_check.out" "sitting_b.setup.log" "sitting_b.probe.log" "$exp.log" \
      "$exp.rc" "$exp.status" "sitting_b.launches.log"
    find . -maxdepth 1 -type f \( -name "$exp.*.halt.log" -o -name "$exp.*.halt.rc" \
      -o -name "$exp.*.halt.status" \) -printf "%f\0"
  } | sort -zu | xargs -0 -r sha256sum
) > "$tmp" 2> "$err"; then
  rm -f -- "$err"
  mv -f -- "$tmp" "$manifest"
  exit 0
fi
rc=94
rm -f -- "$tmp" "$err" "$manifest"
printf "EXIT=%s\n" "$rc" > "$rc_file"
printf "SITTING_B_FAILED rc=%s final-manifest\n" "$rc" > "$status"
echo "[$(date -u +%FT%TZ)] SITTING_B_FAILED rc=$rc final-manifest"
exit "$rc"
' _ "$WORK" "$EXP" "$RUN_MODE" "$LC_PY" "$READY_FILE" \
  > "$RUN_LOG" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" > "$PID_FILE"
printf '[%s] pid=%s mode=%s lc=%s up=%s\n' "$(date -u +%FT%TZ)" "$pid" "$RUN_MODE" "$LC_SHA" "$UP_SHA" \
  >> "$LAUNCH_LOG"
say "SITTING_B_LAUNCHED pid=$pid mode=$RUN_MODE log=$RUN_LOG status=$STATUS_FILE"
say "  resume is automatic; a budget stop closes at HOME (--final-partial, then e9 --close-partial)"
say "  this script will never terminate the pod; home pull+verify owns termination"
atomic_line "$SETUP_STATUS" "SITTING_B_LAUNCHED pid=$pid mode=$RUN_MODE"
: > "$READY_FILE"
trap - EXIT
exit 0
