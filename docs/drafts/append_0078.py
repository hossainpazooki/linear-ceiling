"""DRAFT append script for linear-ceiling: the FAB v2 document-reuse opportunity's figures (registered by 0075), written
ONLY from `linear_ceiling.fab_reuse.summarize` run in-process over the run's private log root. DESCRIPTIVE: no
`verdict:` line, no hypothesis row, no band, no cell moves. The number is the ledger's next after 0077, PROVISIONAL
until the drafts README stages this script.

0075: "The figures enter by their own entry, which runs the summarizer in-process; no figure is typed." The summary of
record, `results/fab-reuse/summary.json`, is written once by the module's own command (its gate first) and pinned here
by sha256; this script runs the gate, recomputes the summary in-process with the committed module and refuses unless
the bytes are equal. Run facts (each launch's start and end and what ended it, the launches by question, which questions
started before 0075's commit, the stops of new starts and the restarts, whether the spend limit rose) are recounted
from the wrapper's launch records and the run's output logs, each passed by argument and pinned by sha256 here. No
spend, limit amount or spend estimate enters the entry: the script reads the records' times, stops, exits and
manifests, and from the output logs the stop, end and restart lines. Every log file the summary hashed must carry the
sha256 the wrapper's manifest recorded when its question ended. The User-Agent change is stated by its diff, computed
here from the pinned harness tarball and the run's harness file, with the hard-coded contact elided; every other file
of the tarball must be byte-identical in the run's harness folder. When the summary of record was written is read from
the summarizer's own output log, pinned by sha256 here: one start and one end of the module's command, rc 0, and the
line keeping this summary, by its sha256 and size.

    python -I docs/drafts/append_NUM.py --repo-root . --date YYYY-MM-DD --runs <log root> --questions <public.csv>
        --tokenizer-json <tokenizer.json> --records <wrapper records dir> --wrapper-out <log> [<log> ...]
        --tarball <harness tarball> --harness <the run's harness folder> --summarizer-out <its output log> [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root must be the current directory and the
top of its git work tree, and the imported `linear_ceiling` must be that tree's; run it with the tree's venv python
(the summarizer imports numpy and tokenizers). The script refuses under -O. Outside `--preview` it refuses until the
drafts README stages this script with the next number. Before the write, the ledger must equal HEAD's, be unmodified
and pass `ledger_check`; after it `ledger_check` runs again, and on a failure the old bytes go back. The script writes
only ledger/ledger.md.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import textwrap
import traceback
from pathlib import Path

if not __debug__ or sys.flags.optimize:
    raise SystemExit("REFUSED: python runs with -O or PYTHONOPTIMIZE set, which strips every guard (assert) in this script")


def _refused(et, ev, tb):
    """Any exception is a refusal: print the guard's line so the output shows which one fired; exit status 1."""
    fr = [f for f in traceback.extract_tb(tb) if Path(f.filename).resolve() == Path(__file__).resolve()] or traceback.extract_tb(tb)
    sys.stderr.write(f"REFUSED: {et.__name__} at line {fr[-1].lineno}: {ev}\n  guard: {fr[-1].line}\n")


sys.excepthook = _refused
ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--repo-root", type=Path, required=True)
ap.add_argument("--runs", type=Path, required=True)
ap.add_argument("--questions", type=Path, required=True)
ap.add_argument("--tokenizer-json", type=Path, required=True)
ap.add_argument("--records", type=Path, required=True)
ap.add_argument("--wrapper-out", type=Path, nargs="+", required=True)
ap.add_argument("--tarball", type=Path, required=True)
ap.add_argument("--harness", type=Path, required=True)
ap.add_argument("--summarizer-out", type=Path, required=True)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"            # the module's own git reads inherit it: no index refresh
ENV = dict(os.environ)
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True, env=ENV)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
sys.path.insert(0, str(R / "src"))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling import fab_reuse as fr                                 # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
for _m in (_lc, fr):
    assert Path(_m.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_m.__file__}, not the tree's"

LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
PINNED_MODEL = "anthropic/claude-opus-5-5-no-fallback"
# 0075's pins (its text gives each to 12 hex digits; the full values are those its script computed at append)
PINS_0075 = {"config/fab-reuse.toml": "773ddef7e2c2389586ba1630afa70b8b8b2504792e1ac030093ecef7fe33362c",
             "src/linear_ceiling/fab_reuse.py": "b884ec174132fa43da9bab585d590f59579d06c8f143badc5d1db9fbb2460149",
             "tests/test_fab_reuse.py": "8c9b4438918ecef3657d3e5bdcb0e4f6abcf594a8ba7d3e3146a45572c35c724"}
COMMIT_0075 = "7e772ef604d0a91c5c119005133d00b1730bc0ed"      # ledger: append 0075
SET_0075 = ("45e3e7e119cf78b2e010b71aab9db6f4aa676961", "bde693951bad83dcdea54e5997ed427bd2da0c33", COMMIT_0075,
            "bf56800ba57af0a8c692b59a22223c1abd96176b")           # 0075's commit set, in order
