# Handoff — llama-branch-lcfm close: the second family's E8 amendment is on the ledger (0052/0053, the inversion does not persist), the long cell's 0050 preview is ready, the camera-ready paste was delivered

2026-10-04, written ~09:30Z (session `llama-branch-lcfm`, 701ace2c; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl`). Describes linear-ceiling
`main` = `origin/main` = **`0c5ec15`** (`ledger: 0053 — Llama E8 amendment ran; the inversion does not persist`), CI green at
`0c5ec15`. Uncommitted at write: this brief, its index row, six learnings and their index rows, and `docs/drafts/append_0050.py`
(file-order guard + one word). Also uncommitted, NOT this lane's: the E-TRUNC session's close (`docs/handoff/2026-10-04-e-trunc-for-camera-ready-…`,
three learnings, its rows in both indexes). Untracked, nobody's: `.claude/`, `docs/paper/tex/` (the 09-14 scaffold, not the submitted tree).
Previous briefs in this lane: `2026-10-02-llama-branch-lcfm-close-condition-1-issue-7-posted-lane-closed.md` and the 03:40Z Carryover close.
Private, `~/dev/briefs/`: `2026-10-04-lcfm-camera-ready-paste.tex` (the patch text), `2026-10-04-llama-long-sitting-c-preflight.md`,
`2026-10-04-issue-emerson-0046-preview-draft.md` (posted as issue #15).

The camera-ready deadline is **2026-10-04 11:59Z** (05:59 MDT, operator's figure; nowhere public). At write, 2 h 30 min remain.

## Current state

- **built, on the ledger — 0052 and 0053, the second family's E8 amendment** (entry 0030's protocol: arm (b) over every agent
  sequence on 0040's dumps and token file by fingerprint; `config/e8fa.toml`; no upstream change, the family pin `06f8d55` contains
  0030's `223f469`). Figures, verified by `summarize_e8` at k = 1: arm (a) 0.7139 / 0.4711, arm (b) all 50 sequences 0.6979 / 0.4137,
  drop +0.0160 [+0.0052, +0.0267] / +0.0573 [+0.0410, +0.0740], HOLDS / UNRESOLVED; 0040's two-window inversion does not persist;
  τ_agent_K stays 0.2689, all-sequence counterpart 0.3021 reported beside it. Results under `results/e8fa/` (gitignored; local only).
  re-verify: grep -c '^### 005[23] ' ledger/ledger.md; .venv/Scripts/python.exe -c "import json;s=json.load(open('results/e8fa/summary.json'));r=s['recomputed']['1'];print(round(r['agent']['K'],4), round(r['drop']['K'],4), r['band_outcome'])"   # expect 2, then 0.6979 0.016 {'K': 'HOLDS', 'V': 'UNRESOLVED'}
- **built — the E8 config hash is newline-normalized** (`484e1be`; learning 2026-10-04). Windows E8 summaries no longer need the blob trick.
  re-verify: grep -c "sha256_text_file(cfg.config_path)" src/linear_ceiling/e8.py src/linear_ceiling/summarize_e8.py   # expect 1 each
- **built, verified — the Llama long cell's registration preview (0050) renders under the pin**: 68 observed, 32 included
  (|S| 33,086–74,233), 28 covered by the short cell, 4 above the cap (named), 4 empty receiver; keep subset 3; coverage
  `16121e677b97`, τ `dd3fca27e82a`; the two RoPE controls replacing the bridge; prefill budget 3,453,566 tokens. Guard moved to file
  order ("0052 present, 0050 absent"); one dropped word fixed. Uncommitted.
  re-verify: git -C ../kv-transfer-replication checkout -q --detach 06f8d55 && PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe docs/drafts/append_0050.py --preview --date 2026-10-04 | head -1; git -C ../kv-transfer-replication checkout -q main   # expect the "### 0050 —" heading
- **built, private — the camera-ready paste** (`~/dev/briefs/2026-10-04-lcfm-camera-ready-paste.tex`): W4/W8/W6/W7 text, the long-cell
  tail table and paragraph, W5 and W4 sentences, plus (after 0054) an optional three-column short/scaled/long block. Every number
  grepped at its ledger line; two corrections to the 05:55Z brief applied (0.0494 at 3013; |R| percentiles at 3023).
  re-verify: grep -c "0045:" ~/dev/briefs/2026-10-04-lcfm-camera-ready-paste.tex   # expect >= 12 (one cite per figure block)
- **built — issue #15 (Emerson) carries the operator's take-over comment**; `llama-second-family` is the standing Llama branch,
  level with main at `0c5ec15` after the last push block; `review/llama-r8-recompute` deleted.
  re-verify: gh issue view 15 --json comments --jq '.comments[-1].createdAt'; git rev-parse --short origin/llama-second-family   # expect 2026-10-04T07:19:50Z, then main's sha
- **not this lane's, verified present** — 0054 (Condition 1 discharged), 0055 (E-TRUNC registered), 0056 (pilot figures admitted),
  PR #17 merged, issue #7 closed; the E-TRUNC code is on main (`sender_head_truncate` in `config.py`).
- **planned:** 0050 append (operator), the rented sitting, 0051; nothing else for the second family (no 0038 analogue by design).

## Locked decisions

- **Numbering is by the drafts README and permanent once staged; `ledger_check` chains by file order** (operator, 2026-10-04: "if it's
  just numbering then it's not important"; 0054's Numbering paragraph). Reason: a ready entry never waits behind an unrun one.
  Learning 2026-10-04 (file order).
- **The operator does the Llama long cell prep himself** (2026-10-04, recorded on issue #15); Emerson stays assigned for the sitting.
- **No 0038 analogue for Llama** (this session's recommendation, unopposed): the configuration share is zero by construction on a
  natively long receiver; 0050 says so.
- **The Llama long cell runs on a rented 80 GB or H200 card, not AWS** (runbook §3.4/§4; this session restated it on issue #15).
- **Condition 1 is discharged by ruling (0054)**; the short-cell figures may be cited; 0045's e9/e9s tail released to the same extent.
- Carried unchanged: `llama-second-family` is the standing branch; private docs in `~/dev/briefs`; history is the operator's;
  the Hub token stays; the upstream clone moves only by `checkout --detach <pin>` and returns to `main`.

## Reuse map

- `config/e8fa.toml` and the shape of `append_0052.py` (in `bb0e139`) / `append_0053.py` (in `0c5ec15~1`): a registration that
  asserts every claim against the tree (config tracked and unmodified, pin held and containing a named ancestor, prior report
  fingerprints, a count recomputed from the raw file, a quoted sentence still present in a prior entry, R1 on the results dir), and a
  figures script that runs the summarizer in-process and reads only its output. Copy the shape for 0051 and any future amendment.
- The pinned-run script shape (detach → run → `trap restore EXIT`), used five times today; refuse if the clone is not on `main`.
- `~/dev/briefs/2026-10-04-llama-long-sitting-c-preflight.md`: inputs by sha, gate order, §9 rules, box sizing.
- `results/e9fl/align/coverage.json`, `results/e9fl/calibration/tau.json`: valid for 0050 as long as `config/e9fl.toml`'s blob stays
  `2f8d9545e1f3efcf` and `results/e8f/report.json` stays `4682508afd35`.
- `gh … --jq`, never a pipe to `jq` (absent here); WSL venv `~/lc-wsl-venv` for Linux-side tests; the 4 runpod test failures on WSL
  are CRLF-only, CI is the truth.

## Invariants

- 0001–0056 immutable; the file order is 0047, 0054, 0052, 0056, 0055, 0053; next free number **0057** (the E-TRUNC close may say
  otherwise for its own staged drafts: read `docs/drafts/README.md` before allocating).
- An append block stages `ledger/ledger.md` explicitly and reads `git diff --stat` before any restore (learning 2026-10-04).
- Figure appends re-run the summarizer: ten minutes, uninterrupted, clone at the pin (learning 2026-10-04).
- `results/e8fa/` is evidence that exists only on this machine until the next Llama backup; `git clean -x` destroys it.
- Nothing from 0053 moves a cell: H-E8 is 0020's; the Llama E9 cells read τ_K from arm (a), unchanged.
- The short-cell and long-cell figures are never pooled, in the paste file or anywhere.

## Open / next

1. **Operator, before 11:59Z:** the camera-ready pass in Overleaf from the paste file; nothing else competes for that window.
2. **Operator, after:** commit this close and the 0050 draft edit, then append 0050 and push:
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/handoff/2026-10-04-llama-branch-close-*.md docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md \
           docs/learnings/2026-10-04-both-families-*.md docs/learnings/2026-10-04-the-e8-config-hash-*.md \
           docs/learnings/2026-10-04-ledger-check-chains-*.md docs/learnings/2026-10-04-a-handoffs-built-*.md \
           docs/learnings/2026-10-04-an-append-block-*.md docs/learnings/2026-10-04-a-figures-append-*.md \
           docs/drafts/append_0050.py
   git commit -m "docs: llama-branch close — 0052/0053 on the ledger, 0050 preview ready; six learnings"
   git -C ../kv-transfer-replication checkout -q --detach 06f8d55
   .venv/Scripts/python.exe docs/drafts/append_0050.py --date 2026-10-04 && git rm -q docs/drafts/append_0050.py
   git -C ../kv-transfer-replication checkout -q main
   git add ledger/ledger.md
   git commit -m "ledger: 0050 registers the Llama long cell at a native receiver"
   git push origin main && git push origin main:llama-second-family
   ```
   The E-TRUNC close's files are in the same tree and NOT in this block; commit them from that lane's brief. Verified vs assumed:
   tree read at 09:24Z; only this lane's and the E-TRUNC lane's files are modified or untracked; `main` was 0/0 at `0c5ec15`.
3. **The sitting** (operator; Emerson on the box if he takes it): rent, probe at 74,233, run, pull/verify/delete, back up under the
   project account, `summarize_e9`, `append_0051.py` (ten minutes), `e9_tail`. Then the family is complete.
4. **Carried:** PR #12 open (review records accepted by 0054; its README rewording not adopted); the two empty project-account
   datasets; AWS key pair; a de-duplicated E8 bootstrap on both families as a future amendment, if ever.
