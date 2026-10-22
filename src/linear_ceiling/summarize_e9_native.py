"""E-TRUNC, the L32-NATIVE cell -- the sender head-truncated to S' = S[-L:] at the native cap, as the L32 level of
entry 0055, with BOTH models under their native RoPE (operator ruling A, 2026-10-13; registration by its own numbered
entry). The cell (config/e9t-l32n.toml) is a complete E9 run read by `summarize_e9`, whose native-window control on a
truncated native cell reads the longest DUMPED length against each dump's recorded window; this module then pairs it
token by token with the YaRN level of the same L (config/e9t-l32.toml, entry 0057's run).

Same tokens, by construction: the two cells see the same S' and the same R through the same aligner, so their matched
sets must be IDENTICAL per handoff, and the reader refuses otherwise rather than intersecting them. The paired quantity
is the per-token centered deviation delta_K(t) (0023's unit) on M_cap -- the subset matched under EVERY level of the
E-TRUNC instrument, re-derived here from the FULL cell's [e9.trunc] levels exactly as `summarize_e9_trunc` derives it,
so the native level's far-from-seam median is read on the tokens entry 0057's reading was read on. A handoff whose
|M_cap| is under [e9.trunc] min_common_matched is VOID, as there; the void set must equal the record's.

The pre-registered reading: the far-from-seam (16+, FULL's causal seam frame) pooled MEDIAN delta_K of the NATIVE level
on M_cap over the non-void handoffs, against two levels READ from the record, never typed -- entry 0038's native-short
far-from-seam median (results/e9s/compare.json, `median_native`) and entry 0057's YaRN-L32 median on M_cap
(results/e9t/compare.json, recomputed here on the same tokens and refused on disagreement). Within +/- margin_abs of the
native-short level: the L32 excess over the short cell was THE SCALING (the YaRN receiver); within the margin of the
YaRN-L32 level: NOT THE SCALING (a native receiver reproduces it); between: UNATTRIBUTED, said so. Descriptive; no
hypothesis cell moves. Beside it, the paired difference native - YaRN per handoff (mean over M_cap tokens), median over
handoffs with a seeded percentile bootstrap.

`--alignment-check` runs BEFORE any prefill (CPU): from the native cell's alignment pass and the four levels' it states
that the native matched sets equal the YaRN level's, the M_cap counts and the void set, and the longest dumped length
(S' + 1 or R) the registration entry carries.

Fail-closed, as `summarize_e9_trunc`: every cell's report complete under its committed config at one pin, every score
and per-token record on its recorded hash, every alignment record the same trace text, the reference records at the
hashes the comparison states. Writes <out_dir>/compare.{json,md} or alignment.{json,md}.

usage: python -m linear_ceiling.summarize_e9_native [--config config/e9t-l32n.toml] [--alignment-check]
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e9_config
from linear_ceiling.e7_stats import quantile
from linear_ceiling.e9_compare import _alignment, _delta_K, _report
from linear_ceiling.e9_pertoken import bootstrap_median_interval, f_star, seam_bin, seam_distance_left
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.rng import make_rng
from linear_ceiling.summarize_e9 import SEAM_BIN_LABELS, _dumped_sender_len, _stats, _tau_key
from linear_ceiling.summarize_e9_trunc import FULL, _coverage, _same_trace, common_subset, level_label, load_levels

NATIVE = "NATIVE"
READINGS = ("the scaling", "not the scaling", "unattributed")
_YARN_TOL = 1e-12       # the YaRN level's far-from-seam median, recomputed on the same tokens, against the record's

# what the native cell must share with the YaRN level it pairs with: one instrument but for the RoPE
_SAME = ("pair", "upstream_sha", "rule", "controls", "mapper_k", "mapper_space", "context_cap", "context_floor",
         "keep_seed", "keep_n", "order_by", "profiles", "alignment_method", "sender_head_truncate")


# ------------------------------------------------------------------------------------------- the cells

def load_cells(native: E9Config, repo_root: Path = REPO_ROOT) -> tuple[dict[str, E9Config], str]:
    """{NATIVE: cfg, FULL: cfg, L65536: ..., L32768: ...} and the name of the YaRN level the native cell pairs with;
    refuses unless the native cell and that level are one instrument but for the RoPE."""
    if native.native is None:
        raise ValueError(f"{native.config_path.name} carries no [e9.native]; the comparison is read from the native cell's config")
    if native.rope is not None or native.bridge is not None:
        raise ValueError("the native cell registers no [e9.rope] and no [e9.bridge]")
    if not native.sender_head_truncate:
        raise ValueError("the native cell must register sender_head_truncate; at full length it is the short cell")
    full = load_e9_config(Path(repo_root) / native.native["full_config"], repo_root)
    levels = load_levels(full, repo_root)
    yarn = load_e9_config(Path(repo_root) / native.native["yarn_level"], repo_root)
    name = level_label(yarn.sender_head_truncate) if yarn.sender_head_truncate else None
    if name not in levels or sha256_text_file(levels[name].config_path) != sha256_text_file(yarn.config_path):
        raise ValueError(f"[e9.native] yarn_level {native.native['yarn_level']} is not one of the FULL cell's [e9.trunc] levels")
    if yarn.rope is None:
        raise ValueError(f"{name} carries no [e9.rope]; nothing scaled to pair the native cell with")
    for field in _SAME:
        if getattr(native, field) != getattr(yarn, field):
            raise ValueError(f"NATIVE: {field} differs from {name}'s; the two cells are not one instrument")
    if native.results_dir.resolve() in {c.results_dir.resolve() for c in levels.values()}:
        raise ValueError("the native cell writes a level's results_dir")
    return {NATIVE: native, **levels}, name


def _dumped_length(cfg: E9Config, n_sender: int, n_receiver: int) -> int:
    """The longest position one handoff's dumps ask for: S' plus R's first token (the prefix control), or R."""
    return max(_dumped_sender_len(cfg, n_sender) + 1, int(n_receiver))


