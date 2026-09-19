"""Append entry 0043 -- a PRE-PREFILL AMENDMENT to the E9 short cell of the second model family (0042).

DESCRIPTIVE: no hypothesis row, no `verdict:` line, no cell moves, no figure. It registers two things
BEFORE any prefill, following the 0025/0026/0027 precedent:

  (a) the driver's checkpoint write is now ATOMIC (temp file, fsync, rename). Entry 0042 recorded that
      the driver "gained refusals only"; this changed it again, after that entry and before any run.
      Nothing computed changes -- the bytes written are identical -- but it is the registered
      instrument, so it is stated rather than left to a commit message.

  (b) THE STOP PROTOCOL, which is the reason (a) was needed and the thing that must not be chosen after
      seeing scores: when the driver is stopped, how, and which prefix a stopped run closes on.

Ordering guard: 0042 on the ledger, 0043 absent, and R1 -- NOTHING of this cell may exist yet. No
`results/e9f/report.json`, no score file, no token record, no kept dump. The alignments and the
calibration may exist (0042 required them at registration) and are checked to be the committed ones.

Every claim about the instrument is ASSERTED AGAINST THE SOURCE, not typed: the entry cannot describe
an atomic write, a drain, or a home-side partial close that the tooling does not implement.

  --date <YYYY-MM-DD>   (defaults to today; the entry is dated the day it is appended)
  --preview             (print, do not append)

Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import ast
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.hashing import sha256_text_file
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models

NUM, PREV = "0043", "0042"
FAMILY = "0039"      # the family registration entry, APPENDED 2026-09-18 -- a fixed number now
SHORT = "0042"       # this cell's registration entry, the one being amended; APPENDED, fixed

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"

cfg = load_e9_config(REPO_ROOT / "config" / "e9f.toml", REPO_ROOT)
src_id, tgt_id = pair_models(cfg.pair)
assert cfg.allow_partial and cfg.order_by == "n_sender_asc", \
    f"{SHORT} registered by = n_sender_asc with allow_partial; the config no longer says so"
# This amendment is enforced, not merely stated: the gate must require it, for the same reason
# config/e9.toml's gate requires 0026 and 0027. A protocol that decides which prefix a stopped run
# closes on cannot be registered after the driver has run under it.
assert NUM in cfg.required_entries, \
    f"config/e9f.toml's [e9.gate] does not require {NUM}; this amendment would not bind the driver"
assert list(cfg.required_entries) == ["0019", "0023", "0025", "0027", SHORT, NUM], \
    f"the gate list is not {SHORT}'s extended by exactly this entry: {list(cfg.required_entries)}"

# ---- R1: this is PRE-prefill, and that is checked, not asserted in prose -------------------------
res = cfg.results_dir
assert not (res / "report.json").exists(), "results/e9f/report.json exists; this is no longer pre-prefill"
for sub in ("scores", "tokens", "controls", "scratch", "checkpoints"):
    d = res / sub
    assert not (d.exists() and any(d.iterdir())), f"{d} is not empty; this is no longer pre-prefill"
cov = res / "align" / "coverage.json"
assert cov.is_file(), f"{cov} is missing; {SHORT} registered the run order from it"
# The count below is READ from the registered coverage, never typed: a hand-written 28 in a ledger
# entry is a number no summarizer recomputed, which this repo does not permit anywhere.
coverage = json.loads(cov.read_text(encoding="utf-8"))
N_REG = len(coverage["run_order"])
assert N_REG == coverage["coverage"]["included"] and N_REG > 0, \
    "coverage.json's run_order and coverage.included disagree"
assert coverage["config_sha256"] == sha256_text_file(REPO_ROOT / "config" / "e9f.toml"), \
    "the coverage file was written under another config"
assert coverage["order_by"] == cfg.order_by, "coverage.json was written under another run order"

# ---- the amendment must describe the tooling that exists ---------------------------------------
E9_SRC = (REPO_ROOT / "src" / "linear_ceiling" / "e9.py").read_text(encoding="utf-8")
PULL_SRC = (REPO_ROOT / "tools" / "runpod" / "pull_verify_b.py").read_text(encoding="utf-8")
RP_SRC = (REPO_ROOT / "tools" / "runpod" / "rp.py").read_text(encoding="utf-8")

tree = ast.parse(E9_SRC)
fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_write_checkpoint"), None)
assert fn is not None, "e9.py has no _write_checkpoint; (a) would describe a function that does not exist"
body = ast.get_source_segment(E9_SRC, fn) or ""
for needed in (".tmp", "fsync", "os.replace"):
    assert needed in body, f"_write_checkpoint does not {needed}; the write this entry registers is not atomic"
assert "_write_checkpoint(out, rep)" in E9_SRC, "close_partial does not use the atomic write"

for name in ("choose_partial_basis", "require_driver_stopped", "final_partial", "write_drain_hint"):
    assert f"def {name}(" in PULL_SRC, f"pull_verify_b.py has no {name}; the stop protocol is not implemented"
assert '"--final-partial"' in PULL_SRC, "pull_verify_b.py exposes no --final-partial"
for name in ("drain_threshold", "send_drain_signal", "read_drain_hint"):
    assert f"def {name}(" in RP_SRC, f"rp.py has no {name}; the drain this entry registers does not exist"
m = re.search(r"^DRAIN_FALLBACK_FRACTION = ([0-9.]+)$", RP_SRC, re.M)
assert m, "rp.py does not define DRAIN_FALLBACK_FRACTION"
FALLBACK = float(m.group(1))
assert "kill -TERM" in RP_SRC, "the drain does not signal; it would have to terminate, which loses the handoff"

CFG_SHA = sha256_text_file(REPO_ROOT / "config" / "e9f.toml")
COV_SHA = sha256_text_file(cov)

ENTRY = f"""### {NUM} — {a.date} — Pre-prefill amendment to {SHORT}: the driver's checkpoint write is atomic, and the stop protocol for a budget-limited sitting is registered; descriptive, no cell moves

