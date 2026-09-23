# Astra review — consolidated record

**Date:** 2026-09-20 · **Status:** review record. Not a ledger entry, verdict, amendment or summarizer
output; `ledger/ledger.md` wins over every line here. Written by a Claude Code session from two sources:
the Codex thread `01a08e09` (model `gpt-6-astra`, "Astra"; 2026-09-10 → 09-14, read from
`~/.codex/sessions/2026/09/10/rollout-…01a08e09….jsonl`) and this repo at `main` = `a5053b2`. Each
finding carries who verified it: **A** = Astra, at the commit it reviewed; **C** = re-checked by this
session on 2026-09-20 against `main`; **A only** = not re-checked here.

## Summary of issues

**In the record and the paper (Astra's findings; status as found on `main` at `a5053b2`, and what the
change that carries this document fixes — §12):**

1. **The false token-level universal is still in `README.md`** (lines 37, 138, 164, 169): "f* = 0 at every
   matched token". 0023 defines f* on the MEAN of the remaining tokens; tokens over τ_K exist on every
   handoff. Outline v3 and 0038 carry the corrected reading; the README and the immutable sentences in
   0029/0036 do not, and no corrective entry exists. **README fixed here; the ledger sentences remain and
   need a corrective entry (operator).**
2. **Condition 1 is undischarged, and the README misstates its deadline** as "before submission"
   (`README.md:145`); 0032 says "by the numbers-freeze gate", EOD 2026-09-08 (`ledger:1927-1928, 1949`).
   The LCFM PDF printed 0029-derived figures anyway. **README wording fixed here; the condition itself is
   open — operator's ruling.**
3. **"Longer handoffs spend more of the margin" is unsupported** — Astra marked it on 09-14 (`ledger:2369-2370`
   excludes "anything about length alone"), and the 09-16 ICLR seed still prescribes it as the *legal*
   replacement sentence (§5 item 2, §8). Same for "nine in ten" (the record says 0.9500 and 0.9640) and
   for the configuration share's denominator, which is native-short → long, not scaled-short → long. **Open
   in any text built from that seed.**
4. **The GPU-runs doc has two factual errors** — "six kept directories" are three long handoffs plus three
   bridge controls; and it claims every number is a ledger quote while 57 GB, 31.56 GiB and ~2 h are not.
   **Amendment note added to that doc here; §4.**
5. **Outline v3 still carries figures with no ledger provenance** (89.7 %, median 50,916, bridge R²
   0.8992 / 0.8821 / 0.8932) and "fp32" for dumps that 0025 registers as fp16. **Corrected / annotated in
   place here; the unprovenanced figures still need an entry or a cut before reuse.**
6. **The 09-08 comparator cannot enforce cold provenance**: score-file hashes are reported but do not
   enter `passed` (line 63). **Open, deliberately not touched: it is a co-author's review tool cited by the
   09-08 record; changing it after the fact alters what that record ran.**
7. **Settled this session:** "f*(τ_K) = 0 on every handoff" — true at the handoff level. Max per-handoff
   same-K f* is 0.0 over 25 / 35 / 25 handoffs in `results/{e9,e9l,e9s}/summary.json`. §5.

**In Astra's own work:** its last turn (the introduction rewrite) is recorded `failed` on a usage limit
before its read-back; the rewrite sits unverified in the superseded scaffold `docs/paper/tex/main.tex`. The
refutation was stopped by the operator with the Path A template empty. Its staged Path B script claims
entry number 0039, which the `llama-second-family` branch has since taken. Its first two review attempts
stopped at a dirty-tree gate, and the paper text, `figures.json` and the bibliography were never supplied to
it, so **no Astra finding is a finding about the submitted PDF**.

**In this session's handling (Claude):** I told the operator Astra's two GPU-doc corrections were "already
on record" — they existed only in the Codex thread. I picked up the 09-16 seed without noticing it
prescribes a sentence Astra had already marked unsupported (issue 3). I read "AAR" as Algoverse; it is ARR.
I built a fourteen-row co-author instrument the operator then flagged as process overhead. I summarized
Astra's thread from one slice before reading it whole.

## Contents

