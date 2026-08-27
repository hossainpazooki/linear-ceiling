"""E0 candidate C -- the screen with the vocabulary as the calibration set.

Sample = token id; x_t, y_t = RMS-normalised embedding rows of source and target (the exact
layer-0 residual-stream input under a uniform token prior; a proxy for deeper layers).
Canonical correlations are invariant to the per-layer diagonal layernorm gains, so one CCA
per (pair, lambda) serves every layer; the gain enters through the read-out
R = diag(g_l) W^T. See ledger entry 0003 for the rule.
"""
import numpy as np

from linear_ceiling.pairs import pair_name
from linear_ceiling.screen import predicted_r2, readout_coefficients, regularized_cca
from linear_ceiling.weights import WeightReader, assert_shared_vocab


def rms_normalize(E: np.ndarray) -> np.ndarray:
    E = np.asarray(E, dtype=np.float64)
    rms = np.sqrt((E ** 2).mean(1, keepdims=True))
    bad = np.flatnonzero(~np.isfinite(rms[:, 0]) | (rms[:, 0] == 0))
    if bad.size:
        raise ValueError(
            f"rms_normalize: {bad.size} of {E.shape[0]} row(s) have zero or non-finite RMS "
            f"(cannot normalize); first indices: {bad[:10].tolist()}"
        )
    return E / rms


def decide_pair(by_lambda: dict, rule: dict) -> str:
    meds = [b["median"] for b in by_lambda.values()]
    fracs = [b["frac_positive"] for b in by_lambda.values()]
    if all(m >= rule["delta_separate"] and f >= rule["layer_fraction"] for m, f in zip(meds, fracs)):
        return "SEPARATE"
    if all(abs(m) < rule["delta_same"] for m in meds):
        return "SAME"
    return "UNRESOLVED"


def analyze_pair(src: WeightReader, tgt: WeightReader, reg_sweep, rule: dict) -> dict:
    assert_shared_vocab(src, tgt)
    X, Y = rms_normalize(src.embed()), rms_normalize(tgt.embed())
    if X.shape[0] != Y.shape[0]:
        raise ValueError(f"vocab row counts differ: {X.shape[0]} vs {Y.shape[0]}")
    L = tgt.spec.n_layers
    readouts = []
    for l in range(L):
        g = tgt.input_layernorm(l).astype(np.float64)
        readouts.append((g[:, None] * tgt.k_proj(l).T.astype(np.float64),
                         g[:, None] * tgt.v_proj(l).T.astype(np.float64)))
    by_lambda = {}
    for lam in reg_sweep:
        res = regularized_cca(X, Y, lam, lam)
        r2k, r2v = [], []
        for R_K, R_V in readouts:
            r2k.append(predicted_r2(res.rho, readout_coefficients(res, R_K)))
            r2v.append(predicted_r2(res.rho, readout_coefficients(res, R_V)))
        delta = [a - b for a, b in zip(r2k, r2v)]
        by_lambda[str(lam)] = {
            "rho_top10": res.rho[:10].tolist(), "r2_K": r2k, "r2_V": r2v, "delta": delta,
            "median": float(np.median(delta)), "frac_positive": float(np.mean([d > 0 for d in delta])),
        }
    return {
        "pair": pair_name(src.spec.model_id, tgt.spec.model_id) if src.spec.model_id.startswith("Qwen/") else f"{src.spec.model_id}-to-{tgt.spec.model_id}",
        "source": src.spec.model_id, "target": tgt.spec.model_id, "n_tokens": int(X.shape[0]),
        "hidden_src": src.spec.hidden, "hidden_tgt": tgt.spec.hidden, "n_layers_tgt": L,
        "by_lambda": by_lambda, "verdict": decide_pair(by_lambda, rule),
    }
