"""Append entry 0035 -- E9-long registered BEFORE any prefill, and the 4-pager re-scoped (supersedes 0032's space clause).

Ordering guard: 0034 present, 0035 absent. Nothing under this entry may exist yet: `results/e9l/` holds no report and no
score file (the R1 proof line). What MUST exist: `results/e9l/align/coverage.json` from `e9 --align-only --config
config/e9l.toml` (the instrument's own coverage, cited by sha), `config/e9l.toml` with a real upstream pin whose
`kvt/rope.py` carries the RoPE spec, and 0029's summary (the bridge handoffs are drawn from its kept subset). Every
number below is read from the config or that coverage file; nothing is typed. `--preview` prints the entry without
appending. Runs `ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import UPSTREAM_PATHS, _PENDING, required_markers
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash

PREVIEW = "--preview" in sys.argv
LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0034 " in text and "### 0035 " not in text, "ordering: 0034 present, 0035 absent"
assert "| H-E9L |" not in text, "H-E9L row already in the table"
cfg = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
assert cfg.rule == e9.rule and cfg.controls == e9.controls and cfg.mapper_k == e9.mapper_k, "rule/tau/band/controls must be byte-for-byte E9's"
assert cfg.required_entries[-1] == "0035" and required_markers(cfg)[-1] == "### 0035 "
assert not (cfg.results_dir / "report.json").exists(), "results/e9l/report.json exists: a run happened before registration; refusing"
assert not (cfg.results_dir / "scores").exists() and not (cfg.results_dir / "bridge").exists() and not (cfg.results_dir / "controls").exists(), \
    "results/e9l/ holds score, bridge or control files: refusing"
cov_path = cfg.results_dir / "align" / "coverage.json"
assert cov_path.exists(), "run `e9 --align-only --config config/e9l.toml` first: the coverage this entry states comes from the instrument"
cov = json.loads(cov_path.read_text(encoding="utf-8"))
assert cov["config_sha256"] == sha256_text_file(cfg.config_path), "coverage.json was written under another config/e9l.toml"
assert cov["context_cap"] == cfg.context_cap and cov["context_floor"] == cfg.context_floor and cov["rope"] == cfg.rope
if not PREVIEW:
    assert _PENDING not in cfg.upstream_sha, "config/e9l.toml still carries UPSTREAM_SHA_PENDING; commit the upstream RoPE-spec change and record its sha"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the pin {cfg.upstream_sha[:12]}"
    rope_src = subprocess.run(["git", "show", f"{cfg.upstream_sha}:kvt/rope.py"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout
    assert "class RopeSpec" in rope_src and "check_rope_spec_against_model" in rope_src, "the pinned upstream has no RoPE spec"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *UPSTREAM_PATHS], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert not dirty, f"upstream invoked paths are dirty at the pin:\n{dirty}"
prior = json.loads((e9.results_dir / "summary.json").read_text(encoding="utf-8"))
recs = {a["handoff_id"]: a for a in cov["alignments"]}
kept_prior = sorted(prior["keep_subset"], key=lambda h: (recs[h]["n_sender"], h))
assert list(cfg.bridge["handoffs"]) == kept_prior[:3], "bridge handoffs must be the three shortest of 0029's kept subset"
for h in cfg.bridge["handoffs"]:
    assert recs[h]["excluded"] and "context floor" in recs[h]["reason"], f"bridge handoff {h} must sit below the floor"
included = [h for h, r in recs.items() if not r["excluded"]]
order = cov["run_order"]
assert sorted(included) == sorted(order) and len(order) == cov["coverage"]["included"]
ns = [recs[h]["n_sender"] for h in order]
assert ns == sorted(ns) and len(set(ns)) == len(ns), "run order must be |S| ascending with no ties"
by_reason = {}
for h, r in recs.items():
    if r["excluded"]:
        by_reason.setdefault(r["reason"], []).append(h)
empty = sorted(by_reason.get("receiver prompt is empty in the trace", []))
over = sorted(h for reason, hs in by_reason.items() if "exceeds context cap" in reason for h in hs)
prior_cap = sorted(by_reason.get(f"S and R within context floor {cfg.context_floor} (decided under the prior cap)", []))
assert len(prior_cap) == prior["coverage"]["included"] == 25, "the floor must exclude exactly 0029's included set"
sum_s, sum_r = sum(recs[h]["n_sender"] for h in order), sum(recs[h]["n_receiver"] for h in order)
keep = cov["keep_subset"]
assert len(keep) == cfg.keep_n and set(keep) <= set(order)
tau_K, tau_V, tau_agent = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"]), float(cfg.rule["tau_agent_K"])
ladder = ", ".join(f"{float(t):.4g}" for t in cfg.rule["tau_ladder"])
rope = cfg.rope
window = int(round(rope["original_max_position_embeddings"] * rope["factor"]))
names = lambda hs: "; ".join(f"`{h}`" for h in hs)      # noqa: E731
lens = lambda hs: ", ".join(f"{recs[h]['n_sender']:,}" for h in hs)      # noqa: E731
sl, sp = cfg.profiles["s_len_edges"], cfg.profiles["s_pos_edges"]
sl_bins = " / ".join(f"({sl[i]:,}, {sl[i + 1] - 1:,}]" if i == 0 else f"[{sl[i]:,}, {sl[i + 1] - 1:,}]" for i in range(len(sl) - 1)) + f" / [{sl[-1]:,}, {cfg.context_cap:,}]"
sp_bins = " / ".join(f"[{sp[i]:,}, {sp[i + 1] - 1:,}]" for i in range(len(sp) - 1)) + f" / [{sp[-1]:,}, {cfg.context_cap:,}]"
pin = "UPSTREAM_SHA_PENDING (preview)" if PREVIEW and _PENDING in cfg.upstream_sha else cfg.upstream_sha[:12]

ROW = (f"| H-E9L | (E9's claim on the long half) at a re-rendered handoff whose sender prompt exceeds the prior cap of "
       f"{cfg.context_floor:,} tokens, same-model KV agreement on content-matched tokens keeps its usefulness under a receiver "
       f"extended to {cfg.context_cap:,} positions by static YaRN. Rule verbatim from entry 0023: median over the newly included "
       f"handoffs of the oracle selective-recompute fraction f*(τ_K = {tau_K:.4f}) on the K read-out, HOLDS ≤ {cfg.rule['holds_max']} / "
       f"DEGRADES ≥ {cfg.rule['degrades_min']:.2f} / UNRESOLVED between; decided on the {len(order)} newly included handoffs only, never pooled "
       f"with 0029's {len(prior_cap)}; read on a floor (0027) and, if the bridge control exceeds {cfg.bridge['reading_max_fstar']}, as a claim "
       f"about the scaled receiver only. Registered by entry 0035 before any prefill. | E9-long (entry 0035) | unresolved |")

ENTRY = f"""### 0035 — 2026-09-09 — E9-long registered before any prefill: H-E9's instrument on the {len(order)} handoffs above the prior cap, receiver scaled to {cfg.context_cap:,} by YaRN; H-E9L added `unresolved`; the 4-pager re-scoped around E9 and E9-long (supersedes 0032's space clause)

