# Handoff — `summarize_e7` covers every corpus, headroom, and reported usage

**Date:** 2026-09-01 (night)
**Describes commit:** the working tree after `28c90d9` plus the uncommitted build below
(pick-up measures drift from `28c90d9`; the commit block in the session report lands it).
**Supersedes:** the re-verify lines of `2026-09-01-e7-three-corpora-and-headroom.md` (stale on
suite count and on "headroom numbers are script-derived"). That brief stays unedited.

## Current state

**BUILT — the numbers-freeze requirement.** The fail-closed summarizer now walks all three
corpora and recomputes every recorded value: per-trajectory totals and lanes, coverage with
entry-0011 units and exclusions, per-suite and overall floor verdicts, the unparsed set, every
headroom row and its aggregate (entry 0010), the reported-usage validation (entry 0012), the
tokenizer provenance and the cost-basis label. Comparison is a recursive walker with exact
match on ints/bools/strings and 1e-6 relative on floats, key-set equality at every level, so a
recorded value cannot escape by being new.
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 213 passed
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_summarize_e7.py -q` → 25 passed
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7` → exit 0; the output states
`switches measured: 68`, `byte-identical handoffs: 0/68`, `headroom upper bound as a fraction of
paid: 81.3% (p10 31.7%, p90 88.4%)`, and the assistant row `8914 | 3,423 | 3,239 | 5,962 | 4.14`
(requires the local `traces/` set: 188 files hashed in the report)

**REPRODUCED through the fail-closed path** — every figure the previous brief marked
script-derived now recomputes identically: coverage swe-bench 64 / 5 agents / 15 tasks and
tau2-bench 800 / 4 / 50 tasks (floor MET; tau-bench 1980 / 2 reported, NOT met, excluded from
floor arithmetic per 0011); 68 switches across both composio submissions; overlap median 0.903
(p10 0.353, p90 0.982); paid median 19,972; upper bound 81.3% (31.7 / 88.4); user-simulator
offset −134 (−2,489 / +462, ratio 0.87); agent offset +3,423 (3,239 / 5,962, ratio 4.14); by
turn 3,238 / 3,264 / 3,382 / 3,609. Entry 0012's table is therefore now summarizer-backed
(it was written before the summarizer covered tau2 — that ordering was a process slip, now
closed). **The headroom figures are in no ledger entry yet**; a `[BASELINE]` entry recording
them is the natural next registration and needs the operator's go.

**TAMPER-PROVEN on the real corpus** (three live edits, each refused naming the path, report
restored, clean run exit 0): `headroom.summary.recoverable_fraction.median` pushed 0.813→0.85;
`reported_usage.per_role.assistant.offset.median` set to 0; one headroom row deleted
(`headroom.rows: length 68 != recorded 67`).

