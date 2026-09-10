# E9 independent re-verification record

**Date:** 2026-09-08
**Status:** supporting review record; not a ledger entry, verdict, amendment, or summarizer output

## Purpose

An independent review checked whether the frozen upstream scoring path could
reproduce archived E9 records in a clean Algoverse H100 environment. The review
also assessed interpretation separately from computational reproduction.

The scientific values and verdict remain governed by `results/e9/`, the
fail-closed `summarize_e9` path, and ledger entry 0029. This note does not insert
new scientific values into the repository or change any registered choice.

## Pinned inputs

- Frozen upstream scorer: `d5786df91f55629933067e3c4bb14f1288c4bef2`
- Private transport archive revision: `a45e9ee8c511f5aab738400f06a2462b4fee539`
- Archived mapper stem: `mappers/qwen3-0.6b-to-1.7b/k1`
- Archived alignments: `align/<handoff>.npz`
- Archived comparison targets: `scores/<handoff>.json` and
  `tokens/<handoff>.tokens.npz`

The private archive is transport only. Its name and location stay out of
double-blind paper material.

## Cold-rescore sample

Two retained handoffs from different repositories were selected so the check
did not depend on one convenient record:

- `20241025_composio_swekit__django__django-11066_traj_sw36`
- `20241016_composio_swekit__astropy__astropy-14182_traj_sw68`

For each handoff, the frozen upstream `scripts/score_positions.py` was run from
the archived raw dumps, mapper, and alignment. The archived and regenerated
headline fields matched exactly, as did the keys and contents of every retained
per-token array. The review used exact equality rather than the registered
cross-platform tolerance.

`docs/probes/2026-09-08-e9-independent-rescore-compare.py` makes that comparison
repeatable and emits a machine-readable report with hashes for all four inputs.

## Re-run shape

```bash
python docs/probes/2026-09-08-e9-independent-rescore-compare.py \
  --archive-score "$ARCHIVE/scores/$HANDOFF.json" \
  --cold-score "$RECHECK/$HANDOFF.json" \
  --archive-tokens "$ARCHIVE/tokens/$HANDOFF.tokens.npz" \
  --cold-tokens "$RECHECK/$HANDOFF.tokens.npz" \
  --out "$RECHECK/$HANDOFF.comparison.json"
```

The cold score itself is produced by the pinned upstream repository, never by
this repository importing or copying upstream code.

## Interpretation boundary

This re-verification supports computational integrity for the sampled archived
records. It does not resolve the registered threshold choices, the chronology
of later sign-off, the oracle-floor-versus-achieved-method distinction, or
generalization beyond the recorded harness, model pair, and corpus. Those are
scientific judgment and governance questions, not failures of the comparison
tool.
