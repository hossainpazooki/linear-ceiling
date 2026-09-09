# A parallel session's status report is stale by the time it is read: verify it against the tree, not against itself

kills: (nothing)
ts: 2026-09-09T03:57:39.917Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: The box session's end-of-day report, pasted into this session on 2026-09-08 evening, listed the
R8 backup of the n = 420 pair as "still to do ... needs a Hub write token from you; I have none". By
the time this session read the runbook for a README section, its §6 recorded the backup done by the
operator from a staged copy of the mirror, 89/89 files verified in both directions, with a new reusable
verifier at `tools/hf_verify_backup.py`. The report was true when written and false when read, and a
README written from the report would have said the backup was pending. Two sessions on one repo means
every status sentence is dated the moment it is emitted; the pick-up discipline (read the tree, run the
re-verify line) applies to a sibling session's report exactly as it applies to a handoff brief.
basis: the pasted report's line `4. HF backup of the n=420 pair and the tagged mapper (R8). This needs a Hub write
  token from you in the environment; I have none.` (session transcript, 2026-09-08 ~20:00 local) vs
  `grep -n "^## 6. Backup\|89/89 OK" docs/2026-09-08-n420-target-dump-runbook.md` at 4eafe40 ->
  `227:## 6. Backup (R8), 2026-09-09` / `237:  downloaded and hashed, both directions checked — 89/89 OK.`
re-verify: grep -c "89/89 OK" docs/2026-09-08-n420-target-dump-runbook.md && test -f tools/hf_verify_backup.py && echo verifier-present   # 1, verifier-present
