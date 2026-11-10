"""DRAFT append script for linear-ceiling: entry 0067 (PROVISIONAL number; the drafts README allocates it at staging) --
entry 0061's inputs RE-PREPARED under 0061's own config. The driver 0061 pins refuses 0049's prepared inputs under the
repair config (`check()` compares the manifest's `config_sha256` with `--config`), so 0061's run cannot start as
registered. This entry takes the exit that changes no code: the pinned driver's `--prepare`, under
`config/cache-behavior-repair.toml`, on the archive, traces and evidence manifest 0049's preparation read, writes
`results/cache-behavior-repair/inputs/`. The script checks, file by file, that the result IS 0049's inputs with only the
manifest's config digest moved. DESCRIPTIVE: no `verdict:` line, no figure, no cell moves.

PRIVATE DRAFT (briefs). To stage: `0067-docs-patch.py --date D` (copies this file to docs/drafts/append_0067.py, edits the
one living doc that names 0049's inputs for 0061, appends the allocator block), then from the repo root with
.venv/Scripts/python.exe:
  --date YYYY-MM-DD  --preview  [--repo-root <path>]
Needs the operator's re-prepared inputs under results/cache-behavior-repair/inputs/ (block A of the 2026-11-09 block file).
Ordering guard: 0061 present, the ledger's last entry is PREV, NUM absent. Runs `ledger_check` after appending. Delete once
appended, chained with `&&`.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=None)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
_here = Path(__file__).resolve().parents[2]
R = (a.repo_root or (_here if (_here / "ledger" / "ledger.md").exists() else Path.home() / "dev" / "linear-ceiling")).resolve()
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_text_file                    # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM, PREV, NEXT = "0067", "0066", "0068"
AMENDS, REG, RUN_ENTRY = "0061", "0047", "0049"
CONFIG_SHA = "97aa99b1958eb55badf095955f44f2d6c0d67868a0f4196f6c5851f94e82d563"       # config/cache-behavior-repair.toml (0061)
BASE_CONFIG_SHA = "53c664556d18792401db8c1b930e487a90b88ab19c65ad94a1ab982094443a28"  # config/cache-behavior.toml (0047)
CORE_SHA = "f346b5fdf3d3feff5918e3a0e95f1e084f154317213ba68ce1913ec5acdcade5"        # tools/cache_behavior/core.py (0061)
RUN_SHA = "e137f1d8b8c5ce7f7747c8b06508ed7b09f6dc49a0731225dc8bcece9d8c2c33"         # tools/cache_behavior/run.py (0061)
MANIFEST_0049 = "2aeee5769c0a3b557e1fecd43c2a745abe9f29c37af66b0eabb54358b4c35b22"    # results/cache-behavior/inputs (0049)
MANIFEST_NEW = "7b27942c1da93d3223f04499bb56772300b788684d359d8ea258c1400aac40e5"     # pinned when this entry was drafted
OLD_INPUTS, NEW_INPUTS = "results/cache-behavior/inputs", "results/cache-behavior-repair/inputs"
OUTPUT = "results/cache-behavior-repair"
S_0061_INPUTS = "reused byte for byte; `--prepare` is not re-run."
S_0061_CHECK_HASHES = "asserts the report's source hashes equal the hashes above"

LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert NUM not in heads, f"ordering: {NUM} absent"
assert heads and heads[-1] == PREV, f"ordering: the ledger's last entry must be {PREV}, found {heads[-1] if heads else None}"
for e in (REG, RUN_ENTRY, AMENDS):
    assert heads.count(e) == 1, f"entry {e} must be on the ledger exactly once"


def block(t: str, entry: str) -> str:
    start = re.search(rf"^### {entry} ", t, re.M).start()
    nxt = re.search(r"^### \d{4} ", t[start + 4:], re.M)
    return t[start: start + 4 + nxt.start()] if nxt else t[start:]


b61 = block(text, AMENDS)
for s in (S_0061_INPUTS, S_0061_CHECK_HASHES):
    assert b61.count(s) == 1, f"0061's sentence {s[:50]!r} must occur once in its entry, found {b61.count(s)}"
assert f"`{MANIFEST_0049[:12]}" in b61 and f"`{CONFIG_SHA[:12]}" in b61, "0061 must name 0049's manifest and its config"

# The four files 0061 pins, unchanged: this entry changes no code and no registered config.
pins = {"config/cache-behavior-repair.toml": CONFIG_SHA, "config/cache-behavior.toml": BASE_CONFIG_SHA,
        "tools/cache_behavior/core.py": CORE_SHA, "tools/cache_behavior/run.py": RUN_SHA}
for rel, sha in pins.items():
    assert sha256_text_file(R / rel) == sha, f"{rel} is not at the hash 0061 pins"
    assert f"`{sha[:12]}" in b61, f"0061 does not cite {rel} at {sha[:12]}"
cfg = tomllib.loads((R / "config/cache-behavior-repair.toml").read_text(encoding="utf-8"))


def raw(p: Path) -> str:
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


# 0049's inputs, unchanged; then the re-prepared inputs, file by file against them.
old, new = R / OLD_INPUTS, R / NEW_INPUTS
assert raw(old / "manifest.json") == MANIFEST_0049, f"{OLD_INPUTS}/manifest.json is not 0049's"
assert (new / "manifest.json").exists(), f"{NEW_INPUTS}/manifest.json missing: run block A (the re-prepare) first"
assert raw(new / "manifest.json") == MANIFEST_NEW, f"{NEW_INPUTS}/manifest.json is not the pinned re-preparation"
mo, mn = (json.loads((d / "manifest.json").read_text(encoding="utf-8")) for d in (old, new))
assert set(mo) == set(mn), "the two manifests carry different top-level fields"
fields = sorted(k for k in mo if k != "records")
same = [k for k in fields if mo[k] == mn[k]]
assert [k for k in fields if k not in same] == ["config_sha256"], "only config_sha256 may differ between the manifests"
assert mo["config_sha256"] == BASE_CONFIG_SHA and mn["config_sha256"] == CONFIG_SHA, "config digests are not 0047's / 0061's"
# check()'s other two identity comparisons, on the newline-normalized digest (check() reads raw bytes of an LF checkout).
assert mn["corpus_manifest_sha256"] == sha256_text_file(R / "config/e7-manifest.json"), "corpus manifest digest differs"
assert mn["archive_config_sha256"] == sha256_text_file(R / "config/e9l.toml"), "archive config digest differs"
ro, rn = mo["records"], mn["records"]
n = len(rn)
assert len(ro) == n == cfg["expected_handoffs"], f"records: {len(ro)} vs {n}, expected {cfg['expected_handoffs']}"
excluded = sum(bool(r["excluded"]) for r in rn)
for x, y in zip(ro, rn):
    assert x == y, f"record {y.get('file')} differs from 0049's"
    fo, fn = old / x["file"], new / y["file"]
    assert raw(fn) == y["sha256"] == raw(fo), f"{y['file']}: file bytes differ from its record or from 0049's"
extra = sorted(p.name for p in new.iterdir() if p.name != "manifest.json" and p.name not in {r["file"] for r in rn})
assert not extra, f"{NEW_INPUTS} holds files the manifest does not name: {extra[:3]}"

# R1 for 0061: nothing has run.
out = R / OUTPUT
assert not (out / "report.json").exists() and not (out / "summary.json").exists(), f"{OUTPUT} holds a run; refusing"

s12 = lambda s: s[:12]  # noqa: E731
same_list = ", ".join(f"`{k}`" for k in same)
ENTRY = f"""### {NUM} — {a.date} — Entry {AMENDS}'s inputs re-prepared under its own config: the driver {AMENDS} pins refuses entry {RUN_ENTRY}'s prepared inputs under the repair config, so `--prepare` re-ran on the same archive and reproduced {RUN_ENTRY}'s {n} records byte for byte, only the manifest's config digest moving; no code, config, arm or reading changes; descriptive, no cell moves

