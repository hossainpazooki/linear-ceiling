"""E9 driver on a fake upstream and a synthetic composio corpus (offline, no models)."""
import hashlib
import json
import types
from pathlib import Path

import numpy as np
import pytest

from linear_ceiling import e9 as driver
from linear_ceiling.config import E7Config, E9Config
from linear_ceiling.e9 import _stem, keep_subset
from tests.test_e7_corpus import COMPOSIO

PAIR = "qwen3-0.6b-to-1.7b"
L, H = 2, 2

# two layers x two heads of canned moments; r2 per head = 1 - sse/sst
_LAYER = {"sse": [1.0, 1.0], "sst": [4.0, 2.0], "r2_head_mean": (0.75 + 0.5) / 2}
_MEAN = _LAYER["r2_head_mean"]
RULE = {"statistic": "median f*(tau_K)", "holds_max": 0.15, "degrades_min": 0.50, "tau_K": 0.25, "tau_V": 0.40,
        "tau_ladder": [0.10, 0.03]}     # entry 0025: descriptive ladder, strictly decreasing, below tau_K
CONTROLS = {"null_seed": 23, "seam_bins": [0, 1, 2, 4, 8, 16]}


def canned_scores(shift=0.0, cross=True):
    def block():
        return {"K": [dict(_LAYER), dict(_LAYER)], "V": [dict(_LAYER), dict(_LAYER)]}
    rec = {"same": block(), "same_K_r2_layer_mean": _MEAN + shift, "same_V_r2_layer_mean": _MEAN + shift}
    if cross:
        rec.update({"cross": block(), "cross_K_r2_layer_mean": _MEAN + shift, "cross_V_r2_layer_mean": _MEAN + shift})
    return rec


def per_token_arrays(n, cross=True, zero=False):
    """Squares whose float64 token-sums equal the canned SSE (1.0 per layer-head), with a
    deterministic per-token spread so f* and the seam profile have content."""
    w = 1.0 + (np.arange(n) % 3)
    base = (w / w.sum())[:, None, None] * np.ones((n, L, H))
    arrays = {"ref_K": np.ones((n, L, H), np.float32), "ref_V": np.ones((n, L, H), np.float32)}
    for arm in (["same_K", "same_V"] + (["cross_K", "cross_V"] if cross else [])):
        arrays[arm] = (np.zeros((n, L, H)) if zero else base).astype(np.float32)
    return arrays


def fake_runner_factory(calls=None, recheck_shift=0.0, identity_nonzero=False):
    def runner(cmd, cwd, capture_output):
        if calls is not None:
            calls.append(cmd)
        args = cmd[1:]
        opt = {args[i]: args[i + 1] for i in range(1, len(args) - 1, 2)}
        if args[0].endswith("dump_kv.py"):
            out = Path(opt["--out"])
            out.mkdir(parents=True, exist_ok=True)
            toks = np.load(opt["--tokens"])
            (out / "meta.json").write_text(json.dumps({"n_seqs": 1, "stride": 1}), encoding="utf-8")
            (out / "kv.bin").write_bytes(toks.tobytes() + opt["--which"].encode())
        elif args[0].endswith("score_positions.py"):
            pairs = np.load(opt["--pairs"])["pairs"]
            n = int(pairs.shape[0])
            cross = "--cross-src" in opt
            identity = opt["--same-tgt"] == opt["--same-src"]
            shift = recheck_shift if "recheck" in opt["--out"].replace("\\", "/") else 0.0
            rec = canned_scores(shift, cross=cross)
            arrays = per_token_arrays(n, cross=cross, zero=identity and not identity_nonzero)
            if identity and not identity_nonzero:
                for part in rec["same"].values():
                    for layer in part:
                        layer["sse"] = [0.0, 0.0]
                        layer["r2_head_mean"] = 1.0
                rec["same_K_r2_layer_mean"] = rec["same_V_r2_layer_mean"] = 1.0
            rec["n_pairs"] = n
            rec["seconds"] = 0.1
            pt = Path(opt["--per-token"])
            pt.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(pt, **arrays)
            rec["per_token"] = {"path": pt.name, "sha256": hashlib.sha256(pt.read_bytes()).hexdigest()}
            Path(opt["--out"]).parent.mkdir(parents=True, exist_ok=True)
            Path(opt["--out"]).write_text(json.dumps(rec), encoding="utf-8")
        else:
            raise AssertionError(f"unexpected upstream call {cmd}")
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
                   keep_seed=9, keep_n=1, rule=dict(RULE), controls=dict(CONTROLS), config_path=cp)
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


