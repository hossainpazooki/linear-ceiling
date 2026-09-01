"""Per-token E9 statistics (ledger entry 0023): centered deviation, the oracle
selective-recompute fraction f*(tau), seam distance, the null pairing, and the band.

All of it is CPU arithmetic over the per-token record the upstream scorer writes
(`--per-token`: squares [n, L, H] float32 per read-out and arm, plus the per-head SST in the
score json). Nothing here reads a model.

Units (0023, rider 2): the centered per-token deviation
    delta_c(t, l, h) = ||x_hat(t,l,h) - x_R(t,l,h)||^2 / (SST(l,h) / n)
is the token's share of the layer-head's unexplained variance in R^2's own units: its mean
over tokens is exactly 1 - R^2(l, h), so the head-and-layer mean over tokens is exactly
1 - (the recorded head-averaged, layer-averaged R^2). It is NOT "this token's KV is x% wrong";
that reading belongs to the own-norm deviation delta_own = ||d||^2 / ||x_R||^2, which is kept
only as a diagnostic (it flatters: the uncentered norm is dominated by the per-head mean, and
it blows up on small-norm tokens).
"""
import numpy as np

SEAM_BIN_EDGES = (0, 1, 2, 4, 8, 16)            # bins: 0, 1, 2-3, 4-7, 8-15, 16+  (fixed, 0023)
SEAM_BIN_LABELS = ("0", "1", "2-3", "4-7", "8-15", "16+")


def centered_delta(sq: np.ndarray, sst: np.ndarray, n: int) -> np.ndarray:
    """[n, L, H] squares, [L, H] SST -> [n, L, H] centered deviation (float64)."""
    sq = np.asarray(sq, dtype=np.float64)
    sst = np.asarray(sst, dtype=np.float64)
    if sq.ndim != 3 or sst.shape != sq.shape[1:] or sq.shape[0] != n:
        raise ValueError(f"shape mismatch: squares {sq.shape}, sst {sst.shape}, n {n}")
    if (sst <= 0).any():
        raise ValueError("a layer-head SST is not positive; the reference set is degenerate")
    return sq / (sst / n)[None]


def token_mean(delta: np.ndarray) -> np.ndarray:
    """[n, L, H] -> [n]: mean over heads then layers (equal counts, so the plain mean)."""
    return np.asarray(delta, dtype=np.float64).reshape(len(delta), -1).mean(1)


def layer_mean(delta: np.ndarray) -> np.ndarray:
    """[n, L, H] -> [n, L]: mean over heads."""
    return np.asarray(delta, dtype=np.float64).mean(2)


