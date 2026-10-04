# A count read off a printed table was wrong twice in one hour; recount by code before it reaches a doc

ts: 2026-10-04T09:35:00Z
commit: a2742b9
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: From a 35-row diagnostic table printed by a scratch script, the session wrote "5 handoffs keep nothing (|M_∩| = 0)" and "re-matching loses more on 9 handoffs" into the design doc and into its own messages. The module recount (`summarize_e9_trunc --shrinkage`) gave 11 and 10. Then, while writing THIS entry, the session re-explained the 5 as "the handoffs with no physically survivable token" — and executing the re-verify line below gave 4 (seven rows print 0.000 at three decimals; four are exactly zero). Three counts eyeballed from one table, three wrong; every one caught only by a recompute in code (the registration script states its figures from an in-process run, and the learnings convention executes the re-verify line from the written file).
basis: design doc §10 before/after the 09:2xZ and 10:1xZ edits; `results/e9t/shrinkage.json` keys `n_zero` (11), `n_with_rematching_loss_over_0_05` (10), and `survivable_fraction == 0` on 4 handoffs vs the eyeballed 5 / 9 / 5.
re-verify: .venv/Scripts/python.exe -c "import json; s=json.load(open('results/e9t/shrinkage.json')); print(s['n_zero'], s['n_with_rematching_loss_over_0_05'], sum(1 for r in s['per_handoff'].values() if r['survivable_fraction']==0))"   # expect 11 10 4
