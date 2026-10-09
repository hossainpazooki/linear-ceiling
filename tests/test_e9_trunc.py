"""E-TRUNC (design docs/drafts/e-trunc-design.md): the `sender_head_truncate` key, the truncated
alignment, and the descending run order. Offline, synthetic.

The design's claim (its section 1): under causal attention, TAIL truncation of S changes no matched
token, so the length treatment is HEAD truncation S' = S[-L:], which keeps the matched tokens (where
the aligner re-finds them) at shifted sender positions p_S' = p_S - (|S| - L)."""
import json
from dataclasses import replace

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling import e9 as driver
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import run_order
from linear_ceiling.e9_align import Alignment, Handoff, align
from tests.test_e9 import env, words  # noqa: F401  (fixture reuse)
from tests.test_e9_long import _write_long

A_ID = "20241016_composio_x/a_traj#1"
B_ID = "20241016_composio_x/b_traj#1"

HEAD = "h1 h2 h3 h4 h5"                      # junk the truncation removes: in S only
CORE = "c1 c2 c3 c4 c5 c6 c7 c8"             # the matched content: in S and R
TAIL = "t1 t2 t3 t4"                         # junk after the matched content: in S only


def _enc():
    vocab = {}
    return lambda text: [vocab.setdefault(w, len(vocab)) for w in text.split()]


def _h(sender):
    return Handoff("s/x_traj#1", "s/x_traj", 1, "m1", "m2", sender, CORE)


def test_tail_truncation_changes_no_matched_pair():
    """Design section 1 at the aligner: dropping S's tail leaves the match set and positions intact."""
    enc = _enc()
    full, _, _, p_full = align(_h(f"{HEAD} {CORE} {TAIL}"), enc, context_cap=100)
    cut, _, _, p_cut = align(_h(f"{HEAD} {CORE}"), enc, context_cap=100)
    assert not full.excluded and not cut.excluded
    assert full.n_matched == cut.n_matched == len(CORE.split())
    assert p_full.tolist() == p_cut.tolist()


def test_head_truncation_shifts_the_match_set_by_the_removed_length():
    enc = _enc()
    sender = f"{HEAD} {CORE} {TAIL}"
    n_full = len(sender.split())
    L = n_full - len(HEAD.split())            # removes exactly the junk head
    base, s_base, _, p_base = align(_h(sender), enc, context_cap=100)
    rec, s_ids, r_ids, p = align(_h(sender), enc, context_cap=100, sender_head_truncate=L)
    assert not rec.excluded
    assert rec.n_sender == n_full             # the record keeps the FULL |S| (cap, bins, run order read it)
    assert len(s_ids) == L                    # the npz/dump side holds S'
    assert rec.n_matched == base.n_matched    # same match set...
    off = n_full - L
    assert p[:, 0].tolist() == [i - off for i in p_base[:, 0].tolist()]   # ...at p_S' = p_S - (|S| - L)
    assert p[:, 1].tolist() == p_base[:, 1].tolist()                      # receiver positions untouched


def test_head_truncation_into_the_matched_region_shrinks_the_match():
    enc = _enc()
    sender = f"{HEAD} {CORE} {TAIL}"
    keep_core = 3
    L = keep_core + len(TAIL.split())         # S' = last 3 core tokens + the tail junk
    rec, s_ids, _, p = align(_h(sender), enc, context_cap=100, sender_head_truncate=L)
    assert rec.n_matched == keep_core and len(s_ids) == L
    assert (p[:, 0] < L).all()


def test_truncation_at_or_above_s_is_a_no_op():
    enc = _enc()
    sender = f"{HEAD} {CORE}"
    a, s_a, _, p_a = align(_h(sender), enc, context_cap=100)
    b, s_b, _, p_b = align(_h(sender), enc, context_cap=100, sender_head_truncate=len(sender.split()) + 7)
    assert a == b and s_a.tolist() == s_b.tolist() and p_a.tolist() == p_b.tolist()


def test_exclusions_are_decided_on_the_full_lengths():
    """A handoff over the cap stays EXCLUDED (0017: counted, never truncated into inclusion), and the
    floor reads the full |S| too -- truncation must not move any cell's included set."""
    enc = _enc()
    sender = " ".join(f"w{i}" for i in range(60)) + " " + CORE
    rec, s, r, p = align(_h(sender), enc, context_cap=50, sender_head_truncate=10)
    assert rec.excluded and "exceeds context cap 50" in rec.reason and s is None
    rec2, *_ = align(_h(sender), enc, context_cap=100, context_floor=90, sender_head_truncate=10)
    assert rec2.excluded and "context floor 90" in rec2.reason


