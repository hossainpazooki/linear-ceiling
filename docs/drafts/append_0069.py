"""DRAFT append script for linear-ceiling: entry 0069 (PROVISIONAL number; the drafts README allocates it at staging) --
the cache-behavior REPAIR run (registered by 0061, its inputs re-prepared by 0067): the figures, written ONLY from
`tools.cache_behavior.run.summarize` run in-process over the verified home mirror. DESCRIPTIVE: no `verdict:` line, no
hypothesis row, no band, no cell moves.

Run facts the reader cannot know are recounted from the sitting's own records, each passed by argument and pinned by
sha256: the launch and finish times, the attempt count, the allocator warnings per handoff, and the home verify's dated
stamp (which fixes the year of --run-date). The entry's other sitting sentences (the 7 of 35 handoffs scored at the
ruling, the first five compared, the time limit raised twice, the community card, the driver's lack of an out-of-memory
handler, no copy of 0049's logs found, the operator's confirmation on 2026-11-13 and what it was made in the knowledge
of) rest on the sitting's records outside the repository and are NOT asserted here. The pins this entry
asserts are read from 0061's, 0067's and 0049's own text. The restated REUSE-ALL, RANDOM and CYCLIC figures must equal
0049's exactly, and so must every field each handoff shares with 0049's report, or this script refuses (0061: "refuses
on any disagreement"). The summary is pinned in both renderings: as this machine writes it (CRLF), and with its line
endings normalized, which is the pod's file byte for byte.

  --evidence <dir>     the sitting's final pull: aux/logs/{chain-cb.1.log,cb-repair-probe.1.log,cb-repair-run.1.log,
                       setup-cb.rc,probe-cb.1.rc,run-cb.1.rc,chain-cb.1.rc}, PULL_RESULT, VERIFY_RESULT; and beside it,
                       ../close-home-verify.out (the sitting's close, with the dated VERIFY_DONE stamp)
  --backup-log <file>  the log of the backup's last push and verify (tools/hf_backup.sh), ending "BACKUP VERIFIED"
  --dataset <repo_id>  optional; names the backup in the entry and must be the log's repository. Omitted, the entry
                       says "a private Hub dataset".
  --run-date YYYY-MM-DD  the UTC date of the chain log's times (checked against the allocator lines' month and day and
                       against the home verify's stamp in ../close-home-verify.out)
  --date YYYY-MM-DD    the heading's date: the day the entry is written and appended (entry 0021), not the run day;
                       required, a real date, not before the backup's verify and not after today (UTC)
  --preview  [--repo-root <path>]
The preview's last line must read `[ordering guard: ok]`. Ordering guard: 0047, 0049, 0061 and 0067 present, the
ledger's last entry is PREV, NUM absent. Runs `ledger_check` after appending. Run from the repo root with
`.venv/Scripts/python.exe` (the reader imports torch). Delete once appended, chained with `&&`.
"""
import argparse
import datetime as dt
import hashlib
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--evidence", type=Path, required=True)
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

NUM, PREV, REG, PREP, OLD = "0069", "0068", "0061", "0067", "0049"
OUT, OLD_OUT = R / "results" / "cache-behavior-repair", R / "results" / "cache-behavior"
E = a.evidence.resolve()
PIN = {   # full sha256 of raw bytes
    "report": "21b62a01a504f66421cd1d452c14eed5c8b07c6a6d630d9f64d670cd86d6c9f9",
    "summary_crlf": "9f343af85ea3ffa695663dcd605f083a1dd3ee3caa4f98bfa827dd8afed33ff5",   # as this machine writes it
    "summary_lf": "99c2cace0d30ff852fbd9b2d61597acd5b9ec11e9757f0476e911a3d61a67a30",     # the pod's summary.json
    "backup_log": "ea53253731717a489656758d4c75ae19cb63ab5c25105e798aca1f3f100e2c8c",
}
EVIDENCE = {"aux/logs/chain-cb.1.log": "43ea050ed4ba27580ac6c12f0786c7f4ff316b0423e18b7d490c00128e8737f9",
            "aux/logs/cb-repair-probe.1.log": "17ff89f1c68418b9889b59b84957f53049f095376bb87feee1f49bc7a6f01be0",
            "aux/logs/cb-repair-run.1.log": "ae6148627e23db8b80041a6fb6b665ec9fb6a2a1c3adf6b18412b5d0fe2d8a22",
            "PULL_RESULT": "fbf30d4438f5172c3a2ae7026a2e04ec0c5d2aaa30106c112c280dfbe07deb6a",
            "VERIFY_RESULT": "d30304fd59f0fab583e4f79dd4a12a84feeb7cff82ac24b461f39a2cdd485679",
            "../close-home-verify.out": "4cdcc7925570a579326d3673c4103f5a5778bb57b6eecf22c8e248f8961bb5ac"}
