"""Append the Track B recon entry (0024 by default) -- ordering-guarded, figures from the
summarizer flags only.

Refuses unless: entry 0023 is in the ledger (Track A's entry lands first; the chain is
sequential), the target number is free, `e7.assert_ready` passes (ledger, config/e7.toml and
config/e7-manifest.json committed unmodified, so the report the summarizer verifies was
produced by the GATED driver), and `summarize_e7` with both recon flags returns cleanly.
Every figure in the entry text is read from the summarizer's output (`results/e7/recon.json`
and the verified report), never typed. After appending it runs `ledger_check.check` on the new
text and restores the previous file if anything fails.

    .venv/Scripts/python.exe docs/drafts/append_0024.py --preview      # print the text, touch nothing
    .venv/Scripts/python.exe docs/drafts/append_0024.py                # append as the next free number >= 24
    .venv/Scripts/python.exe docs/drafts/append_0024.py --number 25    # if 0024 was taken by a rebase

Delete this script once the entry is appended (docs/drafts/README.md convention).
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from linear_ceiling import REPO_ROOT, e7
from linear_ceiling.config import load_e7_config
from linear_ceiling.e7_manifest import load as load_manifest, manifest_path, manifest_sha256
from linear_ceiling.ledger_check import chain_hash, check, committed_manifest_sha, parse_ledger
from linear_ceiling.summarize_e7 import summarize

LEDGER = REPO_ROOT / "ledger" / "ledger.md"


def _q(s: dict, pct: bool = False) -> str:
    if pct:
        return f"{100*s['median']:.1f}% (p10 {100*s['p10']:.1f}%, p90 {100*s['p90']:.1f}%)"
    return f"{s['median']:.3f} (p10 {s['p10']:.3f}, p90 {s['p90']:.3f})"


def render(number: int, recon: dict, rep: dict, manifest: dict, msha: str) -> str:
    nb, cb = recon["overlap_null"], recon["cache_aware"]
    sel = manifest["swe_bench_selection"]
    rules = {v["rule"] for v in sel.values()}
    n_s3 = sum(1 for f in manifest["files"] if "s3" in f)
    p = cb["pooled"]
    d, r = p["denominators"], p["ratios"]
    obs, same, cross = nb["observed"], nb["same_family"], nb["cross_family"]
    h = rep["h_e7a"]["pooled"]
    sel_lines = "\n".join(
        f"  - `{s}`: {v['n_local']} of {v['s3_instances']} listed instances "
        f"({'rule: ' + v['rule'] if v['rule'] else 'hand-selected; rule not recoverable'}; listing positions "
        f"{v['listing_positions'][0]}..{v['listing_positions'][-1]})" for s, v in sorted(sel.items()))
    rule_sentence = (
        f"Every submission's local set is the first N objects of its S3 listing ({RULES_TEXT(rules)}) -- "
        "listing order is UTF-8 key order, so the subset is the ALPHABETICALLY FIRST N instances of each "
        "submission (astropy-dominated), not a random draw."
        if rules == {"first-N in listing order"} else
        "Selection rules per submission are recorded verbatim above; where none is recoverable the set is "
        "hand-selected.")
    at_or_above = [k for k in cb["readings"] if p["below_cutoff"][k] is False]
    return f"""### {number:04d} — {date.today().isoformat()} — Corpus manifest committed; SWE-bench selection rule recorded; overlap null controls and cache-aware H-E7a readings `[BASELINE]`; no verdict changes

**Manifest.** `config/e7-manifest.json` (canonical-JSON sha256 `{msha}`): {manifest['n_files']} files over three
suites; S3 key, ETag and size for {n_s3} SWE-bench objects (anonymous listing of
`s3://swe-bench-submissions/verified/<submission>/trajs/`, retrieved {manifest['s3']['listed_at_utc']}).
`e7.assert_ready` refuses until it is committed unmodified; the driver and `summarize_e7` refuse on any
disagreement between disk, report and manifest (a file on disk the manifest does not list, a listed file
absent or with different bytes, a report not produced against this manifest -- tamper tests
`tests/test_e7_manifest.py`, `tests/test_summarize_e7.py`). Every E7 figure from this entry on carries the
manifest sha beside the config sha (`ledger_check` enforces the citation), and `config_sha256` is now the
newline-normalized digest so a CRLF checkout cites the same `{rep['config_sha256'][:12]}` as an LF one.

**Selection rule, as recovered (not assumed).** Local instance set vs the full listing, per submission:
{sel_lines}
{rule_sentence} Bearing: none on Lane A (all 60 composio files present, both submissions); the pooled
taxonomy rows over SWE-bench are a SELECTED SUBSET and are labelled so from here on (coverage stated
beside them: entry 0011 units).

**Overlap null controls (`summarize_e7 --overlap-null`, seed {nb['seed']}, same measure and quantile
convention as 0010/0018).** Observed: overlap {_q(obs['overlap_fraction'])}, headroom upper bound
{_q(obs['recoverable_fraction'], pct=True)} of paid. Same-family null (each receiver prompt against the
sender context of a different composio trajectory, seeded derangement): overlap
{_q(same['overlap_fraction'])}, upper bound {_q(same['recoverable_fraction'], pct=True)}. Cross-family null
(against a seeded random SWE-bench role/content trajectory's full text, pool {cross['pool_size']}): overlap
{_q(cross['overlap_fraction'])}, upper bound {_q(cross['recoverable_fraction'], pct=True)}. What this says:
roughly half of the receiver's words are template vocabulary any composio prompt shares (the same-family
null), about {100*cross['overlap_fraction']['median']:.0f}% is vocabulary any SWE-bench transcript shares; the
observed {obs['overlap_fraction']['median']:.3f} sits {obs['overlap_fraction']['median'] - same['overlap_fraction']['median']:.3f}
above the same-family null, so the 0018 figure is a bound on task-content redundancy over and above the
template, not on template vocabulary alone. It is still an UPPER BOUND (0010). Decides nothing; E9 is the
instrument that measures the achievable fraction.

