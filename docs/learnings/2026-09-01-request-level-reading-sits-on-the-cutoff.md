# Under a request-level reading of "input-token spend", H-E7a's upper-bound ratio is 10.0012%

kills: (nothing)
ts: 2026-09-01T23:57:13Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling track-b (session_01RRk8euGRszMDP4z12wDdJz)
status: verified
fact: The registered H-E7a denominator (0015/0018) prices every assistant turn as a request
that re-bills the trajectory's whole visible prefix: 244,739,122 tokens, ratio 0.20%. Reading
"input-token spend" as what each LLM call was actually billed (entry 0017's `paid`, applied to
all 444 composio requests) gives 4,967,377 tokens, and the unchanged numerator 496,798 then
sits at 10.0012% of it, on the 10% cutoff. Warm bounds: 1.82% (registered) and 8.60%
(request-level; only 7.6% of request-level prefill is a byte-identical prefix of the preceding
request, and write_mult 1.25 makes warm exceed cold). The numerator is an upper bound (0010)
and every denominator a visible-only lower bound (0012), so the true request-level ratio is
strictly below the stated figure. Entry 0024 records all four readings and changes no cell;
choosing the reading is a registration act for a successor to 0006/0014.
basis: `summarize_e7 --cache-aware-ratio` printed
  `| **pooled** (60 trajs) | 496,798 | 244,739,122 -> **0.20%** (below) | 27,354,947 -> **1.82%** (below) | 4,967,377 -> **10.00%** (AT OR ABOVE) | 5,775,842 -> **8.60%** (below) |`
  and an independent second walk of the corpus printed
  `numerator 496797.93 request-level cold 4967377 ratio 0.100012 requests 444` with
  `switch rows 68 ... paid sum headroom 557863 paid sum request-level 557863 mismatching rows 0`.
re-verify: grep -c '10\.0012%' ledger/ledger.md   # 3: entry 0024 states it three times
