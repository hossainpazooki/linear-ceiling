# A ruling default that names a cell presupposes an instrument: the mixed-RoPE L32-native cell has no dump path

ts: 2026-10-04T09:50:00Z
commit: a2742b9
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: Ruling 3's default ("include the L32-native cell, keep R under YaRN") describes a handoff whose sender dumps are made under the native RoPE and whose receiver dump is made under YaRN. `e9.dump_handoff` passes one `rope_args(cfg)` to all three dumps of a handoff and `run_controls` to the prefix dump, and `summarize_e9._check_rope_meta` refuses two "target" dumps whose spec differs — so the cell cannot be run or read by the instrument as it exists. A secondary fact that changes the alternative: every receiver prompt of the 35 long handoffs fits the native window (max |R| 25,073), so a both-arms-native cell needs no driver change but is 0037/0038's comparison on different texts, not the one-thing-changed comparison the ruling wanted. The registration quotes the ruling and defers the cell to its own pre-prefill amendment.
basis: `src/linear_ceiling/e9.py` lines 206–218 and 307–309 (one `rope_args` per run); `summarize_e9.py` `_ROPE_IDENTITY_FIELDS` / `_check_rope_meta` (per-role equality); `results/e9l/align/coverage.json` n_receiver over the included 35.
re-verify: grep -c 'rope_args(cfg)' src/linear_ceiling/e9.py   # expect 3 (handoff dumps, bridge's scaled arm, prefix control); and: .venv/Scripts/python.exe -c "import json; d=json.load(open('results/e9l/align/coverage.json')); print(max(a['n_receiver'] for a in d['alignments'] if not a['excluded']))"   # expect 25073
