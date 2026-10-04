# Paired prompt interventions; shared inputs and scorer for Mac and later CUDA validation.
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys
import time

import numpy as np
import torch
import transformers
from transformers import AutoModel

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from linear_ceiling.e9_pertoken import f_star

parser = argparse.ArgumentParser()
parser.add_argument("--device", choices=["mps", "cpu", "cuda"], default="mps")
parser.add_argument("--config", type=Path, default=Path("results/seam-pilot/proximity_config.json"))
parser.add_argument("--check", action="store_true", help="Verify frozen inputs without loading a model")
parser.add_argument("--output")
args = parser.parse_args()
cfg_path = args.config
cfg_bytes = cfg_path.read_bytes()
sha = hashlib.sha256(cfg_bytes).hexdigest()
source = json.loads((ROOT / "source.json").read_text())
assert sha == source["config_sha256"], "Input differs from the frozen source artifact."
assert sha == cfg_path.with_suffix(".sha256").read_text().strip()
cfg = json.loads(cfg_bytes)
if args.check:
    print(json.dumps({"verified": True, "config_sha256": sha, "cases": len(cfg["cases"]), "model_revision": cfg["revision"]}))
    raise SystemExit(0)
out = Path(args.output or f"results/seam-pilot/{args.device}")
out.mkdir(parents=True, exist_ok=True)
assert not (out / "results.json").exists(), "Use a new output directory for another run."
torch.set_num_threads(4)
torch.manual_seed(cfg["seed"])
if args.device == "mps":
    torch.mps.set_per_process_memory_fraction(0.55)
if args.device == "cuda":
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
model = AutoModel.from_pretrained(cfg["model"], revision=cfg["revision"],
                                 dtype=torch.float32, attn_implementation=cfg["attention"],
                                 local_files_only=True).eval().to(args.device)
print("Loaded", cfg["model"], args.device, flush=True)
span = [0, 0]
capture = {"K": [], "V": []}
heads = model.config.num_key_value_heads
dim = model.config.head_dim

def hook(kind):
    def save(module, inputs, output):
        x = output.reshape(output.shape[0], output.shape[1], heads, dim)
        capture[kind].append(x[0, span[0]:span[1]].detach().clone())
    return save

handles = []
for layer in model.layers:
    handles.append(layer.self_attn.k_norm.register_forward_hook(hook("K")))
    handles.append(layer.self_attn.v_proj.register_forward_hook(hook("V")))

@torch.inference_mode()
def states(tokens, start, shift=0):
    span[:] = [start, start + cfg["block_tokens"]]
    capture["K"].clear()
    capture["V"].clear()
    ids = torch.tensor([tokens], dtype=torch.long, device=args.device)
    positions = torch.arange(shift, shift + len(tokens), device=args.device).unsqueeze(0)
    model(input_ids=ids, position_ids=positions, use_cache=False)
    result = {k: torch.stack(v).cpu().numpy() for k, v in capture.items()}
    capture["K"].clear()
    capture["V"].clear()
    return result

def compare(candidate, reference):
    result, arrays = {}, {}
    for kind in ["K", "V"]:
        ref = reference[kind].astype(np.float64)
        delta = candidate[kind].astype(np.float64) - ref
        variance = ((ref - ref.mean(axis=1, keepdims=True)) ** 2).sum(-1).mean(1)
        assert (variance > 0).all()
        normalized = (delta ** 2).sum(-1) / variance[:, None, :]
        token = normalized.mean(axis=(0, 2))
        result[kind] = {
            "mean_delta": float(token.mean()), "median_delta": float(np.median(token)),
            "p90_delta": float(np.quantile(token, .9)), "max_delta": float(token.max()),
            "raw_vector_mse": float((delta ** 2).sum(-1).mean()),
            "fstar": {str(t): f_star(token, t) for t in cfg["tolerances"]},
            "near_0_15_mean": float(token[:16].mean()),
            "far_64_plus_mean": float(token[64:].mean()),
        }
        arrays[kind + "_token_delta"] = token
        arrays[kind + "_layer_mean"] = normalized.mean(axis=(1, 2))
    return result, arrays

report = {"status": "running", "config_sha256": sha,
          "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          "device": args.device, "torch": torch.__version__, "transformers": transformers.__version__,
          "platform": platform.platform(), "model_revision": cfg["revision"], "dtype": "float32",
          "cache_measurement": "keys after k_norm and before RoPE; values after v_proj; no fp16 serialization",
          "rows": []}

def record(case, condition, candidate, reference):
    metrics, arrays = compare(candidate, reference)
    idx = len(report["rows"])
    np.savez_compressed(out / f"row_{idx:03d}.npz", **arrays)
    row = {"case": case["handoff_id"], "condition": condition, "metrics": metrics}
    report["rows"].append(row)
    (out / "checkpoint.json").write_text(json.dumps(report, indent=2))
    print(idx, condition, "K", round(metrics["K"]["mean_delta"], 6), "V", round(metrics["V"]["mean_delta"], 6), flush=True)
    return metrics

began = time.monotonic()
for i, case in enumerate(cfg["cases"]):
    prefix = case["prefix"][-cfg["prefix_tokens"]:]
    block = case["block"]
    other = cfg["cases"][(i + 1) % len(cfg["cases"])]["prefix"]
    reference = states(prefix + block, len(prefix))
    if cfg.get("experiment") == "proximity_control":
        record(case, "replace_all", states(case["replacement_prefix"] + block, len(prefix)), reference)
        for keep in cfg["retained_recent_tokens"]:
            for location in ["near", "far"]:
                changed = case["replacement_prefix"].copy()
                region = slice(-keep, None) if location == "near" else slice(0, keep)
                changed[region] = prefix[region]
                assert sum(a != b for a, b in zip(changed, prefix)) == len(prefix) - keep
                record(case, f"keep_{location}_{keep}", states(changed + block, len(prefix)), reference)
        continue
    control = record(case, "identity", states(prefix + block, len(prefix)), reference)
    assert all(control[k]["max_delta"] < 1e-6 for k in ["K", "V"])
    control = record(case, "prefix_extension", states(prefix + block + block[:32], len(prefix)), reference)
    assert all(control[k]["max_delta"] < 1e-6 for k in ["K", "V"])
    record(case, "position_shift", states(prefix + block, len(prefix), cfg["position_shift"]), reference)
    record(case, "wrong_token_pairing", {k: v[:, ::-1] for k, v in reference.items()}, reference)
    for keep in cfg["retained_recent_tokens"]:
        changed = other[-len(prefix):].copy()
        if keep:
            changed[-keep:] = prefix[-keep:]
        record(case, f"keep_recent_{keep}", states(changed + block, len(changed)), reference)
    for length in cfg["length_prefix_tokens"]:
        source = case["prefix"][-length:]
        fresh = states(source + block, length)
        changed = other[-length:].copy()
        changed[-32:] = source[-32:]
        record(case, f"history_{length}_keep_32", states(changed + block, length), fresh)
    if args.device == "mps":
        torch.mps.empty_cache()
report["status"] = "complete"
report["elapsed_seconds"] = time.monotonic() - began
if args.device == "mps":
    report["mps_driver_memory_bytes_at_end"] = torch.mps.driver_allocated_memory()
(out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
print("Complete", len(report["rows"]), "comparisons", round(report["elapsed_seconds"], 1), "seconds", flush=True)
