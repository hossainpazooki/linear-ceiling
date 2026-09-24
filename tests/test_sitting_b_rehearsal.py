"""M6: the sitting-B chain rehearsed end to end, in the three ways a sitting can actually end.

WHY A REHEARSAL AND NOT MORE UNIT TESTS. Every piece of this chain has tests. What none of them
exercise is the chain: a stub driver writing real checkpoints into a real directory tree, the puller
reading them over a transport that runs the actual shell command strings, the receipt, rp.py's
interlock, and the close. Both live blockers found on 2026-09-18 -- the launcher's `SITTING_B_OK`
timestamp that no verifier would ever match, and the `[ -f x ] && stat` loop that exited 1 whenever
the final manifest was absent -- lived precisely in that seam, and passed every unit test there was.

`REHEARSAL=1` in sitting_b.sh stops at the E9 gate: it never produces a report.json, kept tensors, a
final manifest or a terminal status, so everything after the gate is what this file covers instead.

The three endings, which are the three the runbook and entry 0042 contemplate:

  1. COMPLETE          -- the driver finishes, the launcher writes the manifest and SITTING_B_OK, the
                          puller verifies every byte and writes a receipt rp.py accepts.
  2. DRAIN -> PARTIAL  -- the driver is stopped BY SIGNAL between handoffs at the budget threshold.
                          The last checkpoint is intact, every tensor it names is already home, and
                          --final-partial closes on it. This is the intended stop.
  3. HARD KILL         -- the ceiling fires mid-handoff. report.json names a kept dump that never
                          arrived and the box disk is gone. The close falls back to the last verified
                          B5 snapshot, and `e9 --close-partial` stamps that prefix.

WHAT IS AND IS NOT VERBATIM. LocalTransport runs the puller's own command strings through bash. Two
of them use GNU primaries macOS does not have (`stat` formats and `find -printf`), so ON DARWIN ONLY
those two are translated to BSD equivalents, with the command's shape asserted first so a production
command that changes form fails loudly instead of quietly diverging. On Linux the commands are passed
through UNTOUCHED, which makes CI the Linux rehearsal this machine cannot be.

THAT DISTINCTION IS NOT PEDANTRY -- it was a live blocker. The translation was originally
unconditional, and BSD `stat -f` interprets backslash escapes while GNU `stat -c` does NOT. So the Mac
rehearsal silently made a broken command work: on the real box `stat -c '%s\t...'` returns a literal
backslash-t, the parser raises "not enough values to unpack" on the first workspace file, and EVERY
round of the puller dies -- no kept dump ever comes home. A translation layer that is more capable
than the thing it stands in for does not hide a bug, it manufactures a pass.
"""
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "runpod"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pull_verify_b as pull_b                                      # noqa: E402
import rp                                                           # noqa: E402
from linear_ceiling.e9 import close_partial                         # noqa: E402
from test_runpod_b_contract import _manifest_via_sitting_b          # noqa: E402

EXP, PAIR = "e9f", pull_b.PAIR
ORDER = ["h1", "h2", "h3", "h4", "h5"]
KEEP = ["h1", "h3", "h5"]
POD = "podREHEARSAL"


# --------------------------------------------------------------------------------- the transport

