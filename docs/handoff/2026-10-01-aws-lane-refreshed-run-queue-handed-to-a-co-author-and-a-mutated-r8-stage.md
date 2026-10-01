# Handoff — the AWS lane refreshed, the MLSys run queue handed to a co-author, and an R8 stage found mutated

2026-10-01 04:55Z (session `e9l-aws-run`; transcript `C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl`).
Newest commit this brief describes: **`bf75008`** (`docs: Carryover close — reviews mapped, Llama backup verified,
e9_tail run; eight learnings`), which is HEAD and `origin/main`. This session's three documents are already in
history — `f711b28` (refresh brief + box plan), `0265290` (percentile learning), `7d8a66d` then `264cc30` (the run
queue, written and then recut). Uncommitted at write: this brief, its index row, two learnings entries and their
index rows. Untracked and **not** this session's: `docs/paper/tex/`.

Supersedes nothing. The 09-14 close `2026-09-14-e9s-closed-backup-verified-and-a-second-session-on-condition-1.md`
and the 10-01 refresh `2026-10-01-e9l-aws-run-refresh.md` both still stand **except** for one rotted line in the
latter, corrected under *Current state* below.

## Current state

- **built — the AWS lane is re-verified and nothing is billing.** Account 547729607601 via `kv-platform-admin`; the
  `default` profile is dead (`InvalidClientTokenId`) and was left dead. Only a foreign stopped t3.micro exists.
  AMI `ami-0eb7d782cce2fe526` available, deprecation 2028-09-07; quota *Running On-Demand G and VT* 768 vCPU
  against the 16 a box needs; g6e.4xlarge offered in us-east-1a/b/c/d. Prices re-fetched live: **$3.00424/h**,
  egress **$0.090/GB** first 10 TB, gp3 **$0.08/GB-month** — the 09-10 runbook's $3.00/$0.09 stand.
  re-verify: `aws ec2 describe-instances --profile kv-platform-admin --region us-east-1 --query "Reservations[].Instances[].[InstanceId,State.Name]" --output text` → only `i-0785c090815238989 stopped`; `aws ec2 describe-images --profile kv-platform-admin --region us-east-1 --image-ids ami-0eb7d782cce2fe526 --query "Images[].State" --output text` → `available`.
- **built — `docs/2026-10-01-mlsys-box-plan.md`** (`f711b28`): per design the card, probe, hours, dollars at those
  re-fetched prices, disk sizing and the R7 release path, plus what waits on which ruling. No launch.
  re-verify: `git log --oneline -1 -- docs/2026-10-01-mlsys-box-plan.md` → `f711b28`.
- **built — `docs/handoff/2026-10-01-e9l-aws-run-refresh.md`** (`f711b28`), the pick-up of the 10-01 seed with every
  §1 row re-verified. **One of its re-verify lines has since rotted** and the next session should not trust it: it
  asserts `results/e9s/summary.json` → `2f562aca`, which the e9_tail re-run replaced with `859a8c98`. No figure
  moved (see the learnings entry); the brief's other claims hold.
  re-verify: `sha256sum results/e9s/summary.json` → `859a8c98…`, **not** the `2f562aca…` that brief names.
- **built — `docs/2026-10-01-run-queue-farhan.md`** (recut at `264cc30`): the co-author ask as five lettered tasks
  (A E-TRUNC, B E-TAIL Part B, C E-BEH, D *optional* a third 1B→3B pair, E the Llama LONG cell), each with the
  ruling it waits on, the code that must land first, minimum card, time and deliverable; plus host-agnostic
  env/probe/run/reader/verify commands, six traps, the return path, and **11 numbered rulings with recommended
  defaults**.
  re-verify: `git log --oneline -1 -- docs/2026-10-01-run-queue-farhan.md` → `264cc30`; `grep -c "^| \*\*[A-E]\*\*" docs/2026-10-01-run-queue-farhan.md` → `5`, one per lettered task.
- **built — the upstream pin is merged, reachable, and the clone has it.** PR #1 on
  `hossainpazooki/kv-transfer-replication` merged **2026-10-01T03:44:25Z** without squash or rebase, so commit
  **P = `06f8d55`** is an ancestor of upstream `main`; the clone is on `main` at `0d27c68` and contains it. This
  retires `docs/drafts/README.md`'s "commit P is not yet merged" and unblocks the staged 0045/0046 and the R12
  recompute. **Being an ancestor is not the same as satisfying the pin** — see *Invariants*.
  re-verify: `git -C ../kv-transfer-replication merge-base --is-ancestor 06f8d55592570deae70c3feb9f84a75c4044fb03 HEAD; echo $?` → `0`.
