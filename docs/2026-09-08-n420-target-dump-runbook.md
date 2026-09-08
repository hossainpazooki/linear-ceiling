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