**What this is.** An amendment to entry {SHORT}, appended **before any prefill of this cell**, on the
0025/0026/0027 precedent: the registered instrument changed after its registering entry, and a change to
the instrument is stated before the run, never explained after it. Nothing here moves a cell, states a
figure, or touches τ, the rule, the band, the ladder, the cap, the keep draw or the run order. Pair
{cfg.pair} ({src_id} → {tgt_id}), `config/e9f.toml` sha256 `{CFG_SHA[:12]}`, run order and coverage from
`results/e9f/align/coverage.json` sha256 `{COV_SHA[:12]}`, both committed and unmodified. At the moment of
writing, `results/e9f/` holds no report, no score file, no token record and no kept dump.

**(a) The checkpoint write is atomic.** Entry {SHORT} recorded that the driver "gained refusals only".
That is no longer the whole of it: `e9._write_checkpoint` now writes `report.json` to a temporary file,
`fsync`s it, and `os.replace`s it into place, and `e9.close_partial` writes through the same function.
**Nothing computed changes** — the same bytes are produced from the same inputs, and no number, refusal
or control is affected. The reason it changed is (b): the registered stop stops the driver **by signal**,
and a signal that lands during a plain `write_text` leaves a truncated `report.json`. Under the rule
below the closing basis is a checkpoint, so a torn checkpoint does not cost one handoff — it costs the
prefix. The change is recorded here because it is the registered instrument, not because it is large.

**(b) The stop protocol.** This cell runs under a hard dollar ceiling, so how it stops decides which
prefix entry {SHORT} closes on — and that must be fixed before any score exists, exactly as {SHORT}
fixed the order for the same reason.

1. **A healthy run closes on all {N_REG} included handoffs.** A partial is a registered outcome, never
   the preferred one and never a rescue.
