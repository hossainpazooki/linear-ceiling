"""docs/drafts/append_0055.py (the E-TRUNC registration) on a synthetic checkout: the preview states every figure
from the alignment passes it finds, and it refuses out of order, on a config that is not the registered one, and
on anything under a level's results tree (R1). Retire with the script in the append commit."""
import io
import json
import runpy
import shutil
import sys
from contextlib import redirect_stdout

import numpy as np
import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import _stem
from linear_ceiling.hashing import sha256_text_file
from tests.test_summarize_e9_trunc import _block_pairs, _level_pairs

DRAFT = REPO_ROOT / "docs" / "drafts" / "append_0055.py"
H = ["20241016_composio_swekit/astropy__astropy-7671_traj#85", "20241025_composio_swekit/django__django-10554_traj#112",
     "20241025_composio_swekit/django__django-11087_traj#152"]
NS = {H[0]: 34974, H[1]: 66991, H[2]: 80111}
NR = {H[0]: 5000, H[1]: 9000, H[2]: 12000}
LEDGER_STUB = """# Ledger

## Entries

### 0025 — 2026-09-02 — stub
**Coverage, registered (review finding 1).** 0019's alignment: **25 included of 68 observed** (39 excluded).

### 0035 — 2026-09-09 — stub

### 0036 — 2026-09-10 — stub
Launched 2026-09-09T23:53:12Z, finished 2026-09-10T01:13:09Z.

### 0037 — 2026-09-13 — stub
Every "what length changes" figure in the paper (outline v3 §5.2) is therefore length AND
configuration.

### 0038 — 2026-09-14 — stub
(long − native)). Far-from-seam (16+) median δ_K: native 0.0195, scaled 0.0381, long
0.0629 → share 0.4285.

### 0054 — 2026-10-04 — stub
"""
RUNBOOK_STUB = """# runbook stub
  The measured peak at the longest included |S| is **31.56 GiB**, 8% above the seed's estimate.
- 00:11–01:12 scored 7 → 34/35 at 1.5–3 min per handoff (the puller's round log).
"""


def _root(tmp_path):
    (tmp_path / "config").mkdir()
    for name in ("e9t-full", "e9t-l65", "e9t-l49", "e9t-l32", "e9l"):
        shutil.copy(REPO_ROOT / "config" / f"{name}.toml", tmp_path / "config" / f"{name}.toml")
    (tmp_path / "ledger").mkdir()
    (tmp_path / "ledger" / "ledger.md").write_text(LEDGER_STUB, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "2026-09-10-e9l-gpu-runbook.md").write_text(RUNBOOK_STUB, encoding="utf-8")
    for cell in ("e9s", "e9l"):
        (tmp_path / "results" / cell).mkdir(parents=True)
    (tmp_path / "results" / "e9s" / "compare.json").write_text(json.dumps({
        "n_handoffs": 25, "configuration_share": {"seam_far": 0.4285},
        "seam_profile_left_pooled": [{"bin": "16+", "n_tokens": 10, "median_native": 0.0195, "median_scaled": 0.0381}]}), encoding="utf-8")
    (tmp_path / "results" / "e9l" / "summary.json").write_text(json.dumps({
        "coverage": {"included": 35, "scored": 35},
        "seam_profile_left_pooled": {"same_K": [{"bin": "16+", "n_tokens": 10, "median": 0.0629}]}}), encoding="utf-8")
    full = load_e9_config(tmp_path / "config" / "e9t-full.toml", tmp_path)
    # H[0] |S| 34,974: one block near its end, cut only by L32; H[1] 66,991 and H[2] 80,111: cut by every level
    pairs = {H[0]: _block_pairs(30000, 100, 3000), H[1]: _block_pairs(40000, 200, 20000), H[2]: _block_pairs(50000, 300, 25000)}
    for name, L in (("e9t-full", None), ("e9t-l65", 65536), ("e9t-l49", 49152), ("e9t-l32", 32768)):
        cfg = load_e9_config(tmp_path / "config" / f"{name}.toml", tmp_path)
        ad = cfg.results_dir / "align"
        ad.mkdir(parents=True)
        recs = []
        for hid in H:
            pr = pairs[hid] if L is None else _level_pairs(pairs[hid], NS[hid], L)
            np.savez(ad / f"{_stem(hid)}.npz", sender=np.zeros(1), receiver=np.zeros(1), pairs=pr)
            recs.append({"handoff_id": hid, "n_sender": NS[hid], "n_receiver": NR[hid], "n_matched": int(len(pr)),
                         "excluded": False, "reason": None, "text_sha256": f"t-{hid}"})
        recs.append({"handoff_id": "x/y_traj#1", "n_sender": 200000, "n_receiver": 10, "n_matched": 0, "excluded": True,
                     "reason": "S exceeds context cap 81920", "text_sha256": "t-x"})
        recs.append({"handoff_id": "x/z_traj#1", "n_sender": 20000, "n_receiver": 10, "n_matched": 0, "excluded": True,
                     "reason": "S and R within context floor 32768 (decided under the prior cap)", "text_sha256": "t-z"})
        cov = {"config_sha256": sha256_text_file(cfg.config_path), "context_cap": 81920, "context_floor": 32768,
               "rope": full.rope, "coverage": {"observed": 5, "included": 3, "excluded": 2},
               "exclusion_reasons": sorted({r["reason"] for r in recs if r["excluded"]}),
               "run_order": [H[2], H[1], H[0]], "order_by": "n_sender_desc", "keep_subset": [H[0], H[1], H[2]],
               "alignments": recs}
        if L is not None:
            cov["sender_head_truncate"] = L
        (ad / "coverage.json").write_text(json.dumps(cov), encoding="utf-8")
    return tmp_path