class LocalTransport:
    """The puller's own commands, run by bash against a local directory that stands in for the box."""

    # The trailing `|| true` is deliberately OPTIONAL in this pattern. It is the B2 fix, and if the
    # pattern required it, removing it again would fail here as "the command changed shape" instead of
    # reproducing what it actually does: the loop exits 1 on the absent final manifest and every
    # mid-run round dies. Matching both forms makes the rehearsal reproduce the bug rather than
    # merely notice the edit. Everything else about the command is pinned.
    GNU_STAT = re.compile(r"^for f in (.*); do \[ -f \"\$f\" \] && "
                          r"stat --printf '%s\\t%Y\\t%n\\n' \"\$f\"( \|\| true)?; done$")
    GNU_FIND = re.compile(r"^cd (\S+) 2>/dev/null && find \. -type f -printf '%s\\t%T@\\t%P\\0' \|\| true$")

    def __init__(self, box: Path) -> None:
        self.box = box
        self.seen: list[str] = []

    def _translate(self, command: str) -> str:
        """On Darwin, BSD equivalents for the two GNU-only commands, shape asserted before rewriting.

        On Linux the command is returned UNCHANGED: CI is then running the genuine GNU commands, which
        is the only place that happens before the box. The shape assertion is the point on Darwin: if
        `mirror_workspace_files` or `remote_small_listing` is ever rewritten, this stops matching and
        the rehearsal fails, rather than testing a command the tool no longer sends."""
        if platform.system() != "Darwin":
            return command
        m = self.GNU_STAT.match(command)
        if m:
            tail = m.group(2) or ""
            return (f"for f in {m.group(1)}; do [ -f \"$f\" ] && "
                    f"stat -f '%z\t%m\t%N' \"$f\"{tail}; done")
        m = self.GNU_FIND.match(command)
        if m:
            d = m.group(1)
            # A real TAB is embedded (not a literal backslash-t): BSD sed does not interpret
            # \t in a pattern, so the separator has to arrive as the character itself.
            return (f"cd {d} 2>/dev/null && find . -type f -exec "
                    "stat -f '%z\t%m\t%N' {} \\; | sed 's|\t\\./|\t|' | tr '\\n' '\\0' || true")
        assert "-printf" not in command and "stat -c" not in command, \
            f"an untranslated GNU-only command reached the rehearsal transport: {command!r}"
        return command

    def run_bytes(self, command: str, *, timeout: int = 120) -> bytes:
        self.seen.append(command)
        proc = subprocess.run(["bash", "-c", self._translate(command)],
                              capture_output=True, timeout=timeout)
        if proc.returncode:
            raise RuntimeError(f"remote command rc={proc.returncode}: "
                               f"{proc.stderr.decode('utf-8', 'replace')[-400:]}")
        return proc.stdout

    def stream_tar(self, remote_dir: str, names: list[str], local_dir: Path, *, timeout: int = 7200) -> None:
        if not names:
            return
        for name in names:
            pull_b.safe_rel(name, what="tar member")
        local_dir.mkdir(parents=True, exist_ok=True)
        cmd = (f"cd {shlex.quote(remote_dir)} && tar -cf - -- "
               + " ".join(shlex.quote(x) for x in names)
               + f" | tar -xf - --no-same-owner -C {shlex.quote(str(local_dir))}")
        proc = subprocess.run(["bash", "-c", cmd], capture_output=True, timeout=timeout)
        if proc.returncode:
            raise RuntimeError(f"tar stream failed: {proc.stderr.decode('utf-8', 'replace')[-400:]}")

    def remove_verified_tree(self, remote_path: str, remote_results: str) -> None:
        from pathlib import PurePosixPath
        p, root = PurePosixPath(remote_path), PurePosixPath(remote_results)
        if (not p.is_absolute() or not root.is_absolute()
                or p.parent != root / "scratch" or p.name in ("", ".", "..", "scratch")):
            raise ValueError(f"refusing unsafe deletion target {remote_path!r}")
        q = shlex.quote(remote_path)
        self.run_bytes(f"rm -rf -- {q} && test ! -e {q}", timeout=300)


# ------------------------------------------------------------------------------- the stub driver

