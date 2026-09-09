"""E9-long (entry 0035): the context floor, the scaled receiver on every dump, the bridge control, the
registered run order, resume after a crash, and the partial close -- on the synthetic corpus."""
import json
from dataclasses import replace

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling import e9 as driver
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import _stem, entry_list, required_markers, rope_args, run_order
from linear_ceiling.e9_align import Alignment, coverage_comparison
from tests.test_e9 import env, fake_runner_factory, words   # noqa: F401  (fixture reuse)

YARN = {"rope_type": "yarn", "factor": 2.5, "original_max_position_embeddings": 32768}
A_ID = "20241016_composio_x/a_traj#1"
B_ID = "20241016_composio_x/b_traj#1"
C_ID = "20241016_composio_x/c_traj#1"


def _long_cfg(cfg, **over):
    base = dict(context_cap=1000, context_floor=100, rope=dict(YARN), order_by="n_sender_asc", allow_partial=True,
                bridge={"handoffs": [A_ID], "reading_max_fstar": 0.15},
                profiles={"s_len_edges": [100, 300], "s_pos_edges": [0, 100, 300]}, keep_n=1)
    base.update(over)
    return replace(cfg, **base)


def _write_long(tmp_path, name, reps):
    """A handoff whose re-rendered receiver prompt REPEATS the sender's content (as the real composio
    handoffs do), so matched tokens exist: |S| ~ 7 * reps words, above the floor of 100 for reps >= 20."""
    from tests.test_e7_corpus import _lc_ai, _lc_human
    body = "look at the file and fix it " * reps
    traj = [[_lc_human("solve this"), _lc_ai(body, "claude-a")],
            [_lc_human("summarize the run: " + body),
             {"llm_output": {"model_name": "o1-b"}, "run": None,
              "generations": [[{"text": "Summary: done", "type": "Generation"}]]}]]
    sub = tmp_path / "traces" / "swe-bench" / "20241016_composio_x"
    (sub / f"{name}_traj.json").write_text(json.dumps(traj), encoding="utf-8")


def test_e9l_config_loads_and_e9_config_is_untouched():
    c = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
    assert c.context_cap == 81920 and c.context_floor == 32768 and c.rope == YARN
    assert c.required_entries == ("0019", "0023", "0025", "0027", "0035") and c.order_by == "n_sender_asc" and c.allow_partial
    assert len(c.bridge["handoffs"]) == 3 and c.bridge["reading_max_fstar"] == 0.15
    assert c.profiles == {"s_len_edges": [32768, 50000, 65000], "s_pos_edges": [0, 32768, 49152, 65536]}
    assert c.keep_n == 3 and c.keep_seed == 9 and c.results_dir.name == "e9l"
    e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
    # the rule, tau, ladder, controls are byte-for-byte E9's
    assert c.rule == e9.rule and c.controls == e9.controls and c.mapper_k == e9.mapper_k
    assert e9.context_floor == 0 and e9.rope is None and e9.required_entries == () and e9.order_by == "id"
    assert not e9.allow_partial and e9.bridge is None and e9.profiles is None
    assert required_markers(e9) == driver.REQUIRED_ENTRIES
    assert required_markers(c) == ("### 0019 ", "### 0023 ", "### 0025 ", "### 0027 ", "### 0035 ")
    assert entry_list(c) == "0019/0023/0025/0027/0035" and rope_args(e9) == []
    assert json.loads(rope_args(c)[1]) == YARN and rope_args(c)[0] == "--rope-scaling"


@pytest.mark.parametrize("old,new,msg", [
    ("context_floor = 32768", "context_floor = 81920", "context_floor"),
    ("factor = 2.5", "factor = 1.0", "rope"),
    ("factor = 2.5", "factor = 2.0", "exceeds the scaled window"),      # 32768 x 2 = 65536 < cap 81920
    ('by = "n_sender_asc"', 'by = "random"', "order"),
    ("reading_max_fstar = 0.15", "reading_max_fstar = 1.5", "reading_max_fstar"),
    ("s_pos_edges = [0, 32768, 49152, 65536]", "s_pos_edges = [0, 49152, 32768]", "s_pos_edges"),
    ("s_len_edges = [32768, 50000, 65000]", "s_len_edges = [1000, 50000]", "s_len_edges"),
    ('required_entries = ["0019", "0023", "0025", "0027", "0035"]', 'required_entries = ["35"]', "required_entries")])
def test_e9l_config_refuses_malformed_0035_parameters(tmp_path, old, new, msg):
    src = (REPO_ROOT / "config" / "e9l.toml").read_text(encoding="utf-8")
    assert old in src
    p = tmp_path / "e9l.toml"
    p.write_text(src.replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, tmp_path)


def test_bridge_without_rope_is_refused(tmp_path):
    src = (REPO_ROOT / "config" / "e9l.toml").read_text(encoding="utf-8")
    cut = src.replace("[e9.rope]", "[e9.rope_off]")
    p = tmp_path / "e9l.toml"
    p.write_text(cut, encoding="utf-8")
    with pytest.raises(ValueError, match="needs \\[e9.rope\\]"):
        load_e9_config(p, tmp_path)


