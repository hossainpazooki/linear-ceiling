# Ledger — linear-ceiling

House style, borrowed with provenance {sourceRepo: kv-transfer-replication, filePath:
docs/ledger.md, commitSha: f3594458f73d70a15f195c863d52ea6592f61578}: hypotheses are
pre-registered before any run; verdicts are stated against the rule as written, before
considering which outcome is more interesting to report; entries are numbered, dated and
immutable — an amendment is a new entry, never an edit; status tags are `[VALIDATED]`
(ran, and survived an independent attempt to refute it), `[BASELINE]` (ran; numbers here),
`[STRETCH]` (designed, not run), `[FUTURE]` (not designed), `[SUPERSEDED]`.

State of the table (regenerated from the cells; each cell names the entry that set it): H-S2's
first clause is `NOT CONFIRMED` (entry 0004, E0); H-S1/H-S3/H-S4 carry `SHELVED` (entry 0007 —
no experiment decided them; none is scheduled; the screen-validation line is CLOSED, entry
0006); H-E7a is `NOT CONFIRMED` (entry 0015; corrected figures 0018; tokenizer sensitivity
0022) and H-E7b `UNESTIMABLE` (entry 0015); H-E8 is `NOT CONFIRMED` (entry 0020); H-E9 is
`unresolved` (registered 0019, rule amended 0023 — gated, awaiting its run). From entry 0007 on, each entry
records a `prior-entries-sha256:` over the entries section above it; from entry 0024 on, an
entry that changes a verdict cell carries a machine-readable line `verdict: H-XX = <VERDICT>`
(the cells above are otherwise frozen in `ledger_check.VERDICT_PROVENANCE`), and an entry that
cites `summarize_e7` figures carries `e7-manifest-sha256: <sha>` naming the committed corpus
manifest — all recomputed by `ledger_check` in CI, which also refuses any edit to an entry
block already committed at the base revision (the trailing entry included).
Dating erratum: entries 0016-0020 were authored 2026-09-01 despite their 2026-09-02 headings — see entry 0021.
Rule amendment: the H-E9 row below embeds entry 0019's rule clause (pooled K R², 0.70/0.40) in its
statement cell; that clause is superseded by entry 0023 (median oracle selective-recompute fraction
f*(τ_K), 0.15/0.50) and the cell text is left as registered under the house rule that only the verdict
cell changes.

## Hypotheses (pre-registered; verdict column is the only cell that ever changes, and only via a numbered entry)

