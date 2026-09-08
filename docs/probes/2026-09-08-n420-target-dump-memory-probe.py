"""R2 probe, NOT the pinned pipeline: run the PINNED load_model + dump_kv on the first 2 sequences into /tmp and
print the peak CUDA memory at the real T=1024 path. Writes nothing under data/."""
import sys, time, shutil, numpy as np, torch
from pathlib import Path
sys.path.insert(0, str(Path.home() / "kv-transfer-replication"))
from kvt.data import dump_kv
from kvt.models import load_model
from kvt.pairs import PAIRS
pair = PAIRS["qwen3-0.6b-to-1.7b"]
seqs = np.load(Path.home() / "kv-transfer-replication/data/tokens/qwen3-0.6b-to-1.7b_n420_len1024_seed0.npy")
print("tokens shape", seqs.shape, seqs.dtype, flush=True)
m = load_model(pair.target)
print("model", pair.target, "attn", m.config._attn_implementation, "dtype", next(m.parameters()).dtype, "dev", next(m.parameters()).device, flush=True)
print("weights GiB", round(torch.cuda.memory_allocated() / 2**30, 2), flush=True)
out = Path("/tmp/probe_n420"); shutil.rmtree(out, ignore_errors=True)
torch.cuda.reset_peak_memory_stats(); t = time.time()
dump_kv(m, seqs[:2], 4, out)
torch.cuda.synchronize()
print("peak GiB", round(torch.cuda.max_memory_allocated() / 2**30, 2), "| 2 seqs in", round(time.time() - t, 1), "s", flush=True)
print("est full run s", round((time.time() - t) / 2 * 420), flush=True)
shutil.rmtree(out, ignore_errors=True); print("PROBE_DONE")
