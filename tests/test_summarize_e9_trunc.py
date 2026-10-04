"""E-TRUNC (summarize_e9_trunc): the levels as one instrument, the common subset M_cap in the FULL frame,
the shrinkage pre-check, the void gate, the three outcomes of the registered reading, and the pins -- on
synthetic records shaped like tests/test_e9_scaled_short.py's."""
import json

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import _stem
from linear_ceiling.e9_pertoken import seam_bin, seam_distance_left
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.summarize_e9 import _tau_key
from linear_ceiling.summarize_e9_trunc import (FULL, common_subset, compare_levels, load_levels, reading, render,
                                               render_shrinkage, shrinkage, to_full_frame)
from tests.test_e9_scaled_short import H as HEADS, L as LAYERS

H1, H2, H3 = "20241016_composio_x/a_traj#1", "20241016_composio_x/b_traj#2", "20241016_composio_x/c_traj#3"
LEVELS = {"full": None, "l65": 600, "l49": 450, "l32": 300}      # synthetic "L" values; |S| runs 400-900 below


# ---- the committed configs ---------------------------------------------------------------------------------------

def test_the_four_committed_configs_are_e9l_byte_for_byte_except_the_named_lines():
    e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
    full = load_e9_config(REPO_ROOT / "config" / "e9t-full.toml", REPO_ROOT)
    levels = load_levels(full)
    assert list(levels) == [FULL, "L65536", "L49152", "L32768"]
    assert full.trunc["margin_abs"] == 0.005 and full.trunc["min_common_matched"] == 2000 and full.trunc["seam_far_bin"] == "16+"
    assert full.trunc["out_dir"] == "results/e9t" and full.trunc["bootstrap_seed"] == 52 and full.trunc["bootstrap_reps"] == 2000
    for name, c in levels.items():
        assert c.rule == e9l.rule and c.controls == e9l.controls and c.rope == e9l.rope and c.bridge == e9l.bridge
        assert c.profiles == e9l.profiles and c.context_cap == 81920 and c.context_floor == 32768
        assert c.keep_seed == e9l.keep_seed and c.keep_n == e9l.keep_n and c.mapper_k == e9l.mapper_k
        assert c.upstream_sha == e9l.upstream_sha and c.pair == e9l.pair and c.alignment_method == e9l.alignment_method
        assert c.required_entries == e9l.required_entries + ("0055",) and c.order_by == "n_sender_desc" and c.allow_partial
    assert [c.sender_head_truncate for c in levels.values()] == [None, 65536, 49152, 32768]
    assert sorted(c.results_dir.name for c in levels.values()) == ["e9t-full", "e9t-l32", "e9t-l49", "e9t-l65"]
    # the FULL cell's text differs from e9l.toml only on the named lines (plus its header and the [e9.trunc] block)
    body = lambda p: [ln for ln in (REPO_ROOT / "config" / p).read_text(encoding="utf-8").splitlines()    # noqa: E731
                      if not ln.startswith("#")]
    a, b = body("e9l.toml"), body("e9t-full.toml")
    b = b[:next(i for i, ln in enumerate(b) if ln.startswith("[e9.trunc]"))]
    while a and not a[-1].strip():
        a.pop()
    while b and not b[-1].strip():
        b.pop()
    changed = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(a) == len(b) and len(changed) == 4, changed
    assert all(k in "".join(x for x, _ in changed) for k in ("results_dir", "scratch_dir", "required_entries", "by = "))


@pytest.mark.parametrize("old,new,msg", [
    ("margin_abs = 0.005", "margin_abs = 1.5", "margin_abs"),
    ("min_common_matched = 2000", "min_common_matched = 0", "min_common_matched"),
    ('levels = ["config/e9t-l65.toml", "config/e9t-l49.toml", "config/e9t-l32.toml"]', "levels = []", "levels"),
    ("bootstrap_reps = 2000", "bootstrap_reps = 5", "bootstrap"),
    ("\n[e9.trunc]", "\n[e9.trunc]\nsurprise = 1", "exactly"),
])
def test_full_config_refuses_a_malformed_trunc_section(tmp_path, old, new, msg):
    src = (REPO_ROOT / "config" / "e9t-full.toml").read_text(encoding="utf-8")
    assert old in src
    p = tmp_path / "e9t-full.toml"
    p.write_text(src.replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, tmp_path)


