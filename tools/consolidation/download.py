# Download each public model once, at its committed revision; no credentials required.
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tomllib
from huggingface_hub import snapshot_download
cfg = tomllib.loads((Path(__file__).resolve().parents[2]/"config/consolidation.toml").read_text())
def download_model(spec):
    snapshot_download(spec["model"],revision=spec["revision"],
                      allow_patterns=["*.json","*.safetensors","*.txt","*.model"])
    print("CACHED",spec["name"],spec["revision"],flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(download_model,cfg["models"]))
