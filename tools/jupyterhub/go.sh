#!/bin/bash
# One-launch multi-level E9 sitting on a JupyterHub-only GPU box (Algoverse; no ssh): the mapper from the public e9
# dataset (setup.sh checks it by sha), setup + the box's own alignment per level (a coverage sha unequal to home's is
# FATAL here, unlike setup.sh alone), the R2 probe at MAX_S, then the levels one after another -- each started only
# when the disk has MIN_FREE_GIB free, i.e. the home puller has taken the previous level's kept dumps away.
# Launched detached by tools/jupyterhub/launch.sh; progress: ~/go.status (one line) and ~/go.log.
# Needs ~/setup.sh ~/run.sh ~/probe_e9l.py ~/traces.tar.gz (uploaded by launch.sh) and, per level, COV_<level> =
# sha256[:12] of results/<level>/align/coverage.json at home (LF bytes), e.g. COV_e9t_full=5d01067ab8bb.
set -euo pipefail
LC_SHA=${LC_SHA:?LC_SHA is required (a pushed commit carrying the registration entry)}
LEVELS=${LEVELS:-"e9t-full e9t-l65 e9t-l49 e9t-l32"}       # run order (runbook 2026-10-04 section 0)
MAX_S=${MAX_S:-80111}                                       # longest prefill of the run: FULL's |S| (0036)
MIN_FREE_GIB=${MIN_FREE_GIB:-70}                            # a level's kept + bridge dumps stay on disk until pulled
MAPPER_URL=${MAPPER_URL:-https://huggingface.co/datasets/hossainpazooki/linear-ceiling-e9-2026-09-04/resolve/main/mappers/qwen3-0.6b-to-1.7b}

status() { echo "$*" > ~/go.status; echo "== $(date -u +%FT%TZ) $*"; }
fail() { status "FAILED $*"; exit 1; }
free_gib() { df -Pk ~ | awk 'NR==2{print int($4/1048576)}'; }
cd ~
status "START $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
df -h ~ | tail -1
[ "$(free_gib)" -ge "$MIN_FREE_GIB" ] || fail "disk: $(free_gib) GiB free < $MIN_FREE_GIB"
for f in k1.json k1.safetensors; do
  [ -f ~/"$f" ] || [ -f ~/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/"$f" ] || curl -sSfL -o ~/"$f" "$MAPPER_URL/$f"
done

for EXP in $LEVELS; do
  status "SETUP $EXP"
  var="COV_${EXP//-/_}"; want=${!var:-}
  [ -n "$want" ] || fail "$var is required (home coverage sha12)"
  EXP=$EXP LC_SHA=$LC_SHA HOME_COVERAGE_SHA12=$want bash ~/setup.sh > ~/setup."$EXP".log 2>&1 || fail "setup $EXP (setup.$EXP.log)"
  got=$(sha256sum ~/linear-ceiling/results/"$EXP"/align/coverage.json | cut -c1-12)
  [ "$got" = "$want" ] || fail "coverage $EXP: box $got != home $want"
done

status "PROBE T=$MAX_S"
EXP=${LEVELS%% *} MAX_S=$MAX_S ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py > ~/probe.log 2>&1 || true
n_ok=$(grep -c "\"T\": $MAX_S, .*\"ok\": true" ~/probe.log || true)
[ "$n_ok" = 2 ] || fail "probe: $n_ok of 2 models fit at T=$MAX_S (probe.log)"

for EXP in $LEVELS; do
  while [ "$(free_gib)" -lt "$MIN_FREE_GIB" ]; do status "WAIT disk before $EXP: $(free_gib) GiB free"; sleep 60; done
  status "RUN $EXP"
  EXP=$EXP bash ~/run.sh
  while [ ! -f ~/"$EXP".rc ]; do sleep 30; done
  grep -q '^EXIT=0$' ~/"$EXP".rc || fail "run $EXP: $(cat ~/"$EXP".rc) ($EXP.log)"
done
status "DONE $(date -u +%FT%TZ)"
