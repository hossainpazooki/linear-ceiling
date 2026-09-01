"""Corpus loader: three suites, nothing dropped silently, entry-0011 units and exclusions."""
import json

import pytest

from linear_ceiling.config import E7Config
from linear_ceiling.e7_corpus import (
    LANE_A_ONLY_AGENTS, agent_of_submission, discover_files, load_corpus,
)
from linear_ceiling.e7_traces import coverage, meets_floor, suite_floor

TOKENIZER = {"encoding": "o200k_base", "default_strategy": "calibrated", "agent_strategy": {},
             "divisors": {"system": 4.817, "user": 4.322, "assistant": 4.005,
                          "tool_output": 2.890, "tool_args": 3.467}}
PRICING = {"provider": "anthropic", "read_mult": 0.1, "write_mult": 1.25,
           "write_mult_1h": 2.0, "ttl_seconds": 300}
THRESHOLDS = {"materiality_fraction": 0.10, "negative_mass_fraction": 0.25,
              "min_trajectories_per_suite": 1, "min_agents_per_suite": 1, "min_suites": 1}

TAU = [{"task_id": 0, "reward": 1.0, "trial": 0, "info": {},
        "traj": [{"role": "user", "content": "u" * 40}, {"role": "assistant", "content": "a" * 80}]}]
TAU2 = {"info": {"agent_info": {"llm": "agent-x"}, "user_info": {"llm": "sim-y"}},
        "simulations": [{"task_id": "t1", "trial": 0, "reward_info": {"reward": 1.0}, "messages": [
            {"role": "assistant", "content": "hi", "usage": None},
            {"role": "user", "content": "help", "usage": {"prompt_tokens": 50}},
            {"role": "assistant", "content": "ok", "usage": {"prompt_tokens": 3000}}]}]}
ROLE_CONTENT = [{"role": "user", "content": "fix it"}, {"role": "assistant", "content": "done"}]


def _lc_human(text):
    return {"id": ["langchain", "schema", "messages", "HumanMessage"], "kwargs": {"content": text, "type": "human"}}


def _lc_ai(text, model_id):
    return {"id": ["langchain", "schema", "messages", "AIMessage"],
            "kwargs": {"content": text, "type": "ai", "response_metadata": {"model_id": model_id}}}


COMPOSIO = [[_lc_human("solve this"), _lc_ai("I will look at the file and fix it", "claude-a")],
            [{"llm_output": {"model_name": "o1-b"}, "run": None,
              "generations": [[{"text": "Summary: look at the file and fix it", "type": "Generation"}]]}]]


def write_corpus(root, *, composio=True, garbage=False):
    (root / "tau-bench").mkdir(parents=True)
    (root / "tau-bench" / "gpt-4o-airline.json").write_text(json.dumps(TAU), encoding="utf-8")
    (root / "tau2-bench").mkdir()
    (root / "tau2-bench" / "agent-x_airline.json").write_text(json.dumps(TAU2), encoding="utf-8")
    flat = root / "swe-bench" / "20240820_honeycomb"
    flat.mkdir(parents=True)
    (flat / "inst-1.json").write_text(json.dumps(ROLE_CONTENT), encoding="utf-8")
    nested = root / "swe-bench" / "20250122_autocoderover" / "inst-2" / "attempt_0"
    nested.mkdir(parents=True)
    (nested / "patching_agent.json").write_text(json.dumps(ROLE_CONTENT), encoding="utf-8")
    (nested / "patch_0.diff").write_text("--- a\n+++ b\n", encoding="utf-8")   # sibling, not a trajectory
    if composio:
        comp = root / "swe-bench" / "20241016_composio_swekit"
        comp.mkdir()
        (comp / "inst-1_traj.json").write_text(json.dumps(COMPOSIO), encoding="utf-8")
    if garbage:
        (flat / "inst-9.json").write_text(json.dumps({"selected_patch": "x"}), encoding="utf-8")


@pytest.fixture
def cfg(tmp_path):
    write_corpus(tmp_path / "traces", garbage=True)
    cfgp = tmp_path / "e7.toml"
    cfgp.write_text("# synthetic\n", encoding="utf-8")
    return E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "results",
                    pricing=PRICING, thresholds=THRESHOLDS, tokenizer=TOKENIZER,
                    lane_b_policy="two-tier-cascade", config_path=cfgp)


