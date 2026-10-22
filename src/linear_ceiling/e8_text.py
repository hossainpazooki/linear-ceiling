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

MLPerf Agentic Inference (the 2026-10-22 plan, cell 1a; config/e8m.toml, config/e8mf.toml): one flat
JSONL under `traces/mlperf-agentic/` (gitignored), one row per message, grouped by `conversation_id`
and ordered by `turn`; its first row is a `_type = "dataset_metadata"` record with no conversation
and is skipped. Two suites out of the one file, split by the row field `_source`: present on every
Workato workflow row (`mlperf-workflow`), absent on the DeepSWE coding rows (`mlperf-coding`).
Rendering is `render_mlperf_rows`: the role tags above, with `reasoning_content` KEPT ahead of the
content (the benchmark's own template keeps it, so the text a serving engine caches includes it),
`tool_calls` as name(arguments) and the contents of `tool_results`. The shared system prompt and
tool schema that each conversation's first row carries in `system` / `tools` are NOT rendered: all
500 workflow conversations share one ~30K-token prefix, and under the FIRST-window rule it would
make every drawn workflow window the same tokens. The same sampling rule then applies unchanged.
Exported with `python -m linear_ceiling.e8_text --suites ... --out <jsonl>` for the lag-ladder
builder that re-tokenizes the rendered trajectories under its instrument's tokenizer.
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
MLPERF_SUITES = ("mlperf-coding", "mlperf-workflow")
MLPERF_DIR = "mlperf-agentic"           # under traces/; every *.jsonl there is read
MLPERF_SOURCE_FIELD = "_source"         # on the Workato (workflow) rows only; the coding rows carry no such field


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
            line = _tool_call_line(tc)
            if line is not None:
                lines.append(line)
        parts.append("\n".join(lines))
    return "\n".join(parts)


def _tool_call_line(tc) -> str | None:
    """`name(arguments)` for one tool call (0016 §4); None for a malformed entry."""
    if not isinstance(tc, dict):
        return None
    fn = tc.get("function") if isinstance(tc.get("function"), dict) else tc
    args = fn.get("arguments", fn.get("args", ""))
    if isinstance(args, dict):
        args = json.dumps(args, separators=(",", ":"), ensure_ascii=False)
    return f"{fn.get('name') or ''}({args or ''})"


def render_mlperf_rows(rows: list[dict]) -> str:
    """Role-tagged rendering of one MLPerf Agentic Inference conversation (one row per message, in turn
    order): reasoning_content kept, tool calls as name(arguments), tool results' contents; the first row's
    shared `system` / `tools` prefix is not rendered (module docstring)."""
    parts = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        role = str(r.get("role") or "assistant")
        lines = [ROLE_TAGS.get(role, f"[{role}]")]
        reasoning = r.get("reasoning_content")
        if isinstance(reasoning, str) and reasoning:
            lines.append(reasoning)
        body = content_text(r.get("content"))
        if body:
            lines.append(body)
        for tc in (r.get("tool_calls") or []) if isinstance(r.get("tool_calls"), list) else []:
            line = _tool_call_line(tc)
            if line is not None:
                lines.append(line)
        for tr in (r.get("tool_results") or []) if isinstance(r.get("tool_results"), list) else []:
            c = tr.get("content") if isinstance(tr, dict) else tr
            body = content_text(c) if isinstance(c, (str, list)) else (
                json.dumps(c, ensure_ascii=False) if c is not None else "")
            if body:
                lines.append(body)
        parts.append("\n".join(lines))
    return "\n".join(parts)


def mlperf_suite(rows: list[dict]) -> str:
    """mlperf-workflow when any row carries `_source` (the Workato rows do); otherwise mlperf-coding."""
    return "mlperf-workflow" if any(isinstance(r, dict) and MLPERF_SOURCE_FIELD in r for r in rows) else "mlperf-coding"


def iter_mlperf_texts(traces_dir: Path, suites: tuple[str, ...]):
    """TraceText per conversation of the requested MLPerf suites, traj_id = conversation_id, sorted."""
    wanted = tuple(s for s in suites if s in MLPERF_SUITES)
    if not wanted:
        return
    convs: dict[str, list[dict]] = {}
    for f in sorted((Path(traces_dir) / MLPERF_DIR).glob("*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if not isinstance(r, dict) or r.get("_type") == "dataset_metadata" or "conversation_id" not in r:
                    continue
                convs.setdefault(str(r["conversation_id"]), []).append(r)
    for cid in sorted(convs):
        rows = sorted(convs[cid], key=lambda r: int(r["turn"]))
        suite = mlperf_suite(rows)
        if suite in wanted:
            yield TraceText(suite, cid, render_mlperf_rows(rows))


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
    yield from iter_mlperf_texts(e7.traces_dir, suites)


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


def export_rendered(traces_dir: Path, suites: tuple[str, ...], out: Path) -> tuple[Path, dict[str, int]]:
    """The rendered trajectories as JSONL, one {suite, traj_id, text} per line sorted by (suite, traj_id),
    for a sibling builder under another tokenizer (lag-ladder tools/agentic_tokens.py). Returns the path and
    the per-suite counts."""
    from collections import Counter
    from linear_ceiling.config import E7Config
    e7 = E7Config(traces_dir=Path(traces_dir), results_dir=Path(traces_dir), pricing={}, thresholds={},
                  tokenizer={}, lane_b_policy="", config_path=Path(traces_dir))
    items = sorted(iter_trace_texts(e7, tuple(suites)), key=lambda t: (t.suite, t.traj_id))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for t in items:
            fh.write(json.dumps({"suite": t.suite, "traj_id": t.traj_id, "text": t.text}, ensure_ascii=False) + "\n")
    return out, dict(Counter(t.suite for t in items))


def main(argv=None) -> int:
    import argparse
    from linear_ceiling import REPO_ROOT
    from linear_ceiling.config import load_e7_config
    ap = argparse.ArgumentParser(description="export the rendered agent trajectories (0016 s4 rendering) as JSONL")
    ap.add_argument("--e7-config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--traces-dir", default=None, help="override the e7 config's traces_dir")
    ap.add_argument("--suites", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    traces = Path(a.traces_dir) if a.traces_dir else load_e7_config(Path(a.e7_config), REPO_ROOT).traces_dir
    out, counts = export_rendered(traces, tuple(a.suites), Path(a.out))
    print(f"{sha256_file_bytes(out)}  {out.as_posix()}  " + " ".join(f"{s}={n}" for s, n in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
