# T03 — §4.x A second source→receiver pair: Llama-3.2-3B → Llama-3.1-8B (table + P1–P4 + App. A scoping sentences)

status: DRAFT (drafted 2026-10-08 in the draft plan §2, skeptic-passed the same day; moved here 2026-10-10; awaiting
  per-paragraph approval — open: P2's tail sentence in the main text or App. C)
sources: ledger lines at `0741fdd` (0051 appended) — 0039:2379, 2404, 2473; 0040:2539; 0042:2666–2667; 0044:2874,
  2942–2943, 2947, 2950, 2957–2958, 2971, 2977, 2986; 0045:3088–3092; 0050 (registration); 0051:3832, 3844, 3870, 3874,
  3878, 3884–3885, 3891, 3896–3905, 3908; 0053:3540, 3559; 0034:2039, 2059. Files — `results/e9f/summary.json`
  (sha256 `e1e5feb8aadd…`): `rule.tau_K`, `rule.tau_V`, `fstar.same_K.{n,median,p10,p90}`, `fstar.cross_K.{median,p10,p90}`,
  `fstar.cross_V.median`, `calibration.heldout.{K,V}_r2_layer_mean`; `results/e9fl/summary.json` (`1ac712b3897e…`):
  `fstar.same_K.{n,median,p10,p90}`, `fstar.cross_K.{median,p10,p90}`, `length_profiles.s_len[i].{bin,n_handoffs,
  fstar_K.median}`; `results/e9f/tail.json` (`c35c48b9dbbe…`): `pooled.same_K.n_tokens`,
  `pooled.same_K.fraction_over_tau.<τ_K>`, max over `per_handoff.<id>.same_K.mean`; `results/e8fa/summary.json`
  (`9ddb66cc2796…`): `recomputed.1.generic.{K,V}`, `per_k.1.prior_0016_protocol.agent.{K,V}`,
  `per_k.1.prior_0016_protocol.drop.{K,V}`, `recomputed.1.agent.{K,V}`, `recomputed.1.drop.{K,V}`,
  `per_k.1.bootstrap.{K,V}.drop_{lower_2.5,upper_97.5}` (0040's registered arm is the `prior_0016_protocol` block;
  `results/e8f/` holds `report.json` only)
conventions: four decimals; every (p10, p90) over handoffs is `e7_stats.quantile` lower nearest-rank; the per-token tail
  fraction is a pooled count, not a quantile (T01 does not apply); E8 intervals are a seeded percentile bootstrap of the
  drop over agent sequences; τ_K = 1 − R²_K of the pair's own k = 1 map
re-verify: .venv/Scripts/python.exe -c "import json;f=json.load(open('results/e9f/summary.json'));l=json.load(open('results/e9fl/summary.json'));t=json.load(open('results/e9f/tail.json'));e=json.load(open('results/e8fa/summary.json'));r4=lambda x:round(x,4);print(r4(f['rule']['tau_K']),r4(f['rule']['tau_V']),f['fstar']['same_K']['n'],[r4(f['fstar']['same_K'][k]) for k in('median','p10','p90')],[r4(f['fstar']['cross_K'][k]) for k in('median','p10','p90')],r4(f['fstar']['cross_V']['median']),l['fstar']['same_K']['n'],[r4(l['fstar']['same_K'][k]) for k in('median','p10','p90')],[r4(l['fstar']['cross_K'][k]) for k in('median','p10','p90')],[(b['n_handoffs'],b['fstar_K']['median']) for b in l['length_profiles']['s_len']],t['pooled']['same_K']['n_tokens'],r4(t['pooled']['same_K']['fraction_over_tau'][str(f['rule']['tau_K'])]),r4(max(v['same_K']['mean'] for v in t['per_handoff'].values())),[r4(e['recomputed']['1']['generic'][k]) for k in'KV'],[r4(e['per_k']['1']['prior_0016_protocol']['agent'][k]) for k in'KV'],[r4(e['per_k']['1']['prior_0016_protocol']['drop'][k]) for k in'KV'],[r4(e['recomputed']['1']['agent'][k]) for k in'KV'],[r4(e['recomputed']['1']['drop'][k]) for k in'KV'],[(r4(e['per_k']['1']['bootstrap'][k]['drop_lower_2.5']),r4(e['per_k']['1']['bootstrap'][k]['drop_upper_97.5'])) for k in'KV'])"   # 0.2861 0.5289 28 [0.0, 0.0, 0.0] [0.7317, 0.6074, 0.8516] 0.8148 32 [0.0, 0.0, 0.0] [0.7626, 0.5963, 0.9212] [(21, 0.0), (10, 0.0), (1, 0.0)] 169437 0.1127 0.286 [0.7139, 0.4711] [0.7311, 0.4599] [-0.0172, 0.0111] [0.6979, 0.4137] [0.016, 0.0573] [(0.0052, 0.0267), (0.041, 0.074)]

Working title: **4.x A second source→receiver pair: Llama-3.2-3B → Llama-3.1-8B.** Placement: after the same-model
extension (Table 7's receivers), before App. references; the table replaces nothing. T02 (E-TRUNC) follows it.

### P1 — why a second pair, and what is held fixed

> The Qwen3 results concern one source→receiver pair, one direction and one mapper. To test whether the zero median is a
> property of that pair, we registered a second pair in a different model family before any fit: Llama-3.2-3B as the
> source and Llama-3.1-8B as the receiver, a matched-KV pair (8 key–value heads × 128 head dimension on both sides), so
> the same k = 1 mapper and the same per-token rule apply unchanged. Every tolerance for this pair is its own: τ_K is
> 1 − R²_K of the pair's k = 1 map on held-out generic text, 0.2861 (Qwen3: 0.3186), and τ_V = 0.5289. Nothing from the
> two pairs is pooled: the same token cap selects a different set of handoffs under each tokenizer, so the pairs are
> compared in prose, never averaged.

Changes, and why: the pair, matched-KV premise and "registered before any fit" — 0039:2379 (heading) and the
registration paragraph (matched-KV 8 × 128: 0039:2404, 2473); τ_K = 1 − 0.7139 = 0.2861 and τ_V = 0.5289 —
0042:2666–2667, restated 0044:2942 (τ_K) / 2950 (τ_V) and 0051:3870 / 3878; "never pooled … different tokenizer selects a
different set" — 0044:2957–2958. Qwen3's τ_K = 0.3186 is the paper's own (§3 and Table 6 — NOT Table 1, which carries
no τ; skeptic 2026-10-08). No figure is new to the paper's reader except 0.2861 / 0.5289.

### P2 — the short cell (the registered verdict cell)

> On the 28 handoffs whose sender and receiver prompts both fit 32,768 Llama-3 tokens, the pre-registered hypothesis
> H-E9F — the same-model claim of H-E9 on this pair — **held**: the median oracle removal fraction f*(τ_K) over
> handoffs is 0.0000 (p10 0.0000, p90 0.0000; 28 scored of 28 registered), against the pre-registered edges HOLDS ≤ 0.15
> and DEGRADES ≥ 0.5. The cross-model arm through the pair's own k = 1 map sits beyond the DEGRADES edge: median
> f*(τ_K) = 0.7317 (p10 0.6074, p90 0.8516), f*(τ_V) = 0.8148. As with Qwen3, individual tokens exceed τ_K (11.3 % of the
> 169,437 matched tokens) while every handoff's mean sits under it; the largest per-handoff mean is 0.2860 against
> τ_K = 0.2861.

Changes, and why: "28 scored of 28", median 0.0000 (0, 0) — 0044:2947; "both fit 32,768" — 0044:2874, 2977; the edges
HOLDS ≤ 0.15 / DEGRADES ≥ 0.5 — 0044:2942–2943; H-E9F HELD — the `verdict:` line 0044:2986; cross arm 0.7317 / 0.8148 —
0044:2971; the per-token tail 11.27 % → "11.3 %" and the maximum mean 0.2860 — 0045:3088–3092 (`results/e9f/tail.json`
recomputed 2026-10-08 by the skeptic: 169,437 tokens, 0.1127 over τ_K, max handoff mean 0.286048 vs τ_K 0.286133, 28/28
under). **Operator decision:** whether to print the tail sentence (it is the honest reading under 0058) or leave it to
App. C.

### P3 — the long cell at a native receiver

> The 32 handoffs whose longer side runs 32,769–81,920 tokens were replayed on the same pair with nothing scaled: the
> receiver's own context window covers the cap, so this cell has no YaRN configuration and no configuration bridge;
> instead, the recorded rotary parameters of every dump are checked against the loaded model and against each other
> within each model role. This cell was registered as descriptive — it carries no hypothesis and is not pooled with the
> Qwen3 long cohort, whose receiver was pushed past its pretraining window. Its median f*(τ_K) over 32 handoffs is
> 0.0000 (p10 0.0000, p90 0.0000); by sender length, the median is 0.0000 in each of the three |S| bins (21, 10 and 1
> handoffs); the cross arm's median is 0.7626 (p10 0.5963, p90 0.9212). Beside the Qwen3 long cohort's 0.0000 this is a
> second zero on a different receiver — one scaled past its pretraining window, one not — stated side by side and not
> compared as a number: different models, tokenizers, handoff sets and tolerances.

Changes, and why: 32 handoffs, floor/cap "32,769–81,920" — 0051:3844, 3908; native receiver, no rope/bridge, the two
RoPE controls, "cannot move H-E9L, never pooled" — 0050 (registration) and 0051:3832 (heading); median 0.0000 over 32 —
0051:3874; length profile (i) with n = 21 / 10 / 1 — 0051:3884–3885; cross arm 0.7626 — 0051:3891; the closing sentence
now follows 0051:3896–3905 ("stated side by side and are not comparable as numbers … not averaged, pooled or differenced")
instead of asserting an equivalence the entry withholds (skeptic 2026-10-08).

### P4 — content shift for the pair's map (goes to App. B beside Table 4)

> For this pair the k = 1 map's held-out R² on generic text is 0.7139 (K) / 0.4711 (V); on the registered 10 agent
> sequences it is 0.7311 / 0.4599 (drop −0.0172 / +0.0111, both HOLDS), and on all 50 agent sequences 0.6979 / 0.4137
> (drop +0.0160 / +0.0573, HOLDS / UNRESOLVED, bootstrap 95 % [+0.0052, +0.0267] / [+0.0410, +0.0740]). The apparent
> inversion in the 10-sequence arm (agent K R² above generic K R²; V never inverted) does not persist on all sequences.
> These figures are descriptive for this pair; H-E8's cell is Qwen3's.

Changes, and why: the k = 1 rows — 0040:2539 (registered arm) and 0053:3540 (all-sequence amendment; the intervals are
bootstrap 95 % of the drop); "the inversion does not persist" is a K-only statement — 0053:3559 (skeptic: V's agent R²
0.4599 was never above its generic 0.4711, so the draft now scopes it); "H-E8's cell is Qwen3's / never pooled" — 0039's
registration clause.

### Table (one, in §4.x)

| cohort (Llama-3.2-3B → Llama-3.1-8B) | n | τ_K | same-model f*(τ_K) median (p10, p90) | cross f*(τ_K) median (p10, p90) | source |
|---|---|---|---|---|---|
| short (sender and receiver ≤ 32,768) | 28 | 0.2861 | 0.0000 (0.0000, 0.0000) | 0.7317 (0.6074, 0.8516) | 0044:2942, 2947, 2971; `e9f/summary.json` `rule.tau_K`, `fstar.same_K`, `fstar.cross_K` |
| long (longer side 32,769–81,920, native receiver) | 32 | 0.2861 | 0.0000 (0.0000, 0.0000) | 0.7626 (0.5963, 0.9212) | 0051:3870, 3874, 3891; `e9fl/summary.json` `rule.tau_K`, `fstar.same_K`, `fstar.cross_K` |

**Llama-only, by design (skeptic 2026-10-08).** The first draft restated Qwen rows beside these; that failed twice — the
paper's Table 1 is the long cohort only, its Table 2 short row is the 0038 YaRN-scaled run, not 0029's native cell, and
the paper prints no short-cohort cross figure — and a shared table is not "compared in prose or not at all" (0044:2958).
The Qwen figures stay in the paper's own tables; the caption says this pair is at its own tolerance on its own handoff
sets and is not compared with them as numbers.

### The scoping sentences, rewritten (App. A)

> The representation results replicate across four receiver models from three families and two source→receiver pairs,
> each pair at its own calibrated tolerance; prediction measurements use only Qwen3-1.7B; cross-model transfer uses
> one calibration size per pair on the long cohorts, and the larger calibration (420 sequences) was scored at a handoff
> on 8 short Qwen3 handoffs only.

Changes, and why: counts — the paper's three receivers + Llama-3.1-8B (0044); "two pairs" — 0044:2971, 0051:3891;
"420 … 8 short handoffs only" — 0034:2039, 2059 (the n = 420 map was re-scored on the 8 kept handoffs of the 25, plus the
E8 arms; "short cohort" overstated it — skeptic 2026-10-08); the paper's own App. B says it "was not run on the long cohort".

### Skeptic pass (2026-10-08, read-only `skeptic-verifier`, HEAD `0741fdd`)

Every Llama figure CONFIRMED on its line; `tail.json` and the four empty-receiver sender lengths recomputed from raw
files and CONFIRMED; nothing averaged or differenced. REFUTED and corrected above: two Qwen attributions to "the paper's
tables" (Table 1 has no τ and is long-only; Table 2's short row is the scaled run; no short cross figure printed), the
unscoped inversion (K only), "short cohort" for the n = 420 map (8 handoffs), five cites on neighbouring lines (0044 τ
2942/2950, edges 2942–2943, verdict 2986; 0051 τ_V 3878), the shared Qwen/Llama table (dropped), and P3's closing
equivalence (replaced by 0051's own wording).

Approval record: (none yet; reply with the paragraph letters approved, or the change wanted; once every paragraph is
approved the status line becomes `APPROVED <date>` in the approving commit and the file is immutable from then on).
