"""The L32-native cell (summarize_e9_native): the committed config against the L32 YaRN level's, the [e9.native]
refusals, the pre-prefill alignment check, the three outcomes of the registered reading on M_cap, the partial rule and
the pins -- on the synthetic levels of tests/test_summarize_e9_trunc.py."""
import json
import re

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import _stem
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.summarize_e9_native import (NATIVE, _SAME, alignment_check, compare_native, load_cells, reading,
                                                render, render_alignment)
from linear_ceiling.summarize_e9_trunc import FULL, compare_levels, load_levels
from tests.test_summarize_e9_trunc import H1, H2, H3, LEVELS, _delta_for, _write_level, cells  # noqa: F401

SHORT_NATIVE, SHORT_SCALED, LONG, YARN_L32 = 0.0195, 0.0381, 0.0629, 0.0868


# ---- the committed config -----------------------------------------------------------------------------------------

def _body(name):
    return [ln for ln in (REPO_ROOT / "config" / name).read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]


def _strip_blocks(src: str, *sections: str) -> str:
    for sec in sections:
        m = re.search(r"\n" + re.escape(sec) + r".*?\n(?=\n)", src, flags=re.S)
        assert m, sec
        src = src[:m.start()] + src[m.end():]
    return src


def test_the_committed_native_config_is_the_l32_level_byte_for_byte_except_the_named_lines():
    l32 = _strip_blocks("\n".join(_body("e9t-l32.toml")), "[e9.rope]", "[e9.bridge]").splitlines()
    nat = _body("e9t-l32n.toml")
    nat = nat[:next(i for i, ln in enumerate(nat) if ln.startswith("[e9.native]"))]
    while l32 and not l32[-1].strip():
        l32.pop()
    while nat and not nat[-1].strip():
        nat.pop()
    changed = [(x, y) for x, y in zip(l32, nat) if x != y]
    assert len(l32) == len(nat) and len(changed) == 3, changed
    assert all(k in "".join(x for x, _ in changed) for k in ("results_dir", "scratch_dir", "required_entries"))
    cfg = load_e9_config(REPO_ROOT / "config" / "e9t-l32n.toml", REPO_ROOT)
    yarn = load_e9_config(REPO_ROOT / "config" / "e9t-l32.toml", REPO_ROOT)
    assert cfg.rope is None and cfg.bridge is None and cfg.native is not None and cfg.sender_head_truncate == 32768
    assert cfg.required_entries == yarn.required_entries + ("0062",) and cfg.results_dir.name == "e9t-l32n"
    for field in _SAME:
        assert getattr(cfg, field) == getattr(yarn, field), field
    cs, name = load_cells(cfg, REPO_ROOT)
    assert list(cs) == [NATIVE, FULL, "L65536", "L49152", "L32768"] and name == "L32768"
    assert cfg.native["margin_abs"] == 0.005 and cfg.native["bootstrap_seed"] == 62 and cfg.native["bootstrap_reps"] == 2000
    assert cfg.native["short_native_compare"] == "results/e9s/compare.json" and cfg.native["trunc_compare"] == "results/e9t/compare.json"
    for other in ("e9.toml", "e9l.toml", "e9s.toml", "e9t-full.toml", "e9t-l32.toml", "e9fl.toml"):
        assert load_e9_config(REPO_ROOT / "config" / other, REPO_ROOT).native is None


@pytest.mark.parametrize("edit,msg", [
    (lambda s: s.replace("[e9.alignment]\nsender_head_truncate = 32768", "[e9.alignment]"), "belongs to a truncated level"),
    (lambda s: s.replace("\n[e9.native]", '\n[e9.rope]\nrope_type = "yarn"\nfactor = 2.5\noriginal_max_position_embeddings = 32768\n\n[e9.native]'),
     "no \\[e9.rope\\]"),
    (lambda s: s.replace("bootstrap_reps = 2000\n\n[e9.native]", "bootstrap_reps = 2000\n\n[e9.native]\nsurprise = 1"), "exactly"),
    (lambda s: s.replace("margin_abs = 0.005", "margin_abs = 1.5"), "margin_abs"),
    (lambda s: s.replace('full_config = "config/e9t-full.toml"', 'full_config = ""'), "repo-relative"),
    (lambda s: s.replace("context_floor = 32768", "context_floor = 0"), "context_floor > 0"),
])
def test_config_refuses_a_native_section_on_the_wrong_cell(tmp_path, edit, msg):
    src = (REPO_ROOT / "config" / "e9t-l32n.toml").read_text(encoding="utf-8")
    out = edit(src)
    assert out != src
    p = tmp_path / "e9t-l32n.toml"
    p.write_text(out, encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, tmp_path)


