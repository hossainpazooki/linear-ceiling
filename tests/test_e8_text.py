"""E8 arm (b) text rule (entry 0016 §4): rendering, eligibility, stratified seeded draw."""
import json

import numpy as np
import pytest

from linear_ceiling.config import E7Config, E8Config
from linear_ceiling.e8_text import (TraceText, export_rendered, iter_trace_texts, mlperf_suite, render_messages,
                                    render_mlperf_rows, sample_windows, write_tokens)


def _cfg(tmp_path, n_seqs=4, seq_len=8, suites=("tau2-bench", "swe-bench"), seed=8):
    return E8Config(pair="qwen3-0.6b-to-1.7b", results_dir=tmp_path / "r", tokens_dir=tmp_path / "tok",
                    upstream_path=tmp_path / "up", upstream_sha="0" * 40, verdict_k=1, report_k=(1,),
                    generic_dumps="data/kv/x", agent_dumps=tmp_path / "agent", holdout_frac=0.2, stride=4,
                    text={"seed": seed, "n_seqs": n_seqs, "seq_len": seq_len, "suites": list(suites), "window": "first"},
                    band={"holds_max_drop": 0.05, "degrades_min_drop": 0.15}, config_path=tmp_path / "e8.toml")


def words(text):          # a stand-in encoder: one id per whitespace token
    return [hash(w) % 1000 for w in text.split()]


def test_render_role_tags_and_tool_calls():
    msgs = [{"role": "system", "content": "be terse"},
            {"role": "assistant", "content": None,
             "tool_calls": [{"function": {"name": "look", "arguments": {"q": "x"}}}]},
            {"role": "tool", "content": [{"type": "text", "text": "found"}]}]
    out = render_messages(msgs)
    assert out == '[system]\nbe terse\n[assistant]\nlook({"q":"x"})\n[tool]\nfound'


def test_short_trajectories_are_skipped_never_padded(tmp_path):
    items = [TraceText("tau2-bench", f"t{i}", "w " * (20 if i < 3 else 3)) for i in range(6)]
    items += [TraceText("swe-bench", f"s{i}", "w " * 20) for i in range(3)]
    cfg = _cfg(tmp_path, n_seqs=4, seq_len=8)
    tok, man = sample_windows(items, words, cfg)
    assert tok.shape == (4, 8) and tok.dtype == np.int64
    assert [m["suite"] for m in man] == ["tau2-bench", "tau2-bench", "swe-bench", "swe-bench"]
    assert all(m["traj_id"] in {"t0", "t1", "t2"} for m in man[:2])      # the short ones never drawn


def test_draw_is_a_pure_function_of_seed_and_corpus(tmp_path):
    items = [TraceText("tau2-bench", f"t{i}", "w " * 20) for i in range(10)]
    items += [TraceText("swe-bench", f"s{i}", "w " * 20) for i in range(10)]
    a = sample_windows(list(reversed(items)), words, _cfg(tmp_path))[1]
    b = sample_windows(items, words, _cfg(tmp_path))[1]
    c = sample_windows(items, words, _cfg(tmp_path, seed=9))[1]
    assert a == b and a != c


def test_refuses_when_a_suite_cannot_fill_its_share(tmp_path):
    items = [TraceText("tau2-bench", "t0", "w " * 20), TraceText("swe-bench", "s0", "w " * 20)]
    with pytest.raises(ValueError, match="only 1 trajectories"):
        sample_windows(items, words, _cfg(tmp_path, n_seqs=4))


def test_refuses_unequal_stratification(tmp_path):
    with pytest.raises(ValueError, match="stratify equally"):
        sample_windows([], words, _cfg(tmp_path, n_seqs=3))


