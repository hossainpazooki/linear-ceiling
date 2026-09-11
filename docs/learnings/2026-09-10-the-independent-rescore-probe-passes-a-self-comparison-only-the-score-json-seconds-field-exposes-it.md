# The independent E9 rescore probe passes when the archive is compared with itself; only the score JSON's hash exposes that, because numpy writes byte-identical npz files and the JSON records the run's wall-clock seconds

kills: (nothing)
ts: 2026-09-10T13:53:39Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: e9l-aws-run (01VDywUv8N146LzzLgRDTihm)
status: verified
fact: `docs/probes/2026-09-08-e9-independent-rescore-compare.py` (merged at `bb85a28`) decides by exact equality of five
score fields and every per-token array. That makes it sensitive in the right direction: one element of one array moved
by a single ULP fails with exit 1 and names the array. It also means it cannot refuse a self-comparison: pointing both
the archive and the cold arguments at the same archived files passes with exit 0 and 6 of 6 arrays exact. The report
records the sha256 of all four inputs, and that is where a self-comparison has to be caught — but only one of those
hashes carries information. numpy 2.5.2 writes byte-identical `.npz` files for identical arrays (two saves 2.2 s apart
hashed the same), so equal token hashes are also what a genuine exact reproduction produces. The score JSON differs:
upstream `score_positions.py` records the run's wall-clock `seconds` to full float precision and the absolute
`mapper.path` of the machine it ran on, so a separate run cannot reproduce its bytes. Equal archive and cold score-JSON
hashes therefore mean the same file was fed twice, whatever `passed` says; equal token hashes mean nothing either way.
basis: the probe was fetched from remote main with
  `gh api "repos/hossainpazooki/linear-ceiling/contents/docs/probes/2026-09-08-e9-independent-rescore-compare.py?ref=main"`
  (sha256 `7acfe948ff4820f5…`; not present in local HEAD `50bc439`, which predates the merge) and run on handoff
  `20241025_composio_swekit__django__django-11066_traj_sw36` from `results/e9/`. Archive vs itself -> `exit=0`,
  `passed=True arrays_exact=6/6 score_sha_equal=True tokens_sha_equal=True`. Archive vs a copy of its tokens with
  `cross_K` element 0 moved by `np.nextafter` -> `exit=1`, `passed=False arrays_exact=5/6`. Score JSON top-level keys ->
  `['cross', 'cross_K_r2_layer_mean', 'cross_V_r2_layer_mean', 'mapper', 'n_pairs', 'per_token', 'same',
  'same_K_r2_layer_mean', 'same_V_r2_layer_mean', 'seconds']`, with `seconds = 18.858345985412598` and
  `mapper = {'path': '/home/jupyter-rrhs-fe3a-xl/kv-transfer-replication/mappers/qwen3-0.6b-to-1.7b/k1…`. The same
  arrays passed to `np.savez` twice, 2.2 s apart -> `file sha equal: True (4d08f4efefa19aa4 vs 4d08f4efefa19aa4)`,
  numpy 2.5.2.
re-verify: .venv/Scripts/python.exe docs/probes/2026-09-08-e9-independent-rescore-compare.py --archive-score results/e9/scores/20241025_composio_swekit__django__django-11066_traj_sw36.json --cold-score results/e9/scores/20241025_composio_swekit__django__django-11066_traj_sw36.json --archive-tokens results/e9/tokens/20241025_composio_swekit__django__django-11066_traj_sw36.tokens.npz --cold-tokens results/e9/tokens/20241025_composio_swekit__django__django-11066_traj_sw36.tokens.npz   # prints "passed": true and exits 0 on a self-comparison; needs merge bb85a28 in the local tree
