"""E9-long R2 probe on the rented card, NOT the pinned pipeline and NOT a result: peak CUDA memory of the PINNED
`load_model(model_id, rope_scaling=[e9.rope])` forward (fp32, sdpa_repeat_kv, use_cache, logits_to_keep=1 as
dump_kv does) over a T ladder ending at the longest included |S| (80,111), for both models of the pair. Synthetic
token ids. Writes nothing under data/ or results/. Each T is its own attempt; an OOM is a row, not a halt.
One JSON line per row; the T = 80,111 target row is the measured peak the runbook and entry 0036 cite.

usage (box, upstream venv):  ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py [T,T,...]
"""
import json
import sys
import time
import tomllib
from pathlib import Path

import torch

sys.path.insert(0, str(Path.home() / "kv-transfer-replication"))
from kvt.models import load_model  # noqa: E402
from kvt.pairs import PAIRS  # noqa: E402

cfg = tomllib.loads((Path.home() / "linear-ceiling" / "config" / "e9l.toml").read_text(encoding="utf-8"))["e9"]
pair = PAIRS[cfg["pair"]]
rope = dict(cfg["rope"])
ladder = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else "32768,65536,80111".split(","))]
free, total = torch.cuda.mem_get_info()
print(json.dumps({"card": torch.cuda.get_device_name(0), "total_GiB": round(total / 2**30, 2),
                  "free_GiB": round(free / 2**30, 2), "torch": torch.__version__, "rope": rope}), flush=True)
for which in ("target", "source"):
    mid = getattr(pair, which)
    m = load_model(mid, rope_scaling=rope)
    w = torch.cuda.memory_allocated() / 2**30
    print(json.dumps({"model": mid, "attn": m.config._attn_implementation, "weights_GiB": round(w, 2),
                      "rope_parameters": {k: (v if isinstance(v, (int, float, str)) else str(v))
                                          for k, v in dict(getattr(m.config, "rope_parameters", {}) or {}).items()}}), flush=True)
    for T in ladder:
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
        ids = torch.randint(100, 20000, (1, T), device="cuda")
        t0 = time.time()
        row = {"model": mid, "T": T}
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
        if not row["ok"]:
            break
    del m; torch.cuda.empty_cache()
print("PROBE_E9L_DONE", flush=True)
