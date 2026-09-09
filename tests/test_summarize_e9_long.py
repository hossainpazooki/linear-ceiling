"""summarize_e9 under an E9-long config (entry 0035): floor, run order, partial close, the bridge control
and its reading, the length profiles -- on the fake-upstream fixture."""
import json

import numpy as np
import pytest

from linear_ceiling import e9 as driver
from linear_ceiling import summarize_e9 as s9
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.summarize_e9 import summarize
from tests.test_e9 import env, fake_runner_factory, words  # noqa: F401
from tests.test_e9_long import A_ID, B_ID, C_ID, YARN, _long_cfg, _write_long, _crash_on
from tests.test_summarize_e9 import FAKE_CAL, write_fake_e7_report


@pytest.fixture
def long_env(env, tmp_path, monkeypatch):
    cfg, e7, calls, runner = env
    _write_long(tmp_path, "b", 40)
    _write_long(tmp_path, "c", 20)
    cfg = _long_cfg(cfg, keep_n=1)
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    monkeypatch.setattr(s9, "_check_calibration", lambda cfg, runner: FAKE_CAL)
    return cfg, e7, calls, runner


def _ran(long_env, tmp_path):
    cfg, e7, calls, runner = long_env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    write_fake_e7_report(e7, cfg.results_dir / "report.json")
    return cfg, e7, cfg.results_dir / "report.json", runner


def test_long_summary_states_bridge_profiles_and_full_coverage(long_env, tmp_path):
    cfg, e7, rp, runner = _ran(long_env, tmp_path)
    md = summarize(cfg, runner=runner, encoder=words, e7=e7)
    fig = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    assert fig["context_floor"] == 100 and fig["rope"] == YARN and fig["order_by"] == "n_sender_asc"
    assert fig["run_order"] == [C_ID, B_ID] and fig["partial"] is None
    assert fig["coverage"] == {"observed": 3, "included": 2, "excluded": 1, "scored": 2, "registered": 2, "unscored": []}
    assert fig["coverage_comparison"]["n"]["excluded_prior_cap"] == 1
    # bridge: one handoff, (p, p) over |S|, f* from the record, reading stated against the registered max
    br = fig["bridge"]
    assert set(br["per_handoff"]) == {A_ID} and br["reading_max_fstar"] == 0.15 and br["rope"] == YARN
    row = br["per_handoff"][A_ID]
    assert row["n_sender"] > 0 and 0.0 <= row["fstar_K"] <= 1.0 and set(row["fstar_ladder_K"]) == {"0.1", "0.03"}
    assert row["rescore_agreement"]["same_K"]["bit_identical_frac"] == 1.0
    assert br["median_fstar_K"] == row["fstar_K"]
    assert br["reading"].startswith("SCALED RECEIVER ONLY" if row["fstar_K"] > 0.15 else "CARRIED")
    assert (cfg.results_dir / "recheck" / "bridge" / f"{driver._stem(A_ID)}.json").exists()
    # profiles: every scored token lands in exactly one position bin; handoff bins partition the scored set
    prof = fig["length_profiles"]
    n_pairs = sum(json.loads((cfg.results_dir / "scores" / fig_rec["score_file"]).read_text(encoding="utf-8"))["n_pairs"]
                  for fig_rec in json.loads(rp.read_text(encoding="utf-8"))["scores"].values())
    assert sum(r["n_tokens"] for r in prof["s_pos"]) == n_pairs and len(prof["s_pos"]) == 3
    assert sum(r["n_handoffs"] for r in prof["s_len"]) == 2 and len(prof["s_len"]) == 2
    assert prof["s_len"][0]["bin"] == "101-299" and prof["s_len"][1]["bin"] == "300-1000"
    for r in prof["s_pos"]:
        assert (r["fstar_K_pooled"] is None) == (r["n_tokens"] == 0)
    assert "E9-long (entry 0035)" in md and "configuration bridge" in md and "2 scored of 2 registered" in md


