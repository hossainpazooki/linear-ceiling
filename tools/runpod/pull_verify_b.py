"""Incrementally mirror and verify RunPod Sitting B (E9F) before ephemeral-disk release.

The E9 driver checkpoints ``report.json`` after each handoff.  For every checkpoint this program
mirrors the small records, pulls any report-named kept tensor directory, hashes every named byte at
home, and *optionally* deletes that one remote directory only after the hashes agree.  It is safe to
restart: its state is bound to the current RunPod pod id and verification nonce, while all deletion
decisions are made again from raw local bytes rather than trusted from the state file.

Completion is deliberately stronger than ``report.complete``.  The report must describe exactly the
registered score set, every report fingerprint must match at home, and the launcher's atomically
written ``/workspace/<exp>.final.sha256`` must cover and match every non-scratch result plus the final
logs/status.  Only then is a nonce- and pod-bound JSON receipt written at the ``--verify-file`` path
stored by :mod:`tools.runpod.rp`; that receipt is what makes a normal ``rp.py terminate`` safe.

The default pod-name check makes accidentally pointing this at the live Sitting A pod a refusal.

Typical use (start beside the detached driver; deletion is opt-in)::

    .venv/bin/python tools/runpod/pull_verify_b.py --delete-verified

Use ``--once`` for a supervisor-driven polling loop.  This tool never terminates a pod.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rp  # noqa: E402  (sibling script; supplies the one mapped-SSH authority)


EXP = "e9f"
PAIR = "llama3.2-3b-to-llama3.1-8b"
POD_NAME = "linear-ceiling-sitting-b"
RECEIPT_SCHEMA = rp.VERIFY_RECEIPT_SCHEMA
FINAL_LOGS = (
    "sitting_b.setup.log",
    "sitting_b.probe.log",
    "{exp}.log",
    "{exp}.rc",
    "{exp}.status",
    "sitting_b.launches.log",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sha256(path: Path) -> str:
    # Universal-newline reading is the experiment's sha256_text_file convention.
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def _atomic_json(path: Path, obj: dict, *, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if mode is not None:
        tmp.chmod(mode)
    tmp.replace(path)


def safe_rel(value: str, *, what: str = "path") -> str:
    """Return a canonical safe POSIX relative path or refuse traversal/ambiguous spellings."""
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError(f"{what} is empty or not a string")
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        raise ValueError(f"unsafe {what}: {value!r}")
    canonical = p.as_posix()
    if canonical != value:
        raise ValueError(f"non-canonical {what}: {value!r}")
    return canonical


def _digest(value: object, *, what: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{what} is not a sha256")
    try:
        int(value, 16)
    except ValueError as e:
        raise ValueError(f"{what} is not a sha256") from e
    return value.lower()


@dataclass(frozen=True)
class Artifact:
    label: str
    rel: str
    digest: str


def _artifact(out: dict[str, Artifact], label: str, rel: str, digest: object) -> None:
    rel = safe_rel(rel, what=f"{label} path")
    item = Artifact(label, rel, _digest(digest, what=f"{label} digest"))
    prior = out.get(rel)
    if prior is not None and prior.digest != item.digest:
        raise ValueError(f"report assigns conflicting hashes to {rel}")
    out[rel] = item


def report_artifacts(report: dict) -> list[Artifact]:
    """All report-fingerprinted files, including controls and any bridge records."""
    out: dict[str, Artifact] = {}
    scores = report.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("report.scores is not an object")
    for hid, rec in scores.items():
        if not isinstance(rec, dict):
            raise ValueError(f"score record {hid!r} is not an object")
        _artifact(out, f"score {hid}", f"scores/{safe_rel(rec.get('score_file'), what='score_file')}",
                  rec.get("score_sha256"))
        _artifact(out, f"tokens {hid}", f"tokens/{safe_rel(rec.get('tokens_file'), what='tokens_file')}",
                  rec.get("tokens_sha256"))
        kept = rec.get("kept_dumps")
        if kept is not None:
            kept_dir = safe_rel(rec.get("kept_dir"), what=f"kept_dir {hid}")
            if not kept_dir.startswith("scratch/"):
                raise ValueError(f"score {hid!r} kept_dir is outside scratch/: {kept_dir}")
            if not isinstance(kept, dict) or not kept:
                raise ValueError(f"score {hid!r} has an empty/malformed kept_dumps")
            for dump_name, files in kept.items():
                dump_name = safe_rel(dump_name, what=f"dump name {hid}")
                if "/" in dump_name or not isinstance(files, dict) or not files:
                    raise ValueError(f"score {hid!r} has malformed dump {dump_name!r}")
                for rel, digest in files.items():
                    rel = safe_rel(rel, what=f"dump file {hid}")
                    _artifact(out, f"kept {hid}", f"{kept_dir}/{dump_name}/{rel}", digest)

    controls = report.get("controls")
    if isinstance(controls, dict):
        for arm in ("identity", "prefix", "null"):
            rec = controls.get(arm)
            if not isinstance(rec, dict):
                raise ValueError(f"report.controls.{arm} is missing or malformed")
            _artifact(out, f"control {arm} score",
                      f"controls/{safe_rel(rec.get('score_file'), what=f'{arm} score_file')}",
                      rec.get("score_sha256"))
            _artifact(out, f"control {arm} tokens",
                      f"controls/{safe_rel(rec.get('tokens_file'), what=f'{arm} tokens_file')}",
                      rec.get("tokens_sha256"))
            if rec.get("pairs_file") is not None or rec.get("pairs_sha256") is not None:
                _artifact(out, f"control {arm} pairs",
                          f"controls/{safe_rel(rec.get('pairs_file'), what=f'{arm} pairs_file')}",
                          rec.get("pairs_sha256"))

    bridge = report.get("bridge")
    if isinstance(bridge, dict):
        for hid, rec in (bridge.get("handoffs") or {}).items():
            kept_dir = safe_rel(rec.get("kept_dir"), what=f"bridge kept_dir {hid}")
            if not kept_dir.startswith("bridge/"):
                raise ValueError(f"bridge {hid!r} kept_dir is outside bridge/: {kept_dir}")
            _artifact(out, f"bridge score {hid}",
                      f"bridge/{safe_rel(rec.get('score_file'), what='bridge score_file')}",
                      rec.get("score_sha256"))
            _artifact(out, f"bridge tokens {hid}",
                      f"bridge/{safe_rel(rec.get('tokens_file'), what='bridge tokens_file')}",
                      rec.get("tokens_sha256"))
            _artifact(out, f"bridge pairs {hid}",
                      f"{kept_dir}/{safe_rel(rec.get('pairs_file'), what='bridge pairs_file')}",
                      rec.get("pairs_sha256"))
            for dump_name, files in (rec.get("kept_dumps") or {}).items():
                dump_name = safe_rel(dump_name, what=f"bridge dump name {hid}")
                for rel, digest in files.items():
                    _artifact(out, f"bridge kept {hid}",
                              f"{kept_dir}/{dump_name}/{safe_rel(rel, what='bridge dump file')}", digest)
    return sorted(out.values(), key=lambda x: x.rel)


def validate_checkpoint_report(report: dict, *, config: Path, exp: str, pair: str) -> tuple[set[str], set[str]]:
    """Validate an in-progress E9F checkpoint before any remote deletion.

    Returns ``(included_ids, scored_ids)``.  The driver writes all alignment/run-order metadata up
    front and appends scores in that order, so even an incomplete checkpoint can be tied to the exact
    config, pin, pair, included set, keep draw, and control handoff.
    """
    with config.open("rb") as f:
        cfg = tomllib.load(f)["e9"]
    expected_results = f"results/{exp}"
    if cfg.get("pair") != pair or cfg.get("results_dir") != expected_results:
        raise ValueError("config is not the requested experiment/pair")
    if report.get("pair") != pair or report.get("upstream_sha") != cfg.get("upstream_sha"):
        raise ValueError("report pair/upstream pin does not match the config")
    if report.get("config_sha256") != text_sha256(config):
        raise ValueError("report config_sha256 does not match the home config")
    # Entry 0042 REGISTERS a stopping rule for this cell: [e9.order] by = "n_sender_asc" and
    # allow_partial = true. This verifier was written when the short cell forbade a partial close, and
    # it refused both the report claiming one AND the config permitting one -- so as written it would
    # have refused a correctly-registered E9F run outright, and a budget-killed sitting could never be
    # closed. What must still be enforced is the SHAPE of a partial: the scored set must be a PREFIX of
    # the registered run order (checked below against `order`), never "the handoffs that happened to
    # finish". The config and the report must also agree with each other about whether a partial is
    # permitted, so neither can drift from the registered rule.
    order_cfg = cfg.get("order") or {}
    allow_partial = bool(order_cfg.get("allow_partial", False))
    if report.get("partial") and not allow_partial:
        raise ValueError("the report claims a partial close but the registered config forbids one")
    expected_order_by = order_cfg.get("by", "id")
    if report.get("order_by") != expected_order_by:
        raise ValueError("report order_by does not match the E9F config")
    if report.get("bridge") not in (None, {}):
        raise ValueError("E9F is native-receiver/no-bridge, but the report contains a bridge")

    coverage, scores, order = report.get("coverage"), report.get("scores"), report.get("run_order")
    if not isinstance(coverage, dict) or not isinstance(scores, dict) or not isinstance(order, list):
        raise ValueError("report coverage/scores/run_order is malformed")
    included = coverage.get("included")
    if not isinstance(included, int) or included < 1:
        raise ValueError("report coverage.included is not a positive integer")
    if len(order) != included or len(set(order)) != included or not all(isinstance(x, str) and x for x in order):
        raise ValueError("report run_order is not a unique coverage.included-sized ID list")
    if list(scores) != order[:len(scores)]:
        raise ValueError("checkpoint scores are not a prefix of the registered run_order")
    observed, excluded_n = coverage.get("observed"), coverage.get("excluded")
    if (not isinstance(observed, int) or not isinstance(excluded_n, int)
            or observed != included + excluded_n):
        raise ValueError("report coverage observed/included/excluded arithmetic is inconsistent")
    aligns = report.get("alignments")
    if not isinstance(aligns, list) or len(aligns) != observed:
        raise ValueError("report alignments do not match coverage.observed")
    align_ids = [x.get("handoff_id") for x in aligns if isinstance(x, dict)]
    if len(align_ids) != len(aligns) or any(not isinstance(x, str) or not x for x in align_ids):
        raise ValueError("report alignment IDs are malformed")
    if len(set(align_ids)) != len(align_ids):
        raise ValueError("report alignment IDs are not unique")
    if any(type(x.get("excluded")) is not bool for x in aligns):
        raise ValueError("report alignment excluded flags are not strict booleans")
    included_ids = {x["handoff_id"] for x in aligns if not bool(x.get("excluded"))}
    if included_ids != set(order):
        raise ValueError("included alignment IDs do not equal run_order")
    if expected_order_by == "id" and order != sorted(included_ids):
        raise ValueError("run_order is not the registered ID-sorted included set")
    controls = report.get("controls")
    if scores:
        if not isinstance(controls, dict) or controls.get("handoff_id") != order[0]:
            raise ValueError("checkpoint controls are absent or do not belong to run_order[0]")
    elif controls is not None:
        raise ValueError("checkpoint has controls before any scored handoff")

    keep = report.get("keep_subset")
    if not isinstance(keep, list) or len(set(keep)) != len(keep) or not set(keep) <= set(order):
        raise ValueError("report keep_subset is malformed")
    with_kept = {hid for hid, rec in scores.items() if rec.get("kept_dumps") is not None}
    if with_kept != set(keep) & set(scores):
        raise ValueError("checkpoint kept_dumps set does not equal scored keep_subset")
    return included_ids, set(scores)


def validate_complete_report(report: dict, *, config: Path, exp: str, pair: str) -> set[str]:
    """Validate E9F's identity/completeness and return every required non-scratch result path."""
    validate_checkpoint_report(report, config=config, exp=exp, pair=pair)
    if report.get("complete") is not True:
        raise ValueError("report is not complete")
    # A report closed by `e9 --close-partial` also carries complete = true; it is NOT a complete run
    # and has no final manifest to check against. Say so, rather than failing below on the run_order
    # comparison with a message that reads like corruption.
    if report.get("partial"):
        raise ValueError("this is a CLOSED PARTIAL, not a complete run: it is verified by "
                         "--final-partial (before the close), never by the complete path")
    scores, order = report["scores"], report["run_order"]
    if list(scores) != order:
        raise ValueError("complete report scores are not exactly run_order")
    if not isinstance(report.get("controls"), dict):
        raise ValueError("complete report has no controls")

    required = {"report.json", "align/coverage.json"}
    for row in report["alignments"]:
        hid = row.get("handoff_id")
        if not isinstance(hid, str) or not hid:
            raise ValueError("alignment has no handoff_id")
        stem = hid.replace("/", "__").replace("#", "_sw")
        required.update((f"align/{stem}.json", f"align/{stem}.npz"))
    for item in report_artifacts(report):
        if not item.rel.startswith("scratch/") and not (
                item.rel.startswith("bridge/") and item.rel.count("/") >= 2):
            required.add(item.rel)
    return required