RCS = ("setup-cb.rc", "probe-cb.1.rc", "run-cb.1.rc", "chain-cb.1.rc")
RUNBOOK = "docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md"
ARMS = {"reuse": "REUSE-ALL (assembled same-model cache)", "random": "RANDOM (norm-matched perturbation)",
        "scrambled": "CYCLIC (matched states permuted, keys relocated)"}
# The ruling of 2026-11-11 on the stopping rule's "OOM", verbatim (confirmed by the operator on 2026-11-13).
RULING = ("An OOM in that rule is an out-of-memory error that ends the driver or fails a handoff. A warning from the "
          "caching allocator that it freed its cache and retried, after which the handoff scored with every control "
          "passing, is not one.")
RULING_STOP = ("If a warning ever coincides with a control, bridge or hash failure, or with a restated figure that "
               "differs from 0049's beyond the summarizer's tolerance, that is a stop under the rule as it stands.")

# --- the ledger: ordering, and the pins 0061, 0067 and 0049 state -----------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
for e in ("0047", OLD, REG, PREP):
    assert heads.count(e) == 1, f"entry {e} must be on the ledger exactly once"
ordering_ok = NUM not in heads and bool(heads) and heads[-1] == PREV


def block(t: str, entry: str) -> str:
    s = t.index(f"\n### {entry} ") + 1
    nxt = re.search(r"^### \d{4} ", t[s + 4:], re.M)
    return t[s: s + 4 + nxt.start()] if nxt else t[s:]


flat = lambda s: re.sub(r"\s+", " ", s)  # noqa: E731
b61, b67, b49 = (flat(block(text, e)) for e in (REG, PREP, OLD))
pin61 = {"config": re.search(r"`config/cache-behavior-repair\.toml` \(`([0-9a-f]{12})…`\)", b61).group(1),
         "core.py": re.search(r"Driver `tools/cache_behavior/core\.py` `([0-9a-f]{12})…`", b61).group(1),
         "run.py": re.search(r"and `run\.py` `([0-9a-f]{12})…`, which differs", b61).group(1),
         "receiver": re.search(r"receiver `(Qwen/Qwen3-1\.7B)@([0-9a-f]{12})`", b61).groups()}
pin67 = re.search(r"the report's `identity\.manifest_sha256` is `([0-9a-f]{12})…`", b67).group(1)
m49 = re.search(r"launched (\d{4}-\d\d-\d\dT\d\d:\d\dZ), finished (\d{4}-\d\d-\d\dT\d\d:\d\dZ);", b49)
pin49 = {"report": re.search(r"Pinned: `report\.json` `([0-9a-f]{12})…`", b49).group(1),
         "summary": re.search(r"`summary\.json` `([0-9a-f]{12})…`\.", b49).group(1)}
ts = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")  # noqa: E731
min49 = round((ts(m49.group(2)) - ts(m49.group(1))).total_seconds() / 60)
for phrase in ("the bound is three times 0049's run", f"{min49} minutes by its own launched and finished timestamps",
               "replaced by the probe on the largest case", "bounds what a δ-informed selector could achieve"):
    assert phrase in b61, f"0061 no longer reads {phrase!r}"
CONFIRMED = "2026-11-13"            # the operator's confirmation of the 2026-11-11 ruling, after the run had completed
assert a.run_date < CONFIRMED, "the confirmation must fall after the run"


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=R, capture_output=True, text=True, check=True).stdout.strip()