- **built — the e9f mirror is complete locally.** `C:\m\e9f` holds **1,054** files, 52 GiB, matching the Hub
  dataset's 1,054 exactly. This is a **file-count** match; the hash verification needs a read token and has **not**
  been run for e9f.
  re-verify: `find /c/m/e9f -type f -not -path "*/.cache/*" | wc -l` → `1054`, against `curl -s "https://huggingface.co/api/datasets/emmmy/linear-ceiling-e9f-2026-09-19?full=true" | grep -o '"rfilename"' | wc -l` → `1054`.
- **built — two learnings entries** (uncommitted): the hardlinked R8 stage that silently diverged from its published
  dataset, and the configuration share's near-invariance to mean-vs-median.
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings 2>&1 | grep -c "LEARNINGS FAIL"` → 7, all pre-existing, none naming a 2026-10-01 entry.
- **in progress — NOT this session's: the Carryover session's close**, committed at `bf75008`: `e9_tail` run on all
  three Qwen cells (16/16 figures reproduced), the Llama R8 verification, eight learnings entries, and a
  corrective-entry draft that **proposes taking number 0045**. That proposal collides with the staged Llama drafts
  and is ruling 11 of the run queue.
  re-verify: `ls docs/learnings/ | grep -c "^2026-10-01"` → 11 (8 theirs, 3 mine), and `git show --stat --oneline bf75008 | head -3`.
- **planned — not started here:** every GPU row (tasks A–E) — all blocked on rulings; the `sender_head_truncate`
  config key and E-TRUNC's paired reader; E-TAIL Part B's chunked hook and its probe; E-BEH's injection splice.
- **not started, and flagged rather than done:** unlinking or deleting the two mutated R8 staging trees; amending
  the refresh brief's rotted line (briefs are immutable, so that is a correction in a *new* brief — this one).

## Locked decisions

- **No box was launched, no entry appended, no git history written by this session.** Reason: the 10-01 seed
  authorized preparation only and the operator rules on launches; the global rule is that history is the operator's.
  Commit blocks were emitted instead, and the operator ran them.
- **`git fetch` was run; nothing else that writes.** Reason: the seed's §0 recovery action asks for it and drift
  detection needs it. A fetch updates remote refs only and writes no history. Disclosed at the time.
- **Prices and limits re-fetched live rather than copied from the runbook.** Reason: the seed required it, and the
  answer matters — it confirmed $3.00/h and $0.090/GB rather than assuming them.
- **Spot is not recommended for these sittings.** Reason: 12–24 % off ($2.29–2.65 observed) against an interruption
  that costs a restart under R4 and a partial close; the two completed sittings were ~$11 and ~$7 on demand.
- **The two mutated R8 stages must NOT be re-pushed.** Reason: the Hub still holds the exact bytes entries 0036 and
  0038 cite, and no value changed — only an added `dump_rope` key. Re-pushing would make the published datasets
  diverge from what the ledger cites, which is strictly worse than a stale stage.
- **A design doc's figures are corrected in the brief, not in the design.** Reason: the seed forbade editing the
  three designs; `e-trunc-design.md`'s "18 over 49,152" (actually **19**) is recorded in the run queue and the
  refresh brief for the operator to fix before registration.
- **The registered second family is 3.2-3B → 3.1-8B, and a 1B→3B pair is a separate optional proposal.** Reason:
  `pairs.py:93` carries exactly one Llama entry; the 3B→8B short cohort already ran (0044) and could not have run
  smaller (8B fp32 OOMs at T = 32,768 on 44.43 GiB). A 1B→3B pair would fit 48 GB but is a new pair needing its own
  E8 fit, τ and registration — and its matched-KV status is **unverified** (the 1B is gated, 401).

## Reuse map

- `docs/2026-10-01-run-queue-farhan.md` — the co-author-facing ask. Edit a copy for another audience, not this file.
- `docs/2026-10-01-mlsys-box-plan.md` — the operator-facing costing of the same rows.
- `tools/ec2/` — the AWS sitting, parameterized by `EXP`. **`probe_e9l.py` is already generalised** (`EXP`,
  `MAX_S`, `LADDER`, and a native-RoPE path for a config with no `[e9.rope]`), so no sibling is needed to size a
  prefill; one is still needed for an eager-attention hook.
- `tools/runpod/rp.py` — the container-host path; its header is the authority on what containers change.
- `tools/preflight_pair.py` — CPU-only, network-free, weights-free pair go/no-go (pair resolution, provenance,
  matched-KV with both declared and derived head dim, vocab equality). The right first move on any proposed pair.
- `tools/hf_verify_backup.py <repo_id> <local_root>` — two-way R8 verification; exit 0 only when every file matches
  both directions.
- `src/linear_ceiling/e9_tail.py` (`0a51275`, the Carryover session's) — the Part A reader; outputs
  `results/*/tail.json`. Read figures from it, don't recompute them by hand.
- `src/linear_ceiling/e7_stats.py` — the one pinned quantile convention. Use it for any percentile check.

## Invariants

- `results/`, `data/`, `traces/` never enter git history. Entries 0025–0044 are immutable; a correction is a new
  numbered entry. **`docs/drafts/README.md` is the only number allocator**, and `append_0039.py` on main carries an
  already-taken number — never run it.
- No figure reaches the ledger or the paper except from a fail-closed reader run in-process (R11). Registration
  precedes the run (R1): the entry and its thresholds land before any prefill.
- **An ancestor pin is not a satisfied pin.** The clone sitting on `main` at `0d27c68` contains P but still fails
  every cell's gate, which checks the invoked paths unchanged *and* clean; detach at the cell's pin, run, return.
  There is no upstream-path override, so **one clone means one cell at a time** — a worktree does not help.
- **Never hardlink a results tree into a staging dir and then run a reader.** `summarize_e9` writes in place, so the
  stage mutates with the live tree and the published dataset silently falls out of date; and a stage-vs-live diff
  cannot detect it, because both paths are one inode. Verify against the published bytes.
- Before any sitting, extend `release_sweep.sh`'s `OURS_FILES` (`:7`) for every new file the box will hold, or the
  sweep reports `NOT OURS` and `foreign=1` on a clean box.
- Run `summarize_e9 --calibrate-tau` at home **before** the GPU run: the gate does not check for
  `results/<exp>/calibration/tau.json` and the summarizer refuses without it.
- A registered absolute band on the seam-bin figures must name **mean or median** — the levels differ by ~1.7×.
- Git history is the operator's; stage explicit paths, never another session's files; no attribution trailers.
- `git clean -x`/`-X` deletes the gitignored `results/` tree that nearly every re-verify line above reads from.

## Open / next

1. **Commit this session's close** (operator), explicit paths only — not `docs/paper/tex/`:
   `git add docs/handoff/2026-10-01-aws-lane-refreshed-run-queue-handed-to-a-co-author-and-a-mutated-r8-stage.md docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-10-01-a-hardlinked-r8-stage-keeps-mutating-with-the-live-tree-so-a-later-reader-silently-diverges-it-from-the-published-dataset.md docs/learnings/2026-10-01-the-configuration-share-is-near-invariant-to-mean-vs-median-even-though-the-levels-it-is-built-from-differ-by-1-7x.md`
2. **Answer the 11 rulings** in `docs/2026-10-01-run-queue-farhan.md` §10. **Ruling 11 blocks two files** and is the
   one to take first: if the corrective entry takes 0045, the staged Llama drafts move to 0046/0047, which means
   every `NUM`/`PREV` literal in both scripts **and** `config/e9fl.toml`'s `[e9.gate] required_entries` (currently
   `"0045"`) change in one commit, and that commit must precede any `e9 --check`. Rulings 1–3 unblock task A,
   the only GPU row plausibly entered by Oct 30.
3. **Unlink or delete the two R8 staging trees** (`~/dev/hf-staging/linear-ceiling-e9{l,s}-*`) so a later reader
   cannot mutate published evidence again. Do not re-push.
4. **Carried, not closed:** the HF write-token revocation (R9, unverified since 09-14); the two empty
   `hossainpazooki` e8f/e9f datasets to delete; `docs/drafts/README.md`'s staging list stale by two (0043/0044 are
   appended); `e-trunc-design.md`'s 18 → 19; Condition 1's admission outcome, which keeps the Qwen3 short cell out
   of every registered verdict.
5. **Housekeeping, harmless:** key pair `lc-e9l-2026-09-10` and `sg-03021d0b6c09b4c75` (`lc-e9l-ssh`) still exist in
   us-east-1; both free, both the operator's call.
