# linear-ceiling — repo brief

Read `README.md` for what this is; `docs/2026-08-26-kv-handoff-screen-design.md` is the
authority on scope. `ledger/ledger.md` is append-only by numbered entry.

## Rules that override nothing global but must never be broken here
- `../kv-transfer-replication` is **read-only** and pinned (`UPSTREAM.md`). Never write there,
  never `import kvt`, never copy its code. Borrowed facts carry `{sourceRepo, filePath, commitSha}`.
- Never write a number into the ledger that was not recomputed from `results/` by a summarizer.
- Never edit a hypothesis after its experiment starts; never edit a sealed prediction.
- Seeds and thresholds live in `config/*.toml`. Randomness only via `linear_ceiling.rng.make_rng`.

## GPU runs
`docs/gpu-experiment-protocol.md` (rules R1–R12) governs every GPU experiment; each run also gets a
dated runbook (E9: `docs/2026-09-02-e9-gpu-runbook.md`). The short form: registered before requested
(no rule/τ/band/cap change once a score file exists); budget the attention backend, not the parameters
(f32 + GQA takes the math kernel); every input the driver reads is in git, the manifest, or listed by
sha in the runbook (gitignored mappers included); launch detached, rotate the log before any relaunch,
never `pkill -f` a self-matching pattern; pull → verify against `report.json` `kept_dumps` → delete,
per handoff; release by the seven-step checklist (mirror re-verified, box swept, HF cache removed,
server stopped and the effect probed); back the verified home mirror up to a private HF dataset
(`results/<exp>/` at the root + upstream artifacts in upstream layout; every file checked by
`lfs.sha256`), transport only — the summarizer reads the local mirror and a refusal is a finding.
Tokens: scoped, expiring, env-only, revoked once pasted anywhere. `tools/jupyterhub/` drives a
JupyterHub-only box (Algoverse) from home. E9's backup: `hossainpazooki/linear-ceiling-e9-2026-09-04`
(private; kept dumps 48 GB + `mappers/qwen3-0.6b-to-1.7b/k1.*`).

## Commands
```
.venv/Scripts/python.exe -m pytest -q                 # suite (synthetic, offline)
.venv/Scripts/python.exe -m linear_ceiling.seal verify
.venv/Scripts/python.exe -m linear_ceiling.lint_scope
.venv/Scripts/python.exe -m linear_ceiling.ledger_check
.venv/Scripts/python.exe -m linear_ceiling.e0 --config config/e0.toml   # refuses until entry 0003 sets the rule
.venv/Scripts/python.exe -m linear_ceiling.summarize_e0
.venv/Scripts/python.exe -m linear_ceiling.summarize_e0_depth   # per-layer depth structure (entry 0006)
.venv/Scripts/python.exe -m linear_ceiling.e7_manifest write     # NETWORK, once: hash traces/ + S3 keys/ETags + selection rule -> config/e7-manifest.json (commit it)
.venv/Scripts/python.exe -m linear_ceiling.e7_manifest fetch     # NETWORK: rebuild traces/ from the committed manifest (S3 for SWE-bench, sha256+size refused on mismatch; tau files listed by sha for manual restore, LF-normalize a Windows clone)
.venv/Scripts/python.exe -m linear_ceiling.e7_manifest check     # disk vs the committed manifest, both directions + bytes
.venv/Scripts/python.exe -m linear_ceiling.e7 --check           # E7 gate only; refuses until 0006/0007 + config/e7.toml + config/e7-manifest.json are committed
.venv/Scripts/python.exe -m linear_ceiling.e7 --config config/e7.toml   # replay over ALL corpora under traces/ (gitignored); refuses if disk != manifest
.venv/Scripts/python.exe -m linear_ceiling.summarize_e7          # fail-closed: recomputes EVERY E7 figure from RAW traces (all 3 suites, headroom, reported usage); refuses if disk, report or manifest disagree
.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 --strategy-override composio_swekit=exact   # entry 0022's sensitivity as a flag (after full verification; `sensitivity` in recon.json; ships only in the 0009 successor)
LC_REAL_TRACES=1 .venv/Scripts/python.exe -m pytest -q tests/test_e7_sensitivity.py   # the 0022 pin (565,025 / 255,690,850 = 0.2210%) against the real corpus; skipped without traces/
.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 --overlap-null --cache-aware-ratio   # entry 0024 recon (after full verification): null controls + H-E7a under four denominator readings -> results/e7/recon.json
.venv/Scripts/python.exe -m linear_ceiling.e8 --check           # E8 gate: refuses until 0016 + config/e8.toml committed AND upstream HEAD == pinned sha, clean
.venv/Scripts/python.exe -m linear_ceiling.e8                   # CPU: sample agent text (0016 s4) -> upstream dump_kv -> score_mapper both arms -> results/e8/report.json
.venv/Scripts/python.exe -m linear_ceiling.summarize_e8          # fail-closed: re-runs the upstream scorer on fingerprinted dumps (~25 min CPU) and compares
.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8a.toml   # E8 amendment gate (entry 0030): 0009 + 0016 + 0030 committed, the 0030 upstream re-pin, 0020's dumps by fingerprint
.venv/Scripts/python.exe -m linear_ceiling.e8 --config config/e8a.toml           # CPU (~10 min): rescores 0020's agent dumps with --holdout-frac 1.0 + per-token records -> results/e8a/report.json; re-dumps nothing
.venv/Scripts/python.exe -m linear_ceiling.summarize_e8 --config config/e8a.toml # fail-closed: re-scores, per-sequence R^2 from the record, seeded bootstrap over agent sequences, change from 0020 -> results/e8a/summary.{md,json}
.venv/Scripts/python.exe -m linear_ceiling.e9 --check           # E9 gate: refuses until 0019 + 0023 + 0025 + 0026 + 0027 + config/e9.toml committed AND the 0026 upstream re-pin holds (and the mapper artifact is present)
.venv/Scripts/python.exe -m linear_ceiling.e9 --align-only      # entry 0025: every alignment + results/e9/align/coverage.json (coverage, reasons, keep draw, block counts) before any prefill; CPU, no gate
.venv/Scripts/python.exe -m linear_ceiling.e9                   # GPU-scale: identity + null controls on the first handoff, then per handoff 3 stride-1 dumps + score_positions --per-token; checkpoints per handoff; keep-subset dumps retained
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --calibrate-tau   # 0023, before the GPU run: tau = 1 - archived k=1 held-out R^2 via upstream score_mapper --per-token; writes results/e9/calibration/tau.json (~1 min CPU)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9          # fail-closed: alignments from raw traces, R^2 from moments, per-token sums to moments, keep subset re-scored under 0028's cross-platform tolerance (sums 1e-5, squares 1e-2), tau recomputed, controls checked -> f*(tau), seam/depth profiles, band
```
On Linux/web the interpreter is `.venv/bin/python`.

