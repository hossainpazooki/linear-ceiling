"""E9-long R2 probe, NOT the pinned pipeline and NOT a result: peak CUDA memory of the PINNED load_model forward
(fp32, sdpa_repeat_kv, use_cache, logits_to_keep=1 as dump_kv does) on a MIG 1g.20gb slice, over a T ladder, for
both models of the pair. Synthetic token ids; RoPE scaling is irrelevant to memory. Writes nothing under data/ or
results/. Each T is its own attempt; an OOM is recorded as a row, not a halt. Output: one JSON line per row."""
import sys, time, json, torch
from pathlib import Path
sys.path.insert(0, str(Path.home() / "kv-transfer-replication"))
from kvt.models import load_model
from kvt.pairs import PAIRS
pair = PAIRS["qwen3-0.6b-to-1.7b"]
ladder = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else "4096,8192,16384,32768,40960,49152,65536,80111".split(","))]
free, total = torch.cuda.mem_get_info(); print(json.dumps({"slice_total_GiB": round(total / 2**30, 2), "free_GiB": round(free / 2**30, 2), "torch": torch.__version__}), flush=True)
for which in ("target", "source"):
    mid = getattr(pair, which); m = load_model(mid)
    w = torch.cuda.memory_allocated() / 2**30
    print(json.dumps({"model": mid, "attn": m.config._attn_implementation, "weights_GiB": round(w, 2)}), flush=True)
    for T in ladder:
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
        ids = torch.randint(100, 20000, (1, T), device="cuda"); t0 = time.time(); row = {"model": mid, "T": T}
        try:
            with torch.no_grad():
                out = m(input_ids=ids, use_cache=True, logits_to_keep=1)
            torch.cuda.synchronize()
            row.update(peak_GiB=round(torch.cuda.max_memory_allocated() / 2**30, 2), s=round(time.time() - t0, 1), ok=True)
            del out
        except torch.cuda.OutOfMemoryError as e:
            row.update(ok=False, oom=str(e).split(".")[0][:160], peak_GiB=round(torch.cuda.max_memory_allocated() / 2**30, 2))
        del ids; torch.cuda.empty_cache()
        print(json.dumps(row), flush=True)
        if not row["ok"]: break
    del m; torch.cuda.empty_cache()
print("PROBE_LONG_DONE", flush=True)
