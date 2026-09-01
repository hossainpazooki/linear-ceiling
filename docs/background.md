# Background: how this program got its shape

The README carries the current state, the discipline, and the visuals; this file carries the
narrative a first-time reader may want and the README deliberately omits. Nothing here is
authoritative — the ledger is; where this file and an entry disagree, the entry wins.

## The two program lines

**The sealed pre-fit screen (closed).** The original question: can a cheap, weights-only
screen predict what a fitted linear KV mapper will achieve, before fitting it? The discipline
was built for that question — sealed predictions written before any fit, a decision rule
committed before any weight was read. E0 ran on a vocabulary proxy across the Qwen3 ladder and
returned SAME under the frozen rule (entry 0004). One caveat deserves a first-time reader's
attention: nominally six ordered pairs, E0 is effectively n = 1 in every dimension that
matters — one model family, one training recipe, one proxy — and **all three checkpoints tie
their embedding and unembedding matrices**, which makes the vocabulary proxy structurally most
faithful at exactly the layers where the per-layer gap was large and least faithful in the
middle, where SAME was won. Entry 0003 named this escape before any data ("depth-dependent
nulls are the proxy's"), so the verdict is scoped to this operationalization and was never
generalized; the depth structure is recorded with both readings — real end-of-network
geometry vs proxy artifact — explicitly open (0006). The line E1–E6 was then closed on
opportunity-cost grounds (0006), a decision distinct from the verdict: the mechanism lane of
this niche is crowded with top-track work, the measurement lane was open. H-S1/H-S3/H-S4
carry `SHELVED` — no experiment decided them, and none is scheduled; reopening is one numbered
entry away, and E9's real-stream KV comparisons on the same pair may shed side-channel light
on which depth reading was right.

**The trace-replay measurement program (live).** The motivating claim of the cross-model
KV-transfer literature is that agentic serving crosses model boundaries mid-trajectory, so
caches die at switches and transfer would recover the re-prefill. Rather than assume it, the
program measured it: three public corpora (tau-bench, tau2-bench, SWE-bench), pre-registered
thresholds (0006/0007), a six-class invalidation taxonomy with a measurability rule per class
(0014), and pinned provider pricing. The verdicts are in the README's findings table; the
short version is that the premise did not survive contact with its own evidence, and the
paper's contribution became the measurement itself: switching exists only as a designed
critic/selector stage and is immaterial in recoverable prefill; compaction is unwitnessable in
final transcripts and absent where witnessable; and every trace-only cost figure anyone
publishes is a lower bound, because provider-reported usage reveals a fixed hidden prefix the
traces never record (0012).

**The transfer legs (E8 ran, E9 gated).** With the workload premise decided, the remaining
question is what transfer could deliver where the one observed handoff pattern exists. E8
evaluated the upstream's fitted mapper on agent-trace text with no refit — content shift
alone broke the registered retention band on the value pathway (0020). E9 is registered
(0019) to prefill the real handoffs on both models and measure how much of a content-matched
token's KV survives the re-render — the achievable ceiling under the observed handoff, against
the recorded upper bound.

## The correction chapter, briefly

Entries 0013 and 0015 carried figures produced by an instrument that misread half of one trace
family (a nested prompt shape) and mis-defined "paid" as the trajectory prefix rather than the
receiver's own request prefill. The defect was found by an independent measurement of the same
objects (E9's token counts could not be reconciled with the recorded slices), fixed with
pinning tests, registered as entry 0017 (figures `[SUPERSEDED]`, both verdicts re-derived and
standing — by a wider margin), and replaced by recomputed figures in 0018. The loop is drawn
in the README's "When the instrument is wrong" section; 0017 is that loop executed for real.
The lesson now encoded in the tooling: a summarizer that shares the driver's adapter proves
the arithmetic, not the reading — independence proves the reading.

## Vocabulary

Status tags on entries: `[VALIDATED]` ran and survived refutation · `[BASELINE]` ran, numbers
in the ledger · `[STRETCH]` designed, not run · `[FUTURE]` not designed · `[SUPERSEDED]`.

Hypothesis verdicts: `unresolved` (live, undecided) · `HELD` · `NOT CONFIRMED` (the rule as
written returned a negative) · `WITHDRAWN` (a claim retracted) · `SUPERSEDED` (replaced) ·
`SHELVED` (no experiment ran; none scheduled) · `UNESTIMABLE` (the experiment ran and its
estimand has no support in the corpus).

Recurring phrases with exact meanings: **NOT MEASURABLE** — the trace cannot evidence the
event class; excluded from both numerator and denominator, never a zero. **UPPER BOUND** — a
ceiling that is not an achievable value (re-rendering changes tokens and positions).
**LOWER BOUND** — visible-messages-only accounting; the provider billed more (the hidden
prefix). **Lane A / Lane B** — measured switch points vs a counterfactual cascade policy; Lane
B never resolves any hypothesis.
