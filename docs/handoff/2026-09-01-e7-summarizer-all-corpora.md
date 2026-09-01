# Handoff — `summarize_e7` covers every corpus, headroom, and reported usage; entries 0013/0014

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
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 230 passed
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_summarize_e7.py -q` → 31 passed
re-verify (AFTER the ledger commit and a fresh `python -m linear_ceiling.e7`):
`.venv/Scripts/python.exe -m linear_ceiling.summarize_e7` → exit 0; the output states
`switches measured: 68`, `byte-identical handoffs: 0/68`, `headroom upper bound as a fraction of
paid: 81.3% (p10 31.7%, p90 88.4%)`, and the assistant row `8914 | 3,423 | 3,239 | 5,962 | 4.14`
(requires the local `traces/` set: 188 files hashed). Until that rerun, the summarizer REFUSES
the pre-taxonomy report on disk (`report has no \`taxonomy\` section; it predates this
summarizer -- rerun the driver`) — that refusal is correct, not a bug.

**REGISTERED — entry 0013 `[BASELINE]`**: the headroom figures, pulled from the report only
after `summarize()` passed inside the append script; chain `161b3835…`. **Entry 0014**: the
six-class invalidation taxonomy (`model_switch`, `rerender_at_switch`, `compaction`,
`idle_expiry`, `branch`, `edit`), each with a detection AND a measurability rule, plus the
H-E7a denominator = Lane A measurable subset; chain `5a2eaea7…`. Both uncommitted.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`

**REPLAYED — the taxonomy; entry 0015 written from the summarizer only.** The operator committed
0013/0014 (`4430a03`), ran `e7` + `summarize_e7` (exit 0), and `docs/drafts/append_0015.py`
re-ran `summarize()` in-process before pulling every figure from the report. **H-E7a
`NOT CONFIRMED`**: 2,339,562 / 165,959,914 over 60 measurable trajectories = 1.41% vs 10%.
**H-E7b `UNESTIMABLE`** (new verdict token, `ledger_check` + test): compaction 0 events over
the 800 trajectories that can evidence one, 2,104 NOT MEASURABLE. Also on record: 68/68
switches are re-renders; idle expiry 0/800 (tau2's warm bound is the realized case); branch
4 extra attempts on 2 of 4 nested instances. Chain `2899f4d3…`.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7` → exit 0 and the line
`pooled: ... = **1.41%** vs cutoff 10% -> BELOW the cutoff`
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e7_taxonomy.py tests/test_ledger_check.py -q` → 22 passed
re-verify: `grep -c "UNESTIMABLE" ledger/ledger.md` → ≥ 3 (table cell, header, entry)

**RECON (not on the record; informed 0014's definitions, stated there as recon):** tau2's
reported prompt tokens never decrease over 8,114 consecutive agent requests (compaction =
measured zero once replayed); no tau2 gap exceeds 300 s (max 235 s; idle expiry = measured
zero); the H-E7a ratio is ~0.4% / 0.5% / 1.4% under whole-corpus / suite / measurable-subset
denominators — below the 10% cutoff by an order of magnitude under every choice, which is why
the denominator could be registered without being outcome-selected.

**REPRODUCED through the fail-closed path** — every figure the previous brief marked
script-derived now recomputes identically: coverage swe-bench 64 / 5 agents / 15 tasks and
tau2-bench 800 / 4 / 50 tasks (floor MET; tau-bench 1980 / 2 reported, NOT met, excluded from
floor arithmetic per 0011); 68 switches across both composio submissions; overlap median 0.903
(p10 0.353, p90 0.982); paid median 19,972; upper bound 81.3% (31.7 / 88.4); user-simulator
offset −134 (−2,489 / +462, ratio 0.87); agent offset +3,423 (3,239 / 5,962, ratio 4.14); by
turn 3,238 / 3,264 / 3,382 / 3,609. Entry 0012's table is therefore now summarizer-backed
(it was written before the summarizer covered tau2 — that ordering was a process slip, now
closed). The headroom figures are on the record as entry 0013.

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

**BUILT, GATED, NOT RUN — E8** (`config/e8.toml`, `e8_text`, `e8`, `summarize_e8`; +21 tests).
The gate refuses until entry 0016 is committed, `config/e8.toml` carries the upstream sha
(currently the placeholder `TBD`, which the gate rejects by design) and the upstream HEAD
matches it with a clean tree. Two things verified for real, not on synthetic data: the
upstream's new `scripts/score_mapper.py` re-scores the archived k=1 mapper on the archived
dumps to **exactly** the archived `r2.json` (K 0.6813557347 / V 0.5132943501, diff 0.0e+00,
71 s CPU) — so 0016 §6's cross-check is a real refusal condition; and the Qwen3 tokenizer +
shared-vocab check run offline from the cached snapshots.
re-verify: `.venv/Scripts/python.exe -m pytest tests/test_e8_text.py tests/test_e8.py tests/test_summarize_e8.py -q` → 23 passed
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e8 --check` → exit 2, `upstream_sha is not a commit sha`
re-verify (upstream, ~71 s): `cd ../kv-transfer-replication && .venv/Scripts/python.exe scripts/score_mapper.py --mapper mappers/qwen3-0.6b-to-1.7b/k1 --src data/kv/qwen3-0.6b-to-1.7b/source --tgt data/kv/qwen3-0.6b-to-1.7b/target --out /tmp/k1.json` → `heldout K=0.6814 V=0.5133`

