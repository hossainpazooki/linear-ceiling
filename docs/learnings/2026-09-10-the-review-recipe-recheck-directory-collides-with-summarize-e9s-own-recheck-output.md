# The independent review's re-run recipe names its cold directory `$RECHECK`, and `summarize_e9` writes exactly those filenames into `results/e9/recheck/`: feeding them in makes the evidence path grade itself, which fails loudly on Windows only because of float jitter

kills: (nothing)
ts: 2026-09-10T13:52:43Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: e9l-aws-run (01VDywUv8N146LzzLgRDTihm)
status: verified
fact: The independent re-verification record (`docs/reviews/2026-09-08-e9-independent-reverification.md`, merged at
`bb85a28`) shows the probe invoked with `--cold-score "$RECHECK/$HANDOFF.json"`, `--cold-tokens
"$RECHECK/$HANDOFF.tokens.npz"` and `--out "$RECHECK/$HANDOFF.comparison.json"`. Separately, `summarize_e9` writes
`results/e9/recheck/<stem>.json` and `<stem>.tokens.npz` for every kept handoff, including both handoffs the review
sampled, by running upstream `score_positions.py` from linear-ceiling's own driver with linear-ceiling's own alignment
pairs. Those files have the name and shape of a cold rescore and are not independent of the evidence path the review
exists to check. Fed to the probe on this Windows machine they fail with exit 1: three of the five score fields and 3 of
6 arrays differ, which is entry 0028's thread-order jitter. That loud failure is platform luck. Entry 0028 records the
same-model arrays reproducing bit-for-bit on a matching Linux platform, and the review's own Linux run matched every
array exactly, so the same mistake made on Linux would likely pass silently; that case was not run here. The recipe's
`--out` would also write a non-summarizer file into `results/e9/`, which the repo never rewrites. A cold directory must
sit outside `results/` and be produced by a recorded run of the pinned upstream, never by `summarize_e9`.
basis: `sed -n 395,407p src/linear_ceiling/summarize_e9.py` at HEAD `50bc439` -> `rdir = cfg.results_dir / "recheck"`,
  `out, out_tok = rdir / f"{_stem(hid)}.json", rdir / f"{_stem(hid)}.tokens.npz"`, and
  `run_upstream(cfg, ["scripts/score_positions.py", … "--pairs", str((cfg.results_dir / "align" / f"{_stem(hid)}.npz").resolve()), …`;
  `ls results/e9/recheck/ | wc -l` -> `17`, listing both
  `20241025_composio_swekit__django__django-11066_traj_sw36.{json,tokens.npz}` and
  `20241016_composio_swekit__astropy__astropy-14182_traj_sw68.{json,tokens.npz}`; the review record fetched from remote
  main with `gh api` (sha256 `1a8ac32108aa7287…`), lines 49–53 -> the `$RECHECK` recipe quoted above. Probe run at
  2026-09-10T13:52:43Z, archive `results/e9/scores/…traj_sw36.json` and `results/e9/tokens/…traj_sw36.tokens.npz`
  against `results/e9/recheck/…traj_sw36.json` and `.tokens.npz` -> `exit=1`,
  `passed=False score_fields_all_exact=False arrays_exact=3/6`, fields
  `{'cross_K_r2_layer_mean': False, 'cross_V_r2_layer_mean': False, 'n_pairs': True, 'same_K_r2_layer_mean': False, 'same_V_r2_layer_mean': True}`.
re-verify: grep -n 'rdir = cfg.results_dir / "recheck"' src/linear_ceiling/summarize_e9.py   # two lines (kept handoffs, and recheck/bridge for the bridge control): the summarizer owns results/<exp>/recheck/, so no cold rescore may be read from anywhere under it
