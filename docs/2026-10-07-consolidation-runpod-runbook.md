# Same-model extension (entry 0046) GPU runbook — one rented 80 GB card on RunPod, the operator's registered run

**Date:** written 2026-10-07 (UTC), for a sitting approved by the operator the same day · **Status:** runbook; §6 is filled
during the sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating them; copies the shape of
`docs/2026-10-06-cache-behavior-runpod-runbook.md` (the 0047 sitting) and applies its traps (h)–(j). The experiment is
entry **0046** (registered 2026-10-04 at `a941377`, before any operator prefill); its figures enter by
`docs/drafts/append_0048.py` from `tools/consolidation/summarize.py` run in-process over the verified home mirror. The
co-author's A100 pilot (`docs/2026-10-01-a100-analysis.md`, provenance `docs/provenance/2026-09-30-a100/`) is the pilot
0046 names; nothing from it is a figure here. Nothing below is a figure: every number is a budget, a count or a pin.

## 0. What the sitting is

THREE runs of `tools/consolidation/run.py --model <name>` on one card, in the registered order and with the registered
pause: **`qwen17_bridge`** (Qwen3-1.7B on the 6 bridge texts: shortest / middle / longest sender of each original cohort)
→ pull → **home `summarize.py --bridge-only` must pass** → **`qwen4`** (Qwen3-4B, all 60 texts) → **`smollm3`**
(SmolLM3-3B, all 60 texts, YaRN 2.0 / 65,536). Each model: a 1,024-token full-vs-chunked control first
(`control_max_delta` 1e-4), then the **real longest sender as the memory probe**, then the rest; fp32, SDPA, TF32 off,
256-token chunks with the full causal KV retained; per-handoff compact `.npz` + one raw K/V witness per model (the
shortest included sender). Descriptive: no hypothesis row, no verdict (0046). Resume refuses a changed code commit,
runtime, GPU or dtype — so all three models run on ONE pod, and a pod loss restarts the unfinished model from scratch.

## 1. The pod

RunPod, **80 GB A100** (PCIe community $1.19/h first; SXM community $1.39/h second; both re-queried before `up`; a
secure-cloud row at $1.59/h is a new price and goes back to the operator). Not the entry's "L40S 48 GB expectation": the
R2 arithmetic (§2) puts the 4B's largest case at ≈ 43 GB, inside a 44.4 GiB card's noise, and the driver's resume rule
makes an OOM on model 2 a restart on a different card, which is the expensive failure. Image
`runpod/base:1.3.1-cuda1281-ubuntu2204`, **container disk 120 GB** (scratch K/V memmaps for one 80K-token handoff of the
4B are ≈ 31 GB on disk, transient), host RAM ≥ 24 GB, 4 vCPU, CUDA 12.8–13.2, pod name `linear-ceiling-cons`, no volume.
Balance at write $27.41 (operator recharge); 0047 spent $2.57; campaign cap raised to **$15** for this sitting
(`--cap 15`), sitting ceiling `--hours 6.0 × price`.

## 2. R2 — the budget (arithmetic, no pilot peak on record)

The pilot document records no peak memory. Per token of retained KV, fp32, K+V:
Qwen3-4B 36 layers × 8 KV heads × 128 × 4 B × 2 = **295 KB** → 81,920 tokens = **23.6 GB**, plus fp32 weights 16.1 GB,
plus the SDPA chunk workspace (256 queries × 80K keys × 32 heads × 4 B ≈ 2.6 GB) ≈ **43 GB**.
SmolLM3-3B 36 × 4 × 128 × 8 = 147 KB/token → 11.8 GB + 12.3 GB weights ≈ 25 GB. Qwen3-1.7B 28 × 8 × 128 × 8 = 229 KB/token
→ 18.4 GB + 6.9 GB ≈ 26 GB (E9-long measured 31.56 GiB for the same model under its own driver). The driver scores the
real longest sender first, so each model's peak is reached in its first minutes; `peak_allocated_GiB` per handoff goes
into the report and §6. Disk: the pod writes sender + receiver memmaps per handoff (4B, longest: 23.6 + 7.4 GB) and
deletes them after scoring; witnesses (one per model, the shortest sender, ≈ 1–2 GB each) and compact records
(squares `n × layers × heads` float32, ≈ 90 MB for the longest) stay — expect **≈ 10–15 GB to pull**.
Wall-clock: ≈ 2.4 M sender tokens per full model in fp32 with TF32 off; 3.5–6 h for the three on an A100 was the
estimate; the bridge model is minutes. Home mirror disk: 61 GB free on C: before the sitting; fine.

