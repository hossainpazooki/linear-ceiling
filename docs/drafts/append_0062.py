"""Append entry 0062 -- REGISTER, before any operator prefill, the L32-NATIVE cell: entry 0055's L32 level (the sender
head-truncated to S' = S[-32768:], the same 35 handoffs of entry 0036, inclusion decided on the full |S| under the
81,920 cap) with BOTH models under their native RoPE -- no [e9.rope], no [e9.bridge] -- paired token by token with the
L32 YaRN level entry 0057 ran, on the subset matched under every E-TRUNC level (M_cap). Operator ruling A of 2026-10-13
(private design, ~/dev/briefs/2026-10-13-linear-ceiling-experimental-gaps-plan.md, sections 8-9), which supersedes the
WORDING of 0055's ruling 3 ("keep R under YaRN"): every dump of this cell sits inside the receiver's declared native
window, read below, so no sender-native / receiver-scaled instrument is needed. DESCRIPTIVE: no hypothesis row, no
`verdict:` line, no band, no cell moves.

Ordering guard: 0061 present, 0062 absent. Refuses unless the config, the instrument files and the two reference records
are in the tree at the hashes below (text files hashed newline-normalized, as the ledger cites configs), the alignment
check passes in-process, and nothing exists under the registered output trees but the alignment passes (R1).

  --date YYYY-MM-DD   --preview   --repo-root <path>
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.config import load_e9_config                       # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file  # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402
from linear_ceiling.summarize_e9_native import NATIVE, alignment_check, load_cells  # noqa: E402

NUM, PREV = "0062", "0061"
TRUNC_REG, TRUNC_RUN, LONG, SHORT_CMP = "0055", "0057", "0036", "0038"
CONFIG_SHA = "5e01f133c3c02146ce32bbd4556b3a7d0ce91e0053b4762d8c760272842594da"      # config/e9t-l32n.toml
L32_SHA = "3c0663fbb651ad50e01389822263c67ae85bb78198d58aaf0333a3c6771dadaa"         # config/e9t-l32.toml, 0055's, unchanged
FULL_SHA = "005d8d102deb743e2de66c62b884dfa5b602e3308a0e7960cc2260bb1de11f7f"        # config/e9t-full.toml, 0055's, unchanged
NATIVE_READER_SHA = "7741fe19fb20b3b74d8f2d5e93b5acfb93518ec29e075705f7899cc4a8026b11"  # src/linear_ceiling/summarize_e9_native.py
SUMMARIZER_SHA = "12a645af2315d803703e26146f1045966bb8a4fb58306a174207aae63f10d9ff"     # src/linear_ceiling/summarize_e9.py (the window control)
CONFIG_PY_SHA = "56ef7e845ed26f19db7ea93ec184b3399d7b9ce6f9db2e50d10c8500d5adc77c"      # src/linear_ceiling/config.py ([e9.native])
TRUNC_CMP_SHA12, SHORT_CMP_SHA12 = "0572662307f3", "a0699a826f1f"   # results/e9t/compare.json (0057), results/e9s/compare.json (0038)
L32_COVERAGE_SHA12 = "d07606d8d3e8"     # results/e9t-l32/align/coverage.json, on the ledger in 0055
RECEIVER, RECEIVER_REV = "Qwen/Qwen3-1.7B", "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"   # the revision entry 0047 pins
OUTPUT, OUT_CMP = "results/e9t-l32n", "results/e9tn"

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
if f"### {PREV} " not in text:
    # The append waits for 0061 (ruling F: both entries before the sitting). A preview may run while 0061 is still staged,
    # and says so; the append never does.
    assert a.preview and (R / "docs" / "drafts" / f"append_{PREV}.py").exists(), f"ordering: {PREV} present, {NUM} absent"
    print(f"[preview] {PREV} is staged, not appended; the append refuses until it is", file=sys.stderr)
for e in (TRUNC_REG, TRUNC_RUN, LONG, SHORT_CMP):
    assert f"### {e} " in text, f"{e} must be on the ledger"
for s in (L32_COVERAGE_SHA12, TRUNC_CMP_SHA12, SHORT_CMP_SHA12, L32_SHA[:12], FULL_SHA[:12]):
    assert f"`{s}" in text, f"{s} is not on the ledger as expected"

pins = {"config/e9t-l32n.toml": CONFIG_SHA, "config/e9t-l32.toml": L32_SHA, "config/e9t-full.toml": FULL_SHA,
        "src/linear_ceiling/summarize_e9_native.py": NATIVE_READER_SHA, "src/linear_ceiling/summarize_e9.py": SUMMARIZER_SHA,
        "src/linear_ceiling/config.py": CONFIG_PY_SHA}
for rel, sha in pins.items():
    assert (R / rel).exists(), f"{rel} missing"
    assert sha256_text_file(R / rel) == sha, f"{rel} is not the file this entry pins"
assert (R / "tests" / "test_summarize_e9_native.py").exists(), "the paired reader is untested"
cfg = load_e9_config(R / "config" / "e9t-l32n.toml", R)
yarn = load_e9_config(R / "config" / "e9t-l32.toml", R)
assert cfg.rope is None and cfg.bridge is None and cfg.sender_head_truncate == 32768 == yarn.sender_head_truncate
assert cfg.required_entries == yarn.required_entries + (NUM,), "[e9.gate] must end at this entry"
assert cfg.native["margin_abs"] == 0.005 and cfg.native["trunc_compare"] == "results/e9t/compare.json" \
    and cfg.native["short_native_compare"] == "results/e9s/compare.json"
cells, yarn_name = load_cells(cfg, R)
assert yarn_name == "L32768"

# R1: nothing under this entry's trees but the alignment passes and the alignment check.
out = R / OUTPUT
assert not any((out / f).exists() for f in ("report.json", "summary.json", "scores", "tokens", "controls", "scratch")), f"{out} holds a run; refusing"
assert not (R / OUT_CMP / "compare.json").exists(), f"{OUT_CMP} holds a comparison; refusing"

# Every count below is READ: the alignment check in-process over the five passes, the two reference records by hash, and
# the receiver's declared window from its pinned config.json (borrowed fact, {Qwen/Qwen3-1.7B, config.json, 70d244cc86cc}).
chk = alignment_check(cells, yarn_name)
assert chk["n_handoffs"] == chk["n_identical_to_yarn"] == 35 and chk["min_common_matched"] == 2000
assert chk["cells"]["L32768"]["coverage_sha256"][:12] == L32_COVERAGE_SHA12, "e9t-l32's alignment pass is not the one 0055 cites"
trunc_p, short_p = R / "results" / "e9t" / "compare.json", R / "results" / "e9s" / "compare.json"
assert sha256_file_bytes(trunc_p)[:12] == TRUNC_CMP_SHA12 and sha256_file_bytes(short_p)[:12] == SHORT_CMP_SHA12, "reference records off-hash"
trunc, short = json.loads(trunc_p.read_text(encoding="utf-8")), json.loads(short_p.read_text(encoding="utf-8"))
assert trunc["n_used"] == chk["n_used"] and trunc["n_void"] == chk["n_void"] and sorted(trunc["void"]) == chk["void"] \
    and trunc["n_common_total"] == chk["n_common_total"], "M_cap here is not 0057's"
YARN_FAR = float(trunc["reading"]["far_from_seam_median_on_M_cap"])
SHORT_SCALED, LONG_LEVEL = float(trunc["reading"]["short_scaled_level"]), float(trunc["reading"]["long_level"])
SHORT_NATIVE = float(next(r["median_native"] for r in short["seam_profile_left_pooled"] if r["bin"] == "16+"))
assert trunc["reading"]["reads_as"] == "unattributed" and trunc["reading"]["level"] == yarn_name
from huggingface_hub import hf_hub_download     # noqa: E402  (cache hit when the receiver is present; one small file otherwise)
rcfg = json.loads(Path(hf_hub_download(RECEIVER, "config.json", revision=RECEIVER_REV)).read_text(encoding="utf-8"))
WINDOW = int(rcfg["max_position_embeddings"])
assert chk["max_dumped_length"] <= WINDOW < cfg.context_cap, "the cell's premise: every dump inside the native window, the cap above it"
NATIVE_COV_SHA12 = chk["cells"][NATIVE]["coverage_sha256"][:12]

s12 = lambda s: s[:12]  # noqa: E731
ENTRY = f"""### {NUM} — {a.date} — E-TRUNC, the L32-NATIVE cell registered before any prefill: entry {TRUNC_REG}'s L32 level with both models under their native RoPE, paired with the L32 YaRN level of entry {TRUNC_RUN} on the same tokens; descriptive, no band, no cell moves

