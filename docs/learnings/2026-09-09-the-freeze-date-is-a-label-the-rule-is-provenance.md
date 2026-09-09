# The numbers-freeze "date" is a gate label; the registered rule is provenance-only, so missing the date costs nothing on the ledger

kills: (nothing)
ts: 2026-09-09T03:57:39.866Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: The LCFM outline, the README and three days of sprint planning treated "numbers freeze EOD
2026-09-08" as a stop-work event and drove the 09-08 GPU sitting toward whatever could be frozen by
then (the §5.1 calibration-size chain). Entry 0006 registers something narrower: "the 4-page submission
may contain only numbers that recompute clean from results/ via a fail-closed summarizer". The date is
the gate's label, not a term of the rule. A figure that first recomputes clean on 09-09 or 09-10
satisfies 0006 as written. What the date did was allocate the day's compute to the section least
relevant to the paper while the section that IS the paper (§3.5, E9) stayed unfrozen on a zero-compute
block: a summarizer refusal known since 09-04 and a ruling open since 09-07. Rule for the next sprint:
a freeze date schedules the LAST summarizer run, never the choice of which experiment to run.
basis: `awk '/^### 0006/,/^### 0007/' ledger/ledger.md | grep -n -A3 "Numbers-freeze gate"` at 4eafe40 ->
  `91:- **Numbers-freeze gate, EOD 2026-09-08:** the 4-page submission may contain only numbers` /
  `92-  that recompute clean from results/ via a fail-closed summarizer, in the pattern of` /
  `93-  summarize_e0. Scope cap: Lane A/B premise numbers and the taxonomy; the transfer-fidelity` /
  `94-  leg and compaction break-even appear only if they clear the same gate.`; outline freeze table
  row `| §3.5 | summarize_e9 → 0032 | REFUSED 2026-09-07 ...` unchanged on 09-09.
re-verify: awk '/^### 0006/,/^### 0007/' ledger/ledger.md | grep -c "recompute clean from results/ via a fail-closed summarizer"   # 1; the rule names no stop-work
