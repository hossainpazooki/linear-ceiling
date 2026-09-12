# GPU runs after the PIC pivot — what would add to the paper, and why none is needed for it

**Date:** 2026-09-11 · **Status:** proposed, unregistered, unnumbered. Nothing here is a ledger figure, and
nothing here is scheduled. Written in answer to the operator's question "do you need additional GPU box runs
for the pivot?" after the review of the 2026-09-11 v3 seed (`docs/paper/2026-09-11-seed-lcfm-v3.md`).
Every number cited below is quoted from the ledger entry beside it at repo HEAD `d0b91db`.

## The answer

**No run is needed for the pivot.** The pivot reframes the paper around the quantity E9 already measures
(the post-position-correction residual of non-prefix reuse, read as an oracle recompute floor, 0023/0027);
every figure the seed's §2 and §3 use is on the ledger in 0018, 0023, 0027, 0029 and 0036. The two clauses
the seed leaves open are literature lookups (a PIC paper's maximum evaluated context; CacheBlend's selection
rule and units), not measurements.

## What a run could add, ranked, with why each is deferred

### 1. A downstream-quality number (the gap the PIC frame exposes)

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
4-pager states the gap as a limitation. It is the first item for a follow-up or camera-ready.

### 2. The n = 420 mapper arm on the E9-long kept subset

CPU only: `e9_rescore` over the six kept directories with the tagged n = 420 mapper, as 0033/0034 did for
E9's eight. Needs its own config (`config/e9lc.toml`) and numbered entry. Sharpens the cross arm, which
0029 and 0036 mark descriptive and the pivot moves further to the margin. Skip for the 4-pager.

### 3. More long handoffs

None available at this cap: 0035 registered all 35 handoffs above the prior cap, and the four excluded
ones are 147K–358K (0036 coverage), beyond an L40S under YaRN 2.5 and beyond the bridge control's
warrant for τ_K. A larger cap is a new registration with its own bridge, not an extension.

### 4. A second model pair (not raised by the seed; a PIC reviewer will)

Every same-model figure is Qwen3-1.7B on one pair. A second family at the short cap would be a repeat of
the E9 sitting (~40 min on a 40 GB slice, 0029) after a new 0016-style calibration for τ_K on that family.
Worth registering only if the paper's claim is to generalise across families, which v2 and the seed do not
make.

## Not a run: the two lookups that gate §2's clauses

- CacheBlend's recompute budget in its own units and its selection rule, to write the HOLDS anchor beside
  0027's floor reading without a units mismatch.
- The maximum evaluated context of at least CacheBlend, EPIC and KVShareArena, or drop the "none at this
  length" clause.
