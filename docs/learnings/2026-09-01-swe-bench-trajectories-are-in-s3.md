# SWE-bench trajectories live in a public S3 bucket, and no format records a per-step model

ts: 2026-09-01T06:05:06Z
commit: 62282e9
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: SWE-bench leaderboard trajectories are NOT in the `SWE-bench/experiments` repo — a scan
of all 4,336 paths finds zero `trajs` paths; submissions hold only `results/`, `metadata.yaml`
and logos. Each `metadata.yaml` points at `s3://swe-bench-submissions/verified/<sub>/trajs/`,
a bucket that is publicly and anonymously listable over HTTPS. Census of the verified split:
119 of 181 submissions (66%) have trajectories; extensions are .json 50, .log 22, .txt 18,
.traj 13, .jsonl 5, .md 5, other 6 — roughly 68 structured against 47 human-readable prose
(compliant with the leaderboard's "human-readable" requirement, but unusable for per-message
token accounting). Five sampled files had five distinct schemas, clustering into ~3 adapter
families. Two structural findings matter more than the counts: **no sampled format records a
per-step serving model**, so measured mid-trajectory model switching is unmeasurable in
SWE-bench exactly as in tau-bench; and **no sampled format carries timestamps**, so idle-gap
cache expiry is never modelable from public traces. The first means the "agents switch models
mid-trajectory" premise that the cross-model KV-transfer literature motivates itself with
cannot be evidenced either way from the public record — a corpus-independent claim, not a
one-suite artifact.
basis: S3 listing returns
  `<Key>verified/20240728_sweagent_gpt4o/trajs/astropy__astropy-12907.traj</Key>` anonymously,
  while `gh api repos/SWE-bench/experiments/git/trees/main?recursive=1 --jq '[.tree[].path |
  select(contains("trajs"))] | length'` returns `0`. Full census and schema table:
  `docs/2026-09-01-swe-bench-trace-recon.md`.
re-verify: curl -sS "https://swe-bench-submissions.s3.amazonaws.com/?list-type=2&prefix=verified/20240728_sweagent_gpt4o/trajs/&max-keys=1" | grep -c "<Key>"
