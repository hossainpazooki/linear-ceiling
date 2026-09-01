"""Recompute every E7 figure from the RAW TRACES and refuse on any disagreement.

The rule this exists to satisfy (CLAUDE.md, ledger entry 0006): no number reaches the ledger
except recomputed from `results/` by a summarizer that fails closed. Re-reading the driver's
own report would only restate its arithmetic, so this walks the raw trajectory files again
across all three corpora, rebuilds counters from config, and recomputes per-trajectory
totals, both lanes, coverage and its floor verdicts, the unparsed set, every headroom row
and its aggregate (entry 0010), and the reported-usage validation (entry 0012) -- then
compares ALL of it against what the driver recorded, key by key, so no recorded value can
escape comparison by being new.

Refuses (ValueError), never with a partial or a NaN, on: no report; config drift since the
run (`config_sha256` mismatch); a trace file missing, added, or whose bytes no longer match
the hash recorded at run time; any recorded figure the recomputation does not reproduce.

Floats are compared with a relative tolerance (`_TOL`) because they are sums whose addition
order this module need not reproduce; ints, bools and strings must match EXACTLY.
"""
import argparse
import json
import math
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, load_e7_config
from linear_ceiling.e7 import COST_BASIS
from linear_ceiling.e7_corpus import LANE_A_ONLY_AGENTS, discover_files, load_corpus
from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_headroom import rows as headroom_rows, rows_summary
from linear_ceiling.e7_lanes import lane_a, lane_b
from linear_ceiling.e7_swe import MODEL_KEYS
from linear_ceiling.e7_traces import coverage, meets_floor, suite_floor
from linear_ceiling.e7_usage import validation
from linear_ceiling.hashing import sha256_file_bytes

_TOL = 1e-6   # relative, floats only


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


def _compare(path: str, recomputed, recorded) -> None:
    """Deep equality with float tolerance; refuses naming the first divergent path."""
    if isinstance(recomputed, bool) or isinstance(recorded, bool):
        if recomputed is not recorded:
            raise ValueError(f"{path}: recomputed {recomputed!r} != recorded {recorded!r}")
    elif isinstance(recomputed, (int, float)) and isinstance(recorded, (int, float)):
        if isinstance(recomputed, float) or isinstance(recorded, float):
            if not _close(recomputed, recorded):
                raise ValueError(f"{path}: recomputed {recomputed} != recorded {recorded}")
        elif recomputed != recorded:
            raise ValueError(f"{path}: recomputed {recomputed} != recorded {recorded}")
    elif isinstance(recomputed, dict) and isinstance(recorded, dict):
        if set(recomputed) != set(recorded):
            raise ValueError(f"{path}: key set differs (recomputed {sorted(recomputed)} vs "
                             f"recorded {sorted(recorded)})")
        for k in recomputed:
            _compare(f"{path}.{k}", recomputed[k], recorded[k])
    elif isinstance(recomputed, (list, tuple)) and isinstance(recorded, (list, tuple)):
        if len(recomputed) != len(recorded):
            raise ValueError(f"{path}: length {len(recomputed)} != recorded {len(recorded)}")
        for i, (a, b) in enumerate(zip(recomputed, recorded)):
            _compare(f"{path}[{i}]", a, b)
    elif recomputed != recorded:
        raise ValueError(f"{path}: recomputed {recomputed!r} != recorded {recorded!r}")


def _verify_provenance(cfg: E7Config, rep: dict) -> None:
    recorded = rep.get("trace_files") or {}
    if not recorded:
        raise ValueError("report records no trace_files; provenance is unverifiable, refusing to summarize")
    root = cfg.traces_dir.resolve()
    current = {f.resolve().relative_to(root).as_posix(): f for f in discover_files(cfg.traces_dir)}
    missing = sorted(set(recorded) - set(current))
    added = sorted(set(current) - set(recorded))
    if missing:
        raise ValueError(f"trace file recorded in the report is missing: {missing[0]}")
    if added:
        raise ValueError(f"trace set changed since the run: {added[0]} was added; rerun the driver")
    for key, want in sorted(recorded.items()):
        if sha256_file_bytes(current[key]) != want:
            raise ValueError(f"trace file {key} does not match the hash recorded at run time")


