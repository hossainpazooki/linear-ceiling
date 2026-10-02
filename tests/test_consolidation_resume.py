import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("changed", ["code_commit", "code_sha256", "torch", "complete"])
def test_resume_refuses_changed_runtime_or_incomplete_cohort(tmp_path, monkeypatch, changed):
    def unexpected_model_load(*args, **kwargs):
        pytest.fail("changed run reached model loading")

    # Resume refusal precedes inference; these checks need no Transformers install.
    loader = SimpleNamespace(from_pretrained=unexpected_model_load)
    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(
        __version__="test runtime", AutoConfig=loader, AutoModel=loader))
    folder = Path(__file__).parents[1] / "tools/consolidation"
    monkeypatch.syspath_prepend(str(folder))
    spec = importlib.util.spec_from_file_location("consolidation_run", folder / "run.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver.subprocess, "check_output", lambda *a, **kw: "frozen\n")
    monkeypatch.setattr(driver.torch.cuda, "get_device_name", lambda: "test GPU")
    config = tmp_path / "config"
    config.mkdir()
    cfg = config / "consolidation.toml"
    cfg.write_text('seed = 1\n[[models]]\nname = "qwen17_bridge"\nmodel = "test"\nrevision = "fixed"\n')
    (tmp_path / "input.npz").write_bytes(b"unread: refusal must precede model loading")
    manifest = config / "consolidation-manifest.json"
    manifest.write_text(json.dumps({"config_sha256": driver.digest(cfg), "models": {
        "qwen17_bridge": [{"handoff": "case", "excluded": False, "file": "input.npz",
                           "sha256": driver.digest(tmp_path / "input.npz")}]
    }}))
    output = tmp_path / "output/qwen17_bridge"
    output.mkdir(parents=True)
    report = {"config_sha256": driver.digest(cfg), "manifest_sha256": driver.digest(manifest),
              "code_commit": "frozen", "code_sha256": {name: driver.digest(folder / name)
                                                       for name in ("run.py", "capture.py")},
              "torch": driver.torch.__version__,
              "transformers": driver.transformers.__version__, "numpy": driver.np.__version__,
              "cuda": driver.torch.version.cuda, "gpu": "test GPU", "dtype": "float32",
              "scores": {}, "complete": False}
    report[changed] = True if changed == "complete" else "different"
    (output / "report.json").write_text(json.dumps(report))
    monkeypatch.setattr(sys, "argv", ["run.py", "--model", "qwen17_bridge", "--inputs",
                                     str(tmp_path), "--output", str(output.parent)])
    with pytest.raises(ValueError, match="resume identity|cohort"):
        driver.main()
