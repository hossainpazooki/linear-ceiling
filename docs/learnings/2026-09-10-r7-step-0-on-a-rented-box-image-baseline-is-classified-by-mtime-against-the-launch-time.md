# R7 step 0 on a rented single-tenant box: an allowlist written for a hub login aborts on the image's own files; classify by mtime against the launch time, and the abort is the checklist working

kills: (nothing)
ts: 2026-09-10T01:21:00Z
commit: 3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806
session: linear-ceiling-e9l-box (018fwd195AS7uS2tvJdgSoYP)
status: verified
fact: Protocol R7 step 0 (2026-09-09, after the shared-login incident) says list `~` and the processes before any
deletion and abort on anything not ours. On the AWS Deep Learning AMI the first pass of `release_sweep.sh`
aborted (rc 11, nothing deleted) on ten entries its allowlist did not name: `.aws`, `.gnupg`, `.nv`, `.zshrc`,
four license files, `gds-nvidia-fs`, `nvidia-acknowledgements`. Read-only inspection showed every one is either
the image's baseline (mtime 2026-09-07 05:45–06:50, the AMI build; `.aws` holds only the CLI's `cli/` cache,
no `credentials`; `.gnupg` is the image keyring) or created by our own tooling after launch (`.nv` = CUDA's
kernel cache from the R2 probe; `.zshrc` = the uv installer's one-line hook). The single-tenant rule that
survives: anything with mtime before the instance launch is image baseline (listed for the record), anything
newer must be on the run's own list; the sweep also now searches `~/.aws` for key material. The second pass
tripped on the sweep's own redirected log; the third passed. Three aborts before one deletion is the intended
shape, and each was resolved by inspection, never by loosening the abort.
basis: runbook `docs/2026-09-10-e9l-gpu-runbook.md` §6 entries 01:3x (first pass: `NOT OURS` × 10, `ABORT: foreign
  presence; nothing deleted`, rc 11) and 01:21:45; the pulled `results/e9l/logs/box/release.log` (third pass) lists
  13 `image baseline (mtime before 2026-09-09 23:40)` entries and no `NOT OURS`; the read-only listing of `~/.aws`
  (`cli/` only) and `~/.gnupg` (Sep 7) is in the session transcript and the runbook entry.
re-verify: grep -c "image baseline" results/e9l/logs/box/release.log; grep -c "NOT OURS" results/e9l/logs/box/release.log   # 1 and 0 on the pass that deleted the HF cache