def summarize(cfg: E7Config) -> str:
    rp = cfg.results_dir / "skeleton_report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; E7 has not run (nothing to summarize)")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    _walk_nan(rep, "report")
    if rep.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e7.toml changed since the run (config_sha256 mismatch); rerun or restore the config")
    _verify_provenance(cfg, rep)

    corpus = load_corpus(cfg)
    _compare("unparsed", sorted(corpus.unparsed, key=lambda u: u["traj_id"]), rep.get("unparsed"))

    by_id = {t["traj_id"]: t for t in rep["trajectories"]}
    if len(by_id) != len(rep["trajectories"]):
        raise ValueError("report contains duplicate traj_id entries")
    if len(corpus.trajectories) != len(by_id):
        raise ValueError(f"recomputed {len(corpus.trajectories)} trajectories, report has {len(by_id)}")

    agg: dict[tuple[str, str], dict] = {}
    for t in corpus.trajectories:
        row = by_id.get(t.traj_id)
        if row is None:
            raise ValueError(f"trajectory {t.traj_id} is absent from the report")
        tot = totals(timeline(t, cfg.pricing))
        a, b = lane_a(t), lane_b(t)
        mine = {"traj_id": t.traj_id, "suite": t.suite, "agent": t.agent, "task": t.task,
                "totals": tot,
                "lane_a": {"measurable": a.measurable,
                           "switches": list(a.switches) if a.switches is not None else None},
                "lane_b": {"switch_count": len(b.switches), "turns": len(b.tiers)}}
        if a.measurable != (row.get("lane_a") or {}).get("measurable"):
            # the most damaging edit gets its own words: unmeasurable relabelled as a measured zero
            raise ValueError(f"{t.traj_id}: recomputed lane A measurable={a.measurable} != recorded")
        _compare(t.traj_id, mine, row)
        d = agg.setdefault((t.suite, t.agent), {"n": 0, "requests": 0, "input": 0, "warm": 0.0,
                                                "cold": 0.0, "measurable": 0, "lane_a_switches": 0,
                                                "lane_b_switches": 0})
        d["n"] += 1
        d["requests"] += tot["requests"]
        d["input"] += tot["input_tokens"]
        d["warm"] += tot["cost_warm"]
        d["cold"] += tot["cost_cold"]
        d["measurable"] += 1 if a.measurable else 0
        d["lane_a_switches"] += len(a.switches) if a.switches else 0
        d["lane_b_switches"] += len(b.switches)

    cov = coverage(corpus.trajectories, exclude_agents=LANE_A_ONLY_AGENTS)
    _compare("coverage", cov, rep["coverage"])
    th = cfg.thresholds
    floors = suite_floor(cov, th)
    _compare("suite_floor", floors, rep["suite_floor"])
    cov_ok = meets_floor(cov, th)
    _compare("coverage_meets_floor", cov_ok, rep["coverage_meets_floor"])
    lane_a_only: dict[str, dict] = {}
    for t in corpus.trajectories:
        if t.agent in LANE_A_ONLY_AGENTS:
            e = lane_a_only.setdefault(t.agent, {"suite": t.suite, "trajectories": 0})
            e["trajectories"] += 1
    _compare("lane_a_only", lane_a_only, rep["lane_a_only"])
    _compare("lane_a_detector_keys", list(MODEL_KEYS), rep["lane_a_detector_keys"])
    measurable = sum(d["measurable"] for d in agg.values())
    _compare("lane_a_measurable", measurable, rep["lane_a_measurable"])
    _compare("lane_a_unmeasurable", len(corpus.trajectories) - measurable, rep["lane_a_unmeasurable"])

    _compare("tokenizer", {"encoding": cfg.tokenizer.get("encoding"), "per_agent_strategy": corpus.strategies,
                           "divisors": cfg.tokenizer.get("divisors")}, rep["tokenizer"])
    _compare("cost_basis", COST_BASIS, rep["cost_basis"])

    hr = headroom_rows(corpus.trajectories, corpus.texts, cfg.pricing["read_mult"])
    _compare("headroom", {"read_mult": cfg.pricing["read_mult"], "rows": hr, "summary": rows_summary(hr)},
             rep["headroom"])
    usage = validation(corpus.trajectories)
    _compare("reported_usage", usage, rep["reported_usage"])

    return _render(cfg, rep, corpus, agg, cov, floors, cov_ok, lane_a_only, measurable, hr, usage)


def _fmt_summary(s: dict, pct: bool = False, digits: int = 3) -> str:
    if pct:
        return f"{100*s['median']:.1f}% (p10 {100*s['p10']:.1f}%, p90 {100*s['p90']:.1f}%)"
    return f"{s['median']:,.{digits}f} (p10 {s['p10']:,.{digits}f}, p90 {s['p90']:,.{digits}f})"


