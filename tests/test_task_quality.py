import json
from types import SimpleNamespace

import numpy as np
import pytest

from tools.task_quality.items import (canonical, canonical_contains, contains, deduplicate, exact_match, extract,
                                      first_span_exact, items_for_handoff, lines_of, locate, normalize, token_f1)
from tools.task_quality import pilot

BLOCK = ('{"data": {"result": "<Total 2 result(s) found:>\\n## Details about shortlisted result ID 0:\\n'
         'Class signature: class Model:\\nFile where defined: pkg/core.py\\nClass full name: pkg.core.Model\\n'
         'Functions accessible:\\n* Signature: def rename(self, name): | Member of `Model` class\\n'
         '* Signature: def evaluate(self, *args, **kw): | Member of `Model` class\\n'
         '## Details about shortlisted result ID 1:\\nClass signature: class Other:\\n'
         'File where defined: pkg/other.py\\nClass full name: pkg.other.Other\\nFunctions accessible:\\n'
         '* Signature: def run(self): | Member of `Other` class\\n"}}')
SENDER = "You have the repository org/repo cloned in the workspace.\n" + BLOCK + "\nlater text\n" + BLOCK


def test_lines_split_every_newline_rendering_and_drop_list_markers():
    text = "a\\nb\\\\n* c\nd"
    assert [line for _, _, line in lines_of(text)] == ["a", "b", "c", "d"]
    starts = [text[s:e] for s, e, _ in lines_of(text)]
    assert starts == ["a", "b", "c", "d"]


def test_extract_pairs_file_with_its_class_and_signature_with_its_owner():
    candidates = extract(SENDER)
    kinds = {c["kind"] for c in candidates}
    assert kinds == {"file", "signature", "repository"}
    files = {c["key"]: c["answer"] for c in candidates if c["kind"] == "file"}
    assert files == {"pkg.core.Model": "pkg/core.py", "pkg.other.Other": "pkg/other.py"}
    signatures = {c["key"]: c["answer"] for c in candidates if c["kind"] == "signature"}
    assert signatures == {"Model.rename": "def rename(self, name):", "Model.evaluate": "def evaluate(self, *args, **kw):",
                          "Other.run": "def run(self):"}
    file_item = next(c for c in candidates if c["key"] == "pkg.core.Model")
    # The anchor runs from the file line through the class line, in the raw rendering.
    assert file_item["anchor"] == "File where defined: pkg/core.py\\nClass full name: pkg.core.Model"
    assert file_item["anchor"][file_item["answer_offset"]:].startswith("pkg/core.py")
    repo = next(c for c in candidates if c["kind"] == "repository")
    assert repo["answer"] == "org/repo"


def test_file_line_without_a_class_line_in_the_same_block_is_not_an_item():
    text = "## Details about shortlisted result ID 0:\\nFile where defined: a.py\\n## Details about shortlisted result ID 1:\\nClass full name: x.Y\\n"
    assert extract(text) == []


def test_signature_without_an_owner_is_skipped():
    assert extract("Signature: def free(a):\\n") == []
    assert extract("Signature: def free(a): | Defined in `p.py` | Not a member of any class\\n") == []


def test_signature_renderings_with_annotation_comment_decorators_and_defined_in():
    lines = ("Signature: def tolist(self) -> Any: | Member of `A` class",
             "Signature: def _fix(self): # a comment # more | Member of `A` class",
             "Signature: def run(self, x): | Defined in `pkg/a.py` | Member of `A` class | Decorators: @staticmethod",
             "Signature: def __abs__(self: NDArray[object_]) -> Any: | Member of `A` class | Decorators: @overload",
             "Signature: def cut( self, axis: None | _ShapeLike = | Member of `A` class | Decorators: @overload",
             "Signature: def nonzero(self) -> tuple[ndarray[Any, _dtype[intp]], | Member of `A` class")
    items = extract("\\n".join(lines))
    assert [(i["method"], i["answer"]) for i in items] == [
        ("tolist", "def tolist(self) -> Any:"), ("_fix", "def _fix(self):"), ("run", "def run(self, x):"),
        ("__abs__", "def __abs__(self: NDArray[object_]) -> Any:")]
    assert all(i["class"] == "A" for i in items)


def test_deduplicate_keeps_one_item_per_key_and_drops_conflicting_answers():
    candidates = extract(SENDER)
    assert len(candidates) == 2 * 5 + 1
    items, ambiguous = deduplicate(candidates)
    assert len(items) == 6 and ambiguous == 0
    conflicting = candidates + [{"kind": "file", "key": "pkg.core.Model", "answer": "moved.py", "anchor": "x", "answer_offset": 0}]
    items, ambiguous = deduplicate(conflicting)
    assert ambiguous == 1 and all(i["key"] != "pkg.core.Model" or i["kind"] != "file" for i in items)


def fake_offsets(text):
    # One token per whitespace-free chunk of up to four characters.
    offsets, position = [], 0
    for piece in text.split(" "):
        for start in range(0, len(piece), 4):
            offsets.append((position + start, position + min(start + 4, len(piece))))
        position += len(piece) + 1
    return offsets


