"""DRAFT append script for linear-ceiling: entry 0065 -- the MLSys 2027 cut RESTATED. 0060's sentence "Nothing registered
after this entry enters the submission" is WITHDRAWN; its second sentence ("a figure that changes re-enters only through
a later entry") is kept as the mechanism this entry uses. New rule: the submission may draw on every figure that an entry
ON THIS LEDGER AT THE CUT (2026-10-29 16:00 UTC) states, each read from its summary file by sha, through AGENTS.md's
admitted evidence path. 0060's table, wording invariants and conditions stand. DESCRIPTIVE: no `verdict:` line, no cell
moves, nothing runs, no figure admitted by name.

PRIVATE DRAFT (briefs). To stage: copy to docs/drafts/append_0065.py, add the allocator block to docs/drafts/README.md and
the one-sentence restatement to docs/paper-to-record.md (this script refuses to append until that page names 0065), then
from the repo root with .venv/Scripts/python.exe:  --date YYYY-MM-DD  --preview  [--repo-root <path>]
Ordering guard: 0061, 0062, 0063, 0064 present, 0065 absent (0064 is the MLPerf registration whose sentence on the shared
token file this entry locates). Every cited sentence is located by search inside its entry (refuses on 0 or 2+ hits);
every line number is computed, never typed; the one outside-repository fact (lag-ladder's entry 0036) is read from the
sibling clone's ledger when present and marked unverified otherwise. Runs `ledger_check` after appending. Delete once
appended, chained to the append with `&&`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=None)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
_here = Path(__file__).resolve().parents[2]
R = (a.repo_root or (_here if (_here / "ledger" / "ledger.md").exists() else Path.home() / "dev" / "linear-ceiling")).resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_text_file                    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM = "0065"
MUST_EXIST = ("0006", "0060", "0061", "0062", "0063", "0064")
CUT_UTC, CUT_LOCAL, DEADLINE = "2026-10-29 16:00 UTC", "09:00 PDT", "2026-10-30 19:00 UTC (noon PDT)"
PLAN = "docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md"
P2R = "docs/paper-to-record.md"
RECON = "docs/reviews/2026-10-07-submitted-camera-ready-reconciled-against-the-record-and-the-operator-runs.md"
AGENTS = "AGENTS.md"
LL = R.parent / "lag-ladder" / "ledger" / "ledger.md"            # the sibling clone; read-only, present on the operator's machines

# the sentences this entry rests on, quoted from the record and LOCATED, never retyped into the entry
S_FREEZE = "Nothing registered after this entry enters the submission; a figure that changes re-enters only through a later entry."
S_RECON = "The manuscript tree and its commit are pinned at submission by the reconciliation record"
S_GATE = "0006's gate restated: only numbers that recompute clean from `results/` via a fail-closed summarizer enter."
S_MANUSCRIPT = "are manuscript matters."
S_0064_FILE = "the token file lag-ladder's entry 0030 reads under the seed-1 readers"
S_0064_NOT = "0060 and the frozen figure set."
S_PLAN = "the paper cites the ENTRY if it lands before the freeze, else the subsection stays descriptive and Limitations says so"
S_AGENTS = ("A scientific figure or claim enters paper text only through the admitted evidence path: a ledger entry that "
            "states it, or a document a ledger entry explicitly admits for citation.")
S_LL_0036 = "the reading lands with held-out text, not with the trainer's prompts"

LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {NUM} " not in text, f"ordering: {NUM} absent"
missing = [e for e in MUST_EXIST if f"### {e} " not in text]
if missing and a.preview:
    print(f"[preview] not yet on this ledger: {missing}; the append refuses until they are", file=sys.stderr)
else:
    assert not missing, f"ordering: {missing} must be on the ledger before {NUM}"


def block(t: str, entry: str) -> tuple[int, str]:
    """(0-based start offset, text) of the `### <entry> ` block; refuses on 0 or 2+ header lines."""
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} header lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def line_of(t: str, offset: int) -> int:
    return t.count("\n", 0, offset) + 1


def locate(t: str, entry: str, sentence: str) -> int:
    """1-based ledger line where `sentence` starts inside `entry` (whitespace-insensitive); refuses on 0 or 2+ hits."""
    start, b = block(t, entry)
    pat = re.compile(r"\s+".join(re.escape(w) for w in sentence.split()))
    hits = list(pat.finditer(b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {sentence[:50]!r}"
    return line_of(t, start + hits[0].start())


def locate_file(rel: str, sentence: str) -> int:
    body = (R / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
    pat = re.compile(r"\s+".join(re.escape(w) for w in sentence.split()))
    hits = list(pat.finditer(body))
    assert len(hits) == 1, f"{rel}: {len(hits)} hits for {sentence[:50]!r}"
    return line_of(body, hits[0].start())


def soft(fn, *args, what: str):
    """Run a locator; in preview a miss is a warning and returns None, at append it refuses."""
    try:
        return fn(*args)
    except AssertionError as e:
        assert a.preview, str(e)
        print(f"[preview] {what}: {e}; the append refuses until it holds", file=sys.stderr)
        return None


for rel in (PLAN, P2R, RECON, AGENTS):
    assert (R / rel).exists(), f"{rel} missing"
L = {e: (line_of(text, block(text, e)[0]) if f"### {e} " in text else None) for e in MUST_EXIST}
l_freeze = locate(text, "0060", S_FREEZE)
l_recon = locate(text, "0060", S_RECON)
l_gate = locate(text, "0060", S_GATE)
l_manu = locate(text, "0060", S_MANUSCRIPT)
l_0064_file = soft(locate, text, "0064", S_0064_FILE, what="0064's shared-token-file sentence")
l_0064_not = soft(locate, text, "0064", S_0064_NOT, what="0064's not-touched sentence")
l_plan = locate_file(PLAN, S_PLAN)
l_agents = locate_file(AGENTS, S_AGENTS)
plan_sha, recon_sha = sha256_text_file(R / PLAN), sha256_text_file(R / RECON)
p2r = (R / P2R).read_text(encoding="utf-8")
if not re.search(rf"\b{NUM}\b", p2r):
    assert a.preview, f"{P2R} does not name {NUM}; the staging commit adds the restatement sentence"
    print(f"[preview] {P2R} does not yet name {NUM}; the staging commit adds the one-sentence restatement", file=sys.stderr)
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
NEXT = f"{int(NUM) + 1:04d}"           # once this script is staged the allocator's last line names the number after it
if f"`append_{NUM}.py`" not in readme or not free or free[-1] != NEXT:
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT} (last: {free[-1] if free else 'none'})"
    print(f"[preview] drafts README allocator ends at {free[-1] if free else 'n/a'}; the {NUM} staging block moves it to {NEXT}", file=sys.stderr)
# the sha of the draft plan that 0060 cited, read from 0060's own text (the plan was revised after the freeze)
m_plan0060 = re.search(r"the draft plan is `" + re.escape(PLAN) + r"` \(`([0-9a-f]{12})…`\)", block(text, "0060")[1])
assert m_plan0060, "0060 does not cite the draft plan's sha as expected"
plan_sha_0060 = m_plan0060.group(1)
assert plan_sha_0060 != plan_sha[:12], "the plan is unchanged since 0060; the 'revised after the freeze' sentence would be false"

# the one outside fact: lag-ladder's 0036 read the same fifty windows (primary source: its ledger; retrieval date: the run date)
if not LL.exists():
    assert a.preview, "../lag-ladder clone absent; the append refuses rather than record an unverified sentence"
    print("[preview] ../lag-ladder clone absent; the append refuses until it is present", file=sys.stderr)
    ll_note = "UNVERIFIED IN PREVIEW: sibling clone absent"
else:
    llt = LL.read_text(encoding="utf-8").replace("\r\n", "\n")
    s36, b36 = block(llt, "0036")
    m = re.search(r"^prior-entries-sha256: ([0-9a-f]{64})\s*$", b36, re.M)
    assert m, "lag-ladder 0036 carries no chain line"
    pat = re.compile(r"\s+".join(re.escape(w) for w in S_LL_0036.split()))
    assert len(pat.findall(b36)) == 1, "lag-ladder 0036 does not state the lands-with sentence exactly once"
    ll_head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=LL.parents[1], capture_output=True, text=True)
    assert ll_head.returncode == 0, "lag-ladder clone is not a git tree"
    import hashlib
    ll_block_sha = hashlib.sha256(b36.encode("utf-8")).hexdigest()[:12]
    ll_note = (f"its ledger's entry 0036 — clone HEAD `{ll_head.stdout.strip()}`, entry text sha12 `{ll_block_sha}`, its chain line "
               f"`{m.group(1)[:12]}…` covering the entries before it — which states in those words that \"{S_LL_0036}\"; "
               f"read from the sibling clone on {a.date}")


def ln(x):
    return "line n/a" if x is None else f"line {x}"


entry = f"""### {NUM} — {a.date} — MLSys 2027 cut, restated: 0060's "nothing registered after this entry enters the submission" withdrawn; the submission draws on every figure an entry on this ledger states at the cut ({CUT_UTC}), read from its summary file; 0060's set, invariants and conditions stand; descriptive, no cell moves

