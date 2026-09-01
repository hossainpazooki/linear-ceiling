# Measurement-lane evidence — basis for ledger entries 0006/0007

The re-scope decision (entry 0006) cited "session records of 2026-08-31/09-01." This file
commits that evidence: the delta table behind "all three registered claims remain unclaimed,"
the trace-metadata probe behind the two-lane switch-point design, and the venue facts. Every
row carries its source and retrieval date, per entry 0005's provenance rule.

## The three registered claims (entry 0005, promoted by 0006)

1. Invalidation taxonomy of long-horizon agent traces, with event frequencies.
2. Transfer headroom at model-switch points, in dollars per trajectory, at published pricing.
3. Compaction break-even distribution.

## Four-paper delta table (full texts read 2026-09-01, via arXiv HTML)

| paper | who | what it does | what it does NOT do (the deltas) |
|---|---|---|---|
| Don't Break the Cache (arXiv 2601.06007, v2 2026-01-31) | PricewaterhouseCoopers US, 7 authors; no venue in Comments | Prompt-caching strategies on DeepResearch Bench, 500 sessions, 4 models / 3 providers; 41-80% cost savings, 13-31% TTFT | No invalidation taxonomy or event frequencies (its section 5.1 names cache breakers conceptually only); no model switching or cross-model reuse; no compaction break-even (section 5.2 names the tradeoff, does not quantify it) |
| Agentic AI Workload Characteristics (arXiv 2605.26297, v1 2026-05-25) | UIUC + Gimlet Labs + Intel; no venue field | Traces ReAct agents on ADE-Bench, DABStep, GAIA, SWE-bench Pro, Terminal-Bench 2.0 (Gemma/Qwen, vLLM + OpenTelemetry); 84.6-99.5% cache-hit ratios, decode-dominated | Explicitly measures the IDEAL scenario ("independent of whether it thrashes") -- no invalidation characterization; no model switching; no dollar economics |
| Keeping the Cache Warm Pays (arXiv 2607.19214, v2 2026-07-24) | single author, no affiliation, 5 pp | Keepalive-vs-re-prefill break-even I_max ~ tau(w/r - 1); measured TTLs and price ratios across 4 providers (Anthropic r=0.10, w=1.25) | Synthetic idle-gap patterns only, no real traces; explicitly excludes compaction and model switching; harness not published |
| An Internet for the KV Cache (arXiv 2608.01526) | University of Chicago (Ray, Feamster, Jiang) | Position paper; CacheCost-vs-PrefillCost formalization with illustrative worked examples | Not a measurement study; same-model cache movement only; no agent traces, no switch points, no compaction |

Adjacent context (from the 2026-08-31 caliber research; conference-controlled sources):
CacheBlend = EuroSys '25 best paper; Prompt Cache = MLSys 2024; KVComm (2510.12872) = NeurIPS
2025 main track; Cache-to-Cache (2510.03215) = ICLR 2026 poster (the learned-projector slot);
the source paper 2608.03893 = 9 authors, all NVIDIA, arXiv-only (~4 weeks old at check).
Every peer-reviewed acceptance except Cache-to-Cache is same-model/intra-model work. The
mechanism papers assert the switch-point premise in their motivation sections; none measures
it. That unmeasured premise is claim 2.

## Trace-metadata probe (2026-09-01) — basis for the two-lane design in entry 0006

- SWE-bench experiments repo (github.com/SWE-bench/experiments): trajectories required of
  leaderboard submissions since July 2024; the serving model is identified at RUN level
  (metadata.yaml), not per step; submissions may be multi-rollout (best@k) but are not
  mid-trajectory model switches.
- tau-bench (github.com/sierra-research/tau-bench): ships `./historical_trajectories`
  (airline, retail); model is a run-level harness flag (`--model`); no router.

Consequence: measured switch events (Lane A) are expected sparse to absent in public suites;
a Lane A zero is the premise finding. Lane B (counterfactual two-tier cascade) exists so
headroom can still be sized -- descriptive only, never verdict-bearing (entry 0007).

## Pricing pins (both retrieved 2026-09-01; corroboration: 2607.19214's measured r/w)

- Anthropic prompt-caching docs (platform.claude.com/docs/en/build-with-claude/prompt-caching):
  read 0.1x base input; write 1.25x (5-minute TTL) / 2.0x (1-hour TTL); minimum cacheable
  512-4096 tokens by model; invalidation hierarchy tools -> system -> messages.
- OpenAI prompt-caching guide (developers.openai.com/api/docs/guides/prompt-caching):
  GPT-5.6+ read 0.1x, write 1.25x, retention ~30 minutes after last use; minimum 1,024 tokens.

## Venue facts (checked 2026-08-31/09-01)

- LCFM @ NeurIPS 2026 (longcontextfm.github.io): deadline 2026-09-10 AoE; 4-page short /
  8-page long; double-blind; NON-ARCHIVAL; arXiv preprinting and concurrent submission
  explicitly permitted; decisions 2026-09-29. The 2026 CFP contains no cache/serving/inference
  keywords (regex over the raw page HTML) -- framing must be agentic long-context measurement.
- ICLR 2027: abstracts 2026-09-18, papers 2026-09-25 (iclr.cc) -- collides with the LCFM
  sprint; not the archival target.
- MLSys 2027 (mlsys.org): submissions open 2026-10-10, due 2026-10-30 12:00 PM PDT; author
  notification 2027-02-28; Bellevue, WA. The anchor venue (entry 0006).
- AAAI-27 (aaai.org): Montreal, 2027-02-16..23; workshop list announced ~2026-09-25;
  common workshop paper deadline 2026-11-20 -- candidate second feedback stop, terms to be
  checked per workshop once the list exists.
