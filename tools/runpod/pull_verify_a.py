"""Pull sitting A's artifacts home, verify every one, and only then unlock `rp.py terminate`.

THIS IS THE STEP THAT MAKES TERMINATION SAFE. A pod's container disk is ephemeral: the mapper and the
generic dumps are the only artifacts in this campaign that cannot be recomputed without renting
another card, and terminating destroys whatever was not pulled. So `rp.py terminate` refuses (without
--force) until the verify file this script writes exists, and this script writes it only when every
expected path is present AND every sha256 in the box-written MANIFEST.sha256 matches at home.

Two failure modes it is built around, both of which have happened in this program:

  * a SHORT pull. rsync exits 0 having copied a subset, or a path was never in the box's package
    list, and the gap is only discovered at home weeks later when a summarizer refuses. So the
    EXPECTED list below is explicit and checked by name, not inferred from what happened to arrive.
  * a CORRUPT pull. Bytes change in transit. MANIFEST.sha256 is written ON the box, before anything
    is transferred, and is re-checked here against the files as they landed.

`summarize_e8` re-fingerprints the agent dumps and the token file at home, so those are not optional
extras in the pull set -- omitting them means renting another card. They are in EXPECTED for that
reason, with the reason attached.

usage:
  .venv/bin/python tools/runpod/pull_verify_a.py --local ~/sitting-a --pair <pair> [--exp e8f]
      [--remote /workspace/pull] [--verify-file /tmp/lc_sittingA_verified] [--skip-pull]
exit 0 only when everything verified; the verify file is written only on exit 0.
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Explicit, with the reason each one must be here. Paths are relative to the pull root and mirror
# what tools/runpod/sitting_a.sh packages.
def expected(pair: str, exp: str) -> dict[str, str]:
    return {
        f"lc/results/{exp}/report.json":
            "the E8 result itself; every figure in the figures entry is read from it",
        f"lc/results/{exp}/kv/agent/source":
            "summarize_e8 re-fingerprints the agent dumps at home; without them the summarizer refuses",
        f"lc/results/{exp}/kv/agent/target":
            "the other half of the same fingerprint check",
        f"lc/data/{exp}":
            "the agent-text token file and its manifest, re-fingerprinted by summarize_e8",
        f"up/data/kv/{pair}/source":
            "the generic dump; calibrate_tau fingerprints it and score_mapper re-scores from it",
        f"up/data/kv/{pair}/target":
            "the other generic dump; the pair's tau is 1 - the held-out R^2 measured on these",
        f"up/data/tokens/{pair}_n50_len1024_seed0.npy":
            "the registered n=50 seed-0 draw; the dumps are meaningless without the tokens they used",
        f"up/mappers/{pair}":
            "THE MAPPER. k1/k4/k8, json + safetensors. Irreplaceable without another card",
        f"up/results/mapper/{pair}":
            "r2.json, the archived held-out R^2 that tau is derived from and cross-checked against",
        "logs":
            "the sitting log and the manifest check output; the runbook's box row is reconstructed from them",
        "MANIFEST.sha256":
            "the box-written hashes this script verifies against",
    }


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--local", required=True, help="where the pull lands at home")
    ap.add_argument("--pair", required=True)
    ap.add_argument("--exp", default="e8f")
    ap.add_argument("--remote", default="/workspace/pull")
    ap.add_argument("--verify-file", default="/tmp/lc_sittingA_verified")
    ap.add_argument("--skip-pull", action="store_true", help="verify an already-pulled tree")
    a = ap.parse_args()

    local = Path(a.local).expanduser()
    if not a.skip_pull:
        local.mkdir(parents=True, exist_ok=True)
        print(f"== pulling {a.remote} -> {local}")
        rc = subprocess.call([sys.executable, str(HERE / "rp.py"), "pull", a.remote, str(local)])
        if rc != 0:
            raise SystemExit(f"pull_verify REFUSED: the pull itself failed (rc {rc}). "
                             "Do NOT terminate; the artifacts are still only on ephemeral disk.")
    root = local / Path(a.remote).name if (local / Path(a.remote).name).exists() else local

    print(f"== checking the expected set under {root}")
    missing = []
    for rel, why in expected(a.pair, a.exp).items():
        if not (root / rel).exists():
            missing.append((rel, why))
            print(f"  MISSING {rel}\n          ^ {why}")
        else:
            print(f"  present {rel}")
    if missing:
        raise SystemExit(f"pull_verify REFUSED: {len(missing)} expected path(s) absent. Do NOT "
                         "terminate -- re-package on the box and pull again.")

    man = root / "MANIFEST.sha256"
    print(f"== verifying every sha256 in {man.name} (written on the box)")
    bad, checked = [], 0
    for line in man.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rel = line.partition("  ")
        rel = rel.strip().lstrip("./")
        if rel in ("MANIFEST.sha256", ""):
            continue
        f = root / rel
        if not f.is_file():
            bad.append((rel, "absent at home"))
            continue
        got = sha256(f)
        checked += 1
        if got != digest:
            bad.append((rel, f"sha256 {got[:12]} != box {digest[:12]}"))
    for rel, why in bad:
        print(f"  BAD {rel}: {why}")
    if bad:
        raise SystemExit(f"pull_verify REFUSED: {len(bad)} file(s) failed. Do NOT terminate.")

    vf = Path(a.verify_file)
    vf.write_text(f"sitting A verified at home\nroot={root}\nfiles_checked={checked}\n"
                  f"pair={a.pair}\nexp={a.exp}\n")
    print(f"\n{checked} files verified against the box manifest, every expected path present.")
    print(f"verify file written: {vf}")
    print("`rp.py terminate` will now proceed without --force. Terminate, then confirm it is GONE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
