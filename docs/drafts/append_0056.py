"""Append entry 0056 -- co-author pilot figures admitted to paper text by operator ruling (2026-10-04). DESCRIPTIVE:
records a ruling and its basis; no hypothesis row, no `verdict:` line, no cell moves. It TYPES NO FIGURE: the paper cites
the two co-author documents by path and hash, and this entry records that it may.

What it supersedes: the clause in 0046 and in 0047 that "no figure from the pilot is stated here or in any paper" until
the pilot's bundle is published and recomputed under `docs/2026-10-03-co-author-run-admission.md`. The operator ruled:
figures posted by the co-author, with the code and the environment on the record (merged tree + PR comments naming the
execution commits), may be cited in the paper under a provenance sentence that states who ran it, where, at which commit,
and that the raw bundle is not public and has not been recomputed by anyone else. R1, R8 and R12 of the GPU protocol are
NOT changed for ledger entries; this ruling is about paper text citing co-author documents, and the entries that will
carry these experiments' figures on the ledger (0048, 0049) still require the operator's registered run or the admission
procedure.

Numbering: 0055 is the E-TRUNC registration (staged on branch `e-trunc`); this entry takes 0056. Appended now, so it
precedes the staged 0048-0051, 0053 and 0055 in file order (0052 and 0054 are already appended, in that file order: 0054, 0052); `ledger_check` chains by file order. Guard: 0054 present, 0056 absent.

  --date YYYY-MM-DD   --preview
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.hashing import sha256_text_file                 # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, LAST = "0056", "0054"
DOCS = {  # path -> (sha256 of the LF bytes on main at write time, merge commit, PR, the co-author's reproduction comment)
    "docs/2026-10-01-cache-behavior-h100.md": ("81ad2740a3457507", "b26dfdb", "#14",
                                               "https://github.com/hossainpazooki/linear-ceiling/pull/14#issuecomment-5977021295"),
    "docs/2026-10-01-a100-analysis.md": ("cf27e75069f9fe04", "c7911a4", "#9",
                                         "https://github.com/hossainpazooki/linear-ceiling/pull/9#issuecomment-5977015570"),
}
FREEZE = ("docs/2026-10-01-cache-behavior-freeze.json", "cff700063b6c3fd5")
EXEC = {"cache-behavior": "9a18ce7", "consolidation": "2fb4464"}

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date)

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {LAST} " in text and f"### {NUM} " not in text, f"ordering: {LAST} present, {NUM} absent"
assert text.count("no figure from the pilot is") == 1 and text.count("No figure from it is stated") == 1, \
    "the two superseded clauses (0046, 0047) are not where this entry says"
for rel, (sha16, *_rest) in DOCS.items():
    p = REPO_ROOT / rel
    assert p.exists(), f"{rel} missing"
    assert sha256_text_file(p).startswith(sha16), f"{rel} differs from the document the ruling admitted"
assert sha256_text_file(REPO_ROOT / FREEZE[0]).startswith(FREEZE[1])
h100 = (REPO_ROOT / "docs/2026-10-01-cache-behavior-h100.md").read_text(encoding="utf-8")
a100 = (REPO_ROOT / "docs/2026-10-01-a100-analysis.md").read_text(encoding="utf-8")
assert "not an admitted upstream E-BEH result" in h100 and EXEC["cache-behavior"] in h100
assert "have not yet been published to a public dataset" in a100, "the a100 document's own disclosure is gone"

ENTRY = f"""### {NUM} — {a.date} — Co-author pilot figures admitted to paper text by operator ruling: the two merged co-author documents may be cited under a provenance sentence; supersedes the "in any paper" clauses of 0046 and 0047; the ledger's evidence rules unchanged; descriptive, no cell moves

**What 0046 and 0047 said.** Each registered a co-author's fork run as the PILOT of the experiment it registered and
said: no figure from the pilot is stated in the entry or in any paper until the pilot's bundle is published to the Hub
and recomputed under `docs/2026-10-03-co-author-run-admission.md`.

**The ruling (operator, 2026-10-04).** Figures the co-author has posted in the repository, with the code and the
environment on the record, may be cited in paper text. The record is: `docs/2026-10-01-cache-behavior-h100.md`
(`{DOCS['docs/2026-10-01-cache-behavior-h100.md'][0]}…`, merged {DOCS['docs/2026-10-01-cache-behavior-h100.md'][1]} by PR {DOCS['docs/2026-10-01-cache-behavior-h100.md'][2]}; execution commit `{EXEC['cache-behavior']}`, freeze record
`{FREEZE[0]}` `{FREEZE[1]}…`, driver `tools/cache_behavior/`, environment torch 2.14.0 / transformers 5.17.0 / CUDA 13.0 on
one H100 PCIe 80 GB; the co-author's reproduction comment {DOCS['docs/2026-10-01-cache-behavior-h100.md'][3]}) for the W1
figures, and `docs/2026-10-01-a100-analysis.md` (`{DOCS['docs/2026-10-01-a100-analysis.md'][0]}…`, merged {DOCS['docs/2026-10-01-a100-analysis.md'][1]} by PR {DOCS['docs/2026-10-01-a100-analysis.md'][2]}; results commit `{EXEC['consolidation']}`,
driver `tools/consolidation/`, `requirements-linux.lock`, input manifest `config/consolidation-manifest.json`, one
A100-SXM4-80GB; comment {DOCS['docs/2026-10-01-a100-analysis.md'][3]}) for the W7 figures. **This entry types none of
those figures**: the paper cites the documents, and the documents are the co-author's.

**The provenance sentence the citation must carry**, in substance: run by a co-author on the named card at the named
commit with the pinned environment; code, input manifest and environment are in this repository; the raw evidence
bundle is on the co-author's machine, not public, and the figures have not been recomputed by anyone else. The a100
document says so itself ("have not yet been published to a public dataset; do not claim …"); the h100 document says it
is "not an admitted upstream E-BEH result". The paper repeats both.

**What this does NOT change.** R1, R8 and R12 of `docs/gpu-experiment-protocol.md` for ledger entries: the figures of
these two experiments enter the LEDGER only by 0048 / 0049 from the operator's registered run, or by the admission
procedure once the bundles are public. The standing sentence "No downstream task-quality number is claimed" (0047): a
top-1 agreement is not task accuracy. Every verdict and cell; τ, the rule, the bands; 0054's ruling on Condition 1.
Entry 0054's precedent is extended, not widened: 0054 ruled on who approves a review; this entry rules on what paper
text may cite, and leaves what the ledger may record untouched.

**Scope.** Two documents, two experiments (W1 cache behavior; W7 same-model extension), one paper lane. A reviewer
pressing on the evidential gap is answered by the provenance sentence, not by this entry.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
