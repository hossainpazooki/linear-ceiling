# Llama family GPU runbook — `llama3.2-3b-to-llama3.1-8b`, three sittings on rented cards

**Date:** written 2026-09-18 · **Status:** runbook written *before* the registration entries exist; §12 is filled
during each sitting in UTC. Inherits `docs/gpu-experiment-protocol.md` R1-R12 without restating them, and takes its
shape from `docs/2026-09-10-e9l-gpu-runbook.md` (the rented-L40S sitting) and `docs/2026-09-13-e9s-gpu-runbook.md`
(the short cell). The pair is **meta-llama/Llama-3.2-3B (source) -> meta-llama/Llama-3.1-8B (receiver)**, matched-KV
(8 KV heads x 128 head dim on both sides), registered by the entries `docs/drafts/README.md` allocates at staging;
the upstream change it needs is specified in `docs/2026-09-18-llama-upstream-patch-spec.md`.

## 0. Nothing here runs on the operator's local machine

Stated plainly at the top because the sizing below makes it a correctness rule, not a preference. The home box has
**no GPU, 18 GiB of RAM (`hw.memsize` = 19,327,352,832) and 82 GiB free on `/Users`** with ~32 GB already held by
`/Users/emersonyu/e9-repro/linear-ceiling`. The receiver's fp32 weights alone are **29.9 GiB**, so no home-side step
may load `meta-llama/Llama-3.1-8B` at all — not "should not": it cannot. The operator has also ruled that nothing is
run locally for this campaign.

What stays at home, all CPU, all cheap:

- `tools/preflight_pair.py` — config and tokenizer JSON only, no weights, no GPU (§1.1);
- the E8 driver `linear_ceiling.e8 --config config/e8f.toml` if and only if it does not load a model (it samples
  agent text and drives the upstream by subprocess; the *dumps* are a box step here, see §7);
- every summarizer and every gate check;
- `e9 --align-only` and `summarize_e9 --calibrate-tau`, which read traces, the archived dumps and E8's report.

What must be on a rented card: `prepare_tokens`, both `dump_kv` runs, `probe.py`, `fit_mapper.py`, and the two E9
drivers. Everything else is transport.

## 1. What must be true before a card is rented

Each of these, left alone, stops the campaign *after* money has been spent. None is hard.

**1.1 The two kill-shots, in this order.** `tools/preflight_pair.py` against the **gated `meta-llama` snapshots**
(never an unsloth / NousResearch mirror: those are re-uploads and cannot be the provenance of a number under the
borrowed-facts rule). It must confirm, and record the sha256 of each `config.json` and `tokenizer.json`:

1. `tok_s.get_vocab() == tok_t.get_vocab()`. `scripts/prepare_tokens.py:21` calls `assert_shared_tokenizer`, which
   compares the vocab maps and raises on any difference (`kvt/models.py:51-55`). Both models ship the
   128,256-entry Llama-3 BPE, but `get_vocab()` includes added and special tokens and the Llama-3.2 release
   repurposed several `<|reserved_special_token_N|>` slots. **If the maps differ by one entry there is no E8 corpus
   and the pair is dead** — reopen the pair decision; do not patch around it.
2. `num_key_value_heads == 8` and `head_dim == 128` on **both** sides, printing the declared and the derived value
   for each (the receiver declares no `head_dim`; 128 comes from `hidden_size // num_attention_heads` = 4096 / 32).
   This is the matched-KV premise the whole plan rests on and the source side has never been read on this machine.

It also records, without asserting they match: `rope_scaling.rope_type == "llama3"` both, `low_freq_factor` 1.0,
`high_freq_factor` 4.0, `original_max_position_embeddings` 8192 both, and the two **different** `factor` values
(3.2: 32.0; 3.1: 8.0 — expected); `max_position_embeddings == 131072` both; `vocab_size == 128256` both;
`num_hidden_layers` 28 / 32; `tie_word_embeddings` true / false (harmless — `dump_kv` passes `logits_to_keep=1` and
never touches `lm_head`).

**1.2 Upstream commit P landed and pushed.** `docs/2026-09-18-llama-upstream-patch-spec.md`, based on `063f4023`,
pushed to `github.com/hossainpazooki/kv-transfer-replication` — `tools/ec2/setup.sh:22-24` clones *from there, at a
sha*, so an unpushed P cannot be brought up. Every linear-ceiling commit the sitting needs is pushed for the same
reason. Then `upstream_sha` is recorded in `UPSTREAM.md`, `config/e8f.toml`, `config/e9f.toml`, `config/e9fl.toml`.

