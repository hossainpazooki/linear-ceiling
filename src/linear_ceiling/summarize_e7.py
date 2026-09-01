"""Recompute every E7 figure from the RAW TRACES and refuse on any disagreement.

The rule this exists to satisfy (CLAUDE.md, ledger entry 0006): no number reaches the ledger
except recomputed from `results/` by a summarizer that fails closed. Re-reading the driver's
own report would only restate its arithmetic, so this walks the raw trajectory files again,
rebuilds counters from config, and recomputes coverage, lane counts and cost aggregates
independently -- then compares against what the driver recorded.

Refuses (ValueError), never with a partial or a NaN, on: no report; config drift since the
run (`config_sha256` mismatch); a trace file missing or whose bytes no longer match the hash
recorded at run time; a per-trajectory total, lane result, or coverage figure that disagrees
with recomputation; a coverage-floor verdict the thresholds do not reproduce.

Costs are compared with a relative tolerance (`_TOL`) because they are float sums whose
addition order this module need not reproduce exactly; token counts, request counts, lane
results and coverage are integers or booleans and must match EXACTLY.
"""
import argparse
import json
import math
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, load_e7_config
from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_lanes import lane_a, lane_b
from linear_ceiling.e7_tokens import make_counter, strategy_for
from linear_ceiling.e7_traces import coverage, load_tau_bench
from linear_ceiling.hashing import sha256_file_bytes

_TOL = 1e-6   # relative, cost sums only


def _walk_nan(obj, path="$"):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        raise ValueError(f"NaN/inf at {path}; a run that produced a non-number must not be summarized")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_nan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_nan(v, f"{path}[{i}]")


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= _TOL * max(1.0, abs(a), abs(b))