| id | statement (H-S1–H-S4: verbatim from docs/2026-08-26-kv-handoff-screen-design.md §1, less the bold **H-Sn (…).** id prefix, dropped because the id is already this row's first column; H-E7a/H-E7b: verbatim from the "Ledger entry 0005 (register verbatim)" text in Appendix C of docs/2026-08-26-seed-w1.md, which does not appear in §1) | decided by | verdict |
|---|---|---|---|
| H-S1 | (identity holds on real models) For a read-out W (target's W_K, W_V), predicted fidelity Σρᵢ²cᵢ²/Σcᵢ² from regularized CCA of residual streams matches the fitted ridge mapper's **held-out** R² within a tolerance band stated in the ledger before E1 runs, on the 0.6B→1.7B pair. The identity is verified exactly on synthetic data; E1 is first real-model contact. | E1 (tolerance band: a numbered entry before E1 runs) | SHELVED |
| H-S2 | (screen discriminates) rowspace(W_K) and rowspace(W_V) occupy measurably different canonical coordinates, and the predicted R² ordering reproduces the measured K>V gap (Run 1 held-out: 0.76 vs 0.55; paper: ~0.2 at 14B→32B). Failure → G1 degrade. | E0 (first clause; rule in entry 0003), E1 (second clause) | NOT CONFIRMED |
| H-S3 | (chain reaches retention) Screen-predicted R² rank-correlates with floor-normalized retention **across pairs and k** — because held-out R² does (Run 2, within-pair: rank correlation +1 across k; in-sample rank-correlates −1), and the screen predicts held-out R². The source paper's r = −0.20 is quarantined explicitly as an in-sample artifact. Falsification mode: screen predicts fidelity but not retention → the contribution becomes the decomposition (symmetric predictable factor + receiver residual), stated in the abstract, not conceded to a reviewer. | E2 | SHELVED |
| H-S4 | (economics load-bearing, not decorative) Composition (H-C1/C2/C3 as already registered in the ledger) and the calibration curve (H-L1–L4) convert the screen from a correlation into a build policy: which pairs, which direction, how many calibration tokens, n−1 vs n(n−1) mappers. | E4, E5 | SHELVED |
| H-E7a | switch-point frequency × recoverable prefill cost makes transfer headroom material (threshold: define the materiality cutoff in entry 0005's successor before replay). | E7 | NOT CONFIRMED |
| H-E7b | the compaction break-even distribution has substantial negative mass at current pricing (threshold: define before replay). | E7 | UNESTIMABLE |
| H-E8 | (transfer survives the agent-trace distribution shift) A linear KV mapper fit on generic calibration text retains its held-out pooled R² (definition A5) when the KV states come from agent-trace text instead, within the tolerance band registered in entry 0009 before E8 runs. Evaluated on the one pair with fitted mappers upstream (qwen3-0.6b-to-1.7b); the traces are off-policy for Qwen, so this tests CONTENT distribution shift, never on-policy agent behaviour and never a real mid-trajectory switch. | E8 (band in entry 0009) | NOT CONFIRMED |
| H-E9 | (achievable fraction of the headroom upper bound at a re-rendered handoff) at a re-rendered handoff, same-model KV agreement on content-matched tokens retains the transfer-relevant fidelity. Rule (entry 0019, band approved 2026-09-01, frozen before any prefill): per-handoff E9-same pooled K R² (definition A5) at LCS-floor matched positions, median over included handoffs — HOLDS >= 0.70, DEGRADES <= 0.40, UNRESOLVED between; V reported alongside, verdict-bearing for nothing; handoffs over the 32,768-token cap excluded and counted. Row added with 0019's commit set completion — the entry says "registered in the table" and the row was initially missing (process slip, noted in the handoff; the entry text is immutable and unchanged). | E9 (band in entry 0019) | unresolved |

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

### 0007 — 2026-09-01 — Review amendments: Lane A decides H-E7a; per-agent coverage; cost-model parameters; SHELVED; entry chain

Source: operator review of the tree at `1f7ad90` (independent clone-and-check, 2026-09-01).
Entry 0006's registered text stands as written; the clauses below supersede it where named,
per house style.

**(1) H-E7a is decided by Lane A alone.** Entry 0006's materiality clause "in at least one
lane" is superseded. Lane B inserts a switch point at every tier boundary of a policy this
program chose, so Lane B headroom is material by construction -- it measures the policy, not
the workload -- and under the superseded wording a Lane A zero plus a Lane B clearance would
have resolved H-E7a positive, softening the premise finding. Amended rule: H-E7a's verdict is
determined solely by Lane A against the 10% cutoff of entry 0006. Lane B output is
descriptive counterfactual only and shall never resolve any hypothesis, in this entry or any
successor.

**(2) The coverage floor counts agents, not runs.** Entry 0006's floor (>= 50 trajectories
per suite, >= 2 suites) is satisfiable by many runs of one scaffold, which yields the
invalidation habits of one agent, not a suite-level property. Amended floor: >= 50
trajectories per suite AND >= 3 distinct agents/scaffolds (distinct leaderboard submissions
or harness configurations) per suite, over >= 2 suites. Invalidation frequencies are reported
per-agent alongside pooled, so no single scaffold's behavior can masquerade as the suite's.

**(3) Cost-model parameters, registered before any replay.** Entry 0006 pinned prices but not
the model that consumes them; these were the free parameters a reviewer would assume were
tuned:

- **TTL base case:** Anthropic 5-minute ephemeral cache (write 1.25x, read 0.1x). The 1-hour
  tier (write 2.0x) is reported as sensitivity only and is verdict-bearing for nothing.
- **Idle-gap expiry IS modeled**, from trace timestamps, wherever the trace carries them: a
  cached prefix older than the TTL at the next request is expired and re-prefills at full
  price.
- **Traces without timestamps:** H-E7b is computed under two bounds -- cache-always-warm (no
  expiry ever) and cache-always-cold (expired at every inter-step gap) -- and the >= 25%
  negative-mass threshold must hold under BOTH bounds to resolve H-E7b positive. Stated bias
  direction: the warm bound overstates the value of retaining tokens and therefore biases
  toward finding compaction net-negative (toward H-E7b positive); the cold bound biases the
  other way; requiring both removes the parameter as a degree of freedom.
- **Tool-latency gaps come only from trace timestamps, never from an assumed distribution.**
  A trajectory with no timestamps contributes to the taxonomy and to Lane A/B counts, but not
  to any expiry-sensitive number outside the two-bound H-E7b computation above.

**(4) `SHELVED` enters the verdict vocabulary.** Entry 0006 left H-S1/H-S3/H-S4 at
`unresolved`, indistinguishable in the table from live-and-pending. `SHELVED` is added to
`ledger_check`'s vocabulary (code change in this commit set) and this entry moves H-S1, H-S3,
and H-S4 from `unresolved` to `SHELVED`: no experiment decided them, and none is scheduled.
Distinct from `WITHDRAWN` (a claim retracted) and `SUPERSEDED` (a claim replaced). A future
program that reopens one moves it back to `unresolved` by a numbered entry.

**(5) The entry chain begins here.** From this entry on, every entry carries a
`prior-entries-sha256:` line -- the sha256 of the ledger text from the `## Entries` heading
(inclusive) up to the entry's own heading (exclusive), computed over the
universal-newline-decoded text encoded as UTF-8, recomputed by `ledger_check` in CI. What it
protects: registered entry text, byte-for-byte. What it deliberately excludes: the header
prose and the hypotheses table above `## Entries`, which are editable commentary (verdict
cells change only via a numbered entry -- a convention this hash cannot enforce). What it
cannot detect: a history rewrite that regenerates the chain, exactly as the README already
says of the seal.

**(6) The evidence entry 0006 cited now lives in the tree:**
`docs/2026-09-01-measurement-lane-evidence.md` -- the four-paper delta table with arXiv IDs
and retrieval dates, the trace-metadata probe result behind the two-lane design, and the
venue facts. A handoff brief for this re-scope is indexed in `docs/handoff/HANDOFF.md`.

prior-entries-sha256: 0b180f2473877c0e7d7826e4c1eefacd7fc15a94d3f7ce82de1d7b93f598d92e

### 0008 — 2026-09-01 — Day-2 gate PASSED; tokenizer question raised, NOT yet registered

**Day-2 gate outcome (entry 0006), recorded as fact.** All three items met on 2026-09-01,
two days before the EOD 2026-09-03 deadline, so the LCFM sprint remains live:

- (i) one suite acquired and parsed -- tau-bench `historical_trajectories`, 4 files,
  **1980 trajectories** (200 / 460 / 400 / 920), count verified by an independent pass over
  the raw files, not taken from the driver's own report;
- (ii) the replay skeleton computed per-trajectory token/cost timelines on all 1980
  (26,316 assistant requests), far above the >= 10 required;
- (iii) both lanes implemented and exercised over the whole set.

The `assert_ready` gate registered in 0006 is now **demonstrated in both directions**: it
refused with exit 2 while `config/e7.toml` was uncommitted, and returned ready only after
the registration landed in history. No trajectory was read before that.

**Lane A over tau-bench: 0 of 1980 measurable.** Every tau-bench trajectory records the
serving model at run level (in the filename) and never per step, so Lane A reports
`measurable=false, switches=null` for all 1980 -- recorded as NOT MEASURABLE, never as zero
switches, per entry 0006's rule. This is the first empirical support for the premise finding
the program was scoped around, on one suite; it is not yet the finding, which requires the
coverage floor.

**Coverage floor NOT met, as expected.** tau-bench supplies 1980 trajectories (>= 50) but
only **2 distinct agents** (gpt-4o, sonnet-35-new) against entry 0007's >= 3, and 1 suite
against >= 2. The driver reports `coverage_meets_floor: false`. Nothing from this run may
ship except as partial-with-coverage-stated; SWE-bench (many scaffolds per split) is the
suite that must clear the floor.

**No number in this entry is verdict-bearing.** Token counts come from the chars/4 estimate
that `e7_traces.approx_tokens` marks non-verdict-bearing; the cost figures the skeleton
produced (including a warm-bound total near 19% of the cold bound) are therefore descriptive
scaffolding only, are deliberately NOT tabulated here, and decide nothing. One trajectory's
warm/cold arithmetic was recomputed by an independent path touching neither `e7_cost` nor
`e7_traces` and agreed to floating-point equality -- that verifies the implementation, not
the estimator.

**The tokenizer is an open decision, NOT registered by this entry.** It must be registered
before any cost number ships (entry 0006's numbers-freeze gate, EOD 2026-09-08). The
difficulty is stated here so the decision is made in the open rather than defaulted into:

- No tokenizer library is installed in this environment, and there is no offline tokenizer
  cache; adding one is a network dependency.
- The traces are gpt-4o and Claude 3.5 Sonnet runs. GPT-4o's encoder is public
  (`o200k_base`, via tiktoken). **Anthropic's tokenizer is not public**, so Claude
  trajectories cannot be tokenized exactly offline; the options are an approximation applied
  to both (comparable, biased, bias direction unmeasured), a per-agent tokenizer (accurate
  where possible, cross-agent comparisons then unsound), or a provider API call (network,
  credentials, and a per-run dependency this repo has so far avoided).
- Whichever is chosen must be registered with its known bias BEFORE the numbers it produces
  are computed, or the choice becomes post-hoc.

Until that entry exists, the E7 instrument may be run and its output inspected, but no
figure it produces may enter a ledger entry, a paper, or a claim.

prior-entries-sha256: 95977ca0bf9e413c493608cbb7579856b0da15a1a491f6ec505dc82a781654ab

### 0009 — 2026-09-01 — Tokenizer registered (measured, not assumed); E8 transfer leg registered; 0006's half-registered clause resolved

Operator rulings of 2026-09-01: approximate the tokenizer; keep LCFM trace-only and add the
Qwen transfer leg to the MLSys program, registered with its own hypothesis before anything
runs. This entry executes both and closes entry 0008's open question.

**(1) A defect found before any number shipped `[BASELINE]`.** tau-bench stores a tool call's
`arguments` inconsistently BY AGENT: gpt-4o records a JSON string (4,438 calls), sonnet-35-new
records a parsed dict (9,847 calls). The skeleton's character-based counter received the dict
directly, so it counted its KEYS -- an undercount affecting only one agent. Fixed by
normalizing dicts to compact JSON (`e7_traces.tool_arguments_text`), justified empirically:
the sibling agent's own wire format in the same suite is compact
(`{"user_id":"mia_li_3668"}`, 25 chars, byte-equal to `json.dumps(separators=(",",":"))`).
Measured impact on estimated input tokens: **+1.5% for sonnet-35-new, 0.0% for gpt-4o, +1.0%
overall.** Small in aggregate but ASYMMETRIC BY AGENT, which is the damaging shape -- it
would have biased every cross-agent comparison in one direction. Regression tests pin both
storage shapes to identical counts. Original bytes are unrecoverable from a parsed dict, so
key order follows the trace and the compact-vs-spaced choice moves the count by ~1 char per
key: a stated, unmeasured limitation.

**(2) The token counter, registered with its bias MEASURED.** Entry 0008 left this open. A
blanket chars/N estimator was the intended ruling; measurement showed it is unsafe, so the
ruling is honored where approximation is actually necessary and dropped where it is not.
Calibrated against `o200k_base` over the full corpus (34,444,409 chars / 9,250,735 tokens,
2026-09-01, after the fix in (1)):

| content type | chars/token | chars/4 error |
|---|---|---|
| tool_output (JSON-ish) | 2.890 | -27.8% |
| tool_call_args (JSON) | 3.467 | -13.3% |
| assistant (prose) | 4.005 | +0.1% |
| user (prose) | 4.322 | +8.0% |
| system (prompt) | 4.817 | +20.4% |
| OVERALL | 3.723 | -6.9% |

The bias is not uniform: chars-per-token spans 2.890 to 4.817, a 1.67x spread. A uniform
multiplicative bias would cancel in both verdict-bearing quantities, since H-E7a and H-E7b are
ratios; this one does not, and it is worst on tool output -- exactly the content that context
compaction preferentially removes -- so a blanket chars/4 would push H-E7b's break-even in a
systematic direction. Registered instead, in `config/e7.toml [e7.tokenizer]`:

- **gpt-4o: `exact`** -- its public encoder `o200k_base` (pinned by name, via tiktoken). No
  estimate at all for 660 of the 1,980 trajectories.
- **sonnet-35-new and any future agent: `calibrated`** -- the per-content-type divisors above,
  measured on the exact half of the same suite.
- **Stated assumption, unverifiable offline:** that the target model's tokenizer has similar
  chars-per-token to `o200k_base` on this content. Anthropic publishes no tokenizer, so this
  cannot be checked without a network call to their counting endpoint. Every `calibrated`
  number carries it, and the report records which strategy produced each agent's counts.
- Divisors are config, not code; `load_e7_config` refuses a config with no measured divisors.
- Determinism: tiktoken caches its BPE file on first use and is offline and deterministic
  after that; the encoding is pinned by name, never "the default for model X".

Residual risk, stated rather than resolved: the calibration set and the measured corpus are
the same corpus, so the divisors are descriptive of tau-bench and are NOT claimed to transfer
to another suite. SWE-bench requires its own calibration before its numbers ship.

**(3) E8 registered -- transfer under the agent-trace distribution shift.** Entry 0006 named a
"transfer-fidelity leg" only inside its numbers-freeze gate clause, with no registered output
and no hypothesis: half-registered, which is worse than either. Resolved: the leg is IN, as
experiment **E8** deciding new hypothesis **H-E8** (registered in the table above), and it
belongs to the MLSys program only.

- **Design.** Take the EXISTING fitted mapper for qwen3-0.6b-to-1.7b (upstream artifact, fit
  on generic calibration text; no refit), and evaluate its held-out pooled R² (definition A5,
  borrowed with provenance from the upstream at the pin) on KV states generated two ways
  under one protocol: (a) generic calibration text, (b) agent-trace text drawn from the E7
  corpus. The difference is the distribution-shift effect.
- **Tolerance band, frozen here, before any dump is generated:** HOLDS if the absolute drop in
  held-out pooled R² is <= 0.05; DEGRADES if the drop is >= 0.15; UNRESOLVED in between.
  Reported for K and V read-outs separately; a single number is never reported alone.
- **Scope limits that the paper must carry.** Qwen did not generate these traces, so the text
  is off-policy for Qwen: E8 tests CONTENT distribution shift, never on-policy agent
  behaviour. E8 is not a transfer at a real mid-trajectory switch point and must never be
  written as one. Only one ordered pair has fitted mappers upstream, so E8 is a single-pair
  result.
- **The seal is not involved.** E8 makes no pre-fit claim -- it evaluates an already-fitted
  mapper -- so no sealed prediction is written and nothing here may later be read as one
  (the D2 post-fit exception of entry 0002 governs why this pair can never be sealed pre-fit).
- **Known cost, not yet paid.** The upstream has NO `dumps/` directory: the KV dumps are gone
  and both arms must be regenerated by forward passes on 0.6B and 1.7B. CPU-feasible; the
  wall-clock is unmeasured, and E8 is scheduled only if it fits before MLSys (2026-10-30).

**(4) LCFM stays trace-only.** The 4-page submission, if the gates pass, carries Lane A/B
premise numbers and the taxonomy. E8 appears in no LCFM submission. Entry 0006's
numbers-freeze scope cap is otherwise unchanged.

prior-entries-sha256: 19612bc72156fa045457c234efef450ea1c8dcf8c68594b8d72374c3c78390b3

### 0010 — 2026-09-01 — A real cross-model switch exists in public traces; Lane A detector breadth and the re-rendered-handoff headroom measure

**What changed and what did not.** Entry 0006 registered Lane A's RULE ("a switch point is
counted only where trajectory metadata records the serving model per step and it changes
mid-trajectory") together with an EXPECTATION ("public trajectories record the model per RUN,
not per step, so Lane A is expected sparse to absent"). The rule is unchanged and needs no
amendment -- it handles what follows exactly as written. **The expectation was wrong**, and
this entry corrects it. An expectation is not a rule; correcting one is not relitigating the
other.

**Finding `[BASELINE]` -- mid-trajectory model switching IS present in public benchmark
traces.** Re-probed with a detector matching `model|model_id|model_name` (the original probe
matched only the literal key `model`, and the LangChain-style family records under the other
two, so it was never probed -- the detector was strictly narrower than the set the conclusion
quantified over):

| submission | trajectories probed | with >1 serving model | models |
|---|---|---|---|
| 20241016_composio_swekit | 25 | 25 | anthropic.claude-3-5-sonnet-20240620-v1:0 + o1-mini-2024-09-12 |
| 20241025_composio_swekit | 25 | 25 | anthropic.claude-3-5-sonnet-20241022-v2:0 + o1-mini-2024-09-12 |

Claude runs the solve threads; o1-mini runs per-run summarization and patch selection. Five
other submissions carrying per-step model identity (zai x2, livesweagent x2, moatless) show one
model each across 125 probed trajectories, 3 vendors. Numbers recomputed independently of the
adversarial report that produced them; that report's separate claim that the handoff is
"verbatim" is REFUTED here (see below) and must not be repeated.

**Consequence for the premise.** The claim this program may make is now narrower and better
supported: mid-trajectory model switching occurs as a **designed critic/selector pipeline
stage**, while **production-style cost/quality routing or mid-conversation switching remains
unevidenced** in public traces. Neither "switching never happens" nor "the premise holds" is
supportable. Submissions that are multi-model by design but record no serving identity
(navie-2, SWE-Fixer, wandb crosscheck, Skywork Bo8, Co-PatcheR) remain NOT MEASURABLE and are
never counted as zero.

**Registered requirement -- detector breadth.** Lane A's implementation MUST search at minimum
the keys `model`, `model_id`, `model_name`, and any adapter for a new family must state which
keys carry serving identity in that family. A detector narrower than the corpus produces false
NOT MEASURABLE and false zeros, both of which corrupt the premise finding in the flattering
direction. **A narrow detector is a defect, never a null result.** Any Lane A output must
record the detector's key set alongside its counts so the two can never be read apart.

**Registered measure -- headroom at a re-rendered handoff, defined before it is computed.**
The observed switch is NOT a byte-identical context handoff. The o1-mini stage re-renders the
Claude conversation into LangChain labels (`HumanMessage` 5, `AIMessage` 11, `ToolMessage` 7 in
the inspected instance), sharing 118 of 119 long tokens with the Claude stage, while a
verbatim-prefix check returns 0/3. The second model therefore re-consumes the first model's
context as a re-serialized prompt and pays full prefill on it. Measure, frozen here:

- **paid**: the second stage's prefill tokens, priced at the pinned rates (entry 0006/0007).
- **overlap**: the portion of the second stage's prompt whose content the first model had
  already processed, measured by token-level overlap and reported with the method named.
- **headroom_upper_bound = overlap x (1 - read_mult)**, and it is registered as an **UPPER
  BOUND, never an achievable saving**: because the re-rendering changes the token sequence and
  the positions, transferred KV would not be directly reusable even where the content matches.
  Any output stating this figure must carry the words "upper bound" and the reason.
- The residual (paid - overlap) is genuinely new framing/instruction text and is reported
  separately, never folded into headroom.

This measure decides nothing on its own: H-E7a's verdict still comes from Lane A against entry
0006's 10% materiality cutoff, through the registered adapter and a fail-closed summarizer, and
never from an ad-hoc probe. The probes reported in this entry are RECON that sized the finding.

prior-entries-sha256: f1e6fc06604d9ffd689a926d9ee272b00de765c92b31a1004fe15c3e5750b9fd

### 0011 — 2026-09-01 — The trajectory unit, defined; coverage floor met on two suites

Entry 0007 set a coverage floor in TRAJECTORIES without defining one. The unit is
load-bearing: a layout difference was observed to change the count by 2x on real data, so the
floor meant nothing until this was fixed. Definition, registered before any coverage claim
ships:

**A trajectory is one agent run on one task instance.** Not one file, and not one task.

- **Flat layout** (`trajs/<instance>.json`, most submissions): one file is one trajectory.
- **Nested layout** (`trajs/<instance>/attempt_N/<stage>.json`, e.g. autocoderover): one
  INSTANCE DIRECTORY is one trajectory; its stage files are concatenated in sorted order.
  Counting stage files instead would have reported 8 trajectories where there were 4.
- **Non-trajectory siblings** (`patch_0.diff`, `selected_patch.json`,
  `regression_test_result_0.json`) are skipped, never counted and never treated as parse
  failures. A file that is not a message document is not evidence of absence.
- **Repeated trials are distinct trajectories** (tau2-bench runs 4 trials per task), because
  each is a separate agent run. **But trials are not independent samples**, so any coverage
  statement must report DISTINCT TASKS alongside trajectories -- 800 tau2 trajectories are 50
  distinct airline tasks x 4 trials x 4 agents, and reporting only the larger number would
  overstate diversity.

**Coverage floor status against entry 0007** (>= 50 trajectories AND >= 3 distinct
agents/scaffolds per suite, over >= 2 suites), under this definition:

| suite | trajectories | distinct agents | meets per-suite floor |
|---|---|---|---|
| swe-bench | 64 | 5 (honeycomb, marscode, Skywork, autocoderover, openhands) | yes |
| tau2-bench | 800 (50 tasks x 4 trials x 4 agents) | 4 (claude-3-7-sonnet, gpt-4.1, gpt-4.1-mini, o4-mini) | yes |

Two suites clear it, so **the floor of entry 0007 is met** and output need no longer ship as
partial-with-coverage-stated on coverage grounds alone. Recorded for the avoidance of doubt:
tau-bench v1 (2 agents) does NOT clear the per-agent floor and is excluded from floor
arithmetic; it may still be reported, labelled below-floor. SWE-bench `multimodal` was checked
and rejected as a candidate suite -- 0 of its 22 submissions publish trajectories
(`trajs: null`).

Composio (the switching family, entry 0010) is 2 submissions of one system and is NOT counted
toward the swe-bench agent floor above; it is the Lane A subject, not a coverage contributor.

prior-entries-sha256: f6e512727a8842b416557077aa273e2c4157aa1f48d3bc4176374fb977b92ca5

### 0012 — 2026-09-01 — Public traces omit the cacheable prefix `[BASELINE]`; every trace-only cost figure is a lower bound

**Finding.** tau2-bench records provider-reported `usage.prompt_tokens` per message, so the
token estimator of entry 0009 can be validated against GROUND TRUTH rather than compared to
another estimator. Over 4 airline result files (800 simulations, 4 agent models), comparing each
message's reported prompt tokens against the cumulative estimated prefix preceding it, split by
which model made the request:

| requesting model | n | offset median (reported - estimated) | p10 | p90 | ratio median |
|---|---|---|---|---|---|
| user simulator (prefix fully visible) | 5,158 | **-134** | -2,489 | +462 | 0.87 |
| agent (prefix partly hidden) | 8,914 | **+3,423** | +3,239 | +5,962 | 4.14 |

By assistant-turn position the agent offset is nearly FLAT: +3,238 (turn 1), +3,264 (turns
2-3), +3,382 (4-8), +3,609 (9+).

**Interpretation, and what it licenses.** The estimator is sound: where the whole prefix is
visible (user-simulator calls) it agrees with the provider to within ~134 tokens. A large
additive gap that does not grow with conversation length is not estimator drift but a **fixed
hidden prefix** -- the domain policy system prompt plus tool schemas -- which the provider
billed and the trace does not record. Roughly 3,240 tokens per agent request, ~42k per
trajectory at the median turn count. Two consequences, both registered here:

1. **Every cost figure this program computes from trace messages alone is a LOWER BOUND**, and
   must be labelled so. The hidden block is byte-identical on every request, i.e. exactly the
   most cacheable content in the conversation, so omitting it understates BOTH total prefill
   spend AND the benefit of caching. The bias is one-directional and cannot be corrected by any
   care taken with the visible messages.
2. **Where a trace carries provider-reported usage, the reported-vs-estimated offset is
   reported alongside the figure** -- per requesting model, never pooled. Pooling the agent and
   user-simulator series produced an uninterpretable ratio of 3.3 on the first pass; the two
   models bill against different prefixes and are different accounting series.

**Scope.** Measured on tau2-bench airline only. It is NOT asserted that the ~3,240-token figure
transfers to another suite or domain; what transfers is the method (validate against reported
usage where it exists) and the direction of the bias (visible-only is a floor). SWE-bench
corpora carry no reported usage, so their cost figures have no such check and must be labelled
lower bounds without a measured gap.

This entry decides no hypothesis. It constrains how every later figure must be stated.

prior-entries-sha256: 51971a4ad1f56f75853d3f7e8e8c130abe4b495f60267cdb7f519d582e64f8a7

### 0013 — 2026-09-01 — Headroom at observed handoffs `[BASELINE]`, through the fail-closed summarizer

**What this entry records.** The entry-0010 measure, computed for the first time through
`summarize_e7` rather than a probe. Every figure below is a value the summarizer recomputed
from the raw traces and compared against the driver's report (config sha256
6915666d452d; 188 trace files hashed); the summarizer refuses on
any disagreement, and three live tampers on this report (aggregate median, a usage offset, one
deleted switch row) were each refused by path before this entry was written.

**Corpus at this run.** 2904 trajectories over three suites. Coverage (entry 0011 units;
composio excluded as Lane A subject): swe-bench 64 trajectories /
5 agents / 15 distinct tasks; tau2-bench
800 / 4 / 50;
tau-bench 1980 / 2 / 165
(reported, below the agent floor, excluded from floor arithmetic). Floor: **MET**.
Lane A (detector keys ['model', 'model_id', 'model_name']): **60 of 2904 trajectories measurable**,
all of them composio (60 trajectories); 2844 recorded NOT MEASURABLE, never zero.
Unparsed trajectories: 0.

**Headroom at the 68 observed Lane A switches** (20241016_composio_swekit, 20241025_composio_swekit), read_mult 0.1:

| figure | value |
|---|---|
| observed switches (Lane A, per-step metadata) | 68, all in the composio family |
| byte-identical handoffs | **0/68** |
| overlap of the receiving prompt with sender-processed content | 0.903 (p10 0.353, p90 0.982) |
| paid prefill at the switch, tokens (visible-only LOWER BOUND) | 19,972 (p10 624, p90 93,805) |
| headroom UPPER BOUND as a fraction of paid | **81.3% (p10 31.7%, p90 88.4%)** |

Method, as registered in 0010 and pinned in code: multiset whitespace-token overlap of the receiving prompt with everything the sender processed; headroom_upper_bound = overlap_tokens x (1 - read_mult). Quantiles are the
repository's one convention (`e7_stats`: median = statistics.median; p = sorted[floor(p x n)],
lower nearest-rank, no interpolation).

**What these numbers are and are not.**

- The upper bound is what a transfer could recover **if** the re-rendered prompt's content
  overlap were fully reusable. It is not: re-rendering changes the token sequence and every
  position, so the achievable fraction is strictly below this and is not measured here.
- `paid` counts only visible messages (entry 0012); the provider also billed a hidden prefix
  the trace omits, so both paid and the absolute headroom are floors.
- The 68 switches come from two submissions of ONE system (entry 0011) that switches by
  design (Claude solves, o1-mini summarizes/selects). They evidence that the expensive form of
  the motivating use case exists in a public trace; they are not a sample of agent practice.

**What this entry decides: nothing.** H-E7a's rule is recoverable prefill spend at Lane A
switch points as a fraction of the trajectory set's total input spend (entry 0006, Lane A
alone per 0007). That ratio is not stated here because its denominator's scope -- which
trajectory set -- is not yet fixed by any entry (the measurable subset, the suite, or the
whole corpus give different answers by orders of magnitude). A successor entry fixes the
denominator before the ratio is computed; this entry records the numerator's ingredients.

