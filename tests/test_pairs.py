import pytest

from linear_ceiling.pairs import LADDER, ordered_pairs, pair_name, short_name


def test_pair_name_matches_upstream_convention():
    # provenance: kv-transfer-replication kvt/pairs.py @ f3594458 uses "qwen3-0.6b-to-1.7b"
    assert pair_name("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B") == "qwen3-0.6b-to-1.7b"
    assert pair_name("Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B") == "qwen3-1.7b-to-4b"


def test_short_name_requires_qwen3_family():
    assert short_name("Qwen/Qwen3-8B") == "qwen3-8b"
    with pytest.raises(ValueError):
        short_name("meta-llama/Llama-3-8B")


def test_pair_name_rejects_identical_models():
    with pytest.raises(ValueError):
        pair_name("Qwen/Qwen3-1.7B", "Qwen/Qwen3-1.7B")


def test_pair_name_rejects_invalid_target():
    with pytest.raises(ValueError):
        pair_name("Qwen/Qwen3-1.7B", "meta-llama/Llama-3-8B")


def test_ordered_pairs_is_n_times_n_minus_one():
    ps = ordered_pairs(LADDER[:3])
    assert len(ps) == 6
    assert ("Qwen/Qwen3-1.7B", "Qwen/Qwen3-0.6B") in ps   # reverse direction included


def test_ladder_order():
    assert LADDER == ("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "Qwen/Qwen3-8B")
