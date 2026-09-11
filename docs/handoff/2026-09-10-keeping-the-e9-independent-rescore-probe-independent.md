# Handoff — keeping the E9 independent rescore probe independent

2026-09-10 13:56Z (session `e9l-aws-run`, `01VDywUv8N146LzzLgRDTihm`). Newest commit this brief describes: **`bb85a28`** on
**remote** `main`, the merge of PR #2 by `hossainpazooki` at 2026-09-10T13:48:07Z. **Local `main` is `50bc439` and does
not contain it.** Local and remote have diverged on purpose: the operator prefers the mismatch for now and will explain
it. Every file path below under `docs/probes/` or `docs/reviews/` exists on remote `main` only until the two are
reconciled, which is the operator's call. This brief does not supersede the other 2026-09-10 briefs; it adds one topic.

## What "independent" means here

PR #2 added an independent check of E9's archived scores that sits outside the evidence path it checks. Its record
states the boundary itself: the scientific values and the verdict stay governed by `results/e9/`, the fail-closed
`summarize_e9` path and entry 0029. The check has two halves, and each can lose its independence in a different way.

- **The cold rescore.** Someone runs upstream `scripts/score_positions.py`, pinned at `d5786df`, from the archived raw
  dumps, mapper and alignment, in a clean environment, without going through linear-ceiling.
- **The comparator.** `docs/probes/2026-09-08-e9-independent-rescore-compare.py` compares that cold output with the
  archive by exact equality and emits a hashed report.

## Current state

- **built / verified — the merge.** PR #2 is merged at `bb85a28`, with parents `700d830` and `d009f36`. It adds exactly two
  files and changes nothing else.
  re-verify: `gh pr view 2 --json state,mergeCommit --jq '"\(.state) \(.mergeCommit.oid)"'` -> `MERGED bb85a28d341e5b31951352b7744ce9666b9cb9bc`;
  `gh api repos/hossainpazooki/linear-ceiling/commits/bb85a28 --jq '[.files[].filename]'` -> the two paths.
- **built / verified — the comparator shares no code with what it checks.** It imports only the standard library and
  numpy: `__future__`, `argparse`, `hashlib`, `json`, `pathlib`, `numpy`. It has its own hash function.
  re-verify: `grep -nE "^(import|from) " docs/probes/2026-09-08-e9-independent-rescore-compare.py` -> those six lines and no `linear_ceiling` or `kvt`.
- **built / verified — exact equality, no tolerance.** Scores compare with `==` and arrays with `np.array_equal`. No
  tolerance constant or close-comparison appears in the code; the one occurrence of the word "tolerance" is the docstring
  saying drift must not be absorbed into one.
  re-verify: `grep -cE "allclose|isclose|atol|rtol|_close\(" docs/probes/2026-09-08-e9-independent-rescore-compare.py` -> `0`.
- **built / verified — nothing on the evidence path references it.** No code under `src/`, `tests/`, `config/` or
  `tools/`, and no ledger entry, names the probe or the review record.
  re-verify: `grep -rnE "independent-rescore-compare|independent-reverification" src tests config tools ledger` -> no output.
- **verified — detection is non-vacuous.** Moving one element of one array by a single ULP fails with exit 1 and names
  the array. Learnings entry `2026-09-10-the-independent-rescore-probe-passes-a-self-comparison-only-the-score-json-seconds-field-exposes-it`.
- **verified GAP — a self-comparison passes.** Pointing the cold arguments at the archive itself passes with exit 0.
  Only the report's score-JSON hashes expose it: upstream records wall-clock `seconds` in that file, so a separate run
  cannot reproduce its bytes. Token hashes cannot expose it, because numpy writes identical `.npz` bytes for identical
  arrays. Same learnings entry.
- **verified GAP — the review's recipe collides with the summarizer's output.** The record's re-run recipe reads cold
  files from `$RECHECK/$HANDOFF.json` and `.tokens.npz`, and `summarize_e9` writes precisely those names into
  `results/e9/recheck/`. Feeding those in fails on this Windows machine, but only through float jitter; on a matching
  Linux platform it would likely pass while being the evidence path grading itself. Learnings entry
  `2026-09-10-the-review-recipe-recheck-directory-collides-with-summarize-e9s-own-recheck-output`.
- **verified — upstream has moved under the pin.** `score_positions.py` imports `kvt.data` and `kvt.pertoken`, and both
  changed after `d5786df`: `kvt/pertoken.py` at `223f469`, `kvt/data.py` with the RoPE spec at `063f402`. A rescore at
  upstream `main` runs different code from the one the review pinned.
  re-verify: `git -C ../kv-transfer-replication diff --stat d5786df HEAD -- scripts/score_positions.py kvt/` -> `kvt/data.py`, `kvt/models.py`, `kvt/pertoken.py`, `kvt/rope.py` changed.
- **verified DEFECT in the review record — the archive pin is not a full hash.** It pins the private transport archive at
  `a45e9ee8c511f5aab738400f06a2462b4fee539`, which is 39 hex characters, one short of a full commit id. The repo records
  only the 8-character prefix `a45e9ee8` elsewhere, so the exact revision cannot be recovered from the repo.
  re-verify: `printf %s a45e9ee8c511f5aab738400f06a2462b4fee539 | wc -c` -> `39`.
- **planned, not built** — any guard that enforces the invariants below in CI. See Open / next.

## Locked decisions

- **The probe and its record are supporting evidence, never ledger evidence.** Reason: an independent check that the
  evidence path depends on is no longer independent, and the record's own boundary section says exactly this. Holds.
