"""fab_reuse on synthetic log trees in the pinned harness's layout (model-library 0.1.37's agent writer)."""
import gzip
import hashlib
import json
import re
import tomllib
from pathlib import Path

import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling import fab_reuse as m

READER = (Path.home() / ".cache" / "huggingface" / "hub" / "models--Qwen--Qwen3-1.7B" / "snapshots"
          / "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e" / "tokenizer.json")
MODEL = "anthropic/claude-opus-5-5-no-fallback"
OVERWRITE = "WARNING: The key already exists in the data storage. The new result overwrites the old one.\n"
T0 = 1_795_000_000.0                                                  # turn n's timestamp is T0 + 1000 n
TURN_MD = {"in_tokens": 100, "cache_read_tokens": 40, "cache_write_tokens": 10, "out_tokens": 5}
HELPER_MD = {"in_tokens": 50, "cache_read_tokens": None, "cache_write_tokens": None, "out_tokens": 5}


def harness_format(prompt, ranges, state):
    """finance_agent/tools.py _validate_inputs + _format_prompt at the pin, copied, for an independent check."""
    rd = {}
    for spec in ranges or []:
        rd[spec["key"]] = (spec["start"], spec["end"])

    def replace(match):
        key = match.group(1)
        doc = state[key]
        if key in rd:
            s, e = rd[key]
            return doc[s:e]
        return doc
    return re.sub(r"{{([^{}]+)}}", replace, prompt)


def chars(text):
    return [ord(c) for c in text], [(i, i + 1) for i in range(len(text))]


def pairs(text):
    return ([ord(text[i]) * 1000 + (ord(text[i + 1]) if i + 1 < len(text) else 0) for i in range(0, len(text), 2)],
            [(i, min(i + 2, len(text))) for i in range(0, len(text), 2)])


def gap_at_q(text):
    """One token per character, except that a 'Q' is folded into the token before it, whose offsets stay as they
    were (as NFC folds a combining mark): the 'Q' is covered by no offset."""
    ids, offs = [], []
    for i, c in enumerate(text):
        if c == "Q" and ids:
            ids[-1] = ids[-1] * 7 + 1
        else:
            ids.append(ord(c))
            offs.append((i, i + 1))
    return ids, offs


def _record(name, args, output, error=None):
    return {"tool_call": {"id": "c", "call_id": None, "name": name, "args": args, "parsed_args": args},
            "tool_output": {"output": output, "error": error, "metadata": None, "done": False,
                            "success": error is None},
            "duration_seconds": 1.0 if name == "parse_html_page" else 2.0, "error": None, "success": error is None}


def _stamp(n):
    import datetime as dt
    return dt.datetime.fromtimestamp(T0 + 1000 * n, dt.timezone.utc).isoformat()


def _dump(path, obj, gz=False):
    body = json.dumps(obj, indent=2, default=str).encode()
    if gz:
        path.with_name(path.name + ".gz").write_bytes(gzip.compress(body))
    else:
        path.write_bytes(body)


def write_traj(root, task_id, turns, init_state=None, stamp="2026-11-20_00-00-00_abcdef",
               tool="retrieve_information", gz_state=False, model=MODEL, error_turns=(), hist_kind="text",
               final=True, compactions=(), turn_md=TURN_MD, helper_md=HELPER_MD, stamps=_stamp, stop_reason="done_tool"):
    """One log directory as the pinned harness writes it. `turns` holds one list of tool events per turn, in order:
    ("parse", key, text) a successful parse_html_page; ("parse_failed", key) a failed one, which writes nothing;
    ("parse_error_text", key) a failed one whose output still holds the success text; ("parse_no_text", key) one
    with no error whose output lacks it (neither writes); ("retrieve", args) a sub-call whose sent text is the
    harness's substitution over the store at that moment; ("retrieve", args, sent) the same with the logged sent
    text given. Turn numbers in `error_turns` get a directory holding error.json alone, as model-library 0.1.37 writes
    a turn whose query failed; the event lists fill the other numbers in order. No event list is a failed launch.
    Each answered turn's query and each sub-call carry a usage record (`turn_md`, `helper_md`) and the turn its
    timestamp (`stamps(n)`); `final=False` leaves out the root result.json, as when the process was ended, and
    `stop_reason` is the final record's (model-library's AgentStopReason value)."""
    q = root / "finance" / "model" / stamp / task_id
    init = q / "turns" / "init"
    init.mkdir(parents=True)
    _dump(init / "config.json", {"llm": {"provider": "anthropic", "model_name": "m", "_registry_key": model},
                                 "agent_config": {}, "tools": []})
    _dump(init / "state.json", init_state or {})
    (init / "history.json").write_text("[]")
    if final:
        _dump(q / "result.json", {"stop_reason": stop_reason, "final_answer": "x",
                                  "compactions": [{"turn_number": 1, "metadata": c} for c in compactions]})
    state = dict(init_state or {})
    todo = list(turns)
    for n in range(1, len(turns) + len(error_turns) + 1):
        td = q / "turns" / f"turn_{n:03d}"
        td.mkdir()
        if n in error_turns:
            _dump(td / "error.json", {"timestamp": "t", "error": {"type": "APIError", "message": "x"},
                                      "duration_seconds": 1.0})
            continue
        events = todo.pop(0)
        records = []
        for i, ev in enumerate(events):
            if ev[0] == "parse":
                said = (OVERWRITE if ev[1] in state else "") + \
                    f"SUCCESS: The result has been saved to the data storage under the key: {ev[1]}.\n"
                state[ev[1]] = ev[2]
                records.append(_record("parse_html_page", {"url": "u", "key": ev[1]}, said))
            elif ev[0] == "parse_failed":
                records.append(_record("parse_html_page", {"url": "u", "key": ev[1]}, "HTTP 404", "HTTP 404"))
            elif ev[0] == "parse_error_text":
                said = f"SUCCESS: The result has been saved to the data storage under the key: {ev[1]}.\n"
                records.append(_record("parse_html_page", {"url": "u", "key": ev[1]}, said, "late failure"))
            elif ev[0] == "parse_no_text":
                records.append(_record("parse_html_page", {"url": "u", "key": ev[1]}, "Could not fetch the page."))
            else:
                args = ev[1]
                sent = ev[2] if len(ev) > 2 else harness_format(args["prompt"], args.get("input_character_ranges"),
                                                                state)
                records.append(_record(tool, args, "answer"))
                hd = td / "helper_queries" / f"tool_{i:03d}"
                hd.mkdir(parents=True)
                _dump(hd / "result.json", {"turn_number": n, "tool_index": i, "tool_call": records[-1]["tool_call"],
                                           "query_result": {"output_text": "ok", "metadata": helper_md}})
                (hd / "history.json").write_text(json.dumps([{"kind": hist_kind, "text": sent},
                                                             {"kind": "raw_response", "response": "eA=="}]))
        _dump(td / "result.json", {"timestamp": stamps(n), "query_result": {"output_text": "", "metadata": turn_md},
                                   "tool_call_records": records, "duration_seconds": 9.0})
        _dump(td / "state.json", state, gz=gz_state)
    return q


