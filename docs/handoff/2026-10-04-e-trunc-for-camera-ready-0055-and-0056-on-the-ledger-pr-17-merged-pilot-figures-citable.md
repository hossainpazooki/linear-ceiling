# Handoff — E-TRUNC for the camera-ready: 0055 and 0056 on the ledger, PR #17 merged, the co-author's pilot figures citable under a provenance sentence

2026-10-04 ~09:10Z (session `d4f6aa2f`, renamed `e-trunc-for-camera-ready`; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl`). Newest commit this brief
describes: **`01b660b`** (`docs: mark 0055 appended; W2 registered with its limitations`) = `main` = `origin/main`, CI green
on `c37f626` / `a5c8691` / `01b660b`; tree clean except untracked `.claude/`, `docs/paper/tex/`. Uncommitted at write: this
brief, its index row, three learnings and their index rows.

Supersedes nothing; extends this session's first close
`2026-10-04-e-trunc-rulings-taken-under-supervision-0055-staged-the-pre-check-rewrote-ruling-2.md` (committed `366a4db`),
whose "Open / next" items 1–2 the operator executed between 08:4xZ and 09:03Z — faster than the brief assumed, and with
one addition the brief did not foresee (0056).

## Current state

- **built, on the ledger — entry 0055 (E-TRUNC registration)** at `a5c8691`, the previewed text plus two LIMITATION sentences
  the operator added on `e-trunc` (`f2e4829`): the 14 void handoffs are a stated limitation (21 of 35 compared), and the deferred
  L32-native cell means nothing in the entry compares native with YaRN on the same tokens. Draft and its test retired.
  re-verify: `grep -c '^### 0055 ' ledger/ledger.md` → `1`; `grep -c '14 of 35 handoffs are void under the floor' ledger/ledger.md` → `1`; `git ls-files docs/drafts/append_0055.py tests/test_append_0055.py | wc -l` → `0`; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`.
- **built, on the ledger — entry 0056 (pilot figures admitted)** at `caccab5`, appended BEFORE 0055 in file order: the operator's
  ruling that the two merged co-author documents (`docs/2026-10-01-cache-behavior-h100.md`, `docs/2026-10-01-a100-analysis.md`) may
  be cited in paper text under a provenance sentence, superseding 0046/0047's "in any paper" clauses.
  re-verify: `grep -n '^### 005[56] ' ledger/ledger.md` → 0056 at a lower line than 0055; `grep -c 'Reused sender states' docs/2026-10-01-cache-behavior-h100.md` → `1`.
- **built, merged — the E-TRUNC instrument** via PR #17 (`c37f626`, 08:56Z): the truncation key, `n_sender_desc`, the four
  `config/e9t-*.toml`, `summarize_e9_trunc`, the tests; history split into the three conventional commits plus the operator's
  limitation and 0056 commits.
  re-verify: `git log --oneline --merges -1 main` → `c37f626 Merge pull request #17 …`; `.venv/Scripts/python.exe -m pytest -q tests/test_e9_trunc.py tests/test_summarize_e9_trunc.py` → `28 passed`.
- **measured, on disk only — the four alignment passes and the shrinkage pre-check** under the committed configs
  (`results/e9t-*/align/`, `results/e9t/shrinkage.{json,md}`); nothing else under `results/e9t*` (R1 holds).
  re-verify: `ls results/e9t-full results/e9t-l32` → `align/` only; `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc --shrinkage | grep -c 'median 0.4470'` → `1`.
- **verified — gates on main:** `ledger ok`, `scope ok`, CI green on the three newest commits.
  re-verify: `gh run list -L 3 --json headSha,conclusion --jq '.[] | "\(.headSha[0:7]) \(.conclusion)"'` → three `success`.
- **NOT done — an independent refutation of 0055's figures.** The skeptic subagent died on credits before running (first
  close); the entry was appended on the session's own two-path recompute. The figures are now immutable on the ledger; a
  refutation would land as a later entry if it found anything.
- **stale, not this session's to fix:** `docs/drafts/README.md` still ends "Next free number: **0056**" though 0056 is appended
  (`01b660b` marked only 0055). The ledger's file order now ends `0046, 0047, 0054, 0052, 0056, 0055` — 0052 (the second
  family's E8 amendment) and 0054 were appended by the other session and their drafts retired; only `append_0053.py` (0052's
  figures), 0048/0049 and 0050/0051 remain staged.
  re-verify: `grep -o '^### 00[0-9][0-9] ' ledger/ledger.md | tail -6` → that order; `git ls-files docs/drafts/ | grep -c 'append_005[24]'` → `0`; `grep -o 'Next free number: \*\*00[0-9][0-9]\*\*' docs/drafts/README.md | tail -1` → `**0056**`.
