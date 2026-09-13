#!/usr/bin/env python3
"""Recompute entry 0036's verdict figures from a published E9-long record.

Reads only the small records -- `report.json`, `scores/`, `tokens/` -- so it runs on a
~2.5 GiB subset of the backup dataset with no tensors, no GPU and no upstream checkout.
It answers three separate questions and keeps them separate:

  1. INTEGRITY   do the published files match the sha256s the driver recorded?
  2. ARITHMETIC  do the recorded figures follow from the recorded per-token data,
                 under entry 0023's rule as `linear_ceiling.e9_pertoken` implements it?
  3. PROSE       entries 0029 and 0036 restate f*(tau) as "the fraction of matched tokens
                 whose centered per-token deviation exceeds tau". Entry 0023 defines it as
                 the smallest fraction whose removal leaves the MEAN of the rest at or below
                 tau. These differ. This probe reports both so the gap is measurable.

This is a supporting review tool. It is not a summarizer, it writes nothing into the
ledger, and a figure it prints is not a ledger figure.

Usage:
  python docs/probes/2026-09-11-e9l-record-recompute.py --mirror <dir>/results/e9l \
      [--out report.json]
"""
import argparse, hashlib, json, sys
from pathlib import Path

import numpy as np

from linear_ceiling.e9_pertoken import band_outcome, centered_delta, f_star, token_mean

