"""Append entry 0057 -- E-TRUNC RAN (registered by 0055); figures only, written ONLY from `summarize_e9_trunc` run
in-process: `summarize_e9.summarize` on each of the four levels first (each level's own fail-closed reader), then
`compare_levels` (M_∩ in the FULL frame, the void gate, the paired statistics, the pre-registered reading). DESCRIPTIVE:
no `verdict:` line, no hypothesis row, no cell moves. The reading's three outcomes ("length" / "the handoffs" /
"unattributed") were registered in 0055 (ruling 1); this entry prints the one the reader returns, never chooses it.

Ordering guard: 0055 on the ledger, 0057 absent (file-order chaining, the 0054 precedent: 0048/0049/0051 may land before
or after). Run facts the reader cannot know come as arguments and are refused when missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC, FULL launch>   --finished <UTC, last level's exit>
  --dataset <repo_id>       the R8 backup of results/e9t-{full,l65,l49,l32}/ and results/e9t/, verified by
                            tools/hf_verify_backup.py (exit 0) before this runs
  --cutoff-reason "<text>"  required if any level closed partial (0035's stopping rule); refused otherwise
  --date <YYYY-MM-DD>       defaults to --finished's date
  --preview                 print, do not append (stdout forced to UTF-8: a cp1252 console dies on the first tau)
The summarizer gate re-scores each level from its records: budget tens of minutes uninterrupted (learning 2026-10-04,
"a figures append script re-runs the summarizer as its gate"). Runbook: docs/2026-10-04-e-trunc-gpu-runbook.md.
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, REG = "0057", "0055"
SPEAK_FOR = ("the comparison speaks for the handoffs whose receiver re-renders enough of the late sender context to survive "
             "head truncation, not for the long cohort as a whole")


def f4(x):
    return "n/a" if x is None else f"{x:.4f}"


def erratum_0055(shrink: dict) -> str:
    """0055 says re-matching 'loses more than the removal on N handoffs'; N is the reader's count with re-matching loss
    ABOVE 0.05 of |M_FULL|. Stated from the record, never typed (review 2026-10-04)."""
    per = shrink["per_handoff"].values()
    n_any = sum(1 for v in per if v["rematching_loss"] > 0)
    n_beyond_removal = sum(1 for v in per if v["rematching_loss"] > 1 - v["survivable_fraction"])
    return (f"**Erratum to {REG}.** Its sentence \"aligner re-matching loses more than the removal on "
            f"{shrink['n_with_rematching_loss_over_0_05']} handoffs\" states the count with re-matching loss above 0.05 of "
            f"|M_FULL| (`n_with_rematching_loss_over_0_05` in `results/e9t/shrinkage.json`); {n_any} handoffs have any "
            f"re-matching loss, and {n_beyond_removal} lose more to re-matching (survivable − ratio) than to the removal itself "
            f"(1 − survivable). Its figures are unchanged.")


def coverage_renderings(levels: dict, ledger_text: str) -> str:
    """Entry 0055 pins each level's `align/coverage.json` sha from the home file's RAW bytes, which were CRLF (written
    on Windows). The box reproduces the same lines as LF and the mirror carries that rendering. Both shas are DERIVED
    from the mirror bytes here and checked against 0055's pins (sentence search; never typed) — the 0051 lesson
    (learning 2026-10-08 `a-registered-sha-pin-is-a-rendering`)."""
    import hashlib
    block = ledger_text[ledger_text.index(f"### {REG} "):]
    block = block[:block.index("\n### ", 1)] if "\n### " in block[1:] else block
    m = re.search(r"coverage sha256 FULL `([0-9a-f]{12})`,\s*L65\s*`([0-9a-f]{12})`,\s*L49\s*`([0-9a-f]{12})`,\s*L32\s*`([0-9a-f]{12})`",
                  block, re.S)
    assert m, f"entry {REG} no longer states the four coverage shas where expected; re-anchor"
    pins = dict(zip(("FULL", "L65536", "L49152", "L32768"), m.groups()))   # the reader's level names
    rows = []
    for name, cfg in levels.items():
        raw = (cfg.results_dir / "align" / "coverage.json").read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        crlf = lf.replace(b"\n", b"\r\n")
        sha_lf, sha_crlf = hashlib.sha256(lf).hexdigest(), hashlib.sha256(crlf).hexdigest()
        pin = pins[name]
        assert sha_crlf.startswith(pin) or sha_lf.startswith(pin), \
            f"{name}: {REG}'s coverage pin {pin} is neither rendering of the mirror's coverage.json"
        which = "CRLF" if sha_crlf.startswith(pin) else "LF"
        other = sha_lf if which == "CRLF" else sha_crlf
        rows.append(f"{name} pinned `{pin}…` ({which}; the other rendering `{other[:12]}…`)")
    return ("**Coverage files, two renderings of one content.** Entry " + REG + " pins each level's `align/coverage.json` by "
            "the sha of the home file's raw bytes; the box reproduced the same lines in the other line-ending rendering and "
            "the mirror carries that one. Both shas are derived from the mirror here: " + "; ".join(rows) + ".")


def build_entry(out: dict, meta: dict) -> str:
    """The entry text from `compare_levels`' output and the run facts. Every number comes from `out`."""
    names = list(out["by_level"])
    full = out["by_level"]["FULL"]
    rd = out["reading"]
    refs = out["references"]
    taus = list(full["fstar_median_over_handoffs"])
    partial = [n for n, p in out["levels"].items() if p["partial"]]
    lines = []
    for n in names:
        b = out["by_level"][n]
        L = "full |S|" if b["sender_head_truncate"] is None else f"S[−{b['sender_head_truncate']:,}:]"
        fs = ", ".join(f"f*({t}) {f4(b['fstar_median_over_handoffs'][t])}" for t in taus)
        far = b["far_from_seam_pooled"]
        pd = b["paired_mean_delta_K_minus_full"]
        bs = pd["bootstrap"]
        paired = ("" if n == "FULL" else
                  f"; paired mean δ_K − FULL per handoff median {f4(pd['median'])} (p10 {f4(pd['p10'])}, p90 {f4(pd['p90'])}; "
                  f"bootstrap 95 % [{f4(bs['lower_2.5'])}, {f4(bs['upper_97.5'])}], seed {bs['seed']}, {bs['reps']:,} reps)")
        lines.append(f"- **{n}** ({L}): median over handoffs of mean δ_K {f4(b['mean_delta_K_median_over_handoffs'])}, of the fraction "
                     f"over τ_K {f4(b['frac_over_tau_K_median_over_handoffs'])}; {fs}; far-from-seam ({far['bin']}) pooled median "
                     f"{f4(far['median'])}, mean {f4(far['mean'])} over {far['n_tokens']:,} tokens{paired}.")
    unscored = {n: v for n, v in out["unscored_by_level"].items() if v}
    unscored_txt = ("every level scored every handoff any level scored" if not unscored else
                    "; ".join(f"{n} did not score " + ", ".join(f"`{h}`" for h in v) for n, v in unscored.items()))
    void_txt = ", ".join(f"`{h}`" for h in out["void"]) or "none"
    pins = "; ".join(f"{n} config `{p['config_sha256'][:12]}…` report `{p['report_sha256'][:12]}…`" for n, p in out["levels"].items())
    cutoff = (f" Levels closed partial under 0035's stopping rule: {', '.join(partial)}; cutoff reason: {meta['cutoff_reason']}."
              if partial else "")
    return f"""### {NUM} — {meta['date']} — E-TRUNC ran `[BASELINE, DESCRIPTIVE]`: head truncation of the sender context at four levels on 0036's long handoffs; the registered reading at the native cap reads "{rd['reads_as']}"; descriptive, no cell moves

**Setup, as registered ({REG}).** {meta['box']}; FULL launched {meta['launched']}, last level finished {meta['finished']};
upstream pin `{out['upstream_sha'][:12]}…` for all four levels; {pins}. Backup: `{meta['dataset']}` (R8, verified both
ways before this entry).{cutoff} Runbook `docs/2026-10-04-e-trunc-gpu-runbook.md`.

{meta['coverage_txt']}

**Coverage and the void gate (ruling 2).** {out['n_scored_at_every_level']} handoffs scored at every level ({unscored_txt}).
Under the registered floor |M_∩| ≥ {out['min_common_matched']:,} common matched tokens, {out['n_void']} are void and named, never
pooled: {void_txt}. **{out['n_used']} handoffs enter the comparison**, carrying {out['n_common_total']:,} common tokens (pooled
|M_∩| / |M_FULL| over them {f4(out['pooled_ratio_used'])}). Stated limitation (0055): {SPEAK_FOR}.

**Figures on M_∩, per level (`summarize_e9_trunc` in-process: each level's `summarize_e9` passed first; medians over the
{out['n_used']} entering handoffs, `e7_stats` convention; δ in R²'s units, 0023; τ_K = {out['tau_K']!r}).**

{chr(10).join(lines)}

**The registered reading (ruling 1, 0055).** At the native-cap level {rd['level']}, the far-from-seam ({refs['seam_far_bin']}) pooled
median δ_K on M_∩ is **{f4(rd['far_from_seam_median_on_M_cap'])}** (FULL on the same tokens {f4(rd['full_far_from_seam_median_on_M_cap'])}),
against the scaled-short level {f4(rd['short_scaled_level'])} (0038, read from `{refs['short_scaled']['path']}` `{refs['short_scaled']['sha256'][:12]}…`)
and the long level {f4(rd['long_level'])} (0036, `{refs['long']['path']}` `{refs['long']['sha256'][:12]}…`), margin ±{rd['margin_abs']}:
**the residual short↔long far-from-seam gap reads as "{rd['reads_as']}"**. M_∩ sits at late sender positions while the two
reference medians were pooled over full matched sets; the reader states this beside the reading and so does this entry.

{meta['erratum']}

**What this does NOT touch.** Every verdict and cell (H-E9 0029, H-E9L 0036, the scaled short cell 0038, the Llama cells);
τ, the rule, the bands; 0045's tail figures. "Length" here means causal-prefix length on the tokens the receiver re-renders
from the late part of S, not number of turns.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the long half of one corpus under the scaled
receiver; YaRN receivers only — the L32-native cell is deferred (ruling 3), so nothing here compares native with YaRN on the
same tokens and 0036's bridge control (W6) stays the only such evidence; f* is read as the oracle removal fraction (0058);
generation quality after reuse not measured.

prior-entries-sha256: PLACEHOLDER
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", required=True)
    ap.add_argument("--launched", required=True)
    ap.add_argument("--finished", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--cutoff-reason", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    a.date = a.date or a.finished[:10]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"

    ledger = REPO_ROOT / "ledger" / "ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert f"### {REG} " in text and f"### {NUM} " not in text, f"ordering: {REG} present, {NUM} absent"

    from linear_ceiling.config import load_e9_config
    from linear_ceiling.summarize_e9 import summarize
    from linear_ceiling.summarize_e9_trunc import compare_levels, load_levels
    full = load_e9_config(REPO_ROOT / "config" / "e9t-full.toml", REPO_ROOT)
    levels = load_levels(full, REPO_ROOT)
    for name, cfg in levels.items():                     # the gate: each level's own fail-closed reader first
        summarize(cfg, runner=subprocess.run)
    out = compare_levels(levels, REPO_ROOT)              # raises on any disagreement; nothing is written then
    import json
    shrink = json.loads((REPO_ROOT / full.trunc["out_dir"] / "shrinkage.json").read_text(encoding="utf-8"))
    partial = [n for n, p in out["levels"].items() if p["partial"]]
    assert bool(partial) == bool(a.cutoff_reason), \
        "--cutoff-reason is required exactly when a level closed partial (0035's stopping rule)"
    entry = build_entry(out, {"date": a.date, "box": a.box, "launched": a.launched, "finished": a.finished,
                              "dataset": a.dataset, "cutoff_reason": a.cutoff_reason,
                              "erratum": erratum_0055(shrink),
                              "coverage_txt": coverage_renderings(levels, text)})
    if a.preview:
        sys.stdout.reconfigure(encoding="utf-8")
        print(entry)
        return 0
    new = text + ("" if text.endswith("\n") else "\n") + "\n" + entry
    head = _ENTRIES_HEAD.search(new)
    digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
    new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
    ledger.write_text(new, encoding="utf-8", newline="\n")
    print(f"appended {NUM}; chain {digest[:12]}")
    r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
