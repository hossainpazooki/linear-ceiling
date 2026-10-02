import json
from types import SimpleNamespace
import tomllib

import numpy as np
import pytest
import torch

pytest.importorskip("transformers")
from transformers import Qwen3Config, Qwen3ForCausalLM

from linear_ceiling.rng import make_rng
from tools.cache_behavior.core import (TailObserver, attention_reduce, blocks, compare_logits,
                                       construct, continuation_logits, half_rotate, matched,
                                       prefill, random_candidate, relocate, relocated_candidate,
                                       validate_pairs)
from tools.cache_behavior import run as driver
from tools.cache_behavior.run import continuation_from, digest, summarize


@pytest.fixture
def model():
    torch.manual_seed(3)
    cfg = Qwen3Config(vocab_size=32, hidden_size=32, intermediate_size=48, num_hidden_layers=2,
                     num_attention_heads=4, num_key_value_heads=2, head_dim=8,
                     max_position_embeddings=81920, attention_dropout=0,
                     rope_parameters={"rope_type": "yarn", "rope_theta": 1000000.0,
                                      "factor": 2.5, "original_max_position_embeddings": 32768})
    cfg._attn_implementation = "sdpa"
    return Qwen3ForCausalLM(cfg).eval()


def test_archived_pairs_and_recompute_splits():
    sender, receiver = np.array([1, 2, 3, 4, 5]), np.array([1, 2, 9, 3, 4, 5])
    pairs = np.array([[0, 0], [1, 1], [2, 3], [3, 4], [4, 5]])
    validate_pairs(sender, receiver, pairs)
    assert [r.tolist() for r in blocks(pairs, [3])] == [[0, 1], [2], [4]]
    assert blocks(pairs, list(range(5))) == []
    for invalid in (np.array([[0, 0], [1, 0]]), np.array([[99, 0]]), np.array([[0, 2]])):
        with pytest.raises(ValueError):
            validate_pairs(sender, receiver, invalid)


def test_long_yarn_relocation_preserves_amplitude(model):
    freq = model.model.rotary_emb.inv_freq
    scale = model.model.rotary_emb.attention_scaling
    content = torch.randn(1, 2, 4, 8)
    source, destination = np.array([32768, 50000, 70000, 80110]), np.array([2, 121, 1234, 19000])
    def direct(positions):
        angles = torch.outer(torch.as_tensor(positions).float(), freq)
        angles = torch.cat((angles, angles), dim=-1)
        return (content * angles.cos() + half_rotate(content) * angles.sin()) * scale
    actual = relocate(direct(source), source, destination, freq)
    torch.testing.assert_close(actual, direct(destination), atol=1e-6, rtol=1e-6)
    # A second YaRN amplitude multiplication would fail this comparison.
    assert scale > 1


def test_full_match_empty_match_and_teacher_forcing(model):
    tokens, continuation = np.array([2, 3, 4, 5, 6]), np.array([9, 10, 11, 12])
    pairs = np.column_stack((np.arange(5), np.arange(5)))
    original = prefill(model, tokens, 2)
    states = matched(original, np.arange(5))
    expected = continuation_logits(model, original, continuation, 2)
    for recompute in ([], list(range(5))):
        cache, counts = construct(model, tokens, pairs, states, 2, recompute)
        actual = continuation_logits(model, cache, continuation, 2)
        torch.testing.assert_close(actual, expected, atol=1e-6, rtol=1e-6)
        assert counts["copied"] == 5 - len(recompute)
    full = model(torch.tensor([tokens.tolist() + continuation[:-1].tolist()]), logits_to_keep=0).logits[0]
    torch.testing.assert_close(expected, full[len(tokens):], atol=1e-6, rtol=1e-6)
    assert len(expected) == len(continuation) - 1
    identical = compare_logits(expected, expected)
    assert not identical["kl"].any() and identical["top1_agrees"].all()


