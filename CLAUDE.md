@AGENTS.md

# CLAUDE.md — how the operator drives Claude Code in this repository

`AGENTS.md` is the contract for any agent; this file restates nothing from it. It holds only what a Claude Code
session on the operator's machines needs on top of that contract. Program state (what is staged, what ran last,
what a statistic currently reads) is never written here; `AGENTS.md` says where it lives.

## Repo override of the global working agreement
This is a paper, not a software project. Work lands on `main` by explicit-path commits; a branch exists only to
put a change in front of a reviewer. Ad-hoc coordination, and no process beyond what the next step calls for.
This applies the global rule that a repo file may override the global one; say so when you apply it.

## The operator's machines
- **Windows** is the primary tree and the paper's editing side. Its disk cannot hold a results mirror, so an append
  script previews here only after the summary files it reads are copied over (see *Previews on Windows*).
- **The Mac mini** on the home LAN is the home side for GPU sittings since entry 0051: every results mirror, the
  upstream clone detached at each cell's pin, and the Hub staging copies live there. It is reached over ssh only.
  It is arm64, so a reader that passes on every x86 rendering can refuse there; entry 0059 records one such refusal.
- Both trees are clones of `origin`. Commits move between them through `origin`, or by a LAN fetch when the
  operator says so. Never assume the two trees match: `git status` and `git log -1` on each before a block.

## Git mechanics for Claude
- Claude writes no git history here, on either machine, including over ssh: no checkout, pull, commit, push, rm,
  branch or rebase. `git fetch` and `git show HEAD:<path> > <path>` (restoring a tracked file to its committed
  bytes) are allowed.
- Commit blocks go to the operator in Git Bash form, one commit per concern, conventional subjects, no
  attribution trailers. A block for the Mac is zsh over ssh: no `#` comments and no apostrophes anywhere in it,
  because bracketed paste makes the whole block one command and a stray quote leaves the shell at `quote>`. Put a
  check that the change took effect before and after the commit instead of a comment.
- The Mac has no git identity configured; a commit block for it starts with `git config --global user.name` and
  `user.email` unless the operator has set them.
- An append script is ratified by the operator running it, never by Claude: the staging commit (the script and
  `docs/drafts/README.md`), then `$PY docs/drafts/append_00NN.py --date YYYY-MM-DD && rm docs/drafts/append_00NN.py`,
  then two commits (the ledger alone first, then the retired script and the README's allocator line), then push.
  Claude runs the script only with `--preview`.

## GPU sittings from the Mac
The operator sits a RunPod pod from the Mac: `tools/runpod/rp.py up`, the watchdog, then the `tools/ec2/` flow over
the ssh alias the runbook names. On every sitting after a campaign's first, pass the watchdog `--kill <cap>` and
`--ttl <hours>` explicitly; its defaults are a campaign-wide spend cap and `up --hours`, which has killed a run early
once (learning `docs/learnings/2026-10-08-the-watchdogs-kill-default-is-9-dollars-of-campaign-spend-and-up-hours-is-its-ttl-set-both-explicitly-on-every-sitting-after-a-campaigns-first.md`).
The minute-by-minute log goes into the dated runbook as it happens, never reconstructed afterwards.

## Shell traps that have bitten here
- Git Bash rewrites a leading-slash argument into a Windows path, even for `python.exe`: an upload to `/workspace`
  went to a Windows path and reported success. Prefix `MSYS_NO_PATHCONV=1`, or pass bytes through Python
  (learning `docs/learnings/2026-10-07-git-bash-rewrites-a-leading-slash-argument-so-rp-py-put-dest-workspace-uploaded-to-a-windows-path-and-reported-success.md`).
- zsh over ssh does not word-split an unquoted variable: a command held in a variable becomes one missing path and
  a release chain silently skips. Spell the arguments out
  (learning `docs/learnings/2026-10-08-zsh-over-ssh-does-not-word-split-an-unquoted-variable-a-command-held-in-a-variable-becomes-one-missing-path-and-the-whole-release-chain-silently-skips.md`).
- The Bash tool's heredocs die past a few KB: write the script into the session scratchpad and run it from there.
- A loop whose body runs `ssh` has its stdin eaten by `ssh`; run each body with `< /dev/null`.
- The Windows console is cp1252: ASCII in `print()`; UTF-8 only into files opened as UTF-8.

## Secrets mechanics (the Claude side of R9)
- The `read -s HF_TOKEN` line is pasted by the operator ALONE, never inside a block Claude wrote, and the token is
  never pasted into the chat.
- A detached push is written in the shell-prefix form, `HF_TOKEN=$HF_TOKEN nohup caffeinate -i bash tools/hf_backup.sh …`.
  The `env HF_TOKEN=$HF_TOKEN …` form puts the token into argv, `ps` and the transcript
  (learning `docs/learnings/2026-10-09-env-var-equals-in-a-detached-command-line-puts-the-secret-into-argv-use-a-shell-environment-prefix-or-the-scripts-tty-prompt.md`).
  The token is revoked once the verifier prints BACKUP VERIFIED.
- The RunPod API key lives at `~/.config/linear-ceiling/runpod_api_key` and is never printed, echoed or read into
  the conversation.
- This is a public repository: no balances, tokens, hostnames or addresses in issues, pull requests, commits or docs.

## Verification choreography
- A skeptic pass (the `skeptic-verifier` agent) runs on every append-script preview before it is offered for
  ratification, and on any paper paragraph before it is offered for approval.
- Every figure in a reply is read from the result file at the point of claiming it, with the file's sha; nothing is
  restated from an earlier message, a brief or memory.
- A reader defect found on a sitting is fixed in the summarizer with a synthetic test in the same change; a
  registered tolerance or control moves only through an entry, in 0028's shape.
- A learning goes to `docs/learnings/` with a `re-verify:` line that Claude runs from the written file before
  handing the block over. A brief goes to `docs/handoff/`. Both are immutable once committed; a brief edited after
  its commit is restored to the committed bytes. Anything private (a consultation draft, reviewer correspondence)
  goes to `~/dev/briefs`, never into this tree.

## Paper text
The manuscript is not in this repository. A rewrite is delivered as the paragraph, then a "Changes, and why" list
citing entry and line for every change; approval is per paragraph, and paragraphs are not batched. A figure or
reading enters a paragraph only by the admitted evidence path in `AGENTS.md`.

## Previews on Windows
An append script reads the summary files of every experiment it cites, by sha, from `results/`. Those files live on
the Mac. Before a preview here, copy the files the script's `FILES` dict names under the same `results/<cell>/`
paths on Windows, then run `$PY docs/drafts/append_00NN.py --date YYYY-MM-DD --preview`. `results/` is gitignored
on both machines, so nothing copied can reach a commit.