def R(prompt, *ranges):
    args = {"prompt": prompt}
    if ranges:
        args["input_character_ranges"] = [{"key": k, "start": s, "end": e} for k, s, e in ranges]
    return ("retrieve", args)


def counts(r):
    return r["new"], r["same_offset"], r["different_offset"]


def test_repeat_at_the_same_offset_then_a_range_at_another(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abcdefghij"), R("Q: {{d}}")], [R("Q: {{d}}")],
                                       [R("Longer: {{d}}", ("d", 2, 8))]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and r["reason"] is None and r["serving_model"] == MODEL and r["stop_reason"] == "done_tool"
    assert r["ended_by_itself"] is True
    assert (r["subcalls"], r["prompt_tokens"], r["document_tokens"]) == (3, 13 + 13 + 14, 26)
    assert counts(r) == (10, 10, 6) and r["prefix_shared"] == 13 and r["documents"] == 1
    assert (r["reused_fraction"], r["new_fraction"], r["prefix_shared_fraction"]) == (16 / 26, 10 / 26, 13 / 40)


def test_a_key_overwritten_later_in_the_turn_takes_its_earlier_value(tmp_path):
    a, b = "ABCDEFghij", "ABCDEFxyz"                 # the same first six characters
    q = write_traj(tmp_path, "row01", [[("parse", "f", a), R("{{f}}")], [R("{{f}}", ("f", 0, 6)), ("parse", "f", b)]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and counts(r) == (10, 6, 0) and r["documents"] == 1


def test_a_write_earlier_in_the_turn_is_read_from_its_snapshot_and_one_on_both_sides_is_not_measurable(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "old"), R("{{d}}")], [("parse", "d", "new text"), R("{{d}}")]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and r["documents"] == 2 and counts(r) == (11, 0, 0)
    q = write_traj(tmp_path, "row02", [[("parse", "d", "one"), R("{{d}}"), ("parse", "d", "two")]])
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "reconstruction"


def test_a_failed_write_is_not_a_write(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "old"), R("{{d}}")],
                                       [("parse_failed", "d"), R("{{d}}"), ("parse", "d", "new")]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and counts(r) == (3, 3, 0)


def test_a_turn_whose_query_failed_falls_back_to_the_latest_earlier_snapshot(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "kept text"), R("{{d}}")],
                                       [R("{{d}}"), ("parse", "d", "replaced")]], error_turns=(2,))
    assert [x.name for x in (q / "turns" / "turn_002").iterdir()] == ["error.json"]
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and counts(r) == (9, 9, 0) and (r["turns"], r["error_turns"]) == (3, 1)
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]], error_turns=(3,))
    r = m.measure_trajectory(q, chars, tmp_path)     # the run's last query failed
    assert r["measurable"] and counts(r) == (3, 3, 0) and r["error_turns"] == 1


def test_a_turn_with_neither_a_result_nor_the_error_record_alone_is_unreadable(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]], error_turns=(2,))
    (q / "turns" / "turn_002" / "error.json").unlink()
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]], error_turns=(2,))
    (q / "turns" / "turn_002" / "state.json").write_text("{}")
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"
    q = write_traj(tmp_path, "row03", [[("parse", "d", "abc"), R("{{d}}")]])
    (q / "turns" / "turn_001" / "error.json").write_text("{}")
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"
    q = write_traj(tmp_path, "row04", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]], error_turns=(2,))
    src = q / "turns" / "turn_001" / "helper_queries" / "tool_001"
    dst = q / "turns" / "turn_002" / "helper_queries" / "tool_000"
    dst.mkdir(parents=True)
    for f in src.iterdir():
        (dst / f.name).write_bytes(f.read_bytes())
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"   # a helper beside error.json


def test_turn_numbers_with_a_gap_are_unreadable(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]])
    assert m.measure_trajectory(q, chars, tmp_path)["measurable"]
    (q / "turns" / "turn_002").rename(q / "turns" / "turn_003")      # a turn whose capture failed, with no helper
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"


def test_a_sub_call_its_turn_records_do_not_yet_list_is_unreadable(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    f = q / "turns" / "turn_001" / "result.json"
    res = json.loads(f.read_text())
    res["tool_call_records"] = res["tool_call_records"][:1]          # killed between the helper write and the rewrite
    f.write_text(json.dumps(res))
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"


def test_the_both_sides_guard_is_what_refuses_a_value_no_snapshot_holds(tmp_path):
    a, b = "ABCDEFghij", "ABCDEFxyz"                 # the same first six characters: the rebuild alone cannot tell
    q = write_traj(tmp_path, "row01", [[("parse", "f", a), R("{{f}}")],
                                       [("parse", "f", a), R("{{f}}", ("f", 0, 6)), ("parse", "f", b)]])
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "reconstruction"


@pytest.mark.parametrize("half", ["parse_error_text", "parse_no_text"])
def test_a_write_needs_both_no_error_and_the_success_text(tmp_path, half):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "old"), R("{{d}}")],
                                       [(half, "d"), R("{{d}}"), ("parse", "d", "new")]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and counts(r) == (3, 3, 0)


