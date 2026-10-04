"""Append entry 0053 -- the second family's E8 amendment RAN (registered by 0052): arm (b) over every agent sequence;
figures only, written ONLY from `summarize_e8.summarize` run in-process on `config/e8fa.toml`. DESCRIPTIVE: no
`verdict:` line, no hypothesis row; band words are 0009's band read for orientation; the H-E8 cell (0020) and this
family's tau (0040) do not move.

Ordering guard: 0052 on the ledger, 0053 absent; the summarizer must PASS (it re-runs the upstream scorer on the
fingerprinted dumps, recomputes per-sequence R^2 from the per-token record against both the report and the re-scored
json, re-checks the prior report's hash, and bootstraps). Every figure is read from the summary it writes; the
distinct-window counts are recomputed from the token file, not copied from 0040 or 0052.
  --date <YYYY-MM-DD>   defaults to today     --preview   print, do not append
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
On a CRLF checkout run it after `e8.py`/`summarize_e8.py` hash the config as text (or write the LF blob first).
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.config import load_e8_config                 # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file   # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402
from linear_ceiling.summarize_e8 import summarize                # noqa: E402

NUM, PREV, REG = "0053", "0052", "0052"
E8_FIGURES, TAU_RULING = "0040", "0041"
CONFIG = REPO_ROOT / "config" / "e8fa.toml"

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"


def git(*args, cwd=REPO_ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
ordering_ok = f"### {PREV} " in text and f"### {NUM} " not in text
assert f"### {REG} " in text, "the registration entry is not on the ledger"

assert git("status", "--porcelain", "--", str(CONFIG.relative_to(REPO_ROOT))) == "", "config/e8fa.toml is modified"
cfg = load_e8_config(CONFIG, REPO_ROOT)
assert cfg.amendment and cfg.amendment["entry"] == REG, f"[e8.amendment] entry must be {REG}"
config_sha = sha256_text_file(CONFIG)

# --- the gate: the summarizer, in-process, fail-closed ---------------------------------------------------------------
summarize(cfg)                                            # raises on any disagreement; writes summary.{json,md}
rdir = REPO_ROOT / cfg.results_dir
rep = json.loads((rdir / "report.json").read_text(encoding="utf-8"))
summ = json.loads((rdir / "summary.json").read_text(encoding="utf-8"))
assert rep["upstream_sha"] == cfg.upstream_sha and rep.get("amendment", {}).get("entry") == REG
assert summ["reused_agent_dumps_from"]["report"].replace("\\", "/").endswith("results/e8f/report.json")
report_sha, summary_sha = sha256_file_bytes(rdir / "report.json"), sha256_file_bytes(rdir / "summary.json")
prior = json.loads((REPO_ROOT / "results" / "e8f" / "report.json").read_text(encoding="utf-8"))
prior_sha = sha256_file_bytes(REPO_ROOT / "results" / "e8f" / "report.json")
assert summ["reused_agent_dumps_from"]["sha256"] == prior_sha, "the prior report's hash in the summary is not the file's"

# --- the draw's repetition, recomputed from the token file -----------------------------------------------------------
tok = REPO_ROOT / rep["tokens"]["path"]
assert sha256_file_bytes(tok) == rep["tokens"]["sha256"] == prior["tokens"]["sha256"]
rows = np.load(tok)
_, counts = np.unique(rows, axis=0, return_counts=True)
n_rows, n_distinct, max_mult = int(rows.shape[0]), int(len(counts)), int(counts.max())
n_distinct_heldout = int(len(np.unique(rows[-int(np.ceil(0.2 * n_rows)):], axis=0)))

# --- figures ---------------------------------------------------------------------------------------------------------
def f4(x, sign=False):
    return f"{x:+.4f}" if sign else f"{x:.4f}"


def st(d):
    return f"{d['median']:.4f} (p10 {d['p10']:.4f}, p90 {d['p90']:.4f})"


ks = [str(k) for k in cfg.report_k]
rows_md, seq_md, vk = [], [], str(cfg.verdict_k)
for k in ks:
    rc, m = summ["recomputed"][k], summ["per_k"][k]
    pri = prior["per_k"][k]["agent"]
    ch, b = m["change_from_prior"], m["bootstrap"]
    n_tok, n_seq = m["n_heldout_tokens"]["agent"], m["n_heldout_seqs"]["agent"]
    label = f"{k} ({E8_FIGURES} verdict k)" if k == vk else k
    rows_md.append(
        f"| {label} | {n_seq} / {n_tok:,} | {f4(rc['generic']['K'])} / {f4(rc['generic']['V'])} | **{f4(rc['agent']['K'])} / {f4(rc['agent']['V'])}** "
        f"| {f4(pri['K'])} / {f4(pri['V'])} | {f4(ch['K'], True)} / {f4(ch['V'], True)} | {f4(rc['drop']['K'], True)} / {f4(rc['drop']['V'], True)} "
        f"| [{f4(b['K']['drop_lower_2.5'], True)}, {f4(b['K']['drop_upper_97.5'], True)}] | [{f4(b['V']['drop_lower_2.5'], True)}, {f4(b['V']['drop_upper_97.5'], True)}] "
        f"| {rc['band_outcome']['K']} / {rc['band_outcome']['V']} |")
    ps = m["per_sequence"]
    seq_md.append(f"| {k} | {st(ps['agent_K'])} | {st(ps['agent_V'])} | {st(ps['generic_K'])} | {st(ps['generic_V'])} |")

r1, m1, p1 = summ["recomputed"][vk], summ["per_k"][vk], prior["per_k"][vk]
all_K, gen_K = float(r1["agent"]["K"]), float(r1["generic"]["K"])
tau_K, tau_agent_K, tau_agent_all = 1.0 - float(p1["generic"]["K"]), 1.0 - float(p1["agent"]["K"]), 1.0 - all_K
inversion = ("persists: arm (b) over every sequence still scores above arm (a) on K" if all_K > gen_K
             else "does not persist: arm (b) over every sequence scores at or below arm (a) on K")
drop_word = {"K": r1["band_outcome"]["K"], "V": r1["band_outcome"]["V"]}
seed, reps = int(cfg.amendment["bootstrap_seed"]), int(cfg.amendment["bootstrap_reps"])

ENTRY = f"""### {NUM} — {a.date} — E8 amendment ran on the second model family `[BASELINE, DESCRIPTIVE]`: arm (b) over every agent sequence; the inversion {('persists' if all_K > gen_K else 'does not persist')}; no cell and no τ moves

