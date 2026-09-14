# Clean-clone reproduction record

**Date:** 2026-09-11
**Status:** supporting review record; not a ledger entry, verdict, amendment, or summarizer output

## Purpose

A newcomer to the repository attempted the reproduction path a stranger would take:
clone, build the environment from the README, run every offline check, follow the record
to the data, and recompute the published verdict figures from the backup dataset.

This note reports how far that path gets, what reproduces, what the record says that is no
longer true, and one defect in the ledger's own prose. No scientific value is asserted or
changed here. `results/`, the fail-closed summarizers and the ledger remain the authority
for every figure.

## Environment

- linear-ceiling at `bb85a28` (merge of PR #2), working tree clean
- Linux, Python 3.12, torch 2.14.0+cpu, package installed editable
- No GPU; `../kv-transfer-replication` not present on this machine; no `traces/`;
  `results/` holds only `.gitkeep` placeholders

## What passed offline

Every check in the README's Setup block, plus the block-diff against the commit the
submission-day board pins.

| check | result |
|---|---|
| `pytest -q` | 423 passed, 1 skipped in 3.01s |
| `seal verify` | `OK (no sealed predictions yet)` |
| `lint_scope` | `scope ok` |
| `ledger_check` | `ledger ok (blocks unchanged vs HEAD)` |
| `ledger_check --against 700d830` | `ledger ok (blocks unchanged vs 700d830)` |

The single skip is `tests/test_e7_sensitivity.py:80`, which states its own reason:
`real corpus: set LC_REAL_TRACES=1 with traces/ acquired (gitignored)`. It skips rather
than passing vacuously.

Every ledger entry block is byte-identical between `700d830` and `bb85a28`. The intervening
commit added two documentation files and changed no evidence.

## What refused, and why that is correct

Both gated paths were invoked without data. Both refused, named the missing input, and
exited non-zero.

```
$ python -m linear_ceiling.e9 --check --config config/e9l.toml          # exit 2
E9 REFUSED: mapper artifact missing at .../mappers/qwen3-0.6b-to-1.7b/k1.safetensors;
copy mappers/qwen3-0.6b-to-1.7b/k1.json and .safetensors from the home checkout
(sha256-verify) before any prefill

$ python -m linear_ceiling.summarize_e9 --config config/e9l.toml        # exit 1
E9 SUMMARY REFUSED: .../results/e9l/report.json does not exist; E9 has not run
```

Neither emitted a figure, an empty result, or a zero.

## Recomputation from the published record

The backup dataset `anon/linear-ceiling-e9l-2026-09-10` is 57.7 GiB, of which
55.2 GiB is the retained tensors (`scratch/` 45.2, `bridge/` 10.0). The remaining 2.5 GiB
— `report.json`, `scores/`, `tokens/`, `align/`, `controls/`, `calibration/`, `recheck/`,
`logs/` — is enough to recompute every figure entry 0036's verdict reads, because the
per-token squares and the per-head SST are both in the record. 257 files were fetched with
`snapshot_download(..., ignore_patterns=["results/e9l/scratch/*", "results/e9l/bridge/*"])`.

`docs/probes/2026-09-11-e9l-record-recompute.py` performs the check and emits a
machine-readable report. It uses `linear_ceiling.e9_pertoken`'s own entry-0023 arithmetic,
so it verifies that the recorded figures follow from the recorded data — it is not an
independent reimplementation of the rule.

**Chain of custody.** The published `report.json` is sha256
`084d9480af74de2b038ce82f22bef3d2e5d477dc7243addf0c357d64b13aa9c8`, byte-identical to the
value `tools/ec2/verify_mirror.py` recorded at home under R6 and the runbook logs at
`docs/2026-09-10-e9l-gpu-runbook.md`. The Hub copy is the artifact that was verified.

**Integrity.** All 70 `scores/` and `tokens/` files match the sha256 the driver recorded in
`report.json`. Zero mismatches.

**Arithmetic.** All 10 headline medians reproduce exactly (atol 1e-12) from the per-token
records:

| statistic | recomputed | recorded |
|---|---|---|
| median f*(τ_K) E9-same K | 0.000000 | 0.000000 |
| median f*(τ_V) E9-same V | 0.000000 | 0.000000 |
| median f*(τ_K) E9-cross K | 0.963976 | 0.963976 |
| median f*(τ_V) E9-cross V | 0.945591 | 0.945591 |
| ladder τ=0.1 same K / V | 0.011865 / 0.025351 | 0.011865 / 0.025351 |
| ladder τ=0.03 same K / V | 0.525491 / 0.583737 | 0.525491 / 0.583737 |
| f*(τ_agent_K) same K / cross K | 0.000000 / 0.665121 | 0.000000 / 0.665121 |

Band outcome recomputed: **HOLDS**, matching the record. Per-handoff f*(τ_K) matches for
35 of 35 scored handoffs. Entry 0023's rider-2 identity — that the token mean of the
centered deviation is exactly 1 − R² — holds to a maximum absolute error of 2.75e-11
across all 35.

**H-E9L = HELD is correct.** The registered rule was applied and the number is right.

## The f*(τ) restatement defect

Entry 0023, which registers the statistic, defines it correctly:

> Sort matched tokens by δ_K(t) descending; f*(τ) is the smallest fraction of `M` that,
> removed (recomputed exactly), leaves the **MEAN** δ_K over the remaining tokens at or
> below τ.

`linear_ceiling.e9_pertoken.f_star` implements exactly that, and its unit test pins the
distinction: `f_star([0.1, 0.2, 0.3, 0.4, 5.0], 0.25) == 0.2`. Three of those five tokens
(0.3, 0.4, 5.0) exceed 0.25, so the "fraction exceeding τ" reading gives 0.60; f* removes only
the 5.0, because the remaining four average exactly 0.25, and returns 0.20. Same data, same τ,
a three-fold difference. The two readings coincide in exactly one case: when no token exceeds τ.

**Why the registered definition is the one that makes sense.** τ_K is itself a mean — it is
1 − R² of the k = 1 mapper, head-averaged then layer-averaged. f* therefore asks a budget
question: how many tokens must be recomputed so that the *average* remaining deviation is no
worse than the mapper already accepted. Testing individual token deviations against a
threshold that is itself an average compares unlike quantities.

**The restatement has a lineage.** Entry 0035 sets the two ideas side by side without
equating them: "a token needs recompute when it exceeds τ_K = 0.3186 …; the verdict statistic
is the median over included handoffs of the oracle selective-recompute fraction f*(τ_K)". The
first clause describes the sorting step and is true; the second names the statistic. Entries
0029 and 0036 collapse the two into one.

**Both verdict entries restate it as a different quantity.** Entry 0029 (H-E9) and entry
0036 (H-E9L) each say:

> f*(τ_K) = the fraction of matched tokens whose centered per-token deviation exceeds τ_K

That is not the registered statistic and not what the code computes. The two coincide only
when no token exceeds τ.

**Entry 0036 carries the misreading into a claim the data contradicts:**

> Not one scored handoff has a single matched token whose centered deviation exceeds τ_K on
> the same-model arm.

Measured from the published record, E9-same K:

| | |
|---|---|
| τ_K | 0.318644 |
| matched tokens with δ > τ_K | **30,701 of 387,508 (7.92%)** |
| handoffs with at least one such token | **35 of 35** |
| per-handoff fraction over τ_K | min 0.0182 · median 0.0577 · max 0.3413 |
| per-handoff count over τ_K | min 153 · median 529 · max 3,119 |
| global max centered per-token δ | **2.669974** (8.4 × τ_K) |

The sentence is false as written, and the entry contains its own counter-evidence: two
bullets above the band paragraph, 0036's seam profile reports a pooled median δ of 0.260 over
the 4,050 matched tokens at seam distance 0 — half of those tokens above 0.260, against a
τ_K of 0.3186. An entry asserting that no token anywhere exceeds 0.3186 published a median
within 20% of it in the same summarizer output.

Nothing in CI could have caught this. `ledger_check` verifies entry structure, the
`prior-entries-sha256` chain, verdict-cell provenance and the manifest citation; it does not
read an entry's prose against the figures printed beside it.

**Entry 0029 makes the same claim in a stronger form, and this record does not test it.**
0029's band paragraph reads "Not one included handoff has a single matched token whose
centered deviation exceeds τ_K on the same-model arm: the receiver's KV at the re-rendered
position agrees with its KV at the original position to within the mapper's own tolerance at
every matched token, on every handoff." That is the same definitional error carried further.
It concerns 0029's 25 short handoffs, whose records are in a different dataset
(`anon/linear-ceiling-e9-2026-09-04`) that was not downloaded here, so it is
untested. 0029's own seam profile (pooled median δ 0.236 in bin 0, n = 2,278, against
τ_K = 0.3186) makes the claim doubtful on its face, but that is an inference, not a
measurement.