def test_a_sub_call_its_turn_records_do_not_place_is_reconstruction(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    f = q / "turns" / "turn_001" / "result.json"
    res = json.loads(f.read_text())
    res["tool_call_records"][1]["tool_call"]["parsed_args"] = {"prompt": "{{d}} "}
    f.write_text(json.dumps(res))
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "reconstruction"


def test_a_helper_record_with_no_call_is_unreadable_not_an_abort(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    f = q / "turns" / "turn_001" / "helper_queries" / "tool_001" / "result.json"
    res = json.loads(f.read_text())
    del res["tool_call"]
    f.write_text(json.dumps(res))
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"


def test_a_call_not_rebuilt_makes_the_trajectory_not_measurable_never_zero(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}"), ("retrieve", {"prompt": "{{d}}"}, "x")]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert not r["measurable"] and r["reason"] == "reconstruction" and r["subcalls"] == 2
    assert all(r[k] is None for k in (*m.COUNTS, *m.FRACTIONS))
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")]], hist_kind="image")
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "reconstruction"


def test_no_sub_call_and_no_document_token_are_not_measurable(tmp_path):
    a = write_traj(tmp_path, "row01", [[("parse", "d", "abc")]])
    b = write_traj(tmp_path, "row02", [[R("x {{d}}"), R("x {{d}}")]], init_state={"d": ""})
    ra, rb = m.measure_trajectory(a, chars, tmp_path), m.measure_trajectory(b, chars, tmp_path)
    assert (ra["reason"], ra["subcalls"]) == ("no sub-call", 0)
    assert (rb["reason"], rb["subcalls"]) == ("no document token", 2)


def test_an_encoder_failure_is_tokenization(tmp_path):
    def boom(text):
        raise RuntimeError("cannot encode")
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    assert m.measure_trajectory(q, boom, tmp_path)["reason"] == "tokenization"


def test_a_token_across_either_span_edge_is_template_text(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("Q{{d}}"), R("Q{{d}}")]], init_state={"d": "abcd"})
    r = m.measure_trajectory(q, pairs, tmp_path)     # "Qabcd" -> "Qa" (straddles), "bc", "d"
    assert (r["document_tokens"], *counts(r)) == (4, 2, 2, 0)
    q = write_traj(tmp_path, "row02", [[R("{{d}}Q"), R("{{d}}Q")]], init_state={"d": "abc"})
    r = m.measure_trajectory(q, pairs, tmp_path)     # "abcQ" -> "ab", "cQ" (straddles)
    assert (r["document_tokens"], *counts(r)) == (2, 1, 1, 0)


def test_an_uncovered_character_at_a_span_edge_is_tokenization(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("{{d}}Q tail")]], init_state={"d": "ab"})
    assert m.measure_trajectory(q, gap_at_q, tmp_path)["reason"] == "tokenization"
    q = write_traj(tmp_path, "row02", [[R("xQ {{d}}")]], init_state={"d": "ab"})     # a gap away from any edge
    assert m.measure_trajectory(q, gap_at_q, tmp_path)["measurable"]
    q = write_traj(tmp_path, "row03", [[R("x{{d}}")]], init_state={"d": "Qab"})      # the start edge, at the end
    assert m.measure_trajectory(q, gap_at_q, tmp_path)["reason"] == "tokenization"
    q = write_traj(tmp_path, "row04", [[R("{{e}} {{d}}Qy", ("d", 1, 1))]], init_state={"e": "ab", "d": "abc"})
    assert m.measure_trajectory(q, gap_at_q, tmp_path)["measurable"]                # an empty span has no edge


def test_a_combining_mark_at_a_span_edge_is_tokenization_and_inside_a_document_is_text(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("x{{d}}")]], init_state={"d": "\u0323tail"})
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "tokenization"
    q = write_traj(tmp_path, "row02", [[R("{{d}}\u0301 x")]], init_state={"d": "abc"})
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "tokenization"
    q = write_traj(tmp_path, "row03", [[R("x {{d}} y")]], init_state={"d": "cafe\u0301 menu"})
    assert m.measure_trajectory(q, chars, tmp_path)["measurable"]


def test_one_document_under_two_keys_is_one_document(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("{{a}}"), R("{{b}}")]], init_state={"a": "same text", "b": "same text"})
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["documents"] == 1 and counts(r) == (9, 9, 0)


def test_a_document_twice_in_the_first_call_is_new_at_both_places_and_its_repeat_is_same_offset(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("{{d}}{{d}}")], [R("{{d}}")]], init_state={"d": "abc"})
    r = m.measure_trajectory(q, chars, tmp_path)     # adjacent placeholders: spans (0,3) and (3,6)
    assert (r["document_tokens"], *counts(r)) == (9, 6, 3, 0)


def test_two_places_in_one_sub_call_are_each_compared_with_earlier_sub_calls_only(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("{{d}}")], [R("{{d}}|{{d}}")]], init_state={"d": "abc"})
    r = m.measure_trajectory(q, chars, tmp_path)     # 3 new, then 3 same and 3 different, never 9 new
    assert (r["document_tokens"], *counts(r)) == (9, 3, 3, 3)


def test_the_within_cap_counts_read_each_prompt_and_its_documents_latest_earlier_carrier(tmp_path):
    # sub-calls: "abc" (3 tokens), "abc" + 9 x's (12), "xabc" (4): with cap 10 the second is over the cap
    turns = [[R("{{d}}"), R("{{d}}xxxxxxxxx"), R("x{{d}}")]]
    q = write_traj(tmp_path, "row01", turns, init_state={"d": "abc"})
    r = m.measure_trajectory(q, chars, tmp_path, cap=10)
    assert counts(r) == (3, 3, 3)                                    # second: 3 same; third: 3 different
    # the second is over the cap; the third fits, but the latest earlier carrier of d (the second) does not
    assert (r["reused_in_capped_prompts"], r["reused_in_capped_pairs"]) == (3, 0)
    assert (r["capped_prompt_share"], r["capped_pair_share"]) == (0.5, 0.0)
    r = m.measure_trajectory(q, chars, tmp_path, cap=12)
    assert (r["reused_in_capped_prompts"], r["reused_in_capped_pairs"]) == (6, 6)
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["reused_in_capped_prompts"] is None and r["capped_pair_share"] is None
    q = write_traj(tmp_path, "row02", [[R("{{d}}")]], init_state={"d": "abc"})
    assert m.measure_trajectory(q, chars, tmp_path, cap=10)["capped_prompt_share"] is None    # nothing reused


