"""Append entry 0059 -- E9 summarizer enforcement: the tau RECOMPUTATION tolerance registered for a cross-platform
recompute (0028's shape). 0023 registers that `summarize_e9` re-derives tau from the archived mapper under the pin and
"refuses on disagreement (1e-9)". That constant held on every x86 rendering and fails on arm64 (the Mac mini, the home
side since 0051): on 2026-10-08 the summarizer refused E-TRUNC's FULL level on tau_V alone. This entry registers 1e-7 in
the check's own units (|a - b| / max(1, |a|, |b|)) as a judgment with the measurement it rests on; the tau every reading
uses stays the config's registered float, so no figure, cell, verdict, rule or band can move. `verdict:` lines: none.

Fail-closed, as 0058: every cited 0023 / 0050 sentence is located by search inside its entry (never a typed line number);
every number is read from files -- the five renderings under results/e9t-full/calibration*/ (x86 Linux at 13 and 1
threads from the box, arm64 at 1 and 8 threads from the Mac, plus the live calibration the summarizer checks), the Llama
cell's calibration vs config/e9fl.toml, and results/e9t-full/summary.json written by `summarize_e9` UNDER the new check
(its `calibration.tau_recompute` block) -- and the script refuses unless the living code carries the change
(`_TAU_TOL = 1e-7`, the recorded drift, the test, append_0057's ordering assertion).

Ordering guard: 0058 and 0051 on the ledger, 0059 absent; 0057 must land AFTER this (its script asserts it).
Run on the machine that holds results/e9t-full/ (the Mac mini).  --date YYYY-MM-DD  --preview
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

NUM, PREV = "0059", "0058"
TOL_OLD, TOL_NEW = 1e-9, 1e-7
FULL = REPO_ROOT / "results" / "e9t-full"
RENDERINGS = [  # label, directory, what produced it
    ("x86 Linux, 13 threads (the box, torch 2.11.0+cu128 CPU path)", FULL / "calibration-x86" / "threads13"),
    ("x86 Linux, 1 thread (the box)", FULL / "calibration-x86" / "threads1"),
    ("arm64 macOS, 1 thread (the Mac mini)", FULL / "calibration-arm64" / "threads1"),
    ("arm64 macOS, 8 threads (the Mac mini)", FULL / "calibration-arm64" / "threads8"),
    ("arm64 macOS, the live `calibration/tau.json` the summarizer checks", FULL / "calibration"),
]


def dist(a: float, b: float) -> float:
    """`_close`'s own units: |a - b| / max(1, |a|, |b|) (summarize_e9), so for tau < 1 it is the absolute gap."""
    return abs(a - b) / max(1.0, abs(a), abs(b))


def f1e(x: float) -> str:
    return "0" if x == 0 else f"{x:.1e}"


def block(text: str, entry: str) -> tuple[str, int]:
    start = text.index(f"### {entry} ")
    nxt = text.find("\n### ", start + 1)
    return text[start:(nxt if nxt > 0 else len(text))], start


def locate(text: str, entry: str, sentence: str) -> int:
    """1-based ledger line of `sentence` inside `entry`'s block; refuses if absent or repeated there."""
    blk, start = block(text, entry)
    assert blk.count(sentence) == 1, f"{entry}: expected exactly one occurrence of {sentence!r}, found {blk.count(sentence)}"
    return text.count("\n", 0, start + blk.index(sentence)) + 1


def read_rendering(d: Path) -> dict:
    tau = json.loads((d / "tau.json").read_text(encoding="utf-8"))
    plat = json.loads((d / "platform.json").read_text(encoding="utf-8")) if (d / "platform.json").exists() else None
    return {"tau": tau["tau"], "mapper": tau["mapper"], "archived_r2_sha256": tau["archived_r2_sha256"],
            "e8_report_sha256": tau["e8_report_sha256"], "upstream_head": tau["upstream_head"], "platform": plat}


def archived_r2_renderings(cfg) -> dict:
    """The archived `results/mapper/<pair>/r2.json` as committed at the pin (LF) and as a Windows checkout renders it
    (CRLF); 0023 pins the CRLF bytes, the box reads the LF ones -- same content, two shas (learning 2026-10-08)."""
    import hashlib
    rel = f"results/mapper/{cfg.pair}/r2.json"
    lf = subprocess.run(["git", "-C", str(cfg.upstream_path), "show", f"{cfg.upstream_sha}:{rel}"],
                        capture_output=True, check=True).stdout
    assert b"\r\n" not in lf, "the committed r2.json is not LF"
    crlf = lf.replace(b"\n", b"\r\n")
    return {"path": rel, "lf": hashlib.sha256(lf).hexdigest(), "crlf": hashlib.sha256(crlf).hexdigest()}


