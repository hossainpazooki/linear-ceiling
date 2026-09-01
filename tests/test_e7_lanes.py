"""Lane semantics tests -- the registered rules of entries 0006/0007 (offline, synthetic)."""
from linear_ceiling.e7_lanes import lane_a, lane_b
from linear_ceiling.e7_traces import Msg, Trajectory


def _t(msgs):
    return Trajectory(suite="s", agent="a", traj_id="t", reward=None, messages=tuple(msgs))


def test_lane_a_no_metadata_is_unmeasurable_not_zero():
    # entry 0006: Lane A counts only where per-step metadata exists. tau-bench's case.
    r = lane_a(_t([Msg(role="assistant", tokens=1), Msg(role="assistant", tokens=1)]))
    assert r.measurable is False and r.switches is None


def test_lane_a_partial_metadata_is_unmeasurable():
    r = lane_a(_t([Msg(role="assistant", tokens=1, model="big"), Msg(role="assistant", tokens=1)]))
    assert r.measurable is False and r.switches is None


def test_lane_a_detects_a_real_switch_and_a_real_zero():
    switched = lane_a(_t([
        Msg(role="assistant", tokens=1, model="big"),
        Msg(role="assistant", tokens=1, model="small"),
        Msg(role="assistant", tokens=1, model="small"),
    ]))
    assert switched.measurable and switched.switches == (1,)
    steady = lane_a(_t([Msg(role="assistant", tokens=1, model="big")] * 3))
    assert steady.measurable and steady.switches == ()   # a measured zero, distinct from unmeasurable


def test_lane_b_two_tier_cascade_boundaries():
    # plan, tool, tool, plan -> tiers large, small, small, large -> switches at ordinals 1 and 3
    r = lane_b(_t([
        Msg(role="assistant", tokens=1),
        Msg(role="user", tokens=1),
        Msg(role="assistant", tokens=1, has_tool_calls=True),
        Msg(role="assistant", tokens=1, has_tool_calls=True),
        Msg(role="assistant", tokens=1),
    ]))
    assert r.tiers == ("large", "small", "small", "large")
    assert r.switches == (1, 3)
