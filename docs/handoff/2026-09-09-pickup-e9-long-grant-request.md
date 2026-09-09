# Pick-up — E9-long: the 3g.40gb grant request, with the seed's numbers re-verified

2026-09-09 18:00Z (session `018fwd19`). Picks up `docs/2026-09-08-seed-e9-long-half.md` (written 09-08, revised 09-09
at `4eafe40`). Newest commit at pick-up: `adb181f` = five doc-only commits after the seed; tree clean except an
untracked `.claude/`. Upstream `kv-transfer-replication` on `main` at `4633718`, no YaRN commit. Deliverable: the
answers for the Algoverse H100 request form, standing only on numbers recomputed this session, plus the premises
the operator must rule on before filing.

## State, as verified now

| claim (seed §1) | status | evidence |
|---|---|---|
| 1.7B fp32 peak 16.72 GiB at T = 32,768; OOM at 40,960 on a 19.62 GiB 1g.20gb slice | verified-now | `docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.out`, rows read directly |
| Long half: 39 excluded for cap; +35 newly included at cap 81,920; \|S\| 34,974–80,111; 4 above cap and 4 empty-R by name | verified-now | recomputed from the 68 `results/e9/align/*.json` records (`n_sender`, `reason`) |
| Prefill budget 3,970,435 tokens (2·ΣS 1,771,353 + ΣR 427,729) | verified-now | same records |
| \|R\| on the long set: median 11,462, max 25,073 | verified-now | same records (seed says median 11,500; rounding) |
| Extrapolated 1.7B peak at T = 80,111 ≈ 29.2 GiB; KV alone 17.1 GiB fp32 | verified-now as an **extrapolation** | 0.6B ladder slope 276 KiB/token (13.07 − 10.91 GiB over 8,192 tokens) applied from the 1.7B 32,768 point; the seed's "283 KB/token" is the same slope in decimal KB |
| 09-04 E9 sitting wall | verified-now | `results/e9/logs/box/e9.log`: 25 handoffs, 2,175 s of driver time (36 min) for 1,323,643 tokens on 3g.40gb |
| §3 items 1–4 (upstream YaRN, `config/e9l.toml`, drafts, gate) | not started | no `config/e9l.toml`; `grep yarn\|rope_scaling ../kv-transfer-replication/kvt/*.py` empty; 09-09 closing brief says "not started" |
| Entry gate | green | `ledger_check` → `ledger ok (blocks unchanged vs HEAD)`; `pytest -q` → 401 passed, 1 skipped |

## Drift the brief doesn't know

`41fb04b`, `4d26803`, `776c976`, `0f6b6c3`, `adb181f`: HF backup verifier and protocol quick-reference, learnings,
the LCFM pick-up brief, ruling (b) executed detached, six learnings. None touches the seed's named files or its
numbers. The 09-09 closing brief adds one constraint the seed already states: E9's own summarizer keeps needing a
detached `d5786df` checkout, so the YaRN commit is free to land on upstream `main`.

## Contradicted premises (for the operator)

1. **R1 "registered before requested" vs a 4-day 40 GB queue.** Nothing for E9-long is registered. R1's premise
   was that approval is fast enough that registering first costs nothing; the form now says both 40 GB slices are in
   use with 6 teams waiting. Filing now and registering during the queue is an R1 breach unless R1 is amended to
   "registered before the window opens." Recommendation: file now and write that amendment explicitly into the
   protocol, never a silent breach.
2. **The seed promises a measured peak at T = 80,111 before the request** (§3 item 5, and the request abstract's
   last sentence). That probe needs a ≥ 30 GiB card, which only this grant provides; there is no GPU at home. The
   request must carry the extrapolation, labeled as such.
3. **The form pushes the AWS $200 credit first.** An L40S 48 GB single-GPU instance (g6e.xlarge, roughly $2/h
   on-demand) would fit 29 GiB and cost under $20 for the sitting, with no queue. Price, G-instance quota and
   availability were NOT verified this session. If the account has quota, this is a real alternative the admin will
   raise; if not, the request should say so in one clause.