def verify_artifacts(local: Path, artifacts: Iterable[Artifact]) -> tuple[list[str], int, int]:
    bad: list[str] = []
    checked = total = 0
    for item in artifacts:
        path = local / item.rel
        if not path.is_file():
            bad.append(f"MISSING {item.label}: {item.rel}")
            continue
        got = sha256(path)
        if got != item.digest:
            bad.append(f"MISMATCH {item.label}: {item.rel} got {got[:12]} want {item.digest[:12]}")
            continue
        checked += 1
        total += path.stat().st_size
    return bad, checked, total


def parse_manifest(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        digest, sep, rel = raw.partition("  ")
        if not sep:
            raise ValueError(f"manifest line {n} has no two-space sha256 separator")
        rel = rel.removeprefix("./")
        rel = safe_rel(rel, what=f"manifest line {n} path")
        digest = _digest(digest, what=f"manifest line {n} digest")
        if rel in out:
            raise ValueError(f"manifest repeats {rel}")
        out[rel] = digest
    if not out:
        raise ValueError("final manifest is empty")
    return out


def manifest_local_path(rel: str, *, local: Path, exp: str) -> Path:
    """Where a path named by the box's final manifest lands at home.

    This MUST accept everything `sitting_b.sh` actually lists, or the verification fails, the terminate
    receipt is never written, and a FINISHED sitting sits there billing. As first written it accepted
    only results/ and FINAL_LOGS, while the box's manifest also lists `manifest_check.out`, the
    `sitting_b.evidence/` tree and the per-attempt `<exp>.*.halt.*` files -- so it could never have
    succeeded. The rule is still allow-list, not "anything goes": every accepted shape is enumerated,
    scratch tensors are still refused, and `safe_rel` still rejects traversal."""
    prefix = f"linear-ceiling/results/{exp}/"
    if rel.startswith(prefix):
        result_rel = safe_rel(rel[len(prefix):], what="manifest result path")
        if result_rel.startswith("scratch/"):
            raise ValueError("final manifest must not include incrementally deleted scratch tensors")
        return local / result_rel
    if rel in {x.format(exp=exp) for x in FINAL_LOGS}:
        return local / "logs" / "box" / rel
    # the run's own evidence tree, kept beside the logs
    if rel.startswith("sitting_b.evidence/"):
        return local / "logs" / "box" / safe_rel(rel, what="manifest evidence path")
    # the traces/manifest check the box ran before the gates
    if rel == "manifest_check.out":
        return local / "logs" / "box" / rel
    # per-attempt halt records: <exp>.<something>.halt.{log,rc,status}, no directory component
    if (rel.startswith(f"{exp}.") and rel.rpartition(".")[2] in {"log", "rc", "status"}
            and ".halt." in rel and "/" not in rel):
        return local / "logs" / "box" / rel
    raise ValueError(f"final manifest contains an out-of-scope path: {rel}")


def verify_final_manifest(manifest_path: Path, *, local: Path, exp: str,
                          required_results: set[str]) -> tuple[int, int, dict[str, str]]:
    manifest = parse_manifest(manifest_path)
    result_prefix = f"linear-ceiling/results/{exp}/"
    named_results = {rel[len(result_prefix):] for rel in manifest if rel.startswith(result_prefix)}
    missing = sorted(required_results - named_results)
    if missing:
        raise ValueError(f"final manifest omits {len(missing)} required result(s): {missing[:3]}")
    required_logs = {x.format(exp=exp) for x in FINAL_LOGS}
    missing_logs = sorted(required_logs - set(manifest))
    if missing_logs:
        raise ValueError(f"final manifest omits required logs: {missing_logs}")
    bad, checked, total = [], 0, 0
    for rel, want in manifest.items():
        path = manifest_local_path(rel, local=local, exp=exp)
        if not path.is_file():
            bad.append(f"MISSING final {rel}")
            continue
        got = sha256(path)
        if got != want:
            bad.append(f"MISMATCH final {rel}: got {got[:12]} want {want[:12]}")
            continue
        checked += 1
        total += path.stat().st_size
    if bad:
        raise ValueError("; ".join(bad[:5]))
    box_logs = local / "logs" / "box"
    if (box_logs / f"{exp}.rc").read_text(encoding="utf-8").strip() != "EXIT=0":
        raise ValueError(f"{exp}.rc is not EXIT=0")
    if (box_logs / f"{exp}.status").read_text(encoding="utf-8").strip() != "SITTING_B_OK":
        raise ValueError(f"{exp}.status is not SITTING_B_OK")
    # sitting_b.sh writes `[<utc>] SITTING_B_OK`, never a bare line, so an exact-match test could
    # NEVER pass on a real run: a correct complete sitting got no receipt and billed until --force.
    # Match the marker as the last field of some line, which accepts the box's timestamped form and
    # still refuses SITTING_B_FAILED or a marker embedded in prose.
    log_lines = (box_logs / f"{exp}.log").read_text(encoding="utf-8", errors="replace").splitlines()
    if not any(ln.split()[-1:] == ["SITTING_B_OK"] for ln in log_lines):
        raise ValueError(f"{exp}.log has no terminal SITTING_B_OK line")
    return checked, total, manifest


class BoxFailed(RuntimeError):
    """The launcher recorded a terminal failure. Polling for a completion that cannot arrive is the
    worst thing this tool can do: the pod bills the whole time and the operator believes it is
    working. Raised so `main` can exit on it distinctly, with the status line quoted."""


def box_status(local: Path, exp: str) -> str | None:
    """The launcher's own terminal state, as mirrored here. None until the box writes one."""
    path = local / "logs" / "box" / f"{exp}.status"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace").strip()


def check_box_status(local: Path, exp: str) -> str | None:
    """Refuse to keep waiting on a run the box has already given up on.

    SITTING_B_FAILED is terminal by construction: the launcher writes it, removes the final manifest
    and exits, so `report.complete` will never appear. What is already mirrored here may still be a
    closeable prefix -- that is `--final-partial`'s job -- but this loop has nothing left to wait for.
    A RUNNING or SITTING_B_OK status, or none yet, is not a failure and returns normally."""
    status = box_status(local, exp)
    if status and status.split()[0:1] == ["SITTING_B_FAILED"]:
        raise BoxFailed(status)
    return status


class Transport:
    """One cached target using rp.py's mapped SSH options; no independent cloud authority."""

    def __init__(self, pod_id: str, expected_name: str) -> None:
        matches = [pod for pod in rp.pods() if pod.get("id") == pod_id]
        if len(matches) != 1:
            raise RuntimeError(f"state pod {pod_id!r} is not the one live RunPod result")
        pod = matches[0]
        if pod.get("name") != expected_name:
            raise RuntimeError(f"state pod {pod_id!r} is named {pod.get('name')!r}, not {expected_name!r}")
        ip, port = rp._ports(pod)
        if not ip or not port:
            raise RuntimeError(f"state pod {pod_id!r} has no public mapped SSH port")
        rp.KNOWN_HOSTS.parent.mkdir(parents=True, exist_ok=True)
        self.ssh = ["ssh", *rp.SSH_OPTS, "-p", port, f"root@{ip}"]

    def run_bytes(self, command: str, *, timeout: int = 120) -> bytes:
        proc = subprocess.run(self.ssh + [command], capture_output=True, timeout=timeout)
        if proc.returncode:
            err = proc.stderr.decode("utf-8", "replace")[-800:]
            raise RuntimeError(f"remote command rc={proc.returncode}: {err}")
        return proc.stdout

    def stream_tar(self, remote_dir: str, names: list[str], local_dir: Path,
                   *, timeout: int = 7200) -> None:
        if not names:
            return
        for name in names:
            safe_rel(name, what="tar member")
        local_dir.mkdir(parents=True, exist_ok=True)
        remote = f"cd {shlex.quote(remote_dir)} && tar -cf - -- " + " ".join(shlex.quote(x) for x in names)
        with subprocess.Popen(self.ssh + [remote], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as src:
            assert src.stdout is not None and src.stderr is not None
            untar = subprocess.run(["tar", "-xf", "-", "--no-same-owner", "-C", str(local_dir)],
                                   stdin=src.stdout, capture_output=True, timeout=timeout)
            src.stdout.close()
            err = src.stderr.read().decode("utf-8", "replace")
            src.wait(timeout=60)
        if src.returncode or untar.returncode:
            terr = untar.stderr.decode("utf-8", "replace")
            raise RuntimeError(f"tar stream failed: ssh={src.returncode} tar={untar.returncode} "
                               f"{err[-400:]} {terr[-400:]}")

    def remove_verified_tree(self, remote_path: str, remote_results: str) -> None:
        # Caller has already restricted this to <results>/scratch/<one handoff>.  Re-state that
        # invariant here at the destructive boundary rather than trusting a distant validation.
        p, root = PurePosixPath(remote_path), PurePosixPath(remote_results)
        if (not p.is_absolute() or not root.is_absolute()
                or p.parent != root / "scratch" or p.name in ("", ".", "..", "scratch")):
            raise ValueError(f"refusing unsafe deletion target {remote_path!r}")
        q = shlex.quote(remote_path)
        self.run_bytes(f"rm -rf -- {q} && test ! -e {q}", timeout=300)


def remote_small_listing(tx: Transport, remote_results: str) -> dict[str, list[object]]:
    cmd = (f"cd {shlex.quote(remote_results)} 2>/dev/null && "
           "find . -type f -printf '%s\\t%T@\\t%P\\0' || true")
    out: dict[str, list[object]] = {}
    for raw in tx.run_bytes(cmd).split(b"\0"):
        if not raw:
            continue
        size, mtime, rel = raw.decode("utf-8").split("\t", 2)
        rel = safe_rel(rel, what="remote result path")
        parts = PurePosixPath(rel).parts
        if parts[0] == "scratch" or (parts[0] == "bridge" and len(parts) >= 3):
            continue
        out[rel] = [int(size), mtime]
    return out


def mirror_small(tx: Transport, remote_results: str, local: Path, seen: dict) -> int:
    listing = remote_small_listing(tx, remote_results)
    changed = sorted(rel for rel, meta in listing.items()
                     if seen.get(rel) != meta or not (local / rel).is_file())
    if changed:
        tx.stream_tar(remote_results, changed, local)
        for rel in changed:
            path = local / rel
            if not path.is_file() or path.stat().st_size != listing[rel][0]:
                raise RuntimeError(f"short small-file mirror: {rel}")
            seen[rel] = listing[rel]
    return len(changed)


def mirror_workspace_files(tx: Transport, remote_work: str, names: list[str], local_logs: Path,
                           seen: dict, *, force: bool = False) -> int:
    quoted = " ".join(shlex.quote(f"{remote_work.rstrip('/')}/{x}") for x in names)
    # `[ -f x ] && stat` is the loop's last command, so a MISSING last name makes the whole loop exit
    # 1 and run_bytes raise. The final manifest is in this list and does not exist until the run ends,
    # so EVERY mid-run round died before pulling a single kept dump. `|| true` per iteration fixes it;
    # absence is the normal case here, not an error.
    cmd = f"for f in {quoted}; do [ -f \"$f\" ] && stat -c '%s\\t%Y\\t%n' \"$f\" || true; done"
    listing: dict[str, list[object]] = {}
    for line in tx.run_bytes(cmd).decode("utf-8").splitlines():
        size, mtime, absolute = line.split("\t", 2)
        name = PurePosixPath(absolute).name
        if name not in names:
            raise RuntimeError(f"unexpected workspace listing path: {absolute}")
        listing[name] = [int(size), mtime]
    changed = sorted(name for name, meta in listing.items()
                     if force or seen.get(name) != meta or not (local_logs / name).is_file())
    if changed:
        tx.stream_tar(remote_work, changed, local_logs)
        for name in changed:
            if not (local_logs / name).is_file() or (local_logs / name).stat().st_size != listing[name][0]:
                raise RuntimeError(f"short workspace-file mirror: {name}")
            seen[name] = listing[name]
    return len(changed)


def kept_groups(report: dict) -> list[tuple[str, str, list[Artifact]]]:
    arts = report_artifacts(report)
    groups: list[tuple[str, str, list[Artifact]]] = []
    for hid, rec in report.get("scores", {}).items():
        if rec.get("kept_dumps") is not None:
            kept_dir = safe_rel(rec["kept_dir"], what=f"kept_dir {hid}")
            groups.append((hid, kept_dir, [a for a in arts if a.rel.startswith(f"{kept_dir}/")]))
    for hid, rec in ((report.get("bridge") or {}).get("handoffs") or {}).items():
        kept_dir = safe_rel(rec["kept_dir"], what=f"bridge kept_dir {hid}")
        groups.append((f"bridge:{hid}", kept_dir, [a for a in arts if a.rel.startswith(f"{kept_dir}/")]))
    return groups


def _load_json(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path} is not a JSON object")
    return obj


def validate_runpod_binding(state: dict, *, expected_name: str) -> None:
    if state.get("name") != expected_name:
        raise ValueError(f"RunPod state names {state.get('name')!r}, not {expected_name!r}; refusing the wrong sitting")
    if not state.get("pod_id") or not state.get("verify_nonce") or not state.get("verify_file"):
        raise ValueError("RunPod state lacks pod_id/verify_nonce/verify_file; create Sitting B with the hardened rp.py")


def write_receipt(runpod_state: dict, *, exp: str, pair: str, report_sha: str,
                  manifest_sha: str | None, checked: int, total_bytes: int,
                  partial: dict | None = None) -> Path:
    """Write the nonce- and pod-bound receipt that makes `rp.py terminate` safe.

    `manifest_sha` is None and `partial` is set on the REGISTERED PARTIAL path (`--final-partial`).
    There is no final manifest in that case by construction: the launcher writes it only after a
    complete run's writers stop, and a partial exists precisely because they did not. What stands in
    its place is `partial`, which names the basis checkpoint and the scored prefix it covers, so a
    reader can tell a complete receipt from a partial one without opening the mirror."""
    verify = Path(runpod_state["verify_file"]).expanduser()
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "verify_nonce": runpod_state["verify_nonce"],
        "pod_id": runpod_state["pod_id"],
        "created_utc": runpod_state["created_utc"],
        "verified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "exp": exp,
        "pair": pair,
        "report_sha256": report_sha,
        "final_manifest_sha256": manifest_sha,
        "files_verified": checked,
        "bytes_verified": total_bytes,
    }
    if partial is not None:
        receipt["partial"] = partial
    if verify.exists():
        old = _load_json(verify)
        for key in ("schema", "verify_nonce", "pod_id", "created_utc", "report_sha256"):
            if old.get(key) != receipt.get(key):
                raise ValueError(f"existing verification receipt belongs to another result ({key})")
    _atomic_json(verify, receipt, mode=0o600)
    return verify


# ---------------------------------------------------------------------------------------------
# B4: the terminal path for a REGISTERED PARTIAL CLOSE (entry 0042's stopping rule).
#
# Everything above serves a run that finishes. A run stopped at the budget ceiling -- drained on
# purpose, or hard-killed -- produces no `report.complete`, no final manifest and no SITTING_B_OK,
# so every acceptance path above refuses it and the sitting has no way to end. That is what this
# section supplies, and it is deliberately a HOME-SIDE operation on the verified mirror: after a
# hard kill the pod and its disk are already gone, so anything that needed the box could not run.
#
# The rule it implements, which is registered BEFORE the run and not chosen after seeing scores:
# the closing basis is the LAST checkpoint whose every named artifact is sha-verified at home. It
# is a genuine driver checkpoint and a prefix of the registered run order -- never an edited
# report. `e9 --close-partial` then stamps `partial{...}` on exactly that file.
# ---------------------------------------------------------------------------------------------

def align_requirements(report: dict) -> set[str]:
    """The alignment records `summarize_e9` re-derives its numbers from.

    They are not fingerprinted in `report.json` (the driver writes them before it scores anything),
    so they are required to be PRESENT rather than hash-checked here. Their absence would make the
    partial unsummarizable, which is the same defect as a missing kept dump."""
    out = {"align/coverage.json"}
    for row in report.get("alignments") or []:
        hid = row.get("handoff_id")
        if not isinstance(hid, str) or not hid:
            raise ValueError("alignment row has no handoff_id")
        stem = hid.replace("/", "__").replace("#", "_sw")
        out.update((f"align/{stem}.json", f"align/{stem}.npz"))
    return out


def partial_candidates(local: Path) -> list[Path]:
    """Every file that could serve as a closing basis, best candidate first.

    Ranked by how much of the registered order it covers, because the rule closes on the LAST good
    checkpoint. `report.json` wins an exact tie: it is the driver's own file, and a B5 snapshot of
    the same prefix is a copy of it."""
    live = local / "report.json"
    cands = [live] if live.is_file() else []
    snaps = local / "checkpoints"
    if snaps.is_dir():
        cands += sorted(x for x in snaps.glob("report.*.json") if x.is_file())
    ranked = []
    for c in cands:
        try:
            rep = _load_json(c)
            scores = rep.get("scores")
            n = len(scores) if isinstance(scores, dict) else -1
        except (OSError, ValueError, json.JSONDecodeError):
            continue                                   # a torn or unreadable file is simply not a basis
        if n > 0:
            ranked.append((n, c))
    ranked.sort(key=lambda t: (-t[0], t[1] != live, t[1].name))
    return [c for _, c in ranked]


def choose_partial_basis(local: Path, *, config: Path, exp: str, pair: str):
    """Return (path, report, n_checked, n_bytes) for the last FULLY VERIFIED checkpoint.

    Fully verified means: it validates as a checkpoint (prefix of the registered order, controls
    present, config/pin/pair bound), every artifact it fingerprints is byte-identical here, and
    every alignment record the summarizer needs is present. A checkpoint that names a kept dump
    still in flight when the pod died fails this and the next one down is tried."""
    local = local.resolve()
    tried: list[str] = []
    for cand in partial_candidates(local):
        rep = _load_json(cand)
        name = cand.name if cand.parent == local else f"{cand.parent.name}/{cand.name}"
        try:
            validate_checkpoint_report(rep, config=config, exp=exp, pair=pair)
        except ValueError as e:
            tried.append(f"{name}: {e}")
            continue
        if rep.get("complete") is True:
            tried.append(f"{name}: the run is COMPLETE; close it by the normal final path, not as a partial")
            continue
        bad, checked, nbytes = verify_artifacts(local, report_artifacts(rep))
        if bad:
            tried.append(f"{name}: {len(bad)} artifact(s) unverified here, first: {bad[0]}")
            continue
        absent = sorted(rel for rel in align_requirements(rep) if not (local / rel).is_file())
        if absent:
            tried.append(f"{name}: {len(absent)} alignment record(s) absent, first: {absent[0]}")
            continue
        return cand, rep, checked, nbytes
    detail = "; ".join(tried) if tried else "no checkpoint or snapshot exists at home"
    raise ValueError(f"no closing basis is fully verified at home ({detail})")


def require_driver_stopped(runpod_state: dict, *, expected_name: str, remote_work: str, exp: str) -> str:
    """Refuse to choose a closing basis while the driver could still append to it.

    Two ways this is satisfied, and no third: the pod is gone from the account (a hard kill, so
    nothing can be running), or the pod is reachable and its recorded driver pid is dead. An
    unreachable API is neither -- it is refused rather than assumed, because guessing wrong here
    closes a partial one handoff short of what actually exists."""
    try:
        live = rp.pods()
    except (Exception, SystemExit) as e:                # gql() reports API failure as SystemExit
        raise ValueError("cannot establish that the driver stopped: the RunPod API is unreachable "
                         f"({e}). Re-run when it answers; do not assume.") from e
    if not any(pod.get("id") == runpod_state["pod_id"] for pod in live):
        return f"pod {runpod_state['pod_id']} is absent from the account listing, so no driver is running"
    tx = Transport(runpod_state["pod_id"], expected_name)
    work = shlex.quote(remote_work.rstrip("/"))
    probe = (f'p=$(tr -cd "0-9" < {work}/{shlex.quote(exp)}.pid 2>/dev/null); '
             f'if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then echo "ALIVE $p"; '
             f'else echo "STOPPED ${{p:-nopid}}"; fi')
    answer = tx.run_bytes(probe, timeout=60).decode("utf-8", "replace").strip()
    if not answer.startswith("STOPPED"):
        raise ValueError(f"the E9 driver is still running on the pod ({answer}); stop it first "
                         "(the registered stop is a signal between handoffs, which leaves the last "
                         "checkpoint intact)")
    return f"pod {runpod_state['pod_id']} is up and its driver pid is dead ({answer})"


def final_partial(a, runpod_state: dict) -> int:
    """`--final-partial`: verify a registered partial at home and write its terminate receipt.

    This writes NO `partial` stamp of its own and edits no report. It proves a basis and installs it
    as `report.json` if a snapshot outranks the live file; the close itself is
    `python -m linear_ceiling.e9 --close-partial --config config/<exp>.toml`, which is the one place
    allowed to mark a run closed."""
    local = Path(a.local).expanduser().resolve()
    config = Path(a.config)
    try:
        how = require_driver_stopped(runpod_state, expected_name=a.expected_pod_name,
                                     remote_work=a.remote_work, exp=a.exp)
        print(f"driver stopped: {how}", flush=True)
        basis, report, checked, nbytes = choose_partial_basis(local, config=config, exp=a.exp, pair=a.pair)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as e:
        print(f"FINAL-PARTIAL REFUSED: {e}; no receipt written", flush=True)
        return 4

    order, scored = report["run_order"], list(report["scores"])
    live = local / "report.json"
    if basis != live:
        # Install the snapshot as the report the closer will read. The superseded file is KEPT: it is
        # the evidence for why this basis was chosen over it, and deleting it would make the decision
        # unreviewable.
        if live.exists():
            kept = live.with_name(f"report.superseded-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json")
            live.replace(kept)
            print(f"  superseded report.json kept as {kept.name}", flush=True)
        _atomic_json(live, report)
        print(f"  installed {basis.parent.name}/{basis.name} as report.json", flush=True)

    report_sha = sha256(live)
    partial = {
        "basis": basis.name if basis.parent == local else f"{basis.parent.name}/{basis.name}",
        "n_scored": len(scored),
        "n_registered": len(order),
        "unscored": order[len(scored):],
        "driver_stopped": how,
    }
    receipt = write_receipt(runpod_state, exp=a.exp, pair=a.pair, report_sha=report_sha,
                            manifest_sha=None, checked=checked, total_bytes=nbytes, partial=partial)
    print(f"FINAL-PARTIAL VERIFIED: {len(scored)} of {len(order)} scored, {checked} hash checks, "
          f"{nbytes:,} B. Terminate receipt: {receipt}", flush=True)
    print(f"  unscored ({len(partial['unscored'])}): {', '.join(partial['unscored']) or 'none'}", flush=True)
    print(f"  NEXT: .venv/bin/python -m linear_ceiling.e9 --close-partial --config {config}", flush=True)
    terminate_on_receipt(a, "the registered partial is verified here")
    return 0


def terminate_on_receipt(a, why: str) -> None:
    """M4: close the billing window the instant the receipt exists, when asked to.

    Opt-in (`--terminate-on-receipt`), because this tool holds no cloud authority by default and a
    human ending their own sitting is a reasonable way to work. But the gap it closes is real money:
    between "verified" and whenever the operator next looks, the pod bills at the full card rate, and
    that window is unbounded overnight.

    It goes through `rp.py terminate` WITHOUT --force, so the receipt this round just wrote is
    re-validated by rp.py's own interlock before anything is destroyed. A terminate that the
    interlock refuses is a bug worth surfacing, not something to force past."""
    if not getattr(a, "terminate_on_receipt", False):
        print("  NOT terminating: --terminate-on-receipt was not passed. The pod is STILL BILLING "
              "until you run `rp.py terminate`.", flush=True)
        return
    print(f"  terminating now ({why}); the receipt is re-checked by rp.py's interlock", flush=True)
    try:
        rc = rp.cmd_terminate(argparse.Namespace(pod=None, force=False))
    except (Exception, SystemExit) as e:    # gql reports API failure as SystemExit (BaseException)
        print(f"\a  TERMINATE FAILED ({e}). THE POD IS STILL BILLING -- run `rp.py terminate` now.",
              flush=True)
        return
    if rc:
        print(f"\a  terminate returned {rc}; verify with `rp.py ps` -- the pod may still be billing",
              flush=True)


def run_round(a, tx: Transport, state: dict, runpod_state: dict) -> bool:
    local = Path(a.local).expanduser().resolve()
    local.mkdir(parents=True, exist_ok=True)
    state.setdefault("small_seen", {})
    state.setdefault("log_seen", {})
    logs = [x.format(exp=a.exp) for x in FINAL_LOGS] + [f"{a.exp}.final.sha256"]
    n_small = mirror_small(tx, a.remote_results, local, state["small_seen"])
    n_logs = mirror_workspace_files(tx, a.remote_work, logs, local / "logs" / "box", state["log_seen"])
    check_box_status(local, a.exp)          # M3: a failed launcher is terminal; stop waiting on it
    report_path = local / "report.json"
    if not report_path.exists():
        print(f"no report.json yet ({n_small} result files, {n_logs} logs refreshed)", flush=True)
        return False
    try:
        report = _load_json(report_path)
        artifacts = report_artifacts(report)
        validate_checkpoint_report(report, config=Path(a.config), exp=a.exp, pair=a.pair)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        state["small_seen"].pop("report.json", None)  # force a fresh copy after a mid-write checkpoint
        print(f"report checkpoint was mid-write/malformed ({e}); retrying", flush=True)
        return False

    print(f"scored {len(report.get('scores', {}))}/{report.get('coverage', {}).get('included', '?')} "
          f"complete={report.get('complete')} ({n_small} result files, {n_logs} logs refreshed)", flush=True)
    # A kept tensor tree is not deletable merely because its own files arrived: its checkpoint's
    # score/per-token record (and the controls once present) must also match the hashes in the same
    # report snapshot. Force-refresh any bad small fingerprint before making a deletion decision.
    small_artifacts = [item for item in artifacts if not item.rel.startswith("scratch/")]
    bad_small, _, _ = verify_artifacts(local, small_artifacts)
    if bad_small:
        retry_names = sorted({item.rel for item in small_artifacts
                              if not (local / item.rel).is_file() or sha256(local / item.rel) != item.digest})
        if retry_names:
            tx.stream_tar(a.remote_results, retry_names, local)
        bad_small, _, _ = verify_artifacts(local, small_artifacts)
    if bad_small:
        print(f"  REFUSED checkpoint fingerprints: {bad_small[0]}; no remote tensor deletion this round",
              flush=True)
    any_kept_bad = False
    for label, kept_dir, items in kept_groups(report):
        bad, checked, _ = verify_artifacts(local, items)
        if bad:
            print(f"  pulling kept {label}: {len(bad)}/{len(items)} absent or mismatched", flush=True)
            parent, leaf = str(PurePosixPath(kept_dir).parent), PurePosixPath(kept_dir).name
            remote_parent = f"{a.remote_results.rstrip('/')}/{parent}" if parent != "." else a.remote_results
            tx.stream_tar(remote_parent, [leaf], local / parent)
            bad, checked, _ = verify_artifacts(local, items)
        if bad:
            any_kept_bad = True
            print(f"  REFUSED kept {label}: {bad[0]}; remote bytes retained", flush=True)
            continue
        print(f"  verified kept {label}: {checked} files", flush=True)
        if a.delete_verified and not bad_small:
            # Always issue the exact idempotent remove after *this round's* raw verification. A resumed
            # driver can recreate a path previously recorded deleted, so state is audit history only.
            tx.remove_verified_tree(f"{a.remote_results.rstrip('/')}/{kept_dir}", a.remote_results)
            if kept_dir not in state.setdefault("remote_deleted", []):
                state["remote_deleted"].append(kept_dir)
            print(f"  deleted/proved absent verified remote tree: {kept_dir}", flush=True)
        elif a.delete_verified:
            print(f"  retained remote tree {kept_dir}: checkpoint small-file verification failed", flush=True)

    # ---- B5: snapshot every FULLY VERIFIED checkpoint -------------------------------------------
    # A ceiling kill destroys the pod's disk, so the only thing that survives is what is already here
    # AND provably whole. `report.json` on its own is not enough: summarize_e9 re-scores the kept
    # dumps from tensors and refuses if any fingerprint is missing, so a report naming a kept dump
    # still in flight makes the WHOLE partial unusable -- the exact failure entry 0042's stopping rule
    # is supposed to prevent.
    # So: when every artifact this checkpoint names is verified at home, keep a numbered copy. After a
    # hard kill the operator installs the LAST snapshot as report.json and closes on that prefix. It is
    # a genuine driver checkpoint and a prefix of the registered order, so 0042's rule is satisfied
    # with nothing edited. The snapshot is written atomically so a kill cannot tear it either.
    if not bad_small and not any_kept_bad:
        n_scored = len(report.get("scores", {}))
        if n_scored:
            snaps = local / "checkpoints"
            snaps.mkdir(parents=True, exist_ok=True)
            _atomic_json(snaps / f"report.{n_scored}.json", report)
            state["last_verified_n_scored"] = n_scored
            print(f"  snapshot: checkpoints/report.{n_scored}.json (every named artifact verified here)",
                  flush=True)

    state_path = Path(a.state).expanduser()
    _atomic_json(state_path, state, mode=0o600)
    if report.get("complete") is not True:
        return False

    # The wrapper writes the manifest only after all writers stop.  Its absence means "not final",
    # even if report.complete has already been observed in the small race before wrapper finalization.
    manifest_name = f"{a.exp}.final.sha256"
    manifest_path = local / "logs" / "box" / manifest_name
    if not manifest_path.exists():
        print("report complete; waiting for the atomic final manifest/status", flush=True)
        return False
    try:
        required = validate_complete_report(report, config=Path(a.config), exp=a.exp, pair=a.pair)
        manifest = parse_manifest(manifest_path)
        # Refuse out-of-scope entries before using any manifest spelling as a remote tar member.
        for rel in manifest:
            manifest_local_path(rel, local=local, exp=a.exp)
        result_prefix = f"linear-ceiling/results/{a.exp}/"
        result_names = sorted(rel[len(result_prefix):] for rel in manifest if rel.startswith(result_prefix))
        work_names = sorted(rel for rel in manifest if not rel.startswith(result_prefix))
        # Force one post-manifest copy: incremental metadata is an optimization, never final evidence.
        tx.stream_tar(a.remote_results, result_names, local)
        tx.stream_tar(a.remote_work, work_names, local / "logs" / "box")
        # Pull the manifest itself again after the bytes it names. It is atomic/immutable after success.
        tx.stream_tar(a.remote_work, [manifest_name], local / "logs" / "box")
        report = _load_json(report_path)
        required = validate_complete_report(report, config=Path(a.config), exp=a.exp, pair=a.pair)
        artifacts = report_artifacts(report)
        bad, n_report, report_bytes = verify_artifacts(local, artifacts)
        if bad:
            raise ValueError(bad[0])
        n_final, final_bytes, _ = verify_final_manifest(
            manifest_path, local=local, exp=a.exp, required_results=required)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as e:
        print(f"FINAL VERIFICATION REFUSED: {e}; no terminate receipt written", flush=True)
        return False

    report_sha, manifest_sha = sha256(report_path), sha256(manifest_path)
    receipt = write_receipt(runpod_state, exp=a.exp, pair=a.pair, report_sha=report_sha,
                            manifest_sha=manifest_sha, checked=n_report + n_final,
                            total_bytes=report_bytes + final_bytes)
    print(f"COMPLETE: report {report_sha}; {n_report + n_final} hash checks, "
          f"{report_bytes + final_bytes:,} B. Terminate receipt: {receipt}", flush=True)
    terminate_on_receipt(a, "the run is complete and every byte is verified here")
    return True


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--exp", default=EXP)
    ap.add_argument("--pair", default=PAIR)
    ap.add_argument("--config", default=f"config/{EXP}.toml")
    ap.add_argument("--local", default=f"results/{EXP}")
    ap.add_argument("--remote-results", default=f"/workspace/linear-ceiling/results/{EXP}")
    ap.add_argument("--remote-work", default="/workspace")
    ap.add_argument("--state", default=str(Path.home() / ".cache" / "linear-ceiling" / f"runpod-{EXP}-pull.json"))
    ap.add_argument("--runpod-state", default=str(rp.STATE))
    ap.add_argument("--expected-pod-name", default=POD_NAME)
    ap.add_argument("--every", type=int, default=60)
    # The kept-dump budget for this cell is ~50.1 GiB (8 handoffs x (n_sender*245760 + n_receiver*131072)),
    # measured from coverage.json, and --local defaults to results/<exp> so tensors land in their FINAL
    # location -- there is no staging copy to double-count it. The floor below is that budget plus
    # headroom; the run pauses rather than filling the disk, because a full disk mid-pull corrupts the
    # very artifacts the sitting exists to produce.
    ap.add_argument("--min-free-gib", type=float, default=65.0,
                    help="PRE-CREATE check only: refuse to start below this")
    ap.add_argument("--headroom-gib", type=float, default=10.0,
                    help="during the run the floor is (outstanding kept bytes) + this, never a constant")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--delete-verified", action="store_true",
                    help="after raw-byte verification, delete that one kept remote tree to free pod disk")
    ap.add_argument("--terminate-on-receipt", action="store_true",
                    help="terminate the pod as soon as a receipt is written (via rp.py's own "
                         "interlock, never --force). Closes the bill-while-nobody-is-looking window.")
    ap.add_argument("--final-partial", action="store_true",
                    help="terminal path for a REGISTERED PARTIAL (entry 0042): with the driver stopped, "
                         "prove the last fully verified checkpoint at home and write its terminate "
                         "receipt. Pulls nothing; `e9 --close-partial` does the close afterwards.")
    return ap



