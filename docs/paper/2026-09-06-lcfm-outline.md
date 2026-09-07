# LCFM 4-pager — outline

**Target:** Long-Context Foundation Models workshop @ NeurIPS 2026 (longcontextfm.github.io).
Deadline 2026-09-10 23:59 AoE · short paper ≤ 4 pages excluding references and appendix ·
double-blind · non-archival · concurrent submission permitted (venue facts checked at source
2026-09-06; `docs/2026-09-01-measurement-lane-evidence.md`). Topic hooks in the CFP: "Robust
evaluation" and "Long-context and long-horizon agentic foundation models"; the CFP has no
caching keyword, so the paper is framed as an evaluation of what the public agentic
long-context record can evidence, not as a caching-systems paper.

**Gate:** the numbers-freeze rule of entry 0006 (EOD 2026-09-08): a figure appears only if it
recomputes clean from `results/` through a fail-closed summarizer. Every number below carries
its entry and its freeze status. Status vocabulary: **FROZEN** (summarizer ran clean on
2026-09-06 or later), **PENDING <what>** (blocked on a named step), **NOT IN** (excluded).

**Frame (operator ruling 2026-09-06):** the paper opens with the gap map and closes with what
the record returned to it — `docs/2026-09-06-gap-map-revisited.md` is the preface's source. The
H-E7a sentence uses the **registered reading** (0018: 0.20%); the request-level reading of 0024
appears once, in Limitations, as a stated sensitivity.

**Anonymity:** no repo name, no HF dataset name, no handle, no artifact link in the submission.
Code and data availability: "released on acceptance" plus the corpus manifest's canonical sha
(a hash identifies nothing). Author list to be fixed before the anonymity check: see the team
note in the handoff index; the co-author review of 0025–0029 is owed.

---

## Title (working)

*What the public agent-trace record can and cannot evidence about long-context cache economics*

Alternatives, shorter: *Caches die in ways public agent traces cannot show* · *Three gaps, one
recording gap: agentic KV-cache economics against the public trace record*.

## Abstract (≤ 150 words, slots)

Agentic serving re-sends near-identical context every step, so cache economics dominates cost
and two events destroy the cache: a model switch mid-trajectory and compaction. We asked
whether the public agent-trace record can price either. We registered an invalidation
taxonomy with per-class measurability rules before counting, replayed **2,904 trajectories
across three suites** [0015, FROZEN], and found: switch headroom is immaterial on the
registered reading (**0.20% of input spend vs a 10% cutoff**) [0018, FROZEN]; compaction has
**zero measurable events** where it could be seen and is unmeasurable elsewhere [0015,
FROZEN]; a linear cross-model KV map fit on generic text **does not survive agent-text content
shift** [0020, 0031, FROZEN]; and at 25 real re-rendered handoffs the **same-model** KV is
inside the mapper's tolerance at every matched token while the cross-model arm is not [0029,
0032; PENDING freeze run + review]. The binding finding is a recording gap: public trace formats drop every
field cache economics needs.

## 1. Preface: three gaps, and what the record returned (≈ 0.6 page)

Source: `docs/2026-09-06-gap-map-revisited.md`, condensed to one table + one paragraph.

- The framing correction (kept): compression is cache-compatible, compaction is
  cache-destroying; the literature blurs them.
- The three gaps as named on 2026-08-26, each with its one-line verdict (the revisited doc's
  table, rows Gap 1–3), and the three intuitions with theirs.
- The one-paragraph reversal: the gaps were assumed to be accounting gaps; the replay says
  they are recording gaps. This is the paper's claim; everything after is its evidence.

## 2. Setup (≈ 0.8 page)

- **Corpora.** SWE-bench verified submissions (trajectories from the public S3 bucket, 180
  files, first-N-of-listing subset rule recovered and recorded [0024]), tau-bench, tau2-bench.
  Trajectory unit defined before any coverage claim [0011]; coverage floor (≥ 50 trajectories
  per agent, ≥ 2 suites) MET [0011, FROZEN]. Corpus manifest: every file's sha256; canonical
  sha cited [0024].
