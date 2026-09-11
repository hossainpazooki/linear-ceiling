#!/usr/bin/env bash
# tools/hf_backup.sh -- protocol R8: push a VERIFIED home mirror's staging tree to its PRIVATE Hugging Face dataset in
# R8 order (small records, then the tree, then the card as the completeness marker), and let tools/hf_verify_backup.py
# -- never an upload's exit status -- decide whether the backup is done.
#
# usage:  tools/hf_backup.sh [--check | --verify-only] <repo_id> <staging_dir>
#   (default)      preflight, records, tree, card, verify
#   --check        preflight only: tools, no conflicting process, token, login, dataset exists and is private
#   --verify-only  preflight, then the verifier; uploads nothing
#
# Run the command as ONE line with nothing pasted after it: when HF_TOKEN is not exported the script prompts on the
# terminal, and anything pasted after the command would be read as the token. The token is never echoed, never written
# to disk, never passed as a flag (R9).
#
# env:    MAX_ATTEMPTS   (3)   attempts per upload step when the Hub rate-limits commits
#         WAIT_MINUTES   (62)  wait between those attempts; the Hub's commit window is one hour
#         VERIFY_EXCLUDE ("")  space-separated repo paths the verifier skips; default none, so the card is verified too
#         ALLOW_PUBLIC   (0)   1 accepts a dataset the operator made PUBLIC (the free tier caps private storage at 100 GB);
#                              a missing dataset is still refused, so the CLI never creates one
#
# exit:   0 verified (or preflight OK with --check); 2 usage; 3 a conflicting upload or summarizer is running
#         4 not logged in; 5 no usable token; 6 dataset missing, unreadable, or public without ALLOW_PUBLIC=1
#         75 still rate-limited after MAX_ATTEMPTS (rerun later: it resumes); otherwise the failing hf/verifier code
#
# Why each guard exists (the E9-long push of 2026-09-10; learnings entries of that date):
# - `hf upload <repo> .` replaces `hf upload-large-folder`, deprecated in huggingface_hub 1.28.0. Rerunning it resumes:
#   files already committed are dropped against their remote oid, so a retry spends no commits on them.
# - The Hub accepts 128 commits per hour per repository and the uploader commits in batches; that push stopped at 247 of
#   724 files on the 429. Only that error is retried, after a wait. Every other failure stops the script.
# - `HfApi.upload_folder` is not a single-commit workaround: with hf_xet installed it batches exactly like the CLI.
# - A 401 out of `create_repo` means no credential reached the process (exist_ok already absorbs scope 401s), so the
#   script proves the login before the long step.
# - The CLI creates a MISSING repo with private=None, i.e. PUBLIC. The script refuses unless the dataset exists and is
#   private, or public by the operator's explicit ALLOW_PUBLIC=1 (E9-long's dataset, made public on 2026-09-10 when
#   the private 100 GB limit stopped the push twice).
# - Staging trees are hardlinked to the home mirror, and a summarizer rewrites summary.* and recheck/ in place, i.e.
#   under a live upload. The script refuses to start while one runs. Its logs go BESIDE the staging tree, never in it:
#   every file inside the tree is a file the upload must carry.
set -euo pipefail
shopt -s nullglob

MAX_ATTEMPTS=${MAX_ATTEMPTS:-3}
WAIT_MINUTES=${WAIT_MINUTES:-62}
VERIFY_EXCLUDE=${VERIFY_EXCLUDE:-}
ALLOW_PUBLIC=${ALLOW_PUBLIC:-0}
LOG=""

ts()  { date -u +%Y-%m-%dT%H:%M:%SZ; }
say() { printf '%s  %s\n' "$(ts)" "$*" >&2; if [ -n "$LOG" ]; then printf '%s  %s\n' "$(ts)" "$*" >>"$LOG"; fi; }
die() { local rc=$1; shift; say "STOP ($rc): $*"; exit "$rc"; }
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }   # Windows paths for python.exe

# ---- arguments --------------------------------------------------------------------------------------------------------
MODE=push
case "${1:-}" in
  --check)       MODE=check;  shift ;;
  --verify-only) MODE=verify; shift ;;
