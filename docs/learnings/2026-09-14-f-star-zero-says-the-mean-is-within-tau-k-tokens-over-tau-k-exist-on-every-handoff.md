# f*(τ_K) = 0 says a handoff's mean deviation is within τ_K; tokens above τ_K exist on every one of the 60 handoffs

ts: 2026-09-14T09:25:11Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: lcfm-sprint-e9l-review (9c42735d)
status: refuted-assumption
fact: The assumption refuted is that f*(τ_K) = 0 means no matched token exceeds τ_K. Entry 0023 defines f*(τ) as the
smallest fraction of matched tokens that, removed in descending order of δ_K, leaves the MEAN δ_K of the rest at or
below τ. So f* = 0 says the handoff's mean is already within τ_K. On the committed records all 60 handoffs have
f*(τ_K) = 0, and all 60 also have tokens above τ_K:
- 0029's 25: 9,047 of 155,257 matched tokens (5.8%); per-handoff means 0.0284–0.2207.
- 0036's 35: 30,701 of 387,508 (7.9%); per-handoff means 0.0429–0.2692.
Both are against τ_K = 0.3186442653116294. The verdicts stand. The prose of 0029 ("inside the tolerance at every
matched token of every handoff") and 0036 over-states its own statistic, and an append-only corrective entry is owed.
Three parties found this independently: the co-author clean-clone review (ef4c2ca,
`docs/reviews/2026-09-11-clean-clone-reproduction.md`), PR #4's note (ffef90a, `docs/2026-09-13-e-rl-validation.md`), and
this session. This session first marked the universal-token sentence verified on 2026-09-11 because it matched 0029's
text. Matching a ledger sentence is not checking it against the registered definition.
basis: re-captured at a5053b2 at 2026-09-14T09:25:11Z, using the summarizer's own functions (`e9_pertoken.centered_delta`,
  `token_mean`, `f_star`, `summarize_e9._sst`) and τ_K read from each `summary.json`:
  `e9: tau_K 0.3186442653116294 | handoffs 25 | f*(tau_K)==0 on 25 | tokens over tau_K 9047 of 155257 | handoffs with
  any token over 25 | per-handoff mean dK 0.0284-0.2207` and `e9l: tau_K 0.3186442653116294 | handoffs 35 |
  f*(tau_K)==0 on 35 | tokens over tau_K 30701 of 387508 | handoffs with any token over 35 | per-handoff mean dK
  0.0429-0.2692`. 0023 at `ledger/ledger.md` 1274–1276: "f*(τ) is the smallest fraction of `M` that, removed
  (recomputed exactly), leaves the MEAN δ_K over the remaining tokens at or below τ". First captured
  2026-09-12T02:25Z at cf4047f with a typed τ; see this date's typed-tolerance entry.
re-verify: .venv/Scripts/python.exe -c "import json,numpy as np;from linear_ceiling.e9_pertoken import centered_delta as c,token_mean as m,f_star as f;from linear_ceiling.summarize_e9 import _sst;R='results/e9l/';t=json.load(open(R+'summary.json',encoding='utf-8'))['rule']['tau_K'];S=json.load(open(R+'report.json',encoding='utf-8'))['scores'].values();B=[(json.load(open(R+'scores/'+r['score_file'],encoding='utf-8')),np.load(R+'tokens/'+r['tokens_file'])) for r in S];D=[m(c(k['same_K'],_sst(b,'same','K'),int(b['n_pairs']))) for b,k in B];print(sum(f(d,t)==0 for d in D),sum(int((d>t).sum()) for d in D),sum(len(d) for d in D),sum(int((d>0.3186).sum()) for d in D))"   # needs the gitignored results/e9l mirror; expect: 35 30701 387508 30711 (f*=0 handoffs, over tau_K, matched tokens, over a typed 0.3186)
