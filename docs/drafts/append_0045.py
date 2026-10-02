"""Append entry 0045 -- CORRECTIVE, descriptive: no hypothesis row, no `verdict:` line, no cell moves.

What it records, beside sentences already on the ledger (which are immutable under the entry chain):
(1) entries 0029 and 0036 state their HOLDS reading as "not one ... matched token ... exceeds tau_K"; 0023 defines
    f* as the MEAN-repair statistic, and the per-token records show tokens over tau_K on every handoff. The counts
    are stated per cell from `e9_tail`, with the per-handoff MAXIMUM mean so "on every handoff" has a figure and a
    margin. 0038 and 0044 already draw the distinction; they are cited, not corrected.
(2) entries 0025 and 0029 label the agent-text K R^2 as 0.4371; that is the shortfall 1 - R^2 (= tau_agent_K); the
    R^2 is 0.5629 (0020's arm (b) at k = 1, restated by 0030). The arithmetic downstream is right; the label is not.
(3) summary-file figures the workshop outline printed with no entry (the configuration bridge's per-handoff R^2,
    the own-norm diagnostic, the depth profile, median |S|) are stated from `summary.json` by key; where a cell's
    own entry already states one, the script finds that in the entry's block and says so instead of re-entering it.
(4) for the second family's short cell (0044): its E7 report hash differs between the box and two later
    regenerations; the home-mirror value is stated from `summary.json`, the clean-clone value is CITED from its
    review record, and no cause is asserted.

Every figure is read from results/<cell>/tail.json (written by `e9_tail`, which ran `summarize_e9` first and
refuses on anything it refuses) and results/<cell>/summary.json; the script refuses if tail.json's pinned
summary / report sha does not match the file on disk. Line anchors are DERIVED by locating each quoted sentence
inside its entry, never typed. Statistics are NAMED mean or median everywhere (ruling 1, 2026-10-01).

  --cells e9l,e9,e9s,e9f   cells to state (default all four; e9 and e9s are Condition-1-bound and marked so)
  --date YYYY-MM-DD        defaults to today
  --preview                print, do not append
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.hashing import sha256_file_bytes            # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, PREV = "0045", "0044"          # ruling 11 (2026-10-01): the corrective entry takes 0045; the Llama long drafts moved
ENTRY_OF = {"e9": "0029", "e9l": "0036", "e9s": "0038", "e9f": "0044"}
CONDITION_1 = ("e9", "e9s")         # entry 0032: the Qwen3 short cells release nothing until Condition 1 is ruled
LEDGER = REPO_ROOT / "ledger" / "ledger.md"
CLEAN_CLONE_RECORD = "docs/reviews/2026-09-28-llama-cell-r8-backup-and-recomputation.md"
WIDTH = 112
_HEADING = re.compile(r"^### (\d{4}) — ", re.M)
# An entry that mentions this marker must carry an `e7-manifest-sha256:` line (ledger_check); this entry cites no
# E7 figure, so the word must not appear in it.
_E7_MARKER = "summarize_e7"


# ----------------------------------------------------------------------------------------------------------------
# Ledger anchors: each quoted sentence is located inside its own entry's block; exactly one hit or refuse.
# ----------------------------------------------------------------------------------------------------------------
def _block(text: str, num: str) -> tuple[int, int]:
    """(first line number, last line number), 1-based inclusive, of entry `num`'s block."""
    lines = text.split("\n")
    starts = [(i + 1, m.group(1)) for i, ln in enumerate(lines) if (m := _HEADING.match(ln))]
    for j, (start, n) in enumerate(starts):
        if n == num:
            end = starts[j + 1][0] - 1 if j + 1 < len(starts) else len(lines)
            return start, end
    raise ValueError(f"anchor: entry {num} not on the ledger")


def block_text(text: str, num: str) -> str:
    start, end = _block(text, num)
    return "\n".join(text.split("\n")[start - 1:end])


def anchor(text: str, num: str, needle: str) -> int:
    """1-based line number of the one line inside entry `num` that contains `needle`."""
    start, end = _block(text, num)
    lines = text.split("\n")
    hits = [i + 1 for i in range(start - 1, end) if needle in lines[i]]
    if len(hits) != 1:
        raise ValueError(f"anchor: {needle!r} found {len(hits)} times inside entry {num} (lines {start}-{end}); need 1")
    return hits[0]


