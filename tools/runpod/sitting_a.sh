#!/usr/bin/env bash
# Sitting A, end to end, non-interactive: E8 calibration and the k = 1/4/8 mapper fit for a pair.
#
# ONE script because the meter runs the whole time. No hand-driven ssh step, no decision to make
# while billing, one log the home side can tail, and a last line that is either SITTING_A_OK or
# SITTING_A_FAILED <step>. Every step is timestamped.
#
# ORDER IS A COST DECISION, NOT A STYLE ONE. The cheap gates run BEFORE the ~22 GB weight pull: a
# refused gate then costs ~3 minutes of card time instead of ~20. Nothing that can fail on
# committed bytes is allowed to wait behind a download.
#
#   clone both repos at exact shas -> venvs -> GATES (e8 --check, e7_manifest check)
#   -> weights -> dumps -> probe -> fit k=1/4/8 -> E8 driver (arms a and b)
#   -> package the pull set with a sha256 manifest written ON the box
#
# It deliberately DOES NOT terminate the pod. Container disk is ephemeral, so the only safe end is:
# home pulls -> home verifies every sha256 against MANIFEST.sha256 -> home terminates. A script that
# helpfully removed the pod when the fit finished would destroy the artifacts it exists to produce.
#
# THE HF TOKEN never reaches this script's environment except for the single download process, is
# never written to disk, never echoed, and never appears in the log: it arrives as HF_TOKEN on the
# one `hf download` invocation and the step ends by PROVING no token file exists under HF_HOME.
#
# REHEARSAL=1 runs everything that needs no GPU and no weights -- clone, gates, manifest check -- and
# stops. That is the $0 fresh-clone rehearsal that proves the pushed shas, the branch, the traces
# tarball and this script agree before any money is involved.
#
# Required env: PAIR UP_REPO UP_SHA LC_REPO LC_SHA
# Optional:     EXP (default e8f) WORK (default /workspace) REHEARSAL TOKENS_NPY TRACES_TGZ
set -euo pipefail

PAIR="${PAIR:?PAIR is required}"
UP_REPO="${UP_REPO:?UP_REPO is required (the fork carrying commit P)}"
UP_SHA="${UP_SHA:?UP_SHA is required (commit P, 40 hex)}"
LC_REPO="${LC_REPO:?LC_REPO is required}"
LC_SHA="${LC_SHA:?LC_SHA is required (the linear-ceiling branch commit)}"
EXP="${EXP:-e8f}"
WORK="${WORK:-/workspace}"
REHEARSAL="${REHEARSAL:-0}"
TRACES_TGZ="${TRACES_TGZ:-$WORK/traces.tar.gz}"
TOKENS_NPY="${TOKENS_NPY:-$WORK/tokens.npy}"     # made at home (CPU-only, seed 0); see step 6
LOG="${LOG:-$WORK/sitting_a.log}"

STEP="init"
mkdir -p "$WORK"
exec > >(tee -a "$LOG") 2>&1
say() { echo "[$(date -u +%FT%TZ)] $*"; }
step() { STEP="$1"; say "== $1"; }
fail() { say "SITTING_A_FAILED $STEP"; }
trap fail ERR

step "host facts"
# Recorded before anything else so the sitting log can answer "what did this run on?" without the
# API (R7 step 6's read-back discipline, and the runbook's box row).
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>&1 | sed 's/^/  gpu: /' || say "  nvidia-smi unavailable"
say "  vcpu: $(nproc 2>/dev/null || echo '?')"
for f in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory/memory.limit_in_bytes; do
  [ -r "$f" ] && say "  cgroup mem ($f): $(cat "$f")" && break
done
say "  disk: $(df -h "$WORK" | awk 'NR==2{print $4" free of "$2}')"

say "sitting A  pair=$PAIR exp=$EXP rehearsal=$REHEARSAL"
say "up=$UP_REPO@${UP_SHA:0:12}  lc=$LC_REPO@${LC_SHA:0:12}"

