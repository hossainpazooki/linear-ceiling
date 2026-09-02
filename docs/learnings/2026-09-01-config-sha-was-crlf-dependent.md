# A raw-bytes config sha differs between LF and CRLF checkouts of the same commit

kills: (nothing)
ts: 2026-09-01T23:45:25Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling track-b (session_01RRk8euGRszMDP4z12wDdJz)
status: verified
fact: Every E7 report's `config_sha256` was `sha256_file_bytes(config/e7.toml)`, the on-disk
bytes. Entries 0013-0022 cite 6915666d452d for an unchanged config, computed on an LF working
copy; a fresh worktree checkout of the same commit is CRLF (autocrlf), and the summarizer
there recorded 9c488cc3c744 for the same committed file. The recorded provenance sha was a
property of the checkout, not of the config, and a report written on a Linux box and
summarized on a Windows checkout would have refused with `config_sha256 mismatch`. Fix:
`hashing.sha256_text_file` (universal-newline text, UTF-8), equal to the raw digest for LF
files so every recorded value stays valid; applied to E7 in the Track B merge and to E9 by
Track A's 7093e55. E0 and E8 (`e8.py`, `summarize_e8.py`) still hash raw bytes.
basis: `python -m linear_ceiling.summarize_e7` in the CRLF worktree printed
  `config sha256 9c488cc3c744 | manifest sha256 371fb4bf3cb0 (config/e7-manifest.json, entry 0024) | trace files verified: 188`
  for a report it had just verified, while entries 0013/0018 cite `config sha256 6915666d452d`
  for the same committed bytes; after the fix the rebuilt report printed
  `built in 2s; config 6915666d452d; manifest 371fb4bf3cb0`.
re-verify: python -c "from linear_ceiling.hashing import sha256_text_file as s;print(s('config/e7.toml')[:12])"   # d16cf4659aab on LF and CRLF checkouts alike (the config gained [e7.overlap_null] with 0024)
