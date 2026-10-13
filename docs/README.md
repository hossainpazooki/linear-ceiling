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
| `2026-10-13-anonymity-denylist.md` | the terms the double-blind mirror censors, refreshed for the MLSys re-cut (supersedes the 2026-10-01 list) |
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
`2026-09-13-seed-e9-scaled-short-cell.md`.

## Status notes and pilot analyses (dated; superseded by later entries)

`2026-09-20-astra_review.md` · `2026-09-30-review-response-map.md` · `2026-10-01-a100-analysis.md` ·
`2026-10-01-cache-behavior-h100.md`. The pilot analyses are the co-author documents entry 0056 lets the paper cite
under a provenance sentence; the operator's registered runs (0048, 0049) are the figures.

Pruned 2026-10-13: superseded outlines, status notes, plans, two archived READMEs and scratch probes that no ledger
entry, live document or code cites by path were removed from the tree (26 files); they remain in git history at every
commit before the removal.

## Process records

- `handoff/HANDOFF.md` — a stub: session briefs and learnings became private records on 2026-10-13 (the files before
  that date remain in git history; the ledger cites this path once, at entry 0007).
- `probes/` — scratch probes that entries 0026 and 0028 cite.
- `provenance/` — borrowed-fact provenance.
