import concurrent.futures
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
DATASETS = {
    "e9": ("hossainpazooki/linear-ceiling-e9-2026-09-04", "a45e9ee8c511f5aab738400f06a2462b4fee5391", ""),
    "e9l": ("hossainpazooki/linear-ceiling-e9l-2026-09-10", "0879f5f59db394e5ebf24e8b06f481ece6e4976a", "results/e9l/"),
    "e9s": ("hossainpazooki/linear-ceiling-e9s-2026-09-13", "a63e3c272afe914aaf96511ab53ab2c2fdf7c6a8", "results/e9s/"),
}

def main():
    jobs = []
    for cell, (repo, revision, prefix) in DATASETS.items():
        url = f"https://huggingface.co/api/datasets/{repo}/revision/{revision}?blobs=true"
        metadata = json.load(urllib.request.urlopen(url))
        if metadata["sha"] != revision:
            raise RuntimeError(f"Wrong archive revision for {cell}")
        destination = ROOT / "records" / cell
        destination.mkdir(parents=True, exist_ok=True)
        files = []
        for item in metadata["siblings"]:
            name = item["rfilename"]
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix):]
            if relative in {"report.json", "summary.json"} or relative.startswith(("scores/", "tokens/", "align/")):
                files.append((item, relative))
        manifest = {"repo": repo, "revision": revision, "sha": revision, "files": [
            {"path": rel, "size": item.get("size"), "sha256": (item.get("lfs") or {}).get("sha256")}
            for item, rel in files]}
        (destination / "source.json").write_text(json.dumps(manifest, indent=2))
        jobs.extend((cell, repo, revision, item, rel, destination) for item, rel in files)
        print(f"{cell}: {len(files)} files at {revision}", flush=True)

    def download(job):
        cell, repo, revision, item, relative, destination = job
        url = f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{urllib.parse.quote(item['rfilename'], safe='/')}"
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url) as response, path.open("wb") as output:
            while block := response.read(1 << 20):
                output.write(block)
        if item.get("size") is not None and path.stat().st_size != item["size"]:
            raise RuntimeError(f"Size mismatch: {path}")
        with path.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        expected = (item.get("lfs") or {}).get("sha256")
        if expected and digest != expected:
            raise RuntimeError(f"SHA-256 mismatch: {path}")
        return cell, relative, digest

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        observed = {}
        for i, (cell, relative, digest) in enumerate(pool.map(download, jobs), 1):
            observed[(cell, relative)] = digest
            if i % 50 == 0:
                print(f"{i}/{len(jobs)} downloaded: {relative}", flush=True)
    for cell in DATASETS:
        path = ROOT / "records" / cell / "source.json"
        manifest = json.loads(path.read_text())
        for item in manifest["files"]:
            item["observed_sha256"] = observed[(cell, item["path"])]
        path.write_text(json.dumps(manifest, indent=2))
    print(f"Downloaded {len(jobs)} pinned archive files.", flush=True)

if __name__ == "__main__":
    main()
