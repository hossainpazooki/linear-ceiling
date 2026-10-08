# Camera-ready evidence map: PDF claims against the ledger

**Date:** 2026-10-06 · **Status:** reconciliation record. It is not a ledger entry, not a manuscript edit, and not a
verdict. It types no new figure: every number below is quoted from the PDF or from the ledger or review record it cites.
**Branch:** `zain/camera-ready-evidence-map` at `efab85a`, which matches current upstream `main` as of the latest
check (`git ls-remote origin refs/heads/main`, 2026-10-06).

**Manuscript baseline.** `126_Carryover_The_Reuse_Margin.pdf`, an untracked file in the repo root. sha256
`be90e0af9723da82fb3e3b33b139d93376e169b3cb620e333c3d918c2874edf5`, 14 pages, pdfTeX creation date
**2026-10-04 06:16:43Z**. Title as printed: *KV Cache Drift Across Handoffs in Long-Horizon Agents* (LCFM workshop
footer). Text was extracted with pypdf, so equation and figure layout in the quotes below is approximate. Locations are
given as PDF page / section / table.

**Authority.** The ledger (`ledger/ledger.md`, cited `entry:line` against `efab85a`) and the dated review records are
the source of truth. The PDF is the baseline being checked. Where the two disagree, the disagreement is recorded here and
nothing is assumed.

**Status words.** **KEEP**: the PDF claim matches the record. **UPDATE**: the claim is contradicted by, or out of date
against, the record. **ADD**: the record supports something the PDF omits and the reader needs. **HOLD**: the change
needs a ruling, a missing artifact, or an entry before anyone edits.

## 0. Timeline that decides several rows

| when (UTC) | event | record |
|---|---|---|
| 2026-10-01 | 0045 appended: f* = 0 is a mean statement; per-token tail per cell | `ledger.md:2991` |
| 2026-10-04 06:16 | **this PDF built** | PDF metadata |
| 2026-10-04 07:40 | operator ruling: issue #7 + PR #12 discharge Condition 1 | issue #7 comment; PR #12 comment |
| 2026-10-04 08:14 | issue #7 closed with a row disposition; 0054 appended (`a2742b9`) | `ledger.md:3287` |
| 2026-10-04 08:34 | PR #12 merged (head `8100414`) | `gh pr view 12` |
| 2026-10-04 11:59 | LCFM camera-ready deadline (2026-10-03 23:59 AoE) | `docs/2026-09-30-review-response-map.md:113-114` |
| 2026-10-04 (night) | 0056 (pilot figures citable, with provenance sentence) and 0055 (E-TRUNC registered) appended | `ledger.md:3372`, `:3406` |
| after | 0053, 0050 appended; 0048 / 0049 / 0051 / 0057 staged, unappended | `docs/drafts/README.md` |

The PDF predates 0054, 0055, 0056, 0053 and 0050. Every row below that turns on those entries is UPDATE or HOLD for that
reason, not because the PDF was wrong when it was built.

## 1. Main text

