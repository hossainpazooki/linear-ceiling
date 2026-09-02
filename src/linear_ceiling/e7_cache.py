"""Cache-aware readings of H-E7a's denominator (`summarize_e7 --cache-aware-ratio`, entry 0024).

Entry 0006's rule reads "recoverable prefill spend at switch points >= 10% of the trajectory
set's total input-token spend" and 0014 fixed WHICH set (the Lane A measurable subset) but not
HOW the spend is priced. The registered figure (0015/0018) prices it cache-obliviously: every
assistant turn is a request that re-bills the trajectory's whole visible prefix at the base
price (`e7_cost.timeline`, cold bound). The numerator is a one-off transfer at a switch. Under
the same pinned pricing a client that caches pays read_mult on a prefix it has already
prefilled, so the denominator has a second reading a reviewer will compute. This module
reports the ratio under every reading, in base-input-price token units, and states nothing
about the verdict (a numbered entry re-examines it against the rule as written).

Two request models x two cache bounds:

- REGISTERED requests (the 0018 denominator): each assistant message is a request whose
  prefill is the trajectory prefix. COLD = the registered denominator by construction; WARM =
  `e7_cost.timeline`'s warm bound (the previous prefix at read_mult, the new messages at
  write_mult -- byte-identical by construction, the prefix is append-only).
- REQUEST-LEVEL requests (entry 0017's reading of `paid`): where the trace records request
  boundaries (`Msg.request`, the LangChain family), a request's prefill is ITS OWN prompt --
  the messages of that request before its response, joined by newline (0017). COLD = every
  prompt at the base price; WARM = the longest byte-identical prefix shared with the PRECEDING
  request's prompt at read_mult, the remainder at write_mult. Tokens inside the shared prefix
  are attributed in proportion to characters (the counter is character-based for this family
  already, 0009). Composio's sub-runs re-render the transcript, so this prefix is a real
  measurement, not append-only by construction.

Both readings keep the numerator (0010/0013/0018 upper bound) unchanged and the 0014
denominator set. Neither includes the hidden prefix (0012): both remain visible-only LOWER
BOUNDS on spend, and the warm bound understates MORE, because the hidden block is the most
cacheable content there is. A measurable trajectory without request boundaries is counted as
NOT COMPUTABLE for the request-level reading, never folded in as zero.
"""
from os.path import commonprefix

from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_lanes import lane_a
from linear_ceiling.e7_traces import Trajectory

READINGS = ("registered_cold", "registered_warm", "request_cold", "request_warm")


def request_prompts(traj: Trajectory, texts: list[str]) -> list[dict]:
    """One record per recorded request, in order of first appearance: its prompt tokens and
    text (every message of the request before its response, the request's LAST assistant
    message). A trajectory with no request boundaries yields []."""
    if len(texts) != len(traj.messages):
        raise ValueError(f"{traj.traj_id}: texts ({len(texts)}) must align with messages ({len(traj.messages)})")
    order: list = []
    members: dict = {}
    for j, m in enumerate(traj.messages):
        if m.request is None:
            continue
        if m.request not in members:
            order.append(m.request)
            members[m.request] = []
        members[m.request].append(j)
    out = []
    for r in order:
        idx = members[r]
        responses = [j for j in idx if traj.messages[j].role == "assistant"]
        resp = responses[-1] if responses else None
        prompt = [j for j in idx if resp is None or j < resp]
        out.append({"request": r, "prompt_tokens": sum(traj.messages[j].tokens for j in prompt),
                    "text": "\n".join(texts[j] for j in prompt)})
    return out


def request_level_costs(traj: Trajectory, texts: list[str], pricing: dict) -> dict | None:
    """Request-level cold/warm input cost (base-input-price units) or None without boundaries."""
    reqs = request_prompts(traj, texts)
    if not reqs:
        return None
    read_m, write_m = float(pricing["read_mult"]), float(pricing["write_mult"])
    prev_text = None
    cold = warm = shared_total = 0.0
    for r in reqs:
        paid = r["prompt_tokens"]
        if prev_text is None or not r["text"]:
            shared = 0.0
        else:
            shared = paid * len(commonprefix([prev_text, r["text"]])) / len(r["text"])
        new = paid - shared
        warm += shared * read_m + new * write_m
        cold += paid
        shared_total += shared
        prev_text = r["text"]
    return {"requests": len(reqs), "input_tokens": cold, "shared_prefix_tokens": shared_total,
            "cost_warm": warm, "cost_cold": cold}


