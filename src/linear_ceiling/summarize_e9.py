"""Recompute every E9 figure and refuse on any disagreement (entry 0019).

What can be recomputed on CPU is recomputed on CPU: the alignments of every handoff are
re-derived from the raw traces and compared record-for-record and array-for-array; every R² is
recomputed from the recorded per-layer, per-head SSE/SST moments; the keep-subset's moments are
recomputed from its fingerprinted tensors by re-running the upstream scorer; medians (the one
pinned quantile convention) and the band outcome are recomputed and compared against nothing --
they are STATED here for the first time, since the driver deliberately does not compute them.

What cannot be recomputed on CPU is named, not hidden: the deleted dumps. For those handoffs
the moments are a GPU-run record, cross-checked by the keep-subset, and the entry that states
the verdict must carry that sentence (0019).

Refuses (ValueError) on: a missing or incomplete report; config or pin drift; an alignment
that does not re-derive; a score file missing or off-hash; an R² the moments do not reproduce;
a kept dump off-fingerprint or a keep-subset re-score that disagrees.
"""
import argparse
import json
import math
import subprocess
from dataclasses import asdict
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e7_config, load_e9_config
from linear_ceiling.e7_stats import summary
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.e9 import UPSTREAM_PATHS, _stem, keep_subset, run_upstream, submission_dirs
from linear_ceiling.e9_align import align, load_handoffs
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.pairs import pair_models
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import snapshot

_TOL = 1e-6


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(a), abs(b))