def test_agent_strips_the_submission_date():
    assert agent_of_submission("20241016_composio_swekit") == "composio_swekit"
    assert agent_of_submission("20250122_autocoderover-v2.1") == "autocoderover-v2.1"
    assert agent_of_submission("no_date_here") == "no_date_here"


def test_all_three_suites_load_into_one_shape(cfg):
    c = load_corpus(cfg)
    suites = {t.suite for t in c.trajectories}
    assert suites == {"tau-bench", "tau2-bench", "swe-bench"}
    agents = {t.agent for t in c.trajectories}
    assert agents == {"gpt-4o", "agent-x", "honeycomb", "autocoderover", "composio_swekit"}


def test_nested_instance_is_one_trajectory_and_siblings_are_skipped(cfg):
    c = load_corpus(cfg)
    auto = [t for t in c.trajectories if t.agent == "autocoderover"]
    assert len(auto) == 1 and auto[0].task == "inst-2"
    assert not any(u["agent"] == "autocoderover" for u in c.unparsed)


def test_unparsed_is_recorded_with_a_reason_never_dropped(cfg):
    c = load_corpus(cfg)
    assert len(c.unparsed) == 1
    u = c.unparsed[0]
    assert u["traj_id"] == "20240820_honeycomb/inst-9" and u["agent"] == "honeycomb"
    assert "role/content" in u["reason"] and "langchain" in u["reason"]
    assert not any(t.traj_id.endswith("inst-9") for t in c.trajectories)


def test_composio_gets_texts_and_a_unique_dated_traj_id(cfg):
    c = load_corpus(cfg)
    comp = [t for t in c.trajectories if t.agent == "composio_swekit"]
    assert len(comp) == 1
    assert comp[0].traj_id == "20241016_composio_swekit/inst-1_traj"   # dated: two submissions never collide
    assert comp[0].task == "inst-1"
    assert comp[0].traj_id in c.texts and len(c.texts[comp[0].traj_id]) == len(comp[0].messages)
    assert all(t.traj_id not in c.texts for t in c.trajectories if t.agent != "composio_swekit")


def test_task_is_set_on_every_suite(cfg):
    c = load_corpus(cfg)
    assert all(t.task is not None for t in c.trajectories)
    assert {t.task for t in c.trajectories if t.suite == "tau-bench"} == {"airline/0"}
    assert {t.task for t in c.trajectories if t.suite == "tau2-bench"} == {"t1"}


def test_lane_a_only_agents_are_excluded_from_coverage_but_not_lost(cfg):
    c = load_corpus(cfg)
    assert "composio_swekit" in LANE_A_ONLY_AGENTS
    cov = coverage(c.trajectories, exclude_agents=LANE_A_ONLY_AGENTS)
    assert "composio_swekit" not in cov["swe-bench"]["agents"]
    assert cov["swe-bench"] == {"trajectories": 2, "agents": ["autocoderover", "honeycomb"], "tasks": 2}
    full = coverage(c.trajectories)
    assert full["swe-bench"]["trajectories"] == 3      # still there when nobody excludes it


def test_floor_counts_suites_that_clear_it_not_all_suites():
    """Entry 0011: a suite below its own floor is reported but excluded from floor arithmetic."""
    cov = {"a": {"trajectories": 60, "agents": ["x", "y", "z"], "tasks": 60},
           "b": {"trajectories": 60, "agents": ["x", "y", "z"], "tasks": 60},
           "c": {"trajectories": 999, "agents": ["x", "y"], "tasks": 9}}
    th = {"min_trajectories_per_suite": 50, "min_agents_per_suite": 3, "min_suites": 2}
    assert suite_floor(cov, th) == {"a": True, "b": True, "c": False}
    assert meets_floor(cov, th) is True
    th2 = dict(th, min_suites=3)
    assert meets_floor(cov, th2) is False


def test_discover_files_is_the_provenance_set(cfg):
    files = discover_files(cfg.traces_dir)
    names = sorted(f.name for f in files)
    assert "patch_0.diff" in names           # discovered => hashed, even though never parsed
    assert "inst-9.json" in names            # the unparsed one is still provenance
    assert len(files) == len(load_corpus(cfg).files)


def test_empty_traces_dir_refuses(tmp_path):
    (tmp_path / "traces").mkdir()
    c = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r", pricing=PRICING,
                 thresholds=THRESHOLDS, tokenizer=TOKENIZER, lane_b_policy="x",
                 config_path=tmp_path / "e7.toml")
    with pytest.raises(ValueError, match="no trajectories"):
        load_corpus(c)
