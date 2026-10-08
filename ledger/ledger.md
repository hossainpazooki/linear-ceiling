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
| H-E9 | (achievable fraction of the headroom upper bound at a re-rendered handoff) at a re-rendered handoff, same-model KV agreement on content-matched tokens retains the transfer-relevant fidelity. Rule (entry 0019, band approved 2026-09-01, frozen before any prefill): per-handoff E9-same pooled K R² (definition A5) at LCS-floor matched positions, median over included handoffs — HOLDS >= 0.70, DEGRADES <= 0.40, UNRESOLVED between; V reported alongside, verdict-bearing for nothing; handoffs over the 32,768-token cap excluded and counted. Row added with 0019's commit set completion — the entry says "registered in the table" and the row was initially missing (process slip, noted in the handoff; the entry text is immutable and unchanged). | E9 (band in entry 0019) | HELD |
| H-E9L | (E9's claim on the long half) at a re-rendered handoff whose sender prompt exceeds the prior cap of 32,768 tokens, same-model KV agreement on content-matched tokens keeps its usefulness under a receiver extended to 81,920 positions by static YaRN. Rule verbatim from entry 0023: median over the newly included handoffs of the oracle selective-recompute fraction f*(τ_K = 0.3186) on the K read-out, HOLDS ≤ 0.15 / DEGRADES ≥ 0.50 / UNRESOLVED between; decided on the 35 newly included handoffs only, never pooled with 0029's 25; read on a floor (0027) and, if the bridge control exceeds 0.15, as a claim about the scaled receiver only. Registered by entry 0035 before any prefill. | E9-long (entry 0035) | HELD |
| H-E9F | (E9's claim on a second model family) at a re-rendered handoff whose sender and receiver prompts both fit 32,768 tokens under the pair's own tokenizer, same-model KV agreement on content-matched tokens retains the transfer-relevant fidelity on meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B — a matched-KV cross-release pair with a natively long receiver, neither side scaled. Rule verbatim from entry 0023: median over the included handoffs of the oracle selective-recompute fraction f*(τ_K = 0.2861) on the K read-out, HOLDS ≤ 0.15 / DEGRADES ≥ 0.50 / UNRESOLVED between; τ_K is 1 − THIS pair's own k = 1 held-out R² (entry 0040) and is never Qwen's; decided on this pair's 28 included handoffs — or, under the stopping rule this entry registers, on a PREFIX of them in `n_sender_asc` order with its coverage stated — never pooled with entry 0029's 25 — the same numeric cap over a different tokenizer is a different set of handoffs; read on a floor (0027). Registered by entry 0042 before any prefill. | E9-family (entry 0042) | HELD |

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

### 0024 — 2026-09-01 — Corpus manifest committed; SWE-bench selection rule recorded; overlap null controls and cache-aware H-E7a readings `[BASELINE]`; no verdict changes

**Manifest.** `config/e7-manifest.json` (canonical-JSON sha256 `371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094`): 188 files over three
suites; S3 key, ETag and size for 180 SWE-bench objects (anonymous listing of
`s3://swe-bench-submissions/verified/<submission>/trajs/`, retrieved 2026-09-01T23:41:46+00:00).
`e7.assert_ready` refuses until it is committed unmodified; the driver and `summarize_e7` refuse on any
disagreement between disk, report and manifest (a file on disk the manifest does not list, a listed file
absent or with different bytes, a report not produced against this manifest -- tamper tests
`tests/test_e7_manifest.py`, `tests/test_summarize_e7.py`). Every E7 figure from this entry on carries the
manifest sha beside the config sha (`ledger_check` enforces the citation), and `config_sha256` is now the
newline-normalized digest so a CRLF checkout cites the same `d16cf4659aab` as an LF one.

**Selection rule, as recovered (not assumed).** Local instance set vs the full listing, per submission:
  - `20240820_honeycomb`: 15 of 500 listed instances (rule: first-N in listing order; listing positions 0..14)
  - `20241016_composio_swekit`: 30 of 498 listed instances (rule: first-N in listing order; listing positions 0..29)
  - `20241025_composio_swekit`: 30 of 499 listed instances (rule: first-N in listing order; listing positions 0..29)
  - `20241125_marscode-agent-dev`: 15 of 500 listed instances (rule: first-N in listing order; listing positions 0..14)
  - `20250122_autocoderover-v2.1-claude-3-5-sonnet-20241022`: 4 of 500 listed instances (rule: first-N in listing order; listing positions 0..3)
  - `20250415_openhands`: 15 of 500 listed instances (rule: first-N in listing order; listing positions 0..14)
  - `20250616_Skywork-SWE-32B`: 15 of 500 listed instances (rule: first-N in listing order; listing positions 0..14)
Every submission's local set is the first N objects of its S3 listing (first-N in listing order) -- listing order is UTF-8 key order, so the subset is the ALPHABETICALLY FIRST N instances of each submission (astropy-dominated), not a random draw. Bearing: none on Lane A (all 60 composio files present, both submissions); the pooled
taxonomy rows over SWE-bench are a SELECTED SUBSET and are labelled so from here on (coverage stated
beside them: entry 0011 units).

**Overlap null controls (`summarize_e7 --overlap-null`, seed 24, same measure and quantile
convention as 0010/0018).** Observed: overlap 0.988 (p10 0.972, p90 0.994), headroom upper bound
88.9% (p10 87.5%, p90 89.5%) of paid. Same-family null (each receiver prompt against the
sender context of a different composio trajectory, seeded derangement): overlap
0.498 (p10 0.311, p90 0.574), upper bound 44.9% (p10 28.0%, p90 51.7%). Cross-family null
(against a seeded random SWE-bench role/content trajectory's full text, pool 64): overlap
0.386 (p10 0.205, p90 0.499), upper bound 34.7% (p10 18.5%, p90 44.9%). What this says:
roughly half of the receiver's words are template vocabulary any composio prompt shares (the same-family
null), about 39% is vocabulary any SWE-bench transcript shares; the
observed 0.988 sits 0.490
above the same-family null, so the 0018 figure is a bound on task-content redundancy over and above the
template, not on template vocabulary alone. It is still an UPPER BOUND (0010). Decides nothing; E9 is the
instrument that measures the achievable fraction.

**Cache-aware readings of H-E7a's denominator (`summarize_e7 --cache-aware-ratio`; numerator unchanged
496,798; Lane A measurable subset per 0014; base-input-price units).**
Registered requests (each assistant turn re-bills the trajectory prefix, as priced in 0015/0018): COLD
244,739,122 -> **0.20%** (= the 0018 figure by construction);
WARM (previous prefix at read_mult, new messages at write_mult) 27,354,947 ->
**1.82%**. Request-level requests (entry 0017's reading of `paid`, applied to every
request: each LLM call's own prompt; 444 requests): COLD 4,967,377 ->
**10.0012%**; WARM (byte-identical prefix shared with the preceding request --
7.6% of request-level prefill tokens -- at read_mult, remainder at
write_mult) 5,775,842 -> **8.60%**. Cutoff 10%.
Beside 0022's exact-tokenizer sensitivity (0.2210% under the registered reading).

**Verdict, re-examined under each reading of "input-token spend" (rule as written, 0006/0007/0014).**
Under the registered reading, priced cold or warm, H-E7a `NOT CONFIRMED` stands
(0.20% / 1.82% vs 10%). Under the request-level reading
the ratio is AT OR ABOVE the cutoff for: request_cold --
10.0012% cold, 8.60% warm. Two things bind the reading of that
number: the numerator is an UPPER BOUND (0010, re-rendering changes every position) and every denominator
is a visible-only LOWER BOUND (0012, the warm bounds more so, because the hidden block is the most
cacheable content), so the true request-level ratio is strictly below the 10.0012% stated;
and 0006's wording does not say which reading it means. **This entry does not change the cell**: the
registered reading is the one 0014/0015/0018 decided under, and choosing between readings is a
registration act -- a successor to 0006/0014 must fix the reading BEFORE any verdict is restated under
it. Until then H-E7a's `NOT CONFIRMED` stands as decided, with the request-level reading on the record
as the reading under which it would not.

No `verdict:` line: no cell changes. Figures: `summarize_e7 --overlap-null --cache-aware-ratio`
(results/e7/recon.json), config sha256 d16cf4659aab, 188 trace files verified.
e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 43879637a17e16e38afec2dd2134fef53fbc33020ab1288e02941b151708fbaa

### 0025 — 2026-09-02 — E9 amended before any prefill: coverage registered; agent-text τ alongside; prefix-invariance control; causal seam distance; block lengths; bootstrap; τ ladder; keep-subset 3 → 8; no verdict changes

**Why before the box.** An independent pre-run review of E9 (2026-09-02) and the E-RL design each
proposed additions to what E9 reports and controls. None touches the H-E9 rule, τ_K = 0.3186, the
band, or the four cells; every one of them is of the kind 0023 forbids after the first score file
exists, so they are registered together here. No prefill has happened: `results/e9/report.json` is
absent at append and this script refuses otherwise. Nothing in this entry is verdict-bearing.

**Coverage, registered (review finding 1).** 0019's alignment over the observed handoffs at the
registered cap 32768: **25 included of 68 observed** (39 excluded because `S` or `R`
exceeds the cap, 4 because the receiver prompt is empty in the trace). The excluded handoffs
are the long ones, and what the cap selects on is stated beside every E9 figure from here on:
included vs excluded-by-length, medians (p10, p90) -- |S| 25,460 (p10 14,269, p90 30,106) vs 52,141 (p10 35,692, p90 147,218);
|R| 6,551 (p10 4,148, p90 9,165) vs 11,500 (p10 7,085, p90 20,589); entry 0018's per-handoff overlap
0.985 (p10 0.978, p90 0.990) vs 0.989 (p10 0.983, p90 1.000); 0018's recoverable fraction
0.886 (p10 0.880, p90 0.891) vs 0.890 (p10 0.885, p90 0.900) (0018 rows from the E7 report verified by
`summarize_e7` at append, sha256 `0aba0fbe7aba`; 0 handoffs without a row). H-E9 is decided on the
included set and is a claim about it; `summarize_e9` recomputes this comparison and states it.

**Agent-text τ, alongside (review finding 2).** τ_K anchors HOLDS to "no more than the mapper itself"
on the mapper's own GENERIC held-out text (0023). Entry 0020 arm (b) measured the same k = 1 mapper on
AGENT text at K R² = 0.4371, so on the distribution E9 actually reads, the mapper's own tolerance
is **τ_agent_K = 0.4371** (= 1 − 0.4371, recomputed by `summarize_e9 --calibrate-tau` from
`results/e8/report.json` and refused on disagreement, like τ_K). f*(τ_agent_K) is reported for the K
arms (E9-same and E9-cross) beside f*(τ_K), per handoff and as medians. It is a K tolerance and is
applied to nothing else. **The band reads τ_K only**; this entry does not move it -- a verdict-bearing
τ chosen after seeing which is looser is exactly what 0023 refused to do -- but the reader sees both.

**τ ladder (descriptive; E-RL design).** f*(τ) is ALSO stated at τ_K ∈ {0.3186, 0.1, 0.03} and
τ_V ∈ {0.4867, 0.1, 0.03} -- the registered value first, then `[e9.rule] tau_ladder` -- for every arm, per
handoff and as median / p10 / p90, from the same per-token record (a re-sort). It reads *how far
inside* the tolerance the re-render sits; the loader refuses a ladder that is not strictly decreasing
inside (0, τ_K). f* at every τ remains an oracle LOWER BOUND (0023, both reasons).

**Prefix-invariance control (review finding 3; HALTS).** 0023's pipeline-identity control scores the
receiver's dump of `S` against itself: the scorer loads one dump twice, so its zero is the scorer's
arithmetic and cannot fail on the box. It stays (it still proves the dump loads and the record sums).
Added: on the same first included handoff, the receiver prefills `S` followed by **R's first token**
(recorded), and rows 0..|S|−1 of that dump are scored against the `S` dump at pairs (p, p). Causal
attention makes them equal up to kernel arithmetic; the max centered per-token deviation (token mean,
K or V, in R²'s units) must be ≤ **1e-04** -- three orders under τ_K, well above float32 noise -- or
the run HALTS before any handoff is scored. The S+1 dump is transient; its per-token record and
score are kept and `summarize_e9` re-derives the maximum, refuses above the tolerance, and refuses a
record whose extra token is not R's first. The tolerance is a registered judgment, not a citation.

**Causal seam distance b⁻(t) (review finding 4).** 0023's b(t) is the distance to the nearest seam on
EITHER side; a matched token's K/V depend only on what precedes it, so a seam after it cannot touch
them and bin 0 is diluted by construction. b⁻(t) = distance to the nearest PRECEDING seam (same seam
definition; a token with no seam before it reports |R|) is computed from the alignment alone and the
seam profile is stated under both, same fixed bins. b(t) stays as registered; neither decides anything.

**Matched-block lengths (review finding 5).** A block is a maximal run of pairs consecutive on both
sides, re-derived from the pairs. Single shared tokens inside otherwise different text carry
null-level deviation and sit in seam bin 0. Registered: the pooled token count by block length in the
fixed bins {1, 2-3, 4-7, 8+}, and f*(τ_K) over tokens in blocks of length ≥ **4**
(`[e9.rule] min_block_len`), E9-same K and V, per handoff and pooled; NOT COMPUTABLE where a handoff has
no such token. Recomputed here from the raw traces over the 25 included handoffs: 155,257 matched tokens in
2,278 blocks -- 1: 679 (0.44%), 2-3: 861 (0.55%), 4-7: 1,715 (1.10%), 8+: 152,002 (97.90%); 153,717 tokens (99.01%) in blocks ≥ 4.
`e9 --align-only` writes every alignment and `results/e9/align/coverage.json` (coverage, reasons,
keep draw, per-handoff block counts) before any prefill, with no gate and no upstream call; the driver
recomputes the same files and `summarize_e9` re-derives every alignment from the raw traces regardless.

**Interval on the median (review finding 6).** The rule reads the point median of f*(τ_K) over the
included handoffs. Beside it, a seeded percentile bootstrap of that median (`[e9.controls]`
`bootstrap_seed` = 25, `bootstrap_reps` = 2000; 2.5 / 97.5 with the ONE pinned quantile convention,
`e7_stats.quantile`) is stated. Reported, never read: the band is the point median as 0023 wrote it.

**δ_null equal-token fraction (review finding 7).** The seeded derangement can pair a receiver position
with a sender position carrying the same token id; the fraction of such pairs is stated beside δ_null.

**Keep subset: n = 3 → 8 (seed 9 unchanged).** 0019 retains a seeded subset of handoffs
with full dumps so a CPU summarizer can re-score from tensors; 0023 registers a `[STRETCH]` partial-
prefill experiment and the E-RL design a behavioral control of the same shape; both can only ever run
on retained dumps, the only tensors that survive the GPU day. Same seed, larger draw: `numpy` choice
without replacement is NOT nested across sizes, so this is a different set, not the old 3 plus 5.
Recomputed here: the n = 3 draw was `django__django-10880_traj#60`, `astropy__astropy-7166_traj#66`, `django__django-11066_traj#36` (14.3 GB); the n = 8 draw is
  - `20241016_composio_swekit/astropy__astropy-14182_traj#68` (4.64 GB)
  - `20241016_composio_swekit/astropy__astropy-7166_traj#88` (6.56 GB)
  - `20241016_composio_swekit/astropy__astropy-7606_traj#88` (6.89 GB)
  - `20241025_composio_swekit/astropy__astropy-14096_traj#80` (7.80 GB)
  - `20241025_composio_swekit/astropy__astropy-14365_traj#119` (7.14 GB)
  - `20241025_composio_swekit/astropy__astropy-14995_traj#74` (7.77 GB)
  - `20241025_composio_swekit/django__django-10999_traj#64` (3.64 GB)
  - `20241025_composio_swekit/django__django-11066_traj#36` (3.72 GB)
1 of the 3 carried over (`django__django-11066_traj#36`). Retained volume 48.2 GB of fp16 stride-1 dumps
(three per handoff; 114,688 B per token on the receiver [28 × 8 × 128 × 2 × 2 B], 114,688 B on the
source), against 14.3 GB before; the box needs that much free beside the transient dumps, and the sync
off the box scales with it. The GPU runbook's named keep handoffs, volumes, "68 handoffs" and "< 1 h"
predate this entry and are superseded by it and by the 09-02 pre-flight; the driver draws from config.

**Instrument and enforcement.** `config/e9.toml` carries every parameter above (`tau_ladder`,
`tau_agent_K`, `min_block_len`, `prefix_invariance_max_delta`, `bootstrap_seed`, `bootstrap_reps`, keep
`n`); `load_e9_config` refuses a config missing or malforming any of them; `e9.assert_ready` requires
THIS entry beside 0019 and 0023 (`REQUIRED_ENTRIES`), so no prefill can start on a ledger that lacks
it; the driver halts on the prefix control; `summarize_e9` states every quantity above in
`summary.json` / `summary.md` under lines that say DESCRIPTIVE or ALONGSIDE and refuses on any
disagreement with config, the calibration, the E7 report, or the per-token record. Tests: ladder and
agent-τ monotone, band unchanged; prefix control halts above tolerance and its record is refused when
tampered, absent, or over tolerance; b⁻ vs b on a seam after a token; block lengths re-derive
difflib's blocks; bootstrap seeded and nearest-rank; coverage comparison never invents a zero;
non-nesting of the keep draw pinned; malformed parameters refused.

**Scope.** All of 0019's and 0023's limits. No hypothesis cell changes with this entry; no
`verdict:` line. The verdict on H-E9 still enters only by its own numbered entry after the run.
The 0018 rows above are E7 figures and name the corpus manifest they were measured against (0024).
e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 8fb9531f556f91cd2090cffe7014956826e2453cbe49b406a7af6a077b115753

### 0026 — 2026-09-04 — E9 upstream re-pin before any score: SDPA attention kernel and logits at dump time, after the first-handoff CUDA OOM; no rule, cap, dtype, τ or handoff-set change

**What happened on the box.** Algoverse grant, one H100 80 GB **MIG 3g.40gb** slice (39.5 GiB, assigned by
`CUDA_VISIBLE_DEVICES`, no other process), linear-ceiling `d965e22`, upstream `36d73b3` (the 0023 pin),
torch 2.11.0+cu128, transformers 5.16.1. `e9 --check` printed ready; the driver refused at the FIRST
included handoff (`astropy__astropy-13033_traj#80`, |S| = 29,391) inside the receiver's dump of `S`:
`torch.OutOfMemoryError: Tried to allocate 51.49 GiB` in `scaled_dot_product_attention`. No score file
was written; `results/e9/report.json` is absent at append and this entry's script refuses otherwise.

**Mechanism (verified, not inferred).** 51.49 GiB = 16 × 29,391² × 4 B exactly: the float32 [heads, T, T]
attention scores. transformers' `sdpa` integration passes `enable_gqa=True` whenever no attention mask is
present (`use_gqa_in_sdpa`); in float32 no fused kernel accepts that (flash needs fp16/bf16, the
memory-efficient kernel does not take `enable_gqa`), so PyTorch takes the math kernel and materializes
the scores. The 2026-09-02 pre-flight budgeted the logits (19.5 GB) and missed this term; at |S| = 32,123
the scores alone are 61.5 GiB, so **no single card runs the 0023 pin as written**, and a bigger card was
never the fix. A scratch probe on the slice (outside `results/`, real Qwen3-1.7B weights, random ids)
measured peak allocated memory of the pinned forward against candidates, GiB:

| T | pinned (`sdpa`, f32) | all-ones mask | `repeat_kv` instead of `enable_gqa` | + `logits_to_keep=1` |
|---|---|---|---|---|
| 4,096 | 10.07 | 10.07 | 9.89 | 7.95 |
| 8,192 | 18.11 | 18.11 | 13.11 | 9.23 |
| 16,384 | OOM (16.0 GiB request) | OOM | 19.56 | 11.80 |
| 29,391 | (51.5 GiB scores alone) | — | 29.80 | 15.89 |
| 32,123 | (61.5 GiB scores alone) | — | 31.95 | 16.74 |

The all-ones mask is dropped before SDPA (K/V bit-identical to the pinned path), so it is not a remedy.
At T = 1,024, where the pinned path runs, K/V under the `repeat_kv` path differ from the math kernel by
max |ΔK| = 9.232e-04 on a K scale of 423.09 and max |ΔV| = 3.891e-04 on a V scale of 215.46 (float32
kernel arithmetic, ≈ 2e-06 relative); `logits_to_keep=1` leaves K/V bit-identical.

**Upstream change (re-pin).** `kvt/models.py` registers an attention implementation `sdpa_repeat_kv`
(the body of `sdpa_attention_forward` with the KV heads expanded by `repeat_kv` and no `enable_gqa`
branch) and `load_model` asks for it; `kvt/data.py::dump_kv` passes `logits_to_keep=1` (K/V are read
from `past_key_values`; the logits were never used). New upstream test `tests/test_models.py`: on a tiny
GQA Qwen3 the registered implementation reproduces eager attention to 1e-05 and returns one logits
row; upstream suite 143 passed. The exact module shipped was validated on the slice before this entry:
K/V bit-identical to the probe's `repeat_kv` path at T = 1,024, peak **15.67 GiB at T = 29,391 and
16.52 GiB at T = 32,123** with the dump call as shipped. Parent of the new pin: `36d73b3` (the 0023
re-pin), so 0019's and 0023's ancestry checks still hold. Re-pin recorded in `config/e9.toml` and
`UPSTREAM.md` by the operator after committing upstream (the placeholder refuses by name).

**What this changes in the measurement, stated plainly.** Every dumped K/V tensor (receiver on `S`, on
`R`, on `S`+1, source on `S`) is now produced by the memory-efficient SDPA kernel instead of the math
kernel: layer-0 K/V are unchanged (no attention upstream of them), deeper layers move at float32
rounding, ≈ 2e-06 relative. All four dumps of a handoff take the same path, so the per-token deviations
0023 defines compare like with like; the pipeline-identity control (exact zero) and the 0025
prefix-invariance control (≤ 1e-04 in R²'s units) still run first on the box and halt on failure.
τ_K = 0.3186 and τ_V = 0.4867 are 0023's recorded numbers from the E8 report (a held-out R² of 0.68 on
generic text, CPU, math kernel); a 2e-06 relative change in the tensors does not move a tolerance
stated to four decimals, and this entry does not touch it. Nothing else moves: context cap 32,768,
float32, pair, band, four cells, keep subset (0025), coverage 25/68, seeds, controls.

**Also learned on the box, for the runbook.** PyPI `torch` 2.14.0 is a CUDA 13.0 build and the box
driver is CUDA 12.8 (`cuda: False` until installed from the `cu128` index); the grant is JupyterHub
only (no ssh/scp — driven over the Jupyter REST API and kernel websocket from home); entry 0025's
8-handoff keep subset is 48.2 GB against a ≈ 50 GB shared-disk policy, so each kept handoff is pulled
home and deleted on the box as it completes. Runbook amended in the same change.

**Enforcement.** `e9.REQUIRED_ENTRIES` now names this entry beside 0019, 0023 and 0025, so no prefill
can start on a ledger that lacks it; `assert_ready` refuses the pending placeholder by name and
`check_upstream` requires the recorded sha to be an ancestor of the upstream checkout with every
invoked path clean.

**Scope.** All of 0019's, 0023's and 0025's limits. No hypothesis cell changes with this entry; no
`verdict:` line. The verdict on H-E9 still enters only by its own numbered entry after the run.

prior-entries-sha256: 070daf0b6ba80a03fe0639235495b4d4186e95456855332a9098d4d3e4212c30

### 0027 — 2026-09-04 — E9 amended before any score: cross-arm outcome named (descriptive); HOLDS bound to a floor; the 0026 kernel change stated as a bound; box discipline

**Precondition, as 0023 and 0025: no score file under `results/e9/` at append.** Home: `results/e9/`
holds `align/` and `calibration/` only, no `report.json` (this entry's script refuses otherwise). Box:
two refused runs on 2026-09-04 left transients and no score — the 16:43 run (0023 pin, OOM in the first
dump; 312 KB of `scratch/`: `S.npy`, `R.npy`, an empty `same_src/`) deleted 17:14 before the relaunch,
and the 17:16 run (0026 pin; died at the first `score_positions` call on the missing mapper) which left
7.2 GB of `scratch/<astropy-13033_traj#80>/` dumps and 93 MB of `controls/` records (identity, prefix,
null pairs) and no `scores/`, `tokens/` or `report.json`; both deleted at 17:29 UTC, confirmed by
listing (`results/e9/` on the box: `align/` only). Nothing scored anywhere. Two review findings not
folded into 0025 or 0026, and the 0026 kernel change quantified as a bound instead of a fix. None
touches the instrument, the H-E9 rule, τ_K, the band or the four cells; `verdict:` lines: none (a
no-op list, as 0025).

**Cross-arm outcome, named (review finding A; descriptive).** 0023 reports E9-cross as its own
f*(τ_K) / f*(τ_V) and as the ratio of its median δ to E9-same's, per handoff, never merged. This entry
names the comparison the verdict entry must state: the median over included handoffs of f*_cross(τ_K),
read against the same edges the same-arm band uses (≤ 0.15 / ≥ 0.50), and the median over handoffs of
the cross/same median-δ ratio. Both are already emitted by `summarize_e9` (the cross-arm f* statistics
and `cross_over_same_median_delta`); no instrument change. Verdict-bearing for nothing — the shape 0025
gave the τ ladder: it reads whether the transfer sits inside, between or beyond the band the same-model
reuse is judged by, and decides no cell.

**HOLDS reads on a floor (review finding C).** f*(τ) is an oracle LOWER BOUND on the recompute fraction
(0023, both reasons: oracle selection of the tokens, and recompute in isolation). CacheBlend's 10–15%
is an ACHIEVED figure. A HOLDS therefore reads: the oracle floor of the re-render's repair is no more
than the budget a same-model reuse the literature already spends — "no more than the mapper, on a
floor" — and not that an achievable scheme reaches it. The verdict entry writes this sentence beside
any HOLDS on the K read-out.

**The 0026 kernel change, as a bound.** τ_K = 0.3186 and τ_V = 0.4867 come from `--calibrate-tau` over
the archived E8 record, whose dumps were produced under the math kernel; E9's dumps come from the
memory-efficient kernel. Measured gap (0026): max |ΔK| = 9.232e-04 on a K scale of 423.09 and
max |ΔV| = 3.891e-04 on 215.46, i.e. a relative perturbation ε ≤ 2.2e-06 of the tensors. δ is a
variance share (a per-token squared deviation over the receiver's centered variance), so a kernel-order
difference enters as ε² where the true deviation is zero and as at most 2ε√δ + ε² elsewhere. For the
prefix-invariance control (true δ = 0) that is ≈ 5e-12, eight orders under the 1e-04 halt — and on the
box the S+1 record came out bit-identical to the identity record (equal sha256). For a measured δ the
shift is ≤ 2.5e-06 absolute at δ = 0.32, below the last stated digit of τ_K (four decimals) and forty
times under the 1e-04 control tolerance. The memory-efficient kernel's block-tiled reduction order, which
can differ between the `S` and `S`+1 forwards at the same prefix position, is the same ε-class effect
and cannot trip a 1e-04 threshold. τ_K and τ_V are not moved.

**Box discipline (runbook, same change).** The 2026-09-04 grant is JupyterHub-only with a ≈ 50 GB
shared-disk policy, against 48.2 GB of kept dumps (0025). Launch detached
(`setsid nohup … > e9.log 2>&1 < /dev/null &`); never `pkill -f` with a pattern the issuing shell
itself matches (the 09-04 self-kill cost eight minutes of stale polling); per handoff, pull each kept
`scratch/<stem>/` home over the Jupyter `/files/` endpoint, verify every file's sha256 against the
`kept_dumps` fingerprint the driver wrote into `report.json`, and only then delete it on the box.
`summarize_e9` at home re-checks the same fingerprints before it re-scores a retained dump.

**Enforcement.** `e9.REQUIRED_ENTRIES` names this entry beside 0019, 0023, 0025 and 0026.

**Scope.** All of 0019's, 0023's, 0025's and 0026's limits. No hypothesis cell changes with this entry;
no `verdict:` line. The verdict on H-E9 still enters only by its own numbered entry after the run.

prior-entries-sha256: 8a0e344bd6ffdfeb9acec713f2017679d21d28f39a7f0781987a9900409aa15c

### 0028 — 2026-09-04 — E9 summarizer enforcement: the keep-subset re-score tolerance registered for a cross-platform re-score; no rule, τ, band, score or handoff change

**What this is, and when.** After the run (2026-09-04, entries 0026/0027 on the record before any score;
`results/e9/report.json` complete, 25 of 68 handoffs scored, 8 kept dumps home and fingerprint-verified)
and BEFORE any figure or verdict is stated. 0023 registered that `summarize_e9` "re-runs the keep-subset
scorer with `--per-token` and compares the squares" and left the comparison's tolerance to the code, which
carried `rtol = 1e-05, atol = 0` -- written for a same-machine comparison of float32 squares against the
float64 sums they were summed into. The re-score at home is a different platform from the box (Linux,
torch 2.11 CPU on the box; Windows, torch 2.13 CPU / numpy 2.5 at home; the scorer has no GPU path), and
under that constant the summarizer refused on the first kept handoff:
`E9 SUMMARY REFUSED: 20241016_composio_swekit/astropy__astropy-14182_traj#68: keep-subset per-token
re-score disagrees on same_K`. This entry registers the tolerance for that check as a judgment, with the
measurement it rests on; it is enforcement of 0023, not a change to anything 0023 registers. The rule
section, τ_K = 0.3186, τ_V = 0.4867, the band, the four cells, the scores on disk and the
handoff set are untouched; `verdict:` lines: none.

**Registered check (replaces the unstated constant).** For every kept handoff, the home re-score's
per-token record must (i) reproduce each per-head float64 SUM of squares to `1e-05` relative
(unchanged: this is what the moments are), and (ii) reproduce every individual float32 square to
`1e-02` relative with no absolute floor; a shape mismatch, a sum beyond (i) or a square beyond
(ii) refuses the summary, as before. The summarizer now also reports what the cross-platform jitter does
to the statistic itself: the largest change in any token's centered δ and in any handoff's f*(τ) between
the box record and the home re-score.

**Measured, by `summarize_e9` on this run (8 kept handoffs × 6 arrays; `rescore_agreement` in
`results/e9/summary.json`):**

| array | bit-identical fraction (min – max over handoffs) | max square rel. diff | max per-head sum rel. diff | max \|Δδ_token\| | max \|Δf*(τ)\| |
|---|---|---|---|---|---|
| same_K | 0.991 – 1.000 | 2.5e-04 | 3.1e-08 | 3.6e-09 | 0.0e+00 |
| same_V | 1.000 – 1.000 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| cross_K | 0.095 – 0.101 | 2.9e-03 | 2.8e-07 | 2.0e-07 | 0.0e+00 |
| cross_V | 0.043 – 0.045 | 3.8e-04 | 2.5e-07 | 4.0e-06 | 0.0e+00 |
| ref_K | 1.000 – 1.000 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| ref_V | 1.000 – 1.000 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 |

Overall: every per-head sum within 2.8e-07 relative (tolerance 1e-05); every square within
2.9e-03 relative (tolerance 1e-02); the largest change in any token's δ is
4.0e-06 and f*(τ_K) / f*(τ_V) is unchanged on every kept handoff and arm (max |Δf*| =
0.0e+00). The same-model arrays and the reference norms reproduce almost or exactly
bit-for-bit; the cross-arm squares pass through the k = 1 mapper's matmul, where the two platforms' BLAS
reduce in a different order, and never differ by more than a third of a percent. The ref arrays are not
squares; they are checked under the same rule for uniformity.

**Basis beyond this run: what the disagreement is (scratch, 2026-09-04, one kept handoff, astropy-14182).**
Re-scored in an Ubuntu WSL on the home machine with the box's torch build (2.11.0 from the cu128 index,
numpy 2.5.2, python 3.12): `same_K`, `same_V`, `ref_K`, `ref_V` reproduce the box record **bit-for-bit**
(the 132 differing same-K squares at home were Windows-vs-Linux, ≤ 2.5e-04 relative on near-zero squares);
two identical runs on one machine are bit-identical on every array; the cross arrays change with the
THREAD COUNT alone (8 threads vs 1 thread on the same machine: 69% / 48% of cross-K / cross-V squares
identical, ≤ 1.2e-03 relative) and against the 104-core box at any thread count agree on ≈ 10% / 4% of
squares within 2.5e-03 / 3.8e-04 relative. So: the verdict-bearing arrays are exactly reproducible on a
matching platform; the cross arrays' per-square disagreement is reduction order inside the mapper's
float32 matmul, a function of thread count and hardware, not of the record. This is a measured
explanation, not an inference from the sizes of the differences.

**Why 1e-02 and not the measured 2.9e-03.** A tolerance set at the observed
maximum is a tautology; one order above it still refuses any square that moved by a percent, which is
339× the largest platform effect seen here and far below anything that could move a
token across τ_K (a token would need δ to move by a factor, not a percent, and the measured max |Δδ| is
4.0e-06 against τ_K = 0.3186). The sum check keeps the tight floor: a record whose
squares were altered in a way that preserved every per-head sum would still have to keep every square
within a percent of the box's.

**Scope.** All of 0019's, 0023's, 0025's, 0026's and 0027's limits. No hypothesis cell changes with this
entry; no `verdict:` line. The verdict on H-E9 enters only by its own numbered entry, from a summary that
passes under this check.

prior-entries-sha256: 3eef45b79417ef3270281c08bfeb7a177aaf4c95d5a6daa909ac8151d7de9a1f

### 0029 — 2026-09-04 — E9 ran `[BASELINE]`; H-E9 HELD

**Setup, as registered.** Algoverse grant, one H100 80 GB MIG 3g.40gb slice, JupyterHub only; linear-ceiling
`0a19b56` (entries 0019, 0023, 0025, 0026, 0027 required by the gate and committed), upstream pin
`d5786df` (entry 0026). Pair qwen3-0.6b-to-1.7b; receiver Qwen3-1.7B, source Qwen3-0.6B, the k = 1
content-space mapper of 0016/0020 for the cross arm. Launched 17:35:32 UTC after two refused attempts (0027
names them; nothing scored in either), finished 18:13 UTC: 25 handoffs scored in 38 minutes wall,
68 observed, 43 excluded (39 over the 32,768 cap, 4 with an empty receiver prompt).
Every figure below is `summarize_e9`'s, from a run that passed all of its checks: alignments re-derived from
the raw traces; every R² recomputed from recorded moments; per-token squares summed against the moments;
the 8 kept dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within
2.9e-03 relative, f* unchanged on every kept handoff); τ recomputed from the archived mapper; controls checked.

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance: max centered per-token δ
0.000e+00 over 29,391 positions (tolerance 1e-04) -- the box reproduced the prefix under one extra
token bit-for-bit. δ_null (deranged pairing, the top of the deviation scale) same K / V token-mean median
2.009 / 1.962; fraction of null pairs with equal token ids 0.0099.
Matched fraction |M|/|R| (a floor; blocks method): 0.9344 (p10 0.8838, p90 0.9783).

**The rule (0023, frozen before any prefill) and the figure it reads.** Per included handoff, E9-same, K
read-out: f*(τ_K) = the fraction of matched tokens whose centered per-token deviation exceeds
τ_K = 0.3186 (1 − the k = 1 mapper's own held-out K R²); median over included handoffs; HOLDS ≤ 0.15,
DEGRADES ≥ 0.5, UNRESOLVED between.

- **median f*(τ_K), E9-same K: 0.0000 (p10 0.0000, p90 0.0000)** over 25 handoffs. Seeded bootstrap of the
  median (0025, seed 25, 2000 reps; reported, not read): [0.0000, 0.0000].
- f*(τ_V = 0.4867), E9-same V (alongside, verdict-bearing for nothing): 0.0000 (p10 0.0000, p90 0.0000).
- τ ladder (0025, descriptive): τ = 0.1: same K 0.0000 (p10 0.0000, p90 0.1563) / V 0.0000 (p10 0.0000, p90 0.1888); τ = 0.03: same K 0.1433 (p10 0.0115, p90 0.5823) / V 0.1394 (p10 0.0177, p90 0.5109).
- f*(τ_agent_K = 0.4371) (0025, alongside): same K 0.0000 (p10 0.0000, p90 0.0000); cross K 0.5045 (p10 0.3825, p90 0.6698).
- f*(τ_K) over matched blocks of length ≥ 4 (0025): same K 0.0000 (p10 0.0000, p90 0.0000).
- Seam profile under the causal distance b⁻(t) (0025), E9-same K, pooled median δ by bin: 0: 0.236 (n=2278) · 1: 0.127 (n=1599) · 2-3: 0.081 (n=2571) · 4-7: 0.062 (n=4039) · 8-15: 0.063 (n=5480) · 16+: 0.019 (n=139290).

**Band outcome, against the rule as written: HOLDS.** Not one included handoff has a single matched token whose centered deviation exceeds τ_K on the same-model arm: the receiver's KV at the re-rendered position agrees with its KV at the original position to within the mapper's own tolerance at every matched token, on every handoff.

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction
(0023: oracle selection of the tokens, and recompute in isolation). CacheBlend's 10–15% is an ACHIEVED
figure. This HOLDS therefore reads: the oracle floor of the re-render's repair is no more than the budget a
same-model reuse the literature already spends -- "no more than the mapper, on a floor" -- and not that an
achievable scheme reaches it.

**Cross-arm outcome, named (0027; descriptive, decides nothing).** E9-cross, the 0.6B source mapped through
the k = 1 mapper: median f*(τ_K) = 0.9286 (p10 0.8579, p90 0.9607) and f*(τ_V) = 0.9089 (p10 0.8656, p90 0.9371); read against the same
edges, the transfer arm sits beyond the DEGRADES edge. Cross/same median-δ ratio K / V: 26.9 (p10 5.6, p90 51.9) / 40.6 (p10 7.5, p90 104.0).
Bridge R² (A5, head- and layer-averaged; decides nothing): same K 0.9318 (p10 0.8430, p90 0.9616), same V 0.9171 (p10 0.8156, p90 0.9521),
cross K 0.4557 (p10 0.4196, p90 0.4760), cross V 0.1722 (p10 0.1458, p90 0.2030) -- the cross K figure lands where 0020's arm (b) put the same
mapper on agent text (K R² 0.4371). Own-norm diagnostic, fraction of tokens with δ_own > 1, same K / V:
0.0000 (p10 0.0000, p90 0.0000) / 0.0043 (p10 0.0028, p90 0.0066).

**Coverage (0025; what the cap selected on).** Included vs excluded-by-length, medians (p10, p90): |S|
25,460 (14,269, 30,106) vs 52,141 (35,692, 147,218); |R| 6,551 vs 11,500;
0018 overlap 0.9846 vs 0.9894; 0018 recoverable fraction 0.8861 vs 0.8904
(0 handoffs without a 0018 row). H-E9 is decided on the included set and is a claim about it: the
shorter half of the corpus by |S|.

**What this establishes, stated narrowly.** On Qwen3-1.7B re-rendering 25 real SWE-bench composio handoffs
under the 32,768-token cap, with the LCS-floor alignment of 0019 and the per-token rule of 0023, the
same-model KV agreement at content-matched tokens is inside the k = 1 mapper's own tolerance at every
matched token of every handoff, so the oracle recompute floor is zero. **Not established:** anything about
the excluded long handoffs; any achievable recompute scheme (floor, not method); the cross-model transfer
at this handoff, which by the named descriptive outcome sits beyond the DEGRADES edge; one pair, one
direction, one mapper, one alignment method; and nothing about generation quality after reuse (0023's
`[STRETCH]` partial-prefill experiment, registered for the retained dumps, is not run).

verdict: H-E9 = HELD
e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 2be23eb054eaceb14c0c8016a015f075be82817f36189b94a684542582bee8ce

### 0030 — 2026-09-04 — E8 amended before any rescoring: arm (b) over every agent sequence, per-sequence moments, a seeded bootstrap of the drop; descriptive; the H-E8 cell and τ_agent_K do not move

**Why, and why now.** 0016 matched arm (b)'s protocol to arm (a)'s "exactly": the agent-text dumps were split
by sequence with `holdout_frac` 0.2, and only the last ⌈0.2 × 50⌉ = 10 sequences (2,560 tokens at stride
4) were scored. That match was the wrong instinct for arm (b): the k = 1 mapper was fit on the GENERIC
calibration dumps (arm (a)'s training rows), never on agent text, so nothing in the agent dumps needs holding
out and the split threw away 40 of 50 sequences. Track B (2026-09-01/02) tried to register this and stopped:
the pinned `score_mapper.py` refused `--holdout-frac 1.0` (empty training mask) and wrote no per-sequence
moments — upstream changes. They are made now (below), after the E9 verdict (0029) and before anything is
rescored: `results/e8a/` holds no report at append and this entry's script refuses otherwise.

**What is registered.** A rescoring of 0020's OWN tensors — the agent dumps at `results/e8/kv/agent`
and the token file they were dumped from are reused and must match the fingerprints recorded in
`results/e8/report.json` (sha256 `5c4e70a097c2`) byte for byte; nothing is resampled
or re-dumped, and the generic dumps are the archived ones. For each k ∈ {1, 4, 8}:

- arm (a), generic: the mapper's own held-out sequences, `holdout_frac` 0.2 — unchanged; scoring more of
  its own calibration dumps would be in-sample and is not done;
- arm (b), agent: `--holdout-frac 1.0` — every one of the 50 sequences (12,800 tokens), the mapper's
  transfer measured on all the agent text 0016 sampled;
- the drop (a − b) and its 0009 band word, **read descriptively**: the H-E8 cell was decided by 0020 under the
  registered protocol and does not move here; this entry carries no `verdict:` line;
- per-sequence R² for both arms from the per-token record (upstream `per_sequence_moments`: SSE and SST per
  sequence per head, SST around the GLOBAL held-out mean, so the sums reproduce the pooled moments exactly and a
  sequence's R² is its share of the same decomposition, not a re-centred fit); median (p10, p90) over sequences
  with the pinned quantile convention (`e7_stats`);
- a seeded percentile bootstrap over agent sequences (seed 30 + k, 2000 reps) of arm (b)'s pooled R² and of the
  drop, 2.5% / 97.5%; reported, read by nothing;
- the change from 0020's arm (b) figure at the same k, named as such.

**What this does NOT touch.** τ_agent_K = 1 − 0020 arm (b) K R² (= 1 − 0.5629 = 0.4371) is 0025's registered
alongside tolerance and stays as registered; the all-sequence figure is reported beside it, never substituted
(0029 has already read τ_agent_K). τ_K, the E9 rule, band and cells are untouched. `results/e8/` is not
rewritten — E9's calibration checks read it — and this amendment writes only under `results/e8a/`.

**Upstream change (re-pin).** `scripts/score_mapper.py` accepts `--holdout-frac 1.0` when only scoring (train
figures null; an empty held-out mask is still refused) and, with `--per-token`, writes `seq_idx`, `seq_ids`,
`sse_seq_*`, `sst_seq_*` plus a `per_sequence` block whose sums it checks against the layer moments before
writing; `kvt/pertoken.py::per_sequence_moments` carries the decomposition with a test that the sequence sums
reproduce the layer moments exactly. Re-pin recorded in `config/e8a.toml` and `UPSTREAM.md` by the operator after
committing upstream (the placeholder refuses by name); parent `d5786df` (the 0026 pin). E8's original pin
`71df4504` is unchanged for `results/e8/`, whose gate now refuses by drift (three later re-pins touched its
invoked paths) — a known state, recorded here, not repaired: 0020 stands on its own record.

**Instrument and enforcement.** `config/e8a.toml` (separate results dir; `agent_holdout_frac`, `reuse_agent_dumps_from`,
`[e8.amendment]`), `e8.reuse_agent_dumps` (fingerprint + token-file check before any scoring), `e8.required_entries`
(the gate requires THIS entry beside 0009 and 0016), `summarize_e8` amendment figures (per-sequence recompute from
the record, refused on disagreement with the report and with the re-scored json; bootstrap; the prior report's
hash re-checked). Tests: reuse by fingerprint, refusal on a changed dump, gate entries, per-sequence recompute and
bootstrap, refusal on a tampered per-sequence list and on a changed prior report.

**Scope.** All of 0009's, 0016's and 0020's limits (off-policy text for Qwen; one pair; one direction; visible
messages only). No hypothesis cell changes with this entry; no `verdict:` line. The figures enter by their own
numbered entry from a passing `summarize_e8 --config config/e8a.toml`.

prior-entries-sha256: fc7a391fc4a827e361340c286c336ca9cdbfe9613d1a66200be1a590029dc9d0

### 0031 — 2026-09-07 — E8 amendment ran `[BASELINE, DESCRIPTIVE]`: arm (b) over every agent sequence; the H-E8 cell does not move

**Provenance.** Registered by 0030 before any rescoring; `config/e8a.toml` and this ledger committed unmodified;
upstream at the 0030 re-pin `223f469`, clean for the invoked paths; 0020's agent dumps and token file
reused byte for byte (fingerprints checked at run time and again by the summarizer); arm (a) cross-checked against
the archived `r2.json` for every k. Every figure below is `summarize_e8 --config config/e8a.toml`'s: the scorer
re-run on the fingerprinted dumps, per-sequence R² recomputed from the per-token record and checked against both
the report and the re-scored json, the prior report's hash re-checked. Arm (a) keeps the mapper's own held-out
fraction 0.2; arm (b) scores all 50 agent sequences (12,800 tokens) — 0020 had scored
10 of them (2,560 tokens at the matched protocol).

| k | agent seqs / tokens | arm (a) generic K / V | arm (b) agent, ALL K / V | 0020's arm (b) K / V | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |
|---|---|---|---|---|---|---|---|---|---|
| 1 (0016 verdict k) | 50 / 12,800 | 0.6814 / 0.5133 | **0.5708 / 0.3230** | 0.5629 / 0.3418 | +0.0079 / -0.0189 | +0.1106 / +0.1903 | [+0.1022, +0.1199] | [+0.1779, +0.2044] | UNRESOLVED / DEGRADES |
| 4 | 50 / 12,800 | 0.5907 / 0.3361 | **0.3783 / -0.0982** | 0.3523 / -0.0796 | +0.0260 / -0.0186 | +0.2124 / +0.4344 | [+0.1980, +0.2281] | [+0.4087, +0.4633] | DEGRADES / DEGRADES |
| 8 | 50 / 12,800 | 0.0984 / -0.6412 | **-0.5128 / -2.1456** | -0.6280 / -2.1380 | +0.1152 / -0.0075 | +0.6112 / +1.5044 | [+0.5749, +0.6493] | [+1.4156, +1.5989] | DEGRADES / DEGRADES |

Bootstrap: seeded percentile over agent sequences (seed 30 + k, 2000 reps), 2.5% / 97.5% of the drop;
reported, read by nothing. Band words are 0009's band applied to the all-sequence drop for orientation only.

**Per-sequence R² (a share of the pooled decomposition, SST around the global held-out mean), median (p10, p90):**

| k | agent K | agent V | generic K | generic V |
|---|---|---|---|---|
| 1 | 0.5671 (p10 0.5367, p90 0.6107) | 0.3224 (p10 0.2535, p90 0.3812) | 0.6835 (p10 0.6653, p90 0.7019) | 0.5096 (p10 0.4942, p90 0.5492) |
| 4 | 0.3691 (p10 0.3287, p90 0.4362) | -0.1039 (p10 -0.2248, p90 -0.0093) | 0.5960 (p10 0.5683, p90 0.6229) | 0.3203 (p10 0.2937, p90 0.4100) |
| 8 | -0.5132 (p10 -0.6455, p90 -0.3515) | -2.1621 (p10 -2.4954, p90 -1.8028) | 0.1074 (p10 0.0103, p90 0.1822) | -0.7107 (p10 -0.8031, p90 -0.3692) |

**What changed and what did not.** Scoring every agent sequence instead of the last 10 moves arm (b) at
k = 1 by +0.0079 (K) / -0.0189 (V); the drop at k = 1 is +0.1106 / +0.1903 with 95% bootstrap
[+0.1022, +0.1199] / [+0.1779, +0.2044], read against 0009's band as UNRESOLVED / DEGRADES
(0020, at the matched protocol: UNRESOLVED / DEGRADES). **The H-E8 cell was decided by 0020 under the registered 0016
protocol and does not move here; this entry carries no `verdict:` line.** τ_agent_K stays 0025's registered
value, 1 − 0.5629 = 0.4371; the all-sequence counterpart, 1 − 0.5708 = 0.4292, is reported here beside it
and substituted for nothing (0029 has already read τ_agent_K). Per-sequence spread on the agent arm at k = 1:
K 0.5671 (p10 0.5367, p90 0.6107), V 0.3224 (p10 0.2535, p90 0.3812) over 50 sequences.

**Not established.** Anything beyond 0020's limits: off-policy text for Qwen, one pair, one direction, one mapper,
visible messages only (0012); the agent windows are the 0016 sample, not new text; arm (a)'s figure is on the
mapper's own 10 held-out generic sequences and its per-sequence spread is over that many.

**Scope.** All of 0009's, 0016's, 0020's and 0030's limits. No hypothesis cell changes with this entry.

prior-entries-sha256: e5763c565d4fae7e4775a5e7e97d9e724f85b2bf63ce9f0ab3551613c6a45129

### 0032 — 2026-09-06 — E9 admitted to the LCFM 4-pager behind the summarizer gate; descriptive; the H-E9 cell does not move

**Operator decision of 2026-09-06.** The LCFM short-paper sprint proceeds (deadline 2026-09-10 AoE; numbers-freeze
gate EOD 2026-09-08 per entry 0006), and E9 joins the submission. Entry 0006's scope cap named "Lane A/B premise
numbers and the taxonomy" as the core and allowed the transfer-fidelity leg "only if they clear the same gate";
entry 0016(1) applied that allowance to E8. This entry applies it to E9 on the same terms and no wider:

- **E9 figures enter the 4-pager only from `summarize_e9`**, fail-closed, from a run that passes every check it
  carries (alignments re-derived from the raw traces; R² from recorded moments; per-token sums against the
  moments; the 25 included handoffs' keep subset re-scored under 0028's tolerance; τ recomputed from the
  archived mapper; controls checked). The submission cites 0029's figures as 0029 states them; nothing is
  re-read, rounded up, or restated from a report.
- **The reading is 0027's, verbatim in spirit:** H-E9 `HELD` is read on a floor — f*(τ) is an oracle lower bound
  on the recompute fraction (oracle token selection, recompute in isolation) — and the cross-model arm's
  descriptive outcome (beyond the DEGRADES edge) is named beside it in every place the same-model figure appears.
  The 4-pager may not present the same-model result without the cross-model outcome in the same table or
  sentence.
- **Coverage travels with the number.** Every appearance of the verdict names the included set (25 of 68,
  the shorter half of the corpus by |S|, entry 0025's comparison) — the claim is about that set.
- **Space.** E9 is one paragraph, one table (controls, same-model and cross-model f*, bridge R²), and the
  τ ladder in an appendix; Lane A/B premise numbers and the taxonomy remain the submission's core (0006, 0016).

**Condition carried forward, not a ledger fact.** The co-author refutation of entries 0025–0029 (two leads:
the τ-ladder sensitivity; the exactly-zero prefix-invariance control) is owed at the time of writing. If it has
not been recorded by the numbers-freeze gate, the 4-pager's E9 section is cut to one sentence marked as
ongoing work and the figures are withheld from the submission; this entry does not decide that outcome and a
later entry records it either way.

**What this does NOT touch.** No `verdict:` line; the H-E9 cell stays `HELD` as 0029 decided it; τ_K, the
rule, the band, the keep subset, the kept dumps and `results/e9/` are unchanged; no experiment is registered
and nothing runs under this entry.

prior-entries-sha256: ce735dbb4c5218c2588db7feba8a28f3b68e8dc61bdeb341d09a34b24471897d

### 0033 — 2026-09-08 — Calibration-size sensitivity registered before any fit: the k = 1 mapper refit on n = 420 sequences, E8 arms and the E9 kept-subset cross arm re-scored; descriptive; no cell moves

**Why, and why now.** Every transfer figure on the record (0020, 0029, 0031) reads through ONE mapper: the k = 1
content-space map fit upstream on 50 calibration sequences (10,240 training tokens). The source paper calibrates on
roughly 128K tokens, 12.5× more (upstream ledger, H2 probe), and the upstream's own curve hypotheses H-L1–L4 asked
whether the collapse at larger k was calibration size; no run of them is on this record. An independent review
(2026-09-06) named the mapper's provenance as the submission's first rejection risk. The n = 420 calibration dumps
exist upstream (`data/kv/qwen3-0.6b-to-1.7b-n420`) with two provenances, stated because `meta.json` records neither platform nor thread
count: the source half is the upstream's CPU dump of 2026-08-24 (`--threads 12`, nested over the n = 50 draw by the upstream's
own check); the target half is the GPU dump of 2026-09-08 (H100 MIG 1g.20gb, fp32, `sdpa_repeat_kv`, torch 2.11.0+cu128,
upstream at the pin below; `docs/2026-09-08-n420-target-dump-runbook.md`), because the 2026-08-25 CPU attempt was killed at
358/420 with nothing written (upstream learnings 2026-08-25) and the config's "existing" comment was never an existence
check (learnings 2026-09-07). The two target halves (CPU n = 50, GPU n = 420 on sequences 0–49) agree to at most one fp16
ULP at every checked layer and kind (runbook §4, 21:17); the mapper's calibration therefore mixes a CPU source half with
a GPU target half, and any figure this entry produces carries that. No mapper has been fit on them: this entry registers that fit and what is re-scored with it, before the fit runs —
`mappers/qwen3-0.6b-to-1.7b/n420` is absent and both results directories are empty at append, and this
script refuses otherwise.

**What is registered.**

- **The fit (upstream, no code change, no re-pin):** `scripts/fit_mapper.py --pair qwen3-0.6b-to-1.7b --k 1 4 8 --tag n420 --dump-root data/kv/qwen3-0.6b-to-1.7b-n420` at the pin
  `223f46916473` (λ 0.01, hold-out 0.2, content space: `fit_mapper.py` defaults, stated); k ∈ {1, 4, 8}
  fitted, k = 1 the compared one. Inputs bound by fingerprint at append: `meta.json` sha256 source `0afb6888a390` /
  target `4645a2574308` (30 / 30 files per dump; n_seqs 420). The artifacts land where
  `--tag` puts them and every downstream report fingerprints them (`mapper` block).
- **E8 under `config/e8c.toml` → `results/e8c/`:** 0030's protocol exactly — arm (a) on the tagged mapper's OWN
  held-out sequences (`holdout_frac` 0.2; the last ⌈0.2 × 420⌉ of the n = 420 dumps; in-sample otherwise),
  arm (b) over every one of the 50 agent sequences (`--holdout-frac 1.0`), 0020's agent dumps and token
  file reused by fingerprint through 0031's record (`results/e8a/report.json`, sha256 `e2e433fa8925`),
  per-sequence moments, seeded bootstrap (seed 33 + k, 2000 reps), the change measured from
  0031's all-sequence figures at the same k, and arm (a) cross-checked against the tagged `r2.json`.
- **E9 cross arm under `config/e9c.toml` → `results/e9c/`:** `score_positions.py` re-run over the 8 kept
  handoffs' retained stride-1 dumps (0025's seeded draw; fingerprints of 0029's record) and 0029's alignments, with
  the tagged k = 1 mapper. Nothing is prefilled. **Control, refusing:** the same-model arm does not depend on the
  mapper, so its per-token squares must reproduce 0028's home re-score within 0028's tolerance (sums 1e-5, squares
  1e-2 relative) on every handoff, or no cross figure is read. Reported: cross-arm f*(τ_K = 0.3186) beside 0029's
  cross figure on the same 8 handoffs (recomputed from 0028's record by the same arithmetic, not read from a
  summary); f* under the tagged mapper's own tolerance τ_K′ = 1 − its verified arm (a) K R² (from `results/e8c/`);
  f*(τ_agent_K = 0.4371); the τ ladder (0.1, 0.03); bridge R²; a seeded bootstrap of the median (seed
  33, 2000 reps). Band words at 0023's edges are descriptive.

**What this does NOT touch.** H-E8 (0020) and H-E9 (0029) stay as decided; τ_K, τ_V, τ_agent_K, the E9 rule, band,
keep subset, and every existing results directory are unchanged; no `verdict:` line here or in the figures entry.
The n = 420 figures are reported BESIDE the n = 50 record, never substituted; whichever way they fall, the decided
cells were decided under the registered protocol. The kept subset is 8 of 25 included handoffs and the cross
re-score is a claim about those 8.

**Instrument and enforcement.** `E8Config.mapper_tag` (tagged mapper + tagged archived `r2.json`; `mapper` fingerprint
in every E8 report, re-checked by `summarize_e8`); `linear_ceiling.e9_rescore` (`check` / `run` / `summarize`;
gate = this entry + 0019/0023/0025/0027/0029 + both configs committed unmodified + the 0030 pin by ancestry with
E9's invoked paths unchanged + the tagged artifact present; the same-arm control; τ_K′ taken from the E8 report
scored with byte-identical mapper files). Tests: tagged paths and fingerprints, refusal on swapped mapper bytes, the
control firing, refusal on a changed kept dump / prior report / foreign E8 report.

**Scope.** 0009/0016/0020/0030's limits (off-policy text; one pair; one direction) and 0029's (one pair, 8 kept of
25 included of 68 observed, floor not method). The figures enter by their own numbered entry from passing
`summarize_e8 --config config/e8c.toml` and `e9_rescore summarize`.

prior-entries-sha256: 9f16a83e3cb98ea26bc23d052638881ed15c6c14618aec4e58a51cd6607dc056

### 0034 — 2026-09-08 — Calibration-size sensitivity ran `[BASELINE, DESCRIPTIVE]`: the n = 420 mapper on E8's arms and E9's kept-subset cross arm; no cell moves

**Provenance.** Registered by 0033 before the fit existed; `config/e8c.toml`, `config/e9c.toml` and this ledger committed
unmodified; upstream at `223f469`, clean for the invoked paths; the tagged mapper `mappers/qwen3-0.6b-to-1.7b/n420/k1` named by
sha256 in both reports (safetensors `b602eaf2e844`); 0020's agent dumps and token file reused through 0031's
record; 0029's kept dumps and alignments by fingerprint. Every figure below is a summarizer's: `summarize_e8 --config
config/e8c.toml` (scorer re-run, per-sequence R² recomputed from the record, bootstrap, prior report re-hashed) and
`e9_rescore summarize` (files by hash, squares summed to moments, the same-arm control, f* recomputed from both records).

**E8 with the n = 420 mapper** (0030's protocol; the change is from 0031's all-sequence figures under the n = 50 mapper):

| k | arm (a) generic K / V, n = 420 mapper | arm (b) agent ALL K / V, n = 420 mapper | 0031's arm (b) K / V, n = 50 mapper | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |
|---|---|---|---|---|---|---|---|---|
| 1 (compared k) | 0.7323 / 0.5895 | **0.6386 / 0.4437** | 0.5708 / 0.3230 | +0.0678 / +0.1207 | +0.0937 / +0.1459 | [+0.0865, +0.1016] | [+0.1357, +0.1562] | UNRESOLVED / UNRESOLVED |
| 4 | 0.7595 / 0.6253 | **0.6547 / 0.4511** | 0.3783 / -0.0982 | +0.2764 / +0.5493 | +0.1048 / +0.1742 | [+0.0970, +0.1129] | [+0.1630, +0.1860] | UNRESOLVED / DEGRADES |
| 8 | 0.7641 / 0.6329 | **0.6474 / 0.4331** | -0.5128 / -2.1456 | +1.1601 / +2.5787 | +0.1167 / +0.1998 | [+0.1092, +0.1248] | [+0.1885, +0.2119] | UNRESOLVED / DEGRADES |

Per-sequence agent K at k = 1: median 0.6363 (p10 0.6110, p90 0.6717) over 50 sequences.

**E9 cross arm on the 8 kept handoffs.** Same-arm control PASSED on every handoff (max relative square vs 0028's
re-score: same_K 0.00e+00, same_V 0.00e+00; the tensors and alignments are 0029's). Tolerances:
τ_K (0023) 0.3186; τ_K′ under the n = 420 mapper 0.2677 (1 − its verified arm (a) K R²); τ_agent_K 0.4371.

- cross K f*(τ_K): **n = 420 mapper 0.8106 (p10 0.6494, p90 0.8498)** vs n = 50 mapper on the same handoffs 0.9352 (p10 0.8993, p90 0.9685);
  bootstrap of the median (seed 33, 2000 reps; reported): [0.7368, 0.8433]; band word at 0023's edges, descriptive: DEGRADES.
- cross K f*(τ_K′), the mapper read against its own tolerance: 0.9283 (p10 0.8794, p90 0.9608) (DEGRADES, descriptive).
- cross K f*(τ_agent_K): 0.1121 (p10 0.0000, p90 0.3067) vs n = 50 mapper 0.6092 (p10 0.3825, p90 0.6850).
- cross V f*(τ_V): 0.6771 (p10 0.5187, p90 0.7410) vs 0.9149 (p10 0.8830, p90 0.9684).
- bridge R² (A5, head- and layer-averaged): cross K 0.5293 (p10 0.4996, p90 0.5652) vs 0.4377 (p10 0.4135, p90 0.4788); cross V 0.3338 (p10 0.3010, p90 0.3684) vs
  0.1639 (p10 0.1256, p90 0.2030); same K (control) 0.8897 (p10 0.8101, p90 0.9341) vs 0.8897 (p10 0.8101, p90 0.9341).

| τ (ladder) | cross K f*, n = 420 mapper | cross K f*, n = 50 mapper |
|---|---|---|
| 0.1 | 1.0000 (p10 1.0000, p90 1.0000) | 1.0000 (p10 1.0000, p90 1.0000) |
| 0.03 | 1.0000 (p10 1.0000, p90 1.0000) | 1.0000 (p10 1.0000, p90 1.0000) |

**What this establishes, narrowly.** Descriptive only: the decided cells (H-E8 0020, H-E9 0029) were decided under the
registered protocol with the n = 50 mapper and do not move; the n = 420 figures stand beside them as the answer to
"was it the calibration size" for this pair, this direction, 8 kept of 25 included handoffs, on a floor (0027).
Not established: anything about the excluded long handoffs; an achievable scheme; the paper's own regime (~128K tokens).

**Scope.** All of 0033's. No `verdict:` line.

prior-entries-sha256: 50c7d5027d891a1b99b93da68e823bb64d941bed501136d652b37218f07d290c

### 0035 — 2026-09-09 — E9-long registered before any prefill: H-E9's instrument on the 35 handoffs above the prior cap, receiver scaled to 81,920 by YaRN; H-E9L added `unresolved`; the 4-pager re-scoped around E9 and E9-long (supersedes 0032's space clause)

**Why, and why now.** H-E9 `HELD` (0029) is a claim about the 25 of 68 observed handoffs whose sender prompt fits
Qwen3's 32,768-token cap — the shorter half by |S| (0025: included median 25,460 vs excluded 52,141). A long-context
venue asks first whether the same result holds where the re-rendered context is 35K–80K tokens, and nothing on the
record answers it. The seed (`docs/2026-09-08-seed-e9-long-half.md`) designed the experiment; the operator ruled
D1(a)/D2/D3/D4/D5 on 2026-09-09 and, the same day, that the LCFM 4-pager is written from an overnight sitting on a
rented single L40S (48 GB; no queue) rather than the Algoverse 3g.40gb queue. This entry registers the experiment,
its controls, its stopping rule and its paper scope BEFORE the box is touched: `results/e9l/` holds no report, no
score, no bridge and no control file at append, and this script refuses otherwise (R1). The only thing under
`results/e9l/` is the instrument's own alignment pass (`e9 --align-only --config config/e9l.toml`,
`align/coverage.json` sha256 `492d8f0db8d0`), from which every count below is read.

**Hypothesis H-E9L (row added to the table, `unresolved`).** The statement is E9's on the long half; the rule is
0023's verbatim (`[e9.rule]` copied byte-for-byte from `config/e9.toml`): per matched token the centered deviation in
R²'s units between the receiver's own K at the sender position and at the re-rendered position; a token needs
recompute when it exceeds τ_K = 0.3186 (the k = 1 mapper's held-out shortfall, 0023); the verdict statistic is the
median over included handoffs of the oracle selective-recompute fraction f*(τ_K) on the K read-out; **HOLDS ≤
0.15 / DEGRADES ≥ 0.50 / UNRESOLVED between**. τ_V = 0.4867, τ_agent_K = 0.4371, the τ ladder (0.1, 0.03),
the seam bins, the block floor (4) and the bootstrap (seed 25, 2000 reps) are 0025's, unchanged.
f* stays an oracle LOWER BOUND read on a floor (0027).

**The verdict set: the newly included handoffs, never pooled.** `context_cap = 81,920` (= 32,768 × 2.5, the knee of the
cap ladder in the seed) and `context_floor = 32,768`: a handoff whose |S| and |R| both fit the floor was decided by
0029 and is EXCLUDED here with its own reason (the 25 of 0029, never pooled; that cell is immutable). Coverage from
the alignment pass: **68 observed · 35 included · 25 excluded as decided under the prior cap · 4 excluded
above the cap · 4 excluded for an empty receiver prompt** (the last eight by name, in the seed's words: above
81,920: `20241016_composio_swekit/astropy__astropy-13398_traj#290`; `20241016_composio_swekit/astropy__astropy-13398_traj#447`; `20241016_composio_swekit/astropy__astropy-14365_traj#298`; `20241025_composio_swekit/astropy__astropy-13453_traj#221` (|S| 185,793, 357,623, 172,327, 147,218); empty R: `20241016_composio_swekit/astropy__astropy-13398_traj#137`; `20241016_composio_swekit/astropy__astropy-13398_traj#294`; `20241016_composio_swekit/astropy__astropy-14365_traj#157`; `20241025_composio_swekit/astropy__astropy-13453_traj#106`). Included |S| runs 34,974 to 80,111; the
prefill budget is 1,771,353 sender tokens (1.7B and 0.6B) + 427,729 receiver tokens = 3,970,435 tokens. H-E9L is a claim
about these 35; coverage travels with every figure (0032's clause, kept).

**The receiver configuration (D1(a)) and the upstream change.** Both models are loaded with static YaRN in the HF
form `{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}` (window 81,920); Qwen's own
recommendation is factor 4.0 for 131,072 and a smaller factor is the same mechanism. Under YaRN the model's rotary
embedding changes the per-dimension inverse frequencies AND multiplies cos/sin by an attention factor
(transformers 5.15.1 `Qwen3RotaryEmbedding.forward`; 0.1·ln 2.5 + 1 ≈ 1.0916), so the K a model writes is
m·R_yarn(pos)·k_content and the upstream's plain-θ strip would leave a wrong rotation and a factor m in every
content-space K. The upstream commit pinned below (`063f4023fdde`, successor of `4633718`) adds a RoPE spec
(`kvt/rope.py::RopeSpec`) read from the model's OWN rotary embedding (`inv_freq` + `attention_scaling`, never a
formula), written into every dump's `meta.json`, HALT-checked against the model at every position of the dump
before any forward pass (atol 1e-5), and used by `KVDump` to strip (R^T/m); `load_model(model_id, rope_scaling=…)`
and `dump_kv.py --rope-scaling`; archived dumps without the block strip exactly as before (tested: the tiny-model
content key equals `k_norm(k_proj(x))` under YaRN to fp16 tolerance; the plain-θ strip is shown wrong; the halt
fires on a dropped factor or plain frequencies; 153 upstream tests; independent refutation 2026-09-09: spec cos/sin bitwise equal to HF's over all 81,920 positions of the real Qwen3-0.6B config, divide-once residual 9.5e-7 vs ~0.5 for zero or two divisions, YaRN static under transformers' dynamic-update decorator, the archived n = 50 dump strips bit-identically). **Seam outside this entry's route, on the record:** the upstream's live-cache mapper path (`kvt/mapper.py::apply_mapper`, used by the perplexity/hellaswag evals and `compose_mapper.py`) still strips and re-applies with the plain θ; E9's scorer never calls it (content space via `KVDump`), and no eval under a scaled model may run until it takes the spec. **Stated risk:** static YaRN changes the KV of
short contexts too, so this receiver is a different function from 0029's; control 4 measures how different and
fixes how the verdict reads. The mapper is 0029's n = 50 k = 1 artifact by sha (D4 realized as: the driver scores
the n = 50 mapper on every handoff, exactly 0029's shape; the n = 420 mapper of 0033/0034 is applied afterwards at
home to the kept subset through `e9_rescore` under its own config, descriptive, by its own entry if run).

**Run order, stopping rule, resume (unattended overnight sitting).** The driver scores the included handoffs in the
REGISTERED order `n_sender_asc` (|S| ascending, ties by id; there are none): astropy__astropy-7671_traj#85 (34,974) first,
django__django-11087_traj#152 (80,111) last. The controls run on the first handoff in that order. If the sitting must
end before all 35 are scored, `e9 --close-partial --config config/e9l.toml` closes the run: it is allowed only by
this config, it refuses unless the scored set is a PREFIX of the registered order, it stamps the close time and
names every unscored handoff in `report.json`, and the verdict entry states the cell on the scored prefix with
"n scored of 35 registered" beside every number. The cutoff is the operator's and is recorded, with the reason, in
the verdict entry; it may not depend on any score. A relaunch after a crash uses `--resume`, which keeps only the
bridge, the controls and the scored handoffs whose score and per-token files still match their recorded hashes
under the same config sha and pin; a plain relaunch over an unfinished report is refused.

**Keep subset (D3).** n = 3, seed 9, a fresh draw from the sorted newly-included ids (numpy `choice` without
replacement is not nested with 0025's draw of 8): `20241016_composio_swekit/astropy__astropy-8872_traj#117`; `20241025_composio_swekit/django__django-10554_traj#112`; `20241025_composio_swekit/django__django-11087_traj#97`. Their three stride-1 dumps are retained,
fingerprinted, pulled home and re-scored from tensors by the summarizer under 0028's tolerance.

**Controls, registered (1–3 as 0023/0025; 4–5 new; 6 unchanged).** (1) Pipeline identity HALT (a dump scored against
itself, every square exactly zero). (2) Prefix-invariance HALT on the first handoff in run order: S vs S + R's first
token, max centered δ ≤ 1e-04. (3) δ_null: seeded derangement of sender positions (seed 23), the
uninformative scale. **(4) Configuration bridge:** for the three SHORTEST of 0029's kept handoffs (`20241025_composio_swekit/django__django-10999_traj#64`; `20241025_composio_swekit/django__django-11066_traj#36`; `20241016_composio_swekit/astropy__astropy-14182_traj#68`;
|S| 13,955, 14,269, 17,935) the receiver prefills S twice ON THE SAME BOX, once under the native RoPE and once under
the scaling above, and the two dumps are scored at pairs (p, p) over every sender position; both dumps are kept and
fingerprinted, the summarizer re-scores them from tensors and states the median native-vs-scaled f*(τ_K).
**Reading fixed now:** if that median exceeds 0.15, the receiver configuration alone exceeds the mapper's
tolerance and H-E9L is read as a claim about the SCALED receiver only, in the verdict entry's first paragraph. The
bridge runs BEFORE the first long handoff and is checkpointed, so a late failure cannot lose it; it cannot gate the
launch, it gates the reading. **(5) Length profiles (descriptive):** f*(τ_K) and median δ_K (i) by |S| bin
(32,768, 49,999] / [50,000, 64,999] / [65,000, 81,920], and (ii) by matched-token position in S [0, 32,767] / [32,768, 49,151] / [49,152, 65,535] / [65,536, 81,920] — (ii) is
the long-context figure: does agreement at a re-rendered position depend on how deep in the sender's context the
token sat. (6) Seam profiles b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9l.toml` refuses until entries 0019/0023/0025/0027/0035 are in the
committed ledger, `config/e9l.toml` is committed unmodified, the upstream is at the pin with every invoked path
clean, and the mapper artifact is present by sha; `summarize_e9 --config config/e9l.toml` (fail-closed, the only
reader) re-derives every alignment from the raw traces with the floor, recomputes every figure, re-scores the kept
and bridge dumps from tensors, checks the controls, states the bridge reading, the profiles and the band, and
refuses on any disagreement. Tests: the floor, the scaling on every dump, the bridge first and recorded, the run
order, resume, the partial close and its prefix rule, and that `config/e9.toml`'s behaviour is untouched.

**Paper scope (operator ruling 2026-09-09; supersedes 0032's space clause).** The LCFM 4-pager is re-cut with long
context central: E9 (0029) and E9-long are the results; E-RL (`docs/2026-09-02-e-rl-design.md`, designed and
unregistered — stated as such, in those words) is the contrasting registered direction on the weights axis; E7 is
the corpus paragraph; E8 is one sentence with its table in an appendix. 0032's clause "E9 is one paragraph, one table
… Lane A/B premise numbers and the taxonomy remain the submission's core" is superseded by this paragraph. **Kept
from 0032, unchanged:** E9 and E9-long figures enter the 4-pager only from a passing `summarize_e9` run (E9's at the
detached `d5786df` checkout, 2026-09-09; E9-long's under `config/e9l.toml`); the same-model result never appears
without the cross-model outcome in the same table or sentence; coverage travels with every number, and E9-long's
reads "n of 35 newly included, the long half, never pooled with 0029's 25"; the co-author refutation of 0025–0029 is
still owed and 0032's consequence for E9's figures stands as written — a later entry records it either way. E9-long's
figures enter by their own numbered entry.

**What this does NOT touch.** The H-E9 cell (0029), τ_K, τ_V, τ_agent_K, the rule, the band, the ladder, 0025's keep
subset, `results/e9/`, `results/e8*/`, `results/e9c/` and `config/e9.toml` are unchanged (its sha is in 0029's
report); no `verdict:` line here. The n = 420 arm is not run under this entry. Nothing here is a figure.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the long half of one corpus; a scaled
receiver that is not the trained-range model of 0029 (control 4 says by how much); floor not method (0027); the
four handoffs above 81,920 and the four with an empty receiver prompt stay excluded by name.

prior-entries-sha256: f6a715fd94402eb419155a2afd2f14fcbb28e954a9e8ee1a16b07ffa920dd5da

### 0036 — 2026-09-10 — E9-long ran `[BASELINE]`; H-E9L HELD (35 scored of 35 registered)

**Bridge reading (entry 0035 control 4): CARRIED.** Median native-vs-scaled f*(τ_K) = 0.0000 over 3 short handoffs, within the registered maximum 0.15; τ_K carries to the scaled receiver.

**Setup, as registered (0035).** AWS EC2 g6e.4xlarge (1x NVIDIA L40S 48 GB), us-east-1d, i-0eafae594ebe8c291; linear-ceiling at the commit carrying 0035 and `config/e9l.toml`
(gate: entries 0019/0023/0025/0027/0035), upstream pin `063f402` (the RoPE-spec commit). Pair qwen3-0.6b-to-1.7b;
receiver Qwen3-1.7B and source Qwen3-0.6B both under `{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}`
(window 81,920); the n = 50 k = 1 mapper of 0016/0020 for the cross arm. Launched 2026-09-09T23:53:12Z, finished 2026-09-10T01:13:09Z.
Complete: 35 scored of 35 registered. Of 68 observed handoffs: 35 registered (|S| or |R| above the prior cap 32,768, both within
81,920), 25 decided under 0029 and excluded here, 4 above the cap, 4 with an empty receiver prompt.
Every figure below is `summarize_e9 --config config/e9l.toml`'s, from a run that passed all of its checks: alignments
re-derived from the raw traces under the cap and floor; the run order re-derived; every R² recomputed from recorded
moments; per-token squares summed against the moments; the 3 kept dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within 4.2e-04 relative, max |f* diff| 0.0e+00); the bridge dumps re-scored from tensors; τ
recomputed from the archived mapper; controls checked.

**Controls (0023, 0025, 0035).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run order:
max centered per-token δ 0.000e+00 over 34,974 positions (tolerance 1e-04). δ_null same K / V token-mean
median 2.015 / 1.975; equal-token null pairs 0.0126. **Bridge (control 4), per handoff:** `django__django-10999_traj#64` (|S| 13,955) K 0.0000 / V 0.0000, median δ_K 0.071; `django__django-11066_traj#36` (|S| 14,269) K 0.0000 / V 0.0000, median δ_K 0.089; `astropy__astropy-14182_traj#68` (|S| 17,935) K 0.0000 / V 0.0000, median δ_K 0.080;
median K 0.0000 / V 0.0000 against the reading maximum 0.15. Matched fraction |M|/|R| (a floor): 0.9606 (p10 0.7735, p90 0.9873).

**The rule (0023, carried verbatim by 0035) and the figure it reads.** Per scored handoff, E9-same, K read-out:
f*(τ_K) = the fraction of matched tokens whose centered per-token deviation exceeds τ_K = 0.3186; median over
scored handoffs; HOLDS ≤ 0.15, DEGRADES ≥ 0.5, UNRESOLVED between.

- **median f*(τ_K), E9-same K: 0.0000 (p10 0.0000, p90 0.0000)** over 35 handoffs (35 scored of 35 registered). Seeded bootstrap of the
  median (seed 25, 2000 reps; reported, not read): [0.0000, 0.0000].
- f*(τ_V = 0.4867), E9-same V (alongside): 0.0000 (p10 0.0000, p90 0.0000).
- τ ladder (descriptive): τ = 0.1: same K 0.0119 (p10 0.0000, p90 0.3876) / V 0.0254 (p10 0.0000, p90 0.4289); τ = 0.03: same K 0.5255 (p10 0.0762, p90 0.9037) / V 0.5837 (p10 0.1829, p90 0.9071).
- f*(τ_agent_K = 0.4371) (alongside): same K 0.0000 (p10 0.0000, p90 0.0000); cross K 0.6651 (p10 0.4968, p90 0.8770).
- f*(τ_K) over matched blocks of length ≥ 4: same K 0.0000 (p10 0.0000, p90 0.0000).
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: 0: 0.260 (n=4050) · 1: 0.153 (n=2956) · 2-3: 0.089 (n=4624) · 4-7: 0.074 (n=7224) · 8-15: 0.086 (n=9451) · 16+: 0.063 (n=359203).
- **Length profiles (0035 control 5, descriptive).** (i) by |S| bin, median f*(τ_K) same K over handoffs: |S| 32769-49999: 0.0000 (p10 0.0000, p90 0.0000) (n = 17); |S| 50000-64999: 0.0000 (p10 0.0000, p90 0.0000) (n = 14); |S| 65000-81920: 0.0000 (p10 0.0000, p90 0.0000) (n = 4).
  (ii) by matched-token position in S, pooled f*(τ_K) same K / median δ_K: positions 0-32767: 0.0000 / 0.038 (n = 284,094); positions 32768-49151: 0.0000 / 0.131 (n = 40,967); positions 49152-65535: 0.0000 / 0.162 (n = 43,643); positions 65536-81920: 0.0000 / 0.092 (n = 18,804).

**Band outcome, against the rule as written: HOLDS** — on the scored prefix, 35 scored of 35 registered, never pooled with 0029's 25.
Not one scored handoff has a single matched token whose centered deviation exceeds τ_K on the same-model arm.

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction (oracle
selection, recompute in isolation); this cell reads "no more than the mapper, on a floor", never that an achievable
scheme reaches it.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through the n = 50 k = 1 mapper: median f*(τ_K)
= 0.9640 (p10 0.9043, p90 0.9904) and f*(τ_V) = 0.9456 (p10 0.9023, p90 0.9863); against the same edges the transfer arm sits beyond the DEGRADES edge.
Cross/same median-δ ratio K / V: 8.2 (p10 3.5, p90 21.9) / 10.5 (p10 5.0, p90 26.3). Bridge R² (A5; decides nothing): same K 0.8894 (p10 0.7977, p90 0.9511),
same V 0.8779 (p10 0.7727, p90 0.9313), cross K 0.4214 (p10 0.3525, p90 0.4578), cross V 0.1478 (p10 0.1079, p90 0.1758). The n = 420 mapper's arm on the kept subset is not
in this entry (its own config and entry, if run).

**What this establishes, stated narrowly.** On Qwen3-1.7B under YaRN factor 2.5 re-rendering 35 real SWE-bench
composio handoffs whose sender prompt runs 32,769–81,920 tokens, with 0019's alignment and 0023's per-token rule, the
same-model oracle recompute floor is as stated above. **Not established:** anything
about the 0 unscored registered handoffs (none), the four above 81,920 or the four with an empty receiver prompt;
any achievable recompute scheme; the trained-range receiver of 0029 at these lengths;
one pair, one direction, one mapper, one alignment method; generation quality after reuse.

verdict: H-E9L = HELD
e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 055a140592979dd40bb2cbfcd106612aaeea2e6dc6f87514aab77212be7ce08c

### 0037 — 2026-09-13 — E9 scaled short cell registered before any prefill: 0029's 25 handoffs under 0036's receiver configuration; descriptive, decides nothing

**Why, and why now.** The 4-pager's two cells differ in receiver configuration as well as length: 0029 (H-E9, the 25
handoffs within 32,768) was measured on the native receiver, 0036 (H-E9L, the 35 handoffs of 35K–80K) on a receiver
scaled by static YaRN 2.5. 0036's configuration bridge (control 4) measured, on three short handoffs at pairs (p, p),
that YaRN alone moves the content key by a median δ_K of 0.071–0.089 — the same order as the cross-cell difference in
the far-from-seam floor (16+ bin: 0.019 in 0029, 0.063 in 0036) and a plausible part of the τ = 0.03 ladder's move
(0.1433 → 0.5255). Every "what length changes" figure in the paper (outline v3 §5.2) is therefore length AND
configuration. This entry registers, before any prefill, the run that removes the configuration from that comparison:
0029's 25 handoffs, re-rendered under 0036's receiver, scored by 0029's instrument unchanged. `results/e9s/` holds
no report and no score file at append; this script refuses otherwise (R1). The only thing under it is the
instrument's own alignment pass (`e9 --align-only --config config/e9s.toml`, `align/coverage.json` sha256
`c371185c7e06`), which reproduces 0029's coverage and keep draw exactly (checked by this script
against `results/e9/report.json`: the same 25 included ids with the same `n_sender`/`n_receiver`/`n_matched` and
text hashes, the same 43 excluded, the same eight kept).

**What is measured, and what is not decided.** The instrument is 0023/0025/0027's verbatim (`[e9.rule]`, `[e9.controls]`,
`[e9.alignment]`, `[e9.mapper]`, `[e9.keep]` byte-for-byte `config/e9.toml`): per matched token the centered deviation
in R²'s units between the receiver's own K at the sender position and at the re-rendered position; f*(τ_K = 0.3186)
as the oracle selective-recompute fraction defined on the MEAN of the remaining tokens (0023), read on a floor (0027);
τ_V = 0.4867, τ_agent_K = 0.4371, the τ ladder (0.1, 0.03), the seam bins, the block floor (4), the
bootstrap (seed 25, 2000 reps), the cross arm through 0029's n = 50 k = 1 mapper by sha. **No hypothesis row is
added and no `verdict:` line will follow:** H-E9 (0029) and H-E9L (0036) are immutable; this run's band word, if
stated, is descriptive. Cap 32,768, no floor, so the verdict set of 0029 is the whole included set: **68
observed · 25 included · 43 excluded** (0029's reasons, unchanged). Prefill budget 578,338 sender tokens (1.7B and
0.6B) + 166,967 receiver tokens = 1,323,643 tokens.

**The receiver configuration.** Both models under static YaRN in the HF form `{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}`,
exactly 0036's, on every dump of the run, at the upstream pin `063f4023fdde` (0035's RoPE-spec commit: the
spec is read from the model's own rotary embedding, halt-checked at dump time, and stripped as R^T/m). The native
run's pin `d5786df` is NOT usable here: its strip is plain-θ and would be wrong under YaRN (0035).

**The registered reading (`linear_ceiling.e9_compare`, fail-closed; descriptive).** After a passing
`summarize_e9 --config config/e9s.toml`, the comparison reads the native run (`results/e9/`) and the scaled run
(`results/e9s/`) token by token: it refuses unless both are complete under their committed configs, cover the same
25 handoffs, share every alignment array byte for byte, and every score and per-token record matches the hash its
report recorded. It states, per handoff and in the median over handoffs, the paired difference of the mean δ_K
(scaled − native; seeded bootstrap of the median, seed 37, 2000 reps), f*(τ) at τ_K and on the ladder under both
receivers, the fraction of tokens over τ_K under both, the pooled per-token difference, and the seam profile b⁻(t)
under both. Against `results/e9l/summary.json` it states the **configuration share**: (scaled − native) / (long −
native) for the far-from-seam (16+) median δ_K and for each ladder τ's median f*. **Reading fixed now:** a share near
1 says the receiver configuration accounts for the cross-cell difference and the paper's "what length changes"
figures are re-stated as configuration effects; a share near 0 says the handoffs do and length is the remaining
candidate; in between the paper reports both. None of these is a claim about length alone: the two cells are
different handoffs. The one thing this run can change in the paper is which sentence follows each 0036 descriptive.

**Run order, stopping rule, resume.** As 0035: `n_sender_asc` (|S| ascending, ties by id), controls on the first handoff
in that order, `--close-partial` allowed only on a prefix of the registered order with every unscored handoff named,
`--resume` after a crash. A partial close leaves the comparison undefined on the unscored handoffs, which
`e9_compare` refuses; the entry recording the figures states "n scored of 25 registered".

**Keep subset.** 0025's draw reproduced: seed 9, n 8 over the same sorted ids → the same eight handoffs
(`20241016_composio_swekit/astropy__astropy-14182_traj#68`; `20241016_composio_swekit/astropy__astropy-7166_traj#88`; `20241016_composio_swekit/astropy__astropy-7606_traj#88`; `20241025_composio_swekit/astropy__astropy-14096_traj#80`; `20241025_composio_swekit/astropy__astropy-14365_traj#119`; `20241025_composio_swekit/astropy__astropy-14995_traj#74`; `20241025_composio_swekit/django__django-10999_traj#64`; `20241025_composio_swekit/django__django-11066_traj#36`). Their scaled stride-1 dumps are retained, fingerprinted, pulled home beside their native twins
under `results/e9/scratch/`, and re-scored from tensors by the summarizer under 0028's tolerance. A (p, p)
native-vs-scaled read on these eight at home, CPU only, is available and is not registered here.

**Controls (1–3 as 0023/0025; 6 as 0025).** (1) Pipeline identity HALT. (2) Prefix-invariance HALT on the first handoff in
run order, max centered δ ≤ 1e-04. (3) δ_null (seed 23). No configuration bridge (control 4) and no length
profiles (control 5): the whole run is the bridge, over all 25 handoffs at the pairs the instrument actually reads.
(6) Seam profiles b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9s.toml` refuses until entries 0019/0023/0025/0027/0035/0037 are in the
committed ledger, `config/e9s.toml` is committed unmodified, the upstream is at the pin with every invoked path clean,
and the mapper artifact is present by sha; `summarize_e9 --config config/e9s.toml` is the only reader of the run's
figures and `e9_compare` the only reader of the comparison; both refuse on any disagreement. Tests:
`tests/test_e9_scaled_short.py` (the config is 0029's instrument under 0036's receiver; the comparison refuses on a
different handoff set, a different pairing, an incomplete run, a report under another config, and an edited record).

**What this does NOT touch.** The H-E9 and H-E9L cells, τ_K, τ_V, τ_agent_K, the rule, the band, the ladder, 0025's keep
subset, `results/e9/`, `results/e9l/`, `results/e8*/`, `results/e9c/`, `config/e9.toml` and `config/e9l.toml`. The
n = 420 arm is not run under this entry. Nothing here is a figure; the comparison's figures enter by their own
numbered entry, and the paper only from that entry.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the short half of one corpus under a
receiver that is not the trained-range model; floor not method (0027); generation quality after reuse not measured.

prior-entries-sha256: f24f8df65f91e62ada4cd9097f0afe685ec76b944cfe2c5fc9da2b8050ddf2bc

### 0038 — 2026-09-14 — E9 scaled short cell ran `[BASELINE, DESCRIPTIVE]`: 0029's 25 handoffs under 0036's receiver; the configuration share stated; no cell moves (25 scored of 25 registered)

**Setup, as registered (0037).** AWS EC2 g6e.4xlarge (1× NVIDIA L40S 48 GB), us-east-1c, i-03c1b238426ff218c; linear-ceiling at the commit carrying 0037 and `config/e9s.toml` (gate: entries
0019/0023/0025/0027/0035/0037, printed ready from a fresh clone on the box), upstream pin `063f402` (0035's
RoPE-spec commit). Pair qwen3-0.6b-to-1.7b; receiver Qwen3-1.7B and source Qwen3-0.6B both under
`{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}` (window 32,768, no floor); the n = 50 k = 1 mapper of 0016/0020 for the cross
arm. Launched 2026-09-14T02:26:08Z, finished 2026-09-14T02:56Z. Complete: 25 scored of 25 registered, in 0037's order; of 68 observed handoffs 25
included and 43 excluded, 0029's sets exactly. Every figure in the next three paragraphs is
`summarize_e9 --config config/e9s.toml`'s, from a run that passed all of its checks: alignments re-derived from the raw
traces; the run order re-derived; every R² recomputed from recorded moments; per-token squares summed against the moments;
the 8 kept handoffs' stride-1 dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square
within 3.2e-04 relative, max |f* diff| 0.0e+00); τ recomputed from the archived mapper; controls checked.

**Two departures from 0037's text, neither moving a figure.** (i) The cell's τ calibration
(`summarize_e9 --calibrate-tau --config config/e9s.toml`) was written at home after the GPU run, not before it: the
runbook omitted the step, `e9 --check` does not look for it, and the summarizer refused until it existed. The calibration
reads only the upstream mapper, the archived generic dumps, the archived `r2.json` and E8's report — no artifact of this
run — and gave τ_K, τ_V and τ_agent_K identical to E9-long's calibration at the same pin; the summarizer recomputed it and
refused on any disagreement with config. (ii) 0037 says the eight scaled kept dumps are pulled home "beside their native
twins under `results/e9/scratch/`"; they are under `results/e9s/scratch/` (this config's results directory), with the same
directory names as the native twins in `results/e9/scratch/`.

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run order: max
centered per-token δ 0.000e+00 over 8,213 positions (tolerance 1e-04). δ_null same K / V token-mean median
2.021 / 1.988; equal-token null pairs 0.0106. Matched fraction |M|/|R| (a floor): 0.9344 (p10 0.8838, p90 0.9783).
No bridge and no length profiles (0037: the whole run is the bridge).

**The scaled cell under 0023's statistic (descriptive; the band word decides nothing here).** E9-same, K read-out, τ_K =
0.3186: median f*(τ_K) 0.0000 (p10 0.0000, p90 0.0000) over 25 handoffs; seeded bootstrap of the median (seed 25,
2000 reps) [0.0000, 0.0000]; against 0023's edges the band word would be HOLDS, stated
descriptively. f*(τ) is 0023's MEAN-repair statistic: it is the fraction of tokens an oracle must recompute before the
mean δ of the rest is at or below τ, not the fraction of tokens whose δ exceeds τ (that fraction is stated under both
receivers in the next paragraph). f*(τ_V = 0.4867), E9-same V: 0.0000 (p10 0.0000, p90 0.0000). τ ladder: τ = 0.1: same K 0.0000 (p10 0.0000, p90 0.2200) / V 0.0033 (p10 0.0000, p90 0.2634); τ = 0.03: same K 0.2930 (p10 0.0919, p90 0.6653) / V 0.3988 (p10 0.1432, p90 0.6855).
f*(τ_agent_K = 0.4371): same K 0.0000 (p10 0.0000, p90 0.0000); cross K 0.6141 (p10 0.4800, p90 0.7559). Over matched blocks of length ≥
4: same K 0.0000 (p10 0.0000, p90 0.0000). Seam profile b⁻(t), same K, pooled median δ by bin: 0: 0.265 (n=2278) · 1: 0.145 (n=1599) · 2-3: 0.093 (n=2571) · 4-7: 0.071 (n=4039) · 8-15: 0.075 (n=5480) · 16+: 0.038 (n=139290).
Cross arm (the n = 50 k = 1 mapper): f*(τ_K) 0.9500 (p10 0.8957, p90 0.9782), f*(τ_V) 0.9215 (p10 0.8877, p90 0.9519), beyond the DEGRADES edge; cross/same
median-δ ratio K / V 15.4 (p10 4.5, p90 23.9) / 17.7 (p10 5.5, p90 29.7); R² across the handoff (A5, the summarizer's "bridge R²", not control
4; decides nothing) same K 0.9105 (p10 0.8266, p90 0.9463), cross K 0.4317 (p10 0.3833, p90 0.4527).

**The registered reading (`e9_compare`, 0037).** Native run `results/e9/` (0029) against this run on identical tokens:
25 handoffs, 155,257 matched tokens, every alignment array byte-identical, every score and per-token
record on its reported hash. Per-handoff mean δ_K, median over handoffs: native 0.0682 →
scaled 0.0895; paired (scaled − native) median 0.0165 (p10 0.0118, p90 0.0231),
seeded bootstrap of the median (seed 37, 2000 reps) [0.0152, 0.0171].
f*(τ) median over handoffs, native → scaled: τ = 0.3186: 0.0000 → 0.0000; τ = 0.1: 0.0000 → 0.0000; τ = 0.03: 0.1433 → 0.2930. Fraction of matched tokens with δ_K over τ_K, median over
handoffs: native 0.0437 → scaled 0.0527. Pooled per-token (scaled − native):
median 0.0115, p10 -0.0054, p90 0.0459, p99 0.2793. Seam profile b⁻(t),
pooled median δ_K native → scaled: 0: 0.236 → 0.265 (n=2,278) · 1: 0.127 → 0.145 (n=1,599) · 2-3: 0.081 → 0.093 (n=2,571) · 4-7: 0.062 → 0.071 (n=4,039) · 8-15: 0.063 → 0.075 (n=5,480) · 16+: 0.019 → 0.038 (n=139,290).

**The configuration share, against the long cell** (`results/e9l/summary.json`, 35 handoffs; (scaled − native) /
(long − native)). Far-from-seam (16+) median δ_K: native 0.0195, scaled 0.0381, long
0.0629 → share 0.4285. Ladder: τ = 0.1: native 0.0000, scaled 0.0000, long 0.0119 → share 0.0000 (both short-cell medians are 0, a floor, so this share is 0 by construction and does not measure how far the configuration moves f* at this τ); τ = 0.03: native 0.1433, scaled 0.2930, long 0.5255 → share 0.3916. 0037's reading, fixed before any prefill and quoted, not
applied beyond it: "a share near 1 says the receiver configuration accounts for the cross-cell difference and the
paper's 'what length changes' figures are re-stated as configuration effects; a share near 0 says the handoffs do and
length is the remaining candidate; in between the paper reports both." No threshold for "near" was registered; the
values above are the reading.

**What this establishes, stated narrowly.** On 0029's 25 SWE-bench composio handoffs, with 0019's alignment and 0023's
per-token statistic, how far YaRN factor 2.5 alone moves the receiver's own content key at the pairs the instrument
reads, and what share of the 0029 → 0036 difference that movement reproduces on identical tokens. **Not established:**
anything about length alone (the long cell is different handoffs); the H-E9 or H-E9L cell (unchanged); any achievable
recompute scheme (a floor, 0027); the n = 420 arm; the (p, p) twin read of the kept eight (not registered); one pair,
one direction, one mapper, one alignment method; generation quality after reuse.

e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: c9128ee936cd7e8afefa0301ddf9f8306abbe4676de31480fe9db50c8d037a54

### 0039 — 2026-09-18 — A second model family registered before any fit: the matched-KV pair meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B, the upstream re-pin that registers it, the amended seal requirement, and E8 on the new pair; descriptive, no hypothesis row

**Why, and why now.** Every result on this ledger is one pair: Qwen3-0.6B → 1.7B. H-E8 `NOT CONFIRMED`
(0020), H-E9 `HELD` (0029) and H-E9L `HELD` (0036) are claims about that pair, and the honest reading of
all three has always been "one pair, one direction, one mapper". A second family is the cheapest thing
that can turn a single-pair observation into a statement with any generality, and it is the first
question a reviewer asks. This entry registers the family — the pair, the upstream change that makes the
instrument accept it, the amended seal requirement, and E8 on it — BEFORE any mapper is fitted and before the calibration
text is drawn. It decides nothing: **no hypothesis row is added, no `verdict:` line follows, and the
H-E8 cell does not move.** The one verdict-bearing cell of this campaign is the E9 short cell, registered
by its own later entry with its own row.

**The pair, and the fact the whole design rests on.** `llama3.2-3b-to-llama3.1-8b` = meta-llama/Llama-3.2-3B (source) → meta-llama/Llama-3.1-8B
(receiver/target). Cross-release inside one family, so the name carries BOTH sides: the upstream's
same-release short form names only the TARGET's size, which here would assert a Llama-3.2-8B — a model
that does not exist. The string keys the mapper directory, the dumps, the token file and every report,
so a name that misidentifies the receiver is
not recoverable. **The pair is matched-KV**, which is what makes the upstream delta one line:
both sides carry 8 KV heads and a per-head dim of 128, so `check_matched_kv` passes unrelaxed, the
paper's Sec. 2.1 premise holds, and `Mapper.formula_params` is exact for this pair (the Appendix-D /
Table-12 parameter-count control is preserved, not forfeited). Read from the two GATED `meta-llama`
snapshots by `tools/preflight_pair.py`, record sha256 `e99c29a75d0b` (2026-09-18T13:14:29Z),
20/20 checks passed, and cited by nothing else —
no mirror, no re-upload, no remembered value ({sourceRepo: meta-llama/Llama-3.2-3B, filePath: config.json, sha256:
35f063e9f381} and {sourceRepo: meta-llama/Llama-3.1-8B, filePath: config.json, sha256:
54acfad3cffe}): Llama-3.2-3B: 28 layers, hidden 3072, 24 attention heads, 8 KV heads, head_dim 128 (declared), vocab 128,256, max_position_embeddings 131,072, rope_theta 500000, rope_scaling {"factor": 32.0, "high_freq_factor": 4.0, "low_freq_factor": 1.0, "original_max_position_embeddings": 8192, "rope_type": "llama3"}, tie_word_embeddings True, 229,376 KV bytes/token (fp32, all layers, K and V) · Llama-3.1-8B: 32 layers, hidden 4096, 32 attention heads, 8 KV heads, head_dim 128 (DERIVED as hidden_size // num_attention_heads; the config declares none), vocab 128,256, max_position_embeddings 131,072, rope_theta 500000, rope_scaling {"factor": 8.0, "high_freq_factor": 4.0, "low_freq_factor": 1.0, "original_max_position_embeddings": 8192, "rope_type": "llama3"}, tie_word_embeddings False, 262,144 KV bytes/token (fp32, all layers, K and V).

**The shared-vocabulary gate, which could still kill this.** `scripts/prepare_tokens.py` refuses unless
the two tokenizers' `get_vocab()` maps are equal, and `weights.assert_shared_vocab` is the home-side half
of the same check. Both sides ship the 128,256-entry Llama-3 BPE, but added and special
tokens are part of that map. The preflight record's check "shared vocab: get_vocab() maps" passed —
128256 entries, identical mapping — and that is the evidence; had it failed there would be no E8 corpus for this pair
and the family decision would reopen rather than be worked around.

**The two sides carry DIFFERENT RoPE, and that is safe here for a stated reason.** Source
rope_scaling {"factor": 32.0, "high_freq_factor": 4.0, "low_freq_factor": 1.0, "original_max_position_embeddings": 8192, "rope_type": "llama3"}; receiver {"factor": 8.0, "high_freq_factor": 4.0, "low_freq_factor": 1.0, "original_max_position_embeddings": 8192, "rope_type": "llama3"}. The two
build different inverse-frequency vectors. That is not a matched-KV problem (`check_matched_kv` reads
`n_kv` and `d_h` only) and not a content-space problem — PROVIDED the pin strips with each dump's OWN
recorded `RopeSpec`, read off the loaded model's `rotary_emb.inv_freq` and halt-checked at every dumped
position. That machinery is entry 0035's commit `063f4023fdde`, and this entry requires the pin to be a
DESCENDANT of it (checked by this script). Under an older base the strip is plain-θ, which is silently
wrong for `rope_type "llama3"` on both sides. Consequence carried forward to every cell of this family:
any "the recorded RoPE is identical across the run" control is scoped **per model role** — receiver dumps
against receiver dumps, source dumps against source dumps — because a cross-role equality assert would
refuse every CORRECT run of this pair.

**The upstream change, and what it is not.** Pin `06f8d5559257`, base 063f4023fdde: **one entry in
`kvt/pairs.py`'s `PAIRS`**, so `dump_kv`, `fit_mapper`, `probe`, `score_mapper` and `score_positions`
accept the pair by name. No dataclass change, no signature change, no relaxation of any check, no new
flag. An earlier design for this campaign assumed unmatched head dims and specified a rectangular
mapper, a registry flag, a `check_kv_heads`, a `formula_params` signature change and a τ ceiling
justified by the conditioning of that map; **the pair is matched-KV, so every one of those is dropped**
and nothing about the estimator is extended. `linear-ceiling` never writes upstream: the change is landed
by the operator from `docs/2026-09-18-llama-upstream-patch-spec.md` and pushed before any box is rented
(`tools/ec2/setup.sh` clones by sha). **Known limitation, recorded rather than fixed:**
`kvt/mapper.py::apply_mapper` still strips and re-applies with the plain θ it records, so it is wrong for
any `rope_type != "default"` and therefore for this pair; it is OFF the E8/E9 path (the scorers work in
content space through `KVDump`), so `eval_hellaswag.py` and `compose_mapper.py` must not be run on this
pair without a fix. Keeping the diff at one dict entry is worth more than pre-emptively fixing a path
nobody here calls. **While the single upstream checkout sits at this pin the Qwen cells refuse at their
gates** — existing practice, not a regression: re-summarizing a Qwen cell means
`git -C kv-transfer-replication checkout --detach <that cell's pin>` first. There is ONE clone.

**The seal (invariant 1), AMENDED for this entry — operator ruling, 2026-09-18.** This registration
carries **no sealed prediction**, and the requirement is amended rather than satisfied. Invariant 1
exists for the SCREEN's pre-fit predictions: a prediction that can be sealed before a fit must be.
The screen line is `SHELVED` (H-S1/S3/S4, entries 0003–0006) and `screen.py` has no entry point that
produces a payload, so there is no screen prediction about this pair to seal. The alternatives were
considered and rejected in the open: sealing a *null* or procedural payload would satisfy the check
while asserting nothing, which is precisely the failure this ledger is built to prevent; and inventing
a pre-fit R² to seal would put a number on the record that no instrument produced. The amendment is
narrow — it applies to a **descriptive second-family registration that adds no hypothesis row**, and
it does not touch invariant 1 for any cell that does carry a screen prediction.

What survives the amendment is the clause that actually carries the evidential weight: **no fitted
mapper for this pair exists in ANY configured artifact root at append** (this script re-checks all
four and refuses otherwise), and this script additionally refuses if a sealed prediction for the pair
has appeared since the ruling. "Registered before any fit" therefore remains a checkable claim about
the world, not an assertion of good faith.

**E8 on the new pair (`config/e8f.toml`, `results/e8f/`).** 0009's instrument and 0016's amendment,
unchanged: mapper fit on generic calibration text, scored on agent-trace text, arm (a) generic vs arm (b)
agent, held-out pooled R² (definition A5), band HOLDS ≤ 0.05 drop /
DEGRADES ≥ 0.15 drop; verdict k = 1 fixed here at registration
(not chosen after the sweep), reported at k = 1, 4, 8; `[e8.text]` seed
8, n = 50, len = 1024, suites tau2-bench, swe-bench, window
"first"; holdout 0.2, stride 4. **The sampling RULE is 0016's
byte-for-byte; the DRAW is not** — it is re-made under the Llama-3 BPE and is a different
50 windows, not a reuse of `results/e8/`'s. Parameter count per read-out is
p = k · n_kv · d_h = 1,024k against n_train = 10,240, so **p/n is k = 1: 0.10 / k = 4: 0.40 / k = 8: 0.80** — numerically
identical to the Qwen arm's, because the two pairs happen to share 8 KV heads and head_dim 128. The
k-sweep collapse entry 0016 reports is therefore directly comparable here at the same p/n, and there is no
p/n caveat to state. **Descriptive: every figure produced
under this config is stated for the Llama pair alone and is never pooled with a Qwen figure; H-E8's cell
was decided by 0020 and does not move.** Scope recorded in the report: "off-policy text for Llama-3; cross-release pair (source 3.2, receiver 3.1); matched-KV (8 x 128 both sides); not a real switch point; visible messages only (0012)".

**BOS carry-over, stated rather than changed.** The existing instrument tokenizes with
`add_special_tokens=False` in both the generic-calibration and agent-text paths, and that rule carries
over unchanged. Llama-3's `<|begin_of_text|>` is therefore absent and the first content token takes the
attention-sink role. This is self-consistent across the two E8 arms and preserves comparability with the
registered instrument; it is not a claim that the token layout matches a normal chat/inference request.

**Three decisions fixed now, before any number exists.** The E9 cells of this family calibrate τ from
THIS pair's own mapper, and three values that follow from τ_K must be fixed before τ_K is seen or they
are not registered at all. (1) **τ ladder** (`[e9.rule] tau_ladder`, descriptive, verdict-bearing for
nothing): ABSOLUTE [0.10, 0.03], identical to config/e9.toml; not a function of tau_K (operator ruling 2026-09-18). (2) **Prefix-invariance tolerance**
(`[e9.controls] prefix_invariance_max_delta`, a HALT): ABSOLUTE 1e-4, identical to config/e9.toml; a float32 kernel-noise floor (operator ruling 2026-09-18). It must NOT inherit the
Qwen cells' value. (3) **τ_K ceiling** — the τ_K above which the short cell is UNRESOLVED by
construction, because a mapper that transfers badly enough makes f*(τ_K) trivially small for everything:
0.45. All five tau-derived keys in `config/e9f.toml` and `config/e9fl.toml` carry refusing
`UNRESOLVED::` markers at append (this script checks it), so neither cell can load, let alone run, until
the calibration exists — a Qwen τ pasted in would load and produce a verdict calibrated against the wrong
pair's mapper, which is the failure the markers exist to make impossible.

**Gate and enforcement.** `e8 --check --config config/e8f.toml` refuses until entries 0009/0016/0039 are in the
committed ledger, `config/e8f.toml` is committed unmodified, and the upstream is at the pin with every
invoked path clean; `[e8.gate]` EXTENDS the driver's 0009/0016 premise entries and cannot weaken them.
`summarize_e8 --config config/e8f.toml` is the only reader of the run's figures: it re-runs the upstream
scorer on the fingerprinted dumps, cross-checks arm (a) against the archived `r2.json` for every k, and
refuses on any disagreement. Tests: `tests/test_pairs.py` (the pair name round-trips and the Qwen names
are byte-identical), `tests/test_llama_configs.py` (the three configs; the five tau keys refuse
individually), `tools/preflight_pair.py` (the gate on the two gated checkpoints).

**What this does NOT touch.** The H-E8, H-E9 and H-E9L cells; τ_K, τ_V, τ_agent_K, the rule, the band,
the ladder and the keep subsets of the Qwen cells; `results/e8*/`, `results/e9*/`; `config/e8.toml`,
`config/e8a.toml`, `config/e8c.toml`, `config/e9.toml`, `config/e9l.toml`, `config/e9s.toml`,
`config/e9c.toml` and `config/seal.toml` (unchanged: `_resolve` expands only the literal `${upstream}`,
and the four existing artifact roots already cover the new pair under one clone). No figure appears in
this entry: E8's enter by their own numbered entry, and the paper only from that entry.

**Scope.** One new pair, one direction, one agent family, off-policy text for Llama-3, visible messages
only (0012); a cross-release pair whose two sides carry different llama3 RoPE factors; a registration,
not a result. The matched-KV premise rests on the preflight record cited above and on nothing else.

prior-entries-sha256: 0c8bc66ba38a207ba5d01b8cc98a4f318f26aac4b089af78b4affdfb4393d725

### 0040 — 2026-09-18 — E8 ran on the second model family `[BASELINE, DESCRIPTIVE]`: llama3.2-3b-to-llama3.1-8b; the pair's own τ stated; no cell moves

**Provenance.** Registered by 0039 before any fit; `config/e8f.toml` and this ledger committed
unmodified; upstream at the pin `06f8d55` (the one-line `PAIRS` entry on top of the
RoPE-spec commit), clean for every invoked path; entry 0039's no-seal ruling re-verified AFTER the fit:
no `ledger/predictions/llama3.2-3b-to-llama3.1-8b.*` sidecar exists, so no post-fit prediction is presented as pre-fit.
RunPod secure A40 48GB, pod 4cxydvpwbyr1ix, machine 9abgo2ybpf3t; launched 2026-09-18T15:47:09Z, finished 2026-09-18T18:13:29Z. Source meta-llama/Llama-3.2-3B, receiver meta-llama/Llama-3.1-8B. Every figure
below is `summarize_e8 --config config/e8f.toml`'s, from a run that passed all of its checks: the upstream
scorer re-run on the fingerprinted dumps, arm (a) cross-checked against the archived `r2.json` for every k
(at the verdict k: archived 0.713867 vs recomputed 0.713867), the mapper
bytes re-hashed (k = 1: `k1.json` 6cbfad42b6b0,
`k1.safetensors` fe77166a8ff4), the agent token file and its manifest re-hashed
(agent_n50_len1024_seed8.npy, sha256 4e02d14af008).

**What ran.** 0009's instrument with 0016's amendment, unchanged and re-registered by 0039: the mapper
is fit on generic calibration text and scored on agent-trace text; arm (a) is the generic held-out arm,
arm (b) the agent arm; the figure is held-out pooled R² (definition A5, per head, averaged over heads then
layers). The sampling RULE is 0016's byte-for-byte — seed 8, n = 50,
len = 1024, suites tau2-bench, swe-bench, window "first", holdout 0.2,
stride 4 — and the DRAW is this pair's own, re-made under the Llama-3 BPE. Parameter count per
read-out p = k · n_kv · d_h against n_train = 10,240.

| k | arm (a) generic K / V | arm (b) agent K / V | drop K / V | band K / V |
|---|---|---|---|---|
| 1 (verdict-bearing, K and V separately) | 0.7139 / 0.4711 | 0.7311 / 0.4599 | -0.0172 / +0.0111 | HOLDS / HOLDS |
| 4 (reported only) | 0.6183 / 0.2909 | 0.6219 / 0.2265 | -0.0036 / +0.0644 | HOLDS / UNRESOLVED |
| 8 (reported only) | -0.0591 / -0.9696 | -0.1333 / -1.3388 | +0.0742 / +0.3692 | UNRESOLVED / DEGRADES |

Band (entry 0009, unchanged): HOLDS if the drop ≤ 0.05, DEGRADES if the drop ≥
0.15, UNRESOLVED between; verdict k = 1 fixed at registration, K
and V read separately and neither alone (0009) → K **HOLDS** / V **HOLDS**. **This is a
DESCRIPTIVE reading of the band on a second pair. H-E8's cell was decided by entry 0020 on the Qwen pair
under the registered 0016 protocol; it does not move, this entry carries no `verdict:` line, and no figure
here is pooled with a Qwen figure.**

**This pair's τ, stated here and written nowhere yet.** τ per read-out is 1 − this pair's archived
held-out R² at the verdict k, and it is the only calibration the family's E9 cells may use: **τ_K =
1 − 0.7139 = 0.2861**, τ_V = 1 − 0.4711 =
0.5289, and the alongside agent-text tolerance τ_agent_K = 1 − 0.7311 =
0.2689 (entry 0025's arm (b) reading, verdict-bearing for nothing).

**Disclosure: the agent draw repeats windows, and the registered hold-out is two of them.** The arm (b) draw is 50 sequences but only **42 distinct windows**: rows 41–49 are byte-identical, one window appearing **9 times**. `score_mapper` holds out the LAST ceil(0.2 × 50) = 10 sequences, so arm (b)'s registered held-out R² — and therefore τ_agent_K — is computed on **2 distinct windows**, one of them weighted 9×. The repeated window is the opening of 9 DIFFERENT trajectories — 3 from `20250415_openhands` (astropy__astropy-14309, astropy__astropy-14365, astropy__astropy-14369); 6 from `20250616_Skywork-SWE-32B` (astropy__astropy-13398, astropy__astropy-13579, astropy__astropy-14309, astropy__astropy-14369, astropy__astropy-14508, astropy__astropy-14539) — which share a ≥ 1024-token preamble under the Llama-3 BPE, and `[e8.text] window = "first"` takes the FIRST window of each. Entry 0016 §4's rule was followed byte-for-byte and is not changed here; this is a property of the draw it produces on this corpus with this tokenizer. The generic draw is unaffected (checked: all distinct). **No figure in this entry is adjusted for it.** A reading over every agent sequence, or over distinct windows only, requires arm (b) rescored at `agent_holdout_frac = 1.0` with per-sequence records — the shape entry 0030 registered for the Qwen pair — and enters by its own numbered entry, not this one.  **τ_agent_K sits BELOW τ_K on the registered held-out set** (τ_K = 0.2861, τ_agent_K = 0.2689). **This is not stated as a property of the pair.** The registered arm (b) hold-out is the last ceil(0.2 x 50) = 10 sequences of the agent draw, and those 10 rows carry only TWO DISTINCT WINDOWS (see the disclosure above), one of them nine times, so the comparison rests on two windows rather than ten. What the inversion is a property of -- this pair, or this draw -- is not decided by this entry and no rule is changed after seeing it. `load_e9_config` refuses any E9 config carrying these two values, because `config.py` requires `tau_K < tau_agent_K < 1`. **That ordering is registered by no entry.** Entry 0025 registers τ_agent_K's derivation (1 − arm (b)'s held-out K R², recomputed and refused on disagreement) and states that it “is a K tolerance and is applied to nothing else” and that “the band reads τ_K only”; it fixes no ordering. The check predates this family, and its own message calls τ_agent_K “the LOOSER agent-text tolerance from entry 0020 arm (b)” — it encodes what 0020 MEASURED on the Qwen pair. So `config/e9f.toml` and `config/e9fl.toml` cannot load until a numbered entry rules on that check. **Nothing is edited into a config, and no guard is relaxed, to make them load.** These three come
from the arm (a) and arm (b) numbers in the table above, which the summarizer re-derived from the tensors;
they are not carried over from anything. `config/e9f.toml` and `config/e9fl.toml` still carry their
refusing `UNRESOLVED::` markers at this entry (checked by the script that appended it): the next entry
writes these values in and `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report results/e8f/report.json`
then recomputes them from the archived mapper independently and refuses on any disagreement. **A Qwen τ appears nowhere in
this family's configs and never will.** **Corrections to immutable entry 0039** (append-only; neither
changes a registered rule or value, and both are errors of prose in 0039, not of the configs, which
were and are correct): **(i)** 0039 said five τ-derived keys were unresolved. Only `tau_K`, `tau_V` and
`tau_agent_K` carried markers; `tau_ladder = [0.10, 0.03]` and `prefix_invariance_max_delta = 1e-4`
were already literal, registered values. **(ii)** 0039's paragraph (2) registers
`prefix_invariance_max_delta` as "ABSOLUTE 1e-4, identical to config/e9.toml" and then says "It must
NOT inherit the Qwen cells' value." Those two clauses contradict each other. The registered value is
**1e-4, deliberately identical to `config/e9.toml`'s** — it is a float32 kernel-noise floor, a property
of the arithmetic and the attention kernel rather than of how well a mapper fitted, so it does not
scale with τ and has no reason to differ between families. The trailing clause is a leftover from the
superseded framing in which the key was a function of τ_K, and is void. `config/e9f.toml` and
`config/e9fl.toml` carry 1e-4 and always did.

