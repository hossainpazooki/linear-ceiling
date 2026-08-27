import io

import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.lint_scope import SCOPE_SENTENCE, _ascii_safe, check_paraphrase, check_readme


def test_scope_sentence_is_the_spec_text():
    assert SCOPE_SENTENCE == ("The screen predicts what a linear mapper can achieve; retention "
                              "asymmetry beyond that prediction is measured and attributed "
                              "receiver-side, not explained.")


def test_readme_needs_exactly_one():
    assert check_readme("no sentence here") == ["README.md: scope sentence appears 0 times, expected exactly 1"]
    assert check_readme(SCOPE_SENTENCE + "\n\n" + SCOPE_SENTENCE) == \
        ["README.md: scope sentence appears 2 times, expected exactly 1"]
    assert check_readme("x\n" + SCOPE_SENTENCE + "\ny") == []


def test_wrapped_verbatim_sentence_counts_as_one():
    wrapped = ("> The screen predicts what a linear mapper can achieve; retention asymmetry beyond that\n"
               "> prediction is measured and attributed receiver-side, not explained.")
    assert check_readme(wrapped) == []


def test_paraphrase_is_flagged():
    text = "The screen predicts what a linear mapper achieves; the receiver explains the rest."
    assert check_paraphrase(text, "docs/x.md") == \
        ["docs/x.md: sentence closely paraphrases the scope sentence (word overlap 0.54 >= 0.45) "
         "and is not the verbatim scope sentence: "
         "'The screen predicts what a linear mapper achieves; the receiver explains the rest.'"]
    assert check_paraphrase(SCOPE_SENTENCE, "docs/x.md") == []


def test_paraphrase_joined_by_arrow_is_also_flagged():
    # Regression for the evasion hole: an earlier version treated the unicode arrow as a
    # sentence boundary, which let a paraphrase joined with "->" (rather than ";") through
    # undetected. The overlap heuristic doesn't care which punctuation joins the clauses.
    text = "The screen predicts what a linear mapper achieves → the receiver explains the rest."
    result = check_paraphrase(text, "docs/x.md")
    assert len(result) == 1
    assert "closely paraphrases the scope sentence" in result[0]
    assert text in result[0]


def test_near_miss_paraphrase_without_both_keywords_is_flagged():
    # Reuses most of the scope sentence's distinctive vocabulary ("screen", "predicts",
    # "linear", "mapper", "achieve", "beyond", "explained") without ever saying "receiver",
    # pinning that the heuristic gates on vocabulary overlap, not co-occurrence of two
    # specific trigger words.
    text = "The screen predicts what a linear mapper can achieve, and nothing beyond that is explained here."
    assert "receiver" not in text.lower()
    result = check_paraphrase(text, "docs/x.md")
    assert len(result) == 1
    assert "closely paraphrases the scope sentence" in result[0]


def test_ledger_hs3_false_positive_stays_unflagged_on_overlap_not_exemption():
    # The case that motivated the old arrow-boundary hack: mentions "screen" and "receiver"
    # in one breath but says something else entirely, so its overlap with the scope
    # sentence's distinctive vocabulary is low. It is not in EXEMPT, so this must hold by
    # measurement, not by a filename exception.
    text = ("Falsification mode: screen predicts fidelity but not retention → the contribution "
            "becomes the decomposition (symmetric predictable factor + receiver residual), "
            "stated in the abstract, not conceded to a reviewer.")
    assert check_paraphrase(text, "ledger/ledger.md") == []


def test_flagged_nonascii_sentence_is_reported_without_raising():
    # Windows-local console is cp1252 (see repo CLAUDE.md / global rule: print() output
    # must be ASCII, files stay UTF-8). Ledger/docs prose legitimately contains non-ASCII
    # math notation, so a flagged sentence containing it must still be reportable there
    # instead of raising UnicodeEncodeError at the exact moment the lint finds a real
    # violation. Exercise the actual encoding path with a real cp1252 stream, not just a
    # string-transformation assertion.
    text = "The screen ρ predicts what a linear mapper achieves; the receiver explains the rest."
    problems = check_paraphrase(text, "docs/rho.md")
    assert len(problems) == 1
    raw = problems[0]
    assert "ρ" in raw  # sanity: the raw diagnostic does carry the non-ASCII character

    stream = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")

    # Sanity check that this reproduces the real crash: printing the raw (un-sanitized)
    # diagnostic on a cp1252 stream is exactly the bug this finding is about.
    with pytest.raises(UnicodeEncodeError):
        print("SCOPE:", raw, file=stream)

    # The ASCII-safe rendering must not raise on the same stream, and must still let a
    # developer identify which sentence tripped the lint.
    safe = _ascii_safe(raw)
    print("SCOPE:", safe, file=stream)  # must not raise
    stream.flush()
    buf = stream.buffer.getvalue().decode("cp1252")
    assert "SCOPE:" in buf
    assert "receiver" in buf  # sentence content is still identifiable
    assert "\\u03c1" in buf  # the non-ASCII char is escaped, not silently dropped


def test_repo_passes():
    from linear_ceiling.lint_scope import main
    assert main() == 0
