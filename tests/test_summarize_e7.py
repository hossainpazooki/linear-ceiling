"""The summarizer's REFUSALS are the point: a summarizer that cannot fail closed is decoration.

Each test tampers with exactly one thing and proves the refusal names it. Fixtures are
synthetic tau-bench-shaped files written to tmp_path, so these run offline with no real traces.
"""
import json

import pytest

from linear_ceiling.config import E7Config
from linear_ceiling.summarize_e7 import summarize

TOKENIZER = {"encoding": "o200k_base", "default_strategy": "calibrated",
             "agent_strategy": {}, "divisors": {"system": 4.817, "user": 4.322,
                                                "assistant": 4.005, "tool_output": 2.890,
                                                "tool_args": 3.467}}
PRICING = {"provider": "anthropic", "read_mult": 0.1, "write_mult": 1.25,
           "write_mult_1h": 2.0, "ttl_seconds": 300}
THRESHOLDS = {"materiality_fraction": 0.10, "negative_mass_fraction": 0.25,
              "min_trajectories_per_suite": 1, "min_agents_per_suite": 1, "min_suites": 1}

RECORDS = [
    {"task_id": 0, "reward": 1.0, "trial": 0, "info": {},
     "traj": [{"role": "system", "content": "s" * 400},
              {"role": "user", "content": "u" * 40},
              {"role": "assistant", "content": "a" * 80},
              {"role": "assistant", "content": None,
               "tool_calls": [{"id": "c", "type": "function",
                               "function": {"name": "look", "arguments": {"q": "x"}}}]},
              {"role": "tool", "content": "t" * 120},
              {"role": "assistant", "content": "done"}]},
]


@pytest.fixture
def env(tmp_path):
    """Build a config + traces + a genuine report by running the driver's own logic."""
    (tmp_path / "traces" / "tau-bench").mkdir(parents=True)
    (tmp_path / "results").mkdir()
    cfgp = tmp_path / "e7.toml"
    cfgp.write_text("# synthetic\n", encoding="utf-8")
    tf = tmp_path / "traces" / "tau-bench" / "gpt-4o-airline.json"
    tf.write_text(json.dumps(RECORDS), encoding="utf-8")
    cfg = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "results",
                   pricing=PRICING, thresholds=THRESHOLDS, tokenizer=TOKENIZER,
                   lane_b_policy="two-tier-cascade", config_path=cfgp)
    from linear_ceiling import e7 as driver
    # build the report exactly as the driver does, without its git gate
    monkey = driver.assert_ready
    driver.assert_ready = lambda *a, **k: None
    try:
        driver.run(cfg, repo_root=tmp_path)
    finally:
        driver.assert_ready = monkey
    return cfg, tmp_path / "results" / "skeleton_report.json", tf


def _write(p, obj):
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def test_clean_report_summarizes(env):
    cfg, _, _ = env
    md = summarize(cfg)
    assert "recomputed from the raw traces" in md and "gpt-4o" in md


def test_refuses_when_a_trace_file_changed(env):
    cfg, _, tf = env
    doctored = json.loads(tf.read_text(encoding="utf-8"))
    doctored[0]["traj"][1]["content"] = "u" * 41          # one character
    _write(tf, doctored)
    with pytest.raises(ValueError, match="does not match the hash recorded"):
        summarize(cfg)


def test_refuses_on_config_drift(env):
    cfg, _, _ = env
    cfg.config_path.write_text("# changed after the run\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config_sha256 mismatch"):
        summarize(cfg)


def test_refuses_edited_cost_total(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["cost_warm"] *= 0.5   # the number a paper would quote
    _write(rp, rep)
    with pytest.raises(ValueError, match="cost_warm"):
        summarize(cfg)


def test_refuses_edited_token_count(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["input_tokens"] += 1
    _write(rp, rep)
    with pytest.raises(ValueError, match="input_tokens"):
        summarize(cfg)


def test_refuses_lane_a_flipped_to_a_false_zero(env):
    """The most damaging possible edit: unmeasurable relabelled as a measured zero."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["lane_a"] = {"measurable": True, "switches": []}
    _write(rp, rep)
    with pytest.raises(ValueError, match="lane A measurable"):
        summarize(cfg)


def test_refuses_inflated_coverage(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage"]["tau-bench"]["agents"] = ["gpt-4o", "ghost-agent", "phantom"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage"):
        summarize(cfg)


def test_refuses_floor_verdict_that_thresholds_do_not_reproduce(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage_meets_floor"] = not rep["coverage_meets_floor"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage_meets_floor"):
        summarize(cfg)


def test_refuses_nan(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["cost_cold"] = float("nan")
    rp.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    with pytest.raises(ValueError, match="NaN"):
        summarize(cfg)


def test_refuses_missing_provenance(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    del rep["trace_files"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="provenance is unverifiable"):
        summarize(cfg)
