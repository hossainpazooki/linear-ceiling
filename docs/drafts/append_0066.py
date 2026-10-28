"""DRAFT append script for linear-ceiling: entry 0066 -- the conference cut WITHDRAWN. The submission of 2026-10-30 is not
made (operator ruling 2026-10-27); the workshop camera-ready (nine pages, due 2026-11-13) is the first public form of the
one paper covering both axes and draws on every figure an entry on this ledger states at ITS OWN cut (--cut-utc, set by
the operator at append). 0065's mechanism and 0060's table, invariants and conditions stand; the next reviewed venue takes
its own cut entry when chosen. Written venue-neutral: it cites 0060 and 0065 by number and never repeats the venue name.
DESCRIPTIVE: no `verdict:` line, no cell moves, nothing runs, no figure admitted by name.

PRIVATE DRAFT (briefs). To stage: run `0066-docs-patch.py --date D --cut-utc "YYYY-MM-DD HH:MM UTC"` (copies this file to
docs/drafts/append_0066.py and makes the living-doc edits), then from the repo root with .venv/Scripts/python.exe:
  --date YYYY-MM-DD  --cut-utc "YYYY-MM-DD HH:MM UTC"  --preview  [--repo-root <path>]
Ordering guard: 0065 present, 0066 absent. Every cited sentence is located by search inside its entry (refuses on 0 or 2+
hits); every line number is computed. Refuses until docs/paper-to-record.md names 0066 with the same cut and the drafts
README's last allocator line reads 0067. Runs `ledger_check` after appending. Delete once appended, chained with `&&`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--cut-utc", required=True, help='the camera-ready cut, e.g. "2026-11-10 16:00 UTC"')
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=None)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", a.cut_utc), '--cut-utc must be "YYYY-MM-DD HH:MM UTC"'
assert a.cut_utc[:10] < "2026-11-13", "the cut must precede the camera-ready deadline (2026-11-13)"
_here = Path(__file__).resolve().parents[2]
R = (a.repo_root or (_here if (_here / "ledger" / "ledger.md").exists() else Path.home() / "dev" / "linear-ceiling")).resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_text_file                    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM, NEXT = "0066", "0067"
MUST_EXIST = ("0006", "0060", "0065")
DEADLINE = "2026-11-13"
P2R = "docs/paper-to-record.md"
RECON = "docs/reviews/2026-10-07-submitted-camera-ready-reconciled-against-the-record-and-the-operator-runs.md"
AGENTS = "AGENTS.md"
DENY = "docs/2026-10-13-anonymity-denylist.md"

S_0060_MECH = "a figure that changes re-enters only through a later entry."
S_0065_DRAW = "may draw on every figure that an entry on this ledger states at the cut"
S_0065_AFTER = "After the cut a later entry's figure goes to the camera-ready or a later venue, never into the submission."
S_0065_STAND = "0060's table — every entry, line, figure and sha12 it names — remains admitted as stated"
S_0065_SIBLING = "a figure read by lag-ladder's ledger enters this paper's text through that ledger's own entries, never through this one"
S_AGENTS = ("A scientific figure or claim enters paper text only through the admitted evidence path: a ledger entry that "
            "states it, or a document a ledger entry explicitly admits for citation.")

LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {NUM} " not in text, f"ordering: {NUM} absent"
missing = [e for e in MUST_EXIST if f"### {e} " not in text]
assert not missing, f"ordering: {missing} must be on the ledger before {NUM}"


def block(t: str, entry: str) -> tuple[int, str]:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} header lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def line_of(t: str, offset: int) -> int:
    return t.count("\n", 0, offset) + 1


def locate(t: str, entry: str, sentence: str) -> int:
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


for rel in (P2R, RECON, AGENTS, DENY):
    assert (R / rel).exists(), f"{rel} missing"
L = {e: line_of(text, block(text, e)[0]) for e in MUST_EXIST}
l_mech = locate(text, "0060", S_0060_MECH)
l_draw = locate(text, "0065", S_0065_DRAW)
l_after = locate(text, "0065", S_0065_AFTER)
l_stand = locate(text, "0065", S_0065_STAND)
l_sib = locate(text, "0065", S_0065_SIBLING)
l_agents = locate_file(AGENTS, S_AGENTS)
recon_sha = sha256_text_file(R / RECON)
m65 = re.search(r"at the cut — (\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)", block(text, "0065")[1])
assert m65, "0065 does not state its cut as expected"
OLD_CUT = m65.group(1)

# the living documents this entry requires in its staging commit
p2r = (R / P2R).read_text(encoding="utf-8")
if not (re.search(rf"\b{NUM}\b", p2r) and a.cut_utc in p2r):
    assert a.preview, f"{P2R} does not name {NUM} with the cut {a.cut_utc}; the staging commit adds that"
    print(f"[preview] {P2R} does not yet name {NUM} with the cut; the staging commit adds it", file=sys.stderr)
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if f"`append_{NUM}.py`" not in readme or not free or free[-1] != NEXT:
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    print(f"[preview] drafts README allocator ends at {free[-1] if free else 'n/a'}; the staging block moves it to {NEXT}", file=sys.stderr)
deny = (R / DENY).read_text(encoding="utf-8")
if not re.search(r"Pattern: `[^`]*\|mlsys", deny, re.I):
    assert a.preview, f"{DENY} pattern does not yet carry the venue term; the staging commit adds it"
    print(f"[preview] {DENY} pattern lacks the venue term; the staging commit adds it", file=sys.stderr)

entry = f"""### {NUM} — {a.date} — The conference cut withdrawn: the submission 0065 cut for is not made; the workshop camera-ready (nine pages, due {DEADLINE}) is the one paper's first public form and draws on every figure an entry on this ledger states at its own cut ({a.cut_utc}); 0060's set, invariants and conditions stand; descriptive, no cell moves

