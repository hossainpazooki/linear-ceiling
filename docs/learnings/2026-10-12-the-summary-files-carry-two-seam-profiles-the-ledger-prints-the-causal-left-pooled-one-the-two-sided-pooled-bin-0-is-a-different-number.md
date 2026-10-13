# The summary files carry two seam profiles; the ledger prints the causal left_pooled one; the two-sided pooled bin 0 is a different number

ts: 2026-10-12T03:21:11Z
commit: 081994f
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `results/e9/summary.json` has both `seam_profile_pooled` (two-sided distance) and `seam_profile_left_pooled` (causal
distance b⁻(t), entry 0025). The ledger's printed E9 profile (0029:1786, bin 0 = 0.236) is the causal one. The first cut of
`tools/readme_figure.py` plotted the two-sided field, whose bin 0 is 0.174 and cannot be matched to any ledger line; the
committed figure plots `seam_profile_left_pooled.same_K`. Any figure built from these files must say which profile it reads.
basis: python on `results/e9/summary.json`: `seam_profile_pooled.same_K[0]` = `{'bin': '0', 'n_tokens': 3877, 'median': 0.17441831438647298}`;
  `seam_profile_left_pooled.same_K[0]` = `{'bin': '0', 'n_tokens': 2278, 'median': 0.23581409699332734}`;
  `grep -n "0\.236" ledger/ledger.md` → line 1786 "Seam profile under the causal distance b⁻(t) (0025)…" (captured 2026-10-12T03:21:11Z at 081994f; needs the local results mirror).
re-verify: grep -n "seam_profile_left_pooled" tools/readme_figure.py | head -1   # the committed figure reads the causal profile
