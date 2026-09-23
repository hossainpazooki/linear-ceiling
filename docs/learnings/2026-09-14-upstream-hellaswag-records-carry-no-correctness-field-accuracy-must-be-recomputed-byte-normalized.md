# The upstream HellaSwag records carry no correctness field: acc_norm must be recomputed as the byte-normalized argmax, which reproduces the 0.856 retention the paper borrows

kills: (nothing)
ts: 2026-09-14T09:27:57.070Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: Rows of `../kv-transfer-replication/results/hellaswag/qwen3-0.6b-to-1.7b/*.jsonl` hold only `idx`, `gold`, `logprobs` and
`nbytes`. Anyone re-verifying the replication's downstream figures from raw records must compute acc_norm as
argmax over the four endings of logprobs / nbytes, compared with gold. Done that way, mapped-k1 scores 0.548 and native
0.598, a floor-normalized retention (acc − 0.25) / (native − 0.25) of 0.8563, the figure an upstream-first introduction
quotes as 0.856. Upstream checkout at `063f402`; the upstream is read-only from this repo.
basis: `head -c 160 .../mapped-k1.jsonl` printed `{"idx": 27, "gold": 3, "logprobs": [-68.69337191130035, ...], "nbytes":
  [101, 45, 65, 58]}`; the recompute printed `mapped-k1 0.548 native 0.598 floor_norm 0.8563` (captured with the upstream
  at `063f402`).
re-verify: .venv/Scripts/python.exe -c "import json;L=lambda f:[json.loads(l) for l in open('../kv-transfer-replication/results/hellaswag/qwen3-0.6b-to-1.7b/'+f)];a=lambda R:sum(max(range(4),key=lambda j:x['logprobs'][j]/x['nbytes'][j])==x['gold'] for x in R)/len(R);m,n=a(L('mapped-k1.jsonl')),a(L('native.jsonl'));print(m,n,round((m-0.25)/(n-0.25),4))"   # 0.548 0.598 0.8563
