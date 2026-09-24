#!/usr/bin/env bash
# Start the E9 driver as a distinct child, publish that child's PID, and wait for it.
# The surrounding launcher remains alive to write status and the final manifest.  The watchdog must
# signal this child rather than the surrounding shell, otherwise the Python driver keeps running.
set -uo pipefail

pid_file=$1
go_file=$2
mode=$3
lc_py=$4
config=$5

(
  for _ in $(seq 1 600); do [ -f "$go_file" ] && break; sleep 0.1; done
  if [ ! -f "$go_file" ]; then
    echo "driver release barrier timed out" >&2
    exit 97
  fi
  rm -f -- "$go_file"
  case "$mode" in
    plain)  exec "$lc_py" -u -m linear_ceiling.e9 --config "$config" ;;
    resume) exec "$lc_py" -u -m linear_ceiling.e9 --config "$config" --resume ;;
    complete) echo "[$(date -u +%FT%TZ)] report already complete; E9 driver skipped" ;;
    *) echo "unknown run mode: $mode" >&2; exit 96 ;;
  esac
) &
driver_pid=$!
printf '%s\n' "$driver_pid" > "$pid_file"
wait "$driver_pid"
