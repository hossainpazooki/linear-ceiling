"""Recompute the per-layer depth structure of E0's delta distributions from results/e0/*.json.

Entry 0004 records the per-pair medians; this summarizer records what the median hides: the
per-layer Delta(l) distribution, whose tails exceed the SEPARATE threshold at the ends of the
network in every pair (handoff 2026-08-26 section 2.3). It exists so that a ledger entry can
carry those numbers without violating the rule that no number reaches the ledger except
recomputed from results/ by a summarizer.

Inherits the fail-closed path from summarize_e0 rather than re-implementing it: unit hashes,
NaN refusal, and the recorded-vs-recomputed statistic cross-check all run before any depth
statistic is computed, so a tampered artifact refuses here exactly where it refuses there.

The "same exceedance layers at every lambda" claim is CHECKED, not asserted: the exceedance
set is computed per lambda and the summarizer reports whether the sets are identical across
the sweep, printing the differing sets if they are not.

p90 is numpy's default percentile (linear interpolation), stated here so the number is
reproducible from this line alone.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E0Config, load_e0_config
from linear_ceiling.hashing import hash_json_file, sha256_file_bytes
from linear_ceiling.summarize_e0 import _recompute_lambda_stats, _walk_nan


def depth_stats(delta: list, delta_separate: float) -> dict:
    """Pure depth statistics for one pair at one lambda, from the recomputed delta vector."""
    arr = np.asarray(delta, dtype=np.float64)
    exceed = [int(i) for i, d in enumerate(delta) if d >= delta_separate]
    return {
        "n_layers": int(arr.size),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "max": float(np.max(arr)),
        "exceed_layers": exceed,
    }


def exceedance_consistent(per_lambda: dict) -> bool:
    """True iff the exceedance layer set is identical at every lambda."""
    sets = [tuple(s["exceed_layers"]) for s in per_lambda.values()]
    return len(set(sets)) == 1


def _fmt_layers(layers: list) -> str:
    if not layers:
        return "none"
    runs, start = [], layers[0]
    prev = start
    for x in layers[1:]:
        if x != prev + 1:
            runs.append((start, prev))
            start = x
        prev = x
    runs.append((start, prev))
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def summarize_depth(cfg: E0Config) -> str:
    d = cfg.results_dir
    vp = d / "verdict.json"
    if not vp.exists():
        raise ValueError(f"{vp} does not exist; E0 has not run (nothing to summarize)")
    v = json.loads(vp.read_text(encoding="utf-8"))
    if v.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e0.toml changed since the run (config_sha256 mismatch); rerun or restore the config")
    delta_separate = v["rule"]["delta_separate"]
    report_lam = None
    rows, inconsistencies = [], []
    for name in v["required_units"] + v["optional_units"]:
        meta = v["units"].get(name)
        if meta is None:
            raise ValueError(f"unit {name} is listed but absent from verdict.json units")
        f = d / meta["file"]
        if not f.exists():
            raise ValueError(f"unit file for {name} is missing: {f}")
        unit = json.loads(f.read_text(encoding="utf-8"))
        _walk_nan(unit, name)
        if hash_json_file(f) != meta["sha256"]:
            raise ValueError(f"unit file {f.name} does not match the hash recorded at run time")
        per_lambda = {}
        for lam, block in unit["by_lambda"].items():
            rec = _recompute_lambda_stats(name, lam, block)  # fail-closed: recomputes delta from r2_K/r2_V
            per_lambda[lam] = depth_stats(rec["delta"], delta_separate)
        if not exceedance_consistent(per_lambda):
            inconsistencies.append(
                f"{name}: exceedance layers differ across lambdas: "
                + "; ".join(f"{lam}: [{_fmt_layers(s['exceed_layers'])}]" for lam, s in per_lambda.items())
            )
        lam0 = min(per_lambda, key=float)
        if report_lam is None:
            report_lam = lam0
        elif report_lam != lam0:
            raise ValueError(f"unit {name} sweeps a different lambda grid (smallest {lam0} vs {report_lam})")
        s = per_lambda[lam0]
        rows.append(
            f"| {name} | {s['n_layers']} | {s['median']:+.4f} | {s['p90']:+.4f} | {s['max']:+.4f} "
            f"| {len(s['exceed_layers'])} -- layers {_fmt_layers(s['exceed_layers'])} |"
        )
    consistency_line = (
        "exceedance layer sets are IDENTICAL at every lambda in the sweep (checked per pair)"
        if not inconsistencies
        else "EXCEEDANCE SETS DIFFER ACROSS LAMBDAS:\n" + "\n".join(inconsistencies)
    )
    head = (
        f"| pair | n layers | median | p90 | max | layers with delta >= {delta_separate} (= delta_separate) |\n"
        "|---|---|---|---|---|---|\n"
    )
    md = (
        f"E0 depth structure at lambda {report_lam} (smallest in sweep), "
        f"delta_separate {delta_separate}, config sha256 {v['config_sha256'][:12]}\n\n"
        + head + "\n".join(rows) + "\n\n" + consistency_line
        + f"\nverdict.json sha256: {hash_json_file(vp)}\n"
    )
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e0_depth")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e0.toml"))
    a = ap.parse_args(argv)
    try:
        print(summarize_depth(load_e0_config(Path(a.config), REPO_ROOT)))
    except ValueError as e:
        print(f"DEPTH SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
