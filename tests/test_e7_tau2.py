"""tau2-bench adapter tests (offline, synthetic fixtures)."""
import json

import pytest

from linear_ceiling.e7_lanes import lane_a
from linear_ceiling.e7_tau2 import agent_of, load_tau2, parse_ts
from linear_ceiling.e7_traces import approx_tokens


def counter(text, content_type="assistant"):
    return approx_tokens(text)


DOC = {
    "info": {"agent_info": {"llm": "o4-mini-2025-04-16"},
             "user_info": {"llm": "gpt-4.1-2025-04-14"}},
    "simulations": [
        {"task_id": "t1", "trial": 0, "reward_info": {"reward": 1.0}, "messages": [
            {"role": "assistant", "content": "hi", "turn_idx": 0,
             "timestamp": "2025-06-05T14:17:59.426683", "usage": None},
            {"role": "user", "content": "help me", "turn_idx": 1,
             "timestamp": "2025-06-05T14:18:00.502950",
             "usage": {"prompt_tokens": 120, "completion_tokens": 45}},
            {"role": "assistant", "content": "", "turn_idx": 2,
             "timestamp": "2025-06-05T14:18:06.335302",
             "tool_calls": [{"id": "c1", "function": {"name": "book", "arguments": {"id": 7}}}],
             "usage": {"prompt_tokens": 3400, "completion_tokens": 20}},
            {"role": "tool", "content": "ok", "turn_idx": 3,
             "timestamp": "2025-06-05T14:18:06.335371"},
        ]},
        {"task_id": "t1", "trial": 1, "reward_info": {"reward": 0.0}, "messages": []},
    ],
}


def test_agent_identity_comes_from_run_info():
    assert agent_of(DOC) == "o4-mini-2025-04-16"
    with pytest.raises(ValueError, match="no info.agent_info.llm"):
        agent_of({"info": {}})


def test_load_tau2_one_trajectory_per_simulation(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps(DOC), encoding="utf-8")
    ts = load_tau2(p, counter)
    assert len(ts) == 1, "a simulation with no messages yields no trajectory"
    t = ts[0]
    assert t.suite == "tau2-bench" and t.agent == "o4-mini-2025-04-16"
    assert t.traj_id == "o4-mini-2025-04-16/t1/0" and t.reward == 1.0
    assert [m.role for m in t.messages] == ["assistant", "user", "assistant", "tool"]


def test_ground_truth_and_timestamps_are_carried(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps(DOC), encoding="utf-8")
    t = load_tau2(p, counter)[0]
    assert [m.reported_tokens for m in t.messages] == [None, 120, 3400, None]
    assert t.has_timestamps and all(m.timestamp for m in t.messages)
    assert t.messages[1].timestamp < t.messages[2].timestamp


def test_tool_calls_are_counted(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps(DOC), encoding="utf-8")
    t = load_tau2(p, counter)[0]
    m = t.messages[2]
    assert m.has_tool_calls and m.tool_names == ("book",) and m.tokens > 0


def test_lane_a_is_not_measurable_despite_a_known_run_level_model(tmp_path):
    """Run-level metadata names the CONFIGURED model, not what served each step, so it cannot
    evidence absence of switching within the run. NOT MEASURABLE, never a measured zero."""
    p = tmp_path / "r.json"
    p.write_text(json.dumps(DOC), encoding="utf-8")
    t = load_tau2(p, counter)[0]
    assert all(m.model is None for m in t.messages)
    a = lane_a(t)
    assert a.measurable is False and a.switches is None


def test_user_simulator_model_never_becomes_a_switch(tmp_path):
    """Two models run per simulation (agent + user simulator). The simulator stands in for a
    human, so counting the alternation would manufacture a Lane A finding from scaffolding."""
    p = tmp_path / "r.json"
    p.write_text(json.dumps(DOC), encoding="utf-8")
    t = load_tau2(p, counter)[0]
    assert lane_a(t).switches is None


def test_parse_ts_refuses_to_guess():
    assert parse_ts("2025-06-05T14:17:59.426683") is not None
    assert parse_ts("not-a-time") is None and parse_ts(None) is None and parse_ts("") is None


def test_refuses_non_tau2_document(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps([{"role": "user"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="not a tau2 results file"):
        load_tau2(p, counter)
