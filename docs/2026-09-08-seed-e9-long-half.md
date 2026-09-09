# Seed — E9-long: the same-model re-render result on the long half of the handoffs

**Date:** 2026-09-08 · **Status:** seed, unnumbered, not registered; nothing here is a ledger figure.
Every value under *verified* was recomputed this session from `results/e9/align/*.json`, the upstream
checkout, or the Hub model configs, with the source beside it. Every value under *proposed* is a design
choice the operator rules on. Written for the session that drives the **next** GPU grant from home over
JupyterHub (`tools/jupyterhub/`); there is no agent on the box. Inherits `docs/gpu-experiment-protocol.md`
R1–R12 without restating them.

**Not this grant.** Today's grant (runbook `docs/2026-09-08-n420-target-dump-runbook.md`, another
session) is one MIG **1g.20gb** slice of an H100, shuts down 2026-09-09 07:30 UTC, and is running the
n = 420 target dump. The budget in §1 does not fit a 1g.20gb slice. This seed is for a grant requested
after 0033/0034 are on the record and the §3 checklist is green.

**Not the 4-pager.** The LCFM numbers froze EOD 2026-09-08. This experiment is the successor the
outline's Limitations names; its result goes to the camera-ready or the MLSys version, never into a
frozen figure.

## 0. The question

H-E9 (0029, `HELD`) was decided on the 25 handoffs whose sender prompt fits Qwen3's 32,768-token cap,
which is the **shorter half by |S|** (0025). The 39 handoffs excluded for length are the long ones:
|S| 34,974 to 357,623, median 52,141. A Long-Context workshop will ask whether same-model KV reuse at a
re-rendered handoff still needs zero recompute when the re-rendered context is 35K–80K tokens. Nothing
in the record answers it. This experiment runs E9's registered instrument, unchanged in rule and
statistic, on the long half, under a receiver configuration that can reach those positions.

## 1. Verified this session (2026-09-08)

