"""DRAFT append script for linear-ceiling: the outcome of 0076 (window end amended by 0077), the cache reading of the
Finance Agent run's paired helper sub-calls. Written ONLY from the driver's summary of record and the driver's records
beside it. DESCRIPTIVE: no `verdict:` line, no hypothesis row, no band, no interval, no cell moves. The number is the
ledger's next after 0078, PROVISIONAL until the drafts README stages this script.

The summary of record is the `summary.json` the driver's own `--summarize` wrote from the output tree copied off the
reading machine, under the code at the commit the reading ran; it is pinned here by sha256, and this script refuses
unless it is that file byte for byte, unless the reading machine's own `summary.json` (also pinned) holds the same values
and the same bytes up to line ends, and unless the summary agrees with itself: every pair-level and trajectory-level
median, p10 and p90 is recomputed here from `per_pair` with the repository's one convention (`e7_stats.summary`), the
counts are recomputed from the named lists, and `over_the_cap_matched_share` from the matched counts of the read and
the excluded pairs (the report's `excluded`). Beside it, each pinned by sha256: the driver's report (its identity, the
commit, the excluded candidates), the lock `launch.json`, the chain's log (the two launches, each the first attempt, and
their times), the record of the inputs' removal, and the driver's own logs of the two launches (the allocator's
warnings, counted by step; every line of each must be a weight-loading bar, an allocator warning, the control's line or
a pair's progress line, so no text of the Finance Agent run's logs is read). Every figure in the entry comes from these
files; none is typed.

    python -I docs/drafts/append_NUM.py --repo-root . --date YYYY-MM-DD --summary <summary.json>
        --pod-summary <summary.pod.json> --report <report.json> --lock <launch.json> --chain-log <chain log>
        --removal <removal record> --probe-log <first launch's log> --run-log <resume's log> [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root must be the current directory and the
top of its git work tree, and the imported `linear_ceiling` must be that tree's. The script refuses under -O. Outside
`--preview` it refuses until the drafts README stages this script with the next number. Before the write, the ledger
must equal HEAD's, be unmodified and pass `ledger_check`; after it `ledger_check` runs again, and on a failure the old
bytes go back. The script writes only ledger/ledger.md.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import textwrap
import tomllib
import traceback
from pathlib import Path

if not __debug__ or sys.flags.optimize:
    raise SystemExit("REFUSED: python runs with -O or PYTHONOPTIMIZE set, which strips every guard (assert) in this script")


def _refused(et, ev, tb):
    """Any exception is a refusal: print the guard's line so the output shows which one fired; exit status 1."""
    fr = [f for f in traceback.extract_tb(tb) if Path(f.filename).resolve() == Path(__file__).resolve()] or traceback.extract_tb(tb)
    sys.stderr.write(f"REFUSED: {et.__name__} at line {fr[-1].lineno}: {ev}\n  guard: {fr[-1].line}\n")


sys.excepthook = _refused
ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--repo-root", type=Path, required=True)
ap.add_argument("--summary", type=Path, required=True)
ap.add_argument("--pod-summary", type=Path, required=True)
ap.add_argument("--report", type=Path, required=True)
ap.add_argument("--lock", type=Path, required=True)
ap.add_argument("--chain-log", type=Path, required=True)
ap.add_argument("--removal", type=Path, required=True)
ap.add_argument("--probe-log", type=Path, required=True)
ap.add_argument("--run-log", type=Path, required=True)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
ENV = dict(os.environ)
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True, env=ENV)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
sys.path.insert(0, str(R / "src"))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling import e7_stats                                        # noqa: E402
from linear_ceiling.hashing import sha256_text_file                       # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
for _m in (_lc, e7_stats):
    assert Path(_m.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_m.__file__}, not the tree's"

LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
# The commit the reading ran at (the report's git_commit; it carries 0075, 0076 and 0077).
READ_COMMIT = "383605578d8731ffe9f262189446c03f2bb26e38"
# The files the reading ran, as 0076 and 0077 pin them (each entry's text gives the first 12 hex digits).
PINS = {"config/cache-behavior-fab.toml": ("0077", "93d05ca402fd9ed28d0223f0df2d03205a86bcf004924a28433d53754bbf1085"),
        "tools/cache_behavior/run.py": ("0076", "055d8eaccf78847a05ae05bddd209e76f2494ae1aac8d02fc67610f921fcc31f"),
        "tools/cache_behavior/core.py": ("0076", "128eea9649fbfe950e60bd39fa0db7101eba8d8515d5724993e94e5da78e8693"),
        "tools/cache_behavior/fab_pairs.py": ("0076", "c3323d44f67c5648157e241de6aa43c4d0efa1748f01b1192a4b08a441eeb8a6"),
        "src/linear_ceiling/fab_reuse.py": ("0076", "b884ec174132fa43da9bab585d590f59579d06c8f143badc5d1db9fbb2460149"),
        "config/fab-reuse.toml": ("0076", "773ddef7e2c2389586ba1630afa70b8b8b2504792e1ac030093ecef7fe33362c")}
# The summary of record and the records beside it, pinned by the sha256 of their bytes.
SUMMARY_SHA256 = "bf2523f4783129b0bd88ca27f07891de369c7093f533c7f99ac050dbb32e142d"
POD_SUMMARY_SHA256 = "7d59519584fe1207f903ab6c8c12ac53f641adf363aaf93b3067017408d3eef3"
REPORT_SHA256 = "b07e61db6a3efc44d1f6bba995715529f558dbe72879bd3bb7cf732afa78a0bd"
LOCK_SHA256 = "74a931c8666c2bf8e2aa32736c6755a53a5fc971c2bbf7416e6e82a406321297"
CHAIN_LOG_SHA256 = "8e0604fc14b826a6260d0cd96c23948d7f3d245a97560d051ffb8cfa2865bc3c"
REMOVAL_SHA256 = "95e54c53a3cb1fcb4c357b48c41711e9b871f656a5e24b721af91167da077299"
PROBE_LOG_SHA256 = "e923ef6e89fab8cb80be31e57d9b8f03fb9f0c68cc31b734e2cd89784fe7b757"
RUN_LOG_SHA256 = "638647693bebb8ebc5c013aafe87c6be9c4994f0706087e5b2a62d188656ed44"
# The driver's logs: the forms a line may take (lines split at CR and LF; a bar redraws itself with CR).
OOM_PHRASE = "memory allocation failed with OOM on device 0"
OOM_LINE = re.compile(r"\[W\d{4} \d\d:\d\d:\d\d\.\d+ CUDACachingAllocator\.cpp:\d+\] " + re.escape(OOM_PHRASE)
                      + r" while trying to allocate \d+ bytes \(free: \d+, total: \d+\)\.")