def test_keep_subset_redraw_at_a_larger_n_is_not_nested():
    """Entry 0025 raises n; numpy's choice without replacement is NOT nested across sizes, so the
    entry states the new set explicitly instead of calling it 'the old three plus five'."""
    ids = [f"h{i}" for i in range(25)]
    small, big = keep_subset(ids, 9, 3), keep_subset(ids, 9, 8)
    assert len(big) == 8 and big == sorted(big)
    assert not set(small) <= set(big)


@pytest.mark.parametrize("ladder,msg", [
    ([], "tau_ladder"), ([0.10, 0.10], "tau_ladder"), ([0.03, 0.10], "tau_ladder"),
    ([0.40, 0.03], "tau_ladder"), ([0.10, 0.0], "tau_ladder"), ("0.1", "tau_ladder")])   # 0.40 > tau_K 0.3186
def test_config_refuses_a_malformed_tau_ladder(tmp_path, ladder, msg):
    """Entry 0025: the ladder must be strictly decreasing and strictly inside (0, tau_K)."""
    import json as _json
    from linear_ceiling import REPO_ROOT
    from linear_ceiling.config import load_e9_config
    src = (REPO_ROOT / "config" / "e9.toml").read_text(encoding="utf-8")
    assert "tau_ladder = [0.10, 0.03]" in src
    bad = src.replace("tau_ladder = [0.10, 0.03]", f"tau_ladder = {_json.dumps(ladder)}")
    p = tmp_path / "e9.toml"
    p.write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, tmp_path)
    ok = tmp_path / "ok.toml"
    ok.write_text(src, encoding="utf-8")
    assert load_e9_config(ok, tmp_path).rule["tau_ladder"] == [0.10, 0.03]


def test_stem_is_filesystem_safe():
    assert _stem("20241016_x/a_traj#3") == "20241016_x__a_traj_sw3"


def test_run_scores_included_counts_excluded_and_runs_controls(env, tmp_path):
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
    # the per-token record travels with the score and is hashed in the report
    tok = cfg.results_dir / "tokens" / rec["tokens_file"]
    assert tok.exists() and hashlib.sha256(tok.read_bytes()).hexdigest() == rec["tokens_sha256"]
    # controls ran on the (only) included handoff, before its scoring
    ctl = rep["controls"]
    assert ctl["handoff_id"] == hid and ctl["identity"]["max_abs_square"] == 0.0
    assert ctl["null"]["seed"] == 23 and (cfg.results_dir / "controls" / ctl["null"]["pairs_file"]).exists()
    scripts = [c[1] for c in calls]
    # three dumps; three scorings: identity, null, the handoff itself -- in that order
    assert scripts.count("scripts/dump_kv.py") == 3 and scripts.count("scripts/score_positions.py") == 3
    outs = [c[c.index("--out") + 1].replace("\\", "/") for c in calls if c[1] == "scripts/score_positions.py"]
    assert outs[0].endswith("controls/identity.json") and outs[1].endswith("controls/null.json")
    assert "--per-token" in calls[-1] and "--cross-src" in calls[-1] and "--cross-src" not in calls[3]
    dump = next(c for c in calls if c[1] == "scripts/dump_kv.py")
    assert dump[dump.index("--stride") + 1] == "1"


def test_identity_control_halts_the_run(env, tmp_path):
    cfg, e7, _, _ = env
    bad = fake_runner_factory(identity_nonzero=True)
    with pytest.raises(RuntimeError, match="HALTED: pipeline identity control is nonzero"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=bad, encoder=words)
    assert not (cfg.results_dir / "scores").exists()          # nothing scored after the halt


def test_run_deletes_unkept_dumps(env, tmp_path):
    cfg, e7, calls, runner = env
    cfg = cfg.__class__(**{**cfg.__dict__, "keep_n": 0})
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(out.read_text(encoding="utf-8"))
    (hid, rec), = rep["scores"].items()
    assert "kept_dumps" not in rec
    assert not (cfg.scratch_dir / _stem(hid)).exists()
    assert (cfg.results_dir / "scores" / rec["score_file"]).exists()   # scores always survive


def test_assert_ready_refuses_the_pending_pin_placeholder(env, tmp_path, monkeypatch):
    cfg, _, _, _ = env
    monkeypatch.undo()
    cfg = cfg.__class__(**{**cfg.__dict__, "upstream_sha": "UPSTREAM_SHA_PENDING_0023"})
    with pytest.raises(RuntimeError, match="pending upstream pin placeholder"):
        driver.assert_ready(cfg, tmp_path)
