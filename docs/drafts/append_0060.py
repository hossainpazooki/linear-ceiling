"""Append entry 0060 -- the MLSys 2027 cut: the FIGURE SET frozen. The experiments run since the LCFM reviews
(2026-09-25/28; map `docs/2026-09-30-review-response-map.md`), each mapped to the reviewer point it answers, each figure
READ from its summary file in-process with the file's sha, each entry located by its header line (search, never typed).
Nothing registered after this entry enters the MLSys submission; the manuscript tree is pinned at submission time by the
reconciliation record (the camera-ready precedent, `docs/reviews/2026-10-07-…reconciled.md`), not here. DESCRIPTIVE:
no `verdict:` line, no cell moves, nothing runs.

Ordering guard: 0057 and 0059 on the ledger (file order ends 0059, 0057), 0060 absent. Runs on the machine that holds the
small summary files (Windows: `results/e9fl/summary.json` and `results/e9t/compare.json` were copied from the Mac mini on
2026-10-09; every other file is native here).  --date YYYY-MM-DD  --preview
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&` (`rm`, it is untracked).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.hashing import sha256_file_bytes  # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM = "0060"
MUST_EXIST = ("0029", "0034", "0036", "0038", "0044", "0045", "0048", "0049", "0051", "0053", "0054", "0055", "0056",
              "0057", "0058", "0059")
R = REPO_ROOT / "results"
FILES = {
    "e9": R / "e9" / "summary.json", "e9l": R / "e9l" / "summary.json", "e9f": R / "e9f" / "summary.json",
    "e9fl": R / "e9fl" / "summary.json", "e9s": R / "e9s" / "compare.json", "e8fa": R / "e8fa" / "summary.json",
    "e9c": R / "e9c" / "summary.json", "cons": R / "consolidation" / "a100" / "summary.json",
    "cache": R / "cache-behavior" / "summary.json", "e9t": R / "e9t" / "compare.json",
    "tail_e9l": R / "e9l" / "tail.json", "tail_e9": R / "e9" / "tail.json", "tail_e9s": R / "e9s" / "tail.json",
    "tail_e9f": R / "e9f" / "tail.json",
}
MAP = "docs/2026-09-30-review-response-map.md"
PLAN = "docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md"


def f4(x):
    return "n/a" if x is None else f"{x:.4f}"


def pct(x):
    return f"{100 * x:.1f} %"


def header_line(text: str, entry: str) -> int:
    """1-based ledger line of `### <entry> ` -- unique by construction; refuses on 0 or 2+."""
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", text, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} header lines"
    return text.count("\n", 0, hits[0]) + 1


def load_all() -> tuple[dict, dict]:
    data, shas = {}, {}
    for key, p in FILES.items():
        assert p.exists(), f"{p} is missing; the figure set cannot be read"
        data[key] = json.loads(p.read_text(encoding="utf-8"))
        shas[key] = sha256_file_bytes(p)
    return data, shas


def figures(d: dict) -> dict:
    """Every figure the entry states, read by key. Assertions pin the shape the sentences rely on."""
    g = {}
    # the Qwen cells (on the ledger before the reviews; restated for the table's completeness)
    for cell in ("e9", "e9l"):
        s = d[cell]
        g[cell] = {"n": s["fstar"]["same_K"]["n"], "same_K": s["fstar"]["same_K"]["median"],
                   "cross_K": s["fstar"]["cross_K"]["median"], "band": s["band_outcome"],
                   "null_same_K": s["delta_null"]["same_K"]["median_token_mean"]}
    g["e9l"]["bridge_K"], g["e9l"]["bridge_V"] = d["e9l"]["bridge"]["median_fstar_K"], d["e9l"]["bridge"]["median_fstar_V"]
    g["e9l"]["bridge_reading"] = d["e9l"]["bridge"]["reading"]
    # the second pair (0044 short, 0051 long at a NATIVE receiver, 0053 E8 amendment)
    for cell in ("e9f", "e9fl"):
        s = d[cell]
        g[cell] = {"n": s["fstar"]["same_K"]["n"], "same_K": s["fstar"]["same_K"]["median"],
                   "cross_K": s["fstar"]["cross_K"]["median"], "band": s["band_outcome"],
                   "null_same_K": s["delta_null"]["same_K"]["median_token_mean"], "rope": s.get("rope")}
    assert not g["e9fl"]["rope"], "the Llama long cell must be a NATIVE receiver (no rope block)"
    k1 = d["e8fa"]["recomputed"]["1"]
    g["e8fa"] = {"generic_K": k1["generic"]["K"], "generic_V": k1["generic"]["V"], "agent_K": k1["agent"]["K"],
                 "agent_V": k1["agent"]["V"], "band_K": k1["band_outcome"]["K"], "band_V": k1["band_outcome"]["V"],
                 "n_seqs": d["e8fa"]["per_k"]["1"]["bootstrap"]["K"]["n_seqs"]}
    # the same-model extension (0048): two more receivers on the 60 texts, medians per cohort with cluster bootstraps
    cons = d["cons"]["models"]
    g["cons"] = {m: {c: {"fstar": cons[m][c]["median"]["fstar"], "fstar_ci": cons[m][c]["cluster_bootstrap_95"]["fstar"],
                         "mean_delta": cons[m][c]["median"]["mean_delta"], "n": int(cons[m][c]["handoffs"]),
                         "zero": int(cons[m][c]["zero_fstar_handoffs"])}
                     for c in ("e9s_K", "e9l_K")} for m in ("qwen4", "smollm3")}
    assert all(v["fstar"] == 0.0 for m in g["cons"].values() for v in m.values()), "0048's 'median 0 on every cohort' no longer holds"
    # calibration size (0034): the n = 420 refit on the kept-subset cross arm
    agg = d["e9c"]["aggregate"]
    g["e9c"] = {"n": agg["n_handoffs"], "cross_reg": agg["cross_K"]["fstar_tau_reg"]["median"],
                "cross_prior": agg["cross_K"]["prior_fstar_tau_reg"]["median"]}
    # the scaled-short cell (0038) and its configuration share
    g["e9s"] = {"n": d["e9s"]["n_handoffs"], "share_far": d["e9s"]["configuration_share"]["seam_far"],
                "share_f003": d["e9s"]["configuration_share"]["fstar_0.03"]}
    # E-TRUNC (0057)
    rd = d["e9t"]["reading"]
    assert rd["reads_as"] == "unattributed", "the reading on the record is not the one this entry states"
    l32 = d["e9t"]["by_level"][rd["level"]]["paired_mean_delta_K_minus_full"]
    g["e9t"] = {"n_used": d["e9t"]["n_used"], "n_void": d["e9t"]["n_void"], "n_all": d["e9t"]["n_scored_at_every_level"],
                "tokens": d["e9t"]["n_common_total"], "l32": rd["far_from_seam_median_on_M_cap"],
                "full": rd["full_far_from_seam_median_on_M_cap"], "short": rd["short_scaled_level"],
                "long": rd["long_level"], "margin": rd["margin_abs"], "reads_as": rd["reads_as"],
                "paired": l32["median"], "lo": l32["bootstrap"]["lower_2.5"], "hi": l32["bootstrap"]["upper_97.5"],
                "levels": list(d["e9t"]["levels"])}
    # the tails (0045), per cell
    tails = {}
    for cell in ("e9l", "e9", "e9s", "e9f"):
        t = d[f"tail_{cell}"]
        frac = t["pooled"]["same_K"]["fraction_over_tau"]
        key = next(k for k in frac if abs(float(k) - float(t["tau"]["K"])) < 1e-9)      # the registered tau_K, by value
        means = [rec["same_K"]["mean"] for rec in t["per_handoff"].values()]            # 0045's per-handoff MEAN, max over handoffs
        tails[cell] = {"frac_over_tau": frac[key], "max_handoff_mean": max(means), "n_handoffs": len(means),
                       "after_top10": t["pooled"]["same_K"]["mean_after_removing_top"]["0.10"],
                       "after_top20": t["pooled"]["same_K"]["mean_after_removing_top"]["0.20"],
                       "n_tokens": t["pooled"]["same_K"]["n_tokens"], "n_bins": len(t["seam_left_bins"]["same_K"])}
    g["tails"] = tails
    tl = d["tail_e9l"]
    g["native_window"] = {"cap": tl["native_window"]["cap"], "n_tokens": tl["native_window"]["n_tokens"],
                          "share": tl["native_window"]["share_of_matched"],
                          "median": tl["native_window"]["same_K"]["median"], "mean": tl["native_window"]["same_K"]["mean"],
                          "receiver_median": tl["receiver_length"]["median"], "receiver_n": tl["receiver_length"]["n"]}
    # cache behaviour (0049): next-token sensitivity, three arms, no band
    arms = d["cache"]["arms"]
    g["cache"] = {a: {"kl": arms[a]["mean_kl"]["median"], "top1": arms[a]["top1_agreement"]["median"], "n": arms[a]["mean_kl"]["n"]}
                  for a in ("reuse", "random", "scrambled")}
    g["cache"]["scored"] = d["cache"]["scored"]
    g["cache"]["interpretation"] = d["cache"]["interpretation"]
    return g


def build_entry(date: str, g: dict, shas: dict, lines: dict, map_sha: str, plan_sha: str) -> str:
    L = lines
    s12 = {k: v[:12] for k, v in shas.items()}
    c = g["cache"]
    t = g["tails"]
    nw = g["native_window"]
    e = g["e9t"]
    cons = g["cons"]
    rows = [
        "| reviewer point (map row) | experiment, entry (ledger line) | figure read from the record (file sha12) |",
        "|---|---|---|",
        (f"| **W7 narrow**: one pair, one agent family, a 50-sequence mapper | second source→receiver pair, Llama-3.2-3B → 3.1-8B at its own "
         f"τ: short cell 0044 (line {L['0044']}), E8 amendment 0053 (line {L['0053']}), long cell at a NATIVE receiver 0051 (line {L['0051']}); "
         f"same-model extension 0048 (line {L['0048']}): Qwen3-4B and SmolLM3-3B on the 60 texts — four receivers, three families; "
         f"calibration size 0034 (line {L['0034']}) | 0044: same-model f*(τ_K) median {f4(g['e9f']['same_K'])} over {g['e9f']['n']} handoffs, cross "
         f"{f4(g['e9f']['cross_K'])} (`{s12['e9f']}`); 0051: {f4(g['e9fl']['same_K'])} over {g['e9fl']['n']}, cross {f4(g['e9fl']['cross_K'])} "
         f"(`{s12['e9fl']}`); 0053 (k = 1, {g['e8fa']['n_seqs']} agent sequences): generic K/V R² {f4(g['e8fa']['generic_K'])}/{f4(g['e8fa']['generic_V'])}, "
         f"agent {f4(g['e8fa']['agent_K'])}/{f4(g['e8fa']['agent_V'])}, bands {g['e8fa']['band_K']}/{g['e8fa']['band_V']} (`{s12['e8fa']}`); "
         f"0048: same-model f*(τ_K) median {f4(cons['qwen4']['e9s_K']['fstar'])} on every cohort — Qwen3-4B short / long "
         f"(n {cons['qwen4']['e9s_K']['n']} / {cons['qwen4']['e9l_K']['n']}, zero on {cons['qwen4']['e9s_K']['zero']} / {cons['qwen4']['e9l_K']['zero']}; "
         f"median mean δ_K {f4(cons['qwen4']['e9s_K']['mean_delta'])} / {f4(cons['qwen4']['e9l_K']['mean_delta'])}), SmolLM3-3B "
         f"(zero on {cons['smollm3']['e9s_K']['zero']} / {cons['smollm3']['e9l_K']['zero']}; {f4(cons['smollm3']['e9s_K']['mean_delta'])} / "
         f"{f4(cons['smollm3']['e9l_K']['mean_delta'])}) (`{s12['cons']}`); 0034: kept-subset cross arm at the n = 420 refit {f4(g['e9c']['cross_reg'])} "
         f"vs {f4(g['e9c']['cross_prior'])} at n = 50, {g['e9c']['n']} handoffs (`{s12['e9c']}`) |"),
        (f"| **W2 length not isolated**: \"truncating the sender context of the same handoffs would isolate it\" | E-TRUNC 0055 (line {L['0055']}) "
         f"ran as 0057 (line {L['0057']}): head truncation at {len(e['levels'])} levels on the 35 long handoffs | {e['n_all']} scored at every "
         f"level, {e['n_void']} void under the registered floor, {e['n_used']} enter on {e['tokens']:,} common tokens; at the native cap the "
         f"far-from-seam median on M_∩ is {f4(e['l32'])} (FULL on the same tokens {f4(e['full'])}) against scaled-short {f4(e['short'])} and long "
         f"{f4(e['long'])}, margin ±{e['margin']} → **\"{e['reads_as']}\"**, the value above both references; paired per-handoff median "
         f"{f4(e['paired'])}, bootstrap [{f4(e['lo'])}, {f4(e['hi'])}] (`{s12['e9t']}`) |"),
        (f"| **W3 mean vs tail**: \"a mean criterion can pass while the tail still matters\" | corrective 0045 (line {L['0045']}): the per-token "
         f"tail per cell from `e9_tail`; corrective 0058 (line {L['0058']}): f* read as the oracle REMOVAL fraction, not a lower bound on "
         f"recompute | tokens over τ_K on the same-model K arm: long {pct(t['e9l']['frac_over_tau'])}, short {pct(t['e9']['frac_over_tau'])}, "
         f"scaled-short {pct(t['e9s']['frac_over_tau'])}, Llama short {pct(t['e9f']['frac_over_tau'])}; per-handoff maximum mean {f4(t['e9l']['max_handoff_mean'])} / "
         f"{f4(t['e9']['max_handoff_mean'])} / {f4(t['e9s']['max_handoff_mean'])} / {f4(t['e9f']['max_handoff_mean'])}; long-cell pooled mean after removing the "
         f"top 10 % / 20 % of tokens {f4(t['e9l']['after_top10'])} / {f4(t['e9l']['after_top20'])} (`{s12['tail_e9l']}`, `{s12['tail_e9']}`, `{s12['tail_e9s']}`, `{s12['tail_e9f']}`) |"),
        (f"| **W4 framing**: most matched tokens inside the native window, receivers short | 0045 (line {L['0045']}): the native-window subset and "
         f"|R| per cell | long cell: {pct(nw['share'])} of matched tokens at sender positions ≤ {nw['cap']:,} ({nw['n_tokens']:,} tokens), their "
         f"median / mean δ_K {f4(nw['median'])} / {f4(nw['mean'])}; receiver length median {nw['receiver_median']:,} tokens over {nw['receiver_n']} handoffs (`{s12['tail_e9l']}`) |"),
        (f"| **W5 Corollary 3 with medians** | 0045 (line {L['0045']}): seam-bin MEANS beside the medians, per cell | {t['e9l']['n_bins']} seam bins "
         f"with mean and median in each cell's `tail.json` (`{s12['tail_e9l']}`); the submitted LCFM text printed no bin mean (map row W5) |"),
        (f"| **W6 Prop. 4 under YaRN** | bridge control 0036 (line {L['0036']}) and at every E-TRUNC level (0057); the second pair's long cell at a "
         f"NATIVE receiver, 0051 | 0036 bridge: scaled vs native receiver f*(τ_K) K {f4(g['e9l']['bridge_K'])} / V {f4(g['e9l']['bridge_V'])} → "
         f"{g['e9l']['bridge_reading']} (`{s12['e9l']}`); 0051 carries no `[e9.rope]` block — no registered RoPE override; the Llama "
         f"models' built-in `llama3` scaling is the native receiver (`{s12['e9fl']}`) |"),
        (f"| **W1 behavioural validation**: \"next-token KL or top-1 agreement\" | cache behaviour 0049 (line {L['0049']}): next-token sensitivity of "
         f"the receiver to reading an assembled same-model cache, three arms, descriptive | over {c['scored']} long handoffs: reuse median KL "
         f"{f4(c['reuse']['kl'])} nats / top-1 {pct(c['reuse']['top1'])}; random {f4(c['random']['kl'])} / {pct(c['random']['top1'])}; cyclic "
         f"(0049's name; the file's `scrambled` arm) {f4(c['scrambled']['kl'])} / {pct(c['scrambled']['top1'])} (`{s12['cache']}`); the reader's own words: \"{c['interpretation']}\" — "
         f"no task-quality band exists; E-BEH's HOLDS / DEGRADES bands stay unregistered and unrun |"),
        (f"| **W8 what HOLDS could have failed against** | null pairing on every same-model cell: 0029 (line {L['0029']}), 0036, and now 0051 | "
         f"null-pairing median token mean on K: short {f4(g['e9']['null_same_K'])}, long {f4(g['e9l']['null_same_K'])}, Llama short "
         f"{f4(g['e9f']['null_same_K'])}, Llama long {f4(g['e9fl']['null_same_K'])} — against same-model medians of {f4(g['e9']['same_K'])}, "
         f"{f4(g['e9l']['same_K'])}, {f4(g['e9f']['same_K'])}, {f4(g['e9fl']['same_K'])} f*(τ_K) (`{s12['e9']}`, `{s12['e9l']}`, `{s12['e9f']}`, `{s12['e9fl']}`) |"),
    ]
    return f"""### {NUM} — {date} — MLSys 2027 cut: the figure set frozen — the experiments run since the LCFM reviews, mapped to the reviewers' points, every figure read from its summary file; conditions discharged or carried; descriptive, no cell moves