**1.3 `tools/ec2/probe_e9l.py` fixed.** Line 25 is `rope = dict(cfg["rope"])`, unconditional, and every Llama config
here deliberately carries **no** `[e9.rope]` — so the R2 probe that sittings B and C require KeyErrors before it
loads anything. It must read `cfg.get("rope") or {}` and pass `rope=None` through, and its hardcoded
`default_ladder = "32768,65536,80111"` (the longest *Qwen*-tokenized |S|) must come from an env var, set to the
max |S| in this run's own `coverage.json`.

**1.4 `tools/ec2/setup.sh` parameterized.** `UP_SHA` (line 10) and the two mapper shas (11-12) are literals and
`MD` (line 38) is hardcoded to `mappers/qwen3-0.6b-to-1.7b`. `UP_SHA`, `PAIR`, `MAPPER_JSON_SHA`, `MAPPER_ST_SHA`
become environment-overridable beside the already-overridable `EXP` / `LC_SHA` / `HOME_COVERAGE_SHA12`, and `MD` is
built from `$PAIR`.

**1.5 The corpus, including the 8 files `fetch` cannot reach.** `config/e7-manifest.json` lists 188 files, of which
**8 carry no `s3` record** (4 tau-bench, 4 tau2-bench airline JSONs); `e7_manifest fetch` can only print
`NO S3 SOURCE …`. `[e8.text] suites` includes tau2-bench, so E8-Llama's calibration draw cannot be made without
them. Restore them by hand from their suites' repositories, sha256-match, then `e7_manifest check` must print
`manifest ok: 188 files match disk; sha256 371fb4bf3cb089bd…` in both directions before anything is scheduled.

**1.6 Disk and HF storage budgeted.** §11.

## 2. The three sittings and what each produces

| sitting | config | what runs | what it produces | cuttable |
|---|---|---|---|---|
| **A** — E8 calibration + fit | `config/e8f.toml` | `prepare_tokens` -> `dump_kv` x2 (n = 50, len 1024, stride 4) -> `probe.py` -> `fit_mapper --k 1 4 8` -> the E8 arms | the pair's mapper at k = 1/4/8, `results/mapper/<pair>/r2.json`, `results/e8f/report.json`, and from them the pair's own τ | no — everything downstream needs the mapper |
| **B** — E9 short | `config/e9f.toml` | `e9` over the handoffs with `max(|S|,|R|) <= 32,768` Llama-3 tokens | `results/e9f/report.json`; the campaign's **one** verdict-bearing cell | no |
| **C** — E9 long, native receiver | `config/e9fl.toml` | `e9` over `32,768 < max(|S|,|R|) <= 81,920` | `results/e9fl/report.json`, descriptive | **yes** — stage 3 is explicitly cuttable; nothing else depends on it |

**Sitting C is a native-receiver, descriptive cell.** Llama is natively 131,072, so there is no YaRN, no
`[e9.rope]` and no `[e9.bridge]`; 81,920 and 32,768 are **registered length thresholds in Llama-3 tokens, not
hardware bounds**. It cannot move, support or refute H-E9L and is never pooled with entry 0036's 35 handoffs. What
replaces E9-long's configuration bridge is three fail-closed, zero-GPU-cost controls: `context_cap <=` every dump's
recorded `max_position_embeddings`; RoPE identity across dumps **of the same model role** (receiver with receiver,
source with source — the two sides carry different llama3 `factor` values, 32.0 and 8.0, so a cross-role equality
assertion would refuse every correct run); and the position profile re-cut at `s_pos_edges = [0, 8192, 32768,
65536]`, where 8,192 is llama3 scaling's `original_max_position_embeddings`, the same on both sides.

The short and long cells partition cleanly — `e9_align.align` includes iff `max(|S|,|R|) <= cap`, and the long cell
additionally excludes `max(|S|,|R|) <= floor` — and the **residual** (handoffs whose longer side exceeds 81,920
Llama-3 tokens) is scored by neither and must be named and counted in both entries from the two `coverage.json`
files.

Every count in this runbook that depends on the Llama-3 tokenizer is unknown until `e9 --align-only` runs, and the
Qwen figures (0029's 25 included / 39 excluded-for-length, 0036's 35 in the band) **carry over to nothing**: the
128,256-entry Llama-3 BPE re-partitions the handoff set and the direction of the shift is not predictable. Use the
marker, never a number:

