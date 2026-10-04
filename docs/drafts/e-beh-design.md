# E-BEH — next-token sensitivity to same-model KV reuse (design; NO entry number)

**Original draft:** 2026-09-30 at `118d08e`. **Update:** 2026-10-01, before a registered E-BEH run.
**Status:** design, unregistered, unrun. This update corrects interpretation and narrows the first
run; it does not retroactively register the cache-injection pilot. Entry numbers are allocated
only by `docs/drafts/README.md`. Answers reviewer W1 (`docs/2026-09-30-review-response-map.md`).
The original draft targeted MLSys 2027; the focused experiment could also inform the accepted
LCFM paper without requiring the other experiments in the MLSys queue.

**Subsequent fork follow-up:** the separate `exp/cache-behavior` change completed a
35-handoff H100 comparison with archived matches, fixed continuations and perturbation
controls. Its freeze/run record states the exact scope; it is descriptive and was not
admitted as a registered upstream E-BEH result. No repair-budget arms were run.

**Precedent.** Entry 0023's `[STRETCH]` proposal called for practical cache injection with a
separate registration. This design tests predictions from an assembled cache. It does not turn
the representation statistic `f*` into an achieved repair cost or a task-quality measurement.

## 1. Question and scope

When the receiver actually reads the sender's same-model KV states at the archived matched
positions, how much do its next-token distributions change relative to a fresh receiver cache?
The first run compares **FRESH and REUSE-ALL**, with correctness controls. Repair variants and
perturbation comparisons are optional follow-ups, not dependencies for interpreting this contrast.

## 2. Fixed inputs

- **Handoffs:** the 35 long handoffs of 0035/0036, preserving the archived IDs and order, replayed through
  Qwen3-1.7B with the fixed YaRN settings in `config/e9l.toml`. Use the archived alignment pairs
  as `M`; do not introduce the pilot's 32-token minimum, question wrapper, or a new alignment.
  The 25 short handoffs remain a separate optional cell, subject to Condition 1's admission rule.
- **Continuation C:** the recorded receiver response following R, extracted from the pinned
  trajectory. The original response came from a proprietary model, not the replayed Qwen model.
  Pin the extractor, tokens, source node, maximum length, and missing/short-response rule before
  launch. Retain the input hashes and the number of available and scored tokens per handoff.
- **Scoring alignment:** construct the cache for **all of R**, including every token in M. Feed
  `C[0]` as the first conditioning token, then score predictions for `C[1:]` under the same
  teacher-forced history in each arm. `C[0]` is not scored. This avoids recomputing the final
  receiver token merely to obtain its logits, which would silently remove it from reused M.
  A continuation of fewer than two tokens supplies no score; report it under the fixed coverage
  rule. The cap includes the unscored conditioning token.

## 3. Core arms and construction

| Arm | Matched tokens M | Unmatched receiver tokens |
|---|---|---|
| FRESH | Receiver prefill of R | Same prefill |
| REUSE-ALL | Copy same-model KV from S at p_S and move keys to p_R | Compute gaps in receiver order, attending to the cache assembled so far |

This is block-wise cache construction, not replacing states in an otherwise fully fresh cache.
Later gaps and continuation tokens can depend on earlier reused states. The sender cache is
assumed available; record any source-cache build cost separately from reconstruction timing.
Do not report a production speedup from diagnostic timings alone.

**Position correction.** Both S and R must use the same fixed YaRN schedule and amplitude.
With cached key `K_S = a_S R_S(p_S) k`, relocation is
`K_R = (a_R/a_S) R_R(p_R) R_S(p_S)^T K_S`. Only when schedules and amplitudes match does this
reduce to rotation by `p_R - p_S` using that model's scaled `inv_freq`. Do not apply YaRN's
amplitude a second time. Reject an unsupported schedule/configuration mismatch rather than
silently treating a native cache as a YaRN cache. Values are copied without rotary correction.

**Correctness controls before expansion:** repeat the fresh path; compare no-reuse/full-fresh
construction with ordinary fresh prefill; check exact-prefix reuse; and check relocated keys
against direct destination rotation under the fixed schedule. Pin dtype, backend, model revision,
package versions, and numerical acceptance tolerances before the run. Record actual errors.
Exact repeats may be bitwise equal; chunking, backend, and Transformers-version bridges need
declared finite-precision tolerances, not an assumption of bitwise identity. A failed control
stops expansion; changing its tolerance after seeing experimental results is not allowed.

