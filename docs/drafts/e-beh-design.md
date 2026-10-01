# E-BEH — behavioral check of same-model KV reuse at a handoff (design for registration; NO entry number)

**Date:** 2026-09-30 · **HEAD at write:** `118d08e` · **Last entry:** 0044 (next free 0047; this doc allocates
nothing — `docs/drafts/README.md` is the only allocator) · **Status:** design, unregistered, unrun. Answers reviewer
weakness W1 (`docs/2026-09-30-review-response-map.md`). Every threshold below is `??? (operator)`; nothing here may run
with a placeholder. Target: MLSys 2027 (deadline Oct 30 2026 12:00 PDT).

**Precedent on the ledger.** 0023:1367-1370 registers a `[STRETCH]` partial-prefill experiment "own entry before
anything runs … needs injection code upstream and a task; it is the experiment that would make f* an achieved number
rather than an oracle floor." E-BEH is that experiment's first half (the continuation measure) with the task delta
replaced by teacher-forced divergence, because the recorded continuation exists and a task harness does not.

## 1. Question

Does reusing the receiver's own K/V for matched tokens (the f* = 0 reading, 0023:1275-1281) change what the receiver
predicts on the continuation that was actually recorded, relative to a fresh prefill of R — and by how much relative
to a size-matched random perturbation?

## 2. Substrate

- **Handoffs:** the 35 long handoffs of 0035 / 0036 (`results/e9l/align/coverage.json` `run_order`), receiver
  Qwen3-1.7B under 0036's YaRN configuration (`config/e9l.toml` `[e9.rope]`). The 25 short handoffs form a
  **separate cell** if run at all (Condition 1, 0032, still open; short-half results stay out of registered verdicts).
  Never pooled.
- **Continuation C:** the receiver's recorded response text following prompt R in the trajectory. The traces carry
  it (`e7_swe.py` reads LangChain `LLMResult.generations`; the E9 handoff record does **not** carry it — an extractor
  is a build item). State in the entry: the recorded text was produced by a proprietary model (the handoffs are
  Claude 3.5 Sonnet ↔ o1-mini switches, fact-check brief invariant), so this measures the representation effect on a
  held-fixed continuation, not generation quality of the replay model. Cap C at `??? (operator)` tokens; record the
  cap and the per-handoff |C|.
- **Greedy-continuation arm:** secondary, only if injection lands; not verdict-bearing in the first registration.

## 3. Arms (per handoff; same R, same C, same model and dtype throughout)

| arm | cache for matched tokens M | seams / unmatched | reads as |
|---|---|---|---|
| FRESH | receiver's own prefill of R | — | the reference |
| REUSE-ALL | receiver's own K/V at p_S(t) (from a prefill of S), re-rotated to p_R(t); V unrotated (0023's content-space convention) | prefilled fresh, in order, attending to the reused K/V | f* = 0 taken literally |
| REUSE-ORACLE-τ | as REUSE-ALL, then recompute the k = ⌈n·f*(τ)⌉ highest-δ_K tokens **in situ** (recompute reads reused neighbours) for τ ∈ {0.1, 0.03} | as above | the achievable version of the oracle, not the oracle — say so (0023:1278-1281 reason 2) |
| CACHEBLEND-10 / -20 | as REUSE-ALL, then recompute the top 10 % / 20 % by δ_K in situ | as above | the CacheBlend rule in this paper's units (no numeric comparison to their figure — different units and selection rule) |
| NULL | matched K/V replaced by the fresh K/V plus a random perturbation whose per-layer-head δ equals the matched set's measured δ (seeded via `linear_ceiling.rng.make_rng`) | as above | is the measured deviation special, or just its size? |

