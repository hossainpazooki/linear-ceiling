import hashlib
import json
from pathlib import Path

import pytest

from tools.runpod import pull_verify_b as pull_b
from tools.runpod import rp


def _write(path: Path, data: bytes = b"x") -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _fixture(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    local = tmp_path / "mirror"
    config = tmp_path / "e9f.toml"
    config.write_text(
        '[e9]\n'
        f'pair = "{pull_b.PAIR}"\n'
        'results_dir = "results/e9f"\n'
        'upstream_sha = "upstream-pin"\n'
        # entry 0042 registers the stopping rule for this cell; the fixture must mirror it or the
        # tests below assert behaviour the real config can never produce.
        '[e9.order]\n'
        'by = "n_sender_asc"\n'
        'allow_partial = true\n',
        encoding="utf-8",
    )
    score_sha = _write(local / "scores" / "h.json", b"score")
    tokens_sha = _write(local / "tokens" / "h.tokens.npz", b"tokens")
    kept_sha = _write(local / "scratch" / "h" / "same_src" / "meta.json", b"kept")
    pair_sha = _write(local / "controls" / "identity_pairs.npz", b"pairs")
    controls = {}
    for name in ("identity", "prefix", "null"):
        cs = _write(local / "controls" / f"{name}.json", f"{name}-score".encode())
        ct = _write(local / "controls" / f"{name}.tokens.npz", f"{name}-tokens".encode())
        controls[name] = {
            "score_file": f"{name}.json", "score_sha256": cs,
            "tokens_file": f"{name}.tokens.npz", "tokens_sha256": ct,
            "pairs_file": "identity_pairs.npz", "pairs_sha256": pair_sha,
        }
    _write(local / "align" / "coverage.json", b"coverage")
    _write(local / "align" / "h.json", b"alignment")
    _write(local / "align" / "h.npz", b"alignment-array")
    report = {
        "config_sha256": pull_b.text_sha256(config),
        "upstream_sha": "upstream-pin",
        "pair": pull_b.PAIR,
        "coverage": {"observed": 1, "included": 1, "excluded": 0},
        "alignments": [{"handoff_id": "h", "excluded": False}],
        "run_order": ["h"],
        "order_by": "n_sender_asc",   # entry 0042's registered order
        "keep_subset": ["h"],
        "bridge": None,
        "controls": {"handoff_id": "h", **controls},
        "scores": {
            "h": {
                "score_file": "h.json", "score_sha256": score_sha,
                "tokens_file": "h.tokens.npz", "tokens_sha256": tokens_sha,
                "kept_dir": "scratch/h",
                "kept_dumps": {"same_src": {"meta.json": kept_sha}},
            }
        },
        "complete": True,
    }
    (local / "report.json").write_text(json.dumps(report), encoding="utf-8")
    return local, config, report


def test_complete_report_and_final_manifest_cover_every_required_byte(tmp_path):
    local, config, report = _fixture(tmp_path)
    required = pull_b.validate_complete_report(report, config=config, exp="e9f", pair=pull_b.PAIR)
    artifacts = pull_b.report_artifacts(report)
    bad, checked, _ = pull_b.verify_artifacts(local, artifacts)
    assert not bad and checked == len(artifacts)

    logs = local / "logs" / "box"
    log_bodies = {
        "sitting_b.setup.log": b"setup\n",
        "sitting_b.probe.log": b"probe\n",
        "e9f.log": b"driver\nSITTING_B_OK\n",
        "e9f.rc": b"EXIT=0\n",
        "e9f.status": b"SITTING_B_OK\n",
        "sitting_b.launches.log": b"launch\n",
    }
    for name, body in log_bodies.items():
        _write(logs / name, body)
    entries = {}
    for path in sorted(p for p in local.rglob("*") if p.is_file()
                       and "scratch" not in p.relative_to(local).parts
                       and "logs" not in p.relative_to(local).parts):
        rel = path.relative_to(local).as_posix()
        entries[f"linear-ceiling/results/e9f/{rel}"] = pull_b.sha256(path)
    for name in log_bodies:
        entries[name] = pull_b.sha256(logs / name)
    manifest = logs / "e9f.final.sha256"
    manifest.write_text("".join(f"{digest}  {rel}\n" for rel, digest in sorted(entries.items())),
                        encoding="utf-8")
    n, total, parsed = pull_b.verify_final_manifest(
        manifest, local=local, exp="e9f", required_results=required)
    assert n == len(parsed) and total > 0


def test_complete_report_refuses_missing_score_and_partial(tmp_path):
    _, config, report = _fixture(tmp_path)
    report["scores"] = {}
    report["controls"] = None
    with pytest.raises(ValueError, match="complete report scores"):
        pull_b.validate_complete_report(report, config=config, exp="e9f", pair=pull_b.PAIR)
    # Entry 0042 registers allow_partial = true for this cell, so a partial report is NOT refused for
    # being partial. What is still refused is a partial whose config does not permit one -- the two
    # must agree, or either could drift from the registered rule.
    _, config, report = _fixture(tmp_path / "again")
    forbidding = config.read_text(encoding="utf-8").replace("allow_partial = true", "allow_partial = false")
    (tmp_path / "again" / "forbids.toml").write_text(forbidding, encoding="utf-8")
    report["partial"] = {"n_scored": 1}
    forbids = tmp_path / "again" / "forbids.toml"
    report["config_sha256"] = pull_b.text_sha256(forbids)   # the report is written under THAT config
    with pytest.raises(ValueError, match="registered config forbids one"):
        pull_b.validate_complete_report(report, config=forbids, exp="e9f", pair=pull_b.PAIR)


def test_manifest_refuses_traversal_and_missing_required_path(tmp_path):
    bad = tmp_path / "bad.sha256"
    bad.write_text(f"{'0' * 64}  ../escape\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe"):
        pull_b.parse_manifest(bad)
    empty = tmp_path / "empty.sha256"
    empty.write_text(f"{'0' * 64}  sitting_b.setup.log\n", encoding="utf-8")
    with pytest.raises(ValueError, match="omits"):
        pull_b.verify_final_manifest(empty, local=tmp_path, exp="e9f", required_results={"report.json"})


def test_new_terminate_receipt_is_nonce_and_pod_bound_but_legacy_a_still_works(tmp_path):
    receipt = tmp_path / "verified.json"
    state = {"verify_nonce": "nonce", "pod_id": "pod-b", "created_utc": "time"}
    receipt.write_text(json.dumps({
        "schema": rp.VERIFY_RECEIPT_SCHEMA,
        "verify_nonce": "nonce",
        "pod_id": "pod-b",
        "created_utc": "time",
        "verified_utc": "later",
        "report_sha256": "a" * 64,
    }), encoding="utf-8")
    assert rp._check_verify_interlock(state, receipt, "pod-b")[0]
    assert not rp._check_verify_interlock(state, receipt, "another-pod")[0]
    state["verify_nonce"] = "different"
    assert not rp._check_verify_interlock(state, receipt, "pod-b")[0]
    legacy = tmp_path / "legacy-a.txt"
    legacy.write_text("sitting A verified at home\n", encoding="utf-8")
    assert rp._check_verify_interlock({"pod_id": "pod-a", "name": "linear-ceiling-sitting-a"},
                                      legacy, "pod-a")[0]
    assert not rp._check_verify_interlock({"pod_id": "pod-b", "name": "linear-ceiling-sitting-b"},
                                          legacy, "pod-b")[0]


def test_binding_refuses_live_sitting_a_state():
    state = {"name": "linear-ceiling-sitting-a", "pod_id": "a", "verify_nonce": "n", "verify_file": "v"}
    with pytest.raises(ValueError, match="wrong sitting"):
        pull_b.validate_runpod_binding(state, expected_name=pull_b.POD_NAME)


def test_checkpoint_identity_refuses_wrong_included_order_and_control_handoff(tmp_path):
    _, config, report = _fixture(tmp_path)
    report["alignments"].append({"handoff_id": "a", "excluded": False})
    report["coverage"] = {"observed": 2, "included": 2, "excluded": 0}
    report["complete"] = False
    # The ID-sort guard only applies to a cell registered `by = "id"`. E9F registers n_sender_asc
    # (entry 0042), so that guard is exercised against its own config rather than deleted -- it is
    # still live code for any cell that registers the ID order, including config/e9.toml's default.
    id_cfg = tmp_path / "by_id.toml"
    id_cfg.write_text(config.read_text(encoding="utf-8").replace('by = "n_sender_asc"', 'by = "id"'),
                      encoding="utf-8")
    id_report = dict(report, order_by="id", run_order=["h", "a"],   # not the registered ID sort
                     config_sha256=pull_b.text_sha256(id_cfg))
    with pytest.raises(ValueError, match="ID-sorted"):
        pull_b.validate_checkpoint_report(id_report, config=id_cfg, exp="e9f", pair=pull_b.PAIR)
    report["run_order"] = ["a", "h"]
    report["scores"] = {}
    report["controls"] = {"handoff_id": "not-first"}
    with pytest.raises(ValueError, match="controls before"):
        pull_b.validate_checkpoint_report(report, config=config, exp="e9f", pair=pull_b.PAIR)


def test_transport_resolves_exact_state_pod_not_first_prefix(monkeypatch):
    pods = [
        {"id": "other", "name": pull_b.POD_NAME},
        {"id": "wanted", "name": pull_b.POD_NAME},
    ]
    monkeypatch.setattr(pull_b.rp, "pods", lambda: pods)
    monkeypatch.setattr(pull_b.rp, "_ports", lambda pod: (f"ip-{pod['id']}", "22"))
    tx = pull_b.Transport("wanted", pull_b.POD_NAME)
    assert tx.ssh[-1] == "root@ip-wanted"


def test_remote_delete_boundary_is_exactly_one_scratch_child():
    tx = object.__new__(pull_b.Transport)
    called = []
    tx.run_bytes = lambda command, timeout=120: called.append(command) or b""
    root = "/workspace/linear-ceiling/results/e9f"
    tx.remove_verified_tree(f"{root}/scratch/handoff", root)
    assert called and "scratch/handoff" in called[0]
    for bad in (
        f"{root}/scratch",
        f"{root}/scratch/nested/child",
        "/tmp/scratch/handoff",
        f"{root}/scores/handoff",
    ):
        with pytest.raises(ValueError, match="unsafe deletion"):
            tx.remove_verified_tree(bad, root)
