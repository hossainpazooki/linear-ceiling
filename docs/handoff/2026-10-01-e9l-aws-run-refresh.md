# Pick-up — `e9l-aws-run` refreshed on the 10-01 seed: one row drifted, AWS clear, no box requested

**2026-10-01** (session `e9l-aws-run`). **HEAD `5a71df6` = `origin/main`, 0 ahead / 0 behind** (fetched at pick-up).
**Last entry 0044; next free 0047.** Gates green: `ledger ok (blocks unchanged vs HEAD)`, `scope ok`,
`seal verify → OK (no sealed predictions yet)`.

Brief picked up = the 09-14 close `2026-09-14-e9s-closed-backup-verified-and-a-second-session-on-condition-1.md`
(describes `a5053b2`) **+** the seed `~/dev/briefs/2026-10-01-seed-e9l-aws-run-context-update.md`. The seed's §1 rows
were re-verified one by one rather than trusted; results below. Working tree: only `?? docs/paper/tex/` plus this
session's two new files. **Nothing was launched, appended or committed.**

## Entry gate and money

- `aws sts get-caller-identity --profile kv-platform-admin` → **547729607601**. The `default` profile is **dead**
  (`InvalidClientTokenId`) — re-confirmed, **not repaired** (seed §4).
- `describe-instances` (us-east-1) → **only `i-0785c090815238989`, t3.micro, `stopped`**, not this project's.
  **Nothing of ours is running and nothing is billing compute.**

## §1 re-verification

| seed row | verdict | evidence |
|---|---|---|
| 0039–0044 on main, H-E9F HELD 28/28, PR 5 `3902a16` | **confirmed** | all six headers present (`0040` E8 second family, `0041` τ-ordering, `0042` short-cell registration, `0043` pre-prefill amendment, `0044` H-E9F HELD); `3902a16` = "Merge pull request #5 from hossainpazooki/llama-second-family" |
| `tools/runpod/` exists as a second box path | **confirmed, count off** | **29** commits touch `tools/runpod`, not 19 |
| **`tools/ec2/` and the protocol doc unchanged since 09-14** | **DRIFTED — the one row that failed** | `2a30e28` (Emerson Yu, 2026-09-18) changed **`tools/ec2/probe_e9l.py` (+38/−…) and `tools/ec2/setup.sh` (+122/−21)**. `docs/gpu-experiment-protocol.md` *is* unchanged. See the note below — this is my lane's own tooling and it changed **for the better**. |
| Llama R8 backups under the co-author's account, public | **confirmed** | `emmmy/linear-ceiling-e8f-2026-09-18` and `emmmy/linear-ceiling-e9f-2026-09-19` both `"private":false` |
| the two empty `hossainpazooki/…-e8f/e9f` datasets are to be deleted | **confirmed still present** | both API endpoints return **200** — operator's delete, not done |
| R12 gap closable: `06f8d55` not an ancestor of the clone tip | **confirmed** | `merge-base --is-ancestor` → **rc 1**; clone tip `9ca6258`. Read-only; no checkout or fetch there |
| LCFM/NeurIPS accepted; MLSys 2027 Oct 30 | not re-verifiable from the repo (OpenReview PDF outside it) | taken as given; no claim of mine rests on it |
| three designs on main at `e0bd810`, thresholds `??? (operator)` | **confirmed** | `e-beh` 6, `e-trunc` 3, `e-tail` 2 placeholder hits; all three dated 09-30, HEAD-at-write `118d08e` |
| numbering: 0045/0046 staged, next free 0047, never run `append_0039.py` | **confirmed, README line stale** | `docs/drafts/` holds `append_0039.py`, `append_0045.py`, `append_0046.py`. But `README.md:21` still says "**Four** drafts staged … `append_0043.py`, `append_0044.py`, 0045, 0046" — 0043/0044 are **on the ledger** and their scripts are gone. The allocator's own staging list is stale by two; flagged, **not edited** |
| housekeeping: key pair + `lc-e9l-ssh` still exist; HF token unverified | **confirmed** | `lc-e9l-2026-09-10` in `describe-key-pairs`; `sg-03021d0b6c09b4c75 lc-e9l-ssh` in `describe-security-groups`. **The HF write-token revocation from 09-14 is still unverified by me** — it was open then and is open now |

### The drifted row, in detail — and why it helps

`2a30e28` **generalised `probe_e9l.py`**: it now takes `EXP`, `MAX_S` and `LADDER`, treats a missing `[e9.rope]` as the
model's native RoPE instead of an error (`rope = None`, `load_model`'s unscaled path), prints `pair`,
`max_position_embeddings`, the ladder and **`top_rung_from`**, and documents that the config's `context_cap` is a
*bound*, not the run's longest prefill — so a launch decision should use `MAX_S` from `align/coverage.json`. Its
`setup.sh` companion fix made an **E8** sitting bringable-up at all (it used to demand the mapper that sitting A exists
to create, and ran the e9 gate on an `[e8]` config).