def measure(cfg) -> dict:
    """The five renderings against the config's registered floats, with the assertions the entry's sentences rest on."""
    reg = {k: float(cfg.rule[f"tau_{k}"]) for k in ("K", "V", "agent_K")}
    rows = []
    for label, d in RENDERINGS:
        r = read_rendering(d)
        rows.append({"label": label, "dir": str(d.relative_to(REPO_ROOT)).replace("\\", "/"), "platform": r["platform"],
                     **{k: {"value": float(r["tau"][k]), "dist": dist(reg[k], float(r["tau"][k]))} for k in reg},
                     "mapper": r["mapper"], "archived_r2_sha256": r["archived_r2_sha256"],
                     "e8_report_sha256": r["e8_report_sha256"], "upstream_head": r["upstream_head"]})
    # one mapper, one E8 report, one pin under every rendering; the archived r2.json in one of its TWO renderings
    for key in ("e8_report_sha256", "upstream_head"):
        assert len({row[key] for row in rows}) == 1, f"renderings differ in {key}"
    assert len({json.dumps(row["mapper"], sort_keys=True) for row in rows}) == 1, "renderings differ in mapper bytes"
    assert rows[0]["upstream_head"] == cfg.upstream_sha, "renderings were not computed under the config's pin"
    r2 = archived_r2_renderings(cfg)
    for row in rows:
        assert row["archived_r2_sha256"] in (r2["lf"], r2["crlf"]), \
            f"{row['label']}: archived r2.json sha {row['archived_r2_sha256'][:12]} is neither the LF nor the CRLF rendering of the pinned object"
        row["archived_r2_rendering"] = "LF" if row["archived_r2_sha256"] == r2["lf"] else "CRLF"
    x86, arm = rows[:2], rows[2:]
    for row in x86:
        assert all(row[k]["dist"] <= TOL_OLD for k in reg), f"{row['label']}: outside 1e-9 -- the x86 sentence is false"
    assert any(row["V"]["dist"] > TOL_OLD for row in arm), "arm64 V inside 1e-9 -- the refusal sentence is false"
    assert all(row["K"]["dist"] <= TOL_OLD for row in arm), "arm64 K outside 1e-9 -- the 'V alone' sentence is false"
    assert len({(row["K"]["value"], row["V"]["value"]) for row in arm}) == 1, "arm64 renderings differ across threads"
    assert len({(row["K"]["value"], row["V"]["value"]) for row in x86}) == 2, "x86 renderings identical across threads"
    assert all(row["agent_K"]["dist"] == 0 for row in rows), "agent_K moved: it is read from the E8 report, no arithmetic"
    assert all(row[k]["dist"] <= TOL_NEW for row in rows for k in reg), "a rendering sits outside the NEW tolerance"
    worst = max(row[k]["dist"] for row in rows for k in reg)
    return {"registered": reg, "rows": rows, "worst": worst, "headroom": TOL_NEW / worst, "r2": r2}


def llama(repo_root: Path) -> dict:
    """The 0051 cell passed on the same arm64 machine: its distances sit under 1e-9 by magnitude, not by design."""
    from linear_ceiling.config import load_e9_config
    cfg = load_e9_config(repo_root / "config" / "e9fl.toml", repo_root)
    tau = json.loads((cfg.results_dir / "calibration" / "tau.json").read_text(encoding="utf-8"))["tau"]
    d = {k: dist(float(cfg.rule[f"tau_{k}"]), float(tau[k])) for k in ("K", "V", "agent_K")}
    assert all(v <= TOL_OLD for v in d.values()), "the Llama calibration is NOT within 1e-9 here; the entry's sentence would be false"
    return {"pair": cfg.pair, "dist": d}