# ------------------------------------------------------------------------------------ before any prefill

def alignment_check(cells: dict[str, E9Config], yarn_name: str) -> dict:
    """Pre-prefill (CPU): the native cell's matched sets equal the YaRN level's per handoff, M_cap and the void set from
    the four levels' passes (as `summarize_e9_trunc --shrinkage` states them), and the longest dumped length."""
    native, full = cells[NATIVE], cells[FULL]
    floor = int(full.trunc["min_common_matched"])
    L_by = {name: c.sender_head_truncate for name, c in cells.items()}
    covs = {name: _coverage(c, name) for name, c in cells.items()}
    recs = {name: {a["handoff_id"]: a for a in cov["alignments"]} for name, cov in covs.items()}
    ids = sorted(h for h, r in recs[FULL].items() if not r["excluded"])
    for name, rr in recs.items():
        if sorted(h for h, r in rr.items() if not r["excluded"]) != ids:
            raise ValueError(f"{name}: included set differs from the FULL cell's; the native cell must keep the same handoffs")
    per = {}
    for hid in ids:
        rec = _same_trace({name: rr[hid] for name, rr in recs.items()}, hid)
        pairs = {name: _alignment(c, hid)["pairs"] for name, c in cells.items()}
        for name, p in pairs.items():
            if int(p.shape[0]) != int(recs[name][hid]["n_matched"]):
                raise ValueError(f"{name} {hid}: stored pairs ({p.shape[0]}) do not match the record's n_matched")
        if not np.array_equal(pairs[NATIVE], pairs[yarn_name]):
            raise ValueError(f"{hid}: the native cell's matched set differs from {yarn_name}'s "
                             f"({pairs[NATIVE].shape[0]} vs {pairs[yarn_name].shape[0]} pairs); not the same tokens")
        m_cap, _ = common_subset({n: p for n, p in pairs.items() if n != NATIVE}, int(rec["n_sender"]), L_by)
        n_cap = int(m_cap.shape[0])
        per[hid] = {"n_sender": int(rec["n_sender"]), "n_receiver": int(rec["n_receiver"]),
                    "n_matched": int(pairs[NATIVE].shape[0]), "identical_to_yarn": True,
                    "n_common": n_cap, "void": n_cap < floor,
                    "dumped_sender": _dumped_sender_len(native, int(rec["n_sender"])),
                    "dumped_length": _dumped_length(native, int(rec["n_sender"]), int(rec["n_receiver"]))}
    void = sorted(h for h in ids if per[h]["void"])
    used = [h for h in ids if not per[h]["void"]]
    return {
        "cells": {name: {"sender_head_truncate": L_by[name], "rope": c.rope, "config_sha256": sha256_text_file(c.config_path),
                         "coverage_sha256": sha256_file_bytes(c.results_dir / "align" / "coverage.json")}
                  for name, c in cells.items()},
        "yarn_level": yarn_name, "min_common_matched": floor, "n_handoffs": len(ids), "n_identical_to_yarn": len(ids),
        "void": void, "n_void": len(void), "n_used": len(used),
        "n_common_total": int(sum(per[h]["n_common"] for h in used)),
        "n_matched_total": int(sum(per[h]["n_matched"] for h in ids)),
        "max_dumped_sender": max(per[h]["dumped_sender"] for h in ids),
        "max_n_receiver": max(per[h]["n_receiver"] for h in ids),
        "max_dumped_length": max(per[h]["dumped_length"] for h in ids),
        "per_handoff": per,
    }


