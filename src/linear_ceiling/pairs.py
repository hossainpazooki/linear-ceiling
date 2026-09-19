"""Model ladders and ordered-pair naming, across families.

Naming provenance: {sourceRepo: kv-transfer-replication, filePath: kvt/pairs.py,
commitSha: f3594458f73d70a15f195c863d52ea6592f61578} — pair names there are
"qwen3-0.6b-to-1.7b" style and this repo keeps them so sealed predictions and upstream
mapper artifacts key on the same string. That string is baked into
mappers/qwen3-0.6b-to-1.7b/k1.{json,safetensors} (whose sha256 calibrate_tau records) and
into every published dataset, so it can never be rewritten: anything added here must be a
strict extension that leaves it byte-identical.

A model id parses into a RELEASE (the whole prefix before the size: qwen3, llama3.1,
llama3.2) and a SIZE. The FAMILY is the release up to the first dot (qwen3, llama3). A pair
must stay inside one family; inside one family it may cross releases, and that is the only
case where the pair name has to name the receiver in full:

  * same release  -> upstream's short form, `<src short>-to-<tgt size>`   (qwen3-0.6b-to-1.7b)
  * cross release -> `<src short>-to-<tgt short>`             (llama3.2-3b-to-llama3.1-8b)

The conditional is forced, not stylistic. The short form applied to the Llama pair would
read "llama3.2-3b-to-8b", which asserts the receiver is Llama-3.2-8B — a model that does
not exist — and the string keys mapper directories, results/probe/<pair>, data/kv/<pair>,
the sealed prediction ledger/predictions/<pair>.json and every report. A seal can never be
rewritten, so a name that names the wrong receiver is not recoverable.

The Llama pair is matched-KV under paper Sec. 2.1 (both sides num_key_value_heads=8,
head_dim=128; the 8B declares no head_dim and reaches 128 via hidden_size //
num_attention_heads), so upstream check_matched_kv passes without relaxation. Its upstream
registration is one entry in kvt/pairs.py PAIRS on top of 063f4023 — commit
UNRESOLVED::upstream_sha_P::kvt/pairs.py PAIRS entry, not yet written or pushed; the
gate-bearing value belongs in config/e8f.toml, config/e9f.toml and config/e9fl.toml, not
here.
"""
import itertools
import re

# The Qwen3 ladder. Four ids, in size order; e0 scans its ordered pairs and
# tests/test_pairs.py pins the tuple. Unchanged by the second family.
LADDER: tuple[str, ...] = ("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "Qwen/Qwen3-8B")

# The Llama ladder is a two-model, CROSS-RELEASE ladder: source first, receiver second.
# It is therefore unreachable by any single-ladder ordered-pairs scan and is registered
# explicitly in EXTRA_PAIRS below rather than being derived.
LLAMA_LADDER: tuple[str, ...] = ("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B")

_QWEN3 = re.compile(r"^Qwen/Qwen3-(\d+(?:\.\d+)?B)$")
# Two Llama releases, one family. Llama-3 (no dot) deliberately does NOT match: it is a
# different release with a different tokenizer and nothing here is registered for it.
_LLAMA3X = re.compile(r"^meta-llama/Llama-(3\.1|3\.2)-(\d+(?:\.\d+)?B)$")


def _parse(model_id: str) -> tuple[str, str]:
    """(release, size) for a known base model id; ValueError otherwise."""
    m = _QWEN3.match(model_id)
    if m:
        return "qwen3", m.group(1).lower()
    m = _LLAMA3X.match(model_id)
    if m:
        return f"llama{m.group(1)}", m.group(2).lower()
    raise ValueError(f"not a known base model id: {model_id!r}")


def _family(release: str) -> str:
    return release.split(".")[0]


def short_name(model_id: str) -> str:
    release, size = _parse(model_id)
    return f"{release}-{size}"


def pair_name(src_id: str, tgt_id: str) -> str:
    if src_id == tgt_id:
        raise ValueError("a pair needs two different models")
    rel_s, _ = _parse(src_id)
    rel_t, size_t = _parse(tgt_id)
    if _family(rel_s) != _family(rel_t):
        raise ValueError(f"a pair must stay inside one model family: {src_id!r} -> {tgt_id!r}")
    if rel_s == rel_t:
        return f"{short_name(src_id)}-to-{size_t}"          # qwen3-0.6b-to-1.7b (sealed; byte-identical)
    return f"{short_name(src_id)}-to-{short_name(tgt_id)}"  # llama3.2-3b-to-llama3.1-8b


def ordered_pairs(models) -> list[tuple[str, str]]:
    return [(a, b) for a, b in itertools.permutations(models, 2)]


# Pairs that no single ladder's ordered-pairs scan reaches, mirroring the upstream PAIRS
# registry. Keyed by the same string upstream uses, so one name serves both repos.
EXTRA_PAIRS: dict[str, tuple[str, str]] = {
    # linear-ceiling entry NNNN (provisional; numbers are allocated by docs/drafts/README.md
    # at staging time). Matched-KV: 8 KV heads x 128 head dim on both sides. Cross-release by
    # construction — see the module docstring for why the receiver is named in full.
    "llama3.2-3b-to-llama3.1-8b": ("meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B"),
}


def pair_models(name: str) -> tuple[str, str]:
    """`qwen3-0.6b-to-1.7b` -> ("Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B"), resolved against
    EXTRA_PAIRS first and then against LADDER."""
    if name in EXTRA_PAIRS:
        return EXTRA_PAIRS[name]
    for a, b in ordered_pairs(LADDER):
        if pair_name(a, b) == name:
            return a, b
    raise ValueError(f"unknown pair {name!r}; not an ordered pair of {LADDER}")
