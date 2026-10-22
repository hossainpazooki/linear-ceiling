"""Append entry 0063 -- REGISTER, before any operator prefill, the TASK-QUALITY cell (ruling C of the 2026-10-13
plan): structured-field recall of method signature lines, asked after the receiver prompt R and answered by greedy
decoding, under the receiver's own cache (FRESH) and under the assembled caches of entry 0047 / entry 0061 (REUSE-ALL,
RANDOM, REPAIR-f at f in {0.05, 0.10, 0.20}), on the handoffs of entry 0036 (long) and entry 0038's cell (short) whose
sender holds structured code-search results. The C2 pilot gate (three handoffs, fresh arm, CPU) is recorded by hash.
DESCRIPTIVE: no hypothesis row, no `verdict:` line, no band, no cell moves. The standing sentence "no downstream
task-quality number is claimed" is NOT retired by this entry; the figures entry reads what this entry registers.

Ordering guard: 0062 present, 0063 absent. Refuses unless the config, the driver, the reader and the tests are in the
tree at the hashes below (text files hashed newline-normalized, as the ledger cites configs), the two items files and the
two pilot reports are present at their pinned hashes, both pilot summaries re-derive in-process from their reports, and
nothing exists under the registered output trees (R1).

  --date YYYY-MM-DD   --preview   --repo-root <path>
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import json
import re
import statistics
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))
from linear_ceiling.hashing import sha256_text_file                    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM, PREV = "0063", "0062"
LONG, SHORT, BEH, BEH_RUN, REPAIR = "0036", "0038", "0047", "0049", "0061"
CONFIG_SHA = "cce4326c0ed0c139ac702179d5eefa195de866ccefc47e5f91bf18247d3e5d80"   # config/task-quality-cell.toml
PILOT_CONFIG_SHA = "ea4e2abb01aa5c5ff2109f3a2337f2085af3c5fc576de115b8e17a31445d326b"   # config/task-quality-pilot.toml, the items' and the gate's configuration
ITEMS_SHA = "f5360038cef454361294a074768fbed549ffbed1aa042163e3ff2066924c8d2e"   # tools/task_quality/items.py: extraction, location in R, the scorers
PILOT_SHA = "009ff9f04601e3c07a0bf779f0c16bc847b3c03409df8ce13d6e44a3576534e8"   # tools/task_quality/pilot.py: extraction driver, the gate, the draw
CELL_SHA = "412b88a3d001c6cc5773671bc1b3438030b960e53509a496e23c9ef74a3670e5"    # tools/task_quality/cell.py: the cell driver and its reader
CORE_SHA = "f346b5fdf3d3feff5918e3a0e95f1e084f154317213ba68ce1913ec5acdcade5"   # tools/cache_behavior/core.py, as 0047 / 0061 pin it
TESTS_SHA = {"tests/test_task_quality.py": "9600fab36c643b4eafa14f1660a88a5b91b035fa31a3db10fb2b5714934c8ecf",
             "tests/test_task_quality_cell.py": "374282b8453cf97a32823daa9058c5ef02e8f6cea07a121923b6ece09d901dce"}
ITEMS_FILES_SHA = {"long": "8153e9d30d04b9c7cebe7bf44a661eab4df56a170635204f52ce8da660ce9239",     # results/task-quality/items-e9l.json
                   "short": "96499cb24cb88f4c233245bd2793b73728105124e3f25c6ac9862f33a0cb958a"}    # results/task-quality/items-e9.json
PILOT_REPORTS_SHA = {"pilot": "6e194dc79a58b80af52e898a996f2df52db49e5b10c8635243e15db8bae0f14f",           # run 2, results/task-quality/pilot/report.json
                     "pilot-widened": "e069f14326d85ef0b0ca8ade775a311f521dfa8c9373c3d2fada37989f2a42ec"}   # run 3, results/task-quality/pilot-widened/report.json
SUPERSEDED_REPORT_SHA = "6b85322681cbc26bb1c95002bf98e34c1025faf254a1d06a79d104f06b934971"   # run 1, results/task-quality/pilot-newline-stop-partial/report.json (two handoffs, newline stop)
OUTPUT = "results/task-quality-cell"

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
R = a.repo_root.resolve()
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {NUM} " not in text, f"ordering: {NUM} absent"
missing = [e for e in (PREV, REPAIR, LONG, SHORT, BEH, BEH_RUN) if f"### {e} " not in text]
if missing and a.preview:
    print(f"[preview] not yet on this ledger: {missing}; the append refuses until they are", file=sys.stderr)
else:
    assert not missing, f"ordering: {missing} must be on the ledger before {NUM}"

pins = {"config/task-quality-cell.toml": CONFIG_SHA, "config/task-quality-pilot.toml": PILOT_CONFIG_SHA,
        "tools/task_quality/items.py": ITEMS_SHA, "tools/task_quality/pilot.py": PILOT_SHA,
        "tools/task_quality/cell.py": CELL_SHA, "tools/cache_behavior/core.py": CORE_SHA, **TESTS_SHA}
for rel, sha in pins.items():
    assert (R / rel).exists(), f"{rel} missing"
    assert sha256_text_file(R / rel) == sha, f"{rel} is not the file this entry pins"
cfg = tomllib.loads((R / "config/task-quality-cell.toml").read_text(encoding="utf-8"))
pilot_cfg = tomllib.loads((R / "config/task-quality-pilot.toml").read_text(encoding="utf-8"))
for key in ("model", "revision", "context_cap", "chunk_tokens", "rope", "questions", "prompts", "max_new_tokens",
            "stop_at_newline", "min_form2_items", "max_items_per_handoff"):
    assert cfg[key] == pilot_cfg[key], f"{key} differs between the cell and the pilot configuration"
assert cfg["repair_fractions"] == [0.05, 0.10, 0.20], "the repair budgets are 0061's"
assert cfg["headline"] == {"form": "chat", "scorer": "first_span_exact", "kinds": ["signature"]}
assert cfg["forms"] == ["chat", "plain"]
beh = tomllib.loads((R / "config/cache-behavior.toml").read_text(encoding="utf-8"))
assert cfg["model"] == beh["model"] and cfg["revision"] == beh["revision"] and cfg["rope"] == beh["rope"]
assert cfg["context_cap"] == beh["context_cap"] == 81920 and cfg["chunk_tokens"] == beh["chunk_tokens"]

from tools.task_quality import pilot as pilot_module   # noqa: E402  (the pinned reader, imported after the pin check)

# The items files and the archive they index: present at their hashes, counts READ from them, never typed.
items = {}
for cell, rel in (("long", "results/task-quality/items-e9l.json"), ("short", "results/task-quality/items-e9.json")):
    path = R / rel
    assert path.exists(), f"{rel} missing: produce it with `tools.task_quality.pilot --items` from the verified {cell} mirror"
    assert sha256_text_file(path) == ITEMS_FILES_SHA[cell], f"{rel} is not the items file this entry pins"
    assert cfg["cells"][cell]["items_file"] == rel and cfg["cells"][cell]["items_sha256"] == ITEMS_FILES_SHA[cell]
    body = json.loads(path.read_text(encoding="utf-8"))
    assert body["config_sha256"] == PILOT_CONFIG_SHA, "items extracted under another configuration"
    counts = [pilot_module.form2_count(h) for h in body["handoffs"]]
    sig = sum(h["counts"]["valid_by_kind"].get("signature", 0) for h in body["handoffs"])
    fil = sum(h["counts"]["valid_by_kind"].get("file", 0) for h in body["handoffs"])
    rep = sum(h["counts"]["valid_by_kind"].get("repository", 0) for h in body["handoffs"])
    kept = [h for h in body["handoffs"] if pilot_module.form2_count(h) >= cfg["min_form2_items"]]
    void = [h for h in body["handoffs"] if pilot_module.form2_count(h) < cfg["min_form2_items"]]
    items[cell] = {"n": len(body["handoffs"]), "kept": len(kept), "void": len(void), "zero": counts.count(0),
                   "signature": sig, "file": fil, "repository": rep, "median": statistics.median(counts),
                   "max": max(counts), "void_median_sender": statistics.median(h["n_sender"] for h in void) if void else None,
                   "kept_median_sender": statistics.median(h["n_sender"] for h in kept),
                   "coverage_sha12": body["coverage_sha256"][:12]}
assert items["long"]["n"] == 35 and items["short"]["n"] == 25, "the cells are 0036's 35 and 0038's 25 handoffs"

# The pilot gate record: reports at their hashes, summaries RE-DERIVED here by the pinned reader.
gate = {}
for run in PILOT_REPORTS_SHA:
    folder = R / "results/task-quality" / run
    assert (folder / "report.json").exists(), f"{folder.relative_to(R)}/report.json missing: the pilot record is required"
    assert sha256_text_file(folder / "report.json") == PILOT_REPORTS_SHA[run], f"{run}/report.json is not the pinned pilot report"
    summary = pilot_module.summarize(folder)
    assert summary["complete"] and summary["handoffs"] == 3
    gate[run] = {form: {"first_span": [round(h["first_span_exact"], 3) for h in summary["forms"][form]["per_handoff"]],
                        "median": summary["forms"][form]["median_first_span_exact"],
                        "sig": summary["forms"][form]["by_kind"]["signature"]["first_span_exact"],
                        "n_sig": summary["forms"][form]["by_kind"]["signature"]["n"]}
                 for form in ("plain", "chat")}
# Run 3 scored the pinned extraction: its items copy equals the pinned long items file, item for item.
_copy = json.loads((R / "results/task-quality/pilot-widened/items-e9l.json").read_text(encoding="utf-8"))
_pinned = json.loads((R / "results/task-quality/items-e9l.json").read_text(encoding="utf-8"))
assert _copy["handoffs"] == _pinned["handoffs"] and _copy["coverage_sha256"] == _pinned["coverage_sha256"], "run 3 scored other items"
superseded = R / "results/task-quality/pilot-newline-stop-partial/report.json"
assert not superseded.exists() or sha256_text_file(superseded) == SUPERSEDED_REPORT_SHA, "run 1's report is not the superseded one"

# R1: nothing under this entry's output trees exists yet.
for cell in ("long", "short"):
    out = R / OUTPUT / cell
    assert not (out / "report.json").exists() and not (out / "summary.json").exists(), f"{out} holds a run; refusing"

s12 = lambda s: s[:12]  # noqa: E731
L, S = items["long"], items["short"]
g2, g3 = gate["pilot"], gate["pilot-widened"]
fmt3 = lambda xs: " / ".join(f"{x:.3f}" for x in xs)  # noqa: E731
ENTRY = f"""### {NUM} — {a.date} — Task-quality cell registered before any operator prefill: structured-field recall of signature lines under FRESH, REUSE-ALL, RANDOM and REPAIR-f caches on the handoffs whose sender holds structured code-search results, long and short cells; the C2 pilot gate recorded; descriptive, no band, no cell moves

