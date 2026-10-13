# Handoff — camera-ready polish landed, README in manual shape with a pinned figure, deep-research brief on "carryover" prior art prefaced with the poster and headline readings

2026-10-12 ~03:25Z. Newest commit described: `081994f` on `main` = `origin/main` (CI green at push time, 2026-10-11
evening ET). Windows tree clean before this brief and the two learnings were written. Previous brief: 2026-10-11 ~05:10Z
(`12088d6`); everything there about 0060, 0061, T01–T03 and PR #19 still holds unless stated below.

## Current state

- **built** — Camera-ready polish for public readers, five commits by the operator between `12088d6` and `081994f`:
  `LICENSE` (Apache-2.0 canonical text), `CITATION.cff` (operator only; seven co-authors still to fill from the submitted
  PDF p.1 before the first tag), `pyproject.toml` metadata (PEP 639 `license = "Apache-2.0"`, `setuptools>=77`, extras
  `dev` and `figures`, `[project.urls]` Repository + Paper = OpenReview forum `kEGVswNFaq`), `docs/README.md` (map of the
  dated root docs; nothing moved, the ledger cites those paths), `docs/paper-to-record.md` (paper cell → T file → entry:line
  → summary sha12 → dataset, with an executable re-verify block), `proofs/README.md` status paragraph.
  re-verify: `sha256sum LICENSE | cut -c1-12` → `cfc7749b96f6`; `grep -n 'openreview.net/forum?id=kEGVswNFaq' pyproject.toml CITATION.cff README.md | wc -l` → ≥ 3
- **built** — README rewritten in manual shape (`081994f`): centered title + four badges (OpenReview, CI, License, Lean),
  hero figure, TOC, Overview with the four-row results table, Get started with three gates and a runnable Hub record check,
  Reproduce a cell, How the record is built, Data, Formal proofs, Contributing, Documentation, Citation (bibtex key
  `pazooki2026kvdrift`). The scope sentence appears exactly once.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.lint_scope` → "scope ok"; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → "ledger ok"
- **built** — Hero figure `docs/assets/seam-profile-same-model.png` from `tools/readme_figure.py`: reads four summary files,
  refuses unless each sha256 prefix matches its pin (e9 `ae461db872f2`, e9l `64e64e9318d4`, e9f `e1e5feb8aadd`, e9fl
  `1ac712b3897e`), plots `seam_profile_left_pooled.same_K` (the causal profile the ledger prints at 0029:1786), both pairs'
  τ_K dashed (Qwen 0.3186, Llama 0.2861). Title is descriptive, not a claim (0045).
  re-verify: `grep -c "ae461db872f2\|64e64e9318d4\|e1e5feb8aadd\|1ac712b3897e" tools/readme_figure.py` → 4; `grep -n seam_profile_left_pooled tools/readme_figure.py | head -1` non-empty
- **built** — README's Hub record check downloads `results/e9l/report.json` from `hossainpazooki/linear-ceiling-e9l-2026-09-10`
  and expects sha12 `084d9480af74`, which the ledger pins at 0045:3034. It checks `report.json` and not `summary.json`
  because the Hub copy of e9l `summary.json` (`be136307cdfa`) differs from the local pin (`64e64e9318d4`) by a later-added
  `dump_rope` key only, and the e9 dataset has no `results/e9/summary.json` at that path.
  re-verify: `grep -n "084d9480af74" ledger/ledger.md | cut -c1-60` → `3034:084d9480af74, \`summary.json\` 64e64e9318d4.`
- **built** — Repo metadata set by the operator on GitHub: description, homepage = OpenReview forum, 12 topics
  (kv-cache, llm-inference, llm-serving, prefix-caching, kv-cache-reuse, llm-agents, agent-handoff, long-context,
  reproducible-research, pre-registration, lean4, mlsys).
  re-verify: `gh repo view hossainpazooki/linear-ceiling --json repositoryTopics --jq '.repositoryTopics | length'` → 12
- **built** — Deep-research brief (private, not in the repo):
  `~/dev/briefs/linear-ceiling/2026-10-11-deep-research-carryover-term-prior-art-lineage.md`, nine findings F1–F9, six
  refuted claims, 20 sources, now PREFACED (2026-10-12) with the two session assessments: the "Carryover in Inference"
  poster ruling and the reading of why the headline is still the E9 cells. The preface says in its first line that both are
  judgments, not findings, and the entry numbers it cites were typed from the earlier answer, not re-read from the ledger.
  re-verify: `grep -n "^## Preface\|^### On " ~/dev/briefs/linear-ceiling/2026-10-11-deep-research-carryover-term-prior-art-lineage.md` → three lines (5, 9, 26)
