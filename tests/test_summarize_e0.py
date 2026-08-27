"""Fail-closed summarizer tests for operationalization C.

Each test below isolates exactly one refusal mode. A naive port of the brief's A-oriented
test would mutate a unit's on-disk JSON and expect a specific downstream error (NaN,
verdict-mismatch) without realizing that any content edit also changes that file's hash --
so an implementation that checks the hash would (correctly) refuse on hash-mismatch instead
of ever reaching the NaN/verdict-mismatch logic being tested. Two fixes applied here:
  - the NaN check runs before the hash check (so an injected NaN is always caught first,
    hash notwithstanding) -- covered directly by test_refuses_nan, with the hash check
    covered separately and un-confounded by test_refuses_unit_hash_mismatch.
  - the recomputed-verdict-mismatch test explicitly re-syncs the recorded sha256 after its
    edit (via _patch_unit_and_resync_hash) so the mismatch it is checking for is the only
    one triggered.
"""
import json
import re

import pytest

from linear_ceiling.hashing import hash_json_file
from linear_ceiling.summarize_e0 import summarize
from tests.conftest import commit_all
from tests.test_e0_cli import _cfg, _pair_snaps
from linear_ceiling.e0 import run


def _ran(repo, tmp_path):
    cfg = _cfg(repo); commit_all(repo, "rule")
    snaps = _pair_snaps(tmp_path)
    run(cfg, repo_root=repo, snapshot_fn=lambda mid, cache_dir=None: snaps[mid])
    return cfg


def _first_unit_name(repo) -> str:
    v = json.loads((repo / "results" / "e0" / "verdict.json").read_text(encoding="utf-8"))
    return v["required_units"][0]


def _patch_unit_and_resync_hash(repo, name, transform) -> None:
    f = repo / "results" / "e0" / f"{name}.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    transform(d)
    f.write_text(json.dumps(d), encoding="utf-8")
    vp = repo / "results" / "e0" / "verdict.json"
    v = json.loads(vp.read_text(encoding="utf-8"))
    v["units"][name]["sha256"] = hash_json_file(f)     # isolate: only `transform`'s effect should fire
    vp.write_text(json.dumps(v), encoding="utf-8")


def test_summary_renders_every_unit_and_verdict(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    md = summarize(cfg)
    assert "qwen3-0.6b-to-1.7b" in md and "qwen3-1.7b-to-0.6b" in md and "ladder verdict:" in md
    assert (repo / "results" / "e0" / "summary.md").exists()


def test_refuses_missing_unit_file(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    name = _first_unit_name(repo)
    (repo / "results" / "e0" / f"{name}.json").unlink()
    with pytest.raises(ValueError, match=re.escape(name)):
        summarize(cfg)


def test_refuses_config_drift(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    p = repo / "config" / "e0.toml"
    p.write_text(p.read_text(encoding="utf-8") + "\n# edited after the run\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config"):
        summarize(cfg)


def test_refuses_unit_hash_mismatch(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    name = _first_unit_name(repo)
    f = repo / "results" / "e0" / f"{name}.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d["n_tokens"] = d["n_tokens"] + 1        # tamper WITHOUT re-syncing the recorded hash
    f.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        summarize(cfg)


def test_refuses_nan(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    name = _first_unit_name(repo)
    f = repo / "results" / "e0" / f"{name}.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    lam_key = next(iter(d["by_lambda"]))
    d["by_lambda"][lam_key]["median"] = float("nan")
    f.write_text(json.dumps(d, allow_nan=True), encoding="utf-8")   # hash now also mismatches;
    with pytest.raises(ValueError, match="NaN"):                    # NaN must still win the race
        summarize(cfg)


def test_refuses_recomputed_verdict_mismatch(repo, tmp_path):
    cfg = _ran(repo, tmp_path)
    v = json.loads((repo / "results" / "e0" / "verdict.json").read_text(encoding="utf-8"))
    name = v["required_units"][0]
    recorded = v["units"][name]["verdict"]
    target = "SAME" if recorded != "SAME" else "SEPARATE"

    def _force(d):
        for b in d["by_lambda"].values():
            n = len(b["r2_K"])
            # Rewrite r2_K/r2_V/delta/median/frac_positive together and internally consistent
            # (median and frac_positive are recomputed from delta = r2_K - r2_V by summarize()
            # since I1 was fixed), so the only mismatch this forces is the unit-level `verdict`
            # left below -- not a delta/median/frac_positive recomputation mismatch.
            delta = [0.1] * n if target == "SEPARATE" else [0.0] * n  # clears delta_separate=0.05 / under delta_same=0.02
            b["r2_K"], b["r2_V"], b["delta"] = delta, [0.0] * n, delta
            b["median"] = 0.1 if target == "SEPARATE" else 0.0
            b["frac_positive"] = 1.0 if target == "SEPARATE" else 0.0
        # d["verdict"] deliberately left as recorded -- that's the mismatch under test

    _patch_unit_and_resync_hash(repo, name, _force)
    with pytest.raises(ValueError, match="verdict"):
        summarize(cfg)


def test_refuses_when_nothing_ran(repo):
    cfg = _cfg(repo)
    with pytest.raises(ValueError, match="verdict.json"):
        summarize(cfg)


def test_refuses_median_inconsistent_with_delta(repo, tmp_path):
    """I1 regression: a tampered `median` must be refused even when `delta`/`r2_K`/`r2_V`
    are left untouched and the unit file's recorded hash is refreshed to match -- this is
    exactly the tamper the final review demonstrated fooling the pre-fix summarizer (it
    published a fabricated `+0.0001 (0.10)` cell where the true, still-on-disk values were
    `+0.0043`/`0.72`).
    """
    cfg = _ran(repo, tmp_path)
    name = _first_unit_name(repo)

    def _tamper_median_only(d):
        lam_key = next(iter(d["by_lambda"]))
        d["by_lambda"][lam_key]["median"] = 0.0001   # delta/r2_K/r2_V untouched -- inconsistent

    _patch_unit_and_resync_hash(repo, name, _tamper_median_only)
    with pytest.raises(ValueError, match="median"):
        summarize(cfg)


def test_recomputed_stats_match_real_run(repo, tmp_path):
    """Today's real artifacts must pass the new recomputation cleanly (I1 fix must not
    change any published number): every unit's delta/median/frac_positive as recomputed
    from r2_K/r2_V must equal the recorded values, and the rendered table must show them.
    """
    cfg = _ran(repo, tmp_path)
    md = summarize(cfg)
    name = _first_unit_name(repo)
    f = repo / "results" / "e0" / f"{name}.json"
    unit = json.loads(f.read_text(encoding="utf-8"))
    for lam, block in unit["by_lambda"].items():
        recomputed_delta = [a - b for a, b in zip(block["r2_K"], block["r2_V"])]
        assert recomputed_delta == block["delta"]
    assert f"{unit['by_lambda'][next(iter(unit['by_lambda']))]['median']:+.4f}" in md
