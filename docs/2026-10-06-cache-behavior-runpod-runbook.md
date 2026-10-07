# Cache-behavior (entry 0047) GPU runbook — one rented 80 GB card on RunPod, the operator's registered run

**Date:** written 2026-10-06 (UTC evening), for a sitting not yet started · **Status:** runbook; §6 is filled during the
sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating them. The experiment is entry **0047**
(registered 2026-10-04 at `55a5c47`, before any operator prefill); its figures enter by `docs/drafts/append_0049.py` from
`tools.cache_behavior.run.summarize` run in-process. The co-author's H100 pilot (`docs/2026-10-01-cache-behavior-h100.md`,
freeze `docs/2026-10-01-cache-behavior-freeze.json`) is the pilot 0047 names; nothing from it is a figure here. The box
tooling is `tools/runpod/rp.py` (the RunPod analogue of `tools/ec2/box.sh`, with the cost guardrails); the sitting shape is
`docs/2026-09-19-sitting-b-procedure.md`. Nothing below is a figure: every number is a budget, a count or a pin.

## 0. What the sitting is

ONE run of `tools/cache_behavior/run.py` over entry 0036's 35 long handoffs: fresh receiver prefill vs the assembled
same-model cache, with the two perturbation controls (norm-matched random, cyclic permutation), teacher-forced on the
recorded continuation; per-token KL and top-1 agreement; attention diagnostic on the final 32 receiver queries. Order:
the largest sender first (`ordered_records`: `django__django-11087_traj#152`, |S| 80,111, |R| 25,073) as the retained
memory probe, then the rest in manifest order. Stopping rule (0047, config `[stopping_rule]` in the freeze): stop on any
failed numerical control, archive bridge, hash check or OOM; keep the completed prefix; resume only under identical
code, inputs, configuration, runtime and GPU. The reading is descriptive (no band, no cell moves).

## 1. The pod

RunPod, **NVIDIA A100 80GB PCIe, community cloud, $1.19/h** at the 2026-10-06 listing (stock Low; fallback A100 SXM
secure $1.59/h, stock Medium; both re-queried immediately before `up`). Image `runpod/base:1.3.1-cuda1281-ubuntu2204`,
container disk 60 GB (ephemeral — R5 is load-bearing), host RAM ≥ 48 GB, 8 vCPU, ssh as `root` on the mapped port, no
network volume. Billing stops only on `terminate`; a stopped pod bills its disk. Pod name `linear-ceiling-cb`.

| item | value | source |
|---|---|---|
| account balance at write | $10.00 | `rp.py balance`, 2026-10-06 |
| sitting ceiling | `--hours 5.0 × $1.19 = $5.95`; campaign cap $10 (default) | `rp.py up --dry-run` |
| drain | 70 % of the sitting ceiling unless a measured hint moves it earlier | `rp.py watchdog` |
| 80 GB, not 48 | 0047: the pilot's 24.95 GiB peak **with allocator retries** on an H100 does not establish a 48 GB fit | ledger 0047 |

## 2. R2 — the budget

Measured on the pilot (H100 PCIe 80 GB, fp32, SDPA, YaRN 2.5, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, TF32 off,
deterministic algorithms): peak allocation **24.95 GiB with retries** on the largest case; 8,908 scored continuation
tokens over 35 handoffs. The retries are why an 80 GB card is specified rather than inferred. The probe here is the
driver's own `--probe` (the largest handoff only, written into the same output tree so its score is kept, not redone).
Compute is not on record for the pilot; the bound used for the ceiling is E9-long's 1.5–3 min per handoff on an L40S
times the A100's slower fp32 path with TF32 off → 1.5–4 h for 35 handoffs. A run that is still scoring at the drain
closes as a partial; `summarize` names what was not scored and 0049 refuses a partial by construction.

## 3. R3 — everything the run reads, by sha

All git paths at linear-ceiling **`7c9a5fd34c2df70c66269f755a61a882440e4f79`** (= `main`, the LF bytes; this Windows
checkout is CRLF and hashes differently — see trap (a)).

