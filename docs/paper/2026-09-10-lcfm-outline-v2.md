# LCFM 4-pager — outline v2 (long context central; E9 + E9-long the results; E-RL the contrasting direction)

**Supersedes** `docs/paper/2026-09-06-lcfm-outline.md` under entry 0035's paper-scope paragraph (operator ruling
2026-09-09), which supersedes 0032's space clause and keeps 0032's gate, cross-arm, coverage and co-author
conditions. Until 0035 is on the ledger this file is a draft of the re-cut; the 09-06 outline stays the record of the
earlier frame and is not edited.

**Target:** Long-Context Foundation Models workshop @ NeurIPS 2026. Deadline **2026-09-10 23:59 AoE = 2026-09-11
11:59 UTC**. ≤ 4 pages excluding references and appendix; double-blind; non-archival; concurrent submission
permitted. CFP hooks: "Long-context and long-horizon agentic foundation models" and "Robust evaluation". No caching
keyword in the CFP: the paper is an evaluation of KV reuse at long-context agent boundaries, not a serving paper.

**Gate (0006's provenance rule, 0032/0035's terms):** a figure appears only if it recomputes clean through a
fail-closed summarizer and is on the ledger by a numbered entry. Every number below carries its entry and one of:
**FROZEN** (on the ledger; summarizer ran clean 2026-09-06 or later), **PENDING <what>**, **NOT IN**.

**Anonymity:** no repo name, HF dataset, handle or artifact link. The E-RL design's named amendment author is not
quoted. "Code and data released on acceptance" plus the corpus manifest's canonical sha.

**The two conditions that decide what this paper contains (not the framing):**
1. **E9 (0029) stays in only if the co-author refutation of 0025–0029 is recorded** before submission; otherwise
   0032's consequence stands and §4 is one sentence marked ongoing. Status 2026-09-09: NOT recorded.
2. **E9-long (0036) enters only from a passing `summarize_e9 --config config/e9l.toml`**, by its own entry, with
   "n scored of 35 registered" beside every number. Status: registered (0035), run pending tonight.

---

## Title (working)

*Same weights, new positions: KV reuse at long-context agent handoffs, and the other axis*

Alternatives: *Two boundaries, one yardstick: when a long-horizon agent's KV cache stops being its own* ·
*Re-render or retrain: the two events that stale a long-horizon agent's cache*.

## Abstract (≤ 150 words; slots)

A long-horizon agent's KV cache is a function of the context that produced it and the weights that computed it.
Two structural events change one factor each: a re-rendered handoff changes the context under fixed weights; a
policy update under an in-flight rollout changes the weights under fixed context. We ask one question of both —
how many cached tokens go stale — with one statistic, the oracle selective-recompute fraction f*(τ) at a
tolerance set by a cross-model linear map's own shortfall. On the context axis we measure: at **25 real
re-rendered SWE-bench handoffs up to 32K tokens** [0029, FROZEN, cond. 1] the same-model cache needs
**zero recompute at every matched token on an oracle floor**, while a linear cross-model map through the same
tokens does not [0029]; **at 35 handoffs of 35K–80K tokens under a YaRN-extended receiver [0036, PENDING run]
the floor <reads …>**, with the deviation confined to within 16 tokens of a seam [0029]. On the weights axis we
register the measurement an async-RL engine's `clear_cache` flag needs and no engine has, and state what the
context-axis result predicts for it.

## 1. Two boundaries, one yardstick (≈ 0.6 page)

- **The object.** KV(P; θ): the cache is a function of prefix P and weights θ. A cache is "its own" when both
  factors are the ones the reader will use. Long-horizon agents break this two ways. (Framing correction kept
  from the 09-06 outline, one clause: compression is cache-compatible, compaction is cache-destroying.)
- **Context axis — the re-rendered handoff.** The receiver of a handoff rebuilds its prompt from the sender's
  content: same tokens at new positions, new tokens at the seam. Observed on the public record: 68 handoffs,
  none byte-identical [0015/0018, FROZEN]. The question is positional: does K at the new position agree with K
  at the old one?
