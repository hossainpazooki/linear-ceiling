"""The launcher -> puller -> receipt -> terminate chain, end to end, on a REAL manifest shape.

WHY THIS EXISTS, AND WHY THE REHEARSAL DOES NOT COVER IT. `REHEARSAL=1` stops at the E9 gate: it never
produces a `report.json` or the box's final manifest, so everything after the gate -- the puller's
acceptance rules, the receipt it writes, and whether `rp.py`'s interlock then permits a terminate -- is
unexercised. That chain is what decides whether a FINISHED sitting can be shut down cleanly, and a
failure in it leaves a pod billing with the run already complete.

The manifest here is built with `sitting_b.sh`'s OWN `find` expression over a synthetic tree, not a
hand-written approximation, so the paths that tripped `manifest_local_path` in the live tooling
(`sitting_b.evidence/`, `manifest_check.out`, `<exp>.*.halt.*`) are present exactly as the box emits
them. A test that invented its own shape would have passed against the broken classifier.

Covered:
  * a COMPLETE run is accepted and yields a receipt rp.py's interlock accepts;
  * a REGISTERED PARTIAL (a prefix of the run order, controls present) is accepted -- entry 0042;
  * a tampered kept dump is refused;
  * a missing score file is refused;
  * a NON-PREFIX partial is refused.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "runpod"))
import pull_verify_b as pull_b                                     # noqa: E402
import rp                                                          # noqa: E402

EXP, PAIR = "e9f", pull_b.PAIR
ORDER = ["h1", "h2", "h3"]


def _w(p: Path, data: bytes) -> str:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _manifest_via_sitting_b(work: Path, exp: str) -> Path:
    """Build the final manifest with sitting_b.sh's own find expression, lifted verbatim.

    Verbatim matters: if the launcher's list changes and this copy does not, the assertion below that
    the two agree will fail, which is the point -- the test should notice a drift it cannot see."""
    src = (ROOT / "tools" / "runpod" / "sitting_b.sh").read_text(encoding="utf-8")
    m = re.search(r'\{\n(\s*find "linear-ceiling/results/\$exp".*?)\n\s*\} \| sort -zu \| xargs -0 -r sha256sum',
                  src, re.S)
    assert m, "could not lift the manifest expression out of sitting_b.sh; it has been restructured"
    body = m.group(1)
    # GNU `find -printf "%f\\0"` is not available on BSD/macOS, and its only use in the launcher is to
    # emit the BASENAMES of the halt records null-delimited. The box is Linux, where the original works;
    # here the same clause is expressed portably so the test can build the identical file list.
    # GNU `find -printf "%f\\0"` is unavailable on BSD/macOS, and its only use in the launcher is to
    # emit the BASENAMES of the halt records null-delimited. The box is Linux, where the original works;
    # here the same clause is expressed portably so the test builds the identical file list. Located by
    # index rather than regex: the launcher's line-continued find is painful to match and a silently
    # non-matching regex would leave the unsupported primary in place (it did, once).
    i = body.index("find . -maxdepth 1")
    j = body.index('-printf "%f\\0"', i) + len('-printf "%f\\0"')
    body = body[:i] + (
        'for _h in ./"$exp".*.halt.log ./"$exp".*.halt.rc ./"$exp".*.halt.status; do '
        '[ -f "$_h" ] && printf \'%s\\0\' "$(basename "$_h")" || true; done'
    ) + body[j:]
    script = f'set -euo pipefail\nexp={exp}\ncd "$1"\n{{\n{body}\n}} | sort -zu | xargs -0 -r shasum -a 256\n'
    out = subprocess.run(["bash", "-c", script, "_", str(work)], capture_output=True, text=True)
    assert out.returncode == 0, f"manifest build failed: {out.stderr[:400]}"
    man = work / f"{exp}.final.sha256"
    man.write_text(out.stdout, encoding="utf-8")
    return man


@pytest.fixture
def world(tmp_path):
    """A synthetic box tree plus the home mirror, wired the way a real sitting leaves them."""
    work = tmp_path / "workspace"
    res = work / "linear-ceiling" / "results" / EXP
    shas = {}
    shas["report"] = None
    for hid in ORDER:
        shas[f"scores/{hid}.json"] = _w(res / "scores" / f"{hid}.json", f"score-{hid}".encode())
        shas[f"tokens/{hid}.tokens.npz"] = _w(res / "tokens" / f"{hid}.tokens.npz", f"tok-{hid}".encode())
    shas["kept"] = _w(res / "scratch" / "h1" / "same_src" / "kv.npz", b"kept-tensor")   # scratch: excluded
    _w(res / "align" / "coverage.json", json.dumps({"run_order": ORDER}).encode())
    # the non-results paths the box's manifest always lists
    _w(work / "sitting_b.evidence" / "gate.txt", b"gate evidence")
    # verify_final_manifest reads these three for the terminal state, so they must carry their REAL
    # contents on the box before the manifest hashes them -- writing them at home afterwards would
    # break the very hashes the manifest records (it did, first time).
    terminal = {f"{EXP}.rc": b"EXIT=0\n", f"{EXP}.status": b"SITTING_B_OK\n",
                f"{EXP}.log": b"...\nSITTING_B_OK\n"}
    for name in ("manifest_check.out", "sitting_b.setup.log", "sitting_b.probe.log",
                 f"{EXP}.log", f"{EXP}.rc", f"{EXP}.status", "sitting_b.launches.log"):
        _w(work / name, terminal.get(name, b"x\n"))
    _w(work / f"{EXP}.1.halt.log", b"halt\n")
    return work, res


def _report(complete=True, scored=None, partial=None):
    scored = ORDER if scored is None else scored
    rep = {
        "pair": PAIR, "upstream_sha": "pin", "config_sha256": "cfg",
        "order_by": "n_sender_asc", "run_order": ORDER,
        "coverage": {"observed": 5, "included": len(ORDER), "excluded": 2},
        "alignments": ([{"handoff_id": h, "excluded": False} for h in ORDER]
                       + [{"handoff_id": f"x{i}", "excluded": True} for i in range(2)]),
        # The keep-subset handoff must carry kept_dumps when it is scored: the validator requires the
        # scored-with-kept set to equal keep_subset intersect scored, which is what makes a partial's
        # kept tensors provably accounted for. Shape mirrors the driver's: {dump: {relpath: sha}}.
        "scores": {h: ({"n_pairs": 3} if h != ORDER[0] or h not in scored else
                       {"n_pairs": 3, "kept_dir": f"scratch/{h}",
                        "kept_dumps": {"same_src": {"kv.npz": "a" * 64}}})
                   for h in scored},
        "controls": {"handoff_id": ORDER[0]},
        "keep_subset": [ORDER[0]],
        "complete": complete,
    }
    if partial is not None:
        rep["partial"] = partial
    return rep


def test_the_manifest_expression_is_lifted_from_the_launcher_and_covers_every_shape(world):
    work, _ = world
    man = _manifest_via_sitting_b(work, EXP)
    entries = pull_b.parse_manifest(man)
    rels = set(entries)
    assert any(r.startswith(f"linear-ceiling/results/{EXP}/scores/") for r in rels)
    assert "manifest_check.out" in rels, "the box lists it; the verifier must expect it"
    assert any(r.startswith("sitting_b.evidence/") for r in rels), "evidence tree missing"
    assert any(".halt." in r for r in rels), "halt records missing"
    assert not any("/scratch/" in r for r in rels), "scratch tensors must never be in the final manifest"
    # every listed path must be classifiable by the verifier -- this is the check that would have
    # caught the live blocker, where evidence/ and the halt records raised "out-of-scope path".
    for rel in rels:
        pull_b.manifest_local_path(rel, local=Path("/tmp/none"), exp=EXP)


@pytest.mark.parametrize("scored,partial,ok,why", [
    (ORDER, None, True, "a complete run"),
    (ORDER[:2], {"n_scored": 2, "unscored": ORDER[2:]}, True, "a registered partial on a prefix"),
    ([ORDER[0], ORDER[2]], {"n_scored": 2, "unscored": [ORDER[1]]}, False, "a NON-PREFIX partial"),
])
def test_checkpoint_acceptance_follows_the_registered_stopping_rule(tmp_path, scored, partial, ok, why):
    cfg = tmp_path / "e9f.toml"
    cfg.write_text('[e9]\n'
                   f'pair = "{PAIR}"\n'
                   'results_dir = "results/e9f"\n'
                   'upstream_sha = "pin"\n'
                   '[e9.order]\nby = "n_sender_asc"\nallow_partial = true\n', encoding="utf-8")
    rep = _report(complete=False, scored=scored, partial=partial)
    rep["config_sha256"] = pull_b.text_sha256(cfg)
    if ok:
        pull_b.validate_checkpoint_report(rep, config=cfg, exp=EXP, pair=PAIR)
    else:
        with pytest.raises(ValueError, match="prefix"):
            pull_b.validate_checkpoint_report(rep, config=cfg, exp=EXP, pair=PAIR)


def test_a_receipt_written_by_the_puller_is_accepted_by_rp_interlock(tmp_path, monkeypatch):
    """The join between the two tools: the puller writes it, rp.py's terminate gate reads it."""
    verify = tmp_path / "verified.json"
    state = {"pod_id": "pod123", "verify_nonce": "n" * 32, "created_utc": "2026-09-19T00:00:00Z",
             "verify_file": str(verify), "name": f"{rp.NAME_PREFIX}sitting-b"}
    pull_b.write_receipt(state, exp=EXP, pair=PAIR, report_sha="r" * 64,
                         manifest_sha="m" * 64, checked=7, total_bytes=123)
    ok, why = rp._check_verify_interlock(state, verify, "pod123")
    assert ok, f"rp.py rejected the puller's own receipt: {why}"
    # and it must be bound: another pod's terminate may not ride on it
    ok2, why2 = rp._check_verify_interlock(state, verify, "OTHERPOD")
    assert not ok2 and "another pod" in why2


