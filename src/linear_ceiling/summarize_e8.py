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
from linear_ceiling.e7_stats import quantile
from linear_ceiling.e8 import (UPSTREAM_PATHS, agent_holdout_frac, archived_r2, band_outcome, crosscheck,
                               dump_fingerprint, score)
from linear_ceiling.rng import make_rng
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.hashing import sha256_file_bytes

import numpy as np

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
    try:
        # ancestor + E8's invoked paths unchanged since the pin (a later re-pin is not drift)
        check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E8 summary")
    except RuntimeError as e:
        raise ValueError(str(e)) from e
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
    recomputed, amend = {}, {}
    for k in cfg.report_k:
        gpt = scratch / f"generic_k{k}.npz" if cfg.amendment else None
        apt = scratch / f"agent_k{k}.npz" if cfg.amendment else None
        g = score(cfg, k, dumps["generic"]["source"], dumps["generic"]["target"], scratch / f"generic_k{k}.json", runner,
                  per_token=gpt)
        chk = crosscheck(k, g, archived_r2(cfg, k))
        if chk != rep["archived_crosscheck"].get(str(k)):
            raise ValueError(f"k={k}: archived cross-check differs from the recorded one")
        a = score(cfg, k, dumps["agent"]["source"], dumps["agent"]["target"], scratch / f"agent_k{k}.json", runner,
                  holdout_frac=agent_holdout_frac(cfg), per_token=apt)
        if cfg.amendment:
            amend[k] = _amendment_figures(cfg, k, rep, g, a, gpt, apt)
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
    if cfg.amendment:
        (cfg.results_dir / "summary.json").write_text(json.dumps({"per_k": {str(k): v for k, v in amend.items()},
                                                                  "recomputed": {str(k): v for k, v in recomputed.items()},
                                                                  "amendment": rep.get("amendment"),
                                                                  "reused_agent_dumps_from": rep.get("reused_agent_dumps_from")},
                                                                 indent=1), encoding="utf-8")
        lines.append("")
        lines.append(_amendment_md(cfg, rep, amend))
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


def _seq_r2(z, key: str) -> np.ndarray:
    """Per-sequence R^2 from the record's per-sequence moments: 1 - sse_s/sst_s per head, head- and
    layer-mean -> [S]. SST is around the GLOBAL held-out mean (upstream per_sequence_moments), so the
    pooled per-head R^2 is 1 - sum_s sse / sum_s sst."""
    sse, sst = np.asarray(z[f"sse_seq_{key}"], dtype=np.float64), np.asarray(z[f"sst_seq_{key}"], dtype=np.float64)
    return (1.0 - sse / sst).mean((1, 2))


def _pooled_from_seqs(z, key: str, idx) -> float:
    sse, sst = np.asarray(z[f"sse_seq_{key}"], dtype=np.float64)[idx], np.asarray(z[f"sst_seq_{key}"], dtype=np.float64)[idx]
    return float((1.0 - sse.sum(0) / sst.sum(0)).mean())


def _stats(v) -> dict:
    v = [float(x) for x in v]
    return {"n": len(v), "median": quantile(v, 0.5), "p10": quantile(v, 0.1), "p90": quantile(v, 0.9)}