def test_document_tokens_is_the_public_definition():
    sent = "Q: wxyz ok"                                              # the document "uvwxyz" sliced [2:6]
    spans = [(3, 7, "sha-d", 2)]
    assert m.document_tokens(sent, spans, *chars(sent)) == [(3, "sha-d", 2, 3, ord("w")), (4, "sha-d", 3, 4, ord("x")),
                                                             (5, "sha-d", 4, 5, ord("y")), (6, "sha-d", 5, 6, ord("z"))]
    ids, offs = pairs(sent)                                          # two characters a token: "Q:", " w", "xy", "z ", "ok"
    assert m.document_tokens(sent, spans, ids, offs) == [(2, "sha-d", 3, 5, ids[2])]
    s2 = "Q: wxQz ok"                                                # the 'Q' at 5, inside the span, is covered by no token
    assert m.document_tokens(s2, spans, *gap_at_q(s2)) is not None
    assert m.document_tokens("Q: Qxyz ok", spans, *gap_at_q("Q: Qxyz ok")) is None   # at the span's first character
    assert m.document_tokens(sent, [(3, 3, "sha-e", 0)], *chars(sent)) == []          # an empty span has no edge
    ids0, offs0 = chars(sent)
    ids0, offs0 = [*ids0[:4], 0, *ids0[4:]], [*offs0[:4], (4, 4), *offs0[4:]]      # an empty-offset token inside the span
    assert [t[0] for t in m.document_tokens(sent, spans, ids0, offs0)] == [3, 5, 6, 7]  # carries no text: not a document token


def test_prefix_shared_is_the_longest_over_every_earlier_call(tmp_path):
    q = write_traj(tmp_path, "row01", [[R("{{a}}"), R("{{b}}"), R("{{a}}")]], init_state={"a": "x" * 8, "b": "yyyy"})
    assert m.measure_trajectory(q, chars, tmp_path)["prefix_shared"] == 8


def test_negative_and_none_starts_and_the_later_spec_for_a_key(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "ABCDEFGHIJ"), R("{{d}}"), R("{{d}}", ("d", -5, 10)),
                                        R("{{d}}", ("d", None, 4)), R("{{d}}", ("d", 0, 3), ("d", 6, 10))]])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and (r["document_tokens"], *counts(r)) == (23, 10, 4, 9)


def test_a_gzipped_state_reads_and_hashes_its_decompressed_bytes(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]], gz_state=True)
    r = m.measure_trajectory(q, chars, tmp_path)
    rel = q.relative_to(tmp_path).as_posix() + "/turns/turn_001/state.json"
    assert r["measurable"]
    assert r["files"][rel] == hashlib.sha256(json.dumps({"d": "abc"}, indent=2).encode()).hexdigest()
    (q / "turns" / "turn_001" / "state.json").write_text("{}")
    with pytest.raises(ValueError, match="both"):
        m.measure_trajectory(q, chars, tmp_path)


def test_a_missing_or_truncated_record_is_unreadable_not_an_abort(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    (q / "turns" / "turn_001" / "helper_queries" / "tool_001" / "history.json").unlink()
    r = m.measure_trajectory(q, chars, tmp_path)
    assert (r["reason"], r["subcalls"], r["document_tokens"]) == ("unreadable record", 1, None)
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")]])
    (q / "turns" / "turn_001" / "state.json").write_text('{"d": "ab')
    assert m.measure_trajectory(q, chars, tmp_path)["reason"] == "unreadable record"


def test_without_its_final_record_the_last_turn_is_set_aside_unread(tmp_path):
    turns = [[("parse", "d", "abcdef"), R("{{d}}")], [R("{{d}}"), R("{{d}}")]]
    whole = m.measure_trajectory(write_traj(tmp_path, "row01", turns[:1]), chars, tmp_path)
    q = write_traj(tmp_path, "row02", turns, final=False)
    (q / "turns" / "turn_002" / "result.json").write_text('{"tool_call_records": [')     # cut short by the kill
    r = m.measure_trajectory(q, chars, tmp_path)
    assert (r["final_record"], r["set_aside_turn"], r["cut_subcalls"], r["stop_reason"]) == (False, 2, 2, "absent")
    assert r["measurable"] and r["turns"] == 2 and r["subcalls"] == 1
    for k in (*m.COUNTS, *m.FRACTIONS, "main_input_tokens", "helper_input_tokens", "input_share_helper"):
        assert r[k] == whole[k], k
    assert r["compaction_input_tokens"] is None and whole["compaction_input_tokens"] == 0
    assert not any("turn_002" in f for f in r["files"]) and r["ended_by_itself"] is False
    assert m.measure_trajectory(write_traj(tmp_path, "row03", turns), chars, tmp_path)["set_aside_turn"] is None
    q = write_traj(tmp_path, "row04", [[("parse", "d", "abc")], [R("{{d}}"), R("{{d}}")]], final=False)
    r = m.measure_trajectory(q, chars, tmp_path)                      # its only sub-calls lie in the set-aside turn
    assert (r["reason"], r["subcalls"], r["cut_subcalls"], r["documents"]) == ("no sub-call", 0, 2, None)


def test_the_input_share_and_the_main_loop_caching_read_the_usage_records(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}"), R("x {{d}}")]],
                   compactions=[{"in_tokens": 7, "cache_read_tokens": 3}, None])
    r = m.measure_trajectory(q, chars, tmp_path)
    assert (r["main_input_tokens"], r["main_cache_read_tokens"], r["helper_input_tokens"]) == (300, 80, 150)
    assert r["compaction_input_tokens"] == 10                            # a failed attempt, no metadata, adds nothing
    assert r["input_share_helper"] == 150 / 450 and r["main_cache_read_fraction"] == 80 / 300
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")]], hist_kind="raw")   # reconstruction
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["reason"] == "reconstruction" and r["helper_input_tokens"] == 50 and r["reuse_gaps_seconds"] is None
    q = write_traj(tmp_path, "row03", [[("parse", "d", "abc"), R("{{d}}")]], helper_md={})
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and all(r[k] is None for k in m.USAGE)
    q = write_traj(tmp_path, "row04", [[("parse", "d", "abc"), R("{{d}}")]], compactions=[{"in_tokens": "x"}])
    assert m.measure_trajectory(q, chars, tmp_path)["compaction_input_tokens"] is None
    q = write_traj(tmp_path, "row05", [[("parse", "d", "abc"), R("{{d}}")]])
    (q / "turns" / "turn_001" / "helper_queries" / "tool_001" / "history.json").unlink()
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["reason"] == "unreadable record" and all(r[k] is None for k in m.USAGE)


