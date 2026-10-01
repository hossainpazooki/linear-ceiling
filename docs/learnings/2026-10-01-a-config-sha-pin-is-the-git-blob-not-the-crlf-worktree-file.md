# A config sha pin in the ledger is the LF bytes git stores, not the CRLF file in a Windows worktree

ts: 2026-10-01T04:47:26Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: Entry 0043 (ledger line 2795) pins `config/e9f.toml` at sha256 `2e7cade40489`, and the Llama E8 report pins
`config/e8f.toml` at `cba5e38c8864`. Hashing the worktree files on this Windows checkout gives `50c92535a588` and
`bf7f4e62fff4`, because the checkout is CRLF (188 and 81 CRLF lines). `git show HEAD:<file> | sha256sum` reproduces
both pins exactly. The summarizer hashes through `hashing.sha256_text_file`, which normalizes; a verifier that hashes
raw worktree bytes reports a false mismatch on Windows and a true match on Linux.
basis: at 0a51275, 2026-10-01T04:47:26Z, `sha256sum config/e9f.toml | cut -c1-12` printed `50c92535a588`;
  `git show HEAD:config/e9f.toml | sha256sum | cut -c1-12` printed `2e7cade40489`; the CRLF count printed 188. Earlier
  the same session (at 5a71df6) read `cba5e38c8864` from the Hub copy of `results/e8f/report.json` `config_sha256`
  and reproduced it from `git show HEAD:config/e8f.toml`.
re-verify: git show HEAD:config/e9f.toml | sha256sum | cut -c1-12; sha256sum config/e9f.toml | cut -c1-12   # expect 2e7cade40489 then (on a CRLF checkout) a different hash