```
UNRESOLVED::coverage@llama3.2-3b-to-llama3.1-8b::read from results/e9f/align/coverage.json (short) and results/e9fl/align/coverage.json (long)
```

The same holds for `tau_K`, `tau_V`, `tau_agent_K`, the R², the medians and the handoff counts: none of them exists
yet, none is computable at home, and none may be written anywhere as a plausible-looking placeholder.

## 3. R2 — the budget, and why it is bigger than every prior sitting

### 3.1 KV bytes per token (all layers, K and V, float32)

`n_layers x 2 x n_kv x d_h x 4 B`:

| model | layers | bytes/token (fp32, in memory) | bytes/token (fp16, on disk) |
|---|---|---|---|
| Llama-3.1-8B (receiver) | 32 | 262,144 = 256 KiB | 131,072 |
| Llama-3.2-3B (source) | 28 | 229,376 = 224 KiB | 114,688 |
| Qwen3-1.7B (the prior receiver) | 28 | 229,376 | 114,688 |

The **Llama source is byte-for-byte the Qwen3-1.7B receiver** (28 / 8 / 128 both); the receiver grows by exactly
32/28 = 1.1429x per token. Dumps are stored float16 (`kvt/data.py:45-46`), so on disk it is half.

### 3.2 Weights, float32

`meta-llama/Llama-3.1-8B` 8,030,261,248 params x 4 B = **29.91 GiB** (untied `lm_head`);
`meta-llama/Llama-3.2-3B` 3,212,749,824 x 4 B = **11.97 GiB** (tied embeddings). Against the measured prior
sitting: Qwen3-1.7B 6.41 GiB, Qwen3-0.6B 2.25 GiB (`docs/2026-09-08-n420-target-dump-runbook.md:72`).
The two parameter counts are the published model-card figures; they are **not** read on this machine and
`tools/preflight_pair.py` confirms the architecture they follow from before either is quoted in an entry.

### 3.3 The non-weight, non-KV residual — an extrapolation, not a measurement

Two independent measured points, Qwen3-1.7B fp32, `sdpa_repeat_kv`, `logits_to_keep=1`:

```
T = 32,768: peak 16.72 GiB - 6.41 weights - 7.00 KV = 3.31 GiB -> 108,441 B/token   (09-08 ladder)
T = 80,111: peak 31.56 GiB - 6.41 weights - 17.11 KV = 8.04 GiB -> 107,750 B/token  (09-10 L40S)
```

Consistent at ~106 KiB/token. Scaled by the per-token activation width `hidden + intermediate + n_q_heads*d_h`
(Qwen3-1.7B: 2048 + 6144 + 2048 = 10,240 floats = 40,960 B; measured/proxy = **2.65x**):

```
Llama-3.1-8B  4096 + 14336 + 4096 = 22,528 floats -> 90,112 B  x2.65 = 238,800 B/token (233 KiB)
Llama-3.2-3B  3072 +  8192 + 3072 = 14,336 floats -> 57,344 B  x2.65 = 151,960 B/token (148 KiB)
```

**Nothing in this program has measured an 8B fp32 forward.** Under R2 an extrapolated peak is a bound to be
replaced by a measurement: the fixed `probe_e9l.py` (§1.3) on the real card at the run's real max |S| is the only
thing that may authorize sittings B and C. The Qwen extrapolation under-predicted its own measurement by 8%, so
every row below carries a +8% column and the L40S-vs-80 GB call for sitting B turns on the measured number.

### 3.4 Peak per sitting

| sitting | model | weights | KV | residual | point estimate | +8% | card |
|---|---|---|---|---|---|---|---|
| **A** (T = 1,024) | receiver 8B | 29.91 | 0.25 | 0.23 | **30.4 GiB** | 32.8 | **>= 40 GB** |
| | source 3B | 11.97 | 0.22 | 0.14 | 12.3 GiB | 13.3 | |
| **B** (T = 32,768) | receiver 8B | 29.91 | 8.00 | 7.29 | **45.2 GiB** | 48.8 | **80 GB** |
| | source 3B | 11.97 | 7.00 | 4.64 | 23.6 GiB | 25.5 | |
| **C** (T = 81,920) | receiver 8B | 29.91 | 20.00 | 18.22 | **68.1 GiB** | 73.6 | 80 GB at 85-92%, or H200 141 GB |
| | source 3B | 11.97 | 17.50 | 11.59 | 41.1 GiB | 44.4 | |

