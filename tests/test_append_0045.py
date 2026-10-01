"""The staged corrective-entry draft (docs/drafts/append_0045.py), exercised read-only on the synthetic cell the
`ran` fixture produces: every figure it prints comes from that cell's tail.json, the candidate ledger passes
ledger_check, the pins refuse on drift, and the ordering guard refuses a taken number. Never appends."""
import json
import runpy
from pathlib import Path

import pytest

from linear_ceiling import e9_tail
from linear_ceiling.ledger_check import check, check_against, parse_ledger
from tests.test_e9 import env, words  # noqa: F401  (pytest fixture + the synthetic encoder)
from tests.test_summarize_e9 import _retoken, ran  # noqa: F401  (pytest fixture)

REPO_ROOT = Path(__file__).resolve().parents[1]
DRAFT = REPO_ROOT / "docs" / "drafts" / "append_0045.py"
M = runpy.run_path(str(DRAFT), run_name="draft")          # not "__main__": nothing runs, nothing is appended
LEDGER_TEXT = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8").replace("\r\n", "\n")
DATE = "2026-10-01"


@pytest.fixture
def cell(ran):
    cfg, e7, report, runner = ran
    e9_tail.tail(cfg, runner=runner, encoder=words, e7=e7)
    t, f = M["load_cell"](cfg.results_dir)
    return cfg, t, f


def test_every_ledger_anchor_resolves_to_exactly_one_line_in_its_entry():
    L = M["anchors"](LEDGER_TEXT)
    lines = LEDGER_TEXT.split("\n")
    assert "Not one included handoff" in lines[L["0029_sentence"] - 1]
    assert "Not one scored handoff" in lines[L["0036_sentence"] - 1]
    assert "0.5629 / 0.3418" in lines[L["0020_r2"] - 1]
    assert "27dc922e3f7d" in lines[L["0044_e7_hash"] - 1]
    assert len(set(L.values())) == len(L)           # eleven distinct lines


def test_anchor_refuses_a_sentence_that_is_absent_or_ambiguous():
    with pytest.raises(ValueError, match="found 0 times"):
        M["anchor"](LEDGER_TEXT, "0029", "this sentence is on no ledger")
    with pytest.raises(ValueError, match="need 1"):
        M["anchor"](LEDGER_TEXT, "0029", "τ_K")       # many lines of 0029 carry it


def test_entry_states_the_cells_figures_and_the_candidate_ledger_checks(cell):
    cfg, t, f = cell
    entry = M["build_entry"](LEDGER_TEXT, {"e9": (t, f)}, DATE)
    flat = " ".join(entry.split())            # paragraphs are wrapped at WIDTH; phrases may straddle a line break
    k = t["pooled"]["same_K"]
    tk = str(t["tau"]["K"])
    over = int(round(k["fraction_over_tau"][tk] * k["n_tokens"]))
    mx = max(ph["same_K"]["mean"] for ph in t["per_handoff"].values())
    assert f"**{over:,} ({k['fraction_over_tau'][tk]:.1%}) exceed τ_K individually**" in flat
    assert f"**maximum {mx:.4f}**" in flat
    assert f"counted at the registered {t['tau']['K']!r}" in flat      # the full tau, never a typed 4-digit one
    depth = f["depth_profile_median_per_layer"]["same_K"]
    assert ", ".join(f"{x:.3f}" for x in depth) in flat
    if f.get("bridge") is None:
        assert "configuration bridge" not in flat
    assert max(len(line) for line in entry.splitlines()[1:]) <= 2 * M["WIDTH"]   # wrapped; the heading is one line
    assert f"{k['mean_after_removing_top']['0.10']:.4f} / {k['mean_after_removing_top']['0.20']:.4f}" in flat
    assert f"{t['native_window']['n_tokens']:,} tokens" in flat
    assert t["summary_sha256"][:12] in entry and t["report_sha256"][:12] in entry
    assert "Condition 1 (entry 0032)" in flat       # e9 is a Condition-1-bound cell
    assert "verdict:" not in entry and "summarize_e7" not in entry and "PLACEHOLDER" in entry
    assert entry.startswith(f"### {M['NUM']} — {DATE} — ")
    candidate = M["prepare_append"](LEDGER_TEXT, entry)
    assert candidate.startswith(LEDGER_TEXT.rstrip("\n"))
    assert "PLACEHOLDER" not in candidate
    assert check(candidate) == []
    assert check_against(candidate, LEDGER_TEXT) == []
    assert parse_ledger(candidate)["hypotheses"] == parse_ledger(LEDGER_TEXT)["hypotheses"]


def test_a_changed_summary_or_report_refuses_before_any_figure_is_read(cell):
    cfg, t, f = cell
    sj = cfg.results_dir / "summary.json"
    data = json.loads(sj.read_text(encoding="utf-8"))
    data["tau"]["K"] = data["tau"]["K"] + 1e-6
    sj.write_text(json.dumps(data, indent=1), encoding="utf-8")
    with pytest.raises(ValueError, match="summary.json changed"):
        M["load_cell"](cfg.results_dir)
    sj.write_text(json.dumps(json.loads(sj.read_text(encoding="utf-8")), indent=1), encoding="utf-8")
    rj = cfg.results_dir / "report.json"
    rj.write_text(rj.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    sj.write_bytes(sj.read_bytes())
    with pytest.raises(ValueError, match="changed since tail.json"):
        M["load_cell"](cfg.results_dir)


def test_ordering_guard_refuses_once_the_number_is_taken(cell):
    cfg, t, f = cell
    taken = LEDGER_TEXT + f"\n### {M['NUM']} — {DATE} — another entry\n"
    with pytest.raises(ValueError, match="ordering"):
        M["build_entry"](taken, {"e9": (t, f)}, DATE)
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        M["build_entry"](LEDGER_TEXT, {"e9": (t, f)}, "Oct 1")


def test_the_e7_hash_paragraph_appears_only_with_the_llama_cell(cell):
    cfg, t, f = cell
    without = M["build_entry"](LEDGER_TEXT, {"e9": (t, f)}, DATE)
    assert "(4) Entry 0044's E7 report hash" not in without
    with_llama = " ".join(M["build_entry"](LEDGER_TEXT, {"e9f": (t, f)}, DATE).split())
    assert "(4) Entry 0044's E7 report hash" in with_llama
    assert f["coverage_comparison"]["e7_report_sha256"][:12] in with_llama
    assert "Second model family (0039)" in with_llama
