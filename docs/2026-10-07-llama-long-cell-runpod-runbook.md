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
| linear-ceiling `LC_SHA` | the pushed commit carrying this runbook and the launcher change (§6 records it) | launcher `clone_exact` |
| mapper `k1.json` / `k1.safetensors` | `6cbfad42b6b0…27fb` / `fe77166a8ff4…69fc` (Mac = Windows = Hub) | launcher `sha256sum -c`; calibration names them |
| `results/e9fl/align/coverage.json` | `16121e677b97195cc1df9053f0e07d26302f12ae9994bbf96e016a1212b648f3` | box `--align-only` must reproduce it exactly |
| `results/e9fl/calibration/tau.json` | `dd3fca27e82affc937d70639b6d9428b811187c5354fb255eda4a9b991a0f604` | launcher `CALIBRATION_SHA256` |
| `traces.tar.gz` (Mac-built, 16,628,699 B) | `21fe358eae8b2c13…` | box `e7_manifest check` → `manifest ok` |
| Llama-3.2-3B snapshot `13afe512…` | `config.json` `35f063e9…`, `tokenizer.json` `79e3e522…` | staged offline (§3) |
| Llama-3.1-8B snapshot | **pending Meta's gate approval** (requested 2026-10-07 ~15:35Z) | staged offline (§3) |

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
4. Launch, detached: `setsid nohup env PATH=… EXP=e9fl CONTEXT_FLOOR=32768 DUMP_FREE_GIB=100 PAIR=… UP_REPO=… UP_SHA=…
   LC_REPO=… LC_SHA=… MAPPER_JSON_SHA=… MAPPER_ST_SHA=… COVERAGE_SHA256=… CALIBRATION_SHA256=… bash /workspace/sitting_b.sh`.
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
- next: Meta's 8B approval → `stage_llama_snapshots.py` rerun → `hf-cache.tar.gz` → operator pushes this commit → Mac
  `git pull` → `LC_SHA` = that head → §5.
