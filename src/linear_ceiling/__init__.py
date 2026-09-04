"""linear-ceiling: pre-fit screen, seal protocol, and ledger tooling.

The fitting/injection/evaluation harness lives in the pinned upstream repository and is
invoked, never imported (see UPSTREAM.md).
"""
from pathlib import Path

__version__ = "0.0.1"

# src/linear_ceiling/__init__.py -> repo root is three parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Single source of truth for the upstream pin; UPSTREAM.md repeats it for humans and
# tests/test_imports.py asserts the two agree.
UPSTREAM_REPO = "https://github.com/hossainpazooki/kv-transfer-replication"
UPSTREAM_SHA = "d5786df91f55629933067e3c4bb14f1288c4bef2"   # re-pinned by ledger entry 0026 (prior: 36d73b3f entry 0023, 7e41f792 entry 0019, 71df4504 entry 0016, f3594458 entry 0001)
