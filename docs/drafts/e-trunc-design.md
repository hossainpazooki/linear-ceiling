# E-TRUNC — length isolation by head truncation of the sender context on the same handoffs (design; NO entry number)

**Date:** 2026-09-30 · **HEAD at write:** `118d08e` · **Last entry:** 0044 *(2026-10-04: last entry 0054; **0055 is allocated
to this design's registration**, `docs/drafts/append_0055.py` staged — the only allocator is `docs/drafts/README.md`; 0052,
the seed's number, went to the second family's E8 amendment the same day)* ·
**Status:** design; registration STAGED 2026-10-04, unappended, unrun. Answers reviewer weakness W2 (`docs/2026-09-30-review-response-map.md`).
Thresholds: ruled 2026-10-04, quoted verbatim in section 10. Target: MLSys 2027.

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
| L32-native | S[−32,768:] | **native** receiver (0029's) | optional — the only cell where native vs YaRN can be compared on the same tokens; in scope only if the native-context verdict's exclusion rule does not cover it — ruling 3 (section 10): taken as "include it, keep R under YaRN, and state so", **deferred to its own pre-prefill amendment**: the instrument cannot yet dump one handoff under two RoPE schedules (`e9.dump_handoff` applies `[e9.rope]` to all three dumps; `summarize_e9` enforces per-role spec identity), and 0017/0019's rule — over-cap handoffs are "EXCLUDED and counted, never truncated" — makes the cell descriptive-only in any case |

Receiver R is unchanged in every cell (the same prompt, same configuration within a row). The YaRN cells share one
receiver prefill per handoff.

## 3. Matched subset

- Alignment is re-run per level (the aligner sees S'). Tokens matched under **every** level form the common subset
  M_∩; δ is compared on M_∩ only. Report |M_∩| / |M_FULL| per handoff and pooled, **before** any verdict is read —
  shrinkage is this design's weak point (seed F3), and a common subset with **|M_∩| < 2,000 tokens** voids the
  handoff for the comparison (ruling 2, section 10: the absolute floor is the gate; the ratio |M_∩| / |M_FULL| is
  stated per handoff and pooled and gates nothing — the 2026-10-04 CPU pre-check in section 10 is why).
- The short cohort is never pooled in. A handoff with |S| ≤ L is identical at that level and FULL; it still counts.

## 4. Statistics (per handoff on M_∩, paired across levels)

Mean δ_K; p(τ_K) (fraction of tokens over τ_K); f*(τ_K) and f*(0.03); seam-bin 16+ pooled mean and median (0025's bins,
`seam_distance_left`); the sender-position profile re-binned on p_S'. Bootstrap as 0025's unless re-registered. V
alongside, verdict-bearing for nothing (0023's convention).

## 5. Pre-registered reading

- If the far-from-seam level at L32 — the pooled **median** δ_K over M_∩ in the 16+ bin of FULL's causal seam
  frame — lies within **±0.005 absolute** (ruling 1, section 10) of 0038's scaled-short far-from-seam median
  (0.0381, 0038:2361) — the same receiver configuration, matched by this design — the residual short↔long gap reads
  as **length**. Both reference medians are READ from `results/e9s/compare.json` and `results/e9l/summary.json` by
  the summarizer, never typed. Caveat the entry states: M_∩ sits at late sender positions, while the two references
  were pooled over full matched sets; FULL's own 16+ median on M_∩ is stated beside L32's so the within-handoff
  paired move is visible.
- If it stays near FULL's level (0.0629, the long far-from-seam median, 0038:2362), the residual reads as **the
  handoffs** (content, not length).
- Between: unattributed; say so. No hypothesis cell moves either way (descriptive, as 0037/0038); if the operator
  wants a verdict-bearing row, the band is registered here before any prefill.

## 6. Stopping rule, partial close, release

Order by |S| descending within each level so the longest (the only ones L65 changes) are scored first; checkpoint per
(handoff, level); a stop leaves a named scored prefix per level. R1-R12 of `docs/gpu-experiment-protocol.md`; R8 backup.

## 7. Dependencies

- `config/e9l.toml` → a new config per level (`[e9.align]` on S', cap and floor as 0036's; `[e9.rope]` identical);
  `config.py` must accept a `sender_head_truncate = L` key (does not exist; build item, tested). *(BUILT 2026-10-04:
  `[e9.alignment] sender_head_truncate`, applied in `e9_align.align` after the cap/floor decision on the full
  lengths, so every level keeps 0036's included set; the record's `n_sender` stays the full |S|; `[e9.order] by =
  "n_sender_desc"`; `config/e9t-{full,l65,l49,l32}.toml`, e9l.toml byte-for-byte except the named lines; the FULL
  config carries `[e9.trunc]` — levels, floor, margin, the two reference records, bootstrap seed 52.)*
- The aligner and the per-token record writer exist (`e9.py`, `e9_pertoken.py`); the common-subset intersection and
  the paired comparison are new summarizer code (fail-closed, as `summarize_e9`), with the comparison's inputs
  sha-pinned. *(BUILT 2026-10-04: `linear_ceiling.summarize_e9_trunc` — `--shrinkage` before any prefill from the
  alignment passes; the paired comparison after each level's own `summarize_e9` passes.)*
- No upstream change. No injection.

## 8. Compute estimate (from E9L's record; probe before launch)

- E9L: 35 handoffs, 1.5-3 min each on an L40S (`docs/2026-09-10-e9l-gpu-runbook.md:139`); peak 31.56 GiB at
  |S| = 80,111 (`:127`).
- E-TRUNC adds, per handoff, up to three shorter S' prefills (L65 only for the 4 handoffs over 65,536; L49 for the
  **19** over 49,152 — recounted 2026-10-01 from `n_sender` in `results/e9l/align/coverage.json`: 0036's `s_len` bins give 18 because their edge is 50,000 and one handoff sits at 49,196; L32 for all 35) plus FULL. Each S' prefill is at most
  the FULL cost and L32 is at most 16.70 GiB / 7.3 s forward (runbook 09-13:96). **Upper bound ≈ 3× the E9L sitting,
  ≈ 4-5 h on an L40S**; realistically under 3 h because most added prefills are the short ones. Memory is bounded by
  FULL (31.56 GiB): an L40S 48 GB fits; a 20 GB slice fits only L32 and L32-native. *(2026-10-04: the registration
  computes the bound from the coverage as a token budget — FULL 3,970,435; L65 3,921,773; L49 3,596,221; L32 2,721,489;
  total 14,209,918 = **3.58×** E9-long's, since the truncated levels still re-prefill every receiver prompt and the
  cross arm — so "≈ 3×" above is an under-estimate as a bound; wall time ≈ 3.58 × 80 min ≈ 4.8 h as a bound, less in
  practice for the same reason as before.)*
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

## 10. Rulings (2026-10-04) and the CPU pre-check that informed ruling 2

Taken 2026-10-04 under the operator's direction to the session ("needs your supervision"); each quotes the option
chosen verbatim from `docs/2026-10-01-run-queue-farhan.md` §10 / the 2026-10-04 seed. **Running
`docs/drafts/append_0055.py` is the operator's ratification**; nothing is on the ledger before that.

- **Ruling 1 — margin and statistic.** The run queue's default, verbatim: "±0.005 absolute on the far-from-seam (16+)
  same-K *median*, as entry 0038 reports it" (0.0381 scaled-short, 0.0629 long); "unattributed" between the band and
  FULL's level. Why the median: 0038 reports medians and the seam-bin means run 1.6–1.8× higher (0045). The two
  levels are 0.0248 apart, five margins. Lives in `config/e9t-full.toml` `[e9.trunc] margin_abs`.
- **Ruling 2 — shrinkage gate.** NOT the run queue's default. Taken: the seed's alternative (b), verbatim, "an
  absolute floor (|M_∩| ≥ 2,000) beside the ratio", as the void gate, with the seed's recommendation clause "the
  pooled |M_∩| / |M_FULL| stated in the entry regardless of the gate". Why: the pre-check below shows the ratio
  default would void 29 of 35 handoffs. Lives in `[e9.trunc] min_common_matched`.
- **Ruling 3 — the L32-native cell.** The run queue's default, verbatim: "include it, keep R under YaRN, and state
  so". Scope check made: 0017/0019's rule excludes over-cap handoffs "never truncated", so the cell can never enter
  or speak to H-E9's native-context verdict; it is descriptive-only. **Deferred** to its own pre-prefill amendment
  because the instrument does not exist (section 2's row); 0055 registers the four YaRN cells.

**The pre-check (CPU, 2026-10-04; re-derivable by `summarize_e9_trunc --shrinkage` from the four alignment
passes; `append_0055.py` recomputes every figure in-process and states it — none is typed from here).** The 35
handoffs re-aligned under S[−65,536:], S[−49,152:], S[−32,768:] with the registered aligner, M_∩ intersected in the
FULL frame: |M_∩| / |M_FULL| per handoff has median 0.447, pooled 0.409 (158,480 of 387,508 matched tokens); 29 of 35
sit below 0.80 and all 35 below 0.90; 11 handoffs keep NOTHING (|M_∩| = 0), 4 of them because no matched token's
sender position survives S[−32,768:] at all (three more keep under 0.1 % of their pairs physically; the rest lose
everything to re-matching). Diagnosis: the loss is dominated by what the truncation REMOVES — the
receiver's prompt re-renders EARLY sender content, and the fraction of FULL pairs whose sender position lies inside
S[−32,768:] ("survivable") has median 0.503 — with aligner re-matching losing more than the removal on 10 handoffs
(up to 0.42 of |M_FULL| beyond it; median re-matching loss 0.000). Under |M_∩| ≥ 2,000, 21 of 35 handoffs (154,620
common tokens) enter the comparison; under ratio ≥ 0.80, 6. (Figures from `summarize_e9_trunc --shrinkage`
2026-10-04 on the four alignment passes; the entry restates them from an in-process run.) Consequence for the paper: "length"
here means causal-prefix length on the tokens the receiver re-renders from the LATE part of S; the entry says so.
The design's section 1 premise ("tail truncation changes nothing for any matched token") is pinned by
`tests/test_e9_trunc.py`; the aligner's instability is what section 3 reports, not an assumption.