def own_norm_delta(sq: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """The seed's original per-token deviation, heads pooled: [n, L, H] x2 -> [n, L]. Diagnostic only."""
    sq, ref = np.asarray(sq, dtype=np.float64), np.asarray(ref, dtype=np.float64)
    den = ref.sum(2)
    if (den <= 0).any():
        raise ValueError("a token has zero reference norm; own-norm deviation undefined")
    return sq.sum(2) / den


F_STAR_REL_TOL = 1e-9            # "at or below tau" is judged to this relative tolerance (float32 record)


def f_star(delta_token: np.ndarray, tau: float) -> float:
    """Oracle selective-recompute fraction: the smallest fraction of tokens that, removed in
    descending order of deviation (each assumed restored exactly), leaves the MEAN deviation of
    the rest at or below tau (to F_STAR_REL_TOL relative, so a float32 per-token record whose
    mean lands 1e-11 above tau does not cost a token). 0 when the full-set mean is already
    <= tau; 1 when no proper subset qualifies. An oracle LOWER BOUND on real selective recompute
    (0023: restored-exactly assumption; no error propagation through the reused KV)."""
    d = np.sort(np.asarray(delta_token, dtype=np.float64))[::-1]
    n = len(d)
    if n == 0:
        raise ValueError("f* of an empty token set; refusing to invent a number")
    if not np.isfinite(tau) or tau < 0:
        raise ValueError(f"tau must be a finite non-negative number, got {tau}")
    # mean of the suffix d[k:] for k = 0..n-1; suffix means are monotone non-increasing in k
    suffix = np.cumsum(d[::-1])[::-1]
    counts = np.arange(n, 0, -1)
    ok = (suffix / counts) <= tau * (1.0 + F_STAR_REL_TOL) + 1e-15
    if not ok.any():
        return 1.0
    return float(np.argmax(ok) / n)


def band_outcome(median_f: float, rule: dict) -> str:
    """0023 rule on median f*(tau_K) over included handoffs, K read-out."""
    if median_f <= rule["holds_max"]:
        return "HOLDS"
    if median_f >= rule["degrades_min"]:
        return "DEGRADES"
    return "UNRESOLVED"


def seam_distance(pairs: np.ndarray, n_receiver: int) -> np.ndarray:
    """b(t) per matched token, from the alignment alone (0023). A seam is (a) a receiver
    position not in M, or (b) the gap between two receiver-adjacent matched tokens whose sender
    positions are not consecutive (a reordering). b = number of receiver positions strictly
    between p_R(t) and the nearest seam (0 = adjacent). If R is matched end to end with no
    reordering, b = n_receiver for every token (no seam exists)."""
    pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
    n = len(pairs)
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    p_r = pairs[:, 1]
    order = np.argsort(p_r, kind="stable")
    ps, pr = pairs[order, 0], pairs[order, 1]
    if len(np.unique(pr)) != n or pr.min() < 0 or pr.max() >= n_receiver:
        raise ValueError("receiver positions in pairs must be unique and within [0, n_receiver)")
    matched = np.zeros(n_receiver, dtype=bool)
    matched[pr] = True
    # seam coordinates on a doubled axis: unmatched position u -> 2u; gap between j and j+1 -> 2j+1
    seams = [2 * u for u in np.flatnonzero(~matched)]
    for i in range(n - 1):
        if pr[i + 1] == pr[i] + 1 and ps[i + 1] != ps[i] + 1:
            seams.append(2 * pr[i] + 1)
    b = np.full(n, n_receiver, dtype=np.int64)
    if seams:
        s = np.sort(np.asarray(seams, dtype=np.int64))
        x = 2 * pr
        idx = np.searchsorted(s, x)
        left = np.where(idx > 0, x - s[np.clip(idx - 1, 0, len(s) - 1)], np.iinfo(np.int64).max)
        right = np.where(idx < len(s), s[np.clip(idx, 0, len(s) - 1)] - x, np.iinfo(np.int64).max)
        dist = np.minimum(left, right)              # in half-positions: 2 per unmatched token, 1 to a gap
        # tokens strictly between: unmatched at distance 2k half-steps -> k-1; gap at 2k+1 -> k
        b[:] = np.where(dist % 2 == 0, dist // 2 - 1, dist // 2)
    out = np.empty(n, dtype=np.int64)
    out[order] = b
    return out


def seam_bin(b: np.ndarray) -> np.ndarray:
    """Bin index per token under the fixed edges (0023)."""
    return np.searchsorted(np.asarray(SEAM_BIN_EDGES), np.asarray(b), side="right") - 1


def null_pairs(pairs: np.ndarray, rng) -> np.ndarray:
    """The delta_null control (0023): pair each receiver position with the SENDER position of a
    different matched token, by a seeded permutation repaired to a derangement (any fixed
    point swaps with its successor). Deterministic given the rng state."""
    pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
    n = len(pairs)
    if n < 2:
        raise ValueError("delta_null needs at least two matched tokens")
    perm = rng.permutation(n)
    fixed = np.flatnonzero(perm == np.arange(n))
    for i in fixed:
        if perm[i] != i:                   # already repaired by an earlier swap
            continue
        j = (i + 1) % n
        perm[i], perm[j] = perm[j], perm[i]
    if (perm == np.arange(n)).any():         # cannot happen for n >= 2 after the repair; refuse if it does
        raise ValueError("derangement repair failed")
    return np.stack([pairs[perm, 0], pairs[:, 1]], 1)