def test_the_reuse_gap_runs_from_the_latest_earlier_sub_call_carrying_the_document(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abcdef"), R("{{d}}", ("d", 0, 3)), R("{{d}}", ("d", 3, 6))],
                                       [R("{{d}}", ("d", 0, 3)), R("{{e}}")]], init_state={"e": "zz"})
    r = m.measure_trajectory(q, chars, tmp_path)
    # turn 1 at T0+1000: the parse takes 1 s, each retrieve 2 s; the third sub-call (turn 2, at T0+2000) reuses
    # "abc", which the FIRST carried, but the latest to carry d is the second, started at T0+1000+1+2
    assert counts(r) == (8, 3, 0) and r["reuse_gaps_seconds"] == [997.0]
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}"), R("{{d}}")]])
    assert m.measure_trajectory(q, chars, tmp_path)["reuse_gaps_seconds"] == [2.0]
    q = write_traj(tmp_path, "row03", [[("parse", "d", "abc"), R("{{d}}"), R("{{d}}")]], stamps=lambda n: "2026-11-20T00:00:00")
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["measurable"] and r["reuse_gaps_seconds"] is None        # no time zone: untimed


def test_a_helper_of_another_tool_refuses(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]], tool="web_search")
    with pytest.raises(ValueError, match="retrieve_information"):
        m.measure_trajectory(q, chars, tmp_path)


