# `hf download` of the e9f mirror dies on Windows MAX_PATH under a ~/dev-length root; an 8-character root works

ts: 2026-10-01T04:47:32Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `hf download emmmy/linear-ceiling-e9f-2026-09-19 --repo-type dataset --local-dir ~/dev/lc-mirror/e9f` failed with
`FileNotFoundError` on the downloader's temp file
`…\e9f\.cache\huggingface\download\results\e9f\scratch\<handoff>\cross_src\<base64>.<sha256>.<hex>.incomplete`: the
`.cache/huggingface/download/` prefix plus the base64-sha-suffix temp name add about 120 characters to the kept-dump
path, which pushes a 31-character root past 260. The same pull completed at `C:\m\e9f` (root 8 characters; longest
final path 146 characters) and verified. The e8f dataset, whose paths are shorter, completed under the long root.
`LongPathsEnabled` was not changed. Same family as the 09-28 learning in operator memory about deep venv installs.
basis: at 0a51275, 2026-10-01T04:47:32Z, `find /c/m/e9f -type f | awk '{ if (length>m) m=length } END{print m}'`
  printed 146, and the first pull's log (`mirror-pull.log`, 02:54Z) carried one `FileNotFoundError` on the
  `.incomplete` path quoted above, ending `e9f exit=1`; the restarted pull at `C:\m\e9f` ended `e9f exit=0`, 52 GB,
  1,054 files, and `tools/hf_verify_backup.py` printed `BACKUP VERIFIED`.
re-verify: find /c/m/e9f -type f -not -path "*/.cache/*" | wc -l   # expect 1054 (the dataset's files including .gitattributes) on this machine; absent elsewhere
