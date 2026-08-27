"""Qwen3 ladder and ordered-pair naming.

Naming provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/pairs.py,
commitSha: f3594458f73d70a15f195c863d52ea6592f61578} — pair names there are
"qwen3-0.6b-to-1.7b" style and this repo keeps them so sealed predictions and upstream
mapper artifacts key on the same string.
"""
import itertools
import re

LADDER: tuple[str, ...] = ("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "Qwen/Qwen3-8B")

_QWEN3 = re.compile(r"^Qwen/Qwen3-(\d+(?:\.\d+)?B)$")


def short_name(model_id: str) -> str:
    m = _QWEN3.match(model_id)
    if not m:
        raise ValueError(f"not a Qwen3 base model id: {model_id!r}")
    return f"qwen3-{m.group(1).lower()}"


def pair_name(src_id: str, tgt_id: str) -> str:
    if src_id == tgt_id:
        raise ValueError("a pair needs two different models")
    tgt_match = _QWEN3.match(tgt_id)
    if not tgt_match:
        raise ValueError(f"not a Qwen3 base model id: {tgt_id!r}")
    return f"{short_name(src_id)}-to-{tgt_match.group(1).lower()}"


def ordered_pairs(models) -> list[tuple[str, str]]:
    return [(a, b) for a, b in itertools.permutations(models, 2)]
