"""The invalidation taxonomy, exactly as registered in ledger entry 0014.

Six event classes, each with a detection rule and a measurability rule. A trajectory that
cannot evidence a class is NOT MEASURABLE for it and enters neither side of that class's
frequency -- never a zero (entry 0006's Lane A rule, generalized by 0014 to every class).

    model_switch        Lane A (e7_lanes): consecutive assistant turns with different serving model
    rerender_at_switch  a model_switch whose handoff is not byte-identical (e7_headroom rows)
    compaction          provider-reported prompt size DECREASES between consecutive agent requests
    idle_expiry         gap between consecutive agent requests exceeds the TTL (entry 0007: 300 s)
    branch              more than one recorded attempt on the instance (nested layout only)
    edit                in-place modification of an earlier message: no corpus can evidence it

`branch` events are counted as attempts - 1 (the extra attempts), so one attempt is zero
events and a flat layout is NOT MEASURABLE. Tool-output truncation before insertion is not a
compaction event: the prompt still grows (entry 0014).

Frequencies ship per agent alongside pooled (entry 0007): for every class, the measurable
trajectory count, trajectories with >= 1 event, total events, and the NOT MEASURABLE count.
No class may be added, merged, or redefined after the first frequency table is computed.
"""
from linear_ceiling.e7_lanes import lane_a
from linear_ceiling.e7_traces import Trajectory

CLASSES = ("model_switch", "rerender_at_switch", "compaction", "idle_expiry", "branch", "edit")


def _pairs(traj: Trajectory, attr: str):
    vals = [getattr(m, attr) for m in traj.messages if m.role == "assistant" and getattr(m, attr)]
    return list(zip(vals, vals[1:]))


def classify(traj: Trajectory, headroom_rows_for_traj: list[dict] | None, ttl_seconds: float) -> dict:
    """class -> {"measurable": bool, "events": int | None}. `headroom_rows_for_traj` is the
    trajectory's entry-0010 rows, or None when the adapter exposed no text."""
    out: dict[str, dict] = {}
    a = lane_a(traj)
    out["model_switch"] = {"measurable": a.measurable,
                           "events": len(a.switches) if a.measurable else None}
    if a.measurable and headroom_rows_for_traj is not None:
        out["rerender_at_switch"] = {"measurable": True,
                                     "events": sum(1 for r in headroom_rows_for_traj if not r["byte_identical"])}
    else:
        out["rerender_at_switch"] = {"measurable": False, "events": None}
    rp = _pairs(traj, "reported_tokens")
    out["compaction"] = ({"measurable": True, "events": sum(1 for a_, b in rp if b < a_)} if rp
                         else {"measurable": False, "events": None})
    tp = _pairs(traj, "timestamp")
    out["idle_expiry"] = ({"measurable": True, "events": sum(1 for a_, b in tp if b - a_ > ttl_seconds)} if tp
                          else {"measurable": False, "events": None})
    out["branch"] = ({"measurable": True, "events": max(traj.attempts - 1, 0)} if traj.attempts is not None
                     else {"measurable": False, "events": None})
    out["edit"] = {"measurable": False, "events": None}
    return out


def _empty_row() -> dict:
    return {c: {"measurable_trajs": 0, "trajs_with_event": 0, "events": 0, "not_measurable": 0}
            for c in CLASSES}


def _add(row: dict, cls: dict) -> None:
    for c in CLASSES:
        cell, r = cls[c], row[c]
        if cell["measurable"]:
            r["measurable_trajs"] += 1
            r["events"] += cell["events"]
            r["trajs_with_event"] += 1 if cell["events"] > 0 else 0
        else:
            r["not_measurable"] += 1


def frequencies(per_traj: dict[str, dict], trajectories: list[Trajectory]) -> dict:
    """{"per_agent": {"suite/agent": row}, "per_suite": {suite: row}, "pooled": row}."""
    per_agent: dict[str, dict] = {}
    per_suite: dict[str, dict] = {}
    pooled = _empty_row()
    for t in trajectories:
        cls = per_traj[t.traj_id]
        _add(per_agent.setdefault(f"{t.suite}/{t.agent}", _empty_row()), cls)
        _add(per_suite.setdefault(t.suite, _empty_row()), cls)
        _add(pooled, cls)
    return {"classes": list(CLASSES),
            "per_agent": dict(sorted(per_agent.items())),
            "per_suite": dict(sorted(per_suite.items())),
            "pooled": pooled}


def h_e7a(trajectories: list[Trajectory], input_tokens: dict[str, int], headroom_rows: list[dict],
          cutoff: float) -> dict:
    """The entry-0014 ratio: recoverable upper bound at observed switches / total input spend
    of the Lane A MEASURABLE subset, per suite and pooled, both in base-input-price token
    units. Reports the comparison against the cutoff; the VERDICT is a numbered entry's."""
    rec: dict[str, float] = {}
    for r in headroom_rows:
        suite = next(t.suite for t in trajectories if t.traj_id == r["traj_id"])
        rec[suite] = rec.get(suite, 0.0) + r["headroom_upper_bound"]
    den: dict[str, int] = {}
    n_meas: dict[str, int] = {}
    for t in trajectories:
        if lane_a(t).measurable:
            den[t.suite] = den.get(t.suite, 0) + input_tokens[t.traj_id]
            n_meas[t.suite] = n_meas.get(t.suite, 0) + 1
    def block(num: float, d: int, n: int) -> dict:
        if d == 0:
            return {"measurable_trajs": n, "recoverable_upper_bound": num, "input_spend": d,
                    "ratio": None, "below_cutoff": None}
        return {"measurable_trajs": n, "recoverable_upper_bound": num, "input_spend": d,
                "ratio": num / d, "below_cutoff": (num / d) < cutoff}
    per_suite = {s: block(rec.get(s, 0.0), den.get(s, 0), n_meas.get(s, 0))
                 for s in sorted(set(den) | set(rec))}
    return {"denominator": "Lane A measurable subset (entry 0014)", "cutoff": cutoff,
            "numerator": "entry-0010 upper bound summed over observed switches (ratio is an upper bound)",
            "per_suite": per_suite,
            "pooled": block(sum(rec.values()), sum(den.values()), sum(n_meas.values()))}