def cache_aware_block(trajectories: list[Trajectory], texts: dict[str, list[str]], headroom_rows: list[dict],
                      pricing: dict, cutoff: float) -> dict:
    """Per suite and pooled, over the Lane A measurable subset (0014): the numerator and the
    four denominators, each with its ratio against the cutoff."""
    num: dict[str, float] = {}
    for r in headroom_rows:
        suite = next(t.suite for t in trajectories if t.traj_id == r["traj_id"])
        num[suite] = num.get(suite, 0.0) + r["headroom_upper_bound"]
    acc: dict[str, dict] = {}
    for t in trajectories:
        if not lane_a(t).measurable:
            continue
        a = acc.setdefault(t.suite, {"measurable_trajs": 0, "request_level_not_computable": 0,
                                     "registered_cold": 0.0, "registered_warm": 0.0,
                                     "request_cold": 0.0, "request_warm": 0.0, "request_shared_prefix_tokens": 0.0,
                                     "request_count": 0})
        a["measurable_trajs"] += 1
        tot = totals(timeline(t, pricing))
        a["registered_cold"] += tot["cost_cold"]
        a["registered_warm"] += tot["cost_warm"]
        rl = request_level_costs(t, texts[t.traj_id], pricing) if t.traj_id in texts else None
        if rl is None:
            a["request_level_not_computable"] += 1
            continue
        a["request_cold"] += rl["cost_cold"]
        a["request_warm"] += rl["cost_warm"]
        a["request_shared_prefix_tokens"] += rl["shared_prefix_tokens"]
        a["request_count"] += rl["requests"]

    def block(suite_acc: dict, n: float) -> dict:
        out = {"measurable_trajs": suite_acc["measurable_trajs"],
               "request_level_not_computable": suite_acc["request_level_not_computable"],
               "recoverable_upper_bound": n, "denominators": {}, "ratios": {}, "below_cutoff": {}}
        for key in READINGS:
            d = suite_acc[key]
            if key.startswith("request") and suite_acc["request_level_not_computable"] == suite_acc["measurable_trajs"]:
                d = None
            out["denominators"][key] = d
            out["ratios"][key] = (n / d) if d else None
            out["below_cutoff"][key] = ((n / d) < cutoff) if d else None
        out["request_shared_prefix_fraction"] = (suite_acc["request_shared_prefix_tokens"] / suite_acc["request_cold"]
                                                 if suite_acc["request_cold"] else None)
        out["requests"] = suite_acc["request_count"]
        return out

    per_suite = {s: block(acc[s], num.get(s, 0.0)) for s in sorted(acc)}
    pooled_acc = {k: sum(acc[s][k] for s in acc) for k in next(iter(acc.values()))} if acc else None
    return {"cutoff": cutoff, "readings": list(READINGS),
            "numerator": "entry-0010 upper bound summed over observed switches (unchanged)",
            "denominator_set": "Lane A measurable subset (entry 0014)",
            "pricing": {"read_mult": pricing["read_mult"], "write_mult": pricing["write_mult"]},
            "per_suite": per_suite,
            "pooled": block(pooled_acc, sum(num.values())) if pooled_acc else None}


def _row(name: str, b: dict) -> str:
    cells = []
    for key in READINGS:
        d, r = b["denominators"][key], b["ratios"][key]
        if d is None:
            cells.append("NOT COMPUTABLE")
        else:
            cells.append(f"{d:,.0f} -> **{100*r:.2f}%** ({'below' if b['below_cutoff'][key] else 'AT OR ABOVE'})")
    return f"| {name} ({b['measurable_trajs']} trajs) | {b['recoverable_upper_bound']:,.0f} | " + " | ".join(cells) + " |"


def render(cb: dict) -> str:
    head = ("| scope | numerator | registered requests, COLD (= 0018) | registered, WARM | "
            "request-level, COLD | request-level, WARM |\n|---|---|---|---|---|---|")
    rows = [_row(s, b) for s, b in cb["per_suite"].items()]
    if cb["pooled"]:
        rows.append(_row("**pooled**", cb["pooled"]))
        p = cb["pooled"]
        sf = p["request_shared_prefix_fraction"]
        shared = (f"request-level shared byte-identical prefix: {100*sf:.1f}% of request-level prefill tokens "
                  f"over {p['requests']} requests" if sf is not None else "request-level reading NOT COMPUTABLE")
        nc = (f"; {p['request_level_not_computable']} measurable trajectories without request boundaries "
              "(NOT COMPUTABLE, never zero)" if p["request_level_not_computable"] else "")
    else:
        shared, nc = "no Lane A measurable trajectory", ""
    return ("H-E7a under every reading of \"input-token spend\" (entry 0024; `--cache-aware-ratio`; base-input-price "
            f"token units; cutoff {100*cb['cutoff']:.0f}%; read_mult {cb['pricing']['read_mult']}, write_mult "
            f"{cb['pricing']['write_mult']}):\n\n{head}\n" + "\n".join(rows)
            + f"\n\n{shared}{nc}.\nAll four denominators are visible-only LOWER BOUNDS on spend (0012); the warm "
              "bounds understate more, because the hidden prefix is the most cacheable content. The verdict is "
              "NOT re-stated here; a numbered entry re-examines it under each reading against the rule as written.")