**What this establishes, stated narrowly.** On meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B, a matched-KV cross-release pair, with
a k = 1 linear KV mapper fit on 50 generic calibration windows and scored
on 50 agent-trace windows drawn under 0016's rule from tau2-bench, swe-bench, how much held-out
pooled R² the mapper loses under the content distribution shift, at the k values in the table. **Not
established:** anything about H-E8, which is a Qwen claim and is unchanged; anything about on-policy agent
behaviour (the traces are off-policy for Llama-3 exactly as they were for Qwen) or about a real
mid-trajectory switch point; anything pooled across the two pairs; generation quality after reuse.
`eval_hellaswag.py` and `compose_mapper.py` are out of scope for this pair (upstream `apply_mapper`
re-applies with a plain θ and is wrong for `rope_type "llama3"`; entry 0039).

**Scope.** All of 0009's, 0016's and 0039's limits: one new pair, one direction, one mapper, one
alignment-free calibration corpus, off-policy text for Llama-3, visible messages only (0012). No
hypothesis cell changes with this entry.

prior-entries-sha256: cabb1b15ba3c508ab35124b3121e1f193af265fa3d7fa8d8281f8d85c97692fb

### 0041 — 2026-09-18 — The τ_K < τ_agent_K ordering was never registered; `config.py`'s refusal becomes report-only; descriptive, no cell moves

