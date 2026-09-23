# A tolerance typed at four decimals shifts the over-tolerance count; read τ_K from the config, never from prose

ts: 2026-09-14T09:25:40Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: τ_K is registered at full precision: 0.3186442653116294 in `config/e9.toml`, recomputed by the summarizer, which
refuses on disagreement. The ledger prose prints 0.3186. On the E9-long records, a probe that types 0.3186 counts 30,711
matched tokens over τ_K, where the registered value gives 30,701; ten tokens lie in (0.3186, τ_K]. On the short cell
both give 9,047. This session's 2026-09-11 count used the typed value, and 30,711 stayed in outline v3 until 3f494f7
corrected it. A tolerance read off prose is a different statistic from the registered one. Read τ from the config or
from the summary's `rule` block.
basis: re-captured at a5053b2, 2026-09-14T09:25:40Z, with the summarizer's functions:
  `e9: over typed 0.3186 = 9047 | over registered 0.3186442653116294 = 9047 | tokens in (0.3186, tau_K] = 0` and
  `e9l: over typed 0.3186 = 30711 | over registered 0.3186442653116294 = 30701 | tokens in (0.3186, tau_K] = 10`.
  Commit 3f494f7: "docs(paper): v3 tail count at the registered tau_K (30,701)".
re-verify: .venv/Scripts/python.exe -c "import json,numpy as np;from linear_ceiling.e9_pertoken import centered_delta as c,token_mean as m;from linear_ceiling.summarize_e9 import _sst;R='results/e9l/';t=json.load(open(R+'summary.json',encoding='utf-8'))['rule']['tau_K'];S=json.load(open(R+'report.json',encoding='utf-8'))['scores'].values();D=[m(c(np.load(R+'tokens/'+r['tokens_file'])['same_K'],_sst(json.load(open(R+'scores/'+r['score_file'],encoding='utf-8')),'same','K'),int(json.load(open(R+'scores/'+r['score_file'],encoding='utf-8'))['n_pairs']))) for r in S];print(sum(int((d>0.3186).sum()) for d in D),sum(int((d>t).sum()) for d in D))"   # needs the gitignored results/e9l mirror; expect: 30711 30701