**Why, and why now.** Entry {TRUNC_RUN} read the L32 level's far-from-seam median on M_cap at {YARN_FAR:.4f}, above both the
scaled-short level {SHORT_SCALED:.4f} and the long level {LONG_LEVEL:.4f} (read from `results/e9t/compare.json` `{TRUNC_CMP_SHA12}…`), and
read it as UNATTRIBUTED. Every E-TRUNC level ran the receiver under {LONG}'s YaRN, so the record cannot say whether a
truncated sender at the native cap would read the same under a receiver that is NOT scaled -- whether the L32 excess is
the handoffs' or the scaled receiver's. Entry {TRUNC_REG}'s ruling 3 said "include it, keep R under YaRN, and state so" and
deferred the cell for want of a sender-native / receiver-scaled instrument. Operator ruling A (2026-10-13) takes both sides
NATIVE instead, and the alignment passes show that needs no new dump instrument: the longest dumped LENGTH of this
cell is {chk['max_dumped_length']:,} (the dumped sender at most {chk['max_dumped_sender']:,}, plus one for the prefix control; |R| at most
{chk['max_n_receiver']:,}), inside the receiver's declared window of {WINDOW:,} (`max_position_embeddings`, `{RECEIVER}` `config.json` at
revision `{s12(RECEIVER_REV)}…`, the revision entry 0047 pins; the sender's model, which dumps S' for the cross arm, is read the same way
off its own dumps at summary time), while the 81,920 cap is for inclusion only (decided on the FULL |S|, {TRUNC_REG}).
This entry registers that cell and the two reader changes it needs, before any prefill.

