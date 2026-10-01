# Handoff — main-branch session: pick-up, PR #6 reviewed and merged, ruling 11 applied, the corrective entry 0045 staged

2026-10-01 ~20:10Z (session `dev-fd`, f87605d5; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl`).
Newest commit this brief describes: **`20a4e71`** (`docs: denylist row for the merged R12 record; e9_tail and draft
commands`) = HEAD = `origin/main`, CI green. Uncommitted at write: this brief, its index row, eight learnings entries
and their index rows. Untracked and not this session's: `.claude/`, `docs/paper/tex/`. Outside the repo: the audit
`~/dev/briefs/2026-10-01-linear-ceiling-open-work-audit.md` gained a dated close section.

Picked up from `2026-10-01-aws-lane-refreshed-run-queue-handed-to-a-co-author-and-a-mutated-r8-stage.md` (and its
sibling, the Carryover close). The operator split the day's work: **this session owned the main branch and the Qwen
cells; the "Carryover: MLSys NeurIPS Sprint" session owned the Llama family** (its R12 run on the local mirror, task 6).
That session's results are referenced here only where this session re-verified them.

## Current state

- **built — PR #6 (Ritvik, R12 recompute of 0040/0044 from a clean clone + the `emmmy/` backups) reviewed and MERGED**
  at `704e4c4` (merge commit, as PR #5). Review comment: anchors and Hub revisions hold; the "third regeneration" on
  this machine is the 09-01 artifact the 09-10 summary recorded, so the honest count stays "two of three"; three
  non-blocking asks (scripts not in the PR, machine-specific re-verify paths, denylist row).
  re-verify: `git log --format='%h %s' -1 704e4c4` → `Merge pull request #6 ...`; `gh pr view 6 --json state --jq .state` → `MERGED`.
- **built — ruling 11 applied (`36e0621`): 0045 is the corrective entry; the Llama long drafts are `append_0046.py`
  (registration) and `append_0047.py` (figures); `config/e9fl.toml`'s gate ends at `"0046"`; the config test expects it.**
  The registration draft gained `VERDICT = "0044"` because its prose had used `PREV` to mean the short cell's verdict
  entry, which `PREV` no longer is. Next free number: **0048**.
  re-verify: `ls docs/drafts/append_004*.py | tr '\n' ' '` → `append_0045.py append_0046.py append_0047.py`; `grep -c '"0046"' config/e9fl.toml` → `1`; `grep -n 'VERDICT = "0044"' docs/drafts/append_0046.py` → one line.
- **built — `docs/drafts/append_0045.py` staged (`dcf9bd5`) with `tests/test_append_0045.py` (6 tests).** The corrective
  entry: per-cell tail (e9l, e9, e9s, e9f) from `tail.json`, the per-handoff MAXIMUM mean and its margin under τ_K, the
  0025/0029 R² label, summary-file figures by key (|S| median, own-norm, same-K depth profile, and for e9l the
  configuration bridge's per-handoff R²), and 0044's E7-hash erratum. Every ledger line anchor is derived by sentence
  search inside the named entry (refuses on 0 or 2+ hits); the pins refuse on drift; the word `summarize_e7` is refused
  (ledger_check's manifest marker). Preview on the four real cells reproduces every PENDING figure in outline v3
  §5.1/§5.2; the in-memory candidate passes `check`, `check_against` and the scope lint. **Not appended.**
  re-verify: `wsl -e bash -lc 'cd /mnt/c/Users/hossa/dev/linear-ceiling && PYTHONPATH=src ~/lc-wsl-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_append_0045.py'` → `6 passed`; `.venv/Scripts/python.exe docs/drafts/append_0045.py --preview | grep -c "exceed τ_K individually"` → `4`.
- **built — `docs/drafts/e-trunc-design.md` L49 count corrected 18 → 19 (`092c734`)**, recounted from `n_sender` in
  `results/e9l/align/coverage.json`: one handoff (astropy-14369 traj#108) has |S| = 49,196, over the 49,152 level and
  under 0036's 50,000 bin edge.
  re-verify: `grep -c '\*\*19\*\* over 49,152' docs/drafts/e-trunc-design.md` → `1`.
- **built — the two hardlinked R8 staging trees are DELETED** (`~/dev/hf-staging/linear-ceiling-e9{l,s}-*`). Every file
  in them was a hardlink into `results/` except the dataset card, which was byte-identical to the Hub's; the live
  `summary.json` files went from link count 2 to 1 with unchanged hashes.
  re-verify: `ls ~/dev/hf-staging/` → `logs/` only; `stat -c %h results/e9l/summary.json results/e9s/summary.json` → `1` `1`.
- **built — denylist row for the merged review file, CLAUDE.md command lines for `e9_tail` and the draft, README staged
  note (`20a4e71`).**
  re-verify: `grep -c 'llama-cell-r8-backup-and-recomputation' docs/2026-10-01-anonymity-denylist.md` → `2` (the table row and the dated per-term note); `grep -c 'append_0045.py --preview' CLAUDE.md` → `1`.
- **verified, not this session's build — the Llama session's local R12 run closed task 6**: `summarize_e9` and
  `e9_tail` on `results/e9f` from the mirror, clone detached at `06f8d55` and returned to `main`. This session
  recomputed the e9f tail from `tail.json`: 19,094 of 169,437 tokens over τ_K (11.27 %), max per-handoff mean 0.2860
  (0.00008 under τ_K), seam mean/median up to **8.59×** (that session's chat said 8.7; the file says 8.59).
  re-verify: `git -C ../kv-transfer-replication status --short --branch | head -1` → `## main...origin/main`; `.venv/Scripts/python.exe -c "import json;t=json.load(open('results/e9f/tail.json'));k=t['pooled']['same_K'];print(k['n_tokens'], round(k['fraction_over_tau'][str(t['tau']['K'])]*k['n_tokens']))"` → `169437 19094`.
- **in progress:** nothing is running from this session.
- **planned, not started:** the append of 0045 (operator); rulings 1–3 and tasks A–E of the run queue; the macro table
  (blocked on the submitted tree); Condition 1; the HF login revocation (still `hossainpazooki` at pick-up); deleting the
  two empty `hossainpazooki` e8f/e9f datasets (1 file each at pick-up).

## Locked decisions

- **This session is main-branch / Qwen-side; the Llama family belongs to the Carryover sprint session** (operator,
  2026-10-01, "the other session I'm dedicating to Llama-family models"). Reason: one upstream clone, one cell at a
  time, and two sessions were live on the tree. Ruling 11 was the one Llama-touching change, taken by the operator here.
- **Ruling 11: the corrective entry takes 0045; the Llama long drafts move to 0046/0047 in one commit with the gate
  string** (operator, 2026-10-01). Reason: the corrective entry can run today and the Llama long cell cannot; the drafts
  README's own contingency; the commit must precede any `e9 --check`, which verifies the config is committed unmodified.
- **Rulings 4 and 7 were applied at their recommended defaults, not ruled separately**: one widened corrective entry
  carries the tail table, the per-handoff maximum, the seam-bin MEANS beside the medians and the |R| row (and now the
  Llama cell). Reason: the operator said "begin task 5" after the defaults were stated; nothing is appended, so this is
  relitigated by editing the draft, not the ledger.
- **PR #6 merged with a merge commit, not squash** (operator). Reason: PR #5 precedent; the review branch's commits stay
  attributable to the co-author.
- **The draft derives every ledger line number; none is typed.** Reason: the plan's anchors had rotted by one line after
  the PR 5 merge (learning), and an entry landing above would rot them again.
- **The draft refers to the E7 report by its `summary.json` key and never writes `summarize_e7`.** Reason: ledger_check's
  `MANIFEST_MARKER` makes that word a manifest-citation obligation (learning).
- **The clean-clone E7 hash is CITED from `docs/reviews/2026-09-28-...`, not recomputed.** Reason: it is another
  machine's result; the entry says so in the sentence.
- **The depth profile enters as the same-K per-layer medians only, with the file named for the other arms** (this
  session's call on the audit's "enter or cut"). Reason: 28–32 values per arm per cell; the verdict arm is the one the
  paper discusses. Cut is one clause if the operator prefers.

## Reuse map

- `docs/drafts/append_0045.py` — `anchor(text, num, needle)` / `block_text(text, num)` (entry-scoped sentence search),
  `load_cell(rdir)` (pin check), `build_entry(text, cells, date)`, `prepare_append(text, entry)` (the `append_0046`
  chain idiom). Import it in a test with `runpy.run_path(..., run_name="draft")` so nothing runs.
- `tests/test_append_0045.py` — the pattern for testing a draft on the `ran` fixture: run `e9_tail.tail`, load the cell,
  build, compare on whitespace-normalized text (paragraphs are wrapped at 112), check the candidate with
  `ledger_check.check` / `check_against`.
- `src/linear_ceiling/e9_tail.py` — `tail(cfg, **summarize_kwargs)`; outputs `results/<cell>/tail.{json,md}` pinned to
  `summary.json` and `report.json`. All four cells have one on this machine.
- `~/lc-wsl-venv` — the Linux gate on this machine (`PYTHONPATH=src`, from `/mnt/c/Users/hossa/dev/linear-ceiling`).
  The Windows venv cannot run the `ran` fixture (the `e9.py:415` fsync bug).
- Exact-match edit scripts (abort unless each old string matches once; preserve CRLF) — the shape used for the
  renumber and the doc edits; session-local under the scratchpad, trivial to re-write.
- `docs/2026-10-01-run-queue-farhan.md` §10 — the rulings list, now with ruling 11 answered inline.

## Invariants

- `results/`, `data/`, `traces/`, `mappers/` never enter history; `git clean -x` destroys the four `tail.json` files and
  the mirrors' copies. Entries 0001–0044 are immutable; a correction is a new entry (0045 is that entry).
- `docs/drafts/README.md` is the only number allocator; next free is **0048**. `append_0039.py` carries a taken number:
  never run it.
- **The draft's anchors are computed at append time.** If any entry lands before 0045, re-run `--preview` and read it
  again; the line numbers in the text will have moved, correctly.
- `ledger_check` reads the literal `summarize_e7` as an E7-figure citation that requires an `e7-manifest-sha256:` line.
- One upstream clone means one cell at a time **across sessions**: check `ListAgents` / the process list before
  detaching it or running any gate.
- Every config pin is the LF blob hash: `git show HEAD:<file> | sha256sum`, never the CRLF worktree file.
- The WSL suite on this checkout shows exactly four CRLF-shebang failures in `tests/test_runpod_*`; any fifth is real.
- Git history is the operator's; no attribution trailers; stage explicit paths, never another session's files.

## Open / next

1. **Commit this close** (operator), explicit paths:
   `git add docs/handoff/2026-10-01-main-branch-pick-up-pr-6-merged-ruling-11-renumber-and-the-corrective-entry-staged.md docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-10-01-a-live-sibling-session-*.md docs/learnings/2026-10-01-the-wsl-suite-*.md docs/learnings/2026-10-01-a-sibling-sessions-chat-figure-*.md docs/learnings/2026-10-01-this-machines-e7-report-*.md docs/learnings/2026-10-01-a-plans-ledger-line-anchors-*.md docs/learnings/2026-10-01-entry-0042-does-not-*.md docs/learnings/2026-10-01-an-entry-that-mentions-summarize-e7-*.md docs/learnings/2026-10-01-bridge-r2-in-summary-json-*.md`
2. **Append 0045** (operator): `.venv/Scripts/python.exe docs/drafts/append_0045.py --preview`, read it whole, then the
   same command without `--preview` (it runs `ledger_check`), then in ONE commit: `git rm docs/drafts/append_0045.py`,
   update the README's staged paragraph to "appended", and `git add ledger/ledger.md`. `tests/test_append_0045.py`
   imports the script by path and must go in the same commit (`git rm`), or CI goes red.
3. **After the append:** outline v3's PENDING rows (§5.1, §5.2, the reconciliation table) can name 0045; the
   `docs/2026-09-30-review-response-map.md` W3/W4/W5 rows get their entry. Paper session's work.
4. **Rulings 1–3** (E-TRUNC margin and statistic, shrinkage gate, L32-native) unblock run-queue task A. Ruling 1's
   default names the median; the corrective entry shows the mean/median gap per cell, which is the evidence for that choice.
5. **Carried, not closed:** HF login revocation and the two empty `hossainpazooki` datasets; Condition 1; the macro
   table; the drafts README's 09-19 staging paragraph (kept as a record, superseded by the dated one above it).
