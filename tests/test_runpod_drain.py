"""The DRAIN: stop the compute while the evidence is still retrievable.

A spend ceiling that only terminates turns "out of budget" into "lost the sitting". Terminating
destroys ephemeral disk, so a kill fired mid-handoff leaves a report naming tensors that never came
home -- and `summarize_e9` refuses a kept dump whose fingerprint is missing, which makes the WHOLE
partial unusable, not just that handoff. Draining stops the DRIVER instead: the last checkpoint is
intact (the driver's checkpoint write is atomic), the puller finishes what is already written, and the
run closes on a prefix under entry 0042's stopping rule. The ceiling stays as the backstop behind it.

WHEN to drain depends on what is still outstanding and how fast it is actually moving. The watchdog
measures neither, so the puller writes both to a hint file and the watchdog reads it. These tests pin
that the hint is honoured when fresh, ignored when stale or malformed, and floored so that a pessimistic
hint cannot drain a sitting before it has produced anything.
"""
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "runpod"))
import pull_verify_b as pull_b                                      # noqa: E402
import rp                                                           # noqa: E402


def _hint(tmp_path: Path, **kw) -> Path:
    p = tmp_path / "drain-hint.json"
    base = {"schema": "linear-ceiling.runpod.drain-hint.v1", "updated_epoch": time.time(),
            "outstanding_gib": 20.0, "rate_gib_per_h": 10.0}
    base.update(kw)
    p.write_text(json.dumps(base), encoding="utf-8")
    return p


def test_a_fresh_hint_reserves_exactly_the_hours_the_pull_still_needs(tmp_path):
    """20 GiB left at 10 GiB/h is 2 hours; at $0.50/h that is $1.00 of ceiling held back."""
    hint = rp.read_drain_hint(_hint(tmp_path))
    assert hint is not None
    at, why = rp.drain_threshold(limit=6.55, rate_per_hour=0.50, hint=hint)
    # 6.55 - 1.00 = 5.55, but the fallback caps it: a measurement may only drain EARLIER, because
    # `outstanding_gib` cannot see the handoff in flight (see drain_threshold).
    assert at == pytest.approx(0.70 * 6.55)
    assert "2.00 h" in why and "$1.00 reserved" in why and "capped" in why

    # a LARGER outstanding set does move it earlier -- the measurement is not inert
    big = rp.read_drain_hint(_hint(tmp_path, outstanding_gib=60.0, rate_gib_per_h=10.0))
    at2, why2 = rp.drain_threshold(limit=6.55, rate_per_hour=0.50, hint=big)
    assert at2 == pytest.approx(3.55) and at2 < at


def test_a_stale_or_malformed_hint_falls_back_and_never_later_than_a_measurement(tmp_path):
    """The fallback must be a decision, not a crash, and must not be later than the truth."""
    stale = _hint(tmp_path, updated_epoch=time.time() - 3600)
    assert rp.read_drain_hint(stale) is None
    for bad in ({"rate_gib_per_h": 0.0}, {"outstanding_gib": "lots"}, {"updated_epoch": "soon"}):
        assert rp.read_drain_hint(_hint(tmp_path, **bad)) is None
    (tmp_path / "nope.json").write_text("{ not json", encoding="utf-8")
    assert rp.read_drain_hint(tmp_path / "nope.json") is None
    assert rp.read_drain_hint(tmp_path / "absent.json") is None

    at, why = rp.drain_threshold(limit=6.55, rate_per_hour=0.50, hint=None)
    assert at == pytest.approx(0.70 * 6.55) and "fallback" in why


def test_a_pessimistic_hint_cannot_drain_the_sitting_before_it_produces_anything(tmp_path):
    """A hint claiming a pull slower than the whole sitting would otherwise drain at handoff zero.
    A drain at handoff zero is not a partial -- it is a wasted card."""
    hint = rp.read_drain_hint(_hint(tmp_path, outstanding_gib=500.0, rate_gib_per_h=1.0))
    at, why = rp.drain_threshold(limit=6.55, rate_per_hour=0.50, hint=hint)
    assert at == pytest.approx(0.5 * 6.55) and "floored at 50%" in why


def test_the_watchdog_drains_before_it_kills_and_keeps_the_pod_up(tmp_path, monkeypatch, capsys):
    """The whole point: at the drain threshold it signals the DRIVER and keeps polling. It does not
    terminate, because terminating is what loses the unpulled tensors."""
    monkeypatch.setattr(rp, "DRAIN_HINT", tmp_path / "absent.json")   # fallback: 70% of 6.55 = 4.585
    assert rp.read_drain_hint() is None, "the module attribute must be read at CALL time, not bound"
    sent = {}

    def fake_signal(exp):
        sent["exp"] = exp
        return True, "TERM 4242"

    terminated = {"n": 0}
    monkeypatch.setattr(rp, "send_drain_signal", fake_signal)
    monkeypatch.setattr(rp, "_terminate_until_gone", lambda why: terminated.update(n=1) or 0)
    spends = iter([(4.60, 4.60, 5.0), (5.00, 5.00, 4.6), (6.60, 6.60, 3.0)])
    monkeypatch.setattr(rp, "spend_now", lambda _st: next(spends))
    monkeypatch.setattr(rp, "pods", lambda: [{"name": f"{rp.NAME_PREFIX}sitting-b", "id": "p1"}])
    monkeypatch.setattr(rp, "load_state", lambda: {"created_epoch": time.time(), "sitting_max": 6.55,
                                                   "hours": 5.5, "warn": 2.5, "price": 0.50})
    monkeypatch.setattr(rp.time, "sleep", lambda *_: None)
    monkeypatch.setattr(rp.os.environ, "get", lambda k, d=None: "1" if k == "RP_CAFFEINATED" else d)

    args = rp.build_parser().parse_args(["watchdog", "--kill", "9.0", "--every", "1"])
    assert rp.cmd_watchdog(args) == 0
    out = capsys.readouterr().out
    assert sent["exp"] == "e9f", "the drain must signal the driver by the experiment's own pid file"
    assert "DRAIN at $4.6" in out and "pod stays UP" in out
    assert out.count("DRAIN at") == 1, "it must not re-signal a driver it already stopped"
    assert terminated["n"] == 1, "the ceiling must still be the backstop behind the drain"


