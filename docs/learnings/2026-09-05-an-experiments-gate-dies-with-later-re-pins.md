# An experiment's gate becomes unrunnable once later re-pins touch its invoked paths; the record stands, the gate does not

kills: (nothing)
ts: 2026-09-05T02:19:55Z
commit: 31a5f692e85298eb32a8f39fe2a71e1ce5ef2542
session: qwen-kv-cache-oom-debug (8e4ab089-ff2e-43bc-9d6a-4da8ea00ce04)
status: verified
fact: upstream_gate.check_upstream passes only if the recorded pin is an ancestor of the upstream
HEAD AND every path the experiment invokes is byte-identical between pin and HEAD. E8's pin is
71df4504 (entry 0016); the 0019, 0023, 0026 (and now 0030) re-pins each changed scripts/dump_kv.py,
scripts/score_mapper.py or kvt/, so `e8 --check` and `summarize_e8` on results/e8 refuse by drift
and will keep refusing: 0020's figures can no longer be re-summarized in place, only re-derived
under a new pin as a new entry (which is what 0030/0031 do, in results/e8a). The design choice
"an older experiment's pin survives a newer one's re-pin" is true for the RECORD (the pin and the
fingerprints are on the ledger) and false for the GATE (the bytes it wants no longer exist at HEAD).
Either re-pin every live experiment on each upstream change, or accept that a closed experiment's
summarizer is frozen with its verdict and say so in the entry that moves the pin.
basis: `.venv/Scripts/python.exe -m linear_ceiling.e8 --check` at 31a5f69 with a clean ledger printed
  "E8 REFUSED: upstream paths ('scripts/dump_kv.py', 'scripts/score_mapper.py', 'kvt') changed between the pin
  71df45043a79 and HEAD; the invoked tools are not the pinned bytes" (captured 2026-09-04 ~20:50Z, pre-dates this
  entry's timestamp; at 02:19:55Z the same command fires the earlier "ledger not committed" check first because
  0030 is appended and uncommitted). Recorded as a known state in entry 0030.
re-verify: .venv/Scripts/python.exe -m linear_ceiling.e8 --check   # on a committed ledger: refuses with "changed between the pin 71df45043a79 and HEAD"
