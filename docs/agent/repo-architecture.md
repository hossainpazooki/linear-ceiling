# Repository architecture

A reference map of where things live and which module owns which rule. It is not a status log: verdicts are in
the ledger's hypothesis table, current work in the newest brief of `docs/handoff/HANDOFF.md`, staged entries in
`docs/drafts/README.md`. Commands: `docs/agent/experiment-commands.md`. Rules: the root `CLAUDE.md`.

## Single owners (one module, one rule)

A second implementation of any of these would silently change a recorded figure or let a gate pass that should
refuse, so extend the owner rather than adding a sibling.

| rule | owner |
|---|---|
| quantiles (lower nearest-rank, no interpolation) | `e7_stats` — the ONE pinned quantile convention |
| upstream pin check (ancestor + invoked paths unchanged + clean) | `upstream_gate` — the ONE pin check; a later experiment's re-pin is not an older experiment's drift |
| ledger structure, entry chain (by file order), block diff `--against <rev>` (so the TRAILING entry is immutable too), verdict-cell provenance (frozen map through 0022 + `verdict: H-XX = <VERDICT>` lines from 0024 on), the E7 manifest citation | `ledger_check` |
| the scope sentence: exactly once, verbatim, in README; no paraphrase in README / ledger / `docs/**/*.md` | `lint_scope` |
| canonical sha256 | `hashing` |
| randomness | `rng.make_rng` |
| sealed predictions | `seal` |
| entry-number allocation | `docs/drafts/README.md` (not a module; the only allocator) |

## `src/linear_ceiling/`

Infrastructure: `hashing` (canonical sha256) · `rng` · `config` · `pairs` · `seal` · `run_experiment` (E1+ gate
stub: the seal gate, then exit 3) · `screen` (CCA math) · `weights` (safetensors reader) · `lint_scope` ·
`ledger_check` · `upstream_gate`.

E0 (the screen line): `e0` (refuses to read a weight until 0003's rule is committed) · `e0_vocab` (candidate C:
the vocabulary as the calibration set) · `summarize_e0` · `summarize_e0_depth`.

E7 (public traces):

- `e7_traces` — adapters; normalizes tau-bench's per-agent str/dict `arguments` split.
- `e7_tokens` — exact `o200k_base` where a public encoder exists, per-content-type calibrated divisors otherwise
  (ledger 0009).
- `e7_cost` — two-bound timeline. `e7_lanes` — Lane A measured / Lane B cascade.
- `e7_corpus` — loads all three suites into one shape; `LANE_A_ONLY_AGENTS`; unparsed recorded, never dropped.
- `e7_manifest` — the committed corpus manifest `config/e7-manifest.json`: per-file sha256, S3 key/ETag,
  recovered selection rule; `verify_disk` both directions; canonical-JSON sha cited by every E7 entry from 0024
  (`ledger_check` enforces the citation).
- `e7` — gate + driver, `build_report`; refuses if disk != manifest.
- `summarize_e7` — fail-closed; recomputes every recorded value from raw traces via a recursive comparator,
  refuses on tamper or on disk/report/manifest disagreement.
- `e7_swe` (LangChain family + layout-aware `discover_trajectories`) · `e7_rolecontent` (4 variants) · `e7_tau2`
  (ground-truth usage/timestamps).
- `e7_headroom` — entry 0010 measure + rows/summary; `switch_slices` shared with the nulls.
- `e7_null` — entry 0024 overlap null controls: seeded derangement same-family + cross-family role/content draw;
  NOT COMPUTABLE where a null cannot be formed.
- `e7_cache` — entry 0024 H-E7a under registered/request-level x cold/warm denominators; request-level = 0017's
  `paid` for every request, byte-identical prefix vs the preceding request at read_mult.
- `e7_usage` — reported-vs-estimated, per role.
- `e7_taxonomy` — entry 0014's six event classes, each with a measurability rule; H-E7a ratio over the Lane A
  measurable subset.
- `e7_stats` — the ONE pinned quantile convention.

E8 (mapper content shift): `e8_text` (0016 §4 sampling + Qwen tokenizer from the snapshot) · `e8` (gate + driver
by subprocess; never imports kvt) · `summarize_e8`. `config.E8Config.mapper_tag` is the E8 half of entry 0033.

E9 (handoffs):

- `e9_align` — 0019 handoff slices + difflib matched blocks + exclusions (and `[e9.alignment]
  sender_head_truncate` for E-TRUNC).
- `e9` — gate + pre-batch controls + per-handoff dump/score/delete driver, checkpointed.
- `e9_pertoken` — entry 0023 arithmetic: centered delta in R²'s units, oracle f*(tau), seam distance b(t) + fixed
  bins, null pairing, band.
- `summarize_e9` — alignments re-derived from raw traces; R² from recorded moments; per-token squares summed
  against the moments; keep-subset re-scored from fingerprinted tensors; tau recomputed from the archived mapper;
  controls checked; then f*, profiles, band.
- `e9_rescore` — entry 0033: the kept-subset cross arm re-scored with a tagged mapper; the same-model arm is a
  refusing control against 0028's recheck.
- `e9_compare` — the native E9 run against the scaled run of the same handoffs, token by token, and the
  configuration share against the long cell.
