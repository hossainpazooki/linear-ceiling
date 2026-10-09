# The watchdog's `--kill` default is $9.00 of CAMPAIGN spend and `up --hours` is its TTL; set both explicitly on every sitting after a campaign's first

ts: 2026-10-08T23:40:00Z
commit: b33c6ce
session: e-trunc-0057-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `rp.py watchdog` terminates the pod when `camp >= a.kill` (campaign spend, not sitting spend) with no drain, and
`--kill` defaults to 9.0; `up --cap` is checked once at creation and never reaches the watchdog. Its TTL defaults to the
`--hours` given at `up`, so raising `--sitting-max` alone leaves the time kill where it was. On 2026-10-08 the E-TRUNC
sitting was the campaign's SECOND (0051 had spent $4.86): the 16:28Z supervisor was started as on 10-07, without
`--kill`, and at 18:40:22Z campaign spend read $8.86 — about five minutes from a termination mid-FULL that nothing would
have drained. Replaced at 18:40:56Z with `--kill 18` (the authorized cap); the second restart then printed `TTL 7.0h`
and needed `--ttl 8.1` beside `--sitting-max 14.5`. Rules: (1) start the supervisor with `--kill <campaign cap>` and
`--ttl <ceiling ÷ $/h>` written out, every sitting; (2) read the watchdog's first status line (`sitting kill $, account
kill $, TTL h`) back before trusting it; (3) a stale watchdog under `caffeinate -dimsu` survived SIGTERM here — kill by
pid with -9 and confirm with a bracketed `pgrep`.
basis: `tools/runpod/rp.py` (`--kill` default 9.0; `if sit >= limit or camp >= a.kill: return _terminate_until_gone(...)`;
  `ttl = a.ttl if a.ttl is not None else st.get("hours")`); runbook `docs/2026-10-04-e-trunc-gpu-runbook.md` §6 entries
  18:40 and 18:43–18:45 (spend readings, the three restarts, the `TTL 7.0h` line).
re-verify: grep -n 'add_argument("--kill"' tools/runpod/rp.py; grep -n "camp >= a.kill\|ttl = a.ttl if a.ttl is not None else st.get" tools/runpod/rp.py   # default=9.0; both lines present
