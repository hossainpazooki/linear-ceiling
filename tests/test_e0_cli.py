"""E0 CLI tests for operationalization C (the vocabulary-paired screen).

The design brief this repo's task list was written against assumed operationalization A
(units = model short names, `linear_ceiling.e0_geometry.analyze_model`). The operator chose
C instead (ledger entry 0003): `e0_geometry` was deliberately never built. Under C, units are
ORDERED PAIRS (`pairs.pair_name(src, tgt)`), not models -- for a two-model ladder that is two
units (both directions), and `run()` must dispatch to `linear_ceiling.e0_vocab.analyze_pair`.
"""
import json
import re

import pytest

from linear_ceiling.config import load_e0_config
from linear_ceiling.e0 import assert_ready, decide_ladder, run
from tests.conftest import CFG, commit_all, tiny_snapshot

# Vocabulary rows are the CCA samples for C; regularized_cca needs n > max(p, q) where p, q
# are the two models' hidden sizes (32 by default) -- see tests/test_e0_vocab.py::_pair_snapshots,
# which sizes its synthetic vocab at a few hundred rows for the same reason. conftest's default
# CFG has vocab_size=16, which is far too small.
PAIR_CFG = {**CFG, "vocab_size": 200}

TOML_C = '''
seed = 0
operationalization = "C"
[models]
ladder = ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B"]
optional = ["Qwen/Qwen3-4B"]
[e0]
results_dir = "results/e0"
reg_sweep = [0.01]
heldout_frac = 0.2
[e0.rule]
delta_separate = 0.05
delta_same = 0.02
layer_fraction = 0.67
pair_scope = "all"
'''

# A config that sets operationalization = "A" with A's own required rule keys present and
# committed -- used only to prove run() refuses cleanly for an unimplemented operationalization
# (assert_ready must pass so the refusal we observe is run()'s, not assert_ready's).
TOML_A_COMMITTABLE = '''
seed = 0
operationalization = "A"
[models]
ladder = ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B"]
optional = []
[e0]
results_dir = "results/e0"
reg_sweep = [0.01]
heldout_frac = 0.2
[e0.rule]
theta_same = 0.9
theta_separate = 0.5
p95_cap = 0.9
n_random_baseline = 3
'''


def _cfg(repo, text=TOML_C):
    (repo / "config").mkdir(exist_ok=True)
    (repo / "ledger").mkdir(exist_ok=True)
    (repo / "config" / "e0.toml").write_text(text, encoding="utf-8")
    (repo / "ledger" / "ledger.md").write_text("# Ledger\n", encoding="utf-8")
    return load_e0_config(repo / "config" / "e0.toml", repo)


def _pair_snaps(tmp_path, models=("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B")):
    snaps = {}
    for mid in models:
        d, _ = tiny_snapshot(tmp_path, mid.split("/")[1], cfg={**PAIR_CFG, "_name_or_path": mid})
        snaps[mid] = d
    return snaps


def test_decide_ladder():
    assert decide_ladder({"a": "SEPARATE", "b": "SEPARATE", "x": "SAME"}, ["a", "b"]) == "SEPARATE"
    assert decide_ladder({"a": "SEPARATE", "b": "SAME"}, ["a", "b"]) == "SAME"
    assert decide_ladder({"a": "SEPARATE", "b": "UNRESOLVED"}, ["a", "b"]) == "UNRESOLVED"
    with pytest.raises(KeyError):
        decide_ladder({"a": "SEPARATE"}, ["a", "b"])


def test_assert_ready_refuses_unset_or_uncommitted(repo):
    cfg = _cfg(repo, TOML_C.replace('operationalization = "C"', 'operationalization = ""'))
    with pytest.raises(RuntimeError, match="operationalization"):
        assert_ready(cfg, repo)
    cfg = _cfg(repo, TOML_C.replace('pair_scope = "all"\n', ""))
    with pytest.raises(RuntimeError, match="pair_scope"):
        assert_ready(cfg, repo)
    cfg = _cfg(repo)
    with pytest.raises(RuntimeError, match="committed"):
        assert_ready(cfg, repo)          # rule written but not committed
    commit_all(repo, "rule")
    assert_ready(cfg, repo)


def test_run_writes_units_and_verdict(repo, tmp_path):
    cfg = _cfg(repo); commit_all(repo, "rule")
    snaps = _pair_snaps(tmp_path)
    out = run(cfg, repo_root=repo, snapshot_fn=lambda mid, cache_dir=None: snaps[mid])
    v = json.loads(out.read_text(encoding="utf-8"))
    assert v["verdict"] in ("SEPARATE", "SAME", "UNRESOLVED")
    expected = {"qwen3-0.6b-to-1.7b", "qwen3-1.7b-to-0.6b"}
    assert set(v["units"]) == expected
    assert set(v["required_units"]) == expected
    assert v["optional_units"] == []           # include_optional defaulted False: 4B never touched
    for u, meta in v["units"].items():
        assert (repo / "results" / "e0" / meta["file"]).exists()
    assert v["config_sha256"] and v["operationalization"] == "C" and v["seed"] == 0


def test_run_includes_optional_units_but_excludes_them_from_the_ladder(repo, tmp_path):
    cfg = _cfg(repo); commit_all(repo, "rule")
    snaps = _pair_snaps(tmp_path, models=("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B"))
    out = run(cfg, repo_root=repo, snapshot_fn=lambda mid, cache_dir=None: snaps[mid], include_optional=True)
    v = json.loads(out.read_text(encoding="utf-8"))
    required = {"qwen3-0.6b-to-1.7b", "qwen3-1.7b-to-0.6b"}
    assert set(v["required_units"]) == required
    optional = set(v["units"]) - required
    assert optional and optional == set(v["optional_units"])   # 4B-touching pairs, reported, not required
    required_only = {u: m["verdict"] for u, m in v["units"].items() if u in required}
    assert v["verdict"] == decide_ladder(required_only, v["required_units"])


def test_run_refuses_when_not_ready(repo, tmp_path):
    cfg = _cfg(repo)
    with pytest.raises(RuntimeError):
        run(cfg, repo_root=repo, snapshot_fn=lambda mid, cache_dir=None: (_ for _ in ()).throw(AssertionError("must not download")))


def test_run_refuses_unimplemented_operationalization(repo):
    """A and B were never chosen (ledger entry 0003 chose C) and must raise a clear
    RuntimeError, not a bare ModuleNotFoundError from an import of the never-built
    e0_geometry module."""
    cfg = _cfg(repo, TOML_A_COMMITTABLE)
    commit_all(repo, "rule")               # assert_ready must pass so this is run()'s own refusal
    with pytest.raises(RuntimeError, match="not implemented"):
        run(cfg, repo_root=repo, snapshot_fn=lambda mid, cache_dir=None: (_ for _ in ()).throw(AssertionError("must not download")))
