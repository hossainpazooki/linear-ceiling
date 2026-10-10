# `rp.py pull --force-tar` on Windows extracted into `C:\c\Users\…`, so results come home as one on-pod tarball by `scp`, opened with `/usr/bin/tar`

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `cmd_pull`'s tar-over-ssh fallback pipes the remote stream into a local `tar -xzf - -C <local>`. With `<local>` given
as a POSIX path (`/c/Users/hossa/dev/linear-ceiling/results/`), the `tar` Python resolved on this machine created
`C:\c\Users\hossa\dev\linear-ceiling\results\cache-behavior\` and left `results/cache-behavior/` untouched; three
"successful" pulls over 20 minutes brought nothing home, and the pod billed idle for ~12 minutes after the driver had
finished before the gap was noticed. The reliable path on Windows is: `tar -czf` ONE archive on the pod with its
`sha256sum`, `scp` it, compare the sha, then extract with `/usr/bin/tar` named explicitly.
basis: 2026-10-07 01:09–01:30Z puller log: three `pull: rsync unavailable on the pod; falling back to tar-over-ssh` lines,
  then `FileNotFoundError: … results\cache-behavior\report.json`; `ls /c/c/Users/hossa/dev/linear-ceiling/results/cache-behavior`
  listed 38 files (partial). The tarball route: 332,507,779 B, sha `3339e1b3…` equal on the pod and at home, 73 files
  extracted, 35/35 fingerprints matched `report.json`. Stray tree deleted. Runbook trap (j).
re-verify: grep -n '"tar", "-xzf", "-", "-C"' tools/runpod/rp.py   # the local tar invocation that misplaced the extraction (one hit, in cmd_pull)
