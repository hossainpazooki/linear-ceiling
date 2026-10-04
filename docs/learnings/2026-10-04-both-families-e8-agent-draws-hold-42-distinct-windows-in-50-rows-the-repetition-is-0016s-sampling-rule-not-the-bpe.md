# Both families' E8 agent draws hold 42 distinct windows in 50 rows; the repetition is 0016's sampling rule, not the Llama BPE

ts: 2026-10-04T09:24:16Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: Entry 0040 disclosed that the Llama arm (b) draw holds 42 distinct windows in 50 rows, one window 9 times, and read it as a
property of that pair's draw. The Qwen token file drawn under the same rule (`data/e8/agent_n50_len1024_seed8.npy`, entry 0020's) has
the same counts: 42 distinct rows, maximum multiplicity 9. The repetition therefore comes from entry 0016's sampling rule on these
suites (one window per trajectory, "first" window, trajectories that share an identical opening), not from the Llama-3 tokenizer.
Entry 0031's all-sequence bootstrap on Qwen resampled rows with that multiplicity without saying so; 0052/0053 say so for Llama.
A de-duplicated rerun on either family would be a future amendment, not a correction of any figure.
basis: at 0c5ec15, 2026-10-04T09:24:16Z, `np.unique(np.load(f), axis=0, return_counts=True)` printed
  `data/e8/agent_n50_len1024_seed8.npy (50, 1024) distinct 42 max multiplicity 9` and
  `data/e8f/agent_n50_len1024_seed8.npy (50, 1024) distinct 42 max multiplicity 9` (first observed 07:2xZ at 8e53eac, re-captured here).
re-verify: .venv/Scripts/python.exe -c "import numpy as np;print([len(np.unique(np.load(f),axis=0)) for f in ('data/e8/agent_n50_len1024_seed8.npy','data/e8f/agent_n50_len1024_seed8.npy')])"   # expect [42, 42] (local data tree)