Three consequences that overturn every prior runbook's card choice:

- **Sitting A is not a 24 GB job.** 29.91 GiB of fp32 receiver weights overflows a 24 GB card before a single
  token. A100 40 GB, L40S 48 GB or A6000 48 GB.
- **Sitting B is not an L40S job.** The L40S's *measured* usable memory is 44.39 GiB (09-10 probe) and the point
  estimate is 45.2 GiB before any margin. Budget an 80 GB card (H100 / A100 80 GB). The Qwen short sitting fit in
  16.7 GiB; this one does not.
- **Sitting C must be launched on a measurement, never on this table.** At 68.1 GiB it is 85% of an 80 GB card, and
  the `sdpa_repeat_kv` shim is more load-bearing here than anywhere in the program so far: the fp32 math-kernel
  score matrix would be `32 q heads x 81,920^2 x 4 B` = **859 GB** (137 GB even at T = 32,768). If the registered
  attention backend is not the one that loads, the run does not OOM gracefully — it asks for 859 GB.

### 3.5 Artefact sizes

Sitting A: source dump 12,800 x 114,688 = **1.47 GB**, target dump 12,800 x 131,072 = **1.68 GB**; probe =
28 x 32 x 8 = **7,168 OLS fits per kind** x 3 kinds (CPU, ~15-25 min); mapper artefacts **268 MB / 1.07 GB /
2.15 GB** at k = 1/4/8 (= 2 x 32 layers x 1024k x 1024 x 4 B). `build_features` peaks at 10,240 x 8192 x 4 =
336 MB at k = 8 and the float64 Gram at 8192^2 x 8 = 537 MB — trivial at n = 50.

Sitting B, per handoff, fp16 on disk at the cap: `same_src` 4.30 + `same_tgt` 4.30 + `cross_src` 3.76 =
**12.4 GB**. With `[e9.keep] n = 8` the kept tensors alone can reach ~100 GB. Sitting C at its cap: 10.74 + 10.74 +
9.39 = **30.9 GB** per handoff. **R5 (pull, verify against `report.json`, then delete, per handoff) is not
optional at this scale** — it is what keeps the box's 250 GB root from filling mid-run.

## 4. The boxes

The 09-10 / 09-13 shape carries over except the instance type: Deep Learning Base OSS Nvidia Driver GPU AMI
(Ubuntu 22.04), ssh as `ubuntu`, a key pair whose private half stays at home, a security group opening port 22 to
the home IP only, 250 GB gp3 root deleted on termination, shutdown behaviour `stop`, the 24 h self-halt armed by
`setup.sh`, and the pinned stack: Python 3.12 (uv), torch 2.11.0+cu128, transformers 5.15.1, numpy 2.5.2 — the
stack entry 0028's cross-platform tolerance was measured on. **A 250 GB root is right for A and B and marginal for
C** (30.9 GB per handoff before the puller catches up); size it from the sitting's own kept-dump count.

`tools/ec2/` is AWS-specific. AWS's single-GPU line tops out at the L40S 48 GB, which §3.4 rules out for B and C,
so both sittings likely run on a rented 80 GB card **outside** AWS and `box.sh` up/put/terminate become that
provider's equivalents, done by hand and logged in §12 with the same read-back discipline (R7 step 6). Everything
else — `setup.sh`, `run.sh`, `probe_e9l.py`, `release_sweep.sh`, `pull.py`, `verify_mirror.py` — is plain ssh and
carries over unchanged.

Instance id, region, IP, card, driver, launch time and price go into §12 at launch, per sitting.

## 5. R3 — everything each sitting reads, by sha

Nothing in this table can be filled in yet; that is the point of writing it now. Each `UNRESOLVED::` line is a
refusal, not a placeholder — a sitting does not start with one of its own rows unfilled.