**What this entry rules, and what it does not.** `config.py` has required
`tau_K < tau_agent_K < 1` of every E9 config. **No entry registers that ordering.** Entry 0025
registers τ_agent_K's *derivation* — 1 − arm (b)'s held-out K R² at the verdict k, recomputed by
`summarize_e9 --calibrate-tau` and refused on disagreement, exactly as τ_K is — and states that it
“is a K tolerance and is applied to nothing else” and that “The band reads τ_K only; this entry does
not move it”. It fixes no ordering between the two. The nearest clause, “a verdict-bearing τ chosen
after seeing which is looser is exactly what 0023 refused to do”, forbids *choosing* a τ after seeing
the data; it presupposes nothing about which is looser, and nothing is chosen here. The requirement
exists only in code, predates this model family, and its own refusal message names τ_agent_K “the
LOOSER agent-text tolerance from entry 0020 arm (b)” — that is what entry 0020 **measured** on the
Qwen pair, which is an observation and not a rule.

**Therefore:** a quantity this ledger says is applied to nothing and reads no band could, in the
code, stop an entire cell from loading. That is corrected in the narrowest available way. The
`load_e9_config` refusal on the ordering becomes a **recorded, reported fact**: the relation between
τ_K and τ_agent_K is stated wherever they are, and refuses nothing. `summarize_e9` states it beside
both values.