prior-entries-sha256: 161b38359f50b631de6639e8f878c6489943bfd01338bf24e17cffa9f84c78c2

### 0014 — 2026-09-01 — Invalidation taxonomy registered (event definitions and measurability, before any frequency); H-E7a denominator fixed

Entry 0005 promised "an invalidation taxonomy with event frequencies per trace suite" and no
entry has yet said what an event IS. Frequencies computed before the definitions are
registered would be definitions fitted to the data; this entry registers them first. Two recon
probes informed the definitions and are stated as recon, not results: (a) tau2-bench's
provider-reported prompt tokens never decrease across 8,114 consecutive agent requests; (b)
no tau2 inter-request gap exceeds 300 s (max 235 s). Neither is a registered number until it
recomputes through `summarize_e7`.

**The taxonomy: why a cached prefix dies, one event class per cause.** Each class carries a
DETECTION RULE and a MEASURABILITY RULE. A trajectory that cannot evidence a class is recorded
NOT MEASURABLE for that class and contributes to neither numerator nor denominator of its
frequency -- never a zero (entry 0006's rule, generalized from Lane A to every class).

| class | detection rule (per trajectory) | measurable iff |
|---|---|---|
| `model_switch` | Lane A exactly as registered (0006/0010): consecutive assistant turns whose per-step serving model differs | every assistant turn records a serving model (detector keys per 0010) |
| `rerender_at_switch` | a `model_switch` whose handoff is not byte-identical (entry 0010's `byte_identical` = false) | `model_switch` measurable AND per-message text available to the adapter |
| `compaction` | the provider-reported prompt size of an agent request is SMALLER than that of the preceding agent request in the same trajectory (the context was rewritten to fewer tokens; append-only growth is the null) | at least two consecutive agent requests carry provider-reported prompt tokens |
| `idle_expiry` | an inter-request gap between consecutive agent requests exceeds the TTL of entry 0007's base case (300 s) | at least two consecutive agent requests carry timestamps |
| `branch` | more than one attempt on the same task instance within one trajectory directory (nested layout `attempt_N`, N >= 1) | the layout records attempts (nested); flat layouts cannot evidence a branch and are NOT MEASURABLE |
| `edit` | an earlier message modified in place between requests | NO current corpus records per-request prompts for the same model, so `edit` is NOT MEASURABLE everywhere; it is registered so its absence from every table is a stated unmeasurable, not an omission |

Rules that bind the frequencies when they ship:

- **Per agent alongside pooled** (entry 0007) for every class: measurable trajectories,
  trajectories with >= 1 event, total events, and the NOT MEASURABLE count, in one row.
- A final-transcript trace (every role/content SWE-bench family, tau-bench v1) is append-only
  by construction and therefore NOT MEASURABLE for `compaction`, `idle_expiry`, and `edit`.
  This is the expected shape of the table, and it is the finding, not a gap in the tooling.
- Tool-output truncation applied before a message enters the context is NOT a compaction
  event: the prompt still grows. Only a decrease in what the provider was asked to prefill
  counts.
- No class is added, merged, or re-defined after the first frequency table is computed.

**H-E7a's denominator, fixed before the ratio is computed.** Entry 0006's rule is "recoverable
prefill spend at switch points >= 10% of the trajectory set's total input-token spend" and does
not say which trajectory set. Registered here: **the Lane A MEASURABLE subset, per suite and
pooled.** Reason: an unmeasurable trajectory cannot contribute switches to the numerator, and
placing it in the denominator would count it as a measured zero -- the one thing entry 0006
forbids. The numerator is the entry-0010 upper bound summed over observed switches (so the
ratio is itself an upper bound), both sides in base-input-price token units (the ratio is
price-independent). Recon over the current corpus, stated so that this choice cannot later be
read as outcome-selected: the ratio is below the cutoff under EVERY candidate denominator
(whole corpus, suite, measurable subset), by roughly an order of magnitude. The verdict is
still not stated here: it enters by a successor entry only from the summarizer's recomputed
ratio, against the 10% cutoff, with Lane A alone (entry 0007).

**Enforcement.** `summarize_e7` recomputes every class count, measurability flag, per-agent row
and the H-E7a ratio from the raw traces and refuses on any disagreement; replay must not begin
until this entry is committed unmodified (`e7.assert_ready`, entry 0006).

prior-entries-sha256: 5a2eaea7cc174b727cac9c8dcc0446091f650abc6f7df2bc8849a9f7408905b1

### 0015 — 2026-09-01 — Invalidation taxonomy frequencies `[BASELINE]`; H-E7a NOT CONFIRMED; H-E7b UNESTIMABLE

**Provenance.** First replay under entry 0014's definitions, after 0013/0014 were committed
(`e7.assert_ready` passed); every figure below recomputed by `summarize_e7` from the raw traces
(config sha256 6915666d452d; 188 trace files hashed; 2904 trajectories;
Lane A detector keys ['model', 'model_id', 'model_name']) and compared against the driver's report before this
entry was written. Coverage floor: MET (entry 0011 units).

**Taxonomy frequencies** (`ev` = events; `a of b` = trajectories with >= 1 event, of the measurable
trajectories; `n/m` = NOT MEASURABLE for that class -- in neither numerator nor denominator, never a
zero). Rows NOT MEASURABLE for every class are listed once below the table rather than repeated.

| scope | model_switch | rerender_at_switch | compaction | idle_expiry | branch | edit |
|---|---|---|---|---|---|---|
| swe-bench/autocoderover-v2.1-claude-3-5-sonnet-20241022 | n/m (4) | n/m (4) | n/m (4) | n/m (4) | 4 ev / 2 of 4 | n/m (4) |
| swe-bench/composio_swekit | 68 ev / 60 of 60 | 68 ev / 60 of 60 | n/m (60) | n/m (60) | n/m (60) | n/m (60) |
| tau2-bench/claude-3-7-sonnet-20250219 | n/m (200) | n/m (200) | 0 ev / 0 of 200 | 0 ev / 0 of 200 | n/m (200) | n/m (200) |
| tau2-bench/gpt-4.1-2025-04-14 | n/m (200) | n/m (200) | 0 ev / 0 of 200 | 0 ev / 0 of 200 | n/m (200) | n/m (200) |
| tau2-bench/gpt-4.1-mini-2025-04-14 | n/m (200) | n/m (200) | 0 ev / 0 of 200 | 0 ev / 0 of 200 | n/m (200) | n/m (200) |
| tau2-bench/o4-mini-2025-04-16 | n/m (200) | n/m (200) | 0 ev / 0 of 200 | 0 ev / 0 of 200 | n/m (200) | n/m (200) |
| **swe-bench (pooled)** | 68 ev / 60 of 60 (+64 n/m) | 68 ev / 60 of 60 (+64 n/m) | n/m (124) | n/m (124) | 4 ev / 2 of 4 (+120 n/m) | n/m (124) |
| **tau-bench (pooled)** | n/m (1980) | n/m (1980) | n/m (1980) | n/m (1980) | n/m (1980) | n/m (1980) |
| **tau2-bench (pooled)** | n/m (800) | n/m (800) | 0 ev / 0 of 800 | 0 ev / 0 of 800 | n/m (800) | n/m (800) |
| **ALL** | 68 ev / 60 of 60 (+2844 n/m) | 68 ev / 60 of 60 (+2844 n/m) | 0 ev / 0 of 800 (+2104 n/m) | 0 ev / 0 of 800 (+2104 n/m) | 4 ev / 2 of 4 (+2900 n/m) | n/m (2904) |

NOT MEASURABLE for every class (final-transcript traces: no per-step model, no reported usage, no
timestamps, flat layout): swe-bench/Skywork-SWE-32B (15), swe-bench/honeycomb (15), swe-bench/marscode-agent-dev (15), swe-bench/openhands (15), tau-bench/gpt-4o (660), tau-bench/sonnet-35-new (1320).

**What the table says.**

- Every observed model switch is a re-render (68 of 68): the receiving model
  never received a byte-identical prefix. Entry 0013's upper bound is the ceiling of a transfer that
  does not exist as prefix reuse in any public trace.
- Compaction: 0 events over 800 measurable trajectories (tau2-bench, the only suite
  that records per-request prompt sizes); 2104 trajectories NOT MEASURABLE. On the one
  corpus that can show it, context only grows.
- Idle expiry under the 5-minute TTL: 0 events over 800 measurable trajectories --
  for tau2-bench, entry 0007's warm bound is not a bound but the realized case; 2104
  NOT MEASURABLE.
- Branch: 4 extra attempts over 2 of 4 measurable instances (nested layout
  only); 2900 NOT MEASURABLE. Edit: NOT MEASURABLE everywhere, as registered.

**H-E7a -- NOT CONFIRMED.** Rule: entry 0006's materiality cutoff (10% of the trajectory set's
input spend), Lane A alone (0007), denominator = the Lane A measurable subset (0014). Recomputed:
recoverable upper bound 2,339,562 / input spend 165,959,914 over 60
measurable trajectories = **1.41%** (swe-bench: 1.41% over 60 measurable trajectories). Below the cutoff by roughly an order of
magnitude, and the numerator is itself an upper bound (0010/0013), so the true ratio is lower still.
Entry 0014's recon showed the same direction under every candidate denominator; the choice was not
outcome-selecting. Per entry 0005's registered kill condition, **the motivation reverts to the
fleet-mixing framing**: on public agent traces, mid-trajectory model switching is rare (one designed
critic/selector family) and its recoverable prefill is immaterial against what those trajectories
spend on prefill; any case for cross-model KV transfer must rest on different models serving
different requests, not on handoffs within a trajectory. H-E7a's verdict cell changes to
`NOT CONFIRMED` with this entry.

**H-E7b -- UNESTIMABLE.** The compaction break-even distribution has no support: zero compaction events
on every trajectory that can evidence one, NOT MEASURABLE on the rest. Entry 0005 registered this
outcome in advance ("compaction events too sparse -> H-E7b dropped as unestimable, stated, not
silently omitted"); this entry states it. `UNESTIMABLE` enters the verdict vocabulary (`ledger_check`,
in this commit set) for exactly this case -- the experiment ran and its estimand has no support in
the corpus -- distinct from `SHELVED` (no experiment ran) and `NOT CONFIRMED` (the rule returned a
negative). It is not a claim that compaction does not occur in practice: final-transcript traces
cannot show it. A corpus that records per-request prompt sizes AND compacts would reopen H-E7b by a
numbered entry; nothing is scheduled.

**What this entry does not decide.** H-E8 (entry 0009, to be amended by 0016) and H-E9 (0017) are
untouched. Entry 0005's three E7 outputs are now all on the record: (i) the taxonomy above,
(ii) headroom (0013), (iii) the break-even distribution, as UNESTIMABLE.

prior-entries-sha256: 2899f4d32d7be320548bc2c7bb78b4cd8dd73ba6efe24f795b218f3900784505

### 0016 — 2026-09-02 — E8 amended: admitted to LCFM behind the summarizer gate; dumps correction; verdict k = 1; text-sampling rule; upstream re-pin

Operator decisions of 2026-09-01: GPU runs join the LCFM plan (`docs/2026-09-01-lcfm-gpu-plan.md`);
band numbers and entry ordering approved. Entry 0009's registered E8 design and band stand as
written; the clauses below amend it where named.

**(1) E8 may appear in the LCFM 4-pager.** Entry 0009(4) ("E8 appears in no LCFM submission")
is superseded. Entry 0006's numbers-freeze gate already allowed the transfer-fidelity leg
"only if they clear the same gate"; that allowance is restored: E8 numbers enter the 4-pager
only from `summarize_e8`, fail-closed, in the pattern of `summarize_e0`/`summarize_e7`. Lane A/B
premise numbers and the taxonomy remain the submission's core; E8 is one paragraph and one table.

**(2) Correction of 0009's "the KV dumps are gone".** They are not. At the time of writing the
upstream checkout at `../kv-transfer-replication` holds `data/kv/qwen3-0.6b-to-1.7b` (50
sequences, 2.8 GB), `data/kv/qwen3-0.6b-to-1.7b-n420` (12 GB) and the fitted mappers
`mappers/qwen3-0.6b-to-1.7b/k{1,4,8}` -- all gitignored upstream, present on the operator's
machine only. Consequence: arm (a) needs no regeneration and E8 needs no GPU. The claim was
made from the upstream's git tree without checking the gitignored working tree; recorded so
the next reader does not repeat the inference.

**(3) The verdict-bearing mapper is k = 1.** Upstream held-out pooled R² at n = 50 (archived
`results/mapper/qwen3-0.6b-to-1.7b/r2.json`): k=1 K 0.681 / V 0.513; k=4 K 0.591 / V 0.336;
k=8 K 0.098 / V −0.641 (collapsed; p/n = 0.8). Entry 0009's band applies to k = 1 only; k = 4
and k = 8 are reported alongside and are verdict-bearing for nothing. A "drop" from a collapsed
baseline is not a measurement.

**(4) Arm (b) text-sampling rule, frozen before any dump.** One window per trajectory: the
first `seq_len` = 1024 tokens of the trajectory's visible messages concatenated in trace order,
each message prefixed by its role tag (`[system]`, `[user]`, `[assistant]`, `[tool]`) on its
own line, tool calls rendered as `name(arguments)`. Trajectories shorter than 1024 tokens are
skipped, never padded. n = 50 sequences, drawn with `rng.make_rng(8)` from the tau2-bench and
SWE-bench suites stratified equally (25 + 25), composio included (it is text, not a coverage
claim), tau-bench v1 excluded (below the agent floor, 0011). Tokenized with the pair's shared
Qwen3 tokenizer (`weights.assert_shared_vocab` checked first). Protocol otherwise identical to
arm (a): `--stride 4`, held out by sequence, `holdout_frac` 0.2. The text is off-policy for
Qwen (0009's scope limit stands) and, per 0012, omits every hidden prefix the provider billed.

**(5) Upstream change and re-pin.** No upstream script scores an EXISTING mapper on NEW dumps
(`kvt.mapper.mapper_r2` is library-only). `scripts/score_mapper.py` is added upstream (load
mapper + source/target dumps, hold out by sequence, write `r2.json` with the same keys as
`fit_mapper.py`), and `UPSTREAM.md` re-pins to `71df45043a799560e7631faa2b42a9cf3f2be3ad`. `config/e8.toml` carries the same
sha and `e8.assert_ready` refuses unless the upstream HEAD matches it with a clean tree for
every script E8 invokes. The "never import kvt" rule is unchanged: E8 calls the upstream by
subprocess in the upstream's own environment. The seal is not involved (0009).

**(6) What E8 reports.** For each k: arm (a) held-out K and V R² (recomputed by
`score_mapper.py` on the archived dumps and cross-checked against the archived `r2.json`,
refusing on disagreement beyond 1e-6), arm (b) held-out K and V R², and the drop (a − b).
The band outcome for k = 1 is stated by the summarizer as HOLDS / DEGRADES / UNRESOLVED
against 0009's numbers; the VERDICT on H-E8 enters only by a successor entry.

prior-entries-sha256: c2646932f5e5abf7235b72a1634f64df21ccb07de66eaeda0ae9389f4154e88b

### 0017 — 2026-09-02 — Composio adapter read half the family wrong; the headroom measure's `paid` was not the receiver's prefill. Figures of 0013 and 0015's ratio `[SUPERSEDED]`; verdicts stand

Found 2026-09-02 while building E9's alignment (a receiver prompt of median 685 tokens against a
sender context of 16,675 could not be "the whole transcript re-rendered"). Three defects, all in
the instrument, none in a registered rule:

**(1) A second shape inside the composio family.** The 20241016 submission lists LangChain message
nodes directly inside each sub-run. The 20241025 submission nests each sub-run's entire prompt as
ONE LIST node before the `LLMResult`. The adapter skipped non-dict nodes, so for 30 of the 60
files it read seven responses per file and no prompt at all: their tokens never entered the cost
totals, Lane A slices, or headroom. Detector breadth (0010) was not the failure; shape breadth
was. Fix: `e7_swe._flatten_nodes` -- nesting is flattened at any depth and nothing that is a dict
is dropped; a test pins the nested shape.

**(2) `paid` was the trajectory's cumulative prefix, not the receiver's prefill.** Entry 0010
defines `paid` as "the second stage's prefill tokens". The implementation summed every message
before the receiving turn -- three Claude solve threads plus the o1-mini prompt, ~6x the prompt
the o1-mini call was billed for. Fix: `Msg.request` records the request (LangChain sub-run) a
message belongs to; the receiver's prefill is the tokens of ITS request's messages preceding its
response; `measure` REFUSES a switch whose trace records no request boundary rather than fall
back to the prefix. The sender's processed content is unchanged (everything before the switch).

**(3) Messages were concatenated without a separator**, fusing the last word of one message with
the first of the next before whitespace tokenization. Fix: newline join. Minor; recorded because
the number moved.

**What is superseded.** Entry 0013's corpus row for composio and its headroom table (paid median
19,972; overlap 0.903; upper bound 81.3% of paid) are `[SUPERSEDED]` as figures -- the entry's
registration text and its provenance discipline stand. Entry 0015's H-E7a numerator, denominator
and ratio (2,339,562 / 165,959,914 = 1.41%) are `[SUPERSEDED]` as figures. **Neither verdict
changes**: H-E7a stays `NOT CONFIRMED` and H-E7b `UNESTIMABLE`; 0015's taxonomy class counts for
composio (68 switches, 68 re-renders, 60 of 60) are unaffected by (1)-(3) and stand.

