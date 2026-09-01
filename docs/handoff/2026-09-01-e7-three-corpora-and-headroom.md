# Handoff — three corpora adapted, coverage floor met, first headroom numbers

**Date:** 2026-09-01 (late)
**Describes commit:** `23441e7` (`docs: ledger 0011 trajectory unit and floor met; 0012 hidden
prefix constrains every cost figure`), plus an uncommitted doc set (README rewrite, CLAUDE.md,
this brief). Pick-up measures drift from `23441e7`.
**Supersedes:** the re-verify lines of `2026-09-01-e7-instrument-and-recon.md` (stale on suite
count, corpora, and the switching claim). That brief stays unedited.

## Current state

**BUILT — screen line, closed.** E0's SAME verdict stands under the rule frozen before any
weight was read; per-layer depth structure recorded (entry 0006), both readings left open.
H-S1/H-S3/H-S4 `SHELVED`, H-S2 first clause `NOT CONFIRMED`.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e0_depth` → exit 0, verdict.json
sha256 `59fd962f92788eb4323594226e053ce121fe4ba17a1e821af0f9a43409e0c3bf`

**BUILT — E7 across three corpora, coverage floor MET.** Adapters: `e7_traces` (tau-bench),
`e7_tau2` (tau2-bench), `e7_swe` (LangChain/composio + layout-aware discovery),
`e7_rolecontent` (four role/content variants). Floor per entry 0011: swe-bench 64 trajectories /
5 agents, tau2-bench 800 / 4 agents, two suites.
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 183 passed

**BUILT — fail-closed `summarize_e7`, tamper-proven** on the real tau-bench corpus (relabelling
one unmeasurable trajectory as a measured zero is caught by traj_id; exit 1 on refusal).
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_summarize_e7.py -q` → 10 passed

**MEASURED — headroom at 68 observed cross-model switches** (composio, the only public family
that switches). 0/68 byte-identical. Overlap of the receiving prompt with sender-produced
content: median 0.903 (p10 0.353, p90 0.982). Paid prefill at switch: median 19,972 tokens.
Headroom **upper bound**: median 81.3% of paid (p10 31.7%, p90 88.4%).
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e7_headroom.py -q` → 8 passed
**These numbers came from a script, NOT from a summarizer — they may not enter the record until
`summarize_e7` recomputes them (entry 0006). That is the next build.**

**MEASURED — the hidden prefix** (entry 0012). Validated against tau2's provider-reported usage:
user-simulator offset −134 tokens (estimator sound), agent offset +3,423 and flat across turn
depth (a fixed system-prompt-plus-tool-schema block the trace omits, ~42k per trajectory).
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e7_tau2.py -q` → 8 passed

**REGISTERED, NOT RUN — E8** (transfer under agent-trace distribution shift), H-E8, band frozen
in entry 0009. MLSys program only; upstream `dumps/` are gone so both arms need regenerating.

**NOT STARTED.** Extending `summarize_e7` to the SWE-bench/tau2 suites and the headroom table;
compaction event detection and the taxonomy event definitions (which need their own registration
before frequencies ship); any paper draft.

## Locked decisions

- **Screen line closed on opportunity-cost grounds** — mechanism lane crowded with top-track
  work, measurement lane open (`docs/2026-09-01-measurement-lane-evidence.md`).
- **Lane A ALONE decides H-E7a; Lane B never resolves anything** (0007/0010) — Lane B inserts a
  switch at every boundary of a policy we chose, so its headroom is material by construction.
- **Unmeasurable is never zero** (0006) — collapsing the two inverts the premise finding.
- **A narrow detector is a defect, not a null** (0010) — this rule exists because a detector
  matching only the key `model` missed the one family that switches.
- **Trajectory = one agent run on one task instance** (0011) — file-counting overstated one
  submission 2x, and the count feeds the floor.
- **Headroom is an UPPER BOUND; trace-only cost is a LOWER BOUND** (0010/0012) — re-rendering
  changes tokens and positions; public traces omit the billed system prompt.
- **MLSys 2027 (2026-10-30) is the anchor; LCFM optional and non-archival.**
- **Tokenizer: exact where a public encoder exists, calibrated per content type otherwise**
  (0009), because the crude estimator is worst on tool output — what compaction removes.

## Reuse map

- `src/linear_ceiling/summarize_e0.py` — the fail-closed pattern every summarizer copies.
  `summarize_e7.py` is its second instance; extend that one, never add a second summary path.
- `src/linear_ceiling/e7_traces.py` — `Trajectory`/`Msg` is the shape all adapters target.
  `Msg.reported_tokens` carries provider ground truth where a corpus has it.
- `src/linear_ceiling/e7_swe.py` — `models_in` (registered-breadth detector),
  `discover_trajectories` (flat vs nested layouts), `load_composio_detailed` (returns texts
  alongside the trajectory so token and content views cannot drift).
- `src/linear_ceiling/e7_headroom.py` — the entry-0010 measure; `overlap_fraction` is a
  MULTISET intersection (set intersection overstates headroom).
- `src/linear_ceiling/e7_tokens.py` — `make_counter(agent, cfg)`; add a strategy there, never a
  divisor in code.
- `docs/2026-09-01-swe-bench-trace-recon.md` — S3 paths, per-format census, schema families.
- `docs/learnings/` — six entries, each with a read-only `re-verify:` line; two carry `kills:`
  supersession chains. Read before re-deriving anything about corpus formats.

## Invariants

- **No number reaches the ledger except recomputed from raw inputs by a fail-closed summarizer.**
- **Registered entry text is immutable**; the `prior-entries-sha256` chain enforces it in CI.
- **Experiments refuse until their rules are committed** (`assert_ready`).
- **Lane B never resolves a hypothesis**; **unmeasurable is never a zero**.
- **`traces/` and `results/` are gitignored** — trajectories never enter history.
- **The scope sentence appears verbatim exactly once, in the README** (`lint_scope`).
- **The upstream is read-only and pinned** — never `import kvt`, never copy its code.

## Open / next

1. **Extend `summarize_e7`** to the SWE-bench and tau2 suites and the headroom table. Until it
   does, the headroom and hidden-prefix numbers cannot enter a ledger entry or a paper. This is
   the numbers-freeze requirement (EOD 2026-09-08).
2. **Register the taxonomy event definitions** before any frequency is computed.
3. **Compaction detection** — what H-E7b needs; no compaction events are detected yet.
4. **Decide LCFM** (deadline 2026-09-10 AoE, non-archival; skipping costs nothing structurally).

**Open questions for the operator:**

- The surviving premise claim is narrow and should be stated carefully: switching **does** occur
  in public traces as a designed critic/selector stage (composio), while **production-style
  cost/quality routing remains unevidenced**. Neither "switching never happens" nor "the premise
  holds" is supportable.
- Composio is 2 submissions of one system; the 68 measured switches are not a sample of agent
  practice generally, and the paper must say so.
- The `9 model-ish / 5 timestamp-ish` census in the recon doc was produced with the pre-0010
  narrow detector and is marked **unverified**; re-derive before quoting.
- E8's dump-regeneration wall-clock is still unmeasured.