**The verdict is unaffected.** f* = 0 because the full-set mean is already at or below τ_K:
the per-handoff mean centered δ runs 0.0429 to 0.2692 (median 0.1106), all below 0.318644.
That is the intended reading, stated in 0023 — τ is calibrated as the mapper's own mean
centered deviation, "so the mapper's own f*(τ) is 0 by construction and HOLDS keeps 0019's
meaning, 'the re-render costs no more to repair than the mapper itself'".

So HOLDS means **the mean deviation sits within the mapper's own mean error**, not that no
token deviates. The defect is in how two verdict entries describe the statistic, not in the
statistic, the code, or the result.

**What a corrected statement would say.** The verdict and every number survive it:

> Band outcome, against the rule as written: HOLDS. On every scored handoff the mean centered
> deviation over matched tokens (0.0429–0.2692, median 0.1106) already sits at or below
> τ_K = 0.3186, so the oracle selective-recompute fraction is 0.0000 — no token needs
> recomputing for the average remaining deviation to stay within the mapper's own tolerance.
> Individual tokens do exceed τ_K (7.92% of matched tokens, concentrated near seams), which is
> what the seam profile describes.

**Consequence.** Entries are immutable, so neither 0029 nor 0036 can be edited; a correction
takes a new numbered entry through `docs/drafts/README.md`, which is the operator's call.
This matters before submission because §4.1 and §4.2 of
`docs/paper/2026-09-10-lcfm-outline-v2.md` are written from these two entries, and "not one
token deviates" is a materially stronger claim than the result supports.