def test_write_tokens_manifest_records_rule_and_hash(tmp_path):
    cfg = _cfg(tmp_path)
    p = write_tokens(cfg, np.zeros((2, 3), dtype=np.int64), [{"suite": "s", "traj_id": "a"}])
    man = json.loads(p.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert man["rule"].startswith("ledger entry 0016") and man["shape"] == [2, 3] and len(man["sha256"]) == 64


def test_iter_trace_texts_reads_all_three_swe_families_and_tau2(tmp_path):
    from tests.test_e7_corpus import write_corpus
    write_corpus(tmp_path / "traces")
    e7 = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r", pricing={}, thresholds={},
                  tokenizer={}, lane_b_policy="x", config_path=tmp_path / "c")
    got = {t.traj_id: t for t in iter_trace_texts(e7, ("tau2-bench", "swe-bench"))}
    assert "agent-x/t1/0" in got and got["agent-x/t1/0"].text.startswith("[assistant]\nhi")
    assert "20240820_honeycomb/inst-1" in got and "20250122_autocoderover/inst-2" in got
    assert "20241016_composio_swekit/inst-1_traj" in got
    assert "[user]\nsolve this" in got["20241016_composio_swekit/inst-1_traj"].text
    assert not any(t.suite == "tau-bench" for t in got.values())


# --- MLPerf Agentic Inference (the 2026-10-22 plan, cell 1a) -----------------------------------------------------

SHARED_PREFIX = "# Workato Customer Support Agent -- shared by every workflow conversation"


def _row(cid, turn, role, source=None, **fields):
    r = {"conversation_id": cid, "turn": turn, "role": role, **fields}
    if source is not None:
        r["_source"] = source
    return r


def write_mlperf_corpus(traces_dir):
    """Three trajectories in one flat JSONL, rows written OUT of turn order, a metadata first row and a blank
    line: two Workato workflow conversations (`_source` on every row, the shared system/tools prefix on the
    first) and one DeepSWE coding trajectory (no `_source`)."""
    rows = [{"_type": "dataset_metadata", "source": "Workato", "license": "CC BY 4.0"},
            _row("sim_000002", 2, "assistant", "Workato", reasoning_content="refund path", content="On it."),
            _row("sim_000001", 1, "user", "Workato", content="Where is my order?", system=SHARED_PREFIX,
                 tools=[{"type": "function", "function": {"name": "track_package"}}]),
            _row("sim_000001", 3, "tool", "Workato", tool_results=[{"tool_call_id": "t0", "content": "{\"eta\": \"Tue\"}"}]),
            _row("sim_000001", 2, "assistant", "Workato", reasoning_content="look it up",
                 tool_calls=[{"id": "t0", "type": "function", "function": {"name": "track_package", "arguments": {"id": "A1"}}}]),
            _row("sim_000001", 4, "assistant", "Workato", content="It arrives Tuesday.", intent_codes=["I001"]),
            _row("sim_000002", 1, "user", "Workato", content="I want a refund.", system=SHARED_PREFIX, tools=[]),
            _row("deepswe_0001", 1, "user", content="Fix the failing test in utils.py", system="You are a coding agent.",
                 tools=[{"type": "function", "function": {"name": "bash"}}]),
            _row("deepswe_0001", 3, "tool", tool_results=[{"tool_call_id": "c0", "content": "utils.py"}]),
            _row("deepswe_0001", 2, "assistant", reasoning_content="first list the files",
                 tool_calls=[{"id": "c0", "type": "function", "function": {"name": "bash", "arguments": "{\"cmd\": \"ls\"}"}}]),
            _row("deepswe_0001", 4, "assistant", content="Patched.")]
    d = traces_dir / "mlperf-agentic"
    d.mkdir(parents=True)
    lines = [json.dumps(r) for r in rows]
    lines.insert(3, "")
    (d / "mlperf_agentic_inference_dataset.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


def _e7(tmp_path):
    return E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "r", pricing={}, thresholds={},
                    tokenizer={}, lane_b_policy="x", config_path=tmp_path / "c")


def test_render_mlperf_rows_keeps_reasoning_tool_calls_and_tool_results_not_the_shared_prefix():
    rows = [_row("c", 1, "user", content="fix it", system=SHARED_PREFIX, tools=[{"x": 1}]),
            _row("c", 2, "assistant", reasoning_content="think",
                 tool_calls=[{"id": "t0", "type": "function", "function": {"name": "run", "arguments": {"cmd": "ls"}}}]),
            _row("c", 3, "tool", tool_results=[{"tool_call_id": "t0", "content": "a.py"}]),
            _row("c", 4, "assistant", content="done")]
    out = render_mlperf_rows(rows)
    assert out == '[user]\nfix it\n[assistant]\nthink\nrun({"cmd":"ls"})\n[tool]\na.py\n[assistant]\ndone'
    assert SHARED_PREFIX not in out and "x" not in out.split("\n")[0]


