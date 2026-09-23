# MiniPIC's authors state they could not find public traces to evaluate position-independent caching on, which is a citable source for "PIC is evaluated on built compositions"

kills: (nothing)
ts: 2026-09-14T09:29:11.316Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: MiniPIC (arXiv 2606.13126) contains "we were not able to find such traces despite our best efforts". A summarized
read of the page gives the referent as public RAG traces with full timing and tokenized prompts, and the evaluation
set as 2WikiMultihopQA compositions. The paper can cite this sentence for its claim that PIC is evaluated on built
compositions rather than recorded traces. The same capture could not confirm the corresponding sentences for
KVShareArena (2609.10266) or SemPIC (2607.28069): grepping their HTML for the quoted phrases returned nothing. Those two
attributions rest on summarized reads only and should not carry a quotation until read in full.
basis: `curl -sL https://arxiv.org/html/2606.13126 | grep -o "we were not able to find such traces despite our best
  efforts"` printed the phrase; `curl ... 2609.10266 | grep -o "Reports are frozen once[^.]*"` and `curl ... 2607.28069 |
  grep -o "Synthetic Biographies, HotpotQA, MuSiQue[^.]*"` printed nothing.
re-verify: curl -sL https://arxiv.org/html/2606.13126 | grep -o "we were not able to find such traces despite our best efforts" | head -1   # the phrase
