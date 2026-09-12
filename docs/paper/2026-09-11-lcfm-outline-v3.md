# LCFM 4-pager — outline v3 (the recompute floor for non-prefix KV reuse at long-horizon agent handoffs)

**Supersedes** `2026-09-10-lcfm-outline-v2.md` as the writing outline, under the 2026-09-11 seed
(`2026-09-11-seed-lcfm-v3.md`, read against the ledger at `d0b91db`; corrections listed at the end). v2 stays the
record of the two-axis frame and is not edited. Every cell, table, verdict and scope line is v2's; what changes is
the frame, the order, and where the ladder and the related work sit.

**Target:** Long-Context Foundation Models workshop @ NeurIPS 2026. The deadline on record, **2026-09-11 11:59
UTC**, had passed when this outline was written (21:30Z). Whether v2 was submitted at that deadline, or the deadline
moved, is not recorded in the repo; this outline serves either a revision of a submitted v2 or a first submission,
and the writing lead states which at the top of the draft. ≤ 4 pages excluding references and appendix;
double-blind; non-archival; concurrent submission permitted. CFP hooks unchanged: "Long-context and long-horizon
agentic foundation models" and "Robust evaluation". No caching keyword in the CFP; under this frame the paper is an
evaluation of non-prefix KV reuse at long-context agent boundaries, placed in the serving literature, not a serving
paper.

**Gate (0006's provenance rule, 0032/0035's terms), unchanged:** a figure appears only if it recomputes clean through
a fail-closed summarizer and is on the ledger by a numbered entry. Every number carries its entry and one of
**FROZEN**, **PENDING <what>**, **NOT IN**.

**Anonymity, unchanged:** no repo name, HF dataset, handle or artifact link. The literature table's identifiers
appear only in the references.

**The two conditions that decide what this paper contains (not the framing), status 2026-09-11:**
1. **E9 (0029) stays in only if the co-author refutation of 0025–0029 is recorded.** Status: **NOT discharged.** The
   co-author's PR (merged 2026-09-10) records a computational re-verification of two sampled handoffs; the 09-10
   brief on it states this does not by itself discharge condition 1, and whether it counts is the operator's ruling.
   Until ruled, §5.1 is written and marked cond. 1 as in v2.
2. **E9-long (0036) enters only from a passing `summarize_e9 --config config/e9l.toml`.** Status: **satisfied** (v2).

**Framing ruling this outline assumes (seed §7.1–7.2, operator to confirm):** the pivot, and E-RL as one
future-work sentence. The hybrid fallback — v2's frame with §2 below inserted and seed title 3 — needs no new
numbers either; only §1, the abstract and the title differ.

---

## Title

*Carryover: The Recompute Floor for Non-Prefix KV Reuse at Long-Horizon Agent Handoffs* (seed candidate 1).

Alternatives: seed candidates 2 and 3. Not proposed: any title that headlines the cross arm.

## Abstract (≤ 150 words; slots; "floor" before "zero")

Prefix caching reuses a long-horizon agent's KV cache only under a byte-identical prefix, and a handoff between
agents breaks that by construction: the receiver re-renders its prompt from the sender's content, so the same tokens
reappear at new positions. Position-independent caching repairs this by recomputing a subset of tokens; every
published evaluation of it uses compositions built for the benchmark. We measure the quantity those methods repair —
the residual after position correction — on real handoffs from public agent trajectories, as an **oracle recompute
floor** at a tolerance set by a cross-model linear map's own shortfall. At **25 SWE-bench handoffs up to 32K
tokens** [0029, FROZEN, cond. 1] and **35 handoffs of 35K–80K tokens under a YaRN-extended receiver** [0036, FROZEN]
the floor is **zero on every handoff**: no matched token needs recompute at the tolerance, while a linear cross-model
map through the same tokens sits past the degrade edge [0029, 0036]. Length leaves the floor at zero and spends most
of the headroom under it [0029, 0036]. No downstream-quality number is claimed.

## 1. Non-prefix reuse at a handoff (≈ 0.6 page)

