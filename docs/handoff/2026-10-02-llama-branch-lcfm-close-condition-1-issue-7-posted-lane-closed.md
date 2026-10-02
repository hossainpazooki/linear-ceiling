# Handoff — llama-branch-lcfm close: Condition 1 is issue #7, the Carryover lane is closed, what remains waits on co-authors and rulings

2026-10-02, written ~04:05Z (session `llama-branch-lcfm`, renamed from `Carryover: MLSys NeurIPS Sprint`, 701ace2c;
transcript `C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl`).
Describes linear-ceiling `main` = `origin/main` = **`a470322`** (`docs: Carryover close — 0045 appended, Llama R12 closed
here, E-BEH driver found; five learnings`), CI green at `a470322` (`gh run list --branch main --limit 1` → `success`).
Uncommitted at write: this brief, its index row, two learnings and their index rows. Untracked, not this lane's:
`docs/paper/tex/`, `.claude/`. Previous brief in this lane, 25 minutes older:
`2026-10-02-carryover-close-0045-appended-llama-r12-closed-e-beh-has-a-driver.md` — **its Current state, Locked decisions,
Reuse map and Invariants all still hold at `a470322` and are not repeated here; pick-up runs that brief's `re-verify:` lines
too.** This brief records only what moved after it.

## Current state

- **built, verified — the Condition 1 issue is posted**: https://github.com/hossainpazooki/linear-ceiling/issues/7, opened
  2026-10-02T03:46:37Z from the operator's account after the operator's review of the revised draft
  (`~/dev/briefs/2026-10-01-issue-condition-1-draft.md`, now the posted text). Body 4,351 characters; scope table (leads A
  and B, 0036/0038 pass, 0045 tail, beyond-0032 rows, second family done via PR #6); three asks (@neuriv PR the review into
  `docs/reviews/`, @ritvikagg second signature by approval, operator records the ruling on the PR); closing line "entries
  0025–0045 stay as written". No comments yet, no open PRs. Learning 2026-10-02 (issue #7).
  re-verify: gh issue view 7 --json state,createdAt,author --jq '.state + " " + .createdAt + " " + .author.login'   # expect OPEN 2026-10-02T03:46:37Z hossainpazooki
- **built — the previous close is committed** (`a470322`, the operator): the 03:40Z brief, five learnings, the response-map
  note. The HANDOFF and LEARNINGS indexes carry them.
  re-verify: git show --stat --oneline a470322 | tail -8   # expect the brief, HANDOFF.md, LEARNINGS.md, five 2026-10-02-*.md, the response map
- **corrected by the sibling lane, carried here — the e9f seam-bin ratio is 8.59×, not 8.7×**: this lane's 2026-10-01 chat
  figure "up to 8.7× the medians" was recomputed by the `dev-fd` session from `results/e9f/tail.json` (max over seam bins
  8.59, bin 16+; over position bins 7.58) and recorded as a `refuted-assumption` learning
  (`2026-10-01-a-sibling-sessions-chat-figure-is-a-claim-the-e9f-seam-ratio-is-8-59x-not-8-7x.md`). Nothing on the ledger or
  in a doc carries 8.7×; the issue body does not state the ratio. Use 8.59× anywhere the figure is wanted.
  re-verify: .venv/Scripts/python.exe -c "import json;t=json.load(open('results/e9f/tail.json'));print(round(max(b['mean']/b['median'] for b in t['seam_left_bins']['same_K'] if b['median']),2))"   # expect 8.59
