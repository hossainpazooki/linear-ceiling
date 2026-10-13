# Paper to record: where every printed figure comes from

Two papers draw on this record: the LCFM workshop paper (camera-ready sha256 `6c706bef…`, built 2026-10-04,
[OpenReview](https://openreview.net/forum?id=kEGVswNFaq)) and the MLSys 2027 draft. Neither paper's LaTeX is in this
repository. What is here is the chain a reader can follow from a printed number back to the bytes it was read from:

    paper sentence or cell  →  paste source (docs/drafts/tables/T<nn>)  →  ledger entry:line  →  summary file + sha256  →  Hugging Face dataset

The ledger never restates a summary-file figure from memory: the append script of each figures entry reads the file
in-process, and `ledger_check` keeps the entry immutable afterwards.

## The camera-ready, row by row

`docs/reviews/2026-10-07-submitted-camera-ready-reconciled-against-the-record-and-the-operator-runs.md` reconciles the
submitted PDF against the ledger, the Lean formalization and the two operator runs, one row per claim or four-digit
figure. Where the submitted text and the record disagree, that review says so; the MLSys delta table in
`docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md` §1 is the list of what changes.

## The MLSys figure set

Entry 0060 (2026-10-10) froze the figure set: a table mapping each reviewer point W1–W8 to the experiment that answers
it, the entry and ledger line, and the figure as read from its summary file with the file's sha12. That table is the
authority; this page only names the files beside it.

| cell | entry | summary file (local mirror, sha12 as recomputed 2026-10-11) | backup dataset |
|---|---|---|---|
| E9, same-model short cohort, Qwen3-0.6B → 1.7B | 0029 (figures), 0045 (tail), 0058 (reading) | `results/e9/summary.json` `ae461db872f2` | `hossainpazooki/linear-ceiling-e9-2026-09-04` |
| E9-long, the 35 long handoffs under a YaRN receiver | 0036, 0045 | `results/e9l/summary.json` `64e64e9318d4` | `hossainpazooki/linear-ceiling-e9l-2026-09-10` |
| E9 scaled short cell and the configuration share | 0038 | `results/e9s/compare.json` `a0699a826f1f` | `hossainpazooki/linear-ceiling-e9s-2026-09-13` |
| E-TRUNC, four truncation levels on the long handoffs | 0057 | `results/e9t/compare.json` `0572662307f3` | `hossainpazooki/linear-ceiling-e9t-2026-10-08` |
| second family E8, Llama-3.2-3B → 3.1-8B, all-sequence arm | 0040, 0053 | `results/e8fa/summary.json` `9ddb66cc2796` | `emmmy/linear-ceiling-e8f-2026-09-18` |
| second family E9 short cell | 0044, 0045 | `results/e9f/summary.json` `e1e5feb8aadd`; tail `results/e9f/tail.json` `c35c48b9dbbe` | `emmmy/linear-ceiling-e9f-2026-09-19` |
| second family long cell at a native receiver | 0051 | `results/e9fl/summary.json` `1ac712b3897e` | `hossainpazooki/linear-ceiling-e9fl-2026-10-07` (public since 2026-10-13) |
| same-model extension to two more models | 0048 | `results/consolidation/` | see entry 0048 |
| cache behaviour, next-token sensitivity | 0049 | `results/cache-behavior/summary.json`; the entry's CYCLIC arm is the file's `arms.scrambled` key (reuse and random keep their names) | see entry 0049 |
| corpus and headroom, E7 | 0015, 0018, 0022, 0024 | `results/e7/` (recomputed from raw traces by `summarize_e7`) | traces rebuilt from `config/e7-manifest.json` |

The paste sources, each with both source forms (entry:line at a named ledger revision, and summary-file key with sha12),
the conventions every number is under and an executable re-verify line: `docs/drafts/tables/` (T01 the quantile rule,
T02 the E-TRUNC paragraph, T03 the second-pair section).

## Quantile conventions, because one word changes a p90

Over-handoff quantiles are lower nearest-rank (`e7_stats.quantile`, the one pinned convention). The pooled per-token p10/p90/p99 fields
in the E9 summary files are `np.quantile` linear interpolation, on the record at 0038 and 0045. A paper table printing a
pooled per-token quantile states both conventions in words; the rule is `docs/drafts/tables/T01-pooled-per-token-quantiles.md`.

## Re-verify

```sh
cd ~/dev/linear-ceiling
for f in e9/summary e9l/summary e9s/compare e9t/compare e8fa/summary e9f/summary e9f/tail e9fl/summary; do sha256sum results/$f.json | cut -c1-12; done
# ae461db872f2 64e64e9318d4 a0699a826f1f 0572662307f3 9ddb66cc2796 e1e5feb8aadd c35c48b9dbbe 1ac712b3897e (one per line)
grep -c "ae461db872f2\|64e64e9318d4\|a0699a826f1f\|0572662307f3\|9ddb66cc2796\|e1e5feb8aadd\|c35c48b9dbbe\|1ac712b3897e" ledger/ledger.md   # 13
```

The first line needs the local mirror (`results/` never enters git; restore it from the datasets with
`tools/hf_verify_backup.py`). The second holds on any clone: every sha12 above is pinned on at least one ledger line.
