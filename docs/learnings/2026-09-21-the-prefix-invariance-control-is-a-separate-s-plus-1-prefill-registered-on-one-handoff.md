# The prefix-invariance control is a separate S+1 prefill, registered on one handoff, added because the identity control cannot fail

ts: 2026-09-21T02:38:18Z
commit: 3d2fbb14d3919cd2e798f4ffbe5132506cef1c7b
session: carryover-iclr-pickup-drift-wrapup (e7805827; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\e7805827-47f9-400a-a107-71d2eeb94fb2.jsonl)
status: refuted-assumption
fact: Three attacks drafted against 0032's second refutation lead (the exactly-zero prefix-invariance control) assumed
the record was silent on how the control works: that it might score the same tensors twice, that it might share a code
path with the pipeline-identity control, and that it was unknown how many handoffs it ran on. Entry 0025 answers all
three. The identity control "loads one dump twice, so its zero is the scorer's arithmetic and cannot fail on the box";
prefix invariance was ADDED for that reason, is a separate receiver prefill of S followed by R's first token scored
against the S dump at pairs (p, p), and runs "on the same first included handoff" only. An exact zero is what causal
attention predicts on one kernel. The live attack is whether the check CAN fail (a planted violation), not why it
reads zero. Read the registering entry before drafting an attack on a control.
basis: at 3d2fbb1, 2026-09-21T02:38:18Z, `sed -n 1483,1486p ledger/ledger.md` printed: "**Prefix-invariance control
  (review finding 3; HALTS).** 0023's pipeline-identity control scores the receiver's dump of `S` against itself: the
  scorer loads one dump twice, so its zero is the scorer's arithmetic and cannot fail on the box. ... Added: on the same
  first included handoff, the receiver prefills `S` followed by **R's first token**". The three rows are R10, R11 and
  R12 of `docs/reviews/refutation-0025-0029-rows.csv` (committed 3d2fbb1), now marked answered by the record.
re-verify: sed -n 1483,1488p ledger/ledger.md   # expect: "loads one dump twice ... cannot fail on the box"; "Added: on the same first included handoff ... R's first token"; "Causal attention makes them equal up to kernel arithmetic"