class StubDriver:
    """Writes the checkpoint shapes the real E9 driver writes, in the registered order.

    It is deliberately NOT a mock of the driver's arithmetic: what this rehearsal tests is the file
    protocol between driver, puller and closer -- checkpoint after each handoff, kept tensors for the
    keep subset, controls attached to run_order[0] -- not what is inside a score file."""

    def __init__(self, box: Path, cfg: Path) -> None:
        self.res = box / "linear-ceiling" / "results" / EXP
        self.cfg = cfg
        (self.res / "align").mkdir(parents=True, exist_ok=True)
        (self.res / "align" / "coverage.json").write_text(
            json.dumps({"run_order": ORDER}), encoding="utf-8")
        for hid in ORDER + ["x0"]:
            (self.res / "align" / f"{hid}.json").write_text("{}", encoding="utf-8")
            (self.res / "align" / f"{hid}.npz").write_bytes(f"align-{hid}".encode())
        self.report = {
            "pair": PAIR, "upstream_sha": "pin", "config_sha256": pull_b.text_sha256(cfg),
            "order_by": "n_sender_asc", "run_order": ORDER,
            "coverage": {"observed": len(ORDER) + 1, "included": len(ORDER), "excluded": 1},
            "alignments": ([{"handoff_id": h, "excluded": False} for h in ORDER]
                           + [{"handoff_id": "x0", "excluded": True}]),
            "scores": {}, "controls": None, "keep_subset": KEEP, "complete": False,
        }

    # -- the driver's own atomic checkpoint write, mirrored here on purpose
    def _checkpoint(self) -> None:
        out = self.res / "report.json"
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(json.dumps(self.report, indent=1), encoding="utf-8")
        os.replace(tmp, out)

    def _w(self, rel: str, data: bytes) -> str:
        import hashlib
        p = self.res / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def run(self, n: int, *, withhold_last_tensor: bool = False) -> None:
        """Score the first `n` handoffs. `withhold_last_tensor` is the hard-kill shape: the checkpoint
        names a kept dump whose bytes never reach the disk the puller can see."""
        for i, hid in enumerate(ORDER[:n]):
            if i == 0:
                controls = {"handoff_id": hid}
                for arm in ("identity", "prefix", "null"):
                    controls[arm] = {
                        "score_file": f"{arm}.json",
                        "score_sha256": self._w(f"controls/{arm}.json", f"c-{arm}".encode()),
                        "tokens_file": f"{arm}.npz",
                        "tokens_sha256": self._w(f"controls/{arm}.npz", f"ct-{arm}".encode()),
                    }
                self.report["controls"] = controls
            rec = {
                "score_file": f"{hid}.json",
                "score_sha256": self._w(f"scores/{hid}.json", f"score-{hid}".encode()),
                "tokens_file": f"{hid}.tokens.npz",
                "tokens_sha256": self._w(f"tokens/{hid}.tokens.npz", f"tok-{hid}".encode()),
            }
            if hid in KEEP:
                import hashlib
                payload = f"kv-{hid}".encode()
                rec["kept_dir"] = f"scratch/{hid}"
                last = withhold_last_tensor and i == n - 1
                digest = (hashlib.sha256(payload).hexdigest() if not last
                          else self._w(f"scratch/{hid}/same_src/kv.npz", payload))
                if not last:
                    self._w(f"scratch/{hid}/same_src/kv.npz", payload)
                rec["kept_dumps"] = {"same_src": {"kv.npz": digest}}
                if last:
                    # the bytes exist on the box for an instant and then the card is destroyed
                    (self.res / f"scratch/{hid}/same_src/kv.npz").unlink()
            self.report["scores"][hid] = rec
            self._checkpoint()

    def finish(self, box: Path) -> None:
        """What the launcher does after a driver rc == 0: terminal bytes first, then hash them."""
        self.report["complete"] = True
        self._checkpoint()
        (box / f"{EXP}.rc").write_text("EXIT=0\n", encoding="utf-8")
        (box / f"{EXP}.status").write_text("SITTING_B_OK\n", encoding="utf-8")
        (box / f"{EXP}.log").write_text("[2026-09-19T01:00:00Z] SITTING_B_OK\n", encoding="utf-8")
        for name in ("manifest_check.out", "sitting_b.setup.log", "sitting_b.probe.log",
                     "sitting_b.launches.log"):
            (box / name).write_text("x\n", encoding="utf-8")
        (box / "sitting_b.evidence").mkdir(exist_ok=True)
        (box / "sitting_b.evidence" / "gate.txt").write_text("gate\n", encoding="utf-8")
        _manifest_via_sitting_b(box, EXP)

    def fail(self, box: Path, rc: int) -> None:
        (box / f"{EXP}.rc").write_text(f"EXIT={rc}\n", encoding="utf-8")
        (box / f"{EXP}.status").write_text(f"SITTING_B_FAILED rc={rc}\n", encoding="utf-8")
        (box / f"{EXP}.log").write_text(f"[2026-09-19T01:00:00Z] SITTING_B_FAILED rc={rc}\n", encoding="utf-8")


# ------------------------------------------------------------------------------------- the world

