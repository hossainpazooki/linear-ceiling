# Handoff — E9-long's record is committed; the R8 push is partial on a rate limit; a second session holds the working tree

2026-09-10 04:35Z (session `e9l-aws-run`, `018fwd195AS7uS2tvJdgSoYP` — the box-and-launch session). Newest commit
this brief describes: **`50bc439`** on `main`, which is **ahead 1 of `origin/main` and unpushed**. This brief does
not restate the sitting: that is `docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md`, committed
at `700d830` and immutable. This one supersedes that brief's **"Open / next" only**, and corrects one of its
`re-verify:` lines that has since rotted. LCFM deadline 2026-09-11 11:59 UTC = 07:59 EDT.

## Current state

- **built / verified — the whole sitting record is now IN HISTORY.** Five commits landed after the earlier brief was
  written: `cb9ae54` (ledger 0036 + draft retired), `6bd9047` (`tools/ec2/` + the runbook), `852c104` (three
  learnings entries), `700d830` (docs + the sitting brief), `50bc439` (a newcomer README with status moved to
  `docs/status.md`). The first four are the commit block that brief emitted; `50bc439` is the other session's.
  re-verify: `git log --oneline 3f67e4e..HEAD` → 5 commits, newest `50bc439`.
- **built / verified — H-E9L `HELD` is on the ledger and the chain is intact.**
  re-verify: `grep -n "^verdict: H-E9L = HELD" ledger/ledger.md` → one line (2227);
  `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok (blocks unchanged vs HEAD)`.
- **built / verified — the evidence is home and self-checking.** 529 fingerprinted files, 61,143,230,360 B,
  re-hashed from raw bytes against `report.json` (`084d9480af74…`, `complete: true`).
  re-verify: `.venv/Scripts/python.exe tools/ec2/verify_mirror.py e9l` → `529/529 … ALL VERIFIED` (~49 s).
- **verified — AWS is clean; nothing from the sitting is billing.** The instance is gone, no unattached volumes
  remain, and the only other instance in `us-east-1` is a pre-existing stopped `t3.micro` unrelated to this work.
  The key pair `lc-e9l-2026-09-10` and the security group `sg-03021d0b6c09b4c75` still exist and are free to keep.
  re-verify: `aws ec2 describe-instances --profile kv-platform-admin --region us-east-1 --filters Name=instance-id,Values=i-0eafae594ebe8c291 --query 'length(Reservations)' --output text` → `0`
  (the same query on a live id returns `1`, so it distinguishes absence from presence);
  `aws ec2 describe-volumes --profile kv-platform-admin --region us-east-1 --filters Name=status,Values=available --query 'Volumes[]' --output text` → empty.
  **Correction to the earlier brief:** its release `re-verify:` line (`--instance-ids … State.Name` → `terminated`)
  now prints `None`, because EC2 forgets terminated instances within hours. The claim is still true; use the line
  above instead. Learnings entry `2026-09-10-a-re-verify-line-anchored-on-a-providers-transient-record-rots-within-hours`.
