# `env VAR=secret cmd` in a detached command line puts the secret into argv: use a shell environment prefix or the script's tty prompt

ts: 2026-10-09T01:15:00Z
commit: b33c6ce
session: e-trunc-0057-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The R8 push for the E-TRUNC datasets was launched on the Mac as `nohup caffeinate -i env ALLOW_PUBLIC=1
HF_TOKEN=$HF_TOKEN bash tools/hf_backup.sh … < /dev/null &`. `env NAME=value` receives the assignment as an ARGUMENT, so the
expanded token sat in the argv of `env` (and of `caffeinate`, which re-executes its command) for the life of the upload,
visible to `ps` on the machine — and it was captured into the assistant session's transcript the moment the process list
was read to confirm the push. `tools/hf_backup.sh` itself never does this: it reads the token from the environment or from
`/dev/tty` and never passes it as a flag (R9). The operator accepted the local exposure for the day and the token is revoked
after `BACKUP VERIFIED`. Rules: (1) a detached secret goes in the ENVIRONMENT, not the command line — `HF_TOKEN=$HF_TOKEN
nohup caffeinate -i bash tools/hf_backup.sh …` (a shell assignment prefix is applied by the shell and never appears in any
process's argv) or let the script prompt; (2) never confirm a running secret-bearing job with an unfiltered `ps` / `pgrep -fl`
— filter the token shape out before the output reaches a transcript; (3) R9's "revoked once pasted anywhere" includes a
process list.
basis: runbook `docs/2026-10-04-e-trunc-gpu-runbook.md` §7 ("R9 slip, stated"); `tools/hf_backup.sh` header lines 8–20 and
  its `read -rs HF_TOKEN <&3` prompt path; the 2026-10-09 01:11Z process listing (not reproduced anywhere).
re-verify: grep -n "R9 slip, stated" docs/2026-10-04-e-trunc-gpu-runbook.md | cut -c1-60; grep -c "never passed as a flag" tools/hf_backup.sh   # one line; 1