## Findings on the record and the Hub

**1. All three backup datasets are public; the record said private.** Checked against the
Hub API on 2026-09-11, metadata only:

| dataset | `private` | `gated` | `lastModified` | `downloads` |
|---|---|---|---|---|
| `…/linear-ceiling-e9-2026-09-04` | false | false | 2026-09-04T21:03:17Z | 9 |
| `…/linear-ceiling-n420-2026-09-08` | false | false | 2026-09-09T02:31:04Z | 0 |
| `…/linear-ceiling-e9l-2026-09-10` | false | false | 2026-09-10T18:26:06Z | 0 |

**2. Protocol R8 still specifies a private dataset.** R8 reads "pushed to a private Hugging
Face dataset". This is a divergence between a registered rule and the world, not a stale
fact, and it is the operator's to rule on. R8 has not been edited; the divergence is flagged
in `README.md` and `CLAUDE.md`.

**3. The E9-long backup push completed after the newest handoff brief was written.**
`docs/handoff/2026-09-10-e9l-sitting-on-a-rented-l40s-run-complete.md` records the R8 backup
as "staged by hardlink, NOT pushed (token)" and lists the push as a Next item. The dataset's
`lastModified` is 2026-09-10T18:26:06Z, about 17 hours after the run finished at 01:13:09Z.
The brief is dated and is not edited; this note is the record that the step completed.

**4. `docs/status.md` does not exist and was referenced three times.** The most consequential
was the "Where to go next" row reading "see every hypothesis, rule, result and verdict →
`ledger/ledger.md`, then `docs/status.md`". Corrected in `README.md` to name what exists.
The archived form is `docs/archive/README-2026-09-09-status.md`; whether to install it as
`docs/status.md` is not decided here.

