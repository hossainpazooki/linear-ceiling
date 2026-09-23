import os
import signal
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_published_pid_is_the_signal_receiving_driver_not_the_waiting_supervisor(tmp_path):
    pid_file = tmp_path / "driver.pid"
    go_file = tmp_path / "driver.go"
    started_file = tmp_path / "driver.started"
    fake_python = tmp_path / "python"
    fake_python.write_text(f"#!/usr/bin/env bash\ntrap 'exit 42' TERM\ntouch {started_file}\n"
                           "while :; do sleep 0.05; done\n", encoding="utf-8")
    fake_python.chmod(0o755)
    proc = subprocess.Popen([str(ROOT / "tools/runpod/driver_child.sh"), str(pid_file), str(go_file),
                             "plain", str(fake_python), "config/e9f.toml"])
    try:
        for _ in range(100):
            if pid_file.exists():
                break
            time.sleep(0.01)
        driver_pid = int(pid_file.read_text(encoding="utf-8"))
        assert driver_pid != proc.pid, "the watchdog must not receive the supervisor shell's PID"
        go_file.touch()
        for _ in range(100):
            if started_file.exists():
                break
            time.sleep(0.01)
        assert started_file.exists(), "the released child must exec the real driver"
        os.kill(driver_pid, signal.SIGTERM)
        assert proc.wait(timeout=5) == 42, "SIGTERM must reach the published driver and propagate its exit"
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
