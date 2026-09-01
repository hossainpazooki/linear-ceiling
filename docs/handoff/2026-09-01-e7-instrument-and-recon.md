# Handoff — E7 instrument built, tokenizer registered, SWE-bench recon

**Date:** 2026-09-01
**Describes commit:** `62282e9` (`feat: fail-closed E7 summarizer recomputing from raw traces,
with provenance hashes`) — plus an uncommitted doc set (README rewrite, SWE-bench recon,
learnings ledger, this brief). Pick-up measures drift from `62282e9`.
**Supersedes:** the re-verify lines of `2026-09-01-e7-rescope.md` and `2026-09-01-e7-skeleton.md`
(both stale on suite count and on "E7 has zero code"). Those briefs stay unedited.

## Current state

**BUILT — screen line, closed.** E0 ran; ladder verdict SAME under the rule frozen before any
weight was read (entries 0003/0004). Per-layer depth structure recorded via a fail-closed
summarizer (entry 0006); both readings — real end-of-network separation vs layer-0 proxy
degradation — deliberately left open, and no scheduled experiment will decide them.
H-S1/H-S3/H-S4 carry `SHELVED`; H-S2's first clause is `NOT CONFIRMED`.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e0_depth` → exit 0, verdict.json
sha256 `59fd962f92788eb4323594226e053ce121fe4ba17a1e821af0f9a43409e0c3bf`

**BUILT — E7 instrument.** `e7_traces` (tau-bench adapter, normalizes the per-agent str/dict
`arguments` split), `e7_tokens` (exact `o200k_base` for gpt-4o, per-content-type calibrated
divisors otherwise), `e7_cost` (warm/cold two-bound timeline), `e7_lanes`, `e7` (commit gate +
driver), `summarize_e7` (recomputes from RAW traces, refuses on tamper).
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 147 passed

**BUILT — the E7 commit gate, demonstrated in both directions.** `e7.assert_ready` refuses to
read a trajectory until ledger + `config/e7.toml` are committed unmodified and entries
0006/0007 are in the committed ledger. It refused live (exit 2) while config was dirty and
returned ready after the commit landed.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e7 --check` → "E7 gate: ready" on a clean
tree; modify `config/e7.toml` and it refuses with exit 2

**BUILT — fail-closed E7 summarizer, tamper-proven.** Ten refusal tests (config drift,
one-character trace edit, edited cost totals, edited token counts, inflated coverage, a floor
verdict the thresholds do not reproduce, NaN, missing provenance, and the worst case:
unmeasurable relabelled as a measured zero). The relabel tamper was also run against the real
1,980-trajectory report and was caught by `traj_id`; exit 1 on refusal, 0 clean.
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_summarize_e7.py -q` → 10 passed

