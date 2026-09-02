"""Null controls for the entry-0010 overlap measure (`summarize_e7 --overlap-null`, entry 0024).

The observed overlap at a re-rendered handoff (0018: median 0.988 of the receiver's prompt is
words the sender already processed) is a bag-of-words multiset intersection of a ~8k-token
prompt against a ~17k-token context. A number that high needs to be told apart from what ANY
two texts of that shape would score. Two nulls, same measure, same quantile convention:

- SAME-FAMILY: each observed switch's receiver prompt against the sender context of a
  DIFFERENT composio trajectory -- a seeded derangement over the trajectory ids (no id maps to
  itself), fixed once by the registered seed; the partner switch is the one with the same
  ordinal in the partner trajectory, else its last. Composio shares system prompts and tool
  templates across trajectories, so this null isolates template vocabulary from task content.
- CROSS-FAMILY: the same receiver prompts against a seeded random SWE-bench role/content
  trajectory's full visible text (a different scaffold on a different task), drawn with
  replacement from the pool sorted by trajectory id.

Randomness only via `rng.make_rng(seed)` with the seed in `config/e7.toml [e7.overlap_null]`;
the derangement is drawn first, then the cross-family partners, so both are a pure function of
(seed, corpus). Each null reports the overlap fraction and the headroom upper bound as a
fraction of paid (= overlap x (1 - read_mult), the observed measure's own identity) with
median / p10 / p90 from `e7_stats`. A null that cannot be formed (fewer than two composio
trajectories with a switch; an empty role/content pool) is reported NOT COMPUTABLE -- never a
zero. No band, no verdict: this decides nothing (entry 0024 says so); it says what the observed
figure is a bound ON.
"""
from pathlib import Path

from linear_ceiling.config import E7Config
from linear_ceiling.e7_corpus import LANE_A_ONLY_AGENTS, Corpus, agent_of_submission
from linear_ceiling.e7_headroom import overlap_fraction, switch_slices
from linear_ceiling.e7_rolecontent import _messages_from_file, content_text
from linear_ceiling.e7_stats import summary
from linear_ceiling.e7_swe import discover_trajectories
from linear_ceiling.rng import make_rng

METHOD = ("same measure as entry 0010 (multiset whitespace-token overlap of the receiver prompt with a "
          "sender context); same-family = seeded derangement over composio trajectory ids, partner switch "
          "by ordinal (else last); cross-family = seeded draw with replacement from SWE-bench role/content "
          "trajectories' full visible text, pool sorted by id")


def derangement(n: int, rng) -> list[int]:
    """A permutation of range(n) with no fixed point, by rejection; refuses n < 2."""
    if n < 2:
        raise ValueError(f"a derangement needs at least 2 items, got {n}")
    while True:
        p = rng.permutation(n).tolist()
        if all(p[i] != i for i in range(n)):
            return p


def rolecontent_texts(traces_dir: Path) -> dict[str, str]:
    """Full visible text of every SWE-bench role/content trajectory (Lane-A-only agents
    excluded), keyed by `<submission>/<instance>`, messages joined by newline (0017)."""
    out: dict[str, str] = {}
    swe = Path(traces_dir) / "swe-bench"
    if not swe.is_dir():
        return out
    for sub in sorted(p for p in swe.iterdir() if p.is_dir()):
        if agent_of_submission(sub.name) in LANE_A_ONLY_AGENTS:
            continue
        for tid, files in discover_trajectories(sub):
            parts = []
            for fp in files:
                lst = _messages_from_file(fp)
                if lst is None:
                    continue
                parts.extend(content_text(m.get("content")) for m in lst if isinstance(m, dict) and "role" in m)
            if parts:
                out[f"{sub.name}/{tid}"] = "\n".join(parts)
    return out


def observed_switches(corpus: Corpus) -> dict[str, list[dict]]:
    """traj_id -> its switch slices (sender context, receiver prompt), for every trajectory
    with text; trajectories without a switch are omitted."""
    out = {}
    for t in corpus.trajectories:
        if t.traj_id not in corpus.texts:
            continue
        s = switch_slices(t, corpus.texts[t.traj_id])
        if s:
            out[t.traj_id] = s
    return out


