# LCFM plan with GPU runs — resources, what runs where, and what must be registered first

**Date:** 2026-09-01 · **Status:** PLAN (nothing here is built or registered; entries named
below are drafts until they are in the ledger). LCFM deadline 2026-09-10 AoE; numbers-freeze
gate EOD 2026-09-08 (entry 0006). Anchor venue unchanged: MLSys 2027.

## The resource (Algoverse A100 portal, as described 2026-09-01)

| fact | consequence for this plan |
|---|---|
| request via web form, admin-approved queue; 1- or 2-day grants | request **now**; approval latency is the schedule risk, not compute |
| countdown starts at approval, not first login; ~20 usable h per 24 | have the run script tested end-to-end on CPU at tiny sizes BEFORE requesting |
| machine deleted at expiry; reminders at 36/24/12/2 h (2-day) | every artifact is pulled to local `results/` after each stage, never at the end |
| idle ~1 h → may be reclaimed | one batch driver runs everything; no interactive sessions; log off when done |
| A100 40 GB, possibly **shared** (assume 20 GB) | bf16 weights; Qwen3-1.7B at 32k context KV ≈ 3.7 GB — fits even shared |
| backup CPU machine when the queue is full | everything in Tier 1 runs on CPU anyway; only Tier 2 is GPU-bound |

Discipline on the box: `results/` synced to local after each stage (`rsync`/`scp` from the
driver, not by hand); models and FineWeb stream from the Hub (internet assumed); the upstream
checkout on the box is the **pinned** commit plus whatever the amendment entry re-pins.

## What actually needs a GPU — a correction first

Entry 0009 said the upstream's KV dumps were gone. **They are not**: `data/kv/qwen3-0.6b-to-1.7b`
(2.8 GB, 50 sequences) and `data/kv/qwen3-0.6b-to-1.7b-n420` (12 GB) exist locally, with the
fitted mappers `mappers/qwen3-0.6b-to-1.7b/k{1,4,8}` — all gitignored, so they live only on
this machine. Consequences:

