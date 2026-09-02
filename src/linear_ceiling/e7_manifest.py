"""The E7 corpus manifest -- committed provenance for a corpus that never enters history.

`traces/` is gitignored and `results/` is gitignored, so before this module the "188 trace
files hashed" that the ledger cites lived only in the driver's own report, on one machine.
The manifest is the committed record of exactly which bytes E7 measured:

- one record per file the corpus walk touches (`e7_corpus.discover_files` order): suite,
  submission or agent, task instance where the layout names one, path under `traces/`,
  sha256 of the bytes, byte size;
- for SWE-bench objects, the S3 key, ETag and size as returned by the anonymous listing of
  `s3://swe-bench-submissions/verified/<submission>/trajs/` (entry 0005's "every suite carries
  its version" rule, met for S3 objects by the listing's own identity fields), and the listing
  time;
- per submission, the SELECTION record: which instances of the full listing are present
  locally, and whether a stated rule reproduces that set (first-N in listing order, first-N in
  sorted-id order, or none). The rule is RECOVERED from the two sets, never assumed, and a
  set no rule reproduces is recorded as `rule: null` -- "hand-selected; rule not recoverable".

The driver refuses to run and the summarizer refuses to summarize when the manifest and the
disk disagree in any direction: a file on disk that the manifest does not list, a listed file
absent from disk, or a listed file whose bytes hash differently. Each refusal names the path.

The manifest's own identity is `manifest_sha256`: the canonical-JSON hash (`hashing`), not
the on-disk bytes, so a CRLF checkout and an LF checkout agree. Every E7 report from entry
0024 on carries it beside `config_sha256`, and `ledger_check` requires every E7 entry from
0024 on to cite it (`e7-manifest-sha256:`).

`python -m linear_ceiling.e7_manifest write` reads the local tree and the S3 listing (network,
once; the file is the artifact). `... check` verifies disk against the committed manifest.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, load_e7_config
from linear_ceiling.e7_corpus import agent_of_submission, discover_files
from linear_ceiling.e7_tau2 import agent_of, read_tau2
from linear_ceiling.hashing import canonical_bytes, hash_json_file, sha256_file_bytes

SCHEMA = 1
BUCKET = "swe-bench-submissions"
S3_BASE = f"https://{BUCKET}.s3.amazonaws.com/"
_S3NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
_EXT = re.compile(r"(_traj)?\.[A-Za-z0-9]+$")

RULES = ("first-N in listing order", "first-N in sorted-id order")


def manifest_path(cfg: E7Config) -> Path:
    """Beside the config by convention (`config/e7-manifest.json`); the config itself is
    unchanged so its registered sha256 (entries 0013-0022) still identifies the same file."""
    return cfg.manifest_path if cfg.manifest_path is not None else cfg.config_path.parent / "e7-manifest.json"


def manifest_sha256(path: Path) -> str:
    return hash_json_file(path)


# --- local records --------------------------------------------------------------------------

def _instance_of(rel_under_submission: str) -> str:
    """`astropy__astropy-12907_traj.json` -> `astropy__astropy-12907`;
    `inst-2/attempt_0/patching_agent.json` -> `inst-2` (nested layout: the instance is the dir)."""
    head = rel_under_submission.split("/", 1)[0]
    return head if "/" in rel_under_submission else _EXT.sub("", head)


def local_records(cfg: E7Config) -> list[dict]:
    """One record per file, in `discover_files` order, from the bytes on disk."""
    root = Path(cfg.traces_dir).resolve()
    out = []
    for f in discover_files(cfg.traces_dir):
        rel = f.resolve().relative_to(root).as_posix()
        suite = rel.split("/", 1)[0]
        rec = {"suite": suite, "path": rel, "sha256": sha256_file_bytes(f), "bytes": f.stat().st_size}
        if suite == "tau-bench":
            rec["agent"] = f.stem.rsplit("-", 1)[0]
        elif suite == "tau2-bench":
            rec["agent"] = agent_of(read_tau2(f))
        elif suite == "swe-bench":
            sub, rest = rel.split("/", 2)[1:]
            rec["submission"] = sub
            rec["agent"] = agent_of_submission(sub)
            rec["instance"] = _instance_of(rest)
        out.append(rec)
    return out


# --- S3 listing -----------------------------------------------------------------------------

def list_s3(prefix: str, opener=urllib.request.urlopen) -> list[dict]:
    """Every object under `prefix` in the anonymous listing, paginated; listing order is the
    bucket's (UTF-8 binary key order)."""
    keys, token = [], None
    while True:
        url = f"{S3_BASE}?list-type=2&prefix={urllib.parse.quote(prefix)}&max-keys=1000"
        if token:
            url += "&continuation-token=" + urllib.parse.quote(token, safe="")
        with opener(url, timeout=60) as r:
            root = ET.fromstring(r.read())
        for c in root.findall("s3:Contents", _S3NS):
            keys.append({"key": c.find("s3:Key", _S3NS).text,
                         "etag": (c.find("s3:ETag", _S3NS).text or "").strip('"'),
                         "size": int(c.find("s3:Size", _S3NS).text),
                         "last_modified": c.find("s3:LastModified", _S3NS).text})
        trunc = root.find("s3:IsTruncated", _S3NS)
        if trunc is None or trunc.text != "true":
            return keys
        token = root.find("s3:NextContinuationToken", _S3NS).text


