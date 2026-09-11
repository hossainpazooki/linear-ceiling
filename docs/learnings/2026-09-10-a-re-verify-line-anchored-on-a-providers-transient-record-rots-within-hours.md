# A `re-verify:` line anchored on a cloud provider's transient record rots within hours: three hours after termination the instance query returns `None`, so a pick-up reads the claim as unverifiable rather than true

kills: (nothing)
ts: 2026-09-10T04:33:52Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: e9l-aws-run (018fwd195AS7uS2tvJdgSoYP)
status: verified
fact: The committed brief `docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md` proves R7 step 6
with `aws ec2 describe-instances --instance-ids i-0eafae594ebe8c291 --query '…State.Name'` -> `terminated`. Run
verbatim about three hours after the termination it prints `None`: EC2 drops terminated instances from
`describe-instances` shortly after they are reaped, so the line that was the proof becomes indistinguishable from
a typo'd instance id. The claim is still true and still checkable — but only through anchors that persist: the
runbook's recorded read-back at 01:35:36Z, and the DURABLE NEGATIVE form
`--filters Name=instance-id,Values=<id> --query 'length(Reservations)'`, which returns 0 for the terminated
instance and 1 for an instance that still exists in any state (positive control run against the account's
surviving `t3.micro`), so it can tell absence from presence rather than only failing to find something. Rule for
writing a brief: anchor `re-verify:` on an artifact under our own control (a committed file, a pulled log, a
hash), and where the fact genuinely IS a third party's state, use the form whose answer stays stable after the
provider forgets the record.
basis: at 2026-09-10T04:33:52Z, the brief's own line
  `aws ec2 describe-instances --profile kv-platform-admin --region us-east-1 --instance-ids i-0eafae594ebe8c291
  --query 'Reservations[0].Instances[0].State.Name' --output text` -> `None` (exit 0); the same account's
  `… --filters Name=instance-id,Values=i-0eafae594ebe8c291 --query 'length(Reservations)'` -> `0` while
  `Values=i-0785c090815238989` (a stopped `t3.micro` that still exists) -> `1`; the durable record of the
  original read-back is `docs/2026-09-10-e9l-gpu-runbook.md`, which carries `01:35:36Z` twice.
re-verify: aws ec2 describe-instances --profile kv-platform-admin --region us-east-1 --filters Name=instance-id,Values=i-0eafae594ebe8c291 --query 'length(Reservations)' --output text   # 0 = gone for good; the same query on a live id returns 1
