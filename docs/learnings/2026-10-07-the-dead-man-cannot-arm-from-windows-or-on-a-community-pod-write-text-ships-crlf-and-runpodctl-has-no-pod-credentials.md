# The dead-man cannot arm from Windows or on this community pod: `write_text` ships CRLF, and the pod's `runpodctl` has no pod-scoped credentials — the home watchdog is the only net

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `cmd_arm_deadman` writes the on-pod script with `Path.write_text(DEAD_MAN)`; on Windows that is text mode, so the
shipped file has CRLF and the pod answers `/usr/bin/env: 'bash\r'` — from the LF clone too, since the bug is the write,
not the checkout. Stripping `\r` on the pod gets the script running, but on this community A100 pod `runpodctl get pod`
fails (no pod-scoped credentials), so the script REFUSES to arm by design. Both failures are loud and the tool says
"the home watchdog is the ONLY net"; the operational rule is to start `rp.py watchdog --exp <exp>` the moment `up`
returns and keep the machine awake, and not to count on the TTL backstop on community pods.
basis: 2026-10-06 23:44:30Z and 23:45:00Z `arm-deadman` (CRLF tree and LF clone): identical `'bash\r'` error; 23:46Z after
  `sed -i 's/\r$//' /workspace/deadman.sh`: `dead-man: REFUSING to arm -- 'runpodctl get pod mvwb1quo5c2hi1' failed`.
  Watchdog ran 23:45–01:35Z (`sitting kill $6.95, account kill $9.00, TTL 5.0h, warn $4.17`) and stood down on `pods 0`.
re-verify: grep -n "local.write_text(DEAD_MAN)" tools/runpod/rp.py   # one hit: the text-mode write (newline="\n" would fix the CRLF half)
