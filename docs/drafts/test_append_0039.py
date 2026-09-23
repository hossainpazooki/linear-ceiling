"""Read-only and in-memory checks for the staged admission draft; never append."""

import runpy
from pathlib import Path

import pytest

from linear_ceiling.ledger_check import check, check_against, parse_ledger

DRAFT = Path(__file__).with_name("append_0039.py")
MODULE = runpy.run_path(str(DRAFT))
ORIGINAL = MODULE["LEDGER"].read_bytes()
TEXT = ORIGINAL.decode("utf-8")


def test_candidate_preserves_old_bytes_and_cells_and_has_valid_chain():
    candidate, entry = MODULE["prepare_append"](ORIGINAL, "2026-09-14", "operator")
    assert candidate.startswith(ORIGINAL)
    assert check(candidate.decode("utf-8")) == []
    assert check_against(candidate.decode("utf-8"), TEXT) == []
    assert parse_ledger(candidate.decode("utf-8"))["hypotheses"] == parse_ledger(TEXT)["hypotheses"]
    assert not any(line.startswith("verdict:") for line in entry.splitlines())
    assert "PLACEHOLDER" not in entry


def test_next_entry_landing_refuses_instead_of_duplicating_number():
    changed = TEXT + "\n### 0039 — 2026-09-14 — another entry\n"
    with pytest.raises(ValueError, match="ordering"):
        MODULE["validate_staged_ledger"](changed)


def test_edited_trailing_entry_refuses_even_without_a_new_entry():
    with pytest.raises(ValueError, match="ledger changed"):
        MODULE["validate_staged_ledger"](TEXT.replace("25 scored of 25 registered", "edited", 1))


def test_changed_review_boundary_refuses():
    review = MODULE["REVIEW"].read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="review record changed"):
        MODULE["validate_review"](review.replace("does not resolve", "resolves"))


def test_newline_conversion_does_not_rewrite_existing_bytes():
    windows = MODULE["normalized"](TEXT).replace("\n", "\r\n").encode("utf-8")
    candidate, _ = MODULE["prepare_append"](windows, "2026-09-14", "operator")
    assert candidate.startswith(windows)
    assert check(candidate.decode("utf-8")) == []


def test_operator_cannot_inject_another_ledger_line():
    with pytest.raises(ValueError, match="operator identity"):
        MODULE["entry_text"]("2026-09-14", "operator\nverdict: H-E9 = unresolved")


def test_preview_does_not_write(monkeypatch, capsys):
    def refuse_write(*args, **kwargs):
        raise AssertionError("preview attempted a write")

    original_open = Path.open

    def read_only_open(path, mode="r", *args, **kwargs):
        if any(flag in mode for flag in "wax+"):
            return refuse_write()
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", read_only_open)
    assert MODULE["main"](["--preview", "--date", "2026-09-14"]) == 0
    assert "PREVIEW ONLY" in capsys.readouterr().out
    assert MODULE["LEDGER"].read_bytes() == ORIGINAL