def summary_under_new_check() -> dict:
    """`summarize_e9` must have PASSED on FULL under the new check and recorded the drift (the 0028 move)."""
    p = FULL / "summary.json"
    assert p.exists(), f"{p} missing: run `summarize_e9 --config config/e9t-full.toml` under the 1e-7 check first"
    s = json.loads(p.read_text(encoding="utf-8"))
    tr = s["calibration"]["tau_recompute"]
    assert tr["tolerance_rel"] == TOL_NEW, f"summary was written under tolerance {tr['tolerance_rel']}, not {TOL_NEW}"
    assert tr["platform"]["machine"] in ("arm64", "aarch64"), "the summary was not written on the arm64 home side"
    assert all(TOL_OLD < tr[k]["rel_diff_config"] <= TOL_NEW for k in ("V",)), "summary's V drift is not the refused one"
    return {"sha256": sha256_file_bytes(p), "tr": tr, "scored": len(s["fstar_per_handoff"]["same_K"])
            if isinstance(s.get("fstar_per_handoff", {}).get("same_K"), dict) else None}


def check_tree(repo_root: Path) -> None:
    code = (repo_root / "src" / "linear_ceiling" / "summarize_e9.py").read_text(encoding="utf-8")
    assert "_TAU_TOL = 1e-7" in code and "entry 0059" in code and '"tau_recompute"' in code, "summarize_e9.py lacks the 0059 change"
    assert "_TAU_TOL = 1e-9" not in code, "the old constant is still in the code"
    tests = (repo_root / "tests" / "test_summarize_e9.py").read_text(encoding="utf-8")
    assert "test_0059_tau_recompute_tolerance" in tests, "the 0059 test is missing"
    a57 = repo_root / "docs" / "drafts" / "append_0057.py"
    if a57.exists():
        assert '"### 0059 "' in a57.read_text(encoding="utf-8"), "append_0057.py must assert 0059 is on the ledger first"