The seed's §2 prose, with the corrections below applied. Paragraph by paragraph:

- **The event.** Prefix caching's condition; the handoff breaks it by construction; "re-render" defined once here
  as the mechanism verb. On the record: 2,904 public trajectories, 68 mid-trajectory switches on 60 measurable
  trajectories, 0 of 68 byte-identical, median overlap 0.988 (p10 0.972, p90 0.994) [0015/0018, FROZEN]. "The
  content relocates; it does not go missing."
- **The name.** Position-independent caching (PIC): reuse an independently cached chunk at any position, repair the
  cross-context loss by recomputing a subset of tokens (§2). Every method in that line is evaluated on compositions
  built for the benchmark; none measures the loss at a real handoff inside a long-horizon trajectory. **The
  "none at this length" clause is dropped** (seed §6 records that no PIC paper's maximum context was read); it
  returns only if the lookup in the freeze checklist is done and supports it.
- **The quantity.** Receiver's own K for a shared token at its receiver position vs at its sender position, content
  space (rotary encoding removed; V unrotated) [0023]. The free step of every PIC method (rotating a cached key to
  its new position) is therefore already taken; what is measured is the residual selective recompute exists to
  repair. f*(τ): the fraction of matched tokens whose centered deviation exceeds τ = the fraction an oracle would
  recompute. τ_K = 0.3186, the k = 1 cross-model map's own held-out shortfall (1 − R²) [0016/0020, 0023]. HOLDS
  f* ≤ 0.15, anchored to the 10–15% of high-deviation tokens CacheBlend recomputes to recover full-prefill quality
  under non-prefix reuse [0023]; **DEGRADES f* ≥ 0.50 is the operator's stated judgment, not a citation [0023]** —
  say so, a PIC reviewer will ask. **f* is a floor** [0027]: oracle selection, recompute in isolation; CacheBlend's
  budget is an *achieved* figure, so HOLDS reads "the oracle floor of the re-render's repair is no more than the
  budget a same-model reuse the literature already spends" and never "an achievable scheme reaches it." Rule,
  tolerance and band registered before any prefill; every figure through a summarizer that refuses on disagreement
  [0023, 0028] (one sentence here; the rest in §4).
- **The claim, stated once.** On 25 real SWE-bench handoffs, sender prompts **median 25K tokens (p10 14K, p90 30K)**
  [0029], the same-model floor is zero: not one matched token of any handoff exceeds τ_K [0029, FROZEN, cond. 1].
  On 35 further handoffs of 35K–80K tokens under a receiver extended by YaRN to 81,920, zero again on every handoff,
  after a bridge control shows τ_K carries to the scaled receiver [0036, FROZEN]. **Beside the zero, the control that
  makes it a measurement:** prefix invariance max δ 0.000e+00 over 29,391 positions [0029] and over 34,974 [0036],
  pipeline identity exactly zero — the zero is not a pipeline identity. The residual is seam-local: pooled median δ
  0.236 at the seam and 0.019 **sixteen or more tokens from it** on the short half, 0.260 and 0.063 on the long
  [0029, 0036]. A linear cross-model map through the same tokens sits past DEGRADES on both halves, 0.9286 and
  0.9640, descriptive [0029, 0036]. Below the registered tolerance the floor is not vacuous: τ = 0.03 reads 0.1433
  short / 0.5255 long [0029, 0036], so length spends most of the headroom. Nothing in this paper is a
  downstream-quality number.

## 2. Related work (≈ 0.25 page; seed §3 verbatim, identifiers in references only)

- **Position-independent caching.** vLLM/SGLang prefix caching (exact prefix only); CacheBlend (non-prefix reuse,
  selective recompute); EPIC (boundary recomputation); PromptCache (position slots); KVLink, APE, MiniPIC
  (selection, encoding, engine integration); KV Packet, COMB, SemPIC (repair moved into training). All evaluated on
  retrieval or template-built compositions. KVShareArena (concurrent, posted 2026-09-09): position correction
  suffices until a query draws on several sources; unrepaired caches can fall below no cache; checkpoint-trained
  adapters lose quality across checkpoints. We measure the post-position-correction residual on real trajectories at
  14K–80K tokens, as an oracle floor, not a method.
- **Cross-model KV transfer.** C2C, LatentAlign (trained fusers/adapters); DroidSpeak (identical architectures);
  Heo et al. (closed-form per-head ridge within a family, 73–98% retention on four of six pairs, generic calibration
  text). Our cross arm is the k = 1 member of that class, fit on 50 generic sequences [0016], read on agent text,
  descriptive; its shortfall on agent text at rest is measured separately [0020, 0031, 0034].
- Citation discipline: rows at provenance S or R in the seed's table are cited for existence and one-line scope
  only; no number from them enters the paper without a full read. KVCOMM's identifier is in the repo
  (`docs/2026-09-01-measurement-lane-evidence.md`: arXiv 2510.12872) — confirm on arXiv, then cite.

## 3. Corpus: real handoffs are long-context events (≈ 0.4 page; v2 §2 compressed)

- Taxonomy registered before counting [0014]; 68 switches on 60 measurable trajectories, 0 of 68 byte-identical
  [0015, 0018, FROZEN]; headroom 0.20% of input spend on the registered reading [0018, FROZEN]; benchmark
  trajectories are single-model runs by construction (scope reading).
- **Length table:** included at 32,768: |S| median 25,460 (p10 14,269, p90 30,106); excluded for length: 52,141
  (p10 35,692, p90 147,218); |R| 6,551 vs 11,500; overlap 0.985 vs 0.989 [0025, FROZEN]. Cap ladder: 25 within
  32,768; +35 within 81,920; 4 above (147K–358K); 4 with an empty receiver prompt [0035, FROZEN as registration
  text].
- Hidden cacheable prefix: +3,423 tokens median [0012, FROZEN]; every trace-only length is a lower bound. (Footnote
  if over budget.)

## 4. Instrument (≈ 0.4 page; v2 §3, plus the ladder's definition)

- Alignment: difflib matching blocks over token ids, a floor on |M| [0019]; matched fraction |M|/|R| median 0.9344
  (p10 0.8838, p90 0.9783) [0029, FROZEN]. Three stride-1 dumps per handoff, fp32 [0026].
- Controls: pipeline identity; prefix invariance; δ_null (deranged pairing) token-mean median 2.009 / 1.962 K / V
  [0029]; for the long half, the configuration bridge and length profiles [0035].
- **The τ ladder, defined here and read in §5 beside each HOLDS:** f*(τ) at τ ∈ {0.3186, 0.10, 0.03}, descriptive
  [0025]. It is the answer to "why is the same-model tolerance a cross-model map's shortfall": the verdict is read at
  τ_K, and the ladder shows how much of that tolerance each half uses.
- Cross arm: the k = 1 content-space mapper on 50 generic sequences [0009/0016]; n = 420 calibration beside it
  [0033/0034, FROZEN].
- Pre-registration, three lines (as v2); the long half's stopping rule registered before the box was touched [0035].

## 5. The floor, measured (≈ 1.4 pages; v2 §4 with the ladder in the body)

### 5.1 Up to 32K: H-E9 HELD, on a floor [0029, 0032; FROZEN 2026-09-09; cond. 1]

- v2's table unchanged (same-model 0.0000 (0.0000, 0.0000), bootstrap [0.0000, 0.0000]; cross 0.9286 (0.8579,
  0.9607); bridge R² K 0.9318 / 0.4557). Not one matched token exceeds τ_K.
