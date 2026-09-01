"""Per-trajectory token/cost timeline under the registered cost model (entries 0006/0007).

A request is each assistant message: its input is every message before it, its output is
itself. Costs are in units of the base input-token price (multiply by a $/token rate to get
dollars), so pricing multipliers are the only pricing inputs.

Two bounds per entry 0007 (traces without timestamps -- tau-bench's case -- get both):

- WARM (cache never expires): the first request cache-writes its whole input at write_mult;
  each later request cache-reads everything it has seen before (the previous request's input
  plus that request's own output) at read_mult and cache-writes only the messages new since
  then at write_mult. Append-only prefixes are assumed -- true of the tau-bench format, and
  an invalidation event in other suites ends the reusable prefix instead.
- COLD (cache expired at every gap): the economically rational client stops caching, so
  every request pays its full input at the base price (multiplier 1.0). Note cold equals
  no-cache under this pricing model.

Where timestamps exist, `expired` uses them against ttl_seconds and the single realized
timeline replaces the bounds. Output tokens are carried but priced by neither bound -- output
price is identical across caching strategies and cancels in every comparison E7 makes.
"""
from dataclasses import dataclass

from linear_ceiling.e7_traces import Trajectory


@dataclass(frozen=True)
class RequestCost:
    index: int              # message index of the assistant turn
    input_tokens: int       # full prefix at this request
    new_input_tokens: int   # portion not seen by the previous request
    output_tokens: int
    cost_warm: float        # input cost, warm bound (base-input-price units)
    cost_cold: float        # input cost, cold bound (== no-cache)


def timeline(traj: Trajectory, pricing: dict) -> list[RequestCost]:
    read_m, write_m = float(pricing["read_mult"]), float(pricing["write_mult"])
    out, seen = [], 0   # `seen` = tokens already in cache under the warm bound
    prefix = 0
    for i, m in enumerate(traj.messages):
        if m.role != "assistant":
            prefix += m.tokens
            continue
        new = prefix - seen
        if new < 0:
            raise ValueError(f"{traj.traj_id}: prefix shrank at message {i}; append-only assumption violated")
        out.append(RequestCost(
            index=i,
            input_tokens=prefix,
            new_input_tokens=new,
            output_tokens=m.tokens,
            cost_warm=seen * read_m + new * write_m,
            cost_cold=float(prefix),
        ))
        seen = prefix + m.tokens    # the assistant output joins the cached prefix
        prefix += m.tokens
    return out


def totals(rows: list[RequestCost]) -> dict:
    return {
        "requests": len(rows),
        "input_tokens": sum(r.input_tokens for r in rows),
        "output_tokens": sum(r.output_tokens for r in rows),
        "cost_warm": sum(r.cost_warm for r in rows),
        "cost_cold": sum(r.cost_cold for r in rows),
    }
