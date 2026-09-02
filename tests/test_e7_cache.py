"""Cache-aware readings of the H-E7a denominator (entry 0024): the registered cold reading
reproduces the 0018 denominator by construction; the request-level warm reading prices the
byte-identical prefix shared with the preceding request at read_mult."""
import pytest

from linear_ceiling.e7_cache import READINGS, cache_aware_block, render, request_level_costs, request_prompts
from linear_ceiling.e7_cost import timeline, totals
from linear_ceiling.e7_headroom import rows as headroom_rows
from linear_ceiling.e7_traces import Msg, Trajectory

PRICING = {"read_mult": 0.1, "write_mult": 1.25, "ttl_seconds": 300}


def _traj(msgs, tid="c/1", agent="composio"):
    return Trajectory(suite="swe-bench", agent=agent, traj_id=tid, reward=None, messages=tuple(msgs))


def _two_requests():
    # request 0: SYS (4 tokens) + task (2) -> response; request 1: SYS (4) + summary prompt (6) -> response
    msgs = [Msg(role="system", tokens=4, request=0), Msg(role="user", tokens=2, request=0),
            Msg(role="assistant", tokens=3, model="m1", request=0),
            Msg(role="system", tokens=4, request=1), Msg(role="user", tokens=6, request=1),
            Msg(role="assistant", tokens=1, model="m2", request=1)]
    texts = ["SYS PROMPT TOOL SCHEMA", "solve it", "I did", "SYS PROMPT TOOL SCHEMA", "summarize: solve it I did ok", "sum"]
    return _traj(msgs), texts


def test_request_prompts_exclude_the_response_and_keep_order():
    t, texts = _two_requests()
    reqs = request_prompts(t, texts)
    assert [r["request"] for r in reqs] == [0, 1]
    assert reqs[0]["prompt_tokens"] == 6 and reqs[0]["text"] == "SYS PROMPT TOOL SCHEMA\nsolve it"
    assert reqs[1]["prompt_tokens"] == 10 and reqs[1]["text"].startswith("SYS PROMPT TOOL SCHEMA\n")
    assert request_prompts(_traj([Msg(role="user", tokens=1), Msg(role="assistant", tokens=1)]), ["a", "b"]) == []


def test_request_level_warm_prices_the_shared_prefix_at_read_mult():
    t, texts = _two_requests()
    c = request_level_costs(t, texts, PRICING)
    assert c["requests"] == 2 and c["cost_cold"] == 16 and c["input_tokens"] == 16
    # request 1: shared prefix "SYS PROMPT TOOL SCHEMA\ns" (both prompts continue with "s") = 24 of the
    # 51 chars of its prompt -> 10 * 24/51 tokens attributed to the prefix, character-proportional
    shared = 10 * 24 / 51
    assert c["shared_prefix_tokens"] == pytest.approx(shared)
    assert c["cost_warm"] == pytest.approx(6 * 1.25 + shared * 0.1 + (10 - shared) * 1.25)
    assert c["cost_warm"] < c["cost_cold"] * 1.25


def test_no_request_boundaries_is_none_not_zero():
    t = _traj([Msg(role="user", tokens=5), Msg(role="assistant", tokens=1, model="m")])
    assert request_level_costs(t, ["a b", "c"], PRICING) is None


def test_block_registered_cold_equals_the_timeline_denominator_and_ratios_follow():
    t, texts = _two_requests()
    hr = headroom_rows([t], {t.traj_id: texts}, PRICING["read_mult"])
    assert len(hr) == 1
    cb = cache_aware_block([t], {t.traj_id: texts}, hr, PRICING, cutoff=0.10)
    p = cb["pooled"]
    tot = totals(timeline(t, PRICING))
    assert p["denominators"]["registered_cold"] == tot["input_tokens"] == tot["cost_cold"]
    assert p["denominators"]["registered_warm"] == pytest.approx(tot["cost_warm"])
    assert p["denominators"]["request_cold"] == 16
    assert p["recoverable_upper_bound"] == pytest.approx(hr[0]["headroom_upper_bound"])
    for key in READINGS:
        assert p["ratios"][key] == pytest.approx(p["recoverable_upper_bound"] / p["denominators"][key])
        assert p["below_cutoff"][key] == (p["ratios"][key] < 0.10)
    assert p["request_shared_prefix_fraction"] == pytest.approx((10 * 24 / 51) / 16)
    assert cb["per_suite"]["swe-bench"]["measurable_trajs"] == 1
    md = render(cb)
    assert "registered requests, COLD (= 0018)" in md and "NOT re-stated" in md


def test_measurable_trajectory_without_text_is_not_computable_at_request_level():
    t, texts = _two_requests()
    u = _traj([Msg(role="user", tokens=5, request=0), Msg(role="assistant", tokens=1, model="m", request=0),
               Msg(role="assistant", tokens=1, model="n", request=1)], tid="c/2")
    hr = headroom_rows([t], {t.traj_id: texts}, 0.1)
    cb = cache_aware_block([t, u], {t.traj_id: texts}, hr, PRICING, cutoff=0.10)
    p = cb["pooled"]
    assert p["measurable_trajs"] == 2 and p["request_level_not_computable"] == 1
    assert p["denominators"]["request_cold"] == 16                         # u contributes nothing, not zero
    only_u = cache_aware_block([u], {}, [], PRICING, cutoff=0.10)["pooled"]
    assert only_u["denominators"]["request_cold"] is None and only_u["ratios"]["request_warm"] is None
    assert "NOT COMPUTABLE" in render(only_u and cache_aware_block([u], {}, [], PRICING, cutoff=0.10))


def test_unmeasurable_trajectories_stay_out_of_every_denominator():
    t, texts = _two_requests()
    plain = _traj([Msg(role="user", tokens=1000), Msg(role="assistant", tokens=1)], tid="c/3", agent="other")
    hr = headroom_rows([t], {t.traj_id: texts}, 0.1)
    cb = cache_aware_block([t, plain], {t.traj_id: texts}, hr, PRICING, cutoff=0.10)
    assert cb["pooled"]["measurable_trajs"] == 1
    assert cb["pooled"]["denominators"]["registered_cold"] == totals(timeline(t, PRICING))["input_tokens"]
