# The EC2 launcher set no CPU thread cap: 191 scorer threads on a 13.6-CPU cgroup quota halved E-TRUNC's throughput until capped at the quota

ts: 2026-10-08T23:41:00Z
commit: b33c6ce
session: e-trunc-0057-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The E9 driver's per-handoff time is dominated by the CPU-bound per-token scorer (`score_positions.py`), not the GPU
prefill (GPU 0 % between prefills). On the RunPod secure A100 pod of 2026-10-08 the container showed `nproc` 128 but
`/sys/fs/cgroup/cpu.max` read `1360000 100000` (13.6 CPUs); the scorer spawned 191 threads and `cpu.stat` recorded
`nr_throttled 34611` of `nr_periods 71474` (48 % of scheduler periods throttled). FULL ran 255–370 s per handoff for its
first 18 handoffs; after a drain-by-pid and `run.sh --resume` under `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB _NUM_THREADS=13`
the same handoff mix ran 130–150 s — E9-long's L40S rate — and the three later levels ran 102–185 s throughout.
`tools/runpod/sitting_b.sh` had derived exactly this cap from the cgroup quota since the 0048 sitting; `tools/ec2/run.sh`
(the multi-level launcher this sitting used) had none. Rules: (1) every launcher derives the thread cap from the cgroup
quota, never from `nproc`, and prints it; (2) when a run is slower than its record, read GPU utilisation, the hot
process's thread count and `cpu.stat` before blaming the card; (3) a mid-run cap change is a reduction-order change —
state the split (handoffs 1–19 vs 20–35 here) and let 0028's re-score tolerance judge it.
basis: runbook `docs/2026-10-04-e-trunc-gpu-runbook.md` §6 entries 16:36–18:27 (diagnosis: GPU 0 %, 191 threads, the
  `cpu.max` and `cpu.stat` readings), 18:30:48 (drain and relaunch), 18:39 (150 / 142 / 136 s); `tools/ec2/run.sh` as
  fixed in the close commit; `tools/runpod/sitting_b.sh` lines deriving `LC_THREADS`.
re-verify: grep -n "cpu.max\|LC_THREADS=" tools/ec2/run.sh tools/runpod/sitting_b.sh | head -6; grep -n "nr_throttled 34611\|191 threads" docs/2026-10-04-e-trunc-gpu-runbook.md | head -2
