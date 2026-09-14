# E9 scaled short cell (e9s) GPU runbook — one rented L40S, one short sitting

**Date:** written 2026-09-13 · **Status:** runbook; §6 is filled during the sitting in UTC. Inherits
`docs/gpu-experiment-protocol.md` R1–R12 without restating them, and `docs/2026-09-10-e9l-gpu-runbook.md`'s shape.
The experiment is entry **0037** (registered before any prefill, 2026-09-13; `config/e9s.toml`; seed
`docs/2026-09-13-seed-e9-scaled-short-cell.md`): 0029's 25 handoffs under 0036's receiver configuration, descriptive,
no verdict. Its figures enter by their own entry from `summarize_e9 --config config/e9s.toml` and `e9_compare`.
Rulings (operator, 2026-09-13): D1 keep = 0025's eight; D2 cross arm kept; D3 rented EC2 L40S; D4 twin read not registered.

## 1. The box

Same as the 09-10 sitting (`docs/2026-09-10-e9l-gpu-runbook.md` §1): g6e.4xlarge (1 × L40S 48 GB), AMI
`ami-0eb7d782cce2fe526`, key pair `lc-e9l-2026-09-10` (still in the account, private key at home), security group
`sg-03021d0b6c09b4c75` (port 22 from the home IP, re-checked 2026-09-13), 250 GB gp3 root deleted on termination,
shutdown behaviour `stop`, 24 h self-halt armed by `setup.sh`, $3.00/h + $0.09/GB egress. Stack pinned as before:
Python 3.12 (uv), torch 2.11.0+cu128, transformers 5.15.1, numpy 2.5.2. Instance id, IP and launch time in §6.
The scripts are `tools/ec2/` with `EXP=e9s` (parameterized 2026-09-13; defaults reproduce the 09-10 sitting).

## 2. R2 — the measured budget

Prior: 1.7B under YaRN 2.5 at T = 32,768 measured **16.70 GiB** on an L40S (09-10 probe) and 16.72 GiB natively on
an H100 1g.20gb slice (09-08 ladder); 0.6B 10.89 GiB. The longest included |S| is 32,123. `probe_e9l.py` with
`EXP=e9s` runs the pinned scaled forward at T = 32,768 for both models on the granted card before launch; the row
goes into §6. Stop if either row is not `ok`.

## 3. R3 — everything the run reads, by sha

