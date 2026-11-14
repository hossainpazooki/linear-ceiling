"""DRAFT append script for linear-ceiling: the camera-ready's figure set LISTED. The number is the ledger's next: 0072 when
entry 0071 (the L32-native cell's figures) is the ledger's last entry, 0071 when 0070 is. DESCRIPTIVE: no `verdict:` line,
no cell moves, nothing runs, no figure is admitted by value. The entry lists the entries appended after 0066's cut that
the camera-ready also draws figures from: this ledger's 0069, and 0071 when it is on the ledger, and the holdover
ledger's 0039.
Written venue-neutral.

Every line number and date in the entry is computed here: the line of each heading and located sentence, on this ledger
(the tree's, LF-normalized) and on the holdover ledger at its pinned commit; the dates from the headings and from 0069's
and 0071's Setup lines. Which entries were appended after the cut is computed from the commit log (read-only): the
entries on the ledger at the last commit before the cut are the ones before it, and every later heading is after it.
The script refuses unless the entries after the cut are exactly the named ones plus 0070, on this ledger, and 0039
alone on the holdover ledger. Five facts are in neither repository, so they are constants here, each read first-hand:
the operator's words and their time; the time it was decided to move the cut so that 0061's figures, and the holdover
ledger's 0039, might enter the camera-ready, and the date it was to move to (the script asserts that neither ledger states that date); the time a
place in it was kept for 0062's figures. The script asserts their order: the holdover commit that appended its 0039,
then the two decisions inside 0061's run (0069's Setup line) and before 0062's run began (0071's Setup line, when 0071
is on the ledger), then the operator's line, still inside 0061's run. The sentence on Figure 2(a) cites 0036, 0045 and
0060 by computed line; the files it names are not read here.

    python -I append_NNNN.py --repo-root . --date YYYY-MM-DD --holdover-repo <lag-ladder clone> [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root is required. It must be the current
directory and the top of its git work tree, and the imported `linear_ceiling` must be that tree's. --holdover-repo is
read with `git show`, `git log` and `git rev-list` only, at the pinned commit, and the ledger blob there must have the
pinned sha256. The script refuses under -O. Before the write, the ledger must equal HEAD's, be unmodified and pass
`ledger_check`. After the write `ledger_check` runs again, and on a failure the old bytes go back. Outside `--preview`,
the script refuses until docs/paper-to-record.md carries the listing sentence and the drafts README stages this
script with the next number. The script writes only ledger/ledger.md.
"""
import argparse
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys
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
ap.add_argument("--holdover-repo", type=Path, required=True)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)                    # a real calendar date, or ValueError
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True, env=ENV)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
assert (R / "ledger" / "ledger.md").is_file(), f"no ledger/ledger.md under {R}"
sys.path.insert(0, str(R / "src"))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
assert Path(_lc.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_lc.__file__}, not the tree's"

# --- constants: the two facts in neither repository, and the holdover ledger's pin -------------------------------------------
OP_WORDS = "cut is fluid as we write and as results come in"       # the operator's line, verbatim (a substring of it)
OP_TIME = "2026-11-11T19:14:07Z"                                    # its time, to the second (record 2026-11-11T19:14:07.480Z)
DEC61 = "2026-11-11T18:00:21Z"      # recorded: 0061's figures may enter the camera-ready (record 2026-11-11T18:00:21.583Z)
REDATE = "2026-11-12 16:00 UTC"      # what DEC61 decided, on the operator's delegation: the cut moved there by a new entry
                                     # (the 2026-11-11 ruling's ruling 2), so that 0061's figures and the holdover ledger's
                                     # 0039 might enter; never appended
DEC62 = "2026-11-11T18:42:40Z"      # recorded: a place in the camera-ready kept for 0062's figures (the record's stamp)
LL_COMMIT = "840098ef073bd8047ee5acca0746a321a73a6b3d"              # holdover main that appended its 0039
LL_LEDGER_SHA256 = "7d9135ae61342debba083911648dac57cd95d2f1d29ea74e2bf14f2ec7220847"
P2R = "docs/paper-to-record.md"
P2R_ANCHOR = "Entry 0066 (2026-10-27) withdrew that cut"
P2R_LAST = "own cut entry when chosen."                              # the last line of 0066's sentence there, at P0
LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"


