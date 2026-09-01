"""Taxonomy classes exactly as registered in entry 0014 (offline, synthetic)."""
import pytest

from linear_ceiling.e7_taxonomy import CLASSES, classify, frequencies, h_e7a
from linear_ceiling.e7_traces import Msg, Trajectory


def _t(msgs, attempts=None, suite="s", agent="a", tid="t"):
    return Trajectory(suite=suite, agent=agent, traj_id=tid, reward=None, messages=tuple(msgs),
                      attempts=attempts)


def test_registered_classes_in_registered_order():
    assert CLASSES == ("model_switch", "rerender_at_switch", "compaction", "idle_expiry", "branch", "edit")


def test_final_transcript_is_unmeasurable_for_everything_but_switch():
    """A role/content trace: no per-step model, no usage, no timestamps, flat layout."""
    t = _t([Msg(role="user", tokens=5), Msg(role="assistant", tokens=5), Msg(role="assistant", tokens=5)])
    c = classify(t, None, 300)
    assert all(c[k] == {"measurable": False, "events": None} for k in CLASSES)


def test_compaction_is_a_decrease_in_reported_prompt_size():
    grow = _t([Msg(role="assistant", tokens=1, reported_tokens=100),
               Msg(role="assistant", tokens=1, reported_tokens=150),
               Msg(role="assistant", tokens=1, reported_tokens=150)])   # equal is not compaction
    assert classify(grow, None, 300)["compaction"] == {"measurable": True, "events": 0}
    shrink = _t([Msg(role="assistant", tokens=1, reported_tokens=100),
                 Msg(role="assistant", tokens=1, reported_tokens=40),
                 Msg(role="assistant", tokens=1, reported_tokens=60),
                 Msg(role="assistant", tokens=1, reported_tokens=20)])
    assert classify(shrink, None, 300)["compaction"] == {"measurable": True, "events": 2}
    one = _t([Msg(role="assistant", tokens=1, reported_tokens=100)])
    assert classify(one, None, 300)["compaction"] == {"measurable": False, "events": None}


def test_idle_expiry_uses_the_ttl_strictly():
    t = _t([Msg(role="assistant", tokens=1, timestamp=0.0),
            Msg(role="assistant", tokens=1, timestamp=300.0),      # exactly TTL: not expired
            Msg(role="assistant", tokens=1, timestamp=601.0)])     # 301 s: expired
    assert classify(t, None, 300)["idle_expiry"] == {"measurable": True, "events": 1}


def test_user_turn_timestamps_do_not_make_it_measurable():
    t = _t([Msg(role="user", tokens=1, timestamp=0.0), Msg(role="assistant", tokens=1, timestamp=1.0),
            Msg(role="user", tokens=1, timestamp=1000.0)])
    assert classify(t, None, 300)["idle_expiry"]["measurable"] is False


def test_branch_counts_extra_attempts_only_when_recorded():
    m = [Msg(role="assistant", tokens=1)]
    assert classify(_t(m, attempts=1), None, 300)["branch"] == {"measurable": True, "events": 0}
    assert classify(_t(m, attempts=3), None, 300)["branch"] == {"measurable": True, "events": 2}
    assert classify(_t(m, attempts=None), None, 300)["branch"] == {"measurable": False, "events": None}


def test_switch_and_rerender_follow_lane_a_and_text_availability():
    sw = _t([Msg(role="assistant", tokens=1, model="m1"), Msg(role="assistant", tokens=1, model="m2")])
    no_text = classify(sw, None, 300)
    assert no_text["model_switch"] == {"measurable": True, "events": 1}
    assert no_text["rerender_at_switch"] == {"measurable": False, "events": None}
    with_text = classify(sw, [{"byte_identical": False}], 300)
    assert with_text["rerender_at_switch"] == {"measurable": True, "events": 1}
    verbatim = classify(sw, [{"byte_identical": True}], 300)
    assert verbatim["rerender_at_switch"] == {"measurable": True, "events": 0}


def test_edit_is_registered_as_never_measurable():
    t = _t([Msg(role="assistant", tokens=1, model="m", reported_tokens=5, timestamp=1.0)], attempts=1)
    assert classify(t, [], 300)["edit"] == {"measurable": False, "events": None}


def test_frequencies_keep_unmeasurable_out_of_both_sides():
    a = _t([Msg(role="assistant", tokens=1, reported_tokens=100), Msg(role="assistant", tokens=1, reported_tokens=50)],
           suite="s", agent="x", tid="1")
    b = _t([Msg(role="assistant", tokens=1)], suite="s", agent="x", tid="2")           # unmeasurable
    c = _t([Msg(role="assistant", tokens=1, reported_tokens=10), Msg(role="assistant", tokens=1, reported_tokens=20)],
           suite="s", agent="y", tid="3")
    per = {t.traj_id: classify(t, None, 300) for t in (a, b, c)}
    f = frequencies(per, [a, b, c])
    assert f["per_agent"]["s/x"]["compaction"] == {"measurable_trajs": 1, "trajs_with_event": 1, "events": 1,
                                                   "not_measurable": 1}
    assert f["per_suite"]["s"]["compaction"] == {"measurable_trajs": 2, "trajs_with_event": 1, "events": 1,
                                                 "not_measurable": 1}
    assert f["pooled"]["edit"] == {"measurable_trajs": 0, "trajs_with_event": 0, "events": 0, "not_measurable": 3}


def test_h_e7a_denominator_is_the_measurable_subset_only():
    meas = _t([Msg(role="assistant", tokens=100, model="m1"), Msg(role="assistant", tokens=100, model="m2")],
              suite="s", agent="x", tid="m")
    unm = _t([Msg(role="assistant", tokens=100)], suite="s", agent="y", tid="u")
    rows = [{"traj_id": "m", "headroom_upper_bound": 90.0}]
    inputs = {"m": 1000, "u": 1_000_000}          # the unmeasurable one must not dilute the ratio
    h = h_e7a([meas, unm], inputs, rows, cutoff=0.10)
    assert h["pooled"]["input_spend"] == 1000 and h["pooled"]["measurable_trajs"] == 1
    assert h["pooled"]["ratio"] == pytest.approx(0.09) and h["pooled"]["below_cutoff"] is True
    assert h["per_suite"]["s"]["ratio"] == pytest.approx(0.09)


def test_h_e7a_with_no_measurable_trajectory_is_not_computable_not_zero():
    unm = _t([Msg(role="assistant", tokens=100)], tid="u")
    h = h_e7a([unm], {"u": 5}, [], cutoff=0.10)
    assert h["pooled"] == {"measurable_trajs": 0, "recoverable_upper_bound": 0.0, "input_spend": 0,
                           "ratio": None, "below_cutoff": None}
