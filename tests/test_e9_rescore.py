"""Entry 0033: the E9 kept-subset re-score with a tagged mapper -- offline, fake upstream, synthetic tensors.
The same-model arm is a control (must reproduce 0028's recheck record); the cross arm is what changes."""
import json
import types
from pathlib import Path

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling import e9_rescore as m
from linear_ceiling.config import E9RescoreConfig, load_e9_rescore_config
from linear_ceiling.e9 import _stem, dump_fingerprint
from linear_ceiling.hashing import sha256_file_bytes

PAIR = "qwen3-0.6b-to-1.7b"
HIDS = ("20241016_composio_swekit/astropy__astropy-1_traj#1", "20241016_composio_swekit/astropy__astropy-2_traj#2")
N, L, H = 6, 2, 2
ARMS = ("same_K", "same_V", "cross_K", "cross_V")


def _squares(seed: int, cross_scale: float) -> dict:
    """Per-token squares [N, L, H]; same arms fixed by seed (mapper-independent), cross arms scaled."""
    rng = np.random.default_rng(seed)
    base = {a: rng.uniform(0.1, 1.0, size=(N, L, H)).astype(np.float32) for a in ("same_K", "same_V")}
    rng2 = np.random.default_rng(seed + 100)
    base["cross_K"] = (rng2.uniform(0.5, 2.0, size=(N, L, H)) * cross_scale).astype(np.float32)
    base["cross_V"] = (rng2.uniform(0.5, 2.0, size=(N, L, H)) * cross_scale).astype(np.float32)
    base["ref_K"] = np.full((N, L, H), 3.0, dtype=np.float32)
    base["ref_V"] = np.full((N, L, H), 3.0, dtype=np.float32)
    return base


def _body(sq: dict, tok_sha: str) -> dict:
    sst = np.full((L, H), 4.0)
    body = {"n_pairs": N, "per_token": {"sha256": tok_sha}}
    for arm in ARMS:
        part, key = arm.split("_")
        sse = np.asarray(sq[arm], dtype=np.float64).sum(0)
        body.setdefault(part, {})[key] = [{"sse": sse[l].tolist(), "sst": sst[l].tolist()} for l in range(L)]
        body[f"{arm}_r2_layer_mean"] = float((1 - sse / sst).mean())
    return body


def _write_dump(d: Path, payload: bytes) -> dict:
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps({"n_seqs": 1, "stride": 1}), encoding="utf-8")
    (d / "K.bin").write_bytes(payload)
    return dump_fingerprint(d)


