# 0046's "full-cap KV < 3 GB" was off eightfold: fp32 KV per token is layers × KV heads × head dim × 8 bytes, and the 4B peaked at 39.7 GiB on an 80K-token sender

ts: 2026-10-07T06:46:00Z
commit: d4d48a1
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: Entry 0046 expects "an L40S 48 GB … (fp32 weights ≈ 16 GB for the 4B, full-cap KV < 3 GB)". The driver retains the
full causal KV in fp32 (`capture()` passes `past_key_values` back each 256-token chunk), so per token it holds
layers × KV heads × head dim × 4 B × 2 (K and V): Qwen3-4B 36 × 8 × 128 × 8 = 294,912 B, i.e. **22.5 GiB at the 81,920
cap**, not 3 GB. With 16.1 GB of fp32 weights and the SDPA chunk workspace, the measured peak on the longest sender was
**39.72 GiB** — under 5 GiB from a 48 GB card's usable memory, and an OOM on model 2 would have forced a restart on a
different card (the driver refuses to resume across GPUs). The sitting went on an 80 GB A100 on that arithmetic, before
renting; the entry's clause "a larger card if the probe says so" covers it, but the figures entry should state the card
and the peak, and the next registration should carry the per-token formula instead of a round number.
basis: `results/consolidation/a100/results/qwen4/report.json` `scores[*].peak_allocated_GiB` max 39.72 (the 80,111-token
  sender), bridge model 24.93, SmolLM3 22.96 (4 KV heads → 11.8 GiB cache); runbook `docs/2026-10-07-consolidation-runpod-runbook.md`
  §2 and §6; ledger 0046 line "full-cap KV < 3 GB" (`awk '/^### 0046/,/^### 0047/' ledger/ledger.md | grep -n "KV <"`).
re-verify: .venv/Scripts/python.exe -c "print(round(36*8*128*4*2*81920/2**30,1))"   # 22.5 (GiB of fp32 K+V for Qwen3-4B at the 81,920-token cap)
