# A moved upstream HEAD fails every E9 pin even when the pin is an ancestor, and the config offers no other path

ts: 2026-10-01T04:47:30Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `upstream_gate.check_upstream` passes only if the pin is an ancestor of HEAD AND `git diff --quiet <pin> HEAD --
scripts/dump_kv.py scripts/score_positions.py scripts/score_mapper.py kvt` is empty AND those paths are clean. The
upstream clone `../kv-transfer-replication` is now on `main` at 0d27c68 (PR #2 merged), which changed those paths
after every pin (063f402 for e9l/e9s, d5786df for e9, 06f8d55 for e9f), so `summarize_e9` refuses all four cells
with "the invoked tools are not the pinned bytes" while every pin is still an ancestor. `config.py` resolves
`upstream_path` as `repo_root / "../kv-transfer-replication"` with no environment override, and each config is
sha-pinned by its entry, so a worktree at the pin cannot be pointed at without a ledger amendment. The only sanctioned
move is `git checkout --detach <pin>` in the clone (config/e9f.toml line 42), returning it to `main` afterwards; the
clone's editable `kvt` then imports the pinned bytes too. Done this way today for the three Qwen cells (04:08–04:36Z,
operator-authorized), clone returned to `main`.
basis: at 0a51275, 2026-10-01T04:47:30Z: `git -C ../kv-transfer-replication rev-parse --abbrev-ref HEAD` printed
  `main`, `--short HEAD` printed `0d27c68`, `merge-base --is-ancestor 063f4023fdde HEAD` succeeded, and `git diff
  --quiet 063f4023fdde HEAD -- <the four paths>` exited 1. `grep -c "environ\|getenv" src/linear_ceiling/config.py`
  printed 0. The refusals were captured at 03:40Z with the clone at 9ca6258: "E9 summary REFUSED: upstream paths (…)
  changed between the pin 063f4023fdde and HEAD; the invoked tools are not the pinned bytes".
re-verify: git -C ../kv-transfer-replication diff --quiet 063f4023fdde HEAD -- scripts/dump_kv.py scripts/score_positions.py scripts/score_mapper.py kvt; echo "exit=$?"   # expect exit=1 while the clone is on main
