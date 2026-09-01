# linear-ceiling

Instruments for pre-registered, auditable experiments on cross-model KV-cache questions.
Two program lines live here: a **sealed pre-fit screen** (E0 ran; ladder verdict **SAME** on a
vocabulary proxy; the line is **closed**, its hypotheses `SHELVED`), and a **trace-replay
measurement program** over agentic KV-cache workloads — registered, built, and replayed across
three public corpora. Its premise hypothesis is decided: **H-E7a `NOT CONFIRMED`** (mid-trajectory
switch headroom is immaterial on public traces, so the motivation reverts to fleet mixing) and
**H-E7b `UNESTIMABLE`** (no corpus that can evidence compaction shows any). The transfer legs
E8 and E9 are the live hypotheses. The ledger is the authority on state; every figure lives
there or in `docs/`, never here.

```mermaid
flowchart LR
    RULE[rule committed first] --> E0[E0: weights-only screen test]
    E0 -->|SAME under the frozen rule| CLOSED[screen line E1..E6 CLOSED<br/>H-S1/S3/S4 SHELVED]
    E0 --> DEPTH[per-layer depth structure recorded<br/>real vs proxy: both readings open]
    E7[E7 trace-replay: taxonomy, switch-point<br/>headroom, compaction: replayed] --> V7[H-E7a NOT CONFIRMED<br/>H-E7b UNESTIMABLE]
    V7 --> ANCHOR[measurement paper<br/>anchor venue: MLSys]
    E7 -.->|numbers-freeze gate| WS[workshop 4-pager]
    E8[E8 transfer under agent-trace<br/>distribution shift: built, gated] --> ANCHOR
    E9[E9 achievable fraction at the<br/>re-rendered handoff: registered next] --> ANCHOR
```

The scope sentence, held verbatim:

> The screen predicts what a linear mapper can achieve; retention asymmetry beyond that
> prediction is measured and attributed receiver-side, not explained.

## How a number becomes a claim

Nothing enters the ledger by hand. `results/` and `traces/` are gitignored; the only path from
computation to record is a summarizer that **recomputes from the raw inputs and refuses on any
disagreement** — proven by tamper tests, not asserted. Each entry then hash-chains the
registered text above it, so editing a registered entry fails CI.

```mermaid
flowchart LR
    RAW[("traces/ + results/<br/>(gitignored)")] --> S1[summarize_e0]
    RAW --> S2[summarize_e0_depth]
    RAW --> S3[summarize_e7<br/>recomputes from raw traces]
    S1 --> E[numbered ledger entry<br/>immutable once registered]
    S2 --> E
    S3 --> E
    S3 -.->|hash / NaN / recompute mismatch| REF[REFUSE, exit 1]
    E --> H[prior-entries-sha256] -->|recomputed in CI| LC[ledger_check]
```

## The E7 measurement program

Three registered outputs on public agent traces at pinned provider pricing: an invalidation
taxonomy with event frequencies, transfer headroom at model-switch points, and the compaction
break-even distribution. Adapters cover three corpora with incompatible formats; the coverage
floor (trajectories *and* distinct agents per suite, over two suites) is met.

```mermaid
flowchart TD
    T1[tau-bench] --> P[adapters -> one normalized shape]
    T2[tau2-bench<br/>ground-truth usage + timestamps] --> P
    T3[SWE-bench<br/>role/content + LangChain families] --> P
    P --> C[two-bound token/cost timeline]
    C --> A["Lane A: measured switch points<br/>unmeasurable is NOT zero"]
    C --> B["Lane B: counterfactual cascade<br/>descriptive only"]
    A -->|alone decided| HA[H-E7a: NOT CONFIRMED<br/>1.41% vs 10% cutoff]
    A --> HR[headroom at observed handoffs<br/>reported as an UPPER BOUND]
    B -.->|never resolves a hypothesis| DESC[labeled counterfactual]
    C --> TAX[invalidation taxonomy<br/>six classes, each with its own<br/>NOT MEASURABLE state]
    TAX --> CB[compaction events: measured zero<br/>where measurable, so H-E7b UNESTIMABLE]
```

Two properties of the corpora shape every figure. Serving-model identity is recorded per step
by only a minority of formats, so most trajectories are **not measurable** for Lane A and are
never counted as zero. And public traces omit the system prompt and tool schemas the provider
billed, so **every cost figure computed from visible messages is a lower bound** — the omitted
block is byte-identical per request, i.e. the most cacheable content there is. Both are
registered; the measured basis is in the ledger.

## Hard invariants, and what enforces each

