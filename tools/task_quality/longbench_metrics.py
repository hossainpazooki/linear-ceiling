# LongBench's QA F1, copied verbatim (the borrowed-facts invariant: never re-implemented).
#   sourceRepo: https://github.com/THUDM/LongBench
#   filePath:   LongBench/metrics.py  (normalize_answer, f1_score, qa_f1_score)
#   commitSha:  c5ea10bcd06285223c58dfed76bbc92d22273709
#   file sha256 at that commit: see config/benchmark-control-pilot.toml [scorer]
# `best_over_answers` is the per-item rule of LongBench/eval.py `scorer` at the same commit (lines
# 72-73): the maximum over the item's ground truths. The 2wikimqa and hotpotqa sets are not among
# the sets whose prediction is cut at the first newline there (line 70).
import re
import string
from collections import Counter


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth, **kwargs):
    common = Counter(prediction) & Counter(ground_truth)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction)
    recall = 1.0 * num_same / len(ground_truth)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def qa_f1_score(prediction, ground_truth, **kwargs):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    return f1_score(prediction_tokens, ground_truth_tokens)


def best_over_answers(prediction, answers):
    score = 0.
    for ground_truth in answers:
        score = max(score, qa_f1_score(prediction, ground_truth))
    return float(score)
