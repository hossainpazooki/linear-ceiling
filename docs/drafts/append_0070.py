"""DRAFT append script for linear-ceiling: entry 0070 (PROVISIONAL number; the drafts README allocates it at staging) --
the task-quality cell (registered by 0063), long and short cells: the figures, written ONLY from
`tools.task_quality.cell.summarize` run in-process over the verified home mirror. DESCRIPTIVE: no `verdict:` line, no
hypothesis row, no band, no cell moves.

0063: the figures entry "calls `tools.task_quality.cell.summarize` in-process over the operator's verified output,
asserts the report's hashes equal the hashes above, and refuses on any disagreement; no figure is typed." The pins this
entry asserts are read from 0063's own text. Run facts the reader cannot know are recounted from the sitting's records,
each pinned by sha256: the launch and finish times, the one chain launch per cell, the allocator warnings per handoff,
the long cell's home verify before the short cell's launch, and the stopped first sitting's report. `summarize` writes
LF on every platform, so one pin per summary is the pod's file byte for byte. The entry's other sitting sentences (the
community card, no partial close, the new pod of the second sitting, the dates of the two rulings it cites) rest on the
sitting's records outside the repository and are NOT asserted here.

  --evidence <dir>         the sitting folder: short-cell/pull-final/ (both chains' logs and both cells' trees, pulled
                           after the short cell), pull-final/VERIFY_RESULT and home-verify-final.out (the long cell's close)
  --stopped-report <file>  the stopped first sitting's long-cell report.json
  --backup-log <file>      the log of the backup's last push and verify (tools/hf_backup.sh), ending "BACKUP VERIFIED"
  --dataset <repo_id>      optional; names the backup in the entry and must be the log's repository. Omitted, the entry
                           says "a private Hub dataset".
  --run-date YYYY-MM-DD    the UTC date of the chain logs' times (checked against the allocator lines and the verify stamp)
  --date YYYY-MM-DD        the heading's date: the day the entry is written and appended (entry 0021), not the run day;
                           required, a real date, not before the backup's verify and not after today (UTC)
  --preview  [--repo-root <path>]
The preview's last line must read `[ordering guard: ok]`. Ordering guard: 0063 present; the ledger's last entry is PREV
and states the 2026-11-11 ruling's sentence, which this entry carries; NUM absent. Runs `ledger_check` after appending.
Run from the repo root with `.venv/Scripts/python.exe` (the reader imports torch). Delete once appended, chained with `&&`.
"""
import argparse
import datetime as dt
import hashlib
import importlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--evidence", type=Path, required=True)
ap.add_argument("--stopped-report", type=Path, required=True)
ap.add_argument("--backup-log", type=Path, required=True)
ap.add_argument("--dataset", default=None)
ap.add_argument("--run-date", required=True)
ap.add_argument("--date", required=True)
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=None)
a = ap.parse_args()
for d in (a.date, a.run_date):
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", d), "dates must be YYYY-MM-DD (the ledger heading's form)"
    dt.date.fromisoformat(d)                     # a real calendar date, or ValueError
assert a.run_date <= a.date <= dt.datetime.now(dt.timezone.utc).date().isoformat(), \
    "--date is the day of writing: not before --run-date and not after today (UTC)"
_here = Path(__file__).resolve().parents[2]
R = (a.repo_root or (_here if (_here / "ledger" / "ledger.md").exists() else Path.home() / "dev" / "linear-ceiling")).resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file    # noqa: E402  (text = LF-normalized, for tracked files on a CRLF checkout)
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402

NUM, PREV, REG = "0070", "0069", "0063"
CELLS = ("long", "short")
CHAIN = {"long": 1, "short": 2}      # the pod's chain launches in order: the long cell, then the short cell on the same pod
OUT = R / "results" / "task-quality-cell"
E = a.evidence.resolve()
PULL = E / "short-cell" / "pull-final"
LOGS = PULL / "aux" / "logs"
PIN = {   # full sha256 of raw bytes
    "long/report.json": "f8054e6e259c1e7b6f09349ac60d40eaa728322bb87c68090b24047426d2b11a",
    "long/summary.json": "3eb17759faeff175eaaa736f78f1e6ee19aefde3f28adc8993df1f9975318a5d",
    "short/report.json": "01d955983cae2ff13cddf1701232429349fae24e787e83e64744c9ee22eccc73",
    "short/summary.json": "0173777cc014d0f4ee73221eda70f5a934fb6d769613208d391ea776c17869e2",
    "stopped_report": "b4a5aeeb955f2138aa55789181557a5597f36c738bb6e1d1e768da2d547fa366",
    "backup_log": "c61e6f3691a1e30e8738077fe46ec9145b6eba80988c6f408284a30edbd369c2",
}
EVIDENCE = {
    "short-cell/pull-final/aux/logs/chain-tq.1.log": "723820f03abb1dd99c7c24b494331a1579d1f0effa9a9f50839463adb1687196",
    "short-cell/pull-final/aux/logs/chain-tq.2.log": "7803889cfd31fbf3417280695c22935defbc7fcacffb5041a7f103e0a5d9f130",
    "short-cell/pull-final/aux/logs/tq-long-probe.1.log": "94950cdbddf552f087f4054001b84d57bc3553df7a8da9db0e7b682769c630a9",
    "short-cell/pull-final/aux/logs/tq-long-run.1.log": "f57dcb179468a3d10e707d4bf4df5892020d3e896a3c0293dd7551fbcb8b3514",
    "short-cell/pull-final/aux/logs/tq-short-probe.2.log": "113aa1a4a8da56a99c0bc64772d6106f0684c9da088e597b0a24f0d05d90b4a6",
    "short-cell/pull-final/aux/logs/tq-short-run.2.log": "64e8b75a67de0f0865a2f83d2b7a80fb445af24af6f49fc9805ed82dbb7d2eb5",
    "short-cell/pull-final/PULL_RESULT": "fbf30d4438f5172c3a2ae7026a2e04ec0c5d2aaa30106c112c280dfbe07deb6a",
    "short-cell/pull-final/VERIFY_RESULT": "104b0d10e2c02e4223f72d81ffc5c13d3a4e4f8fc16b42826c053fc7f3f08678",
    "pull-final/VERIFY_RESULT": "4ce80e8a1c07c5a1841da2594c4c94f7baa8b010510b2f13cef635f0edc531e5",
    "home-verify-final.out": "3f70e493672714d9afa1d01653820a1e412e1f90442798a779dbf6b330da4650",
}
LOG_FILES = sorted(["chain-tq.1.log", "chain-tq.1.rc", "chain-tq.2.log", "chain-tq.2.rc", "preflight-tq.log", "setup-tq.log",
                    "setup-tq.rc", "probe-tq-long.1.rc", "run-tq-long.1.rc", "probe-tq-short.2.rc", "run-tq-short.2.rc",
                    "tq-long-probe.1.log", "tq-long-probe.1.progress.log", "tq-long-run.1.log", "tq-long-run.1.progress.log",
                    "tq-short-probe.2.log", "tq-short-probe.2.progress.log", "tq-short-run.2.log", "tq-short-run.2.progress.log"])
RCS = ("setup-tq.rc", "chain-tq.1.rc", "probe-tq-long.1.rc", "run-tq-long.1.rc", "chain-tq.2.rc", "probe-tq-short.2.rc",
       "run-tq-short.2.rc")
RUNBOOK = "docs/runbooks/2026-10-21-task-quality-cell-runpod-runbook.md"
ARMS = ["fresh", "reuse", "random", "repair_5pct", "repair_10pct", "repair_20pct"]
LABEL = {"fresh": "FRESH", "reuse": "REUSE-ALL", "random": "RANDOM", "repair_5pct": "REPAIR-0.05", "repair_10pct": "REPAIR-0.10",
         "repair_20pct": "REPAIR-0.20"}
SCORERS = ["first_span_exact", "exact_match", "contains", "token_f1", "canonical_contains"]
# The 2026-11-11 ruling, verbatim as PREV (0061's figures) quotes it; this entry quotes it again and carries its reading.
RULING_61 = ("An OOM in that rule is an out-of-memory error that ends the driver or fails a handoff. A warning from the "
             "caching allocator that it freed its cache and retried, after which the handoff scored with every control "
             "passing, is not one.")

# --- the ledger: ordering, and the pins 0063 states --------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert heads.count(REG) == 1, f"entry {REG} must be on the ledger exactly once"


def block(t: str, entry: str) -> str:
    s = t.index(f"\n### {entry} ") + 1
    nxt = re.search(r"^### \d{4} ", t[s + 4:], re.M)
    return t[s: s + 4 + nxt.start()] if nxt else t[s:]


flat = lambda s: re.sub(r"\s+", " ", s)  # noqa: E731
b63 = flat(block(text, REG))
b47 = flat(block(text, "0047"))
# "This cell registers none of 0047's numerical controls (fresh repeat, prefix copy) and no archive bridge."
for phrase in ("**Numerical controls, fixed now;", "Fresh repeat: a second FRESH pass", "Prefix copy over 128 tokens",
               "Archive bridge: the current runtime's"):
    assert phrase in b47, f"0047 no longer reads {phrase!r}"
assert not any(w in b63.lower() for w in ("fresh repeat", "prefix copy", "bridge")), "0063 registers a 0047 control or a bridge"
ordering_ok = (NUM not in heads and bool(heads) and heads[-1] == PREV and heads.count(PREV) == 1
               and RULING_61 in flat(block(text, PREV)))
pin63 = {"config": re.search(r"`config/task-quality-cell\.toml` \(`([0-9a-f]{12})…`\)", b63).group(1),
         "items.py": re.search(r"`tools/task_quality/items\.py` `([0-9a-f]{12})…`", b63).group(1),
         "pilot.py": re.search(r"`pilot\.py` `([0-9a-f]{12})…` \(the items driver", b63).group(1),
         "cell.py": re.search(r"`cell\.py` `([0-9a-f]{12})…` \(the cell driver", b63).group(1),
         "core.py": re.search(r"over `tools/cache_behavior/core\.py` `([0-9a-f]{12})…`", b63).group(1),
         "long": re.search(r"`results/task-quality/items-e9l\.json` `([0-9a-f]{12})…`", b63).group(1),
         "short": re.search(r"`items-e9\.json` `([0-9a-f]{12})…`", b63).group(1),
         "revision": re.search(r"receiver `Qwen/Qwen3-1\.7B@([0-9a-f]{12})`", b63).group(1)}
pv = re.search(r"The floor voids (\d+) of (\d+) long handoffs \(\d+ hold no item at all\) and (\d+) of (\d+) short ones", b63)
pr = re.search(r"the cell runs (\d+) long and (\d+) short handoffs", b63)
VOID = {"long": int(pv.group(1)), "short": int(pv.group(3))}
N = {"long": int(pr.group(1)), "short": int(pr.group(2))}
assert int(pv.group(2)) - VOID["long"] == N["long"] and int(pv.group(4)) - VOID["short"] == N["short"]
for phrase in ("is ASSUMED until the probe times it", "the largest sender first as the memory probe (R2)",
               "mirrored home and verified before the figures entry"):
    assert phrase in b63, f"{REG} no longer reads {phrase!r}"


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=R, capture_output=True, text=True, check=True).stdout.strip()


