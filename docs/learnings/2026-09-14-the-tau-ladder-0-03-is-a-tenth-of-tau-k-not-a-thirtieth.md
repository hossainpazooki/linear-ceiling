# The τ ladder's 0.03 is a tenth of τ_K, not a thirtieth

ts: 2026-09-14T02:17:22Z
commit: 12c113c2f9b0e32e6e74e340e266ff9e2a5f5acd
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: The descriptive τ ladder {0.1, 0.03} (0025) is written in R²'s own units, not as fractions of τ_K. Against
τ_K = 0.3186, the 0.03 rung is 0.094 of it, about a tenth, and the 0.1 rung is 0.314 of it. A draft abstract on
2026-09-14 said "at a thirtieth of the tolerance it reads 0.14 and 0.53", but 0.03 is a thirtieth of 1.0, not of the
tolerance. PR #4's note had already flagged the same wording. State the absolute τ, or say "a tenth of the tolerance".
basis: session arithmetic at 12c113c, 2026-09-14T02:17Z: `0.03 / tau_K = 0.09414887781099854 | 1/30 =
  0.03333333333333333`. `docs/2026-09-13-e-rl-validation.md` line 50 (merged in ffef90a): "tenth of `0.3186`, not one
  thirtieth." The operator's manuscript is not on this machine, so whether it kept the wording is not captured here; the
  untracked 09-13 scaffold `docs/paper/tex/main.tex`, which is not the manuscript, had 0 occurrences of "thirtieth" at
  2026-09-14T09:25Z, after this entry's anchor.
re-verify: .venv/Scripts/python.exe -c "import tomllib; r=tomllib.load(open('config/e9.toml','rb'))['e9']['rule']; print(r['tau_ladder'], r['tau_K'], [round(t/r['tau_K'],4) for t in r['tau_ladder']])"   # expect: [0.1, 0.03] 0.3186442653116294 [0.3138, 0.0941]
