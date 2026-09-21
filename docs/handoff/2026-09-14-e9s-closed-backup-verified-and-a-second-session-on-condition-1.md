# Handoff — E9 scaled short cell closed: backup verified, result note on main; a second session is preparing condition 1 in the same tree

2026-09-14 09:20Z (session `e9l-aws-run`; transcript `C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl`).
Newest commit this brief describes: linear-ceiling **`a5053b2`** = the tracking ref of origin/main (0 ahead / 0 behind, read
from the local ref at 09:19Z, not fetched). Uncommitted from this session: this brief, its index row, two learnings entries
and their index rows. Uncommitted and NOT this session's: the condition-1 preparation listed under *Current state*.
Supersedes the 03:45Z brief `2026-09-14-e9s-sitting-run-read-and-entered-backup-staged.md` on the backup (then staged, now
verified); every other claim there still stands and is not repeated here.

## Current state

- **built — the sitting is closed.** Rented g6e.4xlarge `i-03c1b238426ff218c`, driver 02:26:08Z → EXIT=0 02:56Z, 25/25;
  terminated 03:09:57Z. Full log with every hash: `docs/2026-09-13-e9s-gpu-runbook.md` §6.
  re-verify: `cat results/e9s/logs/box/e9s.rc` → `EXIT=0`; `grep -ac '^\[[0-9]*/25\]' results/e9s/logs/box/e9s.log` → 25.
- **built — entry 0038 on main** (`44468ab`; chain `c9128ee936cd`): descriptive, no `verdict:` line; configuration share
  0.4285 (16+ seam median δ_K), 0.3916 (τ = 0.03), τ = 0.1 share 0 by construction; states the post-run τ calibration
  and the `results/e9s/scratch/` path.
  re-verify: `grep -n "^### 0038 " ledger/ledger.md` → line 2310; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`.
- **built — the readers' outputs at home** (gitignored): `results/e9s/summary.json` sha256 `2f562aca…`, `compare.json`
  `a0699a82…` as written by the append script's in-process run. A standalone `e9_compare` writes a different hash with the
  same figures (learnings entry below), so do not re-run it to "check" by hash.
  re-verify: `sha256sum results/e9s/summary.json results/e9s/compare.json` → `2f562aca…`, `a0699a82…`.
- **built — R8 backup VERIFIED** 04:04:21Z by the operator's `ALLOW_PUBLIC=1 tools/hf_backup.sh`: dataset
  `hossainpazooki/linear-ceiling-e9s-2026-09-13` (public, revision `a63e3c27`), 983 remote = 983 local, 821 by LFS sha256,
  162 downloaded and hashed, 0 problems. README dataset table carries it (`01e65c7`).
  re-verify: `grep -a "BACKUP VERIFIED:" ~/dev/hf-staging/logs/linear-ceiling-e9s-2026-09-13.20260914T034942Z.push.log` → one line at 04:04:21Z;
  full re-check needs a read token: `.venv/Scripts/python.exe tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9s-2026-09-13 ~/dev/hf-staging/linear-ceiling-e9s-2026-09-13`.
- **built — result note for an out-of-loop co-author read** `docs/2026-09-14-e9s-result-note.md` (`a5053b2`): no names, no PR
  references; the share table, the paper reading, what to read, the fallback.
  re-verify: `git log --oneline -1 -- docs/2026-09-14-e9s-result-note.md` → `a5053b2`.
- **built — learnings** (this session, 2026-09-14): the gate never checks the cell's τ calibration (`282542a`); the zero-hit
  `xargs grep` count that kills a `pipefail` script; the path-dependent `compare.json` hash (the last two uncommitted).
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings 2>&1 | grep -c "LEARNINGS FAIL"` → 7, all pre-existing (09-02/09-04), none naming a 2026-09-14 entry.
- **in progress — NOT this session's: condition-1 preparation.** Untracked `docs/2026-09-14-condition-1-board-source.md`,
  `docs/2026-09-14-condition-1-status.md`, `docs/2026-09-14-seed-condition-1.md`, `docs/reviews/2026-09-14-refutation-0025-0029.md`,
  `docs/drafts/append_0039.py`, `docs/drafts/test_append_0039.py`, and a modified `docs/drafts/README.md` that allocates
  **0039** (Path B admission ruling; `--append --operator NAME` reserved to the operator). This session did not read, run or
  edit any of it beyond the drafts README's current-state paragraph.
  re-verify: `git status --short` lists exactly those six untracked paths plus `M docs/drafts/README.md` (and `.claude/`, `docs/paper/tex/`).
- **planned — not started here:** the §4.2 / §5.2 sentence per length descriptive from 0038 (paper author); the out-of-loop
  read of 0038 and `compare.md` (co-author, before 11:59Z).

