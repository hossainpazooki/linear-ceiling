"""Normalized trajectory model and suite adapters for E7.

Grounded in the real tau-bench artifact (historical_trajectories/gpt-4o-airline.json,
inspected 2026-09-01): a JSON list of {task_id, reward, info, traj, trial} where traj is an
OpenAI-style message list (system/user/assistant/tool; assistant messages may carry
tool_calls and null content). Those files carry NO per-message timestamps, NO usage/token
fields, and NO per-step model identity -- the model is run-level, encoded in the filename.
Three consequences, all registered or flagged:

- Lane A must distinguish "not measurable" (no per-step model metadata) from "zero switches"
  (metadata present, no change). Absence of metadata is never counted as zero (entry 0006's
  Lane A counts only where metadata records the model per step).
- Timestamps absent => expiry-sensitive numbers use entry 0007's two-bound rule.
- Token counts must be ESTIMATED. `approx_tokens` (chars/4, ceil) is a stand-in that is
  NON-VERDICT-BEARING: no number derived from it may decide a hypothesis until a successor
  ledger entry registers the tokenization method. Every loader takes a pluggable counter so
  the registered method drops in without touching adapters.
"""
import json
import math
from dataclasses import dataclass, field
from pathlib import Path


def approx_tokens(text: str) -> int:
    """chars/4 estimate. NON-VERDICT-BEARING until a ledger entry registers the tokenizer."""
    return math.ceil(len(text) / 4) if text else 0


@dataclass(frozen=True)
class Msg:
    role: str                      # system | user | assistant | tool
    tokens: int                    # estimated content tokens (counter applied at load)
    has_tool_calls: bool = False
    tool_names: tuple[str, ...] = ()
    model: str | None = None       # per-step serving model, None when the trace has none
    timestamp: float | None = None # epoch seconds, None when the trace has none


@dataclass(frozen=True)
class Trajectory:
    suite: str
    agent: str                     # distinct scaffold/submission identity (entry 0007 floor unit)
    traj_id: str
    reward: float | None
    messages: tuple[Msg, ...] = field(default_factory=tuple)

    @property
    def has_step_model_metadata(self) -> bool:
        return any(m.model is not None for m in self.messages)

    @property
    def has_timestamps(self) -> bool:
        return any(m.timestamp is not None for m in self.messages)


def _tau_msg(m: dict, counter) -> Msg:
    content = m.get("content") or ""
    tokens = counter(content)
    tool_names = ()
    if m.get("tool_calls"):
        tool_names = tuple(tc["function"]["name"] for tc in m["tool_calls"])
        for tc in m["tool_calls"]:
            tokens += counter(tc["function"]["name"]) + counter(tc["function"].get("arguments") or "")
    return Msg(role=m["role"], tokens=tokens, has_tool_calls=bool(m.get("tool_calls")),
               tool_names=tool_names)


def load_tau_bench(path: Path, agent: str, counter=approx_tokens) -> list[Trajectory]:
    """One tau-bench historical_trajectories file -> normalized trajectories.

    `agent` is the run identity from the filename (e.g. "gpt-4o"); tau-bench ships two
    agents in-repo, which alone CANNOT satisfy entry 0007's >= 3 distinct agents per suite --
    tau-bench can only ever ship as partial-with-coverage-stated unless more agents' runs
    are sourced.
    """
    path = Path(path)
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError(f"{path}: expected a JSON list of trajectory records, got {type(items).__name__}")
    out = []
    for it in items:
        traj = it.get("traj")
        if not isinstance(traj, list) or not traj:
            raise ValueError(f"{path}: record task_id={it.get('task_id')!r} has no traj message list")
        out.append(Trajectory(
            suite="tau-bench",
            agent=agent,
            traj_id=f"{path.stem}/{it.get('task_id')}/{it.get('trial')}",
            reward=it.get("reward"),
            messages=tuple(_tau_msg(m, counter) for m in traj),
        ))
    return out


def coverage(trajectories: list[Trajectory]) -> dict:
    """Per-suite coverage against entry 0007's floor units: trajectories AND distinct agents."""
    suites: dict[str, dict] = {}
    for t in trajectories:
        s = suites.setdefault(t.suite, {"trajectories": 0, "agents": set()})
        s["trajectories"] += 1
        s["agents"].add(t.agent)
    return {k: {"trajectories": v["trajectories"], "agents": sorted(v["agents"])} for k, v in suites.items()}
