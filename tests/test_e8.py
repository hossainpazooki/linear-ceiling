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
AGENT_ALL = {"1": (0.61, 0.44), "4": (0.31, 0.09)}   # canned arm (b) at --holdout-frac 1.0 (E8 amendment)
N_SEQS, PER_SEQ, N_LAYERS, N_KV = 5, 4, 2, 2


def per_seq_record(K: float, V: float, n_seqs: int, seed: int) -> dict:
    """Synthetic per-sequence moments whose pooled per-head R^2 is exactly (K, V) on every head: sst_s drawn
    positive, sse_s = (1 - r2) * sst_s. seq-level R^2 then equals the pooled one; a jitter on sse keeps the
    sequences distinguishable while the layer-mean stays K/V (compensated within each sequence pair)."""
    rng = np.random.default_rng(seed)
    out = {}
    for key, r2 in (("K", K), ("V", V)):
        sst = rng.uniform(1.0, 2.0, size=(n_seqs, N_LAYERS, N_KV))
        sse = (1.0 - r2) * sst
        out[f"sst_seq_{key}"] = sst
        out[f"sse_seq_{key}"] = sse
    out["seq_ids"] = np.arange(n_seqs, dtype=np.int64)
    out["seq_idx"] = np.repeat(np.arange(n_seqs), PER_SEQ).astype(np.int64)
    return out


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


def fake_runner_factory(agent=AGENT, generic=ARCHIVED, calls=None, agent_all=AGENT_ALL):
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
            is_generic = "data" in opt["--src"].replace("\\", "/").split("/")
            frac = float(opt.get("--holdout-frac", "0.2"))
            if is_generic:
                K, V = generic[k]["K_r2_heldout_layer_mean"], generic[k]["V_r2_heldout_layer_mean"]
            else:
                K, V = (agent_all if frac >= 1.0 else agent)[k]
            n_seqs = N_SEQS if frac >= 1.0 else max(1, int(np.ceil(frac * N_SEQS)))
            rec = {"k": int(k), "K_r2_heldout_layer_mean": K, "V_r2_heldout_layer_mean": V,
                   "K_r2_train_layer_mean": None if frac >= 1.0 else K, "V_r2_train_layer_mean": None if frac >= 1.0 else V,
                   "holdout_frac": frac, "n_heldout_seqs": n_seqs, "n_heldout_tokens": n_seqs * PER_SEQ}
            if "--per-token" in opt:
                pt = Path(opt["--per-token"])
                pt.parent.mkdir(parents=True, exist_ok=True)
                arrays = per_seq_record(K, V, n_seqs, seed=int(k) * 7 + (0 if is_generic else 1))
                np.savez(pt, **arrays)
                rec["per_sequence"] = {"seq_ids": [int(i) for i in arrays["seq_ids"]],
                                       "K_r2_layer_mean": [float(x) for x in (1 - arrays["sse_seq_K"] / arrays["sst_seq_K"]).mean((1, 2))],
                                       "V_r2_layer_mean": [float(x) for x in (1 - arrays["sse_seq_V"] / arrays["sst_seq_V"]).mean((1, 2))]}
            out = Path(opt["--out"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(rec), encoding="utf-8")
        else:
            raise AssertionError(f"unexpected upstream call {cmd}")
        return types.SimpleNamespace(returncode=0, stderr=b"")
    return runner


def cfg_for(tmp_path, up, sha="a" * 40, report_k=(1, 4), amendment=False):
    cp = tmp_path / ("e8a.toml" if amendment else "e8.toml")
    cp.write_text("# synthetic e8a\n" if amendment else "# synthetic e8\n", encoding="utf-8")
    extra = {}
    if amendment:   # E8 amendment: reuse the prior run's agent dumps by fingerprint, score every agent sequence
        extra = dict(agent_holdout_frac=1.0, reuse_agent_dumps_from=tmp_path / "results" / "e8" / "report.json",
                     amendment={"entry": "0030", "bootstrap_seed": 30, "bootstrap_reps": 50})
    return E8Config(pair=PAIR, results_dir=tmp_path / "results" / ("e8a" if amendment else "e8"),
                    tokens_dir=tmp_path / "data" / "e8",
                    upstream_path=up, upstream_sha=sha, verdict_k=1, report_k=report_k,
                    generic_dumps=f"data/kv/{PAIR}", agent_dumps=tmp_path / "results" / "e8" / "kv" / "agent",
                    holdout_frac=0.2, stride=4,
                    text={"seed": 8, "n_seqs": 2, "seq_len": 4, "suites": ["tau2-bench", "swe-bench"], "window": "first"},
                    band={"holds_max_drop": 0.05, "degrades_min_drop": 0.15}, config_path=cp, **extra)


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
    assert rep["verdict_bearing"]["k"] == 1
    assert rep["verdict_bearing"]["outcome"] == {"K": "UNRESOLVED", "V": "UNRESOLVED"}
    assert "neither alone" in rep["verdict_bearing"]["note"]
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


def test_amendment_reuses_the_prior_dumps_by_fingerprint_and_records_per_sequence(env, tmp_path):
    """E8 amendment (entry 0030): after a normal run, the amendment run re-dumps nothing, scores arm (b) with
    --holdout-frac 1.0 and both arms with --per-token, records hold-out fractions, counts, per-sequence lists
    and the per-token record hashes, and names the prior report it reused."""
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
    acfg = cfg_for(tmp_path, cfg.upstream_path, amendment=True)
    calls.clear()
    out = driver.run(acfg, e7, repo_root=tmp_path, runner=runner)
    scripts = [c[1] for c in calls]
    assert scripts.count("scripts/dump_kv.py") == 0 and scripts.count("scripts/score_mapper.py") == 4
    fracs = {(c[c.index("--src") + 1].replace("\\", "/").split("/")[-2], c[c.index("--holdout-frac") + 1]) for c in calls}
    assert ("agent", "1.0") in fracs and all("--per-token" in c for c in calls)
    rep = json.loads(out.read_text(encoding="utf-8"))
    row = rep["per_k"]["1"]
    assert row["holdout_frac"] == {"generic": 0.2, "agent": 1.0}
    assert row["n_heldout_seqs"]["agent"] == N_SEQS and row["agent"] == {"K": 0.61, "V": 0.44}
    assert len(row["per_sequence"]["agent"]["K"]) == N_SEQS and (tmp_path / "results" / "e8a" / row["per_token"]["agent"]["path"].split("results/e8a/")[-1]).exists()
    assert rep["reused_agent_dumps_from"]["report"].endswith("results/e8/report.json")
    assert "does not move here" in rep["verdict_bearing"]["note"] and rep["amendment"]["entry"] == "0030"


def test_amendment_refuses_dumps_that_do_not_match_the_prior_report(env, tmp_path):
    cfg, e7, calls, runner = env
    driver.run(cfg, e7, repo_root=tmp_path, runner=runner)
    (cfg.agent_dumps / "source" / "K.bin").write_bytes(b"tampered")
    acfg = cfg_for(tmp_path, cfg.upstream_path, amendment=True)
    with pytest.raises(RuntimeError, match="does not match the fingerprint recorded"):
        driver.run(acfg, e7, repo_root=tmp_path, runner=runner)


def test_amendment_gate_requires_its_own_entry(tmp_path):
    acfg = cfg_for(tmp_path, tmp_path / "up", amendment=True)
    assert driver.required_entries(acfg) == ("### 0009 ", "### 0016 ", "### 0030 ")
    assert driver.required_entries(cfg_for(tmp_path, tmp_path / "up")) == ("### 0009 ", "### 0016 ")
