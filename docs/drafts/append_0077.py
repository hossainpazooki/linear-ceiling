"""DRAFT append script for linear-ceiling: AMEND entry 0076, before any pair is built, in two settings of its config:
its window end (`config/cache-behavior-fab.toml`'s `window_end`), from 2026-11-20T12:00:00Z to 2026-11-20T06:30:00Z,
set after the run 0075 registers had ended, and the cell's gate, which now names this entry too. DESCRIPTIVE: no hypothesis row, no
band, no `verdict:` line, no cell moves. The number is the ledger's next, 0077 after 0076, PROVISIONAL until the
drafts README stages this script.

Every line number and hash in the entry is computed here, read-only: 0076's sentences that this entry reads with the
new value, located by search; the two changed files, tracked, unmodified and hashed newline-normalized, with their git
blob ids; the cell's section of docs/agent/experiment-commands.md, likewise; and the files 0076 pins that this entry
leaves as they are, which must still be the blobs 0076 pins.

    python -I docs/drafts/append_0077.py --repo-root . --date YYYY-MM-DD --runs-root D [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root is required. It must be the current
directory and the top of its git work tree, and the imported `linear_ceiling` and `tools` must be that tree's. The
script refuses under -O. Outside `--preview` it refuses until the config and the test file are committed as-is, the
config differs from the one 0076 pins in `window_end` and the gate only, and in exactly those values, the other files
0076 pins are its blobs, the test file is 0076's but for the two tests the entry names (every other line compared,
decorators and comments included), docs/agent/experiment-commands.md is 0076's but for the three lines the entry
names, nothing exists under `results/cache-behavior-fab/` and the drafts README stages this script with the next
number. --runs-root (the run's folder, outside the repository; required outside --preview) checks the launch records'
bytes against the digest the entry states, recomputes the launch facts it states from the records' names and their
`end` and `trajectory` fields alone, and runs the cell's own `window` under the old time, the new one and the last
`end`; the script refuses on a difference. Before the write, the ledger must equal HEAD's, be unmodified and pass `ledger_check`. After the write
`ledger_check` runs again, and on a failure the old bytes go back. The script writes only ledger/ledger.md.
"""
import argparse
import ast
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap
import tomllib
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
ap.add_argument("--preview", action="store_true")
ap.add_argument("--runs-root", type=Path, help="the run's folder: recompute the launch facts from its launch records")
a = ap.parse_args()
assert a.preview or a.runs_root is not None, "--runs-root is required: the entry's launch facts are recomputed from the launch records"
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True, env=ENV)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
sys.path.insert(0, str(R / "src"))
sys.path.insert(0, str(R))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling.fab_reuse import load_config                          # noqa: E402
from linear_ceiling.hashing import sha256_text_file                       # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
from tools.cache_behavior import fab_pairs as FP                         # noqa: E402
assert Path(_lc.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_lc.__file__}, not the tree's"
assert Path(FP.__file__).resolve().is_relative_to(R), f"imported {FP.__file__}, not the tree's"

LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
CONFIG, TESTS = "config/cache-behavior-fab.toml", "tests/test_cache_behavior_fab.py"
CHANGED = (CONFIG, TESTS)
DOCS = "docs/agent/experiment-commands.md"       # pinned here: 0076's text but for the three lines below
DOCS_SUBS = (  # (0076's text, this entry's, occurrences): the cell's heading, and the --prepare and --check comments
    ("## FAB v2 paired sub-call cache reading (registered 0076; GPU; descriptive)",
     "## FAB v2 paired sub-call cache reading (registered 0076, window end amended by 0077; GPU; descriptive)", 1),
    ("# 0075 and 0076 on the ledger", "# 0075, 0076 and 0077 on the ledger", 2))
# The only tests that change: the registered config's, and the gate's (renamed for the entry it now also requires).
TESTS_0076 = ("test_the_registered_config", "test_prepare_refuses_until_the_ledger_holds_0076")
TESTS_NOW = ("test_the_registered_config", "test_prepare_refuses_until_the_ledger_holds_0076_and_0077")
# The files 0076 pins (or reads) that this entry leaves as they are: each must be the blob it was at 0076's commit.
UNCHANGED = ("tools/cache_behavior/fab_pairs.py", "tools/cache_behavior/run.py", "tools/cache_behavior/core.py",
             "src/linear_ceiling/fab_reuse.py", "config/fab-reuse.toml", "config/cache-behavior.toml")
