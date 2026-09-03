"""Per-token E9 statistics (entry 0023): the exact bridge, f*, seam distance, null pairing, band."""
import numpy as np
import pytest

from linear_ceiling.e9_pertoken import (
    SEAM_BIN_LABELS, band_outcome, centered_delta, f_star, layer_mean, null_pairs, own_norm_delta,
    seam_bin, seam_distance, token_mean,
)
from linear_ceiling.rng import make_rng


def test_centered_delta_token_mean_is_one_minus_r2_exactly():
    rng = np.random.default_rng(0)
    n, L, H = 40, 3, 2
    sq = rng.gamma(2.0, size=(n, L, H))
    sst = rng.uniform(50, 100, size=(L, H))
    d = centered_delta(sq, sst, n)
    r2 = 1 - sq.sum(0) / sst
    assert np.allclose(d.mean(0), 1 - r2, atol=1e-12)
    assert token_mean(d).shape == (n,) and layer_mean(d).shape == (n, L)
    assert token_mean(d).mean() == pytest.approx(1 - r2.mean())
    with pytest.raises(ValueError, match="not positive"):
        centered_delta(sq, np.zeros((L, H)), n)
    with pytest.raises(ValueError, match="shape mismatch"):
        centered_delta(sq, sst, n + 1)


def test_own_norm_delta_pools_heads_and_refuses_zero_reference():
    sq = np.ones((5, 2, 3)); ref = np.full((5, 2, 3), 2.0)
    assert np.allclose(own_norm_delta(sq, ref), 0.5)
    ref[0, 0] = 0.0
    with pytest.raises(ValueError, match="zero reference norm"):
        own_norm_delta(sq, ref)


def test_f_star_is_the_smallest_removed_fraction_and_zero_at_the_mean():
    d = np.array([0.1, 0.2, 0.3, 0.4, 5.0])
    assert f_star(d, d.mean()) == 0.0                      # tau = own mean -> nothing to remove
    assert f_star(d, 0.25) == pytest.approx(0.2)           # drop the 5.0: mean of the rest 0.25
    assert f_star(d, 0.2) == pytest.approx(0.4)            # drop 5.0 and 0.4: mean 0.2
    assert f_star(d, 0.0) == 1.0                           # nothing qualifies
    assert f_star(d, float(np.median(d))) > 0.0            # a median tau is NOT self-consistent
    assert f_star(np.zeros(3), 0.0) == 0.0
    with pytest.raises(ValueError):
        f_star(np.zeros(0), 0.1)
    with pytest.raises(ValueError):
        f_star(d, -1.0)


def test_band_outcome_edges():
    rule = {"holds_max": 0.15, "degrades_min": 0.50}
    assert band_outcome(0.15, rule) == "HOLDS" and band_outcome(0.0, rule) == "HOLDS"
    assert band_outcome(0.50, rule) == "DEGRADES" and band_outcome(1.0, rule) == "DEGRADES"
    assert band_outcome(0.3, rule) == "UNRESOLVED"


def test_seam_distance_counts_positions_strictly_between():
    # receiver length 10; matched R positions 0..3 and 6..9 (S contiguous), 4-5 unmatched
    pairs = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [10, 6], [11, 7], [12, 8], [13, 9]])
    b = seam_distance(pairs, 10)
    assert b.tolist() == [3, 2, 1, 0, 0, 1, 2, 3]
    # a reordering seam: R 0..3 matched but S jumps between R=1 and R=2
    pairs = np.array([[0, 0], [1, 1], [7, 2], [8, 3]])
    assert seam_distance(pairs, 4).tolist() == [1, 0, 0, 1]
    # no seam at all: b = n_receiver for every token
    pairs = np.array([[5, 0], [6, 1], [7, 2]])
    assert seam_distance(pairs, 3).tolist() == [3, 3, 3]
    # order of pairs does not matter
    sh = np.array([[12, 8], [0, 0], [3, 3], [11, 7], [1, 1], [13, 9], [2, 2], [10, 6]])
    assert seam_distance(sh, 10).tolist() == [2, 3, 0, 1, 2, 3, 1, 0]
    assert seam_distance(np.zeros((0, 2)), 5).tolist() == []
    with pytest.raises(ValueError):
        seam_distance(np.array([[0, 0], [1, 0]]), 3)