def test_the_puller_measures_what_the_watchdog_cannot(tmp_path):
    """The hint is the puller's own measurement: what is left, and the honest end-to-end rate --
    verification and waiting included, because those are equally part of how long the rest will take."""
    local = tmp_path / "mirror"
    local.mkdir()
    report = {"scores": {"h1": {"score_file": "h1.json", "score_sha256": "a" * 64,
                                "tokens_file": "h1.npz", "tokens_sha256": "b" * 64,
                                "kept_dir": "scratch/h1",
                                "kept_dumps": {"d": {"kv.npz": "c" * 64}}}}}
    state = {"rate_started_epoch": time.time() - 3600, "bytes_verified_total": 20.0 * 2**30}
    out = tmp_path / "hint.json"
    pull_b.write_drain_hint(state, local, report, {"scratch/h1/d/kv.npz": 8 * 2**30}, path=out)
    hint = json.loads(out.read_text(encoding="utf-8"))
    assert hint["outstanding_gib"] == pytest.approx(8.0), "the kept dump is not home yet"
    assert hint["rate_gib_per_h"] == pytest.approx(20.0, rel=1e-3)
    assert rp.read_drain_hint(out) is not None, "the watchdog must accept what the puller writes"


def test_verified_bytes_are_credited_once_across_repeated_polling_rounds(tmp_path):
    local = tmp_path / "mirror"
    body = b"verified tensor bytes"
    rel = "scratch/h1/same_src/kv.npz"
    path = local / rel
    path.parent.mkdir(parents=True)
    path.write_bytes(body)
    item = pull_b.Artifact("kept h1", rel, "a" * 64)
    state = {}
    assert pull_b.credit_newly_verified(state, local, [item]) == len(body)
    assert pull_b.credit_newly_verified(state, local, [item]) == 0
    assert state["bytes_verified_total"] == len(body)


def test_outstanding_measurement_refuses_an_unlisted_remote_file(tmp_path):
    report = {"scores": {"h1": {"score_file": "h1.json", "score_sha256": "a" * 64,
                                "tokens_file": "h1.npz", "tokens_sha256": "b" * 64,
                                "kept_dir": "scratch/h1",
                                "kept_dumps": {"d": {"kv.npz": "c" * 64}}}}}
    with pytest.raises(ValueError, match="absent both locally and from the remote"):
        pull_b.outstanding_gib(tmp_path, report, {})


# ---------------------------------------------------------------------------------------------
# The disk sequencing the staged weights force: the promise is counted once, and only once.
# ---------------------------------------------------------------------------------------------

def test_the_pre_create_gate_counts_committed_space_but_the_running_floor_never_does(tmp_path, capsys):
    """The staged weight cache must exist at home to be uploaded, is dead once the on-box sha check
    passes, and is bigger than the margin. Counting it makes the gate true; ignoring it refuses a
    sitting that fits, and lowering the floor instead admits one that does not.

    But it is a PROMISE. If the deletion never happens, the running floor -- real free space -- must
    still pause the pull rather than fill the disk."""
    local = tmp_path / "mirror"
    local.mkdir()
    doomed = tmp_path / "box-cache"
    doomed.mkdir()
    (doomed / "shard.safetensors").write_bytes(b"x" * (3 * 2**20))

    gib, lines = pull_b.reclaimable_gib([str(doomed), str(tmp_path / "gone")])
    assert gib == pytest.approx(3 / 1024, rel=1e-3)
    assert any("ABSENT" in ln for ln in lines), "a path already freed must be reported, not counted"

    have = pull_b.free_gib(local)
    # a floor just above what is really free, but within reach of the promise
    floor = have + gib / 2
    pull_b.require_free_space(local, floor, blocking=False, reclaimable=[str(doomed)])
    out = capsys.readouterr().out
    assert "PROMISE, not space" in out and "log the freed bytes" in out

    # and with no promise at all, the same floor refuses
    with pytest.raises(SystemExit, match="below the"):
        pull_b.require_free_space(local, floor, blocking=False, reclaimable=[])

    # a promise too small to close the gap refuses too, and says by how much
    with pytest.raises(SystemExit, match="reclaimable"):
        pull_b.require_free_space(local, have + 10 * gib, blocking=False, reclaimable=[str(doomed)])