# ---------------------------------------------------------------------------------- the paired reading

def reading(native_far_median: float, short_native_level: float, yarn_level: float, margin: float) -> str:
    near_short = abs(native_far_median - short_native_level) <= margin
    near_yarn = abs(native_far_median - yarn_level) <= margin
    if near_short and near_yarn:
        raise ValueError(f"the margin {margin} spans both reference levels ({short_native_level}, {yarn_level}); the reading is undefined")
    return "the scaling" if near_short else "not the scaling" if near_yarn else "unattributed"


def _references(native: E9Config, yarn_name: str, repo_root: Path) -> dict:
    """The two levels the reading is measured against, READ from the record with their hashes."""
    bin_ = str(load_e9_config(Path(repo_root) / native.native["full_config"], repo_root).trunc["seam_far_bin"])
    sp = Path(repo_root) / native.native["short_native_compare"]
    tp = Path(repo_root) / native.native["trunc_compare"]
    for p in (sp, tp):
        if not p.exists():
            raise ValueError(f"reference record {p} is missing; the reading cannot be measured against a typed number")
    comp = json.loads(sp.read_text(encoding="utf-8"))
    trunc = json.loads(tp.read_text(encoding="utf-8"))
    try:
        short = next(r["median_native"] for r in comp["seam_profile_left_pooled"] if r["bin"] == bin_)
        rd = trunc["reading"]
        yarn = rd["far_from_seam_median_on_M_cap"]
        if rd["level"] != yarn_name or trunc["by_level"][yarn_name]["far_from_seam_pooled"]["bin"] != bin_:
            raise ValueError(f"the E-TRUNC record read its {rd['level']} level on bin "
                             f"{trunc['by_level'][rd['level']]['far_from_seam_pooled']['bin']}, not {yarn_name} on {bin_}")
    except (KeyError, StopIteration, TypeError) as e:
        raise ValueError(f"reference records lack the {bin_} far-from-seam medians: {e}")
    if short is None or yarn is None:
        raise ValueError("a reference far-from-seam median is null; nothing to read against")
    return {"seam_far_bin": bin_,
            "short_native": {"path": native.native["short_native_compare"], "sha256": sha256_file_bytes(sp),
                             "far_median": float(short), "n_handoffs": int(comp["n_handoffs"])},
            "yarn": {"path": native.native["trunc_compare"], "sha256": sha256_file_bytes(tp), "level": yarn_name,
                     "far_median": float(yarn), "n_used": int(trunc["n_used"]), "void": sorted(trunc["void"]),
                     "yarn_report_sha256": trunc["levels"][yarn_name]["report_sha256"],
                     "min_common_matched": int(trunc["min_common_matched"])}}


