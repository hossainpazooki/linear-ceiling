# Handoff — the Astra review landed, PR #5's review is posted, and the Carryover items this session was opened for were never started

2026-09-21, written ~02:45Z. Describes linear-ceiling `main` = `origin/main` = `3d2fbb1` (0 ahead / 0 behind at
the 02:30Z fetch), plus this brief, five learnings and their two index rows, all uncommitted. The working tree
also carries four OTHER sessions' uncommitted files (listed under Invariants). PR #5 head: `7f83cea`.

This session was opened on 2026-09-16 to pick up an "ICLR 2027 nine-pager" seed for the Carryover paper. It
verified the seed, then drifted for four days. **ICLR was dropped by the operator on 2026-09-19.** What the
session actually produced is an adversarial-review record and its fixes; what it was opened for is in
Open / next, untouched.

## Current state

- **built — the Astra review record**, `docs/2026-09-20-astra_review.md` (`487580b`, row updated in `3d2fbb1`).
  Consolidates a Codex thread (model `gpt-6-astra`) that ran three adversarial reviews of this repo between
  09-11 and 09-14, a critique of the GPU-runs doc, a workshop-reviewer read, and the Condition 1 work: 27
  findings, each tagged with who verified it and its status on main. Its own caveat: the reviewer was never
  given the paper text, `figures.json` or the bibliography, so no finding is about the submitted PDF.
  re-verify: git show 3d2fbb1:docs/2026-09-20-astra_review.md | grep -c "^| R[123]-"   # expect: 24 register rows (27 findings; several share a row)
- **built — README no longer states the false token-level universal** (`487580b`). Four statements of "f* = 0 /
  within tolerance at every matched token" now say what 0023 defines (the MEAN over a handoff's matched tokens);
  the yardstick paragraph no longer says "a token needs recompute above τ_K"; Condition 1's deadline reads as
  0032 wrote it (the numbers-freeze gate, EOD 2026-09-08) and says it was not met.
  re-verify: grep -c "every matched token\|needs recompute above\|before submission" README.md   # expect: 0
- **built — outline v3 and the GPU-runs doc carry dated correction notes** (`487580b`): dumps are fp16 [0025], the
  forward pass is fp32 [0026]; the median |S| 50,916 and the three bridge R² values are marked as summary-file
  figures no entry states; the GPU-runs doc has an amendment note for its two errors ("six kept directories" =
  three long handoffs + three bridge controls; 57 GB / 31.56 GiB / ~2 h are not ledger figures).
  re-verify: awk 'index($0,"0.8992")||index($0,"50,916")||index($0,"57 GB")||index($0,"31.56"){n++} END{print n+0}' ledger/ledger.md   # expect: 0
- **built — the co-author refutation as an importable table**, `docs/reviews/refutation-0025-0029-rows.csv`
  (`3d2fbb1`): one administrative row plus fourteen attacks on 0025–0029, each with its ledger line, a PRE/POST
  tag, what would refute it, whether it is a different route, and what it needs. Two rows are marked
  run-first (R1 re-derives f* without the package; R9 asks whether the prefix control can fail). `observed` and
  the signature columns are blank. It replaces a Codex seed of mine that was never run and never committed.
  re-verify: git show 3d2fbb1:docs/reviews/refutation-0025-0029-rows.csv | .venv/Scripts/python.exe -c "import sys,csv,io;r=list(csv.DictReader(io.StringIO(sys.stdin.buffer.read().decode('utf-8-sig'))));print(len(r),len(r[0]),[x['id'] for x in r if x['run_first']])"   # expect: 15 16 ['R1', 'R9']
- **built — "zero on every handoff" settled** (learning 2026-09-21, f-star-is-zero-on-every-handoff): max
  per-handoff same-K f*(τ_K) is 0.0 over 25 / 35 / 25 handoffs. No ledger entry states that maximum.
  re-verify: .venv/Scripts/python.exe -c "import json;[print(e,len(v),max(v.values())) for e in ('e9','e9l','e9s') for v in [json.load(open(f'results/{e}/summary.json'))['fstar_per_handoff']['same_K']]]"   # expect: e9 25 0.0 / e9l 35 0.0 / e9s 25 0.0
- **built — PR #5 reviewed; the review is posted on the PR as two comments** (issuecomment-5754565968 and
  -5754567237). Verdict: request changes. Findings 1–4 each carry file:line at `7f83cea`, what was confirmed, the
  consequence against entry 0043 or 0042, a suggested fix and an acceptance test. Finding 1 was reproduced under
  WSL. None of them touches 0044's evidence (28 of 28 scored; no partial close was used).
  re-verify: gh pr view 5 --json comments,state,headRefOid --jq '{state,head:.headRefOid[0:7],n:(.comments|length)}'   # expect: OPEN, 7f83cea (or later), n >= 2