**What this entry is.** 0060 ({ln(L['0060'])}) froze the figure set on 2026-10-10 in two sentences ({ln(l_freeze)}): "{S_FREEZE}"
This entry **withdraws the first sentence and keeps the second**, which is the mechanism it uses. The rule from here: **the
MLSys 2027 submission may draw on every figure that an entry on this ledger states at the cut — {CUT_UTC} ({CUT_LOCAL};
the deadline is {DEADLINE})** — each figure as its summary file states it, with the file's sha, entering paper text
only by the admitted evidence path (`{AGENTS}` line {l_agents}: "{S_AGENTS}"). A staged script that has not
appended admits nothing. 0060's gate stands as written ({ln(l_gate)}): "{S_GATE}" The commit at which the ledger
stood at the cut is pinned by the reconciliation record at submission, as 0060 already provides ({ln(l_recon)}; the
camera-ready precedent `{RECON}`, `{recon_sha[:12]}…`). After the cut a later entry's figure goes to the camera-ready
or a later venue, never into the submission. Nothing is measured here.

**Why the freeze moves from an entry number to a date.** Four registrations were drafted for this submission after
0060, on the operator's rulings of 2026-10-13 and 2026-10-22: 0061 ({ln(L['0061'])}), 0062 ({ln(L['0062'])}), 0063 ({ln(L['0063'])}) and 0064
({ln(L['0064'])}). The draft plan as revised after the freeze (`{PLAN}`, now `{plan_sha[:12]}…`; 0060 cited it at
`{plan_sha_0060}…`) names 0061 in its E-BEH row and conditions the band on the freeze in words that presume a date, not a
number (line {l_plan}: "{S_PLAN}"). The plan and the freeze have disagreed since that revision; this entry repairs the record
by rule rather than by naming figures that have not been read. The gate
"appended before the cut" is one the reconciliation record can check against a commit; "registered before 0060" cannot
be checked against a deadline. Third, the benchmark anchor: 0064 registers E8 on the MLPerf Agentic Inference windows and
states ({ln(l_0064_file)}) that its Qwen token file is, id for id, {S_0064_FILE}; lag-ladder has read the windows 0064 draws
(its n = 50) under its readers ({ll_note}). A figure set that could admit neither half would leave the paper's one benchmark
cell outside its own record.

