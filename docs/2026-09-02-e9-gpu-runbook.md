# E9 GPU runbook — Algoverse A100, one sitting

(Filename misdated; authored 2026-09-01 — see entry 0021. Amended 2026-09-01 for entry 0023.)

**Preconditions (must be true before the request):** linear-ceiling `main` carries entries 0019
AND 0023 with `config/e9.toml` (rule section, τ) committed unmodified; upstream `main` at the
0023 re-pin (the commit adding `--per-token` to `scripts/score_positions.py` and
`scripts/score_mapper.py`; recorded in `config/e9.toml` and `UPSTREAM.md`); `e9 --check` prints
ready on a correct checkout. The countdown starts at APPROVAL, so do steps 1–5 the moment the
email lands. Budget (re-sized 2026-09-02, see §4/§5): setup ~20 min, run ~1–2 h wall (GPU compute is
minutes; dump I/O and CPU scoring dominate), sync ~5–25 min for ~15 GB. Everything on
the box is DELETED at expiry; nothing may exist only there.

**Pre-flight, 2026-09-02, at linear-ceiling `8b6cced` / upstream `36d73b3` (this checkout, CPU only):**
`e9 --check` prints ready; a 48-token dump → `score_positions --per-token` toy on the REAL models
at the pin wrote all six `[n, 28, 8]` float32 arrays and `score.json` named the per-token file
(scratch, nothing under `results/`). Alignment recon over the real corpus (read-only): **68
observed, 25 included, 43 excluded** (`S exceeds context cap 32768` or `receiver prompt is empty
in the trace`); prefill total 1,323,643 tokens (1.7B on S 578,338 + 1.7B on R 166,967 + 0.6B on S
578,338); max |S| 32,123, max |R| 9,698, median |S| 25,460; matched tokens 155,257 (3,362–9,194 per
handoff); keep subset (seed 9) = django-10880_traj#60, astropy-7166_traj#66, django-11066_traj#36,
≈ 14.3 GB of fp16 stride-1 dumps in total; per-token record ≈ 0.7 GB; largest single transient dump
≈ 3.7 GB; the first included handoff (where both controls run) is astropy-13033_traj#80 with
|S| = 29,391. So the box must expect **N = 25** `[i/N]` lines and coverage 25/68 in the verdict entry.

## 1. Clone and pin

```bash
git clone https://github.com/hossainpazooki/linear-ceiling.git
git clone https://github.com/hossainpazooki/kv-transfer-replication.git
cd kv-transfer-replication && git checkout "$(grep -oE 'upstream_sha = "[0-9a-f]{40}"' ../linear-ceiling/config/e9.toml | cut -d'"' -f2)" && cd ..
```

## 2. Environments (upstream gets CUDA torch; linear-ceiling stays CPU)

```bash
cd kv-transfer-replication
uv venv --python 3.12 .venv && uv pip install torch --index-url https://download.pytorch.org/whl/cu128   # see the 09-04 amendment: PyPI torch is now a CUDA 13.0 build
uv pip install -e .
cd ../linear-ceiling
uv venv --python 3.12 .venv && uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -e ".[dev]"
.venv/bin/python -c "import torch,sys; sys.path.insert(0,'../kv-transfer-replication')" \
  && ../kv-transfer-replication/.venv/bin/python -c "import torch; print('cuda:', torch.cuda.is_available())"
```

`cuda: True` is required; if False, stop and fix before burning the window.

Amended 2026-09-02: the original line pointed at `download.pytorch.org/whl/cu121`, whose newest
cp312 wheel is torch 2.5.1 (checked 2026-09-02) — it would pair a year-old torch with a current
transformers 5.x and is not what the local env runs (torch 2.13). If the box has no `uv`:
`python3.12 -m venv .venv && .venv/bin/pip install torch && .venv/bin/pip install -e .` (and
`-e ".[dev]"` for linear-ceiling) is the same environment.

**Amended 2026-09-04, on the box (Algoverse grant, JupyterHub only — no ssh/scp; driven over the Jupyter
REST API + kernel websocket from home).** (i) PyPI `torch` 2.14.0 is a **cu130** build and the box driver is
570.148.08 / CUDA 12.8, so `torch.cuda.is_available()` was False: install from the `cu128` index (2.11.0+cu128
worked). (ii) The grant is an H100 80 GB **MIG 3g.40gb** slice (39.5 GiB), assigned by `CUDA_VISIBLE_DEVICES`;
exclusive by construction. (iii) Entry 0025 raised the keep subset to 8 handoffs = **48.2 GB** retained (the
3-handoff / 14.3 GB figures above are superseded); the box's policy is ≈50 GB of shared disk, so pull each kept
handoff home and delete it on the box as it completes. (iv) **The run OOMed at the first included handoff and
not on the logits**: in float32 with grouped-query heads, transformers' `sdpa` passes `enable_gqa=True`, no
fused kernel accepts that in f32, and PyTorch falls back to the math kernel — the [16, T, T] scores are 51.5 GiB
at T = 29,391 (measured allocation request), so NO single card runs the 0023 pin as-is. Remedy landed at home as
the entry 0026 upstream re-pin (`sdpa_repeat_kv` attention + `logits_to_keep=1`): measured peak 16.5 GiB at
T = 32,123 on the slice, K/V bit-identical to the probe path and within float32 rounding of the math kernel
(max |ΔK| 9.2e-4 on a scale of 423). No cap, dtype or handoff set changed.