**Nothing else moves, and this is exhaustive.** τ_K, τ_V and τ_agent_K keep their registered
derivations (0023, 0025) — no value is edited, anywhere, in any config. The band still reads τ_K
only (0023, 0025). The τ ladder, the τ_K ceiling and the prefix-invariance HALT are untouched
(0039). Every other refusal in `load_e9_config` stands, including the three `UNRESOLVED::` markers
that keep an uncalibrated cell unloadable — this ruling does not make `config/e9f.toml` or
`config/e9fl.toml` loadable by itself; only their own calibration does. `0 < τ_agent_K < 1` is still
required, because a τ outside the unit interval is not a tolerance at all. No hypothesis row is
added, no `verdict:` line follows, and no decided cell moves — H-E8 is entry 0020's and is untouched.

**The occasion, stated so it is not mistaken for the reason.** On `llama3.2-3b-to-llama3.1-8b`, entry 0040 reported
τ_K = 0.2861 and τ_agent_K = 0.2689, so the code refused the family's E9 configs.
That is what made the mismatch visible; it is not what makes it a mismatch. The ruling above would
read identically had the inequality gone the other way, and it is made on what 0025 says rather than
on what this pair measured. **This entry does not claim that this pair's mapper transfers better to
agent text than to generic text.** Entry 0040 disclosed that the registered arm (b) hold-out carries
two distinct windows, one of them weighted nine times, so that comparison rests on two windows and not
on ten; whether the inversion is a property of the pair or of the draw is open, needs arm (b) rescored
at `agent_holdout_frac = 1.0` over every agent sequence, and enters by its own numbered entry.

**Enforcement, and how this entry was checked before it was written.** The appending script refuses
unless (i) entry 0025 still contains both quoted clauses above, read from this ledger — a citation
that has drifted is a false entry; (ii) `config.py` no longer carries the refusal and does carry the
report-only marker, so the change is in the tree *before* the record claims it; and (iii) both
`config/e9f.toml` and `config/e9fl.toml` load with a deliberately INVERTED stand-in τ pair
(τ_K > τ_agent_K), proving the ordering no longer blocks, while their real fields still carry refusing
markers. Tests pin the report-only behaviour and that an out-of-unit-interval τ_agent_K still refuses.

**Scope.** A ruling about what the record registers, on the whole E9 instrument, not about any pair.
It reads no data, decides no hypothesis, and moves no cell.

prior-entries-sha256: b6774ebbb3c06280b2cefc9a85d9287302144cc6c45f941d1dd876b36abcacad

### 0042 — 2026-09-18 — E9 short cell registered before any prefill on the second model family: H-E9's instrument on meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B; H-E9F added `unresolved`; τ recalibrated on this pair's own k = 1 mapper

**Why, and why now.** H-E9 `HELD` (0029) and H-E9L `HELD` (0036) are claims about one pair. Entry 0040
has just run E8 on a second family and produced the one thing a second E9 cell needs: this pair's own
mapper and its own held-out R². This entry registers the cell BEFORE any prefill: `results/e9f/` holds no
report and no score file at append, and the script refuses otherwise (R1). The only things under it are
the instrument's own alignment pass (`e9 --align-only --config config/e9f.toml`, `align/coverage.json`
sha256 `c0764a05f486`) and the τ calibration (`summarize_e9 --calibrate-tau`,
`calibration/tau.json` sha256 `54c6962230fe`), both checked here against the
committed config. **This is the one verdict-bearing cell of the Llama campaign**: the family registration
(0039) and the long half are descriptive, and exactly one hypothesis row is added.

**Hypothesis H-E9F (row added to the table, `unresolved`).** The statement is H-E9's on a second model
family; the rule is 0023's verbatim, with only τ recalibrated. Per matched token the centered deviation in
R²'s units between the receiver's own K at the sender position and at the re-rendered position; a token
needs recompute when it exceeds **τ_K = 0.2861**; the verdict statistic is the median over included
handoffs of the oracle selective-recompute fraction f*(τ_K) on the K read-out; **HOLDS ≤
0.15 / DEGRADES ≥ 0.50 / UNRESOLVED between**. τ_V =
0.5289, τ_agent_K = 0.2689 (alongside, verdict-bearing for nothing), the τ ladder (0.1, 0.03),
the seam bins, the block floor (4) and the bootstrap (seed
25, 2000 reps) are 0025's, unchanged. f* stays an
oracle LOWER BOUND read on a floor (0027).

**τ is this pair's.** τ_K = 1 − 0.7139 =
0.2861 and τ_V = 1 − 0.4711 = 0.5289, the k = 1 mapper's held-out R² over
2,560 tokens (A5 per head, averaged over heads then layers (kvt.mapper.mapper_r2)), recomputed by `summarize_e9 --calibrate-tau`
from the archived mapper (`mappers/llama3.2-3b-to-llama3.1-8b/k1`, json
6cbfad42b6b0) against the archived `r2.json`
(8498e977785e) and entry 0040's E8 report
(4682508afd35); τ_agent_K = 1 − that mapper's agent-arm R² (0025's alongside
tolerance), and on this pair **τ_agent_K = 0.2689 sits BELOW τ_K**. Entry 0041 ruled that the
τ_K < τ_agent_K ordering was never registered, so that relation is REPORTED and enforces nothing; entry
0040 disclosed that the registered arm (b) hold-out carries two distinct windows with one weighted
nine times, so whether the inversion is a property of this pair or of that draw is open and is not decided
here. What `load_e9_config` actually enforces today is: τ_K and τ_V each in (0, 1); the ladder strictly
decreasing inside (0, τ_K); τ_agent_K in (0, 1). The ladder and prefix bound are the exact absolute
literals entry 0039 registered, deliberately identical across families. What keeps a Qwen τ out of
this cell is not an ordering check: it is that `summarize_e9 --calibrate-tau` recomputes all three from
THIS pair's own archived mapper and refuses on any disagreement with this file, and that a test asserts no
`config/e9.toml` constant appears in a Llama config.
**No figure from this cell is ever pooled with a Qwen figure.**