- **built — gates green at `3d2fbb1`**: `ledger ok (blocks unchanged vs HEAD)`, `scope ok`, seal `OK (no sealed
  predictions yet)`, `436 passed, 1 skipped` (run 2026-09-21 ~00:20Z, after the second set of edits).
  re-verify: .venv/Scripts/python.exe -m linear_ceiling.ledger_check && .venv/Scripts/python.exe -m linear_ceiling.lint_scope && .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
- **in-progress, not this session's — PR #5** (`llama-second-family`, ledger 0039–0044, H-E9F HELD). Open,
  unmerged; the branch's own agent owns the four fixes. Nobody here touched the branch.
- **planned, PROPOSED only — the Async RL design for ARR**, `docs/2026-09-19-async-rl-arr-design.md`, untracked.
  Written by this session on 09-19 and **revised by another session on 09-20** (its §2 now cites PipelineRL
  Fig. 7, Magistral and Nemotron from the primary PDFs). Unregistered, nothing run. Not mine to commit any more.
- **not started — the two items this session was opened for** (Open / next 1).

## Locked decisions

- **ICLR 2027 is dropped** (operator, 2026-09-19: "not possible on such a tight timeline"). Reason: two days to
  the author lock and nine to the paper with the manuscript tree off this machine. The 09-16 seed's deadlines and
  Friday gates are dead; its §5 fixes and §6 owed items still apply to any extended Carryover.
- **Tracks** (operator, 2026-09-19, stated as "possible"): Async RL → ARR → ICML; Carryover → the NeurIPS
  workshop (done) → MLSys. "AAR" in the operator's shorthand is ARR, the ACL Rolling Review. Read from the venue
  sites on 09-19: ARR October cycle submission Oct 12, commitment NAACL / COLING 2027 Dec 23; MLSys 2027 details
  "have not been announced yet" — the seed's "Oct 30" has no public source.
- **This is a paper, not a software project** (operator, 2026-09-19): coordination is ad hoc, the tracker is
  Airtable, GitHub Actions stay minimal (main has one `ci.yml`), no feature-branch workflow. Reason: process
  overhead was outgrowing the work. Consequence: trackable items go to the tracker as rows, not into the repo as
  new scripts or seeds. The ledger's own discipline is science, not process, and stays.
- **The history is the operator's.** This session wrote no commit; both commits were run by the operator from
  handed-over blocks.
