# docs/ — map

Five files at this level; everything else is sorted by kind. The dated filenames are unchanged, only the folders are
new (2026-10-13): the ledger cites the old paths at the revision each entry was written, and the table at the end of
this page resolves them.

## Read first

| file | what it is |
|---|---|
| `paper-to-record.md` | every figure the papers print, traced to its entry, its summary file and its paste source |
| `gpu-experiment-protocol.md` | the standing rules R1–R12 that bind every GPU run |
| `2026-10-03-co-author-run-admission.md` | how a co-author's GPU run enters the ledger |
| `2026-10-13-anonymity-denylist.md` | the terms a double-blind mirror censors; refreshed 2026-10-13, the venue term added 2026-10-27 (entry 0066) |
| `design/2026-08-26-kv-handoff-screen-design.md` | the design spec; the scope authority |
| `design/background.md` · `design/gap-map.md` · `design/2026-09-06-gap-map-revisited.md` | how the program got its shape, and the motivating claims read against the record |

## Folders

| folder | holds |
|---|---|
| `design/` | the design spec, seeds, plans and recon documents an experiment was specified from before it ran |
| `runbooks/` | one record per GPU sitting (box, registered config, pin, release checklist) plus the literal sitting procedure; each cited by the entry the sitting produced |
| `reviews/` | dated adversarial reads of the record, the camera-ready, the co-author runs and the reviewer responses; each a finished document |
| `pilots/` | the two co-author pilot analyses and the freeze record that entry 0056 admits for paper citation under a provenance sentence |
| `drafts/` | staged append scripts and `drafts/tables/` (the paper's paste-source tables); its README is the only entry-number allocator |
| `paper/` | the full paper's draft plan and delta index (dated 2026-10-08; its status line says what still holds) |
| `agent/` | command reference and module map for agents working in the repo |
| `probes/` | scratch probes that entries 0026 and 0028 cite |
| `provenance/` | borrowed-fact provenance and frozen input manifests |
| `assets/` | the README figure, built by a pinned script |
| `handoff/` | a stub only: session briefs and learnings became private records on 2026-10-13 (entry 0007 cites this path) |

## Runbooks, by sitting

| file | sitting | entry |
|---|---|---|
| `runbooks/2026-09-02-e9-gpu-runbook.md` | E9, Algoverse A100/H100 slice | 0029 |
| `runbooks/2026-09-08-n420-target-dump-runbook.md` | n = 420 target dump | 0033 |
| `runbooks/2026-09-10-e9l-gpu-runbook.md` | E9-long, rented L40S | 0036 |
| `runbooks/2026-09-13-e9s-gpu-runbook.md` | E9 scaled short cell | 0038 |
| `runbooks/2026-09-18-llama-gpu-runbook.md` · `design/2026-09-18-llama-upstream-patch-spec.md` | second family E8 and short cell | 0040, 0044 |
| `runbooks/2026-09-19-sitting-b-procedure.md` | the literal sitting procedure | — |
| `runbooks/2026-09-30-consolidation-runbook.md` · `runbooks/2026-10-07-consolidation-runpod-runbook.md` | same-model extension, pilot then operator run | 0046, 0048 |
| `runbooks/2026-10-01-cache-behavior-runbook.md` · `runbooks/2026-10-06-cache-behavior-runpod-runbook.md` | cache behaviour, pilot then operator run | 0047, 0049 |
| `runbooks/2026-10-07-llama-long-cell-runpod-runbook.md` | second family long cell at a native receiver | 0051 |
| `runbooks/2026-10-04-e-trunc-gpu-runbook.md` | E-TRUNC, four truncation levels | 0057 |

## Paths cited by the ledger before 2026-10-13, and where the file is now

Dated records (runbooks, reviews, seeds, the ledger, approved paste-source files) keep the old spelling in their
text; only live documents and code were updated. `git log --follow` on the new path shows the whole history.

| cited as | now |
|---|---|
| `docs/2026-08-26-kv-handoff-screen-design.md` | `docs/design/2026-08-26-kv-handoff-screen-design.md` |
| `docs/2026-08-26-seed-w1.md` | `docs/design/2026-08-26-seed-w1.md` |
| `docs/2026-09-01-lcfm-gpu-plan.md` | `docs/design/2026-09-01-lcfm-gpu-plan.md` |
| `docs/2026-09-01-measurement-lane-evidence.md` | `docs/design/2026-09-01-measurement-lane-evidence.md` |
| `docs/2026-09-01-swe-bench-trace-recon.md` | `docs/design/2026-09-01-swe-bench-trace-recon.md` |
| `docs/2026-09-02-e-rl-design.md` | `docs/design/2026-09-02-e-rl-design.md` |
| `docs/2026-09-02-e9-gpu-runbook.md` | `docs/runbooks/2026-09-02-e9-gpu-runbook.md` |
| `docs/2026-09-06-gap-map-revisited.md` | `docs/design/2026-09-06-gap-map-revisited.md` |
| `docs/2026-09-08-n420-target-dump-runbook.md` | `docs/runbooks/2026-09-08-n420-target-dump-runbook.md` |
| `docs/2026-09-08-seed-e9-long-half.md` | `docs/design/2026-09-08-seed-e9-long-half.md` |
| `docs/2026-09-10-e9l-gpu-runbook.md` | `docs/runbooks/2026-09-10-e9l-gpu-runbook.md` |
| `docs/2026-09-13-e9s-gpu-runbook.md` | `docs/runbooks/2026-09-13-e9s-gpu-runbook.md` |
| `docs/2026-09-13-seed-e9-scaled-short-cell.md` | `docs/design/2026-09-13-seed-e9-scaled-short-cell.md` |
| `docs/2026-09-18-llama-gpu-runbook.md` | `docs/runbooks/2026-09-18-llama-gpu-runbook.md` |
| `docs/2026-09-18-llama-upstream-patch-spec.md` | `docs/design/2026-09-18-llama-upstream-patch-spec.md` |
| `docs/2026-09-19-sitting-b-procedure.md` | `docs/runbooks/2026-09-19-sitting-b-procedure.md` |
| `docs/2026-09-20-astra_review.md` | `docs/reviews/2026-09-20-astra_review.md` |
| `docs/2026-09-30-consolidation-runbook.md` | `docs/runbooks/2026-09-30-consolidation-runbook.md` |
| `docs/2026-09-30-review-response-map.md` | `docs/reviews/2026-09-30-review-response-map.md` |
| `docs/2026-10-01-a100-analysis.md` | `docs/pilots/2026-10-01-a100-analysis.md` |
| `docs/2026-10-01-cache-behavior-freeze.json` | `docs/pilots/2026-10-01-cache-behavior-freeze.json` |
| `docs/2026-10-01-cache-behavior-h100.md` | `docs/pilots/2026-10-01-cache-behavior-h100.md` |
| `docs/2026-10-01-cache-behavior-runbook.md` | `docs/runbooks/2026-10-01-cache-behavior-runbook.md` |
| `docs/2026-10-04-e-trunc-gpu-runbook.md` | `docs/runbooks/2026-10-04-e-trunc-gpu-runbook.md` |
| `docs/2026-10-06-cache-behavior-runpod-runbook.md` | `docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md` |
| `docs/2026-10-07-consolidation-runpod-runbook.md` | `docs/runbooks/2026-10-07-consolidation-runpod-runbook.md` |
| `docs/2026-10-07-llama-long-cell-runpod-runbook.md` | `docs/runbooks/2026-10-07-llama-long-cell-runpod-runbook.md` |
| `docs/background.md` | `docs/design/background.md` |
| `docs/gap-map.md` | `docs/design/gap-map.md` |
| `docs/2026-10-01-anonymity-denylist.md` | removed (superseded by `docs/2026-10-13-anonymity-denylist.md`; in history) |
| `docs/handoff/<brief>.md` · `docs/learnings/<entry>.md` | private records since 2026-10-13; in history at every commit before `833fc28` |

Pruned 2026-10-13: superseded outlines, status notes, plans, two archived READMEs and scratch probes that no ledger
entry, live document or code cites by path were removed from the tree (26 files); they remain in git history.
