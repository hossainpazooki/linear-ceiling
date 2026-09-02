"""Headroom at an observed cross-model handoff — the measure frozen in ledger entry 0010.

At a Lane A switch, the receiving model is fed context the sending model already processed. If
the handoff were byte-identical, the overlapping prefix could in principle be transferred
instead of re-prefilled. In the one public family that actually switches (composio_swekit), it
is NOT byte-identical: the second stage re-renders the first stage's conversation into a new
prompt. So the overlap bounds what any transfer could recover, and cannot be achieved:

    paid                  = prefill tokens the receiving model was charged for
    overlap               = the part of that prompt whose CONTENT the sender already processed
    headroom_upper_bound  = overlap * (1 - read_mult)
    residual              = paid - overlap        (genuinely new framing/instruction text)

`headroom_upper_bound` is an UPPER BOUND, never an achievable saving (entry 0010): re-rendering
changes the token sequence and every position, so transferred KV would not be directly reusable
even where content matches. Every figure this module returns carries that word.

Overlap is measured by CONTENT, not by bytes, because the handoff is a re-serialization. The
registered method (named here so the number is reproducible): split both sides into whitespace
tokens, take the multiset intersection via counts, and express it as a fraction of the
receiving prompt's tokens. Multiset intersection -- not set intersection -- so a phrase repeated
twice on the receiving side is only credited twice if the sender also produced it twice.

Per entry 0012, every figure here is a LOWER BOUND on real spend: public traces omit the system
prompt and tool schemas the provider billed.
"""
import re
from collections import Counter
from dataclasses import asdict, dataclass

from linear_ceiling.e7_stats import summary
from linear_ceiling.e7_traces import Trajectory

METHOD = ("multiset whitespace-token overlap of the receiving prompt with everything the sender "
          "processed; headroom_upper_bound = overlap_tokens x (1 - read_mult)")

_WORD = re.compile(r"\S+")


def word_multiset(text: str) -> Counter:
    return Counter(_WORD.findall(text or ""))


def overlap_fraction(sender_text: str, receiver_text: str) -> float:
    """Fraction of the receiver's words that the sender had already produced (multiset)."""
    recv = word_multiset(receiver_text)
    total = sum(recv.values())
    if total == 0:
        return 0.0
    send = word_multiset(sender_text)
    shared = sum(min(n, send[w]) for w, n in recv.items())
    return shared / total


@dataclass(frozen=True)
class Headroom:
    switch_index: int          # assistant-turn ordinal of the switch
    sender_model: str
    receiver_model: str
    paid_tokens: int           # receiving model's prefill, from the visible trace (a floor)
    overlap_fraction: float
    overlap_tokens: float
    residual_tokens: float
    headroom_upper_bound: float   # in base-input-price units; UPPER BOUND (entry 0010)
    byte_identical: bool          # was the handoff a verbatim prefix reuse?

    @property
    def recoverable_fraction(self) -> float:
        return self.headroom_upper_bound / self.paid_tokens if self.paid_tokens else 0.0


def switch_slices(traj: Trajectory, texts: list[str]) -> list[dict]:
    """The two texts the measure compares at each Lane A switch, exactly as `measure` slices
    them (shared with the null controls of entry 0024 so the nulls cannot drift from the
    observed measure): sender context = every message before the switch; receiver prompt = the
    messages of the receiver's own request before its response (0017), newline-joined."""
    if len(texts) != len(traj.messages):
        raise ValueError(f"texts ({len(texts)}) must align with messages ({len(traj.messages)})")
    out = []
    asst = [(i, m) for i, m in enumerate(traj.messages) if m.role == "assistant"]
    for k in range(1, len(asst)):
        (i_prev, prev), (i_cur, cur) = asst[k - 1], asst[k]
        if prev.model is None or cur.model is None or prev.model == cur.model:
            continue
        if cur.request is None:
            raise ValueError(f"{traj.traj_id}: switch at assistant turn {k} but the trace records no request "
                             "boundary; the receiver's prefill is unknown and must not be approximated by the "
                             "trajectory prefix (entry 0017)")
        # Messages are joined by a newline so boundary words are not fused (0017).
        sender_text = "\n".join(texts[:i_prev + 1])
        # The receiving model's prompt is ITS request's prompt: the messages of the same request
        # that precede its response -- not the trajectory's cumulative prefix (0017 correction).
        prompt_idx = [j for j in range(i_cur) if traj.messages[j].request == cur.request]
        receiver_text = "\n".join(texts[j] for j in prompt_idx)
        out.append({"switch_index": k, "sender_model": prev.model, "receiver_model": cur.model,
                    "sender_text": sender_text, "receiver_text": receiver_text,
                    "paid_tokens": sum(traj.messages[j].tokens for j in prompt_idx),
                    "overlap_fraction": overlap_fraction(sender_text, receiver_text)})
    return out


def measure(traj: Trajectory, texts: list[str], read_mult: float) -> list[Headroom]:
    """Headroom at each Lane A switch in `traj`.

    `texts` is the per-message text, index-aligned with `traj.messages`, because Msg carries
    token counts rather than content. Sender context is every message before the switch;
    receiver prompt is the message at the switch.
    """
    out = []
    for s in switch_slices(traj, texts):
        paid, frac = s["paid_tokens"], s["overlap_fraction"]
        overlap_tokens = frac * paid
        out.append(Headroom(
            switch_index=s["switch_index"],
            sender_model=s["sender_model"], receiver_model=s["receiver_model"],
            paid_tokens=paid,
            overlap_fraction=frac,
            overlap_tokens=overlap_tokens,
            residual_tokens=paid - overlap_tokens,
            headroom_upper_bound=overlap_tokens * (1.0 - read_mult),
            byte_identical=bool(s["sender_text"]) and s["sender_text"] in s["receiver_text"],
        ))
    return out


def rows(trajectories: list[Trajectory], texts: dict[str, list[str]], read_mult: float) -> list[dict]:
    """One row per observed Lane A switch across every trajectory whose text is available.

    A trajectory with a switch but no text (an adapter that returns token counts only) cannot
    be measured here and is NOT a zero: `rows` skips it, and the caller's Lane A count is what
    says how many switches exist. Keyed by traj_id so the summarizer can compare row-for-row.
    """
    out = []
    for t in trajectories:
        if t.traj_id not in texts:
            continue
        for h in measure(t, texts[t.traj_id], read_mult):
            out.append({"traj_id": t.traj_id, **asdict(h),
                        "recoverable_fraction": h.recoverable_fraction})
    return out


def rows_summary(rs: list[dict]) -> dict | None:
    """Aggregate over switch rows; None when there is nothing to aggregate (never a zero)."""
    if not rs:
        return None
    return {"switches": len(rs),
            "submissions": sorted({r["traj_id"].split("/", 1)[0] for r in rs}),
            "byte_identical": sum(1 for r in rs if r["byte_identical"]),
            "overlap_fraction": summary([r["overlap_fraction"] for r in rs]),
            "paid_tokens": summary([r["paid_tokens"] for r in rs]),
            "recoverable_fraction": summary([r["recoverable_fraction"] for r in rs]),
            "method": METHOD,
            "label": "UPPER BOUND, never an achievable saving: re-rendering changes the token "
                     "sequence and positions (entry 0010); paid tokens are a visible-only LOWER "
                     "BOUND (entry 0012)"}
