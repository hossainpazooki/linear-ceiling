# MLSys box plan — which of the three designs runs on a rented L40S, and what each needs first

**Date:** 2026-10-01 · **HEAD at write:** `5a71df6` (= `origin/main`, 0/0) · **Last entry:** 0044 (next free 0047) ·
**Status:** plan only. **No box is launched by this document and nothing here is registered.** Every design below is
unregistered (`docs/drafts/e-{beh,trunc,tail}-design.md`); the operator rules on launches and on every `??? (operator)`.

All prices and limits in §1 were re-fetched live today rather than copied from the 09-10 runbook, per the seed's
instruction. Where a figure is *not* re-fetched, it says so.

## 1. Card, prices and limits — re-fetched 2026-10-01

| item | value | source |
|---|---|---|
| g6e.4xlarge on-demand | **$3.00424/h** (effective 2026-09-01) | Pricing API, `AmazonEC2`, us-east-1, Linux/Shared/Used |
| Data transfer out | **$0.090/GB**, first 10 TB/month (then 0.085 / 0.070 / 0.050) | Pricing API, `AWSDataTransfer`, effective 2026-06-01 |
| EBS gp3 | **$0.08/GB-month** → the default 250 GB root for a 6 h sitting ≈ **$0.17** | Pricing API, `volumeApiName=gp3` |
| Spot, same type | $2.2944–$2.6521/h observed in us-east-1b/c/d | `describe-spot-price-history` |
| Card | L40S, **45,776 MiB**; 16 vCPU, 128 GiB RAM | `describe-instance-types` |
| Offered in | us-east-1**a, b, c, d** (all four of `box.sh`'s subnets) | `describe-instance-type-offerings` |
| Quota, Running On-Demand G and VT | **768 vCPU**; one box needs 16 | `service-quotas`, `L-DB2E81BA` |
| AMI `ami-0eb7d782cce2fe526` | **available** — "Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) 20260907", created 2026-09-07, deprecation **2028-09-07** | `describe-images` |

The $3.00/h and $0.09/GB in the 09-10 runbook (`:29`) therefore **still hold**, and the 768 vCPU quota is unchanged
from the figure recorded on 2026-09-09 (`:16`). The AMI is current; no successor is needed and none is substituted.

**Spot is not recommended** despite the 12–24 % saving: an interruption mid-sitting costs a restart under R4 and a
partial close under the design's own stopping rule, and the two sittings this lane has run both completed inside the
window on-demand (E9-long ≈ $11, E9-scaled ≈ $7). The saving is a few dollars; the cost of a lost prefill is an hour.

## 2. Per design

Forecast overhead, in every row below, is box-up + `setup.sh` + probe ≈ **40 min** and pull/verify/sweep/release
≈ **20 min**, both from the 09-13 sitting's own log (`docs/2026-09-13-e9s-gpu-runbook.md` §6) — an hour of billed time
that is not run time.

### E-TAIL Part B — attention-weighted deviation

| | |
|---|---|
| **Card** | L40S is comfortable; the floor is ~20 GB. Weights 6.41 GiB + ≈2.6 GB per 2,048-query chunk at p90 \|R\|. |
| **Probe** | `probe_e9l.py` is **already generalised** (`EXP`, `MAX_S`, `LADDER`, optional `[e9.rope]`) by `2a30e28` — no sibling is needed to size a *prefill*. But Part B's cost is **not** a `load_model` prefill: it is a chunked eager-attention hook, which this probe does not exercise. Part B needs its own probe (`tools/ec2/probe_tailb.py`, **not written**) that runs the hook at p90 \|R\| and performs the design's identity check (eager K/V vs the archived SDPA dumps, to a tolerance the entry must state). |
| **Forecast** | run **< 1 h** for the 35 → ≈ **2 h billed** → **$6.0 compute + $0.17 disk + <$0.10 egress ≈ $6.3**. |
| **Disk** | No kept dumps; outputs are per-handoff float summaries. The 250 GB default root is ample. |
| **Blocked on** | a **registration entry** (operator) carrying the quantity, the fresh-vs-reused attention choice, the backend pin and the identity tolerance — plus the Proposition 4 attribution quoted verbatim, which the design says is not readable on this machine. Part A's summarizer (Carryover session) is a separate, CPU-only prerequisite for the table Part B sits beside. |

### E-TRUNC — head truncation of the sender context

| | |
|---|---|
| **Card** | **L40S 48 GB required.** FULL peaks 31.56 GiB at \|S\| = 80,111 (`09-10 runbook:127`). A 20 GB slice fits only L32 and L32-native (16.70 GiB at 32,768, `09-13 runbook:96`). |
| **Probe** | one ladder covers all four levels: `EXP=<cfg> LADDER=32768,49152,65536,80111 ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py`. Prefer `MAX_S` taken from `results/<exp>/align/coverage.json` over the config's `context_cap` — the probe's own docstring now says the cap is a *bound*, not the run's longest prefill, and a launch decision should rest on the run's number (80,111 for the E9L cohort, recomputed today from the included alignments). |
| **Forecast** | run ≤ **3 h** realistic, **4–5 h** upper bound (≈3× the E9L sitting) → **4–6 h billed** → **$12–18 compute**, ≈$0.17–0.25 disk, egress small. |
| **Disk** | 250 GB is fine with no kept dumps. If a keep subset is registered per level, budget **114,688 B per token per dump** (`0025:1535`) ≈ **8.6 GB** for one 80K handoff — the keep list sizes the volume, so set `LC_ROOT_GB` with it. |
| **Blocked on** | registration entry; the §5 **margin ruling**; the **L32-native scope** ruling; and `config.py`'s `sender_head_truncate` key, which does not exist and is the Carryover session's code. |
| **Correction to the design** | §8 says L49 differs for "the 18 over 49,152". Recomputed from `results/e9l/align/coverage.json`: **19** of the 35 exceed 49,152. The 18 is the count above the `s_len` **bin edge 49,999**, and one handoff sits at \|S\| = **49,196**, between the two. Immaterial to the hours; worth fixing before the design is registered, since the design states the count as a fact about the cells. |

### E-BEH — behavioral check

| | |
|---|---|
| **Card** | L40S (the S prefill is 31.56 GiB). A 3g.40gb slice is marginal; a 20 GB slice does not fit. |
| **Probe** | the memory question is already answered by `probe_e9l.py` at `MAX_S=80111`. The real gate is **not** a memory probe: it is the design's §9 correctness probe — recomputing *all* tokens in situ must reproduce FRESH bit-for-bit under the pinned backend — and that needs the injection code that does not exist. |
| **Forecast** | ≈ **3 h** run (≈2× E9L) → **4 h billed** → **≈$12 compute** + disk; egress small (per-position KL/argmax summaries). |
| **Blocked on** | the **cache-injection splice** on upstream `kvt/cache.py`, which `0023:1367` requires be **pinned by an entry before it runs**; the continuation extractor out of `traces/`; the bands ruling; and `ledger_check.VERDICTS` learning the `-B` band words (or the entry reusing an existing band). |
| **Recommendation** | **last** of the three for a rented card. Its blocking dependency is code that must be written *and* entry-pinned first; a box rented before that exists would idle at $3/h. |

### Suggested order, if the operator wants one

1. **E-TRUNC** — answers reviewer weakness W2 with the clearest paper sentence, needs no upstream change and no
   injection; its only code item is one `config.py` key. Highest paper value per dollar.
2. **E-TAIL Part B** — cheapest sitting on the list (~$6) and the only one that would fit a 1g.20gb slice if
   Algoverse is ever the host, but it needs a probe that does not exist and Part A ahead of it.
3. **E-BEH** — most informative and least ready.

Nothing above fits an Algoverse 1g.20gb slice except E-TAIL Part B, and a 3g.40gb slice is marginal for FULL-length S.
The Llama LONG cell (0045/0046) needs 80 GB and is not a g6e job at all.

## 3. Release path (R7), and one trap to fix before any sitting

- Step 0 listing first (`ls ~` and `ps -u`), then `EXP=<exp> tools/ec2/release_sweep.sh`, then terminate with a
  durable read-back recorded in the runbook at the time — the `terminated` state re-verify line **rots**, because EC2
  forgets terminated instances (09-10 brief's own correction).
- The `${EXP}.records.sha256` generalisation from 09-14 **is on main** (`release_sweep.sh:7,32`), so a second sweep
  under a new `EXP` no longer flags its own records file as foreign.
- **Trap:** `OURS_FILES` (`release_sweep.sh:7`) is a *fixed allowlist of the e9l/e9s filenames*. Any new file the next
  sitting puts in `~` — `probe_tailb.py`, a per-level driver, extra configs — will be reported `NOT OURS` and the sweep
  will return `foreign=1` on a clean box. Extend `OURS_FILES` in the **same change that adds the file**, before the
  sitting, not while trying to release a running box.

## 4. What waits on which ruling or entry

| row | waits on | owner |
|---|---|---|
| E-TAIL Part B launch | registration entry (quantity, backend pin, identity tolerance, Proposition 4 quote) | operator |
| E-TAIL Part B probe | `tools/ec2/probe_tailb.py` + the identity check | this lane, once registered |
| E-TAIL Part A | the fail-closed `--tail` reader; the owed corrective f* entry as carrier | Carryover session / operator |
| E-TRUNC launch | registration entry + margin ruling + L32-native scope ruling | operator |
| E-TRUNC code | `config.py` `sender_head_truncate`, tested | Carryover session |
| E-BEH launch | injection splice pinned by an entry; continuation extractor; bands + `-B` verdict words | operator, then build |
| Short cell riding along | **Condition 1 (0032) is still open** — `docs/2026-09-14-condition-1-status.md:177` says this board does not release 0029's figures and the admission outcome must be recorded in a later numbered entry. Until then the short half is a separate cell and enters no registered verdict. | operator |
| Any of the above on AWS | nothing technical: quota, AMI, card and prices are all clear today | — |

## 5. Not done here

No instance created or started. No ledger entry appended, no entry edited, no design draft edited (every comment on a
design is in §2 above or in the refresh brief). No git history written. No Hub visibility change. No credential repair:
the `default` AWS profile is dead (`InvalidClientTokenId`, re-confirmed today) and stays that way — `kv-platform-admin`
is the working profile.
