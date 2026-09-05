"""Per-handoff puller for a GPU run on a JupyterHub-only box (no ssh): mirror, verify, then delete.

Every ROUND: mirror results/<exp>/{report.json, align/, controls/, scores/, tokens/} and <exp>.log home;
for each handoff whose report record carries `kept_dumps`, download scratch/<stem>/ file by file, verify
every sha256 against the fingerprint the driver wrote into report.json, and ONLY THEN delete that
scratch dir on the box. State in pulled.json next to this script's state dir. Exits when
report.complete and every kept dump is home.

usage:  pull.py [exp]            (default exp = e9)
env:    JH_URL, JH_USER, JH_TOKEN as jh.py; JH_STATE_DIR for pulled.json;
        LC_RESULTS   local results root (default ~/dev/linear-ceiling/results)
        JH_REPO_DIR  the linear-ceiling checkout on the box (default linear-ceiling)

Mirror rule (learnings 2026-09-04): a file is re-pulled when its remote size OR last_modified differs
from what was recorded; a same-size skip alone is blind to a rewritten binary of equal length.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import jh  # noqa: E402

EXP = sys.argv[1] if len(sys.argv) > 1 else "e9"
LOCAL = Path(os.environ.get("LC_RESULTS") or (Path.home() / "dev" / "linear-ceiling" / "results")) / EXP
REPO = os.environ.get("JH_REPO_DIR", "linear-ceiling")
REMOTE = f"{REPO}/results/{EXP}"
STATE = jh.STATE / f"pulled_{EXP}.json"
MIRROR_DIRS = ("align", "controls", "scores", "tokens")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def listing(remote_dir: str):
    r = requests.get(f"{jh.BASE}/api/contents/{remote_dir}", headers=jh.HDR, timeout=60)
    if r.status_code != 200:
        return []
    return [(c["name"], c["size"], c["type"], c.get("last_modified")) for c in r.json().get("content", [])]


def mirror(sub: str, seen: dict) -> None:
    for name, size, typ, mtime in listing(f"{REMOTE}/{sub}"):
        if typ != "file":
            continue
        key = f"{sub}/{name}"
        dst = LOCAL / sub / name
        if dst.exists() and seen.get(key) == [size, mtime]:
            continue
        jh.down(f"{REMOTE}/{sub}/{name}", str(dst))
        seen[key] = [size, mtime]


def pull_kept(stem: str, fp: dict) -> bool:
    ok = True
    for rel, want in fp.items():
        dst = LOCAL / "scratch" / stem / rel
        if not (dst.exists() and sha256(dst) == want):
            jh.down(f"{REMOTE}/scratch/{stem}/{rel}", str(dst))
            got = sha256(dst)
            if got != want:
                print(f"  MISMATCH {stem}/{rel}: got {got[:12]} want {want[:12]} (kept on box)")
                ok = False
    return ok


def stem_of(hid: str) -> str:
    return hid.replace("/", "__").replace("#", "_sw")


def main() -> None:
    state = json.loads(STATE.read_text()) if STATE.exists() else {"deleted": [], "seen": {}}
    state.setdefault("seen", {})
    while True:
        t0 = time.strftime("%H:%M:%S", time.gmtime())
        jh.down(f"{REPO}/{EXP}.log", str(LOCAL / f"{EXP}.log"))
        try:
            jh.down(f"{REMOTE}/report.json", str(LOCAL / "report.json"))
        except Exception as e:   # no report until the first handoff is scored
            print(f"== {t0} no report.json yet ({type(e).__name__})", flush=True)
            time.sleep(120)
            continue
        rep = json.loads((LOCAL / "report.json").read_text(encoding="utf-8"))
        for sub in MIRROR_DIRS:
            mirror(sub, state["seen"])
        STATE.write_text(json.dumps(state, indent=1))
        print(f"== {t0} scored {len(rep['scores'])}/{rep['coverage']['included']}", flush=True)
        for hid, rec in rep["scores"].items():
            stem = stem_of(hid)
            fp = rec.get("kept_dumps")
            if not fp or stem in state["deleted"]:
                continue
            flat = {f"{d}/{rel}": h for d, files in fp.items() for rel, h in files.items()}
            print(f"  pulling kept {stem} ({len(flat)} files)", flush=True)
            if pull_kept(stem, flat):
                jh.exec_(f"rm -rf ~/{REMOTE}/scratch/{stem} && echo deleted-on-box {stem}", 60)
                state["deleted"].append(stem)
                STATE.write_text(json.dumps(state, indent=1))
        if rep.get("complete") and all(stem_of(hid) in state["deleted"]
                                       for hid, rec in rep["scores"].items() if rec.get("kept_dumps")):
            print("== run complete and every kept dump is home; final mirror done", flush=True)
            return
        time.sleep(120)


if __name__ == "__main__":
    main()
