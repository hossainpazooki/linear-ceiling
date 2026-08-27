"""Invariant 5: the scope sentence appears exactly once in README.md, verbatim, and no
sentence anywhere in README/ledger/docs paraphrases it. Heuristic for paraphrase: a sentence
whose distinctive vocabulary overlaps heavily with the scope sentence's, and that is not the
verbatim sentence itself, is flagged. Overlap (not mere co-occurrence of two keywords) is the
discriminator, because sentences legitimately discuss "the screen" and "the receiver" in the
same breath without paraphrasing the scope commitment (e.g. ledger.md H-S3's falsification
clause), and punctuation choice (";" vs the unicode arrow "->") is not a reliable signal of
which case is which."""
import re
import sys

from linear_ceiling import REPO_ROOT

SCOPE_SENTENCE = ("The screen predicts what a linear mapper can achieve; retention asymmetry beyond "
                  "that prediction is measured and attributed receiver-side, not explained.")

# Verbatim source documents: committed exactly as authored (the design spec and the docs it
# governs). They must not be edited to dodge this lint, so they are exempted by exact filename
# instead of relying on the paraphrase heuristic to spare them.
EXEMPT = {"docs/2026-08-26-kv-handoff-screen-design.md", "docs/2026-08-26-seed-w1.md", "docs/gap-map.md"}

# Sentence boundary: standard terminal punctuation only. An earlier version also treated the
# unicode arrow "->" as a boundary, to stop a false positive on ledger.md H-S3 (a long
# arrow-joined clause that mentions both "screen" and "receiver" without paraphrasing the scope
# sentence). That made punctuation the discriminator between a false positive and a real
# paraphrase, which is wrong: a paraphrase joined with "->" evaded detection entirely, while the
# identical paraphrase joined with ";" was still caught. The real discriminator is below
# (_overlap_score): H-S3's clause and a genuine paraphrase both contain "screen" and "receiver",
# but only the paraphrase reuses most of the scope sentence's distinctive vocabulary.
_SENTENCE_BOUNDARY = r"(?<=[.!?])\s+"

# Common function words excluded when measuring vocabulary overlap, so the score reflects
# distinctive content words rather than words like "the"/"that"/"is" that any two English
# sentences share. None of these are words that appear in SCOPE_SENTENCE.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by", "can", "could",
    "did", "do", "does", "for", "from", "had", "has", "have", "he", "if", "in", "is", "it",
    "its", "nor", "not", "of", "on", "or", "our", "she", "should", "so", "such", "than",
    "that", "the", "their", "then", "these", "they", "this", "those", "to", "was", "we",
    "were", "what", "when", "which", "while", "who", "whom", "will", "with", "would", "you",
    "your",
}

# Crude length-based stem: truncate to 6 characters. Cheap enough to justify with a table of
# measured scores (see the module's caller / test suite) rather than a real stemmer, and it is
# enough to match inflected forms that matter here (achieve/achieves, predicts/prediction,
# explained/explains) without a dependency.
_STEM_LEN = 6


def _stem(word: str) -> str:
    return word if len(word) <= _STEM_LEN else word[:_STEM_LEN]


def _distinctive_stems(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {_stem(w) for w in words if w not in _STOPWORDS}


_SCOPE_STEMS = _distinctive_stems(SCOPE_SENTENCE)

# Threshold chosen with margin between the two measured anchor cases (see fix-lint-report.md
# for the full table): the reviewer's evasion-case paraphrase overlaps the scope sentence's
# distinctive vocabulary at ~0.54; ledger.md H-S3's falsification clause -- the case the arrow
# hack was protecting -- overlaps at ~0.31. 0.45 sits in the gap with margin on both sides.
_PARAPHRASE_THRESHOLD = 0.45


def _overlap_score(sentence: str) -> float:
    if not _SCOPE_STEMS:
        return 0.0
    stems = _distinctive_stems(sentence)
    return len(stems & _SCOPE_STEMS) / len(_SCOPE_STEMS)


def _normalize(text: str) -> str:
    # join wrapped lines (and blockquote markers) so a verbatim sentence split over lines still matches
    text = re.sub(r"\n>\s?", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def check_readme(text: str) -> list[str]:
    n = _normalize(text).count(SCOPE_SENTENCE)
    return [] if n == 1 else [f"README.md: scope sentence appears {n} times, expected exactly 1"]


def check_paraphrase(text: str, label: str) -> list[str]:
    flat = _normalize(text)
    problems = []
    for sent in re.split(_SENTENCE_BOUNDARY, flat):
        s = sent.strip()
        if not s or SCOPE_SENTENCE in s:
            # covers exact match and the verbatim sentence embedded in a larger span (e.g.
            # README's "The scope sentence, held verbatim: <sentence>", one regex "sentence"
            # because there is no terminal punctuation before the colon)
            continue
        score = _overlap_score(s)
        if score >= _PARAPHRASE_THRESHOLD:
            problems.append(f"{label}: sentence closely paraphrases the scope sentence "
                            f"(word overlap {score:.2f} >= {_PARAPHRASE_THRESHOLD}) and is not "
                            f"the verbatim scope sentence: '{s}'")
    return problems


def _ascii_safe(s: str) -> str:
    # Project rule: print() output must be ASCII (files stay UTF-8). Ledger/docs prose
    # legitimately contains non-ASCII math notation (rho, Sigma, superscript 2, arrows,
    # plus-minus), and this project's stated Windows-local console is cp1252; a flagged
    # sentence containing such characters must still be reportable there instead of raising
    # UnicodeEncodeError at the exact moment the lint is doing its job.
    return s.encode("ascii", "backslashreplace").decode("ascii")


def main() -> int:
    problems = check_readme((REPO_ROOT / "README.md").read_text(encoding="utf-8"))
    files = [REPO_ROOT / "README.md", REPO_ROOT / "ledger" / "ledger.md",
             *sorted((REPO_ROOT / "docs").rglob("*.md"))]
    for f in files:
        if "superpowers" in f.parts:
            continue
        rel = f.relative_to(REPO_ROOT).as_posix()
        if rel in EXEMPT:
            continue
        problems += check_paraphrase(f.read_text(encoding="utf-8"), rel)
    for p in problems:
        print("SCOPE:", _ascii_safe(p))
    print("scope ok" if not problems else f"scope: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
