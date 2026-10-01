# Restore the small, frozen pilot input artifact; no model download or inference.
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/seam-pilot"))
    args = parser.parse_args()
    source = json.loads(Path(__file__).with_name("source.json").read_text())
    path = args.output / "proximity_config.json"
    if path.exists():
        data = path.read_bytes()
    else:
        url = ("https://raw.githubusercontent.com/neuriv/linear-ceiling/"
               + source["source_commit"] + "/" + source["config_path"])
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
    sha = hashlib.sha256(data).hexdigest()
    if sha != source["config_sha256"]:
        raise ValueError("Frozen pilot input hash mismatch")
    args.output.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    path.with_suffix(".sha256").write_text(sha + "\n")
    print(f"Verified {path}: {sha}")


if __name__ == "__main__":
    main()
