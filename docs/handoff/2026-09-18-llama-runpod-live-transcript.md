# Llama second-family RunPod campaign — live takeover transcript

**Status:** LIVE. Update this file at every major transition until the campaign is safely handed off.
**Operator date/time zone:** 2026-09-18, America/Toronto. **Secrets are intentionally omitted.**

## Objective and registered pair

Complete the registered Llama replication for
`meta-llama/Llama-3.2-3B -> meta-llama/Llama-3.1-8B`, pair key
`llama3.2-3b-to-llama3.1-8b`. Sitting A produces the generic KV dumps, k=1/4/8 mappers,
agent-text E8 arm, verified E8 report, and the pair's own tau calibration inputs. Sitting B is the
verdict-bearing E9 short cell; Sitting C is descriptive/cuttable long context. Do not rent B until the
post-A registration and tooling blockers below are closed.

## Repositories and immutable pins

- Linear Ceiling working tree: `/Users/emersonyu/Desktop/linear-ceiling/linear-ceiling`, branch
  `llama-second-family`, origin `https://github.com/hossainpazooki/linear-ceiling.git`.
- Pinned upstream checkout: `/Users/emersonyu/e9-repro/kv-transfer-replication`, detached at
  `06f8d55592570deae70c3feb9f84a75c4044fb03` (fork branch contains the Llama pair and descends from
  RoPE-spec commit `063f4023fdde67dedbee01a92518ce7f83f6cf5d`). Keep tracked upstream bytes read-only.
- Linear Ceiling commit used by the live scientific process:
  `cd91a477c3ff4e72b99db604006b8be997c76a5c`. Later commits change verifier/docs only, not the running
  estimator/config.
- Current pushed Linear Ceiling HEAD: `db01387`.

## Ledger and pre-registration

- Entry 0039 is appended and hash-chained (`prior-entries-sha256` begins `0c8bc66ba38a`). It registers
  Sitting A, no prediction seal, tau ceiling 0.45, absolute tau ladder `[0.10, 0.03]`, absolute prefix
  delta `1e-4`, and the BOS/tokenization caveat.
- Entry 0039 contains one factual prose error: it says five values were unresolved markers. In the
  committed configs only `tau_K`, `tau_V`, and `tau_agent_K` were markers; the ladder and prefix delta
  were already registered literals. `docs/drafts/append_0040.py` now emits an explicit append-only
  correction; do not edit immutable entry 0039.

## RunPod Sitting A — live state

- Pod id `4cxydvpwbyr1ix`, name `linear-ceiling-sitting-a`, secure cloud, NVIDIA A40 46,068 MiB,
  machine `9abgo2ybpf3t`, price `$0.49/h`, 200 GB container disk.
- Advertised 96 vCPUs are misleading for scheduling: cgroup quota is `765000/100000` = **7.65 CPUs**.
  The probe consumes ~763% CPU, so a second numerical job on the pod would contend rather than add
  throughput.
- Provider-side `terminateAfter` is armed. The RunPod credential could not arm an in-container
  `runpodctl` deadman. A home watchdog is running under `caffeinate` with sitting ceiling `$1.715`,
  campaign kill `$9`, TTL 3.5 h, poll 30 s. Command:

  ```bash
  .venv/bin/python tools/runpod/rp.py watchdog --sitting-max 1.715 --ttl 3.5 --warn 1.03 --kill 9.0 --every 30
  ```

- Live script: `/workspace/sitting_a.sh`; log `/workspace/sitting_a.log`.
- Launch timestamp from log: `2026-09-18T16:13:34Z`; probe began `2026-09-18T16:15:38Z`.
- Both generic dumps completed: source 23 s, target 48 s. Both record `rope_type=llama3` and
  `check_max_abs=5.960464477539063e-08` (< `1e-5`).
- Probe has three sequential readouts: `K_rope`, `K_stripped`, `V`, each 7,168 ridge fits. `K_rope`
  completed at `2026-09-18T16:44:00Z`; `K_stripped` completed at `2026-09-18T17:17:29Z`; `V` is
  currently running. The process PID at this
  writing is 4550. Do not interrupt while it remains healthy.
- Last observed spend at this writing: `$0.8728`; account balance `$10.3769`.

