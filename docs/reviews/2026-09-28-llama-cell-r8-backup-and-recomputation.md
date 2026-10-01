# The Llama second-family cell: R8 backup found absent, then restored and recomputed

*Review and recomputation by Ritvik Aggarwal, 2026-10-01.*

**Outcome (2026-10-01):** backups found on the Hub 2026-09-30, checked against the run's own fingerprints and the
ledger, and both summarizers PASS on a download — see the last section. The sections in between record the
2026-09-28 state they describe and are kept as written.

**Date:** 2026-09-28
**Status:** supporting review record; not a ledger entry, verdict, amendment, or summarizer output.
No figure here is new. Every number quoted is read from a committed file or a registered entry and is
attributed to it; nothing was recomputed by a summarizer for this note, and nothing here may enter the
paper.

**Reviewed revision:** `118d08e` (= `origin/main`), working tree clean.

> **Update 2026-09-30 — superseded in part.** Two public datasets appeared on the Hub
> after this note was written: `emmmy/linear-ceiling-e8f-2026-09-18` and
> `emmmy/linear-ceiling-e9f-2026-09-19` (e9f last modified 2026-09-30T08:00:30Z, commit `ab7d0fd0`). Their
> cards describe them as the verified home mirrors of `results/e8f/` and `results/e9f/`. Findings 2 and 3
> and open item 1 below describe the state on 2026-09-28 and are **not** current; Finding 4 stands. The
> project-account datasets `hossainpazooki/linear-ceiling-e8f-2026-09-18` and `-e9f-2026-09-19` also exist,
> created 2026-09-30, reported empty by the operator.
>
> **Result of the check (2026-09-30).** Run by the reviewer on a Windows machine that can reach the Hub (this
> session cannot); scripts `check_hub.py` and `inspect_hub.py`, outputs `report.txt` and `inspect.txt`. No
> token, no tensors downloaded. Revisions read: e8f `17da9aeb69b0`, e9f `ab7d0fd08820`.
>
> - **e9f:** 1,052 files and 55,369,570,972 bytes, equal to its card. All 848 files that `report.json`
>   fingerprints (scores, token records, controls, 784 kept-dump files of the 8 kept handoffs) are on the Hub
>   with the recorded hash: 848 OK, 0 BAD, 0 missing. The box manifest `e9f.final.sha256`: 215 of 216 lines OK,
>   0 BAD, 1 unresolved (a 107-byte `manifest_check.out` that exists under two paths).
> - **e8f:** 157 files and 9,783,828,779 bytes, equal to its card. 149 of 150 manifest lines match. The one
>   BAD is `MANIFEST.sha256`'s line for itself, recorded as the hash of an empty file (`e3b0c442…`); this is the
>   "149/150, the 1 is the manifest hashing itself" that `sitting-a-record` already describes. The 7 files
>   beyond the 150 manifest lines were not checked against anything except the ledger pins below.
> - **Ledger pins, all matching:** `k1.safetensors` `fe77166a8ff4`, `k1.json` `6cbfad42b6b0`, the agent token
>   file `4e02d14af008`, `r2.json` `8498e977785e`, the E8 report `4682508afd35`.
> - **`coverage.json`** on the Hub is `6a8dc1242300`, the hash entry 0043 re-records; it differs from 0042's
>   `c0764a05f486` for the reason 0043 gives. **`tau.json`** on the Hub is `bddf1b281753`; no entry records that
>   hash. Its content: τ_K 0.28613264297901364, τ_V 0.5289405769525087, τ_agent_K 0.26891567134937666 over 2,560
>   held-out tokens, citing the same mapper, `r2.json` and E8-report hashes as above. τ_K differs from
>   `config/e9f.toml`'s typed value by 6.1e-11, inside the 1e-9 that entry 0044 states.
>
> **What this establishes and what it does not.** Each dataset is consistent with the records the run wrote
> about itself, and the pinned files match the ledger. It did not, on 2026-09-30, show that the summarizers pass on a
> download; **that test has since been run and passed — see "Recomputation from the download (2026-10-01)"
> at the end of this file.** A manifest inside
> a dataset shows the files agree with it, not where it came from; the ledger pins are the independent anchor,
> and they cover six files. Both datasets sit under a personal account (`emmmy`), not the project account;
> the operator ruled on 2026-10-01 to keep them there (README `5a71df6`) and to delete the two empty
> project-account datasets. The account name must stay out of paper material.

## Purpose