**Recon, stated as recon** (fixed instrument, replay not yet on the record because this entry
was not yet committed when it ran): composio input tokens 244,739,122 (was 165,959,914); 68
switches, 0/68 byte-identical; overlap of the receiver's ACTUAL prompt with sender-processed
content median 0.988 (p10 0.972, p90 0.994) -- the o1-mini prompt is the re-rendered transcript,
almost entirely words the sender produced; receiver prefill median 7,492 tokens (p10 3,434, p90
15,442); upper bound 88.9% of paid; H-E7a ratio 496,798 / 244,739,122 = **0.20%** vs 10%. The
correction moves the ratio DOWN by 7x: the verdict was robust to the defect, the figure was not.

**What this changes going forward.** The corrected figures enter the record by the next entry,
from `summarize_e7` only, after this entry is committed. E9's registration (drafted as 0017,
band approved) becomes **0019**, and its handoff definition is request-level: `S` = everything
the sender processed up to its last response, `R` = the receiver's request prompt. The learnings
ledger carries the shape finding with a read-only re-verify line.

prior-entries-sha256: 41982f56a4f9fbfc6dc7bb6e6c306c68b7bbe358668ca35d298f119dcc1e63f3

### 0018 — 2026-09-02 — Corrected figures of 0013 and 0015's ratio `[BASELINE]`, through the fixed instrument

