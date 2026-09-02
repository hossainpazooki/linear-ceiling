"""The summarizer's REFUSALS are the point: a summarizer that cannot fail closed is decoration.

Each test tampers with exactly one thing and proves the refusal names it. The fixture is the
synthetic three-suite corpus from test_e7_corpus written to tmp_path, so these run offline
with no real traces and still exercise headroom rows, reported usage, and the unparsed set.
"""
import json

import pytest

from linear_ceiling.config import E7Config
from linear_ceiling.summarize_e7 import summarize

TOKENIZER = {"encoding": "o200k_base", "default_strategy": "calibrated",
             "agent_strategy": {}, "divisors": {"system": 4.817, "user": 4.322,
                                                "assistant": 4.005, "tool_output": 2.890,
                                                "tool_args": 3.467}}
PRICING = {"provider": "anthropic", "read_mult": 0.1, "write_mult": 1.25,
           "write_mult_1h": 2.0, "ttl_seconds": 300}
THRESHOLDS = {"materiality_fraction": 0.10, "negative_mass_fraction": 0.25,
              "min_trajectories_per_suite": 1, "min_agents_per_suite": 1, "min_suites": 1}

@pytest.fixture
def env(tmp_path):
    """Build a config + a three-suite corpus + a genuine report by running the driver's own logic.

    The corpus fixture is shared with test_e7_corpus: tau-bench, tau2-bench (reported usage),
    and swe-bench with a role/content submission, a nested instance, a LangChain submission that
    switches model (headroom rows), and one unparseable file.
    """
    from tests.test_e7_corpus import write_corpus
    write_corpus(tmp_path / "traces", garbage=True)
    (tmp_path / "results").mkdir()
    cfgp = tmp_path / "e7.toml"
    cfgp.write_text("# synthetic\n", encoding="utf-8")
    tf = tmp_path / "traces" / "tau-bench" / "gpt-4o-airline.json"
    cfg = E7Config(traces_dir=tmp_path / "traces", results_dir=tmp_path / "results",
                   pricing=PRICING, thresholds=THRESHOLDS, tokenizer=TOKENIZER,
                   lane_b_policy="two-tier-cascade", config_path=cfgp)
    from linear_ceiling.e7_manifest import write as write_manifest
    write_manifest(cfg, list_fn=None)          # the committed corpus manifest (entry 0024), no S3 here
    from linear_ceiling import e7 as driver
    # build the report exactly as the driver does, without its git gate
    monkey = driver.assert_ready
    driver.assert_ready = lambda *a, **k: None
    try:
        driver.run(cfg, repo_root=tmp_path)
    finally:
        driver.assert_ready = monkey
    return cfg, tmp_path / "results" / "skeleton_report.json", tf


def _write(p, obj):
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def test_clean_report_summarizes(env):
    cfg, _, _ = env
    md = summarize(cfg)
    assert "recomputed from the raw traces" in md and "gpt-4o" in md
    assert "tau2-bench" in md and "swe-bench" in md
    assert "UPPER BOUND" in md and "LOWER BOUND" in md
    assert "switches measured: 1" in md and "byte-identical handoffs: 0/1" in md
    assert "unparsed trajectories (recorded, never counted): 1" in md
    assert "Lane A only, excluded from floor arithmetic (entry 0011): composio_swekit: 1" in md
    assert "manifest sha256" in md and "SWE-bench selection" in md


# --- the committed corpus manifest is a third party to provenance (entry 0024) ---------------

def _manifest(cfg):
    from linear_ceiling.e7_manifest import manifest_path
    p = manifest_path(cfg)
    return p, json.loads(p.read_text(encoding="utf-8"))


def test_refuses_without_a_manifest(env):
    cfg, _, _ = env
    p, _ = _manifest(cfg)
    p.unlink()
    with pytest.raises(ValueError, match="no corpus manifest"):
        summarize(cfg)


def test_refuses_manifest_hash_edited_naming_the_path(env):
    """A byte flipped in the manifest's record of one file: refused by path, before any
    number is compared."""
    cfg, _, _ = env
    p, m = _manifest(cfg)
    m["files"][0]["sha256"] = "0" * 64
    _write(p, m)
    with pytest.raises(ValueError, match=f"does not match the manifest hash: {m['files'][0]['path']}"):
        summarize(cfg)


def test_refuses_manifest_missing_a_file_that_is_on_disk(env):
    cfg, _, _ = env
    p, m = _manifest(cfg)
    gone = m["files"].pop()["path"]
    _write(p, m)
    with pytest.raises(ValueError, match=f"not in the manifest: {gone}"):
        summarize(cfg)


