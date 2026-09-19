"""The second model family's configs (config/e8f.toml, config/e9f.toml, config/e9fl.toml): what they
register, and -- mostly -- what they REFUSE.

tau is 1 - THIS pair's archived held-out R^2. The Llama mapper has not been fitted and cannot be fitted
here, so the THREE calibrated tolerances carry refusing UNRESOLVED markers instead of numbers and both E9
configs fail to load at all. That is the point of the cell as staged, so it is pinned here key by key
rather than left to a convention someone could tidy away by pasting the Qwen values in -- which would
load, run, and produce a verdict calibrated against another pair's mapper. These tests must NOT assert
`c.rule == e9.rule` the way tests/test_e9_long.py:52 does for the Qwen cells: three of those values
belong to Qwen and must never appear here. The other two formerly-"derived" keys (tau_ladder,
prefix_invariance_max_delta) were registered ABSOLUTE and identical to Qwen's by the 2026-09-18 ruling,
and are asserted EQUAL rather than asserted-to-be-markers."""
import re
import tomllib

import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling import e8 as e8_driver
from linear_ceiling import e9 as e9_driver
from linear_ceiling.config import load_e8_config, load_e9_config
from linear_ceiling.e9_pertoken import SEAM_BIN_EDGES
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.pairs import pair_models

PAIR = "llama3.2-3b-to-llama3.1-8b"
MODELS = ("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B")
E9_NAMES = ("e9f", "e9fl")
# The THREE keys derived from this pair's own held-out R^2. Only these can carry a refusing marker,
# because only these are unknowable before the fit. tau_ladder and prefix_invariance_max_delta were
# once listed here as "registered functions of tau_K"; the 2026-09-18 ruling registered them ABSOLUTE
# and identical to config/e9.toml -- the ladder so a Llama f*(0.03) is comparable with entry 0029's,
# the prefix bound because it is a float32 kernel-noise floor and not a property of the mapper -- so
# they are now asserted EQUAL to E9's by the not-tau-derived branch below, which is a stricter check
# than "is a marker", not a looser one.
TAU_KEYS = ("tau_K", "tau_V", "tau_agent_K")
# Stand-ins used ONLY to get past one refusal so the next can be tested. Deliberately unlike any value in
# config/e9.toml: nothing in this file may hand a Llama config a Qwen number, not even in a tmp copy.
STANDIN = {"tau_K": "0.25", "tau_V": "0.31", "tau_agent_K": "0.42"}
# config/e9.toml's calibrated values, verbatim. None may appear in a Llama config in any form.
QWEN_TAU = ("0.3186442653116294", "0.4867056499055992", "0.4371020133925453")


def _text(name):
    return (REPO_ROOT / "config" / f"{name}.toml").read_text(encoding="utf-8")


def _toml(name):
    return tomllib.loads(_text(name))["e9" if name.startswith("e9") else "e8"]


def _resolve(text, *, leave=()):
    """Substitute a stand-in for every tau-derived marker but those named in `leave`."""
    for key, value in STANDIN.items():
        if key in leave:
            continue
        text, n = re.subn(rf'(?m)^{key} = "UNRESOLVED::[^"]*"$', f"{key} = {value}", text)
        assert n == 1, f"{key}: expected exactly one refusing marker line, found {n}"
    return text


def _resolved_cfg(tmp_path, name, *, leave=(), extra=""):
    p = tmp_path / f"{name}.toml"
    p.write_text(_resolve(_text(name), leave=leave) + extra, encoding="utf-8")
    return load_e9_config(p, REPO_ROOT)


# ---- E8 on the second family ---------------------------------------------------------------------------