def anchors(text: str) -> dict:
    return {
        "0023_unit": anchor(text, "0023", "**Per-token deviation, registered.**"),
        "0023_fstar": anchor(text, "0023", "**Oracle selective-recompute fraction f*(τ).**"),
        "0029_sentence": anchor(text, "0029", "Not one included handoff has a single matched token"),
        "0036_sentence": anchor(text, "0036", "Not one scored handoff has a single matched token"),
        "0038_distinction": anchor(text, "0038", "not the fraction of tokens whose δ exceeds τ"),
        "0044_distinction": anchor(text, "0044", "The fraction of tokens individually"),
        "0044_e7_hash": anchor(text, "0044", "27dc922e3f7d"),
        "0025_label": anchor(text, "0025", "AGENT text at K R² = 0.4371"),
        "0029_label": anchor(text, "0029", "mapper on agent text (K R² 0.4371)"),
        "0020_r2": anchor(text, "0020", "| 1 (verdict-bearing) | 0.6814 / 0.5133 | 0.5629 / 0.3418 |"),
        "0030_r2": anchor(text, "0030", "(= 1 − 0.5629 = 0.4371)"),
    }


# ----------------------------------------------------------------------------------------------------------------
# Cells: tail.json + summary.json, pins checked.
# ----------------------------------------------------------------------------------------------------------------
def load_cell(rdir: Path) -> tuple[dict, dict]:
    tj, sj, rj = rdir / "tail.json", rdir / "summary.json", rdir / "report.json"
    if not (tj.exists() and sj.exists() and rj.exists()):
        raise FileNotFoundError(f"{rdir}: run `python -m linear_ceiling.e9_tail --config config/<cell>.toml` first")
    t = json.loads(tj.read_text(encoding="utf-8"))
    if t["summary_sha256"] != sha256_file_bytes(sj):
        raise ValueError(f"{rdir.name}: summary.json changed since tail.json was written (pin {t['summary_sha256'][:12]})")
    if t["report_sha256"] != sha256_file_bytes(rj):
        raise ValueError(f"{rdir.name}: report.json changed since tail.json was written (pin {t['report_sha256'][:12]})")
    return t, json.loads(sj.read_text(encoding="utf-8"))


def load_cells(results_root: Path, cells: list[str]) -> dict:
    return {c: load_cell(results_root / c) for c in cells}


def _s(d: dict, nd: int = 4) -> str:
    fmt = (lambda x: f"{x:,.0f}") if nd == 0 else (lambda x: f"{x:.{nd}f}")
    return f"median {fmt(d['median'])} (p10 {fmt(d['p10'])}, p90 {fmt(d['p90'])}; n = {d['n']})"


def _bins(rows: list[dict]) -> str:
    return " · ".join(f"{r['bin']}: mean {r['mean']:.3f} / median {r['median']:.3f} (n = {r['n_tokens']:,})"
                      for r in rows if r["n_tokens"])


def _wrap(para: str) -> str:
    return textwrap.fill(para, width=WIDTH, break_long_words=False, break_on_hyphens=False)