BAR_LINE = re.compile(r"Loading weights: +\d+%\|[^|]*\| *\d+/\d+ \[[^\]]*\]")
CONTROL_LINE = "cross-instrument control passed"
PROGRESS_LINE = re.compile(r"(\d+)/(\d+) (row\d\d/t\d{3}\.\d{3}<t\d{3}\.\d{3})")
# 0076's stopping rule, quoted from its line (the script holds the quote to 0076's text).
STOP_QUOTE = "a failed control, identity check or hash, or an out-of-memory, stops the run"
# 0076's summary fields, in its order (line "Summary, fixed now."); the script holds the summary to them.
FAB_FIELDS = ("label", "cross_check_label", "cross_check", "read", "selected", "not_read", "stop_at", "stopped",
              "ended_in_flight", "probe_pair", "built", "candidates", "eligible", "exclusions", "excluded",
              "over_the_cap_matched_share", "reused_within_cap_0075", "questions", "all", "same_offset",
              "different_offset", "per_pair")
EXCLUSIONS = ("prefix", "repeated keys only", "below the matched-token floor", "no logged response",
              "fewer than two continuation tokens", "over the cap", "over host memory", "beyond the ceiling")
STATS = ("mean_kl", "p90_kl", "top1_agreement")
ARMS = (("reuse", "REUSE"), ("random", "RANDOM"), ("scrambled", "CYCLIC"))
PAIR_STATS = ("f_star_K", *(f"{arm}_{k}" for arm, _ in ARMS for k in STATS))
CC_FIELDS = ("matched", "tokens_outside_tolerance", "max_gap", "max_gap_over_bound", "f_star_driver", "f_star_archive",
             "tokens_over_tau_K_driver", "tokens_over_tau_K_archive", "passed", "handoff", "identity", "archived_mean",
             "minutes")
CEILING = 60


def git(*args) -> bytes:
    return subprocess.run(["git", "-C", str(R), *args], capture_output=True, check=True, env=ENV).stdout


