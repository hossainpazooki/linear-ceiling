# linear-ceiling — repo brief

Read `README.md` for what this is; `docs/2026-08-26-kv-handoff-screen-design.md` is the
authority on scope. `ledger/ledger.md` is append-only by numbered entry.

## Rules that override nothing global but must never be broken here
- `../kv-transfer-replication` is **read-only** and pinned (`UPSTREAM.md`). Never write there,
  never `import kvt`, never copy its code. Borrowed facts carry `{sourceRepo, filePath, commitSha}`.
- Never write a number into the ledger that was not recomputed from `results/` by a summarizer.
- Never edit a hypothesis after its experiment starts; never edit a sealed prediction.
- Seeds and thresholds live in `config/*.toml`. Randomness only via `linear_ceiling.rng.make_rng`.

## Commands
```
.venv/Scripts/python.exe -m pytest -q                 # suite (synthetic, offline)
.venv/Scripts/python.exe -m linear_ceiling.seal verify
.venv/Scripts/python.exe -m linear_ceiling.lint_scope
.venv/Scripts/python.exe -m linear_ceiling.ledger_check
.venv/Scripts/python.exe -m linear_ceiling.e0 --config config/e0.toml   # refuses until entry 0003 sets the rule
.venv/Scripts/python.exe -m linear_ceiling.summarize_e0
.venv/Scripts/python.exe -m linear_ceiling.summarize_e0_depth   # per-layer depth structure (entry 0006)
.venv/Scripts/python.exe -m linear_ceiling.e7 --check           # E7 gate only; refuses until 0006/0007 + config/e7.toml are committed
.venv/Scripts/python.exe -m linear_ceiling.e7 --config config/e7.toml   # replay over ALL corpora under traces/ (gitignored)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e7          # fail-closed: recomputes EVERY E7 figure from RAW traces (all 3 suites, headroom, reported usage)
.venv/Scripts/python.exe -m linear_ceiling.e8 --check           # E8 gate: refuses until 0016 + config/e8.toml committed AND upstream HEAD == pinned sha, clean
.venv/Scripts/python.exe -m linear_ceiling.e8                   # CPU: sample agent text (0016 s4) -> upstream dump_kv -> score_mapper both arms -> results/e8/report.json
.venv/Scripts/python.exe -m linear_ceiling.summarize_e8          # fail-closed: re-runs the upstream scorer on fingerprinted dumps (~25 min CPU) and compares
```
On Linux/web the interpreter is `.venv/bin/python`.

## Layout
`src/linear_ceiling/` — `hashing` (canonical sha256) · `rng` · `config` · `pairs` · `seal` ·
`run_experiment` (E1+ gate stub) · `screen` (CCA math) · `weights` (safetensors reader) ·
`e0*` · `summarize_e0` · `summarize_e0_depth` · `e7_traces` (adapters; normalizes tau-bench's
per-agent str/dict `arguments` split) · `e7_tokens` (exact `o200k_base` where a public encoder
exists, per-content-type calibrated divisors otherwise — ledger 0009) · `e7_cost` (two-bound
timeline) · `e7_lanes` (Lane A measured / Lane B cascade) · `e7_corpus` (loads all three
suites into one shape; `LANE_A_ONLY_AGENTS`; unparsed recorded, never dropped) · `e7` (gate +
driver, `build_report`) · `summarize_e7` (fail-closed; recomputes every recorded value from raw
traces via a recursive comparator, refuses on tamper) · `e7_swe` (LangChain family +
layout-aware `discover_trajectories`) · `e7_rolecontent` (4 variants) · `e7_tau2` (ground-truth
usage/timestamps) · `e7_headroom` (entry 0010 measure + rows/summary) · `e7_usage`
(reported-vs-estimated, per role) · `e7_taxonomy` (entry 0014's six event classes, each with a
measurability rule; H-E7a ratio over the Lane A measurable subset) · `e7_stats` (the ONE pinned
quantile convention) · `e8_text` (0016 §4 sampling + Qwen tokenizer from the snapshot) · `e8`
(gate incl. upstream pin + driver by subprocess; never imports kvt) · `summarize_e8` ·
`lint_scope` · `ledger_check`. Tests mirror modules under `tests/`. `docs/drafts/` holds the
append scripts for entries not yet written (0016, 0017), ordering-guarded.

Program state: screen line closed (H-S1/S3/S4 `SHELVED`); E7 replayed across three corpora
(tau-bench, tau2-bench, SWE-bench), floor **met**, all three registered outputs on the record:
headroom (0013), taxonomy frequencies (0015), break-even `UNESTIMABLE` (0015). **H-E7a is
`NOT CONFIRMED`** (1.41% vs the 10% cutoff, Lane A alone, measurable-subset denominator) —
entry 0005's kill condition applies and the motivation reverts to fleet mixing. Entry 0017
supersedes the FIGURES of 0013 and 0015's ratio (composio adapter shape defect; `paid` is the
receiver's request prefill, never the trajectory prefix); the corrected figures land as 0018,
E9 registers as 0019. Live hypotheses: H-E8 (built, gated on 0016) and H-E9. **Entries
0006–0017 (and successors) are the authority; read them whole before touching E7/E8 code.** Every taxonomy class carries its own
NOT MEASURABLE state; a recorded 0 where the class is unmeasurable is the forbidden zero.
Quantiles come only from `e7_stats` (lower nearest-rank; no interpolation) — a second
convention would silently change a p90. The rules newcomers break first: Lane A
ALONE decides H-E7a and Lane B never resolves anything (0007/0010); unmeasurable is never a zero
(0006); a narrow detector is a defect, not a null — search `model|model_id|model_name` minimum
(0010); a trajectory is one agent run on one task instance, not one file (0011); every
trace-only cost figure is a LOWER BOUND and headroom is an UPPER BOUND, both labelled (0010/0012).
`e7.assert_ready` refuses until the registering entries and `config/e7.toml` are committed
unmodified. Corpus formats and what they omit: `docs/2026-09-01-swe-bench-trace-recon.md`. Real
trajectories live under `traces/` (gitignored), never in history.
