# Handoff — E9-long ran end to end on a rented L40S; 35 of 35 scored; mirror verified; box terminated

2026-09-10 02:00Z (session `018fwd19`, the box-and-launch session of the overnight plan; the builds session's brief is
`2026-09-09-e9-long-build-and-paper-recut.md`). Newest commit this brief describes: linear-ceiling `3f67e4e` = origin/main
plus this session's UNCOMMITTED work (commit block at the end); upstream `kv-transfer-replication` at `063f402` = origin/main,
clean except the untracked `results/mapper/qwen3-0.6b-to-1.7b/n420/` (ours). LCFM deadline 2026-09-11 11:59 UTC = 07:59 EDT.

## Current state

- **verified — the sitting.** AWS EC2 g6e.4xlarge (1× L40S 48 GB), us-east-1d, `i-0eafae594ebe8c291`, out of pocket (no credit;
  G-quota 768 vCPU). Setup from fresh clones at the pins, mapper by sha, traces by manifest, `e9 --check` ready on the box; R2
  probe measured the 1.7B YaRN forward at **31.56 GiB** peak at T = 80,111 (seed's extrapolation 29.2); driver launched
  23:53:12Z, **EXIT=0 at 01:13:09Z**, 3 bridge + 35/35 handoffs in the registered order, no partial close, 0 Tracebacks.
  re-verify: `grep -c "^\[" results/e9l/logs/box/e9l.log` → 38; `cat results/e9l/logs/box/e9l.rc` → `EXIT=0`; runbook §6.
- **verified — the mirror (R5/R6).** Six kept directories pulled by fingerprint and deleted on the box; at home
  `tools/ec2/verify_mirror.py e9l` → `529/529 fingerprinted files verified from raw bytes, 61,143,230,360 B; ALL VERIFIED`;
  `report.json` sha256 `084d9480af74de2b…`, `complete: true`; the box's 222 small-record hashes diffed by path: 0 differing.
  re-verify: `.venv/Scripts/python.exe tools/ec2/verify_mirror.py e9l` (49 s).
- **verified — release (R7).** Sweep rc 0 after two designed aborts (image baseline; the sweep's own log); no tensors left on the
  box; logs pulled and hashed (`results/e9l/logs/box/`); nothing sensitive; HF cache removed; **`terminated` read back from
  `describe-instances` at 01:35:36Z**. Life 1 h 49 min ≈ $5.5 + ≈ $5.5 egress.
  re-verify: `aws ec2 describe-instances --profile kv-platform-admin --region us-east-1 --instance-ids i-0eafae594ebe8c291 --query 'Reservations[0].Instances[0].State.Name'` → `terminated`.
- **verified — `summarize_e9 --config config/e9l.toml` PASSED at home** (rc 0, no refusal, 9 min; log
  `results/e9l/logs/summarize_e9.20260910T0120Z.log`): 35 of 35; bridge (control 4) median native-vs-scaled f*(τ_K) 0.0000 vs
  0.15 → **CARRIED** (τ_K carries; H-E9L reads on the same footing as 0029); keep-subset re-score within 0028's tolerance
  (sums 3.4e-08 rel, squares 4.2e-04 rel, f* diff 0); prefix-invariance 0.000e+00; rule line `-> HOLDS`.
  re-verify: rerun the command (9 min) or `head -12 results/e9l/summary.md`.
- **verified — entry 0036 APPENDED** (`append_0036.py`, in-process summarizer passed again; `appended 0036 (H-E9L = HELD); chain 055a14059297`;
  `ledger ok`): H-E9L row `unresolved` → **`HELD`**, 35 scored of 35, bridge CARRIED leads the entry, cross arm named beyond DEGRADES,
  read on a floor. Script retired (deleted) in this change; drafts README, README rows, CLAUDE.md program state updated.
  re-verify: `grep -n "^verdict: H-E9L = HELD" ledger/ledger.md` → line 2227; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`.
- **built — `tools/ec2/`** (box.sh, setup.sh, probe_e9l.py, run.sh, pull.py, verify_mirror.py, release_sweep.sh, README): the ssh
  form of `tools/jupyterhub/`, used for this sitting exactly as committed except the two in-sitting fixes named in the runbook
  (sweep baseline rule + fail-open count; `python -u` in the launcher).
- **built — runbook** `docs/2026-09-10-e9l-gpu-runbook.md` (§6 log complete through release), **three learnings entries**
  (2026-09-10: sweep fail-open; block-buffered driver log; step 0 on a rented box), CLAUDE.md / README pointers.
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings` → 7 FAILs, all pre-existing (09-02/09-04), none 09-10.
- **staged, NOT PUSHED — R8 backup.** `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10/` = `results/e9l/` + `mappers/qwen3-0.6b-to-1.7b/k1.*`
  by HARDLINK (same NTFS volume; 723 files, 61,937,721,692 B; verified from raw bytes in place; card `README.md` written).
  Needs the operator's scoped write token; commands below.
- **not started** — co-author refutation of 0025–0029 (paper condition 1); the n = 420 arm on the e9l kept subset (own config +
  entry); the Algoverse request (moot for this run; optional for re-runs).

## Locked decisions — premises checked

- **Rented L40S instead of the Algoverse 3g.40gb queue** (operator, 2026-09-09; recorded in 0035). Premise held: the queue was
  four days against a 42-hour deadline; the sitting cost ≈ $11 and the run fit with ~13 GiB to spare.
- **Termination held until the summarizer passed** (this session). Reason: a refusal might have wanted a same-platform
  re-score; the hold cost < $1. Not needed: the summarizer passed on the first run.
- **R7 step 0 aborts were resolved by inspection, never by loosening the abort.** The single-tenant rule (image baseline = mtime
  before launch) is now in the sweep; the abort behaviour is unchanged.
- **D1–D5, the bridge on one platform, the prefix stopping rule** — the builds session's; all held at the run (bridge first,
  order n_sender_asc, 35 = the registered set, keep draw of 3 realized).

## Reuse map

- `docs/2026-09-10-e9l-gpu-runbook.md` — §1 box facts, §2 the measured ladder, §3 the R3 table, §6 every timestamp and hash.
- `tools/ec2/README.md` — the eight commands of a sitting, in order.
- `results/e9l/summary.md` — the passing summary (local by rule); `results/e9l/logs/box/` — the box's own record.
- Entry 0036 itself (`grep -n "^### 0036" ledger/ledger.md`); the draft is retired. Trap for the next append script: run it with
  `PYTHONIOENCODING=utf-8` on Windows (the console is cp1252 and the entries carry τ; the first preview died on the final print).
- `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10/` — the R8 tree, ready.

## Invariants

`results/`, `data/`, `traces/` never enter history; `results/e9/` untouched; `results/e9l/` written only by the driver (box), the
puller (mirror), the summarizer (`summary.*`, `logs/`); entries 0025–0036 immutable; no number enters the ledger or the paper that
a summarizer did not produce; upstream read-only (its tree is unchanged by this session); git history is the operator's; the
ssh private key `~/.ssh/lc-e9l-2026-09-10` stays at home (the key pair and the security group `sg-03021d0b6c09b4c75` still exist
in the account; harmless, deletable).

## R8 backup — operator, from this shell (token never on disk, never in a flag)

```bash
cd ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10
# Hub UI first: New dataset "linear-ceiling-e9l-2026-09-10", PRIVATE; then a fine-grained WRITE token scoped to it, named
# e9l-backup-pusher-hossain-exp-2026-09-17
read -s HF_TOKEN && export HF_TOKEN
HF=~/dev/linear-ceiling/.venv/Scripts/hf.exe; REPO=hossainpazooki/linear-ceiling-e9l-2026-09-10
$HF upload "$REPO" results/e9l/report.json results/e9l/report.json --repo-type dataset --quiet      # 1. small records first
$HF upload "$REPO" results/e9l/logs results/e9l/logs --repo-type dataset --quiet
$HF upload-large-folder "$REPO" . --repo-type dataset --num-workers 1                                 # 2. the tree: ONE resumable run, ONE worker
$HF upload "$REPO" README.md README.md --repo-type dataset --quiet                                    # 3. the card last = "complete"
~/dev/linear-ceiling/.venv/Scripts/python.exe ~/dev/linear-ceiling/tools/hf_verify_backup.py "$REPO" . --exclude README.md   # BACKUP VERIFIED
unset HF_TOKEN   # then revoke the token in the UI
```

## Open / next

1. **Operator:** the commit block below (the ledger commit alone, then the rest); then the R8 push above.
2. **Paper:** fill outline v2's PENDING §4.2 slots from 0036 only; `/honesty-check` on §5's verbs; condition 1 (co-author
   refutation of 0025–0029) still decides §4.1.
3. **Optional, own entry:** the n = 420 mapper on the e9l kept subset via `e9_rescore` (needs `config/e9lc.toml`).
4. Housekeeping: delete the key pair `lc-e9l-2026-09-10` and `sg-03021d0b6c09b4c75` when no re-run is planned; remove the
   hardlink staging dir after `BACKUP VERIFIED` (it holds no unique bytes).

## Commit block (operator; Git Bash; nothing here touches the upstream)

```bash
cd ~/dev/linear-ceiling
# 1. the ledger alone, with the draft's retirement riding along (precedent d582f48 for 0035)
git add ledger/ledger.md docs/drafts/README.md
git add -u docs/drafts/                       # stages the deletion of append_0036.py
git commit -m "docs(ledger): 0036 E9-long ran; H-E9L HELD (35 of 35); retire append_0036.py"
# 2. the sitting's tooling and record
git add tools/ec2/ docs/2026-09-10-e9l-gpu-runbook.md
git commit -m "feat(ec2): rented-instance sitting tooling (box, setup, probe, launcher, puller, verifier, sweep); E9-long runbook"
# 3. learnings (3 entries + index)
git add docs/learnings/2026-09-10-*.md docs/learnings/LEARNINGS.md
git commit -m "docs(learnings): three entries from the E9-long sitting (sweep fail-open, buffered log, step 0 on a rented box)"
# 4. the docs the run made stale, and this brief
git add README.md CLAUDE.md docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md docs/handoff/HANDOFF.md
git commit -m "docs: H-E9L HELD in README and program state; EC2 tooling pointers; sitting handoff"
git push
```

Not folded in: the untracked `.claude/` directory (not mine); `results/e9l/` and the staging dir (never in history, by rule).
Verified with read-only `git status` and `git diff --check`; the remote was not re-checked after `3f67e4e`, where main tracked
origin at 0/0, so a plain `git push` is expected to suffice.
