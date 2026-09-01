"""Entry 0019 -- E9 registered. Run ONLY after 0018 (the corrected figures) exists.
Renumbered from 0017 by the 0017 correction entry; band and design as approved 2026-09-01.
usage (repo root): .venv/Scripts/python.exe docs/drafts/append_0019.py <date YYYY-MM-DD>"""
import hashlib, re, sys
from pathlib import Path
LEDGER = Path("ledger/ledger.md")
DATE = sys.argv[1]
ENTRY = f"""### 0019 — {DATE} — E9 registered: the achievable fraction of the headroom upper bound at a re-rendered handoff (H-E9, band frozen)

Entry 0013 (figures corrected by 0017/0018) records headroom as an UPPER BOUND and states that
the achievable fraction is not measured. E9 measures it, on the observed handoffs, on the A100
the plan names (`docs/2026-09-01-lcfm-gpu-plan.md`). Band numbers approved by the operator
2026-09-01; this entry was drafted as 0017 and renumbered by the 0017 correction.

**Unit.** One observed Lane A switch (entry 0010; 68 at the time of writing), defined at the
REQUEST level per 0017: sender context `S` = everything the sender processed up to and
including its last response before the switch; receiver prompt `R` = the receiver's own
request prompt (the messages of its request preceding its response), never the trajectory
prefix. Both as text from the registered adapter (`e7_swe.load_composio_detailed`, which
records `Msg.request`), the same slices `e7_headroom.measure` prices.

**Alignment, registered method.** Tokenize `S` and `R` with the pair's shared Qwen3 tokenizer
(no special tokens); match tokens by the longest-matching-blocks algorithm of Python's
`difflib.SequenceMatcher` over token ids with `autojunk=False` (Ratcliff/Obershelp: the longest
common contiguous block, then recursively left and right; deterministic; yields a common
subsequence, in general shorter than the true LCS, so `|M|` is a floor). The matched set `M`
carries a position pair `(p_S, p_R)` per token. `|M| / |R|` is reported beside entry 0010's
word-multiset overlap. Exact LCS was not chosen because it is quadratic in 32k-token
sequences; the method is named so the number reproduces.

**Two measurements, both pooled R² (definition A5, provenance per UPSTREAM.md), K and V
separately, over `M` only:**

- **E9-same** (the ceiling under re-rendering, independent of any mapper): the receiver model
  Qwen3-1.7B prefills `S` and `R` natively; its K/V at `p_S` are re-roped to `p_R` in content
  space and compared against its own K/V at `p_R`. This is how much of a content-matched
  token's KV survives a different preceding context -- the achievable ceiling for ANY transfer
  across this handoff.
- **E9-cross** (the transfer): Qwen3-0.6B prefills `S`; the existing k = 1 content-space mapper
  (0016) is applied with receiver positions `p_R` (`kvt.mapper.apply_mapper`, upstream) and
  compared against the receiver's K/V at `p_R`. Reported as an absolute R² and as a fraction of
  E9-same, so mapper error and re-render loss are never conflated.

**H-E9** (registered in the table): *at a re-rendered handoff, same-model KV agreement on
content-matched tokens retains the transfer-relevant fidelity.* **Band, frozen here before any
prefill:** per-handoff E9-same K R², median over included handoffs: **HOLDS if >= 0.70;
DEGRADES if <= 0.40; UNRESOLVED between.** V is reported alongside and is verdict-bearing for
nothing. Reason for 0.70: it is the k = 1 mapper's own same-text held-out K R² (0.681), so
HOLDS means "the re-render costs no more than the mapper itself does".

**Scope limits, registered up front.** Context cap 32,768 tokens (Qwen3 native): a handoff
with `|S|` or `|R|` above the cap is EXCLUDED and counted; coverage (included / observed) is
stated with every figure and nothing is truncated. Text is off-policy for Qwen. One pair.
Composio is one system (0011). E9 bounds what a transfer could recover at the one public
instance of the use case; it says nothing about routing frequency (H-E7a's domain) and must
never be written as a real mid-trajectory transfer.

**Dumps and what is kept.** Every position of `S` and `R` is dumped with the upstream's
existing `dump_kv.py` (`--stride 1`, one sequence per file; no new dump code). A handoff's three
dumps (receiver on `S`, receiver on `R`, source on `S`) are up to ~11 GB, so they are scored
and deleted per handoff; what is kept per handoff is the alignment, the per-layer, per-head
sums of squares (SSE and SST, for E9-same and E9-cross, K and V) and the R² derived from them.
A seeded keep-subset of handoffs (seed and size in `config/e9.toml`, drawn before any prefill)
retains its full dumps, fingerprinted, so a CPU summarizer can recompute those R² from tensors.

**Enforcement.** `e9.assert_ready` refuses until this entry and `config/e9.toml` are committed
unmodified and the upstream is at a pinned commit that adds `scripts/score_positions.py` (the
scorer; a re-pin recorded in `config/e9.toml` and `UPSTREAM.md`) with a clean tree for every
path E9 invokes. Per-handoff checkpoints are synced off the GPU box after each handoff.
`summarize_e9` recomputes the alignment of every handoff from the raw traces, recomputes every
R² from the recorded moments, recomputes the keep-subset's moments from its fingerprinted
tensors by re-running the scorer, recomputes the medians and the band outcome, and refuses on
any disagreement. What it cannot do on CPU is regenerate the deleted dumps: for those handoffs
the moments are a GPU-run record, verified by the keep-subset, and the entry that states the
verdict must say so. The seal is not involved: no mapper is fitted.

prior-entries-sha256: __CHAIN__
"""
text = LEDGER.read_text(encoding="utf-8")
if "### 0019" in text: sys.exit("0019 present")
if "### 0018" not in text: sys.exit("0018 (corrected figures) must exist first")
head = re.search(r"^## Entries\s*$", text, re.M)
if not text.endswith("\n"): text += "\n"
prefix = text + "\n"
chain = hashlib.sha256(prefix[head.start():].encode("utf-8")).hexdigest()
LEDGER.write_text(prefix + ENTRY.replace("__CHAIN__", chain), encoding="utf-8", newline="\n")
from linear_ceiling.ledger_check import check
p = check(LEDGER.read_text(encoding="utf-8")); print("0019 chain:", chain, "problems:", p or "none")
sys.exit(1 if p else 0)