def _cfg(tmp_path, n=3, model=MODEL, gate=("0075",), ceiling=2_000_000, parallel=2):
    csv = tmp_path / "public.csv"
    csv.write_text("Question,Question Type,Rubric\n" + "".join(f"q{i},{'AB'[i % 2]},r\n" for i in range(n)),
                   encoding="utf-8")
    real = m.load_config(REPO_ROOT / "config" / "fab-reuse.toml", REPO_ROOT)
    harness = {**real.harness, "questions_csv_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(), "model": model}
    cfg = m.FabReuseConfig(config_path=real.config_path, results_dir=tmp_path / "out", cohort=n,
                           task_id_format=real.task_id_format, required_entries=gate, harness=harness,
                           reader=real.reader, run={**real.run, "token_ceiling": ceiling, "max_parallel": parallel},
                           timing=real.timing)
    return cfg, csv


def test_the_cohort_summary_names_unrun_unmeasurable_questions_and_failed_launches(tmp_path):
    cfg, csv = _cfg(tmp_path)
    runs = tmp_path / "logs"
    write_traj(runs, "row01", [[("parse", "d", "abcdefghij"), R("Q: {{d}}")], [R("Q: {{d}}")]])
    write_traj(runs, "row01", [], stamp="2026-11-19_23-00-00_000000")      # row 1's earlier failed launch
    write_traj(runs, "row02", [[("parse", "d", "abc")]], stamp="2026-11-20_01-00-00_123456")
    write_traj(runs, "row03", [], stamp="2026-11-20_02-00-00_654321", error_turns=(1,))   # row 3: its one query failed
    s = m.summarize(cfg, runs, csv, chars)
    assert (s["cohort"], s["run"], s["measured"], s["not_run"]) == (3, 2, 1, ["row03"])
    assert s["failed_launches"] == {"row01": 1, "row03": 1}
    assert s["not_measurable"] == {"no sub-call": 1, "no document token": 0, "reconstruction": 0,
                                   "tokenization": 0, "unreadable record": 0}
    assert s["pooled"]["reused_fraction"] == 0.5 and s["pooled"]["same_offset_fraction"] == 0.5
    assert s["pooled"]["new_fraction"] == 0.5
    assert s["pooled"]["prefix_shared_fraction"] == 13 / 26
    assert s["pooled"]["capped_prompt_share"] == 1.0 and s["reader"]["context_cap"] == 81920
    assert s["per_trajectory"]["reused_fraction"] == {"n": 1, "median": 0.5, "p10": 0.5, "p90": 0.5}
    assert s["trajectories"][0]["reused_fraction"] == 0.5 and s["trajectories"][1]["reused_fraction"] is None
    for phrase in ("upper bound", "keyed on the retrieved document's sha256", "keyed on content could reuse more",
                   "prefix_shared is not bounded", "not a realized saving", "logged sub-calls"):
        assert phrase in s["label"]
    assert s["by_question_type"] == {"A": {"run": ["row01"], "not_run": ["row03"]}, "B": {"run": ["row02"], "not_run": []}}
    assert [x["question_type"] for x in s["trajectories"]] == ["A", "B"]
    # row 1: two turn queries (150 each, 40 cache-read) and two sub-calls (50 each); row 2 (no sub-call): one query
    assert s["input_share"]["pooled"] == 100 / (100 + 450) and s["main_loop_caching"]["pooled"] == 120 / 450
    assert s["input_share"]["per_trajectory"]["n"] == 2 and s["reuse_gap"]["trajectories"] == 1
    assert s["reuse_gap"]["gaps"] == 1 and s["reuse_gap"]["share_within"] == {"300": 0.0, "3600": 1.0}
    assert s["trajectories"][0]["reuse_gaps_seconds"] == [999.0]       # turn 1's sub-call after a 1 s parse
    assert set(s) == set(m.SUMMARY_FIELDS) - {"sources"}             # `sources` is added by the command
    for x in s["trajectories"]:
        assert set(x) == set(m.ROW_FIELDS)
    for k, v in m.NESTED_FIELDS.items():
        if k == "not_ended_by_itself":
            assert s[k] == [] and v == ("task_id", "stop_reason")       # every trajectory here ended by itself
        elif k not in ("reader", "summary"):
            assert set(s[k]) == set(v), k
    for k in m.AGGREGATES:
        assert s["aggregates_ended_by_itself"][k] == s[k], k            # every trajectory here ended by itself
    for blk in (s["per_trajectory"]["reused_fraction"], s["input_share"]["per_trajectory"], s["reuse_gap"]["seconds"]):
        assert set(blk) == set(m.NESTED_FIELDS["summary"])
    assert set(s["reader"]) == set(m.NESTED_FIELDS["reader"]) - {"tokenizers_version"}   # added by the command
    assert set(s["labels"]) == {"input_share", "main_loop_caching", "reuse_gap", "by_question_type"}
    empty = m.summarize(cfg, tmp_path / "none", csv, chars)                # nothing run: every field still written
    assert set(empty) == set(m.SUMMARY_FIELDS) - {"sources"} and empty["pooled"] is None
    assert empty["reuse_gap"]["seconds"] is None and empty["input_share"] is None


def test_a_directory_without_turns_init_is_not_seen(tmp_path):
    cfg, csv = _cfg(tmp_path)
    runs = tmp_path / "logs"
    write_traj(runs, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    for name in ("row02", "row99"):                                   # died before turns/init/
        d = runs / "finance" / "model" / "2026-11-20_05-00-00_aaaaaa" / name
        d.mkdir(parents=True)
        (d / "agent.log").write_text("x")
    s = m.summarize(cfg, runs, csv, chars)
    assert (s["not_run"], s["failed_launches"], s["run"]) == (["row02", "row03"], {}, 1)


def test_the_summary_refuses_a_second_run_a_stray_question_another_model_and_another_csv(tmp_path):
    cfg, csv = _cfg(tmp_path)
    one = [[("parse", "d", "abc"), R("{{d}}")]]
    runs = tmp_path / "logs"
    write_traj(runs, "row01", one)
    write_traj(runs, "row01", one, stamp="2026-11-20_02-00-00_fedcba")
    with pytest.raises(ValueError, match="more than one trajectory"):
        m.summarize(cfg, runs, csv, chars)
    write_traj(tmp_path / "logs2", "row09", [])
    with pytest.raises(ValueError, match="outside the cohort"):
        m.summarize(cfg, tmp_path / "logs2", csv, chars)
    write_traj(tmp_path / "logs3", "row01", one, model="anthropic/claude-sonnet-5-5-no-fallback")
    with pytest.raises(ValueError, match="served by"):
        m.summarize(cfg, tmp_path / "logs3", csv, chars)
    csv.write_text("Question\nchanged\n", encoding="utf-8")
    with pytest.raises(ValueError, match="pinned public.csv"):
        m.summarize(cfg, tmp_path / "logs3", csv, chars)
    csv.write_text("Question,Rubric\n" + "".join(f"q{i},r\n" for i in range(3)), encoding="utf-8")
    cfg = m.FabReuseConfig(**{**cfg.__dict__, "harness": {**cfg.harness, "questions_csv_sha256":
                                                         hashlib.sha256(csv.read_bytes()).hexdigest()}})
    with pytest.raises(ValueError, match="no column 'Question Type'"):
        m.summarize(cfg, tmp_path / "logs3", csv, chars)


def test_the_gate(tmp_path, monkeypatch):
    dirty = set()

    class Res:
        def __init__(self, rc):
            self.returncode, self.stdout = rc, "### 0075 — x\n"

    monkeypatch.setattr(m.subprocess, "run",
                        lambda cmd, **k: Res(1 if cmd[:2] == ["git", "diff"] and cmd[-1] in dirty else 0))
    cfg, _ = _cfg(tmp_path, model="UNSET")
    with pytest.raises(RuntimeError, match="model is UNSET"):
        m.assert_ready(cfg, REPO_ROOT)
    cfg, _ = _cfg(tmp_path, ceiling="UNSET")
    with pytest.raises(RuntimeError, match="token_ceiling is UNSET"):
        m.assert_ready(cfg, REPO_ROOT)
    cfg, _ = _cfg(tmp_path, parallel="UNSET")
    with pytest.raises(RuntimeError, match="max_parallel is UNSET"):
        m.assert_ready(cfg, REPO_ROOT)
    cfg, _ = _cfg(tmp_path, gate=("0075", "9999"))
    with pytest.raises(RuntimeError, match="no entry 9999"):
        m.assert_ready(cfg, REPO_ROOT)
    cfg, _ = _cfg(tmp_path)
    m.assert_ready(cfg, REPO_ROOT)
    for rel in ("ledger/ledger.md", "config/fab-reuse.toml", *m.SOURCES):
        dirty.clear()
        dirty.add(rel)
        with pytest.raises(RuntimeError, match=re.escape(rel)):
            m.assert_ready(cfg, REPO_ROOT)


def test_the_command_reads_the_registered_config_only(tmp_path):
    other = tmp_path / "config" / "fab-reuse.toml"                  # the same name, outside this tree
    other.parent.mkdir()
    other.write_bytes((REPO_ROOT / "config" / "fab-reuse.toml").read_bytes())
    for path in (tmp_path / "other.toml", other):
        with pytest.raises(SystemExit, match="not config/fab-reuse.toml"):
            m.main(["--config", str(path), "--runs", str(tmp_path), "--questions", "q", "--tokenizer-json", "t"])


def test_the_run_section_is_checked(tmp_path):
    real = (REPO_ROOT / "config" / "fab-reuse.toml").read_text(encoding="utf-8")
    bad = {r"order = \[1, 4,": "order = [1, 1,", r'last_start_utc = "[^"]*"': 'last_start_utc = "noon"',
           r"disk_floor_gb = \d+": "disk_floor_gb = 0", r"poll_seconds = \d+": "poll_seconds = 0",
           r"wall_seconds = \d+": "wall_seconds = true", r"poll_seconds = \d+ ": "poll_seconds = 1.5 ",
           r"cache_lifetimes_seconds = \[300, 3600\]": "cache_lifetimes_seconds = []",
           r"context_cap = 81920": "context_cap = 0"}
    f = tmp_path / "fab-reuse.toml"
    for old, new in bad.items():
        text, n = re.subn(old, new, real)
        assert n == 1, old
        f.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            m.load_config(f, REPO_ROOT)
    for key in ("token_ceiling", "max_parallel"):
        for value in ("0", "-5", "1.5", "true", "\"none\""):
            f.write_text(re.sub(key + r" = \S+", f"{key} = {value}", real), encoding="utf-8")
            with pytest.raises(ValueError, match=key):
                m.load_config(f, REPO_ROOT)


def test_the_registered_config():
    cfg = m.load_config(REPO_ROOT / "config" / "fab-reuse.toml", REPO_ROOT)
    assert cfg.cohort == 27 and cfg.required_entries == ("0075",) and cfg.task_id_format.format(row=1) == "row01"
    assert cfg.run["order"][:4] == [1, 4, 7, 10] and cfg.run["order"] == [1] + [r for k in (1, 2, 0)
                                                                            for r in range(2, 28) if r % 3 == k]
    assert cfg.run["question_type_column"] == "Question Type" and cfg.timing["cache_lifetimes_seconds"] == [300, 3600]
    assert cfg.harness["commit"] == "25b6cab9bcb4f8f9857f2e1a6721732c85511c5c" and cfg.harness["model"] == MODEL
    beh = tomllib.loads((REPO_ROOT / "config" / "cache-behavior.toml").read_text(encoding="utf-8"))
    assert (cfg.reader["model"], cfg.reader["revision"]) == (beh["model"], beh["revision"])   # the handoff reader
    assert cfg.reader["context_cap"] == beh["context_cap"] == 81920


@pytest.mark.skipif(not READER.exists(), reason="the reader's tokenizer is not in the local HF cache")
def test_the_reader_tokenizer_counts_a_repeat_as_same_offset_and_cannot_place_a_folded_edge(tmp_path):
    sha = m.load_config(REPO_ROOT / "config" / "fab-reuse.toml").reader["tokenizer_json_sha256"]
    enc = m.reader_encoder(READER, sha)
    doc ="Total revenue was $42.1 million in fiscal 2025, up 7% from $39.3 million.\nNet income: $5.0 million."
    q = write_traj(tmp_path, "row01", [[("parse", "10k", doc), R("Extract revenue:\n{{10k}}\nAnswer:")],
                                       [R("Extract revenue:\n{{10k}}\nAnswer:")]])
    r = m.measure_trajectory(q, enc, tmp_path)
    ids, offs = enc("Extract revenue:\n" + doc + "\nAnswer:")
    lo, hi = len("Extract revenue:\n"), len("Extract revenue:\n") + len(doc)
    inside = sum(1 for a, b in offs if lo <= a and b <= hi and a < b)
    assert 0 < inside < len(ids)
    assert (r["document_tokens"], *counts(r)) == (2 * inside, inside, inside, 0)
    assert r["prefix_shared"] == len(ids)
    q = write_traj(tmp_path, "row02", [[R("{{d}}́ menu")]], init_state={"d": "cafe"})   # NFC folds U+0301
    assert m.measure_trajectory(q, enc, tmp_path)["reason"] == "tokenization"


def test_an_unreadable_helper_record_nulls_the_usage_whatever_the_first_reason(tmp_path):
    def two_subcalls(task_id):                       # every history is raw: the first sub-call is not rebuilt
        return write_traj(tmp_path, task_id, [[("parse", "d", "abc"), R("{{d}}"), R("{{d}}")]], hist_kind="raw")
    r = m.measure_trajectory(two_subcalls("row01"), chars, tmp_path)   # every record readable: the usage is read
    assert r["reason"] == "reconstruction" and (r["main_input_tokens"], r["helper_input_tokens"]) == (150, 100)
    assert r["input_share_helper"] == 100 / 250
    q = two_subcalls("row02")
    (q / "turns" / "turn_001" / "helper_queries" / "tool_002" / "result.json").write_text('{"tool_call": ')
    r = m.measure_trajectory(q, chars, tmp_path)     # the second sub-call's record is truncated
    assert r["reason"] == "reconstruction" and all(r[k] is None for k in m.USAGE)
    q = two_subcalls("row03")
    f = q / "turns" / "turn_001" / "helper_queries" / "tool_002" / "result.json"
    rec = json.loads(f.read_text())
    del rec["tool_call"]
    f.write_text(json.dumps(rec))
    r = m.measure_trajectory(q, chars, tmp_path)     # the second sub-call's record names no call
    assert r["reason"] == "reconstruction" and all(r[k] is None for k in m.USAGE)


def test_an_unreadable_turn_record_nulls_the_usage_too(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), R("{{d}}")]])
    (q / "turns" / "turn_001" / "state.json").write_text('{"d": "ab')
    r = m.measure_trajectory(q, chars, tmp_path)     # the turn's usage is never summed; the helper's is
    assert r["reason"] == "unreadable record" and all(r[k] is None for k in m.USAGE)
    q = write_traj(tmp_path, "row02", [[("parse", "d", "abc"), R("{{d}}")]])
    f = q / "turns" / "turn_001" / "result.json"
    res = json.loads(f.read_text())
    res["tool_call_records"] = res["tool_call_records"][:1]          # the helper written, its turn's record not yet rewritten
    f.write_text(json.dumps(res))
    r = m.measure_trajectory(q, chars, tmp_path)
    assert r["reason"] == "unreadable record" and all(r[k] is None for k in m.USAGE)


