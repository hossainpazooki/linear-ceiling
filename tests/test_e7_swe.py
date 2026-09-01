"""SWE-bench adapter tests, on synthetic LangChain-shaped fixtures (offline, no real traces)."""
import json

import pytest

from linear_ceiling.e7_lanes import lane_a
from linear_ceiling.e7_swe import MODEL_KEYS, load_composio, models_in
from linear_ceiling.e7_traces import approx_tokens


def counter(text, content_type="assistant"):
    return approx_tokens(text)


def _human(text):
    return {"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "HumanMessage"],
            "kwargs": {"content": text, "type": "human"}}


def _ai(text, model_id):
    return {"lc": 1, "type": "constructor", "id": ["langchain", "schema", "messages", "AIMessage"],
            "kwargs": {"content": text, "type": "ai",
                       "response_metadata": {"model_id": model_id}}}


def _llmresult(text, model_name):
    return {"llm_output": {"model_name": model_name}, "run": None,
            "generations": [[{"text": text, "type": "Generation"}]]}


FIXTURE = [
    [_human("solve this issue"), _ai("I will look at the file", "bedrock.claude-x")],
    [_llmresult("Summary of the agent run", "o1-mini-x")],
]


def test_detector_breadth_is_the_registered_minimum():
    # entry 0010: a narrower detector produces false NOT MEASURABLE and false zeros
    assert set(MODEL_KEYS) >= {"model", "model_id", "model_name"}


def test_models_in_finds_all_three_key_spellings():
    obj = {"a": {"model": "m1"}, "b": [{"model_id": "m2"}], "c": {"d": {"model_name": "m3"}}}
    assert sorted(set(models_in(obj))) == ["m1", "m2", "m3"]


def test_models_in_ignores_default_and_non_strings():
    assert models_in({"model": "default", "model_id": 7, "model_name": ""}) == []


def test_narrow_detector_would_miss_the_switch():
    """Pins the entry-0010 defect: matching only `model` sees nothing in this family."""
    assert models_in(FIXTURE, keys=("model",)) == []
    assert set(models_in(FIXTURE)) == {"bedrock.claude-x", "o1-mini-x"}


def test_load_composio_parses_both_node_shapes(tmp_path):
    p = tmp_path / "inst_traj.json"
    p.write_text(json.dumps(FIXTURE), encoding="utf-8")
    t = load_composio(p, agent="composio_swekit", counter=counter)
    assert t.suite == "swe-bench" and t.agent == "composio_swekit"
    roles = [m.role for m in t.messages]
    assert roles == ["user", "assistant", "assistant"]
    assert [m.model for m in t.messages] == ["bedrock.claude-x", "bedrock.claude-x", "o1-mini-x"]


def test_llmresult_response_is_not_dropped(tmp_path):
    """Regression: the second-stage model is recorded ONLY as an LLMResult in this family.
    Dropping that node made a real cross-model switch invisible to Lane A."""
    p = tmp_path / "inst_traj.json"
    p.write_text(json.dumps(FIXTURE), encoding="utf-8")
    t = load_composio(p, agent="a", counter=counter)
    assistants = [m for m in t.messages if m.role == "assistant"]
    assert len(assistants) == 2, "the LLMResult response must appear as an assistant turn"
    assert assistants[-1].tokens > 0


def test_lane_a_sees_the_switch(tmp_path):
    p = tmp_path / "inst_traj.json"
    p.write_text(json.dumps(FIXTURE), encoding="utf-8")
    t = load_composio(p, agent="a", counter=counter)
    a = lane_a(t)
    assert a.measurable is True
    assert a.switches == (1,)   # second assistant turn is served by a different model


def test_refuses_wrong_shape(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="expected a JSON list"):
        load_composio(p, agent="a", counter=counter)
    p.write_text(json.dumps([[{"unrecognized": 1}]]), encoding="utf-8")
    with pytest.raises(ValueError, match="wrong adapter for this shape"):
        load_composio(p, agent="a", counter=counter)


def test_nested_list_subrun_shape_is_read_in_full(tmp_path):
    """Entry 0017 defect (1): the 20241025 submission nests a sub-run's whole prompt as ONE
    LIST node before the LLMResult; the first adapter skipped it and read only responses."""
    nested = [[[_human("solve this issue"), _ai("looking at the file", "bedrock.claude-x")],
               _llmresult("Let me review the patch", "bedrock.claude-x")],
              [[_human("summarize the run")], _llmresult("Summary of the agent run", "o1-mini-x")]]
    p = tmp_path / "inst_traj.json"
    p.write_text(json.dumps(nested), encoding="utf-8")
    t = load_composio(p, agent="composio_swekit", counter=counter)
    roles = [m.role for m in t.messages]
    assert roles == ["user", "assistant", "assistant", "user", "assistant"]
    assert [m.request for m in t.messages] == [0, 0, 0, 1, 1]
    assert t.messages[3].tokens > 0                       # the prompt is counted, not dropped
    assert lane_a(t).switches == (2,)                     # Claude -> o1-mini, once
