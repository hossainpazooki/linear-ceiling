#!/bin/bash
# R4 launcher for the E9-long driver on the box: detached, log rotated before any relaunch, exit code to ~/e9l.rc.
# Args pass through to the driver (`--resume` after a crash; the driver itself refuses a plain relaunch over an
# unfinished report). Home-side liveness is read from ~/e9l.rc and the log, never from a self-matching pgrep;
# if you must look: pgrep -f "[l]inear_ceiling.e9 " (bracketed).
EXP=${EXP:-e9l}
cd ~/linear-ceiling
# CPU thread cap from the cgroup quota (the sitting_b.sh rule). The per-token scorer is CPU-bound; on a container that
# shows 128 cores but is throttled to a 13.6-CPU quota, the default 191 threads halved throughput (E-TRUNC FULL,
# 2026-10-08: 48 % of scheduler periods throttled; 255-370 s per handoff against 130-150 s once capped). An explicit
# LC_THREADS in the environment wins; no quota readable -> nproc, capped at 16 (beyond that the reductions thrash).
if [ -z "${LC_THREADS:-}" ]; then
  if [ -r /sys/fs/cgroup/cpu.max ]; then read -r _q _p < /sys/fs/cgroup/cpu.max || true
    [ "${_q:-max}" != "max" ] && [ "${_p:-0}" -gt 0 ] && LC_THREADS=$(( _q / _p )); fi
  [ -z "${LC_THREADS:-}" ] || [ "$LC_THREADS" -lt 1 ] && LC_THREADS=$(nproc 2>/dev/null || echo 8)
  [ "$LC_THREADS" -gt 16 ] && LC_THREADS=16
fi
export OMP_NUM_THREADS="$LC_THREADS" OPENBLAS_NUM_THREADS="$LC_THREADS" MKL_NUM_THREADS="$LC_THREADS" \
       NUMEXPR_NUM_THREADS="$LC_THREADS" VECLIB_MAXIMUM_THREADS="$LC_THREADS"
[ -f ~/$EXP.log ] && mv ~/$EXP.log ~/"$EXP.$(date -u +%Y%m%dT%H%M%SZ).halt.log"
rm -f ~/$EXP.rc
setsid nohup bash -c '.venv/bin/python -u -m linear_ceiling.e9 --config "config/$0.toml" "${@:1}"; echo "EXIT=$?" > ~/$0.rc' "$EXP" "$@" \
  > ~/$EXP.log 2>&1 < /dev/null &
echo "launched pid $! at $(date -u +%FT%TZ) args: $* (threads $LC_THREADS)" | tee -a ~/launches.log