- **Taxonomy, registered before counting** [0014]: six classes (model_switch,
  rerender_at_switch, compaction, idle_expiry, branch, edit), each with a detection rule and a
  measurability rule; NOT MEASURABLE contributes to neither numerator nor denominator, never a
  zero. One sentence on why this matters: it is the instrument that turns "nobody counted"
  into "the format cannot show it".
- **Cost model** [0007]: published cached/uncached pricing with sources and retrieval dates;
  no timestamps in any suite ⇒ every expiry-sensitive number is bracketed warm/cold, not
  measured. Tokenizer: exact where a public encoder exists, calibrated per content type
  otherwise, bias measured [0009]; exact-encoder sensitivity [0022].
- **Hidden prefix** [0012, FROZEN]: provider-reported usage on tau2-bench shows agent requests
  carry a fixed cacheable prefix of about 3,400 tokens the public trace omits (median offset
  +3,423, p10 +3,239, p90 +5,962) ⇒ every trace-only cost figure is a lower bound.
- **Pre-registration discipline, one sentence:** rules committed before runs; numbers enter
  only through a summarizer that recomputes from raw inputs and refuses on disagreement;
  entries hash-chained. (Do not spend more than three lines; reviewers can read the appendix.)

## 3. Results (≈ 1.6 pages)

### 3.1 Invalidation frequencies on the public record [0015, FROZEN]

Table (condensed from 0015's): rows = suites pooled + ALL; columns = the six classes; cells =
`events / trajectories-with-≥1 of measurable` or `n/m (N)`. Headline cells: model_switch
68 ev / 60 of 60 (+2,844 n/m); compaction 0 ev / 0 of 800 (+2,104 n/m); edit n/m (2,904).
One sentence: every observed switch is a re-render (68 of 68); no receiver ever got a
byte-identical prefix [0015, 0018].

### 3.2 H-E7a — switch headroom is not material on the registered reading [0018, 0022, FROZEN]

- Headroom at the 68 observed handoffs: byte-identical 0/68; overlap of the receiver's actual
  prompt with sender-processed content 0.988 (p10 0.972, p90 0.994); receiver prefill 7,492
  tokens (p10 3,434, p90 15,442; visible-only lower bound); headroom upper bound 88.9% of paid
  (p10 87.5%, p90 89.5%) [0018].
- The ratio, registered reading: 496,798 / 244,739,122 over 60 measurable trajectories =
  **0.20%** vs cutoff 10% [0018]; exact `o200k` moves it to 0.2210% [0022]. Numerator an upper
  bound, denominator a lower bound ⇒ true ratio lower still.
- Verdict: H-E7a NOT CONFIRMED; registered consequence: any case for cross-model KV transfer
  must rest on different models serving different requests [0015].
- Overlap null controls, one line [0024, FROZEN]: observed 0.988 vs same-family null 0.498
  vs cross-family 0.386 — the redundancy is task content, not shared vocabulary.

### 3.3 H-E7b — compaction is UNESTIMABLE [0015, FROZEN]

Two sentences. Zero events on the 800 trajectories that record per-request prompt sizes;
2,104 cannot show it. Not a claim that compaction does not occur; the format cannot evidence
it. Lane B's dollar counterfactual withdrawn as material by construction [0021]; its
descriptive count (23,365 tier boundaries over 2,904 trajectories) stays out of the 4-pager.

### 3.4 H-E8 — the linear map does not survive content shift [0020, 0031; FROZEN]

- Setup, two lines: existing k = 1 content-space mapper (fit upstream on generic text, n = 50
  sequences × 256 tokens at stride 4), scored without refit on (a) its own held-out generic
  sequences and (b) agent-trace text (one 1,024-token window per trajectory, 50 sequences,
  tau2-bench + SWE-bench stratified) [0009, 0016].
- Table, k = 1 verdict-bearing (k = 4, 8 reported): arm (a) K / V 0.6814 / 0.5133; arm (b)
  0.5629 / 0.3418; drop +0.1185 / +0.1715; band UNRESOLVED / DEGRADES [0020].
- Verdict: H-E8 NOT CONFIRMED (V fails, K in the dead band).
- **Freeze status: FROZEN 2026-09-07.** 0020's summarizer refuses under the current upstream pin (0030
  records this); entry 0031 (appended 2026-09-07) rescored the same tensors under the live pin, arm (b)
  over all 50 sequences with per-sequence spread and a seeded bootstrap; `summarize_e8 --config
  config/e8a.toml` ran clean 2026-09-07 (~10 min CPU). The 4-pager shows 0020's decided numbers and
  0031's all-sequence numbers side by side, both from that summarizer:

  | k = 1 | arm (a) generic K / V | arm (b) agent K / V | drop K / V | drop 95% K / V | band K / V |
  |---|---|---|---|---|---|
  | 0020 (last 10 agent seqs; decided) | 0.6814 / 0.5133 | 0.5629 / 0.3418 | +0.1185 / +0.1715 | — | UNRESOLVED / DEGRADES |
  | 0031 (all 50 agent seqs; descriptive) | 0.6814 / 0.5133 | 0.5708 / 0.3230 | +0.1106 / +0.1903 | [+0.1022, +0.1199] / [+0.1779, +0.2044] | UNRESOLVED / DEGRADES |

  Per-sequence agent K at k = 1: median 0.5671 (p10 0.5367, p90 0.6107) over 50 sequences [0031].
  k = 4 and k = 8 reported only, in 0031's table.