| # | PDF location | PDF claim (quote / paraphrase) | Repo evidence | Status | Proposed action |
|---|---|---|---|---|---|
| 1 | p.1 Abstract | "sender histories of 35K–80K tokens and receiver prompts of 3.4K–25.1K tokens" | W4 action (`review-response-map.md:44`); 0047 scope `ledger.md:3281-3282` (34,974–80,111 / 3,433–25,073) | KEEP | — |
| 2 | p.1 Abstract | "the mean key deviation … stays within a fixed reference. At that reference, the median handoff requires no oracle token removal" | 0036 `ledger.md:2198`; 0045 mean reading `:2993-2997` | KEEP | Mean wording is correct (0045). |
| 3 | p.1 Abstract | Qwen3-4B and SmolLM3-3B "produce the same zero cohort medians" | `docs/2026-10-01-a100-analysis.md:10-15`; admissible in paper text only under 0056 `ledger.md:3378-3392` | KEEP + ADD | Figures match. Carry 0056's provenance sentence where these figures are cited (row 30). |
| 4 | p.1 Abstract | reuse gives "0.1424 nats and 90.20% top-1 agreement" | `docs/2026-10-01-cache-behavior-h100.md:25`; 0056 | KEEP + ADD | Figures match. Provenance sentence required (row 34). |
| 5 | p.1 Abstract | shifts smaller than norm-matched perturbation, "indicating that the structure of the reuse error, not just its magnitude, governs its effect" | h100 doc `:42-44` ("do not establish a causal mechanism"); 0047 scope `ledger.md:3283` ("an association, not a cause") | HOLD | "governs" reads as causal. Consider "is consistent with …"; author's call. |
| 6 | p.1 Abstract | "making cache reuse a viable alternative to recomputation" | Invariant "no downstream-quality number until an entry reports one" (`review-response-map.md:69-71`); W8 "avoid 'reuse works', 'no recomputation needed'" (`feedback-and-claims.md:36`); PDF's own App. A ("not … compute savings") | UPDATE | Practical claim beyond the evidence: no task quality, no serving cost, f* is oracle. Narrow it to representation and prediction agreement. |
| 7 | p.2 §1 | "A matched YaRN rerun checks that the results are not an artifact of the model configuration" | 0038 `ledger.md:2361-2362`: configuration accounts for 0.4285 / 0.3916 of the short-to-long gap; f*(τ_K) stays 0 under both | UPDATE | True for the τ_K result, misleading for the gap. Say it measures the configuration's share. |
| 8 | p.2 §2 | τ_K is the held-out key deviation of the reimplemented k = 1 map | 0023 τ definition `ledger.md:1283-1285`; 0040/0044 use the Llama pair's own τ (0.2861) | KEEP | — |
| 9 | p.2 §3 Corpus | 68 handoffs; 25 short (cap 32,768); 35 long (≤ 81,920) | 0035; issue #7 disposition R13 (68 = 25 + 35 + 8) | KEEP | — |
| 10 | p.3 §3 | τ_K = 0.3186, τ_V = 0.4867; bands HOLDS ≤ 0.15 / DEGRADES ≥ 0.50 | 0023; 0036 `ledger.md:2196` | KEEP | — |
| 11 | **p.3 §3, end of "Arms, controls, and pre-registration"** | "**A co-author review of the native-context verdict is still open.**" | **0054** `ledger.md:3287-3315` (Condition 1 discharged by ruling; short-cell figures citable "without the 'subject to Condition 1' qualifier"); issue #7 CLOSED 2026-10-04 08:14Z; PR #12 MERGED | **UPDATE** | Stale. Replace with the 0054 status. Do not overstate: 0054 says the review record is partial and unsigned, and the ruling accepts it as sufficient (`:3307-3309`). Issue #7's closing comment also says "the paper states that the long and scaled-short cells were recomputed by the operator only" (see Q5 / ambiguity A2). |
| 12 | p.3 §3 "Meaning of the statistic" | μ = 1 − R̄², so "f*(τ) = 0 exactly when R̄² ≥ 1 − τ … even if some tokens exceed τ" | 0045 `ledger.md:2993-3004`; Theorem 1 | KEEP | This is the 0045 mean reading, stated correctly. |
| 13 | p.3 §3 "Meaning of the statistic" | (absent) the per-token tail: how many tokens exceed τ_K | 0045 e9l `ledger.md:3009-3014`: 30,701 of 387,508 tokens (7.9%) over τ_K, on every one of 35 handoffs; per-handoff mean maximum 0.2692 (0.04947 under τ_K) | ADD | W3 asked for the tail beside the mean (`review-response-map.md:43`). One sentence citing 0045 makes "even if some tokens exceed τ" concrete. |
| 14 | p.3 §3 / p.2 Fig. 1 | f* is "oracle token removal" throughout. Intro: "how much of the cache a handoff would need to recompute" | 0023 `ledger.md:1275-1277` defines f* as removal **(recomputed exactly)**; operator on PR #12: "Changing 'recompute' to 'remove' … changes the registered operational meaning … Keep recompute" | HOLD | That ruling was on the README, not the paper. The paper's "removal" vocabulary diverges from the registered word. Rule on it together with row 37. |
| 15 | p.3 §3 "Prediction comparison" | descriptive H100 follow-up | 0047 registered the operator's run, pilot not credited (`ledger.md:3256-3264`); 0056 lets paper text cite the pilot document | KEEP + ADD | Add the 0056 provenance sentence here or in App. F (row 34). |
| 16 | p.3 Table 1 | same-model f*(τ_K) 0.0000 (0, 0), bootstrap [0, 0]; f*(τ_V) 0.0000; R²_K 0.8894, R²_V 0.8779; cross 0.9640 (0.9043, 0.9904), 0.9456 (0.9023, 0.9863), 0.4214, 0.1478 | 0036 `ledger.md:2198-2200`, `:2216-2218`. 0.8894 = 1 − 0.1106, the per-handoff mean δ_K median (0045 `:3012`), so the "head-and-layer-averaged" label agrees with Theorem 1 | KEEP | All values match. |
| 17 | p.3 Table 1 caption | "Only same-model f*(τ_K) determines the verdict … cross-model arm and R² are descriptive" | 0036 cross arm "descriptive, decides nothing" `ledger.md:2215` | KEEP | — |
| 18 | p.3 Table 1 / §4 RQ1 | (absent) the 0027 floor qualifier | 0036 `ledger.md:2211-2213` ("Read on a floor … never that an achievable scheme reaches it"); 0023 `:1281` ("Every output stating f* carries the words 'oracle lower bound' and both reasons") | HOLD | Rides on row 37. The operator's invariant "'floor' nowhere in the body" (`review-response-map.md:71`) and 0023's "every output" clause pull in different directions. Rule before editing. |
| 19 | p.4 §4 Table 2 | Qwen3-1.7B 25/35: f*(τ_K) 0/0, f*(0.1) 0.0000/0.0119, f*(0.03) 0.2930/0.5255 | 0038 `ledger.md:2343` (scaled short 0.0000 / 0.2930); 0036 `:2201` (long 0.0119 / 0.5255) | KEEP | The short row is the scaled-short cell (0038), which 0054 admits (`:3311-3312`). |
| 20 | p.4 §4 Table 2 | Qwen3-4B 0/0, 0.0007/0.0460, 0.2739/0.4979; SmolLM3-3B 0/0, 0.0000/0.0580, 0.1527/0.4529 | a100 doc `:12-15` | KEEP + ADD | Figures match. Caption needs the 0056 provenance sentence (row 30). |
| 21 | p.4 §4 "Additional models" | "one SmolLM3 long handoff has f*(τ_K) = 0.0228" | Not in either 0056 document. a100 doc `:15` gives only "34" zero of 35. The value is in `docs/provenance/2026-09-30-a100/fork-ledger-0045-0046.md:31` (0.022754…) | HOLD | 0056 admits "the two merged co-author documents". Whether the linked fork-ledger provenance copy counts is the operator's call (A3). |
| 22 | p.4 §4 RQ2 | τ = 0.1: 0.0119 K / 0.0254 V; τ = 0.03: 0.5255 / 0.5837 | 0036 `ledger.md:2201` | KEEP | — |
| 23 | p.4 §4 RQ2 | pooled median key deviation peaks after a seam; 0.0629 in the 16+ bin | 0036 `ledger.md:2203`; 0045 `:3016-3019` gives bin MEANS 1.76× the medians (0: mean 0.428 / median 0.260; 16+: 0.110 / 0.063) | ADD | 0045 `:3116-3118`: "any restatement of the workshop paper's per-token bound on these records uses the means and says so". W5 action (`review-response-map.md:45`). Put the means beside the medians in Fig. 3 or the text. |
| 24 | p.4 §4 RQ2 | "Pooled medians cannot isolate an effect of length or supply the uniform bounds of Corollary 3" | W5 (`feedback-and-claims.md:33`) | KEEP | — |
| 25 | p.4 §4 RQ2 | removing tokens within 16 positions of a seam leaves the mean above 0.03 on all 35 (median 0.1016) | a100 doc `:24-26` (0.101553); a co-author analysis of the archived e9l records | KEEP + ADD | Provenance is the a100 document, so the 0056 sentence applies here too. |
| 26 | p.4 §4 "Matched configuration comparison" | f*(0.03) 0.1433 → 0.2930; f*(τ_K) stays 0; shares 0.43 / 0.39; "descriptive rather than causal" | 0038 `ledger.md:2355`, `:2361-2362`; issue #7 disposition recomputed 0.42854 / 0.39162 | KEEP | — |
| 27 | p.4 §4 RQ2 | (absent) a within-handoff length test | 0055 registered E-TRUNC (`ledger.md:3406`), unrun; 0057 staged only (`docs/drafts/README.md`, "Staged 2026-10-04 (late)") | HOLD | Claim no E-TRUNC result (0057 is unappended and no `results/e9t*` run exists in this checkout). At most one future-work sentence saying it is registered, with 0055's two stated limitations (`ledger.md:3513-3517`). |
| 28 | p.4 §4 RQ3, Table 3 | reuse 0.1424 / 90.20; random 11.2982 / 4.71; cyclic 0.2826 / 85.49; 8,908 positions; attention 41.00% matched, 8.85% tail | h100 doc `:25-27`, `:39-41` | KEEP + ADD | Figures match. Caption or App. F needs the 0056 provenance sentence (row 34). |
| 29 | p.4 §5 Conclusion | "cohort-median oracle removal fraction is zero across the tested models"; "practical savings remain open" | rows 16, 19, 20; 0044 also zero for the Llama pair at its own τ (`ledger.md:2947`) | KEEP | Revisit only if Llama enters the paper (Q3). |

