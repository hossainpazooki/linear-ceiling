"""DRAFT append script for linear-ceiling: a note to entries 0047 and 0061. Both register the fresh-repeat control as
exact; the driver of each of their two runs of record stops only when the larger of the two controls exceeds 0.0005.
Both runs' fresh repeat is exactly 0, so the registered rule was met and no figure moves. The number is the ledger's
next, 0074 after 0073. DESCRIPTIVE: no `verdict:` line, no cell moves, nothing runs.

Every line number and value in the entry is computed here, read-only: the lines of the registrations on this ledger (the
tree's, LF-normalized); the two runs' reports under `results/`, each pinned by sha256 and each sha's prefix as the entry
that pins it states it; each run's driver and config, read with `git show` at the commit its entry names, pinned by
sha256, and the lines of the control check.

    python -I append_NNNN.py --repo-root . --date YYYY-MM-DD [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root is required. It must be the current
directory and the top of its git work tree, and the imported `linear_ceiling` must be that tree's. The script refuses
under -O. Before the write, the ledger must equal HEAD's, be unmodified and pass `ledger_check`. After the write
`ledger_check` runs again, and on a failure the old bytes go back. Outside `--preview`, the script refuses until the
drafts README stages this script with the next number. The script writes only ledger/ledger.md.
"""
import argparse
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

# --- pins: each full sha256 here, and its prefix as the entry that pins it states it --------------------------------------------
DRIVER = "tools/cache_behavior/run.py"
LIMIT_KEY = "control_max_logit_error"
LIMIT = 0.0005
RUNS = [  # (registration, figures entry, run commit, driver sha, config path, config sha, report path, report sha)
    dict(reg="0047", fig="0049", commit="7c9a5fd34c2df70c66269f755a61a882440e4f79",
         drv_sha="15e1ff8c1dbc7925398edc11ed68d91b6cdba4f335a49adcb29baa1b10729de5",      # 0049: "`run.py` `15e1ff8c1dbc…`"
         cfg="config/cache-behavior.toml",
         cfg_sha="53c664556d18792401db8c1b930e487a90b88ab19c65ad94a1ab982094443a28",      # 0047: "(`53c664556d18…`)"
         rep="results/cache-behavior/report.json",
         rep_sha="3564605773bb3751d9e0e842fcbf238cd41e662a7f93a1442902a61c0ca56f14"),     # 0049: "`report.json` `3564605773bb…`"
    dict(reg="0061", fig="0069", commit="f98d53bfef4d11fb53f1335d712414cd8cd3571e",
         drv_sha="e137f1d8b8c5ce7f7747c8b06508ed7b09f6dc49a0731225dc8bcece9d8c2c33",      # 0061 and 0069: "`run.py` `e137f1d8b8c5…`"
         cfg="config/cache-behavior-repair.toml",
         cfg_sha="97aa99b1958eb55badf095955f44f2d6c0d67868a0f4196f6c5851f94e82d563",      # 0061: "(`97aa99b1958e…`)"
         rep="results/cache-behavior-repair/report.json",
         rep_sha="21b62a01a504f66421cd1d452c14eed5c8b07c6a6d630d9f64d670cd86d6c9f9"),     # 0069: "`21b62a01a504…`"
]
LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
S47_FR = ("Fresh repeat: a second FRESH pass must reproduce the first's logits exactly. Prefix copy over 128 tokens: "
          "maximum logit error ≤ 0.0005.")
S61_FR = "As 0047, unchanged: fresh repeat exact, prefix copy over 128 tokens ≤ 0.0005,"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args) -> bytes:
    return subprocess.run(["git", "-C", str(R), *args], capture_output=True, check=True, env=ENV).stdout


def block(t: str, entry: str) -> tuple:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} heading lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def line_of(t: str, offset: int) -> int:
    return t.count("\n", 0, offset) + 1


def loose(phrase: str) -> re.Pattern:
    """The phrase with any whitespace between its words."""
    return re.compile(r"\s+".join(re.escape(w) for w in phrase.split()))


