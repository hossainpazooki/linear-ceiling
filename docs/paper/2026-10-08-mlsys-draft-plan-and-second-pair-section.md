# MLSys 2027 draft — the delta from the submitted camera-ready, and the second-pair section drafted for approval

**Date:** 2026-10-08 · **Status:** plan + draft paragraphs, operator-side. Nothing here is manuscript text until the
operator approves it paragraph by paragraph (the 2026-10-04 shape: paragraph, then "Changes, and why" with entry:line
per figure). Every figure below carries its ledger line; none is typed from memory. Line numbers are those of
`ledger/ledger.md` at `0741fdd` (0051 appended).

**Target format** (MLSys 2027's CFP page still says "details … not announced"; MLSys 2026's rules are the proxy): two
columns, **up to 10 pages not including references**, the MLSys 2025 style files, double-blind for the research track
(no names, affiliations, repo names, dataset handles or artifact links in the text — the anonymity denylist
`a6a746d` applies), artifact evaluation voluntary. The 2026 deadline was Oct 30 20:00 UTC; 2027's dates page says
**Oct 30 2026 12:00 PDT** (= 19:00 UTC).

## 1. The delta, by section (what the camera-ready `6c706bef…` has, what the MLSys draft needs)

| where | camera-ready | MLSys draft | source |
|---|---|---|---|
| Abstract, §1, Conclusion | "three receiver models from two families"; "across the tested models" | **four receivers from three families and two source→receiver pairs**, each pair at its own calibrated tolerance; the second pair's long cell at a native receiver | 0044:2947, 0051:3874 |
| §2 / Limitations (App. A) | "cross-model transfer uses a single model pair and a single calibration size on the long cohort" | "two model pairs; the second calibration size on the long cohort is still unrun" (review §6.2) | 0034 (n = 420 refit), 0044:2971, 0051:3891 |
| App. A, lower-bound sentence | "not a general lower bound … because practical recomputation can propagate errors" | conclusion stands; the **reason** becomes App. D's denominator (0058); "oracle removal fraction" wording throughout | 0058 (whole entry); review §6.1 |
| App. D | "not an achievable recomputation or runtime cost" | stands, now citing the registered reading | 0058 |
| Table 5 caption | "4 exceed 81,920, and 4 have empty receiver prompts" | "4 more exceed 81,920, and 4 others — also over 81,920 — have empty receiver prompts and are excluded for that reason" | review §6.3 (raw records: all four empty-R handoffs have \|S\| 89,296–284,742) |
| Tables 3, 7, App. C, App. F provenance | pilot figures without the 0056 provenance sentence | cite the **registered operator runs** 0048 (same-model extension) and 0049 (cache behaviour) instead; the 0056 clause becomes unnecessary; App. F's three 4th-decimal differences take 0049's values | 0048, 0049; review §2 |
| §3 "still pending" sentences (two) | Condition 1 "still open" | delete; 0054 discharged it | 0054 |
| App. B, Table 4 | Qwen E8 blocks only | add the second pair's k = 1 block (registered 10-sequence arm (b) and the all-sequence amendment) | 0040:2539, 0053:3540, 3559 |
| **new §4.x "A second source→receiver pair"** | absent | the section drafted in §2 below; one table | 0039, 0042, 0044, 0050, 0051, 0053 |
| Related work / E-TRUNC | — | if 0057 lands before the deadline, one paragraph in §4 (length vs. handoff identity); otherwise one future-work sentence with 0055's two limitations | 0055, 0057 (staged) |
| Lean | no claim | no claim (`lake build` has not run on an operator machine) | CLAUDE.md rule |

Page budget: the camera-ready's main text is ~4 pages in the NeurIPS one-column style; the MLSys two-column 10-page
limit leaves room for the second-pair section (~0.75 page with its table), the moved App. C controls (~0.5 page) and
E-TRUNC if it lands. Appendices D–F stay appendices.

## 2. The second-pair section, paragraph by paragraph (for approval)

