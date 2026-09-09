# On the one corpus that records per-request sizes, compaction never occurs: for Gap 2 the gap is occurrence, not recording

kills: (nothing)
ts: 2026-09-09T03:57:39.605Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: The LCFM outline's abstract states the paper's binding finding as "public trace formats drop every
field cache economics needs". For compaction that is not what the ledger shows. Entry 0015 records that
tau2-bench, the one suite that records per-request prompt sizes, has zero compaction events on all 800
trajectories that could evidence one; the other 2,104 are NOT MEASURABLE. So on the corpus where the
field IS recorded, the event does not happen. The recording-gap reading holds for model switches,
timestamps and the hidden prefix; for compaction the honest sentence is "every field but one is dropped,
and on that one the event never occurs on benchmark runs". The revisited gap map hedges this in prose;
the abstract does not. A reviewer will write this objection if the paper does not, and the recorded-corpus
experiment (revisited gap map, open item) is the one that would separate the two readings.
basis: `grep -n "zero compaction events" ledger/ledger.md` at 4eafe40 -> `872:**H-E7b -- UNESTIMABLE.** The
  compaction break-even distribution has no support: zero compaction events`; `docs/2026-09-06-gap-map-revisited.md`
  line 58 `compaction and idle expiry on 800`, line 74 `zero compaction events on the 800 trajectories that record
  per-request`; outline line 47 `public trace formats drop every` (abstract).
re-verify: grep -c "zero compaction events" ledger/ledger.md && grep -c "drop every" docs/paper/2026-09-06-lcfm-outline.md   # 1 and >=1 until the abstract is re-cut
