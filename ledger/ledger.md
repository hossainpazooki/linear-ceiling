# Ledger — linear-ceiling

House style, borrowed with provenance {sourceRepo: kv-transfer-replication, filePath:
docs/ledger.md, commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: hypotheses are
pre-registered before any run; verdicts are stated against the rule as written, before
considering which outcome is more interesting to report; entries are numbered, dated and
immutable — an amendment is a new entry, never an edit; status tags are `[VALIDATED]`
(ran, and survived an independent attempt to refute it), `[BASELINE]` (ran; numbers here),
`[STRETCH]` (designed, not run), `[FUTURE]` (not designed), `[SUPERSEDED]`.

**Nothing in this repository has run.** Every verdict below is `unresolved`.

## Hypotheses (pre-registered; verdict column is the only cell that ever changes, and only via a numbered entry)

| id | statement (H-S1–H-S4: verbatim from docs/2026-08-26-kv-handoff-screen-design.md §1, less the bold **H-Sn (…).** id prefix, dropped because the id is already this row's first column; H-E7a/H-E7b: verbatim from the "Ledger entry 0005 (register verbatim)" text in Appendix C of docs/2026-08-26-seed-w1.md, which does not appear in §1) | decided by | verdict |
|---|---|---|---|
| H-S1 | (identity holds on real models) For a read-out W (target's W_K, W_V), predicted fidelity Σρᵢ²cᵢ²/Σcᵢ² from regularized CCA of residual streams matches the fitted ridge mapper's **held-out** R² within a tolerance band stated in the ledger before E1 runs, on the 0.6B→1.7B pair. The identity is verified exactly on synthetic data; E1 is first real-model contact. | E1 (tolerance band: a numbered entry before E1 runs) | unresolved |
| H-S2 | (screen discriminates) rowspace(W_K) and rowspace(W_V) occupy measurably different canonical coordinates, and the predicted R² ordering reproduces the measured K>V gap (Run 1 held-out: 0.76 vs 0.55; paper: ~0.2 at 14B→32B). Failure → G1 degrade. | E0 (first clause; rule in entry 0003), E1 (second clause) | unresolved |
| H-S3 | (chain reaches retention) Screen-predicted R² rank-correlates with floor-normalized retention **across pairs and k** — because held-out R² does (Run 2, within-pair: rank correlation +1 across k; in-sample rank-correlates −1), and the screen predicts held-out R². The source paper's r = −0.20 is quarantined explicitly as an in-sample artifact. Falsification mode: screen predicts fidelity but not retention → the contribution becomes the decomposition (symmetric predictable factor + receiver residual), stated in the abstract, not conceded to a reviewer. | E2 | unresolved |
| H-S4 | (economics load-bearing, not decorative) Composition (H-C1/C2/C3 as already registered in the ledger) and the calibration curve (H-L1–L4) convert the screen from a correlation into a build policy: which pairs, which direction, how many calibration tokens, n−1 vs n(n−1) mappers. | E4, E5 | unresolved |
| H-E7a | switch-point frequency × recoverable prefill cost makes transfer headroom material (threshold: define the materiality cutoff in entry 0005's successor before replay). | E7 | unresolved |
| H-E7b | the compaction break-even distribution has substantial negative mass at current pricing (threshold: define before replay). | E7 | unresolved |

Gates: **G1** (W1) = H-S2 first clause via E0. **G2** (W6) = H-S1 in tolerance AND screen
ordering retention on the first two E2 pairs. **G3** (W9) = results complete.

## Entries

### 0001 — 2026-08-26 — Repo-split deviation from the design spec

The design spec (docs/2026-08-26-kv-handoff-screen-design.md, header line "Repo") says it
extends `kv-transfer-replication` and does not start a new codebase. Decision, superseding
that line and nothing else: **`linear-ceiling` is a separate public repository that depends
on the upstream pinned at one commit** (UPSTREAM.md: `f3594458f73d70a15f195c863d52ea6592f61578`).

Rationale: the screen, the seal, the ledger and the orchestration are new objects with their
own invariants (sealed pre-fit predictions, immutable entries, fail-closed summarizers) and
their own CI; the upstream is a finished replication whose ledger and artifacts are the
evidence E1 compares against. Keeping the instrument read-only and pinned makes "the screen
was computed before the fit" auditable from history rather than from a claim: nothing in
this repo can write a mapper into the upstream tree, and every number borrowed from it
carries `{sourceRepo, filePath, commitSha}`. Fitting, injection and evaluation stay upstream
and are invoked by subprocess in the upstream's environment (W2+), never vendored.

Scope for W1 (this entry is the scope record the runner stub cites): seal protocol, screen
math, E0, entries 0001–0005. E1 and beyond, forward passes, GPU code, dump formats are out.

### 0002 — 2026-08-26 — H-S1..H-S4 registered; references pinned; the post-fit exception

H-S1..H-S4 are registered in the table above, verbatim from the spec, verdicts `unresolved`.

Reference numbers cited by H-S2 and H-S3, recomputed from the upstream ledger at the pin
{sourceRepo: kv-transfer-replication, filePath: docs/ledger.md, commitSha:
f3594458f73d70a15f195c863d52ea6592f61578} rather than restated from the spec's rounding:

- H-S2's "Run 1 held-out: 0.76 vs 0.55" is the **best held-out cell** of the single-source
  OLS probe on Qwen3-0.6B→1.7B: K_stripped 0.7606 at (src 0, tgt 0), V 0.5473 at
  (src 19, tgt 19). Diagonal-mean held-out: K_stripped 0.6284, V 0.4361 (gap +0.192).
  Statistic matters: E1's comparison must name which of the two it targets.
- H-S3's "Run 2 within-pair rank correlation +1 across k" is the joint Run 2/Run 4 table:
  held-out K R² 0.6814 / 0.5907 / 0.0984 at k = 1/4/8 against floor-normalized HellaSwag
  retention ordered the same way (in-sample 0.7783 / 0.8816 / 0.9607 orders it the
  opposite way). n = 500, seed 0, Wilson ±4 pp.

**Post-fit exception (decision D2).** At the pin the upstream already holds fitted mappers
for `qwen3-0.6b-to-1.7b` (`mappers/qwen3-0.6b-to-1.7b/k{1,4,8}.safetensors`, `rope/k1`, and
`results/mapper/qwen3-0.6b-to-1.7b/r2.json`), so no prediction for that pair can ever be
sealed pre-fit. The seal therefore has a second, explicitly inferior kind of record:
`sealed_pre_fit: false` with the pre-existing artifacts listed. Only the E1 identity check
may consume it (`allow_post_fit=True`); E2 refuses it. E1 on this pair is a test of the
theorem on real activations, not a pre-fit claim, and will be reported as such. Evidence
that the guard fires on the real tree (seal writer, 2026-08-26):

```
SEAL VIOLATION: fitted mapper artifact(s) already exist for qwen3-0.6b-to-1.7b; a prediction written now would not be pre-fit:
  C:/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.safetensors
  C:/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k4.safetensors
  C:/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k8.safetensors
  C:/Users/hossa/dev/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/rope/k1.safetensors
  C:/Users/hossa/dev/kv-transfer-replication/results/mapper/qwen3-0.6b-to-1.7b/r2.json
  C:/Users/hossa/dev/kv-transfer-replication/results/mapper/qwen3-0.6b-to-1.7b/rope/r2.json
```

### 0005 — 2026-08-26 — E7 registered; gap map committed; compute assumption amended

The gap-map prose is committed verbatim as docs/gap-map.md; the registered entry
block below it is the verbatim "Ledger entry 0005 (register verbatim)" text from
Appendix C of docs/2026-08-26-seed-w1.md (the design spec,
docs/2026-08-26-kv-handoff-screen-design.md, has no Appendix C — it ends at
Appendix B). Entry text, verbatim:

**0005 — E7 registered; gap map committed; compute assumption amended.**

- **E7 (trace-replay economics).** Replay public agent trajectories through a cache
  cost model. Outputs: (i) invalidation taxonomy with event frequencies per trace
  suite; (ii) transfer headroom at model-switch points, in dollars per trajectory,
  under published cached/uncached pricing; (iii) compaction break-even distribution.
  CPU-only. Hard-capped to the W4–5 window; if incomplete, ships as partial with trace
  coverage stated. Trace-coverage floor: set the minimum trajectory count per suite
  here, before replay begins, and do not lower it after seeing data.
- **H-E7a:** switch-point frequency × recoverable prefill cost makes transfer headroom
  material (threshold: define the materiality cutoff in this entry before replay).
- **H-E7b:** the compaction break-even distribution has substantial negative mass at
  current pricing (threshold: define before replay).
- **Kill conditions:** switch points rare → motivation reverts to fleet-mixing framing,
  H-E7a resolved negative and reported. Compaction events too sparse → H-E7b dropped
  as unestimable, stated, not silently omitted.
- **Compute amendment:** GPU access assumed available from W3 onward. 8B promoted from
  stretch to plan (twelve ordered pairs); reverts to designated cut only if the
  assumption fails. E0/E1 remain CPU-only gates regardless.
- **Provenance rule for E7:** every pricing figure carries its source and retrieval
  date; every trace suite carries its version/commit. No number ships without both.

The registered wording above says the materiality cutoff and the H-E7b threshold are
defined "in this entry" — no threshold is in fact set here. That instruction is carried
forward: a successor numbered entry sets the trace-coverage floor and both thresholds
before any E7 replay begins (W4), because setting them requires the W1 lit sweep's
pricing verification, a human task outside this repo's sessions. This paragraph records
a divergence from the registered wording, not a correction of it: the registered text
above stands as written; this note is the amendment.

### 0003 — 2026-08-26 — E0 operationalization C (vocabulary-paired screen) and the G1 decision rule

Chosen by Hossain from the three candidates presented on 2026-08-26. Read-out for E0 is the rows of
`k_proj` / `v_proj` scaled by the layer's `input_layernorm` gain (pre-`k_norm`; decision D4; the
H-S1-on-K consequence is a W2 item, flagged, not resolved).

Instrument, per ordered pair (S→T) in the ladder and per λ in reg_sweep = {1e-3, 1e-2, 1e-1}:
X = RMS-normalised rows of E_S, Y = RMS-normalised rows of E_T, paired by token id after
`assert_shared_vocab`; `regularized_cca(X, Y, λ, λ)`; for each target layer l,
R_K = diag(g_l) W_K^{lᵀ}, R_V = diag(g_l) W_V^{lᵀ}; R²_K(l), R²_V(l) = `predicted_r2`.
Δ(l) = R²_K(l) − R²_V(l). Reported per layer, per λ, per pair; never averaged across layers
except in the two statistics the rule names.

Rule, per pair: med = median over target layers of Δ(l); frac = fraction of layers with Δ(l) > 0.
- SEPARATE if, at every λ in the sweep, med ≥ delta_separate = 0.05 and frac ≥ layer_fraction = 0.67.
- SAME if, at every λ, |med| < delta_same = 0.02.
- otherwise UNRESOLVED (including sign flips across λ, which are reported as such).
Ladder verdict over pair_scope = "all" ordered pairs among the required models (six pairs):
SEPARATE only if every pair is SEPARATE; SAME if any pair is SAME; otherwise UNRESOLVED. Pairs
involving 8B are reported if present and do not enter the verdict. Direction of Δ matters: the
rule is written for K > V (Run 1's ordering, entry 0002); a robust V > K would be reported as
UNRESOLVED-with-inverted-sign, not as SEPARATE.
G1 semantics as in the candidate text: SEPARATE → proceed (H-S2 first clause held on the
vocabulary proxy; the second clause still awaits E1). SAME → Variant 3 degrade. UNRESOLVED →
recorded; E1 decides.

Known limits, stated before running: layer-0 embedding stands in for every layer's residual
stream, so depth-dependent nulls are the proxy's, and a uniform token prior is used. Neither
is tuned after seeing results.

Thresholds frozen in config/e0.toml at this commit. Seed 0. No weight had been read by this
repository when this entry was written.
