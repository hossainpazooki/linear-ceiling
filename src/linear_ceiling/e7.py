"""E7 replay driver and its gate.

`assert_ready` is the enforcement registered in ledger entry 0006 ("replay must not begin
until this entry is committed and unmodified"), mirroring linear_ceiling.e0's gate: it
refuses to read any trajectory until ledger/ledger.md and config/e7.toml are committed and
byte-identical to HEAD, and until the COMMITTED ledger contains entries 0006 and 0007 (the
registration and its amendments). The refusal happens before any trace file is opened.

The driver is the day-2-gate skeleton: it loads every tau-bench file found under traces_dir,
computes per-trajectory token/cost timelines (two bounds) and both lanes, checks coverage
against the registered floor, and writes results/e7/skeleton_report.json. It produces
intermediate state, not claims: nothing here writes to the ledger, and any number that would
decide a hypothesis still travels only through a fail-closed summarizer (to be built before
the numbers-freeze gate).
"""
import argparse
import json
import subprocess
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, load_e7_config
from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_lanes import lane_a, lane_b
from linear_ceiling.e7_tokens import make_counter, strategy_for
from linear_ceiling.e7_traces import coverage, load_tau_bench

REQUIRED_ENTRIES = ("### 0006 ", "### 0007 ")


def assert_ready(cfg: E7Config, repo_root: Path) -> None:
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(
                f"E7 REFUSED: {rel} is not committed as-is; entries 0006/0007 and config/e7.toml "
                "must be committed before any trajectory is read"
            )
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=repo_root,
                               capture_output=True, text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("E7 REFUSED: cannot read HEAD:ledger/ledger.md")
    for marker in REQUIRED_ENTRIES:
        if marker not in committed.stdout:
            raise RuntimeError(
                f"E7 REFUSED: committed ledger has no entry {marker.strip('# ').strip()}; the E7 "
                "registration and its amendments must be in history before replay"
            )


def run(cfg: E7Config, *, repo_root: Path) -> Path:
    assert_ready(cfg, repo_root)
    files = sorted(cfg.traces_dir.glob("tau-bench/*.json"))
    if not files:
        raise RuntimeError(f"E7 REFUSED: no trajectory files under {cfg.traces_dir / 'tau-bench'}; "
                           "acquire traces first (they are gitignored, never committed)")
    trajs, strategies = [], {}
    counters: dict = {}
    for f in files:
        agent = f.stem.rsplit("-", 1)[0]  # gpt-4o-airline -> gpt-4o (agent identity, domain stripped)
        if agent not in counters:
            counters[agent] = make_counter(agent, cfg.tokenizer)
            strategies[agent] = strategy_for(agent, cfg.tokenizer)
        trajs.extend(load_tau_bench(f, agent=agent, counter=counters[agent]))
    per_traj = []
    for t in trajs:
        rows = timeline(t, cfg.pricing)
        a, b = lane_a(t), lane_b(t)
        per_traj.append({
            "traj_id": t.traj_id, "suite": t.suite, "agent": t.agent,
            "totals": totals(rows),
            "lane_a": {"measurable": a.measurable,
                       "switches": list(a.switches) if a.switches is not None else None},
            "lane_b": {"switch_count": len(b.switches), "turns": len(b.tiers)},
        })
    cov = coverage(trajs)
    floor = cfg.thresholds
    cov_ok = (
        len(cov) >= floor["min_suites"]
        and all(v["trajectories"] >= floor["min_trajectories_per_suite"]
                and len(v["agents"]) >= floor["min_agents_per_suite"] for v in cov.values())
    )
    report = {
        "coverage": cov,
        "coverage_meets_floor": cov_ok,
        "coverage_note": "below-floor output ships only as partial with coverage stated (entries 0005/0007)",
        "lane_a_measurable": sum(1 for p in per_traj if p["lane_a"]["measurable"]),
        "lane_a_unmeasurable": sum(1 for p in per_traj if not p["lane_a"]["measurable"]),
        "tokenizer": {"encoding": cfg.tokenizer.get("encoding"), "per_agent_strategy": strategies,
                      "divisors": cfg.tokenizer.get("divisors")},
        "trajectories": per_traj,
    }
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.results_dir / "skeleton_report.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e7")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--check", action="store_true", help="run the gate only, read no trace")
    a = ap.parse_args(argv)
    cfg = load_e7_config(Path(a.config), REPO_ROOT)
    try:
        if a.check:
            assert_ready(cfg, REPO_ROOT)
            print("E7 gate: ready (registration committed; no trace was read)")
            return 0
        out = run(cfg, repo_root=REPO_ROOT)
        print(f"skeleton report: {out}")
        return 0
    except RuntimeError as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
