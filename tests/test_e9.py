"""E9 driver on a fake upstream and a synthetic composio corpus (offline, no models)."""
import json

import numpy as np
import pytest

from linear_ceiling import e9 as driver
from linear_ceiling.config import E7Config, E9Config
from linear_ceiling.e9 import _stem, keep_subset
from tests.test_e7_corpus import COMPOSIO

PAIR = "qwen3-0.6b-to-1.7b"

# two layers x two heads of canned moments; r2 per head = 1 - sse/sst
_LAYER = {"sse": [1.0, 1.0], "sst": [4.0, 2.0], "r2_head_mean": (0.75 + 0.5) / 2}
_MEAN = _LAYER["r2_head_mean"]


def canned_scores(shift=0.0):
    def block():
        return {"K": [dict(_LAYER), dict(_LAYER)], "V": [dict(_LAYER), dict(_LAYER)]}
    return {"same": block(), "cross": block(),
            "same_K_r2_layer_mean": _MEAN + shift, "same_V_r2_layer_mean": _MEAN + shift,
            "cross_K_r2_layer_mean": _MEAN + shift, "cross_V_r2_layer_mean": _MEAN + shift}


def fake_runner_factory(calls=None, recheck_shift=0.0):
    def runner(cmd, cwd, capture_output):
        if calls is not None:
            calls.append(cmd)
        args = cmd[1:]
        opt = {args[i]: args[i + 1] for i in range(1, len(args) - 1, 2)}
        from pathlib import Path
        if args[0].endswith("dump_kv.py"):
            out = Path(opt["--out"])
            out.mkdir(parents=True, exist_ok=True)
            toks = np.load(opt["--tokens"])
            (out / "meta.json").write_text(json.dumps({"n_seqs": 1, "stride": 1}), encoding="utf-8")
            (out / "kv.bin").write_bytes(toks.tobytes() + opt["--which"].encode())
        elif args[0].endswith("score_positions.py"):
            pairs = np.load(opt["--pairs"])["pairs"]
            rec = canned_scores(recheck_shift if "recheck" in opt["--out"].replace("\\", "/") else 0.0)
            rec["n_pairs"] = int(pairs.shape[0])
            rec["seconds"] = 0.1
            Path(opt["--out"]).parent.mkdir(parents=True, exist_ok=True)
            Path(opt["--out"]).write_text(json.dumps(rec), encoding="utf-8")
        else:
            raise AssertionError(f"unexpected upstream call {cmd}")
        import types
        return types.SimpleNamespace(returncode=0, stderr=b"")
    return runner


def words(text):
    return [hash(w) % 997 for w in text.split()]


def write_traces(root):
    sub = root / "swe-bench" / "20241016_composio_x"
    sub.mkdir(parents=True)
    (sub / "a_traj.json").write_text(json.dumps(COMPOSIO), encoding="utf-8")
    big = [[COMPOSIO[0][0], {"id": ["l", "s", "m", "AIMessage"],
                             "kwargs": {"content": "w " * 300, "type": "ai",
                                        "response_metadata": {"model_id": "claude-a"}}}],
           COMPOSIO[1]]
    (sub / "b_traj.json").write_text(json.dumps(big), encoding="utf-8")   # |S| over a small cap
    return sub


@pytest.fixture
def env(tmp_path, monkeypatch):
    write_traces(tmp_path / "traces")
    up = tmp_path / "up"
    (up / ".venv" / "Scripts").mkdir(parents=True)
    (up / ".venv" / "Scripts" / "python.exe").write_text("", encoding="utf-8")
    (up / "mappers" / PAIR).mkdir(parents=True)
    cp = tmp_path / "e9.toml"
    cp.write_text("# synthetic e9\n", encoding="utf-8")
    cfg = E9Config(pair=PAIR, results_dir=tmp_path / "results" / "e9",
                   scratch_dir=tmp_path / "results" / "e9" / "scratch", upstream_path=up,
                   upstream_sha="a" * 40, suite="swe-bench", agent="composio", context_cap=100,
                   alignment_method="difflib blocks", mapper_k=1, mapper_space="content",
                   keep_seed=9, keep_n=1, band={"holds_min": 0.70, "degrades_max": 0.40},
                   config_path=cp)
    e7 = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r7", pricing={},
                  thresholds={}, tokenizer={}, lane_b_policy="x", config_path=tmp_path / "c7")
    monkeypatch.setattr(driver, "assert_ready", lambda *a, **k: None)
    calls = []
    return cfg, e7, calls, fake_runner_factory(calls=calls)


def test_keep_subset_is_seeded_and_sorted():
    ids = [f"h{i}" for i in range(10)]
    a = keep_subset(list(reversed(ids)), 9, 3)
    assert a == keep_subset(ids, 9, 3) and len(a) == 3 and a == sorted(a)
    assert keep_subset(ids, 10, 3) != a
    assert keep_subset(["x"], 9, 3) == ["x"]


def test_stem_is_filesystem_safe():
    assert _stem("20241016_x/a_traj#3") == "20241016_x__a_traj_sw3"


def test_run_scores_included_and_counts_excluded(env, tmp_path):
    cfg, e7, calls, runner = env
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["complete"] is True
    assert rep["coverage"] == {"observed": 2, "included": 1, "excluded": 1}
    excluded = next(a for a in rep["alignments"] if a["excluded"])
    assert "exceeds context cap" in excluded["reason"] and excluded["n_sender"] > 100
    (hid, rec), = rep["scores"].items()
    assert rec["n_pairs"] > 0 and rec["same_K_r2_layer_mean"] == pytest.approx(_MEAN)
    assert rep["keep_subset"] == [hid] and "kept_dumps" in rec
    assert set(rec["kept_dumps"]) == {"same_src", "same_tgt", "cross_src"}
    # three dumps + one scoring per included handoff
    scripts = [c[1] for c in calls]
    assert scripts.count("scripts/dump_kv.py") == 3 and scripts.count("scripts/score_positions.py") == 1
    dump = next(c for c in calls if c[1] == "scripts/dump_kv.py")
    assert dump[dump.index("--stride") + 1] == "1"


def test_run_deletes_unkept_dumps(env, tmp_path):
    cfg, e7, calls, runner = env
    cfg = cfg.__class__(**{**cfg.__dict__, "keep_n": 0})
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(out.read_text(encoding="utf-8"))
    (hid, rec), = rep["scores"].items()
    assert "kept_dumps" not in rec
    assert not (cfg.scratch_dir / _stem(hid)).exists()
    assert (cfg.results_dir / "scores" / rec["score_file"]).exists()   # scores always survive
