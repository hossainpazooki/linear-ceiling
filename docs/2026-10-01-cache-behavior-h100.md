# H100 cache-reuse follow-up: results and scope

All 35 original long Qwen handoffs completed on one H100 PCIe 80 GB, with zero
exclusions and 8,908 scored continuation positions. This is a descriptive fork
follow-up, not an admitted upstream E-BEH result or a new registered verdict.
The [execution freeze](2026-10-01-cache-behavior-freeze.json) predates inference;
the allocated hardware predates that freeze. The freeze and numerical rules remain
unchanged. Execution used commit `9a18ce73af8655361dfb7c4f201a871a073958e6`.

## What was measured

Qwen3-1.7B reads receiver prompts assembled from sender KV at the exact archived
matched positions. Gaps are computed against the assembled cache. Both prompts
use the same static YaRN-2.5 configuration, float32 and SDPA. Sender contexts are
34,974–80,111 tokens; receiver prompts are 3,433–25,073 tokens.

All arms receive the same recorded proprietary-model response. Its first token is
conditioning and unscored; predictions for the following tokens are compared with
fresh-cache predictions. Each row below reports the median across handoffs, with
p10/p90 in parentheses. Handoffs have equal weight; they are not GPU replicas or
independent token samples. Quantiles use the repository's `e7_stats` convention.

| Candidate cache | Mean KL, nats (p10, p90) | Top-1 agreement, % (p10, p90) |
|---|---:|---:|
| Reused sender states | 0.1424 (0.0802, 0.1900) | 90.20 (85.49, 92.16) |
| Norm-matched random perturbation | 11.2982 (9.2594, 13.5359) | 4.71 (1.96, 9.80) |
| Cyclic permutation of matched states | 0.2826 (0.1795, 0.3569) | 85.49 (80.39, 89.02) |

KL is `KL(fresh || candidate)`. The random control matches K/V perturbation norms
separately per token, layer and KV head. The cyclic control permutes matched K/V
states and relocates keys to their destination positions. Its perturbation norms
are not matched to reuse. No oracle-ranked repair or CacheBlend arm was run.

Reuse produces measurable prediction changes, with lower median divergence than
these two controls. **90.20% agreement is not 90.20% task accuracy**, and no quality
acceptance threshold was set. The result does not validate the paper's mapper
tolerance as a quality threshold or establish unchanged free generation or speedup.

Fresh attention was observed only at the last 32 receiver queries, at every layer
and query head with GQA mapping. Median handoff mean attention mass on matched
tokens is 41.00%; mass on the archived high-error tail is 8.85%. Matched mass and
conditional error are retained beside weighted error. These observations combine
fresh attention with archived errors; they do not establish a causal mechanism or
verify Proposition 4's assumptions along the fresh-to-reused attention path.

## Controls and retained evidence

- The largest-sender probe was retained, not rerun for the cohort. Identical fresh
  repeat had zero logit error; the prefix-copy maximum was 0.00014114 against the
  frozen 0.0005 limit. All 35 current-runtime/archived K/V mean checks passed.
- CPU re-summarization reproduced the remote summary byte-for-byte. A separate
  NumPy calculation checked the first handoff's four-position vocabulary-logit
  witness. Per-token arrays, aggregates and attention-mass bounds were checked.
- 82 server/input/output/log files matched the downloaded bytes. The full record
  is under `~/Desktop/Carryover-evidence/cache-behavior`: `run/report.json`, per-case
  NPZ files, `run/summary.json`, inputs, traces, runtime pins and verification logs.
  These new outputs have not been published to a public dataset. Full KV tensors
  were not retained. The runbook contains the CPU re-summarization command.
- Peak allocated memory was 24.95 GiB. The allocator retried after allocation
  failures and the run exited 0 without changing settings. Reserved memory is
  distinct from allocated memory; this does not establish a 40 GB fit.

Report SHA-256:
`7320fdeb69e61f789c6c9ae64b624b8a4b8ebe8581d1a1c3b42aa1aeac8638ad`.
Input-manifest SHA-256:
`9a6f2923d3beda90cebde009ba80a12c5363c43a440fc19a356d6b3f11d4e2dc`.
The report records hashes for the measured source, configuration and per-case data;
the later documentation update does not change those measured bytes.