**RAN — E7 over tau-bench only. No hypothesis decided.** 1,980 trajectories, 26,316 requests,
4 files, 2 agents. Lane A: 0 of 1,980 measurable (run-level model only — recorded NOT
MEASURABLE, never as zero). Coverage floor NOT met (2 agents < 3; 1 suite < 2), so every figure
is partial-with-coverage-stated.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7` → exit 0, `coverage floor
NOT met`, `Lane A: 0 of 1980 trajectories measurable` (needs `traces/tau-bench/`, gitignored —
acquire per the recon doc)

**REGISTERED, NOT RUN — E8** (transfer under agent-trace distribution shift), hypothesis H-E8,
tolerance band frozen in entry 0009 before any dump exists. Belongs to the MLSys program only.
re-verify: `grep -n "H-E8" ledger/ledger.md` → table row plus entry 0009's design section

**NOT STARTED.** SWE-bench adapters (~3 families) and its own tokenizer calibration; compaction
event detection and the taxonomy event definitions (which need their own registration before
frequencies ship); the E8 dump regeneration; any paper draft.

## Locked decisions

- **Screen line closed on opportunity-cost grounds** — the mechanism lane is crowded with
  top-track work (EuroSys best paper, NeurIPS/ICLR main-track) while the measurement lane is
  thin. Reason and evidence: `docs/2026-09-01-measurement-lane-evidence.md`. Reopening any H-S
  hypothesis means a numbered entry moving it back to `unresolved`.
- **Lane A alone decides H-E7a** (entry 0007) — Lane B inserts a switch at every tier boundary
  of a policy we chose, so its headroom is material by construction and measures the policy,
  not the workload.
- **MLSys 2027 (2026-10-30) is the anchor venue; LCFM is optional feedback** — LCFM is
  non-archival and permits concurrent submission, so it costs nothing structurally to skip.
  ICLR 2027 was rejected: its deadline collides and its genre rewards method novelty.
- **LCFM stays trace-only; E8 goes to MLSys** (entry 0009) — a transfer leg cannot be built in
  the remaining days.
- **Tokenizer: exact where a public encoder exists, calibrated per content type otherwise**
  (entry 0009) — a blanket estimator is differentially biased worst on tool output, exactly
  what compaction removes, so it would push H-E7b in a systematic direction.
- **Upstream drift is a one-time acknowledged exception** (operator, 2026-08-31) — do not build
  process around it; any upstream invocation records the actual state it ran against.

## Reuse map

- `src/linear_ceiling/summarize_e0.py` — the fail-closed pattern every summarizer copies
  (hash, NaN, recorded-vs-recomputed). `summarize_e0_depth` inherits `_recompute_lambda_stats`
  from it rather than re-implementing; do the same for new summarizers.
- `src/linear_ceiling/summarize_e7.py` — recomputes from raw inputs, not from the driver's
  report. The SWE-bench work extends this; do not add a second summary path.
- `src/linear_ceiling/e7_traces.py` — `Trajectory`/`Msg` is the normalized shape all adapters
  target; `tool_arguments_text` is the per-agent shape normalizer; `coverage` counts agents,
  not runs.
- `src/linear_ceiling/e7_tokens.py` — `make_counter(agent, cfg)` returns
  `count(text, content_type)`; add a strategy here, never a divisor in code.
- `src/linear_ceiling/e0.py::assert_ready` — the commit-gate pattern; `e7.assert_ready` is its
  second instance. Any new experiment runner gets one.
- `src/linear_ceiling/ledger_check.py::chain_hash` — the entry-chain hash; a new entry's
  `prior-entries-sha256` must be computed over the exact bytes preceding its heading.
- `docs/2026-09-01-swe-bench-trace-recon.md` — S3 paths, per-format census, schema families.
  Read before writing an adapter; it will save a day of format archaeology.

## Invariants

- **No number reaches the ledger except recomputed from raw inputs by a fail-closed
  summarizer.** Violating it creates a second, unaudited path from computation to claim —
  which is the entire failure mode this repo exists to prevent.
- **Registered entry text is immutable**, and from 0007 on the chain hash enforces it in CI.
  Amendments are new numbered entries. Editing a registered entry fails `ledger_check`.
- **Experiments refuse until their rules are committed.** Weakening `assert_ready` would make
  "the rule was frozen first" an assertion instead of a mechanism.
- **Lane B never resolves a hypothesis.** Merging the lanes would let a chosen policy
  manufacture the premise finding.
- **Unmeasurable is not zero.** Lane A reports `measurable=false, switches=null`; collapsing
  that to zero would invert the premise finding. A summarizer test pins this.
- **`traces/` and `results/` are gitignored.** Committing trajectories or result artifacts
  would create the unaudited path above and bloat history.
- **The scope sentence appears verbatim exactly once, in the README** (`lint_scope`).
- **The upstream is read-only and pinned** — never `import kvt`, never copy its code; borrowed
  facts carry `{sourceRepo, filePath, commitSha}`.

## Open / next

1. **Commit the uncommitted doc set** (README rewrite, recon doc, learnings ledger, this
   brief). The learnings ledger `docs/learnings/` is NEW to this repo — it needs the operator's
   blessing as a structure, not just a commit.
2. **SWE-bench adapters, role/content family first** — it covers the most submissions per unit
   of work. Then its own tokenizer calibration: the tau-bench divisors are corpus-specific and
   provably do not transfer.
3. **Validate the divisors against `20251110_frogboss-32b`**, which reports real
   `token_usage_prompt/completion/total`. This is ground truth independent of any tokenizer and
   can retire the tokenizer caveat instead of carrying it into the paper.
4. **Register the taxonomy event definitions** in a numbered entry before any frequency ships.
5. **Decide LCFM.** The numbers-freeze gate is EOD 2026-09-08 and the deadline 2026-09-10 AoE;
   skipping costs nothing structurally.

**Blockers / open questions for the operator:**

- The SWE-bench recon's finding — no public format records a per-step model — means H-E7a can
  only ever resolve as *unmeasurable across public corpora*. That IS the registered premise
  finding, but it may deserve its own numbered entry, since it is now a corpus-independent
  claim rather than a tau-bench artifact.
- E8's dump regeneration wall-clock is unmeasured (the upstream's `dumps/` are gone). Size it
  before committing E8 to the MLSys timeline.
- 47 of 119 SWE-bench submissions with trajectories are prose-only and must be excluded with
  the exclusion stated; 62 have no trajectories at all.
