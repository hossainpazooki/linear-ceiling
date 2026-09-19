#!/usr/bin/env bash
# Keep a home-side spend ceiling alive for as long as a pod can bill.
#
# WHY THIS EXISTS. `rp.py watchdog` is the only thing that stops a runaway sitting, and on 2026-09-18
# it died mid-sitting on an `[SSL: UNEXPECTED_EOF_WHILE_READING]` and a rented pod ran five minutes
# with no ceiling at all. That specific bug is fixed (the loop now catches SystemExit as well as
# Exception, and retries), but the class is not: a watchdog is one process, and one process can be
# killed by an OOM, a closed terminal, a laptop lid, a bad deploy, or a bug nobody has hit yet. The
# fix for "the net can die" is not a better net -- it is a supervisor that notices and re-hangs it.
#
# Contract:
#   * exit 0  only when the watchdog itself exits 0, which now means TWO consecutive polls saw
#     nothing billing. That is the one condition under which no ceiling is needed.
#   * any other exit -> restart after RESTART_DELAY, audibly, forever. A supervisor with a retry
#     limit is a supervisor that gives up while a pod bills, so there is deliberately no limit.
#   * every restart is appended to the log with a UTC stamp and the exit code, so the cost of an
#     unwatched window is reconstructable afterwards rather than a guess.
#
# Start it IMMEDIATELY after `rp.py up`, detached, and leave it:
#   nohup bash tools/runpod/watchdog_supervised.sh > /dev/null 2>&1 &
#
# It does NOT terminate anything itself and holds no cloud authority: every decision belongs to
# `rp.py watchdog`, whose own guardrails (sitting ceiling, account ceiling, TTL, the long
# unreachable backstop) are the authority. This script only guarantees that something is asking.
set -uo pipefail                    # NOT -e: a non-zero watchdog exit is the case this handles

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PY="${PY:-$REPO/.venv/bin/python}"
LOG="${WATCHDOG_LOG:-$HOME/.cache/linear-ceiling/watchdog-supervisor.log}"
RESTART_DELAY="${RESTART_DELAY:-10}"
STAMP() { date -u +%FT%TZ; }

mkdir -p "$(dirname "$LOG")"
[ -x "$PY" ] || { echo "$(STAMP) REFUSED: no interpreter at $PY" | tee -a "$LOG"; exit 2; }

# One supervisor per machine. Two would double every alert and make the log unreadable at the exact
# moment it matters, and the second adds nothing: the first already restarts forever.
LOCK="${WATCHDOG_LOCK:-$HOME/.cache/linear-ceiling/watchdog-supervisor.lock}"
if ! mkdir "$LOCK" 2>/dev/null; then
  held="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if [ -n "$held" ] && kill -0 "$held" 2>/dev/null; then
    echo "$(STAMP) REFUSED: supervisor pid $held already holds $LOCK" | tee -a "$LOG"
    exit 3
  fi
  echo "$(STAMP) taking over a stale lock (pid ${held:-unknown} is gone)" | tee -a "$LOG"
  rm -rf -- "$LOCK" && mkdir "$LOCK" || { echo "$(STAMP) REFUSED: cannot take $LOCK" | tee -a "$LOG"; exit 3; }
fi
printf '%s\n' "$$" > "$LOCK/pid"
trap 'rm -rf -- "$LOCK"' EXIT

echo "$(STAMP) supervisor up: pid $$, watchdog args: $*" | tee -a "$LOG"
restarts=0
while true; do
  "$PY" "$HERE/rp.py" watchdog "$@"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "$(STAMP) watchdog exited 0 (two consecutive polls saw nothing billing) after $restarts restart(s); supervisor stopping" \
      | tee -a "$LOG"
    exit 0
  fi
  restarts=$((restarts + 1))
  # \a is deliberate: an unwatched pod is exactly the thing that should interrupt whatever the
  # operator is doing, and a silent line in a log nobody is reading is how the five minutes happened.
  printf '\a%s WATCHDOG DIED rc=%s; restart %s in %ss -- a pod may be billing UNWATCHED right now\n' \
    "$(STAMP)" "$rc" "$restarts" "$RESTART_DELAY" | tee -a "$LOG"
  sleep "$RESTART_DELAY"
done
