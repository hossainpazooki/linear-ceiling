"""DRAFT append script for linear-ceiling: entry 0068 (PROVISIONAL number; the drafts README allocates it at staging) --
E8 on the MLPerf Agentic Inference text RAN (registered by 0064): the figures of both cells, written ONLY from files
pinned below by sha256. DESCRIPTIVE: no `verdict:` line, no hypothesis row; band words are 0009's band read for
orientation; H-E8 (0020) does not move.

Why no summarizer runs here, unlike 0053's script: 0064 says the figures entry "runs `summarize_e8` in-process", but the
operator's upstream clone is past the pin on E8's paths, so `check_upstream` refuses in this checkout. The summary ran
instead off the pod in a scratch pair at the pin (operator ruling 2026-11-09), and the operator ruled 2026-11-10 that this
entry cites that run's summary and states its difference from the pod's. This script reads that run's files by digest and
refuses on any other. The entry states what it reads, by digest, and names in one clause each its departures: from
0064's plan (it reads by digest, and no summarizer runs at append); from 0065's sources (the LC side comes from the
re-scored record, because LC's summary has no per-window value); and from lag-ladder 0030's wording of the join (R²
rather than the R² drop, and B1's mean rather than a median). Operator rulings 2026-11-10 keep all three as worded.

PRIVATE DRAFT (briefs). Inputs outside the repository, each named by argument and each pinned:
  --scratch-lc <dir>   the scratch LC tree of the home run: results/<cell>/{summary.json,report.json},
                       results/e8m/recheck/agent_k1.npz, data/<cell>/agent_n50_len1024_seed8.{npy,manifest.json}
  --evidence <dir>     the sitting's evidence folder: results-final/results/<cell>/summary.json (the pod's), pull/*.tgz,
                       pull-final.{log,rc}, aux-final/aux/logs/*, upload.log, home-summary-run.log
  --ll-summary <file>  lag-ladder's home summary.json that its entry 0036 cites (d9131524...)
  --date YYYY-MM-DD  --preview  [--repo-root <path>]
To stage: `0068-docs-patch.py --date D --script-sha16 <this file's reviewed digest>` (copies this file to docs/drafts/append_0068.py, edits the one living doc that
still read the cell as unregistered, appends the allocator block). The preview's last line must read `[ordering guard: ok]`.
Ordering guard: 0064 present, the ledger's last entry is PREV, NUM absent. Runs `ledger_check` after appending. Delete once
appended, chained with `&&`.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=None)
ap.add_argument("--scratch-lc", type=Path, required=True)
ap.add_argument("--evidence", type=Path, required=True)
ap.add_argument("--ll-summary", type=Path, required=True)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
_here = Path(__file__).resolve().parents[2]
R = (a.repo_root or (_here if (_here / "ledger" / "ledger.md").exists() else Path.home() / "dev" / "linear-ceiling")).resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.config import load_e8_config                         # noqa: E402
from linear_ceiling.e7_stats import quantile                             # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
from linear_ceiling.summarize_e8 import _TOL, _seq_r2                     # noqa: E402

NUM, PREV, REG = "0068", "0067", "0064"
CELLS = ("e8m", "e8mf")
S, E = a.scratch_lc.resolve(), a.evidence.resolve()
PIN = {   # full sha256; "text" = linear_ceiling.hashing.sha256_text_file (newline-normalized), else raw bytes
    "e8m": {"report": "cb5c362dfb26883260c746b03fc9bbc65cdd491b6fcb217ec1b6a2cae517e0f9",
            "home_summary_text": "808959fbfdf3b2522a0b6a59a363ca151a2310aba04185b21f4f2017ce86a794",
            "pod_summary": "95fa3689cbe49c6c10c6f5395386196cf6a827a335dc85120b7efb4d69dd74bb"},
    "e8mf": {"report": "6236c6f03f7a57cc534419ca96f24bced1b25e704b86619496ebe7ee3af247d8",
             "home_summary_text": "bcc8012f640b4fd746137a3f0b0a948850a50f2e45c313522895155d8e0fb803",
             "pod_summary": "8c4bb39e364db5f48dee0f6dcdc00c537b42dca47122ac2c0243b708ec090620"},
}
RECHECK_E8M_K1 = "94fb0b3d21d9f29561992a64086b4f658e746b519218c135f699a22bf9cad155"   # home re-scored record, arm (b), k = 1
LL_SUMMARY = "d91315247d79deaf9133c063dbdcd2a52f3013d364fa43bac5f04b27809fc5eb"       # lag-ladder 0036's home summary
EVIDENCE = {"pull/e8-results-final.tgz": "f646312b5572ef6bc0b12230a3da349263a7029eaed8657a6362636879ad4c65",
            "pull/e8-aux-final.tgz": "07dbfc4297cc755e9f7249839a4adc6345d1cce5db9e695f5bd9da44e299fc44",
            "aux-final/aux/logs/chain.log": "22f0e93a6ab01c4dd56e8e8ed453f811e2d16a7ecf81c13864a55a366fcc3129",
            "aux-final/aux/logs/setup.log": "d5749790236974df61d46df27d273d99d4981ef001bac2c9b38ebc1ada320808",
            "upload.log": "3bd7ec6ebce3f62e34996224ac420edbcd5bc11e7b17962964dac78530f00f46",
            "home-summary-run.log": "fd8aa22f643c53e1df9e494eb82ef536b29abd4d32ff3b68fe769da67a1a65b1"}

# --- the ledger: ordering, and 0064's own pins and read-beside rows -----------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
for e in ("0009", "0016", "0020", "0030", "0039", "0040", REG):
    assert heads.count(e) == 1, f"entry {e} must be on the ledger exactly once"
ordering_ok = NUM not in heads and bool(heads) and heads[-1] == PREV


def block(t: str, entry: str) -> str:
    s = t.index(f"\n### {entry} ") + 1                      # the heading line itself
    nxt = re.search(r"^### \d{4} ", t[s + 4:], re.M)         # the NEXT heading, past this one's "### "
    return t[s: s + 4 + nxt.start()] if nxt else t[s:]


b64 = block(text, REG)
pin64 = {c: {"config": re.search(rf"`config/{c}\.toml`\s+`([0-9a-f]{{12}})…`", b64).group(1),
             "tokens": re.search(rf"`data/{c}/agent_n50_len1024_seed8\.npy`\s+`([0-9a-f]{{12}})…`", b64).group(1)}
         for c in CELLS}
pin64["e8m"]["manifest"] = re.search(r"Qwen pair:.*?manifest\s+`([0-9a-f]{12})…`", b64, re.S).group(1)
pin64["e8mf"]["manifest"] = re.search(r"Llama pair:.*?manifest\s+`([0-9a-f]{12})…`", b64, re.S).group(1)
m = re.search(r"Read beside: Qwen k = 1 on tau2/SWE-bench\s+\(0020\) `([^`]+)`; Llama k = 1 \(0040\) `([^`]+)`", b64)
assert m, "0064's read-beside rows not found"
beside = {"e8m": ("0020", m.group(1)), "e8mf": ("0040", m.group(2))}


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=R, capture_output=True, text=True, check=True).stdout.strip()


# the code this script imports defines figures (_seq_r2, _TOL, quantile, the band): unmodified, and as at the pod's commit
SRC_USED = ["src/"]     # the whole package: the imports load more modules than they name
assert (R / "src" / "linear_ceiling" / "summarize_e8.py").is_file(), "not a linear-ceiling checkout"
assert git("status", "--porcelain", "--", *SRC_USED) == "", "a module under src/ is modified or untracked in the working tree"
POD_COMMIT = "c95570d731cd827d25a78a76b5bfd9ada3146048"   # LINEAR_CEILING_HEAD on the pod and LC_HEAD of the home run
assert subprocess.run(["git", "diff", "--quiet", POD_COMMIT, "HEAD", "--", *SRC_USED], cwd=R).returncode == 0, \
    "an imported module changed since the commit the pod and the home run used"


def lines_of(p: Path) -> list:
    return p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").split("\n")


def one(lines: list, pattern: str) -> re.Match:
    hits = [mm for mm in (re.fullmatch(pattern, ln.strip()) for ln in lines) if mm]
    assert len(hits) == 1, f"expected exactly one line matching {pattern!r}, found {len(hits)}"
    return hits[0]


# --- evidence: the sitting's records, by digest and by line ------------------------------------------------------------
for rel, want in EVIDENCE.items():
    assert sha256_file_bytes(E / rel) == want, f"{rel} is not the pinned file"
chain, setup = lines_of(E / "aux-final/aux/logs/chain.log"), lines_of(E / "aux-final/aux/logs/setup.log")
heads_line = one(setup, r"LINEAR_CEILING_HEAD ([0-9a-f]{40})\s+KVT_HEAD ([0-9a-f]{40})")
pod_versions = one(setup, r"VERSIONS (\S+) (True|False) (\S+) (\S+) (\S+) (\S+)")
gpu = one(setup, r"(NVIDIA [^,]+), (\d+) MiB, \S+")
one(setup, r"R1_OK")
one(chain, r"GATES_OK")
one(chain, r"CHAIN_DONE")
# the two earlier launches of the sitting: setup attempt 1 failed (tar ownership), chain attempt 1 stopped at the downloads
assert (E / "aux-final/aux/logs/setup-attempt1.rc").read_text().strip() not in ("", "0")
assert any("Cannot change ownership" in ln for ln in lines_of(E / "aux-final/aux/logs/setup-attempt1.log"))
chain1 = lines_of(E / "aux-final/aux/logs/chain-attempt1.log")
one(chain1, r"CHAIN_STOP: snapshots did not finish")
assert not any(ln.startswith(("E8_LAUNCH", "run e8m")) for ln in chain1), "chain attempt 1 reached a dump"
assert any("403" in ln and "gated" in ln for ln in lines_of(E / "aux-final/aux/logs/downloads-attempt1.log"))
assert (E / "aux-final/aux/logs/chain.rc").read_text().strip() == "0"
run_t = {}
for c in CELLS:
    run_t[c] = one(chain, rf"run {c} rc 0 (\d\d:\d\d:\d\d)").group(1)
    assert (E / f"aux-final/aux/logs/run_{c}.rc").read_text().strip() == "0"
    one(lines_of(E / f"aux-final/aux/logs/summary_{c}.log"), r"SUMMARY_RC 0")
assert (E / "pull-final.rc").read_text().strip() == "0"
pull = lines_of(E / "pull-final.log")
one(pull, r"\S+Z HASHES MATCH")
one(pull, r"\S+Z PULL_OK final")
up = lines_of(E / "upload.log")
up_manifest = one(up, r"manifest: (\d+) wanted, 0 missing, 0 lfs-sha mismatches")
one(up, r"MANIFEST_OK")
home_run = lines_of(E / "home-summary-run.log")
hk = one(home_run, r"KVT_HEAD ([0-9a-f]{40})\s+LC_HEAD ([0-9a-f]{40})")
uv = one(home_run, r"UPSTREAM_VENV (\S+) (\S+) (\S+) (\S+) (\S+) \S.*")
lv = one(home_run, r"LC_VENV (\S+) (\S+) (\S+) (\S+) \S.*")
for c in CELLS:
    one(home_run, rf"HOME_SUMMARY_RC {c} 0")
one(home_run, r"LINK_SOURCES checked \d+, changed 0")
one(home_run, r"SCRIPT_RC 0 \S+")

# --- configs, reports, token files --------------------------------------------------------------------------------------
cfg, rep, draw = {}, {}, {}
for c in CELLS:
    cpath = R / "config" / f"{c}.toml"
    assert git("status", "--porcelain", "--", f"config/{c}.toml") == "", f"config/{c}.toml is modified"
    cfg[c] = load_e8_config(cpath, R)
    assert cfg[c].amendment and cfg[c].amendment["entry"] == REG, f"[e8.amendment] entry must be {REG}"
    csha = sha256_text_file(cpath)
    assert csha.startswith(pin64[c]["config"]), f"config/{c}.toml is not 0064's pin"
    rp = S / "results" / c / "report.json"
    assert sha256_file_bytes(rp) == PIN[c]["report"], f"{c} report.json is not the pinned file"
    rep[c] = json.loads(rp.read_text(encoding="utf-8"))
    assert rep[c]["config_sha256"] == csha, f"{c}: the run recorded another config"
    assert rep[c]["upstream_sha"] == cfg[c].upstream_sha == heads_line.group(2) == hk.group(1)
    assert heads_line.group(1) == hk.group(2), "the pod and the home pair ran different commits of this repository"
    assert rep[c]["amendment"]["entry"] == REG and not rep[c].get("reused_agent_dumps_from")
    assert rep[c]["verdict_k"] == cfg[c].verdict_k
    tok_s, tok_h = S / rep[c]["tokens"]["path"], R / rep[c]["tokens"]["path"]
    t_s, t_h = sha256_file_bytes(tok_s), sha256_file_bytes(tok_h)
    assert t_s == t_h == rep[c]["tokens"]["sha256"] and t_s.startswith(pin64[c]["tokens"]), f"{c}: token file differs"
    one(chain, rf"TOKENS_OK {c} {t_s}")
    man_s, man_h = tok_s.with_suffix(".manifest.json"), tok_h.with_suffix(".manifest.json")
    ms, mh_raw = sha256_file_bytes(man_s), man_h.read_bytes()
    assert ms == rep[c]["tokens"]["manifest_sha256"]
    mh = hashlib.sha256(mh_raw).hexdigest()
    mh_lf = hashlib.sha256(mh_raw.replace(b"\r\n", b"\n")).hexdigest()
    assert mh.startswith(pin64[c]["manifest"]), f"{c}: the home manifest is not 0064's pin"
    assert mh_lf == ms, f"{c}: the manifests differ beyond line endings"
    rows = np.load(tok_s)
    suites = [r["suite"] for r in json.loads(man_s.read_text(encoding="utf-8"))["rows"]]
    assert len(suites) == rows.shape[0]
    draw[c] = {"sha": t_s, "man_pod": ms, "man_home": mh, "n_cr": mh_raw.count(b"\r"), "shape": rows.shape,
               "distinct": int(len(np.unique(rows, axis=0))), "suites": suites,
               "blocked": suites == sorted(suites) and len(set(suites)) == 2}

# --- the home summaries (cited) and the pod's (for the difference) -----------------------------------------------------
home, pod = {}, {}
for c in CELLS:
    hp, pp = S / "results" / c / "summary.json", E / "results-final" / "results" / c / "summary.json"
    assert sha256_text_file(hp) == PIN[c]["home_summary_text"], f"{c}: the home summary is not the pinned one"
    assert sha256_file_bytes(pp) == PIN[c]["pod_summary"], f"{c}: the pod summary is not the pinned one"
    home[c], pod[c] = (json.loads(p.read_text(encoding="utf-8")) for p in (hp, pp))
    assert home[c]["amendment"]["entry"] == REG and home[c]["reused_agent_dumps_from"] is None
    assert set(home[c]["per_k"]) == {str(k) for k in cfg[c].report_k} == set(home[c]["recomputed"])
TH = {c: (float(cfg[c].band["holds_max_drop"]), float(cfg[c].band["degrades_min_drop"])) for c in CELLS}
assert TH["e8m"] == TH["e8mf"]


def leaves(x, path=""):
    if isinstance(x, dict):
        for k in sorted(x):
            yield from leaves(x[k], f"{path}.{k}" if path else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


isf = lambda v: isinstance(v, float)  # noqa: E731
diff = {}
for c in CELLS:
    P, H = dict(leaves(pod[c])), dict(leaves(home[c]))
    assert set(P) == set(H), f"{c}: the two summaries have different keys"
    fl = [k for k in H if isf(H[k]) and isf(P[k])]
    nonf = [k for k in H if k not in fl]
    dif = [k for k in fl if P[k] != H[k]]
    nonf_equal = all(P[k] == H[k] and type(P[k]) is type(H[k]) for k in nonf)
    absd = {k: abs(P[k] - H[k]) for k in dif}
    assert all(H[k] != 0.0 for k in dif), f"{c}: a differing field is 0 at home; max rel would skip it"
    reld = {k: absd[k] / abs(H[k]) for k in dif}
    mx = max(absd.values())
    pts = [k for k in fl if ".drop." in f".{k}." and "bootstrap" not in k]
    near_pt = min((min(abs(H[k] - t) for t in TH[c]), k) for k in pts)
    bnds = [k for k in fl if "bootstrap" in k and ".drop_" in k]
    side = all((P[k] > t) == (H[k] > t) for k in bnds + pts for t in TH[c])
    near_b = min((min(abs(H[k] - t) for t in TH[c]), k) for k in bnds)
    diff[c] = {"n": len(H), "n_float": len(fl), "n_dif": len(dif), "n_nonf": len(nonf), "nonf_equal": nonf_equal,
               "n_band": sum("band_outcome" in k for k in nonf), "max_abs": mx, "max_rel": max(reld.values()),
               "near_pt": near_pt, "near_b": near_b, "same_side": side}
    assert nonf_equal, f"{c}: a non-float field differs between the pod and home summaries"
    assert side, f"{c}: a drop or bound crosses a band line between the pod and home summaries (the entry's sentence fails)"

# --- the per-window join (form: 2026-11-10-e8m-ll0036-join-spec.md) ----------------------------------------------------
rk = S / "results" / "e8m" / "recheck" / "agent_k1.npz"
assert sha256_file_bytes(rk) == RECHECK_E8M_K1, "the home re-scored arm (b) record is not the pinned file"
z = np.load(rk)
ids = [int(i) for i in z["seq_ids"]]
assert ids == list(range(50))
lc = {key: _seq_r2(z, key) for key in ("K", "V")}
rec = rep["e8m"]["per_k"]["1"]["per_sequence"]["agent"]
assert list(rec["seq_ids"]) == ids
for key in ("K", "V"):
    assert np.allclose(lc[key], rec[key], rtol=0, atol=_TOL), f"per-sequence {key} differs from the run's record"
    assert quantile([float(x) for x in lc[key]], 0.5) == home["e8m"]["per_k"]["1"]["per_sequence"][f"agent_{key}"]["median"]
assert sha256_file_bytes(a.ll_summary) == LL_SUMMARY, "the lag-ladder summary is not 0036's home summary"
ll = json.loads(a.ll_summary.read_text(encoding="utf-8"))
kl = {}
for r in ll["rungs"]:
    lag = int(re.fullmatch(r".*-lag-(\d+)", r["label"]).group(1))
    assert r["controls_passed"] is True and r["withheld"] is False, f"lag {lag}: rung not evaluable"
    t = r["texts"]["agentic"]
    assert [int(s) for s in t["seqs"]] == ids, f"lag {lag}: sequence ids differ"
    v = np.asarray(t["b1"]["per_seq_mean_kl"], dtype=np.float64)
    assert len(v) == 50 and float(np.median(v)) == t["b1"]["median_kl"]
    kl[lag] = v
assert sorted(kl) == [1, 2, 4, 8, 16, 32]
assert draw["e8m"]["blocked"] and draw["e8m"]["suites"][:25] == [draw["e8m"]["suites"][0]] * 25
SPLIT = {"all": slice(0, 50), "coding": slice(0, 25), "workflow": slice(25, 50)}
assert set(draw["e8m"]["suites"][0:25]) == {"mlperf-coding"} and set(draw["e8m"]["suites"][25:50]) == {"mlperf-workflow"}


def ranks(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    r, sx, i = np.empty(len(x)), x[order], 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(u, v) -> float:
    return float(np.corrcoef(ranks(u), ranks(v))[0, 1])


rho = {lag: {key: {s: spearman(lc[key][sl], kl[lag][sl]) for s, sl in SPLIT.items()} for key in ("K", "V")}
       for lag in sorted(kl)}

# --- rendering ----------------------------------------------------------------------------------------------------------
def f4(x, sign=False):
    return f"{x:+.4f}" if sign else f"{x:.4f}"


def st(d):
    return f"{d['median']:.4f} ({d['p10']:.4f}, {d['p90']:.4f})"


main_md, h16_md, seq_md = [], [], []
for c in CELLS:
    pair = rep[c]["pair"]
    for k in [str(x) for x in cfg[c].report_k]:
        rc, pk = home[c]["recomputed"][k], home[c]["per_k"][k]
        b, h, ch = pk["bootstrap"], pk["heldout_0016_protocol"], pk["change_from_heldout"]
        assert pk["n_heldout_seqs"]["agent"] == 50 and b["K"]["seed"] == int(cfg[c].amendment["bootstrap_seed"]) + int(k)
        vk = " (verdict k)" if int(k) == cfg[c].verdict_k else ""
        main_md.append(
            f"| {pair} | {k}{vk} | {f4(rc['generic']['K'])} / {f4(rc['generic']['V'])} | **{f4(rc['agent']['K'])} / {f4(rc['agent']['V'])}** "
            f"| {f4(rc['drop']['K'], True)} / {f4(rc['drop']['V'], True)} "
            f"| [{f4(b['K']['drop_lower_2.5'], True)}, {f4(b['K']['drop_upper_97.5'], True)}] "
            f"| [{f4(b['V']['drop_lower_2.5'], True)}, {f4(b['V']['drop_upper_97.5'], True)}] "
            f"| {rc['band_outcome']['K']} / {rc['band_outcome']['V']} |")
        h16_md.append(
            f"| {pair} | {k}{vk} | {f4(h['agent']['K'])} / {f4(h['agent']['V'])} | {f4(h['drop']['K'], True)} / {f4(h['drop']['V'], True)} "
            f"| {h['band_outcome']['K']} / {h['band_outcome']['V']} | {f4(ch['K'], True)} / {f4(ch['V'], True)} |")
        ps = pk["per_sequence"]
        seq_md.append(f"| {pair} | {k} | {st(ps['agent_K'])} | {st(ps['agent_V'])} | {st(ps['generic_K'])} | {st(ps['generic_V'])} |")
h_ids = {c: home[c]["per_k"]["1"]["heldout_0016_protocol"]["seq_ids"] for c in CELLS}
for c in CELLS:
    assert h_ids[c] == list(range(40, 50))
h_suites = {c: sorted({draw[c]["suites"][i] for i in h_ids[c]}) for c in CELLS}
assert h_suites["e8m"] == h_suites["e8mf"] == ["mlperf-workflow"]
near_line = []
for c in CELLS:
    for k in [str(x) for x in cfg[c].report_k]:
        for key in ("K", "V"):
            for side_name in ("drop_lower_2.5", "drop_upper_97.5"):
                val = home[c]["per_k"][k]["bootstrap"][key][side_name]
                for t in TH[c]:
                    if abs(val - t) < 1e-3:
                        near_line.append(f"{rep[c]['pair']} k = {k} {key} {side_name.replace('drop_', '').replace('_', ' ')}% bound "
                                         f"{val:.6f}, {abs(val - t):.1e} {'above' if val > t else 'below'} {t}")
assert near_line, "no bootstrap bound within 1e-3 of a band line (the entry's sentence would be empty)"
j_md = [f"| {lag} | {rho[lag]['K']['all']:+.3f} / {rho[lag]['K']['coding']:+.3f} / {rho[lag]['K']['workflow']:+.3f} "
        f"| {rho[lag]['V']['all']:+.3f} / {rho[lag]['V']['coding']:+.3f} / {rho[lag]['V']['workflow']:+.3f} |" for lag in sorted(kl)]
vk1 = {c: home[c]["recomputed"][str(cfg[c].verdict_k)] for c in CELLS}
h1 = {c: home[c]["per_k"][str(cfg[c].verdict_k)]["heldout_0016_protocol"] for c in CELLS}


def dline(c):
    d = diff[c]
    return (f"{rep[c]['pair']}: {d['n_dif']} of {d['n_float']} float fields differ, max abs {d['max_abs']:.2e}, max rel "
            f"{d['max_rel']:.1e}; all {d['n_nonf']} non-float fields equal, the {d['n_band']} band words among them; the point drop "
            f"nearest a band line is {d['near_pt'][0]:.2e} from it ({d['near_pt'][0] / d['max_abs']:,.0f}× the largest difference)")


cut = lambda s: s[:12]  # noqa: E731
pv = pod_versions
ENTRY = f"""### {NUM} — {a.date} — E8 ran on the MLPerf Agentic Inference text `[BASELINE, DESCRIPTIVE]`: both pairs, arm (b) over every agent sequence with the 0016-protocol figure beside it; the summary recomputed off the pod; no hypothesis row, no cell moves

