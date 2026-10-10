# A registered float tolerance is a platform rendering: 0023's 1e-9 τ recomputation check held on every x86 rendering and refused arm64 at 3.7e-9 (entry 0059)

ts: 2026-10-08T23:42:00Z
commit: b33c6ce
session: e-trunc-0057-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `summarize_e9` re-derives τ from the archived k=1 mapper's held-out R² and 0023 registers that it "refuses on
disagreement (1e-9)" — applied as |a − b| ≤ tol · max(1, |a|, |b|), an absolute gap for τ < 1. The config floats were
computed on Windows x86. Recomputing the SAME arithmetic on the same mapper bytes gave five renderings: x86 Linux at 13
threads (K gap 1.0e-10, V 7.3e-11) and at 1 thread (4.2e-11, 4.3e-10) — within 1e-9 and different from each other — and
arm64 macOS at 1 and 8 threads, identical to each other (deterministic, not thread jitter) and 3.7e-9 away on V, so the
Mac mini home side refused E-TRUNC's FULL level: `config tau_V 0.4867056499055992 != recomputed 0.48670564617346357`. The
Llama cell (0051) had passed on the same machine only because its gaps (2.6e-10, 1.9e-11) fell under 1e-9 by magnitude.
Entry 0059 registered 1e-7 with the five renderings as files (the 0028 move); the τ every reading uses stays the config
float, so nothing moved. Rules: (1) an equality-grade tolerance on a recomputed float is a property of the platform that
produced the registered value — register it with renderings from every home platform that will run the reader; (2)
before loosening, test thread count and a second architecture separately, so the entry can say which it is; (3) the
same lesson in bytes: the archived `r2.json` 0023 pins by sha is the CRLF checkout rendering of the LF object.
basis: ledger 0059 (its table; files `results/e9t-full/calibration-{x86,arm64}/threads*/tau.json` + `platform.json` on
  the home machines); runbook `docs/2026-10-04-e-trunc-gpu-runbook.md` §6 19:07:55, 19:10–19:14, 19:12–19:16;
  `src/linear_ceiling/summarize_e9.py` `_TAU_TOL`.
re-verify: .venv/Scripts/python.exe -c "import json,tomllib;c=tomllib.load(open('config/e9t-full.toml','rb'))['e9']['rule']['tau_V'];[print(d,'%.1e'%abs(c-json.load(open(f'results/e9t-full/{d}/tau.json'))['tau']['V'])) for d in ('calibration-x86/threads13','calibration-x86/threads1','calibration-arm64/threads1','calibration-arm64/threads8')]"   # 7.3e-11 4.3e-10 3.7e-09 3.7e-09