## Layout
`src/linear_ceiling/` — `hashing` (canonical sha256) · `rng` · `config` · `pairs` · `seal` ·
`run_experiment` (E1+ gate stub) · `screen` (CCA math) · `weights` (safetensors reader) ·
`e0*` · `summarize_e0` · `summarize_e0_depth` · `e7_traces` (adapters; normalizes tau-bench's
per-agent str/dict `arguments` split) · `e7_tokens` (exact `o200k_base` where a public encoder
exists, per-content-type calibrated divisors otherwise — ledger 0009) · `e7_cost` (two-bound
timeline) · `e7_lanes` (Lane A measured / Lane B cascade) · `e7_corpus` (loads all three
suites into one shape; `LANE_A_ONLY_AGENTS`; unparsed recorded, never dropped) · `e7_manifest`
(the committed corpus manifest `config/e7-manifest.json`: per-file sha256, S3 key/ETag,
recovered selection rule; `verify_disk` both directions; canonical-JSON sha cited by every E7
entry from 0024 — `ledger_check` enforces the citation) · `e7` (gate + driver, `build_report`;
refuses if disk != manifest) · `summarize_e7` (fail-closed; recomputes every recorded value
from raw traces via a recursive comparator, refuses on tamper or on disk/report/manifest
disagreement) · `e7_swe` (LangChain family +
layout-aware `discover_trajectories`) · `e7_rolecontent` (4 variants) · `e7_tau2` (ground-truth
usage/timestamps) · `e7_headroom` (entry 0010 measure + rows/summary; `switch_slices` shared with the
nulls) · `e7_null` (entry 0024 overlap null controls: seeded derangement same-family + cross-family
role/content draw; NOT COMPUTABLE where a null cannot be formed) · `e7_cache` (entry 0024 H-E7a
under registered/request-level x cold/warm denominators; request-level = 0017's `paid` for every
request, byte-identical prefix vs the preceding request at read_mult) · `e7_usage`
(reported-vs-estimated, per role) · `e7_taxonomy` (entry 0014's six event classes, each with a
measurability rule; H-E7a ratio over the Lane A measurable subset) · `e7_stats` (the ONE pinned
quantile convention) · `e8_text` (0016 §4 sampling + Qwen tokenizer from the snapshot) · `e8`
(gate + driver by subprocess; never imports kvt) · `summarize_e8` · `upstream_gate` (the ONE
pin check: ancestor + invoked-paths-unchanged + clean — a later experiment's re-pin is not an
older experiment's drift) · `e9_align` (0019 handoff slices + difflib matched blocks +
exclusions) · `e9` (gate + pre-batch controls + per-handoff dump/score/delete driver, checkpointed) ·
`e9_pertoken` (entry 0023 arithmetic: centered delta in R²'s units, oracle f*(tau), seam distance
b(t) + fixed bins, null pairing, band) · `summarize_e9` (alignments re-derived from raw traces;
R² from recorded moments; per-token squares summed against the moments; keep-subset re-scored
from fingerprinted tensors; tau recomputed from the archived mapper; controls checked; then f*,
profiles, band) · `lint_scope` · `ledger_check` (structure, entry chain, block diff
`--against <rev>` so the TRAILING entry is immutable too, verdict-cell provenance — frozen map
through 0022 + `verdict: H-XX = <VERDICT>` lines from 0024 on — and the manifest citation).
Tests mirror modules under `tests/`.
`docs/drafts/` holds append scripts for entries not yet written, ordering-guarded.
`docs/probes/` holds the scratch probes entries 0026 and 0028 cite (SDPA memory probe, the shipped
candidate module's validation, the matching-platform re-score and its determinism test).

Program state: screen line closed (H-S1/S3/S4 `SHELVED`); E7 replayed across three corpora
(tau-bench, tau2-bench, SWE-bench), floor **met**, all registered outputs on the record.
Decided: **H-E7a `NOT CONFIRMED`** (an order of magnitude under the 10% cutoff under the
registered denominator after the 0017 correction; corrected figures in 0018, tokenizer
sensitivity in 0022 — 0005's kill condition applies; this is a claim about what public
BENCHMARK traces evidence, Lane A being measurable on 60 of 2,904 trajectories from one
designed critic stage, not about production workloads, which leave no public trace),
**H-E7b `UNESTIMABLE`** (0015), **H-E8 `NOT CONFIRMED`** (0020: K UNRESOLVED
/ V DEGRADES at the verdict k, neither read-out alone). **H-E9 `HELD`** (0029, 2026-09-04): E9 ran on an Algoverse H100 MIG 3g.40gb slice (JupyterHub only) at
`0a19b56` / upstream `d5786df`; 25 of 68 handoffs scored (the shorter half by |S|); median f*(τ_K) on the
same-model K arm is 0.0000 on every handoff (bootstrap [0, 0]) against HOLDS ≤ 0.15, read ON A FLOOR (0027:
f* is an oracle lower bound, CacheBlend's 10–15% is achieved); the cross arm's named descriptive outcome
sits beyond the DEGRADES edge (median f*_cross(τ_K) 0.9286). Pre-prefill amendments 0025, 0026 (upstream
re-pin after the 0023 pin OOMed on float32 attention scores, not logits: `sdpa_repeat_kv` +
`logits_to_keep=1`), 0027 (cross-arm outcome named, HOLDS-on-a-floor, kernel change as a bound, box
discipline); post-run 0028 registers the keep-subset re-score tolerance after the Windows re-score refused
on float32 thread-order jitter (same-model arrays reproduce bit-for-bit on a matching Linux platform). The
gate requires 0019 + 0023 + 0025 + 0026 + 0027. Runbook `docs/2026-09-02-e9-gpu-runbook.md` (amended
09-04); closing brief `docs/handoff/2026-09-04-e9-gpu-day-and-verdict.md`. Retained dumps (45 GB, 8
handoffs) live under `results/e9/scratch/` at home only; the `[STRETCH]` partial-prefill experiment on them
is registered and unrun. **E8 amendment (0030, registered 2026-09-04, descriptive):** arm (b) rescored over every agent
sequence with per-sequence moments and a seeded bootstrap, on 0020's dumps by fingerprint, under `config/e8a.toml`
and a separate `results/e8a/`; the H-E8 cell and τ_agent_K do not move; figures enter by their own entry. **E-RL** (KV reuse
across RL post-training checkpoints: recompute cost vs stale-KV cost at a weight update, read for
MLSys; 0023's f*(τ_K) plus a stale-vs-fresh importance-ratio / ESS statistic, τ unchanged) is
DESIGN ONLY — `docs/2026-09-02-e-rl-design.md` — unregistered, unnumbered, no code; own
Qwen3-0.6B GRPO run primary, OLMo-2 RLVR1 descriptive; first build step is an upstream change
(revision-aware `Pair`). **Entries 0006–0023 are the
authority; read them whole before touching E7/E8/E9 code.** Per-token deviation is in R²'s own
units (a token's share of unexplained variance), never a per-token percent error (0023). Every taxonomy class carries its own
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