**What is wrong in {AMENDS}.** Entry {AMENDS} registers its run on "the operator's prepared inputs of entry {RUN_ENTRY} (manifest
`{s12(MANIFEST_0049)}…`, …), {S_0061_INPUTS}" The driver {AMENDS} pins, `tools/cache_behavior/run.py` (`{s12(RUN_SHA)}…`),
cannot run on those inputs under the repair config. Every action except `--prepare` first calls `check()`, and `check()`
refuses ("configuration changed after preparation") unless the manifest's `config_sha256` equals the digest of the
`--config` file. Entry {RUN_ENTRY}'s manifest records entry {REG}'s config (`{s12(BASE_CONFIG_SHA)}…`); {AMENDS}'s run reads
`config/cache-behavior-repair.toml` (`{s12(CONFIG_SHA)}…`). So `--check`, `--probe`, `--run` and `--summarize` each refuse, and
{AMENDS}'s run could not start on any card. Found before any {AMENDS} prefill; nothing of {AMENDS} has run (R1, below).

**The exit taken.** Either the driver or the manifest has to change. This entry changes only the manifest, and only by the
pinned driver's own hand: `run.py --prepare` under `config/cache-behavior-repair.toml`, on the archive, traces and evidence
manifest that {RUN_ENTRY}'s preparation read, writes {AMENDS}'s inputs to `{NEW_INPUTS}/`. No code, config, test or registered
value changes: `run.py`, `core.py` and both configs are at the hashes {AMENDS} cites. The preparation runs on Linux from an
LF checkout, as {RUN_ENTRY}'s did; the driver writes the manifest with the platform's newline and digests the config's raw
bytes.

