"""E0 runner. Refuses to load any weight matrix until the operationalization and its G1 rule
are set in config/e0.toml AND committed together with ledger/ledger.md (entry 0003) -- that
ordering is what makes the verdict a prediction rather than a rationalisation.

Ledger entry 0003 chose operationalization "C" (the vocabulary-paired screen): units are
ORDERED PAIRS of models, scored by `linear_ceiling.e0_vocab.analyze_pair`. Operationalizations
"A" and "B" (geometry-only, per-model units) were presented as candidates but not chosen, and
their implementation (`linear_ceiling.e0_geometry`) was deliberately never built. `run()`
refuses cleanly for them rather than importing a module that does not exist.
"""
import argparse
import subprocess
from pathlib import Path

from linear_ceiling import REPO_ROOT, UPSTREAM_SHA, __version__
from linear_ceiling.config import E0Config, load_e0_config
from linear_ceiling.e0_vocab import analyze_pair
from linear_ceiling.hashing import canonical_bytes, hash_json_file, sha256_file_bytes
from linear_ceiling.pairs import ordered_pairs, pair_name
from linear_ceiling.rng import make_rng
from linear_ceiling import weights

# Rule-key names only (no import of any operationalization's analysis module) -- this is how
# assert_ready can report a missing key for whichever operationalization config/e0.toml names,
# including the two that are not implemented in this repository.
REQUIRED_RULE_KEYS = {
    "A": ("theta_same", "theta_separate", "p95_cap", "n_random_baseline"),
    "B": ("theta_same", "theta_separate", "p95_cap", "n_random_baseline"),
    "C": ("delta_separate", "delta_same", "layer_fraction", "pair_scope"),
}


def assert_ready(cfg: E0Config, repo_root: Path) -> None:
    if cfg.operationalization == "":
        raise RuntimeError("config/e0.toml: operationalization is unset; write ledger entry 0003 first")
    missing = [k for k in REQUIRED_RULE_KEYS[cfg.operationalization] if k not in cfg.rule]
    if missing:
        raise RuntimeError(f"config/e0.toml [e0.rule] is missing {missing}; the G1 rule must be complete before E0 runs")
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"{rel} is not committed as-is; the rule must be committed (entry 0003) before any matrix is loaded")


def decide_ladder(unit_verdicts: dict, required_units: list) -> str:
    vs = [unit_verdicts[u] for u in required_units]     # KeyError if a required unit is missing: fail closed
    if any(v == "SAME" for v in vs):
        return "SAME"
    if all(v == "SEPARATE" for v in vs):
        return "SEPARATE"
    return "UNRESOLVED"


def _pair_units(cfg: E0Config, include_optional: bool):
    """Units are ordered pairs among the ladder (required) and, when include_optional,
    additionally every ordered pair touching an optional model (reported, never required)."""
    required = [pair_name(a, b) for a, b in ordered_pairs(cfg.ladder)]
    models = list(cfg.ladder) + (list(cfg.optional) if include_optional else [])
    all_pairs = [(pair_name(a, b), a, b) for a, b in ordered_pairs(models)]
    return required, all_pairs


def run(cfg: E0Config, *, repo_root: Path, snapshot_fn=weights.snapshot, include_optional: bool = False) -> Path:
    assert_ready(cfg, repo_root)
    if cfg.operationalization != "C":
        raise RuntimeError(
            f"operationalization {cfg.operationalization!r} was not chosen and is not implemented "
            "in this repository (see ledger entry 0003, which selected C); config/e0.toml must "
            "set operationalization = \"C\" for this runner"
        )
    # Invariant 4: the one seeded generator. cfg.seed is what actually reaches the verdict
    # artifact for provenance; `rng` itself is unused below -- analyze_pair/regularized_cca
    # are deterministic given the weights on operationalization C (no resampling, no
    # held-out split in W1). Built anyway rather than skipped, so a future operationalization
    # or a W2 resampling step has a single obvious place to consume it.
    rng = make_rng(cfg.seed)  # noqa: F841
    required, all_pairs = _pair_units(cfg, include_optional)
    models = sorted({m for _, a, b in all_pairs for m in (a, b)})
    readers = {m: weights.WeightReader(snapshot_fn(m), model_id=m) for m in models}
    out_dir = cfg.results_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    unit_meta, verdicts = {}, {}
    for name, a, b in all_pairs:
        res = analyze_pair(readers[a], readers[b], cfg.reg_sweep, cfg.rule)
        f = out_dir / f"{name}.json"
        f.write_bytes(canonical_bytes(res))
        unit_meta[name] = {"verdict": res["verdict"], "file": f.name, "sha256": hash_json_file(f)}
        verdicts[name] = res["verdict"]
        print(f"E0 {name}: {res['verdict']}")
    verdict = {
        "experiment": "E0", "operationalization": cfg.operationalization, "package_version": __version__,
        "upstream_sha": UPSTREAM_SHA, "config_sha256": sha256_file_bytes(cfg.config_path),
        "seed": cfg.seed, "rule": cfg.rule, "required_units": required,
        "optional_units": [n for n in unit_meta if n not in required],
        "units": unit_meta, "verdict": decide_ladder(verdicts, required),
    }
    vp = out_dir / "verdict.json"
    vp.write_bytes(canonical_bytes(verdict))
    print(f"E0 ladder verdict: {verdict['verdict']} -> {vp}")
    return vp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e0")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e0.toml"))
    ap.add_argument("--include-optional", action="store_true", help="also run the optional (8B) pairs")
    a = ap.parse_args(argv)
    cfg = load_e0_config(Path(a.config), REPO_ROOT)
    try:
        run(cfg, repo_root=REPO_ROOT, include_optional=a.include_optional)
    except RuntimeError as e:
        print(f"E0 REFUSED: {e}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
