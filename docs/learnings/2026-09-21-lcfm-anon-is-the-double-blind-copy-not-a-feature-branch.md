# `lcfm_anon` is the double-blind copy of the tree, not a feature branch: "drop the branches" must not include it

ts: 2026-09-21T02:38:21Z
commit: 3d2fbb14d3919cd2e798f4ffbe5132506cef1c7b
session: carryover-iclr-pickup-drift-wrapup (e7805827; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\e7805827-47f9-400a-a107-71d2eeb94fb2.jsonl)
status: verified
fact: `origin/lcfm_anon` sits three commits ahead of main and will never merge back: it censors identifying names
across the tree, drops 24 infrastructure-only records, and re-derives the ledger chain, and its README says it "is the
copy prepared for double-blind review". A branch clean-up that reads it as stale feature work and deletes it destroys
the anonymized artifact. Its ledger chain proves internal consistency of the censored copy, not that no entry was
edited, so it is never a source for a ledger figure. NOT verified here: that the anonymous code link printed in the
workshop submission resolves to this branch; the mirror's own configuration was not read.
basis: at 3d2fbb1, 2026-09-21T02:38:21Z, `git log --oneline main..origin/lcfm_anon` printed `5e37cd4 docs(readme):
  state what this branch changes from main, and why`, `f211f35 chore(anon): drop 24 infrastructure-only records from the
  submitted tree`, `85813c9 chore(anon): censor identifying names across the tree; ledger chain re-derived`; and
  `git show origin/lcfm_anon:README.md | sed -n 22,23p` printed "This branch (`lcfm_anon`) is the copy prepared for
  double-blind review. It differs from `main` in two ways, both listed below."
re-verify: git show origin/lcfm_anon:README.md | sed -n 20,23p   # expect: "## Anonymized branch" and "the copy prepared for double-blind review"
