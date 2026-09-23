# Handoff — Carryover manuscript: fact check, the short-cell figures in the abstract, and condition 1

2026-09-14, written ~09:30Z. Describes linear-ceiling `a5053b2` (HEAD; working tree also carries untracked and modified
files from two other sessions, listed below) and the upstream `../kv-transfer-replication` at `063f402`. The manuscript
under review is the operator's `neurips/main.tex`, which is **not on this machine**; everything about it was checked
from text pasted into this session (transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl`).

Parallel work, not this session's, sits in the same tree. The 09:20Z e9s-close brief is one. The other is the
condition-1 session: `docs/2026-09-14-condition-1-{status,board-source}.md`, `docs/2026-09-14-seed-condition-1.md`,
`docs/reviews/2026-09-14-refutation-0025-0029.md`, `docs/drafts/append_0039.py` + `test_append_0039.py`, and the modified
`docs/drafts/README.md`. Do not edit or commit those as this session's.

## Current state

- **built — full fact check of the pasted manuscript.** Every numeric macro was matched against its ledger entry or
  summary file: entries 0009, 0018, 0020, 0023, 0025, 0029, 0031, 0034, 0035, 0036, 0038, and `results/{e9,e9l,e9s}/summary.json`.
  All matched. The long-summary sha256 in the manuscript's comment matched the file. Every `[entry:line]` comment
  reference landed on the cited ledger lines. Related-work descriptions matched their sources for EPIC, CacheBlend,
  Heo et al., C2C, DroidSpeak, KVCOMM, KVShareArena, TraceLab, Stable Asynchrony, AReaL, Laminar, PipelineRL and vLLM.
  The problems found were contradictions, not wrong numbers; see Open / next item 2.
  re-verify: .venv/Scripts/python.exe -c "import json;L=json.load(open('results/e9l/summary.json'));X=json.load(open('results/e9s/summary.json'));print(L['fstar']['cross_K']['median'],L['fstar_ladder']['same_K']['0.03']['median'],X['fstar']['cross_K']['median'],X['fstar_ladder']['same_K']['0.03']['median'],all(v==0.0 for v in L['fstar_per_handoff']['same_K'].values()),all(v==0.0 for v in X['fstar_per_handoff']['same_K'].values()))"   # 0.9639.. 0.5254.. 0.95 0.2930.. True True
- **built — the condition-1 answer, given to the operator.** The short half cannot enter the paper as the record
  stands. 0038 re-measures 0029's exact 25 handoffs, and 0034's E9 arm re-scores 8 of 0029's kept handoffs from 0029's
  dumps, so both inherit the withheld status. The operator turned this into a seed, and the condition-1 session wrote
  it up; the seed records the release scope the operator confirmed as 0029, 0038 and 0034's E9 figures.
  re-verify: sed -n 1947,1951p ledger/ledger.md && grep -n "0029, 0038, and 0034" docs/2026-09-14-seed-condition-1.md
- **built, superseded — `docs/paper/tex/{main.tex,refs.bib}`, untracked.** This session's 09-13 scaffold, overtaken by
  the operator's manuscript. `refs.bib` is still useful: 25 entries, each with a provenance comment. Twenty were read
  from arXiv abstract pages or docs on 09-13 and 09-14; five are tagged `[memory]` and unconfirmed (vLLM/SOSP, SGLang,
  YaRN, Qwen3, SWE-bench). Its keys differ from the manuscript's (`crosskv`, `yarn`, and others).
  re-verify: git status --short docs/paper/tex && grep -c "^% \[memory\]" docs/paper/tex/refs.bib   # ?? docs/paper/tex/, then 5
- **in-progress, chat only — abstract.** The operator's live abstract reports 25 scaled-short and 35 long handoffs, "the
  median is zero in both cells", cross 0.95 short / 0.96 long, and 0.29 / 0.53 at τ = 0.03. A reviewer flagged that the
  body gives neither the scaled-short f*(τ_K) nor its cross f*(τ_K); both are true figures (0038: 0.0000 on all 25;
  cross K 0.9500). This session supplied a long-cohort-only abstract consistent with condition 1, and macros plus a
  sentence for the case where the short cell is released. Whether either was applied is not known here.
- **in-progress, chat only — Limitations rewrite.** Five paragraphs were supplied, covering: the oracle statistic
  scoped against a full-cache criterion; no generation or serving measurement; the tolerance as a reference; replay on
  one pair; the extended receiver and approximate matching. There was also one conditional sentence for a released
  short cell. Application is not known.
- **planned, not started.** Check `neurips/references.bib` and the `dblblindworkshop` style option; compile; resolve
  the off-ledger figures (Open / next item 3).

## Locked decisions

- **Short-half figures stay out of the paper until a numbered entry admits them.** This covers 0029, 0038, and 0034's E9
  figures. Reason: 0032 says that without the recorded refutation "the 4-pager's E9 section is cut to one sentence
  marked as ongoing work and the figures are withheld", and "a later entry records it either way". Neither a brief
  nor a board can loosen an immutable entry. Pick-up check: does a numbered entry after 0038 now exist?
  (`grep -n "^### 0039" ledger/ledger.md`).
- **DeepSeek is out of the introduction.** Reason, per the operator's comment in the manuscript: "removing deepseek
  paper from intro due to workshop topic". It also stays out because the card does not support the attributed wording
  (learning `2026-09-14-the-deepseek-v4-1-flash-card-never-calls-kv-a-first-order-cost`).
- **The upstream replication is featured, and Related Works opens with it.** Reason: the operator asked that the paper
  "start with, or at least feature heavily, the upstream work in kv-transfer-replication". The manuscript's Related
  Works now opens "Cross-model transfer" with the reimplementation.
- **Title: "Carryover: The Reuse Margin of a Stale KV Cache in Long-Horizon Agents".** Reason: the operator set it on
  09-13. Pick-up check: "Reuse Margin" is still undefined in the body.
- **A figure enters the paper only when a numbered entry states it.** Reason: outline v3's gate, which carries entry
  0032's provenance terms. See `docs/paper/2026-09-11-lcfm-outline-v3.md`, "Gate".
- **f* is described as the registered mean-repair statistic, never as "no token exceeds τ_K".** Reason: 5.8% and 7.9% of
  matched tokens exceed τ_K on every handoff (outline v3 corrections table).

## Reuse map

- **Figure sources.** Ledger 0023 lines 1252–1297 hold δ, f*, τ, the pooled-versus-head-averaged R² note, and the
  "oracle lower bound" wording rule. Line references: 0029 from 1755, 0036 from 2173, 0038 from 2310, E8 band at 0009
  lines 69–70, 0031's registered-protocol counts, 0034's k = 1 rows. `results/e9/summary.json` `coverage_comparison`
  holds the corpus table's p10 and p90 values.
- **Summary keys** in `results/{e9,e9l,e9s}/summary.json`: `fstar`, `fstar_per_handoff`, `fstar_ladder`,
  `bridge.per_handoff.{r2_K,r2_V}`, `own_norm_delta_gt_1_fraction`, `depth_profile_median_per_layer`, `matched_fraction`.
  These files are gitignored, so they exist locally and in the HF backups only.
- **Upstream replication**, read-only. The mapper report is at `../kv-transfer-replication/results/mapper/qwen3-0.6b-to-1.7b/r2.json`.
  HellaSwag lives at `results/hellaswag/qwen3-0.6b-to-1.7b/{summary.json,*.jsonl}`; recompute it byte-normalized (learning
  `2026-09-14-upstream-hellaswag-...`). The upstream `docs/ledger.md` covers Run 2 (line 217), Run 4 (316), the
  adversarial pass (557) and the five questions (737).
- **`docs/paper/tex/refs.bib`**: verified title, author, date and venue metadata to copy into the manuscript's bibliography
  under its own keys.
- **The fact-check recipe**: read each macro's value from the summary key or ledger line above, and `sed -n` the line
  ranges cited in the manuscript's comments.
- **The condition-1 session's files**: the status note, board excerpts, Path A template and staged `append_0039.py`.
  Read them; do not re-derive them.

## Invariants

- `ledger/ledger.md` is append-only, and entries 0001–0038 are immutable. `append_0039.py` runs only with `--preview`
  unless the operator appends. Breaking this breaks the entry chain `ledger_check` enforces.
- No paper number without an entry. `\bridgeRtwoV` 0.8603 is currently in the manuscript and on no entry (learning).
- Wording of f*: mean repair. Use "oracle lower bound" with both reasons, per 0023 line 1280, scoped: it is not a lower
  bound under a full-cache criterion (learning).
- The cross-model arm mixes mapping error with context change. Never present it as map error alone.
- The recorded handoffs are switches between Claude 3.5 Sonnet and o1-mini, and the measurement is a Qwen3 replay. Do
  not file "model switch" under the weights axis only.
- The short and long cohorts are never pooled. No length-alone attribution: 0038's configuration shares are 0.4285 and
  0.3916.
- Double-blind: no repo name, dataset, handle or link in the PDF. The manuscript's source comments name people, so
  strip them before any source is posted.
- `../kv-transfer-replication` is read-only. Git history is the operator's.
- Cite only what was read. Two sources were not confirmable by grep: KVShareArena's and SemPIC's corpus sentences
  (learning).

## Open / next

1. **Operator: rule on condition 1.** Path A is a dated refutation under `docs/reviews/` with two signatures. The
   condition-1 session records one name supplied, Farhan Ishmam, and the second not identified. Path B is `append_0039.py`,
   staged: run `--preview`, then the operator appends. **This blocks** the manuscript's abstract short-cell figures, its
   Controls paragraph (0029's 0.9344, 2.009 and 1.962), and its matched-configuration paragraph. Until the ruling, those
   come out.
2. **Apply to `neurips/main.tex`**, which is off this machine. Six contradictions:
   (a) the condition-1-bound figures above;
   (b) "fit on 50 generic sequences" against a held-out τ; it is 40 fit and 10 held out;
   (c) "model switch" filed under weight changes, while the handoffs are model switches measured with fixed weights;
   (d) Limitations and Related Works speak of a native cohort the paper does not report;
   (e) Future Work "no claim about its outcome" against the E-RL appendix "We hypothesize…", with Conclusion and Future
   Work repeating each other;
   (f) Limitations denies the lower bound without 0023's scoped wording.
   Smaller items: "Reuse Margin" is undefined; PIC is expanded twice; "below τ" should be "at or below"; the Taxonomy
   and Corpus manifest appendices are empty.
3. **Off-ledger figures.** `\bridgeRtwoV` 0.8603 is confirmed absent from the ledger. `\bridgeRtwoK` 0.8932, the long
   own-norm diagnostic and the depth profile were not grepped: check each, then enter or cut.
4. **Wherever the manuscript lives**, check `references.bib` against `docs/paper/tex/refs.bib`, and confirm the style
   option; compile there. Also cite PipelineRL's stale-versus-recomputed finding (learning).
5. **Deadline.** The CFP was extended to 2026-09-13 23:59 AoE, which is 2026-09-14 11:59 UTC (outline v3, CFP read 09-11).
   This brief was written about 09:30Z. Submission status is not recorded here.
6. **Commit block** (operator; Git Bash; explicit paths). The two index files also carry the 09:20Z session's uncommitted
   rows, so commit that session's block first or together. Not folded in: `docs/paper/tex/`, a superseded scaffold, and
   every condition-1 file, which is another session's.

```bash
cd ~/dev/linear-ceiling
# This session's handoff brief and nine learnings; the index files also hold the 09:20Z session's rows
git add docs/handoff/2026-09-14-carryover-manuscript-fact-check-short-cell-figures-and-condition-1.md \
        docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md \
        docs/learnings/2026-09-14-the-k1-map-was-fit-on-40-sequences-and-tau-comes-from-the-other-10.md \
        docs/learnings/2026-09-14-f-star-is-a-lower-bound-only-against-real-prefill-under-its-own-remaining-token-criterion.md \
        docs/learnings/2026-09-14-the-abstract-0-95-is-the-scaled-short-key-figure-and-the-long-value-figure-also-rounds-to-0-95.md \
        docs/learnings/2026-09-14-the-bridge-value-r2-median-0-8603-is-a-summary-figure-no-entry-states.md \
        docs/learnings/2026-09-14-upstream-hellaswag-records-carry-no-correctness-field-accuracy-must-be-recomputed-byte-normalized.md \
        docs/learnings/2026-09-14-the-manuscript-source-and-a-latex-toolchain-are-not-on-this-machine.md \
        docs/learnings/2026-09-14-the-deepseek-v4-1-flash-card-never-calls-kv-a-first-order-cost.md \
        docs/learnings/2026-09-14-pipelinerl-measures-stale-against-recomputed-kv-in-its-body-not-its-abstract.md \
        docs/learnings/2026-09-14-minipic-found-no-public-traces-to-evaluate-pic-on.md
git commit -m "docs(handoff): manuscript fact check, short-cell figures, condition 1"
git push
```
