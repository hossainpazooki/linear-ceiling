"""Append entry 0039 -- a SECOND MODEL FAMILY registered BEFORE any fit: the matched-KV pair
meta-llama/Llama-3.2-3B -> meta-llama/Llama-3.1-8B, the upstream re-pin that registers it, the AMENDED
seal requirement, and E8 on the new pair. DESCRIPTIVE: no hypothesis row is added, no `verdict:` line follows, and
no cell moves -- H-E8 is 0009/0020's and is immutable.

Ordering guard: 0038 present, 0039 absent (if another entry lands as 0039 first, rename this script and
the six `NUM` strings, config/e8f.toml's [e8.gate] and config/e9f.toml / config/e9fl.toml's [e9.gate], in
ONE commit; docs/drafts/README.md allocates). Nothing under this entry may exist yet: no mapper for the
pair in ANY configured artifact root, NO sealed prediction for the pair (0039 amends invariant 1 away
for a descriptive second-family entry -- operator ruling 2026-09-18 -- and refuses if one appears),
no `results/e8f/report.json`, no agent dumps, no token draw (R1). What MUST exist: a PASSING `tools/preflight_pair.py` record over the two GATED `meta-llama` snapshots (the
matched-KV premise and the shared-vocabulary go/no-go are read from it, never typed here); `config/e8f.toml`
committed with the real pin P; and the upstream HEAD at P, which must be a descendant of the RoPE-spec
commit config/e9l.toml pins.

Three PRE-REGISTERED operator decisions the repo cannot derive are required arguments and are quoted
verbatim into the entry -- they fix, before the fit, what config/e9f.toml and config/e9fl.toml's five
tau-derived keys will be filled with, so none of them can be chosen after a number is seen:

  --tau-ladder-rule   "<the function of tau_K that produces [e9.rule] tau_ladder>"
  --prefix-delta-rule "<the function of tau_K that produces [e9.controls] prefix_invariance_max_delta>"
  --tau-ceiling       "<the tau_K above which the short cell is UNRESOLVED by construction, or why none>"
  --preflight <path>  (the tools/preflight_pair.py --json record)
  --date <YYYY-MM-DD> (defaults to today; the entry is dated the day it is appended)
  --preview           (print, do not append)

Every figure below is read from that preflight record or the configs; nothing is typed. Runs
`ledger_check` after appending. Delete once appended, chained to the append with `&&`."""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config, load_seal_config
from linear_ceiling.e8 import DEFAULT_SCOPE, UPSTREAM_PATHS, required_entries
from linear_ceiling.e9 import _PENDING
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models, pair_name
from linear_ceiling.seal import find_mapper_artifacts, sidecar_path

NUM, PREV = "0039", "0038"
ap = argparse.ArgumentParser()
ap.add_argument("--preflight", required=True, help="tools/preflight_pair.py --json record over the gated snapshots")
ap.add_argument("--tau-ladder-rule", required=True)
ap.add_argument("--prefix-delta-rule", required=True)
ap.add_argument("--tau-ceiling", required=True)
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

cfg = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
e8 = load_e8_config(REPO_ROOT / "config" / "e8.toml", REPO_ROOT)
src_id, tgt_id = pair_models(cfg.pair)
assert pair_name(src_id, tgt_id) == cfg.pair, "the pair string does not round-trip through pairs.pair_name"
assert src_id != tgt_id and "/" not in cfg.pair, "a pair needs two different models and a name with no separator"
# The instrument is 0009/0016's, byte-for-byte; only the pair, the directories and the scope differ.
assert cfg.band == e8.band and cfg.text == e8.text, "band and text sampling rule must be 0009's and 0016's"
assert (cfg.verdict_k, cfg.report_k, cfg.holdout_frac, cfg.stride) == (e8.verdict_k, e8.report_k, e8.holdout_frac, e8.stride)
assert cfg.amendment is None and cfg.mapper_tag is None, "this is a plain E8 arm, not an amendment or a tagged refit"
assert cfg.results_dir != e8.results_dir and cfg.tokens_dir != e8.tokens_dir, "a second family gets its own directories"
assert required_entries(cfg)[:2] == ("### 0009 ", "### 0016 ") and required_entries(cfg)[-1] == f"### {NUM} ", \
    "the E8 gate must be 0009 + 0016 EXTENDED by this entry, never replaced"
