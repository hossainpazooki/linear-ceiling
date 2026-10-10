#!/bin/bash
# R8 staging for the E-TRUNC datasets, by HARD LINKS (the Mac has 72 Gi free against ~207 G of mirrors). Layout per the
# campaign runbook section 11 and the e9l/e9fl cards: results/<exp>/ at the root for the four levels (recheck/ excluded)
# plus results/e9t/ (shrinkage, compare, release hashes, logs); the upstream INPUTS in the upstream's own layout
# (mappers, archived r2.json, the generic dumps the tau calibration reads, the probe); then SHA256SUMS over every file
# except itself and the card. The card README.md is written separately and uploaded last. Idempotent.
set -euo pipefail
LC=~/dev/linear-ceiling
UP=~/dev/kv-transfer-replication
PAIR=qwen3-0.6b-to-1.7b
ST=~/dev/hf-staging/linear-ceiling-e9t-2026-10-08
mkdir -p "$ST/results" "$ST/mappers/$PAIR" "$ST/results/mapper/$PAIR" "$ST/data/kv" "$ST/results/probe"
link_tree() {   # link_tree <src_dir> <dst_dir> [find-prune-name]
  local src=$1 dst=$2 prune=${3:-__none__}
  mkdir -p "$dst"
  ( cd "$src" && find . -type d -name "$prune" -prune -o -type d -print | while read -r d; do mkdir -p "$dst/$d"; done )
  ( cd "$src" && find . -type d -name "$prune" -prune -o -type f -print | while read -r f; do [ -e "$dst/$f" ] || ln "$f" "$dst/$f"; done )
}
for e in e9t-full e9t-l65 e9t-l49 e9t-l32; do link_tree "$LC/results/$e" "$ST/results/$e" recheck; done
link_tree "$LC/results/e9t" "$ST/results/e9t"
for f in k1.json k1.safetensors; do [ -e "$ST/mappers/$PAIR/$f" ] || ln "$UP/mappers/$PAIR/$f" "$ST/mappers/$PAIR/$f"; done
[ -e "$ST/results/mapper/$PAIR/r2.json" ] || ln "$UP/results/mapper/$PAIR/r2.json" "$ST/results/mapper/$PAIR/r2.json"
link_tree "$UP/data/kv/$PAIR" "$ST/data/kv/$PAIR"
link_tree "$UP/results/probe/$PAIR" "$ST/results/probe/$PAIR"
for t in "$UP"/data/tokens/${PAIR}_*; do [ -e "$t" ] && { mkdir -p "$ST/data/tokens"; [ -e "$ST/data/tokens/$(basename "$t")" ] || ln "$t" "$ST/data/tokens/"; }; done
cd "$ST"
echo "files: $(find . -type f ! -name SHA256SUMS ! -name README.md | wc -l | tr -d ' ')  bytes: $(find . -type f ! -name SHA256SUMS ! -name README.md -print0 | xargs -0 stat -f %z | awk '{s+=$1} END {print s}')"
echo "hashing (hard links read the mirror bytes once each)..."
find . -type f ! -name SHA256SUMS ! -name README.md | sort | xargs shasum -a 256 > SHA256SUMS.tmp && mv SHA256SUMS.tmp SHA256SUMS
echo "SHA256SUMS lines: $(wc -l < SHA256SUMS | tr -d ' ')"
grep -c "results/e9t-full/report.json\|results/e9t/compare.json" SHA256SUMS
echo "credential sweep over text files (positive control first):"
printf 'hf_%s\n' "ABCDEFGHIJKLMNOPQRSTUVWXYZ" > /tmp/planted.txt; grep -l "hf_[A-Za-z0-9]\{20,\}" /tmp/planted.txt > /dev/null && echo "  control: pattern fires"; rm -f /tmp/planted.txt
find . -type f \( -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.log" -o -name "*.sh" -o -name "*.py" -o -name "*.toml" -o -name "*.sha256" \) -print0 | xargs -0 grep -l "hf_[A-Za-z0-9]\{20,\}\|HF_TOKEN=" 2>/dev/null | awk 'END {print "  token-shaped files:", NR}'
echo "staged at $ST  $(date -u +%FT%TZ)"