def cell_para(cell: str, entry: str, t: dict, f: dict, ledger_text: str) -> str:
    k = t["pooled"]["same_K"]
    tau_k = t["tau"]["K"]
    tk = str(tau_k)
    frac = k["fraction_over_tau"][tk]
    over = int(round(frac * k["n_tokens"]))
    means = {h: ph["same_K"]["mean"] for h, ph in t["per_handoff"].items()}
    mx = max(means.values())
    n_over_tau = sum(m > tau_k for m in means.values())
    fr_ph = [ph["same_K"]["fraction_over_tau"][tk] for ph in t["per_handoff"].values()]
    n_with_tail = sum(x > 0 for x in fr_ph)
    rm = k["mean_after_removing_top"]
    nw = t["native_window"]
    seam = t["seam_left_bins"]["same_K"]
    ratio = max(r["mean"] / r["median"] for r in seam if r["n_tokens"] and r["median"] > 0)
    own = f["own_norm_delta_gt_1_fraction"]
    ns = f["coverage_comparison"]["included"]["n_sender"]
    depth = f["depth_profile_median_per_layer"]["same_K"]
    n_sc = t["n_scored"]
    block = block_text(ledger_text, entry)
    own_note = f"already stated by {entry}" if "Own-norm" in block else f"not previously on the ledger for this cell"
    s_note = f"already stated by {entry}" if f"{ns['median']:,.0f}" in block else "not previously on the ledger for this cell"
    if cell in CONDITION_1:
        scope = (" **Condition 1 (entry 0032) binds this cell: these figures correct a sentence already on the ledger and "
                 "release nothing; no pooled row with any other cell; nothing enters a paper until the co-author "
                 "refutation is merged under `docs/reviews/` with two signatures. (The 2026-09-08 numbers-freeze clause "
                 "of 0032 applied to the LCFM submission, since accepted; the operator ruled it moot on 2026-10-01 for "
                 "the camera-ready. The review's substance is what remains.)**")
    elif cell == "e9f":
        scope = " Second model family (0039), its own τ; never pooled with the Qwen3 cells (0044)."
    else:
        scope = ""
    every = (f"on every one of the {n_sc} handoffs" if n_with_tail == n_sc
             else f"on {n_with_tail} of the {n_sc} handoffs")
    cfg_bridge = ""
    b = f.get("bridge")
    if b and b.get("per_handoff"):
        rows = " · ".join(f"`{hid.split('/')[-1]}` (|S| {r['n_sender']:,}) K {r['r2_K']:.4f} / V {r['r2_V']:.4f}"
                          for hid, r in b["per_handoff"].items())
        cfg_bridge = (f" The configuration bridge's per-handoff R² (entry 0035 control 4; `summary.json` key "
                      f"`bridge.per_handoff[].r2_K/r2_V`, not previously on the ledger; the bridge's f* and median δ are in "
                      f"{entry}): {rows}.")
    return _wrap(
        f"**{cell} (entry {entry}; {n_sc} scored handoffs; τ_K = {tau_k:.4f}, counted at the registered "
        f"{tau_k!r}).**{scope} "
        f"Of {k['n_tokens']:,} matched tokens, **{over:,} ({frac:.1%}) exceed τ_K individually**, {every} "
        f"(per-handoff fraction over τ_K: {_s(t['per_handoff_fraction_over_tau_K'])}, max {max(fr_ph):.1%}). Pooled "
        f"per-token δ_K: mean {k['mean']:.4f}, median {k['median']:.4f}, p90 {k['p90']:.4f}, p99 {k['p99']:.4f}, max "
        f"{k['delta_max']:.4f}. Per-handoff MEAN δ_K: {_s(t['per_handoff_mean_same_K'])}; **maximum {mx:.4f}**, which "
        f"sits {tau_k - mx:.5f} under τ_K — so f* = 0 \"on every handoff\" means every handoff's mean is at or under τ_K "
        f"({n_over_tau} of {n_sc} over it), not that no token is. Mean after removing the top 10 % / 20 % of tokens by "
        f"δ_K: {rm['0.10']:.4f} / {rm['0.20']:.4f} (CacheBlend's selection rule in this paper's units; their figure is in "
        f"other units under another rule and is not compared). Pooled δ_K by causal seam bin b⁻(t), MEAN and MEDIAN both "
        f"stated because they differ by up to {ratio:.2f}× here: {_bins(seam)}. By sender position: "
        f"{_bins(t['position_bins']['same_K'])}. Native window (sender position < {nw['cap']:,}): {nw['n_tokens']:,} "
        f"tokens, {nw['share_of_matched']:.1%} of matched, mean {nw['same_K']['mean']:.4f}, median "
        f"{nw['same_K']['median']:.4f}. |R| over the scored handoffs: {_s(t['receiver_length'], 0)}. Summary-file figures "
        f"(`summary.json` keys): |S| of the included handoffs `coverage_comparison.included.n_sender` {_s(ns, 0)} "
        f"({s_note}); `own_norm_delta_gt_1_fraction` K {_s(own['K'])}, V {_s(own['V'])} ({own_note}); "
        f"`depth_profile_median_per_layer.same_K`, median δ_K by layer 0…{len(depth) - 1}: "
        f"{', '.join(f'{x:.3f}' for x in depth)} (the V and cross arms are in the file, not restated).{cfg_bridge} "
        f"Pinned: `tail.json` → `report.json` {t['report_sha256'][:12]}, `summary.json` {t['summary_sha256'][:12]}."
    )


