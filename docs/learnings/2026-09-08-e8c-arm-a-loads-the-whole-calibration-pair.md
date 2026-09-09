ts: 2026-09-08T23:36:00Z
commit: a71c3b4
session: Claude Code session 878feb6f, e8c run at home
status: verified
fact: `e8 --config config/e8c.toml` arm (a) scores the tagged mapper on its OWN calibration dumps, so the upstream scorer loads the full n = 420 pair (about 24 GB committed) at home; the n = 50 amendment's arm (a) needed 2.8 GB. On a 31.7 GB machine this pages for the whole run (about 37 min) and the summarizer repeats it (about 42 min); running the E9 rescore beside it pushed commit to 47 / 48 GB. Budget e8c-style runs like a dump, not like a rescore, and run them alone.
basis: `Get-Process` during the run: `26232 python pm=23.69GB ws=4.12GB cpu=00:04:32` under `scripts/score_mapper.py --mapper ...n420...`; `Win32_OperatingSystem`: `RAM free=0GB; commit used=47.1GB of 48.3GB`; `Pages Input/sec` 3045 and 1620 on two samples; both runs exited clean (`results/e8c/report.json`, `results/e9c/report.json`).
re-verify: grep -n "24 GB committed" docs/2026-09-08-n420-target-dump-runbook.md | head -1
