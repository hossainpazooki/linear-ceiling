"""Entry 0017 -- composio adapter defect + headroom measure correction. Supersedes the FIGURES of
0013 and 0015's H-E7a ratio (verdicts unchanged). Run ONLY after 0016 exists.
usage (repo root): .venv/Scripts/python.exe docs/drafts/append_0017.py <date YYYY-MM-DD>"""
import hashlib
import re
import sys
from pathlib import Path

LEDGER = Path("ledger/ledger.md")
DATE = sys.argv[1]
ENTRY = f"""### 0017 — {DATE} — Composio adapter read half the family wrong; the headroom measure's `paid` was not the receiver's prefill. Figures of 0013 and 0015's ratio `[SUPERSEDED]`; verdicts stand

Found 2026-09-02 while building E9's alignment (a receiver prompt of median 685 tokens against a
sender context of 16,675 could not be "the whole transcript re-rendered"). Three defects, all in
the instrument, none in a registered rule:

**(1) A second shape inside the composio family.** The 20241016 submission lists LangChain message
nodes directly inside each sub-run. The 20241025 submission nests each sub-run's entire prompt as
ONE LIST node before the `LLMResult`. The adapter skipped non-dict nodes, so for 30 of the 60
files it read seven responses per file and no prompt at all: their tokens never entered the cost
totals, Lane A slices, or headroom. Detector breadth (0010) was not the failure; shape breadth
was. Fix: `e7_swe._flatten_nodes` -- nesting is flattened at any depth and nothing that is a dict
is dropped; a test pins the nested shape.

**(2) `paid` was the trajectory's cumulative prefix, not the receiver's prefill.** Entry 0010
defines `paid` as "the second stage's prefill tokens". The implementation summed every message
before the receiving turn -- three Claude solve threads plus the o1-mini prompt, ~6x the prompt
the o1-mini call was billed for. Fix: `Msg.request` records the request (LangChain sub-run) a
message belongs to; the receiver's prefill is the tokens of ITS request's messages preceding its
response; `measure` REFUSES a switch whose trace records no request boundary rather than fall
back to the prefix. The sender's processed content is unchanged (everything before the switch).

**(3) Messages were concatenated without a separator**, fusing the last word of one message with
the first of the next before whitespace tokenization. Fix: newline join. Minor; recorded because
the number moved.

**What is superseded.** Entry 0013's corpus row for composio and its headroom table (paid median
19,972; overlap 0.903; upper bound 81.3% of paid) are `[SUPERSEDED]` as figures -- the entry's
registration text and its provenance discipline stand. Entry 0015's H-E7a numerator, denominator
and ratio (2,339,562 / 165,959,914 = 1.41%) are `[SUPERSEDED]` as figures. **Neither verdict
changes**: H-E7a stays `NOT CONFIRMED` and H-E7b `UNESTIMABLE`; 0015's taxonomy class counts for
composio (68 switches, 68 re-renders, 60 of 60) are unaffected by (1)-(3) and stand.

**Recon, stated as recon** (fixed instrument, replay not yet on the record because this entry
was not yet committed when it ran): composio input tokens 244,739,122 (was 165,959,914); 68
switches, 0/68 byte-identical; overlap of the receiver's ACTUAL prompt with sender-processed
content median 0.988 (p10 0.972, p90 0.994) -- the o1-mini prompt is the re-rendered transcript,
almost entirely words the sender produced; receiver prefill median 7,492 tokens (p10 3,434, p90
15,442); upper bound 88.9% of paid; H-E7a ratio 496,798 / 244,739,122 = **0.20%** vs 10%. The
correction moves the ratio DOWN by 7x: the verdict was robust to the defect, the figure was not.

**What this changes going forward.** The corrected figures enter the record by the next entry,
from `summarize_e7` only, after this entry is committed. E9's registration (drafted as 0017,
band approved) becomes **0019**, and its handoff definition is request-level: `S` = everything
the sender processed up to its last response, `R` = the receiver's request prompt. The learnings
ledger carries the shape finding with a read-only re-verify line.

prior-entries-sha256: __CHAIN__
"""
text = LEDGER.read_text(encoding="utf-8")
if "### 0017" in text:
    sys.exit("0017 present")
if "### 0016" not in text:
    sys.exit("0016 must exist first")
head = re.search(r"^## Entries\s*$", text, re.M)
if not text.endswith("\n"):
    text += "\n"
prefix = text + "\n"
chain = hashlib.sha256(prefix[head.start():].encode("utf-8")).hexdigest()
LEDGER.write_text(prefix + ENTRY.replace("__CHAIN__", chain), encoding="utf-8", newline="\n")
from linear_ceiling.ledger_check import check  # noqa: E402

pr = check(LEDGER.read_text(encoding="utf-8"))
print("0017 chain:", chain)
print("problems:", pr or "none")
sys.exit(1 if pr else 0)
