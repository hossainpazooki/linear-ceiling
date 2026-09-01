"""tau2-bench adapter — the corpus that carries ground truth.

tau2-bench ships completed simulation results (`data/tau2/results/final/*.json`), each file one
agent model on one domain with N trials. Unlike every other corpus reached so far, its messages
carry provider-reported `usage.prompt_tokens`, per-message ISO `timestamp`, and per-message
`cost`, which makes it the only suite where the token estimator can be VALIDATED rather than
compared to another estimator, and the only one where realized idle-gap expiry is computable
instead of bounded (ledger entry 0007's two-bound rule remains the rule for the rest).

Two models run in every simulation: the agent LLM (`info.agent_info.llm`) and the user-simulator
LLM (`info.user_info.llm`). The simulator is a benchmark construct standing in for a human, not
a serving-model handoff of the agent's context, so counting the alternation as a switch would
manufacture a Lane A finding out of benchmark scaffolding. Lane A compares consecutive ASSISTANT
turns only (entry 0006), which excludes it by construction -- no special-casing needed.

`Msg.model` is left None even for assistant turns: tau2 records the agent model at RUN level
(`info.agent_info.llm`), not per step, and entry 0006's Lane A counts only per-step records.
Run-level metadata names the configured model, not what served each step, so it cannot evidence
absence of switching within the run. tau2 is therefore NOT MEASURABLE for Lane A, and that is
the honest outcome rather than a measured zero.
"""
import json
from datetime import datetime
from pathlib import Path

from linear_ceiling.e7_traces import Msg, Trajectory

_ROLE_TO_CONTENT_TYPE = {"system": "system", "user": "user", "assistant": "assistant",
                         "tool": "tool_output"}


def parse_ts(value) -> float | None:
    """ISO-8601 -> epoch seconds; None when absent or unparseable (never a guess)."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        return None


def agent_of(doc: dict) -> str:
    """The agent model identity for a results file, from its own recorded run info."""
    info = doc.get("info") or {}
    llm = (info.get("agent_info") or {}).get("llm")
    if not llm:
        raise ValueError("tau2 results file has no info.agent_info.llm; cannot name the agent")
    return str(llm)


def _message(m: dict, counter) -> Msg:
    role = str(m.get("role") or "assistant")
    ctype = _ROLE_TO_CONTENT_TYPE.get(role, "assistant")
    tokens = counter(m.get("content") or "", ctype)
    names = []
    for tc in (m.get("tool_calls") or []):
        if not isinstance(tc, dict):
            continue
        fn = tc.get("function") if isinstance(tc.get("function"), dict) else tc
        name = fn.get("name") or ""
        names.append(name)
        args = fn.get("arguments", fn.get("args", ""))
        if isinstance(args, dict):
            args = json.dumps(args, separators=(",", ":"), ensure_ascii=False)
        tokens += counter(str(name), "tool_args") + counter(str(args or ""), "tool_args")
    usage = m.get("usage")
    reported = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    return Msg(role=role, tokens=tokens, has_tool_calls=bool(names), tool_names=tuple(names),
               model=None, timestamp=parse_ts(m.get("timestamp")),
               reported_tokens=reported if isinstance(reported, int) else None)


def load_tau2(path: Path, counter) -> list[Trajectory]:
    """One tau2 results file -> one Trajectory per simulation (task x trial)."""
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "simulations" not in doc:
        raise ValueError(f"{path}: not a tau2 results file (no 'simulations' key)")
    agent = agent_of(doc)
    out = []
    for sim in doc["simulations"]:
        msgs = sim.get("messages") or []
        if not msgs:
            continue
        out.append(Trajectory(
            suite="tau2-bench", agent=agent,
            traj_id=f"{agent}/{sim.get('task_id')}/{sim.get('trial')}",
            reward=(sim.get("reward_info") or {}).get("reward"),
            messages=tuple(_message(m, counter) for m in msgs),
        ))
    return out