def s3_prefix(submission: str) -> str:
    return f"verified/{submission}/trajs/"


def selection(local_instances: list[str], listing: list[dict], prefix: str) -> dict:
    """Which instances of the full listing are present locally, and which stated rule (if
    any) reproduces that set. Instances are the first path segment after the prefix, in
    listing order, de-duplicated (the nested layout has many objects per instance)."""
    order, seen = [], set()
    for k in listing:
        rest = k["key"][len(prefix):]
        inst = _instance_of(rest)
        if inst not in seen:
            seen.add(inst)
            order.append(inst)
    local = sorted(set(local_instances))
    n = len(local)
    missing = sorted(set(local) - seen)
    rule = None
    if not missing and n:
        if local == sorted(order[:n]):
            rule = RULES[0]
        elif local == sorted(order)[:n]:
            rule = RULES[1]
    return {"n_local": n, "s3_instances": len(order), "s3_objects": len(listing),
            "rule": rule, "listing_positions": [order.index(i) for i in local if i in seen],
            "not_in_listing": missing}


def annotate_s3(records: list[dict], list_fn=list_s3) -> tuple[list[dict], dict]:
    """Attach S3 identity to every SWE-bench record and build the per-submission selection
    block. Refuses on a local file the listing does not contain: such a file cannot be
    reproduced from the public bucket and must not be silently carried."""
    subs = sorted({r["submission"] for r in records if r["suite"] == "swe-bench"})
    listings = {s: list_fn(s3_prefix(s)) for s in subs}
    by_key = {s: {k["key"]: k for k in listings[s]} for s in subs}
    out = []
    for r in records:
        r = dict(r)
        if r["suite"] == "swe-bench":
            sub = r["submission"]
            rest = r["path"].split("/", 2)[2]
            key = s3_prefix(sub) + rest
            obj = by_key[sub].get(key)
            if obj is None:
                raise ValueError(f"{r['path']}: no such object in the S3 listing ({key}); a local file the "
                                 "public bucket does not contain is not reproducible provenance")
            r["s3"] = {"bucket": BUCKET, "key": key, "etag": obj["etag"], "size": obj["size"],
                       "last_modified": obj["last_modified"]}
        out.append(r)
    sel = {}
    for s in subs:
        local = [r["instance"] for r in records if r["suite"] == "swe-bench" and r["submission"] == s]
        sel[s] = selection(local, listings[s], s3_prefix(s))
    return out, sel


# --- build / write / load / verify ------------------------------------------------------------

