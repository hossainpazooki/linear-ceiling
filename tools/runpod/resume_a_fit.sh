#!/usr/bin/env bash
# RESUME sitting A from the fit step, after SITTING_A_FAILED fit k=1/4/8 at 2026-09-18T17:50:51Z.
#
# WHAT FAILED: sitting_a.sh called `fit_mapper.py --k 1 4 8 --lam 0.01 --holdout-frac 0.2 --space
# content` with no `--pair`, and argparse rejected it in 3 seconds. Same class as the probe fix in
# cd91a47, missed for the fit. Nothing scientific went wrong and nothing is lost.
#
# WHY NOT RERUN sitting_a.sh FROM THE TOP: it would regenerate both generic dumps, so the probe
# (already computed, 95 minutes) would describe DIFFERENT BYTES than the fit that followed it, and
# the 95 minutes would be spent again against a hard 19:45:22Z wall. This resumes from the fit and
# REUSES the existing dumps and probe outputs -- which is only legitimate if they are still the bytes
# the probe was computed from, so the first thing this script does is assert they exist and record
# their sha256 into the log. The resumed run is thereby tied to the bytes it actually used.
#
# THREADING: the cgroup quota is 7.65 CPUs but the previous process ran 111 threads and racked up
# ~50k throttle events, which is most of the observed 3.7x slowdown. The BLAS/OMP thread counts are
# capped at 8 here. This changes NO registered parameter -- not the rule, tau, band, cap, seeds, k,
# lambda or holdout -- only how many threads a reduction uses. It can move float32 results at the
# last-ULP level, which is exactly the class entry 0028 registered a cross-platform tolerance for,
# and which is already unavoidable between this box and the home re-score. Stated here so the sitting
# record can carry it rather than discover it.
set -euo pipefail

PAIR="${PAIR:-llama3.2-3b-to-llama3.1-8b}"
EXP="${EXP:-e8f}"
WORK="${WORK:-/workspace}"
UP="$WORK/kv-transfer-replication"
LC="$WORK/linear-ceiling"
UP_PY="$UP/.venv/bin/python"
LC_PY="$LC/.venv/bin/python"
LOG="${LOG:-$WORK/sitting_a.log}"

STEP="resume-init"
exec > >(tee -a "$LOG") 2>&1
say() { echo "[$(date -u +%FT%TZ)] $*"; }
step() { STEP="$1"; say "== $1"; }
fail() { say "SITTING_A_FAILED $STEP"; }
trap fail ERR

say "RESUME after SITTING_A_FAILED fit k=1/4/8 at 17:50:51Z: missing --pair; dumps and probe REUSED, not regenerated"
say "  BLAS/OMP threads capped at 8 (cgroup quota 7.65 CPUs); no registered parameter changes"

# Same offline environment the original run established after its weight step.
export HF_HOME="$WORK/hf"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
export VECLIB_MAXIMUM_THREADS=8

# ---------------------------------------------------------------- assert the inputs, do not assume
step "verify the reused inputs"
cd "$UP"
for w in source target; do
  d="data/kv/$PAIR/$w"
  [ -f "$d/meta.json" ] || { say "REFUSED: $d/meta.json missing; the dumps are not intact"; exit 1; }
  say "  $w meta.json sha256 $(sha256sum "$d/meta.json" | cut -c1-16)  files=$(find "$d" -type f | wc -l)"
done
PROBE="results/probe/$PAIR"
for f in r2_K_rope_train.npy r2_K_rope_heldout.npy r2_K_stripped_train.npy r2_K_stripped_heldout.npy \
         r2_V_train.npy r2_V_heldout.npy summary.json; do
  [ -f "$PROBE/$f" ] || { say "REFUSED: $PROBE/$f missing; fit_mapper reads the probe's r2 files"; exit 1; }
  say "  probe $f sha256 $(sha256sum "$PROBE/$f" | cut -c1-16)"
done

# ---------------------------------------------------------------- the fit, WITH --pair
step "fit k=1/4/8"
"$UP_PY" scripts/fit_mapper.py --pair "$PAIR" --k 1 4 8 --lam 0.01 --holdout-frac 0.2 --space content

# ---------------------------------------------------------------- E8 driver, unchanged
step "E8 driver, arms (a) and (b)"
cd "$LC"
"$LC_PY" -m linear_ceiling.e8 --config "config/$EXP.toml"
[ -f "results/$EXP/report.json" ] || { say "REFUSED: no results/$EXP/report.json"; exit 1; }

# ---------------------------------------------------------------- package
step "package the pull set"
OUT="$WORK/pull"; rm -rf "$OUT"; mkdir -p "$OUT"
need() { [ -e "$1" ] || { say "REFUSED: required artifact missing on the box: $1"; exit 1; }
         mkdir -p "$OUT/$2"; cp -r "$1" "$OUT/$2/"; }
want() { [ -e "$1" ] && { mkdir -p "$OUT/$2"; cp -r "$1" "$OUT/$2/"; } || say "  absent (recorded): $1"; }
need "results/$EXP/report.json"          "lc/results/$EXP"
need "results/$EXP/kv/agent"             "lc/results/$EXP/kv"
need "data/$EXP"                         "lc/data"
need "$UP/data/kv/$PAIR"                 "up/data/kv"
need "$UP/data/tokens/${PAIR}_n50_len1024_seed0.npy" "up/data/tokens"
need "$UP/mappers/$PAIR"                 "up/mappers"
need "$UP/results/mapper/$PAIR"          "up/results/mapper"
need "$LOG"                              "logs"
want "$WORK/sitting_a.attempt7.log"      "logs"      # the pre-resume log, per the rotate rule
want "$WORK/manifest_check.out"          "logs"
want "$UP/results/probe/$PAIR"           "up/results/probe"

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
