# The e9fl backup dataset is private; a README sentence called every backup public; the anonymous API probe is the check

ts: 2026-10-12T03:21:00Z
commit: 081994f
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: refuted-assumption
fact: The README draft of 2026-10-11 said every R8 backup dataset is public. It is not: `hossainpazooki/linear-ceiling-e9fl-2026-10-07`
(second family long cell, entry 0051) answers 401 to an anonymous request while `…-e9t-2026-10-08` answers 200. README
and `docs/paper-to-record.md` now say "private as of 2026-10-11"; the visibility ruling is the operator's (Open in the handoff).
basis: `curl -s -o /dev/null -w '%{http_code}\n' https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9fl-2026-10-07` = `401`;
  same for `…-e9t-2026-10-08` = `200` (captured 2026-10-12T03:21:00Z at 081994f).
re-verify: curl -s -o /dev/null -w '%{http_code}\n' https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9fl-2026-10-07   # 401 while private
