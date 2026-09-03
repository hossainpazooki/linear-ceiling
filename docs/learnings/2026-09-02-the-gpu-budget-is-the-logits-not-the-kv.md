# At long context the GPU memory budget is the logits, not the KV cache

kills: (nothing)
ts: 2026-09-02T22:46:00Z
commit: 8b6cced3a1419bbe5d14e84dda18fcb34b0fc777
session: linear-ceiling-gpu-preflight (8e4ab089-ff2e-43bc-9d6a-4da8ea00ce04)
status: verified (arithmetic from code and config; not measured on a GPU)
fact: The LCFM GPU plan sized E9 on the KV cache alone ("Qwen3-1.7B at 32k context KV ≈ 3.7 GB
— fits even shared", assuming bf16) and concluded a 20 GB share of an A100 was enough. The
upstream instrument does neither of the things that sizing assumed: `kvt/models.py` loads every
model in float32 (the CPU replication's precision), and `kvt/data.py::dump_kv` obtains the KV
through a CausalLM forward, `model(input_ids=ids, use_cache=True)`, which materializes logits for
every position over the full vocabulary. At the longest included handoff (|S| = 32,123 tokens,
Qwen3 vocab 151,936) the logits alone are 32,123 × 151,936 × 4 B ≈ 19.5 GB — 2.6× the f32 KV cache
(28 layers × 8 kv heads × 128 × K+V × 32,123 × 4 B ≈ 7.4 GB) and 2.8× the 1.7B weights (≈ 6.9 GB).
Peak ≈ 35 GB: fits one exclusive 40 GB card, not a share, and not a 24 GB card. Corollary: any
plan that puts a HF `AutoModelForCausalLM` forward at long context on a GPU must budget
`seq_len × vocab × bytes` for logits unless the call passes `logits_to_keep` (or uses the base
model), and the check is a grep of the loader and the forward call, not the KV formula.
basis: `kvt/models.py` line 11 `AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)`;
  `kvt/data.py` line 42 `out = model(input_ids=ids, use_cache=True)` (upstream at `36d73b3`);
  `config.json` of `Qwen/Qwen3-1.7B` in the local HF cache: 28 layers, 8 kv heads, head_dim 128,
  hidden 2048; vocab 151,936 from the tokenizer; |S| max 32,123 from the read-only E9 alignment
  recon over the real 68 handoffs run 2026-09-02 (25 included at the 32,768 cap).
re-verify: grep -n "float32" ../kv-transfer-replication/kvt/models.py && grep -n "use_cache=True" ../kv-transfer-replication/kvt/data.py && .venv/Scripts/python.exe -c "print(round(32123*151936*4/1e9,1), round(28*8*128*2*32123*4/1e9,1))"
