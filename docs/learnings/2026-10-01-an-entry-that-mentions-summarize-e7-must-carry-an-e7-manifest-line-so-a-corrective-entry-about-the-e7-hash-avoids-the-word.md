# An entry that mentions `summarize_e7` must carry an `e7-manifest-sha256:` line, so an entry about the E7 report hash must avoid that word

ts: 2026-10-01T19:44:00Z
commit: 36e0621
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: `ledger_check` treats the literal `summarize_e7` as the marker that an entry cites E7 figures (`MANIFEST_MARKER`, entries >= 0024) and fails the ledger if such an entry has no `e7-manifest-sha256:` line. The corrective entry discusses 0044's E7 REPORT hash without citing any E7 figure; naming the summarizer would have made `ledger_check` refuse the append. The draft asserts the word is absent and refers to the hash by its `summary.json` key instead.
basis: at 36e0621, ~19:44Z: `grep -n -E "MANIFEST_MARKER\s*=|MANIFEST_CITED_FROM\s*=" src/linear_ceiling/ledger_check.py` printed `75:MANIFEST_CITED_FROM = 24` and `76:MANIFEST_MARKER = "summarize_e7"`; the in-memory candidate built by `docs/drafts/append_0045.py` passed `check()` with `[]` only once the word was absent. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: grep -n 'MANIFEST_MARKER = ' src/linear_ceiling/ledger_check.py   # expect `"summarize_e7"`