def once(t: str, entry: str, phrase: str) -> str:
    """'line N' or 'lines N-M' of the phrase, which must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(loose(phrase).finditer(b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {phrase[:60]!r}"
    l0, l1 = line_of(t, start + hits[0].start()), line_of(t, start + hits[0].end() - 1)
    return f"line {l0}" if l0 == l1 else f"lines {l0}-{l1}"


def pinned(t: str, entry: str, full: str) -> None:
    assert re.search(rf"`{full[:12]}…`", block(t, entry)[1]), f"{entry} does not pin `{full[:12]}…`"


# --- this ledger: the tree's, the ordering ------------------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0073", f"the ledger's last entry is {PREV}, not 0073"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
for e in ("0047", "0049", "0061", "0069", "0073"):
    assert e in heads, f"ordering: {e} must be on the ledger"
assert re.match(r"### 0047 — \d{4}-\d{2}-\d{2} — Cache-behavior comparison registered ", block(text, "0047")[1]), "0047 is not the registration"
assert re.match(r"### 0049 — \d{4}-\d{2}-\d{2} — Cache-behavior comparison ran ", block(text, "0049")[1]), "0049 is not the run"
assert re.match(r"### 0061 — \d{4}-\d{2}-\d{2} — Cache-behavior REPAIR amendment registered ", block(text, "0061")[1]), "0061 is not the repair registration"
assert re.match(r"### 0069 — \d{4}-\d{2}-\d{2} — Cache-behavior REPAIR ran ", block(text, "0069")[1]), "0069 is not the repair run"
L = {e: line_of(text, block(text, e)[0]) for e in ("0047", "0049", "0061", "0069")}
W47 = once(text, "0047", S47_FR)
W61 = once(text, "0061", S61_FR)
for r in RUNS:
    b = block(text, r["fig"])[1]
    assert f"run at commit `{r['commit'][:7]}`" in b, f"{r['fig']} does not name the run commit {r['commit'][:7]}"
    pinned(text, r["fig"], r["drv_sha"])
    pinned(text, r["fig"], r["rep_sha"])
    pinned(text, r["reg"], r["cfg_sha"])
pinned(text, "0061", RUNS[1]["drv_sha"])
for later in sorted(h for h in heads if int(h) > 47):
    assert LIMIT_KEY not in block(text, later)[1], f"{later} already names the driver's control limit"

# --- each run of record: its report, its driver and config at its commit -------------------------------------------------------


def dline(src: str, pattern: str) -> int:
    hits = [m.start() for m in re.finditer(pattern, src, re.M)]
    assert len(hits) == 1, f"driver: {len(hits)} hits for {pattern!r}"
    return line_of(src, hits[0])


for r in RUNS:
    rb = (R / r["rep"]).read_bytes()
    assert sha(rb) == r["rep_sha"], f"{r['rep']} is not the file {r['fig']} pins"
    rep = json.loads(rb)
    ident = rep.get("identity", {})
    assert rep.get("git_commit") == r["commit"], f"{r['rep']} does not record the run commit"
    assert ident.get("code_sha256", {}).get("run.py") == r["drv_sha"], f"{r['rep']} does not record the pinned driver"
    assert ident.get("config_sha256") == r["cfg_sha"], f"{r['rep']} does not record the pinned config"
    s, order = rep["scores"], rep["run_order"]
    assert rep["complete"] is True and list(s) == order and len(s) == 35, f"{r['rep']}: not complete, not 35, or out of run order"
    carry = [h for h, v in s.items() if v["controls"]]
    assert carry == [order[0]], f"{r['rep']}: the controls are on {carry}, not on the first handoff alone"
    c = s[order[0]]["controls"]
    assert set(c) == {"fresh_repeat", "prefix_copy"}, f"{r['rep']}: controls {sorted(c)}"
    fr, pc = c["fresh_repeat"]["max_logit_error"], c["prefix_copy"]["max_logit_error"]
    assert type(fr) is float and fr == 0.0, f"{r['rep']}: the fresh repeat's maximum logit error is {fr!r}, not exactly 0"
    assert type(pc) is float and 0.0 < pc <= LIMIT, f"{r['rep']}: prefix copy {pc!r} is not within the limit"
    r.update(probe=order[0], fr=fr, pc=pc)

    assert subprocess.run(["git", "-C", str(R), "merge-base", "--is-ancestor", r["commit"], "HEAD"], env=ENV).returncode == 0, \
        f"{r['commit'][:7]} is not an ancestor of HEAD"
    db = git("show", f"{r['commit']}:{DRIVER}")
    assert sha(db) == r["drv_sha"], f"{DRIVER} at {r['commit'][:7]} is not the pinned blob"
    cb = git("show", f"{r['commit']}:{r['cfg']}")
    assert sha(cb) == r["cfg_sha"], f"{r['cfg']} at {r['commit'][:7]} is not the pinned blob"
    drv, cfg = db.decode("utf-8"), cb.decode("utf-8")
    assert "\r" not in drv and "\r" not in cfg, "a blob is not LF"
    assert tomllib.loads(cfg)[LIMIT_KEY] == LIMIT, f"{r['cfg']}: {LIMIT_KEY} is not {LIMIT}"
    r["cfg_line"] = dline(cfg, rf"^{LIMIT_KEY} = 0\.0005$")
    r["if0"] = dline(drv, r'^        if index == 0:$')
    r["fr_line"] = dline(drv, r'^            controls\["fresh_repeat"\] = \{\*\*metrics\(compared\), "max_logit_error": compared\["max_logit_error"\]\}$')
    r["pc_line"] = dline(drv, r'^            controls\["prefix_copy"\] = \{\*\*metrics\(compared\), "max_logit_error": compared\["max_logit_error"\]\}$')
    r["max_line"] = dline(drv, r'^            if max\(c\["max_logit_error"\] for c in controls\.values\(\)\) > cfg\["control_max_logit_error"\]:$')
    r["raise_line"] = dline(drv, r'^                raise ValueError\(f"fresh/prefix identity control failed: \{controls\}"\)$')
    assert r["if0"] < r["fr_line"] < r["pc_line"] < r["max_line"] == r["raise_line"] - 1, f"{r['commit'][:7]}: the check is not in this order"
    assert drv.count(LIMIT_KEY) == 1 and drv.count("fresh_repeat") == 1, f"{r['commit'][:7]}: the driver uses the limit or the fresh repeat elsewhere"
    gg = subprocess.run(["git", "-C", str(R), "grep", "-l", "fresh_repeat", r["commit"], "--", "tools", "src"],
                        capture_output=True, text=True, env=ENV)
    assert gg.returncode == 0 and gg.stdout.split() == [f"{r['commit']}:{DRIVER}"], \
        f"{r['commit'][:7]}: code other than the driver names the fresh repeat: {gg.stdout.split()}"
    dl = drv.split("\n")
    r["loop"] = dline(drv, r'^    for index, record in enumerate\(order\[:1\] if args\.probe else order\):$')
    r["skip"] = dline(drv, r'^        if hid in report\["scores"\]:$')
    assert dl[r["skip"]] == "            continue" and r["loop"] < r["skip"] < r["if0"], f"{r['commit'][:7]}: the resume skip is not where stated"
    r["res0"] = dline(drv, r'^        if not args\.resume:$')
    assert dl[r["res0"]] == '            raise ValueError("output exists; pass --resume to verify and continue")' and r["res0"] < r["loop"], \
        f"{r['commit'][:7]}: an existing output does not require --resume before the loop"
    assert all(ln.startswith(" " * 12) or not ln.strip() for ln in dl[r["if0"]:r["raise_line"]]), \
        f"{r['commit'][:7]}: the control check is not inside `if index == 0:`"

A, B = RUNS
# --- each run of record is two launches into one output tree: the probe launch, then the resumed run -------------------------
RB = "docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md"
rbt = git("show", f"HEAD:{RB}").decode("utf-8").replace("\r\n", "\n")
assert (R / RB).read_text(encoding="utf-8").replace("\r\n", "\n") == rbt, f"{RB} is not HEAD's"


def rline(phrase: str) -> int:
    hits = [m.start() for m in re.finditer(re.escape(phrase), rbt)]
    assert len(hits) == 1, f"{RB}: {len(hits)} hits for {phrase!r}"
    return line_of(rbt, hits[0])


RB_PROBE = rline("**23:50 R2 probe launched** detached (`--probe`, the largest handoff `django__django-11087_traj#152`")
RB_RUN = rline("**23:56 `--run --resume` launched** over the remaining 34")
assert RB_PROBE < RB_RUN, f"{RB}: the probe launch is not before the resumed run"
assert A["probe"] == "20241016_composio_swekit/django__django-11087_traj#152", "the probe handoff is not the runbook's"
W69_LAUNCH = once(text, "0069", "probe on the largest handoff launched")
_ = once(text, "0069", "run launched")
W69_FIRST = once(text, "0069", "3 on the first handoff in run order (the probe)")
W69_CTRL = once(text, "0069", "on the probe handoff, the only one that carries the two controls")
EX_COMMIT = "40fbdd975e79d22144957bb835c85029fe45cc91"      # 0069's staging commit
EX_PATH = "docs/drafts/append_0069.py"
exs = git("show", f"{EX_COMMIT}:{EX_PATH}").decode("utf-8")
assert git("log", "-1", "--format=%s", EX_COMMIT).decode().strip() == "docs: stage 0069 (cache-behavior REPAIR figures)", "not 0069's staging commit"
EX_LOG = git("log", "--format=%H", "--", EX_PATH).decode().split()
assert EX_LOG == ["25e5360e6aeba2b6213514dc172b737aeade66d8", EX_COMMIT], f"{EX_PATH} has commits other than its staging and retirement: {EX_LOG}"
EX_LINE = dline(exs, r'^assert ctrl\["fresh_repeat"\] == 0\.0 and ctrl\["prefix_copy"\] <= limit$')
assert A["probe"] == B["probe"] and (A["fr"], A["pc"]) == (B["fr"], B["pc"]), "the two runs do not carry the controls on the same handoff with the same values"

# --- the drafts README stages this script --------------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
staged_readme = f"`append_{NUM}.py`" in readme and bool(free) and free[-1] == NEXT
if not a.preview:
    assert staged_readme, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"


def runs_line(r: dict) -> str:
    return (f"`{DRIVER}` (`{r['drv_sha'][:12]}…`) at `{r['commit'][:7]}`, with `{r['cfg']}` (`{r['cfg_sha'][:12]}…`) "
            f"setting `{LIMIT_KEY} = {LIMIT}` (line {r['cfg_line']})")


# --- the entry ----------------------------------------------------------------------------------------------------------------
RAW = f"""### {NUM} — {a.date} — Note to 0047 and 0061: both register the fresh repeat as exact, while the driver of each of their two runs of record stops on the controls' size only when either exceeds {LIMIT}; in both runs the fresh repeat is exactly 0 on the probe handoff, so the registered rule was met and nothing moves

