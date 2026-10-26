import json
import tomllib
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
import torch
from transformers import Qwen3Config, Qwen3ForCausalLM

from tools.task_quality import cell
from tools.task_quality.pilot import digest

ROOT = cell.ROOT


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


def test_arm_list_labels_every_budget_and_refuses_bad_ones():
    assert [a for a, _ in cell.arm_list({"repair_fractions": [0.05, 0.1, 0.2]})] == \
        ["fresh", "reuse", "random", "repair_5pct", "repair_10pct", "repair_20pct"]
    for bad in ([0.1, 0.1], [1.01], [0]):
        with pytest.raises(ValueError):
            cell.arm_list({"repair_fractions": bad})


def test_cell_handoffs_apply_the_floor_and_run_the_largest_sender_first():
    def row(name, n, items):
        return {"handoff": name, "n_sender": n, "counts": {"valid_by_kind": {"signature": items}}}
    body = {"handoffs": [row("a", 10, 3), row("b", 50, 12), row("c", 90, 10), row("d", 70, 30)]}
    kept, void = cell.cell_handoffs(body, 10)
    assert [h["handoff"] for h in kept] == ["c", "d", "b"] and void == ["a"]


def test_retention_raw_and_floor_normalized_with_void_handoffs():
    per = {"fresh": [1.0, 0.8, 0.0, 0.5], "random": [0.2, 0.8, 0.0, 0.1], "reuse": [0.6, 0.8, 0.0, 0.3]}
    out = cell.retention(per, ["fresh", "random", "reuse"], 50, 1, ["h0", "h1", "h2", "h3"])
    assert out["reuse"]["raw"]["n"] == 3 and out["reuse"]["raw"]["void"] == 1
    assert out["reuse"]["raw"]["void_handoffs"] == ["h2"] and out["reuse"]["floor_normalized"]["void_handoffs"] == ["h1", "h2"]
    assert out["reuse"]["raw"]["median"] == pytest.approx(0.6)
    assert out["reuse"]["floor_normalized"]["n"] == 2 and out["reuse"]["floor_normalized"]["void"] == 2
    assert out["reuse"]["floor_normalized"]["median"] == pytest.approx(0.5)
    assert out["fresh"]["floor_normalized"]["median"] == 1.0 and out["random"]["floor_normalized"]["median"] == 0.0
    assert out["reuse"]["raw"]["bootstrap"]["low"] <= 0.6 <= out["reuse"]["raw"]["bootstrap"]["high"]


class Tokenizer:
    # Four token ids spell any question; the decode of any generation is one fixed def-line, so every
    # arm scores the same way and the summary's arithmetic is checkable by hand.
    eos_token_id = 0
    is_fast = True

    def encode(self, text, add_special_tokens=False):
        return [5, 6, 7, 8]

    def decode(self, ids):
        return "def run(self):"

    def convert_tokens_to_ids(self, token):
        return 0


def synthetic_cell(tmp_path, monkeypatch, model):
    """A two-handoff archive in the E9 layout, an items file over it, the config the reader re-reads
    under ROOT/config, and the run config (the same file, so the identity check passes)."""
    archive = tmp_path / "archive"
    for sub in ("align", "scores", "tokens"):
        (archive / sub).mkdir(parents=True)
    report = {"complete": True, "scores": {}}
    items = {"cell": "synthetic", "coverage_sha256": "x", "config_sha256": "x", "handoffs": []}
    for hid, n in (("20240101_a/b__c-1_traj#1", 12), ("20240101_a/b__d-2_traj#2", 6)):
        tokens = np.arange(1, n + 1)
        pairs = np.column_stack((np.arange(n), np.arange(n)))
        stem = hid.replace("/", "__").replace("#", "_sw")
        np.savez(archive / "align" / f"{stem}.npz", sender=tokens, receiver=tokens, pairs=pairs)
        np.savez(archive / "tokens" / f"{stem}.tokens.npz", same_K=np.ones((n, 2, 2), dtype=np.float32))
        (archive / "scores" / f"{stem}.json").write_text(json.dumps({"same": {"K": [{"sst": [1.0, 1.0]}, {"sst": [1.0, 1.0]}]}}))
        report["scores"][hid] = {"score_file": f"{stem}.json", "score_sha256": digest(archive / "scores" / f"{stem}.json"),
                                 "tokens_file": f"{stem}.tokens.npz",
                                 "tokens_sha256": digest(archive / "tokens" / f"{stem}.tokens.npz")}
        rows = [{"kind": "signature", "key": f"C.m{i}", "answer": "def run(self):" if i % 2 else "def go(self):",
                 "class": "C", "method": f"m{i}", "anchor": "", "answer_offset": 0, "in_receiver": True,
                 "valid": True, "first_token": i, "answer_tokens": [i]} for i in range(4)]
        rows.append({"kind": "repository", "key": "repository", "answer": "o/r", "anchor": "", "answer_offset": 0,
                     "in_receiver": True, "valid": True, "first_token": 0, "answer_tokens": [0]})
        items["handoffs"].append({"handoff": hid, "n_sender": n, "n_receiver": n, "n_matched": n, "trace_sha256": "x",
                                  "alignment_sha256": digest(archive / "align" / f"{stem}.npz"),
                                  "counts": {"valid_by_kind": {"signature": 4, "repository": 1}}, "items": rows})
    (archive / "report.json").write_text(json.dumps(report))
    items_path = tmp_path / "items.json"
    items_path.write_text(json.dumps(items))
    cfg = tomllib.loads((ROOT / "config/task-quality-cell.toml").read_text(encoding="utf-8"))
    cfg.update(chunk_tokens=2, min_form2_items=4, max_new_tokens=3, repair_fractions=[0.25], bootstrap_resamples=20)
    cfg["cells"]["long"] = {"items_file": str(items_path), "items_sha256": digest(items_path), "archive": str(archive)}
    (tmp_path / "config").mkdir()
    config_path = tmp_path / "config" / "task-quality-cell.toml"
    config_path.write_text("\n".join([f"seed = {cfg['seed']}", f"min_form2_items = {cfg['min_form2_items']}",
                                      f"bootstrap_resamples = {cfg['bootstrap_resamples']}",
                                      f"max_new_tokens = {cfg['max_new_tokens']}", "[headline]",
                                      f'form = "{cfg["headline"]["form"]}"', f'scorer = "{cfg["headline"]["scorer"]}"',
                                      'kinds = ["signature"]']) + "\n", encoding="utf-8")
    monkeypatch.setattr(cell, "ROOT", tmp_path)
    monkeypatch.setattr(cell, "load_model", lambda cfg, device: model)
    monkeypatch.setattr(cell, "load_tokenizer", lambda cfg: Tokenizer())
    monkeypatch.setattr(cell.subprocess, "check_output", lambda *a, **k: "deadbeef\n")
    return cfg, config_path


