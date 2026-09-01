"""Token counting for E7: exact where a public tokenizer exists, calibrated where none does.

Why not one blanket chars/N estimator (the obvious reading of "approximate"): measured
against o200k_base over the full tau-bench corpus (34.4M chars / 9.25M tokens, 2026-09-01),
chars-per-token is NOT uniform across content types --

    tool_output(JSON-ish)   2.890     chars/4 errs -27.8%
    tool_call_args(JSON)    3.467     chars/4 errs -13.3%
    assistant(prose)        4.005     chars/4 errs  +0.1%
    user(prose)             4.322     chars/4 errs  +8.0%
    system(prompt)          4.817     chars/4 errs +20.4%
    OVERALL                 3.723     chars/4 errs  -6.9%

A uniform multiplicative bias would cancel in E7's verdict-bearing quantities, which are both
ratios. This bias is not uniform, and it is largest exactly on tool output -- the content
that context compaction preferentially removes -- so a blanket chars/4 would push H-E7b's
break-even in a systematic direction. Hence per-content-type divisors, in config, not code.

Strategy per agent (config `[e7.tokenizer]`):
- `exact`: the agent's own public encoder (gpt-4o -> o200k_base via tiktoken). No estimate.
- `calibrated`: per-content-type divisors measured on the exact half of the SAME suite.
  Stated assumption, unverifiable offline: the target model's tokenizer has similar
  chars-per-token to o200k_base on this content. Anthropic publishes no tokenizer, so this
  cannot be checked without a network call to their counting endpoint; any number produced
  under `calibrated` carries that assumption.

Determinism: tiktoken downloads its BPE file once and caches it; after that this module is
offline and deterministic. Pin the encoding by name (config), never "the default for model X".
"""
import math

CONTENT_TYPES = ("system", "user", "assistant", "tool_output", "tool_args")


def _exact_counter(encoding: str):
    import tiktoken  # imported lazily so the rest of the package stays dependency-free
    enc = tiktoken.get_encoding(encoding)

    def count(text: str, content_type: str = "assistant") -> int:
        return len(enc.encode(text)) if text else 0

    return count


def _calibrated_counter(divisors: dict):
    missing = [c for c in CONTENT_TYPES if c not in divisors]
    if missing:
        raise ValueError(f"[e7.tokenizer.divisors] is missing {missing}; every content type must "
                         "carry a measured divisor or its counts would silently fall back")

    def count(text: str, content_type: str = "assistant") -> int:
        if not text:
            return 0
        if content_type not in divisors:
            raise ValueError(f"unknown content type {content_type!r}: refusing to guess a divisor")
        return math.ceil(len(text) / divisors[content_type])

    return count


def make_counter(agent: str, tokenizer_cfg: dict):
    """Return a `count(text, content_type) -> int` for this agent, per registered strategy."""
    strategies = tokenizer_cfg.get("agent_strategy", {})
    strategy = strategies.get(agent, tokenizer_cfg.get("default_strategy", "calibrated"))
    if strategy == "exact":
        return _exact_counter(tokenizer_cfg["encoding"])
    if strategy == "calibrated":
        return _calibrated_counter(tokenizer_cfg["divisors"])
    raise ValueError(f"unknown tokenizer strategy {strategy!r} for agent {agent!r}")


def strategy_for(agent: str, tokenizer_cfg: dict) -> str:
    return tokenizer_cfg.get("agent_strategy", {}).get(
        agent, tokenizer_cfg.get("default_strategy", "calibrated"))