def test_refuses_manifest_listing_a_file_absent_from_disk(env):
    cfg, _, _ = env
    p, m = _manifest(cfg)
    m["files"].append(dict(m["files"][0], path="tau-bench/phantom-airline.json"))
    _write(p, m)
    with pytest.raises(ValueError, match="missing on disk: tau-bench/phantom-airline.json"):
        summarize(cfg)


def test_refuses_report_produced_against_a_different_manifest(env):
    """Disk and manifest agree, but the report was not produced against THIS manifest
    (regenerated since the run): refused, rerun the driver."""
    cfg, _, _ = env
    p, m = _manifest(cfg)
    m["selection_note"] = "regenerated after the run"
    _write(p, m)
    with pytest.raises(ValueError, match="manifest_sha256 mismatch"):
        summarize(cfg)


def test_refuses_report_that_predates_the_manifest(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    del rep["manifest_sha256"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="report has no `manifest_sha256` section"):
        summarize(cfg)


def test_refuses_when_a_trace_file_changed(env):
    cfg, _, tf = env
    doctored = json.loads(tf.read_text(encoding="utf-8"))
    doctored[0]["traj"][0]["content"] = "u" * 41          # one character
    _write(tf, doctored)
    with pytest.raises(ValueError, match="does not match the hash recorded"):
        summarize(cfg)


def test_refuses_on_config_drift(env):
    cfg, _, _ = env
    cfg.config_path.write_text("# changed after the run\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config_sha256 mismatch"):
        summarize(cfg)


def test_refuses_edited_cost_total(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["cost_warm"] *= 0.5   # the number a paper would quote
    _write(rp, rep)
    with pytest.raises(ValueError, match="cost_warm"):
        summarize(cfg)


def test_refuses_edited_token_count(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["input_tokens"] += 1
    _write(rp, rep)
    with pytest.raises(ValueError, match="input_tokens"):
        summarize(cfg)


def test_refuses_lane_a_flipped_to_a_false_zero(env):
    """The most damaging possible edit: unmeasurable relabelled as a measured zero."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["lane_a"] = {"measurable": True, "switches": []}
    _write(rp, rep)
    with pytest.raises(ValueError, match="lane A measurable"):
        summarize(cfg)


def test_refuses_inflated_coverage(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage"]["tau-bench"]["agents"] = ["gpt-4o", "ghost-agent", "phantom"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage"):
        summarize(cfg)


def test_refuses_floor_verdict_that_thresholds_do_not_reproduce(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage_meets_floor"] = not rep["coverage_meets_floor"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage_meets_floor"):
        summarize(cfg)


def test_refuses_nan(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["trajectories"][0]["totals"]["cost_cold"] = float("nan")
    rp.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    with pytest.raises(ValueError, match="NaN"):
        summarize(cfg)


def test_refuses_missing_provenance(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    del rep["trace_files"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="provenance is unverifiable"):
        summarize(cfg)


def test_refuses_edited_headroom_row(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    assert len(rep["headroom"]["rows"]) == 1
    rep["headroom"]["rows"][0]["overlap_fraction"] = 1.0        # claim a perfect handoff
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"headroom\.rows\[0\]\.overlap_fraction"):
        summarize(cfg)


def test_refuses_edited_headroom_summary(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["headroom"]["summary"]["recoverable_fraction"]["median"] += 0.05   # the paper's headline
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"headroom\.summary\.recoverable_fraction\.median"):
        summarize(cfg)


def test_refuses_headroom_flipped_to_byte_identical(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["headroom"]["rows"][0]["byte_identical"] = True
    rep["headroom"]["summary"]["byte_identical"] = 1
    _write(rp, rep)
    with pytest.raises(ValueError, match="byte_identical"):
        summarize(cfg)


def test_refuses_dropped_headroom_row(env):
    """Deleting a switch row is the quiet way to move a median."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["headroom"]["rows"] = []
    rep["headroom"]["summary"] = None
    _write(rp, rep)
    with pytest.raises(ValueError, match="headroom"):
        summarize(cfg)


def test_refuses_edited_reported_usage_offset(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["reported_usage"]["per_role"]["assistant"]["offset"]["median"] = 0   # "no hidden prefix"
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"reported_usage\.per_role\.assistant\.offset\.median"):
        summarize(cfg)


def test_refuses_pooled_usage_series(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    pooled = rep["reported_usage"]["per_role"].pop("user")
    rep["reported_usage"]["per_role"]["all"] = pooled
    _write(rp, rep)
    with pytest.raises(ValueError, match="key set differs"):
        summarize(cfg)


def test_refuses_lane_a_only_agent_folded_into_coverage(env):
    """Entry 0011: composio is a Lane A subject, not a coverage contributor."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage"]["swe-bench"]["agents"].append("composio_swekit")
    rep["coverage"]["swe-bench"]["trajectories"] += 1
    rep["lane_a_only"] = {}
    _write(rp, rep)
    with pytest.raises(ValueError, match="coverage"):
        summarize(cfg)


def test_refuses_unparsed_trajectory_erased(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    assert len(rep["unparsed"]) == 1
    rep["unparsed"] = []
    _write(rp, rep)
    with pytest.raises(ValueError, match="unparsed"):
        summarize(cfg)


def test_refuses_per_suite_floor_verdict_edit(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["suite_floor"]["tau-bench"] = not rep["suite_floor"]["tau-bench"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="suite_floor"):
        summarize(cfg)


def test_refuses_narrowed_detector_key_set(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["lane_a_detector_keys"] = ["model"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="lane_a_detector_keys"):
        summarize(cfg)


def test_refuses_trace_file_added_after_the_run(env):
    cfg, _, tf = env
    (tf.parent / "gpt-4o-retail.json").write_text(tf.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="trace set changed since the run"):
        summarize(cfg)


def test_refuses_edited_task_count(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["coverage"]["tau2-bench"]["tasks"] += 1
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"coverage\.tau2-bench\.tasks"):
        summarize(cfg)


def test_provenance_keys_are_relative_posix_paths(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    keys = list(rep["trace_files"])
    assert all("\\" not in k and not k.startswith("/") for k in keys)
    assert "swe-bench/20250122_autocoderover/inst-2/attempt_0/patch_0.diff" in keys
    assert "tau2-bench/agent-x_airline.json" in keys


def test_refuses_relabelled_tokenizer_strategy(env):
    """Calling a calibrated estimate 'exact' is a provenance lie about every token count."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["tokenizer"]["per_agent_strategy"]["composio_swekit"] = "exact"
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"tokenizer\.per_agent_strategy"):
        summarize(cfg)


def test_refuses_cost_basis_label_edit(env):
    """Dropping the LOWER BOUND wording is a claim change, not a typo."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["cost_basis"] = "full billed prompt"
    _write(rp, rep)
    with pytest.raises(ValueError, match="cost_basis"):
        summarize(cfg)


def test_refuses_taxonomy_count_edit(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["taxonomy"]["pooled"]["model_switch"]["events"] += 1
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"taxonomy\.pooled\.model_switch\.events"):
        summarize(cfg)


def test_refuses_unmeasurable_class_recorded_as_zero(env):
    """Entry 0014: NOT MEASURABLE enters neither side; a recorded 0 there is the forbidden zero."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    tid = next(k for k, v in rep["taxonomy"]["per_trajectory"].items() if not v["compaction"]["measurable"])
    rep["taxonomy"]["per_trajectory"][tid]["compaction"] = {"measurable": True, "events": 0}
    row = rep["taxonomy"]["pooled"]["compaction"]
    row["measurable_trajs"] += 1
    row["not_measurable"] -= 1
    _write(rp, rep)
    with pytest.raises(ValueError, match="taxonomy"):
        summarize(cfg)


def test_refuses_h_e7a_ratio_edit(env):
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    assert rep["h_e7a"]["pooled"]["ratio"] is not None
    rep["h_e7a"]["pooled"]["ratio"] = 0.5
    rep["h_e7a"]["pooled"]["below_cutoff"] = False
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"h_e7a\.pooled\.ratio"):
        summarize(cfg)


def test_refuses_h_e7a_denominator_widened(env):
    """Folding unmeasurable trajectories into the denominator counts them as zero-switch."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    rep["h_e7a"]["pooled"]["input_spend"] *= 10
    rep["h_e7a"]["pooled"]["measurable_trajs"] += 5
    _write(rp, rep)
    with pytest.raises(ValueError, match=r"h_e7a\.pooled"):
        summarize(cfg)


def test_summary_states_the_ratio_without_a_verdict(env):
    cfg, _, _ = env
    md = summarize(cfg)
    assert "H-E7a ratio" in md and "the cutoff" in md
    assert "NOT MEASURABLE" in md and "n/m" in md
    assert "verdict is NOT stated" in md


def test_refuses_report_from_an_older_driver(env):
    """A report lacking a section this summarizer compares must be regenerated, not summarized."""
    cfg, rp, _ = env
    rep = json.loads(rp.read_text(encoding="utf-8"))
    del rep["taxonomy"]
    _write(rp, rep)
    with pytest.raises(ValueError, match="report has no `taxonomy` section"):
        summarize(cfg)