TARBALL_MEMBER = "finance-agent-v2-25b6cab9bcb4f8f9857f2e1a6721732c85511c5c/"
TOOLS = "finance_agent/tools.py"
TOOLS_BEFORE = "d58fc6af24f5b64136671798e0da6ae307710db230f98aa7a8602dd2ad4e232a"   # the tarball's
TOOLS_AFTER = "ee32f478a2ab80ca8110fa1c85b2eb889eaf7f60160b7cab395ba1b74d8ea8fa"    # the run's
# --- filled once the run has ended and the summary of record exists (the fill step checks each against its file) ---
SUMMARY_SHA256 = "b0325c4bbf1982d35cbf0a9a42e544323b269741c02f60ad3707527622df003a"
RECORDS = {  # rowNN-k.json -> sha256, every launch record of the run
    "row01-1.json": "9dd79e15c5ec20e8cb70b88ae7adda0da227d03560dba0a13d1fbdb78b35a1a2",
    "row02-1.json": "8fe7406932258a6c238571778967ec2659288df8cf30fc23d1ff4a7b35b48fc6",
    "row03-1.json": "deb3dcf820b34199a281804d781d8b6d3cf9430d8973f2cb20a103def841213a",
    "row04-1.json": "7037b1eb22cd75459954afad7a9d7d539bec6f37747c4b6c5d285e8598c6de36",
    "row05-1.json": "68d0b86ce3947d6fe0de080903e85183b06324acba40b657bfff43bad804ef98",
    "row06-1.json": "329b625a1fc1c8b73da8253cd3facf4315031ca8a829b745d8a4fb9a7b184d3d",
    "row07-1.json": "0dae9e1d79744e95b4c9b91f3b3348c9f5bf4a7b647fe66f6b136acb9ed86e15",
    "row08-1.json": "2b2ad2f41681a023ba2eb9eac56cb91a461709b5771d3985121d0ed463bb41b0",
    "row09-1.json": "b8fd8238f8c017db076a1e576c590baa752b0f4f34d37b98cfca9b470c23ceb2",
    "row10-1.json": "190a414292d72419de2a058e3a9676a1d00c456094c99d9a2c192dceb8de4399",
    "row11-1.json": "db9a3f731cbcdb89d3dc641dd5e38e52b8719a171d2b175d48b7c86f2ae287bb",
    "row12-1.json": "3fcc20a902027ea2e14a5447b1c48333ca44261b23bf99b30f14fa17c0704cc7",
    "row13-1.json": "3beac8a89ac114b5db18debba18d0c9676b39daaf660c1dafb04b7a468d3f595",
    "row14-1.json": "8602d08f103963a17f7250ba667ef98637feffede74270c26b00377d14b8308d",
    "row15-1.json": "0cd58c05ca275857c34063c2fa386d64d780491dd9506eeed36ed3e550dfafd0",
    "row16-1.json": "0c23fa6ad1faccf557cfe134252a05a1a2b040fea8c642735eb75f7f61e2fe92",
    "row17-1.json": "1ca1b4a08e3b088825b4e14d0bc7ac596e733211301a5de11ad8af5982f3ade4",
    "row18-1.json": "6e07e4125b40c89d0bd107e575767ca2f93bd86866c26b97f2be4899f3caf497",
    "row19-1.json": "3e56952bd52e01fae8a4036daf3f5bb2762ec8c09ef2e004a5b8507bcb66cf69",
    "row20-1.json": "6114e4e67974eb8b46277cffc9ca00cc9a4ce53eeb9a845b4c9f78671133afdb",
    "row21-1.json": "d42837c994c5b3cba090afcae11942a5fb386955b5f7436aef74322e5412da1e",
    "row22-1.json": "faae564b4df2ac416d6f8957bebcf3dedc352bf65b1e13390a51c49235554b46",
    "row23-1.json": "a7b32666bdb5e72893db34e28b61ed169f4189a0a7006b7a746fe62d97f76270",
    "row24-1.json": "32165dd8dee7732d96706faf0cd5fce94f35c7509733d5892affc8146ce02c08",
    "row25-1.json": "3973892695e7b89d69502449bcaf5f49ce452af3b72c6ac8610477b68610ead2",
    "row26-1.json": "790e36396934651a88d95ee5905ddf63deb8c02d3c68d9375a42ce32b566ff4f",
    "row27-1.json": "4c5bfdb017fc29a8398bd7d7c55b2b97b0ea3d809dc5ef9a539f2bb42ddfac33",
}
WRAPPER_OUT = {  # output log name -> sha256, in run order
    "run26.out": "c465ebc14615301e89afab1b02a105a5defccfeda23cdb83815e442b0925c447",
    "margin27.out": "dc3b771856396b368550bc2d7d78f905abbf89760bf3165a47667418d4d594c8",
    "run27.out": "1439dda48d15b909314d9bde27f684991cd30b046e6231f3b5f8ac43db1f5902",
    "run28.out": "e8d3386e731a94734043ae951e267cd4a3e303e6ecdb64e753b4838db663011a",
    "run29.out": "8e78939e5fcd838b6d9da18dad3b3f892e47815e7d21ad3083479c641b5e2b9f",
}
SUMMARIZER_OUT_SHA256 = "3651135710ebc3edff42644aec788cf3d169901f01ef9a7e50beb627821c91f3"   # the summarizer's own output log, passed by --summarizer-out
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


def git(*args) -> bytes:
    return subprocess.run(["git", "-C", str(R), *args], capture_output=True, check=True, env=ENV).stdout


