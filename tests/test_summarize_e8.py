"""summarize_e8 refusals, on the fake-upstream fixture from test_e8."""
import json
import types

import pytest

from linear_ceiling import e8 as driver
from linear_ceiling import summarize_e8 as s8
from linear_ceiling.summarize_e8 import summarize
from tests.test_e8 import AGENT, env, fake_runner_factory  # noqa: F401  (pytest fixture, imported by name)


@pytest.fixture
def ran(env, tmp_path, monkeypatch):
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
    # the summarizer checks the upstream HEAD; the fake upstream has no git
    monkeypatch.setattr(s8.subprocess, "run", lambda *a, **k: types.SimpleNamespace(stdout=cfg.upstream_sha + "\n", returncode=0))
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


def test_refuses_moved_upstream_head(ran, monkeypatch):
    cfg, _, runner = ran
    monkeypatch.setattr(s8.subprocess, "run", lambda *a, **k: types.SimpleNamespace(stdout="b" * 40 + "\n", returncode=0))
    with pytest.raises(ValueError, match="upstream HEAD"):
        summarize(cfg, runner=runner)