ARMS = ("same_K", "same_V", "cross_K", "cross_V")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sst_of(body: dict, part: str, key: str) -> np.ndarray:
    """[L, H] per-head SST, exactly as summarize_e9._sst reads it."""
    return np.asarray([layer["sst"] for layer in body[part][key]], dtype=np.float64)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mirror", required=True, type=Path,
                    help="a results/e9l directory holding report.json, scores/, tokens/")
    ap.add_argument("--out", type=Path, help="write the machine-readable report here")
    a = ap.parse_args()

    rep = json.loads((a.mirror / "report.json").read_text(encoding="utf-8"))
    summ = json.loads((a.mirror / "summary.json").read_text(encoding="utf-8"))
    rule = summ["rule"]
    tau = {"K": rule["tau_K"], "V": rule["tau_V"]}
    tau_agent, ladder = rule["tau_agent_K"], rule["tau_ladder"]

    bad_hash, per_handoff, exceed = [], {}, {}
    for hid, rec in rep["scores"].items():
        sf = a.mirror / "scores" / rec["score_file"]
        tf = a.mirror / "tokens" / rec["tokens_file"]
        for path, want, what in ((sf, rec["score_sha256"], "score"),
                                 (tf, rec["tokens_sha256"], "tokens")):
            if sha256_file(path) != want:
                bad_hash.append({"handoff": hid, "file": what, "path": str(path)})
        body, tok, n = json.loads(sf.read_text(encoding="utf-8")), np.load(tf), rec["n_pairs"]
        row = {}
        for arm in ARMS:
            part, key = arm.split("_")
            dt = token_mean(centered_delta(tok[arm], sst_of(body, part, key), n))
            row[arm] = {
                "fstar_tau": f_star(dt, tau[key]),
                "fstar_ladder": {str(t): f_star(dt, t) for t in ladder},
                "mean_centered_delta": float(dt.mean()),
                "max_centered_delta": float(dt.max()),
                # the reading entries 0029/0036 state in prose, measured:
                "fraction_tokens_over_tau": float((dt > tau[key]).mean()),
                "n_tokens_over_tau": int((dt > tau[key]).sum()),
                "n_tokens": int(dt.size),
            }
            if key == "K":
                row[arm]["fstar_tau_agent"] = f_star(dt, tau_agent)
        # entry 0023 rider 2: the token mean of the centered delta is exactly 1 - R^2
        row["r2_identity_abs_err"] = abs(
            (1.0 - row["same_K"]["mean_centered_delta"]) - rec["same_K_r2_layer_mean"])
        per_handoff[hid] = row
        exceed[hid] = row["same_K"]["n_tokens_over_tau"]

    def med(arm, path):
        vals = []
        for row in per_handoff.values():
            v = row[arm]
            for step in path:
                v = v[step]
            vals.append(v)
        return float(np.median(vals))

    checks = []

    def check(name, got, want):
        ok = bool(np.isclose(got, want, rtol=0, atol=1e-12))
        checks.append({"name": name, "recomputed": got, "recorded": want, "match": ok})
        return ok

    for arm in ARMS:
        check(f"median f*(tau) {arm}", med(arm, ["fstar_tau"]), summ["fstar"][arm]["median"])
    for arm in ("same_K", "same_V"):
        for t in ladder:
            check(f"median f*({t}) {arm}", med(arm, ["fstar_ladder", str(t)]),
                  summ["fstar_ladder"][arm][str(t)]["median"])
    for arm in ("same_K", "cross_K"):
        check(f"median f*(tau_agent_K) {arm}", med(arm, ["fstar_tau_agent"]),
              summ["fstar_at_tau_agent"][arm]["median"])

    med_same_K = med("same_K", ["fstar_tau"])
    band = band_outcome(med_same_K, {"holds_max": rule["holds_max"],
                                     "degrades_min": rule["degrades_min"]})
    n_over = sum(exceed.values())
    n_tok = sum(r["same_K"]["n_tokens"] for r in per_handoff.values())
    max_delta = max(r["same_K"]["max_centered_delta"] for r in per_handoff.values())
    max_r2_err = max(r["r2_identity_abs_err"] for r in per_handoff.values())

    out = {
        "probe": "2026-09-11-e9l-record-recompute",
        "mirror": str(a.mirror.resolve()),
        "report_sha256": sha256_file(a.mirror / "report.json"),
        "summary_sha256": sha256_file(a.mirror / "summary.json"),
        "upstream_sha": rep.get("upstream_sha"),
        "config_sha256": rep.get("config_sha256"),
        "n_scored": len(per_handoff),
        "integrity": {"files_checked": 2 * len(per_handoff), "mismatches": bad_hash},
        "arithmetic": {"checks": checks,
                       "all_match": all(c["match"] for c in checks),
                       "median_fstar_same_K": med_same_K,
                       "band_outcome_recomputed": band,
                       "band_outcome_recorded": summ["band_outcome"],
                       "r2_identity_max_abs_err": max_r2_err},
        "prose_reading": {
            "claim": ("entries 0029/0036: 'f*(tau_K) = the fraction of matched tokens whose "
                      "centered per-token deviation exceeds tau_K'; 0036 adds 'not one scored "
                      "handoff has a single matched token whose centered deviation exceeds tau_K'"),
            "tau_K": tau["K"],
            "handoffs_with_a_token_over_tau_K": sum(1 for v in exceed.values() if v),
            "n_handoffs": len(exceed),
            "tokens_over_tau_K": n_over,
            "tokens_total": n_tok,
            "fraction_over_tau_K": n_over / n_tok if n_tok else None,
            "max_centered_delta_same_K": max_delta,
            "sentence_holds": n_over == 0,
        },
        "per_handoff": per_handoff,
    }

    ok = not bad_hash and out["arithmetic"]["all_match"] and band == summ["band_outcome"]
    print(f"integrity : {2*len(per_handoff) - len(bad_hash)}/{2*len(per_handoff)} files match "
          f"their recorded sha256")
    print(f"arithmetic: {sum(c['match'] for c in checks)}/{len(checks)} medians reproduce exactly")
    print(f"            median f*(tau_K) same K = {med_same_K:.6f} -> {band} "
          f"(recorded {summ['band_outcome']})")
    print(f"            max |1-mean(delta) - recorded R2| = {max_r2_err:.2e}")
    print(f"prose     : {n_over:,}/{n_tok:,} matched tokens exceed tau_K "
          f"({100*n_over/n_tok:.2f}%) in {sum(1 for v in exceed.values() if v)}/{len(exceed)} "
          f"handoffs; max delta {max_delta:.4f} vs tau_K {tau['K']:.4f}")
    print(f"            0036's 'not one matched token' sentence holds: {n_over == 0}")
    if a.out:
        a.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"wrote {a.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
