"""Append entry 0040 -- E8 on the second model family RAN; the pair's own tau stated. Every figure comes
from an in-process `summarize_e8 --config config/e8f.toml` run (it re-runs the upstream scorer on the
fingerprinted dumps, cross-checks arm (a) against the archived r2.json for every k, and refuses on any
disagreement -- and nothing is written when it refuses). DESCRIPTIVE: no `verdict:` line, no cell moves.

Ordering guard: 0039 on the ledger, 0040 absent. Run facts the summarizer cannot know come as arguments
and are refused when missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC>   --finished <UTC>
  --date <YYYY-MM-DD>   (defaults to --finished's date)
  --preview             (print, do not append)

Why this entry states tau. tau is 1 - THIS pair's own held-out R^2, and `summarize_e9 --calibrate-tau`
cannot produce it yet: `load_e9_config` refuses config/e9f.toml while its three pair-calibrated tau
fields carry UNRESOLVED markers, so the calibration cannot be reached through a config that will not load. The
quantity itself is not blocked -- it is 1 - arm (a)'s held-out R^2 at the verdict k, which the run this
entry reports has just produced and the summarizer has just re-derived from the tensors. So this entry
states it from the verified report; the registration entry that follows writes it into the two E9 configs;
and `summarize_e9 --calibrate-tau` then recomputes it independently from the archived mapper and refuses
on any disagreement with what is written here. Nothing is typed and nothing is chosen after being seen.

Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`."""
import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config, load_seal_config
from linear_ceiling.e8 import required_entries
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models
from linear_ceiling.seal import sidecar_path
from linear_ceiling.summarize_e8 import summarize

