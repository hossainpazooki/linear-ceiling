"""E-TRUNC -- length isolation by HEAD truncation of the sender context on the SAME handoffs (design
docs/drafts/e-trunc-design.md; registration by its own numbered entry). The FULL cell (config/e9t-full.toml,
entry 0035's instrument re-run under this entry's gate) and the truncated levels it names in [e9.trunc]
(S' = S[-L:] for L in 65,536 / 49,152 / 32,768) are each a complete E9 run read by `summarize_e9`; this
module then pairs them token by token.

The paired quantity is the per-token centered deviation delta_K(t) (0023's unit) at the tokens matched under
EVERY level -- the common subset M_cap, identified in the FULL frame as (p_S, p_R) after undoing each level's
offset |S| - L. Alignment is re-run per level because the aligner sees S', so M_cap can shrink two ways:
the receiver re-renders content the truncation removed (physical: those tokens have no sender position in
S'), and the aligner re-matches the rest differently (instability, the design's stated weak point). Both are
reported per handoff BEFORE any reading; a handoff whose |M_cap| is under [e9.trunc] min_common_matched is
VOID for the comparison and listed, and the ratio |M_cap| / |M_FULL| is stated per handoff and pooled, gating
nothing (ruling 2, 2026-10-04).

The pre-registered reading (ruling 1): the far-from-seam (16+, FULL's causal seam frame) pooled MEDIAN
delta_K at L32 on M_cap over the non-void handoffs, against two levels READ from the record, never typed --
entry 0038's scaled-short far-from-seam median (results/e9s/compare.json) and entry 0036's long one
(results/e9l/summary.json). Within +/- margin_abs of the short level: the residual short<->long gap reads as
LENGTH; within the margin of the long level: THE HANDOFFS; between: UNATTRIBUTED, said so. Descriptive; no
hypothesis cell moves.

`--shrinkage` runs BEFORE any prefill (CPU): from the five alignment passes alone (`e9 --align-only` per
config) it states M_cap and the ratio distribution the registration entry carries.

Fail-closed, as `summarize_e9` and `e9_compare`: every level's report must be complete under its committed
config at one pin, every score and per-token record on its recorded hash, every alignment record the same
trace text; refuses on any disagreement. Writes <out_dir>/compare.{json,md} or shrinkage.{json,md}.

usage: python -m linear_ceiling.summarize_e9_trunc [--config config/e9t-full.toml] [--shrinkage]
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e9_config
from linear_ceiling.e7_stats import quantile
from linear_ceiling.e9 import _stem
from linear_ceiling.e9_pertoken import bootstrap_median_interval, f_star, seam_bin, seam_distance_left
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.rng import make_rng
from linear_ceiling.summarize_e9 import SEAM_BIN_LABELS, _stats, _tau_key
from linear_ceiling.e9_compare import _alignment, _delta_K, _report

FULL = "FULL"
READINGS = ("length", "the handoffs", "unattributed")


# ------------------------------------------------------------------------------------------- the levels

def level_label(L: int) -> str:
    return f"L{L}"


def load_levels(full: E9Config, repo_root: Path = REPO_ROOT) -> dict[str, E9Config]:
    """{FULL: cfg, L65536: cfg, ...} in the registered order; refuses unless the levels are one instrument."""
    if full.trunc is None:
        raise ValueError(f"{full.config_path.name} carries no [e9.trunc]; the comparison is read from the FULL cell's config")
    if full.sender_head_truncate is not None:
        raise ValueError("the FULL cell registers no sender_head_truncate")
    out = {FULL: full}
    seen = set()
    for rel in full.trunc["levels"]:
        cfg = load_e9_config(Path(repo_root) / rel, repo_root)
        L = cfg.sender_head_truncate
        if L is None:
            raise ValueError(f"{rel}: a truncated level must register sender_head_truncate")
        if L in seen:
            raise ValueError(f"{rel}: level {L} registered twice")
        seen.add(L)
        out[level_label(L)] = cfg
    _check_levels(full, out)
    return out


def _check_levels(full: E9Config, levels: dict[str, E9Config]) -> None:
    Ls = [c.sender_head_truncate for k, c in levels.items() if k != FULL]
    if any(a <= b for a, b in zip(Ls, Ls[1:])):
        raise ValueError(f"[e9.trunc] levels must be listed with L strictly descending, got {Ls}")
    dirs = set()
    for name, c in levels.items():
        if c.results_dir.resolve() in dirs:
            raise ValueError(f"{name}: two levels write the same results_dir")
        dirs.add(c.results_dir.resolve())
        for field in ("pair", "upstream_sha", "rule", "controls", "mapper_k", "mapper_space", "context_cap",
                      "context_floor", "rope", "keep_seed", "keep_n", "order_by", "bridge", "profiles",
                      "alignment_method", "required_entries"):
            if getattr(c, field) != getattr(full, field):
                raise ValueError(f"{name}: {field} differs from the FULL cell's; the levels are not one instrument")
        if c.sender_head_truncate is not None and c.sender_head_truncate >= c.context_cap:
            raise ValueError(f"{name}: truncation at or above the cap truncates nothing")


# ----------------------------------------------------------------------------- the common subset M_cap

def to_full_frame(pairs: np.ndarray, n_sender: int, L: int | None) -> np.ndarray:
    """A level's (p_S', p_R) pairs restated in the FULL frame: p_S = p_S' + max(0, |S| - L)."""
    off = 0 if L is None else max(0, int(n_sender) - int(L))
    out = np.array(pairs, dtype=np.int64, copy=True)
    out[:, 0] += off
    return out


