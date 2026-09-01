"""Recompute every E8 figure and refuse on any disagreement (entries 0006/0009/0016).

Independence here means: re-run the upstream scorer on the SAME dumps and mapper, into a
scratch directory, and compare -- not re-read the driver's numbers. Before that, verify that
nothing the report depends on has moved: config bytes, the token file and its manifest, every
file of every dump, the upstream HEAD. Then recompute the drops and band outcomes from the
recomputed R² and compare those too. Refuses (ValueError) on any of it; never emits a partial.

Cost: one `score_mapper.py` call per (arm, k) -- on CPU roughly 45 s (k=1), 3 min (k=4),
10 min (k=8) each, so a full recomputation over three k's and two arms is ~25 minutes.
"""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E8Config, load_e8_config
from linear_ceiling.e8 import archived_r2, band_outcome, crosscheck, dump_fingerprint, score
from linear_ceiling.hashing import sha256_file_bytes

_TOL = 1e-6


def _close(a: float, b: float) -> bool:
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


def summarize(cfg: E8Config, runner=subprocess.run) -> str:
    rp = cfg.results_dir / "report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; E8 has not run")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    _walk_nan(rep, "report")
    if rep.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e8.toml changed since the run (config_sha256 mismatch)")
    if rep.get("upstream_sha") != cfg.upstream_sha:
        raise ValueError("report's upstream_sha differs from config; the pin moved")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True)
    if head.stdout.strip() != cfg.upstream_sha:
        raise ValueError(f"upstream HEAD {head.stdout.strip()[:12]} != pinned {cfg.upstream_sha[:12]}")
    tok = rep.get("tokens") or {}
    tp = (Path(REPO_ROOT) / tok.get("path", "")) if not Path(tok.get("path", "")).is_absolute() else Path(tok["path"])
    if not tp.exists() or sha256_file_bytes(tp) != tok.get("sha256"):
        raise ValueError("agent token file missing or changed since the run")
    if sha256_file_bytes(tp.with_suffix(".manifest.json")) != tok.get("manifest_sha256"):
        raise ValueError("token manifest changed since the run")
    dumps = {"generic": {w: cfg.upstream_path / cfg.generic_dumps / w for w in ("source", "target")},
             "agent": {w: cfg.agent_dumps / w for w in ("source", "target")}}
    for arm, d in dumps.items():
        for w, p in d.items():
            if dump_fingerprint(p) != (rep.get("dumps") or {}).get(arm, {}).get(w):
                raise ValueError(f"{arm}/{w} dump does not match the fingerprint recorded at run time")

    scratch = cfg.results_dir / "recheck"
    shutil.rmtree(scratch, ignore_errors=True)
    per_k = rep.get("per_k") or {}
    if set(per_k) != {str(k) for k in cfg.report_k}:
        raise ValueError(f"report per_k {sorted(per_k)} != config report_k {list(cfg.report_k)}")
    recomputed = {}
    for k in cfg.report_k:
        g = score(cfg, k, dumps["generic"]["source"], dumps["generic"]["target"], scratch / f"generic_k{k}.json", runner)
        chk = crosscheck(k, g, archived_r2(cfg, k))
        if chk != rep["archived_crosscheck"].get(str(k)):
            raise ValueError(f"k={k}: archived cross-check differs from the recorded one")
        a = score(cfg, k, dumps["agent"]["source"], dumps["agent"]["target"], scratch / f"agent_k{k}.json", runner)
        row = {"generic": {"K": g["K_r2_heldout_layer_mean"], "V": g["V_r2_heldout_layer_mean"]},
               "agent": {"K": a["K_r2_heldout_layer_mean"], "V": a["V_r2_heldout_layer_mean"]}}
        row["drop"] = {r: row["generic"][r] - row["agent"][r] for r in ("K", "V")}
        row["band_outcome"] = {r: band_outcome(row["drop"][r], cfg.band) for r in ("K", "V")}
        rec = per_k[str(k)]
        for sect in ("generic", "agent", "drop"):
            for r in ("K", "V"):
                if not _close(row[sect][r], rec[sect][r]):
                    raise ValueError(f"k={k} {sect}.{r}: recomputed {row[sect][r]} != recorded {rec[sect][r]}")
        if row["band_outcome"] != rec["band_outcome"]:
            raise ValueError(f"k={k}: band outcome recomputed {row['band_outcome']} != recorded {rec['band_outcome']}")
        recomputed[k] = row
    vb = rep.get("verdict_bearing") or {}
    if vb.get("k") != cfg.verdict_k or vb.get("outcome") != recomputed[cfg.verdict_k]["band_outcome"]:
        raise ValueError("verdict-bearing block does not match the recomputed verdict-k outcomes")

    lines = ["| k | arm (a) generic K / V | arm (b) agent K / V | drop K / V | band K / V |", "|---|---|---|---|---|"]
    for k in cfg.report_k:
        r = recomputed[k]
        tag = " (verdict-bearing, K)" if k == cfg.verdict_k else " (reported only)"
        lines.append(f"| {k}{tag} | {r['generic']['K']:.4f} / {r['generic']['V']:.4f} | "
                     f"{r['agent']['K']:.4f} / {r['agent']['V']:.4f} | {r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                     f"{r['band_outcome']['K']} / {r['band_outcome']['V']} |")
    md = ("E8 summary -- every R² recomputed by re-running the upstream scorer on the fingerprinted dumps\n\n"
          f"pair {cfg.pair} | upstream {cfg.upstream_sha[:12]} | config {rep['config_sha256'][:12]} | "
          f"arm (a) cross-checked against the archived r2.json for every k\n\n" + "\n".join(lines)
          + f"\n\nband (entry 0009): HOLDS if drop <= {cfg.band['holds_max_drop']}, DEGRADES if drop >= "
            f"{cfg.band['degrades_min_drop']}, else UNRESOLVED; verdict-bearing k={cfg.verdict_k} (entry 0016), "
            f"K and V separately, neither alone (entry 0009) -> "
            f"K **{recomputed[cfg.verdict_k]['band_outcome']['K']}** / "
            f"V **{recomputed[cfg.verdict_k]['band_outcome']['V']}**\n"
          + f"scope: {rep.get('scope')}\n\nThe verdict on H-E8 is NOT stated here; it enters by a numbered entry.\n")
    (cfg.results_dir / "summary.md").write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e8")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e8.toml"))
    a = ap.parse_args(argv)
    try:
        print(summarize(load_e8_config(Path(a.config), REPO_ROOT)))
    except (ValueError, RuntimeError) as e:
        print(f"E8 SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
