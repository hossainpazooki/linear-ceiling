#!/bin/bash
# Home side of a JupyterHub (Algoverse) sitting, one command: refuse unless the home prerequisites hold, look at the
# slice, upload the box scripts and the traces, start tools/jupyterhub/go.sh detached on the box, then the per-level
# pullers here (tools/ec2/pull.py over the jh transport, one level after another, kept awake by caffeinate).
#
#   export JH_URL=https://<hub> JH_USER=<user> JH_TOKEN=<token from POST /hub/api/users/<user>/tokens>
#   tools/jupyterhub/launch.sh                  # E-TRUNC (0055): the four e9t levels
#
# env: LEVELS (default the four e9t levels, run order) · LC_SHA (default HEAD; must be pushed) · TRACES (tarball of
#      traces/, default ~/lc-sitting-c/traces.tar.gz) · LC_RESULTS (where the mirror lands, default ./results; point
#      results/<level> there by symlink if it is another disk) · MIN_FREE_GIB / MAX_S passed through to go.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${JH_URL:?}" "${JH_USER:?}" "${JH_TOKEN:?}"
PY=.venv/bin/python
JHPY="$PY tools/jupyterhub/jh.py"
LEVELS=${LEVELS:-"e9t-full e9t-l65 e9t-l49 e9t-l32"}
LC_SHA=${LC_SHA:-$(git rev-parse HEAD)}
TRACES=${TRACES:-$HOME/lc-sitting-c/traces.tar.gz}
export LC_RESULTS=${LC_RESULTS:-$PWD/results}
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

echo "== home prerequisites"
git fetch -q origin
[ -n "$(git branch -r --contains "$LC_SHA" 2>/dev/null)" ] || { echo "REFUSED: LC_SHA $LC_SHA is not on origin"; exit 2; }
[ -f "$TRACES" ] || { echo "REFUSED: $TRACES missing (COPYFILE_DISABLE=1 tar --no-mac-metadata -czf $TRACES traces)"; exit 2; }
covs=""
for EXP in $LEVELS; do
  cov=results/$EXP/align/coverage.json
  [ -f "$cov" ] || { echo "REFUSED: $cov missing (e9 --align-only --config config/$EXP.toml)"; exit 2; }
  [ -f "results/$EXP/calibration/tau.json" ] || echo "  WARNING: results/$EXP/calibration/tau.json missing: the summarizer refuses without it (calibrate before the window ends)"
  [ -z "$(ls -A "results/$EXP" | grep -v -x -e align -e calibration)" ] || { echo "REFUSED: results/$EXP holds more than align/ + calibration/ (R1)"; exit 2; }
  covs="$covs COV_${EXP//-/_}=$(shasum -a 256 "$cov" | cut -c1-12)"
done
echo "  LC_SHA $LC_SHA;$covs"
echo "  launch $STAMP UTC (release_sweep.sh needs LAUNCH_UTC no later than this)" | tee "$HOME/lc-sitting-launch-utc.txt"

echo "== the slice"
$JHPY exec 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; df -h ~ | tail -1; ls -la ~ | head -30' 60

echo "== upload"
for f in tools/ec2/setup.sh tools/ec2/run.sh tools/ec2/probe_e9l.py tools/ec2/release_sweep.sh tools/jupyterhub/go.sh; do
  $JHPY up "$f" "$(basename "$f")"
done
$JHPY up "$TRACES" traces.tar.gz

echo "== go.sh, detached on the box"
$JHPY exec "cd ~ && setsid nohup env LC_SHA=$LC_SHA LEVELS='$LEVELS'$covs ${MIN_FREE_GIB:+MIN_FREE_GIB=$MIN_FREE_GIB} ${MAX_S:+MAX_S=$MAX_S} bash ~/go.sh > ~/go.log 2>&1 < /dev/null & sleep 3; cat ~/go.status" 30

echo "== pullers, one level after another (exits when the last level is complete and every kept dump is home)"
nohup caffeinate -dimsu bash -c 'for EXP in '"$LEVELS"'; do BOX_EXTRA_FILES="go.log go.status setup.$EXP.log" '"$PY"' -u tools/ec2/pull.py "$EXP" || exit $?; done; echo PULLERS_DONE' \
  >> "$LC_RESULTS/pull-$STAMP.log" 2>&1 < /dev/null &
echo "  pid $!; log $LC_RESULTS/pull-$STAMP.log"
cat <<EOF

watch:  $JHPY exec 'cat ~/go.status; tail -3 ~/go.log; tail -2 ~/e9t-*.log 2>/dev/null' 30
        tail -f $LC_RESULTS/pull-$STAMP.log
EOF
