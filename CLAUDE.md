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
(reported-vs-estimated, per role) · `e7_stats` (the ONE pinned quantile convention) ·
`lint_scope` · `ledger_check`. Tests mirror modules under `tests/`.

Program state: screen line closed (H-S1/S3/S4 `SHELVED`); the E7 measurement program is
registered **and built** across three corpora (tau-bench, tau2-bench, SWE-bench), coverage floor
**met**, headroom and reported-usage figures now **summarizer-recomputed** (admissible to the
record) — **no hypothesis decided**. **Entries 0006–0012 are the authority; read them whole
before touching E7 code.** Quantiles come only from `e7_stats` (lower nearest-rank; no
interpolation) — a second convention would silently change a p90. The rules newcomers break first: Lane A
ALONE decides H-E7a and Lane B never resolves anything (0007/0010); unmeasurable is never a zero
(0006); a narrow detector is a defect, not a null — search `model|model_id|model_name` minimum
(0010); a trajectory is one agent run on one task instance, not one file (0011); every
trace-only cost figure is a LOWER BOUND and headroom is an UPPER BOUND, both labelled (0010/0012).
`e7.assert_ready` refuses until the registering entries and `config/e7.toml` are committed
unmodified. Corpus formats and what they omit: `docs/2026-09-01-swe-bench-trace-recon.md`. Real
trajectories live under `traces/` (gitignored), never in history.
