# Handoff — E9-long verified a second time, the 4-pager's §4.2 filled from 0036, and the R8 retry corrected

2026-09-10 05:00Z (session `lcfm-sprint-e9l-review`, `9c42735d` — the builds-and-review session of the overnight
plan). Newest commit this brief describes: **`50bc439`** on `main`, **ahead 1 of `origin/main` and unpushed**.
Two sibling briefs cover the other half of the night and are immutable: `2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md`
(the sitting, committed at `700d830`) and `2026-09-10-e9l-close-r8-unsettled-and-a-second-session-in-the-tree.md`
(the box session's close, untracked). This brief neither restates nor supersedes them; it records what THIS session
did, and corrects two claims that touch it. LCFM deadline 2026-09-11 11:59 UTC = 07:59 EDT.

## Current state

- **verified — entry 0036 survives an independent second summarizer pass.** 0036 was written by the box session
  from its own 01:20Z run. This session re-ran the same fail-closed summarizer at home 03:01–03:12Z with no
  refusal, rule line `-> HOLDS`, 35 scored of 35, and every load-bearing figure reproducing to the digit against
  the entry: cross K `0.9639764831640834`, τ-ladder at 0.10 `0.011865312667022983`, seam 16+ `0.0629`, bridge
  median 0.0000 → `CARRIED`, keep-subset re-score max 4.2e-04 relative with f* difference exactly 0. The claim
  H-E9L `HELD` therefore rests on two independent runs, not one.
  re-verify: `head -12 results/e9l/summary.md`, or rerun `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --config config/e9l.toml` (~9 min); this session's log is `results/e9l/logs/summarize_e9.20260910T0301Z.home-reverify.log`.
- **verified — the record and every gate at `50bc439`.**
  re-verify: `.venv/Scripts/python.exe -m pytest -q` → `423 passed, 1 skipped`; `-m linear_ceiling.lint_scope` → `scope ok`;
  `-m linear_ceiling.ledger_check` → `ledger ok (blocks unchanged vs HEAD)`; `grep -c "^verdict: H-E9L = HELD" ledger/ledger.md` → 1.
- **built — the E9-long instrument and its registration, all now in history.** Upstream RoPE spec (`063f402`,
  refuted independently and SURVIVES: bitwise cos/sin over all 81,920 positions, divide-once residual 9.5e-7,
  archived dumps bit-identical); `config/e9l.toml`; the driver's context floor, scaled dumps, configuration-bridge
  control, registered run order, `--resume` and `--close-partial`; the summarizer's floor, prefix rule, bridge
  re-score and reading, and the two length profiles; entry 0035; the 0036 draft. Commits `648f913`, `7054972`,
  `bacfe86`, `d582f48`, `cb9ae54`.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e9 --check --config config/e9l.toml` → `E9 gate: ready (entries 0019/0023/0025/0027/0035 committed; upstream pinned and clean; config/e9l.toml)`.
- **built — outline v2's §4.2 filled from 0036 only**, plus the abstract, the one-line claim, paper condition 2,
  limitation 1 and the freeze row; committed inside `700d830`. Every §4.1 figure was recomputed from
  `results/e9/summary.json` during the fill, which caught one typed error (matched fraction is 0.9344, not the
  0.7746 the draft carried). The section states what length changes as well as what holds: f* stays 0 in every
  |S| and position bin, while the τ = 0.03 ladder moves 0.1433 → 0.5255 and the far-from-seam floor 0.019 → 0.063.
  re-verify: `grep -c PENDING docs/paper/2026-09-10-lcfm-outline-v2.md` → 1, the legend line that defines the word.
- **corrected — this session's own R8 advice was wrong, and the correction is on the learnings ledger.** I told the
  operator to replace the CLI with `HfApi.upload_folder` "for one commit". With `hf_xet` installed that call takes
  the same batched pipeline, so it was no fix at all. Two entries record the measured cause and the mechanism.
  re-verify: `.venv/Scripts/python.exe -c "import huggingface_hub._upload_pipeline as p, hf_xet; print(p.INITIAL_COMMIT_SIZE_INDEX, p.COMMIT_SIZE_SCALE[p.INITIAL_COMMIT_SIZE_INDEX], p.MAX_COMMIT_INTERVAL)"` → `6 250 300.0`.
- **UNSETTLED — the R8 push, with the cause now measured.** At 03:47Z the push stopped with `429 … You have
  exceeded the rate limit for repository commits (128 per hour). You can retry this action in about 1 hour.`, at
  `Committing 247 / 724`. The limit counts commits, not bytes. The sibling entry that attributes the failure to the
  free 100 GB tier is superseded by
  `2026-09-10-the-r8-push-died-on-a-commit-rate-limit-not-the-storage-tier`, which preserves its arithmetic as a
  separate, still-unverified risk for the next attempt.
  re-verify (settles the backup's state; needs a read token in `$HF_TOKEN`): `.venv/Scripts/python.exe tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9l-2026-09-10 ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10 --exclude README.md`.
- **in flight and NOT this session's — `README.md` modified, `docs/status.md` deleted.** The box session's brief
  attributes both to this session ("dev-47 … is unwinding its own `50bc439`"). That is incorrect on both halves:
  `50bc439` was authored by the operator's own identity at 23:35:13 −0400, and this session has made no edit to
  `README.md` since the version committed at `3f67e4e` and has never touched `docs/status.md`. The in-flight change
  reverts the newcomer restructure back toward the `3f67e4e` README (10 lines differ) and removes the status page
  it created; its mtime is 23:36:34 −0400, one minute after `50bc439`. Owner unknown to this session — the operator
  or a third session. **Nobody should commit those two paths without claiming them first.**
  re-verify: `git log -1 --format='%an %cd' 50bc439`; `git diff --stat README.md`; `ls -la --time-style=full-iso README.md`.
- **not started** — the co-author refutation of entries 0025–0029, which is paper condition 1 and decides whether
  §4.1 stays; the n = 420 mapper arm on the E9-long kept subset (needs its own config and numbered entry).

## Locked decisions

- **E9 and E9-long figures reach the paper only through a passing summarizer, the cross arm always beside the
  same-model figure, and coverage travelling with every number** (0032, carried unchanged by 0035). Reason: a cell
  is decided once under the rule registered before its run. Premise holds: both cells came through their
  summarizers, and 0036 states "35 scored of 35 registered" on every figure.
- **0035 supersedes 0032's space clause and nothing else.** Reason: the operator's re-cut ruling lived only in
  briefs, and a brief cannot override an immutable entry. Premise holds; the co-author condition is untouched.
- **R8 is transport, not evidence.** Reason: the summarizer reads the local mirror, so a failed push costs a
  re-upload and never a result. Premise re-checked tonight: the mirror verifies 529/529 from raw bytes with no
  reference to the Hub.
- **Never run a summarizer against a hardlinked staging tree that is being uploaded.** Reason: the staging copies
  share inodes with `results/e9l/`, and this session's re-verification rewrote 17 regenerable files under a live
  uploader. Record files were untouched. Binding for the retry.
- **The R8 retry is the same `hf upload` command after the window clears — not a plan upgrade, not a
  single-commit workaround.** Reason: the server named commits per hour, and with `hf_xet` installed no
  single-commit path exists in-library short of `HF_HUB_DISABLE_XET=1`, which would sacrifice deduplication and
  resumability across 62 GB. At 250 files per commit the remaining files need single-digit commits.

## Reuse map

- `docs/paper/2026-09-10-lcfm-outline-v2.md` — what the team writes from; §4.2 is complete and every figure carries
  its entry and freeze status.
- `results/e9l/summary.md` and `results/e9l/logs/` — the passing summaries and both runs' logs (local by rule).
- `tools/ec2/verify_mirror.py` (evidence intact, ~49 s) and `tools/hf_verify_backup.py` (backup complete) — the two
  read-only checks that settle state without trusting a log.
- `tests/test_e9_long.py`, `tests/test_summarize_e9_long.py` — the fake-runner shape for the floor, the bridge, the
  run order, resume, the partial close and the profiles; extend these rather than inventing a fixture.
- `../kv-transfer-replication/tests/test_rope_spec.py` — the RoPE halt check and the demonstration that a plain-θ
  strip is wrong under YaRN.
- `docs/learnings/LEARNINGS.md` — nine 2026-09-10 rows across three sessions; read the two HF entries before any
  R8 retry.

## Invariants

- `results/`, `data/`, `traces/` never enter history; `results/e9/` and `results/e9l/`'s record files are never
  rewritten; entries 0025–0036 are immutable; no number reaches the ledger, the outline or a brief that a
  summarizer did not produce.
- `../kv-transfer-replication` is read-only from here; its RoPE-spec change is its own commit at `063f402`.
- Git history is the operator's: this session emits commands and never runs `git commit` or `git push`.
- **Two other writers are in this tree.** Stage explicit paths or bounded globs only; `git add -A` sweeps
  `README.md` and `docs/status.md` mid-edit by someone who has not claimed them here.
- `docs/learnings/LEARNINGS.md` rows and their entry files must be committed together, and the same is true of
  `docs/handoff/HANDOFF.md` and the briefs it points at — the gate fails on a row whose file is missing.
- Create nothing inside `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10/` while a push is pending: every file
  there is a file the upload must carry.

## Open / next

1. **Retry R8 after the rate-limit window**, with the same command from the staging root and the token exported by
   a `read` run on its own line, then `tools/hf_verify_backup.py`. If the verifier names missing files, re-upload
   only those. Only if it then fails on storage does the free-tier arithmetic become the live question.
2. **Resolve the two conflicting HF learnings entries** before either is committed: this session's kills the box
   session's quota-cause entry and restates its arithmetic, so commit the superseding one and drop the other, or
   commit both and let the `kills:` line stand as the record.
3. **Claim or revert the in-flight `README.md` and `docs/status.md` change.** It belongs to neither this session
   nor, on the evidence, the box session.
4. **Paper:** the team writes from outline v2; run `/rigor:honesty-check` over §5's verbs before submission, since
   E-RL is designed and unregistered and must read that way; condition 1 still decides §4.1.
5. Housekeeping when no re-run is planned: the EC2 key pair and security group, and the staging tree once
   `BACKUP VERIFIED` (it holds no unique bytes).

## Commit block (operator; Git Bash; explicit paths — two other writers hold this tree)

```bash
cd ~/dev/linear-ceiling
# Learnings: all six untracked 2026-09-10 entry files with the shared index, in one commit. The index already
# carries rows from three sessions and the gate fails on a row whose file is missing, so they cannot be split.
git add docs/learnings/2026-09-10-*.md docs/learnings/LEARNINGS.md
git commit -m "docs(learnings): R8 commit-rate limit supersedes the quota cause; xet batching; 401 diagnosis; live hardlinked staging; HF ceiling; rotted re-verify"

# Both untracked 09-10 briefs with the shared index, same coupling.
git add docs/handoff/2026-09-10-e9l-independent-verification-outline-filled-and-the-r8-retry-corrected.md \
        docs/handoff/2026-09-10-e9l-close-r8-unsettled-and-a-second-session-in-the-tree.md \
        docs/handoff/HANDOFF.md
git commit -m "docs: two 09-10 briefs — R8 unsettled and its cause measured; E9-long verified a second time"

git push   # also carries the unpushed 50bc439
```

Deliberately **not** staged: `README.md` and `docs/status.md` (in flight, owner unclaimed — item 3 above) and the
untracked `.claude/` directory. Verified with read-only `git status`, `git log`, `git diff --check` and the gate
set at `50bc439`; `origin` was contacted only by `git fetch`, and `main` was `[ahead 1]` at the time of writing, so
the push carries `50bc439` as well — confirm that is intended before running it.