**Provenance.** Registered by {REG} before any rescoring; `config/e8fa.toml` (sha256 `{config_sha[:12]}`) and this ledger committed
unmodified; upstream at the family's pin `{cfg.upstream_sha[:7]}`, clean for the invoked paths; {E8_FIGURES}'s agent dumps and token file
(`{tok.name}`, sha256 `{rep['tokens']['sha256'][:12]}`) reused byte for byte, fingerprints checked at run time and again by the summarizer
against `results/e8f/report.json` (sha256 `{prior_sha[:12]}`); arm (a) cross-checked against the archived `r2.json` for every k. Every
figure below is `summarize_e8 --config config/e8fa.toml`'s: the scorer re-run on the fingerprinted dumps, per-sequence R² recomputed from
the per-token record and checked against both the report and the re-scored json, the prior report's hash re-checked. Pinned:
`report.json` `{report_sha[:12]}`, `summary.json` `{summary_sha[:12]}`. Arm (a) keeps the mapper's own held-out fraction 0.2; arm (b)
scores all {n_rows} agent sequences ({m1['n_heldout_tokens']['agent']:,} tokens) — {E8_FIGURES} had scored the last {int(np.ceil(0.2 * n_rows))}
({int(np.ceil(0.2 * n_rows)) * int(rows.shape[1]) // cfg.stride:,} tokens at the matched protocol).

**The draw, restated beside the figures (recomputed from the token file).** {n_rows} rows, **{n_distinct} distinct windows**, the most repeated
window {max_mult} times; the registered hold-out was **{n_distinct_heldout} distinct windows**. The bootstrap below resamples rows, so a repeated
window carries its multiplicity; nothing here de-duplicates, because 0016's rule drew rows and this entry rescored the rows it drew.

| k | agent seqs / tokens | arm (a) generic K / V | arm (b) agent, ALL K / V | {E8_FIGURES}'s arm (b) K / V | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows_md)}

Bootstrap: seeded percentile over agent sequences (seed {seed} + k, {reps:,} reps), 2.5% / 97.5% of the drop; reported, read by nothing.
Band words are 0009's band applied to the all-sequence drop for orientation only.

**Per-sequence R² (a share of the pooled decomposition, SST around the global held-out mean), median (p10, p90):**

| k | agent K | agent V | generic K | generic V |
|---|---|---|---|---|
{chr(10).join(seq_md)}

**What changed and what did not.** At k = {vk}, scoring every agent sequence instead of the last {int(np.ceil(0.2 * n_rows))} moves arm (b) by
{f4(m1['change_from_prior']['K'], True)} (K) / {f4(m1['change_from_prior']['V'], True)} (V); the drop is {f4(r1['drop']['K'], True)} / {f4(r1['drop']['V'], True)} with 95% bootstrap
[{f4(m1['bootstrap']['K']['drop_lower_2.5'], True)}, {f4(m1['bootstrap']['K']['drop_upper_97.5'], True)}] / [{f4(m1['bootstrap']['V']['drop_lower_2.5'], True)}, {f4(m1['bootstrap']['V']['drop_upper_97.5'], True)}], read against
0009's band as {drop_word['K']} / {drop_word['V']} ({E8_FIGURES}, at the matched protocol: {p1['band_outcome']['K']} / {p1['band_outcome']['V']}). **The question {TAU_RULING} left open:**
the τ_agent_K < τ_K inversion {inversion} (all-sequence arm (b) K {f4(all_K)} against arm (a) K {f4(gen_K)}); whether that is a property of
the pair or of a draw with {n_distinct} distinct windows is narrowed, not closed — the windows are the same {n_distinct}. **τ_agent_K stays
{E8_FIGURES}'s registered value, 1 − {f4(float(p1['agent']['K']))} = {f4(tau_agent_K)}; the all-sequence counterpart, 1 − {f4(all_K)} = {f4(tau_agent_all)}, is
reported here beside it and substituted for nothing** (0044 has already read τ_agent_K; τ_K = {f4(tau_K)} is untouched). **No cell moves; this
entry carries no `verdict:` line; nothing here is pooled with a Qwen figure.**

**Not established.** Anything beyond {E8_FIGURES}'s limits: off-policy text for Llama-3, one pair, one direction, one mapper, visible messages
only (0012); the agent windows are 0016's draw under the Llama-3 BPE, not new text, and {n_rows - n_distinct} of the {n_rows} rows repeat another; arm (a)'s
figure is on the mapper's own held-out generic sequences and its per-sequence spread is over that many. H-E8 is 0020's and is unchanged.

**Scope.** All of 0009's, 0016's, 0039's, {E8_FIGURES}'s and {REG}'s limits. No hypothesis cell changes with this entry.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print(f"[ordering guard: {'ok' if ordering_ok else f'NOT satisfied — {PREV} absent or {NUM} present'}]")
    raise SystemExit(0)
assert ordering_ok, f"ordering: {PREV} present, {NUM} absent"
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head_m = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head_m.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
