"""Headroom-measure tests — the measure frozen in ledger entry 0010 (offline, synthetic)."""
import pytest

from linear_ceiling.e7_headroom import Headroom, measure, overlap_fraction, word_multiset
from linear_ceiling.e7_traces import Msg, Trajectory


def _traj(msgs):
    return Trajectory(suite="s", agent="a", traj_id="t", reward=None, messages=tuple(msgs))


def test_overlap_fraction_bounds():
    assert overlap_fraction("a b c", "a b c") == 1.0
    assert overlap_fraction("", "a b") == 0.0
    assert overlap_fraction("a b", "") == 0.0          # empty receiver is 0, never a crash
    assert overlap_fraction("x y", "a b") == 0.0


def test_overlap_is_multiset_not_set():
    """A phrase repeated twice on the receiving side is only credited twice if the sender
    produced it twice -- set intersection would score this 1.0 and overstate headroom."""
    assert overlap_fraction("a", "a a") == 0.5
    assert overlap_fraction("a a", "a a") == 1.0
    assert word_multiset("a a b")["a"] == 2


def test_measure_reports_nothing_without_a_switch():
    t = _traj([Msg(role="assistant", tokens=5, model="m1"),
               Msg(role="assistant", tokens=5, model="m1")])
    assert measure(t, ["x", "y"], read_mult=0.1) == []


def test_measure_ignores_turns_with_unknown_model():
    t = _traj([Msg(role="assistant", tokens=5, model=None),
               Msg(role="assistant", tokens=5, model="m2")])
    assert measure(t, ["x", "y"], read_mult=0.1) == []


def test_measure_computes_the_registered_formula():
    # sender says "a b c d"; receiver prompt repeats it verbatim -> overlap 1.0
    t = _traj([Msg(role="assistant", tokens=100, model="m1"),
               Msg(role="assistant", tokens=50, model="m2")])
    (h,) = measure(t, ["a b c d", "a b c d"], read_mult=0.1)
    assert isinstance(h, Headroom)
    assert h.sender_model == "m1" and h.receiver_model == "m2"
    assert h.paid_tokens == 100                     # everything before the receiving turn
    assert h.overlap_fraction == 1.0
    assert h.overlap_tokens == pytest.approx(100)
    assert h.residual_tokens == pytest.approx(0)
    assert h.headroom_upper_bound == pytest.approx(100 * 0.9)   # overlap * (1 - read_mult)
    assert h.recoverable_fraction == pytest.approx(0.9)


def test_residual_is_the_new_framing_text():
    t = _traj([Msg(role="assistant", tokens=100, model="m1"),
               Msg(role="assistant", tokens=10, model="m2")])
    (h,) = measure(t, ["a b", "a b NEW NEW"], read_mult=0.1)
    assert h.overlap_fraction == pytest.approx(0.5)
    assert h.residual_tokens == pytest.approx(50)
    assert h.overlap_tokens + h.residual_tokens == pytest.approx(h.paid_tokens)


def test_byte_identical_flag_distinguishes_reuse_from_rerendering():
    verbatim = _traj([Msg(role="assistant", tokens=10, model="m1"),
                      Msg(role="assistant", tokens=10, model="m2")])
    (h,) = measure(verbatim, ["abc", "PREFIX abc SUFFIX"], read_mult=0.1)
    assert h.byte_identical is True
    (h2,) = measure(verbatim, ["a b c", "a  b   c"], read_mult=0.1)   # re-rendered whitespace
    assert h2.byte_identical is False
    assert h2.overlap_fraction == 1.0, "content overlap survives re-rendering; bytes do not"


def test_misaligned_texts_are_refused():
    t = _traj([Msg(role="assistant", tokens=1, model="m1")])
    with pytest.raises(ValueError, match="must align"):
        measure(t, ["a", "b"], read_mult=0.1)
