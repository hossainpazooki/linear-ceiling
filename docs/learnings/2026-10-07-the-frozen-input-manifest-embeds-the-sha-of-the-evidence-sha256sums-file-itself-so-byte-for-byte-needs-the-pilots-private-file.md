# The frozen input manifest embeds the sha of the evidence `SHA256SUMS` file itself, so 0047's "byte-for-byte" clause needs the pilot author's private file, not just the same inputs

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `prepare()` writes `"evidence_sha256_manifest": digest(args.evidence_sha256)` — the sha256 of the SHA256SUMS *file*
passed on the command line — into `inputs/manifest.json`, and `append_0049.py` asserts that manifest's sha equals the
frozen `9a6f2923…`. Every other field is reproducible from the repository and the verified e9l mirror (config, corpus
manifest, archive config and report, 35 record shas once prepared on Unix), but that one field depends on the exact
bytes of a file that lives only on the pilot author's machine. A regenerated SHA256SUMS over the same 208 files, in 192
plausible `sha256sum` layouts, never reproduced the frozen hash. 0047's sentence "the operator's `--prepare` must
reproduce it byte-for-byte" cannot be satisfied without that file or a corrective reading; the run itself is unaffected.
basis: 2026-10-07 ~00:10Z: `manifest sha256 f403dea7…` (Windows) and `2aeee576…` (WSL) vs frozen `9a6f2923…`; the four
  pinned digests equal the freeze record (`config_sha256 == freeze: True`, corpus `371fb4bf…`, archive config `bab1afca…`,
  report `084d9480…`); brute force `candidates tried: 192 hits: 0` with `write()` reproducing the manifest bytes exactly
  (`write() reproduces manifest bytes: True`). `freeze.json` carries no evidence-file digest.
re-verify: grep -n '"evidence_sha256_manifest": digest(args.evidence_sha256)' tools/cache_behavior/run.py   # one hit: the field that pins the pilot's private file
