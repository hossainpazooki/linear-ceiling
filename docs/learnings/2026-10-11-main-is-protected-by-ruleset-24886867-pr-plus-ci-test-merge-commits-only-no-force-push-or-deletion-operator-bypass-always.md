# main is protected by ruleset 24886867: PR + CI `test`, merge commits only, no force-push or deletion; operator bypass "always"

ts: 2026-10-11T17:54:41Z
commit: f8a66ac
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: Until 2026-10-11 `main` was unprotected while seven collaborators held write, so any of them could push or
force-push over the chain-hashed ledger. The operator created ruleset 24886867 ("main: PR + CI, no rewrite", active,
target `~DEFAULT_BRANCH`): deletion blocked, non-fast-forward blocked, pull request required with 0 approvals and
`merge` as the only allowed method, required status check `test` from GitHub Actions (integration 15368), bypass list =
the operator (user 105302879) with mode "always". Consequences: co-authors land work by PR only; the operator's
ratification and docs pushes are unchanged; a PR merges with the Merge button or the merge-commit option of the CLI,
never squash or rebase. The web form saved with an empty target list the first time ("Applies to 0 targets"); the
target was set by `PUT /repos/.../rulesets/24886867` with `conditions.ref_name.include = ["~DEFAULT_BRANCH"]`.
basis: `gh api repos/hossainpazooki/linear-ceiling/rules/branches/main --jq '[.[] | .type] | join(",")'` =
  `deletion,non_fast_forward,pull_request,required_status_checks`; `gh api .../rulesets/24886867` =
  enforcement `active`, include `~DEFAULT_BRANCH`, `allowed_merge_methods ["merge"]`, `required_approving_review_count 0`,
  `required_status_checks [{context: test, integration_id: 15368}]`, bypass `[{actor_id: 105302879, bypass_mode: always}]`;
  before the fix, `GET .../branches/main/protection` = 404 "Branch not protected" and `rulesets` = `[]`.
re-verify: gh api repos/hossainpazooki/linear-ceiling/rules/branches/main --jq '[.[] | .type] | join(",")'   # deletion,non_fast_forward,pull_request,required_status_checks
