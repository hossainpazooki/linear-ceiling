# The co-author's cache-injection repo prefills the gaps on the assembled cache — the in-situ reuse E-BEH needs — and reviews 0025–0029 in this repo's format

ts: 2026-10-02T03:35:17Z
commit: 470133e
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `neuriv/cache-injection` (one commit, `8e8417a`, "Publish cache-injection replication materials"; Qwen3-1.7B at a pinned
revision; the three public E9 archives at pinned Hub revisions) contains in `practical.py::construct()` the reuse E-BEH's
design asks for: aligned blocks copy the sender's K/V with keys re-rotated by `dstpos − srcpos` using the model's `inv_freq`,
and every unmatched span is prefilled ON TOP of the cache assembled so far (`practical.py:38`, `:48`), so seams attend to reused
neighbours — the achievable version, not the oracle. Its recorded aggregates (`results/historical-summary.json`, run
2026-09-23 on an Apple M5): short-window replacement with 50–95 % of the prefix replaced kept the top next token on 8 of 8
cases (max total variation 6.35 %; a position permutation changed it on 3 of 8); three complete-history reuses answered
4 of 8 extraction questions against 5 of 8 fresh, at 1.9–2.7× speedup. Its `docs/refutations.html` reviews entries
0025–0029 in this repo's claim / attack / evidence / finding / limits format and reproduces the tokenwise counts
9,047 / 10,336 / 30,701 that entry 0045 now states. It uses its own difflib alignment (blocks ≥ 32) rather than the
archived pairs, pins transformers 4.57.6, and has no subset-recompute or teacher-forced-continuation arm.
basis: at 470133e, 2026-10-02T03:35:17Z, `curl -s https://raw.githubusercontent.com/neuriv/cache-injection/main/practical.py |
  grep -n …` printed line 38 `if dst>position:cache,_=prefill(model,receiver[position:dst],cache)`, line 45
  `kk=rotate(kk,dstpos-srcpos,freq)`, line 48 `if position<len(receiver)-1:cache,_=prefill(model,receiver[position:-1],cache)`;
  the clone at `C:\m\ci` is at `8e8417a`. The aggregates and the refutation text were read from the clone's
  `results/historical-summary.json` and `docs/refutations.html` on 2026-10-01 (~22:30Z).
re-verify: curl -s https://raw.githubusercontent.com/neuriv/cache-injection/main/practical.py | grep -c "cache,_=prefill(model,receiver\[position"   # expect 2: the gap prefills before and after the copied blocks