@pytest.fixture
def world(tmp_path):
    box = tmp_path / "workspace"
    (box / "linear-ceiling" / "results" / EXP).mkdir(parents=True)
    cfg = tmp_path / "e9f.toml"
    cfg.write_text('[e9]\n'
                   f'pair = "{PAIR}"\n'
                   'results_dir = "results/e9f"\n'
                   'upstream_sha = "pin"\n'
                   '[e9.order]\nby = "n_sender_asc"\nallow_partial = true\n', encoding="utf-8")
    local = tmp_path / "home" / "results" / EXP
    local.mkdir(parents=True)
    verify = tmp_path / "verified.json"
    runpod_state = {"pod_id": POD, "verify_nonce": "n" * 32, "created_utc": "2026-09-19T00:00:00Z",
                    "verify_file": str(verify), "name": f"{rp.NAME_PREFIX}sitting-b"}
    args = pull_b.build_parser().parse_args([
        "--local", str(local), "--config", str(cfg),
        "--remote-results", str(box / "linear-ceiling" / "results" / EXP),
        "--remote-work", str(box), "--delete-verified",
        # never the operator's real cache: the default path is a live file the watchdog reads
        "--drain-hint", str(tmp_path / "drain-hint.json"),
    ])
    driver = StubDriver(box, cfg)
    # The home mirror carries its own alignments (the box verifies against them); copy them across so
    # the closer has what summarize_e9 will need, exactly as `e9 --align-only` leaves them at home.
    subprocess.run(["cp", "-a", str(driver.res / "align"), str(local / "align")], check=True)
    return types.SimpleNamespace(box=box, cfg=cfg, local=local, verify=verify, args=args,
                                 runpod_state=runpod_state, driver=driver,
                                 tx=LocalTransport(box), state={})


def _round(w) -> bool:
    return pull_b.run_round(w.args, w.tx, w.state, w.runpod_state)


# ------------------------------------------------------------------------------ scenario 1: done

def test_scenario_1_a_complete_run_is_pulled_verified_receipted_and_terminable(world, monkeypatch):
    w = world
    # rounds while the driver works: nothing is complete, and each one must survive the ABSENT
    # final manifest -- the blocker that killed every mid-run round.
    for n in (1, 3):
        w.driver.run(n)
        assert _round(w) is False
        snaps = sorted(p.name for p in (w.local / "checkpoints").glob("report.*.json"))
        assert f"report.{n}.json" in snaps, f"no verified snapshot after {n} scored: {snaps}"
    # verified kept trees are gone from the box, which is what keeps its disk from filling
    assert not (w.driver.res / "scratch" / "h1").exists()

    w.driver.run(len(ORDER))
    w.driver.finish(w.box)
    assert _round(w) is True, "a complete, fully verified run must be accepted"

    receipt = json.loads(w.verify.read_text(encoding="utf-8"))
    assert receipt["final_manifest_sha256"] and "partial" not in receipt
    ok, why = rp._check_verify_interlock(w.runpod_state, w.verify, POD)
    assert ok, f"rp.py rejected the receipt the puller just wrote: {why}"


# --------------------------------------------------------------- scenario 2: drain -> partial

def test_scenario_2_a_drained_run_closes_on_its_last_intact_checkpoint(world, monkeypatch, capsys):
    """The intended budget stop: the driver is signalled between handoffs, so the last checkpoint is
    whole and every tensor it names is already home. Nothing is edited; the live report.json is the
    basis, and `e9 --close-partial` stamps it."""
    w = world
    w.driver.run(3)
    assert _round(w) is False
    # the drain: the driver stops between handoffs. No rc, no manifest, no SITTING_B_OK.
    assert not (w.box / f"{EXP}.final.sha256").exists()

    monkeypatch.setattr(pull_b.rp, "pods", lambda: [{"id": POD, "name": f"{rp.NAME_PREFIX}sitting-b"}])
    monkeypatch.setattr(pull_b, "Transport", lambda *_a, **_k: types.SimpleNamespace(
        run_bytes=lambda *_x, **_y: b"STOPPED 4242\n"))
    assert pull_b.final_partial(w.args, w.runpod_state) == 0
    assert not list(w.local.glob("report.superseded-*.json")), \
        "a graceful drain leaves report.json usable; nothing should have been superseded"

    receipt = json.loads(w.verify.read_text(encoding="utf-8"))
    assert receipt["partial"]["n_scored"] == 3 and receipt["partial"]["unscored"] == ORDER[3:]
    ok, why = rp._check_verify_interlock(w.runpod_state, w.verify, POD)
    assert ok, why

    closed = close_partial(types.SimpleNamespace(
        allow_partial=True, results_dir=w.local, config_path=w.cfg))
    rep = json.loads(closed.read_text(encoding="utf-8"))
    assert rep["complete"] is True
    assert rep["partial"]["n_scored"] == 3 and rep["partial"]["unscored"] == ORDER[3:]
    assert list(rep["scores"]) == ORDER[:3], "the closed set must be the registered prefix"

    # and the closed shape must not be mistaken for a complete run by the normal path
    with pytest.raises(ValueError, match="CLOSED PARTIAL"):
        pull_b.validate_complete_report(rep, config=w.cfg, exp=EXP, pair=PAIR)


