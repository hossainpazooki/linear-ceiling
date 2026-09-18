"""Emit a pair's tau lines, at full float precision, from its own E8 report.

WHY THIS EXISTS. `summarize_e9 --calibrate-tau` is the authority on tau, but it LOADS the config
first, and a second-family config refuses to load until tau is filled in. That circularity is the
bootstrap trap the 2026-09-18 review found documented three contradictory ways. This tool is the
one-way door out of it, and deliberately the smallest possible one:

  E8 runs -> summarize_e8 -> `emit_tau.py` (here) -> the lines are TYPED into the config ->
  `summarize_e9 --calibrate-tau` CROSS-CHECKS them against a re-scored mapper and refuses on
  disagreement -> `e9 --align-only` -> the registration entry.

So this tool never decides anything and is never the authority: it reads one recorded number per
tau out of the E8 report and subtracts it from 1. The authority is still the summarizer, which
recomputes all of it from the tensors and refuses at 1e-9 if a digit was mistyped -- which is
exactly why the value must leave here at FULL precision. `summarize_e8` prints 4 decimals; typing
0.3186 where the summarizer recomputes 0.3186442653116294 refuses, and has.

  tau_K       = 1 - (arm (a), generic text) held-out K R^2 at the verdict k   [entry 0016 / 0023]
  tau_V       = 1 - (arm (a), generic text) held-out V R^2                    [alongside f* only]
  tau_agent_K = 1 - (arm (b), agent text)   held-out K R^2                    [entry 0025, alongside]

WHAT IT REFUSES TO DO. `tau_ladder` and `prefix_invariance_max_delta` are registered as FUNCTIONS of
tau_K by the registering entry, and that entry is not written. This tool will evaluate a function it
is GIVEN (`--ladder`, `--prefix-delta`) and will not invent one: without them it prints the two keys
as still-unresolved and says so in its exit line. Choosing them is a registration decision, not a
tooling one.

Usage:
  .venv/bin/python tools/emit_tau.py results/e8f/report.json --pair llama3.2-3b-to-llama3.1-8b
  ... [--k 1] [--ladder 0.10 0.03] [--prefix-delta 1e-4] [--json out.json]
"""
import argparse
import json
import sys
from pathlib import Path


def _r2(report: dict, k: str, arm: str, key: str) -> float:
    try:
        return float(report["per_k"][k][arm][key])
    except (KeyError, TypeError, ValueError) as e:
        raise SystemExit(f"emit_tau REFUSED: report has no per_k[{k!r}][{arm!r}][{key!r}] ({e}); "
                         "that is not an E8 report this tool recognises") from e


