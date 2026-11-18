#!/usr/bin/env bash
# Check every proof by calling `lean` directly, then print the axiom audit.
# Use this when `lake build` is unavailable. It was written for the earlier pins, Lean v4.34.0-rc2,
# whose `lake` exits with SIGTRAP on macOS 27 (lean4 issue 15087). At the current pins it was run on
# 2026-11-17 (UTC) on macOS 27 (arm64), with LEAN set to the `lean` of the v4.34.0 toolchain: it
# compiled the ten modules and `Carryover.lean`, printed the audit's 114 results and exited 0.
# Needs the built Mathlib in .lake/packages (see README.md).
set -euo pipefail
cd "$(dirname "$0")"
LEAN="${LEAN:-$HOME/.elan/bin/lean}"
OUT=.lake/build/lib/lean
LEAN_PATH="$(ls -d "$PWD"/.lake/packages/*/.lake/build/lib/lean | tr '\n' ':')$PWD/$OUT"
export LEAN_PATH
mkdir -p "$OUT/Carryover"
for m in Fstar Identity Seams Attention Numbers Pred PredKL PredFlip PredMain PredStop; do
  echo "lean Carryover/$m.lean"
  "$LEAN" -o "$OUT/Carryover/$m.olean" "Carryover/$m.lean"
done
"$LEAN" -o "$OUT/Carryover.olean" Carryover.lean
echo "lean Audit.lean"
"$LEAN" Audit.lean