## 4. Statistics and interpretation

- Per scored token: `KL(p_FRESH || p_REUSE)` over the vocabulary and top-1 agreement. Compute
  probability reductions in a pinned numerical precision and keep the per-token results.
- Per handoff: mean and p90 KL, top-1 agreement rate, matched-token coverage, scored |C|, and the
  archived `delta_K` mean and `f*(tau_K)`. Use `e7_stats` for the reported quantile convention.
- Across handoffs: median and p10/p90; retain handoff IDs and trajectory IDs. Freeze the bootstrap
  unit, seed, and resample count in the registration; repeated handoffs from one trajectory are
  not independent trajectories. No pooling of hardware replicas or short/long cohorts.

These measurements test **prediction sensitivity on fixed text**. Top-1 agreement is not coding
task success, and KL is not an answer-quality score. Even a small measured change does not
establish unchanged greedy continuations, sampled outcomes, or agent success. The first run is
descriptive: the earlier suggested 0.95/0.90 HOLDS-B bands have no validated quality meaning and
are withdrawn from this proposal. No new verdict words or hypothesis row are needed.

## 5. Optional contrasts, only if separately included before launch

- **Oracle-ranked recomputation:** remove selected tokens from the copied blocks so they are
  computed against the assembled cache. Choose the selection using the archived token-average
  `delta_K`, either at the archived tau-ladder counts or a fixed 10%/20% budget. Selection still
  uses the fresh reference, even though the recomputation itself is executable. These are not
  CacheBlend implementations; do not label them CACHEBLEND or claim a deployable selector.
- **Norm-matched random perturbation:** compare actual cache differences with perturbations of
  matched magnitude. Specify K and V separately, per token/layer/KV head, the coordinate basis,
  the perturbation location in the construction, and a seed through `make_rng`. Use pure
  rotation when expressing K differences in content space. This can test whether direction or
  placement matters beyond error magnitude. It is not required to interpret fresh-vs-reuse KL,
  and doing better than a random perturbation is not an acceptable-quality threshold.
- A position scramble is a separate disruption control. Name whether positions within blocks
  or the blocks themselves are permuted; do not describe one as the other.

The recorded pilot's per-example outputs were deleted. Its retained aggregates are exploratory
background, not verified observations in this new cell; new runs preserve their own records.

## 6. Registration, resources, and stopping

The separate implementation and runbook must pass the controls before the full cell is launched.
Before any experimental prefill, commit the fixed input manifest, continuation coverage rule,
cap, arms, controls/tolerances, software pin, run order, checkpoint format, and partial-close
rule. Operator approval and the numbered registration remain pending. No placeholder permits a
run, and a preparation/probe result is not a registered E-BEH finding.

The old longest-S prefill (80,111 tokens) peaked at **31.56 GiB** on an L40S. That is one measured
prefill, not a memory bound for simultaneous sender/fresh/assembled caches or retained logits.
A **40 GB slice is marginal**. Prefer **one A100 80 GB or H100 80 GB** to reduce memory friction;
H100 is not scientifically necessary. A 48 GB or 40 GB alternative needs a successful probe
of the largest actual construction and scoring case with the intended cache lifetimes.
Synchronize CUDA around measured intervals; MPS-only synchronization does not time CUDA work.

Do not reserve a 24-hour experiment on the assumption that the previous approximate three-hour
estimate is an upper bound. Probe memory and time with the actual port, then estimate the core
two-arm run. Reuse verified work rather than repeatedly collecting the same fresh baselines.
The proposed port scores the largest sender first as a retained memory-probe case, then the
remaining handoffs in archive order; freeze that explicit execution order before launch.
Checkpoint per handoff; a stopped run reports the exact scored subset and why it stopped, not
an inferred full-cell outcome. Retain per-token scores, controls, configuration and source hashes,
and enough selected logits/cache evidence for the registered verification. Apply R5–R8 to the
new outputs. Passing this experiment would still leave coding-task quality unmeasured.
