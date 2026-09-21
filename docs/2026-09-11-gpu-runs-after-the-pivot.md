# GPU runs after the PIC pivot — what would add to the paper, and why none is needed for it

**Date:** 2026-09-11 · **Status:** proposed, unregistered, unnumbered. Nothing here is a ledger figure, and
nothing here is scheduled. Written in answer to the operator's question "do you need additional GPU box runs
for the pivot?" after the review of the 2026-09-11 v3 seed (`docs/paper/2026-09-11-seed-lcfm-v3.md`).
Every number cited below is quoted from the ledger entry beside it at repo HEAD `d0b91db`.

> **Amendment, 2026-09-20 — two errors in this document, found by an outside review on 2026-09-12 and
> confirmed against the ledger; the text below is left as written.** (1) "The six E9-long kept
> directories" (items 2 and 3) are not six long handoffs. 0035 keeps **three** long handoffs by a seeded
> draw (n = 3, seed 9); the other three directories are the configuration-bridge control, the three
> shortest of 0029's kept handoffs prefilled native and scaled and scored at (p, p). They are not
> long-cell observations, and the rescorer needs a source dump plus both receiver dumps per handoff.
> Usable kept handoffs: eight short, three long. (2) The sentence above is false for three figures in
> item 2: **57 GB**, **31.56 GiB** and **~2 h**. None is in the ledger (the "0036" beside 31.56 GiB is not a
> ledger citation); the memory figure is from the operational protocol, the runtime is a projection, and
> neither sizes a cache-injection workload. Record: `docs/2026-09-20-astra_review.md` §4.

## The answer

**No run is needed for the pivot itself.** The pivot reframes the paper around the quantity E9 already measures
(the post-position-correction residual of non-prefix reuse, read as an oracle recompute floor, 0023/0027);
every figure the seed's §2 and §3 use is on the ledger in 0018, 0023, 0027, 0029 and 0036. The two clauses
the seed leaves open are literature lookups (a PIC paper's maximum evaluated context; CacheBlend's selection
rule and units), not measurements.

**One run is worth registering for the length argument, and the first version of this document missed it**
(raised by the 2026-09-11 chat session, confirmed here): the scaled configuration on the original 25 short
handoffs, item 1 below. The deadline was extended to 2026-09-13 23:59 AoE (= 09-14 11:59 UTC; CFP page read
2026-09-11), so it is feasible if registered now.

## What a run could add, ranked

### 1. The scaled short cell: 0029's 25 handoffs under 0036's receiver configuration (the one to register)

**Why.** §5.1 (native receiver) and §5.2 (YaRN 2.5 receiver) differ in configuration as well as length. The
bridge control (0036 control 4) shows YaRN alone moves content keys by median δ_K 0.071–0.089 on three short
handoffs — the same order as the cross-cell far-from-seam difference (0.019 → 0.063) and a plausible part of
the ladder shift (0.1433 → 0.5255 at τ = 0.03). Measuring the 25 under the scaled configuration removes that
confound from every "what length changes" figure. Differences between the two handoff sets still prevent a
causal claim about length alone; the paper's descriptives become configuration-matched, which is the claim
a reviewer will test. No verdict moves: the run is descriptive, H-E9 and H-E9L stay as decided.

**What exists.** The driver and summarizer already take `[e9.rope]`, `context_floor = 0` and no bridge
(`config.py` validation: cap ≤ original × factor; floor 0 allowed; `bridge`/`profiles` optional). The
alignment at cap 32,768, floor 0 must reproduce 0029's coverage (25 included) exactly — a gate, not an
assumption. Memory: the 0036 probe measured the 1.7B forward at T = 32,768 under YaRN at 16.70 GiB, equal
to the native 16.72 on the 20 GB slice E9 ran on, so the E9 slice suffices; E9 scored 25 in 38 min (0029).