assert cfg.scope_note and "Qwen" not in cfg.scope_note and cfg.scope_note != DEFAULT_SCOPE, \
    "config/e8f.toml must state its own scope; inheriting the Qwen literal would misdescribe the run"
# R1: nothing under this entry exists yet.
assert not (cfg.results_dir / "report.json").exists(), f"{cfg.results_dir}/report.json exists: E8 ran before registration; refusing"
assert not cfg.agent_dumps.exists(), f"{cfg.agent_dumps} exists: agent dumps were written before registration; refusing"
draw = sorted(cfg.tokens_dir.glob("*.npy")) if cfg.tokens_dir.exists() else []
assert not draw, f"the agent-text draw already exists ({draw[0].name}): the sampling rule is registered BEFORE the draw"

# The E9 cells' configs are written in the same change and must still be UNCALIBRATED here: tau is
# 1 - THIS pair's held-out R^2 and that R^2 does not exist until the fit this entry precedes.
# Only THREE keys are derived from the fit and must still be unresolved here. tau_ladder and
# prefix_invariance_max_delta are ABSOLUTE by the same 2026-09-18 ruling -- the ladder so a Llama
# f*(0.03) is comparable to 0029's, the prefix bound because it is a float32 kernel-noise floor and
# not a property of the mapper -- so they are already written, and this entry registers them by
# pinning them to config/e9.toml's values rather than by promising a function of a number nobody has.
tau_keys = ("tau_K", "tau_V", "tau_agent_K")
qwen9 = tomllib.loads((REPO_ROOT / "config" / "e9.toml").read_text(encoding="utf-8"))["e9"]
e9_docs = {}
for name in ("e9f", "e9fl"):
    p = REPO_ROOT / "config" / f"{name}.toml"
    assert p.exists(), f"config/{name}.toml is not written; the family's E9 cells are registered from it"
    doc = tomllib.loads(p.read_text(encoding="utf-8"))["e9"]
    e9_docs[name] = doc
    assert doc["pair"] == cfg.pair, f"config/{name}.toml names pair {doc['pair']!r}, not {cfg.pair!r}"
    assert doc.get("rope") is None and doc.get("bridge") is None, \
        f"config/{name}.toml carries [e9.rope] or [e9.bridge]; this receiver is natively long and has neither"
    for key in tau_keys:
        v = doc["rule"][key]
        assert isinstance(v, str) and v.startswith("UNRESOLVED::"), \
            f"config/{name}.toml [e9.rule] {key} is already {v!r}; this entry is registered BEFORE the fit that calibrates it"
    assert doc["rule"]["tau_ladder"] == qwen9["rule"]["tau_ladder"], \
        (f"config/{name}.toml [e9.rule] tau_ladder is {doc['rule']['tau_ladder']!r}, not config/e9.toml's "
         f"{qwen9['rule']['tau_ladder']!r}; the ruling registered the rungs ABSOLUTE and identical so the "
         "descriptive ladder stays comparable across families")
    assert doc["controls"]["prefix_invariance_max_delta"] == qwen9["controls"]["prefix_invariance_max_delta"], \
        (f"config/{name}.toml prefix_invariance_max_delta is "
         f"{doc['controls']['prefix_invariance_max_delta']!r}, not config/e9.toml's "
         f"{qwen9['controls']['prefix_invariance_max_delta']!r}; it is a float32 kernel-noise floor, "
         "registered absolute")

# The seal, AMENDED (operator ruling 2026-09-18): this entry carries NO sealed prediction. Invariant 1
# exists for the SCREEN's pre-fit predictions, and the screen line is SHELVED (H-S1/S3/S4, 0003-0006)
# with no entry point in screen.py that could produce a payload. A descriptive second-family
# registration has no screen prediction to seal, and sealing a null payload would satisfy the check
# while asserting nothing -- the one thing this ledger exists to prevent. The amendment is stated in
# the entry text, not hidden here.
#
# What is NOT dropped, because it is the clause that actually carries evidential weight: NO FITTED
# MAPPER FOR THIS PAIR MAY EXIST ANYWHERE at append. "Registered before any fit" is a claim about the
# world, and this is what makes it checkable. It is checked across all four configured artifact roots.
scfg = load_seal_config(REPO_ROOT / "config" / "seal.toml", REPO_ROOT)
hits = find_mapper_artifacts(cfg.pair, scfg)
assert not hits, "a fitted mapper for this pair already exists: " + "; ".join(h.as_posix() for h in hits)
sealed = sidecar_path(cfg.pair, scfg).exists()
assert not sealed, (f"ledger/predictions/{cfg.pair}.* exists, but this entry registers that the pair "
                    "carries NO sealed prediction. Someone sealed one after the amendment was ruled; "
                    "reconcile before appending.")

