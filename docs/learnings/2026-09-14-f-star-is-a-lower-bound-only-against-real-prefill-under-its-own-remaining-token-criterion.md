# f* is an oracle lower bound only against real partial prefill under its own remaining-token criterion; against a full-cache criterion it can over-count

kills: (nothing)
ts: 2026-09-14T09:27:49.558Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: `e9_pertoken.f_star` divides the sum of the retained deviations by the retained count (`counts = np.arange(n, 0, -1)`),
so f* is the smallest removed share with S_rem / (n − k) ≤ τ. A full-cache criterion that counts exactly repaired tokens
as zero divides the same S_rem by n, which is never larger; it is met with no more repairs than f*, and possibly fewer.
So f* is NOT a lower bound under a full-cache criterion. Entry 0023's "oracle LOWER BOUND" holds against real partial
prefill under the same remaining-token criterion (oracle selection; exact, isolated repair; no error propagation). 0023
line 1280 also requires every output stating f* to carry "oracle lower bound" and both reasons, so a paper sentence that
denies the lower bound without this scoping breaks the registered wording rule.
basis: `grep -n "suffix / counts" src/linear_ceiling/e9_pertoken.py` printed
  `77:    ok = (suffix / counts) <= tau * (1.0 + F_STAR_REL_TOL) + 1e-15`; `grep -n "counts = np.arange(n, 0, -1)"` printed
  line `76`; `grep -n 'oracle lower bound" and both reasons' ledger/ledger.md` printed line `1280`.
re-verify: grep -n "counts = np.arange(n, 0, -1)" src/linear_ceiling/e9_pertoken.py && grep -n 'carries the words "oracle lower bound"' ledger/ledger.md   # line 76, then line 1280