def git(repo: Path, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True, env=ENV).stdout.decode("utf-8")


def block(t: str, entry: str) -> tuple:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} heading lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def line_of(t: str, offset: int) -> int:
    return t.count("\n", 0, offset) + 1


def heading(t: str, entry: str) -> tuple:
    """(line, date) of the entry's heading."""
    start, b = block(t, entry)
    m = re.match(rf"### {entry} — (\d{{4}}-\d{{2}}-\d{{2}}) — ", b)
    assert m, f"{entry}: heading is not '### {entry} — YYYY-MM-DD — '"
    return line_of(t, start), m.group(1)


def loose(phrase: str) -> re.Pattern:
    """The phrase with any whitespace between its words."""
    return re.compile(r"\s+".join(re.escape(w) for w in phrase.split()))


def span(t: str, base: int, m0: re.Match, m1: re.Match) -> str:
    l0, l1 = line_of(t, base + m0.start()), line_of(t, base + m1.end() - 1)
    return f"line {l0}" if l0 == l1 else f"lines {l0}-{l1}"


def lines(t: str, entry: str, first: str, last: str = None) -> str:
    """'line N' or 'lines N-M': where the text from `first` to `last` (or `first` alone) stands inside the entry; each
    phrase is matched with any whitespace between its words and must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(loose(first).finditer(b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {first[:60]!r}"
    if last is None:
        return span(t, start, hits[0], hits[0])
    ends = list(loose(last).finditer(b))
    assert len(ends) == 1 and ends[0].start() > hits[0].start(), f"{entry}: {last[:60]!r} is not once, after {first[:40]!r}"
    assert "\n\n" not in b[hits[0].start():ends[0].end()], f"{entry}: {first[:40]!r} to {last[:40]!r} crosses a paragraph"
    return span(t, start, hits[0], ends[0])


def utc(iso: str) -> str:
    return dt.datetime.fromisoformat(iso).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def at_cut(repo: Path, rev: str, cut_iso: str) -> tuple:
    """The headings on the ledger at the last commit (up to rev) committed before the cut, and that commit's UTC time."""
    c = git(repo, "rev-list", "-1", f"--before={cut_iso}", rev).strip()
    assert re.fullmatch(r"[0-9a-f]{40}", c), f"no commit before the cut under {rev} in {repo}"
    when = utc(git(repo, "show", "-s", "--format=%cI", c).strip())
    assert when < cut_iso, f"{c[:7]} at {when} is not before the cut"
    led = git(repo, "show", f"{c}:ledger/ledger.md").replace("\r\n", "\n")
    return re.findall(r"^### (\d{4}) ", led, re.M), when


def after_cut(t: str, repo: Path, rev: str, cut_iso: str) -> list:
    """The entries of ledger text t that were not on the ledger at the cut; each heading's date agrees with its side."""
    hs = re.findall(r"^### (\d{4}) ", t, re.M)
    before, _ = at_cut(repo, rev, cut_iso)
    assert hs[:len(before)] == before, "the ledger at the cut is not a prefix of this ledger"
    for e in hs:
        d = heading(t, e)[1]
        assert (d <= cut_iso[:10]) if e in before else (d >= cut_iso[:10]), f"{e}'s heading date {d} is on the wrong side of the cut"
    return hs[len(before):]


def first_on_ledger(repo: Path, rev: str, entry: str) -> str:
    """UTC time of the oldest commit (up to rev) whose ledger/ledger.md gained the entry's heading."""
    log = git(repo, "log", "--format=%cI", "--reverse", "-S", f"### {entry} — ", rev, "--", "ledger/ledger.md").split()
    assert log, f"no commit put {entry}'s heading on {repo}'s ledger"
    return utc(log[0])


