"""The corpus manifest (entry 0024): built from disk, annotated from the S3 listing, the
selection rule RECOVERED from the two sets, and enforced in both directions by the driver's
gate and by `verify_disk`. Offline: the S3 listing is a fake callable."""
import json
from datetime import datetime, timezone

import pytest

from linear_ceiling import e7 as driver
from linear_ceiling import e7_manifest
from linear_ceiling.config import E7Config
from linear_ceiling.e7_corpus import discover_files
from linear_ceiling.e7_manifest import (
    RULES, _instance_of, annotate_s3, build, load, local_records, manifest_path, manifest_sha256,
    selection, verify_disk, write,
)
from tests.conftest import commit_all
from tests.test_e7_corpus import PRICING, THRESHOLDS, TOKENIZER, write_corpus


def _cfg(root, garbage=True):
    write_corpus(root / "traces", garbage=garbage)
    cfgp = root / "config" / "e7.toml"
    cfgp.parent.mkdir(exist_ok=True)
    cfgp.write_text("# synthetic\n", encoding="utf-8")
    return E7Config(traces_dir=root / "traces", results_dir=root / "results", pricing=PRICING,
                    thresholds=THRESHOLDS, tokenizer=TOKENIZER, lane_b_policy="two-tier-cascade",
                    config_path=cfgp)


def _obj(key, size=7):
    return {"key": key, "etag": "etag-" + key.rsplit("/", 1)[-1], "size": size,
            "last_modified": "2026-01-06T06:20:55.000Z"}


def fake_listing(prefix):
    """The bucket as the synthetic corpus would see it: every local file present, plus more."""
    sub = prefix.split("/")[1]
    if sub == "20240820_honeycomb":
        names = ["inst-1.json", "inst-9.json", "inst-a.json", "inst-b.json"]     # local = first 2
    elif sub == "20241016_composio_swekit":
        names = ["inst-1_traj.json", "inst-2_traj.json"]
    elif sub.startswith("20250122_autocoderover"):
        names = ["inst-2/attempt_0/patching_agent.json", "inst-2/attempt_0/patch_0.diff",
                 "inst-3/attempt_0/patching_agent.json"]
    else:
        names = []
    return [_obj(prefix + n) for n in names]


def test_instance_id_from_either_layout():
    assert _instance_of("astropy__astropy-12907_traj.json") == "astropy__astropy-12907"
    assert _instance_of("astropy__astropy-12907.json") == "astropy__astropy-12907"
    assert _instance_of("inst-2/attempt_0/patching_agent.json") == "inst-2"


def test_local_records_cover_every_discovered_file_in_walk_order(tmp_path):
    cfg = _cfg(tmp_path)
    recs = local_records(cfg)
    root = cfg.traces_dir.resolve()
    assert [r["path"] for r in recs] == [f.resolve().relative_to(root).as_posix() for f in discover_files(cfg.traces_dir)]
    by = {r["path"]: r for r in recs}
    assert by["tau-bench/gpt-4o-airline.json"]["agent"] == "gpt-4o"
    assert by["tau2-bench/agent-x_airline.json"]["agent"] == "agent-x"
    nested = by["swe-bench/20250122_autocoderover/inst-2/attempt_0/patching_agent.json"]
    assert nested["submission"] == "20250122_autocoderover" and nested["instance"] == "inst-2"
    comp = by["swe-bench/20241016_composio_swekit/inst-1_traj.json"]
    assert comp["agent"] == "composio_swekit" and comp["instance"] == "inst-1"
    assert by["swe-bench/20240820_honeycomb/inst-9.json"]["instance"] == "inst-9"   # unparsed is still provenance
    assert all(len(r["sha256"]) == 64 and r["bytes"] > 0 for r in recs)