- **PARTIAL — the R8 backup push stopped on a rate limit, and the cause is now known.** I first inferred, from an
  `hf.exe` that was gone and left no resume state, that the push had hit the storage tier. The server said otherwise
  in the operator's terminal at 03:47Z: `429 Too Many Requests … You have exceeded the rate limit for repository
  commits (128 per hour). You can retry this action in about 1 hour`, at `247 / 724` files committed. So the push is
  **partial, past the small records, and stopped by a commit-count limit that has nothing to do with bytes**. My
  inference is superseded by `docs/learnings/2026-09-10-the-r8-push-died-on-a-commit-rate-limit-not-the-storage-tier.md`,
  which `kills:` my entry; both stay on the record so the chain reads. **The first retry is the same command after the
  window clears, not a plan upgrade.** What remains genuinely unknown is only which files are on the Hub. Nothing is at
  risk either way: R8 is transport, the home mirror is the evidence.
  re-verify (settles it, needs a read token in `$HF_TOKEN`): `.venv/Scripts/python.exe tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9l-2026-09-10 ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10 --exclude README.md`
  → `BACKUP VERIFIED`, or the list of files to re-upload.
- **risk for a LATER attempt, not what stopped this one — the free storage tier.** The arithmetic stands as
  arithmetic and nothing more: staging is 61,937,723,784 B (~61.9 GB), and the repo documents ~48 GB (E9) plus
  27.7 GB (n420) already in private datasets against a free 100 GB allowance, leaving ~24 GB. Those two prior
  figures are the repo's own and were never measured against the Hub, so ~75.7 GB is a lower bound. A ceiling may
  bite once the retry gets past the rate limit; it did not bite here. Read the plan and used storage on the Billing
  page before assuming either way.
- **built — the standing GPU protocol now carries this sitting's lessons.** Twelve dated amendments inside the
  existing rules of `docs/gpu-experiment-protocol.md`, plus a second "The box, concretely" section for a rented
  instance: R2 an extrapolated peak is a bound to be replaced by a probe on the granted card; R4 run the driver
  unbuffered and key liveness on the checkpoint, never the log; R5 and R6 name the ssh pull loop and the
  independent mirror verifier; R7 gains the single-tenant step 0 rule, the fail-open grep fix in step 4, and
  termination with its expiring proof in step 6; R8 gains quota-before-the-sitting and the ban on summarizing
  into a live hardlinked stage; R12 gains the rule for anchoring a `re-verify:` line. The rule-instance table
  now points at the E9-long records. After the 429 refuted my storage inference, R8 was corrected again so it
  states the commit-rate limit as what stopped the push and the byte ceiling as an unobserved later risk, the
  token quick reference now forbids pasting anything after its `read -s` line, and the push recipe says to
  expect several rate-limit windows.
  re-verify: `grep -c "added 2026-09-10" docs/gpu-experiment-protocol.md` -> 12;
  `sed -n '/^## The box, concretely (a rented/,/^## Where/p' docs/gpu-experiment-protocol.md` -> the new section.
- **defect in my own earlier brief, for whoever runs that block next.** The R8 block I wrote at line 78 of
  `docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md` opens with `read -s HF_TOKEN && export HF_TOKEN`
  as the first line of a pasted sequence. `read` consumes the next line of standard input, which in a paste is the
  next command, so the token is never entered and the push runs unauthenticated; the operator hit exactly this and saw
  `Not logged in` with a 401 out of `create_repo`. Run the `read` alone, paste nothing after it, and confirm with
  `hf auth whoami` before the long command. That brief is committed and immutable, so the correction lives here and in
  `docs/learnings/2026-09-10-a-propagating-401-from-hf-upload-proves-no-credential-not-a-missing-scope.md`.
- **in progress — NOT THIS SESSION'S, do not disturb.** Session `dev-47` (`9c42735d`) holds the working tree:
  `README.md` modified and `docs/status.md` deleted (it is unwinding its own `50bc439` in the tree), plus one
  untracked learnings entry of its own (the hardlinked-staging-tree finding). `main` is ahead 1 and unpushed.
  re-verify: `git status --short` and `git status -sb | head -1` → `## main...origin/main [ahead 1]`.
- **not started** — the co-author refutation of 0025–0029 (paper condition 1); the n = 420 mapper arm on the
  E9-long kept subset (needs its own config and entry); the Algoverse request (moot for this run).

## Locked decisions

- **The sitting brief at `700d830` is immutable.** Reason: rigor's briefs are append-only records, and a committed
  brief is what a pick-up measures drift against. Hence this second brief rather than an edit. The reason holds.
- **R8 is transport, not evidence** (protocol R8). Reason: the summarizer reads the local mirror only, so a failed
  or partial push costs a re-upload, never a result. Premise re-checked and holding: the mirror verifies 529/529
  from raw bytes independently of anything on the Hub.
- **Never run a summarizer against a hardlinked staging tree that is being uploaded** (the other session's entry,
  2026-09-10). Reason: the staging copies share inodes with `results/e9l/`, so a re-run rewrote 17 files under a
  live uploader. Independently corroborated here: `results/e9l/summary.json` has link count 2 and mtime Sep 9
  23:12. Treat as binding for the retry — copy the tree, or finish and verify the push first.
- **Rented L40S over the Algoverse queue**, and **termination held until the summarizer passed** — both from the
  sitting brief, both closed and unchanged.

## Reuse map

- `docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md` — the sitting itself, its R8 command block,
  and the four-commit block that has now landed. Read it first; this brief only corrects and extends it.
- `docs/2026-09-10-e9l-gpu-runbook.md` §6 — every timestamp and hash of the run, including the durable `01:35:36Z`
  termination read-back.
- `tools/ec2/verify_mirror.py` (R6, ~49 s) and `tools/hf_verify_backup.py` (R8) — the two checks that settle
  "is the evidence intact" and "is the backup complete" without trusting any log.
- `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10/` — the R8 tree, hardlinked to `results/e9l/` (see the locked
  decision above before touching it) with its dataset card already written.
- `docs/learnings/LEARNINGS.md` — six 2026-09-10 rows now; three from the sitting, two from this brief, one from
  session `dev-47`.

## Invariants

- `results/`, `data/`, `traces/` never enter history; `results/e9/` is never rewritten; entries 0025–0036 are
  immutable; no number reaches the ledger or the paper that a summarizer did not produce.
