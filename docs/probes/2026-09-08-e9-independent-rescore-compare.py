#!/usr/bin/env python3
"""Compare a cold E9 rescore with its archived score and token records.

This is an independent-review helper, not a summarizer and not ledger evidence.
It deliberately performs exact comparisons so that any platform-level drift is
visible rather than absorbed into a tolerance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


SCORE_FIELDS = (
    "n_pairs",
    "same_K_r2_layer_mean",
    "same_V_r2_layer_mean",
    "cross_K_r2_layer_mean",
    "cross_V_r2_layer_mean",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-score", required=True, type=Path)
    parser.add_argument("--cold-score", required=True, type=Path)
    parser.add_argument("--archive-tokens", required=True, type=Path)
    parser.add_argument("--cold-tokens", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive_score = json.loads(args.archive_score.read_text(encoding="utf-8"))
    cold_score = json.loads(args.cold_score.read_text(encoding="utf-8"))

    score_equal = {
        field: archive_score[field] == cold_score[field]
        for field in SCORE_FIELDS
    }

    with np.load(args.archive_tokens) as archive_tokens, np.load(args.cold_tokens) as cold_tokens:
        keys_equal = archive_tokens.files == cold_tokens.files
        token_equal = {
            key: bool(np.array_equal(archive_tokens[key], cold_tokens[key]))
            for key in archive_tokens.files
        }

    passed = all(score_equal.values()) and keys_equal and all(token_equal.values())
    report = {
        "schema": "linear-ceiling.independent-e9-rescore-compare.v1",
        "passed": passed,
        "score_fields_exact": score_equal,
        "token_keys_exact": keys_equal,
        "token_arrays_exact": token_equal,
        "inputs": {
            "archive_score": {"path": str(args.archive_score), "sha256": sha256(args.archive_score)},
            "cold_score": {"path": str(args.cold_score), "sha256": sha256(args.cold_score)},
            "archive_tokens": {"path": str(args.archive_tokens), "sha256": sha256(args.archive_tokens)},
            "cold_tokens": {"path": str(args.cold_tokens), "sha256": sha256(args.cold_tokens)},
        },
    }

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
