# Llama long cell (entry 0050 → 0051) on a RunPod A100 80 GB — home side on the Mac mini

**Date:** 2026-10-07 · **Status:** runbook written before the sitting; §6 is the log, filled in UTC as it happens.
Inherits `docs/gpu-experiment-protocol.md` R1–R12 and the Llama campaign runbook `docs/2026-09-18-llama-gpu-runbook.md`
(§9 is this sitting's design: native receiver, floor 32,768, cap 81,920, cuttable); takes its RunPod shape from the two
operator sittings of 2026-10-06/07 (`docs/2026-10-06-cache-behavior-runpod-runbook.md`, `docs/2026-10-07-consolidation-runpod-runbook.md`).
Registration: **0050** (appended `cff787f`); figures: `docs/drafts/append_0051.py` (staged). Descriptive, no row, no verdict;
this cell cannot move, support or refute H-E9L and is never pooled with 0036.

## 0. The home side is the Mac mini, not the Windows box

Decided 2026-10-07 after the camera-ready work. Windows had 23 GB free against a ~45 GB verified mirror (3 kept handoffs,
42.3 GiB by the runbook's formula) plus 22 GB of staged gated weights, and every trap of the week lives there (MSYS path
conversion, CRLF digests, the `.npz` `create_system` byte, MAX_PATH, `fsync` on a read handle). The Mac (arm64, macOS
27.0.1, 16 GB RAM, 363 GiB free, uv 0.12.20, Python 3.12 via uv) has none of them. **What was verified on it before any
card was considered**, each in one ssh round-trip from the Windows session (so no paste corruption):

- `~/dev/linear-ceiling` at `ea5d9cf` (origin/main), `.venv` 3.12: `ledger ok`, `scope ok`, **595 passed / 3 skipped**
  (the Windows checkout errors on 28 of the same tests in the driver's `fsync`).
- `~/dev/kv-transfer-replication` detached at `06f8d55` with its own venv (torch 2.14.1, transformers 5.15.1, numpy 2.5.3);
  the pair's inputs pulled from the public R8 datasets `emmmy/linear-ceiling-e8f-2026-09-18` / `…-e9f-2026-09-19`:
  `data/kv/<pair>/{source,target}` 2.9 GB, `mappers/<pair>/k1.{json,safetensors}`, `results/mapper/<pair>/r2.json`.
- Carry bundle from Windows (331 files, 28 MiB, sha `796088b2…`, every member sha-checked on arrival): `traces/` (145 MB,
  the committed manifest's bytes), `results/e7/skeleton_report.json` (`0aba0fbe…`, the reproducible value, not 0044's
  `27dc922e` outlier), `results/e8f/report.json` (`4682508afd35`), `results/e9fl/align/` + `calibration/tau.json`
  (0050's pins `16121e677b97` / `dd3fca27e82a`).
- **τ rehearsal PASS**: `calibrate_tau(cfg, out_dir=results/e9fl/recheck/mac-rehearsal)` ran the upstream scorer on the
  archived dumps on the Mac and reproduced τ_K / τ_V / τ_agent_K within tolerance (2e-10 / 5e-11 / exact). This is every
  home-side path of `summarize_e9` except the kept-dump re-score, which gets its first exercise on the sitting's first
  kept handoff while the pod is still up (R7: hold termination until the summarizer passes).
- `e9 --check --config config/e9fl.toml` → `E9 gate: ready`. `rp.py balance` from the Mac's own key file: $23.51.
- A fresh 4096-bit pod keypair at `~/.ssh/id_rsa` (private half never leaves the Mac); `rp.py up` injects the public half
  as the pod's `PUBLIC_KEY`, so no RunPod account-level key is involved.
- Launcher rehearsal (`REHEARSAL=1 EXP=e9fl CONTEXT_FLOOR=32768`): see §6.

**Known Mac facts for the operator:** a non-interactive ssh shell has no `~/.local/bin` on `PATH` (prepend it before
anything that needs `uv`); the 09-14 review measured less `same_K` bit-identity on Apple arm64 than Linux-vs-Windows
(0.51–0.69 of squares vs 0.99+), inside the 1e-5 re-score tolerance by ~1.5× — a refusal there is a finding to record,
not to work around; the re-score of a 19.8 GiB kept handoff on 16 GB RAM has not been done before (per-layer files,
~0.6 GB each, should stream).

## 1. What 0050 registered (the run reads none of this from here; the config and coverage are the authority)

32 handoffs (68 observed; 28 covered by the short cell under the floor; 4 above 81,920 and 4 with an empty receiver
prompt excluded and named), `n_sender_asc`, `allow_partial`; included |S| 33,086–74,233; prefill budget 1,541,320 sender
(both models) + 370,926 receiver = 3,453,566 tokens; `[e9.keep] n = 3, seed 9`; τ_K 0.2861 / τ_V 0.5289 / τ_agent_K
0.2689 (this pair's own, identical to the short cell's); no `[e9.rope]`, no `[e9.bridge]` — the two RoPE controls
(native window ≤ every dump's `max_position_embeddings`; role-scoped frequency identity) replace the bridge.

## 2. Pins (R3 — everything by sha)

| what | value | where it is checked |
|---|---|---|
| upstream `UP_SHA` | `06f8d55592570deae70c3feb9f84a75c4044fb03` | `config/e9fl.toml`; launcher `clone_exact` + RoPE-spec ancestry |
| linear-ceiling `LC_SHA` | `8696e83bd2c98c548c0aa2d854dcdbc7ce6eb584` (pushed 2026-10-07 ~16:00Z; carries this runbook, the launcher change and entry 0058; launcher sha at it `df4c9707…` = the rehearsed copy) | launcher `clone_exact` |
| mapper `k1.json` / `k1.safetensors` | `6cbfad42b6b0…27fb` / `fe77166a8ff4…69fc` (Mac = Windows = Hub) | launcher `sha256sum -c`; calibration names them |
| `results/e9fl/align/coverage.json` | `16121e677b97195cc1df9053f0e07d26302f12ae9994bbf96e016a1212b648f3` | box `--align-only` must reproduce it exactly |
| `results/e9fl/calibration/tau.json` | `dd3fca27e82affc937d70639b6d9428b811187c5354fb255eda4a9b991a0f604` | launcher `CALIBRATION_SHA256` |
| `traces.tar.gz` (Mac-built, 16,628,699 B) | `21fe358eae8b2c13…` | box `e7_manifest check` → `manifest ok` |
| Llama-3.2-3B snapshot `13afe512…` | `config.json` `35f063e9…`, `tokenizer.json` `79e3e522…` | staged offline (§3) |
| Llama-3.1-8B snapshot `d04e592b…` | `config.json` `54acfad3…`, `tokenizer.json` `76e48799…` (gate approved ~16:05Z, staged 16:4xZ) | staged offline (§3) |
| `hf-cache.tar.gz` (Mac-built: `COPYFILE_DISABLE=1 tar --exclude='._*' -cf - hub \| gzip -1`) | 18,008,081,915 B, sha `478bf578a6e612b7c0039c4382e39e43f03db29a09e008a0047eac462c0d72c6`; members: all under `hub/`, 0 AppleDouble, 0 token-shaped, 6 safetensors | launcher archive validation (hub/ only, no token files) |

## 3. Budget and the card (R2)

- **Card:** A100-SXM4-80GB, community, $1.39/h (`rp.py price` 2026-10-07; PCIe refused thrice on 10-06 — create
  *filters*, not stock). `--hours 6.0` → sitting ceiling $8.34; campaign `--cap 12`; `--max-price 1.45`; `--disk 160`
  (0044's secure pod had 160 GB; 30.9 GB of dumps per handoff at the cap, puller deleting kept trees after verification);
  `--min-ram 48` (fp32 8B loads to host first, ~30 GiB). **Fallback:** H200 141 GB at $3.59/h, only if the probe refuses.
- **Peak:** runbook §3.4's 68.1 GiB (73.6 with margin) is an *extrapolation*; the launcher's R2 probe measures a forward at
  this run's real top rung (coverage max 74,233, or the first handoff's S+1) for both models and refuses under
  `MIN_GPU_MARGIN_GIB=4` of measured headroom. Launch on the measurement, never on the table.
- **Time:** the short cell (28 handoffs ≤ 32,768) took 64 min on an A100 SXM; this has ~2.2× the tokens on longer
  sequences — plan 2.5–4 h GPU plus setup and the ~22 GB weights upload from the Mac.

## 4. Inputs staged offline (R3, R9) — `~/stage-0051/` on the Mac

`sitting_b.sh` (this commit's copy, CR-free), `k1.json`, `k1.safetensors`, `tau.json`, `traces.tar.gz`, and
`hf-cache.tar.gz` built as `tar -cf - -C ~/hf-stage hub | gzip -1` once both snapshots are staged (`hub/` only — never the
parent, which could hold a token file; the launcher validates the archive before extracting). **No HF token ever exists
on the pod**; R7 step 4 asserts "never existed", not "removed".

## 5. The sequence (every command from the Mac over ssh; `PATH=$HOME/.local/bin:$PATH`)

1. `rp.py up --gpu 'NVIDIA A100-SXM4-80GB' --cloud COMMUNITY --price 1.39 --max-price 1.45 --hours 6.0 --disk 160
   --min-ram 48 --cap 12 --name linear-ceiling-sitting-c --verify-file ~/.cache/linear-ceiling/e9fl-verified.json --yes`;
   `rp.py wait-ssh`.
2. **Net first:** `nohup bash tools/runpod/watchdog_supervised.sh` (home, detached; `rp.py watchdog --exp e9fl
   --sitting-max 8.34`), then `rp.py arm-deadman --ttl-min 400` on the pod (community images lack pod credentials, so the
   home watchdog is the only real net — 10-06 lesson).
3. `rp.py put` each staged input to `/workspace/` (hf-cache last; verify each by `ls -l` + `sha256sum` on the pod).
4. Launch, detached, on the pod (one line; values are §2's):
   `setsid nohup env EXP=e9fl CONTEXT_FLOOR=32768 DUMP_FREE_GIB=100 PAIR=llama3.2-3b-to-llama3.1-8b
   UP_REPO=https://github.com/hossainpazooki/kv-transfer-replication.git UP_SHA=06f8d55592570deae70c3feb9f84a75c4044fb03
   LC_REPO=https://github.com/hossainpazooki/linear-ceiling.git LC_SHA=8696e83bd2c98c548c0aa2d854dcdbc7ce6eb584
   MAPPER_JSON_SHA=6cbfad42b6b08d3a39c770dd6313d7d7cfc6035555c03aed1dc4c549828c27fb
   MAPPER_ST_SHA=fe77166a8ff4f7d55230486806679f6a91acd24c4efb305fdf9a93556a2869fc
   COVERAGE_SHA256=16121e677b97195cc1df9053f0e07d26302f12ae9994bbf96e016a1212b648f3
   CALIBRATION_SHA256=dd3fca27e82affc937d70639b6d9428b811187c5354fb255eda4a9b991a0f604
   bash /workspace/sitting_b.sh > /workspace/sitting_c.launch.out 2>&1 < /dev/null &`
   Watch `/workspace/sitting_b.setup.log` through: clones → venvs (torch 2.11.0+cu128) → CUDA smoke (≥ 70 GiB) → τ bound
   → `manifest ok` → mapper shas → free space ≥ 100 GiB → `E9 gate: ready` → weights extracted, offline, token-file count 0
   → box coverage sha = home sha → **probe** (`PROBE_SITTING_B_OK`, both models, headroom ≥ 4 GiB) → `SITTING_B_LAUNCHED`.
5. Puller, home, beside the driver: `pull_verify_b.py --exp e9fl --pair llama3.2-3b-to-llama3.1-8b --config
   config/e9fl.toml --expected-pod-name linear-ceiling-sitting-c --delete-verified --terminate-on-receipt`. It mirrors
   each checkpoint, pulls kept trees, hashes every named byte at home, deletes the remote copy only after agreement, and
   writes the terminate receipt only when the launcher's final manifest covers and matches everything.
6. **Before termination:** `summarize_e9 --config config/e9fl.toml` on the Mac mirror (the only reader, R11). A refusal
   is re-scored on the pod while it is still up. Then R7 steps 0–7 (shared-login check, sweep with a planted positive
   control, terminate, read absence back), R8 push from the verified mirror to `hossainpazooki/linear-ceiling-e9fl-<date>`
   + `hf_verify_backup.py` → `BACKUP VERIFIED`, token revoked, `append_0051.py --preview --box … --launched … --finished …`.
7. A budget stop: drain by signal at the watchdog's threshold → `pull_verify_b.py --final-partial` → `e9 --close-partial
   --config config/e9fl.toml` at home → `--cutoff-reason` on the append.

## 6. Log (UTC)

- 15:17 Mac ssh opened from the Windows session (operator added the key); upstream clone confirmed at `06f8d55`; carry
  bundle `796088b2…` copied, 331/331 sha OK; **τ rehearsal PASS** (K pinned 0.2861326431727862 / mac 0.28613264297901364;
  V 0.5289405769050128 / 0.5289405769525087; agent_K equal).
- 15:30 RunPod key file on the Mac (0600); `balance $23.5124` from the Mac. Pod keypair generated 15:32.
- 15:35 Llama-3.2-3B staged (6.0 GiB); **Llama-3.1-8B refused: account not in the authorized list** — the 3.1 licence is a
  separate Meta gate from 3.2 (the 10-01 work needed only the shared tokenizer). Request submitted; awaiting review.
- 15:39 staged `traces.tar.gz` (`21fe358eae8b`), `k1.*`, `tau.json`, launcher under `~/stage-0051/`.
- 15:41 launcher rehearsal attempt 1: clones at both exact pins OK, RoPE ancestry OK, then `uv: command not found`
  (non-interactive ssh PATH); re-run with `PATH=$HOME/.local/bin:$PATH` — result recorded below.
- 15:42 **launcher rehearsal COMPLETE** (`REHEARSAL=1 EXP=e9fl CONTEXT_FLOOR=32768 DUMP_FREE_GIB=100`, LC_SHA `ea5d9cf`
  for the clone; launcher sha `df4c9707…` = this commit's `tools/runpod/sitting_b.sh` with CRs stripped): both venvs
  built (torch pin relaxed, stated), τ bound to `config/e9fl.toml` (`pair=llama3.2-3b-to-llama3.1-8b cap=81920
  floor=32768 mapper_k=1 allow_partial=True`), `manifest ok: 188 files` (`371fb4bf…`), both mapper shas OK, `E9 gate:
  ready`, config sha `2f8d9545e1f3…`, `SITTING_B_OK`. Not validated by it (the script says so): the cu128 torch build,
  the GPU smoke, the 100 GiB disk floor, the weights — all box-side.
- ~16:05 Meta approved the 3.1-8B gate; 16:4x operator staged the 8B (`d04e592b…`; §2 shas); `~/hf-stage` 21 GB.
- 16:00 operator pushed `1ca3650` (0058) + `8696e83` (launcher, this runbook); CI green on both; Mac checkout at `8696e83`
  (operator's `git pull`; the git-guard blocks mine even over ssh). Dry-run `rp.py up` from the Mac rendered the planned
  request (160 GB disk, ≥ 48 GB RAM, ≥ 8 vCPU, CUDA 12.8–13.0, Mac pubkey injected).
- 16:49–16:56 `hf-cache.tar.gz` built on the Mac (§2 row; 0 AppleDouble, 0 token-shaped, 6 safetensors members).
- 17:00:23 `up` A100-SXM4-80GB community $1.39, 6.0 h, cap $12, default host filters: **REFUSED** ("no longer any
  instances available with the requested specifications") — the 10-06 cause (create filters, not stock). Retried with
  `--min-ram 32 --min-vcpu 4 --cuda 12.8 12.9 13.0 13.1 13.2` (none registered; RAM kept ≥ 32 GB for the fp32 8B host load).
- 17:00:58 REFUSED again (widened filters, disk 160); 17:01:25 REFUSED (disk 120). `rp.py price` now lists **no community
  A100-SXM4-80GB at all** (it showed $1.39 Low at 16:3xZ) — stock, not filters, this time.
- **17:01:48 `up` SECURE A100-SXM4-80GB $1.59/h (0044's own card), 6.0 h, disk 160, widened filters: pod `uua1cpjql18jb6`
  created**, `linear-ceiling-sitting-c`, start balance $23.5124, sitting ceiling $9.54, campaign cap $12. Home watchdog
  supervisor started on the Mac under `caffeinate -i` (`--exp e9fl --sitting-max 9.54 --every 60`); 17:02:13 watchdog
  up (`rp.py` wraps it in `caffeinate -dimsu` itself; `pmset` shows sleep prevented).
- 17:02:22 `wait-ssh` OK → `root@154.54.102.29 -p 16988`. `arm-deadman`: **NOT ARMED** (no pod-scoped credentials on
  this pod either; the home watchdog is the only net — as on 10-06/10-07). Card `NVIDIA A100-SXM4-80GB, 81920 MiB,
  driver 580.126.16` (0044's driver), overlay 160 GB, 128 vCPU, host RAM 2,003 GB.
- 17:02–17:03 `put` sitting_b.sh, k1.json, k1.safetensors, tau.json, traces.tar.gz; all five sha-verified on the pod
  (`df4c9707` / `6cbfad42` / `fe77166a` / `dd3fca27` / `21fe358e`).
- 17:03:47–17:08:23 `put hf-cache.tar.gz` (18,008,081,915 B at ~68 MB/s); `sha256sum -c` on the pod **OK** (`478bf578…`).
- **17:09:39 launcher started on the pod** (pid 438, detached; `/workspace/launch_c.sh` = the §5 step-4 line with the sha
  check in front; output `/workspace/sitting_c.launch.out`, steps in `sitting_b.setup.log`). Home puller started on the Mac
  17:1x under `caffeinate -i` (`--exp e9fl --pair … --config config/e9fl.toml --expected-pod-name linear-ceiling-sitting-c
  --delete-verified --every 60`; NOT `--terminate-on-receipt` — R7 holds termination until the summarizer passes).
- 17:09:39–17:16:43 launcher: clones at both pins ✓, venvs ✓ (29 s), CUDA smoke ✓, τ bound ✓, `manifest ok` ✓, mapper
  shas ✓, free space 127 GiB ≥ 100 ✓, `E9 gate: ready` ✓ (config `2f8d9545…`), archive validated and extracted (6.5 min;
  `hub/blobs/` 21 G, model dirs are symlinks), offline mode, token-file count 0 ✓ — then **SETUP_FAILED at "box alignment"**:
  `huggingface_hub.errors.IncompleteSnapshotError: … 'meta-llama/Llama-3.2-3B' … 1 file(s) are missing (original/params.json)`.
  **Cause:** `linear_ceiling.weights.snapshot` calls `snapshot_download(allow_patterns=["*.safetensors", "*.json"])`, and
  huggingface_hub 1.33 (unpinned in the lc venv) checks the offline cache for completeness *under those patterns*; the
  staging excluded `original/*`, which dropped `original/params.json` (a ~200 B JSON that `*.json` matches). The weights are
  complete; the instrument is untouched. **Rule from it: stage a gated cache with the consumer's exact `allow_patterns`,
  not a hand-picked subset.** Fix: stage `original/params.json` for both models (operator's token, once more), ship a delta
  into `/workspace/hf`, prove completeness with the same `snapshot_download` call offline on the pod, relaunch via
  `/workspace/launch_c2.sh` (the §5 line without the archive sha check — the archive was validated, extracted and removed).
- 17:16:47 home puller **REFUSED**: "pull state pod_id belongs to another sitting". **Cause:** `pull_verify_b.py` derives
  the `--state`, `--local` and `--remote-results` defaults from the module constant `EXP = "e9f"` at import time, not from
  `--exp`, so it opened `runpod-e9f-pull.json` and `results/e9f`. For this cell all three are passed explicitly
  (`--state ~/.cache/linear-ceiling/runpod-e9fl-pull.json --local results/e9fl --remote-results
  /workspace/linear-ceiling/results/e9fl`). Not a launcher or driver matter; the pod kept billing idle meanwhile
  (spend $0.47 at 17:19Z; watchdog healthy).
- 17:2x operator staged `original/params.json` for both models (3B 220 B `9ec1107c…`, 8B 199 B `fce5ee11…`); delta tarball
  of the 6 files newer than the archive (2 symlinks, 2 blobs, 2 lock files; all under `hub/`) put and extracted into
  `/workspace/hf`; **offline completeness proven on the pod with the consumer's own call** (`snapshot_download(
  allow_patterns=["*.safetensors","*.json"])` under `HF_HUB_OFFLINE=1` in the box's lc venv) for both snapshots.
  Relaunched via `/workspace/launch_c2.sh`.
- 17:27:29–17:28:23 relaunch: every step through weights passed (cache complete); box `--align-only` ran (48 s) and
  **REFUSED: box coverage sha `9f10092b…` != home `16121e67…`**. Fetched the box file and diffed it against the home
  pin: parsed JSON identical (all 68 alignment records, run order, keep subset, counts); byte diff = **CRLF only** — the
  home file carries 992 CRs (written on Windows in text mode), the box file none; after stripping CRs, 993 lines, 0
  differ. **So 0050's pin `16121e677b97…` is the sha of the CRLF rendering; the LF rendering of the same content is
  `9f10092b62382e69080e155e59551a15ed6e0894ae2bba4839a61cb0c47550f5`.** The short cell matched byte-for-byte on 09-19
  because that home file was LF. Relaunched (`launch_c3.sh`) with the LF sha as `COVERAGE_SHA256`; 0051 must state both
  renderings beside the pin (`hash-what-the-pipeline-consumes` trap, now on a registered pin).
- **17:31:07 relaunch (`launch_c3.sh`): alignment passed with the LF sha; R2 probe at T = 74,233 (coverage max) PASSED on
  the card** — `meta-llama/Llama-3.1-8B` (target) fp32, `attn = sdpa_repeat_kv`: peak allocated **64.546 GiB**, peak
  reserved **69.754 GiB**, headroom 9.081 GiB ≥ 4.0 (109 s); `meta-llama/Llama-3.2-3B` (source): 38.104 / 40.906 GiB,
  headroom 37.825 (58 s). `PROBE_SITTING_B_OK`. The campaign runbook's §3.4 extrapolation (68.1 GiB) sat 1.7 GiB under the
  measured reserved peak; an 80 GB card is right, with ~9 GiB to spare.
- **17:35:23 driver LAUNCHED** (`SITTING_B_LAUNCHED pid=2300 mode=plain`; `/workspace/e9fl.status` RUNNING; log
  `/workspace/e9fl.log`). 17:40 home puller started on the Mac with the explicit `e9fl` paths (§6 17:16 entry); first poll:
  "no report.json yet (141 result files, 5 logs refreshed)". Spend $1.05 at 17:40Z (0.65 h, of which ~25 min were the two
  refused launches).
- 17:41 first handoff (`astropy-7336_traj_sw119`, |S| 33,086, the shortest) dumped (8.6 G scratch) and scoring on CPU
  (`score_positions.py`; GPU idle between dumps, driver log empty by design — the record is `report.json`).
- **17:43 first checkpoint**: `report.json` scored 1 of 32, `complete: false`, controls {identity, prefix, null} on
  run_order[0]; GPU 50,389 MiB in use (handoff 2 dumping); disk 39 G used. Home puller: "scored 1/32 … snapshot
  `checkpoints/report.1.json` (every named artifact verified here)". Spend $1.10. Loop proven end to end; a 10-min
  background poll now waits for the driver's exit.
- **19:46:17 `SITTING_B_OK` — driver EXIT=0, `report.json` scored 32 of 32, `complete: true`, no partial**; last handoff
  `django__django-11087_traj#152` (same K 0.9138, 385 s); `/workspace/e9fl.final.sha256` written 19:46. Driver wall time
  17:35:23 → 19:46:17 = **2 h 11 min** for 3,453,566 tokens. Home puller **COMPLETE** by 19:54: report sha
  `b046bb9dd70d56d2b52877df81ce37734ebcc69216a4c5d663fc81fb5d2844f9`, **591 hash checks, 49,377,348,389 B** verified at
  home, all three kept trees (`astropy-8872_traj#117`, `django-10097_traj#137`, `django-11087_traj#97`) verified then
  deleted/proved absent on the pod; terminate receipt `~/.cache/linear-ceiling/e9fl-verified.json`. Spend $4.57 at 19:54Z.
  Pod held (R7): the summarizer runs on the Mac mirror first.
- 19:54:57 `summarize_e9 --config config/e9fl.toml` started on the Mac (detached under `caffeinate`, 8-thread cap as at
  home for e9f; the Mac has 12 cores, 16 GiB). Mirror on the Mac: 46 G — `align/ calibration/ checkpoints/ controls/
  logs/ report.json scores/ scratch/{3 kept trees} tokens/`; `logs/box/sitting_b.evidence/versions.txt`: launcher
  `df4c9707…`, linear-ceiling `8696e83…`, upstream `06f8d55…`, coverage `9f10092b…`, coverage_max = probe_max = 74,233,
  card `A100-SXM4-80GB 81920 MiB driver 580.126.16`, up_python 3.12.13, torch 2.11.0+cu128 (CUDA 12.8).
- 19:55 **R7 read-only pre-checks on the pod** (release itself waits for the summary): step 0 — `~` holds the image
  baseline (`.bashrc`, `.profile` 2019, `.launchpadlib` Sep 10) and only our `.cache .nv .runpod .ssh` (17:02–17:10);
  processes: `docker-init`, `start.sh`, nginx, `sleep infinity` only — the driver is gone. Step 2 — `results/e9fl/scratch`
  empty, 1.9 G of small records left (all mirrored and in the final manifest). Step 4 — no `~/.cache/huggingface`;
  `grep -rlsE 'hf_[A-Za-z0-9]{20,}'` over `/root` + `/workspace` (excluding the weight cache, venvs, results, .git) with a
  planted positive control: **3 matches = the planted file + 2 library false positives in uv's package cache**
  (`hf_xet/hf_xet.abi3.so`, `transformers/testing_utils.py`) — code, not credentials; the box never had a token
  (`HF_HUB_DISABLE_IMPLICIT_TOKEN=1`, offline weights). Weight cache `/workspace/hf` 21 G, removed at release.
- 19:55 summarizer **false start** on the Mac (my launch, not a result): it re-derives the alignments from the traces and
  resolves the source tokenizer through `weights.snapshot` → `snapshot_download`; launched without `HF_HOME` at the staged
  cache or offline mode it hit the gated repo (401) before any check. Relaunched 19:5x with `HF_HOME=~/hf-stage
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` (the box's own recipe; no token). Spend $4.64.
- **19:56:32–19:58:53 `summarize_e9 --config config/e9fl.toml` PASSED on the Mac** (2 min 21 s; `summary.json` 94,944 B,
  `summary.md`): alignments re-derived from the traces, every R² recomputed from the moments, per-token squares summed
  against the moments, **keep-subset re-score of the 3 kept handoffs within tolerance** (per-head sums 6.4e-07 relative vs
  1e-05; every square 6.9e-04 relative vs 1e-02; bit-identical fraction ≥ 0.079 — Apple arm64, as the 09-14 review
  predicted), τ recomputed from the archived mapper, RoPE controls on 97 dumps (cap 81,920 inside every recorded window
  131,072 both roles; frequencies identical within each role; spec-vs-model max |diff| 1.2e-07). 32 scored of 32,
  complete. The reader prints 0058's words beside f*. The 16 GiB re-score risk did not materialise. Figures enter only by
  0051 from this reader; none are restated here.
- 20:02–20:03 **R7 release** (a first attempt at 19:59 ran nothing — an unquoted zsh variable; nothing destructive
  happened): step 3 — wrapper outputs pulled to `results/e9fl/logs/box/wrappers/` (`sitting_c.launch.out` 8,706 B
  `0c748480…`; `launch_c.sh` `46a7eb5e…`, `launch_c2.sh` `e1f6b237…`, `launch_c3.sh` `365ec949…`); step 4 — sweep with the
  planted control, uv's package cache excluded: **1 match = the planted file**; `rm -rf /workspace/hf` confirmed gone;
  no `~/.cache/huggingface`; step 5 — the 19:55 listing stands (system processes only; the 20:02 count line was malformed
  by quoting and is not relied on); box `report.json` sha = mirror `b046bb9dd70d56d2…`; step 6 — `terminate` on the puller's
  receipt → **PROVEN GONE** 20:03:45Z, `pods 0 (nothing is billing)`. **Sitting total $4.8014**; balance $18.7339. GPU
  2 h 11 min of 3 h 02 min billed (two refused launches, the deliberate hold for the home summary, release).
- 20:0x `append_0051.py --preview` renders from the Mac mirror (needed `results/e9l/summary.json`, carried from Windows,
  sha `64e64e9318d442ec…`). Two "floor" phrases in the staged script predate 0058 and are corrected before the append;
  the entry gains the coverage pin's two renderings and the R8 dataset. R8 staging copy
  `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07/` (44 G, 569 files: `results/e9fl/` without `recheck/`, plus
  `mappers/<pair>/k1.*` and `results/mapper/<pair>/r2.json` in the upstream layout, per the campaign runbook §11).
- 20:1x card `README.md` + `SHA256SUMS` (569 lines) at the staging root (571 files; `summary.json` `1ac712b3…`, box final
  manifest `f538a17f…`). Dataset `hossainpazooki/linear-ceiling-e9fl-2026-10-07` created private by the operator;
  `upload-large-folder` (1 worker) began at ~60 MB/s inside the operator's own ssh session into the Mac.
- ~22:46 local **the home internet connection dropped**: the router reset every TCP session, the operator's ssh into the
  Mac included (the upload was its child and died), and all probes from Windows got `Connection reset by peer` for the
  better part of an hour while TCP/22 still opened. 23:50Z the Mac answered again: no upload process, resumable state
  intact (1,073 metadata files under `.cache/huggingface/`), 50 files already committed on the Hub. **Rule from it: run a
  multi-GB push detached (`nohup … caffeinate -i`), never as a child of an interactive session.** Restart = the same
  `upload-large-folder` line, detached, chained to the verifier.
- 23:55Z (Mac moved to Wi‑Fi; mDNS name now `Hossains-Mac-Mini.local`) the operator restarted the push detached, chained to
  `hf_verify_backup.py`, log `~/.cache/linear-ceiling/hf-upload.log`. The pasted block ran **twice** (a `read -s` prompt in a
  pasted block consumes the following pasted line), so two chains ran on one folder; the younger (pids 6283/6286) was
  stopped at 23:5x, the older kept its per-file resume state: 177 / 256 files, 11.6 GB of the first 24.5 GB batch, 69 MB/s.
  **Rule from it: a `read -s` line must be pasted alone, or the token goes in through a file descriptor the paste cannot
  reach.**
- **2026-10-08 00:04:23Z upload COMPLETE**: `hashed 571/571 (47.7G) | pre-uploaded 398/398 | committed 571/571`, 12 min
  40 s for the detached chain's share (two batches: 256 files / 24.5 GB, 142 files / 23.1 GB; 55–75 MB/s). The chained
  `hf_verify_backup.py` then died at interpreter start (`init_sys_streams … Bad file descriptor`): the `nohup bash -c` chain
  had no `< /dev/null`, so when the operator's session closed, Python had no stdin to initialise. Not a verification
  result — the verifier never ran. Re-run detached with stdin from `/dev/null`.
- 00:5x the Mac moved to Wi‑Fi at 192.168.1.26 (`Hossains-Mac-Mini.local` does not resolve from Windows; the old
  Ethernet address is gone from the neighbour table — address the Mac by IP). Operator ran the verifier detached
  (`< /dev/null`), token in the child's environment only, two separate pastes.
- **2026-10-08 01:31Z R8 BACKUP VERIFIED**: `hossainpazooki/linear-ceiling-e9fl-2026-10-07` (private) against the staging
  tree in both directions — `lfs-compared 398, downloaded+hashed 173, problems 0`. Token to be revoked by the operator (R9).
  Remaining: `append_0051.py` on the Mac (the summarizer runs again as its gate), two commits, push; Windows pulls and
  closes the docs.
- **~02:0xZ 0051 APPENDED on the Mac** (`appended 0051; chain 75a47a51de6e`, `ledger ok`), commits `91cea79` (ledger + the
  script version that rendered it) and `62982a8` (script retired). The Mac has no GitHub credential; rather than mint one,
  the Windows clone fetched the two commits over the LAN (`git fetch ssh://hossa@192.168.1.26/Users/hossa/dev/linear-ceiling
  main`), `ledger_check` passed on the fetched file, and the operator pushes from Windows. The Mac fast-forwards afterwards.

## 7. After the sitting

- Mirror: `~/dev/linear-ceiling/results/e9fl/` on the Mac (46 G incl. the three kept trees) is the evidence; the Hub
  dataset is transport. The staging copy `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07/` (44 G) can be deleted once
  the Mac mirror has a second local copy or the operator rules the Hub copy sufficient for that purpose. `~/hf-stage`
  (21 G of gated weights) stays for future Llama sittings; it holds no token.
- Open: the operator's HF token revoke (R9); PR #18 Q3's consequence in the MLSys draft (Llama enters as the second
  pair, now with a long cell too); the launcher's `sitting_b.*` naming is generic in function but short-cell in name.
- Issue #21 (2026-10-08, to @emersony99, the family's author): the record above in short, plus two asks — an R12 recompute
  of 0051 from the Hub mirror from a clean clone (as PR #6 did for 0040/0044; his read-only token for the October datasets
  already covers the private dataset), and whether he writes the second-pair section of the MLSys draft. Supersedes #15.
