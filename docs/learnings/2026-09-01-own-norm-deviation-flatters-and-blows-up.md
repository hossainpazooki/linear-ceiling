# A per-token deviation relative to the token's own norm flatters the record and blows up on small-norm tokens

kills: (nothing)
ts: 2026-09-01T23:41:01Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: Normalizing a per-token KV error by the token's own uncentered norm, ||d||^2 / ||x||^2,
does not bridge to R^2 and reads far better than the variance it fails to explain: on the
archived k=1 held-out set the K own-norm mean is 0.084 while 1 - R^2 is 0.308, because the
uncentered norm is dominated by the per-head mean vector. It also has a fat tail from
small-norm tokens: the smallest per-layer V reference norm is 0.35% of the layer median, 0.66%
of V tokens exceed 1 (max 5.8). Scaling by the layer-head's centered SST/n instead makes the
token mean equal 1 - R^2 to 1e-11, so the per-token record and the recorded R^2 are one
quantity in two views; the own-norm form survives only as a labelled diagnostic.
basis: `summarize_e9 --calibrate-tau` output written to `results/e9/calibration/tau.json` at
  commit f48b536 (pre-dates the entry-0023 commits): K `own_norm_delta.mean 0.08365`, `tau
  0.31864` (= 1 - 0.68136); V `own_norm_delta.frac_gt_1 0.006640625`, `max 5.8279`,
  `min_ref_norm_over_layer_median 0.00346`; `bridge_check_max_abs` 1.2e-11.
re-verify: .venv/Scripts/python.exe -c "import json;t=json.load(open('results/e9/calibration/tau.json'));print(t['bridge_check_max_abs'],{k:(t['diagnostics'][k]['own_norm_delta']['mean'],t['diagnostics'][k]['tau'],t['diagnostics'][k]['own_norm_delta']['frac_gt_1']) for k in 'KV'})"
