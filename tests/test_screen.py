import numpy as np
import pytest

from linear_ceiling.rng import make_rng
from linear_ceiling.screen import (predicted_r2, r2_pooled, readout_coefficients,
                                   regularized_cca, screen_readout)


def _ols_fit(X, Y):
    """Test oracle only (NOT the upstream harness; E1 invokes kvt.ridge there). Centered OLS."""
    xm, ym = X.mean(0), Y.mean(0)
    W = np.linalg.lstsq(X - xm, Y - ym, rcond=None)[0]
    return W, ym - xm @ W


def _synthetic(rng, n=4000, p=6, q=8, m=3, noise=0.7):
    """Y shares a low-rank linear factor with X plus independent noise, so canonical
    correlations are spread in (0, 1)."""
    Z = rng.standard_normal((n, p))
    X = Z @ rng.standard_normal((p, p)) + 0.3 * rng.standard_normal((n, p))
    Y = Z[:, : min(p, q)] @ rng.standard_normal((min(p, q), q)) + noise * rng.standard_normal((n, q))
    R = rng.standard_normal((q, m))
    return X, Y, R


def test_r2_pooled_matches_a5_definition():
    Y = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    Yhat = Y + np.array([[0.5, 0.0], [0.0, -0.5], [0.0, 0.0]])
    ss_res = 0.25 + 0.25
    ss_tot = ((Y - Y.mean(0)) ** 2).sum()
    assert r2_pooled(Y, Yhat) == pytest.approx(1 - ss_res / ss_tot)


def test_rho_in_unit_interval_sorted_and_padded():
    X, Y, _ = _synthetic(make_rng(0))
    res = regularized_cca(X, Y, 0.0, 0.0)
    assert res.rho.shape == (Y.shape[1],)
    assert np.all(np.diff(res.rho) <= 1e-12) and res.rho.min() >= -1e-12 and res.rho.max() <= 1 + 1e-9
    assert np.allclose(res.rho[X.shape[1]:], 0.0)     # q > p: extra directions have rho = 0


def test_canonical_basis_whitens_y():
    X, Y, _ = _synthetic(make_rng(1))
    res = regularized_cca(X, Y, 0.0, 0.0)
    V = (Y - Y.mean(0)) @ res.B
    assert np.allclose(V.T @ V / len(Y), np.eye(Y.shape[1]), atol=1e-8)
    assert np.allclose(res.B_inv @ res.B, np.eye(Y.shape[1]), atol=1e-8)


def test_identity_is_exact_in_sample_at_lambda_zero():
    """H-S1's theorem, verified exactly on synthetic data: predicted R^2 from the CCA
    decomposition equals pooled in-sample OLS R^2 of the read-out."""
    for seed in range(3):
        X, Y, R = _synthetic(make_rng(seed))
        res = regularized_cca(X, Y, 0.0, 0.0)
        C = readout_coefficients(res, R)
        pred = predicted_r2(res.rho, C)
        T = Y @ R
        W, b = _ols_fit(X, T)
        assert pred == pytest.approx(r2_pooled(T, X @ W + b), abs=1e-9)


def test_identity_holds_per_column_and_pooled_differs_from_mean_of_columns():
    X, Y, R = _synthetic(make_rng(5), m=2)
    res = regularized_cca(X, Y, 0.0, 0.0)
    C = readout_coefficients(res, R)
    per_col = [predicted_r2(res.rho, C[:, [j]]) for j in range(R.shape[1])]
    T = Y @ R
    W, b = _ols_fit(X, T)
    for j in range(R.shape[1]):
        assert per_col[j] == pytest.approx(r2_pooled(T[:, [j]], (X @ W + b)[:, [j]]), abs=1e-9)
    assert predicted_r2(res.rho, C) != pytest.approx(np.mean(per_col), abs=1e-6)


def test_prediction_tracks_heldout_r2_with_large_n():
    """The H-S1 shape on synthetic data: train-set CCA prediction vs held-out OLS R^2."""
    rng = make_rng(11)
    X, Y, R = _synthetic(rng, n=40000)
    tr = np.arange(len(X)) < 32000
    res = regularized_cca(X[tr], Y[tr], 0.0, 0.0)
    pred = predicted_r2(res.rho, readout_coefficients(res, R))
    T = Y @ R
    W, b = _ols_fit(X[tr], T[tr])
    held = r2_pooled(T[~tr], X[~tr] @ W + b)
    assert abs(pred - held) < 0.02


def test_regularization_is_scale_free():
    X, Y, R = _synthetic(make_rng(2))
    a = screen_readout(X, Y, R, 1e-2, 1e-2)["predicted_r2"]
    b = screen_readout(1000 * X, 0.001 * Y, 0.001 * R, 1e-2, 1e-2)["predicted_r2"]
    assert a == pytest.approx(b, rel=1e-6)


def test_regularization_shrinks_prediction_monotonically():
    X, Y, R = _synthetic(make_rng(3))
    vals = [screen_readout(X, Y, R, lam, lam)["predicted_r2"] for lam in (0.0, 1e-2, 1e-1, 1.0)]
    assert vals == sorted(vals, reverse=True)


def test_refuses_degenerate_inputs():
    rng = make_rng(4)
    X = rng.standard_normal((10, 20))          # n <= p
    Y = rng.standard_normal((10, 3))
    with pytest.raises(ValueError, match="n"):
        regularized_cca(X, Y, 0.0, 0.0)
    X = np.zeros((100, 4)); Y = rng.standard_normal((100, 3))   # singular Sxx at lambda 0
    with pytest.raises(ValueError, match="positive definite"):
        regularized_cca(X, Y, 0.0, 0.0)
    with pytest.raises(ValueError, match="rows"):
        regularized_cca(rng.standard_normal((50, 4)), rng.standard_normal((40, 3)), 0.0, 0.0)
    with pytest.raises(ValueError, match="zero"):
        predicted_r2(np.array([0.5]), np.zeros((1, 2)))
