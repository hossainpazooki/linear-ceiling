# A relaunch script that redirects `> e9.log` deletes the previous attempt's halt log; rotate and pull before every relaunch

kills: (nothing)
ts: 2026-09-04T18:29:12Z
commit: 0a19b56ee3bd4b45eca28f84a20cf6ded4dcd436
session: algoverse-gpu-run-session (8a0fb97e-0020-43aa-a9b2-9ae67eec2fe3)
status: verified
fact: Both relaunch scripts on the E9 box (run2.sh at 17:14 UTC, run3.sh at 17:35 UTC) started the
driver with `setsid nohup ... > e9.log 2>&1`, the exact form the runbook prescribes, so by the time
the release checklist asked for the halt logs of the two refused attempts (16:43 UTC OOM, 17:16 UTC
missing mapper) the box held one e9.log, the final run's, and nothing else. The only surviving
record of the refused attempts was whatever the driving session had printed at the time (tail -30,
head -12, tail -4 of the file), reconstructed into results/e9/logs/halt-reconstructed/ with a README
that says so. A verdict entry cites refused runs (0027 does); a box that is wiped at expiry is the
only copy until pulled; a redirect is a silent delete.
basis: `ls -la ~/linear-ceiling/*.log ~/*.log` on the box at 18:2x UTC printed exactly
  `e9.log 2349 Sep 4 18:12`, `setup.log 1891 Sep 4 16:30`, `setup2.log 314 Sep 4 16:41`; run2.sh and
  run3.sh (session scratch, copied verbatim to the box) both contain
  `setsid nohup .venv/bin/python -m linear_ceiling.e9 > e9.log 2>&1 < /dev/null &`; the transcript
  captures are at 16:43:29Z (tail -30) and 17:20:10Z / 17:20:28Z (tail -4, head -12).
re-verify: grep -n "> e9.log 2>&1" docs/2026-09-02-e9-gpu-runbook.md tools/jupyterhub/README.md