def overlap_null(corpus: Corpus, cfg: E7Config, pool: dict[str, str] | None = None) -> dict:
    seed = (cfg.overlap_null or {}).get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("config/e7.toml [e7.overlap_null] must register an integer `seed` before the null "
                         "controls are computed (entry 0024)")
    read_mult = float(cfg.pricing["read_mult"])
    switches = observed_switches(corpus)
    ids = sorted(switches)
    n_sw = sum(len(v) for v in switches.values())
    if pool is None:
        pool = rolecontent_texts(cfg.traces_dir)
    pool_ids = sorted(pool)
    rng = make_rng(seed)
    obs = [s["overlap_fraction"] for tid in ids for s in switches[tid]]
    out = {"seed": seed, "read_mult": read_mult, "method": METHOD,
           "n_switches": n_sw, "n_trajectories_with_switch": len(ids),
           "observed": _block(obs, read_mult) if obs else None}
    # same-family: a derangement over trajectory ids, drawn FIRST
    if len(ids) >= 2:
        perm = derangement(len(ids), rng)
        vals, pairs = [], []
        for i, tid in enumerate(ids):
            partner = ids[perm[i]]
            ps = switches[partner]
            for j, s in enumerate(switches[tid]):
                null_sender = ps[min(j, len(ps) - 1)]["sender_text"]
                vals.append(overlap_fraction(null_sender, s["receiver_text"]))
            pairs.append([tid, partner])
        out["same_family"] = {**_block(vals, read_mult), "derangement": pairs}
    else:
        out["same_family"] = None
        out["same_family_not_computable"] = (f"{len(ids)} trajectory with a switch; a derangement needs 2 "
                                             "(NOT COMPUTABLE, not a zero)")
    # cross-family: one seeded partner per switch, with replacement, drawn SECOND
    if pool_ids and n_sw:
        vals, pairs = [], []
        for tid in ids:
            for j, s in enumerate(switches[tid]):
                partner = pool_ids[int(rng.integers(len(pool_ids)))]
                vals.append(overlap_fraction(pool[partner], s["receiver_text"]))
                pairs.append([tid, s["switch_index"], partner])
        out["cross_family"] = {**_block(vals, read_mult), "pool_size": len(pool_ids), "pairs": pairs}
    else:
        out["cross_family"] = None
        out["cross_family_not_computable"] = (f"pool of {len(pool_ids)} role/content trajectories and {n_sw} "
                                              "switches (NOT COMPUTABLE, not a zero)")
    return out


def _block(vals: list[float], read_mult: float) -> dict:
    return {"n": len(vals), "overlap_fraction": summary(vals),
            "recoverable_fraction": summary([v * (1.0 - read_mult) for v in vals])}


def _fmt(s: dict, pct: bool = False) -> str:
    if pct:
        return f"{100*s['median']:.1f}% (p10 {100*s['p10']:.1f}%, p90 {100*s['p90']:.1f}%)"
    return f"{s['median']:.3f} (p10 {s['p10']:.3f}, p90 {s['p90']:.3f})"


def render(nb: dict) -> str:
    rows = ["| control | n | overlap of the receiver prompt | headroom upper bound as a fraction of paid |",
            "|---|---|---|---|"]
    for name, key in (("observed (entry 0018 measure)", "observed"), ("same-family null (derangement)", "same_family"),
                      ("cross-family null (role/content)", "cross_family")):
        b = nb.get(key)
        if b is None:
            rows.append(f"| {name} | -- | NOT COMPUTABLE: {nb.get(key + '_not_computable', 'no switch measured')} | -- |")
        else:
            rows.append(f"| {name} | {b['n']} | {_fmt(b['overlap_fraction'])} | {_fmt(b['recoverable_fraction'], pct=True)} |")
    extra = ""
    if nb.get("cross_family"):
        extra = f"; cross-family pool {nb['cross_family']['pool_size']} trajectories"
    return ("Overlap null controls (entry 0024; `--overlap-null`, seed "
            f"{nb['seed']}, read_mult {nb['read_mult']}; {nb['n_switches']} observed switches over "
            f"{nb['n_trajectories_with_switch']} trajectories{extra}):\n\n" + "\n".join(rows)
            + f"\n\nmethod: {nb['method']}.\nNo band and no verdict: the nulls decide nothing; they say what the "
              "observed figure is a bound ON. Quantiles: e7_stats (median; lower nearest-rank p10/p90).")
