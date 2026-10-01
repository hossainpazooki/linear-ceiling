"""The tail summarizer (reviewer weakness W3; the figures W4 / W5 need). Everything it prints is recomputed from
the per-token records the summarizer already verified, and every identity below is exact arithmetic, not a fit."""
import json

import numpy as np
import pytest

from linear_ceiling import e9_tail
from tests.test_e9 import env, words  # noqa: F401  (pytest fixture + the synthetic encoder)
from tests.test_summarize_e9 import _retoken, ran  # noqa: F401  (pytest fixture)

NATIVE = 32768


def _run(ran):
    cfg, e7, report, runner = ran
    out = e9_tail.tail(cfg, runner=runner, encoder=words, e7=e7)
    return cfg, out


def test_tail_writes_pinned_outputs_with_the_registered_keys(ran):
    cfg, out = _run(ran)
    tj = json.loads((cfg.results_dir / "tail.json").read_text(encoding="utf-8"))
    assert tj == out
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    assert set(out["per_handoff"]) == set(rep["scores"])
    for key in ("summary_sha256", "report_sha256", "tau", "taus", "unit", "per_handoff", "pooled",
                "seam_left_bins", "position_bins", "native_window", "receiver_length"):
        assert key in out, key
    assert "R^2" in out["unit"] and "percent error" in out["unit"]
    md = (cfg.results_dir / "tail.md").read_text(encoding="utf-8")
    assert "R^2" in md and "oracle lower bound" not in md.lower()   # the tail does not restate f*


def test_bin_means_decompose_exactly_to_the_pooled_mean_and_to_one_minus_r2(ran):
    cfg, out = _run(ran)
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    for arm in ("same_K", "same_V"):
        pooled = out["pooled"][arm]
        rows = out["seam_left_bins"][arm]
        n = sum(r["n_tokens"] for r in rows)
        assert n == pooled["n_tokens"]
        recon = sum(r["n_tokens"] * r["mean"] for r in rows if r["n_tokens"]) / n
        assert recon == pytest.approx(pooled["mean"], rel=1e-9)
        for hid, ph in out["per_handoff"].items():
            r2 = rep["scores"][hid][f"{arm}_r2_layer_mean"]
            # float32 squares vs float64 moments: the summarizer's own sum tolerance (1e-5 relative)
            assert ph[arm]["mean"] == pytest.approx(1.0 - r2, rel=e9_tail._SUM_TOL)


def test_removed_top_means_and_exceedance_fractions_are_monotone(ran):
    cfg, out = _run(ran)
    taus = out["taus"]
    assert taus == sorted(taus, reverse=True)
    for ph in out["per_handoff"].values():
        k = ph["same_K"]
        assert k["mean"] >= k["mean_after_removing_top"]["0.10"] >= k["mean_after_removing_top"]["0.20"] >= 0.0
        fr = [k["fraction_over_tau"][str(t)] for t in taus]
        assert fr == sorted(fr)                       # a tighter tau can only add tokens over it
        assert 0.0 <= fr[0] <= fr[-1] <= 1.0
        assert k["delta_max"] >= k["mean"]


def test_native_window_subset_and_receiver_length_come_from_the_pairs(ran):
    cfg, out = _run(ran)
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    nw = out["native_window"]
    assert nw["cap"] == NATIVE and 0 < nw["n_tokens"] <= out["pooled"]["same_K"]["n_tokens"]
    assert nw["share_of_matched"] == pytest.approx(nw["n_tokens"] / out["pooled"]["same_K"]["n_tokens"])
    rl = out["receiver_length"]
    assert rl["n"] == len(rep["scores"]) and rl["p10"] <= rl["median"] <= rl["p90"]


def test_tail_refuses_whatever_the_summarizer_refuses(ran):
    cfg, e7, report, runner = ran
    rep = json.loads(report.read_text(encoding="utf-8"))
    hid = next(iter(rep["scores"]))

    def bump(z):
        z["same_K"] = z["same_K"] * 1.5
    _retoken(cfg, rep, hid, bump)
    report.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    with pytest.raises(ValueError, match="do not sum to the recorded SSE"):
        e9_tail.tail(cfg, runner=runner, encoder=words, e7=e7)
    assert not (cfg.results_dir / "tail.json").exists()
