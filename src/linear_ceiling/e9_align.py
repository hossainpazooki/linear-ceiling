"""E9 alignment (entry 0017): handoff texts -> token ids -> matched position pairs. CPU only.

A handoff is one observed Lane A switch in the composio family: sender context `S` (every
message before the switch) and receiver prompt `R` (everything the receiving model was fed at
the switch) -- exactly the slices `e7_headroom.measure` scores, so the two measures describe
the same event. Both are tokenized with the pair's shared Qwen3 tokenizer, no special tokens.

Registered alignment: `difflib.SequenceMatcher(None, S_ids, R_ids, autojunk=False)`
`.get_matching_blocks()` -- the longest common contiguous block, then recursively left and
right. Deterministic; a common subsequence, in general shorter than the true LCS, so `|M|` is
a floor. Chosen over exact LCS because LCS is quadratic in 32k-token sequences.

Exclusions: a handoff whose `|S|` or `|R|` exceeds the context cap is EXCLUDED and counted,
never truncated (0017). Excluded handoffs still appear in the manifest with their sizes.
"""
import difflib
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from linear_ceiling.e7_swe import load_composio_detailed
from linear_ceiling.e7_traces import Trajectory


@dataclass(frozen=True)
class Handoff:
    handoff_id: str          # "<submission>/<instance>#<switch_index>"
    traj_id: str
    switch_index: int
    sender_model: str
    receiver_model: str
    sender_text: str
    receiver_text: str


def handoffs_from(traj: Trajectory, texts: list[str]) -> list[Handoff]:
    """The same event set and the same S/R slices as `e7_headroom.measure` after entry 0017:
    S = everything the sender processed up to its last response; R = the receiver's own request
    prompt (its request's messages preceding its response), NEVER the trajectory prefix.
    Messages joined by a newline (0017)."""
    if len(texts) != len(traj.messages):
        raise ValueError(f"texts ({len(texts)}) must align with messages ({len(traj.messages)})")
    out = []
    asst = [(i, m) for i, m in enumerate(traj.messages) if m.role == "assistant"]
    for k in range(1, len(asst)):
        (i_prev, prev), (i_cur, cur) = asst[k - 1], asst[k]
        if prev.model is None or cur.model is None or prev.model == cur.model:
            continue
        if cur.request is None:
            raise ValueError(f"{traj.traj_id}: switch at assistant turn {k} without a request boundary (0017)")
        prompt_idx = [j for j in range(i_cur) if traj.messages[j].request == cur.request]
        out.append(Handoff(handoff_id=f"{traj.traj_id}#{k}", traj_id=traj.traj_id, switch_index=k,
                           sender_model=prev.model, receiver_model=cur.model,
                           sender_text="\n".join(texts[:i_prev + 1]),
                           receiver_text="\n".join(texts[j] for j in prompt_idx)))
    return out


def load_handoffs(submission_dirs: list[Path], counter) -> list[Handoff]:
    out = []
    for sub in submission_dirs:
        for f in sorted(Path(sub).glob("*.json")):
            traj, texts = load_composio_detailed(f, Path(sub).name, counter)
            out.extend(handoffs_from(traj, texts))
    return out