**What stands.** 0060's table — every entry, line, figure and sha12 it names — remains admitted as stated; its wording
invariants bind the submission unchanged; its conditions stand as it wrote them (the L32-native E-TRUNC cell it carried is
now registered by 0062 and enters, like every other cell, only through a figures entry on the ledger before the cut).
0060's sentence that reviewer nits N1 and N2 "{S_MANUSCRIPT.rstrip('.')}" ({ln(l_manu)}) is kept and extended: a figure read by
lag-ladder's ledger enters this paper's text through that ledger's own entries, never through this one; a join of the two
records on the MLPerf windows (0064's mapper reading beside lag-ladder's reader reading, window by window) is a figure with
no verdict, recomputed from both summary files by sha, and is stated by this ledger only in the entry that reads 0064's run.

**What this does NOT touch.** No `verdict:` line; every cell as decided; τ_K, τ_V, τ_agent_K, the band, the ladder, the kept
dumps; 0060's table and invariants; 0064's own "does not touch" clause ({ln(l_0064_not)}) remains true of 0064. No figure is
admitted by name: 0061–0064 admit figures only through their own figures entries, each read from its summary file, each
on the ledger before the cut or not in the submission at all. Nothing runs under this entry.

**Consequences in this commit set.** `{P2R}` ("The MLSys figure set") gains one sentence pointing at this entry; the
drafts README's allocator. Nothing under `results/`.

**Numbering.** {NUM} is the number the drafts README allocates at staging, after 0064's script is staged; ordering guard 0061, 0062, 0063 and 0064 present, {NUM} absent.
Next free number after this entry: 0066.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(entry)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + entry
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
