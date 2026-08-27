"""The screen: regularized CCA between two representations and the read-out-conditioned
predicted R^2  sum_ij rho_i^2 C_ij^2 / sum_ij C_ij^2.

This is textbook multivariate statistics (the spec says so in one sentence); the
contribution is what gets sealed around it, not the theorem. At lambda = 0 the prediction
equals the pooled in-sample OLS R^2 of the read-out exactly (tests/test_screen.py).

Regularization is scale-free: lam multiplies the mean eigenvalue of the covariance it is
added to. A sweep is reported, never tuned-and-hidden (risk register, row 1).
"""
from dataclasses import dataclass

import numpy as np


def r2_pooled(Y, Yhat) -> float:
    """Definition A5. Provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/ridge.py
    (r2_score) and docs/ledger.md (A5), commitSha: f3594458f73d70a15f195c863d52ea6592f61578}:
    pooled over rows and columns; ybar is the mean of the set being scored."""
    Y = np.asarray(Y, dtype=np.float64); Yhat = np.asarray(Yhat, dtype=np.float64)
    ss_res = ((Y - Yhat) ** 2).sum()
    ss_tot = ((Y - Y.mean(0)) ** 2).sum()
    if ss_tot == 0.0:
        raise ValueError("R^2 undefined: scored set has zero total variance")
    return float(1.0 - ss_res / ss_tot)


@dataclass(frozen=True)
class CCAResult:
    rho: np.ndarray      # (q,) descending, zero-padded
    A: np.ndarray        # (p, p) canonical directions for X
    B: np.ndarray        # (q, q) canonical directions for Y
    B_inv: np.ndarray    # (q, q)
    x_mean: np.ndarray
    y_mean: np.ndarray
    lam_x: float
    lam_y: float


def _cov(Xc: np.ndarray, lam: float, name: str) -> np.ndarray:
    n, p = Xc.shape
    S = Xc.T @ Xc / n
    if lam < 0:
        raise ValueError(f"lam_{name} must be >= 0")
    if lam > 0:
        S = S + lam * (np.trace(S) / p) * np.eye(p)
    return S


def _inv_sqrt_and_sqrt(S: np.ndarray, name: str):
    w, Q = np.linalg.eigh(S)
    tol = 1e-10 * max(w.max(), 1e-300)
    if w.min() <= tol:
        raise ValueError(f"S_{name}{name} is not positive definite (min eigenvalue {w.min():.3e}); "
                         "add regularization or drop constant/collinear columns")
    return (Q * (1 / np.sqrt(w))) @ Q.T, (Q * np.sqrt(w)) @ Q.T


def regularized_cca(X, Y, lam_x: float, lam_y: float) -> CCAResult:
    X = np.asarray(X, dtype=np.float64); Y = np.asarray(Y, dtype=np.float64)
    if X.ndim != 2 or Y.ndim != 2 or X.shape[0] != Y.shape[0]:
        raise ValueError(f"X and Y must be 2-D with the same number of rows, got {X.shape} and {Y.shape}")
    n, p = X.shape; q = Y.shape[1]
    if n <= max(p, q):
        raise ValueError(f"need n > max(p, q) rows for CCA, got n={n}, p={p}, q={q}")
    x_mean, y_mean = X.mean(0), Y.mean(0)
    Xc, Yc = X - x_mean, Y - y_mean
    Sxx, Syy = _cov(Xc, lam_x, "x"), _cov(Yc, lam_y, "y")
    Sxy = Xc.T @ Yc / n
    Sxx_ih, _ = _inv_sqrt_and_sqrt(Sxx, "x")
    Syy_ih, Syy_h = _inv_sqrt_and_sqrt(Syy, "y")
    M = Sxx_ih @ Sxy @ Syy_ih
    U, s, Vt = np.linalg.svd(M, full_matrices=True)
    rho = np.zeros(q); rho[: len(s)] = np.clip(s, 0.0, 1.0)
    V = Vt.T
    return CCAResult(rho=rho, A=Sxx_ih @ U, B=Syy_ih @ V, B_inv=V.T @ Syy_h,
                     x_mean=x_mean, y_mean=y_mean, lam_x=float(lam_x), lam_y=float(lam_y))


def readout_coefficients(res: CCAResult, R) -> np.ndarray:
    R = np.asarray(R, dtype=np.float64)
    if R.ndim == 1:
        R = R[:, None]
    if R.shape[0] != res.B.shape[0]:
        raise ValueError(f"read-out has {R.shape[0]} rows, CCA basis has {res.B.shape[0]}")
    return res.B_inv @ R


def predicted_r2(rho, C) -> float:
    rho = np.asarray(rho, dtype=np.float64); C = np.asarray(C, dtype=np.float64)
    C2 = C ** 2
    denom = C2.sum()
    if denom == 0.0:
        raise ValueError("read-out has zero energy in the canonical basis; predicted R^2 undefined")
    return float((rho[:, None] ** 2 * C2).sum() / denom)


def screen_readout(X, Y, R, lam_x: float, lam_y: float) -> dict:
    res = regularized_cca(X, Y, lam_x, lam_y)
    C = readout_coefficients(res, R)
    energy = (C ** 2).sum(1)
    return {"predicted_r2": predicted_r2(res.rho, C), "rho": res.rho,
            "coef_energy_by_rank": energy / energy.sum()}
