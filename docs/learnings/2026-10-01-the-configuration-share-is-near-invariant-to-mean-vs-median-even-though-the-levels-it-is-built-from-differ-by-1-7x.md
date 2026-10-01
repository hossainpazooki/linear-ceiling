# The configuration share is near-invariant to mean-vs-median (0.4285 vs 0.4577) even though the three far-from-seam levels it is built from differ by ~1.7× between the two statistics

kills: (nothing)
ts: 2026-10-01T04:53:01Z
commit: bf75008b95990237c84906d4f9bfeecb7f2ec870
session: e9l-aws-run (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl)
status: verified
fact: Entry 0038 registers the configuration share (scaled − native) / (long − native) on the 16+ seam bin as
**0.4285**, computed from pooled **medians**. Because the pooled means run 1.6–1.8× the medians in every bin
([[2026-10-01-seam-bin-means-run-1-6-to-1-8-times-the-medians-the-ledger-reports]]), the obvious worry is that a
bin-mean restatement — which reviewer teFN's Corollary 3 objection forces — would move the share too. It does not:
recomputed on means the share is **0.4577**, a 0.029 shift, because all three levels rise together. The reading
("the configuration accounts for a bit under half the far-from-seam gap") survives the change of statistic. What
does **not** survive is any *absolute* margin stated without naming its statistic: the far-from-seam levels are
0.019497 / 0.038085 / 0.062873 by median and 0.070807 / 0.088973 / 0.110493 by mean, so a ±0.005 band is 13 % of
the scaled-short median but 5.6 % of its mean. Any registered band on these figures — E-TRUNC's pre-registered
reading is written against exactly them — must say "median" or "mean". The mean share is not on the ledger; 0038's
0.4285 is the registered number and the median is its statistic.
basis: at bf75008, 2026-10-01T04:53:01Z, reading the 16+ `seam_left_bins.same_K` row of `results/e9/tail.json`,
  `results/e9s/tail.json` and `results/e9l/tail.json` and recomputing the share printed:
  `median: native 0.019497 scaled 0.038085 long 0.062873 share 0.4285` and
  `mean: native 0.070807 scaled 0.088973 long 0.110493 share 0.4577`. The median share reproduces entry 0038's
  0.4285 to four places, which is what licenses the mean figure beside it. `results/` is gitignored: the re-verify
  line needs the home mirror or a pull of the public backups.
re-verify: .venv/Scripts/python.exe -c "import json;f=lambda c:[r for r in json.load(open('results/%s/tail.json'%c))['seam_left_bins']['same_K'] if r['bin']=='16+'][0];n,s,l=f('e9'),f('e9s'),f('e9l');print({k:round((s[k]-n[k])/(l[k]-n[k]),4) for k in ('median','mean')})"   # {'median': 0.4285, 'mean': 0.4577}