esac
if [ $# -ne 2 ]; then sed -n '6,10p' "$0" >&2; exit 2; fi
REPO=$1
[[ $REPO =~ ^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || die 2 "repo_id must be <owner>/<name>, got '$REPO'"
[ -d "$2" ] || die 2 "staging dir not found: $2"
STAGING=$(cd "$2" && pwd)
[ -n "$(find "$STAGING" -type f -not -path '*/.cache/huggingface/*' -print -quit)" ] || die 2 "staging dir holds no files: $STAGING"

# ---- tools ------------------------------------------------------------------------------------------------------------
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if   [ -x "$ROOT/.venv/Scripts/hf.exe" ]; then HF="$ROOT/.venv/Scripts/hf.exe"; PY="$ROOT/.venv/Scripts/python.exe"   # Windows (Git Bash)
elif [ -x "$ROOT/.venv/bin/hf" ];         then HF="$ROOT/.venv/bin/hf";         PY="$ROOT/.venv/bin/python"
else die 2 "no hf CLI under $ROOT/.venv (the system python has no huggingface_hub; install the dev extras)"; fi
VERIFIER="$ROOT/tools/hf_verify_backup.py"
[ -f "$VERIFIER" ] || die 2 "verifier missing: $VERIFIER"
export PYTHONIOENCODING=utf-8

LOGDIR="$(dirname "$STAGING")/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(basename "$STAGING").$(date -u +%Y%m%dT%H%M%SZ).$MODE.log"
say "R8 $MODE  repo $REPO  staging $STAGING"
say "log $LOG"

# ---- no concurrent upload or summarizer -------------------------------------------------------------------------------
conflicts() {
  if command -v powershell.exe >/dev/null 2>&1; then
    # Windows only: Git Bash's ps shows no command lines, so ask CIM. $me drops this PowerShell process, whose own
    # command line contains the pattern it searches for (the self-match trap).
    powershell.exe -NoProfile -NonInteractive -Command '$me = $PID; Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $me -and $_.CommandLine -match "hf(\.exe)?\W{0,2}\s+upload|summarize_e9" } | ForEach-Object { "{0} {1}" -f $_.ProcessId, $_.Name }' 2>/dev/null | tr -d '\r'
  else
    pgrep -af 'hf upload|summarize_e9' || true
  fi
}
busy=$(conflicts)
[ -z "$busy" ] || die 3 "another hf upload or a summarizer is running; let it finish or stop it first:
$busy"
if [ -n "$(find "$STAGING" -type f -links +1 -print -quit 2>/dev/null)" ]; then
  say "NOTE staging shares inodes with the home mirror (hardlinks): run no summarizer until this script exits."
fi

# ---- token and login ----------------------------------------------------------------------------------------------------
if [ -z "${HF_TOKEN:-}" ]; then
  { exec 3</dev/tty; } 2>/dev/null || die 5 "HF_TOKEN is not exported and there is no terminal to prompt on"
  printf 'HF token for %s (write scope; input hidden, press Enter): ' "$REPO" >&2
  IFS= read -rs HF_TOKEN <&3 || true
  exec 3<&-
  printf '\n' >&2
fi
[[ ${HF_TOKEN:-} == hf_* ]] || die 5 "HF_TOKEN does not look like a Hugging Face token (no hf_ prefix). If text was pasted after the command, it was read as the token. Nothing was sent."
export HF_TOKEN
trap 'unset HF_TOKEN' EXIT

who=$("$HF" auth whoami 2>&1) || true
user=$(printf '%s\n' "$who" | tr -d '\r' | sed -n 's/^[[:space:]]*user:[[:space:]]*//p' | head -1)
[ -n "$user" ] || die 4 "hf auth whoami did not confirm a login: $(printf '%s\n' "$who" | tr -d '\r' | head -1). Check the token and its expiry."
say "logged in as $user"

# ---- the dataset exists and is private (the CLI would create a missing one PUBLIC) -------------------------------------
priv=$(REPO="$REPO" "$PY" - 2>&1 <<'PYEOF'
import os
from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError, RepositoryNotFoundError
try:
    info = HfApi().dataset_info(os.environ["REPO"])
    print("private" if info.private else "PUBLIC")
except RepositoryNotFoundError:
    print("MISSING")
except HfHubHTTPError as e:
    print(f"ERROR {getattr(e.response, 'status_code', '')}")
PYEOF
) || true
priv=$(printf '%s\n' "$priv" | tr -d '\r' | tail -1)
case "$priv" in
  private) say "dataset exists and is private" ;;
  PUBLIC)  [ "$ALLOW_PUBLIC" = 1 ] || die 6 "dataset $REPO is PUBLIC; an R8 backup is private. Change its visibility in the Hub UI first, or rerun with ALLOW_PUBLIC=1 if public is intended."
           say "dataset exists and is PUBLIC (ALLOW_PUBLIC=1): everything this push uploads is world-readable" ;;
  MISSING) die 6 "dataset $REPO does not exist or this token cannot see it. Create it in the Hub UI as PRIVATE first." ;;
  *)       die 6 "could not read dataset $REPO: $priv" ;;
