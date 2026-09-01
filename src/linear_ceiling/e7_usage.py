"""Estimator validation against provider-reported usage, where a trace carries it (entry 0012).

For every message that carries `reported_tokens` (the provider's `prompt_tokens` for the
request that produced it) and that has a non-empty visible prefix, one point is taken:

    estimated = sum of the counter's tokens over every message BEFORE it   (the visible prefix)
    reported  = what the provider says it billed for that request's prompt
    offset    = reported - estimated          ratio = reported / estimated

Points are split by the ROLE of the requesting message and never pooled: in tau2 the `user`
role is the user-simulator LLM (its whole prompt is visible in the trace) and `assistant` is
the agent LLM (its system prompt and tool schemas are NOT in the trace). They bill against
different prefixes and are different accounting series; pooling them produced an
uninterpretable ratio on the first pass (entry 0012).

The assistant series is additionally binned by assistant-turn position, because a hidden
prefix that is FIXED shows up as an offset that does not grow with turn depth -- which is the
evidence that separates "the trace omits a block" from "the estimator drifts".

Every figure here qualifies a LOWER BOUND: where the offset is large and flat, the visible
messages understate what the provider billed by that much per request.
"""
from collections import defaultdict

from linear_ceiling.e7_stats import summary
from linear_ceiling.e7_traces import Trajectory

TURN_BINS = ((1, 1), (2, 3), (4, 8), (9, None))


def points(trajectories: list[Trajectory]) -> dict[str, list[tuple[int, int]]]:
    """role -> [(estimated_prefix, reported)] over every message with reported usage."""
    by_role: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for t in trajectories:
        prefix = 0
        for m in t.messages:
            if m.reported_tokens and prefix > 0:
                by_role[m.role].append((prefix, m.reported_tokens))
            prefix += m.tokens
    return dict(by_role)


def assistant_points_by_turn(trajectories: list[Trajectory]) -> list[tuple[int, int, int]]:
    """[(assistant_turn_ordinal, estimated_prefix, reported)], ordinal counted over measured turns."""
    out = []
    for t in trajectories:
        prefix, k = 0, 0
        for m in t.messages:
            if m.role == "assistant" and m.reported_tokens and prefix > 0:
                k += 1
                out.append((k, prefix, m.reported_tokens))
            prefix += m.tokens
    return out


def _bin_label(lo: int, hi) -> str:
    return f"{lo}" if hi == lo else (f"{lo}-{hi}" if hi is not None else f"{lo}+")


def validation(trajectories: list[Trajectory]) -> dict | None:
    """The entry-0012 table, recomputed from trajectories; None when no message reports usage."""
    pts = points(trajectories)
    if not pts:
        return None
    per_role = {}
    for role, ps in sorted(pts.items()):
        offsets = [r - e for e, r in ps]
        ratios = [r / e for e, r in ps]
        per_role[role] = {"offset": summary(offsets), "ratio": summary(ratios)}
    by_turn = []
    apts = assistant_points_by_turn(trajectories)
    for lo, hi in TURN_BINS:
        sel = [(e, r) for k, e, r in apts if lo <= k and (hi is None or k <= hi)]
        if sel:
            by_turn.append({"turns": _bin_label(lo, hi), **summary([r - e for e, r in sel])})
    return {"per_role": per_role, "assistant_by_turn": by_turn,
            "definition": "offset = reported prompt tokens - estimated visible prefix; "
                          "per requesting role, never pooled (entry 0012)"}
