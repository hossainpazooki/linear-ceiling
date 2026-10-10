# E-TRUNC GPU runbook — one rented L40S, four levels in one sitting

**Date:** written 2026-10-04 (UTC evening), for a sitting not yet scheduled · **Status:** runbook; §6 is filled during
the sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating them. The experiment is entry
**0055** (registered 2026-10-04 at `a5c8691`, before any prefill; design `docs/drafts/e-trunc-design.md`, rulings in its
§10, limitations in its §9b); its figures enter by `docs/drafts/append_0057.py` from `summarize_e9_trunc` run in-process.
The shape is `docs/2026-09-10-e9l-gpu-runbook.md` (the E9-long sitting, same card, same instrument, same pins); the box
tooling is `tools/ec2/`, parameterised by `EXP` (its README). Nothing here is a figure: every number below is a budget or a
pin, and the entry reads its figures from the reader.

## 0. What the sitting is

FOUR runs of the E9 driver on entry 0036's 35 long handoffs under the same YaRN receiver, one per config, on one card,
in this order: `config/e9t-full.toml` (FULL, the control arm: 0035's instrument re-run under 0055's gate), then
`e9t-l65.toml`, `e9t-l49.toml`, `e9t-l32.toml` (the sender head-truncated to S[−L:] for L = 65,536 / 49,152 / 32,768).
Within a level the registered order is |S| DESCENDING (`[e9.order] by = "n_sender_desc"`): `django__django-11087_traj#152`
first, `astropy__astropy-7671_traj#85` last, so a stop leaves a scored prefix that contains the handoffs the higher levels
change. The reading (ruling 1) is pre-registered in 0055; the void gate (ruling 2, |M_∩| ≥ 2,000) and the deferred native
cell (ruling 3) are stated limitations. Memory is bounded by FULL (the same prefills as E9-long); the truncated levels are
cheaper.

## 1. The box

Same instance class, image, key and security-group pattern as the E9-long sitting (its §1): EC2 **g6e.4xlarge**, 1 ×
L40S 48 GB, us-east-1, Deep Learning Base OSS Nvidia Driver AMI, 250 GB gp3, ssh as `ubuntu`, self-halt 24 h after setup.
`LC_NAME=lc-e9t-<date> tools/ec2/box.sh up`; id, IP and the UTC times go in §6. Price was $3.00/h on-demand on 2026-09-09
and $3.00424/h on 2026-10-01; re-fetch at `box.sh up`. Nobody else shares the login; R7 step 0 still runs.

## 2. R2 — the budget