**Provenance.** Registered by {REG} before any dump. `config/e8m.toml` (`{cut(rep['e8m']['config_sha256'])}`) and `config/e8mf.toml`
(`{cut(rep['e8mf']['config_sha256'])}`) committed unmodified and equal to the configs each run recorded; upstream at the pin
`{cfg['e8m'].upstream_sha[:7]}`; this repository at `{heads_line.group(1)[:7]}` on the pod. One sitting on one {gpu.group(1)}
({int(gpu.group(2)):,} MiB); the upstream environment torch {pv.group(1)} (CUDA available: {pv.group(2)}), transformers {pv.group(4)},
safetensors {pv.group(5)}, numpy {pv.group(6)}, as its setup log records them; setup's R1 check passed (neither results directory
existed). `e8 --config config/e8m.toml` then `--config config/e8mf.toml`, each rc 0 (`run e8m rc 0 {run_t['e8m']}`,
`run e8mf rc 0 {run_t['e8mf']}` UTC), each followed by the driver's token-file check (`TOKENS_OK` with the file's sha256) and the
pod's own `summarize_e8` (`SUMMARY_RC 0`). Two earlier launches in the same sitting stopped before any dump: setup on a tar
ownership refusal, the chain at a gated-model download. Records pulled with equal digests at both ends (results
`{cut(EVIDENCE['pull/e8-results-final.tgz'])}…`, aux `{cut(EVIDENCE['pull/e8-aux-final.tgz'])}…`); the dumps and records backed up to
the private dataset ({int(up_manifest.group(1))} files, `manifest: {int(up_manifest.group(1))} wanted, 0 missing, 0 lfs-sha mismatches`,
`MANIFEST_OK`; that check compares the LFS files by digest and the small files by name only). All off-repository.

