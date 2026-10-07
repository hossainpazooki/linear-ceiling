# The submitted camera-ready (`6c706bef…`) reconciled against the ledger, the Lean formalization and the two operator runs

**Date:** 2026-10-07 · **Status:** review record, operator-side (same machine and mirrors as the runs; not independent of
them). Not a ledger entry, not a manuscript edit. It types no figure: every number is quoted from the PDF, the ledger, a
summarizer output or `proofs/Carryover/Numbers.lean`.

**Baseline.** The submitted PDF `126_KV_Cache_Drift_Across_Hand.pdf`, sha256 `6c706bef9aff9cc4f77802240f7457ea08e67c170f44a49877f45b9679a2ebd6`,
14 pages, built 2026-10-04 23:08:41Z (recorded in `docs/2026-09-30-review-response-map.md`, last section). PR #18's
evidence map (`docs/camera-ready-evidence-map.md`, open) reconciled a DIFFERENT build (`be90e0af…`, 06:16Z); this record
re-runs its 49 rows against the submitted text and adds what the operator runs (entries 0048 appended, 0049 staged)
now source. Method: text extracted with pypdf (split numerals healed), each row's quoted claim and 4-digit figures
string-matched, then targeted phrase probes for every row whose verbatim quote was absent (the builds differ in wording).

## 1. PR #18 rows against the submitted build

**23 rows match verbatim** (quote and figures present). Of the 26 others:

| disposition | rows | what the submitted text actually says |
|---|---|---|
| **Moot — the flagged sentence is not in the submission** | 5, 6, 7 | "governs" / "structure of the reuse error": 0 hits; "viable alternative to recomputation": 0 hits; row 7's sentence became "A matched YaRN rerun measures configuration sensitivity: the zero median persists at the reference while stricter-tolerance results change" — #18's proposed UPDATE was applied between the builds. |
| **Resolved — now sourced by an operator run** | 21, 31, 35 | SmolLM3's single long handoff at f*(τ_K) = 0.0228 (0048: `django__django-10554_traj#112`, 0.0228); every Table 7 interval, 28 of 28 numbers, equals 0048's trajectory-cluster bootstrap to the digit; App. F's conditional weighted deviation 0.3012 equals 0049's summarizer (0.30119). These figures came from private bundles when #18 was written; the registered runs reproduce them. |
| **Stands — present in different wording** | 1, 2, 3, 4, 12, 17, 24, 26 | abstract: "35K–80K-token sender histories and 3.4K–25.1K-token receiver prompts"; "the median same-model removal fraction is zero. At a stricter tolerance of 0.03, it rises to 53% of matched tokens"; "The zero median at the reference also appears for Qwen3-4B and SmolLM3-3B"; 0.1424 / 90.20 present; Theorem 1 sentence present; "only τ_K determines the verdict … do not enter that decision"; "These pooled medians do not isolate …"; "these ratios cannot explain how much of the gap is caused by configuration or length". All KEEP; rows 3 and 4 still lack the 0056 provenance sentence. |
| **Stands — the flagged problem is in the submission** | 11, 32, 14, 37, 38 | "Co-author review of the native-context result is still pending" (§3) and "The co-author review of the short-cohort results (Section 3) is still open" (App. D) — stale against 0054; "oracle removal fraction" ×3, "removal fraction" ×13, "recompute" ×3; App. A "not a general lower bound on that cost" and App. D "f* is not an achievable recomputation or runtime cost" — the reading 0054 declined to adopt. |
| **Unchanged — rows about absences or judgment** | 8, 13, 15, 18, 27, 40, 45, 48, 49 | nothing to string-match; #18's dispositions stand (no tail sentence, no floor qualifier, no E-TRUNC result, no Llama, no Lean claim). |

Net: #18's Q4/A1 (lower-bound wording, the two stale sentences) and the missing 0056 provenance clause remain the
substantive defects; its rows 5–7 can be closed, and rows 21/31/35 change from HOLD to "sourced by 0048/0049".

## 2. Figures from the private bundles against the operator runs

