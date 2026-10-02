# `git checkout -- <file>` on an unmodified file does not rewrite its line endings; to get the LF bytes git stores, write the blob

ts: 2026-10-02T03:35:16Z
commit: 470133e
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: With `core.autocrlf=true`, `git -c core.autocrlf=false checkout -- config/e8f.toml` leaves the CRLF worktree file as it is
(raw sha stays `bf7f4e62fff4`): checkout skips a path whose index entry already matches, so the conversion setting never
applies. `git show HEAD:config/e8f.toml > config/e8f.toml` writes the stored LF bytes (`cba5e38c8864`, the pin). Afterwards
`git status` shows the file as modified by line ending only; `rm` plus `git checkout -- <file>` restores the CRLF form and a
clean status. Needed once on 2026-10-01 to run the raw-byte-hashing E8 summarizer on Windows (previous learning).
basis: at 470133e, 2026-10-02T03:35:16Z, after `git -c core.autocrlf=false checkout -- config/e8f.toml`, `sha256sum` printed
  `bf7f4e62fff4`; `git show HEAD:config/e8f.toml > <tmp>` then `sha256sum <tmp>` printed `cba5e38c886…`; the earlier run log
  (18:05Z, 2026-10-01) shows the checkout leaving `bf7f4e62fff4` and the blob write giving `cba5e38c8864` with status ` M`.
re-verify: git -c core.autocrlf=false checkout -- config/e8f.toml; sha256sum config/e8f.toml | cut -c1-12; git show HEAD:config/e8f.toml | sha256sum | cut -c1-12   # expect bf7f4e62fff4 (unchanged CRLF worktree) then cba5e38c8864 (the blob)