def block(t: str, entry: str) -> tuple:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} heading lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def once(t: str, entry: str, phrase: str) -> int:
    """The line of the phrase (any whitespace between its words), which must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(re.finditer(r"\s+".join(re.escape(w) for w in phrase.split()), b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {phrase[:60]!r}"
    return t.count("\n", 0, start + hits[0].start()) + 1


def utc(s: str) -> dt.datetime:
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s), f"not a UTC stamp: {s!r}"
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def preview_note(msg: str) -> None:
    print(f"[preview] {msg}; the append refuses until it is", file=sys.stderr)


# --- this ledger: the ordering, 0075's pins as its text states them ---------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0077", f"the ledger's last entry is {PREV}, not 0077"
assert "0075" in heads, "0075 is not on the ledger"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
_, B75 = block(text, "0075")
for rel, full in PINS_0075.items():
    assert f"`{rel}` (`{full[:12]}…`)" in B75, f"0075 does not pin {rel} at {full[:12]}"
assert "The figures enter by their own entry, which runs the summarizer in-process; no figure is typed." in " ".join(B75.split())
L75 = {k: once(text, "0075", p) for k, p in {
    "own": "The figures enter by their own entry, which runs the summarizer in-process; no figure is typed.",
    "ua": "The outcome entry states that change by its diff, with any contact elided.",
    "launches": "the outcome entry reports the launch count by question.",
    "limit": "the outcome entry names the questions run and says whether it was raised.",
    "stops": "every launch is counted, and the outcome entry reports each stop.",
    "before": "the outcome entry says which questions had started before the commit.",
    "used": "The outcome entry says why starts ended and whether either was used.",
    "label": "Every reuse figure carries the label",
    "pins": "Pinned at append:",
    "smoke": "Set after it: from it, the token ceiling and the number of questions run at once",
    "otherstop": "Any other check that fails stops new starts at once.",
}.items()}

# --- the pinned files, committed as 0075 pins them; the module's own gate ----------------------------------------------------
for rel, full in PINS_0075.items():
    assert sha256_text_file(R / rel) == full, f"{rel} is not the file 0075 pins"
    assert hashlib.sha256(git("show", f"{COMMIT_0075}:{rel}").replace(b"\r\n", b"\n")).hexdigest() == full, \
        f"{rel} at 0075's commit is not the pinned file"
FILES_COMMIT = SET_0075[0]                       # the three pinned files were added by the first commit of 0075's set
for rel in PINS_0075:
    assert git("log", "--format=%H", "--diff-filter=A", "--", rel).split() == [FILES_COMMIT.encode()], \
        f"{rel} was not added by {FILES_COMMIT[:7]} alone"
assert git("log", "--format=%H", f"{FILES_COMMIT}..HEAD", "--", *PINS_0075) == b"", "a pinned file changed after 0075's set"
assert git("ls-files", "--", "results/fab-reuse") == b"", "a file under results/fab-reuse/ is tracked"
cfg = fr.load_config(R / "config/fab-reuse.toml", R)
assert cfg.required_entries == ("0075",) and cfg.harness["model"] == PINNED_MODEL and cfg.cohort == 27
fr.assert_ready(cfg, R)                          # the gate: ledger, config, module, test committed as-is; 0075 on HEAD
RUN = cfg.run
_t75 = {c: int(git("show", "-s", "--format=%ct", c).strip()) for c in SET_0075}
assert git("rev-list", "--count", f"{SET_0075[0]}^..{SET_0075[-1]}").strip() == b"4", "0075's commit set is not four commits"
assert git("merge-base", "--is-ancestor", SET_0075[-1], "HEAD") == b"", "0075's commit set is not on HEAD's history"
assert b"### 0075 " in git("show", f"{COMMIT_0075}:ledger/ledger.md") and \
    b"### 0075 " not in git("show", f"{COMMIT_0075}^:ledger/ledger.md"), f"{COMMIT_0075[:7]} is not the commit that appended 0075"
T75 = dt.datetime.fromtimestamp(_t75[COMMIT_0075], dt.timezone.utc)
T75_FIRST = dt.datetime.fromtimestamp(min(_t75.values()), dt.timezone.utc)
T75_LAST = dt.datetime.fromtimestamp(max(_t75.values()), dt.timezone.utc)

# --- the summary of record, recomputed in-process ------------------------------------------------------------------------------
OUT = cfg.results_dir / "summary.json"
assert OUT.is_file(), f"{OUT.relative_to(R).as_posix()} does not exist: the module's command writes it first"
assert sorted(p.name for p in cfg.results_dir.iterdir()) == ["summary.json"], "results/fab-reuse/ holds more than the summary"
held = OUT.read_bytes()
if SUMMARY_SHA256 == "FILL":
    assert a.preview, "the summary of record is not pinned in this script"
    preview_note("the summary of record is not pinned in this script")
else:
    assert hashlib.sha256(held).hexdigest() == SUMMARY_SHA256, "results/fab-reuse/summary.json is not the summary of record"
res = fr.provenance(fr.summarize(cfg, a.runs, a.questions,
                                 fr.reader_encoder(a.tokenizer_json, cfg.reader["tokenizer_json_sha256"])), cfg, R)
raw = json.dumps(res, indent=1, sort_keys=True).encode("utf-8")      # main()'s own serialization, written with newline="\n"
assert raw == held, "the summary recomputed in-process is not the summary of record, byte for byte"
SUMMARY = hashlib.sha256(held).hexdigest()
assert res["sources"] == {k: v for k, v in PINS_0075.items()}, "the summary's sources are not 0075's pins"
assert set(res) == set(fr.SUMMARY_FIELDS), "the summary's fields are not the module's list"
TR = {x["task_id"]: x for x in res["trajectories"]}
# when the summary of record was written: the summarizer's own output log, one start and one end of the module's
# command with rc 0, and the line keeping this summary by its sha256 and size
if SUMMARIZER_OUT_SHA256 == "FILL":
    assert a.preview, "the summarizer's output log is not pinned in this script"
    preview_note("the summarizer's output log is not pinned in this script")
else:
    assert sha256_file_bytes(a.summarizer_out) == SUMMARIZER_OUT_SHA256, "--summarizer-out is not the pinned output log"
so_lines = a.summarizer_out.read_text(encoding="utf-8").splitlines()
so_start = [ln.split()[0] for ln in so_lines if re.fullmatch(r"\S+ module command start", ln)]
so_end = [ln.split()[0] for ln in so_lines if re.fullmatch(r"\S+ module command end: rc=0", ln)]
assert len(so_start) == 1 and len(so_end) == 1 and so_lines[-1] == "exit 0", \
    "the summarizer's output log does not hold one start and one end of the module's command, rc 0"
so_kept = [ln for ln in so_lines if re.fullmatch(rf"\S+ kept .+ sha256 {SUMMARY} \({len(held)} bytes\)", ln)]
assert len(so_kept) == 1, "the summarizer's output log does not record keeping this summary"
SO_START, SO_END = utc(so_start[0]), utc(so_end[0])
assert SO_START < SO_END

# --- the wrapper's launch records ------------------------------------------------------------------------------------------------
recs_on_disk = sorted(p.name for p in a.records.glob("row*-*.json"))
if not RECORDS:
    assert a.preview, "the launch records are not pinned in this script"
    preview_note("the launch records are not pinned in this script")
else:
    assert recs_on_disk == sorted(RECORDS), "the records folder does not hold exactly the pinned launch records"
    for name, sha in RECORDS.items():
        assert sha256_file_bytes(a.records / name) == sha, f"{name} is not the pinned launch record"
REC = {}
for name in recs_on_disk:
    m = re.fullmatch(r"(row\d{2})-(\d+)\.json", name)
    assert m, f"unexpected record name {name}"
    d = json.loads((a.records / name).read_text(encoding="utf-8"))
    assert (d["task_id"], d["launch"]) == (m.group(1), int(m.group(2))), f"{name} names another launch"
    assert d["model"] == PINNED_MODEL, f"{name} launched another model"
    assert d.get("config_sha256", PINS_0075["config/fab-reuse.toml"]) == PINS_0075["config/fab-reuse.toml"], f"{name}: another config"
    REC[(d["task_id"], d["launch"])] = d
ids = [cfg.task_id_format.format(row=r) for r in range(1, cfg.cohort + 1)]
LAUNCHES = {t: sorted(k for (tt, k) in REC if tt == t) for t in ids}
for t, ks in LAUNCHES.items():
    assert ks == list(range(1, len(ks) + 1)), f"{t}: launches {ks} do not run 1, 2, ..."
with_traj = sorted(t for (t, _), d in REC.items() if d["trajectory"])
failed = sorted(f"{t}-{k}" for (t, k), d in REC.items() if not d["trajectory"])
assert with_traj == sorted(TR), f"the records' trajectories {with_traj} are not the summary's {sorted(TR)}"
assert sorted(res["not_run"]) == sorted(t for t in ids if not LAUNCHES[t]), "a question with no launch is not the summary's NOT RUN"
assert len(failed) == sum(res["failed_launches"].values()), "the records' failed launches are not the summary's"
assert len(with_traj) == len(set(with_traj)), "a question has two trajectories"
# every log file the summary hashed carries the sha256 the wrapper recorded when its question ended
n_checked = 0
for t, row in TR.items():
    (k,) = [k for k in LAUNCHES[t] if REC[(t, k)]["trajectory"]]
    man = REC[(t, k)]["files"]
    for rel, sha in row["files"].items():
        assert man.get(f"logs/{rel}") == sha, f"{t}: {rel} differs from the wrapper's manifest"
        n_checked += 1
# what ended each launch: its own exit, or a wrapper limit
STOPS = {}
for (t, k), d in REC.items():
    s = d.get("stop")
    if s is None:                                # the smoke's record, written by the wrapper's first version
        assert (t, k) == ("row01", 1) and d["exit"] == 0 and TR[t]["final_record"], f"{t}-{k} has no stop"
        s = "exit"
    assert s in ("exit", "wall time", "token ceiling"), f"{t}-{k}: unknown stop {s!r}"
    STOPS[(t, k)] = s
LIMITED = sorted((t, k, s) for (t, k), s in STOPS.items() if s != "exit")
for t, k, s in LIMITED:
    assert not TR[t]["final_record"] and TR[t]["stop_reason"] == "absent", f"{t}: ended at the {s} but has a final record"
for (t, k), s in STOPS.items():
    if s == "exit" and REC[(t, k)]["trajectory"]:
        assert TR[t]["final_record"], f"{t} exited by itself without a final record"
FIRST = {t: utc(REC[(t, 1)]["start"]) for t in ids if LAUNCHES[t]}
assert not any(T75_FIRST <= s <= T75_LAST for s in FIRST.values()), "a start falls inside 0075's commit set"
BEFORE = [r for r in RUN["order"] if ids[r - 1] in FIRST and FIRST[ids[r - 1]] < T75]
AFTER = [r for r in RUN["order"] if ids[r - 1] in FIRST and FIRST[ids[r - 1]] > T75]
START_ORDER = sorted(FIRST, key=lambda t: (FIRST[t], RUN["order"].index(int(t[3:]))))
assert [int(t[3:]) for t in START_ORDER] == [r for r in RUN["order"] if ids[r - 1] in FIRST], "the starts are not in the registered order"
LAST_START = max(FIRST.values())
assert LAST_START <= utc(RUN["last_start_utc"]), "a question started after the last start time"
ENDS = {t: utc(REC[(t, max(LAUNCHES[t]))]["end"]) for t in FIRST}

# --- the run's output logs: the stops of new starts, the restarts, the limit -------------------------------------------------------
if not WRAPPER_OUT:
    assert a.preview, "the output logs are not pinned in this script"
    preview_note("the output logs are not pinned in this script")
else:
    assert [p.name for p in a.wrapper_out] == list(WRAPPER_OUT), "--wrapper-out does not name the pinned logs in run order"
    for p in a.wrapper_out:
        assert sha256_file_bytes(p) == WRAPPER_OUT[p.name], f"{p.name} is not the pinned output log"
SESSIONS, DRY = [], []
for p in a.wrapper_out:
    lines = p.read_text(encoding="utf-8").splitlines()
    head = [ln for ln in lines if re.match(r"run (start|restart) ", ln)]
    starts = [ln for ln in lines if re.match(r"start \S+Z: ", ln)]
    ends = [ln for ln in lines if re.match(r"end \S+Z: ", ln)]
    assert len(starts) == 1 and len(ends) == 1, f"{p.name}: not one wrapper start and one end"
    if any(ln.startswith("dry-run ") for ln in lines):
        assert not head and not any(re.search(r" launch \d+ started", ln) for ln in lines), f"{p.name}: a dry run that launched"
        (dr,) = [ln for ln in lines if ln.startswith("dry-run ")]
        DRY.append((utc(starts[0].split()[1].rstrip(":")), re.match(r"dry-run (row\d{2}):", dr).group(1),
                    re.match(r"start \S+Z: (\d+) rows in order", starts[0]).group(1)))
        continue
    assert len(head) == 1, f"{p.name}: not one run line"
    hm = re.fullmatch(r"run (start|restart) (\S+Z)(?: \((.*)\))?", head[0])
    lim = re.search(r"limit (\d+) -> (\d+)", hm.group(3) or "")
    kept = re.search(r"limit (\d+)\)?$", hm.group(3) or "")
    sm = re.fullmatch(r"start (\S+Z): (\d+) rows in order, at most (\d+) at once, last start (\S+Z)", starts[0])
    assert sm and int(sm.group(2)) == cfg.cohort and int(sm.group(3)) == RUN["max_parallel"] and sm.group(4) == RUN["last_start_utc"], \
        f"{p.name}: the wrapper did not start on the full order with the registered limits"
    em = re.fullmatch(r"end (\S+Z): (.*)", ends[0])
    stop = [re.fullmatch(r"STOP (\S+Z): (.*)", ln) for ln in lines if ln.startswith("STOP ")]
    assert len(stop) <= 1, f"{p.name}: more than one STOP"
    launched = [re.match(r"(\S+Z) (row\d{2}) launch (\d+) started", ln) for ln in lines if re.search(r" launch \d+ started", ln)]
    SESSIONS.append({"name": p.name, "kind": hm.group(1), "at": utc(hm.group(2)), "start": utc(sm.group(1)),
                     "raise": (int(lim.group(1)), int(lim.group(2))) if lim else None,
                     "kept": int(kept.group(1)) if (kept and not lim) else None,
                     "stop": (utc(stop[0].group(1)), stop[0].group(2)) if stop else None,
                     "end": (utc(em.group(1)), em.group(2)),
                     "launched": [(m.group(2), int(m.group(3))) for m in launched]})
assert SESSIONS and SESSIONS[0]["kind"] == "start" and all(s["kind"] == "restart" for s in SESSIONS[1:])
for prev, cur in zip(SESSIONS, SESSIONS[1:]):
    assert prev["stop"] is not None and prev["end"][0] <= cur["at"], f"{cur['name']} restarted before {prev['name']} had ended"
    assert cur["raise"] or cur["kept"] is not None, f"{cur['name']}: the restart line names no limit"
lims = [s["raise"] for s in SESSIONS[1:] if s["raise"]]
for s1, s2 in zip(SESSIONS[1:], SESSIONS[2:]):           # the chain: each restart's old limit is the one in force
    before = s2["raise"][0] if s2["raise"] else s2["kept"]
    after = s1["raise"][1] if s1["raise"] else s1["kept"]
    assert before == after, f"{s2['name']}: the limit it names is not the one {s1['name']} ran under"
assert all(new > old for old, new in lims), "a restart lowered the spend limit"
RAISES = [s for s in SESSIONS[1:] if s["raise"]]
KEPT = [s for s in SESSIONS[1:] if not s["raise"]]
launched_all = [x for s in SESSIONS for x in s["launched"]]
assert sorted(launched_all) == sorted(k for k in REC if k[0] != "row01"), \
    "the output logs' launches are not the records' (the smoke excepted)"
FINAL = SESSIONS[-1]
assert (FINAL["stop"] is None) == (FINAL["end"][1] == "every row in the order started"), "the last session's end is not read"
assert FINAL["stop"] is None or FINAL["end"][1] == "stopped: " + FINAL["stop"][1]
SPEND = "the spend estimate would pass the cap with nothing running"
DISK = re.compile(r"free disk [\d.]+ GB under the (\d+) GB floor")
for prev, cur in zip(SESSIONS, SESSIONS[1:]):           # a raise follows a failed spend check; a kept limit, the disk floor
    assert prev["stop"][1].startswith(SPEND) if cur["raise"] else DISK.fullmatch(prev["stop"][1]), \
        f"{cur['name']}: the limit's change does not match the stop before it"


def stop_text(s: str) -> str:
    if s.startswith(SPEND):
        return "the spend check failed with nothing running"
    m = DISK.fullmatch(s)
    if m:
        assert int(m.group(1)) == RUN["disk_floor_gb"]
        return f"free disk on the run's drive fell under the {RUN['disk_floor_gb']} GB floor"
    if s.startswith("past the last start"):
        return f"the last start time ({RUN['last_start_utc']}) passed"
    raise AssertionError(f"a stop this script does not read: {s[:80]!r}")


# --- the local change: its diff, the contact elided; every other file byte-identical -------------------------------------
assert sha256_file_bytes(a.tarball) == cfg.harness["tarball_sha256"], "the tarball is not the pinned one"
assert sha256_file_bytes(a.questions) == cfg.harness["questions_csv_sha256"]
assert a.questions.resolve() == (a.harness / "data" / "public.csv").resolve(), "--questions is not the run's harness public.csv"
n_same = 0
with tarfile.open(a.tarball, "r:gz") as tf:
    members = [m for m in tf.getmembers() if m.isfile()]
    assert members and all(m.name.startswith(TARBALL_MEMBER) for m in members)
    for m in members:
        rel = m.name[len(TARBALL_MEMBER):]
        body = tf.extractfile(m).read()
        local = (a.harness / rel).read_bytes()
        if rel == TOOLS:
            assert hashlib.sha256(body).hexdigest() == TOOLS_BEFORE and hashlib.sha256(local).hexdigest() == TOOLS_AFTER
            before_t, after_t = body.decode("utf-8"), local.decode("utf-8")
        else:
            assert local == body, f"{rel} differs from the tarball's"
            n_same += 1
DIFF = list(difflib.unified_diff(before_t.splitlines(), after_t.splitlines(), lineterm="", n=3))[2:]
DIFF = [EMAIL.sub("<contact elided>", ln) for ln in DIFF]
assert DIFF and not any(EMAIL.search(ln) for ln in DIFF), "a contact survives the elision"
assert sum(ln.count("<contact elided>") for ln in DIFF) == 1 and any("FAB_CONTACT" in ln for ln in DIFF)
assert not any(ln.startswith("```") for ln in DIFF)

# --- the drafts README stages this script -------------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if not (f"`append_{NUM}.py`" in readme and free and free[-1] == NEXT):
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    preview_note(f"the drafts README does not stage append_{NUM}.py at {NEXT}")


# --- the entry's text, every figure from `res` ---------------------------------------------------------------------------------
def z(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def f4(x) -> str:
    return "null" if x is None else f"{x:.4f}"


def n(x) -> str:
    return "null" if x is None else f"{x:,}"


def sm(d, fmt=f4) -> str:
    return "null" if d is None else f"{fmt(d['median'])} (p10 {fmt(d['p10'])}, p90 {fmt(d['p90'])}; n = {d['n']})"


def rows(rs) -> str:
    rs = list(rs)
    return "none" if not rs else ", ".join(str(r) for r in rs)


def tids(ts) -> str:
    ts = list(ts)
    return "none" if not ts else ", ".join(f"`{t}`" for t in ts)


def aggregate_lines(g: dict, over: str) -> list:
    p, pt = g["pooled"], g["per_trajectory"]
    ins, mc, gap = g["input_share"], g["main_loop_caching"], g["reuse_gap"]
    out = [f"*{over}.*"]
    if p is None:
        out.append("- No measured trajectory: every reuse figure is null.")
    else:
        out += [
            f"- **Pooled** over the measured trajectories: {n(p['document_tokens'])} document tokens in "
            f"{n(p['prompt_tokens'])} prompt tokens; SAME OFFSET {n(p['same_offset'])}, DIFFERENT OFFSET "
            f"{n(p['different_offset'])}, NEW {n(p['new'])}; `reused_fraction` {f4(p['reused_fraction'])} "
            f"(`same_offset_fraction` {f4(p['same_offset_fraction'])}, `different_offset_fraction` "
            f"{f4(p['different_offset_fraction'])}), `new_fraction` {f4(p['new_fraction'])}; `prefix_shared_fraction` "
            f"{f4(p['prefix_shared_fraction'])} ({n(p['prefix_shared'])} of the prompt tokens); within the cap, "
            f"`capped_prompt_share` {f4(p['capped_prompt_share'])} ({n(p['reused_in_capped_prompts'])}), "
            f"`capped_pair_share` {f4(p['capped_pair_share'])} ({n(p['reused_in_capped_pairs'])}).",
            f"- **Per trajectory**, median (p10, p90): `reused_fraction` {sm(pt['reused_fraction'])}; "
            f"`same_offset_fraction` {sm(pt['same_offset_fraction'])}; `different_offset_fraction` "
            f"{sm(pt['different_offset_fraction'])}; `new_fraction` {sm(pt['new_fraction'])}; sub-calls "
            f"{sm(pt['subcalls'], lambda v: f'{v:g}')}."]
    if ins is None:
        out.append("- Input share and main-loop caching: null (no trajectory's usage could be read).")
    else:
        out += [
            f"- **Input share**: over {ins['trajectories']} trajectories, helper "
            f"{n(ins['helper_input_tokens'])} and main {n(ins['main_input_tokens'])} input tokens, pooled "
            f"{f4(ins['pooled'])}; per trajectory {sm(ins['per_trajectory'])}; compaction input tokens "
            f"{n(ins['compaction_input_tokens'])}, unknown for {tids(ins['compaction_unknown'])}.",
            f"- **Main-loop caching**: {n(mc['main_cache_read_tokens'])} "
            f"cache-read of {n(mc['main_input_tokens'])} input tokens, pooled {f4(mc['pooled'])}; per trajectory "
            f"{sm(mc['per_trajectory'])}."]
    if gap["gaps"]:
        ks = sorted(gap["share_within"], key=int)          # the bounds are the summary's own keys, checked against the config
        assert [int(k) for k in ks] == sorted(cfg.timing["cache_lifetimes_seconds"]), "the summary's gap bounds are not the config's"
        sw = ", ".join(f"{gap['share_within'][k]:.4f} within {int(k):,} s" for k in ks)
        out.append(f"- **Reuse gap**: {n(gap['gaps'])} gaps over "
                   f"{gap['trajectories']} timed trajectories, seconds {sm(gap['seconds'], lambda v: f'{v:.1f}')}; "
                   f"{sw}; untimed {tids(gap['untimed'])}.")
    else:
        out.append(f"- **Reuse gap**: no gap (`gaps` 0); untimed {tids(gap['untimed'])}.")
    return out


for k, v in fr.LABELS.items():          # the entry quotes these labels verbatim, as the summary carries them
    assert k in ("input_share", "main_loop_caching", "reuse_gap", "by_question_type") and v == res["labels"][k]
assert res["label"] == fr.LABEL

t01 = "row01"
SM = REC[(t01, 1)]
ORDER_AFTER = [r for r in RUN["order"] if r != 1 and ids[r - 1] in FIRST]
traj_lines = []
for t in ids:
    if t not in TR:
        traj_lines.append(f"- `{t}` NOT RUN.")
        continue
    x = TR[t]
    end = "ended by itself" if x["ended_by_itself"] else f"did not end by itself (`stop_reason` {x['stop_reason']})"
    base = (f"- `{t}` ({x['question_type']}; {end}; {x['turns']} turns, {x['subcalls']} sub-calls"
            + (f", turn {x['set_aside_turn']} set aside with {x['cut_subcalls']} logged sub-calls" if x["set_aside_turn"] is not None else "")
            + ")")
    if x["measurable"]:
        traj_lines.append(f"{base}: {n(x['document_tokens'])} document tokens, `reused_fraction` {f4(x['reused_fraction'])} "
                          f"(same {f4(x['same_offset_fraction'])}, different {f4(x['different_offset_fraction'])}), "
                          f"`prefix_shared_fraction` {f4(x['prefix_shared_fraction'])}, {x['documents']} document{'' if x['documents'] == 1 else 's'}; "
                          f"input share {f4(x['input_share_helper'])}, main-loop cache read {f4(x['main_cache_read_fraction'])}.")
    else:
        traj_lines.append(f"{base}: NOT MEASURABLE ({x['reason']}); input share {f4(x['input_share_helper'])}, "
                          f"main-loop cache read {f4(x['main_cache_read_fraction'])}.")

stops_par = [f"{z(s['stop'][0])}, {stop_text(s['stop'][1])}" for s in SESSIONS[:-1]]
restarts = [f"{z(s['at'])}" + (" with the limit raised" if s["raise"] else " with the limit unchanged") for s in SESSIONS[1:]]
final_end = FINAL["end"]
assert SO_START > final_end[0], "the summarizer's command started before the run's end"
final_text = ("every question in the order had started and the last had ended" if FINAL["stop"] is None
              else f"new starts stopped at {z(FINAL['stop'][0])}, {stop_text(FINAL['stop'][1])}, and the wrapper exited once "
                   "the questions in flight had ended")
disk_text = (" The restart after the disk-floor stop kept the limit; it was made once space had been freed on the run's drive."
             " 0075 gives no rule for a restart after a disk-floor stop: it says only that such a failed check stops new"
             f" starts at once (line {L75['otherstop']})." if KEPT else "")


def cut_text(t: str) -> str:
    """From the summary alone: 0075 sets the cut turn aside and reads none of its records."""
    x = TR[t]
    if x["set_aside_turn"] is None:
        return "no turn set aside"
    if x["cut_subcalls"] == 0:
        return f"its last turn (turn {x['set_aside_turn']}) set aside, which holds no logged sub-call"
    return f"its last turn (turn {x['set_aside_turn']}) set aside and its {x['cut_subcalls']} sub-calls not read"


limited_text = "; ".join(f"`{t}` at its {s}, at {z(utc(REC[(t, k)]['end']))}, with no final record, {cut_text(t)}"
                         for t, k, s in LIMITED) or "none"
counts = ", ".join(f"{k} {v}" for k, v in res["not_measurable"].items())
bytype = "; ".join(f"{qt}: {tids(v['run'])}" + (f", NOT RUN {tids(v['not_run'])}" if v["not_run"] else "")
                   for qt, v in res["by_question_type"].items())
nob = res["not_ended_by_itself"]
assert len(DRY) == 1 and DRY[0][2] == "1", "the text states one dry run given one row"
dry_text = "; ".join(f"at {z(t)}, {r} alone, with the wrapper's dry-run flag, which runs its checks and starts nothing"
                     for t, r, rows_n in DRY)
assert res["reader"]["tokenizers_version"]

RAW = f"""### {NUM} — {a.date} — FAB v2 document-reuse opportunity ran `[BASELINE, DESCRIPTIVE]`: the document tokens a logged helper sub-call of a Finance Agent Benchmark v2 trajectory carries that an earlier sub-call of the same trajectory already carried, over {res['run']} of {cfg.cohort} questions, one run each; an upper bound, not a realized saving; no band, no cell moves