## Locked decisions

- **D1–D4 (operator, 2026-09-13):** keep = 0025's eight; cross arm kept; rented EC2 L40S instead of the Algoverse slice;
  the (p, p) twin read of the kept eight not registered. Reason: the Algoverse queue could not meet the 09-14 11:59Z
  deadline and a rented card reproduced the 09-10 stack exactly (probe rows identical). Recorded in the runbook header.
- **The τ calibration written after the GPU run stands; no re-run of the cell.** Reason: `calibrate_tau` reads only the
  upstream mapper, archived generic dumps, archived `r2.json` and E8's report, and the summarizer refuses unless it equals
  the committed τ; τ came out identical to E9-long's at the same pin. Stated in 0038.
- **The configuration share is reported as values, not classified.** Reason: 0037 fixed "near 1 / near 0 / in between" and
  registered no threshold for "near". The τ = 0.1 share is stated as 0 by construction because both short medians are 0.
- **The backup dataset is public.** Reason: operator ruling 2026-09-11 (protocol R8), and the private tier had already
  stopped E9-long's push; the push ran from the staging tree only, after a credential sweep with a firing control.
- **0038's draft script was retired without ever entering history.** Reason: the drafts convention deletes a script once
  appended, and `append_0038.py` was written, run and deleted between commits; the entry text is the record, and its shape
  follows `git show cb9ae54^:docs/drafts/append_0036.py`.

## Reuse map

- `tools/ec2/` — the whole sitting, parameterized by `EXP` (`setup.sh`, `run.sh`, `probe_e9l.py`, `release_sweep.sh`,
  `pull.py`, `verify_mirror.py`, `box.sh`); `tools/ec2/README.md` now starts with `--calibrate-tau` at home and ends with the
  release-sweep line.
- `tools/hf_backup.sh` + `tools/hf_verify_backup.py` — push and two-way verification; the stage recipe (hardlink
  `results/<exp>/` + `mappers/<pair>/k1.*`, card copied) is written out in the runbook §6 staging line.
- `docs/2026-09-13-e9s-gpu-runbook.md` §6 — the template for the next sitting's log, including the refusal and deviation form.
- `linear_ceiling.e9_compare` — the only reader of the native-vs-scaled comparison; `results/e9s/compare.md` is its render.
- `docs/2026-09-14-e9s-result-note.md` — the shareable summary; edit a copy, not the committed file, for other audiences.

## Invariants

- `results/`, `data/`, `traces/` never enter git history; `results/e9/`, `results/e9l/` untouched; `results/e9s/` written only by
  the driver, the puller, `summarize_e9` (incl. `--calibrate-tau`), `e9_compare` and the append script.
- Entries 0025–0038 are immutable; a correction is a new numbered entry. No figure enters the ledger or the paper that a
  fail-closed reader did not produce in-process.
- The drafts README is the only number allocator: 0039 is already allocated there by the other session. Do not stage a
  script under 0039, and do not run `append_0039.py` (operator only).
- Never run a summarizer, `e9_compare` or an append while a hardlinked stage of that results dir is uploading: they rewrite
  files in place under the uploader.
- Git history is the operator's; stage explicit paths only, never the other session's untracked files; no attribution trailers.
- `git clean -x`/`-X` deletes the gitignored `results/` tree the backups were verified against.

## Open / next

1. **Commit this session's close** (operator), explicit paths only:
   `git add docs/handoff/2026-09-14-e9s-closed-backup-verified-and-a-second-session-on-condition-1.md docs/handoff/HANDOFF.md docs/learnings/LEARNINGS.md docs/learnings/2026-09-14-a-counted-xargs-grep-under-pipefail-kills-the-script-on-the-clean-outcome-and-a-piped-tail-hides-it.md docs/learnings/2026-09-14-e9-compare-json-hash-depends-on-how-the-long-summary-path-was-spelled.md`.
   Not `docs/drafts/README.md`: its uncommitted change is the condition-1 session's.
2. **Revoke the HF write token** used for the push (R9). Not verified by this session.
3. **Paper:** §5.2 of `docs/paper/2026-09-11-lcfm-outline-v3.md` (lines ~171–190) still says the length reading waits on the
   scaled short cell; rewrite from 0038 only. Blocker: the out-of-loop read before 11:59Z, else the fallback (0029 + 0036 with
   the configuration difference as a limitation).
4. Carried, not this session's: the corrective f* entry (README's H-E9 row still reads "f* = 0 at every matched token");
   condition 1, now with the other session's staged 0039.
5. Housekeeping, harmless: key pair `lc-e9l-2026-09-10` and security group `sg-03021d0b6c09b4c75` still exist in us-east-1; the
   stopped t3.micro `eks-instance` (`i-0785c090815238989`) is not this project's.