Monitor without dumping the large progress log:

```bash
.venv/bin/python tools/runpod/rp.py ssh -- \
  'ps -o pid,stat,etime,%cpu,%mem,rss -p 4550; \
   find /workspace/kv-transfer-replication/results/probe/llama3.2-3b-to-llama3.1-8b \
   -maxdepth 1 -type f -printf "%f %s %TY-%Tm-%TdT%TH:%TM:%TSZ\\n" | sort'
.venv/bin/python tools/runpod/rp.py spend
```

## Inputs and home-side overlap

- Deterministic token draw:
  `~/.cache/linear-ceiling/sitting-a-home/data/tokens/llama3.2-3b-to-llama3.1-8b_n50_len1024_seed0.npy`,
  SHA-256 `2a79dbe4c8b59f245d876426f2b930d36df8696c0dc9e91e9718ef220170af21`, shape `(50, 1024)`, int64.
- Clean traces archive: `~/.cache/linear-ceiling/sitting-a-home/traces.clean.tar.gz`, SHA-256
  `ae05a2660582363c6b7bec4f5effa469ded7c62e0e8b59c9e29341341d110afc`; extracted manifest check is
  188 files, manifest SHA `371fb4bf3cb089bdbca1588330f997199045426e84983e6ee6691b43fbc6a094`.
- Both model snapshots are cached under `/workspace/hf`; later processes run offline. The supplied HF
  token was streamed only into the download process, then unset; no token file exists under HF_HOME.
- To overlap network with CPU, the completed 3.0 GB generic dump tree was rsynced read-only into the
  final staging layout:
  `~/.cache/linear-ceiling/sitting-a-pull/pull/up/data/kv/llama3.2-3b-to-llama3.1-8b` (2.9 GiB on disk).
  The eventual box-written manifest remains authoritative; this pre-copy only lets final rsync resume.
- `/tmp/lc_sittingA_verified` must remain absent until `pull_verify_a.py` completes successfully.
- The retained failed-attempt log and launcher copy were pulled to
  `~/.cache/linear-ceiling/sitting-a-pull/preflight-logs/`; both local files match the pod at SHA-256
  `aa99046ec257b08d42a3388d562ae37f4de6fd9d94fa5ce410398f93a836bbad`.

## Sitting A failures already diagnosed and fixed

All failures occurred before a scientific report existed. Preserve this history; do not repeat them.

1. Unpinned dependency resolution installed a CUDA-incompatible stack: pinned torch 2.11.0+cu128,
   transformers 5.15.1, NumPy 2.5.2 (`07a8d83`).
2. Venv creation was not restartable: made idempotent (`25016aa`).
3. macOS AppleDouble trace metadata dirtied the clone: rebuilt clean archive and clean extraction.
4. RoPE guard expected the wrong JSON nesting: accept `rope.parameters.rope_type` (`fbd9f66`).
5. Probe invocation omitted the required pair: pass `--pair "$PAIR"` (`cd91a47`).
6. Fresh-clone rehearsal now fails visibly on install errors (`3084fb5`) and price is enforced after pod
   creation (`6a40e4e`). The final no-GPU rehearsal ended `SITTING_A_OK` at `6a40e4e`.

## Linear Ceiling changes after the live run SHA

- `5cc5c38`: align entry-0040 draft with entry 0039's no-seal ruling.
- `b4a42f2`: clarify no-seal and three-tau bootstrap documentation.
- `e6ee014`: fix `summarize_e8` to apply its registered `1e-6` tolerance to the nested archived
  cross-check instead of exact dict equality; added two regression tests. This was fixed before the E8
  report existed or any result value was inspected.
- `771f74e`: append-only correction machinery for entry 0039's three-marker/five-marker prose error.
- `f809adf`: harden the 0041/0042/0043 appenders and correct the E9 short/long runbook semantics.
- `db01387`: record the `K_stripped` probe milestone in this transcript.
- Last completed suite: **484 passed, 1 skipped**; ledger check green.

## Required completion sequence for Sitting A

1. Wait for the live script to print a single terminal `SITTING_A_OK`. Probe is followed automatically
   by k=1/4/8 mapper fit, E8 driver, and `/workspace/pull` packaging.