def test_seam_distance_left_counts_only_preceding_seams():
    """Entry 0025 (review finding 4): one unmatched receiver position (5) in a 10-token R. The
    bidirectional b(t) puts token 4 in bin 0 (its seam is AFTER it); the causal b^-(t) does not."""
    from linear_ceiling.e9_pertoken import seam_distance, seam_distance_left
    pairs = np.asarray([(p, p) for p in range(10) if p != 5])
    b = seam_distance(pairs, 10)
    bl = seam_distance_left(pairs, 10)
    assert list(b) == [4, 3, 2, 1, 0, 0, 1, 2, 3]
    assert list(bl) == [10, 10, 10, 10, 10, 0, 1, 2, 3]
    # a reordering gap between receiver-adjacent tokens is a seam for the LATER token only
    pairs2 = np.asarray([(0, 0), (1, 1), (7, 2), (8, 3)])
    assert list(seam_distance_left(pairs2, 4)) == [4, 4, 0, 1]
    # permuted input order is respected
    perm = np.asarray([(8, 3), (0, 0), (7, 2), (1, 1)])
    assert list(seam_distance_left(perm, 4)) == [1, 4, 0, 4]


def test_block_lengths_re_derive_the_matching_blocks():
    """Entry 0025 (review finding 5): a block is a run consecutive on BOTH sides."""
    from linear_ceiling.e9_pertoken import BLOCK_BIN_LABELS, block_bin, block_lengths
    pairs = np.asarray([(0, 0), (1, 1), (2, 2), (10, 5), (11, 6), (20, 8), (30, 9)])   # 3, 2, 1, 1 (30,9 breaks sender run)
    assert list(block_lengths(pairs)) == [3, 3, 3, 2, 2, 1, 1]
    perm = np.asarray([(20, 8), (11, 6), (0, 0), (2, 2), (10, 5), (1, 1), (30, 9)])
    assert list(block_lengths(perm)) == [1, 2, 3, 3, 2, 3, 1]
    assert list(block_bin(np.asarray([1, 2, 3, 4, 7, 8, 100]))) == [0, 1, 1, 2, 2, 3, 3] and len(BLOCK_BIN_LABELS) == 4
    assert block_lengths(np.zeros((0, 2))).size == 0


def test_bootstrap_median_interval_is_seeded_and_uses_the_pinned_quantile():
    """Entry 0025 (review finding 6)."""
    from linear_ceiling.e7_stats import quantile
    from linear_ceiling.e9_pertoken import bootstrap_median_interval
    vals = [i / 24 for i in range(25)]
    a = bootstrap_median_interval(vals, make_rng(25), 500, quantile)
    b = bootstrap_median_interval(vals, make_rng(25), 500, quantile)
    assert a == b and a["reps"] == 500 and a["lower_2.5"] <= 0.5 <= a["upper_97.5"]
    assert a["lower_2.5"] in vals and a["upper_97.5"] in vals            # nearest-rank: an observed median
    with pytest.raises(ValueError):
        bootstrap_median_interval([], make_rng(1), 10, quantile)
    with pytest.raises(ValueError):
        bootstrap_median_interval(vals, make_rng(1), 0, quantile)


def test_seam_bins_are_the_registered_edges():
    b = np.array([0, 1, 2, 3, 4, 7, 8, 15, 16, 1000])
    labels = [SEAM_BIN_LABELS[i] for i in seam_bin(b)]
    assert labels == ["0", "1", "2-3", "2-3", "4-7", "4-7", "8-15", "8-15", "16+", "16+"]


def test_null_pairs_is_a_seeded_derangement_of_sender_positions():
    pairs = np.stack([np.arange(100, 130), np.arange(30)], 1)
    a = null_pairs(pairs, make_rng(23))
    assert np.array_equal(a, null_pairs(pairs, make_rng(23)))
    assert not np.array_equal(a, null_pairs(pairs, make_rng(24)))
    assert np.array_equal(a[:, 1], pairs[:, 1])                       # receiver positions untouched
    assert sorted(a[:, 0].tolist()) == pairs[:, 0].tolist()           # a permutation of sender positions
    assert (a[:, 0] != pairs[:, 0]).all()                             # no token paired with itself
    with pytest.raises(ValueError):
        null_pairs(pairs[:1], make_rng(1))