# 0076's pins of the two files this entry changes (0076, "Pinned at append").
PINNED_0076 = {CONFIG: ("90d23e40587d4d1248e28ac20927e4f234e2a772",
                        "78560c47b3891dca08b6866711a1bdbbdd18516a90dd367b853e97b0c30edc9c"),
               TESTS: ("f0f5844c85dcce78331e72b8e21ca55f80c25afd",
                       "edd79d597ca62825fa1c9f7ca22f2d2e137fef8f5a137623f92e536c582ba56e")}
OLD_WINDOW, NEW_WINDOW = "2026-11-20T12:00:00Z", "2026-11-20T06:30:00Z"
# The run's launch facts when the value was set; --runs-root recomputes them from the launch records.
RECORDS, LAST_END = 27, "2026-11-20T06:29:49Z"
# sha256 of the 27 launch records' bytes (`runs/<task id>-1.json`), concatenated in row order: binds the facts to the run.
RECORDS_SHA256 = "6f791514aca1db3d80bd3cf76665608a89aa4607b3f817290860433a00f54e63"
CITED = {  # key: (entry, the sentence quoted or pointed at, which must occur exactly once in that entry)
    "gate_build": ("0076", "the build refuses until the committed ledger holds 0075 and 0076"),
    "gate_prepare": ("0076", "It refuses before the window ends, until the committed ledger holds 0075 and 0076"),
    "gate_driver": ("0076", "The driver refuses until the committed ledger holds 0075 and 0076"),
    "gate_reads": ("0076", "The driver reads no pair until the committed ledger holds 0076."),
    "seen": ("0076", "Every rule here was fixed before any content of the run's logs was read: the window,"),
    "window": ("0076", "A question is read only if every one of its launches has ended, each with its launch record "
                       f"written and its `end` at or before {OLD_WINDOW}."),
    "ended": ("0076", "If the run has ended by then, the window holds the whole run."),
    "beside": ("0076", f"the window, questions that ended by {OLD_WINDOW};"),
    "built": ("0076", "The inputs are built after this entry's commit"),
    "pinned": ("0076", "Pinned at append:"),
}


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


def preview_note(msg: str) -> None:
    print(f"[preview] {msg}; the append refuses until it is", file=sys.stderr)


# --- this ledger: the ordering, the cited sentences ------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0076", f"the ledger's last entry is {PREV}, not 0076"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
L = {k: once(text, e, p) for k, (e, p) in CITED.items()}
_b76 = block(text, "0076")[1]
for rel, (blob, sha) in PINNED_0076.items():         # 0076's text pins the two files as this script states
    assert f"`{rel}` (blob `{blob[:12]}…`, sha256 `{sha[:12]}…`)" in " ".join(_b76.split()), f"0076 does not pin {rel} so"


# --- the files: the two changed ones, committed as-is; the rest as 0076's commit left them --------------------------------
def committed_as_is(rel: str) -> bool:
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=R, capture_output=True, env=ENV).returncode == 0
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=R, env=ENV).returncode == 0
    return tracked and clean


_landed = git("log", "--format=%H", "-S", "### 0076 —", "--", "ledger/ledger.md").decode().split()
assert _landed, "no commit adds 0076 to the ledger"
C0076 = _landed[-1]
_c76 = dt.datetime.fromisoformat(git("show", "-s", "--format=%cI", C0076).decode().strip())
assert _c76 < FP.parse_stamp(LAST_END), f"0076's commit ({_c76.isoformat()}) is not before the run's last end: the entry says 0076 set its window end before the run had ended"
for rel, (blob, sha) in PINNED_0076.items():
    assert git("rev-parse", f"{C0076}:{rel}").decode().strip() == blob, f"{rel} at 0076's commit is not blob {blob[:12]}"
BLOB = {}
for rel in (*CHANGED, DOCS, *UNCHANGED):
    assert (R / rel).is_file(), f"{rel} missing"
    if committed_as_is(rel):
        BLOB[rel] = git("rev-parse", f"HEAD:{rel}").decode().strip()
    else:
        assert a.preview, f"{rel} is not committed as-is"
        preview_note(f"{rel} is not committed as-is (its blob id below is the working file's)")
        BLOB[rel] = git("hash-object", f"--path={rel}", str(R / rel)).decode().strip()