def _run(root):
    sys.argv = [str(DRAFT), "--preview", "--repo-root", str(root), "--date", "2026-10-05"]
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            runpy.run_path(str(DRAFT), run_name="draft")
        except SystemExit as e:
            assert e.code == 0, e.code
    return buf.getvalue()


def test_preview_states_the_registration_from_the_alignment_passes(tmp_path):
    root = _root(tmp_path)
    out = _run(root)
    assert out.startswith("### 0055 — 2026-10-05 — E-TRUNC registered before any prefill")
    assert "\nverdict:" not in out and "prior-entries-sha256: PLACEHOLDER" in out
    # the rulings, verbatim
    assert "±0.005 absolute on the far-from-seam (16+) same-K *median*, as entry 0038 reports it" in out
    assert "an absolute floor (|M_∩| ≥ 2,000) beside the ratio" in out and "include it, keep R under YaRN, and state so" in out
    # figures read from the fixture, not typed: 3 included; two handoffs over 65,536; every one over 32,768
    assert "5 observed · 3 included · 1 excluded as decided" in out      # the entry wraps after "decided"
    assert "under the prior cap · 1 excluded above the cap · 0 excluded for an empty receiver prompt" in out
    assert "L65536 (L = 65,536: 2 of 3 handoffs differ from FULL)" in out and "L32768 (L = 32,768: 3 of 3 handoffs differ from FULL)" in out
    assert "`django__django-11087_traj#152` (80,111) first, `astropy__astropy-7671_traj#85` (34,974)" in out
    assert "0.0381" in out and "0.0629" in out and "0038 (line 18)" in out and "0037 (line 14)" in out and "0025 (line 6)" in out
    assert "in 80 minutes (0036)" in out and "31.56 GiB" in out and "1.5–3 min per handoff" in out
    assert "handoffs are void under the floor" in out and "× E9-long's" in out
    # H[0]'s block at 30,000..32,999 of |S| 34,974 survives L32 (offset 2,206) whole; H[2]'s 50,000..74,999 of 80,111 keeps
    # the 25,000 - (47,343 - 50,000 < 0 -> all)... every pair above the offset: the counts are arithmetic on the fixture
    assert "0 of 3 handoffs are void under the floor" in out
    # the budget is arithmetic on the coverage: FULL = 2*sum|S| + sum|R|
    assert f"FULL {2 * sum(NS.values()) + sum(NR.values()):,} tokens" in out
    assert "0052 / 0053) and 0054" in out


def test_refuses_out_of_order_an_unregistered_config_and_a_prior_run(tmp_path):
    root = _root(tmp_path)
    led = root / "ledger" / "ledger.md"
    led.write_text(led.read_text(encoding="utf-8") + "\n### 0055 — 2026-10-05 — already there\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="ordering"):
        _run(root)
    led.write_text(LEDGER_STUB, encoding="utf-8")
    cfg = root / "config" / "e9t-l32.toml"
    src = cfg.read_text(encoding="utf-8")
    cfg.write_text(src.replace("sender_head_truncate = 32768", "sender_head_truncate = 30000"), encoding="utf-8")
    with pytest.raises(AssertionError, match="not the registered config"):
        _run(root)
    cfg.write_text(src, encoding="utf-8")
    (root / "results" / "e9t-l49" / "report.json").write_text("{}", encoding="utf-8")
    with pytest.raises(AssertionError, match="before registration"):
        _run(root)
    (root / "results" / "e9t-l49" / "report.json").unlink()
    cov_p = root / "results" / "e9t-full" / "align" / "coverage.json"
    cov = json.loads(cov_p.read_text(encoding="utf-8"))
    cov_p.write_text(json.dumps(cov | {"config_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(AssertionError, match="another config"):
        _run(root)
