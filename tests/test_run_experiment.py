from linear_ceiling.run_experiment import main
from linear_ceiling.seal import write_prediction
from tests.conftest import commit_all

PAIR = "qwen3-0.6b-to-4b"


def _cfg_file(repo, seal_cfg):
    up = seal_cfg.upstream_path.as_posix()
    p = repo / "seal.toml"
    p.write_text(f'''
predictions_dir = "ledger/predictions"
upstream_path = "{up}"
[[artifact_roots]]
path = "mappers"
pattern = "{{pair}}/**/k*.safetensors"
[[artifact_roots]]
path = "results/mapper"
pattern = "{{pair}}/**/r2.json"
[[artifact_roots]]
path = "${{upstream}}/mappers"
pattern = "{{pair}}/**/k*.safetensors"
[[artifact_roots]]
path = "${{upstream}}/results/mapper"
pattern = "{{pair}}/**/r2.json"
''', encoding="utf-8")
    return p


def test_e2_refuses_to_start_without_seal(repo, seal_cfg, capsys):
    rc = main(["--experiment", "e2", "--pair", PAIR], repo_root=repo, config_path=_cfg_file(repo, seal_cfg))
    assert rc == 2
    assert "SEAL VIOLATION" in capsys.readouterr().err


def test_e2_passes_gate_then_stops_as_unimplemented(repo, seal_cfg, capsys):
    write_prediction(PAIR, {"x": 1}, seal_cfg)
    commit_all(repo)
    rc = main(["--experiment", "e2", "--pair", PAIR], repo_root=repo, config_path=_cfg_file(repo, seal_cfg))
    out = capsys.readouterr()
    assert rc == 3 and "seal OK" in out.out and "not implemented" in out.err


def test_e0_is_not_this_runner(repo, seal_cfg, capsys):
    rc = main(["--experiment", "e0", "--pair", PAIR], repo_root=repo, config_path=_cfg_file(repo, seal_cfg))
    assert rc == 2 and "linear_ceiling.e0" in capsys.readouterr().err


def test_missing_seal_config_refuses_cleanly(repo, capsys):
    missing = repo / "does-not-exist.toml"
    rc = main(["--experiment", "e2", "--pair", PAIR], repo_root=repo, config_path=missing)
    out = capsys.readouterr()
    assert rc == 2
    assert "SEAL VIOLATION" in out.err
    assert "seal OK" not in out.out
    assert out.out == ""
