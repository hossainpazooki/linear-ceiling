"""Entry point for every experiment that consumes a sealed prediction (E1, E2, E3).

In W1 this runner does exactly one thing: the seal gate. It exits 3 ("not implemented")
after the gate passes, so the refusal behaviour exists before any experiment does.
E0 is weights-only and pre-seal; it lives in linear_ceiling.e0.
"""
import argparse
import sys
import tomllib
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_seal_config
from linear_ceiling.seal import SealViolation, require_sealed

SEALED_CONSUMERS = ("e1", "e2", "e3")
POST_FIT_ALLOWED = {"e1"}   # decision D2: only the identity check may read a post-fit prediction


def main(argv=None, *, repo_root: Path = REPO_ROOT, config_path: Path | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.run_experiment")
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--pair", required=True)
    a = ap.parse_args(argv)
    exp = a.experiment.lower()
    if exp not in SEALED_CONSUMERS:
        print(f"SEAL VIOLATION: {exp} is not a sealed-prediction consumer; E0 runs via "
              "python -m linear_ceiling.e0", file=sys.stderr)
        return 2
    cfg_path = config_path or (repo_root / "config" / "seal.toml")
    try:
        cfg = load_seal_config(cfg_path, repo_root)
    except (OSError, tomllib.TOMLDecodeError, KeyError, ValueError) as e:
        print(f"SEAL VIOLATION: could not load seal config {cfg_path}: {e}", file=sys.stderr)
        return 2
    try:
        rec = require_sealed(a.pair, cfg, repo_root=repo_root, allow_post_fit=exp in POST_FIT_ALLOWED)
    except SealViolation as e:
        print(f"SEAL VIOLATION: {e}", file=sys.stderr)
        return 2
    print(f"seal OK for {a.pair} (pre-fit={rec['sealed_pre_fit']})")
    print(f"{exp} is not implemented in W1 (see ledger entry 0001 for scope); the seal gate is "
          "the only thing this runner does yet", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
