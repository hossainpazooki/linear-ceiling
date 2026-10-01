# E-TAIL — tail and attention-weighted deviation (design; NO entry number)

**Date:** 2026-09-30 · **HEAD at write:** `118d08e` · **Last entry:** 0044 (next free 0047; nothing allocated here) ·
**Status:** design, unregistered, unrun. Answers reviewer weakness W3 and supplies the figures W4 / W5 need
(`docs/2026-09-30-review-response-map.md`). Descriptive unless the operator registers a band (`??? (operator)`).

**Unit discipline (0023:1253-1266).** δ(t) is the token's share of the layer-head's unexplained variance in R²'s units:
its mean over tokens is 1 − R². A δ of 0.6 is not "60 % wrong". Every table below carries that sentence.

## Part A — from the archived per-token records, CPU only, no GPU

**Inputs on this machine:** `results/e9l/tokens/*.tokens.npz` (35 files; arrays `same_K`, `same_V`, `ref_K`, `ref_V`,
`cross_K`, `cross_V`, each `[|M|, 28 layers, 8 KV heads]` float32), `results/e9l/align/` (pairs → p_S, p_R, seam
distance via `e9_pertoken.seam_distance_left`), `results/e9l/summary.json` and `report.json` for the hashes the
summarizer checks. The same layout exists for `e9` and `e9s` (25 each); the short half is a **separate** table and
enters nothing registered while Condition 1 (0032) is open.

Per handoff and pooled, same-K (V alongside):

1. δ_max; p(τ) for τ ∈ {τ_K = 0.3186…, 0.1, 0.03} — the fraction of matched tokens over τ (the tail count outline v3
   §5 carries as PENDING: 7.9 % over τ_K pooled on the long half, 5.8 % on the short — **not on the ledger**; this
   is the figure the owed corrective entry would state).
2. Remaining-token mean after removing the top 10 % / 20 % of tokens by δ_K (CacheBlend's selection rule in this
   paper's units; state that CacheBlend's own number is in different units under a different rule — no numeric
   comparison).
3. Both Theorem 2 lower bounds per handoff — **the statement is not readable here** (the submitted tree is off this
   machine); the summarizer code implements whatever the entry states, verbatim, once the operator supplies it.
4. Pooled **bin means** (not only medians) by seam distance b⁻ (0025's bins) and by sender position (0036's
   `s_pos` edges 0 / 32,768 / 49,152 / 65,536), plus the exact decomposition check µ = Σ_b (n_b / n) · mean_b δ
   reproducing the recorded 1 − R² to float tolerance — the figures W5's Corollary 3 restatement needs.
5. The native-window subset (p_S < 32,768): n tokens, pooled mean and median δ_K — W4's row. (The count 284,094 of
   387,508 is already on the ledger at 0036:2206; the mean is new.)
6. |R| for the 35: median / p10 / p90 (11,462 / 7,085 / 19,853 in `summary.json`, not on the ledger) — W4's row.

**Build:** a fail-closed `summarize_e9 --tail` (or a small `e9_tail` module) that recomputes from the npz files,
re-verifies their sha against `report.json`, and refuses on drift — the same discipline as the existing summarizer
(0023:1360-1366). Its output is the only source for any of these numbers; the entry quotes the summarizer.

**Cost:** 35 × 35 MB npz on CPU; minutes.

## Part B — attention-weighted deviation (one GPU forward per handoff)

**Quantity.** For each receiver query position i and layer l, head h: w_i(l,h) = Σ_{j ∈ M} a_ij(l,h) · δ_K(j,l,h), with
a_ij the **fresh** receiver's attention weights (what the receiver actually attends to; the reused cache's own
attention is a different, post-hoc quantity — state which is used). Report per handoff: mean and p90 of w over
(i, l, h); the share of attention mass that lands on matched tokens with δ_K > τ_K; and, with per-head averaging as
0023 does for δ, a per-token attention-weighted δ. **The seed attributes this to Proposition 4's diffuse / concentrated
cases; that statement is not readable here, so the entry must quote it before the quantity is tied to it.** Report w
next to µ and δ_max, never instead of them.

**Mechanics.** One prefill of R per handoff with eager attention (`attn_implementation="eager"`,
`output_attentions=True`) is the simple path but materializes `[heads, |R|, |R|]` fp32 per layer: at the p90 |R| of
19,853 with 16 query heads that is 16 × 19,853² × 4 B ≈ 25 GB per layer — too much on one card. Instead hook each
layer's attention and compute the scores in query chunks of 2,048 (≈ 2.6 GB per chunk at p90 |R|), reducing against
δ on the fly; never store a full attention matrix. Model weights 6.41 GiB (runbook 09-13:96); the forward at
T = 19,853 is under the 16.70 GiB measured at 32,768 — a 20 GB slice suffices for Part B.

**Determinism and pin.** The same backend question as 0026: eager and SDPA differ in the last bits; the entry pins the
backend and records that δ (from the SDPA dumps) and a (from eager) come from different kernels. The receiver's K/V
under eager must match the archived dumps to a stated tolerance (identity check) or the run refuses.

**Cost:** one R prefill per handoff (seconds each; |R| p90 19,853 over the 35, `summary.json`) → **well under 1 h on any
card ≥ 20 GB**;
no dumps kept; outputs are per-handoff float summaries. R5-R8 still apply.

## Verdict

Descriptive unless registered. If the operator wants a band: a candidate is "attention-weighted mean δ_K ≤ τ_K on
every handoff" (`??? (operator)`), read beside f*, not as a replacement; it does not move H-E9L.

## What enters the paper, and when

- Part A rows 1, 2, 4, 5, 6 can be computed today and could enter the **camera-ready** (T1) **only** through a
  numbered entry — the 09-21 brief's owed corrective entry (tail counts and the per-handoff maximum) is the natural
  carrier; whether to widen it to carry the bin means and the |R| row is ruling 4 in the response map.
- Part B is T2 (MLSys) material.
- Nothing here changes "f* = 0 means the matched-set mean passes τ" — Part A is what makes the tail visible beside it.