def free_gib(path: Path) -> float:
    """Free space where the kept tensors actually land."""
    st = os.statvfs(path if path.exists() else path.parent)
    return st.f_bavail * st.f_frsize / 2**30


def outstanding_gib(local: Path, report: dict | None) -> float:
    """Bytes the checkpoint still expects to land here, in GiB.

    The floor must track what is LEFT to pull, not a constant: the pulled tensors consume the very
    space a fixed floor measures, so a constant floor makes the puller pause against its own
    downloads and never resume. (Measured: a 65 GiB floor with 79.6 GiB free froze for good after the
    4th kept dump.)"""
    if not report:
        return 0.0
    total = 0
    for _hid, rec in (report.get("scores") or {}).items():
        kept = rec.get("kept_dumps")
        if not kept:
            continue
        kdir = rec.get("kept_dir") or ""
        for dump, files in kept.items():
            for rel in files:
                if not (local / kdir / dump / rel).is_file():      # not yet home
                    total += int(rec.get("kept_bytes", {}).get(dump, 0)) or 0
                    break
    return total / 2**30


def require_free_space(local: Path, floor: float, *, blocking: bool) -> None:
    """Refuse before the run, PAUSE during it. Never silently fill the disk.

    A pull that runs out of space part-way through a kept tensor leaves a short file whose hash will
    not match -- and the pod deletes nothing until the hash matches, so the artifact survives on the
    box only until the run ends. Pausing keeps the operator's options open; filling the disk does not.
    """
    have = free_gib(local)
    if have >= floor:
        return
    msg = (f"only {have:.1f} GiB free at {local}, below the {floor:.1f} GiB floor "
           f"(this cell's kept dumps need ~50.1 GiB)")
    if not blocking:
        raise SystemExit(f"pull_verify_b REFUSED: {msg}")
    while free_gib(local) < floor:
        print(f"\a  PAUSED: {msg}. Free space and I will continue; nothing is deleted on the pod "
              f"while paused.", flush=True)
        time.sleep(60)
    print(f"  resumed: {free_gib(local):.1f} GiB free", flush=True)


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if a.every < 5:
        raise SystemExit("pull_verify_b REFUSED: --every must be at least 5 seconds")
    runpod_state = _load_json(Path(a.runpod_state).expanduser())
    try:
        validate_runpod_binding(runpod_state, expected_name=a.expected_pod_name)
    except ValueError as e:
        raise SystemExit(f"pull_verify_b REFUSED: {e}") from e
    if a.final_partial:
        # Deliberately ahead of the free-space refusal and of any pull state: this path downloads
        # nothing, and after a hard kill it is the only path left, so it must not be gated on a floor
        # that exists to protect a pull that is no longer going to happen.
        return final_partial(a, runpod_state)
    require_free_space(Path(a.local).expanduser(), a.min_free_gib, blocking=False)
    pull_state_path = Path(a.state).expanduser()
    state = _load_json(pull_state_path) if pull_state_path.exists() else {
        "schema": "linear-ceiling.runpod.pull-b.v1",
        "pod_id": runpod_state["pod_id"],
        "verify_nonce": runpod_state["verify_nonce"],
        "exp": a.exp,
        "pair": a.pair,
        "small_seen": {},
        "log_seen": {},
        "remote_deleted": [],
    }
    for key, want in (("pod_id", runpod_state["pod_id"]), ("verify_nonce", runpod_state["verify_nonce"]),
                      ("exp", a.exp), ("pair", a.pair)):
        if state.get(key) != want:
            raise SystemExit(f"pull_verify_b REFUSED: pull state {key} belongs to another sitting")
    tx = Transport(runpod_state["pod_id"], a.expected_pod_name)
    local_root = Path(a.local).expanduser()
    while True:
        # Checked EVERY round, not only at startup: the kept tensors arrive over hours, and the disk
        # that was comfortable at the first handoff is the one that fills at the eighth. Pausing here
        # blocks before a round pulls anything, so nothing is half-written and nothing on the pod is
        # deleted while we wait.
        # DYNAMIC floor: what is still outstanding plus headroom, never the pre-create constant.
        # a.min_free_gib stays the PRE-CREATE check only (checked once, above).
        try:
            _rep = _load_json(local_root / "report.json") if (local_root / "report.json").exists() else None
        except Exception:                                          # a torn checkpoint mid-write
            _rep = None
        _need = outstanding_gib(local_root, _rep) + a.headroom_gib
        require_free_space(local_root, _need, blocking=True)
        try:
            if run_round(a, tx, state, runpod_state):
                return 0
        except BoxFailed as e:
            print(f"\a BOX FAILED: {e}. The launcher will not produce a complete run, so this loop "
                  f"has nothing left to wait for. What is mirrored here may still be a closeable "
                  f"prefix: stop the pod, then `--final-partial`.", flush=True)
            return 5
        except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as e:
            print(f"round failed safely ({type(e).__name__}: {e}); nothing unverified was deleted", flush=True)
        if a.once:
            return 3
        time.sleep(a.every)


if __name__ == "__main__":
    raise SystemExit(main())
