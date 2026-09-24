"""E9-long R2 probe on the rented card, NOT the pinned pipeline and NOT a result: peak CUDA memory of the PINNED
`load_model(model_id, rope_scaling=[e9.rope] or None)` forward (fp32, sdpa_repeat_kv, use_cache, logits_to_keep=1 as
dump_kv does) over a T ladder ending at the run's longest prefill, for both models of the pair. Synthetic
token ids. Writes nothing under data/ or results/. Each T is its own attempt; an OOM is a row, not a halt.
One JSON line per row; the top rung's row is the measured peak the runbook and entry 0036 cite.

The config decides the RoPE, and a config may legitimately carry none. `[e9.rope]` is present only when the
receiver's window must be EXTENDED to reach the cap (E9-long on Qwen3: YaRN 2.5 over a 32,768 native window);
a natively long receiver reaches the same cap unscaled and its config carries no `[e9.rope]` at all, which
`config.py` requires and this probe must not treat as an error. `rope = None` is exactly what
`kvt.models.load_model` takes for the unscaled path (`if rope_scaling:`), so the probe measures the same
forward the driver will run in either case -- never a scaled forward standing in for a native one.

The TOP RUNG is the longest prefill the run will actually attempt, which is a fact about the run's own
handoffs under the pair's own tokenizer, not a constant: take it from `results/<exp>/align/coverage.json`
(the largest n_sender/n_receiver among the INCLUDED alignments) and pass it as MAX_S, or give the whole
ladder explicitly. With neither, the probe falls back to the config's `context_cap`, which bounds every
prefill by construction and so is the conservative choice -- but it is a bound, not the run's number, and
a launch decision should be made on the run's number.

usage (box, upstream venv):  ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py [T,T,...]
                             EXP=e9l MAX_S=80111 ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py
                             LADDER=32768,65536,80111 ... ~/probe_e9l.py        (same, whole ladder)
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

import os
EXP = os.environ.get("EXP", "e9l")
cfg = tomllib.loads((Path.home() / "linear-ceiling" / "config" / f"{EXP}.toml").read_text(encoding="utf-8"))["e9"]
pair = PAIRS[cfg["pair"]]
rope = dict(cfg.get("rope") or {}) or None       # None = the model's native RoPE; load_model's unscaled path
cap = int(cfg["handoffs"]["context_cap"])
if len(sys.argv) > 1 or os.environ.get("LADDER"):
    spec = sys.argv[1] if len(sys.argv) > 1 else os.environ["LADDER"]
    ladder, top_from = [int(x) for x in spec.split(",")], ("argv" if len(sys.argv) > 1 else "LADDER")
else:
    top = int(os.environ.get("MAX_S") or 0)
    top, top_from = (top, "MAX_S") if top else (cap, "context_cap (a BOUND, not the run's longest prefill)")
    ladder = [r for r in (32768, 65536) if r < top] + [top]
free, total = torch.cuda.mem_get_info()
print(json.dumps({"card": torch.cuda.get_device_name(0), "total_GiB": round(total / 2**30, 2),
                  "free_GiB": round(free / 2**30, 2), "torch": torch.__version__, "pair": pair.name,
                  "rope": rope, "context_cap": cap, "ladder": ladder, "top_rung_from": top_from}), flush=True)
for which in ("target", "source"):
    mid = getattr(pair, which)
    m = load_model(mid, rope_scaling=rope)
    w = torch.cuda.memory_allocated() / 2**30
    print(json.dumps({"model": mid, "attn": m.config._attn_implementation, "weights_GiB": round(w, 2),
                      "max_position_embeddings": int(m.config.max_position_embeddings),
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