def block(t: str, entry: str) -> tuple:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} heading lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def once(t: str, entry: str, phrase: str) -> int:
    """The line of the phrase (any whitespace between its words), which must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(re.finditer(r"\s+".join(re.escape(w) for w in phrase.split()), b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {phrase[:60]!r}"
    return t.count("\n", 0, start + hits[0].start()) + 1


def preview_note(msg: str) -> None:
    print(f"[preview] {msg}; the append refuses until it is", file=sys.stderr)


def pinned(p: Path, full: str, what: str) -> bytes:
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == full, f"{what} ({p.name}) is not the pinned file"
    return raw


# --- this ledger: the ordering, and the lines of 0076 and 0077 this entry cites ------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0078", f"the ledger's last entry is {PREV}, not 0078"
assert "0076" in heads and "0077" in heads, "0076 or 0077 is not on the ledger"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
_, B76 = block(text, "0076")
_, B77 = block(text, "0077")
L76 = {k: once(text, "0076", p) for k, p in {
    "head": "Cache reading of the Finance Agent run's paired helper sub-calls registered before any pair is built",
    "window": "A question is read only if every one of its launches has ended",
    "pairs": "B is a sub-call carrying at least one document token whose identity an earlier sub-call of its trajectory",
    "classes": "The two classes are reported apart and pooled.",
    "cap": "The outcome reports the pairs the cap leaves out",
    "excl": "Exclusions, in order, each counted and named.",
    "counts": "the outcome reports the counts with the manifest's digest.",
    "label": "Every figure carries the label",
    "cc": "The cross-instrument control, before any finance pair.",
    "names": "The outcome names every manifest built, its lock and every launch.",
    "ccpass": "If the control runs and passes, every f* carries",
    "probe": "is read first as the memory probe",
    "controls": "The controls are 0047's (line 3243), on the probe pair only",
    "fresh": "The fresh repeat must reproduce the first FRESH pass's logits exactly",
    "prefixcopy": "The prefix copy over 128 tokens stays at most 0.0005.",
    "readcount": "the summary states the read count and names the selected pairs not read.",
    "stoprule": "The stopping rule is 0047's",
    "summary": "Summary, fixed now.",
    "nointerval": "No interval is reported",
    "beside": "This cell is on the same axis as 0049's 35-handoff REUSE-ALL row",
    "removed": "and they are removed from the pod before it is released.",
    "private": "They are kept private with the output tree",
    "scope": "One reader, Qwen3-1.7B at YaRN 2.5, cap 81,920;",
}.items()}
L77 = {k: once(text, "0077", p) for k, p in {
    "head": "Window amendment to 0076, before any pair is built",
    "window": "Its `window_end`, from `2026-11-20T12:00:00Z` to `2026-11-20T06:30:00Z`",
}.items()}
for rel, (entry, full) in PINS.items():
    assert f"sha256 `{full[:12]}…`" in " ".join((B77 if entry == "0077" else B76).split()), f"{entry} does not pin {rel} at {full[:12]}"
for f in FAB_FIELDS:
    assert f"`{f}`" in B76, f"0076 does not name the summary field {f}"
for x in EXCLUSIONS:
    assert f'"{x}"' in B76, f"0076 does not name the exclusion {x!r}"
assert f"The stopping rule is 0047's: {STOP_QUOTE};" in " ".join(B76.split()), "0076's stopping rule is not the quoted text"
# The allocator-warning precedent: 0070's paragraph, the reading it carries, and the ruling it quotes (taken from it, not typed)
_, B70 = block(text, "0070")
L70 = once(text, "0070", "**Allocator warnings.** The long cell's logs hold")
assert "By the operator's ruling (2026-11-11, restated 2026-11-13) the reading given for 0061's run carries to this one." \
    in " ".join(B70.split()), "0070 does not carry the reading given for 0061's run"
_rul = re.findall(r'Verbatim: "(An OOM in that rule[^"]*)"', B70)
assert len(_rul) == 1, "0070 does not quote the ruling once"
RULING = " ".join(_rul[0].split())
assert f'Verbatim: "{RULING}"' in " ".join(block(text, "0069")[1].split()), "0069 does not quote the same ruling"

# --- the files the reading ran: at the reading's commit, unchanged to HEAD, and the tree's ---------------------------------------
assert git("merge-base", "--is-ancestor", READ_COMMIT, "HEAD") == b"", f"{READ_COMMIT[:12]} is not on HEAD's history"
assert git("log", "--format=%H", f"{READ_COMMIT}..HEAD", "--", *PINS) == b"", "a file the reading ran changed after its commit"
for rel, (_, full) in PINS.items():
    assert sha256_text_file(R / rel) == full, f"{rel} in the tree is not the pinned file"
    assert hashlib.sha256(git("show", f"{READ_COMMIT}:{rel}").replace(b"\r\n", b"\n")).hexdigest() == full, \
        f"{rel} at {READ_COMMIT[:12]} is not the pinned file"
for _e in ("0075", "0076", "0077"):
    assert f"\n### {_e} ".encode() in git("show", f"{READ_COMMIT}:ledger/ledger.md"), f"{_e} is not on the ledger at {READ_COMMIT[:12]}"
CFG = tomllib.loads(git("show", f"{READ_COMMIT}:config/cache-behavior-fab.toml").decode("utf-8"))
assert CFG["window_end"] == "2026-11-20T06:30:00Z" and f"to `{CFG['window_end']}`" in " ".join(B77.split()), \
    "the config's window_end is not the one 0077 sets"
assert git("ls-files", "--", "results/cache-behavior-fab") == b"", "a file under results/cache-behavior-fab/ is tracked"

# --- the summary of record and the records beside it -----------------------------------------------------------------------------
raw = pinned(a.summary, SUMMARY_SHA256, "the summary of record")
raw_pod = pinned(a.pod_summary, POD_SUMMARY_SHA256, "the reading machine's summary")
assert raw.replace(b"\r\n", b"\n") == raw_pod, "the summary of record is not the reading machine's, byte for byte up to line ends"
S = json.loads(raw.decode("utf-8"))
assert S == json.loads(raw_pod.decode("utf-8")), "the two summaries' values differ"
REP = json.loads(pinned(a.report, REPORT_SHA256, "the driver's report").decode("utf-8"))
LOCK = json.loads(pinned(a.lock, LOCK_SHA256, "the lock").decode("utf-8"))
CHAIN = pinned(a.chain_log, CHAIN_LOG_SHA256, "the chain's log").decode("utf-8").splitlines()
REMOVAL = pinned(a.removal, REMOVAL_SHA256, "the removal record").decode("utf-8").splitlines()
F = S["fab"]
assert tuple(F) == FAB_FIELDS, f"the summary's fab fields are not 0076's: {list(F)}"
ID = REP["identity"]

# the report: the commit, the reader, the pins, the manifest, the control, the order
assert REP["git_commit"] == READ_COMMIT, "the report's git_commit is not the reading's commit"
assert REP["cell"] == "fab-pairs" and REP["model"] == "Qwen/Qwen3-1.7B", "the report is not the fab cell's, or not Qwen3-1.7B's"
assert REP["rope"]["rope_type"] == "yarn" and REP["rope"]["factor"] == 2.5, "the report's reader is not at YaRN 2.5"
assert ID["config_sha256"] == PINS["config/cache-behavior-fab.toml"][1], "the report's config digest is not the pinned config"
for f in ("run.py", "core.py", "fab_pairs.py"):
    assert ID["code_sha256"][f] == PINS[f"tools/cache_behavior/{f}"][1], f"the report's {f} digest is not the pinned file"
assert set(ID["code_sha256"]) == {"run.py", "core.py", "fab_pairs.py"}
MANIFEST = ID["manifest_sha256"]
assert re.fullmatch(r"[0-9a-f]{64}", MANIFEST) and LOCK["manifest_sha256"] == MANIFEST, "the lock is not the report's manifest's"
assert set(LOCK) == {"manifest_sha256", "stop_at", "branch", "at"}, f"the lock's fields: {sorted(LOCK)}"
assert LOCK["stop_at"] == REP["stop_at"] == F["stop_at"], "the wall-time limit differs between the lock, the report and the summary"
assert LOCK["branch"] == REP["cross_check"]["branch"] == F["cross_check"]["branch"] == "run", "the cross-check branch is not `run` throughout"
assert REP["cross_check"] == F["cross_check"], "the summary's cross_check is not the report's"
assert REP["complete"] is True and S["complete"] is True, "the reading is not complete"
assert REP["attention_queries"] == 0 and S["attention"] == "not computed: attention_queries = 0", "the attention slice is not recorded as not computed"
assert REP["archive_bridge"] == "not computed: no archive holds these pairs", "the archive bridge is not recorded as not computed"
assert REP["ended_in_flight"] == [] and F["ended_in_flight"] == [] and not REP.get("in_flight"), "a step was under way"
assert F["stopped"] is None and REP.get("stopped") is None and F["not_read"] == [], "the sitting stopped at its limit, or a selected pair is not read"

# the chain's log: two launches, each the first attempt; both exit 0; the identity line is the report's
_launch = [ln for ln in CHAIN if re.match(r"(PROBE|RUN)_LAUNCH ", ln)]
assert [ln.split()[0] for ln in _launch] == ["PROBE_LAUNCH", "RUN_LAUNCH"], f"the launches: {_launch}"
assert re.fullmatch(r"PROBE_LAUNCH \d\d:\d\d:\d\d attempt 1 first", _launch[0]) and \
    re.fullmatch(r"RUN_LAUNCH \d\d:\d\d:\d\d attempt 1", _launch[1]), f"a launch is not the first attempt: {_launch}"
assert not any(re.search(r"attempt [2-9]", ln) for ln in CHAIN), "a relaunch is recorded"
assert sum(1 for ln in CHAIN if re.fullmatch(r"probe rc 0 \d\d:\d\d:\d\d", ln)) == 1 and \
    sum(1 for ln in CHAIN if re.fullmatch(r"run rc 0 \d\d:\d\d:\d\d", ln)) == 1, "a launch did not exit 0"
assert CHAIN[-1] == "CHAIN_DONE" and sum(1 for ln in CHAIN if ln.startswith("CHAIN_")) == 1, "the chain did not end CHAIN_DONE"
_idl = [ln for ln in CHAIN if ln.startswith("IDENTITY ")]
assert _idl == [f"IDENTITY manifest {MANIFEST[:12]} config {ID['config_sha256'][:12]} run.py {ID['code_sha256']['run.py'][:12]} "
                f"core.py {ID['code_sha256']['core.py'][:12]} fab_pairs.py {ID['code_sha256']['fab_pairs.py'][:12]} | {ID['gpu']} "
                f"{ID['torch']} {ID['transformers']} cuda {ID['cuda']} {ID['cublas_workspace_config']} | git {READ_COMMIT[:12]}"], \
    "the chain's identity line is not the report's"
_ix = {k: [i for i, ln in enumerate(CHAIN) if re.match(p, ln)] for k, p in {
    "probe": r"PROBE_LAUNCH ", "control": r"STOP_AT \S+ \| CROSS_CHECK branch run passed True$", "scored1": r"SCORED 1 of \d+ \|",
    "run": r"RUN_LAUNCH ", "close": r"CLOSE complete True "}.items()}
assert all(len(v) == 1 for v in _ix.values()), f"the launch log's lines: {_ix}"
assert _ix["probe"][0] < _ix["control"][0] < _ix["scored1"][0] < _ix["run"][0] < _ix["close"][0], \
    "the launch log is not: the first launch, the control passed, one pair scored, the resume, the close"
assert f"CLOSE complete True read {F['read']} of {F['selected']} stopped None | summary_scored {F['read']} summary_stopped None" in CHAIN
T_FIRST, T_RESUME = _launch[0].split()[1], _launch[1].split()[1]      # the reading machine's clock, as the log records it

# the removal record: the inputs recorded, no copy left, removed
assert sum(1 for ln in REMOVAL if re.fullmatch(r"INPUTS_REMOVED \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", ln)) == 1, "no removal line"
assert sum(1 for ln in REMOVAL if re.match(r"LEFT_DIRS 0 \| COPIES_FOUND 0 \(", ln)) == 1, "the removal found a copy or a folder left"
assert REMOVAL[-1].startswith("INPUTS_REMOVED "), "the removal record does not end with the removal"
REMOVED_AT = REMOVAL[-1].split()[1]

# --- the summary agrees with itself --------------------------------------------------------------------------------------------
PP = F["per_pair"]
READ = [x["handoff"] for x in PP]
assert len(READ) == len(set(READ)) == F["read"] == S["scored"] == len(REP["scores"]), "the read count is not the per-pair rows'"
assert READ == REP["run_order"][:len(READ)] and set(READ) == set(REP["scores"]), "the read pairs are not the order's first"
assert F["selected"] == len(REP["run_order"]) <= CEILING, "the selection exceeds the ceiling or is not the run order"
assert F["probe_pair"] == REP["run_order"][0] == READ[0], "the probe pair is not read first"
assert [x["handoff"] for x in PP if x["probe"]] == [F["probe_pair"]], "the probe flag is not on the probe pair alone"
# the controls, on the probe pair only (0076, from 0047): the fresh repeat exact, the prefix copy within the config's limit
CTRL = REP["scores"][F["probe_pair"]]["controls"]
assert set(CTRL) == {"fresh_repeat", "prefix_copy"}, "the probe pair's controls are not the fresh repeat and the prefix copy"
assert not any(REP["scores"][h]["controls"] for h in READ[1:]), "a control ran on a pair other than the probe pair"
assert CFG["prefix_control_tokens"] == 128 and CFG["control_max_logit_error"] == 0.0005, "the config's controls are not 0076's"
assert CTRL["fresh_repeat"]["max_logit_error"] == 0, "the fresh repeat is not exact"
assert 0 <= CTRL["prefix_copy"]["max_logit_error"] <= CFG["control_max_logit_error"], "the prefix copy is over its limit"
# the probe pair is the largest selected pair by 0076's size rule (line "is read first as the memory probe"): the larger
# of A's prefill and B with its continuation less one; unique, and every selected pair is read, so per_pair is the selection
assert F["read"] == F["selected"] == len(PP), "a selected pair is not in per_pair"
_size = {x["handoff"]: max(x["sender_tokens"], x["receiver_tokens"] + x["continuation_tokens"] - 1) for x in PP}
_big = max(_size.values())
assert [h for h, v in _size.items() if v == _big] == [F["probe_pair"]], "the probe pair is not the unique largest by 0076's rule"


# --- the driver's own logs of the two launches: the allocator's warnings, counted by step -------------------------------------
def driver_log(raw: bytes, what: str) -> list:
    """The steps a driver log closes, in order, each with the warnings counted on it. The driver prints the control's
    line once its result is written and a pair's progress line once its score is written (run.py), so a warning is
    counted on the step whose line follows it. Every line must be a weight-loading bar, an allocator warning, the
    control's line or a progress line: any other line refuses, so nothing but these forms is read. The weight-loading
    bars must all come before the first warning or step line, so no warning of the model's loading is counted on a step."""
    assert b"Traceback" not in raw, f"{what} holds a traceback"
    steps, pending, oom, loaded = [], 0, 0, False
    for ln in raw.decode("utf-8").replace("\r", "\n").split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if BAR_LINE.fullmatch(ln):
            assert not loaded, f"{what}: a weight-loading bar after a warning or a step's line"
            continue
        loaded = True
        if OOM_LINE.fullmatch(ln):
            pending, oom = pending + 1, oom + 1
            continue
        m = PROGRESS_LINE.fullmatch(ln)
        assert ln == CONTROL_LINE or m, f"{what}: a line that is not a bar, a warning, the control's line or a progress line"
        steps.append(("control", None, pending) if m is None else (int(m.group(1)), (m.group(3), int(m.group(2))), pending))
        pending = 0
    assert pending == 0, f"{what}: a warning after its last step's line"
    assert oom == raw.count(OOM_PHRASE.encode()), f"{what}: a warning not in the counted form"
    return steps


