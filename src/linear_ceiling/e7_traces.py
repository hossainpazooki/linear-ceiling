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


def approx_tokens(text: str, content_type: str = "assistant") -> int:
    """Bare chars/4 fallback, kept only for tests and for callers with no config.

    NOT the registered counter: measured against o200k_base it is differentially biased by
    content type (-27.8% on tool output, +20.4% on system prompts). Production paths build a
    counter from config via `e7_tokens.make_counter`; see ledger entry 0009.
    """
    return math.ceil(len(text) / 4) if text else 0


_ROLE_TO_CONTENT_TYPE = {"system": "system", "user": "user", "assistant": "assistant",
                         "tool": "tool_output"}


@dataclass(frozen=True)
class Msg:
    role: str                      # system | user | assistant | tool
    tokens: int                    # estimated content tokens (counter applied at load)
    has_tool_calls: bool = False
    tool_names: tuple[str, ...] = ()
    model: str | None = None       # per-step serving model, None when the trace has none
    timestamp: float | None = None # epoch seconds, None when the trace has none
    # Provider-reported prompt tokens for the request this message completed, when the trace
    # carries them (tau2-bench does). This is GROUND TRUTH for token counting -- independent of
    # both the exact encoder and the calibrated divisors of entry 0009 -- so it is the only
    # thing that can validate the estimator rather than compare it to another estimator.
    reported_tokens: int | None = None
    # The request (LLM call) this message belongs to, where the trace records request
    # boundaries (the LangChain family's sub-runs). A receiving model's prefill is the prompt
    # of ITS request, not the trajectory's cumulative prefix (entry 0017 correction).
    request: int | None = None


@dataclass(frozen=True)
class Trajectory:
    suite: str
    agent: str                     # distinct scaffold/submission identity (entry 0007 floor unit)
    traj_id: str
    reward: float | None
    messages: tuple[Msg, ...] = field(default_factory=tuple)
    # The task instance this run was on. Entry 0011: repeated trials are distinct trajectories
    # but NOT independent samples, so coverage reports DISTINCT TASKS beside trajectories.
    task: str | None = None
    # Number of attempts the layout records for this instance (nested `attempt_N` dirs);
    # None when the layout cannot evidence attempts (entry 0014: `branch` is then NOT MEASURABLE).
    attempts: int | None = None

    @property
    def has_step_model_metadata(self) -> bool:
        return any(m.model is not None for m in self.messages)

    @property
    def has_timestamps(self) -> bool:
        return any(m.timestamp is not None for m in self.messages)


def tool_arguments_text(arguments) -> str:
    """Normalize a tool call's arguments to the text that was billed.

    tau-bench stores this field inconsistently BY AGENT (verified 2026-09-01 over the four
    shipped files): gpt-4o records a JSON *string* (4,438 calls), sonnet-35-new records a
    parsed *dict* (9,847 calls). Passing a dict to a character-based counter silently counts
    its KEYS -- a large undercount that this function exists to prevent.

    Dicts are re-serialized compactly because the sibling agent's wire format in the same
    suite is compact (`{"user_id":"mia_li_3668"}`, 25 chars == json.dumps(separators=(",",":"))).
    The original bytes are unrecoverable from a parsed dict, so this is a reconstruction:
    key order follows the trace's, and the compact-vs-spaced choice moves the count by ~1
    char per key (a stated limitation, not a measured one).
    """
    if arguments is None:
        return ""
    if isinstance(arguments, str):
        return arguments
    if isinstance(arguments, dict):
        return json.dumps(arguments, separators=(",", ":"), ensure_ascii=False)
    raise ValueError(f"tool call arguments have unexpected type {type(arguments).__name__}; "
                     "refusing to guess how it was billed")


def _tau_msg(m: dict, counter) -> Msg:
    ctype = _ROLE_TO_CONTENT_TYPE.get(m["role"], "assistant")
    content = m.get("content") or ""
    tokens = counter(content, ctype)
    tool_names = ()
    if m.get("tool_calls"):
        tool_names = tuple(tc["function"]["name"] for tc in m["tool_calls"])
        for tc in m["tool_calls"]:
            args = tool_arguments_text(tc["function"].get("arguments"))
            tokens += counter(tc["function"]["name"], "tool_args") + counter(args, "tool_args")
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
            task=f"{path.stem.rsplit('-', 1)[-1]}/{it.get('task_id')}",   # domain/task_id
        ))
    return out


def coverage(trajectories: list[Trajectory], exclude_agents: tuple[str, ...] = ()) -> dict:
    """Per-suite coverage against entry 0007's floor units: trajectories AND distinct agents,
    with DISTINCT TASKS alongside (entry 0011: trials are not independent samples).

    `exclude_agents` are agents that are a Lane A subject, not a coverage contributor (entry
    0011 names composio: two submissions of one system). Their trajectories are dropped from
    every count here; the caller reports them separately so they are never invisible.
    """
    suites: dict[str, dict] = {}
    for t in trajectories:
        if t.agent in exclude_agents:
            continue
        s = suites.setdefault(t.suite, {"trajectories": 0, "agents": set(), "tasks": set()})
        s["trajectories"] += 1
        s["agents"].add(t.agent)
        if t.task is not None:
            s["tasks"].add(t.task)
    return {k: {"trajectories": v["trajectories"], "agents": sorted(v["agents"]),
                "tasks": len(v["tasks"])} for k, v in suites.items()}


def suite_floor(cov: dict, thresholds: dict) -> dict[str, bool]:
    """Per suite: does it clear entry 0007's per-suite floor (trajectories AND distinct agents)?"""
    return {s: (v["trajectories"] >= thresholds["min_trajectories_per_suite"]
                and len(v["agents"]) >= thresholds["min_agents_per_suite"])
            for s, v in cov.items()}


def meets_floor(cov: dict, thresholds: dict) -> bool:
    """Entry 0007's floor: at least `min_suites` suites, EACH clearing its per-suite floor.

    A suite that fails its own floor does not count toward the suite minimum (entry 0011:
    tau-bench v1 is reported but excluded from floor arithmetic).
    """
    return sum(1 for ok in suite_floor(cov, thresholds).values() if ok) >= thresholds["min_suites"]
