# `hf upload-large-folder` with four workers sat at zero bytes for twelve minutes while the same endpoint answered a fresh process in 0.4 s; one worker finished 48 GB in twelve minutes

kills: (nothing)
ts: 2026-09-04T20:03:55Z
commit: 0a19b56ee3bd4b45eca28f84a20cf6ded4dcd436
session: algoverse-gpu-run-session (8a0fb97e-0020-43aa-a9b2-9ae67eec2fe3)
status: verified
fact: Backing the 720-file, 48.2 GB keep subset up to a private Xet dataset from the Windows home
machine with `hf upload-large-folder ... --num-workers 4` (huggingface_hub 1.28.0, hf-xet 1.6.0)
hashed every file and then made no progress: `pre-uploaded: 0/696` for twelve minutes while its
workers logged 53 `WinError 10060` timeouts on `POST .../preupload/main`, six of them terminal
(`Retry 5/5`). A plain requests.post to that URL from a fresh interpreter returned HTTP 200 in
0.4 s three times in a row during the stall. Killing the process and rerunning the identical
command with `--num-workers 1` resumed from `.cache/huggingface/` and committed all 720 files by
20:15:54Z, in part because the failed attempts' Xet xorbs had already landed and deduplicated. The
tool's last status line said `committed: 536/720` beside "Upload is complete!"; the count that
matters is `dataset_info(files_metadata=True)` lfs.sha256 against the driver's fingerprints, which
gave 720/720. Earlier the same evening, two `hf upload` runs of the small binaries had failed with
`ConnectionError ... cas-server.xethub.hf.co` after about four minutes each.
basis: docs/probes/2026-09-04-hf-upload-large-folder-4workers.{out,err} (the stalled run's own
  output): last status `hashed 720/720 (48.2G/48.2G) | pre-uploaded: 0/696 (0.0/48.2G) | committed:
  0/720`; 109 stderr lines, 53 `WinError 10060`, 6 `Retry 5/5`; restart at 20:03:55Z with one
  worker, verify at 20:15:59Z: `hf verify done: 720/720 ok, 0 bad` (session hf.log).
re-verify: grep -c "WinError 10060" docs/probes/2026-09-04-hf-upload-large-folder-4workers.err
