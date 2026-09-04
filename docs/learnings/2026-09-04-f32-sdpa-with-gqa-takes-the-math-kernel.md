# In float32, transformers' SDPA with grouped-query heads takes the math kernel: the budget is the attention scores, not the logits

kills: 2026-09-02-the-gpu-budget-is-the-logits-not-the-kv (its arithmetic was right and its conclusion wrong: peak was not 35 GB and the whole card was not enough)
ts: 2026-09-04T17:04:53Z
commit: d965e2290371a6067df7f1232758fdf28b592333
session: qwen-kv-cache-oom-debug (8e4ab089-ff2e-43bc-9d6a-4da8ea00ce04)
status: verified (measured on the box; entry 0026 carries the table)
fact: The 09-02 entry budgeted weights + KV + full-vocab logits (≈ 35 GB) and concluded an exclusive
40 GB card fits. On the Algoverse H100 MIG 3g.40gb (39.5 GiB) the pinned run OOMed at the first
included handoff (|S| = 29,391) with a 51.49 GiB request inside scaled_dot_product_attention:
16 heads × 29,391² × 4 B, the float32 attention scores. transformers' sdpa integration passes
enable_gqa=True whenever no mask is present; in float32 flash is ineligible and the memory-efficient
kernel does not accept enable_gqa, so PyTorch silently takes the math kernel and materializes
[heads, T, T]. That term is quadratic and dominates everything the 09-02 entry summed; at 32,123
tokens it is 61.5 GiB alone, so no single card runs the pin. An explicit all-ones mask does not help
(it is dropped before SDPA; K/V bit-identical). Expanding KV heads with repeat_kv instead of
enable_gqa makes the memory-efficient kernel eligible: peak 31.95 GiB at 32,123 (16.74 GiB with
logits_to_keep=1), K/V within float32 rounding of the math kernel (max |dK| 9.2e-4 on a scale of 423).
Corollary: a memory budget for an HF forward is not complete until the SDPA backend is known; in
float32 with GQA assume the math kernel unless measured, and measure with
torch.cuda.max_memory_allocated at the real sequence length before requesting hardware.
basis: e9.log on the box 2026-09-04 16:43 UTC (the OOM message); transformers 5.16.1
  integrations/sdpa_attention.py::use_gqa_in_sdpa (returns True when attention_mask is None);
  scratch probe on the slice, table in ledger entry 0026; candidate kvt/models.py validated there
  (15.67 GiB at 29,391; 16.52 GiB at 32,123).
re-verify: .venv/Scripts/python.exe -c "print(round(16*29391**2*4/2**30,2))" prints 51.49; grep -n "enable_gqa" ../kv-transfer-replication/.venv/Lib/site-packages/transformers/integrations/sdpa_attention.py; grep -n "sdpa_repeat_kv\|logits_to_keep" ../kv-transfer-replication/kvt/models.py ../kv-transfer-replication/kvt/data.py
