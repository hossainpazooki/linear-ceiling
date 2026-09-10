# Program status

The detailed state that used to live in the README: the current objective, every decided cell with
its entry, what the one positive verdict means, the descriptive entries, and the restore recipes.
`ledger/ledger.md` is the authority; this page is a reading of it, kept current by whoever appends.
Newest brief: `docs/handoff/HANDOFF.md`.

## Objective (2026-09-10)

**Ship the LCFM @ NeurIPS 2026 short paper by 2026-09-11 11:59 UTC with long context central.**
Working title: *Same weights, new positions: KV reuse at long-context agent handoffs, and the other
axis*. Outline: `docs/paper/2026-09-10-lcfm-outline-v2.md`.

The frame: a cache is a function of the context that produced it and the weights that computed it,
and two structural events change one factor each.

| axis | event | experiment | state |
|---|---|---|---|
| context | a re-rendered handoff: same tokens at new positions, new tokens at the seam | **E9** — 25 real SWE-bench handoffs up to 32K tokens | **HELD** on an oracle floor (0029); admitted to the paper (0032); freeze run passed 2026-09-09 |
| context, long | the same event at 35K–80K tokens under a YaRN-extended receiver | **E9-long** — the 35 handoffs above the prior cap | **HELD** (0036, 2026-09-10): median f*(τ_K) 0.0000 on all 35, bridge CARRIED; run on a rented L40S, 80 min; summarizer passed at home twice |
| weights | a policy update under an in-flight rollout in async RL | **E-RL** | **designed, unregistered** (`docs/2026-09-02-e-rl-design.md`); the paper's contrasting direction, no figure |

One yardstick for both axes: per matched token, the centered deviation between two KV states in the
units of a cross-model mapper's R²; a token needs recompute above τ_K = 0.3186, the k = 1 mapper's
own held-out shortfall; f*(τ_K) is the fraction an oracle would recompute; HOLDS ≤ 0.15, DEGRADES
≥ 0.50 (0023). E7 supplies the handoffs and is the paper's corpus paragraph; E8 explains the cross
arm in one sentence and an appendix table.

**Two conditions decide what the paper contains, and neither is a framing choice:**

1. E9 stays in only if the co-author refutation of entries 0025–0029 is recorded before submission
   (0032's condition, carried unchanged by 0035). Not recorded at the time of writing.
2. E9-long enters only from a passing `summarize_e9 --config config/e9l.toml`, by its own entry,
   with "n scored of 35 registered" beside every number, never pooled with E9's 25. **Satisfied
   2026-09-10** (0036; the summarizer passed at home 01:20Z and again on re-verification at 03:01Z).

## Decided cells

| hypothesis | verdict | entries |
|---|---|---|
| H-E7a — switch-point headroom is material on public agent traces | **NOT CONFIRMED** (0.20% of spend vs a 10% cutoff, registered reading) | 0015, 0018, 0022, 0024 |
| H-E7b — compaction break-even has substantial negative mass | **UNESTIMABLE** (no public format records it where it could occur) | 0015 |
| H-E8 — the fitted cross-model map survives agent-text content shift | **NOT CONFIRMED** (V DEGRADES, K dead band at k = 1; V calibration-sensitive under n = 420, 0034) | 0020, 0031, 0034 |
| H-E9 — KV agreement at a real re-rendered handoff keeps its usefulness | **HELD**, read on a floor: f* = 0 at every matched token of every included handoff; cross arm beyond DEGRADES (descriptive, 0.9286) | 0029 (0023, 0025, 0027) |
| H-E9L — the same claim on the long half under a scaled receiver | **HELD**, 35 scored of 35; read on a floor; bridge CARRIED; cross arm 0.9640 beyond DEGRADES (descriptive) | 0036 (0035) |
| H-S1…H-S4 (pre-fit screen line) | `SHELVED` / H-S2 first clause `NOT CONFIRMED` | 0003–0006 |

A verdict cell is decided once, under the rule registered before its run, and only a numbered entry
with a `verdict:` line can change it. Entries 0030–0034 re-ran the mechanism experiments under other
protocols (all agent sequences; an eight-times-larger calibration) and no cell moved; 0034's V
band-word movement is reported beside the decided cell, never in place of it.

## What HELD means here

- **The claim.** At a real re-rendered handoff (the receiver rebuilds the prompt from the sender's
  content), the receiver's own KV at the new positions agrees with its KV at the original positions
  closely enough to be reused. Same model on both sides; this is not a cross-model claim.
- **The statistic (0023).** Per matched token, the centered deviation between the two KV states in
  the units of the mapper's R². A token "needs recompute" when its deviation exceeds τ_K, which is
  set to the k = 1 cross-model mapper's own held-out shortfall on generic text: "no worse than the
  mapper itself" is the tolerance. f* is the fraction of matched tokens an oracle would have to
  recompute; the verdict is the median f* over included handoffs. HOLDS ≤ 0.15 (CacheBlend's
  achieved recompute budget), DEGRADES ≥ 0.50, UNRESOLVED between. Band frozen before any prefill.
- **The results (0029, 0036).** f* = 0 on every matched token of every included handoff, on the 25
  short handoffs under the native receiver and on the 35 long ones under a YaRN-scaled receiver
  whose bridge control read CARRIED. The τ ladder shows this is not vacuous, and on the long half
  it shows far less headroom: at τ = 0.03 the median is 0.5255 against 0.1433 on the short half;
  the far-from-seam deviation floor is 0.063 against 0.019; deviation at a re-rendered position
  rises three- to four-fold for tokens that sat beyond the native 32K window.
- **Read on a floor (0027).** f* assumes an oracle that knows which tokens deviate and recomputes
  them in isolation. It is a lower bound on what any real scheme would recompute, not a scheme. HELD
  says "no more than the mapper, on a floor"; it does not say a system achieves this.
- **Scope.** One pair (Qwen3-0.6B → 1.7B, receiver 1.7B), one direction, one agent family; 25 of 68
  handoffs at the native cap and 35 of 68 under the scaled receiver, never pooled; the four handoffs
  above 81,920 tokens and the four with an empty receiver prompt are unmeasured.
- **The cross arm beside it, descriptive.** The same tokens pushed through the fitted cross-model
  mapper sit beyond DEGRADES on both halves, and further out on the long one (0.9286 → 0.9640); they
  stay there under the larger-calibration mapper of 0034. For the gap map's routing question this is
  the finding: what a cache-aware router needs to know at a boundary is the binary "same model or
  not", not a transfer quantity.
- **What HELD does not move.** H-E7a's headroom verdict (switches are rare and the recoverable
  spend immaterial on the public record), H-E8 (the linear map fails on agent text), and the
  recording-gap reading. HELD says same-model reuse across a re-render is free at the floor; it does
  not say there is much of it to collect on public traces.