- **not moved — the sibling lane's five staged learnings** are still only in `~/dev/briefs/2026-10-01-staged-learnings/`
  (ARR ruling location; Llama backup under the co-author's account; Mac mini 16 GB; PR 5 line shift and the CSV; upstream
  PR 1 merged). None of the five filenames exists under `docs/learnings/`. Operator's call whether they enter (they were
  written against a tree before `a470322`; each would need its anchor checked, not re-stamped).
  re-verify: for f in ~/dev/briefs/2026-10-01-staged-learnings/*.md; do [ -e "docs/learnings/$(basename "$f")" ] && echo IN || echo OUT; done   # expect five OUT
- **drafted, unsent (operator)** — the Slack message to Vikram (box-request preface, summary sentence naming E-BEH, the two
  asks, three design questions) and the Algoverse form text (24 h, 40 GB slice; team name, code and emails to fill). Both
  are in this session's chat, not on disk; the issue link now serves ask 2 of the message.
- **planned** (unchanged from the previous brief): E-BEH registration draft + `construct()` port; E-TAIL Part B draft +
  chunked-attention driver; E-TRUNC; the macro table (blocked on the submitted tree); audit item 15 (fsync `e9.py:415`,
  the E8 raw-byte config hash).

## Locked decisions

All of the previous brief's decisions stand. Two refinements from this close:

- **Condition 1's coordination record is issue #7, not the ledger** (operator, 2026-10-02: "ok open the issue"). The ledger
  keeps the ruling in 0045's scope sentence and never names the issue; the review PR cites the issue. Reason: the ledger is
  descriptive and append-only; coordination with co-authors changes daily.
- **The issue closes only on the review PR's merge with both signatures**; the assistant does not close, edit or comment on
  it without the operator's word (outward-facing action). Reason: the issue is the public face of the ruling; every change to
  it is a change to what the co-authors were asked.

## Reuse map

- The previous brief's map in full (tail summarizer, pinned-run script shape, WSL gate, `C:\m\ci`, the design docs, the
  config-blob trick).
- `gh issue view 7` / `gh pr list` with `--jq`, never a pipe to `jq` (learning 2026-10-02: `jq` is absent on this
  machine's Git Bash).
- `~/dev/briefs/2026-10-01-issue-condition-1-draft.md` is the posted text, verbatim; quote it rather than the issue page
  when drafting the PR comment that records the ruling.

## Invariants

The previous brief's invariants hold unchanged (0001–0045 immutable, next number 0048, short-cell figures enter no paper
before the review merges, upstream clone returned to `main` — it is on `main` at `0d27c68` now, pins are LF blob hashes,
R1 before any box request). Added:

- **Issue #7's scope table is the review's contract.** A row added or removed there is a ruling, not an edit; it goes
  through the operator and gets a dated comment, so Vikram's PR and the table stay in step.
- **Figures quoted in co-author-facing text come from a pinned output on disk**, never from another session's chat
  (the 8.7× → 8.59× case above; the sibling's learning says so with its basis).

## Open / next

1. **Operator: commit this close** (explicit paths):
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/handoff/2026-10-02-llama-branch-lcfm-close-condition-1-issue-7-posted-lane-closed.md \
           docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md \
           docs/learnings/2026-10-02-condition-1-for-the-camera-ready-is-tracked-as-issue-7-the-public-record-of-the-ruling-outside-the-ledger.md \
           docs/learnings/2026-10-02-jq-is-not-on-this-machines-git-bash-path-so-a-re-verify-line-that-pipes-to-jq-fails-use-gh-jq.md
   git commit -m "docs: llama-branch-lcfm close — Condition 1 is issue #7; two learnings"
   git push
   ```
   Verified vs assumed: `git status --short` at 04:00:59Z showed only `.claude/` and `docs/paper/tex/` untracked before
   this close wrote its five files; `main` was 0/0 against `origin/main` at `a470322` after a fetch at that time.
2. **Operator: send the Vikram message** (link issue #7 for ask 2). His answers to the three design questions gate the
   E-BEH registration draft; his PR into `docs/reviews/` plus Ritvik's approval close the issue.
3. **Next assistant session, on the answers**: E-BEH registration draft (`docs/drafts/`, number 0048 if it is the next
   entry) + the `construct()` port per `docs/drafts/e-beh-design.md`; E-TAIL Part B draft on the quantity / backend /
   tolerance rulings; then the Algoverse form the day those entries land.
4. **Carried, operator-only**: the staged learnings' entry decision (item above); delete the two empty
   `hossainpazooki/…-e8f/-e9f` datasets and `origin/llama-second-family`; the AWS key pair and security group.
5. **Code fixes, unowned**: the E8 config hash (`e8.py:220`, `summarize_e8.py:54`, with a test) and the `e9.py:415` fsync.
