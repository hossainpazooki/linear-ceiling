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
dated runbook (E9: `docs/2026-09-02-e9-gpu-runbook.md`; the n = 420 target dump: `docs/2026-09-08-n420-target-dump-runbook.md`). The short form: registered before requested
(no rule/τ/band/cap change once a score file exists); budget the attention backend, not the parameters
(f32 + GQA takes the math kernel); every input the driver reads is in git, the manifest, or listed by
sha in the runbook (gitignored mappers included); launch detached, rotate the log before any relaunch,
never `pkill -f` a self-matching pattern; pull → verify against `report.json` `kept_dumps` → delete,
per handoff; release by the seven-step checklist (mirror re-verified, box swept, HF cache removed,
server stopped and the effect probed); back the verified home mirror up to an HF dataset, public or private
(`results/<exp>/` at the root + upstream artifacts in upstream layout; every file checked by
`lfs.sha256`), transport only — the summarizer reads the local mirror and a refusal is a finding.
(Observed 2026-09-11: all three datasets read `private: false` on the Hub, which R8's "private"
clause does not contemplate; unreconciled, the operator's to rule on. R8 is unchanged here.)
Ruled 2026-09-11 by the operator: public is fine, and R8 now says so.
`tools/hf_backup.sh [--check|--verify-only] <repo_id> <staging_dir>` is that push: records, tree, card last; retries
only the Hub's 128-commits/hour 429; refuses a missing dataset, a public one unless `ALLOW_PUBLIC=1`, a concurrent upload or summarizer, and a
token without the `hf_` prefix; ends in `tools/hf_verify_backup.py`, whose exit is the script's. Run `--check` first.
Tokens: scoped, expiring, env-only, revoked once pasted anywhere. `tools/jupyterhub/` drives a
JupyterHub-only box (Algoverse) from home; `tools/ec2/` drives a rented EC2 GPU instance over ssh (E9-long,
runbook `docs/2026-09-10-e9l-gpu-runbook.md`). E9's backup: `hossainpazooki/linear-ceiling-e9-2026-09-04`
(public as of 2026-09-11; kept dumps 48 GB + `mappers/qwen3-0.6b-to-1.7b/k1.*`).

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
.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8fa.toml  # second family's E8 amendment gate (staged entry 0052, provisional): 0009 + 0016 + 0039 + 0052 committed, the family pin 06f8d55 (contains 0030's 223f469), 0040's dumps and token file by fingerprint
.venv/Scripts/python.exe -m linear_ceiling.e8 --config config/e8fa.toml          # CPU (~10 min): rescores 0040's agent dumps with --holdout-frac 1.0 + per-token records -> results/e8fa/report.json; re-dumps nothing; results/e8f untouched
.venv/Scripts/python.exe -m linear_ceiling.summarize_e8 --config config/e8fa.toml # fail-closed, as e8a: per-sequence R^2 from the record, seeded bootstrap, change from 0040 -> results/e8fa/summary.{md,json}; the figures entry reads it in-process
.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8c.toml   # entry 0033 gate: 0009 + 0016 + 0033 committed, the 0030 pin, the TAGGED n = 420 mapper present, 0031's dumps by fingerprint
.venv/Scripts/python.exe -m linear_ceiling.e8 --config config/e8c.toml           # CPU: 0030's protocol with the n = 420 mapper (mappers/<pair>/n420) -> results/e8c/report.json (mapper bytes fingerprinted)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e8 --config config/e8c.toml # fail-closed, as e8a; also refuses on swapped mapper bytes
.venv/Scripts/python.exe -m linear_ceiling.e9_rescore check --config config/e9c.toml   # entry 0033 gate: 0019/0023/0025/0027/0029 + 0033, both configs committed, pin by ancestry, tagged mapper present
.venv/Scripts/python.exe -m linear_ceiling.e9_rescore run                              # CPU: score_positions over the 8 kept handoffs' retained dumps + 0029's alignments with the n = 420 mapper -> results/e9c/
.venv/Scripts/python.exe -m linear_ceiling.e9_rescore summarize                        # fail-closed: same-arm CONTROL vs 0028's recheck (refuses), cross f* under tau_K / tau_K' / ladder beside 0029's, bootstrap -> results/e9c/summary.{md,json}
.venv/Scripts/python.exe -m linear_ceiling.e9 --check           # E9 gate: refuses until 0019 + 0023 + 0025 + 0026 + 0027 + config/e9.toml committed AND the 0026 upstream re-pin holds (and the mapper artifact is present)
.venv/Scripts/python.exe -m linear_ceiling.e9 --align-only      # entry 0025: every alignment + results/e9/align/coverage.json (coverage, reasons, keep draw, block counts) before any prefill; CPU, no gate
.venv/Scripts/python.exe -m linear_ceiling.e9 --align-only --config config/e9s.toml   # scaled short cell (0037): must reproduce 0029's 25 + keep draw; the registration script checked it
.venv/Scripts/python.exe -m linear_ceiling.e9 --check --config config/e9s.toml        # gate: 0019/0023/0025/0027/0035/0037 committed, upstream at 0036's pin 063f402, mapper by sha
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --calibrate-tau --config config/e9s.toml   # BEFORE the GPU run (0023): the gate does not check it and the summarizer refuses without it (learnings 2026-09-14)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --config config/e9s.toml      # fail-closed, as e9l minus bridge/profiles; then:
.venv/Scripts/python.exe -m linear_ceiling.e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json   # paired native-vs-scaled per token + the configuration share -> results/e9s/compare.{json,md}; refuses on any seam
.venv/Scripts/python.exe -m linear_ceiling.e9                   # GPU-scale: identity + null controls on the first handoff, then per handoff 3 stride-1 dumps + score_positions --per-token; checkpoints per handoff; keep-subset dumps retained
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --calibrate-tau   # 0023, before the GPU run: tau = 1 - archived k=1 held-out R^2 via upstream score_mapper --per-token; writes results/e9/calibration/tau.json (~1 min CPU)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9          # fail-closed: alignments from raw traces, R^2 from moments, per-token sums to moments, keep subset re-scored under 0028's cross-platform tolerance (sums 1e-5, squares 1e-2), tau recomputed, controls checked -> f*(tau), seam/depth profiles, band
.venv/Scripts/python.exe -m linear_ceiling.e9 --check --config config/e9l.toml        # E9-long gate (entry 0035): 0019/0023/0025/0027/0035 committed, config/e9l.toml committed, the RoPE-spec upstream pin, mapper by sha
.venv/Scripts/python.exe -m linear_ceiling.e9 --align-only --config config/e9l.toml   # cap 81,920 / floor 32,768: the 35 newly included handoffs, run order, keep draw -> results/e9l/align/coverage.json (what 0035 cites)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --calibrate-tau --config config/e9l.toml   # tau recomputed under the e9l pin -> results/e9l/calibration/tau.json (needed before the e9l summary; ~2 min CPU)
.venv/Scripts/python.exe -m linear_ceiling.e9 --config config/e9l.toml [--resume]    # GPU box: bridge control first (native vs YaRN receiver on 3 short handoffs), then the 35 by |S| ascending; every dump under --rope-scaling; --resume keeps hash-matching checkpoint work
.venv/Scripts/python.exe -m linear_ceiling.e9 --close-partial --config config/e9l.toml   # entry 0035 stopping rule: close an unfinished run at the operator's cutoff; scored set must be a prefix of the registered order; unscored named
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --config config/e9l.toml     # fail-closed as above plus: floor re-derived, run order re-derived, partial prefix checked, bridge re-scored from tensors + its registered reading, length profiles (by |S| bin, by position in S)
.venv/Scripts/python.exe -m linear_ceiling.e9_tail --config config/<cell>.toml       # runs summarize_e9 first (the gate), then the per-token TAIL from the same pinned records: tokens over each tau, means after removing the top 10/20 %, seam and position bin MEANS beside medians, native-window subset, |R| -> results/<cell>/tail.{json,md}, pinned to summary.json + report.json (W3/W4/W5; the corrective entry reads it)
.venv/Scripts/python.exe -m linear_ceiling.e9 --align-only --config config/e9t-<level>.toml   # E-TRUNC (0055 appended 2026-10-04): the alignment pass per level (full / l65 / l49 / l32); the truncated levels see S' = S[-L:] via [e9.alignment] sender_head_truncate; inclusion is decided on the full |S| so every level keeps 0036's 35
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc --shrinkage           # BEFORE any prefill, CPU: M_cap (tokens matched under every level) and |M_cap|/|M_FULL| per handoff from the four passes -> results/e9t/shrinkage.{json,md}; append_0055.py runs it in-process
.venv/Scripts/python.exe -m linear_ceiling.e9 --check --config config/e9t-<level>.toml        # gate per level: 0019/0023/0025/0027/0035/0055 committed, the four configs committed, upstream at 0036's pin 063f402, mapper by sha
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc                        # after the four runs: summarize_e9 per level (fail-closed, the gate), then the paired comparison on M_cap, the |M_cap| >= 2000 void gate, and the registered +/-0.005 reading of L32's far-from-seam median against 0038 / 0036 (READ from results/e9s/compare.json and results/e9l/summary.json) -> results/e9t/compare.{json,md}
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
`e9_rescore` (entry 0033: the kept-subset cross arm re-scored with a tagged mapper; the same-model arm is a refusing
control against 0028's recheck; `E8Config.mapper_tag` is the E8 half) · `e9_pertoken` (entry 0023 arithmetic: centered delta in R²'s units, oracle f*(tau), seam distance
b(t) + fixed bins, null pairing, band) · `summarize_e9` (alignments re-derived from raw traces;
R² from recorded moments; per-token squares summed against the moments; keep-subset re-scored
from fingerprinted tensors; tau recomputed from the archived mapper; controls checked; then f*,
profiles, band) · `lint_scope` · `ledger_check` (structure, entry chain, block diff
`--against <rev>` so the TRAILING entry is immutable too, verdict-cell provenance — frozen map
through 0022 + `verdict: H-XX = <VERDICT>` lines from 0024 on — and the manifest citation).
Tests mirror modules under `tests/`.
`docs/drafts/` holds append scripts for entries not yet written, ordering-guarded.
`proofs/` (PR #16, 2026-10-04) is the Lean 4 formalization of the paper's theory: 0023's statistic (`fstar` is the exact-criterion twin of
`e9_pertoken.f_star`), Theorem 1 (μ = 1 − R̄²), Theorem 2, Corollary 3 (seams), Proposition 4 (attention under `ass:rope`) and the
reported numbers in `Carryover/Numbers.lean`; `Audit.lean` prints the axioms of all 52 headline results (only `propext`,
`Classical.choice`, `Quot.sound`; no `sorry`). Toolchain Lean v4.34.0-rc2 + Mathlib pinned in `lean-toolchain` / `lake-manifest.json`;
build with `cd proofs && lake exe cache get && lake build && lake env lean Audit.lean`, or `./check.sh` where `lake` is broken (needs the
Mathlib build in `.lake/packages`; ~21 min, mostly loading Mathlib). Not run in CI and not verified on this Windows machine. "Lean" may be
claimed in the paper only after `lake build` has passed on the committed tree (seed §5/§8); `.lake/` is git-ignored.
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
and a separate `results/e8a/`; the H-E8 cell and τ_agent_K do not move; figures enter by their own entry. **LCFM sprint (operator ruling 2026-09-06):** outline in `docs/paper/2026-09-06-lcfm-outline.md`
(gap-map preface from `docs/2026-09-06-gap-map-revisited.md`; registered reading for H-E7a); 0031 (E8 figures) and
0032 (E9 admitted to the 4-pager) appended 2026-09-07; 0033 (calibration-size sensitivity: k = 1/4/8 mapper refit upstream on
the n = 420 dumps under tag `n420`, E8 arms via `config/e8c.toml`, E9 kept-subset cross arm via `config/e9c.toml`; descriptive)
appended 2026-09-08 after the n = 420 TARGET half was dumped on an Algoverse H100 MIG 1g.20gb slice
(`docs/2026-09-08-n420-target-dump-runbook.md`; the 2026-08-25 CPU attempt had died with nothing written, so the source half
is CPU 08-24 and the target half GPU 09-08, stated in 0033); the registered fit ran on the same box (home swapped at k = 4);
0034 (its figures: e8c + e9c summarizers, both passed) appended 2026-09-09. The box release hit a co-author's audit on the
shared login → protocol R7 step 0 + learnings 2026-09-09. **E9-long (0035 registered 2026-09-09; 0036 decided 2026-09-10): H-E9L `HELD`** — the same instrument on the 35 handoffs above the prior cap (|S| 34,974–80,111) under a YaRN-2.5 receiver (upstream RoPE-spec pin `063f402`, `config/e9l.toml`), run on a rented EC2 L40S (`tools/ec2/`, runbook `docs/2026-09-10-e9l-gpu-runbook.md`): median f*(τ_K) 0.0000 on every handoff, bootstrap [0, 0], bridge control CARRIED (scaled vs native receiver f* 0 ≤ 0.15, so τ_K carries), cross arm 0.9640 beyond DEGRADES; never pooled with 0029's 25; read on a floor (0027). Mirror + backup (operator, 2026-09-10: the files stay local AND are backed up): `results/e9l/` at home, and the HF dataset `hossainpazooki/linear-ceiling-e9l-2026-09-10`, BACKUP VERIFIED 18:28Z 2026-09-10 (724 files, 61.94 GB; all 529 `report.json` fingerprints match the Hub). The dataset is PUBLIC: the operator changed it after the free tier's 100 GB private limit stopped the push twice, and squashed its history first, so the stray files of a mis-directed upload are gone. **E-RL** (KV reuse
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
trajectories live under `traces/` (gitignored), never in history. **0045 (2026-10-01, corrective, descriptive):** f* = 0 is a
statement about the MEAN within τ_K, not "no token over τ_K" (0029/0036's sentence); the per-token tail per cell from `e9_tail`
(e9l 7.9 %, e9 5.8 %, e9s 6.7 %, e9f 11.3 % of matched tokens over τ_K, on every handoff; per-handoff maximum mean 0.2692 / 0.2207 /
0.2255 / 0.2860 against τ_K 0.3186 / 0.2861), the 0025/0029 R² label (0.4371 is 1 − R²; R² = 0.5629), seam-bin MEANS beside the
medians, and 0044's E7-hash erratum. No cell moves. **Allocation 2026-10-04:** 0046/0047 (APPENDED 2026-10-04, `a941377` / `55a5c47`) register the two co-author-piloted runs (same-model extension, PR #8+#9; cache-behavior, PR #14) for the operator's own run under R1-R8, 0048/0049 (staged) take their figures by in-process readers, the Llama long drafts moved to 0050/0051 (gate `"0050"`); 0052/0053 (staged, 4ab54ae) the Llama E8 amendment; 0054 (APPENDED `a2742b9`) records the 2026-10-04 Condition 1 ruling (issue #7 + PR #12 as the confirmation; issue #7 closed with a row disposition); 0052 APPENDED (Llama E8 amendment registration); 0056 (APPENDED `caccab5`) lets paper text cite the co-author pilot documents under a provenance sentence, ledger evidence rules unchanged; 0055 (APPENDED `a5c8691`, PR #17) registers E-TRUNC with its two stated limitations (|M_∩| ≥ 2,000 floor, 21 of 35 enter; L32-native deferred). 0053 APPENDED (`0c5ec15`, the Llama E8 amendment ran; the inversion does not persist); 0050 APPENDED (`cff787f`, Llama long cell registered at a native receiver). File order after 0047: 0054, 0052, 0056, 0055, 0053, 0050; `ledger_check` chains by file order. Staged: 0048/0049 (the two registered runs' figures), 0051 (Llama long figures), 0057 (E-TRUNC figures; runbook `docs/2026-10-04-e-trunc-gpu-runbook.md`). Next free entry: 0058. The pilots' figures enter only via `docs/2026-10-03-co-author-run-admission.md`.
