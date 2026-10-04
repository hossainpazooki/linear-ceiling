# Review response map — LCFM Submission 126 (Accept), reviewer weaknesses → record → action → target

**Date:** 2026-09-30 · **HEAD:** `118d08e` (= `origin/main`, 0 / 0) · **Last ledger entry:** 0044 (0045 / 0046 staged in
`docs/drafts/`, unappended; next free number 0047) *(2026-10-01: the corrective entry **0045 is APPENDED** at `b3bf7ec`; the Llama
long drafts were renumbered 0046 / 0047; next free number 0048)* · **Gates at write time:** `ledger ok`, `scope ok`, seal `OK`; suite
491 passed / 28 failed / 26 errors on Windows (same counts as 2026-09-24; Linux CI green at `118d08e`).

**Sources read for this map.** The decision and both official reviews, from the OpenReview forum page printed
2026-09-30 (`~/Downloads/Carryover_ … _ OpenReview.pdf`, text extracted; the API returns nothing anonymously).
Reviewer TE3a, 2026-09-28, rating 6 / confidence 4. Reviewer teFN, 2026-09-25, rating 6 / confidence 3. Decision
2026-09-29: Accept. Quotations below are verbatim from that print. The decision email (OpenReview, 2026-09-30 06:09Z)
carries no camera-ready instruction.

**Not on this machine, and this map does not reconstruct it:** the submitted tree (`neurips-farhan/main.tex`,
`make_figures.py`, `figures.json`, `lean/Carryover/*.lean`) and the submitted PDF. The "paper line" column therefore
cites the OpenReview abstract (verbatim, public) and otherwise the outline v3 slot the sentence came from. The
"ledger" column is what the record actually states; where the figure a weakness needs is **not** on the ledger, the
cell says so — that is the finding, not an omission.

## F7 / F8 — the two lookups the seed asked for first

- **F7, appendix lettering: unresolved.** Reviewer TE3a: "Appendix E describes an unrun study and could be dropped."
  The submitted PDF is not here. The only tex on this machine is the superseded 2026-09-13 scaffold
  (`docs/paper/tex/main.tex`, untracked), whose plan puts the E-RL design at **F** and the corpus manifest at E —
  that scaffold is not the submitted build, so it resolves nothing. Operator: read the submitted PDF's appendix
  headings before any edit by letter.
