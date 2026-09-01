"""summarize_e9 refusals and outputs (entries 0019/0023), on the fake-upstream fixture from test_e9."""
import hashlib
import json
import types
from pathlib import Path

import numpy as np
import pytest

from linear_ceiling import e9 as driver
from linear_ceiling import summarize_e9 as s9
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.summarize_e9 import calibrate_tau, summarize
from tests.test_e9 import _MEAN, PAIR, RULE, env, fake_runner_factory, words  # noqa: F401  (pytest fixture)

FAKE_CAL = {"tau": {"K": RULE["tau_K"], "V": RULE["tau_V"]}, "heldout": {"n_tokens": 0, "K_r2_layer_mean": 0.75, "V_r2_layer_mean": 0.6}}


@pytest.fixture
def ran(env, tmp_path, monkeypatch):
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    monkeypatch.setattr(s9, "_check_calibration", lambda cfg, runner: FAKE_CAL)
    return cfg, e7, tmp_path / "results" / "e9" / "report.json", runner


def _write(p, obj):
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def _retoken(cfg, rep, hid, mutate):
    """Edit the per-token file of `hid` and re-hash it everywhere, so only the SUM check can catch it."""
    rec = rep["scores"][hid]
    tp = cfg.results_dir / "tokens" / rec["tokens_file"]
    z = dict(np.load(tp))
    mutate(z)
    np.savez_compressed(tp, **z)
    sha = sha256_file_bytes(tp)
    rec["tokens_sha256"] = sha
    sf = cfg.results_dir / "scores" / rec["score_file"]
    body = json.loads(sf.read_text(encoding="utf-8"))
    body["per_token"]["sha256"] = sha
    _write(sf, body)
    rec["score_sha256"] = sha256_file_bytes(sf)


def test_clean_report_summarizes_with_the_0023_statistics(ran):
    cfg, e7, rp, runner = ran
    md = summarize(cfg, runner=runner, encoder=words, e7=e7)
    assert "1 included / 1 excluded" in md
    assert "f*(tau_K = 0.2500)" in md and "oracle LOWER BOUND" in md
    assert "bridge R²" in md and f"{_MEAN:.4f}" in md
    assert "verdict on H-E9 is NOT stated" in md and "Units:" in md
    fig = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    hid = next(iter(fig["fstar_per_handoff"]["same_K"]))
    # canned squares: token mean of centered delta == 1 - R2 == 0.375 > tau_K 0.25 -> some recompute needed
    f = fig["fstar_per_handoff"]["same_K"][hid]
    assert 0.0 < f < 1.0 and fig["band_outcome"] in ("HOLDS", "UNRESOLVED", "DEGRADES")
    assert fig["fstar_per_handoff"]["same_V"][hid] == 0.0           # tau_V 0.40 > 0.375: nothing to remove
    assert fig["tau"] == {"K": 0.25, "V": 0.40}
    n_pairs = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))["scores"][hid]["n_pairs"]
    assert len(fig["seam_profile_pooled"]["same_K"]) == 6
    assert sum(r["n_tokens"] for r in fig["seam_profile_pooled"]["same_K"]) == n_pairs   # every token lands in one bin
    assert len(fig["depth_profile_median_per_layer"]["same_K"]) == 2
    assert fig["delta_null"]["same_K"]["median_token_mean"] > 0 and fig["delta_null_handoff"] == hid
    assert fig["cross_over_same_median_delta"]["K"]["median"] == pytest.approx(1.0)   # canned: identical arms


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


def test_refuses_offhash_per_token_file(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))
    tp = cfg.results_dir / "tokens" / rep["scores"][hid]["tokens_file"]
    tp.write_bytes(tp.read_bytes() + b" ")
    with pytest.raises(ValueError, match="per-token file missing or does not match"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


@pytest.mark.parametrize("arm", ["same_K", "same_V", "cross_K", "cross_V"])
def test_refuses_per_token_squares_that_do_not_sum_to_the_moments(ran, arm):
    """Re-hashed everywhere, so only the sum-to-SSE check stands between the tamper and a figure."""
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))

    def bump(z):
        z[arm][0, 0, 0] *= 1.5
    _retoken(cfg, rep, hid, bump)
    _write(rp, rep)
    with pytest.raises(ValueError, match=f"{arm} per-token squares do not sum"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_per_token_shape_or_reference_tamper(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))

    def zero_ref(z):
        z["ref_K"][1, 0, 0] = 0.0
    _retoken(cfg, rep, hid, zero_ref)
    _write(rp, rep)
    with pytest.raises(ValueError, match="reference norms ref_K missing or not positive"):
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


