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
              -- from --home-r2 when given, because the summarizer's 1e-9 cross-check runs at HOME
  tau_V       = 1 - (arm (a), generic text) held-out V R^2                    [alongside f* only]
  tau_agent_K = 1 - (arm (b), agent text)   held-out K R^2                    [entry 0025, alongside]

WHAT IT REFUSES TO DO. It will not choose `tau_ladder` or `prefix_invariance_max_delta`. The
2026-09-18 ruling registered both ABSOLUTE and identical to config/e9.toml ([0.10, 0.03] and 1e-4),
so they are already written in the Llama configs and this tool only ECHOES values it is handed via
`--ladder` / `--prefix-delta`, validating them against tau_K. Without them it prints both as
unresolved and exits 3. Which values they take is a registration decision, not a tooling one.

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
    ap.add_argument("--home-r2", default=None,
                    help="a HOME-produced upstream r2.json (score_mapper output over the pulled dumps). "
                         "STRONGLY PREFERRED: see the module docstring on cross-platform jitter.")
    # NOT a registered tolerance. Entry 0028 registers 1e-05 (per-head sums) and 1e-02 (squares) for
    # the keep-subset PER-TOKEN re-score, which is a different comparison; no entry fixes a tolerance
    # for a scorer-level held-out R^2 compared across machines. 1e-6 is an operational default chosen
    # here to be far tighter than anything that would matter and far looser than bit-equality; a
    # difference above it is a finding to be read, not a value to paste.
    ap.add_argument("--jitter-max", type=float, default=1e-6,
                    help="operational default, NOT registered: refuse if home and box R^2 differ by more")
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

    # M5, the trap this option exists to close. The E8 report's R^2 was computed ON THE BOX. The value
    # typed into the config is later cross-checked by `summarize_e9 --calibrate-tau`, which re-scores
    # AT HOME, at a tolerance of 1e-9 -- and entry 0028 exists precisely because float32 reductions do
    # not reproduce bit-for-bit across platforms (it registers 1e-05/1e-02 for the keep-subset per-token
    # re-score; no entry fixes a tolerance for the comparison made here). Taking tau from the box therefore risks a config that
    # refuses at summary time, AFTER sitting B has been paid for and with no repair allowed (the rule
    # and tau are frozen once a score file exists). So when a HOME re-score is available, it is the
    # authority and the box report becomes the cross-check.
    if a.home_r2:
        hp = Path(a.home_r2)
        if not hp.exists():
            raise SystemExit(f"emit_tau REFUSED: {hp} does not exist. Produce it at home by running the "
                             "upstream score_mapper over the PULLED dumps before writing the config.")
        home = json.loads(hp.read_text(encoding="utf-8"))
        deltas, home_tau = {}, {}
        for key, name in (("K", "tau_K"), ("V", "tau_V")):
            field = f"{key}_r2_heldout_layer_mean"
            if field not in home:
                raise SystemExit(f"emit_tau REFUSED: {hp} has no {field}; that is not a score_mapper r2.json")
            home_tau[name] = 1.0 - float(home[field])
            deltas[name] = abs(home_tau[name] - t[name])
        worst = max(deltas.values())
        print(f"# home-vs-box jitter: " + ", ".join(f"{k} {v:.3e}" for k, v in deltas.items()))
        if worst > a.jitter_max:
            raise SystemExit(
                f"emit_tau REFUSED: the home re-score differs from the box by {worst:.3e}, above "
                f"--jitter-max {a.jitter_max:.3e}. That is not a number to paste -- it is a finding. "
                "Entry 0028 registered cross-platform tolerances for the keep-subset per-token re-score "
                "(1e-05 on sums, 1e-02 on squares) because float32 reductions do not reproduce bit-for-bit "
                "across machines; it fixes none for THIS comparison, so a difference this large needs its "
                "own reading before any tau is written.")
        t.update(home_tau)     # the HOME values are what the config gets
        print(f"# tau_K and tau_V taken from the HOME re-score {hp} (box report used as cross-check).")
        print("# tau_agent_K stays from the E8 report: arm (b) has no home re-score of its own.")

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
    print("\nAll three tau values and both pre-registered absolute constants emitted. The summarizer is still the authority: run "
          "`summarize_e9 --calibrate-tau` after typing them in, and believe it over this file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