esac

if [ "$MODE" = check ]; then say "preflight OK; nothing uploaded (--check)"; exit 0; fi

# ---- uploads, retrying ONLY the commit-rate 429 -------------------------------------------------------------------------
hf_up() {   # hf_up <label> <hf upload arguments...>
  local label=$1; shift
  local attempt=1 rc out
  while :; do
    out=$(mktemp "$LOGDIR/.attempt.XXXXXX")
    say "[$label] attempt $attempt/$MAX_ATTEMPTS"
    set +e
    "$HF" upload "$@" 2>&1 | tee -a "$LOG" "$out"
    rc=${PIPESTATUS[0]}
    set -e
    if [ "$rc" -eq 0 ]; then rm -f "$out"; say "[$label] done"; return 0; fi
    if grep -q "rate limit for repository commits" "$out"; then
      rm -f "$out"
      if [ "$attempt" -ge "$MAX_ATTEMPTS" ]; then
        say "[$label] still rate-limited after $attempt attempts; rerun this script later, it resumes"
        return 75
      fi
      say "[$label] the Hub's 128-commits/hour limit: waiting $WAIT_MINUTES min, then resuming (committed files are skipped)"
      sleep $((WAIT_MINUTES * 60))
      attempt=$((attempt + 1))
      continue
    fi
    rm -f "$out"
    say "[$label] failed with exit $rc, not a rate limit; stopping (a 401 here means no credential reached hf)"
    return "$rc"
  done
}

cd "$STAGING"
if [ "$MODE" = push ]; then
  records=()
  for p in results/*/report.json results/*/summary.json results/*/summary.md \
           results/*/logs results/*/align results/*/controls results/*/scores results/*/calibration ./*.sha256; do
    [ -e "$p" ] && records+=("${p#./}")
  done
  say "step 1/3: the small records first (${#records[@]} paths) so a partial push still carries them"
  for p in "${records[@]}"; do
    hf_up "records $p" "$REPO" "$p" "$p" --repo-type dataset --commit-message "R8 records: $p"
  done
  say "step 2/3: the whole tree, card excluded (resumable; unchanged files are skipped)"
  hf_up tree "$REPO" . --repo-type dataset --exclude README.md --commit-message "R8 tree: $(basename "$STAGING")"
  if [ -f README.md ]; then
    say "step 3/3: the card, last, because it marks the dataset complete"
    hf_up card "$REPO" README.md README.md --repo-type dataset --commit-message "R8 card: complete"
  else
    say "step 3/3 SKIPPED: staging has no README.md card, so the dataset carries no completeness marker"
  fi
fi

# ---- verify: the only thing that settles it ------------------------------------------------------------------------------
say "verify: every file in both directions, LFS by sha256, the rest downloaded and hashed (hashes the whole tree; minutes)"
vargs=("$REPO" "$(native "$STAGING")")
if [ -n "$VERIFY_EXCLUDE" ]; then read -ra ex <<<"$VERIFY_EXCLUDE"; vargs+=(--exclude "${ex[@]}"); fi
set +e
"$PY" "$(native "$VERIFIER")" "${vargs[@]}" 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
set -e
if [ "$rc" -eq 0 ]; then
  say "BACKUP VERIFIED: $REPO matches $STAGING in both directions. Revoke the write token in the Hub UI now (R9)."
else
  say "verifier exit $rc: the backup is NOT verified. Rerun this script (it resumes) or re-upload only the files named above."
fi
exit "$rc"