| quantity | value | how known |
|---|---|---|
| peak memory | **31.56 GiB** at |S| = 80,111 for the 1.7B under YaRN (E9-long runbook §6, the row 0036 cites); the four levels never exceed FULL's prefills | measured 2026-09-09 on the same card and pin |
| probe before launch | `EXP=e9t-full MAX_S=80111 ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py` → the 80,111 row must read `ok`; stop otherwise | `tools/ec2/probe_e9l.py` (reads `[e9.rope]` from the config; `[e9.rope]` is identical to e9l's) |
| driver time | E9-long scored its 35 in **80 minutes** (0036; 23:53:12Z → 01:13Z). 0055 states the four levels total **3.58×** E9-long's prefill tokens (two sender prefills + the receiver per handoff: FULL 3,970,435, L65 3,921,773, L49 3,596,221, L32 2,721,489; recomputed from `results/e9l/align/coverage.json` 2026-10-04), so ≈ **4.8 h** of driver time as an upper bound; the truncated levels run faster per token than FULL | 0055; coverage |
| cost | ≈ 6 h on the card including setup and release ≈ **$18–20** + egress ($0.09/GB; the kept dumps decide it) | prices above |
| kept dumps | whatever each config's `[e9.keep]` registers; read the four configs before launch and size the egress from E9-long's record (its kept set was 3 handoffs + the bridge dumps) | configs |

## 3. R3 — everything the run reads, by sha

| artifact | where | sha / pin |
|---|---|---|
| linear-ceiling on the box | `~/linear-ceiling`, detached at `LC_SHA` | the commit carrying this runbook (≥ `a5c8691`, which carries 0055) — fill in §6 |
| upstream on the box | `~/kv-transfer-replication`, detached | `063f4023fdde67dedbee01a92518ce7f83f6cf5d` (= every e9t config's `upstream_sha`; the RoPE-spec commit, as e9l) |
| `config/e9t-full.toml` | committed | `005d8d102deb743e…` (LF-normalized; `sha256_text_file`) |
| `config/e9t-l65.toml` | committed | `782f7354f4220757…` |
| `config/e9t-l49.toml` | committed | `d4d54381e3942b9e…` |
| `config/e9t-l32.toml` | committed | `3c0663fbb651ad50…` |
| `config/e7-manifest.json` | committed | `371fb4bf3cb089bd…` (LF-normalized); `e7_manifest check` on the box in setup.sh |
| traces | `~/linear-ceiling/traces/` from the home tarball (gitignored) | checked both directions + bytes by setup.sh |
| mapper (0029's n = 50 k = 1, byte-identical to e9l's) | `~/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1.{json,safetensors}` | `2fd05c333156…` / `cd6a8d939b36…` (setup.sh defaults) |
| alignment / coverage at home, per level | `results/e9t-{full,l65,l49,l32}/align/coverage.json` | `0b0419ea1d27…` / `c5c3b3d55828…` / `1120282c65b0…` / `d07606d8d3e8…` (raw bytes, 2026-10-04); the box's `--align-only` must reproduce each (`HOME_COVERAGE_SHA12` per level) |
| shrinkage pre-check at home | `results/e9t/shrinkage.{json,md}` | re-derivable by `summarize_e9_trunc --shrinkage`; 0055 states its figures |
| tau per level, at home, BEFORE launch | `results/e9t-<level>/calibration/tau.json` | `summarize_e9 --calibrate-tau --config config/e9t-<level>.toml` × 4 (the gate does not check it and the summarizer refuses without it — learnings 2026-09-14); ~2 min CPU each |
| box scripts | `~/setup.sh`, `~/run.sh`, `~/probe_e9l.py`, `~/release_sweep.sh` = `tools/ec2/*` at `LC_SHA`, LF | pulled back into each level's `logs/box/` by `pull.py` |
| models | `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-0.6B`, public, no token | HF cache on the box, removed at release |

What the box must print per level: `[bridge] <hid>: …` × 3 (the configs carry e9l's `[e9.bridge]`), then `[i/35] <hid>: …`
in |S|-descending order. Coverage each level's run must match: 68 observed · 35 included · 25 under the floor · 4 above the
cap · 4 empty receiver (0035's eight by name), identical across the four levels — truncation is applied AFTER inclusion
is decided on the full lengths (`e9_align.align`), so a level that excludes differently has the wrong config.

**Addendum 2026-10-08 (from the 0051 sitting's lesson, learning `a-registered-sha-pin-is-a-rendering`):** the four
`align/coverage.json` files above were written on Windows and are CRLF (1,029–1,030 CRs each); the shas in the table are
their raw renderings. The box's `--align-only` writes LF, and `setup.sh` compares the box file's sha to `HOME_COVERAGE_SHA12`,
so the launch must pass the **LF rendering**: full `5d01067ab8bb`, l65 `4d9cc526b1dc`, l49 `db8c32746a33`, l32
`a227bea0e058` (computed on the Mac mini, `tr -d '\r' | shasum -a 256`, 2026-10-08). Same 1,030-odd lines, two renderings;
**0055 pins the raw renderings at ledger lines 3417–3418**, so 0057 states both, derived from the bytes as 0051 did. Home side for this sitting = the Mac mini (`~/stage-e9t/`:
the four box scripts LF, `traces.tar.gz`, the Qwen k1 mapper `2fd05c33…` / `cd6a8d93…`; the Qwen archived dumps and
the four alignment passes carried from Windows and sha-verified, 615 files); the box = a RunPod 48 GB card (A40 secure
$0.49/h or RTX 6000 Ada community $0.74/h at 10-07 prices; L40S measured peak 31.56 GiB) reached through an `~/.ssh/config`
alias so `pull.py`'s port-less `ssh -i KEY user@host` works unchanged; AWS credentials are invalid (pickup 2026-10-07).

## 4. Steps

0. **Home, before anything paid:** `summarize_e9 --calibrate-tau` for each of the four configs (table above); confirm
   `results/e9t/shrinkage.json` exists (0055 read it); `git status` clean; this runbook committed so `LC_SHA` carries it.
1. **Home:** `tar -czf <scratch>/traces.tar.gz traces`; `LC_NAME=lc-e9t-<date> tools/ec2/box.sh up`.
2. **Upload** the mapper pair, the tarball and the box scripts (LF: `sed -i 's/\r$//'` first on a CRLF clone).
3. **`setup.sh` detached** with the level's environment:
   `setsid nohup env EXP=e9t-full LC_SHA=<sha> HOME_COVERAGE_SHA12=0b0419ea1d27 bash ~/setup.sh > ~/setup.log 2>&1 < /dev/null &`;
   poll `~/setup.rc`. It ends with `e9 --check --config config/e9t-full.toml` → ready, the alignment sha equal to home's,
   and the versions. Stop on any refusal. (The other three levels need only their `--align-only` + `--check` on the same
   box; run them after setup: `EXP=e9t-l65 …` etc., comparing each coverage sha to the table.)
4. **R2 probe** at 80,111 (table) → `~/probe.log`; record the row in §6.
5. **FULL:** `EXP=e9t-full bash ~/run.sh`; at home `BOX=… pull.py e9t-full` (hidden on Windows). Then `verify_mirror.py
   e9t-full` prints the report sha. Record launch / exit times.
6. **L65, L49, L32** the same way, one after another (`EXP=e9t-l65 bash ~/run.sh`, …). Each level is its own report,
   mirror, verification and log set; never two drivers at once on the card.
7. **Cutoff.** Each level's stopping rule is 0035's (`e9 --close-partial --config config/e9t-<level>.toml` at an operator
   cutoff whose reason may not depend on any score); the default is to let all four finish. A level closed partial
   shrinks `n_scored_at_every_level` in the comparison; the reader names what each level did not score.
8. **Release (R7)** as E9-long's §4 step 8: listing, mirrors re-verified from raw bytes, no tensor directory left under
   any `results/e9t*/` on the box, every log pulled and hashed, HF cache removed, `box.sh terminate` read back as
   `terminated`. Record the UTC time.
9. **Backup (R8)** from the verified home mirrors only: one dataset `hossainpazooki/linear-ceiling-e9t-<date>` carrying
   `results/e9t-{full,l65,l49,l32}/` and `results/e9t/` at the root (public or private, ruling 2026-10-04); verified by
   `tools/hf_verify_backup.py`. Token hygiene R9.
10. **Home:** `python -m linear_ceiling.summarize_e9_trunc` is the only reader (it runs `summarize_e9` on each level first,
    then the comparison → `results/e9t/compare.{json,md}`); a refusal is pasted verbatim into the closing brief. Then
    `append_0057.py --box "AWS EC2 g6e.4xlarge (1x L40S 48 GB), us-east-1, <instance id>" --launched <§6 FULL launch>
    --finished <§6 L32 exit> --dataset hossainpazooki/linear-ceiling-e9t-<date>`.

## 5. Traps carried forward

Everything in the E9-long runbook §5 (one launch line, liveness from `~/<EXP>.rc`, log rotation by `run.sh`, cu128 index,
LF box scripts, size-or-mtime re-pull). New here: (a) four `EXP` values share one box, so every `pull.py` / `verify_mirror.py`
/ `release_sweep.sh` call names its level, and `~/<EXP>.log` / `~/<EXP>.rc` are per level; (b) `HOME_COVERAGE_SHA12`
differs per level — a copy-paste of FULL's value into L65's setup makes the box refuse, which is correct; (c) the four
configs are CRLF on a Windows clone while every pin above is LF-normalized — hash with `sha256_text_file`, never
`sha256sum`, and never compare `read_bytes()` with `git show` (the 0050 append refused on exactly that, 2026-10-04);
(d) tau.json per level is a home-side prerequisite the gate does not check.

## 6. Log (UTC; filled during the sitting)

- 2026-10-08 15:35 Qwen-pair inputs and the four alignment passes carried Windows → Mac mini (615 files, all sha-verified);
  box scripts (LF), `traces.tar.gz`, k1 mapper staged under `~/stage-e9t/`. 15:4x operator detached the Mac's upstream
  clone at `063f4023` (the Qwen pin).
- 15:56–15:57 **step 0 done on the Mac**: `summarize_e9 --calibrate-tau` for all four configs → each level's
  `calibration/tau.json` written; every level's τ equals the registered Qwen tolerances (0023/0025: τ_K 0.3186, τ_V 0.4867,
  τ_agent_K 0.4371 — pins, not new figures); `e9 --check` → `E9 gate: ready` for all four configs. `bash -n` on the three
  box scripts, `py_compile` on the probe: clean. (`setup.sh` itself cannot rehearse on macOS — its torch pin is Linux-only;
  the box proves it, as the 0051 launcher did.)
- 15:58 RunPod: no A40 / L40S / RTX 6000 Ada listed; 48 GB only as RTX PRO 5000 Blackwell community $0.82 (an
  architecture the pinned `torch 2.11.0+cu128` has not run under in this program); A100-SXM4-80GB community back at $1.39.
  First `--dry-run` refused on the **campaign** cap (it still counts 0051's $4.86) — the cap must cover both sittings.
- 16:16–16:23 operator chose the community A100-SXM4-80GB at $1.39 for 7 h (`--disk 120`, then `--disk 100`; `--cap 15`;
  projected $9.73, campaign $14.59). `rp.py up` **refused six times** over seven minutes: "There are no longer any instances
  available with the requested specifications." By 16:23 the price list no longer carried that card at all (community A100
  only as 40 GB at $1.00; secure A100 SXM/PCIe 80 GB at $1.79, up from $1.59 at 15:58; RTX PRO 5000 Blackwell $0.82;
  H100 SXM secure $3.99). **No pod was created; nothing billed.** Card and price are the operator's call (R2) — the sitting
  waits on it.
- **16:26:57 operator: "go, secure A100 at 1.79, 7 hours" → `up` SECURE A100-SXM4-80GB $1.79/h, 7.0 h, disk 100, `--cap 18`:
  pod `w28h3vp07g8nnz` created**, `linear-ceiling-e9t`, start balance $18.65, sitting ceiling $12.53, campaign $17.39 vs
  cap $18. 16:27:54 `wait-ssh` OK → `root@154.54.102.27 -p 15131`; `arm-deadman` **NOT ARMED** (no pod-scoped
  credentials, as on every RunPod sitting so far) — the home watchdog is the only net. 16:28:53 watchdog supervisor up on
  the Mac under `caffeinate -i` (pid 7916, `--exp e9t-full --sitting-max 12.53 --every 60`; `pmset` shows sleep
  prevented). `~/.ssh/config` alias `e9tbox` (port 15131, `~/.ssh/id_rsa`) so `pull.py`'s port-less ssh works unchanged.
  Card `NVIDIA A100-SXM4-80GB, 81920 MiB, driver 580.126.16` (0044/0051's driver), overlay 100 GB, 128 vCPU, Ubuntu 22.04.
- 16:29:22–16:29:28 the seven staged inputs (`k1.json`, `k1.safetensors`, `probe_e9l.py`, `release_sweep.sh`, `run.sh`,
  `setup.sh`, `traces.tar.gz`) scp'd to the pod's `~`; `sha256sum -c` on the pod: all OK against the Mac's shas.
- **16:29:42–16:31:44 `setup.sh` EXIT=0** (`EXP=e9t-full LC_SHA=0d2c5a3b… HOME_COVERAGE_SHA12=5d01067ab8bb`): clones at
  `0d2c5a3` / upstream `063f4023` ✓, upstream env torch 2.11.0+cu128 / transformers 5.15.1 / numpy 2.5.2 ✓, pair from the
  pinned registry ✓, Qwen weights public (no staged cache; download at run time, the Qwen path unchanged), mapper shas ✓,
  `manifest ok` ✓, **`E9 gate: ready`** for `config/e9t-full.toml`, box alignment `results/e9t-full/align/coverage.json`
  sha256 `5d01067ab8bb…` **= the LF pin**, `cuda True NVIDIA A100-SXM4-80GB`.
- 16:32:13–16:35:06 the other three levels on the box: `--align-only` → coverage sha12 **l65 `4d9cc526b1dc`, l49
  `db8c32746a33`, l32 `a227bea0e058`** (each = its LF pin in the addendum); `e9 --check` → `E9 gate: ready` for all three.
- 16:32–16:35 **R2 probe** (`EXP=e9t-full MAX_S=80111`, ladder 32,768 / 65,536 / 80,111, YaRN 2.5, `sdpa_repeat_kv`):
  1.7B peak **31.56 GiB at 80,111 `ok`** (16.70 / 26.98 on the lower rungs; the 0036 figure to the hundredth), 0.6B
  23.40 GiB `ok`; `PROBE_E9L_DONE`; card idle after. Free card memory 78.83 GiB.
- **16:35:23 FULL launched** (`EXP=e9t-full bash ~/run.sh`, pid 2737, log `~/e9t-full.log`, exit to `~/e9t-full.rc`).
  16:35:43 home puller up on the Mac under `caffeinate -i` (`BOX=e9tbox BOX_KEY=~/.ssh/id_rsa LC_RESULTS=~/dev/linear-ceiling/results
  PULL_STATE=~/.lc-e9t-full-pull.json pull.py e9t-full`, log `~/.cache/linear-ceiling/pull-e9t-full.log`). Spend $0.27 at
  16:35:58Z; watchdog healthy.
- 16:36–18:27 FULL scored 18/35 at **255–370 s per handoff** (handoff 1 1,093 s with the controls) — about twice E9-long's
  1.5–3 min on the L40S. Diagnosis on the box at 18:28: GPU **0 %, 0 MiB** between prefills; `score_positions.py` at
  1,224 % CPU with **191 threads** against a cgroup quota of **13.6 CPUs** (`cpu.max 1360000 100000`; `nproc` says 128);
  `cpu.stat` `nr_throttled 34611 / nr_periods 71474` (48 % of periods throttled). The per-token scorer is CPU-bound and
  oversubscribed: `tools/ec2/run.sh` sets no thread cap, whereas `tools/runpod/sitting_b.sh` derives one from the cgroup
  quota for exactly this reason. Spend $3.60 at 18:27Z.
- **18:30:48 drained and relaunched:** `kill -TERM 2742` (the driver, by pid — the watchdog's own drain mechanism) and its
  scorer child 56708; `~/e9t-full.rc` EXIT=143; log rotated by `run.sh` to `~/e9t-full.20261008T183053Z.halt.log`;
  **18:30:53 relaunch** `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB _NUM_THREADS=13 EXP=e9t-full bash ~/run.sh --resume` (pid
  57459; 13 = quota ÷ period, the `sitting_b.sh` rule). The new scorer child runs 14 threads. 18:32:57 the resumed
  driver reports **19 kept from the checkpoint** (handoff 19 had finished scoring before the TERM; lost = the in-flight
  work on handoff 20 only). Note for 0057: handoffs 1–19 were scored under 191 threads and 20–35 under 13 — float32 reduction
  order may differ between the two, which is what 0028's re-score tolerance covers; the summarizer's checks decide.
  `/workspace/e9t-full.pid` written for the watchdog's drain (`run.sh` never writes it; `send_drain_signal` reads it).
- 18:39 handoffs 20–22 at the thread cap: **150 / 142 / 136 s** — E9-long's rate; the card was never the bottleneck.
- **18:40 near miss.** Reading the watchdog loop for the drain point: `rp.py watchdog --kill` defaults to **$9.00 of
  CAMPAIGN spend** (`camp >= a.kill` → terminate, no drain) and the 16:28 supervisor was started without `--kill`. Campaign
  spend read **$8.86 at 18:40:22Z** — about five minutes from a pod termination mid-FULL. `up --cap 18` does not reach the
  watchdog; 0051's sitting never crossed $9 because it was the campaign's first. 18:40:53 supervisor 7916 killed; the
  watchdog pair (7930 under `caffeinate -dimsu`) survived SIGTERM and took `kill -9` at 18:41:27; **18:40:56 new supervisor
  9935 → watchdog 9949 with `--exp e9t-full --sitting-max 12.53 --kill 18 --every 60`** (kill = the authorized campaign
  cap; the sitting ceiling unchanged). Unwatched window: none (the new watchdog was up 31 s before the old one died).
  → learnings candidate: the watchdog's `--kill` must be set to the campaign cap on every sitting after the first.
- 18:42 projection at the new rate: FULL ≈ 19:10Z, L65 ≈ 20:30Z, L49 ≈ 21:45Z, L32 ≈ 22:45Z, release ≈ 23:00Z at ≈ $11.7 —
  inside the $12.53 ceiling (kill 23:27Z) but across the watchdog's graceful drain at 70 % = $8.77 (≈ 21:21Z), which would
  SIGTERM the L49 driver into a partial. **Operator ruling 18:43Z: option 1 — `--no-drain --sitting-max 14.5 --kill 18`**
  (ceiling as a backstop, expected spend unchanged); no credit reload needed (balance $14.66 against ≈ $7.7 remaining).
- 18:43–18:45 three supervisor restarts to land it: (i) the kill loop over `$S`/`$W` did nothing — zsh does not word-split
  an unquoted variable (learnings 2026-10-08), the 18:40 watchdog stayed the net throughout; (ii) 18:44:11 supervisor 10111
  up with the new flags but printing **`TTL 7.0h`** — `up --hours` is also the watchdog's default TTL, so the pod would
  still have been terminated at 23:27Z; (iii) 18:44:50 restarted with `--ttl 8.1` (= $14.5 ÷ $1.79/h): **`sitting kill
  $14.50, account kill $18.00, TTL 8.1h`**, supervisor 10163. Restarts (ii) and (iii) each killed the old pair before
  starting the new one: two unwatched windows of about 3 s (18:44:08–18:44:11, 18:44:47–18:44:50); the 18:40 restart had none.
- **19:05:31 FULL driver EXIT=0** (`~/e9t-full.rc` mtime): 35/35 in the registered order, `[35/35] astropy-7671_traj#85 …
  107s`, 0 Tracebacks, `report.json` `complete: true`. Handoffs 23–35 ran 104–130 s. **`--launched 2026-10-08T16:35:23Z`;
  FULL exit 19:05:31Z** (wall 2 h 30 min, of which ≈ 55 min was the oversubscription). 19:06:24 home puller: `run complete
  and every kept directory is home; final mirror done; report.json sha256 5a7ab122fcc118837d6c6800692a216ab9ae8fed87b09f1489a331cb211abc1a`;
  2.3 G left under `results/e9t-full/` on the box (scores, tokens, align, bridge, controls; kept dumps deleted on receipt).
- **19:06:19 L65 launched** (`EXP=e9t-l65 bash ~/run.sh` under the 13-thread cap, pid 63429, scorer child 14 threads);
  `/workspace/e9t-full.pid` and `e9t-l65.pid` = 63429. 19:06:49 L65 puller up on the Mac (`PULL_STATE=~/.lc-e9t-l65-pull.json`,
  log `pull-e9t-l65.log`). Spend $4.74 at 19:05Z.
- 19:07:00 **FULL mirror verified on the Mac** (`verify_mirror.py e9t-full`): `report.json sha256 5a7ab122…  complete=True
  scored=35/35`; **529/529 fingerprinted files verified from raw bytes, 61,142,204,890 B; ALL VERIFIED**; 59 G under
  `results/e9t-full/`. Mac disk after: 168 Gi free (three more levels at ≈ 50 G each fit, with little margin).
- 19:07:55 `summarize_e9 --config config/e9t-full.toml` on the Mac (8-thread cap, log
  `results/e9t-full/logs/summarize_e9.20261008T1907Z.log`) → **`E9 SUMMARY REFUSED: config tau_V 0.4867056499055992 !=
  recomputed 0.48670564617346357`** within seconds. The recomputation is the Mac's (arm64): its `calibration/tau.json`
  carries K 0.3186442649443352 / V 0.48670564617346357 against the config's 0.3186442653116294 / 0.4867056499055992
  (K off by 3.7e-10, V by 3.7e-9; the check's tolerance sits between them). **Correction to the 15:56 line above:** the
  four τ passes "equal the registered tolerances" only to the four decimals the ledger prints; at full precision they are
  the Mac's renderings of the Windows-computed config values. The Llama cell passed on the same machine on 10-07 because its
  drift (K 2.5e-10, V 1.9e-11) fell under the tolerance. Windows cannot recompute today: `../kv-transfer-replication` sits
  at `0d27c68`, where the invoked upstream paths differ from the `063f402` pin, so the calibration refuses there. The
  sitting continues (the mirrors are the record; the reader is a home-side question).
- 19:10–19:14 `--calibrate-tau` re-run on the Mac at 1 thread and at 8: **identical** K 0.3186442649443352 /
  V 0.48670564617346357 / agent_K 0.4371020133925453 both times — a deterministic arm64 rendering, not thread-order
  jitter. The calibration's own checks against the archived `r2.json` and E8 arm (a) passed (those sit at `_TOL`); only
  the registered 1e-9 τ check (0023, ledger line 1308) fails, on V alone (relative 7.6e-9; K 1.2e-9 passes). Windows has
  17 G free, so the four mirrors (≈ 240 G) cannot move there either way.
- 19:12–19:16 **x86 diagnostic on the pod** (the E8 generic dumps, 2.8 G, the archived `r2.json` and `results/e8/report.json`
  shipped; `--calibrate-tau` under the pin, CPU, torch 2.11.0+cu128 / numpy 2.5.2): at 13 threads K 0.31864426521157985 /
  V 0.48670564997852195; at 1 thread K 0.3186442652698682 / V 0.4867056503322168. **x86 Linux does not reproduce the
  config's floats either, and moves with the thread count**; every x86 rendering sits within 1e-9 relative of the config
  (worst 1.2e-9 absolute on V at 1 thread, i.e. 8.9e-10 relative) while the Mac's V sits at 7.6e-9. The registered 1e-9
  is an x86 property, not a property of the archived mapper. Scratch calibration removed from the box; the shipped
  `r2.json` had overwritten the pod's committed copy (status `M`) and was restored from the git object before the next gate.
  Side finding: the Mac's (Windows-carried) archived `r2.json` is the **CRLF rendering** (758 CRs; `tr -d '\r'` sha
  `99177e9c…` = the committed object), and its raw sha `18d2276f…` is what 0023 pins at ledger line 1294 — the pin is a
  rendering, as 0051 found for coverage; content identical. Pod upstream tree clean again; `data/` is ignored.
- 19:17:48 L65 alive (pid 63429): three `[bridge]` lines done, controls on handoff 1 under way (18 G scratch); GPU idle
  between prefills as expected.
- **Operator ruling ≈ 19:50Z: "recommendation accepted" — entry 0059** (0028's shape: the τ recomputation tolerance 1e-9 → 1e-7
  in `_close`'s units; the τ the readings use stays the config's float). 19:40–19:52 the renderings captured as FILES the
  append script reads in-process: `results/e9t-full/calibration-x86/threads{13,1}/` (re-run on the box, `tau.json` +
  `r2.json` + `platform.json`; scratch calibration removed from the box again) and `calibration-arm64/threads{1,8}/` (the
  Mac); values as logged at 19:12–19:16 and 19:10–19:14. 19:5x `summarize_e9.py`: `_TAU_TOL = 1e-7` with the 0059 comment,
  `_check_calibration` now returns a `tau_recompute` block (config / recorded / recomputed / gaps / platform) that
  `summary.json` carries under `calibration` and `summary.md` prints; `tests/test_summarize_e9.py` gains
  `test_0059_tau_recompute_tolerance_is_1e7_relative_and_recorded`; `append_0057.py` asserts 0059 is on the ledger first;
  `docs/drafts/append_0059.py` staged (allocator: next free 0060). Windows cannot run the summarizer tests (the known
  `e9.py` fsync red: `os.fsync` on a read-only handle, `OSError: [Errno 9]`); on the Mac `tests/test_summarize_e9.py`:
  **40 passed**. 19:57 L65 at 13/35 (145–168 s per handoff), spend $6.27, campaign $11.11.
- **Mac disk, 19:57:** 124 Gi free; mirrors FULL 59 G, L65 44 G at 12/35 (its kept dumps already home). Three levels
  at ≈ 50–60 G each need ≈ 115 G more → single-digit margin. Reclaimable: `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07`
  (44 G, the e9fl R8 staging copy; the Hub dataset is BACKUP VERIFIED and `results/e9fl/` is the canonical mirror) — the
  operator's call.
- **19:58:12–20:00:37 `summarize_e9 --config config/e9t-full.toml` on the Mac under the 1e-7 check: rc 0, no refusal**
  (log `results/e9t-full/logs/summarize_e9.20261008T1958Z.log`; `summary.json` `62a6b69947b7…`): 35 scored of 35, bridge
  f* 0.0000 on all three, keep-subset re-score within 0028's tolerances (sums 4.5e-06, squares 5.7e-03), **tau recomputation
  (entry 0059): K 3.7e-10, V 3.7e-09, agent_K 0 on arm64 Darwin**, rule → HOLDS (FULL is 0036's instrument re-run; the
  figure enters by 0057, never here). 20:02 `append_0059.py --preview` on the Mac: first refused on its own assertion (the
  x86 renderings recorded the archived `r2.json` as the LF object `99177e9c…`, the Mac's as the CRLF checkout `18d2276f…` —
  the sha 0023 pins at line 1294); the script now derives both renderings from the pinned git object and accepts either;
  preview clean. Mac: full suite **596 passed, 3 skipped**, `ledger ok`, `scope ok` with the staged changes in place.
- **20:44:22 L65 driver EXIT=0** (`~/e9t-l65.rc` mtime): 35/35 in the registered order (`[1/35] django-11087_traj#152 … 575s`
  with the controls, then 103–185 s per handoff), 0 Tracebacks, `complete: true`; wall 1 h 38 min from the 19:06:19 launch.
  20:44:29 home puller: `run complete and every kept directory is home; final mirror done; report.json sha256
  b72a498690927fb5cfa2ac7aacc67078c6755009930b2d8507dc6db930f9374b`; 2.3 G left under `results/e9t-l65/` on the box. Spend
  $7.75, campaign $12.61 at 20:45Z.
- **20:45:28 L49 launched** (`EXP=e9t-l49 bash ~/run.sh` under the 13-thread cap, pid 77711, scorer child 14 threads;
  `/workspace/e9t-full.pid` = `e9t-l49.pid` = 77711); 20:45:58 L49 puller up on the Mac (`PULL_STATE=~/.lc-e9t-l49-pull.json`).
  Box disk 72 G free. 20:46:09 **L65 mirror verified on the Mac**: `report.json sha256 b72a4986…  complete=True  scored=35/35`;
  **529/529 fingerprinted files verified from raw bytes, 60,029,627,616 B; ALL VERIFIED**; 58 G under `results/e9t-l65/`.
  **Mac disk 109 Gi free** against ≈ 58 + 50 G for L49 + L32 — the staging-copy ruling is now load-bearing before L32's pulls.
  The staging copy shares no inodes with `results/e9fl/` (0 multiply-linked files of 1,715), so deleting it frees the full 44 G.
- 20:46:59–20:48:38 `summarize_e9 --config config/e9t-l65.toml` on the Mac → **`E9 SUMMARY REFUSED: identity control did not
  cover every sender position`**. Diagnosis from the records: L65's identity control has `n_pairs 65536`, `max_abs_square 0.0`,
  R² 1.0 — every position of the sender the level DUMPS (S' = S[−65,536:]); the alignment record keeps `n_sender 80111`, the
  FULL |S|, by 0055's design (inclusion and run order on the full sender). The reader compared the two. **Reader defect, driver
  correct**: `summarize_e9.py` now expects min(|S|, L) on a truncated level (`_dumped_sender_len`, used for the identity and
  bridge coverage checks; |S| elsewhere, existing cells unchanged); `tests/test_e9_trunc.py` gains a test that summarizes a
  truncated synthetic level. To be stated in 0057 as a reader correction, beside 0059.
- 20:50:56–20:53:00 **L65 summary under both reader fixes: rc 0, no refusal** (log `results/e9t-l65/logs/summarize_e9.20261008T2050Z.log`,
  `summary.json` `4dc6924d8ca2…`): prefix-invariance control max centered delta 0 over **65,536** positions, keep-subset
  re-score within 0028's tolerances, tau recomputation K 3.7e-10 / V 3.7e-09 / agent_K 0, rule → HOLDS (descriptive here;
  the level's figures enter by 0057 on M_∩). Mac: `tests/test_e9_trunc.py` + `tests/test_summarize_e9.py` **55 passed**.
- **22:12:53 L49 driver EXIT=0** (`~/e9t-l49.rc` mtime): 35/35 in the registered order (`[1/35] … 452s` with the controls,
  then 106–131 s per handoff), 0 Tracebacks, `complete: true`; wall 1 h 27 min from the 20:45:28 launch. 22:13:24 home
  puller: `run complete and every kept directory is home; final mirror done; report.json sha256
  c7535211d033265efa2ff349611c57444cab0646d9898f418b5879949ec27530`. Spend $10.34, campaign $15.17, balance $8.35 at 22:13Z;
  **Mac disk 59 Gi free** (L49's mirror ≈ 50 G; L32's is expected smaller, its sender being 32,768 tokens) — the
  staging-copy ruling still unanswered.
- **22:14:08 L32 launched** (`EXP=e9t-l32 bash ~/run.sh` under the 13-thread cap, pid 91117, scorer child 14 threads;
  `/workspace/e9t-full.pid` = `e9t-l32.pid` = 91117); 22:14:38 L32 puller up on the Mac (`PULL_STATE=~/.lc-e9t-l32-pull.json`).
  Box disk 70 G free. 22:14:48 **L49 mirror verified on the Mac**: `report.json sha256 c7535211…  complete=True  scored=35/35`;
  **529/529 fingerprinted files verified from raw bytes, 51,502,992,865 B; ALL VERIFIED**; 49 G under `results/e9t-l49/`.
  22:15–22:16:59 **L49 summary: rc 0, no refusal** (`summary.json` `23cfc8a0611e…`): prefix control 0 over **49,152**
  positions, tau recomputation K 3.7e-10 / V 3.7e-09 / agent_K 0, rule → HOLDS (descriptive here; figures by 0057).
- Timing at 22:17Z: the campaign kill at $18 is the binding ceiling (sitting $13.14 ≈ 23:47Z at $1.79/h). L49 took 87 min
  for 3.60 M prefill tokens; L32 carries 2.72 M (0055) → ≈ 66 min + controls → exit ≈ 23:25Z, final pull + R7 release
  ≈ 23:40Z: single-digit minutes of margin. Raising `--kill` is the operator's (campaign cap 18 was the ruling).
- **23:25:49 L32 driver EXIT=0** (`~/e9t-l32.rc` mtime): 35/35 in the registered order (`[1/35] … 345s` with the controls,
  then 102–108 s per handoff), 0 Tracebacks, `complete: true`; wall 1 h 12 min from the 22:14:08 launch. **`--finished
  2026-10-08T23:25:49Z` for 0057.** 23:26:29 home puller: `run complete and every kept directory is home; final mirror done;
  report.json sha256 c166d8f114271a936d1f3ce3409cff767e219528a246456f7b69f4493a35737d`. Spend $12.56, campaign $17.42,
  balance $6.09 at 23:26:48Z — ≈ 19 min to the $18 campaign kill (no ruling on raising it arrived); R7 release begins at once.
  Mac disk 21 Gi free after the four mirrors.
- 23:27:12 **L32 mirror verified on the Mac**: `report.json sha256 c166d8f1…  complete=True  scored=35/35`; **529/529
  fingerprinted files verified from raw bytes, 40,051,410,891 B; ALL VERIFIED**; 38 G under `results/e9t-l32/`. Mirrors:
  FULL 59 G / L65 58 G / L49 49 G / L32 38 G, 529 fingerprinted files each, all four ALL VERIFIED.
- **23:28:05–23:28:46 R7 on the box** (the sweep's steps run by hand in one ssh because `release_sweep.sh`'s single-level
  `OURS_FILES` would read the other three levels' logs as "foreign"; output in `results/e9t/release/box_sweep_20261008T2328Z.txt`):
  step 0 listing, no driver; step 2 **0 `layer*.npz`, 0 `*.safetensors` under any `results/e9t-*/`** on the box (kept dumps
  deleted on receipt; 2.0–2.3 G of small records per level left); step 3 box-side sha256 of 17 logs/scripts →
  `results/e9t/release/e9t.logs.sha256`, step 3b 222 small records per level → `e9t-<level>.records.sha256` (pulled home);
  step 4 no HF token file, 0 token-shaped strings in `~/*.sh ~/*.py ~/*.log`, no `.git-credentials`; **HF hub cache (5.2 G)
  removed**. The E8 generic dumps shipped for the x86 diagnostic sat under the ignored `data/` and died with the pod.
- **23:29:10 `rp.py terminate` → `terminate sent: w28h3vp07g8nnz` … `PROVEN GONE`**, after the home receipt
  `~/.cache/linear-ceiling/e9t-verified.json` (nonce- and pod-bound, the four verified `report.json` shas and the
  verification time) satisfied the interlock; `rp.py status`: `pods 0 (none — nothing is billing)`. **Final: sitting
  $12.60, campaign $17.42, balance $6.09** (≈ 17 min before the $18 campaign kill). Pod life 16:26:57–23:29:10 = 7 h 02 min.
- 23:30:24 watchdog **exited 0 (two consecutive polls saw nothing billing)**, supervisor stopped; no puller, no caffeinate
  assertion left on the Mac. Log check against the box's final hashes: every pulled log hash-identical except
  `launches.log` under FULL/L65/L49, which the box appended at each later launch (3/3/4 lines vs the final 5); L32's copy
  `8281ed06…` is the final one and lists all five launches (incl. the 18:30:53 `--resume`).
- 23:3x operator: "you may delete" the e9fl staging copy → `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07` (44 G, 1,715
  files, the 10-07 R8 staging whose Hub dataset is BACKUP VERIFIED) removed; `results/e9fl/` untouched.
  `tools/ec2/run.sh` now derives the CPU thread cap from the cgroup quota (the `sitting_b.sh` rule) and prints it in
  `launches.log` — the defect behind the 16:35–18:30 slow half.
- 23:31:45–23:33:21 **L32 summary: rc 0** (`summary.json` `eb12ae5b86ce…`): prefix control 0 over **32,768** positions,
  tau recomputation K 3.7e-10 / V 3.7e-09, rule → HOLDS (descriptive; figures by 0057). **23:33:21–23:41:04
  `summarize_e9_trunc`: rc 0, no refusal** — the four per-level summaries re-run in-process as the gate, then the paired
  comparison → `results/e9t/compare.json` `0572662307f3…` / `compare.md` (log `results/e9t/logs/summarize_e9_trunc.20261008T2331Z.log`).
  **The registered reading (ruling 1): L32's far-from-seam pooled median δ_K on M_∩ = 0.0868 against scaled-short 0.0381
  and long 0.0629 (FULL on the same tokens 0.1112), margin ±0.005 → "unattributed"** — and the value sits ABOVE both
  reference levels, not between them; the reader's label and that position are both to be stated by 0057. The step-10
  reader passed on the first run after the two reader corrections; nothing was pasted into a closing brief as a refusal.
- 23:4x the four learnings written (`docs/learnings/2026-10-08-{the-watchdogs-kill-default…, the-ec2-launcher-set-no-cpu-thread-cap…,
  a-registered-float-tolerance-is-a-platform-rendering…, a-reader-adapted-to-a-new-instrument…}.md` + index rows); every
  `re-verify:` line executed from the written file on Windows against the small records copied from the Mac
  (`results/e9t-*/report.json`, `results/e9t-full/calibration*/{tau,platform}.json`, `results/e9t/release/`).
- 23:42:04–23:48:47 **R8 staging built by hard links** on the Mac (`~/stage_e9t_r8.sh` → `~/dev/hf-staging/linear-ceiling-e9t-2026-10-08/`;
  no space cost, 72 Gi still free): `results/e9t-{full,l65,l49,l32}/` without `recheck/`, `results/e9t/` (shrinkage, compare,
  release hashes, logs), and the upstream INPUTS in the upstream layout per the campaign runbook §11 — `mappers/<pair>/k1.*`,
  `results/mapper/<pair>/r2.json` (the CRLF rendering the Mac read), `data/kv/<pair>/{source,target}` (the generic dumps the
  τ calibration reads, 2.7 G), `results/probe/<pair>/`. **2,891 files, 217,253,073,065 B; `SHA256SUMS` 2,891 lines**;
  credential sweep over every text file: planted control fires, **0 token-shaped files**. (The script's last echo was cut
  by `grep -l` exiting 1 on zero matches under `pipefail` — the 09-xx `grep -c` lesson in another coat; outputs complete.)
  Card `README.md` to be written last; the dataset must be PUBLIC (217 G > the 100 GB private allowance) — ruling pending.
  23:5x card written at the staging root (2,893 files with card and SHA256SUMS); the staging script kept as
  `tools/hf_stage_e9t_r8.sh`.
- 23:42:57–23:50:57 **`append_0057.py --preview` on the Mac: rc 0** — the four `summarize_e9` runs as its gate, then
  `compare_levels`; renders the Setup (box, launch/finish, pins), the coverage renderings, the two reader corrections with
  per-level identity coverage, the void gate (35 / 14 void / 21 enter / 154,620 tokens / ratio 0.6423), the per-level
  figures, the registered reading ("unattributed"; ABOVE both references, 0.0239 above the long level; FULL 0.1112 → L32
  0.0868 on the same tokens, paired −0.0257 [−0.0434, 0.0024]), the 0055 erratum (10 / 14 / 0), scope. **Skeptic pass
  dispatched 23:5xZ against the rendered text; the append waits on it and on R8.**
- ~00:05Z (10-09) **skeptic verdict: SURVIVES WITH CORRECTIONS — two wording items, no numeric error.** Every number
  recomputed from compare.json / shrinkage.json / the four report.json / the coverage bytes / the ledger (counts, the 14
  void ids in order, every 4-decimal figure, the pins byte-identical Windows↔Mac, the erratum's 10 / 14 / 0, the CRLF↔LF
  coverage pairs). Correction 1: 0055's reading paragraph says "between, unattributed" (the two references), which read
  literally does not cover 0.0868; 0055's ruling (1) sentence — `"unattributed" between the band and FULL's level` (ledger
  line 3423) — does (0.0868 lies between the long band's top 0.0679 and FULL's 0.1112). The script now cites that sentence
  by search, and only when the value lies in that region. Correction 2: "a shorter causal prefix lowers the late-position
  deviation on identical tokens" overstated — the paired per-handoff interval [−0.0434, 0.0024] includes zero; now
  "lowers the pooled far-from-seam median (0.1112 → 0.0868); the paired per-handoff interval includes zero, so no
  per-handoff direction is claimed". Not verifiable by the skeptic (no source named): pod id, driver, timestamps, R8 —
  these are this log's. 23:55:52–00:03:35Z **preview re-rendered after the edits: rc 0**; the reading paragraph now cites
  0055 line 3423 and states the pooled-median move with the zero-spanning paired interval. A doubled quotation mark around
  the cited sentence was fixed afterwards (code span); the append renders the final text.

## 7. After the sitting

- **R8**: the hard-link staging `~/dev/hf-staging/linear-ceiling-e9t-2026-10-08/` (2,893 files, 217,253,073,065 B, card at the
  root). **Operator ruling 2026-10-09 ~00:10Z: "public"** (217 G > the 100 GB private allowance; the 2026-09-11 reasoning —
  KV of public models over public benchmark traces). Push by the operator: `read -s HF_TOKEN` alone, then `export`, `hf auth
  whoami`, `hf repo create hossainpazooki/linear-ceiling-e9t-2026-10-08 --repo-type dataset` (public by default),
  `ALLOW_PUBLIC=1 tools/hf_backup.sh --check …`, then the push detached under `caffeinate -i` with `< /dev/null` (log
  `~/.cache/linear-ceiling/hf-upload-e9t.log`), ending in `BACKUP VERIFIED`; `unset` and revoke the token (R9). Home watcher
  armed on the log from Windows. **01:10Z push started** (pid 20928; `.gitattributes` commit, then the records step).
  **R9 slip, stated:** the push line I wrote used `nohup caffeinate -i env ALLOW_PUBLIC=1 HF_TOKEN=$HF_TOKEN bash …`, which
  puts the token into the ARGUMENTS of `env`/`caffeinate`, readable by `ps` on the Mac for the life of the upload and captured
  into the assistant session's transcript when the process list was read. The right form is a shell environment prefix
  (`HF_TOKEN=$HF_TOKEN nohup caffeinate -i bash …`) or the script's own `/dev/tty` prompt, which never reach argv. The token is
  fine-grained and scoped to this dataset; the upload is left to finish and the token is to be **revoked immediately after
  BACKUP VERIFIED** (R9 says revoked once pasted anywhere; the process list counts). Learnings entry 2026-10-09 written;
  operator: "local exposure is acceptable for today".
- **01:10:46–01:40:34Z R8 push and verification** (`hf_backup.sh`, log `~/.cache/linear-ceiling/hf-upload-e9t.log`): step 1
  the 33 small-record paths; step 2 the whole tree 01:11:59 → 01:36:55 (25 min for 217 GB — the receiver dumps are identical
  across the four levels and the Hub stores each blob once); step 3 the card; then `hf_verify_backup.py` both directions,
  LFS by `lfs.sha256`, the rest downloaded and hashed → **`BACKUP VERIFIED: hossainpazooki/linear-ceiling-e9t-2026-10-08`
  (PUBLIC) at 01:40:34Z**. The push log: `2,892/2,892 files checked, 2,292/2,296 uploaded (101GB transferred), 2,509
  committed in 8 commit(s)` then `Upload completed in 10 commits`; verifier `remote 2893 files | local 2893 files`.
  Independent probe from Windows 01:4xZ (anonymous API, `?blobs=true`): PUBLIC, **2,894 files on the Hub** (the 2,893 plus
  the Hub's `.gitattributes`), 2,296 LFS files; `README.md`, `SHA256SUMS`, the four `report.json`, `compare.json` present;
  `mappers/…/k1.safetensors` LFS sha `cd6a8d939b36…` = `SHA256SUMS`. Upload processes and the caffeinate assertion gone.
  **Token: revoke now (R9).**
- **0057 APPENDED 2026-10-09 ~02:5xZ** by the operator on the Mac (token revoked first; Mac pulled `da5f07a`): the gate re-ran
  the four summaries and the comparison, `appended 0057; chain 815cdcf5…`, `ledger ok (blocks unchanged vs HEAD)`; script
  retired; commits `fd76600` (append) and `ce89ef2` (retire) on the Mac, to be fetched into Windows over the LAN and pushed.
  Allocator lines (drafts README, CLAUDE.md) updated in the same close: nothing staged, next free 0060.
- Close brief: `docs/handoff/2026-10-08-e-trunc-0057-ran-on-runpod-from-the-mac-mini-four-levels-35-of-35-reads-unattributed-0059-appended-r8-pending.md`.
