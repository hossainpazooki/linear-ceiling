"""DRAFT append script for linear-ceiling: REGISTER, before any dump, E8 on the MLPerf Agentic Inference text on both
pairs (config/e8m.toml, Qwen3 0.6B -> 1.7B; config/e8mf.toml, Llama-3.2-3B -> Llama-3.1-8B): the 0016 §4 sampling rule
over two new suites out of the MLCommons dataset, reasoning kept, the shared system prefix not rendered. DESCRIPTIVE: no
hypothesis row, no `verdict:` line, no cell moves; the band is reported as 0009 writes it and decides nothing.

Staged 2026-10-26 as docs/drafts/append_0064.py (number from docs/drafts/README.md; [e8.gate] and [e8.amendment] in both
configs name it in the same commit). Run from the repo root with .venv/Scripts/python.exe:
  --date YYYY-MM-DD   --preview   --repo-root <path>
Ordering guard: PREV present, NUM absent. Refuses unless both configs are tracked and unmodified and name NUM in their gate,
the adapter and tests are the committed files (hashes recorded in the entry at append, newline-normalized), the dataset,
the rendered export and both token manifests are present and re-derive (50 distinct windows, 25 + 25, the dataset's sha
equal to its README's), the family pin contains 0030's upstream commit, and nothing exists under results/e8m or
results/e8mf (R1). Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=Path.home() / "dev" / "linear-ceiling")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
R = a.repo_root.resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_text_file                    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM, PREV = "0064", "0063"          # allocated by docs/drafts/README.md (staged 2026-10-26); 0061-0063 land first
RULE, FAMILY, FAMILY_RUN, QWEN_RUN, QWEN_AMEND, LLAMA_AMEND = "0016", "0039", "0040", "0020", "0030", "0053"
DATASET_SHA = "1beb24c882122df96571cf11b390acbea388944038bc55c78b891475459014ae"   # the README's, checked on download
UPSTREAM_0030 = "223f469"            # 0030's upstream commit, which the family pin must contain
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {NUM} " not in text, f"ordering: {NUM} absent"
missing = [e for e in ("0061", "0062", PREV, RULE, FAMILY, FAMILY_RUN, QWEN_RUN, QWEN_AMEND, LLAMA_AMEND) if f"### {e} " not in text]
if missing and a.preview:
    print(f"[preview] not yet on this ledger: {missing}; the append refuses until they are", file=sys.stderr)
else:
    assert not missing, f"ordering: {missing} must be on the ledger before {NUM}"
# the figures this entry reads beside, quoted from the ledger and asserted present rather than typed
QWEN_ROW = "| 1 (verdict-bearing) | 0.6814 / 0.5133 | 0.5629 / 0.3418 | +0.1185 / +0.1715 | UNRESOLVED / DEGRADES |"
LLAMA_ROW = "| 1 (verdict-bearing, K and V separately) | 0.7139 / 0.4711 | 0.7311 / 0.4599 | -0.0172 / +0.0111 | HOLDS / HOLDS |"
assert QWEN_ROW in text and LLAMA_ROW in text, "the k = 1 rows of 0020 and 0040 are not on this ledger as quoted"
assert "only **42 distinct windows**" in text, "0040's repeated-window disclosure is not on this ledger as quoted"


def tracked_unmodified(rel: str) -> None:
    t = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=R, capture_output=True)
    c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=R)
    if not (t.returncode == 0 and c.returncode == 0):
        assert a.preview, f"{rel} is not committed as-is"
        print(f"[preview] {rel} is not committed as-is; the append refuses until it is", file=sys.stderr)


PINNED = ("config/e8m.toml", "config/e8mf.toml", "src/linear_ceiling/e8_text.py", "src/linear_ceiling/e8.py",
          "tests/test_e8_text.py", "tests/test_e8m_configs.py")
for rel in PINNED:
    assert (R / rel).exists(), f"{rel} missing"
    tracked_unmodified(rel)
H = {rel: sha256_text_file(R / rel) for rel in PINNED}
_t = (R / "tests/test_e8m_configs.py").read_text(encoding="utf-8")
if f'"### {NUM} " not in' in _t:
    assert a.preview, f"tests/test_e8m_configs.py still asserts {NUM} is absent from the ledger; the staging commit flips it"
    print(f"[preview] tests/test_e8m_configs.py still asserts {NUM} absent; the staging commit flips it (hashes then change)", file=sys.stderr)
e8m = tomllib.loads((R / "config/e8m.toml").read_text(encoding="utf-8"))["e8"]
e8mf = tomllib.loads((R / "config/e8mf.toml").read_text(encoding="utf-8"))["e8"]
e8f = tomllib.loads((R / "config/e8f.toml").read_text(encoding="utf-8"))["e8"]
assert e8m["gate"]["required_entries"] == [NUM] and e8mf["gate"]["required_entries"] == [FAMILY, NUM], "[e8.gate] must name this entry"
assert e8m["upstream_sha"] == e8mf["upstream_sha"] == e8f["upstream_sha"], "one family pin for both MLPerf cells"
PIN = e8m["upstream_sha"]
for c in (e8m, e8mf):
    assert c["text"] == {"seed": 8, "n_seqs": 50, "seq_len": 1024, "suites": ["mlperf-coding", "mlperf-workflow"], "window": "first"}
    assert c["mappers"] == {"verdict_k": 1, "report_k": [1, 4, 8]} and c["band"] == {"holds_max_drop": 0.05, "degrades_min_drop": 0.15}
    assert c["arms"]["holdout_frac"] == 0.2 and c["arms"]["stride"] == 4
assert e8m["pair"] == "qwen3-0.6b-to-1.7b" and e8mf["pair"] == "llama3.2-3b-to-llama3.1-8b"
assert e8m["results_dir"] == "results/e8m" and e8mf["results_dir"] == "results/e8mf"
for c in (e8m, e8mf):      # ruled 2026-10-22: arm (b) over every sequence, 0030's readout, on this cell's own dumps
    assert c["arms"].get("agent_holdout_frac") == 1.0 and "reuse_agent_dumps_from" not in c["arms"]
    assert c["amendment"] == {"entry": NUM, "bootstrap_seed": int(NUM), "bootstrap_reps": 2000}
protocol_all = True
for d in ("results/e8m", "results/e8mf"):
    assert not any((R / d).rglob("*")) if (R / d).exists() else True, f"R1: {d} holds something"

up = (R / e8m["upstream_path"]).resolve()
if up.exists():
    anc = subprocess.run(["git", "-C", str(up), "merge-base", "--is-ancestor", UPSTREAM_0030, PIN]).returncode
    assert anc == 0, f"the family pin {PIN[:12]} does not contain {UPSTREAM_0030} (0030's upstream commit)"
else:
    assert a.preview, "upstream clone missing"
    print("[preview] upstream clone missing; the pin's ancestry is not checked", file=sys.stderr)

# the artefacts (all gitignored): the dataset, its notices, the rendered export and the two token manifests
TR = R / "traces" / "mlperf-agentic"
jsonl = TR / "mlperf_agentic_inference_dataset.jsonl"
facts: dict = {}
if jsonl.exists():
    assert hashlib.sha256(jsonl.read_bytes()).hexdigest() == DATASET_SHA, "dataset bytes are not the README's sha"
    facts["licenses"] = hashlib.sha256((TR / "LICENSES.txt").read_bytes()).hexdigest()
    facts["notice"] = hashlib.sha256((TR / "NOTICE").read_bytes()).hexdigest()
    n_rows, convs, with_source = 0, {}, set()
    with open(jsonl, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("_type") == "dataset_metadata":
                continue
            n_rows += 1
            convs.setdefault(r["conversation_id"], 0)
            convs[r["conversation_id"]] += 1
            if "_source" in r:
                with_source.add(r["conversation_id"])
    facts["rows"], facts["traj"] = n_rows, len(convs)
    facts["workflow"], facts["coding"] = len(with_source), len(convs) - len(with_source)
    assert (facts["coding"], facts["workflow"]) == (113, 500), facts
else:
    assert a.preview, "the dataset is not under traces/mlperf-agentic/"
    print("[preview] dataset absent; row and trajectory counts not recomputed", file=sys.stderr)
rend = R / e8m["tokens_dir"] / "rendered_mlperf.jsonl"
if rend.exists():
    facts["rendered"] = hashlib.sha256(rend.read_bytes()).hexdigest()
    suites = Counter(json.loads(l)["suite"] for l in open(rend, encoding="utf-8") if l.strip())
    assert suites == {"mlperf-coding": 113, "mlperf-workflow": 500}, suites
for key, c in (("e8m", e8m), ("e8mf", e8mf)):
    mp = R / c["tokens_dir"] / "agent_n50_len1024_seed8.manifest.json"
    tp = mp.with_suffix("").with_suffix(".npy")
    if not mp.exists():
        assert a.preview, f"{mp} missing"
        print(f"[preview] {mp.relative_to(R)} absent", file=sys.stderr)
        continue
    man = json.loads(mp.read_text(encoding="utf-8"))
    tok = np.load(tp)
    assert hashlib.sha256(tp.read_bytes()).hexdigest() == man["sha256"] and tok.shape == (50, 1024)
    assert len({r.tobytes() for r in tok}) == 50, f"{key}: the windows are not all distinct"
    assert Counter(r["suite"] for r in man["rows"]) == {"mlperf-coding": 25, "mlperf-workflow": 25}
    assert man["rule"] == "ledger entry 0016 section 4"
    facts[key] = {"npy": man["sha256"], "manifest": hashlib.sha256(mp.read_bytes()).hexdigest(),
                  "heldout": [r["traj_id"] for r in man["rows"][-10:]],
                  "heldout_suites": sorted(Counter(r["suite"] for r in man["rows"][-10:]).items())}


def h12(k):
    return (facts.get(k) or "UNVERIFIED")[:12]


PROTOCOL = ("0030's protocol, ruled 2026-10-22: arm (b) scored over EVERY agent sequence (`agent_holdout_frac = 1.0`; the "
            "mapper was never fit on them), per-sequence R² from the per-token records, seeded percentile bootstrap of the "
            f"drop (`[e8.amendment]`, seed {int(NUM)} + k, 2,000 reps), on this cell's OWN dumps — no `reuse_agent_dumps_from`, so "
            "the driver samples, dumps and scores in one run and the summarizer's 0030 readout applies to it. Why not 0016's "
            "hold-out: the token file is written suite by suite, so the LAST ceil(0.2 × 50) = 10 rows are all workflow windows "
            f"({dict((facts.get('e8m') or {}).get('heldout_suites', []))}) and no coding window would enter the figure. For "
            "comparability with 0020 and 0040 the 0016-protocol figure — pooled R² over those last ten rows — is reported "
            "BESIDE the every-sequence reading, recomputed by the summarizer from the same per-sequence moments; that readout "
            "does not exist for a fresh run today (it reads a reused prior report only) and is added in this commit set with a "
            "test, or the registration does not append" if protocol_all else
            "0016's protocol: arm (b) held out by sequence at `holdout_frac` 0.2, the LAST ceil(0.2 × 50) = 10 rows. Under "
            "this draw those are ten DISTINCT windows (0040's repeat is absent here) but, because the token file is written "
            f"suite by suite, ALL TEN ARE WORKFLOW WINDOWS ({dict((facts.get('e8m') or {}).get('heldout_suites', []))}): the "
            "registered held-out R² and the reported band read workflow text only and no coding window enters the figure. "
            "Stated, not adjusted; 0030's every-sequence reading enters as its own amendment as 0030 and 0053 did")
ENTRY = f"""### {NUM} — {a.date} — MLPerf Agentic Inference text registered before any dump: E8 on both pairs over the MLCommons trajectories (`config/e8m.toml`, `config/e8mf.toml`), reasoning kept, the shared system prefix not rendered; descriptive, no hypothesis row, no cell moves