- **Table 7** (Qwen3-4B / SmolLM3-3B × short / long: f*_K(0.03) median and 95 % CI, f*_V(τ_V), f*_V(0.03) and CI): all
  28 printed numbers equal `results/consolidation/a100/summary.json` (entry 0048's reader) at 4 decimals.
- **App. F** (the cache-behavior follow-up): 14 of the 21 numerals are figures and 11 of those equal 0049's summarizer at
  the printed precision (0.1424 / 0.0802 / 0.1900 reuse; 0.2826-arm p10/p90 0.1795 / 0.3569; 85.49 / 80.39 / 89.02;
  92.16; attention 0.4100 / 0.0885 / 0.3012; peak 24.95). **Three differ in the 4th decimal**: the norm-matched random arm's
  median 11.2982 (operator 11.2981) and its p10 / p90 9.2594 / 13.5359 (operator 9.2592 / 13.5357) — the pilot's H100
  against the operator's A100 on the arm whose KL is ~11 nats; the reuse and cyclic arms agree to 4 decimals. The other
  numerals are version strings (2.14, 4.57, 5.17) and the registered limits (0.0001, 0.0005). Both runs are on the
  record with their cards; the MLSys draft should cite 0049's values.

## 3. The formal statements against `proofs/`

- `Numbers.lean` pins 41 four-digit constants: **all 41 are on the ledger**, 40 appear in the PDF (0.9105 = 1 − 0.0895 is
  the scaled-short R² restatement, not printed).
- Statement correspondence (read, not machine-checked): the paper's **Theorem 1** (μ = 1 − R̄², f*(τ) = 0 ⇔ R̄² ≥ 1 − τ, the
  τ_K = 1 − R²_map clause) ↔ `Identity.theorem1` / `theorem1_verdict`; **Theorem 2** (max{(μ−τ)⁺/(δ_max−τ) read as 0 when
  δ_max ≤ τ, sup_{d>τ}(φ(d)d−τ)⁺/(d−τ)} ≤ f*(τ) ≤ p(τ) ≤ min{1, μ/τ}, f* nonincreasing) ↔ `Fstar.theorem2_sandwich` with
  `lower_bound_max`, `lower_bound_beta_iSup`, `fstar_le_p`, `p_le_one`, `p_le_mu_div`, `fstar_antitone`; **Corollary 3**'s
  bound (μ ≤ δ_far + (m·w/n)(δ_near − δ_far), and f* = 0 when that is ≤ τ) ↔ `Seams.cor_seam`; **Proposition 4**'s logit
  shift |Δz_ij| ≤ ‖q_i‖ s_{l,h} √(δ_{l,h}(j)/d) ↔ `Attention.logit_shift_le`. No statement in the PDF lacks a formal
  counterpart; the PDF makes no Lean claim (correct: `lake build` has not run on this machine, CLAUDE.md rule).

## 5. Skeptic pass over the 0049 entry's operator-written paragraph (before the append)

A read-only skeptic subagent (rigor `skeptic-verifier`, 2026-10-07 ~12:40Z) was prompted to refute eight claims in the
paragraph "Inputs and the manifest clause of 0047" of the rendered 0049 entry. Verdicts: C1 (manifest `2aeee576…` on disk and
in `report.json`), C4 (`evidence_sha256_manifest` = `digest(SHA256SUMS file)`; no such file or pilot manifest tracked or in
history), C6 (`create_system` 0/3; the installed `.npz` entries are 210/210 at 3; a Windows re-save differs on 35/35 shas
with identical members and equal bytes after patching that byte), C7 (ruling text identical in entry, script and runbook),
C8 (issue #20 open and asking for both files) **CONFIRMED**. **C2 REFUTED as overstated**: the freeze record pins only
`config_sha256` and `input_manifest_sha256`; three of the "four freeze-record fields" are checked against the committed
bytes, not the record (the skeptic additionally verified all 35 record-level trace, alignment, score and token digests,
0 mismatches). **C3's attribution UNPROVEN**: non-identity with `9a6f2923…` is a fact, but "because the evidence field" asserts
it is the only differing field, which nothing shows without the pilot's manifest. **C5 UNVERIFIABLE as "192"**: the skeptic's
own 672-candidate brute force (orders × prefixes × separators × line endings) had 0 hits, supporting "not reproduced" but
not "no other machine can". Unlisted finding: 0047 says "or the run refuses", yet the frozen `run.py` compares no manifest
hash — the only refusal was the figures script's — and the ruling (2026-10-07) postdates the run (finished 01:22Z); the
paragraph did not say so. **All four recommended wording changes were applied** to `append_0049.py` before the append, the
0047 runbook's §3/§7 were corrected, and a correction was posted on issue #20 (which repeated the C2 overstatement).

## 4. What this record does not do

It does not judge the causal/interpretive rows (#18 rows 5–7 are moot; 36–38 and Q3/Q4 remain the operator's), it does
not check the PDF's prose against reviewer feedback, and it is not independent: the operator runs it cites were produced
and verified on this machine. The deadline question (PDF built 11 h after the recorded 11:59Z deadline) is unchanged.
