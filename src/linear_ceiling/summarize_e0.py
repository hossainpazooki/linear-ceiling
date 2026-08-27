"""Recompute every E0 number and verdict from results/e0/*.json. Never restate from stdout.

Refuses (ValueError), loudly and never with a NaN or a silent partial, on: nothing has run
yet, config drift since the run (config_sha256 mismatch), a listed unit whose file is missing,
any NaN/inf anywhere in a unit's numbers, a unit file whose hash no longer matches what was
recorded at run time, a recorded per-lambda statistic (`delta`, `median`, `frac_positive`)
that disagrees with what recomputing it from `r2_K`/`r2_V` produces, or a recorded verdict
(unit-level or ladder-level) that the rule does not reproduce from the recomputed numbers.

Statistic recomputation tolerance: `_STAT_TOL = 1e-9`. `delta`/`median`/`frac_positive` are
derived from `r2_K`/`r2_V` by the same float64 arithmetic (`a - b`, `np.median`, `np.mean`)
that produced the recorded values, and Python's `json` module round-trips float64 via `repr`
(exact to the last bit -- see tests/test_summarize_e0.py for a round-trip check), so an
untampered artifact recomputes bit-identically. `_STAT_TOL` exists only to absorb any
platform-dependent summation-order noise in `np.median`/`np.mean`, not to tolerate tampering: a
review-demonstrated tamper (editing a recorded median while leaving `delta`/`r2_K`/`r2_V`
untouched) moved a median by ~4e-3, seven orders of magnitude above this tolerance.

Only operationalization "C" (ledger entry 0003) is implemented; see linear_ceiling.e0 for why
"A"/"B" are refused rather than dispatched to a module (`e0_geometry`) that does not exist.

Check order within a unit matters: NaN is detected before the hash is checked, so an injected
NaN is always reported as "NaN", never masked by the hash mismatch that editing the file to
inject it necessarily also causes (see tests/test_summarize_e0.py for why this is asserted
directly rather than left implicit).

Shape provenance: {sourceRepo: kv-transfer-replication, filePath:
scripts/summarize_hellaswag.py (load_and_validate_records), commitSha: f3594458f73d70a15f195c863d52ea6592f61578}.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E0Config, load_e0_config
from linear_ceiling.e0 import decide_ladder
from linear_ceiling.e0_vocab import decide_pair
from linear_ceiling.hashing import hash_json_file, sha256_file_bytes

_STAT_TOL = 1e-9  # see module docstring: absorbs summation-order noise, not tampering


def _recompute_lambda_stats(name: str, lam: str, block: dict) -> dict:
    """Return `block` with delta/median/frac_positive recomputed from r2_K/r2_V.

    Raises ValueError if any recomputed statistic disagrees with the recorded one beyond
    _STAT_TOL -- this is what closes the hole where a recorded median/frac_positive/delta was
    edited directly (and the unit file's hash refreshed to match) without touching r2_K/r2_V.
    """
    r2k, r2v = block["r2_K"], block["r2_V"]
    if len(r2k) != len(r2v):
        raise ValueError(f"unit {name} lambda {lam}: r2_K and r2_V have different lengths ({len(r2k)} vs {len(r2v)})")
    delta = [a - b for a, b in zip(r2k, r2v)]
    recorded_delta = block["delta"]
    if len(recorded_delta) != len(delta) or any(abs(a - b) > _STAT_TOL for a, b in zip(delta, recorded_delta)):
        raise ValueError(
            f"unit {name} lambda {lam}: recorded delta does not match r2_K - r2_V recomputed from the same file"
        )
    median = float(np.median(delta))
    if abs(median - block["median"]) > _STAT_TOL:
        raise ValueError(
            f"unit {name} lambda {lam}: recomputed median {median} disagrees with recorded median {block['median']}"
        )
    frac_positive = float(np.mean([d > 0 for d in delta]))
    if abs(frac_positive - block["frac_positive"]) > _STAT_TOL:
        raise ValueError(
            f"unit {name} lambda {lam}: recomputed frac_positive {frac_positive} disagrees with "
            f"recorded frac_positive {block['frac_positive']}"
        )
    return {**block, "delta": delta, "median": median, "frac_positive": frac_positive}


def _walk_nan(obj, path="$"):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        raise ValueError(f"NaN/inf at {path}; a run that produced a non-number must not be summarized")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_nan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_nan(v, f"{path}[{i}]")


def _recompute_unit_verdict(op: str, by_lambda: dict, rule: dict) -> str:
    if op != "C":
        raise ValueError(
            f"operationalization {op!r} is not implemented in this repository (see ledger entry "
            "0003, which selected C); there is no rule to recompute this unit's verdict against"
        )
    return decide_pair(by_lambda, rule)  # decide_pair itself is frozen (ledger entry 0003); only its input changed


def summarize(cfg: E0Config) -> str:
    d = cfg.results_dir
    vp = d / "verdict.json"
    if not vp.exists():
        raise ValueError(f"{vp} does not exist; E0 has not run (nothing to summarize)")
    v = json.loads(vp.read_text(encoding="utf-8"))
    if v.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e0.toml changed since the run (config_sha256 mismatch); rerun or restore the config")
    if v.get("operationalization") != cfg.operationalization:
        raise ValueError("operationalization in verdict.json differs from config")
    op, rule = v["operationalization"], v["rule"]
    rows, verdicts = [], {}
    for name in v["required_units"] + v["optional_units"]:
        meta = v["units"].get(name)
        if meta is None:
            raise ValueError(f"unit {name} is listed but absent from verdict.json units")
        f = d / meta["file"]
        if not f.exists():
            raise ValueError(f"unit file for {name} is missing: {f}")
        unit = json.loads(f.read_text(encoding="utf-8"))
        _walk_nan(unit, name)                                    # NaN wins the race over hash mismatch
        if hash_json_file(f) != meta["sha256"]:
            raise ValueError(f"unit file {f.name} does not match the hash recorded at run time")
        # Recompute delta/median/frac_positive from r2_K/r2_V before trusting any of them --
        # the recorded fields are what CLAUDE.md forbids restating unrecomputed into the ledger.
        by_lambda = {
            lam: _recompute_lambda_stats(name, lam, block) for lam, block in unit["by_lambda"].items()
        }
        rec = _recompute_unit_verdict(op, by_lambda, rule)
        if rec != meta["verdict"] or rec != unit["verdict"]:
            raise ValueError(f"recomputed verdict for {name} is {rec}, recorded {meta['verdict']}/{unit['verdict']}")
        verdicts[name] = rec
        cells = " / ".join(f"{b['median']:+.4f} ({b['frac_positive']:.2f})" for b in by_lambda.values())
        rows.append(f"| {name} | {unit['n_tokens']} | {cells} | {rec} |")
    ladder = decide_ladder(verdicts, v["required_units"])
    if ladder != v["verdict"]:
        raise ValueError(f"recomputed ladder verdict {ladder} != recorded {v['verdict']}")
    head = ("| pair | tokens | median delta (frac K>V) per lambda " + " / ".join(str(l) for l in cfg.reg_sweep) +
            " | verdict |\n|---|---|---|---|\n")
    md = (f"E0 operationalization {op}, seed {v['seed']}, package {v['package_version']}, upstream {v['upstream_sha'][:7]}, "
          f"config sha256 {v['config_sha256'][:12]}\n\n" + head + "\n".join(rows) +
          f"\n\nladder verdict: **{ladder}** (required units: {', '.join(v['required_units'])})\n"
          f"verdict.json sha256: {hash_json_file(vp)}\n")
    (d / "summary.md").write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e0")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e0.toml"))
    a = ap.parse_args(argv)
    try:
        print(summarize(load_e0_config(Path(a.config), REPO_ROOT)))
    except ValueError as e:
        print(f"SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
