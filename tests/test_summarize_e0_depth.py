"""Tests for the depth-structure summarizer's own logic (stats, run-length formatting,
cross-lambda consistency). The fail-closed plumbing (hash, NaN, recorded-vs-recomputed
statistics) is inherited from summarize_e0 and tested in tests/test_summarize_e0.py; these
tests cover only what this module adds."""
import numpy as np

from linear_ceiling.summarize_e0_depth import _fmt_layers, depth_stats, exceedance_consistent


def test_depth_stats_values():
    delta = [0.06, 0.0, 0.0, 0.0, 0.01, 0.02, 0.07, 0.12]
    s = depth_stats(delta, delta_separate=0.05)
    assert s["n_layers"] == 8
    assert s["exceed_layers"] == [0, 6, 7]
    assert s["max"] == 0.12
    assert abs(s["median"] - float(np.median(delta))) < 1e-15
    assert abs(s["p90"] - float(np.percentile(delta, 90))) < 1e-15


def test_depth_stats_threshold_is_inclusive():
    # >= delta_separate, matching the SEPARATE bar's own comparison, not a strict >
    s = depth_stats([0.05, 0.049999], delta_separate=0.05)
    assert s["exceed_layers"] == [0]


def test_exceedance_consistent_detects_drift():
    same = {"0.001": {"exceed_layers": [0, 7]}, "0.01": {"exceed_layers": [0, 7]}}
    drift = {"0.001": {"exceed_layers": [0, 7]}, "0.01": {"exceed_layers": [0, 6, 7]}}
    assert exceedance_consistent(same)
    assert not exceedance_consistent(drift)


def test_fmt_layers_run_lengths():
    assert _fmt_layers([]) == "none"
    assert _fmt_layers([0]) == "0"
    assert _fmt_layers([0, 22, 23, 24, 25, 26, 27]) == "0, 22-27"
    assert _fmt_layers([1, 3, 5]) == "1, 3, 5"
