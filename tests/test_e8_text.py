"""E8 arm (b) text rule (entry 0016 §4): rendering, eligibility, stratified seeded draw."""
import json

import numpy as np
import pytest

from linear_ceiling.config import E7Config, E8Config
from linear_ceiling.e8_text import TraceText, iter_trace_texts, render_messages, sample_windows, write_tokens


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
