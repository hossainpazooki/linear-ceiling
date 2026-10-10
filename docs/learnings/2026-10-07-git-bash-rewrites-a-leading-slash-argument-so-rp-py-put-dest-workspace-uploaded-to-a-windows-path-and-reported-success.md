# Git Bash rewrites a leading-slash argument before Python sees it, so `rp.py put --dest /workspace/` uploaded to `C:/Program Files/Git/workspace/` and reported success

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: MSYS path conversion applies to every argument of a native executable that starts with `/`, including the venv's
`python.exe`. `tools/runpod/rp.py put <file> --dest /workspace/` therefore ran `scp … root@<ip>:C:/Program Files/Git/workspace/`;
`scp` wrote nothing useful on the pod, the call's exit code was masked by a `| tail`, and the setup script launched
against a tarball that did not exist. Nothing in the repo's tooling guards against this because it was written for a
Linux/macOS shell. Run every `rp.py` call from Git Bash under `MSYS_NO_PATHCONV=1`, and verify an upload on the pod
(`ls -l` + `sha256sum`), never by the local exit code.
basis: 2026-10-06 23:45:12Z first `put`: pod listing showed no `cb-inputs.tar.gz` anywhere (`find / -xdev -name …` empty);
  the second `put` of `cb-setup.sh` printed `scp: failed to upload file … to C:/Program Files/Git/workspace/`. Under
  `MSYS_NO_PATHCONV=1` both uploads landed: 317,991,348 B, sha `037855dde3cbc1ad…` on the pod. Runbook
  `docs/2026-10-06-cache-behavior-runpod-runbook.md` trap (h).
re-verify: .venv/Scripts/python.exe -c "import sys;print(sys.argv[1])" /workspace/   # prints C:/Program Files/Git/workspace/ from Git Bash; prints /workspace/ with MSYS_NO_PATHCONV=1 set