NUM, PREV = "0040", "0039"
ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--date", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
a.date = a.date or a.finished[:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"

cfg = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
src_id, tgt_id = pair_models(cfg.pair)
rp = cfg.results_dir / "report.json"
assert rp.exists(), f"{rp} does not exist; E8 has not run on this pair"
rep = json.loads(rp.read_text(encoding="utf-8"))
assert rep.get("pair") == cfg.pair, f"{rp} is for pair {rep.get('pair')!r}, not {cfg.pair!r}"
assert rep.get("upstream_sha") == cfg.upstream_sha, "the report's pin differs from the config's; the pin moved"
assert rep.get("config_sha256") == sha256_file_bytes(cfg.config_path), "config/e8f.toml changed since the run"
assert required_entries(cfg)[-1] == f"### {PREV} ", "config/e8f.toml's [e8.gate] does not name the registering entry"

md = summarize(cfg)                       # refuses on anything wrong; nothing is written then
assert cfg.pair in md, "the summary does not name this pair"
rep = json.loads(rp.read_text(encoding="utf-8"))       # re-read AFTER the summarizer verified it
per_k = rep["per_k"]
kv = str(cfg.verdict_k)

# No seal for this pair, by the amendment entry 0039 registered (operator ruling 2026-09-18): the
# screen line is SHELVED and a descriptive second-family entry carries no screen prediction. What is
# still checked after the fit is that nobody quietly sealed one in between -- a post-fit "pre-fit"
# seal would be exactly the reconstruction decision D2 (entry 0002) had to carve out for the Qwen pair.
scfg = load_seal_config(REPO_ROOT / "config" / "seal.toml", REPO_ROOT)
assert not sidecar_path(cfg.pair, scfg).exists(), (
    f"ledger/predictions/{cfg.pair}.* exists, but 0039 registered that this pair carries no sealed "
    "prediction, and the mapper is now fitted: any seal written since is post-fit. Reconcile before appending.")

# tau is stated here and written into the E9 configs by the NEXT entry; both must still be uncalibrated.
for name in ("e9f", "e9fl"):
    doc = tomllib.loads((REPO_ROOT / "config" / f"{name}.toml").read_text(encoding="utf-8"))["e9"]
    assert doc["pair"] == cfg.pair, f"config/{name}.toml names another pair"
    for key in ("tau_K", "tau_V", "tau_agent_K"):
        v = doc["rule"][key]
        assert isinstance(v, str) and v.startswith("UNRESOLVED::"), \
            (f"config/{name}.toml [e9.rule] {key} is already {v!r}: tau was written into a cell's config before "
             "this entry stated where it came from; the ordering that makes it auditable is gone")

tau_K = 1.0 - float(per_k[kv]["generic"]["K"])
tau_V = 1.0 - float(per_k[kv]["generic"]["V"])
tau_agent_K = 1.0 - float(per_k[kv]["agent"]["K"])
ordered = tau_K < tau_agent_K < 1.0
rows = ["| k | arm (a) generic K / V | arm (b) agent K / V | drop K / V | band K / V |", "|---|---|---|---|---|"]
for k in cfg.report_k:
    r = per_k[str(k)]
    tag = " (verdict-bearing, K and V separately)" if k == cfg.verdict_k else " (reported only)"
    rows.append(f"| {k}{tag} | {r['generic']['K']:.4f} / {r['generic']['V']:.4f} | "
                f"{r['agent']['K']:.4f} / {r['agent']['V']:.4f} | {r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                f"{r['band_outcome']['K']} / {r['band_outcome']['V']} |")
table = "\n".join(rows)
xchk = rep["archived_crosscheck"][kv]["K_r2_heldout_layer_mean"]
fp = rep["mapper"]["files"][kv]
suites = ", ".join(cfg.text["suites"])
n_train = int(round((1 - cfg.holdout_frac) * cfg.text["n_seqs"] * (cfg.text["seq_len"] / cfg.stride)))
tok = rep["tokens"]
rp_rel = rp.resolve().relative_to(Path(REPO_ROOT).resolve()).as_posix()
band = rep["verdict_bearing"]["outcome"]
tau_note = ("" if ordered else
            "  **The registered ordering τ_K < τ_agent_K < 1 does NOT hold on this pair** "
            f"(τ_K = {tau_K:.4f}, τ_agent_K = {tau_agent_K:.4f}): this pair's mapper scores at least as well on "
            "agent text as on generic text. `config.py` refuses any E9 config carrying these two values, so the "
            "short and long cells cannot load until entry 0039's pre-registered contingency is applied by a "
            "numbered entry. Nothing is edited into a config to make it load.")

ENTRY = f"""### {NUM} — {a.date} — E8 ran on the second model family `[BASELINE, DESCRIPTIVE]`: {cfg.pair}; the pair's own τ stated; no cell moves

**Provenance.** Registered by {PREV} before any fit; `config/e8f.toml` and this ledger committed
unmodified; upstream at the pin `{cfg.upstream_sha[:7]}` (the one-line `PAIRS` entry on top of the
RoPE-spec commit), clean for every invoked path; entry {PREV}'s no-seal ruling re-verified AFTER the fit:
no `ledger/predictions/{cfg.pair}.*` sidecar exists, so no post-fit prediction is presented as pre-fit.
{a.box}; launched {a.launched}, finished {a.finished}. Source {src_id}, receiver {tgt_id}. Every figure
below is `summarize_e8 --config config/e8f.toml`'s, from a run that passed all of its checks: the upstream
scorer re-run on the fingerprinted dumps, arm (a) cross-checked against the archived `r2.json` for every k
(at the verdict k: archived {xchk['archived']:.6f} vs recomputed {xchk['recomputed']:.6f}), the mapper
bytes re-hashed (k = {cfg.verdict_k}: `k{cfg.verdict_k}.json` {fp['json'][:12]},
`k{cfg.verdict_k}.safetensors` {fp['safetensors'][:12]}), the agent token file and its manifest re-hashed
({Path(tok['path']).name}, sha256 {tok['sha256'][:12]}).

**What ran.** 0009's instrument with 0016's amendment, unchanged and re-registered by {PREV}: the mapper
is fit on generic calibration text and scored on agent-trace text; arm (a) is the generic held-out arm,
arm (b) the agent arm; the figure is held-out pooled R² (definition A5, per head, averaged over heads then
layers). The sampling RULE is 0016's byte-for-byte — seed {cfg.text['seed']}, n = {cfg.text['n_seqs']},
len = {cfg.text['seq_len']}, suites {suites}, window "{cfg.text['window']}", holdout {cfg.holdout_frac},
stride {cfg.stride} — and the DRAW is this pair's own, re-made under the Llama-3 BPE. Parameter count per
read-out p = k · n_kv · d_h against n_train = {n_train:,}.

{table}

Band (entry 0009, unchanged): HOLDS if the drop ≤ {cfg.band['holds_max_drop']}, DEGRADES if the drop ≥
{cfg.band['degrades_min_drop']}, UNRESOLVED between; verdict k = {cfg.verdict_k} fixed at registration, K
and V read separately and neither alone (0009) → K **{band['K']}** / V **{band['V']}**. **This is a
DESCRIPTIVE reading of the band on a second pair. H-E8's cell was decided by entry 0020 on the Qwen pair
under the registered 0016 protocol; it does not move, this entry carries no `verdict:` line, and no figure
here is pooled with a Qwen figure.**

**This pair's τ, stated here and written nowhere yet.** τ per read-out is 1 − this pair's archived
held-out R² at the verdict k, and it is the only calibration the family's E9 cells may use: **τ_K =
1 − {per_k[kv]['generic']['K']:.4f} = {tau_K:.4f}**, τ_V = 1 − {per_k[kv]['generic']['V']:.4f} =
{tau_V:.4f}, and the alongside agent-text tolerance τ_agent_K = 1 − {per_k[kv]['agent']['K']:.4f} =
{tau_agent_K:.4f} (entry 0025's arm (b) reading, verdict-bearing for nothing).{tau_note} These three come
from the arm (a) and arm (b) numbers in the table above, which the summarizer re-derived from the tensors;
they are not carried over from anything. `config/e9f.toml` and `config/e9fl.toml` still carry their
refusing `UNRESOLVED::` markers at this entry (checked by the script that appended it): the next entry
writes these values in and `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report {rp_rel}`
then recomputes them from the archived mapper independently and refuses on any disagreement. **A Qwen τ appears nowhere in
this family's configs and never will.** **Correction to immutable entry 0039:** its prose said five
τ-derived keys were unresolved. Only `tau_K`, `tau_V`, and `tau_agent_K` carried markers; `tau_ladder =
[0.10, 0.03]` and `prefix_invariance_max_delta = 1e-4` were already literal, registered values. This
correction changes no registered rule or value.

**What this establishes, stated narrowly.** On {src_id} → {tgt_id}, a matched-KV cross-release pair, with
a k = {cfg.verdict_k} linear KV mapper fit on {cfg.text['n_seqs']} generic calibration windows and scored
on {cfg.text['n_seqs']} agent-trace windows drawn under 0016's rule from {suites}, how much held-out
pooled R² the mapper loses under the content distribution shift, at the k values in the table. **Not
established:** anything about H-E8, which is a Qwen claim and is unchanged; anything about on-policy agent
behaviour (the traces are off-policy for Llama-3 exactly as they were for Qwen) or about a real
mid-trajectory switch point; anything pooled across the two pairs; generation quality after reuse.
`eval_hellaswag.py` and `compose_mapper.py` are out of scope for this pair (upstream `apply_mapper`
re-applies with a plain θ and is wrong for `rope_type "llama3"`; entry {PREV}).

**Scope.** All of 0009's, 0016's and {PREV}'s limits: one new pair, one direction, one mapper, one
alignment-free calibration corpus, off-policy text for Llama-3, visible messages only (0012). No
hypothesis cell changes with this entry.

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
