# An append block must `git add ledger/ledger.md`; a 42-line ledger diff after an append is the entry, not line endings

ts: 2026-10-04T09:24:27Z
commit: 0c5ec15
session: llama-branch-lcfm (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: refuted-assumption
fact: My commit block for 0052 ran the append script, `git rm` of the script, then `git commit -m …` with no `git add ledger/ledger.md`.
Commit `560c26a` therefore holds only the script's deletion; the appended entry stayed unstaged. I then saw ` M ledger/ledger.md`,
assumed the 10-02 line-ending artefact, and ran `rm ledger/ledger.md && git checkout -- ledger/ledger.md`, which erased the append.
Recovery was exact because every input is deterministic (the script from `bb0e139`, the same `--date`, the same prior text gives the
same chain), and the entry landed in `f016bde`. Two rules: a block that retires an append script stages the ledger in the same
commit, explicitly; and `git diff --stat -- ledger/ledger.md` is read BEFORE any restore, since an eol-only change shows 0 insertions
and an append shows the entry's line count.
basis: at 0c5ec15, 2026-10-04T09:24:27Z, `git show --stat --oneline 560c26a | tail -2` printed `docs/drafts/append_0052.py | 179 ----`
  / `1 file changed, 179 deletions(-)`; `git show --stat --oneline f016bde | tail -2` printed `ledger/ledger.md | 42 ++++` /
  `1 file changed, 42 insertions(+)`. The erasure and regeneration happened ~08:38–08:43Z at 560c26a.
re-verify: git show --stat --oneline 560c26a | grep -c "ledger/ledger.md"   # expect 0 (the retire commit carried no ledger change)
