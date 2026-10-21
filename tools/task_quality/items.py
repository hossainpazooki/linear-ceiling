# Structured-field recall items (ruling C1, form 2'): extraction, location in R, scoring.
#
# Ground truth is the field as the trace renders it; an item is valid iff the field's tokens
# lie in the archived matched set M (receiver positions). Nothing here selects on model output.
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

from linear_ceiling.e7_swe import load_composio_detailed
from linear_ceiling.e9_align import handoffs_from

# Tool results are JSON-rendered text: a newline is the two-character "\n", doubled when the
# result is itself JSON-encoded a second time. Split on every rendering.
LINE_BREAK = re.compile(r"\\\\n|\\n|\n")
BLOCK_HEAD = re.compile(r"^## Details about shortlisted result ID \d+:")
CLASS_FULL = re.compile(r"^Class full name: (\S+)$")
FILE_LINE = re.compile(r"^File where defined: (\S+)$")
# The signature as rendered (with its return annotation), then an optional inline comment, then any
# of the renderer's " | " suffixes. A truncated rendering (unbalanced parentheses, no closing colon)
# does not match and is not an item.
SIGNATURE = re.compile(r"^Signature: (def ([A-Za-z_]\w*)\(.*?\)(?: -> [^|#]+?)?:)(?: #.*?)?"
                       r"((?: \| (?:Member of `[A-Za-z_]\w*` class|Defined in `[^`]+`|Decorators: [^|]+"
                       r"|Not a member of any class))*)$")
OWNER = re.compile(r" \| Member of `([A-Za-z_]\w*)` class")
REPOSITORY = re.compile(r"You have the repository (\S+) cloned")
KINDS = ("file", "signature", "repository")


def lines_of(text):
    # (start, end, stripped line) over every rendered line; the leading "* " of a list item is
    # not part of the field.
    out = []
    position = 0
    for piece in LINE_BREAK.split(text):
        start = text.index(piece, position)
        inner = piece.strip()
        if inner.startswith("* "):
            inner = inner[2:].strip()
        if inner:
            offset = piece.index(inner)
            out.append((start + offset, start + offset + len(inner), inner))
        position = start + len(piece)
    return out


def extract(sender_text):
    """Candidate items from S, before deduplication: dicts with kind, key, answer, anchor
    (the raw rendered text whose first occurrence in R locates the item) and answer_offset
    (where the answer starts inside the anchor)."""
    candidates = []
    pending_file = None
    for start, end, line in lines_of(sender_text):
        if BLOCK_HEAD.match(line):
            pending_file = None
            continue
        if (m := FILE_LINE.match(line)):
            pending_file = (start, m.group(1))
            continue
        if (m := CLASS_FULL.match(line)):
            if pending_file is not None:
                file_start, path = pending_file
                anchor = sender_text[file_start:end]
                candidates.append({"kind": "file", "key": m.group(1), "answer": path, "anchor": anchor,
                                   "answer_offset": anchor.index(path), "class": m.group(1)})
            pending_file = None
            continue
        if (m := SIGNATURE.match(line)):
            signature, method = m.group(1), m.group(2)
            owner = (o := OWNER.search(m.group(3))) and o.group(1)
            if not owner:
                continue   # a signature outside a class listing has no mechanical owner
            candidates.append({"kind": "signature", "key": f"{owner}.{method}", "answer": signature,
                               "anchor": line, "answer_offset": line.index(signature),
                               "class": owner, "method": method})
    for m in REPOSITORY.finditer(sender_text):
        candidates.append({"kind": "repository", "key": "repository", "answer": m.group(1),
                           "anchor": m.group(0), "answer_offset": m.group(0).index(m.group(1))})
    return candidates


def deduplicate(candidates):
    """One item per (kind, key). A key rendered with two different answers is ambiguous and
    dropped; the count of dropped keys is returned beside the items."""
    answers = {}
    first = {}
    for c in candidates:
        slot = (c["kind"], c["key"])
        answers.setdefault(slot, set()).add(c["answer"])
        first.setdefault(slot, c)
    items = [first[slot] for slot in first if len(answers[slot]) == 1]
    return items, sum(len(a) > 1 for a in answers.values())


