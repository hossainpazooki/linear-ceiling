"""E9 scaled short cell -- compare the NATIVE E9 run (config/e9.toml, entry 0029) with the SCALED run of the
SAME handoffs (config/e9s.toml, registered by its own entry) token by token, and state how much of the
cross-cell difference between the short cell (0029) and the long cell (0036) the receiver configuration
alone reproduces on identical tokens.

Fail-closed: refuses unless both runs are complete under their committed configs, cover the same handoffs,
share every alignment array byte for byte, and every score and per-token record matches the hash its report
recorded. Descriptive; no verdict; writes <scaled results_dir>/compare.{json,md}. The paired quantity is the
per-token centered deviation delta_K(t) (0023: token mean over heads then layers) of the receiver's own K,
native minus scaled at the same (p_S, p_R) pair.

usage: python -m linear_ceiling.e9_compare [--native config/e9.toml] [--scaled config/e9s.toml]
                                            [--long results/e9l/summary.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e9_config
from linear_ceiling.e7_stats import quantile
from linear_ceiling.e9 import _stem
from linear_ceiling.e9_pertoken import (bootstrap_median_interval, centered_delta, f_star, seam_bin,
                                        seam_distance_left, token_mean)
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.rng import make_rng
from linear_ceiling.summarize_e9 import SEAM_BIN_LABELS, _load_tokens, _sst, _stats, _tau_key

BOOT_SEED, BOOT_REPS = 37, 2000
SEAM_FAR = "16+"           # the far-from-seam bin whose cross-cell difference (0029 0.019 -> 0036 0.063) the share reads


def _report(cfg: E9Config, who: str) -> dict:
    p = cfg.results_dir / "report.json"
    if not p.exists():
        raise ValueError(f"{who}: {p} is missing")
    rep = json.loads(p.read_text(encoding="utf-8"))
    if not rep.get("complete"):
        raise ValueError(f"{who}: the run is not complete")
    if rep.get("config_sha256") != sha256_text_file(cfg.config_path):
        raise ValueError(f"{who}: report.json was written under another {cfg.config_path.name}")
    return rep


def _alignment(cfg: E9Config, hid: str) -> dict:
    p = cfg.results_dir / "align" / f"{_stem(hid)}.npz"
    if not p.exists():
        raise ValueError(f"alignment record missing: {p}")
    with np.load(p) as z:
        return {k: z[k] for k in z.files}


def _delta_K(cfg: E9Config, rep: dict, hid: str, who: str) -> tuple[np.ndarray, int]:
    rec = rep["scores"][hid]
    body_path = cfg.results_dir / "scores" / rec["score_file"]
    if not body_path.exists() or sha256_file_bytes(body_path) != rec["score_sha256"]:
        raise ValueError(f"{who} {hid}: score file missing or off-hash")
    body = json.loads(body_path.read_text(encoding="utf-8"))
    tok = _load_tokens(cfg.results_dir / "tokens" / rec["tokens_file"], rec["tokens_sha256"], f"{who} {hid}")
    n = int(body["n_pairs"])
    sq = np.asarray(tok["same_K"])
    if sq.ndim != 3 or sq.shape[0] != n:
        raise ValueError(f"{who} {hid}: per-token record shape {sq.shape} does not match n_pairs {n}")
    return token_mean(centered_delta(sq, _sst(body, "same", "K"), n)), n


def _check_configs(native: E9Config, scaled: E9Config) -> None:
    if native.rope is not None:
        raise ValueError("the native config carries [e9.rope]; the native run is the unscaled one (config/e9.toml)")
    if scaled.rope is None:
        raise ValueError("the scaled config has no [e9.rope]; nothing to compare")
    if scaled.context_cap != native.context_cap or scaled.context_floor != 0:
        raise ValueError("the scaled run must use the native cap with no floor: the SAME handoffs")
    if scaled.rule != native.rule or scaled.controls != native.controls or scaled.mapper_k != native.mapper_k:
        raise ValueError("rule, tau, ladder, controls or mapper differ between the two configs; the comparison is undefined")
    if scaled.results_dir.resolve() == native.results_dir.resolve():
        raise ValueError("the two configs write the same results_dir")


def _long_cell(path: Path, taus: list[float]) -> dict:
    s = json.loads(path.read_text(encoding="utf-8"))
    try:
        far = next(r["median"] for r in s["seam_profile_left_pooled"]["same_K"] if r["bin"] == SEAM_FAR)
        ladder = {_tau_key(t): float(s["fstar_ladder"]["same_K"][_tau_key(t)]["median"]) for t in taus[1:]}
    except (KeyError, StopIteration, TypeError) as e:
        raise ValueError(f"long summary {path} lacks the seam profile or the tau ladder: {e}")
    return {"path": str(path), "seam_far_median": float(far), "fstar_ladder_median": ladder,
            "n_handoffs": int(s["coverage"].get("scored", s["coverage"]["included"]))}


def _share(native: float, scaled: float, long_: float) -> float | None:
    """The fraction of the cross-cell difference (long - native) that the scaled short cell reproduces
    (scaled - native) on identical tokens; None when the cells do not differ."""
    d = long_ - native
    return None if abs(d) < 1e-12 else float((scaled - native) / d)


def compare(native: E9Config, scaled: E9Config, long_summary: Path | None = None) -> dict:
    _check_configs(native, scaled)
    rep_n, rep_s = _report(native, "native"), _report(scaled, "scaled")
    ids = sorted(rep_n["scores"])
    if sorted(rep_s["scores"]) != ids:
        raise ValueError(f"the two runs score different handoffs: native {len(rep_n['scores'])}, scaled {len(rep_s['scores'])}, "
                         f"common {len(set(rep_n['scores']) & set(rep_s['scores']))}")
    al_n = {a["handoff_id"]: a for a in rep_n["alignments"]}
    al_s = {a["handoff_id"]: a for a in rep_s["alignments"]}
    tau_K = float(scaled.rule["tau_K"])
    taus = [tau_K] + [float(t) for t in scaled.rule["tau_ladder"]]
    per, seam = {}, {lab: {"native": [], "scaled": []} for lab in SEAM_BIN_LABELS}
    diffs_all = []
    for hid in ids:
        for key in ("n_sender", "n_receiver", "n_matched", "text_sha256"):      # the same trace text, the same match
            if al_n[hid].get(key) != al_s[hid].get(key):
                raise ValueError(f"{hid}: alignment {key} differs between the runs ({al_n[hid].get(key)} vs {al_s[hid].get(key)})")
        an, as_ = _alignment(native, hid), _alignment(scaled, hid)
        if set(an) != set(as_) or any(not np.array_equal(an[k], as_[k]) for k in an):
            raise ValueError(f"{hid}: the alignment arrays differ between the runs; the pairing is not the same")
        d_n, n = _delta_K(native, rep_n, hid, "native")
        d_s, n2 = _delta_K(scaled, rep_s, hid, "scaled")
        if n != n2 or len(d_n) != len(d_s):
            raise ValueError(f"{hid}: token counts differ ({n} vs {n2})")
        diff = d_s - d_n
        diffs_all.append(diff)
        bins = seam_bin(seam_distance_left(an["pairs"], int(al_n[hid]["n_receiver"])))
        for i, lab in enumerate(SEAM_BIN_LABELS):
            sel = bins == i
            seam[lab]["native"].append(d_n[sel])
            seam[lab]["scaled"].append(d_s[sel])
        per[hid] = {
            "n_pairs": n,
            "mean_delta_K": {"native": float(d_n.mean()), "scaled": float(d_s.mean()), "scaled_minus_native": float(diff.mean())},
            "frac_over_tau_K": {"native": float((d_n > tau_K).mean()), "scaled": float((d_s > tau_K).mean())},
            "fstar": {_tau_key(t): {"native": f_star(d_n, t), "scaled": f_star(d_s, t)} for t in taus},
            "token_diff": {"median": float(np.median(diff)), "p90": float(np.quantile(diff, 0.9)), "max": float(diff.max())},
        }
    mean_diffs = [per[h]["mean_delta_K"]["scaled_minus_native"] for h in ids]
    pooled = np.concatenate(diffs_all)
    seam_out = []
    for lab in SEAM_BIN_LABELS:
        nat, sca = np.concatenate(seam[lab]["native"]), np.concatenate(seam[lab]["scaled"])
        seam_out.append({"bin": lab, "n_tokens": int(len(nat)),
                         "median_native": float(np.median(nat)) if len(nat) else None,
                         "median_scaled": float(np.median(sca)) if len(sca) else None})
    out = {
        "native_config_sha256": sha256_text_file(native.config_path), "scaled_config_sha256": sha256_text_file(scaled.config_path),
        "rope": scaled.rope, "n_handoffs": len(ids), "n_tokens": int(len(pooled)), "tau_K": tau_K,
        "paired_mean_delta_K_scaled_minus_native": {
            **_stats(mean_diffs),
            "bootstrap": bootstrap_median_interval(mean_diffs, make_rng(BOOT_SEED), BOOT_REPS, quantile) | {"seed": BOOT_SEED}},
        "mean_delta_K_median_over_handoffs": {"native": float(np.median([per[h]["mean_delta_K"]["native"] for h in ids])),
                                             "scaled": float(np.median([per[h]["mean_delta_K"]["scaled"] for h in ids]))},
        "fstar_median_over_handoffs": {_tau_key(t): {"native": float(np.median([per[h]["fstar"][_tau_key(t)]["native"] for h in ids])),
                                                     "scaled": float(np.median([per[h]["fstar"][_tau_key(t)]["scaled"] for h in ids]))}
                                       for t in taus},
        "frac_over_tau_K_median_over_handoffs": {"native": float(np.median([per[h]["frac_over_tau_K"]["native"] for h in ids])),
                                                 "scaled": float(np.median([per[h]["frac_over_tau_K"]["scaled"] for h in ids]))},
        "pooled_token_diff": {"median": float(np.median(pooled)), "p10": float(np.quantile(pooled, 0.1)),
                              "p90": float(np.quantile(pooled, 0.9)), "p99": float(np.quantile(pooled, 0.99))},
        "seam_profile_left_pooled": seam_out,
        "per_handoff": per,
        "long_cell": None, "configuration_share": None,
    }
    if long_summary is not None:
        lc = _long_cell(Path(long_summary), taus)
        far = next(r for r in seam_out if r["bin"] == SEAM_FAR)
        share = {"seam_far": _share(far["median_native"], far["median_scaled"], lc["seam_far_median"])}
        for t in taus[1:]:
            k = _tau_key(t)
            share[f"fstar_{k}"] = _share(out["fstar_median_over_handoffs"][k]["native"], out["fstar_median_over_handoffs"][k]["scaled"],
                                         lc["fstar_ladder_median"][k])
        out["long_cell"], out["configuration_share"] = lc, share
    return out


def render(out: dict) -> str:
    fmt = lambda x: "n/a" if x is None else f"{x:.4f}"      # noqa: E731
    pm = out["paired_mean_delta_K_scaled_minus_native"]
    lines = [
        "# E9 scaled short cell vs native (descriptive; decides nothing)", "",
        f"- {out['n_handoffs']} handoffs, {out['n_tokens']:,} matched tokens, identical alignments; scaled receiver `{json.dumps(out['rope'], sort_keys=True)}`.",
        f"- per-handoff mean delta_K, median over handoffs: native {fmt(out['mean_delta_K_median_over_handoffs']['native'])} -> scaled "
        f"{fmt(out['mean_delta_K_median_over_handoffs']['scaled'])}; paired (scaled - native) median {fmt(pm['median'])} "
        f"(p10 {fmt(pm['p10'])}, p90 {fmt(pm['p90'])}; bootstrap [{fmt(pm['bootstrap']['lower_2.5'])}, {fmt(pm['bootstrap']['upper_97.5'])}]).",
        "- f*(tau) median over handoffs, native -> scaled: " + "; ".join(
            f"tau {k}: {fmt(v['native'])} -> {fmt(v['scaled'])}" for k, v in out["fstar_median_over_handoffs"].items()) + ".",
        f"- tokens over tau_K (fraction per handoff, median): native {fmt(out['frac_over_tau_K_median_over_handoffs']['native'])} -> "
        f"scaled {fmt(out['frac_over_tau_K_median_over_handoffs']['scaled'])}.",
        f"- pooled per-token (scaled - native): median {fmt(out['pooled_token_diff']['median'])}, p10 {fmt(out['pooled_token_diff']['p10'])}, "
        f"p90 {fmt(out['pooled_token_diff']['p90'])}, p99 {fmt(out['pooled_token_diff']['p99'])}.",
        "- seam profile b^-(t), pooled median delta_K native -> scaled: " + " · ".join(
            f"{r['bin']}: {fmt(r['median_native'])} -> {fmt(r['median_scaled'])} (n={r['n_tokens']:,})" for r in out["seam_profile_left_pooled"]) + ".",
    ]
    if out["long_cell"]:
        lc, sh = out["long_cell"], out["configuration_share"]
        far = next(r for r in out["seam_profile_left_pooled"] if r["bin"] == SEAM_FAR)
        lines += ["", f"## Against the long cell ({lc['n_handoffs']} handoffs, `{lc['path']}`)", "",
                  f"- far-from-seam ({SEAM_FAR}) median delta_K: native {fmt(far['median_native'])}, scaled {fmt(far['median_scaled'])}, "
                  f"long {fmt(lc['seam_far_median'])} -> configuration reproduces {fmt(sh['seam_far'])} of the cross-cell difference on identical tokens."]
        for k, v in lc["fstar_ladder_median"].items():
            f = out["fstar_median_over_handoffs"][k]
            lines.append(f"- f*(tau {k}) median: native {fmt(f['native'])}, scaled {fmt(f['scaled'])}, long {fmt(v)} -> share {fmt(sh[f'fstar_{k}'])}.")
        lines += ["", "A share near 1 says the receiver configuration accounts for the cross-cell difference; near 0 says the "
                  "handoffs do. Neither is a claim about length alone: the two cells are different handoffs."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e9_compare")
    ap.add_argument("--native", default=str(REPO_ROOT / "config" / "e9.toml"))
    ap.add_argument("--scaled", default=str(REPO_ROOT / "config" / "e9s.toml"))
    ap.add_argument("--long", default=None, help="results/e9l/summary.json: adds the configuration-share reading")
    a = ap.parse_args(argv)
    native, scaled = load_e9_config(Path(a.native), REPO_ROOT), load_e9_config(Path(a.scaled), REPO_ROOT)
    try:
        out = compare(native, scaled, Path(a.long) if a.long else None)
    except (ValueError, RuntimeError) as e:
        print(f"E9 COMPARE REFUSED: {e}")
        return 1
    md = render(out)
    scaled.results_dir.mkdir(parents=True, exist_ok=True)
    (scaled.results_dir / "compare.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (scaled.results_dir / "compare.md").write_text(md, encoding="utf-8", newline="\n")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
