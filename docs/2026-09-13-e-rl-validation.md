# E-RL: what would justify retaining the cache?

This note extends the [E-RL design](2026-09-02-e-rl-design.md). It proposes
measurement corrections; it does not register an experiment or change a ledger
entry, tolerance, or verdict. E-RL remains unrun.

After a weight update, the new model reads a cache written by the old model.
The useful question is whether retaining or mapping that cache saves time while
preserving useful training behavior. [vLLM exposes this choice through
`clear_cache`](https://docs.vllm.ai/en/stable/training/async_rl/).
[PipelineRL, Section 5.1](https://arxiv.org/html/2509.19128v2#S5.SS1), already
compares retained and recomputed caches after in-flight updates. Its experiment
finds slightly greater distributional divergence with retained caches. A new
contribution needs to establish when reuse remains useful, and whether mapping
extends that range at a lower total cost than rebuilding.

## What zero recomputation means

The implemented `f_star` sorts token deviations from largest to smallest and
removes the fewest tokens needed to bring the **mean of the remaining tokens**
below the tolerance. It is not the fraction of tokens individually above that
tolerance. For deviations `[0.0, 0.6]` and tolerance `0.3186`, `f_star` is zero:
the mean is `0.3`, although one token exceeds the threshold.

This distinction occurs in the archived data. I recomputed the same-model key
deviations for `20241025_composio_swekit/django__django-10973_traj#78` from the
[E9L token record](https://huggingface.co/datasets/hossainpazooki/linear-ceiling-e9l-2026-09-10/blob/main/results/e9l/tokens/20241025_composio_swekit__django__django-10973_traj_sw78.tokens.npz)
and its [score record](https://huggingface.co/datasets/hossainpazooki/linear-ceiling-e9l-2026-09-10/blob/main/results/e9l/scores/20241025_composio_swekit__django__django-10973_traj_sw78.json).
Their SHA-256 hashes match the published report. Divide each token's squared
error by its layer/head `SST / n`, then average over heads and layers:

| Quantity | Recomputed value |
|---|---:|
| Matched tokens | 13,075 |
| Mean key deviation | 0.2023384457 |
| Tokens above the archived key tolerance, 0.3186442653 | 1,998 |
| `f_star` at that tolerance | 0.0 |
| `f_star` at 0.1 | 0.3856978967 |
| `f_star` at 0.03 | 0.9398087954 |

These are one handoff's values, not cohort medians. Zero establishes that the
average already passes this representation-error criterion. It establishes
neither tokenwise agreement nor preserved answer quality or zero engine cost.
Entry 0023 defines the remaining-token mean correctly. The descriptions in
entries 0029 and 0036 instead call `f_star` an exceedance fraction and infer
tokenwise agreement. That wording needs an append-only correction; the saved
fractions agree with the implementation of 0023.
The criterion covers matched tokens and assumes ideal selection and isolated
repair; actual recomputation can change other tokens. Also, `0.03` is about one
tenth of `0.3186`, not one thirtieth. Report absolute tolerances to avoid this
ambiguity.

## Keep the likelihood diagnostic separate from training ESS

Teacher-forcing the same greedy continuation through fresh and stale caches
isolates how the cache changes token probabilities. Report log-probability
differences and their tails. The concentration formula
`(sum(w) ** 2) / (N * sum(w ** 2))` is computable on those ratios, but greedy
continuations do not supply samples from the behavior distribution needed for
the usual importance-sampling interpretation.

For sampled rollouts, record the actual behavior probability at each generated
token, including weight version, cache state, and sampling rule. To estimate a
current-policy expectation from those samples, use current-policy probability
divided by the probability that generated the sample, with compatible support.
Compute sequence ratios in log space. Retain the mean log ratio alongside
concentration: weights `[0.01, 0.01]` and `[1.0, 1.0]` both give normalized ESS
of one, despite very different likelihood ratios. Neither statistic alone
establishes stable training.

## A comparison that can support a decision

Use identical held-out prefixes and checkpoint pairs for fresh, retained, and
mapped caches. Fit the mapper on separate sequences. Keep zero-lag and fresh
recomputation controls. Specify the checkpoint schedule before running: the
proposed anchor at step 8 with lag 40 needs checkpoint 48; an anchor at 24 needs
checkpoint 64. Saving only through step 40 cannot cover those pairs.

Report every measured lag. If an arm never fails within the tested range,
report that limit rather than inventing a crossing point; do not assume the
curve is monotone. Keep representation and rollout outcomes separate and set
their decision rules before inspecting results.

Measure cache rebuilding and mapping in the same engine, including mapping
overhead and the stated amortization of fitting cost. Then compare useful
training progress per wall-clock time at a predeclared quality criterion.
Tensor-dump timing and a small `f_star` cannot establish that benefit.

## Validation performed

The accompanying fix rejects non-finite, negative, and non-vector deviations
before `f_star` can return a plausible fraction. Valid-input arithmetic is
unchanged. Exhaustive subset selection agreed with both the old and new
implementations in 1,254 cases: all sorted vectors of lengths 1–6 over
`{0, 0.1, 0.4, 1}`, at six tolerances. The archived handoff also returned the
same fractions before and after the fix. This was CPU validation of arithmetic
and saved GPU output, not a new GPU run, a full corpus replay, or E-RL evidence.
