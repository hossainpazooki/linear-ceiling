# linear-ceiling

Pre-registered, auditable experiments on cross-model KV-cache questions: what the public
agent-trace record can evidence about cache economics, and whether a linear cross-model KV map
survives real agent text and real re-rendered handoffs. Every rule is committed before its run;
every number enters the ledger only through a fail-closed summarizer; entries are immutable and
hash-chained. `ledger/ledger.md` is the authority on state.

> The screen predicts what a linear mapper can achieve; retention asymmetry beyond that
> prediction is measured and attributed receiver-side, not explained.

## Aims

- **LCFM @ NeurIPS 2026 short paper** (4 pages, deadline 2026-09-10 AoE; numbers freeze EOD
  2026-09-08). Framed as an evaluation of what public agentic long-context traces can and cannot
  show. Outline: `docs/paper/2026-09-06-lcfm-outline.md`; preface source:
  `docs/2026-09-06-gap-map-revisited.md`.
- **MLSys 2027 measurement paper** (anchor venue; due 2026-10-30). Same record, full length.
- **E-RL** (KV reuse across RL post-training checkpoints): design only, unregistered.

## Status

| hypothesis | verdict | entries |
|---|---|---|
| H-E7a — switch-point headroom is material on public agent traces | **NOT CONFIRMED** (registered reading; request-level reading recorded, ruling: registered) | 0015, 0018, 0022, 0024 |
| H-E7b — compaction break-even has substantial negative mass | **UNESTIMABLE** | 0015 |
| H-E8 — the fitted cross-model map survives agent-text content shift | **NOT CONFIRMED** | 0020 |
| H-E9 — KV agreement at a real re-rendered handoff keeps its usefulness | **HELD**, read on a floor; cross arm beyond DEGRADES (descriptive) | 0029 (0023, 0025, 0027) |
| H-S1…H-S4 (pre-fit screen line) | `SHELVED` / H-S2 first clause `NOT CONFIRMED` | 0003–0006 |

Descriptive amendments, no cell moves: 0030 (E8 arm (b) over every agent sequence; figures in
0031) · 0032 (E9 admitted to the 4-pager) · 0033 (calibration-size sensitivity: the k = 1 mapper
refit on n = 420 sequences, E8 arms and the E9 kept-subset cross arm re-scored; registered before
the fit) · 0034 (its figures).

**Now:** freeze → the 4-pager.
Newest brief: `docs/handoff/HANDOFF.md`.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -e ".[dev]"
pytest
python -m linear_ceiling.seal verify && python -m linear_ceiling.lint_scope && python -m linear_ceiling.ledger_check
```

The suite runs offline on synthetic fixtures; green proves the tooling, not a result. E7 needs
trajectories under `traces/` (local, never committed; rebuilt from `config/e7-manifest.json`);
E8 and E9 invoke the pinned upstream (`UPSTREAM.md`) by subprocess and refuse if its pin does
not hold. Commands per experiment: `CLAUDE.md`.

## Backups (Hugging Face)

`results/`, `data/` and `traces/` never enter git history, so the only off-machine copy of a
GPU run's tensors is a **private Hugging Face dataset**, pushed from the verified home mirror
after every sitting (protocol R8 in `docs/gpu-experiment-protocol.md`). Three rules bound it:

- **Transport, not evidence.** A summarizer reads the local mirror only; nothing on the Hub is a
  ledger figure, and a refusal at home is a finding, never something a re-download works around.
- **Every file verified in both directions.** Each LFS file's `lfs.sha256` must equal the local
  sha256; each non-LFS file is downloaded and hashed; every local file must be on the Hub and
  vice versa. `tools/hf_verify_backup.py <repo_id> <local_root>` is that check and exits 0 only
  when all of it holds.
- **Tokens are scoped, expiring, and live only in the environment.** Write tokens for the pusher,
  read tokens for collaborators; a token pasted anywhere is revoked. A private user-namespace
  dataset cannot be shared per user, so a collaborator gets a read token.

| dataset | holds | layout at the dataset root |
|---|---|---|
| `hossainpazooki/linear-ceiling-e9-2026-09-04` | the E9 record (entries 0026–0029): `report.json`, `align/`, `controls/`, `scores/`, `tokens/`, box logs, and the kept full dumps | `results/e9/` as in this repo, plus the fitted mapper `mappers/qwen3-0.6b-to-1.7b/k1.*` in the upstream's layout |
| `hossainpazooki/linear-ceiling-n420-2026-09-08` | the n = 420 calibration pair behind entries 0033/0034, the tagged mapper and its `r2.json`, the sitting's box logs and sha manifests | the upstream's own layout: `data/kv/qwen3-0.6b-to-1.7b-n420/`, `mappers/qwen3-0.6b-to-1.7b/n420/`, `results/mapper/qwen3-0.6b-to-1.7b/n420/` |

Restore, with a read token in `HF_TOKEN`:

```bash
# E9: results/ lands in this repo, the mapper in the upstream checkout
hf download hossainpazooki/linear-ceiling-e9-2026-09-04 --repo-type dataset --local-dir /tmp/e9-restore
cp -r /tmp/e9-restore/results/e9 results/ && cp -r /tmp/e9-restore/mappers ../kv-transfer-replication/
python tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9-2026-09-04 /tmp/e9-restore

