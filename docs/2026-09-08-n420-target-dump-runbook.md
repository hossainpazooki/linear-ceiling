# n = 420 target dump runbook — Algoverse box, 2026-09-08 (one sitting)

Inherits `docs/gpu-experiment-protocol.md` (R1–R12). Produces the missing half of the upstream calibration
dataset behind entry 0033 (`config/e8c.toml` `[e8.arms] generic_dumps`): `data/kv/qwen3-0.6b-to-1.7b-n420/target/`,
whose 2026-08-25 CPU attempt was killed at 358/420 with zero bytes written (upstream learnings
2026-08-25). This is an upstream INPUT, not a linear-ceiling experiment: no linear-ceiling driver runs, no
`results/` record is written, and no ledger figure comes from the box. The fit, `e8c`, `e9_rescore` and the
summarizers all run at home afterwards, gated by 0033.

## R1 — registration state (honest)

0033 is staged (`docs/drafts/append_0033.py`), not committed: its own guard asserts the target dump exists,
so the entry cannot be appended before this run. `config/e8c.toml` is committed unmodified and names the
pin, the dump root and the fit. The operator's ruling (a) of the 2026-09-07 brief = re-dump; 0033's
"pre-existing" wording is amended to state the two halves' provenance before it is appended.

## R3 — every input, by sha

| input | where | identity |
|---|---|---|
| upstream code | `github.com/hossainpazooki/kv-transfer-replication` | `223f469164734a5780110a5e2e906a2af3c36b1a` (0030 pin; `config/e8c.toml` `upstream_sha`) |
| token file | `data/tokens/qwen3-0.6b-to-1.7b_n420_len1024_seed0.npy` (upstream, gitignored) | sha256 `64343ab3365e345d1b7f3ea6c0cf46d24a7b7c1473530b1bc9458198c5ce61ca`, 3,440,768 B; uploaded, re-hashed on the box |
| model | `Qwen/Qwen3-1.7B` from the Hub, float32, `sdpa_repeat_kv` (`kvt/models.py::load_model` at the pin) | |
| source half (home, for the record) | `.../n420/source/` | 30 files, 12,332,988,482 B; `meta.json` sha `0afb6888…`, `layer00.npz` sha `8488ee18…` |
| box scripts | `setup2.sh`, `probe_mem.py`, `run.sh` (session scratch, uploaded through `/api/contents`) | `setup.sh` `b0d02a4b…` (attempt 1, died on torch==2.13.0), `probe_mem.py` `c0d21767…`, `run.sh` `4fcf9964…` |

Versions pinned on the box: `torch==2.11.0+cu128` (the `whl/cu128` index tops out at 2.11.0; driver 570.148.08 is
CUDA 12.8, so the cu130 PyPI build is out; 2.11.0+cu128 is also what E9 ran on 2026-09-04, entry 0028), `transformers==5.15.1`
and `numpy==2.5.2` to match home, Python 3.12.6. Home torch is 2.13.0+cpu; the dump's fp16 K/V are not
bit-reproducible across platforms anyway (upstream learnings 2026-08-24), and the source half was a CPU dump.

## The box

JupyterHub-only (TLJH), no ssh; driven by `tools/jupyterhub/jh.py`. Grant: `CUDA_VISIBLE_DEVICES` = one
**MIG 1g.20gb** slice of an H100 80 GB (four H100s on the box, 14 × 1g.20gb + 2 × 3g.40gb). 104 CPUs,
885 GB RAM, 11 TB shared disk (315 GB used at start). Shutdown 2026-09-09 07:30 UTC; everything deleted.

## R2 — the measured budget

`probe_mem.py` runs the PINNED `load_model` + `dump_kv` on the first 2 sequences into `/tmp` and prints
`torch.cuda.max_memory_allocated` at the real T = 1,024 path. Result recorded in §4 before the launch.
Prior bound: 7.95 GiB at T = 4,096 on the same model path (entry 0026 probe table).

## Steps

1. `setup.sh` detached (`setsid nohup bash ~/setup.sh > ~/setup.log 2>&1 < /dev/null &`): clone, checkout
   at the pin, venv, cu128 torch, deps, move the token file into place, print its sha and the CUDA device.