# --- this ledger: the tree's, the ordering, the case -------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]                                 # file order is not number order (0005, 0052-0056), but the last is the highest
assert PREV == max(heads), f"the ledger's last entry {PREV} is not its highest number"
assert PREV in ("0070", "0071"), f"the ledger's last entry is {PREV}, not 0070 or 0071"
WITH71 = PREV == "0071"
if WITH71:
    assert re.match(r"### 0071 — \d{4}-\d{2}-\d{2} — E-TRUNC, the L32-native cell ran ", block(text, "0071")[1]), \
        "0071 is not the L32-native cell's figures entry"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
assert NUM not in heads, f"ordering: {NUM} must be absent"
for e in ("0061", "0062", "0065", "0066", "0069", "0070"):
    assert e in heads, f"ordering: {e} must be on the ledger"

# 0066: the cut and the sentences this entry reads beside its list
_, b66 = block(text, "0066")
m = re.search(r"\*\*It may draw on\s+every figure that an entry on this ledger states at (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC\*\*", b66)
assert m, "0066 does not state its cut as '**It may draw on every figure that an entry on this ledger states at <date> <time> UTC**'"
CUT_DATE, CUT_HM = m.group(1), m.group(2)
CUT = f"{CUT_DATE} {CUT_HM} UTC"
CUT_ISO = f"{CUT_DATE}T{CUT_HM}:00Z"
L66, D66 = heading(text, "0066")
assert f"at its own cut ({CUT})" in b66.split("\n", 1)[0], "0066's heading does not state the same cut"
S_DRAW = lines(text, "0066", f"may draw on every figure that an entry on this ledger states at {CUT}")
S_BOTH = lines(text, "0066", "0065's sentence on the sibling record stands", "cut applies to both ledgers by date.")
S_AFTER = lines(text, "0066", f"a figures entry appended after {CUT} is material for the full paper at the next venue.")
S_SIB = lines(text, "0066", "0065's sentence on the sibling record stands", "own entries, never through this one,")
CLAUSE = "enter the camera-ready if on the ledger at the cut and the full paper otherwise"
S_CLAUSE = lines(text, "0066", "the registrations 0061–0064 and their figures entries, which", CLAUSE + ".")
S_NAME = lines(text, "0066", "No figure is admitted by name.")
HIST = "The camera-ready's appendix tells the venue history in the record's own words, by entry number (0060, 0065, this entry)"
S_HIST = lines(text, "0066", HIST, "find the same account.")
READ = "each figure as its summary file states it, with the file's sha, entering paper text only by the admitted evidence path"
S_READ = lines(text, "0066", READ)

# the entries named, and the one appended after the cut that is not
L61, D61 = heading(text, "0061")
L62, D62 = heading(text, "0062")
L67, D67 = heading(text, "0067")
L69, D69 = heading(text, "0069")
L70, D70 = heading(text, "0070")
assert D70 > CUT_DATE, "0070 is not dated after the cut"
assert D61 < CUT_DATE and D62 < CUT_DATE, "0061 and 0062 were not registered before the cut's day"
assert re.match(r"### 0067 — \d{4}-\d{2}-\d{2} — Entry 0061's inputs re-prepared ", block(text, "0067")[1]), "0067 is not 0061's inputs re-prepared"
_, b69 = block(text, "0069")
m = re.search(r"probe on the\s+largest handoff launched (\d{4}-\d{2}-\d{2})T([\d:]{8})Z, run launched ([\d:]{8})Z, finished ([\d:]{8})Z", b69)
assert m, "0069's Setup line does not state the probe launch, the run launch and the finish as expected"
RUN69 = m.group(1)
R69_START, R69_END = f"{RUN69}T{m.group(3)}Z", f"{RUN69}T{m.group(4)}Z"
assert m.group(2) < m.group(3) < m.group(4), "0069's times are not on one day in order (probe, run, finish)"
assert CUT_ISO < R69_START, "0069's run started before the cut"
assert R69_START < OP_TIME < R69_END, "the operator's line does not fall inside 0069's run"
assert R69_START < DEC61 < DEC62 < OP_TIME and DEC61[:10] == DEC62[:10] == RUN69, "the decisions are not inside 0061's run, in order, on its day, before the operator's line"
assert CUT_DATE < DEC61[:10] < REDATE[:10] < D69, "the date the cut was to move to is not after the decision and before 0069's heading date"
assert REDATE not in text and REDATE[:16] not in text, f"this ledger states {REDATE}: an entry did move the cut"
if WITH71:
    L71, D71 = heading(text, "0071")
    _, b71 = block(text, "0071")
    m = re.search(r"chain launched ((\d{4}-\d{2}-\d{2})T[\d:]{8}Z), driver up [\d:]{8}Z, the \w+ handoff and driver exit 0 by\s+(\d{4}-\d{2}-\d{2})T[\d:]{8}Z", b71)
    assert m, "0071's Setup line does not state the chain launch and the driver exit as expected"
    CHAIN71, RUN71S, RUN71E = m.group(1), m.group(2), m.group(3)
    assert CUT_DATE < RUN71S <= RUN71E <= D71, "0071's run dates are not after the cut and before its heading date"
    assert DEC62 < CHAIN71, "the place for 0062's figures was not kept before 0062's run began"
