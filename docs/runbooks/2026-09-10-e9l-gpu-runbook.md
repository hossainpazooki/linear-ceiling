# E9-long GPU runbook — one rented L40S, one overnight sitting

**Date:** written 2026-09-09 (EDT evening), for the sitting that starts 2026-09-10 UTC · **Status:** runbook; the
log in §6 is filled during the sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating
them. The experiment is entry **0035** (registered before any prefill; `config/e9l.toml`; seed
`docs/2026-09-08-seed-e9-long-half.md`); its figures enter by entry 0036 (`docs/drafts/append_0036.py`,
`--box … --launched … --finished …` from §6). Driver tooling: `tools/ec2/` (this sitting's ssh form of
`tools/jupyterhub/`). The previous runbooks are the shape: `docs/2026-09-02-e9-gpu-runbook.md` (E9, the
instrument) and `docs/2026-09-08-n420-target-dump-runbook.md` (the box facts and traps of the last sitting).

## 0. Why a rented card, not the Algoverse queue

The pick-up of 2026-09-09 18:00Z (`docs/handoff/2026-09-09-pickup-e9-long-grant-request.md`) measured that no
E9-long option fits a 20 GB slice (1.7B fp32 OOM at T = 40,960 on 1g.20gb; every included |S| ≥ 34,974) and that
the Algoverse 40 GB pool had a four-day queue against an LCFM deadline of 2026-09-11 11:59 UTC. The operator
ruled AWS out of pocket (no credit on the account; G-instance quota verified at 768 vCPU on 2026-09-09). The 0035
entry records the ruling as "an overnight sitting on a rented single L40S (48 GB; no queue)".

## 1. The box

| fact | value | how known |
|---|---|---|
| Instance | EC2 **g6e.4xlarge**: 1 × NVIDIA L40S 48 GB, 16 vCPU, 128 GiB RAM, us-east-1 | `tools/ec2/box.sh up`; id and IP in §6 |
| Image | `ami-0eb7d782cce2fe526` = Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) 20260907 | `describe-images` 2026-09-09 |
| Root volume | 250 GB gp3, deleted on termination | `box.sh up` |
| Access | ssh as `ubuntu`, key pair `lc-e9l-2026-09-10` (created 2026-09-09, private key at home only), security group `sg-03021d0b6c09b4c75` = port 22 from the home IP only | `box.sh` |
| Shutdown behaviour | `stop` (a self-halt or an OS shutdown keeps the volume); termination is an explicit `box.sh terminate` that waits for `terminated` | `box.sh up` / R7 step 6 |
| Self-halt | `sudo shutdown -h +1440` armed by `setup.sh` (24 h); cancel with `sudo shutdown -c` | setup.sh |
| Price | $3.00/h on-demand (fetched 2026-09-09); egress $0.09/GB; forecast $16–34 for the sitting | pick-up conversation, prices fetched |
| Stack (pinned to the 09-04 / 09-08 sittings; 0028's tolerance was measured on it) | Python 3.12 (uv-managed), torch **2.11.0+cu128**, transformers **5.15.1**, numpy **2.5.2**; linear-ceiling venv CPU torch | setup.sh; versions printed in §6 |
| Shared? | No. R7 step 0 still runs (`ls -la ~`, `ps -u ubuntu`) and is expected to list only what §3 put there | protocol |

## 2. R2 — the measured budget

`tools/ec2/probe_e9l.py` runs the PINNED `load_model(model_id, rope_scaling=[e9.rope])` forward (fp32,
`sdpa_repeat_kv`, `use_cache`, `logits_to_keep=1` as `dump_kv` does) on synthetic ids at T = 32,768 / 65,536 /
**80,111** (the longest included |S|) for both models, and prints `torch.cuda.max_memory_allocated`. Prior
bound: the seed's extrapolation of ≈ 29.2 GiB for the 1.7B at 80,111 from the 09-08 1g.20gb ladder (16.72 GiB at
32,768; slope 276 KiB/token from the 0.6B ladder). The measured row goes into §6 and into 0036; stop if the 1.7B
row at 80,111 is not `ok`.

## 3. R3 — everything the run reads, by sha