def build_entry(text: str, cells: dict, date: str) -> str:
    text = text.replace("\r\n", "\n")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("date must be YYYY-MM-DD (the ledger heading's form)")
    if f"### {PREV} " not in text or f"### {NUM} " in text:
        raise ValueError(f"ordering: {PREV} present, {NUM} absent")
    L = anchors(text)
    paras = "\n\n".join(cell_para(c, ENTRY_OF[c], t, f, text) for c, (t, f) in cells.items())
    e7 = ""
    if "e9f" in cells:
        t, f = cells["e9f"]
        home = f["coverage_comparison"]["e7_report_sha256"]
        e7 = "\n\n" + _wrap(
            f"**(4) Entry 0044's E7 report hash.** 0044 (line {L['0044_e7_hash']}) records the E7 report regenerated on "
            f"the box as `27dc922e3f7d…`, differing from the `0aba0fbe…` the 2026-09-10 long-run summary recorded, cause "
            f"not asserted. The home-mirror recomputation pinned here (`summary.json` {t['summary_sha256'][:12]}, key "
            f"`coverage_comparison.e7_report_sha256`) gives `{home[:12]}…`; the clean-clone recomputation record "
            f"`{CLEAN_CLONE_RECORD}` reports the same value (cited, not recomputed by this script). The box value is "
            f"the outlier. The cause is still not established and none is asserted; the file feeds only the "
            f"descriptive coverage comparison, as 0044 states."
        )
    heading = (f"### {NUM} — {date} — Corrective: f* = 0 is a statement about the MEAN within τ_K, not \"no token over "
               f"τ_K\"; the per-token tail counted per cell with the per-handoff maximum; the 0025/0029 R² label; "
               f"summary-file figures entered — descriptive, no cell moves")
    p_intro = _wrap(
        f"**What this entry corrects, and what it does not.** Entry 0029 (line {L['0029_sentence']}) and entry 0036 (line "
        f"{L['0036_sentence']}) state their HOLDS reading as \"not one … handoff has a single matched token whose centered "
        f"deviation exceeds τ_K\". Entry 0023 (line {L['0023_fstar']}) defines f*(τ) as the smallest fraction of matched "
        f"tokens whose exact recompute brings the MEAN δ_K of the rest to τ; f* = 0 therefore says every included "
        f"handoff's mean is already at or under τ_K, and says nothing about individual tokens. Entries 0038 (line "
        f"{L['0038_distinction']}) and 0044 (line {L['0044_distinction']}) already draw that distinction; 0044 adds that "
        f"the fraction of tokens individually above τ_K was not computed by its summarizer — it now is, by `e9_tail`, "
        f"which runs `summarize_e9` first and refuses on anything it refuses. Registered headings and bodies are "
        f"immutable under the entry chain, so the two sentences stand and this entry records what the per-token records "
        f"say beside them. **No verdict moves**: H-E9, H-E9L and H-E9F keep their cells; the statistic, the bands and "
        f"every τ are untouched. Unit (0023, line {L['0023_unit']}): δ is a token's share of the layer-head's unexplained "
        f"variance in R²'s units, its mean over tokens is exactly 1 − R², and it is not a per-token percent error. Every "
        f"statistic below is named mean or median; the two differ on these records."
    )
    p_tail_head = _wrap(
        "**(1) The tail, per cell, from `e9_tail` (`results/<cell>/tail.json`, pinned to the `summary.json` and "
        "`report.json` it was computed beside).**"
    )
    p_label = _wrap(
        f"**(2) The R² label in 0025 and 0029.** Entry 0025 (line {L['0025_label']}) writes \"AGENT text at K R² = 0.4371\" "
        f"and entry 0029 (line {L['0029_label']}) \"mapper on agent text (K R² 0.4371)\". 0.4371 is 1 − R², the shortfall "
        f"that 0025 registers as τ_agent_K; the R² is **0.5629**, entry 0020's arm (b) K at the verdict k = 1 (line "
        f"{L['0020_r2']}), restated by 0030 as \"1 − 0.5629 = 0.4371\" (line {L['0030_r2']}). τ_agent_K and every figure "
        f"computed from it are unchanged; only the label in the two sentences is wrong (review record "
        f"`docs/2026-09-20-astra_review.md`, R1-4)."
    )
    p_down = _wrap(
        "**(3) What this changes downstream.** The seam-concentration reading (\"deviation is local to the seam\") rests on "
        "the bin MEANS above, not on the medians the earlier entries printed; any restatement of the workshop paper's "
        "per-token bound on these records uses the means and says so. Bridge R² (A5; decides nothing) is already stated "
        "by each cell's own entry and is not restated here. Nothing here is a new experiment; the `[STRETCH]` "
        "partial-prefill run and the designs under `docs/drafts/` remain unregistered."
    )
    entry = (f"{heading}\n\n{p_intro}\n\n{p_tail_head}\n\n{paras}\n\n{p_label}\n\n{p_down}{e7}\n\n"
             f"prior-entries-sha256: PLACEHOLDER\n")
    if _E7_MARKER in entry:
        raise ValueError(f"the entry mentions {_E7_MARKER!r}, which ledger_check reads as an E7 figure citation")
    if "verdict:" in entry:
        raise ValueError("a descriptive entry carries no `verdict:` line")
    return entry


def prepare_append(text: str, entry: str) -> str:
    """The ledger text with `entry` appended and its chain hash filled in (the append_0046 idiom)."""
    text = text.replace("\r\n", "\n")
    new = text + ("" if text.endswith("\n") else "\n") + "\n" + entry
    head = _ENTRIES_HEAD.search(new)
    digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
    return new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="e9l,e9,e9s,e9f")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args(argv)
    text = LEDGER.read_text(encoding="utf-8")
    cells = load_cells(REPO_ROOT / "results", [c.strip() for c in a.cells.split(",") if c.strip()])
    entry = build_entry(text, cells, a.date)
    if a.preview:
        sys.stdout.reconfigure(encoding="utf-8")
        print(entry)
        return 0
    new = prepare_append(text, entry)
    LEDGER.write_text(new, encoding="utf-8", newline="\n")
    digest = re.search(r"prior-entries-sha256: ([0-9a-f]{64})", new[new.index(f"### {NUM} "):]).group(1)
    print(f"appended {NUM}; chain {digest[:12]}")
    r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