H = {rel: sha256_text_file(R / rel) for rel in (*CHANGED, DOCS, *UNCHANGED)}
for rel in UNCHANGED:
    assert BLOB[rel] == git("rev-parse", f"{C0076}:{rel}").decode().strip(), f"{rel} is not the blob 0076's commit left"
for rel, (blob, sha) in PINNED_0076.items():
    assert BLOB[rel] != blob and H[rel] != sha, f"{rel} is unchanged from 0076's pin: nothing to amend"


def outside(src: str, skip) -> list:
    """Every line of the file, less the lines of the named top-level functions, each from its first decorator to its
    end; so decorators, comments and blank lines outside those functions are all compared."""
    tree = ast.parse(src)
    names = [getattr(n, "name", None) for n in tree.body]
    assert all(names.count(s) == 1 for s in skip), f"the test file lacks, or repeats, one of {skip}"
    drop = set()
    for n in tree.body:
        if getattr(n, "name", None) in skip:
            drop.update(range(min([n.lineno] + [d.lineno for d in n.decorator_list]), n.end_lineno + 1))
    return [ln for i, ln in enumerate(src.split("\n"), 1) if i not in drop]


assert outside(git("show", f"{C0076}:{TESTS}").decode("utf-8").replace("\r\n", "\n"), TESTS_0076) == \
       outside((R / TESTS).read_text(encoding="utf-8").replace("\r\n", "\n"), TESTS_NOW), \
    "the test file changes outside the registered config's test and the gate's"
_docs = git("show", f"{C0076}:{DOCS}").decode("utf-8").replace("\r\n", "\n")
for _was, _now, _n in DOCS_SUBS:
    assert _docs.count(_was) == _n, f"{DOCS} at 0076's commit holds {_docs.count(_was)} of {_was!r}"
    _docs = _docs.replace(_was, _now)
assert (R / DOCS).read_text(encoding="utf-8").replace("\r\n", "\n") == _docs, \
    f"{DOCS} is not 0076's text with the cell's heading and its --prepare and --check comments naming 0077, and nothing else"

# --- the config: 0076's, but for the window end and the gate ---------------------------------------------------------------
old = tomllib.loads(git("show", f"{C0076}:{CONFIG}").decode("utf-8"))
cfg = tomllib.loads((R / CONFIG).read_text(encoding="utf-8"))
assert old["window_end"] == OLD_WINDOW and cfg["window_end"] == NEW_WINDOW, "the window ends are not the ones stated"
assert old["gate"] == {"prepare_entries": ["0075", "0076"], "run_entries": ["0075", "0076"]}, f"0076's gate is {old['gate']}"
assert cfg["gate"] == {"prepare_entries": ["0075", "0076", NUM], "run_entries": ["0075", "0076", NUM]}, \
    f"the cell's gate is {cfg['gate']}, not 0075, 0076 and {NUM}"
def _rest(c: dict) -> str:        # by value and by type: 64 and 64.0, or 1 and true, are not the same here
    return json.dumps({k: v for k, v in c.items() if k not in ("window_end", "gate")}, sort_keys=True)


assert _rest(cfg) == _rest(old), "the config differs from 0076's in another value"
FLOOR, CEILING = cfg["min_matched_tokens"], cfg["max_pairs"]
assert (FLOOR, CEILING) == (64, 60)
fab = load_config(R / "config/fab-reuse.toml", R)
assert fab.cohort == RECORDS == 27
OUT = R / "results" / "cache-behavior-fab"
assert not (OUT.exists() and any(OUT.rglob("*"))), "results/cache-behavior-fab/ holds something: the entry comes before any reading"

