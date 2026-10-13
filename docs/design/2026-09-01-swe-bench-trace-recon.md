# SWE-bench trajectory recon — availability, formats, and two structural findings

Census of the SWE-bench `verified` split, run 2026-09-01, to decide whether SWE-bench can be
the suite that clears entry 0007's per-agent coverage floor. Method: full repo tree via the
GitHub API (one call, 4,336 paths), then one anonymous S3 list per submission for all 181.

## Where trajectories actually live

**Not in `SWE-bench/experiments`.** That repo holds `results/`, `metadata.yaml`, `README.md`
and logos per submission; a scan of all 4,336 paths found **zero** `trajs` paths. Each
`metadata.yaml` instead carries a uniform pointer:

```yaml
assets:
  logs:  s3://swe-bench-submissions/verified/<submission>/logs
  trajs: s3://swe-bench-submissions/verified/<submission>/trajs
```

The bucket is **public and anonymously listable** over HTTPS
(`https://swe-bench-submissions.s3.amazonaws.com/?list-type=2&prefix=verified/<sub>/trajs/`),
one object per instance, ~110-640 KB each. No credentials, no per-submitter scavenger hunt.
This retires the acquisition risk that the 2026-09-01 handoff flagged as the dominant unknown.

## Census — all 181 verified submissions

**119 of 181 (66%) have trajectories in S3**; 62 have none.

| extension | submissions | parseable for message-level token accounting? |
|---|---|---|
| `.json` | 50 | yes (multiple internal schemas) |
| `.log` | 22 | no — human-readable prose |
| `.txt` | 18 | no — human-readable prose |
| `.traj` | 13 | yes (SWE-agent) |
| `.jsonl` | 5 | yes |
| `.md` | 5 | no — human-readable prose |
| `(no ext)`, `.yaml`, `.logs`, `.diff` | 6 | mixed / unknown |

So roughly **68 structured against 47 unstructured**. The leaderboard requires only
"human-readable" trajectories, so prose logs are compliant; they are simply unusable for
per-message token accounting and must be excluded with the exclusion stated, never silently.

Two of the 68 still fail to parse after byte-safe decoding; six earlier "parse failures" were
an artifact of the probe decoding S3 bytes as cp1252 on Windows, not of the data.

## Schema families (five files sampled, one per submission)

Five files, five distinct schemas:

| submission | shape | per-item keys |
|---|---|---|
| `20240728_sweagent_gpt4o` (`.traj`) | dict: `environment/trajectory/history/info` | `action, observation, response, state, thought` |
| `20241125_marscode-agent-dev` | root list | `agent, content, role` |
| `20250603_Refact_Agent_claude-4-sonnet` | root list | `role, content, finish_reason, tool_call_id` |
| `20250901_entroPO_R2E_QwenCoder30BA3B` | root list | `role, content` |
| `20251110_frogboss-32b` | root list | `step_idx, thought, action, observation, done, info, token_usage_prompt, token_usage_completion, token_usage_total` |

Three of the five are role/content variants that one tolerant adapter covers; SWE-agent's
`.traj` and the step/action shape each need their own. The per-agent coverage floor (>= 3
distinct agents per suite) is met comfortably.