| input | sha256 | pinned to |
|---|---|---|
| `config/cache-behavior.toml` | `53c664556d18792401db8c1b930e487a90b88ab19c65ad94a1ab982094443a28` | = freeze `config_sha256` |
| `tools/cache_behavior/run.py` | `15e1ff8c1dbc7925398edc11ed68d91b6cdba4f335a49adcb29baa1b10729de5` | = freeze `source_sha256` |
| `tools/cache_behavior/core.py` | `f346b5fdf3d3feff5918e3a0e95f1e084f154317213ba68ce1913ec5acdcade5` | = freeze `source_sha256` |
| `config/e7-manifest.json` (corpus) | `371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094` | `manifest ok: 188 files match disk` at home |
| `config/e9l.toml` (archive config) | `bab1afca494cf8…` (full value in `results/e9l/report.json` `config_sha256`) | e9l report |
| `results/e9l/report.json` (archive) | `084d9480af74de2b038ce82f22bef3d2e5d477dc7243addf0c357d64b13aa9c8` | verified e9l mirror (R6 2026-09-10) |
| `results/e9l/SHA256SUMS` (evidence; 208 files: `report.json`, `align/`, `scores/`, `tokens/`) | `9c21ad089953f42bfae667c9844a2ade05c2070bc47da54a83ac622e56bc1b77` | written 2026-10-06 from the mirror |
| **`results/cache-behavior/inputs/manifest.json`** (prepared 2026-10-06 on Linux — WSL Ubuntu, Python 3.12.3, the LF clone `~/lc-lf`) | **`2aeee5769c0a3b557e1fecd43c2a745abe9f29c37af66b0eabb54358b4c35b22`** | `--check` in WSL and from the Windows LF clone `~/dev/lc-lf`: "Inputs and runtime verified: 35 handoffs" (the CRLF tree's own `--check` refuses it, trap (a)); the Windows-prepared manifest `f403dea7…` was discarded |
| model | `Qwen/Qwen3-1.7B` @ `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | config; downloaded on the pod, public, no token |
| runtime pins | torch 2.14.0, transformers 5.17.0, numpy 2.5.3, safetensors 0.8.0, huggingface_hub 1.32.0 | `tools/cache_behavior/requirements.txt`; `check()` refuses other versions |

Cohort from the prepared manifest: 35 handoffs, 0 excluded, Σ|S| 1,771,353, Σ|R| 427,729, Σ continuation 8,943 tokens
(the scored count is one less per handoff).

**The manifest is NOT byte-identical to the pilot's frozen `9a6f2923…`.** The four pinned digests match (config, corpus
manifest, archive config, archive report). The 35 record shas hash `np.savez_compressed` output, which is
**platform-dependent by one byte per zip entry**: Python's `zipfile` writes `create_system` 0 on Windows and 3 on Unix,
so a Windows prepare and a Linux prepare of the same inputs agree on every `.npy` member byte (35/35 verified) and on
none of the 35 `.npz` shas (0/35). The pilot prepared on Unix, so only a Unix-side prepare can match its record shas;
the inputs used here were prepared in WSL for that reason. The one field that cannot be reproduced from this side is
`evidence_sha256_manifest`, the sha256 of the evidence `SHA256SUMS` *file itself* — the co-author's private file, not in
the repository; 192 plausible `sha256sum` layouts were tried against the frozen hash with no hit. So 0047's sentence "the
operator's `--prepare` must reproduce it byte-for-byte" is not met. **This does not affect the run (R1–R8); it blocks
`append_0049.py`'s manifest assertion until the pilot's `SHA256SUMS` is obtained (then a WSL re-prepare should hit
`9a6f2923…` exactly) or a corrective reading pins the manifest by its verified fields.** Open, §7.

## 4. Steps

0. **Home, before anything bills (done 2026-10-06):** `.venv-cb` with the pinned requirements (torch 2.14.0+cpu);
   `tests/test_cache_behavior.py` 27 passed; `SHA256SUMS` written; `--prepare` from the LF clone `~/dev/lc-lf`
   (trap (a)); `--check` passed; dry run read. Commit this runbook so `LC_SHA` carries it.
1. **Rent:** `rp.py price --min-gb 80 --limit 14` (re-query), then
   `rp.py up --gpu 'NVIDIA A100 80GB PCIe' --cloud COMMUNITY --price 1.19 --hours 5.0 --max-price 1.25 --disk 60
   --name linear-ceiling-cb --verify-file ~/.cache/linear-ceiling/cb-verified.json --yes`; `rp.py wait-ssh`.
2. **Arm the net immediately:** `rp.py arm-deadman --ttl-min 330`; at home `rp.py watchdog --exp cb --sitting-max 5.95`
   detached, log to the scratchpad. The drain SIGTERMs the pid in `/workspace/cb.pid`; the pod keeps running for the pull.
3. **Stage:** `rp.py put results/cache-behavior/inputs.tar.gz` (the 36 prepared files, 304 MB; tar at home, LF paths).
   On the pod: `git clone https://github.com/hossainpazooki/linear-ceiling /workspace/lc && git -C /workspace/lc checkout
   7c9a5fd`; `python3.12 -m venv /workspace/venv && /workspace/venv/bin/pip install -r tools/cache_behavior/requirements.txt
   -e .` (CUDA wheels; `check()` compares the version string only); weights by
   `huggingface_hub.snapshot_download("Qwen/Qwen3-1.7B", revision="70d244cc…")` — public, **no token on the pod**;
   untar inputs to `/workspace/lc/results/cache-behavior/inputs`; `sha256sum` the manifest = `f403dea7…`.
4. **Check on the pod:** `python -m tools.cache_behavior.run --check --inputs results/cache-behavior/inputs` →
   "Inputs and runtime verified: 35 handoffs"; `nvidia-smi` row into §6. Stop on any refusal.
5. **R2 probe (largest handoff, kept):** `setsid nohup env CUBLAS_WORKSPACE_CONFIG=:4096:8 python -m
   tools.cache_behavior.run --probe --inputs results/cache-behavior/inputs --output results/cache-behavior
   > ~/cb-probe.log 2>&1 < /dev/null & echo $! > /workspace/cb.pid`; record `peak_allocated_GiB` from `report.json`.
   Output goes to `results/cache-behavior` (NOT `…/run`): `append_0049.py` reads `report.json`, `summary.json` and
   `inputs/manifest.json` from one tree.
6. **Run:** same line with `--run --resume`, log `~/cb.log` (rotate per attempt: `~/cb.<n>.log`), pid to `/workspace/cb.pid`.
   Liveness from the `i/35` lines and `report.json` mtime, never from `pgrep -f`.
7. **Pull from the moment the driver starts** (R5; ephemeral disk): every ~10 handoffs and at the end,
   `rp.py pull --force-tar /workspace/lc/results/cache-behavior results/` (local `rsync` is absent on this machine).
   Verify at home: every `report.json` `scores[*].sha256` against the pulled `.npz`; `inputs/manifest.json` unchanged.
8. **Home summarize (R11, the only reader), from the LF clone:** `cd ~/dev/lc-lf && ~/dev/linear-ceiling/.venv-cb/Scripts/python.exe
   -m tools.cache_behavior.run --summarize --inputs ~/dev/linear-ceiling/results/cache-behavior/inputs --output
   ~/dev/linear-ceiling/results/cache-behavior` (the CRLF tree's `digest()` of the config refuses, trap (a)); a refusal
   is pasted verbatim into the closing brief. Write `~/.cache/linear-ceiling/cb-verified.json` only after this passes.
9. **Release (R7):** listing of `/workspace/lc/results/cache-behavior` pulled and hashed; `rm -rf ~/.cache/huggingface`
   on the pod; `rp.py terminate` (refuses without the verify file); `rp.py status` reads the pod back as absent;
   `rp.py spend` into §6.
10. **Backup (R8):** `tools/hf_backup.sh --check` then push `results/cache-behavior/` to
    `hossainpazooki/linear-ceiling-cache-behavior-<date>` (public or private, ruling 2026-10-04); `tools/hf_verify_backup.py`.
    Token hygiene R9.
11. **Entry:** `append_0049.py --box "RunPod <cloud> NVIDIA A100 80GB PCIe, pod <id>, machine <id>" --launched <§6>
    --finished <§6> --dataset <R8 id> --preview` — refuses today on the manifest assertion (§3, §7).

## 5. Traps

(a) **CRLF.** `run.py`'s `digest()` hashes raw bytes; `config/cache-behavior.toml` and `config/e7-manifest.json` are
CRLF in this worktree (`core.autocrlf=true`), so a manifest prepared here carries digests the Linux pod's `--check`
rejects ("configuration changed after preparation"). And even from an LF tree, a Windows prepare yields `.npz` shas no
Unix machine can reproduce (§3, `create_system`). **Prepare on Linux** (WSL: `~/lc-lf` clone, `~/lc-venv` with the
pins, `HF_HOME` pointed at the Windows HF cache, `HF_HUB_OFFLINE=1`), then copy the inputs into the Windows tree. The
first two prepares of 2026-10-06 (CRLF tree; Windows LF clone) were discarded for exactly this.
(b) **The evidence digest** (§3): the SHA256SUMS file's own hash is in the manifest; a regenerated file is a different
manifest even when every listed hash is equal.
(c) `rp.py pull` calls a *local* `rsync`; pass `--force-tar` here.
(d) The watchdog drain reads `/workspace/<exp>.pid`; `--exp` defaults to `e9f`. Write the pid and pass `--exp cb`.
(e) `--probe` is `run()` over `order[:1]` into the same tree; the follow-up is `--run --resume`, whose identity check
(code, inputs, config, runtime, GPU name) must match the probe's — same pod, same venv.
(f) The sibling `tools/consolidation/prepare.py` (entry 0046) writes `config/consolidation-manifest.json` *into the
repository* and reads a hardcoded `~/Desktop/Carryover-evidence`; run it only in a scratch clone. From Windows it
diverges from the frozen manifest on all 126 record shas (same `create_system` byte) and writes a CRLF `texts.jsonl`;
**from WSL it reproduces the frozen manifest byte-for-byte (verified 2026-10-06, clean `git status` in `~/lc-lf`)**, so
0046's home-side inputs are the WSL ones at `~/Desktop/Carryover-evidence/a100/inputs` (WSL home), 60 texts, 126 `.npz`.
(g) No `--run` on CPU (`device.type != "cuda"` refuses); the home side only prepares, checks and summarizes.
(h) **Git Bash mangles leading-slash arguments**: `rp.py put … --dest /workspace/` reached `scp` as
`C:/Program Files/Git/workspace/`, the upload failed silently (exit 0 through a `tail`), and nothing landed on the pod.
Every `rp.py` call from Git Bash runs under `MSYS_NO_PATHCONV=1`; verify an upload by `ls -l` + `sha256sum` on the pod,
never by the local exit code.
(i) The dead-man has two independent failure modes here: `rp.py` writes its script with `Path.write_text` (CRLF on
Windows → `/usr/bin/env: 'bash\r'`), and this community pod's `runpodctl` has no working pod-scoped credentials, so
even the LF script REFUSES to arm. The home watchdog is the only net; keep its log open and the laptop awake.

## 6. Log (UTC; filled during the sitting)

- 23:39:49 `rp.py up` (A100 80GB PCIe, community, $1.19/h, 5.0 h, cap $10): **REFUSED by RunPod — "no longer any
  instances available with the requested specifications"** (the listing had shown stock Low). `status`: pods 0, nothing
  billing, balance $10.00. Inputs tarball `cb-inputs.tar.gz` 317,991,348 B sha256 `037855dde3cbc1ad…` ready in the
  scratchpad. Retry and fallback decision recorded below.
- 23:40:32 retry, same flags, after a fresh `price` listing (community: A100 PCIe $1.19 Low, A100 SXM $1.39 Low, H100 NVL
  $2.59 Low; secure: A100 PCIe/SXM $1.59 Low/Medium): **REFUSED again, same message**. Pods 0, $0.00. Every fallback row
  needs `--max-price` above 1.25, which the sitting procedure (§2 of 2026-09-19) makes an operator decision; taken back
  to the operator with the costs: A100 SXM community $1.39 × 5 h = $6.95; A100 secure $1.59 × 5 h = $7.95; cap $10,
  balance $10.00.
- 23:42 operator: "SXM community at 1.39". 23:42:34 `up` A100-SXM4-80GB community $1.39, default filters: **REFUSED**,
  same message. Cause per the 09-19 procedure: the create-time FILTERS, not stock — the defaults (host RAM ≥ 48 GB,
  8 vCPU, CUDA {12.8, 12.9, 13.0}) were sized for fp32 Llama-8B host loading and exclude hosts on 13.1+ drivers.
- **23:43:10 `up` with widened filters** (`--min-ram 24 --min-vcpu 4 --cuda 12.8 12.9 13.0 13.1 13.2 --disk 60`,
  none a registered quantity): **pod `mvwb1quo5c2hi1` created**, `linear-ceiling-cb`, A100-SXM4-80GB community,
  **$1.39/h**, machine `iklhq2d1mg0g`, start balance $10.00, sitting ceiling $6.95. 23:44:30 ssh up:
  `root@216.249.100.66 -p 22426`. Card `NVIDIA A100-SXM4-80GB, 81920 MiB, driver 595.71.05`; Ubuntu 22.04.5; python3.12.13,
  `uv`, git, `runpodctl` present; 60 GB overlay; host RAM 1,007 GB, 256 vCPU.
- 23:44:30 `arm-deadman`: **NOT ARMED** — `/usr/bin/env: 'bash\r'`. Cause: `rp.py` writes the dead-man script with
  `Path.write_text` (text mode → CRLF on Windows) before `scp`; same from the LF clone, since the bug is the write, not
  the checkout. Home `watchdog --exp cb --sitting-max 6.95` started 23:45 as the only net; dead-man re-armed by
  stripping `\r` on the pod (below).
- 23:45–23:48 inputs tarball uploaded (`cb-inputs.tar.gz`, 317,991,348 B). Setup script `cb-setup.sh` (LF) launched
  detached: clone at `7c9a5fd`, `uv venv` 3.12, pinned requirements, CUDA smoke test, `snapshot_download` of
  `Qwen/Qwen3-1.7B@70d244cc` (public, no token), untar, manifest sha check, `--check`. Exit code → `/workspace/setup.rc`.
  The first `put` of the tarball and of the script had gone nowhere (trap (h)); re-uploaded under `MSYS_NO_PATHCONV=1`,
  verified on the pod: 317,991,348 B, sha256 `037855dde3cbc1ad…`.
- 23:46:57–23:47:48 `cb-setup.sh`: clone at `7c9a5fd` ✓; venv `torch 2.14.0+cu130, cuda True 13.0, transformers 5.17.0,
  numpy 2.5.3` ✓; CUDA smoke test ✓; weights at `/workspace/hf/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc…` (3.8 GB) ✓;
  **`tar` exit 2** — all 36 files extracted but `chown` to the Windows uid 197609 failed in the container (`--no-same-owner`
  next time). Finished by hand: `chown -R root:root`, manifest sha `2aeee576…` ✓, `--check` → "Inputs and runtime
  verified: 35 handoffs" ✓. Dead-man: REFUSES on this pod (trap (i)); watchdog log shows sitting kill $6.95, warn $4.17.
- **23:50 R2 probe launched** detached (`--probe`, the largest handoff `django__django-11087_traj#152`, |S| 80,111),
  pid 1260 → `/workspace/cb.pid`, log `/workspace/cb-probe.log`, `HF_HUB_OFFLINE=1`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`.
  23:50:34–23:51:20 three `CUDACachingAllocator` "memory allocation failed with OOM … retrying" warnings (396–633 MB
  requests against ≤ 335 MB free of 85.09 GB) — the allocator-retry behaviour the pilot recorded; the process stayed
  alive, 45.8 GB resident at 23:52. Spend $0.21 at 0.15 h.
- **~23:55 probe EXIT**, 1/35 scored: `peak_allocated_GiB` **24.95** (= the pilot's figure on the H100, to the hundredth);
  controls `fresh_repeat` mean KL 0.0 / top-1 1.0 / max logit error 0.0, `prefix_copy` mean KL 2.4e-11 / top-1 1.0 /
  max logit error 0.00029 (limit 0.0005); 255 continuation tokens scored. ≈ 5 min wall for the largest handoff incl. load.
- **23:56 `--run --resume` launched** over the remaining 34 (same pod, venv, inputs, config → resume identity holds),
  log `/workspace/cb.1.log`, pid → `/workspace/cb.pid`. Home puller every 10 min (`pull --force-tar`), R5.
- **2026-10-07 ~01:22 driver EXIT: 35/35 scored, `complete: true`**, `summary.json` written on the pod; max
  `peak_allocated_GiB` over the 35 = **24.95** (the probe's largest case). ≈ 86 min for 35 handoffs on the A100 SXM.
  No control, bridge, hash or OOM failure (the allocator warnings were retries, not failures).
- 01:09–01:30 the home puller's `pull --force-tar` extracted NOTHING into `results/`: Python resolved `tar` to
  `C:\Windows\System32\tar.exe`, which read `/c/Users/…` as `C:\c\Users\…` and left a partial stray tree there
  (deleted). The pod kept billing idle from 01:22 until the manual pull (watchdog: $2.50 at 1.80 h). **Trap (j)**: on
  Windows, pull by `scp` of a single on-pod tarball and extract with `/usr/bin/tar` explicitly.
- 01:31 on-pod `tar -czf /workspace/cb-results.tar.gz --owner=0 --group=0 cache-behavior`: 332,507,779 B, 73 files
  (35 case `.npz`, `report.json`, `summary.json`, `inputs/` 36), sha256
  `3339e1b3a069bd1e2b8f3c55d75f669e6f60cd0ec228aacb56d0ff779094513b`; `scp` home, sha verified before extraction.
- 01:32 home, R5/R6: 73 files extracted; **35/35 case `.npz` match `report.json` fingerprints**; `inputs/manifest.json`
  still `2aeee576…` = `report.identity.manifest_sha256`; identity `{gpu A100-SXM4-80GB, torch 2.14.0+cu130, transformers
  5.17.0, cuda 13.0, cublas :4096:8}`, `git_commit 7c9a5fd`, `code_sha256` = the R3 table. Pod logs pulled and hashed
  (`cb-probe.log 9a146e1d…`, `cb.1.log 556993ee…`, `setup.log 4d5c7c06…`, `deadman.log 0decd473…`).
- 01:34 **R11 `--summarize` from the LF clone: PASSED** (rc 0; complete, scored 35, excluded []). The reader's figures
  are the entry's business (`append_0049.py` re-runs it in-process); recorded here only as the sitting's evidence that
  the reader accepted the run.
- 01:35 R7 sweep on the pod: no token file, no `HF_TOKEN`/`hf_…` in env or history; `/workspace/hf` removed; no
  `cache_behavior` process; results dir 318 MB / 73 files still on the pod until `terminate`.
- 01:34:11 verify receipt written (`~/.cache/linear-ceiling/cb-verified.json`: schema v1, this pod's nonce, `report_sha256
  3564605773bb…`, the tarball sha). **`terminate` sent; read back PROVEN GONE** (pods 0, nothing billing).
  **Sitting $2.57** (pessimistic `max(balance delta, elapsed × rate)`; balance $10.00 → $7.51), 1.85 h wall, of which
  ≈ 86 min compute and ≈ 12 min idle after the driver exited (trap (j)). Campaign $2.57 vs cap $10.
- **03:47:34Z R8 BACKUP VERIFIED**: `hossainpazooki/linear-ceiling-cache-behavior-2026-10-07` (created private by the
  operator) matches the staging tree `~/dev/hf-staging/linear-ceiling-cache-behavior-2026-10-07` in both directions —
  74 files: 70 compared by `lfs.sha256`, 4 downloaded and hashed, 0 problems. Staging was a COPY of the mirror (link
  count 1, not hardlinks), `results/cache-behavior/` at the root plus the card; credential sweep before the push caught
  exactly the planted control. Token: typed into the terminal for the push, `unset` after, revoke in the Hub UI (R9).

## 7. Open before 0049 can append

- **Ordering guard first:** `append_0049.py --preview` refuses with `ordering: 0048 present, 0049 absent` — 0048 (the
  0046 extension's figures, which needs the operator's 0046 run) is staged, not appended. 0049 is queued behind it by
  staging order. Re-sequencing (0049 before 0048) is an allocator decision: edit `PREV` in the draft and the README,
  nothing on the ledger moves.
- **RULED 2026-10-07 (operator), verbatim:** "0047's byte-for-byte clause is read as: every field of the operator's
  manifest that is pinned to the repository or the verified archive equals the pilot's freeze record; the evidence-file
  digest, which pins a private file, is excluded. The operator's manifest 2aeee576… is the one 0049 asserts." Applied to
  `docs/drafts/append_0049.py` (assertions on `2aeee576…` plus the four freeze-record fields; the reading stated in the
  entry text). The pilot author's files were requested in parallel for a field-level confirmation (GitHub issue, same day).
- *(superseded by the ruling above)* **Then the manifest assertion:** 0047's "byte-for-byte" sentence vs the unpinnable `evidence_sha256_manifest` field
  (§3). Either obtain the pilot's `SHA256SUMS` from its author (neuriv) and re-prepare on Linux (the 35 record shas
  will then match, §3), or record a reading that compares the manifest with that field masked (a draft-script change
  plus a sentence in 0049; 0047's text is immutable). Nothing else in the run is in question: every other identity
  field equals the frozen record and the summarizer passed.
- **R8 backup** (operator token): stage `results/cache-behavior/` and push; `--dataset` for `append_0049.py`.
- **0046's operator run** is the next sitting: inputs prepared on WSL reproduce the frozen `consolidation-manifest.json`
  exactly (trap (f)); card L40S/A100; the same RunPod path with traps (h)–(j) applied; ~3.5–6 h, ≈ $5–9.