| artifact | where | sha256 / pin |
|---|---|---|
| linear-ceiling checkout on the box | `~/linear-ceiling`, detached | **the commit carrying entry 0037** (`LC_SHA`, filled in §6 at launch) |
| upstream checkout on the box | `~/kv-transfer-replication`, detached | `063f4023fdde67dedbee01a92518ce7f83f6cf5d` (= `config/e9s.toml` `upstream_sha`, 0036's pin) |
| `config/e9s.toml` | committed at `9a7816d` | text sha `1842be5b493f506721242dd24572f870384f626351707576b8642c49c8e325d9` |
| `config/e9.toml` (the native cell `e9_compare` reads) | committed, unchanged since 0029 | text sha `4ba4a86733d74e03b5b271b85039ab0e04d73c6bef4b1c49b01fe8438e49bc8f` |
| `config/e7-manifest.json` | committed | `e7_manifest check` at home 2026-09-13 → `manifest ok: 188 files match disk; sha256 371fb4bf3cb089bd…` |
| traces | `~/linear-ceiling/traces/` from the home tarball (16,637,313 B; 145 MB raw) | checked on the box by `e7_manifest check` in `setup.sh` |
| mapper (gitignored, 0029's n = 50 k = 1) | `~/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.json` / `k1.safetensors` | `2fd05c333156607436af128ccd7a009f175f13138d27e4126588c24f515cc86e` / `cd6a8d939b36db901f50e13bae446aef833f5d2ea7276658f499e993e63607f2` (`sha256sum -c` in `setup.sh`) |
| alignment / coverage at home | `results/e9s/align/coverage.json` | `c371185c7e06…` as 0037 cites (home bytes, CRLF); LF-normalized `a956acf0d4d7…`, which is what the box's own `--align-only` should print |
| box scripts | `~/setup.sh`, `~/run.sh`, `~/probe_e9l.py`, `~/release_sweep.sh` = `tools/ec2/*` at the commit above | pulled back into `results/e9s/logs/box/` each round |
| models | `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-0.6B`, public, no token | HF cache on the box, removed at release |

What the box must print: no `[bridge]` lines (0037 registers no bridge), then `[i/25] <hid>: same K …` in the
registered order `n_sender_asc` (`astropy__astropy-7336_traj#26` first, |S| 8,213; `astropy__astropy-14539_traj#96`
last, 32,123). Coverage the figures entry states: 68 observed · 25 included · 43 excluded, 0029's reasons. Kept
dumps: 0025's eight (three stride-1 dumps each, ≈ 45 GB pulled).

## 4. Steps

1. **Home, before anything:** the ledger commit carrying 0037 is pushed (the box clones from GitHub); record its sha
   as `LC_SHA` in §6. `tar -czf <scratch>/traces.tar.gz traces` exists from 09-10 (same bytes: manifest unchanged).
2. `LC_NAME=lc-e9s-2026-09-13 tools/ec2/box.sh up`; upload the mapper pair, the tarball and the four box scripts (LF).
3. **`setup.sh` detached** with `env EXP=e9s LC_SHA=<sha> HOME_COVERAGE_SHA12=a956acf0d4d7`; poll `~/setup.rc`. It ends
   with `E9 gate: ready (entries 0019/0023/0025/0027/0035/0037 committed; upstream pinned and clean; config/e9s.toml)`
   from a fresh clone — R1's fresh-clone gate — the alignment sha and the versions. Stop on any refusal.
4. **R2 probe** `EXP=e9s probe_e9l.py` → `~/probe.log`; both rows into §6.
5. **`EXP=e9s bash ~/run.sh`** (R4). Record the launch time.
6. **`BOX=… pull.py e9s` at home** (hidden process): kept handoffs verified then deleted on the box; small records and
   box logs every round.
7. **Cutoff:** none planned (≈ 1 h). `e9 --close-partial --config config/e9s.toml` only on a stated reason that does not
   depend on any score; `e9_compare` refuses a partial run, so a partial close ends this cell's comparison.
8. **Release (R7)** in order, step 0 first (`EXP=e9s release_sweep.sh`), then `box.sh terminate` and the durable
   read-back (`--filters Name=instance-id … --query 'length(Reservations)'` → 0).
9. **Backup (R8)** from the verified home mirror: `verify_mirror.py e9s`, stage by hardlink, `ALLOW_PUBLIC=1
   tools/hf_backup.sh hossainpazooki/linear-ceiling-e9s-2026-09-13 <staging>`, then `tools/hf_verify_backup.py`.
   Do not run a summarizer while the hardlinked stage is uploading. Tokens R9.
10. **Home readers, in order:** `summarize_e9 --config config/e9s.toml` (≈ 9 min), then
    `e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json`, then the figures entry
    by its own script. A refusal is pasted verbatim into the closing brief.

## 5. Traps carried

From 09-10: `python -u` in the launcher (a buffered log shows nothing until exit); liveness from `~/e9s.rc` and
`report.json`, never the log; strip CRLF before `put`; the sweep's step 0 classifies by mtime against launch; the
token `read -s` runs alone, then `hf auth whoami`; the push needs several 128-commits-per-hour windows; a hardlinked
staging tree is live under the uploader. New here: `setup.sh` clones at `LC_SHA`, which must already be on GitHub.

## 6. Log (UTC; filled during the sitting)

- 2026-09-14 ~02:13Z home: 0037 committed as `c360950`, tooling as `83419c8`, PR #4 (`ffef90a`: f* input validation in
  `e9_pertoken.py`, evidence path, CI green) merged in; pushed tip **`12c113c2f9b0e32e6e74e340e266ff9e2a5f5acd` = `LC_SHA`**.
  Home gate: `E9 gate: ready (entries 0019/0023/0025/0027/0035/0037 committed; upstream pinned and clean; config/e9s.toml)`;
  suite 436 passed, 1 skipped; `ledger ok`. `summarize_e9 --config config/e9l.toml` re-run on the merged tree as the check
  that PR #4's validation is silent on real per-token data (result below).
- 02:16:16 `LC_NAME=lc-e9s-2026-09-13 box.sh up`: us-east-1b refused (InsufficientInstanceCapacity), us-east-1c took it.
  Instance **`i-03c1b238426ff218c`**, g6e.4xlarge, public IP 13.218.117.252, ssh up on the third try. Key pair and
  security group reused from 09-10.
- 02:17 uploads by `box.sh put`, box-side sha256: `setup.sh 294f0893…`, `run.sh a373ffce…`, `probe_e9l.py ed23d353…`,
  `release_sweep.sh 072f8b0e…`, `traces.tar.gz ba9d43ab…` (= 09-10's tarball), `k1.json 2fd05c33…`, `k1.safetensors cd6a8d93…`
  (= R3). Card `NVIDIA L40S, 46068 MiB, driver 595.91.07`.
- 02:17:43 `setup.sh` launched detached with `EXP=e9s LC_SHA=12c113c… HOME_COVERAGE_SHA12=a956acf0d4d7`; exit code to `~/setup.rc`.
- 02:18:57 `setup.sh` **EXIT=0** (74 s): clones detached at `12c113c` / `063f402`; mapper `k1.json` OK, `k1.safetensors` OK;
  manifest ok; **`E9 gate: ready (entries 0019/0023/0025/0027/0035/0037 committed; upstream pinned and clean; config/e9s.toml)`
  from a fresh clone (R1)**; the box's `--align-only` wrote `results/e9s/align/coverage.json` sha256
  `a956acf0d4d7938f0b796d2570d665098ca0ea25f8c9786993903b8229562182` = home's LF-normalized value (0037 cites the CRLF home
  bytes, `c371185c7e06…`; same content). 24 h self-halt armed.
- 02:19:22 **R2 probe** (`EXP=e9s probe_e9l.py`, pinned `load_model(rope_scaling=[e9.rope])`, fp32, `sdpa_repeat_kv`,
  `logits_to_keep=1`; EXIT=0; card 44.39 GiB): 1.7B weights 6.41 GiB, **T = 32,768 peak 16.70 GiB** (7.3 s forward);
  0.6B weights 2.23 GiB, peak 10.89 GiB (4.8 s). Identical to the 09-10 rows; ~27 GiB of headroom on this card, ~3 GiB
  on a 1g.20gb slice.
- 02:2x home: **PR #4 check PASSED** — `summarize_e9 --config config/e9l.toml` on the merged tree `12c113c` (log
  `results/e9l/logs/summarize_e9.*.merged-12c113c.log`): rc 0, no refusal, 35 of 35, bridge CARRIED, rule line `-> HOLDS`,
  verdict-bearing median f*(τ_K) 0.0000 — identical to 09-10, so the new f* input validation never fires on real
  per-token data.