**What the re-preparation produced, checked by this script at append.** Manifest `{s12(MANIFEST_NEW)}…`. Its {n} records
are {RUN_ENTRY}'s {n}, in the same order and with every field equal ({excluded} excluded). Each prepared file is byte-identical
(sha256) to {RUN_ENTRY}'s file of the same name and to its own record's hash, and the folder holds no other file. Of the
manifest's {len(fields)} top-level fields beside the records, {len(same)} equal {RUN_ENTRY}'s ({same_list}). `config_sha256` reads
`{s12(CONFIG_SHA)}…`, the repair config's, where {RUN_ENTRY}'s reads `{s12(BASE_CONFIG_SHA)}…`. So {AMENDS}'s run reads, byte for
byte, the inputs {AMENDS} registered, and only the identity the driver checks has moved. The script repeats `check()`'s
input comparisons (the three config digests, each file's hash, the cohort size) but not its runtime pin. The operator's block runs
the driver's own `--check` on these inputs before the append and stops unless it passes under the repair config and refuses
under {REG}'s.

**{AMENDS} as amended.** Its inputs sentence reads: the inputs at `{NEW_INPUTS}/` (manifest `{s12(MANIFEST_NEW)}…`), prepared by
the pinned driver under the repair config, every record and file byte-identical to entry {RUN_ENTRY}'s (manifest
`{s12(MANIFEST_0049)}…`). Everything else in {AMENDS} stands as registered: the arms, the budgets, the selection seed, the
numerical controls, the readout, the stopping rule, the card, the output tree `{OUTPUT}/`, the mirror and backup, and
the figures entry's checks, to which this entry adds one: that entry must also assert that the report's
`identity.manifest_sha256` is `{s12(MANIFEST_NEW)}…`. {AMENDS}'s
run is requested only after this entry is on main.

**Gate and enforcement.** This script refuses unless all of these hold. {AMENDS} is on the ledger and its inputs sentence occurs
once. The four files {AMENDS} pins are at its hashes. {RUN_ENTRY}'s manifest is unchanged. The new manifest's sha256 is exactly
the value pinned when this entry was drafted, so a re-preparation that differs in any byte refuses. Every record and
file equals {RUN_ENTRY}'s. `config_sha256` is the repair config's digest. `{OUTPUT}` holds no run (R1: no `report.json`, no
`summary.json`).

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries {REG} and {RUN_ENTRY} and their records;
entry {AMENDS} except its one inputs sentence; `{OLD_INPUTS}/` (read, not written); `config/`, `tools/`, `tests/`.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard {AMENDS} present, {PREV} last,
{NUM} absent. Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new_text = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new_text)
digest = chain_hash(new_text, re.search(rf"^### {NUM} ", new_text, re.M).start(), head.start())
new_text = new_text.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new_text, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