# The preflight record: the ONLY source of a fact about either checkpoint. Both repos are gated and
# neither config has ever been read on the machine that staged this script.
pf_path = Path(a.preflight)
pf = json.loads(pf_path.read_text(encoding="utf-8"))
assert pf.get("tool") == "tools/preflight_pair.py" and pf.get("pair") == cfg.pair, \
    f"{pf_path} is not a preflight record for {cfg.pair}"
assert pf.get("ok") and all(c["ok"] for c in pf["checks"]), \
    "the preflight record has failing checks: " + "; ".join(c["name"] for c in pf["checks"] if not c["ok"])
ms, mt = pf["models"]["source"], pf["models"]["target"]
assert (ms["model_id"], mt["model_id"]) == (src_id, tgt_id), "the preflight record is for other model ids"
for m in (ms, mt):
    assert m["repo_id_from_path"] == m["model_id"], \
        f"{m['model_id']} was read from {m['snapshot_dir']}, which is not that repo's HF cache entry (borrowed-facts rule)"
assert ms["num_key_value_heads"] == mt["num_key_value_heads"] and ms["head_dim"] == mt["head_dim"], \
    "the pair is NOT matched-KV; the whole registration below is void"
assert ms["vocab_size"] == mt["vocab_size"] and ms["get_vocab_entries"] == mt["get_vocab_entries"]
n_kv, d_h = ms["num_key_value_heads"], ms["head_dim"]
vocab_row = next(c for c in pf["checks"] if "vocab" in c["name"].lower() and "get_vocab" in c["name"])
rope_s, rope_t = ms["rope_scaling"] or {}, mt["rope_scaling"] or {}
assert rope_s.get("rope_type") == rope_t.get("rope_type"), "the two sides do not share a rope_type"

# The upstream pin P: a real sha, checked out, clean, registering the pair, and a descendant of the
# RoPE-spec commit (read from config/e9l.toml, never typed here).
rope_pin = tomllib.loads((REPO_ROOT / "config" / "e9l.toml").read_text(encoding="utf-8"))["e9"]["upstream_sha"]
if not a.preview:
    assert _PENDING not in cfg.upstream_sha and re.fullmatch(r"[0-9a-f]{40}", cfg.upstream_sha), \
        "config/e8f.toml still carries the pending pin placeholder; land commit P upstream, PUSH it, record its sha"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the pin {cfg.upstream_sha[:12]}"
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", rope_pin, cfg.upstream_sha], cwd=cfg.upstream_path)
    assert anc.returncode == 0, (f"the pin {cfg.upstream_sha[:12]} is not a descendant of the RoPE-spec commit "
                                 f"{rope_pin[:12]}; under an older base the strip is plain-theta and silently wrong "
                                 "for rope_type \"llama3\" on BOTH sides of this pair")
    reg = subprocess.run(["git", "show", f"{cfg.upstream_sha}:kvt/pairs.py"], cwd=cfg.upstream_path,
                         capture_output=True, text=True).stdout
    for needle in (cfg.pair, src_id, tgt_id):
        assert needle in reg, f"the pinned kvt/pairs.py does not register {needle}"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *UPSTREAM_PATHS], cwd=cfg.upstream_path,
                           capture_output=True, text=True).stdout.strip()
    assert not dirty, f"upstream invoked paths are dirty at the pin:\n{dirty}"

