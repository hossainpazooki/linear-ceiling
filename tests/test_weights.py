import numpy as np
import pytest

from linear_ceiling.weights import ModelSpec, WeightReader, assert_shared_vocab, spec_from_config
from tests.conftest import CFG, tiny_snapshot as _tiny_snapshot


def test_spec_from_config_matches_upstream_kv_shape():
    s = spec_from_config(CFG, "x")
    assert s == ModelSpec("x", 32, 2, 4, 2, 8, 10000.0, 16)
    s2 = spec_from_config({**CFG, "head_dim": None, "rope_theta": None,
                           "rope_parameters": {"rope_theta": 5.0}}, "x")
    assert s2.d_h == 8 and s2.rope_theta == 5.0
    with pytest.raises(ValueError, match="rope_theta"):
        spec_from_config({k: v for k, v in CFG.items() if k != "rope_theta"}, "x")


@pytest.mark.parametrize("sharded", [False, True])
def test_reader_returns_float32_exact(tmp_path, sharded):
    d, ref = _tiny_snapshot(tmp_path, sharded=sharded)
    r = WeightReader(d)
    assert r.spec.n_layers == 2 and r.spec.n_kv == 2
    for l in range(2):
        for name, getter in (("k_proj", r.k_proj), ("v_proj", r.v_proj)):
            W = getter(l)
            assert W.dtype == np.float32 and W.shape == (16, 32)
            assert np.array_equal(W, ref[f"model.layers.{l}.self_attn.{name}.weight"])
        assert np.array_equal(r.k_norm(l), np.full(8, 0.5, np.float32))
        assert np.array_equal(r.input_layernorm(l), np.full(32, 2.0, np.float32))
    assert r.embed().shape == (16, 32)
    assert r.heads(r.k_proj(0)).shape == (2, 8, 32)
    assert np.array_equal(r.heads(r.k_proj(0))[1], r.k_proj(0)[8:16])


def test_reader_refuses_out_of_range_layer(tmp_path):
    d, _ = _tiny_snapshot(tmp_path)
    with pytest.raises(IndexError):
        WeightReader(d).k_proj(2)


def test_shared_vocab_check(tmp_path):
    a, _ = _tiny_snapshot(tmp_path, "a")
    b, _ = _tiny_snapshot(tmp_path, "b", seed=1)
    assert_shared_vocab(WeightReader(a), WeightReader(b))
    c, _ = _tiny_snapshot(tmp_path, "c", vocab_words=[f"u{i}" for i in range(16)])
    with pytest.raises(ValueError, match="vocab"):
        assert_shared_vocab(WeightReader(a), WeightReader(c))