**The verdict set, and why it is not 0029's.** `context_cap = 32,768` is the same NUMERIC
threshold entry 0029 registered, and that is all it shares: it is a registered length threshold in this
pair's own tokens, not a hardware bound (both models are natively long), and `e9_align` measures |S| and
|R| under the pair's own tokenizer, so the Llama-3 BPE re-partitions the handoff set. Coverage from the
alignment pass: **68 observed · 28 included · 36 excluded
above the cap · 4 excluded for an empty receiver prompt**. Included |S| runs 7,435 to
32,478; the prefill budget is 640,898 sender tokens (both models) + 182,192 receiver tokens =
1,463,988 tokens. The 36 above the cap are not lost: the long half of this family
(its own later entry) takes those within its own cap and names the residual above it. H-E9F is a claim
about these 28 handoffs; coverage travels with every figure (0032's clause, kept).

**The receiver is NATIVE, and nothing is scaled.** There is no `[e9.rope]` and therefore no `[e9.bridge]`:
the receiver's own checkpoint declares a window that already covers this cap, so there is no scaled arm to
compare and entry 0035's control 4 does not apply here. What replaces it is read off the dumps themselves
(upstream `kvt/data.py` writes each dump's `RopeSpec` — the `inv_freq` and attention factor of the loaded
model's own rotary embedding — halt-checked against the model at every dumped position, and
`linear_ceiling.e9.dump_rope_meta` keeps that record beside every dump's fingerprint BEFORE the non-kept
dumps are deleted): **(i) native window** — the registered cap must be ≤ every dump's recorded
`max_position_embeddings`, the positive statement that no extrapolation happened; **(ii) frequency
identity** — the recorded spec must be identical across every dump OF THE SAME MODEL ROLE. (ii) is
role-scoped and must be: this pair's two sides carry different llama3 scaling factors and build different
inverse-frequency vectors by construction, so an unscoped equality assert would refuse every CORRECT run.
Both are asserted by `summarize_e9`, which also refuses a dump recording an attention factor other than
1.0 — the only positive evidence that the box applied no scaling the registration does not describe.

**The stopping rule, registered before the run.** `[e9.order] by = "n_sender_asc"` and
`allow_partial = true`. `config/e9.toml` registers neither, because 0029's sitting ran to
completion on a card already paid for; this cell runs under a hard dollar ceiling, and without a
registered stopping rule a budget kill mid-run would yield **no verdict at all** — only a spent card —
because the summarizer refuses a partial close it was never told to expect. Both keys are fixed here,
BEFORE any prefill, exactly as entry 0035 did for the long half. Shortest sender first (ties by handoff
id) means the cheapest handoffs score first, so a kill keeps the MOST handoffs rather than an arbitrary
set, and the order is a deterministic function of the alignment, so the prefix a partial close accepts
cannot be chosen after seeing which handoffs scored well. `e9 --close-partial` may then close an
unfinished run **only** on a PREFIX of that order — never "the ones that happened to finish" — the
closing entry names every unscored handoff by id, and coverage ("n scored of 28 registered")
travels beside every number, as 0036's did. A partial close is a REGISTERED OUTCOME of this cell, not a
rescue, and there is **no registered minimum number of scored handoffs** — the operator's ruling was
shortest-first plus allow-partial, on E9-long's convention that coverage travels beside every number,
and none of this repo's code defines a "too short" prefix. What the instrument actually does, read from
`e9.close_partial` and `summarize_e9`: a close is REFUSED if nothing scored, if the scored set is not a
prefix of the registered order, if the report is already complete, if it was written under another
config, or **if the controls never ran** — the identity, prefix-invariance and null controls execute on
the first handoff in run order, so they are a precondition of any close, not an optional extra. Above
that floor there is no threshold: ANY non-empty prefix is decided by the same rule, the median and the
seeded bootstrap are computed over exactly the scored handoffs, the unscored are named by id, and
coverage ("n scored of 28 registered") is stated beside every number. The reader weighs the
coverage; the entry does not pre-judge it and no later choice is available.

**Tokenisation: `add_special_tokens=False`, carried over and now stated for E9 as well.** Entry 0039
recorded this for E8's generic-calibration and agent-text paths. The same convention governs THIS cell:
every handoff's sender and receiver text is tokenised without special tokens, so Llama-3's
`<|begin_of_text|>` is absent at position 0 and the first content token takes the attention-sink role.
It is registered rather than changed, for the same reason as there — it keeps the instrument identical
to the one the Qwen cells ran under, where the convention was a no-op — and it is stated here so the
E9 cell is not read as a normal chat/inference token layout. A Llama-native-BOS variant is out of scope
and unrun.

**One driver change, stated because it is the registered instrument.** `linear_ceiling.e9` gained
refusals only: every included handoff must carry at least one matched token position, the first handoff
in run order at least two (or the registered derangement null is not computable), a bridge handoff must
be observed and within the cap, and a resumed run must validate each retained control artifact against
its recorded hash before reusing it. **Nothing about what is computed changes** — not the included set,
the run order, the keep draw, the scoring, or any schema — and the new guards were checked against the
decided Qwen cells and would not have refused any of them. They are stated here because a change to the
instrument belongs on the record even when it only adds refusals.

**Run order, keep subset, controls.** The driver scores the included handoffs in `n_sender_asc` order;
the controls run on the first handoff in that order. Keep subset: n = 8, seed 9,
a fresh draw from THIS cell's sorted included ids (numpy `choice` without replacement is not nested with
0025's draw, so it is not a subset of anything): `20241016_composio_swekit/astropy__astropy-14182_traj#68`; `20241016_composio_swekit/astropy__astropy-7166_traj#88`; `20241016_composio_swekit/astropy__astropy-7671_traj#85`; `20241025_composio_swekit/astropy__astropy-14182_traj#78`; `20241025_composio_swekit/astropy__astropy-14508_traj#90`; `20241025_composio_swekit/astropy__astropy-14539_traj#96`; `20241025_composio_swekit/astropy__astropy-14995_traj#74`; `20241025_composio_swekit/astropy__astropy-7166_traj#66`. Their three stride-1 dumps are retained,
fingerprinted, pulled home and re-scored from tensors by the summarizer under 0028's tolerance. Controls
(1–3 as 0023/0025; 6 as 0025): (1) pipeline identity HALT (a dump scored against itself, every square
exactly zero); (2) prefix-invariance HALT on the first handoff in run order, max centered δ ≤
1e-04 — entry 0039's pre-registered absolute
float32 kernel-noise bound, explicitly held identical across families and not derived from τ_K; (3) δ_null,
seeded derangement of sender positions (seed 23); (6) seam profiles b(t) and
b⁻(t), same bins. The cross arm runs through this pair's own k = 1 mapper by sha, and its
outcome is descriptive and decides nothing (0027).

**Gate and enforcement.** `e9 --check --config config/e9f.toml` refuses until entries 0019/0023/0025/0027/0042 are in the
committed ledger, `config/e9f.toml` is committed unmodified, the upstream is at the pin
`06f8d5559257` with every invoked path clean, and the mapper artifact is present by sha.
`summarize_e9 --config config/e9f.toml` (fail-closed, the only reader) re-derives every alignment from the
raw traces under the cap, recomputes every figure, re-scores the kept dumps from tensors, recomputes τ and
refuses on disagreement with this config, checks the controls and the two RoPE controls above, and states
f*, the profiles and the band. **The τ calibration is checked at THIS entry, not only by the summarizer:**
`e9 --check` does not look for `calibration/tau.json`, and on 2026-09-14 a sitting printed ready, ran to
completion and was refused at home for exactly that gap (learnings). The record exists and agrees before
this row is written.

**What this does NOT touch.** The H-E8, H-E9 and H-E9L cells; the Qwen τ values, rule, band, ladder, keep
subsets and results directories; `config/e9.toml`, `config/e9l.toml`, `config/e9s.toml`, `config/e9c.toml`
and every `config/e8*.toml` but this family's. Nothing here is a figure: H-E9F's verdict and every number
enter by their own numbered entry, and the paper only from that entry.

**Scope.** One new pair (meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B), one direction, one agent family, the short half of one
corpus under a natively long receiver; off-policy text for Llama-3 (entry 0039, restated for this cell above); floor not method
(0027); the 36 handoffs above the cap and the 4 with an empty receiver prompt stay
excluded and counted; generation quality after reuse not measured. `eval_hellaswag.py` and
`compose_mapper.py` remain out of scope for this pair (upstream `apply_mapper` re-applies with a plain θ).

prior-entries-sha256: a93cc5ee357122a8b9fa6885c42e7932022fe046c6953da6c7d616781948b25d

### 0043 — 2026-09-19 — Pre-prefill amendment to 0042: the driver's checkpoint write is atomic, and the stop protocol for a budget-limited sitting is registered; descriptive, no cell moves

**What this is.** An amendment to entry 0042, appended **before any prefill of this cell**, on the
0025/0026/0027 precedent: the registered instrument changed after its registering entry, and a change to
the instrument is stated before the run, never explained after it. Nothing here moves a cell, states a
figure, or touches τ, the rule, the band, the ladder, the cap, the keep draw or the run order. Pair
llama3.2-3b-to-llama3.1-8b (meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B), `config/e9f.toml` sha256 `2e7cade40489`, run order and coverage from
`results/e9f/align/coverage.json` sha256 `6a8dc1242300`, both committed and unmodified. At the moment of
writing, `results/e9f/` holds no report, no score file, no token record and no kept dump.

**(a) The checkpoint write is atomic.** Entry 0042 recorded that the driver "gained refusals only".
That is no longer the whole of it: `e9._write_checkpoint` now writes `report.json` to a temporary file,
`fsync`s it, and `os.replace`s it into place, and `e9.close_partial` writes through the same function.
**Nothing computed changes** — the same bytes are produced from the same inputs, and no number, refusal
or control is affected. The reason it changed is (b): the registered stop stops the driver **by signal**,
and a signal that lands during a plain `write_text` leaves a truncated `report.json`. Under the rule
below the closing basis is a checkpoint, so a torn checkpoint does not cost one handoff — it costs the
prefix. The change is recorded here because it is the registered instrument, not because it is large.

**(b) The stop protocol.** This cell runs under a hard dollar ceiling, so how it stops decides which
prefix entry 0042 closes on — and that must be fixed before any score exists, exactly as 0042
fixed the order for the same reason.

1. **A healthy run closes on all 28 included handoffs.** A partial is a registered outcome, never
   the preferred one and never a rescue.
2. **Drain before the ceiling.** The home watchdog stops the **driver** before the spend ceiling
   terminates the **pod**, by `SIGTERM` to the driver's recorded pid (never a self-matching pattern —
   protocol R4). The pod stays up so the home puller can finish the tensors already written. The ceiling
   remains unchanged behind this, as the backstop.
3. **When.** At `70%` of the sitting ceiling by default, or **earlier** if the puller's own
   measurement — bytes still outstanding ÷ the rate it is actually achieving — says the remaining pull
   needs more than the leftover budget. A measurement may only move the drain earlier, never later: the
   outstanding figure counts the kept dumps a checkpoint already names and cannot see the handoff in
   flight, so an uncapped measurement reads "nothing outstanding" at the moment the most is at risk.
4. **The closing basis after ANY abnormal end** — drained, hard-killed, crashed, or a pod lost outright
   — is the **last checkpoint whose every named artifact is sha-verified at home**: the small records and
   the kept directories of the scored prefix, each byte-for-byte against that checkpoint's own
   fingerprints. It is a genuine driver checkpoint and a prefix of the registered `n_sender_asc` order.
   **It is never an edited report.** If no checkpoint verifies whole at home, there is no close, and
   H-E9F stays `unresolved` — that is the finding, not a problem to be worked around.
5. **Where.** The close happens **at home, on the verified mirror**, never on the box: box storage is
   ephemeral, so after a hard kill it is already gone at exactly the moment a close is needed.
   `tools/runpod/pull_verify_b.py --final-partial` refuses unless the driver is provably stopped, proves
   the basis, and writes the termination receipt; `e9 --close-partial --config config/e9f.toml` then
   stamps it and needs nothing but `report.json`.
6. **What the closing entry must carry.** The cutoff reason, the coverage as "n scored of N registered"
   beside every number, and every unscored handoff named by id — as entry 0036 did for the long half.

**(c) The gate, and one regenerated artifact.** `config/e9f.toml`'s `[e9.gate]` now requires
`0019/0023/0025/0027/0042/0043` — entry 0042's list extended by this entry and nothing else — so
`e9 --check` refuses until this amendment is committed on the ledger. Enforcement, not decoration: a
protocol deciding which prefix a stopped run closes on must bind the driver, and 0042 recorded the
gate as it stood then. Adding one entry changed the file's sha256 to `2e7cade40489`, and
`results/e9f/align/coverage.json` and `results/e9f/calibration/tau.json` are recorded under that sha, so
both were regenerated by `e9 --align-only` and `summarize_e9 --calibrate-tau`. **The coverage file
differs in exactly one key, `config_sha256`**: the 28 included handoffs, the `n_sender_asc` run
order, the keep draw, the exclusion counts and every alignment are identical, and τ_K, τ_V and τ_agent_K
are unchanged to every digit. No registered quantity moved; the file now records the sha of the file that
actually governs it. No other config is touched.

**Why this is an amendment and not a note.** Under 0042 the scored set of a stopped run is a prefix of
a registered order, which fixes *which* handoffs a partial keeps. It did not fix *when* the run stops or
*which* checkpoint is then closed on, and both are choices that could otherwise be made with the scores
already visible. Registering them here removes that freedom before there is anything to see.

**What this does NOT touch.** The H-E8, H-E9, H-E9L and H-E9F cells and every verdict; τ_K, τ_V,
τ_agent_K, the rule, the band edges, the ladder, `prefix_invariance_max_delta`, the cap, the seeds, the
keep draw, the run order, the coverage figures themselves; every other cell's config and results. Entry 0039's τ_K ceiling of 0.45 and entry
0041's report-only ordering both stand as written.

**Scope.** One pair (meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B), one cell, one sitting's stopping behaviour. Nothing here is
evidence about KV reuse, and nothing here may be cited as a finding.

prior-entries-sha256: 5112398f506937881144964ba7fbca7316d68165e7aaedccf00974005de7849f

### 0044 — 2026-09-19 — E9 short cell ran on the second model family `[BASELINE]`; H-E9F HELD (28 scored of 28 registered)

**The registered τ_K ceiling does not bite (entry 0039).** τ_K = 0.2861 ≤ 0.45, so the band below is read as the rule writes it. Operator provenance note (non-verdict-bearing): tau_K 0.2861 = 1 MINUS this pair's own k=1 generic held-out K R^2 (0.7139, entry 0040's verified E8 report), recomputed by summarize_e9 --calibrate-tau and agreeing to 1e-9; it sits below entry 0039's 0.45 ceiling, which was registered before the fit. The billed sitting began at pod creation 16:02:36Z, 72 minutes before the driver launch stated above.

**Setup, as registered (0042, amended by 0043).** RunPod SECURE, pod k83m2em0mgp9dx created 2026-09-19T16:02:36Z at $1.59/h under a 5.0 h / $7.95 ceiling (runpod_state.json, receipt e9f-verified.json); NVIDIA A100-SXM4-80GB, 81,920 MiB, driver 580.126.16; torch 2.11.0+cu128 (CUDA 12.8), transformers 5.15.1, numpy 2.5.2, python 3.12.13 — as the box recorded them in sitting_b.evidence/versions.txt at 17:14:36Z; linear-ceiling at the commit carrying 0043 and
`config/e9f.toml` (gate: entries 0019/0023/0025/0027/0042/0043), upstream pin `06f8d55`
(the one-line `PAIRS` entry on top of the RoPE-spec commit). Pair llama3.2-3b-to-llama3.1-8b: receiver meta-llama/Llama-3.1-8B, source
meta-llama/Llama-3.2-3B, **neither scaled** — no `[e9.rope]`, no `[e9.bridge]`, no `--rope-scaling` on any dump; the
k = 1 mapper this family's E8 sitting fitted (entry 0040) for the cross arm, by sha. Launched
2026-09-19T17:14:41Z, finished 2026-09-19T18:18:30Z. 28 scored of 28 registered, in the registered `n_sender_asc` order. Of
68 observed handoffs: 28 included (|S| and |R| both within 32,768 tokens
under this pair's own tokenizer), 36 above the cap, 4
with an empty receiver prompt. Every figure below is `summarize_e9 --config config/e9f.toml`'s, from a run
that passed all of its checks: alignments re-derived from the raw traces under the cap; every R²
recomputed from recorded moments; per-token squares summed against the moments; the 8 kept handoffs' stride-1 dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within 8.8e-04 relative, max |f* diff| 0.0e+00); τ
recomputed from the archived mapper and checked against the config; controls checked.

**The two controls that replace entry 0035's configuration bridge.** This receiver is natively long, so
there is no scaled arm to compare and no bridge to run; what stands in its place is read off the dumps
themselves, from the `RopeSpec` the upstream recorded off each loaded model's own rotary embedding and
halt-checked against the model at every dumped position (worst |diff| 1.2e-07
against atol 1e-05), over all 85 dumps of the run. **(i) Native
window:** the registered cap 32,768 sat inside EVERY dump's own recorded
`max_position_embeddings` — no dump asked either model for a position its configuration does not declare,
which is the positive "no extrapolation happened" statement. **(ii) Frequency identity, scoped by model
role:** source (28 dumps, max_position_embeddings 131,072, inv_freq 31576ad84e5a, attention factor 1.0), target (57 dumps, max_position_embeddings 131,072, inv_freq 8480b7658cd7, attention factor 1.0). The 2 roles are compared separately and MUST be: this pair's two sides carry
different llama3 scaling factors and build different inverse-frequency vectors by construction, so an
unscoped equality assert would refuse every correct run. Every dump recorded an attention factor of 1.0,
the only positive evidence that the box applied no scaling the registration does not describe.

**How the sitting actually ran, for the record.** The card was not the one planned. Creates were repeatedly
refused for stock on the $1.19 A100 80GB PCIe and then the $1.39 A100 SXM, both community: **nine such
refusals are recorded in `~/.cache/linear-ceiling/create-attempts.log`** (15:52:01Z–16:01:59Z), and
earlier by-hand attempts that day are not separately recorded, so no total is stated here. The sitting
ran on a SECURE A100 SXM at $1.59/h with a 5.0 h ceiling — which put entry
0043's drain at 3.5 h and made a registered partial the likelier outcome. It did not occur: the run
finished all 28 in 63.8 minutes, and the drain never armed. Three SETUP attempts failed before the
driver started, none of which touched a scored artefact and all of which are macOS→Linux archive or
tooling defects rather than anything about this pair: a traces archive carrying macOS AppleDouble
members (rebuilt with `COPYFILE_DISABLE=1`, re-verified against the committed manifest); the same
defect in the weight archive (17 GiB by `du`, `freed-bytes.log`), whose own sha256 matched, so the
cache was extracted by hand with `--exclude='._*'` and then verified per object — 6 LFS blobs by
content sha256, 14 git blobs by sha1;
and a false positive in that per-object check from a size-based rather than name-length-based rule.
Two different BLAS thread caps applied, and they are not the same cap: ON THE BOX the driver ran
under a **13**-thread cap that `sitting_b.sh` derived from the container's cgroup CPU quota
(`/sys/fs/cgroup/cpu.max`), whose raw value the run did not record — the box log states only the derived
cap — and never from the host core count, which the same log records as `vcpu: 128` at 17:12:55Z. (That
log line's own parenthetical reads `NOT nproc=13`: the script prints `nproc` a second time AFTER
exporting `OMP_NUM_THREADS=13`, and GNU `nproc` honours that variable, so the 13 there is an artifact of
the cap being reported and not a second measurement of the host. Stated because a reader grepping
`nproc` in the log finds 13 and would otherwise read this entry as wrong.) The box also recorded
`disk: 107G free of 160G`. AT HOME the summarizer ran under an **8**-thread cap. Both matter only through entry 0028's float32 reduction-order tolerance, which the
keep-subset re-score figures above already bound.

**One input was rebuilt, and its bytes differ from the earlier record's.** `results/e7/` was absent on the
summarizing machine (`results/` is gitignored and E7 ran elsewhere), so `summarize_e9` refused until
`skeleton_report.json` was regenerated by its own registered driver from `traces/` verified against the
committed manifest `371fb4bf3cb0`; `summarize_e7`, which recomputes every E7 figure from the raw traces,
then PASSED on it. The regenerated report's sha256 is `27dc922e3f7d…` (recorded in
`results/e9f/summary.json`) and it **DIFFERS** from the `0aba0fbe…` that the 2026-09-10 long-run summary
records in the public dataset `hossainpazooki/linear-ceiling-e9l-2026-09-10`. **The cause is not
established and none is asserted here.** What is established is that the difference is not in the
values: the regenerated rows reproduce that earlier summary's six coverage figures to all 16 digits, and
this file feeds the DESCRIPTIVE coverage comparison alone — no verdict-bearing figure, no control and no
τ reads it (`summarize_e9` takes only `headroom.rows` from it). Nothing under `results/e9f/` was
touched.

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run
order: max centered per-token δ 0.000e+00 over 7,435 positions
(tolerance 1e-04 — entry 0039's registered ABSOLUTE literal, deliberately
IDENTICAL to `config/e9.toml`'s by the operator's 2026-09-18 ruling, and never a function of τ_K: it is a
float32 kernel-noise floor, a property of the arithmetic rather than of how well a mapper fitted). δ_null same K / V token-mean median 2.004 /
2.015; equal-token null pairs 0.0083.
Matched fraction |M|/|R| (a floor): 0.9304 (p10 0.8794, p90 0.9788).

**The rule (0023, carried verbatim by 0043) and the figure it reads.** Per scored handoff, E9-same, K
read-out: f*(τ_K) = the fraction of matched tokens an oracle must recompute before the mean centered
deviation of the rest is at or below τ_K = 0.2861; median over scored handoffs; HOLDS ≤
0.15, DEGRADES ≥ 0.5, UNRESOLVED between. τ_K is 1 − THIS pair's own
held-out R² (0.7139 over
2,560 tokens), recomputed here and refused on disagreement.

- **median f*(τ_K), E9-same K: 0.0000 (p10 0.0000, p90 0.0000)** over 28 handoffs (28 scored of 28 registered). Seeded
  bootstrap of the median (seed 25, 2000 reps; reported, not read):
  [0.0000, 0.0000].
- f*(τ_V = 0.5289), E9-same V (alongside): 0.0000 (p10 0.0000, p90 0.0000).
- τ ladder (descriptive): τ = 0.1: same K 0.0000 (p10 0.0000, p90 0.2505) / V 0.0000 (p10 0.0000, p90 0.2942); τ = 0.03: same K 0.1078 (p10 0.0010, p90 0.4536) / V 0.1491 (p10 0.0094, p90 0.5047).
- f*(τ_agent_K = 0.2689) (alongside): same K 0.0000 (p10 0.0000, p90 0.0000); cross K 0.8040 (p10 0.6888, p90 0.8925).
- f*(τ_K) over matched blocks of length ≥ 4: same K 0.0000 (p10 0.0000, p90 0.0000).
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: 0: 0.223 (n=2502) · 1: 0.107 (n=1777) · 2-3: 0.065 (n=2853) · 4-7: 0.051 (n=4467) · 8-15: 0.053 (n=6030) · 16+: 0.010 (n=151808).

**Band outcome, against the rule as written: HOLDS** — on this pair's 28 scored
handoffs, **never pooled with entry 0029's**: the same numeric cap over a different tokenizer selects a
different set of handoffs, and the two cells are compared in prose or not at all.
f* = 0 on a handoff means its MEAN centered deviation over matched tokens is ALREADY at or below τ_K
with nothing recomputed. It is entry 0023's mean-repair statistic and is **NOT** a statement that no
single token exceeds τ_K — entry 0038 draws that distinction explicitly, and the identical sentence in
entries 0029 and 0036 claimed otherwise; it is not repeated here. The fraction of tokens individually
above τ_K is not computed by this summarizer and no figure for it is stated. How far inside the
tolerance this cell sits is what the τ ladder and the seam profile above show.

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction
(oracle selection, recompute in isolation); this cell reads "no more than the mapper, on a floor", never
that an achievable scheme reaches it.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through this pair's own
k = 1 mapper: median f*(τ_K) = 0.7317 (p10 0.6074, p90 0.8516) and f*(τ_V) = 0.8148 (p10 0.7407, p90 0.8977); against
the same edges the transfer arm sits beyond the DEGRADES edge. Cross/same median-δ ratio K / V: 30.0 (p10 3.8, p90 65.4) /
42.0 (p10 5.2, p90 122.0). Bridge R² (A5 across the handoff; decides nothing): same K 0.9199 (p10 0.7812, p90 0.9685), same V
0.9020 (p10 0.7478, p90 0.9608), cross K 0.5848 (p10 0.5124, p90 0.6142), cross V 0.2657 (p10 0.2264, p90 0.2948).

**What this establishes, stated narrowly.** On meta-llama/Llama-3.1-8B re-rendering 28 real SWE-bench
`composio_swekit` handoffs whose sender and receiver prompts both fit 32,768 tokens under this
pair's own tokenizer, with 0019's alignment and 0023's per-token rule and τ calibrated on THIS pair's
k = 1 mapper, the same-model oracle recompute floor is as stated above. **Not established:**
anything about the 36 handoffs above the cap or the
4 with an empty receiver prompt; any achievable recompute scheme; anything
about the Qwen cells, which are a different pair and are unchanged; one pair, one direction, one mapper,
one alignment method; generation quality after reuse. `eval_hellaswag.py` and `compose_mapper.py` remain
out of scope for this pair (entry 0039).

verdict: H-E9F = HELD
e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 53b14a5e89f3a829a115ca9e233a3b52440e8ff1711e45ecda11126a6901bcca

### 0045 — 2026-10-01 — Corrective: f* = 0 is a statement about the MEAN within τ_K, not "no token over τ_K"; the per-token tail counted per cell with the per-handoff maximum; the 0025/0029 R² label; summary-file figures entered — descriptive, no cell moves

**What this entry corrects, and what it does not.** Entry 0029 (line 1788) and entry 0036 (line 2209) state
their HOLDS reading as "not one … handoff has a single matched token whose centered deviation exceeds τ_K".
Entry 0023 (line 1275) defines f*(τ) as the smallest fraction of matched tokens whose exact recompute brings the
MEAN δ_K of the rest to τ; f* = 0 therefore says every included handoff's mean is already at or under τ_K, and
says nothing about individual tokens. Entries 0038 (line 2342) and 0044 (line 2962) already draw that
distinction; 0044 adds that the fraction of tokens individually above τ_K was not computed by its summarizer —
it now is, by `e9_tail`, which runs `summarize_e9` first and refuses on anything it refuses. Registered headings
and bodies are immutable under the entry chain, so the two sentences stand and this entry records what the
per-token records say beside them. **No verdict moves**: H-E9, H-E9L and H-E9F keep their cells; the statistic,
the bands and every τ are untouched. Unit (0023, line 1253): δ is a token's share of the layer-head's
unexplained variance in R²'s units, its mean over tokens is exactly 1 − R², and it is not a per-token percent
error. Every statistic below is named mean or median; the two differ on these records.

**(1) The tail, per cell, from `e9_tail` (`results/<cell>/tail.json`, pinned to the `summary.json` and
`report.json` it was computed beside).**

**e9l (entry 0036; 35 scored handoffs; τ_K = 0.3186, counted at the registered 0.3186442653116294).** Of 387,508
matched tokens, **30,701 (7.9%) exceed τ_K individually**, on every one of the 35 handoffs (per-handoff fraction
over τ_K: median 0.0577 (p10 0.0207, p90 0.1776; n = 35), max 34.1%). Pooled per-token δ_K: mean 0.1165, median
0.0647, p90 0.2856, p99 0.7600, max 2.6700. Per-handoff MEAN δ_K: median 0.1106 (p10 0.0489, p90 0.2023; n =
35); **maximum 0.2692**, which sits 0.04947 under τ_K — so f* = 0 "on every handoff" means every handoff's mean
is at or under τ_K (0 of 35 over it), not that no token is. Mean after removing the top 10 % / 20 % of tokens by
δ_K: 0.0773 / 0.0586 (CacheBlend's selection rule in this paper's units; their figure is in other units under
another rule and is not compared). Pooled δ_K by causal seam bin b⁻(t), MEAN and MEDIAN both stated because they
differ by up to 1.76× here: 0: mean 0.428 / median 0.260 (n = 4,050) · 1: mean 0.244 / median 0.153 (n = 2,956)
· 2-3: mean 0.155 / median 0.089 (n = 4,624) · 4-7: mean 0.127 / median 0.074 (n = 7,224) · 8-15: mean 0.143 /
median 0.086 (n = 9,451) · 16+: mean 0.110 / median 0.063 (n = 359,203). By sender position: 0-32767: mean 0.093
/ median 0.038 (n = 284,094) · 32768-49151: mean 0.185 / median 0.131 (n = 40,967) · 49152-65535: mean 0.207 /
median 0.162 (n = 43,643) · 65536-81919: mean 0.118 / median 0.092 (n = 18,804). Native window (sender position
< 32,768): 284,094 tokens, 73.3% of matched, mean 0.0926, median 0.0381. |R| over the scored handoffs: median
11,462 (p10 7,085, p90 19,853; n = 35). Summary-file figures (`summary.json` keys): |S| of the included handoffs
`coverage_comparison.included.n_sender` median 50,916 (p10 35,692, p90 66,991; n = 35) (not previously on the
ledger for this cell); `own_norm_delta_gt_1_fraction` K median 0.0000 (p10 0.0000, p90 0.0000; n = 35), V median
0.0033 (p10 0.0020, p90 0.0070; n = 35) (not previously on the ledger for this cell);
`depth_profile_median_per_layer.same_K`, median δ_K by layer 0…27: 0.000, 0.010, 0.013, 0.028, 0.023, 0.046,
0.044, 0.053, 0.074, 0.076, 0.072, 0.070, 0.083, 0.085, 0.100, 0.099, 0.083, 0.089, 0.072, 0.068, 0.067, 0.062,
0.053, 0.044, 0.042, 0.042, 0.044, 0.047 (the V and cross arms are in the file, not restated). The configuration
bridge's per-handoff R² (entry 0035 control 4; `summary.json` key `bridge.per_handoff[].r2_K/r2_V`, not
previously on the ledger; the bridge's f* and median δ are in 0036): `django__django-10999_traj#64` (|S| 13,955)
K 0.8992 / V 0.8682 · `django__django-11066_traj#36` (|S| 14,269) K 0.8821 / V 0.8489 ·
`astropy__astropy-14182_traj#68` (|S| 17,935) K 0.8932 / V 0.8603. Pinned: `tail.json` → `report.json`
084d9480af74, `summary.json` 64e64e9318d4.