def test_prefix_and_gap_prefill_reads_the_assembled_cache(model):
    source, receiver = np.array([15, 3, 4, 5]), np.array([2, 3, 9, 5])
    pairs = np.array([[1, 1], [3, 3]])
    source_cache = prefill(model, source, 2)
    candidate = relocated_candidate(matched(source_cache, pairs[:, 0]), pairs,
                                    model.model.rotary_emb.inv_freq)
    assembled, counts = construct(model, receiver, pairs, candidate, 2)
    fresh = prefill(model, receiver, 2)
    assert counts["copied"] == 2 and assembled.get_seq_length() == len(receiver)
    # Position 2 is computed, but its deeper states change because it reads reused predecessors.
    assert not torch.equal(assembled.layers[1].values[:, :, 2], fresh.layers[1].values[:, :, 2])
    prefix_pairs = np.array([[0, 0], [1, 1]])
    prefix = matched(prefill(model, receiver[:2], 2), np.arange(2))
    exact, _ = construct(model, receiver, prefix_pairs, prefix, 2)
    for actual, expected in zip(exact.layers, fresh.layers):
        torch.testing.assert_close(actual.keys, expected.keys, atol=1e-6, rtol=1e-6)


def test_random_null_preserves_each_error_norm_and_seed():
    fresh = [(torch.zeros(1, 2, 3, 8), torch.ones(1, 2, 3, 8))]
    reused = [(torch.arange(48).reshape(1, 2, 3, 8).float(), torch.ones(1, 2, 3, 8))]
    a, b = random_candidate(fresh, reused, make_rng(11)), random_candidate(fresh, reused, make_rng(11))
    for i in (0, 1):
        assert torch.equal(a[0][i], b[0][i])
        torch.testing.assert_close(((a[0][i] - fresh[0][i]) ** 2).sum(-1),
                                   ((reused[0][i] - fresh[0][i]) ** 2).sum(-1))
    assert torch.equal(a[0][1], fresh[0][1])


def test_attention_reducer_causal_gqa_and_observer(model):
    query, keys = torch.randn(4, 3, 8), torch.randn(2, 5, 8)
    positions = torch.tensor([2, 3, 4])
    delta = torch.arange(10).reshape(5, 2).float() / 10
    mask = torch.tensor([True, False, True, True, False])
    delta[~mask] = 0
    tail = mask & (delta.mean(-1) > .5)
    actual = attention_reduce(query, keys, positions, delta, tail, mask, chunk=1)
    weights = (query @ keys.repeat_interleave(2, dim=0).transpose(-1, -2)) / 8 ** .5
    weights.masked_fill_(torch.arange(5)[None, None] > positions[None, :, None], float("-inf"))
    weights = weights.softmax(-1)
    d = delta.T.repeat_interleave(2, dim=0)
    expected = torch.stack(((weights * d[:, None]).sum(-1),
                            (weights * tail[None, None]).sum(-1),
                            (weights * mask[None, None]).sum(-1)), -1).transpose(0, 1)
    torch.testing.assert_close(actual, expected)
    pairs = np.array([[0, 0], [2, 2], [3, 3]])
    observer = TailObserver(model, 4, pairs, np.ones((3, 2, 2)), 2, .5, 1)
    prefill(model, np.array([2, 3, 4, 5]), 2)
    result = observer.close()
    assert result.shape == (2, 2, 4, 3)
    np.testing.assert_allclose(result[..., 0], result[..., 1])
    assert np.all((result >= 0) & (result <= 1.000001))


def test_observer_matches_model_eager_attention(model):
    tokens = np.array([2, 3, 4, 5, 6])
    pairs = np.array([[0, 0], [2, 2], [4, 4]])
    delta = np.arange(12).reshape(3, 2, 2).astype(np.float32) / 10
    tail = delta.mean((1, 2)) > .5
    observer = TailObserver(model, len(tokens), pairs, delta, 2, .5, 1, tail)
    prefill(model, tokens, 2)
    actual = observer.close()
    model.config._attn_implementation = "eager"
    with torch.inference_mode():
        attention = model(torch.as_tensor(tokens)[None], output_attentions=True).attentions
    expected = []
    for layer, weights in enumerate(attention):
        d = torch.zeros(5, 2)
        d[pairs[:, 1]] = torch.as_tensor(delta[:, layer])
        mask, tail_mask = torch.zeros(5), torch.zeros(5)
        mask[pairs[:, 1]] = 1
        tail_mask[pairs[:, 1]] = torch.as_tensor(tail).float()
        w = weights[0, :, -2:]
        expected.append(torch.stack(((w * d.T.repeat_interleave(2, 0)[:, None]).sum(-1),
                                     (w * tail_mask[None, None]).sum(-1),
                                     (w * mask[None, None]).sum(-1)), -1).transpose(0, 1))
    np.testing.assert_allclose(actual, torch.stack(expected).numpy(), atol=1e-6, rtol=1e-6)