def test_context_floor_excludes_handoffs_decided_under_the_prior_cap(env, tmp_path):
    cfg, e7, calls, _ = env
    cfg = _long_cfg(cfg)
    p = driver.align_only(cfg, e7, encoder=words)
    cov = json.loads(p.read_text(encoding="utf-8"))
    assert cov["coverage"] == {"observed": 2, "included": 1, "excluded": 1} and cov["context_floor"] == 100
    assert cov["rope"] == YARN and cov["run_order"] == [B_ID] and cov["order_by"] == "n_sender_asc"
    rec = {a["handoff_id"]: a for a in cov["alignments"]}
    assert rec[A_ID]["excluded"] and "context floor 100" in rec[A_ID]["reason"] and not rec[B_ID]["excluded"]
    cc = coverage_comparison(list(rec.values()), [], lambda xs: {"n": len(list(xs))})
    assert cc["n"] == {"included": 1, "excluded_long": 0, "excluded_empty_r": 0, "excluded_prior_cap": 1}


def test_run_order_is_by_sender_length_then_id():
    recs = [Alignment("h/b#1", 300, 10, 5, False, None, "x"), Alignment("h/a#1", 300, 10, 5, False, None, "x"),
            Alignment("h/c#1", 150, 10, 5, False, None, "x"), Alignment("h/z#1", 9999, 10, 0, True, "cap", "x")]
    inc = ["h/b#1", "h/a#1", "h/c#1"]
    assert run_order(recs, inc, "n_sender_asc") == ["h/c#1", "h/a#1", "h/b#1"]
    assert run_order(recs, inc, "id") == ["h/a#1", "h/b#1", "h/c#1"]


def test_long_run_scales_every_dump_runs_the_bridge_first_and_records_it(env, tmp_path):
    cfg, e7, calls, runner = env
    _write_long(tmp_path, "b", 40)          # replaces the fixture's unmatched long handoff: 280 words, matched
    cfg = _long_cfg(cfg)
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["complete"] and rep["run_order"] == [B_ID] and rep["context_floor"] == 100 and rep["rope"] == YARN
    assert list(rep["scores"]) == [B_ID] and rep["controls"]["handoff_id"] == B_ID
    # the bridge: two receiver dumps of the short handoff (native, then scaled), one identity-pairs score, all BEFORE
    # any long-handoff dump; both dumps kept and fingerprinted
    dumps = [c for c in calls if c[1] == "scripts/dump_kv.py"]
    scores = [c for c in calls if c[1] == "scripts/score_positions.py"]
    b_native, b_scaled = dumps[0], dumps[1]
    assert b_native[b_native.index("--out") + 1].replace("\\", "/").endswith(f"bridge/{_stem(A_ID)}/same_src") and "--rope-scaling" not in b_native
    assert b_scaled[b_scaled.index("--out") + 1].replace("\\", "/").endswith(f"bridge/{_stem(A_ID)}/scaled")
    assert json.loads(b_scaled[b_scaled.index("--rope-scaling") + 1]) == YARN and b_native[b_native.index("--which") + 1] == "target"
    assert scores[0][scores[0].index("--same-tgt") + 1].replace("\\", "/").endswith("/scaled") and "--cross-src" not in scores[0]
    assert scores[0][scores[0].index("--out") + 1].replace("\\", "/").endswith(f"bridge/{_stem(A_ID)}.json")
    assert calls.index(scores[0]) < calls.index(dumps[2])
    # every dump of the long handoff (3 + the prefix-invariance dump) carries the scaling
    for d in dumps[2:]:
        assert json.loads(d[d.index("--rope-scaling") + 1]) == YARN
    assert len(dumps) == 2 + 4
    br = rep["bridge"]
    assert br["reading_max_fstar"] == 0.15 and set(br["handoffs"]) == {A_ID}
    b = br["handoffs"][A_ID]
    assert set(b["kept_dumps"]) == {"same_src", "scaled"} and b["n_sender"] > 0 and b["kept_dir"].endswith(_stem(A_ID))
    assert (cfg.results_dir / "bridge" / b["score_file"]).exists() and (cfg.results_dir / "bridge" / b["tokens_file"]).exists()
    assert np.load(cfg.results_dir / "bridge" / _stem(A_ID) / b["pairs_file"])["pairs"].shape == (b["n_sender"], 2)
    # the bridge handoff is NOT in the verdict set: it sits below the floor
    assert A_ID not in rep["scores"] and any(a["handoff_id"] == A_ID and a["excluded"] for a in rep["alignments"])


def test_bridge_handoff_must_be_observed_and_within_the_cap(env, tmp_path):
    cfg, e7, _, runner = env
    with pytest.raises(RuntimeError, match="not among the observed handoffs"):
        driver.run(_long_cfg(cfg, bridge={"handoffs": ["nope/x#1"], "reading_max_fstar": 0.15}), e7,
                   repo_root=tmp_path, runner=runner, encoder=words)
    with pytest.raises(RuntimeError, match="excluded at the cap"):
        driver.run(_long_cfg(cfg, context_cap=150, context_floor=50, bridge={"handoffs": [B_ID], "reading_max_fstar": 0.15},
                             profiles=None), e7, repo_root=tmp_path, runner=runner, encoder=words)   # fixture's b: |S| > 150