| fact | value | source |
|---|---|---|
| Coverage at cap 32,768 | 68 observed · 25 included · 39 excluded "S exceeds context cap" · 4 excluded "receiver prompt is empty" | `results/e9/align/coverage.json`; 68 per-handoff rows |
| Newly included per cap (total / 68) | 40,960: **+8** (33) · 65,536: **+31** (56) · **81,920: +35 (60)** · 131,072: +35 (60) · 262,144: +38 (63) | per-handoff `n_sender` vs cap |
| Still above 81,920 (stay excluded, by name) | astropy-13453 #221 (147,218) · astropy-14365 #298 (172,327) · astropy-13398 #290 (185,793) · astropy-13398 #447 (357,623) | same rows |
| Empty receiver (stay excluded, by name) | astropy-13398 #137 · astropy-13398 #294 · astropy-14365 #157 (all 20241016) · astropy-13453 #106 (20241025) | same rows |
| Receiver length on the long set | \|R\| median 11,500, max 25,073 → **every R fits the native window; only S needs extension** | same rows |
| Qwen3-1.7B and Qwen3-0.6B | `max_position_embeddings` 40,960 · `rope_theta` 1e6 · `rope_scaling` null · 28 layers · 8 KV heads · head_dim 128 → identical KV bytes per token: 229,376 fp32 / 114,688 fp16 | `curl huggingface.co/Qwen/<m>/raw/main/config.json` |
| Upstream RoPE strip | `kvt/rope.py::rope_cos_sin(positions, d_h, theta)` is plain RoPE from θ; `kvt/models.py::load_model` is fp32 + `sdpa_repeat_kv` with no `rope_scaling` argument | read at upstream `4633718` |
| ⇒ | **A scaled-RoPE receiver is an upstream code change, not a config change** (R1: entry + re-pin before the request) | |
| E9 driver | `e9 --config <toml>`; `results_dir`, `scratch_dir`, `context_cap`, `[e9.keep]`, `[e9.rule]` all from the toml; **`REQUIRED_ENTRIES` and the refusal text hard-code e9.toml's five entries** | `src/linear_ceiling/e9.py` lines 49–75, 325–330 |
| Pins | E9 `d5786df` (0026) vs E8 family `223f469` (0030); between them only `scripts/score_mapper.py` and `kvt/pertoken.py` changed; `dump_kv.py` and `score_positions.py` unchanged | `git diff --stat d5786df HEAD -- <4 paths>` |
| ⇒ | an E9-long pin at `223f469`'s successor is legitimate for `score_positions.py` and also retires the two-pin state for the new experiment | |
| Mapper artifact (R3) | `mappers/qwen3-0.6b-to-1.7b/k1.json` `2fd05c33…` · `k1.safetensors` `cd6a8d93…` (full sha256 into the runbook at R3 time) | `sha256sum` in the upstream checkout |
| Prefill budget at cap 81,920 | 1.7B on S 1,771,353 + 1.7B on R 427,729 + 0.6B on S 1,771,353 = **3,970,435 tokens** (E9 09-04: 1,323,643 tokens in ~1–2 h wall, dump I/O and CPU scoring dominant → **estimate 3–6 h**, unmeasured) | sum over the 35 rows; runbook 09-02 |
| Memory at max \|S\| 80,111 | in-forward KV fp32 **17.1 GiB** + 6.8 GiB fp32 weights, before activations → **a 3g.40gb slice or a full card, never 1g.20gb**; R2 measures the true peak at T = 80,111 on the pinned path | formula 28·2·8·128·4 B/token |
| Transients | largest fp16 dump 8.6 GiB per side; a kept handoff ≈ up to 20 GiB (S 1.7B + S 0.6B + R 1.7B) | same formula |
| Home disk | 384 GB free on `C:`; `results/e9/scratch` (8 kept native handoffs) = 45 GB present | `df -h`, `du -sh` |
| **Measured 2026-09-08 on the 1g.20gb slice** (R2 ladder, pinned path, `logits_to_keep=1`) | 1.7B: 16.72 GiB at T = 32,768, **OOM at 40,960** (18.04 at the throw); 0.6B: 15.24 at 49,152, OOM at 65,536 → **D1(c) does not fit 1g.20gb either; every option needs 3g.40gb or a full card**. *Extrapolation, not a measurement:* the 0.6B ladder's slope is ≈ 283 KB/token (10.91 → 13.07 GiB over 8,192 tokens; KV alone is 229 KB/token); the 1.7B at T = 80,111 from its 32,768 point is then ≈ 16.7 + 12.5 ≈ **29 GiB**, inside a 3g.40gb slice with ~10 GB to spare, unproven until the §3 item 5 probe runs at that T | `docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.out`; n420 runbook §4 21:27 |
| Box versions (today's sitting) | torch 2.11.0+cu128 (the cu128 index tops out there; driver 570.148.08) · transformers 5.15.1 · numpy 2.5.2 · Python 3.12.6 | n420 runbook §R3 |

## 2. Decisions for the operator — rule before anything is built

**D1 — how S reaches 80K positions.**

- **(a) YaRN on both models, factor 2.5 over original 32,768 → cap 81,920.** *Recommended.* Reaches
  the knee of the ladder (+35 of 39; the last four need 147K–358K). Requires upstream work: cos/sin
  taken from the model's own `rotary_emb` (or re-derived and halt-tested against it, max |Δ| ≤ 1e-6 at
  positions {0, 1,000, 32,767, 40,960, 80,000}), `load_model(model_id, rope_scaling=...)`, a
  `dump_kv.py` flag, tests, commit, sha. HF form *(proposed; verify against transformers 5.15.1)*:
  `{"rope_type": "yarn", "factor": 2.5, "original_max_position_embeddings": 32768}`. Qwen's own
  recommendation is factor 4.0 for 131,072; a smaller factor is the same mechanism. **Risk, stated:**
  static YaRN changes the KV of short contexts too, so this receiver is a different function from
  0029's; the bridge control (§5) measures how different, and D2 says how the verdict reads.
- **(b) factor 2.0 → cap 65,536.** +31 instead of +35; in-forward KV 13.7 GiB. The conservative
  alternative if the 3g.40gb request is refused and only a 1g.20gb-class budget is offered (it will
  still not fit 20 GB in fp32 with weights; it is the option for a 24–32 GB card).
- **(c) native only, cap 40,960.** +8 handoffs, no upstream change, model inside its trained range.
  The fallback if (a) cannot land before the grant. Too small to carry a long-context claim alone;
  fine as a first sitting that de-risks the driver at 40K.
- **(d) extrapolate past 40,960 with no scaling.** *Not recommended.* The model is outside its trained
  range and any deviation is uninterpretable as a property of re-rendering.

