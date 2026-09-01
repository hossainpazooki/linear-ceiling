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
.venv/Scripts/python.exe -m linear_ceiling.e7 --config config/e7.toml   # skeleton replay over traces/ (gitignored)
```
On Linux/web the interpreter is `.venv/bin/python`.

## Layout
`src/linear_ceiling/` — `hashing` (canonical sha256) · `rng` · `config` · `pairs` · `seal` ·
`run_experiment` (E1+ gate stub) · `screen` (CCA math) · `weights` (safetensors reader) ·
`e0*` · `summarize_e0` · `summarize_e0_depth` · `e7_traces` (adapters; token counts are a
chars/4 ESTIMATE, non-verdict-bearing until a tokenizer is registered) · `e7_cost` (two-bound
timeline) · `e7_lanes` (Lane A measured / Lane B cascade) · `e7` (gate + skeleton driver) ·
`lint_scope` · `ledger_check`. Tests mirror modules under `tests/`. Program state: screen line
closed; the E7 measurement program is registered (entries 0006 + 0007 are the authority —
read both whole before touching E7 code) with the skeleton instrument built; no replay has
run, and `e7.assert_ready` refuses until the registration is committed unmodified. Real
trajectories go under `traces/` (gitignored), never into history.