**What this entry is.** 0065 (line {L['0065']}) replaced 0060's entry-number freeze with a date cut for a conference submission
(line {l_draw}: an entry on this ledger "{S_0065_DRAW}" — {OLD_CUT}). **That submission is not made** (operator ruling
{a.date}: the full text of the one paper, both axes, could not be written in the days that remained, and a partial text
that could not cite its own weights-axis sections would not be the paper). This entry withdraws the {OLD_CUT} cut and sets
the next one. The first public form of the one paper is the workshop camera-ready — the successor of the submitted text
reconciled at `{RECON}` (`{recon_sha[:12]}…`) — nine pages, due {DEADLINE}, non-anonymous, non-archival. **It may draw on
every figure that an entry on this ledger states at {a.cut_utc}**, each figure as its summary file states it, with the
file's sha, entering paper text only by the admitted evidence path (`{AGENTS}` line {l_agents}: "{S_AGENTS}"). A staged
script that has not appended admits nothing. The next reviewed venue takes its own cut entry when it is chosen; nothing
is said about it here. Nothing is measured here.

**What stands.** 0060's mechanism, which 0065 kept (line {l_mech}: "{S_0060_MECH}"), is the mechanism this entry uses.
0060's table remains admitted as 0065 stated it (line {l_stand}); its wording invariants bind the camera-ready as they bound
the submission; its conditions stand as written. 0065's sentence on the sibling record stands (line {l_sib}): a figure read
by the holdover ledger enters the paper through that ledger's own entries, never through this one, and the camera-ready's
cut applies to both ledgers by date. 0065's "{S_0065_AFTER}" (line {l_after}) is superseded only in its last clause: there
is no submission for a later figure to be kept out of; a figures entry appended after {a.cut_utc} is material for the full
paper at the next venue.

**The record and the venue.** The living documents of this repository name no venue from this entry on ("the conference
submission", "the full paper"); the appended entries that name one (0060, 0065) are immutable and stay as written, as does
every dated record. The anonymity list (`{DENY}`) gains the venue term in its pattern so that any future double-blind
mirror is venue-free; the camera-ready itself is non-anonymous and needs no mirror. The camera-ready's appendix tells the
venue history in the record's own words, by entry number (0060, 0065, this entry), so a reader of the public record and a
reader of the paper find the same account.

**What this does NOT touch.** No `verdict:` line; every cell as decided; τ_K, τ_V, τ_agent_K, the band, the ladder, the kept
dumps; 0060's table and invariants; the registrations 0061–0064 and their figures entries, which enter the camera-ready if
on the ledger at the cut and the full paper otherwise. No figure is admitted by name. Nothing runs under this entry.

**Consequences in this commit set.** `{P2R}` (the figure-set section names this entry and the cut); `README.md`, `CLAUDE.md`,
`docs/README.md` (venue-neutral wording); `{DENY}` (status paragraph; the venue term in the pattern); a status line atop
`docs/paper/2026-10-08-mlsys-draft-plan-and-second-pair-section.md` (superseded as a venue plan; its delta table stands;
the page budget is the camera-ready's nine pages); the drafts README's allocator. Nothing under `results/`.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard 0065 present, {NUM} absent.
Next free number after this entry: {NEXT}.

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
