# Learnings ledger

Pointers only — no evidence lives here. One non-obvious, re-verifiable fact per dated entry;
entries are immutable (a wrong one is superseded by a new entry carrying `kills:`, never
edited). Every entry carries a read-only `re-verify:` line, so a skeptical reader can execute
the claim rather than trust it.

| date | entry | one-line |
|---|---|---|
| 2026-09-01 | [per-agent-trace-schema-split](2026-09-01-per-agent-trace-schema-split.md) | tau-bench stores tool-call `arguments` as str for gpt-4o and dict for sonnet; a char counter counts dict KEYS, biasing one agent only (+1.5%) — asymmetric, so it corrupts cross-agent comparison while the aggregate looks fine. |
| 2026-09-01 | [prefix-repetition-reweights-tokenizer-bias](2026-09-01-prefix-repetition-reweights-tokenizer-bias.md) | chars/4 is differentially biased by content type (−27.8% tool output, +20.4% system); cost bills the prefix repeatedly so the system prompt is 50.4% of billed chars and the errors nearly cancel — aggregate agreement is coincidence, not safety. |
| 2026-09-01 | [swe-bench-trajectories-are-in-s3](2026-09-01-swe-bench-trajectories-are-in-s3.md) | SWE-bench trajectories are in a public S3 bucket, not the experiments repo (119/181 have them, ~68 structured). **Its per-step-model and timestamp clauses are superseded — see the next row.** |
| 2026-09-01 | [per-step-model-is-recorded-and-never-changes](2026-09-01-per-step-model-is-recorded-and-never-changes.md) | Widening 5 samples to 68 refutes "no format records a per-step model": ≥3 families record it per step, and 125 probed trajectories show one model each. **Its "never changes" generalization and vendor count are superseded — see the next row.** |
| 2026-09-01 | [one-trace-family-does-switch-models](2026-09-01-one-trace-family-does-switch-models.md) | A detector matching only the key `model` missed the LangChain family, which uses `model_id`/`model_name`: composio_swekit is **50/50 two vendors mid-trajectory** (Claude solves, o1-mini summarizes/selects), handing the transcript across **re-rendered, not verbatim** — so switching does occur; what survives is that no public trace shows production-style cost/quality routing. |