NAMED = ["0069"] + (["0071"] if WITH71 else [])
after = after_cut(text, R, "HEAD", CUT_ISO)
assert after == sorted(NAMED + ["0070"]), f"entries appended after the cut are {after}, not {sorted(NAMED + ['0070'])}"
assert "0067" in heads and "0067" not in after, "0067 is not on the ledger before the cut"

# --- the holdover ledger, at its pinned commit -------------------------------------------------------------------------------
H = a.holdover_repo.resolve()
llb = subprocess.run(["git", "-C", str(H), "show", f"{LL_COMMIT}:ledger/ledger.md"], capture_output=True, check=True, env=ENV).stdout
assert hashlib.sha256(llb).hexdigest() == LL_LEDGER_SHA256, "the holdover ledger at the pinned commit is not the pinned blob"
ll = llb.decode("utf-8").replace("\r\n", "\n")
ll_heads = re.findall(r"^### (\d{4}) ", ll, re.M)
assert ll_heads[-1] == "0039" and ll_heads.count("0039") == 1 and ll_heads.count("0035") == 1, "the holdover ledger's 0035 and 0039 are not as pinned"
LL35, DLL35 = heading(ll, "0035")
LL39, DLL39 = heading(ll, "0039")
assert DLL35 < CUT_DATE, "the holdover 0035 was not registered before the cut's day"
assert "0035" in block(ll, "0039")[1].split("\n", 1)[0], "the holdover 0039's heading does not name its registration, 0035"
T39 = first_on_ledger(H, LL_COMMIT, "0039")
assert T39 == utc(git(H, "show", "-s", "--format=%cI", LL_COMMIT).strip()), "the pinned commit is not the one that appended the holdover 0039"
assert T39[:10] == DLL39 == DEC61[:10] and CUT_ISO < T39 < DEC61, "the holdover 0039 was not appended after the cut and earlier on the day of the decisions"
assert after_cut(ll, H, LL_COMMIT, CUT_ISO) == ["0039"], "the holdover entries appended after the cut are not 0039 alone"
assert REDATE[:16] not in ll, f"the holdover ledger states {REDATE}: an entry did move the cut"

# --- the living documents this entry requires in its staging commit ----------------------------------------------------------
p2r = (R / P2R).read_text(encoding="utf-8").replace("\r\n", "\n")
assert p2r.count(P2R_ANCHOR) == 1 and p2r.count(P2R_LAST) == 1, f"{P2R} does not hold 0066's sentence once"
NAMES_P2R = "this ledger's 0069 and 0071" if WITH71 else "this ledger's 0069"
P2R_SENTENCE = (f"Entry {NUM} ({a.date}) lists the entries appended after that cut that the camera-ready also draws figures from: "
                f"{NAMES_P2R} and the holdover ledger's 0039, each registered before the cut. Any other figures entry "
                f"appended after the cut stays material for the full paper.")
