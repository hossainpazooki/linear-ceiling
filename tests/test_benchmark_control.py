import json
import tomllib
from pathlib import Path

import pytest

from tools.task_quality import benchmark
from tools.task_quality.longbench_metrics import best_over_answers, normalize_answer, qa_f1_score

ROOT = Path(__file__).resolve().parents[1]


def test_longbench_qa_f1_is_the_copied_scorer():
    assert normalize_answer("The Ozalj  Castle.") == "ozalj castle"
    assert qa_f1_score("Miller v. California", "miller v california") == 1.0
    assert qa_f1_score("the Ozalj castle", "Ozalj") == pytest.approx(2 * (1 / 2) * 1 / (1 / 2 + 1))
    assert qa_f1_score("", "Ozalj") == 0
    assert best_over_answers("Ozalj", ["Zagreb", "Ozalj"]) == 1.0
    assert best_over_answers("nothing", []) == 0.0


def config():
    return tomllib.loads((ROOT / "config/benchmark-control-pilot.toml").read_text(encoding="utf-8"))


def test_compose_renders_the_passage_identically_in_s_and_r_and_locates_it():
    cfg = config()
    comp = benchmark.compose(cfg, "Passage 1:\nA line with \"quotes\".\n")
    rendered = benchmark.tool_result(cfg, "Passage 1:\nA line with \"quotes\".\n")
    assert "\n" not in rendered and '\\"quotes\\"' in rendered
    assert comp["sender"][slice(*comp["sender_span"])] == rendered
    assert comp["receiver"][slice(*comp["receiver_span"])] == rendered
    assert comp["receiver"].startswith("The following is the run of the agent")
    assert comp["receiver"].endswith("chronological points.")


def test_token_span_covers_every_overlapping_token():
    offsets = [(0, 3), (3, 5), (5, 9), (9, 12)]
    assert benchmark.token_span(offsets, 4, 9) == [1, 3]
    assert benchmark.token_span(offsets, 3, 5) == [1, 2]
    with pytest.raises(ValueError):
        benchmark.token_span(offsets, 12, 14)


def test_pilot_items_are_shortest_middle_longest_receiver():
    table = [{"index": i, "n_receiver": n} for i, n in enumerate([50, 10, 30, 70, 20])]
    assert [t["index"] for t in benchmark.pilot_items(table)] == [1, 2, 3]
    with pytest.raises(ValueError):
        benchmark.pilot_items(table[:2])


def test_load_set_refuses_a_file_whose_sha_moved(tmp_path, monkeypatch):
    path = tmp_path / "set.jsonl"
    path.write_text('{"input": "q", "context": "c", "answers": ["a"], "_id": "x"}\n', encoding="utf-8")
    cfg = {"data": {"sets": {"s": {"path": str(path), "sha256": "0" * 64}}}}
    monkeypatch.setattr(benchmark, "ROOT", Path("/"))
    with pytest.raises(ValueError, match="pinned sha"):
        benchmark.load_set(cfg, "s")
    cfg["data"]["sets"]["s"]["sha256"] = benchmark.digest(path)
    assert benchmark.load_set(cfg, "s")[0]["answers"] == ["a"]


def test_summarize_recomputes_f1_and_reads_the_gate(tmp_path):
    cfg = config()

    def item(index, prediction, answers, control="nothing", tokens=4):
        return {"index": index, "id": str(index), "n_receiver": 100 + index, "answers": answers,
                "forms": {form: {"prediction": prediction, "generated_tokens": tokens,
                                 "qa_f1": best_over_answers(prediction, answers),
                                 "no_context": {"prediction": control, "generated_tokens": 2,
                                                "qa_f1": best_over_answers(control, answers)}}
                          for form in ("plain", "chat")}}
    report = {"identity": {"config_sha256": benchmark.digest(ROOT / "config/benchmark-control-pilot.toml")},
              "complete": True, "prompts": cfg["prompts"],
              "sets": {"a": {"n_items": 3, "table": [], "items": [item(0, "Ozalj", ["Ozalj"]), item(1, "x", ["y"]),
                                                                  item(2, "Ozalj castle", ["Ozalj"], tokens=32)]},
                       "b": {"n_items": 3, "table": [], "items": [item(0, "x", ["y"]), item(1, "x", ["y"]), item(2, "x", ["y"])]}}}
    (tmp_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
    body = benchmark.summarize(tmp_path)
    a, b = body["forms"]["chat"]["a"], body["forms"]["chat"]["b"]
    assert a["median_qa_f1"] == pytest.approx(2 / 3) and a["within_gate"] is True and a["at_cap"] == 1
    assert b["median_qa_f1"] == 0.0 and b["within_gate"] is False
    assert a["no_context_median_qa_f1"] == 0.0
    assert body["forms"]["plain"]["pooled"]["n"] == 6
    assert (tmp_path / "summary.json").exists()
    report["sets"]["a"]["items"][0]["forms"]["chat"]["qa_f1"] = 0.5
    (tmp_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError, match="stored score differs"):
        benchmark.summarize(tmp_path)
