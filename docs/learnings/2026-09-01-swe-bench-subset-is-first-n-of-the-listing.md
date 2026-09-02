# Every SWE-bench submission's local subset is the first N objects of its S3 listing

kills: (nothing)
ts: 2026-09-01T23:33:41Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling track-b (session_01RRk8euGRszMDP4z12wDdJz)
status: verified
fact: The 15 instances acquired per SWE-bench submission (30 per composio submission, 4 for
the nested autocoderover) were never a random draw. For all seven submissions the local
instance ids are exactly listing positions 0..N-1 of
`s3://swe-bench-submissions/verified/<sub>/trajs/`, and ListObjectsV2 returns keys in UTF-8
binary order, so the subset is the alphabetically first N instances of each submission
(astropy__astropy-* dominated). `config/e7-manifest.json` records this per submission as
`rule: first-N in listing order`, and from entry 0024 on the pooled SWE-bench taxonomy rows
carry the label SELECTED SUBSET. No bearing on Lane A: the 60 composio files are the first 30
of each of its two submissions.
basis: a scratch recon over the paginated anonymous listing (8,763 objects for the nested
submission) printed, per submission,
  `20240820_honeycomb: local 15 / s3 500 instances (500 objects); rule=first-N in listing order; listing positions [0, 1, ..., 14]`
  `20241016_composio_swekit: local 30 / s3 498 instances (498 objects); rule=first-N in listing order; ...`
  `20250122_autocoderover-v2.1-...: local 4 / s3 500 instances (8763 objects); rule=first-N in listing order; listing positions [0, 1, 2, 3]`
  and `shared across ALL submissions: 4`; `e7_manifest write` then reproduced the rule for all seven
  (`rule: first-N in listing order; positions 0..14` etc.).
re-verify: python -c "import json;m=json.load(open('config/e7-manifest.json'));print({k:(v['n_local'],v['s3_instances'],v['rule']) for k,v in m['swe_bench_selection'].items()})"
