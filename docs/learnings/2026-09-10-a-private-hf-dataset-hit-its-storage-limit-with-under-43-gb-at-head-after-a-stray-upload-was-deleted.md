# A private HF dataset hit the storage limit with 42.61 GB at head after a stray upload was deleted from it; the quota risk the commit-rate entry demoted did bite

ts: 2026-09-10T18:23:02Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: lcfm-sprint-e9l-review (9c42735d)
status: suspected
fact: After the 03:47Z commit-rate stop, the E9-long push stopped on `Private repository storage limit reached` twice more,
at 16:50Z and 18:15Z. The 03:47Z entry's `kills:` of the free-tier entry therefore held for that attempt only: the
quota risk it demoted did materialize later. At 18:15Z the operator reported this dataset as the account's only private
one. After the refusal its head held the 595 staging files plus `.gitattributes`, 42.61 GB, and the stray upload's
18,986 files were already deleted from the head. So the Hub counted something besides the head's bytes against the
100 GB limit. The likely component is the deleted strays still in history, which count until `super_squash_history`
runs. That is not isolated from a second candidate: chunks uploaded through hf_xet before the commit that was then
refused. The operator squashed at 18:20:30Z and made the dataset public; the remaining 129 files then went up and the
backup verified at 18:28:26Z. The operational reading is that a stray upload into a private dataset keeps costing quota
after it is deleted. `super_squash_history` is the irreversible remedy, and public visibility removes the private cap.
basis: `~/dev/hf-staging/logs/linear-ceiling-e9l-2026-09-10.20260910T164949Z.push.log` carries the phrase once, and
  `…20260910T181427Z.push.log` seven times, ending `[tree] failed with exit 1, not a rate limit; stopping` at 18:15:25Z
  after `723/723 files checked, 567/567 uploaded (472MB transferred), 574 committed in 2 commit(s)` (both counts
  re-read with awk 2026-09-14T09:25Z). Tokenless listing at 2026-09-10T18:23Z: `commit: 367a7d2d 2026-09-10
  18:20:30+00:00 'R8: squash history to drop the stray upload'`; `remote 596 | local 724 | not in staging 0 | size
  mismatches 0`; `head bytes: 42.61 GB`. The operator in session: "it shows 90gb in the repo and is the only private
  dataset", then "it's 95.8 at this point". The verifier line `BACKUP VERIFIED` at 2026-09-10T18:28:26Z was pasted by
  the operator.
re-verify: awk '/Private repository storage limit reached/{n++} END{print n+0}' ~/dev/hf-staging/logs/linear-ceiling-e9l-2026-09-10.20260910T181427Z.push.log   # expect 7 (the 164949Z log gives 1)