# --- the reader this script imports, and each cell's identity ------------------------------------------------------------
USED = ["src/", "tools/task_quality/", "tools/cache_behavior/core.py", "config/task-quality-cell.toml"]
assert git("status", "--porcelain", "--", *USED) == "", "a file this entry reads is modified or untracked in the working tree"
reports = {c: json.loads((OUT / c / "report.json").read_text(encoding="utf-8")) for c in CELLS}
RUN_COMMIT = reports["long"]["git_commit"]
assert re.fullmatch(r"[0-9a-f]{40}", RUN_COMMIT) and reports["short"]["git_commit"] == RUN_COMMIT
assert subprocess.run(["git", "diff", "--quiet", RUN_COMMIT, "HEAD", "--", *USED], cwd=R).returncode == 0, \
    "the reader, the package or the config changed since the commit the run used"
cfg_path = R / "config/task-quality-cell.toml"
cfg_sha = sha256_text_file(cfg_path)
code = {n: sha256_text_file(R / "tools/task_quality" / n) for n in ("cell.py", "pilot.py", "items.py")}
core_sha = sha256_text_file(R / "tools/cache_behavior/core.py")
# "the driver's hash checks on the items file, the alignment files and the archive raised nothing": the raising checks in
# the pinned cell.py (the archive check covers the score and per-token files against the archive report's pins), and
# "the summarizer, which recomputes every stored score from the stored prediction": its raising check.
cell_src = (R / "tools/task_quality/cell.py").read_text(encoding="utf-8")
for check in ('raise ValueError("items file differs from the registered sha")',
              '''raise ValueError(f"alignment file differs from the items file's pin: {hid}")''',
              'raise ValueError(f"archive hash mismatch: {hid}")',
              'raise ValueError(f"stored score differs from the recomputed one: {hid} {arm} {form} {scorer}")'):
    assert cell_src.count(check) == 1, f"cell.py no longer holds {check!r}"