def test_run_order_descending_longest_sender_first():
    recs = [Alignment("h/b#1", 300, 10, 5, False, None, "x"), Alignment("h/a#1", 300, 10, 5, False, None, "x"),
            Alignment("h/c#1", 150, 10, 5, False, None, "x"), Alignment("h/z#1", 9999, 10, 0, True, "cap", "x")]
    inc = ["h/b#1", "h/a#1", "h/c#1"]
    assert run_order(recs, inc, "n_sender_desc") == ["h/a#1", "h/b#1", "h/c#1"]   # ties by id, excluded never ordered


def test_align_only_records_the_truncation_and_writes_truncated_arrays(env, tmp_path):  # noqa: F811
    cfg, e7, _, _ = env
    _write_long(tmp_path, "b", 40)
    cfg = replace(cfg, context_cap=1000, order_by="n_sender_desc", sender_head_truncate=60)
    p = driver.align_only(cfg, e7, encoder=words)
    cov = json.loads(p.read_text(encoding="utf-8"))
    assert cov["sender_head_truncate"] == 60
    rec = {a["handoff_id"]: a for a in cov["alignments"]}
    assert not rec[B_ID]["excluded"] and rec[B_ID]["n_sender"] > 60      # the record keeps the full |S|
    z = np.load(cfg.results_dir / "align" / "20241016_composio_x__b_traj_sw1.npz")
    assert len(z["sender"]) == 60 and (z["pairs"][:, 0] < 60).all()
    assert rec[B_ID]["n_matched"] == 60                                   # S' sits inside R's repeat of the body
    assert cov["run_order"][0] == B_ID                                    # longest sender first
    cfg0 = replace(cfg, sender_head_truncate=None)
    cov0 = json.loads(driver.align_only(cfg0, e7, encoder=words).read_text(encoding="utf-8"))
    assert "sender_head_truncate" not in cov0                             # existing cells stay byte-identical


def test_summarizer_reads_a_truncated_level_whose_controls_cover_the_dumped_sender(env, tmp_path, monkeypatch):  # noqa: F811
    """2026-10-08 (the E-TRUNC sitting): the L65 level's identity control covered its 65,536 dumped positions, every
    square zero, and the reader refused it against the alignment record's FULL |S| = 80,111 -- which 0055 keeps on purpose
    (inclusion and run order are decided on the full sender). The reader must expect min(|S|, L) positions on a truncated
    level and |S| elsewhere; the driver was right."""
    from linear_ceiling import summarize_e9 as s9
    from linear_ceiling.summarize_e9 import summarize
    from tests.test_summarize_e9 import FAKE_CAL, write_fake_e7_report
    cfg, e7, _, runner = env
    _write_long(tmp_path, "b", 40)
    cfg = replace(cfg, context_cap=1000, order_by="n_sender_desc", sender_head_truncate=60)
    rp = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rec = {a["handoff_id"]: a for a in rep["alignments"]}
    assert rep["controls"]["handoff_id"] == B_ID and rec[B_ID]["n_sender"] > 60    # the controls ran on a truncated sender
    assert rep["controls"]["identity"]["n_pairs"] == 60                             # ... and covered S' = S[-60:]
    write_fake_e7_report(e7, rp)
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    monkeypatch.setattr(s9, "_check_calibration", lambda cfg, runner: FAKE_CAL)
    summarize(cfg, runner=runner, encoder=words, e7=e7)                              # refused before the fix
    s = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    assert s["prefix_control"]["n_positions"] == 60
    assert s9._dumped_sender_len(cfg, 80111) == 60 and s9._dumped_sender_len(replace(cfg, sender_head_truncate=None), 80111) == 80111
    assert s9._dumped_sender_len(cfg, 40) == 40                                      # a sender shorter than L is dumped whole


def test_e9l_config_accepts_the_key_and_existing_configs_carry_none(tmp_path):
    src = (REPO_ROOT / "config" / "e9l.toml").read_text(encoding="utf-8")
    p = tmp_path / "e9t.toml"
    p.write_text(src.replace("[e9.alignment]", "[e9.alignment]\nsender_head_truncate = 32768"), encoding="utf-8")
    c = load_e9_config(p, tmp_path)
    assert c.sender_head_truncate == 32768
    for name in ("e9.toml", "e9l.toml", "e9s.toml"):
        assert load_e9_config(REPO_ROOT / "config" / name, REPO_ROOT).sender_head_truncate is None


@pytest.mark.parametrize("value", ["0", "-5", "true", "2.5", "81920", "100000"])   # 81920 == the cap
def test_config_refuses_a_truncation_that_is_not_an_integer_inside_the_cap(tmp_path, value):
    src = (REPO_ROOT / "config" / "e9l.toml").read_text(encoding="utf-8")
    p = tmp_path / "e9t.toml"
    p.write_text(src.replace("[e9.alignment]", f"[e9.alignment]\nsender_head_truncate = {value}"), encoding="utf-8")
    with pytest.raises(ValueError, match="sender_head_truncate"):
        load_e9_config(p, tmp_path)
