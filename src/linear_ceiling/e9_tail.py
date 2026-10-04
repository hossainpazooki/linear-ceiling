"""Tail of the per-token deviation, beside f* (reviewer weakness W3; the figures W4 and W5 need).

Runs `summarize_e9.summarize` FIRST -- it verifies every record and refuses on tamper -- then re-reads the same
sha-pinned per-token squares and alignment pairs and computes, per handoff and pooled, same-K and same-V:
delta_max; the fraction of matched tokens over each tau (tau_K, then the registered ladder); the mean after
removing the top 10 % / 20 % of tokens by delta (oracle-ranked token DELETION in THIS paper's units: not CacheBlend's
selection rule, not a measured recomputation cost, no numeric comparison with their figure); pooled MEANS (not only medians) per causal seam bin b^-(t) and per sender-position
bin; the native-window subset (sender position < 32,768); and |R| over the scored handoffs.

Unit (0023): delta is a token's share of the layer-head's unexplained variance, in R^2's own units; its mean over
tokens is exactly 1 - R^2. It is never a percent error. Nothing here moves a verdict; f* is not restated.

usage: python -m linear_ceiling.e9_tail --config config/<cell>.toml
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e7_config, load_e9_config
from linear_ceiling.e7_stats import summary
from linear_ceiling.e9 import _stem
from linear_ceiling.e9_pertoken import SEAM_BIN_LABELS, centered_delta, seam_bin, seam_distance_left, token_mean
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.summarize_e9 import _SUM_TOL, _load_tokens, _sst, summarize

NATIVE_WINDOW = 32768
REMOVE_FRACTIONS = (0.10, 0.20)
ARMS = ("same_K", "same_V")
UNIT = ("delta is a token's share of the layer-head's unexplained variance, in R^2's own units (entry 0023): the "
        "mean over tokens is exactly 1 - R^2; it is not a per-token percent error")


def mean_after_removing_top(d: np.ndarray, frac: float) -> float:
    s = np.sort(d)[::-1]
    k = int(math.ceil(frac * len(s)))
    rest = s[k:]
    return float(rest.mean()) if len(rest) else 0.0


def bin_statistics(labels, per_bin: list[list[np.ndarray]]) -> list[dict]:
    rows = []
    for i, label in enumerate(labels):
        allv = np.concatenate(per_bin[i]) if per_bin[i] else np.zeros(0)
        rows.append({"bin": label, "n_tokens": int(len(allv)),
                     "mean": None if len(allv) == 0 else float(allv.mean()),
                     "median": None if len(allv) == 0 else float(np.median(allv))})
    return rows


def sender_position_edges(cfg: E9Config) -> list[int]:
    if cfg.profiles and cfg.profiles.get("s_pos_edges"):
        return [int(e) for e in cfg.profiles["s_pos_edges"]]
    return [0]                                               # one bin: every sender position


def sender_position_labels(edges: list[int], cap: int) -> list[str]:
    hi = edges[1:] + [cap]
    return [f"{lo}-{h - 1}" for lo, h in zip(edges, hi)]


def tail(cfg: E9Config, **summarize_kwargs) -> dict:
    # Gate, then compute. Refuses (raises) on anything `summarize` refuses; writes nothing in that case.
    summarize(cfg, **summarize_kwargs)                       # the gate: verifies every record read below
    rdir = cfg.results_dir
    report_path, summary_path = rdir / "report.json", rdir / "summary.json"
    rep = json.loads(report_path.read_text(encoding="utf-8"))
    fig = json.loads(summary_path.read_text(encoding="utf-8"))
    tau = {"K": float(fig["tau"]["K"]), "V": float(fig["tau"]["V"])}
    ladder = [float(t) for t in cfg.rule["tau_ladder"]]
    taus = {"K": [tau["K"]] + ladder, "V": [tau["V"]] + ladder}
    scored = list(rep["scores"])
    edges = sender_position_edges(cfg)
    pos_labels = sender_position_labels(edges, int(cfg.context_cap))

    per_handoff, n_recv = {}, {}
    seam_tokens = [[[] for _ in SEAM_BIN_LABELS] for _ in ARMS]
    pos_tokens = [[[] for _ in pos_labels] for _ in ARMS]
    native = [[] for _ in ARMS]
    pooled_tokens = [[] for _ in ARMS]
    for hid in scored:
        rec = rep["scores"][hid]
        sf = rdir / "scores" / rec["score_file"]
        if sha256_file_bytes(sf) != rec["score_sha256"]:
            raise ValueError(f"{hid}: score file changed after the summarizer verified it")
        body = json.loads(sf.read_text(encoding="utf-8"))
        tok = _load_tokens(rdir / "tokens" / rec["tokens_file"], rec["tokens_sha256"], hid)
        n = int(rec["n_pairs"])
        with np.load(rdir / "align" / f"{_stem(hid)}.npz") as z:
            pairs = np.asarray(z["pairs"], dtype=np.int64)
        align = json.loads((rdir / "align" / f"{_stem(hid)}.json").read_text(encoding="utf-8"))
        n_recv[hid] = int(align["n_receiver"])
        if len(pairs) != n:
            raise ValueError(f"{hid}: n_pairs {n} != alignment pairs {len(pairs)}")
        bins = seam_bin(seam_distance_left(pairs, n_recv[hid]))
        pos_bins = np.searchsorted(np.asarray(edges), pairs[:, 0], side="right") - 1
        in_native = pairs[:, 0] < NATIVE_WINDOW
        per_handoff[hid] = {"n_matched": n, "n_receiver": n_recv[hid]}
        for ai, arm in enumerate(ARMS):
            part, key = arm.split("_")
            d = token_mean(centered_delta(tok[arm], _sst(body, part, key), n))
            # 0023: the token mean IS 1 - R^2. The per-token record is float32 and the recorded moments are
            # float64, so the identity holds to the summarizer's own sum tolerance, not to the last bit.
            recorded = 1.0 - float(rec[f"{arm}_r2_layer_mean"])
            if not math.isclose(float(d.mean()), recorded, rel_tol=_SUM_TOL, abs_tol=0.0):
                raise ValueError(f"{hid}: {arm} token mean {d.mean():.9f} != 1 - recorded R^2 {recorded:.9f} "
                                 f"(beyond {_SUM_TOL:.0e} relative)")
            per_handoff[hid][arm] = {
                "mean": float(d.mean()), "delta_max": float(d.max()), "p90": float(np.quantile(d, 0.9)),
                "fraction_over_tau": {str(t): float((d > t).mean()) for t in taus[key]},
                "mean_after_removing_top": {f"{f:.2f}": mean_after_removing_top(d, f) for f in REMOVE_FRACTIONS},
                "native_window_mean": None if not in_native.any() else float(d[in_native].mean()),
            }
            pooled_tokens[ai].append(d)
            native[ai].append(d[in_native])
            for i in range(len(SEAM_BIN_LABELS)):
                seam_tokens[ai][i].append(d[bins == i])
            for i in range(len(pos_labels)):
                pos_tokens[ai][i].append(d[pos_bins == i])

    pooled, native_window, seam_rows, pos_rows = {}, {}, {}, {}
    for ai, arm in enumerate(ARMS):
        key = arm.split("_")[1]
        allv = np.concatenate(pooled_tokens[ai])
        nat = np.concatenate(native[ai])
        pooled[arm] = {"n_tokens": int(len(allv)), "mean": float(allv.mean()), "median": float(np.median(allv)),
                       "p90": float(np.quantile(allv, 0.9)), "p99": float(np.quantile(allv, 0.99)),
                       "delta_max": float(allv.max()),
                       "fraction_over_tau": {str(t): float((allv > t).mean()) for t in taus[key]},
                       "mean_after_removing_top": {f"{f:.2f}": mean_after_removing_top(allv, f)
                                                   for f in REMOVE_FRACTIONS}}
        native_window[arm] = {"n_tokens": int(len(nat)), "mean": None if len(nat) == 0 else float(nat.mean()),
                              "median": None if len(nat) == 0 else float(np.median(nat))}
        seam_rows[arm] = bin_statistics(SEAM_BIN_LABELS, seam_tokens[ai])
        pos_rows[arm] = bin_statistics(pos_labels, pos_tokens[ai])
    native_window.update({"cap": NATIVE_WINDOW, "n_tokens": native_window["same_K"]["n_tokens"],
                          "share_of_matched": native_window["same_K"]["n_tokens"] / pooled["same_K"]["n_tokens"]})
    out = {
        "cell": rdir.name, "unit": UNIT,
        "report_sha256": sha256_file_bytes(report_path), "summary_sha256": sha256_file_bytes(summary_path),
        "tau": tau, "taus": taus["K"], "remove_fractions": [f"{f:.2f}" for f in REMOVE_FRACTIONS],
        "n_scored": len(scored), "per_handoff": per_handoff, "pooled": pooled,
        "seam_left_bins": seam_rows, "position_bins": pos_rows, "position_edges": edges,
        "native_window": native_window,
        "receiver_length": summary([n_recv[h] for h in scored]),
        "per_handoff_mean_same_K": summary([per_handoff[h]["same_K"]["mean"] for h in scored]),
        "per_handoff_fraction_over_tau_K": summary([per_handoff[h]["same_K"]["fraction_over_tau"][str(tau["K"])]
                                                    for h in scored]),
        "per_handoff_delta_max_same_K": summary([per_handoff[h]["same_K"]["delta_max"] for h in scored]),
    }
    (rdir / "tail.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (rdir / "tail.md").write_text(format_tail_summary(out), encoding="utf-8")
    return out


def format_tail_summary(o: dict) -> str:
    k = o["pooled"]["same_K"]
    s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"  # noqa: E731
    lines = [f"# Tail of the per-token deviation -- {o['cell']} ({o['n_scored']} scored handoffs)", "",
             f"Unit: {o['unit']}.", "",
             f"Pooled same-K over {k['n_tokens']:,} matched tokens: mean {k['mean']:.4f}, median {k['median']:.4f}, "
             f"p90 {k['p90']:.4f}, p99 {k['p99']:.4f}, max {k['delta_max']:.4f}.", "",
             "| tau | tokens over tau (pooled) | per-handoff fraction, median (p10, p90) |", "|---|---|---|"]
    for t in o["taus"]:
        per = summary([ph["same_K"]["fraction_over_tau"][str(t)] for ph in o["per_handoff"].values()])
        lines.append(f"| {t:.4g} | {k['fraction_over_tau'][str(t)]:.4f} | {s(per)} |")
    lines += ["", "| removed (top by delta) | mean of the rest, pooled same-K |", "|---|---|"]
    for f, v in k["mean_after_removing_top"].items():
        lines.append(f"| {float(f):.0%} | {v:.4f} |")
    lines += ["", "Pooled MEAN (median) same-K by causal seam distance b^-(t):", ""]
    lines.append(" . ".join(f"{r['bin']}: {r['mean']:.3f} ({r['median']:.3f}, n={r['n_tokens']:,})"
                            for r in o["seam_left_bins"]["same_K"] if r["n_tokens"]))
    lines += ["", "Pooled MEAN (median) same-K by sender position:", ""]
    lines.append(" . ".join(f"{r['bin']}: {r['mean']:.3f} ({r['median']:.3f}, n={r['n_tokens']:,})"
                            for r in o["position_bins"]["same_K"] if r["n_tokens"]))
    nw = o["native_window"]
    lines += ["", f"Native window (sender position < {nw['cap']:,}): {nw['n_tokens']:,} tokens, "
              f"{nw['share_of_matched']:.1%} of matched; same-K mean {nw['same_K']['mean']:.4f}, "
              f"median {nw['same_K']['median']:.4f}.",
              "", f"|R| over the scored handoffs: {s(o['receiver_length'], 0)}.",
              f"Per-handoff same-K mean: {s(o['per_handoff_mean_same_K'])}; per-handoff fraction over tau_K: "
              f"{s(o['per_handoff_fraction_over_tau_K'])}; per-handoff delta_max: "
              f"{s(o['per_handoff_delta_max_same_K'])}.",
              "", f"Pinned to report.json {o['report_sha256'][:12]} and summary.json {o['summary_sha256'][:12]}.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e9_tail")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9.toml"))
    a = ap.parse_args(argv)
    cfg = load_e9_config(Path(a.config), REPO_ROOT)
    e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    out = tail(cfg, e7=e7)
    print(f"tail ok: {out['n_scored']} handoffs; pooled same-K mean {out['pooled']['same_K']['mean']:.4f}, "
          f"over tau_K {out['pooled']['same_K']['fraction_over_tau'][str(out['tau']['K'])]:.4f}; "
          f"written to {cfg.results_dir / 'tail.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