# ---- synthetic cells ------------------------------------------------------------------------------------------------

def _native_cfg(tmp_path, *, yarn="l32.toml", results="l32n", margin=0.005, reps=200):
    """The native synthetic cell: tests/test_summarize_e9_trunc.py's l32.toml minus [e9.rope] / [e9.bridge] plus [e9.native]."""
    src = (tmp_path / "l32.toml").read_text(encoding="utf-8")
    src = _strip_blocks(src, "[e9.rope]", "[e9.bridge]")
    src = src.replace('results_dir = "results/l32"', f'results_dir = "results/{results}"').replace(
        'scratch_dir = "results/l32/scratch"', f'scratch_dir = "results/{results}/scratch"')
    src = src.rstrip("\n") + f"""

[e9.native]
full_config = "full.toml"
yarn_level = "{yarn}"
out_dir = "results/{results}-out"
margin_abs = {margin}
short_native_compare = "refs/compare.json"
trunc_compare = "refs/trunc_compare.json"
bootstrap_seed = 62
bootstrap_reps = {reps}
"""
    p = tmp_path / "l32n.toml"
    p.write_text(src, encoding="utf-8")
    return load_e9_config(p, tmp_path)


def _refs(tmp_path, *, short_native=SHORT_NATIVE, short_scaled=SHORT_SCALED, long_=LONG):
    d = tmp_path / "refs"
    d.mkdir(exist_ok=True)
    (d / "compare.json").write_text(json.dumps({"n_handoffs": 25, "seam_profile_left_pooled": [
        {"bin": "16+", "n_tokens": 10, "median_native": short_native, "median_scaled": short_scaled}]}), encoding="utf-8")
    (d / "summary.json").write_text(json.dumps({"coverage": {"included": 35, "scored": 35}, "seam_profile_left_pooled": {
        "same_K": [{"bin": "16+", "n_tokens": 10, "median": long_}]}}), encoding="utf-8")


def _write_everything(tmp_path, cfgs, handoffs, native_value, l32_value=YARN_L32, **kw):
    """The four levels and the native cell with per-token records, the two reference records, and the E-TRUNC comparison
    record written by the real `compare_levels` over the synthetic levels (the record the native reader checks against)."""
    _refs(tmp_path)
    deltas = _delta_for(handoffs, l32_value)
    for cell, L in LEVELS.items():
        name = FULL if L is None else f"L{L}"
        _write_level(cfgs[cell], L, handoffs, delta={h: d[name] for h, d in deltas.items()})
    rng = np.random.default_rng(1)
    native = _native_cfg(tmp_path)
    _write_level(native, 300, handoffs,
                 delta={h: np.full(len(fp), native_value) + rng.uniform(-1e-4, 1e-4, len(fp)) for h, (fp, *_r) in handoffs.items()}, **kw)
    levels = load_levels(cfgs["full"], tmp_path)
    rec = compare_levels(levels, tmp_path)
    (tmp_path / "refs" / "trunc_compare.json").write_text(json.dumps(rec), encoding="utf-8")
    return native, rec