The 2026-09-25 handoff carries, as open item 3, "check whether Sitting A's R8 backup exists before any
Llama refutation." This note answers that question, records why the answer cannot be changed by
re-running the experiment, and states what the program loses while it stands.

The review covered PR #5 (merged `3902a16`, ledger 0039–0044),
`docs/handoff/2026-09-18-llama-runpod-live-transcript.md`, `docs/handoff/2026-09-18-sitting-a-record.md`,
and a replication report circulated 2026-09-28 describing both sittings.

## Environment

- Linux, Python 3.12, package installed editable from a clean clone of `118d08e`
- No GPU; `../kv-transfer-replication` not present; no `traces/`; `results/` holds only `.gitkeep`
- Outbound network restricted: the Hub was reached over HTTPS, PyPI's torch CPU index was not

## Finding 1 — the two sittings are on the record and their gates pass

Ledger 0039–0044 register and report the second model family
(`meta-llama/Llama-3.2-3B` → `meta-llama/Llama-3.1-8B`): 0040 is E8 on the new pair, 0044 is the E9
short cell, H-E9F `HELD`, 28 scored of 28 registered. Both structural gates pass at this revision.

```
re-verify: grep -n "^### 004[0-4]" ledger/ledger.md            # five headings, 0040-0044
re-verify: .venv/Scripts/python.exe -m linear_ceiling.ledger_check   # ledger ok
re-verify: .venv/Scripts/python.exe -m linear_ceiling.lint_scope     # scope ok
```

The offline suite gives 543 passed, 2 skipped, 1 failed on this machine. The one failure is
`tests/test_e7_sensitivity.py::test_override_recomputes_readings_and_labels_them_sensitivity`, which
fails inside `requests` with a `ProxyError` — it is this environment's blocked egress, not the code.
Read it as environmental only; it was not reproduced on an unrestricted machine here.

```
re-verify: .venv/Scripts/python.exe -m pytest -q
```

## Finding 2 — no backup dataset exists for this pair

The Hub's dataset listing for the account carries four datasets, all public, and none of them is this
pair's:

| dataset | experiment |
|---|---|
| `hossainpazooki/linear-ceiling-e9-2026-09-04` | E9 (Qwen, entry 0029) |
| `hossainpazooki/linear-ceiling-n420-2026-09-08` | n = 420 calibration (0033/0034) |
| `hossainpazooki/linear-ceiling-e9l-2026-09-10` | E9-long (0036) |
| `hossainpazooki/linear-ceiling-e9s-2026-09-13` | E9 scaled short cell (0038) |

Nothing named for `e8f`, `e9f` or the Llama pair appears, under this account or in a public search for
`linear-ceiling`.

```
re-verify: curl -s "https://huggingface.co/api/datasets?author=hossainpazooki&limit=100"
```

**Scope of this finding.** The query was unauthenticated, so it enumerates public datasets only. It
therefore cannot exclude a private dataset under this account, nor any dataset under a different
account. What it does establish is that no backup exists in the form R8 and the 2026-09-11 operator
ruling call for — public, under the project account, named to the existing convention — and that the
Llama runbook §11's planned dataset was never created there. Two independent records agree with this
reading: `sitting-a-record`'s open item 6 lists the R8 backup as not done, and the 09-25 handoff lists
it as unchecked.

## Finding 3 — the mirrors are held on one machine and are not retrievable

The verified home mirrors of `results/e8f/` and `results/e9f/` exist only on the machine that ran the
sittings — `/Users/emersonyu/e9-repro/linear-ceiling` per the Llama runbook, with the Sitting A pull
under `~/.cache/linear-ceiling/sitting-a-pull/pull/`. As of this date the reviewer reports them
unrecoverable (2026-09-28, reported by the reviewer; not independently verified from this checkout). This
note treats the mirrors as lost.

No other copy is known. `results/` is gitignored by rule and never enters history, so the repository
holds none of it; the rented pods were terminated at the close of each sitting.

## Finding 4 — a re-run cannot produce this backup, and this is by construction

The obvious repair — re-run both sittings and upload the result — cannot close the gap, because the
registered record pins the artifacts by content:

- `config/e9f.toml:125` fixes `tau_K = 0.28613264291767326`, derived in 0040 from this pair's own k = 1
  held-out R². `summarize_e9` recomputes it from the archived mapper and refuses on any disagreement.
