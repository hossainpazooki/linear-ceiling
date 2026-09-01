# Public agent traces omit the system prompt and tool schemas — the most cacheable ~3,240 tokens per request

ts: 2026-09-01T06:45:42Z
commit: 8b0938a
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: tau2-bench records provider-reported `usage.prompt_tokens` per message, which allows a
token estimator to be validated against GROUND TRUTH rather than against another estimator.
Doing so shows the estimator is sound and the TRACE is incomplete. Split by which model made
the request: for **user-simulator** calls, whose prefix is fully visible in the trace, reported
minus estimated is **-134 tokens** (ratio 0.87) -- close agreement, so the counting pipeline is
right. For **agent** calls, reported minus estimated is **+3,423 tokens** (p10 +3,239, p90
+5,962), and the offset is nearly flat across turn depth (+3,238 at the first assistant turn,
+3,264 at turns 2-3, +3,382 at 4-8, +3,609 at 9+). A near-constant additive gap that does not
grow with conversation length is a FIXED HIDDEN PREFIX -- the domain policy system prompt plus
tool schemas -- that the provider billed and the trace does not record. Consequence for anyone
computing agent cache economics from public traces: the hidden block is both large (~3,240
tokens per agent request, roughly 42k per trajectory at the median turn count) and exactly the
most cacheable content, since it is byte-identical on every request. Omitting it understates
total prefill spend AND understates the benefit of caching, biasing cache-savings analysis
downward in a way no amount of care with the visible messages can correct. Any cost figure
derived from trace messages alone must state this floor.
basis: over 4 tau2-bench airline result files (800 simulations, 4 agent models), comparing each
  message's reported `usage.prompt_tokens` against the cumulative estimated prefix preceding it
  -- `role=assistant  n=  8914  offset median=   3,423 p10=   3,239 p90=   5,962   ratio
  median=4.14` and `role=user       n=  5158  offset median=    -134 p10=  -2,489 p90=     462
  ratio median=0.87`; by turn position `assistant turns 1-1: n=800 offset median=3,238`,
  `2-3: n=1595 offset median=3,264`, `4-8: n=3549 offset median=3,382`, `9-+: n=2970 offset
  median=3,609`. A first pass pooled both roles into one series and produced an uninterpretable
  ratio of 3.3; separating by requesting model is what made it legible -- pooling two models'
  billing into one accounting series was my error, not the data's.
re-verify: .venv/Scripts/python.exe -m pytest tests/test_e7_tau2.py -q