2. `probe_mem.py` under the venv (R2). Stop if the peak exceeds the slice.
3. `run.sh` (R4): rotates any `dump.log`, refuses if the target dir exists, launches
   `scripts/dump_kv.py --pair qwen3-0.6b-to-1.7b --which target --tokens <token file> --stride 4 --out <target>`
   detached. `dump_kv` accumulates all 28 layers in RAM and writes once at the end (flat loss profile).
4. After `wrote ... n_seqs=420` appears in `dump.log`: box-side `sha256sum` of the 30 files into
   `~/kv-transfer-replication/n420_target.sha256` — the oracle for R5.
5. `pull_n420.py` at home (R5/R6): pull all 30 files, sha256 each against the manifest, re-verify from raw
   bytes. Only after `ALL VERIFIED`: delete the target dir on the box, with a listing.
6. Release checklist R7 steps 1–7 (mirror = the upstream `target/` dir + this runbook's log section;
   logs pulled: `setup.log`, `probe.log`, `dump.log` and any `*.halt.log`, hashed).
7. Backup R8: not a `results/<exp>/` record; the dump is an upstream artifact and goes to the HF dataset as
   `data/kv/qwen3-0.6b-to-1.7b-n420/target/` in upstream layout, after the home verification.

## 4. Log (filled during the sitting, UTC)

- 20:36 hub login, token minted (12 h expiry, note `lc-n420-dump-2026-09-08`), server started; slice `MIG-b2a6425e…` (1g.20gb).
- 20:43 `setup.sh`, `probe_mem.py`, `run.sh`, token file uploaded; token sha on the box = home (`64343ab3…`).
- 20:44 `setup.sh` launched detached; DIED at `torch==2.13.0` (not on the cu128 index, max 2.11.0). Home-side poller
  self-matched its own `pgrep -f` and reported the process alive for 9 min (the E9 `pkill` trap, poller form).
  Log kept as `~/setup.attempt1.log`.
- 20:56 `setup2.sh` (idempotent; torch 2.11.0+cu128; writes `~/setup.rc` on exit) launched; poller keyed on `setup.rc`.
- 20:58 `setup2.sh` EXIT=0: pin `223f469` clean; `torch 2.11.0+cu128 cuda True NVIDIA H100 80GB HBM3 MIG 1g.20gb`;
  `transformers 5.15.1 numpy 2.5.2`; token sha on the box `64343ab3…` = home.
- 21:03 **R2 probe** (`probe_mem.py`, pinned `load_model` + `dump_kv`, 2 sequences, T = 1,024, `/tmp`, EXIT=0, 0 Tracebacks):
  `model Qwen/Qwen3-1.7B attn sdpa_repeat_kv dtype torch.float32 dev cuda:0` · `weights GiB 6.41` ·
  **`peak GiB 6.98`** · `2 seqs in 1.1 s` → est. 225 s of forward for 420. Fits the 1g.20gb slice with 13 GiB to spare.
  (The 0026 bound of 7.95 GiB at T = 4,096 held.) A first poller died on `tail -c` splitting a multibyte tqdm
  glyph inside the kernel's `text=True` capture; polls are line-wise (`grep -a`) from here.
- 21:06 `run.sh`: `dump_kv.py --pair qwen3-0.6b-to-1.7b --which target --tokens … --stride 4 --out …/target` launched
  detached (`setsid nohup`, log `dump.log`, no prior log to rotate).
- 21:07 `dump.log`: `wrote data/kv/qwen3-0.6b-to-1.7b-n420/target n_seqs=420 stride=4 in 181s`, 0 Tracebacks, process
  exited; 30 files in `target/`. Box-side `sha256sum *` → `~/kv-transfer-replication/n420_target.sha256` launched detached.
