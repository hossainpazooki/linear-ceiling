import re
import subprocess
from pathlib import Path

import pytest

import linear_ceiling


def test_repo_root_is_the_repo():
    assert (linear_ceiling.REPO_ROOT / "pyproject.toml").exists()


def test_upstream_pin_matches_upstream_md():
    text = (linear_ceiling.REPO_ROOT / "UPSTREAM.md").read_text(encoding="utf-8")
    shas = set(re.findall(r"\b[0-9a-f]{40}\b", text))
    assert shas == {linear_ceiling.UPSTREAM_SHA}, shas


def test_verbatim_docs_present():
    docs = linear_ceiling.REPO_ROOT / "docs"
    for name in ("2026-08-26-kv-handoff-screen-design.md", "2026-08-26-seed-w1.md", "gap-map.md"):
        assert (docs / name).exists(), name


_ALLOWED_TRACKED_RESULTS_PATHS = {"results/.gitkeep", "results/mapper/.gitkeep"}


def _tracked_results_paths() -> list[str]:
    """Ask git which paths under results/ it actually tracks, rather than listing the
    working tree (which legitimately grows real experiment output -- e.g. results/e0/ --
    once E0 is run locally; results/* is gitignored precisely so that output never
    becomes committable). `git ls-files` reads the index/history, not the filesystem,
    so gitignored working-tree files never appear here regardless of what E0 wrote.

    Robust to git being unavailable and to a repo with zero commits (`git ls-files`
    works fine against an empty history since it reads the index, not a commit)."""
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--", "results"],
            cwd=linear_ceiling.REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        pytest.fail(f"could not query git for tracked results/ paths: {exc}")
    return [line for line in proc.stdout.splitlines() if line]


def _assert_no_result_artifacts_tracked(tracked_paths) -> None:
    """No experiment RESULTS are ever committed -- only tracked placeholders may be.
    results/mapper/.gitkeep is a seal local artifact root (config/seal.toml) that must
    exist in a fresh clone, so it is expected alongside the top-level results/.gitkeep;
    nothing else under results/ may ever be tracked by git. (Tracking the placeholders
    themselves is not required here -- only that nothing beyond them ever is.)"""
    untracked_extras = sorted(set(tracked_paths) - _ALLOWED_TRACKED_RESULTS_PATHS)
    assert not untracked_extras, f"unexpected tracked files under results/: {untracked_extras}"


def test_results_tree_is_empty_placeholder():
    """See `_assert_no_result_artifacts_tracked` for the invariant. This checks it
    against the real repo; `test_results_tree_check_catches_tracked_artifact` proves
    the check still fires on a genuine violation, without ever `git add`-ing one."""
    _assert_no_result_artifacts_tracked(_tracked_results_paths())


def test_results_tree_check_catches_tracked_artifact():
    """The helper must still fail if a real result artifact ever becomes tracked.
    Prove this against a synthetic list rather than actually staging a file in the
    real repo (which would require `git add`, forbidden here)."""
    with pytest.raises(AssertionError):
        _assert_no_result_artifacts_tracked(
            sorted(_ALLOWED_TRACKED_RESULTS_PATHS | {"results/e0/verdict.json"})
        )