PLOG = driver_log(pinned(a.probe_log, PROBE_LOG_SHA256, "the first launch's log"), "the first launch's log")
RLOG = driver_log(pinned(a.run_log, RUN_LOG_SHA256, "the resume's log"), "the resume's log")
assert [s[0] for s in PLOG] == ["control", 1] and [s[0] for s in RLOG] == list(range(2, len(READ) + 1)), \
    "the logs' steps are not: the control and pair 1, then pairs 2 onward, each once and in order"
assert [s[1] for s in PLOG[1:] + RLOG] == [(h, F["selected"]) for h in READ], "a progress line does not name the pair read in its place"
OOM_CONTROL = PLOG[0][2]
OOM_PAIR = [s[2] for s in PLOG[1:] + RLOG]                                   # by place in the order read; [0] is the probe
OOM_TOTAL = OOM_CONTROL + sum(OOM_PAIR)
assert OOM_TOTAL > 0, "the logs hold no allocator warning: this paragraph's text does not fit"
assert F["exclusions"] == {k: len(F["excluded"][k]) for k in EXCLUSIONS}, "an exclusion count is not its named list's length"
assert tuple(F["exclusions"]) == EXCLUSIONS, "the exclusions are not in 0076's order"
assert F["candidates"] == F["eligible"] + sum(F["exclusions"].values()) - F["exclusions"]["beyond the ceiling"], "candidates != eligible + excluded"
assert F["eligible"] == F["selected"] + F["exclusions"]["beyond the ceiling"], "eligible != selected + beyond the ceiling"
EXC = {r["handoff"]: r for r in REP["excluded"]}
assert sorted(EXC) == sorted(h for v in F["excluded"].values() for h in v), "the report's excluded are not the summary's"
assert all(EXC[h]["reason"] == k for k, v in F["excluded"].items() for h in v), "an excluded pair's reason differs"
_over = sum(EXC[h]["matched"] for h in F["excluded"]["over the cap"])
_all = sum(r["matched"] for r in EXC.values()) + sum(x["matched"] for x in PP)
assert len(EXC) + len(PP) == F["candidates"] and F["over_the_cap_matched_share"] == _over / _all, \
    "over_the_cap_matched_share is not the over-the-cap pairs' matched tokens over all candidates'"
