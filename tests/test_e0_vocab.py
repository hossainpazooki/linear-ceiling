import numpy as np
import pytest

from linear_ceiling.e0_vocab import analyze_pair, decide_pair, rms_normalize
from linear_ceiling.rng import make_rng
from linear_ceiling.screen import regularized_cca
from linear_ceiling.weights import WeightReader
from tests.conftest import CFG, tiny_snapshot

RULE = {"delta_separate": 0.05, "delta_same": 0.02, "layer_fraction": 0.67, "pair_scope": "all"}
SWEEP = (1e-3, 1e-2)


def test_rms_normalize_rows_have_unit_rms():
    E = make_rng(0).standard_normal((20, 8)) * 7
    Eh = rms_normalize(E)
    assert np.allclose(np.sqrt((Eh ** 2).mean(1)), 1.0)


def test_rms_normalize_raises_on_zero_row():
    E = make_rng(3).standard_normal((10, 8))
    E[4] = 0.0
    with pytest.raises(ValueError, match=r"1 of 10 row\(s\)") as exc_info:
        rms_normalize(E)
    assert "4" in str(exc_info.value)


def test_rms_normalize_raises_on_multiple_zero_rows_naming_indices():
    E = make_rng(3).standard_normal((10, 8))
    E[2] = 0.0
    E[7] = 0.0
    with pytest.raises(ValueError, match=r"2 of 10 row\(s\)") as exc_info:
        rms_normalize(E)
    msg = str(exc_info.value)
    assert "2" in msg and "7" in msg


def test_rms_normalize_raises_on_non_finite_row():
    E = make_rng(3).standard_normal((10, 8))
    E[5, 0] = np.nan
    with pytest.raises(ValueError, match=r"1 of 10 row\(s\)") as exc_info:
        rms_normalize(E)
    assert "5" in str(exc_info.value)


def test_decide_pair_rule():
    good = {"a": {"median": 0.1, "frac_positive": 0.9}, "b": {"median": 0.06, "frac_positive": 0.7}}
    assert decide_pair(good, RULE) == "SEPARATE"
    assert decide_pair({"a": {"median": 0.01, "frac_positive": 0.5}, "b": {"median": -0.015, "frac_positive": 0.4}}, RULE) == "SAME"
    assert decide_pair({"a": {"median": 0.1, "frac_positive": 0.9}, "b": {"median": 0.01, "frac_positive": 0.5}}, RULE) == "UNRESOLVED"
    assert decide_pair({"a": {"median": -0.2, "frac_positive": 0.1}}, RULE) == "UNRESOLVED"   # inverted sign


def _pair_snapshots(tmp_path, rng, *, same: bool):
    """Source/target embeddings share a linear factor; target read-outs are built from the
    pair's own canonical basis so K loads on high-rho directions and V on low-rho ones
    (or identically, for the SAME case)."""
    V, hs, ht = 400, 24, CFG["hidden_size"]      # ht = 32
    cfg_s = {**CFG, "hidden_size": hs, "vocab_size": V}
    cfg_t = {**CFG, "vocab_size": V}
    Z = rng.standard_normal((V, 12))
    Es = Z @ rng.standard_normal((12, hs)) + 0.2 * rng.standard_normal((V, hs))
    Et = Z @ rng.standard_normal((12, ht)) + 0.2 * rng.standard_normal((V, ht))
    res = regularized_cca(rms_normalize(Es), rms_normalize(Et), 1e-3, 1e-3)
    kvd = CFG["num_key_value_heads"] * CFG["head_dim"]           # 16
    top, bottom = res.B[:, :kvd], res.B[:, -kvd:]                 # (ht, 16) canonical directions
    g = 2.0                                                       # tiny_snapshot's input_layernorm gain
    Wk = (top / g).T                                              # R_K = g * Wk^T = top
    Wv = (top / g).T if same else (bottom / g).T
    Wk, Wv = np.round(Wk, 3), np.round(Wv, 3)
    layers = CFG["num_hidden_layers"]
    ds, _ = tiny_snapshot(tmp_path, "src", cfg=cfg_s, embed=Es)
    dt, _ = tiny_snapshot(tmp_path, "tgt", cfg=cfg_t, embed=Et,
                          k_proj={l: Wk for l in range(layers)}, v_proj={l: Wv for l in range(layers)})
    return WeightReader(ds), WeightReader(dt)


def test_analyze_pair_separate_and_same(tmp_path):
    s, t = _pair_snapshots(tmp_path, make_rng(1), same=False)
    r = analyze_pair(s, t, SWEEP, RULE)
    assert r["verdict"] == "SEPARATE" and r["n_tokens"] == 400
    for lam in SWEEP:
        blk = r["by_lambda"][str(lam)]
        assert len(blk["r2_K"]) == CFG["num_hidden_layers"] and all(d > 0 for d in blk["delta"])
    (tmp_path / "x").mkdir()
    s2, t2 = _pair_snapshots(tmp_path / "x", make_rng(1), same=True)
    r2 = analyze_pair(s2, t2, SWEEP, RULE)
    assert r2["verdict"] == "SAME" and all(abs(d) < 1e-9 for d in r2["by_lambda"]["0.001"]["delta"])


def test_analyze_pair_refuses_different_vocab(tmp_path):
    s, t = _pair_snapshots(tmp_path, make_rng(2), same=False)
    (t.dir / "tokenizer.json").write_text('{"model": {"vocab": {"only": 0}}}')
    with pytest.raises(ValueError, match="vocab"):
        analyze_pair(s, t, SWEEP, RULE)