- **E8 needs no GPU.** Arm (a) (generic text) is the archived held-out R² and can be re-scored
  locally in minutes; arm (b) (agent-trace text) is one dump pass of both models over ~50
  sequences: 12 min on CPU (upstream's measured wall-clock). Scheduling E8 on the A100 would
  waste the grant; run it here, this week.
- **The verdict-bearing mapper must be k = 1.** Upstream held-out pooled R² at n = 50:
  k=1 K 0.681 / V 0.513; k=4 K 0.591 / V 0.336; k=8 K 0.098 / V −0.641 (collapsed, p/n = 0.8).
  A "drop" from a collapsed baseline is meaningless, so E8's band applies to k=1; k=4/8 are
  reported, never verdict-bearing.
- **The GPU's job is Tier 2 (E9)**: two long-context prefills per real handoff, 68 handoffs,
  up to 32k tokens each — hours to days on CPU, well under an hour on an A100.

## Tier 1 — E8 on CPU, this week (registered; needs one amendment)

Design as registered in entry 0009 (existing mapper, no refit; held-out pooled R² on generic
vs agent-trace KV; HOLDS ≤ 0.05 drop, DEGRADES ≥ 0.15, K and V separately). Still to register
BEFORE arm (b) is dumped, in one amendment entry:

1. **E8 may appear in the LCFM 4-pager** if it clears the same fail-closed summarizer gate as
   every other number — restoring entry 0006's allowance ("the transfer-fidelity leg ... appear
   only if they clear the same gate") that 0009(4) narrowed. Lane A/B + taxonomy remain the
   scope cap's core; E8 is one paragraph and one table.
2. **Correction of 0009's "dumps are gone"** (see above), with the local paths and sizes.
3. **Verdict-bearing k = 1**, for the reason above; k=4, k=8 reported alongside.
4. **Agent-text sampling rule** for arm (b): one 1024-token window per trajectory, taken from
   the concatenated visible message text (system/user/assistant/tool, in trace order,
   role-tagged), drawn with the repo's single seeded RNG from the tau2-bench and SWE-bench
   suites stratified equally, tokenized with the Qwen3 tokenizer (shared across the pair —
   `weights.assert_shared_vocab`), n = 50 sequences to match arm (a)'s protocol exactly
   (`--stride 4`, held-out by sequence, same `holdout_frac`). Text is off-policy for Qwen
   (0009's scope limit stands).
5. **Upstream change and re-pin.** No upstream script scores an *existing* mapper on *new*
   dumps (`kvt.mapper.mapper_r2` is library-only). Add `scripts/score_mapper.py` upstream
   (load mapper + two dumps + mask → `r2.json`), commit there, and re-pin `UPSTREAM.md` in the
   same entry. The "never import kvt" rule holds: linear-ceiling invokes it by subprocess.
6. **Gate**: `e8.assert_ready` mirrors `e7.assert_ready` — refuses until the amendment entry
   and `config/e8.toml` (seed, n, k list, band) are committed unmodified.

**Status 2026-09-01 (late): BUILT and gated, not run.** `config/e8.toml`; `e8_text.py`
(sampling rule → token `.npy` in linear-ceiling's own `data/`); `e8.py` (gate incl. the
upstream pin + subprocess `dump_kv.py --tokens … --out …` and `score_mapper.py` in the
upstream env, writing `results/e8/`); `summarize_e8` (fail-closed: re-runs the upstream scorer
on fingerprinted dumps and compares; states the band outcome, never a verdict); 23 tests on a
fake upstream. `scripts/score_mapper.py` is written in the upstream tree, uncommitted, and
verified to reproduce the archived k=1 `r2.json` exactly. Entry 0016 is drafted
(`docs/drafts/append_0016.py`, takes the upstream sha). Then a `[BASELINE]`/verdict entry
from the summarizer.

## Tier 2 — E9 on the A100: how much of the upper bound is achievable at a re-rendered handoff

Entry 0013 records headroom as an UPPER BOUND and says the achievable fraction "is not
measured here". E9 measures it, on the 68 real handoffs, and is the run the GPU exists for.

**Unit.** One observed Lane A switch: sender context `S` (every message before the switch) and
receiver prompt `R` (the re-rendered prompt), both as text from `e7_swe.load_composio_detailed`.

**Alignment (CPU).** Tokenize `S` and `R` with the Qwen3 tokenizer; match tokens by a
longest-common-subsequence over token ids (registered method; the token-level analogue of
0010's word multiset); the matched set `M` with positions `(p_S, p_R)` per token. Report
`|M| / |R|` beside 0010's word overlap.

**Two measurements, both pooled R² (definition A5), K and V separately, on `M` only:**

- **E9-same (the ceiling under re-rendering, model-independent of any mapper):** the receiver
  model (Qwen3-1.7B) prefills `S` and `R` natively; compare its KV at `p_S` (re-roped to `p_R`,
  content space) against its own KV at `p_R`. This is how much KV of a content-matched token
  survives having a different preceding context — the true achievable ceiling for ANY transfer
  across this handoff, and the number that turns 0013's upper bound into a measured fraction.
- **E9-cross (the transfer):** Qwen3-0.6B prefills `S`; apply the k=1 content-space mapper
  (`kvt.mapper.apply_mapper(m, src_kvs, positions=p_R)` — exists upstream, re-ropes at the
  receiver positions) and compare against the receiver's KV at `p_R`. Reported as a fraction of
  E9-same, so mapper error and re-render loss are never conflated.

**Hypothesis H-E9 and band — APPROVED by the operator 2026-09-01, drafted verbatim in
`docs/drafts/append_0017.py`:** *at a re-rendered handoff, the same-model KV agreement on
content-matched tokens (E9-same) retains the transfer-relevant fidelity.* HOLDS if median
E9-same pooled K R² ≥ 0.70, DEGRADES if ≤ 0.40, UNRESOLVED between; V reported alongside,
verdict-bearing for nothing. Reason: 0.70 ≈ the k = 1 mapper's own same-text held-out K R²
(0.681), so HOLDS means "the re-render costs no more than the mapper does". Frozen before the
first prefill by the entry's position in the chain.

**Scope limits, registered up front.** Context cap 32,768 tokens (Qwen3 native): handoffs with
`|S|` or `|R|` above it are EXCLUDED and counted (p90 paid is 93,805 tokens, so expect a third
or more excluded — report coverage, never truncate silently). Off-policy text (Qwen did not
produce it). One pair. Composio is one system (0011). E9 says nothing about what a router
would do; it bounds what a transfer could recover at the one public instance of the use case.

**Compute.** 68 × 2 prefills ≤ 32k tokens on 1.7B + 68 × 1 on 0.6B, bf16: minutes of GPU per
model; alignment and scoring on CPU. Whole run < 1 h on the A100; budget 4 h for the dump
files and the sync. A 1-day grant is enough; request 2 days only if E8 slips onto the box.

**Build (~2 sessions, all testable on CPU at 64-token sizes):** `config/e9.toml`;
`e9_align.py` (tokenize + LCS + exclusions, pure CPU, tested); an upstream
`scripts/dump_positions.py` (one variable-length sequence → KV at every position, no stride;
the existing `dump_kv.py` assumes `[n_seqs, seq_len]` with stride — another upstream change
in the same re-pin); `e9.py` (gate + subprocess driver + per-handoff checkpointing so a
reclaimed box loses one handoff, not the run); `summarize_e9` (fail-closed); tests.

## Schedule (today = 09-01)

| when | what | gate |
|---|---|---|
| 09-01 | ~~commit 0013/0014; taxonomy run + summarizer; entry 0015~~ **DONE**: H-E7a `NOT CONFIRMED` (1.41%), H-E7b `UNESTIMABLE` | — |
| 09-02 | submit the A100 request (1 day; 2 if E8 slips); draft + commit the E8 amendment entry; build E8; run E8 on CPU; `summarize_e8`; E8 verdict entry | nothing reads a dump before the entry is in HEAD |
| 09-03/04 | draft + commit the E9 registration entry (H-E9, band, alignment method, cap); build E9 end-to-end on CPU at toy sizes; re-pin upstream with the two scripts | **go/no-go EOD 09-04**: E9 runs on the GPU only if its CPU toy run is green and the entry is committed; otherwise LCFM ships trace-only + E8 |
| approval day (est. 09-04/05) | E9 batch on the A100 within the first 2 h; sync; log off | per-handoff checkpoints synced |
| 09-06/07 | `summarize_e9`; E9 verdict entry; draft the 4-pager from summarizer output only | every number recomputes clean |
| 09-08 EOD | numbers freeze | entry 0006 |
| 09-10 AoE | submit | non-archival; MLSys dual-submission permitted |

## What this does NOT change

Lane A alone decides H-E7a (0007); unmeasurable is never zero (0006/0014); every trace-only
cost figure is a lower bound and headroom an upper bound (0010/0012/0013); the seal is not
involved in E8 or E9 (0009 — both evaluate already-fitted mappers or the same model; no
pre-fit claim is made); the upstream stays read-only except by a re-pinned commit recorded in
a numbered entry. If H-E7a resolves negative (the recon says it will), E9 is still worth
running: it is the achievable-fraction number for the one place a switch was observed, and
the paper's framing becomes "the use case exists, is rare, and here is what transfer could
and could not recover at it" — which is a measurement paper's honest shape.
