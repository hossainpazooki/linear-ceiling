# Stratified item draw by seam bin (ruling (v) of the 2026-10-21 seed, OPEN): built, tested and NOT wired.
# Nothing in pilot.py or cell.py imports this module; both are pinned by the staged 0063 draft. If (v) is
# ruled stratified, the wiring is a `draw` key read by `pilot.drawn_items`, a re-extraction of both items
# files with `attach_seam_bins`, and an edit of the draft, all before its staging commit.
import numpy as np

from linear_ceiling.e9_pertoken import SEAM_BIN_LABELS, seam_bin, seam_distance
from linear_ceiling.rng import make_rng


def attach_seam_bins(items, pairs, n_receiver):
    """Add `seam_bin` (index into SEAM_BIN_LABELS) to every located item from the alignment alone: the
    bin of the item's first answer token, a matched receiver position. Items that are not valid keep None."""
    pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
    bins = seam_bin(seam_distance(pairs, n_receiver))
    by_position = dict(zip(pairs[:, 1].tolist(), bins.tolist()))
    out = []
    for item in items:
        row = dict(item)
        row["seam_bin"] = by_position.get(item["first_token"]) if item.get("valid") else None
        if row["valid"] and row["seam_bin"] is None:
            raise ValueError("a valid item's first answer token is not a matched position")
        out.append(row)
    return out


def stratified_draw(items, cap, seed):
    """At most `cap` items, allocated across seam bins in proportion to each bin's count (largest
    remainders break ties), drawn within each bin by the seeded stream; every bin with at least one item
    keeps at least one when the cap allows. Under the cap, every item is returned in first-token order."""
    items = sorted(items, key=lambda it: it["first_token"])
    if len(items) <= cap:
        return items
    groups = {}
    for it in items:
        groups.setdefault(it["seam_bin"], []).append(it)
    labels = sorted(groups)
    counts = np.array([len(groups[b]) for b in labels], dtype=np.float64)
    share = counts / counts.sum() * cap
    take = np.floor(share).astype(int)
    take = np.maximum(take, 1) if cap >= len(labels) else take
    remainder = cap - int(take.sum())
    if remainder > 0:
        for i in np.argsort(-(share - np.floor(share)), kind="stable")[:remainder]:
            take[i] += 1
    elif remainder < 0:
        for i in np.argsort(share - np.floor(share), kind="stable")[:-remainder]:
            take[i] -= 1
    rng = make_rng(seed)
    chosen = []
    for label, n in zip(labels, take.tolist()):
        n = min(n, len(groups[label]))
        picked = sorted(rng.choice(len(groups[label]), size=n, replace=False).tolist())
        chosen += [groups[label][i] for i in picked]
    return sorted(chosen, key=lambda it: it["first_token"])


def bin_counts(items):
    return {SEAM_BIN_LABELS[b]: sum(1 for it in items if it.get("seam_bin") == b) for b in range(len(SEAM_BIN_LABELS))}