def test_refuses_identity_control_tamper(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    cdir = cfg.results_dir / "controls"
    # (a) identity record edited to carry a nonzero square, re-hashed
    tp = cdir / rep["controls"]["identity"]["tokens_file"]
    z = dict(np.load(tp))
    z["same_K"][0, 0, 0] = 1e-3
    np.savez_compressed(tp, **z)
    rep["controls"]["identity"]["tokens_sha256"] = sha256_file_bytes(tp)
    _write(rp, rep)
    with pytest.raises(ValueError, match="identity control: a per-token square is nonzero"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_null_pairs_that_do_not_rederive(ran):
    cfg, e7, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    cdir = cfg.results_dir / "controls"
    pf = cdir / rep["controls"]["null"]["pairs_file"]
    z = dict(np.load(pf))
    z["pairs"] = z["pairs"][::-1].copy()
    np.savez(pf, **z)
    rep["controls"]["null"]["pairs_sha256"] = sha256_file_bytes(pf)
    _write(rp, rep)
    with pytest.raises(ValueError, match="null control pairs do not re-derive"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


def test_refuses_missing_calibration_and_tau_drift(ran, monkeypatch):
    cfg, e7, rp, runner = ran
    monkeypatch.setattr(s9, "_check_calibration", s9.__dict__["_check_calibration"].__wrapped__
                        if hasattr(s9._check_calibration, "__wrapped__") else _real_check_calibration)
    with pytest.raises(ValueError, match="calibration/tau.json does not exist|run `summarize_e9 --calibrate-tau`"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    cal_dir = cfg.results_dir / "calibration"
    cal_dir.mkdir(parents=True)
    _write(cal_dir / "tau.json", {"tau": {"K": 0.25, "V": 0.40}})
    monkeypatch.setattr(s9, "calibrate_tau", lambda *a, **k: {"tau": {"K": 0.26, "V": 0.40}, "heldout": {}})
    with pytest.raises(ValueError, match="tau_K: recorded calibration"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)
    monkeypatch.setattr(s9, "calibrate_tau", lambda *a, **k: {"tau": {"K": 0.25, "V": 0.41}, "heldout": {}})
    _write(cal_dir / "tau.json", {"tau": {"K": 0.25, "V": 0.41}})
    with pytest.raises(ValueError, match="config tau_V"):
        summarize(cfg, runner=runner, encoder=words, e7=e7)


_real_check_calibration = s9._check_calibration


# ---------------------------------------------------------------- calibrate_tau on a fake archive

def _fake_archive(tmp_path, cfg, k_r2=0.75, v_r2=0.6, n=8, L=2, H=2):
    up = cfg.upstream_path
    mp = up / "mappers" / PAIR / "k1"
    mp.with_suffix(".json").write_text("{}", encoding="utf-8")
    mp.with_suffix(".safetensors").write_bytes(b"w")
    for name in ("source", "target"):
        d = up / "data" / "kv" / PAIR / name
        d.mkdir(parents=True)
        (d / "meta.json").write_text(json.dumps({"n_seqs": 2, "stride": 4}), encoding="utf-8")
        (d / "layer00.npz").write_bytes(name.encode())
    fps = {name: driver.dump_fingerprint(up / "data" / "kv" / PAIR / name) for name in ("source", "target")}
    (up / "results" / "mapper" / PAIR).mkdir(parents=True)
    _write(up / "results" / "mapper" / PAIR / "r2.json",
           {"k": {"1": {"K_r2_heldout_layer_mean": k_r2, "V_r2_heldout_layer_mean": v_r2}}})
    e8 = tmp_path / "e8_report.json"
    _write(e8, {"dumps": {"generic": fps}, "per_k": {"1": {"generic": {"K": k_r2, "V": v_r2}}}})

    def runner(cmd, cwd, capture_output):
        args = cmd[1:]
        opt = {args[i]: args[i + 1] for i in range(1, len(args) - 1, 2)}
        assert args[0] == "scripts/score_mapper.py"
        rng = np.random.default_rng(0)
        arrays = {}
        for key, r2 in (("K", k_r2), ("V", v_r2)):
            sst = rng.uniform(10, 20, size=(L, H))
            w = rng.uniform(0.5, 1.5, size=(n, L, H))
            sq = w / w.sum(0, keepdims=True) * ((1 - r2) * sst)[None]     # sums to SSE = (1-r2) SST per head
            arrays[f"{key}_sq"] = sq.astype(np.float32)
            arrays[f"ref_{key}"] = np.ones((n, L, H), np.float32)
            arrays[f"sst_{key}"] = sst
        arrays["n_heldout"] = np.asarray(n)
        pt = Path(opt["--per-token"])
        np.savez_compressed(pt, **arrays)
        rec = {"n_heldout_tokens": n, "K_r2_heldout_layer_mean": k_r2, "V_r2_heldout_layer_mean": v_r2,
               "K_r2_heldout_pooled_over_heads_layer_mean": k_r2 + 0.01,
               "V_r2_heldout_pooled_over_heads_layer_mean": v_r2 + 0.01,
               "per_token": {"path": pt.name, "sha256": hashlib.sha256(pt.read_bytes()).hexdigest()}}
        _write(Path(opt["--out"]), rec)
        return types.SimpleNamespace(returncode=0, stderr=b"")
    return runner, e8


def test_calibrate_tau_writes_tau_as_one_minus_r2_with_provenance(env, tmp_path, monkeypatch):
    cfg, _, _, _ = env
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    runner, e8 = _fake_archive(tmp_path, cfg)
    out = calibrate_tau(cfg, runner, e8_report=e8)
    assert out["tau"]["K"] == pytest.approx(0.25) and out["tau"]["V"] == pytest.approx(0.40)
    assert out["diagnostics"]["K"]["mapper_own_fstar"]["at_tau_mean"] == 0.0
    assert out["diagnostics"]["K"]["mapper_own_fstar"]["at_centered_median"] > 0.0
    assert out["diagnostics"]["K"]["pooled_over_heads_r2_layer_mean"] == pytest.approx(0.76)
    assert out["bridge_check_max_abs"] < 1e-5
    assert out["generic_dumps_match_e8_fingerprints"] == {"source": True, "target": True}
    saved = json.loads((cfg.results_dir / "calibration" / "tau.json").read_text(encoding="utf-8"))
    assert saved["tau"] == out["tau"] and saved["upstream_pin_check"] == "held"


def test_calibrate_tau_refuses_archive_or_fingerprint_disagreement(env, tmp_path, monkeypatch):
    cfg, _, _, _ = env
    monkeypatch.setattr(s9, "check_upstream", lambda *a, **k: None)
    runner, e8 = _fake_archive(tmp_path, cfg)
    arch = cfg.upstream_path / "results" / "mapper" / PAIR / "r2.json"
    _write(arch, {"k": {"1": {"K_r2_heldout_layer_mean": 0.70, "V_r2_heldout_layer_mean": 0.6}}})
    with pytest.raises(ValueError, match="disagrees with the archived r2.json"):
        calibrate_tau(cfg, runner, e8_report=e8)
    _write(arch, {"k": {"1": {"K_r2_heldout_layer_mean": 0.75, "V_r2_heldout_layer_mean": 0.6}}})
    (cfg.upstream_path / "data" / "kv" / PAIR / "source" / "layer00.npz").write_bytes(b"moved")
    with pytest.raises(ValueError, match="do not match the fingerprints E8 recorded"):
        calibrate_tau(cfg, runner, e8_report=e8)


def test_calibrate_tau_refuses_a_dirty_upstream_unless_allowed(env, tmp_path, monkeypatch):
    cfg, _, _, _ = env

    def refuse(*a, **k):
        raise RuntimeError("pin not held")
    monkeypatch.setattr(s9, "check_upstream", refuse)
    runner, e8 = _fake_archive(tmp_path, cfg)
    with pytest.raises(ValueError, match="pin not held"):
        calibrate_tau(cfg, runner, e8_report=e8)
    out = calibrate_tau(cfg, runner, e8_report=e8, allow_dirty_upstream=True)
    assert out["upstream_pin_check"] == "pin not held"
