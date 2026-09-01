"""E8 gate, band, cross-check and driver assembly -- with a fake upstream (offline, no models)."""
import json
import types

import numpy as np
import pytest

from linear_ceiling import e8 as driver
from linear_ceiling.config import E7Config, E8Config
from linear_ceiling.e8 import assemble, band_outcome, crosscheck, upstream_python
from linear_ceiling.e8_text import TraceText

PAIR = "qwen3-0.6b-to-1.7b"
ARCHIVED = {"1": {"K_r2_heldout_layer_mean": 0.6813557346883706, "V_r2_heldout_layer_mean": 0.5132943500944008},
            "4": {"K_r2_heldout_layer_mean": 0.5906939844474344, "V_r2_heldout_layer_mean": 0.33614564065248614}}
AGENT = {"1": (0.60, 0.45), "4": (0.30, 0.10)}       # canned arm (b): k=1 drop 0.081 (UNRESOLVED), k=4 DEGRADES


def make_upstream(tmp_path, sha="a" * 40):
    up = tmp_path / "up"
    (up / ".venv" / "Scripts").mkdir(parents=True)
    (up / ".venv" / "Scripts" / "python.exe").write_text("", encoding="utf-8")
    for k in ("1", "4"):
        d = up / "mappers" / PAIR
        d.mkdir(parents=True, exist_ok=True)
        (d / f"k{k}.safetensors").write_bytes(b"\0")
        (d / f"k{k}.json").write_text("{}", encoding="utf-8")
    r = up / "results" / "mapper" / PAIR
    r.mkdir(parents=True)
    (r / "r2.json").write_text(json.dumps({"k": ARCHIVED}), encoding="utf-8")
    for w in ("source", "target"):
        d = up / "data" / "kv" / PAIR / w
        d.mkdir(parents=True)
        (d / "meta.json").write_text(json.dumps({"n_seqs": 50, "stride": 4}), encoding="utf-8")
        (d / "K.bin").write_bytes(b"generic" + w.encode())
    return up


def fake_runner_factory(agent=AGENT, generic=ARCHIVED, calls=None):
    def runner(cmd, cwd, capture_output):
        if calls is not None:
            calls.append(cmd)
        args = cmd[1:]
        script = args[0]
        opt = {args[i]: args[i + 1] for i in range(1, len(args) - 1, 2)}
        if script.endswith("dump_kv.py"):
            from pathlib import Path
            out = Path(opt["--out"])
            out.mkdir(parents=True, exist_ok=True)
            (out / "meta.json").write_text(json.dumps({"n_seqs": int(np.load(opt["--tokens"]).shape[0]),
                                                      "stride": int(opt["--stride"])}), encoding="utf-8")
            (out / "K.bin").write_bytes(b"agent" + opt["--which"].encode())
        elif script.endswith("score_mapper.py"):
            from pathlib import Path
            k = opt["--mapper"].rsplit("k", 1)[-1]
            src = generic if "data" in opt["--src"].replace("\\", "/").split("/") else None
            if src is not None:
                K, V = generic[k]["K_r2_heldout_layer_mean"], generic[k]["V_r2_heldout_layer_mean"]
            else:
                K, V = agent[k]
            out = Path(opt["--out"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"k": int(k), "K_r2_heldout_layer_mean": K, "V_r2_heldout_layer_mean": V,
                                       "K_r2_train_layer_mean": K, "V_r2_train_layer_mean": V}), encoding="utf-8")
        else:
            raise AssertionError(f"unexpected upstream call {cmd}")
        return types.SimpleNamespace(returncode=0, stderr=b"")
    return runner


def cfg_for(tmp_path, up, sha="a" * 40, report_k=(1, 4)):
    cp = tmp_path / "e8.toml"
    cp.write_text("# synthetic e8\n", encoding="utf-8")
    return E8Config(pair=PAIR, results_dir=tmp_path / "results" / "e8", tokens_dir=tmp_path / "data" / "e8",
                    upstream_path=up, upstream_sha=sha, verdict_k=1, report_k=report_k,
                    generic_dumps=f"data/kv/{PAIR}", agent_dumps=tmp_path / "results" / "e8" / "kv" / "agent",
                    holdout_frac=0.2, stride=4,
                    text={"seed": 8, "n_seqs": 2, "seq_len": 4, "suites": ["tau2-bench", "swe-bench"], "window": "first"},
                    band={"holds_max_drop": 0.05, "degrades_min_drop": 0.15}, config_path=cp)