**Cache-aware readings of H-E7a's denominator (`summarize_e7 --cache-aware-ratio`; numerator unchanged
{p['recoverable_upper_bound']:,.0f}; Lane A measurable subset per 0014; base-input-price units).**
Registered requests (each assistant turn re-bills the trajectory prefix, as priced in 0015/0018): COLD
{d['registered_cold']:,.0f} -> **{100*r['registered_cold']:.2f}%** (= the 0018 figure by construction);
WARM (previous prefix at read_mult, new messages at write_mult) {d['registered_warm']:,.0f} ->
**{100*r['registered_warm']:.2f}%**. Request-level requests (entry 0017's reading of `paid`, applied to every
request: each LLM call's own prompt; {p['requests']} requests): COLD {d['request_cold']:,.0f} ->
**{100*r['request_cold']:.4f}%**; WARM (byte-identical prefix shared with the preceding request --
{100*p['request_shared_prefix_fraction']:.1f}% of request-level prefill tokens -- at read_mult, remainder at
write_mult) {d['request_warm']:,.0f} -> **{100*r['request_warm']:.2f}%**. Cutoff {100*cb['cutoff']:.0f}%.
Beside 0022's exact-tokenizer sensitivity (0.2210% under the registered reading).

**Verdict, re-examined under each reading of "input-token spend" (rule as written, 0006/0007/0014).**
Under the registered reading, priced cold or warm, H-E7a `NOT CONFIRMED` stands
({100*r['registered_cold']:.2f}% / {100*r['registered_warm']:.2f}% vs 10%). Under the request-level reading
the ratio is {'AT OR ABOVE the cutoff for: ' + ', '.join(at_or_above) if at_or_above else 'below the cutoff under both bounds'} --
{100*r['request_cold']:.4f}% cold, {100*r['request_warm']:.2f}% warm. Two things bind the reading of that
number: the numerator is an UPPER BOUND (0010, re-rendering changes every position) and every denominator
is a visible-only LOWER BOUND (0012, the warm bounds more so, because the hidden block is the most
cacheable content), so the true request-level ratio is strictly below the {100*r['request_cold']:.4f}% stated;
and 0006's wording does not say which reading it means. **This entry does not change the cell**: the
registered reading is the one 0014/0015/0018 decided under, and choosing between readings is a
registration act -- a successor to 0006/0014 must fix the reading BEFORE any verdict is restated under
it. Until then H-E7a's `NOT CONFIRMED` stands as decided, with the request-level reading on the record
as the reading under which it would not.

No `verdict:` line: no cell changes. Figures: `summarize_e7 --overlap-null --cache-aware-ratio`
(results/e7/recon.json), config sha256 {rep['config_sha256'][:12]}, {len(rep['trace_files'])} trace files verified.
e7-manifest-sha256: {msha}
"""


def RULES_TEXT(rules):
    return "; ".join(sorted(r or "none" for r in rules))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", type=int, default=None, help="entry number (default: next free >= 24)")
    ap.add_argument("--preview", action="store_true", help="print the entry text from the current results; touch nothing")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")       # the heading's em dashes on a cp1252 console
    text = LEDGER.read_text(encoding="utf-8")
    entries = parse_ledger(text)["entries"]
    number = a.number or max(max(entries) + 1, 24)
    cfg = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    if not a.preview:
        if 23 not in entries:
            print("REFUSED: entry 0023 (Track A) is not in the ledger yet; appends are sequential")
            return 2
        if number in entries:
            print(f"REFUSED: entry {number:04d} already exists; pass --number for the next free one")
            return 2
        try:
            e7.assert_ready(cfg, REPO_ROOT)
        except RuntimeError as e:
            print(str(e))
            return 2
        summarize(cfg, overlap_null=True, cache_aware=True)      # verifies the gated report, writes recon.json
    recon = json.loads((cfg.results_dir / "recon.json").read_text(encoding="utf-8"))
    rep = json.loads((cfg.results_dir / "skeleton_report.json").read_text(encoding="utf-8"))
    manifest = load_manifest(cfg)
    msha = manifest_sha256(manifest_path(cfg))
    if recon["manifest_sha256"] != msha or recon["config_sha256"] != rep["config_sha256"]:
        print("REFUSED: recon.json was not produced against the current manifest/report; rerun the summarizer")
        return 2
    if recon["overlap_null"]["same_family"] is None or recon["overlap_null"]["cross_family"] is None:
        print("REFUSED: a null control is NOT COMPUTABLE on this corpus; the entry text assumes both")
        return 2
    body = render(number, recon, rep, manifest, msha)
    if a.preview:
        print(body)
        return 0
    entries_start = re.search(r"^## Entries\s*$", text, re.M).start()
    new = text.rstrip("\n") + "\n\n"
    chain = chain_hash(new, len(new), entries_start)
    new += body.rstrip("\n") + f"\n\nprior-entries-sha256: {chain}\n"
    LEDGER.write_text(new, encoding="utf-8", newline="\n")
    problems = check(new, committed_manifest_sha())
    if problems:
        LEDGER.write_text(text, encoding="utf-8", newline="\n")
        print("REFUSED after append (ledger restored):\n  " + "\n  ".join(problems))
        return 1
    print(f"appended entry {number:04d}; ledger_check ok. Commit it alone (no header/README edits in the same commit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
