# Seed — E9 scaled short cell: 0029's 25 handoffs under 0036's receiver configuration

**Date:** 2026-09-13 · **Status:** DONE 2026-09-14 — 0037 appended (`c360950`), run on a rented L40S (runbook
`docs/2026-09-13-e9s-gpu-runbook.md`), figures in entry 0038; this seed is kept as written below, and
nothing here is a ledger figure. Written by the builds-and-review session for the session that runs GPU sittings
(`tools/ec2/` over ssh, or `tools/jupyterhub/` on the grant hub). Every value under *verified* was read this
session from the ledger, the summarizer outputs or the code, with the source beside it; every item under *proposed*
is a choice the operator rules on. Inherits `docs/gpu-experiment-protocol.md` R1–R12 without restating them.
Companion: `docs/2026-09-11-gpu-runs-after-the-pivot.md` (item 1) and outline v3 §5.2/§6.

## 0. The question

The paper's two cells differ in receiver configuration as well as length. 0029 measured the 25 short handoffs on the
native receiver; 0036 measured the 35 long ones on a receiver scaled by static YaRN 2.5. The bridge control in 0036
showed that YaRN alone moves the content key by a median δ_K of 0.071–0.089 on three short handoffs at (p, p) — the
same order as the cross-cell far-from-seam difference (0.019 → 0.063) and a plausible part of the τ = 0.03 ladder's
move (0.1433 → 0.5255). Until the short cell is measured under the scaled receiver, every "what length changes"
figure is length *and* configuration. This run measures it. No verdict moves; the run is descriptive and its one
effect on the paper is which sentence follows each 0036 descriptive.

## 1. Verified this session (2026-09-13)

