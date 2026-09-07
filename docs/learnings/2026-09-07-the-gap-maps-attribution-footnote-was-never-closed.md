# The gap map's "who's nearby" attributions were conditioned on a W1 lit sweep whose verdict never reached the ledger

kills: (nothing)
ts: 2026-09-07T03:56:07Z
commit: 74c35fd964262bb7d7685f7df76ffeab074996b0
session: lcfm-sprint-pickup (e992199e-cc8f-4335-bce4-fa177630087c)
status: verified
fact: docs/gap-map.md (committed verbatim by entry 0005) attributes its three gaps to named lines of
work (LLMLingua, gist/beacon, vLLM) under an explicit condition: "All 'who's nearby' attributions
require primary-source verification in the W1 sweep before appearing in the paper." The design spec
scheduled that sweep as a gated W1 task "verdict recorded in ledger". No ledger entry records a
lit-sweep verdict: the only mention of the sweep in ledger/ledger.md is entry 0005's carried-forward
note that E7's thresholds await it. The three attributions therefore have never been verified at
source and cannot appear in any submission as written; docs/2026-09-06-gap-map-revisited.md and the
LCFM outline both say so and the outline's reference list carries them as NOT cited until the
verification is recorded. A motivation-layer footnote is a claim with a deadline; nothing enforced it.
basis: `grep -n -i "lit sweep\|lit-sweep\|literature sweep" ledger/ledger.md` at 74c35fd -> one line,
  `136:before any E7 replay begins (W4), because setting them requires the W1 lit sweep's` (entry 0005);
  `grep -c` -> 1. `grep -rn -i "LLMLingua\|gist/beacon\|vLLM line" ledger/ledger.md README.md docs/*.md
  docs/paper/*.md | grep -v docs/gap-map.md` -> 2 hits: docs/2026-08-26-seed-w1.md lines 287-288 (the
  verbatim seed whose Appendix C IS the gap map) and docs/paper/2026-09-06-lcfm-outline.md line 179
  (the reference list, marked not cited until verified). No entry, no verdict, no source check anywhere.
re-verify: grep -c -i "lit sweep\|lit-sweep\|literature sweep" ledger/ledger.md   # 1 (entry 0005's forward reference only); any recorded verdict would add a line
