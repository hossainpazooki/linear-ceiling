# `summarize_e9` fetches the SOURCE model's snapshot, so a gated pair needs a Hub token with gated-repo scope, not just an accepted license

ts: 2026-10-02T03:35:11Z
commit: 470133e
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `summarize_e9` builds its encoder from `snapshot(pair_models(cfg.pair)[0])` (`summarize_e9.py:483`), and `weights.snapshot`
calls `snapshot_download` with `allow_patterns=["*.safetensors", "*.json"]` (`weights.py:69`), so re-summarizing the Llama cell
downloads the whole Llama-3.2-3B snapshot (~6.4 GB) for its tokenizer. Both meta-llama repos are gated. On 2026-10-01 the
run refused three ways in sequence: `GatedRepoError 403` with the 09-30 fine-grained token (license not accepted AND the
token had no gated-repo scope — its global permissions were `discussion.write, post.write` only); `401` after that token was
invalidated on the Hub while the machine still held it; `200` with a new fine-grained token carrying "Read access to contents
of all public gated repos" after the Llama 3.2 license was accepted (18:32Z). The receiver (Llama-3.1-8B) is never loaded by
the summarizer, so its separate Llama 3.1 license is not needed for R12 (`403` on it, run passed). The E8 summarizer loads no
model at all.
basis: at 470133e, 2026-10-02T03:35:11Z, `grep -n "qwen_encoder(snapshot(pair_models(cfg.pair)[0]))"` printed line 483;
  `grep -n allow_patterns src/linear_ceiling/weights.py` printed line 69 with both patterns; with the cached token,
  `curl … /meta-llama/Llama-3.2-3B/resolve/main/tokenizer.json` returned HTTP 200 and `…/Llama-3.1-8B/…` HTTP 403. The
  earlier 403 / 401 / token-scope readings are in the session log (18:0x–18:3xZ, 2026-10-01); the `whoami-v2` read of the
  old token printed `role fineGrained | global ['discussion.write', 'post.write']`.
re-verify: grep -n "qwen_encoder(snapshot(pair_models(cfg.pair)\[0\]))" src/linear_ceiling/summarize_e9.py   # expect line 483: the source model's snapshot is fetched for the encoder
