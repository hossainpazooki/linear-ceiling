"""The paired sub-call cell of the cache readout (config/cache-behavior-fab.toml): synthetic logs in the pinned
harness's layout through the adapter (tools/cache_behavior/fab_pairs.py), tiny-model CPU forwards through the
driver, and the earlier configs' paths unchanged."""
import gzip
import hashlib
import importlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

pytest.importorskip("transformers")
from transformers import Qwen3Config, Qwen3ForCausalLM

from linear_ceiling.e9_pertoken import token_mean
from linear_ceiling.rng import make_rng
from tests.test_fab_reuse import R, write_traj
from tools.cache_behavior import fab_pairs
from tools.cache_behavior import run as driver
from tools.cache_behavior.core import (deviation_means, matched, prefill, relocated_candidate, token_deviation)
from tools.cache_behavior.run import digest, summarize

FAB = driver.ROOT / "config" / "cache-behavior-fab.toml"
DOC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"          # 40 characters, one token each
TAU = 0.3186442653116294
# The 0069 driver's committed blobs (run.py, core.py), against which the earlier summary is compared byte for byte.
OLD_BLOBS = {"run.py": "a80fbc28a2d50ecca5c7ac0164aeffee4167cb4f", "core.py": "04fab278e7d1772b0b822d1523af59bdfcd4d5df"}
# One trajectory's sub-calls and what each B is against its A (A = the latest earlier carrier of B's keys).
TURNS = [[("parse", "d", DOC), R("Q: {{d}}")],        # S0 (turn 1, tool 1): all new
         [R("Q: {{d}}")],                              # S1: the same prompt as S0, all in the common prefix: PREFIX
         [R("Z: {{d}}")],                              # S2 against S1: same offsets, no common prefix: |M| = 40
         [R("Longer: {{d}}", ("d", 2, 30))],           # S3 against S2: moved by 3: |M| = 28, DIFFERENT-OFFSET
         [R("Q: {{d}}{{d}}")]]                         # S4 against S3: every shared key twice in B: none matched


@pytest.fixture
def model():
    torch.manual_seed(3)
    cfg = Qwen3Config(vocab_size=32, hidden_size=32, intermediate_size=48, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, head_dim=8,
                      max_position_embeddings=81920, attention_dropout=0,
                      rope_parameters={"rope_type": "yarn", "rope_theta": 1000000.0,
                                       "factor": 2.5, "original_max_position_embeddings": 32768})
    cfg._attn_implementation = "sdpa"
    return Qwen3ForCausalLM(cfg).eval()


def small(text):
    # One token per character, with ids inside the tiny model's vocabulary.
    return [ord(c) % 31 + 1 for c in text], [(i, i + 1) for i in range(len(text))]


def fab_cfg(**over):
    cfg = tomllib.loads(FAB.read_text(encoding="utf-8"))
    cfg.update(window_end="2026-01-01T00:00:00Z", min_matched_tokens=20, chunk_tokens=4, continuation_chunk=2,
               prefix_control_tokens=2)
    cfg.update(over)
    return cfg


def started(root, tid, k=1):
    # The wrapper creates <task id>-<k>.out (the harness's stdout) when launch k starts.
    (root / "runs").mkdir(exist_ok=True)
    (root / "runs" / f"{tid}-{k}.out").write_text("harness output, never opened by the adapter")


