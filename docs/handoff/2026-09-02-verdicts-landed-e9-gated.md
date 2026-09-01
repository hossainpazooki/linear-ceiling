# Handoff — all E7/E8 verdicts on the record; E9 built, gated, awaiting the A100

**Date:** 2026-09-02
**Describes commit:** `151bb719e05231fdd12fc8766b1668c427655d5c` (clean tree except this brief,
the three 2026-09-02 learnings entries curated with it, and their index rows). Pick-up
measures drift from `151bb719`.
**Supersedes:** the re-verify lines of `2026-09-01-e7-summarizer-all-corpora.md` (stale on
suite count, entries, and E8/E9 state). That brief stays unedited.

## Current state

**built — the ledger through entry 0020, chained and pushed.** 0013 headroom `[BASELINE]`;
0014 taxonomy definitions + H-E7a denominator; 0015 taxonomy frequencies, **H-E7a
`NOT CONFIRMED`**, **H-E7b `UNESTIMABLE`**; 0016 E8 amendments (LCFM admission, dumps
correction, verdict k=1, text rule, re-pin `71df450`); 0017 instrument correction (composio
nested-prompt shape read as responses-only in 30/60 files; `paid` was the trajectory prefix,
not the receiver's request prefill — FIGURES of 0013/0015 superseded, verdicts stand); 0018
corrected figures (ratio 0.20% vs 10%); 0019 E9 registered (H-E9, band K ≥ 0.70 HOLDS /
≤ 0.40 DEGRADES, difflib-blocks alignment, 32k cap, keep-subset design, re-pin `7e41f792`);
0020 **H-E8 `NOT CONFIRMED`** (k=1: K +0.1185 UNRESOLVED / V +0.1715 DEGRADES, neither
read-out alone; arm (a) cross-checked against the archived r2.json exactly; two independent
end-to-end runs byte-identical).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`
re-verify: `grep -c "^### 00" ledger/ledger.md` → 20
re-verify: `grep -E "^\| H-E7a|^\| H-E7b|^\| H-E8|^\| H-E9" ledger/ledger.md | grep -oE "(NOT CONFIRMED|UNESTIMABLE|unresolved) \|$"` → NOT CONFIRMED, UNESTIMABLE, NOT CONFIRMED, unresolved (in that row order)

**built — the corrected E7 instrument.** `e7_swe._flatten_nodes` (both composio shapes),
`Msg.request`, request-level `paid` with a refusal when no request boundary exists, newline
joins; summarizer recomputes every figure across all three corpora.
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 279 passed
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7` → exit 0; contains
`= **0.20%** vs cutoff 10% -> BELOW the cutoff` (needs local `traces/`)

**built — E8, ran and decided.** Driver + fail-closed `summarize_e8` (re-runs the upstream
scorer on fingerprinted dumps; ~25 min CPU when invoked — the cheap check below reads the
gate instead).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e8 --check` → `E8 gate: ready` (proves
the ancestor-pin rule too: the upstream sits one commit past E8's pin)

**built — E9, gated and READY.** `e9_align` (0019 slices; over-cap and empty-receiver
handoffs excluded and counted), `e9` driver (per-handoff dump → score → delete, report
checkpointed after every handoff, seeded keep-subset retains fingerprinted dumps),
`summarize_e9` (re-derives every alignment from raw traces, recomputes every R² from recorded
per-layer/per-head SSE/SST, re-scores the keep subset from tensors, states medians + band —
the only place they are stated), upstream `scripts/score_positions.py` at pin `7e41f792`.
Live toy e2e on the real models passed (48 tokens: dump → align → score → moments).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e9 --check` → `E9 gate: ready`
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e9_align.py tests/test_e9.py tests/test_summarize_e9.py -q` → 22 passed

**built — docs to the current record.** Reviewer-first README in the rigor format (7 sections,
7 visuals, color only where the category is the message; findings table verdicts-only);
`docs/background.md` (history + the E0 n=1 / tied-embeddings scoping caveat + vocabulary);
staleness audit across every living doc; `docs/2026-09-02-e9-gpu-runbook.md`.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.lint_scope` → `scope ok`

**in-progress — nothing.** **planned — the A100 day** (runbook), then entry 0021 (H-E9
verdict) from `summarize_e9` output only; then the LCFM decision and the MLSys draft.

## Locked decisions

- **H-E8's verdict k = 1, K and V read out separately, neither alone** (0016 §3, 0009) — the
  k=8 mapper is collapsed on held-out data, and the summarizer's early "K read-out elected"
  line was removed as an unregistered election.
- **H-E7a's denominator is the Lane A measurable subset** (0014) — an unmeasurable trajectory
  in the denominator is a measured zero; recon showed every candidate denominator gives the
  same verdict direction.
- **`paid` is the receiver's own request prefill, never the trajectory prefix** (0017) — and
  the measure REFUSES without a request boundary rather than approximating.
- **E9 alignment = difflib longest matching blocks, autojunk off** (0019) — exact LCS is
  quadratic at 32k tokens; `|M|` is declared a floor.
- **E9 keeps a seeded 3-handoff subset's full dumps** (0019) — the CPU summarizer re-scores
  those from tensors; the rest's moments are a GPU-run record cross-checked by that subset,
  and the verdict entry must say so.
- **Upstream pins are checked by ancestry + invoked-paths-unchanged + clean tree, never
  HEAD-equality** (`upstream_gate`; learnings 2026-09-02) — HEAD-equality breaks the previous
  experiment at every re-pin.
- **One full upstream sha in UPSTREAM.md** (`tests/test_imports.py`) — prior pins cited
  short-form; each experiment's own pin lives in its config.
- **The E8 first-run figures stand** — the "contaminated sample" ruling was retracted on
  byte-compare evidence (learnings 2026-09-02); the two runs are a determinism check.
- **Screen-line closure is a decision, not a verdict** (0006; README top visual draws them as
  separate edges) — and E0's SAME is scoped to one family/proxy with tied embeddings
  (`docs/background.md`); reopening is one numbered entry away.

## Reuse map

- `src/linear_ceiling/upstream_gate.py::check_upstream` — the one pin check; any new
  experiment that invokes the upstream uses it, never a bespoke HEAD comparison.
- `src/linear_ceiling/e9.py` — `keep_subset` (seeded retention draw), `score_handoff`
  (dump → score → delete with fingerprints), per-handoff checkpointing pattern for any
  wipeable-box run.
- Upstream `scripts/dump_kv.py --stride 1` on a `[1, L]` token file dumps EVERY position of
  one sequence — no new dump code is ever needed for position-level work.
- Upstream `scripts/score_positions.py` — matched-position KV agreement + mapper transfer,
  with per-layer/per-head SSE+SST recorded so R² reproduces from moments.
- `docs/drafts/` append-script pattern — an entry that carries numbers runs its summarizer
  IN-PROCESS and pulls figures from the verified output; ordering-guarded; script deleted
  once appended. 0021's script gets staged there after the E9 sync.
- `docs/2026-09-02-e9-gpu-runbook.md` — the whole GPU day, verbatim; follow it, don't improvise.
- `linear_ceiling.e7_stats` — the ONE quantile convention; a second convention silently moves
  a p90.

## Invariants

- **No number reaches the ledger except recomputed from raw inputs by a fail-closed
  summarizer**; registered entry text is immutable (`prior-entries-sha256`, CI).
- **Experiments refuse until their rules are committed** (`assert_ready`, all of E0/E7/E8/E9)
  and until their upstream pin holds (`check_upstream`).
- **Unmeasurable is never a zero — per event class** (0014); figures carry their bound
  direction (UPPER for headroom, LOWER for trace-visible cost) or they do not ship.
- **Figures and verdicts are superseded separately** (0017 is the executed example).
- **The scope sentence appears verbatim exactly once, in the README** (`lint_scope` — and it
  reads period-free tables as one sentence; see learnings 2026-09-02).
- **`traces/`, `results/`, `data/` never enter history; the upstream is read-only** — changes
  land there as commits recorded by a re-pin entry, never as working-tree edits.
- **Handoff briefs and learnings entries are immutable** — a later session writes a new one;
  the index row supersedes, `kills:` supersedes.

## Open / next

1. **Submit the A100 request** (human-only: `slack.algoverseairesearch.org/a100`; 1-day grant
   suffices; countdown starts at approval). Then execute
   `docs/2026-09-02-e9-gpu-runbook.md` verbatim; the driver checkpoints per handoff and the
   keep-subset dumps MUST come off the box before expiry.
2. **Entry 0021 — the H-E9 verdict** from a clean local `summarize_e9` run, nothing else.
   Expected shape per 0019: median E9-same K vs the band; E9-cross reported as a fraction of
   E9-same; coverage (included/excluded at the 32k cap) stated with every figure.
3. **LCFM go/no-go stands at EOD 09-04** (plan doc): no GPU by then → ship trace-only + E8;
   numbers freeze EOD 09-08; deadline 09-10 AoE. The MLSys draft (10-30) is the anchor either
   way.
4. **Unregistered idea, needs a ruling before any work:** rerun E8 against mappers refit at
   n = 420 (dumps exist upstream) to separate content-shift degradation from small-calibration
   fragility — it would need a registration amendment (new baseline, band re-application)
   before anything runs.
5. **Standing small opens:** the 9/5 model/timestamp census in the recon doc is still marked
   unverified (pre-0010 detector); tau2's `gpt-4.1*` agents are tokenized by calibrated
   divisors though `o200k_base` would be exact (config change = successor to 0009 if wanted).
