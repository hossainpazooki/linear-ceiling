# RunPod's "no longer any instances available" was the create filters, not stock: the Llama-sized RAM/vCPU/CUDA floors excluded every host that the price listing counted

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `rp.py up` passes `minMemoryInGb`, `minVcpuCount`, `containerDiskInGb` and `allowedCudaVersions` to the create
mutation; `rp.py price` applies only the RAM/vCPU floors. The defaults (RAM ≥ 48 GB, 8 vCPU, CUDA {12.8, 12.9, 13.0})
were sized for loading fp32 Llama-8B through host memory and exclude hosts whose driver reports CUDA 13.1+. Three creates
on two 80 GB rows the listing showed in stock were refused with the same message; the fourth, with RAM ≥ 24 GB, 4 vCPU
and CUDA 12.8–13.2 (none a registered quantity for 0047, whose model is 7 GB in fp32), was created in one second on the
first row tried. The 09-19 procedure already records this class of refusal; the floors it widened then were disk and
CUDA, and this sitting shows RAM/vCPU and the CUDA ceiling matter too.
basis: 2026-10-06 23:39:49Z, 23:40:32Z (A100 PCIe community $1.19) and 23:42:34Z (A100 SXM community $1.39), default
  filters: `rp REFUSED: RunPod API error: There are no longer any instances available with the requested specifications`;
  23:43:10Z with `--min-ram 24 --min-vcpu 4 --cuda 12.8 12.9 13.0 13.1 13.2`: `pod mvwb1quo5c2hi1 created at $1.39/h`.
  The host allocated had 1,007 GB RAM and 256 vCPU, driver 595.71.05 (CUDA 13.x).
re-verify: grep -n -E '"--min-ram".*default=48|"--cuda".*default=\["12.8", "12.9", "13.0"\]' tools/runpod/rp.py   # the two defaults that filtered the hosts out (two hits)