# ------------------------------------------------------ scenario 3: hard kill -> snapshot -> close

def test_scenario_3_a_hard_kill_closes_on_the_last_verified_snapshot(world, monkeypatch):
    """The ceiling fires mid-handoff. report.json names a kept dump that never arrived and the box is
    destroyed, so the live report is unusable -- but the B5 snapshot of the previous prefix is whole,
    and that is a genuine driver checkpoint and a prefix of the registered order."""
    w = world
    w.driver.run(3)
    assert _round(w) is False
    assert (w.local / "checkpoints" / "report.3.json").is_file()

    # handoff 4 starts; h5 is next in the keep subset, so score 5 with its tensor withheld
    w.driver.run(5, withhold_last_tensor=True)
    _round(w)                                        # pulls what it can; h5's tensor cannot verify
    assert not (w.local / "checkpoints" / "report.5.json").exists(), \
        "a checkpoint naming an unverifiable tensor must never be snapshotted"

    # the kill: the pod and its disk are gone
    subprocess.run(["rm", "-rf", str(w.box)], check=True)
    monkeypatch.setattr(pull_b.rp, "pods", lambda: [])

    assert pull_b.final_partial(w.args, w.runpod_state) == 0
    superseded = list(w.local.glob("report.superseded-*.json"))
    assert len(superseded) == 1, "the unusable live report must be kept as evidence, not deleted"
    assert json.loads(superseded[0].read_text(encoding="utf-8"))["scores"].keys() >= {"h5"}

    installed = json.loads((w.local / "report.json").read_text(encoding="utf-8"))
    assert list(installed["scores"]) == ORDER[:3]

    receipt = json.loads(w.verify.read_text(encoding="utf-8"))
    assert receipt["partial"]["basis"] == "checkpoints/report.3.json"
    assert receipt["partial"]["n_scored"] == 3

    closed = close_partial(types.SimpleNamespace(
        allow_partial=True, results_dir=w.local, config_path=w.cfg))
    rep = json.loads(closed.read_text(encoding="utf-8"))
    assert rep["complete"] is True and list(rep["scores"]) == ORDER[:3]
    # every byte the closed report names is present and correct at home -- the whole point
    bad, checked, _ = pull_b.verify_artifacts(w.local, pull_b.report_artifacts(rep))
    assert not bad and checked == len(pull_b.report_artifacts(rep))


# --------------------------------------------------------------------- the fourth way it can end

def test_a_launcher_failure_is_noticed_rather_than_polled_through(world):
    """Not one of the three closes, but the same seam: the box gives up and the puller must too."""
    w = world
    w.driver.run(2)
    assert _round(w) is False
    w.driver.fail(w.box, 95)
    with pytest.raises(pull_b.BoxFailed, match="rc=95"):
        _round(w)


# ---------------------------------------------------------------------------------------------
# UNATTENDED. Both sessions hit their limit at 23:35 on 2026-09-18 and went dark for three hours.
# If that happens mid-run, these paths must finish the sitting with nobody watching.
# ---------------------------------------------------------------------------------------------