**The registrations.** 0047 (line {L['0047']}) reads: "{S47_FR}" ({W47}). 0061 (line {L['0061']}) keeps the controls:
"{S61_FR} …" ({W61}).

**The drivers.** The run of 0047, entered as 0049 (line {L['0049']}), ran {runs_line(A)}. Inside `if index == 0:` (line
{A['if0']}), that is on the first handoff of the run order alone, it records the fresh repeat's maximum logit error (line
{A['fr_line']}) and the prefix copy's (line {A['pc_line']}), and stops if the larger of the two exceeds the limit (lines
{A['max_line']}-{A['raise_line']}). The run of 0061, entered as 0069 (line {L['0069']}), ran {runs_line(B)}; the same
check is at lines {B['if0']}, {B['fr_line']}, {B['pc_line']} and {B['max_line']}-{B['raise_line']}. Neither driver, nor any
other file under `tools/` or `src/` at either commit, checks the fresh repeat on its own: each would have accepted a
fresh-repeat error up to {LIMIT}, where 0047 and 0061 allow none.

**The two runs of record.** This entry covers the two runs under `results/` registered with an exact fresh repeat, and
no other output. Each is two launches into one output tree. The `--probe` launch scores the first handoff of the run
order alone (line {A['loop']} at `{A['commit'][:7]}`, line {B['loop']} at `{B['commit'][:7]}`), and so computes and
checks both controls. The `--run --resume` launch then continues that tree: an existing output needs `--resume` (lines
{A['res0']}-{A['res0'] + 1}; {B['res0']}-{B['res0'] + 1}), and a handoff already scored is skipped (lines
{A['skip']}-{A['skip'] + 1}; {B['skip']}-{B['skip'] + 1}), so the control block does not run again. For 0049 the runbook
`{RB}` records the two launches (lines {RB_PROBE} and {RB_RUN}); for 0069, its setup sentence ({W69_LAUNCH}), which with 0069's "the first handoff in run order (the probe)"
({W69_FIRST}) and "on the probe handoff, the only one that carries the two controls" ({W69_CTRL}) places the controls in
the probe launch. 0049's `{A['rep']}` (`{A['rep_sha'][:12]}…`) and 0069's `{B['rep']}`
(`{B['rep_sha'][:12]}…`) each carry the controls on the same handoff, `{A['probe']}`, and in each the fresh repeat's
maximum logit error is recorded as {A['fr']!r}, exactly 0. The prefix copy's is {A['pc']:.2e} in both, within {LIMIT}.

**Consequence.** Both runs met the rule as registered, on the probe handoff, the only one that carries the controls
(0073). 0069's append script (`{EX_PATH}` at `{EX_COMMIT[:7]}`, line {EX_LINE}) already required the recorded fresh
repeat to equal 0.0 before 0069 was written. Every figure of 0049 and 0069 stands. A reader checks the fresh
repeat by its recorded value against "exactly", not by the driver having run to the end.

**Before any further run of record.** No driver changes under this entry. A further run of record under 0047's controls
needs a driver that stops on any nonzero fresh-repeat error, apart from the prefix copy's {LIMIT}; that run is registered
in its own entry before it runs.

**What this does NOT touch.** No `verdict:` line; every cell as decided; every figure of 0049 and 0069; the drivers and
configs; both reports. Nothing runs under this entry.

**Consequences in this commit set.** The drafts README's allocator. Nothing under `results/`.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard {PREV} present, {NUM} absent.
Next free number after this entry: {NEXT}.

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

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print("[ordering guard: ok]")
    raise SystemExit(0)


# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included --------------------------------------
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
# --- the write, and after it: ledger_check, else the old bytes go back -------------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