def test_alignment_check_states_identity_m_cap_the_void_set_and_the_dumped_length(cells, tmp_path):
    cfgs, handoffs = cells
    for cell, L in LEVELS.items():
        _write_level(cfgs[cell], L, handoffs)
    native = _native_cfg(tmp_path)
    _write_level(native, 300, handoffs)
    cs, name = load_cells(native, tmp_path)
    assert list(cs) == [NATIVE, FULL, "L600", "L450", "L300"] and name == "L300"
    s = alignment_check(cs, name)
    assert s["n_handoffs"] == s["n_identical_to_yarn"] == 3 and s["void"] == [H3] and s["n_used"] == 2
    assert s["min_common_matched"] == 50 and s["cells"][NATIVE]["rope"] is None and s["cells"]["L300"]["rope"]["rope_type"] == "yarn"
    # H1: |S| 900 -> S' = 300, + 1 for the prefix control; |R| 400 is the longest dump
    assert s["per_handoff"][H1] == {**s["per_handoff"][H1], "dumped_sender": 300, "dumped_length": 400, "n_common": 300, "void": False}
    assert s["max_dumped_sender"] == 300 and s["max_n_receiver"] == 400 and s["max_dumped_length"] == 400
    assert s["per_handoff"][H3]["dumped_length"] == 301                   # |S| 350 -> 300 + 1 > |R| 60
    md = render_alignment(s)
    assert "equals L300's on 3 of 3" in md and "longest dumped length 400" in md and "void:" in md
    # a native matched set that differs from the YaRN level's refuses: not the same tokens
    ap = native.results_dir / "align" / f"{_stem(H1)}.npz"
    z = dict(np.load(ap))
    z["pairs"] = z["pairs"][1:]
    np.savez(ap, **z)
    cov_p = native.results_dir / "align" / "coverage.json"
    cov = json.loads(cov_p.read_text(encoding="utf-8"))
    for a in cov["alignments"]:
        if a["handoff_id"] == H1:
            a["n_matched"] -= 1
    cov_p.write_text(json.dumps(cov), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from L300's"):
        alignment_check(cs, name)


def test_load_cells_refuses_cells_that_are_not_one_instrument(cells, tmp_path):
    cfgs, _ = cells
    native = _native_cfg(tmp_path)
    load_cells(native, tmp_path)
    with pytest.raises(ValueError, match="not one of the FULL cell's"):
        load_cells(_native_cfg(tmp_path, yarn="full.toml"), tmp_path)
    with pytest.raises(ValueError, match="sender_head_truncate differs"):
        load_cells(_native_cfg(tmp_path, yarn="l49.toml"), tmp_path)        # a level, but not the native cell's L
    p = _native_cfg(tmp_path).config_path                                 # back to the pairing with l32.toml
    src = p.read_text(encoding="utf-8")
    p.write_text(src.replace("holds_max = 0.15", "holds_max = 0.2"), encoding="utf-8")
    with pytest.raises(ValueError, match="rule differs"):
        load_cells(load_e9_config(p, tmp_path), tmp_path)
    p.write_text(src.replace('results_dir = "results/l32n"', 'results_dir = "results/l32"'), encoding="utf-8")
    with pytest.raises(ValueError, match="writes a level's results_dir"):
        load_cells(load_e9_config(p, tmp_path), tmp_path)
    with pytest.raises(ValueError, match="no \\[e9.native\\]"):
        load_cells(cfgs["l32"], tmp_path)


@pytest.mark.parametrize("native_value,expected", [(SHORT_NATIVE, "the scaling"), (YARN_L32, "not the scaling"), (0.05, "unattributed")])
def test_the_reading_lands_in_each_of_its_three_outcomes(cells, tmp_path, native_value, expected):
    cfgs, handoffs = cells
    native, rec = _write_everything(tmp_path, cfgs, handoffs, native_value)
    assert rec["reading"]["far_from_seam_median_on_M_cap"] == pytest.approx(YARN_L32, abs=2e-4)
    cs, name = load_cells(native, tmp_path)
    out = compare_native(cs, name, tmp_path)
    rd = out["reading"]
    assert rd["reads_as"] == expected and rd["complete_coverage"] and out["yarn_level"] == "L300"
    assert rd["far_from_seam_median_on_M_cap"] == pytest.approx(native_value, abs=2e-4)
    assert rd["yarn_level"] == rd["yarn_level_on_the_record"] == rec["reading"]["far_from_seam_median_on_M_cap"]
    assert rd["short_native_level"] == SHORT_NATIVE
    assert out["void"] == [H3] and out["n_used"] == 2 and out["n_scored_everywhere"] == 3 and out["max_dumped_length"] == 400
    assert out["references"]["yarn"]["sha256"] == sha256_file_bytes(tmp_path / "refs" / "trunc_compare.json")
    assert out["references"]["short_native"]["sha256"] == sha256_file_bytes(tmp_path / "refs" / "compare.json")
    b = out["by_cell"]
    assert b[NATIVE]["rope"] is None and b["L300"]["rope"]["rope_type"] == "yarn" and b["L300"]["sender_head_truncate"] == 300
    assert b["L300"]["far_from_seam_pooled"]["n_tokens"] == rec["by_level"]["L300"]["far_from_seam_pooled"]["n_tokens"]
    pm = out["paired_native_minus_yarn_mean_delta_K"]
    assert pm["median"] == pytest.approx(native_value - YARN_L32, abs=3e-4) and pm["bootstrap"]["seed"] == 62 and pm["bootstrap"]["reps"] == 200
    md = render(out)
    assert f"reads as {expected}" in md and "decides nothing" in md and "void:" in md and "PARTIAL" not in md
    assert out["cells"][NATIVE]["config_sha256"] == sha256_text_file(native.config_path)


def test_reading_refuses_a_margin_that_spans_both_levels():
    assert reading(0.02, SHORT_NATIVE, YARN_L32, 0.005) == "the scaling"
    assert reading(0.09, SHORT_NATIVE, YARN_L32, 0.005) == "not the scaling"
    assert reading(0.05, SHORT_NATIVE, YARN_L32, 0.005) == "unattributed"
    with pytest.raises(ValueError, match="spans both"):
        reading(0.05, 0.048, 0.052, 0.005)


def test_a_partial_native_run_reads_against_the_yarn_level_on_the_commonly_scored_tokens(cells, tmp_path):
    cfgs, handoffs = cells
    native, rec = _write_everything(tmp_path, cfgs, handoffs, SHORT_NATIVE)
    rp = native.results_dir / "report.json"
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["scores"].pop(H2)                                                   # stopped after H1 and H3 (|S| descending)
    rep["partial"] = {"n_scored": 2, "n_registered": 3, "unscored": [H2]}
    rp.write_text(json.dumps(rep), encoding="utf-8")
    cs, name = load_cells(native, tmp_path)
    out = compare_native(cs, name, tmp_path)
    assert out["n_scored_everywhere"] == 2 and out["unscored_by_cell"][NATIVE] == [H2] and out["n_used"] == 1
    assert out["cells"][NATIVE]["partial"] and not out["reading"]["complete_coverage"]
    assert out["reading"]["yarn_level_on_the_record"] == rec["reading"]["far_from_seam_median_on_M_cap"]
    assert out["reading"]["yarn_level"] == pytest.approx(YARN_L32, abs=2e-4) and out["reading"]["reads_as"] == "the scaling"
    assert "PARTIAL coverage" in render(out)
    rep["scores"] = {}
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="no handoff is scored"):
        compare_native(cs, name, tmp_path)