| artifact | where | sha256 / pin |
|---|---|---|
| linear-ceiling checkout on the box | `~/linear-ceiling`, detached | the commit carrying this sitting's registration entry (`LC_SHA`, filled in §12 at launch; must be pushed) |
| upstream checkout on the box | `~/kv-transfer-replication`, detached | `UNRESOLVED::upstream_sha@P::docs/2026-09-18-llama-upstream-patch-spec.md, based on 063f4023` |
| `config/e8f.toml` / `config/e9f.toml` / `config/e9fl.toml` | committed | `UNRESOLVED::config_sha256@<config>::sha256 of the committed file at LC_SHA` |
| `config/e7-manifest.json` | committed | `e7_manifest check` at home -> `manifest ok: 188 files match disk; sha256 371fb4bf3cb089bd…`, after the 8 hand-restored files (§1.5) |
| traces | `~/linear-ceiling/traces/` from the home tarball | checked on the box by `e7_manifest check` in `setup.sh`, both directions + bytes |
| mapper (gitignored; sittings B and C only) | `~/kv-transfer-replication/mappers/llama3.2-3b-to-llama3.1-8b/k1.{json,safetensors}` | `UNRESOLVED::mapper_sha256@k1::produced by sitting A; checked by sha256sum -c in setup.sh before the gate` |
| alignment / coverage at home | `results/e9f/align/coverage.json` (B), `results/e9fl/align/coverage.json` (C) | `UNRESOLVED::coverage_sha256@<cell>::written by e9 --align-only at home under the committed config's sha` |
| model weights | `meta-llama/Llama-3.2-3B`, `meta-llama/Llama-3.1-8B`, **gated** | staged offline from home (§6); snapshot revisions and `config.json` / `tokenizer.json` sha256 from `tools/preflight_pair.py` |
| box scripts | `~/setup.sh`, `~/run.sh`, `~/probe_e9l.py`, `~/release_sweep.sh` = `tools/ec2/*` at `LC_SHA` | pulled back into `results/<exp>/logs/box/` each round and hashed |

## 6. Gated weights: staged offline, no token on the box