- **in-progress** — PR #19 (`zain/agent-onboarding-cleanup` at `a2c34e5`): still open, waits on Zain's local test. It now
  conflicts with main's README; resolution is to take main's README whole.
- **planned** — T03 P1–P4 approvals, Emerson's fixes-only PR, T04, issue #21 (T03 read), CITATION.cff co-authors,
  e9fl visibility ruling, lag-ladder 0004 re-pin, `origin/add-lean-proofs` for its author, optional poster panel text as a
  tables file (offered, not requested), optional re-read of arXiv 2608.03893 raw before citing its method details.

## Locked decisions

- **OpenReview is the paper link, not arXiv** (operator, 2026-10-11): the paper is non-archival at LCFM and has no arXiv
  id; badge, `pyproject`, `CITATION.cff` and README all point at forum `kEGVswNFaq`.
- **Docs-root files keep their dated names; no `git mv`** (operator, 2026-10-11): the ledger cites those paths and is
  immutable. `docs/README.md` is the index instead.
- **README hero is the causal seam profile, not the two-sided one** (2026-10-11): only the causal profile matches a
  ledger line (0029:1786); see the 2026-10-12 learning on the two profiles.
- **Two public repos were read as README examples and are not to be recorded as anchors** (operator, 2026-10-11): do not
  name them in docs, commits or memory as the model for the README.
- **Deep-research model tiers** (operator, 2026-10-11): search Fable low, fetch Opus 5.5 high, verify Opus 5.5 high,
  synthesize Fable high. The harness ran "Fable 5" as Fable 5.1.
- **main is protected: merge commits only** (ruleset 24886867, 2026-10-11 learning). PR #19 merges with a merge commit.
- Everything in the 2026-10-11 ~05:10Z brief's locked list still stands (0061 withdrawn, next free entry 0061, T02
  approved, AGENTS.md convention, allocator state only in `docs/drafts/README.md`).

## Reuse map

- `tools/readme_figure.py` — pinned-input figure pattern (sha-refusal before reading); reuse for any poster or paper figure.
- `docs/paper-to-record.md` — the cell → file → sha12 → dataset table and its re-verify block (eight sha12s, grep count 13).
- `docs/drafts/tables/T01–T03` — paste sources for every paper number; poster panel text should be a T file too.
- `tools/hf_verify_backup.py` — restores `results/` from the datasets; the README Hub check is a one-file version of it.
- The research brief's Sources and Refuted sections — the citation list for the MLSys related-work paragraph; cite
  2506.06609 only as a within-family linear-map instrument precedent (it is model stitching, not KV transfer).

## Invariants

- `lint_scope` needs the scope sentence exactly once in README; `ledger_check` must print "ledger ok"; CI `test` on Linux
  is the gate (Windows reds are CRLF bash-exec tests, learning 2026-10-01).
- No ledger figure typed from memory: README numbers, the figure and paper-to-record were all read in-process; any new
  number goes through a summary file or a T file.
- `results/` never enters git; `docs/assets/*.png` does, built only by a pinned script.
- Public repo: no balances, tokens, hostnames or addresses anywhere. HF tokens env-only, revoked after use.
- Claude never writes git history; commit blocks are handed over in Git Bash format, no attribution trailers.
- Ledger entries, briefs, learnings and approved T files are immutable; a wrong one is superseded, not edited. The
  research brief in `~/dev/briefs` was amended on the operator's explicit ask; that is the one exception this session.

## Open / next

1. **Commit this brief and the two learnings** (untracked; the block is in the session reply).
2. **PR #19**: wait for Zain's local test; on merge, resolve the README conflict by taking main's README whole, merge commit.
3. **T03 P1–P4 approvals** after Emerson's per-paragraph comments; P2 placement decision.
4. **e9fl visibility ruling**: `…-e9fl-2026-10-07` is private (401 anonymously) while README and paper-to-record say so;
   making it public, or leaving the sentence, is the operator's call.
5. **CITATION.cff co-authors** from the submitted PDF p.1 before any release tag.
6. **Poster**: build in the first week of November from the T files; panel text can be drafted as a tables file on request.