def launch(root, tid, qdir, k=1, end="2025-12-31T23:00:00Z", corrupt=False):
    # The wrapper's run record, written once when launch k ends: every log file's sha256 (a packed file under its
    # plain name, by its decompressed bytes), keyed relative to the run folder, and the launch's log directories.
    started(root, tid, k)
    files = {}
    for p in sorted(qdir.rglob("*.json*")):
        gz = p.suffix == ".gz"
        raw = gzip.decompress(p.read_bytes()) if gz else p.read_bytes()
        files[(p.with_name(p.name[:-3]) if gz else p).relative_to(root).as_posix()] = hashlib.sha256(raw).hexdigest()
    body = json.dumps({"start": "2025-12-31T22:00:00Z", "end": end, "wall_seconds": 3600, "exit": 0, "launch": k,
                       "files": files, "log_dirs": [qdir.relative_to(root).as_posix()]})
    (root / "runs").mkdir(exist_ok=True)
    (root / "runs" / f"{tid}-{k}.json").write_text(body[:len(body) // 2] if corrupt else body)


def run_tree(tmp_path):
    root = tmp_path / "run"
    stamp = "2025-12-31_22-00-00_{}".format
    qs = {tid: write_traj(root / "logs", tid, TURNS, stamp=stamp(tid * 2)[:32], gz_state=tid == "row02")
          for tid in ("row01", "row02", "row03", "row04")}
    qs["row05"] = write_traj(root / "logs", "row05", [], stamp=stamp("e"))          # a failed launch only
    launch(root, "row01", qs["row01"])
    launch(root, "row02", qs["row02"])
    launch(root, "row03", qs["row03"], end="2026-01-01T00:00:01Z")                # ended after the window
    launch(root, "row04", qs["row04"], corrupt=True)                              # record not yet whole
    launch(root, "row05", qs["row05"])
    launch(root, "row06", write_traj(root / "logs", "row06", [], stamp=stamp("f")))  # failed, then relaunched:
    started(root, "row06", 2)                                                     # launch 2 still running
    started(root, "row07")                                                        # its first launch running
    return root


def prepared(tmp_path, monkeypatch, **over):
    root = run_tree(tmp_path)
    monkeypatch.setattr(fab_pairs, "assert_registered", lambda *a: None)
    monkeypatch.setattr(fab_pairs, "reader_encoder", lambda path, sha: small)
    args = SimpleNamespace(inputs=tmp_path / "inputs", config=FAB, runs_root=root, tokenizer_json=tmp_path / "t")
    cfg = fab_cfg(**over)
    return fab_pairs.prepare(args, cfg, driver.ROOT, digest, driver.write), args.inputs, cfg, root


def test_synthetic_logs_through_the_adapter(tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    status = {k: v["status"] for k, v in man["questions"].items()}
    assert status["row01"] == status["row02"] == "measured" and status["row05"] == "no trajectory in its launch records"
    assert status["row03"] == status["row04"] == "outside the window"
    assert sum(v == "outside the window" for v in status.values()) == 2
    assert status["row06"] == status["row07"] == "a launch with no end record at the build"
    assert sum(v == "no launch record" for v in status.values()) == 20          # never started
    assert man["questions"]["row01"]["subcalls"] == 5 and man["questions"]["row01"]["b_subcalls"] == 4
    assert man["candidates"] == 8 and man["eligible"] == man["selected"] == 4
    assert man["exclusions"]["prefix"] == man["exclusions"]["repeated keys only"] == 2
    rec = {r["handoff"]: r for r in man["records"]}
    p = rec["row01/t002.000<t001.001"]
    assert (p["reason"], p["matched"], p["matched_in_common_prefix"], p["class"]) == ("prefix", 0, 40, None)
    s = rec["row02/t003.000<t002.000"]
    assert (s["class"], s["matched"], s["different_offset_share"], s["common_prefix_tokens"]) == ("same_offset", 40, 0, 0)
    assert (s["sender_tokens"], s["a_tokens"], s["matched_share_of_reused"]) == (43, 43, 1.0)    # cut capped at |A|
    d = rec["row01/t004.000<t003.000"]
    assert (d["class"], d["matched"], d["different_offset_share"], d["reused_document_tokens"]) == \
        ("different_offset", 28, 1.0, 28)
    assert (d["sender_tokens"], d["a_tokens"], d["receiver_tokens"], d["continuation_tokens"]) == (36, 43, 36, 2)
    q = rec["row01/t005.000<t004.000"]
    assert (q["reason"], q["repeated_key_tokens"], q["reused_document_tokens"]) == ("repeated keys only", 56, 80)
    # The registered order takes one pair from each trajectory before any trajectory's second.
    order = man["registered_order"]
    assert len(order) == 4 and {order[0][:5], order[1][:5]} == {"row01", "row02"}
    assert [r["handoff"] for r in man["records"] if not r["excluded"]] == order
    with np.load(inputs / d["file"]) as z:
        assert np.array_equal(z["sender"], small("Z: " + DOC)[0][:36])
        assert np.array_equal(z["receiver"], small("Longer: " + DOC[2:30])[0])
        assert np.array_equal(z["pairs"], np.column_stack((np.arange(2, 30) + 3, np.arange(2, 30) + 6)))
        assert np.array_equal(z["continuation"], small("ok")[0])
        fab_pairs.check_arrays(z, d)
    fab_pairs.check_manifest(man, cfg, FAB, driver.ROOT)
    assert "Longer" not in (inputs / "manifest.json").read_text() and man["files_read"] > 0
    fab_pairs.parse_stamp(man["built"])
    measured = [man["questions"][t] for t in ("row01", "row02")]
    assert man["reused_within_cap_0075"] == {"trajectories": 2, **{k: sum(q[k] for q in measured)
                                                                    for k in fab_pairs.WITHIN_CAP_0075}}
    assert all(q["ended_by_itself"] is True for q in measured)
    assert all(r["ended_by_itself"] is True for r in man["records"])
    with pytest.raises(ValueError, match="not the registered order's first pairs"):
        fab_pairs.check_manifest({**man, "registered_order": man["registered_order"][::-1]}, cfg, FAB, driver.ROOT)
    with np.load(inputs / d["file"]) as z:
        changed = {k: z[k].copy() for k in fab_pairs.ARRAYS}
    changed["sender"][0] += 1
    with pytest.raises(ValueError, match="input arrays differ from the manifest"):
        fab_pairs.check_arrays(changed, d)


@pytest.mark.parametrize("final", [False, True])
def test_without_its_final_record_the_last_turn_gives_no_pair_and_is_not_read(tmp_path, monkeypatch, final):
    # 0075 sets the last turn aside when the root result.json is absent; the walk must agree (its counts are
    # reproduced) and read none of that turn's records. final=True is the control: the same turn is then read.
    root = tmp_path / "run"
    q = write_traj(root / "logs", "row01", TURNS + [[R("Z: {{d}}")]], stamp="2025-12-31_22-00-00_" + "f" * 10,
                   final=final)
    launch(root, "row01", q)
    monkeypatch.setattr(fab_pairs, "assert_registered", lambda *a: None)
    monkeypatch.setattr(fab_pairs, "reader_encoder", lambda path, sha: small)
    args = SimpleNamespace(inputs=tmp_path / "inputs", config=FAB, runs_root=root, tokenizer_json=tmp_path / "t")
    man = fab_pairs.prepare(args, fab_cfg(), driver.ROOT, digest, driver.write)
    late = [r["handoff"] for r in man["records"] if "/t006." in r["handoff"]]
    assert man["questions"]["row01"]["subcalls"] == (6 if final else 5)
    assert bool(late) == final
    files = json.loads((args.inputs / "manifest.json").read_text())["files_read"]
    assert {r["ended_by_itself"] for r in man["records"]} == {final}      # 0075's value for the trajectory
    turn6 = sum(1 for p in q.rglob("*.json*") if "turn_006" in p.as_posix())
    assert turn6 > 0 and files == len(list(q.rglob("*.json*"))) - (0 if final else turn6) - 1     # history of init


def test_the_floor_the_cap_and_the_ceiling_exclude_and_count(tmp_path, monkeypatch):
    man = prepared(tmp_path / "a", monkeypatch, min_matched_tokens=30)[0]
    assert man["exclusions"]["below the matched-token floor"] == 2 and man["selected"] == 2
    man = prepared(tmp_path / "b", monkeypatch, context_cap=40)[0]
    assert man["exclusions"]["over the cap"] == 2 and man["over_the_cap_matched_share"] == 80 / 136
    man, _, cfg, _ = prepared(tmp_path / "c", monkeypatch, max_pairs=1)
    assert man["exclusions"]["beyond the ceiling"] == 3 and man["selected"] == 1
    fab_pairs.check_manifest(man, cfg, FAB, driver.ROOT)
    with pytest.raises(ValueError, match="exceed the ceiling"):
        fab_pairs.check_manifest({**man, "selected": 1}, {**cfg, "max_pairs": 0}, FAB, driver.ROOT)


def two_subcalls(n, a_len=1000, b_len=None, response="ok"):
    # A carries n document keys at 0..n-1, B the same keys one place later; their ids differ at index 0, so no
    # common prefix: M is all n tokens, DIFFERENT-OFFSET.
    keys = [("sha", i, i + 1, 7) for i in range(n)]
    a = {"turn": 1, "tool": 0, "ids": np.full(a_len, 1, dtype=np.int64), "doc": list(enumerate(keys)),
         "response": "x", "reused": 0}
    b = {"turn": 2, "tool": 0, "ids": np.full(b_len or n + 1, 2, dtype=np.int64),
         "doc": [(i + 1, k) for i, k in enumerate(keys)], "response": response, "reused": n}
    return [a, b]


def test_each_exclusion_at_its_boundary():
    cfg = fab_cfg(min_matched_tokens=64, chunk_tokens=256, context_cap=81920)

    def pair(n, **over):
        a_len, b_len, response = over.pop("a_len", 1000), over.pop("b_len", None), over.pop("response", "ok")
        return fab_pairs.candidate_pairs("row01", two_subcalls(n, a_len, b_len, response), small, {**cfg, **over})[0]
    assert pair(63)["reason"] == "below the matched-token floor" and pair(64)["reason"] is None
    assert pair(64, response=None)["reason"] == "no logged response"
    assert pair(64, response="x")["reason"] == "fewer than two continuation tokens"
    long = pair(64, response="y" * 300)                          # the continuation is B's response's first 256
    assert long["reason"] is None and long["continuation_tokens"] == 256 and len(long["_arrays"]["continuation"]) == 256
    # A's cut: the last matched token is at 63, so A is prefilled through 256, its first chunk boundary.
    assert pair(64)["sender_tokens"] == fab_pairs.a_cut(63, 1000, 256) == 256 and pair(64, a_len=100)["sender_tokens"] == 100
    assert pair(64, context_cap=256)["reason"] is None and pair(64, context_cap=255)["reason"] == "over the cap"
    assert pair(64, b_len=299, context_cap=300)["reason"] is None              # |B| + |C| - 1 = 300
    assert pair(64, b_len=300, context_cap=300)["reason"] == "over the cap"
    memory = {"host_fixed_GiB": 0, "host_bytes_per_matched_token": 2**30}      # one GiB per matched token
    assert pair(64, host_memory_limit_GiB=64, **memory)["reason"] is None
    over = pair(64, host_memory_limit_GiB=63, **memory)
    assert over["reason"] == "over host memory" and over["predicted_host_GiB"] == 64 and "_arrays" not in over
    assert pair(64, host_memory_limit_GiB=63, context_cap=255, **memory)["reason"] == "over the cap"   # the first applies


def test_the_registered_order_is_seeded_round_robin():
    eligible = {t: [{"handoff": f"{t}/{b}", "b": [b, 0]} for b in range(1, n + 1)]
                for t, n in (("row03", 3), ("row01", 2), ("row02", 1))}
    order = [r["handoff"] for r in fab_pairs.registered_order(eligible, 20261001)]
    assert order == [r["handoff"] for r in fab_pairs.registered_order(eligible, 20261001)]
    assert order == ["row03/3", "row02/1", "row01/1", "row03/2", "row01/2", "row03/1"]
    assert len({h[:5] for h in order[:3]}) == 3 and sorted(order) == sorted(r["handoff"] for v in eligible.values() for r in v)
    assert order != [r["handoff"] for r in fab_pairs.registered_order(eligible, 20261002)]


def test_two_trajectories_for_one_question_refuse(tmp_path, monkeypatch):
    root = tmp_path / "run"
    q1 = write_traj(root / "logs", "row01", TURNS, stamp="2025-12-31_22-00-00_" + "a" * 10)
    q2 = write_traj(root / "logs", "row01", TURNS, stamp="2025-12-31_22-00-00_" + "b" * 10)
    launch(root, "row01", q1)
    launch(root, "row01", q2, k=2)
    monkeypatch.setattr(fab_pairs, "assert_registered", lambda *a: None)
    monkeypatch.setattr(fab_pairs, "reader_encoder", lambda path, sha: small)
    args = SimpleNamespace(inputs=tmp_path / "inputs", config=FAB, runs_root=root, tokenizer_json=tmp_path / "t")
    with pytest.raises(ValueError, match="more than one trajectory"):
        fab_pairs.prepare(args, fab_cfg(), driver.ROOT, digest, driver.write)


def test_the_adapter_refuses(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="built after it"):
        prepared(tmp_path / "a", monkeypatch, window_end="2099-01-01T00:00:00Z")
    _, inputs, cfg, root = prepared(tmp_path / "b", monkeypatch)
    args = SimpleNamespace(inputs=inputs, config=FAB, runs_root=root, tokenizer_json=root)
    with pytest.raises(ValueError, match="already exists"):
        fab_pairs.prepare(args, cfg, driver.ROOT, digest, driver.write)
    record = root / "runs" / "row01-1.json"
    body = json.loads(record.read_text())
    key = next(k for k in body["files"] if k.endswith("turn_003/state.json"))
    body["files"][key] = "0" * 64
    record.write_text(json.dumps(body))
    args.inputs = tmp_path / "b" / "again"
    with pytest.raises(ValueError, match="differ from the launch record"):
        fab_pairs.prepare(args, cfg, driver.ROOT, digest, driver.write)
    real = fab_pairs.measure_trajectory
    monkeypatch.setattr(fab_pairs, "measure_trajectory",
                        lambda *a, **k: {**real(*a, **k), "same_offset": real(*a, **k)["same_offset"] + 1})
    with pytest.raises(ValueError, match="0075's count"):
        prepared(tmp_path / "c", monkeypatch)


def test_the_gate_reads_the_committed_ledger():
    fab_pairs.assert_registered(driver.ROOT, ["0047"])
    with pytest.raises(RuntimeError, match="no entry 9999"):
        fab_pairs.assert_registered(driver.ROOT, ["9999"])


def test_prepare_refuses_until_the_ledger_holds_0076_and_0077(tmp_path, monkeypatch):
    # The registered gate: no pair is built before 0076 itself is committed, so a ledger with 0075 alone refuses; nor
    # before 0077, which amends 0076's window end, so a ledger with 0075 and 0076 refuses too.
    def ledger(text):
        shown = subprocess.CompletedProcess(["git"], 0, stdout=text, stderr="")
        monkeypatch.setattr(fab_pairs, "subprocess", SimpleNamespace(run=lambda *a, **k: shown))
    args = SimpleNamespace(inputs=tmp_path / "inputs", config=FAB, runs_root=tmp_path, tokenizer_json=tmp_path / "t")
    ledger("### 0075 — the reuse opportunity\n")
    with pytest.raises(RuntimeError, match="no entry 0076"):
        fab_pairs.prepare(args, fab_cfg(), driver.ROOT, digest, driver.write)
    ledger("### 0075 — the reuse opportunity\n### 0076 — this cell\n")
    with pytest.raises(RuntimeError, match="no entry 0077"):
        fab_pairs.prepare(args, fab_cfg(), driver.ROOT, digest, driver.write)
    assert not args.inputs.exists()
    ledger("### 0075 — the reuse opportunity\n### 0076 — this cell\n### 0077 — its window end\n")
    fab_pairs.assert_registered(driver.ROOT, fab_cfg()["gate"]["prepare_entries"])


def test_the_a_cut_leaves_every_matched_state_bit_identical(model):
    tokens = make_rng(7).integers(1, 32, 23)
    chunk = 4
    for positions in ([2, 5, 9], [0, 21, 22], [11]):
        cut = fab_pairs.a_cut(max(positions), len(tokens), chunk)
        assert (cut % chunk == 0 or cut == len(tokens)) and cut > max(positions)
        full = matched(prefill(model, tokens, chunk), positions)
        part = matched(prefill(model, tokens[:cut], chunk), positions)
        for (k0, v0), (k1, v1) in zip(full, part, strict=True):
            assert torch.equal(k0, k1) and torch.equal(v0, v1)


def test_the_per_token_deviation_averages_to_deviation_means_k(model):
    g = torch.Generator().manual_seed(11)
    n = 9
    pairs = np.column_stack((np.arange(3, 3 + n), np.arange(20, 20 + n)))
    fresh = [(torch.randn(1, 2, n, 8, generator=g), torch.randn(1, 2, n, 8, generator=g)) for _ in range(2)]
    reused = [(k + 0.3 * torch.randn(k.shape, generator=g), v + 0.1) for k, v in fresh]
    freq = model.model.rotary_emb.inv_freq
    delta = token_deviation(fresh, reused, pairs, freq)
    assert delta.shape == (n, 2, 2) and delta.dtype == np.float64
    means = deviation_means(fresh, reused, pairs, freq)
    per_token = token_mean(delta)
    assert abs(per_token.mean() - means["K"]) <= 1e-12 * means["K"]
    got = fab_pairs.removal(per_token, means, TAU)
    assert got["matched"] == n and got["tokens_over_tau_K"] == int((per_token > TAU).sum())
    assert got["max_token_mean_K"] == per_token.max() and 0 <= got["f_star_K"] <= 1
    with pytest.raises(ValueError, match="differs from deviation_means"):
        fab_pairs.removal(per_token, {**means, "K": means["K"] * (1 + 1e-6)}, TAU)


def _cpu(monkeypatch, model):
    # Real tiny-model CPU forwards; only CUDA plumbing is replaced (as test_cache_behavior does).
    monkeypatch.setattr(model, "to", lambda device: model)
    monkeypatch.setattr(driver.AutoConfig, "from_pretrained", lambda *a, **k: model.config)
    monkeypatch.setattr(driver.AutoModelForCausalLM, "from_pretrained", lambda *a, **k: model)
    monkeypatch.setattr(torch.cuda, "get_device_name", lambda device: "CPU test")
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda device: 0)
    for name in ("empty_cache", "reset_peak_memory_stats"):
        monkeypatch.setattr(torch.cuda, name, lambda *a: None)
    monkeypatch.setattr(torch, "use_deterministic_algorithms", lambda enabled: None)
    monkeypatch.setattr(driver, "sync", lambda device: None)


def _args(inputs, output, **over):
    return SimpleNamespace(**{"device": "cuda", "inputs": inputs, "output": output, "config": FAB, "resume": False,
                              "probe": False, "stop_at": "2099-01-01T00:00:00Z", "cross_check_inputs": None,
                              "no_cross_check": True, **over})


def test_end_to_end_on_the_tiny_model(model, tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    _cpu(monkeypatch, model)
    args = _args(inputs, tmp_path / "out")
    driver.run(args, cfg, man)
    report_path = args.output / "report.json"
    first = report_path.read_bytes()
    report = json.loads(first)
    assert report["complete"] and len(report["scores"]) == 4 and report["attention_queries"] == 0
    assert report["cross_check"] == {"branch": "not staged", "label": "not cross-checked per token", "result": None}
    probe = report["run_order"][0]
    assert probe.split("/")[1] == "t003.000<t002.000"           # the largest by max(|A_cut|, |B| + |C| - 1)
    assert [h for h, s in report["scores"].items() if s["probe"]] == [probe]
    assert report["run_order"][1:] == [h for h in man["registered_order"] if h != probe]
    controls = report["scores"][probe]["controls"]
    assert controls["fresh_repeat"]["max_logit_error"] == 0 and controls["prefix_copy"]["max_logit_error"] <= 5e-4
    for hid, score in report["scores"].items():
        assert set(score["arms"]) == {"reuse", "random", "scrambled"} and "archive_bridge_mean" not in score
        removal = score["removal"]
        assert removal["matched"] == next(r["matched"] for r in man["records"] if r["handoff"] == hid)
        assert score["continuation_tokens"] == 2 and score["scored_continuation_tokens"] == 1
        with np.load(args.output / score["file"]) as z:
            assert "continuation" not in z.files and "attention" not in z.files
            assert abs(z["token_mean_K"].mean() - removal["deviation_means"]["K"]) <= 1e-9 * removal["deviation_means"]["K"]
    body = summarize(args.output, inputs)
    assert body["attention"] == "not computed: attention_queries = 0"
    fab = body["fab"]
    assert (fab["read"], fab["not_read"], fab["all"]["pairs"], fab["all"]["trajectories"]) == (4, [], 4, 2)
    # Every field the summary writes is in the lists the registering entry is held to, and no other.
    assert tuple(fab) == fab_pairs.FAB_FIELDS
    assert all(tuple(fab[c]) == fab_pairs.BLOCK_FIELDS for c in ("all", *fab_pairs.CLASSES))
    assert all(tuple(fab["all"][lv]) == fab_pairs.PAIR_STATS for lv in ("pair_level", "trajectory_level"))
    assert all(tuple(x) == fab_pairs.PER_PAIR_FIELDS for x in fab["per_pair"])
    meta = {r["handoff"]: r for r in man["records"]}
    assert all(x[k] == meta[x["handoff"]][k] for x in fab["per_pair"] for k in fab_pairs.PAIR_RECORD_FIELDS)
    assert fab["built"] == man["built"] and fab["ended_in_flight"] == [] and fab["reused_within_cap_0075"]["trajectories"] == 2
    assert fab["questions"]["measured"] == ["row01", "row02"] and fab["questions"]["outside the window"] == ["row03", "row04"]
    assert fab["excluded"]["prefix"] == [r["handoff"] for r in man["records"] if r["reason"] == "prefix"]
    assert fab["same_offset"]["pairs"] == fab["different_offset"]["pairs"] == 2
    assert fab["cross_check_label"] == "not cross-checked per token" and fab["probe_pair"] == probe
    assert set(fab["all"]["trajectory_level"]) == set(fab["all"]["pair_level"]) >= {"f_star_K", "reuse_mean_kl"}
    args.resume = True
    driver.run(args, cfg, man)
    assert report_path.read_bytes() == first
    for change in ({"stop_at": "2099-01-02T00:00:00Z"}, {"no_cross_check": False, "cross_check_inputs": tmp_path}):
        with pytest.raises(ValueError, match="keeps the first launch"):
            driver.run(_args(inputs, args.output, resume=True, **change), cfg, man)


def test_the_first_launch_fixes_the_stop_and_a_past_stop_reads_nothing(model, tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    for missing in ({"stop_at": None}, {"no_cross_check": False}, {"cross_check_inputs": tmp_path}):
        with pytest.raises(ValueError, match="first launch fixes"):
            driver.run(_args(inputs, tmp_path / "out", **missing), cfg, man)
    _cpu(monkeypatch, model)
    args = _args(inputs, tmp_path / "out", stop_at="2000-01-01T00:00:00Z")
    driver.run(args, cfg, man)
    report = json.loads((args.output / "report.json").read_text())
    assert report["scores"] == {} and report["stopped"]["read"] == 0 and not report["complete"]
    written = json.loads((args.output / "summary.json").read_text())        # the driver's own, written on the stop
    assert written["fab"]["stopped"] == report["stopped"] and written["scored"] == 0
    fab = summarize(args.output, inputs)["fab"]
    assert (fab["read"], fab["not_read"], fab["all"]) == (0, report["run_order"], None) and len(fab["not_read"]) == 4


def test_a_stop_after_the_probe_leaves_a_summary_that_records_it(model, tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    _cpu(monkeypatch, model)
    args = _args(inputs, tmp_path / "out", probe=True)
    driver.run(args, cfg, man)                                  # the probe pair alone; the stop is still ahead

    class Later(driver.datetime):
        @classmethod
        def now(cls, tz=None):
            return driver.datetime(2099, 1, 1, 0, 0, 1, tzinfo=tz)
    monkeypatch.setattr(driver, "datetime", Later)              # the resume starts after the stop time
    driver.run(_args(inputs, args.output, resume=True), cfg, man)
    report = json.loads((args.output / "report.json").read_text())
    written = json.loads((args.output / "summary.json").read_text())
    assert report["stopped"]["read"] == 1 and len(report["scores"]) == 1 and not report["complete"]
    assert written["fab"]["stopped"] == report["stopped"] and written["fab"]["read"] == 1
    assert written == json.loads(json.dumps(summarize(args.output, inputs)))


def test_one_reading_per_manifest(model, tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    _cpu(monkeypatch, model)
    args = _args(inputs, tmp_path / "out", probe=True)
    driver.run(args, cfg, man)
    lock = json.loads((inputs / "launch.json").read_text())
    assert (lock["stop_at"], lock["branch"]) == ("2099-01-01T00:00:00Z", "not staged")
    assert lock["manifest_sha256"] == digest(inputs / "manifest.json")
    for change in ({}, {"stop_at": "2099-01-02T00:00:00Z"}):   # a new output folder, with the same stop or another
        with pytest.raises(ValueError, match="launched before"):
            driver.run(_args(inputs, tmp_path / "elsewhere", **change), cfg, man)
    assert not (tmp_path / "elsewhere" / "report.json").exists()
    (inputs / "launch.json").write_text(json.dumps({**lock, "stop_at": "2099-01-03T00:00:00Z"}))
    with pytest.raises(ValueError, match="differs from the manifest's launch.json"):
        driver.run(_args(inputs, args.output, resume=True), cfg, man)
    (inputs / "launch.json").unlink()
    with pytest.raises(ValueError, match="no launch.json"):
        driver.run(_args(inputs, args.output, resume=True), cfg, man)


def test_a_step_that_did_not_finish_is_named(model, tmp_path, monkeypatch):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    _cpu(monkeypatch, model)
    real = driver.continuation_logits

    def killed(*a):
        raise MemoryError("a stand-in for the process ending during the probe pair")
    monkeypatch.setattr(driver, "continuation_logits", killed)
    args = _args(inputs, tmp_path / "out", probe=True)
    with pytest.raises(MemoryError):
        driver.run(args, cfg, man)
    report = json.loads((args.output / "report.json").read_text())
    probe = report["run_order"][0]
    assert report["in_flight"]["step"] == probe and report["scores"] == {} and report["ended_in_flight"] == []
    assert summarize(args.output, inputs)["fab"]["ended_in_flight"] == [report["in_flight"]]
    monkeypatch.setattr(driver, "continuation_logits", real)
    driver.run(_args(inputs, args.output, resume=True, probe=True), cfg, man)
    report = json.loads((args.output / "report.json").read_text())
    assert "in_flight" not in report and [e["step"] for e in report["ended_in_flight"]] == [probe]
    assert set(report["ended_in_flight"][0]) == {"step", "started", "found"} and list(report["scores"]) == [probe]
    assert summarize(args.output, inputs)["fab"]["ended_in_flight"] == report["ended_in_flight"]


def test_a_fresh_repeat_that_is_not_exact_stops_every_config(model, tmp_path, monkeypatch):
    # 0074: any nonzero fresh-repeat error stops the run, under every config; 1e-6 passes the 0.0005 control bound.
    _cpu(monkeypatch, model)
    real, calls = driver.continuation_logits, []

    def nudged(*a):
        calls.append(1)
        out = real(*a)
        return out + 1e-6 if len(calls) == 2 else out          # the second call is the repeat on the probe
    monkeypatch.setattr(driver, "continuation_logits", nudged)
    cfg = tomllib.loads((driver.ROOT / "config/cache-behavior.toml").read_text())
    cfg.update(chunk_tokens=2, continuation_chunk=2, attention_queries=2, attention_query_chunk=1,
               prefix_control_tokens=2)
    old = tmp_path / "old-inputs"
    old.mkdir()
    tokens = np.arange(1, 9)
    np.savez(old / "h.npz", sender=tokens, receiver=tokens, pairs=np.column_stack((np.arange(8),) * 2),
             continuation=np.array([21, 22, 23]), delta_K=np.zeros((8, 2, 2), dtype=np.float32),
             tail_K=np.zeros(8, dtype=bool))
    manifest = {"records": [{"handoff": "h", "file": "h.npz", "sender_tokens": 8, "excluded": False,
                             "archived_mean": {"K": 0, "V": 0}}]}
    (old / "manifest.json").write_text(json.dumps(manifest))
    args = SimpleNamespace(device="cuda", inputs=old, output=tmp_path / "old-out", resume=False, probe=True,
                           config=driver.ROOT / "config/cache-behavior.toml")
    with pytest.raises(ValueError, match="fresh repeat is not exact"):
        driver.run(args, cfg, manifest)
    calls.clear()
    man, inputs, fcfg, _ = prepared(tmp_path / "fab", monkeypatch)
    with pytest.raises(ValueError, match="fresh repeat is not exact"):
        driver.run(_args(inputs, tmp_path / "fab-out", probe=True), fcfg, man)


def cross_inputs(folder, model, shift):
    # A stand-in for 0049's prepared probe handoff: its archived delta_K is this arithmetic's, plus `shift`.
    folder.mkdir()
    sender = make_rng(3).integers(1, 32, 30)
    receiver = sender[4:20].copy()
    pairs = np.column_stack((np.arange(4, 20), np.arange(16)))
    freq = model.model.rotary_emb.inv_freq.detach()
    fresh = matched(prefill(model, receiver, 4), pairs[:, 1])
    reused = relocated_candidate(matched(prefill(model, sender, 4), pairs[:, 0]), pairs, freq)
    delta = token_deviation(fresh, reused, pairs, freq) + shift
    np.savez(folder / "probe.npz", sender=sender, receiver=receiver, pairs=pairs, continuation=np.array([1, 2]),
             delta_K=delta.astype(np.float32), tail_K=token_mean(delta) > TAU)
    (folder / "manifest.json").write_text(json.dumps({"records": [
        {"handoff": "probe#1", "file": "probe.npz", "sha256": digest(folder / "probe.npz"),
         "archived_mean": {"K": float(token_mean(delta).mean()), "V": 0.0}}]}))
    return {"handoff": "probe#1", "manifest_sha256": digest(folder / "manifest.json"),
            "file_sha256": digest(folder / "probe.npz")}


@pytest.mark.parametrize("shift, passed", [(0.0, True), (1.0, False)])
def test_the_cross_instrument_control_runs_before_any_pair_and_a_failure_stops_the_run(model, tmp_path, monkeypatch,
                                                                                       shift, passed):
    man, inputs, cfg, _ = prepared(tmp_path, monkeypatch)
    _cpu(monkeypatch, model)
    cfg["cross_check"] = cross_inputs(tmp_path / "e9", model, shift)
    args = _args(inputs, tmp_path / "out", no_cross_check=False, cross_check_inputs=tmp_path / "e9", probe=True)
    if passed:
        driver.run(args, cfg, man)
    else:
        with pytest.raises(ValueError, match="failed; no pair is read"):
            driver.run(args, cfg, man)
    report = json.loads((args.output / "report.json").read_text())
    result = report["cross_check"]["result"]
    assert result["passed"] is passed and report["cross_check"]["branch"] == "run"
    assert tuple(report["cross_check"]) == ("branch", "label", "result") and tuple(result) == fab_pairs.CROSS_CHECK_FIELDS
    assert result["tokens_outside_tolerance"] == (0 if passed else 16) and result["matched"] == 16
    assert len(report["scores"]) == (1 if passed else 0)
    if passed:
        assert report["cross_check"]["label"] == "checked per token against the E9-long archive on one handoff"
    else:
        with pytest.raises(ValueError, match="failed; no pair is read"):
            driver.run(_args(inputs, args.output, resume=True, no_cross_check=False, cross_check_inputs=None,
                             probe=True), cfg, man)
        with pytest.raises(ValueError, match="launched before"):     # a failed control ends this reading
            driver.run(_args(inputs, tmp_path / "again", probe=True), cfg, man)
    assert "in_flight" not in report and report["ended_in_flight"] == []


def test_the_cross_check_compares_per_token_and_f_star_within_one_token():
    archive = np.array([0.1, 0.2, 0.5, 0.05])
    ok = fab_pairs.cross_check_compare(archive + 0.0005, archive, {"tau_K": TAU, "bridge_absolute_tolerance": 0.001,
                                                                    "bridge_relative_tolerance": 0.01})
    assert ok["passed"] and ok["tokens_outside_tolerance"] == 0 and ok["tokens_over_tau_K_archive"] == 1
    bad = archive.copy()
    bad[1] += 0.004                                        # bound there is 0.001 + 0.002
    out = fab_pairs.cross_check_compare(bad, archive, {"tau_K": TAU, "bridge_absolute_tolerance": 0.001,
                                                       "bridge_relative_tolerance": 0.01})
    assert not out["passed"] and out["tokens_outside_tolerance"] == 1


def _old_driver(tmp_path):
    pkg = tmp_path / "old" / "cache_behavior_0069"
    pkg.mkdir(parents=True)
    for name, blob in OLD_BLOBS.items():
        shown = subprocess.run(["git", "cat-file", "blob", blob], cwd=driver.ROOT, capture_output=True)
        if shown.returncode:
            pytest.skip("the 0069 driver's blobs are not in this clone")
        (pkg / name).write_bytes(shown.stdout)
    (pkg / "__init__.py").write_text("")
    sys.path.insert(0, str(pkg.parent))
    try:
        return importlib.import_module("cache_behavior_0069.run")
    finally:
        sys.path.remove(str(pkg.parent))


def _old_output(folder):
    folder.mkdir(parents=True)
    rng = make_rng(5)
    scores, records = {}, []
    for index, hid in enumerate(("big", "small")):
        payload = {"continuation": np.array([2, 3, 4]), "attention": rng.random((2, 3, 4, 3)),
                   "receiver_query_positions": np.arange(3)}
        for arm in ("reuse", "random", "scrambled"):
            payload[f"{arm}_kl"] = rng.random(2)
            payload[f"{arm}_top1_agrees"] = np.array([True, index == 0])
        if index == 0:
            payload.update(fresh_witness=rng.random((2, 5)), witness_continuation_indices=np.array([1, 2]))
            for arm in ("reuse", "random", "scrambled"):
                payload[f"{arm}_witness"] = payload["fresh_witness"] + 0.0
                payload[f"{arm}_kl"] = np.zeros(2)
                payload[f"{arm}_top1_agrees"] = np.ones(2, dtype=bool)
        np.savez(folder / f"{hid}.npz", **payload)
        scores[hid] = {"file": f"{hid}.npz", "sha256": digest(folder / f"{hid}.npz"),
                       "arms": {a: {} for a in ("reuse", "random", "scrambled")}, "scored_continuation_tokens": 2,
                       "witness_count": 2 if index == 0 else 0}
        records.append({"handoff": hid, "sender_tokens": 10 - index, "excluded": False})
    records.append({"handoff": "short", "sender_tokens": 99, "excluded": True})
    inputs = folder / "inputs"
    inputs.mkdir()
    (inputs / "manifest.json").write_text(json.dumps({"records": records}))
    (folder / "report.json").write_text(json.dumps({
        "scores": scores, "complete": True, "run_order": ["big", "small"], "excluded": [records[-1]],
        "identity": {"manifest_sha256": digest(inputs / "manifest.json")}}))
    return inputs


def test_an_earlier_runs_summary_is_byte_identical(tmp_path):
    old = _old_driver(tmp_path)
    for name, mod in (("by-new", driver), ("by-0069", old)):
        inputs = _old_output(tmp_path / name)
        mod.summarize(tmp_path / name, inputs)
    assert (tmp_path / "by-new" / "summary.json").read_bytes() == (tmp_path / "by-0069" / "summary.json").read_bytes()
    assert json.loads((tmp_path / "by-new" / "summary.json").read_text())["attention"]


@pytest.mark.parametrize("name", ["cache-behavior.toml", "cache-behavior-repair.toml"])
def test_the_earlier_configs_still_pass_check(name, tmp_path, monkeypatch):
    path = driver.ROOT / "config" / name
    cfg = tomllib.loads(path.read_text())
    assert not driver.is_fab(cfg)
    monkeypatch.setattr(driver.transformers, "__version__", cfg["transformers"])
    monkeypatch.setattr(driver.torch, "__version__", cfg["torch"])
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    records = []
    for i in range(cfg["expected_handoffs"]):
        tokens = np.arange(1, 6) + i
        np.savez(inputs / f"h{i}.npz", sender=tokens, receiver=tokens, pairs=np.column_stack((np.arange(5),) * 2),
                 continuation=np.array([1, 2, 3]), delta_K=np.zeros((5, 2, 2)), tail_K=np.zeros(5, dtype=bool))
        records.append({"handoff": f"h{i}", "file": f"h{i}.npz", "sha256": digest(inputs / f"h{i}.npz"),
                        "sender_tokens": 5, "excluded": False})
    manifest = {"config_sha256": digest(path), "corpus_manifest_sha256": digest(driver.ROOT / "config/e7-manifest.json"),
                "archive_config_sha256": digest(driver.ROOT / "config/e9l.toml"), "records": records}
    (inputs / "manifest.json").write_text(json.dumps(manifest))
    args = SimpleNamespace(inputs=inputs, config=path)
    assert driver.check(args, cfg) == manifest
    long = np.arange(cfg["context_cap"] + 1) % 30 + 1                 # the length guard holds for every config
    np.savez(inputs / "h0.npz", sender=long, receiver=long[:5], pairs=np.column_stack((np.arange(5),) * 2),
             continuation=np.array([1, 2, 3]), delta_K=np.zeros((5, 2, 2)), tail_K=np.zeros(5, dtype=bool))
    records[0]["sha256"] = digest(inputs / "h0.npz")
    (inputs / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="exceed the registered context cap"):
        driver.check(args, cfg)


def test_the_registered_config():
    fab = tomllib.loads(FAB.read_text(encoding="utf-8"))
    base = tomllib.loads((driver.ROOT / "config" / "cache-behavior.toml").read_text(encoding="utf-8"))
    assert driver.is_fab(fab) and fab["cell"] == fab_pairs.CELL
    assert (fab["window_end"], fab["min_matched_tokens"], fab["max_pairs"], fab["attention_queries"]) == \
        ("2026-11-20T06:30:00Z", 64, 60, 0)                            # 0077 moved the window end from 12:00:00Z
    for key in ("model", "revision", "transformers", "torch", "seed", "context_cap", "chunk_tokens",
                "continuation_tokens", "continuation_chunk", "prefix_control_tokens", "control_max_logit_error",
                "bridge_absolute_tolerance", "bridge_relative_tolerance", "tau_K", "rope"):
        assert fab[key] == base[key], key
    assert fab["oracle_fractions"] == [] and "random_control_fractions" not in fab
    assert fab["gate"] == {"prepare_entries": ["0075", "0076", "0077"], "run_entries": ["0075", "0076", "0077"]}
    assert fab["cross_check"]["handoff"] == "20241016_composio_swekit/django__django-11087_traj#152"
    assert fab["host_bytes_per_matched_token"] == 4 * 28 * 8 * 128 * 2 * 4          # Qwen3-1.7B's K and V, float32
    assert (fab["host_memory_limit_GiB"], fab["host_fixed_GiB"]) == (88, 12)
    assert fab_pairs.host_gib(fab["context_cap"], fab) <= fab["host_memory_limit_GiB"]  # |M| < the cap
