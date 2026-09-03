"""E9 alignment (entry 0019): handoff extraction, matched blocks, exclusions. Offline."""
import json

import numpy as np
import pytest

from linear_ceiling.e9_align import (
    Handoff, align, handoffs_from, load_handoffs, matching_pairs, write_alignment,
)
from linear_ceiling.e7_traces import Msg, Trajectory


def _traj(msgs, tid="sub/inst"):
    return Trajectory(suite="swe-bench", agent="a", traj_id=tid, reward=None, messages=tuple(msgs))


def words(text):
    return [hash(w) % 997 for w in text.split()]


def test_handoffs_use_the_request_level_slices_of_0017():
    t = _traj([Msg(role="user", tokens=1, request=0),
               Msg(role="assistant", tokens=1, model="claude", request=0),
               Msg(role="user", tokens=1, request=1),
               Msg(role="assistant", tokens=1, model="o1", request=1),
               Msg(role="assistant", tokens=1, model="o1", request=2)])
    texts = ["ctx", "answer", "rerender", "summary", "more"]
    hs = handoffs_from(t, texts)
    assert len(hs) == 1
    h = hs[0]
    assert h.sender_model == "claude" and h.receiver_model == "o1" and h.switch_index == 1
    assert h.sender_text == "ctx\nanswer"          # everything the sender processed, newline-joined
    assert h.receiver_text == "rerender"            # ITS request prompt only -- response excluded


def test_handoffs_refuse_without_request_boundaries():
    t = _traj([Msg(role="assistant", tokens=1, model="m1"),
               Msg(role="assistant", tokens=1, model="m2")])
    with pytest.raises(ValueError, match="request boundary"):
        handoffs_from(t, ["a", "b"])


def test_matching_pairs_is_a_common_subsequence_in_order():
    a = [1, 2, 3, 4, 5, 6]
    b = [9, 2, 3, 9, 5, 6]
    p = matching_pairs(a, b)
    assert p.tolist() == [[1, 1], [2, 2], [4, 4], [5, 5]]
    assert all(a[i] == b[j] for i, j in p.tolist())
    # strictly increasing in both coordinates: a subsequence, never a bag
    assert (np.diff(p[:, 0]) > 0).all() and (np.diff(p[:, 1]) > 0).all()


def test_align_excludes_over_cap_and_counts_it():
    h = Handoff("id", "t", 1, "m1", "m2", "w " * 100, "w " * 10)
    rec, s, r, p = align(h, words, context_cap=50)
    assert rec.excluded and "S exceeds context cap 50" in rec.reason
    assert s is None and r is None and p is None
    assert rec.n_sender == 100 and rec.n_receiver == 10 and rec.n_matched == 0
    ok, _, _, p2 = align(h, words, context_cap=200)
    assert not ok.excluded and p2.shape[0] == 10          # all receiver tokens match


def test_align_hashes_the_texts():
    h1 = Handoff("id", "t", 1, "m1", "m2", "a b", "a")
    h2 = Handoff("id", "t", 1, "m1", "m2", "a b", "b")
    assert align(h1, words, 100)[0].text_sha256 != align(h2, words, 100)[0].text_sha256


def test_write_alignment_roundtrip(tmp_path):
    h = Handoff("sub/inst_traj#3", "sub/inst_traj", 3, "m1", "m2", "a b c", "a b")
    rec, s, r, p = align(h, words, 100)
    npz = write_alignment(tmp_path, rec, s, r, p)
    z = np.load(npz)
    assert z["sender"].tolist() == words("a b c") and z["pairs"].shape == (2, 2)
    j = json.loads(npz.with_suffix(".json").read_text(encoding="utf-8"))
    assert j["handoff_id"] == "sub/inst_traj#3" and j["n_matched"] == 2 and not j["excluded"]


def test_load_handoffs_reads_both_composio_shapes(tmp_path):
    from tests.test_e7_corpus import COMPOSIO
    flat = tmp_path / "20241016_x"
    flat.mkdir()
    (flat / "a_traj.json").write_text(json.dumps(COMPOSIO), encoding="utf-8")
    nested = tmp_path / "20241025_x"
    nested.mkdir()
    # 20241025 shape: [ [prompt nodes...], LLMResult ]
    wrapped = [[[n for n in sub if "generations" not in n]] + [n for n in sub if "generations" in n]
               for sub in COMPOSIO]
    (nested / "b_traj.json").write_text(json.dumps(wrapped), encoding="utf-8")
    hs = load_handoffs([flat, nested], lambda t, ct="assistant": 0)
    assert len(hs) == 2
    assert all(h.sender_model == "claude-a" and h.receiver_model == "o1-b" for h in hs)
    assert all("solve" in h.sender_text for h in hs)


def test_coverage_comparison_groups_included_and_excluded_and_joins_0018_rows():
    """Entry 0025 (review finding 1)."""
    from linear_ceiling.e7_stats import summary
    from linear_ceiling.e9_align import coverage_comparison
    recs = [
        {"handoff_id": "s/a_traj#1", "n_sender": 100, "n_receiver": 50, "n_matched": 40, "excluded": False, "reason": None, "text_sha256": "x"},
        {"handoff_id": "s/a_traj#2", "n_sender": 200, "n_receiver": 60, "n_matched": 40, "excluded": False, "reason": None, "text_sha256": "x"},
        {"handoff_id": "s/b_traj#3", "n_sender": 40000, "n_receiver": 70, "n_matched": 0, "excluded": True, "reason": "S exceeds context cap 32768", "text_sha256": "x"},
        {"handoff_id": "s/b_traj#4", "n_sender": 500, "n_receiver": 0, "n_matched": 0, "excluded": True, "reason": "receiver prompt is empty in the trace", "text_sha256": "x"},
    ]
    rows = [{"traj_id": "s/a_traj", "switch_index": 1, "overlap_fraction": 0.9, "recoverable_fraction": 0.8},
            {"traj_id": "s/a_traj", "switch_index": 2, "overlap_fraction": 0.7, "recoverable_fraction": 0.6},
            {"traj_id": "s/b_traj", "switch_index": 3, "overlap_fraction": 0.5, "recoverable_fraction": 0.4}]
    out = coverage_comparison(recs, rows, summary)
    assert out["n"] == {"included": 2, "excluded_long": 1, "excluded_empty_r": 1} and out["unmatched_0018_rows"] == 0
    assert out["included"]["n_sender"]["median"] == 150 and out["included"]["overlap_fraction_0018"]["median"] == pytest.approx(0.8)
    assert out["excluded_long"]["n_sender"]["median"] == 40000 and out["excluded_long"]["recoverable_fraction_0018"]["median"] == 0.4
    out2 = coverage_comparison(recs, rows[:1], summary)
    assert out2["unmatched_0018_rows"] == 2 and out2["excluded_long"]["overlap_fraction_0018"] is None   # never a zero


def test_align_excludes_an_empty_receiver_prompt():
    """A switch whose request prompt is invisible (paid 0) has nothing to measure."""
    h = Handoff("id", "t", 1, "m1", "m2", "a b c", "")
    rec, s, r, p = align(h, words, context_cap=100)
    assert rec.excluded and rec.reason == "receiver prompt is empty in the trace"
    assert rec.n_receiver == 0 and s is None