CLASSES = {"same_offset": [x for x in PP if x["class"] == "same_offset"], "different_offset": [x for x in PP if x["class"] == "different_offset"]}
assert len(CLASSES["same_offset"]) + len(CLASSES["different_offset"]) == len(PP), "a read pair is in neither class"


def recompute(sel):
    if not sel:
        return None
    by_t = {}
    for x in sel:
        by_t.setdefault(x["task_id"], []).append(x)
    return {"pairs": len(sel), "trajectories": len(by_t),
            "pair_level": {s: e7_stats.summary([x[s] for x in sel]) for s in PAIR_STATS},
            "trajectory_level": {s: e7_stats.summary([statistics.median([x[s] for x in v]) for v in by_t.values()])
                                 for s in PAIR_STATS}}


assert F["all"] == recompute(PP), "the pooled block is not its per-pair rows' summary"
for c, sel in CLASSES.items():
    assert F[c] == recompute(sel), f"the {c} block is not its per-pair rows' summary"
for arm, _ in ARMS:
    for k in STATS:
        assert S["arms"][arm][k] == F["all"]["pair_level"][f"{arm}_{k}"], f"the report-level {arm} {k} is not the pooled pair level"
assert F["questions"] and all(re.fullmatch(r"row\d\d", t) for v in F["questions"].values() for t in v)
NQ = sum(len(v) for v in F["questions"].values())
assert NQ == 27, f"the questions' statuses name {NQ} task ids, not the run's 27"
assert set(x["task_id"] for x in PP) <= set(F["questions"].get("measured", [])), "a read pair's trajectory is not measured"
W = F["reused_within_cap_0075"]
assert W["trajectories"] == len(F["questions"].get("measured", [])), "0075's counts at the cap are not over the measured trajectories"
assert F["label"] in " ".join(B76.split()), "the summary's label is not 0076's"
assert F["cross_check_label"] == "checked per token against the E9-long archive on one handoff" and \
    f'"{F["cross_check_label"]}"' in " ".join(B76.split()), "the cross-check label is not 0076's passed label"
CC = F["cross_check"]["result"]
assert tuple(CC) == CC_FIELDS and CC["passed"] is True, "the control's fields are not 0076's, or it did not pass"
assert CC["handoff"] in " ".join(B76.split()), "the control's handoff is not 0076's"

# --- the drafts README stages this script --------------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if not (f"`append_{NUM}.py`" in readme and free and free[-1] == NEXT):
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    preview_note(f"the drafts README does not stage append_{NUM}.py at {NEXT}")


# --- the entry's text, every figure from the files above -------------------------------------------------------------------------
def f4(x) -> str:
    return "null" if x is None else f"{x:.4f}"


def n(x) -> str:
    return "null" if x is None else f"{x:,}"


def sm(d) -> str:
    return "null" if d is None else f"{f4(d['median'])} (p10 {f4(d['p10'])}, p90 {f4(d['p90'])})"


def level_lines(lv: dict) -> list:
    out = [f"  - f* (`f_star_K`): {sm(lv['f_star_K'])}"]
    for arm, name in ARMS:
        out.append(f"  - {name}: mean KL {sm(lv[f'{arm}_mean_kl'])}; p90 KL {sm(lv[f'{arm}_p90_kl'])}; "
                   f"top-1 agreement {sm(lv[f'{arm}_top1_agreement'])}")
    return out


def block_text(name: str, g) -> str:
    if g is None:
        return f"*`{name}`: null (no read pair).*"
    lines = [f"*`{name}`: {g['pairs']} pairs from {g['trajectories']} trajectories.*",
             f"- **Pair level** (`pair_level`, n = {g['pair_level']['f_star_K']['n']}, each pair one unit):"]
    lines += level_lines(g["pair_level"])
    lines.append(f"- **Trajectory level** (`trajectory_level`, n = {g['trajectory_level']['f_star_K']['n']}, each trajectory's median):")
    lines += level_lines(g["trajectory_level"])
    return "\n".join(lines)


def hs(hs_list) -> str:
    return "none" if not hs_list else ", ".join(f"`{h}`" for h in hs_list)


# what the classes hold
if F["same_offset"] is None:
    assert F["different_offset"] == F["all"]
    CLASS_TEXT = (f"no read pair is SAME-OFFSET: `same_offset` is null, and `different_offset` holds the same "
                  f"{F['all']['pairs']} pairs and the same figures as `all`, which are given once below.")
    BLOCKS = block_text("all", F["all"]) + "\n\n" + block_text("same_offset", None)
elif F["different_offset"] is None:
    assert F["same_offset"] == F["all"]
    CLASS_TEXT = (f"no read pair is DIFFERENT-OFFSET: `different_offset` is null, and `same_offset` holds the same "
                  f"{F['all']['pairs']} pairs and the same figures as `all`, which are given once below.")
    BLOCKS = block_text("all", F["all"]) + "\n\n" + block_text("different_offset", None)
else:
    CLASS_TEXT = "both classes hold read pairs; each is given apart below, then pooled."
    BLOCKS = "\n\n".join(block_text(c, F[c]) for c in ("same_offset", "different_offset", "all"))