def make_world(tmp_path, cross_scale_prior=1.0):
    """Fake upstream (tagged + untagged mapper), the 0029 mirror (report, align, recheck, kept dumps) and an
    E8 report scored with the tagged mapper."""
    up = tmp_path / "up"
    (up / ".venv" / "Scripts").mkdir(parents=True)
    (up / ".venv" / "Scripts" / "python.exe").write_text("", encoding="utf-8")
    for tag, byte in ((None, b"\x00"), ("n420", b"\x01")):
        d = up / "mappers" / PAIR / (tag or "")
        d.mkdir(parents=True, exist_ok=True)
        (d / "k1.safetensors").write_bytes(byte)
        (d / "k1.json").write_text("{}", encoding="utf-8")
    prior = tmp_path / "results" / "e9"
    (prior / "align").mkdir(parents=True)
    (prior / "recheck").mkdir()
    scores = {}
    for i, hid in enumerate(HIDS):
        st = _stem(hid)
        np.savez(prior / "align" / f"{st}.npz", pairs=np.stack([np.arange(N), np.arange(N)], 1))
        kept_dir = prior / "scratch" / st
        kept = {name: _write_dump(kept_dir / name, f"{hid}-{name}".encode()) for name in m.KEPT}
        sq = _squares(seed=i, cross_scale=cross_scale_prior)
        tp = prior / "recheck" / f"{st}.tokens.npz"
        np.savez(tp, **sq)
        body = _body(sq, sha256_file_bytes(tp))
        (prior / "recheck" / f"{st}.json").write_text(json.dumps(body), encoding="utf-8")
        scores[hid] = {"n_pairs": N, "kept_dir": f"scratch/{st}", "kept_dumps": kept,
                       **{f"{a}_r2_layer_mean": body[f"{a}_r2_layer_mean"] for a in ARMS}}
    scores["not-kept/x#0"] = {"n_pairs": 3}
    (prior / "report.json").write_text(json.dumps({"upstream_sha": "d" * 40, "scores": scores}), encoding="utf-8")
    e8 = tmp_path / "results" / "e8c"
    e8.mkdir(parents=True)
    fp = {suf: sha256_file_bytes(up / "mappers" / PAIR / "n420" / f"k1.{suf}") for suf in ("json", "safetensors")}
    (e8 / "report.json").write_text(json.dumps({"mapper": {"tag": "n420", "files": {"1": fp}},
                                                "per_k": {"1": {"generic": {"K": 0.75, "V": 0.6}}}}), encoding="utf-8")
    cp = tmp_path / "e9c.toml"
    cp.write_text("# synthetic\n", encoding="utf-8")
    cfg = E9RescoreConfig(pair=PAIR, results_dir=tmp_path / "results" / "e9c", prior_results_dir=prior,
                          e8_report=e8 / "report.json", upstream_path=up, upstream_sha="a" * 40, mapper_k=1,
                          mapper_tag="n420", amendment={"entry": "0033", "bootstrap_seed": 33, "bootstrap_reps": 100},
                          config_path=cp)
    return cfg


def fake_runner(cross_scale=0.5, same_jitter=0.0):
    def runner(cmd, cwd, capture_output):
        args = cmd[1:]
        assert args[0] == "scripts/score_positions.py"
        opt = {args[i]: args[i + 1] for i in range(1, len(args) - 1, 2)}
        assert opt["--mapper"].replace("\\", "/").endswith(f"/mappers/{PAIR}/n420/k1")
        hid_stem = Path(opt["--out"]).stem
        i = [_stem(h) for h in HIDS].index(hid_stem)
        sq = _squares(seed=i, cross_scale=cross_scale)
        if same_jitter:
            sq["same_K"] = (sq["same_K"] * (1 + same_jitter)).astype(np.float32)
        tp = Path(opt["--per-token"])
        np.savez(tp, **sq)
        Path(opt["--out"]).write_text(json.dumps(_body(sq, sha256_file_bytes(tp))), encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stderr=b"")
    return runner


@pytest.fixture
def world(tmp_path, monkeypatch):
    cfg = make_world(tmp_path)
    monkeypatch.setattr(m, "assert_ready", lambda *a, **k: None)
    monkeypatch.setattr(m, "check_upstream", lambda *a, **k: None)
    return cfg


def test_run_rescores_exactly_the_kept_subset_and_fingerprints_everything(world, tmp_path):
    rp = m.run(world, repo_root=tmp_path, runner=fake_runner())
    rep = json.loads(rp.read_text(encoding="utf-8"))
    assert set(rep["scores"]) == set(HIDS)
    assert rep["mapper"]["tag"] == "n420" and rep["mapper"]["path"].endswith("/n420/k1")
    assert rep["prior"]["sha256"] == sha256_file_bytes(world.prior_results_dir / "report.json")
    rec = rep["scores"][HIDS[0]]
    assert rec["kept_dumps"] == json.loads((world.prior_results_dir / "report.json").read_text())["scores"][HIDS[0]]["kept_dumps"]
    assert (world.results_dir / "tokens" / rec["tokens_file"]).exists()


