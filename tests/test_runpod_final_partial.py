"""B4: the terminal path for a REGISTERED PARTIAL CLOSE.

WHY THIS EXISTS. Entry 0042 registers a stopping rule for the verdict cell -- a run stopped at the
budget ceiling closes on a prefix of the registered order -- and before this path existed the rule had
no terminal step. `close_partial` writes `complete: true` + `partial{...}`, and every acceptance path
in the tooling refused that shape, so a budget-killed sitting could be paid for and never closed.

The rule under test, registered BEFORE the run so that it is not a choice made after seeing scores:
the closing basis is the LAST checkpoint whose every named artifact is sha-verified at home. It must
be a genuine driver checkpoint and a prefix of the registered order, never an edited report.

Covered:
  * the basis is the checkpoint with the most scored handoffs that verifies WHOLE;
  * a checkpoint naming a kept dump that never arrived is skipped, and the next one down is used;
  * a snapshot that outranks the live report.json is installed, and the superseded file is kept;
  * a NON-prefix checkpoint is never a basis, however much it scored;
  * the receipt records `partial{n_scored}` and rp.py's interlock accepts it;
  * a live driver is a refusal, and an unreachable API is a refusal rather than an assumption.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "runpod"))
import pull_verify_b as pull_b                                     # noqa: E402
import rp                                                          # noqa: E402

EXP, PAIR = "e9f", pull_b.PAIR
ORDER = ["h1", "h2", "h3", "h4"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def mirror(tmp_path):
    """A home mirror with alignments present, plus the config the reports are bound to."""
    local = tmp_path / "results" / EXP
    (local / "align").mkdir(parents=True)
    (local / "align" / "coverage.json").write_text(json.dumps({"run_order": ORDER}), encoding="utf-8")
    for hid in ORDER + ["x0"]:
        (local / "align" / f"{hid}.json").write_text("{}", encoding="utf-8")
        (local / "align" / f"{hid}.npz").write_bytes(b"npz")
    cfg = tmp_path / "e9f.toml"
    cfg.write_text('[e9]\n'
                   f'pair = "{PAIR}"\n'
                   'results_dir = "results/e9f"\n'
                   'upstream_sha = "pin"\n'
                   '[e9.order]\nby = "n_sender_asc"\nallow_partial = true\n', encoding="utf-8")
    return local, cfg


KEEP = [ORDER[0], ORDER[2]]      # two kept handoffs, so a longer prefix names a dump a shorter one does not


def _report(cfg: Path, scored: list[str]):
    """A driver checkpoint over `scored`. h1 and h3 carry keep-subset dumps."""
    scores = {}
    for hid in scored:
        rec = {"score_file": f"{hid}.json", "score_sha256": _sha(f"s-{hid}".encode()),
               "tokens_file": f"{hid}.npz", "tokens_sha256": _sha(f"t-{hid}".encode())}
        if hid in KEEP:
            rec["kept_dir"] = f"scratch/{hid}"
            rec["kept_dumps"] = {"same_src": {"kv.npz": _sha(b"kept")}}
        scores[hid] = rec
    controls = None
    if scored:
        controls = {"handoff_id": scored[0]}
        for arm in ("identity", "prefix", "null"):
            controls[arm] = {"score_file": f"{arm}.json", "score_sha256": _sha(f"c-{arm}".encode()),
                             "tokens_file": f"{arm}.npz", "tokens_sha256": _sha(f"ct-{arm}".encode())}
    return {
        "pair": PAIR, "upstream_sha": "pin", "config_sha256": pull_b.text_sha256(cfg),
        "order_by": "n_sender_asc", "run_order": ORDER,
        "coverage": {"observed": len(ORDER) + 1, "included": len(ORDER), "excluded": 1},
        "alignments": ([{"handoff_id": h, "excluded": False} for h in ORDER]
                       + [{"handoff_id": "x0", "excluded": True}]),
        "scores": scores, "controls": controls, "keep_subset": KEEP, "complete": False,
    }


def _materialise(local: Path, report: dict, *, kept: bool = True) -> None:
    """Write to disk exactly the bytes the report fingerprints (optionally omitting the kept dump)."""
    for hid, rec in report["scores"].items():
        (local / "scores").mkdir(parents=True, exist_ok=True)
        (local / "tokens").mkdir(parents=True, exist_ok=True)
        (local / "scores" / rec["score_file"]).write_bytes(f"s-{hid}".encode())
        (local / "tokens" / rec["tokens_file"]).write_bytes(f"t-{hid}".encode())
        if rec.get("kept_dumps") and kept:
            d = local / rec["kept_dir"] / "same_src"
            d.mkdir(parents=True, exist_ok=True)
            (d / "kv.npz").write_bytes(b"kept")
    if report.get("controls"):
        (local / "controls").mkdir(parents=True, exist_ok=True)
        for arm in ("identity", "prefix", "null"):
            (local / "controls" / f"{arm}.json").write_bytes(f"c-{arm}".encode())
            (local / "controls" / f"{arm}.npz").write_bytes(f"ct-{arm}".encode())


def _snapshot(local: Path, report: dict) -> Path:
    snaps = local / "checkpoints"
    snaps.mkdir(parents=True, exist_ok=True)
    path = snaps / f"report.{len(report['scores'])}.json"
    path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return path


def test_the_basis_is_the_longest_checkpoint_that_verifies_whole(mirror):
    """Three scored beats two -- but only because all three verify."""
    local, cfg = mirror
    two, three = _report(cfg, ORDER[:2]), _report(cfg, ORDER[:3])
    _materialise(local, three)
    _snapshot(local, two)
    _snapshot(local, three)
    basis, rep, checked, _ = pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)
    assert basis.name == "report.3.json"
    assert list(rep["scores"]) == ORDER[:3]
    assert checked == len(pull_b.report_artifacts(rep))


def test_a_checkpoint_naming_a_kept_dump_that_never_arrived_is_skipped(mirror):
    """The exact hard-kill shape: the newest checkpoint names a tensor still in flight when the pod
    died. It must NOT be the basis, and the next one down must be.

    h3 is in the keep subset and h1 is too, so the 3-prefix names a dump the 2-prefix does not. Delete
    only h3's and the 3-checkpoint becomes unusable while the 2-checkpoint stays whole -- which is what
    makes the fall-through observable rather than an all-or-nothing refusal."""
    local, cfg = mirror
    two, three = _report(cfg, ORDER[:2]), _report(cfg, ORDER[:3])
    _materialise(local, three)
    (local / "scratch" / ORDER[2] / "same_src" / "kv.npz").unlink()   # h3's dump never landed
    _snapshot(local, two)
    _snapshot(local, three)
    basis, rep, _, _ = pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)
    assert basis.name == "report.2.json", "the longest checkpoint was not whole; the last whole one closes"
    assert list(rep["scores"]) == ORDER[:2]

    # Restore it and the longest wins again, proving the fall-through was about that file alone.
    d = local / "scratch" / ORDER[2] / "same_src"
    d.mkdir(parents=True, exist_ok=True)
    (d / "kv.npz").write_bytes(b"kept")
    basis, _, _, _ = pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)
    assert basis.name == "report.3.json"


def test_a_torn_live_report_loses_to_a_verified_snapshot(mirror):
    """report.json half-written by a kill is not a basis; the last good snapshot is."""
    local, cfg = mirror
    two = _report(cfg, ORDER[:2])
    _materialise(local, two)
    _snapshot(local, two)
    (local / "report.json").write_text('{"scores": {"h1": ', encoding="utf-8")   # torn mid-write
    basis, rep, _, _ = pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)
    assert basis.name == "report.2.json" and list(rep["scores"]) == ORDER[:2]


def test_a_non_prefix_checkpoint_is_never_a_basis(mirror):
    """0042 registers a PREFIX of `n_sender_asc`, not "whatever finished"."""
    local, cfg = mirror
    bad = _report(cfg, [ORDER[0], ORDER[2]])
    _materialise(local, bad)
    _snapshot(local, bad)
    with pytest.raises(ValueError, match="prefix"):
        pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)


def test_a_complete_report_is_refused_and_told_to_use_the_complete_path(mirror):
    local, cfg = mirror
    done = _report(cfg, ORDER)
    done["complete"] = True
    _materialise(local, done)
    (local / "report.json").write_text(json.dumps(done), encoding="utf-8")
    with pytest.raises(ValueError, match="COMPLETE"):
        pull_b.choose_partial_basis(local, config=cfg, exp=EXP, pair=PAIR)


def test_final_partial_installs_the_snapshot_keeps_the_superseded_file_and_receipts_it(mirror, tmp_path, monkeypatch, capsys):
    """End to end, the hard-kill case: pod gone, live report torn, close on the last good snapshot."""
    local, cfg = mirror
    three = _report(cfg, ORDER[:3])
    _materialise(local, three)
    _snapshot(local, three)
    (local / "report.json").write_text("{ torn", encoding="utf-8")

    verify = tmp_path / "verified.json"
    runpod_state = {"pod_id": "pod123", "verify_nonce": "n" * 32, "created_utc": "2026-09-19T00:00:00Z",
                    "verify_file": str(verify), "name": f"{rp.NAME_PREFIX}sitting-b"}
    monkeypatch.setattr(pull_b.rp, "pods", lambda: [])            # the pod is gone: a hard kill

    a = pull_b.build_parser().parse_args(["--local", str(local), "--config", str(cfg)])
    assert pull_b.final_partial(a, runpod_state) == 0

    installed = json.loads((local / "report.json").read_text(encoding="utf-8"))
    assert list(installed["scores"]) == ORDER[:3] and installed.get("complete") is False
    superseded = list(local.glob("report.superseded-*.json"))
    assert len(superseded) == 1 and superseded[0].read_text(encoding="utf-8") == "{ torn", \
        "the file that lost must be kept: it is the evidence for why this basis was chosen"

    receipt = json.loads(verify.read_text(encoding="utf-8"))
    assert receipt["partial"]["n_scored"] == 3
    assert receipt["partial"]["unscored"] == ORDER[3:]
    assert receipt["final_manifest_sha256"] is None, "a partial has no final manifest by construction"
    ok, why = rp._check_verify_interlock(runpod_state, verify, "pod123")
    assert ok, f"rp.py rejected the partial receipt: {why}"

    out = capsys.readouterr().out
    assert "--close-partial" in out, "the operator must be told the one remaining step"


def test_a_live_driver_and_an_unreachable_api_are_both_refusals(mirror, tmp_path, monkeypatch, capsys):
    """Closing a partial while the driver can still append would close it short. So would guessing."""
    local, cfg = mirror
    two = _report(cfg, ORDER[:2])
    _materialise(local, two)
    _snapshot(local, two)
    verify = tmp_path / "verified.json"
    runpod_state = {"pod_id": "pod123", "verify_nonce": "n" * 32, "created_utc": "2026-09-19T00:00:00Z",
                    "verify_file": str(verify), "name": f"{rp.NAME_PREFIX}sitting-b"}
    a = pull_b.build_parser().parse_args(["--local", str(local), "--config", str(cfg)])

    # 1. the API is down -- gql reports that as SystemExit, which is NOT an Exception subclass
    def boom():
        raise SystemExit("rp REFUSED: RunPod API unreachable")
    monkeypatch.setattr(pull_b.rp, "pods", boom)
    assert pull_b.final_partial(a, runpod_state) == 4
    assert "unreachable" in capsys.readouterr().out
    assert not verify.exists()

    # 2. the pod is up and the driver pid is alive
    monkeypatch.setattr(pull_b.rp, "pods", lambda: [{"id": "pod123", "name": f"{rp.NAME_PREFIX}sitting-b"}])

    class FakeTx:
        def __init__(self, *_a, **_k): pass
        def run_bytes(self, cmd, **_k): return b"ALIVE 4242\n"
    monkeypatch.setattr(pull_b, "Transport", FakeTx)
    assert pull_b.final_partial(a, runpod_state) == 4
    assert "still running" in capsys.readouterr().out
    assert not verify.exists(), "no receipt may exist while the driver could still append"

    # 3. same pod, pid dead -> it proceeds
    class DeadTx(FakeTx):
        def run_bytes(self, cmd, **_k): return b"STOPPED 4242\n"
    monkeypatch.setattr(pull_b, "Transport", DeadTx)
    assert pull_b.final_partial(a, runpod_state) == 0
    assert json.loads(verify.read_text(encoding="utf-8"))["partial"]["n_scored"] == 2