ZERO_COLS = [k for k in ("matched_in_common_prefix", "repeated_key_tokens") if all(x[k] == 0 for x in PP)]
FSTAR_POS = sum(1 for x in PP if x["f_star_K"] > 0)
OVER_TAU = sum(1 for x in PP if x["tokens_over_tau_K"] > 0)
DOS = sorted(x["different_offset_share"] for x in PP)
DOS_TEXT = (f"`different_offset_share` is {f4(DOS[0])} for every read pair: every matched token is at a different offset."
            if DOS[0] == DOS[-1] == 1 else f"`different_offset_share` runs from {f4(DOS[0])} to {f4(DOS[-1])}.")
TAB1 = ["| `handoff` | `ended_by_itself` | `matched` | `matched_share_of_reused` | `different_offset_share` | `sender_tokens` | "
        "`a_tokens` | `receiver_tokens` | `continuation_tokens` |" + "".join(f" `{k}` |" for k in ("matched_in_common_prefix", "repeated_key_tokens") if k not in ZERO_COLS),
        "|---|---|---|---|---|---|---|---|---|" + "---|" * (2 - len(ZERO_COLS))]
for x in PP:
    TAB1.append(f"| `{x['handoff']}`{' (probe)' if x['probe'] else ''} | {str(x['ended_by_itself']).lower()} | {n(x['matched'])} | "
                f"{f4(x['matched_share_of_reused'])} | {f4(x['different_offset_share'])} | {n(x['sender_tokens'])} | "
                f"{n(x['a_tokens'])} | {n(x['receiver_tokens'])} | {n(x['continuation_tokens'])} |"
                + "".join(f" {n(x[k])} |" for k in ("matched_in_common_prefix", "repeated_key_tokens") if k not in ZERO_COLS))