- **The comparator keeps exact equality and never takes entry 0028's tolerance.** Reason: 0028's tolerance is part of the
  evidence path under test, so importing it would grade the evidence path by its own rule; exact equality is what makes
  platform drift visible, and the one-ULP control shows it working. Holds.
- **The cold rescore runs upstream at a detached `d5786df`.** Reason: the scorer's imports changed after that commit.
  This is the same shape as ruling (b) of 2026-09-09 for `summarize_e9`, and upstream `main` is restored afterwards.
- **The archive is transport only and stays unnamed in double-blind material.** Reason: the record states it, and the
  paper is under double-blind review.
- **The review record belongs to its reviewer.** Reason: an independent attestation that the checked party rewrites is no
  longer independent. Corrections go to the reviewer, or into a new dated note, never into that file.

## Reuse map

- `docs/probes/2026-09-08-e9-independent-rescore-compare.py` — the comparator. Run it without `--out` to print the report.
- `docs/reviews/2026-09-08-e9-independent-reverification.md` — the pinned inputs, the sampled handoffs and the boundary
  statement. Read the boundary before citing the review anywhere.
- `docs/handoff/2026-09-09-ruling-b-detached-and-session-close.md` — the detached-checkout procedure for a `d5786df` run,
  including restoring upstream `main` afterwards.
- `src/linear_ceiling/summarize_e9.py` lines 395–407 — the recheck writer, so you know which directory never to feed in.
- `results/e9/scores/`, `results/e9/tokens/` — the archive side of every comparison, at home and in the E9 backup.

## Invariants

1. **The comparator never imports `linear_ceiling` or `kvt`, and never copies their code.** Breaks: it would share the code
   it is checking, and a bug common to both would pass.
2. **No gate, test, summarizer, config or ledger entry calls, imports or cites the probe as evidence.** Breaks: circularity;
   the check becomes part of the path it verifies.
3. **Exact equality stays.** No tolerance, no close-comparison, no constant from 0028. Breaks: the check inherits the rule
   under test and absorbs the drift it exists to show.
4. **Cold inputs never come from `results/e9/recheck/`, `results/e9l/recheck/`, or anything else `summarize_e9` writes.**
   They come from a directory outside `results/`, produced by a recorded run of upstream `score_positions.py` at a detached
   `d5786df`. Breaks: the evidence path grades itself, and on Linux it would pass without a sound.
5. **A report whose `inputs.archive_score.sha256` equals `inputs.cold_score.sha256` is not a cold rescore, whatever `passed`
   says.** Equal token hashes are not a signal either way. Breaks: a self-comparison reads as a reproduction.
6. **`--out` never points under `results/`.** Breaks: `results/e9/` is never rewritten, and a stray file there would also
   travel into the HF backup.
7. **The reviewer's record is not edited by this side.** A behavior change to the comparator bumps its schema string
   `linear-ceiling.independent-e9-rescore-compare.v1` and gets a new dated review note. Breaks: the attestation stops being
   the reviewer's.
8. **Extending the check to E9-long means a new probe and record pinned at `063f402`, not a retarget of this one.**
   Breaks: this record's pins, archive and sample describe E9 only; retargeting would silently change what it attests.

## Open / next

1. **Decide whether to enforce invariants 1, 2, 3 and 6 in CI.** Recommendation: a small test under `tests/` that reads the
   probe's source text and fails on a `linear_ceiling` or `kvt` import or a close-comparison, and that fails if any file
   under `src/`, `config/` or `ledger/` names the probe. Reading the probe's text does not make the probe depend on
   anything, so independence survives. Invariants that live only in briefs rot. Not built: it changes CI, so it waits for a go.
2. **Take invariants 4 and 5 to the reviewer rather than editing their tool.** Two asks: rename `$RECHECK` in the recipe to
   a cold directory outside `results/`, and have the comparator refuse when the two score-JSON hashes are equal. Both
   change the reviewer's code or record, so both are theirs to make.
3. **Ask the reviewer for the full 40-character archive revision** and a corrected record line.
4. **Paper condition 1 is not discharged by this merge.** The record supports computational integrity for two sampled
   handoffs, and says itself that it does not resolve the threshold choices, the sign-off chronology, the oracle floor
   versus an achieved method, or generalization. Whether it counts toward the owed refutation of 0025–0029 is the
   operator's ruling.
5. **Reconcile local and remote `main` when the operator chooses.** Until then, the probe's re-verify lines above run
   against a checkout of remote `main`, not the local tree.

## Commit block (operator; Git Bash; explicit paths)

```bash
cd ~/dev/linear-ceiling
# Run the commit block in 2026-09-10-e9l-close-r8-unsettled-and-a-second-session-in-the-tree.md FIRST: the shared learnings
# and handoff indexes already carry rows for the untracked files that block stages, and these rows sit after them.
git add docs/learnings/2026-09-10-the-independent-rescore-probe-passes-a-self-comparison-only-the-score-json-seconds-field-exposes-it.md \
        docs/learnings/2026-09-10-the-review-recipe-recheck-directory-collides-with-summarize-e9s-own-recheck-output.md \
        docs/learnings/LEARNINGS.md
git commit -m "docs(learnings): the independent probe passes a self-comparison; the review recipe collides with recheck/"

git add docs/handoff/2026-09-10-keeping-the-e9-independent-rescore-probe-independent.md docs/handoff/HANDOFF.md
git commit -m "docs: handoff for keeping the E9 independent rescore probe independent"
```

No push line: local `main` has diverged from remote `main`, which now carries `bb85a28`, so a plain push would be
rejected, and how to reconcile them is the operator's decision. Not staged: `README.md`, `docs/status.md` and `.claude/`.
Verified with read-only `git status`, `git log`, `git diff`, `git ls-remote` and `gh`; `git fetch` was not run.