Both repos are gated (manual licence grant on the operator's HF account). Pre-download both snapshots **at home**
and push them with `box.sh put`, then point `HF_HOME` at the staged cache and export `HF_HUB_OFFLINE=1`. This keeps
R7 step 4's sweep asserting *"no HF token ever existed on this box"* rather than being rewritten to prove removal —
an upload is cheaper than weakening a release check.

Budget: **bf16 safetensors ~6.4 GB (3B) + ~16.1 GB (8B) = ~22.5 GB to upload** per box, once per sitting. (An
earlier draft said ~9 GB; that was the 1B -> 3B pair.) Load is fp32 *in memory* — the on-disk bf16 checkpoint is
upcast by `load_model`; the disk figure and the memory figure in §3.2 are not the same number and neither is
derivable from the other.

## 7. Sitting A — E8 calibration and the mapper fit

Card >= 40 GB. Forecast ~2 h of card time; the probe and the E8 arms are CPU.

1. **Home, before the box:** §1 complete. The ledger commit carrying the registration entry is **pushed**; record
   it as `LC_SHA`. `tar -czf <scratch>/traces.tar.gz traces`.
2. Bring the box up; upload the traces tarball, the four box scripts (LF — strip CRLF before `put`) and the staged
   weight cache.
3. **`setup.sh` detached** with `EXP=e8f PAIR=llama3.2-3b-to-llama3.1-8b UP_SHA=<P> LC_SHA=<sha>`; poll
   `~/setup.rc`. It must end with `manifest ok` and the E8 gate from a **fresh clone** (R1). Stop on any refusal.
4. **The upstream chain, in the upstream venv, by hand** (this is how every existing mapper was produced; the
   read-only rule binds this repository, not the operator, and no linear-ceiling driver writes a `results/` record
   for these steps):
   - `scripts/prepare_tokens.py --pair llama3.2-3b-to-llama3.1-8b --n-seqs 50 --seq-len 1024 --seed 0`
     — **this is where §1.1's tokenizer check fires for real.**
   - `scripts/dump_kv.py --pair … --which source --stride 4` then `--which target` (1.47 GB / 1.68 GB).
     `check_matched_kv` runs unconditionally on both and must pass silently; each dump's `meta.json` must carry a
     `rope` block with `rope_type "llama3"`, its own `inv_freq`, and `check_max_abs` under `1e-5`. **The two dumps'
     `inv_freq` vectors differ — that is correct here** and is why every RoPE-identity assertion downstream is
     scoped per model role.
   - `scripts/probe.py --pair llama3.2-3b-to-llama3.1-8b` (7,168 fits per kind, CPU).
   - `scripts/fit_mapper.py --pair llama3.2-3b-to-llama3.1-8b --k 1 4 8 --lam 0.01 --holdout-frac 0.2 --space content`.
     **`--pair` is required and was missing from this line**, which killed the 2026-09-18 sitting three
     seconds into the fit, after the 95-minute probe had already succeeded.
     p/n = **0.10 / 0.40 / 0.80** at k = 1/4/8 — numerically identical to Qwen's, so entry 0016's k = 4 collapse is
     directly comparable and `Mapper.formula_params` is exact for this pair (the Table-12 parameter-count control
     is preserved, not forfeited).
5. **`e8 --config config/e8f.toml`** (arms (a) and (b); CPU driver). Run it wherever RAM allows — at home if the
   step never loads a model, otherwise on the box.
6. **Pull everything** and `sha256sum` it at home: both dumps, `results/mapper/<pair>/r2.json`, the three mapper
   pairs, `results/e8f/report.json`, every log. Record `k1.json` / `k1.safetensors` sha256 in §12 — they become
   sittings B and C's R3 rows and `setup.sh`'s `sha256sum -c`.
7. **Release (§10), then backup (§11).** The mapper and the dumps are the only artefacts in this campaign that
   cannot be recomputed without renting another card; the Qwen equivalents are absent from every checkout, which is
   exactly why the Qwen τ is not recomputable today. They go into R8 (§11) as *inputs*, not just outputs.
8. **At home, after:** `summarize_e8 --config config/e8f.toml`, then
   `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report results/e8f/report.json`, which writes the
   pair's own `results/e9f/calibration/tau.json`. Its τ is what `config/e9f.toml` is then written with — typed from
   the file, never from a screen — and the figures entry reads every number from the summarizer's output.

## 8. Sitting B — E9 short (cap 32,768 Llama-3 tokens)

Card **80 GB**. The verdict-bearing cell.

1. **Home, in this order, all before `box.sh up`:** `config/e9f.toml` committed with the τ from sitting A;
   `e9 --align-only --config config/e9f.toml` written `results/e9f/align/coverage.json` under that config's sha and
   `results/e9f/` holds nothing else; **`summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report
   results/e8f/report.json`** has run. That last step is the one the 2026-09-14 sitting skipped: `e9 --check` never
   looks at `tau.json` (`e9.assert_ready` checks the pin placeholder, the mapper's presence, git cleanliness of
   ledger + config, the entry markers and `check_upstream` — nothing else), so the box printed `ready`, ran 25/25,
   and the summarizer refused after the card was released. It goes **before** the box, every time.
2. `e9 --check --config config/e9f.toml` prints ready from a fresh clone; the registration entry is on the ledger
   and pushed.
3. Box up; upload the mapper pair (by the §12 sha), the traces tarball, the four scripts, the weight cache.
4. **`setup.sh`** with `EXP=e9f PAIR=… UP_SHA=<P> LC_SHA=<sha> MAPPER_*_SHA=<from §12>
   HOME_COVERAGE_SHA12=<from the home coverage.json>`. It ends with the gate from a fresh clone and the box's own
   `--align-only` sha, which should match home's LF-normalized value.
5. **R2 probe** — the fixed `probe_e9l.py` (§1.3) with the ladder's top rung set to this run's real max |S| from
   `coverage.json`, fp32, `sdpa_repeat_kv`, `logits_to_keep=1`, both models. Both rows into §12.
   **Stop if either row is not `ok`, and stop if the receiver's measured peak exceeds the card's usable memory
   less a real margin** — §3.4's 45.2 GiB is an extrapolation and this is the measurement that replaces it.
6. **`run.sh`** (R4: `python -u`, detached, log rotated, exit code to `~/e9f.rc`). Expect **no** `[bridge]` lines —
   this cell registers no bridge — then `[i/N] <hid>: same K …` in the registered order. Record the launch time.
7. **`pull.py e9f` at home** (R5): each kept handoff verified against `report.json`'s fingerprints, then deleted on
   the box; small records and box logs every round. At 12.4 GB per handoff this is what keeps the root from filling.
8. **No cutoff for this cell.** `config/e9f.toml` does not register `[e9.order] allow_partial = true`, so
   `e9 --close-partial --config config/e9f.toml` refuses. If the run is interrupted, resume it in the same
   registered order until `report.json` is complete; if it cannot finish, H-E9F remains `unresolved` and entry
   0042 is not appended. Only the descriptive long cell in §9 registers a partial close.
9. **Release (§10), backup (§11), then at home `summarize_e9 --config config/e9f.toml`** — the only reader (R11).
   A refusal is pasted verbatim into the closing brief and investigated, never worked around. Then the figures
   entry's own script, in-process, reading every number from `results/e9f/summary.json`.

## 9. Sitting C — E9 long, native receiver (floor 32,768, cap 81,920)

Card 80 GB at 85-92% full, or an H200 141 GB. **Cuttable**: nothing else depends on it, and the decision to cut is
free until the box is up.

Identical to §8 with `EXP=e9fl` and `config/e9fl.toml`, plus:

- **Launch only on a measured probe.** §3.4's 68.1 GiB is extrapolated from two Qwen3-1.7B measurements at a scale
  nothing in this program has touched. Run `probe_e9l.py` at this run's real max |S| and require margin against the
  card's *measured* usable memory, not its nameplate.
- `[e9.keep] n = 3` and 30.9 GB per handoff: the puller must be ahead of the driver, not beside it.
- `[e9.order] by = "n_sender_asc"` with `allow_partial`, so a cutoff closes on a prefix.
- **Expect no `[bridge]` lines and no `[e9.rope]` anywhere.** If the run emits a bridge block, the config is wrong:
  `config.py` refuses a bridge without a rope, which is the correct refusal for a native receiver.
- The entry states plainly that this cell cannot move, support or refute H-E9L, names the three fail-closed
  replacements for control 4 (§2), cites its **own** `coverage.json`, and states the residual above 81,920 tokens.

## 10. R7 — the release checklist, in order, stop at the first failure

Unchanged from `docs/gpu-experiment-protocol.md`; run per sitting, and hold the termination until the summarizer
has passed so a refusal can still be re-scored on the same platform.

0. **The account is shared until proven otherwise.** `ls -la ~` and `ps -u $(whoami)` *before* any deletion or
   stop, classified by mtime against the instance launch time: older is image baseline and is listed for the
   record; newer must be on this runbook's own list. Anything not ours aborts the release — delete nothing, stop
   nothing, tell the operator. Each abort is the checklist working; never resolve one by loosening it.
1. Mirror complete and re-verified from raw bytes (R6); print the mirror's `report.json` sha256.
2. No tensor directory left under `results/<exp>/` on the box; if one is, pull and verify before deleting.
3. Pull every box-side log the entry will cite that the puller did not — `setup.log`, `probe.log`, `<exp>.log`, the
   rotated halt logs, `launches.log`, `manifest_check.out` — and hash each after download; the mirrored copies must
   hash identically at home.
4. Sensitive-data sweep: no `~/.cache/huggingface/token`, no `HF_TOKEN` or `hf_…` string in any history, rc file,
   script or log, no credential store or `.netrc`, plain HTTPS remotes only. **Count matches; never read grep's
   exit status as the verdict** (`grep -rls … | awk 'END{print NR}'`), and use a planted positive control. Then
   `rm -rf ~/.cache/huggingface` — **which on this campaign removes ~22.5 GB of gated weights**, so confirm the
   removal by listing, not by the command's exit. Because the weights were staged offline (§6), step 4's assertion
   is the strong form: no token ever existed here.
5. Stop every process of ours; `ps -u $(whoami)` then shows only the system's own session.
6. Terminate, wait, and **read the state back** — not the API's acknowledgement — then record the UTC time. The
   provider drops terminated instances from its listing within hours, so the durable form is the negative that
   persists: query by instance-id filter and require zero reservations, with a live instance as the positive
   control. Confirm no unattached volume survived.
7. Report: box vs mirror `report.json` sha256 (must match), what step 3 pulled with sizes, what step 4 found, the
   termination read-back, the release time. No run numbers in the release report — the summarizer is where numbers
   are read.

## 11. R8 — backup, both directions, with the inputs

Push **from the verified home mirror only**, never from the box, and never while a summarizer is running against a
hardlinked staging tree. Order: small records first, then the tensors in one resumable `upload-large-folder` (one
worker), then the card last as the "complete" marker. Then `tools/hf_verify_backup.py` must end in
`BACKUP VERIFIED`: it compares every LFS file's `lfs.sha256` against the local sha256, downloads and hashes every
non-LFS file, and checks **both directions** for missing files. A finished upload command is not a finished backup;
only the verifier is.

**This campaign's addition: the upstream *inputs* go in too.** Every prior dataset holds only outputs, which is
precisely why the Qwen τ cannot be recomputed from any checkout today (the upstream has no `data/` at all and
`results/probe/qwen3-0.6b-to-1.7b/` holds only a figure and a summary). So each sitting's dataset carries, in the
upstream's own layout under its own top-level directory:

- `data/tokens/llama3.2-3b-to-llama3.1-8b_n50_len1024_seed0.npy`
- `data/kv/llama3.2-3b-to-llama3.1-8b/{source,target}/` (1.47 + 1.68 GB)
- `results/probe/llama3.2-3b-to-llama3.1-8b/*.npy`
- `results/mapper/llama3.2-3b-to-llama3.1-8b/r2.json` and `mappers/llama3.2-3b-to-llama3.1-8b/k{1,4,8}.*`

Budget before the sitting, not during: a push is rate-limited by **commits** (128/hour, and the Python API batches
commits too, so it is not a way around it) and backups compound in **bytes** — the four existing datasets already
document ~187 GB against a 100 GB private allowance, and E9-long's push died twice on the limit and once on a 429.
Make these datasets **public** (operator ruling, 2026-09-11: the tensors are KV of public models over public
benchmark traces), plan several hourly windows, and sweep the staging tree's text files for credential shapes with
a planted positive control before the first push. Dataset names stay out of double-blind paper material. Tokens
per R9: fine-grained, scoped to the one dataset, expiring, `read -s` **on a line of its own**, `hf auth whoami`
before the long command, `unset` and revoke after.

## 12. Where each protocol rule lands in this campaign

| rule | this campaign's instance |
|---|---|
| R1 registered before requested | the registration entries (`docs/drafts/`, provisional numbers allocated at staging); τ, band, cap, floor, seeds, `verdict_k = 1`, `s_pos_edges` and the keep draw are all fixed before a score file exists |
| R2 budget the forward | §3, and the **fixed** `probe_e9l.py` on the real card — §3.4 is extrapolation and may not authorize a launch by itself |
| R3 everything by sha | §5; nothing starts with one of its own rows unfilled |
| R4 launch detached, rotate, never self-match | `run.sh` with `python -u`; liveness from `~/<exp>.rc` and `report.json`, never the log, never a self-matching `pgrep` |
| R5 pull, verify, delete | `pull.py <exp>`; mandatory here — 12.4 GB (B) and 30.9 GB (C) per handoff |
| R6 nothing only on the box | `verify_mirror.py <exp>` from raw bytes before any deletion |
| R7 release | §10 |
| R8 backup | §11, **including the upstream inputs** |
| R9 tokens | §11; and §6 means no token is ever on a box |
| R10 what goes where | unchanged; the staged weight cache is "never on the box after release" |
| R11 the summarizer is the only reader | `summarize_e8` / `summarize_e9`; a refusal is pasted verbatim and investigated. The Llama configs' three pair-calibrated τ fields refuse **fail-closed by type** until they are real: `load_e9_config` requires `tau_K` / `tau_V` / `tau_agent_K` to be numbers in (0, 1) and names the missing calibration when they are not, so an `UNRESOLVED::tau_K@<pair>::…` marker raises `ValueError` and the config does not load at all. The absolute ladder `[0.10, 0.03]` and prefix delta `1e-4` were already literal, registered values; they were never unresolved markers |
| R12 re-verifiable by someone who was not there | §12's log, the pulled logs, and the R8 datasets with the inputs in them |

## 13. Traps carried

From 09-08 / 09-10 / 09-13, all still live: the launch line stands alone (a chained `setsid … & sleep; …` holds the
pipe); `python -u` or a buffered log shows nothing until exit; never `> <exp>.log` on a relaunch (`run.sh` rotates);
PyPI torch is a cu130 build and the box takes the cu128 index; strip CRLF before `put` or a box script is a
`bad interpreter`; the release sweep's step 0 classifies by mtime against launch; `read -s` runs alone and
`hf auth whoami` is the confirmation; a push needs several 128-commits/hour windows; a hardlinked staging tree is
live under the uploader; the home puller re-pulls a small file on size **or** mtime change; `setup.sh` clones at
`LC_SHA`, which must already be on GitHub.

New to this campaign: the receiver is an 8B, so **every card estimate in every prior runbook is wrong here** —
re-read §3 rather than reusing a number from 09-10; `HF_HUB_OFFLINE=1` means a missing snapshot fails as a
confusing cache miss rather than a download, so verify the staged cache before `setup.sh`; and the two models'
`inv_freq` vectors differ **by design**, so any assertion that treats them as equal across roles is a bug in the
assertion, not a finding about the run.

## 14. Log (UTC; filled during each sitting)

### Sitting A — E8 calibration and fit
- (empty)

### Sitting B — E9 short
- (empty)

### Sitting C — E9 long, native receiver (cuttable)
- (empty)