def test_e8f_registers_the_second_family_and_carries_0016s_sampling_rule_unchanged():
    c = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
    e8 = load_e8_config(REPO_ROOT / "config" / "e8.toml", REPO_ROOT)
    assert c.pair == PAIR and pair_models(c.pair) == MODELS
    assert c.results_dir.name == "e8f" and c.tokens_dir.name == "e8f"
    assert c.results_dir != e8.results_dir and c.tokens_dir != e8.tokens_dir   # a new dir, or the emptiness gate reads Qwen's
    assert c.upstream_path == e8.upstream_path                                # ONE clone, moved per cell
    # the instrument is 0009/0016's, unchanged; only the pair, the dirs, the scope and the pin differ
    assert c.text == e8.text and c.band == e8.band
    assert (c.verdict_k, c.report_k, c.holdout_frac, c.stride) == (e8.verdict_k, e8.report_k, e8.holdout_frac, e8.stride)
    assert c.generic_dumps == f"data/kv/{PAIR}" and c.generic_dumps != e8.generic_dumps
    assert c.mapper_tag is None and c.amendment is None and c.agent_holdout_frac is None
    # [e8.gate] is ADDITIVE: 0009 and 0016 are still required, plus this family's registration
    assert c.gate == ("0039",)
    assert e8_driver.required_entries(c) == e8_driver.REQUIRED_ENTRIES + ("### 0039 ",)
    assert e8_driver.required_entries(e8) == e8_driver.REQUIRED_ENTRIES and e8.gate == ()
    # the recorded scope states the truth about this pair; Qwen's report keeps e8.py's literal
    assert c.scope_note is not None and "Llama-3" in c.scope_note and "matched-KV" in c.scope_note
    assert e8.scope_note is None and c.scope_note != e8_driver.DEFAULT_SCOPE


def test_e8f_carries_a_real_pin_and_still_refuses_one_that_does_not_hold():
    """Commit P is recorded (2026-09-18), so the placeholder refusal no longer applies -- but the pin
    must still be ENFORCED, which is the property that actually matters. Asserting against a
    well-formed sha that is not in the checkout keeps this independent of which commit the single
    local clone happens to be detached at."""
    c = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
    assert re.fullmatch(r"[0-9a-f]{40}", c.upstream_sha), "commit P's sha must be recorded in full"
    assert "UNRESOLVED" not in c.upstream_sha
    bogus = c.__class__(**{**c.__dict__, "upstream_sha": "0" * 40})
    with pytest.raises(RuntimeError, match="REFUSED"):
        e8_driver.assert_ready(bogus, REPO_ROOT)


# ---- the refusals that keep E9-Llama from running before the E8 fit -------------------------------------

@pytest.mark.parametrize("name", E9_NAMES)
def test_llama_e9_config_refuses_outright_until_tau_is_calibrated(name):
    """The whole cell is unreachable: no driver, gate or summarizer can hold this config at all."""
    with pytest.raises(ValueError, match="tau_K must be a calibrated number"):
        load_e9_config(REPO_ROOT / "config" / f"{name}.toml", REPO_ROOT)


@pytest.mark.parametrize("name", E9_NAMES)
@pytest.mark.parametrize("key,msg", [("tau_K", "tau_K must be a calibrated number"),
                                     ("tau_V", "tau_V must be a calibrated number"),
                                     ("tau_agent_K", "tau_agent_K must be a calibrated number")])
def test_each_tau_derived_key_refuses_on_its_own_marker(tmp_path, name, key, msg):
    """Not one refusal shadowing two: resolve the other two and the remaining marker still refuses, so
    no single paste can smuggle a cell through."""
    with pytest.raises(ValueError, match=msg):
        _resolved_cfg(tmp_path, name, leave=(key,))