**Setup, as registered (0075).** `vals-ai/finance-agent-v2` at `{cfg.harness['commit'][:12]}`, from the pinned tarball (`{cfg.harness['tarball_sha256'][:12]}…`), run locally in single-task mode, one question per process, serving model `{cfg.harness['model']}` at the registry's default effort; at most {RUN['max_parallel']} questions at once, the wrapper ending a question at {RUN['wall_seconds']:,} s of wall time or {RUN['token_ceiling']:,} input tokens, last start {RUN['last_start_utc']}. Config `{PINS_0075['config/fab-reuse.toml'][:12]}…`, `fab_reuse.py` `{PINS_0075['src/linear_ceiling/fab_reuse.py'][:12]}…` and `test_fab_reuse.py` `{PINS_0075['tests/test_fab_reuse.py'][:12]}…` as 0075 pins them (line {L75['pins']}), committed in `{FILES_COMMIT[:7]}`, the first commit of 0075's set, and unchanged since; the summary's `sources` are these three hashes. Reader `{cfg.reader['model']}@{cfg.reader['revision'][:12]}`, `tokenizer.json` `{cfg.reader['tokenizer_json_sha256'][:12]}…`, tokenizers {res['reader']['tokenizers_version']}. The summary, `results/fab-reuse/summary.json` (`{SUMMARY[:12]}…`), was written once by the module's command after its gate passed, from {z(SO_START)} to {z(SO_END)} with rc 0, after the run's end; it is not committed (nothing under `results/fab-reuse/` is tracked). This entry's script ran the gate again, recomputed the summary in-process with the committed module, and refuses unless it is that file byte for byte. As 0075 asks (line {L75['own']}), the summarizer's figures enter by this entry: each one under **Figures** below is read from that recomputation, and none is typed; the times of the run's events are read from the wrapper's launch records and output logs, which the script also pins by sha256. Each of the {n_checked:,} log files the summary read has the sha256 the wrapper's manifest recorded when its question ended.

