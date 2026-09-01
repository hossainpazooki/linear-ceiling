# E9 GPU runbook — Algoverse A100, one sitting

**Preconditions (already true):** linear-ceiling `main` at `d633a6d`+ (E9 gated, re-pin
`7e41f792`); upstream `main` at `7e41f792`; `e9 --check` prints ready on a correct checkout.
The countdown starts at APPROVAL, so do steps 1–5 the moment the email lands. Budget: setup
~20 min, run well under 1 h of GPU, sync ~10–30 min. Everything on the box is DELETED at
expiry; nothing may exist only there.

## 1. Clone and pin

```bash
git clone https://github.com/hossainpazooki/linear-ceiling.git
git clone https://github.com/hossainpazooki/kv-transfer-replication.git
cd kv-transfer-replication && git checkout 7e41f792df0a03caa745a52de0ad2bd930e52a47 && cd ..
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

The driver checkpoints `results/e9/report.json` after EVERY handoff — a reclaimed box loses
one handoff, not the run. Keep the process running (idle ~1 h = reclaim risk); do not run
anything else heavy if the card is shared (dumps are bf-free f32 forward passes of 0.6B/1.7B).

## 5. Sync off the box — during the run and again at the end

```bash
# from the local machine, repeat every ~15 min and once after "E9 report:" appears in e9.log
rsync -avz <box>:linear-ceiling/results/e9/ ~/dev/linear-ceiling/results/e9/
```

`results/e9/` must arrive complete: `report.json` (with `"complete": true`), `align/`,
`scores/`, and `scratch/<kept handoffs>/` (the keep-subset dumps — the largest part, possibly
tens of GB; they are what lets the CPU summarizer re-score from tensors). Verify before
logging off: local `report.json` says `"complete": true` and the three kept `scratch/` dirs
match the `kept_dumps` fingerprints (the summarizer will check; a quick `du -sh` sanity that
they are non-trivial is enough on the box). Then log off — do not idle.

## 6. Back home (CPU)

```bash
cd ~/dev/linear-ceiling
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9      # re-derives alignments, R² from moments, re-scores keep subset
```

Exit 0 prints the medians and the band outcome (HOLDS ≥ 0.70 / DEGRADES ≤ 0.40 on median
E9-same K). The H-E9 verdict entry (0021) is written ONLY from that output, in the pattern of
0015/0020. A refusal is a finding, not an obstacle — paste it verbatim.

## If the queue is full / no GPU

E9 on CPU is roughly 0.5–2 min per 1k tokens of prefill per model; the included handoffs are
mostly 3k–25k tokens × 3 prefills — a multi-day CPU job. Options, in order: wait for a slot;
the backup machine (same runbook); or run the ≤8k-token handoffs on CPU overnight and report
coverage honestly. Do not truncate to fit — the cap and exclusions are registered (0019).
