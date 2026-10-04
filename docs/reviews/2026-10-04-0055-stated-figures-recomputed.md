# Entry 0055's stated figures, recomputed from the record

**Date:** 2026-10-04 (run 09:49–10:08Z). **Status:** review record, not a ledger entry, not a verdict, not summarizer
output. **Who:** the operator's main-branch session — operator-side, NOT independent (same machine, same mirrors). The
E-TRUNC close (`docs/handoff/2026-10-04-e-trunc-for-camera-ready-0055-and-0056-on-the-ledger-pr-17-merged-pilot-figures-citable.md`,
"Open / next" item 4) asked for this pass; an independent one by a co-author would be a different record.
**Pins:** linear-ceiling `9e5249b` (0055 appended at `a5c8691`); the four alignment passes `results/e9t-{full,l65,l49,l32}/align/coverage.json`
(raw sha12 `0b0419ea1d27` / `c5c3b3d55828` / `1120282c65b0` / `d07606d8d3e8`); `results/e9t/shrinkage.json`.

## Method

`summarize_e9_trunc.shrinkage(load_levels(...))` re-run in-process from the four alignment passes and compared key by key
with the `shrinkage.json` on disk that 0055 read; the reference medians re-read through the reader's own `_references`;
the compute bound recomputed from `results/e9l/align/coverage.json` (two sender prefills plus the receiver per included
handoff, per level); every count the entry states checked against the per-handoff records; the runbook and ledger lines
the entry cites read at those lines.

## Findings

| 0055 states | recomputed | result |
|---|---|---|
| shrinkage pre-check, all aggregate keys | fresh in-process run equal to the file on disk on every key (`levels`, `ratio`, `pooled_ratio`, `n_common*`, `void`, `n_void`, `n_zero`, `n_below_0_80`, `survivable_fraction`, `rematching_loss`, `n_with_rematching_loss_over_0_05`) | SURVIVES |
| per-handoff ratio median 0.4470 (p10 0.0000, p90 0.8270; min 0.0000, max 0.8965); pooled 0.4090 (158,480 of 387,508) | same | SURVIVES |
| 14 of 35 void under the 2,000 floor (11 with no common token); 21 enter; 29 below the 0.80 ratio | 14 / 11 / 21 / 29; all 35 below 0.90; 154,620 common tokens on the 21 | SURVIVES |
| of the 11 with no common token, 4 because no matched token's sender position survives S[−32,768:]; three more keep under 0.1 % | 4 with survivable fraction 0; 3 with survivable fraction in (0, 0.001) | SURVIVES |
| survivable fraction median 0.5027 | 0.5027 | SURVIVES |
| reference levels 0.0381 (`results/e9s/compare.json` `a0699a826f1f`) and 0.0629 (`results/e9l/summary.json` `64e64e9318d4`) | 0.038085 / 0.062873 read by `_references`, same shas | SURVIVES |
| 4 handoffs above 65,536; 19 above 49,152 | 4 / 19 (included n_sender) | SURVIVES |
| prefill tokens FULL 3,970,435 / L65536 3,921,773 / L49152 3,596,221 / L32768 2,721,489; total 14,209,918 = 3.58× | identical, as Σ(2·min(\|S\|, L) + \|R\|) | SURVIVES |
| E9-long: 1.5–3 min per handoff (runbook :139), peak 31.56 GiB at 80,111 (runbook :127), 80 minutes (0036) | both runbook lines say so; 0036 states launched 23:53:12Z, finished 01:13:09Z = 79 min 57 s | SURVIVES |
| "aligner re-matching loses more than the removal on 10 handoffs (median loss beyond removal 0.0000, max 0.4159)" | 10 is `n_with_rematching_loss_over_0_05`; 14 handoffs have any re-matching loss; on 0 does re-matching (survivable − ratio) exceed the removal (1 − survivable); median 0.0000 and max 0.4159 are right | **WORDING REFUTED, figures survive** |

The design document's §10 carries the same sentence. The entry is immutable; the erratum is staged in
`docs/drafts/append_0057.py` (`erratum_0055`, counts read from `shrinkage.json` at append time), so it lands with the
E-TRUNC figures entry. Nothing here moves the reading, the gate or any cell.

## Re-verify

```
.venv/Scripts/python.exe -c "import json;s=json.load(open('results/e9t/shrinkage.json',encoding='utf-8'));p=s['per_handoff'].values();print(s['n_void'],s['n_zero'],s['n_with_rematching_loss_over_0_05'],sum(v['rematching_loss']>0 for v in p))"   # 14 11 10 14
```