- **Ladder beside the HOLDS (moved from an aside):** τ = 0.10 → 0.0000 (p90 0.1563); τ = 0.03 → 0.1433 (p90 0.5823)
  [0029].
- Seam profile b⁻(t), pooled median δ_K: 0: 0.236 (n = 2,278) · 1: 0.127 · 2–3: 0.081 · 4–7: 0.062 · 8–15: 0.063 ·
  16+: 0.019 (n = 139,290) [0029, FROZEN]; 139,290 of 155,257 matched tokens (89.7%) sit ≥ 16 from any seam.
- Cross arm in one sentence with App. A: fit on generic text, does not hold on agent text at rest (K +0.1106 dead
  band, V +0.1903 DEGRADES at k = 1) [0020, 0031, FROZEN]; under n = 420 moves toward the floor (0.8106 vs 0.9352 on
  the 8 kept handoffs) and stays beyond DEGRADES [0034, FROZEN]. Attribution to the map, not the handoff.
- The 0027 sentence, verbatim: "no more than the mapper, on a floor."

### 5.2 35K–80K: H-E9L HELD, 35 of 35, bridge CARRIED [0036; FROZEN 2026-09-10; registration 0035]

- Setup, bridge, table, controls, position profile, |S| bins, seam profile and cross arm exactly as v2 §4.2
  (|S| 34,974–80,111, median 50,916; bridge native-vs-scaled f*(τ_K) 0.0000 on all three, bridge R² 0.8992 / 0.8821
  / 0.8932 → CARRIED; same-model 0.0000, bootstrap [0.0000, 0.0000]; cross 0.9640 (0.9043, 0.9904); prefix
  invariance 0.000e+00 over 34,974; δ_null 2.015 / 1.975; |M|/|R| median 0.9606).
