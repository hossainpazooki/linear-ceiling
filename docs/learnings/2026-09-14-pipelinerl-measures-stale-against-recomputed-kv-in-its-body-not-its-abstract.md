# PipelineRL measures a stale KV cache against a recomputed one in its body, not its abstract: a citation decided from the abstract misses a measured weights-axis result

kills: (nothing)
ts: 2026-09-14T09:28:12.509Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: The HTML body of PipelineRL (arXiv 2509.19128) contains "using stale KV-cache for mixed policy sequences
introduces only slightly higher divergence compared to recomputing the cache". It is a measured comparison of a
retained cache with a recomputed one after in-flight weight updates, the question the weights-axis (E-RL) design sets
out to measure. A summarized read of the same page places it in Section 5.1 beside Figure 7, as a KL divergence against
"PipelineRL with KV cache recomputed"; that location is from the summary, not from this capture. The paper should cite
this result, not describe the weights axis as unmeasured.
basis: `curl -sL https://arxiv.org/html/2509.19128 | grep -o "using stale KV-cache for mixed policy sequences introduces
  only slightly higher divergence[^.]*"` printed `using stale KV-cache for mixed policy sequences introduces only slightly
  higher divergence compared to recomputing the cache`.
re-verify: curl -sL https://arxiv.org/html/2509.19128 | grep -o "using stale KV-cache for mixed policy sequences introduces only slightly higher divergence[^.]*" | head -1   # the sentence above
