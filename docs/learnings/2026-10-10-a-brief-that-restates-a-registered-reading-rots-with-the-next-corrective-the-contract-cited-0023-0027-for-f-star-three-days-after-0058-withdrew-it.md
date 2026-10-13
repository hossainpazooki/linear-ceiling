# A brief that restates a registered reading rots with the next corrective: the agent contract cited 0023/0027 for f* three days after 0058 withdrew it

ts: 2026-10-10T21:30:00Z
commit: 5cedd54
session: pr19-agent-docs-audit (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: PR #19 rewrote `CLAUDE.md` into a 93-line contract whose paper-facing section said "The registered reading of f* is in
entries 0023 and 0027". The branch was cut from `efab85a` (2026-10-04); entry 0058 withdrew that reading on 2026-10-07 (f* is
the oracle REMOVAL fraction, not a lower bound on recompute). Nothing gates a contract sentence against the ledger, so the
always-loaded file would have reinstated a superseded reading on merge. The 190-line `CLAUDE.md` it replaced had the same
defect class in its program-state paragraph, edited by hand five times in two days. The fix is structural, not a cite
update: the contract (now `AGENTS.md`) says a reading is whatever the latest entry registers and what its summarizer
prints, and never restates one. A sentence that points cannot rot; a sentence that paraphrases rots at the next entry.
basis: PR #19 head `1217a98` `CLAUDE.md` line 41 (the 0023/0027 sentence); `ledger/ledger.md` `### 0058` header
  (2026-10-07); the review comment on PR #19 of 2026-10-10 (issuecomment-6100466701); `AGENTS.md` on the PR branch
  after `b71147a`: "The reading of every registered statistic … is whatever the LATEST ledger entry on it registers …
  This file never restates a reading".
re-verify: grep -c "^### 0058 " ledger/ledger.md; (git show origin/zain/agent-onboarding-cleanup:AGENTS.md 2>/dev/null || cat AGENTS.md) | grep -c "never restates a reading"   # 1; 1