**5. A pinned input in an earlier review record is one character short.**
`docs/reviews/2026-09-08-e9-independent-reverification.md` gives the transport archive
revision as `a45e9ee8c511f5aab738400f06a2462b4fee539` — 39 characters. A git revision is 40.
The Hub API reports `a45e9ee8c511f5aab738400f06a2462b4fee5391`, of which the recorded value
is a correct prefix, so the revision identified is the right one and nothing in that review's
conclusion is affected. That dataset's `lastModified` (2026-09-04) predates the review, so
the head revision has not moved since.

This is not caught by CI: `tests/test_imports.py::test_upstream_pin_matches_upstream_md`
counts 40-hex shas in `UPSTREAM.md` only, and nothing checks revisions quoted in
`docs/reviews/`. The learnings entry
`2026-09-04-every-re-pin-trips-the-one-full-sha-rule.md` records the same class of error in
the file that is checked. Per the convention that dated records are immutable, the 09-08
record is **not** edited; this note is the correction.

**6. Public datasets raise the cost of a double-blind slip.** The 09-08 review states that the
archive's name and location stay out of double-blind paper material. While the datasets were
private, a leaked name resolved to nothing for a reviewer. It now resolves to a named account.
The rule is unchanged and already sufficient; what changed is the consequence of breaking it.
Paper material should be swept for the dataset names and the account name before submission.

**7. The README's Setup block does not mention the CPU torch index.** A default
`pip install torch` pulls CUDA wheels that no offline check needs.
`.github/workflows/ci.yml` uses `--index-url https://download.pytorch.org/whl/cpu`; the
README's `uv pip install` line does carry it, but a reader using plain `pip` has nothing to
follow. Not corrected here; noted.

## Changes made to tracked files

Living documents only. No dated record, no archived snapshot, no handoff brief, no protocol
rule and no ledger file was edited.

- `README.md` — the three datasets described as public with the check date; the R8 divergence
  stated; three `docs/status.md` pointers repaired; the "private" adjective dropped from the
  backup-mechanism sentence that now sits four lines above the visibility statement.
- `CLAUDE.md` — the E9 dataset's parenthetical corrected to public; a dated observation added
  beside the R8 summary recording the divergence and stating that R8 is unchanged.
- `docs/probes/2026-09-11-e9l-record-recompute.py` — new; the recomputation above, repeatable.

All five offline checks were re-run after these edits and return the same results.

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

# the 2.5 GiB record subset, then the recomputation:
.venv/bin/python -c 'from huggingface_hub import snapshot_download as d; \
  d("anon/linear-ceiling-e9l-2026-09-10", repo_type="dataset", \
    local_dir="e9l-mirror", \
    ignore_patterns=["results/e9l/scratch/*","results/e9l/bridge/*"])'
.venv/bin/python docs/probes/2026-09-11-e9l-record-recompute.py \
  --mirror e9l-mirror/results/e9l --out e9l-recompute.json
```

Dataset visibility was read from the Hub API metadata endpoint (`/api/datasets/<repo_id>`)
with no authentication.

## Interpretation boundary

This record establishes that the instrument builds and verifies end to end from a clean clone;
that the ledger is byte-identical to the board's pinned commit; that the gated paths refuse
correctly when their inputs are absent; that the published E9-long record is the artifact
verified at home; that its 70 score and token files match their recorded hashes; and that
entry 0036's ten headline medians, its per-handoff f*(τ_K) for all 35 handoffs, and its band
outcome all follow from the published per-token data under entry 0023's rule.

It does **not** establish anything about the retained tensors: `scratch/` and `bridge/` were
not downloaded, no `lfs.sha256` was compared, no dump was re-scored, and
`tools/hf_verify_backup.py` was not run. The recomputation uses the repository's own
`e9_pertoken` implementation, so it confirms that the recorded figures follow from the
recorded data — not that the implementation is a correct reading of entry 0023 beyond the
definitional comparison stated above, and not that the per-token records themselves are
correct, which would require re-scoring from tensors against the frozen upstream. Nothing
here re-derives the alignments from raw traces, bears on any registered threshold, or
disturbs the oracle-floor reading bound to H-E9 and H-E9L by entry 0027. Whether R8 should
now read "public", and how the f*(τ) restatement in 0029 and 0036 should be corrected, are
governance questions and are left open.
