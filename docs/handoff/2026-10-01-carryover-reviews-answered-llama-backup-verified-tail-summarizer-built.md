# Handoff — Carryover: the LCFM reviews answered on the record, the Llama backup found and verified, the tail summarizer built and run

2026-10-01, written ~05:00Z (session `Carryover: MLSys NeurIPS Sprint`, 701ace2c; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl`).
Describes linear-ceiling `main` = **`0a51275`** (`e9_tail` committed by the operator; **1 ahead of `origin/main`** at
write time, not pushed). Uncommitted from this session: this brief, its index row, eight learnings entries and their
index rows. Untracked and not this session's: `docs/paper/tex/` (the superseded 09-13 scaffold), `.claude/`.
Previous brief in this lane: `2026-09-25-pr-5-merged-fixes-verified-refutation-target-and-algoverse-request-open.md`;
the AWS lane's refresh is `2026-10-01-e9l-aws-run-refresh.md` (committed `f711b28`).

Private working documents for this lane live in `~/dev/briefs/` (operator rule): the open-work audit
(`2026-10-01-linear-ceiling-open-work-audit.md`), the seven-task build plan
(`2026-10-01-plan-linear-ceiling-tonight.md`), and the seed that refreshed the AWS session
(`2026-10-01-seed-e9l-aws-run-context-update.md`).

## Current state

- **built — the review response map**, `docs/2026-09-30-review-response-map.md` (`e0bd810`): both official reviews
  (TE3a 6/4, teFN 6/3; decision Accept 09-29) quoted verbatim, each weakness mapped to the ledger line it rests on, with
  the figures that are NOT on the ledger named as such (W4's |R| of the 35 and native-window mean, W5's bin means, W3's
  tail). Every cited `entry:line` was refuted by a script that checks the line contains the figure.
  re-verify: sed -n 2206p ledger/ledger.md | grep -c "284,094"   # expect 1 (the native-window count the map cites)
- **built — three experiment designs**, `docs/drafts/e-beh-design.md`, `e-trunc-design.md`, `e-tail-design.md`
  (`e0bd810`): registration form, every threshold `??? (operator)`, no entry numbers, compute estimates derived from the
  E9L runbook. The meeting one-pager is `docs/2026-10-01-team-status-wednesday.md`.
  re-verify: grep -c "???" docs/drafts/e-beh-design.md docs/drafts/e-trunc-design.md docs/drafts/e-tail-design.md   # expect 6, 3, 2
- **built, verified — the Llama R8 backups exist**, under the co-author's account: `emmmy/linear-ceiling-e8f-2026-09-18`
  (9.8 GB) and `emmmy/linear-ceiling-e9f-2026-09-19` (55.4 GB), public. Every sha 0040–0044 pins and every report
  fingerprint matches; `tools/hf_verify_backup.py` printed `BACKUP VERIFIED` on full local mirrors (`~/dev/lc-mirror/e8f`,
  `C:\m\e9f`). README's two backup tables carry them (`5a71df6`). The 09-28 note's Finding 2 is superseded.
  re-verify: curl -s https://huggingface.co/api/datasets/emmmy/linear-ceiling-e9f-2026-09-19 | grep -o '"private":[a-z]*'   # expect "private":false
- **built, verified — `e9_tail`** (`0a51275`): `src/linear_ceiling/e9_tail.py` + `tests/test_e9_tail.py`. Runs
  `summarize_e9` as the gate, then from the same sha-pinned records computes tokens over each τ, the mean after removing
  the top 10 % / 20 %, pooled bin MEANS by seam and sender position, the native-window subset and |R|, writing
  `results/<cell>/tail.{json,md}` pinned to `report.json` and `summary.json`. Five tests green under a Linux venv
  (`~/lc-wsl-venv` in WSL Ubuntu, torch-cpu; the Windows venv errors in the fixture's driver on the known `e9.py:415`
  fsync bug before any tail code runs).
  re-verify: wsl -e bash -lc 'cd /mnt/c/Users/hossa/dev/linear-ceiling && PYTHONPATH=src ~/lc-wsl-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e9_tail.py'   # expect 5 passed
- **built, verified — the tail ran on all three Qwen cells** (04:08–04:36Z) with the upstream clone detached at each
  pin and returned to `main` afterwards. 16 of 16 figures match the outline's PENDING numbers and the ledger's counts
  (e9l: 30,701 of 387,508 over τ_K = 7.9 %, per-handoff max mean 0.2692, p90 0.2856, p99 0.7600, native window 284,094,
  |R| 11,462 / 7,085 / 19,853; e9: 9,047 of 155,257, max mean 0.2207; e9s: 10,336 of 155,257, max mean 0.2255). The
  gate rewrote each `summary.json` with unchanged verdict figures. `results/` is gitignored: the outputs are on this
  machine only.
  re-verify: .venv/Scripts/python.exe -c "import json; t=json.load(open('results/e9l/tail.json')); k=t['pooled']['same_K']; print(k['n_tokens'], round(k['fraction_over_tau'][str(t['tau']['K'])]*k['n_tokens']), t['native_window']['n_tokens'])"   # expect 387508 30701 284094
- **in-progress — tasks 2–7 of the briefs plan**: finding-4 pin tests; two dated doc lines; the anonymity denylist;
  the corrective-entry draft (`docs/drafts/append_corrective.py`, reads `tail.json` per cell); the R12 run on the
  Llama mirror; the close. None started.
- **planned — the macro table** (number → `entry:line` → macro): blocked on the submitted tree, which is not on this
  machine.

## Locked decisions

- **MLSys 2027 is the Carryover target; deadline Oct 30 2026 12:00 PDT** (mlsys.org/Conferences/2027/Dates, read
  09-30; submissions open Oct 10). Reason: ICLR dropped 09-19; the date, unknown then, is now public. LCFM 126 is
  accepted and non-archival; its camera-ready date is stated nowhere reachable (site, OpenReview group, decision email).
- **The upstream clone is moved by `git checkout --detach <pin>` and returned to `main`, never left detached**
  (operator, 2026-10-01, after the clone advanced to `0d27c68`). Reason: `config.py` resolves `upstream_path` to
  `../kv-transfer-replication` with no override, and each config is sha-pinned by its entry, so a worktree at the pin
  cannot be pointed at (the operator's preferred shape) without a ledger amendment. The pins (063f402, d5786df,
  06f8d55) are all ancestors of `main` and intact.
- **The tail's 1 − R² identity is gated at `_SUM_TOL`** (this session). Reason: float32 squares vs float64 moments;
  a 1e-9 gate refused a correct record on the fixture.
- **Short cells stay Condition-1-bound** (0032). The tail computes on e9 and e9s; the corrective draft states them only
  as corrections to sentences already on the ledger and marks them so.
- **Private working docs go to `~/dev/briefs`, not the repo** (operator rule, re-applied 2026-10-01 for the audit).
- **Paper, not software project** (operator, 09-19): no feature branches; history is the operator's; this session wrote
  no commit.

## Reuse map

- `src/linear_ceiling/e9_tail.py` — `tail(cfg, **summarize_kwargs) -> dict`; CLI `python -m linear_ceiling.e9_tail
  --config config/<cell>.toml`. Reuses `summarize_e9._load_tokens`, `_sst`, `_SUM_TOL`; `e9_pertoken.centered_delta`,
  `token_mean`, `seam_distance_left`, `seam_bin`. Output keys the corrective draft reads: `pooled.same_K.fraction_over_tau
  [str(tau_K)]`, `per_handoff[hid].same_K.mean`, `native_window.{n_tokens,share_of_matched,same_K}`, `receiver_length`,
  `seam_left_bins.same_K[].{bin,n_tokens,mean,median}`, `position_bins`, `summary_sha256`, `report_sha256`.
- `tests/test_e9_tail.py` — imports the `ran` fixture and `_retoken` from `tests/test_summarize_e9.py`; the pattern for
  any further summarizer-side test.
- The pinned-cell runner: `~/AppData/Local/Temp/claude/…/scratchpad/run_pinned_cells.sh` (session-local; its shape —
  `trap restore EXIT`, detach, run, return to `main` — is the one to copy for the e9f run).
- `~/lc-wsl-venv` — the Linux gate on this machine (python 3.12, numpy, torch 2.14 cpu, pytest). Run with
  `PYTHONPATH=src` from `/mnt/c/Users/hossa/dev/linear-ceiling`.
- Local mirrors: `~/dev/lc-mirror/e8f` (verified) and `C:\m\e9f` (verified). Copy, do not move, into `results/e8f`,
  `results/e9f`, `mappers/` for the R12 run (plan task 6).
- `docs/2026-09-30-review-response-map.md` §3 — the rulings list; `~/dev/briefs/2026-10-01-plan-linear-ceiling-tonight.md`
  — tasks 2–7 with code and commands.

## Invariants

- Every ledger config pin is the LF blob hash: verify with `git show HEAD:<file> | sha256sum`, never the CRLF worktree
  file (learning 2026-10-01).
- `summarize_e9` refuses whenever the clone's HEAD differs from the pin on the invoked paths, ancestor or not; the Qwen
  cells need 063f402 (e9l, e9s) or d5786df (e9), the Llama cell 06f8d55. Return the clone to `main` after every run.
- `results/`, `data/`, `traces/`, `mappers/` never enter history; `git clean -x` destroys the tail outputs and the mirrors'
  copies. Entries 0001–0044 are immutable; a correction is a new entry.
- `docs/drafts/README.md` is the only number allocator. 0045/0046 are staged for the Llama LONG cell; the corrective
  entry's number is a ruling (0045 recommended, with the Llama drafts moving up together). `append_0039.py` carries a
  taken number: never run it.
- The `hf` login cached on this machine (`hossainpazooki`) was used read-only through the environment for the two
  verifier runs; it is to be logged out / revoked by the operator (R9).
- No number enters the ledger or the paper that a fail-closed reader did not produce in-process; `tail.json` is such an
  output only while its `summary_sha256` / `report_sha256` pins still match.

## Open / next

1. **Operator: push** (`main` is 1 ahead), then commit this close:
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/handoff/2026-10-01-carryover-reviews-answered-llama-backup-verified-tail-summarizer-built.md \
           docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-10-01-*.md
   git commit -m "docs: Carryover close — reviews mapped, Llama backup verified, e9_tail run; eight learnings"
   git push
   ```
   Not folded in: `docs/paper/tex/` (another session's). Verified vs assumed: `main...origin/main` read 1/0 at ~04:48Z;
   the AWS session's `2026-10-01` learning row is already in `LEARNINGS.md` (committed `0265290`), so the index carries
   both sessions' rows.
2. **Plan tasks 2, 3, 4** (no rulings needed): finding-4 pin tests, the two dated doc lines, the denylist.
3. **Ruling: the corrective entry's number** (0045 with the Llama drafts moving to 0046/0047, or wait). Then task 5's
   draft and its `--preview` against the real `tail.json` files.
4. **Task 6, R12 on the Llama mirror**: copy the mirrors into `results/` and `mappers/`, detach the clone at 06f8d55,
   `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report results/e8f/report.json`, then the summary and
   the tail; return the clone to `main`; compare with the Hub `summary.json` and 0044. Closes the 09-28 note.
5. **Operator housekeeping carried**: delete the two empty `hossainpazooki/…-e8f/-e9f` datasets; revoke the cached Hub
   login and the 09-10/09-13 write tokens; `git push origin --delete llama-second-family`; the Algoverse form; the ARR
   ruling; Condition 1.
6. **Design note for the paper**: seam-bin MEANS are 1.6–1.8× the medians (learning); the Corollary 3 restatement on
   means will print larger numbers than the medians the submission showed. Say so in the camera-ready text, not after.