| fact | value | source |
|---|---|---|
| f*(τ_K) is a mean-repair statistic | f* = 0 says the full-set mean δ_K ≤ τ_K, not that every token is; 5.8% (short) and 7.9% (long) of matched tokens exceed τ_K, on every handoff; per-handoff means 0.028–0.221 and 0.043–0.269 | recomputed from `results/{e9,e9l}/tokens/*.npz` with `e9_pertoken.f_star`; corrective entry in flight elsewhere |
| Bridge (0036 control 4), native vs scaled at (p, p) on 3 short handoffs | f*(τ_K) 0.0000 on all three; bridge R² 0.8992 / 0.8821 / 0.8932; median δ_K 0.071–0.089 | ledger 0036 |
| Cross-cell descriptives the run addresses | 16+ seam bin 0.019 → 0.063; τ = 0.03 ladder 0.1433 → 0.5255; τ = 0.10 0.0000 → 0.0119 | ledger 0029, 0036 |
| Memory at T = 32,768 | 1.7B under YaRN **16.70 GiB** (L40S, 09-10 probe) = native 16.72 on the 1g.20gb slice (09-08 ladder); 0.6B 10.89 | runbook 09-10 §6 R2 table; seed 09-08 §1 |
| Time | E9 scored 25 handoffs in 38 min wall on 09-04 (1,323,643 prefill tokens); the scaled forward costs the same memory and about the same time | ledger 0029; seed 09-08 §1 |
| Kept dumps | 0025's eight native handoffs are at home: `results/e9/scratch/` (45 GB) | `ls results/e9/scratch` |
| Driver and summarizer support | `[e9.rope]` with `context_floor = 0` and no bridge/profiles validates; `rope_args` puts `--rope-scaling` on every dump; the summarizer's bridge and profile sections are optional | `config.py` 270–300; `e9.py`; `summarize_e9.py` 478, 722; `tests/test_e9_scaled_short.py` |
| Pin | `063f402` (0035's RoPE spec; 0036's pin). `d5786df` (0029's) strips plain-θ and is wrong under YaRN | ledger 0035 |
| Deadline | LCFM extended to 2026-09-13 23:59 AoE = 09-14 11:59 UTC; this run is for the camera-ready, not the submission | CFP page, read 09-11 |

**Built this session (uncommitted until the operator's commit block):** `config/e9s.toml` (0029's instrument
byte-for-byte + 0036's rope block and pin; cap 32,768, floor 0; keep seed 9 n 8; order `n_sender_asc`,
`allow_partial`; `[e9.gate]` lists 0037); `src/linear_ceiling/e9_compare.py` (the fail-closed paired comparison and the
configuration share); `tests/test_e9_scaled_short.py`; `docs/drafts/append_0037.py`.

## 2. Decisions for the operator — rule before the script runs

**D1 — keep subset.** *Recommended: the same draw as 0025* (seed 9, n 8 over the same sorted ids → the same eight
handoffs; the script refuses otherwise). Cost: ~45 GB home + the R8 backup. Gain: the eight scaled dumps sit beside
their native twins, so a (p, p) native-vs-scaled read on eight handoffs (0036's bridge on three) is one CPU job at
home if wanted, and the summarizer's 0028 re-score check runs on the same handoffs as 0029's. Alternative: n = 3, seed 9
(a different draw; not nested) — ~17 GB; loses the twin read. If n changes, `config/e9s.toml` `[e9.keep]`, the
script's keep assertion and this seed change together.

**D2 — the cross arm.** The driver dumps the 0.6B source on S under the same YaRN and scores the n = 50 mapper on
every handoff, exactly 0029's shape; descriptive, reported beside 0029's 0.9286 and 0036's 0.9640. *Recommended: keep
it* — it costs the 0.6B prefill on S (~0.6M tokens, minutes) and puts the cross arm on one configuration across both
cells. The n = 420 mapper is not run under this entry.

**D3 — the box.** Either fits. (a) *Rented EC2 g6e.4xlarge (L40S 48 GB)* via `tools/ec2/`, proven on 09-10: no queue,
the 09-10 scripts run unchanged with `e9s` for `e9l` in `run.sh`/`pull.py`/`setup.sh`, about 1 h of instance time
(09-10 rate: ≈ $3/h compute + egress at ≈ $0.09/GB for the kept dumps). (b) *grant hub, a 1g.20gb slice*: 16.70 GiB
peak fits with ~3 GB to spare (E9 ran natively on exactly this footprint); `tools/jupyterhub/`; a shared login, so R7
step 0 binds. *Recommended: (a) if no grant is active this week*; otherwise (b). The R2 probe at T = 32,768 runs on
the chosen box before launch regardless (`tools/ec2/probe_e9l.py` prints it; the 09-10 numbers are from an L40S).

**D4 — the (p, p) twin read.** Not registered by 0037. If the operator wants it, it is a follow-up config for
`e9_rescore`-style CPU scoring of `results/e9/scratch/<h>/same_tgt` against `results/e9s/scratch/<h>/same_tgt` at
identity pairs, by its own entry. The entry says so.

## 3. Definition of done — home, before the box (R1)

1. **Commit** the four built files (block at the end of this seed) — `config/e9s.toml` must be committed unmodified
   for the gate and the script.
2. **`e9 --align-only --config config/e9s.toml`** at home (CPU, no gate): writes `results/e9s/align/coverage.json`. The
   script checks it reproduces 0029's 25 included ids, their `n_sender`/`n_receiver`/`n_matched` and text hashes, the
   43 exclusions and the eight kept. (Run at home 2026-09-13: coverage 68 / 25 / 43, keep draw and every alignment
   equal to 0029's — see the check below the commit block.)
3. **`append_0037.py --preview`**, read the entry, then run it without `--preview` (needs the upstream checkout at
   `063f402`, clean on the invoked paths). It appends 0037 and runs `ledger_check`. Commit the ledger and retire the
   script in the same change (README convention). If the corrective f* entry has landed as 0037 by then, rename to
   0038 first (script `NUM`, `config/e9s.toml` `[e9.gate]`, this seed's title line).
4. **Gate from a fresh clone:** `e9 --check --config config/e9s.toml` → `E9 gate: ready (entries
   0019/0023/0025/0027/0035/0037 committed; upstream pinned and clean; config/e9s.toml)`, with the mapper artifact
   `mappers/qwen3-0.6b-to-1.7b/k1.{json,safetensors}` copied by sha (R3; the 09-04 launch died on exactly this).
5. **Runbook** `docs/<date>-e9s-gpu-runbook.md` inheriting R1–R12 and the 09-10 runbook's shape: the R3 table (config
   sha, upstream sha, mapper shas, box scripts by sha), N = 25 `[i/25]` lines, the R2 probe row at T = 32,768, the HF
   dataset name `anon/linear-ceiling-e9s-<date>` (public is allowed since `d0b91db`; `ALLOW_PUBLIC=1`
   for `tools/hf_backup.sh`), and the version pins.

## 4. Definition of done — the sitting

- R2 probe on the box at T = 32,768 (both models) before launch; the peak into the runbook.
- Launch detached (R4): `run.sh` with `e9s`; `python -u`; exit code to `~/e9s.rc`; log rotated before any relaunch.
- Per handoff: pull the kept `scratch/<stem>/`, verify every file against `report.json` `kept_dumps`, then delete on the
  box (R5); small records mirrored every round (`pull.py e9s`).
- Release R7 in order, **step 0 first** (list `~` and `ps -u` before any deletion); terminate and read `terminated`
  back (EC2) or stop the server and probe (hub).
- Backup R8 from the verified home mirror only: `tools/ec2/verify_mirror.py e9s` (needs the `e9s` results dir; the
  script takes the experiment name as its argument), then `tools/hf_backup.sh`, then `tools/hf_verify_backup.py`.
  Token hygiene R9.
- At home, in this order, each fail-closed and the only reader of its figures (R11):
  1. `summarize_e9 --config config/e9s.toml` (~9 min; re-scores the eight kept from tensors under 0028's tolerance);
  2. `e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json` → `results/e9s/compare.{json,md}`;
  3. the figures entry by its own script (`append_00NN.py`, in-process summarizer + compare; number allocated at
     staging), "n scored of 25 registered" beside every number; then the outline's §5.2 sentence that the share selects.
- A refusal at any step is pasted verbatim into the closing brief and investigated, never worked around.

## 5. Controls — registered by 0037

(1) Pipeline identity HALT; (2) prefix-invariance HALT on the first handoff in run order, max centered δ ≤ 1e-4;
(3) δ_null, seed 23; (6) seam profiles b(t) and b⁻(t), 0025's bins. **No bridge (4) and no length profiles (5):** the
whole run is the bridge, at the pairs the instrument reads, over all 25.

## 6. The registered reading (what `e9_compare` states, fixed before the run)

Per handoff and in the median over handoffs: the paired difference of the mean δ_K (scaled − native; seeded
bootstrap of the median, seed 37, 2000 reps); f*(τ) at τ_K and on the ladder under both receivers; the fraction of
tokens over τ_K under both; the pooled per-token difference; the seam profile b⁻(t) under both. Against
`results/e9l/summary.json`: the **configuration share** (scaled − native) / (long − native) for the 16+ seam median
and for each ladder τ's median f*. A share near 1: the configuration accounts for the cross-cell difference and the
paper re-states the 0036 descriptives as configuration effects; near 0: the handoffs do, and length is the remaining
candidate; in between: both are reported. Never a claim about length alone — the two cells are different handoffs.

## 7. Not in this seed

The n = 420 arm; the (p, p) twin read (D4, a follow-up); the downstream-quality experiment (0023 `[STRETCH]`; GPU doc
item 2); any change to `results/e9/`, `results/e9l/`, `config/e9.toml`, `config/e9l.toml`; the 4-pager's submission
(deadline 09-14 11:59 UTC; this run is for the camera-ready); the corrective f* entry (another session).

## 8. Reuse map

- `config/e9s.toml` — done; `config/e9l.toml` is where its rope block and pin came from.
- `tools/ec2/{box.sh,setup.sh,run.sh,pull.py,verify_mirror.py,release_sweep.sh,probe_e9l.py}` — the 09-10 sitting's
  scripts; `e9l` → `e9s` in the three that name the experiment; `setup.sh` clones at the pins (both unchanged).
- `docs/2026-09-10-e9l-gpu-runbook.md` — the runbook shape, the R3 table, the §6 log format, the R7/R8 close.
- `src/linear_ceiling/e9_compare.py` — the comparison; `tests/test_e9_scaled_short.py` — its refusals.
- `docs/drafts/append_0037.py` — the registration; its shape is `append_0035.py`'s (retired at `d582f48`; `git show
  d582f48^:docs/drafts/append_0035.py`).
- `results/e9/{report.json,summary.json,scratch/}` — 0029's record and the eight native kept dumps.
- `tools/hf_backup.sh`, `tools/hf_verify_backup.py` — R8.

## 9. Hard invariants

`results/`, `data/`, `traces/` never enter history; `results/e9/` and `results/e9l/` are never rewritten; this run
writes only under `results/e9s/`. Entries 0025–0036 immutable; no `verdict:` line for this cell. No number enters the
ledger, a brief or the paper that a summarizer (or `e9_compare`) did not produce. No rule, τ, band, cap, dtype,
keep or handoff-set change after the first score file exists (R1). The upstream is read-only from here. Git history
is the operator's. Double-blind: no repo, dataset, handle or link in the paper.

## Commit block (operator; Git Bash; explicit paths)

```bash
cd ~/dev/linear-ceiling
# The scaled short cell: config, the fail-closed comparison, its tests, the staged registration, the seed
git add config/e9s.toml src/linear_ceiling/e9_compare.py tests/test_e9_scaled_short.py \
        docs/drafts/append_0037.py docs/drafts/README.md docs/2026-09-13-seed-e9-scaled-short-cell.md \
        docs/2026-09-11-gpu-runs-after-the-pivot.md CLAUDE.md
git commit -m "feat(e9s): scaled short cell — 0029's 25 under 0036's receiver; e9_compare; stage 0037"
git push
```

## Check run at home, 2026-09-13 (read-only; `results/e9s/` holds only `align/`)

`e9 --align-only --config config/e9s.toml` → coverage `{observed: 68, included: 25, excluded: 43}`; included ids ==
0029's scored set; `n_sender`/`n_receiver`/`n_matched`/`text_sha256` equal to 0029's on all 25; keep draw == 0025's
eight; rope `{yarn, 2.5, 32768}`; run order `astropy-7336#26` (|S| 8,213) first → `astropy-14539#96` (32,123) last.
`append_0037.py --preview` renders (78 lines) without appending; `e9_compare` refuses on the real tree with
`scaled: results/e9s/report.json is missing`, as it must until the run exists. Suite 430 passed, 1 skipped;
`scope ok`; `ledger ok`.