# --- the driver this script imports, and the run's identity -------------------------------------------------------------
USED = ["src/", "tools/cache_behavior/", "config/cache-behavior-repair.toml"]
assert git("status", "--porcelain", "--", *USED) == "", "a file this entry reads is modified or untracked in the working tree"
report = json.loads((OUT / "report.json").read_text(encoding="utf-8"))
RUN_COMMIT = report["git_commit"]
assert re.fullmatch(r"[0-9a-f]{40}", RUN_COMMIT)
assert subprocess.run(["git", "diff", "--quiet", RUN_COMMIT, "HEAD", "--", *USED], cwd=R).returncode == 0, \
    "the driver, the package or the config changed since the commit the run used"
cfg_path, core_path, run_path = (R / "config/cache-behavior-repair.toml", R / "tools/cache_behavior/core.py",
                                 R / "tools/cache_behavior/run.py")
cfg_sha, core_sha, run_sha = (sha256_text_file(p) for p in (cfg_path, core_path, run_path))
assert cfg_sha.startswith(pin61["config"]) and core_sha.startswith(pin61["core.py"]) and run_sha.startswith(pin61["run.py"]), \
    "the committed config or driver is not 0061's pin"
ident = report["identity"]
assert ident["config_sha256"] == cfg_sha, "the run recorded another config"
assert ident["code_sha256"] == {"run.py": run_sha, "core.py": core_sha}, "the run recorded another driver"
assert ident["manifest_sha256"].startswith(pin67) and sha256_file_bytes(OUT / "inputs" / "manifest.json") == ident["manifest_sha256"], \
    "the run's inputs are not 0067's manifest"
assert ident["cublas_workspace_config"] == ":4096:8"
cfg_toml = __import__("tomllib").loads(cfg_path.read_text(encoding="utf-8"))
assert report["model"] == cfg_toml["model"] == pin61["receiver"][0] and report["model_revision"] == cfg_toml["revision"] \
    and report["model_revision"].startswith(pin61["receiver"][1]), f"the run's receiver is not the one {REG} registers"
assert sha256_file_bytes(OUT / "report.json") == PIN["report"], "report.json is not the pinned file"
assert report["complete"] and report["excluded"] == [] and len(report["run_order"]) == 35 \
    and list(report["scores"]) == report["run_order"], "the scored set is not the registered 35 in run order"
sys.path.insert(0, str(R))                       # run.py does `from .core import …`: import it as the package module
mod = importlib.import_module("tools.cache_behavior.run")
assert Path(mod.__file__).resolve() == run_path.resolve(), f"imported {mod.__file__}, expected {run_path}"
cfg = __import__("tomllib").loads(cfg_path.read_text(encoding="utf-8"))


def lines_of(p: Path) -> list:
    return re.split(r"\r\n|\r|\n", p.read_text(encoding="utf-8", errors="replace"))


def one(lines: list, pattern: str) -> re.Match:
    hits = [mm for mm in (re.fullmatch(pattern, ln.strip()) for ln in lines) if mm]
    assert len(hits) == 1, f"expected exactly one line matching {pattern!r}, found {len(hits)}"
    return hits[0]


# --- the sitting's records, by digest and by line ----------------------------------------------------------------------
for rel, want in EVIDENCE.items():
    assert sha256_file_bytes(E / rel) == want, f"{rel} is not the pinned file"
for rc in RCS:
    assert (E / "aux" / "logs" / rc).read_text().strip() == "0", f"{rc} is not 0"
assert (E / "PULL_RESULT").read_text().strip() == "PULL_OK final"
assert (E / "VERIFY_RESULT").read_text().strip().startswith("VERIFY_OK home summarize rc 0, EXACT_EQUAL")
chain = lines_of(E / "aux/logs/chain-cb.1.log")
one(chain, r"setup rc 0 \d\d:\d\d:\d\d attempt 1")
t_probe = one(chain, r"PROBE_LAUNCH (\d\d:\d\d:\d\d) attempt 1").group(1)
t_probe_end = one(chain, r"probe rc 0 (\d\d:\d\d:\d\d)").group(1)
t_run = one(chain, r"RUN_LAUNCH (\d\d:\d\d:\d\d) attempt 1").group(1)
t_end = one(chain, r"run rc 0 (\d\d:\d\d:\d\d)").group(1)
assert all(mm.group(1) == "1" for mm in (re.search(r"attempt (\d+)", ln) for ln in chain) if mm), \
    "the chain log records another attempt"