def test_a_truncated_level_may_not_carry_the_trunc_section(tmp_path):
    src = (REPO_ROOT / "config" / "e9t-full.toml").read_text(encoding="utf-8")
    p = tmp_path / "e9t-full.toml"
    p.write_text(src.replace("[e9.alignment]", "[e9.alignment]\nsender_head_truncate = 32768"), encoding="utf-8")
    with pytest.raises(ValueError, match="belongs to the FULL cell"):
        load_e9_config(p, tmp_path)


# ---- the common subset ------------------------------------------------------------------------------------------

def test_full_frame_and_common_subset_undo_each_levels_offset():
    full = np.array([[10, 0], [11, 1], [50, 2], [51, 3], [90, 4]])
    n_sender = 100
    # level L=60 sees S[-60:], so FULL positions >= 40 survive at p' = p - 40; the aligner also drops (90, 4)
    l60 = np.array([[10, 2], [11, 3]])
    assert to_full_frame(l60, n_sender, 60).tolist() == [[50, 2], [51, 3]]
    assert to_full_frame(full, n_sender, None).tolist() == full.tolist()
    m, rows = common_subset({FULL: full, "L60": l60}, n_sender, {FULL: None, "L60": 60})
    assert m.tolist() == [[50, 2], [51, 3]]
    assert rows[FULL].tolist() == [2, 3] and rows["L60"].tolist() == [0, 1]
    with pytest.raises(ValueError, match="duplicate"):
        common_subset({FULL: np.array([[1, 1], [1, 1]])}, 10, {FULL: None})


# ---- synthetic cells ---------------------------------------------------------------------------------------------

def _cfg(tmp_path, cell, L):
    src = (REPO_ROOT / "config" / "e9t-full.toml").read_text(encoding="utf-8")
    src = src[:src.index("\n[e9.trunc]")] + "\n" if L is not None else src    # the header COMMENT names the section too
    src = src.replace('results_dir = "results/e9t-full"', f'results_dir = "results/{cell}"').replace(
        'scratch_dir = "results/e9t-full/scratch"', f'scratch_dir = "results/{cell}/scratch"')
    if L is not None:
        src = src.replace("[e9.alignment]", f"[e9.alignment]\nsender_head_truncate = {L}")
    else:
        src = src.replace('levels = ["config/e9t-l65.toml", "config/e9t-l49.toml", "config/e9t-l32.toml"]',
                          'levels = ["l65.toml", "l49.toml", "l32.toml"]')
        src = src.replace('short_scaled_compare = "results/e9s/compare.json"', 'short_scaled_compare = "refs/compare.json"')
        src = src.replace('long_summary = "results/e9l/summary.json"', 'long_summary = "refs/summary.json"')
        src = src.replace("min_common_matched = 2000", "min_common_matched = 50")
    p = tmp_path / f"{cell}.toml"
    p.write_text(src, encoding="utf-8")
    return load_e9_config(p, tmp_path)


def _refs(tmp_path, short, long_):
    d = tmp_path / "refs"
    d.mkdir(exist_ok=True)
    (d / "compare.json").write_text(json.dumps({"n_handoffs": 25, "seam_profile_left_pooled": [
        {"bin": "16+", "n_tokens": 10, "median_native": 0.02, "median_scaled": short}]}), encoding="utf-8")
    (d / "summary.json").write_text(json.dumps({"coverage": {"included": 35, "scored": 35}, "seam_profile_left_pooled": {
        "same_K": [{"bin": "16+", "n_tokens": 10, "median": long_}]}}), encoding="utf-8")