- `e9_tail` — the per-token tail beside f*; runs `summarize_e9` first and refuses on anything it refuses.
- `summarize_e9_trunc` — E-TRUNC: the shrinkage pre-check and the paired comparison of the truncation levels on
  the common matched subset; each level is first read by `summarize_e9`.

Every experiment invokes the upstream by subprocess in the upstream's own environment; nothing here imports
`kvt` or copies its code.

## `tests/`

Mirror the modules under `src/` (`tests/test_<module>.py`) and cover the tool drivers (`test_runpod_*`,
`test_consolidation_*`, `test_cache_behavior.py`); synthetic and offline. A few pins need local data and
skip without it (e.g. `LC_REAL_TRACES=1` for `tests/test_e7_sensitivity.py`). `tests/test_imports.py` reserves the
one full upstream sha in `UPSTREAM.md` for `linear_ceiling.UPSTREAM_SHA`.

## `config/`

One TOML per experiment cell (`e0`, `e7`, `e8`, `e8a`, `e8c`, `e8f`, `e8fa`, `e9`, `e9c`, `e9s`, `e9l`, `e9f`, `e9fl`,
`e9t-{full,l65,l49,l32}`, `consolidation`, `cache-behavior`), plus `seal.toml` and the manifests
`e7-manifest.json` and `consolidation-manifest.json`. Seeds and thresholds live here and nowhere else. A config is
registered by a ledger entry and committed unmodified before its run; the gates check its hash, so editing one
after registration makes its experiment refuse.

## `ledger/`

`ledger/ledger.md`: the hypothesis table (the verdict column changes only through a numbered entry with a
`verdict:` line), then the append-only numbered entries, each carrying `prior-entries-sha256`. The chain follows
FILE order, not number order, so an entry can be numbered after staged drafts and appended before them.

## `docs/`

| path | role |
|---|---|
| `docs/handoff/` | dated session briefs, immutable; `HANDOFF.md` is the index and its newest brief is the pick-up target |
| `docs/drafts/` | ordering-guarded `append_00NN.py` scripts for entries not yet written, each running its fail-closed summarizer in-process; `README.md` is the only number allocator and records staged vs appended |
| `docs/reviews/` | dated review and refutation records (claim / attack / evidence / finding / limits) |
| `docs/learnings/` | `LEARNINGS.md`: one non-obvious, re-verifiable fact per dated entry, each with a `re-verify:` line; immutable, superseded by `kills:` |
| `docs/paper/` | paper outlines and seeds; the manuscript source is not in this repository |
| `docs/probes/` | scratch probes entries 0026 and 0028 cite (SDPA memory probe, the shipped candidate module's validation, the matching-platform re-score and its determinism test) |
| `docs/provenance/` | verbatim copies of outside records, with hashes (e.g. the A100 fork's ledger excerpt) |
| `docs/archive/` | superseded READMEs, verbatim |
| `docs/gpu-experiment-protocol.md` | standing GPU rules R1–R12 |
| `docs/*-runbook.md` | one dated runbook per GPU sitting |
| `docs/agent/` | this file and the command reference |

## `tools/`

| path | role |
|---|---|
| `tools/hf_backup.sh` · `tools/hf_verify_backup.py` · `tools/hf_prune_backup.py` | protocol R8: push the verified mirror, verify both directions, repair a mis-push |
| `tools/jupyterhub/` · `tools/ec2/` · `tools/runpod/` | GPU box drivers: JupyterHub-only box from home; rented EC2 over ssh; the second family's RunPod sittings |
| `tools/preflight_pair.py` · `tools/emit_tau.py` | pre-rental checks for a new pair; a family's τ lines from its own E8 report |
| `tools/consolidation/` · `tools/cache_behavior/` | drivers and fail-closed readers for the registered runs of entries 0046 and 0047 |
| `tools/seam_pilot/` · `tools/cache_injection_pilots/` | preserved exploratory pilots; not registered results (see each README) |

## `proofs/`

The Lean 4 formalization of the paper's theory: 0023's statistic (`fstar` is the exact-criterion twin of
`e9_pertoken.f_star`), Theorem 1 (μ = 1 − R̄²), Theorem 2, Corollary 3 (seams), Proposition 4 (attention under
`ass:rope`) and the reported numbers in `Carryover/Numbers.lean`; `Audit.lean` prints the axioms of all 52 headline
results (only `propext`, `Classical.choice`, `Quot.sound`; no `sorry`). Toolchain Lean v4.34.0-rc2 + Mathlib
pinned in `lean-toolchain` / `lake-manifest.json`; build with
`cd proofs && lake exe cache get && lake build && lake env lean Audit.lean`, or `./check.sh` where `lake` is broken
(needs the Mathlib build in `.lake/packages`; ~21 min, mostly loading Mathlib). Not run in CI. "Lean" may be
claimed in the paper only after `lake build` has passed on the committed tree; `.lake/` is git-ignored. Details:
`proofs/README.md`.

## `UPSTREAM.md`

The read-only upstream instrument (`../kv-transfer-replication`): the pinned commit and its re-pin chain, the
second family's pin, and the provenance table of everything borrowed, as `{sourceRepo, filePath, commitSha}`.
Each experiment's gate checks its own recorded pin through `upstream_gate`; one clone is detached per cell
before that cell is re-summarized.