def _walk_nan(obj, path="$"):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        raise ValueError(f"NaN/inf at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_nan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_nan(v, f"{path}[{i}]")


def _r2_from_moments(part: dict) -> dict:
    """Recompute per-layer head-mean R² and the layer mean from recorded SSE/SST."""
    out = {}
    for key in ("K", "V"):
        layers = []
        for i, layer in enumerate(part[key]):
            r2 = [1.0 - e / t for e, t in zip(layer["sse"], layer["sst"])]
            mean = float(np.mean(r2))
            if not _close(mean, layer["r2_head_mean"]):
                raise ValueError(f"{key} layer {i}: r2_head_mean {layer['r2_head_mean']} does not "
                                 f"follow from the recorded SSE/SST ({mean})")
            layers.append(mean)
        out[key] = float(np.mean(layers))
    return out


def band_outcome(median_k: float, band: dict) -> str:
    if median_k >= band["holds_min"]:
        return "HOLDS"
    if median_k <= band["degrades_max"]:
        return "DEGRADES"
    return "UNRESOLVED"


def summarize(cfg: E9Config, runner=subprocess.run, encoder=None, e7=None) -> str:
    rp = cfg.results_dir / "report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; E9 has not run")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    _walk_nan(rep, "report")
    if not rep.get("complete"):
        raise ValueError("report is a per-handoff checkpoint, not a complete run; finish or rerun E9")
    if rep.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e9.toml changed since the run (config_sha256 mismatch)")
    if rep.get("upstream_sha") != cfg.upstream_sha:
        raise ValueError("report's upstream_sha differs from config; the pin moved")
    try:
        check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 summary")
    except RuntimeError as e:
        raise ValueError(str(e)) from e

    # 1. Re-derive every alignment from the raw traces and compare, records and arrays.
    e7 = e7 or load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    enc = encoder or qwen_encoder(snapshot(pair_models(cfg.pair)[0]))
    counter = lambda t, ct="assistant": 0     # noqa: E731
    handoffs = {h.handoff_id: h for h in load_handoffs(submission_dirs(e7, cfg), counter)}
    recorded = {a["handoff_id"]: a for a in rep.get("alignments") or []}
    if set(handoffs) != set(recorded):
        raise ValueError(f"handoff set differs: recomputed {len(handoffs)}, recorded {len(recorded)}")
    included = []
    for hid, h in sorted(handoffs.items()):
        rec, s_ids, r_ids, pairs = align(h, enc, cfg.context_cap)
        if asdict(rec) != recorded[hid]:
            raise ValueError(f"{hid}: alignment record does not re-derive from the raw trace")
        if not rec.excluded:
            z = np.load(cfg.results_dir / "align" / f"{_stem(hid)}.npz")
            if not (np.array_equal(z["sender"], s_ids) and np.array_equal(z["receiver"], r_ids)
                    and np.array_equal(z["pairs"], pairs)):
                raise ValueError(f"{hid}: stored alignment arrays do not match the recomputation")
            included.append(hid)
    cov = {"observed": len(handoffs), "included": len(included), "excluded": len(handoffs) - len(included)}
    if cov != rep["coverage"]:
        raise ValueError(f"coverage recomputed {cov} != recorded {rep['coverage']}")
    if keep_subset(included, cfg.keep_seed, cfg.keep_n) != rep["keep_subset"]:
        raise ValueError("keep_subset does not re-derive from the seed and the included set")
    if set(rep.get("scores") or {}) != set(included):
        raise ValueError("scored handoff set differs from the included set")

    # 2. Every R² from moments; score files by hash; kept dumps by fingerprint + re-score.
    per_handoff = {}
    for hid in included:
        rec = rep["scores"][hid]
        sf = cfg.results_dir / "scores" / rec["score_file"]
        if not sf.exists() or sha256_file_bytes(sf) != rec["score_sha256"]:
            raise ValueError(f"{hid}: score file missing or does not match the hash recorded at run time")
        body = json.loads(sf.read_text(encoding="utf-8"))
        same, cross = _r2_from_moments(body["same"]), _r2_from_moments(body["cross"])
        for label, mine in (("same", same), ("cross", cross)):
            for key in ("K", "V"):
                stored = body[f"{label}_{key}_r2_layer_mean"]
                if not _close(mine[key], stored):
                    raise ValueError(f"{hid}: {label} {key} layer mean {stored} != moments ({mine[key]})")
                if not _close(rec[f"{label}_{key}_r2_layer_mean"], stored):
                    raise ValueError(f"{hid}: report copy of {label} {key} differs from the score file")
        per_handoff[hid] = {"same": same, "cross": cross, "n_pairs": body["n_pairs"]}
        if "kept_dumps" in rec:
            hdir = cfg.results_dir / rec["kept_dir"]
            for name, fp in rec["kept_dumps"].items():
                d = hdir / name
                actual = {p.relative_to(d).as_posix(): sha256_file_bytes(p)
                          for p in sorted(d.rglob("*")) if p.is_file()}
                if actual != fp:
                    raise ValueError(f"{hid}: kept dump {name} does not match its fingerprint")
            out = cfg.results_dir / "recheck" / f"{_stem(hid)}.json"
            mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{cfg.mapper_k}"
            try:
                run_upstream(cfg, ["scripts/score_positions.py",
                                   "--same-src", str((hdir / "same_src").resolve()),
                                   "--same-tgt", str((hdir / "same_tgt").resolve()),
                                   "--cross-src", str((hdir / "cross_src").resolve()),
                                   "--mapper", str(mapper),
                                   "--pairs", str((cfg.results_dir / "align" / f"{_stem(hid)}.npz").resolve()),
                                   "--out", str(out.resolve())], runner)
            except RuntimeError as e:
                raise ValueError(str(e)) from e
            re_body = json.loads(out.read_text(encoding="utf-8"))
            for label in ("same", "cross"):
                for key in ("K", "V"):
                    if not _close(re_body[f"{label}_{key}_r2_layer_mean"], body[f"{label}_{key}_r2_layer_mean"]):
                        raise ValueError(f"{hid}: keep-subset re-score disagrees on {label} {key}")

    # 3. Medians, fractions, band outcome -- stated here for the first time.
    same_k = summary([per_handoff[h]["same"]["K"] for h in included])
    same_v = summary([per_handoff[h]["same"]["V"] for h in included])
    cross_k = summary([per_handoff[h]["cross"]["K"] for h in included])
    cross_v = summary([per_handoff[h]["cross"]["V"] for h in included])
    matched = summary([recorded[h]["n_matched"] / recorded[h]["n_receiver"] for h in included])
    outcome = band_outcome(same_k["median"], cfg.band)

    def fmt(s, d=4):
        return f"{s['median']:.{d}f} (p10 {s['p10']:.{d}f}, p90 {s['p90']:.{d}f})"

    md = ("E9 summary -- alignments re-derived from raw traces; every R² recomputed from recorded "
          "moments; keep-subset re-scored from fingerprinted tensors\n\n"
          f"pair {cfg.pair} | upstream {cfg.upstream_sha[:12]} | config {rep['config_sha256'][:12]} | "
          f"coverage: {cov['included']} included / {cov['excluded']} excluded (cap {cfg.context_cap}) "
          f"of {cov['observed']} observed handoffs\n\n"
          f"- matched fraction |M|/|R| (a FLOOR; blocks method, entry 0019): {fmt(matched)}\n"
          f"- E9-same K R² per handoff: {fmt(same_k)}  <- the achievable ceiling under re-rendering\n"
          f"- E9-same V R² per handoff: {fmt(same_v)} (reported, verdict-bearing for nothing)\n"
          f"- E9-cross K R² per handoff: {fmt(cross_k)} (the k={cfg.mapper_k} mapper across the handoff)\n"
          f"- E9-cross V R² per handoff: {fmt(cross_v)}\n\n"
          f"band (entry 0019): HOLDS if median E9-same K >= {cfg.band['holds_min']}, DEGRADES if <= "
          f"{cfg.band['degrades_max']}, else UNRESOLVED -> **{outcome}**\n\n"
          f"keep-subset ({len(rep['keep_subset'])} handoffs) recomputed from tensors; the remaining "
          "handoffs' moments are a GPU-run record cross-checked by that subset (0019). Every figure "
          "is trace-visible-only (0012).\n\n"
          "The verdict on H-E9 is NOT stated here; it enters by a numbered entry.\n")
    (cfg.results_dir / "summary.md").write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e9")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9.toml"))
    a = ap.parse_args(argv)
    try:
        print(summarize(load_e9_config(Path(a.config), REPO_ROOT)))
    except (ValueError, RuntimeError) as e:
        print(f"E9 SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
