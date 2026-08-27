# Pre-Fit Prediction of Cross-Model KV Handoff Fidelity — Design Spec

**Date:** 2026-08-26
**Status:** approved design; no experiment in this document has run
**Repo:** `kv-transfer-replication` (this spec extends it; it does not start a new codebase)
**Anchor:** Variant 1 ("the screen and its price"), with Variant 2 promotion at G2 and
Variant 3 degrade at G1 — all three termination states are publishable objects.
**Timeline:** 12 weeks to a submittable draft. Venue decided at week 12, not before.
**Compute:** CPU box (repo's native habitat) for all linear algebra, mapper fits, E0, E4,
E5, E7, the screen itself. GPU access is assumed available from W3 onward (amended
2026-08-26); the initial gates E0 and E1 remain CPU-only by design — the cheap kills
stay cheap regardless of what hardware exists.

*(Seed-level note: the repo line above is superseded by the separate-repo deviation
recorded as ledger entry 0001; every other line stands.)*

---

## 1. Question and hypotheses

**Research question.** When a serving fleet considers moving KV state between models,
which ordered handoffs are worth building can currently only be learned by fitting and
benchmarking every pair — quadratic in models, GPU-hours per pair. Can the achievable
fidelity of a handoff be predicted from the two models' weights plus one calibration
pass, before any mapper is fit — and does that prediction survive contact with the one
quantity that matters, downstream retention?

**Scope sentence — held verbatim in abstract and limitations, never paraphrased:**

> The screen predicts what a linear mapper can achieve; retention asymmetry beyond that
> prediction is measured and attributed receiver-side, not explained.

Two claims and a refusal: (a) the screen computes a *ceiling* — best held-out R² any
linear mapper can reach for an ordered pair and read-out; (b) retention minus that
ceiling leaves a residual, and the asymmetry lives in the residual, demonstrated to be a
receiver property; (c) no mechanism for *why* receivers differ is offered — mechanism
stories are the same-model perturbation-tolerance program the compression literature
owns (KVTuner, HeadQ, NOVA-KV, Ada-KV), and this paper does not enter that arena.

**Hypotheses** (pre-registered in the ledger before any run, in the ledger's house
style; verdicts stated against the rule as written before considering which outcome is
more interesting to report):

- **H-S1 (identity holds on real models).** For a read-out W (target's W_K, W_V),
  predicted fidelity Σρᵢ²cᵢ²/Σcᵢ² from regularized CCA of residual streams matches the
  fitted ridge mapper's **held-out** R² within a tolerance band stated in the ledger
  before E1 runs, on the 0.6B→1.7B pair. The identity is verified exactly on synthetic
  data; E1 is first real-model contact.
- **H-S2 (screen discriminates).** rowspace(W_K) and rowspace(W_V) occupy measurably
  different canonical coordinates, and the predicted R² ordering reproduces the measured
  K>V gap (Run 1 held-out: 0.76 vs 0.55; paper: ~0.2 at 14B→32B). Failure → G1 degrade.
- **H-S3 (chain reaches retention).** Screen-predicted R² rank-correlates with
  floor-normalized retention **across pairs and k** — because held-out R² does (Run 2,
  within-pair: rank correlation +1 across k; in-sample rank-correlates −1), and the
  screen predicts held-out R². The source paper's r = −0.20 is quarantined explicitly as
  an in-sample artifact. Falsification mode: screen predicts fidelity but not retention
  → the contribution becomes the decomposition (symmetric predictable factor + receiver
  residual), stated in the abstract, not conceded to a reviewer.
- **H-S4 (economics load-bearing, not decorative).** Composition (H-C1/C2/C3 as already
  registered in the ledger) and the calibration curve (H-L1–L4) convert the screen from
  a correlation into a build policy: which pairs, which direction, how many calibration
  tokens, n−1 vs n(n−1) mappers.

**Honesty item carried into the draft:** the CCA variance decomposition is textbook
multivariate statistics and the paper says so in one sentence. The contribution is the
sealed pre-fit validation and the build policy, never the theorem.

## 2. Experiment matrix

Ordering is the kill-order: nothing expensive runs before its cheap kill has passed.

| # | experiment | decides | instrument | cost | kill / gate |
|---|---|---|---|---|---|
| E0 | W_K vs W_V canonical coordinates, weights only, all layers, Qwen3 ladder | H-S2 | regularized CCA on downloaded weights; no forward pass | hours, CPU | same coordinates → Variant 3 degrade; screen demoted to exploratory appendix |
| E1 | screen vs fitted mapper, 0.6B→1.7B (Run 2/3 artifacts exist) | H-S1 | CCA of residual streams from existing dumps; compare predicted R² to held-out R² | CPU overnight or one A100 burst | identity misses beyond pre-stated tolerance → report the gap; decomposition becomes the claim |
| E2 | cross-pair main table: ordered pairs across 0.6B/1.7B/4B (+8B stretch) × {W_K, W_V} × k ∈ {1,4,8} — sealed predicted R² vs held-out R² vs floor-normalized retention | H-S1, H-S3 | repo harness extended per pair; screen computed pre-fit, sealed by ledger hash before any mapper for that pair is fit | bulk of A100 budget; dumps dominate | screen orders pairs but not retention → H-S3 falsified, decomposition framing activates |
| E3 | directed residual: retention − predicted ceiling, both directions per pair | asymmetry exhibit | subtraction over E2's table; no new runs | free | residual symmetric → exhibit dies, table stands |
| E4 | WP1 composition (H-C1/C2/C3) | H-S4 | code built + reviewed; needs 4B checkpoint | CPU, days | H-C3 is a bug gate — no composed number is read until it passes |
| E5 | WP2 calibration curve (H-L1–L4) | H-S4 | code built + reviewed; 420-seq dump protocol as amended in ledger (every curve point recomputed from the single 420-seq dump, n=50 included) | CPU, days | none — runs regardless |
| E6 | WP3 length sweep, P = 2048 required, 4096 stretch | supporting; the content-space claim | Run 5 baseline + H-G3 control exist | moderate A100 | H-G2 outcome is itself reportable |
| E7 | trace-replay economics: replay public agent trajectories (SWE-bench verified, terminal-bench, tau-bench) through a cache cost model → invalidation taxonomy + two headroom numbers (transfer-at-switch-points; compaction break-even distribution) | H-E7a/b; the motivation's numbers | CPU-only replay against published cached/uncached pricing; no model runs | CPU, days; hard-capped to the W4–5 window | taxonomy shows switch points rare → transfer headroom immaterial, motivation reverts to fleet-mixing framing; break-even claim dropped if trace compaction events too sparse to estimate |

**Design commitments, fixed now:**

1. **Seal before fitting.** E2's per-pair predictions are hash-committed to the ledger
   before any mapper for that pair is fit. Without the seal the pre-fit claim is
   unfalsifiable. This is the got-away-oracle move transplanted.
2. **Pair-set scope.** Four sizes (0.6B/1.7B/4B/8B) → twelve ordered pairs is the plan
   under the amended GPU assumption (access available from W3). 8B reverts to the
   designated cut only if that assumption fails in practice; six ordered pairs remains
   the floor for rank correlation.
3. **Retention metric frozen.** Floor-normalized HellaSwag at n = 500, seed 0, Wilson
   ±4 pp stated beside every number (protocol A3). No benchmark shopping after results.
4. **Reverse directions are the same dumps with roles swapped** — no new forward passes
   for direction reversal on already-dumped pairs.

## 3. Schedule and gates

A100 bursts are spent only where a big model must run forward; dumps are batched so
each burst produces every dump that model will ever need, once.

| week | work | machine | gate |
|---|---|---|---|
| 1 | **Lit sweep (gated task):** forward citations of arXiv 2608.03893 and 2506.06609; 90-day arXiv cs.LG scan ("cross-model" + "KV cache"); OpenReview check. Budget two hours; verdict recorded in ledger. Then E0; commit untracked `docs/handoff/` + `docs/learnings/`; build seal-protocol code | CPU | **G1:** W_K/W_V coordinates separate? no → Variant 3, re-scope W2+ |
| 2 | E1 with tolerance band pre-stated in ledger | CPU | E1 verdict recorded either way |
| 3–4 | 4B checkpoint + dumps (8B if budget healthy); reverse-direction fits on existing 0.6B/1.7B dumps | A100 bursts + CPU | dump alignment checks per Run 1 protocol |
| 4–5 | E4 + E5 + E7 in parallel with dumping (E7 hard-capped to this window; unfinished taxonomy ships as partial with its coverage stated) | CPU | H-C3 bug gate; E7 trace-coverage floor per ledger entry 0005 |
| 6 | First E2 pairs: sealed predictions vs held-out R² vs retention | CPU + A100 (HellaSwag) | **G2 (midpoint):** E1 in tolerance AND screen ordering retention on first two pairs → Variant 2 promotion (abstract leads with the decomposition); else ship-as-is framing locked |
| 7–8 | E2 full table; E3 residual subtraction | A100 for retention runs | 8B stretch = designated cut |
| 9 | E6, P = 2048 required | A100 | **G3:** results complete; writing starts regardless of stretch status |
| 10–11 | Draft in CSL structure; adversarial pass on the three load-bearing claims (repo's pattern); every number recomputed from `results/` by a summarize script | — | fail-closed summarizers |
| 12 | Related-work primary-source verification; figures; venue decision | — | submit-ready draft |

Weeks 3–5 are the risk concentration: an A100 slip cascades, which is why E4/E5 occupy
the same window on CPU — the degrade path stays fully productive through a GPU drought.
The venue decision is deliberately last: G2's outcome legitimately changes which venue
the paper belongs to, and the CSL-format draft ports to either.

Division of labor is unassigned here; the natural seam is screen/theory vs
harness/economics.

## 4. Risks and positioning

**Positioning — papers that must be beaten, one-sentence delta each (all require
primary-source verification in week 12 before any citation ships):**

| paper | their claim | our delta |
|---|---|---|
| Chen et al. (NeurIPS '25 spotlight) | feature transferability is heterogeneous — post hoc, correlational | closed-form prediction from weights **before** anything is built, sealed pre-fit. If this sentence stops being true the paper dies; checked week 1, not week 10 |
| Oozeer et al. (2503.04429) | affine mappers often lose to nonlinear | a boundary, not a counter: the screen predicts the *linear* ceiling; pairs where linearity fails should be pairs the screen prices low — itself testable |
| NVIDIA source (2608.03893) | R² doesn't predict retention (r = −0.20) | solves their Future Work 2; quarantines r = −0.20 as an in-sample artifact, citing Run 2 |
| DroidSpeak | receiver layer-sensitivity, measured empirically per pair | pre-fit, from weights |
| KVTuner / HeadQ / NOVA-KV / Ada-KV | same-model perturbation tolerance | never entered: cross-model, read-out-conditioned, no mechanism claims (scope sentence) |
| CKA / SVCCA / Procrustes / Platonic | representation similarity indices | invariant to exactly the maps that matter; silent on read-outs and behavior |

**Risk register, ranked by expected damage:**

| risk | likelihood | mitigation |
|---|---|---|
| Regularized-CCA instability on anisotropic residual streams (outlier dims; hidden 1024–4096 across ladder) | high — most likely technical failure | regularization sweep reported, not tuned-and-hidden; shrinkage estimator fallback |
| H-S3 fails cross-pair (screen orders fidelity, not retention) | moderate | decomposition framing pre-planned; abstract written to survive it |
| E0 kills discrimination | low–moderate | Variant 3 degrade fully specified (E4 + E5 + held-out predictor + E6) |
| Field turnover — literature cycles monthly | certain, magnitude unknown | week-1 gated lit sweep (Section 3) |
| GPU assumption fails after W3 (amended: access assumed, not guaranteed) | low–moderate | CPU-productive window (E4/E5/E7) absorbs a slip; 8B reverts to designated cut; schedule structure unchanged |

**Termination states, all publishable:** Variant 2 (decomposition-led, if G2 promotes) ·
Variant 1 (screen + price, the default) · Variant 3 (honest economics: composition +
calibration curve + held-out predictor + length, if G1 kills the screen).

---

# Appendix B — Paper title (confirmed)

**"The Linear Ceiling: Predicting Cross-Model KV Cache Transfer Before Fitting the
Mapper."** The head term names the paper's object and encodes the scope discipline — a
ceiling is by definition not an explanation of what falls short of it. The subtitle
carries the falsifiable claim and reviewers' search terms; "handoff" is our coinage and
stays out of the title. If G2 promotes, the title flexes to "The Linear Ceiling and the
Receiver's Floor: …" — earned only if E3's residual is clean. The directed-residual
line (fidelity symmetric, retention directional, gap receiver-side) is the reveal: body,
never title.