- The upstream `../kv-transfer-replication` is read-only from here and its tree was not touched by this session.
- Git history is the operator's: this session emits commands and never runs `git commit` or `git push`.
- **A second session is editing this tree.** Anything staged must name explicit paths — a `git add -A` or a broad
  glob will sweep up `README.md`, `docs/status.md` and `dev-47`'s learnings entry mid-edit.
- `docs/learnings/LEARNINGS.md` now carries `dev-47`'s uncommitted row alongside mine, and the gate requires every
  row to have its file: **the three untracked 2026-09-10 entry files must be committed together with the index**,
  or the gate breaks on a row pointing at a missing file.

## Open / next

1. **Finish R8** — the only loose end. Mint the token with a bare `read -s HF_TOKEN` on its own line, confirm with
   `hf auth whoami`, and re-run the same upload after the commit window clears; it resumes rather than restarting.
   Expect to need more than one window: 724 files against 128 commits per hour, with `hf_xet` batching the commits for
   the Python API too, so there is no one-commit workaround. Then settle completeness with `tools/hf_verify_backup.py`
   and re-upload only what it names. Only if that run reports a storage ceiling does the plan question arise; the
   options then are upgrading, making the E9 dataset public to reclaim ~48 GB, or pushing the ~2 GB of small records
   and holding the tensors. Nothing else in the program is blocked by any of this.
2. **Commit block below**, once `dev-47` has finished with `README.md` and `docs/status.md`. Its unpushed `50bc439`
   and its in-flight revert are its own to resolve; do not commit those paths.
3. **Paper:** outline v2 §4.2 is filled from 0036 (`700d830`); `/honesty-check` on §5's verbs before submission;
   condition 1 (the co-author refutation of 0025–0029) still decides whether §4.1 stays.
4. Housekeeping when no re-run is planned: delete the key pair `lc-e9l-2026-09-10` and the security group
   `sg-03021d0b6c09b4c75`; drop the staging tree only after `BACKUP VERIFIED` (it holds no unique bytes).

## Commit block (operator; Git Bash; explicit paths, because a second session is in the tree)

```bash
cd ~/dev/linear-ceiling
# All three untracked 2026-09-10 learnings entries plus the shared index, together: the index already carries a row
# for dev-47's entry, and the gate fails on a row whose file is missing.
git add docs/learnings/2026-09-10-the-third-private-hf-backup-crosses-the-free-tier-check-quota-before-the-sitting.md \
        docs/learnings/2026-09-10-the-r8-push-died-on-a-commit-rate-limit-not-the-storage-tier.md \
        docs/learnings/2026-09-10-a-re-verify-line-anchored-on-a-providers-transient-record-rots-within-hours.md \
        docs/learnings/2026-09-10-a-hardlinked-staging-tree-is-live-a-summarizer-rerun-rewrites-it-under-the-uploader.md \
        docs/learnings/2026-09-10-a-propagating-401-from-hf-upload-proves-no-credential-not-a-missing-scope.md \
        docs/learnings/2026-09-10-hf-xet-makes-upload-folder-batch-its-commits-so-the-one-commit-workaround-does-not-exist.md \
        docs/learnings/LEARNINGS.md
git commit -m "docs(learnings): six entries from the E9-long close; the 429 supersedes the free-tier inference"

# The standing protocol is its own concern: what every future runbook inherits from this sitting.
git add docs/gpu-experiment-protocol.md
git commit -m "docs(protocol): rented-instance rules — measured peaks, unbuffered driver, R7 step 0/4/6, R8 quota, R12 anchoring"

git add docs/handoff/2026-09-10-e9l-close-r8-unsettled-and-a-second-session-in-the-tree.md \
        docs/handoff/2026-09-10-e9l-independent-verification-outline-filled-and-the-r8-retry-corrected.md \
        docs/handoff/HANDOFF.md
git commit -m "docs: second 09-10 brief — R8 unsettled, AWS clean, tree shared with another session"

git push   # also carries the unpushed 50bc439
```

`docs/handoff/HANDOFF.md` is shared, and session `dev-47`'s row for its own 09-10 brief is already in it — which is
why that brief is staged above alongside mine. Read it before committing: it is that session's work, not mine.
The index is pointers only and no gate catches a row whose file is missing, so this would not have failed loudly.

Deliberately **not** staged: `README.md` and `docs/status.md` (session `dev-47` is mid-edit on both) and the
untracked `.claude/` directory (not this session's). Verified with read-only `git status`, `git log` and
`git diff --check`; `origin` was not contacted, and `main` was `[ahead 1]` at the time of writing, so the push
carries `50bc439` too — confirm that is intended before running it.
