# `kept_bytes` is read by the pull verifier and written by nothing, so outstanding bytes are always zero

ts: 2026-09-21T02:38:10Z
commit: 3d2fbb14d3919cd2e798f4ffbe5132506cef1c7b
session: carryover-iclr-pickup-drift-wrapup (e7805827; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\e7805827-47f9-400a-a107-71d2eeb94fb2.jsonl)
status: verified
fact: On branch `llama-second-family` at 7f83cea (PR #5, not on main), `tools/runpod/pull_verify_b.py` sizes the
not-yet-pulled kept dumps from a report field `kept_bytes`, defaulting to 0. Nothing in `src/` or `tools/` writes that
field: the driver records `kept_dumps` (fingerprints) and `kept_dir` only. The outstanding-bytes figure is therefore 0
for every driver-shaped report, even with every kept file missing, which disables the measured early-drain condition
entry 0043 registers and understates the mirror's free-space need. A reader with a `.get(..., 0)` default and no writer
is a silent zero, the same shape as the forbidden zero of entry 0006. Fix on the pull side (sizes from the remote
listing or from `verify_artifacts`) so the registered driver is not touched.
basis: at main 3d2fbb1, 2026-09-21T02:38:10Z, `git grep -n "kept_bytes" 7f83cea -- src tools` printed four lines, all
  in `tools/runpod/pull_verify_b.py`: 883 and 889 (`bad, checked, _kept_bytes = verify_artifacts(local, items)`, a local
  variable), 894 (`state["bytes_verified_total"] = … + _kept_bytes`) and 1042 (`total += int(rec.get("kept_bytes",
  {}).get(dump, 0)) or 0`). `git show 7f83cea:src/linear_ceiling/e9.py | grep -n 'rec\["kept_'` printed only
  `353: rec["kept_dumps"] = …` and `354: rec["kept_dir"] = …`. Whether line 894 re-adds already-verified files each
  round was NOT traced. First found by an outside review of PR #5; posted to the PR as issuecomment-5754565968.
re-verify: git grep -n "kept_bytes" 7f83cea -- src tools   # expect: 4 lines, all in tools/runpod/pull_verify_b.py, none assigning rec["kept_bytes"] (needs origin/llama-second-family fetched)