- **Ladder beside the HOLDS:** τ = 0.10 → 0.0119 (p90 0.3876); τ = 0.03 → **0.5255** (p90 0.9037), against 0.0000 /
  0.1433 on the short half [0029]. Floor still zero at the registered tolerance; far less headroom under it.
- Position in the sender context (f*(τ_K) 0.0000 in every bin): 0–32K 0.038 · 32K–49K 0.131 · 49K–65K 0.162 ·
  65K–82K 0.092 (n = 4 handoffs reach it) [0036]. Seam 16+: 0.063 (n = 359,203) vs 0.019 [0029]: seam-local in
  shape, far-from-seam floor three times higher.
- Read on a floor [0027] under the scaled receiver, as v2.

## 6. Limitations (≈ 0.35 page; two new, then v2's five)

1. **No downstream-quality number.** PIC papers report task quality against full recompute; this paper reports KV
   deviation only, and generation quality after reuse is not established [0029, 0036]. The experiment that would
   turn the floor into an achieved figure is named in 0023 as `[STRETCH]` and is future work
   (`docs/2026-09-11-gpu-runs-after-the-pivot.md`).
2. **The tolerance is a cross-model anchor.** τ_K is one map's held-out shortfall; the ladder is the sensitivity
   [0029, 0036], and the DEGRADES edge is a stated judgment [0023].
3. Length and the receiver (v2 §6.1). 4. One pair, one direction, one agent family, one alignment method (v2 §6.2).
5. Floor, not method; calibration sensitivity on V under n = 420 (v2 §6.3). 6. The public record under-prices
switches (v2 §6.4). 7. Co-author refutation of 0025–0029 owed (cond. 1), until recorded.

## 7. Future work (one sentence)

The same instrument is designed for the weights axis — KV written by θ_t and read by θ_{t+k} under an async-RL
rollout — and is unregistered and unrun; no prediction is made. (E-RL design doc; App. F retained.)

## References (not counted)

