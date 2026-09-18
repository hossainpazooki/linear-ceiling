# E9 kept-handoff cold re-score on a second machine

**Date:** 2026-09-14 (run 06:13–07:14Z). **Status:** review record, not a ledger entry, not a verdict, not summarizer output.
**Machine:** not the operator's — Apple M3 Pro (11 cores, 18 GB), macOS 26.5, arm64. Python 3.12.13, torch 2.14.0 (CPU), numpy 2.5.3; upstream venv transformers 5.16.1.
**Pins:** linear-ceiling `a5053b2f1d45` (fresh clone from GitHub, detached); upstream `kv-transfer-replication` `d5786df91f55` (fresh clone, detached; invoked paths clean); public dataset `hossainpazooki/linear-ceiling-e9-2026-09-04` at revision `a45e9ee8c511f5aab738400f06a2462b4fee5391`.

## Result

1. **Repo gates pass at `a5053b2`.** `pytest -q`: 436 passed, 1 skipped. `ledger_check`: `ledger ok (blocks unchanged vs HEAD)`. `ledger_check --against 700d830`: `ledger ok (blocks unchanged vs 700d830)`. `lint_scope`: `scope ok`. `seal verify`: `OK (no sealed predictions yet)`. `e9 --check`: `E9 gate: ready (entries 0019/0023/0025/0026/0027 committed; upstream pinned and clean; config/e9.toml)`.
2. **The corpus figures recompute from the public coverage file.** From `results/e9/align/coverage.json` with the repo's nearest-rank quantile: included |S| 25,460 (14,269, 30,106), |R| 6,551 (4,148, 9,165); excluded-for-length |S| 52,141 (35,692, 147,218), |R| 11,500 (7,085, 20,589); 68 observed = 25 included + 35 within 81,920 + 4 above + 4 empty receiver; newly included |S| 34,974–80,111. All equal to 0025 and 0035.
3. **`summarize_e9` cannot run from public artifacts alone.** Cold, it refuses: `E9 SUMMARY REFUSED: tau calibration: .../kv-transfer-replication/data/kv/qwen3-0.6b-to-1.7b/source/meta.json does not exist`. Its τ recalibration reads the upstream's n = 50 generic calibration dumps, and later steps read `results/e8/report.json` and `results/e7/skeleton_report.json`; none is in any public dataset of this program. It also refuses unless all 8 kept handoffs' dumps are present (48.16 GB). This is a finding about the reproducibility of the published record, not a failure of the E9 cell; no tolerance was touched.
4. **Kept-subset re-score: 6 of 8 pass 0028's registered tolerance.** The six smallest kept handoffs — django-10999#64, django-11066#36, astropy-14182#68, astropy-7166#88, astropy-7606#88, astropy-14365#119; the Sep 8 review covered 11066#36 and 14182#68, so four are new — were downloaded, fingerprint-verified against `report.json` (90 files each, 0 Finder files), and re-scored with the pinned `scripts/score_positions.py --per-token`. Compared against the archived records with `summarize_e9._rescore_agreement` (per-head sums ≤ 1e-05 relative, every square ≤ 1e-02 relative) and the summarizer's 1e-06 layer-mean R² check: **RESULT: ALL PASS (6 of 6)**.

| array | bit-identical fraction (min–max) | max square rel. diff | max per-head sum rel. diff |
|---|---|---|---|
| same_K | 0.507 – 0.689 | 4.1e-03 | 6.8e-06 |
| same_V | 1.000 – 1.000 | 0.0e+00 | 0.0e+00 |
| cross_K | 0.076 – 0.079 | 4.5e-03 | 3.4e-07 |
| cross_V | 0.043 – 0.043 | 2.7e-04 | 3.8e-07 |
| ref_K | 0.904 – 0.915 | 5.2e-07 | 1.1e-08 |
| ref_V | 1.000 – 1.000 | 0.0e+00 | 0.0e+00 |

