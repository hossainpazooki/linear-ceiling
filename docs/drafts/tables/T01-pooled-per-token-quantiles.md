# T01 — Printing a pooled per-token p10/p90/p99 under a nearest-rank sentence

status: RULE (2026-10-10, operator ruling; replaces the withdrawn ledger draft 0061)
sources: 0038:2357 (scaled − native p10/p90/p99; `results/e9s/compare.json` key `pooled_token_diff`); 0045:3011–3090 (each
  cell's pooled p90/p99; `results/<cell>/tail.json` key `pooled.<arm>`); 0006:267 (an interpolated p90 already on the
  record); 0013:740–742 (the over-handoff convention); `src/linear_ceiling/e9_compare.py`, `e9_tail.py` (`np.quantile`)
conventions: quantiles over handoffs = `e7_stats.quantile`, lower nearest-rank, `sorted[min(floor(p·n), n−1)]`; pooled
  per-token quantiles = `np.quantile`, linear interpolation (numpy default); medians agree under both
re-verify: grep -c "np.quantile" src/linear_ceiling/e9_tail.py src/linear_ceiling/e9_compare.py; sed -n 267p ledger/ledger.md | grep -c interpolation; sed -n 741,742p ledger/ledger.md | grep -c nearest-rank   # e9_tail 2, e9_compare 3; 1; 1

The MLSys draft plan (`docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md`) prints no pooled per-token
quantile. The September outlines did ("pooled token p90 0.2305, p99 0.6736"; "p90 0.2856, p99 0.7600"); those sentences
are the kind this rule governs. If a table or sentence ever prints one, it is required that:

1. The figure is read from its summary file at the printed precision, never retyped from the entry.
2. The caption or the quantile sentence states both conventions in words: quantiles over handoffs are lower nearest-rank
   (`e7_stats`, 0013); pooled per-token quantiles are linearly interpolated (numpy default). A single "quantiles are
   nearest-rank" sentence over a table that holds one of these is false by up to one unit in the fourth decimal: the
   largest gap over the 11 such figures on the record is 0.0001001, computed 2026-10-10 by the withdrawn 0061 preview
   from the pinned `scores/` + `tokens/` records (a scratch figure, not a registered one; recompute it before printing it).
3. If the convention sentence is cited to the ledger, cite 0006:267 and 0013:740, not a claim of one convention. No
   ledger entry exists or is needed for this: the summarizers' printed values are the readings, and nothing moves.
4. The skeptic pass recomputes the printed value with `np.quantile` from the records and the nearest-rank value beside
   it, and the approval note records both.
