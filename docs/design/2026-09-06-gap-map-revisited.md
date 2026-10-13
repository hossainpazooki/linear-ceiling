# Gap map, revisited

**Date:** 2026-09-06 · **Status:** reassessment of `docs/gap-map.md` (2026-08-26, committed
verbatim by entry 0005) against the ledger as it stands at entry 0030. The original is immutable
and is not edited; this document appends a verdict under each of its claims and cites the entry
that carries every figure. No number here is new: each one is quoted from the named entry, which
recomputed it through the fail-closed summarizer. Where a clause of the original has not been
tested, this says so.

The short form: the three gaps are real, and the program could not fill two of them from the
public record, because the public record does not carry the fields cache economics needs. The
three intuitions were tested; one is negative, one has no support, one is half right. The one
piece of the original that stands untouched is definitional.

| original claim (2026-08-26) | status at 0030 | what the ledger says | entries |
|---|---|---|---|
| Framing: compression is cache-compatible, compaction is cache-destroying | **stands** | definitional; nothing tested it | — |
| Framing: agentic serving is where cross-model boundaries occur | **failed on the public record** | every observed switch is one designed critic/selector family; the kill condition fired and the motivation reverted to different models serving different requests | 0005, 0015 |
| Gap 1: invalidation taxonomy for agentic runs | **filled in structure, empty in frequency** | six classes registered before any count; most cells NOT MEASURABLE because the traces do not record the fields | 0014, 0015 |
| Gap 2: compaction economics, priced on real traces | **still missing, unfillable from public corpora** | zero compaction events on the 800 trajectories that could show one; only the pricing pins shipped | 0007, 0015 |
| Gap 3: cache-aware cross-model routing | **second clause unsupported at k = 1** | the map fails on content shift; at a real re-render the same-model floor is zero and the cross arm sits beyond DEGRADES, so the router's missing fact is a binary | 0020, 0029 |
| "Who's nearby" attributions (footnote: verify at source in W1) | **never closed** | no ledger entry records a lit-sweep verdict; cannot ship as written | — |
| Intuition 1: switches frequent, headroom material in dollars | **NOT CONFIRMED** (H-E7a) | 0.20% of spend vs a 10% cutoff under the registered reading; the request-level reading of 0024 sits at the cutoff and awaits a ruling | 0006, 0015, 0018, 0022, 0024 |
| Intuition 2: compaction common, break-even often negative | **UNESTIMABLE** (H-E7b) | no support where measurable, NOT MEASURABLE elsewhere | 0015 |
| Intuition 3: both extractable by CPU replay, no forward passes | **half right** | extracted as proposed, but every cost figure is a lower bound: hidden prefix omitted, no timestamps; Lane B dollars withdrawn | 0007, 0011, 0012, 0021 |

## The framing correction

*Original:* agentic serving is where cross-model cache boundaries occur; two events destroy the
cache, model switch and compaction; compression is cache-compatible, compaction is
cache-destroying.

*Now:* the compression/compaction distinction is definitional and nothing in the program touched
it; it stands. The claim that agentic serving is *where boundaries occur* was tested on the
public record and failed there (below): across 2,904 public trajectories, every observed
mid-trajectory switch comes from one designed critic/selector family (0015). The README's
scope reading of that cell, not a ledger claim, adds why: public benchmark trajectories are
single-model leaderboard runs by construction, so the cell decides what the public record
evidences, not what production routers, fallbacks and cost tiers do. The boundary the
program now works on is the one that exists without observation: a weight update under an
in-flight cache (E-RL, `docs/2026-09-02-e-rl-design.md`, design only, unregistered). That is the
"fleet-mixing" reversion entry 0005 registered as the kill condition, and it fired as written.

*The break-even inequality* ("unwritten as of the W1 lit sweep, to be re-verified there") is
still unwritten in priced form, and this program cannot write it: see gap 2.

## Where people are missing: the three gaps

### Gap 1 — invalidation taxonomy for agentic runs

*Original:* the prefix-caching literature assumes append-only; nobody accounts for *why* caches
die on real trajectories (compaction vs switch vs branch vs edit).