# ---------------------------------------------------------------- 1. exact shas
step "clone at exact shas"
cd "$WORK"
for spec in "kv-transfer-replication|$UP_REPO|$UP_SHA" "linear-ceiling|$LC_REPO|$LC_SHA"; do
  IFS='|' read -r dir repo sha <<< "$spec"
  if [ ! -d "$dir" ]; then
    git clone --quiet "$repo" "$dir"
  fi
  git -C "$dir" fetch --quiet origin "$sha" 2>/dev/null || git -C "$dir" fetch --quiet --all
  git -C "$dir" checkout --quiet --detach "$sha"
  # A sha that resolves is not the same as a sha that is what we asked for; prove it.
  got="$(git -C "$dir" rev-parse HEAD)"
  [ "$got" = "$sha" ] || { say "REFUSED: $dir is at $got, not $sha"; exit 1; }
  [ -z "$(git -C "$dir" status --porcelain)" ] || { say "REFUSED: $dir is dirty on arrival"; exit 1; }
  say "  $dir at $got (clean)"
done
# The upstream pin must descend from the RoPE-spec commit or every dump of this pair is stripped with
# a plain theta and is silently wrong. This is the cheapest possible place to find that out.
ROPE_SPEC=063f4023fdde67dedbee01a92518ce7f83f6cf5d
git -C kv-transfer-replication merge-base --is-ancestor "$ROPE_SPEC" HEAD \
  || { say "REFUSED: P does not descend from the RoPE-spec commit ${ROPE_SPEC:0:12}"; exit 1; }
say "  upstream descends from the RoPE spec"

# ---------------------------------------------------------------- 2. venvs
step "venvs"
if [ "$REHEARSAL" = "1" ]; then
  say "  rehearsal: using the ambient interpreter for linear-ceiling only"
  LC_PY="${LC_PY:-python3}"
  # This install is part of the rehearsal's proof. Suppressing its failure would let the script
  # continue and misreport an uninstalled package as a trace-manifest refusal.
  ( cd linear-ceiling && "$LC_PY" -m pip install --quiet -e ".[dev]" )
else
  command -v uv >/dev/null 2>&1 || pip install --quiet uv
  ( cd linear-ceiling && { [ -x .venv/bin/python ] || uv venv --python 3.12 .venv >/dev/null; } \
      && uv pip install --quiet -e ".[dev]" >/dev/null \
      && uv pip install --quiet --python .venv/bin/python \
           --index-url https://download.pytorch.org/whl/cu128 "torch==2.11.0" >/dev/null \
      && uv pip install --quiet --python .venv/bin/python "numpy==2.5.2" >/dev/null )
  ( cd kv-transfer-replication && { [ -x .venv/bin/python ] || uv venv --python 3.12 .venv >/dev/null; } \
      && uv pip install --quiet -e . >/dev/null \
      && uv pip install --quiet --python .venv/bin/python \
           --index-url https://download.pytorch.org/whl/cu128 "torch==2.11.0" >/dev/null \
      && uv pip install --quiet --python .venv/bin/python \
           "transformers==5.15.1" "numpy==2.5.2" >/dev/null )
  LC_PY="$WORK/linear-ceiling/.venv/bin/python"
  UP_PY="$WORK/kv-transfer-replication/.venv/bin/python"
fi
say "  linear-ceiling python: $LC_PY"

# The CUDA smoke test belongs HERE: after the venv, before the ~22 GB weight pull. A driver mismatch
# against the pinned torch 2.11.0+cu128 is otherwise found at the first dump, ~25 billed minutes in
# instead of ~8. allowedCudaVersions on the create call should prevent it; this proves it worked.
if [ "$REHEARSAL" != "1" ]; then
  step "CUDA smoke test (before any download)"
  "$UP_PY" -c "
import torch
print(f'  torch {torch.__version__}  cuda_available={torch.cuda.is_available()}')
assert torch.cuda.is_available(), 'torch.cuda.is_available() is False'
torch.zeros(1).cuda()
print(f'  device: {torch.cuda.get_device_name(0)}')
free, total = torch.cuda.mem_get_info()
print(f'  gpu memory: {free/2**30:.2f} GiB free of {total/2**30:.2f} GiB')
" || { say "REFUSED: torch cannot reach the GPU on this host"; exit 1; }
fi