- **02:26:08 `EXP=e9s run.sh`: driver launched detached** (`e9 --config config/e9s.toml`, `python -u`, pid 5757; log `~/e9s.log`,
  exit code to `~/e9s.rc`). `--launched 2026-09-14T02:26:08Z` for the figures entry. 02:26:28Z home puller `pull.py e9s`
  started hidden (pid 44048; log `results/e9s/logs/pull.log`).
- **02:56 driver EXIT=0** (`~/e9s.rc`; ≈ 30 min): 25 `[i/25]` lines in registered order (`[1/25] …astropy-7336_traj#26: same K
  0.9559 in 104s` … `[25/25] …astropy-14539_traj#96: same K 0.9247 in 92s`), no Traceback, no `[bridge]` line; box
  `report.json` `complete True`, 25 scored, no partial, no bridge. No cutoff used.
- 02:59:21 puller: `scored 25/25 … complete=True` then `run complete and every kept directory is home; final mirror done;
  report.json sha256 abd1e456196692966043b542573599b7c7b8823fbb9f83dfa72e18279311ca55`. The eight kept handoffs were each
  verified file by file against `report.json` and deleted on the box (R5).
- **03:02:56 R7 sweep** (`EXP=e9s LAUNCH_UTC="2026-09-14 02:10" release_sweep.sh`, SWEEP_RC=0; log pulled as
  `results/e9s/logs/box/release.log`, sha256 `6dc0e157…`): step 0 image baseline = the AMI's 09-07 license files, `.aws`,
  `.gnupg`, `gds-nvidia-fs`, `nvidia-acknowledgements`; nothing NOT OURS; driver not running. Step 2: 0 `layer*.npz` left.
  Step 3 box hashes `setup.log 568d8676…`, `probe.log bfe7f4af…`, `e9s.log 1188a0d2…`, `launches.log a0a686d5…`,
  `manifest_check.out 0ecbf600…`, scripts = the 02:17 uploads — the mirrored copies in `results/e9s/logs/box/` hash identically
  at home. Step 3b: 196 small records hashed (`e9s.records.sha256 9302b85e…`); `sha256sum -c` at home over the mirror: all 196
  OK. Step 4: sweep hits 0; HF cache (5.2 G) removed. Step 5: only systemd's user session. The home copy of
  `release_sweep.sh` now takes `${EXP}.records.sha256` in its allowlist (was hard-coded `e9l.…`, which only a second sweep run
  would have tripped on).
