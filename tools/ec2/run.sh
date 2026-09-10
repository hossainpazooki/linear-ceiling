#!/bin/bash
# R4 launcher for the E9-long driver on the box: detached, log rotated before any relaunch, exit code to ~/e9l.rc.
# Args pass through to the driver (`--resume` after a crash; the driver itself refuses a plain relaunch over an
# unfinished report). Home-side liveness is read from ~/e9l.rc and the log, never from a self-matching pgrep;
# if you must look: pgrep -f "[l]inear_ceiling.e9 " (bracketed).
cd ~/linear-ceiling
[ -f ~/e9l.log ] && mv ~/e9l.log ~/"e9l.$(date -u +%Y%m%dT%H%M%SZ).halt.log"
rm -f ~/e9l.rc
setsid nohup bash -c '.venv/bin/python -u -m linear_ceiling.e9 --config config/e9l.toml "$@"; echo "EXIT=$?" > ~/e9l.rc' _ "$@" \
  > ~/e9l.log 2>&1 < /dev/null &
echo "launched pid $! at $(date -u +%FT%TZ) args: $*" | tee -a ~/launches.log
