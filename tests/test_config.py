from pathlib import Path

import pytest

from linear_ceiling.config import load_e0_config, load_seal_config


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_seal_config_expands_upstream_and_resolves_relative_to_root(tmp_path):
    p = _write(tmp_path, "seal.toml", '''
predictions_dir = "ledger/predictions"
upstream_path = "../up"
[[artifact_roots]]
path = "mappers"
pattern = "{pair}/**/k*.safetensors"
[[artifact_roots]]
path = "${upstream}/mappers"
pattern = "{pair}/**/k*.safetensors"
''')
    cfg = load_seal_config(p, repo_root=tmp_path / "repo")
    assert cfg.predictions_dir == (tmp_path / "repo" / "ledger" / "predictions")
    assert cfg.artifact_roots[0].path == tmp_path / "repo" / "mappers"
    assert cfg.artifact_roots[1].path == (tmp_path / "repo" / ".." / "up" / "mappers").resolve()
    assert "{pair}" in cfg.artifact_roots[1].pattern


def test_seal_config_refuses_pattern_without_pair_placeholder(tmp_path):
    p = _write(tmp_path, "seal.toml", '''
predictions_dir = "ledger/predictions"
upstream_path = "../up"
[[artifact_roots]]
path = "mappers"
pattern = "**/k*.safetensors"
''')
    with pytest.raises(ValueError, match="{pair}"):
        load_seal_config(p, repo_root=tmp_path)


def test_e0_config_loads_and_records_its_path(tmp_path):
    p = _write(tmp_path, "e0.toml", '''
seed = 3
operationalization = ""
[models]
ladder = ["Qwen/Qwen3-0.6B"]
optional = []
[e0]
results_dir = "results/e0"
reg_sweep = [0.01]
heldout_frac = 0.2
[e0.rule]
''')
    cfg = load_e0_config(p, repo_root=tmp_path)
    assert cfg.seed == 3 and cfg.operationalization == "" and cfg.rule == {}
    assert cfg.results_dir == tmp_path / "results" / "e0"
    assert cfg.config_path == p


def test_e0_config_rejects_unknown_operationalization(tmp_path):
    p = _write(tmp_path, "e0.toml", '''
seed = 0
operationalization = "Z"
[models]
ladder = ["Qwen/Qwen3-0.6B"]
optional = []
[e0]
results_dir = "results/e0"
reg_sweep = [0.01]
heldout_frac = 0.2
[e0.rule]
''')
    with pytest.raises(ValueError, match="operationalization"):
        load_e0_config(p, repo_root=tmp_path)


def test_repo_configs_load():
    from linear_ceiling import REPO_ROOT
    load_seal_config(REPO_ROOT / "config" / "seal.toml", REPO_ROOT)
    load_e0_config(REPO_ROOT / "config" / "e0.toml", REPO_ROOT)