# --- the launch facts, recomputed from the launch records (names, `end`, `trajectory`) -------------------------------------
if a.runs_root is not None:
    runs = a.runs_root / "runs"
    _rd = hashlib.sha256()
    for row in range(1, fab.cohort + 1):
        _rd.update((runs / f"{fab.task_id_format.format(row=row)}-1.json").read_bytes())
    assert _rd.hexdigest() == RECORDS_SHA256, f"the launch records' bytes have sha256 {_rd.hexdigest()}, not the run's {RECORDS_SHA256}"
    print(f"[runs root] the 27 launch records' bytes, in row order: sha256 {RECORDS_SHA256[:16]}..., as stated", file=sys.stderr)
    recs, outs, ends = {}, set(), []
    for p in runs.iterdir():
        m = re.fullmatch(r"(.+)-(\d+)\.(json|out)", p.name)
        assert m, f"an unexpected name in the run's launch folder: {p.name}"
        (recs.setdefault((m.group(1), int(m.group(2))), p) if m.group(3) == "json" else outs.add((m.group(1), int(m.group(2)))))
    tids = [fab.task_id_format.format(row=row) for row in range(1, fab.cohort + 1)]
    assert set(recs) == {(t, 1) for t in tids} and outs == set(recs), "not one launch per question, each with its record"
    for key, p in sorted(recs.items()):
        body = json.loads(p.read_bytes().decode("utf-8"))
        assert body["trajectory"] is True, f"{p.name}: no trajectory"
        ends.append(body["end"])
    assert len(ends) == RECORDS and max(ends) == LAST_END and all(FP.parse_stamp(e) <= FP.parse_stamp(NEW_WINDOW) for e in ends), \
        f"the launch records give {len(ends)} records, latest end {max(ends)}"
    print(f"[runs root] {len(ends)} launch records, one per question, each with its output file and a trajectory; "
          f"latest end {max(ends)}: as stated", file=sys.stderr)
    for stamp in (OLD_WINDOW, NEW_WINDOW, LAST_END):    # the cell's own rule: every question in the window, each time
        _st, _ = FP.window(a.runs_root, fab, FP.parse_stamp(stamp))
        _in = sorted(t for t, s in _st.items() if s == "in the window")
        assert _in == sorted(tids), f"the cell's window at {stamp} holds {len(_in)} of the {len(tids)} questions"
        print(f"[runs root] the cell's window at {stamp}: {len(_in)} of {len(tids)} questions in the window", file=sys.stderr)
else:
    print("[preview] the launch facts are not recomputed without --runs-root", file=sys.stderr)

# --- the drafts README stages this script ----------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if not (f"`append_{NUM}.py`" in readme and free and free[-1] == NEXT):
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    preview_note(f"the drafts README does not stage append_{NUM}.py at {NEXT}")


def h(rel: str) -> str:
    return f"`{rel}` (blob `{BLOB[rel][:12]}…`, sha256 `{H[rel][:12]}…`)"


def h0076(rel: str) -> str:
    blob, sha = PINNED_0076[rel]
    return f"blob `{blob[:12]}…`, sha256 `{sha[:12]}…`"