1. [Sources and method](#1-sources-and-method)
2. [Astra's thread, turn by turn](#2-astras-thread-turn-by-turn)
3. [Findings register](#3-findings-register)
4. [The GPU-runs doc: two errors and the judgments](#4-the-gpu-runs-doc-two-errors-and-the-judgments)
5. [Settled: zero on every handoff](#5-settled-zero-on-every-handoff)
6. [What Astra wrote to the tree](#6-what-astra-wrote-to-the-tree)
7. [Condition 1: both paths, and the 0039 collision](#7-condition-1-both-paths-and-the-0039-collision)
8. [Astra as workshop reviewer](#8-astra-as-workshop-reviewer)
9. [This session's work, with pointers](#9-this-sessions-work-with-pointers)
10. [Open items by owner](#10-open-items-by-owner)
11. [Re-verify](#11-re-verify)
12. [Fixes applied with this record](#12-fixes-applied-with-this-record)

## 1. Sources and method

- Codex state under `~/.codex/`: `history.jsonl` (prompts), the rollout file (full thread, 77 messages),
  `thread_history_1.sqlite` (`thread_turns.status`), `state_5.sqlite` (`threads`). Read-only.
- Astra worked under the operator's constraint "ledger first, quote with line numbers, run no experiment";
  its findings use three bins — VERIFIED FALSE, COULD NOT VERIFY, CHECKED CLEAN — kept here.
- This session re-checked against `main` only what is marked **C**. Gates at `a5053b2` on 2026-09-16:
  `ledger ok`, `scope ok`, seal `OK`, 436 passed / 1 skipped.

## 2. Astra's thread, turn by turn

| when (UTC) | asked | reviewed at | outcome |
|---|---|---|---|
| 09-11 01:25 | adversarial last read of the LCFM 4-pager | `775dda4` (wrong dir), then `50bc439` | two stops at the dirty-tree gate; after the operator scoped the gate, review 1 (11 findings). Paper text, `figures.json`, `.bib` absent throughout |
| 09-11 20:20 | additional review after rulings | `d0b91db` | review 2 (10 findings) |
| 09-12 01:39 | critique the GPU-runs assessment | `cf4047f` | 2 verified false + 5 judgments + priority order (§4) |
| 09-12 02:15 | next best step for LCFM | — | run the scaled short cell, register first, firm cutoff → became 0037 / 0038 |
| 09-14 05:01 | "review opus's work" (0037/0038 wording) | `a5053b2` | review 3 (6 findings) |
| 09-14 05:09–05:55 | rewrite abstract; rewrite intro; re-lead with carryover | — | three drafts, in the thread only |
| 09-14 06:31 | read it as an LCFM reviewer | — | §8 |
| 09-14 06:43–07:15 | Condition 1 seed | `a5053b2` | status note, board-source note, Path A template, Path B script + 7 tests; stopped on an unverifiable source row |
| 09-14 07:18 | "stop the refutation and rewrite the introduction" | — | patch applied to the scaffold; turn `failed` (usage limit) |

## 3. Findings register

Severity is Astra's. "Status" is on `main` today.

| # | finding | evidence | by | status |
|---|---|---|---|---|
| R1-3 | 0029 and 0036 define f* in prose as an exceedance fraction; 0023 registers mean repair; code implements 0023 | `ledger:1775-1776, 2194` vs `1274-1276`; `e9_pertoken.py:56-75` | A | entries immutable; 0038 restates correctly (C, `ledger:2340-2341`); no corrective entry |
| R1-4 | agent K R² cited as 0.4371; that is the shortfall, R² is 0.5629 | `ledger:1470-1471, 1800` vs `1113, 1853` | A; 1113/1853 C | prose defect stands; arithmetic correct in 0030 |
| R1-5 | outline called E-RL "registered" | outline v2 `:74, :181` vs `ledger:2152-2153` | A | fixed in v3 (`:198`, C) |
| R1-6 | outline says dumps are fp32; 0025 says fp16 | outline v2 `:94-95` vs `ledger:1533-1534` | A | **corrected in v3 here** (fp16 stored [0025]; fp32 is the forward pass [0026]) |
| R1-1 | paper, `figures.json`, `.bib` never supplied | — | A | never supplied; the submitted tree is off this machine (C) |
| R1-2 / R2-1 | Condition 1 undischarged; living docs say "before submission", 0032 says the 09-08 freeze | `ledger:1947-1951, 2159-2160`; `README.md:145` | A; C | condition open; **README wording fixed here** |
| R1-7 / R2-2 | universal token claims ("not one matched token exceeds τ_K") | `ledger:1787, 1811-1812, 2208`; README | A; C | **README fixed here** (four places); v3 marks it FALSE (`:225`); ledger sentences stand until a corrective entry |
| R1-8 | outline figures without ledger provenance: 89.7 %, median 50,916, 80 min, bridge R² ×3, δ_K medians by bin | outline v2 lines; `ledger:2190-2191` has no bridge R² | A | **annotated in v3 here**: 89.7 % is arithmetic on two ledger counts; median 50,916 and the three bridge R² values occur 0 times in the ledger (C); 0.8603 confirmed absent by a 09-14 learning |
| R1-9 | calibration-size attribution extended to the long cell | `ledger:2042, 2057-2058, 2217-2218` | A only | — |
| R1-10 | 0028's tolerance change is post-run | `ledger:1687-1705` | A only | disclosed in the ledger; a paper must say so |
| R1-11 | "identity likely reads f* ≈ 0 at engine lags" has no measured premise | outline v2 `:179-180` | A only | bears on the Async RL design |
| R2-3 | brief said the archive-revision correction was not on main; it was | clean-clone review `:93-106` | A only | closed |
| R2-4 | a seam median of 0.260 is below τ_K and is not a counterexample to the universal claim | `ledger:2203, 2194` | A only | closed (argument withdrawn) |
| R2-5 | no registration for the short-cell run; bridge ≠ re-render comparison; config loader rejects profile edges ≥ cap | `ledger:2132-2134, 1053-1057`; `config.py:304-308` | A only | closed by 0037 + `config/e9s.toml` |
| R2-7 | comparator `passed` ignores score-file hashes; `$RECHECK` collides with the summarizer's `recheck/` | compare script `:63, :71-72` | A; `:63` C | open |
| R2-8 | "deviation is local to the seam / concentrated at seams" needs exceedance-by-bin, not medians | `ledger:1785, 2203`; README | A | the README phrase is gone on `main` (C: no match); the seam claim still needs exceedance-by-bin before it is reused |
| R2-9 | R2 memory probe not shown for the new run; `probe_e9l.py` hardcodes its config | protocol `:96-97` | A only | superseded by the e9s sitting log |
| R2-10 | matching configuration removes a confound, does not isolate length | `ledger:2086-2093` | A only | carried into 0037/0038's "not established" |
| R3-1 | fallback "submit on 0029 + 0036" conflicts with Condition 1 | `ledger:1947, 2159` | A | the LCFM PDF did this anyway |
| R3-2 | configuration share explained with the wrong denominator | `ledger:2359-2361` | A; C | the share is (scaled − native) / (long − native) |
| R3-3 | "nine in ten" fails the number trace | `ledger:2345, 2215` | A only | 0.9500 and 0.9640 |
| R3-4 | "longer handoffs spend more of the margin" still reads as a length effect | `ledger:2369-2370` | A; C | prescribed by the 09-16 seed §5.2 / §8 |
| R3-5 | "PIC's cost begins below that tolerance" exceeds an oracle lower bound | `ledger:1277, 2370` | A only | — |
| R3-6 | "zero on every handoff" stronger than median/p10/p90 | `ledger:2337` | A | **settled true, §5** |

Astra's CHECKED-CLEAN items that matter for any rewrite: verdict arithmetic follows 0023's rule; corpus
arithmetic (68 = 25 + 35 + 4 + 4; 2,904 trajectories, 60 measurable) is consistent; the bridge rule predates
its result (branch present at the registration commit `bacfe86`); alignment is labelled a floor; the two
cells are never pooled; 0037 predates prefill and 0038 moves no cell.

## 4. The GPU-runs doc: two errors and the judgments

Target: `docs/2026-09-11-gpu-runs-after-the-pivot.md` (both errors present at `a5053b2`, C; an amendment
note stating them now sits under its status block, with the original text left as written).

**Error 1 — the rescore population.** Lines 74 and 84 say "the six E9-long kept directories". 0035 keeps
**three** long handoffs by a seeded draw (n = 3, seed 9; `ledger:2124-2126`). The other three directories
are the configuration bridge: the three shortest of 0029's kept handoffs, prefilled native and scaled and
scored at (p, p) (`ledger:2131-2134`). They are not long-cell handoffs and the rescorer needs source plus
both receiver dumps per handoff. Usable kept handoffs: eight short, three long.

**Error 2 — the provenance claim.** Line 6: "Every number cited below is quoted from the ledger entry
beside it." Lines 74–76 cite 57 GB, "31.56 GiB peak … 0036", and ~2 h. `57 GB` and `31.56` occur zero
times in the ledger (C). Astra: the memory figure is from the operational protocol, the runtime is a
projection, and neither sizes a cache-injection workload.

**Judgments (not errors):** the downstream experiment was framed all-or-nothing — three separable
questions (does the perturbation change receiver behavior / does a practical scheme preserve quality /
does reuse improve serving), the first answerable alone; "exact-match of the sender-observed continuation"
is the wrong target (off-policy; not an answer to the receiver's prompt); the dump footprint does not
transfer to injection; under the PIC framing the unit of generalisation is a second *receiver*, and a
recalibrated τ changes the yardstick. Its priority order: scaled short cell (done: 0037/0038) → controlled
receiver-output comparison → another receiver (now the Llama branch) → n = 420 long rescore → defer larger
contexts and full serving.

## 5. Settled: zero on every handoff

Astra (R3-6, R1-7) could not verify the handoff-level universal from median / p10 / p90. From
`fstar_per_handoff` in each summary (summarizer output, not ledger text; read 2026-09-20):

| cell | handoffs | max same-K f*(τ_K) | nonzero |
|---|---|---|---|
| `results/e9` (0029) | 25 | 0.0 | 0 |
| `results/e9l` (0036) | 35 | 0.0 | 0 |
| `results/e9s` (0038) | 25 | 0.0 | 0 |

So "f*(τ_K) = 0 on every handoff" is supported; "at every matched token" is not. A paper sentence needs the
first form and a ledger figure for it: none of 0029 / 0036 / 0038 states a maximum.

## 6. What Astra wrote to the tree

All untracked on `main`, mtimes 09-14 02:51–03:22 local: `docs/2026-09-14-condition-1-status.md`,
`…-board-source.md`, `docs/2026-09-14-seed-condition-1.md`, `docs/reviews/2026-09-14-refutation-0025-0029.md`
(TEMPLATE ONLY), `docs/drafts/append_0039.py`, `docs/drafts/test_append_0039.py`; one-line edit to
`docs/drafts/README.md` ("0039 STAGED"); one patch to `docs/paper/tex/main.tex` (3 hunks; the pre-image is
recoverable from the patch's `-` lines). Its abstract and two introduction drafts exist only in the thread.

## 7. Condition 1: both paths, and the 0039 collision

- **Path A** (a recorded attack on 0032's two leads, two signatures): template empty; one signatory named
  by the operator, the second not identified.
- **Path B** (`append_0039.py`): an operator ruling accepting the 09-08 two-handoff re-verification in
  place of the attack, post-freeze and stated as such; releases 0029, 0038 and 0034's E9 figures.
  `--preview` ran clean on 09-16. **Not appended.**
- **Collision:** `origin/llama-second-family` appended its registration as **0039** on 09-18. The Path B
  script is ordering-guarded against `a5053b2` and will refuse; it needs renumbering and re-staging after
  that branch lands.
- Astra's chronology point stands either way: a refutation recorded now cannot satisfy a 09-08 freeze "as
  written"; only a numbered entry that says so can change the consequence.

## 8. Astra as workshop reviewer

Fit strong, contribution borderline. Five concerns: (1) no clear empirical takeaway — promote the seam
profile (0.260 adjacent to a seam vs 0.063 at 16+, `ledger:2203`) beside the ladder; (2) τ_K is the largest
vulnerability — self-anchored, no link to generation quality; (3) "real handoffs" are replayed through
Qwen, say so where the pair first appears; (4) prompt inequality does not establish lost prefix reuse; (5)
the weights axis dilutes the introduction — one sentence, no credit. Its one-line verdict: the strongest
supported contribution is *where* mismatch occurs and how its severity depends on tolerance; a zero under a
self-anchored tolerance cannot carry acceptance alone.

## 9. This session's work, with pointers

| work | where | state |
|---|---|---|
| Pick-up of the 09-16 ICLR seed: HEAD, gates, figure→entry greps, deadlines, missing trees, staged 0039 | session transcript; memory `linear-ceiling-iclr-2027` | done; ICLR since dropped |
| Codex forensics (what Astra wrote, which thread is open) | §1, §2, §6 here; memory `codex-traces-on-this-machine` | done |
| The five GPU runs, and Astra's critique | §4 here | done |
| Downstream-quality run narrowed to three cells (full recompute / stale reuse / mismatched null; next-token divergence on the 8 + 3 kept handoffs; upstream `kvt/cache.py` `build_cache` + `forward_with_cache` and the HellaSwag identity cell already exist) | this row | PROPOSED; unregistered |
| Co-author refutation rows (R0 admin + 14 attacks; Nanda's evidence standard) | `docs/reviews/refutation-0025-0029-rows.csv`, for import into the operator's tracker | 2026-09-20: the Codex seed that carried these rows was never run, was flagged by the operator as too much process, and is retired (deleted, never committed). Three Lead-B rows are already answered by 0025:1483-1492 (the prefix control is a separate S+1 prefill, distinct from the identity control, registered on one handoff); the live Lead-B attack is whether the control can fail (R9). `OPERATOR_ONLY_note` is to be hidden from the co-author's view |
| Branch state: `track-b` merged by patch-equivalence; `llama-second-family` = PR #5, CI green; `lcfm_anon` = the double-blind copy, keep | session transcript; memory `linear-ceiling-keep-process-light` | commands handed over; nothing run |
| Venue tracks: ICLR dropped; ARR October cycle (submission Oct 12, commitment Dec 23); MLSys 2027 dates unannounced | memory `linear-ceiling-iclr-2027` | read from the venue sites 09-19 |
| Async RL design for ARR (task-accuracy statistic, mid-generation swap, kill line Sep 26) | `docs/2026-09-19-async-rl-arr-design.md` (untracked) | PROPOSED; unregistered |

## 10. Open items by owner

**Operator:** Condition 1 (Path A, Path B, or withhold); the corrective entry for the 0029 / 0036 token
sentences and the 0025 / 0029 R² mislabel, carrying the per-handoff maximum of §5; the three-session 09-14
commit block; PR #5; whether the refutation seed and the ARR design stay in the tree.
**Next writing session:** strike "longer handoffs spend more of the margin", "nine in ten", and the
mis-denominated share from any seed or draft (the 09-16 ICLR seed lives in chat, not in this repo); enter or
cut outline v3's unprovenanced figures. The README, outline v3 and GPU-runs doc fixes are done (§12).
**Tooling, small:** score-file hashes into the comparator's `passed`; a cold directory outside `results/`.

## 11. Re-verify

```
cd ~/dev/linear-ceiling
git log --oneline -1                                           # a5053b2 when this was written
grep -n "every matched token\|needs recompute above\|before submission" README.md
grep -n "six kept\|six E9-long\|Every number cited\|57 GB\|31.56" docs/2026-09-11-gpu-runs-after-the-pivot.md
awk 'index($0,"57 GB")||index($0,"31.56"){n++} END{print n+0}' ledger/ledger.md    # 0
sed -n 2124,2134p ledger/ledger.md                              # three kept long + three bridge
sed -n 2359,2361p ledger/ledger.md                              # the share's definition
grep -n "passed =" docs/probes/2026-09-08-e9-independent-rescore-compare.py
grep -n "fp32\|89.7\|50,916\|0.8992" docs/paper/2026-09-11-lcfm-outline-v3.md
.venv/Scripts/python.exe -c "import json;[print(e,len(v),max(v.values()),sum(x>0 for x in v.values())) for e in ('e9','e9l','e9s') for v in [json.load(open(f'results/{e}/summary.json'))['fstar_per_handoff']['same_K']]]"   # e9 25 0.0 0 / e9l 35 0.0 0 / e9s 25 0.0 0
```

## 12. Fixes applied with this record

Made on 2026-09-20 in the same change that adds this document. Documentation only; no ledger entry, config,
result, code or test was touched.

| file | what changed | finding |
|---|---|---|
| `README.md` | four statements of "within tolerance / f* = 0 at every matched token" now say what 0023 defines: the MEAN over each handoff's matched tokens, with 0038 named for the tokenwise fraction; the yardstick paragraph no longer says "a token needs recompute above τ_K"; the H-E9 row quotes 0029's median and p10 / p90 | R1-3, R1-7, R2-2 |
| `README.md` | Condition 1's deadline reads as 0032 wrote it (the numbers-freeze gate, EOD 2026-09-08), states that it was not met, and that only a numbered entry changes the consequence | R1-2, R2-1 |
| `docs/paper/2026-09-11-lcfm-outline-v3.md` | dumps are fp16 [0025], the forward pass is fp32 [0026]; 89.7 % marked as the outline's own arithmetic; median 50,916 and the three bridge R² values marked as summary-file figures no entry states. Dated in-place notes, following this outline's own corrections table | R1-6, R1-8 |
| `docs/2026-09-11-gpu-runs-after-the-pivot.md` | dated amendment note under the status block stating both errors with their ledger evidence; body left as written | §4 |

**Not fixed, on purpose:** the immutable sentences in 0025 / 0029 / 0036 (a corrective numbered entry is the
operator's, and the allocator currently carries a staged 0039 that collides with the Llama branch); the 09-08
comparator (a co-author's tool, cited by a review record); superseded dated documents that repeat the token
claim (`docs/2026-09-06-gap-map-revisited.md:94`, outlines v1 and v2, `docs/archive/README-2026-09-09-status.md`),
which v3 and this record already mark as wrong.

Gates after the edits, run 2026-09-20 on the working tree at `a5053b2` + these changes: `ledger ok (blocks
unchanged vs HEAD)`, `scope ok`, seal `OK`, `436 passed, 1 skipped`. `README.md` no longer matches
`every matched token`, `needs recompute above` or `before submission`.