## How the cells hold each other up

- **E7 supplies the event.** The 68 handoffs E9 and E9-long score are the switch points E7 found on
  the public record (0015, 0018), and E7's finding that none of the 68 hands the receiver a
  byte-identical prefix is what makes "re-rendered" an observed event rather than a construction of
  the experiment. Without E7 the mechanism experiments would be scoring a handoff nobody has seen.
- **E8 explains the contrast.** The cross-model arm sits beyond DEGRADES, and that number is
  unexplained on its own. E8 is the explanation: the linear map was fit on generic text and does not
  hold on agent text (0020, 0031), so pushing agent KV through it at a handoff fails for the same
  reason it fails at rest. 0034 closes the obvious objection, since the failure survives an
  eight-times-larger calibration. Without E8, a reader could attribute the cross-arm number to the
  handoff; with it, the attribution is to the map.

## Descriptive entries after the decided cells

| entry | kind | what it did | effect on cells |
|---|---|---|---|
| 0030 | registration | E8 amended before any rescoring: arm (b) over every agent sequence instead of a held-out tail, per-sequence moments, a seeded bootstrap of the drop; upstream re-pinned | none |
| 0031 | figures | the amended E8 run through its summarizer; same band words as 0020 at k = 1 | none |
| 0032 | admission | E9 allowed into the LCFM 4-pager behind its summarizer gate, with the co-author refutation as a stated condition | none |
| 0033 | registration | calibration-size sensitivity: the k = 1 mapper refit on n = 420 sequences (eight times 0009's), E8 arms and the E9 kept-subset cross arm to be re-scored; registered before the fit existed | none |
| 0034 | figures | the n = 420 mapper's run through both summarizers. E8 at k = 1: K stays in the dead band, **V's drop falls to the DEGRADES edge and reads UNRESOLVED**. E9 cross arm: closer to the same-model floor, still beyond DEGRADES | none |
| 0035 | registration | E9-long registered before any prefill: cap 81,920 by YaRN, floor 32,768, the 35 newly included handoffs, the configuration bridge and length profiles, a registered run order and stopping rule; the paper re-scoped (supersedes 0032's space clause) | H-E9L row added `unresolved` |
| 0036 | figures + verdict | E9-long ran on a rented L40S; 35 of 35; bridge CARRIED; `verdict: H-E9L = HELD` | H-E9L `unresolved` → `HELD` |

## Beyond the paper

- **MLSys 2027** (due 2026-10-30): the anchor venue; the same record at full length, with E-RL
  measured if it fits.
- **E-RL**: KV reuse across RL post-training checkpoints, the weights axis; first build step is an
  upstream revision-aware `Pair`. Unregistered; takes a number when its script is staged.
- **A self-recorded corpus** carrying the fields public traces drop (per-step model, timestamps,
  request sizes, the cacheable prefix): the recording gap's fix; MLSys cycle, unregistered.
- **The n = 420 mapper on E9-long's kept subset**: its own config and entry, if run.
- **Upstream seam, on the record (0035):** the live-cache mapper path (`apply_mapper`) still strips
  with the plain θ; no perplexity/hellaswag eval under a scaled model until it takes the RoPE spec.

## Backups (Hugging Face): restore and verify

`results/`, `data/` and `traces/` never enter git history; the only off-machine copy of a GPU run's
tensors is a private Hugging Face dataset pushed from the verified home mirror after every sitting
(protocol R8 in `docs/gpu-experiment-protocol.md`). Three rules bound it: transport, not evidence (a
summarizer reads the local mirror only, and a refusal at home is a finding); every file verified in
both directions (`tools/hf_verify_backup.py <repo_id> <local_root>` exits 0 only when every
`lfs.sha256` matches and every non-LFS file re-downloads to its hash); tokens scoped, expiring,
environment-only, revoked once pasted anywhere.

| dataset | holds | layout at the dataset root |
|---|---|---|
| `hossainpazooki/linear-ceiling-e9-2026-09-04` | the E9 record (entries 0026–0029): `report.json`, `align/`, `controls/`, `scores/`, `tokens/`, box logs, and the kept full dumps | `results/e9/` as in this repo, plus the fitted mapper `mappers/qwen3-0.6b-to-1.7b/k1.*` in the upstream's layout |
| `hossainpazooki/linear-ceiling-n420-2026-09-08` | the n = 420 calibration pair behind entries 0033/0034, the tagged mapper and its `r2.json`, the sitting's box logs and sha manifests | the upstream's own layout: `data/kv/qwen3-0.6b-to-1.7b-n420/`, `mappers/qwen3-0.6b-to-1.7b/n420/`, `results/mapper/qwen3-0.6b-to-1.7b/n420/` |
| `hossainpazooki/linear-ceiling-e9l-2026-09-10` | the E9-long record (entries 0035/0036): `report.json`, `align/`, `bridge/`, `controls/`, `scores/`, `tokens/`, box logs, the three kept handoffs and the three bridge pairs | `results/e9l/` as in this repo, plus the mapper in the upstream's layout |

Restore, with a read token in `HF_TOKEN`:

```bash
# E9 / E9-long: results/ lands in this repo, the mapper in the upstream checkout
hf download hossainpazooki/linear-ceiling-e9-2026-09-04 --repo-type dataset --local-dir /tmp/e9-restore
cp -r /tmp/e9-restore/results/e9 results/ && cp -r /tmp/e9-restore/mappers ../kv-transfer-replication/
python tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9-2026-09-04 /tmp/e9-restore
hf download hossainpazooki/linear-ceiling-e9l-2026-09-10 --repo-type dataset --local-dir /tmp/e9l-restore
cp -r /tmp/e9l-restore/results/e9l results/
python tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9l-2026-09-10 /tmp/e9l-restore --exclude README.md

# n = 420 pair: upstream layout, so it lands directly in the upstream checkout
hf download hossainpazooki/linear-ceiling-n420-2026-09-08 --repo-type dataset --local-dir ../kv-transfer-replication
python tools/hf_verify_backup.py hossainpazooki/linear-ceiling-n420-2026-09-08 ../kv-transfer-replication
```

After a restore the gates decide, not the download: `e9 --check`, `e9 --check --config config/e9l.toml`,
`e8 --check --config config/e8c.toml` and `e9_rescore check --config config/e9c.toml` must print ready
before any summarizer runs. Large pushes use `hf upload-large-folder --num-workers 1` on Windows
(multi-worker uploads stall); the dataset card goes last.

## Docs map

| path | role |
|---|---|
| `ledger/ledger.md` | the registered record: hypotheses, verdicts, numbered immutable entries — **start here** |
| `docs/paper/2026-09-10-lcfm-outline-v2.md` | the 4-pager outline the team writes from; every figure with its entry and freeze status (`2026-09-06-lcfm-outline.md` is the superseded frame) |
| `docs/handoff/HANDOFF.md` · `docs/learnings/LEARNINGS.md` | handoff index (newest brief = pick-up target); non-obvious findings with `re-verify:` lines |
| `config/e9l.toml` · `docs/2026-09-08-seed-e9-long-half.md` | E9-long's registered parameters; the seed that designed it |
| `docs/2026-09-02-e-rl-design.md` | E-RL design, unregistered |
| `docs/2026-09-06-gap-map-revisited.md` · `docs/gap-map.md` | the original motivation read against the ledger, claim by claim |
| `docs/gpu-experiment-protocol.md` · `docs/2026-09-02-e9-gpu-runbook.md` · `docs/2026-09-08-n420-target-dump-runbook.md` · `docs/2026-09-10-e9l-gpu-runbook.md` | standing rules R1–R12; the two prior GPU sittings; the E9-long sitting on a rented L40S |
| `tools/jupyterhub/` · `tools/ec2/` · `tools/hf_verify_backup.py` | the JupyterHub box driver and pull loop; the ssh/EC2 form of the same; the backup verifier |
| `docs/2026-09-01-measurement-lane-evidence.md` · `docs/2026-09-01-swe-bench-trace-recon.md` · `docs/background.md` | why the program re-scoped; trace formats and what they omit; history and vocabulary |
| `docs/drafts/` | append scripts for entries not yet written; its README is the only number allocator |
| `docs/archive/` | superseded READMEs, verbatim: the visual-heavy one (`7ce63cf`) and the status form (`b4b56aa`) |
| `UPSTREAM.md` | the pinned upstream and the provenance ledger for everything borrowed |