**Why, and why now.** Every registered statistic so far is a deviation, a KL or a flip on fixed text; entry {BEH_RUN}'s
sentence "no downstream task-quality number is claimed" stands. Reviewers asked what a reused cache does to a task. The
2026-10-13 plan (private; ruling C) chose structured-field recall from the trace itself as the ground truth: fields the
sender's tool results render verbatim and the receiver prompt R re-renders, so the answer's tokens lie inside the matched
set M and a question about them is a question about the reused states. This entry registers that cell, after a CPU pilot
read its power. It is CONTEXT for the registered statistics, not a verdict on them: a task number beside the KL.

**What is registered, by hash (text files newline-normalized, as the ledger cites configs).** `config/task-quality-cell.toml`
(`{s12(CONFIG_SHA)}…`): receiver `{cfg['model']}@{s12(cfg['revision'])}`, fp32, SDPA, the long cell's YaRN schedule
(factor {cfg['rope']['factor']}, original {cfg['rope']['original_max_position_embeddings']:,}), cap {cfg['context_cap']:,}, {cfg['chunk_tokens']}-token prefill chunks — entry {BEH}'s receiver,
unchanged; seed {cfg['seed']}; item floor {cfg['min_form2_items']}; at most {cfg['max_items_per_handoff']} form-2' items per handoff drawn by seed, the
repository item always; greedy decoding to end-of-text or {cfg['max_new_tokens']} tokens, no newline stop; two prompt forms (chat: the
question in the receiver's chat template with an empty think block; plain: "Question: … Answer:"); repair budgets
{cfg['repair_fractions']} (entry {REPAIR}'s). Code: `tools/task_quality/items.py` `{s12(ITEMS_SHA)}…` (extraction, location in R,
the scorers), `pilot.py` `{s12(PILOT_SHA)}…` (the items driver, the gate, the draw), `cell.py` `{s12(CELL_SHA)}…` (the cell driver
and its fail-closed reader), over `tools/cache_behavior/core.py` `{s12(CORE_SHA)}…` (byte-identical to {BEH}'s and {REPAIR}'s
cache construction); tests `tests/test_task_quality.py` and `tests/test_task_quality_cell.py` (synthetic archive, real
tiny-model CPU forwards). Inputs: the items files `results/task-quality/items-e9l.json` `{s12(ITEMS_FILES_SHA['long'])}…` and
`items-e9.json` `{s12(ITEMS_FILES_SHA['short'])}…`, extracted under `config/task-quality-pilot.toml` `{s12(PILOT_CONFIG_SHA)}…` from the
verified E9 mirrors (coverage `{L['coverage_sha12']}…` and `{S['coverage_sha12']}…`, raw bytes as the mirrors are verified), each handoff's
trace and alignment file pinned inside them; the archives' alignment pairs as M, per-token record and score files, each checked against the hash the items file
or the archive report pins. No new alignment, no new trace.

**Items (form 2' of the plan).** From each sender's rendered code-search blocks: the signature line of a method listed as
a member of a class (key `Class.method`, answer the `def …:` line as rendered), the file where a class is defined, and
the cloned repository. One item per key; a key rendered with two answers is dropped as ambiguous. An item is valid iff
the anchor's first occurrence lies in R and every token of the answer is in M (the archived pairs), decided by the
receiver tokenizer's offsets against the archived receiver ids. The question is appended after the whole R, so the
answer's tokens are the reused states under every arm. Long cell: {L['signature']:,} valid signature items, {L['file']} file items and
{L['repository']} repository items over {L['n']} handoffs; form-2' items per handoff median {L['median']:g}, max {L['max']}. Short cell: {S['signature']:,} / {S['file']} / {S['repository']} over
{S['n']}; median {S['median']:g}, max {S['max']}.

**The population, stated.** The floor voids {L['void']} of {L['n']} long handoffs ({L['zero']} hold no item at all) and {S['void']} of {S['n']} short ones ({S['zero']} with none); the
cell runs {L['kept']} long and {S['kept']} short handoffs. Voiding is by tool usage, not length: the voided long senders' median is
{L['void_median_sender']:,.1f} tokens against {L['kept_median_sender']:,.1f} for the kept. The cell is "handoffs whose sender holds structured code-search results"; the
void handoffs are listed in the report and no accuracy is imputed to them.

**Arms.** FRESH: the receiver's own prefill of R. REUSE-ALL, RANDOM and REPAIR-f exactly as entries {BEH} and {REPAIR}
construct them (the same `core.py`): the sender's matched states relocated to R; the norm-matched random perturbation of
the fresh states; the top-f matched tokens by archived token-mean δ_K recomputed in place against reused predecessors.
CYCLIC and the random-selection control are not run here. Under each cache every drawn item's question is appended
after R, decoded, and the cache returned to R before the next item; the continuation is not scored and no KL is read.

**Readout, fixed now (ruling C3).** Headline: under the CHAT form, per handoff, the fraction of signature items whose
FIRST def-span in the generation equals the rendered field after undoing the trace's JSON escaping and collapsing
whitespace, the trailing colon ignored (`items.first_span_exact`, pinned above; a preamble does not fail it, a hedge
list is read by its first entry). Over the handoffs: median with p10 / p90 by `e7_stats`, handoffs weighted equally, and a
percentile interval of the median from {cfg['bootstrap_resamples']:,} seeded resamples of handoffs. Retention per arm: raw (arm over FRESH per
handoff) and floor-normalized ((arm − RANDOM) / (FRESH − RANDOM) per handoff), the handoffs whose denominator is not
positive counted as void and listed by id in the summary. Beside it, descriptive: the same statistic under the PLAIN form
and under every scorer (whole-generation exact match, containment, token F1, canonical containment), on signature items
and on form-2' items (signature plus file); file and repository items reported by kind only — they scored 3 of 3 under
both forms in the pilot and are treated as guessable without context, so they are out of the headline. **No band is
registered**; the first run is descriptive and a later entry may register one.

**The pilot gate, recorded (ruling C2).** Three handoffs (shortest, middle, longest sender above the floor), FRESH only,
both forms, on this receiver on CPU; the gate [0.2, 0.9] read as context. Run 2 (`results/task-quality/pilot/report.json`
`{s12(PILOT_REPORTS_SHA['pilot'])}…`, the narrower extraction) and run 3 (`pilot-widened/report.json` `{s12(PILOT_REPORTS_SHA['pilot-widened'])}…`, the pinned
extraction), re-read here by the pinned reader: chat first-span per handoff {fmt3(g2['chat']['first_span'])} (median {g2['chat']['median']:.3f}) and
{fmt3(g3['chat']['first_span'])} (median {g3['chat']['median']:.3f}); plain {fmt3(g2['plain']['first_span'])} (median {g2['plain']['median']:.3f}) and {fmt3(g3['plain']['first_span'])} (median
{g3['plain']['median']:.3f}); pooled signature first-span chat {g2['chat']['sig']:.3f} (n = {g2['chat']['n_sig']}) and {g3['chat']['sig']:.3f} (n = {g3['chat']['n_sig']}). Run 1 (two handoffs, a
newline stop) is superseded and kept at `{s12(SUPERSEDED_REPORT_SHA)}…`. Both chat medians exceed the gate's ceiling of 0.9, as do two
of the three handoffs in each run; the ceiling was a proxy for context-independence, and most of the pilot's chat misses
are retrieval confusions between same-named methods of different classes in S (the rest alter a parameter list), not
answers from no context, so the chat form is registered and the gate reading is reported as it is. The plain form
continued the trace's own rendering to the token cap on every item and is kept as a sensitivity row, not the instrument.

**The registered run (the operator's).** Requested only after this entry is committed: `tools.task_quality.cell --run`
per cell, the largest sender first as the memory probe (R2), `--resume` verifying the identity; output `{OUTPUT}/long/`
and `{OUTPUT}/short/` (`report.json`, `summary.json`), mirrored home and verified before the figures entry. Card: 80 GB.
Cost is ASSUMED until the probe times it: per handoff one sender prefill, one FRESH prefill and five cache constructions,
then up to 41 items × 2 forms × 6 arms short decodes.

**Gate and enforcement.** The driver refuses an items file, alignment, score or per-token file whose hash differs from
its pin, records the config, items and source hashes, runtime and device in `report.json`, and re-reads every score from
the stored prediction after each handoff. This script refuses if any pinned file differs, if the cell and pilot
configurations disagree on the receiver or the items rule, if either pilot summary fails to re-derive, or if `{OUTPUT}`
holds a run. The figures enter by their own entry, which calls `tools.task_quality.cell.summarize` in-process over the
operator's verified output, asserts the report's hashes equal the hashes above, and refuses on any disagreement; no
figure is typed.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, {LONG}, {SHORT}, 0044, 0045, {BEH},
{BEH_RUN}, 0058, {REPAIR}, {PREV} and their records; `config/cache-behavior*.toml` and their output trees; `config/e9*.toml`; the
E9 drivers and summarizers; the standing sentence of {BEH_RUN}.

**Scope.** One receiver, two repositories' traces, fixed proprietary-model text, same-model reuse only; one item kind in
the headline; accuracy of a 1.7B receiver on a recall question, not the agent's task success; the question sits after
the whole R, so a seam-local reading needs a later entry; no public benchmark (a composition of LongBench items into a
standalone handoff is piloted separately and enters by its own entry, if at all).

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
