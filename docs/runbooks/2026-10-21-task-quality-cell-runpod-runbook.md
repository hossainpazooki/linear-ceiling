# Task-quality cell (draft 0063) GPU runbook — one rented 80 GB card on RunPod, the operator's registered run

**Date:** written 2026-10-21 (UTC evening), for a sitting not yet requested · **Status:** runbook; §6 is filled during
the sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating them and the sitting shape of
`docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md` (traps (a), (c), (d), (h), (i) apply unchanged). The
experiment is **draft 0063** (`docs/drafts/append_0063.py`, staged at `f80cfb6`, NOT on the ledger: it refuses to
append until 0061 and 0062 land). **No sitting is requested by this runbook**; it is written before the request so
the order, the inputs and the cost line exist when the entry is appended. Nothing below is a figure: every number is a
budget, a count or a pin, and the cost line is ASSUMED until the probe prints a time.

## 0. What the sitting is

Two runs of `tools/task_quality/cell.py` (`--cell long`, then `--cell short`): for each handoff above the item floor
the receiver's cache for R is built FRESH, by REUSE-ALL, by RANDOM and by REPAIR-f at the registered budgets (0047's /
0061's `core.py`), and under each cache every drawn item's question is appended after R and answered by greedy
decoding (chat and plain forms). Order per cell: the largest sender first (`cell_handoffs`) as the retained memory
probe, then descending sender length. Stopping rule: stop on any hash refusal or OOM; keep the completed prefix;
`--resume` continues only under the identity the report records (code, items, configuration, runtime, device). The
reading is descriptive (no band, no cell moves); the figures enter by their own entry from `cell.summarize` in-process.

## 1. The pod

