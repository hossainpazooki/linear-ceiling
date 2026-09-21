# The DeepSeek-V4.1-Flash model card never calls persistent KV "a first-order cost"; it says only that its architecture improves cost efficiency for input-heavy agentic workloads

kills: (nothing)
ts: 2026-09-14T09:28:11.507Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: refuted-assumption
fact: A 2026-09-13 draft introduction said DeepSeek's V4.1-Flash release "prices" persistent KV as "a first-order cost
rather than an implementation detail". The card's raw README contains no "first-order". What it does say:
"substantially improving cost efficiency for input-heavy agentic workloads", attached to the architecture's prefill
activation, and a global KV cache of "890 bytes per token". The operator has since removed DeepSeek from the
introduction. Any reintroduction may quote only what the card says.
basis: `curl -sL https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/README.md` saved `bytes 13110`;
  `grep -c -i "first-order"` printed `0`; `grep -o` printed `substantially improving cost efficiency for input-heavy
  agentic workloads` and `890 bytes per token`.
re-verify: curl -sL https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/README.md | grep -o -i "first-order\|substantially improving cost efficiency for input-heavy agentic workloads\|890 bytes per token"   # the last two phrases only; no first-order