def _render(cfg, rep, corpus, agg, cov, floors, cov_ok, lane_a_only, measurable, hr, usage) -> str:
    th = cfg.thresholds
    lines = ["| suite | agent | strategy | trajs | requests | input tokens (LOWER BOUND) | warm/cold | "
             "Lane A measurable | Lane A switches | Lane B switches |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for (suite, agent) in sorted(agg):
        d = agg[(suite, agent)]
        tag = " (Lane A only, not a coverage contributor)" if agent in LANE_A_ONLY_AGENTS else ""
        lines.append(f"| {suite} | {agent}{tag} | {corpus.strategies[agent]} | {d['n']} | {d['requests']} | "
                     f"{d['input']} | {100*d['warm']/d['cold']:.2f}% | {d['measurable']} | "
                     f"{d['lane_a_switches']} | {d['lane_b_switches']} |")
    tn = sum(d["n"] for d in agg.values())
    tw = sum(d["warm"] for d in agg.values())
    tc = sum(d["cold"] for d in agg.values())
    lines.append(f"| **ALL** | | | {tn} | {sum(d['requests'] for d in agg.values())} | "
                 f"{sum(d['input'] for d in agg.values())} | {100*tw/tc:.2f}% | {measurable} | "
                 f"{sum(d['lane_a_switches'] for d in agg.values())} | "
                 f"{sum(d['lane_b_switches'] for d in agg.values())} |")

    cov_lines = ["| suite | trajectories | distinct tasks | distinct agents | per-suite floor |",
                 "|---|---|---|---|---|"]
    for s in sorted(cov):
        v = cov[s]
        cov_lines.append(f"| {s} | {v['trajectories']} | {v['tasks']} | {len(v['agents'])} "
                         f"({', '.join(v['agents'])}) | {'met' if floors[s] else 'NOT met'} |")
    floor_note = (f"coverage floor {'MET' if cov_ok else 'NOT met'}: >= {th['min_trajectories_per_suite']} "
                  f"trajectories AND >= {th['min_agents_per_suite']} agents per suite, on >= "
                  f"{th['min_suites']} suites (entry 0007; unit and exclusions per entry 0011)")
    if not cov_ok:
        floor_note += " -- output ships only as partial with coverage stated"
    excl = "; ".join(f"{a}: {v['trajectories']} {v['suite']} trajectories" for a, v in sorted(lane_a_only.items()))
    unparsed = rep["unparsed"]

    hs = rows_summary(hr)
    if hs is None:
        head = ("Headroom (entry 0010): no observed Lane A switch had message text available -- "
                "nothing to measure (not a zero).")
    else:
        head = ("Headroom at observed cross-model handoffs (entry 0010 measure; UPPER BOUND, never an "
                "achievable saving, because the handoff is re-rendered and token positions change):\n\n"
                f"- switches measured: {hs['switches']} across {', '.join(hs['submissions'])}\n"
                f"- byte-identical handoffs: {hs['byte_identical']}/{hs['switches']}\n"
                f"- overlap fraction of the receiving prompt: {_fmt_summary(hs['overlap_fraction'])}\n"
                f"- paid prefill at the switch, visible-only LOWER BOUND: "
                f"{_fmt_summary(hs['paid_tokens'], digits=0)} tokens\n"
                f"- headroom upper bound as a fraction of paid: {_fmt_summary(hs['recoverable_fraction'], pct=True)}\n"
                f"- method: {hs['method']}; read_mult {cfg.pricing['read_mult']}")
    if usage is None:
        use = "Reported usage (entry 0012): no corpus in this run carries provider-reported prompt tokens."
    else:
        ul = ["Estimator validation against provider-reported usage (entry 0012), per requesting role, "
              "never pooled:\n",
              "| requesting role | n | offset median (reported - estimated) | p10 | p90 | ratio median |",
              "|---|---|---|---|---|---|"]
        for role, v in sorted(usage["per_role"].items()):
            o, r = v["offset"], v["ratio"]
            ul.append(f"| {role} | {o['n']} | {o['median']:,.0f} | {o['p10']:,.0f} | {o['p90']:,.0f} | "
                      f"{r['median']:.2f} |")
        ul.append("")
        ul.append("assistant offset by turn position: " + "; ".join(
            f"turn {b['turns']}: {b['median']:,.0f} (n={b['n']})" for b in usage["assistant_by_turn"]))
        use = "\n".join(ul)

    md = ("E7 summary -- every figure recomputed from the raw traces, not restated\n\n"
          f"config sha256 {rep['config_sha256'][:12]} | trace files verified: {len(rep['trace_files'])} | "
          f"cost basis: {rep['cost_basis']}\n\n"
          + "\n".join(lines)
          + "\n\n" + "\n".join(cov_lines) + f"\n\n{floor_note}\n"
          + (f"Lane A only, excluded from floor arithmetic (entry 0011): {excl}\n" if excl else "")
          + f"unparsed trajectories (recorded, never counted): {len(unparsed)}"
          + (" -- " + "; ".join(f"{u['traj_id']}: {u['reason']}" for u in unparsed[:5]) if unparsed else "")
          + "\n"
          + f"\nLane A (detector keys {list(MODEL_KEYS)}): {measurable} of {tn} trajectories measurable; "
            f"{tn - measurable} carry no per-step model metadata (recorded NOT MEASURABLE, never as zero).\n"
          + f"\n{head}\n\n{use}\n"
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