Working title: **4.x A second source→receiver pair: Llama-3.2-3B → Llama-3.1-8B.** Placement: after the same-model
extension (Table 7's receivers), before App. references; the table replaces nothing.

### P1 — why a second pair, and what is held fixed

> The Qwen3 results concern one source→receiver pair, one direction and one mapper. To test whether the zero median is a
> property of that pair, we registered a second pair in a different model family before any fit: Llama-3.2-3B as the
> source and Llama-3.1-8B as the receiver, a matched-KV pair (8 key–value heads × 128 head dimension on both sides), so
> the same k = 1 mapper and the same per-token rule apply unchanged. Every tolerance for this pair is its own: τ_K is
> 1 − R²_K of the pair's k = 1 map on held-out generic text, 0.2861 (Qwen3: 0.3186), and τ_V = 0.5289. Nothing from the
> two pairs is pooled: the same token cap selects a different set of handoffs under each tokenizer, so the pairs are
> compared in prose, never averaged.

Changes, and why: the pair, matched-KV premise and "registered before any fit" — 0039:2379 (heading) and the
registration paragraph (matched-KV 8 × 128: 0039:2404, 2473); τ_K = 1 − 0.7139 = 0.2861 and τ_V = 0.5289 —
0042:2666–2667, restated 0044:2942 (τ_K) / 2950 (τ_V) and 0051:3870 / 3878; "never pooled … different tokenizer selects a
different set" — 0044:2957–2958. Qwen3's τ_K = 0.3186 is the paper's own (§3 and Table 6 — NOT Table 1, which carries
no τ; skeptic 2026-10-08). No figure is new to the paper's reader except 0.2861 / 0.5289.

### P2 — the short cell (the registered verdict cell)

> On the 28 handoffs whose sender and receiver prompts both fit 32,768 Llama-3 tokens, the pre-registered hypothesis
> H-E9F — the same-model claim of H-E9 on this pair — **held**: the median oracle removal fraction f*(τ_K) over
> handoffs is 0.0000 (p10 0.0000, p90 0.0000; 28 scored of 28 registered), against the pre-registered edges HOLDS ≤ 0.15
> and DEGRADES ≥ 0.5. The cross-model arm through the pair's own k = 1 map sits beyond the DEGRADES edge: median
> f*(τ_K) = 0.7317 (p10 0.6074, p90 0.8516), f*(τ_V) = 0.8148. As with Qwen3, individual tokens exceed τ_K (11.3 % of the
> 169,437 matched tokens) while every handoff's mean sits under it; the largest per-handoff mean is 0.2860 against
> τ_K = 0.2861.

Changes, and why: "28 scored of 28", median 0.0000 (0, 0) — 0044:2947; "both fit 32,768" — 0044:2874, 2977; the edges
HOLDS ≤ 0.15 / DEGRADES ≥ 0.5 — 0044:2942–2943; H-E9F HELD — the `verdict:` line 0044:2986; cross arm 0.7317 / 0.8148 —
0044:2971; the per-token tail 11.27 % → "11.3 %" and the maximum mean 0.2860 — 0045:3088–3092 (`results/e9f/tail.json`
recomputed 2026-10-08 by the skeptic: 169,437 tokens, 0.1127 over τ_K, max handoff mean 0.286048 vs τ_K 0.286133, 28/28 under). **Operator decision:** whether to print the tail sentence (it is the honest reading under 0058)
or leave it to App. C.

### P3 — the long cell at a native receiver

> The 32 handoffs whose longer side runs 32,769–81,920 tokens were replayed on the same pair with nothing scaled: the
> receiver's own context window covers the cap, so this cell has no YaRN configuration and no configuration bridge;
> instead, the recorded rotary parameters of every dump are checked against the loaded model and against each other
> within each model role. This cell was registered as descriptive — it carries no hypothesis and is not pooled with the
> Qwen3 long cohort, whose receiver was pushed past its pretraining window. Its median f*(τ_K) over 32 handoffs is
> 0.0000 (p10 0.0000, p90 0.0000); by sender length, the median is 0.0000 in each of the three |S| bins (21, 10 and 1
> handoffs); the cross arm's median is 0.7626 (p10 0.5963, p90 0.9212). Beside the Qwen3 long cohort's 0.0000 this is a
> second zero on a different receiver — one scaled past its pretraining window, one not — stated side by side and not
> compared as a number: different models, tokenizers, handoff sets and tolerances.

Changes, and why: 32 handoffs, floor/cap "32,769–81,920" — 0051:3844, 3908; native receiver, no rope/bridge, the two
RoPE controls, "cannot move H-E9L, never pooled" — 0050 (registration) and 0051:3832 (heading); median 0.0000 over 32 —
0051:3874; length profile (i) with n = 21 / 10 / 1 — 0051:3884–3885; cross arm 0.7626 — 0051:3891; the closing sentence
now follows 0051:3896–3905 ("stated side by side and are not comparable as numbers … not averaged, pooled or differenced")
instead of asserting an equivalence the entry withholds (skeptic 2026-10-08).

