# A gate that can be measured for free before the ruling must be: E-TRUNC's 0.80 shrinkage-ratio default would have voided 29 of 35 handoffs

ts: 2026-10-04T09:30:00Z
commit: a2742b9 (HEAD when measured; the E-TRUNC files are uncommitted on top of it)
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: The run queue's default for E-TRUNC's shrinkage gate ("|M_∩| / |M_FULL| < 0.80 voids the handoff") was a guess; the quantity it gates is computable on CPU from the alignment passes before any prefill. Measured over the 35 long handoffs re-aligned at S[−65536:], S[−49152:], S[−32768:]: the ratio has median 0.447 (pooled 0.409), 29 of 35 sit below 0.80, all 35 below 0.90, and 11 handoffs keep NO common token. The loss is mostly physical — the receiver prompt re-renders EARLY sender content that head truncation removes (median survivable fraction 0.503) — with aligner re-matching losing more than the removal on 10 handoffs (up to 0.42 of |M_FULL|). The ruling taken instead is an absolute floor |M_∩| ≥ 2,000 (21 of 35 enter) with the ratio reported, not gating.
basis: `summarize_e9_trunc --shrinkage` at ~09:20Z on the four `e9 --align-only --config config/e9t-*.toml` passes (coverage shas FULL 0b0419ea1d27, L65 c5c3b3d55828, L49 1120282c65b0, L32 d07606d8d3e8); first found by a scratch re-alignment at ~06:40Z with the same per-handoff ratios; the figures are stated by `docs/drafts/append_0055.py --preview` from an in-process recompute.
re-verify: .venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc --shrinkage | grep -E 'median 0.4470|void under .*: 14 handoffs \(11|proposed: 29'   # three lines; needs the four alignment passes under the committed configs
