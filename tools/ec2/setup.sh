#!/bin/bash
# E9-long box setup on a rented EC2 g6e (1x L40S 48 GB), Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04).
# Idempotent; writes EXIT=<rc> to ~/setup.rc on exit (the home poller keys on that file, never on pgrep).
# Inputs uploaded to ~ before this runs: k1.json, k1.safetensors (the mapper, R3), traces.tar.gz (the manifest's bytes),
# and -- for a pair whose weights are GATED -- hf-cache.tar.gz, the pre-staged HF cache (see "weights" below).
# Defaults below are entry 0035's: EXP=e9l, the Qwen pair, and the mapper and manifest shas of the R3 table of
# docs/2026-09-10-e9l-gpu-runbook.md. EVERY pin is overridable from the environment, and a second family changes
# nothing here but those values -- box.sh ssh 'setsid nohup env EXP=... PAIR=... UP_SHA=... bash ~/setup.sh ...'.
# Both clones come from https://github.com/hossainpazooki/... AT A SHA, so the upstream commit and every
# linear-ceiling commit this sitting needs MUST BE PUSHED to those remotes before a box is brought up; a sha that
# exists only in the home checkout fails here at `checkout --detach`, after the instance is already billing.
trap 'echo "EXIT=$?" > ~/setup.rc' EXIT
set -euo pipefail
EXP=${EXP:-e9l}                                            # experiment name: config/$EXP.toml, results/$EXP/ (e9l = the 09-10 sitting)
PAIR=${PAIR:-qwen3-0.6b-to-1.7b}                           # must be a key of the upstream PAIRS at $UP_SHA; keys mappers/ and data/kv/
LC_SHA=${LC_SHA:-3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806}   # linear-ceiling commit to clone at: the one carrying the registration entry
UP_SHA=${UP_SHA:-063f4023fdde67dedbee01a92518ce7f83f6cf5d}   # upstream: the RoPE-spec commit (config/$EXP.toml upstream_sha)
MAPPER_JSON_SHA=${MAPPER_JSON_SHA:-2fd05c333156607436af128ccd7a009f175f13138d27e4126588c24f515cc86e}
MAPPER_ST_SHA=${MAPPER_ST_SHA:-cd6a8d939b36db901f50e13bae446aef833f5d2ea7276658f499e993e63607f2}
HOME_COVERAGE_SHA12=${HOME_COVERAGE_SHA12:-492d8f0db8d0}   # results/$EXP/align/coverage.json at home as the entry cites it (home bytes; a CRLF home file hashes differently from the box LF copy: reported, not fatal)
HF_HOME=${HF_HOME:-$HOME/.cache/huggingface}; export HF_HOME
WEIGHTS_TGZ=${WEIGHTS_TGZ:-$HOME/hf-cache.tar.gz}          # optional: a home-made HF cache (tar of the `hub/` tree) for a gated pair
GATED_ORGS=${GATED_ORGS:-meta-llama}                       # orgs whose weights cannot be fetched without a token, so must be pre-staged
cd ~
echo "== $(date -u +%FT%TZ) host"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
df -h / | tail -1; nproc; free -g | head -2
echo "== uv"
[ -x ~/.local/bin/uv ] || curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null
export PATH=$HOME/.local/bin:$PATH; uv --version
echo "== clones at the pins (detached)"
[ -d ~/kv-transfer-replication/.git ] || git clone -q https://github.com/hossainpazooki/kv-transfer-replication.git
git -C ~/kv-transfer-replication fetch -q origin && git -C ~/kv-transfer-replication checkout -q --detach "$UP_SHA"
[ -d ~/linear-ceiling/.git ] || git clone -q https://github.com/hossainpazooki/linear-ceiling.git
git -C ~/linear-ceiling fetch -q origin && git -C ~/linear-ceiling checkout -q --detach "$LC_SHA"
git -C ~/kv-transfer-replication log --oneline -1; git -C ~/linear-ceiling log --oneline -1
echo "== upstream env: python 3.12, torch 2.11.0+cu128 (the 09-04 / 09-08 stack), transformers 5.15.1, numpy 2.5.2"
cd ~/kv-transfer-replication
[ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv
uv pip install -q --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu128 torch==2.11.0
uv pip install -q --python .venv/bin/python -e . transformers==5.15.1 numpy==2.5.2
echo "== linear-ceiling env (CPU torch; the driver calls the upstream by subprocess in its own venv)"
cd ~/linear-ceiling
[ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv
uv pip install -q --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch
uv pip install -q --python .venv/bin/python -e ".[dev]" numpy==2.5.2
echo "== pair $PAIR from the upstream registry at $UP_SHA (this also proves the pin registers it)"
SRC_ID=""; TGT_ID=""
read -r SRC_ID TGT_ID < <(~/kv-transfer-replication/.venv/bin/python -c \
  "from kvt.pairs import PAIRS; p = PAIRS['$PAIR']; print(p.source, p.target)") || true
[ -n "$SRC_ID" ] && [ -n "$TGT_ID" ] || { echo "ABORT: pair $PAIR is not a key of the upstream PAIRS at $UP_SHA"; exit 6; }
echo "  source $SRC_ID  target $TGT_ID"
echo "== weights: a pre-staged HF cache, or the public path"
# No HF token may ever exist on this box: release checklist R7 step 4 asserts token-shaped strings NEVER EXISTED,
# which is a much stronger claim than "were removed", and it is only true if nothing here ever needed one. Public
# repos (Qwen3) need no token and download at run time, unchanged. Gated repos (meta-llama) are staged INSTEAD:
# the operator downloads both snapshots at home with their own token, then
#   tar -czf hf-cache.tar.gz -C ~/.cache/huggingface hub
# (hub/ ONLY: never the parent, which holds ~/.cache/huggingface/token), uploads it with box.sh put, and this step
# unpacks it and switches the hub to offline. The cache must hold the FULL snapshots (*.safetensors and *.json):
# the upstream dumps load the weights from it, and the linear-ceiling driver's own `--align-only` resolves the
# tokenizer through `weights.snapshot` -> `snapshot_download`, which is a network call unless offline. The tarball
# is deleted once unpacked -- it is ~22 GB of duplicate on a 250 GB root, and release_sweep.sh's R7 step 0
# ours-list does not name it, so leaving it behind would abort the release as a foreign file.
[ -z "${HF_TOKEN:-}" ] || { echo "ABORT: HF_TOKEN is set in this environment; no token may reach the box"; exit 7; }
if [ -f "$WEIGHTS_TGZ" ]; then
  mkdir -p "$HF_HOME"; tar -xzf "$WEIGHTS_TGZ" -C "$HF_HOME"; rm -f "$WEIGHTS_TGZ"
  echo "  unpacked $WEIGHTS_TGZ into $HF_HOME and removed the tarball"
fi
staged=1
for MID in "$SRC_ID" "$TGT_ID"; do
  D="$HF_HOME/hub/models--${MID//\//--}"
  # A half-made tarball is worse than none: it passes here and then 404s offline, hours in. Require the three
  # things that are actually read -- the config, the tokenizer, and at least one weight shard.
  miss=""
  for want in config.json tokenizer.json "*.safetensors"; do
    [ -n "$(find "$D/snapshots" -maxdepth 2 -name "$want" -print -quit 2>/dev/null)" ] || miss="$miss $want"
  done
  if [ -z "$miss" ]; then
    echo "  staged $MID -> $(du -sh "$D" | cut -f1)"
    find "$D/snapshots" -maxdepth 2 \( -name config.json -o -name tokenizer.json \) | sort | xargs -r sha256sum
  else
    staged=0; echo "  NOT staged: $MID ($D missing:$miss)"
  fi
done
for MID in "$SRC_ID" "$TGT_ID"; do
  for ORG in ${GATED_ORGS//,/ }; do
    case "$MID" in "$ORG"/*)
      [ "$staged" = 1 ] || { echo "ABORT: $MID is gated ($ORG) and not staged; upload hf-cache.tar.gz first -- fetching it here would need a token, and R7 step 4 must keep asserting that none ever existed"; exit 8; };;
    esac
  done
done
if [ "$staged" = 1 ]; then
  # Refuse a cache that carries the operator's token along with the weights (the tar is made from ~/.cache/huggingface).
  tok=$(find "$HF_HOME" -maxdepth 2 \( -name token -o -name stored_tokens \) | tee /dev/stderr | awk 'END{print NR}')
  [ "$tok" = 0 ] || { echo "ABORT: the staged cache carries token file(s) (listed above); rebuild the tarball from hub/ only"; exit 9; }
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  # The env file lives INSIDE $HF_HOME on purpose: R7 step 0 aborts on any file in ~ it does not name, and step 4
  # deletes the whole cache, so the offline switch is released with the weights it belongs to.
  printf 'HF_HOME=%s\nHF_HUB_OFFLINE=1\nTRANSFORMERS_OFFLINE=1\n' "$HF_HOME" > "$HF_HOME/offline.env"
  echo "  offline: HF_HUB_OFFLINE=1 for this script; every LATER step must carry it too --"
  echo "    env \$(cat $HF_HOME/offline.env) bash ~/run.sh"
  echo "    env \$(cat $HF_HOME/offline.env) ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py"
else
  echo "  no staged cache; $SRC_ID and $TGT_ID are public and download at run time (the Qwen path, unchanged)"
fi
# An [e8] config (sitting A) is the sitting that CREATES the mapper, so it cannot be asked to check one
# in, and `linear_ceiling.e9` cannot parse it at all -- `--check` raises KeyError('e9') on the [e8] table.
# The kind is read from the config itself, not from the experiment name, so a future e8* / e9* config
# needs no edit here. Everything outside these two blocks (clone, venv, weights, traces, manifest) is
# identical for both kinds and is deliberately NOT duplicated.
if grep -qE '^\[e8\]' "$HOME/linear-ceiling/config/$EXP.toml"; then KIND=e8; else KIND=e9; fi
echo "== config kind: $KIND (config/$EXP.toml)"
if [ "$KIND" = e9 ]; then
  echo "== mapper by sha (R3; gitignored upstream artifact, the 2026-09-04 launch died without it)"
  # k1 is literal on purpose: every registered config's [e9.mapper] k is 1, and release_sweep.sh's ours-list names
  # k1.json / k1.safetensors by name -- a different k needs that list widened in the same commit.
  MD=~/kv-transfer-replication/mappers/$PAIR; mkdir -p "$MD"
  for f in k1.json k1.safetensors; do [ -f "$MD/$f" ] || mv ~/"$f" "$MD/$f"; done
  echo "$MAPPER_JSON_SHA  $MD/k1.json" | sha256sum -c -
  echo "$MAPPER_ST_SHA  $MD/k1.safetensors" | sha256sum -c -
else
  echo "== mapper: SKIPPED -- sitting A produces it (mappers/$PAIR/ must be absent or the fit would"
  echo "   overwrite an artifact some other cell's R3 row names; refusing here is cheaper than on the card)"
  MD=~/kv-transfer-replication/mappers/$PAIR
  if [ -e "$MD" ] && [ -n "$(ls -A "$MD" 2>/dev/null)" ]; then
    echo "SETUP REFUSED: $MD already holds artifacts on a sitting that exists to create them" >&2; exit 1
  fi
fi
echo "== traces: the home tarball, checked against the committed manifest (both directions + bytes)"
[ -d ~/linear-ceiling/traces ] || tar -xzf ~/traces.tar.gz -C ~/linear-ceiling
.venv/bin/python -m linear_ceiling.e7_manifest check | tail -1 | tee ~/manifest_check.out | grep -q "^manifest ok"
echo "== gate"
.venv/bin/python -m linear_ceiling."$KIND" --check --config "config/$EXP.toml"
if [ "$KIND" = e9 ]; then
  echo "== alignment on the box (expected to reproduce home's coverage.json sha $HOME_COVERAGE_SHA12; a mismatch is reported, not fatal here)"
  .venv/bin/python -m linear_ceiling.e9 --align-only --config "config/$EXP.toml" | tail -2
  sha256sum "results/$EXP/align/coverage.json"
else
  # E8 has no alignment step: its corpus is the sampled agent text of entry 0016 s4, not handoff slices.
  # The traces ARE still required and were checked above -- arm (b) samples from them.
  echo "== alignment: SKIPPED (an [e8] config has no handoff alignment; arm (b) samples traces/ directly)"
fi
echo "== versions"
~/kv-transfer-replication/.venv/bin/python -c "import torch,transformers,numpy;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.cuda.get_device_name(0));print('transformers',transformers.__version__,'numpy',numpy.__version__)"
.venv/bin/python -c "import sys,torch,numpy;print('lc python',sys.version.split()[0],'torch',torch.__version__,'numpy',numpy.__version__)"
echo "== safety: the box halts itself in 24 h (shutdown behaviour = stop: billing ends, the volume stays); cancel with sudo shutdown -c"
sudo shutdown -h +1440 > /dev/null 2>&1 || true
echo "SETUP_DONE $(date -u +%FT%TZ)"