s_hits = list(loose(P2R_SENTENCE).finditer(p2r))
staged_p2r = len(s_hits) == 1 and p2r.index(P2R_LAST) + len(P2R_LAST) + 1 == s_hits[0].start() and p2r[s_hits[0].start() - 1] == "\n"
_p0 = p2r.index(P2R_ANCHOR)
_p1 = s_hits[0].end() - 1 if staged_p2r else p2r.index(P2R_LAST) + len(P2R_LAST) - 1
P2R_LINES = f"lines {line_of(p2r, _p0)}-{line_of(p2r, _p1)}"
assert "\n\n" not in p2r[_p0:_p1], f"{P2R}: 0066's sentence and this entry's are not one paragraph"
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
staged_readme = f"`append_{NUM}.py`" in readme and bool(free) and free[-1] == NEXT
if not a.preview:
    assert staged_p2r, f"{P2R} does not carry the listing sentence for {NUM} right after 0066's; the staging commit adds it"
    assert staged_readme, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"

# --- Figure 2(a): the one drawing that goes past the entries -------------------------------------------------------------------
L36, D36 = heading(text, "0036")
assert re.match(r"### 0036 — \d{4}-\d{2}-\d{2} — E9-long ran `\[BASELINE\]`; H-E9L HELD \(35 scored of 35 registered\)", block(text, "0036")[1]), "0036 is not E9-long's run, 35 of 35"
S60 = lines(text, "0060", "`tail.json` (`7683696cd02a`)")
S45 = lines(text, "0045", "Pinned: `tail.json` → `report.json` 084d9480af74,")
FIG2A = (f"Figure 2(a) is drawn directly from the files of 0036's run (line {L36}). Its 35 "
         f"ticks are the per-handoff means that `results/e9l/tail.json` holds (0060 names that file with its sha, {S60}); its "
         f"curve is drawn from the 35 handoffs' score files and per-token files, each pinned by the sha256 that "
         f"`results/e9l/report.json` records for it, and 0045 pins that report ({S45}). No entry tabulates the curve or the 35 means.")

# --- the entry --------------------------------------------------------------------------------------------------------------
NAMES_HEAD = "this ledger's 0069 and 0071 and the holdover ledger's 0039" if WITH71 else "this ledger's 0069 and the holdover ledger's 0039"
FIG_ENTRIES = "0069 and 0071, the figures entries of 0061 and 0062," if WITH71 else "0069, the figures entry of 0061,"
ITEM71 = (f"""
- This ledger's 0071 (line {L71}): the figures of the L32-native cell that 0062 registered (line {L62}) on {D62},
  before the cut. Its run started on {RUN71S} and finished on {RUN71E} (0071's Setup line); 0071 was appended on {D71}.""" if WITH71 else "")