**The run.** Row 1's smoke, its one run, started {SM['start']} and ended {SM['end']}, before the token ceiling and the number of questions run at once were set (line {L75['smoke']}). The other {len(FIRST) - 1} questions started in the registered order ({', '.join(str(r) for r in ORDER_AFTER)}) from {z(min(FIRST[t] for t in FIRST if t != t01))} to {z(LAST_START)}; the last ended {z(max(ENDS.values()))}. As 0075 asks (line {L75['before']}): {len(BEFORE)} questions had started before its commit (`{COMMIT_0075[:7]}`, {z(T75)}), rows {rows(BEFORE)}; the other {len(AFTER)} started after the last commit of its set ({z(T75_LAST)}), and no start falls between that set's first and last commit. Questions run: {res['run']} of {cfg.cohort}; NOT RUN: {tids(res['not_run'])}. Launches by question (line {L75['launches']}): {"; ".join(sorted({f"{len(v)} for {sum(1 for w in LAUNCHES.values() if len(w) == len(v))} questions" for v in LAUNCHES.values() if v}))}, {sum(len(v) for v in LAUNCHES.values())} in all; failed launches: {tids(failed)}. Ended by a wrapper limit: {limited_text}; every other question ended with its own final record.

**Stops and restarts (line {L75['stops']}).** New starts stopped {len(stops_par)} times before the run's end: {"; ".join(stops_par)}. After each, the questions in flight, if any, ran to their own end, and once nothing ran the wrapper was started again with the same config pin, model and arguments, the spend limit aside: {"; ".join(restarts)}. As 0075 asks (line {L75['limit']}), the spend limit was raised {len(RAISES)} times, at each restart after a failed spend check and never lowered, before the last start time; its amount is not stated.{disk_text} The run's last session ended at {z(final_end[0])}: {final_text}. As 0075 asks (line {L75['used']}): no question was started from a part of the order and no stop by hand was used; a part of the order was given once, {dry_text}, to read the spend check before a restart.