def locate(items, receiver_text, offsets, matched_positions):
    """Place each item in R: the anchor's FIRST occurrence; the answer's token span under
    the tokenizer offsets of R; valid iff every answer token is a matched position.

    `offsets` is the fast tokenizer's (start, end) per receiver token; `matched_positions`
    the receiver column of the archived pairs."""
    matched = np.zeros(len(offsets), dtype=bool)
    matched[np.asarray(matched_positions, dtype=np.int64)] = True
    starts = np.asarray([s for s, _ in offsets], dtype=np.int64)
    ends = np.asarray([e for _, e in offsets], dtype=np.int64)
    out = []
    for item in items:
        row = dict(item)
        at = receiver_text.find(item["anchor"])
        row["in_receiver"] = at >= 0
        if at < 0:
            row.update(answer_char_start=None, answer_tokens=[], valid=False, first_token=None)
            out.append(row)
            continue
        a = at + item["answer_offset"]
        b = a + len(item["answer"])
        tokens = np.flatnonzero((starts < b) & (ends > a))
        if not len(tokens):
            raise ValueError("answer span covers no receiver token")
        row.update(answer_char_start=a, answer_tokens=[int(t) for t in tokens],
                   valid=bool(matched[tokens].all()), first_token=int(tokens[0]))
        out.append(row)
    return out


def items_for_handoff(sender_text, receiver_text, offsets, matched_positions):
    candidates = extract(sender_text)
    items, ambiguous = deduplicate(candidates)
    located = locate(items, receiver_text, offsets, matched_positions)
    counts = {"candidate_lines": len(candidates), "distinct": len(items), "ambiguous_keys": ambiguous,
              "in_receiver": sum(r["in_receiver"] for r in located), "valid": sum(r["valid"] for r in located),
              "valid_by_kind": dict(Counter(r["kind"] for r in located if r["valid"]))}
    return located, counts


def handoff_texts(traces, handoff_id):
    # The same parser and slice E9 used; the trace path follows the handoff id.
    path = traces / ("swe-bench/" + handoff_id.split("#")[0] + ".json")
    trajectory, texts = load_composio_detailed(path, path.parent.name, lambda text, kind: 0)
    handoff = next(h for h in handoffs_from(trajectory, texts) if h.handoff_id == handoff_id)
    return path, handoff


def included_alignments(align_dir):
    coverage = json.loads((Path(align_dir) / "coverage.json").read_text())
    return [row for row in coverage["alignments"] if not row["excluded"]]


def alignment_file(align_dir, handoff_id):
    stem = handoff_id.replace("/", "__").replace("#", "_sw")
    return Path(align_dir) / f"{stem}.npz"


# ---- scoring: normalized exact match and token F1, both judge-free ----

def normalize(text):
    first = text.strip().split("\n", 1)[0].strip()
    for _ in range(2):   # a wrapped answer may end "`." or ".`"
        first = first.rstrip(".").strip().strip("`'\"").strip()
    return re.sub(r"\s+", " ", first)


def tokens_of(text):
    return re.findall(r"\w+|[^\w\s]", normalize(text))


def exact_match(prediction, gold):
    return normalize(prediction) == normalize(gold)


def contains(prediction, gold):
    # The gold field appears verbatim (whitespace-collapsed) anywhere in the generation: the
    # literal-answer relaxation of EM for a receiver that wraps the answer in a sentence.
    return re.sub(r"\s+", " ", gold.strip()) in re.sub(r"\s+", " ", prediction)


# The span a generation is read by, per kind: the first def-line, the first path, the first org/repo.
# A def-line may wrap inside its parentheses (DOTALL) and may end without its colon (a fenced code
# block drops it); the span ends at the colon, a backtick, a line end or the end of the text. The
# parentheses may not swallow a blank line or a second `def `, so an unclosed decoy does not run
# into the next def-line.
SPANS = {"signature": re.compile(r"def [A-Za-z_]\w*\((?:(?!\n\s*\n|def )[\s\S])*?\)(?: -> [^`\n:]+?)?(?::|(?=[`\n])|$)", re.M),
         "file": re.compile(r"[\w.-]+(?:/[\w.-]+)+\.\w+"),
         "repository": re.compile(r"[\w.-]*\w/[\w.-]*\w")}


def canonical(text):
    # The trace renders fields JSON-escaped and sometimes with a line break collapsed inside the
    # parentheses ("( self"); the receiver prints plain quotes. Undo both before comparing.
    text = text.replace('\\"', '"').replace("\\\\", "\\")
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return re.sub(r"\s+", " ", text).strip()


def first_span_exact(prediction, gold, kind="signature"):
    # The reading proposed after the pilot: the FIRST span of the item's kind that the generation
    # emits equals the field. A preamble does not fail it; a hedge list is read by its first entry.
    m = SPANS[kind].search(prediction)
    return m is not None and canonical(m.group(0)).rstrip(":") == canonical(gold).rstrip(":")


def canonical_contains(prediction, gold):
    return canonical(gold) in canonical(prediction)


def token_f1(prediction, gold):
    p, g = Counter(tokens_of(prediction)), Counter(tokens_of(gold))
    common = sum((p & g).values())
    if common == 0:
        return 0.0
    precision, recall = common / sum(p.values()), common / sum(g.values())
    return 2 * precision * recall / (precision + recall)