# --- the entry -------------------------------------------------------------------------------------------------------------
RAW = f"""### {NUM} — {a.date} — Window amendment to 0076, before any pair is built: two settings of its config change, the window end, now {NEW_WINDOW} instead of {OLD_WINDOW}, set after the run had ended, so the window holds the same whole run, and the cell's gate, which now names this entry too; nothing else in 0076 changes; descriptive, no cell moves

**What changes.** Two settings of 0076's config, `{CONFIG}`. Its `window_end`, from `{OLD_WINDOW}` to `{NEW_WINDOW}`: 0076's window rule (line {L['window']}) reads with the new time, so a question is read only if every one of its launches has ended, each with its launch record written and its `end` at or before {NEW_WINDOW}, and its comparison with 0049 (line {L['beside']}) reads "the window, questions that ended by {NEW_WINDOW}". And its gate, which names this entry as well: `tools/cache_behavior/run.py --prepare` and the driver refuse until the committed ledger holds 0075, 0076 and {NUM}, so the new value is not acted on before this entry is committed, and 0076's gate sentences (lines {L['gate_build']}, {L['gate_prepare']} and {L['gate_driver']}: "until the committed ledger holds 0075 and 0076"; line {L['gate_reads']}: "until the committed ledger holds 0076") read with {NUM} added. The config's header comment, the two tests that pin the registered config and the gate, and the cell's section of `{DOCS}` change with them.

**Why.** 0076 set its window end before the run had ended, as a cutoff on which questions are read. The run has ended, so no time at or after its last `end` selects among them, and the new value, the first whole minute after that `end`, lets the build, which refuses before the window ends (line {L['gate_prepare']}), follow the run instead of a time fixed before the run's end was known.

**Why it cannot change which trajectories are read.** When the value was set, the run 0075 registers had ended. Its launch records (the sha256 of their bytes, concatenated in row order, is `{RECORDS_SHA256[:12]}…`) give {RECORDS} records, one for each of the {fab.cohort} public questions, each the question's only launch and each a launch whose record marks a trajectory; every launch's output file has its record; and the latest `end` is {LAST_END}. Every question's records therefore end at or before both times, and the window holds the whole run under either, as 0076 provides (line {L['ended']}): "{CITED['ended'][1]}" The cell's own window rule (`window` in `tools/cache_behavior/fab_pairs.py`) puts the same {RECORDS} questions in the window at {OLD_WINDOW}, at {NEW_WINDOW} and at {LAST_END}. Any window end at or after {LAST_END} selects the same questions, so the choice between the two cannot select among them.

**What had been done when this was written.** No input had been prepared, no pair built, no manifest written, and the driver had not run; nothing exists under `results/cache-behavior-fab/`. 0075's summary, which reads the run's logs, had been computed after the run ended and before this value was set. 0076 says (line {L['seen']}) that every rule it registers, the window among them, was fixed before any content of the run's logs was read. That holds for the window's rule and for every other value 0076 registers. It does not hold for the two settings this entry changes, which were set after 0075's summary had been computed. For setting them and for this entry, of the run's files nothing was read but its launch records, the wrapper's own progress lines, and the names, sizes and times of the launches' output files: no content of the run's logs and none of the summary's values. It cannot matter to which questions are read: the same {RECORDS} are selected under either time.

**Registered before any pair is built.** 0076 was registered before any pair was built (line {L['built']}: "{CITED['built'][1]}"), and so is this entry: the build refuses until the committed ledger holds it.

**What does not change.** Everything else 0076 registers, each fixed, as line {L['seen']} says, before any content of the run's logs was read: the trajectories by 0075's code, the pair rule, the floor of {FLOOR} matched tokens, the ceiling of {CEILING} pairs and the registered order, the length rule and the cap, the host-memory rule, what is scored, the oracle removal fraction, the cross-instrument control, the controls, the probe and the stop, one preparation of the inputs, no interval, and the summary's fields. These files are the blobs 0076's commit left: {", ".join(h(r) for r in UNCHANGED)}. Nor does any cell or verdict change, or any other entry, config, record or output tree.

**Pinned at append.** {h(CONFIG)} and {h(TESTS)}, which 0076 pinned (line {L['pinned']}) as {h0076(CONFIG)} and {h0076(TESTS)}, and {h(DOCS)}, which 0076 did not pin. This script refuses unless the three are committed as-is, the config differs from 0076's in `window_end` and the gate only, by the values stated here, the test file differs from 0076's only in those two tests, and `{DOCS}` only in the cell's heading and its two comments; unless the other files are 0076's blobs; unless 0076's commit is dated before the run's last `end`; unless the launch records' bytes have the digest stated here, give the facts stated here, and the cell's `window` puts every question in the window at each of the three times; unless the drafts README stages it; and unless nothing exists under `results/cache-behavior-fab/`.

**Consequences in this commit set.** `{CONFIG}` (the value, the gate and the header comment), `{TESTS}` (the two tests above), the cell's section heading and two comments in `{DOCS}`, and the drafts README's allocator. Nothing under `results/`.

**Scope.** Two settings of one registration's config, the window end and the gate; a registration, not a result.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard {PREV} present, {NUM} absent. Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""
NB = "\u0000"


def wrap(par: str) -> str:
    """One paragraph at width 120; a code span is never broken across lines."""
    par = re.sub(r"`[^`]*`", lambda m: m.group(0).replace(" ", NB), " ".join(par.split()))
    return "\n".join(ln.replace(NB, " ") for ln in textwrap.wrap(par, width=120, break_long_words=False, break_on_hyphens=False))


_paras = RAW.split("\n\n")
assert _paras[0].startswith(f"### {NUM} ") and "\n" not in _paras[0] and _paras[-1] == "prior-entries-sha256: PLACEHOLDER\n"
assert NB not in RAW, "the entry text holds the wrap's placeholder"
ENTRY = "\n\n".join([_paras[0]] + [wrap(x) for x in _paras[1:-1]] + [_paras[-1]])
assert ENTRY.endswith("prior-entries-sha256: PLACEHOLDER\n") and ENTRY.count("PLACEHOLDER") == 1, "the chain line is not the entry's last"
assert "UNVERIFIED" not in ENTRY and OLD_WINDOW in ENTRY and NEW_WINDOW in ENTRY

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
