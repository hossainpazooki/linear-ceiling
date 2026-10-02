# Handoff — Carryover close: 0045 appended, the Llama cell's R12 closed from this machine, E-BEH has a driver to port, Condition 1 has a candidate review

2026-10-02, written ~03:40Z (session `Carryover: MLSys NeurIPS Sprint`, 701ace2c; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl`).
Describes linear-ceiling `main` = `origin/main` = **`ce7b3e7`** (`docs: 0045 is on the ledger; README allocator, outline
PENDING rows, repo brief`, the operator's post-append doc commit on top of `470133e`, the append), CI green at `470133e`.
Uncommitted at write: this brief, its index row, five learnings and their index rows, and a dated note appended to
`docs/2026-09-30-review-response-map.md`. Untracked, not this session's: `docs/paper/tex/`, `.claude/`. Previous brief in this lane: `2026-10-01-carryover-reviews-answered-llama-backup-verified-tail-summarizer-built.md`;
the sibling lane's: `2026-10-01-main-branch-pick-up-pr-6-merged-ruling-11-renumber-and-the-corrective-entry-staged.md`.

Private documents for this lane in `~/dev/briefs/`: the open-work audit (`2026-10-01-linear-ceiling-open-work-audit.md`,
dated close sections appended), the seven-task plan (`2026-10-01-plan-linear-ceiling-tonight.md`, tasks 1–7 done), the
Condition 1 issue draft (`2026-10-01-issue-condition-1-draft.md`, unposted), the AWS-lane seed.

## Current state

- **built — ledger 0045 appended** (`b3bf7ec`, scope sentence per the Condition 1 ruling `62a8e8d`, script retired `470133e`):
  the per-token tail per cell (e9l 7.9 %, e9 5.8 %, e9s 6.7 %, e9f 11.3 % of matched tokens over τ_K; per-handoff mean
  maximum 0.2692 / 0.2207 / 0.2255 / 0.2860), the 0025/0029 R² label, seam-bin means beside medians, 0044's E7-hash
  erratum. Descriptive; no cell moves. Next free number 0048 (0046/0047 are the staged Llama long drafts).
  re-verify: grep -c "^### 0045" ledger/ledger.md; .venv/Scripts/python.exe -m linear_ceiling.ledger_check   # expect 1, then ledger ok
- **built, verified — the Llama cell's R12 from this machine** (task 6): `summarize_e8 --config config/e8f.toml` PASSED
  (18:19Z) with the three k rows byte-identical to 0040's; `summarize_e9 --config config/e9f.toml` PASSED (18:50Z) with every
  verdict figure equal to 0044; `e9_tail` on e9f PASSED (19:03Z). All under the clone detached at 06f8d55 and returned to
  `main`. Independently, PR 6 (Ritvik, merged `704e4c4`) reproduced both summaries from a clean clone. Three regenerations
  now give the E7 report hash `0aba0fbe…`; 0044's `27dc922e…` is the outlier (0045 records it).
  re-verify: .venv/Scripts/python.exe -c "import json; t=json.load(open('results/e9f/tail.json')); print(t['n_scored'], round(max(p['same_K']['mean'] for p in t['per_handoff'].values()),4))"   # expect 28 0.286
- **built, verified — plan tasks 2–4** (`57e0d06`, `c3f4e30`, `a6a746d`): finding-4 pin tests (both pass; no code change was
  needed), the two dated doc lines, the anonymity denylist (78 rows, no word collisions).
  re-verify: wsl -e bash -lc 'cd /mnt/c/Users/hossa/dev/linear-ceiling && PYTHONPATH=src ~/lc-wsl-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_summarize_e9.py -k "prefix_control_has_no_rope_record or absent_prefix_control_even"'   # expect 2 passed
- **built — the Llama mirrors restored for the run** (gitignored): `results/e8f`, `results/e9f`, `results/mapper/`,
  `results/probe/`, `mappers/llama…`, `data/e8f/` here; `data/kv/llama…`, `data/e8f/`, `data/tokens/`, `mappers/llama…`,
  `results/mapper/llama…` in the upstream clone (the last shows there as untracked; the upstream does not ignore it).
  The verified staging mirrors stay at `~/dev/lc-mirror/e8f` and `C:\m\e9f`.
  re-verify: ls results/e8f/report.json results/e9f/report.json ../kv-transfer-replication/mappers/llama3.2-3b-to-llama3.1-8b/k1.json   # expect all three
- **drafted, unposted — the Condition 1 issue** (`~/dev/briefs/2026-10-01-issue-condition-1-draft.md`): asks @neuriv to PR
  his `docs/refutations.html` review into `docs/reviews/` and @ritvikagg to approve as the second signature; scope per the
  rulings below. Also drafted: the Slack message to Vikram (three design questions + the two asks) and the Algoverse form
  (24 h, 40 GB slice, E-BEH + E-TAIL Part B; team name, code and emails to fill).
- **assessed, not built — E-BEH's driver exists to port**: `neuriv/cache-injection` `practical.py::construct()` is the
  in-situ reuse (learning 2026-10-02). What the port adds: the archived alignment pairs as M, the recorded continuation
  teacher-forced (per-token KL, top-1), a size-matched random NULL beside the position scramble, subset-recompute arms by
  block splitting, fp32 + SDPA pin, an identity check against the archived receiver dumps.
- **planned — E-TAIL Part B driver**; **planned — E-TRUNC** (config key, paired summarizer; L49 count corrected to 19 by
  the sibling lane); **planned — the macro table** (blocked on the submitted tree); **planned — audit item 15** (fsync at
  `e9.py:415`; the E8 raw-byte config hash, learning 2026-10-02).

## Locked decisions

- **Ruling 11 (operator, 2026-10-01): the corrective entry is 0045; the Llama long drafts are 0046/0047**, with
  `config/e9fl.toml`'s gate moved in the same commit (`36e0621`). Done.
- **Condition 1 for the camera-ready (operator, 2026-10-01): the 2026-09-08 numbers-freeze clause of 0032 is moot** (the
  submission is accepted); what remains is a co-author refutation merged under `docs/reviews/` with two signatures. Scope:
  0032's leads A and B in full (R1–R6, R9–R12), the same attacks on 0036/0038, the tail figures 0045 adds; **R13 and R14 in
  scope; R7 addressed by E-BEH and the limitations paragraph, not by refutation; R8 deferred until E-TRUNC has run.**
  0045's scope sentence carries the ruling.
- **The upstream clone is moved by `git checkout --detach <pin>` and returned to `main`** (operator, 2026-10-01); the
  config's `upstream_path` has no override, so worktrees cannot be pointed at. Used four times today; the clone is on `main`.
- **The Hub token stays** (operator, 2026-10-01 evening): the 18:32Z fine-grained token with gated-repo scope is kept on this
  machine; the Llama 3.2 license is accepted, the 3.1 license is not and is not needed for the summarizers.
- **E-BEH is built on Vikram's `construct()`**, with his three recorded complete-history cells entering as the pilot
  (this session's recommendation; co-run or credit is his answer to the message).
- **Private working docs in `~/dev/briefs`**; **paper, not software project**; **history is the operator's** (this session
  wrote no commit; the operator committed and pushed every block).

## Reuse map

- `src/linear_ceiling/e9_tail.py` and `tests/test_e9_tail.py` — the tail summarizer (0a51275); outputs under
  `results/<cell>/tail.{json,md}` for e9, e9l, e9s, e9f, pinned to the summaries now on disk.
- The pinned-run shape: a bash script with `trap restore EXIT` that detaches the clone, runs, and returns it to `main`
  (session scratchpad `run_pinned_cells.sh`, `run_e9f_tail.sh`); copy the shape, not the path.
- `~/lc-wsl-venv` (WSL Ubuntu, python 3.12, numpy, torch-cpu, pytest): the Linux gate on this machine, run with
  `PYTHONPATH=src` from `/mnt/c/Users/hossa/dev/linear-ceiling`.
- `C:\m\ci` — a clone of `neuriv/cache-injection` at `8e8417a`; `practical.py`, `local_experiments.py`, `common.py`,
  `docs/refutations.html`, `results/historical-summary.json`.
- `docs/2026-09-30-review-response-map.md` — the rulings list; `docs/2026-10-01-run-queue-farhan.md` (sibling lane) — the
  box task list and its §10 rulings; `docs/drafts/e-beh-design.md` — the arms and statistics the port implements.
- For E8 re-summaries on Windows: write the config blob (`git show HEAD:config/e8f.toml > config/e8f.toml`), run, then
  `rm` + `git checkout -- config/e8f.toml` (learning 2026-10-02) until the hash fix lands.

## Invariants

- Entries 0001–0045 are immutable; the next number is 0048 and only `docs/drafts/README.md` allocates. `append_0039.py`
  carries a taken number: never run it.
- The short-cell figures (0029, 0038, 0034's E9 arm, and 0045's e9/e9s paragraphs) enter no paper until the co-author
  review is merged with two signatures. The freeze clause no longer applies; the review does.
- `summarize_e9` refuses whenever the clone's HEAD differs from the cell's pin on the invoked paths; return the clone to
  `main` after every run. The Llama pin is 06f8d55; PR 2 changed five invoked files above it.
- `results/`, `data/`, `mappers/`, `traces/` never enter history; `git clean -x` destroys the tail outputs, the restored
  mirrors and the Linux venv's work. The upstream's restored `results/mapper/llama…` is untracked there, not ignored.
- Config pins are LF blob hashes; hash with `git show HEAD:<file>`, never the CRLF worktree file.
- No box request before the entry it serves is on the ledger (R1); the Algoverse clock starts at approval.

## Open / next

1. **Operator: commit this close** (explicit paths):
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/handoff/2026-10-02-carryover-close-0045-appended-llama-r12-closed-e-beh-has-a-driver.md \
           docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-10-02-*.md \
           docs/2026-09-30-review-response-map.md
   git commit -m "docs: Carryover close — 0045 appended, Llama R12 closed here, E-BEH driver found; five learnings"
   git push
   ```
   Verified vs assumed: tree state read at ~03:50Z (only this session's files modified or untracked, plus
   `docs/paper/tex/`); `main` was 0/0 against `origin/main` at `ce7b3e7` after a fetch at that time.
2. **Operator: send the Vikram message and post the Condition 1 issue** (both drafted). His answers to the three design
   questions gate the E-BEH registration draft.
3. **E-BEH registration draft + driver port** (this lane, on his answers and the bands ruling); **E-TAIL Part B draft +
   driver** (on the quantity / backend / tolerance rulings). Then the Algoverse form, the day the entries land.
4. **Carried, operator-only:** delete the two empty `hossainpazooki/…-e8f/-e9f` datasets and `origin/llama-second-family`;
   the AWS key pair and security group; move the sibling lane's staged learnings in, if not yet moved.
5. **Code fixes, unowned:** the E8 config hash (both files, with a test) and the `e9.py:415` fsync, so the Windows suite and
   E8 re-summaries stop false-refusing.
