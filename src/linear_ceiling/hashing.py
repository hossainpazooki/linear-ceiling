"""Canonical bytes and SHA-256 for sealed artifacts.

A seal hashes the *parsed, canonicalised* JSON (sorted keys, 2-space indent, LF, UTF-8,
trailing newline), never the on-disk bytes. Reason: a Windows CRLF checkout must not break
a seal made on Linux. Lesson carried from passed-vs-true-demo's `canonicalBytes`
content-hash pinning, where hashing post-normalisation bytes was what made the pin
portable.
"""
import hashlib
import json
from pathlib import Path


def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_json_obj(obj) -> str:
    return sha256_hex(canonical_bytes(obj))


def hash_json_file(path) -> str:
    return hash_json_obj(json.loads(Path(path).read_text(encoding="utf-8")))


def sha256_file_bytes(path) -> str:
    """Raw-bytes digest, for non-JSON artifacts (e.g. TOML configs recorded in verdicts)."""
    return sha256_hex(Path(path).read_bytes())