def test_an_unmeasurable_trajectory_carries_no_document_count(tmp_path):
    q = write_traj(tmp_path, "row01", [[("parse", "d", "abc"), ("parse", "e", "xyz"), R("{{d}}"),
                                        ("retrieve", {"prompt": "{{e}}"}, "not the sent text")]])
    r = m.measure_trajectory(q, chars, tmp_path)     # the first sub-call is read, the second is not rebuilt
    assert r["reason"] == "reconstruction" and r["documents"] is None and r["document_tokens"] is None


def test_a_tool_record_without_its_duration_is_untimed(tmp_path):
    cfg, csv = _cfg(tmp_path)
    runs = tmp_path / "logs"
    q = write_traj(runs, "row01", [[("parse", "d", "abc"), R("{{d}}"), R("{{d}}")]])
    f = q / "turns" / "turn_001" / "result.json"
    res = json.loads(f.read_text())
    del res["tool_call_records"][0]["duration_seconds"]
    f.write_text(json.dumps(res))
    s = m.summarize(cfg, runs, csv, chars)
    x = s["trajectories"][0]
    assert x["measurable"] and counts(x) == (3, 3, 0) and x["reuse_gaps_seconds"] is None
    assert (s["reuse_gap"]["untimed"], s["reuse_gap"]["trajectories"], s["reuse_gap"]["seconds"]) == (["row01"], 0, None)