PLACE62 = (f""" The same day, before 0062's run
began, a place in the camera-ready was kept for 0062's figures.""" if WITH71 else "")
ENTRY = f"""### {NUM} — {a.date} — The camera-ready's figure set listed: beside every figure on either ledger at 0066's cut ({CUT}), it draws figures from the entries appended after that cut and listed here, {NAMES_HEAD}, each registered before the cut and listed here with its figures in hand; for these entries 0066's clause on the figures entries of 0061 to 0064 and its "No figure is admitted by name" change, as do its sentence on the venue history in the camera-ready's appendix and, for Figure 2(a)'s curve alone, its sentence on how each figure is read, and the rest of 0066 stands; descriptive, no cell moves

**What this entry is.** 0066 (line {L66}) set the camera-ready's cut: the camera-ready "may draw on every figure that an
entry on this ledger states at {CUT}" ({S_DRAW}). The cut applies to both ledgers by date ({S_BOTH}), and a
figures entry appended after it is material for the full paper at the next venue ({S_AFTER}). The camera-ready also
draws figures from the entries listed below, each appended after that time. This entry lists them, and so closes the camera-ready's
figure set: every figure of either record that the camera-ready prints comes from an entry on either ledger at 0066's cut
or from an entry listed here, but for one drawing: {FIG2A} Every other figure is read as its summary file states it, with the file's sha, by the
admitted evidence path, as 0066 states. Nothing is measured here.

**The entries listed.**
- This ledger's 0069 (line {L69}): the figures of the repair arms that 0061 registered (line {L61}) on {D61}, run on
  the inputs that 0067 re-prepared (line {L67}) on {D67}, both before the cut. Its run started and finished on
  {RUN69}; 0069 was appended on {D69}.{ITEM71}
- The holdover ledger's 0039 (that ledger's line {LL39}): the outcome of the run that its 0035 (line {LL35}) registered on
  {DLL35}, before the cut. It was appended on {DLL39}, after the run. Its figures enter the paper through that
  ledger's own entry, as 0065's sentence requires ({S_SIB}); this entry only lists it past the cut.

**When each was listed.** The holdover ledger's 0039 came first: it was appended on {DLL39} with its outcome stated.
Later that day, while 0061's run was in progress and before its outcome was complete, it was decided, on the operator's
delegation, to move the cut to {REDATE} by a new entry, so that 0061's figures, and the holdover ledger's 0039, might
enter the camera-ready.{PLACE62}
After that, with 0061's run still in progress, the operator ruled, verbatim: "{OP_WORDS}". No such entry was appended,
and the date {REDATE} was not kept after the operator's sentence; 0069, appended on {D69}, is after it as well. No entry
moved the cut. Only this entry's list comes with every listed entry's figures in hand. This ledger's 0070 was also
appended after the cut (line {L70}) and is not one of the entries listed here: the camera-ready draws no figure from it
and says only that its cell has run. Its figures, like those of any entry appended after the cut and not listed here,
are material for the full paper at the next venue, as 0066 says.

**What changes in 0066, and what stands.** Four statements of 0066 change. For the entries listed here, its clause that
the figures entries of 0061 to 0064 "{CLAUSE}" ({S_CLAUSE}), and its "No figure is admitted
by name" ({S_NAME}): {FIG_ENTRIES} {"were" if WITH71 else "was"} not on the ledger at the cut, and this entry lists {"them" if WITH71 else "it"} for the
camera-ready. Its sentence "{HIST}" ({S_HIST}): the camera-ready does not tell that history; the record does. And,
for Figure 2(a)'s curve alone, its sentence on how each figure is read, "{READ}" ({S_READ}): the curve is drawn as
the sentence on Figure 2(a) above states.
Everything else in 0066 stands as written. Its three statements of {CUT} (its heading, line
{L66}; {S_DRAW}; {S_AFTER}) stand; for the camera-ready they are read with this entry's list beside them.

**What this does NOT touch.** No `verdict:` line; every cell as decided; the entries listed, which this entry neither
restates nor re-reads. No figure is admitted by value. Nothing runs under this entry.

**Consequences in this commit set.** `{P2R}` (the figure-set sentence, {P2R_LINES}: the camera-ready
also draws figures from the entries listed here); the drafts README's allocator. Nothing under `results/`.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard {PREV} present, {NUM} absent.
Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""
assert ENTRY.endswith("prior-entries-sha256: PLACEHOLDER\n") and ENTRY.count("PLACEHOLDER") == 1, "the chain line is not the entry's last"

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print("[ordering guard: ok]")
    raise SystemExit(0)


# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included --------------------------------------
def ledger_check():
    return subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True,
                          env=dict(ENV, PYTHONPATH=str(R / "src")))


at_head = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=R, capture_output=True, check=True, env=ENV).stdout
assert text == at_head.decode("utf-8").replace("\r\n", "\n"), "ledger/ledger.md is not HEAD's: an uncommitted edit"
assert git(R, "status", "--porcelain", "--", "ledger/ledger.md").strip() == "", "ledger/ledger.md is modified in the working tree"
r0 = ledger_check()
assert r0.returncode == 0 and r0.stdout.strip().endswith(LEDGER_OK), f"ledger_check before the write: {(r0.stdout + r0.stderr).strip()[-400:]}"
assert "prior-entries-sha256: PLACEHOLDER" not in text, "the ledger already holds a placeholder chain line"
base = text + ("" if text.endswith("\n") else "\n") + "\n"
digest = chain_hash(base + ENTRY, len(base), _ENTRIES_HEAD.search(base).start())
new = base + ENTRY.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
assert new.startswith(text) and new.count(f"\n### {NUM} ") == 1 and new.index(f"\n### {NUM} ") + 1 == len(base), "the new ledger is not the old one plus this entry"
# --- the write, and after it: ledger_check, else the old bytes go back -------------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