RunPod, 80 GB card (A100 80GB PCIe community, or A100 SXM / H100 secure as priced at `up` time; both re-queried
immediately before `up`). Image `runpod/base:1.3.1-cuda1281-ubuntu2204`, container disk 60 GB (ephemeral — R5 is
load-bearing), host RAM ≥ 48 GB, 8 vCPU, ssh as `root` on the mapped port, no network volume. Billing stops only on
`terminate`. Pod name `linear-ceiling-tq`. Watchdog on every sitting after a campaign's first: `--kill <cap> --ttl
<hours>` passed explicitly (learning 2026-10-08: the defaults are a campaign-wide spend cap and `up --hours`).

| item | value | source |
|---|---|---|
| sitting ceiling | `--hours H × price`, H from §2's assumed cost plus the staging hour, re-set at `up` | `rp.py up --dry-run` |
| drain | 70 % of the sitting ceiling unless the probe's time moves it | `rp.py watchdog --exp tq --sitting-max <ceiling> --kill <cap> --ttl <H>` |
| 80 GB | the E-BEH family's design card; the long cell's largest sender (|S| 80,111) prefills at the same footprint as 0049 (peak 24.95 GiB with retries on an H100) | ledger 0047 / 0049 |

## 2. R2 — the budget (ASSUMED until the probe)

Per handoff: one sender prefill (|S| up to 80,111 tokens), one FRESH receiver prefill, five cache constructions
(REUSE-ALL, RANDOM, REPAIR-5/10/20 %: each the gap tokens recomputed against the assembled cache plus the copies), then
up to 41 items × 2 forms × 6 arms greedy decodes of ≤ 64 tokens with the cache cropped back after each. 0049's record
gives the only measured anchor: 35 handoffs × 3 arm passes in 92 minutes on an A100 80 GB. Scaling by passes
(6 constructions + 1 sender prefill per handoff against 0049's 4) and adding the decodes (about 500 per handoff, each
a question prefill of ~40 tokens plus ≤ 64 single-token steps against a 10k–25k-token cache) gives **3–5 h for the
long cell (25 handoffs)** and **1–2 h for the short cell (14)**; the probe replaces this bound with a time before the
drain is set. Items per handoff are capped at 40 by seed; a cheaper sitting halves the forms (chat only) by a config
edit BEFORE the entry is appended, never after.

## 3. R3 — everything the run reads, by sha

All git paths at linear-ceiling **`f80cfb6d3a3d40af54dd3ebcf800a5653f7bfe4c`** (LF bytes; this Windows checkout is
CRLF and the readers accept either rendering of an unchanged text file since 2c402e8). Hashes below are the
LF-normalized ones the draft pins (`linear_ceiling.hashing.sha256_text_file`); the driver records the same.

| input | sha256 (12) | pinned by |
|---|---|---|
| `config/task-quality-cell.toml` | `cce4326c0ed0` | draft 0063 |
| `tools/task_quality/items.py` / `pilot.py` / `cell.py` | `f5360038cef4` / `009ff9f04601` / `412b88a3d001` | draft 0063 |
| `tools/cache_behavior/core.py` | `f346b5fdf3d3` | 0047, 0061, draft 0063 |
| `results/task-quality/items-e9l.json` / `items-e9.json` | `8153e9d30d04` / `96499cb24cb8` | config `items_sha256`; draft 0063 |
| `results/e9l/report.json` (archive) | `084d9480af74` (raw) | verified e9l mirror (R6 2026-09-10); every alignment, score and per-token file checked by the driver against the items file or this report |
| `results/e9/report.json` (archive) | `1b2153e31245` (raw) | verified e9 record |
| model | `Qwen/Qwen3-1.7B` @ `70d244cc86cc` | config; public, no token on the pod |
| runtime pins | torch 2.14.0, transformers 5.17.0 (the pilot's) | recorded in `report.json` identity; a resume refuses a different version |

What the pod needs on disk, staged from the verified home mirrors (sizes from this machine): `results/e9l/{report.json,
align/ (24 MB), scores/ (1.6 MB), tokens/ (1.8 GB)}`, `results/e9/{report.json, align/ (8.5 MB), scores/ (1.1 MB),
tokens/ (727 MB)}`, `results/task-quality/items-e9l.json` (1.8 MB), `items-e9.json` (0.5 MB). The per-token archives
are read only for the repair ranking (token-mean δ_K); a `--prepare` step that writes the 60 per-handoff rankings into
a small pinned file is a possible later change to the driver and is NOT in draft 0063.

## 4. Steps

0. **Home, before anything bills:** 0061, 0062 and 0063 appended in that order (0063's script refuses otherwise);
   `tests/test_task_quality_cell.py` green in `.venv-cb`; the items files and archives above present at their hashes;
   this runbook committed so the clone carries it.
1. **Rent:** `rp.py price --min-gb 80 --limit 14`, then `rp.py up --gpu '<card>' --cloud <cloud> --price <p> --hours <H>
   --max-price <p+0.06> --disk 60 --name linear-ceiling-tq --verify-file ~/.cache/linear-ceiling/tq-verified.json --yes`;
   `rp.py wait-ssh`. Every `rp.py` call from Git Bash under `MSYS_NO_PATHCONV=1` with Windows-form local paths.
2. **Arm the net immediately:** `rp.py arm-deadman --ttl-min <60·H+30>` (may refuse on a community pod, trap (i)); at
   home `rp.py watchdog --exp tq --sitting-max <ceiling> --kill <cap> --ttl <H>` detached, log to the scratchpad.
3. **Stage:** tar the inputs of §3 at home (LF paths), `rp.py put <tar>`; on the pod `git clone` + `checkout f80cfb6`,
   venv with `tools/cache_behavior/requirements.txt` and `-e .`, weights by `snapshot_download` (public), untar under
   `/workspace/lc/results/`; `sha256sum` the two items files and the two archive reports against §3.
4. **Probe (R2, kept):** `setsid nohup env CUBLAS_WORKSPACE_CONFIG=:4096:8 python -m tools.task_quality.cell --run
   --cell long --output results/task-quality-cell/long --probe > ~/tq-long-probe.log 2>&1 < /dev/null & echo $! >
   /workspace/tq.pid`; record `peak_allocated_GiB` and the wall time of the largest handoff from `report.json` and
   the log into §6; re-set the drain from it.
5. **Run:** same line with `--resume` and without `--probe`, log `~/tq-long.<n>.log` (rotate per attempt); then the
   short cell into `results/task-quality-cell/short` (its own probe line first). Liveness from the `i/N` lines and
   `report.json` mtime, never from `pgrep -f`.
6. **Pull from the moment the driver starts** (R5): `rp.py pull --force-tar /workspace/lc/results/task-quality-cell results/`
   every few handoffs and at the end; verify at home by re-running `cell.summarize` (fail-closed) on each pulled tree.
7. **Home summarize (R11, the only reader):** `$PY -m tools.task_quality.cell --summarize --output results/task-quality-cell/long`
   (and `short`); a refusal is pasted verbatim into the closing brief. Write the verify file only after both pass.
8. **Release (R7):** listing pulled and hashed; `rm -rf ~/.cache/huggingface` on the pod; `rp.py terminate`; `rp.py status`
   reads the pod back as absent; `rp.py spend` into §6.
9. **Backup (R8):** `tools/hf_backup.sh --check`, push `results/task-quality-cell/` to a Hub dataset, verify by
   `tools/hf_verify_backup.py`; R9 token hygiene.
10. **Entry:** the figures entry (next free number at staging) calls `cell.summarize` in-process, asserts the report's
    hashes equal §3, and reads the headline, retention and sensitivity table; no figure is typed.

## 5. Traps (beyond the 2026-10-06 list)

(a) **Two output trees, one identity each.** `--resume` compares the report's identity (config, items, code, runtime,
device). A pod change between probe and run is a refusal, not a resume; start over in a fresh tree.
(b) **The reader re-reads the config from the clone**, not from the output tree: do not edit `config/task-quality-cell.toml`
on the pod or at home while a run or a summarize is in flight (learning 2026-10-16).
(c) **CPU `--run` is for the synthetic tests only**; the real cells are CUDA (`--device cuda` is the default).
(d) The per-token archives are 2.5 GB of staging; upload once, verify by `sha256sum` on the pod against the archive
reports, never by the local exit code (trap (h) of 2026-10-06).

## 6. Log (UTC; filled during the sitting)

(empty: no sitting requested)
