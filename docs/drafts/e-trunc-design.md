# E-TRUNC — length isolation by head truncation of the sender context on the same handoffs (design; NO entry number)

**Date:** 2026-09-30 · **HEAD at write:** `118d08e` · **Last entry:** 0044 (next free 0047; nothing allocated here) ·
**Status:** design, unregistered, unrun. Answers reviewer weakness W2 (`docs/2026-09-30-review-response-map.md`).
Thresholds are `??? (operator)`. Target: MLSys 2027.

**What the record already says.** 0038:2361-2362: the configuration share of the short→long far-from-seam gap is
0.4285 ((scaled − native) / (long − native)); 0036:2240 and 0037: every cross-cell difference is "length AND
configuration"; the matched cell decides nothing. The residual is unattributed because the short and long cohorts are
different handoffs. E-TRUNC varies length **within** a handoff.

## 1. The key fact that makes the design clean

Under causal attention the receiver's own K/V for token t at position p_S(t) depends only on S[:p_S(t)]. **Tail**
truncation of S changes nothing for any matched token. The length treatment is therefore **head** truncation:
S'_L = S[−L:] (the last L tokens of S), so every matched token's reused K/V is computed from a shorter causal prefix
and sits at a smaller sender position p_S'(t) = p_S(t) − (|S| − L).

## 2. Cells

| level | S' | receiver config | note |
|---|---|---|---|
| FULL | S (|S| 34,974-80,111) | 0036's YaRN | = E9L, re-run under this entry's pin (the control arm) |
| L65 | S[−65,536:] | YaRN | only handoffs with |S| > 65,536 differ from FULL (4 handoffs reach 65K-82K: 0036 `s_len` bin) |
| L49 | S[−49,152:] | YaRN | |
| L32 | S[−32,768:] | YaRN | the native cap; every sender position now < 32,768 |
| L32-native | S[−32,768:] | **native** receiver (0029's) | optional — the only cell where native vs YaRN can be compared on the same tokens; in scope only if the native-context verdict's exclusion rule does not cover it — ruling |

Receiver R is unchanged in every cell (the same prompt, same configuration within a row). The YaRN cells share one
receiver prefill per handoff.

## 3. Matched subset

- Alignment is re-run per level (the aligner sees S'). Tokens matched under **every** level form the common subset
  M_∩; δ is compared on M_∩ only. Report |M_∩| / |M_FULL| per handoff and pooled, **before** any verdict is read —
  shrinkage is this design's weak point (seed F3), and a common subset under `??? (operator)` of |M_FULL| voids the
  handoff for the comparison.
- The short cohort is never pooled in. A handoff with |S| ≤ L is identical at that level and FULL; it still counts.

## 4. Statistics (per handoff on M_∩, paired across levels)

Mean δ_K; p(τ_K) (fraction of tokens over τ_K); f*(τ_K) and f*(0.03); seam-bin 16+ pooled mean and median (0025's bins,
`seam_distance_left`); the sender-position profile re-binned on p_S'. Bootstrap as 0025's unless re-registered. V
alongside, verdict-bearing for nothing (0023's convention).

## 5. Pre-registered reading

- If the far-from-seam level at L32 lies within `??? (operator)` of 0038's scaled-short far-from-seam median
  (0.0381, 0038:2361) — the same receiver configuration, matched by this design — the residual short↔long gap reads
  as **length**.
- If it stays near FULL's level (0.0629, the long far-from-seam median, 0038:2362), the residual reads as **the
  handoffs** (content, not length).
- Between: unattributed; say so. No hypothesis cell moves either way (descriptive, as 0037/0038); if the operator
  wants a verdict-bearing row, the band is registered here before any prefill.

## 6. Stopping rule, partial close, release

Order by |S| descending within each level so the longest (the only ones L65 changes) are scored first; checkpoint per
(handoff, level); a stop leaves a named scored prefix per level. R1-R12 of `docs/gpu-experiment-protocol.md`; R8 backup.

## 7. Dependencies

- `config/e9l.toml` → a new config per level (`[e9.align]` on S', cap and floor as 0036's; `[e9.rope]` identical);
  `config.py` must accept a `sender_head_truncate = L` key (does not exist; build item, tested).
- The aligner and the per-token record writer exist (`e9.py`, `e9_pertoken.py`); the common-subset intersection and
  the paired comparison are new summarizer code (fail-closed, as `summarize_e9`), with the comparison's inputs
  sha-pinned.
- No upstream change. No injection.

## 8. Compute estimate (from E9L's record; probe before launch)

- E9L: 35 handoffs, 1.5-3 min each on an L40S (`docs/2026-09-10-e9l-gpu-runbook.md:139`); peak 31.56 GiB at
  |S| = 80,111 (`:127`).
- E-TRUNC adds, per handoff, up to three shorter S' prefills (L65 only for the 4 handoffs over 65,536; L49 for the
  **19** over 49,152 — recounted 2026-10-01 from `n_sender` in `results/e9l/align/coverage.json`: 0036's `s_len` bins give 18 because their edge is 50,000 and one handoff sits at 49,196; L32 for all 35) plus FULL. Each S' prefill is at most
  the FULL cost and L32 is at most 16.70 GiB / 7.3 s forward (runbook 09-13:96). **Upper bound ≈ 3× the E9L sitting,
  ≈ 4-5 h on an L40S**; realistically under 3 h because most added prefills are the short ones. Memory is bounded by
  FULL (31.56 GiB): an L40S 48 GB fits; a 20 GB slice fits only L32 and L32-native.
- Kept dumps: none required beyond E9L's precedent (keep subset re-registered per level if home re-scoring is wanted;
  ≈ 114,688 B per token per dump, 0025:1535).

## 9. Pre-mortem

- Alignment under head truncation may re-match different tokens (the aligner's windows shift); if |M_∩| collapses the
  design says nothing — hence the shrinkage gate in §3.
- Head truncation also removes the system prompt / early turns from S, so the reused K/V at L32 are computed without
  them: this is **the** treatment, not a confound, but the paper must say that "length" here means "causal prefix
  length", not "number of turns".
- The native cell (L32-native) changes two things at once if R is also re-prefilled natively; keep R under YaRN in
  that cell unless the ruling says otherwise, and state which.
