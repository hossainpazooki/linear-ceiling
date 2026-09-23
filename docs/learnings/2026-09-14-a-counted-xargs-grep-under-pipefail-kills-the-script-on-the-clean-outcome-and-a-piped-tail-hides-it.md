# A `$(find … | xargs grep -l … | awk …)` count under `set -euo pipefail` kills the script on the clean, zero-hit outcome, and a `| tail` on the caller hides the exit

kills: (nothing)
ts: 2026-09-14T03:42:00Z
commit: 12c113c2f9b0e32e6e74e340e266ff9e2a5f5acd
session: e9l-aws-run (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl)
status: verified
fact: the e9s R8 staging script (session scratchpad, not the repo) counted credential-shaped hits with
`hits=$(find "$S" … -print0 | xargs -0 grep -ls "$PAT" | awk 'END{print NR}')` under `set -euo pipefail`. When no file
matches, `grep -l` exits 1, `xargs` turns that into 123, `pipefail` makes the substitution fail, and `set -e` ends the
script before its verdict line: the clean stage produced no "credential sweep" line, no stage size and no `STAGED`. The
calling chain piped the script through `| tail -12`, so the chain reported exit 0 and the silence read like a truncated
log. The failure mode is the mirror image of the 2026-09-10 fail-OPEN sweep (`grep -l … && hits=1`): here the good outcome
is the one that aborts. The sweep was re-run by hand with the pipe guarded (`{ … || true; }`): planted control fired, 161
text files, 0 hits. Any count of matches taken through `grep` inside `$( )` under `pipefail` needs that guard, and a
script whose verdict matters is never piped through `tail` without `PIPESTATUS`.
basis: the staging chain's output ended at `k1.json: OK` / `k1.safetensors: OK` with no sweep line (stage card mtime
  2026-09-13 23:42 local = 03:42Z, the time used for ts:); the guarded re-run printed `control fired: 1 (must be 1);
  text files swept: 161; files with a hit: 0`. Re-captured at a5053b2 (after this entry's anchor; bash/xargs behaviour,
  not tree state): `set -o pipefail; n=$(… | xargs -0 grep -l "NO_SUCH_STRING_zq7" | awk …)` → `status=123 count=0`.
re-verify: bash -c 'set -o pipefail; n=$(find docs/learnings -name LEARNINGS.md -print0 | xargs -0 grep -l "NO_SUCH_STRING_zq7" | awk "END{print NR}"); echo "status=$? count=$n"'   # status=123 count=0: the zero-hit count fails the substitution