def _amendment_figures(cfg: E8Config, k: int, rep: dict, g: dict, a: dict, gpt: Path, apt: Path) -> dict:
    """Entry 0030 (E8 amendment): recompute the per-sequence R^2 of both arms from the re-scored per-token
    records, compare with the run's record, and bootstrap arm (b)'s pooled R^2 and the drop over agent
    sequences (seeded, config). Refuses on any disagreement with the recorded report."""
    rec = rep["per_k"][str(k)]
    if rec.get("holdout_frac") != {"generic": cfg.holdout_frac, "agent": agent_holdout_frac(cfg)}:
        raise ValueError(f"k={k}: recorded hold-out fractions {rec.get('holdout_frac')} differ from config")
    out = {"holdout_frac": rec["holdout_frac"], "n_heldout_tokens": rec.get("n_heldout_tokens"),
           "n_heldout_seqs": rec.get("n_heldout_seqs"), "per_sequence": {}}
    zs = {}
    for arm, sc, pt in (("generic", g, gpt), ("agent", a, apt)):
        z = np.load(pt)
        zs[arm] = z
        if sc.get("n_heldout_seqs") != rec["n_heldout_seqs"][arm] or sc.get("n_heldout_tokens") != rec["n_heldout_tokens"][arm]:
            raise ValueError(f"k={k} {arm}: re-scored token/sequence counts differ from the record")
        if [int(i) for i in z["seq_ids"]] != list(rec["per_sequence"][arm]["seq_ids"]):
            raise ValueError(f"k={k} {arm}: per-sequence ids differ from the record")
        for key in ("K", "V"):
            mine = _seq_r2(z, key)
            if not np.allclose(mine, rec["per_sequence"][arm][key], rtol=0, atol=_TOL):
                raise ValueError(f"k={k} {arm}: per-sequence {key} R^2 recomputed from the record differs from the recorded list")
            if not np.allclose(mine, sc["per_sequence"][f"{key}_r2_layer_mean"], rtol=0, atol=_TOL):
                raise ValueError(f"k={k} {arm}: per-sequence {key} R^2 in the re-scored json differs from its own record")
            pooled = _pooled_from_seqs(z, key, slice(None))
            if not _close(pooled, sc[f"{key}_r2_heldout_layer_mean"]):
                raise ValueError(f"k={k} {arm}: per-sequence moments do not reproduce the pooled {key} R^2")
            out["per_sequence"][f"{arm}_{key}"] = _stats(mine)
    rng = make_rng(int(cfg.amendment["bootstrap_seed"]) + k)
    reps = int(cfg.amendment["bootstrap_reps"])
    S = len(zs["agent"]["seq_ids"])
    idx = rng.integers(0, S, size=(reps, S))
    boot = {}
    for key in ("K", "V"):
        agent_b = np.asarray([_pooled_from_seqs(zs["agent"], key, idx[r]) for r in range(reps)])
        drop_b = float(g[f"{key}_r2_heldout_layer_mean"]) - agent_b
        boot[key] = {"agent_lower_2.5": quantile(agent_b.tolist(), 0.025), "agent_upper_97.5": quantile(agent_b.tolist(), 0.975),
                     "drop_lower_2.5": quantile(drop_b.tolist(), 0.025), "drop_upper_97.5": quantile(drop_b.tolist(), 0.975),
                     "reps": reps, "seed": int(cfg.amendment["bootstrap_seed"]) + k, "n_seqs": S}
    out["bootstrap"] = boot
    prior_ref = rep.get("reused_agent_dumps_from") or {}
    prior_path = Path(REPO_ROOT) / prior_ref.get("report", "")
    if prior_ref and prior_path.exists():
        if sha256_file_bytes(prior_path) != prior_ref.get("sha256"):
            raise ValueError("the prior E8 report this amendment reuses dumps from has changed since the run")
        prior = json.loads(prior_path.read_text(encoding="utf-8"))["per_k"].get(str(k))
        if prior:
            out["prior_0016_protocol"] = {"agent": prior["agent"], "drop": prior["drop"], "band_outcome": prior["band_outcome"],
                                          "holdout_frac_agent": cfg.holdout_frac}
            prior_r2 = prior_path.parent / "r2" / f"agent_k{k}.json"     # the prior run's own scorer record, if kept
            if prior_r2.exists():
                pj = json.loads(prior_r2.read_text(encoding="utf-8"))
                out["prior_0016_protocol"]["n_heldout_tokens"] = pj.get("n_heldout_tokens")
                out["prior_0016_protocol"]["n_heldout_seqs"] = int(np.ceil(float(pj.get("holdout_frac", cfg.holdout_frac)) * int(pj.get("n_seqs", 0))))
            out["change_from_prior"] = {key: float(a[f"{key}_r2_heldout_layer_mean"]) - float(prior["agent"][key]) for key in ("K", "V")}
    return out


def _amendment_md(cfg: E8Config, rep: dict, amend: dict) -> str:
    ent = (rep.get("amendment") or {}).get("entry", "?")
    rows = [f"E8 amendment (entry {ent}): arm (b) over every agent sequence (hold-out fraction "
            f"{agent_holdout_frac(cfg)}), arm (a) at its own held-out fraction {cfg.holdout_frac}; per-sequence R² from "
            f"the per-token record; seeded bootstrap over agent sequences. DESCRIPTIVE: the H-E8 cell was decided by 0020.",
            "", "| k | agent seqs / tokens | agent K / V (all) | prior 0016-protocol agent K / V | change K / V | "
            "drop K / V (all) | drop 95% K | drop 95% V | per-seq agent K median (p10, p90) |", "|---|---|---|---|---|---|---|---|---|"]
    for k in cfg.report_k:
        m, r = amend[k], rep["per_k"][str(k)]
        pr = m.get("prior_0016_protocol", {}).get("agent", {})
        ch = m.get("change_from_prior", {})
        b, ps = m["bootstrap"], m["per_sequence"]
        rows.append(f"| {k} | {m['n_heldout_seqs']['agent']} / {m['n_heldout_tokens']['agent']} | "
                    f"{r['agent']['K']:.4f} / {r['agent']['V']:.4f} | "
                    + (f"{pr['K']:.4f} / {pr['V']:.4f} | {ch['K']:+.4f} / {ch['V']:+.4f} | " if pr else "— | — | ")
                    + f"{r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                    f"[{b['K']['drop_lower_2.5']:+.4f}, {b['K']['drop_upper_97.5']:+.4f}] | "
                    f"[{b['V']['drop_lower_2.5']:+.4f}, {b['V']['drop_upper_97.5']:+.4f}] | "
                    f"{ps['agent_K']['median']:.4f} ({ps['agent_K']['p10']:.4f}, {ps['agent_K']['p90']:.4f}) |")
    return "\n".join(rows)


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
