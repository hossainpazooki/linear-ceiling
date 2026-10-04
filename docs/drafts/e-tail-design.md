# E-TAIL — tail and attention-weighted deviation (design; NO entry number)

**Original draft:** 2026-09-30 at `118d08e`. **Update:** 2026-10-01, after the CPU Part A analysis
and before any registered Part B run. **Part A:** implemented at `0a51275`; its numerical
publication/admission follows the corrective-entry process. **Part B:** design, unregistered,
unrun, descriptive. This update allocates no entry and changes no historical result or verdict.
It addresses W3 and supplies context for W4/W5 (`docs/2026-09-30-review-response-map.md`).

**Subsequent fork follow-up:** `exp/cache-behavior` collected fresh attention at the
last 32 receiver queries for all 35 long handoffs on an H100. This bounded descriptive
slice is complete; an all-query or registered upstream Part B run remains unrun.

**Units.** `delta` is squared cache error divided by centered receiver variance, not a percentage
of token error. Its token mean equals `1 - R^2` under the matching head/layer aggregation,
subject to the archived floating-point reduction tolerance.

## Part A — archived records; already computed, do not rerun GPU baselines

Inputs are the hash-checked score/per-token/alignment files for E9, E9s, and E9l. Keep their
25/25/35 handoff cells separate; the first two reuse the same texts under different receiver
configurations. Short-cell admission remains subject to Condition 1.

`src/linear_ceiling/e9_tail.py` now runs the existing summary verification before reporting:

1. Maximum token deviation and fractions above the registered reference and tighter ladder.
2. Remaining-token mean after removing the largest 10%/20% of errors. This is **oracle-ranked
   deletion**, not a CacheBlend implementation or an achieved recomputation cost.
3. Pooled means and medians by causal seam distance and sender position, the native-window
   subset, and receiver prompt lengths. Means support an error-budget decomposition; medians
   do not supply the uniform token bounds assumed by the paper's seam corollary.

The proposed lower-bound evaluation from Theorem 2 is not a completed Part A result. Any later
extension must use the exact statement and its assumptions. Existing verified results can be
read without repeating prefills. New descriptive arithmetic must retain its provenance and
not be presented as a new registered verdict.

## Part B — what the fresh receiver attends to

**Question.** Are large archived representation errors concentrated on matched tokens that
receive substantial attention? This is a descriptive mechanism check beside the unweighted
mean, maximum, and behavioral fresh-vs-reuse comparison.

### Quantity, heads, and matched attention mass

Index matched tokens by their receiver positions `j`. For selected query position `i`, layer
`l`, and **query head** `h`, let `a_ij(l,h)` be the fresh receiver's causal attention weight.
Map that query head to its shared KV head `g(h)` using the
model's GQA grouping; do not treat the query-head and KV-head axes as interchangeable. Define

`w_i(l,h) = sum_{j in M, j <= i} a_ij(l,h) * delta_K(j,l,g(h))`.

Report beside it:

- matched attention mass `m_i(l,h) = sum_{j in M, j <= i} a_ij(l,h)`;
- the conditional matched-token average `w_i/m_i` when `m_i > 0`, otherwise missing/undefined;
- attention mass on tokens whose **archived token-average** `delta_K(j)` exceeds `tau_K`, so
  this tail set matches the one reported in Part A;
- the number and exact positions of sampled queries, layers, and heads, plus per-handoff
  summaries before cohort aggregation.

A small `w` can reflect little attention on M, not agreement of the reused states. Report both
mass and conditional error to distinguish them. Explicitly identify whether queries are in R
or the teacher-forced continuation. Pin query selection and aggregation before launch; sampled
queries do not represent an exhaustive all-position evaluation.

### Interpretation and relation to Proposition 4

Weights from the fresh pass are one endpoint. Proposition 4's attention-shift argument involves
attention along the path between fresh and perturbed logits, fixed queries, and head-specific
norm/variance factors. Fresh `w` alone checks neither those conditions nor a bound on output
quality. A diffuse-attention guarantee requires its stated assumptions; observing small fresh
attention-weighted error does not prove it. Reused-cache attention, if collected, is a separately
named descriptive quantity. Do not say that this analysis validates the mapper tolerance under
YaRN or certifies harmless reuse.

### Implementation and validation

Use the archived alignments and headwise error normalization. Record the same fixed YaRN
schedule/amplitude used for the measured states; any source/destination position correction
follows the conditions in `e-beh-design.md`. Preserve the query-to-KV-head mapping, causal mask,
query positions, and attention temperature when reconstructing attention weights.

Keep the ordinary SDPA forward where possible and reduce selected-query attention in chunks.
Do not ask eager attention to materialize an all-layer `[heads, |R|, |R|]` tensor and then slice
it afterward. Verify the chunked reductions and GQA mapping against a small explicit causal
attention calculation. If an eager forward replaces SDPA, bridge its states/logits at declared
finite-precision tolerances and report that backend difference; do not assume bitwise equality.

At `|R| = 19,853`, a full 16-query-head FP32 attention matrix is about 25 GB per layer. Query
chunking reduces that workspace but does not bound the model/cache/other-output peak. The old
20 GB fit and sub-hour runtime were estimates, not measurements of this path. Probe the largest
selected receiver/continuation case with the exact hook before choosing a smaller card. If
E-BEH uses an A100/H100 80 GB, collect these summaries on that same allocated GPU when practical.

### Registration and retained evidence

Part B remains optional and descriptive. No quality band or new hypothesis verdict is proposed.
Before launch, fix query selection, precision/backend, numerical checks, GQA mapping, output
schema, and stopping rule in its own registration/runbook. Save per-query reductions and masses,
configuration/input hashes, and controls rather than only final cohort means; no full attention
matrices are needed. R5–R8 still apply. A future paper can report the observed association, with
its sampling limits, without claiming that attention weighting proves unchanged behavior.
