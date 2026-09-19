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
# There is intentionally no partial-close path: the loaded config must have allow_partial=false.
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
( cd "$UP_DIR"
  [ -x .venv/bin/python ] || uv venv --python 3.12 .venv >/dev/null
  uv pip install --quiet --python .venv/bin/python \
    --index-url https://download.pytorch.org/whl/cu128 'torch==2.11.0'
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
assert not cfg.allow_partial, "short verdict cell must not register allow_partial"
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

step "fresh-pin E9 gate before weights"
cd "$LC_DIR"
"$LC_PY" -m linear_ceiling.e9 --check --config "config/$EXP.toml"
say "  config sha256 $(sha256sum "$CFG" | awk '{print $1}')"

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
RUN_MODE="$("$LC_PY" - "$REPORT" "$CFG" "$UP_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path
from linear_ceiling.hashing import sha256_text_file

report, cfg_path = map(Path, sys.argv[1:3])
up_sha = sys.argv[3]
if not report.exists():
    leftovers = [p for name in ("scores", "tokens", "controls", "scratch")
                 if (p := report.parent / name).exists() and any(p.iterdir())]
    assert not leftovers, f"result files exist without a checkpoint report: {leftovers}"
    print("plain")
    raise SystemExit
r = json.loads(report.read_text(encoding="utf-8"))
assert not r.get("partial"), "short-cell report carries a partial close; this config forbids it"
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
assert not r.get("partial"), "short cell must not carry a partial close"
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
say "  resume is automatic; never use --close-partial for this short verdict cell"
say "  this script will never terminate the pod; home pull+verify owns termination"
atomic_line "$SETUP_STATUS" "SITTING_B_LAUNCHED pid=$pid mode=$RUN_MODE"
: > "$READY_FILE"
trap - EXIT
exit 0