| artifact | where | sha256 / pin |
|---|---|---|
| linear-ceiling checkout on the box | `~/linear-ceiling`, detached | `3f67e4e07c77a3d94c9e6a1ec93f1c91a5c37806` (0035 on the ledger; the e9l instrument) |
| upstream checkout on the box | `~/kv-transfer-replication`, detached | `063f4023fdde67dedbee01a92518ce7f83f6cf5d` (= `config/e9l.toml` `upstream_sha`, the RoPE-spec commit) |
| `config/e9l.toml` | committed | `bab1afca494c19131ef12ab1333aa771bb12aaebf5197e8f2765968986b577b7` |
| `config/e7-manifest.json` | committed | `8cf69956b8740b280a356adb70b29d60717cc17b64c58a563526bf6f4bbfd347`; `e7_manifest check` at home 2026-09-09 → `manifest ok: 188 files match disk; sha256 371fb4bf3cb089bd…` |
| traces | `~/linear-ceiling/traces/` from the home tarball (145 MB; gitignored) | checked on the box by `e7_manifest check` (both directions + bytes) in setup.sh |
| mapper (gitignored, 0029's n = 50 k = 1) | `~/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.json` / `k1.safetensors` | `2fd05c333156607436af128ccd7a009f175f13138d27e4126588c24f515cc86e` / `cd6a8d939b36db901f50e13bae446aef833f5d2ea7276658f499e993e63607f2` (`sha256sum -c` in setup.sh; the 2026-09-04 launch died without this file) |
| alignment / coverage at home | `results/e9l/align/coverage.json` | `492d8f0db8d0…` (0035 cites it); the box's `--align-only` is expected to reproduce it |
| box scripts | `~/setup.sh`, `~/run.sh`, `~/probe_e9l.py` = `tools/ec2/{setup.sh,run.sh,probe_e9l.py}` at the commit that carries this runbook | pulled back into `results/e9l/logs/box/` by the puller each round |
| models | `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-0.6B` from the Hub, public, no token | HF cache on the box, removed at release |

What the box must print: `[bridge] <hid>: …` × 3 (control 4, before any long handoff), then `[i/35] <hid>: same K …`
in the registered order (|S| ascending: `astropy__astropy-7671_traj#85` first, `django__django-11087_traj#152`
last). Coverage the verdict entry states: 68 observed · 35 included · 25 excluded as decided under the prior
cap · 4 above the cap · 4 empty receiver, the last eight by name (0035). Kept dumps: the 3 of the seed-9 draw
(`astropy-8872_traj#117`, `django-10554_traj#112`, `django-11087_traj#97`) + the 3 bridge handoffs' two receiver
dumps each.

## 4. Steps

1. **Home:** `tar -czf <scratch>/traces.tar.gz traces` from the linear-ceiling root; `tools/ec2/box.sh up`.
2. **Upload** the mapper pair, the tarball and the three box scripts (LF) with `box.sh put`.
3. **`setup.sh` detached** (`setsid nohup bash ~/setup.sh > ~/setup.log 2>&1 < /dev/null &`); poll `~/setup.rc`.
   It ends with the gate (`e9 --check` → ready), the alignment sha and the versions. Stop on any refusal.
4. **R2 probe** `probe_e9l.py` → `~/probe.log`; record the 80,111 row in §6.
5. **`run.sh`** (R4: log rotated, detached, `~/e9l.rc` on exit). Record the launch time.
6. **`pull.py e9l` at home** (hidden process on Windows): bridge kept dirs first (they are written first), then
   each kept handoff; verified then deleted on the box; small records and box logs every round.
7. **Cutoff.** The registered stopping rule (0035) allows `e9 --close-partial --config config/e9l.toml` at an
   operator-stated cutoff whose reason may not depend on any score; the default plan is to let all 35 finish
   (forecast 2–4 h of driver time after setup). If the morning sequence needs the box closed, the reason is
   "LCFM deadline 2026-09-11 11:59 UTC", recorded in §6 and in 0036 `--cutoff-reason`.
8. **Release (R7)**, in order: step 0 listing; mirror complete and re-verified from raw bytes (R6), print the
   mirror's `report.json` sha256; no tensor directory left under `results/e9l/` on the box; pull every log
   (`setup.log`, `probe.log`, `e9l.log`, `e9l.*.halt.log`, `launches.log`) and hash; sensitive sweep (no HF
   token was ever on the box; check anyway); `rm -rf ~/.cache/huggingface`; `box.sh terminate` and read
   `terminated` back from `describe-instances`. Record the UTC time.
9. **Backup (R8)** from the verified home mirror only: private dataset (made public by the operator on 2026-09-10; §6)
   `hossainpazooki/linear-ceiling-e9l-2026-09-10`, `results/e9l/` at the root plus
   `mappers/qwen3-0.6b-to-1.7b/k1.*` in upstream layout; verified by `tools/hf_verify_backup.py`. Token hygiene R9.
10. **Home:** `summarize_e9 --config config/e9l.toml` is the only reader (R11); a refusal is pasted verbatim into
    the closing brief. Then `append_0036.py --box "AWS EC2 g6e.4xlarge (1x L40S 48 GB), us-east-1, <instance id>"
    --launched <§6> --finished <§6> [--cutoff-reason …]`.

## 5. Traps carried from the last two sittings

The launch line stands alone on its line (a chained `setsid … & sleep; …` held the kernel pipe on 09-08; over ssh
the equivalent is a hung session — `run.sh` is the whole command). Liveness from `~/e9l.rc` and the log, never a
self-matching `pgrep`. Never `> e9l.log` on a relaunch (`run.sh` rotates). PyPI torch is a cu130 build; the box
takes the cu128 index (setup.sh). The upstream venv is where `dump_kv`/`score_positions` run; the driver finds it
at `.venv/bin/python`. Windows CRLF in a box script is a `bad interpreter`/`\r: command not found`; strip before
`put`. The home puller re-pulls a small file on size OR mtime change.

## 6. Log (UTC; filled during the sitting)

- 23:46:47 `box.sh up`: us-east-1c refused (InsufficientInstanceCapacity), us-east-1d took it. Instance **`i-0eafae594ebe8c291`**,
  g6e.4xlarge, public IP 3.231.206.244, ssh up on the second try. Card `NVIDIA L40S, 46068 MiB, driver 595.91.07`;
  AMI python 3.10.12 (the venvs take a uv-managed 3.12).
- 23:47 uploads by `box.sh put`: `k1.safetensors` (235,119,216 B, 6 s), `k1.json`, `traces.tar.gz` (16,637,313 B, sha256
  `ba9d43ab4be3…`; 211 entries), `setup.sh` (`ab3d2d02a10a…`), `run.sh` (`ab7432f143e7…`), `probe_e9l.py` (`a382aee0ac23…`).
- 23:47:59 `setup.sh` launched detached (`setsid nohup … > ~/setup.log`, exit code to `~/setup.rc`).
- 23:49:51 `setup.sh` **EXIT=0** in under two minutes: uv 0.12.12; clones detached at `063f402` / `3f67e4e`; mapper
  `k1.json` OK, `k1.safetensors` OK (`sha256sum -c`); `manifest ok: 188 files match disk; sha256 371fb4bf3cb089bd…` (= home);
  **`E9 gate: ready (entries 0019/0023/0025/0027/0035 committed; upstream pinned and clean; config/e9l.toml)`**;
  `--align-only` wrote `results/e9l/align/coverage.json` sha256 `074c04f19470…` — home's is `492d8f0db8d0…`, and the two
  are CONTENT-IDENTICAL (every field equal: `config_sha256`, `coverage`, `keep_subset`, `run_order`, `alignments`); the byte
  difference is CRLF (home, written on Windows) vs LF (box): both normalize to `074c04f19470…`. Versions: upstream venv
  `torch 2.11.0+cu128 cuda True NVIDIA L40S`, `transformers 5.15.1`, `numpy 2.5.2`; linear-ceiling venv python 3.12.14,
  torch 2.14.0+cpu. 24 h self-halt armed.
- 23:50:18 **R2 probe** `probe_e9l.py` (pinned `load_model(rope_scaling=[e9.rope])`, fp32, `sdpa_repeat_kv`, `logits_to_keep=1`,
  synthetic ids; EXIT=0; card 44.39 GiB total): 1.7B weights 6.41 GiB, `rope_parameters` on the loaded config
  `{rope_theta 1e6, yarn, factor 2.5, original 32768}`;

  | model | T | peak GiB | forward s |
  |---|---|---|---|
  | Qwen3-1.7B | 32,768 | 16.70 | 7.0 |
  | Qwen3-1.7B | 65,536 | 26.98 | 20.3 |
  | **Qwen3-1.7B** | **80,111** | **31.56** | 28.8 |
  | Qwen3-0.6B | 32,768 | 10.89 | 4.8 |
  | Qwen3-0.6B | 65,536 | 19.54 | 16.5 |
  | Qwen3-0.6B | 80,111 | 23.40 | 24.0 |

  The measured peak at the longest included |S| is **31.56 GiB**, 8% above the seed's 29.2 GiB extrapolation, ~13 GiB under the
  card; the 32,768 row (16.70) agrees with the 09-08 native row on the 1g.20gb slice (16.72), so the scaled forward costs the same
  memory as the native one and the two platforms agree. Every option would have OOMed a 20 GB slice; a 40 GB slice would have held
  it with ~8 GiB to spare. The row 0036 cites.
- **23:53:12 `run.sh`: driver launched detached** (`e9 --config config/e9l.toml`, pid 3300; log `~/e9l.log`, no prior log to
  rotate; exit code to `~/e9l.rc`). `--launched 2026-09-09T23:53:12Z` for 0036. 23:53:34Z home puller `tools/ec2/pull.py e9l`
  started as a hidden process (pid 29552; log `results/e9l/logs/pull.log`).
- 00:00–00:10 **control 4 (bridge) done before any long handoff**, all three kept directories (61 files each) streamed home,
  sha-verified against `report.json`, deleted on the box; controls ran on the first handoff in run order; scored 6/35 by 00:09Z
  (about two minutes per short handoff; GPU 100 %, 11 GB used; 4.9 G under `results/e9l/` on the box). Trap for next time: the
  driver's stdout is block-buffered into `~/e9l.log` (no `-u`), so `[bridge]` / `[i/35]` lines appear only at exit;
  `report.json` (mirrored every round) is the live record. Nothing in `~/e9l.rc` (still running).
- 00:11–01:12 scored 7 → 34/35 at 1.5–3 min per handoff (the puller's round log); kept dirs `django-10554_traj#112` and
  `django-11087_traj#97` (90 files each) verified home and deleted on the box as they appeared.
- **01:13 driver EXIT=0** (`~/e9l.rc`): the flushed log carries the three `[bridge]` lines and all 35 `[i/35]` lines in the
  registered order (`[1/35] astropy-7671_traj#85 … 238s` … `[35/35] django-11087_traj#152: same K 0.8880 in 217s`); 0 Tracebacks,
  0 REFUSED; `report.json` `complete: true`, 35 scored, `partial: null`. **`--finished 2026-09-10T01:13Z` for 0036** (the exact
  second is in the mirrored `e9l.rc` mtime / puller log). Driver wall 80 min against the 2–4 h forecast. Last kept dir
  (`astropy-8872_traj#117`, 17 G) streaming home at 01:13.
- 01:18:59 **puller done**: `run complete and every kept directory is home; final mirror done; report.json sha256
  084d9480af74de2b038ce82f22bef3d2e5d477dc7243addf0c357d64b13aa9c8`. Six kept directories (3 bridge × 61 files, 3 scratch × 90
  files) each verified against the driver's fingerprint before its box-side delete; mirror 46 G scratch + 11 G bridge + 2 G records;
  zero mismatches, zero stream failures, empty stderr over 43 rounds.
- 01:20 **R6 at home** (`tools/ec2/verify_mirror.py e9l`, independent of the puller's bookkeeping): `529/529 fingerprinted files
  verified from raw bytes, 61,143,230,360 B; ALL VERIFIED`; report.json sha256 `084d9480af74…` (R7 step 1).
- 01:21:00 **R7 step 0, first pass ABORTED (rc 11), nothing deleted** — `release_sweep.sh`'s allowlist was written for a hub login and
  flagged ten entries as NOT OURS: `.aws`, `.gnupg`, `.nv`, `.zshrc`, four license files, `gds-nvidia-fs`, `nvidia-acknowledgements`.
  Inspected read-only: every one either predates the launch (mtime 2026-09-07 05:45–06:50, the image build; `.aws` holds only the
  CLI's `cli/` cache dir, no `credentials`; `.gnupg` is the image keyring) or was created by our own tooling after it (`.nv` 8 K =
  CUDA's kernel cache at the probe; `.zshrc` = the uv installer's one-line shell hook). No other tenant. The script now classifies
  by mtime against the launch time (image baseline listed for the record; anything newer must be ours) and also sweeps
  `~/.aws` for keys; the abort itself is the checklist working as written (step 0 of 2026-09-09).
- 01:21:45–01:21:54 **R7 steps 0–5 on the box, rc 0** (`release_sweep.sh`, output `release.log`, pulled home): step 0 lists the
  13 image-baseline entries by mtime and nothing newer that is not ours; step 2 `layer*.npz files remaining: 0` (the six kept dirs are
  gone, `scratch/` and `bridge/` hold only the small records); step 3 box-side sha256 of every log (`setup.log 60c207d5…`,
  `probe.log 7fae19fe…`, `e9l.log b9d43d04…`, `launches.log 3f4da129…`, `manifest_check.out 0ecbf600…`, scripts as uploaded), all
  re-hashed at home after the pull and EQUAL; step 3b `e9l.records.sha256` (222 small records) diffed against the mirror by path:
  **0 missing, 0 differing**; step 4 no token file, no `.git-credentials`, no `.netrc`, `~/.aws` has no key material, HTTPS remotes
  only, `~/.cache/huggingface` (5.2 G) removed; step 5 only systemd's user session remains.
  **Defect found in the sweep itself, on the record:** its token grep printed a match (this script's own pattern literal, a false
  positive) yet reported `hits: 0`, because a nonexistent `~/.bash_history` made `grep -l` exit 2 and `&& hits=1` never ran — a
  fail-open. Read by eye: the only match was `release_sweep.sh`. Fixed in `tools/ec2/release_sweep.sh` (count matches with `-s`,
  exclude the script itself); the box copy that ran is the pulled `logs/box/release_sweep.sh` (pre-fix).
- 01:20–01:29 **`summarize_e9 --config config/e9l.toml` at home, rc 0, no refusal** (9 min; log
  `results/e9l/logs/summarize_e9.20260910T0120Z.log`; `results/e9l/summary.{md,json}`): 35 scored of 35 registered, complete;
  bridge (control 4) median native-vs-scaled f*(tau_K) K 0.0000 / V 0.0000 vs reading max 0.15 -> CARRIED; keep-subset re-score
  within 0028's tolerance (per-head sums 3.4e-08 rel, squares 4.2e-04 rel; f* diff 0); prefix-invariance 0.000e+00 over 34,974
  positions; rule line `-> HOLDS`. No number from here enters the ledger except through `append_0036.py`.
- 01:29:59 **R7 step 6: `box.sh terminate`** (held until the summarizer passed, so a same-platform re-score stayed possible);
  `shutting-down` → **`terminated` read back from `describe-instances` at 01:35:36Z**; no tagged volume remains (root deleted on
  termination). Box vs mirror `report.json` sha256: both `084d9480af74…` (the puller's final line and `verify_mirror.py` agree; the
  box copy was in the 222-record diff). Instance life 23:46:47–01:35:36 = 1 h 49 min ≈ $5.5 compute + ≈ $5.5 egress (61 GB).
- **Release report (R7 step 7):** mirror complete and re-verified (529 files, 61,143,230,360 B); step 3 pulled `setup.log`, `probe.log`,
  `e9l.log`, `launches.log`, `manifest_check.out`, `release.log`, `e9l.records.sha256`, the three scripts and the three `.rc` files
  into `results/e9l/logs/box/` (sizes small; hashes above); step 4 found nothing sensitive and removed 5.2 G of HF cache; stop
  response `shutting-down`; release time 01:35:36Z. No run numbers here.
- **For 0036:** `--box "AWS EC2 g6e.4xlarge (1x NVIDIA L40S 48 GB), us-east-1d, i-0eafae594ebe8c291" --launched 2026-09-09T23:53:12Z
  --finished 2026-09-10T01:13:09Z` (launch line in `launches.log`; finish = `e9l.rc` mtime). No cutoff: 35 of 35.
- **R8 backup: NOT YET PUSHED** (needs the operator's scoped write token; the commands are in the closing brief). Dataset name
  `hossainpazooki/linear-ceiling-e9l-2026-09-10`.
- **R8, 2026-09-10 (operator): the run's files stay local AND are backed up to the dataset above.** State at 16:50Z: the push is INCOMPLETE. 482 of the 724 staging files are on the Hub and match byte for byte; `tools/hf_backup.sh` stopped on `Private repository storage limit reached` at the tree step. The dataset also holds 18,986 stray repository files (incl. `.venv` and gitignored `results/`) from an upload run in the wrong directory; nothing credential-shaped was among them (swept, with positive controls). Removing them is `tools/hf_prune_backup.py` (dry run: 27 operations), and they keep counting against storage until the history is squashed. Nothing is to be deleted locally.
- **R8 closed, 18:28:26Z: BACKUP VERIFIED.** Steps, all by the operator: the strays were already deleted from the
  dataset (the prune found 0 left to remove). A second `tools/hf_backup.sh` run at 18:14Z stopped on the private storage limit
  again, at 595 of 724. 18:20:30Z history squashed (`super_squash_history`), which removed the strays from history too.
  The dataset was then made **PUBLIC**, and `ALLOW_PUBLIC=1 tools/hf_backup.sh` finished the tree and the card. Verifier: `lfs-compared 567,
  downloaded+hashed 157, problems 0`. Re-checked independently without a token: 725 files at head (724 + `.gitattributes`),
  61.94 GB, none missing or extra. All 529 `report.json` fingerprints match (476 by the Hub's `lfs.sha256`, 53 read back
  and hashed), and a flipped hash does not match. Before the dataset went public, the 156 text files in the staging tree were
  swept for credential shapes. The one match is `logs/box/release_sweep.sh`'s own pattern; a planted control matched 2 of 2.
  The write token is to be revoked (R9).