def test_compaction_unknown_names_a_missing_final_record_and_an_unreadable_compaction_usage(tmp_path):
    cfg, csv = _cfg(tmp_path)
    runs = tmp_path / "logs"
    one = [[("parse", "d", "abc"), R("{{d}}")], [R("{{d}}")]]
    write_traj(runs, "row01", one, compactions=[{"in_tokens": "x"}])
    write_traj(runs, "row02", one, final=False, stamp="2026-11-20_01-00-00_123456")
    write_traj(runs, "row03", one, compactions=[{"in_tokens": 7}], stamp="2026-11-20_02-00-00_222222")
    s = m.summarize(cfg, runs, csv, chars)
    assert [x["final_record"] for x in s["trajectories"]] == [True, False, True]
    assert s["input_share"]["compaction_unknown"] == ["row01", "row02"] and s["input_share"]["compaction_input_tokens"] == 7


def test_aggregates_over_the_trajectories_that_ended_by_themselves_stand_beside_those_over_all(tmp_path):
    turns = [[("parse", "d", "abcdef"), R("{{d}}")], [R("{{d}}")]]   # 12 document tokens: 6 new, then 6 same
    for sr, want in (("done_tool", True), ("should_stop", True), ("max_time", False), ("max_turns", False),
                     ("error", False)):
        q = write_traj(tmp_path / "one", f"row_{sr}", turns, stop_reason=sr)
        assert m.measure_trajectory(q, chars, tmp_path)["ended_by_itself"] is want, sr
    cfg, csv = _cfg(tmp_path, n=4)
    runs = tmp_path / "logs"
    write_traj(runs, "row01", turns)
    write_traj(runs, "row02", turns + [[R("{{d}}"), R("{{d}}")]], final=False, stamp="2026-11-20_01-00-00_123456")
    write_traj(runs, "row03", turns, stop_reason="max_time", stamp="2026-11-20_02-00-00_222222")
    write_traj(runs, "row04", [[("parse", "d", "abc")]], stamp="2026-11-20_03-00-00_333333")   # ended; no sub-call
    s = m.summarize(cfg, runs, csv, chars)
    assert [x["ended_by_itself"] for x in s["trajectories"]] == [True, False, False, True]
    assert s["not_ended_by_itself"] == [{"task_id": "row02", "stop_reason": "absent"},
                                        {"task_id": "row03", "stop_reason": "max_time"}]
    own = s["aggregates_ended_by_itself"]
    assert set(own) == set(m.NESTED_FIELDS["aggregates_ended_by_itself"]) and (own["trajectories"], own["measured"]) == (2, 1)
    for k in m.AGGREGATES:
        assert set(own[k]) == set(s[k]), k
    assert s["measured"] == 3 and s["per_trajectory"]["reused_fraction"]["n"] == 3
    assert own["per_trajectory"]["reused_fraction"]["n"] == 1
    assert (s["pooled"]["document_tokens"], own["pooled"]["document_tokens"]) == (36, 12)
    assert (s["input_share"]["trajectories"], own["input_share"]["trajectories"]) == (4, 2)
    # each read turn query is 150 input tokens: rows 1-3 read two turns each, row 4 one
    assert (s["main_loop_caching"]["main_input_tokens"], own["main_loop_caching"]["main_input_tokens"]) == (1050, 450)
    assert (s["reuse_gap"]["trajectories"], own["reuse_gap"]["trajectories"]) == (3, 1)
    assert "did not end by itself" in s["label"] and "aggregates_ended_by_itself leaves it out" in s["label"]


def test_the_command_adds_the_sources_and_the_tokenizers_version(tmp_path):
    from importlib.metadata import version
    pytest.importorskip("tokenizers")
    cfg, csv = _cfg(tmp_path)
    s = m.provenance(m.summarize(cfg, tmp_path / "none", csv, chars), cfg, REPO_ROOT)
    assert s["reader"]["tokenizers_version"] == version("tokenizers")
    rels = ("config/fab-reuse.toml", "src/linear_ceiling/fab_reuse.py", "tests/test_fab_reuse.py")
    assert s["sources"] == {rel: hashlib.sha256((REPO_ROOT / rel).read_text(encoding="utf-8").encode()).hexdigest()
                            for rel in rels}
    assert set(s) == set(m.SUMMARY_FIELDS) and set(s["reader"]) == set(m.NESTED_FIELDS["reader"])
