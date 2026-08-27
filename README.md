# linear-ceiling

Public repository for **"The Linear Ceiling: Predicting Cross-Model KV Cache Transfer
Before Fitting the Mapper."** It holds the pre-fit screen, the seal protocol that makes
"pre-fit" auditable, the pre-registration ledger, and the experiment orchestration. The
fitting/injection/evaluation harness is the pinned, read-only upstream
[kv-transfer-replication](https://github.com/hossainpazooki/kv-transfer-replication)
(`UPSTREAM.md`), invoked rather than vendored.

> **STATUS: ONLY E0 HAS RUN.** E0 — the first gate, weights-only, no forward pass — has run on
> all six required ordered pairs, and its verdict is **SAME** (ladder). Its decision rule was
> written into the ledger as entry 0003 and committed *before* any weight was read; the verdict
> is recorded in **entry 0004**. Under entry 0003's rule, SAME kills the screen at G1 and
> activates the Variant 3 degrade path. That verdict is on a vocabulary-based proxy for the
> residual stream, a limit entry 0003 registered before the run — it is not a verdict on residual
> streams, and does not by itself settle the screen in general. `H-S2`'s first clause is
> therefore `NOT CONFIRMED`; **every other hypothesis in `ledger/ledger.md` is still
> `unresolved`**, and nothing beyond E0 has run — no forward pass, no fitted mapper, no E1.
> Apart from E0's own figures in entry 0004 and in `results/` (gitignored), the only numbers in
> the tree are references to the upstream's ledger, each with a commit-pinned provenance line.

The scope sentence, held verbatim:

> The screen predicts what a linear mapper can achieve; retention asymmetry beyond that
> prediction is measured and attributed receiver-side, not explained.

## What is here

| path | what |
|---|---|
| `docs/2026-08-26-kv-handoff-screen-design.md` | the approved design spec, verbatim (authority on scope, hypotheses, gates) |
| `docs/2026-08-26-seed-w1.md`, `docs/gap-map.md` | the W1 seed and the E7 gap map, verbatim |
| `ledger/ledger.md` | pre-registered hypotheses and numbered, immutable entries |
| `ledger/predictions/` | sealed per-pair screen predictions (`<pair>.json` + `<pair>.sha256`), written before any fit |
| `src/linear_ceiling/screen.py` | regularized CCA + read-out-conditioned predicted R² (identity exact on synthetic data) |
| `src/linear_ceiling/seal.py` | the seal: writer refuses if a fitted mapper exists; runners refuse without a matching sealed hash |
| `src/linear_ceiling/e0.py` | E0, weights only, no forward pass; one verdict artifact |
| `config/*.toml` | seeds and thresholds — never in code |
| `results/` | gitignored; numbers reach the ledger only through `summarize_e0.py`, which fails closed |

## Hard invariants (enforced in CI where possible)

1. **Seal before fit.** `python -m linear_ceiling.seal verify` runs in CI: every sealed file's
   canonical hash matches its sidecar, it is committed, and it was never modified after the
   commit that sealed it. A green CI seal check proves hash integrity and commit immutability
   of sealed records — it does not and cannot re-verify the ordering guarantee itself, since CI
   never checks out the upstream artifact roots the seal predictions are compared against.
2. **Pre-registration.** Verdicts are stated against the rule as written; amendments are new
   numbered entries. `python -m linear_ceiling.ledger_check` runs in CI.
3. **No fabricated numbers.** Zero results at scaffold; synthetic figures appear only in the
   spec, labeled synthetic.
4. **Determinism.** One seeded generator (`rng.make_rng`), seeds in config; the test suite
   greps the tree for any other generator.
5. **Scope sentence verbatim,** once, in this README. `python -m linear_ceiling.lint_scope`
   runs in CI.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -e ".[dev]"
pytest
python -m linear_ceiling.seal verify && python -m linear_ceiling.lint_scope && python -m linear_ceiling.ledger_check
```

The suite runs offline in seconds on synthetic matrices. A green suite proves the tooling,
not any result. The seal writer additionally needs the upstream checked out at
`../kv-transfer-replication` (it fails closed if that tree is missing).

## Status tags

`[VALIDATED]` ran and survived an independent attempt to refute it · `[BASELINE]` ran, numbers
in the ledger · `[STRETCH]` designed, not run · `[FUTURE]` not designed · `[SUPERSEDED]`.
Ledger entry 0004 (the E0 verdict) is the only `[VALIDATED]` item; everything else carries
`[FUTURE]` or `[STRETCH]`.