# n = 420 pair: upstream layout, so it lands directly in the upstream checkout
hf download hossainpazooki/linear-ceiling-n420-2026-09-08 --repo-type dataset --local-dir ../kv-transfer-replication
python tools/hf_verify_backup.py hossainpazooki/linear-ceiling-n420-2026-09-08 ../kv-transfer-replication
```

After a restore the gates decide, not the download: `e9 --check`, `e8 --check --config config/e8c.toml`
and `e9_rescore check --config config/e9c.toml` must print ready before any summarizer runs.
Large pushes use `hf upload-large-folder --num-workers 1` on Windows (multi-worker uploads
stall); the dataset card goes last.

## Docs map

| path | role |
|---|---|
| `ledger/ledger.md` | the registered record: hypotheses, verdicts, numbered immutable entries — **start here** |
| `docs/handoff/HANDOFF.md` | handoff index; the newest brief is the pick-up target |
| `docs/learnings/LEARNINGS.md` | non-obvious findings, one per entry, each with a `re-verify:` line |
| `docs/paper/2026-09-06-lcfm-outline.md` | the LCFM 4-pager outline: every figure with its entry and freeze status |
| `docs/2026-09-06-gap-map-revisited.md` | the 2026-08-26 gap map read against the ledger: each claim with its verdict |
| `docs/gap-map.md` · `docs/2026-08-26-seed-w1.md` · `docs/2026-08-26-kv-handoff-screen-design.md` | the original motivation, seed and design spec, verbatim and immutable |
| `docs/background.md` | program history and vocabulary |
| `docs/2026-09-01-measurement-lane-evidence.md` | why the program re-scoped: paper deltas, pricing pins, venue facts |
| `docs/2026-09-01-swe-bench-trace-recon.md` | trace formats and what they do and do not record |
| `docs/2026-09-02-e9-gpu-runbook.md` · `docs/2026-09-08-n420-target-dump-runbook.md` · `docs/gpu-experiment-protocol.md` | the two GPU sittings; standing rules R1–R12 |
| `tools/jupyterhub/` · `tools/hf_verify_backup.py` | the JupyterHub box driver and pull loop; the two-direction backup verifier |
| `docs/2026-09-08-seed-e9-long-half.md` | seed for E9 on the long half of the handoffs, unregistered; needs a 3g.40gb slice or a full card |
| `docs/2026-09-02-e-rl-design.md` | E-RL design, unregistered |
| `docs/drafts/` | append scripts for entries not yet written; the README there is the only number allocator |
| `UPSTREAM.md` | the pinned upstream and the provenance ledger for everything borrowed |
