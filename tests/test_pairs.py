import pytest

from linear_ceiling.pairs import (EXTRA_PAIRS, LADDER, LLAMA_LADDER, ordered_pairs, pair_models,
                                  pair_name, short_name)


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


# --- second family: the cross-release Llama pair -------------------------------------------

def test_llama_pair_name_names_the_receiver_in_full():
    # The short form would be "llama3.2-3b-to-8b", asserting a Llama-3.2-8B that does not
    # exist. The string keys the seal and every artifact path, so it must name both sides.
    assert (pair_name("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B")
            == "llama3.2-3b-to-llama3.1-8b")


def test_llama_short_names():
    assert short_name("meta-llama/Llama-3.2-3B") == "llama3.2-3b"
    assert short_name("meta-llama/Llama-3.1-8B") == "llama3.1-8b"


def test_llama_pair_resolves_both_ways():
    name = pair_name(*LLAMA_LADDER)
    assert name in EXTRA_PAIRS
    assert pair_models(name) == ("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B")
    assert LLAMA_LADDER == ("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B")


def test_same_release_llama_pair_keeps_the_short_form():
    # This is why pair_name is conditional rather than always naming both sides: inside one
    # release the upstream convention is unchanged, which is what keeps the sealed Qwen name
    # byte-identical.
    assert (pair_name("meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-3B")
            == "llama3.2-1b-to-3b")


def test_qwen_pair_still_resolves_exactly_as_before():
    assert pair_models("qwen3-0.6b-to-1.7b") == ("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B")
    assert pair_models("qwen3-1.7b-to-4b") == ("Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B")


def test_pair_name_rejects_a_cross_family_pair():
    with pytest.raises(ValueError, match="one model family"):
        pair_name("Qwen/Qwen3-4B", "meta-llama/Llama-3.1-8B")
    with pytest.raises(ValueError, match="one model family"):
        pair_name("meta-llama/Llama-3.2-3B", "Qwen/Qwen3-8B")


def test_unknown_model_id_is_refused_with_a_clear_message():
    for bad in ("meta-llama/Llama-3-8B", "meta-llama/Llama-4-8B", "mistralai/Mistral-7B-v0.1",
                "llama3.2-3b", ""):
        with pytest.raises(ValueError, match="not a known base model id"):
            short_name(bad)


def test_unknown_pair_name_is_refused():
    with pytest.raises(ValueError, match="unknown pair"):
        pair_models("llama3.2-3b-to-8b")          # the wrong-receiver short form
    with pytest.raises(ValueError, match="unknown pair"):
        pair_models("qwen3-0.6b-to-llama3.1-8b")


def test_no_emitted_pair_name_contains_a_path_separator():
    # seal._validate_pair rejects a '/' outright; a pair name is also a directory component
    # of mappers/, data/kv/ and results/probe/.
    names = [pair_name(a, b) for a, b in ordered_pairs(LADDER)]
    names.append(pair_name(*LLAMA_LADDER))
    names.extend(EXTRA_PAIRS)
    for n in names:
        assert "/" not in n and "\\" not in n
