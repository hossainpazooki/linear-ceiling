# Entry 0042 does not carry the "not one matched token exceeds tau_K" sentence; only 0029 and 0036 do, and 0038/0044 already draw the distinction

ts: 2026-10-01T19:42:00Z
commit: 36e0621
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: refuted-assumption
fact: The plan and the 09-14 audit list 0029 / 0036 / 0042 as the entries stating the HOLDS reading as "not one matched token exceeds tau_K". On the ledger the sentence appears in exactly two entries, 0029 (line 1788) and 0036 (line 2209); 0042's only `exceeds` line is its rule statement. 0038 (line 2342) and 0044 (line 2962) already state that f* is the mean-repair statistic and not a per-token claim. The corrective entry therefore corrects two sentences and cites two entries, not three and none.
basis: at 36e0621 (ledger identical through 20a4e71), ~19:42Z: `grep -n -i -E "not one matched token|single matched token|..." ledger/ledger.md` printed lines 1788, 2209 and 2961 only (2961 is 0044 quoting the phrase to deny it); `awk 'NR>=2643 && NR<=2789' ledger/ledger.md | grep -i -E "single|not one|exceed"` printed only line 2658 `needs recompute when it exceeds **tau_K = 0.2861**`. (ts reconstructed from the tool sequence to within a few minutes, anchored on the 18:02Z `date` call, the 19:12Z PR #6 comment and the 19:28Z / 19:31Z / 19:46Z pushes.)
re-verify: git show 20a4e71:ledger/ledger.md | grep -n 'has a single matched token' | cut -d: -f1 | tr '\n' ' '   # expect `1788 2209 ` and nothing from 0042's block (2643-2788)