Consequence for deliverable 2: the seed asks for "`probe_e9l.py` generalised or a sibling". **It is already
generalised** — no sibling is needed to size a prefill. A sibling *is* still needed for E-TAIL Part B, whose cost is a
chunked eager-attention hook rather than a `load_model` prefill. Recorded in the box plan §2.

## Figures I recomputed before quoting them

- **Confirmed to the digit** from the cited lines: peak **31.56 GiB** at |S| = 80,111 and **1.5–3 min per handoff**
  (09-10 runbook `:127`, `:139`); **16.70 GiB** at T = 32,768 and weights **6.41 GiB** (09-13 runbook `:96`).
- **|S| recomputed** from `results/e9l/align/coverage.json` (35 included): min 34,974, **max 80,111**; 35 over 32,768,
  **19 over 49,152**, 4 over 65,536.
- **One design figure is off by one.** `e-trunc-design.md:§8` says L49 differs for "the **18** over 49,152". It is
  **19**: the 18 is the count above the `s_len` **bin edge 49,999**, and one handoff sits at |S| = **49,196**. Hours
  unaffected; the design states it as a fact about its own cells, so it should be fixed before registration. **I did
  not edit the design** (seed §4).
- **|R| p10/p90 = 7,085 / 19,853 stands**, and is the summarizer's own figure
  (`summary.json → coverage_comparison.included.n_receiver`), which is the only authority under R11. My independent
  linear-interpolation recompute gave **7,354 / 18,998**; both the summarizer's values are *observed* |R| values, so it
  uses nearest-rank. A convention difference, not an error — but worth knowing before anyone "corrects" the design.
- **Condition 1 is still open**: `docs/2026-09-14-condition-1-status.md:177` — this board does not release 0029's
  figures and the admission outcome must be recorded in a later numbered entry. So the short cell may **not** ride
  along into any registered verdict.
- My own 09-14 fix survived: `release_sweep.sh` uses `${EXP}.records.sha256` at both `:7` and `:32`.

## Deliverables

1. **This brief** + its `HANDOFF.md` row.
2. **`docs/2026-10-01-mlsys-box-plan.md`** — per design: card, probe command, hours, dollars at today's re-fetched
   prices, disk sizing, release path, and what waits on which ruling. **No launch.**
3. **AMI and quota re-check (read-only):** `ami-0eb7d782cce2fe526` **available**, "Deep Learning Base OSS Nvidia Driver
   GPU AMI (Ubuntu 22.04) 20260907", deprecation **2028-09-07** — current, no successor substituted. Quota
   *Running On-Demand G and VT* = **768 vCPU** (one box needs 16), **unchanged** from the figure recorded 2026-09-09.
   g6e.4xlarge is offered in **us-east-1a/b/c/d**. Prices re-fetched live: **$3.00424/h**, **$0.090/GB** egress,
   **$0.08/GB-month** gp3 — the runbook's $3.00/$0.09 stand.
4. **Housekeeping, proposed not run:** delete or keep `lc-e9l-2026-09-10` and `sg-03021d0b6c09b4c75` (`lc-e9l-ssh`) —
   both cost nothing, both are the operator's call; the only argument for deleting is that a stale tagged SG invites a
   future launch into an unreviewed ingress rule. The `default` profile is dead and was left dead.

## Open / next

1. **Commit this session's two files** (operator), explicit paths — not `docs/paper/tex/`, which is another session's:
   `docs/2026-10-01-mlsys-box-plan.md`, `docs/handoff/2026-10-01-e9l-aws-run-refresh.md`, `docs/handoff/HANDOFF.md`.
2. **Rulings needed before any box can be requested** — none of them mine:
   E-TAIL Part B registration (quantity, backend pin, identity tolerance, the Proposition 4 quote);
   E-TRUNC margin ruling + the L32-native scope ruling (and the `sender_head_truncate` key, Carryover's code);
   whether the short cell may ride along, which **Condition 1 currently forbids**.
3. **Carried, not closed:** HF write-token revocation (R9, unverified since 09-14); the two empty `hossainpazooki`
   datasets to delete; the stale `docs/drafts/README.md` staging list; `e-trunc-design.md`'s 18→19; the R12 gap on
   0040/0044, which is the Carryover session's.

## Invariants (unchanged, restated because they bound the next step)

- `results/`, `data/`, `traces/` never enter git history. Entries 0025–0044 are immutable; a correction is a new entry.
  `docs/drafts/README.md` is the only number allocator — **0047 is the next free number, and `append_0039.py` carries a
  taken one: never run it.**
- No figure enters the ledger or the paper that a fail-closed reader did not produce in-process (R11).
- Git history is the operator's; stage explicit paths, never another session's files; no attribution trailers.
- `git clean -x`/`-X` deletes the gitignored `results/` tree every re-verify line above reads from.
- Before any sitting: extend `release_sweep.sh`'s `OURS_FILES` for every new file the box will hold, or the sweep
  reports `NOT OURS` on a clean box (box plan §3).
