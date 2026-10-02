# Restoring an E8 mirror splits across two trees: the agent token file under this repo, the generic dumps and mapper under the upstream

ts: 2026-10-02T03:35:15Z
commit: 470133e
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `summarize_e8` resolves the agent token file as `REPO_ROOT / report["tokens"]["path"]` (`summarize_e8.py:64`, path
`data/e8f/agent_n50_len1024_seed8.npy`) but the generic dumps as `cfg.upstream_path / cfg.generic_dumps` (`:69`,
`data/kv/llama3.2-3b-to-llama3.1-8b` under `../kv-transfer-replication`), and `summarize_e9`'s calibration reads the mapper
and `r2.json` from the upstream's `mappers/<pair>/` and `results/mapper/<pair>/`. A backup dataset flattens both trees into one
root, so a restore must split it: `data/e8f/`, `results/e8f/`, `results/e9f/`, `results/mapper/`, `results/probe/`, `mappers/`
into this repo and `data/kv/<pair>/`, `data/e8f/`, `data/tokens/`, `mappers/<pair>/`, `results/mapper/<pair>/` into the upstream.
Placing the token file only under the upstream refused with "agent token file missing or changed since the run". The upstream
does not gitignore `results/mapper/`, so the restored `r2.json` directory shows there as untracked.
basis: at 470133e, 2026-10-02T03:35:15Z, `grep -n` printed `summarize_e8.py:64: tp = (Path(REPO_ROOT) / tok.get("path", …` and
  `:69: dumps = {"generic": {w: cfg.upstream_path / cfg.generic_dumps / w …`; `config/e8f.toml` lines 33 and 67 read
  `tokens_dir = "data/e8f"` and `generic_dumps = "data/kv/llama3.2-3b-to-llama3.1-8b"   # relative to upstream`; `ls data/e8f`
  printed the manifest and the `.npy`. The refusal is in the session's run log (18:06Z, 2026-10-01).
re-verify: grep -n "Path(REPO_ROOT) / tok.get\|cfg.upstream_path / cfg.generic_dumps" src/linear_ceiling/summarize_e8.py   # expect lines 64 and 69: two roots