def taus(report: dict, k: int) -> dict:
    """The three tau values, as floats, straight from the report's recorded held-out R^2."""
    ks = str(k)
    out = {"tau_K": 1.0 - _r2(report, ks, "generic", "K"),
           "tau_V": 1.0 - _r2(report, ks, "generic", "V"),
           "tau_agent_K": 1.0 - _r2(report, ks, "agent", "K")}
    for name, v in out.items():
        # config.py refuses anything outside (0, 1); catching it here names the arm instead.
        if not (0.0 < v < 1.0):
            raise SystemExit(f"emit_tau REFUSED: {name} = {v!r} is not in (0, 1). An R^2 outside [0, 1) "
                             "means the mapper did not fit; tau is not defined and no config may be written.")
    # Entry 0025's reading: tau_K anchors to GENERIC text, tau_agent_K to the agent text E9 actually
    # reads, and the mapper is expected to do WORSE on the shifted distribution. config.py enforces
    # tau_K < tau_agent_K; saying so here points at the measurement rather than at the loader.
    if not out["tau_K"] < out["tau_agent_K"]:
        raise SystemExit(f"emit_tau REFUSED: tau_K {out['tau_K']!r} is not below tau_agent_K "
                         f"{out['tau_agent_K']!r}: this pair's mapper scored no worse on agent text than on "
                         "generic text, which entry 0025's reading does not contemplate. config.py would "
                         "refuse the written config too. This is a finding for the registering entry, not "
                         "a value to paste.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit full-precision tau lines from an E8 report (see module docstring)")
    ap.add_argument("report", help="results/<exp>/report.json written by linear_ceiling.e8")
    ap.add_argument("--pair", required=True, help="the pair the report must name; refuses on any other")
    ap.add_argument("--k", type=int, default=1, help="the verdict k (default 1, every registered config's)")
    ap.add_argument("--ladder", type=float, nargs="*", default=None,
                    help="tau_ladder rungs, as the REGISTERING ENTRY fixes them; omit to leave unresolved")
    ap.add_argument("--prefix-delta", type=float, default=None,
                    help="prefix_invariance_max_delta, as the REGISTERING ENTRY fixes it; omit to leave unresolved")
    ap.add_argument("--json", help="also write the record here")
    a = ap.parse_args()

    path = Path(a.report)
    if not path.exists():
        raise SystemExit(f"emit_tau REFUSED: {path} does not exist. Sitting A writes it; nothing here "
                         "can stand in for it.")
    rep = json.loads(path.read_text(encoding="utf-8"))
    if rep.get("pair") != a.pair:
        raise SystemExit(f"emit_tau REFUSED: report is for pair {rep.get('pair')!r}, not {a.pair!r}. "
                         "tau is 1 - THIS pair's own held-out R^2 and is never inherited.")
    t = taus(rep, a.k)

    print(f"# tau for {a.pair} at k = {a.k}, from {path} (verdict_k in the report: {rep.get('verdict_k')!r})")
    print("# Full precision on purpose: summarize_e9 --calibrate-tau recomputes and refuses at 1e-9.")
    print("# Paste into [e9.rule] of the pair's e9 config(s), replacing the UNRESOLVED markers.\n")
    for name in ("tau_K", "tau_V"):
        print(f"{name} = {t[name]!r}")
    if a.ladder is not None:
        rungs = sorted((float(x) for x in a.ladder), reverse=True)
        bad = [r for r in rungs if not (0.0 < r < t["tau_K"])]
        if bad:
            raise SystemExit(f"emit_tau REFUSED: ladder rungs {bad} are not inside (0, tau_K = {t['tau_K']!r}); "
                             "config.py refuses the same thing.")
        print(f"tau_ladder = [{', '.join(repr(r) for r in rungs)}]")
    print(f"tau_agent_K = {t['tau_agent_K']!r}")
    if a.prefix_delta is not None:
        if not (0.0 < a.prefix_delta < t["tau_K"]):
            raise SystemExit(f"emit_tau REFUSED: prefix delta {a.prefix_delta!r} is not inside (0, tau_K).")
        print(f"\n# [e9.controls]\nprefix_invariance_max_delta = {float(a.prefix_delta)!r}")

    missing = [n for n, v in (("tau_ladder", a.ladder), ("prefix_invariance_max_delta", a.prefix_delta)) if v is None]
    if a.json:
        rec = dict(t, pair=a.pair, k=a.k, report=str(path), report_sha_named=rep.get("upstream_sha"),
                   tau_ladder=(sorted((float(x) for x in a.ladder), reverse=True) if a.ladder is not None else None),
                   prefix_invariance_max_delta=(float(a.prefix_delta) if a.prefix_delta is not None else None),
                   unresolved=missing)
        Path(a.json).write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nrecord -> {a.json}")
    if missing:
        print(f"\nSTILL UNRESOLVED: {', '.join(missing)} — each is a registered FUNCTION of tau_K and this "
              f"tool will not choose one. Pass --ladder / --prefix-delta with the values the registering "
              f"entry fixes, or leave the markers in place. The config refuses either way.", file=sys.stderr)
        return 3
    print("\nAll five tau-derived keys emitted. The summarizer is still the authority: run "
          "`summarize_e9 --calibrate-tau` after typing them in, and believe it over this file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
