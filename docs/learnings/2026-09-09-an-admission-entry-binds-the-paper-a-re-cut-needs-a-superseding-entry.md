# An admission entry's space clause binds the paper; a re-cut around a different result needs a superseding entry, not a ruling in a brief

kills: (nothing)
ts: 2026-09-09T20:40:00Z
commit: 407a38e
session: dev-47 (9c42735d)
status: verified
fact: Entry 0032 admitted E9 to the LCFM 4-pager on stated terms, one of which is space: "E9 is one paragraph,
one table, and the τ ladder in an appendix; Lane A/B premise numbers and the taxonomy remain the submission's
core (0006, 0016)." The 2026-09-09 operator ruling "re-cut the paper around E9" and the later "E-RL replaces E7
and E8 as the contrast" were recorded only in handoff briefs and the README, and neither the 09-09 brief nor the
seed noticed that they contradict a committed, immutable entry. A paper written from those briefs would breach
its own ledger. The fix is the shape 0032 itself used against 0006's scope cap: a numbered entry (0035) that
names the clause it supersedes and lists the clauses it keeps (the summarizer gate, cross-arm-beside-same-model,
coverage-with-every-number, the co-author condition). Rule: before writing from a re-cut ruling, grep the
ledger for the admission entry of every result the paper carries and read its terms; a brief cannot override an
entry.
basis: `awk '/^### 0032/,/^### 0033/' ledger/ledger.md | grep -n "one paragraph, one table"` at 407a38e -> 1 line;
  `grep -n "0032" docs/handoff/2026-09-09-lcfm-pickup-e9-long-seed-readme.md docs/2026-09-08-seed-e9-long-half.md`
  -> no mention of the space clause in either.
re-verify: awk '/^### 0032/,/^### 0033/' ledger/ledger.md | grep -c "remain the submission's core"   # 1