def test_locate_uses_first_occurrence_and_requires_every_answer_token_matched():
    receiver = "intro " + SENDER
    offsets = fake_offsets(receiver)
    items, _ = deduplicate(extract(SENDER))
    everything = np.arange(len(offsets))
    located = locate(items, receiver, offsets, everything)
    assert all(row["valid"] and row["in_receiver"] for row in located)
    first = next(row for row in located if row["key"] == "pkg.core.Model")
    assert receiver[first["answer_char_start"]:].startswith("pkg/core.py")
    assert receiver.find(first["anchor"]) == first["answer_char_start"] - first["answer_offset"]
    # Remove one answer token from M: that item alone becomes invalid.
    without = np.setdiff1d(everything, [first["answer_tokens"][1]])
    located = locate(items, receiver, offsets, without)
    assert not next(row for row in located if row["key"] == "pkg.core.Model")["valid"]
    assert sum(row["valid"] for row in located) == len(items) - 1
    # An item absent from R is invalid and carries no span.
    located = locate(items, "nothing here", fake_offsets("nothing here"), np.array([0]))
    assert all(not row["valid"] and not row["in_receiver"] and row["first_token"] is None for row in located)


def test_items_for_handoff_counts():
    receiver = SENDER.replace("pkg/other.py", "pkg/elsewhere.py", 1)
    offsets = fake_offsets(receiver)
    located, counts = items_for_handoff(SENDER, receiver, offsets, np.arange(len(offsets)))
    assert counts["candidate_lines"] == 11 and counts["distinct"] == 6 and counts["ambiguous_keys"] == 0
    assert counts["in_receiver"] == 6 and counts["valid"] == 6
    assert counts["valid_by_kind"] == {"file": 2, "signature": 3, "repository": 1}


def test_scoring_is_judge_free_and_tolerant_of_wrapping_only():
    assert normalize(" `pkg/core.py`.\nmore") == "pkg/core.py"
    assert exact_match(" pkg/core.py\n", "pkg/core.py")
    assert not exact_match("pkg/Core.py", "pkg/core.py")
    assert token_f1("rename(self, name)", "def rename(self, name):") == pytest.approx(2 * (6 / 6) * (6 / 8) / (1 + 6 / 8))
    assert token_f1("", "def run(self):") == 0.0
    assert contains("The signature is: `def run(self):` | Member", "def run(self):")
    assert contains("def  run(self):", "def run(self):")   # whitespace collapsed on both sides
    assert contains("def run(self, x):", "def run(self):") is False
    # The pilot's reading: the first def-span, after undoing the trace's JSON escaping.
    gold = 'def _verify(self, option=\\"warn\\"):'
    assert canonical(gold) == 'def _verify(self, option="warn"):'
    assert canonical("def run( self, x )") == "def run(self, x)"
    assert first_span_exact('The signature is:\n\n`def _verify(self, option="warn"):`', gold)
    assert first_span_exact("1. `def clear(self):`  \n2. `def clear(cls):`", "def clear(cls):") is False
    assert first_span_exact("no signature here", gold) is False
    assert first_span_exact("It is in `pkg/core.py`, see x.py", "pkg/core.py", "file")
    assert first_span_exact("The repo is org/repo.", "org/repo", "repository")
    assert canonical_contains('x def _verify(self, option="warn"): y', gold)
    # Two real pilot generations the first reader failed for no reason of content: a fenced block
    # drops the colon; a wrapped parameter list breaks the line inside the parentheses.
    appended = "def append(self, card=None, useblanks=True, bottom=False, end=False):"
    assert first_span_exact("```python\ndef append(self, card=None, useblanks=True, bottom=False, end=False)\n```", appended)
    collect = "def collect(self, objs, source=None, nullable=False, collect_related=True, source_attr=None, ...):"
    assert first_span_exact("def collect(self, objs, source=None, nullable=False, collect_related=True,\n"
                            "            source_attr=None, ...):", collect)
    assert first_span_exact("def append(self, card=None):", appended) is False   # wrong arity still fails
    assert first_span_exact("def f(x) -> Tuple[int, str]:\nmore", "def f(x) -> Tuple[int, str]:")
    assert first_span_exact("`def f(x) -> int` is it", "def f(x) -> int:")
    # An unclosed decoy never swallows the next def-line into its parentheses (skeptic pass, 2026-10-21).
    assert first_span_exact("def foo(a, b is the method.\ndef foo(a, b):", "def foo(a, b):")
    assert first_span_exact("not def bar(x but rather:\n\ndef foo(self, a):", "def foo(self, a):")


def test_writes_are_lf_and_text_hashes_ignore_the_checkout_newline(tmp_path):
    from tools.task_quality import pilot
    path = tmp_path / "a.json"
    pilot.write(path, {"k": [1, 2]})
    assert b"\r\n" not in path.read_bytes()
    crlf = tmp_path / "b.json"
    crlf.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert pilot.text_digest(crlf) == pilot.text_digest(path) == pilot.digest(path) != pilot.digest(crlf)
    assert pilot.same_text(pilot.digest(crlf), crlf) and pilot.same_text(pilot.digest(path), crlf)
    assert not pilot.same_text("0" * 64, path)


