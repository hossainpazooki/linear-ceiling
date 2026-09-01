# Prefix repetition reweights tokenizer bias, so aggregate agreement can be coincidence

ts: 2026-09-01T06:05:04Z
commit: 62282e9
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: A chars/4 token estimator is differentially biased by content type — measured against
`o200k_base`: tool output 2.890 chars/token (-27.8%), tool-call args 3.467 (-13.3%), assistant
prose 4.005 (+0.1%), user prose 4.322 (+8.0%), system prompt 4.817 (+20.4%), corpus-wide 3.723
(-6.9%). Switching to the registered counter moved totals only +1.6%, not the +7.4% the
corpus-wide figure predicts, because COST totals bill the PREFIX once per request: the system
prompt is 50.4% of billed characters versus ~34% of raw corpus text, and its +20.4% overcount
nearly cancels tool output's -27.8% undercount. So the two estimators agreeing in aggregate is
an artifact of this corpus's prefix weighting, NOT evidence the crude estimator is safe — and
the cancellation will not transfer to a suite with a different system-prompt share. Generally:
when a quantity re-bills earlier tokens, validate an estimator against the WEIGHTED
composition the quantity actually sees, never against the raw corpus.
basis: prediction from prefix-weighted shares reproduces the observation exactly —
  `prefix-weighted predicted exact/chars4: +1.6%` against an observed +1.6% overall shift,
  while `raw-corpus predicted (chars/token 3.723): +7.4%`. Ratio sensitivity measured
  alongside: warm/cold moved 19.27% -> 20.01% (+0.74pp, 3.8% relative).
re-verify: .venv/Scripts/python.exe -c "share={'system':0.504,'tool_output':0.266,'assistant':0.168,'user':0.037,'tool_args':0.024}; div={'system':4.817,'tool_output':2.890,'assistant':4.005,'user':4.322,'tool_args':3.467}; print(round(100*(4*sum(share[k]/div[k] for k in share)-1),1))"
