"""DRAFT append script for linear-ceiling: an erratum to entry 0049. Two sentences of 0049's controls paragraph are
corrected and no figure moves: its two numerical controls ran on one handoff, not "over all scored handoffs", and the
driver, not the reader, stops on a failed archive bridge. The number is the ledger's next, 0073 after 0072.
DESCRIPTIVE: no `verdict:` line, no cell moves, nothing runs.

Every line number and value in the entry is computed here, read-only: the lines of the sentences on this ledger (the
tree's, LF-normalized); the report and the inputs manifest of 0049's run and the report of 0069's run, under `results/`,
each pinned by sha256 and each sha's prefix as the entry that pins it states it; the driver 0049 ran, read with `git show`
at the commit 0049 names, pinned by sha256, and the lines of its control, ordering, bridge and record steps.

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
RUN_COMMIT = "7c9a5fd34c2df70c66269f755a61a882440e4f79"                 # 0049: "run at commit `7c9a5fd`"
DRIVER = "tools/cache_behavior/run.py"
DRIVER_SHA = "15e1ff8c1dbc7925398edc11ed68d91b6cdba4f335a49adcb29baa1b10729de5"   # 0049: "`run.py` `15e1ff8c1dbc…`"
REPORT49 = "results/cache-behavior/report.json"
REPORT49_SHA = "3564605773bb3751d9e0e842fcbf238cd41e662a7f93a1442902a61c0ca56f14"  # 0049: "`report.json` `3564605773bb…`"
MANIFEST49 = "results/cache-behavior/inputs/manifest.json"
MANIFEST49_SHA = "2aeee5769c0a3b557e1fecd43c2a745abe9f29c37af66b0eabb54358b4c35b22"  # 0049: "their manifest is `2aeee5769c0a…`"
REPORT69 = "results/cache-behavior-repair/report.json"
REPORT69_SHA = "21b62a01a504f66421cd1d452c14eed5c8b07c6a6d630d9f64d670cd86d6c9f9"  # 0069: "`21b62a01a504…`"
LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
S49_CTRL = ("fresh-repeat maximum logit error 0.00e+00, prefix-copy maximum logit error 2.90e-04 (limit 5e-4), "
            "over all scored handoffs.")
S49_BRIDGE = "Every per-handoff archive bridge passed, or the reader would have refused."
S69_CTRL = "on the probe handoff, the only one that carries the two controls."
S69_BRIDGE = "Every per-handoff archive bridge passed, or the driver would have stopped before scoring that handoff."
S47_PROBE = "The largest sender is scored first as the retained memory probe."


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


def once(t: str, entry: str, phrase: str) -> tuple:
    """(offset in t, 'line N' or 'lines N-M') of the phrase, which must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(loose(phrase).finditer(b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {phrase[:60]!r}"
    l0, l1 = line_of(t, start + hits[0].start()), line_of(t, start + hits[0].end() - 1)
    return start + hits[0].start(), (f"line {l0}" if l0 == l1 else f"lines {l0}-{l1}")


def pinned(t: str, entry: str, prefix: str) -> None:
    assert len(prefix) >= 12 and re.search(rf"`{prefix[:12]}…`", block(t, entry)[1]), f"{entry} does not pin `{prefix[:12]}…`"


# --- this ledger: the tree's, the ordering ------------------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0072", f"the ledger's last entry is {PREV}, not 0072"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
for e in ("0047", "0049", "0069"):
    assert e in heads, f"ordering: {e} must be on the ledger"
L49 = line_of(text, block(text, "0049")[0])
L69 = line_of(text, block(text, "0069")[0])
assert re.match(r"### 0049 — \d{4}-\d{2}-\d{2} — Cache-behavior comparison ran ", block(text, "0049")[1]), "0049 is not the cache-behavior run"
assert re.match(r"### 0069 — \d{4}-\d{2}-\d{2} — Cache-behavior REPAIR ran ", block(text, "0069")[1]), "0069 is not the repair run"
o_ctrl, W_CTRL = once(text, "0049", S49_CTRL)
o_bridge, W_BRIDGE = once(text, "0049", S49_BRIDGE)
assert o_ctrl < o_bridge and "\n\n" not in text[o_ctrl:o_bridge], "0049's two sentences are not one paragraph, in this order"
_, W69_CTRL = once(text, "0069", S69_CTRL)
_, W69_BRIDGE = once(text, "0069", S69_BRIDGE)
_, W47_PROBE = once(text, "0047", S47_PROBE)
b49 = block(text, "0049")[1]
assert f"run at commit `{RUN_COMMIT[:7]}`" in b49, "0049 does not name the run commit"
pinned(text, "0049", DRIVER_SHA)
pinned(text, "0049", REPORT49_SHA)
pinned(text, "0049", MANIFEST49_SHA)
pinned(text, "0069", REPORT69_SHA)
for later in sorted(h for h in heads if int(h) > 49):
    assert not loose("over all scored handoffs").search(block(text, later)[1]), f"{later} already restates or corrects 0049's sentence"

# --- the raw records: 0049's report and inputs manifest, 0069's report ----------------------------------------------------------
rb49 = (R / REPORT49).read_bytes()
assert sha(rb49) == REPORT49_SHA, f"{REPORT49} is not the file 0049 pins"
mb49 = (R / MANIFEST49).read_bytes()
assert sha(mb49) == MANIFEST49_SHA, f"{MANIFEST49} is not the manifest 0049 names"
rb69 = (R / REPORT69).read_bytes()
assert sha(rb69) == REPORT69_SHA, f"{REPORT69} is not the file 0069 pins"
r49, m49, r69 = json.loads(rb49), json.loads(mb49), json.loads(rb69)
assert r49.get("git_commit") == RUN_COMMIT, "0049's report does not record the run commit 0049 names"
assert r49.get("identity", {}).get("code_sha256", {}).get("run.py") == DRIVER_SHA, "0049's report does not record the driver 0049 pins"


def controls_shape(r: dict, name: str) -> tuple:
    """(scored count, the one handoff with controls, its fresh-repeat and prefix-copy maximum logit errors)."""
    s, order = r["scores"], r["run_order"]
    assert r["complete"] is True and list(s) == order, f"{name}: not complete, or scored out of run order"
    carry = [h for h, v in s.items() if v["controls"]]
    assert carry == [order[0]], f"{name}: the controls are on {carry}, not on the first handoff of the run order alone"
    assert all(v["controls"] == {} for h, v in s.items() if h != order[0]), f"{name}: a handoff other than the first has a control"
    c = s[order[0]]["controls"]
    assert set(c) == {"fresh_repeat", "prefix_copy"}, f"{name}: the first handoff's controls are {sorted(c)}"
    return len(s), order[0], c["fresh_repeat"]["max_logit_error"], c["prefix_copy"]["max_logit_error"]


N49, PROBE, FR49, PC49 = controls_shape(r49, REPORT49)
N69, PROBE69, FR69, PC69 = controls_shape(r69, REPORT69)
assert N49 == N69 == 35 and PROBE69 == PROBE and (FR69, PC69) == (FR49, PC49), "0069's report does not have 0049's shape and values"
assert f"{FR49:.2e}" == "0.00e+00" and f"{PC49:.2e}" == "2.90e-04", "the report's two values are not 0049's figures"
assert re.search(rf"\b{N49} of {N49} handoffs scored", b49), f"0049 does not state {N49} of {N49} handoffs scored"
included = [row for row in m49["records"] if not row["excluded"]]
largest = max(included, key=lambda row: row["sender_tokens"])
assert sum(1 for row in included if row["sender_tokens"] == largest["sender_tokens"]) == 1, "the largest sender is tied"
assert largest["handoff"] == PROBE and len(included) == N49, "the first handoff is not the manifest's largest sender"

# --- the driver 0049 ran, at its commit ---------------------------------------------------------------------------------------
assert subprocess.run(["git", "-C", str(R), "merge-base", "--is-ancestor", RUN_COMMIT, "HEAD"], env=ENV).returncode == 0, \
    "0049's run commit is not an ancestor of HEAD"
drv_b = git("show", f"{RUN_COMMIT}:{DRIVER}")
assert sha(drv_b) == DRIVER_SHA, f"{DRIVER} at {RUN_COMMIT[:7]} is not the blob 0049 pins"
drv = drv_b.decode("utf-8")
assert "\r" not in drv, "the driver blob is not LF"


def dline(pattern: str) -> int:
    hits = [m.start() for m in re.finditer(pattern, drv, re.M)]
    assert len(hits) == 1, f"driver: {len(hits)} hits for {pattern!r}"
    return line_of(drv, hits[0])


D_ORDER0 = dline(r'^    largest = max\(included, key=lambda row: row\["sender_tokens"\]\)$')
D_ORDER1 = dline(r'^    return \[largest\] \+ \[row for row in included if row != largest\]$')
D_LOOP = dline(r'^    for index, record in enumerate\(order\[:1\] if args\.probe else order\):$')
D_ORD = dline(r'^    order = ordered_records\(manifest\)$')
D_IF0 = dline(r'^        if index == 0:$')
D_CTRL = dline(r'^                raise ValueError\(f"fresh/prefix identity control failed: \{controls\}"\)$')
D_BR0 = dline(r'^        for key in \("K", "V"\):$')
D_BR1 = dline(r'^                raise ValueError\(f"archive/runtime deviation bridge failed: ')
D_ARMS = dline(r'^        for arm, fraction in arm_fractions:$')
D_REC = dline(r'^        report\["scores"\]\[hid\] = ')
D_SUM0 = dline(r'^def summarize\(')
D_SUM1 = dline(r'^def run\(') - 1
while not drv.split("\n")[D_SUM1 - 1].strip():
    D_SUM1 -= 1                                      # summarize's last line, not the blank lines after it
assert D_ORDER0 + 1 == D_ORDER1 < D_SUM0 < D_SUM1 < D_ORD < D_LOOP < D_IF0 < D_CTRL < D_BR0 < D_BR1 < D_ARMS < D_REC, \
    "the driver's steps are not in the order this entry states"
_if0_body = drv.split("\n")[D_IF0:D_CTRL]           # the lines after `if index == 0:`, to the control raise
assert all(ln.startswith(" " * 12) or not ln.strip() for ln in _if0_body), "the control raise is not inside `if index == 0:`"
_loop = drv.split("\n")[D_LOOP:D_REC]
assert all(ln.startswith(" " * 8) or not ln.strip() for ln in _loop), "the bridge check is not inside the per-handoff loop"
_sum = "\n".join(drv.split("\n")[D_SUM0 - 1:D_SUM1])
assert "bridge" not in _sum and "control" not in _sum, "summarize checks a bridge or a control"
assert "max_logit_error" in drv.split("\n")[D_CTRL - 2], "the line before the control raise is not the limit check"

# --- the drafts README stages this script --------------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
staged_readme = f"`append_{NUM}.py`" in readme and bool(free) and free[-1] == NEXT
if not a.preview:
    assert staged_readme, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"

# --- the entry ----------------------------------------------------------------------------------------------------------------
RAW = f"""### {NUM} — {a.date} — Erratum to 0049: its two numerical controls ran on one handoff, not on all scored handoffs, and its driver, not its reader, stops on a failed archive bridge; no figure moves

**The controls.** 0049 (line {L49}) reads: "{S49_CTRL}" ({W_CTRL}). Its `report.json` (`{REPORT49_SHA[:12]}…`)
carries the two controls on one of its {N49} scored handoffs, the first in its run order (`{PROBE}`); the other
{N49 - 1} carry none. The driver 0049 ran (`{DRIVER}` `{DRIVER_SHA[:12]}…` at `{RUN_COMMIT[:7]}`) puts the handoff
with the most sender tokens first (lines {D_ORDER0}-{D_ORDER1}), as 0047 registered ("{S47_PROBE}", {W47_PROBE}),
computes both controls on that handoff alone (lines {D_IF0}-{D_CTRL}), and stops if either exceeds the limit. The two
figures are that handoff's, and they stand. "Over all scored handoffs" is withdrawn: the sentence reads "{S69_CTRL[:-1]}",
as 0069 (line {L69}) states the same controls for its own run ({W69_CTRL}), whose `report.json`
(`{REPORT69_SHA[:12]}…`) carries them on the same handoff alone, with the same two values.

**The archive bridge.** 0049 continues: "{S49_BRIDGE}" ({W_BRIDGE}). The reader, `run.summarize` (lines
{D_SUM0}-{D_SUM1}), checks no bridge. The driver checks the bridge on every handoff (lines {D_BR0}-{D_BR1}), before it
scores that handoff's arms (line {D_ARMS}) and writes its record (line {D_REC}), and stops on a failure. The sentence
reads "or the driver would have stopped before scoring that handoff", as in 0069 ({W69_BRIDGE}). All {N49} handoffs
scored, so every bridge passed.

**What this does NOT touch.** No `verdict:` line; every cell as decided; every figure of 0049 and 0069; 0047's
registered limits; both reports. Nothing runs under this entry.

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
