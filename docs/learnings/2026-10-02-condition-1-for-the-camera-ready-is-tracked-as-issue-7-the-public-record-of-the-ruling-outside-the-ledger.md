# Condition 1 for the camera-ready is tracked as issue #7 — the public record of the ruling, outside the ledger

ts: 2026-10-02T04:00:59Z
commit: a470322
session: llama-branch-lcfm, formerly Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: The Condition 1 ruling (numbers-freeze clause of 0032 moot for the camera-ready; a co-author refutation merged under
`docs/reviews/` with two signatures remains; scope widened to 0036/0038 and 0045's tail; R13/R14 in, R7 via E-BEH and the
limitations paragraph, R8 deferred until E-TRUNC has run) lives in two places only: entry 0045's scope sentence and GitHub
issue #7 (opened 2026-10-02T03:46:37Z by the operator's account, mentions `@neuriv` and `@ritvikagg`, closing line
"entries 0025–0045 stay as written"). The review PR is expected to reference the issue; nothing in `ledger/` records the
issue number, so a reader of the ledger alone does not learn where the review is being coordinated. The ledger stays
descriptive; the issue is the coordination record.
basis: at a470322, 2026-10-02T04:00:59Z, `gh issue view 7 --json number,state,title,url,createdAt,author,comments` printed
  `{"author":"hossainpazooki","comments":0,"createdAt":"2026-10-02T03:46:37Z","number":7,"state":"OPEN","title":"Condition 1
  for the camera-ready: co-author refutation of 0025–0029, extended to the cells the paper prints", …}`; `gh pr list --state open`
  printed nothing; `grep -c "issues/7" ledger/ledger.md` printed 0.
re-verify: gh issue view 7 --json state,createdAt --jq '.state + " " + .createdAt'   # expect OPEN 2026-10-02T03:46:37Z (CLOSED once the review PR is merged with both signatures)