@pytest.mark.parametrize("name", E9_NAMES)
@pytest.mark.parametrize("line,bad,msg", [
    ("tau_ladder = [0.10, 0.03]", "tau_ladder = [0.03, 0.10]", "tau_ladder must be a strictly decreasing"),
    ("tau_ladder = [0.10, 0.03]", "tau_ladder = [0.9, 0.03]", "tau_ladder"),
    ("prefix_invariance_max_delta = 1e-4", "prefix_invariance_max_delta = -1.0",
     "prefix_invariance_max_delta must be in"),
])
def test_the_absolute_keys_are_still_validated_not_merely_present(tmp_path, name, line, bad, msg):
    """They stopped being markers, so prove they did not stop being CHECKED. Each is written absolute
    (ruling 2026-09-18), but config.py must still reject a ladder that is not strictly decreasing, a
    rung outside (0, tau_K), and a non-positive prefix bound -- otherwise "absolute" would have quietly
    meant "unvalidated", which is how a wrong constant survives to a verdict."""
    text = _text(name)
    assert text.count(line) == 1, f"{name}.toml no longer carries {line!r} verbatim"
    p = tmp_path / f"{name}.toml"
    p.write_text(_resolve(text.replace(line, bad)), encoding="utf-8")
    with pytest.raises(ValueError, match=msg):
        load_e9_config(p, REPO_ROOT)


@pytest.mark.parametrize("name", ("e8f", "e9f", "e9fl"))
def test_no_qwen_tau_constant_appears_in_any_llama_config(name):
    text = _text(name)
    for value in QWEN_TAU:
        assert value not in text, f"config/{name}.toml carries config/e9.toml's {value}"
    # The COMMENTS may name Qwen -- several must, to say what does not carry over (0029's included set,
    # 0036's band, the "Qwen3 native" justification for 32,768) -- but no VALUE may.
    values = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    assert "qwen" not in values.lower(), f"config/{name}.toml names the Qwen pair in a value, not a comment"


@pytest.mark.parametrize("name", E9_NAMES)
def test_rule_and_controls_are_e9s_on_every_key_that_is_not_tau_derived(name):
    """What tests/test_e9_long.py asserts as `c.rule == e9.rule` for the Qwen cells, key by key here --
    because three of those keys are this pair's own calibration and cannot exist yet. The other two
    formerly-"derived" keys are asserted EQUAL here, by the else branch, exactly as registered."""
    llama, e9 = _toml(name), _toml("e9")
    for section in ("rule", "controls"):
        assert llama[section].keys() == e9[section].keys()
        for key, value in e9[section].items():
            if key in TAU_KEYS:
                assert isinstance(llama[section][key], str) and llama[section][key].startswith("UNRESOLVED::")
                assert PAIR in llama[section][key]      # the marker names the pair whose R^2 is missing
            else:
                assert llama[section][key] == value, f"{name}.toml [e9.{section}] {key} is not E9's"
    assert llama["controls"]["seam_bins"] == list(SEAM_BIN_EDGES)
    assert llama["mapper"] == e9["mapper"] and llama["alignment"] == e9["alignment"]
    assert llama["keep"]["seed"] == e9["keep"]["seed"]


# ---- the long cell: a NATIVE receiver, not a scaled one -------------------------------------------------

def test_e9fl_is_a_native_receiver_cell_and_carries_no_rope_and_no_bridge():
    fl = _toml("e9fl")
    assert "rope" not in fl and "bridge" not in fl          # both models are natively 131,072
    assert fl["handoffs"]["context_cap"] == 81920 and fl["handoffs"]["context_floor"] == 32768
    assert fl["order"] == {"by": "n_sender_asc", "allow_partial": True}
    assert fl["keep"]["n"] == 3
    # the position bins are re-cut at Llama's own boundary: 8,192 is llama3 scaling's
    # original_max_position_embeddings, the same on both sides despite the differing factors
    assert fl["profiles"]["s_pos_edges"] == [0, 8192, 32768, 65536]
    assert 8192 in fl["profiles"]["s_pos_edges"] and 49152 not in fl["profiles"]["s_pos_edges"]
    # the two Llama cells partition their handoffs exactly, with no gap and no overlap
    assert _toml("e9f")["handoffs"]["context_cap"] == fl["handoffs"]["context_floor"]
    assert "rope" not in _toml("e9f")


