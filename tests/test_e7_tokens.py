"""Token-counter tests (entry 0009). The calibrated path is offline; the exact path is
skipped when tiktoken/its BPE cache is unavailable, so CI never depends on a download."""
import math

import pytest

from linear_ceiling.e7_tokens import make_counter, strategy_for

CFG = {
    "encoding": "o200k_base",
    "default_strategy": "calibrated",
    "agent_strategy": {"gpt-4o": "exact", "sonnet-35-new": "calibrated"},
    "divisors": {"system": 4.817, "user": 4.322, "assistant": 4.005,
                 "tool_output": 2.890, "tool_args": 3.467},
}


def test_strategy_selection_and_default():
    assert strategy_for("gpt-4o", CFG) == "exact"
    assert strategy_for("sonnet-35-new", CFG) == "calibrated"
    assert strategy_for("some-future-agent", CFG) == "calibrated"   # default, never silent-exact


def test_calibrated_uses_per_type_divisors():
    c = make_counter("sonnet-35-new", CFG)
    text = "x" * 289
    # tool output is the most compressed type: same text must cost MORE tokens than prose
    assert c(text, "tool_output") == math.ceil(289 / 2.890)
    assert c(text, "assistant") == math.ceil(289 / 4.005)
    assert c(text, "tool_output") > c(text, "assistant")
    assert c(text, "system") < c(text, "assistant")   # system prompts compress best
    assert c("", "assistant") == 0


def test_calibrated_refuses_unknown_content_type():
    c = make_counter("sonnet-35-new", CFG)
    with pytest.raises(ValueError, match="refusing to guess"):
        c("text", "not_a_type")


def test_missing_divisor_is_refused_not_defaulted():
    bad = {**CFG, "divisors": {"system": 4.8}}
    with pytest.raises(ValueError, match="missing"):
        make_counter("sonnet-35-new", bad)


def test_unknown_strategy_refused():
    with pytest.raises(ValueError, match="unknown tokenizer strategy"):
        make_counter("x", {**CFG, "default_strategy": "vibes"})


def test_exact_counter_matches_the_encoder():
    tiktoken = pytest.importorskip("tiktoken")
    try:
        enc = tiktoken.get_encoding("o200k_base")
    except Exception:                                    # no cached BPE and no network
        pytest.skip("o200k_base unavailable offline")
    c = make_counter("gpt-4o", CFG)
    s = '{"user_id":"mia_li_3668"}'
    assert c(s, "tool_args") == len(enc.encode(s))
    # exact counting ignores content type -- the encoder is the ground truth either way
    assert c(s, "tool_args") == c(s, "system")
