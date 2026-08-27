## Gap map: agentic serving and cache economics

**Date:** 2026-08-26 · **Status:** motivation-layer analysis; feeds E7. Sources of the
concerns: co-author review. Claims below marked *intuition* are pre-registered
expectations, not results.

### The framing correction

Agentic serving is the workload where cross-model cache boundaries actually occur.
Multi-step runs re-send nearly identical context every step, so cache economics
dominates cost — and the two events that destroy the cache are this paper's subject:

- **Model switch mid-trajectory** (router escalation, cascade): invalidates the entire
  prefix cache at the boundary. This is the cross-model transfer setting, verbatim.
- **Compaction**: rewrites the token stream, so exact-match prefix caching invalidates
  by construction. Distinct from **compression** (quantization, eviction), which
  preserves tokens and stays cache-compatible. The literature does not consistently
  hold this distinction; this paper does: *compression is cache-compatible, compaction
  is cache-destroying.*

The compaction break-even, stated once: with cached input tokens priced ~an order of
magnitude below fresh prefill (verify current provider pricing before any number
ships), compaction pays only when future-step savings on the shortened context exceed
the one-time uncached re-prefill of the compacted history. That inequality, priced on
real trace statistics, is — as of the W1 lit sweep, to be re-verified there — unwritten.

### Where people are missing

| gap | who's nearby | what's actually missing |
|---|---|---|
| invalidation taxonomy for agentic runs | prefix-caching literature (append-only assumption) | no accounting of *why* caches die on real trajectories: compaction vs model-switch vs branch vs edit |
| compaction economics | text-level compression (LLMLingua line) and KV-level (gist/beacon line) | the break-even inequality above, priced on real traces — compaction treated as free context hygiene |
| cache-aware cross-model routing | same-model prefix-aware scheduling (vLLM line) | routers ignore cache state at the model boundary; transfer changes what a switch costs, and no router knows it |

*(All "who's nearby" attributions require primary-source verification in the W1 sweep
before appearing in the paper.)*

### Intuitions, stated as falsifiable claims

- *Intuition 1:* model-switch points on public agent traces are frequent enough that
  transfer headroom is material in dollars.
- *Intuition 2:* compaction events are common enough to estimate the break-even
  distribution, and it often goes negative — compaction is quietly uneconomic at
  current pricing for short remaining horizons.
- *Intuition 3:* both numbers are extractable by CPU replay of public trajectories
  (SWE-bench verified runs, terminal-bench, tau-bench) against a published-pricing cost
  model — no model forward passes required.

### What this does NOT change

The frozen retention metric (floor-normalized HellaSwag) stays: it measures the
transfer mechanism, not the workload. Building an agentic cache benchmark is a
different paper and is explicitly out of scope. Everything sealed stays sealed. The
specificity of E0–E6 is the defense, not the flaw; E7 is how the paper earns its
general motivation without the experiments sprawling.