def _block_pairs(ps0, pr0, n):
    """One contiguous matched block (p_S, p_R) = (ps0 + i, pr0 + i): the receiver re-renders a run of the sender
    verbatim, so the tokens sit far from any seam and the 16+ bin the reading reads is populated. Random pairs
    would put every token in seam bin 0 and leave the registered reading nothing to read."""
    i = np.arange(n, dtype=np.int64)
    return np.stack([ps0 + i, pr0 + i], 1)


def _level_pairs(full_pairs, n_sender, L, drop_every=0):
    """What the aligner would see under S[-L:]: the FULL pairs whose sender position survives, shifted --
    optionally dropping every k-th survivor to imitate re-matching instability."""
    off = max(0, n_sender - L)
    keep = full_pairs[full_pairs[:, 0] >= off]
    if drop_every:
        keep = keep[np.arange(len(keep)) % drop_every != 0]
    out = keep.copy()
    out[:, 0] -= off
    return out


def _write_level(cfg, L, handoffs, *, complete=True, delta=None, partial=False):
    """handoffs: hid -> (full_pairs, n_sender, n_receiver, drop_every). Writes align/, coverage.json and, when
    `delta` is given (hid -> FULL-frame delta per FULL pair), the scores/tokens/report of a complete run."""
    rd = cfg.results_dir
    for d in ("align", "scores", "tokens"):
        (rd / d).mkdir(parents=True, exist_ok=True)
    recs, scores = [], {}
    for hid, (fp, n_s, n_r, drop) in handoffs.items():
        pr = fp if L is None else _level_pairs(fp, n_s, L, drop)
        np.savez(rd / "align" / f"{_stem(hid)}.npz", sender=np.arange(min(n_s, L or n_s)), receiver=np.arange(n_r), pairs=pr)
        recs.append({"handoff_id": hid, "n_sender": n_s, "n_receiver": n_r, "n_matched": int(len(pr)),
                     "excluded": False, "reason": None, "text_sha256": f"text-{hid}"})
        if delta is not None:
            off = 0 if L is None else max(0, n_s - L)
            full_keys = {(int(a), int(b)): i for i, (a, b) in enumerate(fp.tolist())}
            target = np.asarray([delta[hid][full_keys[(int(a) + off, int(b))]] for a, b in pr.tolist()], dtype=np.float64)
            n = len(target)
            sq = np.repeat(np.repeat(target[:, None, None], LAYERS, 1), HEADS, 2).astype(np.float32)
            tf, sf = f"{_stem(hid)}.tokens.npz", f"{_stem(hid)}.json"
            np.savez(rd / "tokens" / tf, same_K=sq, same_V=sq, ref_K=sq, ref_V=sq, cross_K=sq, cross_V=sq)
            body = {"n_pairs": n, "same": {k: [{"sst": [float(n)] * HEADS} for _ in range(LAYERS)] for k in "KV"},
                    "cross": {k: [{"sst": [float(n)] * HEADS} for _ in range(LAYERS)] for k in "KV"}}
            (rd / "scores" / sf).write_text(json.dumps(body), encoding="utf-8")
            scores[hid] = {"score_file": sf, "score_sha256": sha256_file_bytes(rd / "scores" / sf),
                           "tokens_file": tf, "tokens_sha256": sha256_file_bytes(rd / "tokens" / tf)}
    cov = {"config_sha256": sha256_text_file(cfg.config_path), "alignments": recs, "coverage": {"included": len(recs)}}
    if L is not None:
        cov["sender_head_truncate"] = L
    (rd / "align" / "coverage.json").write_text(json.dumps(cov), encoding="utf-8")
    if delta is not None:
        rep = {"complete": complete, "config_sha256": sha256_text_file(cfg.config_path), "upstream_sha": "a" * 40,
               "scores": scores, "alignments": recs, "partial": {"n_scored": len(scores)} if partial else None}
        (rd / "report.json").write_text(json.dumps(rep), encoding="utf-8")