## 3. R3 — everything the run reads, by sha

All git paths at linear-ceiling `main` **`d4d48a1`** (the 0047 close; `run.py` / `capture.py` / the two configs
unchanged since 0046's registration — the LF bytes below are what 0048 asserts).

| input | sha256 (LF / registered) | pinned to |
|---|---|---|
| `config/consolidation.toml` | `857cc92320cb6adc…` | 0046 (frozen from PR #8) |
| `config/consolidation-manifest.json` | `99185c5891fcebd1…` | 0046; `texts_sha256` `32d2217549275c9d…` |
| `tools/consolidation/run.py`, `capture.py` | `sha256_text_file` at HEAD; asserted by `append_0048.py` as `code_sha256` | 0046 |
| **prepared inputs** (`a100/inputs/`: `texts.jsonl` + 6 + 60 + 60 `.npz`) | every record sha = the frozen manifest's (126/126); `texts.jsonl` = `texts_sha256` | prepared **2026-10-07 in WSL** by `tools/consolidation/prepare.py` from the e9s/e9l records; reproduces the frozen manifest byte-for-byte (0047 runbook trap (f)); tarball `cons-inputs.tar.gz` 10,249,304 B sha `164971f52a407bed…` |
| archive records `archive/records/{e9s,e9l}/` (`report.json` + `align/`) | the verified e9s/e9l mirrors | home side only (summarizer's bridge comparison) |
| models | `Qwen/Qwen3-1.7B@70d244cc…`, `Qwen/Qwen3-4B@1cfa9a72…`, `HuggingFaceTB/SmolLM3-3B@a07cc9a0…` | config; `download.py`, public, **no token on the pod** |
| runtime | `tools/consolidation/requirements-linux.lock` (torch 2.14.0, transformers 5.17.0, numpy 2.5.3; the lock's torch wheel is cu130) via `setup.sh` (`uv pip sync`) | 0046 cites the lock |

Home mirror skeleton `results/consolidation/` built before renting: `provenance/` (the two files by `git show HEAD:`,
LF, hashes above), `archive/records/`, `a100/inputs/` (the WSL inputs), `a100/results/` (empty until the pulls),
`SHA256SUMS` written after the final pull over every file in the mirror.

## 4. Steps

0. **Home, before anything bills (done 2026-10-07):** inputs prepared in WSL and checked against the frozen manifest;
   mirror skeleton; tarball; this runbook. Commit this runbook so the sitting's `LC_SHA` carries it.
1. **Rent** (`MSYS_NO_PATHCONV=1` on every `rp.py` call, trap (h)): `rp.py price --min-gb 80 --min-ram 24 --min-vcpu 4`,
   then `rp.py up --gpu 'NVIDIA A100 80GB PCIe' --cloud COMMUNITY --price 1.19 --max-price 1.45 --hours 6.0 --disk 120
   --min-ram 24 --min-vcpu 4 --cuda 12.8 12.9 13.0 13.1 13.2 --cap 15 --name linear-ceiling-cons --verify-file
   ~/.cache/linear-ceiling/cons-verified.json --yes`; on refusal the SXM row at 1.39; `wait-ssh`.
2. **Arm the net:** `rp.py watchdog --exp cons --sitting-max <price×6> --every 60` at home immediately (the dead-man
   does not arm on community pods, trap (i)).
3. **Stage:** `put cons-inputs.tar.gz` and `cons-setup.sh` (verify size + sha on the pod); setup detached: clone at
   `d4d48a1`, `UV_BIN=/usr/bin/uv CARRYOVER_VENV=/workspace/venv bash tools/consolidation/setup.sh` (lock sync + CUDA
   smoke), `HF_HOME=/workspace/hf python tools/consolidation/download.py` (three public snapshots, ≈ 17 GB), untar
   inputs to `/workspace/inputs` with `--no-same-owner`, check the manifest hashes against the clone's frozen manifest.
4. **Run 1 — `qwen17_bridge`:** `setsid nohup env HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 /workspace/venv/bin/python -u
   tools/consolidation/run.py --model qwen17_bridge --inputs /workspace/inputs --output /workspace/out > /workspace/cons-bridge.log
   2>&1 < /dev/null & echo $! > /workspace/cons.pid`. The 1,024-token control and the longest sender are its first two
   steps (R2 row into §6).
5. **Pull + home bridge check (the registered pause):** on-pod `tar -czf /workspace/out-bridge.tar.gz -C /workspace/out
   qwen17_bridge`, `scp` home (trap (j)), extract into `results/consolidation/a100/results/`, write a provisional
   `SHA256SUMS`, then from the LF clone `python tools/consolidation/summarize.py --evidence
   ~/dev/linear-ceiling/results/consolidation --bridge-only`. It must pass (bridge within `bridge_mean_relative_tolerance`
   0.01 / `bridge_fstar_absolute_tolerance` 0.01 of the archived e9s/e9l values) before run 2 starts; a refusal stops
   the sitting and is a finding.
6. **Runs 2 and 3 — `qwen4`, then `smollm3`**, same line, logs `cons-qwen4.log`, `cons-smollm3.log`, pid file rewritten
   each time. Liveness from the report's `scores` count and `nvidia-smi`, never `pgrep -f`.
7. **Final pull:** one tarball of `/workspace/out` (three model dirs incl. witnesses), `scp`, sha compared, extract into
   `a100/results/`; verify every `report.json` `scores[*].sha256` and `witness` hash; write the final `SHA256SUMS` over
   the whole mirror (`<sha>  <relpath>`, LF).
8. **Home summarize (R11):** `summarize.py --evidence results/consolidation` from the LF clone → `verified: true`; a
   refusal is pasted verbatim into the closing brief. Then `append_0048.py --preview` (expect the ordering guard: 0048's
   `PREV` is 0047, which IS appended, so this one may render; it asserts one GPU and one runtime across the three models).
9. **Release (R7):** no token on the pod (none was ever there), `rm -rf /workspace/hf`, listing hashed, verify receipt
   written, `terminate`, `status` reads back absent, `spend` into §6.
10. **Backup (R8):** stage a COPY of `results/consolidation/` with a card; `tools/hf_backup.sh --check` then push to
    `hossainpazooki/linear-ceiling-consolidation-2026-10-07`; `tools/hf_verify_backup.py`; token hygiene R9.

## 5. Traps

All of the 0047 runbook's (a)–(j), plus: (k) `prepare.py` must never run in the main tree or the Windows LF clone — it
overwrites `config/consolidation-manifest.json`; the Windows LF clone `~/dev/lc-lf` carries that overwrite as an
uncommitted modification and the mirror's provenance files come from `git show HEAD:`, not from a worktree.
(l) `run.py` imports `capture` from its own directory and records `git rev-parse HEAD` of the clone — run it from the
repo root of a real clone at the pinned commit. (m) The three models must share one GPU name and one runtime
(`append_0048.py` asserts both); a pod loss means a new pod with the same card class and the same lock.
(n) The bridge pause is registered sequencing, not a convenience: do not start `qwen4` until the home check passes.

## 6. Log (UTC; filled during the sitting)

- 03:56:36 `up` A100 80GB PCIe community $1.19 (widened filters, `--disk 120`, `--cap 15`): **REFUSED** ("no longer any
  instances"), as in the 0047 sitting. 03:56:37 `up` A100-SXM4-80GB community **$1.39/h**: **pod `9rlzui4nli6uup`
  created**, `linear-ceiling-cons`, machine `zwtqdin590js`, start balance $27.41, sitting ceiling 1.39 × 6 = $8.34.
  03:56:39 ssh up `root@216.249.100.66 -p 22279`. Note: `rp.py` prints `campaign total $-10.27` because the operator's
  recharge moved the balance above the campaign's start balance; the guardrail uses `max(balance delta, elapsed × rate)`,
  so the elapsed-time figure governs — the cap still binds.
- 03:57 home `watchdog --exp cons --sitting-max 8.34` started (the dead-man does not arm on community pods, trap (i));
  `cons-inputs.tar.gz` + `cons-setup.sh` uploaded under `MSYS_NO_PATHCONV=1` (10,249,304 B, sha `164971f52a407bed…`
  verified on the pod), setup launched detached.
- 03:58:39–04:00:11 `cons-setup.sh` rc 0: clone at `d4d48a1` ✓; frozen manifest in the clone ✓; `setup.sh` lock sync →
  `{torch 2.14.0+cu130, transformers 5.17.0, numpy 2.5.3, cuda 13.0, gpu A100-SXM4-80GB}`, CUDA smoke ✓; `download.py`
  CACHED all three revisions (18 GB, public, no token); inputs 126/126 match the frozen manifest; disk 28 GB used / 93 GB free.
- 04:01 **run 1 `qwen17_bridge` launched** detached (pid → `/workspace/cons.pid`, log `/workspace/cons-bridge.log`).
- **04:05:55 run 1 EXIT, `COMPLETE qwen17_bridge`**: control (1,024-token full vs chunked) max delta K 0.0 / V 0.0
  (limit 1e-4); 6/6 texts; per-text peak GiB `24.93` (the longest sender, 80,111 tokens — the R2 row; arithmetic said ≈ 26),
  8.32, 12.28, 13.81, 14.48, 18.18; seconds 126, 15, 22, 32, 33, 45. One allocator-retry warning on the last text, no failure.
- 04:06–04:10 pull: on-pod `out-bridge.tar.gz` 3,237,592,222 B (the raw witness dominates), sha `adc09c1672285aa9…` equal on
  the pod and at home, 11 files into `results/consolidation/a100/results/qwen17_bridge/`; `SHA256SUMS` written over the
  whole mirror (416 files, LF, posix paths).
- 04:10 home `summarize.py --bridge-only`: first attempt failed on a PATH (bash expanded `~` to `/c/Users/…`, which Windows
  Python cannot open — pass `C:/…`); second attempt refused because the mirror's `archive/records/<cohort>/` lacked
  `scores/` and `tokens/` (the bridge comparison re-derives the archived per-token deltas from them; `prepare.py` needed
  only `report.json` + `align/`) — copied from the verified e9s/e9l mirrors, `SHA256SUMS` rewritten (536 files).
- **04:12 home `summarize.py --bridge-only` PASSED (rc 0)** from the LF clone: every bridge row within the registered
  tolerances (`bridge_mean_relative_tolerance` 0.01, `bridge_fstar_absolute_tolerance` 0.01): 12 rows (6 texts × K/V),
  max `relative_mean_gap` **1.2e-5**, max `max_fstar_gap` **0.0** (budgets, not figures; the entry reads them from the
  summarizer). The registered pause is satisfied.
- 04:13 **run 2 `qwen4` launched** detached (log `/workspace/cons-qwen4.log`, pid file rewritten).
