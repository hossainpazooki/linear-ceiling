"""Headroom-measure tests — the measure frozen in ledger entry 0010, with the receiver's
prefill defined as ITS request's prompt (entry 0017 correction). Offline, synthetic."""
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
    t = _traj([Msg(role="assistant", tokens=5, model="m1", request=0),
               Msg(role="assistant", tokens=5, model="m1", request=0)])
    assert measure(t, ["x", "y"], read_mult=0.1) == []


def test_measure_ignores_turns_with_unknown_model():
    t = _traj([Msg(role="assistant", tokens=5, model=None, request=0),
               Msg(role="assistant", tokens=5, model="m2", request=1)])
    assert measure(t, ["x", "y"], read_mult=0.1) == []


def test_measure_refuses_a_switch_without_request_boundaries():
    """The receiver's prefill must never be approximated by the trajectory prefix (0017)."""
    t = _traj([Msg(role="assistant", tokens=100, model="m1"),
               Msg(role="assistant", tokens=50, model="m2")])
    with pytest.raises(ValueError, match="no request boundary"):
        measure(t, ["a b", "a b"], read_mult=0.1)


def test_paid_is_the_receivers_own_request_prompt_not_the_prefix():
    # request 0: the sender's thread (600 tokens of context + its answer);
    # request 1: the receiver's prompt (40 tokens, re-rendered from the sender) + its answer.
    t = _traj([Msg(role="user", tokens=500, request=0),
               Msg(role="assistant", tokens=100, model="m1", request=0),
               Msg(role="user", tokens=40, request=1),
               Msg(role="assistant", tokens=10, model="m2", request=1)])
    texts = ["context words here", "a b c d", "a b c d", "summary"]
    (h,) = measure(t, texts, read_mult=0.1)
    assert isinstance(h, Headroom)
    assert h.sender_model == "m1" and h.receiver_model == "m2"
    assert h.paid_tokens == 40                      # NOT 640: only the receiver's request prompt
    assert h.overlap_fraction == 1.0                # "a b c d" was all produced by the sender side
    assert h.overlap_tokens == pytest.approx(40)
    assert h.residual_tokens == pytest.approx(0)
    assert h.headroom_upper_bound == pytest.approx(40 * 0.9)   # overlap * (1 - read_mult)
    assert h.recoverable_fraction == pytest.approx(0.9)


def test_residual_is_the_new_framing_text():
    t = _traj([Msg(role="assistant", tokens=100, model="m1", request=0),
               Msg(role="user", tokens=100, request=1),
               Msg(role="assistant", tokens=10, model="m2", request=1)])
    (h,) = measure(t, ["a b", "a b NEW NEW", "ok"], read_mult=0.1)
    assert h.paid_tokens == 100
    assert h.overlap_fraction == pytest.approx(0.5)
    assert h.residual_tokens == pytest.approx(50)
    assert h.overlap_tokens + h.residual_tokens == pytest.approx(h.paid_tokens)


def test_receiver_with_an_empty_prompt_is_a_zero_paid_not_a_crash():
    """A response with no visible request prompt (the nested-list shape before the 0017 fix
    looked like this): paid 0, overlap 0 -- recorded, never a prefix guess."""
    t = _traj([Msg(role="assistant", tokens=100, model="m1", request=0),
               Msg(role="assistant", tokens=10, model="m2", request=1)])
    (h,) = measure(t, ["a b", "ok"], read_mult=0.1)
    assert h.paid_tokens == 0 and h.overlap_fraction == 0.0 and h.headroom_upper_bound == 0.0


def test_byte_identical_flag_distinguishes_reuse_from_rerendering():
    verbatim = _traj([Msg(role="assistant", tokens=10, model="m1", request=0),
                      Msg(role="user", tokens=10, request=1),
                      Msg(role="assistant", tokens=10, model="m2", request=1)])
    (h,) = measure(verbatim, ["abc", "PREFIX abc SUFFIX", "r"], read_mult=0.1)
    assert h.byte_identical is True
    (h2,) = measure(verbatim, ["a b c", "a  b   c", "r"], read_mult=0.1)   # re-rendered whitespace
    assert h2.byte_identical is False
    assert h2.overlap_fraction == 1.0, "content overlap survives re-rendering; bytes do not"


def test_misaligned_texts_are_refused():
    t = _traj([Msg(role="assistant", tokens=1, model="m1", request=0)])
    with pytest.raises(ValueError, match="must align"):
        measure(t, ["a", "b"], read_mult=0.1)