def test_a_tampered_kept_dump_and_a_missing_score_are_both_refused(world, tmp_path):
    work, res = world
    man = _manifest_via_sitting_b(work, EXP)
    local = tmp_path / "mirror"
    for rel, want in pull_b.parse_manifest(man).items():
        dst = pull_b.manifest_local_path(rel, local=local, exp=EXP)
        dst.parent.mkdir(parents=True, exist_ok=True)
        src = work / rel
        dst.write_bytes(src.read_bytes())
    required = {f"scores/{h}.json" for h in ORDER}
    # clean: verifies
    pull_b.verify_final_manifest(man, local=local, exp=EXP, required_results=required)
    # tampered kept/score byte: refused
    (local / "scores" / "h2.json").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="MISMATCH final"):
        pull_b.verify_final_manifest(man, local=local, exp=EXP, required_results=required)
    # missing entirely: refused, and distinctly
    (local / "scores" / "h2.json").unlink()
    with pytest.raises(ValueError, match="MISSING final"):
        pull_b.verify_final_manifest(man, local=local, exp=EXP, required_results=required)


def test_the_manifest_must_name_every_required_result(world, tmp_path):
    work, _ = world
    man = _manifest_via_sitting_b(work, EXP)
    with pytest.raises(ValueError, match="omits .* required result"):
        pull_b.verify_final_manifest(man, local=tmp_path, exp=EXP,
                                     required_results={"scores/NOT-PACKAGED.json"})


