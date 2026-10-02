# The E8 driver and summarizer hash the config as raw bytes, so a CRLF checkout refuses an unchanged committed config; E9 normalizes

ts: 2026-10-02T03:35:13Z
commit: 470133e
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `e8.py:220` records `config_sha256 = sha256_file_bytes(cfg.config_path)` and `summarize_e8.py:54` compares the same raw
hash, while `e9.py:385` / `:435` use `sha256_text_file` (line-ending normalized). The Llama E8 run on Linux recorded
`cba5e38c8864`; on this `core.autocrlf=true` Windows checkout the raw hash of the identical committed file is `bf7f4e62fff4`,
so `summarize_e8 --config config/e8f.toml` refused with "config/e8.toml changed since the run (config_sha256 mismatch)" (the
message also names the wrong file). The text hash equals the pin. Worked around on 2026-10-01 by writing the stored blob into
the worktree for the run (`git show HEAD:config/e8f.toml > config/e8f.toml`) and restoring the checkout form after; the run
then PASSED and reproduced 0040's table. The fix is to hash the config the way E9 does, in both the driver and the summarizer,
with a test; until then E8 re-summaries on Windows need the blob trick (Ritvik's clean clone used `core.autocrlf=false`).
basis: at 470133e, 2026-10-02T03:35:13Z, `grep -n "sha256_file_bytes(cfg.config_path)"` printed `e8.py:220` and
  `summarize_e8.py:54`; `grep -n "sha256_text_file\|config_sha256" src/linear_ceiling/e9.py` printed lines 385 and 435 using
  `sha256_text_file`; a read of `results/e8f/report.json` against both hashes printed `report pin cba5e38c8864 | raw
  bf7f4e62fff4 | text cba5e38c8864`. The refusal and the later `e8 exit=0` are in the session's run logs (18:03Z, 18:19Z).
re-verify: grep -n "sha256_file_bytes(cfg.config_path)" src/linear_ceiling/e8.py src/linear_ceiling/summarize_e8.py   # expect e8.py:220 and summarize_e8.py:54 until the fix lands
