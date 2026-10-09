# Stage a gated weight cache with the consumer's exact allow_patterns: huggingface_hub 1.33 refuses an offline snapshot that lacks any file the patterns match

ts: 2026-10-08T01:35:00Z
commit: 8696e83
session: llama-long-cell-0051-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `linear_ceiling.weights.snapshot` resolves a model with `snapshot_download(model_id, allow_patterns=["*.safetensors",
"*.json"])`. Under `HF_HUB_OFFLINE=1`, huggingface_hub 1.33 checks the cached snapshot against the repo's file listing FOR
THOSE PATTERNS and raises `IncompleteSnapshotError` if any matching file is absent. The 0051 sitting staged both Llama
snapshots at home with `ignore_patterns=["original/*"]` to skip the 16 GB PyTorch duplicates — which also dropped
`original/params.json`, a ~200 B JSON that `*.json` matches — so the box's `--align-only` refused after the 18 GB archive
was already uploaded and extracted, ~7 billed minutes in. The launcher's own `cache_complete` check (config, tokenizer, one
safetensors present) is weaker than the consumer's and passed. Fix was a 6-file delta (two `params.json`, two blobs, two
lock files) and a completeness proof with the consumer's own call before relaunching. Rule: a staging script downloads
with the SAME `allow_patterns` the consumer will ask for (exclude by extension — `original/*.pth`, `*.model` — never a
whole directory that holds a matching file), and the pre-flight proves completeness with that call offline.
basis: pod log `results/e9fl/logs/box/sitting_b.setup.log` (17:16:43Z traceback, 17:27Z pass) mirrored on the Mac; runbook
  `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6 17:09–17:28 entries; `src/linear_ceiling/weights.py` line 69.
re-verify: grep -n 'allow_patterns=\["\*.safetensors", "\*.json"\]' src/linear_ceiling/weights.py   # the consumer's patterns; original/params.json matches the second