def test_render_mlperf_rows_without_reasoning_is_the_0016_rendering():
    msgs = [{"role": "user", "content": "hi"},
            {"role": "assistant", "content": None, "tool_calls": [{"function": {"name": "look", "arguments": {"q": "x"}}}]}]
    assert render_mlperf_rows(msgs) == render_messages(msgs)


def test_mlperf_suite_is_decided_by_the_source_field_alone():
    assert mlperf_suite([_row("a", 1, "user", "Workato", content="x")]) == "mlperf-workflow"
    assert mlperf_suite([_row("a", 1, "user", content="x"), _row("a", 2, "assistant", "Workato")]) == "mlperf-workflow"
    assert mlperf_suite([_row("a", 1, "user", content="# Workato Customer Support Agent")]) == "mlperf-coding"


def test_iter_trace_texts_reads_mlperf_in_turn_order_split_by_source(tmp_path):
    write_mlperf_corpus(tmp_path / "traces")
    got = {t.traj_id: t for t in iter_trace_texts(_e7(tmp_path), ("mlperf-coding", "mlperf-workflow"))}
    assert set(got) == {"sim_000001", "sim_000002", "deepswe_0001"}
    assert got["sim_000001"].suite == "mlperf-workflow" and got["deepswe_0001"].suite == "mlperf-coding"
    assert got["sim_000001"].text == ('[user]\nWhere is my order?\n[assistant]\nlook it up\ntrack_package({"id":"A1"})\n'
                                      '[tool]\n{"eta": "Tue"}\n[assistant]\nIt arrives Tuesday.')
    assert got["deepswe_0001"].text.startswith('[user]\nFix the failing test in utils.py\n[assistant]\nfirst list the files\n'
                                               'bash({"cmd": "ls"})\n[tool]\nutils.py')
    assert all(SHARED_PREFIX not in t.text and "coding agent" not in t.text for t in got.values())
    # one suite at a time, and the old suites see nothing of the new directory
    assert [t.traj_id for t in iter_trace_texts(_e7(tmp_path), ("mlperf-coding",))] == ["deepswe_0001"]
    assert list(iter_trace_texts(_e7(tmp_path), ("tau2-bench", "swe-bench"))) == []


def test_mlperf_windows_draw_under_the_0016_rule(tmp_path):
    write_mlperf_corpus(tmp_path / "traces")
    items = list(iter_trace_texts(_e7(tmp_path), ("mlperf-coding", "mlperf-workflow")))
    cfg = _cfg(tmp_path, n_seqs=2, seq_len=4, suites=("mlperf-coding", "mlperf-workflow"))
    tok, man = sample_windows(items, words, cfg)
    assert tok.shape == (2, 4) and [m["suite"] for m in man] == ["mlperf-coding", "mlperf-workflow"]
    assert man[0]["traj_id"] == "deepswe_0001"
    with pytest.raises(ValueError, match="mlperf-coding: only 1 trajectories"):
        sample_windows(items, words, _cfg(tmp_path, n_seqs=4, seq_len=4, suites=("mlperf-coding", "mlperf-workflow")))


def test_export_rendered_writes_sorted_jsonl_with_counts(tmp_path):
    write_mlperf_corpus(tmp_path / "traces")
    out, counts = export_rendered(tmp_path / "traces", ("mlperf-coding", "mlperf-workflow"), tmp_path / "x" / "r.jsonl")
    lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert counts == {"mlperf-coding": 1, "mlperf-workflow": 2}
    assert [(l["suite"], l["traj_id"]) for l in lines] == [("mlperf-coding", "deepswe_0001"),
                                                          ("mlperf-workflow", "sim_000001"), ("mlperf-workflow", "sim_000002")]
    assert lines[1]["text"].startswith("[user]\nWhere is my order?")
