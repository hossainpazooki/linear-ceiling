# `jq` is not on this machine's Git Bash PATH, so a re-verify line that pipes to `jq` fails here; `gh --jq` is the substitute

ts: 2026-10-02T04:01:15Z
commit: a470322
session: llama-branch-lcfm, formerly Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: On the home Windows machine (Git Bash / MINGW64) `jq` is absent, so `gh … --json x | jq …` exits 127 and, inside a
`;`-chained command, aborts the rest of the line with "The pipe is being closed". `gh` 2.93.0 ships its own `--jq` flag,
which evaluates the same expressions in-process; every re-verify line in this repo that reads GitHub state should use
`gh --json … --jq …` rather than a pipe to `jq`, or it false-fails on this machine (the WSL venv box is a separate PATH).
basis: at a470322, 2026-10-02T04:01:15Z, `command -v jq || echo "jq: not found"` printed `jq: not found`; `gh --version`
  printed `gh version 2.93.0 (2026-05-27)`; sixteen seconds earlier `gh pr list --state open --json number | jq length`
  printed `/usr/bin/bash: line 1: jq: command not found` and `write /dev/stdout: The pipe is being closed`.
re-verify: command -v jq >/dev/null && echo "jq present" || echo "jq absent"; gh pr list --state open --json number --jq length   # expect "jq absent" on this machine, then the open-PR count (0 at a470322)