### P4 — content shift for the pair's map (goes to App. B beside Table 4)

> For this pair the k = 1 map's held-out R² on generic text is 0.7139 (K) / 0.4711 (V); on the registered 10 agent
> sequences it is 0.7311 / 0.4599 (drop −0.0172 / +0.0111, both HOLDS), and on all 50 agent sequences 0.6979 / 0.4137
> (drop +0.0160 / +0.0573, HOLDS / UNRESOLVED, bootstrap 95 % [+0.0052, +0.0267] / [+0.0410, +0.0740]). The apparent
> inversion in the 10-sequence arm (agent K R² above generic K R²; V never inverted) does not persist on all sequences.
> These figures are descriptive for this pair; H-E8's cell is Qwen3's.

Changes, and why: the k = 1 rows — 0040:2539 (registered arm) and 0053:3540 (all-sequence amendment; the intervals are
bootstrap 95 % of the drop); "the inversion does not persist" is a K-only statement — 0053:3559 (skeptic: V's agent R²
0.4599 was never above its generic 0.4711, so the draft now scopes it); "H-E8's cell is Qwen3's / never pooled" — 0039's
registration clause.

### Table (one, in §4.x)

| cohort (Llama-3.2-3B → Llama-3.1-8B) | n | τ_K | same-model f*(τ_K) median (p10, p90) | cross f*(τ_K) median (p10, p90) | source |
|---|---|---|---|---|---|
| short (sender and receiver ≤ 32,768) | 28 | 0.2861 | 0.0000 (0.0000, 0.0000) | 0.7317 (0.6074, 0.8516) | 0044:2942, 2947, 2971 |
| long (longer side 32,769–81,920, native receiver) | 32 | 0.2861 | 0.0000 (0.0000, 0.0000) | 0.7626 (0.5963, 0.9212) | 0051:3870, 3874, 3891 |

**Llama-only, by design (skeptic 2026-10-08).** The first draft restated Qwen rows beside these; that failed twice — the
paper's Table 1 is the long cohort only, its Table 2 short row is the 0038 YaRN-scaled run, not 0029's native cell, and
the paper prints no short-cohort cross figure — and a shared table is not "compared in prose or not at all" (0044:2958).
The Qwen figures stay in the paper's own tables; the caption says this pair is at its own tolerance on its own handoff
sets and is not compared with them as numbers.

### The scoping sentences, rewritten (App. A)

> The representation results replicate across four receiver models from three families and two source→receiver pairs,
> each pair at its own calibrated tolerance; prediction measurements use only Qwen3-1.7B; cross-model transfer uses
> one calibration size per pair on the long cohorts, and the larger calibration (420 sequences) was scored at a handoff
> on 8 short Qwen3 handoffs only.

Changes, and why: counts — the paper's three receivers + Llama-3.1-8B (0044); "two pairs" — 0044:2971, 0051:3891;
"420 … 8 short handoffs only" — 0034:2039, 2059 (the n = 420 map was re-scored on the 8 kept handoffs of the 25, plus the
E8 arms; "short cohort" overstated it — skeptic 2026-10-08); the paper's own App. B says it "was not run on the long cohort".

## 2b. Skeptic pass (2026-10-08, read-only `skeptic-verifier`, HEAD `0741fdd`)

Every Llama figure CONFIRMED on its line; `tail.json` and the four empty-receiver sender lengths recomputed from raw
files and CONFIRMED; nothing averaged or differenced. REFUTED and corrected above: two Qwen attributions to "the paper's
tables" (Table 1 has no τ and is long-only; Table 2's short row is the scaled run; no short cross figure printed), the
unscoped inversion (K only), "short cohort" for the n = 420 map (8 handoffs), five cites on neighbouring lines (0044 τ
2942/2950, edges 2942–2943, verdict 2986; 0051 τ_V 3878), the shared Qwen/Llama table (dropped), and P3's closing
equivalence (replaced by 0051's own wording).

## 3. What is NOT in this plan

No Lean claim; no E-TRUNC figure until 0057 is on the ledger; no cache-behaviour or extension figure beyond what 0048
and 0049 state; no sentence about "practical savings" beyond the camera-ready's; no pooled Qwen/Llama number anywhere.
The LaTeX source of the camera-ready is not in this repository (co-authors' Overleaf), so this document is the paste
source and the ledger lines are its provenance; whoever holds the source applies the delta table.
