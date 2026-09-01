"""Cost-timeline tests with hand-computed expectations (offline, synthetic)."""
import pytest

from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_traces import Msg, Trajectory

PRICING = {"read_mult": 0.1, "write_mult": 1.25, "write_mult_1h": 2.0, "ttl_seconds": 300}


def _t(msgs):
    return Trajectory(suite="s", agent="a", traj_id="t", reward=None, messages=tuple(msgs))


def test_timeline_hand_computed():
    t = _t([
        Msg(role="system", tokens=100),
        Msg(role="user", tokens=10),
        Msg(role="assistant", tokens=20),   # req 1: prefix 110, all new
        Msg(role="user", tokens=5),
        Msg(role="assistant", tokens=8),    # req 2: prefix 135, seen 130 (110 + output 20), new 5
    ])
    rows = timeline(t, PRICING)
    assert [r.input_tokens for r in rows] == [110, 135]
    assert [r.new_input_tokens for r in rows] == [110, 5]
    r1, r2 = rows
    assert r1.cost_warm == pytest.approx(110 * 1.25)          # first request: all cache-write
    assert r2.cost_warm == pytest.approx(130 * 0.1 + 5 * 1.25)
    assert r1.cost_cold == 110 and r2.cost_cold == 135        # cold == no cache, base price
    # warm must be the cheaper bound whenever anything is reused
    assert r2.cost_warm < r2.cost_cold


def test_totals_sums():
    t = _t([Msg(role="user", tokens=4), Msg(role="assistant", tokens=6)])
    tot = totals(timeline(t, PRICING))
    assert tot == {"requests": 1, "input_tokens": 4, "output_tokens": 6,
                   "cost_warm": pytest.approx(4 * 1.25), "cost_cold": 4.0}


def test_no_assistant_turns_means_no_requests():
    assert timeline(_t([Msg(role="system", tokens=50)]), PRICING) == []