assert cfg_sha.startswith(pin63["config"]) and core_sha.startswith(pin63["core.py"]) \
    and all(code[n].startswith(pin63[n]) for n in code), f"the committed config or code is not {REG}'s pin"
cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
assert cfg["revision"].startswith(pin63["revision"])
CAP = int(cfg["max_new_tokens"])
for c in CELLS:
    r, i = reports[c], reports[c]["identity"]
    assert sha256_file_bytes(OUT / c / "report.json") == PIN[f"{c}/report.json"], f"{c}/report.json is not the pinned file"
    assert i["config_sha256"] == cfg_sha and i["code_sha256"] == code and i["cell"] == c, f"{c}: the run recorded another config or code"
    items_path = R / cfg["cells"][c]["items_file"]
    assert i["items_sha256"] == cfg["cells"][c]["items_sha256"] and i["items_sha256"].startswith(pin63[c]) \
        and i["items_sha256"] in (sha256_text_file(items_path), sha256_file_bytes(items_path)), f"{c}: the items file is not {REG}'s"
    assert i["model"] == cfg["model"] and i["model_revision"] == cfg["revision"] and i["dtype"] == "float32" \
        and i["device"] == "cuda" and i["cublas_workspace_config"] == ":4096:8"
    assert r["complete"] and set(r["handoffs"]) == set(r["run_order"]) and len(r["run_order"]) == N[c] \
        and len(r["void"]) == VOID[c] and r["floor"] == cfg["min_form2_items"], f"{c}: the scored set is not the registered one"
    sizes = [r["handoffs"][h]["n_sender"] for h in r["run_order"]]
    assert sizes == sorted(sizes, reverse=True), f"{c}: the run order is not descending sender length (the probe the largest)"
ident = reports["long"]["identity"]
assert all(reports["short"]["identity"][k] == v for k, v in ident.items() if k not in ("cell", "items_sha256"))
sys.path.insert(0, str(R))                       # cell.py does `from .pilot import …`: import it as the package module
mod = importlib.import_module("tools.task_quality.cell")
assert Path(mod.__file__).resolve() == (R / "tools/task_quality/cell.py").resolve(), f"imported {mod.__file__}"


def lines_of(p: Path) -> list:
    return re.split(r"\r\n|\r|\n", p.read_text(encoding="utf-8", errors="replace"))


def one(lines: list, pattern: str) -> re.Match:
    hits = [mm for mm in (re.fullmatch(pattern, ln.strip()) for ln in lines) if mm]
    assert len(hits) == 1, f"expected exactly one line matching {pattern!r}, found {len(hits)}"
    return hits[0]


