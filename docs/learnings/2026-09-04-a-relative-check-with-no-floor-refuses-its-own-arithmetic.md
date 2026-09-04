# A per-square relative check with no absolute floor refuses float32 arithmetic it should accept; test the check on a matching platform before calling the record bad

kills: (nothing)
ts: 2026-09-04T20:35:17Z
commit: 0a19b56ee3bd4b45eca28f84a20cf6ded4dcd436
session: qwen-kv-cache-oom-debug (8e4ab089-ff2e-43bc-9d6a-4da8ea00ce04)
status: verified (entry 0028 table; docs/probes/2026-09-04-rescore-*.sh)
fact: summarize_e9 compared every per-token float32 square of the home re-score against the box
record with rtol=1e-5, atol=0 -- a constant written for a same-machine comparison -- and refused
the whole summary on 132 of 952,672 same-K squares of size ~1e-4 that differed by ~4e-8. The
verdict statistic was identical (f* unchanged, max token delta shift 4e-6) and the pre-existing
aggregate checks (layer-mean R^2 at 1e-6, per-head sums at 1e-5) passed with three orders of margin.
Re-scoring the same tensors on Linux with the box's torch build reproduced the same-model arrays
bit-for-bit; the cross arrays still differed, and changing only the THREAD COUNT on one machine
changed them by the same class (69%/48% of squares identical, <= 1.2e-3 relative), so that part is
reduction order in a float32 matmul, not the record. Two rules: (1) a check on individual float32
values needs either an absolute floor or a tolerance that admits thread-order effects, with the
tight check kept on the sums those values feed; (2) before loosening a check after seeing data --
which is post hoc by construction -- reproduce the disagreement on a matching platform and vary
the one suspected cause (threads) so the tolerance rests on a measured mechanism, not on the size
of the residual.
basis: results/e9/recheck/ (Windows), ~/wsl-recheck/ (WSL, torch 2.11.0+cu128, numpy 2.5.2);
  determinism log: 8 vs 1 thread; box vs WSL same_K eq=1.0000; entry 0028 in ledger/ledger.md.
re-verify: bash docs/probes/2026-09-04-rescore-determinism.sh (in the WSL, after the matching-platform script) prints "wsl1 vs wsl2 eq=1.0000" for every arm and "wsl1 vs wsl_t1 eq<1" for cross_K
