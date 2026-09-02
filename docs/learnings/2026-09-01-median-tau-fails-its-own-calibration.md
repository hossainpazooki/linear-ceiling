# A threshold set at the median of a skewed per-token statistic fails its own calibration

kills: (nothing)
ts: 2026-09-01T23:19:25Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: The E9 amendment seed set tau at the MEDIAN of the k=1 mapper's own per-token deviation
and decided the verdict by the smallest fraction of tokens whose removal brings the MEAN of the
rest under tau. Because per-token squared errors are right-skewed (mean > median), the
instrument the threshold was calibrated on does not itself pass: the mapper's own oracle
recompute fraction under a median tau is 6.2% (K) / 5.1% (V) on the own-norm deviation and
7.3% / 6.2% on the centered one, against a HOLDS edge of 15%. Setting tau to the mean makes the
mapper's own fraction exactly 0 by construction and keeps the "no worse than the mapper"
meaning. General form: a mean-based repair criterion must be calibrated with a mean.
basis: recon script over the archived held-out dumps (2,560 tokens), run at commit f48b536
  (pre-dates the entry-0023 commits): `mapper_own_fstar_at_tau_median: 0.06171875` (K),
  `0.05078125` (V); `mapper_own_fstar_at_tau_mean: 0.0` both. Re-captured by the registered
  calibration at 23:41:01Z in `results/e9/calibration/tau.json` ->
  `"at_centered_median": 0.073046875` / `0.062109375`, `"at_tau_mean": 0.0` / `0.0`.
re-verify: .venv/Scripts/python.exe -c "import json;d=json.load(open('results/e9/calibration/tau.json'))['diagnostics'];print({k:d[k]['mapper_own_fstar'] for k in d})"