**What has to be built (this session's side), in order:**
1. `config/e9s.toml`: `config/e9.toml`'s rule, controls, alignment, mapper and keep sections byte-identical;
   `results_dir = "results/e9s"`; `context_cap = 32768`, `context_floor = 0`; `[e9.rope]` as `e9l.toml`;
   `upstream_sha = 063f402…`; `required_entries` = 0019/0023/0025/0027 plus the new registration entry.
2. The registration entry, before any prefill: the 25 by id; the receiver and source configuration; the
   statistic, thresholds and controls unchanged; the pre-stated reading — per-handoff paired native-vs-scaled
   comparison of mean δ_K, the τ ladder and the seam profile; what agreement means (a paired difference within
   the bridge's own δ_K reads "configuration accounts for ≤ x of the cross-cell difference"); descriptive,
   nothing decided.
3. A comparison in `summarize_e9` (or a small `e9_compare` module) that reads `results/e9/summary.json` and
   `results/e9s/summary.json` per handoff, fails closed on any id mismatch, and emits the paired table.
4. Probe, launch, pull, verify, release by R1–R12; backup by R8.

**Cost.** One GPU sitting of about an hour on the E9 slice; builds and a review before it, a summarizer pass and
an outside read after. It enters the paper only with its entry; otherwise §5.2 states the configuration
difference and makes no length-alone claim (outline v3 §5.2, §6).

**Status 2026-09-13: BUILT, registration STAGED, not run.** `config/e9s.toml`, `src/linear_ceiling/e9_compare.py`,
`tests/test_e9_scaled_short.py`, `docs/drafts/append_0037.py`; the GPU session's seed is
`docs/2026-09-13-seed-e9-scaled-short-cell.md` (decisions D1–D4, the home and box definitions of done, the
registered reading). For the camera-ready: the submission deadline (09-14 11:59 UTC) is before any sitting.

### 2. A downstream-quality number (the gap the PIC frame exposes)

PIC papers report task quality against full recompute; E9 reports KV deviation only, and 0029/0036 state
that generation quality after reuse is not established. The experiment that closes this is the one 0023
already names as `[STRETCH]`: "real CacheBlend-style partial prefill — recompute the top-f tokens against the
reused KV, measure attention-output deviation and a downstream task delta. Needs injection code upstream and
a task; it is the experiment that would make f* an achieved number rather than an oracle floor."

What it needs, in order: (a) KV injection in the upstream (`../kv-transfer-replication`, read-only from
here, so its own commit there and a re-pin); (b) a task with a scorer — SWE-bench pass/fail is out of reach
per handoff, so a proxy on the receiver's next generation (e.g. next-turn log-likelihood or exact-match of
the sender-observed continuation) has to be chosen and registered; (c) a numbered entry before any prefill
that fixes the recompute rule (which tokens, in what order, against what) and the reading; (d) a
fail-closed summarizer; (e) a box: the six E9-long kept directories (57 GB at home) plus a receiver forward
per handoff under YaRN 2.5 is the same footprint as the E9-long sitting (L40S 48 GB, 31.56 GiB peak at
T = 80,111, 0036), so one rented g6e.4xlarge sitting of ~2 h covers the kept subsets of both halves.

Why deferred: it is a new experiment with a different claim (achieved, not floor), not a rerun, and the
4-pager states the gap as a limitation. It is the first item for a follow-up or camera-ready, and the
strongest subsequent experiment.

### 3. The n = 420 mapper arm on the E9-long kept subset

CPU only: `e9_rescore` over the six kept directories with the tagged n = 420 mapper, as 0033/0034 did for
E9's eight. Needs its own config (`config/e9lc.toml`) and numbered entry. Sharpens the cross arm, which
0029 and 0036 mark descriptive and the pivot moves further to the margin. Skip for the 4-pager.

### 4. More long handoffs

None available at this cap: 0035 registered all 35 handoffs above the prior cap, and the four excluded
ones are 147K–358K (0036 coverage), beyond an L40S under YaRN 2.5 and beyond the bridge control's
warrant for τ_K. A larger cap is a new registration with its own bridge, not an extension.

### 5. A second model pair (not raised by the seed; a PIC reviewer will)

Every same-model figure is Qwen3-1.7B on one pair. A second family at the short cap would be a repeat of
the E9 sitting (~40 min on a 40 GB slice, 0029) after a new 0016-style calibration for τ_K on that family.
Worth registering only if the paper's claim is to generalise across families, which v2 and the seed do not
make.

## Not a run: the corrective reading of f* (found 2026-09-11, in flight elsewhere)

0023 defines f*(τ) on the **mean** deviation of the tokens left after oracle recompute, so f* = 0 says the
full-set mean is within τ_K — not that every token is. Recomputed from the raw token records with the
summarizer's own functions: 5.8% of matched tokens exceed τ_K on the short cell and 7.9% on the long, on every
handoff, while every per-handoff mean (0.028–0.269) is under 0.3186. 0029's "at every matched token of every
handoff" sentence and every draft that copied it ("not one matched token exceeds τ_K") over-state the
statistic. A corrective ledger entry is being closed by the 2026-09-11 chat session; the tail figures need a
summarizer figure before any of them enters the paper. Outline v3 is corrected; no GPU is involved.

## Not a run: the two lookups that gate §2's clauses

- CacheBlend's recompute budget in its own units and its selection rule, to write the HOLDS anchor beside
  0027's floor reading without a units mismatch.
- The maximum evaluated context of at least CacheBlend, EPIC and KVShareArena, or drop the "none at this
  length" clause.