# ---------------------------------------------------------------- 3. traces
step "traces"
cd "$WORK/linear-ceiling"
if [ ! -d traces ]; then
  [ -f "$TRACES_TGZ" ] || { say "REFUSED: $TRACES_TGZ not uploaded"; exit 1; }
  tar -xzf "$TRACES_TGZ"
fi
"$LC_PY" -m linear_ceiling.e7_manifest check | tail -1 | tee "$WORK/manifest_check.out" \
  | grep -q "^manifest ok" || { say "REFUSED: traces do not match the committed manifest"; exit 1; }
say "  $(cat "$WORK/manifest_check.out")"

# ---------------------------------------------------------------- 4. the gates, BEFORE the weights
step "gates (before any download)"
# upstream_path is `../kv-transfer-replication`, which resolves correctly from $WORK/linear-ceiling.
"$LC_PY" -m linear_ceiling.e8 --check --config "config/$EXP.toml"
say "  e8 gate: ready"

if [ "$REHEARSAL" = "1" ]; then
  say "REHEARSAL COMPLETE: shas, tarball, manifest and gates all agree. No weights, no GPU, no cost."
  say "SITTING_A_OK"
  exit 0
fi

# ---------------------------------------------------------------- 5. weights
step "weights (token lives for this step only)"
export HF_HOME="$WORK/hf"
mkdir -p "$HF_HOME"
SRC_ID="$("$LC_PY" -c "from linear_ceiling.pairs import pair_models;print(pair_models('$PAIR')[0])")"
TGT_ID="$("$LC_PY" -c "from linear_ceiling.pairs import pair_models;print(pair_models('$PAIR')[1])")"
if [ -n "${HF_TOKEN:-}" ]; then
  for mid in "$SRC_ID" "$TGT_ID"; do
    say "  downloading $mid"
    # The token is passed to THIS process only, never written, never echoed. `hf` inherits it from
    # the environment of this single invocation; nothing after this block sees it.
    HF_TOKEN="$HF_TOKEN" "$LC_PY" - "$mid" <<'PY'
import sys
from huggingface_hub import snapshot_download
p = snapshot_download(sys.argv[1], allow_patterns=["*.json", "*.safetensors", "tokenizer*"])
print("  ->", p)
PY
  done
  unset HF_TOKEN
else
  say "  no HF_TOKEN in env; assuming a pre-staged cache under $HF_HOME"
fi
# R7's assertion, made true and then PROVEN rather than asserted.
if find "$HF_HOME" -name "token" -o -name "*.token" 2>/dev/null | grep -q .; then
  say "REFUSED: a token file exists under $HF_HOME after the download"; exit 1
fi
say "  no token file under HF_HOME (proven)"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
say "  offline mode on for every later step"

# ---------------------------------------------------------------- 6. tokens
step "generic token draw"
cd "$WORK/kv-transfer-replication"
TOK_REL="data/tokens/${PAIR}_n50_len1024_seed0.npy"
if [ -f "$TOKENS_NPY" ]; then
  # Made at home: CPU-only, tokenizer-only, deterministic at seed 0. Doing it at home removes the
  # FineWeb-Edu network dependency from a box that is mandated HF_HUB_OFFLINE=1, and saves the
  # billed minutes of a streaming download.
  mkdir -p data/tokens && cp "$TOKENS_NPY" "$TOK_REL"
  say "  using the home-made draw $(sha256sum "$TOK_REL" | cut -c1-12)"
else
  say "  no home-made draw uploaded; streaming FineWeb-Edu (needs network: temporarily unsetting offline)"
  ( unset HF_HUB_OFFLINE TRANSFORMERS_OFFLINE
    "$UP_PY" scripts/prepare_tokens.py --pair "$PAIR" --n-seqs 50 --seq-len 1024 --seed 0 )
fi

# ---------------------------------------------------------------- 7. dumps
step "generic dumps (GPU)"
"$UP_PY" scripts/dump_kv.py --pair "$PAIR" --which source --stride 4
"$UP_PY" scripts/dump_kv.py --pair "$PAIR" --which target --stride 4
for w in source target; do
  m="data/kv/$PAIR/$w/meta.json"
  [ -f "$m" ] || { say "REFUSED: $m missing"; exit 1; }
  "$LC_PY" - "$m" "$w" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
