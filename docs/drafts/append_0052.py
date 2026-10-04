"""Append entry 0052 -- E8 amendment REGISTERED on the second model family before any rescoring: arm (b) over every
agent sequence (entry 0030's protocol) on 0040's own tensors, `config/e8fa.toml`. DESCRIPTIVE: no hypothesis row,
no band read for a verdict, no `verdict:` line; the H-E8 cell (0020, Qwen) and this family's tau (0040) do not move.

Ordering guard: 0054 (the file's last entry) on the ledger, 0052 absent. `ledger_check` chains by FILE order and the
README allocates numbers, so this entry appends when its inputs are ready and precedes 0048-0051 in the file (the 0054
precedent, recorded in that entry's Numbering paragraph).
Nothing under this entry may exist yet: `results/e8fa/` holds no report, summary or per-token record (R1).
Every claim below about the instrument or the record is CHECKED against the tree, never typed:
  - config/e8fa.toml is tracked and unmodified, names this entry, reuses results/e8f/report.json, scores arm (b) at 1.0;
  - the upstream clone is at the family's pin and that pin contains the 0030 upstream change (223f469 is its ancestor);
  - 0040's report pins the agent dumps and the token file; the token file on disk matches, and its distinct-window
    count is recomputed here (0040 disclosed 42 of 50), as is the multiplicity of the most repeated window;
  - entry 0041 still contains the sentence that calls for this rescoring;
  - the driver's gate for this config is exactly 0009 + 0016 + 0039 + this entry.
usage: python docs/drafts/append_0052.py [--date YYYY-MM-DD] [--preview]
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
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
from linear_ceiling import e8 as e8_driver                      # noqa: E402
from linear_ceiling.config import load_e8_config                 # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file   # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, PREV = "0052", "0054"     # ledger_check chains by FILE order (the 0054 precedent): 0054 is the last entry in the file; 0048-0051 land later
FAMILY, E8_FIGURES, TAU_RULING, QWEN_AMEND = "0039", "0040", "0041", "0030"
CONFIG = REPO_ROOT / "config" / "e8fa.toml"
PRIOR_REPORT = REPO_ROOT / "results" / "e8f" / "report.json"
UPSTREAM_0030 = "223f469164734a5780110a5e2e906a2af3c36b1a"
CALLS_FOR_IT = ("needs arm (b) rescored at `agent_holdout_frac = 1.0` over every agent sequence, and enters by "
                "its own numbered entry")

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"


def git(*args, cwd=REPO_ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def entry_block(text: str, num: str) -> str:
    """One entry's text with line wraps collapsed, so a quoted sentence matches however the ledger wrapped it."""
    i = text.index(f"### {num} ")
    j = text.find("\n### ", i + 1)
    return " ".join((text[i:] if j < 0 else text[i:j]).split())


LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
ordering_ok = f"### {PREV} " in text and f"### {NUM} " not in text
for n in (FAMILY, E8_FIGURES, TAU_RULING, QWEN_AMEND):
    assert f"### {n} " in text, f"entry {n} is not on the ledger"
assert CALLS_FOR_IT in entry_block(text, TAU_RULING), f"entry {TAU_RULING} no longer carries the sentence that calls for this rescoring"
assert "42 distinct windows" in entry_block(text, E8_FIGURES), f"entry {E8_FIGURES} no longer carries the distinct-window disclosure"

# --- the config: tracked, unmodified, and saying what this entry says it says --------------------------------------
tracked = bool(git("ls-files", "--", str(CONFIG.relative_to(REPO_ROOT))))
unmodified = git("status", "--porcelain", "--", str(CONFIG.relative_to(REPO_ROOT))) == ""
config_committed = tracked and unmodified          # asserted at append; reported in --preview so the text can be read before the commit
cfg = load_e8_config(CONFIG, REPO_ROOT)
assert cfg.amendment and cfg.amendment["entry"] == NUM, f"[e8.amendment] entry must be {NUM}"
assert cfg.pair == "llama3.2-3b-to-llama3.1-8b" and cfg.gate == (FAMILY,)
assert (REPO_ROOT / cfg.reuse_agent_dumps_from).resolve() == PRIOR_REPORT.resolve() and cfg.agent_holdout_frac == 1.0
assert cfg.holdout_frac == 0.2 and cfg.verdict_k == 1 and tuple(cfg.report_k) == (1, 4, 8)
assert cfg.results_dir.name == "e8fa" and (REPO_ROOT / cfg.results_dir).resolve() != PRIOR_REPORT.parent.resolve()
e8f = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
assert cfg.upstream_sha == e8f.upstream_sha, "one pin per family: e8fa must pin what e8f pins"
assert cfg.text == e8f.text and cfg.band == e8f.band and cfg.generic_dumps == e8f.generic_dumps
gate = e8_driver.required_entries(cfg)
assert gate == e8_driver.REQUIRED_ENTRIES + (f"### {FAMILY} ", f"### {NUM} "), f"gate is {gate}"
config_sha = sha256_text_file(CONFIG)