2. **Drain before the ceiling.** The home watchdog stops the **driver** before the spend ceiling
   terminates the **pod**, by `SIGTERM` to the driver's recorded pid (never a self-matching pattern —
   protocol R4). The pod stays up so the home puller can finish the tensors already written. The ceiling
   remains unchanged behind this, as the backstop.
3. **When.** At `{FALLBACK:.0%}` of the sitting ceiling by default, or **earlier** if the puller's own
   measurement — bytes still outstanding ÷ the rate it is actually achieving — says the remaining pull
   needs more than the leftover budget. A measurement may only move the drain earlier, never later: the
   outstanding figure counts the kept dumps a checkpoint already names and cannot see the handoff in
   flight, so an uncapped measurement reads "nothing outstanding" at the moment the most is at risk.
4. **The closing basis after ANY abnormal end** — drained, hard-killed, crashed, or a pod lost outright
   — is the **last checkpoint whose every named artifact is sha-verified at home**: the small records and
   the kept directories of the scored prefix, each byte-for-byte against that checkpoint's own
   fingerprints. It is a genuine driver checkpoint and a prefix of the registered `{cfg.order_by}` order.
   **It is never an edited report.** If no checkpoint verifies whole at home, there is no close, and
   H-E9F stays `unresolved` — that is the finding, not a problem to be worked around.
5. **Where.** The close happens **at home, on the verified mirror**, never on the box: box storage is
   ephemeral, so after a hard kill it is already gone at exactly the moment a close is needed.
   `tools/runpod/pull_verify_b.py --final-partial` refuses unless the driver is provably stopped, proves
   the basis, and writes the termination receipt; `e9 --close-partial --config config/e9f.toml` then
   stamps it and needs nothing but `report.json`.
6. **What the closing entry must carry.** The cutoff reason, the coverage as "n scored of N registered"
   beside every number, and every unscored handoff named by id — as entry 0036 did for the long half.

**(c) The gate, and one regenerated artifact.** `config/e9f.toml`'s `[e9.gate]` now requires
`{'/'.join(cfg.required_entries)}` — entry {SHORT}'s list extended by this entry and nothing else — so
`e9 --check` refuses until this amendment is committed on the ledger. Enforcement, not decoration: a
protocol deciding which prefix a stopped run closes on must bind the driver, and {SHORT} recorded the
gate as it stood then. Adding one entry changed the file's sha256 to `{CFG_SHA[:12]}`, and
`results/e9f/align/coverage.json` and `results/e9f/calibration/tau.json` are recorded under that sha, so
both were regenerated by `e9 --align-only` and `summarize_e9 --calibrate-tau`. **The coverage file
differs in exactly one key, `config_sha256`**: the {N_REG} included handoffs, the `{cfg.order_by}` run
order, the keep draw, the exclusion counts and every alignment are identical, and τ_K, τ_V and τ_agent_K
are unchanged to every digit. No registered quantity moved; the file now records the sha of the file that
actually governs it. No other config is touched.

**Why this is an amendment and not a note.** Under {SHORT} the scored set of a stopped run is a prefix of
a registered order, which fixes *which* handoffs a partial keeps. It did not fix *when* the run stops or
*which* checkpoint is then closed on, and both are choices that could otherwise be made with the scores
already visible. Registering them here removes that freedom before there is anything to see.

**What this does NOT touch.** The H-E8, H-E9, H-E9L and H-E9F cells and every verdict; τ_K, τ_V,
τ_agent_K, the rule, the band edges, the ladder, `prefix_invariance_max_delta`, the cap, the seeds, the
keep draw, the run order, the coverage figures themselves; every other cell's config and results. Entry {FAMILY}'s τ_K ceiling of 0.45 and entry
0041's report-only ordering both stand as written.

**Scope.** One pair ({src_id} → {tgt_id}), one cell, one sitting's stopping behaviour. Nothing here is
evidence about KV reuse, and nothing here may be cited as a finding.

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
