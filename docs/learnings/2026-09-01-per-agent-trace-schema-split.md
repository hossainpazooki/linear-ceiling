# tau-bench stores tool-call arguments as str for one agent and dict for another

ts: 2026-09-01T06:04:58Z
commit: 62282e9
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: In tau-bench's `historical_trajectories`, a tool call's `function.arguments` is a JSON
STRING for the gpt-4o files (4,438 calls) and a parsed DICT for the sonnet-35-new files (9,847
calls). A character-based token estimator handed the dict silently counts `len(dict)` — the
number of KEYS — so only one agent's counts are wrong. Measured impact: +1.5% input tokens for
sonnet-35-new, 0.0% for gpt-4o. Small in aggregate but ASYMMETRIC BY AGENT, which is the
damaging shape: it biases exactly the cross-agent comparisons the corpus exists to support,
while the aggregate looks fine. The general lesson is that a public trace corpus can be
internally heterogeneous per contributor, so a per-field type check belongs in the adapter
rather than trust in a single sampled file.
basis: over the four local trace files —
  `gpt-4o-airline.json {'str': 1164}` · `gpt-4o-retail.json {'str': 3274}` ·
  `sonnet-35-new-airline.json {'dict': 2761}` · `sonnet-35-new-retail.json {'dict': 7086}`
  (requires `traces/tau-bench/` locally; the files are gitignored). Normalization to compact
  JSON is justified by the sibling agent's own wire format in the same suite:
  `{"user_id":"mia_li_3668"}` is 25 chars, byte-equal to `json.dumps(separators=(",",":"))`.
re-verify: .venv/Scripts/python.exe -m pytest tests/test_e7_traces.py -k "dict_and_str or dict_is_serialized" -q
