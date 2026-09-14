"""E9 scaled short cell (config/e9s.toml + linear_ceiling.e9_compare): the config is 0029's instrument under
0036's receiver, and the comparison is fail-closed on every seam it can check -- on synthetic records."""
import json

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import _stem, entry_list, required_markers, rope_args
from linear_ceiling.e9_compare import compare, render
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.summarize_e9 import _tau_key

YARN = {"rope_type": "yarn", "factor": 2.5, "original_max_position_embeddings": 32768}
H1, H2 = "20241016_composio_x/a_traj#1", "20241016_composio_x/b_traj#2"
L, H = 2, 3


def test_e9s_config_is_e9s_instrument_under_e9l_receiver():
    s = load_e9_config(REPO_ROOT / "config" / "e9s.toml", REPO_ROOT)
    e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
    e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
    assert s.rule == e9.rule and s.controls == e9.controls and s.mapper_k == e9.mapper_k
    assert s.context_cap == e9.context_cap == 32768 and s.context_floor == 0
    assert s.keep_seed == e9.keep_seed == 9 and s.keep_n == e9.keep_n == 8       # the same draw over the same ids
    assert s.rope == e9l.rope == YARN and s.upstream_sha == e9l.upstream_sha    # 0036's receiver and pin
    assert s.bridge is None and s.profiles is None                              # the whole run is the bridge
    assert s.order_by == "n_sender_asc" and s.allow_partial
    assert s.results_dir.name == "e9s" and s.results_dir != e9.results_dir
    assert s.required_entries == ("0019", "0023", "0025", "0027", "0035", "0037")
    assert required_markers(s)[-1] == "### 0037 " and entry_list(s).endswith("/0037")
    assert json.loads(rope_args(s)[1]) == YARN


@pytest.mark.parametrize("old,new,msg", [
    ("context_floor = 0", "context_floor = 32768", "context_floor"),
    ("factor = 2.5", "factor = 0.5", "rope"),
    ('required_entries = ["0019", "0023", "0025", "0027", "0035", "0037"]', 'required_entries = ["37"]', "required_entries")])
def test_e9s_config_refuses_malformed_parameters(tmp_path, old, new, msg):
    src = (REPO_ROOT / "config" / "e9s.toml").read_text(encoding="utf-8")
    assert old in src
    p = tmp_path / "e9s.toml"
    p.write_text(src.replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, tmp_path)


# ---- synthetic runs for the comparison -----------------------------------------------------------------------------

def _cfg(tmp_path, name, rope: bool):
    src = (REPO_ROOT / "config" / ("e9s.toml" if rope else "e9.toml")).read_text(encoding="utf-8")
    src = src.replace('results_dir = "results/e9s"', f'results_dir = "results/{name}"').replace(
        'scratch_dir = "results/e9s/scratch"', f'scratch_dir = "results/{name}/scratch"').replace(
        'results_dir = "results/e9"\n', f'results_dir = "results/{name}"\n').replace(
        'scratch_dir = "results/e9/scratch"', f'scratch_dir = "results/{name}/scratch"')
    p = tmp_path / f"{name}.toml"
    p.write_text(src, encoding="utf-8")
    return load_e9_config(p, tmp_path)


def _pairs(n, n_sender, n_receiver, seed):
    rng = np.random.default_rng(seed)
    ps = np.sort(rng.choice(n_sender, n, replace=False))
    pr = np.sort(rng.choice(n_receiver, n, replace=False))
    return np.stack([ps, pr], 1).astype(np.int64)


