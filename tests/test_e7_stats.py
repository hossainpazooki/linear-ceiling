"""The pinned quantile convention: exact functions of the sorted input, never interpolated."""
import pytest

from linear_ceiling.e7_stats import quantile, summary


def test_lower_nearest_rank_no_interpolation():
    v = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    assert quantile(v, 0.10) == 20        # floor(0.1 * 10) = index 1
    assert quantile(v, 0.90) == 100       # floor(0.9 * 10) = index 9
    assert quantile(v, 0.0) == 10
    assert quantile(v, 1.0) == 100        # clamped to the last element


def test_order_independent():
    assert quantile([3, 1, 2], 0.5) == quantile([1, 2, 3], 0.5) == 2


def test_summary_shape_and_median_convention():
    s = summary([1, 2, 3, 4])
    assert s == {"n": 4, "median": 2.5, "p10": 1, "p90": 4}


def test_empty_refuses_rather_than_nan():
    with pytest.raises(ValueError, match="refusing"):
        summary([])
    with pytest.raises(ValueError, match="refusing"):
        quantile([], 0.5)


def test_probability_out_of_range_refuses():
    with pytest.raises(ValueError):
        quantile([1], 1.5)