def test_a_drained_run_closes_itself_with_nobody_watching(world, monkeypatch):
    """A drain and a crash arrive IDENTICALLY: the watchdog SIGTERMs the driver, the driver exits
    non-zero, and the launcher writes `SITTING_B_FAILED rc=143`. So one unattended path serves both.

    What must not happen is the loop noticing the terminal status and returning, leaving the pod to
    idle at the full card rate until the spend ceiling kills it hours later -- with the tensors the
    launcher wrote in its last seconds destroyed along with it."""
    w = world
    w.driver.run(2)
    assert _round(w) is False

    # handoff 3 completes on the box, and only THEN does the drain land
    w.driver.run(3)
    w.driver.fail(w.box, 143)                       # SIGTERM: 128 + 15

    terminated = {"n": 0}
    monkeypatch.setattr(pull_b.rp, "pods", lambda: [{"id": POD, "name": f"{rp.NAME_PREFIX}sitting-b"}])
    monkeypatch.setattr(pull_b, "Transport", lambda *_a, **_k: types.SimpleNamespace(
        run_bytes=lambda *_x, **_y: b"STOPPED 4242\n"))      # the pod is up, the driver pid is dead
    monkeypatch.setattr(pull_b.rp, "cmd_terminate", lambda ns: terminated.update(n=1) or 0)
    a = w.args
    a.terminate_on_receipt = True

    # drive the loop the way main() does, so the BoxFailed handler is the thing under test
    rc = None
    try:
        _round(w)
    except pull_b.BoxFailed as e:
        a._ignore_box_status = True
        for _ in range(2):
            try:
                pull_b.run_round(a, w.tx, w.state, w.runpod_state)
            except Exception:
                pass
        rc = pull_b.final_partial(a, w.runpod_state)
    assert rc == 0, "a drained sitting must close itself on its verified prefix"

    receipt = json.loads(w.verify.read_text(encoding="utf-8"))
    assert receipt["partial"]["n_scored"] == 3, \
        "handoff 3 landed before the drain and must be IN the close, not lost to it"
    assert receipt["partial"]["unscored"] == ORDER[3:]
    assert terminated["n"] == 1, "the pod must be terminated once the receipt exists, not left idling"


def test_the_terminal_sweep_rescues_what_the_launcher_wrote_last(world, monkeypatch):
    """The round that notices the terminal status must still PULL. The launcher's final writes are on
    a disk the terminate is about to destroy, so skipping that sweep loses exactly the handoff the
    drain was timed to preserve."""
    w = world
    w.driver.run(2)
    assert _round(w) is False
    n_before = len(list((w.local / "scores").glob("*.json")))

    w.driver.run(3)                                  # h3 exists on the box but has never been pulled
    w.driver.fail(w.box, 143)
    with pytest.raises(pull_b.BoxFailed):
        _round(w)
    n_after = len(list((w.local / "scores").glob("*.json")))
    assert n_after == n_before + 1, \
        f"the terminal round pulled nothing ({n_before} -> {n_after}); h3 would have died with the pod"
    assert (w.local / "checkpoints" / "report.3.json").is_file(), \
        "and it must snapshot that prefix, which is what the close will run on"


def test_the_workspace_listing_uses_printf_because_stat_c_does_not_interpret_escapes():
    """GNU `stat -c/--format` does NOT interpret backslash escapes; only `--printf` does.

    With `-c '%s\\t%Y\\t%n'` the box returns a LITERAL backslash-t, `line.split("\\t", 2)` raises
    "not enough values to unpack" on the first workspace file, and every round of the puller dies --
    so no kept dump ever comes home and a drain closes on nothing. It shipped that way and was
    invisible here, because the Darwin shim rewrote it to BSD `stat -f`, which DOES interpret escapes.

    Pinned as source text rather than behaviour on purpose: this machine cannot execute the GNU form,
    so the only check available here is that the command asks for escape interpretation. Linux CI runs
    the real thing (the shim is Darwin-only)."""
    src = (ROOT / "tools" / "runpod" / "pull_verify_b.py").read_text(encoding="utf-8")
    listing = [ln for ln in src.splitlines() if "stat" in ln and "%s" in ln and not ln.lstrip().startswith("#")]
    assert listing, "the workspace listing command has moved; re-pin it here"
    for ln in listing:
        assert "stat --printf" in ln, f"stat format without escape interpretation: {ln.strip()}"
        assert "stat -c" not in ln and "stat --format" not in ln, f"-c/--format cannot expand \\t: {ln.strip()}"
        assert "\\\\n" in ln, f"--printf adds no trailing newline, so the format must: {ln.strip()}"
