"""SWE-bench trajectory adapters, and the per-step serving-model detector.

Trajectories are not in the `SWE-bench/experiments` repo; they live in a public S3 bucket at
`verified/<submission>/trajs/<instance>.<ext>` (see docs/2026-09-01-swe-bench-trace-recon.md).
Formats differ per submitter, so an adapter states which shape it handles and refuses anything
else rather than guessing.

**Detector breadth is a registered requirement (ledger entry 0010).** Serving identity appears
under `model` in some families and `model_id` / `model_name` in others; a detector narrower
than the corpus produces false NOT MEASURABLE and false zeros, both of which flatter the
premise finding. `MODEL_KEYS` is the registered minimum, every Lane A output records the key
set it used, and a narrow detector is a defect, never a null result.

Currently implemented: the LangChain-style family (composio_swekit), the only public family
observed to switch serving model mid-trajectory. Its file is a list of sub-runs; each sub-run
is a list of LangChain message dicts under `kwargs`, and serving identity is echoed per
response under `kwargs.response_metadata.model_id` or `llm_output.model_name`.
"""
import json
from pathlib import Path

from linear_ceiling.e7_traces import Msg, Trajectory

MODEL_KEYS = ("model", "model_id", "model_name")   # registered minimum, entry 0010

_ROLE_BY_LC_TYPE = {"human": "user", "ai": "assistant", "system": "system", "tool": "tool"}


def models_in(obj, keys=MODEL_KEYS, _depth=0) -> list[str]:
    """Every serving-identity string anywhere in `obj`, in document order (duplicates kept)."""
    out: list[str] = []
    if _depth > 12:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and isinstance(v, str) and v and v.lower() != "default":
                out.append(v)
            out.extend(models_in(v, keys, _depth + 1))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(models_in(v, keys, _depth + 1))
    return out


def _lc_text(kw: dict) -> str:
    c = kw.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):   # content blocks
        return "".join(b.get("text", "") for b in c if isinstance(b, dict))
    return ""


def _lc_role(kw: dict, node: dict) -> str:
    for src in (node.get("id"), kw.get("type")):
        if isinstance(src, list):
            src = ".".join(str(x) for x in src)
        if isinstance(src, str):
            low = src.lower()
            for key, role in _ROLE_BY_LC_TYPE.items():
                if key in low:
                    return role
    return "assistant"


def discover_trajectories(submission_dir: Path) -> list[tuple[str, list[Path]]]:
    """Group a submission's files into trajectories, handling both observed S3 layouts.

    A TRAJECTORY is one agent run on one task instance -- not one file. Two layouts exist
    under `verified/<submission>/trajs/`:

    - flat:   `<instance>.json`                      -> one file is one trajectory
    - nested: `<instance>/attempt_N/<stage>.json`    -> MANY files are one trajectory

    Counting files as trajectories in the nested layout inflates the count (observed: 4
    instances presenting as 8+ files) and the count feeds entry 0007's coverage floor, so the
    unit matters. Stage files are returned sorted so concatenation is deterministic.
    """
    submission_dir = Path(submission_dir)
    out: list[tuple[str, list[Path]]] = []
    for child in sorted(submission_dir.iterdir()):
        if child.is_dir():
            files = sorted(p for p in child.rglob("*") if p.is_file())
            if files:
                out.append((child.name, files))
        elif child.is_file():
            out.append((child.stem, [child]))
    return out


def load_jsonl(path: Path) -> list:
    """Parse a .jsonl trajectory (one JSON value per line)."""
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _llmresult_texts(node: dict) -> list[str]:
    """Response texts from a LangChain LLMResult node ({llm_output, run, generations})."""
    if "generations" not in node:
        return []
    out = []
    for outer in node.get("generations") or []:
        for leaf in (outer if isinstance(outer, list) else [outer]):
            if isinstance(leaf, dict) and isinstance(leaf.get("text"), str):
                out.append(leaf["text"])
    return out


def load_composio(path: Path, agent: str, counter) -> Trajectory:
    """One composio_swekit trajectory file -> a normalized Trajectory.

    Sub-runs are concatenated in file order; each message carries the serving model that was
    in force for its sub-run, which is what makes Lane A measurable here.
    """
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, list):
        raise ValueError(f"{path}: expected a JSON list of sub-runs, got {type(doc).__name__}")
    messages: list[Msg] = []
    for sub in doc:
        found = models_in(sub)
        model = found[0] if found else None
        for node in (sub if isinstance(sub, list) else []):
            if not isinstance(node, dict):
                continue
            kw = node.get("kwargs")
            if isinstance(kw, dict):
                text = _lc_text(kw)
                role = _lc_role(kw, node)
                ctype = {"system": "system", "user": "user", "tool": "tool_output"}.get(role, "assistant")
                tokens = counter(text, ctype)
                tool_calls = kw.get("tool_calls") or []
                names = tuple(tc.get("name", "") for tc in tool_calls if isinstance(tc, dict))
                for tc in tool_calls:
                    if isinstance(tc, dict):
                        tokens += counter(json.dumps(tc.get("args", {}), separators=(",", ":")), "tool_args")
                messages.append(Msg(role=role, tokens=tokens, has_tool_calls=bool(tool_calls),
                                    tool_names=names, model=model))
                continue
            # LangChain LLMResult: {llm_output, run, generations}. The model's RESPONSE lives
            # here, not as an AI message node -- the second-stage model in this family is
            # recorded only this way, so skipping it makes a real switch invisible to Lane A.
            for text in _llmresult_texts(node):
                resp_model = (node.get("llm_output") or {}).get("model_name") or model
                messages.append(Msg(role="assistant", tokens=counter(text, "assistant"),
                                    model=resp_model))
    if not messages:
        raise ValueError(f"{path}: no LangChain message nodes found; wrong adapter for this shape")
    return Trajectory(suite="swe-bench", agent=agent, traj_id=f"{agent}/{path.stem}",
                      reward=None, messages=tuple(messages))