- Entry 0040 pins the k = 1 mapper by sha256 (`k1.safetensors` `fe77166a8ff4`, `k1.json`
  `6cbfad42b6b0`), and entry 0042 pins the E8 report τ was calibrated from (`4682508afd35`), the fit
  record `r2.json` (`8498e977785e`), the alignment coverage (`c0764a05f486`) and the τ calibration
  (`54c6962230fe`). (Corrected 2026-09-30: the first version of this note attributed `4682508afd35` to
  the mapper; it is the E8 report.)

A mapper re-fitted on different hardware produces different bytes and a slightly different held-out R².
It therefore fails the sha pin, and the τ it implies fails the config pin. Entry 0028 already registers
why: float32 reduction order varies with platform and thread count, which is why the keep-subset
re-score is checked under a tolerance rather than for bit-identity.

The two sittings are also coupled in one direction: `config/e9f.toml` `[e9.mapper]` reads the k = 1
mapper that Sitting A fitted, so the E9 half cannot be re-run without re-running the E8 half first.

The consequence is worth stating plainly, because it is easy to mistake for pessimism about
reproducibility: **a re-run is a second cell, not a backup.** It would need its own configs and its own
entry registered before it ran (R1), and it would stand beside 0040/0044 rather than substantiating
them. That may well be worth doing on its own merits. It is not this.

```
re-verify: grep -n "tau_K = 0" config/e9f.toml
re-verify: awk '/^### 0040/,/^### 0041/' ledger/ledger.md | grep -n "fe77166a8ff4"
re-verify: awk '/^### 0042/,/^### 0043/' ledger/ledger.md | grep -n "4682508afd35"
```

## What this costs the program

Protocol R12 requires that "a co-author's refutation of the run's entries is recomputation from the git
repo plus the backup, and if that is not possible from a clean checkout, something is missing from R3 or
R8." That condition is now met for entries 0040 and 0044: the recomputation is not possible from a clean
checkout, and what is missing is R8. Until a backup exists, those two entries cannot be independently
recomputed by anyone, and a co-author refutation of them cannot be attempted at all.

What is **not** lost: R8 opens by stating that backup is transport, not evidence, and the summarizer
reads the local mirror only. The figures in 0040 and 0044 entered the ledger through fail-closed
summarizers that passed, and the ledger is the registered record of them. The loss is the ability of
others to recheck those figures — which is precisely what R12 exists to protect, and is not a small
loss — but it is not a defect in the entries themselves, and nothing here impeaches them.

Two scope notes limit how far this reaches. The Llama cell is a second-family baseline: 0044 records
H-E9F, which is a separate row from H-E9 and H-E9L, and the 09-25 handoff states that the Llama cell
"cannot discharge Condition 1." So the open condition on §4.1/§5.1 is untouched by this finding. And
the Llama cell postdates outline v3 (2026-09-11) and does not appear among the cells it carries;
whether the manuscript cites the Llama cell at all is the paper session's to confirm, and this note does
not assume either way.

## Open, for the operator

1. ~~**The mirrors are lost, so no push can close this.** Only items 2 and 3 remain.~~ Superseded by
   the 2026-09-30 update above: the datasets exist and match the run's own records and the ledger pins.
2. *(Superseded 2026-10-01: the backups exist and R12 passed, see the last section, so there is no gap left
   to record.)* **Whether to append a ledger entry.** A provenance entry recording that 0040/0044 have no R8 backup
   would put this on the registered record, where 0021 (dating erratum) and 0041 (an ordering that was
   never registered) are the precedents. It is append-only and chain-hashed, so it is the operator's to
   append; no script is staged for it, and the next free number is 0047 per the 09-25 handoff.
3. *(Superseded 2026-10-01 as a remedy for the gap; a re-run stays possible as its own registered cell.)*
   **Whether to fund a re-run as its own registered cell.** Per the Llama runbook §3.4 and the recorded
   sitting prices, that is a ≥ 40 GB card for Sitting A (peak 30.4 GiB) and an 80 GB card for Sitting B
   (peak 45.2 GiB); the two sittings as run cost $6.20 in total. It would require the entry and configs
   committed before anything ran.

A 32 GB laptop cannot substitute for either sitting: Sitting A's 30.4 GiB point estimate (32.8 GiB with
the runbook's +8% column) exceeds usable RAM on such a machine, and Sitting B's 45.2 GiB is further out
of reach. Reducing precision to fit would change the method and would need its own registration.

## Recomputation from the download (2026-10-01)

R12's test, run by someone who was not at either sitting: both fail-closed summarizers, on a clean clone plus the
two Hub datasets, **PASSED**, and every figure they print equals the one entries 0040 and 0044 record.

