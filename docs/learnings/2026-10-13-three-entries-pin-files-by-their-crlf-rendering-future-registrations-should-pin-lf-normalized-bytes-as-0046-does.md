# Three entries pin files by their CRLF rendering; future registrations should pin LF-normalized bytes, as 0046 does

ts: 2026-10-13T14:00:13Z
commit: 5c4e645
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: suspected
fact: Entries 0050 and 0055 pin `align/coverage.json` files by the sha of their CRLF rendering (written on Windows), 0057 and
0051 state "the other rendering" beside each, and 0059 registered a τ-recomputation tolerance for the same platform
reason. Entry 0046 already pins its configs by LF-normalized digest (line 1390) and 0055's config pins are LF-normalized
(line 3441). The existing entries are correct as stated; the trap is a future registration that pins raw bytes of a
text file and then refuses on the other platform. Suspected because the protocol (R1–R12) does not yet say "pin
normalized bytes"; adding it is the operator's protocol change, not this entry's.
basis: `grep -n "CRLF rendering\|two renderings of one content" ledger/ledger.md | cut -c1-70` = `3843:both ways before this entry). **Coverage file, two renderings of ;3844:`align/coverage.json` at `16121e677b97…`, the sha of the home f;3989:**Coverage files, two renderings of one content.** Entry 0055 pin;` (captured 2026-10-13T14:00:13Z at 5c4e645).
re-verify: grep -c "CRLF" ledger/ledger.md   # non-zero while the raw-byte pins stand
