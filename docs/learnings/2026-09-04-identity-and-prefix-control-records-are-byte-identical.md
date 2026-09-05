# The E9 identity and prefix-invariance control records are byte-identical; a control that returns exactly zero must be shown able to fail

kills: (nothing)
ts: 2026-09-04T18:23:37Z
commit: 0a19b56ee3bd4b45eca28f84a20cf6ded4dcd436
session: algoverse-gpu-run-session (8a0fb97e-0020-43aa-a9b2-9ae67eec2fe3)
status: verified
fact: On the box after the run, results/e9/controls/identity.tokens.npz and
results/e9/controls/prefix.tokens.npz had the same sha256 (c7a45346...), and the mirror copies match.
Entry 0029 records the prefix-invariance control at max centered per-token delta 0.000e+00 over
29,391 positions, i.e. the box reproduced the prefix under one extra token bit-for-bit, which is
what two all-zero arrays of the same shape serialize to. Entry 0025 introduced the prefix control
because the 0023 identity control (one dump loaded twice) cannot fail; if a causal mask plus
deterministic kernels makes the prefix control exactly zero by construction on this pipeline, it
tests kernel determinism rather than anything the statistic could get wrong. This entry records
the byte identity as a fact; whether the control can fail is the open question handed to the
refutation of 0025 to 0029.
basis: box listing 2026-09-04 18:23 UTC: `c7a45346e4966bafcd097b00cae82fe89b4196e2dc15df43da797708e6a4a5ee
  ./controls/identity.tokens.npz` and the same digest for `./controls/prefix.tokens.npz`; ledger 0029
  "Prefix invariance: max centered per-token δ 0.000e+00 over 29,391 positions".
re-verify: sha256sum results/e9/controls/identity.tokens.npz results/e9/controls/prefix.tokens.npz
