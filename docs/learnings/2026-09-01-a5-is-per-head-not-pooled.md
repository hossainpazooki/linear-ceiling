# The upstream "pooled R² (A5)" is per-head A5 averaged over heads; pooling a layer's heads gives a different number

kills: (nothing)
ts: 2026-09-01T23:31:52Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: Entries 0009/0016/0019 and UPSTREAM.md describe the transfer statistic as "pooled R²
(definition A5, pooled over rows and columns)". The code applies A5 per KV head
(`kvt.mapper.mapper_r2`, `score_positions.py`) and then averages heads and layers. Pooling a
whole layer's columns at once gives K 0.6917 / V 0.5267 on the same held-out set, against the
recorded head-averaged 0.6814 / 0.5133 -- a 0.01 gap that would have looked like drift the
first time anyone recomputed "pooled" R² literally. Entry 0023 records the distinction; any
bridge between a per-token record and the recorded R² must normalize per head.
basis: upstream `scripts/score_mapper.py --per-token` on the archived k=1 mapper and generic
  dumps at commit f48b536 (pre-dates the entry-0023 commits), scratch output cal_r2.json:
  `K_r2_heldout_layer_mean 0.68136`, `K_r2_heldout_pooled_over_heads_layer_mean 0.69168`;
  V `0.51329` vs `0.52665`. Re-captured in `results/e9/calibration/tau.json` at 23:41:01Z.
re-verify: .venv/Scripts/python.exe -c "import json;d=json.load(open('results/e9/calibration/tau.json'))['diagnostics'];print({k:(d[k]['head_averaged_r2_layer_mean'],d[k]['pooled_over_heads_r2_layer_mean']) for k in d})"