def build(cfg: E7Config, list_fn=list_s3, now=None) -> dict:
    records = local_records(cfg)
    sel: dict = {}
    listed_at = None
    if list_fn is not None and any(r["suite"] == "swe-bench" for r in records):
        records, sel = annotate_s3(records, list_fn)
        listed_at = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    return {"schema": SCHEMA,
            "traces_dir": "traces",
            "files": records,
            "n_files": len(records),
            "s3": {"bucket": BUCKET, "listing": "anonymous ListObjectsV2, key order",
                   "listed_at_utc": listed_at},
            "swe_bench_selection": sel,
            "selection_note": "rule RECOVERED from local set vs full listing; null = hand-selected, "
                              "rule not recoverable. Listing order is UTF-8 key order, so first-N in "
                              "listing order is the alphabetically-first N instances."}


def write(cfg: E7Config, list_fn=list_s3, now=None) -> Path:
    p = manifest_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(canonical_bytes(build(cfg, list_fn, now)))
    return p


def load(cfg: E7Config) -> dict:
    p = manifest_path(cfg)
    if not p.exists():
        raise ValueError(f"no corpus manifest at {p}; run `python -m linear_ceiling.e7_manifest write` and "
                         "commit it before any trajectory is measured")
    m = json.loads(p.read_text(encoding="utf-8"))
    if m.get("schema") != SCHEMA or not isinstance(m.get("files"), list):
        raise ValueError(f"{p}: not a schema-{SCHEMA} corpus manifest")
    return m


def verify_disk(cfg: E7Config, manifest: dict) -> None:
    """Disk vs manifest, both directions plus bytes. Refuses naming the first offending path."""
    root = Path(cfg.traces_dir).resolve()
    on_disk = {f.resolve().relative_to(root).as_posix(): f for f in discover_files(cfg.traces_dir)}
    listed = {r["path"]: r for r in manifest["files"]}
    if len(listed) != len(manifest["files"]):
        raise ValueError("manifest lists a path twice")
    extra = sorted(set(on_disk) - set(listed))
    if extra:
        raise ValueError(f"trace file on disk is not in the manifest: {extra[0]}")
    gone = sorted(set(listed) - set(on_disk))
    if gone:
        raise ValueError(f"trace file in the manifest is missing on disk: {gone[0]}")
    for rel in sorted(listed):
        if sha256_file_bytes(on_disk[rel]) != listed[rel]["sha256"]:
            raise ValueError(f"trace file does not match the manifest hash: {rel}")


def selection_lines(manifest: dict) -> list[str]:
    """Human-readable selection record, one line per submission (rendered by the summarizer)."""
    sel = manifest.get("swe_bench_selection") or {}
    if not sel:
        return ["SWE-bench selection: no S3 listing recorded in the manifest"]
    out = [f"SWE-bench selection vs the S3 listing (listed {manifest['s3'].get('listed_at_utc')}):"]
    for s, v in sorted(sel.items()):
        rule = v["rule"] or "hand-selected; rule not recoverable"
        pos = v["listing_positions"]
        span = f"positions {pos[0]}..{pos[-1]}" if pos else "no positions"
        out.append(f"- {s}: {v['n_local']} of {v['s3_instances']} listed instances "
                   f"({v['s3_objects']} objects); rule: {rule}; {span}"
                   + (f"; NOT IN LISTING: {v['not_in_listing']}" if v["not_in_listing"] else ""))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e7_manifest")
    ap.add_argument("cmd", choices=("write", "check"))
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--no-s3", action="store_true", help="write without the S3 listing (no selection record)")
    a = ap.parse_args(argv)
    cfg = load_e7_config(Path(a.config), REPO_ROOT)
    try:
        if a.cmd == "write":
            p = write(cfg, None if a.no_s3 else list_s3)
            m = load(cfg)
            print(f"wrote {p}: {m['n_files']} files; sha256 {manifest_sha256(p)}")
            for line in selection_lines(m):
                print(line)
        else:
            m = load(cfg)
            verify_disk(cfg, m)
            print(f"manifest ok: {m['n_files']} files match disk; sha256 {manifest_sha256(manifest_path(cfg))}")
        return 0
    except ValueError as e:
        print(f"E7 MANIFEST REFUSED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
