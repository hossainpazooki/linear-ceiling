"""E8 arm (b): agent-trace text, sampled and tokenized by the rule frozen in ledger entry 0016.

Rendering, per trajectory (0016 §4): the visible messages in trace order, each prefixed by its
role tag on its own line, tool calls rendered as `name(arguments)`:

    [system]
    <content>
    [assistant]
    <content>
    lookup({"q":"x"})

Sampling: one window per trajectory -- the FIRST `seq_len` tokens; trajectories shorter than
`seq_len` tokens are skipped, never padded. `n_seqs` windows drawn with the repo's single seeded
generator from the configured suites, stratified equally, from the eligible trajectories of
each suite sorted by traj_id (so the draw is a pure function of seed + corpus). tau-bench v1 is
excluded by config (below the agent floor, entry 0011).

Tokenizer: the pair's shared Qwen3 tokenizer, read from the snapshot's `tokenizer.json` after
`weights.assert_shared_vocab` has passed. The token file has the upstream's `[n_seqs, seq_len]`
int64 layout so `scripts/dump_kv.py --tokens` consumes it unchanged.
"""
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from linear_ceiling.config import E7Config, E8Config
from linear_ceiling.e7_rolecontent import _messages_from_file, content_text
from linear_ceiling.e7_swe import discover_trajectories, load_composio_detailed
from linear_ceiling.e7_tau2 import read_tau2
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.rng import make_rng

ROLE_TAGS = {"system": "[system]", "user": "[user]", "assistant": "[assistant]", "tool": "[tool]"}


@dataclass(frozen=True)
class TraceText:
    suite: str
    traj_id: str
    text: str


def render_messages(messages: list[dict]) -> str:
    """Role-tagged rendering of OpenAI-style message dicts (0016 §4)."""
    parts = []
    for m in messages:
        if not isinstance(m, dict) or "role" not in m:
            continue
        role = str(m.get("role") or "assistant")
        lines = [ROLE_TAGS.get(role, f"[{role}]")]
        body = content_text(m.get("content"))
        if body:
            lines.append(body)
        for tc in (m.get("tool_calls") or []) if isinstance(m.get("tool_calls"), list) else []:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function") if isinstance(tc.get("function"), dict) else tc
            args = fn.get("arguments", fn.get("args", ""))
            if isinstance(args, dict):
                args = json.dumps(args, separators=(",", ":"), ensure_ascii=False)
            lines.append(f"{fn.get('name') or ''}({args or ''})")
        parts.append("\n".join(lines))
    return "\n".join(parts)


def iter_trace_texts(e7: E7Config, suites: tuple[str, ...]):
    """Yield TraceText for every trajectory of the requested suites, in a deterministic order."""
    if "tau2-bench" in suites:
        for f in sorted(e7.traces_dir.glob("tau2-bench/*.json")):
            doc = read_tau2(f)
            agent = (doc.get("info") or {}).get("agent_info", {}).get("llm")
            for sim in doc["simulations"]:
                msgs = sim.get("messages") or []
                if msgs:
                    yield TraceText("tau2-bench", f"{agent}/{sim.get('task_id')}/{sim.get('trial')}",
                                    render_messages(msgs))
    if "swe-bench" in suites:
        swe = e7.traces_dir / "swe-bench"
        if swe.is_dir():
            for sub in sorted(p for p in swe.iterdir() if p.is_dir()):
                for tid, files in discover_trajectories(sub):
                    msgs = []
                    for fp in files:
                        lst = _messages_from_file(fp)
                        if lst is not None:
                            msgs.extend(lst)
                    if msgs:
                        yield TraceText("swe-bench", f"{sub.name}/{tid}", render_messages(msgs))
                        continue
                    if len(files) == 1 and files[0].suffix == ".json":
                        try:
                            traj, texts = load_composio_detailed(files[0], sub.name, lambda t, ct="assistant": 0)
                        except (ValueError, json.JSONDecodeError):
                            continue
                        text = "\n".join(f"{ROLE_TAGS.get(m.role, '[' + m.role + ']')}\n{t}"
                                         for m, t in zip(traj.messages, texts))
                        yield TraceText("swe-bench", f"{sub.name}/{tid}", text)


def sample_windows(items: list[TraceText], encode, cfg: E8Config) -> tuple[np.ndarray, list[dict]]:
    """Eligible = at least seq_len tokens. Equal draw per suite with make_rng(seed); returns
    the [n_seqs, seq_len] token matrix and a manifest of what was drawn."""
    t = cfg.text
    suites = tuple(t["suites"])
    n, L = int(t["n_seqs"]), int(t["seq_len"])
    if n % len(suites):
        raise ValueError(f"n_seqs={n} does not stratify equally over {len(suites)} suites")
    per = n // len(suites)
    eligible: dict[str, list[tuple[str, list[int]]]] = {s: [] for s in suites}
    for it in sorted(items, key=lambda x: (x.suite, x.traj_id)):
        if it.suite not in eligible:
            continue
        ids = encode(it.text)
        if len(ids) >= L:
            eligible[it.suite].append((it.traj_id, ids[:L]))
    rng = make_rng(int(t["seed"]))
    rows, manifest = [], []
    for s in suites:
        pool = eligible[s]
        if len(pool) < per:
            raise ValueError(f"suite {s}: only {len(pool)} trajectories have >= {L} tokens; need {per}")
        picks = sorted(rng.choice(len(pool), size=per, replace=False).tolist())
        for i in picks:
            tid, ids = pool[i]
            rows.append(ids)
            manifest.append({"suite": s, "traj_id": tid})
    return np.asarray(rows, dtype=np.int64), manifest


def qwen_encoder(snapshot_dir: Path):
    """Token-id encoder from a snapshot's tokenizer.json (no special tokens added)."""
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(Path(snapshot_dir) / "tokenizer.json"))
    return lambda text: tok.encode(text, add_special_tokens=False).ids


def write_tokens(cfg: E8Config, tokens: np.ndarray, manifest: list[dict]) -> Path:
    t = cfg.text
    cfg.tokens_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.tokens_dir / f"agent_n{t['n_seqs']}_len{t['seq_len']}_seed{t['seed']}.npy"
    np.save(out, tokens)
    (out.with_suffix(".manifest.json")).write_text(json.dumps(
        {"rule": "ledger entry 0016 section 4", "shape": list(tokens.shape),
         "sha256": sha256_file_bytes(out), "rows": manifest}, indent=1), encoding="utf-8")
    return out