- **03:03:50 `box.sh terminate`** after the logs were home and hashed → `shutting-down` → **`terminated` at 03:09:57Z**; read back
  from EC2: `i-03c1b238426ff218c terminated User initiated (2026-09-14 03:03:51 GMT)`. The one other non-terminated instance in
  us-east-1 is `i-0785c090815238989` (t3.micro `eks-instance`, stopped, launched 2026-02-10): not this project's, untouched.
  Instance time ≈ 54 min (≈ $2.70) plus ≈ 49 GB egress (≈ $4.40).
- 03:0x home: `verify_mirror.py e9s` → `report.json sha256 abd1e456… complete=True scored=25/25`; **770/770 fingerprinted files
  verified from raw bytes, 48,927,599,343 B; ALL VERIFIED** (log `results/e9s/logs/verify_mirror.log`).
- 03:09:12 home: `summarize_e9 --config config/e9s.toml` **REFUSED** (rc 1), verbatim: `E9 SUMMARY REFUSED:
  …\results\e9s\calibration\tau.json does not exist; run `summarize_e9 --calibrate-tau` before the GPU run (0023)`. **Deviation
  from 0023's order:** E9-long ran `--calibrate-tau` at home on 09-09 before its run (`results/e9l/calibration/`); this runbook's
  §4 omitted the step, so e9s's calibration is written after the GPU run. What it can and cannot move: `calibrate_tau` reads
  only the upstream mapper, the archived generic dumps, the archived `r2.json` and E8's report — no `results/e9s/` artifact — and
  the summarizer recomputes it and refuses unless it equals the τ committed in `config/e9s.toml` (byte-identical to
  `config/e9.toml`) before reading any score. Run next, then compared with `results/e9l/calibration/tau.json` (same pin).
- 03:10:32 home: `summarize_e9 --calibrate-tau --config config/e9s.toml` **rc 0** (log `results/e9s/logs/calibrate_tau.20260914T031032Z.log`),
  upstream HEAD `063f4023…`, pin check `held`, generic dumps match E8's fingerprints. Against `results/e9l/calibration/` (09-09,
  same pin): `tau` identical (K 0.31864426531162937, V 0.48670564990559917, agent_K 0.4371020133925453), `heldout`, per-token
  sha, archived r2 sha and E8 report sha identical; `r2.json` differs in one field only, `seconds` (wall clock, 87.1 vs 44.4).
  `summarize_e9 --config config/e9s.toml` re-run immediately after.
