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

- (pending the ledger commit and push)