def test_continuation_extractor_uses_the_registered_switch_index(tmp_path):
    folder = tmp_path / "submission"
    folder.mkdir()
    path = folder / "task.json"
    path.write_text(json.dumps([
        [{"kwargs": {"type": "human", "content": "first", "model": "sender"}},
         {"llm_output": {"model_name": "sender"}, "generations": [[{"text": "old response"}]]}],
        [{"kwargs": {"type": "human", "content": "receiver prompt", "model": "receiver"}},
         {"llm_output": {"model_name": "receiver"}, "generations": [[{"text": "recorded continuation"}]]}]]))
    handoff, continuation = continuation_from(path, "submission/task#1")
    assert handoff.receiver_text == "receiver prompt"
    assert continuation == "recorded continuation"


def test_summary_rechecks_logits_witness_and_zero_attention_mass(tmp_path):
    fresh, reused = torch.tensor([[0., 1., 2.], [1., 2., 3.]]), torch.tensor([[2., 0., 1.], [1., 2., 2.]])
    observed = compare_logits(fresh, reused)
    path = tmp_path / "handoff.npz"
    payload = {"reuse_kl": observed["kl"], "reuse_top1_agrees": observed["top1_agrees"],
               "fresh_witness": fresh.numpy(), "reuse_witness": reused.numpy(),
               "continuation": np.array([2, 3, 4]), "witness_continuation_indices": np.array([1, 2]),
               "attention": np.zeros((1, 2, 1, 3))}
    np.savez(path, **payload)
    report = {"scores": {"handoff": {"file": path.name, "sha256": digest(path), "arms": ["reuse"], "witness_count": 2,
                                        "scored_continuation_tokens": 2}},
              "complete": True, "excluded": [], "run_order": ["handoff"]}
    (tmp_path / "report.json").write_text(json.dumps(report))
    result = summarize(tmp_path)
    assert result["attention"]["conditional_weighted_delta_mean"] is None
    assert result["attention"]["conditional_undefined_count"]["median"] == 2
    payload["reuse_kl"][0] += .1
    np.savez(path, **payload)
    report["scores"]["handoff"]["sha256"] = digest(path)
    (tmp_path / "report.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="witness"):
        summarize(tmp_path)


@pytest.mark.parametrize("order,scores,complete", [
    (["first", "second"], {"first": {}}, True),  # removed second result, stale complete flag
    (["first", "second"], {"second": {}}, False),  # missing beginning of scored prefix
    (["first", "first"], {}, False),  # duplicate cohort member
    (["first"], {"first": {}}, False),  # all scored but falsely marked incomplete
])
def test_summary_refuses_false_coverage(tmp_path, order, scores, complete):
    (tmp_path / "report.json").write_text(json.dumps({"run_order": order, "scores": scores,
                                                      "complete": complete, "excluded": []}))
    with pytest.raises(ValueError, match="prefix|complete"):
        summarize(tmp_path)


def test_summary_checks_cohort_against_prepared_manifest(tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    manifest = {"records": [{"handoff": "first", "sender_tokens": 9, "excluded": False},
                            {"handoff": "second", "sender_tokens": 4, "excluded": False}]}
    (inputs / "manifest.json").write_text(json.dumps(manifest))
    report = {"identity": {"manifest_sha256": digest(inputs / "manifest.json")},
              "run_order": ["first"], "scores": {}, "complete": False, "excluded": []}
    (tmp_path / "report.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="cohort differs"):
        summarize(tmp_path, inputs)

@pytest.mark.parametrize("side", ["fresh", "candidate"])
@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_logits_reject_nonfinite_values(side, bad):
    logits = {"fresh": torch.zeros(2, 3), "candidate": torch.zeros(2, 3)}
    logits[side][0, 0] = bad
    with pytest.raises(ValueError, match="logits"):
        compare_logits(**logits)


@pytest.mark.parametrize("damage", ["missing_witness", "short_metrics", "wrong_positions",
                                    "nan_kl", "float_top1"])
def test_summary_rejects_incomplete_records_with_valid_file_hashes(tmp_path, damage):
    payload = {"continuation": np.array([2, 3, 4]),
               "reuse_kl": np.zeros(2), "reuse_top1_agrees": np.ones(2, dtype=bool),
               "fresh_witness": np.ones((2, 3)), "reuse_witness": np.ones((2, 3)),
               "witness_continuation_indices": np.array([1, 2]),
               "attention": np.zeros((1, 2, 1, 3))}
    result = {"file": "sample.npz", "arms": ["reuse"], "scored_continuation_tokens": 2, "witness_count": 2}
    if damage == "missing_witness":
        del result["witness_count"]
    elif damage == "short_metrics":
        payload["reuse_kl"] = payload["reuse_kl"][:1]
    elif damage == "wrong_positions":
        payload["witness_continuation_indices"] = np.array([0, 1])
    elif damage == "nan_kl":
        payload["reuse_kl"][1] = np.nan
    else:
        payload["reuse_top1_agrees"] = np.ones(2)
    np.savez(tmp_path / "sample.npz", **payload)
    result["sha256"] = digest(tmp_path / "sample.npz")
    (tmp_path / "report.json").write_text(json.dumps({
        "scores": {"sample": result}, "complete": True, "excluded": [], "run_order": ["sample"]}))
    with pytest.raises((KeyError, ValueError)):
        summarize(tmp_path)


def test_resumed_probe_keeps_one_handoff_and_exact_recompute_budget(model, tmp_path, monkeypatch):
    # Real tiny-model CPU forwards exercise assembly and records; only CUDA plumbing is replaced.
    cfg = tomllib.loads((driver.ROOT / "config/cache-behavior.toml").read_text())
    cfg.update(chunk_tokens=2, continuation_chunk=2, attention_queries=2,
               attention_query_chunk=1, prefix_control_tokens=2, oracle_fractions=[.105])
    monkeypatch.setattr(model, "to", lambda device: model)
    monkeypatch.setattr(driver.AutoConfig, "from_pretrained", lambda *a, **k: model.config)
    monkeypatch.setattr(driver.AutoModelForCausalLM, "from_pretrained", lambda *a, **k: model)
    monkeypatch.setattr(torch.cuda, "get_device_name", lambda device: "CPU test")
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda device: 0)
    for name in ("empty_cache", "reset_peak_memory_stats"):
        monkeypatch.setattr(torch.cuda, name, lambda *a: None)
    monkeypatch.setattr(torch, "use_deterministic_algorithms", lambda enabled: None)
    monkeypatch.setattr(driver, "sync", lambda device: None)
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    records = []
    for hid, n in (("largest", 20), ("shorter", 5)):
        tokens = np.arange(1, n + 1)
        path = inputs / f"{hid}.npz"
        np.savez(path, sender=tokens, receiver=tokens,
                 pairs=np.column_stack((np.arange(n), np.arange(n))),
                 continuation=np.array([21, 22, 23]),
                 delta_K=np.zeros((n, 2, 2), dtype=np.float32), tail_K=np.zeros(n, dtype=bool))
        records.append({"handoff": hid, "file": path.name, "sender_tokens": n,
                        "excluded": False, "archived_mean": {"K": 0, "V": 0}})
    manifest = {"records": records}
    (inputs / "manifest.json").write_text(json.dumps(manifest))
    args = SimpleNamespace(device="cuda", inputs=inputs, output=tmp_path / "output",
                           config=driver.ROOT / "config/cache-behavior.toml", resume=False, probe=True)
    driver.run(args, cfg, manifest)
    report_path = args.output / "report.json"
    first = report_path.read_bytes()
    report = json.loads(first)
    assert list(report["scores"]) == ["largest"]
    assert report["scores"]["largest"]["arms"]["oracle_ranked_10.5pct"]["recomputed"] == 3
    args.resume = True
    driver.run(args, cfg, manifest)
    assert report_path.read_bytes() == first


@pytest.mark.parametrize("fractions", [[.1, .1], [1.01], [0]])
def test_invalid_recompute_budgets_fail_before_model_loading(fractions):
    with pytest.raises(ValueError, match="oracle fractions"):
        driver.run(None, {"oracle_fractions": fractions}, None)