- **F8, LCFM camera-ready date: not stated anywhere reachable.** Workshop site (read 2026-09-30): submission
  2026-09-13 AoE (extended), reviews to 09-25, decisions 09-29, workshop date "TBD", **non-archival** ("Accepted papers
  will appear on the workshop website. They will also be available on OpenReview and the NeurIPS virtual site").
  OpenReview venue group: `instructions` empty, `date` empty, contact `longcontextfm@googlegroups.com`. Decision
  email: no date. Operator: ask the organizers; until then T1 has no deadline and T2's is **MLSys 2027, Oct 30 2026
  12:00 PDT** (mlsys.org/Conferences/2027/Dates, read 2026-09-30; submissions open Oct 10).

## 1. Reconciliation table

Columns: weakness (reviewer, verbatim core) · what the record states (ledger `entry:line`, or "NOT ON LEDGER") ·
action · target · owner slot.

| # | Weakness | Record | Action | Target | Owner |
|---|---|---|---|---|---|
| W1 | **Behavioral validation.** TE3a W1: "The tolerance is the error of a weak linear map and … is not validated against answer quality … A behavioral check (e.g., next-token KL or top-1 agreement when teacher-forcing the recorded continuation from reused vs fresh caches) would better show what the relevant repair budget is." teFN W1: "Even a small experiment comparing continuations from fresh and reused caches would help." | 0023:1278-1281 (f* is an oracle LOWER BOUND, two reasons); 0023:1367-1370 (`[STRETCH]` partial prefill "registered, own entry before anything runs … needs injection code upstream and a task"); scope limits repeat "generation quality after reuse" unmeasured at 0029:1816, 0036:2226, 0038:2307, 0044:2373. | Register **E-BEH** (`docs/drafts/e-beh-design.md`). Text stays "No downstream-quality number is claimed" until an entry reports one. | T2 | ??? |
| W2 | **Length not isolated.** TE3a W3: "length is not isolated (different handoffs, and about two fifths of the gap is receiver configuration); truncating the sender context of the same handoffs would isolate it." teFN: "differences between distinct short and long handoffs cannot be attributed to length alone." | 0038:2361-2362 (shares 0.4285 far-from-seam, 0.3916; "(scaled − native) / (long − native)"); 0036:2240 ("length AND configuration"); 0037 registers the matched cell as deciding nothing. | Register **E-TRUNC** (`docs/drafts/e-trunc-design.md`): head truncation of S on the same 35 handoffs, common matched subset. | T2 | ??? |
| W3 | **Mean vs tail.** TE3a W2: "A mean criterion can pass while the tail still matters. CacheBlend found … recomputing roughly the 10-20% highest-deviation tokens is what preserves quality, and attention-weighted deviation would say more than the Prop. 4 bound." | 0023:1253-1266 (δ in R²'s units; "not 'this token's KV is x% wrong'"); 0023:1275-1281 (f* repairs the MEAN); per-token tail counts (5.8% / 7.9% of matched tokens over τ_K, on every handoff; per-handoff mean δ_K max 0.221 / 0.269) are in outline v3 §5 and `docs/2026-09-20-astra_review.md` §5 but **NOT ON LEDGER** (corrective entry owed, 09-21 brief item 2). *(2026-10-01: **ON LEDGER** — 0045:3009 e9l, 0045:3036 e9 and 0045:3061 e9s (both Condition-1-bound, stated as corrections only), 0045:3087 e9f; each paragraph carries the tokens over τ_K, the per-handoff maximum mean with its margin under τ_K, and the top-10 % / 20 %-removed means, all from `e9_tail`.)* | Register or describe **E-TAIL** (`docs/drafts/e-tail-design.md`). Its dumps-derived table (δ_max, p(τ), top-10/20 %-removed mean) is CPU-only from `results/e9l/tokens/` (35 records present) — it can enter T1 **only** through a numbered entry (locked rule: a figure enters the paper only when an entry states it). *(2026-10-01: Part A entered via 0045, at the run queue's ruling-4 default; Part B, the attention-weighted quantity, stays T2 and unregistered.)* | T2; T1 table on ruling | ??? |
| W4 | **Framing.** TE3a W3: "73% of matched tokens sit at sender positions inside the native 32K window, receivers are short (median 11.5K for the 39 length-excluded handoffs that include the 35, Table 3), and the abstract should say that 35K to 80K is the sender length." teFN W3: "The 35K–80K lengths describe sender contexts, not receiver prompts." | Abstract (OpenReview, verbatim): "On 35 handoffs of 35K to 80K tokens read by a YaRN-extended receiver". Position bins with token counts: 0036:2206 (0-32767: n = 284,094 of 387,508 → 73.3 %, the reviewer's figure, derivable from the entry). \|R\| for the **39**: 0029:1463/1805 (11,500; p10 7,085; p90 20,589). \|R\| for the **35**: `results/e9l/summary.json` `coverage_comparison.included.n_receiver` = 11,462 (p10 7,085, p90 19,853) — **NOT ON LEDGER**. *(2026-10-01: **ON LEDGER** — 0045:3022 \|R\| median 11,462 (p10 7,085, p90 19,853; n = 35); 0045:3021 the native-window row: 284,094 tokens, 73.3 % of matched, mean δ_K 0.0926 / median 0.0381.)* | Abstract clause → "35 handoffs whose sender contexts run 35K to 80K tokens" (grounded in the public abstract). Native-window row: the 73.3 % is arithmetic on 0036:2206's counts (state it as such, as outline v3 does for 89.7 %). The 35-set \|R\| row needs an entry before it can print; the 39-set figure can print now with its scope stated. | T1 | ??? |
| W5 | **Corollary 3 applied with medians.** teFN W2: "Corollary 3 requires bounds that hold for every token, while the figures report medians. Those medians do not justify the claimed prediction of a zero floor." | Seam and position medians: 0029:1785, 0036:2203, 0036:2206. Pooled **means** per bin: `summary.json` `seam_profile_pooled` carries `median` only (checked e9 / e9s / e9l) — **NOT COMPUTED by the summarizer, NOT ON LEDGER**. The per-token records can produce them on CPU. *(2026-10-01: computed by `e9_tail` and **ON LEDGER** — pooled seam-bin MEANS beside the medians, with n per bin: 0045:3016 e9l, 0045:3095 e9f, and inside the e9 / e9s paragraphs from 0045:3036 / 0045:3061; position-bin means alongside. Means run 1.8–8.6× the medians.)* | Restate Cor. 3 on bin means (exact decomposition µ = Σ_b (n_b/n)·mean_b δ, no per-token bound); Remark 1 cites means and reads "is consistent with". **The means need a summarizer figure and an entry** — this is not a text-only fix. Lean statement: cannot be checked here (`lean/` absent). *(2026-10-01: both exist; the Cor. 3 restatement cites 0045. 0045:3116 says the restatement uses the means and says so.)* | T1 text; figures gated on an entry | ??? |
| W6 | **Prop. 4 under YaRN.** teFN W2: "Proposition 4 alone does not establish that the same tolerance remains meaningful under YaRN." | Bridge control: 0036:2191-2192 (three short handoffs under native vs scaled receiver, f*(τ_K) K 0.0000 / V 0.0000 each, median δ_K 0.071-0.089). Bridge R² values (0.8992 / 0.8821 / 0.8932; V 0.8603) are **NOT ON LEDGER** (astra R1-8; fact-check brief item 3). | Reword: the bound's form is schedule-independent, its magnitude is not; the **bridge control** is the empirical carrier; delete "predicts". Cite the bridge by its f* and δ (on ledger), not by R² unless entered. | T1 | ??? |
| W7 | **Narrow.** teFN W3: "one model pair and one coding-agent family … a mapper trained on only 50 generic sequences, so it should not be taken as evidence against cross-model reuse more generally." | Calibration-size sensitivity: 0034:2043 (n = 420 mapper cross f*(τ_K) 0.8106 vs 0.9352 on the same kept handoffs — still beyond DEGRADES); k = 4 / 8 collapse noted at ledger 913 and 1129. Second family: 0040-0044 (H-E9F HELD 28 / 28 on Llama-3.2-3B → Llama-3.1-8B) — on the ledger but **not recomputable from a clean checkout** until the R8 push lands (both Hub targets exist and are empty as of 2026-09-30 04:24Z). The seed's "independent reimplementation R²_K 0.76 at k = 8 vs 0.68 at k = 1" was **not located on the ledger** by grep; do not cite it until its line is found. | T1: one sentence — the cross arm is a reference instrument; cite 0034's n = 420 refit as the reason the map is not a ceiling on cross-model reuse. T2: the Llama cell once R8 holds; the n = 420 map on the long cohort (unrun). | T1 + T2 | ??? |
| W8 | **What HOLDS could have failed against.** TE3a W1: "HOLDS says that same-model stale keys explain about 89% of fresh key variance, more than the map does, which is expected." | Null pairing: 0029:1772 (2.009 / 1.962), 0036:2191 (2.015 / 1.975). Cross arm: 0029:1797 (0.9286), 0036:2216 (0.9640), 0036:2218 (cross K R² 0.4214). Ladder at 0.03: 0029:1783 (0.1433), 0036:2201 (0.5255). | One sentence in §5 naming the three: null pairing, cross arm, τ = 0.03 where the floor does rise. All on the ledger. | T1 | ??? |
| N1 | TE3a nit: "The footer uses the main-conference template". | — | Switch to the LCFM workshop class/footer. Template is the organizers' Overleaf link (read-only); the scaffold's comment (`docs/paper/tex/main.tex:12-19`) records the same unknown. | T1 | ??? |
| N2 | TE3a nit: "Appendix E describes an unrun study and could be dropped." | E-RL: `docs/2026-09-02-e-rl-design.md` ("design, unnumbered, not registered"); ledger 2153 (astra R1-5 cites 2152-2153). | Drop the E-RL appendix from T1; keep the one intro / future-work sentence. Letter unresolved (F7). | T1 | ??? |

## 2. Camera-ready patch (T1) — status: NOT PREPARED, branch stopped

The seed's deliverable 3 is a diff against `neurips-farhan/main.tex` and `make_figures.py`. Neither file is on this
machine (searched `~/dev`, `~/Downloads`, `~/Documents`, `~/Desktop`, `~/OneDrive` to depth 4), and the seed forbids
reconstructing them. What the operator can carry to wherever the tree lives:

- **Grounded now (public abstract text):** "On 35 handoffs of 35K to 80K tokens read by a YaRN-extended receiver" →
  "On 35 handoffs whose sender contexts run 35K to 80K tokens, read by a YaRN-extended receiver". Same clause in §1
  and §5 wherever it recurs.
- **Grounded now (ledger):** W8's sentence; W7's reference-instrument sentence citing 0034:2043; W6's rewording
  citing the bridge's f* and δ from 0036:2191-2192.
- **Blocked on an entry (new figures):** W4's \|R\| row for the 35; W4's native-window subset row (73.3 % is
  arithmetic on 0036:2206 and may print as such; a pooled mean/median δ for that subset is new); W5's pooled bin
  means; any W3 tail table. These are macros that `make_figures.py` cannot emit from the ledger today.
- **Blocked on the tree:** Cor. 3 / Remark 1 / Prop. 4 / Remark 2 wording (statements not readable here); appendix
  lettering (F7); the Lean diff (`lean/` absent); template/footer (N1).
- **Invariants no patch may cross** (from the fact-check brief and the seed, unchanged): short and long never pooled;
  removal never presented as achieved repair; no tokenwise bound inferred from a mean; f* = 0 means the matched-set
  mean passes τ, not that every token agrees; cross arm never headlined; no downstream-quality number until an entry
  reports one; "floor" nowhere in the body, "reuse margin" only in the title.

## 3. Rulings this map needs (operator)

1. **E-BEH bands** (HOLDS / DEGRADES on top-1 agreement and KL; the NULL-arm margin). Numbers are `???` in the draft.
2. **E-TRUNC margin** (how close L = 32,768 must sit to 0038's far-from-seam 0.0381 to read as "length") and whether
   the native-receiver cell at L = 32,768 is in scope.
3. **E-TAIL:** registered with a band, or descriptive only; and whether its dumps-derived table enters T1 via the
   owed corrective entry. *(2026-10-01: Part A's table entered via 0045, descriptive; band-or-descriptive for Part B still open — run queue ruling 5.)*
4. **W5:** accept that the bin-mean restatement needs a summarizer figure + entry (not text-only), and whether that
   entry is the same corrective entry as W3's tail counts (one entry, or two). *(2026-10-01: one entry, 0045, at the run queue's default for rulings 4 and 7.)*
5. **Lean:** per-token statement kept as stated-stronger-than-used, or restated — decidable only at the tree.
6. **De-anonymization at camera-ready** (HF dataset names, the account name): the Sep 29 decision is Accept; the
   workshop is non-archival; still the operator's call.
7. **Owner slots** in the table above (all `???`).

## 4. Drift this map noticed, outside the seed's scope

- The seed's §0 says "last known ≥ 0042"; the ledger's last entry is 0044 (PR 5 merged 2026-09-24).
- The seed's known-red list names "7 pre-existing `check-learnings` entries"; no `check_learnings` module or script
  exists in this tree or in `.github/` (grep). The Windows reds are `os.fsync` on a read-only handle
  (`src/linear_ceiling/e9.py:415`, EBADF on Windows) and tests that exec bash scripts (WinError 193); Linux CI is green.
- Upstream `../kv-transfer-replication` local HEAD is `9ca6258` (holdover-instrument branch tip, untracked
  `results/mapper/qwen3-0.6b-to-1.7b/n420/`); the pins in `UPSTREAM.md` are by ancestry, so nothing here is affected,
  but E-BEH's injection work must be pinned by entry before it runs (0023:1367).

## Entries, 2026-10-02

W3, W4 and W5's off-ledger figures (tail counts and per-handoff maximum, |R| of the 35, native-window mean, seam and position bin MEANS) are now ON the ledger: entry **0045** (`b3bf7ec`, 2026-10-01), stated per cell from `e9_tail` (also the second family, e9f, with its per-handoff maximum 0.2860 against τ_K 0.2861). The camera-ready macros can cite 0045 for every figure the table above marked NOT ON LEDGER, except the Lean restatement (tree still absent). The short-cell paragraphs of 0045 remain Condition-1-bound: they enter no paper until the co-author review is merged (ruling 2026-10-01; the freeze clause is moot).

## Ruling, 2026-10-04 — Condition 1

Condition 1 (0032; restated 0045:3062–3064: the co-author refutation merged under `docs/reviews/` with two signatures) is
**discharged by operator ruling**: issue #7 together with PR #12's two review records (`docs/reviews/2026-10-01-cache-refutation-0025-0029.md`,
`docs/reviews/2026-10-01-feedback-and-claims.md`, PR head `8100414`) is treated as the confirmation. The review covers issue #7's
rows R1/R3/R4 and R9/R10 and lists the rest as not covered; those no longer gate the paper. **Issue #7 was closed later the
same day with a row-by-row disposition** (https://github.com/hossainpazooki/linear-ceiling/issues/7#issuecomment-5978012666):
R13 (68 = 25 + 35 + 8), R14 (0.8106 vs 0.9352), the configuration share (0.4285 / 0.3916) and 0045's tail per cell were
recomputed operator-side from the raw records and match the ledger; R2, R5/R6, R11/R12 and a second-person e9l/e9s recompute
from the public backups were dropped by ruling — the paper says the long and scaled-short cells were recomputed by the operator only. Ledger entry
**0054** records the ruling (staged as `docs/drafts/append_0054.py`, numbered after the Llama drafts 0050–0053 by operator instruction).
Not changed by the ruling: the registered reading of f* as an oracle lower bound (0023:1278/1281, 0027); PR #12's README
paragraph to the contrary is not adopted. Whether the camera-ready text printed the short-cell figures before this ruling is
not recorded here; the deadline closed 2026-10-03 23:59 AoE.

## Ruling, 2026-10-04 — co-author pilot figures citable in the paper (0056)

W1 and W7 may cite the co-author's merged documents `docs/2026-10-01-cache-behavior-h100.md` (H100, execution commit `9a18ce7`,
freeze record, torch 2.14.0 / transformers 5.17.0 / CUDA 13.0) and `docs/2026-10-01-a100-analysis.md` (A100, results commit `2fb4464`,
`requirements-linux.lock`, input manifest) under a provenance sentence: run by a co-author on the named card at the named commit
with the pinned environment; code, inputs manifest and environment in this repository; the raw bundle is on the co-author's machine,
not public, and the figures have not been recomputed by anyone else. Ledger entry **0056** (staged as `docs/drafts/append_0056.py`)
records the ruling and supersedes the "in any paper" clauses of 0046/0047; the ledger's own evidence rules (R1/R8/R12) are unchanged,
so these figures reach the ledger only by 0048/0049 from the operator's run or by the admission procedure. The sentences are in
the camera-ready paste list (`~/dev/briefs/2026-10-04-lcfm-camera-ready-patch.md`, W1/W7 additions of 2026-10-04 night).