# --- the sitting's records, by digest and by line ------------------------------------------------------------------------
for rel, want in EVIDENCE.items():
    assert sha256_file_bytes(E / rel) == want, f"{rel} is not the pinned file"
assert sorted(p.name for p in LOGS.iterdir()) == LOG_FILES, "the last pull holds another chain's logs, or lacks one"
for rc in RCS:
    assert (LOGS / rc).read_text().strip() == "0", f"{rc} is not 0"
assert (PULL / "PULL_RESULT").read_text().strip() == "PULL_OK final"
want_vr = [f"VERIFY_OK {c} home summarize rc 0, EXACT_EQUAL; COMPLETE {c} True handoffs {N[c]} of {N[c]} summary_handoffs {N[c]}"
           for c in CELLS]
assert [ln for ln in lines_of(PULL / "VERIFY_RESULT") if ln.strip()] == want_vr
assert [ln for ln in lines_of(E / "pull-final/VERIFY_RESULT") if ln.strip()] == want_vr[:1]
hv = lines_of(E / "home-verify-final.out")                # the long cell's close, before the short cell was launched
assert one(hv, r"VERIFY_HEAD ([0-9a-f]{7,40})").group(1) == RUN_COMMIT[:7]
one(hv, r"EXACT_EQUAL")
vd = one(hv, r"VERIFY_DONE (\d{4}-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z \(result in .+/pull-final/VERIFY_RESULT\)")
assert vd.group(1) == a.run_date, "the long cell's verify stamp is not on --run-date"
for c in CELLS:
    tree = PULL / "tree" / "results" / "task-quality-cell" / c
    assert sha256_file_bytes(tree / "report.json") == PIN[f"{c}/report.json"], f"{c}: the mirror's report is not the pod's"
    assert sha256_file_bytes(tree / "summary.json") == PIN[f"{c}/summary.json"], f"{c}: the pinned summary is not the pod's"

clock = lambda s: dt.datetime.strptime(f"{a.run_date}T{s}", "%Y-%m-%dT%H:%M:%S")  # noqa: E731
T = {}
for c, k in CHAIN.items():
    chain = lines_of(LOGS / f"chain-tq.{k}.log")
    t_setup = one(chain, rf"setup rc 0 (\d\d:\d\d:\d\d) attempt {k}").group(1)
    t_probe = one(chain, rf"PROBE_LAUNCH {c} (\d\d:\d\d:\d\d)").group(1)
    t_probe_end = one(chain, rf"probe {c} rc 0 (\d\d:\d\d:\d\d)").group(1)
    t_run = one(chain, rf"RUN_LAUNCH {c} (\d\d:\d\d:\d\d) attempt {k}").group(1)
    t_end = one(chain, rf"run {c} rc 0 (\d\d:\d\d:\d\d)").group(1)
    assert all(mm.group(1) == str(k) for mm in (re.search(r"attempt (\d+)", ln) for ln in chain) if mm), \
        f"chain-tq.{k}.log names another attempt"
    assert not any(re.search(r"(PROBE|RUN)_LAUNCH|COMPLETE|HANDOFFS", ln) and c not in ln for ln in chain), \
        f"chain-tq.{k}.log runs another cell"
    r, i = reports[c], reports[c]["identity"]
    idl = one(chain, r"IDENTITY config (\w{12}) cell (\w+) items (\w{12}) cell\.py (\w{12}) pilot\.py (\w{12}) items\.py (\w{12}) "
                     r"rev (\w{12}) tf (\S+) torch (\S+) (\S+) (\S+) \| (.+) (\S+) cuda (\S+) (\S+)")
    assert idl.groups() == (cfg_sha[:12], c, i["items_sha256"][:12], code["cell.py"][:12], code["pilot.py"][:12],
                            code["items.py"][:12], i["model_revision"][:12], i["transformers"], i["torch"].split("+")[0],
                            i["device"], i["dtype"], i["gpu"], i["torch"], i["cuda"], i["cublas_workspace_config"]), \
        f"{c}: the pod's identity line differs from the report"
    hl = one(chain, rf"HANDOFFS {c} 1 of {N[c]} void {VOID[c]} peak_GiB (\d+\.\d\d)")
    assert hl.group(1) == f"{float(r['handoffs'][r['run_order'][0]]['peak_allocated_GiB']):.2f}", f"{c}: the probe's peak differs"
    one(chain, rf"COMPLETE {c} True handoffs {N[c]} summary_complete True summary_handoffs {N[c]}")
    one(chain, rf"{PIN[f'{c}/report.json'][:16]} results/task-quality-cell/{c}/report\.json")
    one(chain, rf"{PIN[f'{c}/summary.json'][:16]} results/task-quality-cell/{c}/summary\.json")
    one(chain, r"CHAIN_DONE")
    assert clock(t_setup) <= clock(t_probe) < clock(t_probe_end) <= clock(t_run) < clock(t_end), f"{c}: the chain's times are out of order"
    T[c] = {"probe": t_probe, "run": t_run, "end": t_end, "setup": t_setup}
assert clock(T["long"]["end"]) < clock(vd.group(2)) < clock(T["short"]["setup"]), \
    "the short cell was not launched after the long cell's home verify"

