# A learning that falsifies a brief sentence must edit the brief in the same commit: the 2026-10-01 quantile learning left "ONE quantile convention" in CLAUDE.md for nine days

ts: 2026-10-10T21:35:00Z
commit: 5cedd54
session: pr19-agent-docs-audit (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The learning of 2026-10-01 recorded that `summary.json` carries two percentile conventions — `e7_stats` lower
nearest-rank for every quantile over handoffs, `np.quantile` linear interpolation for the pooled per-token p90/p99 — and
that the interpolated value differs by about 4 % and "looks like drift". `CLAUDE.md` kept "Quantiles come only from
`e7_stats` … the ONE pinned quantile convention" through nine days and six ledger appends, and PR #19 carried the
sentence into its rewrite and its architecture table. Two read-only skeptic audits of the rewrite against the tree
(2026-10-10) found it, together with four other contract sentences the tree contradicts (a tool that imports the pinned
`kvt`, the RunPod sitting scripts' own ancestry check, one tracked `results/` path, two wrong entry cites). The learnings
ledger and the brief are read by different readers at different times; a fact that kills a brief sentence has to land in
the brief in the same commit, or the brief is the one the next session believes. The pooled per-token quantiles that
0038 and 0045 print under the interpolating convention get their own corrective entry (staged as 0061).
basis: `docs/learnings/2026-10-01-the-summarizers-p10-p90-are-floor-index-order-statistics-and-the-same-summary-json-also-carries-np-quantile-fields.md`;
  `src/linear_ceiling/e9_tail.py` lines 114 and 132, `src/linear_ceiling/e9_compare.py` lines 136 and 159–160
  (`np.quantile`); `git log --oneline 5a71df6..5cedd54 -- CLAUDE.md` (no edit to the quantile sentence); the two audit
  reports of 2026-10-10 (this session's transcript); `AGENTS.md` on the PR branch after `561bc05`.
re-verify: grep -c "np.quantile" src/linear_ceiling/e9_tail.py src/linear_ceiling/e9_compare.py; (git show origin/zain/agent-onboarding-cleanup:AGENTS.md 2>/dev/null || cat AGENTS.md) | grep -c "Handoff-level quantiles come only from"   # e9_tail 2, e9_compare 2 or more; 1