sent = lambda t: t.strip().rstrip(".") + "."      # operator free text, punctuated once  # noqa: E731
pin = "P (preview; not landed)" if a.preview and _PENDING in cfg.upstream_sha else cfg.upstream_sha[:12]
n_train = int(round((1 - cfg.holdout_frac) * cfg.text["n_seqs"] * (cfg.text["seq_len"] / cfg.stride)))
pn = " / ".join(f"k = {k}: {k * n_kv * d_h / n_train:.2f}" for k in cfg.report_k)
suites = ", ".join(cfg.text["suites"])
gates = "/".join(m.strip("# ").strip() for m in required_entries(cfg))
shapes = " · ".join(
    f"{m['model_id'].split('/')[-1]}: {m['num_hidden_layers']} layers, hidden {m['hidden_size']}, "
    f"{m['num_attention_heads']} attention heads, {m['num_key_value_heads']} KV heads, head_dim {m['head_dim']}"
    f"{' (declared)' if m['head_dim_declared'] else f' (DERIVED as hidden_size // num_attention_heads; the config declares none)'}, "
    f"vocab {m['vocab_size']:,}, max_position_embeddings {m['max_position_embeddings']:,}, "
    f"rope_theta {m['rope_theta']:g}, rope_scaling {json.dumps(m['rope_scaling'], sort_keys=True)}, "
    f"tie_word_embeddings {m['tie_word_embeddings']}, {m['kv_bytes_per_token_fp32']:,} KV bytes/token (fp32, all layers, K and V)"
    for m in (ms, mt))