r = m.get("rope")
assert r, f"{sys.argv[2]} dump carries no rope block: the pin predates the RoPE spec"
assert r.get("rope_type") == "llama3", f"{sys.argv[2]} rope_type is {r.get('rope_type')!r}, expected llama3"
ck = r.get("check_max_abs")
assert ck is not None and float(ck) < 1e-5, f"{sys.argv[2]} rope check_max_abs {ck} is not under 1e-5"
print(f"  {sys.argv[2]}: rope llama3, check_max_abs {ck}")
PY
done

# ---------------------------------------------------------------- 8. probe + fit
step "probe (CPU, ~15-25 min)"
"$UP_PY" scripts/probe.py
step "fit k=1/4/8"
"$UP_PY" scripts/fit_mapper.py --k 1 4 8 --lam 0.01 --holdout-frac 0.2 --space content

# ---------------------------------------------------------------- 9. E8 driver
step "E8 driver, arms (a) and (b)"
cd "$WORK/linear-ceiling"
"$LC_PY" -m linear_ceiling.e8 --config "config/$EXP.toml"
[ -f "results/$EXP/report.json" ] || { say "REFUSED: no results/$EXP/report.json"; exit 1; }

# ---------------------------------------------------------------- 10. package
step "package the pull set"
OUT="$WORK/pull"; rm -rf "$OUT"; mkdir -p "$OUT"
U="$WORK/kv-transfer-replication"
# `need` REFUSES on a missing source; `want` only records one. The distinction matters because the
# home verifier checks (a) an expected-path list and (b) every entry in MANIFEST.sha256 -- and the
# manifest is generated FROM what was copied. So a required artifact that never got copied would be
# absent from the manifest and would pass both checks silently. The only place that can be caught is
# here, on the box, while the card is still up and it can be re-made.
need() { [ -e "$1" ] || { say "REFUSED: required artifact missing on the box: $1"; exit 1; }
         mkdir -p "$OUT/$2"; cp -r "$1" "$OUT/$2/"; }
want() { [ -e "$1" ] && { mkdir -p "$OUT/$2"; cp -r "$1" "$OUT/$2/"; } || say "  absent (recorded): $1"; }
need "results/$EXP/report.json"          "lc/results/$EXP"
need "results/$EXP/kv/agent"             "lc/results/$EXP/kv"        # summarize_e8 re-fingerprints these
need "data/$EXP"                         "lc/data"                   # the agent token file + manifest
need "$U/data/kv/$PAIR"                  "up/data/kv"                # the generic dumps
need "$U/data/tokens/${PAIR}_n50_len1024_seed0.npy" "up/data/tokens"
need "$U/mappers/$PAIR"                  "up/mappers"                # k1/k4/k8 json+safetensors
need "$U/results/mapper/$PAIR"           "up/results/mapper"         # r2.json, the archived held-out R^2
need "$LOG"                              "logs"
want "$WORK/manifest_check.out"          "logs"
want "$U/results/probe"                  "up/results"                # probe outputs, if the fit wrote any

# The mapper is THE product of this sitting and the one thing another card would have to be rented to
# remake. Its file list is checked by name here, not left to "the directory exists".
for k in 1 4 8; do
  for ext in json safetensors; do
    f="$OUT/up/mappers/$PAIR/k${k}.${ext}"
    [ -s "$f" ] || { say "REFUSED: mapper artifact k${k}.${ext} missing or empty after packaging"; exit 1; }
  done
done
say "  mapper k1/k4/k8 json+safetensors all present and non-empty"

( cd "$OUT" && find . -type f -exec sha256sum {} \; | sort -k2 > MANIFEST.sha256 )
say "  $(wc -l < "$OUT/MANIFEST.sha256") files, $(du -sh "$OUT" | cut -f1)"
say "  pull set at $OUT ; verify MANIFEST.sha256 at home BEFORE terminating"

say "SITTING_A_OK"