- **Weights axis — the policy update under a rollout.** In async RL the rollout engine's cache was written by
  θ_t and read by θ_{t+k}. AReaL recomputes on interruption; Laminar calls the recompute a cost and the
  alternative a convergence risk; vLLM ships `pause_generation(mode="keep")` with a `clear_cache` flag and no
  guidance (all three quoted at source, E-RL design §1). Nobody measures the trade.
- **One yardstick.** Per matched token, the centered deviation between the two K states in the units of a
  mapper's R² (a token's share of unexplained variance, never a percent error) [0023]. A token "needs
  recompute" above τ_K = 0.3186, the k = 1 cross-model mapper's own held-out shortfall — "no worse than the
  mapper itself". f*(τ_K) = the fraction an oracle would recompute; HOLDS ≤ 0.15 (CacheBlend's achieved
  budget), DEGRADES ≥ 0.50. Registered before any prefill; hash-chained; every figure through a refusing
  summarizer (three lines, appendix D for the rest).
- **Claim, stated once.** On the context axis, same-model reuse at a real re-render is free on an oracle floor
  up to 32K [0029] and <at 35K–80K: PENDING 0036>; a linear cross-model map is not. On the weights axis the
  same instrument is registered and unrun; the paper says which way the context result bets.

## 2. Corpus: real handoffs are long-context events (≈ 0.5 page; E7 compressed)

- 2,904 public trajectories, three suites; an invalidation taxonomy registered before counting [0014]; every
  observed mid-trajectory switch is one designed critic family, 68 switches on 60 measurable trajectories, 0 of
  68 byte-identical prefixes [0015, 0018, FROZEN]. One sentence on why the public record under-prices this:
  headroom 0.20% of input spend on the registered reading [0018, FROZEN]; benchmark trajectories are
  single-model runs by construction (scope reading).
- **The length table (the long-context fact):** |S| of the 68 handoffs — included at 32,768: median 25,460
  (p10 14,269, p90 30,106); excluded for length: median 52,141 (p10 35,692, p90 147,218); |R| 6,551 vs 11,500;
  overlap with sender content 0.985 vs 0.989 [0025, FROZEN]. Cap ladder: 25 within 32,768; +35 within 81,920;
  4 above (147K–358K); 4 with an empty receiver prompt [0035, FROZEN as registration text]. Length is the
  selection variable, and it is the paper's own limitation until §4.2.
- Hidden cacheable prefix the record omits, one line: +3,423 tokens median [0012, FROZEN] — every trace-only
  length is a lower bound.

## 3. Instrument (≈ 0.5 page)

- Alignment: difflib matching blocks over token ids, a floor on |M| [0019]; matched fraction |M|/|R| median
  0.9344 (p10 0.8838, p90 0.9783) [0029, FROZEN]. Three stride-1 dumps per handoff (receiver on S, receiver on R,
  source on S), fp32 [0026].
- Controls: pipeline identity (exactly zero); prefix invariance (max δ 0.000e+00 over 29,391 positions) [0029];
  δ_null (deranged pairing) token-mean median 2.009 / 1.962 K / V [0029]; for E9-long, the configuration bridge
  (§4.2) and length profiles [0035].
- Cross arm: the k = 1 content-space mapper fit on 50 generic sequences [0009/0016]; a larger calibration
  (n = 420) reported beside it [0033/0034, FROZEN].
- Pre-registration, three lines: rules committed before runs; numbers enter only through a summarizer that
  recomputes from raw inputs and refuses on disagreement; entries hash-chained; the long half's stopping rule
  registered before the box was touched [0035].

## 4. Context axis, measured (≈ 1.3 pages)

### 4.1 Up to 32K: H-E9 HELD, read on a floor [0029, 0032; FROZEN 2026-09-09; cond. 1]