- **Not fixed on purpose:** the immutable sentences in 0025 / 0029 / 0036 (and now 0042 on the branch); the
  09-08 comparator (a co-author's tool cited by a review record — changing it alters what that record ran);
  superseded dated docs that repeat the token claim (outlines v1 / v2, the 09-06 gap map, the archived README).

## Reuse map

- `docs/2026-09-20-astra_review.md` — start here for anything about what is wrong in the record: §3 is the
  findings register with status, §10 open items by owner, §11 a re-verify block.
- `docs/reviews/refutation-0025-0029-rows.csv` — the Path A instrument. Import it; hide `OPERATOR_ONLY_note`
  from the co-author's view (it holds pre-reads that would anchor them).
- `docs/drafts/append_0039.py` (untracked, Codex's) — Path B: an operator ruling accepting the 09-08
  re-verification post-freeze. `--preview` ran clean at `a5053b2`. **Its number is taken** (Invariants).
- Upstream `../kv-transfer-replication` `kvt/cache.py` (`build_cache`, `forward_with_cache`) and the HellaSwag
  identity cell already exist — the downstream-quality run (full recompute / stale reuse / mismatched null, read
  as next-token divergence on the 8 short + 3 long kept handoffs) needs a splice, not injection from scratch.
  PROPOSED, unregistered; the upstream is read-only from here.
- `~/.codex/` is readable: `history.jsonl` (prompts), `sessions/…/rollout-*.jsonl` (threads; `*** Add/Update
  File:` lines list what it wrote), `thread_history_1.sqlite` (`thread_turns.status`). Open sqlite read-only.
- Five learnings dated 2026-09-21 in `docs/learnings/`.

## Invariants

- **Ledger number 0039 is taken on `origin/llama-second-family`** (the Llama registration, 2026-09-18). The
  staged Path B script claims 0039 against `a5053b2` and is ordering-guarded: it will refuse. Renumber and
  re-stage it after PR #5 lands; never append it as is.
- **A refutation signed now cannot satisfy 0032's 09-08 freeze as written.** Path A or Path B, a numbered
  operator entry must supersede that clause. Until one does, 0029, 0038 and 0034's E9 figures are withheld.
- **Say "on every handoff", never "at every matched token"**, and say the first only with a ledger figure for
  the maximum (none exists). Do not write "longer handoffs spend more of the margin", "nine in ten", or a
  configuration share of the scaled-short → long difference: `ledger:2369-2370` excludes "anything about length
  alone", the cross arm reads 0.9500 and 0.9640, and the share is (scaled − native) / (long − native).
- **`lcfm_anon` is the double-blind copy, not a feature branch.** Never delete it; never read a ledger figure
  from it.
- **Merge PR #5 with a plain merge, never a squash:** `ledger_check --against <rev>` reads the chain by commit.
- **Four other sessions' files sit uncommitted in this tree; do not fold them into your commit:** the three
  2026-09-14 closes (rows in `HANDOFF.md` and `LEARNINGS.md`, two briefs, ~16 learnings); Codex's
  `docs/2026-09-14-condition-1-*.md`, `docs/2026-09-14-seed-condition-1.md`, `docs/reviews/2026-09-14-refutation-0025-0029.md`
  (an empty template), `docs/drafts/append_0039.py` + test and the one-line `docs/drafts/README.md` edit;
  `docs/paper/tex/` (a superseded scaffold whose introduction was rewritten by a Codex turn that failed before
  its read-back — unverified); `.claude/`; and the Async RL design doc.
- **The rigor change-guard hook refuses a `gh` comment whose body it cannot read** (a body passed by file). Post
  inline, in parts under ~3 KB. It also pattern-matches heredoc bodies in Bash commands.
- The repo is PUBLIC. No names, pod ids, balances or tokens in a PR comment.

## Open / next

1. **The two Carryover items that were startable on day one and never started.** (a) The macro table: every
   number printed in the workshop paper → ledger `entry:line` → macro name; a number without all three does not
   enter an extended paper. Most entry:line anchors are already in `docs/2026-09-20-astra_review.md` §3 and in the
   09-14 fact-check brief. (b) The anonymity denylist for anything mirrored from `main`: at `a5053b2`, 52 files
   carried team names, including `README.md`, `ledger/ledger.md` and `CLAUDE.md`. Neither needs the manuscript.
   **Blocker for everything beyond these two:** the submitted `neurips-farhan/` tree, the team's `neurips/` tree
   and the PDF are not on this machine; the operator supplies them.
2. **Operator: the corrective ledger entry** for the token sentence in 0029 / 0036 (and 0042 once PR #5 lands)
   and the R² mislabel in 0025 / 0029, carrying the per-handoff maximum so "on every handoff" has a figure.
3. **Operator: Condition 1** — Path A (send the CSV; name the second signatory; rule on whether the 09-08
   reviewer may sign and whether the four `beyond-0032` rows are required), Path B (renumbered), or withhold.
4. **PR #5:** point the branch's agent at the two PR comments (a comment does not wake a session). Merge after
   findings 1–4 are fixed and the four gates are shown; then renumber the Path B script.
5. **Operator: rule whether ARR Oct 12 is a target.** That decides whether the Async RL design doc is committed
   as a plan or parked. This session's view, recorded in that doc: 23 days is tighter than the ICLR window that
   was just judged impossible for a paper with its results in hand.
6. **Housekeeping, handed over and not run:** `git branch -D track-b` (both its commits are in main by patch
   equivalence — `git cherry main track-b` prints two `-` lines).
7. **Commit block** (operator; Git Bash; explicit paths). `HANDOFF.md` and `LEARNINGS.md` also carry the three
   09-14 sessions' uncommitted rows, so whichever block runs first carries every session's rows; the brief and
   learning FILES each block names are disjoint. Run the r8-closed brief's block first if it is still pending.

```bash
cd ~/dev/linear-ceiling

# This session's close: one brief, five learnings, and the two index files.
# The index files also hold the 09-14 sessions' rows (see above) - that is expected, not a mistake.
git add docs/handoff/2026-09-21-astra-review-landed-pr-5-review-posted-and-the-carryover-items-never-started.md \
        docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md \
        docs/learnings/2026-09-21-f-star-is-zero-on-every-handoff-in-all-three-cells-and-no-entry-states-that-maximum.md \
        docs/learnings/2026-09-21-the-prefix-invariance-control-is-a-separate-s-plus-1-prefill-registered-on-one-handoff.md \
        docs/learnings/2026-09-21-a-pid-taken-after-setsid-nohup-bash-c-is-the-wrappers-and-sigterm-to-it-leaves-the-driver-running.md \
        docs/learnings/2026-09-21-kept-bytes-is-read-by-the-pull-verifier-and-written-by-nothing.md \
        docs/learnings/2026-09-21-lcfm-anon-is-the-double-blind-copy-not-a-feature-branch.md

git diff --cached --stat   # expect 8 files

git commit -m "docs(handoff): Astra review landed, PR 5 review posted, Carryover items unstarted"
git push
```

Not folded in, and left to the operator: every file listed under the fourth invariant.
Verified vs assumed: `main` was 0 / 0 against `origin/main` at the 02:30Z fetch and no merge was in progress
(`.git/MERGE_HEAD` absent, checked 00:20Z); not re-fetched after that, so `git pull --ff-only` first if the push
is rejected.