**DRAFTED, NOT APPENDED — entries 0016 (E8 amendment) and 0017 (E9 registration, band
K ≥ 0.70 HOLDS / ≤ 0.40 DEGRADES, operator-approved)** as ordering-guarded scripts in
`docs/drafts/`. **NOT STARTED** — E9 code (`e9_align`, upstream `dump_positions.py`, `e9`,
`summarize_e9`); the compaction break-even distribution (H-E7b needs compaction EVENTS first);
any paper draft.

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
- **H-E7a's denominator is the Lane A measurable subset** (0014): an unmeasurable trajectory
  cannot feed the numerator, and putting it in the denominator counts it as a measured zero.
  The recon showed the verdict direction is the same under every candidate, so this is not
  outcome-selection — say so if challenged, with the three recon ratios.
- **Taxonomy classes were registered before any frequency was computed** (0014), with a
  measurability rule per class. A final-transcript trace is NOT MEASURABLE for compaction,
  idle expiry and edit — that is the expected table shape and the finding, not a tooling gap.
- **`branch` events = attempts − 1**, flat layouts NOT MEASURABLE (a flat file cannot evidence
  a second attempt).
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
- `src/linear_ceiling/e7_taxonomy.py` — `classify(traj, headroom_rows|None, ttl)`,
  `frequencies`, `h_e7a`; `e7.taxonomy_block` glues them for driver and summarizer alike.
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

1. ~~Commit 0013/0014, rerun, entry 0015~~ — DONE 2026-09-01 (see above). The paper's framing
   is now fixed by the record: switching exists but is immaterial (fleet-mixing motivation);
   compaction is unestimable on public traces; the measurement paper's contribution is the
   taxonomy with its measurability structure, the hidden-prefix lower bound, and the
   re-rendered-handoff headroom with E9 measuring what is achievable.
2. ~~Taxonomy event definitions~~ — DONE (0014). 3. ~~Compaction detection~~ — DONE (0014/0015:
   measured zero where measurable).
4. **E8 run sequence (after 0015):** commit `scripts/score_mapper.py` upstream → note its sha →
   `python docs/drafts/append_0016.py <sha> <date>` → put the sha in `config/e8.toml` and
   `UPSTREAM.md` → commit → `e8 --check` → `e8` (CPU, ~15 min: one dump pass + 6 scorings) →
   `summarize_e8` (~25 min) → E8 verdict entry from its output only.
5. **LCFM now includes GPU runs** (operator, 2026-09-01): plan in
   `docs/2026-09-01-lcfm-gpu-plan.md`. Tier 1 = E8 on CPU this week (needs one amendment
   entry: E8 admitted to LCFM behind the summarizer gate; 0009's "dumps are gone" corrected —
   they exist locally, gitignored; verdict-bearing k = 1; text-sampling rule; upstream
   `score_mapper.py` + re-pin). Tier 2 = E9 on the A100 (achievable fraction of 0013's upper
   bound at the 68 real handoffs), registered with H-E9 + band before any prefill; go/no-go
   EOD 09-04. Deadline 09-10 AoE; freeze EOD 09-08.

**Open questions for the operator:**

- tau2's `gpt-4.1*` agents are tokenized by the calibrated divisors, not exactly, because
  `config/e7.toml` registers only `gpt-4o` as exact. gpt-4.1 also uses `o200k_base`; extending
  `agent_strategy` is a config change (gate-committed) and arguably a successor to entry 0009.
- The 9/5 model/timestamp census in the recon doc remains unverified (pre-0010 detector).
- E8's dump-regeneration wall-clock is still unmeasured.