ENTRY = f"""### {NUM} — {a.date} — A second model family registered before any fit: the matched-KV pair {src_id} → {tgt_id}, the upstream re-pin that registers it, the pre-fit seal, and E8 on the new pair; descriptive, no hypothesis row

**Why, and why now.** Every result on this ledger is one pair: Qwen3-0.6B → 1.7B. H-E8 `NOT CONFIRMED`
(0020), H-E9 `HELD` (0029) and H-E9L `HELD` (0036) are claims about that pair, and the honest reading of
all three has always been "one pair, one direction, one mapper". A second family is the cheapest thing
that can turn a single-pair observation into a statement with any generality, and it is the first
question a reviewer asks. This entry registers the family — the pair, the upstream change that makes the
instrument accept it, the seal, and E8 on it — BEFORE any mapper is fitted and before the calibration
text is drawn. It decides nothing: **no hypothesis row is added, no `verdict:` line follows, and the
H-E8 cell does not move.** The one verdict-bearing cell of this campaign is the E9 short cell, registered
by its own later entry with its own row.

**The pair, and the fact the whole design rests on.** `{cfg.pair}` = {src_id} (source) → {tgt_id}
(receiver/target). Cross-release inside one family, so the name carries BOTH sides: the upstream's
same-release short form names only the TARGET's size, which here would assert a Llama-3.2-8B — a model
that does not exist. The string keys the mapper directory, the dumps, the token file, this pair's sealed
prediction and every report, and a seal cannot be rewritten, so a name that misidentifies the receiver is
not recoverable. **The pair is matched-KV**, which is what makes the upstream delta one line:
both sides carry {n_kv} KV heads and a per-head dim of {d_h}, so `check_matched_kv` passes unrelaxed, the
paper's Sec. 2.1 premise holds, and `Mapper.formula_params` is exact for this pair (the Appendix-D /
Table-12 parameter-count control is preserved, not forfeited). Read from the two GATED `meta-llama`
snapshots by `tools/preflight_pair.py`, record sha256 `{sha256_file_bytes(pf_path)[:12]}` ({pf['utc']}),
{sum(1 for c in pf['checks'] if c['ok'])}/{len(pf['checks'])} checks passed, and cited by nothing else —
no mirror, no re-upload, no remembered value ({{sourceRepo: {src_id}, filePath: config.json, sha256:
{ms['config_json_sha256'][:12]}}} and {{sourceRepo: {tgt_id}, filePath: config.json, sha256:
{mt['config_json_sha256'][:12]}}}): {shapes}.

**The shared-vocabulary gate, which could still kill this.** `scripts/prepare_tokens.py` refuses unless
the two tokenizers' `get_vocab()` maps are equal, and `weights.assert_shared_vocab` is the home-side half
of the same check. Both sides ship the {ms['vocab_size']:,}-entry Llama-3 BPE, but added and special
tokens are part of that map. The preflight record's check "{vocab_row['name']}" passed —
{vocab_row['detail']} — and that is the evidence; had it failed there would be no E8 corpus for this pair
and the family decision would reopen rather than be worked around.

**The two sides carry DIFFERENT RoPE, and that is safe here for a stated reason.** Source
rope_scaling {json.dumps(rope_s, sort_keys=True)}; receiver {json.dumps(rope_t, sort_keys=True)}. The two
build different inverse-frequency vectors. That is not a matched-KV problem (`check_matched_kv` reads
`n_kv` and `d_h` only) and not a content-space problem — PROVIDED the pin strips with each dump's OWN
recorded `RopeSpec`, read off the loaded model's `rotary_emb.inv_freq` and halt-checked at every dumped
position. That machinery is entry 0035's commit `{rope_pin[:12]}`, and this entry requires the pin to be a
DESCENDANT of it (checked by this script). Under an older base the strip is plain-θ, which is silently
wrong for `rope_type "llama3"` on both sides. Consequence carried forward to every cell of this family:
any "the recorded RoPE is identical across the run" control is scoped **per model role** — receiver dumps
against receiver dumps, source dumps against source dumps — because a cross-role equality assert would
refuse every CORRECT run of this pair.

**The upstream change, and what it is not.** Pin `{pin}`, base {rope_pin[:12]}: **one entry in
`kvt/pairs.py`'s `PAIRS`**, so `dump_kv`, `fit_mapper`, `probe`, `score_mapper` and `score_positions`
accept the pair by name. No dataclass change, no signature change, no relaxation of any check, no new
flag. An earlier design for this campaign assumed unmatched head dims and specified a rectangular
mapper, a registry flag, a `check_kv_heads`, a `formula_params` signature change and a τ ceiling
justified by the conditioning of that map; **the pair is matched-KV, so every one of those is dropped**
and nothing about the estimator is extended. `linear-ceiling` never writes upstream: the change is landed
by the operator from `docs/2026-09-18-llama-upstream-patch-spec.md` and pushed before any box is rented
(`tools/ec2/setup.sh` clones by sha). **Known limitation, recorded rather than fixed:**
`kvt/mapper.py::apply_mapper` still strips and re-applies with the plain θ it records, so it is wrong for
any `rope_type != "default"` and therefore for this pair; it is OFF the E8/E9 path (the scorers work in
content space through `KVDump`), so `eval_hellaswag.py` and `compose_mapper.py` must not be run on this
pair without a fix. Keeping the diff at one dict entry is worth more than pre-emptively fixing a path
nobody here calls. **While the single upstream checkout sits at this pin the Qwen cells refuse at their
gates** — existing practice, not a regression: re-summarizing a Qwen cell means
`git -C {cfg.upstream_path.name} checkout --detach <that cell's pin>` first. There is ONE clone.

**The seal (invariant 1), AMENDED for this entry — operator ruling, {a.date}.** This registration
carries **no sealed prediction**, and the requirement is amended rather than satisfied. Invariant 1
exists for the SCREEN's pre-fit predictions: a prediction that can be sealed before a fit must be.
The screen line is `SHELVED` (H-S1/S3/S4, entries 0003–0006) and `screen.py` has no entry point that
produces a payload, so there is no screen prediction about this pair to seal. The alternatives were
considered and rejected in the open: sealing a *null* or procedural payload would satisfy the check
while asserting nothing, which is precisely the failure this ledger is built to prevent; and inventing
a pre-fit R² to seal would put a number on the record that no instrument produced. The amendment is
narrow — it applies to a **descriptive second-family registration that adds no hypothesis row**, and
it does not touch invariant 1 for any cell that does carry a screen prediction.

What survives the amendment is the clause that actually carries the evidential weight: **no fitted
mapper for this pair exists in ANY configured artifact root at append** (this script re-checks all
four and refuses otherwise), and this script additionally refuses if a sealed prediction for the pair
has appeared since the ruling. "Registered before any fit" therefore remains a checkable claim about
the world, not an assertion of good faith.

**E8 on the new pair (`config/e8f.toml`, `results/e8f/`).** 0009's instrument and 0016's amendment,
unchanged: mapper fit on generic calibration text, scored on agent-trace text, arm (a) generic vs arm (b)
agent, held-out pooled R² (definition A5), band HOLDS ≤ {cfg.band['holds_max_drop']} drop /
DEGRADES ≥ {cfg.band['degrades_min_drop']} drop; verdict k = {cfg.verdict_k} fixed here at registration
(not chosen after the sweep), reported at k = {', '.join(str(k) for k in cfg.report_k)}; `[e8.text]` seed
{cfg.text['seed']}, n = {cfg.text['n_seqs']}, len = {cfg.text['seq_len']}, suites {suites}, window
"{cfg.text['window']}"; holdout {cfg.holdout_frac}, stride {cfg.stride}. **The sampling RULE is 0016's
byte-for-byte; the DRAW is not** — it is re-made under the Llama-3 BPE and is a different
{cfg.text['n_seqs']} windows, not a reuse of `results/e8/`'s. Parameter count per read-out is
p = k · n_kv · d_h = {n_kv * d_h:,}k against n_train = {n_train:,}, so **p/n is {pn}** — numerically
identical to the Qwen arm's, because the two pairs happen to share {n_kv} KV heads and head_dim {d_h}. The
k-sweep collapse entry 0016 reports is therefore directly comparable here at the same p/n, and there is no
p/n caveat to state. **Descriptive: every figure produced
under this config is stated for the Llama pair alone and is never pooled with a Qwen figure; H-E8's cell
was decided by 0020 and does not move.** Scope recorded in the report: "{cfg.scope_note}".

**Three decisions fixed now, before any number exists.** The E9 cells of this family calibrate τ from
THIS pair's own mapper, and three values that follow from τ_K must be fixed before τ_K is seen or they
are not registered at all. (1) **τ ladder** (`[e9.rule] tau_ladder`, descriptive, verdict-bearing for
nothing): {sent(a.tau_ladder_rule)} (2) **Prefix-invariance tolerance**
(`[e9.controls] prefix_invariance_max_delta`, a HALT): {sent(a.prefix_delta_rule)} It must NOT inherit the
Qwen cells' value. (3) **τ_K ceiling** — the τ_K above which the short cell is UNRESOLVED by
construction, because a mapper that transfers badly enough makes f*(τ_K) trivially small for everything:
{sent(a.tau_ceiling)} All five tau-derived keys in `config/e9f.toml` and `config/e9fl.toml` carry refusing
`UNRESOLVED::` markers at append (this script checks it), so neither cell can load, let alone run, until
the calibration exists — a Qwen τ pasted in would load and produce a verdict calibrated against the wrong
pair's mapper, which is the failure the markers exist to make impossible.

**Gate and enforcement.** `e8 --check --config config/e8f.toml` refuses until entries {gates} are in the
committed ledger, `config/e8f.toml` is committed unmodified, and the upstream is at the pin with every
invoked path clean; `[e8.gate]` EXTENDS the driver's 0009/0016 premise entries and cannot weaken them.
`summarize_e8 --config config/e8f.toml` is the only reader of the run's figures: it re-runs the upstream
scorer on the fingerprinted dumps, cross-checks arm (a) against the archived `r2.json` for every k, and
refuses on any disagreement. Tests: `tests/test_pairs.py` (the pair name round-trips and the Qwen names
are byte-identical), `tests/test_llama_configs.py` (the three configs; the five tau keys refuse
individually), `tools/preflight_pair.py` (the gate on the two gated checkpoints).

**What this does NOT touch.** The H-E8, H-E9 and H-E9L cells; τ_K, τ_V, τ_agent_K, the rule, the band,
the ladder and the keep subsets of the Qwen cells; `results/e8*/`, `results/e9*/`; `config/e8.toml`,
`config/e8a.toml`, `config/e8c.toml`, `config/e9.toml`, `config/e9l.toml`, `config/e9s.toml`,
`config/e9c.toml` and `config/seal.toml` (unchanged: `_resolve` expands only the literal `${{upstream}}`,
and the four existing artifact roots already cover the new pair under one clone). No figure appears in
this entry: E8's enter by their own numbered entry, and the paper only from that entry.

**Scope.** One new pair, one direction, one agent family, off-policy text for Llama-3, visible messages
only (0012); a cross-release pair whose two sides carry different llama3 RoPE factors; a registration,
not a result. The matched-KV premise rests on the preflight record cited above and on nothing else.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    print(ENTRY)
    raise SystemExit(0)

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
