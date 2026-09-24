"""M1: the home-side ceiling must outlive the process that enforces it.

`rp.py watchdog` is the only thing that stops a runaway sitting. On 2026-09-18 it died mid-sitting on
an SSL EOF and a rented pod billed five minutes with no ceiling. The retry bug is fixed; the class --
one process, many ways to die -- is what `watchdog_supervised.sh` answers.

Two rules are pinned here because both were learned the expensive way:
  * the supervisor restarts on ANY non-zero exit, forever, and stops only on exit 0;
  * exit 0 means the watchdog saw nothing billing on TWO CONSECUTIVE polls. A single empty listing is
    not proof -- the account listing is eventually consistent -- and standing down on one removes the
    ceiling while a pod is still up.
"""
import importlib.util
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "tools" / "runpod" / "watchdog_supervised.sh"
RP = ROOT / "tools" / "runpod" / "rp.py"


def _load_rp():
    spec = importlib.util.spec_from_file_location("rp_under_supervision", RP)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rp_under_supervision"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def rp():
    return _load_rp()


def test_one_empty_listing_does_not_stand_the_watchdog_down(rp, monkeypatch, capsys):
    """The regression this rule exists for: a transient empty page must not end the ceiling."""
    seen = {"polls": 0}
    # poll 1: empty (the blip).  poll 2: the pod is back and billing.  poll 3+: genuinely gone.
    listings = [[], [{"name": f"{rp.NAME_PREFIX}sitting-b", "id": "p1"}], [], []]

    def fake_pods():
        i = seen["polls"]
        seen["polls"] += 1
        return listings[min(i, len(listings) - 1)]

    monkeypatch.setattr(rp, "pods", fake_pods)
    monkeypatch.setattr(rp, "spend_now", lambda _st: (0.10, 0.10, 9.9))
    monkeypatch.setattr(rp, "load_state", lambda: {"created_epoch": rp.time.time(),
                                                   "sitting_max": 6.55, "hours": 5.5, "warn": 2.5})
    monkeypatch.setattr(rp.time, "sleep", lambda *_: None)
    monkeypatch.setattr(rp.os.environ, "get", lambda k, d=None: "1" if k == "RP_CAFFEINATED" else d)
    args = rp.build_parser().parse_args(["watchdog", "--kill", "9.0", "--every", "1"])
    assert rp.cmd_watchdog(args) == 0
    out = capsys.readouterr().out
    assert "1/2" in out, "the first empty listing must be reported as unconfirmed, not acted on"
    # It kept watching through the blip and only stood down once two polls in a row agreed.
    assert seen["polls"] >= 4, f"stood down too early after {seen['polls']} polls"


def _stub_interpreter(tmp_path: Path, exits: list[int]) -> Path:
    """An executable that stands in for the venv python, returning `exits` in order (last repeats)."""
    counter = tmp_path / "n"
    counter.write_text("0", encoding="utf-8")
    stub = tmp_path / "fake-python"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'n=$(cat {counter})\n'
        f'echo $((n + 1)) > {counter}\n'
        f'codes=({" ".join(str(x) for x in exits)})\n'
        'i=$n; last=$(( ${#codes[@]} - 1 )); [ "$i" -gt "$last" ] && i=$last\n'
        'echo "stub watchdog call $((n + 1)) -> rc=${codes[$i]}"\n'
        'exit "${codes[$i]}"\n', encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    return stub


def _run_supervisor(tmp_path: Path, exits: list[int], *, timeout: int = 30):
    env = dict(os.environ)
    env.update(PY=str(_stub_interpreter(tmp_path, exits)),
               WATCHDOG_LOG=str(tmp_path / "sup.log"),
               WATCHDOG_LOCK=str(tmp_path / "sup.lock"),
               RESTART_DELAY="0")
    return subprocess.run(["bash", str(SUPERVISOR)], capture_output=True, text=True,
                          timeout=timeout, env=env)


def test_the_supervisor_rehangs_the_net_after_a_crash_and_stops_only_on_zero(tmp_path):
    """Two deaths, then a clean stand-down. It must survive both and not give up in between."""
    out = _run_supervisor(tmp_path, [1, 137, 0])
    assert out.returncode == 0, out.stderr[-500:]
    log = (tmp_path / "sup.log").read_text(encoding="utf-8")
    assert log.count("WATCHDOG DIED") == 2, log
    assert "rc=137" in log, "a killed watchdog must be recorded by its real exit code"
    assert "after 2 restart(s)" in log, "the unwatched windows must be countable afterwards"
    assert "\a" in log or "\a" in out.stdout, "an unwatched pod must make noise, not just a log line"


def test_a_second_supervisor_refuses_rather_than_doubling_every_alert(tmp_path):
    lock = tmp_path / "sup.lock"
    lock.mkdir()
    (lock / "pid").write_text(str(os.getpid()), encoding="utf-8")   # a live pid: this test process
    env = dict(os.environ)
    env.update(PY=str(_stub_interpreter(tmp_path, [0])), WATCHDOG_LOG=str(tmp_path / "sup.log"),
               WATCHDOG_LOCK=str(lock), RESTART_DELAY="0")
    out = subprocess.run(["bash", str(SUPERVISOR)], capture_output=True, text=True, timeout=30, env=env)
    assert out.returncode == 3 and "already holds" in out.stdout + out.stderr


def test_a_stale_lock_is_taken_over_rather_than_left_to_block_the_ceiling(tmp_path):
    """A supervisor killed without cleanup must not prevent the next one; that would be a lock that
    causes the very outage it guards against."""
    lock = tmp_path / "sup.lock"
    lock.mkdir()
    (lock / "pid").write_text("999999", encoding="utf-8")            # a pid that cannot be alive
    env = dict(os.environ)
    env.update(PY=str(_stub_interpreter(tmp_path, [0])), WATCHDOG_LOG=str(tmp_path / "sup.log"),
               WATCHDOG_LOCK=str(lock), RESTART_DELAY="0")
    out = subprocess.run(["bash", str(SUPERVISOR)], capture_output=True, text=True, timeout=30, env=env)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "stale lock" in (tmp_path / "sup.log").read_text(encoding="utf-8")
