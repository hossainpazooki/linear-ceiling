"""The watchdog must survive a transient API failure, because that is exactly when it is needed.

REGRESSION UNDER TEST (2026-09-18, live, with a pod billing). `gql()` reports every API failure by
raising `SystemExit("rp REFUSED: ... unreachable")`. `SystemExit` derives from `BaseException`, NOT
from `Exception`, so:

  * the original loop caught `SystemExit` and let ordinary errors (TimeoutError,
    RemoteDisconnected, JSONDecodeError) kill the watchdog;
  * the fix for that caught `Exception` and let the `SystemExit`s kill it instead.

The second version died on `[SSL: UNEXPECTED_EOF_WHILE_READING]` and a rented pod ran for five
minutes with no home-side spend ceiling. Neither `except Exception` nor `except SystemExit` alone is
correct here; it must be both. These tests fail against either single-clause version.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

RP = Path(__file__).resolve().parents[1] / "tools" / "runpod" / "rp.py"


def _load():
    spec = importlib.util.spec_from_file_location("rp_under_test", RP)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rp_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def rp():
    return _load()


def test_the_retry_loop_survives_a_gql_systemexit(rp, monkeypatch, capsys):
    """_terminate_until_gone is the path that must never give up. A SystemExit from gql on the
    terminate call, then on the confirmation call, must both be swallowed and retried."""
    calls = {"terminate": 0, "pods": 0}

    def fake_terminate(_ns):
        calls["terminate"] += 1
        if calls["terminate"] == 1:
            raise SystemExit("rp REFUSED: RunPod API unreachable ([SSL: UNEXPECTED_EOF_WHILE_READING])")

    def fake_pods():
        calls["pods"] += 1
        if calls["pods"] == 1:
            raise SystemExit("rp REFUSED: RunPod API unreachable (transient)")
        return []                                  # second look: the pod is gone

    monkeypatch.setattr(rp, "cmd_terminate", fake_terminate)
    monkeypatch.setattr(rp, "pods", fake_pods)
    monkeypatch.setattr(rp.time, "sleep", lambda *_: None)

    assert rp._terminate_until_gone("test") == 0
    assert calls["terminate"] >= 2, "a SystemExit on the first attempt must not end the retry loop"
    out = capsys.readouterr().out
    assert "STILL BILLING" in out, "it must say so while a pod may still be running"


def test_the_retry_loop_survives_an_ordinary_exception(rp, monkeypatch, capsys):
    """The other half of the regression: plain exceptions must not escape either."""
    seen = {"n": 0}

    def fake_terminate(_ns):
        seen["n"] += 1
        if seen["n"] == 1:
            raise TimeoutError("read timed out")

    monkeypatch.setattr(rp, "cmd_terminate", fake_terminate)
    monkeypatch.setattr(rp, "pods", lambda: [] if seen["n"] >= 2 else [{"name": "linear-ceiling-x"}])
    monkeypatch.setattr(rp.time, "sleep", lambda *_: None)
    assert rp._terminate_until_gone("test") == 0
    assert seen["n"] >= 2


def test_the_watchdog_loop_keeps_polling_through_a_gql_systemexit(rp, monkeypatch, capsys):
    """The live failure, end to end: the poll raises SystemExit, and the watchdog must count it as
    unreachable and CARRY ON rather than exit the process."""
    state = {"polls": 0}

    def fake_spend(_st):
        state["polls"] += 1
        if state["polls"] <= 2:
            raise SystemExit("rp REFUSED: RunPod API unreachable ([SSL: UNEXPECTED_EOF_WHILE_READING])")
        return (0.10, 0.10, 9.9)

    monkeypatch.setattr(rp, "spend_now", fake_spend)
    monkeypatch.setattr(rp, "pods", lambda: [])          # third poll: nothing billing -> clean exit
    monkeypatch.setattr(rp, "load_state", lambda: {"created_epoch": rp.time.time(),
                                                   "sitting_max": 3.25, "hours": 6.5, "warn": 2.5})
    monkeypatch.setattr(rp.time, "sleep", lambda *_: None)
    monkeypatch.setattr(rp.os.environ, "get", lambda k, d=None: "1" if k == "RP_CAFFEINATED" else d)

    args = rp.argparse.Namespace(warn=None, kill=9.0, sitting_max=None, ttl=None,
                                 unreachable_terminate_after=10.0, every=1)
    assert rp.cmd_watchdog(args) == 0, "the watchdog must exit 0 only because nothing is billing"
    assert state["polls"] >= 3, "it must have kept polling after the SystemExits"
    assert "unreachable" in capsys.readouterr().out
