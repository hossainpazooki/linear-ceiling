# E9 GPU runbook — Algoverse A100, one sitting

(Filename misdated; authored 2026-09-01 — see entry 0021. Amended 2026-09-01 for entry 0023.)

**Preconditions (must be true before the request):** linear-ceiling `main` carries entries 0019
AND 0023 with `config/e9.toml` (rule section, τ) committed unmodified; upstream `main` at the
0023 re-pin (the commit adding `--per-token` to `scripts/score_positions.py` and
`scripts/score_mapper.py`; recorded in `config/e9.toml` and `UPSTREAM.md`); `e9 --check` prints
ready on a correct checkout. The countdown starts at APPROVAL, so do steps 1–5 the moment the
email lands. Budget: setup ~20 min, run well under 1 h of GPU, sync ~10–30 min. Everything on
the box is DELETED at expiry; nothing may exist only there.

## 1. Clone and pin

```bash
git clone https://github.com/hossainpazooki/linear-ceiling.git
git clone https://github.com/hossainpazooki/kv-transfer-replication.git
cd kv-transfer-replication && git checkout "$(grep -oE 'upstream_sha = "[0-9a-f]{40}"' ../linear-ceiling/config/e9.toml | cut -d'"' -f2)" && cd ..
```

## 2. Environments (upstream gets CUDA torch; linear-ceiling stays CPU)

```bash
cd kv-transfer-replication
uv venv --python 3.12 .venv && uv pip install torch --index-url https://download.pytorch.org/whl/cu121
uv pip install -e .
cd ../linear-ceiling
uv venv --python 3.12 .venv && uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -e ".[dev]"
.venv/bin/python -c "import torch,sys; sys.path.insert(0,'../kv-transfer-replication')" \
  && ../kv-transfer-replication/.venv/bin/python -c "import torch; print('cuda:', torch.cuda.is_available())"
```

`cuda: True` is required; if False, stop and fix before burning the window.

## 3. Traces (E9 needs only the composio submissions)

From the local machine:

```bash
scp -r ~/dev/linear-ceiling/traces/swe-bench/20241016_composio_swekit \
       ~/dev/linear-ceiling/traces/swe-bench/20241025_composio_swekit \
       <box>:linear-ceiling/traces/swe-bench/
```

## 4. Gate, then run (interpreter is `.venv/bin/python` on Linux)

```bash
cd linear-ceiling
.venv/bin/python -m linear_ceiling.e9 --check      # MUST print "E9 gate: ready"; stop on anything else
nohup .venv/bin/python -m linear_ceiling.e9 > e9.log 2>&1 &
tail -f e9.log                                      # one "[i/N] ... same K ..." line per handoff
```

**Two pre-batch checks run by the driver on the first included handoff (entry 0023), before
that handoff is scored:**

1. **Pipeline identity** — the receiver's dump of `S` scored against itself at pairs `(p, p)`.
   Every per-token square must be exactly zero. A nonzero square prints
   `E9 HALTED: pipeline identity control is nonzero` and the run stops with nothing scored.
   That is a finding about the box or the checkout, not an obstacle to work around: do not
   edit anything on the box; capture `e9.log`, `results/e9/controls/`, and stop.
2. **δ_null** — the same dumps scored with each receiver position paired to a *different*
   matched token's sender position (seeded derangement, `null_seed` in `config/e9.toml`). It
   writes `results/e9/controls/null.*` and decides nothing; it is the top of the deviation scale.

Both records are checked again by `summarize_e9` at home (identity exactly zero; the null
pairing re-derived from the seed). The first `[1/N]` line appears only after both have run.

The driver checkpoints `results/e9/report.json` after EVERY handoff — a reclaimed box loses
one handoff, not the run. Keep the process running (idle ~1 h = reclaim risk); do not run
anything else heavy if the card is shared (dumps are bf-free f32 forward passes of 0.6B/1.7B).

## 5. Sync off the box — during the run and again at the end

```bash
# from the local machine, repeat every ~15 min and once after "E9 report:" appears in e9.log
rsync -avz <box>:linear-ceiling/results/e9/ ~/dev/linear-ceiling/results/e9/
```

`results/e9/` must arrive complete: `report.json` (with `"complete": true`), `align/`,
`scores/`, `tokens/` (the per-token record, ~43 MB per handoff — every 0023 figure is
recomputed from it), `controls/` (identity + null records), and `scratch/<kept handoffs>/`
(the keep-subset dumps — the largest part, possibly tens of GB; they are what lets the CPU
summarizer re-score from tensors). Do NOT let the rsync overwrite the local
`results/e9/calibration/` (made at home before the request; `--exclude calibration/` if the
box has none). Verify before logging off: local `report.json` says `"complete": true` and the
three kept `scratch/` dirs match the `kept_dumps` fingerprints (the summarizer will check; a
quick `du -sh` sanity that they are non-trivial is enough on the box). Then log off — do not idle.

## 6. Back home (CPU)

```bash
cd ~/dev/linear-ceiling
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9      # alignments, moments, per-token sums, keep subset, tau, controls -> f*, profiles, band
```

Exit 0 prints, in R²'s own units (0023): median f*(τ_K) over included handoffs with the band
outcome (HOLDS ≤ 0.15 / DEGRADES ≥ 0.50), V and E9-cross alongside, δ_null, the seam profile,
the own-norm diagnostic, and the bridge R² medians; `results/e9/summary.json` carries the depth
profile and per-handoff rows. The H-E9 verdict entry (**0025** — number allocation lives in `docs/drafts/README.md`; 0024 went to
Track B's corpus manifest) is written ONLY from that
output, in the pattern of 0015/0020. A refusal is a finding, not an obstacle — paste it verbatim.

## If the queue is full / no GPU

E9 on CPU is roughly 0.5–2 min per 1k tokens of prefill per model; the included handoffs are
mostly 3k–25k tokens × 3 prefills — a multi-day CPU job. Options, in order: wait for a slot;
the backup machine (same runbook); or run the ≤8k-token handoffs on CPU overnight and report
coverage honestly. Do not truncate to fit — the cap and exclusions are registered (0019).
