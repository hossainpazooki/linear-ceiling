# Handoff — ruling (b) executed on a detached upstream; the n = 420 sitting closed end to end

2026-09-09 04:30Z (session `878feb6f`, the same session as `2026-09-09-n420-dump-fit-0033-0034-landed.md`, which this
brief supersedes for "Open / next" only). Newest commit this brief describes: linear-ceiling `4eafe40` = origin/main as
of 03:51Z, plus the uncommitted work in the commit block below. Upstream `kv-transfer-replication` on `main` at
`4633718` = origin, tree clean except the untracked `results/mapper/qwen3-0.6b-to-1.7b/n420/` (ours, the fit's record).
The Algoverse grant (`rrhs-66f0`) expires 2026-09-09 07:30Z; it is a shared login and we are off it.

## Current state

- **built / verified — ruling (b) executed.** Operator ruled "detached" at ≈ 04:04Z. Upstream checked out at `d5786df`
  (E9's pin), `summarize_e9` ran clean at home 04:05:41Z–04:12:26Z (no refusal; rule line `-> HOLDS`; keep subset
  recomputed from tensors under 0028's tolerance), upstream restored to `main`. No entry appended: nothing on the record
  changes; this is the passing run 0032 requires for E9's admission to the 4-pager.
  re-verify: `head -c 400 results/e9/logs/summarize_e9.2026-09-09T0405Z.detached-d5786df.log` (mirror only) and
  `ls -la results/e9/summary.json` (mtime 2026-09-09 00:12 local = 04:12Z); `git -C ../kv-transfer-replication log --oneline -1` → `4633718`.
- **built / verified — the summarizer still refuses at upstream HEAD, by design.**
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9` → `E9 SUMMARY REFUSED: ... changed between the pin d5786df91f55 and HEAD`.
  This is the pin gap (0030's `223f469` touched `scripts/score_mapper.py` and `kvt/pertoken.py`), not the data; any later
  upstream commit widens it, so the detached checkout is the durable way to re-run E9's summarizer.
- **built / verified — 0033 and 0034 on the ledger** (0033 at `88d7476`, 0034 at `257988c`).
  re-verify: `grep -n "^### 003[34]" ledger/ledger.md`; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`.
- **built / verified — both entry-0033 gates ready on `main` after the restore.**
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8c.toml` → `E8 gate: ready`;
  `.venv/Scripts/python.exe -m linear_ceiling.e9_rescore check --config config/e9c.toml` → `E9 rescore ready`.
- **built / verified — R8 backup** `hossainpazooki/linear-ceiling-n420-2026-09-08` @ `8675b719`, 89 files / 27.7 GB,
  89/89 verified from the Hub's `lfs.sha256` plus re-download of the 28 non-LFS files (operator's shell, scoped token,
  revoked).
  re-verify: with a read token in `$HF_TOKEN` and the mirror reconstructed, `tools/hf_verify_backup.py <repo> <dir> --exclude README.md` → `BACKUP VERIFIED`.
- **built — outline updated:** §3.5 header now "freeze run PASSED 2026-09-09; PENDING co-author review" with a dated
  status paragraph; §5.1 [FROZEN] on 0033/0034.
  re-verify: `grep -n "freeze run PASSED\|FROZEN\]: the k = 1/4/8" docs/paper/2026-09-06-lcfm-outline.md`.
- **built — six learnings entries** from this sitting's captured bases (cu128 index ceiling; chained launch holds the
  kernel pipe; two upload streams reset together; box venv needs PYTHONPATH; e8c arm (a) loads the whole pair; `hf.exe`
  globs `--include`), plus the earlier shared-login entry.
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings` → 7 FAILs, all pre-existing (dated 2026-09-02/04), none dated 09-08/09.
- **not started — co-author refutation of 0025–0029** (their audit was running on the shared box; see the incident in
  the previous brief). **not started — E9-long seed D1–D5** (the seed session's; measured: 1.7B OOMs at T = 40,960 on
  1g.20gb, so every option needs 3g.40gb or a full card).

## Locked decisions

- **Ruling (b) = detached checkout, not a re-pin entry.** Reason: a re-pin to `223f469` would be refused again by the
  next upstream commit (the seed's YaRN change touches `kvt/models.py` and `dump_kv.py`, both on E9's invoked list),
  and each re-pin needs its own measurement; a detached run changes nothing on the record and works forever.
- **The upstream is restored to `main` after every detached run.** Reason: the E8-family gates pin `223f469` by ancestry
  and refuse on a detached older HEAD (verified: e8c gate ready again after the restore).
- **Ruling (a) = re-dump** (taken by requesting the box on 09-08); premise held; the two halves' provenance is stated in 0033.
- **0034's header date = the run date** (2026-09-08 local), precedent 0020/0029/0031.
- **The Algoverse box is not touched again this grant.** Reason: it is a shared login with a co-author's audit on it;
  protocol R7 step 0 (2026-09-09) says abort on anything foreign.

## Reuse map

- `docs/2026-09-08-n420-target-dump-runbook.md` — §§1–7: request, box facts, R2 probes, dump, fit on the box, home
  chain, incident, backup, ruling (b). Every timestamp and command of the sitting.
- `docs/gpu-experiment-protocol.md` — "Quick reference — HF backups and tokens (team)" at the top; R7 step 0.
- `tools/hf_verify_backup.py` — HF dataset vs local mirror, both directions, `lfs.sha256` + re-download of non-LFS.
- `tools/jupyterhub/` + the mirror's `box-logs-2026-09-08/` (`push_dumps.py` one stream / 32 MB parts / `Connection: close`;
  `pull_fit.py`; `fit.sh` — needs `export PYTHONPATH=$PWD` on the box).
- `docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.{py,out}` — the seed's request numbers.
- `results/e8c/summary.md`, `results/e9c/summary.md`, `results/e9/summary.md` — 0034's tables and the passing E9 run; local by rule.

## Invariants

- `results/`, `data/`, `traces/` never enter history; `results/e8/`, `results/e9/` records never rewritten (the 09-09
  summarizer run rewrote only `results/e9/summary.*`, which are regenerable summarizer outputs, and kept its log under `results/e9/logs/`).
- Entries 0025–0034 immutable; no number enters the ledger or the 4-pager that a summarizer did not produce.
- Upstream read-only: its gitignored `data/`, `mappers/`, `results/` are the home mirror; a detached checkout for a
  summarizer run is the one sanctioned working-tree change, and `main` comes back after.
- Tokens: scoped, expiring, env-only, revoked once used or pasted. The grant password is in the email and in this
  session's transcript; the grant expires 07:30Z.

## Open / next

1. **Operator:** the commit block in the session log (learnings ×6 + index, runbook §7, outline, this brief + HANDOFF row);
   tell the co-author about the 00:40Z stop and that `summarize_e9` needs the upstream at `d5786df` (detached) to run.
2. **Co-author refutation of 0025–0029** — the last inclusion condition on §3.5; not ours to do.
3. **E9-long** — the seed session's D1–D5 and build; its YaRN commit is now free to land (the 0033 chain no longer needs
   `223f469`'s invoked paths unchanged), but E9's own summarizer will keep needing the detached checkout.
4. 4-pager → PI review. `check-learnings` red on the same 7 pre-existing entries.
