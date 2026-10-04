# Feedback disposition and claim limits

This review covers the seven proposed upstream changes and their retained A100/H100
evidence. It does not close a ledger admission decision or certify the live Overleaf
manuscript. The original reviews remain in `docs/2026-09-30-review-response-map.md`.
No new PR, human signature, or experiment is implied by this record.

Upstream entry 0045 now records the per-token correction. [Issue #7](https://github.com/hossainpazooki/linear-ceiling/issues/7)
removes the submission's expired numbers-freeze clause and specifies the remaining camera-ready
review, including calibration refits and further control checks. This record does not close that issue.

## Cache-injection feedback

| Feedback | Disposition and evidence |
|---|---|
| Use archived matches and an actual assembled cache | Implemented in `exp/cache-behavior` (merged as PR #14, registered as entry 0047); the pilot completed all 35 original long handoffs. Matched states include one-token blocks and the final receiver token. Gaps read earlier reused states. |
| Score recorded continuations instead of extraction questions | Implemented. The pilot scored 8,908 positions; the first response token is shared conditioning and unscored. This measures prediction sensitivity on fixed text, not coding accuracy. |
| Add a size-matched random control beside the scramble | Implemented. K/V perturbation norms are matched separately per token/layer/head. The cyclic control permutes matched states and relocates keys; it is a distinct, non-norm-matched control. Neither is a quality threshold. |
| Rotate cached keys under YaRN | Correct only for the same fixed schedule/amplitude. The driver undoes source rotation and applies destination rotation, retaining amplitude once. This avoids extra long-position phase rounding in the single-angle implementation. CPU rotation checks and the H100 archive bridge passed. |
| Explain Transformers 4.57 versus 5.x | 4.57.6 remains an isolated historical-pilot pin; no original rationale was recorded. The new run uses pinned 5.17.0 for every arm and checks current K/V means against the archived values. This does not prove arbitrary cross-version cache compatibility. |
| Include oracle or CacheBlend repair arms | Deferred to preserve scope. No repair-budget result is claimed. Optional implementation is called oracle-ranked recomputation; selecting by archived errors is not a CacheBlend implementation. |
| Record Lead A/Lead B review with two approvals | The dated review is prepared under `docs/reviews/`; approvals are still pending. Lead A arithmetic reproduces and refutes the universal-token claim. Lead B confirms separate forwards by source inspection; planted-error sensitivity remains unevaluated. Ritvik's Llama reproduction is not approval of this Qwen review. |
| Verify exceedance counts | Rechecked 9,047 / 10,336 / 30,701 above the key tolerance for native-short / scaled-short / long. The first two cells reuse the same handoffs. A zero removal fraction is a mean condition, not tokenwise agreement. |

## Reviewer concerns and the smallest supported claims

| Concern | Supported statement and remaining limit |
|---|---|
| W1: behavior is unmeasured | The H100 follow-up (the pilot recorded in ledger entry 0047) supplies fixed-text prediction measurements; its figures are withheld here until the run is admitted under docs/2026-10-03-co-author-run-admission.md or the registered operator run lands (entry 0049). It does not validate the mapper tolerance against task success, free generation, or a repair budget. |
| W2: length is confounded | The original native/YaRN comparison controls configuration on the same texts. Short and long cohorts still contain different handoffs. No causal length claim; paired truncation remains unrun. The four-case seam pilot is exploratory and does not replace it. |
| W3: means hide tails | Keep tail fractions beside means. CPU tail/deletion diagnostics are not achievable repair. New attention covers only the last 32 receiver queries; matched mass and conditional error are reported. It does not establish why reuse works or a causal mechanism. |
| W4: sender versus receiver length | State sender contexts of 34,974–80,111 tokens and receiver prompts of 3,433–25,073 tokens for the H100 cohort. Do not call these 80K-token receiver prompts or evidence of repeated handoff accumulation. |
| W5: corollary applied to medians | Per-token upper bounds cannot be replaced by bin medians. Remove the claim that the displayed medians predict a zero fraction. Bin means permit a descriptive decomposition; they do not prove the corollary's premises. |
| W6: YaRN bound overreach | Orthogonality preserves the form of a fixed-query bound. Query norms, variance factors and attention can change with configuration. The numerical bridge is an empirical check, not a proof that the same tolerance preserves behavior. |
| W7: narrow model/map coverage | The A100 extension measured same-model Qwen3-4B and SmolLM3-3B on the original 25/35 texts. Key fractions were zero on 60/60 and 59/60 handoffs respectively at the common Qwen reference. This is not cross-model transfer, a model-specific quality calibration, or replication across independent workloads. |
| W8: zero at a loose reference | State the registered result beside tolerance sensitivity and the tested map's failures. Avoid “reuse works,” “no recomputation needed,” and universal cross-model ceilings. The map and calibration are specific baselines. |
| Practical cost and prefix reuse | Describe f* as oracle token removal with a retained-token denominator. It is not a general lower bound on full-cache repair (reviewer's position; the registered reading of f* as an oracle lower bound for two stated reasons, 0023/0027, stands — entry 0054). Different prompts do not imply zero shared prefix; no achieved H100 serving speedup was measured. |
| Template/footer and unrun RL appendix | These remain camera-ready source edits, not changes in the seven code branches. Use the workshop's final requirements when updating the submitted source; drop or clearly separate unrun RL work. No compliance claim is made here. |

The new H100 outputs remain in `~/Desktop/Carryover-evidence/cache-behavior`; the
execution report SHA-256 is
`7320fdeb69e61f789c6c9ae64b624b8a4b8ebe8581d1a1c3b42aa1aeac8638ad`.
The `exp/cache-behavior` runbook records execution pins and controls. A100 figures
come from its verified summary and per-handoff records, described by the separate
`exp/a100-analysis` change. Historical pilot aggregates whose raw outputs were
deleted are background, not newly verified experimental evidence.