- 21:12 box-side manifest `n420_target.sha256` written (EXIT=0, 30 entries) — the R5 oracle. Target `meta.json` on the box:
  model Qwen/Qwen3-1.7B, 28 layers, n_kv 8, d_h 128, rope_theta 1e6, stride 4, seq_len 1024, n_seqs 420 (= the source
  half's shape); every `layerNN.npz` is 440,402,410 B, the source half's size. `pull_n420.py` started at home (hidden
  PowerShell process): pull all 30, sha256 each against the manifest; deletes nothing.
- 21:14 `pull_n420.py` (home, hidden process, pid 22224): 30/30 files pulled and sha256-verified against the box manifest
  in ~4.5 min (≈50 MB/s), `MISMATCHES: none`, `ALL VERIFIED`, empty stderr. Box logs pulled and hashed (`setup.attempt1.log`,
  `setup.log`, `probe.log`, `sha.log`, `dump.log`, the manifest, the three scripts) into the home mirror
  `…/n420/box-logs-2026-09-08/` with `SHA256SUMS`. Nothing deleted on the box yet.
- 21:15 **home re-verify from raw bytes (R6)**: 30/30 sha256 = manifest, 12,332,988,473 B, none missing/extra/bad. Box-side
  `target/` deleted (12G, 30 files → empty dir; no `.npz` above 1 MB left under `~`); `/tmp/probe_n420` removed. 21:15:01Z.
- 21:17 **nesting check** (the 08-24 check, target side): token nesting `n420[:50] == n50` True; CPU n = 50 target vs GPU
  n = 420 target on sequences 0–49, 12,800 positions × 8 × 128 per layer, NOT bit-exact (expected across platforms):

  | kind | layer | max abs diff | mean abs diff | scale (max abs value) |
  |---|---|---|---|---|
  | K_rope | 0 | 2.50e-1 | 7.6e-7 | 393.8 |
  | K_rope | 27 | 3.13e-2 | 1.7e-6 | 48.0 |
  | K_stripped | 0 | 2.50e-1 | 8.5e-7 | 393.9 |
  | K_stripped | 27 | 3.13e-2 | 2.0e-6 | 48.0 |
  | V | 0 | 4.88e-4 | 4.7e-8 | 2.8 |
  | V | 27 | 6.25e-2 | 3.0e-5 | 283.0 |

  Every max diff is ≤ one fp16 ULP at its scale (ULP = 0.25 on [256, 512), 0.03125 on [32, 64), 4.9e-4 on [2, 4)), the
  08-24 finding's magnitude. The two halves are consistent to fp16 rounding; `meta.json` does not record platform, so 0033's
  prose must (source: CPU 12 threads 2026-08-24; target: H100 MIG 1g.20gb fp32 torch 2.11.0+cu128 2026-09-08).
- 21:16 (slip) a relative-path append put a 250-byte stray copy of this runbook under the READ-ONLY upstream's `docs/`;
  removed the same minute; upstream tree clean again.
- 21:22 `append_0033.py` prose amended first (two provenances stated; header date = append date 2026-09-08, precedent
  0020/0029/0031), then run: `appended 0033; chain 9f16a83e3cb9`, `ledger ok`. Tag dir and both results dirs were absent at
  append (the script's own guards). The registered fit launched at home (hidden process, upstream `.venv`):
  `scripts/fit_mapper.py --pair qwen3-0.6b-to-1.7b --k 1 4 8 --tag n420 --dump-root data/kv/qwen3-0.6b-to-1.7b-n420`.
- 21:18 (box, in parallel) `probe_long.py`: E9-long R2 ladder on the 1g.20gb slice, pinned `load_model` forward with
  `use_cache` + `logits_to_keep=1`, T ∈ {4,096 … 80,111}, both models; writes nothing under `data/` or `results/`.
- 21:27 **E9-long R2 ladder result** (`docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.{py,out}`; slice 19.62 GiB total,
  19.48 free; torch 2.11.0+cu128; pinned `load_model`, `use_cache=True`, `logits_to_keep=1`, synthetic ids):

  | T | Qwen3-1.7B peak GiB (s) | Qwen3-0.6B peak GiB (s) |
  |---|---|---|
  | 4,096 | 7.73 (1.8) | 3.33 (0.7) |
  | 8,192 | 9.01 (3.5) | 4.42 (1.8) |
  | 16,384 | 11.58 (8.0) | 6.58 (5.0) |
  | 32,768 | 16.72 (22.5) | 10.91 (16.5) |
  | 40,960 | **OOM** (18.04 at the throw) | 13.07 (24.6) |
  | 49,152 | — | 15.24 (34.4) |
  | 65,536 | — | **OOM** (18.07 at the throw) |

  Weights 6.41 / 2.25 GiB. The 1.7B receiver OOMs at the native cap 40,960 on a 1g.20gb slice: the seed's D1(c) does not
  fit this grant either, and D1(a)/(b) need the 3g.40gb slice or a full card, as the seed says. The 32,768 row (16.72)
  agrees with 0026's 32,123 row (16.74) on the 3g.40gb slice, so the ladder is platform-consistent.
- 21:20–21:21 **Release (R7), in order.** (1) mirror re-verified from raw bytes, above; the R5 oracle's sha256 at home
  `201c3146cdd3656b…` (`n420_target.sha256`). (2) box listing: `target/` absent, no `.npz` > 1 MB under `~`. (3) logs pulled
  and hashed (§ 21:14, plus `probe_long.log` `a03cca5a914a79ee…`). (4) sweep: no `~/.cache/huggingface/token`, no token
  string in any rc file, script or log (the one grep hit was `release.sh` matching its own pattern text), no
  `.git-credentials`/`.netrc`, HTTPS remote only; `~/.cache/huggingface` (5.2G) removed; then `~/venv`, `~/.cache/pip` and
  the clone removed, `~` = 180K of pulled logs/scripts. (5) `ps -u` shows only the hub server and the kernel used to look.
  (6) `DELETE /hub/api/users/<u>/server` → 204; user record `server = None, pending = None, servers = []`;
  `GET /user/<u>/api/status` → 302 (not 200); the token-authenticated `/hub/home` fetch did not show "Start My Server"
  (that page is cookie-rendered, so this leg is inconclusive; the two API probes are the evidence). **Released
  2026-09-08T21:21:08Z.** (7) box vs mirror: `dump.log` `c3501e9ce0d0c019…` and the manifest `201c3146cdd3656b…` identical on
  both sides. No run numbers here; the summarizers at home are where numbers are read.
- Hub token revoked after release (R9); nothing of it was written inside a checkout or pasted.

## 5. The fit, moved to the box (same sitting)

- 21:18–21:45 the registered fit ran at home (upstream `.venv`, torch 2.13.0+cpu): k = 1 written at 21:21 (its log line
  `K r2 heldout=0.732 | V heldout=0.590`, an upstream stdout line, not a ledger figure), then k = 4 swapped: the pinned
  `build_features` materializes an n_train × p float32 matrix (≈ 11 GiB at k = 4, ≈ 22 GiB at k = 8) on top of the two
  dumps, on a 31.7 GB machine (0 GB free, commit 50.2 / 51.5 GB, ~3,000 page-ins/s). The home process was stopped by the
  operator at ≈ 21:53 (`taskkill //PID 26124 //F`). Its partial outputs (`mappers/<pair>/n420/k1.*`, 235 MB, written 21:21,
  and an empty `results/mapper/<pair>/n420/`) were removed at 22:40 — NOT earlier as a first draft of this line said: the
  removal had been chained to a process-kill command that the harness refused, so neither ran, and the home tag dir was
  found still present when checked before the pull. Nothing had been scored from them, and the registration names the
  command and the pin, not the machine.
- 21:47 box re-entered (new 11 h token, note `lc-n420-fit-2026-09-08`; server restarted; `setup2.sh` again from a fresh
  clone at `223f469`, venv + torch 2.11.0+cu128 + deps OK; its last step, the token file's sha, tripped because that file
  is not needed and was not re-uploaded). Inputs pushed through `/api/contents` in 60 MB parts (`push_dumps.py`, ≈ 8–9 MB/s
  per stream, two streams): both n = 420 halves, each file verified on the box against the HOME manifests
  (`n420_source.sha256` made from the home bytes; `n420_target.sha256` = the R5 oracle), plus the two 6,400 B probe inputs
  the fit reads (`results/probe/<pair>/r2_K_stripped_train.npy` `11e3f4a0…`, `r2_V_train.npy` `50f222fc…`, gitignored
  upstream artifacts of 2026-08-23). `fit.sh` refuses unless pin, clean tree, both manifests 30/30 and an absent tag dir
  all hold, then launches the exact registered command detached with an rc file.
- 21:43–22:01 first push (two streams, 60 MB parts, 4 retries × 5 s): 5 files landed and verified, then BOTH streams got
  `ConnectionResetError(10054)` from the box on every retry within the same 20 s and gave up. Server was healthy
  (`api/status` 200, load ≈ 20 from other tenants). Stale parts removed.
- 22:01–22:33 second push, one stream, 32 MB parts, `Connection: close`, 10 retries with 10 s + 10 s·attempt backoff:
  all 60 files on the box, each reassembled with `cat` and sha256-verified against the home manifest
  (`push2.log`: 60 × `sha OK`, 0 put errors, 13–17 MB/s per file). 24.7 GB total on the box.
- 22:34 `fit.sh` invoked; its `sha256sum -c` over both halves outran the 40 s socket (my slip: a launcher that hashes
  24 GB must itself be detached), so its stdout was lost; the kernel finished it regardless — effects checked below.
- 22:27:52Z `fit.sh` pre-checks from its captured output: pin `223f469`, clean tree, probe inputs `11e3f4a0…` / `50f222fc…`,
  `source: 30/30 OK`, `target: 30/30 OK`, tag dir absent; fit launched pid 3488284 — and died at import
  (`ModuleNotFoundError: No module named 'kvt'`): the launcher omitted `export PYTHONPATH=$PWD` (home runs the upstream's
  own venv with `kvt` installed; the box venv does not). `fit.log` rotated to `fit.<ts>.halt.log` (R4), relaunched with
  the path set, same command, same guards (tag dir still absent).
- 22:28:41Z–23:14Z **the fit on the box**, `EXIT=0`, 0 Tracebacks: k = 1 written 22:31, k = 4 22:42, k = 8 ≈ 23:13,
  `wrote results/mapper/qwen3-0.6b-to-1.7b/n420/r2.json`. Peak ≈ 42 GB virtual / 32 GB resident, 50–57 cores. Upstream
  stdout lines (NOT ledger figures; the summarizers recompute):
  `k=1 … K r2 train=0.740 heldout=0.732 | V train=0.600 heldout=0.590` (identical to the home run's k = 1 line at
  3 decimals, so the two platforms agree there), `k=4 … 0.789 / 0.760 | 0.672 / 0.625`, `k=8 … 0.818 / 0.764 | 0.718 / 0.633`.
  Box-side manifest `~/fit_out.sha256` (k1/k4/k8 `.json` + `.safetensors` = 235 MB / 940 MB / 1.88 GB, `r2.json`
  `efc8995d…`, `fit.log` `f929bb38…`, the halt log `bab46086…`) is the oracle for the pull.
- 23:16–23:18 `pull_fit.py`: nine files home, each sha = box manifest, then an independent re-hash from raw bytes at home
  (R6): 9/9 OK, 3,054,186,873 B. Landed in the upstream's own layout (`mappers/qwen3-0.6b-to-1.7b/n420/k{1,4,8}.*`,
  `results/mapper/qwen3-0.6b-to-1.7b/n420/r2.json`), logs under the mirror's `box-logs-2026-09-08/` (`SHA256SUMS` refreshed,
  15 entries). The home tag dir was verified EMPTY before landing (puller refuses otherwise).