5. **The statistic does not move.** Recomputed with the summarizer's own `centered_delta` → `token_mean` → `f_star`: f\* at τ_K, τ_V, τ = 0.1 and τ = 0.03 is identical, archive vs this machine, on every one of the six handoffs and all four arms (max |Δf\*| = 0.0e+00); the largest change in any token's centered δ is 3.3e-06 (cross_V; same_K 4.8e-08). Per-handoff same-model f\*(τ_K) = 0.0000 on all six; cross-model f\*(τ_K) 0.9360 / 0.9343 / 0.9438 / 0.9287 / 0.9607 / 0.9685.

## Stated, not smoothed

- **Exact equality does not hold on this platform.** The Sep 8 review's comparator (`docs/probes/2026-09-08-e9-independent-rescore-compare.py`) exits 1 on all six: `same_K`, `cross_K`, `cross_V`, `ref_K` token arrays and the corresponding layer-mean R² fields are not bit-equal (the R² fields agree within 1e-06). This is expected cross-platform float32 reduction order, the case 0028 registered its tolerance for.
- **Apple arm64 differs more on same_K than 0028 measured.** 0028 (Linux box vs Windows home) found same_K bit-identical on 0.991–1.000 of squares; here 0.507–0.689. The largest same_K per-head sum difference, 6.8e-06, is inside the 1e-05 tolerance by a factor of about 1.5. Reported as measured; the tolerance was not changed.
- **Per-token exceedance, beside f\* = 0.** Same-model K tokens with δ above τ_K, identical archive vs cold: 215 of 3,362; 488 of 3,622; 218 of 4,253; 636 of 4,485; 1,115 of 6,393; 356 of 7,302. f\*(τ_K) is 0 on each because f\* is 0023's mean-repair statistic. 0029's sentence that no matched token exceeds τ_K is false on these handoffs; the cell is unaffected.

## Interpretation boundary

A computational check of 6 of the 8 retained handoffs on a second platform. It does not cover the two largest retained handoffs (astropy-14995#74, astropy-14096#80, 7.8 GB each) or the 17 scored handoffs without retained dumps; it does not test the tolerance, the controls, the alignment or the floor reading; it does not re-run `summarize_e9` end to end (item 3); and whether it bears on the co-author condition on entries 0025–0029 is the operator's ruling. The comparison helpers are outside the repo: `e9_tolcheck.py` (sha256 `65af35aa2991…`) and `fstar_compare.py` (sha256 `7129fbd79044…`); both import linear-ceiling's own functions, so they are not independent of the code under test — the exact comparator above is the independent read.

## Reproduce

```bash
mkdir -p ~/e9-repro && cd ~/e9-repro
git clone https://github.com/hossainpazooki/linear-ceiling.git && (cd linear-ceiling && git checkout --detach a5053b2)
git clone https://github.com/hossainpazooki/kv-transfer-replication.git && (cd kv-transfer-replication && git checkout --detach d5786df91f55629933067e3c4bb14f1288c4bef2)
# linear-ceiling: uv venv --python 3.12 .venv; uv pip install torch (CPU index); uv pip install -e ".[dev]"; run the gates
# upstream: uv venv --python 3.12 .venv; uv pip install torch (CPU index); uv pip install -e . 'transformers==5.16.1'
cd linear-ceiling; REV=a45e9ee8c511f5aab738400f06a2462b4fee5391
hf download hossainpazooki/linear-ceiling-e9-2026-09-04 --repo-type dataset --revision $REV --exclude "scratch/*" --local-dir results/e9
hf download hossainpazooki/linear-ceiling-e9-2026-09-04 --repo-type dataset --revision $REV --local-dir results/e9 --include "scratch/<stem>/*"   # per handoff
# per handoff, from the upstream checkout:
.venv/bin/python scripts/score_positions.py --same-src $R/scratch/$S/same_src --same-tgt $R/scratch/$S/same_tgt --cross-src $R/scratch/$S/cross_src \
  --mapper $R/mappers/qwen3-0.6b-to-1.7b/k1 --pairs $R/align/$S.npz --out cold/$S.json --per-token cold/$S.tokens.npz
```

Raw outputs (gitignored locations, not committed): `~/e9-repro/cold/` (`tolcheck-6.json` sha256 `114b38f01484…`, `fstar-compare-6.json` sha256 `7ea5ad080b0e…`, per-handoff scores, per-token records, exact-comparator reports) and `~/e9-repro/logs/` (`fetch.sh`, `repro.sh`, `repro.log`).