def test_selection_rule_is_recovered_not_assumed():
    p = "verified/s/trajs/"
    listing = [_obj(p + n) for n in ("inst-1.json", "inst-9.json", "inst-a.json")]
    assert selection(["inst-9", "inst-1"], listing, p)["rule"] == RULES[0]            # first-N, listing order
    unsorted = [_obj(p + n) for n in ("inst-9.json", "inst-1.json", "inst-5.json")]
    assert selection(["inst-1", "inst-5"], unsorted, p)["rule"] == RULES[1]           # first-N, sorted ids
    assert selection(["inst-9", "inst-1"], unsorted, p)["rule"] == RULES[0]
    gap = [_obj(p + n) for n in ("inst-1.json", "inst-5.json", "inst-9.json")]
    s = selection(["inst-1", "inst-9"], gap, p)
    assert s["rule"] is None and s["listing_positions"] == [0, 2]                     # hand-selected
    s = selection(["inst-1", "zz"], gap, p)
    assert s["rule"] is None and s["not_in_listing"] == ["zz"]
    nested = [_obj(p + n) for n in ("i2/attempt_0/a.json", "i2/attempt_0/b.diff", "i3/attempt_0/a.json")]
    s = selection(["i2"], nested, p)
    assert s["s3_instances"] == 2 and s["s3_objects"] == 3 and s["rule"] == RULES[0]


def test_build_annotates_s3_and_records_the_selection(tmp_path):
    cfg = _cfg(tmp_path)
    m = build(cfg, fake_listing, now=datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert m["schema"] == 1 and m["n_files"] == len(m["files"])
    swe = [r for r in m["files"] if r["suite"] == "swe-bench"]
    assert swe and all(r["s3"]["key"].startswith("verified/") and r["s3"]["etag"] for r in swe)
    assert all("s3" not in r for r in m["files"] if r["suite"] != "swe-bench")
    assert m["s3"]["listed_at_utc"] == "2026-09-01T00:00:00+00:00"
    sel = m["swe_bench_selection"]
    assert sel["20240820_honeycomb"] == {"n_local": 2, "s3_instances": 4, "s3_objects": 4, "rule": RULES[0],
                                         "listing_positions": [0, 1], "not_in_listing": []}
    assert sel["20250122_autocoderover"]["n_local"] == 1 and sel["20250122_autocoderover"]["s3_instances"] == 2
    assert sel["20241016_composio_swekit"]["rule"] == RULES[0]


def test_annotate_refuses_a_local_file_the_bucket_does_not_list(tmp_path):
    cfg = _cfg(tmp_path)

    def listing_without_inst9(prefix):
        return [o for o in fake_listing(prefix) if not o["key"].endswith("inst-9.json")]

    with pytest.raises(ValueError, match="swe-bench/20240820_honeycomb/inst-9.json: no such object"):
        annotate_s3(local_records(cfg), listing_without_inst9)


def test_write_load_and_a_sha_that_survives_crlf(tmp_path):
    cfg = _cfg(tmp_path)
    p = write(cfg, fake_listing)
    assert p == manifest_path(cfg) == tmp_path / "config" / "e7-manifest.json"
    m = load(cfg)
    sha = manifest_sha256(p)
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))                # a CRLF checkout
    assert manifest_sha256(p) == sha
    p.write_text(json.dumps(m, indent=1), encoding="utf-8")            # a re-serialization
    assert manifest_sha256(p) == sha
    m["files"][0]["sha256"] = "0" * 64
    p.write_text(json.dumps(m), encoding="utf-8")
    assert manifest_sha256(p) != sha


def test_no_s3_manifest_records_no_selection(tmp_path):
    cfg = _cfg(tmp_path)
    write(cfg, None)
    m = load(cfg)
    assert m["swe_bench_selection"] == {} and m["s3"]["listed_at_utc"] is None
    assert all("s3" not in r for r in m["files"])