1. **Seal before fit** — the seal writer refuses if a fitted mapper exists; CI's `seal verify`
   proves hash integrity and commit immutability only, never the pre-fit ordering itself
   (that is proved by the writer's refusal, on a machine that sees the upstream).
2. **Pre-registration** — verdicts stated against the rule as written; amendments are new
   numbered entries; the entry chain makes silent edits to registered text fail CI. The
   header/table above `## Entries` are editable commentary outside the chain, and a history
   rewrite that regenerates chain or seal is locally undetectable.
3. **No unrecomputed numbers** — summarizers only, fail-closed, tamper-tested.
4. **Experiments refuse until their rules are committed** — the E0 and E7 runners read no data
   until the registering entries and their config are committed and unmodified.
5. **A narrow detector is a defect, never a null** — a probe that cannot see a thing must not
   report its absence; Lane A records the key set it searched alongside its counts.
6. **Determinism** — one seeded generator (`rng.make_rng`); the suite greps for any other.
7. **Scope sentence verbatim, once, in this README** — `lint_scope`.

```mermaid
flowchart LR
    I1[seal before fit] --> C1[seal verify + writer refusal]
    I2[pre-registration] --> C2[ledger_check + entry chain]
    I3[no unrecomputed numbers] --> C3[fail-closed summarizers]
    I4[rules committed first] --> C4[assert_ready gates]
    I5[detector breadth] --> C5[recorded key set + tests]
    I6[determinism] --> C6[single rng + suite grep]
    I7[scope sentence] --> C7[lint_scope]
```

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -e ".[dev]"
pytest
python -m linear_ceiling.seal verify && python -m linear_ceiling.lint_scope && python -m linear_ceiling.ledger_check
```

The suite runs offline in seconds on synthetic fixtures; a green suite proves the tooling, not
any result. The seal writer additionally needs the upstream checked out at
`../kv-transfer-replication` (read-only, pinned — `UPSTREAM.md`; it fails closed if missing).
E7 additionally needs trajectories under `traces/`, acquired locally and never committed.

```mermaid
flowchart LR
    V[uv venv] --> D[install -e .dev] --> P[pytest: synthetic, offline] --> G[seal + scope + ledger gates]
    U[("../kv-transfer-replication<br/>pinned, read-only")] -.->|seal writer only| G
    TR[("traces/ (gitignored)")] -.->|E7 replay only| G
```

## Docs map

| path | role |
|---|---|
| `ledger/ledger.md` | the registered record: hypotheses, verdicts, numbered immutable entries — **start here for program state** |
| `docs/handoff/HANDOFF.md` | handoff index; the newest brief is the pick-up target |
| `docs/learnings/LEARNINGS.md` | non-obvious findings, one per entry, each with a read-only `re-verify:` line |
| `docs/2026-08-26-kv-handoff-screen-design.md` | design spec, verbatim (authority on the original scope; superseded where entries say so) |
| `docs/2026-08-26-seed-w1.md` · `docs/gap-map.md` | W1 seed and E7 gap map, verbatim |
| `docs/2026-09-01-measurement-lane-evidence.md` | why the program re-scoped: paper deltas, pricing pins, venue facts |
| `docs/2026-09-01-swe-bench-trace-recon.md` | trajectory availability, formats, and what they do and do not record |
| `docs/2026-09-01-lcfm-gpu-plan.md` | the LCFM sprint plan with GPU runs: what runs on CPU (E8), what needs the A100 (E9), and what must be registered before each |
| `UPSTREAM.md` | the pinned upstream and the provenance ledger for everything borrowed |
| `CLAUDE.md` | repo brief for agent sessions: commands, layout, binding rules |

```mermaid
flowchart TD
    README[README: essentials] --> LED[ledger/ledger.md<br/>registered record]
    README --> HOF[docs/handoff/<br/>newest brief = pick-up target]
    README --> LRN[docs/learnings/<br/>re-verifiable findings]
    LED --> EV[measurement-lane evidence]
    LED --> RECON[swe-bench trace recon]
    LED --> SPEC[design spec + seed + gap map<br/>verbatim, immutable]
    LED --> UP[UPSTREAM.md<br/>pin + borrow provenance]
```

Status tags used in the ledger: `[VALIDATED]` ran and survived refutation · `[BASELINE]` ran,
numbers in the ledger · `[STRETCH]` designed, not run · `[FUTURE]` not designed ·
`[SUPERSEDED]`. Verdicts: `unresolved` · `HELD` · `NOT CONFIRMED` · `WITHDRAWN` · `SUPERSEDED` ·
`SHELVED` (no experiment ran) · `UNESTIMABLE` (ran; the estimand has no support in the corpus).
