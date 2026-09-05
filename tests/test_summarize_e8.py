"""summarize_e8 refusals, on the fake-upstream fixture from test_e8."""
import json
import types

import pytest

from linear_ceiling import e8 as driver
from linear_ceiling import summarize_e8 as s8
from linear_ceiling.summarize_e8 import summarize
from tests.test_e8 import AGENT, AGENT_ALL, N_SEQS, cfg_for, env, fake_runner_factory  # noqa: F401  (pytest fixture, imported by name)


@pytest.fixture
def ran(env, tmp_path, monkeypatch):
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
    # the summarizer checks the upstream pin via check_upstream; the fake upstream has no git
    monkeypatch.setattr(s8, "check_upstream", lambda *a, **k: None)
    return cfg, tmp_path / "results" / "e8" / "report.json", runner


def _write(p, obj):
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def test_clean_report_summarizes(ran):
    cfg, _, runner = ran
    md = summarize(cfg, runner=runner)
    assert "verdict-bearing k=1" in md and "K **UNRESOLVED** / V **UNRESOLVED**" in md
    assert "verdict on H-E8 is NOT stated" in md
    assert (cfg.results_dir / "recheck" / "agent_k1.json").exists()


def test_refuses_edited_agent_r2(ran):
    cfg, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["per_k"]["1"]["agent"]["K"] = 0.68            # "no drop"
    rep["per_k"]["1"]["drop"]["K"] = 0.0
    rep["per_k"]["1"]["band_outcome"]["K"] = "HOLDS"
    rep["verdict_bearing"]["outcome"] = "HOLDS"
    _write(rp, rep)
    with pytest.raises(ValueError, match="k=1 agent.K"):
        summarize(cfg, runner=runner)


def test_refuses_band_outcome_relabelled(ran):
    cfg, rp, runner = ran
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["per_k"]["1"]["band_outcome"]["K"] = "HOLDS"
    _write(rp, rep)
    with pytest.raises(ValueError, match="band outcome"):
        summarize(cfg, runner=runner)


def test_refuses_when_the_scorer_now_disagrees(ran):
    """The dumps are unchanged but the upstream scorer returns something else: refuse."""
    cfg, _, _ = ran
    drifted = fake_runner_factory(agent={k: (K + 0.02, V) for k, (K, V) in AGENT.items()})
    with pytest.raises(ValueError, match="recomputed"):
        summarize(cfg, runner=drifted)


def test_refuses_changed_dump_bytes(ran):
    cfg, _, runner = ran
    (cfg.agent_dumps / "source" / "K.bin").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="agent/source dump does not match"):
        summarize(cfg, runner=runner)


def test_refuses_changed_token_file(ran):
    cfg, _, runner = ran
    tok = next(cfg.tokens_dir.glob("*.npy"))
    tok.write_bytes(tok.read_bytes() + b"\0")
    with pytest.raises(ValueError, match="token file missing or changed"):
        summarize(cfg, runner=runner)


def test_refuses_config_drift(ran):
    cfg, _, runner = ran
    cfg.config_path.write_text("# changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config_sha256"):
        summarize(cfg, runner=runner)


def test_refuses_a_broken_upstream_pin(ran, monkeypatch):
    """check_upstream's refusal (not an ancestor / changed paths / dirty) surfaces as a refusal."""
    cfg, _, runner = ran

    def broken(*a, **k):
        raise RuntimeError("E8 summary REFUSED: pinned upstream commit deadbeef is not an ancestor of HEAD")
    monkeypatch.setattr(s8, "check_upstream", broken)
    with pytest.raises(ValueError, match="not an ancestor"):
        summarize(cfg, runner=runner)


@pytest.fixture
def ran_amendment(ran, tmp_path):
    cfg, _, runner = ran
    acfg = cfg_for(tmp_path, cfg.upstream_path, amendment=True)
    from tests.test_e8 import E7Config
    e7 = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r7", pricing={}, thresholds={},
                  tokenizer={}, lane_b_policy="x", config_path=tmp_path / "c7")
    driver.run(acfg, e7, repo_root=tmp_path, runner=runner)
    return acfg, acfg.results_dir / "report.json", runner


def test_amendment_summary_recomputes_per_sequence_and_bootstraps(ran_amendment):
    """Entry 0030: per-sequence R^2 recomputed from the per-token record and checked against the report; a
    seeded bootstrap over agent sequences; the change from the 0016-protocol figure named."""
    acfg, _, runner = ran_amendment
    md = summarize(acfg, runner=runner)
    assert "E8 amendment (entry 0030)" in md and "does not move" in md.lower() or "decided by 0020" in md
    fig = json.loads((acfg.results_dir / "summary.json").read_text(encoding="utf-8"))
    k1 = fig["per_k"]["1"]
    assert k1["n_heldout_seqs"]["agent"] == N_SEQS and k1["per_sequence"]["agent_K"]["n"] == N_SEQS
    assert k1["change_from_prior"] == pytest.approx({"K": 0.61 - 0.60, "V": 0.44 - 0.45})
    b = k1["bootstrap"]["K"]
    assert b["reps"] == 50 and b["n_seqs"] == N_SEQS and b["agent_lower_2.5"] <= 0.61 <= b["agent_upper_97.5"] + 1e-12
    # the per-sequence R^2 equals the pooled one by construction of the synthetic record
    assert k1["per_sequence"]["agent_K"]["median"] == pytest.approx(0.61)


def test_amendment_summary_refuses_a_tampered_per_sequence_list(ran_amendment):
    acfg, rp, runner = ran_amendment
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["per_k"]["1"]["per_sequence"]["agent"]["K"][0] += 0.01
    _write(rp, rep)
    with pytest.raises(ValueError, match="per-sequence K"):
        summarize(acfg, runner=runner)


def test_amendment_summary_refuses_when_the_prior_report_changed(ran_amendment, tmp_path):
    acfg, rp, runner = ran_amendment
    prior = tmp_path / "results" / "e8" / "report.json"
    d = json.loads(prior.read_text(encoding="utf-8")); d["scope"] = "edited"
    _write(prior, d)
    with pytest.raises(ValueError, match="prior E8 report"):
        summarize(acfg, runner=runner)
