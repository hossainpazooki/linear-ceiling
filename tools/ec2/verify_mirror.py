"""R6 at home: re-verify the mirror of results/<exp>/ from RAW BYTES against report.json, independently of the
puller's own bookkeeping. Every kept dump file (scored keep subset + bridge) and every score/per-token file the
report fingerprints is re-hashed; the report must be complete. Prints the report's sha256 (R7 step 1) and exits
non-zero on any missing or mismatched file.

usage:  verify_mirror.py [exp]      (default e9l; LC_RESULTS as pull.py)
"""
import hashlib
import json
import os
import sys
from pathlib import Path

EXP = sys.argv[1] if len(sys.argv) > 1 else "e9l"
LOCAL = Path(os.environ.get("LC_RESULTS") or (Path.home() / "dev" / "linear-ceiling" / "results")) / EXP


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    rep_path = LOCAL / "report.json"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    print(f"report.json sha256 {sha256(rep_path)}  complete={rep.get('complete')}  scored={len(rep['scores'])}/{rep['coverage']['included']}"
          + (f"  PARTIAL {rep['partial']}" if rep.get("partial") else ""))
    if not rep.get("complete"):
        print("NOT COMPLETE: the mirror is not releasable")
        return 2
    checks: list[tuple[str, Path, str]] = []
    for hid, rec in rep["scores"].items():
        checks.append((f"score {hid}", LOCAL / "scores" / rec["score_file"], rec["score_sha256"]))
        checks.append((f"tokens {hid}", LOCAL / "tokens" / rec["tokens_file"], rec["tokens_sha256"]))
        for d, files in (rec.get("kept_dumps") or {}).items():
            for rel, h in files.items():
                checks.append((f"kept {hid}", LOCAL / rec["kept_dir"] / d / rel, h))
    for hid, rec in (rep.get("bridge") or {}).get("handoffs", {}).items():
        checks.append((f"bridge score {hid}", LOCAL / "bridge" / rec["score_file"], rec["score_sha256"]))
        checks.append((f"bridge tokens {hid}", LOCAL / "bridge" / rec["tokens_file"], rec["tokens_sha256"]))
        checks.append((f"bridge pairs {hid}", LOCAL / rec["kept_dir"] / rec["pairs_file"], rec["pairs_sha256"]))
        for d, files in (rec.get("kept_dumps") or {}).items():
            for rel, h in files.items():
                checks.append((f"bridge kept {hid}", LOCAL / rec["kept_dir"] / d / rel, h))
    bad, total_bytes = [], 0
    for label, p, want in checks:
        if not p.exists():
            bad.append(f"MISSING {label}: {p.relative_to(LOCAL)}")
            continue
        total_bytes += p.stat().st_size
        got = sha256(p)
        if got != want:
            bad.append(f"MISMATCH {label}: {p.relative_to(LOCAL)} got {got[:12]} want {want[:12]}")
    for line in bad:
        print(line)
    print(f"{len(checks) - len(bad)}/{len(checks)} fingerprinted files verified from raw bytes, {total_bytes:,} B; "
          f"{'ALL VERIFIED' if not bad else str(len(bad)) + ' BAD'}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