2. Before trusting the package, require terminal marker, nonempty manifest, and verify every box byte
   except the manifest's self-entry:

   ```bash
   .venv/bin/python tools/runpod/rp.py ssh -- 'set -eu
   term=$(grep -E "SITTING_A_(OK|FAILED)" /workspace/sitting_a.log | tail -1)
   test "$term" = SITTING_A_OK
   test -s /workspace/pull/MANIFEST.sha256
   cd /workspace/pull
   grep -v "  ./MANIFEST.sha256$" MANIFEST.sha256 | sha256sum -c -
   du -sh .
   find . -type f | wc -l'
   ```

3. Pull/resume and verify the explicit expected set and every SHA:

   ```bash
   .venv/bin/python tools/runpod/pull_verify_a.py \
     --local "$HOME/.cache/linear-ceiling/sitting-a-pull" \
     --pair llama3.2-3b-to-llama3.1-8b --exp e8f \
     --remote /workspace/pull --verify-file /tmp/lc_sittingA_verified
   ```

4. Once that interlock is written, terminate promptly to stop billing, then require `rp.py status` to
   show no pod. R8 backup is explicitly home-side and does not require the pod. A generic runbook section
   says to hold the pod for a home summary, but Sitting A's verifier and `rp.py terminate` were deliberately
   built to make verified-pull termination safe; cost-efficient path is verified pull, terminate, summarize.
5. Install the verified `pull/lc/` tree into this repo and `pull/up/` into the pinned upstream checkout
   using `rsync -a --checksum`, then re-hash installed files against `MANIFEST.sha256`. Upstream artifacts
   are operational/gitignored data; do not modify tracked upstream code.
6. Pin both home venvs from NumPy 2.5.3 to the box's 2.5.2 before the home re-score. Run
   `docs/drafts/append_0040.py` directly (avoid a redundant separate summary and preview); it runs
   `summarize_e8` in-process. Capture stdout, inspect the appended entry, retire the script in the same
   commit, run suite/ledger/E8 gate, push.
7. Reuse `results/e8f/recheck/generic_k1.json` as `tools/emit_tau.py --home-r2`; do not re-run the scorer.

## Post-A blockers before Sitting B

- Calibrate both E9 configs and transition `tests/test_llama_configs.py` from marker-state to calibrated
  state in the same commit.
- Run E9F/E9FL calibrations and align-only passes home-side; these write disjoint directories. Do not run
  two BLAS-heavy calibrations concurrently on the 18 GB home host.
- Append 0041 only after E9F calibration/coverage and committed config pass.
- RunPod-native Sitting-B runner and incremental pull verifier are being built in parallel in the shared
  working tree. They are not yet reviewed, committed, or rehearsed. Do not rent B until all three are done.
- B needs an 80 GB GPU, at least the registered 250 GB container disk, a unique terminate verification
  file, measured max `max(n_sender,n_receiver)`, and concurrent per-handoff pull/hash/delete. The short
  cell forbids partial close: finish or resume.
- Hostile review found two additional pre-rent gates. Every included alignment must have `n_matched >= 1`,
  and the first run-order handoff must have `n_matched >= 2` because the null control needs a derangement.
  Also, the wrapper must dispatch absent report -> plain run, incomplete report -> `--resume`, and complete
  report -> terminal success; a plain driver call over a complete report otherwise reruns it. Before
  retaining controls on resume, validate every identity/prefix/null artifact against its recorded hash.
- Home disk is currently roughly 76 GiB free before the rest of A lands. After E9F alignment, compute the
  exact kept-dump budget `sum(nS * 245760 + nR * 131072)` bytes before renting B.
- R8 backup has no Llama dataset/repo/card yet. It runs after pod termination from the verified home
  mirror. A dataset-scoped write token and explicit dataset creation are still prerequisites.

## Credential hygiene

Never paste either credential into commands, logs, this transcript, or git. The HF token and RunPod key
were supplied in chat and should be revoked after the campaign. The HF token has already served its only
Sitting-A purpose. Credential sweeps must search for actual `hf_...` token shapes and token files, not the
literal variable name `HF_TOKEN` that intentionally appears in checked-in scripts.
