"""Verify an HF dataset backup against a local mirror (protocol R8): every LFS file's `lfs.sha256` from
`dataset_info(files_metadata=True)` must equal the local file's sha256; every non-LFS file is downloaded and hashed;
every local file must be on the Hub and vice versa. Reads HF_TOKEN from the environment only.

usage: python tools/hf_verify_backup.py <repo_id> <local_root> [--exclude README.md]
exit 0 only when every file matches in both directions."""
import argparse, hashlib, io, os, sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""): h.update(c)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("repo_id"); ap.add_argument("local_root")
    ap.add_argument("--exclude", nargs="*", default=[]); a = ap.parse_args()
    if not os.environ.get("HF_TOKEN"): print("HF_TOKEN not set in the environment"); return 2
    root = Path(a.local_root); api = HfApi()
    info = api.dataset_info(a.repo_id, files_metadata=True)
    remote = {s.rfilename: s for s in info.siblings}
    local = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file() and not p.relative_to(root).as_posix().startswith(".cache/")}
    for e in list(a.exclude) + [".gitattributes"]:   # the Hub writes .gitattributes itself; it is never part of a mirror
        remote.pop(e, None); local.pop(e, None)
    print(f"repo {a.repo_id} @ {info.sha[:8]} | remote {len(remote)} files | local {len(local)} files")
    bad, n_lfs, n_dl = [], 0, 0
    for rel in sorted(set(remote) | set(local)):
        if rel not in remote: bad.append(f"MISSING ON HUB {rel}"); print("  MISSING ON HUB", rel); continue
        if rel not in local: bad.append(f"NOT LOCAL {rel}"); print("  NOT LOCAL", rel); continue
        want = sha256(local[rel]); s = remote[rel]
        if s.lfs and s.lfs.get("sha256"):
            got, how = s.lfs["sha256"], "lfs"; n_lfs += 1
        else:
            got, how = sha256(Path(hf_hub_download(a.repo_id, rel, repo_type="dataset", revision=info.sha))), "downloaded"; n_dl += 1
        ok = got == want
        print(f"  {'OK ' if ok else 'BAD'} {how:10s} {rel}")
        if not ok: bad.append(f"MISMATCH {rel}")
    print(f"lfs-compared {n_lfs}, downloaded+hashed {n_dl}, problems {len(bad)}")
    print("BACKUP VERIFIED" if not bad else "BACKUP NOT VERIFIED: " + "; ".join(bad[:10]))
    return 0 if not bad else 1

if __name__ == "__main__":
    sys.exit(main())
