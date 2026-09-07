# A registered config asserted an upstream artifact that the upstream's own ledger said was destroyed

kills: (nothing)
ts: 2026-09-07T04:52:38Z
commit: 6d20680b7b3aaa9a186de9b8d8d1090f2c9cb97f
session: lcfm-sprint-pickup-2 (73d64579-4856-4085-a6d8-19989f5bf384)
status: verified
fact: `config/e8c.toml` (committed `b37914d`), `docs/drafts/append_0033.py` and the LCFM outline all describe
the calibration-size entry as a refit "on the existing n = 420 calibration dumps" (the config comment dates them
2026-08-24). Only the SOURCE half exists: `data/kv/qwen3-0.6b-to-1.7b-n420/source` holds 28 `layer*.npz` plus
`meta.json` (12 GB). `target/` is an empty directory. The upstream's own learnings entry
`2026-08-25-buffered-writers-have-a-flat-loss-profile.md` records why: the target dump was killed at 358/420 and
`dump_kv` writes only after its loop, so zero bytes landed; it was never re-run. The 09-06 session registered
0033's shape and locked the "calibration-size" decision on the config comment, not on the directory. What would
have caught it without a pick-up is `append_0033.py`'s own `assert (p / "meta.json").exists()`, i.e. at
registration time, after the freeze plan had already been built on the premise. Rule: a premise about an
artifact ("existing", "pre-existing", "already dumped") is verified by listing the artifact at the time the
decision is locked, and the check is written into the brief's `re-verify:` line, not into a comment.
basis: `ls -la data/kv/qwen3-0.6b-to-1.7b-n420/target` -> `total 0` (dir mtime 2026-08-24 20:51); the upstream
  entry's own re-verify line, run 2026-09-07 in the upstream venv: `source layers=28 meta=True` /
  `target layers=0 meta=False` / `writes only after the loop: True`; `grep -n "pre-existing\|2026-08-24"
  docs/drafts/append_0033.py` -> lines 5 and 65; `config/e8c.toml` `[e8.calibration]` comment.
re-verify: cd ~/dev/kv-transfer-replication && .venv/Scripts/python.exe -c "from pathlib import Path; d=Path('data/kv/qwen3-0.6b-to-1.7b-n420'); [print(w, len(list((d/w).glob('layer*.npz'))), (d/w/'meta.json').exists()) for w in ('source','target')]"   # target 0 False until a re-dump lands