**Environment.** Windows 11 laptop, 32 GB RAM, no GPU. Python 3.12.10; torch 2.14.1+cpu, numpy 2.5.3,
tokenizers 0.23.2, tiktoken 0.14.0, huggingface_hub 1.33.0 (both environments), transformers 5.18.0 (upstream).
linear-ceiling at `118d08e`, upstream at `06f8d55592570deae70c3feb9f84a75c4044fb03`, both cloned with
`core.autocrlf=false`, both clean (`git status --porcelain` empty). Datasets pinned to the revisions
`check_hub.py` verified: e8f `17da9aeb69b0`, e9f `ab7d0fd08820`. Traces rebuilt from the committed manifest:
180 SWE-bench files by `e7_manifest fetch`, the 8 tau files from the suites' GitHub raw endpoints, each written
only after its byte count and sha256 matched the manifest; `e7_manifest check` 188 of 188. `results/e7/` was
regenerated by its own driver (`e7 --config config/e7.toml`). The Llama-3.2-3B tokenizer came from the gated
snapshot, read offline during the summaries.

**`summarize_e8 --config config/e8f.toml` — PASSED** (config `cba5e38c8864`, arm (a) cross-checked against the
archived `r2.json` for every k). All 12 cells of the k = 1/4/8 table equal 0040's at printed precision, and both
band columns match: k = 1 K HOLDS / V HOLDS.

**`summarize_e9 --config config/e9f.toml` — PASSED** (config `2e7cade40489`). Equal to 0044: coverage 28 / 36 / 4
of 68; the per-dump RoPE record (85 dumps, max |diff| 1.2e-07, inv_freq `31576ad84e5a` / `8480b7658cd7`);
prefix control 0.000e+00 over 7,435 positions; δ_null 2.004 / 2.015, equal-token pairs 0.0083; matched fraction
0.9304 (0.8794, 0.9788); **median f*(τ_K) same K 0.0000 (0.0000, 0.0000)**, bootstrap [0, 0]; V 0.0000; ladder
τ = 0.1 and 0.03, both read-outs; f*(τ_agent_K) same / cross; blocks ≥ 4; the causal seam profile, all six bins
with their n; cross arm 0.7317 / 0.8148 with p10/p90; cross/same ratios and bridge R² to 0044's printed precision.
Rule line: **HOLDS**.

**The one figure that differs, and why it may.** The keep-subset re-score agreement is "every square within
5.3e-04 relative" here against 0044's 8.8e-04, with per-head sums within 1.5e-07 and max |f* diff| 0. This is the
float32 reduction-order quantity entry 0028 registers a tolerance for (1e-02), so it is a property of the machine
doing the re-score, not of the cell; both machines sit inside the tolerance and neither moves the statistic.

**0044's open question, narrowed.** 0044 records that the E7 report regenerated on the summarizing machine
(`27dc922e3f7d…`) differs from the `0aba0fbe…` the 2026-09-10 long-run summary records, and asserts no cause.
The report regenerated here from the manifest-verified corpus is
`0aba0fbe7aba2f28c7bb62aae47097310179f2d4225afc7dd7e3590a87deb73b` — the 09-10 value. Two independent
regenerations therefore agree, and the 0044 machine's copy is the outlier. The cause is still not established and
none is asserted; what is now known is that `0aba0fbe` is what a clean clone reproduces. As 0044 states, this file
feeds only the descriptive coverage comparison, and the coverage medians printed here agree with it.

```
re-verify: (C:\lc\linear-ceiling) .venv\Scripts\python.exe -m linear_ceiling.summarize_e8 --config config/e8f.toml
re-verify: (C:\lc\linear-ceiling) .venv\Scripts\python.exe -m linear_ceiling.summarize_e9 --config config/e9f.toml
re-verify: sha256 of results/e7/skeleton_report.json after `e7 --config config/e7.toml`   # 0aba0fbe7aba...
```

**What this establishes, and its limits.** Entries 0040 and 0044 are now recomputable from the repository plus a
public backup by someone who was not there, which is R12's requirement; the gap this note was opened to record
is closed. The limits are the summarizers' own: they are the project's code, not an independent reimplementation;
of 0044's 28 handoffs, the 8 kept ones are re-scored from tensors and the other 20 are checked through their
recorded moments and per-token squares (0019's design); and the upstream scorer is the pinned one. A refutation of
the cell is a different exercise from this, and this is not one.