- 25 of 68 handoffs (the shorter half by |S|; coverage travels). Table (0032's clause: same-model never without
  the cross column):

  | arm | median f*(τ_K) (p10, p90) | median f*(τ_V) | bridge R² K |
  |---|---|---|---|
  | same-model, K read-out (verdict) | **0.0000** (0.0000, 0.0000); bootstrap [0.0000, 0.0000] | 0.0000 | 0.9318 |
  | cross-model through the k = 1 map (descriptive) | 0.9286 (0.8579, 0.9607) | 0.9089 | 0.4557 |

  Not one matched token of any handoff exceeds τ_K on the same-model arm. τ ladder shows it is not vacuous:
  τ = 0.10 → 0.0000 (p90 0.1563); τ = 0.03 → 0.1433 (p90 0.5823) [0029].
- **Where deviation lives (the long-context figure):** seam profile under the causal distance b⁻(t), pooled
  median δ_K by bin: 0: 0.236 (n = 2,278) · 1: 0.127 · 2–3: 0.081 · 4–7: 0.062 · 8–15: 0.063 · 16+: 0.019
  (n = 139,290) [0029, FROZEN]. The re-render perturbation is local to the seam; 139,290 of 155,257 matched tokens (89.7%) sit ≥ 16
  from any seam and agree at δ ≈ 0.02 across prefixes of 14K–30K tokens.
- Cross arm explained in one sentence with the appendix table: the map was fit on generic text and does not
  hold on agent text at rest (K +0.1106 in the dead band, V +0.1903 DEGRADES at k = 1, all 50 sequences)
  [0020, 0031, FROZEN]; under the n = 420 map the cross arm moves toward the floor (0.8106 vs 0.9352 on the 8
  kept handoffs) and stays beyond DEGRADES [0034, FROZEN]. Attribution is to the map, not the handoff.
- Read on a floor [0027]: oracle selection, recompute in isolation; "no more than the mapper, on a floor".

### 4.2 35K–80K: H-E9L [0036; PENDING tonight's run; registration 0035 FROZEN]

- Setup, three lines: the 35 handoffs excluded by the 32K cap and within 81,920 (|S| 34,974–80,111; prefill
  3,970,435 tokens); receiver and source under static YaRN factor 2.5 (window 81,920) — an upstream RoPE-spec
  change so content-space K strips exactly under the scaled rotation [0035]; same rule, τ, band, ladder,
  controls as 4.1; run order |S| ascending with a registered stopping rule; verdict on the scored prefix, "n
  scored of 35 registered", never pooled with 4.1's 25.
- **Configuration bridge, first:** native vs YaRN receiver on the same tokens (three short handoffs, (p, p)):
  median f*(τ_K) = <PENDING>; if > 0.15 the section's first sentence reads "a claim about the scaled receiver
  only" [0035 control 4].