def _write_run(cfg, handoffs: dict, pairs: dict, *, complete=True):
    """handoffs: hid -> per-token delta_K target [n]; the squares are built so that token_mean(centered_delta) == target
    exactly (sst = n per head, every head and layer equal)."""
    rd = cfg.results_dir
    for d in ("align", "scores", "tokens"):
        (rd / d).mkdir(parents=True, exist_ok=True)
    scores, aligns = {}, []
    for hid, target in handoffs.items():
        n = len(target)
        pr = pairs[hid]
        np.savez(rd / "align" / f"{_stem(hid)}.npz", pairs=pr, s_ids=np.arange(pr[:, 0].max() + 1), r_ids=np.arange(pr[:, 1].max() + 1))
        sq = np.repeat(np.repeat(np.asarray(target, dtype=np.float64)[:, None, None], L, 1), H, 2).astype(np.float32)
        tf, sf = f"{_stem(hid)}.tokens.npz", f"{_stem(hid)}.json"
        np.savez(rd / "tokens" / tf, same_K=sq, same_V=sq, ref_K=sq, ref_V=sq, cross_K=sq, cross_V=sq)
        body = {"n_pairs": n, "same": {k: [{"sst": [float(n)] * H} for _ in range(L)] for k in "KV"},
                "cross": {k: [{"sst": [float(n)] * H} for _ in range(L)] for k in "KV"}}
        (rd / "scores" / sf).write_text(json.dumps(body), encoding="utf-8")
        scores[hid] = {"score_file": sf, "score_sha256": sha256_file_bytes(rd / "scores" / sf),
                       "tokens_file": tf, "tokens_sha256": sha256_file_bytes(rd / "tokens" / tf)}
        aligns.append({"handoff_id": hid, "n_sender": int(pr[:, 0].max() + 1), "n_receiver": int(pr[:, 1].max() + 1),
                       "n_matched": n, "excluded": False, "reason": None, "text_sha256": f"text-{hid}"})
    rep = {"complete": complete, "config_sha256": sha256_text_file(cfg.config_path), "scores": scores, "alignments": aligns}
    (rd / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    return rep


@pytest.fixture
def runs(tmp_path):
    native, scaled = _cfg(tmp_path, "e9", rope=False), _cfg(tmp_path, "e9s", rope=True)
    rng = np.random.default_rng(0)
    n1, n2 = 400, 300
    pairs = {H1: _pairs(n1, 600, 500, 1), H2: _pairs(n2, 450, 400, 2)}
    d1, d2 = rng.uniform(0.0, 0.3, n1), rng.uniform(0.0, 0.3, n2)
    _write_run(native, {H1: d1, H2: d2}, pairs)
    _write_run(scaled, {H1: d1 * 1.5, H2: d2}, pairs)          # H1 moves by half of itself, H2 does not move
    return native, scaled, pairs, {H1: d1, H2: d2}


def test_compare_pairs_tokens_and_reads_the_shift(runs, tmp_path):
    native, scaled, _, d = runs
    out = compare(native, scaled)
    assert out["n_handoffs"] == 2 and out["n_tokens"] == 700 and out["rope"] == YARN
    h1, h2 = out["per_handoff"][H1], out["per_handoff"][H2]
    assert h1["mean_delta_K"]["native"] == pytest.approx(d[H1].mean(), rel=1e-5)
    assert h1["mean_delta_K"]["scaled"] == pytest.approx(d[H1].mean() * 1.5, rel=1e-5)
    assert h1["mean_delta_K"]["scaled_minus_native"] == pytest.approx(d[H1].mean() * 0.5, rel=1e-5)
    assert h2["mean_delta_K"]["scaled_minus_native"] == pytest.approx(0.0, abs=1e-9)
    assert h2["token_diff"]["max"] == pytest.approx(0.0, abs=1e-9) and h1["token_diff"]["median"] > 0
    tk = _tau_key(float(scaled.rule["tau_K"]))
    assert h1["fstar"][tk] == {"native": 0.0, "scaled": 0.0}          # means 0.15 / 0.225 sit under tau_K = 0.3186
    k03 = _tau_key(0.03)
    assert h1["fstar"][k03]["scaled"] > h1["fstar"][k03]["native"] > 0   # the ladder moves where the mean does not
    pm = out["paired_mean_delta_K_scaled_minus_native"]
    assert pm["n"] == 2 and pm["bootstrap"]["seed"] == 37 and "lower_2.5" in pm["bootstrap"]
    assert sum(r["n_tokens"] for r in out["seam_profile_left_pooled"]) == 700
    assert out["long_cell"] is None and out["configuration_share"] is None
    md = render(out)
    assert "decides nothing" in md and "identical alignments" in md and "Against the long cell" not in md


def test_compare_share_against_a_long_summary(runs, tmp_path):
    native, scaled, _, _ = runs
    base = compare(native, scaled)
    far = next(r for r in base["seam_profile_left_pooled"] if r["bin"] == "16+")
    k03 = _tau_key(0.03)
    f03 = base["fstar_median_over_handoffs"][k03]
    # a long cell whose far-from-seam median sits exactly twice as far from native as the scaled short cell does
    long_far = far["median_native"] + 2 * (far["median_scaled"] - far["median_native"])
    long_f03 = f03["native"] + 4 * (f03["scaled"] - f03["native"])
    ls = {"coverage": {"included": 35, "scored": 35},
          "seam_profile_left_pooled": {"same_K": [{"bin": "16+", "n_tokens": 10, "median": long_far}]},
          "fstar_ladder": {"same_K": {_tau_key(0.1): {"median": 0.0}, k03: {"median": long_f03}}}}
    p = tmp_path / "long.json"
    p.write_text(json.dumps(ls), encoding="utf-8")
    out = compare(native, scaled, p)
    assert out["configuration_share"]["seam_far"] == pytest.approx(0.5)
    assert out["configuration_share"][f"fstar_{k03}"] == pytest.approx(0.25)
    assert "Against the long cell (35 handoffs" in render(out)
    ls["seam_profile_left_pooled"]["same_K"][0]["median"] = far["median_native"]      # no cross-cell difference -> no share
    p.write_text(json.dumps(ls), encoding="utf-8")
    assert compare(native, scaled, p)["configuration_share"]["seam_far"] is None
    ls.pop("fstar_ladder")
    p.write_text(json.dumps(ls), encoding="utf-8")
    with pytest.raises(ValueError, match="lacks the seam profile or the tau ladder"):
        compare(native, scaled, p)


def test_compare_refuses_on_every_seam(runs, tmp_path):
    native, scaled, pairs, d = runs
    # 1. a native config that carries rope, or a scaled one that does not
    with pytest.raises(ValueError, match="native config carries"):
        compare(scaled, scaled)
    with pytest.raises(ValueError, match="no \\[e9.rope\\]"):
        compare(native, native)
    # 2. an incomplete scaled run
    rep = json.loads((scaled.results_dir / "report.json").read_text(encoding="utf-8"))
    (scaled.results_dir / "report.json").write_text(json.dumps(rep | {"complete": False}), encoding="utf-8")
    with pytest.raises(ValueError, match="not complete"):
        compare(native, scaled)
    # 3. a report written under another config
    (scaled.results_dir / "report.json").write_text(json.dumps(rep | {"config_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="another e9s.toml"):
        compare(native, scaled)
    (scaled.results_dir / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    # 4. different handoff sets
    _write_run(scaled, {H1: d[H1]}, pairs)
    with pytest.raises(ValueError, match="different handoffs"):
        compare(native, scaled)
    # 5. the same ids over a different pairing
    other = dict(pairs, **{H2: _pairs(300, 450, 400, 9)})
    _write_run(scaled, d, other)
    with pytest.raises(ValueError, match="alignment arrays differ"):
        compare(native, scaled)
    # 6. a per-token record edited after its hash was recorded
    _write_run(scaled, d, pairs)
    tf = scaled.results_dir / "tokens" / f"{_stem(H1)}.tokens.npz"
    z = dict(np.load(tf))
    z["same_K"] = z["same_K"] * 2
    np.savez(tf, **z)
    with pytest.raises(ValueError):
        compare(native, scaled)