**e9 (entry 0029; 25 scored handoffs; τ_K = 0.3186, counted at the registered 0.3186442653116294).** **Condition
1 (entry 0032) binds this cell: these figures correct a sentence already on the ledger and release nothing; no
pooled row with any other cell; nothing enters a paper until the co-author refutation is merged under
`docs/reviews/` with two signatures. (The 2026-09-08 numbers-freeze clause of 0032 applied to the LCFM
submission, since accepted; the operator ruled it moot on 2026-10-01 for the camera-ready. The review's
substance is what remains.)** Of 155,257 matched tokens, **9,047 (5.8%) exceed τ_K individually**, on every one
of the 25 handoffs (per-handoff fraction over τ_K: median 0.0437 (p10 0.0192, p90 0.1418; n = 25), max 28.3%).
Pooled per-token δ_K: mean 0.0810, median 0.0233, p90 0.2305, p99 0.6736, max 2.2738. Per-handoff MEAN δ_K:
median 0.0682 (p10 0.0384, p90 0.1570; n = 25); **maximum 0.2207**, which sits 0.09790 under τ_K — so f* = 0 "on
every handoff" means every handoff's mean is at or under τ_K (0 of 25 over it), not that no token is. Mean after
removing the top 10 % / 20 % of tokens by δ_K: 0.0435 / 0.0283 (CacheBlend's selection rule in this paper's
units; their figure is in other units under another rule and is not compared). Pooled δ_K by causal seam bin
b⁻(t), MEAN and MEDIAN both stated because they differ by up to 3.63× here: 0: mean 0.409 / median 0.236 (n =
2,278) · 1: mean 0.209 / median 0.127 (n = 1,599) · 2-3: mean 0.129 / median 0.081 (n = 2,571) · 4-7: mean 0.110
/ median 0.062 (n = 4,039) · 8-15: mean 0.121 / median 0.063 (n = 5,480) · 16+: mean 0.071 / median 0.019 (n =
139,290). By sender position: 0-32767: mean 0.081 / median 0.023 (n = 155,257). Native window (sender position <
32,768): 155,257 tokens, 100.0% of matched, mean 0.0810, median 0.0233. |R| over the scored handoffs: median
6,551 (p10 4,148, p90 9,165; n = 25). Summary-file figures (`summary.json` keys): |S| of the included handoffs
`coverage_comparison.included.n_sender` median 25,460 (p10 14,269, p90 30,106; n = 25) (already stated by 0029);
`own_norm_delta_gt_1_fraction` K median 0.0000 (p10 0.0000, p90 0.0000; n = 25), V median 0.0043 (p10 0.0028,
p90 0.0066; n = 25) (already stated by 0029); `depth_profile_median_per_layer.same_K`, median δ_K by layer 0…27:
0.000, 0.001, 0.003, 0.006, 0.005, 0.007, 0.007, 0.010, 0.012, 0.019, 0.018, 0.022, 0.031, 0.036, 0.042, 0.044,
0.039, 0.044, 0.034, 0.033, 0.034, 0.032, 0.026, 0.024, 0.022, 0.023, 0.024, 0.019 (the V and cross arms are in
the file, not restated). Pinned: `tail.json` → `report.json` 1b2153e31245, `summary.json` ae461db872f2.

**e9s (entry 0038; 25 scored handoffs; τ_K = 0.3186, counted at the registered 0.3186442653116294).**
**Condition 1 (entry 0032) binds this cell: these figures correct a sentence already on the ledger and release
nothing; no pooled row with any other cell; nothing enters a paper until the co-author refutation is merged
under `docs/reviews/` with two signatures. (The 2026-09-08 numbers-freeze clause of 0032 applied to the LCFM
submission, since accepted; the operator ruled it moot on 2026-10-01 for the camera-ready. The review's
substance is what remains.)** Of 155,257 matched tokens, **10,336 (6.7%) exceed τ_K individually**, on every one
of the 25 handoffs (per-handoff fraction over τ_K: median 0.0527 (p10 0.0252, p90 0.1677; n = 25), max 26.1%).
Pooled per-token δ_K: mean 0.0986, median 0.0414, p90 0.2524, p99 0.7330, max 2.3712. Per-handoff MEAN δ_K:
median 0.0895 (p10 0.0537, p90 0.1734; n = 25); **maximum 0.2255**, which sits 0.09312 under τ_K — so f* = 0 "on
every handoff" means every handoff's mean is at or under τ_K (0 of 25 over it), not that no token is. Mean after
removing the top 10 % / 20 % of tokens by δ_K: 0.0600 / 0.0438 (CacheBlend's selection rule in this paper's
units; their figure is in other units under another rule and is not compared). Pooled δ_K by causal seam bin
b⁻(t), MEAN and MEDIAN both stated because they differ by up to 2.34× here: 0: mean 0.428 / median 0.265 (n =
2,278) · 1: mean 0.224 / median 0.145 (n = 1,599) · 2-3: mean 0.143 / median 0.093 (n = 2,571) · 4-7: mean 0.117
/ median 0.071 (n = 4,039) · 8-15: mean 0.135 / median 0.075 (n = 5,480) · 16+: mean 0.089 / median 0.038 (n =
139,290). By sender position: 0-32767: mean 0.099 / median 0.041 (n = 155,257). Native window (sender position <
32,768): 155,257 tokens, 100.0% of matched, mean 0.0986, median 0.0414. |R| over the scored handoffs: median
6,551 (p10 4,148, p90 9,165; n = 25). Summary-file figures (`summary.json` keys): |S| of the included handoffs
`coverage_comparison.included.n_sender` median 25,460 (p10 14,269, p90 30,106; n = 25) (not previously on the
ledger for this cell); `own_norm_delta_gt_1_fraction` K median 0.0000 (p10 0.0000, p90 0.0000; n = 25), V median
0.0047 (p10 0.0030, p90 0.0068; n = 25) (not previously on the ledger for this cell);
`depth_profile_median_per_layer.same_K`, median δ_K by layer 0…27: 0.000, 0.005, 0.007, 0.011, 0.010, 0.014,
0.018, 0.022, 0.054, 0.052, 0.050, 0.046, 0.060, 0.061, 0.074, 0.076, 0.063, 0.067, 0.052, 0.048, 0.049, 0.045,
0.038, 0.033, 0.031, 0.031, 0.033, 0.036 (the V and cross arms are in the file, not restated). Pinned:
`tail.json` → `report.json` abd1e4561966, `summary.json` 859a8c98e1cd.

**e9f (entry 0044; 28 scored handoffs; τ_K = 0.2861, counted at the registered 0.28613264291767326).** Second
model family (0039), its own τ; never pooled with the Qwen3 cells (0044). Of 169,437 matched tokens, **19,094
(11.3%) exceed τ_K individually**, on every one of the 28 handoffs (per-handoff fraction over τ_K: median 0.0719
(p10 0.0247, p90 0.3442; n = 28), max 42.4%). Pooled per-token δ_K: mean 0.0960, median 0.0137, p90 0.3180, p99
0.9373, max 2.5707. Per-handoff MEAN δ_K: median 0.0801 (p10 0.0315, p90 0.2188; n = 28); **maximum 0.2860**,
which sits 0.00008 under τ_K — so f* = 0 "on every handoff" means every handoff's mean is at or under τ_K (0 of
28 over it), not that no token is. Mean after removing the top 10 % / 20 % of tokens by δ_K: 0.0426 / 0.0219
(CacheBlend's selection rule in this paper's units; their figure is in other units under another rule and is not
compared). Pooled δ_K by causal seam bin b⁻(t), MEAN and MEDIAN both stated because they differ by up to 8.59×
here: 0: mean 0.387 / median 0.223 (n = 2,502) · 1: mean 0.208 / median 0.107 (n = 1,777) · 2-3: mean 0.122 /
median 0.065 (n = 2,853) · 4-7: mean 0.109 / median 0.051 (n = 4,467) · 8-15: mean 0.138 / median 0.053 (n =
6,030) · 16+: mean 0.087 / median 0.010 (n = 151,808). By sender position: 0-32767: mean 0.096 / median 0.014 (n
= 169,437). Native window (sender position < 32,768): 169,437 tokens, 100.0% of matched, mean 0.0960, median
0.0137. |R| over the scored handoffs: median 6,852 (p10 3,945, p90 8,843; n = 28). Summary-file figures
(`summary.json` keys): |S| of the included handoffs `coverage_comparison.included.n_sender` median 24,707 (p10
13,465, p90 32,039; n = 28) (not previously on the ledger for this cell); `own_norm_delta_gt_1_fraction` K
median 0.0004 (p10 0.0003, p90 0.0007; n = 28), V median 0.0071 (p10 0.0028, p90 0.0155; n = 28) (not previously
on the ledger for this cell); `depth_profile_median_per_layer.same_K`, median δ_K by layer 0…31: 0.000, 0.001,
0.001, 0.003, 0.003, 0.004, 0.006, 0.008, 0.011, 0.017, 0.014, 0.016, 0.016, 0.027, 0.023, 0.021, 0.018, 0.019,
0.016, 0.014, 0.014, 0.014, 0.014, 0.014, 0.015, 0.014, 0.014, 0.014, 0.013, 0.015, 0.015, 0.016 (the V and
cross arms are in the file, not restated). Pinned: `tail.json` → `report.json` f9335c0587ad, `summary.json`
e1e5feb8aadd.

**(2) The R² label in 0025 and 0029.** Entry 0025 (line 1471) writes "AGENT text at K R² = 0.4371" and entry
0029 (line 1801) "mapper on agent text (K R² 0.4371)". 0.4371 is 1 − R², the shortfall that 0025 registers as
τ_agent_K; the R² is **0.5629**, entry 0020's arm (b) K at the verdict k = 1 (line 1114), restated by 0030 as "1
− 0.5629 = 0.4371" (line 1854). τ_agent_K and every figure computed from it are unchanged; only the label in the
two sentences is wrong (review record `docs/2026-09-20-astra_review.md`, R1-4).

**(3) What this changes downstream.** The seam-concentration reading ("deviation is local to the seam") rests on
the bin MEANS above, not on the medians the earlier entries printed; any restatement of the workshop paper's
per-token bound on these records uses the means and says so. Bridge R² (A5; decides nothing) is already stated
by each cell's own entry and is not restated here. Nothing here is a new experiment; the `[STRETCH]`
partial-prefill run and the designs under `docs/drafts/` remain unregistered.

**(4) Entry 0044's E7 report hash.** 0044 (line 2923) records the E7 report regenerated on the box as
`27dc922e3f7d…`, differing from the `0aba0fbe…` the 2026-09-10 long-run summary recorded, cause not asserted.
The home-mirror recomputation pinned here (`summary.json` e1e5feb8aadd, key
`coverage_comparison.e7_report_sha256`) gives `0aba0fbe7aba…`; the clean-clone recomputation record
`docs/reviews/2026-09-28-llama-cell-r8-backup-and-recomputation.md` reports the same value (cited, not
recomputed by this script). The box value is the outlier. The cause is still not established and none is
asserted; the file feeds only the descriptive coverage comparison, as 0044 states.

prior-entries-sha256: 4ce8765046ea6b8fdefcdd4b81e747ed774970296b729431f36db495d3535c74

### 0046 — 2026-10-04 — Same-model extension registered before any operator prefill: the E9 instrument on the original 60 handoff texts replayed through Qwen3-4B and SmolLM3-3B, with a six-case Qwen3-1.7B bridge; a co-author's prior fork run recorded as the pilot; descriptive, no cell moves

**Why, and why now.** Reviewer weakness W7 (`docs/2026-09-30-review-response-map.md`): one model pair. The second
family (0039–0044) answers it at one more pair. This entry registers the cheapest further answer the instrument
allows: the SAME 60 handoff texts that decided H-E9L and the scaled short cell (entries 0036 and 0038; 35 long,
25 short) replayed through two more receivers on the same-model arm only, at the registered Qwen reference τ. It
asks whether the zero floor is a property of one small Qwen pair. It does not ask about cross-model reuse, length
(the cohorts are different handoffs), or quality. **No hypothesis row is added and no verdict is read**: a new
model's mean deviation against another model's mapper tolerance is a descriptive comparison, stated as such.

**What is registered, by hash.** `config/consolidation.toml` (`857cc92320cb…`): models and revisions
`Qwen/Qwen3-1.7B@70d244cc86cc` (bridge, 6 handoffs: shortest, middle and
longest sender of each cohort), `Qwen/Qwen3-4B@1cfa9a720891` (60), `HuggingFaceTB/SmolLM3-3B@a07cc9a04f16`
(60); fp32, SDPA, 256-token chunked prefill with the full causal KV history, cap 81,920; YaRN factor
2.5 on the Qwen models and 2.0 on SmolLM3 (its rotary-free layers unchanged); τ_K = 0.3186442653116294 and τ_V = 0.4867056499055992,
**the 0023 Qwen3-0.6B→1.7B mapper's held-out shortfall, used as a common numerical reference and NOT a calibrated
threshold for either new model**; ladder [0.03, 0.1]; seed 20260930. `config/consolidation-manifest.json`
(`99185c5891fc…`) pins every input byte: the 60 texts re-tokenized per model (max sender 80,111 / 74,233 tokens, no exclusion),
each text's sha256 equal to the archived alignment's `text_sha256` (checked here against `results/e9l/align` and
`results/e9s/align`), and exact ordered token matching by `e9_align.matching_pairs`. Keys are captured after any key
normalization and before rotation, values after projection; no fp16 serialization.