def _crash_on(stem_fragment, calls):
    good = fake_runner_factory(calls=calls)

    def runner(cmd, cwd, capture_output):
        if cmd[1].endswith("dump_kv.py") and stem_fragment in cmd[cmd.index("--out") + 1].replace("\\", "/"):
            raise RuntimeError("box reclaimed")
        return good(cmd, cwd, capture_output)
    return runner


def test_resume_keeps_hash_matching_scores_and_the_bridge(env, tmp_path):
    cfg, e7, calls, runner = env
    _write_long(tmp_path, "b", 40)
    _write_long(tmp_path, "c", 20)
    cfg = _long_cfg(cfg, keep_n=0)
    # first launch: c (150 words) scores, then the box dies dumping b
    with pytest.raises(RuntimeError, match="box reclaimed"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=_crash_on(_stem(B_ID), calls), encoder=words)
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    assert not rep["complete"] and list(rep["scores"]) == [C_ID] and rep["run_order"] == [C_ID, B_ID] and rep["bridge"]
    # a plain relaunch refuses; --resume keeps c and the bridge and scores only b
    with pytest.raises(RuntimeError, match="relaunch with --resume"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    calls.clear()
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words, resume=True)
    rep2 = json.loads(out.read_text(encoding="utf-8"))
    assert rep2["complete"] and list(rep2["scores"]) == [C_ID, B_ID] and rep2["resumed_from"]["scored"] == [C_ID]
    assert rep2["resumed_from"]["bridge"] and rep2["resumed_from"]["controls"] and rep2["controls"]["handoff_id"] == C_ID
    outs = [c[c.index("--out") + 1].replace("\\", "/") for c in calls if c[1].endswith("dump_kv.py")]
    assert not any("bridge" in o or _stem(C_ID) in o for o in outs) and any(_stem(B_ID) in o for o in outs)
    assert rep2["scores"][C_ID] == rep["scores"][C_ID] and rep2["bridge"] == rep["bridge"]
    # a tampered per-token file is NOT kept on resume
    tf = cfg.results_dir / "tokens" / rep2["scores"][B_ID]["tokens_file"]
    rep2["complete"] = False
    (cfg.results_dir / "report.json").write_text(json.dumps(rep2), encoding="utf-8")
    tf.write_bytes(b"x")
    calls.clear()
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words, resume=True)
    rep3 = json.loads(out.read_text(encoding="utf-8"))
    assert rep3["resumed_from"]["scored"] == [C_ID] and any(_stem(B_ID) in c[c.index("--out") + 1].replace("\\", "/")
                                                            for c in calls if c[1].endswith("dump_kv.py"))
    with pytest.raises(RuntimeError, match="on a complete report"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words, resume=True)


def test_close_partial_needs_the_registration_a_prefix_and_names_the_unscored(env, tmp_path):
    cfg, e7, calls, runner = env
    _write_long(tmp_path, "b", 40)
    _write_long(tmp_path, "c", 20)
    cfg = _long_cfg(cfg, keep_n=0)
    with pytest.raises(RuntimeError, match="no report to close"):
        driver.close_partial(cfg)
    with pytest.raises(RuntimeError, match="box reclaimed"):
        driver.run(cfg, e7, repo_root=tmp_path, runner=_crash_on(_stem(B_ID), calls), encoder=words)
    with pytest.raises(RuntimeError, match="does not register a partial close"):
        driver.close_partial(replace(cfg, allow_partial=False))
    out = driver.close_partial(cfg)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["complete"] and rep["partial"]["n_scored"] == 1 and rep["partial"]["n_registered"] == 2
    assert rep["partial"]["unscored"] == [B_ID] and rep["partial"]["closed_utc"].endswith("Z")
    with pytest.raises(RuntimeError, match="already complete"):
        driver.close_partial(cfg)
    # a scored set that is not a prefix of the registered order is refused
    rep["complete"] = False
    rep["scores"] = {B_ID: rep["scores"][C_ID]}
    (cfg.results_dir / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    with pytest.raises(RuntimeError, match="not a prefix"):
        driver.close_partial(cfg)


def test_native_e9_run_is_unchanged_by_the_0035_fields(env, tmp_path):
    """config/e9.toml's behaviour: no rope flag, no bridge, id order, no partial."""
    cfg, e7, calls, runner = env
    out = driver.run(cfg, e7, repo_root=tmp_path, runner=runner, encoder=words)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["bridge"] is None and rep["rope"] is None and rep["context_floor"] == 0 and rep["order_by"] == "id"
    assert rep["run_order"] == list(rep["scores"]) and rep["resumed_from"] is None
    assert all("--rope-scaling" not in c for c in calls)
    with pytest.raises(RuntimeError, match="does not register a partial close"):
        driver.close_partial(cfg)
