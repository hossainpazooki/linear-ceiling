# One trace family, two shapes; and a trajectory prefix is not a request's prefill

kills: (nothing; the switching claim of 2026-09-01-one-trace-family-does-switch-models.md stands -- what falls are the headroom FIGURES of ledger 0013 and the H-E7a ratio of 0015, superseded by ledger 0017)
ts: 2026-09-02T00:40:00Z
commit: 9e755a1 (state the defect was found in; fix uncommitted at write time)
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: The two composio_swekit submissions share a family but not a shape. `20241016` lists
LangChain message nodes directly inside each sub-run; `20241025` nests each sub-run's entire
prompt as ONE LIST node ahead of the `LLMResult` (30 of its 30 files; 1 of 30 in the other). An
adapter that iterates a sub-run and skips non-dict nodes reads the nested shape as seven responses
per file and no prompt: 30 files contributed no prompt tokens to anything. Separately, the headroom
measure's `paid` summed every message before the receiving turn -- three Claude solve threads plus
the o1-mini prompt -- when the o1-mini call was billed for its own prompt only, about one sixth of
that. Both were invisible in the aggregates: the adapter still found 60/60 switches, the
summarizer reproduced the driver exactly (it shared the defect), and the H-E7a verdict was the
same either way. What exposed them was a NEW measurement on the same objects: tokenizing S and R
for E9 gave a receiver prompt of median 685 tokens against a 16,675-token sender context, which
cannot be "the transcript re-rendered". Corrected (recon, fixed instrument): composio input tokens
244.7M not 166.0M; receiver prefill median 7,492 not 19,972; overlap of the ACTUAL prompt 0.988
not 0.903; H-E7a 0.20% not 1.41%. Two rules follow. A family adapter must pin every SHAPE it
accepts with a fixture, not just every key it detects (0010's detector-breadth rule was
necessary, not sufficient). And a fail-closed summarizer that shares the adapter with the driver
proves the arithmetic, not the reading: cross-checking a number against an INDEPENDENT view of
the same object (here, a token count of the very text the measure claimed to price) is what
catches a shared misreading.
basis: `python - <<'PY'` over `traces/swe-bench/2024102{5,16}_composio_swekit/*.json`: files whose
  every sub-run has exactly 2 nodes with a LIST first = 30/30 (20241025) and 1/30 (20241016);
  first list node of `astropy__astropy-12907_traj.json` (20241025) = 34 messages
  `system, human, ai, tool, ...` with `id[-1] == "SystemMessage"` etc.; the old adapter's output for
  that file = 7 messages, all `assistant`. Recon after the fix: `summarize_e7` composio row
  `60 | 6377 | 244739122`, headroom `paid ... 7,492`, `overlap ... 0.988`, ratio `0.20%`.
re-verify: .venv/Scripts/python.exe -c "import json,glob; fs=sorted(glob.glob('traces/swe-bench/20241025_composio_swekit/*.json')); n=sum(all(len(s)==2 and isinstance(s[0],list) for s in json.load(open(f,encoding='utf-8'))) for f in fs); print(n, 'of', len(fs), 'files nest the prompt as a list')"
