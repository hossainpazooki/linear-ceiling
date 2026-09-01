"""Adapter for the SWE-bench role/content family — the broadest structured family.

29 of the structured verified submissions carry an OpenAI-style message list. Four shape
variants were observed and this adapter handles all four rather than one per variant, because
they differ only in wrapping and extra keys, never in the fields E7 reads:

- `list:content,role`                (honeycomb, lingma, openhands, entroPO, bloop, trae, ...)
- `list:agent,content,role`          (marscode, trae)          -- extra `agent` key, ignored
- `list:content,role,template`       (autocoderover)           -- extra `template` key, ignored
- `dict[messages]:content,role`      (Skywork, SAGE, livesweagent)

`content` is a plain string in most variants and a list of content blocks in openhands-style
files; both are handled. Tool calls appear as `tool_calls` (OpenAI shape) where present.

Serving-model identity: this family generally does NOT record a per-step model, so Lane A
reports NOT MEASURABLE for it — never a zero (ledger entries 0006/0010). Where a per-step
model IS present (livesweagent nests it at `$.messages[i].extra.response.model`), the
registered-breadth detector finds it and Lane A becomes measurable for that submission.
"""
import json
from pathlib import Path

from linear_ceiling.e7_swe import load_jsonl, models_in
from linear_ceiling.e7_traces import Msg, Trajectory

_MESSAGE_LIST_KEYS = ("messages", "trajectory", "history", "conversation")
_ROLE_TO_CONTENT_TYPE = {"system": "system", "user": "user", "assistant": "assistant",
                         "tool": "tool_output"}


def find_message_list(doc):
    """The message list in either wrapping, or None if this is not a role/content document."""
    if isinstance(doc, list):
        lst = doc
    elif isinstance(doc, dict):
        lst = next((doc[k] for k in _MESSAGE_LIST_KEYS
                    if isinstance(doc.get(k), list) and doc[k]), None)
    else:
        return None
    if not isinstance(lst, list) or not lst:
        return None
    if not any(isinstance(m, dict) and "role" in m for m in lst):
        return None
    return lst


def content_text(content) -> str:
    """Message text from either a plain string or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for b in content:
            if isinstance(b, str):
                out.append(b)
            elif isinstance(b, dict):
                t = b.get("text") or b.get("content")
                if isinstance(t, str):
                    out.append(t)
        return "".join(out)
    return ""


def _messages_from_file(path: Path):
    """Message list from one file, or None if it is not a role/content document.

    A nested-layout instance directory contains non-trajectory files beside the trajectories
    (a `.diff`, `selected_patch.json`, `regression_test_result_0.json`). Returning None for
    those lets the caller skip them without treating a genuine parse failure as absence.
    """
    path = Path(path)
    if path.suffix == ".jsonl":
        try:
            doc = load_jsonl(path)
        except json.JSONDecodeError:
            return None
    elif path.suffix == ".json":
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    else:
        return None                      # .diff and friends are not trajectories
    return find_message_list(doc)


def load_role_content_trajectory(files: list[Path], agent: str, traj_id: str, counter) -> Trajectory:
    """One trajectory from one or more stage files, concatenated in the given order."""
    msgs: list[Msg] = []
    used = 0
    for f in files:
        lst = _messages_from_file(f)
        if lst is None:
            continue
        used += 1
        msgs.extend(_messages_from_list(lst, counter))
    if not msgs:
        raise ValueError(f"{traj_id}: no role/content messages in {len(files)} file(s); wrong adapter")
    return Trajectory(suite="swe-bench", agent=agent, traj_id=f"{agent}/{traj_id}",
                      reward=None, messages=tuple(msgs), task=traj_id)


def load_role_content(path: Path, agent: str, counter) -> Trajectory:
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    lst = find_message_list(doc)
    if lst is None:
        raise ValueError(f"{path}: no role/content message list found; wrong adapter for this shape")
    messages = _messages_from_list(lst, counter)
    if not messages:
        raise ValueError(f"{path}: message list contained no role-bearing messages")
    return Trajectory(suite="swe-bench", agent=agent, traj_id=f"{agent}/{path.stem}",
                      reward=None, messages=tuple(messages), task=path.stem)


def _messages_from_list(lst, counter) -> list[Msg]:
    messages = []
    for m in lst:
        if not isinstance(m, dict) or "role" not in m:
            continue
        role = str(m.get("role") or "assistant")
        ctype = _ROLE_TO_CONTENT_TYPE.get(role, "assistant")
        tokens = counter(content_text(m.get("content")), ctype)
        tool_calls = m.get("tool_calls") or []
        names = []
        for tc in tool_calls if isinstance(tool_calls, list) else []:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function") if isinstance(tc.get("function"), dict) else tc
            name = fn.get("name") or ""
            names.append(name)
            args = fn.get("arguments", fn.get("args", ""))
            if isinstance(args, dict):
                args = json.dumps(args, separators=(",", ":"), ensure_ascii=False)
            tokens += counter(str(name), "tool_args") + counter(str(args or ""), "tool_args")
        found = models_in(m)          # registered-breadth detector (entry 0010)
        messages.append(Msg(role=role, tokens=tokens, has_tool_calls=bool(names),
                            tool_names=tuple(names), model=found[0] if found else None))
    return messages
