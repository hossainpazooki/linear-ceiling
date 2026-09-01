"""The one quantile method every E7 figure uses -- pinned so a number reproduces.

Two different percentile conventions on the same 68 values give two different "p90"s, and a
ledger number that depends on an unstated convention is not reproducible. This is the
convention the entry-0010/0012 recon used and is now the only one the driver and summarizer
may call:

    median  = statistics.median  (mean of the two middle values for even n)
    q(p)    = sorted(values)[min(floor(p * n), n - 1)]   -- lower nearest-rank, no interpolation

Both are exact functions of the sorted input, so recomputation matches to the last digit.
"""
import math
import statistics


def quantile(values, p: float) -> float:
    if not values:
        raise ValueError("quantile of an empty sequence; refusing to invent a number")
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"quantile probability must be in [0, 1], got {p}")
    s = sorted(values)
    return s[min(int(math.floor(p * len(s))), len(s) - 1)]


def summary(values) -> dict:
    """{n, median, p10, p90} of a non-empty sequence; refuses (never NaN) when empty."""
    if not values:
        raise ValueError("summary of an empty sequence; refusing to invent a number")
    return {"n": len(values), "median": statistics.median(values),
            "p10": quantile(values, 0.10), "p90": quantile(values, 0.90)}