def compare_native(cells: dict[str, E9Config], yarn_name: str, repo_root: Path = REPO_ROOT) -> dict:
    native, full = cells[NATIVE], cells[FULL]
    floor, margin = int(full.trunc["min_common_matched"]), float(native.native["margin_abs"])
    bin_far = str(full.trunc["seam_far_bin"])
    if bin_far not in SEAM_BIN_LABELS:
        raise ValueError(f"seam_far_bin {bin_far!r} is not one of the registered bins {SEAM_BIN_LABELS}")
    far_i = SEAM_BIN_LABELS.index(bin_far)
    refs = _references(native, yarn_name, repo_root)
    if refs["yarn"]["min_common_matched"] != floor:
        raise ValueError(f"the E-TRUNC record was read under floor {refs['yarn']['min_common_matched']}, the FULL cell registers {floor}")
    reps = {name: _report(c, name) for name, c in cells.items()}
    pins = {name: {"config_sha256": sha256_text_file(c.config_path),
                   "report_sha256": sha256_file_bytes(c.results_dir / "report.json"),
                   "upstream_sha": reps[name].get("upstream_sha"), "partial": bool(reps[name].get("partial"))}
            for name, c in cells.items()}
    if len({p["upstream_sha"] for p in pins.values()}) != 1:
        raise ValueError("the cells were run under different upstream pins")
    if pins[yarn_name]["report_sha256"] != refs["yarn"]["yarn_report_sha256"]:
        raise ValueError(f"{yarn_name}'s report.json is not the one the E-TRUNC record was read from")
    scored = {name: set(rep.get("scores") or {}) for name, rep in reps.items()}
    common_scored = sorted(set.intersection(*scored.values()))
    if not common_scored:
        raise ValueError("no handoff is scored at the native cell and every level; the comparison is empty")
    everywhere = set.union(*scored.values())
    unscored = {name: sorted(everywhere - s) for name, s in scored.items()}
    al = {name: {a["handoff_id"]: a for a in rep.get("alignments") or []} for name, rep in reps.items()}
    L_by = {name: c.sender_head_truncate for name, c in cells.items()}
    tau_K = float(native.rule["tau_K"])
    taus = [tau_K] + [float(t) for t in native.rule["tau_ladder"]]
    pair_names = (NATIVE, yarn_name)
    per, void = {}, []
    far_tokens = {name: [] for name in pair_names}
    for hid in common_scored:
        rec = _same_trace({name: al[name][hid] for name in cells}, hid)
        pairs = {name: _alignment(c, hid)["pairs"] for name, c in cells.items()}
        if not np.array_equal(pairs[NATIVE], pairs[yarn_name]):
            raise ValueError(f"{hid}: the native cell's matched set differs from {yarn_name}'s; not the same tokens")
        m_cap, rows = common_subset(pairs, int(rec["n_sender"]), L_by)
        n_cap = int(m_cap.shape[0])
        entry = {"n_matched_full": int(pairs[FULL].shape[0]), "n_matched": int(pairs[NATIVE].shape[0]), "n_common": n_cap,
                 "ratio": n_cap / int(pairs[FULL].shape[0]) if pairs[FULL].shape[0] else 0.0, "void": n_cap < floor,
                 "dumped_length": _dumped_length(native, int(rec["n_sender"]), int(rec["n_receiver"]))}
        if entry["void"]:
            void.append(hid)
            per[hid] = entry
            continue
        deltas = {}
        for name in pair_names:
            d, n = _delta_K(cells[name], reps[name], hid, name)
            if n != int(pairs[name].shape[0]):
                raise ValueError(f"{name} {hid}: per-token record length {n} != matched pairs {pairs[name].shape[0]}")
            deltas[name] = d[rows[name]]
        b_full = seam_distance_left(pairs[FULL], int(rec["n_receiver"]))[rows[FULL]]
        far_sel = seam_bin(b_full) == far_i
        entry["cells"] = {}
        for name in pair_names:
            d = deltas[name]
            far_tokens[name].append(d[far_sel])
            entry["cells"][name] = {
                "mean_delta_K": float(d.mean()), "frac_over_tau_K": float((d > tau_K).mean()),
                "fstar": {_tau_key(t): f_star(d, t) for t in taus},
                "far_from_seam": {"n_tokens": int(far_sel.sum()),
                                  "mean": float(d[far_sel].mean()) if far_sel.any() else None,
                                  "median": float(np.median(d[far_sel])) if far_sel.any() else None}}
        diff = deltas[NATIVE] - deltas[yarn_name]
        entry["paired_native_minus_yarn"] = {"mean_diff": float(diff.mean()), "median_token_diff": float(np.median(diff)),
                                             "far_from_seam_mean_diff": float(diff[far_sel].mean()) if far_sel.any() else None}
        per[hid] = entry
    used = [h for h in common_scored if not per[h]["void"]]
    if not used:
        raise ValueError(f"every scored handoff is void under the floor {floor}; the comparison says nothing")
    # The void set is M_cap's, so on the handoffs this run scored it must be the record's. A native run closed partial
    # (allow_partial; the registered order is longest sender first) compares on the commonly scored prefix: the YaRN
    # level is then recomputed on THOSE tokens and read against, and the record's figure over its full used set is
    # stated beside it; a complete run must reproduce the record's figure exactly.
    record_void = set(refs["yarn"]["void"])
    if {h for h in common_scored if h in record_void} != set(void):
        raise ValueError(f"the void set on the scored handoffs ({len(void)}) differs from the E-TRUNC record's; "
                         "not the tokens 0057 was read on")
    complete_coverage = len(used) == refs["yarn"]["n_used"]
    seed, reps_n = int(native.native["bootstrap_seed"]), int(native.native["bootstrap_reps"])
    by_cell = {}
    for name in pair_names:
        pooled_far = np.concatenate(far_tokens[name]) if far_tokens[name] else np.zeros(0)
        by_cell[name] = {
            "sender_head_truncate": L_by[name], "rope": cells[name].rope, "n_handoffs": len(used),
            "mean_delta_K_median_over_handoffs": float(np.median([per[h]["cells"][name]["mean_delta_K"] for h in used])),
            "frac_over_tau_K_median_over_handoffs": float(np.median([per[h]["cells"][name]["frac_over_tau_K"] for h in used])),
            "fstar_median_over_handoffs": {_tau_key(t): float(np.median([per[h]["cells"][name]["fstar"][_tau_key(t)] for h in used])) for t in taus},
            "far_from_seam_pooled": {"bin": bin_far, "n_tokens": int(len(pooled_far)),
                                     "median": float(np.median(pooled_far)) if len(pooled_far) else None,
                                     "mean": float(pooled_far.mean()) if len(pooled_far) else None},
        }
    yarn_far = by_cell[yarn_name]["far_from_seam_pooled"]["median"]
    if yarn_far is None:
        raise ValueError(f"{yarn_name} has no far-from-seam token on M_cap; nothing to read against")
    if complete_coverage and abs(yarn_far - refs["yarn"]["far_median"]) > _YARN_TOL:
        raise ValueError(f"{yarn_name}'s far-from-seam median recomputed on M_cap ({yarn_far}) is not the E-TRUNC record's "
                         f"({refs['yarn']['far_median']}); not the same tokens or not the same records")
    native_far = by_cell[NATIVE]["far_from_seam_pooled"]["median"]
    if native_far is None:
        raise ValueError("the native cell has no far-from-seam token on M_cap; the registered reading has nothing to read")
    diffs = [per[h]["paired_native_minus_yarn"]["mean_diff"] for h in used]
    paired = _stats(diffs) | {"bootstrap": bootstrap_median_interval(diffs, make_rng(seed), reps_n, quantile) | {"seed": seed, "reps": reps_n}}
    verdict = reading(native_far, refs["short_native"]["far_median"], yarn_far, margin)
    return {
        "cells": pins, "upstream_sha": next(iter(pins.values()))["upstream_sha"], "tau_K": tau_K,
        "yarn_level": yarn_name, "min_common_matched": floor, "margin_abs": margin, "references": refs,
        "n_scored_everywhere": len(common_scored), "unscored_by_cell": unscored,
        "void": sorted(void), "n_void": len(void), "n_used": len(used),
        "n_common_total": int(sum(per[h]["n_common"] for h in used)),
        "max_dumped_length": max(per[h]["dumped_length"] for h in common_scored),
        "by_cell": by_cell, "paired_native_minus_yarn_mean_delta_K": paired,
        "reading": {"far_from_seam_median_on_M_cap": native_far, "yarn_level": yarn_far,
                    "yarn_level_on_the_record": refs["yarn"]["far_median"], "complete_coverage": complete_coverage,
                    "short_native_level": refs["short_native"]["far_median"], "margin_abs": margin, "reads_as": verdict,
                    "note": "pre-registered (ruling A, 2026-10-13): the far-from-seam pooled MEDIAN delta_K of the NATIVE level on "
                            "M_cap, within the margin of the native-short level reads as THE SCALING (the YaRN receiver accounts "
                            "for the L32 excess), within the margin of the YaRN-L32 level reads as NOT THE SCALING (a native "
                            "receiver reproduces it), between reads as UNATTRIBUTED. M_cap sits at late sender positions; the "
                            "native-short median was pooled over the short cell's full matched sets. Descriptive; no cell moves."},
        "per_handoff": per,
    }