- Table: same-model K (verdict), same V, cross K/V, bridge R²; τ ladder; bootstrap. <PENDING 0036>
- **Length profiles (the section's reason to exist):** f*(τ_K) by |S| bin (35K–50K / 50K–65K / 65K–82K) and by
  matched-token position in S (0–32K / 32K–49K / 49K–65K / 65K–82K) [0035 control 5; figures PENDING 0036].
  The question the profile answers: does agreement at a re-rendered position depend on how deep in the
  sender's context the token sat?
- If the run is partial: the unscored handoffs by id and the operator's cutoff reason, one line [0036].

## 5. Weights axis, registered direction (≈ 0.6 page; E-RL, designed and unregistered — say so)

- The question: at a weight update, is it cheaper to recompute the in-flight KV under θ_{t+k} or to continue on
  the cache θ_t wrote, and at what lag does the answer flip? The three positions in production (AReaL
  recompute; Laminar cost + convergence risk; vLLM's undecided flag), quoted.
- The instrument transfers unchanged: the same per-token δ, τ_K, band, identity/null controls and seam
  profiles (E-RL design §2), so re-render loss, mapper loss and step loss sit on one table. Statistic (A)
  f*(τ_K) over lags; statistic (B) the stale-vs-fresh importance ratio and ESS/N, the trainer's own instrument
  (Stable Asynchrony; bounds are the operator's stated judgment, no numeric anchor exists in the cited set).
- Sources and lag ladder: an own Qwen3-0.6B GRPO run with per-step checkpoints, lags 1–8 (the engine regime);
  OLMo-2 RLVR1's stride-200 checkpoints as the far tail (checked at source: 13 branches, `main` is not a lag
  point). Cells MOVED / NOT DISTINGUISHED / INVERTED / BOUNDED BY RANGE.
- **What §4 predicts, stated as a prediction, not a result:** a few optimizer steps move K far less than a size
  transfer does, so under the inherited τ identity likely reads f* ≈ 0 at engine lags (BOUNDED BY RANGE); the
  ladder and the behavioral control are registered so that outcome is falsifiable rather than vacuous (design
  Appendix A). No number in this paper. Verbs: "we propose", "designed, unregistered".

## 6. Limitations (≈ 0.3 page)

1. **Length as selection variable.** 4.1 is the shorter half; 4.2 is the long half under a scaled receiver
   that is a different function from the native one (the bridge says by how much) [0025, 0035].
2. **One pair, one direction** (Qwen3-0.6B → 1.7B); one agent family; one alignment method [0009, 0029].
3. **Floor, not method** [0027]. **Calibration size**: the E8 sentence is calibration-sensitive on V (0034:
   V's drop falls to the DEGRADES edge and reads UNRESOLVED under n = 420) [0034, FROZEN].
4. **The public record under-prices switches**: 0.20% registered reading; request-level reading 10.0012% cold
   [0024], one sentence.
5. **Co-author refutation of 0025–0029** owed at the time of writing (cond. 1).

## References (not counted)

CacheBlend; vLLM async RL docs (`pause_generation`, `clear_cache`); AReaL (NeurIPS 2025, §4.1); Laminar
(§2.3); Stable Asynchrony (ICML 2026); LlamaRL/AIPO §6; YaRN; Qwen3; tau-bench / tau2-bench / SWE-bench;
the KV-transfer source paper; provider pricing pages with retrieval dates [0007]. The gap map's "who's nearby"
attributions are **not cited** (lit sweep unrecorded).

## Appendix (not counted)

A. E8 contrast table, k = 1, 0020 and 0031 side by side, with 0034's n = 420 row. B. τ ladder, seam/depth
profiles for 4.1 and 4.2 [0029, 0036]. C. Taxonomy rules verbatim [0014]. D. The pre-registration ledger: entry
list, dates, what each fixed before which run; the stopping rule [0035]. E. Corpus manifest canonical sha and
the SWE-bench selection rule [0024]. F. E-RL design tables (cells, sources, seal shape).

---

## Freeze checklist (verify, do not trust)

| figure set | summarizer | status 2026-09-09 22:30Z |
|---|---|---|
| §2 corpus numbers, hidden prefix, headroom | `summarize_e7` (+ `--overlap-null --cache-aware-ratio`) | FROZEN (ran clean 2026-09-06) |
| §2 length table, cap ladder | 0025's coverage comparison (in `summarize_e9`); 0035's registration text | FROZEN |
| §4.1 | `summarize_e9` at the detached `d5786df` upstream | FROZEN 2026-09-09 04:12Z; **cond. 1 open** |
| §4.1 cross-arm explanation, App. A | `summarize_e8 --config config/e8a.toml`, `--config config/e8c.toml`, `e9_rescore summarize` | FROZEN (0031, 0034) |
| §4.2 | `summarize_e9 --config config/e9l.toml` → `append_0036.py` | PENDING: 0035 append → box run → pull → summary → 0036 |
| §5 | none (no figure) | text only; verbs checked by `/honesty-check` before submission |

## Page budget

§1 0.6 · §2 0.5 · §3 0.5 · §4 1.3 · §5 0.6 · §6 0.3 · title/abstract 0.2 = 4.0. If over: §5 to 0.4 by
dropping statistic (B)'s paragraph to the appendix; §2 headroom sentence to a footnote; §4.1 controls to App. B.
If §4.2 is cut (no passing summary by the writing cutoff): §4.1 grows by 0.4 with the seam profile as a figure,
and §6.1 names E9-long as the registered successor with its entry number.
