"""summarize_e9 refusals, on the fake-upstream fixture from test_e9."""
import json

import numpy as np
import pytest

from linear_ceiling import e9 as driver
from linear_ceiling import summarize_e9 as s9
from linear_ceiling.summarize_e9 import band_outcome, summarize
from tests.test_e9 import _MEAN, env, fake_runner_factory, words  # noqa: F401  (pytest fixture)


@pytest.fixture
def ran(env, tmp_path, monkeypatch):
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    return cfg, e7, tmp_path / "results" / "e9" / "report.json", runner


def _write(p, obj):
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def test_band_outcome_edges():
    band = {"holds_min": 0.70, "degrades_max": 0.40}
    assert band_outcome(0.70, band) == "HOLDS" and band_outcome(0.40, band) == "DEGRADES"
    assert band_outcome(0.55, band) == "UNRESOLVED"


def test_clean_report_summarizes(ran):
    cfg, e7, _, runner = ran
    md = summarize(cfg, runner=runner, encoder=words, e7=e7)
    assert "1 included / 1 excluded" in md
    assert "E9-same K R² per handoff" in md and f"{_MEAN:.4f}" in md
    assert "**UNRESOLVED**" in md                    # canned moments give 0.625: between 0.40 and 0.70
    assert "verdict on H-E9 is NOT stated" in md


def test_refuses_a_checkpoint_report(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["complete"] = False
    _write(rp, rep)
    with pytest.raises(ValueError, match="checkpoint, not a complete run"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_edited_report_copy_of_a_layer_mean(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    rep["scores"][hid]["same_K_r2_layer_mean"] = 0.9
    _write(rp, rep)
    with pytest.raises(ValueError, match="report copy of same K differs"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_score_file_tamper_even_with_updated_hash(ran):
    """Editing the score file AND its recorded hash still fails: the moments must reproduce R²."""
    from linear_ceiling.hashing import sha256_file_bytes
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    sf = cfg.results_dir / "scores" / rep["scores"][hid]["score_file"]
    body = json.loads(sf.read_text(encoding="utf-8"))
    body["same_K_r2_layer_mean"] = 0.99
    body["same"]["K"][0]["r2_head_mean"] = 0.99
    _write(sf, body)
    rep["scores"][hid]["score_sha256"] = sha256_file_bytes(sf)
    rep["scores"][hid]["same_K_r2_layer_mean"] = 0.99
    _write(rp, rep)
    with pytest.raises(ValueError, match="does not follow from the recorded SSE/SST"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_missing_or_offhash_score_file(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    sf = cfg.results_dir / "scores" / rep["scores"][hid]["score_file"]
    sf.write_bytes(sf.read_bytes() + b" ")
    with pytest.raises(ValueError, match="score file missing or does not match"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_tampered_alignment_arrays(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    npz = cfg.results_dir / "align" / f"{driver._stem(hid)}.npz"
    z = dict(np.load(npz))
    z["pairs"] = z["pairs"][:-1]
    np.savez(npz, **z)
    with pytest.raises(ValueError, match="stored alignment arrays do not match"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_edited_coverage(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage"]["excluded"] = 0
    rep["coverage"]["included"] = 2
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage recomputed"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_keep_subset_rescore_disagreement(ran):
    """The kept tensors re-score differently from the recorded moments: the GPU record is bad."""
    cfg, e7, _, _ = ran
    drifted = fake_runner_factory(recheck_shift=0.05)
    with pytest.raises(ValueError, match="keep-subset re-score disagrees"):
        summarize(cfg, runner=drifted, encoder=words, e7=e7)


def test_refuses_tampered_kept_dump(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    d = cfg.results_dir / rep["scores"][hid]["kept_dir"] / "same_src"
    (d / "kv.bin").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="does not match its fingerprint"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