**Memory — the card must be yours alone.** The upstream loads both models in **float32**
(`kvt/models.py`, by design of the CPU replication; the plan doc's "bf16" was never what the code
does) and dumps through a CausalLM forward (`kvt/data.py`: `model(input_ids=ids, use_cache=True)`)
that materializes full-vocabulary logits. At |S| = 32,123 that is 32,123 × 151,936 × 4 B ≈ 19.5 GB of
logits, plus ≈ 6.9 GB of 1.7B weights and ≈ 7.4 GB of f32 KV cache (28 × 8 × 128 × 2 × 32k × 4 B):
**peak ≈ 35 GB on the longest handoffs**, and the very first included handoff is 29,391 tokens.
That fits an exclusive 40 GB A100 (or any 80 GB card) and does NOT fit a 20 GB share — the plan's
"fits even shared" sized on KV alone. Analytic estimate; not measured on a GPU. Before §4,
`nvidia-smi` must show the card idle (no other process, ~0 MiB used). A CUDA OOM is a halt, not
a truncate: the 32k cap is registered (0019); the remedy is an upstream change (e.g. a
`logits_to_keep=1` forward) landed as a re-pin entry at home, never an edit on the box.

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

Wall time (2026-09-02 estimate): GPU compute for the whole run is minutes (≈1.3M tokens of
f32 prefill over 0.6B/1.7B); each handoff also writes 3 fp16 stride-1 dumps (≈3–11 GB per
handoff, deleted after scoring unless kept) and scores ≈3–9k matched positions on CPU — budget
≈2–5 min per handoff, ≈1–2 h for N = 25. The "well under 1 h" above was compute only.

The driver checkpoints `results/e9/report.json` after EVERY handoff — a reclaimed box loses
one handoff, not the run. Keep the process running (idle ~1 h = reclaim risk); do not run
anything else heavy if the card is shared (dumps are bf-free f32 forward passes of 0.6B/1.7B).

## 5. Sync off the box — during the run and again at the end

```bash
# from the local machine, repeat every ~15 min and once after "E9 report:" appears in e9.log
rsync -avz --exclude calibration/ <box>:linear-ceiling/results/e9/ ~/dev/linear-ceiling/results/e9/
# Windows Git Bash has NO rsync (checked 2026-09-02): use the tar-over-ssh form instead, same exclusion
ssh <box> 'tar -C linear-ceiling/results -cf - --exclude=e9/calibration e9' | tar -C ~/dev/linear-ceiling/results -xf -
```

Volume: ≈14.3 GB of keep-subset dumps + ≈0.7 GB per-token record + small `align/`, `scores/`,
`controls/` — ≈20–25 min at 100 Mbit/s, ≈3 min at 1 Gbit/s. Pull each kept `scratch/<handoff>/`
as soon as its `[i/N]` line prints rather than all at the end.

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
profile and per-handoff rows. The H-E9 verdict entry (unnumbered until its script is staged; `docs/drafts/README.md` allocates)
is written ONLY from that
output, in the pattern of 0015/0020. A refusal is a finding, not an obstacle — paste it verbatim.

## If the queue is full / no GPU

E9 on CPU is roughly 0.5–2 min per 1k tokens of prefill per model; the included handoffs are
mostly 3k–25k tokens × 3 prefills — a multi-day CPU job. Options, in order: wait for a slot;
**rent one** (below); the backup machine (same runbook); or run the ≤8k-token handoffs on CPU
overnight and report coverage honestly. Do not truncate to fit — the cap and exclusions are
registered (0019).

**Paid fallback (added 2026-09-02).** The whole day is under 3 h on one exclusive A100 40 GB. Lambda
on-demand lists a single A100 40 GB at $1.99/GPU-h and a single H100 80 GB PCIe at $3.29/GPU-h
(pricing page fetched 2026-09-02; availability not checked) — i.e. ≈ $6–10 for the run. The plan
doc's go/no-go (EOD 09-04) should therefore read: no Algoverse approval by then → rent, same
runbook, not "ship trace-only + E8". Any rented single-GPU box satisfies the exclusive-card
requirement in §2 by construction; a 24 GB card (A10, L4, 4090) does NOT — see the memory
arithmetic.

## The request (human-only form; text to paste)

Purpose: one batch job — KV-cache agreement at 25 real agent handoffs (SWE-bench composio
trajectories), Qwen3-0.6B and Qwen3-1.7B in float32, ≈1.3M tokens of prefill at up to 32k
context. Pre-registered measurement (linear-ceiling ledger entries 0019/0023), gate green,
driver checkpointed per handoff, tested end-to-end on CPU at the pinned commit. Needs: one A100
40 GB **not shared** (peak ≈35 GB on the longest handoffs; a 20 GB share OOMs), Python 3.12,
~60 GB free disk (≈14 GB retained dumps + ≈4 GB transient), outbound internet (Hugging Face
model weights ≈10 GB, two git clones), inbound scp/ssh for a ≈30 MB trace upload and a ≈15 GB
results pull. Duration: 1-day grant; active use ≈3 h, then the box is released. Software
installed by the runbook (`uv`/pip, torch + transformers); nothing system-wide.