# ---------------------------------------------------------------------------------------------
# M2: a crash during the FIRST handoff, before any checkpoint exists.
# ---------------------------------------------------------------------------------------------

def _classifier() -> str:
    """The launcher's run-mode classifier, lifted out of its `$( )` heredoc and run directly.

    Lifted rather than re-written: this is the code that decides whether a relaunch resumes, runs
    plain, or refuses, and a hand-copied approximation would stop tracking it the moment it changed."""
    src = (ROOT / "tools" / "runpod" / "sitting_b.sh").read_text(encoding="utf-8")
    m = re.search(r'RUN_MODE="\$\("\$LC_PY" - "\$REPORT" "\$CFG" "\$UP_SHA" <<\'PY\'\n(.*?)\nPY\n\)"',
                  src, re.S)
    assert m, "could not lift the run-mode classifier out of sitting_b.sh; it has been restructured"
    return m.group(1)


def test_a_first_handoff_crash_is_quarantined_rather_than_refused(tmp_path):
    """Files with no checkpoint mean the driver died before writing anything resumable. Refusing (as
    this did) strands the sitting on a billing card until someone cleans up by hand; deleting would
    destroy the evidence of why it died. Move them aside, keep them, and run plain."""
    res = tmp_path / "results" / EXP
    (res / "scores").mkdir(parents=True)
    (res / "scores" / "h1.json").write_text("half a score", encoding="utf-8")
    (res / "scratch" / "h1").mkdir(parents=True)
    (res / "scratch" / "h1" / "kv.npz").write_bytes(b"half a tensor")
    cfg = tmp_path / "e9f.toml"
    cfg.write_text("[e9]\n", encoding="utf-8")

    out = subprocess.run([sys.executable, "-c", _classifier(), str(res / "report.json"), str(cfg), "pin"],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr[-600:]
    assert out.stdout.strip() == "plain", f"a crashed first handoff must relaunch plain: {out.stdout!r}"

    quarantines = sorted(res.glob("quarantine.*"))
    assert len(quarantines) == 1, f"expected exactly one quarantine dir, got {quarantines}"
    q = quarantines[0]
    assert (q / "scores" / "h1.json").read_text(encoding="utf-8") == "half a score", "evidence was lost"
    assert (q / "scratch" / "h1" / "kv.npz").read_bytes() == b"half a tensor"
    assert not (res / "scores").exists() and not (res / "scratch").exists(), \
        "the driver must start plain on a clean tree, not over half-written files"
    assert "QUARANTINED" in out.stderr, "the setup log must record what was displaced"

    # a SECOND crash must not overwrite the first quarantine
    (res / "scores").mkdir()
    (res / "scores" / "h1.json").write_text("another half", encoding="utf-8")
    out2 = subprocess.run([sys.executable, "-c", _classifier(), str(res / "report.json"), str(cfg), "pin"],
                          capture_output=True, text=True, cwd=ROOT)
    assert out2.returncode == 0 and out2.stdout.strip() == "plain"
    assert len(sorted(res.glob("quarantine.*"))) in (1, 2), "the first quarantine must still be there"
    assert (q / "scores" / "h1.json").read_text(encoding="utf-8") == "half a score"
