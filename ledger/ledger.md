# Ledger — linear-ceiling

House style, borrowed with provenance {sourceRepo: kv-transfer-replication, filePath:
docs/ledger.md, commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: hypotheses are
pre-registered before any run; verdicts are stated against the rule as written, before
considering which outcome is more interesting to report; entries are numbered, dated and
immutable — an amendment is a new entry, never an edit; status tags are `[VALIDATED]`
(ran, and survived an independent attempt to refute it), `[BASELINE]` (ran; numbers here),
`[STRETCH]` (designed, not run), `[FUTURE]` (not designed), `[SUPERSEDED]`.

E0 has run (entry 0004); H-S2's first clause is `NOT CONFIRMED`. Every other verdict below is
`unresolved`. The screen-validation line is CLOSED and E7 is promoted to a standalone
measurement program with pre-registered thresholds (entry 0006, 2026-09-01) — H-S1/H-S3/H-S4
are shelved-not-decided, and only E7 has a live path to a verdict.

## Hypotheses (pre-registered; verdict column is the only cell that ever changes, and only via a numbered entry)

| id | statement (H-S1–H-S4: verbatim from docs/2026-08-26-kv-handoff-screen-design.md §1, less the bold **H-Sn (…).** id prefix, dropped because the id is already this row's first column; H-E7a/H-E7b: verbatim from the "Ledger entry 0005 (register verbatim)" text in Appendix C of docs/2026-08-26-seed-w1.md, which does not appear in §1) | decided by | verdict |
|---|---|---|---|
| H-S1 | (identity holds on real models) For a read-out W (target's W_K, W_V), predicted fidelity Σρᵢ²cᵢ²/Σcᵢ² from regularized CCA of residual streams matches the fitted ridge mapper's **held-out** R² within a tolerance band stated in the ledger before E1 runs, on the 0.6B→1.7B pair. The identity is verified exactly on synthetic data; E1 is first real-model contact. | E1 (tolerance band: a numbered entry before E1 runs) | unresolved |
| H-S2 | (screen discriminates) rowspace(W_K) and rowspace(W_V) occupy measurably different canonical coordinates, and the predicted R² ordering reproduces the measured K>V gap (Run 1 held-out: 0.76 vs 0.55; paper: ~0.2 at 14B→32B). Failure → G1 degrade. | E0 (first clause; rule in entry 0003), E1 (second clause) | NOT CONFIRMED |
| H-S3 | (chain reaches retention) Screen-predicted R² rank-correlates with floor-normalized retention **across pairs and k** — because held-out R² does (Run 2, within-pair: rank correlation +1 across k; in-sample rank-correlates −1), and the screen predicts held-out R². The source paper's r = −0.20 is quarantined explicitly as an in-sample artifact. Falsification mode: screen predicts fidelity but not retention → the contribution becomes the decomposition (symmetric predictable factor + receiver residual), stated in the abstract, not conceded to a reviewer. | E2 | unresolved |
| H-S4 | (economics load-bearing, not decorative) Composition (H-C1/C2/C3 as already registered in the ledger) and the calibration curve (H-L1–L4) convert the screen from a correlation into a build policy: which pairs, which direction, how many calibration tokens, n−1 vs n(n−1) mappers. | E4, E5 | unresolved |
| H-E7a | switch-point frequency × recoverable prefill cost makes transfer headroom material (threshold: define the materiality cutoff in entry 0005's successor before replay). | E7 | unresolved |
| H-E7b | the compaction break-even distribution has substantial negative mass at current pricing (threshold: define before replay). | E7 | unresolved |

Gates: **G1** (W1) = H-S2 first clause via E0 — decided SAME (entry 0004). **G2** (W6) and
**G3** (W9) are retired with the screen line (entry 0006); the live gates are entry 0006's
day-2 and numbers-freeze gates.

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

### 0004 — 2026-08-26 — E0 verdict `[VALIDATED]`

Run: `.venv/Scripts/python.exe -m linear_ceiling.e0 --config config/e0.toml`, operationalization
C, seed 0, package 0.0.1, upstream f3594458f73d70a15f195c863d52ea6592f61578, config/e0.toml
sha256 9814b08d610ce29839cb603b542ffc9419d6e91a949ac290577ff3c347772cd3. Models: 0.6B, 1.7B, 4B
(all six required ordered pairs; no 8B units present). Entry 0003 (the rule) and config/e0.toml
were committed together as `2361c72` at 2026-08-26 17:33:05-04:00; the earliest required-unit
result on disk (qwen3-0.6b-to-1.7b.json) carries a write timestamp of 17:50:05, seventeen
minutes later, and the latest required unit (qwen3-4b-to-1.7b.json / verdict.json) is timestamped
18:17:09 -- confirming entry 0003's own claim that no weight had been read when the rule was
frozen. Wall-clock across the six required units: ~27 minutes (17:50:05-18:17:09), including
per-pair weight downloads.

| pair | tokens | median delta (frac K>V) per lambda 0.001 / 0.01 / 0.1 | verdict |
|---|---|---|---|
| qwen3-0.6b-to-1.7b | 151936 | +0.0193 (1.00) / +0.0192 (1.00) / +0.0175 (1.00) | SAME |
| qwen3-0.6b-to-4b | 151936 | +0.0109 (0.97) / +0.0108 (0.97) / +0.0099 (0.97) | SAME |
| qwen3-1.7b-to-0.6b | 151936 | +0.0062 (0.79) / +0.0062 (0.79) / +0.0065 (0.86) | SAME |
| qwen3-1.7b-to-4b | 151936 | +0.0043 (0.72) / +0.0044 (0.72) / +0.0046 (0.81) | SAME |
| qwen3-4b-to-0.6b | 151936 | +0.0074 (0.82) / +0.0074 (0.82) / +0.0076 (0.93) | SAME |
| qwen3-4b-to-1.7b | 151936 | +0.0108 (0.93) / +0.0107 (0.93) / +0.0103 (0.93) | SAME |

ladder verdict: **SAME** (required units: qwen3-0.6b-to-1.7b, qwen3-0.6b-to-4b,
qwen3-1.7b-to-0.6b, qwen3-1.7b-to-4b, qwen3-4b-to-0.6b, qwen3-4b-to-1.7b)

verdict.json sha256: 59fd962f92788eb4323594226e053ce121fe4ba17a1e821af0f9a43409e0c3bf

**Verdict against the rule as written in entry 0003: SAME.** Applying the per-pair rule (SAME
iff |med| < delta_same = 0.02 at every lambda in the sweep) to each row above: every pair
satisfies it at all three lambdas, so all six per-pair verdicts are SAME, and the ladder rule
("SAME if any pair is SAME") makes the ladder verdict SAME. No pair reaches the SEPARATE bar
(med >= 0.05 and frac >= 0.67 at every lambda); none is UNRESOLVED or sign-flipped. Both halves
of the result: the sign is consistent K>V on every pair at every lambda (all medians positive,
frac_positive 0.72-1.00, matching Run 1's ordering from entry 0002) -- but the magnitude sits
well under the SAME bar rather than on a boundary. qwen3-0.6b-to-1.7b (+0.0193) is the only pair
close to the 0.02 line, at 96.5% of it; the other five range from 54.5% of the threshold
(+0.0108/+0.0109) down to 21.5% of it (+0.0043). This is a comfortable SAME carried by every
pair, not a close vote.

**Independent checks (cited, not re-derived here):**
- *Determinism.* A first invocation of `linear_ceiling.e0` was killed mid-run by a tool timeout
  after completing qwen3-0.6b-to-1.7b; the later full run recomputed that pair byte-identically
  to full float precision (medians 0.019341651670144205 / 0.019157713844428076 /
  0.017489865798854545, frac_positive 1.0, verdict SAME). Two independent invocations, identical
  output.
- *Independent recomputation of one cell*, on a path using neither `e0_vocab.analyze_pair` nor
  `screen.py`: raw safetensors read directly, own RMS normalisation, chunked float64 normal
  equations, pooled R^2 per definition A5. For qwen3-0.6b-to-1.7b, target layer 0, K read-out:
  independent pooled OLS R^2 (lambda=0) = 0.661176, against the artifact's screen-predicted
  r2_K = 0.660187 at lambda=1e-3 (diff -0.000989), 0.651449 at lambda=1e-2 (diff -0.009727),
  0.576301 at lambda=1e-1 (diff -0.084875): the gap is ~1e-3 at the smallest lambda and grows
  monotonically with lambda in the direction regularization predicts. This verifies the screen's
  computation against in-sample OLS on the same vocabulary data on real 151,936x1024 matrices,
  not only synthetic data. It is NOT H-S1, which requires matching a fitted mapper's held-out R^2
  on residual streams -- that is E1's job in W2.
- `linear_ceiling.summarize_e0` reruns clean (exit 0) against the committed artifacts,
  reproducing this table and the verdict.json sha256 above.

**G1 consequence:** SAME -> the screen is killed at G1 per entry 0003's rule; the Variant 3
degrade path activates. This is the rule's dictated consequence, not a recommendation.

**Known limits (entry 0003), bearing on this verdict:** the layer-0 embedding stands in for
every layer's residual stream, and a uniform token prior is used, in this operationalization. A
SAME verdict on this vocabulary proxy is a claim about rowspace(W_K) vs rowspace(W_V) as seen
through shared-vocabulary embeddings paired at layer 0 -- it is not a SAME verdict on residual
streams, and does not by itself settle H-S1 or H-S2's second clause, both of which remain E1's
job.

H-S2's verdict cell is set to `NOT CONFIRMED` by this entry (first clause; decided by E0 per
entry 0003's assignment). H-S1, H-S3, H-S4, H-E7a, H-E7b are unchanged.

Tag: `[VALIDATED]` -- determinism reproduced across two independent invocations, the independent
recomputation agrees with the screen's own computation to ~1e-3 at the smallest lambda, and
`summarize_e0` (fail-closed) ran clean against the committed artifacts.

### 0006 — 2026-09-01 — Program re-scope: screen line closed, depth structure recorded, E7 promoted with thresholds

**Operator decision (Hossain, 2026-09-01).** The screen-validation line (E1, E2, E3, E4, E5,
E6 as validators of the screen) is CLOSED at end of W1, on opportunity-cost grounds: the
niche's mechanism lane is crowded with top-track work while the measurement lane is open
(evidence in docs/handoff and session records of 2026-08-31). The E0 verdict from entry 0004
STANDS exactly as the frozen rule returned it; entry 0003 is untouched, per house style.
H-S1, H-S3, and H-S4 remain `unresolved` -- shelved, not decided: no experiment that decides
them has run, and none will run under this program. Their verdict cells are deliberately NOT
changed by this entry, because the verdict vocabulary records what experiments decided, and
no experiment decided these. D2, D3, D4 (handoff 2026-08-26, section 5) are moot with the
screen line closed and remain unruled. Gates G2 and G3 are retired with the line they gated.

**Depth structure of the E0 result `[BASELINE]`.** What entry 0004's median table does not
carry: the per-layer Delta(l) distribution. Recomputed from results/e0/ by
`python -m linear_ceiling.summarize_e0_depth` (fail-closed: inherits summarize_e0's hash,
NaN, and recorded-vs-recomputed checks; p90 is numpy default linear-interpolation
percentile), output verbatim:

| pair | n layers | median | p90 | max | layers with delta >= 0.05 (= delta_separate) |
|---|---|---|---|---|---|
| qwen3-0.6b-to-1.7b | 28 | +0.0193 | +0.1077 | +0.1212 | 7 -- layers 0, 22-27 |
| qwen3-0.6b-to-4b | 36 | +0.0109 | +0.0654 | +0.0776 | 5 -- layers 0, 31-34 |
| qwen3-1.7b-to-0.6b | 28 | +0.0062 | +0.0624 | +0.0740 | 5 -- layers 0, 24-27 |
| qwen3-1.7b-to-4b | 36 | +0.0043 | +0.0498 | +0.0682 | 4 -- layers 0, 32-34 |
| qwen3-4b-to-0.6b | 28 | +0.0074 | +0.0706 | +0.0828 | 5 -- layers 0, 24-27 |
| qwen3-4b-to-1.7b | 28 | +0.0108 | +0.0975 | +0.1244 | 6 -- layers 0, 23-27 |

Exceedance layer sets are identical at every lambda in the sweep (checked by the summarizer,
not asserted). verdict.json sha256
59fd962f92788eb4323594226e053ce121fe4ba17a1e821af0f9a43409e0c3bf, matching entry 0004. In
every pair the layers exceeding delta_separate are the first block and the last four to six
blocks; the middle of the network drags the median under delta_same. Entry 0003
pre-registered the reason this may not be real ("depth-dependent nulls are the proxy's"), so
two readings remain live -- real end-of-network K/V separation, or the layer-0 proxy
degrading with depth -- and E0 cannot distinguish them. With the screen line closed, no
in-program experiment will decide it; this entry records the finding so it survives the
untracked results/ tree, with both readings open.

**E7 promoted to a standalone measurement program.** Registered outputs unchanged from entry
0005: (i) invalidation taxonomy with event frequencies per trace suite; (ii) transfer
headroom at model-switch points, in dollars per trajectory, under published cached/uncached
pricing; (iii) compaction break-even distribution. Anchor venue: MLSys 2027 (submissions due
2026-10-30). Optional feedback stop: LCFM workshop at NeurIPS 2026 (deadline 2026-09-10 AoE;
non-archival; concurrent submission explicitly permitted), taken only if the day-2 gate below
passes. Candidate trace suites, subject to the coverage floor: SWE-bench leaderboard
trajectories (required of submissions since July 2024), tau-bench historical_trajectories,
Terminal-Bench 2.0 runs.

**Thresholds, set before any replay (per entry 0005's carried-forward instruction):**

- **Trace-coverage floor:** at least 50 trajectories per suite and at least 2 suites before
  any frequency claim ships as a finding; anything below ships labeled partial with its
  coverage stated, per entry 0005's kill conditions.
- **Materiality cutoff (decides H-E7a):** transfer headroom is material iff recoverable
  prefill spend at switch points is >= 10% of the trajectory set's total input-token spend at
  the pinned pricing below, in at least one lane (A or B, reported separately). Below 10% in
  both lanes resolves H-E7a negative, and per entry 0005 the motivation reverts to
  fleet-mixing framing.
- **Substantial-negative-mass threshold (decides H-E7b):** satisfied iff >= 25% of compaction
  events (measured, or policy-inserted under Lane B) are net-cost-negative at the pinned
  pricing. Too-sparse compaction events resolve H-E7b unestimable, stated, per entry 0005.
- **Pricing pins (provenance per entry 0005's rule; both retrieved 2026-09-01):** Anthropic
  prompt-caching documentation (platform.claude.com/docs/en/build-with-claude/prompt-caching):
  cache read 0.1x base input, cache write 1.25x (5-minute TTL) or 2.0x (1-hour TTL). OpenAI
  prompt-caching guide (developers.openai.com/api/docs/guides/prompt-caching): GPT-5.6+ cache
  read 0.1x, cache write 1.25x, retention ~30 minutes after last use. Independent
  corroboration: arXiv 2607.19214 measures r=0.10, w=1.25 for Anthropic. Any replay under
  different pricing re-pins with a new retrieval date in a successor entry.

**Switch-point design choice, frozen before replay.** Two lanes, never merged:

- **Lane A (measured):** a switch point is counted only where trajectory metadata records the
  serving model per step and it changes mid-trajectory. Probe of 2026-09-01 (SWE-bench
  experiments repo, tau-bench repo): public trajectories record the model per RUN, not per
  step, so Lane A is expected sparse to absent -- and a zero count in Lane A IS the premise
  finding (the cross-model transfer literature's motivating premise is unevidenced in public
  agent workloads), reported as such, not padded.
- **Lane B (counterfactual):** switch points inserted under a pre-registered two-tier cascade
  policy -- planning/reasoning turns on the large tier, tool-execution turns on the small
  tier; every tier boundary is a switch point. All Lane B headroom is labeled
  counterfactual-under-stated-policy. No third lane or alternative policy may be added after
  seeing data; a different policy requires a new numbered entry registered before its replay.

**Gates for the LCFM sprint (the MLSys program does not depend on them):**

- **Day-2 gate, EOD 2026-09-03:** (i) at least one suite's trajectories downloaded and
  parsed; (ii) a replay skeleton computes per-trajectory token/cost timelines on at least 10
  trajectories; (iii) both lanes implemented in the parser. Any miss: skip LCFM, continue to
  MLSys unchanged.
- **Numbers-freeze gate, EOD 2026-09-08:** the 4-page submission may contain only numbers
  that recompute clean from results/ via a fail-closed summarizer, in the pattern of
  summarize_e0. Scope cap: Lane A/B premise numbers and the taxonomy; the transfer-fidelity
  leg and compaction break-even appear only if they clear the same gate.

E7 replay must not begin until this entry is committed and unmodified; the replay harness
must enforce this the way linear_ceiling.e0's assert_ready enforced entry 0003 (requirement
registered here; enforcement lands with the harness).