**D2 — verdict-bearing or descriptive.** *Recommended:* a new hypothesis row **H-E9L** with 0023's rule
verbatim (median over included handoffs of the oracle selective-recompute fraction f*(τ_K), K read-out,
HOLDS ≤ 0.15 / DEGRADES ≥ 0.50), τ_K carried at 0.3186 and τ_agent_K alongside, **decided on the newly
included set only**, never pooled with 0029's 25 (that cell is immutable). Reason: a verdict is what
the audience remembers; a descriptive is a footnote. The honest cost: τ_K's anchor ("no more than the
mapper itself") was measured on native dumps. Carrying it is legitimate only with the bridge control
registered, and the entry says exactly that.

**D3 — keep subset.** *Recommended:* n = 3, seed 9, a fresh draw from the sorted newly-included ids (a
different set from 0025's; numpy `choice` without replacement is not nested, state it). ≤ 60 GiB at
home; one resumable `upload-large-folder`.

**D4 — cross arm.** Include as 0029 did (descriptive; mapper k = 1 applied at receiver positions).
Costs the 0.6B prefill on S (1.77M tokens), cheap beside the dumps. If wall time forces a cut, the
cut is written into the registration entry **before** launch, never decided on the box.

**D5 — exclusions.** The four empty-R and the four above 81,920 stay excluded and are counted by
name in the entry (coverage 35/39 of the long half; 60/68 pooled, stated but never pooled for a
verdict).

## 3. Definition of done — home session, before the request (R1)

1. **Upstream** (`kv-transfer-replication`, its own commits; linear-ceiling never edits it):
   rope/model/dump_kv change per D1(a); tests: halt test vs HF `rotary_emb`; strip∘apply identity at
   scaled positions; the existing toy 48-token dump still passes at the native config (regression).
   Commit; record the sha. **Ordering constraint (box session, 2026-09-08): this commit lands only
   after entry 0034 is on the record.** `config/e8c.toml` and `config/e9c.toml` pin `223f469` and
   their gates refuse when any invoked upstream path (`kvt/` included) differs from the pin; a YaRN
   commit on upstream `main` before 0034 breaks the 0033 chain's gates. The upstream checkout stays at
   `223f469` until `append_0034.py` has run and `ledger_check` is ok.
2. **linear-ceiling:** `config/e9l.toml` — pair, a `[e9.rope]` block, `context_cap = 81920`,
   `results_dir = "results/e9l"`, its own scratch, `[e9.keep] n = 3, seed = 9`, `[e9.rule]` copied
   verbatim from `config/e9.toml`, τ_K / τ_V / τ_agent_K / `tau_ladder` copied, `upstream_sha` = the
   new pin. `e9.py`: `REQUIRED_ENTRIES` per config (e9.toml keeps its five; e9l lists the new
   registration number), refusal text built from `cfg.config_path`; `summarize_e9 --config`; the
   §5 bridge control and the two length profiles in driver and summarizer; tests. Gates: `pytest -q`
   green, `lint_scope` ok, `git diff --check` clean, `ledger_check` ok.
3. **Drafts:** the registration script staged in `docs/drafts/README.md` (number = next free at
   staging; **0035 if staged before anything else**); the verdict script staged after it. Both
   ordering-guarded, `--preview`, in-process summarizer, `ledger_check` after append. Never read a
   "prior" value from HEAD in a draft script.
4. **Gate from a fresh clone:** `e9 --check --config config/e9l.toml` prints ready with the mapper
   artifact copied by sha (R3). The 2026-09-04 launch died on exactly this.
5. **R2 probe** at T = 80,111 on the pinned path, real models, `torch.cuda.max_memory_allocated`
   printed; the measured peak goes into the grant request, which asks for a **3g.40gb slice or a full
   card** and states the 3–6 h wall estimate.
6. **Runbook** `docs/<date>-e9l-gpu-runbook.md` inheriting R1–R12: the R3 table (upstream sha,
   config sha, mapper shas, box scripts by sha), N = 35 `[i/N]` lines the box must print (+3 bridge
   handoffs, §5), coverage the entry must state, the HF dataset name
   `hossainpazooki/linear-ceiling-e9l-<date>`, and the version pins from §1.

## 4. Definition of done — the GPU sitting

- Launch detached (R4): the launch line alone on its line, log rotated before any relaunch, the
  home poller keyed on an rc file with a bracketed `pgrep` pattern (both 2026-09-08 traps).
- Per handoff: pull kept `scratch/<stem>/`, verify every file against `report.json` `kept_dumps`,
  then delete on the box (R5). Small records mirrored every round, re-pulled on size **or** mtime.
- Bridge control dumps (§5) run first, before the first long handoff, so a socket drop late in the
  sitting cannot lose them.
- Release R7 in order, stop at the first failure; backup R8 from the verified home mirror only;
  token hygiene R9.
- At home: `summarize_e9 --config config/e9l.toml` is the only reader (R11); a refusal is pasted
  verbatim into the closing brief and investigated, never worked around. Verdict entry by its script.

## 5. Controls — registered before any prefill

1. **Pipeline identity halt** (0025): a dump scored against itself must give δ ≡ 0.
2. **Prefix-invariance halt** (0025) on the first included long handoff: S vs S+R's first token,
   max centered δ ≤ 1e-4.
3. **δ_null** (0023): seeded derangement of receiver→sender pairing; the uninformative scale.
4. **Configuration bridge — new.** Three handoffs from 0025's kept subset (named in the entry; their
   native dumps are at home under `results/e9/scratch/`) are dumped again on the box under the D1
   configuration. At home the summarizer compares native vs scaled `K_stripped` at identical (p, p)
   positions: centered δ_K distribution and f*(τ_K). Descriptive, with its **reading fixed now:** if
   the median native-vs-scaled f*(τ_K) exceeds 0.15, the receiver configuration alone exceeds the
   mapper's tolerance and H-E9L is read as a claim about the scaled receiver only, in the verdict
   entry's first paragraph. Box cost: three short handoffs' dumps. It cannot gate the launch (it is
   computed at home afterwards); it gates the reading.
