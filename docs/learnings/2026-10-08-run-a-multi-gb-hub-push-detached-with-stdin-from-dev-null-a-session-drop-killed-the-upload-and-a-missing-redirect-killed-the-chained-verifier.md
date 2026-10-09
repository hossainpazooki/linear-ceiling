# Run a multi-GB Hub push detached with stdin from /dev/null: a session drop killed the upload, and a missing redirect killed the chained verifier at interpreter start

ts: 2026-10-08T01:38:00Z
commit: 8696e83
session: llama-long-cell-0051-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: Three failures of one shape in the 0051 R8 push, none of them the data's. (1) `hf upload-large-folder` ran as a child of
the operator's interactive ssh session into the Mac; the home internet connection dropped, the router reset every TCP
session, and the upload died with its parent (resumable — 50 files were already committed and the per-file metadata
under `.cache/huggingface/` survived, so the restart re-hashed nothing). (2) The restart was `nohup env HF_TOKEN=… bash -c
'hf upload-large-folder … && python tools/hf_verify_backup.py …' > log 2>&1 &` WITHOUT `< /dev/null`; the upload
completed (571/571, 47.7 GB) and the chained verifier then died with `Fatal Python error: init_sys_streams … Bad file
descriptor` because its inherited stdin was the by-then-closed terminal. (3) A `read -s` token prompt pasted as part of a
multi-line block consumed the NEXT pasted line as the token, and the block ran twice, giving two concurrent upload chains
on one folder (the younger was killed). Rules: every long-running push or verifier runs under `nohup … < /dev/null &`
(plus `caffeinate -i` on a Mac) with its own log; a `read -s` line is pasted alone; one chain per folder; and "Upload is
complete!" is not a backup — only the verifier's `BACKUP VERIFIED` is.
basis: `~/.cache/linear-ceiling/hf-upload.log` and `hf-verify.log` on the Mac (00:04:23Z "Upload is complete!" then the
  init_sys_streams traceback; 01:31Z `lfs-compared 398, downloaded+hashed 173, problems 0 / BACKUP VERIFIED`); runbook
  `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6 entries from 20:1x to 01:31Z.
re-verify: grep -c "init_sys_streams\|BACKUP VERIFIED\|ran \*\*twice\*\*" docs/2026-10-07-llama-long-cell-runpod-runbook.md   # 4 lines: §5's expected verdict, the double paste, the verifier's death, §6's verdict