# The allocator warnings, per handoff: each is printed while its handoff runs, before that handoff's "n/N id:" line.
WARN = (r"\[W(\d{4}) (\d\d:\d\d:\d\d)\.\d+ CUDACachingAllocator\.cpp:\d+\] memory allocation failed with OOM on device 0 "
        r"while trying to allocate \d+ bytes \(free: \d+, total: \d+\)\.")
warn = {}
for c, k in CHAIN.items():
    per, pending, done = {}, 0, []
    for log in (f"tq-{c}-probe.{k}.log", f"tq-{c}-run.{k}.log"):
        for ln in lines_of(LOGS / log):
            s = ln.strip()
            assert "Traceback" not in s and not s.startswith(("Error", "RuntimeError", "torch.OutOfMemoryError")), f"{log}: {s[:80]}"
            w = re.fullmatch(WARN, s)
            if w:
                assert w.group(1) == a.run_date[5:7] + a.run_date[8:10], "an allocator line is not on --run-date"
                pending += 1
                continue
            assert "CUDACachingAllocator" not in s, f"an allocator line of another form: {s[:80]}"
            p = re.match(rf"(\d+)/{N[c]} (\S+): fresh=", s)
            if p:
                n = int(p.group(1))
                assert n == len(done) + 1 and p.group(2) == reports[c]["run_order"][n - 1], f"{log}: progress lines out of run order"
                done.append(n)
                per[n], pending = pending, 0
        assert pending == 0, f"{log}: warnings after its last handoff"
    assert done == list(range(1, N[c] + 1))
    warn[c] = per
n_warn = {c: sum(warn[c].values()) for c in CELLS}
assert n_warn["short"] == 0 and n_warn["long"] > 0, "the entry's sentences on the warnings do not hold"


def warn_text(per: dict, n: int) -> str:
    groups, i = [], 2
    while i <= n:
        j = i
        while j + 1 <= n and per[j + 1] == per[i]:
            j += 1
        groups.append((i, j, per[i]))
        i = j + 1
    parts = [f"{per[1]} on the first handoff in run order (the probe)"]
    for lo, hi, k in groups:
        span = f"handoff {lo}" if lo == hi else f"handoffs {lo} to {hi}"
        count = "one" if k == 1 else str(k)
        parts.append(f"none on {span}" if k == 0 else (f"{count} on {span}" if lo == hi else f"{count} on each of {span}"))
    return ", ".join(parts)


warn_txt = warn_text(warn["long"], N["long"])
rb = flat((R / RUNBOOK).read_text(encoding="utf-8"))
assert "Stopping rule: stop on any hash refusal or OOM;" in rb, "the runbook's stopping rule reads otherwise"

# --- the backup ----------------------------------------------------------------------------------------------------------
assert sha256_file_bytes(a.backup_log) == PIN["backup_log"], "the backup log is not the pinned file"
bl = lines_of(a.backup_log)
one(bl, r"\S+Z\s+dataset exists and is private")
rv = one(bl, r"repo (\S+) @ ([0-9a-f]{8}) \| remote (\d+) files \| local (\d+) files")
assert rv.group(3) == rv.group(4), "remote and local file counts differ"
one(bl, r"lfs-compared \d+, downloaded\+hashed \d+, problems 0")
one(bl, r"BACKUP VERIFIED")
bv = one(bl, r"(\d{4}-\d\d-\d\d)T\d\d:\d\d:\d\dZ\s+BACKUP VERIFIED: (\S+) matches \S+ in both directions\..*")
assert bv.group(2) == rv.group(1)
assert a.run_date <= bv.group(1) <= a.date, "the backup was verified before the run or after the entry's date (\"before this entry\")"
if a.dataset is not None:
    assert a.dataset == bv.group(2), "--dataset is not the repository the backup log verified"
backup_txt = f"`{a.dataset}`" if a.dataset else "a private Hub dataset"


