# This machine's E7 report is the 09-01 artifact the 09-10 summary already recorded, not an independent third regeneration

ts: 2026-10-01T19:08:00Z
commit: a6a746d
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: PR #6 says two of three E7-report regenerations give `0aba0fbe...` and 0044's `27dc922e...` is the outlier. The Llama session counted this machine as a third agreeing regeneration. `results/e7/skeleton_report.json` here hashes `0aba0fbe7aba...` but is dated 2026-09-01 23:36, i.e. it IS the file the 2026-09-10 long-run summary recorded; the local e9f recomputation re-read it rather than regenerating it. Independent evidence for the outlier stays at two (the 09-10 record and the clean clone), and the corrective entry says so.
basis: at a6a746d, ~19:08Z (before the 19:12Z PR comment): `sha256sum results/e7/skeleton_report.json | cut -c1-16` printed `0aba0fbe7aba2f28`; `ls -la --time-style=long-iso results/e7/skeleton_report.json` printed `2026-09-01 23:36`; `grep -n -E "27dc922e|0aba0fbe" ledger/ledger.md` printed lines 1466, 2923, 2924. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: ls -l --time-style=long-iso results/e7/skeleton_report.json | awk '{print $6}'   # expect 2026-09-01 (local results tree); the file predates every Llama run
