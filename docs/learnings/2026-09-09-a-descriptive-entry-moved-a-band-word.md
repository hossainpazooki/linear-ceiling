# A descriptive entry moved a band word without moving a cell: under the n = 420 mapper, E8's V read-out at k = 1 reads UNRESOLVED where the n = 50 mapper read DEGRADES

kills: (nothing)
ts: 2026-09-09T03:57:54.494Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: Entries 0030–0034 are all descriptive: no `verdict:` line, no cell moves, by the ledger's rule that a
cell is decided once under its registered protocol. That rule does not make them minor. 0034 (the k = 1
mapper refit on n = 420 calibration sequences, 8.4× the n = 50 of 0009) reports the E8 k = 1 V drop at
+0.1459 with a 95% bootstrap interval [+0.1357, +0.1562] that straddles the DEGRADES edge of 0.15, and
the band word reads UNRESOLVED / UNRESOLVED; 0031 (same protocol, n = 50 mapper) reads +0.1903 on V,
UNRESOLVED / DEGRADES. H-E8 stays NOT CONFIRMED because 0020 decided it, but the paper's E8 sentence
("does not survive content shift") is calibration-sensitive on V and dead-band on K at both sizes, and
must say "at this calibration" with 0034 beside it. The E9 cross arm moved the same direction under the
larger mapper (median f* 0.9352 → 0.8106) and stayed beyond DEGRADES, so that sentence is safe as is.
basis: `sed -n 2031p ledger/ledger.md` at 4eafe40 -> `| 1 (compared k) | 0.7323 / 0.5895 | **0.6386 / 0.4437** |
  0.5708 / 0.3230 | +0.0678 / +0.1207 | +0.0937 / +0.1459 | [+0.0865, +0.1016] | [+0.1357, +0.1562] |
  UNRESOLVED / UNRESOLVED |`; 0031's k = 1 row (entry text) `... +0.1106 / +0.1903 | [+0.1022, +0.1199] |
  [+0.1779, +0.2044] | UNRESOLVED / DEGRADES`; both rows recomputed from `results/e8c/summary.md` and
  `results/e8a/summary.md` at the 2026-09-09 pre-commit check (identical to the digit).
re-verify: grep -c "| \[+0.1357, +0.1562\] | UNRESOLVED / UNRESOLVED |" ledger/ledger.md   # 1 (entry 0034, immutable)
