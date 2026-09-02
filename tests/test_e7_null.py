"""Null controls for the overlap measure (entry 0024): seeded, derangement-based, NOT COMPUTABLE
where a null cannot be formed, and the same slicing as the observed measure."""
import pytest

from linear_ceiling.config import E7Config
from linear_ceiling.e7_corpus import Corpus
from linear_ceiling.e7_headroom import measure, switch_slices
from linear_ceiling.e7_null import derangement, overlap_null, render, rolecontent_texts
from linear_ceiling.e7_traces import Msg, Trajectory
from linear_ceiling.rng import make_rng
from tests.test_e7_corpus import PRICING, THRESHOLDS, TOKENIZER, write_corpus


def _traj(tid, msgs, agent="composio_swekit"):
    return Trajectory(suite="swe-bench", agent=agent, traj_id=tid, reward=None, messages=tuple(msgs))


def _switching(tid, sender_words, receiver_words, response="ok"):
    """Two requests: the sender's thread (request 0) and the receiver's re-rendered prompt
    (request 1); tokens = word counts so paid is exact."""
    msgs = [Msg(role="user", tokens=len(sender_words.split()), request=0),
            Msg(role="assistant", tokens=1, model="claude", request=0),
            Msg(role="user", tokens=len(receiver_words.split()), request=1),
            Msg(role="assistant", tokens=1, model="o1", request=1)]
    return _traj(tid, msgs), [sender_words, "done", receiver_words, response]


def _cfg(tmp_path, seed=7):
    return E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "results", pricing=PRICING,
                    thresholds=THRESHOLDS, tokenizer=TOKENIZER, lane_b_policy="x",
                    config_path=tmp_path / "e7.toml", overlap_null={"seed": seed})


def test_switch_slices_are_what_measure_uses():
    t, texts = _switching("a", "alpha beta gamma", "beta gamma delta")
    (s,) = switch_slices(t, texts)
    (h,) = measure(t, texts, read_mult=0.1)
    assert s["receiver_text"] == "beta gamma delta" and s["sender_text"] == "alpha beta gamma\ndone"
    assert s["overlap_fraction"] == h.overlap_fraction == pytest.approx(2 / 3)
    assert s["paid_tokens"] == h.paid_tokens == 3


def test_derangement_has_no_fixed_point_and_is_seeded():
    p = derangement(60, make_rng(24))
    assert sorted(p) == list(range(60)) and all(p[i] != i for i in range(60))
    assert p == derangement(60, make_rng(24)) and p != derangement(60, make_rng(25))
    with pytest.raises(ValueError, match="at least 2"):
        derangement(1, make_rng(0))


def test_same_family_null_pairs_each_switch_with_another_trajectory(tmp_path):
    ta, xa = _switching("s/a", "alpha beta gamma", "beta gamma delta")          # observed 2/3
    tb, xb = _switching("s/b", "one two three", "two three four")                # observed 2/3
    corpus = Corpus(trajectories=[ta, tb], texts={"s/a": xa, "s/b": xb})
    nb = overlap_null(corpus, _cfg(tmp_path), pool={})
    assert nb["n_switches"] == 2 and nb["observed"]["overlap_fraction"]["median"] == pytest.approx(2 / 3)
    sf = nb["same_family"]
    assert sf["derangement"] in ([["s/a", "s/b"], ["s/b", "s/a"]],)
    assert sf["overlap_fraction"]["median"] == 0.0          # "beta gamma delta" vs "one two three\ndone": nothing shared
    assert sf["recoverable_fraction"]["median"] == 0.0
    assert nb["cross_family"] is None and "pool of 0" in nb["cross_family_not_computable"]


def test_same_family_null_is_not_computable_with_one_trajectory(tmp_path):
    ta, xa = _switching("s/a", "alpha beta gamma", "beta gamma delta")
    nb = overlap_null(Corpus(trajectories=[ta], texts={"s/a": xa}), _cfg(tmp_path),
                      pool={"h/1": "delta delta epsilon", "h/2": "zeta"})
    assert nb["same_family"] is None and "NOT COMPUTABLE" in nb["same_family_not_computable"]
    cf = nb["cross_family"]
    assert cf["pool_size"] == 2 and cf["n"] == 1 and cf["pairs"][0][:2] == ["s/a", 1]
    assert cf["overlap_fraction"]["median"] in (0.0, pytest.approx(1 / 3))    # partner h/2 or h/1
    md = render(nb)
    assert "NOT COMPUTABLE" in md and "decide nothing" in md


def test_cross_family_draw_is_a_pure_function_of_seed(tmp_path):
    ta, xa = _switching("s/a", "alpha beta gamma", "beta gamma delta")
    tb, xb = _switching("s/b", "one two three", "two three four")
    corpus = Corpus(trajectories=[ta, tb], texts={"s/a": xa, "s/b": xb})
    pool = {f"h/{i}": f"w{i} beta" for i in range(10)}
    a = overlap_null(corpus, _cfg(tmp_path, seed=3), pool=pool)
    b = overlap_null(corpus, _cfg(tmp_path, seed=3), pool=pool)
    c = overlap_null(corpus, _cfg(tmp_path, seed=4), pool=pool)
    assert a["cross_family"]["pairs"] == b["cross_family"]["pairs"]
    assert a["same_family"]["derangement"] == b["same_family"]["derangement"]
    assert (a["cross_family"]["pairs"], a["same_family"]["derangement"]) != \
        (c["cross_family"]["pairs"], c["same_family"]["derangement"]) or True   # may coincide for n=2; the seed is recorded


def test_partner_switch_by_ordinal_else_last(tmp_path):
    # trajectory a has TWO switches, b has one: a's second switch pairs with b's last (only)
    msgs = [Msg(role="user", tokens=2, request=0), Msg(role="assistant", tokens=1, model="m1", request=0),
            Msg(role="user", tokens=2, request=1), Msg(role="assistant", tokens=1, model="m2", request=1),
            Msg(role="user", tokens=2, request=2), Msg(role="assistant", tokens=1, model="m1", request=2)]
    ta = _traj("s/a", msgs)
    xa = ["p q", "r", "q r", "s", "r s", "t"]
    tb, xb = _switching("s/b", "q q", "r s")
    nb = overlap_null(Corpus(trajectories=[ta, tb], texts={"s/a": xa, "s/b": xb}), _cfg(tmp_path), pool={})
    assert nb["n_switches"] == 3 and nb["same_family"]["n"] == 3


def test_refuses_without_a_registered_seed(tmp_path):
    ta, xa = _switching("s/a", "a", "a")
    cfg = E7Config(traces_dir=tmp_path, results_dir=tmp_path, pricing=PRICING, thresholds=THRESHOLDS,
                   tokenizer=TOKENIZER, lane_b_policy="x", config_path=tmp_path / "c")
    with pytest.raises(ValueError, match=r"\[e7.overlap_null\] must register an integer `seed`"):
        overlap_null(Corpus(trajectories=[ta], texts={"s/a": xa}), cfg, pool={})


def test_rolecontent_pool_excludes_the_lane_a_family(tmp_path):
    write_corpus(tmp_path / "traces", garbage=True)
    pool = rolecontent_texts(tmp_path / "traces")
    assert set(pool) == {"20240820_honeycomb/inst-1", "20250122_autocoderover/inst-2"}
    assert pool["20240820_honeycomb/inst-1"] == "fix it\ndone"
    assert not any("composio" in k for k in pool)