### 3.5 H-E9 — same-model KV survives a real re-render; the cross-model arm does not [0029, 0032; PENDING freeze run + co-author review]

- Setup, three lines: 68 observed composio handoffs, 25 inside the 32,768-token cap (the
  shorter half by |S|; excluded compared on the record [0025]); receiver Qwen3-1.7B re-renders
  the handoff; per-token centered deviation at LCS-matched positions; verdict statistic =
  oracle selective-recompute fraction f*(τ_K), τ_K = 0.3186 from the mapper's own held-out
  R²; HOLDS ≤ 0.15 (CacheBlend's achieved budget), DEGRADES ≥ 0.50 [0023].
- Controls [0029]: pipeline identity exactly zero; prefix-invariance max δ 0.000e+00 over
  29,391 positions; δ_null token-mean median 2.009 / 1.962 (K / V).
- Result [0029]: median f*(τ_K), same-model K = **0.0000** (p10 0.0000, p90 0.0000) over 25
  handoffs; τ ladder shows it is not vacuous (τ = 0.03: 0.1433, p90 0.5823). Cross-model arm
  through the k = 1 mapper: median f*(τ_K) = 0.9286 (p10 0.8579, p90 0.9607), beyond DEGRADES.
  Bridge R²: same K 0.9318 vs cross K 0.4557 — the cross figure lands where 0020's arm (b) put
  the same mapper on agent text.
- Verdict: H-E9 HELD, **read on a floor** (0027): oracle selection, recompute in isolation;
  "no more than the mapper, on a floor", not an achievable scheme.
- **Inclusion conditions:** entry 0032 admits E9 to the 4-pager on the same summarizer gate;
  the co-author refutation of 0025–0029 (two leads: τ-ladder sensitivity; the exactly-zero
  prefix control) lands before the freeze or the section is cut to one sentence marked
  "ongoing". **Status 2026-09-07:** 0032 appended; the co-author refutation is not recorded. **The freeze run
  REFUSED:** `summarize_e9` pins the upstream at `d5786df` (0026) and refuses because 0030's re-pin `223f469`
  changed `scripts/score_mapper.py` and added `kvt/pertoken.py`, both on E9's invoked-path list; unrecorded until
  the 2026-09-07 pick-up. Under 0032's own terms E9 does not enter the 4-pager until a `summarize_e9` run passes
  clean. Operator ruling: run it with the upstream checked out at `d5786df` (detached; the gate compares HEAD),
  or register a re-pin. The 0029 figures quoted above are the 09-04 run's, unchanged on disk.

## 4. The recording gap (≈ 0.4 page)

The paper's claim, stated once with its evidence pointers: per-step model is recorded by one
family; timestamps by none; per-request prompt sizes by one suite; the cacheable prefix by
none; compaction by none where it could be seen. Table: field × suite × recorded?. Consequence
for anyone pricing agentic caching from public traces: the numbers are bounds, and the
interesting events are structurally invisible. What a trace format would need to carry (five
fields) — one sentence each, no proposal beyond the list.

## 5. Limitations (≈ 0.3 page)

1. **Calibration size.** The mapper was fit on 10,240 tokens; the source paper calibrates on
   about 128K (12.5×). PENDING entry 0033: the k = 1 mapper refit on the existing n = 420
   dumps, E8 arms and the E9 cross arm re-scored, reported beside the n = 50 record. If 0033's
   figures are not frozen by 09-08, this limitation is stated as is.
2. **One pair, one direction** (Qwen3-0.6B → 1.7B); off-policy text for Qwen [0009].
3. **Public benchmark trajectories are single-model leaderboard runs by construction**; H-E7a
   decides what the public record evidences, not what production routers do (README scope
   reading).
4. **Request-level reading** [0024]: under a request-level denominator the same numerator
   reads 10.0012% cold / 8.60% warm; the registered reading decided the cell; both bounds push
   the true value below.
5. **Coverage**: E9 is decided on the shorter 25 of 68 handoffs [0025].
6. **Floor, not method** [0027].

## References (not counted)

Source paper (KV-transfer, no code release); CacheBlend; prefix-caching line (vLLM);
LLMLingua line; tau-bench / tau2-bench / SWE-bench; provider pricing pages with retrieval
dates [0007]. The "who's nearby" attributions of the gap map are **not cited** until the
lit-sweep verification is recorded (`docs/2026-09-06-gap-map-revisited.md`, "The attribution
footnote").

## Appendix (not counted)

A. Taxonomy detection/measurability rules verbatim [0014]. B. Cost-model parameters and
sources [0007]. C. Tokenizer calibration table [0009]. D. The pre-registration ledger: entry
list with dates and what each fixed before which run. E. E9 seam/depth profiles and the τ
ladder [0029]. F. Corpus manifest canonical sha and the SWE-bench selection rule [0024].

---

## Freeze checklist (owner: whoever holds the pen; verify, do not trust)

| figure set | summarizer | status 2026-09-07 |
|---|---|---|
| §3.1–3.3, §2 hidden prefix, §3.2 nulls | `summarize_e7`, `summarize_e7 --overlap-null --cache-aware-ratio` | FROZEN (ran clean 2026-09-06, 11 s) |
| §3.4 | `summarize_e8 --config config/e8a.toml` after `e8 --config config/e8a.toml` → 0031 | FROZEN (path restored 2026-09-07; run + summarizer ran clean 2026-09-07; 0031 appended) |
| §3.5 | `summarize_e9` → 0032 | REFUSED 2026-09-07 at upstream HEAD: E9 pin `d5786df` vs 0030's re-pin `223f469` (score_mapper.py, kvt/pertoken.py). 0032 appended. Needs: run at a detached checkout of the pin, or a re-pin entry; plus the co-author leads |
| §5.1 | 0033's summarizer | BLOCKED (found at pick-up 2026-09-07): the n = 420 TARGET dump does not exist upstream — killed 2026-08-25 at 358/420, zero bytes (upstream learnings); `append_0033.py` refuses on it by design. Operator ruling needed: re-dump (~2 h CPU, minutes on a GPU) and amend 0033's "pre-existing" prose, or drop §5.1 from the freeze |

## Page budget

Preface 0.6 · Setup 0.8 · Results 1.6 · Recording gap 0.4 · Limitations 0.3 · Abstract/title
0.3 = 4.0. If over: cut §3.3 to one sentence, fold §3.2's null controls into a footnote, move
the E9 controls to Appendix E.