**The local change (line {L75['ua']}).** The page fetcher's User-Agent header, which at the commit carries another party's contact, takes the run's own contact from the environment. The diff of `{TOOLS}`, tarball (`{TOOLS_BEFORE[:12]}…`) to run (`{TOOLS_AFTER[:12]}…`), the hard-coded contact elided; the other {n_same} files of the tarball are byte-identical in the run's harness folder:

```diff
{chr(10).join(DIFF)}
```

**Figures (`fab_reuse.summarize` in-process).** Every reuse figure below carries 0075's label (line {L75['label']}), verbatim: "{res['label']}". The input share, the main-loop caching and the reuse gap carry their own labels (`labels` in the summary), verbatim: input share "{res['labels']['input_share']}"; main-loop caching "{res['labels']['main_loop_caching']}"; reuse gap "{res['labels']['reuse_gap']}". None is compared with the reuse counts. Measured {res['measured']} of {res['run']}; NOT MEASURABLE by reason: {counts}. `not_ended_by_itself`: {"; ".join(f"`{x['task_id']}` ({x['stop_reason']})" for x in nob) or "none"}. By question type (`by_question_type`, listed, not compared): {bytype}.

{chr(10).join(aggregate_lines(res, f"All {res['run']} trajectories ({res['measured']} measured)"))}