## 2. Appendices

| # | PDF location | PDF claim | Repo evidence | Status | Proposed action |
|---|---|---|---|---|---|
| 30 | p.9 App. C "Additional-model replication" | design, A100, pins, bridge "below 0.0013%", "one retained raw-cache sample per model was rescored independently on a local machine", fork record numbers differ from the main ledger, "results come from verified summaries" | a100 doc `:21-22` (1.23258721479e-05 = 0.00123%); 0046 `ledger.md:3172-3183` (**upstream R1 not met**: card provisioned before the fork registration; evidence not on the Hub); 0056 provenance sentence `ledger.md:3388-3392` | UPDATE | Add 0056's sentence in substance: run by a co-author on one A100-SXM4-80GB at `2fb4464` with `requirements-linux.lock`; code and manifest in this repo; raw bundle on the co-author's machine, not public; **not recomputed by anyone else**. "Rescored independently" may read as a second person. 0056 says otherwise, so clarify that the rescoring was the runner's own local check (A4). |
| 31 | p.10 Table 7 | trajectory-cluster bootstrap CIs per model and cohort (e.g. Qwen3-4B long f*_K(0.03) 0.4979 [0.2077, 0.7239]) | Medians match the a100 doc and the fork-ledger provenance copy. **No CI value appears in any tracked file.** The fork copy `:43` points to `a100/summary.json` on the co-author's Desktop | HOLD | The CIs come from the private bundle, and neither 0056 document prints them. Ask whether 0056 covers them (A3); otherwise cite them as bundle-only or drop them. |
| 32 | p.10 App. D "Registration and stopping rule" | "**The co-author review of the short-cohort results (Section 3) is still open.**" | 0054 (as row 11) | **UPDATE** | Stale since 07:40Z on 2026-10-04. Same replacement as row 11. |
| 33 | p.10 App. D | "The A100 and H100 additions are descriptive follow-ups with their own frozen execution records, and neither assigns a new registered verdict" | 0046 `:3178` / 0047 `:3260-3261` (R1 not met: hardware preceded the freeze); h100 doc `:4-7` ("not an admitted upstream E-BEH result"; "allocated hardware predates that freeze"); 0048 / 0049 staged, unrun | UPDATE | True but incomplete. 0056 requires the paper to "repeat both" disclaimers: not an admitted upstream result, raw bundle not public. Add that the hardware preceded the freeze. |
| 34 | p.14 App. F | H100 inputs, execution revision `9a18ce7` "preserves the source and configuration frozen before inference", controls, 24.95 GiB | h100 doc throughout; 0047 `:3256-3264`; 0056 `:3379-3392` | UPDATE | Add the 0056 provenance sentence and the h100 document's own "not an admitted upstream E-BEH result". Figures otherwise match. |
| 35 | p.14 App. F "Attention scope" | conditional weighted deviation 0.3012 | h100 doc `:42` mentions "conditional error retained" but prints **no number** | HOLD | Not in either admitted document. Same question as row 31 (A3). |
| 36 | p.7 App. A | prediction measurements use Qwen3-1.7B only; cross-model transfer uses a single pair; "three receiver models from two families" | Llama-3.2-3B → 3.1-8B is a registered second family with a verdict: **H-E9F HELD** (0044 `ledger.md:2864`, `:2947`, `:2986`), cross arm 0.7317 (`:2971`), E8 (0040 `:2539`; amendment 0053 `:3522`) | HOLD | The PDF never mentions the Llama pair. "Two families" counts Qwen + SmolLM. Whether Llama enters is Q3. If it does, this sentence and "single model pair" change. |
| 37 | **p.7 App. A** | f* "is **not a general lower bound** on that cost because practical recomputation can propagate errors (Appendix D)" | **0023 `ledger.md:1278-1281`** (oracle LOWER BOUND, two reasons; every output carries the words); **0027 `:1651-1655`**; **0054 `:3317-3321`**: PR #12's "not a general lower bound" paragraph "is not adopted by this ruling and needs its own corrective entry if it is ever to stand"; `feedback-and-claims.md:37` states the reviewer's position and that the registered reading stands; README `:42`, `:186-187` keep "oracle lower bound" | **HOLD (conflict)** | The PDF prints the reading the operator explicitly declined to adopt. Either (a) restore the registered words and both reasons, or (b) append a corrective entry with the argument (the retained-token denominator, row 38) before the paper may keep it. This map does not decide which is correct. Also note the PDF's stated reason (error propagation) is one of 0023's own reasons *for* the lower-bound reading, so the sentence as printed is internally odd either way. |
| 38 | p.10 App. D | "Selected tokens are left out of the remaining-token mean, which differs from averaging over all tokens after repair, so f* is not an achievable recomputation or runtime cost" | 0023 `:1275-1281`; `cache-refutation-0025-0029.md:78-83` (the reviewer's argument: meeting a full-cache criterion "can require fewer repairs than f* reports") | HOLD | "Not an achievable … cost" agrees with 0027 ("never that an achievable scheme reaches it"). The denominator argument is the substance of row 37 and needs the same ruling. The oracle-diagnostic vs practical-recompute distinction itself is KEEP (App. D's "selects tokens ideally … each repair is exact and isolated" states both of 0023's reasons). |
| 39 | p.7 Table 4 | registered block K 0.6814 / 0.5629 / +0.1185 UNRESOLVED; V … DEGRADES; all-sequence and n = 420 blocks with intervals | 0020 `ledger.md:1114`; 0031 `:1894`, `:1910`; 0034 `:2033` | KEEP | All values match. 0045 `:3110-3114` confirms 0.5629 is the R² (not 0.4371). |
| 40 | p.7 App. B | (absent) the second family's content-shift result | 0053 `ledger.md:3555-3563`: Llama k = 1 drop +0.0160 / +0.0573, the τ_agent_K < τ_K inversion "does not persist" | HOLD | Only if Llama enters (Q3). 0053 is descriptive and never pooled with Qwen. |
| 41 | p.7 Table 5 | within-cap |S| 25,460 (14,269, 30,106); excluded 52,141 (35,692, 147,218); |R| 6,551 / 11,500; overlap 0.985 / 0.989 | 0025 `ledger.md:1462-1464`; 0029 `:1805-1806` | KEEP | — |
| 42 | p.7 App. C Controls | identity / prefix zero; coverage 0.9344; null 2.009 / 1.962 | 0029 `ledger.md:1772-1773` | KEEP | Short-cell figures, admitted by 0054. |
| 43 | p.7–8 App. C "Configuration bridge" | f* zero; median R² 0.8932 / 0.8603 | 0045 `ledger.md:3030-3033` (per-handoff bridge R²; medians 0.8932 / 0.8603) | KEEP | W6 needed these on the ledger; 0045 put them there. |
| 44 | p.8 App. C | matched configuration: δ_K 0.0682 → 0.0895; fraction over τ_K 0.0437 → 0.0527; 16+ 0.0195 → 0.0381; f*(0.03) 0.1433 → 0.2930; shares 0.43 / 0.39 | 0038 `ledger.md:2352-2362` | KEEP | — |
| 45 | p.8 App. D-adjacent ("For the matched short-cohort rerun, the calibration was written after prefill …") | as quoted | 0038 `ledger.md:2324-2328` | KEEP | — |
| 46 | p.8 Table 6 / Fig. 2 / Fig. 3 / Fig. 4 | ladder; position bins 0.038 / 0.131 / 0.162 / 0.092 with counts; seam bins with counts; depth profiles | 0036 `ledger.md:2201`, `:2203`, `:2206`; 0045 depth profile `:3027-3029` | KEEP (+ ADD for Fig. 3) | Fig. 3 means: see row 23. |
| 47 | p.8 App. C "Normalization diagnostic" | K 0.0000 (0, 0); V 0.0033 (0.0020, 0.0070) | 0045 `ledger.md:3025-3026` | KEEP | — |
| 48 | p.11 App. E Remark 1 | figures are pooled medians and cannot confirm the corollary | W5 (`review-response-map.md:45`: "Remark 1 cites means and reads 'is consistent with'") | ADD | Cite 0045's bin means (row 23). |
| 49 | App. E (whole) | proofs stated in prose; no Lean claim | `proofs/` (PR #16); CLAUDE.md: "Lean" may be claimed only after `lake build` passes on the committed tree | KEEP | Do not add a Lean claim without that build. |

## 3. Repo evidence after the PDF, by entry

| entry | what it is | in the PDF? | status for the camera-ready |
|---|---|---|---|
| 0050 (`ledger.md:3573`) | Llama long cell **registered** at a native receiver; descriptive; "cannot move, support or refute H-E9L, and is never pooled with entry 0036" (`:3586-3587`) | no | HOLD. Its figures entry 0051 is staged, not appended. No result to cite. |
| 0052 (`:3330`) | Llama E8 amendment registered | no | Registration only; nothing to cite by itself. |
| 0053 (`:3522`) | Llama E8 amendment **ran**: inversion does not persist; τ_agent_K unchanged | no | HOLD (Q3); appendix candidate only. |
| 0054 (`:3287`) | Condition 1 discharged by ruling | contradicted (rows 11, 32) | UPDATE both "still open" sentences. |
| 0055 (`:3406`) | E-TRUNC **registered**; 21 of 35 handoffs enter (|M_∩| ≥ 2,000); L32-native deferred | no | HOLD: no result. At most a registered-not-run sentence with both limitations. 0055's re-matching sentence carries a wording erratum staged in `append_0057.py` (`docs/reviews/2026-10-04-0055-stated-figures-recomputed.md:31`), so do not quote it. |
| 0056 (`:3372`) | pilot figures citable under a provenance sentence | figures present, sentence absent | UPDATE (rows 3, 4, 20, 25, 30, 33, 34). |
| 0057 | E-TRUNC figures | — | **Not completed.** The script is staged in `docs/drafts/`; no `results/e9t*` run is present in this checkout. Claim nothing. |
| 0044 (`:2864`, pre-PDF) | **H-E9F HELD** on Llama-3.2-3B → 3.1-8B, 28 of 28, τ_K = 0.2861 | no | HOLD (Q3). It is the only registered second-family verdict, and the PDF omits it while calling SmolLM3 the second family. |
| 0048 / 0049 / 0051 | staged figures entries (operator reruns; Llama long) | — | Nothing to cite. |

## 4. Questions to resolve before manuscript edits

1. **Is this PDF the live camera-ready source of truth, or a snapshot?** It was built 2026-10-04 06:16Z, about 5.7 hours
   before the 11:59Z deadline and before 0054 / 0056. The LaTeX source is not in this repo
   (`review-response-map.md:14-15`). The paste list `~/dev/briefs/2026-10-04-lcfm-camera-ready-patch.md` (cited at
   `review-response-map.md:125`) is off-repo. Was a later build submitted? Where does the source live, and is the
   venue still accepting revisions (it is non-archival, `review-response-map.md:28-29`)?
2. **Has 0057 completed since the snapshot?** No: staged script, no E-TRUNC run under `results/`, and upstream `main`
   is still `efab85a` as of the latest check. Re-check `docs/drafts/README.md` and the ledger tail before writing any
   E-TRUNC sentence.
3. **Which second-family results go in the main text and which in an appendix?** The PDF's "additional models" are
   the 0046 pilot (Qwen3-4B, SmolLM3-3B; cited under 0056, not on the ledger). The ledger's second family is Llama
   (0044 H-E9F HELD; 0040 / 0053 E8; 0050 registered, unrun). Decide: (a) Llama short cell in main text, appendix, or
   omitted; (b) whether "three receiver models from two families" and "single model pair" (App. A) are rewritten;
   (c) whether 0053 enters App. B. Llama is never pooled with Qwen, and it uses its own τ.
4. **What is the final status of the f* lower-bound wording?** The PDF (App. A) says "not a general lower bound". The
   ledger (0023, 0027), README and 0054 say "oracle lower bound", and 0054 requires a corrective entry before the
   contrary reading can stand. Pick one: restore the registered words and both reasons, or append a corrective entry.
   Rule in the same decision on "removal" vs "recompute" (row 14), and on 0023's "every output carries the words" vs
   the "'floor' nowhere in the body" invariant (row 18).
5. **Does every 0056-admitted result appear correctly in the PDF?** The figures that are in the two admitted documents
   match (Tables 2 and 3; the seam deletion 0.1016; attention 41.00% / 8.85%; bridge gap). Missing: the provenance
   sentence, in every place those figures appear. Beyond the documents: Table 7's CIs, SmolLM3's 0.0228 and App. F's
   0.3012 do not appear in either admitted document (rows 21, 31, 35). Rule on whether 0056 covers them.

## 5. Ambiguities for the operator (Hossain) to confirm

- **A1.** Wording that replaces "still open" (rows 11, 32): 0054 accepts a partial, unsigned review by ruling. Should
  the paper say "discharged by operator ruling", say only "reviewed", or say nothing?
- **A2.** Issue #7's closing comment: "The paper states that the long and scaled-short cells were recomputed by the
  operator only (PR #6 and PR #12 cover the other cells)." PR #12's audit did reproduce the token counts and f* medians
  for e9, e9s and e9l from the public datasets (PR #12 reproduction comment). Is that sentence still owed, and what
  exactly should it say?
- **A3.** Scope of 0056: only the figures printed in the two merged documents, or also values in the linked
  fork-ledger provenance copy and the private bundle (Table 7 CIs, 0.0228, 0.3012)?
- **A4.** App. C's "rescored independently on a local machine": the runner's own check, or a second person? 0056 says
  the figures "have not been recomputed by anyone else".
- **A5.** Rows 5 and 6 (causal "governs"; "viable alternative to recomputation"): interpretation, not evidence. The
  author decides.