idl = one(chain, r"IDENTITY manifest (\w{12}) config (\w{12}) run\.py (\w{12}) core\.py (\w{12}) \| (.+) (\S+) (\S+) cuda (\S+) (\S+)")
assert idl.groups() == (ident["manifest_sha256"][:12], cfg_sha[:12], run_sha[:12], core_sha[:12], ident["gpu"], ident["torch"],
                        ident["transformers"], ident["cuda"], ident["cublas_workspace_config"]), "the pod's identity line differs from the report"
one(chain, r"COMPLETE True scored 35 summary_complete True summary_scored 35")
one(chain, rf"{PIN['report'][:16]} results/cache-behavior-repair/report\.json")
one(chain, rf"{PIN['summary_lf'][:16]} results/cache-behavior-repair/summary\.json")
one(chain, r"CHAIN_DONE")
clock = lambda s: dt.datetime.strptime(f"{a.run_date}T{s}", "%Y-%m-%dT%H:%M:%S")  # noqa: E731
assert clock(t_probe) < clock(t_probe_end) <= clock(t_run) < clock(t_end), "the chain log's times are not in order on one day"
hv = lines_of(E.parent / "close-home-verify.out")       # the sitting's close: the only dated stamp, which fixes the year
assert one(hv, r"VERIFY_HEAD ([0-9a-f]{7,40})").group(1) == RUN_COMMIT[:7]
one(hv, r"EXACT_EQUAL")
vd = one(hv, r"VERIFY_DONE (\d{4}-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z \(result in .+/pull-final/VERIFY_RESULT\)")
assert vd.group(1) == a.run_date and clock(t_end) < clock(vd.group(2)), "the home verify is not on --run-date after the run"
probe_min = round((clock(t_probe_end) - clock(t_probe)).total_seconds() / 60)
run_min = round((clock(t_end) - clock(t_run)).total_seconds() / 60)

# The allocator warnings, per handoff: each is printed while its handoff runs, before that handoff's "n/35" line.
WARN = (r"\[W(\d{4}) (\d\d:\d\d:\d\d)\.\d+ CUDACachingAllocator\.cpp:\d+\] memory allocation failed with OOM on device 0 "
        r"while trying to allocate \d+ bytes \(free: \d+, total: \d+\)\.")
per, pending, done = {}, 0, []
for log in ("aux/logs/cb-repair-probe.1.log", "aux/logs/cb-repair-run.1.log"):
    for ln in lines_of(E / log):
        s = ln.strip()
        assert "Traceback" not in s and not s.startswith(("Error", "RuntimeError", "torch.OutOfMemoryError")), f"{log}: {s[:80]}"
        w = re.fullmatch(WARN, s)
        if w:
            assert w.group(1) == a.run_date[5:7] + a.run_date[8:10], "an allocator line is not on --run-date"
            pending += 1
            continue
        assert "CUDACachingAllocator" not in s, f"an allocator line of another form: {s[:80]}"
        p = re.fullmatch(r"(\d+)/35 (\S+)", s)
        if p:
            n = int(p.group(1))
            assert n == len(done) + 1 and p.group(2) == report["run_order"][n - 1], "progress lines out of run order"
            done.append(n)
            per[n], pending = pending, 0
    assert pending == 0, f"{log}: warnings after its last handoff"
assert done == list(range(1, 36))
n_warn = sum(per.values())


def word(k: int) -> str:
    return {0: "none", 1: "one", 2: "two", 3: "three", 4: "four"}.get(k, str(k))


groups, i = [], 2
while i <= 35:
    j = i
    while j + 1 <= 35 and per[j + 1] == per[i]:
        j += 1
    groups.append((i, j, per[i]))
    i = j + 1
parts = [f"{per[1]} on the first handoff in run order (the probe)"]
for lo, hi, k in groups:
    span = f"handoff {lo}" if lo == hi else f"handoffs {lo} to {hi}"
    parts.append(f"none on {span}" if k == 0 else (f"{word(k)} on {span}" if lo == hi else f"{word(k)} on each of {span}"))
warn_txt = ", ".join(parts[:-1]) + ", and " + parts[-1]

# 0049's run on the same probe: its runbook's own reading of the same warnings.
rb = flat((R / RUNBOOK).read_text(encoding="utf-8"))
assert "three `CUDACachingAllocator` \"memory allocation failed with OOM … retrying\" warnings" in rb
assert "(the allocator warnings were retries, not failures)" in rb

# --- the backup -----------------------------------------------------------------------------------------------------------
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