def build_entry(date: str, m: dict, ll: dict, sm: dict, lines: dict, text: str) -> str:
    reg = m["registered"]
    rows = m["rows"]
    tbl = ["| rendering | τ_K | gap | τ_V | gap |", "|---|---|---|---|---|",
           f"| **config (registered; Windows x86 at 0023)** | `{reg['K']!r}` | — | `{reg['V']!r}` | — |"]
    for row in rows:
        tbl.append(f"| {row['label']} | `{row['K']['value']!r}` | {f1e(row['K']['dist'])} | `{row['V']['value']!r}` | {f1e(row['V']['dist'])} |")
    arm_v = rows[2]["V"]["dist"]
    x86_worst = max(row[k]["dist"] for row in rows[:2] for k in ("K", "V"))
    refusal = f"`E9 SUMMARY REFUSED: config tau_V {reg['V']!r} != recomputed {rows[4]['V']['value']!r}`"
    tr = sm["tr"]
    return f"""### {NUM} — {date} — E9 summarizer enforcement: the τ recomputation tolerance registered for a cross-platform recompute (1e-9 → 1e-7 in the check's units); no rule, τ, band, score, handoff or cell change

**What this is, and when.** After E-TRUNC's FULL level ran (2026-10-08, registered by 0055; `results/e9t-full/report.json`
complete, 35 of 35 scored, the home mirror fingerprint-verified) and BEFORE any figure of it is stated. 0023 registers that
`summarize_e9` re-derives τ from the archived mapper and "{lines['0023_sentence']}" (ledger line {lines['0023']}); the constant
behind that sentence is `_TAU_TOL` in `summarize_e9.py`, applied as |a − b| ≤ tol · max(1, |a|, |b|), so for τ < 1 it is an
absolute gap. The home side of this run is the operator's Mac mini (arm64), as it was for 0051. Under that constant the
summarizer refused FULL on τ_V alone: {refusal}. This entry registers the tolerance for that check as a judgment, with the
measurement it rests on — the move 0028 made for the keep-subset re-score. It is enforcement of 0023, not a change to anything
0023 registers about the rule, τ, the band or the cells.

**Measured: five renderings of the same arithmetic.** `--calibrate-tau` under the pin `{rows[0]['upstream_head'][:12]}…` on the same
mapper bytes (`{rows[0]['mapper']['json_sha256'][:12]}…` / `{rows[0]['mapper']['safetensors_sha256'][:12]}…`), the same E8 report
(`{rows[0]['e8_report_sha256'][:12]}…`) and the same archived `{m['r2']['path']}` — read on the box as the LF object committed at the pin
(`{m['r2']['lf'][:12]}…`) and at home as its CRLF checkout rendering (`{m['r2']['crlf'][:12]}…`, the sha 0023 pins at ledger line
{lines['0023_r2']}; the LF bytes with CRLF line ends, derived here); files under `results/e9t-full/calibration*/` with their
`platform.json`; "gap" is the check's own distance to the config float.

{chr(10).join(tbl)}

Every x86 rendering sits within 1e-9 (worst {f1e(x86_worst)}) and the two x86 renderings differ from each other, so the registered
floats are one x86 rendering among several, not a property of the mapper. The arm64 renderings are identical at 1 and 8 threads
(deterministic, not thread-order jitter) and sit {f1e(arm_v)} from the config on V. τ_agent_K is read from the E8 report with no
arithmetic and is identical everywhere (gap 0). The second-family cell (0051, `{ll['pair']}`) passed on this same machine with gaps
K {f1e(ll['dist']['K'])} / V {f1e(ll['dist']['V'])} / agent_K {f1e(ll['dist']['agent_K'])} — under 1e-9 by magnitude, not by design.

**Registered check (replaces the 1e-9 for the recomputation).** The recorded calibration's and the config's τ_K, τ_V and τ_agent_K
must each reproduce the recomputed value within **{TOL_NEW:.0e}** in `_close`'s units; a gap beyond refuses the summary, as before.
{TOL_NEW:.0e} is three orders below the four decimals this ledger states τ to (0023: τ_K 0.3186, τ_V 0.4867) and {m['headroom']:.0f}× the
worst gap measured above ({f1e(m['worst'])}). **The τ every reading uses remains the config's registered float**; the recomputation is a
check that the archived mapper still yields it, and no figure, f*, cell or verdict depends on the recomputed value, so nothing can
move by this entry. `summarize_e9` now records the gap and the platform it was measured on in `summary.json`
(`calibration.tau_recompute`) and prints them, as 0028 made it print the re-score jitter. **Measured by `summarize_e9` on FULL
under this check** (`results/e9t-full/summary.json` `{sm['sha256'][:12]}…`, written on {tr['platform']['machine']} {tr['platform']['system']},
numpy {tr['platform']['numpy']}): gaps to the config K {f1e(tr['K']['rel_diff_config'])}, V {f1e(tr['V']['rel_diff_config'])},
agent_K {f1e(tr['agent_K']['rel_diff_config'])}; to the recorded calibration K {f1e(tr['K']['rel_diff_recorded'])},
V {f1e(tr['V']['rel_diff_recorded'])}. The summary passed; its figures enter by their own entry (0057), never by this one.

**What this does NOT touch.** 0023's per-token judgment "{lines['0023_pertoken_sentence']}" (ledger line {lines['0023_pertoken']}) — a
different check, on the f* statistic, unchanged; the 1e-6 cross-checks of the held-out R² against the archived `r2.json` and E8 arm
(a) (`_TOL`), unchanged; τ_K, τ_V, τ_agent_K and every τ ladder; the rule section; the bands; every verdict and cell (H-E9 0029,
H-E9L 0036, 0038, the Llama cells 0044/0053/0051); 0050's sentence that its config "{lines['0050_sentence']}" (ledger line
{lines['0050']}), which the measurement above confirms at full precision. `verdict:` lines: none.

**Lesson, stated once.** A registered float check is a rendering of the platform that produced it (learnings 2026-10-08, the
coverage-sha and `r2.json` CRLF pins are the same lesson in bytes); an enforcement constant that must hold on a second home
platform is registered with the renderings it was measured on, as here.

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
    assert f"### {PREV} " in text and "### 0051 " in text and f"### {NUM} " not in text, f"ordering: {PREV} and 0051 present, {NUM} absent"
    assert "### 0057 " not in text, "0057 is on the ledger already; this entry had to precede it"

    s0023 = "recomputes it under the pin and refuses on disagreement (1e-9)"
    s0023_pt = "judged to 1e-9 relative"
    s0050 = "this config agrees with it at 1e-9"
    lines = {"0023": locate(text, "0023", s0023), "0023_sentence": s0023,
             "0023_pertoken": locate(text, "0023", s0023_pt), "0023_pertoken_sentence": s0023_pt,
             "0050": locate(text, "0050", s0050), "0050_sentence": s0050}

    check_tree(REPO_ROOT)
    from linear_ceiling.config import load_e9_config
    cfg = load_e9_config(REPO_ROOT / "config" / "e9t-full.toml", REPO_ROOT)
    m = measure(cfg)
    lines["0023_r2"] = locate(text, "0023", f"sha256 `{m['r2']['crlf'][:12]}`")   # 0023 pins the CRLF rendering
    ll = llama(REPO_ROOT)
    sm = summary_under_new_check()
    entry = build_entry(a.date, m, ll, sm, lines, text)
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