# --- R1: nothing under this entry exists yet ----------------------------------------------------------------------
rdir = REPO_ROOT / cfg.results_dir
for p in ("report.json", "summary.json", "summary.md"):
    assert not (rdir / p).exists(), f"{rdir / p} exists: a run happened before registration; refusing"
assert not (rdir / "per_token").exists() or not any((rdir / "per_token").iterdir()), "per-token records exist before registration"

# --- the upstream pin holds and contains the 0030 change -----------------------------------------------------------
up = REPO_ROOT / cfg.upstream_path
head = git("rev-parse", "HEAD", cwd=up)
assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the family's pin {cfg.upstream_sha[:12]}; detach it first"
assert subprocess.run(["git", "merge-base", "--is-ancestor", UPSTREAM_0030, cfg.upstream_sha], cwd=up).returncode == 0, \
    "the family's pin does not contain the 0030 upstream change (per-sequence moments, --holdout-frac 1.0)"
score_mapper = (up / "scripts" / "score_mapper.py").read_text(encoding="utf-8")
assert "--holdout-frac" in score_mapper and "per_sequence" in score_mapper

# --- 0040's record: the tensors this entry reuses, by fingerprint -----------------------------------------------------
prior = json.loads(PRIOR_REPORT.read_text(encoding="utf-8"))
prior_sha = sha256_file_bytes(PRIOR_REPORT)
tok = REPO_ROOT / prior["tokens"]["path"]
assert tok.exists() and sha256_file_bytes(tok) == prior["tokens"]["sha256"], "0040's token file is missing or changed"
rows = np.load(tok)
n_rows, seq_len = rows.shape
_, inv, counts = np.unique(rows, axis=0, return_inverse=True, return_counts=True)
n_distinct, max_mult = int(len(counts)), int(counts.max())
assert n_distinct == 42, f"0040 disclosed 42 distinct windows; the file holds {n_distinct}"
heldout_rows = rows[-int(np.ceil(0.2 * n_rows)):]
n_distinct_heldout = int(len(np.unique(heldout_rows, axis=0)))
agent_dumps = prior["dumps"]["agent"]
n_agent_dumps = sum(len(v) for v in agent_dumps.values()) if isinstance(agent_dumps, dict) else len(agent_dumps)
pk = prior["per_k"][str(cfg.verdict_k)]
b_K, b_V, a_K = float(pk["agent"]["K"]), float(pk["agent"]["V"]), float(pk["generic"]["K"])
tau_agent_K, tau_K = 1.0 - b_K, 1.0 - a_K

