"""Scratch: validate the CANDIDATE kvt/models.py (uploaded beside this file, not the pinned checkout).
Loads Qwen3-1.7B through candidate.load_model and checks (a) K/V bit-identical to the monkeypatch
path measured by probe.py, (b) peak memory at the two longest included handoff lengths with the
candidate dump call (use_cache=True, logits_to_keep=1). Writes nothing under results/."""
import importlib.util, time, torch
from transformers import AutoModelForCausalLM
from transformers.integrations import sdpa_attention as _sa

spec = importlib.util.spec_from_file_location("cand", "/home/jupyter-rrhs-fe3a-xl/probe/kvt_models_candidate.py")
cand = importlib.util.module_from_spec(spec); spec.loader.exec_module(cand)

m_c = cand.load_model("Qwen/Qwen3-1.7B")
print("candidate attn impl:", m_c.config._attn_implementation, "| device", next(m_c.parameters()).device, flush=True)
m_s = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-1.7B", dtype=torch.float32).cuda().eval()


def kv(out):
    pkv = out.past_key_values
    return [(pkv.layers[l].keys, pkv.layers[l].values) for l in range(28)]


torch.manual_seed(0)
ids = torch.randint(0, 150000, (1, 1024), device="cuda")
with torch.no_grad():
    oc = m_c(input_ids=ids, use_cache=True, logits_to_keep=1)
    _orig = _sa.use_gqa_in_sdpa; _sa.use_gqa_in_sdpa = lambda *a, **k: False
    om = m_s(input_ids=ids, use_cache=True)
    _sa.use_gqa_in_sdpa = _orig
    os_ = m_s(input_ids=ids, use_cache=True)
same = all(torch.equal(a[0], b[0]) and torch.equal(a[1], b[1]) for a, b in zip(kv(oc), kv(om)))
print("T=1024 candidate K/V bit-identical to probe.py's nogqa path:", same, flush=True)
dk = max((a[0] - b[0]).abs().max().item() for a, b in zip(kv(oc), kv(os_)))
dv = max((a[1] - b[1]).abs().max().item() for a, b in zip(kv(oc), kv(os_)))
print(f"T=1024 candidate vs pinned math path: max|dK|={dk:.3e} max|dV|={dv:.3e}", flush=True)
print("candidate logits shape:", tuple(oc.logits.shape), flush=True)
del oc, om, os_, m_s; torch.cuda.empty_cache()

for T in (29391, 32123):
    ids = torch.randint(0, 150000, (1, T), device="cuda")
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t = time.time()
    with torch.no_grad():
        out = m_c(input_ids=ids, use_cache=True, logits_to_keep=1)
    torch.cuda.synchronize()
    print(f"T={T} candidate dump call: peak {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB  {time.time() - t:.1f}s", flush=True)
    del out
print("PROBE2-DONE", flush=True)