@pytest.fixture
def cells(tmp_path):
    cfgs = {cell: _cfg(tmp_path, cell, L) for cell, L in LEVELS.items()}
    # three handoffs: H1 |S| 900, one block at p_S 500..899 (L300 keeps the 300 at p_S >= 600); H2 |S| 500, block
    # at 200..349 (L600 identical to FULL, L450/L300 shift it; L300 also drops every 7th survivor: instability);
    # H3 |S| 350 with its block at 0..29, so L300 keeps nothing -> void
    h1, h2, h3 = _block_pairs(500, 0, 400), _block_pairs(200, 100, 150), _block_pairs(0, 0, 30)
    handoffs = {H1: (h1, 900, 400, 0), H2: (h2, 500, 300, 7), H3: (h3, 350, 60, 0)}
    return cfgs, handoffs


def test_shrinkage_states_the_ratio_the_void_set_and_the_loss_split(cells, tmp_path):
    cfgs, handoffs = cells
    for cell, L in LEVELS.items():
        _write_level(cfgs[cell], L, handoffs)
    levels = load_levels(cfgs["full"], tmp_path)
    s = shrinkage(levels)
    assert s["n_handoffs"] == 3 and s["min_common_matched"] == 50
    p1, p2, p3 = (s["per_handoff"][h] for h in (H1, H2, H3))
    # H1: survivors under L32 = FULL pairs with p_S >= 600; no re-matching loss
    h1 = handoffs[H1][0]
    exp1 = int((h1[:, 0] >= 600).sum())
    assert exp1 == 300
    assert p1["n_common"] == exp1 and p1["ratio"] == pytest.approx(exp1 / len(h1)) and abs(p1["rematching_loss"]) < 1e-12
    assert p1["identical_to_full"] == {FULL: True, "L600": False, "L450": False, "L300": False}
    # H2: L65 and L49 identical to FULL (|S| 500 <= 600, 450 is not); L32 drops every 7th survivor on top of the removal
    assert p2["identical_to_full"]["L600"] and not p2["identical_to_full"]["L450"]
    assert p2["rematching_loss"] > 0 and p2["survivable_fraction"] > p2["ratio"]
    # H3: nothing survives L32 -> void, zero
    assert p3["n_common"] == 0 and p3["void"] and s["void"] == [H3] and s["n_zero"] == 1
    assert s["pooled_ratio"] == pytest.approx(s["n_common_total"] / s["n_matched_full_total"])
    assert s["n_below_0_80"] >= 1
    md = render_shrinkage(s)
    assert "void under |M_cap| >= 50" in md and "decides nothing" in md
    # pins: a coverage written under another config refuses
    cov_p = cfgs["l32"].results_dir / "align" / "coverage.json"
    cov = json.loads(cov_p.read_text(encoding="utf-8"))
    cov_p.write_text(json.dumps(cov | {"config_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="another l32.toml"):
        shrinkage(levels)
    cov_p.write_text(json.dumps(cov | {"sender_head_truncate": 299}), encoding="utf-8")
    with pytest.raises(ValueError, match="records truncation"):
        shrinkage(levels)


def _delta_for(handoffs, l32_far_value, full_far_value=0.10, seed=0):
    """FULL-frame per-token delta per handoff, per level: FULL tokens at `full_far_value`, L32 tokens at
    `l32_far_value` (the far-from-seam tokens are what the reading reads, so every token gets the value)."""
    rng = np.random.default_rng(seed)
    out = {}
    for hid, (fp, *_rest) in handoffs.items():
        n = len(fp)
        out[hid] = {FULL: np.full(n, full_far_value) + rng.uniform(-1e-4, 1e-4, n),
                    "L600": np.full(n, full_far_value), "L450": np.full(n, full_far_value),
                    "L300": np.full(n, l32_far_value) + rng.uniform(-1e-4, 1e-4, n)}
    return out


def _write_all(cfgs, handoffs, deltas, **kw):
    for cell, L in LEVELS.items():
        name = FULL if L is None else f"L{L}"
        _write_level(cfgs[cell], L, handoffs, delta={h: d[name] for h, d in deltas.items()}, **kw)


@pytest.mark.parametrize("l32_value,expected", [(0.0381, "length"), (0.0629, "the handoffs"), (0.0505, "unattributed")])
def test_the_reading_lands_in_each_of_its_three_outcomes(cells, tmp_path, l32_value, expected):
    cfgs, handoffs = cells
    _refs(tmp_path, short=0.0381, long_=0.0629)
    _write_all(cfgs, handoffs, _delta_for(handoffs, l32_value))
    levels = load_levels(cfgs["full"], tmp_path)
    out = compare_levels(levels, tmp_path)
    assert out["reading"]["reads_as"] == expected and out["reading"]["level"] == "L300"
    assert out["reading"]["far_from_seam_median_on_M_cap"] == pytest.approx(l32_value, abs=2e-4)
    assert out["reading"]["short_scaled_level"] == 0.0381 and out["reading"]["long_level"] == 0.0629
    assert out["void"] == [H3] and out["n_used"] == 2 and out["n_scored_at_every_level"] == 3
    assert out["references"]["short_scaled"]["sha256"] == sha256_file_bytes(tmp_path / "refs" / "compare.json")
    b = out["by_level"]
    assert b[FULL]["sender_head_truncate"] is None and b["L300"]["sender_head_truncate"] == 300
    assert b["L300"]["paired_mean_delta_K_minus_full"]["median"] == pytest.approx(l32_value - 0.10, abs=2e-4)
    assert b["L300"]["paired_mean_delta_K_minus_full"]["bootstrap"]["seed"] == 52
    assert b["L600"]["paired_mean_delta_K_minus_full"]["median"] == pytest.approx(0.0, abs=2e-4)
    tk = _tau_key(float(cfgs["full"].rule["tau_K"]))
    assert b["L300"]["fstar_median_over_handoffs"][tk] == 0.0        # 0.05 sits under tau_K
    md = render(out)
    assert f"reads as {expected}" in md and "decides nothing" in md and "void:" in md
    # the seam frame is FULL's: the far-from-seam token count on M_cap matches a direct recount
    h1 = handoffs[H1][0]
    rows = np.where(h1[:, 0] >= 600)[0]
    bins = seam_bin(seam_distance_left(h1, 400)[rows])
    assert out["per_handoff"][H1]["levels"][FULL]["far_from_seam"]["n_tokens"] == int((bins == 5).sum())


def test_reading_refuses_a_margin_that_spans_both_levels():
    assert reading(0.04, 0.0381, 0.0629, 0.005) == "length"
    assert reading(0.06, 0.0381, 0.0629, 0.005) == "the handoffs"
    assert reading(0.05, 0.0381, 0.0629, 0.005) == "unattributed"
    with pytest.raises(ValueError, match="spans both"):
        reading(0.05, 0.0381, 0.0629, 0.02)


def test_compare_refuses_on_every_pin(cells, tmp_path):
    cfgs, handoffs = cells
    _refs(tmp_path, short=0.0381, long_=0.0629)
    deltas = _delta_for(handoffs, 0.0381)
    _write_all(cfgs, handoffs, deltas)
    levels = load_levels(cfgs["full"], tmp_path)
    compare_levels(levels, tmp_path)
    l32 = cfgs["l32"]
    rp = l32.results_dir / "report.json"
    rep = json.loads(rp.read_text(encoding="utf-8"))
    # 1. an incomplete level
    rp.write_text(json.dumps(rep | {"complete": False}), encoding="utf-8")
    with pytest.raises(ValueError, match="not complete"):
        compare_levels(levels, tmp_path)
    # 2. a level under another config
    rp.write_text(json.dumps(rep | {"config_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="another l32.toml"):
        compare_levels(levels, tmp_path)
    # 3. two pins
    rp.write_text(json.dumps(rep | {"upstream_sha": "b" * 40}), encoding="utf-8")
    with pytest.raises(ValueError, match="different upstream pins"):
        compare_levels(levels, tmp_path)
    rp.write_text(json.dumps(rep), encoding="utf-8")
    # 4. an edited per-token record
    tf = l32.results_dir / "tokens" / f"{_stem(H1)}.tokens.npz"
    z = dict(np.load(tf))
    z["same_K"] = z["same_K"] * 2
    np.savez(tf, **z)
    with pytest.raises(ValueError):
        compare_levels(levels, tmp_path)
    _write_all(cfgs, handoffs, deltas)
    # 5. a level whose alignment record is another trace
    ap = l32.results_dir / "align" / "coverage.json"
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["alignments"][0]["text_sha256"] = "other"
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="not the same handoff"):
        compare_levels(levels, tmp_path)
    _write_all(cfgs, handoffs, deltas)
    assert ap.exists()
    # 6. a missing reference record
    (tmp_path / "refs" / "summary.json").unlink()
    with pytest.raises(ValueError, match="reference record"):
        compare_levels(levels, tmp_path)
    _refs(tmp_path, short=0.0381, long_=0.0629)
    # 7. every handoff void -> nothing to read
    big = load_e9_config(cfgs["full"].config_path, tmp_path)
    big = big.__class__(**{**big.__dict__, "trunc": {**big.trunc, "min_common_matched": 10_000}})
    with pytest.raises(ValueError, match="every scored handoff is void"):
        compare_levels({**levels, FULL: big}, tmp_path)


def test_partial_levels_compare_on_the_commonly_scored_set(cells, tmp_path):
    cfgs, handoffs = cells
    _refs(tmp_path, short=0.0381, long_=0.0629)
    deltas = _delta_for(handoffs, 0.0381)
    _write_all(cfgs, handoffs, deltas)
    # L32 stopped after H1 and H3 (a prefix by |S| descending: 900, 500, 350 -> drop H2)
    l32 = cfgs["l32"]
    rp = l32.results_dir / "report.json"
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["scores"].pop(H2)
    rep["partial"] = {"n_scored": 2, "n_registered": 3, "unscored": [H2]}
    rp.write_text(json.dumps(rep), encoding="utf-8")
    out = compare_levels(load_levels(cfgs["full"], tmp_path), tmp_path)
    assert out["n_scored_at_every_level"] == 2 and out["unscored_by_level"]["L300"] == [H2] and out["unscored_by_level"][FULL] == []
    assert out["n_used"] == 1 and out["levels"]["L300"]["partial"]
    rep["scores"] = {}
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="no handoff is scored at every level"):
        compare_levels(load_levels(cfgs["full"], tmp_path), tmp_path)


def test_load_levels_refuses_levels_that_are_not_one_instrument(tmp_path):
    full = _cfg(tmp_path, "full", None)
    for cell, L in LEVELS.items():
        if L is not None:
            _cfg(tmp_path, cell, L)
    assert list(load_levels(full, tmp_path)) == [FULL, "L600", "L450", "L300"]
    # a level whose rule differs
    p = tmp_path / "l32.toml"
    src = p.read_text(encoding="utf-8")
    p.write_text(src.replace("holds_max = 0.15", "holds_max = 0.2"), encoding="utf-8")
    with pytest.raises(ValueError, match="rule differs"):
        load_levels(full, tmp_path)
    # a level without the key
    p.write_text(src.replace("sender_head_truncate = 300\n", ""), encoding="utf-8")
    with pytest.raises(ValueError, match="must register sender_head_truncate"):
        load_levels(full, tmp_path)
    # levels not descending
    p.write_text(src.replace("sender_head_truncate = 300", "sender_head_truncate = 700"), encoding="utf-8")
    with pytest.raises(ValueError, match="strictly descending"):
        load_levels(full, tmp_path)
    p.write_text(src, encoding="utf-8")
    # the FULL cell with a truncation of its own, or without [e9.trunc]
    bare = load_e9_config(tmp_path / "l32.toml", tmp_path)
    with pytest.raises(ValueError, match="no \\[e9.trunc\\]"):
        load_levels(bare, tmp_path)