**Why, and why now.** H-E9 `HELD` (0029) is a claim about the 25 of 68 observed handoffs whose sender prompt fits
Qwen3's 32,768-token cap — the shorter half by |S| (0025: included median 25,460 vs excluded 52,141). A long-context
venue asks first whether the same result holds where the re-rendered context is 35K–80K tokens, and nothing on the
record answers it. The seed (`docs/2026-09-08-seed-e9-long-half.md`) designed the experiment; the operator ruled
D1(a)/D2/D3/D4/D5 on 2026-09-09 and, the same day, that the LCFM 4-pager is written from an overnight sitting on a
rented single L40S (48 GB; no queue) rather than the Algoverse 3g.40gb queue. This entry registers the experiment,
its controls, its stopping rule and its paper scope BEFORE the box is touched: `results/e9l/` holds no report, no
score, no bridge and no control file at append, and this script refuses otherwise (R1). The only thing under
`results/e9l/` is the instrument's own alignment pass (`e9 --align-only --config config/e9l.toml`,
`align/coverage.json` sha256 `{sha256_file_bytes(cov_path)[:12]}`), from which every count below is read.

**Hypothesis H-E9L (row added to the table, `unresolved`).** The statement is E9's on the long half; the rule is
0023's verbatim (`[e9.rule]` copied byte-for-byte from `config/e9.toml`): per matched token the centered deviation in
R²'s units between the receiver's own K at the sender position and at the re-rendered position; a token needs
recompute when it exceeds τ_K = {tau_K:.4f} (the k = 1 mapper's held-out shortfall, 0023); the verdict statistic is the
median over included handoffs of the oracle selective-recompute fraction f*(τ_K) on the K read-out; **HOLDS ≤
{cfg.rule['holds_max']} / DEGRADES ≥ {cfg.rule['degrades_min']:.2f} / UNRESOLVED between**. τ_V = {tau_V:.4f}, τ_agent_K = {tau_agent:.4f}, the τ ladder ({ladder}),
the seam bins, the block floor ({cfg.rule['min_block_len']}) and the bootstrap (seed {cfg.controls['bootstrap_seed']}, {cfg.controls['bootstrap_reps']} reps) are 0025's, unchanged.
f* stays an oracle LOWER BOUND read on a floor (0027).

**The verdict set: the newly included handoffs, never pooled.** `context_cap = {cfg.context_cap:,}` (= {rope['original_max_position_embeddings']:,} × {rope['factor']}, the knee of the
cap ladder in the seed) and `context_floor = {cfg.context_floor:,}`: a handoff whose |S| and |R| both fit the floor was decided by
0029 and is EXCLUDED here with its own reason (the {len(prior_cap)} of 0029, never pooled; that cell is immutable). Coverage from
the alignment pass: **{cov['coverage']['observed']} observed · {len(order)} included · {len(prior_cap)} excluded as decided under the prior cap · {len(over)} excluded
above the cap · {len(empty)} excluded for an empty receiver prompt** (the last eight by name, in the seed's words: above
{cfg.context_cap:,}: {names(over)} (|S| {lens(over)}); empty R: {names(empty)}). Included |S| runs {ns[0]:,} to {ns[-1]:,}; the
prefill budget is {sum_s:,} sender tokens (1.7B and 0.6B) + {sum_r:,} receiver tokens = {2 * sum_s + sum_r:,} tokens. H-E9L is a claim
about these {len(order)}; coverage travels with every figure (0032's clause, kept).

**The receiver configuration (D1(a)) and the upstream change.** Both models are loaded with static YaRN in the HF
form `{json.dumps(rope, sort_keys=True)}` (window {window:,}); Qwen's own
recommendation is factor 4.0 for 131,072 and a smaller factor is the same mechanism. Under YaRN the model's rotary
embedding changes the per-dimension inverse frequencies AND multiplies cos/sin by an attention factor
(transformers 5.15.1 `Qwen3RotaryEmbedding.forward`; 0.1·ln {rope['factor']} + 1 ≈ 1.0916), so the K a model writes is
m·R_yarn(pos)·k_content and the upstream's plain-θ strip would leave a wrong rotation and a factor m in every
content-space K. The upstream commit pinned below (`{pin}`, successor of `4633718`) adds a RoPE spec
(`kvt/rope.py::RopeSpec`) read from the model's OWN rotary embedding (`inv_freq` + `attention_scaling`, never a
formula), written into every dump's `meta.json`, HALT-checked against the model at every position of the dump
before any forward pass (atol 1e-5), and used by `KVDump` to strip (R^T/m); `load_model(model_id, rope_scaling=…)`
and `dump_kv.py --rope-scaling`; archived dumps without the block strip exactly as before (tested: the tiny-model
content key equals `k_norm(k_proj(x))` under YaRN to fp16 tolerance; the plain-θ strip is shown wrong; the halt
fires on a dropped factor or plain frequencies; 153 upstream tests; independent refutation 2026-09-09: spec cos/sin bitwise equal to HF's over all 81,920 positions of the real Qwen3-0.6B config, divide-once residual 9.5e-7 vs ~0.5 for zero or two divisions, YaRN static under transformers' dynamic-update decorator, the archived n = 50 dump strips bit-identically). **Seam outside this entry's route, on the record:** the upstream's live-cache mapper path (`kvt/mapper.py::apply_mapper`, used by the perplexity/hellaswag evals and `compose_mapper.py`) still strips and re-applies with the plain θ; E9's scorer never calls it (content space via `KVDump`), and no eval under a scaled model may run until it takes the spec. **Stated risk:** static YaRN changes the KV of
short contexts too, so this receiver is a different function from 0029's; control 4 measures how different and
fixes how the verdict reads. The mapper is 0029's n = 50 k = 1 artifact by sha (D4 realized as: the driver scores
the n = 50 mapper on every handoff, exactly 0029's shape; the n = 420 mapper of 0033/0034 is applied afterwards at
home to the kept subset through `e9_rescore` under its own config, descriptive, by its own entry if run).