# --------------------------------------------------------------------------------------- rendering

def render_alignment(s: dict) -> str:
    lines = ["# L32-native cell: alignment check before any prefill (descriptive; decides nothing)", "",
             f"- {s['n_handoffs']} handoffs included at every cell; the native matched set equals {s['yarn_level']}'s on "
             f"{s['n_identical_to_yarn']} of {s['n_handoffs']} ({s['n_matched_total']:,} matched tokens).",
             f"- M_cap under the four E-TRUNC levels: {s['n_void']} void under |M_cap| >= {s['min_common_matched']}; "
             f"{s['n_used']} enter on {s['n_common_total']:,} common tokens.",
             f"- longest dumped length {s['max_dumped_length']:,} (dumped sender at most {s['max_dumped_sender']:,} + 1 for the prefix "
             f"control; |R| at most {s['max_n_receiver']:,}); the summarizer reads it against every dump's recorded window."]
    if s["void"]:
        lines.append("- void: " + "; ".join(f"`{h}`" for h in s["void"]))
    return "\n".join(lines) + "\n"


def render(out: dict) -> str:
    fmt = lambda x: "n/a" if x is None else f"{x:.4f}"      # noqa: E731
    rd, pm = out["reading"], out["paired_native_minus_yarn_mean_delta_K"]
    lines = ["# L32-native vs L32-YaRN paired comparison on M_cap (descriptive; decides nothing)", "",
             f"- {out['n_scored_everywhere']} handoffs scored at the native cell and every level; {out['n_void']} void under "
             f"|M_cap| >= {out['min_common_matched']}; {out['n_used']} compared on {out['n_common_total']:,} common tokens; "
             f"longest dumped length {out['max_dumped_length']:,}; upstream `{out['upstream_sha'][:12]}`."]
    for name, b in out["by_cell"].items():
        lines.append(f"- {name} (L={b['sender_head_truncate']}, rope {'native' if b['rope'] is None else b['rope']}): mean delta_K median over "
                     f"handoffs {fmt(b['mean_delta_K_median_over_handoffs'])}; tokens over tau_K {fmt(b['frac_over_tau_K_median_over_handoffs'])}; f*: " +
                     ", ".join(f"tau {k} {fmt(v)}" for k, v in b["fstar_median_over_handoffs"].items()) +
                     f"; far-from-seam ({b['far_from_seam_pooled']['bin']}) pooled median {fmt(b['far_from_seam_pooled']['median'])} / mean "
                     f"{fmt(b['far_from_seam_pooled']['mean'])} (n={b['far_from_seam_pooled']['n_tokens']:,}).")
    lines += [f"- paired (native - YaRN) mean delta_K over M_cap: median over handoffs {fmt(pm['median'])} "
              f"(bootstrap [{fmt(pm['bootstrap']['lower_2.5'])}, {fmt(pm['bootstrap']['upper_97.5'])}], seed {pm['bootstrap']['seed']}).",
              "", "## The registered reading (NATIVE, far-from-seam median on M_cap)", "",
              f"- {fmt(rd['far_from_seam_median_on_M_cap'])} against native-short {fmt(rd['short_native_level'])} and YaRN-{out['yarn_level']} "
              f"{fmt(rd['yarn_level'])} on the same tokens"
              + ("" if rd["complete_coverage"] else f" (PARTIAL coverage: the record's YaRN level over its full used set is {fmt(rd['yarn_level_on_the_record'])})")
              + f"; margin +/- {rd['margin_abs']} -> **reads as {rd['reads_as']}**.",
              f"- {rd['note']}"]
    if out["void"]:
        lines.append("- void: " + "; ".join(f"`{h}`" for h in out["void"]))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e9_native")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9t-l32n.toml"))
    ap.add_argument("--alignment-check", action="store_true",
                    help="pre-prefill: the native matched sets against the YaRN level's, M_cap, the void set and the longest "
                         "dumped length, from the alignment passes alone")
    a = ap.parse_args(argv)
    native = load_e9_config(Path(a.config), REPO_ROOT)
    try:
        cells, yarn_name = load_cells(native)
        out_dir = REPO_ROOT / native.native["out_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.alignment_check:
            s = alignment_check(cells, yarn_name)
            md = render_alignment(s)
            (out_dir / "alignment.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
            (out_dir / "alignment.md").write_text(md, encoding="utf-8", newline="\n")
            print(md)
            return 0
        from linear_ceiling.summarize_e9 import summarize       # the gate: each paired cell's own fail-closed reader first
        for name in (NATIVE, yarn_name):
            print(f"[{name}] summarize_e9 --config {cells[name].config_path.name}")
            summarize(cells[name], runner=subprocess.run)
        out = compare_native(cells, yarn_name)
    except (ValueError, RuntimeError) as e:
        print(f"L32-NATIVE SUMMARY REFUSED: {e}")
        return 1
    md = render(out)
    (out_dir / "compare.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (out_dir / "compare.md").write_text(md, encoding="utf-8", newline="\n")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