**What is registered, by hash (text files newline-normalized, as the ledger cites configs).** `config/e9t-l32n.toml`
(`{s12(CONFIG_SHA)}…`): `config/e9t-l32.toml` (`{s12(L32_SHA)}…`, {TRUNC_REG}'s, unchanged) byte for byte except the results and
scratch directories, `[e9.gate]` (ends at this entry), the `[e9.rope]` and `[e9.bridge]` blocks REMOVED, and an `[e9.native]`
block naming the FULL cell (`config/e9t-full.toml` `{s12(FULL_SHA)}…`, whose `[e9.trunc]` defines M_cap, the |M_cap| ≥ 2,000 floor
and the 16+ bin), the YaRN level it pairs with, the margin (±0.005, as {TRUNC_REG} ruling 1), the two reference records and the
bootstrap (seed 62, 2,000 reps). Same pair, pin `{cfg.upstream_sha[:12]}`, rule, τ, ladder, controls, seam bins, block floor, keep
draw, mapper, profiles, cap 81,920, floor 32,768, `sender_head_truncate = 32768`, longest sender first with the partial
close allowed. Instrument: (i) `summarize_e9` (`{s12(SUMMARIZER_SHA)}…`) -- on a cell that registers a truncation and no
`[e9.rope]`, and on no other, the native-window control compares the longest DUMPED length over the scored handoffs (S'
plus one, or R, read from the alignment records) to each dump's recorded `max_position_embeddings` instead of the cap,
and the summary states which basis it read; every existing cell's summary is unchanged. (ii) `[e9.native]` in `config.py`
(`{s12(CONFIG_PY_SHA)}…`): refused on any cell without a truncation, or with a rope or a bridge. (iii) `summarize_e9_native`
(`{s12(NATIVE_READER_SHA)}…`), the paired reader, tested on synthetic cells (`tests/test_summarize_e9_native.py`).

**Alignment, read from the passes (CPU, before any prefill).** `results/e9t-l32n/align/coverage.json` (`{NATIVE_COV_SHA12}…`):
68 observed · 35 included · 33 excluded, the same as every E-TRUNC level; the native cell's matched set equals the L32
level's (`{L32_COVERAGE_SHA12}…`) on **{chk['n_identical_to_yarn']} of {chk['n_handoffs']}** handoffs, {chk['n_matched_total']:,} matched tokens, by construction (the same
S', the same R, the same aligner; the reader refuses otherwise rather than intersecting). M_cap under the four E-TRUNC
levels: **{chk['n_used']} enter, {chk['n_void']} void** under the floor, {chk['n_common_total']:,} common tokens -- exactly {TRUNC_RUN}'s used set, void set and
token count, so the native level is read on the tokens {TRUNC_RUN}'s reading was read on.

**The reading, fixed now (descriptive).** The far-from-seam (16+, FULL's causal seam frame) pooled MEDIAN δ_K of the
native level on M_cap over the non-void handoffs, against two levels read from the record, never typed: {SHORT_CMP}'s
NATIVE-short far-from-seam median, {SHORT_NATIVE:.4f} (`results/e9s/compare.json` `{SHORT_CMP_SHA12}…`, `median_native`), and {TRUNC_RUN}'s
YaRN-L32 median on M_cap, {YARN_FAR:.4f}, recomputed by the reader on the same tokens and refused if it is not the record's.
Within ±0.005 of the native-short level: the L32 excess reads as **THE SCALING** (the YaRN receiver accounts for it);
within ±0.005 of the YaRN-L32 level: **NOT THE SCALING** (a native receiver reproduces it); between: **UNATTRIBUTED**, said
so. The two levels sit {abs(YARN_FAR - SHORT_NATIVE):.4f} apart, so the margin cannot span both. Beside it: the paired difference
native − YaRN per handoff (mean δ_K over M_cap), median over handoffs with the seeded bootstrap; each cell's mean δ_K,
tokens over τ_K, f* on the ladder and far-from-seam median on M_cap. A run closed partial (longest sender first) compares
on the commonly scored prefix: the YaRN level is recomputed on those tokens and read against, with the record's figure
over its full used set stated beside it. No hypothesis cell moves; H-E9L and every verdict stand.

**The registered run (the operator's).** Requested only after this entry is committed, on the same card as entry {PREV}'s
(ruling F). `e9 --check --config config/e9t-l32n.toml` requires 0019/0023/0025/0027/0035/{TRUNC_REG}/{NUM} committed, the
config committed unmodified, the upstream at `{cfg.upstream_sha[:12]}` clean, the mapper by sha. R2–R8 of
`docs/gpu-experiment-protocol.md`; output tree `results/e9t-l32n/` (report, scores, per-token records, controls, three
kept dumps), mirrored home, verified and backed up before the figures entry. Then `summarize_e9_native`: `summarize_e9` on the
native cell and on the L32 level (fail-closed, the gate; the native-window control on basis "dumped_length"), the paired
comparison, `results/e9tn/compare.{{json,md}}`. The figures enter by their own entry, every number read from those files.

**Gate and enforcement.** This script refuses if any pinned file differs, if the alignment check fails in-process, if
M_cap here is not {TRUNC_RUN}'s, if the premise above fails against the pinned `config.json`, or if `results/e9t-l32n/` or
`results/e9tn/` holds anything but the alignment passes and the alignment check's own output (R1).

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries {LONG}, {SHORT_CMP}, {TRUNC_REG}, {TRUNC_RUN} and their
records; `config/e9t-{{full,l65,l49,l32}}.toml` and `results/e9t*/` as they stand; the E9 driver; `summarize_e9_trunc`.

**Scope.** One receiver, one pair, one corpus, the 35 long handoffs at one truncation level; the native-short reference
is a different cohort (0038's 25 handoffs, pooled over their full matched sets) while the YaRN-L32 reference is the same
tokens; both models native, so the cell says nothing about a sender-native / receiver-scaled pairing; descriptive.

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
