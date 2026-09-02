# A float32 per-token record makes "at or below the mean" fail by 1e-11 and costs one whole token

kills: (nothing)
ts: 2026-09-01T23:36:26Z
commit: f48b53639186dd5396e8a4b4368bd627050ed098
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: The oracle recompute fraction f*(tau) removes tokens until the mean of the rest is at or
below tau. With tau = 1 - R^2 computed in float64 and the per-token squares stored as float32,
the recomputed mean lands 1.2e-11 ABOVE tau, so an exact comparison removes one token and the
mapper's own f* reads 1/2560 = 0.00039 instead of the 0 it is by construction. A quantized
record turns an equality-at-the-boundary rule into a coin flip; the rule now carries an
explicit 1e-9 relative tolerance, registered in 0023, and the calibration refuses to write a
tau at which the mapper's own f* is not exactly zero.
basis: first `summarize_e9 --calibrate-tau` run at commit f48b536 (pre-dates the entry-0023
  commits; calibration directory created 23:36:26Z): K `"at_tau_mean": 0.000390625` before
  the tolerance; after it, 0.0. Gap measured on the final record: `mean - tau =
  1.2312e-11` (2026-09-01T23:56Z).
re-verify: .venv/Scripts/python.exe -c "import json,numpy as np;z=np.load('results/e9/calibration/heldout.tokens.npz');n=int(z['n_heldout']);t=json.load(open('results/e9/calibration/tau.json'));d=(z['K_sq'].astype(np.float64)/(z['sst_K']/n)[None]).reshape(n,-1).mean(1);print(d.mean()-t['tau']['K'])"
