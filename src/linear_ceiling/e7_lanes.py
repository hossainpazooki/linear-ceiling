"""The two switch-point lanes, exactly as registered (entry 0006, amended by 0007).

Lane A (measured, ALONE decides H-E7a): a switch point exists only where per-step model
metadata records the serving model and it changes between consecutive assistant turns. A
trajectory without per-step metadata is NOT MEASURABLE -- it is excluded from Lane A's
denominator, never counted as zero switches. `measurable=False` with `switches=None` is the
honest encoding; the premise finding is stated over the measurable subset plus the count of
unmeasurable trajectories.

Lane B (counterfactual, descriptive only, never resolves any hypothesis): the registered
two-tier cascade -- an assistant turn that issues tool calls runs on the small tier, a plain
planning/reasoning turn runs on the large tier; every boundary between consecutive assistant
turns of different tiers is a switch point. No other policy may be computed without a new
numbered ledger entry registered before its replay.
"""
from dataclasses import dataclass

from linear_ceiling.e7_traces import Trajectory


@dataclass(frozen=True)
class LaneA:
    measurable: bool
    switches: tuple[int, ...] | None   # assistant-message indices where the model changed


@dataclass(frozen=True)
class LaneB:
    tiers: tuple[str, ...]             # per assistant turn: "large" (plan) | "small" (tool)
    switches: tuple[int, ...]          # assistant-turn ordinals where the tier changed


def lane_a(traj: Trajectory) -> LaneA:
    assistants = [m for m in traj.messages if m.role == "assistant"]
    if not any(m.model is not None for m in assistants):
        return LaneA(measurable=False, switches=None)
    if any(m.model is None for m in assistants):
        # partial metadata is not measurable either: a gap could hide or invent a switch
        return LaneA(measurable=False, switches=None)
    switches = tuple(
        i for i in range(1, len(assistants)) if assistants[i].model != assistants[i - 1].model
    )
    return LaneA(measurable=True, switches=switches)


def lane_b(traj: Trajectory) -> LaneB:
    tiers = tuple(
        "small" if m.has_tool_calls else "large"
        for m in traj.messages if m.role == "assistant"
    )
    switches = tuple(i for i in range(1, len(tiers)) if tiers[i] != tiers[i - 1])
    return LaneB(tiers=tiers, switches=switches)