def test_partial_close_summarizes_the_prefix_and_names_the_unscored(long_env, tmp_path):
    cfg, e7, calls, runner = long_env
    cfg = cfg.__class__(**{**cfg.__dict__, "keep_n": 0})
    with pytest.raises(RuntimeError, match="box reclaimed"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=_crash_on(driver._stem(B_ID), calls), encoder=words)
    write_fake_e7_report(e7, cfg.results_dir / "report.json")
    with pytest.raises(ValueError, match="not a complete run"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    driver.close_partial(cfg)
    md = summarize(cfg, runner=runner, encoder=words, e7=e7)
    fig = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    assert fig["coverage"]["scored"] == 1 and fig["coverage"]["registered"] == 2 and fig["coverage"]["unscored"] == [B_ID]
    assert fig["partial"]["n_scored"] == 1 and set(fig["fstar_per_handoff"]["same_K"]) == {C_ID}
    assert fig["bridge"] is not None and "PARTIAL close" in md and "1 scored of 2 registered" in md
    # the same partial report under a config that registers no partial close is refused
    with pytest.raises(ValueError, match="registers no partial close"):
        summarize(cfg.__class__(**{**cfg.__dict__, "allow_partial": False}), runner=runner, encoder=words, e7=e7)
    # a partial report whose scored set is not the registered prefix is refused
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    rep["partial"]["unscored"] = []
    (cfg.results_dir / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="unscored list"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_bridge_tamper_missing_or_rescore_drift(long_env, tmp_path):
    cfg, e7, calls, runner = long_env
    long_env = (cfg.__class__(**{**cfg.__dict__, "keep_n": 0}), e7, calls, runner)   # no kept handoff: the bridge is the only re-score
    cfg, e7, rp, runner = _ran(long_env, tmp_path)
    rep = json.loads(rp.read_text(encoding="utf-8"))
    b = rep["bridge"]["handoffs"][A_ID]
    # tampered kept scaled dump
    d = cfg.results_dir / b["kept_dir"] / "scaled"
    orig = (d / "kv.bin").read_bytes()
    (d / "kv.bin").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="bridge .* kept dump scaled does not match"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    (d / "kv.bin").write_bytes(orig)
    # re-score from the tensors disagrees with the box record
    with pytest.raises(ValueError, match="bridge .* re-score from the kept tensors disagrees"):
        summarize(cfg, runner=fake_runner_factory(recheck_shift=0.05), encoder=words, e7=e7)
    # score file edited (hash kept in the report): off-hash
    sf = cfg.results_dir / "bridge" / b["score_file"]
    body = json.loads(sf.read_text(encoding="utf-8"))
    body["same_K_r2_layer_mean"] += 0.01
    sf.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(ValueError, match="missing or off-hash"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    # bridge block removed from the report
    rep["bridge"] = None
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="bridge control missing"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_run_order_or_floor_drift(long_env, tmp_path):
    cfg, e7, rp, runner = _ran(long_env, tmp_path)
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["run_order"] = list(reversed(rep["run_order"]))
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="run order does not re-derive"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    rep["run_order"] = list(reversed(rep["run_order"]))
    rep["context_floor"] = 0
    rp.write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(ValueError, match="context_floor / rope"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_native_e9_summary_is_unchanged_in_shape(env, tmp_path, monkeypatch):
    """config/e9.toml's summarizer output gains only null/empty 0035 fields."""
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    write_fake_e7_report(e7, cfg.results_dir / "report.json")
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    monkeypatch.setattr(s9, "_check_calibration", lambda cfg, runner: FAKE_CAL)
    md = summarize(cfg, runner=runner, encoder=words, e7=e7)
    fig = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    assert fig["bridge"] is None and fig["length_profiles"] is None and fig["partial"] is None and fig["context_floor"] == 0
    assert fig["coverage"]["scored"] == fig["coverage"]["included"] and fig["coverage"]["unscored"] == []
    assert "E9-long" not in md
