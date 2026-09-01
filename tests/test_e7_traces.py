"""Adapter + coverage tests on a synthetic tau-bench-shaped fixture (offline, no real traces)."""
import json

import pytest

from linear_ceiling.e7_traces import (
    Trajectory, Msg, approx_tokens, coverage, load_tau_bench, tool_arguments_text,
)

FIXTURE = [
    {
        "task_id": 0, "reward": 1.0, "trial": 0, "info": {},
        "traj": [
            {"role": "system", "content": "x" * 40},
            {"role": "user", "content": "y" * 8},
            {"role": "assistant", "content": "plan " * 4},
            {"role": "assistant", "content": None,
             "tool_calls": [{"id": "c1", "type": "function",
                             "function": {"name": "lookup", "arguments": "{\"q\":1}"}}]},
            {"role": "tool", "content": "result"},
            {"role": "assistant", "content": "done"},
        ],
    }
]


def test_load_tau_bench_normalizes(tmp_path):
    p = tmp_path / "gpt-4o-airline.json"
    p.write_text(json.dumps(FIXTURE), encoding="utf-8")
    trajs = load_tau_bench(p, agent="gpt-4o")
    assert len(trajs) == 1
    t = trajs[0]
    assert (t.suite, t.agent, t.reward) == ("tau-bench", "gpt-4o", 1.0)
    assert [m.role for m in t.messages] == ["system", "user", "assistant", "assistant", "tool", "assistant"]
    tool_msg = t.messages[3]
    assert tool_msg.has_tool_calls and tool_msg.tool_names == ("lookup",)
    # null content contributes 0; the call's name+arguments are counted
    assert tool_msg.tokens == approx_tokens("lookup") + approx_tokens('{"q":1}')
    # the real files carry no per-step model or timestamps -- both must read as absent
    assert not t.has_step_model_metadata and not t.has_timestamps


def test_tool_arguments_dict_is_serialized_not_key_counted():
    # The 2026-09-01 defect: tau-bench stores arguments as a str for gpt-4o and a DICT for
    # sonnet. len(dict) is its key count, so a character counter silently undercounted every
    # sonnet tool call. Compact separators match the sibling agent's observed wire format.
    d = {"user_id": "mia_li_3668"}
    assert tool_arguments_text(d) == '{"user_id":"mia_li_3668"}'
    assert len(tool_arguments_text(d)) == 25
    assert approx_tokens(tool_arguments_text(d)) > approx_tokens(str(len(d)))
    assert tool_arguments_text('{"a":1}') == '{"a":1}'   # str passes through unchanged
    assert tool_arguments_text(None) == ""


def test_tool_arguments_refuses_unknown_type():
    with pytest.raises(ValueError, match="unexpected type"):
        tool_arguments_text([1, 2, 3])


def test_dict_and_str_arguments_count_identically(tmp_path):
    """Same call, two storage shapes -> identical token counts (the bug made them differ)."""
    def rec(args):
        return [{"task_id": 0, "reward": 1.0, "trial": 0, "info": {},
                 "traj": [{"role": "assistant", "content": None,
                           "tool_calls": [{"id": "c", "type": "function",
                                           "function": {"name": "book", "arguments": args}}]}]}]
    a = tmp_path / "gpt-4o-x.json"
    b = tmp_path / "sonnet-35-new-x.json"
    a.write_text(json.dumps(rec('{"user_id":"mia_li_3668"}')), encoding="utf-8")
    b.write_text(json.dumps(rec({"user_id": "mia_li_3668"})), encoding="utf-8")
    ta = load_tau_bench(a, agent="gpt-4o")[0].messages[0].tokens
    tb = load_tau_bench(b, agent="sonnet-35-new")[0].messages[0].tokens
    assert ta == tb > 0


def test_load_tau_bench_refuses_wrong_shape(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="expected a JSON list"):
        load_tau_bench(p, agent="x")
    p.write_text(json.dumps([{"task_id": 9, "traj": []}]), encoding="utf-8")
    with pytest.raises(ValueError, match="no traj message list"):
        load_tau_bench(p, agent="x")


def _traj(agent, n=1):
    return [Trajectory(suite="tau-bench", agent=agent, traj_id=f"{agent}/{i}", reward=None,
                       messages=(Msg(role="assistant", tokens=1),)) for i in range(n)]


def test_coverage_counts_agents_not_runs():
    # entry 0007's point: 100 runs of one agent is 100 trajectories but ONE agent
    cov = coverage(_traj("gpt-4o", 100) + _traj("sonnet-35-new", 2))
    assert cov["tau-bench"]["trajectories"] == 102
    assert cov["tau-bench"]["agents"] == ["gpt-4o", "sonnet-35-new"]
