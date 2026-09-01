"""E7 replay driver and its gate.

`assert_ready` is the enforcement registered in ledger entry 0006 ("replay must not begin
until this entry is committed and unmodified"), mirroring linear_ceiling.e0's gate: it
refuses to read any trajectory until ledger/ledger.md and config/e7.toml are committed and
byte-identical to HEAD, and until the COMMITTED ledger contains entries 0006 and 0007 (the
registration and its amendments). The refusal happens before any trace file is opened.

The driver replays every corpus under traces_dir (tau-bench, tau2-bench, swe-bench -- see
e7_corpus), computes per-trajectory token/cost timelines (two bounds) and both lanes, checks
coverage against the registered floor with the entry-0011 exclusions, measures headroom at
every observed Lane A switch (entry 0010), validates the estimator against provider-reported
usage where a corpus carries it (entry 0012), and writes results/e7/skeleton_report.json.

It produces intermediate state, not claims: nothing here writes to the ledger, and every
number that could reach a ledger entry travels only through `summarize_e7`, which walks the
raw traces again and refuses on any disagreement.
"""
import argparse
import json
import subprocess
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, load_e7_config
from linear_ceiling.e7_corpus import LANE_A_ONLY_AGENTS, load_corpus
from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_headroom import rows as headroom_rows, rows_summary
from linear_ceiling.e7_lanes import lane_a, lane_b
from linear_ceiling.e7_swe import MODEL_KEYS
from linear_ceiling.e7_traces import coverage, meets_floor, suite_floor
from linear_ceiling.e7_usage import validation
from linear_ceiling.hashing import sha256_file_bytes

REQUIRED_ENTRIES = ("### 0006 ", "### 0007 ")
COST_BASIS = ("visible messages only -- every cost and token figure is a LOWER BOUND on what the "
              "provider billed (entry 0012: the system prompt and tool schemas are not in the trace)")


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


def build_report(cfg: E7Config) -> dict:
    """Everything the driver computes, as one JSON-able dict (shared with the summarizer's
    fixture builder; the gate is the caller's job)."""
    corpus = load_corpus(cfg)
    per_traj = []
    for t in corpus.trajectories:
        rows = timeline(t, cfg.pricing)
        a, b = lane_a(t), lane_b(t)
        per_traj.append({
            "traj_id": t.traj_id, "suite": t.suite, "agent": t.agent, "task": t.task,
            "totals": totals(rows),
            "lane_a": {"measurable": a.measurable,
                       "switches": list(a.switches) if a.switches is not None else None},
            "lane_b": {"switch_count": len(b.switches), "turns": len(b.tiers)},
        })
    cov = coverage(corpus.trajectories, exclude_agents=LANE_A_ONLY_AGENTS)
    lane_a_only: dict[str, dict] = {}
    for t in corpus.trajectories:
        if t.agent in LANE_A_ONLY_AGENTS:
            d = lane_a_only.setdefault(t.agent, {"suite": t.suite, "trajectories": 0})
            d["trajectories"] += 1
    hr = headroom_rows(corpus.trajectories, corpus.texts, cfg.pricing["read_mult"])
    return {
        "config_sha256": sha256_file_bytes(cfg.config_path),
        "trace_files": {corpus.relkey(cfg.traces_dir, f): sha256_file_bytes(f) for f in corpus.files},
        "cost_basis": COST_BASIS,
        "coverage": cov,
        "suite_floor": suite_floor(cov, cfg.thresholds),
        "coverage_meets_floor": meets_floor(cov, cfg.thresholds),
        "coverage_note": "below-floor output ships only as partial with coverage stated (entries "
                         "0005/0007); trajectory = one agent run on one task instance, distinct "
                         "tasks reported beside it (entry 0011)",
        "lane_a_only": lane_a_only,
        "unparsed": sorted(corpus.unparsed, key=lambda u: u["traj_id"]),
        "lane_a_detector_keys": list(MODEL_KEYS),
        "lane_a_measurable": sum(1 for p in per_traj if p["lane_a"]["measurable"]),
        "lane_a_unmeasurable": sum(1 for p in per_traj if not p["lane_a"]["measurable"]),
        "tokenizer": {"encoding": cfg.tokenizer.get("encoding"), "per_agent_strategy": corpus.strategies,
                      "divisors": cfg.tokenizer.get("divisors")},
        "headroom": {"read_mult": cfg.pricing["read_mult"], "rows": hr, "summary": rows_summary(hr)},
        "reported_usage": validation(corpus.trajectories),
        "trajectories": per_traj,
    }


def run(cfg: E7Config, *, repo_root: Path) -> Path:
    assert_ready(cfg, repo_root)
    try:
        report = build_report(cfg)
    except ValueError as e:
        raise RuntimeError(f"E7 REFUSED: {e}") from e
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