def test_pilot_handoffs_are_shortest_middle_longest_sender_above_the_floor():
    def row(i, n, items):
        return {"handoff": f"h{i}", "n_sender": n, "counts": {"valid_by_kind": {"signature": items, "repository": 1}}}
    body = {"handoffs": [row(i, n, k) for i, (n, k) in enumerate([(50, 12), (10, 0), (40, 10), (30, 11), (20, 9), (60, 3)])]}
    assert [h["handoff"] for h in pilot.pilot_handoffs(body, 10)] == ["h3", "h2", "h0"]
    assert [h["handoff"] for h in pilot.pilot_handoffs(body, 0)] == ["h1", "h2", "h5"]
    with pytest.raises(ValueError, match="floor"):
        pilot.pilot_handoffs(body, 11)


def test_drawn_items_caps_form2_by_seed_and_always_adds_the_repository_item():
    items = [{"kind": "signature", "key": f"C.m{i}", "valid": True, "first_token": i} for i in range(50)]
    items += [{"kind": "file", "key": "x", "valid": False, "first_token": 0},
              {"kind": "repository", "key": "repository", "valid": True, "first_token": 3}]
    cfg = {"max_items_per_handoff": 5, "seed": 7}
    drawn = pilot.drawn_items({"items": items}, cfg, 0)
    assert len(drawn) == 6 and drawn[-1]["kind"] == "repository"
    assert all(it["valid"] for it in drawn)
    assert drawn == pilot.drawn_items({"items": items}, cfg, 0)
    assert drawn != pilot.drawn_items({"items": items}, cfg, 1)


def test_summarize_recomputes_scores_and_reads_the_gate(tmp_path, monkeypatch):
    cfg_path = pilot.ROOT / "config/task-quality-pilot.toml"
    def item(kind, answer, prediction):
        return {"kind": kind, "key": answer, "answer": answer, "first_token": 0, "answer_tokens": [0],
                "question": "q", "forms": {"plain": {"prediction": prediction, "generated_tokens": 1,
                                                     "exact_match": exact_match(prediction, answer),
                                                     "contains": contains(prediction, answer),
                                                     "token_f1": token_f1(prediction, answer), "seconds": 0.0}}}
    report = {"identity": {"config_sha256": pilot.digest(cfg_path)}, "prompts": {"plain": {}}, "complete": True,
              "handoffs": [{"handoff": "a", "items": [item("file", "p/a.py", "p/a.py"), item("signature", "def f():", "nope")]},
                           {"handoff": "b", "items": [item("file", "p/b.py", "p/b.py"), item("repository", "o/r", "o/r")]},
                           {"handoff": "c", "items": [item("signature", "def g():", "def g():")]}]}
    pilot.write(tmp_path / "report.json", report)
    body = pilot.summarize(tmp_path)
    form = body["forms"]["plain"]
    assert [h["exact_match"] for h in form["per_handoff"]] == [0.5, 1.0, 1.0]
    assert form["median_exact_match"] == 1.0 and form["within_gate"]["exact_match"] is False
    assert form["median_first_span_exact"] == 1.0 and form["by_kind"]["signature"]["first_span_exact"] == 0.5
    assert form["by_kind"]["repository"]["n"] == 1
    report["handoffs"][0]["items"][1]["forms"]["plain"]["exact_match"] = True
    pilot.write(tmp_path / "report.json", report)
    with pytest.raises(ValueError, match="recomputed"):
        pilot.summarize(tmp_path)


def test_greedy_answer_restores_the_prefix_and_stops_at_newline():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers import Qwen3Config, Qwen3ForCausalLM
    from tools.cache_behavior.core import prefill
    torch.manual_seed(1)
    cfg = Qwen3Config(vocab_size=16, hidden_size=16, intermediate_size=24, num_hidden_layers=2,
                      num_attention_heads=2, num_key_value_heads=1, head_dim=8, max_position_embeddings=4096,
                      rope_parameters={"rope_type": "yarn", "rope_theta": 10000.0, "factor": 2.0,
                                       "original_max_position_embeddings": 2048})
    cfg._attn_implementation = "sdpa"
    model = Qwen3ForCausalLM(cfg).eval()
    tokenizer = SimpleNamespace(decode=lambda ids: "".join("\n" if i == 5 else "x" for i in ids))
    cache = prefill(model, np.array([1, 2, 3, 4]), 2)
    generated = pilot.greedy_answer(model, tokenizer, cache, 4, [6, 7], 8, {0}, stop_at_newline=True)
    assert cache.get_seq_length() == 4
    assert len(generated) <= 8 and (5 not in generated[:-1])
    unstopped = pilot.greedy_answer(model, tokenizer, cache, 4, [6, 7], 8, {0})
    assert unstopped[:len(generated)] == generated and cache.get_seq_length() == 4
    again = pilot.greedy_answer(model, tokenizer, cache, 4, [6, 7], 8, {0}, stop_at_newline=True)
    assert again == generated
