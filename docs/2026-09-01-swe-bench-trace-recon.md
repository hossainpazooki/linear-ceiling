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
`.traj` and the step/action shape each need their own. Estimated **~3 adapter families** for
the structured set. The per-agent coverage floor (>= 3 distinct agents per suite) is met
comfortably.

## Two structural findings

**1. No format carries a per-step `model` field.** None of the five sampled schemas records
which model served each step. Lane A (entry 0006) is therefore **unmeasurable in SWE-bench
exactly as in tau-bench** — recorded as NOT MEASURABLE, never as zero switches. This matters
beyond bookkeeping: the premise finding is not a tau-bench artifact. Across both major public
agent-trace corpora, the mid-trajectory model switching that the cross-model transfer
literature motivates itself with **cannot be evidenced either way from the public record**.
That is a stronger and more defensible claim than any single suite could support.

**2. No timestamps in any sampled format.** Entry 0007's two-bound rule for H-E7b (compute
under cache-always-warm and cache-always-cold, require the threshold under both) is therefore
universal rather than a tau-bench workaround, and idle-gap expiry is never modelable from
public traces. The rule was registered before this was known; it holds.

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
