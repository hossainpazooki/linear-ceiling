# 0055's re-matching sentence names the over-0.05 count as "more than the removal"; 14 have any loss, none exceed the removal

ts: 2026-10-04T10:08:09Z
commit: 9e5249b
session: main-branch dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: Entry 0055 (and e-trunc-design.md section 10) say "aligner re-matching loses more than the removal on 10 handoffs". In
`summarize_e9_trunc`, re-matching loss is `survivable - ratio` and removal is `1 - survivable`; the 10 is
`n_with_rematching_loss_over_0_05`. 14 handoffs have any re-matching loss and on 0 does it exceed the removal. Every other
figure 0055 states recomputes exactly (review `docs/reviews/2026-10-04-0055-stated-figures-recomputed.md`). The entry is
immutable; the erratum is staged in `append_0057.py` with its counts read from `shrinkage.json`.
basis: at 9e5249b, 2026-10-04T10:08:09Z: over `results/e9t/shrinkage.json` per_handoff: `rematching_loss > 0: 14 | > 0.05:
  10 | > 0.01: 10`; `rematching_loss > (1 - survivable): 0`; `grep -n` in `src/linear_ceiling/summarize_e9_trunc.py`:
  line 179 `"rematching_loss": survivable - ratio,  # what the aligner lost beyond the removal`, line 198 `> 0.05`.
re-verify: .venv/Scripts/python.exe -c "import json;p=json.load(open('results/e9t/shrinkage.json',encoding='utf-8'))['per_handoff'].values();print(sum(v['rematching_loss']>0 for v in p),sum(v['rematching_loss']>0.05 for v in p))"   # 14 10