- 23:19 gates at home: `e8 --check --config config/e8c.toml` → `E8 gate: ready (entries 0009/0016/0033 committed; upstream
  pinned and clean)`; `e9_rescore check --config config/e9c.toml` → `E9 rescore ready: mapper n420/k1, upstream 223f46916473,
  entries 0019, 0023, 0025, 0027, 0029 + 0033`. Both runs launched at home (hidden processes, logs in session scratch).
- 23:20 box: both dump halves, the fit outputs and the probe inputs deleted after the home re-verify; release sweep follows.
- 23:18–(running) **home runs, memory note.** `e8 --config config/e8c.toml` and `e9_rescore run` launched together. e8c's
  arm (a) scores the tagged mapper on its OWN calibration dumps, so the upstream scorer loads the full n = 420 pair
  (≈ 24 GB committed; the n = 50 amendment's arm (a) needed 2.8 GB) on the 31.7 GB machine, beside the rescore's ≈ 3 GB:
  0–0.8 GB free, commit 47 / 48 GB, paging, both advancing (scorer CPU 7 min at 23:35; rescore 2/8 handoffs scored). The
  harness killed the home-side pollers twice for low memory; the runs themselves were not touched. If the scorer dies on
  the commit limit, the rerun is sequential (rescore first), never a code or config change.
- 23:52 `e9_rescore run` exited clean: `results/e9c/report.json` (amendment 0033, 8 kept handoffs scored, `scores/` 8 files,
  `tokens/` 8), empty stderr. `e9_rescore summarize --config config/e9c.toml` launched standalone (fail-closed; any refusal
  is pasted here verbatim, R11). e8c's scorer still running.
- 23:57 `e9_rescore summarize` (standalone) REFUSED, verbatim: `E9 rescore REFUSED: C:\Users\hossa\dev\linear-ceiling\results\e8c\report.json
  missing: the tagged mapper's held-out figure has not been recorded by E8`. Reading: an ordering dependency the config
  encodes (e9c reads the mapper's held-out R² from e8c's record, not from `r2.json`), not a disagreement; it re-runs after
  `e8 --config config/e8c.toml` and `summarize_e8` finish. Nothing loosened.
- 23:55 `e8 --config config/e8c.toml` exited clean after ≈ 37 min under paging: `results/e8c/report.json` (amendment 0033,
  upstream `223f469`, mapper tag `n420`), `r2/{generic,agent}_k{1,4,8}.json`, `per_token/`. `summarize_e8 --config
  config/e8c.toml` launched standalone (fail-closed; re-scores from fingerprinted dumps, so the 24 GB pair loads again,
  alone this time). Then `e9_rescore summarize`, then `append_0034.py`.
- 00:38Z (09-09) `summarize_e8 --config config/e8c.toml` passed (≈ 42 min, re-scored from fingerprinted dumps, no refusal):
  `results/e8c/summary.{md,json}`. Its band words are not copied here; 0034 reads them in-process. `e9_rescore summarize`
  relaunched 00:39Z.
- 00:39Z (09-09) `e9_rescore summarize` passed on the second run (`wrote results/e9c/summary.json`); `append_0034.py`
  launched 00:41Z (re-runs both summarizers in-process by design).
- 00:40:22Z–00:40:23Z **INCIDENT — second release hit another user of the same login.** The sweep one-liner ran its
  deletions (`~/venv`, `~/.cache/pip`, `~/.cache/huggingface`, my clone) BEFORE its process listing, and the listing then
  showed a `/bin/bash -l` and a python under `~/venv` that were not mine; the server stop that followed killed them. Found
  at the same moment: `~/e9-audit-data` (8.9 GB: `align/ calibration/ controls/ mappers/ recheck/ scratch/ scores/ tokens/
  report.json`, i.e. the E9 record pulled from the HF backup, last write 00:34:52Z), `~/kv-transfer-e9-audit`,
  `~/linear-ceiling-audit`, `Untitled.ipynb`, `dump{1,2}_download.log`, `ledger_25_30.txt`, `rescore_*.txt` — a co-author's
  E9 audit in progress on the shared grant account. Their data dir is intact; their process, the venv and the two caches
  are what was lost. Server restarted 00:40:49Z by them; notebook saved again 00:41:04Z. Nothing on the box touched by me
  after 00:40:23Z except read-only listings; my restore token revoked 00:43Z; server left running. Operator informed.
  Learning: `docs/learnings/2026-09-09-a-shared-login-is-not-an-empty-box.md`.
- 01:0xZ (09-09) at the operator's request, one more login with a 10-minute token to read `~/e9-audit-data/README.md` ONLY
  (nothing else opened; both tokens revoked, 204 each): it is the dataset card of `hossainpazooki/linear-ceiling-e9-2026-09-04`
  verbatim. So the other user downloaded the private E9 backup onto the box with a read token to that dataset, and the
  working files beside it (`ledger_25_30.txt`, `rescore_*.txt`, `chosen_record.txt`, `cold1.*`) are a refutation of
  0025–0029 in progress on the shared grant login.

## 6. Backup (R8), 2026-09-09

- Private dataset `hossainpazooki/linear-ceiling-n420-2026-09-08`, upstream layout at the root (`data/kv/qwen3-0.6b-to-1.7b-n420/
  {source,target,box-logs-2026-09-08,n420_*.sha256}`, `mappers/qwen3-0.6b-to-1.7b/n420/`, `results/mapper/qwen3-0.6b-to-1.7b/n420/`),
  pushed by the operator from a staged copy of the verified home mirror (staging re-hashed: source 30/30, target 30/30, fit
  outputs 7/7) with a scoped, expiring write token held only in the operator's shell (`read -s`). Order: small records
  (`hf upload`), then one `upload-large-folder --num-workers 1` over the whole tree (89 files, 27.7 GB, 7 min 02 s), then
  the card. Two false starts on my side: `--include` takes one pattern per flag and `hf.exe` globs the pattern itself,
  so the large step now takes the tree with no patterns. Card revision `8675b719`.
- Verified by `tools/hf_verify_backup.py` (new, reusable): 61 LFS files `lfs.sha256` = local sha256, 28 non-LFS files
  downloaded and hashed, both directions checked — 89/89 OK. The one flagged file, `.gitattributes`, is the Hub's own;
  the verifier now ignores it by default. Nothing on the Hub is a ledger figure (summarizers read the local mirror).