def test_summary_passes_the_same_arm_control_and_compares_cross_figures(world, tmp_path):
    m.run(world, repo_root=tmp_path, runner=fake_runner(cross_scale=0.5))
    f = m.summarize(world, repo_root=REPO_ROOT)
    a = f["aggregate"]
    assert a["n_handoffs"] == 2
    # same arms are bit-identical to 0028's record by construction
    assert all(v["min_bit_identical_frac"] == 1.0 for v in a["same_arm_control"].values())
    # tau under the tagged mapper comes from the E8 report scored with it
    assert a["tau"]["tagged_mapper"] == {"K": pytest.approx(0.25), "V": pytest.approx(0.4)}
    # the cross arm was re-scored at half the deviation: f* under the registered tau can only go down
    for h in HIDS:
        r = f["per_handoff"][h]["cross_K"]
        assert r["fstar_tau_reg"] <= r["prior_fstar_tau_reg"]
    assert set(a["ladder"]) and "bootstrap_median_fstar_tau_reg" in a["cross_K"]
    assert (world.results_dir / "summary.md").exists() and "does not move" in (world.results_dir / "summary.md").read_text(encoding="utf-8")


def test_summary_refuses_when_the_same_arm_moves(world, tmp_path):
    """The control: a mapper change cannot move the same-model squares; if they differ from 0028's record the
    tensors are not the same tensors and no cross figure is read."""
    m.run(world, repo_root=tmp_path, runner=fake_runner(same_jitter=0.05))
    with pytest.raises(ValueError, match="same-arm control FAILED"):
        m.summarize(world, repo_root=REPO_ROOT)


def test_summary_refuses_swapped_mapper_bytes(world, tmp_path):
    m.run(world, repo_root=tmp_path, runner=fake_runner())
    (world.upstream_path / "mappers" / PAIR / "n420" / "k1.safetensors").write_bytes(b"\x02")
    with pytest.raises(ValueError, match="mapper artifacts"):
        m.summarize(world, repo_root=REPO_ROOT)


def test_summary_refuses_an_e8_report_scored_with_another_mapper(world, tmp_path):
    m.run(world, repo_root=tmp_path, runner=fake_runner())
    e8 = json.loads(world.e8_report.read_text(encoding="utf-8"))
    e8["mapper"]["files"]["1"]["safetensors"] = "0" * 64
    world.e8_report.write_text(json.dumps(e8), encoding="utf-8")
    with pytest.raises(ValueError, match="not scored with this mapper"):
        m.summarize(world, repo_root=REPO_ROOT)


def test_run_refuses_a_changed_kept_dump(world, tmp_path):
    st = _stem(HIDS[1])
    (world.prior_results_dir / "scratch" / st / "cross_src" / "K.bin").write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="kept dump cross_src"):
        m.run(world, repo_root=tmp_path, runner=fake_runner())


def test_summary_refuses_a_changed_prior_report(world, tmp_path):
    m.run(world, repo_root=tmp_path, runner=fake_runner())
    p = world.prior_results_dir / "report.json"
    p.write_text(p.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="prior .0029. report"):
        m.summarize(world, repo_root=REPO_ROOT)


def test_config_loader_validates(tmp_path):
    good = ('[e9c]\npair = "p"\nresults_dir = "r"\nprior_results_dir = "q"\ne8_report = "e"\nupstream_path = "u"\n'
            'upstream_sha = "s"\n[e9c.mapper]\nk = 1\ntag = "n420"\n[e9c.amendment]\nentry = "0033"\n'
            'bootstrap_seed = 33\nbootstrap_reps = 2000\n')
    p = tmp_path / "c.toml"
    p.write_text(good, encoding="utf-8")
    cfg = load_e9_rescore_config(p, tmp_path)
    assert cfg.mapper_tag == "n420" and cfg.amendment["entry"] == "0033"
    p.write_text(good.replace('tag = "n420"', 'tag = "a/b"'), encoding="utf-8")
    with pytest.raises(ValueError, match="tag"):
        load_e9_rescore_config(p, tmp_path)
    p.write_text(good.replace("bootstrap_reps = 2000", "bootstrap_reps = 5"), encoding="utf-8")
    with pytest.raises(ValueError, match="bootstrap"):
        load_e9_rescore_config(p, tmp_path)
    real = load_e9_rescore_config(REPO_ROOT / "config" / "e9c.toml", REPO_ROOT)
    assert real.mapper_tag == "n420" and real.amendment["entry"] == "0033"