**Controls and bridge, fixed now.** (1) Per model, before any handoff: a 1,024-token full prefill against the chunked
prefill of the same prefix plus one later token; maximum normalized token deviation ≤ 0.0001 or the run refuses.
(2) The bridge: the original receiver re-run on six archived handoffs; relative mean-deviation gap ≤ 0.01 and
absolute f* gap ≤ 0.01 against the archived records at every τ, or expansion to the new models stops.
(3) The longest sender runs first as the memory probe and is retained. (4) One raw matched-vector witness per model
(the shortest included sender) is kept for independent re-scoring; other vectors are transient and removed only after
their compact record and atomic checkpoint exist. (5) Resume refuses changed code, runtime, device, dtype or inputs,
and refuses a `complete` flag with missing handoffs. Readout per handoff and arm: per-token δ (0023's unit: a token's
share of the layer-head's unexplained variance; mean = 1 − R²), its mean, maximum, tail fraction over τ, f*(τ) at τ_K and
the ladder, all by `e9_pertoken.centered_delta` / `token_mean` / `f_star`.

**Instrument, as committed:** `tools/consolidation/run.py` `87e0efb1502c…`, `capture.py` `2cddd19b1c43…`,
`prepare.py` `172b1ff66e37…`, `summarize.py` `d9f65ef1333c…` (the fail-closed reader: bundle hashes, report-to-config and
report-to-manifest pins, every record and witness re-hashed, token deltas recomputed, the mean/R² identity, witnesses
re-scored from raw tensors, a seeded trajectory-cluster bootstrap with `e7_stats` quantiles), `setup.sh`, the Linux lock,
and the runbook `docs/2026-09-30-consolidation-runbook.md`. The committed driver differs from the pilot's by the
resume-identity and cohort checks and comments; its arithmetic is the same functions.

**The pilot, recorded and not credited with a figure.** The co-author who designed this (PRs #8, #9) ran it on a fork:
registration commit `3cb4bb3` (2026-10-01T02:41:37Z, the fork's own ledger), results commit
`2fb4464` (2026-10-01T05:28:11Z); the fork's entry says one A100-SXM4-80GB, FP32 prefill, all 60 texts per model scored
without exclusion, bridge gaps within tolerance; the environment it pins is `requirements-linux.lock` (torch 2.14.0,
transformers 5.17.0, numpy 2.5.3, CUDA runtime 13.0.96); the exact runtime, GPU name and `code_sha256` are in its
unpublished reports; driver at the registration commit `run.py` `f544ae874085…`, `capture.py` `b713473055aa…`
(re-hashed from the fork by the operator's session, 2026-10-04). **Upstream R1 was not met by that run**: the card was
provisioned before the fork registration and no upstream entry existed. Its evidence (compact records, one witness
per model, logs) is on the co-author's machine and not on the Hub (R8 not met). Therefore **no figure from the pilot is
stated here or in any paper**; if its bundle is published and recomputed under `docs/2026-10-03-co-author-run-admission.md`,
that is a separate, later entry, and the pilot's agreement with the run registered here becomes a cross-platform
control in the sense of 0028.

**The registered run (the operator's).** Requested only after this entry is committed. Card: an L40S 48 GB is the
expectation (fp32 weights ≈ 16 GB for the 4B, full-cap KV < 3 GB), confirmed by the protocol's probe before any paid
forward; a larger card if the probe says so. R2–R8 of `docs/gpu-experiment-protocol.md` apply: fresh output tree,
detached launch, log rotation, pull → verify → delete per handoff, release checklist, mirror at `results/consolidation/` laid out as
`summarize.py` reads it (`provenance/`, `a100/inputs/`, `a100/results/<model>/`, `archive/records/{e9s,e9l}`, `SHA256SUMS`;
the `a100/` directory name is the reader's and does not assert the card), backup to a Hub dataset (public or private,
operator ruling 2026-10-04) verified by `tools/hf_verify_backup.py` before the figures entry.

**Gate and enforcement.** The driver asserts the config and manifest hashes at start and every input's hash; this
script refuses if either file differs from the frozen bytes or if any report exists under `results/consolidation` (R1). The figures
enter by `append_0048.py`, which runs `summarize.py` in-process over the verified mirror, asserts the reports' `code_sha256`
equal the committed driver files, and refuses on any disagreement; no figure is typed.

**What this does NOT touch.** H-E9, H-E9L, H-E9F and every cell; τ, the rule, the bands, the ladder; entries 0029,
0036, 0038, 0044 and their records; `config/e9*.toml`; the Llama long drafts (now 0050 / 0051). Nothing here is pooled with
any Qwen3-0.6B→1.7B figure: the new models are reported separately, beside the original, never in one statistic.

**Scope.** Same-model arm only; one corpus; the original 60 texts, so the long/short difference is a difference of
handoffs and configuration, not an isolated length effect (W2 is E-TRUNC's); τ is one map's shortfall; nothing about
generation quality, serving speed, or cross-model transfer is measured. Hardware replicas are never handoffs.

prior-entries-sha256: fe0aff7467ff0a1f7675f37ce047d1a5c0e6dea1320d7e2b39134b24307e8a0b

### 0047 — 2026-10-04 — Cache-behavior comparison registered before any operator prefill: next-token sensitivity of the receiver to reading an assembled same-model cache on the 35 long handoffs, fresh vs reused with two perturbation controls; a co-author's prior fork run recorded as the pilot; descriptive, no band, no cell moves

**Why, and why now.** Reviewer weakness W1 (`docs/2026-09-30-review-response-map.md`): the tolerance τ_K is a weak
linear map's error and is not validated against anything the receiver does. Entry 0023's `[STRETCH]` proposal named
the experiment that would answer it: actually read the reused cache. This entry registers its core, as revised in
`docs/drafts/e-beh-design.md` (2026-10-01 update): FRESH against REUSE-ALL on the 35 handoffs of entry 0036, teacher-forced
on the recorded continuation. It measures **prediction sensitivity on fixed text**, not coding-task quality, not free
generation, not speed. The standing sentence "No downstream task-quality number is claimed" is **not** retired by this
entry or by its figures.

**What is registered, by hash.** `config/cache-behavior.toml` (`53c664556d18…`): receiver `Qwen/Qwen3-1.7B@70d244cc86cc`,
Transformers 5.17.0, PyTorch 2.14.0, fp32, SDPA, the long cell's YaRN schedule (yarn factor 2.5, original
32,768), cap 81,920, 256-token prefill chunks; seed 20261001; τ_K = 0.3186442653116294 used only to name the archived
high-error tail. Driver `tools/cache_behavior/core.py` `f346b5fdf3d3…` and `run.py` `15e1ff8c1dbc…`, byte-identical to the
pilot's execution commit; freeze record `docs/2026-10-01-cache-behavior-freeze.json`; runbook `docs/2026-10-01-cache-behavior-runbook.md`;
tests `tests/test_cache_behavior.py`. Inputs: the 35 handoffs of 0036 in its archived order, their archived alignment
pairs as the matched set M (one-token matches included; no new alignment), the recorded receiver response as the
continuation C capped at 256 tokens including the unscored conditioning token C[0]; a handoff with fewer than two
continuation tokens is excluded and counted. The prepared input manifest the pilot froze hashes `9a6f2923d3be…`;
the operator's `--prepare` must reproduce it byte-for-byte from the verified e9l mirror and the manifest-pinned traces,
or the run refuses.

**Arms.** FRESH: the receiver's own prefill of R. REUSE-ALL: the receiver's KV from a prefill of S copied at p_S for
every token of M, keys relocated to p_R under the same fixed schedule and amplitude (amplitude applied once; a schedule
mismatch is refused), values unrotated; the unmatched tokens computed in receiver order against the cache assembled so
far, so later gaps and the continuation can depend on earlier reused states. Controls: RANDOM, a perturbation of the
fresh states with K and V norms matched to the reuse perturbation separately per token, layer and KV head (seeded via
`make_rng`); CYCLIC, the matched source states permuted across M with keys relocated (norms not matched). No
oracle-ranked or CacheBlend-style repair arm (`oracle_fractions = []`). All arms score the same C[1:] under the same
teacher-forced history.

**Numerical controls, fixed now; a failure stops expansion and is never relaxed after the fact.** Fresh repeat: a
second FRESH pass must reproduce the first's logits exactly. Prefix copy over 128 tokens: maximum logit error ≤ 0.0005.
Archive bridge: the current runtime's same-model centered K/V mean deviation per handoff within 0.001 + 0.01 × |archived|
of the 0036 record. TF32 off, deterministic algorithms, `CUBLAS_WORKSPACE_CONFIG=:4096:8`. The largest sender is scored
first as the retained memory probe. Stopping rule: stop on any failed control, bridge, hash or OOM; keep the completed
prefix; resume only with unchanged code, inputs, config and runtime.

**Readout, fixed now.** Per scored token: KL(p_FRESH ‖ p_ARM) over the vocabulary and top-1 agreement. Per handoff: mean
KL, p90 KL, top-1 agreement rate, scored |C|. Over the 35: median with p10 / p90 by `e7_stats` (no interpolation),
handoffs weighted equally; a handoff is one unit and hardware replicas are never handoffs. Beside it, descriptive and
bounded: at the last 32 receiver query positions, the fresh pass's attention (reconstructed from the SDPA forward's
queries and cached keys, GQA mapping kept, no full attention matrix retained) gives the attention mass on M, the mass on
the archived tail (tokens whose token-average δ_K exceeds τ_K, the set 0045 counts), and the attention-weighted archived
δ_K with its conditional value where mass is positive. This is a slice of E-TAIL Part B, not the all-query experiment,
and establishes no mechanism. **No band is registered**: the first run is descriptive; a later entry may register one
only against a quality measurement that does not exist yet.

**The pilot, recorded and not credited with a figure.** The co-author who designed this (PRs #13, #14) ran it on a fork:
execution commit `9a18ce7` (authored 2026-10-01T23:07:08Z, committed 2026-10-01T23:40:23Z; tag `archive/cache-behavior-h100-2026-10-01`), freeze
record written 2026-10-01T23:40:22Z,
one NVIDIA H100 PCIe 80 GB, PyTorch 2.14.0+cu130, Transformers 5.17.0, CUDA 13.0; 35 of 35 handoffs, 8,908 scored continuation tokens,
peak allocation 24.95 GiB with allocator retries. **Upstream R1 was not met by that run**: the card preceded the freeze,
which the freeze record says itself, and no upstream entry existed. Its evidence (report, 35 case records, summary,
inputs, logs) is on the co-author's machine and not on the Hub. **No figure from it is stated here or in any paper**; if
its bundle is published and recomputed under `docs/2026-10-03-co-author-run-admission.md`, that is a separate, later
entry, and its agreement with the run registered here is a cross-platform control.

**The registered run (the operator's).** Requested only after this entry is committed. Card: 80 GB preferred; the
pilot's 24.95 GiB peak with retries does not establish a smaller fit, so a 48 GB card needs the protocol's probe of the
largest case first. R2–R8 apply; output tree `results/cache-behavior/` (`report.json`, per-case `.npz`, `summary.json`, `inputs/`),
mirrored home, verified, and backed up to a Hub dataset (public or private, operator ruling 2026-10-04) by
`tools/hf_verify_backup.py` before the figures entry.

**Gate and enforcement.** The driver asserts the config hash and every input's hash and records the source hashes,
runtime and GPU in `report.json`; this script refuses if any frozen file differs or if `results/cache-behavior` holds a run (R1). The
figures enter by `append_0049.py`, which calls `tools.cache_behavior.run.summarize` in-process over the operator's
verified output, asserts the report's source hashes equal the committed driver, and refuses on any disagreement.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, 0036, 0038, 0044, 0045 and their
records; `config/e9*.toml`; the Qwen3 short cells, which stay Condition-1-bound and are not run here; the Llama drafts
(0050 / 0051). The registered E9 drivers and `summarize_e9` are unchanged.

**Scope.** One receiver, one corpus, 35 handoffs of 34,974–80,111 sender tokens read by receiver prompts of
3,433–25,073 tokens; fixed proprietary-model text, so KL and top-1 are not task outcomes; same-model only; no repair
arm, so nothing here bounds practical repair cost; fresh attention at 32 query positions is an association, not a cause.

prior-entries-sha256: 1d842dbf1b12d10181bd689cd4cb74371aac1300cd127d0f6a10551c4acef00a

### 0054 — 2026-10-04 — Condition 1 discharged by operator ruling: issue #7 and PR #12's review records stand as the co-author confirmation; the two-signature clause of 0032 / 0045 no longer gates the paper; descriptive, no cell moves

**What Condition 1 said.** Entry 0032 (lines 1948–1951) admitted E9 to the LCFM paper on a condition carried forward:
the co-author refutation of entries 0025–0029 (two leads: τ-ladder sensitivity; the exactly-zero prefix control)
recorded before the submission's numbers froze. Entry 0045 (lines 3062–3064) restated what remained after the
2026-10-01 ruling that the numbers-freeze was moot for the camera-ready: "nothing enters a paper until the co-author
refutation is merged under `docs/reviews/` with two signatures." Issue #7 (opened 2026-10-02) widened the review's
scope to the cells the camera-ready prints (0036, 0038, 0045's tail) and named the two approvers.

**The ruling (operator, 2026-10-04).** Issue #7 together with PR #12 — `docs/reviews/2026-10-01-cache-refutation-0025-0029.md`
and `docs/reviews/2026-10-01-feedback-and-claims.md` at PR head `8100414` — is treated as the Condition 1 confirmation.
The two-signature clause is discharged by this ruling rather than by two approvals on the review file. Recorded the same
day on the issue (https://github.com/hossainpazooki/linear-ceiling/issues/7#issuecomment-5977785608) and on the PR (https://github.com/hossainpazooki/linear-ceiling/pull/12#issuecomment-5977785713); this entry is the ledger's record of it.

**What the basis is, stated as the review states it.** The refutation record covers issue #7's rows R1, R3, R4
(ladder sensitivity and the token claim: the three Qwen exceedance counts reproduced) and R9, R10 (prefix-control source
inspection), against repository revision `39b13b4`, with its own status line "evidence checked; proposed co-author
review and signatures pending" and an empty signature table. It lists as not covered: R2 (calibration refits), R5/R6
(sample and uncertainty), R11/R12 (prefix-control checks beyond one handoff), the long and scaled-short attack pass with
the configuration share, 0045's all-cell maxima and bin means, and R13/R14 (coverage and cross-arm). The disposition
record maps the seven upstream changes to their evidence and claims no new result. Both were written by the co-author who
built PRs #8–#14; neither carries a second reviewer's approval. **The ruling accepts this partial, unsigned record as
sufficient; the entry does not claim the uncovered rows were checked.**

**What changes.** The short-cell figures of 0029 and 0038 (and 0034's E9 column) may be cited in paper text as admitted,
without the "subject to Condition 1" qualifier; 0045's "release nothing" clause for e9s is lifted to the same extent. The
uncovered rows remain open work under issue #7 and no longer gate any paper. No deadline is implied: the LCFM
camera-ready closed 2026-10-03 23:59 AoE; whether its text printed the short-cell figures under the old condition is a
fact for the response map, not for this entry.

**What this does NOT touch.** Every verdict and cell (H-E9 HELD on a floor, 0029; H-E9L, 0036; the scaled short cell,
0038; 0045's tail figures); τ, the rule, the bands; the registered reading of f* as an oracle LOWER BOUND for two reasons
(0023, lines 1278 and 1281; 0027) — PR #12's README paragraph that calls it "not a general lower bound" is not adopted by
this ruling and needs its own corrective entry if it is ever to stand; the admission procedure for co-author-run results
(`docs/2026-10-03-co-author-run-admission.md`) and entries 0046/0047, which are about evidence, not review.

**Numbering.** 0048–0053 are allocated to staged, unrun drafts (the two registered runs' figures; the Llama long cell;
the Llama E8 amendment). By operator instruction this entry is numbered after them and appended before them, so it
precedes them in file order; `ledger_check` chains by file order and the drafts README is the allocator. Next free number
after this entry: 0055.

prior-entries-sha256: 5cbaec202c68a00b25c894450a20f950a8af9c703a15aae4386904d8716120d1

### 0052 — 2026-10-04 — E8 amended on the second model family before any rescoring: arm (b) over every agent sequence on 0040's own tensors; descriptive; no cell and no τ moves

**Why, and why now.** Entry 0040 ran 0009's instrument on `llama3.2-3b-to-llama3.1-8b` at 0016's matched protocol, so
arm (b) was scored on the LAST ⌈0.2 × 50⌉ = 10 agent sequences; it disclosed that the draw holds **42 distinct
windows in 50 rows** (one window 9 times) and that the registered hold-out is **2 distinct windows**. Entry
0041 left open whether the pair's τ_agent_K < τ_K inversion (1 − 0.7311 = 0.2689 against 1 − 0.7139 = 0.2861)
"is a property of the pair or of the draw", and said it "needs arm (b) rescored at `agent_holdout_frac = 1.0` over every agent sequence, and enters by its own numbered entry". Entry 0030 registered exactly that rescoring
for the Qwen pair; this entry re-registers it for this family, before anything is rescored: `results/e8fa/` holds nothing at append
and this entry's script refuses otherwise. (Recomputed here from the raw token files: the Qwen draw under the same rule also holds
42 distinct windows in 50 rows — the repetition is a property of 0016's sampling rule on these suites, not of the Llama-3 BPE;
stated as an observation, it changes nothing registered.)

**What is registered.** A rescoring of 0040's OWN tensors — the 64 fingerprinted agent dump files (source and target, per layer) at `results/e8f/kv/agent` and the token
file they were dumped from (`agent_n50_len1024_seed8.npy`, sha256 `4e02d14af008`), both reused and required to match the
fingerprints in `results/e8f/report.json` (sha256 `4682508afd35`) byte for byte; nothing is resampled or re-dumped; the generic
dumps are the archived ones. The protocol is 0030's, unchanged, under `config/e8fa.toml` (sha256 `80f51f0a36e9`): for each
k ∈ {1, 4, 8}, arm (a) on the mapper's own held-out generic sequences (`holdout_frac` 0.2, unchanged); arm (b) at `--holdout-frac 1.0`,
every one of the 50 agent sequences (12,800 scored tokens at stride 4); the drop (a − b) and its 0009 band word
read descriptively; per-sequence R² for both arms from the per-token record (upstream `per_sequence_moments`, SST around the global
held-out mean, so a sequence's R² is its share of the pooled decomposition); a seeded percentile bootstrap over agent sequences
(seed 52 + k, 2,000 reps) of arm (b)'s pooled R² and of the drop; and the change from 0040's arm (b) at
the same k, named as such. Because 9 rows are one window, the bootstrap resamples rows, not distinct windows, and the entry that
states the figures must say so beside them.

**What this does NOT touch.** τ_K = 0.2861, τ_V and τ_agent_K = 0.2689 stay as 0040 stated them and as `config/e9f.toml`
and `config/e9fl.toml` carry them; the all-sequence counterpart is reported beside τ_agent_K, never substituted (0044 has already read
it). `results/e8f/` is not rewritten — the family's E9 calibration reads it — and this amendment writes only under `results/e8fa/`.
H-E8 is entry 0020's, on the Qwen pair, and is untouched; 0040's band reading is itself descriptive and does not move.

**Instrument and enforcement.** No code change: `config/e8fa.toml` names this entry in `[e8.amendment]`, reuses 0040's report,
and pins the family's upstream commit `06f8d55`, which already contains 0030's upstream change (`223f469` is its
ancestor; `--holdout-frac 1.0` and the per-sequence block are in `scripts/score_mapper.py` at the pin). The driver's gate for this
config is 0009 + 0016 + 0039 + this entry (`e8.required_entries`); `e8.reuse_agent_dumps` checks every fingerprint before scoring;
`summarize_e8` recomputes the per-sequence figures from the record and refuses on disagreement with the report, with the re-scored
json, or with a changed prior report. The script that appended this entry asserted every one of these against the tree.

**Scope.** All of 0009's, 0016's, 0039's and 0040's limits: one pair, one direction, one mapper, off-policy text for Llama-3,
visible messages only (0012). No hypothesis cell changes with this entry; no `verdict:` line. The figures enter by their own numbered
entry from a passing `summarize_e8 --config config/e8fa.toml`, run after the ordinary `e8 --config config/e8fa.toml` (CPU).

prior-entries-sha256: 1f6ed2f90a114d60c95b426d9bf937b0c2a58fdb4a0f19c2201b428a4ce91d02

### 0056 — 2026-10-04 — Co-author pilot figures admitted to paper text by operator ruling: the two merged co-author documents may be cited under a provenance sentence; supersedes the "in any paper" clauses of 0046 and 0047; the ledger's evidence rules unchanged; descriptive, no cell moves

**What 0046 and 0047 said.** Each registered a co-author's fork run as the PILOT of the experiment it registered and
said: no figure from the pilot is stated in the entry or in any paper until the pilot's bundle is published to the Hub
and recomputed under `docs/2026-10-03-co-author-run-admission.md`.

**The ruling (operator, 2026-10-04).** Figures the co-author has posted in the repository, with the code and the
environment on the record, may be cited in paper text. The record is: `docs/2026-10-01-cache-behavior-h100.md`
(`81ad2740a3457507…`, merged b26dfdb by PR #14; execution commit `9a18ce7`, freeze record
`docs/2026-10-01-cache-behavior-freeze.json` `cff700063b6c3fd5…`, driver `tools/cache_behavior/`, environment torch 2.14.0 / transformers 5.17.0 / CUDA 13.0 on
one H100 PCIe 80 GB; the co-author's reproduction comment https://github.com/hossainpazooki/linear-ceiling/pull/14#issuecomment-5977021295) for the W1
figures, and `docs/2026-10-01-a100-analysis.md` (`cf27e75069f9fe04…`, merged c7911a4 by PR #9; results commit `2fb4464`,
driver `tools/consolidation/`, `requirements-linux.lock`, input manifest `config/consolidation-manifest.json`, one
A100-SXM4-80GB; comment https://github.com/hossainpazooki/linear-ceiling/pull/9#issuecomment-5977015570) for the W7 figures. **This entry types none of
those figures**: the paper cites the documents, and the documents are the co-author's.

**The provenance sentence the citation must carry**, in substance: run by a co-author on the named card at the named
commit with the pinned environment; code, input manifest and environment are in this repository; the raw evidence
bundle is on the co-author's machine, not public, and the figures have not been recomputed by anyone else. The a100
document says so itself ("have not yet been published to a public dataset; do not claim …"); the h100 document says it
is "not an admitted upstream E-BEH result". The paper repeats both.

**What this does NOT change.** R1, R8 and R12 of `docs/gpu-experiment-protocol.md` for ledger entries: the figures of
these two experiments enter the LEDGER only by 0048 / 0049 from the operator's registered run, or by the admission
procedure once the bundles are public. The standing sentence "No downstream task-quality number is claimed" (0047): a
top-1 agreement is not task accuracy. Every verdict and cell; τ, the rule, the bands; 0054's ruling on Condition 1.
Entry 0054's precedent is extended, not widened: 0054 ruled on who approves a review; this entry rules on what paper
text may cite, and leaves what the ledger may record untouched.

**Scope.** Two documents, two experiments (W1 cache behavior; W7 same-model extension), one paper lane. A reviewer
pressing on the evidential gap is answered by the provenance sentence, not by this entry.

prior-entries-sha256: 95bee8bea883a0f6bb50ec9faf9765b80a7b25134b995ee1b6ab31c7b486d803

### 0055 — 2026-10-04 — E-TRUNC registered before any prefill: head truncation of the sender context on entry 0036's 35 handoffs at four levels (FULL / 65,536 / 49,152 / 32,768) under the same YaRN receiver, compared on the subset matched under every level; shrinkage stated from the alignment passes; descriptive, no cell moves

**Why, and why now.** Reviewer weakness W2 (`docs/2026-09-30-review-response-map.md`): length is not isolated. The
record agrees — entry 0037 (line 2240) says every cross-cell "what length changes" figure is length AND
configuration, and entry 0038 (line 2361) measured the configuration's share of the short→long far-from-seam gap
at 0.4285 on identical tokens; the residual is unattributed because the short and long cohorts are different handoffs.
This entry registers the run that varies length WITHIN a handoff: under causal attention a matched token's reused
K/V depend only on the sender prefix before it, so TAIL truncation of S changes nothing and the length treatment is
HEAD truncation, S' = S[−L:], every matched token's K/V computed from a shorter causal prefix at sender position
p_S' = p_S − (|S| − L). `results/e9t-*/` hold no report, score, control, bridge, token record or dump at append, and
this script refuses otherwise (R1); the only things under them are the four alignment passes
(`e9 --align-only --config config/e9t-<level>.toml`; coverage sha256 FULL `0b0419ea1d27`, L65
`c5c3b3d55828`, L49 `1120282c65b0`, L32 `d07606d8d3e8`), from which every count below is read.

**Three rulings, 2026-10-04 (design `docs/drafts/e-trunc-design.md` §10; quoted verbatim).** (1) Margin and statistic
for the pre-registered reading: "±0.005 absolute on the far-from-seam (16+) same-K *median*, as entry 0038 reports it" (0038's levels 0.0381 scaled-short, 0.0629 long, READ from
`results/e9s/compare.json` sha256 `a0699a826f1f` and `results/e9l/summary.json` sha256 `64e64e9318d4`);
"unattributed" between the band and FULL's level. Why the median: 0038 reports medians and the seam-bin means run
1.6–1.8× higher (0045). (2) Shrinkage gate: NOT the run queue's 0.80 ratio default but "an absolute floor (|M_∩| ≥ 2,000) beside the ratio", taken as the void
gate, with "the pooled |M_∩| / |M_FULL| stated in the entry regardless of the gate" — because the pre-check below shows the ratio default would void 29 of 35
handoffs. (3) The L32-native cell: "include it, keep R under YaRN, and state so". Scope check: entry 0025 (line 1459) and 0019 register the native cell's
exclusion rule as over-cap handoffs EXCLUDED and counted, never truncated, so a sender truncated into the native window
can never enter or speak to H-E9's verdict and the cell would be descriptive-only. It is **not in this entry**: the
driver applies one RoPE schedule to every dump of a handoff and the summarizer enforces per-role spec identity, so a
sender-native / receiver-scaled dump has no instrument yet; it enters, if at all, by its own pre-prefill amendment
after that instrument exists and is tested (0035's precedent: the RoPE spec before the scaled receiver).

**Cells.** FULL = 0035's instrument on the same 35 handoffs (|S| 34,974–80,111), re-run under this entry's gate
so every level's per-token record comes from one box and one pin — the control arm; L65536 (L = 65,536: 4 of 35 handoffs differ from FULL) / L49152 (L = 49,152: 19 of 35 handoffs differ from FULL) / L32768 (L = 32,768: 35 of 35 handoffs differ from FULL). Receiver and source
under 0036's static YaRN `{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}` on every dump of every level, at the upstream pin
`063f4023fdde`; the n = 50 k = 1 mapper by sha for the cross arm. `config/e9t-{full,l65,l49,l32}.toml` are
`config/e9l.toml` byte-for-byte on the rule, τ, ladder, controls, seam bins, block floor, bootstrap, bridge, profiles,
keep draw, mapper and pin; they differ only in the results and scratch directories, `[e9.gate]` (ends at this entry),
`[e9.order] by = "n_sender_desc"`, `[e9.alignment] sender_head_truncate` on the three levels, and `[e9.trunc]` on FULL
(the levels, the floor, the margin, the two reference records, bootstrap seed 52 / 2000 reps). Registered
hashes (LF-normalized): `e9t-full.toml` `005d8d102deb`; `e9t-l65.toml` `782f7354f422`; `e9t-l49.toml` `d4d54381e394`; `e9t-l32.toml` `3c0663fbb651`. Inclusion is decided on the FULL
lengths before truncation, so every level keeps 0036's set: **68 observed · 35 included · 25 excluded as decided
under the prior cap · 4 excluded above the cap · 4 excluded for an empty receiver prompt**, the same eight by name as 0035.
A handoff with |S| ≤ L is identical at that level and at FULL and still counts.

**The matched subset, and the shrinkage stated before any verdict (ruling 2).** Alignment is re-run per level because
the aligner sees S'. Tokens matched under EVERY level form M_∩, identified in the FULL frame as (p_S, p_R) after
undoing each level's offset |S| − L; δ is compared on M_∩ only. A handoff with **|M_∩| < 2,000** is VOID for the
comparison and listed; |M_∩| / |M_FULL| is stated per handoff and pooled and gates nothing. **The CPU pre-check, from
the four alignment passes alone (`summarize_e9_trunc --shrinkage`, recomputed in-process by this script):** |M_∩| / |M_FULL|
per handoff median 0.4470 (p10 0.0000, p90 0.8270; min 0.0000, max 0.8965), pooled 0.4090
(158,480 of 387,508 matched tokens); **14 of 35 handoffs are void under the floor** (11 with
|M_∩| = 0), so **21 handoffs enter the comparison**; 29 sit below the 0.80 ratio the run queue proposed. The
loss is dominated by what the truncation REMOVES: the receiver's prompt re-renders EARLY sender content, and the
fraction of FULL pairs whose sender position survives S[−32,768:] has median 0.5027; aligner re-matching
loses more than the removal on 10 handoffs (median loss beyond removal 0.0000, max
0.4159 of |M_FULL|) — the design's stated weak point, measured rather than assumed. Void:
`20241016_composio_swekit/astropy__astropy-12907_traj#97`; `20241016_composio_swekit/astropy__astropy-13398_traj#133`; `20241016_composio_swekit/astropy__astropy-13453_traj#109`; `20241016_composio_swekit/astropy__astropy-13977_traj#118`; `20241016_composio_swekit/astropy__astropy-14369_traj#108`; `20241016_composio_swekit/astropy__astropy-14539_traj#114`; `20241016_composio_swekit/django__django-10973_traj#87`; `20241025_composio_swekit/astropy__astropy-12907_traj#104`; `20241025_composio_swekit/astropy__astropy-13453_traj#102`; `20241025_composio_swekit/astropy__astropy-13977_traj#83`; `20241025_composio_swekit/astropy__astropy-14369_traj#132`; `20241025_composio_swekit/astropy__astropy-8707_traj#152`; `20241025_composio_swekit/astropy__astropy-8872_traj#74`; `20241025_composio_swekit/django__django-11087_traj#97`. Consequence stated now: "length" here means causal-prefix length on the tokens the receiver
re-renders from the LATE part of S, and M_∩ sits at late sender positions while the two reference medians were pooled
over full matched sets.

**Statistics (per handoff on M_∩, paired across levels; descriptive).** Per level: mean δ_K; the fraction of tokens
over τ_K = 0.3186; f*(τ_K) and f* on the ladder (0.1, 0.03) by 0023's MEAN-repair definition, oracle
lower bounds (0027); the far-from-seam (16+) pooled median AND mean δ_K in FULL's causal seam frame b⁻(t) (0025); the
paired (level − FULL) mean δ_K per handoff with its median over handoffs and a seeded percentile bootstrap (seed
52, 2000 reps, `e7_stats.quantile`; reported, not read). V alongside, verdict-bearing for nothing. Each level is
also a complete 0035 run and is read by `summarize_e9` on its own (controls, bridge, profiles, band word stated
descriptively) before the comparison runs.

**The pre-registered reading (ruling 1).** If L32's far-from-seam (16+) pooled median δ_K on M_∩ over the non-void
handoffs lies within ±0.005 of 0.0381 (the scaled-short level, the same receiver configuration), the residual
short↔long gap reads as **length**; within ±0.005 of 0.0629 (the long level), as **the handoffs**; between,
**unattributed**, said so. FULL's own 16+ median on the same tokens is stated beside L32's. No hypothesis cell
moves either way; the comparison's figures enter by their own numbered entry and the paper only from that entry.

**Run order, stopping rule, resume.** Within each level the driver scores the included handoffs in the REGISTERED order
`n_sender_desc` (full |S| descending, ties by id): `django__django-11087_traj#152` (80,111) first, `astropy__astropy-7671_traj#85` (34,974)
last, so the longest senders — the only ones the higher levels change — are scored first and a stopped level leaves
a named scored prefix. Controls run on the first handoff in that order at every level. `e9 --close-partial --config
config/e9t-<level>.toml` closes an unfinished level on a PREFIX of its order; the comparison is then defined on the
handoffs scored at EVERY level and the summarizer names the unscored per level. `--resume` after a crash keeps
hash-matching work. Keep subset per level: n = 3, seed 9, the same draw as 0035's over the same ids
(`20241016_composio_swekit/astropy__astropy-8872_traj#117`; `20241025_composio_swekit/django__django-10554_traj#112`; `20241025_composio_swekit/django__django-11087_traj#97`); kept dumps per level, fingerprinted, re-scored at home under 0028's tolerance.

**Compute bound (R2 — a bound to be replaced by the probe on the granted card).** Prefill budget from the coverage:
FULL 3,970,435 tokens; L65536 3,921,773 / L49152 3,596,221 / L32768 2,721,489; total 14,209,918 = 3.58× E9-long's. E9-long's
sitting scored its 35 at 1.5–3 min per handoff (`docs/2026-09-10-e9l-gpu-runbook.md:139`) in 80 minutes (0036), with a measured peak
of 31.56 GiB at |S| = 80,111 (`docs/2026-09-10-e9l-gpu-runbook.md:127`); memory is bounded by FULL, so an L40S 48 GB fits every level,
and the four levels bound at 3.58× E9-long's wall time. The card is requested only after this entry is on the ledger.

**Gate and enforcement.** `e9 --check --config config/e9t-<level>.toml` refuses until entries 0019/0023/0025/0027/0035/0055 are in
the committed ledger, that config is committed unmodified, the upstream is at the pin with every invoked path clean and
the mapper artifact is present by sha. `summarize_e9 --config config/e9t-<level>.toml` (fail-closed) reads each level
as it read 0036's run, re-deriving every alignment from the raw traces under the truncation; `summarize_e9_trunc`
(fail-closed, the only reader of the comparison) runs those four first, then pairs the levels on M_∩, applies the
floor, states the shrinkage, the statistics and the reading, with every report, score, token record, coverage file
and reference record pinned by sha, and refuses on any disagreement — including a level run under another pin,
another config, or a different trace. Tests: `tests/test_e9_trunc.py` (the key, the exclusion decided on full lengths,
the match set shifted by exactly |S| − L and unchanged by a tail cut, the descending order) and
`tests/test_summarize_e9_trunc.py` (the four configs as one instrument, M_∩ in the FULL frame, the void gate, the
three outcomes of the reading, the pins).

**What this does NOT touch.** The H-E9, H-E9L and H-E9F cells; τ_K, τ_V, τ_agent_K, the rule, the band, the ladder;
entries 0036, 0038 and 0045 and their records; `results/e9/`, `results/e9l/`, `results/e9s/`, `results/e9f*/`,
`results/e8*/`, `results/consolidation/`, `results/cache-behavior/`; `config/e9.toml`, `config/e9l.toml`,
`config/e9s.toml`; entries 0046–0049, the Llama long drafts (0050 / 0051), the second family's E8 amendment drafts
(0052 / 0053) and 0054. Nothing here is a figure of the run; the pre-check figures above are alignment counts, not
deviations.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the long half of one corpus under a scaled
receiver (the bridge control runs at every level as 0035 registered it); "length" = causal-prefix length of the
reused K/V on the late-S tokens the receiver re-renders, not the number of turns; the 4 handoffs above
81,920 and the 4 with an empty receiver prompt stay excluded; the comparison is read on the handoffs that keep at least 2,000 common matched tokens
(21 of 35 at the pre-check; the 14 void handoffs are named, never pooled, and are a LIMITATION the
paper states: the result speaks for the handoffs whose receiver re-renders enough of the late sender context to survive truncation,
not for all 35); the L32-native cell is deferred, so nothing here compares native with YaRN on the same tokens, a second
stated LIMITATION (W6's bridge stays the only native-vs-YaRN evidence); f* stays an oracle lower bound; generation quality after reuse not
measured.

prior-entries-sha256: d1fd0344bc30f60f4ca4ae3d70ab2fc293f94189eadabb4bb38f7a481b3bc715

### 0053 — 2026-10-04 — E8 amendment ran on the second model family `[BASELINE, DESCRIPTIVE]`: arm (b) over every agent sequence; the inversion does not persist; no cell and no τ moves

**Provenance.** Registered by 0052 before any rescoring; `config/e8fa.toml` (sha256 `80f51f0a36e9`) and this ledger committed
unmodified; upstream at the family's pin `06f8d55`, clean for the invoked paths; 0040's agent dumps and token file
(`agent_n50_len1024_seed8.npy`, sha256 `4e02d14af008`) reused byte for byte, fingerprints checked at run time and again by the summarizer
against `results/e8f/report.json` (sha256 `4682508afd35`); arm (a) cross-checked against the archived `r2.json` for every k. Every
figure below is `summarize_e8 --config config/e8fa.toml`'s: the scorer re-run on the fingerprinted dumps, per-sequence R² recomputed from
the per-token record and checked against both the report and the re-scored json, the prior report's hash re-checked. Pinned:
`report.json` `5521a423ae29`, `summary.json` `9ddb66cc2796`. Arm (a) keeps the mapper's own held-out fraction 0.2; arm (b)
scores all 50 agent sequences (12,800 tokens) — 0040 had scored the last 10
(2,560 tokens at the matched protocol).

**The draw, restated beside the figures (recomputed from the token file).** 50 rows, **42 distinct windows**, the most repeated
window 9 times; the registered hold-out was **2 distinct windows**. The bootstrap below resamples rows, so a repeated
window carries its multiplicity; nothing here de-duplicates, because 0016's rule drew rows and this entry rescored the rows it drew.

| k | agent seqs / tokens | arm (a) generic K / V | arm (b) agent, ALL K / V | 0040's arm (b) K / V | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |
|---|---|---|---|---|---|---|---|---|---|
| 1 (0040 verdict k) | 50 / 12,800 | 0.7139 / 0.4711 | **0.6979 / 0.4137** | 0.7311 / 0.4599 | -0.0332 / -0.0462 | +0.0160 / +0.0573 | [+0.0052, +0.0267] | [+0.0410, +0.0740] | HOLDS / UNRESOLVED |
| 4 | 50 / 12,800 | 0.6183 / 0.2909 | **0.5816 / 0.1471** | 0.6219 / 0.2265 | -0.0403 / -0.0794 | +0.0367 / +0.1438 | [+0.0212, +0.0511] | [+0.1147, +0.1721] | HOLDS / UNRESOLVED |
| 8 | 50 / 12,800 | -0.0591 / -0.9696 | **-0.2019 / -1.5591** | -0.1333 / -1.3388 | -0.0686 / -0.2203 | +0.1428 / +0.5896 | [+0.1032, +0.1826] | [+0.5003, +0.6805] | UNRESOLVED / DEGRADES |

Bootstrap: seeded percentile over agent sequences (seed 52 + k, 2,000 reps), 2.5% / 97.5% of the drop; reported, read by nothing.
Band words are 0009's band applied to the all-sequence drop for orientation only.

**Per-sequence R² (a share of the pooled decomposition, SST around the global held-out mean), median (p10, p90):**

| k | agent K | agent V | generic K | generic V |
|---|---|---|---|---|
| 1 | 0.6943 (p10 0.6522, p90 0.7619) | 0.4013 (p10 0.3437, p90 0.4961) | 0.7595 (p10 0.5911, p90 0.7895) | 0.5205 (p10 0.3336, p90 0.5764) |
| 4 | 0.5754 (p10 0.5251, p90 0.6668) | 0.1156 (p10 0.0274, p90 0.2853) | 0.6912 (p10 0.3928, p90 0.7269) | 0.3554 (p10 0.0889, p90 0.4496) |
| 8 | -0.2360 (p10 -0.3140, p90 0.0006) | -1.6717 (p10 -1.9578, p90 -1.1538) | 0.1084 (p10 -0.5074, p90 0.2153) | -0.7873 (p10 -1.3942, p90 -0.5658) |

**What changed and what did not.** At k = 1, scoring every agent sequence instead of the last 10 moves arm (b) by
-0.0332 (K) / -0.0462 (V); the drop is +0.0160 / +0.0573 with 95% bootstrap
[+0.0052, +0.0267] / [+0.0410, +0.0740], read against
0009's band as HOLDS / UNRESOLVED (0040, at the matched protocol: HOLDS / HOLDS). **The question 0041 left open:**
the τ_agent_K < τ_K inversion does not persist: arm (b) over every sequence scores at or below arm (a) on K (all-sequence arm (b) K 0.6979 against arm (a) K 0.7139); whether that is a property of
the pair or of a draw with 42 distinct windows is narrowed, not closed — the windows are the same 42. **τ_agent_K stays
0040's registered value, 1 − 0.7311 = 0.2689; the all-sequence counterpart, 1 − 0.6979 = 0.3021, is
reported here beside it and substituted for nothing** (0044 has already read τ_agent_K; τ_K = 0.2861 is untouched). **No cell moves; this
entry carries no `verdict:` line; nothing here is pooled with a Qwen figure.**

**Not established.** Anything beyond 0040's limits: off-policy text for Llama-3, one pair, one direction, one mapper, visible messages
only (0012); the agent windows are 0016's draw under the Llama-3 BPE, not new text, and 8 of the 50 rows repeat another; arm (a)'s
figure is on the mapper's own held-out generic sequences and its per-sequence spread is over that many. H-E8 is 0020's and is unchanged.

**Scope.** All of 0009's, 0016's, 0039's, 0040's and 0052's limits. No hypothesis cell changes with this entry.

prior-entries-sha256: b4ae9246fc407b36d3f24886b84330d63e9f1bce7a0a158da4e68c8eb4e8c002

### 0050 — 2026-10-04 — E9 long half registered before any prefill on the second model family, at a NATIVE receiver: entry 0035's D1(a), its configuration bridge and its scaled-receiver reading declared INAPPLICABLE; descriptive, no cell moves

**Why, and why now.** The short cell of this family (0042, decided by 0044) covers the handoffs whose
longer side fits 32,768 tokens. The handoffs above it are the same question at greater
length, and on this pair they can be asked WITHOUT scaling anything: the receiver meta-llama/Llama-3.1-8B ships a native
window that already covers the cap below. This entry registers that run before any prefill —
`results/e9fl/` holds no report and no score file at append, and the script refuses otherwise (R1) — and
registers, equally explicitly, what it is NOT. The only things under it are the alignment pass
(`e9 --align-only --config config/e9fl.toml`, `align/coverage.json` sha256
`16121e677b97`) and the τ calibration (`calibration/tau.json` sha256
`dd3fca27e82a`), both checked here against the committed config.

**Descriptive, and what that forecloses.** **No hypothesis row is added and no `verdict:` line will
follow.** In particular this cell **cannot move, support or refute H-E9L, and is never pooled with entry
0036's handoffs.** H-E9L is a claim about a receiver pushed PAST its pretraining window by static YaRN
(entry 0035's D1(a)): the question there was whether a SCALED receiver keeps transfer-relevant fidelity at
those lengths. Here nothing is scaled. Two experiments sharing a length axis and nothing else; the numbers
are stated beside each other, never added, averaged or compared as if one were a replication of the other.

**Entry 0035's three scaled-receiver instruments, declared INAPPLICABLE by construction.** (i) **D1(a),
the receiver configuration**: there is no `[e9.rope]` — the receiver's own checkpoint declares a window
covering 81,920, so no scaling is needed and applying one would measure an artifact of our own
construction. (Imposing YaRN here to preserve the comparison with 0036 was considered and rejected:
upstream `scaled_config` merges the override OVER the checkpoint's own rope parameters, replacing this
family's native `rope_type` while leaving its band factors behind — it would REMOVE the checkpoint's own
scaling rather than compose with it.) (ii) **Control 4, the configuration bridge**: its entire content is
scaled arm versus native arm on the same tokens, and a natively long receiver has no scaled arm;
`config.py` refuses a `[e9.bridge]` without an `[e9.rope]`, and that refusal is correct here rather than an
obstacle. (iii) **The scaled-receiver reading** ("if the bridge control exceeds its maximum, H-E9L is a
claim about the scaled receiver only") has no referent and is not carried over. What replaces all three is
stated below and costs no GPU time.

**The two controls that replace the bridge.** Read off the dumps themselves: upstream `kvt/data.py` writes
each dump's `RopeSpec` — the `inv_freq` and attention factor of the loaded model's OWN rotary embedding —
halt-checks the reconstruction against the model at every dumped position, and
`linear_ceiling.e9.dump_rope_meta` keeps that record beside every dump's fingerprint BEFORE the non-kept
dumps are deleted. **(1) Native window:** `context_cap` = 81,920 must be ≤ EVERY dump's
recorded `max_position_embeddings` — the positive statement that no extrapolation happened, which is
exactly what the bridge used to establish by measurement. A run whose dumps carry NO RoPE block at all (a
pin older than the RoPE-spec commit, where the strip is plain-θ and therefore silently wrong for this
family) **FAILS** this control; it does not pass it vacuously, and the summarizer refuses such a run
outright for this cell. **(2) Frequency identity, scoped by model ROLE:** the recorded spec must be
identical across every dump of the receiver, and across every dump of the source, compared separately.
Role-scoped is not a weakening: this pair's two sides carry different scaling factors and build different
inverse-frequency vectors by construction, so an unscoped equality assert would refuse every CORRECT run.
Both are fail-closed in `summarize_e9` and both survive the deletion of the non-kept dumps.

**The verdict set is a band of token counts, and the thresholds are not hardware bounds.**
`context_floor = 32,768`, `context_cap = 81,920`: registered LENGTH thresholds
in this pair's own tokens. 81,920 is NOT "32,768 × 2.5" here — there is no
scaling factor to multiply — it is the same numeric band entry 0036 reported, kept only so the two long
cells are DEFINED over the same token counts. A handoff whose |S| and |R| both fit the floor was covered by
the short cell and is EXCLUDED here with its own reason; this script checks that those excluded ids are
EXACTLY the short cell's included set, so the partition is audited rather than asserted. Coverage from the
alignment pass: **68 observed · 32 included · 28
excluded as covered by the short cell · 4 excluded above the cap · 4 excluded for
an empty receiver prompt**. Together the two cells cover every handoff whose longer side is within
81,920 tokens; the **residual — 4 handoffs above 81,920 — is scored
by NEITHER cell** and is named here so it cannot be mistaken for absence: `20241016_composio_swekit/astropy__astropy-13398_traj#290`; `20241016_composio_swekit/astropy__astropy-13398_traj#447`; `20241016_composio_swekit/astropy__astropy-14365_traj#298`; `20241025_composio_swekit/astropy__astropy-13453_traj#221`
(|S| 175,974, 337,667, 150,160, 135,559). Included |S| runs 33,086 to 74,233; the prefill
budget is 1,541,320 sender tokens (both models) + 370,926 receiver tokens = 3,453,566 tokens.

**The instrument, unchanged.** 0023's rule verbatim, with τ this pair's own and IDENTICAL to the short
cell's (one mapper, one calibration): τ_K = 0.2861 = 1 − 0.7139, the
k = 1 mapper's held-out R² over 2,560 tokens; τ_V = 0.5289; τ_agent_K =
0.2689. The HOME calibration is authoritative for K/V: this config agrees with it at 1e-9 and
the box-written E8 report agrees within the registered 1e-6 cross-platform tolerance; agent K agrees
across config, calibration and E8 arm (b) at 1e-9. The τ ladder (0.1, 0.03); the seam bins; the block floor
(4); the bootstrap (seed 25,
2000 reps). The band words
HOLDS ≤ 0.15 / DEGRADES ≥ 0.50 are **computed and reported
here and are verdict-bearing for nothing**: this cell has no row. f* stays an oracle LOWER BOUND read on a
floor (0027).

**Run order, stopping rule, resume.** The driver scores the included handoffs in the registered order
`n_sender_asc` (|S| ascending, with any ties broken by id): `astropy__astropy-7336_traj#119` (33,086)
first, `django__django-11087_traj#152` (74,233) last. Controls run on the first handoff in that order.
**This is the campaign's cuttable stage.** If the sitting must end before all 32 are scored,
`e9 --close-partial --config config/e9fl.toml` closes the run: allowed only by this config, refused unless
the scored set is a PREFIX of the registered order, stamping the close time and naming every unscored
handoff; the figures entry then states "n scored of 32 registered" beside every number. The
cutoff is the operator's, is recorded with its reason, and may not depend on any score. A relaunch after a
crash uses `--resume`.

**Keep subset.** n = 3, seed 9, a fresh draw from THIS cell's sorted included ids
(numpy `choice` without replacement is not nested, so this is not a subset of the short cell's):
`20241016_composio_swekit/astropy__astropy-8872_traj#117`; `20241025_composio_swekit/django__django-10097_traj#137`; `20241025_composio_swekit/django__django-11087_traj#97`. Small on purpose — at this cap one kept handoff is tens of GB of fp16 dumps. Their
stride-1 dumps are retained, fingerprinted, pulled home and re-scored from tensors by the summarizer under
0028's tolerance.

**Controls (1–3 as 0023/0025; 5 re-cut; 6 as 0025).** (1) Pipeline identity HALT. (2) Prefix-invariance
HALT on the first handoff in run order, max centered δ ≤
1e-04 — entry 0039's
pre-registered absolute float32 kernel-noise bound, exactly `config/e9.toml`'s and never a function of
τ_K. (3) δ_null, seeded derangement (seed
23). **(5) Length profiles (descriptive):** f*(τ_K) and median δ_K (i) by |S| bin
(32,768, 49,999] / [50,000, 64,999] / [65,000, 81,920], and (ii) by matched-token position in S [0, 8,191] / [8,192, 32,767] / [32,768, 65,535] / [65,536, 81,920] — (ii) is the long-context figure, and its
edges are re-cut at this family's OWN boundary (the point where its RoPE frequency rescaling begins),
because entry 0035's edges were the midpoint of a YaRN window that does not exist here. (6) Seam profiles
b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9fl.toml` refuses until entries 0019/0023/0025/0027/0050 are in the
committed ledger, `config/e9fl.toml` is committed unmodified, the upstream is at the pin
`06f8d5559257` with every invoked path clean, and the mapper artifact is present by sha.
`summarize_e9 --config config/e9fl.toml` (fail-closed, the only reader) re-derives every alignment from the
raw traces with the floor, re-derives the run order, checks a partial close is a prefix, recomputes every
figure, re-scores the kept dumps from tensors, recomputes τ, checks the controls and the two RoPE controls
above, and states the profiles and the band. The τ calibration is checked at THIS entry as well as by the
summarizer, for the reason entry 0042 gives.

**What this does NOT touch.** The H-E8, H-E9, H-E9L and H-E9F cells; entry 0036's figures and its 35
handoffs; τ, the rule, the band, the ladder and the keep subsets of every other cell; `results/e9/`,
`results/e9l/`, `results/e9s/`, `results/e9f/`, `results/e8*/`; `config/e9.toml`, `config/e9l.toml`,
`config/e9s.toml`, `config/e9c.toml`, `config/e9f.toml`. Nothing here is a figure: this cell's figures enter by
their own numbered entry, and the paper only from that entry.

**Scope.** One pair (meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B), one direction, one agent family, the long band of one corpus at
a NATIVE receiver; off-policy text for Llama-3; floor not method (0027); the 4 handoffs above
81,920 and the 4 with an empty receiver prompt stay excluded and counted;
generation quality after reuse not measured. `eval_hellaswag.py` and `compose_mapper.py` remain out of
scope for this pair (entry 0039).

prior-entries-sha256: 03ae7892e67a0fe37245ab17eef17a82ccb928fa4a2d5abb3cb3ff19721104d2

### 0048 — 2026-10-07 — Same-model extension ran `[BASELINE, DESCRIPTIVE]`: Qwen3-4B and SmolLM3-3B on the original 60 handoff texts at the Qwen reference τ, bridge passed; stated beside the Qwen3-0.6B→1.7B cells and never pooled; no cell moves

**Setup, as registered (0046).** RunPod community NVIDIA A100-SXM4-80GB (one card), pod and machine ids in docs/2026-10-07-consolidation-runpod-runbook.md; launched 2026-10-07T04:01Z, finished 2026-10-07T06:29Z; GPU as recorded in every report
`NVIDIA A100-SXM4-80GB`; PyTorch 2.14.0+cu130, Transformers 5.17.0, NumPy 2.5.3, CUDA 13.0; config `857cc92320cb…`, manifest
`99185c5891fc…`, driver `run.py` `87e0efb1502c…` / `capture.py` `2cddd19b1c43…` as committed. All 126 handoffs
complete, none excluded. Backup: `hossainpazooki/linear-ceiling-consolidation-2026-10-07` (R8, verified both ways before this entry).

**Controls.** Chunked-prefill control, maximum normalized deviation per model: Qwen3-1.7B (bridge) 4.70e-09, Qwen3-4B 1.07e-09, SmolLM3-3B 1.66e-10
(limit 1e-4). Bridge on six archived handoffs: maximum relative mean-deviation gap 1.23e-05 (limit 0.01), maximum f* gap 0.0000
(limit 0.01). Peak allocation per model: Qwen3-1.7B (bridge) 24.93 GiB, Qwen3-4B 39.72 GiB, SmolLM3-3B 22.96 GiB.

**Figures (same-model arm; `summarize.py` recomputed every record, re-scored every witness, 2,000 trajectory-cluster
bootstrap resamples; brackets are 95 % intervals on f*(0.03)).** τ_K = 0.3186442653116294 is the 0023 Qwen3-0.6B→1.7B mapper's
shortfall, a common numerical reference and not a threshold calibrated for either model.

- **Qwen3-4B, short (0038's 25)**, K: 25 of 25 at f*(τ) = 0; median f*(τ_K) 0.0000; f*(0.1) 0.0007; f*(0.03) 0.2739 [0.2057, 0.4737]; mean δ 0.1011; tail over τ 0.0843. V: 25 of 25 at f*(τ) = 0; median f*(τ_V) 0.0000; f*(0.1) 0.0342; f*(0.03) 0.3883 [0.2732, 0.5397]; mean δ 0.1269; tail over τ 0.0647.
- **Qwen3-4B, long (0036's 35)**, K: 35 of 35 at f*(τ) = 0; median f*(τ_K) 0.0000; f*(0.1) 0.0460; f*(0.03) 0.4979 [0.2077, 0.7239]; mean δ 0.1260; tail over τ 0.0908. V: 35 of 35 at f*(τ) = 0; median f*(τ_V) 0.0000; f*(0.1) 0.0923; f*(0.03) 0.5394 [0.2569, 0.7326]; mean δ 0.1446; tail over τ 0.0728.
- **SmolLM3-3B, short (0038's 25)**, K: 25 of 25 at f*(τ) = 0; median f*(τ_K) 0.0000; f*(0.1) 0.0000; f*(0.03) 0.1527 [0.0983, 0.3896]; mean δ 0.0722; tail over τ 0.0390. V: 25 of 25 at f*(τ) = 0; median f*(τ_V) 0.0000; f*(0.1) 0.0000; f*(0.03) 0.1353 [0.0940, 0.3491]; mean δ 0.0812; tail over τ 0.0276.
- **SmolLM3-3B, long (0036's 35)**, K: 34 of 35 at f*(τ) = 0; median f*(τ_K) 0.0000; f*(0.1) 0.0580; f*(0.03) 0.4529 [0.0955, 0.6761]; mean δ 0.1207; tail over τ 0.0578. V: 35 of 35 at f*(τ) = 0; median f*(τ_V) 0.0000; f*(0.1) 0.0000; f*(0.03) 0.3630 [0.0826, 0.5620]; mean δ 0.0956; tail over τ 0.0283.

Handoffs with f*(τ_K) > 0 on K among the new models: `20241025_composio_swekit/django__django-10554_traj#112` (SmolLM3-3B, e9l): mean δ_K 0.3320, f*(τ_K) 0.0228.

**Reading.** On both new receivers the mean deviation of the matched tokens sits under the Qwen reference on every
handoff but the ones named, with far less headroom at the ladder's 0.03 on the long cohort than on the short, as on the
original pair. This is a statement about means under one map's tolerance (0045); it is not a quality result, not a
length effect (different handoffs), and not pooled with any 0029 / 0036 figure.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; the original pair's entries and records.

prior-entries-sha256: 08b376985b5caac35d54237e9d104f8d03a87399372fe74136cff78fede72bf8

### 0049 — 2026-10-07 — Cache-behavior comparison ran `[BASELINE, DESCRIPTIVE]`: next-token sensitivity of Qwen3-1.7B to reading an assembled same-model cache on the 35 long handoffs, fresh vs reused with two controls; no band, no cell moves

**Setup, as registered (0047).** RunPod community NVIDIA A100-SXM4-80GB (one card), pod and machine ids in docs/2026-10-06-cache-behavior-runpod-runbook.md; launched 2026-10-06T23:50Z, finished 2026-10-07T01:22Z; GPU `NVIDIA A100-SXM4-80GB`, PyTorch 2.14.0+cu130,
Transformers 5.17.0, CUDA 13.0; config `53c664556d18…`, driver `core.py` `f346b5fdf3d3…` / `run.py` `15e1ff8c1dbc…` as committed,
run at commit `7c9a5fd`.
35 of 35 handoffs scored, 8,908 continuation tokens, none excluded; peak allocation 24.95 GiB. Backup: `hossainpazooki/linear-ceiling-cache-behavior-2026-10-07` (R8,
verified both ways before this entry). Pinned: `report.json` `3564605773bb…`, `summary.json` `5228de0dd8c4…`.

**Inputs and the manifest clause of 0047.** The inputs were prepared by the registered `--prepare` on Linux from the verified
E9-long mirror and the manifest-pinned traces; their manifest is `2aeee5769c0a…`. Its config digest equals the
pilot's freeze record; its corpus-manifest, archive-config and archive-report digests equal the committed bytes and the verified
e9l mirror (the freeze record pins no field beyond the config and the manifest hash itself; all checked by this script), and
every record's trace, alignment, score and token digest matches the corpus manifest and the e9l archive. It is NOT byte-identical
to the pilot's frozen `9a6f2923d3be…`: that manifest's `evidence_sha256_manifest` field is the sha256 of the pilot
author's evidence `SHA256SUMS` file, which is in neither the repository nor the archive, so the frozen hash cannot be reproduced
without that file; whether that field is the only one that differs is unknown until the pilot's manifest arrives (regenerated
`SHA256SUMS` layouts over the same archive files were tried against the frozen hash with no hit; a Windows prepare additionally
differs on every record sha by the zip `create_system` byte, members identical). 0047's clause "or the run refuses" was never
the driver's: the frozen `run.py` compares no manifest hash, so the only refusal was this script's, and the ruling below —
made on 2026-10-07 after the run had finished — moved it. Operator ruling, verbatim: "0047's byte-for-byte clause is read as: every field of the operator's manifest that is pinned to the repository or the verified archive equals the pilot's freeze record; the evidence-file digest, which pins a private file, is excluded. The operator's manifest 2aeee576… is the one 0049 asserts." The pilot author's `SHA256SUMS`
and `manifest.json` were requested (issue #20) for a field-level confirmation, which enters as a dated note if it arrives.

**Numerical controls (registered limits in 0047):** fresh-repeat maximum logit error 0.00e+00, prefix-copy maximum logit error 2.90e-04 (limit 5e-4), over all scored handoffs. Every per-handoff archive bridge passed, or the reader would have
refused.

**Figures (`run.summarize` in-process: every case record re-hashed, the scored set checked against the registered 35,
the logit witness re-checked; medians with p10 / p90 over handoffs, `e7_stats` convention, handoffs weighted equally).**
KL is KL(fresh ‖ candidate) per scored token, averaged per handoff.

- **REUSE-ALL (assembled same-model cache)**: mean KL per handoff 0.1424 (p10 0.0802, p90 0.1900) nats; p90 KL 0.3022 (p10 0.1768, p90 0.4713); top-1 agreement 0.9020 (p10 0.8549, p90 0.9216).
- **RANDOM (norm-matched perturbation)**: mean KL per handoff 11.2981 (p10 9.2592, p90 13.5357) nats; p90 KL 19.5226 (p10 16.5229, p90 22.6453); top-1 agreement 0.0471 (p10 0.0196, p90 0.0980).
- **CYCLIC (matched states permuted, keys relocated)**: mean KL per handoff 0.2826 (p10 0.1795, p90 0.3569) nats; p90 KL 0.6521 (p10 0.4347, p90 0.9791); top-1 agreement 0.8549 (p10 0.8039, p90 0.8902).

Fresh attention at the last 32 receiver queries (descriptive; medians over handoffs): weighted_delta_mean 0.1041 (p10 0.0881, p90 0.1440); weighted_delta_p90 0.2479 (p10 0.2038, p90 0.3294); tail_attention_mass_mean 0.0885 (p10 0.0651, p90 0.1295); tail_attention_mass_p90 0.2469 (p10 0.1631, p90 0.2990); matched_attention_mass_mean 0.4100 (p10 0.3280, p90 0.4893); matched_attention_mass_p90 0.8928 (p10 0.7293, p90 0.9655); conditional_weighted_delta_mean 0.3012 (p10 0.2516, p90 0.4060); conditional_weighted_delta_p90 0.6880 (p10 0.5722, p90 0.9666); conditional_undefined_count 0.0000 (p10 0.0000, p90 0.0000).

**Reading.** Reading the assembled same-model cache changes the receiver's predictions on the recorded continuation by
a measurable amount, and by far less than a norm-matched random perturbation of the same states; the cyclic
permutation sits between them. **Top-1 agreement is not task accuracy and no acceptance threshold exists**; the result
does not validate τ_K as a quality threshold, does not establish unchanged free generation, and measures no speed.
"No downstream task-quality number is claimed" stands.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, 0036, 0038, 0044, 0045 and
their records; the Qwen3 short cells (Condition 1).

prior-entries-sha256: f1efa70bf50f624d1d0c319bf7217ff6c3e7cf77959f9a032170529e98b7cb98

### 0058 — 2026-10-07 — Corrective: f* is the oracle REMOVAL fraction, not a lower bound on real selective recompute; the 0023 / 0027 "oracle lower bound … read on a floor" reading is withdrawn and the words every output carries change; definition, verdicts, cells, τ and every figure unchanged

**What 0023 and 0027 say.** 0023 (line 1275) defines f*(τ) as the smallest fraction of matched tokens that, removed
(recomputed exactly), leaves the MEAN δ_K **over the remaining tokens** at or below τ; line 1278 calls it "an oracle
LOWER BOUND on real selective recompute for two stated reasons" — a recomputed token is assumed restored exactly, and real
partial prefill recomputes the selected tokens against the reused KV of the others, so errors propagate; line 1281
requires every output stating f* to carry the words and both reasons. 0027 (line 1651) builds "HOLDS reads on a
floor" on it and sets f* beside CacheBlend's 10–15 % "ACHIEVED figure" (line 1653). 0029, 0036, 0038, 0044 and
others restate the floor beside their cells; 0054 (line 3320) declined to adopt the contrary reading and said it
"needs its own corrective entry if it is ever to stand". This is that entry.

**Why the bound does not hold.** The two registered reasons make a real scheme's repair fraction *higher* than an exact,
isolated one. But the denominator pulls the other way: write g*(τ) for the fraction an exact, isolated repair needs when the
mean is taken over **all** tokens (the k repaired tokens contributing 0). That mean is (n − k)/n times the remaining-token
mean, so every k that satisfies f*'s criterion satisfies g*'s, and **g* ≤ f*** always. Computed here with the registered
`f_star` (`linear_ceiling.e9_pertoken`): δ = (0.5, 0.5, 0.5, 0.0) at τ = 0.3: f* = 0.50, g* = 0.25; over
5,000 seeded random cases (seed 58; n 2–40; τ ∈ {0.03, 0.1, 0.3186}) g* > f* in 0,
g* < f* in 3,210, equal in 1,790, and (f* = 0) ⇔ (g* = 0) in every case. So f* bounds the exact-repair
fraction from *above*, the registered reasons push the real fraction *up* from there, and no ordering between f* and real
selective recompute is established in either direction. Only the reading was wrong: the definition at line 1275
already says "over the remaining tokens", and 0045 (line 2991) already reads f* = 0 as a statement about the mean.

**The ruling (operator, 2026-10-07).** (1) f* is read as the **oracle removal fraction**: the share of each handoff's
matched tokens whose removal brings the remaining-token mean within τ — a measure of how concentrated the disagreement is,
not a repair cost, and **not a bound on real selective recompute in either direction**. (2) Line 1281 is replaced:
every output stating f* carries the words "oracle removal fraction" and this entry's number, and the two 0023 reasons are
stated only where propagation is discussed, never as grounds for a bound. (3) 0027's floor sentence is withdrawn. HOLDS
reads: on the median handoff, the mean δ_K over the matched tokens is at or under the mapper's own mean deviation τ_K, or
gets there by removing at most the band's 15 % of them — f*(τ) = 0 ⇔ mean ≤ τ (Theorem 1 of the paper;
`fstar_eq_zero_iff` in `proofs/Carryover/Fstar.lean`, named from the source, not built here) — "no more than the mapper"
as a statement about disagreement, not about what any scheme pays. (4) The CacheBlend
comparison of line 1653 is dropped: an oracle removal fraction and an achieved recompute fraction are not
comparable in either direction. Entries that restate the floor stand as written (the chain is immutable) and are read
under this entry from here on.

**What changes in the tree, same commit.** The words `summarize_e9` prints beside the verdict-bearing f* line and the
`f_star` docstring; `tests/test_summarize_e9.py`'s pinned phrase; README.md's verdict table and "What HELD means here";
CLAUDE.md's H-E9 line; the staged `append_0057.py`'s scope sentence. The script that appended this entry refused until each
carried the new words and none the old.

**Occasion, for the record.** The camera-ready submitted 2026-10-04 (sha `6c706bef…`) writes App. D's "f* is not an
achievable recomputation or runtime cost" — correct, and the denominator is its reason — and App. A's "not a general lower
bound … because practical recomputation can propagate errors", whose conclusion is correct but whose reason is 0023's
second, which argues *for* the bound; a third sentence in the Introduction carries the same reading. Found by the skeptic
pass of `docs/reviews/2026-10-07-submitted-camera-ready-reconciled-against-the-record-and-the-operator-runs.md` §6.1. What the MLSys draft must change is the response map's business (#18 Q4), not this entry's.

**What this does NOT touch.** The definition of f* (0023, line 1275) and its 1e-9 tolerance; every verdict and cell
(H-E9 0029, H-E9L 0036, H-E9F 0044; the rule compares the statistic to the band, and the statistic is unchanged); τ_K, τ_V,
τ_agent_K, the band edges, the ladder; every figure on the ledger; 0045's tail figures; Theorem 2's bounds *on* f* as a
function of δ (`lower_bound_max`, `lower_bound_deltaMax`, `fstar_le_p` in `Fstar.lean` — bounds on the statistic, not
readings of it); 0010 / 0012's visible-only cost figures, which are LOWER BOUNDs on spend of a different statistic and keep
their label.

**Numbering.** 0058, the next free number in the drafts README; appended after 0049 in file order while 0051 and 0057 stay
staged (`ledger_check` chains by file order). Next free number after this entry: 0059.

prior-entries-sha256: 5ba3adab23b109d2a4e37c8384a6ff544decebab2e04c8f32bd8accbd5dbfee3

### 0051 — 2026-10-07 — E9 long half ran on the second model family `[BASELINE, DESCRIPTIVE]`: the long band at a NATIVE receiver; stated beside entry 0036's scaled-receiver figures and never pooled with them; no cell moves (32 scored of 32 registered)

**Setup, as registered (0050).** RunPod SECURE pod uua1cpjql18jb6, NVIDIA A100-SXM4-80GB (81,920 MiB, driver 580.126.16), 128 vCPU / 2,003 GB host RAM, $1.59/h, created 2026-10-07T17:01:48Z; home side the operator's Mac mini; linear-ceiling at the commit carrying 0050 and
`config/e9fl.toml` (gate: entries 0019/0023/0025/0027/0050), upstream pin `06f8d55`.
Pair llama3.2-3b-to-llama3.1-8b: receiver meta-llama/Llama-3.1-8B, source meta-llama/Llama-3.2-3B, **neither scaled** — no `[e9.rope]`, no
`[e9.bridge]`, no `--rope-scaling` on any dump; the k = 1 mapper of this family's E8 sitting
for the cross arm, by sha. Launched 2026-10-07T17:35:23Z, finished 2026-10-07T19:46:17Z. Backup: `hossainpazooki/linear-ceiling-e9fl-2026-10-07` (R8, verified
both ways before this entry). **Coverage file, two renderings of one content:** entry 0050 pins
`align/coverage.json` at `16121e677b97…`, the sha of the home file's CRLF rendering (written on Windows); the box's
`--align-only` reproduced the same 993 lines as LF, sha `9f10092b6238…` (its evidence `versions.txt`),
and the launcher's exact-match check was passed on that rendering — the parsed records are identical and
the summarizer below re-derived them from the traces. Complete: 32 scored of 32 registered. Of
68 observed handoffs: 32 registered (longer side above 32,768 and within
81,920 tokens under this pair's own tokenizer), 28 covered by the
short cell and excluded here, 4 above the cap and scored by NEITHER cell,
4 with an empty receiver prompt. Every figure below is
`summarize_e9 --config config/e9fl.toml`'s, from a run that passed all of its checks: alignments re-derived
from the raw traces under the cap and floor; the run order re-derived; the partial prefix checked; every R²
recomputed from recorded moments; per-token squares summed against the moments; the 3 kept handoffs' stride-1 dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within 6.9e-04 relative, max |f* diff| 0.0e+00); τ recomputed
from the archived mapper; controls checked.

**The two controls that replace entry 0035's configuration bridge, reported first.** On a natively long
receiver these ARE the evidence that nothing was scaled, and `summarize_e9` refuses this cell outright if
the dumps carry no RoPE spec. Over all 97 dumps: **native window** — the registered cap
81,920 sat inside every dump's own recorded `max_position_embeddings`, so no dump asked either
model for a position its configuration does not declare; **frequency identity, by model role** — source (32 dumps, max_position_embeddings 131,072, inv_freq 31576ad84e5a, attention factor 1.0), target (65 dumps, max_position_embeddings 131,072, inv_freq 8480b7658cd7, attention factor 1.0);
the spec-vs-model halt check passed at every dumped position (worst |diff| 1.2e-07
against atol 1e-05), and every dump recorded an attention factor of 1.0. The roles
are compared separately because this pair's two sides build different inverse-frequency vectors by
construction (entry 0039).

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run
order: max centered per-token δ 0.000e+00 over 33,086 positions
(tolerance 1e-04, this pair's own value). δ_null same K / V token-mean median
2.010 / 2.023; equal-token null pairs
0.0085. Matched fraction |M|/|R| (a floor): 0.9531 (p10 0.7762, p90 0.9868).

**The statistic, computed and verdict-bearing for nothing.** Per scored handoff, E9-same, K read-out:
f*(τ_K = 0.2861) as 0023 defines it, median over scored handoffs. τ_K is 1 − THIS pair's own
held-out R² and is identical to the short cell's; this cell has no hypothesis row, so the band words below
are stated descriptively and decide nothing.

- **median f*(τ_K), E9-same K: 0.0000 (p10 0.0000, p90 0.0000)** over 32 handoffs (32 scored of 32 registered); seeded
  bootstrap of the median (seed 25, 2000 reps): [0.0000,
  0.0000]. Against 0023's edges (HOLDS ≤ 0.15, DEGRADES ≥
  0.5) the band word would be **HOLDS**, stated descriptively.
- f*(τ_V = 0.5289), E9-same V (alongside): 0.0000 (p10 0.0000, p90 0.0000).
- τ ladder (descriptive): τ = 0.1: same K 0.0000 (p10 0.0000, p90 0.3014) / V 0.0088 (p10 0.0000, p90 0.3580); τ = 0.03: same K 0.2696 (p10 0.0000, p90 0.6385) / V 0.2995 (p10 0.0018, p90 0.6132).
- f*(τ_agent_K = 0.2689): same K 0.0000 (p10 0.0000, p90 0.0000); cross K 0.8355 (p10 0.6923, p90 0.9519).
- f*(τ_K) over matched blocks of length ≥ 4: same K 0.0000 (p10 0.0000, p90 0.0000).
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: 0: 0.246 (n=3830) · 1: 0.128 (n=2735) · 2-3: 0.076 (n=4226) · 4-7: 0.061 (n=6598) · 8-15: 0.064 (n=8532) · 16+: 0.022 (n=308783).

**Length profiles (entry 0050 control 5, descriptive).** (i) by |S| bin, median f*(τ_K) same K over
handoffs: |S| 32769-49999: 0.0000 (p10 0.0000, p90 0.0000) (n = 21); |S| 50000-64999: 0.0000 (p10 0.0000, p90 0.0000) (n = 10); |S| 65000-81920: 0.0000 (p10 0.0000, p90 0.0000) (n = 1). (ii) by matched-token position in S, pooled f*(τ_K) same K / median δ_K: positions 0-8191: 0.0000 / 0.007 (n = 159,471); positions 8192-32767: 0.0000 / 0.042 (n = 87,894); positions 32768-65535: 0.0000 / 0.135 (n = 78,711); positions 65536-81920: 0.0000 / 0.041 (n = 8,628).
(ii) is the long-context figure — whether agreement at a re-rendered position depends on how deep in the
sender's context the token sat — and its bins are cut at this family's own RoPE boundary, not at entry
0035's YaRN midpoint.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through this pair's own
k = 1 mapper: median f*(τ_K) = 0.7626 (p10 0.5963, p90 0.9212), f*(τ_V) = 0.8522 (p10 0.7520, p90 0.9322); against the
same edges the transfer arm sits beyond the DEGRADES edge. Cross/same median-δ ratio K / V: 11.1 (p10 2.6, p90 81.1) /
18.6 (p10 4.0, p90 128.6). Bridge R² (A5 across the handoff; not control 4, which does not exist here): same K
0.9094 (p10 0.7631, p90 0.9760), same V 0.8912 (p10 0.7216, p90 0.9678), cross K 0.5798 (p10 0.4991, p90 0.6177), cross V 0.2579 (p10 0.2050, p90 0.2953).

**Beside entry 0036, and NOT pooled with it.** 0036 measured
35 handoffs of 35 registered on
qwen3-0.6b-to-1.7b with the receiver pushed to 81,920 positions by static YaRN
(`{"factor": 2.5, "original_max_position_embeddings": 32768, "rope_type": "yarn"}`), at τ_K = 0.3186, and reported median f*(τ_K)
0.0000 (p10 0.0000, p90 0.0000). This cell measured 32 handoffs on llama3.2-3b-to-llama3.1-8b with **nothing scaled**, at
τ_K = 0.2861, and reported 0.0000 (p10 0.0000, p90 0.0000). **The two numbers are stated side by side and are not
comparable as numbers**: different models, different tokenizers and therefore different handoff sets,
different mappers and therefore different τ, and — the point entry 0050 registered — one receiver is
scaled past its pretraining window and the other is not. Nothing here supports, refutes or moves H-E9L,
and no figure from the two cells is averaged, pooled or differenced.

**What this establishes, stated narrowly.** On meta-llama/Llama-3.1-8B re-rendering 32 real SWE-bench
`composio_swekit` handoffs whose longer side runs 32,769–81,920 tokens under
this pair's own tokenizer, at a receiver inside its native window throughout, with 0019's alignment and
0023's per-token rule at this pair's own τ, the same-model oracle removal fraction is as stated above (read
per entry 0058: not a bound on real selective recompute in either direction).
**Not established:** any hypothesis cell — this entry moves none and carries no `verdict:` line; anything
about the 4 handoffs above 81,920 or the 4 with an empty
receiver prompt; anything about the 0 unscored registered handoffs (none); any achievable recompute
scheme (0058); anything about a scaled receiver, which this cell does not contain; one pair, one
direction, one mapper, one alignment method; generation quality after reuse.

e7-manifest-sha256: 371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094

prior-entries-sha256: 75a47a51de6eb84ae4f3a91da0393bb99775868930242af35926fd31962e1399

### 0059 — 2026-10-08 — E9 summarizer enforcement: the τ recomputation tolerance registered for a cross-platform recompute (1e-9 → 1e-7 in the check's units); no rule, τ, band, score, handoff or cell change

**What this is, and when.** After E-TRUNC's FULL level ran (2026-10-08, registered by 0055; `results/e9t-full/report.json`
complete, 35 of 35 scored, the home mirror fingerprint-verified) and BEFORE any figure of it is stated. 0023 registers that
`summarize_e9` re-derives τ from the archived mapper and "recomputes it under the pin and refuses on disagreement (1e-9)" (ledger line 1308); the constant
behind that sentence is `_TAU_TOL` in `summarize_e9.py`, applied as |a − b| ≤ tol · max(1, |a|, |b|), so for τ < 1 it is an
absolute gap. The home side of this run is the operator's Mac mini (arm64), as it was for 0051. Under that constant the
summarizer refused FULL on τ_V alone: `E9 SUMMARY REFUSED: config tau_V 0.4867056499055992 != recomputed 0.48670564617346357`. This entry registers the tolerance for that check as a judgment, with the
measurement it rests on — the move 0028 made for the keep-subset re-score. It is enforcement of 0023, not a change to anything
0023 registers about the rule, τ, the band or the cells.

**Measured: five renderings of the same arithmetic.** `--calibrate-tau` under the pin `063f4023fdde…` on the same
mapper bytes (`2fd05c333156…` / `cd6a8d939b36…`), the same E8 report
(`5c4e70a097c2…`) and the same archived `results/mapper/qwen3-0.6b-to-1.7b/r2.json` — read on the box as the LF object committed at the pin
(`99177e9c8950…`) and at home as its CRLF checkout rendering (`18d2276f28e9…`, the sha 0023 pins at ledger line
1294; the LF bytes with CRLF line ends, derived here); files under `results/e9t-full/calibration*/` with their
`platform.json`; "gap" is the check's own distance to the config float.

| rendering | τ_K | gap | τ_V | gap |
|---|---|---|---|---|
| **config (registered; Windows x86 at 0023)** | `0.3186442653116294` | — | `0.4867056499055992` | — |
| x86 Linux, 13 threads (the box, torch 2.11.0+cu128 CPU path) | `0.31864426521157985` | 1.0e-10 | `0.48670564997852195` | 7.3e-11 |
| x86 Linux, 1 thread (the box) | `0.3186442652698682` | 4.2e-11 | `0.4867056503322168` | 4.3e-10 |
| arm64 macOS, 1 thread (the Mac mini) | `0.3186442649443352` | 3.7e-10 | `0.48670564617346357` | 3.7e-09 |
| arm64 macOS, 8 threads (the Mac mini) | `0.3186442649443352` | 3.7e-10 | `0.48670564617346357` | 3.7e-09 |
| arm64 macOS, the live `calibration/tau.json` the summarizer checks | `0.3186442649443352` | 3.7e-10 | `0.48670564617346357` | 3.7e-09 |

Every x86 rendering sits within 1e-9 (worst 4.3e-10) and the two x86 renderings differ from each other, so the registered
floats are one x86 rendering among several, not a property of the mapper. The arm64 renderings are identical at 1 and 8 threads
(deterministic, not thread-order jitter) and sit 3.7e-09 from the config on V. τ_agent_K is read from the E8 report with no
arithmetic and is identical everywhere (gap 0). The second-family cell (0051, `llama3.2-3b-to-llama3.1-8b`) passed on this same machine with gaps
K 2.6e-10 / V 1.9e-11 / agent_K 0 — under 1e-9 by magnitude, not by design.

**Registered check (replaces the 1e-9 for the recomputation).** The recorded calibration's and the config's τ_K, τ_V and τ_agent_K
must each reproduce the recomputed value within **1e-07** in `_close`'s units; a gap beyond refuses the summary, as before.
1e-07 is three orders below the four decimals this ledger states τ to (0023: τ_K 0.3186, τ_V 0.4867) and 27× the
worst gap measured above (3.7e-09). **The τ every reading uses remains the config's registered float**; the recomputation is a
check that the archived mapper still yields it, and no figure, f*, cell or verdict depends on the recomputed value, so nothing can
move by this entry. `summarize_e9` now records the gap and the platform it was measured on in `summary.json`
(`calibration.tau_recompute`) and prints them, as 0028 made it print the re-score jitter. **Measured by `summarize_e9` on FULL
under this check** (`results/e9t-full/summary.json` `62a6b69947b7…`, written on arm64 Darwin,
numpy 2.5.3): gaps to the config K 3.7e-10, V 3.7e-09,
agent_K 0; to the recorded calibration K 0,
V 0. The summary passed; its figures enter by their own entry (0057), never by this one.

**What this does NOT touch.** 0023's per-token judgment "judged to 1e-9 relative" (ledger line 1277) — a
different check, on the f* statistic, unchanged; the 1e-6 cross-checks of the held-out R² against the archived `r2.json` and E8 arm
(a) (`_TOL`), unchanged; τ_K, τ_V, τ_agent_K and every τ ladder; the rule section; the bands; every verdict and cell (H-E9 0029,
H-E9L 0036, 0038, the Llama cells 0044/0053/0051); 0050's sentence that its config "this config agrees with it at 1e-9" (ledger line
3638), which the measurement above confirms at full precision. `verdict:` lines: none.

**Lesson, stated once.** A registered float check is a rendering of the platform that produced it (learnings 2026-10-08, the
coverage-sha and `r2.json` CRLF pins are the same lesson in bytes); an enforcement constant that must hold on a second home
platform is registered with the renderings it was measured on, as here.

prior-entries-sha256: 64e1c6bad066f8a961256b227594d6b1338c922334094d6fe91b9023f41a1a5a