- 03:12:21 home: **`summarize_e9 --config config/e9s.toml` PASSED** (rc 0; log `results/e9s/logs/summarize_e9.20260914T031221Z.log`):
  config `1842be5b493f`, coverage 25 included / 43 excluded of 68 observed; keep-subset re-score (0028) over 8 kept handoffs within
  tolerance (sums 9.2e-08, squares 3.2e-04, max |f* diff| 0); prefix control 0.000e+00 over 8,213 positions; rule line `-> HOLDS`
  (descriptive for this cell: 0037 adds no row and no verdict). Figures enter only through the 0038 entry.
- 03:19:59 home: **`e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json` PASSED** (rc 0;
  log `results/e9s/logs/e9_compare.20260914T031959Z.log`; `compare.json` sha256 `a7aa6c32…`, `compare.md` `8095b72f…`): 25
  handoffs, 155,257 matched tokens, identical alignments. Cross-checked, not re-derived: the native medians it reads (16+
  0.0195, τ 0.03 0.1433) are 0037's cited 0029 figures, the long ones (0.0629, 0.5255) are 0036's, the scaled ones (0.0381,
  0.2930) are this run's summarizer output, and both configuration shares (0.4285, 0.3916) reproduce by hand from them. The
  τ = 0.1 share (0.0000) sits on a floor: both short medians are 0.
- 03:20:15 home: `append_0038.py --preview` rc 0 (log `results/e9s/logs/append_0038.preview.20260914T032015Z.log`); the script's
  in-process `summarize_e9` and `e9_compare` passed again and printed the same figures. `compare.json` re-hashed to `a0699a82…`
  (was `a7aa6c32…`): the one field that differs is `long_cell.path` — the script passes the absolute path, the standalone run
  a relative one. Shown, not assumed: re-serializing the new file (CRLF, as `write_text` writes on Windows) reproduces
  `a0699a82` exactly, and the same bytes with only that field set back to `results\e9l\summary.json` reproduce `a7aa6c32` exactly.
  Two prose amendments before the append: the τ = 0.1 share is stated as 0 by construction (both short medians 0), and the
  summarizer's "bridge R²" is labelled as the A5 R² across the handoff, not control 4. Re-previewed before appending.
- 03:28:28 home: re-preview rc 0 (log `results/e9s/logs/append_0038.preview.20260914T032828Z.log`); both amendments present;
  `compare.json` again `a0699a82…` (deterministic across in-process runs), `summary.json` `2f562aca…`. Append run next.
- 03:35:55 home: **0038 APPENDED** (`append_0038.py`, log `results/e9s/logs/append_0038.20260914T033555Z.log`): both readers passed
  in-process a third time; `appended 0038 (E9 scaled short cell figures; no verdict); chain c9128ee936cd`; `ledger ok (blocks
  unchanged vs HEAD)`; `summary.json` `2f562aca…` and `compare.json` `a0699a82…` unchanged. Script retired.
- R8 stage `~/dev/hf-staging/linear-ceiling-e9s-2026-09-13/` = `results/e9s/` + `mappers/qwen3-0.6b-to-1.7b/k1.*` by hardlink + card
  `README.md`: 980 files = the mirror's 980, 0 not hardlinked; mapper shas OK. The staging script's credential sweep died silently
  (`xargs grep -l` exits 123 on zero hits under `pipefail`); re-run by hand with the pipe guarded: planted control fired (1),
  161 text files swept, **0 files with a credential-shaped string**; the one file outside the text extensions,
  `results/e9s/logs/pull.log.err`, swept separately (0). Stage 49,478,265,328 B. Ready for the operator's push
  (`ALLOW_PUBLIC=1 tools/hf_backup.sh hossainpazooki/linear-ceiling-e9s-2026-09-13 <stage>`; the dataset exists, public, empty).