The figures below replace those superseded by entry 0017, recomputed by `summarize_e7` from the
raw traces with the corrected adapter and measure (config sha256 6915666d452d;
188 trace files hashed; refusal on any disagreement). Registered rules unchanged;
the verdicts of 0015 stand as stated there.

**Corpus (composio family, both submissions, prompts now read in full):** 60 trajectories,
6377 requests, 244,739,122 input tokens (visible-only LOWER BOUND, 0012).

**Headroom at the 68 observed Lane A switches** (replacing 0013's table; read_mult
0.1; `paid` is now the receiver's own request prefill per 0017):

| figure | value |
|---|---|
| byte-identical handoffs | **0/68** |
| overlap of the receiver's ACTUAL prompt with sender-processed content | 0.988 (p10 0.972, p90 0.994) |
| receiver prefill at the switch, tokens (visible-only LOWER BOUND) | 7,492 (p10 3,434, p90 15,442) |
| headroom UPPER BOUND as a fraction of paid | **88.9% (p10 87.5%, p90 89.5%)** |

The corrected overlap is HIGHER than 0013's superseded figure and nearly total: the o1-mini
prompt is the re-rendered transcript, almost entirely words the sender produced. The corrected
prefill is much smaller: the receiving stage pays for its own prompt, not the trajectory's
history. Both move the same direction for the program's thesis -- the one observed handoff
pattern re-pays a nearly fully redundant prompt, and that prompt is small.

**H-E7a ratio, restated** (rule unchanged: 0006 cutoff, Lane A alone per 0007, measurable-subset
denominator per 0014): recoverable upper bound 496,798 / input spend
244,739,122 over 60 measurable trajectories = **0.20%** vs
10%. The correction moved the ratio DOWN from the superseded 1.41%: H-E7a's
`NOT CONFIRMED` verdict (0015) stands, now by a wider margin. No other verdict is touched.

This entry decides nothing new; it puts the corrected numbers where the superseded ones stood.

prior-entries-sha256: 5942c0b61b7f5bd3a92c2e5d0d8eeb7ed8de47b45aa34a5108decf4687fcbcf0

### 0019 — 2026-09-02 — E9 registered: the achievable fraction of the headroom upper bound at a re-rendered handoff (H-E9, band frozen)

Entry 0013 (figures corrected by 0017/0018) records headroom as an UPPER BOUND and states that
the achievable fraction is not measured. E9 measures it, on the observed handoffs, on the A100
the plan names (`docs/2026-09-01-lcfm-gpu-plan.md`). Band numbers approved by the operator
2026-09-01; this entry was drafted as 0017 and renumbered by the 0017 correction.

**Unit.** One observed Lane A switch (entry 0010; 68 at the time of writing), defined at the
REQUEST level per 0017: sender context `S` = everything the sender processed up to and
including its last response before the switch; receiver prompt `R` = the receiver's own
request prompt (the messages of its request preceding its response), never the trajectory
prefix. Both as text from the registered adapter (`e7_swe.load_composio_detailed`, which
records `Msg.request`), the same slices `e7_headroom.measure` prices.

**Alignment, registered method.** Tokenize `S` and `R` with the pair's shared Qwen3 tokenizer
(no special tokens); match tokens by the longest-matching-blocks algorithm of Python's
`difflib.SequenceMatcher` over token ids with `autojunk=False` (Ratcliff/Obershelp: the longest
common contiguous block, then recursively left and right; deterministic; yields a common
subsequence, in general shorter than the true LCS, so `|M|` is a floor). The matched set `M`
carries a position pair `(p_S, p_R)` per token. `|M| / |R|` is reported beside entry 0010's
word-multiset overlap. Exact LCS was not chosen because it is quadratic in 32k-token
sequences; the method is named so the number reproduces.

**Two measurements, both pooled R² (definition A5, provenance per UPSTREAM.md), K and V
separately, over `M` only:**

- **E9-same** (the ceiling under re-rendering, independent of any mapper): the receiver model
  Qwen3-1.7B prefills `S` and `R` natively; its K/V at `p_S` are re-roped to `p_R` in content
  space and compared against its own K/V at `p_R`. This is how much of a content-matched
  token's KV survives a different preceding context -- the achievable ceiling for ANY transfer
  across this handoff.
- **E9-cross** (the transfer): Qwen3-0.6B prefills `S`; the existing k = 1 content-space mapper
  (0016) is applied with receiver positions `p_R` (`kvt.mapper.apply_mapper`, upstream) and
  compared against the receiver's K/V at `p_R`. Reported as an absolute R² and as a fraction of
  E9-same, so mapper error and re-render loss are never conflated.

**H-E9** (registered in the table): *at a re-rendered handoff, same-model KV agreement on
content-matched tokens retains the transfer-relevant fidelity.* **Band, frozen here before any
prefill:** per-handoff E9-same K R², median over included handoffs: **HOLDS if >= 0.70;
DEGRADES if <= 0.40; UNRESOLVED between.** V is reported alongside and is verdict-bearing for
nothing. Reason for 0.70: it is the k = 1 mapper's own same-text held-out K R² (0.681), so
HOLDS means "the re-render costs no more than the mapper itself does".

**Scope limits, registered up front.** Context cap 32,768 tokens (Qwen3 native): a handoff
with `|S|` or `|R|` above the cap is EXCLUDED and counted; coverage (included / observed) is
stated with every figure and nothing is truncated. Text is off-policy for Qwen. One pair.
Composio is one system (0011). E9 bounds what a transfer could recover at the one public
instance of the use case; it says nothing about routing frequency (H-E7a's domain) and must
never be written as a real mid-trajectory transfer.

**Dumps and what is kept.** Every position of `S` and `R` is dumped with the upstream's
existing `dump_kv.py` (`--stride 1`, one sequence per file; no new dump code). A handoff's three
dumps (receiver on `S`, receiver on `R`, source on `S`) are up to ~11 GB, so they are scored
and deleted per handoff; what is kept per handoff is the alignment, the per-layer, per-head
sums of squares (SSE and SST, for E9-same and E9-cross, K and V) and the R² derived from them.
A seeded keep-subset of handoffs (seed and size in `config/e9.toml`, drawn before any prefill)
retains its full dumps, fingerprinted, so a CPU summarizer can recompute those R² from tensors.

**Enforcement.** `e9.assert_ready` refuses until this entry and `config/e9.toml` are committed
unmodified and the upstream is at a pinned commit that adds `scripts/score_positions.py` (the
scorer; a re-pin recorded in `config/e9.toml` and `UPSTREAM.md`) with a clean tree for every
path E9 invokes. Per-handoff checkpoints are synced off the GPU box after each handoff.
`summarize_e9` recomputes the alignment of every handoff from the raw traces, recomputes every
R² from the recorded moments, recomputes the keep-subset's moments from its fingerprinted
tensors by re-running the scorer, recomputes the medians and the band outcome, and refuses on
any disagreement. What it cannot do on CPU is regenerate the deleted dumps: for those handoffs
the moments are a GPU-run record, verified by the keep-subset, and the entry that states the
verdict must say so. The seal is not involved: no mapper is fitted.

prior-entries-sha256: 88bb14f51ffcbdd696a5c8886077a6ef0ce598505d8057359840403f0348cd81

### 0020 — 2026-09-02 — E8 ran `[BASELINE]`; H-E8 NOT CONFIRMED

**Provenance.** Design and band per 0009, amendments per 0016; gate passed with the committed
ledger and the upstream pinned at `71df45043a79` (clean tree for every invoked
path). Every figure recomputed by `summarize_e8` re-running the upstream scorer on the
fingerprinted dumps and cross-checking arm (a) against the archived `r2.json` for every k
(config sha256 32307787248a; agent token file sha256 9aa8ffc04c06, manifest
hashed). Two independent end-to-end executions produced a byte-identical arm (b) token matrix
and identical R² -- an unplanned determinism check, recorded here.

**Held-out pooled R² (definition A5), generic calibration text vs agent-trace text, the
EXISTING mappers, no refit:**

| k | arm (a) generic K / V | arm (b) agent K / V | drop K / V | band K / V |
|---|---|---|---|---|
| 1 (verdict-bearing) | 0.6814 / 0.5133 | 0.5629 / 0.3418 | +0.1185 / +0.1715 | UNRESOLVED / DEGRADES |
| 4 (reported only) | 0.5907 / 0.3361 | 0.3523 / -0.0796 | +0.2384 / +0.4158 | DEGRADES / DEGRADES |
| 8 (reported only; k=8 from a collapsed baseline, 0016) | 0.0984 / -0.6412 | -0.6280 / -2.1380 | +0.7263 / +1.4968 | DEGRADES / DEGRADES |

**H-E8 -- NOT CONFIRMED.** The registered claim is that the mapper "retains its held-out pooled R²
when the KV states come from agent-trace text, within the tolerance band, K and V separately"
(0009), verdict-bearing at k = 1 (0016), neither read-out alone (0009). At k = 1 the V drop
(+0.1715) is DEGRADES and the K drop (+0.1185)
is UNRESOLVED (inside the registered dead band): retention FAILS for V and is NOT ESTABLISHED
for K, so the claim as registered is NOT CONFIRMED. The direction is consistent at every k, and V
degrades more than K everywhere -- content shift hits the value pathway harder than the key
pathway on this pair.

**Scope, carried from 0009/0016 and binding on any use of these numbers:** the text is
off-policy for Qwen (content distribution shift only, never on-policy agent behaviour); one
pair, one calibration size (n = 50, where k = 4 is already partly and k = 8 fully collapsed);
NOT a transfer at a real switch point; arm (b) text is visible-messages-only and omits every
hidden prefix the provider billed (0012). H-E8's verdict cell changes to `NOT CONFIRMED` with this
entry.

prior-entries-sha256: 65615f84d33ee898f5c585f470ff7faa7732e96de94a67e8b24ba00452b08d35

### 0021 — 2026-09-01 — Erratum: heading dates of 0016–0020; Lane B reported descriptive `[BASELINE]`, its dollar counterfactual WITHDRAWN

**(1) Dating erratum.** The headings of entries 0016, 0017, 0018, 0019 and 0020 carry the date
2026-09-02. All five were authored on **2026-09-01** (commit author dates 2026-09-01, the
latest 18:17 −0400; the same calendar day in UTC). The wrong dates were supplied by the
session assistant on a timezone assumption and propagated; registered heading text is
immutable under the entry chain, so the correction is recorded here rather than by edit. The
same slip is in the filenames `docs/2026-09-02-*.md`, the 2026-09-02 handoff brief, and the
`ts:` field of the learnings entry `2026-09-02-a-family-has-two-shapes-and-a-prefix-is-not-a-
prefill.md` (stamped hours late; the three later learnings entries carry correct UTC capture
stamps). Why this is on the record at all: this repo uses commit timestamps as ordering
evidence (entry 0004), and COMMIT timestamps remain correct throughout — the erroneous dates
are labels, not evidence — but a reader reconciling heading dates against `git log` deserves
the discrepancy explained rather than discovered.

**(2) Lane B, disposed of explicitly.** Entries 0005/0006 registered switch-point headroom
with Lane B (the counterfactual two-tier cascade) as a reported lane; entry 0007 then ruled
Lane B descriptive-only and verdict-bearing for nothing, because it inserts a switch at every
boundary of a policy this program chose — it measures the policy, not the workload. No entry
since has reported Lane B at all, leaving a registered output dangling. Resolved here, in two
parts:

- **Reported, descriptive `[BASELINE]`** — the labelled counterfactual under the registered
  cascade policy (plain assistant turns on the large tier, tool-calling turns on the small
  tier; every tier boundary a switch point), recomputed by `summarize_e7` from the raw traces:

| suite | trajectories | assistant turns | tier boundaries (Lane B switch points) |
|---|---|---|---|
| swe-bench | 124 | 9,589 | 4,884 |
| tau-bench | 1980 | 26,316 | 13,839 |
| tau2-bench | 800 | 9,714 | 4,642 |
| **ALL** | 2904 | 45,619 | 23,365 |

  Read as registered: IF an operator ran this cascade over these workloads, context would
  cross a model boundary this often. It is a property of the policy applied to these traces,
  labelled counterfactual-under-stated-policy, and comparable to Lane A's 68 observed
  switches only as an illustration of how far the counterfactual outruns observed practice.

- **WITHDRAWN — Lane B's headroom-in-dollars output.** Pricing the counterfactual boundaries
  would manufacture a large transfer-headroom figure whose magnitude is fixed by the policy
  choice, not by any observed workload (0007's "material by construction"). It was never
  computed, and this entry withdraws it as a registered output rather than leaving it
  implicitly pending. Reinstating it would take a new numbered entry registering a policy with
  independent evidentiary standing. No hypothesis cell changes: H-E7a was decided by Lane A
  alone (0007, 0015, 0018) and Lane B never had a hypothesis.

prior-entries-sha256: 50d9bd4ffde65814712ff8b3a532f0e4f611e3e6220edeb53b419872f7f68209

### 0022 — 2026-09-01 — Entry 0009's SWE-bench calibration precondition was not met by 0013/0015/0018; the verdicts stand by bound and by measurement

**The breach, recorded.** Entry 0009 registered the per-content-type divisors as descriptive of
tau-bench and said, verbatim: "the divisors are descriptive of tau-bench and are NOT claimed to
transfer to another suite. **SWE-bench requires its own calibration before its numbers ship.**"
That calibration was never done, and SWE-bench numbers shipped anyway: the headroom figures of
0013 (since superseded) and 0018, and the H-E7a ratio of 0015 (superseded) and 0018, all count
SWE-bench text with tau-bench-calibrated divisors. tau2-bench is not in the same position: its
counts were validated against provider-reported usage (entry 0012's ground-truth check), which
is a stronger per-suite check than calibration. SWE-bench had neither. Event counts, coverage,
and the taxonomy are untouched (they count events, not tokens).

**Why the verdicts stand — the bound.** H-E7a is a RATIO of token counts made by the same
counter over overlapping content: a uniform miscount cancels exactly, and only the differential
per-content-type bias can move it. Entry 0009 measured that bias at at most ~28% for any single
content type; numerator and denominator share their content mix closely enough that the ratio
cannot plausibly move by the ~50x needed to reach the 10% cutoff.

**The measured sensitivity (recon, stated as recon — computed by this entry's append script at
append time, not retyped; the calibrated side agrees with the summarizer-verified record).**
Recounting the entire composio family with exact `o200k_base` in place of the calibrated
divisors — exact is the TRUE billed encoder for the 64 of 68 switches whose
receiver is o1-mini, and a labelled proxy for the 4 Claude-receiver switches and for
the Claude-thread denominator text:

| figure | calibrated (the 0018 record) | o200k exact | exact / calibrated |
|---|---|---|---|
| composio input tokens (H-E7a denominator) | 244,739,122 | 255,690,850 | 1.0447 |
| recoverable upper bound (H-E7a numerator) | 496,798 | 565,025 | 1.1373 |
| **H-E7a ratio, measurable subset** | **0.2030%** | **0.2210%** | 1.0886 |
| receiver prefill at the switch, median tokens | 7,492 | 8,620 | — |

The calibrated counter undercounts the o1-mini receiver prompts (code-heavy re-rendered
transcripts) by roughly the numerator ratio above; the miscalibration therefore worked AGAINST
the verdict, and correcting it moves the ratio from 0.203% to 0.221% — still
roughly 45x under the cutoff. The upper-bound fraction of paid is unchanged
(~88.9%; it is ~0.9 x overlap and
insensitive to the counter). Both remain visible-messages-only LOWER bounds (0012).

**Disposition.** The verdicts of 0015/0018 (H-E7a `NOT CONFIRMED`) stand under both the bound
and the measurement. 0018's calibrated figures remain the record — they are what the
registered counter produces — with this entry as their registered sensitivity. The proper
repair is a successor to 0009 in the MLSys cycle: per-suite calibration or exact-where-the-
true-encoder-is-public as a config change (bundled with the pending gpt-4.1 exactness item),
after which one replay supersedes the figures once, not piecemeal. Until then, no further
SWE-bench token figure ships without citing this entry's sensitivity.

prior-entries-sha256: e275cb5a4b45dc3a2bb3dcd69b1a9802347c39248a46ab0368799d36e2ea2d63

### 0023 — 2026-09-01 — E9 rule amended before any prefill: per-token deviation and oracle selective-recompute fraction replace pooled R² as the verdict statistic; controls and seam profile registered

**Precondition, on the record.** `results/e9/` holds no report and no score file; `linear_ceiling.e9`
has been invoked only with `--check` (the interactive shell histories carry no `e9` invocation
at all -- the gate checks ran from the session assistant -- so the evidence is the absence of
`results/e9/report.json` and `results/e9/scores/`, and the LCFM plan's "BUILT and gated, not
run" line). This amendment is legitimate only while that holds; the append script that wrote
this entry refuses otherwise. 0019's unit, alignment, S/R slices, cap, exclusions, keep-subset
and H-E9 statement stand; 0019's **rule clause only** is superseded here. The H-E9 row of the
hypotheses table embeds 0019's rule text in its statement cell; under the house rule (only the
verdict cell changes) that text is left as registered and is read as superseded by this entry
(a note above the table says so).

**Why amend before the box.** Pooled R² (A5) was borrowed so E8 could be compared against the
archived mapper record; it did that job. For E9 it is the wrong instrument: it is dominated by
the highest-variance tokens and dimensions, so a handoff where 90% of matched tokens survive
exactly and 10% are destroyed can post the same figure as one where every token is moderately
wrong; and it has no tail, whereas the non-prefix-reuse literature asks *which* tokens deviate
and *how many* must be recomputed. R² stays as a bridge (below) and decides nothing.

**Per-token deviation, registered.** For matched token `t` in `M` with positions `(p_S, p_R)`,
layer `l`, KV head `h`, read-out `X` in {K, V}: `x_R(t,l,h)` is the receiver's own KV at `p_R`
and `x̂(t,l,h)` the candidate -- **E9-same**: the receiver's own KV at `p_S`; **E9-cross**: the
k = 1 content-space mapper (0016) applied to the source's KV at `p_S` -- both compared in
content space (K_stripped; V unrotated), exactly as the pinned scorer does. The centered
deviation

    δ(t,l,h) = ‖x̂(t,l,h) − x_R(t,l,h)‖²₂ / (SST(l,h) / |M|),   SST(l,h) = Σ_t ‖x_R(t,l,h) − x̄_R(l,h)‖²₂

is the token's share of the layer-head's unexplained variance, **in R²'s own units**: its mean
over `t` is exactly 1 − R²(l,h), and its mean over `t`, `h`, `l` is exactly 1 − the recorded
head-averaged, layer-averaged R². **It is not "this token's KV is x% wrong"** (rider 2): a seam-bin
value of 0.6 means those tokens carry unexplained variance at 0.6 of the per-token average
scale, not that they are 60% wrong. The seam and depth profiles below inherit this unit. The
seed's original own-norm deviation `‖d‖² / ‖x_R‖²` is kept as a labelled diagnostic only: it is
dominated by the per-head mean vector (on the archived held-out set its K mean is
0.084 while 1 − R² is 0.319) and blows up on small-norm tokens
(0.66% of held-out V tokens exceed 1, max 5.8; the
smallest per-layer V reference norm is 0.35% of the layer median). The
count of own-norm tokens over 1 is reported alongside every E9 figure as a diagnostic, nothing more.
Per-token δ(t) = mean over `h` then `l`; per-layer δ(t,l) = mean over `h`.

**Oracle selective-recompute fraction f*(τ).** Sort matched tokens by δ_K(t) descending; f*(τ)
is the smallest fraction of `M` that, removed (recomputed exactly), leaves the MEAN δ_K over the
remaining tokens at or below τ (judged to 1e-9 relative, so the float32 record cannot cost a
token). It is an **oracle LOWER BOUND** on real selective recompute for two stated reasons: it
assumes a recomputed token is restored exactly, and it ignores that real partial prefill
(CacheBlend-style) recomputes the selected tokens *against the reused KV of the others*, so
errors propagate. Every output stating f* carries the words "oracle lower bound" and both reasons.

**τ, calibrated from the archive before any prefill, per read-out (rider 3).** τ_X = 1 − the
archived k = 1 mapper's held-out R²_X on its own generic held-out sequences (the last 10 of the 50
archived `data/kv/qwen3-0.6b-to-1.7b` dumps, stride 4, 2560 tokens) -- i.e. the mapper's
own MEAN centered deviation, so the mapper's own f*(τ) is 0 by construction and HOLDS keeps
0019's meaning, "the re-render costs no more to repair than the mapper itself". The instrument,
described as it is: R² is **A5 per head, averaged over heads, then over layers**
(`kvt.mapper.mapper_r2`; `score_positions.py` does the same per layer), NOT "pooled over rows and
columns" as 0019 and UPSTREAM.md phrase it; true pooling over a layer's heads gives K
0.6917 / V 0.5267 against the head-averaged
0.6814 / 0.5133, recorded here so the discrepancy is on the record
rather than discovered later. Hence, from `summarize_e9 --calibrate-tau` (archived `r2.json`
sha256 `18d2276f28e9`, cross-checked to 1e-6 against E8's arm (a) record and the
archived dumps against E8's fingerprints; the per-token record reproduces 1 − R² per head to
2.9e-15):

- **τ_K = 0.3186** (= 1 − 0.6814), verdict-bearing;
- **τ_V = 0.4867** (= 1 − 0.5133), for the alongside f* only; never mixed with K.

Why the mean and not the median (the seed's first draft): with τ at the median of the mapper's
own per-token deviation the mapper fails its own calibration -- its f* is
6.2% (K) / 5.1% (V) under the own-norm
deviation and 7.3% / 6.2% under the centered one -- so a
re-render exactly as good as the mapper would spend that much of the HOLDS budget on an artifact
of the statistic. Both values are in `tau.json`; the calibration script refuses to write a τ at
which the mapper's own f* is not zero. τ enters `config/e9.toml` from the script's output and the
summarizer recomputes it under the pin and refuses on disagreement (1e-9).

**Seam distance b(t).** From the alignment alone, no GPU: a seam is a receiver position not in
`M`, or the boundary between two receiver-adjacent matched tokens whose sender positions are not
consecutive (a reordering); b(t) = the number of receiver positions strictly between `p_R(t)` and
the nearest seam (0 = adjacent). A receiver prompt matched end to end with no reordering has no
seam and every token reports b = |R|.

**Rule and band (supersedes 0019's rule clause only).** H-E9 is decided by **median f*(τ_K) over
included handoffs, E9-same, K read-out**:

- **HOLDS** if median f*(τ_K) ≤ 0.15 -- anchored to CacheBlend (Yao et al., EuroSys 2025): the
  10–15% of high-KV-deviation tokens it recomputes to recover full-prefill quality under
  non-prefix reuse. The re-render costs no more to repair than a same-model reuse the literature
  already accepts.
- **DEGRADES** if median f*(τ_K) ≥ 0.50 -- **the operator's stated judgment, not a citation**
  (rider 1): recomputing half or more of the matched tokens leaves no case for reuse across this
  handoff. The seed claimed a literature anchor for both edges; only one exists, and no second
  citation is manufactured here.
- **UNRESOLVED** between.

V's f*(τ_V) is reported alongside on every figure and is verdict-bearing for nothing (0019
unchanged). E9-cross is reported as its own f*(τ_K) / f*(τ_V) and as the ratio of its median δ
to E9-same's, per handoff, never merged. The head-averaged R² (K and V, same and cross) is
reported alongside as the bridge to 0016/0020 and decides nothing. Nothing in this section may be
revisited after the first score file exists.

**Controls and descriptive outputs (registered; decide nothing).** (1) *Pipeline identity*: on
the first included handoff, before any handoff is scored, the receiver's dump of `S` scored
against itself at pairs (p, p) must give every per-token square exactly 0; a nonzero HALTS the
run. (2) *δ_null*, the uninformative scale: the same handoff scored with each receiver position
paired to the sender position of a different matched token (seeded derangement, `null_seed` =
23 in `config/e9.toml`); its median δ per layer and per token is the top of the scale so a δ of
0.3 is read against unrelated content, not in the abstract. (3) *Seam profile*: median δ_K (and
δ_V alongside) by b(t) in the fixed bins 0 / 1 / 2–3 / 4–7 / 8–15 / 16+, pooled over included
handoffs and per handoff; no bin is added or merged after data. It is the descriptive finding
that speaks to the reuse literature's central claim -- deviation concentrating at chunk
boundaries -- measured on real re-renders instead of synthetic chunk insertion. (4) *Depth
profile*: median δ_K and δ_V per layer, pooled, on one axis, reported beside 0020's K/V
asymmetry without asserting the two are one effect.

**Instrument and record.** The upstream scorer `scripts/score_positions.py` gains `--per-token`
(and `scripts/score_mapper.py` the same, for the calibration): per-token, per-layer, per-head
squared deviations for K, V, same, cross plus the receiver's own norms, float32 `[|M|, L, H]`,
with the recorded per-head SSE now the float64 sum of exactly those squares (test upstream:
sums reproduce the moments; identity gives exact zeros; centered mean equals 1 − R² per head).
Roughly 43 MB per handoff, synced off the box with the checkpoints. Re-pin recorded in
`config/e9.toml` and `UPSTREAM.md` (the commit that adds `--per-token`; 0019's pin `7e41f792`
remains its ancestor).

**Enforcement.** `e9.assert_ready` refuses until this entry and `config/e9.toml` are committed
unmodified and the re-pin holds (a placeholder pin refuses by name). `summarize_e9` additionally:
checks every per-token record sums to its recorded moments; re-runs the keep-subset scorer with
`--per-token` and compares the squares; re-runs the τ calibration under the pin and compares
with the recorded `results/e9/calibration/tau.json` (gitignored like every `results/` artifact; its figures live in this entry and in config) and with config; verifies the identity
record is exactly zero and the null pairing re-derives from the seed; and only then states f*,
the seam and depth profiles, δ_null, the bridge R² medians and the band outcome -- refusing on
any disagreement. Deleted dumps stay a GPU-run record verified by the keep subset (0019).

**`[STRETCH]`, registered, own entry before anything runs:** real CacheBlend-style partial
prefill -- recompute the top-f tokens against the reused KV, measure attention-output deviation
and a downstream task delta. Needs injection code upstream and a task; it is the experiment that
would make f* an achieved number rather than an oracle floor. Named so its absence is a stated
gap, not an omission.

**Scope limits.** All of 0019's (32,768 cap with exclusions counted and coverage stated;
off-policy text; one pair; one system; never a real mid-trajectory transfer), plus: f* is an
oracle lower bound (two reasons above) and the seam profile is descriptive; neither is a claim
about what a deployed reuse scheme would achieve. No hypothesis cell changes with this entry.

prior-entries-sha256: 50ee4f2b68fbbb6bb103443f3330f6156f982404f04df71c916d7eacbca2b800
