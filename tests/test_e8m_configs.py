"""config/e8m.toml and config/e8mf.toml (the 2026-10-22 plan, cell 1a): E8's instrument on the MLPerf Agentic
Inference suites, on the Qwen3 pair and on the Llama pair. Both are UNREGISTERED: their [e8.gate] names an entry
the committed ledger does not have, so `e8 --check` refuses by construction, and these tests pin what each file
inherits unchanged from the cell it copies (e8.toml, e8f.toml) and what it is allowed to change."""
from linear_ceiling import REPO_ROOT
from linear_ceiling import e8 as e8_driver
from linear_ceiling.config import load_e8_config
from linear_ceiling.e8_text import MLPERF_SUITES

MLPERF_TEXT = {"seed": 8, "n_seqs": 50, "seq_len": 1024, "suites": list(MLPERF_SUITES), "window": "first"}


def _load(name):
    return load_e8_config(REPO_ROOT / "config" / f"{name}.toml", REPO_ROOT)


def test_e8m_is_e8s_instrument_on_the_mlperf_suites():
    c, e8 = _load("e8m"), _load("e8")
    assert c.pair == e8.pair and c.upstream_path == e8.upstream_path
    assert c.results_dir.name == "e8m" and c.tokens_dir.name == "e8m"
    assert c.results_dir != e8.results_dir and c.tokens_dir != e8.tokens_dir
    assert c.text == MLPERF_TEXT and {k: v for k, v in c.text.items() if k != "suites"} == {k: v for k, v in e8.text.items() if k != "suites"}
    assert c.band == e8.band and c.generic_dumps == e8.generic_dumps
    assert (c.verdict_k, c.report_k, c.holdout_frac, c.stride) == (e8.verdict_k, e8.report_k, e8.holdout_frac, e8.stride)
    assert c.mapper_tag is None and c.amendment is None and c.agent_holdout_frac is None and c.reuse_agent_dumps_from is None
    assert c.scope_note and "MLPerf" in c.scope_note and "reasoning kept" in c.scope_note


def test_e8mf_is_e8fs_pair_on_e8ms_text():
    c, f, m = _load("e8mf"), _load("e8f"), _load("e8m")
    assert c.pair == f.pair and c.upstream_sha == f.upstream_sha and c.generic_dumps == f.generic_dumps
    assert c.results_dir.name == "e8mf" and c.tokens_dir.name == "e8mf" and c.results_dir != f.results_dir
    assert c.text == m.text == MLPERF_TEXT and c.band == f.band
    assert (c.verdict_k, c.report_k, c.holdout_frac, c.stride) == (f.verdict_k, f.report_k, f.holdout_frac, f.stride)
    assert "Llama-3" in c.scope_note and "MLPerf" in c.scope_note and "matched-KV" in c.scope_note


def test_the_gates_are_additive_and_name_an_entry_the_ledger_does_not_have():
    m, f = _load("e8m"), _load("e8mf")
    assert m.gate == ("0064",) and f.gate == ("0039", "0064")        # 0039 stays: it registered the Llama E8 cell
    assert e8_driver.required_entries(m) == e8_driver.REQUIRED_ENTRIES + ("### 0064 ",)
    assert e8_driver.required_entries(f) == e8_driver.REQUIRED_ENTRIES + ("### 0039 ", "### 0064 ")
    ledger = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8")
    # unregistered by construction: the day 0064 lands, this assertion and the PROVISIONAL note in both configs go
    # together, in the staging commit that fixes the number
    assert "### 0064 " not in ledger and "### 0039 " in ledger