def common_subset(pairs_by_level: dict[str, np.ndarray], n_sender: int,
                  L_by_level: dict[str, int | None]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """M_cap as FULL-frame pairs (sorted), and per level the row index of each M_cap token in that level's
    own pairs array (so a level's per-token record can be gathered at exactly those tokens)."""
    index = {}
    common = None
    for name, p in pairs_by_level.items():
        ff = to_full_frame(p, n_sender, L_by_level[name])
        keys = {(int(a), int(b)): i for i, (a, b) in enumerate(ff.tolist())}
        if len(keys) != len(ff):
            raise ValueError(f"{name}: duplicate matched pairs in the alignment")
        index[name] = keys
        common = set(keys) if common is None else common & set(keys)
    common = sorted(common or ())
    rows = {name: np.asarray([index[name][k] for k in common], dtype=np.int64) for name in pairs_by_level}
    return np.asarray(common, dtype=np.int64).reshape(-1, 2), rows


def _coverage(cfg: E9Config, who: str) -> dict:
    p = cfg.results_dir / "align" / "coverage.json"
    if not p.exists():
        raise ValueError(f"{who}: {p} is missing; run `e9 --align-only --config {cfg.config_path.name}` first")
    cov = json.loads(p.read_text(encoding="utf-8"))
    if cov.get("config_sha256") != sha256_text_file(cfg.config_path):
        raise ValueError(f"{who}: coverage.json was written under another {cfg.config_path.name}")
    if (cov.get("sender_head_truncate") or None) != cfg.sender_head_truncate:
        raise ValueError(f"{who}: coverage.json records truncation {cov.get('sender_head_truncate')!r}, "
                         f"config registers {cfg.sender_head_truncate!r}")
    return cov


def _same_trace(recs: dict[str, dict], hid: str) -> dict:
    """The alignment records of one handoff across levels describe the same trace text and lengths."""
    first_name, first = next(iter(recs.items()))
    for name, r in recs.items():
        for key in ("n_sender", "n_receiver", "text_sha256", "excluded"):
            if r.get(key) != first.get(key):
                raise ValueError(f"{hid}: alignment {key} differs between {first_name} and {name} "
                                 f"({first.get(key)!r} vs {r.get(key)!r}); not the same handoff")
    return first


def shrinkage(levels: dict[str, E9Config]) -> dict:
    """Pre-prefill (CPU): |M_FULL|, |M_L| and |M_cap| per handoff from the alignment passes alone, the ratio
    |M_cap| / |M_FULL| per handoff and pooled, the void set under the floor, and -- because the design names
    aligner instability as its weak point -- the loss split into what the truncation REMOVED (matched tokens
    whose FULL sender position lies before |S| - L_min) and what re-matching lost on top."""
    full = levels[FULL]
    floor = int(full.trunc["min_common_matched"])
    L_by = {name: c.sender_head_truncate for name, c in levels.items()}
    L_min = min(L for L in L_by.values() if L is not None)
    covs = {name: _coverage(c, name) for name, c in levels.items()}
    recs = {name: {a["handoff_id"]: a for a in cov["alignments"]} for name, cov in covs.items()}
    ids = sorted(h for h, r in recs[FULL].items() if not r["excluded"])
    for name, rr in recs.items():
        if sorted(h for h, r in rr.items() if not r["excluded"]) != ids:
            raise ValueError(f"{name}: included set differs from the FULL cell's; truncation must not move inclusion")
    per = {}
    for hid in ids:
        rec = _same_trace({name: rr[hid] for name, rr in recs.items()}, hid)
        pairs = {name: _alignment(c, hid)["pairs"] for name, c in levels.items()}
        for name, p in pairs.items():
            if int(p.shape[0]) != int(recs[name][hid]["n_matched"]):
                raise ValueError(f"{name} {hid}: stored pairs ({p.shape[0]}) do not match the record's n_matched")
        m_cap, _ = common_subset(pairs, int(rec["n_sender"]), L_by)
        n_full, n_cap = int(pairs[FULL].shape[0]), int(m_cap.shape[0])
        survivable = float((pairs[FULL][:, 0] >= int(rec["n_sender"]) - L_min).mean()) if n_full else 0.0
        ratio = n_cap / n_full if n_full else 0.0
        per[hid] = {"n_sender": int(rec["n_sender"]), "n_receiver": int(rec["n_receiver"]),
                    "n_matched_full": n_full, "n_common": n_cap, "ratio": ratio, "void": n_cap < floor,
                    "survivable_fraction": survivable,            # physical: FULL pairs inside S[-L_min:]
                    "rematching_loss": survivable - ratio,        # what the aligner lost beyond the removal
                    "n_matched_by_level": {name: int(p.shape[0]) for name, p in pairs.items()},
                    "identical_to_full": {name: bool(L is None or int(rec["n_sender"]) <= L) for name, L in L_by.items()}}
    ratios = [per[h]["ratio"] for h in ids]
    void = sorted(h for h in ids if per[h]["void"])
    n_cap_tot, n_full_tot = sum(per[h]["n_common"] for h in ids), sum(per[h]["n_matched_full"] for h in ids)
    return {
        "levels": {name: {"sender_head_truncate": L_by[name], "config_sha256": sha256_text_file(c.config_path),
                          "coverage_sha256": sha256_file_bytes(c.results_dir / "align" / "coverage.json")}
                   for name, c in levels.items()},
        "min_common_matched": floor, "n_handoffs": len(ids),
        "ratio": _stats(ratios) | {"min": min(ratios) if ratios else None, "max": max(ratios) if ratios else None},
        "pooled_ratio": (n_cap_tot / n_full_tot) if n_full_tot else None,
        "n_common_total": n_cap_tot, "n_matched_full_total": n_full_tot,
        "n_common": _stats(per[h]["n_common"] for h in ids),
        "void": void, "n_void": len(void), "n_zero": sum(1 for h in ids if per[h]["n_common"] == 0),
        "n_below_0_80": sum(1 for r in ratios if r < 0.80),       # the run queue's default gate, stated for the record
        "survivable_fraction": _stats(per[h]["survivable_fraction"] for h in ids),
        "rematching_loss": _stats(per[h]["rematching_loss"] for h in ids) | {"max": max(per[h]["rematching_loss"] for h in ids)},
        "n_with_rematching_loss_over_0_05": sum(1 for h in ids if per[h]["rematching_loss"] > 0.05),
        "per_handoff": per,
    }


# ---------------------------------------------------------------------------------- the paired reading

def reading(l32_far_median: float, short_level: float, long_level: float, margin: float) -> str:
    near_short = abs(l32_far_median - short_level) <= margin
    near_long = abs(l32_far_median - long_level) <= margin
    if near_short and near_long:
        raise ValueError(f"the margin {margin} spans both reference levels ({short_level}, {long_level}); the reading is undefined")
    return "length" if near_short else "the handoffs" if near_long else "unattributed"


def _references(full: E9Config, repo_root: Path) -> dict:
    """The two levels the reading is measured against, READ from the record with their hashes."""
    bin_ = full.trunc["seam_far_bin"]
    sp = Path(repo_root) / full.trunc["short_scaled_compare"]
    lp = Path(repo_root) / full.trunc["long_summary"]
    for p in (sp, lp):
        if not p.exists():
            raise ValueError(f"reference record {p} is missing; the reading cannot be measured against a typed number")
    comp = json.loads(sp.read_text(encoding="utf-8"))
    lsum = json.loads(lp.read_text(encoding="utf-8"))
    try:
        short = next(r["median_scaled"] for r in comp["seam_profile_left_pooled"] if r["bin"] == bin_)
        long_ = next(r["median"] for r in lsum["seam_profile_left_pooled"]["same_K"] if r["bin"] == bin_)
    except (KeyError, StopIteration, TypeError) as e:
        raise ValueError(f"reference records lack the {bin_} far-from-seam medians: {e}")
    if short is None or long_ is None:
        raise ValueError("a reference far-from-seam median is null; nothing to read against")
    return {"seam_far_bin": bin_, "short_scaled": {"path": full.trunc["short_scaled_compare"], "sha256": sha256_file_bytes(sp),
                                                   "far_median": float(short), "n_handoffs": int(comp["n_handoffs"])},
            "long": {"path": full.trunc["long_summary"], "sha256": sha256_file_bytes(lp), "far_median": float(long_),
                     "n_handoffs": int(lsum["coverage"].get("scored", lsum["coverage"]["included"]))}}


def compare_levels(levels: dict[str, E9Config], repo_root: Path = REPO_ROOT) -> dict:
    full = levels[FULL]
    floor, margin = int(full.trunc["min_common_matched"]), float(full.trunc["margin_abs"])
    bin_far = full.trunc["seam_far_bin"]
    if bin_far not in SEAM_BIN_LABELS:
        raise ValueError(f"seam_far_bin {bin_far!r} is not one of the registered bins {SEAM_BIN_LABELS}")
    far_i = SEAM_BIN_LABELS.index(bin_far)
    refs = _references(full, repo_root)
    reps = {name: _report(c, name) for name, c in levels.items()}
    pins = {name: {"config_sha256": sha256_text_file(c.config_path),
                   "report_sha256": sha256_file_bytes(c.results_dir / "report.json"),
                   "upstream_sha": reps[name].get("upstream_sha"), "partial": bool(reps[name].get("partial"))}
            for name, c in levels.items()}
    if len({p["upstream_sha"] for p in pins.values()}) != 1:
        raise ValueError("the levels were run under different upstream pins")
    scored = {name: set(rep.get("scores") or {}) for name, rep in reps.items()}
    common_scored = sorted(set.intersection(*scored.values()))
    if not common_scored:
        raise ValueError("no handoff is scored at every level; the comparison is empty")
    everywhere = set.union(*scored.values())
    unscored = {name: sorted(everywhere - s) for name, s in scored.items()}     # what THIS level did not score
    al = {name: {a["handoff_id"]: a for a in rep.get("alignments") or []} for name, rep in reps.items()}
    L_by = {name: c.sender_head_truncate for name, c in levels.items()}
    tau_K = float(full.rule["tau_K"])
    taus = [tau_K] + [float(t) for t in full.rule["tau_ladder"]]
    names = list(levels)
    per, void = {}, []
    far_tokens = {name: [] for name in names}
    for hid in common_scored:
        rec = _same_trace({name: al[name][hid] for name in names}, hid)
        pairs = {name: _alignment(c, hid)["pairs"] for name, c in levels.items()}
        m_cap, rows = common_subset(pairs, int(rec["n_sender"]), L_by)
        n_cap = int(m_cap.shape[0])
        entry = {"n_matched_full": int(pairs[FULL].shape[0]), "n_common": n_cap,
                 "ratio": n_cap / int(pairs[FULL].shape[0]) if pairs[FULL].shape[0] else 0.0, "void": n_cap < floor}
        if entry["void"]:
            void.append(hid)
            per[hid] = entry
            continue
        deltas = {}
        for name, c in levels.items():
            d, n = _delta_K(c, reps[name], hid, name)
            if n != int(pairs[name].shape[0]):
                raise ValueError(f"{name} {hid}: per-token record length {n} != matched pairs {pairs[name].shape[0]}")
            deltas[name] = d[rows[name]]
        # seams in the FULL frame: b^-(t) from the FULL alignment, gathered at the M_cap tokens
        b_full = seam_distance_left(pairs[FULL], int(rec["n_receiver"]))[rows[FULL]]
        bins = seam_bin(b_full)
        far_sel = bins == far_i
        entry["levels"] = {}
        for name in names:
            d = deltas[name]
            far_tokens[name].append(d[far_sel])
            entry["levels"][name] = {
                "mean_delta_K": float(d.mean()), "frac_over_tau_K": float((d > tau_K).mean()),
                "fstar": {_tau_key(t): f_star(d, t) for t in taus},
                "far_from_seam": {"n_tokens": int(far_sel.sum()),
                                  "mean": float(d[far_sel].mean()) if far_sel.any() else None,
                                  "median": float(np.median(d[far_sel])) if far_sel.any() else None},
                "paired_vs_full": {"mean_diff": float((d - deltas[FULL]).mean()),
                                   "median_token_diff": float(np.median(d - deltas[FULL]))},
            }
        per[hid] = entry
    used = [h for h in common_scored if not per[h]["void"]]
    if not used:
        raise ValueError(f"every scored handoff is void under the floor {floor}; the comparison says nothing")
    seed, reps_n = int(full.trunc["bootstrap_seed"]), int(full.trunc["bootstrap_reps"])
    by_level = {}
    for name in names:
        pooled_far = np.concatenate(far_tokens[name]) if far_tokens[name] else np.zeros(0)
        diffs = [per[h]["levels"][name]["paired_vs_full"]["mean_diff"] for h in used]
        by_level[name] = {
            "sender_head_truncate": L_by[name], "n_handoffs": len(used),
            "mean_delta_K_median_over_handoffs": float(np.median([per[h]["levels"][name]["mean_delta_K"] for h in used])),
            "frac_over_tau_K_median_over_handoffs": float(np.median([per[h]["levels"][name]["frac_over_tau_K"] for h in used])),
            "fstar_median_over_handoffs": {_tau_key(t): float(np.median([per[h]["levels"][name]["fstar"][_tau_key(t)] for h in used])) for t in taus},
            "far_from_seam_pooled": {"bin": bin_far, "n_tokens": int(len(pooled_far)),
                                     "median": float(np.median(pooled_far)) if len(pooled_far) else None,
                                     "mean": float(pooled_far.mean()) if len(pooled_far) else None},
            "paired_mean_delta_K_minus_full": _stats(diffs) | {
                "bootstrap": bootstrap_median_interval(diffs, make_rng(seed), reps_n, quantile) | {"seed": seed, "reps": reps_n}},
        }
    l32_name = min((n for n in names if n != FULL), key=lambda n: L_by[n])
    l32_far = by_level[l32_name]["far_from_seam_pooled"]["median"]
    if l32_far is None:
        raise ValueError(f"{l32_name} has no far-from-seam token on M_cap; the registered reading has nothing to read")
    verdict = reading(l32_far, refs["short_scaled"]["far_median"], refs["long"]["far_median"], margin)
    return {
        "levels": pins, "upstream_sha": next(iter(pins.values()))["upstream_sha"], "tau_K": tau_K,
        "min_common_matched": floor, "margin_abs": margin, "references": refs,
        "n_scored_at_every_level": len(common_scored), "unscored_by_level": unscored,
        "void": sorted(void), "n_void": len(void), "n_used": len(used),
        "n_common_total": int(sum(per[h]["n_common"] for h in used)),
        "pooled_ratio_used": float(sum(per[h]["n_common"] for h in used) / sum(per[h]["n_matched_full"] for h in used)),
        "by_level": by_level,
        "reading": {"level": l32_name, "far_from_seam_median_on_M_cap": l32_far,
                    "full_far_from_seam_median_on_M_cap": by_level[FULL]["far_from_seam_pooled"]["median"],
                    "short_scaled_level": refs["short_scaled"]["far_median"], "long_level": refs["long"]["far_median"],
                    "margin_abs": margin, "reads_as": verdict,
                    "note": "pre-registered (ruling 1, 2026-10-04): the far-from-seam pooled MEDIAN delta_K at the native-cap "
                            "level on M_cap, within the margin of the scaled-short level reads as LENGTH, within the margin of "
                            "the long level reads as THE HANDOFFS, between reads as UNATTRIBUTED. M_cap sits at late sender "
                            "positions; the reference medians were pooled over full matched sets. Descriptive; no cell moves."},
        "per_handoff": per,
    }


# --------------------------------------------------------------------------------------- rendering

def render_shrinkage(s: dict) -> str:
    fmt = lambda x: "n/a" if x is None else f"{x:.4f}"      # noqa: E731
    r = s["ratio"]
    lines = ["# E-TRUNC shrinkage pre-check (CPU, from the alignment passes; decides nothing)", "",
             f"- {s['n_handoffs']} handoffs; levels " + ", ".join(f"{k} (L={v['sender_head_truncate']})" for k, v in s["levels"].items()) + ".",
             f"- |M_cap| / |M_FULL| per handoff: median {fmt(r['median'])} (p10 {fmt(r['p10'])}, p90 {fmt(r['p90'])}; min {fmt(r['min'])}, max {fmt(r['max'])}); "
             f"pooled {fmt(s['pooled_ratio'])} ({s['n_common_total']:,} of {s['n_matched_full_total']:,} matched tokens).",
             f"- void under |M_cap| >= {s['min_common_matched']}: {s['n_void']} handoffs ({s['n_zero']} with |M_cap| = 0); "
             f"below the 0.80 ratio the run queue proposed: {s['n_below_0_80']}.",
             f"- survivable fraction (FULL pairs inside the shortest window): median {fmt(s['survivable_fraction']['median'])}; "
             f"re-matching loss beyond removal: median {fmt(s['rematching_loss']['median'])}, max {fmt(s['rematching_loss']['max'])}, "
             f"over 0.05 on {s['n_with_rematching_loss_over_0_05']} handoffs."]
    if s["void"]:
        lines.append("- void: " + "; ".join(f"`{h}`" for h in s["void"]))
    return "\n".join(lines) + "\n"


def render(out: dict) -> str:
    fmt = lambda x: "n/a" if x is None else f"{x:.4f}"      # noqa: E731
    rd = out["reading"]
    lines = ["# E-TRUNC paired comparison across truncation levels (descriptive; decides nothing)", "",
             f"- {out['n_scored_at_every_level']} handoffs scored at every level; {out['n_void']} void under |M_cap| >= {out['min_common_matched']}; "
             f"{out['n_used']} compared on {out['n_common_total']:,} common tokens (pooled ratio {fmt(out['pooled_ratio_used'])}); upstream `{out['upstream_sha'][:12]}`."]
    for name, b in out["by_level"].items():
        pm = b["paired_mean_delta_K_minus_full"]
        lines.append(f"- {name} (L={b['sender_head_truncate']}): mean delta_K median over handoffs {fmt(b['mean_delta_K_median_over_handoffs'])}; "
                     f"tokens over tau_K {fmt(b['frac_over_tau_K_median_over_handoffs'])}; f*: " +
                     ", ".join(f"tau {k} {fmt(v)}" for k, v in b["fstar_median_over_handoffs"].items()) +
                     f"; far-from-seam ({b['far_from_seam_pooled']['bin']}) pooled median {fmt(b['far_from_seam_pooled']['median'])} / mean "
                     f"{fmt(b['far_from_seam_pooled']['mean'])} (n={b['far_from_seam_pooled']['n_tokens']:,}); paired (level - FULL) mean delta_K median "
                     f"{fmt(pm['median'])} (bootstrap [{fmt(pm['bootstrap']['lower_2.5'])}, {fmt(pm['bootstrap']['upper_97.5'])}]).")
    lines += ["", f"## The registered reading ({rd['level']}, far-from-seam median on M_cap)", "",
              f"- {fmt(rd['far_from_seam_median_on_M_cap'])} against scaled-short {fmt(rd['short_scaled_level'])} and long {fmt(rd['long_level'])} "
              f"(FULL on the same tokens: {fmt(rd['full_far_from_seam_median_on_M_cap'])}); margin +/- {rd['margin_abs']} -> **reads as {rd['reads_as']}**.",
              f"- {rd['note']}"]
    if out["void"]:
        lines.append("- void: " + "; ".join(f"`{h}`" for h in out["void"]))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e9_trunc")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9t-full.toml"))
    ap.add_argument("--shrinkage", action="store_true",
                    help="pre-prefill: M_cap and the ratio distribution from the alignment passes alone")
    a = ap.parse_args(argv)
    full = load_e9_config(Path(a.config), REPO_ROOT)
    try:
        levels = load_levels(full)
        out_dir = REPO_ROOT / full.trunc["out_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.shrinkage:
            s = shrinkage(levels)
            md = render_shrinkage(s)
            (out_dir / "shrinkage.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
            (out_dir / "shrinkage.md").write_text(md, encoding="utf-8", newline="\n")
            print(md)
            return 0
        from linear_ceiling.summarize_e9 import summarize       # the gate: every level's own fail-closed reader first
        for name, cfg in levels.items():
            print(f"[{name}] summarize_e9 --config {cfg.config_path.name}")
            summarize(cfg, runner=subprocess.run)
        out = compare_levels(levels)
    except (ValueError, RuntimeError) as e:
        print(f"E-TRUNC SUMMARY REFUSED: {e}")
        return 1
    md = render(out)
    (out_dir / "compare.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (out_dir / "compare.md").write_text(md, encoding="utf-8", newline="\n")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
