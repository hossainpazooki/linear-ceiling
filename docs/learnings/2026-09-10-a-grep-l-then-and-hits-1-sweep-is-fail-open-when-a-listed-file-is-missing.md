# A `grep -l … && hits=1` sensitive-data sweep is fail-open when any listed file is missing: grep exits 2 on the missing file even after printing a match, and the hit is never counted

kills: (nothing)
ts: 2026-09-10T01:21:54Z
commit: 3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806
session: linear-ceiling-e9l-box (018fwd195AS7uS2tvJdgSoYP)
status: verified
fact: The E9-long release sweep (`tools/ec2/release_sweep.sh`, R7 step 4) searched `~/.bash_history ~/*.sh ~/*.py
~/*.log` for token-shaped strings with `grep -rl PATTERN … && hits=1`. On the box there was no `~/.bash_history`
(non-interactive ssh), so grep printed its one match (the script's own pattern literal, a false positive) and then
exited 2 for the missing file; `&& hits=1` never ran and the sweep reported `sweep hits: 0` with the match visible
two lines above it. POSIX grep returns 2 whenever an error occurred, regardless of matches, unless `-q` matched
first. A sweep whose exit status is the verdict is therefore fail-open exactly when a haystack file is absent,
which is the common case on a fresh box. The fix counts matched files (`grep -rls … | awk 'END{print NR}'`)
and excludes the sweep script itself; a real token would have been reported as "0 hits" by the version that ran.
basis: `results/e9l/logs/box/release.log` (pulled 2026-09-10 01:2xZ): under `== step 4: sensitive-data sweep` the line
  `/home/ubuntu/release_sweep.sh` (grep's `-l` output) is followed by `  sweep hits: 0`; the pre-fix script that
  produced it is the pulled `results/e9l/logs/box/release_sweep.sh`; reproduced at home with
  `grep -l x /nonexistent tools/ec2/release_sweep.sh; echo $?` → prints the file, exits 2.
re-verify: grep -c "awk 'END{print NR}'" tools/ec2/release_sweep.sh   # 2 (token sweep + ~/.aws sweep count matches, never `&& hits=1`)