def test_run_scores_every_arm_and_the_summary_reads_the_headline(model, tmp_path, monkeypatch):
    cfg, config_path = synthetic_cell(tmp_path, monkeypatch, model)
    args = SimpleNamespace(device="cpu", output=tmp_path / "out", config=config_path, cell="long", resume=False, probe=False)
    cell.run(args, cfg)
    report = json.loads((tmp_path / "out" / "report.json").read_text())
    assert report["complete"] and list(report["handoffs"]) == report["run_order"]
    assert report["run_order"][0].endswith("#1") and report["void"] == []
    assert report["arms"] == ["fresh", "reuse", "random", "repair_25pct"]
    first = report["handoffs"][report["run_order"][0]]
    assert first["assembly"]["repair_25pct"]["recomputed"] == 3 and first["assembly"]["reuse"]["copied"] == 12
    assert len(first["items"]) == 5 and set(first["items"][0]["arms"]) == set(report["arms"])
    summary = json.loads((tmp_path / "out" / "summary.json").read_text())
    head = summary["headline"]
    assert head["pool"] == "signature" and head["items_per_handoff"] == [4, 4]
    # Two of four signature answers equal the fixed decode, under every arm and both handoffs.
    assert head["per_handoff"]["fresh"] == [0.5, 0.5] and head["accuracy"]["reuse"]["median"] == 0.5
    assert head["retention"]["reuse"]["raw"]["median"] == 1.0
    assert head["retention"]["reuse"]["floor_normalized"]["void"] == 2   # fresh == random everywhere
    assert head["retention"]["reuse"]["floor_normalized"]["void_handoffs"] == report["run_order"]
    assert summary["by_kind"]["chat"]["fresh"]["repository"]["mean"] == 0.0
    assert summary["sensitivity"]["plain"]["contains"]["form2"]["fresh"]["median"] == 0.5
    # Length guard: every item's generated length is read beside the accuracy, per form and arm.
    length = summary["length"]["chat"]["fresh"]
    assert length["n"] == 10 and length["cap"] == 3 and 0.0 <= length["at_cap"] <= 1.0
    assert 0.0 <= length["mean_generated_tokens"] <= 3.0
    assert set(summary["length"]["plain"]) == set(report["arms"])
    # Resume with an unchanged identity rewrites nothing; a tampered score is refused by the reader.
    before = (tmp_path / "out" / "report.json").read_bytes()
    args.resume = True
    cell.run(args, cfg)
    assert (tmp_path / "out" / "report.json").read_bytes() == before
    report["handoffs"][report["run_order"][0]]["items"][1]["arms"]["reuse"]["chat"]["first_span_exact"] = False
    (tmp_path / "out" / "report.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="stored score differs"):
        cell.summarize(tmp_path / "out")


def test_probe_runs_the_largest_sender_only(model, tmp_path, monkeypatch):
    cfg, config_path = synthetic_cell(tmp_path, monkeypatch, model)
    args = SimpleNamespace(device="cpu", output=tmp_path / "out", config=config_path, cell="long", resume=False, probe=True)
    cell.run(args, cfg)
    report = json.loads((tmp_path / "out" / "report.json").read_text())
    assert list(report["handoffs"]) == [report["run_order"][0]] and not report["complete"]
