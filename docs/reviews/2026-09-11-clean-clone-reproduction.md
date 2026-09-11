# Clean-clone reproduction record

**Date:** 2026-09-11
**Status:** supporting review record; not a ledger entry, verdict, amendment, or summarizer output

## Purpose

A newcomer to the repository attempted the reproduction path a stranger would take:
clone, build the environment from the README, run every offline check, and follow the
record to the data. This note reports how far that path gets, where it stops, and what
the record says that is no longer true.

No scientific value is asserted or changed here. `results/`, the fail-closed
summarizers and the ledger remain the authority for every figure.

## Environment

- linear-ceiling at `bb85a28` (merge of PR #2), working tree clean
- Linux, Python 3.12, torch 2.14.0+cpu, package installed editable
- No GPU; `../kv-transfer-replication` not present on this machine; no `traces/`;
  `results/` holds only `.gitkeep` placeholders

## What passed

Every offline check in the README's Setup block, plus the block-diff against the
commit the submission-day board pins.

| check | result |
|---|---|
| `pytest -q` | 423 passed, 1 skipped in 3.01s |
| `seal verify` | `OK (no sealed predictions yet)` |
| `lint_scope` | `scope ok` |
| `ledger_check` | `ledger ok (blocks unchanged vs HEAD)` |
| `ledger_check --against 700d830` | `ledger ok (blocks unchanged vs 700d830)` |

The single skip is `tests/test_e7_sensitivity.py:80`, which states its own reason:
`real corpus: set LC_REAL_TRACES=1 with traces/ acquired (gitignored)`. It skips
rather than passing vacuously.

The last row is the substantive one: every ledger entry block is byte-identical
between `700d830` and `bb85a28`. The intervening commit added two documentation
files and changed no evidence.

## What refused, and why that is correct

Both gated paths were invoked without data. Both refused, named the missing input,
and exited non-zero.

```
$ python -m linear_ceiling.e9 --check --config config/e9l.toml          # exit 2
E9 REFUSED: mapper artifact missing at .../mappers/qwen3-0.6b-to-1.7b/k1.safetensors;
copy mappers/qwen3-0.6b-to-1.7b/k1.json and .safetensors from the home checkout
(sha256-verify) before any prefill

$ python -m linear_ceiling.summarize_e9 --config config/e9l.toml        # exit 1
E9 SUMMARY REFUSED: .../results/e9l/report.json does not exist; E9 has not run
```

Neither emitted a figure, an empty result, or a zero. This is the intended
fail-closed behaviour and is recorded here as verified, not as an obstacle.

## Findings

**1. All three backup datasets are public; the record said private.**
Checked against the Hub API on 2026-09-11, metadata only:

| dataset | `private` | `gated` | `lastModified` | `downloads` |
|---|---|---|---|---|
| `…/linear-ceiling-e9-2026-09-04` | false | false | 2026-09-04T21:03:17Z | 9 |
| `…/linear-ceiling-n420-2026-09-08` | false | false | 2026-09-09T02:31:04Z | 0 |
| `…/linear-ceiling-e9l-2026-09-10` | false | false | 2026-09-10T18:26:06Z | 0 |

**2. Protocol R8 still specifies a private dataset.** R8 reads "pushed to a private
Hugging Face dataset". The three datasets are public. This is a divergence between a
registered rule and the world, not a stale fact, and it is the operator's to rule on.
R8 has not been edited. The divergence is flagged in `README.md` and `CLAUDE.md`.

**3. The E9-long backup push completed after the newest handoff brief was written.**
`docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md` records the R8
backup as "staged by hardlink, NOT pushed (token)" and lists the push as a Next item.
The dataset's `lastModified` is 2026-09-10T18:26:06Z, about 17 hours after the run
finished at 01:13:09Z. The brief is dated and is not edited; this note is the record
that the step completed.

**4. `docs/status.md` does not exist and was referenced three times.** The most
consequential was the "Where to go next" row reading "see every hypothesis, rule,
result and verdict → `ledger/ledger.md`, then `docs/status.md`" — the record's own
answer to "where are the results" ended in a dead pointer. Corrected in `README.md`
to name what exists. The archived form is
`docs/archive/README-2026-09-09-status.md`; whether to install it as `docs/status.md`
is not decided here.

**5. A pinned input in an earlier review record is one character short.**
`docs/reviews/2026-09-08-e9-independent-reverification.md` gives the transport archive
revision as `a45e9ee8c511f5aab738400f06a2462b4fee539` — 39 characters. A git revision
is 40. The Hub API reports `a45e9ee8c511f5aab738400f06a2462b4fee5391`, of which the
recorded value is a correct prefix, so the revision identified is the right one and
nothing in that review's conclusion is affected. That dataset's `lastModified`
(2026-09-04) predates the review, so the head revision has not moved since.

This is not caught by CI: `tests/test_imports.py::test_upstream_pin_matches_upstream_md`
counts 40-hex shas in `UPSTREAM.md` only, and nothing checks revisions quoted in
`docs/reviews/`. The learnings entry `2026-09-04-every-re-pin-trips-the-one-full-sha-rule.md`
records the same class of error in the file that is checked. Per the convention that
dated records are immutable, the 09-08 record is **not** edited; this note is the
correction.

**6. Public datasets raise the cost of a double-blind slip.** The 09-08 review states
that the archive's name and location stay out of double-blind paper material. While the
datasets were private, a leaked name resolved to nothing for a reviewer. It now resolves
to a named account. The rule is unchanged and already sufficient; what changed is the
consequence of breaking it. Paper material should be swept for the dataset names and the
account name before submission.

**7. The README's Setup block does not mention the CPU torch index.** A default
`pip install torch` pulls CUDA wheels that no offline check needs. `.github/workflows/ci.yml`
uses `--index-url https://download.pytorch.org/whl/cpu`; the README's `uv pip install`
line does carry it, but a reader using plain `pip` has nothing to follow. Not corrected
here; noted.

## Changes made to tracked files

Living documents only. No dated record, no archived snapshot, no handoff brief and no
ledger file was edited.

- `README.md` — the three datasets described as public with the check date; the R8
  divergence stated; three `docs/status.md` pointers repaired; the "private" adjective
  dropped from the backup-mechanism sentence that now sits four lines above the
  visibility statement.
- `CLAUDE.md` — the E9 dataset's parenthetical corrected to public; a dated observation
  added beside the R8 summary recording the divergence and stating that R8 is unchanged.

All five checks above were re-run after these edits and return the same results.

## Re-run shape

```bash
git clone <repo> linear-ceiling && cd linear-ceiling
python3 -m venv .venv
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -e ".[dev]"

.venv/bin/python -m pytest -q
.venv/bin/python -m linear_ceiling.seal verify
.venv/bin/python -m linear_ceiling.lint_scope
.venv/bin/python -m linear_ceiling.ledger_check
.venv/bin/python -m linear_ceiling.ledger_check --against 700d830

# expected to refuse without the upstream checkout and a run:
.venv/bin/python -m linear_ceiling.e9 --check --config config/e9l.toml   ; echo $?   # 2
.venv/bin/python -m linear_ceiling.summarize_e9 --config config/e9l.toml; echo $?   # 1
```

Dataset visibility was read from the Hub API metadata endpoint
(`/api/datasets/<repo_id>`) with no authentication and no download.

## Interpretation boundary

This record establishes that the instrument builds and verifies end to end from a clean
clone with no data, that the ledger is byte-identical to the board's pinned commit, and
that the gated paths refuse correctly when their inputs are absent. It reports the
current visibility of the three backup datasets as the Hub reported it on 2026-09-11.

It does **not** establish anything about the datasets' contents: no file was downloaded,
no `lfs.sha256` compared, no mirror reconstructed, and `tools/hf_verify_backup.py` was
not run. It does not re-derive any figure, does not re-score any handoff, and does not
bear on any registered threshold, verdict, or the oracle-floor reading bound to H-E9
and H-E9L. Whether R8 should now read "public" is a governance question and is left
open. The reproduction of the data path itself remains unattempted: the upstream
checkout at the pin is not present on this machine, and the E9-long gate refuses before
reaching a dataset.