# --- the reader, in-process --------------------------------------------------------------------------------------------
before = (OUT / "summary.json").read_bytes()
if hashlib.sha256(before).hexdigest() not in (PIN["summary_crlf"], PIN["summary_lf"]):
    raise SystemExit("REFUSE: the mirror's summary.json is neither pinned rendering before the re-run; nothing rewritten")
result = mod.summarize(OUT, OUT / "inputs")         # fail-closed: re-hashes every case record, checks the cohort and the witness
assert result["complete"] and result["scored"] == 35 and result["excluded"] == []
summ_raw = (OUT / "summary.json").read_bytes()
if hashlib.sha256(summ_raw).hexdigest() != PIN["summary_crlf"]:
    (OUT / "summary.json").write_bytes(before)        # leave the mirror as it was before refusing
    raise SystemExit("REFUSE: the rewritten summary.json is not the pinned rendering; the previous bytes are restored")
lf_summary = hashlib.sha256(summ_raw.replace(b"\r\n", b"\n")).hexdigest()
assert lf_summary == PIN["summary_lf"] == sha256_file_bytes(OUT / "summary.pod.json"), "the summary is not the pod's once normalized"
pod = json.loads((OUT / "summary.pod.json").read_text(encoding="utf-8"))
assert json.loads(summ_raw.decode("utf-8")) == result == pod