v2's list minus the E-RL sources that no longer appear in the body (vLLM async docs, AReaL, Laminar, Stable
Asynchrony, LlamaRL/AIPO move to App. F's note), plus the seed §6 rows marked *cite*: Heo et al. 2608.03893;
KVShareArena 2609.10266 (concurrent); CacheBlend; EPIC; PromptCache; KVLink; APE; MiniPIC; KV Packet; COMB; SemPIC;
LinearKV (for the roster); C2C; LatentAlign; DroidSpeak; KVCOMM once confirmed. Identifiers confirmed on arXiv
before entering the .bib (seed's own rule); 2608.03893 and 2609.10266 were confirmed 2026-09-11.

## Appendix (not counted)

As v2 (A–F), with B carrying the full ladders and profiles for 5.1 and 5.2, and F the E-RL design tables.

---

## Corrections applied to the seed (review against the ledger at `d0b91db`, 2026-09-11)

| seed text | finding | applied |
|---|---|---|
| "sender prompts run 14K–30K tokens" [0029] | 0029 records |S| median 25,460 (p10 14,269, p90 30,106); a bridge handoff from the same 25 has |S| = 13,955, so the minimum is below 14K | "median 25K (p10 14K, p90 30K)" |
| "none … at prompts of the length measured here" [VERIFY] | seed §6 "Not done": no PIC paper's maximum context was read | clause dropped; checklist row |
| "0.019 sixteen tokens out" | 0.019 / 0.063 are the **16+** bin medians | "sixteen or more tokens from the seam" |
| "[CHECK] CacheBlend's achieved budget" | 0023 anchors HOLDS to CacheBlend's 10–15%; 0027 already states that figure is achieved and f* is a floor | 0027's wording used; the units lookup stays a checklist row |
| KVCOMM "identifier not confirmed" | in the repo: `docs/2026-09-01-measurement-lane-evidence.md` gives 2510.12872 | cite after one arXiv check |
| DEGRADES ≥ 0.50 cited beside 0.15 | 0023: "the operator's stated judgment, not a citation" | stated in §1 |
| (not in the seed) the zero without its control | 0029/0036 prefix-invariance 0.000e+00 is what shows the zero is not a pipeline identity | placed beside the claim in §1 |

Verified as written: 0/68, 0.988, 60 of 2,904; content space per 0023 line 24–25; τ_K = 1 − 0.6814; f* a floor
[0027]; seam and ladder figures; cross 0.9286 / 0.9640; "generation quality not established" in 0029 and 0036; mapper
on n = 50 [0016]; v2's uncited-attributions note; arXiv 2609.10266 = KVShareArena (Shi & Lou, 9 Sep 2026);
2608.03893 = Heo et al., six pairs, 73–98% on four. Not checked: Heo's per-pair R² figures (need the full text).

## Freeze checklist (verify, do not trust)

| figure set | summarizer / source | status 2026-09-11 |
|---|---|---|
| §1, §3 corpus numbers, hidden prefix, headroom | `summarize_e7` (+ `--overlap-null --cache-aware-ratio`) | FROZEN (ran clean 2026-09-06) |
| §3 length table, cap ladder | 0025's coverage comparison; 0035's registration text | FROZEN |
| §5.1 | `summarize_e9` at the detached `d5786df` upstream | FROZEN 2026-09-09; **cond. 1 open** |
| §5.1 cross-arm explanation, App. A | `summarize_e8` (e8a, e8c), `e9_rescore summarize` | FROZEN (0031, 0034) |
| §5.2 | `summarize_e9 --config config/e9l.toml` → 0036 | FROZEN 2026-09-10, two independent passes |
| §2 attributions | seed §6 table, provenance codes | cite-for-existence only at S/R; 2 identifiers confirmed |
| §1 CacheBlend units / selection rule | one read of CacheBlend | **NOT DONE** — gates the HOLDS-anchor sentence's wording |
| §1 "none at this length" | max evaluated context of CacheBlend, EPIC, KVShareArena | **NOT DONE** — clause stays out until done |
| §7 | none (no figure) | text only; `/honesty-check` on verbs before submission |

## Page budget

title/abstract 0.2 · §1 0.6 · §2 0.25 · §3 0.4 · §4 0.4 · §5 1.4 · §6 0.35 · §7 0.05 = 3.65, leaving 0.35 of slack
against v2's 4.0. If over: §3's hidden-prefix line to a footnote; §5.1 controls to App. B; §5.2's |S|-bin row and
seam profile to App. B (the position profile stays). §5.2 is in.

## Open rulings (seed §7, with this outline's recommendation)

1. Pivot (assumed here) or hybrid. 2. E-RL one sentence (assumed). 3. Of the three CHECK/VERIFY clauses: length
clause dropped, CacheBlend clause rewritten from 0027, τ_K sentence kept. 4. Cond. 1 — the operator's ruling on
whether the co-author's two-handoff re-verification discharges it; this outline treats it as open.