ENTRY = f"""### {NUM} — {a.date} — E8 amended on the second model family before any rescoring: arm (b) over every agent sequence on 0040's own tensors; descriptive; no cell and no τ moves

**Why, and why now.** Entry {E8_FIGURES} ran 0009's instrument on `llama3.2-3b-to-llama3.1-8b` at 0016's matched protocol, so
arm (b) was scored on the LAST ⌈0.2 × {n_rows}⌉ = {len(heldout_rows)} agent sequences; it disclosed that the draw holds **{n_distinct} distinct
windows in {n_rows} rows** (one window {max_mult} times) and that the registered hold-out is **{n_distinct_heldout} distinct windows**. Entry
{TAU_RULING} left open whether the pair's τ_agent_K < τ_K inversion (1 − {b_K:.4f} = {tau_agent_K:.4f} against 1 − {a_K:.4f} = {tau_K:.4f})
"is a property of the pair or of the draw", and said it "{CALLS_FOR_IT}". Entry {QWEN_AMEND} registered exactly that rescoring
for the Qwen pair; this entry re-registers it for this family, before anything is rescored: `results/e8fa/` holds nothing at append
and this entry's script refuses otherwise. (Recomputed here from the raw token files: the Qwen draw under the same rule also holds
42 distinct windows in 50 rows — the repetition is a property of 0016's sampling rule on these suites, not of the Llama-3 BPE;
stated as an observation, it changes nothing registered.)

**What is registered.** A rescoring of {E8_FIGURES}'s OWN tensors — the {n_agent_dumps} fingerprinted agent dump files (source and target, per layer) at `results/e8f/kv/agent` and the token
file they were dumped from (`{tok.name}`, sha256 `{prior['tokens']['sha256'][:12]}`), both reused and required to match the
fingerprints in `results/e8f/report.json` (sha256 `{prior_sha[:12]}`) byte for byte; nothing is resampled or re-dumped; the generic
dumps are the archived ones. The protocol is {QWEN_AMEND}'s, unchanged, under `config/e8fa.toml` (sha256 `{config_sha[:12]}`): for each
k ∈ {{1, 4, 8}}, arm (a) on the mapper's own held-out generic sequences (`holdout_frac` 0.2, unchanged); arm (b) at `--holdout-frac 1.0`,
every one of the {n_rows} agent sequences ({n_rows * seq_len // cfg.stride:,} scored tokens at stride {cfg.stride}); the drop (a − b) and its 0009 band word
read descriptively; per-sequence R² for both arms from the per-token record (upstream `per_sequence_moments`, SST around the global
held-out mean, so a sequence's R² is its share of the pooled decomposition); a seeded percentile bootstrap over agent sequences
(seed {cfg.amendment['bootstrap_seed']} + k, {cfg.amendment['bootstrap_reps']:,} reps) of arm (b)'s pooled R² and of the drop; and the change from {E8_FIGURES}'s arm (b) at
the same k, named as such. Because {max_mult} rows are one window, the bootstrap resamples rows, not distinct windows, and the entry that
states the figures must say so beside them.

**What this does NOT touch.** τ_K = {tau_K:.4f}, τ_V and τ_agent_K = {tau_agent_K:.4f} stay as {E8_FIGURES} stated them and as `config/e9f.toml`
and `config/e9fl.toml` carry them; the all-sequence counterpart is reported beside τ_agent_K, never substituted (0044 has already read
it). `results/e8f/` is not rewritten — the family's E9 calibration reads it — and this amendment writes only under `results/e8fa/`.
H-E8 is entry 0020's, on the Qwen pair, and is untouched; {E8_FIGURES}'s band reading is itself descriptive and does not move.

**Instrument and enforcement.** No code change: `config/e8fa.toml` names this entry in `[e8.amendment]`, reuses {E8_FIGURES}'s report,
and pins the family's upstream commit `{cfg.upstream_sha[:7]}`, which already contains {QWEN_AMEND}'s upstream change (`223f469` is its
ancestor; `--holdout-frac 1.0` and the per-sequence block are in `scripts/score_mapper.py` at the pin). The driver's gate for this
config is 0009 + 0016 + {FAMILY} + this entry (`e8.required_entries`); `e8.reuse_agent_dumps` checks every fingerprint before scoring;
`summarize_e8` recomputes the per-sequence figures from the record and refuses on disagreement with the report, with the re-scored
json, or with a changed prior report. The script that appended this entry asserted every one of these against the tree.

**Scope.** All of 0009's, 0016's, {FAMILY}'s and {E8_FIGURES}'s limits: one pair, one direction, one mapper, off-policy text for Llama-3,
visible messages only (0012). No hypothesis cell changes with this entry; no `verdict:` line. The figures enter by their own numbered
entry from a passing `summarize_e8 --config config/e8fa.toml`, run after the ordinary `e8 --config config/e8fa.toml` (CPU).

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print(f"[ordering guard: {'ok' if ordering_ok else f'NOT satisfied — {PREV} absent or {NUM} present; renumber before appending'}]")
    print(f"[config/e8fa.toml committed unmodified: {'yes' if config_committed else 'NO — commit it before appending'}]")
    raise SystemExit(0)
assert config_committed, "config/e8fa.toml must be tracked and unmodified before the entry that names it is appended"
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