5. **Length profiles — new, descriptive.** f*(τ_K) and median δ_K (i) by |S| bin
   {34,974–49,999 · 50,000–64,999 · 65,000–81,920} and (ii) by matched-token position in S
   {0–32,767 · 32,768–49,151 · 49,152–65,535 · 65,536–81,920}. Bins fixed here. (ii) is the
   long-context figure: does agreement at a re-rendered position depend on how deep in the sender's
   context the token sat?
6. **Seam profile** b⁻(t) as 0025, same bins.

## 6. What the registration entry must state

The rule verbatim from 0023 with its numbers; the cap and the ladder that chose it; the rope
configuration and that it differs from 0029's receiver; the eight exclusions by name; τ_K and
τ_agent_K carried and why that is legitimate only with control 4; the keep draw (n, seed, method);
N = 35; controls 1–6 with their fixed thresholds and bins; the pin; and the R1 proof line — no score
file exists under `results/e9l/` at the commit that carries the entry.

## 7. Not in this seed

The n = 420 target dump (today's sitting, another session). The §3.5 freeze ruling (block (b) of the
2026-09-07 brief). The 4-pager. E-RL. The recorded-corpus experiment (`docs/2026-09-06-gap-map-revisited.md`
open item; MLSys cycle). Any pooling of the long half with 0029's 25. Any edit to `results/e9/`.

## 8. Reuse map

- `config/e9.toml` — the template; copy the rule and τ blocks byte-for-byte.
- `src/linear_ceiling/e9.py`, `e9_align.py`, `e9_pertoken.py`, `summarize_e9.py` — the instrument;
  `align()` already handles the cap and the exclusion reasons; `coverage_groups` (0025) already
  splits `excluded_long`.
- `results/e9/align/*.json` — the 68 alignment records with `n_sender` / `n_receiver`; the §1 ladder
  recomputes from them in one script.
- `results/e9/scratch/` — the 8 kept native handoffs for control 4.
- `docs/2026-09-02-e9-gpu-runbook.md`, `docs/2026-09-08-n420-target-dump-runbook.md` — the two
  runbook shapes; the second has today's box facts and the three new traps.
- `tools/jupyterhub/jh.py`, `pull.py`, `README.md` — the driver and the pull loop.
- Upstream `kvt/rope.py`, `kvt/models.py`, `scripts/dump_kv.py`, `scripts/score_positions.py`.
- Memory notes `jupyterhub-box-driving`, `relaunch-redirect-destroys-halt-logs`,
  `hf-upload-large-folder-windows-stall` (session memory, not in the repo).

## 9. Hard invariants

`results/`, `data/`, `traces/` never enter history; `results/e9/` is never rewritten; this experiment
writes only under `results/e9l/`. Entries 0025–0029 immutable. No number enters the ledger, a brief,
or a paper that a summarizer did not produce. The upstream is read-only from linear-ceiling; its
changes are its own commits. No rule, τ, band, cap, dtype or handoff-set change after the first score
file exists (R1). Double-blind rules. Git history is the operator's.
