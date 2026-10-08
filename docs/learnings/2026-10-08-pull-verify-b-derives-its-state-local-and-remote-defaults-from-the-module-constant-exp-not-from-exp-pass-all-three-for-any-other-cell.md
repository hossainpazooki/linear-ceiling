# pull_verify_b.py derives its --state, --local and --remote-results defaults from the module constant EXP = "e9f", not from --exp: pass all three for any other cell

ts: 2026-10-08T01:37:00Z
commit: 8696e83
session: llama-long-cell-0051-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The home puller's argparse defaults are f-strings over the module constant `EXP = "e9f"`, evaluated at import time:
`--config config/e9f.toml`, `--local results/e9f`, `--remote-results /workspace/linear-ceiling/results/e9f`, `--state
~/.cache/linear-ceiling/runpod-e9f-pull.json`. Passing `--exp e9fl` changes the exp recorded in the state but none of those
paths, so the 0051 sitting's first puller start opened the short cell's state file and refused ("pull state pod_id belongs
to another sitting") — and, had the state matched, it would have mirrored the pod's `results/e9fl` into the home
`results/e9f`. The puller for any cell other than e9f is started with `--exp --pair --config --local --remote-results
--state --expected-pod-name` all explicit. The same shape exists in `append_0051.py`'s absence of a `--dataset` argument
until this sitting: a script written for one cell carries that cell's constants in places its flags do not reach.
basis: `tools/runpod/pull_verify_b.py` lines 43–45 (constants) and 1026–1034 (defaults); runbook
  `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6 17:16 entry; the working command in its 17:40 entry.
re-verify: grep -n -E 'default=f"(config|results|/workspace/linear-ceiling/results)/\{EXP\}|runpod-\{EXP\}-pull' tools/runpod/pull_verify_b.py   # four defaults bound to the constant, not the flag