Own recompute (FRESH, run twice) is the control arm: its KL and top-1 disagreement must be exactly zero under the
registered determinism settings, or the run refuses (identity control, as 0023's identity record).

## 4. Statistics (fixed before any data is loaded)

- Per continuation token: KL(p_FRESH ‖ p_ARM) over the vocabulary at the teacher-forced position; top-1 agreement
  (argmax equal). Per handoff: mean KL, p90 KL, top-1 agreement rate. Over handoffs: median and (p10, p90) of each;
  paired bootstrap over handoffs, seed and reps as 0025's (seed 25, 2000 reps) unless re-registered.
- Reported beside, never instead of: f*(τ_K), δ_K mean for the same handoff (from the E9L record), |C|.

## 5. Verdict (proposal for ruling — numbers are placeholders)

- HOLDS-B if median top-1 agreement (REUSE-ALL) ≥ `??? (operator; seed proposes 0.95)` **and** median mean-KL
  (REUSE-ALL) ≤ NULL's median mean-KL minus `??? (operator)`.
- DEGRADES-B if median top-1 agreement (REUSE-ALL) < `??? (operator; seed proposes 0.90)`.
- UNRESOLVED-B between. The band words are new (`-B` suffix) so `ledger_check.VERDICTS` must learn them or the
  entry must reuse an existing band with its own hypothesis row; ruling needed.
- What it changes in the paper: the sentence "No downstream-quality number is claimed" is retired **only** by the
  entry that reports one. Until then it stands.

## 6. Stopping rule and partial close

- Order: `run_order` of 0036 (|S| ascending). Checkpoint after each handoff (atomic write, as 0043 registers for the
  Llama driver). If stopped early, the report names the scored prefix and the unscored tail; a prefix of fewer than
  `??? (operator)` handoffs reports no verdict. The pull/verify/delete and release rules are R5-R7 of
  `docs/gpu-experiment-protocol.md`; R8 backup to a Hub dataset before the entry.

## 7. Dependencies (none exist today)

1. **Cache injection on the receiver side.** Upstream `kvt/cache.py` already has `build_cache` and
   `forward_with_cache` (read-only from here; pinned by ancestry in `UPSTREAM.md`). What is missing: constructing
   the mixed cache (reused K/V at p_S re-rotated to p_R for M, fresh for the rest) for a Qwen3 GQA layout
   `[28 layers, 8 KV heads]` under YaRN, and in-situ recompute of a chosen token subset. This is the splice the 09-21
   brief named; it must be pinned by an entry before it runs (0023:1367).
2. **Continuation extractor** from `traces/` (gitignored, manifest-pinned — `e7_manifest check` first) into the
   handoff record, with its sha in the entry.
3. **Determinism settings** registered: same attention backend as 0026's re-pin (SDPA), fp32 forward, `logits_to_keep`
   unset for the continuation.
4. **Card.** The S prefill of the longest included handoff (|S| = 80,111) peaked at **31.56 GiB** on an L40S under
   this configuration (`docs/2026-09-10-e9l-gpu-runbook.md:127`); the continuation forwards add a cache of |R| + |C|
   and are small beside it. A 20 GB slice does not fit (it fits only T ≤ 32,768 at 16.70 GiB, runbook 09-13:96); a
   3g.40gb slice (39.5 GiB usable, 0026:1561) is marginal; an L40S 48 GB or larger fits.

## 8. Compute estimate (derived from E9L's record; verify on the box with a probe before launch, R2)

- The E9L sitting scored 35 handoffs at **1.5-3 min per handoff** on an L40S (`docs/2026-09-10-e9l-gpu-runbook.md:139`),
  i.e. one S prefill + one R prefill + scoring per handoff — about 1.5 h for the cell.
- E-BEH per handoff = the same S and R prefills (to harvest reused and fresh K/V) + 6 continuation forwards
  (FRESH, REUSE-ALL, two ORACLE-τ, two CACHEBLEND) + 1 NULL + in-situ recompute passes of ≤ 20 % of |M| tokens. Each
  continuation forward is a |C|-token decode-style pass over a |R|-length cache (|R| median 11,462, p90 19,853 for
  the 35 — `results/e9l/summary.json`, not on the ledger) and costs seconds. **Upper bound: ~2× the E9L sitting,
  ≈ 3 h L40S**, dominated by the two prefills. No dumps need to be kept beyond the per-token logits summaries
  (KL and argmax per position, float32, ≈ |C| × 8 B per arm), so the R5/R6 pull is small.
- If kept S dumps are wanted for re-scoring at home: 114,688 B per token per dump (0025:1535) → ≈ 9 GB per 80K
  handoff; the keep subset of 0036 (3 handoffs) is the precedent.

## 9. What would refute the design before it runs (pre-mortem)

- The recorded continuation is not in the trace for some of the 35 (LangChain node missing): coverage rule needed
  (exclude and count, as 0019's cap exclusions).
- Teacher-forced KL on a proprietary model's text measures something the replay model finds unlikely under both
  arms; the NULL arm and the FRESH-vs-FRESH identity are what make the number interpretable — both are mandatory.
- In-situ recompute of a subset under GQA + YaRN with a mixed cache has no existing code path; a correctness probe
  (recompute ALL tokens in situ must reproduce FRESH bit-for-bit under the pinned backend) is the gate before any
  arm runs.
