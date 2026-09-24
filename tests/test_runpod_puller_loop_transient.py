import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "runpod"))
import pull_verify_b as pull_b

def _setup(tmp_path, monkeypatch, exc):
    rs = {"pod_id": "p1", "verify_nonce": "n"}
    (tmp_path / "rp.json").write_text(json.dumps(rs))
    local = tmp_path / "res"; local.mkdir()
    (local / "report.json").write_text(json.dumps({"scores": {}}))
    monkeypatch.setattr(pull_b, "validate_runpod_binding", lambda *a, **k: None)
    monkeypatch.setattr(pull_b, "require_free_space", lambda *a, **k: None)
    monkeypatch.setattr(pull_b.Transport, "__init__", lambda self, *a, **k: None)
    def boom(self, cmd, timeout=120): raise exc
    monkeypatch.setattr(pull_b.Transport, "run_bytes", boom)
    rounds = []
    def fake_round(*a, **k):
        rounds.append(1); raise RuntimeError("ssh blip inside round")
    monkeypatch.setattr(pull_b, "run_round", fake_round)
    return ["--runpod-state", str(tmp_path / "rp.json"), "--local", str(local),
            "--state", str(tmp_path / "pull.json"), "--once", "--every", "5"], rounds

def test_transient_ssh_failure_at_loop_top_is_survived(tmp_path, monkeypatch):
    argv, rounds = _setup(tmp_path, monkeypatch, RuntimeError("remote command rc=255: Connection reset"))
    assert pull_b.main(argv) == 3   # the same "round failed safely" path run_round failures take

def test_ssh_timeout_at_loop_top_is_survived(tmp_path, monkeypatch):
    argv, rounds = _setup(tmp_path, monkeypatch, subprocess.TimeoutExpired("ssh", 120))
    assert pull_b.main(argv) == 3