def test_verify_disk_refuses_in_every_direction(tmp_path):
    cfg = _cfg(tmp_path)
    write(cfg, fake_listing)
    verify_disk(cfg, load(cfg))                                        # clean passes
    extra = cfg.traces_dir / "tau-bench" / "gpt-4o-retail.json"
    extra.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="not in the manifest: tau-bench/gpt-4o-retail.json"):
        verify_disk(cfg, load(cfg))
    extra.unlink()
    gone = cfg.traces_dir / "swe-bench" / "20240820_honeycomb" / "inst-9.json"
    body = gone.read_bytes()
    gone.unlink()
    with pytest.raises(ValueError, match="missing on disk: swe-bench/20240820_honeycomb/inst-9.json"):
        verify_disk(cfg, load(cfg))
    gone.write_bytes(body + b" ")                                       # one byte
    with pytest.raises(ValueError, match="does not match the manifest hash: swe-bench/20240820_honeycomb/inst-9.json"):
        verify_disk(cfg, load(cfg))
    gone.write_bytes(body)
    m = load(cfg)
    m["files"].append(dict(m["files"][0]))
    with pytest.raises(ValueError, match="twice"):
        verify_disk(cfg, m)


def test_load_refuses_absent_or_foreign_manifest(tmp_path):
    cfg = _cfg(tmp_path)
    with pytest.raises(ValueError, match="no corpus manifest"):
        load(cfg)
    manifest_path(cfg).write_text(json.dumps({"schema": 0, "files": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="not a schema-1"):
        load(cfg)


def test_driver_refuses_when_disk_disagrees_with_the_manifest(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    write(cfg, None)
    monkeypatch.setattr(driver, "assert_ready", lambda *a, **k: None)
    (cfg.traces_dir / "tau-bench" / "gpt-4o-retail.json").write_text("[]", encoding="utf-8")
    with pytest.raises(RuntimeError, match="E7 REFUSED: trace file on disk is not in the manifest"):
        driver.run(cfg, repo_root=tmp_path)
    (cfg.traces_dir / "tau-bench" / "gpt-4o-retail.json").unlink()
    out = driver.run(cfg, repo_root=tmp_path)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["manifest_sha256"] == manifest_sha256(manifest_path(cfg))


def test_gate_requires_the_manifest_committed_as_is(repo):
    """`assert_ready` treats the manifest exactly like the ledger and the config: tracked and
    byte-identical to HEAD, or the driver reads nothing."""
    cfg = _cfg(repo)
    (repo / "ledger" / "ledger.md").write_text("## Entries\n### 0006 — x\n### 0007 — y\n", encoding="utf-8")
    write(cfg, None)
    commit_all(repo, "register")
    driver.assert_ready(cfg, repo)                                     # everything committed: ready
    p = manifest_path(cfg)
    p.write_bytes(p.read_bytes() + b"\n")
    with pytest.raises(RuntimeError, match="config/e7-manifest.json is not committed as-is"):
        driver.assert_ready(cfg, repo)
    p.unlink()
    with pytest.raises(RuntimeError, match="config/e7-manifest.json is not committed as-is"):
        driver.assert_ready(cfg, repo)


def test_cli_write_and_check(tmp_path, monkeypatch, capsys):
    from linear_ceiling import REPO_ROOT
    cfg = _cfg(tmp_path)
    cfg.config_path.write_text((REPO_ROOT / "config" / "e7.toml").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(e7_manifest, "REPO_ROOT", tmp_path)           # never touch the real config/
    assert e7_manifest.main(["write", "--no-s3", "--config", str(cfg.config_path)]) == 0
    assert (tmp_path / "config" / "e7-manifest.json").exists()
    assert e7_manifest.main(["check", "--config", str(cfg.config_path)]) == 0
    assert "manifest ok" in capsys.readouterr().out
    (cfg.traces_dir / "tau-bench" / "gpt-4o-retail.json").write_text("[]", encoding="utf-8")
    assert e7_manifest.main(["check", "--config", str(cfg.config_path)]) == 1
    assert "E7 MANIFEST REFUSED" in capsys.readouterr().out
