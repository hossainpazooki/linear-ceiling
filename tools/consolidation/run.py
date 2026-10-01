# Resumable same-model extension, with compact errors and one retained raw witness per model.
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import tomllib
import numpy as np
import torch
import transformers
from transformers import AutoConfig, AutoModel
from linear_ceiling.e9_pertoken import centered_delta, token_mean, f_star
from capture import capture

ROOT = Path(__file__).resolve().parents[2]
def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def write(path, data):
    path = Path(path)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data,indent=2)+"\n")
    temp.replace(path)

def score(source, fresh, cfg, output=None):
    result, arrays = {}, {}
    for kind in ["K","V"]:
        s = np.load(Path(source)/f"{kind}.npy",mmap_mode="r")
        r = np.load(Path(fresh)/f"{kind}.npy",mmap_mode="r")
        layers,n,heads,dim = r.shape
        squares = np.empty((n,layers,heads),dtype=np.float32)
        sst = np.empty((layers,heads),dtype=np.float64)
        for l in range(layers):
            ref = r[l].astype(np.float64)
            squares[:,l] = ((s[l].astype(np.float64)-ref)**2).sum(-1)
            sst[l] = ((ref-ref.mean(0,keepdims=True))**2).sum((0,2))
        d = centered_delta(squares,sst,n)
        per_token = token_mean(d)
        tau = cfg[f"tau_{kind}"]
        result[kind] = {"mean_delta":float(per_token.mean()),"max_delta":float(per_token.max()),
                       "r2":float(1-per_token.mean()),"tail_fraction":float((per_token>tau).mean()),
                       "fstar":f_star(per_token,tau),
                       "ladder":{str(t):f_star(per_token,t) for t in cfg["tau_ladder"]}}
        arrays.update({kind+"_squares":squares,kind+"_sst":sst,kind+"_token_delta":per_token,
                       kind+"_layer_mean":d.mean((0,2))})
    if output:
        np.savez_compressed(output,**arrays)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",required=True)
    parser.add_argument("--inputs",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    cfgpath = ROOT/"config/consolidation.toml"
    cfg = tomllib.loads(cfgpath.read_text())
    spec = next(m for m in cfg["models"] if m["name"]==args.model)
    manifestpath = ROOT/"config/consolidation-manifest.json"
    manifest = json.loads(manifestpath.read_text())
    assert digest(cfgpath)==manifest["config_sha256"]
    records = manifest["models"][args.model]
    included = [r for r in records if not r["excluded"]]
    for r in included:
        assert digest(args.inputs/r["file"])==r["sha256"],r["file"]
    out = args.output/args.model
    out.mkdir(parents=True,exist_ok=True)
    reportpath = out/"report.json"
    source_hashes = {name:digest(Path(__file__).with_name(name)) for name in ("run.py","capture.py")}
    report = json.loads(reportpath.read_text()) if reportpath.exists() else {
        "model":spec,"config_sha256":digest(cfgpath),"manifest_sha256":digest(manifestpath),
        "code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "code_sha256":source_hashes,
        "torch":torch.__version__,"transformers":transformers.__version__,"numpy":np.__version__,
        "cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name(),"dtype":"float32",
        "capture":"K after any key normalization and before RoPE; V after projection; unquantized float32",
        "scores":{},"excluded":[r for r in records if r["excluded"]],"complete":False}
    assert report["config_sha256"]==digest(cfgpath) and report["manifest_sha256"]==digest(manifestpath)
    expected = {r["handoff"] for r in included}
    scored = set(report["scores"])
    if not scored <= expected or (report["complete"] and scored != expected):
        raise ValueError("reported cohort does not match the included handoffs")
    for entry in report["scores"].values():
        assert digest(out/entry["file"])==entry["sha256"]
    if report["complete"]:
        print("Already complete and hash-verified",args.model,flush=True)
        return
    # Partial runs cannot combine records from different code or numerical runtimes.
    identity = {"code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                "code_sha256":source_hashes,
                "torch":torch.__version__,"transformers":transformers.__version__,"numpy":np.__version__,
                "cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name(),"dtype":"float32"}
    if any(key not in report or report[key] != value for key,value in identity.items()):
        raise ValueError("resume identity differs (code, runtime, GPU, or dtype); use a new output")
    torch.set_num_threads(8)
    torch.manual_seed(cfg["seed"])
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    mc = AutoConfig.from_pretrained(spec["model"],revision=spec["revision"])
    rope = {k:spec[k] for k in ["rope_type","factor","original_max_position_embeddings"]}
    mc.rope_parameters = {**mc.rope_parameters,**rope}
    mc.max_position_embeddings = cfg["context_cap"]
    model = AutoModel.from_pretrained(spec["model"],revision=spec["revision"],config=mc,
                                     dtype=torch.float32,attn_implementation=cfg["attention"],local_files_only=True).eval().cuda()
    report["effective_rope"] = model.config.rope_parameters
    report["no_rope_layers"] = [i for i,l in enumerate(model.layers) if not getattr(l.self_attn,"use_rope",True)]
    scratch = out/"scratch"
    scratch.mkdir(exist_ok=True)
    if "control" not in report:
        with np.load(args.inputs/included[0]["file"]) as a:
            tokens = a["sender"][:1025]
        positions = np.arange(1024)
        capture(model,tokens[:1024],positions,scratch/"control-full",1024)
        capture(model,tokens,positions,scratch/"control-chunked-extension",cfg["chunk_tokens"])
        control = score(scratch/"control-full",scratch/"control-chunked-extension",cfg)
        assert max(control[k]["max_delta"] for k in ["K","V"])<=cfg["control_max_delta"],control
        report["control"] = control
        write(reportpath,report)
        shutil.rmtree(scratch/"control-full")
        shutil.rmtree(scratch/"control-chunked-extension")
    # The real longest sender is the memory probe, and its cache is reused when its row is scored.
    largest = max(included,key=lambda r:r["sender_tokens"])
    order = [largest]+[r for r in included if r!=largest]
    for index,r in enumerate(order):
        hid = r["handoff"]
        if hid in report["scores"]:
            continue
        with np.load(args.inputs/r["file"]) as a:
            sender,receiver,pairs = a["sender"],a["receiver"],a["pairs"]
        stem = Path(r["file"]).stem
        folder = scratch/stem
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        began = time.monotonic()
        capture(model,sender,pairs[:,0],folder/"sender",cfg["chunk_tokens"])
        capture(model,receiver,pairs[:,1],folder/"receiver",cfg["chunk_tokens"])
        torch.cuda.synchronize()
        metrics = score(folder/"sender",folder/"receiver",cfg,out/f"{stem}.npz")
        entry = {**r,"metrics":metrics,"file":f"{stem}.npz","sha256":digest(out/f"{stem}.npz"),
                 "seconds":time.monotonic()-began,"peak_allocated_GiB":torch.cuda.max_memory_allocated()/2**30}
        if r == included[0]:
            witness = out/"witness"
            if witness.exists():
                raise RuntimeError("Unexpected previous raw witness; investigate before replacing it")
            folder.rename(witness)
            entry["witness"] = {str(p.relative_to(out)):digest(p) for p in witness.rglob("*.npy")}
        report["scores"][hid] = entry
        write(reportpath,report)
        if folder.exists():
            shutil.rmtree(folder)
        print(json.dumps({"model":args.model,"done":len(report["scores"]),"total":len(included),
                          "sender_tokens":len(sender),"seconds":round(entry["seconds"],1),
                          "peak_GiB":round(entry["peak_allocated_GiB"],2),"K":metrics["K"]}),flush=True)
    report["complete"] = True
    write(reportpath,report)
    print("COMPLETE",args.model,flush=True)

if __name__=="__main__":
    main()