def test_e9fl_refuses_a_bridge_block_because_it_has_no_scaled_arm(tmp_path):
    extra = '\n[e9.bridge]\nhandoffs = ["20241016_composio_x/a_traj#1"]\nreading_max_fstar = 0.15\n'
    with pytest.raises(ValueError, match=r"needs \[e9\.rope\]"):
        _resolved_cfg(tmp_path, "e9fl", extra=extra)


# ---- the rest of both files is well formed: everything but the calibration is ready ---------------------

@pytest.mark.parametrize("name,cap,floor,keep_n,last", [("e9f", 32768, 0, 8, "0041"), ("e9fl", 81920, 32768, 3, "0043")])
def test_the_resolved_config_loads_as_a_native_llama_cell(tmp_path, name, cap, floor, keep_n, last):
    c = _resolved_cfg(tmp_path, name)
    assert c.pair == PAIR and pair_models(c.pair) == MODELS
    assert c.context_cap == cap and c.context_floor == floor and c.keep_n == keep_n and c.keep_seed == 9
    assert c.rope is None and c.bridge is None          # native receiver: no scaling, hence nothing to bridge
    assert c.results_dir.name == name and c.scratch_dir.name == "scratch"
    assert c.mapper_k == 1 and c.mapper_space == "content"
    assert c.required_entries == ("0019", "0023", "0025", "0027", last)
    assert e9_driver.required_markers(c)[-1] == f"### {last} " and e9_driver.entry_list(c).endswith(f"/{last}")
    assert e9_driver.rope_args(c) == []                 # no --rope-scaling reaches any upstream dump
    # tau is recalibrated from THIS pair's E8 report, never from the Qwen one
    assert c.e8_report == REPO_ROOT / "results" / "e8f" / "report.json"


@pytest.mark.parametrize("name", E9_NAMES)
def test_the_resolved_config_carries_a_real_pin_that_is_still_enforced(tmp_path, name):
    """The pin is recorded now, so what must be proven is that a pin which does NOT hold still refuses
    -- a recorded sha nobody checks would be worse than a placeholder.

    This asserts against `check_upstream`, the function `e9.assert_ready` delegates the pin to, rather
    than against `assert_ready` itself. An earlier version called `assert_ready` on a config written to
    `tmp_path` and PASSED ONLY BECAUSE THE ENVIRONMENT WAS INCOMPLETE: while the pin was still a
    placeholder, `assert_ready` refused early, before reaching a `relative_to(REPO_ROOT)` that a config
    outside the repo can never satisfy. The moment the upstream checkout was moved to the real pin the
    same test began failing on that ValueError -- so it was testing the environment, not the guard.
    Going through `check_upstream` tests the mechanism that actually enforces the pin and is
    independent of where the config file happens to live."""
    c = _resolved_cfg(tmp_path, name)
    assert re.fullmatch(r"[0-9a-f]{40}", c.upstream_sha) and "UNRESOLVED" not in c.upstream_sha
    # a well-formed sha that is not in the checkout: neither ancestor nor present
    with pytest.raises(RuntimeError, match="REFUSED"):
        check_upstream(c.upstream_path, "0" * 40, e9_driver.UPSTREAM_PATHS, who="E9")
    # and a malformed one is refused before git is consulted at all
    with pytest.raises(RuntimeError, match="REFUSED"):
        check_upstream(c.upstream_path, "not-a-sha", e9_driver.UPSTREAM_PATHS, who="E9")


def test_the_qwen_configs_are_untouched():
    """A new family is new files: none of the four registered configs may have moved."""
    e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
    e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
    e8 = load_e8_config(REPO_ROOT / "config" / "e8.toml", REPO_ROOT)
    assert e9.pair == e9l.pair == e8.pair == "qwen3-0.6b-to-1.7b"
    assert e9.e8_report is None and e9l.e8_report is None    # the default routing, results/e8/report.json
    assert e9l.rope is not None and e9l.bridge is not None   # still the scaled cell it was
    assert e8.gate == () and e8.scope_note is None
