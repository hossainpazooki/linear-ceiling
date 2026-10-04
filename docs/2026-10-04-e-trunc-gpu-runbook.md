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

- (empty until the sitting)