**What ran.** {REG}'s registered protocol, unchanged: 0009's instrument, 0016's sampling rule on the two MLPerf suites, 0030's protocol.
The existing fitted mappers of each pair; arm (a) the archived generic dumps at the mapper's own held-out fraction 0.2; arm (b)
this cell's own dumps scored over EVERY agent sequence (50 sequences, {home['e8m']['per_k']['1']['n_heldout_tokens']['agent']:,}
tokens at stride {cfg['e8m'].stride}); per-sequence R² from the per-token records; a seeded percentile bootstrap of the drop (seed
{int(cfg['e8m'].amendment['bootstrap_seed'])} + k, {int(cfg['e8m'].amendment['bootstrap_reps']):,} reps); and the 0016-protocol figure
recomputed beside it from the same per-sequence moments, pooled R² over the last ten rows (ids {h_ids['e8m'][0]}–{h_ids['e8m'][-1]},
all `{h_suites['e8m'][0]}` on both pairs).

**The draw, recomputed from the token files.** The pod's files equal {REG}'s pins byte for byte: Qwen `{cut(draw['e8m']['sha'])}…`,
Llama `{cut(draw['e8mf']['sha'])}…`. Each is {draw['e8m']['shape'][0]} rows of {draw['e8m']['shape'][1]:,} tokens:
{draw['e8m']['distinct']} and {draw['e8mf']['distinct']} distinct windows, {draw['e8m']['suites'].count('mlperf-coding')} `mlperf-coding`
rows then {draw['e8m']['suites'].count('mlperf-workflow')} `mlperf-workflow` rows (Qwen), and
{draw['e8mf']['suites'].count('mlperf-coding')} then {draw['e8mf']['suites'].count('mlperf-workflow')} (Llama). The pod-written
manifests (`{cut(draw['e8m']['man_pod'])}…`, `{cut(draw['e8mf']['man_pod'])}…`) are not the bytes {REG} pinned
(`{cut(draw['e8m']['man_home'])}…`, `{cut(draw['e8mf']['man_home'])}…`). The pinned copies carry CRLF line endings
({draw['e8m']['n_cr']} and {draw['e8mf']['n_cr']} CRs); with those removed, each equals the pod's byte for byte.