def leaves(v, pre=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from leaves(x, f"{pre}/{k}")
    elif isinstance(v, list):
        for i_, x in enumerate(v):
            yield from leaves(x, f"{pre}/{i_}")
    else:
        yield pre, v


# --- the stopped first sitting: a description of repeatability, not a control --------------------------------------------
assert sha256_file_bytes(a.stopped_report) == PIN["stopped_report"], "the stopped sitting's report is not the pinned file"
OLD = json.loads(a.stopped_report.read_text(encoding="utf-8"))
RL = reports["long"]
both = [k for k in OLD["handoffs"] if k in RL["handoffs"]]
assert not OLD["complete"] and len(both) == len(OLD["handoffs"]) and both == RL["run_order"][:len(both)] \
    and len(OLD["run_order"]) == N["long"]
a_l, b_l = dict(leaves({k: RL["handoffs"][k] for k in both})), dict(leaves({k: OLD["handoffs"][k] for k in both}))
assert set(a_l) == set(b_l)
t_diff = [k for k in a_l if a_l[k] != b_l[k]]
assert all("seconds" in k for k in t_diff), "a non-timing field differs between the two sittings"
n_eq, n_ne = len(a_l) - len(t_diff), len(t_diff)
assert set(OLD["identity"]) == set(RL["identity"])
id_eq = sum(RL["identity"][k] == OLD["identity"][k] for k in RL["identity"])
assert id_eq == len(RL["identity"])

# --- the reader, in-process ----------------------------------------------------------------------------------------------
S = {}
for c in CELLS:
    before = (OUT / c / "summary.json").read_bytes()
    if hashlib.sha256(before).hexdigest() != PIN[f"{c}/summary.json"]:
        raise SystemExit(f"REFUSE: the mirror's {c}/summary.json is not the pinned file before the re-run; nothing rewritten")
    result = mod.summarize(OUT / c)           # fail-closed: every score recomputed from the stored prediction
    raw = (OUT / c / "summary.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN[f"{c}/summary.json"]:
        (OUT / c / "summary.json").write_bytes(before)   # leave the mirror as it was before refusing
        raise SystemExit(f"REFUSE: the rewritten {c}/summary.json is not the pinned file; the previous bytes are restored")
    assert raw == (OUT / c / "summary.pod.json").read_bytes(), f"{c}: the summary is not the pod's byte for byte"
    assert json.loads(raw.decode("utf-8")) == result
    assert result["complete"] and result["handoffs"] == N[c] and result["void"] == reports[c]["void"]
    assert result["reader_code_sha256"] == code
    h = result["headline"]
    assert h["form"] == "chat" and h["scorer"] == "first_span_exact" and h["kinds"] == ["signature"] and len(h["handoff_ids"]) == N[c]
    assert all(x == 0 for x in h["per_handoff"]["random"]), "RANDOM is not zero on every handoff"
    for arm in ARMS:
        assert h["retention"][arm]["raw"]["void"] == 0 and h["retention"][arm]["floor_normalized"]["void"] == 0
        for q in ("median", "p10", "p90"):
            assert h["retention"][arm]["raw"][q] == h["retention"][arm]["floor_normalized"][q]
    for form in ("chat", "plain"):
        assert all(result["length"][form][arm]["cap"] == CAP for arm in ARMS)
    for hid in h["under_floor"]:
        assert hid in reports[c]["run_order"] and hid not in reports[c]["void"]
    S[c] = result
RESAMPLES = int(cfg["bootstrap_resamples"])


def acc(d):
    return f"{d['median']:.4f} (p10 {d['p10']:.4f}, p90 {d['p90']:.4f}; median's 95 % interval [{d['bootstrap']['low']:.4f}, {d['bootstrap']['high']:.4f}])"


def ret(d):
    return f"{d['median']:.4f} (p10 {d['p10']:.4f}, p90 {d['p90']:.4f}; [{d['bootstrap']['low']:.4f}, {d['bootstrap']['high']:.4f}])"


def cell_block(c):
    s, h = S[c], S[c]["headline"]
    n_items = {k: s["by_kind"]["chat"]["fresh"][k]["n"] for k in ("signature", "file", "repository")}
    total = sum(n_items.values())
    assert s["length"]["chat"]["fresh"]["n"] == total
    lines = [f"*{c.capitalize()} cell* ({N[c]} handoffs; {n_items['signature']:,} signature, {n_items['file']} file and {n_items['repository']} repository items drawn, "
             f"{total:,} in all, {total * 2 * len(ARMS):,} decodes; signature items per handoff {min(h['items_per_handoff'])} to {max(h['items_per_handoff'])})."]
    for arm in ARMS:
        ln = s["length"]["chat"][arm]
        line = f"- **{LABEL[arm]}**: accuracy {acc(h['accuracy'][arm])}"
        if arm != "fresh":
            raw, nrm = h["retention"][arm]["raw"], h["retention"][arm]["floor_normalized"]
            line += f"; retention {ret(raw)}"
            if (raw["bootstrap"]["low"], raw["bootstrap"]["high"]) != (nrm["bootstrap"]["low"], nrm["bootstrap"]["high"]):
                line += f", floor-normalized interval [{nrm['bootstrap']['low']:.4f}, {nrm['bootstrap']['high']:.4f}]"
        line += f"; generations, all drawn items, mean {ln['mean_generated_tokens']:.1f} tokens, {ln['at_cap']:.3f} at the {CAP}-token cap."
        lines.append(line)
    pf = h["per_handoff"]
    below = sum(r_ < f_ for r_, f_ in zip(pf["reuse"], pf["fresh"]))
    equal = sum(r_ == f_ for r_, f_ in zip(pf["reuse"], pf["fresh"]))
    above = sum(r_ > f_ for r_, f_ in zip(pf["reuse"], pf["fresh"]))
    assert below + equal + above == N[c]
    lines.append(f"- REUSE-ALL against FRESH per handoff: below on {below}, equal on {equal}, above on {above} of {N[c]}.")
    if h["under_floor"]:
        uf = h["under_floor"]
        lines.append(f"- Under the item floor on signature items alone: {', '.join('`' + x + '`' for x in uf)} "
                     f"({len(uf)} handoff{'s' if len(uf) > 1 else ''}; {'it meets' if len(uf) == 1 else 'they meet'} the registered floor of "
                     f"{reports[c]['floor']} on form-2' items and {'stays' if len(uf) == 1 else 'stay'} in the {N[c]}).")
    pl = s["length"]["plain"]
    lines.append("- PLAIN form, generation length over all drawn items, mean tokens / fraction at the cap, FRESH / REUSE-ALL / RANDOM / "
                 "REPAIR-0.05 / -0.10 / -0.20: " + " ; ".join(f"{pl[arm]['mean_generated_tokens']:.1f} / {pl[arm]['at_cap']:.3f}" for arm in ARMS) + ".")
    sens = s["sensitivity"]
    for form in ("chat", "plain"):
        parts = []
        for sc in SCORERS:
            if form == "chat" and sc == "first_span_exact":
                continue
            d = sens[form][sc]["signature"]
            assert d["random"]["median"] == 0 or sc == "token_f1"
            parts.append(f"{sc} " + " / ".join(f"{d[arm]['median']:.4f}" for arm in ARMS))
        lines.append(f"- {form.upper()} form, signature items, median over handoffs, FRESH / REUSE-ALL / RANDOM / REPAIR-0.05 / -0.10 / -0.20: " + "; ".join(parts) + ".")
    d2 = sens["chat"]["first_span_exact"]["form2"]
    lines.append("- Form-2' items (signature plus file), CHAT first-span, same order: " + " / ".join(f"{d2[arm]['median']:.4f}" for arm in ARMS)
                 + "; the other form-2' rows are in `summary.json` (`sensitivity`).")
    bk = s["by_kind"]["chat"]
    lines.append("- By kind only, CHAT, pooled mean over items (out of the headline): file (n = " + str(bk["fresh"]["file"]["n"]) + ") "
                 + " / ".join(f"{bk[arm]['file']['mean']:.3f}" for arm in ARMS) + "; repository (n = " + str(bk["fresh"]["repository"]["n"]) + ") "
                 + " / ".join(f"{bk[arm]['repository']['mean']:.3f}" for arm in ARMS) + ".")
    return "\n".join(lines)


def peak(c):
    return max(float(h["peak_allocated_GiB"]) for h in reports[c]["handoffs"].values())


# The reading's sentences, each asserted before it is written.
H = {c: S[c]["headline"] for c in CELLS}
m = lambda c, arm: H[c]["accuracy"][arm]["median"]  # noqa: E731
rr = lambda c, arm: H[c]["retention"][arm]["raw"]  # noqa: E731
ci = lambda c, arm: H[c]["accuracy"][arm]["bootstrap"]  # noqa: E731
overlap = lambda x, y: x["low"] <= y["high"] and y["low"] <= x["high"]  # noqa: E731
for c in CELLS:
    assert m(c, "reuse") < m(c, "fresh") and m(c, "random") == 0
    assert overlap(ci(c, "reuse"), ci(c, "fresh")), f"{c}: the REUSE-ALL and FRESH intervals do not overlap"
    assert rr(c, "reuse")["bootstrap"]["high"] == 1.0
    for arm in ("repair_5pct", "repair_10pct", "repair_20pct"):
        assert overlap(ci(c, arm), ci(c, "fresh")) and overlap(ci(c, arm), ci(c, "reuse")), f"{c}: {arm}'s interval misses FRESH's or REUSE-ALL's"
    v = [m(c, arm) for arm in ("repair_5pct", "repair_10pct", "repair_20pct")]
    assert not (v[0] <= v[1] <= v[2]) and not (v[0] >= v[1] >= v[2]), f"{c}: the repair medians are ordered by budget"
    assert all(S[c]["length"]["plain"][arm]["at_cap"] == 1.0 for arm in ARMS), "a PLAIN generation ended before the cap"
    assert S[c]["length"]["chat"]["random"]["at_cap"] > 0.95, "RANDOM's generations do not almost all run to the cap"
plain = {c: S[c]["sensitivity"]["plain"]["first_span_exact"]["signature"] for c in CELLS}
assert all(plain[c]["reuse"]["median"] > plain[c]["fresh"]["median"] for c in CELLS)
three = lambda c: " / ".join(f"{m(c, arm):.4f}" for arm in ("repair_5pct", "repair_10pct", "repair_20pct"))  # noqa: E731
gpu = ident["gpu"]

ENTRY = f"""### {NUM} — {a.date} — Task-quality cell ran `[BASELINE, DESCRIPTIVE]`: structured-field recall of signature lines under FRESH, REUSE-ALL, RANDOM and REPAIR-f caches, long and short cells; no band, no cell moves

**Setup, as registered ({REG}).** RunPod community, 1x {gpu}, one pod for both cells. Long cell: probe on the largest
sender launched {a.run_date}T{T['long']['probe']}Z, run launched {T['long']['run']}Z, finished {T['long']['end']}Z. Short cell, launched on the same pod once the long cell
had been pulled home and verified: probe {T['short']['probe']}Z, run {T['short']['run']}Z, finished {T['short']['end']}Z. GPU `{gpu}`, PyTorch {ident['torch']},
Transformers {ident['transformers']}, CUDA {ident['cuda']}, fp32; config `{cfg_sha[:12]}…`, `cell.py` `{code['cell.py'][:12]}…`, `pilot.py` `{code['pilot.py'][:12]}…`,
`items.py` `{code['items.py'][:12]}…`, `core.py` `{core_sha[:12]}…` as committed, run at commit `{RUN_COMMIT[:7]}`; items files `{reports['long']['identity']['items_sha256'][:12]}…` (long) and
`{reports['short']['identity']['items_sha256'][:12]}…` (short), each equal to its report's `identity.items_sha256`. {N['long']} of {N['long']} long and {N['short']} of {N['short']} short handoffs, every
return code 0, no partial close; {VOID['long']} long and {VOID['short']} short handoffs void under the item floor and listed in the reports, as registered. Peak
allocation {peak('long'):.2f} GiB (long), {peak('short'):.2f} GiB (short). Mirrored home and verified: the summary recomputed at home at the pinned commit is
byte-identical to the one the pod wrote, in both cells. Backup: {backup_txt} (R8, verified both ways before this
entry). Pinned: long `report.json` `{PIN['long/report.json'][:12]}…`, `summary.json` `{PIN['long/summary.json'][:12]}…`; short `report.json`
`{PIN['short/report.json'][:12]}…`, `summary.json` `{PIN['short/summary.json'][:12]}…`.

**An earlier sitting, stopped; none of its scores enters the figures.** A first sitting of the long cell was stopped after {len(both)} of its {len(OLD['run_order'])}
handoffs by the operator's ruling of 2026-11-12, when the projection from those two handoffs put the cell outside the sitting's time limit
({REG}: the cost "is ASSUMED until the probe times it"). The long cell was run again from its first handoff on a new pod, and the figures
here are that run's alone. As a description of repeatability, not a registered control: on the two handoffs both sittings scored,
{n_eq:,} of {n_eq + n_ne:,} fields of the two reports' handoff records are equal and the {n_ne} that differ are all timings; the {id_eq} fields of the identity
block are equal.

**Allocator warnings.** The long cell's logs hold {n_warn['long']} `CUDACachingAllocator` warnings ("memory allocation failed with OOM on device 0"): {warn_txt}. The
short cell's logs hold none. None raised an error: no traceback, and every probe and run exited 0. The runbook's stopping rule is "stop on any
hash refusal or OOM". By the operator's ruling (2026-11-11, restated 2026-11-13) the reading given for 0061's run carries to this one. Verbatim: "{RULING_61}" This cell
registers none of 0047's numerical controls (fresh repeat, prefix copy) and no archive bridge. What held in its place: all {N['long']} long handoffs scored; the driver's hash checks on the items file, the alignment files and the
archive raised nothing; and the summarizer, which recomputes every stored score from the stored prediction, found no difference.

**Figures (`cell.summarize` in-process; headline as registered: CHAT form, signature items, first def-span exact; per handoff the
fraction of items correct; median with p10 / p90 over handoffs, `e7_stats` convention, handoffs weighted equally; the interval is the
percentile interval of the median from {RESAMPLES:,} seeded resamples of handoffs).** Retention is the arm's accuracy over FRESH's per handoff.
RANDOM scores 0 on every handoff of both cells, so the floor-normalized retention equals the raw retention on every handoff and in its
median, p10 and p90, and no handoff's denominator is void. The reader draws the two intervals from separate resamples; where the
floor-normalized interval differs from the raw one it is printed beside it. Generation lengths are over all drawn items of every kind.

{cell_block('long')}

{cell_block('short')}

**Reading (descriptive; no band, no threshold).** Under RANDOM, the norm-matched random perturbation of the fresh states, the receiver
recalls no signature line in either cell and almost every generation runs to the token cap. Under the reused cache the median accuracy
is below FRESH's in both cells, {m('long', 'reuse'):.4f} against {m('long', 'fresh'):.4f} on the long handoffs and {m('short', 'reuse'):.4f} against {m('short', 'fresh'):.4f} on the short ones, and
the intervals of the two medians overlap in both. The median retention is {rr('long', 'reuse')['median']:.4f} (long) and {rr('short', 'reuse')['median']:.4f} (short), each interval
reaching 1; the p10 of retention over handoffs is {rr('long', 'reuse')['p10']:.4f} and {rr('short', 'reuse')['p10']:.4f}. The repair arms read {three('long')} (long)
and {three('short')} (short) at 5 / 10 / 20 %: their intervals overlap FRESH's and REUSE-ALL's, and this run does not order them
by budget. Under the PLAIN form every generation of every arm runs to the {CAP}-token cap in both cells, and REUSE-ALL's median is above
FRESH's ({plain['long']['reuse']['median']:.4f} against {plain['long']['fresh']['median']:.4f}; {plain['short']['reuse']['median']:.4f} against {plain['short']['fresh']['median']:.4f}): the sign of the median difference is not the same under
the two forms, and the sensitivity rows carry no interval. This is the accuracy of a 1.7B receiver on a recall question whose answer
tokens lie inside the reused states. As {REG} registered it, it is context beside the KL of 0049, a task number beside it, and not a
verdict on any registered statistic or the agent's task success; 0049's standing sentence is not touched.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, 0036, 0038, 0044, 0045, 0047, 0049, 0058,
0061, 0062 and their records; `config/cache-behavior*.toml` and their output trees; `config/e9*.toml`; the E9 drivers and summarizers; the standing sentence of 0049.

**Scope.** One receiver, two repositories' traces, fixed proprietary-model text, same-model reuse only; one item kind in
the headline; accuracy of a 1.7B receiver on a recall question, not the agent's task success; the question sits after
the whole R, so a seam-local reading needs a later entry; no public benchmark (a composition of LongBench items into a
standalone handoff is piloted separately and enters by its own entry, if at all).

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print(f"[ordering guard: {'ok' if ordering_ok else f'NOT satisfied — the last entry is {heads[-1]}, want {PREV} stating the 2026-11-11 ruling; {NUM} must be absent'}]")
    raise SystemExit(0)
assert ordering_ok, f"ordering: the ledger's last entry must be {PREV}, stating the 2026-11-11 ruling, and {NUM} absent"
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head_m = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head_m.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
