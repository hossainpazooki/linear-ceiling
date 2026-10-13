# Carryover post-acceptance consolidation

Scope: reproduce a small Qwen3-1.7B bridge and extend the same-model measurement to Qwen3-4B and
SmolLM3-3B. No additional mapper fitting, generation benchmark, RL experiment, or serving-cost claim.
The supplied server has one A100-SXM4-80GB and 98 GiB system memory. The card was already provisioned
by the operator; this protocol is committed before experimental forwards, rather than before rental.
The existing hypotheses, tolerances, and verdicts are unchanged; these additions are descriptive.

The packaging review now refuses a partial resume under changed code, libraries, CUDA,
GPU type or dtype, and rejects a completion flag with missing handoffs. This changes
future resume checks only; the completed September 30 measurements are unchanged.

## Fixed inputs and measurement

`config/consolidation.toml` pins model revisions, precision, scaling, thresholds and controls.
`config/consolidation-manifest.json` pins every input byte and all exclusions. The 25 original
short and 35 original long handoff texts are reconstructed from archived Qwen token IDs and checked
against the original text hashes before retokenization. Cohort labels retain the original Qwen
partition; model-specific lengths are reported separately. Inputs exceeding 81,920 tokens are
excluded without truncation. Exact ordered token matching uses the existing E9 implementation.

The original Qwen model is rerun only on the shortest, middle, and longest sender in each cohort.
Its scaled short and long references already exist. Both new models evaluate all eligible original
texts, with one fixed YaRN configuration each (Qwen factor 2.5; SmolLM3 factor 2.0). SmolLM3's
layers without rotary embeddings remain unchanged. The original tolerance is a common numerical
reference for the new models, not a newly calibrated quality threshold or a new registered verdict.

FP32 chunked prefill retains the complete causal KV history; nothing is truncated or quantized.
Keys are captured after any key normalization and before rotation, including unrotated SmolLM3
layers. Values are captured after projection. This avoids numerical inversion of RoPE; unlike the
original archive, intermediate vectors are not serialized as FP16. The bridge explicitly checks
this implementation and environment difference: relative mean-error difference at most 1%, and
absolute f* difference at most 0.01, against the original records. A failure stops expansion and
requires investigation; these bounds are fixed before the first GPU result.

The first check per model compares a full 1,024-token prefill with chunked prefill of that prefix
plus one later token. The maximum normalized token error must not exceed 1e-4. A synthetic offline
test independently checks chunking and causality. The actual longest sender is processed first as
the memory probe and retained for scoring; it is not run again as a separate baseline. Remaining
handoffs run in ascending sender length. Interrupted work resumes from hash-verified completed
handoffs. Report the complete set or explicitly identify a partial set and the reason for stopping.

## Outputs, interpretation, and transport

The scorer saves per-token squared errors, headwise variance denominators, layer profiles, and
per-handoff means, tails and f* at the original threshold and the two existing ladder rungs. One
raw matched-vector witness per model (the shortest included sender) is retained for independent
re-scoring. Other vectors are declared transient and removed only after their compact record and
atomic checkpoint exist. All final records and witnesses are copied to the Desktop evidence folder
and verified by SHA256 before any remote cleanup. No model weights or credentials enter that folder.

The local summarizer verifies squared-error sums, the mean-error/R2 identity and the retained raw
witnesses. It computes model-specific handoff medians and trajectory-cluster bootstrap intervals.
Intervals use the repository's pinned non-interpolated quantile convention. The saved token records
also support a descriptive error budget: token and error shares at least 16 positions after a seam,
and the mean left after removing all nearer tokens. This is deletion under the existing diagnostic,
not an experiment in practical boundary recomputation.
Hardware replicas are never counted as additional handoffs. Original and new models are reported
separately, with a table and no more than six new analysis sentences in the main paper.

The existing four-case mechanism pilot remains exploratory. A separately logged CUDA replay of
that fixed pilot may validate backend agreement; no new intervention search is authorized here.
Any discussion of seams and depth uses saved records and distinguishes association from causation.

## Environment and commands

`tools/consolidation/requirements-{linux,macos}.lock` freeze the environment; `setup.sh` checks
CUDA and installs the repository without changing that lock. The initial CUDA-12.8 wheel lookup
failed before any experiment; the successful locked PyPI wheel uses CUDA 13.0 on driver 580.126.09.
Both local and remote environments use PyTorch 2.14.0 and Transformers 5.17.0.

Local root: `~/Downloads/GitHub/linear-ceiling` on branch `carryover-consolidation`.
Single evidence directory: `~/Desktop/Carryover-evidence`.
Remote owned paths: `~/linear-ceiling`, `~/carryover-venv`, `~/carryover-setup`, `~/carryover-data`.
SSH credentials remain outside all repositories and evidence. Remote Git operations use public
read-only HTTPS and receive no account token. Launch detached, retain setup/run logs, and mirror
every completed handoff. Never overwrite a halted run log or silently relax a check.

```sh
python tools/consolidation/prepare.py
python -m pytest -q tests/test_consolidation_capture.py tests/test_e9_pertoken.py
bash tools/consolidation/setup.sh
python tools/consolidation/download.py
python -u tools/consolidation/run.py --model qwen17_bridge --inputs ~/carryover-data/inputs --output ~/carryover-data/results
# After the home-side bridge verification passes, repeat for qwen4 and smollm3.
```

The local mirror is the source of reported numbers. Preserve the validated environment for the
operator's requested workflow; deleting or terminating the supplied instance is a separate action.

## Upstream migration (2026-10-01)

This is the protocol used for the completed September 30 measurements. Its original
pre-run commit is `3cb4bb3` in `neuriv/linear-ceiling`; the final run code is recorded in
each saved report. Repackaging the code on current upstream main is not a new
registration or a rerun. Fork-only ledger entries 0045/0046 are not appended to the
upstream ledger, where those numbers have a different allocation.

Analysis and the exploratory proximity pilot are separate changes. The execution
path here is `prepare.py` → `run.py`; the stored configuration and input manifest
remain byte-identical to the completed run. Install the pinned experiment environment
for the optional Transformers capture tests; the base repository does not require it.

### Input prerequisite

Restore the verified evidence bundle before running `prepare.py`: it reads
`~/Desktop/Carryover-evidence/archive/records/{e9s,e9l}`. The public sources are
`hossainpazooki/linear-ceiling-e9s-2026-09-13` and
`hossainpazooki/linear-ceiling-e9l-2026-09-10`; their exact dataset revisions are
recorded in `provenance/{e9s,e9l}-source.json` in that bundle. Existing prepared inputs
can be checked directly against `config/consolidation-manifest.json`; do not prepare
or download them again unnecessarily. Model downloads are only needed for new forwards.
`prepare.py` is the historical input builder and rewrites the local manifest; run it in
a scratch checkout and compare the resulting manifest with the committed one.
