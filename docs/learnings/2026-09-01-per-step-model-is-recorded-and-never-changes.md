# Some SWE-bench formats DO record a per-step model — and across 125 trajectories it never changes

kills: 2026-09-01-swe-bench-trajectories-are-in-s3.md (its per-step-model and timestamp clauses only; its S3-location and per-format census clauses stand)
ts: 2026-09-01T06:16:42Z
commit: e772390
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: The superseded entry claimed, from a 5-file sample, that no SWE-bench format records a
per-step serving model or timestamps, concluding Lane A is unmeasurable there. Probing all 68
structured submissions refutes both clauses: **9 carry a model-ish key and 5 carry a
timestamp-ish key.** At least three record the model PER STEP, not merely in run config —
`$.metrics.token_usages[i].model` and `$.metrics.response_latencies[i].model` (OpenHands-style,
zai), `$.messages[i].extra.response.model` (livesweagent), `$.nodes[i].completions.*.model`
(moatless) — and the OpenHands-style format also carries per-step `$.history[i].timestamp` and
per-response token usage. Lane A is therefore MEASURABLE on those submissions. Probing 25
trajectories from each of 5 such submissions (125 total, 5 distinct models across 4 vendors),
**0 contain more than one distinct model**. This strengthens rather than weakens the premise
finding: it converts "the public record cannot evidence mid-trajectory model switching"
(absence of evidence) into "where the serving model IS recorded per step, it never changes"
(evidence of absence). The general lesson: a claim of the form "no format records X", drawn
from a handful of samples, is a population claim and needs a population probe — the correction
here came from widening 5 samples to 68.
basis: census over 68 structured submissions returned `submissions whose trajectory JSON
  contains a timestamp-ish key: 5` and `... a model-ish key: 9`; per-step paths confirmed by
  walking each JSON. Constancy probe output: `TOTAL: 125 trajectories with per-step model
  metadata; 0 contain more than one distinct model`, with per-submission lines
  `20250611_moatless_claude-4-sonnet-20250514: 25 trajectories, 0 with >1 distinct model`,
  `20250728_zai_glm4-5: 25 ... 0`, `20250930_zai_glm4-6: 25 ... 0`,
  `20251120_livesweagent_gemini-3-pro-preview: 25 ... 0`,
  `20251215_livesweagent_claude-opus-4-5: 25 ... 0`. This is RECON that sizes the finding; the
  H-E7a verdict must still come through the registered adapter and fail-closed summarizer, not
  through this probe.
re-verify: curl -sS "https://swe-bench-submissions.s3.amazonaws.com/verified/20250728_zai_glm4-5/trajs/astropy__astropy-12907.json" | python -c "import sys,json; d=json.load(sys.stdin); print(sorted({u['model'] for u in d['metrics']['token_usages']}))"