{chr(10).join(aggregate_lines(res['aggregates_ended_by_itself'], f"The {res['aggregates_ended_by_itself']['trajectories']} trajectories that ended by themselves ({res['aggregates_ended_by_itself']['measured']} measured; `aggregates_ended_by_itself`)"))}

*Each trajectory* (`trajectories`; fractions of its document tokens, prefix-shared of its prompt tokens):
{chr(10).join(traj_lines)}

**Reading (descriptive; no band, no threshold).** These are counts in one trajectory's own logged helper sub-calls, in the reader's tokenizer: of the document tokens those sub-calls carried, the share an earlier sub-call of the same trajectory had already carried. It bounds from above what a cache keyed on the retrieved document's sha256 could have reused; the harness sent every sub-call with prompt caching off, so none of it was a realized saving, and a cache keyed on content could reuse more. PREFIX-SHARED is beside it and not bounded by it. The input share and the main-loop caching are in the provider's tokenizer and the reuse gap in seconds; they describe where the input went and the estimated time between carryings, not what a cache would have served. No carryover effect, key statistic or KL is read, and the benchmark's grading is its owner's: this run carries no score.

**What this does NOT touch.** Every cell and verdict, every other config and output tree, the figure set 0072 lists, and entry 0076, whose reading of these trajectories enters by its own entry.

