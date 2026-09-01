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
UPSTREAM_SHA = "71df45043a799560e7631faa2b42a9cf3f2be3ad"   # re-pinned by ledger entry 0016 (prior: f3594458, entry 0001)