**Why.** Every E8 figure on this ledger reads the agent-trace shift on tau2-bench and SWE-bench windows ({QWEN_RUN}, {FAMILY_RUN},
{QWEN_AMEND}, {LLAMA_AMEND}). The MLPerf Agentic Inference benchmark is the workload the field will quote for agent serving with
prefix reuse, and it ships its own recorded trajectories. This entry registers the same instrument on that text — the 0009
mapper on the existing fitted mappers of each pair, 0016 §4's sampling rule byte-for-byte, two new suites out of one file —
BEFORE any token is dumped, and decides nothing: **no hypothesis row, no `verdict:` line; H-E8 was decided by {QWEN_RUN} and
does not move**, and the band is reported as 0009 writes it, descriptive. Every figure is read beside the pair's own
tau2/SWE-bench figure and never pooled with it.

**The text, as verified.** The MLCommons dataset, one flat JSONL of {facts.get('rows', 'UNVERIFIED')} message rows in
{facts.get('traj', 'UNVERIFIED')} trajectories (SHA-256 `{DATASET_SHA[:12]}…`, equal to its README's; fetched by curl into the gitignored
`traces/mlperf-agentic/`): {facts.get('coding', 'UNVERIFIED')} DeepSWE coding traces and {facts.get('workflow', 'UNVERIFIED')} Workato workflow conversations, split by the
`_source` row field, which every Workato row carries and no DeepSWE row does — a field, not a content heuristic. Licenses
ship with it (`LICENSES.txt` `{h12('licenses')}…`, `NOTICE` `{h12('notice')}…`), read as they are written: DeepSWE is listed
"Mixed" — Datacurve AI Inc.'s Apache-2.0 covers its task specifications, harness, verifiers and curation only; the published
execution traces are MLCommons derivative works under MLCommons' Apache-2.0; the upstream project code inside the traces
carries each project's own license (Apache-2.0, MIT, BSD, ISC, Unlicense; "all included licenses are permissive; none are
copyleft or share-alike"). Workato conversations CC BY 4.0, with an attribution header the NOTICE requires preserved
verbatim wherever the data is distributed. Obligations, stated rather than claimed met: nothing derived is committed (`data/`
and `traces/` are gitignored; this entry carries hashes only), the rendered export and the token files DROP the CC BY
header, so they are not distributed from this repository, and any copy that leaves the sitting machine (the private backup)
carries `NOTICE` and `LICENSES.txt` beside it — an operator rule, enforced by no code here. Rendering (`src/linear_ceiling/e8_text.py` `{H['src/linear_ceiling/e8_text.py'][:12]}…`, `render_mlperf_rows`): rows grouped by
conversation id and ordered by turn, the 0016 role tags, `reasoning_content` KEPT ahead of the content (the benchmark's
template keeps it, so the text a serving engine caches includes it), tool calls as `name(arguments)`, tool results'
contents. **The shared system prompt and tool schema on each conversation's first row is NOT rendered**: all 500
workflow conversations open with one identical prefix of about 31K tokens, and under `window = "first"` every workflow
window would be the same 1,024 tokens — the failure {FAMILY_RUN} disclosed on the Llama draw (42 distinct windows of 50, one
preamble nine times) by construction and for every row. Rendered export `{h12('rendered')}…` (the lag-ladder cell reads it).
The old suites' rendering is unchanged: all 924 tau2-bench / SWE-bench texts rendered byte-identically under the
pre-adapter module and this one at build (`tests/test_e8_text.py` `{H['tests/test_e8_text.py'][:12]}…` covers the two renderers on
a fixture and the old suites' blindness to the new directory; it does not re-render the real corpus). The DeepSWE traces
also open with a shared system block (77 tokens, one for all 113), likewise not rendered.

**The draw** (`[e8.text]` of both configs: seed 8, n = 50, len = 1,024, `mlperf-coding` + `mlperf-workflow` stratified 25 + 25,
window "first", skipped never padded — 0016 §4's rule unchanged, only the suites differ). Eligibility, recomputed from the
export under the Qwen3 tokenizer on 2026-10-22: 113/113 coding and 492/500 workflow trajectories reach 1,024 tokens, so n = 50
stands without a rule change. Qwen pair: `data/e8m/agent_n50_len1024_seed8.npy` `{(facts.get('e8m') or {}).get('npy', 'UNVERIFIED')[:12]}…`, manifest
`{(facts.get('e8m') or {}).get('manifest', 'UNVERIFIED')[:12]}…`; Llama pair: `data/e8mf/agent_n50_len1024_seed8.npy` `{(facts.get('e8mf') or {}).get('npy', 'UNVERIFIED')[:12]}…`, manifest `{(facts.get('e8mf') or {}).get('manifest', 'UNVERIFIED')[:12]}…` — the
same rule under the Llama-3 BPE is a different 50 windows, as {FAMILY} stated for e8f. Both: **50 distinct windows, 25 per suite**,
recomputed by this script. The Qwen file is, id for id, the token file lag-ladder's entry 0030 reads under the seed-1 readers (its
`tools/agentic_tokens.py` rebuilds the draw under the Qwen2.5 tokenizer and asserts the equality row by row; both repositories
pin `{(facts.get('e8m') or {}).get('npy', 'UNVERIFIED')[:12]}…`), so every one of these fifty windows carries a mapper reading here and a reader reading there. Said once, not adjusted for: the first 1,024 tokens of a coding trace are mostly its task statement
(median first user turn ≈ 1,100 tokens under Qwen3), so this cell reads the opening of an agent trajectory, not the
accumulated history where the long form lives (a later registration at the 0036/0051 lengths, not this one).

**Protocol.** {PROTOCOL}. Mappers: the EXISTING fitted mappers of each pair (`verdict_k = 1`, reported at k = 1, 4, 8; p/n
0.10 / 0.40 / 0.80 on both pairs, {FAMILY}); arm (a) the archived generic dumps (`data/kv/<pair>`), arm (b) the MLPerf dumps
under `results/e8m/kv/agent` and `results/e8mf/kv/agent`; stride 4. Band (0009, frozen): HOLDS ≤ 0.05 drop / DEGRADES ≥ 0.15 /
UNRESOLVED between, K and V separately — reported, not verdict-bearing. Read beside: Qwen k = 1 on tau2/SWE-bench
({QWEN_RUN}) `{QWEN_ROW}`; Llama k = 1 ({FAMILY_RUN}) `{LLAMA_ROW}`. Scope note carried into every report: "{e8m['scope_note']}".

**Pin.** `upstream_sha = {PIN}` for both cells — the family pin of `config/e8f.toml`, which contains {QWEN_AMEND}'s
`{UPSTREAM_0030}` and the Llama `PAIRS` entry, so the one clone moves once for the two sittings; checked by this script
(`merge-base --is-ancestor`). Nothing upstream changes.

**Gate and enforcement.** `e8 --check --config config/e8m.toml` refuses until entries 0009/{RULE}/{NUM} are in the committed
ledger (`config/e8mf.toml`: 0009/{RULE}/{FAMILY}/{NUM}), the config is committed unmodified, and the upstream is at the pin
with every invoked path clean; `[e8.gate]` EXTENDS the driver's premise entries. `summarize_e8` is the only reader of the
figures: it re-runs the upstream scorer on the fingerprinted dumps, cross-checks arm (a) against the archived `r2.json`,
and refuses on disagreement. This script refuses if either config is modified or does not name this entry, if any pinned
file differs, if the dataset's bytes are not the README's sha, if either token file is not 50 distinct windows at 25 + 25,
if the pin lacks `{UPSTREAM_0030}`, or if `results/e8m/` or `results/e8mf/` holds anything (R1). Pinned at append: `config/e8m.toml`
`{H['config/e8m.toml'][:12]}…`, `config/e8mf.toml` `{H['config/e8mf.toml'][:12]}…`, `src/linear_ceiling/e8.py` `{H['src/linear_ceiling/e8.py'][:12]}…`,
`tests/test_e8m_configs.py` `{H['tests/test_e8m_configs.py'][:12]}…`.

**Run.** One sitting after this entry is committed: `e8 --config config/e8m.toml` then `--config config/e8mf.toml` (the Llama
8B in fp32 wants the 80 GB card), `summarize_e8` per config, outputs mirrored home and verified before the figures entry.
Budget ASSUMED until timed: 4–5 h wall on an A100 (the plan of 2026-10-22, §6). The figures enter by their own entry, which
runs `summarize_e8` in-process; no figure is typed.

**Consequences in this commit set.** `config/e8m.toml` and `config/e8mf.toml` (`[e8.gate]` to this number, `[e8.amendment]`
entry likewise, PROVISIONAL notes dropped), `tests/test_e8m_configs.py` (the absence assertion flipped),
`src/linear_ceiling/summarize_e8.py` (the 0016-protocol figure recomputed from the per-sequence moments over the last ten
rows of a fresh amendment run, reported beside the every-sequence reading) and `tests/test_summarize_e8.py`, this script
retired after the append.

**What this does NOT touch.** Every cell and verdict; τ_K, τ_agent_K, the rule, the band; `config/e8.toml`, `config/e8a.toml`,
`config/e8f.toml`, `config/e8fa.toml`, every `config/e9*.toml` and their output trees; entries {QWEN_RUN}, {QWEN_AMEND}, {FAMILY},
{FAMILY_RUN}, {LLAMA_AMEND}, 0060 and the frozen figure set.

**Scope.** Two pairs, one direction each, off-policy text for both; the opening window of recorded trajectories from one
benchmark release, two suites; reasoning text included; the provider's shared prefix excluded by rule; a registration, not
a result.

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
