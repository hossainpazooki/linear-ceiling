"""Role/content adapter and layout-discovery tests (offline, synthetic fixtures)."""
import json

import pytest

from linear_ceiling.e7_rolecontent import (
    content_text, find_message_list, load_role_content, load_role_content_trajectory,
)
from linear_ceiling.e7_swe import discover_trajectories, load_jsonl
from linear_ceiling.e7_traces import approx_tokens


def counter(text, content_type="assistant"):
    return approx_tokens(text)


PLAIN = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"},
         {"role": "assistant", "content": "hello"}]
WITH_AGENT = [{"role": "user", "content": "hi", "agent": "planner"},
              {"role": "assistant", "content": "ok", "agent": "planner"}]
WITH_TEMPLATE = [{"role": "user", "content": "hi", "template": "t1"},
                 {"role": "assistant", "content": "ok", "template": "t1"}]
NESTED = {"messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "ok"}]}
BLOCKS = [{"role": "assistant", "content": [{"type": "text", "text": "part1"},
                                            {"type": "text", "text": "part2"}]}]


@pytest.mark.parametrize("doc,n", [(PLAIN, 3), (WITH_AGENT, 2), (WITH_TEMPLATE, 2), (NESTED, 2)])
def test_all_four_observed_variants_parse(tmp_path, doc, n):
    p = tmp_path / "inst.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    t = load_role_content(p, agent="a", counter=counter)
    assert len(t.messages) == n and t.suite == "swe-bench"


def test_content_blocks_are_joined():
    assert content_text([{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]) == "ab"
    assert content_text("plain") == "plain"
    assert content_text(None) == ""


def test_find_message_list_rejects_non_message_documents():
    assert find_message_list({"selected_patch": "x", "reason": "y"}) is None
    assert find_message_list([{"no_role": 1}]) is None
    assert find_message_list([]) is None


def test_tool_calls_add_tokens_and_names(tmp_path):
    doc = [{"role": "assistant", "content": "",
            "tool_calls": [{"function": {"name": "edit", "arguments": {"path": "a.py"}}}]}]
    p = tmp_path / "i.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    t = load_role_content(p, agent="a", counter=counter)
    assert t.messages[0].has_tool_calls and t.messages[0].tool_names == ("edit",)
    assert t.messages[0].tokens > 0


def test_discover_flat_layout_one_file_is_one_trajectory(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    for name in ("astropy__a-1.json", "astropy__a-2.json"):
        (d / name).write_text(json.dumps(PLAIN), encoding="utf-8")
    groups = discover_trajectories(d)
    assert [g[0] for g in groups] == ["astropy__a-1", "astropy__a-2"]
    assert all(len(files) == 1 for _, files in groups)


def test_discover_nested_layout_many_files_are_one_trajectory(tmp_path):
    """The counting bug this exists to prevent: a nested instance presenting as N trajectories."""
    d = tmp_path / "sub"
    inst = d / "astropy__a-1" / "attempt_0"
    inst.mkdir(parents=True)
    (inst / "context_agent.json").write_text(json.dumps(PLAIN), encoding="utf-8")
    (inst / "patching_agent.json").write_text(json.dumps(WITH_TEMPLATE), encoding="utf-8")
    (inst / "patch_0.diff").write_text("--- a\n+++ b\n", encoding="utf-8")
    (d / "astropy__a-1" / "selected_patch.json").write_text(json.dumps({"selected_patch": "x"}), encoding="utf-8")
    groups = discover_trajectories(d)
    assert len(groups) == 1, "one instance directory is ONE trajectory, not one per file"
    tid, files = groups[0]
    assert tid == "astropy__a-1" and len(files) == 4


def test_nested_trajectory_concatenates_stages_and_skips_non_trajectories(tmp_path):
    d = tmp_path / "sub"
    inst = d / "inst" / "attempt_0"
    inst.mkdir(parents=True)
    (inst / "a_agent.json").write_text(json.dumps(PLAIN), encoding="utf-8")          # 3 msgs
    (inst / "b_agent.json").write_text(json.dumps(WITH_TEMPLATE), encoding="utf-8")  # 2 msgs
    (inst / "patch_0.diff").write_text("not json", encoding="utf-8")
    (inst / "regression_test_result_0.json").write_text(json.dumps({"no_additional_failure": True}), encoding="utf-8")
    (tid, files), = discover_trajectories(d)
    t = load_role_content_trajectory(files, agent="a", traj_id=tid, counter=counter)
    assert len(t.messages) == 5, "stage files concatenate; the diff and result blob are skipped"


def test_jsonl_stage_file_is_read(tmp_path):
    p = tmp_path / "reproducer_agent.jsonl"
    p.write_text("\n".join(json.dumps(m) for m in PLAIN), encoding="utf-8")
    assert len(load_jsonl(p)) == 3
    t = load_role_content_trajectory([p], agent="a", traj_id="i", counter=counter)
    assert len(t.messages) == 3


def test_trajectory_with_no_messages_is_refused(tmp_path):
    d = tmp_path / "only_blobs"
    d.mkdir()
    p = d / "selected_patch.json"
    p.write_text(json.dumps({"selected_patch": "x"}), encoding="utf-8")
    with pytest.raises(ValueError, match="wrong adapter"):
        load_role_content_trajectory([p], agent="a", traj_id="i", counter=counter)
