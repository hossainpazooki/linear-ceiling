# Seam-bin MEANS of δ_K run 1.6–1.8× the medians the ledger reports, in every bin of the long cell

ts: 2026-10-01T04:47:29Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: Entries 0029 and 0036 report the seam profile as pooled MEDIANS per causal seam bin. The pooled MEANS, which a
bin-mean restatement of the workshop paper's Corollary 3 would feed (reviewer teFN's objection), are larger in every
bin on the long cell: bin 0 0.428 vs 0.260, bin 1 0.244 vs 0.153, 2–3 0.155 vs 0.089, 4–7 0.127 vs 0.074, 8–15 0.143
vs 0.086, 16+ 0.110 vs 0.063 (ratios 1.59–1.76). The far-from-seam floor by mean is 0.110, not 0.063. Neither
number is on the ledger as a mean yet; `e9_tail` computes them and the corrective entry draft states them. Unit:
share of unexplained variance in R²'s units, never a percent.
basis: at 0a51275, 2026-10-01T04:47:29Z, a read of `results/e9l/tail.json` `seam_left_bins.same_K` printed
  `[('0', 0.428, 0.26, 1.65), ('1', 0.244, 0.153, 1.59), ('2-3', 0.155, 0.089, 1.74), ('4-7', 0.127, 0.074, 1.72),
  ('8-15', 0.143, 0.086, 1.67), ('16+', 0.11, 0.063, 1.76)]` (bin, mean, median, ratio). The medians match 0036
  line 2203. `results/` is gitignored: the re-verify line needs the home mirror or a pull of the public backup.
re-verify: .venv/Scripts/python.exe -c "import json; t=json.load(open('results/e9l/tail.json')); print([(r['bin'], round(r['mean'],3), round(r['median'],3)) for r in t['seam_left_bins']['same_K']])"   # expect bin 0 (0.428, 0.26) and 16+ (0.11, 0.063)