def summarize(cfg: E7Config) -> str:
    rp = cfg.results_dir / "skeleton_report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; E7 has not run (nothing to summarize)")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    _walk_nan(rep, "report")
    if rep.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e7.toml changed since the run (config_sha256 mismatch); rerun or restore the config")

    recorded_files = rep.get("trace_files") or {}
    if not recorded_files:
        raise ValueError("report records no trace_files; provenance is unverifiable, refusing to summarize")
    trajs, strategies, counters = [], {}, {}
    for name, want in sorted(recorded_files.items()):
        f = cfg.traces_dir / "tau-bench" / name
        if not f.exists():
            raise ValueError(f"trace file recorded in the report is missing: {f}")
        if sha256_file_bytes(f) != want:
            raise ValueError(f"trace file {name} does not match the hash recorded at run time")
        agent = f.stem.rsplit("-", 1)[0]
        if agent not in counters:
            counters[agent] = make_counter(agent, cfg.tokenizer)
            strategies[agent] = strategy_for(agent, cfg.tokenizer)
        trajs.extend(load_tau_bench(f, agent=agent, counter=counters[agent]))

    by_id = {t["traj_id"]: t for t in rep["trajectories"]}
    if len(by_id) != len(rep["trajectories"]):
        raise ValueError("report contains duplicate traj_id entries")
    if len(trajs) != len(by_id):
        raise ValueError(f"recomputed {len(trajs)} trajectories, report has {len(by_id)}")

    agg = {}
    for t in trajs:
        row = by_id.get(t.traj_id)
        if row is None:
            raise ValueError(f"trajectory {t.traj_id} is absent from the report")
        tot = totals(timeline(t, cfg.pricing))
        rec = row["totals"]
        for k in ("requests", "input_tokens", "output_tokens"):
            if tot[k] != rec[k]:
                raise ValueError(f"{t.traj_id}: recomputed {k} {tot[k]} != recorded {rec[k]}")
        for k in ("cost_warm", "cost_cold"):
            if not _close(tot[k], rec[k]):
                raise ValueError(f"{t.traj_id}: recomputed {k} {tot[k]} != recorded {rec[k]}")
        a, b = lane_a(t), lane_b(t)
        if a.measurable != row["lane_a"]["measurable"]:
            raise ValueError(f"{t.traj_id}: recomputed lane A measurable={a.measurable} != recorded")
        rec_sw = row["lane_a"]["switches"]
        if (list(a.switches) if a.switches is not None else None) != rec_sw:
            raise ValueError(f"{t.traj_id}: recomputed lane A switches != recorded")
        if len(b.switches) != row["lane_b"]["switch_count"]:
            raise ValueError(f"{t.traj_id}: recomputed lane B switch_count != recorded")
        d = agg.setdefault(t.agent, {"n": 0, "requests": 0, "input": 0, "warm": 0.0, "cold": 0.0,
                                     "measurable": 0, "lane_b_switches": 0})
        d["n"] += 1
        d["requests"] += tot["requests"]
        d["input"] += tot["input_tokens"]
        d["warm"] += tot["cost_warm"]
        d["cold"] += tot["cost_cold"]
        d["measurable"] += 1 if a.measurable else 0
        d["lane_b_switches"] += len(b.switches)

    cov = coverage(trajs)
    if cov != rep["coverage"]:
        raise ValueError(f"recomputed coverage {cov} != recorded {rep['coverage']}")
    th = cfg.thresholds
    cov_ok = (len(cov) >= th["min_suites"]
              and all(v["trajectories"] >= th["min_trajectories_per_suite"]
                      and len(v["agents"]) >= th["min_agents_per_suite"] for v in cov.values()))
    if cov_ok != rep["coverage_meets_floor"]:
        raise ValueError(f"recomputed coverage_meets_floor {cov_ok} != recorded {rep['coverage_meets_floor']}")
    measurable = sum(d["measurable"] for d in agg.values())
    if measurable != rep["lane_a_measurable"]:
        raise ValueError(f"recomputed lane_a_measurable {measurable} != recorded {rep['lane_a_measurable']}")

    lines = ["| agent | strategy | trajs | requests | input tokens | warm/cold | Lane A measurable | Lane B switches |",
             "|---|---|---|---|---|---|---|---|"]
    for a in sorted(agg):
        d = agg[a]
        lines.append(f"| {a} | {strategies[a]} | {d['n']} | {d['requests']} | {d['input']} | "
                     f"{100*d['warm']/d['cold']:.2f}% | {d['measurable']} | {d['lane_b_switches']} |")
    tn = sum(d["n"] for d in agg.values())
    tw = sum(d["warm"] for d in agg.values())
    tc = sum(d["cold"] for d in agg.values())
    lines.append(f"| **ALL** | | {tn} | {sum(d['requests'] for d in agg.values())} | "
                 f"{sum(d['input'] for d in agg.values())} | {100*tw/tc:.2f}% | {measurable} | "
                 f"{sum(d['lane_b_switches'] for d in agg.values())} |")

    floor_note = (f"coverage floor NOT met (needs >= {th['min_trajectories_per_suite']} trajectories AND "
                  f">= {th['min_agents_per_suite']} agents per suite, >= {th['min_suites']} suites): "
                  "output ships only as partial with coverage stated"
                  if not cov_ok else "coverage floor met")
    md = ("E7 skeleton summary -- every figure recomputed from the raw traces, not restated\n\n"
          f"config sha256 {rep['config_sha256'][:12]} | trace files verified: {len(recorded_files)}\n\n"
          + "\n".join(lines)
          + f"\n\ncoverage: {json.dumps(cov)}\n{floor_note}\n"
          + f"\nLane A: {measurable} of {tn} trajectories measurable; "
            f"{tn - measurable} carry no per-step model metadata (recorded NOT MEASURABLE, never as zero).\n"
          + "\nNo hypothesis is decided by this summary: H-E7a needs Lane A over a floor-clearing "
            "corpus, H-E7b needs compaction events (not yet implemented).\n")
    (cfg.results_dir / "summary.md").write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e7")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e7.toml"))
    a = ap.parse_args(argv)
    try:
        print(summarize(load_e7_config(Path(a.config), REPO_ROOT)))
    except ValueError as e:
        print(f"E7 SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