4. **bf16 would fit 20 GB** (KV 8.6 GiB + 3.4 GiB weights at 80K, before activations). Recommendation against: the
   instrument is fp32 by pin 0026 and tolerance 0028, and a dtype change on top of YaRN gives the bridge control two
   confounds at once; in bf16 SDPA also leaves the math kernel, a second numerics change.

The form's own slot counts disagree (intro: 1 × 12 h, 1 × 24 h, 10 × 48 h; picker: 1 / 4 / 7). Not ours to fix.

## The form, answered

Fields the repo cannot fill: team name as it appears in Slack, teammate emails, the AWS credit line. Prior grant
logins were `rrhs-fe3a-xl` (09-04) and `rrhs-66f0` (09-08), so the team code is very likely `rrhs`. Mentor field:
leave blank unless the mentor has been looped in since.

- **Your email:** `hossain@pazooki.com`.
- **What are you running:** Inference (closest of the four; see "Anything else").
- **Why does this need an H100:**

```
Forward-only extraction of the KV cache of Qwen3-1.7B in float32 (pinned code path) on 35 agent
handoffs whose prompts are 35K-80K tokens, comparing K at re-rendered vs original positions. No API
exposes KV tensors, so it must run locally. Measured on this cluster's 1g.20gb slice on 2026-09-08
(torch 2.11.0+cu128, same code): 1.7B peak 16.72 GiB at 32,768 tokens, OOM at 40,960. The shortest
prompt in this set is 34,974 tokens, so nothing here fits 20 GB, a T4 (16 GB) or an L4 (24 GB).
Extrapolated peak at the longest prompt (80,111 tokens) is ~29 GiB from the measured ladder (KV
alone 17.1 GiB fp32 + 6.4 GiB weights + activations). The 40 GB slice fits with ~10 GiB headroom;
a full card is not needed. Compute is seconds per forward; the sitting is bounded by dump I/O and
CPU scoring.
```

- **AWS credit status:** paste the console line. If the credit cannot be used, one clause why (no G-instance quota,
  or the single-GPU 48 GB instance not approved).
- **How long:** 24 hours. The 09-04 run took 36 min of driver time for one third of these tokens on the same slice;
  this run is quadratic in a 2.5× longer context, plus 3 bridge handoffs and ~60 GiB of kept dumps pulled over the
  JupyterHub websocket. Estimate 3–6 h of work. The 12 h window (~8 h usable) fits only if no launch is refused, and
  09-04 burned two refused launches. The tier does not change the 40 GB queue position; the two slices are the
  constraint.
- **GPU memory:** tick the 40 GB box; justification is the measured OOM at 40,960.
- **Anything else:**

```
Same-model KV reuse at re-rendered agent handoffs (successor to runs on this cluster 2026-09-04 and
2026-09-08). 35 handoffs, ~4.0M prefill tokens, Qwen3-0.6B/1.7B, fp32. Detached batch driver, no
interactive use; artifacts pulled and verified per handoff and backed up to a private HF dataset;
release checklist frees the machine as soon as the driver exits.
```

## The two clocks

LCFM submission deadline: **2026-09-10 23:59 AoE** (Anywhere on Earth = UTC−12) = **2026-09-11 11:59 UTC** =
**2026-09-11 07:59 EDT** (the operator's local zone, confirmed with `date` at pick-up: 13:58 EDT = 17:58 UTC on 09-09).
About 42 hours from this brief. A 4-day 40 GB queue cannot deliver E9-long before it, which is the seed's own framing:
the long-half result goes to the camera-ready or the MLSys version, never into a figure the 4-pager already carries.
The grant request and the submission are on separate clocks; neither waits on the other.

## Confirmed next

1. **Operator:** rule on premises 1 and 3 (file now under an explicit R1 amendment, or build §3 first; AWS L40S or
   the Algoverse queue). Then fill the three fields the repo cannot, and file.
2. **D1–D5** from the seed, then the §3 build order; the registration entry is 0035 if staged before anything else.
3. The 4-pager is on its own clock (item 4 of the 09-09 closing brief).