TAB2 = ["| `handoff` | `f_star_K` | `tokens_over_tau_K` | `max_token_mean_K` | REUSE mean KL | REUSE p90 KL | REUSE top-1 | "
        "RANDOM mean KL | RANDOM p90 KL | RANDOM top-1 | CYCLIC mean KL | CYCLIC p90 KL | CYCLIC top-1 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for x in PP:
    TAB2.append(f"| `{x['handoff']}` | {f4(x['f_star_K'])} | {n(x['tokens_over_tau_K'])} | {f4(x['max_token_mean_K'])} | "
                + " | ".join(f4(x[f"{arm}_{k}"]) for arm, _ in ARMS for k in STATS) + " |")
ZERO_TEXT = ("" if not ZERO_COLS else " " + " and ".join(f"`{k}`" for k in ZERO_COLS)
             + (" is" if len(ZERO_COLS) == 1 else " are") + " 0 for every read pair, so the table leaves "
             + ("it" if len(ZERO_COLS) == 1 else "them") + " out.")
CC_ID = CC["identity"]
EXCL_TEXT = "; ".join(f'"{k}" {F["exclusions"][k]}' for k in EXCLUSIONS)
EXCL_NAMED = "; ".join(f'"{k}": {hs(F["excluded"][k])}' for k in EXCLUSIONS if F["excluded"][k])
QTEXT = "; ".join(f"`{st}`: {len(v)} ({', '.join(f'`{t}`' for t in v)})" for st, v in F["questions"].items())
A_ = F["all"]["pair_level"]


def count_word(c: int) -> str:
    return "one" if c == 1 else str(c)


def places(ks: list) -> str:
    return (f"pair {ks[0]}" if len(ks) == 1 else
            f"each of pairs {', '.join(str(k) for k in ks[:-1])} and {ks[-1]}")


# the resume's warnings, by count, each with the places (in the order read) of the pairs that hold it
_by = {}
for _k, _c in enumerate(OOM_PAIR[1:], start=2):
    if _c:
        _by.setdefault(_c, []).append(_k)
_none = len(OOM_PAIR) - 1 - sum(len(v) for v in _by.values())
OOM_RESUME = ", ".join(f"{count_word(c)} on {places(ks)}" for c, ks in sorted(_by.items())) or "none"
OOM_RESUME += (f", and none on the other {_none} of the {len(OOM_PAIR) - 1} pairs it read" if _by and _none else "")
OVER_CAP = F["exclusions"]["over the cap"]

RAW = f"""### {NUM} — {a.date} — Cache reading of the Finance Agent run's paired helper sub-calls ran `[BASELINE, DESCRIPTIVE]`: next-token sensitivity of Qwen3-1.7B to reading a logged helper sub-call with its matched document states taken from one earlier sub-call of the same trajectory, fresh vs reused with RANDOM and CYCLIC controls, and the oracle removal fraction at τ_K, over {F['read']} pairs from {F['all']['trajectories']} trajectories; descriptive, no band, no hypothesis row, no cell moves

**What this reports.** The reading 0076 registers (line {L76['head']}), with the window end 0077 sets (line {L77['head']}), reported field by field under 0076's names. Every figure below is filled by this entry's script from the summary of record and the six records beside it, each named next. The summary of record is `summary.json` (sha256 `{SUMMARY_SHA256[:12]}…`), which the driver's own `--summarize` wrote from the output tree copied off the reading machine, with the code at `{READ_COMMIT[:12]}`; the script checks that it holds the same values, and the same bytes up to line ends, as the `summary.json` the reading machine wrote, and recomputes every median, p10 and p90 below from the summary's per-pair rows by the repository's one convention (0013). Beside it the script reads, each pinned by sha256, the driver's report (sha256 `{REPORT_SHA256[:12]}…`), the lock `launch.json` (sha256 `{LOCK_SHA256[:12]}…`), the log of the launches (sha256 `{CHAIN_LOG_SHA256[:12]}…`), the record of the inputs' removal (sha256 `{REMOVAL_SHA256[:12]}…`), and the driver's own logs of the first launch (sha256 `{PROBE_LOG_SHA256[:12]}…`) and of the resume (sha256 `{RUN_LOG_SHA256[:12]}…`). None of these files is committed, and none holds any text of the Finance Agent run's logs. As 0076 asks (line {L76['label']}), every figure carries its label: "{F['label']}". As 0076 asks (line {L76['ccpass']}), since the control ran and passed, every f* carries "{F['cross_check_label']}". **No band, no hypothesis row, no `verdict:` line, no cell moves.** As 0076 fixes (line {L76['nointerval']}), no interval is reported: p10 and p90 are the spread of the pairs' or of the trajectories' values.

**The window and the questions.** 0076 reads a question only if every one of its launches had ended by the window end (line {L76['window']}); 0077 moved that end from 2026-11-20T12:00:00Z to {CFG['window_end']} (line {L77['window']}), the `window_end` of the config the reading ran. `questions` names the run's {NQ} public questions under their statuses: {QTEXT}.

**The manifest, its lock and the launches.** As 0076 asks (line {L76['names']}): the lock, the report and the log of the launches name one manifest, built at `built` {F['built']}, sha256 `{MANIFEST[:12]}…`, the digest in the report's identity and in the lock, and its first twelve digits in the log's identity line. Its lock, `launch.json`, written at the first launch at {LOCK['at']}, holds the cross-check branch `{LOCK['branch']}` and the wall-time limit {LOCK['stop_at']} (`stop_at`). The driver was launched twice on that manifest, each launch its first attempt, and both exited 0: the first, at {T_FIRST}, ran the cross-instrument control and the probe pair, and a resume, at {T_RESUME}, read the other {F['read'] - 1} pairs in the registered order; both times are the reading machine's clock, as the log of the launches records them. No step was under way at a resume or at the end (`ended_in_flight` is empty), and nothing was relaunched.

**Candidates, exclusions and the selection.** As 0076 asks (line {L76['counts']}), with the manifest's digest above: {F['candidates']} candidate pairs (`candidates`), {F['eligible']} eligible (`eligible`). The exclusions, in 0076's order (line {L76['excl']}): {EXCL_TEXT}. Named (`excluded`): {EXCL_NAMED}. As 0076 asks (line {L76['cap']}), the pairs the cap leaves out hold {f4(F['over_the_cap_matched_share'])} of all candidate pairs' matched tokens (`over_the_cap_matched_share`), and 0075's two counts at the cap, summed over the {W['trajectories']} measured in-window trajectories, are {n(W['reused_in_capped_prompts'])} (`reused_in_capped_prompts`) and {n(W['reused_in_capped_pairs'])} (`reused_in_capped_pairs`). {F['selected']} pairs are selected (`selected`), the registered order's first {F['selected']}, under the ceiling of {CEILING}. As 0076 asks (line {L76['readcount']}), {F['read']} of them are read (`read`); no selected pair is unread (`not_read` is empty), and the wall-time limit did not stop the sitting (`stopped` is null).

**The cross-instrument control.** Run first, as 0076 registers (line {L76['cc']}), on 0049's probe handoff `{CC['handoff']}` (`cross_check`, branch `{F['cross_check']['branch']}`): over {n(CC['matched'])} matched tokens, {n(CC['tokens_outside_tolerance'])} lie outside the per-token tolerance (`tokens_outside_tolerance`), the largest gap is {CC['max_gap']:.6f} (`max_gap`), {f4(CC['max_gap_over_bound'])} of its token's bound (`max_gap_over_bound`); f* is {f4(CC['f_star_driver'])} by the driver and {f4(CC['f_star_archive'])} by the archive; {n(CC['tokens_over_tau_K_driver'])} and {n(CC['tokens_over_tau_K_archive'])} tokens are over τ_K (driver, archive; recorded, not gated); the driver's K deviation mean is {f4(CC_ID['deviation_means']['K'])} against the archive's {f4(CC['archived_mean']['K'])} (`identity`, `archived_mean`). `passed` is {str(CC['passed']).lower()}, after {CC['minutes']:.1f} minutes (`minutes`).

**The probe, the controls and the stop.** The probe pair, read first by size as 0076 asks (line {L76['probe']}), is `{F['probe_pair']}` (`probe_pair`), flagged `probe` in the per-pair rows. On it alone ran the controls 0076 keeps from 0047 (line {L76['controls']}), as the report records them: the fresh repeat reproduced the first FRESH pass's logits exactly, as 0076 requires (line {L76['fresh']}), with a largest logit error of {CTRL['fresh_repeat']['max_logit_error']:g} (`fresh_repeat`, `max_logit_error`), and the prefix copy over {CFG['prefix_control_tokens']} tokens has a largest logit error of {CTRL['prefix_copy']['max_logit_error']:.6f} (`prefix_copy`, `max_logit_error`), within the 0.0005 that 0076 sets (line {L76['prefixcopy']}). The reading is complete (`complete` true). The summary records the attention slice as "{S['attention']}", and the report the archive bridge as "{REP['archive_bridge']}", as 0076 provides.

**Allocator warnings.** The driver's logs of the two launches hold {OOM_TOTAL} `CUDACachingAllocator` warnings ("{OOM_PHRASE}"). The driver prints the control's line once its result is written and a pair's progress line once its score is written, so each warning is counted on the step whose line follows it, and a pair by its place in the order read (the order of the per-pair tables below). In the first launch, {count_word(OOM_CONTROL)} during the cross-instrument control and {count_word(OOM_PAIR[0])} on the probe pair, pair 1; in the resume, {sum(OOM_PAIR[1:])}: {OOM_RESUME}. None raised an error: neither log holds a traceback, both launches exited 0, and all {F['read']} selected pairs were read. 0076's stopping rule is 0047's (line {L76['stoprule']}): "{STOP_QUOTE}". By the operator's ruling (2026-11-11, restated 2026-11-13, and for this run on 2026-11-22) the reading given for 0061's run carries to this one. Verbatim, as 0070 quotes it (line {L70}): "{RULING}" What held: the cross-instrument control passed, with {n(CC['tokens_outside_tolerance'])} of its {n(CC['matched'])} matched tokens outside the per-token tolerance; on the probe pair the fresh repeat reproduced the first FRESH pass's logits exactly and the prefix copy stayed within 0.0005; and the summary the driver's own `--summarize` wrote from the output tree copied off the reading machine holds the same values as the one the reading machine wrote.

**The sitting.** One {ID['gpu']}, torch {ID['torch']}, transformers {ID['transformers']}, CUDA {ID['cuda']}, `CUBLAS_WORKSPACE_CONFIG={ID['cublas_workspace_config']}`, from the report's identity; the reader `{REP['model']}` at revision `{REP['model_revision'][:12]}…`, YaRN {REP['rope']['factor']}; the code at `{READ_COMMIT[:12]}` (the report's `git_commit`), whose config, `run.py`, `core.py` and `fab_pairs.py` have the sha256 0077 and 0076 pin (`{PINS['config/cache-behavior-fab.toml'][1][:12]}…`, `{PINS['tools/cache_behavior/run.py'][1][:12]}…`, `{PINS['tools/cache_behavior/core.py'][1][:12]}…`, `{PINS['tools/cache_behavior/fab_pairs.py'][1][:12]}…`), in the report's identity and in the tree at this entry's append. As 0076 registers (line {L76['removed']}), the inputs were removed from the reading machine: the removal record, which ends at {REMOVED_AT}, finds no copy and no folder of them left. As 0076 registers (line {L76['private']}), the per-pair arrays and the probe pair's witness rows stay private with the output tree.

**Summary.** As 0076 fixes it (line {L76['summary']}), over the read pairs, median (p10, p90). As 0076 asks (line {L76['classes']}), the two classes apart and pooled: {CLASS_TEXT}

{BLOCKS}

**Per pair (`per_pair`), in the order read.** The structure of each pair, with A's prefill through the cut (`sender_tokens`) of `a_tokens` in all, B (`receiver_tokens`) and the continuation (`continuation_tokens`).{ZERO_TEXT} {DOS_TEXT}

{chr(10).join(TAB1)}

The readings of each pair: f* and the tokens over τ_K, the largest token mean, and each arm's mean KL, p90 KL and top-1 agreement. f* is above 0 in {FSTAR_POS} of the {F['read']} read pairs, and {OVER_TAU} have at least one token over τ_K.

{chr(10).join(TAB2)}

**Reading.** These figures say only what they are: next-token sensitivities of Qwen3-1.7B, a reader that is not the serving model, on {F['read']} pairs of one run's logged helper prompts, read with matched document states taken from an earlier sub-call of the same trajectory, teacher-forced on the serving model's logged responses; at the pair level REUSE's median mean KL is {f4(A_['reuse_mean_kl']['median'])} with median top-1 agreement {f4(A_['reuse_top1_agreement']['median'])}, RANDOM's {f4(A_['random_mean_kl']['median'])} and {f4(A_['random_top1_agreement']['median'])}, CYCLIC's {f4(A_['scrambled_mean_kl']['median'])} and {f4(A_['scrambled_top1_agreement']['median'])}, and the median f* is {f4(A_['f_star_K']['median'])}. They are descriptive. No financial task outcome was measured, and no free generation by the reader was read; they come from one run of one harness, on the questions of 0076's window, within the cap, which leaves {OVER_CAP} of the {F['candidates']} candidate pairs, holding {f4(F['over_the_cap_matched_share'])} of all candidate pairs' matched tokens, over it and not read.

**What stands beside what.** As 0076 states (line {L76['beside']}), this cell stands beside 0049's 35-handoff REUSE-ALL row, on the same axis, and is never pooled with it; the differences 0076 lists remain, with the window as 0077 sets it.

**What this does NOT touch.** Every cell and verdict; τ, the rule and the bands; entries 0047, 0049, 0069, 0070, 0075, 0076, 0077 and 0078, their configs and records; every other output tree; the figure set 0072 lists.

**Consequences in this commit set.** The cell's heading in `docs/agent/experiment-commands.md`, which now reads that it ran, with figures in {NUM}, and the drafts README's allocator. Nothing under `results/`.

**Scope.** As 0076 states it (line {L76['scope']}): one reader, Qwen3-1.7B at YaRN 2.5, cap 81,920; one run of one serving model, on the public questions in the window; pairs within a trajectory; fixed logged text, so KL and top-1 agreement are not task outcomes; same-model only; no second reader. A descriptive outcome, not a verdict.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard 0076 and 0077 present, {PREV} last, {NUM} absent. Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""
NB = "\u0000"


def wrap(par: str) -> str:
    """One paragraph at width 120; a code span is never broken across lines. Lists and tables are not wrapped."""
    par = re.sub(r"`[^`]*`", lambda m: m.group(0).replace(" ", NB), " ".join(par.split()))
    return "\n".join(ln.replace(NB, " ") for ln in textwrap.wrap(par, width=120, break_long_words=False, break_on_hyphens=False))


assert NB not in RAW, "the entry text holds the wrap's placeholder"
_paras = RAW.split("\n\n")
assert _paras[0].startswith(f"### {NUM} ") and "\n" not in _paras[0] and _paras[-1] == "prior-entries-sha256: PLACEHOLDER\n"
_out = [_paras[0]]
for _p in _paras[1:-1]:
    _out.append(_p if (_p.startswith("|") or _p.startswith("*`") and "\n- " in _p or _p.startswith("*`") and "\n" not in _p) else wrap(_p))
_out.append(_paras[-1])
ENTRY = "\n\n".join(_out)
assert ENTRY.endswith("prior-entries-sha256: PLACEHOLDER\n") and ENTRY.count("PLACEHOLDER") == 1, "the chain line is not the entry's last"
for _bad in ("usd", "$", "C:/", "C:\\", "/c/Users", "hossa", "/workspace", "runpod", "RunPod", "SECURE", "COMMUNITY", "watchdog"):
    assert _bad not in ENTRY, f"the entry holds {_bad!r}"
assert "FILL" not in ENTRY and "UNVERIFIED" not in ENTRY and not re.search(r"\bnan\b|\binf\b", ENTRY, re.I), "a FILL, NaN or inf"

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print("[ordering guard: ok]")
    raise SystemExit(0)


# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included -----------------------------------
def ledger_check():
    code = (f"import sys; sys.path.insert(0, {str(R / 'src')!r}); "
            "from linear_ceiling.ledger_check import main; sys.exit(main())")
    return subprocess.run([sys.executable, "-I", "-c", code], cwd=R, capture_output=True, text=True, env=ENV)


at_head = git("show", "HEAD:ledger/ledger.md")
assert text == at_head.decode("utf-8").replace("\r\n", "\n"), "ledger/ledger.md is not HEAD's: an uncommitted edit"
assert git("status", "--porcelain", "--", "ledger/ledger.md").strip() == b"", "ledger/ledger.md is modified in the working tree"
r0 = ledger_check()
assert r0.returncode == 0 and r0.stdout.strip().endswith(LEDGER_OK), f"ledger_check before the write: {(r0.stdout + r0.stderr).strip()[-400:]}"
assert "prior-entries-sha256: PLACEHOLDER" not in text, "the ledger already holds a placeholder chain line"
base = text + ("" if text.endswith("\n") else "\n") + "\n"
digest = chain_hash(base + ENTRY, len(base), _ENTRIES_HEAD.search(base).start())
new = base + ENTRY.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
assert new.startswith(text) and new.count(f"\n### {NUM} ") == 1 and new.index(f"\n### {NUM} ") + 1 == len(base), "the new ledger is not the old one plus this entry"
# --- the write, and after it: ledger_check, else the old bytes go back ----------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
