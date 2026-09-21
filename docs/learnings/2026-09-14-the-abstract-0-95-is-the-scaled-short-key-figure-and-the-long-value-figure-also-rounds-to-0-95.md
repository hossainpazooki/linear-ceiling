# The manuscript abstract's cross-model 0.95 is 0038's scaled-short KEY figure (0.9500); 0036's long VALUE figure (0.9456) also rounds to 0.95, so a two-decimal macro cannot show which column it came from

kills: (nothing)
ts: 2026-09-14T09:27:53.194Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: Entry 0038 records the scaled-short cross arm as f*(τ_K) 0.9500 and f*(τ_V) 0.9215 (line 2345). Entry 0036 records the
long cross arm's f*(τ_V) as 0.9456 (line 2215). Both 0.9500 and 0.9456 print as 0.95 at two decimals, and a reviewer of the
2026-09-14 manuscript suspected the abstract's `\fStarCrossScaledShortTwo{0.95}` was the long value figure read as a key
figure. It is the key figure. Abstract-precision macros should name the four-decimal source value, the entry and the
read-out in their comment, or the swap is undetectable from the source.
basis: `grep -n "f\*(τ_K) 0.9500" ledger/ledger.md` printed `2345:Cross arm (the n = 50 k = 1 mapper): f*(τ_K) 0.9500 (p10
  0.8957, p90 0.9782), f*(τ_V) 0.9215 (p10 0.8877, p90 0.9519)`; `grep -n "f\*(τ_V) = 0.9456" ledger/ledger.md` printed
  `2215:= 0.9640 (p10 0.9043, p90 0.9904) and f*(τ_V) = 0.9456 (p10 0.9023, p90 0.9863)`.
re-verify: grep -n "f\*(τ_K) 0.9500 (p10 0.8957" ledger/ledger.md && grep -n "f\*(τ_V) = 0.9456" ledger/ledger.md   # line 2345, then line 2215
