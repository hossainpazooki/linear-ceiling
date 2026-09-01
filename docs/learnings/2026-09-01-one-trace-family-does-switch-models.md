# One public trace family DOES switch models mid-trajectory — and hands the transcript across, re-rendered

kills: 2026-09-01-per-step-model-is-recorded-and-never-changes.md (its "never changes" generalization and its "4 vendors" count; its refutation of the earlier no-per-step-model claim stands)
ts: 2026-09-01T06:26:10Z
commit: e772390
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: The superseded entry generalized from 125 trajectories to "where the serving model is
recorded per step, it never changes." An adversarial re-probe with a broader detector refutes
it. The probe behind that claim only fired on a dict key literally named `model`; the
LangChain-style family records serving identity under `model_id` and `model_name`, so it was
never probed at all — the detector was strictly narrower than the set the conclusion quantified
over. In `20241016_composio_swekit` and `20241025_composio_swekit`, **50 of 50 probed
trajectories contain two serving models from two vendors**: Bedrock
`anthropic.claude-3-5-sonnet-*` runs the solve threads, OpenAI `o1-mini-2024-09-12` runs
per-run summarization and patch selection. So mid-trajectory model switching IS present in
public benchmark traces, and the tautology worry ("a submission is one system by construction")
is itself refuted — submissions can and do switch. What survives is narrower and still useful:
no public trace evidences **production-style cost/quality routing or mid-conversation
switching**; composio's switch is a designed critic/selector pipeline stage. Also corrected:
the five single-model submissions span **3 vendors, not 4**, and the "9 model-ish / 5
timestamp-ish" census was produced with that same narrow detector and must be re-derived over
at least `model|model_id|model_name` before it is quoted anywhere.
basis: independent re-probe (not the subagent's numbers) —
  `20241016_composio_swekit: 25 trajectories, 25 with >1 distinct model` /
  `25 x ('anthropic.claude-3-5-sonnet-20240620-v1:0', 'o1-mini-2024-09-12')`;
  `20241025_composio_swekit: 25 trajectories, 25 with >1 distinct model` /
  `25 x ('anthropic.claude-3-5-sonnet-20241022-v2:0', 'o1-mini-2024-09-12')`;
  `INDEPENDENT TOTAL: 50 probed, 50 with more than one serving model`.
  Handoff shape, checked rather than assumed: the o1-mini stage opens `The following is the run
  of the agent after it tried to fix the issue...` and contains the Claude conversation
  re-rendered as LangChain labels (`HumanMessage` 5, `AIMessage` 11, `ToolMessage` 7), with
  118/119 long tokens shared with the Claude stage — but a verbatim-prefix check returned
  **0/3**. So it is a semantically complete handoff that is NOT byte-identical: the second
  model re-consumes the first model's context as a RE-SERIALIZED prompt and pays full prefill.
  Do not describe it as "verbatim"; that was an over-claim in the refuting report.
re-verify: curl -sS "https://swe-bench-submissions.s3.amazonaws.com/verified/20241016_composio_swekit/trajs/astropy__astropy-12907_traj.json" | python -c "import sys,json,re; d=json.load(sys.stdin); s=json.dumps(d); print(sorted(set(re.findall(r'\"model(?:_id|_name)?\":\s*\"([^\"]+)\"', s))))"
