"""Scratch diagnostic, NOT the pinned pipeline. Measures peak CUDA memory of the pinned forward
(model(input_ids, use_cache=True), float32) vs. two candidate upstream changes, and the K/V
difference they introduce. Writes nothing under results/."""
import time, torch
from transformers import AutoModelForCausalLM
from transformers.integrations import sdpa_attention as _sa
_orig_gqa = _sa.use_gqa_in_sdpa


class nogqa:
    """force repeat_kv instead of enable_gqa so the mem-efficient SDPA kernel is eligible in f32"""
    def __enter__(self): _sa.use_gqa_in_sdpa = lambda *a, **k: False
    def __exit__(self, *a): _sa.use_gqa_in_sdpa = _orig_gqa

m = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-1.7B", dtype=torch.float32).cuda().eval()
print("attn impl:", m.config._attn_implementation, "| torch", torch.__version__, flush=True)
print("weights GiB:", round(torch.cuda.memory_allocated() / 2**30, 2), flush=True)


def run(ids, _nogqa=False, **kw):
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t = time.time()
    with torch.no_grad():
        if _nogqa:
            with nogqa():
                out = m(input_ids=ids, use_cache=True, **kw)
        else:
            out = m(input_ids=ids, use_cache=True, **kw)
    torch.cuda.synchronize()
    return out, torch.cuda.max_memory_allocated() / 2**30, time.time() - t


def kv(out):
    pkv = out.past_key_values
    ks, vs = [], []
    for l in range(m.config.num_hidden_layers):
        if hasattr(pkv, "layers"):
            ks.append(pkv.layers[l].keys); vs.append(pkv.layers[l].values)
        else:
            k, v = pkv[l]; ks.append(k); vs.append(v)
    return ks, vs


# 1. K/V agreement between paths on a short sequence where the pinned path runs
torch.manual_seed(0)
ids = torch.randint(0, 150000, (1, 1024), device="cuda")
o0, p0, _ = run(ids)
o1, p1, _ = run(ids, attention_mask=torch.ones_like(ids))
o2, p2, _ = run(ids, _nogqa=True)
o3, p3, _ = run(ids, _nogqa=True, logits_to_keep=1)
k0, v0 = kv(o0); k1, v1 = kv(o1); k2, v2 = kv(o2); k3, v3 = kv(o3)
sk = max(a.abs().max().item() for a in k0); sv = max(a.abs().max().item() for a in v0)
for name, (ka, va) in [("mask", (k1, v1)), ("nogqa", (k2, v2))]:
    dk = max((a - b).abs().max().item() for a, b in zip(k0, ka)); dv = max((a - b).abs().max().item() for a, b in zip(v0, va))
    print(f"T=1024 K/V pinned-vs-{name}: max|dK|={dk:.3e} (scale {sk:.2f})  max|dV|={dv:.3e} (scale {sv:.2f})", flush=True)
print("nogqa vs nogqa+ltk1 K/V bit-identical:", all(torch.equal(a, b) for a, b in zip(k2, k3)) and all(torch.equal(a, b) for a, b in zip(v2, v3)), flush=True)
print(f"T=1024 peaks: pinned {p0:.2f} mask {p1:.2f} nogqa {p2:.2f} nogqa+ltk1 {p3:.2f} GiB", flush=True)
del o0, o1, o2, o3, k0, v0, k1, v1, k2, v2, k3, v3

# 2. peak memory scaling
for T in (4096, 8192, 16384, 29391, 32123):
    ids = torch.randint(0, 150000, (1, T), device="cuda")
    for name, kw in [("pinned", {}), ("mask", {"attention_mask": torch.ones_like(ids)}),
                     ("nogqa", {"_nogqa": True}), ("nogqa+ltk1", {"_nogqa": True, "logits_to_keep": 1})]:
        if name in ("pinned", "mask") and T > 16384:
            print(T, name, "skipped (known OOM: attn matrix alone", round(16 * T * T * 4 / 2**30, 1), "GiB)", flush=True); continue
        try:
            out, p, t = run(ids, **kw); del out
            print(f"T={T} {name:10s} peak {p:6.2f} GiB  {t:5.1f}s", flush=True)
        except torch.OutOfMemoryError as e:
            print(f"T={T} {name:10s} OOM: {str(e)[:80]}", flush=True)
        torch.cuda.empty_cache()
print("PROBE-DONE", flush=True)