**BUILT — corpus loader** (`e7_corpus`): one walk for all suites; agent = submission name minus
the date; composio trajectories keep the DATED submission in `traj_id` (two submissions never
collide) while `agent` is `composio_swekit`; `LANE_A_ONLY_AGENTS` keeps composio out of floor
arithmetic (0011) without hiding it; a trajectory no adapter accepts is recorded under
`unparsed` with both adapters' reasons (real corpus: 0). Provenance = every file discovered,
including `.diff` siblings, keyed by POSIX path relative to `traces/`; the summarizer refuses on
a missing, added, or changed file.
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e7_corpus.py tests/test_e7_stats.py -q` → 15 passed

**BUILT — one quantile convention** (`e7_stats`): median = `statistics.median`, p =
`sorted[floor(p·n)]` (lower nearest-rank, no interpolation). It is the convention the recon
used, so the brief's numbers reproduce to the digit; any other convention changes a p90.

**REGISTERED, NOT RUN — E8** (entry 0009). **NOT STARTED** — compaction detection; taxonomy
event definitions (need their own entry before frequencies ship); any paper draft.

## Locked decisions

- **Floor arithmetic counts suites that clear it, not all suites** (`meets_floor`): entry 0011
  says tau-bench is reported but excluded; the old driver's `all(suites)` would have said NOT
  met with tau-bench present.
- **Composio is Lane-A-only in code, not config** (`LANE_A_ONLY_AGENTS`, like `MODEL_KEYS`):
  it is a registered fact about the corpus (0011), not a tunable parameter, and putting it in
  `config/e7.toml` would have blocked replay behind a config commit for no gain.
- **Unparsed is a recorded set, never a refusal and never a skip.** A whole-run refusal on one
  odd file would be a denial of service against the numbers; silent skipping is absence
  masquerading as evidence. The set is compared exactly by the summarizer.
- **The summarizer compares whole rows with one walker** rather than a hand-picked field list:
  a field that is recorded but not compared is a field that can be edited.
- **Prior locked decisions stand** (Lane A alone decides; unmeasurable ≠ zero; detector breadth;
  trajectory unit; UPPER/LOWER bound labelling; MLSys anchor; exact-or-calibrated tokenizer).

## Reuse map

- `src/linear_ceiling/e7_corpus.py` — `load_corpus(cfg)` → `Corpus(trajectories, texts,
  unparsed, files, strategies)`; `discover_files` is the provenance set. Add a suite here, and
  only here.
- `src/linear_ceiling/e7.py` — `build_report(cfg)` is the gate-free report builder the tests
  use; `run` = gate + build + write.
- `src/linear_ceiling/summarize_e7.py` — `_compare(path, recomputed, recorded)`; add a report
  section by recomputing it and calling `_compare`, never by trusting it.
- `src/linear_ceiling/e7_headroom.py` — `rows(trajs, texts, read_mult)` / `rows_summary`.
- `src/linear_ceiling/e7_usage.py` — `validation(trajs)`; `TURN_BINS` are the entry-0012 bins.
- `src/linear_ceiling/e7_stats.py` — `summary(values)` → `{n, median, p10, p90}`.
- `tests/test_e7_corpus.py::write_corpus` — the synthetic three-suite fixture (role/content,
  nested, LangChain-with-switch, tau2-with-usage, one garbage file); reused by the summarizer
  tests.

## Invariants

- **No number reaches the ledger except recomputed from raw inputs by a fail-closed summarizer**
  — now true for every E7 figure, not only tau-bench.
- **Registered entry text is immutable**; the `prior-entries-sha256` chain enforces it in CI.
- **Experiments refuse until their rules are committed** (`assert_ready`).
- **Lane A never decides from a narrow detector; unmeasurable is never a zero; Lane B never
  resolves anything.**
- **Every trace-only cost figure is a LOWER BOUND; headroom is an UPPER BOUND** — the labels
  are recorded in the report and compared, so they cannot be dropped in a re-render.
- **`traces/` and `results/` are gitignored**; the scope sentence appears once, in the README;
  the upstream is read-only and pinned.

## Open / next

1. **Register the headroom figures** in a numbered `[BASELINE]` entry (they are admissible now;
   they are not yet on the record). Operator's call.
2. **Taxonomy event definitions** — an entry before any frequency is computed.
3. **Compaction detection** — what H-E7b needs; nothing detects a compaction event yet.
4. **Decide LCFM** (deadline 2026-09-10 AoE; numbers-freeze gate EOD 09-08 is now satisfiable).

**Open questions for the operator:**

- tau2's `gpt-4.1*` agents are tokenized by the calibrated divisors, not exactly, because
  `config/e7.toml` registers only `gpt-4o` as exact. gpt-4.1 also uses `o200k_base`; extending
  `agent_strategy` is a config change (gate-committed) and arguably a successor to entry 0009.
- The 9/5 model/timestamp census in the recon doc remains unverified (pre-0010 detector).
- E8's dump-regeneration wall-clock is still unmeasured.
