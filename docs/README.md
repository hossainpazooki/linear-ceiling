# docs/ — map

The files at this level keep their original dated names because the ledger cites them by path and the
ledger is immutable. This page is the sorting the file system does not do. Four kinds of document live
here, and a reader needs only the first two.

## Read first

| file | what it is |
|---|---|
| `paper-to-record.md` | every figure the papers print, traced to its entry, its summary file and its paste source |
| `gpu-experiment-protocol.md` | the standing rules R1–R12 that bind every GPU run |
| `2026-08-26-kv-handoff-screen-design.md` | the design spec; the scope authority |
| `background.md` · `gap-map.md` · `2026-09-06-gap-map-revisited.md` | how the program got its shape, and the motivating claims read against the record |
| `2026-10-03-co-author-run-admission.md` | how a co-author's GPU run enters the ledger |
| `2026-10-01-anonymity-denylist.md` | the terms the double-blind mirror censors |
| `reviews/` | dated adversarial reads of the record, the camera-ready and the co-author runs; each a finished document |
| `drafts/` | staged append scripts and `drafts/tables/` (the paper's paste-source tables); its README is the only entry-number allocator |
| `paper/` | the outlines the LCFM paper was written from and the MLSys delta index |
| `agent/` | command reference and module map for agents working in the repo |

## Runbooks, one per GPU sitting

Each names the box, the registered config, the pin and the release checklist it ran under. Cited by the entry
the sitting produced.

| file | sitting | entry |
|---|---|---|
| `2026-09-02-e9-gpu-runbook.md` | E9, Algoverse A100/H100 slice | 0029 |
| `2026-09-08-n420-target-dump-runbook.md` | n = 420 target dump | 0033 |
| `2026-09-10-e9l-gpu-runbook.md` | E9-long, rented L40S | 0036 |
| `2026-09-13-e9s-gpu-runbook.md` | E9 scaled short cell | 0038 |
| `2026-09-18-llama-gpu-runbook.md` · `2026-09-18-llama-upstream-patch-spec.md` | second family E8 and short cell | 0040, 0044 |
| `2026-09-19-sitting-b-procedure.md` | the literal sitting procedure | — |
| `2026-09-30-consolidation-runbook.md` · `2026-10-07-consolidation-runpod-runbook.md` | same-model extension, pilot then operator run | 0046, 0048 |
| `2026-10-01-cache-behavior-runbook.md` · `2026-10-06-cache-behavior-runpod-runbook.md` | cache behaviour, pilot then operator run | 0047, 0049 |
| `2026-10-07-llama-long-cell-runpod-runbook.md` | second family long cell at a native receiver | 0051 |
| `2026-10-04-e-trunc-gpu-runbook.md` | E-TRUNC, four truncation levels | 0057 |

## Seeds, designs and plans (how an experiment was specified before it ran)

`2026-08-26-seed-w1.md` · `2026-09-01-lcfm-gpu-plan.md` · `2026-09-01-measurement-lane-evidence.md` ·
`2026-09-01-swe-bench-trace-recon.md` · `2026-09-02-e-rl-design.md` (unregistered) · `2026-09-08-seed-e9-long-half.md` ·
`2026-09-11-gpu-runs-after-the-pivot.md` · `2026-09-13-e-rl-validation.md` · `2026-09-13-seed-e9-scaled-short-cell.md` ·
`2026-09-14-seed-condition-1.md` · `2026-09-19-async-rl-arr-design.md` (moved out) · `2026-10-01-mlsys-box-plan.md` ·
`2026-10-01-run-queue-farhan.md` (the ask to a co-author with his own compute).

## Status notes and pilot analyses (dated; superseded by later entries)

`2026-09-14-condition-1-board-source.md` · `2026-09-14-condition-1-status.md` · `2026-09-14-e9s-result-note.md` ·
`2026-09-20-astra_review.md` · `2026-09-30-review-response-map.md` · `2026-09-30-team-status-wednesday.md` ·
`2026-10-01-a100-analysis.md` · `2026-10-01-cache-behavior-h100.md`. The pilot analyses are the co-author documents
entry 0056 lets the paper cite under a provenance sentence; the operator's registered runs (0048, 0049) are the
figures.

## Process records

- `handoff/HANDOFF.md` — a stub: session briefs and learnings became private records on 2026-10-13 (the files before
  that date remain in git history; the ledger cites this path once, at entry 0007).
- `probes/` — scratch probes that entries 0026 and 0028 cite.
- `provenance/` — borrowed-fact provenance.
- `archive/` — superseded READMEs, verbatim.
