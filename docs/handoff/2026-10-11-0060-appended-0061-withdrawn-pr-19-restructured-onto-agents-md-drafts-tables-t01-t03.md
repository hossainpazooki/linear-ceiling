# Handoff — 0060 appended, 0061 withdrawn, PR #19 restructured onto AGENTS.md, drafts/tables T01–T03

2026-10-11 ~05:10Z. Newest commit described: `12088d6` on `main` = `origin/main` (Windows tree clean apart from three
untracked local paths; see Open). PR #19 branch `zain/agent-onboarding-cleanup` at `a2c34e5` on origin.

## Current state

- **built** — Entry 0060 appended 2026-10-10 (`e0be46d`, the MLSys 2027 figure-set freeze; descriptive, no cell
  moves); script retired `5cedd54`. Ledger has 60 entries, file order ends 0059, 0057, 0060.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → "ledger ok"; `grep -c '^### 00' ledger/ledger.md` → 60; `tail -1 ledger/ledger.md` begins `prior-entries-sha256: 84e86162…`
- **built** — 0061 WITHDRAWN before its staging commit (operator ruling 2026-10-10: the pooled per-token `np.quantile`
  convention behind 0038/0045's p10/p90/p99 is a brief + learning matter, nothing on the record moves). Next free number
  stays 0061. Recorded in `docs/drafts/README.md` (the 2026-10-10 late note).
  re-verify: `grep -c "0061 WITHDRAWN" docs/drafts/README.md` → 1; `ls docs/drafts/append_*.py` → nothing
- **built** — `docs/drafts/tables/` (`12088d6`): T01 RULE (pooled per-token quantiles), T02 APPROVED 2026-10-10
  (E-TRUNC §4 paragraph, §X cross-reference open), T03 DRAFT (second-pair section: table, P1–P4, App. A scoping
  sentences). Each carries sources in both forms (entry:line at a named ledger rev AND summary-file key + sha12) and
  a re-verify line; both lines were executed at write time and matched.
  re-verify: run the `re-verify:` line in `docs/drafts/tables/T02-e-trunc-paragraph.md` (expects `14 21 154620 0.0868 0.1112 -0.0257 -0.0434 0.0024 unattributed 0.4285 [0.0, 0.0, 0.0, 0.0]`) and in T03 (expected output after its `#`)
- **built** — E-TRUNC §4 paragraph approved (four decimals) — now T02; the draft plan
  `docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md` is the index only.
  re-verify: `grep -c "^## 2c" docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md` → 0; `grep -c "T02" …` ≥ 2
- **built** — PR #19 (Zain) restructured on his own branch: `AGENTS.md` = tool-neutral contract with the
  never-restate-a-reading rule, `CLAUDE.md` = `@AGENTS.md` + operator notes, `docs/agent/` commands + architecture,
  "Contributing by pull request" section; two skeptic audits applied (`561bc05`); superpowers row dropped (`59182a4`);
  three main-side edits reverted (`a2c34e5`). CI green at `561bc05`.
  re-verify: `git fetch && git diff $(git merge-base main origin/zain/agent-onboarding-cleanup) origin/zain/agent-onboarding-cleanup --stat | tail -1` → "5 files changed" (AGENTS.md, CLAUDE.md, README.md, docs/agent/*.md; a two-point diff against main counts main's later files too); `gh pr view 19 --json mergeable -q .mergeable`
- **built** — Four learnings 2026-10-10/11 with index rows (`c0fc82c`, `91064ee`, this brief's commit); trunc
  docstring says four passes (`91064ee`).
  re-verify: `grep -c "2026-10-1[01]" docs/learnings/LEARNINGS.md` → 4
- **in-progress** — T03 P1–P4 awaiting per-paragraph approval; P2's tail sentence placement (main text vs App. C)
  is the operator's decision.
- **in-progress** — PR #19 merge waits on Zain testing the setup locally and reporting (comment of 2026-10-10).
- **planned** — review PR #22 (neuriv, 2026-10-10, SHA256SUMS + inputs manifest for issue #20); ruling on PR #18
  (Zain's evidence map, 44 behind, two findings stale after 0057); issue #21 (Emerson R12 recompute); Emerson's
  `origin/larger-context` (4 commits, no PR; two fixes worth their own PR).

## Locked decisions

- **No ledger entry for the per-token quantile convention** (2026-10-10). Reason: the summarizers' printed values are
  the readings; 0006:267 already carries an interpolated p90; 0013:740's "one convention" sentence describes its own
  table; the max gap over the 11 figures is 0.0001001 and the paper prints none. Pick-up check: T01 still says the
  plan prints none.
- **`AGENTS.md` canonical, `CLAUDE.md` = `@AGENTS.md` + operator notes; the contract never restates a registered
  reading** (2026-10-10, PR #19 review comment issuecomment-6100466701). Reason: PR #19's contract cited 0023/0027 for
  f* three days after 0058 withdrew it; a sentence that points cannot rot.
- **Allocator/program state lives only in `docs/drafts/README.md`** (2026-10-10). Reason: CLAUDE.md's state paragraph
  was hand-edited five times in two days and rotted; main's CLAUDE.md line 190 is the LAST allocator line there.
- **`docs/drafts/tables/` format** (2026-10-10): both source forms required; annotated paragraph format (block
  quote, "Changes, and why" entry:line, skeptic record, approval record); IMMUTABLE once APPROVED, corrections and
  cross-reference fills are superseding files. Reason: entry lines rot at the next corrective, keys do not; a paste
  source that silently changes is the defect the ledger exists to prevent.
- **PR #19 stays open until Zain tests locally**; main gets no merge of it before then.
- **Four decimals in paper text, as the ledger prints** (2026-10-10).
- **E-TRUNC reads "unattributed"** (0057) — the paragraph says so and claims no per-handoff direction (interval
  includes zero).

## Reuse map

- `docs/drafts/tables/README.md` — the format; copy T02's header shape for the next paragraph, T03's for a section.
- `docs/drafts/append_0060_template.py` is NOT in the tree; the last append script shape is in git history:
  `git show 71c4cef:docs/drafts/append_0060.py` (header_line / locate / in-process figure reads / chain_hash /
  `--date` / `--preview`).
- `src/linear_ceiling/e7_stats.quantile` (nearest-rank) vs `np.quantile` (per-token pooled fields in `e9_compare`,
  `e9_tail`) — T01 says which applies where.
- `docs/2026-10-03-co-author-run-admission.md` (PROPOSED, R13) — the only route for pilot figures.
- Summary-file sha12s at this brief: e9t/compare `0572662307f3`, e9s/compare `a0699a826f1f`, e9f/summary
  `e1e5feb8aadd`, e9fl/summary `1ac712b3897e`, e9f/tail `c35c48b9dbbe`, e8fa/summary `9ddb66cc2796`.

## Invariants

- Ledger entries, learnings, briefs and APPROVED table files are immutable; corrections are new dated files. CI runs
  `ledger_check --against <PR base>` on the block diff.
- No figure is typed from memory: every paper number is read from its summary file at claim time; four decimals.
- `results/` never enters git (one tracked pilot exception, stated in AGENTS.md); no token, balance, hostname or
  private file in issues/PRs/commits/docs (public repo).
- Claude never writes git history; blocks are handed over. A block that switches branches starts from a CLEAN tree
  (learning 2026-10-11).
- Windows suite carries known reds (`os.fsync` in `e9.py:418`, CRLF asserts, bash `find`); CI on Linux is the gate.

## Open / next

1. Operator: commit this brief + the 2026-10-11 learning (block below), then the prune block from the 2026-10-11
   assessment (merged local branches; `.claude/`, `.venv-cb/`, `docs/paper/tex/` → `.git/info/exclude`; tex to
   `~/dev/briefs` or tracked after a denylist check).
2. T03 approvals (P1–P4, table, scoping sentences); P2 placement decision.
3. PR #22 review (never-in-a-PR check; where the pilot's files land vs 0049's operator manifest). PR #18 ruling.
4. Zain's local test → merge PR #19 (`main` CLAUDE.md is replaced; drafts README stays the allocator).
5. Issue #21; Emerson's `larger-context` fixes; lag-ladder 0004 re-pin (upstream `holdover-pilot-pair`).
Blocker: none on main. T02's §X waits on App. C's placement in the main text.