| pair | k | arm (a) generic K / V | arm (b) agent, every sequence K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |
|---|---|---|---|---|---|---|---|
{chr(10).join(main_md)}

The 0016-protocol figure, beside it (pooled over the last ten rows; the change is every-sequence arm (b) minus this one):

| pair | k | arm (b) last ten K / V | drop K / V | band K / V | change K / V |
|---|---|---|---|---|---|
{chr(10).join(h16_md)}

Read beside, as {REG} quoted them, on tau2-bench / SWE-bench windows at the 0016 protocol and never pooled with the rows above:
Qwen ({beside['e8m'][0]}) `{beside['e8m'][1]}`; Llama ({beside['e8mf'][0]}) `{beside['e8mf'][1]}`.

**Per-sequence R²** (a share of the pooled decomposition, SST around the global held-out mean), median (p10, p90):

| pair | k | agent K | agent V | generic K | generic V |
|---|---|---|---|---|---|
{chr(10).join(seq_md)}

Bootstrap bounds within 1e-3 of a band line: {'; '.join(near_line)}. The band reads the point drop. No bound is read by anything.

**Pod and home.** Every figure in the three tables, and the bound in the bound line, is from `summarize_e8` run off the
pod, at the pin: the upstream at `{hk.group(1)[:7]}`
with torch {uv.group(2)}, transformers {uv.group(3)}, safetensors {uv.group(4)} and numpy {uv.group(5)} (the pod's versions, torch's
CPU build), and this repository at `{hk.group(2)[:7]}` with torch {lv.group(2)}, safetensors {lv.group(3)} and numpy {lv.group(4)}
(the pod's versions there). Its inputs were the pod's report, records and token files, without the pod's summary; the
agent dumps from the backup; and the archived generic dumps and mappers, by the run's fingerprints. Its `summary.json`,
sha256 (newline-normalized) Qwen `{cut(PIN['e8m']['home_summary_text'])}…`,
Llama `{cut(PIN['e8mf']['home_summary_text'])}…`, is what this entry reads, by digest, rather than running `summarize_e8`
at append, as 0064 planned. The pod's summaries (sha256 `{cut(PIN['e8m']['pod_summary'])}…`, `{cut(PIN['e8mf']['pod_summary'])}…`) differ from those in floats only:
- {dline('e8m')};
- {dline('e8mf')}.

Every point drop and every bootstrap bound lies on the same side of both band lines in the two summaries. The cause is
inferred and was not tested: the pod's
upstream scorer ran torch's CUDA build, and the home one ran the CPU build.

**Per window, beside lag-ladder's 0036 (a figure, no verdict).** The Qwen file is the token file lag-ladder's 0030 / 0036 read
under seed 1's readers ({REG}). Joined on row id: this cell's arm (b) per-sequence R² at k = {cfg['e8m'].verdict_k}, from the
home run's re-scored record `results/e8m/recheck/agent_k1.npz` (`{cut(RECHECK_E8M_K1)}…`; equal to the run's recorded list within
the summarizer's tolerance; 0065 named both summary files, and this cell's summary carries no per-window value), and
lag-ladder's per-sequence mean per-token KL (B1) at each lag, from its home `summary.json`
(`{cut(LL_SUMMARY)}…`, the one 0036 cites). The figure is Spearman's rank correlation over all 50 windows, and within each
suite over 25:

| lag | ρ, R² K vs B1: all / coding / workflow | ρ, R² V vs B1: all / coding / workflow |
|---|---|---|
{chr(10).join(j_md)}

The two instruments read different positions of the same window. The mapper scores every 4th of
all 1,024 positions, and the readers score the last 256 after a 768-token prefix. They are different models: the Qwen3
0.6B → 1.7B mapper, and the Qwen2.5-1.5B readers at GRPO lags 1–32. Both readings carry the same suite split, so the pooled
column may reflect the suite difference alone; the within-suite columns are there for that reason. These are 36
correlations on 50 windows, in a form this entry fixes (0065 registered the join, not its statistic), stated without an
interval or a test. Lag-ladder's 0030 named the per-sequence R² drop beside the per-window median KL. Measured from arm
(a)'s pooled R², one constant across windows, the drop orders the windows in reverse, so each of its ρ is the one above
with the sign flipped; and the one per-window KL value lag-ladder's summary carries is B1, a mean, whose median is taken
over windows. A negative ρ means the windows the mapper fits worse are the windows where the stale reader draws more KL.
That sign is for orientation only.

**What this establishes, stated narrowly.** On the two pairs, how much held-out pooled R² the existing k = 1, 4, 8 mappers lose
from generic calibration text to the opening 1,024 tokens of MLPerf Agentic Inference trajectories (DeepSWE coding and Workato
workflow, reasoning kept, the shared system prefix not rendered), over every agent sequence and at the 0016 protocol. **Not
established.** Anything about H-E8, which is 0020's and unchanged. Anything on-policy, or at a real switch point. The
accumulated history past the opening window: the first 1,024 tokens of a coding trace are mostly its task statement ({REG}).
Anything pooled across the two pairs or with the tau2-bench / SWE-bench figures. Anything causal from the per-window join.

**Scope.** All of 0009's, 0016's, 0030's, 0039's and {REG}'s limits. No hypothesis cell changes with this entry. Nothing under
`results/` or `data/` is committed; this script is retired after the append.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print(f"[ordering guard: {'ok' if ordering_ok else f'NOT satisfied — the last entry is {heads[-1]}, want {PREV}; {NUM} must be absent'}]")
    raise SystemExit(0)
assert ordering_ok, f"ordering: the ledger's last entry must be {PREV} and {NUM} absent"
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head_m = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head_m.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
