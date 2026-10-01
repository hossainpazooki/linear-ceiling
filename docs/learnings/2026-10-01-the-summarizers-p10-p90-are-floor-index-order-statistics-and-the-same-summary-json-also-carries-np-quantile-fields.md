# The summarizer's `p10`/`p90` are floor-index order statistics, not interpolated quantiles — and the same `summary.json` also carries `np.quantile` fields, so two conventions coexist in one file

kills: (nothing)
ts: 2026-10-01T04:10:00Z
commit: 5a71df696615847233feb332b46f4f6abb79e440
session: e9l-aws-run (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl)
status: verified
fact: `e7_stats.quantile(values, p)` returns `sorted(values)[min(floor(p * n), n - 1)]` — an **observed data point**, with
no interpolation — and `e7_stats.summary` builds every `{n, median, p10, p90}` block from it, including the
`coverage_comparison.included.n_receiver` block that `e-tail-design.md` and `e-beh-design.md` quote as the |R| spread.
For the 35 included E9-long handoffs (n = 35) that gives `p10 = s[3] = 7,085` and `p90 = s[31] = 19,853`, matching
`summary.json` exactly. A hand recompute with `np.quantile`'s default linear interpolation gives **7,354.2** and
**18,997.8** — so an independent check of a registered |R| figure disagrees by ~4 % and looks like drift when nothing
has drifted. Worse, the *same* `summary.json` carries `np.quantile`-derived `p90`/`p99` fields elsewhere
(`summarize_e9.py:239,244`, the timing blocks), so one file holds two percentile conventions under the same key names.
Consequence: recompute a summarizer percentile with `e7_stats.quantile`, never with `np.quantile` or `statistics`, and
when a design or entry quotes a `p10`/`p90`, cite the summarizer field rather than a value derived by any other rule
(R11 makes the summarizer the only authority, and this is one of the places where "the same number computed honestly"
is a different number).
basis: `src/linear_ceiling/e7_stats.py:17-31` (`s[min(int(math.floor(p * len(s))), len(s) - 1)]`, and `summary` calling it
  for `p10`/`p90`); `src/linear_ceiling/summarize_e9.py:156-157` `_stats` → `summary`, `:510` passing `_stats` into
  `coverage_comparison`, `:868` writing the block, versus `:239,244` using `np.quantile`. Recomputed at `5a71df6` from
  `results/e9l/align/coverage.json` (35 included): `p=0.1 → s[3] = 7085` / `np.quantile 7354.2`;
  `p=0.9 → s[31] = 19853` / `np.quantile 18997.8`; `results/e9l/summary.json` `coverage_comparison.included.n_receiver`
  = `{n: 35, median: 11462.0, p10: 7085.0, p90: 19853.0}`. Both summarizer values are observed |R| values.
re-verify: .venv/Scripts/python.exe -c "import json,math,numpy as np;from pathlib import Path;R=sorted(a['n_receiver'] for a in json.loads(Path('results/e9l/align/coverage.json').read_text(encoding='utf-8'))['alignments'] if not a['excluded']);n=len(R);print('floor-index p90',R[min(int(math.floor(0.9*n)),n-1)],'| np.quantile p90',round(float(np.quantile(R,0.9)),1),'| summary.json',json.loads(Path('results/e9l/summary.json').read_text(encoding='utf-8'))['coverage_comparison']['included']['n_receiver']['p90'])"   # 19853 | 18997.8 | 19853.0
