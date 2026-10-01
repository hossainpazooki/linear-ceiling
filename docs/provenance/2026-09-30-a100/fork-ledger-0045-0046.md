### 0045 — 2026-09-30 — Post-acceptance same-model consolidation registered before GPU measurements

Descriptive extension authorized by the operator; no existing hypothesis or verdict changes.
`config/consolidation.toml` fixes the models, revisions, common numerical tolerances, precision,
scaling, controls and bridge acceptance bounds. `config/consolidation-manifest.json` fixes the
reconstructed texts, model-specific token alignments, included cases and exclusions before prefill.
`docs/2026-09-30-consolidation-runbook.md` defines the readout, capture change, stopping/resume rule,
retained witness, environment, transport and paper scope. The supplied GPU was already provisioned;
registration precedes measurements rather than the hardware request, an explicit chronology
exception to R1 for this operator-requested descriptive extension. The original model is rerun only
for the implementation bridge; its complete archived cohorts are reused. New models are scored
separately at the existing numerical reference and ladder, without claiming a calibrated quality
threshold. The existing local mechanism pilot is exploratory and may be replayed unchanged on CUDA.

### 0046 — 2026-09-30 — Verified A100 same-model extension and archived seam error budget

Descriptive results under entry 0045; no hypothesis or registered verdict changes.
All 60 original handoff texts were scored for each new model, without exclusion or truncation.
Hardware: one A100-SXM4-80GB; FP32 prefill, fixed model-specific YaRN settings. The six-case
Qwen3-1.7B bridge has maximum relative mean-error gap 1.23258721479e-05 and maximum f* gap 0.0000 across the three tested tolerances and both K/V.
Local `tools/consolidation/summarize.py` verified all compact records and retained raw witnesses before these numbers were written. It reads the Desktop mirror; hardware replicas are not additional handoffs.

| Model | Cohort | n | Zero K f*(tau_K) | Median K f*(0.1) | Median K f*(0.03) | Median V f*(0.03) |
|---|---|---:|---:|---:|---:|---:|
| qwen4 | e9s | 25 | 25 | 0.0007 | 0.2739 | 0.3883 |
| qwen4 | e9l | 35 | 35 | 0.0460 | 0.4979 | 0.5394 |
| smollm3 | e9s | 25 | 25 | 0.0000 | 0.1527 | 0.1353 |
| smollm3 | e9l | 35 | 34 | 0.0580 | 0.4529 | 0.3630 |

Every new-model V handoff has zero f*(tau_V). The one positive SmolLM3 K case is
`20241025_composio_swekit/django__django-10554_traj#112`: mean deviation 0.33197629276022594 and f*(tau_K) 0.022754660806691713, recomputed in the verified CSV.

`tools/consolidation/archive_error_budget.py` reads the archived squared-error records. Its far-span means also match the earlier independent local audit on all 60 handoffs. Shares below are medians of per-handoff ratios, not pooled token statistics.

| Original Qwen cohort | Far token share | Far normalized-error share | Retained far mean | Handoffs still above 0.03 |
|---|---:|---:|---:|---:|
| e9s | 0.898178 | 0.770462 | 0.073605 | 25/25 |
| e9l | 0.924647 | 0.836802 | 0.101553 | 35/35 |

Far means seam distance at least 16. Deleting nearer tokens leaves the original full-matched-set normalizers fixed; this is a diagnostic deletion, not practical cache repair.
The new-model reference is the original Qwen mapper tolerance, not a validated quality threshold for the new models. Different handoff cohorts do not identify a length effect; model comparisons also change tokenizer, architecture, and scaling settings. No generated-text quality, serving speedup, or repeated-reuse stability was measured.

Full intervals and per-handoff values: `a100/summary.json` and `a100/summary.csv` in `~/Desktop/Carryover-evidence`.
summary-sha256: da3f8cd41ae07c62636fe5be9239c8a6b4a25f49b5b0380adc4d3cabf7d2f3ce
error-budget-sha256: 5b605009d0476d204bb50836d58ff992014a3b622fa15cb9dc8dea6e1c1c59c4
prior-entries-sha256: 5a3f7d81b7ba85915703abed1849e6e7695fb1815ff7eb695913329a1742759f
