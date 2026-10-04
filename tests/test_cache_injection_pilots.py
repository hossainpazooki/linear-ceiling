import ast
from pathlib import Path
from unittest.mock import Mock

import pytest
import torch


PILOT = Path(__file__).resolve().parents[1] / "tools/cache_injection_pilots"


def helpers(device="cpu"):
    # Legacy common.py imports model loaders and changes process-wide settings.
    # Load only the actual pure/helper definitions for these offline checks.
    tree = ast.parse((PILOT / "common.py").read_text())
    definitions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in {"sync", "rotate"}
    ]
    namespace = {"torch": torch, "DEVICE": torch.device(device)}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "common.py", "exec"), namespace)
    return namespace


@pytest.mark.parametrize("device", ["cpu", "mps", "cuda:1"])
def test_timing_synchronizes_only_the_selected_backend(monkeypatch, device):
    cuda, mps = Mock(), Mock()
    monkeypatch.setattr(torch.cuda, "synchronize", cuda)
    monkeypatch.setattr(torch.mps, "synchronize", mps)
    helpers(device)["sync"]()
    if device.startswith("cuda"):
        cuda.assert_called_once_with(torch.device(device))
    else:
        cuda.assert_not_called()
    assert mps.call_count == int(device == "mps")


@pytest.mark.parametrize("amplitude", [1.0, 1.1])
def test_relocation_preserves_existing_rotary_amplitude(amplitude):
    rotate = helpers()["rotate"]
    keys = torch.arange(2 * 3 * 4 * 8, dtype=torch.float32).reshape(2, 3, 4, 8) / 100
    # Binary frequencies avoid angle-rounding differences in this algebra check.
    frequencies = torch.tensor([1.0, 0.125, 0.015625, 0.001953125])
    source = torch.tensor([0, 17, 32767, 80110])
    destination = torch.tensor([29, 0, 641, 12000])
    cached = rotate(keys, source, frequencies, scale=amplitude)
    relocated = rotate(cached, destination - source, frequencies)
    expected = rotate(keys, destination, frequencies, scale=amplitude)
    torch.testing.assert_close(relocated, expected, rtol=2e-6, atol=2e-6)
    torch.testing.assert_close(rotate(cached, -source, frequencies, 1 / amplitude), keys,
                               rtol=2e-6, atol=2e-6)

def test_archive_alias_setup_does_not_delete_existing_records(tmp_path):
    import subprocess
    import sys

    script = tmp_path / "prepare_inputs.py"
    script.write_text((PILOT / script.name).read_text())
    records = tmp_path / "records"
    (records / "align").mkdir(parents=True)
    sentinel = records / "align/measurement.npz"
    sentinel.write_bytes(b"existing measurement")
    result = subprocess.run([sys.executable, str(script)], capture_output=True)
    assert result.returncode != 0
    assert sentinel.read_bytes() == b"existing measurement"