*Now — filled in structure, empty in frequency.* Entry 0014 registered six event classes
(model_switch, rerender_at_switch, compaction, idle_expiry, branch, edit), each with a
detection rule and a measurability rule, before any count was taken. Entry 0015 is the first
frequency table, and its content is the finding: of 2,904 trajectories across three suites,
the switch classes are measurable on 60, compaction and idle expiry on 800, branch on 4, edit on
none. Everything else is NOT MEASURABLE, which the rule keeps out of both numerator and
denominator rather than recording as zero. The gap the original named was an accounting gap
("nobody counted"); the ledger says it is a recording gap ("the traces do not carry per-step
model, timestamps, request sizes, or the hidden prefix, so counting is impossible from the
public record"). Restated honestly, gap 1 is: **public agent trace formats drop every field an
invalidation accounting needs.** The taxonomy is the instrument for the day a corpus that keeps
those fields exists; `docs/2026-09-01-swe-bench-trace-recon.md` records what each format does
and does not keep.

### Gap 2 — compaction economics

*Original:* compaction is treated as free context hygiene; the break-even inequality, priced on
real traces, is missing.

*Now — still missing, and not fillable from any public corpus that exists.* H-E7b is
`UNESTIMABLE` (0015): zero compaction events on the 800 trajectories that record per-request
prompt sizes (tau2-bench, the only suite that does), and NOT MEASURABLE on the other 2,104.
Entry 0005 registered this outcome in advance and 0015 states it. The reading is narrow by
rule: it is not a claim that compaction does not occur in practice; final-transcript traces
structurally cannot show it, and on the one corpus that could, context only grows. A corpus
that both records per-request prompt sizes and compacts would reopen H-E7b by a numbered entry;
none is scheduled. The pricing premise the original leaned on ("cached input tokens priced
about an order of magnitude below fresh prefill") was pinned as the cost-model parameters of
entry 0007 with sources and retrieval dates; it is the one part of gap 2 that shipped.

### Gap 3 — cache-aware cross-model routing

*Original:* routers ignore cache state at the model boundary; transfer changes what a switch
costs, and no router knows it.

*Now — the second clause is unsupported for a linear mapper, and the first clause changes
shape.* Two results bear on it. H-E8 `NOT CONFIRMED` (0020): the k = 1 mapper fit on generic
text loses held-out R² on agent text by +0.1185 (K, inside the registered dead band) and +0.1715
(V, DEGRADES), with no switch and no position change; content shift alone breaks it. H-E9
`HELD` (0029), descriptive cross arm: at 25 real re-rendered SWE-bench handoffs the same-model
oracle recompute fraction f*(τ_K) is 0.0000 at every matched token of every handoff, while the
cross-model arm through the same mapper sits at a median 0.9286, beyond the DEGRADES edge. Read
together for this pair: at a re-rendered handoff, same-model reuse is free on an oracle floor
and cross-model linear transfer is not usable. What a cache-aware router would need to know is
therefore not a transfer quantity but a binary: is the boundary same-model or not. "Transfer
changes what a switch costs" is not established at k = 1 on this pair; 0029 is explicit that
this is a floor (oracle selection, recompute in isolation), one pair, one direction, the shorter
half of the corpus by |S|.

### The attribution footnote

The original's "who's nearby" column carries its own condition: every attribution "requires
primary-source verification in the W1 sweep before appearing in the paper." The design spec
scheduled that sweep as a gated W1 task with its verdict recorded in the ledger. **No ledger
entry records a lit-sweep verdict**, and no doc in `docs/` closes the footnote (checked
2026-09-06 by grep over the ledger, README and docs for the sweep and the named lines). The
three attributions therefore remain unverified and cannot appear in the paper as written until
that check is done and recorded. `docs/2026-09-01-measurement-lane-evidence.md` pins the venue
and pricing facts the re-scope rested on; it does not verify these three rows.

## Intuitions, stated as falsifiable claims, and how they fell

*Intuition 1 — switch points are frequent enough that transfer headroom is material in dollars.*
**NOT CONFIRMED on the public record** (H-E7a, 0015 → corrected 0018). Lane A finds 68
switches on 60 measurable trajectories, all in one system's designed critic stage, and 0 of 68
hand the receiver a byte-identical prefix (0015, 0018). Under the registered denominator the
recoverable prefill is 0.20% of the measurable set's input spend against the 10% cutoff of
entry 0006 (0018); 0022 shows the exact tokenizer moves it to 0.2210%, still an order of
magnitude under. The numerator is an upper bound (0010, 0013) and every trace-only denominator
is a visible-only lower bound (0012), so the true ratio is lower still. One open item binds the
reading: entry 0024 records that under a request-level denominator the same numerator reads
10.0012% cold and 8.60% warm, at the cutoff under one of four readings; the registered reading
decided the cell and choosing between readings is a ruling not yet made. The paper must state
both readings; this document does not choose.

*Intuition 2 — compaction events are common enough to estimate the break-even distribution, and
it often goes negative.* **No support** (H-E7b `UNESTIMABLE`, 0015). See gap 2. The second half
of the intuition was never reachable because the first half has zero events where it can be
measured.

*Intuition 3 — both numbers are extractable by CPU replay of public trajectories against a
published-pricing cost model, no forward passes required.* **Half right.** The taxonomy and the
switch headroom were extracted by CPU replay exactly as proposed (0013–0018), and the coverage
floor was met on two suites (0011). But every cost figure is a lower bound, because
provider-reported usage on tau2-bench shows the public traces omit a fixed cacheable prefix of
about 3,400 tokens on agent requests (0012), and no suite records timestamps, so expiry is
bracketed by a warm and a cold bound rather than measured (0007). The replay extracts what the
traces carry; the traces do not carry enough. The dollar counterfactual on the cascade lane
(Lane B) was withdrawn as material by construction (0021), so the "in dollars" half of
intuition 1 was never decided on a policy the program chose.

## What this does NOT change

Nothing sealed moves. The scope sentence in the README stands verbatim and this document does
not restate it. H-E7a `NOT CONFIRMED`, H-E7b `UNESTIMABLE`, H-E8 `NOT CONFIRMED`, H-E9 `HELD`
are decided cells and this document reads them, never re-reads them. The original gap map
stays in the tree unedited as the record of what was believed on 2026-08-26; a reader who wants
the motivation as first written reads it there, and reads here for what the tests returned.

## Open items this reassessment surfaces

1. The 0024 request-level reading ruling (intuition 1 above). Until it is made, H-E7a's
   sentence in any draft must carry both readings.
2. The lit-sweep verdict: verify the three "who's nearby" attributions at source and record the
   result, or drop the column from the paper.
3. Whether the paper's motivation section is the original gap map with these verdicts appended,
   or is re-cut around the recording gap. This document takes the first shape by the operator's
   choice (2026-09-06) and leaves the second open.