**What this entry is.** The LCFM reviews (TE3a and teFN, 2026-09-25/28; decision Accept) are mapped in `{MAP}`
(`{map_sha[:12]}…`) to what the record stated then and what it lacked. Between 2026-10-01 and 2026-10-09 the lacking figures
were produced under this ledger's rules — registered before run, read only by fail-closed summarizers, backed up and
verified — and entered by their own entries. This entry **freezes the figure set the MLSys 2027 submission may draw from**:
the entries named below, each figure as its summary file states it today, with that file's sha. Nothing registered after
this entry enters the submission; a figure that changes re-enters only through a later entry. 0006's gate restated: only
numbers that recompute clean from `results/` via a fail-closed summarizer enter. The manuscript tree and its commit are
pinned at submission by the reconciliation record (the camera-ready precedent, `docs/reviews/2026-10-07-…reconciled.md`),
not by this entry. Nothing is measured here; the draft plan is `{PLAN}` (`{plan_sha[:12]}…`).

**Experiments addressing the reviews, by point.** Lines are the entries' header lines, located by search at append time.

{chr(10).join(rows)}

**Wording invariants the submission carries** (each registered by the entry named): f* is the oracle REMOVAL fraction, not a
lower bound on recompute (0058); the τ every reading uses is the config's registered float, the recomputation check at
1e-7 (0059); short and long cells never pooled, the second pair's cells stated beside the first pair's and never pooled
(0044, 0051); the cross arm never headlined; E-TRUNC's reading stated with its position above both references (0057); no
downstream task-quality claim (0049's reader states none); co-author pilot figures replaced by the operator's registered
runs 0048 and 0049, so 0056's provenance clause is not needed; **where a bound is invoked, the submission states the seam-bin
MEANS** (0045; the LCFM text printed medians only) — an obligation on the text, not a fact about one.

**Conditions.** Discharged: Condition 1 by ruling 0054 (line {L['0054']}); the 0029 description defect by 0045. Carried as
stated limitations, not resolved: the L32-native E-TRUNC cell (ruled in by 0055 ruling 3, deferred by 0055 itself for lack
of an instrument); a second calibration size on the
long cohort (unrun; 0034 covers the short cohort's kept subset); E-BEH bands (unregistered, unrun); issue #21, the R12
recompute of 0051 by a second person (open). Carried as reviewer nits outside this ledger: N1 (template) and N2 (the
unrun appendix) are manuscript matters.

**What this does NOT touch.** No `verdict:` line; every cell as decided (H-E9 0029, H-E9L 0036, 0038, the Llama cells
0044/0053/0051); τ_K, τ_V, τ_agent_K, the band, the ladder, the kept dumps; nothing runs under this entry.

**Numbering.** {NUM} is the next free number in the drafts README; appended after 0057 in file order; ordering guard 0059 and
0057 present, {NUM} absent. Next free number after this entry: 0061.

prior-entries-sha256: PLACEHOLDER
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
    ledger = REPO_ROOT / "ledger" / "ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("\r\n", "\n")
    for n in MUST_EXIST:
        assert f"### {n} " in text, f"ordering: {n} must be on the ledger"
    assert f"### {NUM} " not in text, f"ordering: {NUM} absent"
    assert text.rfind("### 0057 ") > text.rfind("### 0059 "), "file order must end 0059, 0057"
    lines = {n: header_line(text, n) for n in MUST_EXIST}
    for rel in (MAP, PLAN):
        assert (REPO_ROOT / rel).exists(), f"{rel} missing"
    data, shas = load_all()
    g = figures(data)
    entry = build_entry(a.date, g, shas, lines, sha256_file_bytes(REPO_ROOT / MAP), sha256_file_bytes(REPO_ROOT / PLAN))
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
