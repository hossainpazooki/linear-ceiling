"""Per-handoff puller for a GPU run on a box reached over ssh: mirror, verify, then delete (protocol R5/R6).

Every ROUND: mirror ~/<exp>.log, ~/<exp>.rc, ~/setup.log, ~/probe.log and the box scripts into
results/<exp>/logs/box/, and every SMALL record under results/<exp>/ (report.json, align/, controls/, scores/,
tokens/, the bridge's score + per-token files) home; then for every record that carries `kept_dumps`
(scored handoffs in the keep subset AND the bridge handoffs), stream the kept directory home with tar over
ssh, verify every fingerprinted file's sha256 against report.json, and ONLY THEN delete that directory on the
box. Exits when report.complete and every kept directory is home and deleted on the box.

usage:  pull.py [exp]                      (default exp = e9l)
env:    BOX        ubuntu@<ip>               BOX_KEY   ssh private key (default ~/.ssh/lc-e9l-2026-09-10)
        LC_RESULTS local results root (default ~/dev/linear-ceiling/results)
        BOX_REPO   the linear-ceiling checkout on the box (default linear-ceiling)
        PULL_STATE state file (default ~/.lc-<exp>-pull.json)     PULL_EVERY seconds (default 120)

Mirror rule (learnings 2026-09-04): a small file is re-pulled when its remote size OR mtime differs from what was
recorded; a same-size skip alone is blind to a rewritten binary of equal length. Streams are tar-over-ssh so one
connection carries a whole batch (no ControlMaster on Windows OpenSSH).
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EXP = sys.argv[1] if len(sys.argv) > 1 else "e9l"
BOX = os.environ["BOX"]
KEY = os.environ.get("BOX_KEY", str(Path.home() / ".ssh" / "lc-e9l-2026-09-10"))
LOCAL = Path(os.environ.get("LC_RESULTS") or (Path.home() / "dev" / "linear-ceiling" / "results")) / EXP
REPO = os.environ.get("BOX_REPO", "linear-ceiling")
REMOTE = f"{REPO}/results/{EXP}"
STATE = Path(os.environ.get("PULL_STATE") or (Path.home() / f".lc-{EXP}-pull.json"))
EVERY = int(os.environ.get("PULL_EVERY", "120"))
SSH = ["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=accept-new", "-o", "ServerAliveInterval=30",
       "-o", "ConnectTimeout=20", "-o", "BatchMode=yes", BOX]
BOX_FILES = f"{EXP}.log {EXP}.rc setup.log setup.rc probe.log launches.log manifest_check.out setup.sh run.sh probe_e9l.py"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def ssh(cmd: str, timeout: int = 120) -> str:
    r = subprocess.run(SSH + [cmd], capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"ssh rc={r.returncode}: {r.stderr.decode('utf-8', 'replace')[-500:]}")
    return r.stdout.decode("utf-8", "replace")


def stream_tar(remote_dir: str, names: list[str], local_dir: Path, timeout: int = 7200) -> None:
    """tar -C <remote_dir> <names> on the box, untar into local_dir; one ssh connection per call."""
    local_dir.mkdir(parents=True, exist_ok=True)
    quoted = " ".join(f"'{n}'" for n in names)
    remote = f"cd {remote_dir} && tar -cf - {quoted}"
    with subprocess.Popen(SSH + [remote], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as src:
        tar = subprocess.run(["tar", "-xf", "-", "-C", str(local_dir)], stdin=src.stdout, capture_output=True, timeout=timeout)
        err = src.stderr.read().decode("utf-8", "replace")
        src.wait(timeout=60)
    if src.returncode != 0 or tar.returncode != 0:
        raise RuntimeError(f"stream failed ({remote_dir} {names[:3]}...): ssh rc={src.returncode} tar rc={tar.returncode} {err[-300:]} {tar.stderr.decode('utf-8','replace')[-300:]}")


def remote_small_listing() -> dict[str, list]:
    """{relpath: [size, mtime]} for every file under results/<exp>/ that is NOT inside a kept tensor directory."""
    out = ssh(f"cd {REMOTE} 2>/dev/null && find . -type f -printf '%s %T@ %p\\n' || true")
    listing = {}
    for line in out.splitlines():
        size, mtime, path = line.split(" ", 2)
        rel = path[2:] if path.startswith("./") else path
        parts = rel.split("/")
        if parts[0] == "scratch" or (parts[0] == "bridge" and len(parts) >= 3):
            continue       # tensor directories travel by fingerprint, not by mirror
        listing[rel] = [int(size), mtime]
    return listing


def mirror_small(seen: dict) -> int:
    listing = remote_small_listing()
    changed = [rel for rel, sm in listing.items() if seen.get(rel) != sm or not (LOCAL / rel).exists()]
    if changed:
        stream_tar(REMOTE, changed, LOCAL)
        for rel in changed:
            seen[rel] = listing[rel]
    return len(changed)


def mirror_box_files() -> None:
    dst = LOCAL / "logs" / "box"
    dst.mkdir(parents=True, exist_ok=True)
    names = ssh(f"cd ~ && ls -1 {BOX_FILES} {EXP}.*.halt.log 2>/dev/null || true").split()
    if names:
        stream_tar("~", names, dst)


def kept_records(rep: dict) -> list[tuple[str, str, dict]]:
    """(label, kept_dir, {relpath: sha}) for every record carrying kept_dumps."""
    out = []
    for hid, rec in rep.get("scores", {}).items():
        if rec.get("kept_dumps"):
            flat = {f"{d}/{rel}": h for d, files in rec["kept_dumps"].items() for rel, h in files.items()}
            out.append((hid, rec["kept_dir"], flat))
    for hid, rec in (rep.get("bridge") or {}).get("handoffs", {}).items():
        if rec.get("kept_dumps"):
            flat = {f"{d}/{rel}": h for d, files in rec["kept_dumps"].items() for rel, h in files.items()}
            if rec.get("pairs_file") and rec.get("pairs_sha256"):
                flat[rec["pairs_file"]] = rec["pairs_sha256"]
            out.append((f"bridge:{hid}", rec["kept_dir"], flat))
    return out


def verify_local(kept_dir: str, flat: dict) -> list[str]:
    bad = []
    for rel, want in flat.items():
        p = LOCAL / kept_dir / rel
        if not p.exists() or sha256(p) != want:
            bad.append(rel)
    return bad


def main() -> None:
    state = json.loads(STATE.read_text()) if STATE.exists() else {"deleted": [], "seen": {}}
    state.setdefault("seen", {})
    while True:
        t0 = time.strftime("%H:%M:%S", time.gmtime())
        try:
            mirror_box_files()
            n = mirror_small(state["seen"])
        except Exception as e:
            print(f"== {t0} mirror failed ({type(e).__name__}: {str(e)[:200]}); retrying next round", flush=True)
            time.sleep(EVERY)
            continue
        STATE.write_text(json.dumps(state, indent=1))
        rep_path = LOCAL / "report.json"
        if not rep_path.exists():
            print(f"== {t0} no report.json yet ({n} small files mirrored)", flush=True)
            time.sleep(EVERY)
            continue
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        n_inc = rep.get("coverage", {}).get("included", "?")
        print(f"== {t0} scored {len(rep.get('scores', {}))}/{n_inc}; bridge {'done' if rep.get('bridge') else 'pending'}; "
              f"complete={rep.get('complete')}; {n} small files mirrored", flush=True)
        for label, kept_dir, flat in kept_records(rep):
            if kept_dir in state["deleted"]:
                continue
            bad = verify_local(kept_dir, flat)
            if bad:
                print(f"  pulling {label} -> {kept_dir} ({len(bad)} of {len(flat)} files to fetch)", flush=True)
                try:
                    parent, leaf = os.path.split(kept_dir)
                    stream_tar(f"{REMOTE}/{parent}" if parent else REMOTE, [leaf], LOCAL / parent if parent else LOCAL)
                except Exception as e:
                    print(f"  stream failed ({type(e).__name__}: {str(e)[:200]}); kept on box", flush=True)
                    continue
                bad = verify_local(kept_dir, flat)
            if bad:
                print(f"  MISMATCH {label}: {len(bad)} files differ from the fingerprint (kept on box): {bad[:3]}", flush=True)
                continue
            ssh(f"rm -rf ~/{REMOTE}/{kept_dir} && echo deleted-on-box {kept_dir}", 120)
            print(f"  verified {len(flat)} files, deleted on box: {kept_dir}", flush=True)
            state["deleted"].append(kept_dir)
            STATE.write_text(json.dumps(state, indent=1))
        if rep.get("complete") and all(kd in state["deleted"] for _, kd, _ in kept_records(rep)):
            mirror_small(state["seen"]); mirror_box_files()
            STATE.write_text(json.dumps(state, indent=1))
            print(f"== run complete and every kept directory is home; final mirror done; report.json sha256 {sha256(rep_path)}", flush=True)
            return
        time.sleep(EVERY)


if __name__ == "__main__":
    main()
