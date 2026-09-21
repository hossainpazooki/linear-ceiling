# Handoff — E9-long R8 closed, outline v3 and the f* reading, the scaled short cell built, the abstract reviewed

2026-09-14 09:35Z (session `lcfm-sprint-e9l-review`, `9c42735d`; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\9c42735d-cc28-4309-8cae-07b555ed4ab9.jsonl`). This is the builds-and-review
session. The newest commit this brief describes is **`a5053b2`**, which equals HEAD and origin/main (fetched 09:24Z).
Its previous brief is `2026-09-10-e9l-independent-verification-outline-filled-and-the-r8-retry-corrected.md` at
`50bc439`. The e9s session's two 2026-09-14 briefs cover the sitting, entries 0037/0038 and the e9s backup; this brief does
not restate them.

Uncommitted in the tree:
- **This session:** this brief, its index row, and six learnings entries with their index rows.
- **Not this session's:**
  - The e9s session's close: its brief, two learnings entries and their index rows.
  - The Carryover manuscript session's close (`2f2c397b`, written 09:30–09:33Z in parallel with this one):
    `docs/handoff/2026-09-14-carryover-manuscript-fact-check-short-cell-figures-and-condition-1.md`, nine 2026-09-14
    learnings entries and their index rows. `docs/paper/tex/` is that session's superseded 09-13 scaffold.
  - The condition-1 files: `docs/2026-09-14-condition-1-*.md`, `docs/2026-09-14-seed-condition-1.md`,
    `docs/reviews/2026-09-14-refutation-0025-0029.md`, `docs/drafts/append_0039.py`, `docs/drafts/test_append_0039.py`, and
    the `docs/drafts/README.md` change.

## Current state

- **built — the E9-long R8 backup is closed.** The verifier printed `BACKUP VERIFIED` at 2026-09-10T18:28:26Z. That
  followed a squash (18:20:30Z) and the operator making the dataset public, after the private storage limit had stopped
  two attempts. This session then re-listed it without a token: 725 files (724 plus `.gitattributes`), 61.94 GB, and all
  529 fingerprints in `report.json` match (476 by LFS sha256, 53 read back and hashed). The tools landed in `6f400ab`
  (`tools/hf_backup.sh` with `ALLOW_PUBLIC=1`, `tools/hf_prune_backup.py`); R8 allows public datasets as of `d0b91db`.
  re-verify: `.venv/Scripts/python.exe -c "from huggingface_hub import HfApi; a=HfApi(token=False); r='hossainpazooki/linear-ceiling-e9l-2026-09-10'; print(a.dataset_info(r).private, len(a.list_repo_files(r, repo_type='dataset')))"` → `False 725`.
- **built — outline v3** `docs/paper/2026-09-11-lcfm-outline-v3.md` (`cf4047f`, `3f494f7`), with `docs/paper/2026-09-11-seed-lcfm-v3.md`
  and `docs/2026-09-11-gpu-runs-after-the-pivot.md`. It frames the paper as position-independent caching (PIC). f* is
  defined as registered, a mean-repair statistic. The per-token tail figures are marked PENDING/NOT IN, counted at the
  registered τ_K. The receiver-configuration confound is stated, and a corrections table records seven fixes to the seed,
  including this session's own misreading. **Stale:** §5.2 still says the length reading waits on the scaled short cell,
  and 0038 now answers that. The GPU-runs doc's item-1 status line still reads "BUILT, registration STAGED, not run".
  re-verify: `grep -c "30,701" docs/paper/2026-09-11-lcfm-outline-v3.md` → `1`; `grep -n "Status 2026-09-13" docs/2026-09-11-gpu-runs-after-the-pivot.md` → the stale line.
- **built — the e9s instrument** (`9a7816d`): `config/e9s.toml`, `src/linear_ceiling/e9_compare.py`,
  `tests/test_e9_scaled_short.py`, `docs/2026-09-13-seed-e9-scaled-short-cell.md`, and the registration script the e9s
  session appended as 0037 (`c360950`). The sitting and 0038 (`44468ab`) used the instrument unchanged. Before staging,
  this session checked the home alignment pass against 0029: 68 / 25 / 43, and the same ids, alignments, text hashes and
  keep draw.
  re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_e9_scaled_short.py tests/test_e9_pertoken.py` → `23 passed`; `grep -n '^### 0038 ' ledger/ledger.md` → line 2310.
- **built — PR #4 reviewed before its merge** (`ffef90a`). Both input bugs it fixes reproduced on the pre-merge main:
  `f_star([nan, 0.1], 0.3186)` → `0.5` and `f_star([-0.1, 0.1], 0.3186)` → `0.0`. Its note's one-handoff table for
  `django-10973#78` also reproduced from the home record to every printed digit: n 13,075, mean 0.2023384457, 1,998
  tokens over τ_K, f* 0.0 / 0.3856978967 / 0.9398087954.
  re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_e9_pertoken.py -k refuses` → `7 passed, 9 deselected`.
- **verified — f* = 0 is a mean within τ_K, not "no token over τ_K".** Tokens over τ_K exist on all 60 handoffs:
  9,047 of 155,257 (0029) and 30,701 of 387,508 (0036). The co-author review `ef4c2ca` and PR #4's note agree
  independently. Detail: `docs/learnings/2026-09-14-f-star-zero-says-the-mean-is-within-tau-k-tokens-over-tau-k-exist-on-every-handoff.md`.
  re-verify: that entry's `re-verify:` line → `35 30701 387508 30711`.
- **verified — the co-author's "inconsistency" in the E8 appendix table is rounding.** All 30 drop and change cells equal
  round(summarizer value, 4). Seven differ by one unit from subtracting the displayed columns. The ledger is unchanged.
  Detail: `docs/learnings/2026-09-14-e8-table-differences-are-rounded-exact-values-seven-of-thirty-differ-from-subtracting-the-rounded-columns.md`.
  re-verify: that entry's line → `0.7263 0.7264 0.7263491288189993`.
- **corrected — three pieces of this session's advice were wrong.**
  1. It marked the universal-token sentence verified because it matched 0029's prose; that is now a learnings entry.
  2. It counted tokens over τ_K with a typed 0.3186 and got 30,711 instead of 30,701; that is a learnings entry, and
     `3f494f7` fixed the outline.
  3. It diagnosed two staged files as stray copies when they were the result of an unconcluded merge, so the prescribed
     `git pull --rebase` failed on `MERGE_HEAD`. `git merge --abort` followed by the rebase resolved it; the transcript
     has it at 2026-09-14T01:52Z.
  None has a lasting effect: history is linear through `9a7816d`, and `3f494f7` corrected the count.
- **reviewed — the abstract, as the operator pasted it into this session.** The manuscript itself (`neurips/main.tex`)
  is not on this machine, per the Carryover brief, and this session never read it. This session reported four problems:
  - "a thirtieth of the tolerance" was arithmetic, not a style choice: 0.03 / τ_K = 0.094.
  - The cross arm was placed on the weights axis, but it is a cross-model transfer on the context axis.
  - "Model switch" is the corpus's word for the handoff event itself.
  - "60 real handoffs" pooled two cells that 0035 says are never pooled.
  It also advised that the weights axis carry two measured anchors and a registered, unrun lag ladder, with no ordering
  and no predicted value. Whether the manuscript took these corrections is unverified here. The only file on this machine
  is the Carryover session's superseded scaffold: at 09:25Z it had no "thirtieth", and its line 106 reads "The weights
  axis would take the same instrument…". That says nothing about the manuscript.
- **planned:**
  - The corrective f* entry.
  - §5.2 rewritten from 0038.
  - A caption for the E8 appendix table, or a generated table.
  - The body paragraph that backs the abstract's weights-axis sentence: the two anchors on one table and the ladder's
    falsification condition.
  - The GPU-runs doc's item-1 status line.

## Locked decisions

- **E9-long's files stay local AND are backed up, and the backup dataset is public.** Reason: the operator's rulings
  ("E9L stays local and backed up to HF", 2026-09-10; R8 allows public, `d0b91db`, 2026-09-11), and the private tier
  stopped the push twice.
- **The paper is framed as a measurement of PIC's quantity**: non-prefix reuse at a handoff, read as an oracle recompute
  floor. Reason: E9 measures the residual after position correction, the quantity every PIC repair method targets (seed
  §1), and the abstract the operator marked final names PIC.
- **f*(τ_K) is written as registered, with no universal-token claim anywhere.** Reason: 0023 defines it on the mean of
  the remaining tokens, and tokens over τ_K exist on every handoff (learnings entry).
- **Tail figures (tokens over τ_K, per-handoff means) stay NOT IN** until a summarizer emits them and a numbered entry
  carries them. Reason: 0006's provenance rule, kept by 0032 and 0035.
- **The cross-model arm is the context axis, and it appears beside the same-model zero, labeled descriptive and
  attributed to the map.** It is the same tokens at the same re-rendered positions, with the source's KV passed through
  the k = 1 map (0023's E9-cross). Reason: 0032's clause (kept by 0035) requires it beside the same-model result, and
  0027/0029/0036 make it decide nothing.
- **The weights axis is stated as two measured anchors plus a registered, unrun lag ladder, with no ordering and no
  predicted value.** Reason: "an update is a smaller step" is unmeasured and contested. PipelineRL §5.1 found retained
  caches diverge after in-flight updates, and KVShareArena found checkpoint-fit adapters lose quality on another
  checkpoint; a prediction without a number reads as a claim. Status: this session's recommendation to the operator. It is
  not an operator ruling on record, and it has not been checked against the manuscript, which is not on this machine.
- **"Model switch" names the handoff event and never a weight change.** Reason: the corpus's Lane A switches are model
  switches mid-trajectory. Using the term for the weights axis names the context axis's event.
- **The E8 tables' differences stand as recorded.** Reason: 30 of 30 equal the summarizer's full-precision value rounded.

## Reuse map

- `tools/hf_backup.sh` (`--check`, `--verify-only`, `ALLOW_PUBLIC=1`), `tools/hf_prune_backup.py` (dry run first, then
  `--apply --expect-ops N`, with a parent-commit guard), `tools/hf_verify_backup.py` (both directions).
- `config/e9s.toml`, `src/linear_ceiling/e9_compare.py`, `tests/test_e9_scaled_short.py` — the template for any
  configuration-matched rerun of an existing cell. The comparison refuses on a different handoff set, a different pairing,
  an incomplete run, a report written under another config, or an edited record.
- `docs/probes/2026-09-11-e9l-record-recompute.py` (co-author) — recomputes 0036 without a token from the public backup's
  2.5 GiB of small records, and reports integrity, arithmetic and the prose gap separately.
- `docs/reviews/2026-09-11-clean-clone-reproduction.md` — an outside reproduction of 0036, with a proposed corrected wording
  of the f* sentence that the corrective entry can adopt.
- `docs/2026-09-13-e-rl-validation.md` (PR #4) — for the E-RL design doc: the checkpoint-coverage constraint on the lag
  ladder (an anchor at 8 with lag 40 needs checkpoint 48), and reporting the mean log-ratio beside ESS.
- `docs/paper/2026-09-11-seed-lcfm-v3.md` §6 — the literature sweep with provenance codes; rows marked S or R are cited
  for existence only.
- The learnings entries' `re-verify:` one-liners — each recomputes its figure from the gitignored `results/` with the
  summarizer's own functions.

## Invariants

- **The f* reading.** Never write that no matched token exceeds τ_K, or that every token agrees; f* = 0 means the
  handoff's mean is within τ_K. Breaks: the claim is false on all 60 handoffs, and three outside readers have already
  found it.
- **τ comes from config.** Read it from `config/e9*.toml` or a summary's `rule` block, never type it. Breaks: counts shift
  (30,711 vs 30,701).
- **No token-tail figure in the paper** without a summarizer and an entry. Breaks: 0006's provenance rule.
- **The cross arm** sits beside the same-model zero, labeled descriptive, on the context axis. Breaks: 0032's clause; a
  reader takes 0.93/0.96 for a weights-axis result.
- **No weights-axis ordering or prediction.** E-RL is designed, unregistered and unrun. Breaks: an unmeasured claim that a
  reviewer can rebut with PipelineRL §5.1.
- **Never `hf upload .`**; pass the absolute staging path. Breaks: the repository, `.venv` and ignored `results/` go into
  the dataset, which is now public.
- **Entry numbers.** Entries 0025–0038 are immutable. 0039 is allocated in `docs/drafts/README.md` by the condition-1
  session, so a corrective f* entry takes the next free number at staging, never 0039.
- **Indexes.** `docs/learnings/LEARNINGS.md` and `docs/handoff/HANDOFF.md` must be committed together with the files their
  rows point at. Both now carry rows from three sessions. Breaks: the gate fails on a row whose file is missing.
- **Git.** History is the operator's. Stage explicit paths, never another session's in-progress files, and add no
  attribution trailers.
- **Double-blind.** The public datasets resolve to the account name; the paper names neither the datasets nor the repo.

## Open / next

1. **Commit all three 2026-09-14 session closes in one commit** (operator), because both indexes carry rows for all three:

   ```bash
   cd ~/dev/linear-ceiling
   # Three session closes: HANDOFF.md and LEARNINGS.md hold rows for each, so they land together
   git add docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md \
     docs/handoff/2026-09-14-e9s-closed-backup-verified-and-a-second-session-on-condition-1.md \
     docs/handoff/2026-09-14-carryover-manuscript-fact-check-short-cell-figures-and-condition-1.md \
     docs/learnings/2026-09-14-f-star-is-a-lower-bound-only-against-real-prefill-under-its-own-remaining-token-criterion.md \
     docs/learnings/2026-09-14-minipic-found-no-public-traces-to-evaluate-pic-on.md \
     docs/learnings/2026-09-14-pipelinerl-measures-stale-against-recomputed-kv-in-its-body-not-its-abstract.md \
     docs/learnings/2026-09-14-the-abstract-0-95-is-the-scaled-short-key-figure-and-the-long-value-figure-also-rounds-to-0-95.md \
     docs/learnings/2026-09-14-the-bridge-value-r2-median-0-8603-is-a-summary-figure-no-entry-states.md \
     docs/learnings/2026-09-14-the-deepseek-v4-1-flash-card-never-calls-kv-a-first-order-cost.md \
     docs/learnings/2026-09-14-the-k1-map-was-fit-on-40-sequences-and-tau-comes-from-the-other-10.md \
     docs/learnings/2026-09-14-the-manuscript-source-and-a-latex-toolchain-are-not-on-this-machine.md \
     docs/learnings/2026-09-14-upstream-hellaswag-records-carry-no-correctness-field-accuracy-must-be-recomputed-byte-normalized.md \
     docs/learnings/2026-09-14-a-counted-xargs-grep-under-pipefail-kills-the-script-on-the-clean-outcome-and-a-piped-tail-hides-it.md \
     docs/learnings/2026-09-14-e9-compare-json-hash-depends-on-how-the-long-summary-path-was-spelled.md \
     docs/handoff/2026-09-14-r8-closed-outline-v3-the-f-star-reading-e9s-built-and-the-abstract-review.md \
     docs/learnings/2026-09-10-hf-upload-folder-ignores-the-local-gitignore-so-a-repo-root-upload-pushes-venv-and-ignored-results.md \
     docs/learnings/2026-09-10-a-private-hf-dataset-hit-its-storage-limit-with-under-43-gb-at-head-after-a-stray-upload-was-deleted.md \
     docs/learnings/2026-09-14-f-star-zero-says-the-mean-is-within-tau-k-tokens-over-tau-k-exist-on-every-handoff.md \
     docs/learnings/2026-09-14-a-tolerance-typed-at-four-decimals-shifts-the-over-tolerance-count-read-tau-k-from-the-config.md \
     docs/learnings/2026-09-14-e8-table-differences-are-rounded-exact-values-seven-of-thirty-differ-from-subtracting-the-rounded-columns.md \
     docs/learnings/2026-09-14-the-tau-ladder-0-03-is-a-tenth-of-tau-k-not-a-thirtieth.md
   git commit -m "docs: 09-14 session closes — e9s backup; manuscript fact check; R8 closed, the f* reading, abstract review"
   git push
   ```

   This replaces item 1 of the e9s session's brief. Confirm the other two sessions have stopped writing before running it.
   Not staged: `docs/drafts/README.md` and the condition-1 files (another session's), the `docs/paper/tex/` scaffold,
   `.claude/`.
2. **The corrective f* entry** is owed and gets its number at staging, after 0039. It should cite the co-author review
   (`ef4c2ca`), PR #4's note (`ffef90a`) and this session's learnings entry, and state the corrected reading of 0029's and
   0036's sentences without moving either verdict. The README's H-E9 row carries the same wording.
3. **Paper, before 11:59Z.** Condition 1 comes first: the Carryover brief records that 0038 re-measures 0029's 25
   handoffs, so 0029's, 0038's and 0034's E9 figures all stay withheld until condition 1 is ruled.
   - §5.2 from 0038, only if condition 1 releases it, and after the out-of-loop read.
   - The E8 appendix table caption: differences computed at full precision, then rounded.
   - A check that the abstract's weights-axis sentence has a body paragraph to point at.
4. **The GPU-runs doc's item-1 status line** → ran, 0037/0038 (living doc).
5. **Revoke the HF write tokens used for both pushes (R9).** This session did not verify revocation.