**Scope.** One harness at one commit, one serving model, {cfg.cohort} questions, one run each, {res['run']} run; the document text of one agent's logged helper sub-calls; an upper bound on one cache's opportunity, not a saving.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard 0075 present, {PREV} last, {NUM} absent. Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""
NB = "\u0000"


def wrap(par: str) -> str:
    """One paragraph at width 120; a code span is never broken across lines. List items and the diff are not wrapped."""
    par = re.sub(r"`[^`]*`", lambda m: m.group(0).replace(" ", NB), " ".join(par.split()))
    return "\n".join(ln.replace(NB, " ") for ln in textwrap.wrap(par, width=120, break_long_words=False, break_on_hyphens=False))


assert NB not in RAW, "the entry text holds the wrap's placeholder"
_paras = RAW.split("\n\n")
assert _paras[0].startswith(f"### {NUM} ") and "\n" not in _paras[0] and _paras[-1] == "prior-entries-sha256: PLACEHOLDER\n"
_out = [_paras[0]]
for _p in _paras[1:-1]:
    _out.append(_p if (_p.startswith("```") or _p.startswith("*") and "\n- " in _p) else wrap(_p))
_out.append(_paras[-1])
ENTRY = "\n\n".join(_out)
assert ENTRY.endswith("prior-entries-sha256: PLACEHOLDER\n") and ENTRY.count("PLACEHOLDER") == 1, "the chain line is not the entry's last"
assert not EMAIL.search(ENTRY), "an address in the entry"
for _bad in ("usd", "$", "spend so far", "cap-usd", "C:/", "C:\\", "/c/Users", "hossa"):
    assert _bad not in ENTRY, f"the entry holds {_bad!r}"
assert "FILL" not in ENTRY and "UNVERIFIED" not in ENTRY

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print("[ordering guard: ok]")
    raise SystemExit(0)


# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included -----------------------------------
def ledger_check():
    code = (f"import sys; sys.path.insert(0, {str(R / 'src')!r}); "
            "from linear_ceiling.ledger_check import main; sys.exit(main())")
    return subprocess.run([sys.executable, "-I", "-c", code], cwd=R, capture_output=True, text=True, env=ENV)


at_head = git("show", "HEAD:ledger/ledger.md")
assert text == at_head.decode("utf-8").replace("\r\n", "\n"), "ledger/ledger.md is not HEAD's: an uncommitted edit"
assert git("status", "--porcelain", "--", "ledger/ledger.md").strip() == b"", "ledger/ledger.md is modified in the working tree"
r0 = ledger_check()
assert r0.returncode == 0 and r0.stdout.strip().endswith(LEDGER_OK), f"ledger_check before the write: {(r0.stdout + r0.stderr).strip()[-400:]}"
assert "prior-entries-sha256: PLACEHOLDER" not in text, "the ledger already holds a placeholder chain line"
base = text + ("" if text.endswith("\n") else "\n") + "\n"
digest = chain_hash(base + ENTRY, len(base), _ENTRIES_HEAD.search(base).start())
new = base + ENTRY.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
assert new.startswith(text) and new.count(f"\n### {NUM} ") == 1 and new.index(f"\n### {NUM} ") + 1 == len(base), "the new ledger is not the old one plus this entry"
# --- the write, and after it: ledger_check, else the old bytes go back ----------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
