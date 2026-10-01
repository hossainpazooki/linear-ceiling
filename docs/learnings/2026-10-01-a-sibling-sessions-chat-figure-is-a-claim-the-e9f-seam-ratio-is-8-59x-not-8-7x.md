# A sibling session's chat figure is a claim: the e9f seam-bin mean/median ratio is 8.59x, not the 8.7x it reported

ts: 2026-10-01T18:50:00Z
commit: a6a746d
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: refuted-assumption
fact: The Llama session's close reported seam-bin means "up to 8.7x the medians" for e9f. Recomputed from `results/e9f/tail.json`, the maximum over the six seam bins is 8.59x (bin 16+, n = 151,808, mean 0.0873 / median 0.0102) and over the position bins 7.58x. Every other figure in that report reproduced (11.27 % over tau_K, max per-handoff mean 0.2860, gap 0.00008). A number pasted from another session's chat goes into nothing until it is recomputed from the pinned output.
basis: at a6a746d, ~18:50Z (between the pick-up report and the 19:12Z PR comment): a python read of `results/e9f/tail.json` printed `seam ratio max 8.59  position-bin ratio max 7.58` and, per bin, `bin 16+  n=151808 mean 0.0873 median 0.0102 ratio 8.59`; `tail.json` pins `summary.json` e1e5feb8aadd and `report.json` f9335c0587ad, both matching the files. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: .venv/Scripts/python.exe -c "import json;t=json.load(open('results/e9f/tail.json'));print(round(max(b['mean']/b['median'] for b in t['seam_left_bins']['same_K'] if b['median']),2))"   # expect 8.59 (local results tree)
