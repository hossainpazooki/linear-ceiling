"""`summarize_e7 --strategy-override` (entry 0022's tokenizer sensitivity as a flag).

Synthetic tests run on the shared three-suite fixture. The pinning test against the REAL corpus
(0022's recount: composio family exact -> 0.2210% under the registered reading) runs only when
the gitignored traces are present AND `LC_REAL_TRACES=1` is set, because it loads the full
corpus twice (minutes); it is the test the ruling names and it is not optional once traces exist.
"""
import json
import os
from pathlib import Path

import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config
from linear_ceiling.summarize_e7 import parse_override, summarize
from tests.test_summarize_e7 import env  # noqa: F401  (pytest fixture)

AGENTS = ["gpt-4o", "agent-x", "honeycomb", "autocoderover", "composio_swekit"]


def test_parse_override_patterns_and_refusals():
    assert parse_override("composio_swekit=exact", AGENTS) == {"composio_swekit": "exact"}
    assert parse_override("gpt-4*=exact, honeycomb=calibrated", AGENTS) == {"gpt-4o": "exact", "honeycomb": "calibrated"}
    with pytest.raises(ValueError, match="matches no agent"):
        parse_override("o1-mini=exact", AGENTS)            # o1-mini is a MODEL inside composio, not an agent
    with pytest.raises(ValueError, match="not AGENT=strategy"):
        parse_override("composio_swekit", AGENTS)
    with pytest.raises(ValueError, match="unknown strategy"):
        parse_override("composio_swekit=guess", AGENTS)
    with pytest.raises(ValueError, match="empty"):
        parse_override(" , ", AGENTS)


def test_override_recomputes_readings_and_labels_them_sensitivity(env):
    cfg, rp, _ = env
    md = summarize(cfg, strategy_override="composio_swekit=exact")
    assert "Tokenizer-strategy sensitivity" in md and "decides nothing" in md
    assert "strategies replaced: composio_swekit: calibrated -> exact" in md
    recon = json.loads((cfg.results_dir / "recon.json").read_text(encoding="utf-8"))
    rep = json.loads(rp.read_text(encoding="utf-8"))
    sb = recon["sensitivity"]
    assert sb["label"] == "sensitivity" and sb["registered_config_sha256_untouched"] is True
    assert recon["config_sha256"] == rep["config_sha256"]                # the registered config is what is cited
    assert sb["effective_strategy"]["composio_swekit"] == "exact"
    assert sb["effective_strategy"]["honeycomb"] == "calibrated"          # untouched agents keep theirs
    assert sb["registered_reading"]["registered"] == rep["h_e7a"]["pooled"]
    ov = sb["registered_reading"]["override"]
    assert ov["measurable_trajs"] == rep["h_e7a"]["pooled"]["measurable_trajs"]   # the 0014 set is unchanged
    assert set(sb["cache_aware_override"]["readings"]) == {"registered_cold", "registered_warm", "request_cold", "request_warm"}
    # the override recounted composio messages (exact vs ceil(chars/divisor)) and nothing else;
    # the synthetic prefix totals happen to tie (3+9+11 == 2+9+13), which is why counts are recorded too
    assert sb["messages_recounted_per_agent"] == {"composio_swekit": 2}
    assert set(sb["input_tokens_per_agent"]) <= {"composio_swekit"}
    assert ov["input_spend"] == sb["cache_aware_override"]["pooled"]["denominators"]["registered_cold"]
    # the report itself is untouched: a second plain summary still verifies
    assert "recomputed from the raw traces" in summarize(cfg)


def test_override_refuses_a_pattern_matching_nothing_and_writes_no_recon(env):
    cfg, _, _ = env
    with pytest.raises(ValueError, match="matches no agent"):
        summarize(cfg, strategy_override="o1-mini=exact")
    assert not (cfg.results_dir / "recon.json").exists()


def test_override_does_not_run_on_a_refused_report(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["h_e7a"]["pooled"]["ratio"] = 0.5
    rp.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    with pytest.raises(ValueError):
        summarize(cfg, strategy_override="composio_swekit=exact")
    assert not (cfg.results_dir / "recon.json").exists()


_TRACES = REPO_ROOT / "traces" / "swe-bench"


@pytest.mark.skipif(os.environ.get("LC_REAL_TRACES") != "1" or not _TRACES.is_dir(),
                    reason="real corpus: set LC_REAL_TRACES=1 with traces/ acquired (gitignored)")
def test_pin_composio_exact_reproduces_entry_0022():
    """The ruling's pin: the composio family recounted exact under the registered reading gives
    entry 0022's 565,025 / 255,690,850 = 0.2210%. (0022 recounted the whole family; o1-mini is the
    receiver MODEL inside it, not an agent, so the agent-level override is `composio_swekit=exact`.)"""
    cfg = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    summarize(cfg, strategy_override="composio_swekit=exact")
    sb = json.loads((cfg.results_dir / "recon.json").read_text(encoding="utf-8"))["sensitivity"]
    ov = sb["registered_reading"]["override"]
    assert round(ov["recoverable_upper_bound"]) == 565_025
    assert ov["input_spend"] == 255_690_850
    assert f"{100 * ov['ratio']:.4f}%" == "0.2210%"
    assert f"{100 * sb['registered_reading']['registered']['ratio']:.4f}%" == "0.2030%"
