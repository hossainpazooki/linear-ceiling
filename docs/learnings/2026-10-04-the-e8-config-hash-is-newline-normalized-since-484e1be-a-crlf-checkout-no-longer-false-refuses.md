# The E8 config hash is newline-normalized since `484e1be`; a CRLF checkout no longer false-refuses an unchanged config

ts: 2026-10-04T09:24:17Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: The 2026-10-02 learning (`the-e8-driver-and-summarizer-hash-the-config-as-raw-bytes…`) recorded the bug and said a fix was owed.
Commit `484e1be` makes `e8.py` record `config_sha256` with `sha256_text_file` and `summarize_e8.py` compare with the same, exactly as
`e9.py` always did. Every recorded E8 digest stays valid because the boxes wrote LF files, for which the text digest equals the raw
one. `tests/test_summarize_e8.py::test_a_crlf_checkout_of_the_unchanged_config_is_not_drift` pins the pass; the existing
`test_refuses_config_drift` still refuses an edited file. The `git show HEAD:config/e8f.toml > config/e8f.toml` workaround is retired.
basis: at 0c5ec15, 2026-10-04T09:24:17Z, `pytest tests/test_summarize_e8.py -k "crlf_checkout or config_drift"` printed
  `2 passed, 13 deselected`; `git log --oneline -1 -- src/linear_ceiling/summarize_e8.py` printed `484e1be fix(e8): hash the config
  newline-normalized, as E9 does`. The Llama E8 amendment (0053) ran on this Windows checkout under the fix with no blob trick.
re-verify: grep -n "sha256_text_file(cfg.config_path)" src/linear_ceiling/e8.py src/linear_ceiling/summarize_e8.py | wc -l   # expect 2
