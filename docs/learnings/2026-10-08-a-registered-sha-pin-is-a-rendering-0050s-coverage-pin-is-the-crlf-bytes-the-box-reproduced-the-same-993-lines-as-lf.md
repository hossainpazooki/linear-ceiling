# A registered sha pin is a rendering: 0050's coverage pin is the CRLF bytes; the box reproduced the same 993 lines as LF and the exact-match gate refused

ts: 2026-10-08T01:36:00Z
commit: 8696e83
session: llama-long-cell-0051-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: Entry 0050 pins `results/e9fl/align/coverage.json` at sha256 `16121e677b97…`. That file was written on Windows in
text mode and carries 992 CRs. The pod's `e9 --align-only` wrote the identical JSON (parsed-equal: all 68 alignment
records, run order, keep subset, counts; byte diff after CR normalisation: 0 of 993 lines) as LF, sha256
`9f10092b6238…`, and the launcher's "box coverage sha = home sha" gate refused — the second refused launch of the sitting.
The short cell had matched byte-for-byte on 09-19 only because that home file happened to be LF. The relaunch passed
`COVERAGE_SHA256` as the LF rendering; entry 0051 states both renderings beside the pin, derived from the bytes. Rules:
(1) a sha pinned in a registration is the sha of ONE rendering — write registered JSON with `newline="\n"` (as
`ledger_check` already does for the ledger) so the pin is platform-neutral; (2) a gate that compares shas across
platforms compares CR-normalised bytes or states which rendering it expects; (3) when a pin and a reproduction differ,
diff the parsed content and the bytes before touching either — here the content was never in question.
basis: runbook `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6 17:27–17:31 entries (992 CRs, 993 lines, 0 differing);
  `results/e9fl/logs/box/sitting_b.evidence/versions.txt` on the Mac mirror (`coverage_sha256=9f10092b…`); `append_0051.py`
  derives both shas and asserts each against the ledger and the evidence.
re-verify: .venv-cb/Scripts/python.exe -c "import hashlib;b=open('results/e9fl/align/coverage.json','rb').read();lf=b.replace(b'\r\n',b'\n');print(b.count(b'\r'),hashlib.sha256(lf.replace(b'\n',b'\r\n')).hexdigest()[:12],hashlib.sha256(lf).hexdigest()[:12])"   # 992 16121e677b97 9f10092b6238
