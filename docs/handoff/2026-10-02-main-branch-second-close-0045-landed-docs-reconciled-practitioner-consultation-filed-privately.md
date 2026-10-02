# Handoff — main-branch session, second close: 0045 landed, the docs reconciled to it, a practitioner consultation drafted privately

2026-10-02 ~04:40Z (session `dev-fd`, f87605d5; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl`). Newest commit this brief
describes: **`b891538`** (`docs: llama-branch-lcfm close — Condition 1 is issue #7; two learnings`, the Llama session's close)
= HEAD = `origin/main`. Uncommitted at write: this brief, its index row, two learnings entries and their index rows.
Untracked and not this session's: `.claude/`, `docs/paper/tex/`.

Supersedes nothing; extends this session's first close
`2026-10-01-main-branch-pick-up-pr-6-merged-ruling-11-renumber-and-the-corrective-entry-staged.md` (committed `9eb7515`),
whose state claims all still hold except that the corrective entry is no longer "staged, not appended".

## Current state

- **built — entry 0045 is on the ledger** (operator: `b3bf7ec` append, `62a8e8d` scope-sentence edit before it, `470133e`
  retiring `append_0045.py` and `tests/test_append_0045.py`). CI was red on `b3bf7ec` only because the test was still
  tracked (learning); green on `470133e` and every commit since. The entry's Condition 1 clause carries a NEW operator
  ruling (see *Locked decisions*). Next free number: **0048**.
  re-verify: `grep -n '^### 0045 ' ledger/ledger.md | cut -d: -f1` → `2991`; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`; `git ls-files docs/drafts/append_0045.py tests/test_append_0045.py | wc -l` → `0`.
- **built — the docs reconciled to 0045** (`ce7b3e7`, `abe9777`): drafts README allocator paragraphs say appended; outline v3's
  five PENDING rows carry dated notes naming 0045; CLAUDE.md lost the draft command and gained a 0045 program-state
  sentence; the review response map's W3 / W4 / W5 rows and rulings 3–4 carry dated notes with `0045:<line>` anchors.
  Every figure in those notes was asserted against the ledger line it cites before writing.
  re-verify: `grep -c 'ENTERED by ledger entry 0045' docs/paper/2026-09-11-lcfm-outline-v3.md` → `2`; `grep -c '0045:3022' docs/2026-09-30-review-response-map.md` → `1`; `grep -c 'append_0045.py --preview' CLAUDE.md` → `0`.
- **built, private — a practitioner consultation for E-BEH's band rationale**, filed under `~/dev/briefs/` (operator rule:
  keep local): the operator's seed verbatim (`2026-10-02-seed-practitioner-rule-e-beh-*.md`) and a draft
  (`2026-10-02-*-consultation-draft.md`) holding a source-verification table, the outreach message with three
  questions, and a `docs/reviews/` record skeleton. Nothing sent; nothing in the repo names the practitioner.
  re-verify: `ls ~/dev/briefs | grep -c -E 'practitioner-rule-e-beh|consultation-draft'` → `2`; `git grep -l -i 'practitioner rule for e-beh' -- .` → no output (not in the tree).
- **verified, not this session's — the Llama session closed twice** (`a470322`, `b891538`): 0045 appended, Llama R12 closed
  locally, an E-BEH driver found, Condition 1 opened as GitHub issue #7.
  re-verify: `gh issue view 7 --json state,title --jq '"\(.state) \(.title)"'`.
- **in progress:** nothing running from this session.
- **planned, not started:** sending the consultation (operator); rulings 1–3 (E-TRUNC) and 5, 6, 9, 10 of the run queue;
  task A's config key and reader; the macro table (blocked on the submitted tree); HF login revocation (still
  `hossainpazooki` at 04:00Z); deleting the two empty `hossainpazooki` e8f/e9f datasets; `origin/llama-second-family`.

## Locked decisions

- **Condition 1's numbers-freeze is moot for the camera-ready; the co-author refutation under `docs/reviews/` with two
  signatures is what remains** (operator, 2026-10-01, written into 0045's Condition 1 clause at `62a8e8d`). Reason: 0032's
  2026-09-08 freeze applied to the LCFM submission, since accepted. Pick-up checks: issue #7 is the refutation's tracker.
- **The practitioner's answers enter through one door, E-BEH's pre-registration rationale, before any data loads; his
  posts are citable for framing only** (operator's seed, 2026-10-02). Reason: a post-hoc band on H-E9 / H-E9L / H-E9F is
  forbidden by 0023's pre-registration; the camera-ready sentence may cite the published posts, never a private number.
- **The consultation stays out of the repo** (operator, 2026-10-02, "keep local"). Reason: private working docs go to
  `~/dev/briefs`; a named third party's unpublished answers are not repo material until a consented record exists.
- **Q1 of the consultation asks under what evidence an exact-or-nothing operator would accept an inexact prefix, not "in
  what unit do you judge one"** (this session, from reading his posts). Reason: all three posts describe a byte-exact
  prefix cache with "never invalidate the cache" as the law; there is no acceptance rule for an inexact prefix to elicit,
  and that absence is itself the citable finding.
- **Dated parenthetical notes, never rewrites, in dated docs** (outline v3, the response map). Reason: both are kept
  planning records; the precedent is `c3f4e30`.
- Earlier locked decisions (first close) stand: main-branch / Qwen lane split; ruling 11; rulings 4 and 7 at defaults;
  derived anchors; no `summarize_e7` in a non-E7 entry; merge commits for co-author PRs.

## Reuse map

- `~/dev/briefs/2026-10-02-*-consultation-draft.md` §4 — the `docs/reviews/` record skeleton for any
  practitioner consultation: verbatim-answer slots, unit mapping or "not attempted", scope, citability, consent, and an
  explicit "enters here, not there" section.
- Reading Medium when its pages return 403: the author RSS feed carries full post bodies (private draft §1).
- The exact-match edit-script shape (abort unless each old string matches once; preserve CRLF) used for every doc edit
  this session; trivial to re-write under the scratchpad.
- `docs/handoff/2026-10-01-main-branch-pick-up-...-corrective-entry-staged.md` *Reuse map* — the draft-testing pattern
  (`runpy.run_path(..., run_name="draft")`, whitespace-normalized assertions), still the pattern for 0046/0047.

## Invariants

- Entries 0001–0045 are immutable; `docs/drafts/README.md` is the only allocator; next free is 0048; `append_0039.py`
  carries a taken number and is never run.
- **An append script and its test leave in the append commit.** Left tracked, the test's ordering guard refuses on the
  new ledger and CI goes red (learning, `b3bf7ec`).
- **A figure-presence check against a wrapped entry must whitespace-normalize first**; a line-wise grep returns 0 for
  figures that are on the ledger (learning).
- 0046/0047's anchors and gate string are set; any entry landing before them renumbers them again, in one commit with
  `config/e9fl.toml`, before any `e9 --check`.
- Private working docs, and anything naming an unconsented third party, go to `~/dev/briefs`, not the repo.
- Git history is the operator's; `results/`, `data/`, `traces/`, `mappers/` never enter it; configs are pinned as LF blobs.

## Open / next

1. **Commit this close** (operator), explicit paths:
   `git add docs/handoff/2026-10-02-main-branch-second-close-0045-landed-docs-reconciled-practitioner-consultation-filed-privately.md docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-10-02-a-draft-appended-with-its-test-*.md docs/learnings/2026-10-02-a-wrapped-ledger-entry-*.md`
2. **Send the consultation** (operator): open the three canonical post URLs once to confirm the quotes the draft took from
   the RSS feed, then send the message in the draft's §3 with the reply-by of October 10 ahead of the October 15 PI review.
   When the answer arrives, fill the §4 skeleton into `docs/reviews/` with his consent recorded.
3. **Rulings 1–3** (E-TRUNC margin and statistic, shrinkage gate, L32-native) unblock run-queue task A, the only GPU row
   plausibly entered by Oct 30. Reviewer input, if any, comes as a `review/` branch PR, the PR #6 precedent; the rulings
   themselves land on `main` by the operator.
4. **Carried, operator-only:** HF login revocation; the two empty `hossainpazooki` datasets; `origin/llama-second-family`;
   the AWS key pair and security group; the macro table once the submitted tree is on a machine.