**Run order, stopping rule, resume (unattended overnight sitting).** The driver scores the included handoffs in the
REGISTERED order `n_sender_asc` (|S| ascending, ties by id; there are none): {order[0].split('/')[1]} ({ns[0]:,}) first,
{order[-1].split('/')[1]} ({ns[-1]:,}) last. The controls run on the first handoff in that order. If the sitting must
end before all {len(order)} are scored, `e9 --close-partial --config config/e9l.toml` closes the run: it is allowed only by
this config, it refuses unless the scored set is a PREFIX of the registered order, it stamps the close time and
names every unscored handoff in `report.json`, and the verdict entry states the cell on the scored prefix with
"n scored of {len(order)} registered" beside every number. The cutoff is the operator's and is recorded, with the reason, in
the verdict entry; it may not depend on any score. A relaunch after a crash uses `--resume`, which keeps only the
bridge, the controls and the scored handoffs whose score and per-token files still match their recorded hashes
under the same config sha and pin; a plain relaunch over an unfinished report is refused.

**Keep subset (D3).** n = {cfg.keep_n}, seed {cfg.keep_seed}, a fresh draw from the sorted newly-included ids (numpy `choice` without
replacement is not nested with 0025's draw of 8): {names(keep)}. Their three stride-1 dumps are retained,
fingerprinted, pulled home and re-scored from tensors by the summarizer under 0028's tolerance.

**Controls, registered (1–3 as 0023/0025; 4–5 new; 6 unchanged).** (1) Pipeline identity HALT (a dump scored against
itself, every square exactly zero). (2) Prefix-invariance HALT on the first handoff in run order: S vs S + R's first
token, max centered δ ≤ {cfg.controls['prefix_invariance_max_delta']:.0e}. (3) δ_null: seeded derangement of sender positions (seed {cfg.controls['null_seed']}), the
uninformative scale. **(4) Configuration bridge:** for the three SHORTEST of 0029's kept handoffs ({names(cfg.bridge['handoffs'])};
|S| {lens(cfg.bridge['handoffs'])}) the receiver prefills S twice ON THE SAME BOX, once under the native RoPE and once under
the scaling above, and the two dumps are scored at pairs (p, p) over every sender position; both dumps are kept and
fingerprinted, the summarizer re-scores them from tensors and states the median native-vs-scaled f*(τ_K).
**Reading fixed now:** if that median exceeds {cfg.bridge['reading_max_fstar']}, the receiver configuration alone exceeds the mapper's
tolerance and H-E9L is read as a claim about the SCALED receiver only, in the verdict entry's first paragraph. The
bridge runs BEFORE the first long handoff and is checkpointed, so a late failure cannot lose it; it cannot gate the
launch, it gates the reading. **(5) Length profiles (descriptive):** f*(τ_K) and median δ_K (i) by |S| bin
{sl_bins}, and (ii) by matched-token position in S {sp_bins} — (ii) is
the long-context figure: does agreement at a re-rendered position depend on how deep in the sender's context the
token sat. (6) Seam profiles b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9l.toml` refuses until entries {'/'.join(cfg.required_entries)} are in the
committed ledger, `config/e9l.toml` is committed unmodified, the upstream is at the pin with every invoked path
clean, and the mapper artifact is present by sha; `summarize_e9 --config config/e9l.toml` (fail-closed, the only
reader) re-derives every alignment from the raw traces with the floor, recomputes every figure, re-scores the kept
and bridge dumps from tensors, checks the controls, states the bridge reading, the profiles and the band, and
refuses on any disagreement. Tests: the floor, the scaling on every dump, the bridge first and recorded, the run
order, resume, the partial close and its prefix rule, and that `config/e9.toml`'s behaviour is untouched.

**Paper scope (operator ruling 2026-09-09; supersedes 0032's space clause).** The LCFM 4-pager is re-cut with long
context central: E9 (0029) and E9-long are the results; E-RL (`docs/2026-09-02-e-rl-design.md`, designed and
unregistered — stated as such, in those words) is the contrasting registered direction on the weights axis; E7 is
the corpus paragraph; E8 is one sentence with its table in an appendix. 0032's clause "E9 is one paragraph, one table
… Lane A/B premise numbers and the taxonomy remain the submission's core" is superseded by this paragraph. **Kept
from 0032, unchanged:** E9 and E9-long figures enter the 4-pager only from a passing `summarize_e9` run (E9's at the
detached `d5786df` checkout, 2026-09-09; E9-long's under `config/e9l.toml`); the same-model result never appears
without the cross-model outcome in the same table or sentence; coverage travels with every number, and E9-long's
reads "n of {len(order)} newly included, the long half, never pooled with 0029's 25"; the co-author refutation of 0025–0029 is
still owed and 0032's consequence for E9's figures stands as written — a later entry records it either way. E9-long's
figures enter by their own numbered entry.

**What this does NOT touch.** The H-E9 cell (0029), τ_K, τ_V, τ_agent_K, the rule, the band, the ladder, 0025's keep
subset, `results/e9/`, `results/e8*/`, `results/e9c/` and `config/e9.toml` are unchanged (its sha is in 0029's
report); no `verdict:` line here. The n = 420 arm is not run under this entry. Nothing here is a figure.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the long half of one corpus; a scaled
receiver that is not the trained-range model of 0029 (control 4 says by how much); floor not method (0027); the
four handoffs above {cfg.context_cap:,} and the four with an empty receiver prompt stay excluded by name.

prior-entries-sha256: PLACEHOLDER
"""

if PREVIEW:
    print(ROW)
    print()
    print(ENTRY)
    raise SystemExit(0)

anchor = "| H-E9 | "
i = text.index(anchor)
row_end = text.index("\n", i) + 1
new = text[:row_end] + ROW + "\n" + text[row_end:]
new = new + ("" if new.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0035 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0035 (+ H-E9L row); chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