def test_compare_refuses_on_every_pin(cells, tmp_path):
    cfgs, handoffs = cells
    native, rec = _write_everything(tmp_path, cfgs, handoffs, SHORT_NATIVE)
    cs, name = load_cells(native, tmp_path)
    compare_native(cs, name, tmp_path)
    tp = tmp_path / "refs" / "trunc_compare.json"
    # 1. the E-TRUNC record read from another YaRN report
    tp.write_text(json.dumps({**rec, "levels": {**rec["levels"], "L300": {**rec["levels"]["L300"], "report_sha256": "0" * 64}}}), encoding="utf-8")
    with pytest.raises(ValueError, match="not the one the E-TRUNC record"):
        compare_native(cs, name, tmp_path)
    # 2. a record read under another floor, on another level, or with another void set / YaRN figure
    tp.write_text(json.dumps({**rec, "min_common_matched": 10}), encoding="utf-8")
    with pytest.raises(ValueError, match="read under floor"):
        compare_native(cs, name, tmp_path)
    tp.write_text(json.dumps({**rec, "reading": {**rec["reading"], "level": "L450"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="not L300"):
        compare_native(cs, name, tmp_path)
    tp.write_text(json.dumps({**rec, "void": [], "n_used": 3}), encoding="utf-8")
    with pytest.raises(ValueError, match="void set"):
        compare_native(cs, name, tmp_path)
    tp.write_text(json.dumps({**rec, "reading": {**rec["reading"], "far_from_seam_median_on_M_cap": YARN_L32 + 0.01}}), encoding="utf-8")
    with pytest.raises(ValueError, match="not the E-TRUNC record's"):
        compare_native(cs, name, tmp_path)
    tp.write_text(json.dumps(rec), encoding="utf-8")
    # 3. the native cell under another pin, or incomplete
    rp = native.results_dir / "report.json"
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rp.write_text(json.dumps(rep | {"upstream_sha": "b" * 40}), encoding="utf-8")
    with pytest.raises(ValueError, match="different upstream pins"):
        compare_native(cs, name, tmp_path)
    rp.write_text(json.dumps(rep | {"complete": False}), encoding="utf-8")
    with pytest.raises(ValueError, match="not complete"):
        compare_native(cs, name, tmp_path)
    rp.write_text(json.dumps(rep), encoding="utf-8")
    # 4. an edited native per-token record
    tf = native.results_dir / "tokens" / f"{_stem(H1)}.tokens.npz"
    z = dict(np.load(tf))
    z["same_K"] = z["same_K"] * 2
    np.savez(tf, **z)
    with pytest.raises(ValueError):
        compare_native(cs, name, tmp_path)
    native, rec = _write_everything(tmp_path, cfgs, handoffs, SHORT_NATIVE)
    cs, name = load_cells(native, tmp_path)
    # 5. a native alignment that is not the YaRN level's tokens
    ap = native.results_dir / "align" / f"{_stem(H1)}.npz"
    z = dict(np.load(ap))
    z["pairs"] = z["pairs"][1:]
    np.savez(ap, **z)
    with pytest.raises(ValueError, match="differs from L300's"):
        compare_native(cs, name, tmp_path)
    native, rec = _write_everything(tmp_path, cfgs, handoffs, SHORT_NATIVE)
    cs, name = load_cells(native, tmp_path)
    # 6. a missing reference record
    (tmp_path / "refs" / "compare.json").unlink()
    with pytest.raises(ValueError, match="reference record"):
        compare_native(cs, name, tmp_path)
