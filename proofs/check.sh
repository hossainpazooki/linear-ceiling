#!/usr/bin/env bash
# Check every proof by calling `lean` directly, then print the axiom audit.
# Use this when `lake build` is unavailable: on one macOS machine `lake` (5.0.0, Lean v4.34.0-rc2)
# exits with SIGTRAP before doing any work, while `lean` itself runs normally.
# Needs the built Mathlib in .lake/packages (see README.md).
set -euo pipefail
cd "$(dirname "$0")"
LEAN="${LEAN:-$HOME/.elan/bin/lean}"
OUT=.lake/build/lib/lean
LEAN_PATH="$(ls -d "$PWD"/.lake/packages/*/.lake/build/lib/lean | tr '\n' ':')$PWD/$OUT"
export LEAN_PATH
mkdir -p "$OUT/Carryover"
for m in Fstar Identity Seams Attention Numbers; do
  echo "lean Carryover/$m.lean"
  "$LEAN" -o "$OUT/Carryover/$m.olean" "Carryover/$m.lean"
done
"$LEAN" -o "$OUT/Carryover.olean" Carryover.lean
echo "lean Audit.lean"
"$LEAN" Audit.lean