@pytest.fixture
def env(tmp_path, monkeypatch):
    up = make_upstream(tmp_path)
    cfg = cfg_for(tmp_path, up)
    e7 = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r7", pricing={}, thresholds={},
                  tokenizer={}, lane_b_policy="x", config_path=tmp_path / "c7")
    monkeypatch.setattr(driver, "assert_ready", lambda *a, **k: None)
    monkeypatch.setattr(driver, "snapshot", lambda mid: tmp_path / "snap")
    monkeypatch.setattr(driver, "WeightReader", lambda d, m: (d, m))
    monkeypatch.setattr(driver, "assert_shared_vocab", lambda a, b: None)
    monkeypatch.setattr(driver, "qwen_encoder", lambda snap: (lambda text: [hash(w) % 100 for w in text.split()]))
    monkeypatch.setattr(driver, "iter_trace_texts", lambda e7cfg, suites: [
        TraceText("tau2-bench", "a", "w " * 10), TraceText("swe-bench", "b", "w " * 10)])
    calls = []
    return cfg, e7, calls, fake_runner_factory(calls=calls)


def test_band_outcome_edges():
    band = {"holds_max_drop": 0.05, "degrades_min_drop": 0.15}
    assert band_outcome(0.05, band) == "HOLDS" and band_outcome(-0.2, band) == "HOLDS"
    assert band_outcome(0.15, band) == "DEGRADES" and band_outcome(0.0501, band) == "UNRESOLVED"


def test_gate_refuses_a_placeholder_sha_before_touching_git(tmp_path):
    cfg = cfg_for(tmp_path, tmp_path / "nope", sha="TBD")
    with pytest.raises(RuntimeError, match="not a commit sha"):
        driver.assert_ready(cfg, tmp_path)


def test_upstream_python_must_exist(tmp_path):
    with pytest.raises(RuntimeError, match="no interpreter"):
        upstream_python(tmp_path)
    assert upstream_python(make_upstream(tmp_path)).name == "python.exe"


def test_crosscheck_refuses_disagreement():
    rec = {"K_r2_heldout_layer_mean": 0.68, "V_r2_heldout_layer_mean": 0.51}
    with pytest.raises(RuntimeError, match="not what r2.json describes"):
        crosscheck(1, rec, ARCHIVED["1"])
    ok = crosscheck(1, dict(ARCHIVED["1"]), ARCHIVED["1"])
    assert ok["K_r2_heldout_layer_mean"]["archived"] == ok["K_r2_heldout_layer_mean"]["recomputed"]


def test_run_end_to_end_with_fake_upstream(env, tmp_path):
    cfg, e7, calls, runner = env
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
    rep = json.loads(out.read_text(encoding="utf-8"))
    scripts = [c[1] for c in calls]
    assert scripts.count("scripts/dump_kv.py") == 2 and scripts.count("scripts/score_mapper.py") == 4
    assert rep["per_k"]["1"]["band_outcome"] == {"K": "UNRESOLVED", "V": "UNRESOLVED"}
    assert rep["per_k"]["4"]["band_outcome"]["K"] == "DEGRADES"
    assert rep["verdict_bearing"] == {"k": 1, "readout": "K", "outcome": "UNRESOLVED",
                                      "note": "band outcome only; the verdict on H-E8 enters by a numbered entry"}
    assert rep["per_k"]["1"]["drop"]["K"] == pytest.approx(0.6813557346883706 - 0.60)
    assert set(rep["dumps"]["agent"]["source"]) == {"meta.json", "K.bin"}
    assert rep["tokens"]["sha256"] and (tmp_path / "data" / "e8").glob("*.npy")
    # the dump command carried the registered stride and an absolute token path
    dump = next(c for c in calls if c[1] == "scripts/dump_kv.py")
    assert "--stride" in dump and dump[dump.index("--stride") + 1] == "4"


def test_run_refuses_when_archived_disagrees(env, tmp_path):
    cfg, e7, calls, _ = env
    bad = {k: {"K_r2_heldout_layer_mean": v["K_r2_heldout_layer_mean"] + 0.01,
               "V_r2_heldout_layer_mean": v["V_r2_heldout_layer_mean"]} for k, v in ARCHIVED.items()}
    with pytest.raises(RuntimeError, match="not what r2.json describes"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=fake_runner_factory(generic=bad, calls=calls))


def test_run_refuses_missing_mapper(env, tmp_path):
    cfg, e7, calls, runner = env
    (cfg.upstream_path / "mappers" / PAIR / "k4.safetensors").unlink()
    with pytest.raises(RuntimeError, match="no fitted mapper"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=runner)


def test_run_refuses_missing_generic_dump(env, tmp_path):
    cfg, e7, calls, runner = env
    (cfg.upstream_path / "data" / "kv" / PAIR / "target" / "meta.json").unlink()
    with pytest.raises(RuntimeError, match="archived generic dump missing"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
