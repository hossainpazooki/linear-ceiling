# A byte-compare against what current code draws settles provenance; timeline inference does not

kills: (nothing; corrects an operational ruling from the session transcript, not a ledger entry)
ts: 2026-09-01T22:10:26Z
commit: 151bb719e05231fdd12fc8766b1668c427655d5c
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: Two E8 runs produced R² identical to four decimals, which was read (from launch-time
inference) as "the rerun reused the defective adapter's sample — not on the record, rerun
required." The inference was wrong: both runs had used the FIXED adapter, because the operator
committed the fix before executing. What settled it was not reconstructing the timeline but
recomputing the artifact from current code and comparing bytes: the on-disk arm (b) token
matrix equals what the current sampler draws, sha-for-sha, so the sample on disk is the
current code's sample and the identical R² across two independent end-to-end executions is a
determinism check, not staleness. General rule: when "which code produced this file?" matters,
derive the file again from the code in question and compare bytes; process-start times,
message ordering, and commit timestamps are all weaker evidence than a hash equality, and in
this case they pointed the wrong way.
basis: recomputed the draw from HEAD 151bb719 and compared to disk (2026-09-01T22:10:26Z):
  `recomputed sha256: 2355cef5d891b329 | on-disk sha256: 2355cef5d891b329 | equal: True`
  (tokens file data/e8/agent_n50_len1024_seed8.npy; sampler = e8_text.sample_windows over
  iter_trace_texts with the registered seed 8).
re-verify: .venv/Scripts/python.exe -c "import hashlib,numpy as np; from linear_ceiling import REPO_ROOT; from linear_ceiling.config import load_e7_config, load_e8_config; from linear_ceiling.e8_text import iter_trace_texts, qwen_encoder, sample_windows; from linear_ceiling.weights import snapshot; e7=load_e7_config(REPO_ROOT/'config/e7.toml',REPO_ROOT); e8=load_e8_config(REPO_ROOT/'config/e8.toml',REPO_ROOT); tok,_=sample_windows(list(iter_trace_texts(e7,tuple(e8.text['suites']))),qwen_encoder(snapshot('Qwen/Qwen3-0.6B')),e8); import numpy; disk=numpy.load('data/e8/agent_n50_len1024_seed8.npy'); print('equal:', bool((tok==disk).all()))"
