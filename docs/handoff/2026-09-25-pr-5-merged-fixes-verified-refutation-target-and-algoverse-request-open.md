# Handoff — PR 5 merged with its review fixes verified; the refutation's target and the Algoverse request are open

2026-09-25, written ~04:30Z. Describes linear-ceiling `main` = `origin/main` = `3902a16` (the PR 5 merge),
working tree clean apart from untracked `.claude/` and `docs/paper/tex/`. This brief is uncommitted.
Previous brief: `2026-09-21-astra-review-landed-pr-5-review-posted-and-the-carryover-items-never-started.md`.

## Current state

- **built — PR 5 merged** (2026-09-24T03:32Z, merge `3902a16`): ledger 0039–0044 (Llama-3.2-3B → Llama-3.1-8B;
  E8 in 0040, τ_K 0.2861; H-E9F HELD 28/28 in 0044). Two fix commits after the review: `0859155`, `0ff21ad`.
  re-verify: grep -n "^### 004[0-4]" ledger/ledger.md   # expect five headings, 0040-0044
- **built, verified — review finding 1 (stop signal hit the wrapper)**: `tools/runpod/driver_child.sh` `exec`s
  the driver and writes the driver's own PID. Under WSL on 09-24 a stand-in driver launched by it, SIGTERM'd by
  the recorded PID, stopped; nothing was left running.
  re-verify: grep -n "exec \"\$lc_py\"\|driver_pid=\$!" tools/runpod/driver_child.sh   # expect both
- **built, read not run — findings 2 and 3**: outstanding bytes come from remote sizes (`remote_file_sizes`);
  the partial close needs two consecutive empty listings.
  re-verify: git grep -n "kept_bytes\|two consecutive account listings" -- tools src
- **built with a gap — finding 4**: `summarize_e9.py` now requires exactly same_src / same_tgt / cross_src per
  handoff, and refuses a prefix record lacking `dump_rope`; it still PASSES when the prefix-control record is
  absent entirely (`elif recs and prefix is not None`).
  re-verify: grep -n "prefix is not None\|required = {" src/linear_ceiling/summarize_e9.py
- **CI green on Linux; the suite is red on Windows.** On 09-24 a clean worktree of `3902a16` (PYTHONPATH=src)
  gave 491 passed, 28 failed, 26 errors, all in the e9 / runpod / sitting-b / summarize_e9 test files; the two
  messages read were `Bad file descriptor` and `not a valid Win32 application` (tests exec bash scripts).
  Inferred environmental, not every failure read. Gates: `ledger ok`, `scope ok`.
  re-verify: gh run list --branch main --limit 1 --json conclusion --jq '.[0].conclusion'   # expect success
- **not started — the refutation.** Nothing run. Rows in `docs/reviews/refutation-0025-0029-rows.csv`.
- **drafted, not submitted — Algoverse H100 request** (in chat 2026-09-25, not in the repo): Inference, 24 h,
  40 GB slice, Qwen short-cell work (refutation GPU rows R9b / R11; optional downstream pilot). Team name,
  teammates, mentor email and AWS credit line left for the operator.

## Locked decisions

- Paper, not software project: no feature branches, tracker is Airtable, minimal Actions (operator, 09-19).
- ICLR dropped (09-19); async-RL work lives in `hossainpazooki/lag-ladder` (09-22).
- History is the operator's; this session wrote no commit.

## Reuse map

- `docs/reviews/refutation-0025-0029-rows.csv` — the refutation instrument (hide `OPERATOR_ONLY_note`).
- `~/dev/briefs/2026-09-03-algoverse-a100-request-e9.md` — the previous Algoverse form; `tools/jupyterhub/`
  drives a JupyterHub-only box; protocol `docs/gpu-experiment-protocol.md` §"The box, concretely".
- `docs/handoff/2026-09-18-sitting-a-record.md` — what Sitting A (Llama E8 on RunPod) produced.
- `docs/2026-09-20-astra_review.md` — findings register.

## Invariants

- 0032 requires a CO-AUTHOR refutation of 0025–0029. An operator-run attack is evidence, not the discharge.
- The Llama cell (0042–0044) is a separate, unrequired refutation target; it cannot discharge Condition 1.
- Next free ledger number after the staged 0045 / 0046 drafts is 0047. `docs/drafts/append_0039.py` (Path B)
  is on main but its number is permanently taken — renumber before any use. Row R0 of the CSV is stale on this.
- Llama results (`results/e8f`, `results/e9f`) are not on this Windows machine; whether Sitting A's R8 HF
  backup exists is unchecked.
- The Llama long cell (8B fp32, ~80 GB) cannot run on the Algoverse pool (max 40 GB slice).
- Algoverse login may be shared: protocol R7 step 0 before any release; JupyterHub only, launch detached.

## Open / next

1. **Operator: pick the refutation's target and runner** — Qwen 0025–0029 by a co-author (Path A), by the
   operator (evidence only), or both; and/or the Llama cell. Start with rows R1 and R9 in every case.
2. **Operator: submit the Algoverse form** with the [fill] fields; run the R2 memory probe on the granted card
   (the 16.7 GiB figure is a protocol/probe number, not a ledger one, and the doc's slice wording is unreconciled).
3. Check whether Sitting A's R8 backup exists before any Llama refutation.
4. Small fix, unowned: make `summarize_e9` refuse a report with no prefix-control record (finding 4 gap).
5. Housekeeping, not run: `git push origin --delete llama-second-family` (0 unmerged commits);
   `git branch -D track-b` if still present.
6. Carried from 09-21, still unstarted: the Carryover macro table and anonymity denylist; the corrective
   entry for the token sentence in 0029 / 0036 / 0042 with the per-handoff maximum; the Condition 1 ruling.

```bash
cd ~/dev/linear-ceiling
git add docs/handoff/2026-09-25-pr-5-merged-fixes-verified-refutation-target-and-algoverse-request-open.md \
        docs/handoff/HANDOFF.md
git commit -m "docs(handoff): PR 5 merged and verified; refutation target, Algoverse request open"
git push
```