def leaves(v, pre=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from leaves(x, f"{pre}/{k}")
    elif isinstance(v, list):
        for i_, x in enumerate(v):
            yield from leaves(x, f"{pre}/{i_}")
    else:
        yield pre, v


home_l, pod_l = dict(leaves(result)), dict(leaves(pod))
pod_diff = sum(1 for k in set(home_l) | set(pod_l) if home_l.get(k) != pod_l.get(k))
assert pod_diff == 0

# --- against 0049: the restated arms and every field each handoff shares ------------------------------------------------
assert sha256_file_bytes(OLD_OUT / "report.json").startswith(pin49["report"]), "0049's report is not the file 0049 pins"
assert sha256_file_bytes(OLD_OUT / "summary.json").startswith(pin49["summary"]), "0049's summary is not the file 0049 pins"
old = json.loads((OLD_OUT / "summary.json").read_text(encoding="utf-8"))
old_report = json.loads((OLD_OUT / "report.json").read_text(encoding="utf-8"))
arms = result["arms"]
n_stat = n_diff = 0
for arm in ARMS:
    for st in ("mean_kl", "p90_kl", "top1_agreement"):
        for q in ("median", "p10", "p90"):
            n_stat += 1
            n_diff += arms[arm][st][q] != old["arms"][arm][st][q]
assert set(result["attention"]) == set(old["attention"])
att_n = att_diff = 0
for k in result["attention"]:
    for q in ("median", "p10", "p90"):
        assert result["attention"][k] is not None and old["attention"][k] is not None
        att_n += 1
        att_diff += result["attention"][k][q] != old["attention"][k][q]
assert n_diff == 0 and att_diff == 0, f"a restated statistic differs from 0049's ({n_diff} arms, {att_diff} attention)"
sc, osc = report["scores"], old_report["scores"]
assert set(sc) == set(osc) and len(sc) == 35
with_controls = [k for k in sc if sc[k]["controls"]]
assert with_controls == [report["run_order"][0]], "the controls are not on the probe handoff alone"
n_bridge = sum(len(list(leaves(sc[k]["archive_bridge_mean"]))) for k in sc)


def shared(e: dict) -> dict:
    d = dict(leaves({x: e[x] for x in ("controls", "archive_bridge_mean", "peak_allocated_GiB",
                                       "scored_continuation_tokens", "witness_count")}))
    d.update({f"/arms/{arm}{p}": v for arm in ARMS for p, v in leaves(e["arms"][arm])})
    return d


per_eq = per_ne = 0
for k in sc:
    x, y = shared(sc[k]), shared(osc[k])
    for key in set(x) | set(y):
        if "seconds" in key or "time" in key:
            continue
        if x.get(key) == y.get(key):
            per_eq += 1
        else:
            per_ne += 1
assert per_ne == 0, f"{per_ne} per-handoff fields differ from 0049's report"
tokens = sum(int(e["scored_continuation_tokens"]) for e in sc.values())
peak = max(float(e["peak_allocated_GiB"]) for e in sc.values())
ctrl = {n: max(e["controls"][n]["max_logit_error"] for e in sc.values() if n in e["controls"]) for n in ("fresh_repeat", "prefix_copy")}
limit = float(cfg["control_max_logit_error"])
assert ctrl["fresh_repeat"] == 0.0 and ctrl["prefix_copy"] <= limit
limit_txt = f"{limit:.0e}".replace("e-0", "e-")

# --- rendering ----------------------------------------------------------------------------------------------------------
s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"  # noqa: E731
line = lambda label, r: (f"- **{label}**: mean KL per handoff {s(r['mean_kl'])} nats; p90 KL {s(r['p90_kl'])}; "  # noqa: E731
                         f"top-1 agreement {s(r['top1_agreement'])}.")
budget_lines = []
for pct in ("5", "10", "20"):
    budget_lines.append(line(f"ORACLE-0.{int(pct):02d} (the top {pct} % of matched tokens by archived δ_K, recomputed)", arms[f"oracle_ranked_{pct}pct"]))
    budget_lines.append(line(f"RANDOM-0.{int(pct):02d} (the same number of matched tokens drawn uniformly, recomputed)", arms[f"random_ranked_{pct}pct"]))
m = lambda arm, st="mean_kl", q="median": arms[arm][st][q]  # noqa: E731
three = lambda f: " / ".join(f(p) for p in ("5", "10", "20"))  # noqa: E731
for pct in ("5", "10", "20"):
    assert m(f"oracle_ranked_{pct}pct") < m(f"random_ranked_{pct}pct"), "the reading's mean-KL sentence does not hold"
    assert m(f"oracle_ranked_{pct}pct", "top1_agreement") > m(f"random_ranked_{pct}pct", "top1_agreement"), "the top-1 sentence does not hold"
dur = lambda mins: f"{mins // 60} hours {mins % 60} minutes" if mins >= 60 else f"{mins} minutes"  # noqa: E731

ENTRY = f"""### {NUM} — {a.date} — Cache-behavior REPAIR ran `[BASELINE, DESCRIPTIVE]`: oracle-ranked recompute of the top 5 / 10 / 20 % of matched tokens against the reused cache, beside a random selection at each budget, on the 35 long handoffs; no band, no cell moves

**Setup, as registered ({REG}, its inputs sentence as amended by {PREP}).** RunPod community {ident['gpu']} (one card); probe on the
largest handoff launched {a.run_date}T{t_probe}Z, run launched {t_run}Z, finished {t_end}Z, one attempt, no restart of the driver; GPU
`{ident['gpu']}`, PyTorch {ident['torch']}, Transformers {ident['transformers']}, CUDA {ident['cuda']}; config `{cfg_sha[:12]}…`, driver `core.py`
`{core_sha[:12]}…` / `run.py` `{run_sha[:12]}…` as committed, run at commit `{RUN_COMMIT[:7]}`. Inputs: manifest `{ident['manifest_sha256'][:12]}…` ({PREP}),
equal to the report's `identity.manifest_sha256`. 35 of 35 handoffs scored, {tokens:,} continuation tokens, none excluded; peak allocation
{peak:.2f} GiB. Backup: {backup_txt} (R8, verified both ways before this entry). Pinned: `report.json` `{PIN['report'][:12]}…`,
`summary.json` `{PIN['summary_crlf'][:12]}…` as the home machine wrote it; with its line endings normalized it is `{lf_summary[:12]}…`, byte for byte
the summary the pod wrote ({pod_diff} of {len(home_l)} leaves differ).

**Wall time.** {REG} sized the run at three times {OLD}'s {min49} minutes, "replaced by the probe on the largest case". The probe took {probe_min}
minutes and the run {dur(run_min)}. The sitting's time limit was raised twice while the run was in progress: once by the party
running the sitting under a standing rule for a watched run, once by the operator's approval. No figure depends on the wall time.

**Allocator warnings, and the stopping rule's "OOM".** The probe and run logs hold {n_warn} `CUDACachingAllocator` warnings ("memory allocation
failed with OOM on device 0"): {warn_txt}. None raised an error: no traceback, the probe and the run exited 0, and the driver has no
out-of-memory handler. Entry {OLD}'s run met the same on its probe: its runbook (`{RUNBOOK}`)
records three such warnings on the same handoff on the same card type and reads them as "retries, not failures"; it says that run's
logs were pulled home and hashed, but no copy of them is found now, so whether its later handoffs had more is not known. Ruling of
2026-11-11, made on the operator's delegation with 7 of the 35 handoffs scored, before the run completed and before any complete summary
of it existed; by its own account the party ruling had opened the partial report of the first five handoffs and compared the fields it
shares with {OLD}'s, not the repair arms. The operator confirmed it on {CONFIRMED}, after the run had completed, in the knowledge that
{OLD}'s run had recorded the same three warnings. Verbatim: "{RULING}" And: "{RULING_STOP}" None did. For every one
of the 35 handoffs the archive bridge ({n_bridge} values), the peak allocation, the continuation-token count, the witness count and the three
restated arms equal entry {OLD}'s report field for field, and so do the two controls on the probe handoff, the only handoff that carries
them ({per_eq:,} fields equal, {per_ne} differing; timing fields and each case file's name and hash aside).

**Numerical controls (registered limits in 0047, unchanged by {REG}):** fresh-repeat maximum logit error {ctrl['fresh_repeat']:.2e}, prefix-copy
maximum logit error {ctrl['prefix_copy']:.2e} (limit {limit_txt}), on the probe handoff, the only one that carries the two controls. Every per-handoff
archive bridge passed, or the driver would have stopped before scoring that handoff.

**The restated arms, a within-run control against {OLD} (not new figures).** REUSE-ALL, RANDOM and CYCLIC: {n_stat - n_diff} of {n_stat} summary
statistics equal entry {OLD}'s exactly ({n_diff} differing). The fresh-attention slice: {att_n - att_diff} of {att_n} statistics equal {OLD}'s.

**Figures (`run.summarize` in-process: every case record re-hashed, the scored set checked against the registered 35, the logit witness
re-checked; medians with p10 / p90 over handoffs, `e7_stats` convention, handoffs weighted equally).** KL is KL(fresh ‖ candidate) per
scored token, averaged per handoff. FRESH is 0 by definition. A budget f is ⌈|M| × f⌉ matched tokens of each handoff.

{line(ARMS['reuse'] + ", as " + OLD, arms['reuse'])}
{chr(10).join(budget_lines)}

**Reading (the registered pair at each budget; descriptive).** The pair (ORACLE-f, RANDOM-f) at one budget is the only comparison
{REG} registers. In median mean-KL the ranked selection reads below the uniform selection of the same size at every budget:
{three(lambda p: f"{m(f'oracle_ranked_{p}pct'):.4f} against {m(f'random_ranked_{p}pct'):.4f}")} nats at 5 / 10 / 20 %. In median top-1 agreement it reads above:
{three(lambda p: f"{m(f'oracle_ranked_{p}pct', 'top1_agreement'):.4f} against {m(f'random_ranked_{p}pct', 'top1_agreement'):.4f}")}. Stated beside the pair, as registered and not compared
with it here: REUSE-ALL's median mean-KL {m('reuse'):.4f} and top-1 {m('reuse', 'top1_agreement'):.4f}; FRESH's 0 and 1 by definition. No paired per-handoff
statistic, band or threshold is registered and none is read. The ranking is an oracle: it reads the fresh states, and a
recomputed fraction of matched tokens is not a serving cost. {REG}'s scope says ORACLE-f "bounds what a δ-informed selector could
achieve"; that is not shown, there or here: ranking by archived δ_K is not shown to give the lowest mean KL at a budget, so another
choice of the same number of tokens could score lower. **Top-1 agreement is not
task accuracy and no acceptance threshold exists**; "no downstream task-quality number is claimed" stands.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, 0036, 0038, 0044, 0045, 0047, {OLD}, 0058 and
their records; `config/cache-behavior.toml` and `results/cache-behavior/`; `config/e9*.toml`; the E9 drivers and summarizers.

**Scope.** One receiver, one corpus, the 35 long handoffs; fixed proprietary-model text; same-model only; three budgets and two selection
rules; selection by archived δ_K is an oracle (it reads the fresh states) and is not a deployable policy; that ORACLE-f bounds
what a δ-informed selector could achieve, as {REG}'s scope has it, is not shown (above); generation quality after reuse not measured.

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
