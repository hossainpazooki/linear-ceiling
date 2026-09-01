"""Entry 0016 -- E8 amendment. Run ONLY after 0015 exists (approved ordering).
usage: python append_0016.py <upstream_sha> <date YYYY-MM-DD>"""
import hashlib, re, sys
from pathlib import Path
LEDGER = Path("ledger/ledger.md")
SHA, DATE = sys.argv[1], sys.argv[2]
if not re.fullmatch(r"[0-9a-f]{40}", SHA): sys.exit("upstream sha must be 40 hex")
ENTRY = f"""### 0016 — {DATE} — E8 amended: admitted to LCFM behind the summarizer gate; dumps correction; verdict k = 1; text-sampling rule; upstream re-pin

Operator decisions of 2026-09-01: GPU runs join the LCFM plan (`docs/2026-09-01-lcfm-gpu-plan.md`);
band numbers and entry ordering approved. Entry 0009's registered E8 design and band stand as
written; the clauses below amend it where named.

**(1) E8 may appear in the LCFM 4-pager.** Entry 0009(4) ("E8 appears in no LCFM submission")
is superseded. Entry 0006's numbers-freeze gate already allowed the transfer-fidelity leg
"only if they clear the same gate"; that allowance is restored: E8 numbers enter the 4-pager
only from `summarize_e8`, fail-closed, in the pattern of `summarize_e0`/`summarize_e7`. Lane A/B
premise numbers and the taxonomy remain the submission's core; E8 is one paragraph and one table.

**(2) Correction of 0009's "the KV dumps are gone".** They are not. At the time of writing the
upstream checkout at `../kv-transfer-replication` holds `data/kv/qwen3-0.6b-to-1.7b` (50
sequences, 2.8 GB), `data/kv/qwen3-0.6b-to-1.7b-n420` (12 GB) and the fitted mappers
`mappers/qwen3-0.6b-to-1.7b/k{{1,4,8}}` -- all gitignored upstream, present on the operator's
machine only. Consequence: arm (a) needs no regeneration and E8 needs no GPU. The claim was
made from the upstream's git tree without checking the gitignored working tree; recorded so
the next reader does not repeat the inference.

**(3) The verdict-bearing mapper is k = 1.** Upstream held-out pooled R² at n = 50 (archived
`results/mapper/qwen3-0.6b-to-1.7b/r2.json`): k=1 K 0.681 / V 0.513; k=4 K 0.591 / V 0.336;
k=8 K 0.098 / V −0.641 (collapsed; p/n = 0.8). Entry 0009's band applies to k = 1 only; k = 4
and k = 8 are reported alongside and are verdict-bearing for nothing. A "drop" from a collapsed
baseline is not a measurement.

**(4) Arm (b) text-sampling rule, frozen before any dump.** One window per trajectory: the
first `seq_len` = 1024 tokens of the trajectory's visible messages concatenated in trace order,
each message prefixed by its role tag (`[system]`, `[user]`, `[assistant]`, `[tool]`) on its
own line, tool calls rendered as `name(arguments)`. Trajectories shorter than 1024 tokens are
skipped, never padded. n = 50 sequences, drawn with `rng.make_rng(8)` from the tau2-bench and
SWE-bench suites stratified equally (25 + 25), composio included (it is text, not a coverage
claim), tau-bench v1 excluded (below the agent floor, 0011). Tokenized with the pair's shared
Qwen3 tokenizer (`weights.assert_shared_vocab` checked first). Protocol otherwise identical to
arm (a): `--stride 4`, held out by sequence, `holdout_frac` 0.2. The text is off-policy for
Qwen (0009's scope limit stands) and, per 0012, omits every hidden prefix the provider billed.

**(5) Upstream change and re-pin.** No upstream script scores an EXISTING mapper on NEW dumps
(`kvt.mapper.mapper_r2` is library-only). `scripts/score_mapper.py` is added upstream (load
mapper + source/target dumps, hold out by sequence, write `r2.json` with the same keys as
`fit_mapper.py`), and `UPSTREAM.md` re-pins to `{SHA}`. `config/e8.toml` carries the same
sha and `e8.assert_ready` refuses unless the upstream HEAD matches it with a clean tree for
every script E8 invokes. The "never import kvt" rule is unchanged: E8 calls the upstream by
subprocess in the upstream's own environment. The seal is not involved (0009).

**(6) What E8 reports.** For each k: arm (a) held-out K and V R² (recomputed by
`score_mapper.py` on the archived dumps and cross-checked against the archived `r2.json`,
refusing on disagreement beyond 1e-6), arm (b) held-out K and V R², and the drop (a − b).
The band outcome for k = 1 is stated by the summarizer as HOLDS / DEGRADES / UNRESOLVED
against 0009's numbers; the VERDICT on H-E8 enters only by a successor entry.

prior-entries-sha256: __CHAIN__
"""
text = LEDGER.read_text(encoding="utf-8")
if "### 0016" in text: sys.exit("0016 present")
if "### 0015" not in text: sys.exit("0015 must exist first (approved ordering)")
head = re.search(r"^## Entries\s*$", text, re.M)
if not text.endswith("\n"): text += "\n"
prefix = text + "\n"
chain = hashlib.sha256(prefix[head.start():].encode("utf-8")).hexdigest()
LEDGER.write_text(prefix + ENTRY.replace("__CHAIN__", chain), encoding="utf-8", newline="\n")
from linear_ceiling.ledger_check import check
p = check(LEDGER.read_text(encoding="utf-8")); print("0016 chain:", chain, "problems:", p or "none")
sys.exit(1 if p else 0)