def matching_pairs(a: list[int], b: list[int]) -> np.ndarray:
    """[[p_S, p_R], ...] over every token in the registered matching blocks, in order."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    pairs = []
    for i, j, n in sm.get_matching_blocks():
        for t in range(n):
            pairs.append((i + t, j + t))
    return np.asarray(pairs, dtype=np.int64).reshape(-1, 2)


@dataclass(frozen=True)
class Alignment:
    handoff_id: str
    n_sender: int
    n_receiver: int
    n_matched: int
    excluded: bool
    reason: str | None
    text_sha256: str          # sha256 over sender_text + "\x00" + receiver_text


def align(h: Handoff, encode, context_cap: int) -> tuple[Alignment, np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    """(alignment record, sender ids, receiver ids, pairs) -- ids/pairs are None when excluded."""
    s_ids, r_ids = encode(h.sender_text), encode(h.receiver_text)
    digest = hashlib.sha256((h.sender_text + "\x00" + h.receiver_text).encode("utf-8")).hexdigest()
    if not r_ids:
        # a switch whose request prompt is not visible in the trace (paid 0 in e7_headroom):
        # nothing to prefill, nothing to measure -- EXCLUDED and counted, never a zero R².
        rec = Alignment(h.handoff_id, len(s_ids), 0, 0, True, "receiver prompt is empty in the trace", digest)
        return rec, None, None, None
    too_long = [name for name, ids in (("S", s_ids), ("R", r_ids)) if len(ids) > context_cap]
    if too_long:
        rec = Alignment(h.handoff_id, len(s_ids), len(r_ids), 0, True,
                        f"{'/'.join(too_long)} exceeds context cap {context_cap}", digest)
        return rec, None, None, None
    pairs = matching_pairs(s_ids, r_ids)
    rec = Alignment(h.handoff_id, len(s_ids), len(r_ids), int(pairs.shape[0]), False, None, digest)
    return rec, np.asarray(s_ids, dtype=np.int64), np.asarray(r_ids, dtype=np.int64), pairs


def write_alignment(out_dir: Path, rec: Alignment, s_ids, r_ids, pairs) -> Path:
    """One .npz per handoff (ids + pairs) beside a .json record; the driver feeds the ids to
    the upstream dump as [1, L] token files."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = rec.handoff_id.replace("/", "__").replace("#", "_sw")
    p = out_dir / f"{stem}.npz"
    if rec.excluded:
        np.savez(p, sender=np.zeros(0, np.int64), receiver=np.zeros(0, np.int64), pairs=np.zeros((0, 2), np.int64))
    else:
        np.savez(p, sender=s_ids, receiver=r_ids, pairs=pairs)
    import json
    (out_dir / f"{stem}.json").write_text(json.dumps(asdict(rec), indent=1), encoding="utf-8")
    return p


def coverage_comparison(records: list, headroom_rows: list, summary_fn) -> dict:
    """Entry 0025 (review finding 1): included vs excluded handoffs compared on |S|, |R| (from the
    alignment records) and on entry 0018's per-handoff overlap and recoverable fractions (the
    verified E7 headroom rows, keyed `<traj_id>#<switch_index>` = the E9 handoff id). Says what the
    32,768 cap selects on; decides nothing. Excluded handoffs whose R is empty have no |R| and no
    0018 row worth reading, and are counted separately."""
    by_id = {f"{r['traj_id']}#{r['switch_index']}": r for r in headroom_rows}
    groups = {"included": [], "excluded_long": [], "excluded_empty_r": []}
    for rec in records:
        r = rec if isinstance(rec, dict) else asdict(rec)
        if not r["excluded"]:
            groups["included"].append(r)
        elif r["n_receiver"] == 0:
            groups["excluded_empty_r"].append(r)
        else:
            groups["excluded_long"].append(r)
    out = {"n": {k: len(v) for k, v in groups.items()}, "unmatched_0018_rows": 0}
    for name in ("included", "excluded_long"):
        rows = groups[name]
        if not rows:
            out[name] = None
            continue
        ov = [by_id[r["handoff_id"]]["overlap_fraction"] for r in rows if r["handoff_id"] in by_id]
        rf = [by_id[r["handoff_id"]]["recoverable_fraction"] for r in rows if r["handoff_id"] in by_id]
        out["unmatched_0018_rows"] += len(rows) - len(ov)
        out[name] = {"n_sender": summary_fn([r["n_sender"] for r in rows]),
                     "n_receiver": summary_fn([r["n_receiver"] for r in rows]),
                     "overlap_fraction_0018": summary_fn(ov) if ov else None,
                     "recoverable_fraction_0018": summary_fn(rf) if rf else None}
    return out