Shape census over all 68 structured submissions (item keys of the first message list found):
the role/content family dominates — `list:content,role` 18, `dict[messages]:content,role` 5,
`list:agent,content,role` 3, `list:content,role,template` 1 — roughly **27 submissions reachable
by one tolerant adapter**. SWE-agent's `dict[trajectory]:action,observation,response,state,
thought` and its variants account for ~10; the remainder are long-tail one-offs.

## Two structural findings — CORRECTED after a population probe

> An earlier revision of this section claimed, from the five sampled files above, that **no**
> format records a per-step model or timestamps. Probing all 68 structured submissions refuted
> both claims. The corrected findings are below; the superseded version is recorded in
> `docs/learnings/` (superseding entry: `2026-09-01-per-step-model-is-recorded-and-never-changes.md`).
> The lesson is kept deliberately: a "no format does X" claim is a population claim and a
> five-file sample cannot support it.

**1. A minority of formats DO record a per-step model — and the model never changes.**
Of 66 structured submissions that parse, **9 carry a model-ish key and 5 a timestamp-ish key**.
At least three record the model *per step* rather than only in run config:

| submission family | per-step model path | also carries |
|---|---|---|
| OpenHands-style (`zai_glm4-5`, `zai_glm4-6`) | `$.metrics.token_usages[i].model`, `$.metrics.response_latencies[i].model` | `$.history[i].timestamp`, per-response token usage |
| livesweagent (`gemini-3-pro-preview`, `claude-opus-4-5`) | `$.messages[i].extra.response.model` | — |
| moatless | `$.nodes[i].completions.*.model` | — |

Lane A is therefore **measurable** on those submissions. Probing 25 trajectories from each of
five such submissions — **125 trajectories, 5 distinct models across 3 vendors — 0 contain
more than one distinct model.**

**A fourth family exists, it switches, and the first probe could not see it.** That probe fired
only on a dict key literally named `model`; the LangChain-style family records serving identity
under `model_id` / `model_name`, so it was never probed — the detector was strictly narrower
than the set the conclusion quantified over. Re-probed with `model|model_id|model_name`:

| submission | trajectories probed | with >1 serving model | models |
|---|---|---|---|
| `20241016_composio_swekit` | 25 | **25** | `anthropic.claude-3-5-sonnet-20240620-v1:0` + `o1-mini-2024-09-12` |
| `20241025_composio_swekit` | 25 | **25** | `anthropic.claude-3-5-sonnet-20241022-v2:0` + `o1-mini-2024-09-12` |

Claude runs the solve threads; o1-mini runs per-run summarization and patch selection. So
**"the per-step-recorded model never changes" is false**, and so is the tautology worry that a
benchmark submission is single-model by construction — submissions can and do switch.

**What the handoff actually looks like, checked rather than assumed.** The o1-mini stage opens
`The following is the run of the agent after it tried to fix the issue...` and contains the
Claude conversation re-rendered as LangChain labels (`HumanMessage` 5, `AIMessage` 11,
`ToolMessage` 7), sharing 118 of 119 long tokens with the Claude stage — but a verbatim-prefix
check returns **0/3**. It is a semantically complete cross-model context handoff that is **not
byte-identical**: the second model re-consumes the first model's context as a re-serialized
prompt, and pays full prefill for it. That is precisely the operation cross-model KV transfer
proposes to replace, so this family is the one public instance of the motivating use case —
and it currently implements it the expensive way. Do not describe it as "verbatim".

**The surviving claim, stated narrowly.** Mid-trajectory model switching does occur in public
benchmark traces, as a designed critic/selector pipeline stage. What remains unevidenced is
**production-style cost/quality routing or mid-conversation switching** — the premise the
transfer literature actually motivates itself with. Most multi-model-by-design submissions
(navie-2, SWE-Fixer, wandb crosscheck, Skywork Bo8, Co-PatcheR) record no serving-model
identity at all and stay NOT MEASURABLE, never counted as zero.

**Census caveat.** The "9 model-ish / 5 timestamp-ish" counts above were produced with the same
narrow detector and must be re-derived over at least `model|model_id|model_name` before being
quoted; an independent sweep suggested 13-18 and 12 respectively. Treat 9/5 as unverified.

**2. Timestamps exist in a minority, so the two-bound rule is a floor, not a ceiling.** Entry
0007's two-bound H-E7b rule (require the threshold under both cache-always-warm and
cache-always-cold) was registered for traces without timestamps and still governs those. But
the OpenHands-style format carries per-step `timestamp`, so for that subset the **realized**
idle-gap timeline is computable and strictly better than the bounds. Entry 0007 already
provides for this ("idle-gap expiry IS modeled, from trace timestamps, wherever the trace
carries them"), so no amendment is needed — but the subset must be reported separately from
the two-bound subset, never pooled.

**Re-prioritization this forces.** The OpenHands-style format is now the highest-value adapter
target, ahead of the larger role/content family: it is the only one that simultaneously makes
Lane A measurable, supplies per-response token usage as tokenizer ground truth, and carries
timestamps for realized expiry. The role/content family remains necessary for coverage breadth.

## One opportunity

`20251110_frogboss-32b` reports real `token_usage_prompt`, `token_usage_completion` and
`token_usage_total` per step. That is **ground truth for token counts**, independent of both
`o200k_base` and the calibrated divisors of entry 0009 — a natural experiment for validating
the estimator against reported usage rather than only against another tokenizer. Worth taking
before the divisors carry any published number, since it can retire the tokenizer caveat
instead of carrying it into the paper.

## Consequences for the plan

- SWE-bench acquisition is cheap; adapters are the work (~3 families).
- Exclusions to state in any output: 62 submissions with no trajectories, 47 with prose-only
  trajectories.
- Divisors calibrated on tau-bench do **not** transfer (entry 0009): SWE-bench needs its own
  calibration, and the frogboss usage fields give it a second, better check.