- **planned, not started:** the E-TRUNC sitting (bound 3.58× E9-long ≈ 4.8 h on an L40S; card requested only now that 0055 is
  on the ledger, R2 probe first); the L32-native cell's instrument and amendment; the figures entries for 0046/0047/0055.

## Locked decisions

- **Rulings 1–3 are ratified by the append** (operator, `a5c8691`): ±0.005 on the far-from-seam (16+) same-K median; the
  |M_∩| ≥ 2,000 floor with the ratio reported (NOT the 0.80 ratio: the pre-check voids 29 of 35 under it); L32-native taken
  and deferred (no mixed-RoPE dump path). Reason: entry 0055's own text; no longer provisional. Pick-up check: `[e9.trunc]`
  in `config/e9t-full.toml` reads `margin_abs = 0.005`, `min_common_matched = 2000`.
- **Co-author pilot figures are citable in paper text under a provenance sentence** (operator, entry 0056): run by a co-author
  on the named card at the tagged commit with the pinned environment; code, inputs manifest and environment in the repository;
  not independently recomputed. Reason: the reviewer's question is evidential, the Hub-and-recompute rule was a house
  admission rule, and the figures were already public in merged docs. The operator-registered re-runs (0046/0047) are now
  the operator's recomputation and a cross-platform control, not a precondition for citing.
- **The camera-ready carries only ledger figures plus 0056's two documents**; W2 is "registered (0055)", never a number.
  Reason: no E-TRUNC run exists. Pick-up check: `results/e9t-full/report.json` absent.
- **E-TRUNC "length" means causal-prefix length on the late-S tokens the receiver re-renders; the 14 void handoffs are a
  limitation stated in the paper** (operator, `f2e4829` → 0055). Reason: the pre-check; M_∩ is biased late.
- Earlier locked decisions stand (first close): 0055 not 0052; the allocator re-read at HEAD before any number is written.

## Reuse map

- Entry 0056's provenance-sentence pattern for citing a co-author's run: card, tagged execution commit, freeze record, driver
  path, environment, reproduction comment URL, "not independently recomputed".
- `summarize_e9_trunc.common_subset` / `shrinkage` and `tests/test_summarize_e9_trunc.py::_block_pairs` (first close).
- Gating a branch without switching a dirty checkout: `git worktree add --detach ~/dev/lc-wt-<name> <branch>` +
  `PYTHONPATH=<worktree>/src` (learnings entry).
- The split-a-WIP-blob recipe (backup ref → `git reset --soft <base>` → three `git add`/`commit` → `git push --force-with-lease=<branch>:<old-tip>`), as run on `e-trunc`.

## Invariants

- Entries 0001–0047, 0052 and 0054–0056 are immutable (ledger_check chains by FILE order, which is now non-monotonic);
  `docs/drafts/README.md` is the only allocator and is currently STALE by one (next free is 0057, not 0056) — read the
  ledger's headings before trusting it.
- The four e9t configs are pinned by hash in 0055; an edit re-hashes the registration and invalidates the alignment passes
  (the coverage pin refuses).
- `results/`, `traces/`, `mappers/` never enter git; `results/e9t*` hold alignment passes only until the sitting.
- `ts:` in a learnings entry is read off the clock at capture (the five first-close entries are stamped ~1.5 h ahead; learnings entry).
- Two sessions never edit one tree; this session's second half ran read-only on main while the operator worked.

## Open / next

1. **Operator:** commit this close (`git add docs/handoff/ docs/learnings/`, one `docs:` commit); fix the allocator line to
   0057 while there.
2. **Camera-ready** (LCFM, 11:59Z today): apply `~/dev/briefs/2026-10-04-lcfm-camera-ready-paste.tex`; W1/W7 sentences cite
   0056's two documents with the provenance sentence; W2 reads "registered (0055)".
3. **E-TRUNC sitting** (MLSys): R1 is met; next is the R2 probe under `config/e9t-full.toml` on the granted card, then the
   four levels FULL-first, `summarize_e9_trunc`, and a figures entry (0057 or later) — the reading's three outcomes are
   pre-registered in 0055.
4. **Owed:** an independent refutation pass over 0055's stated figures (would land as its own entry), and the L32-native
   instrument before any amendment that names that cell.
