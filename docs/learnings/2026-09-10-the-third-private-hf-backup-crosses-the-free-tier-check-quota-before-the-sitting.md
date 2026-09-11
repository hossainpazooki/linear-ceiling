# The R8 backup discipline compounds: the third run's private HF dataset does not fit the free 100 GB tier beside the first two, and the arithmetic must be done before the sitting, not at the push

kills: (nothing)
ts: 2026-09-10T04:33:44Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: e9l-aws-run (018fwd195AS7uS2tvJdgSoYP)
status: verified
fact: R8 sends every GPU run's verified mirror to its own private Hugging Face dataset. That cost accumulates
across runs and nothing in the protocol budgets it. E9-long's staging tree measures 61,937,723,784 B (~61.9 GB);
the repo documents two prior private datasets at ~48 GB (E9, 2026-09-04) and 27.7 GB (n420, 2026-09-08), so
~75.7 GB is already committed against Hugging Face's free private allowance of 100 GB. The remaining headroom is
~24 GB, and a full E9-long push therefore cannot complete on a free account: it would take the small records,
then fail roughly 24 GB into `upload-large-folder`, leaving a partial private dataset that looks like a dataset.
The prior two sizes are the repo's own documented figures, NOT measured against the Hub (a private listing needs
a token this session did not hold), so treat ~75.7 GB as a lower bound on what is already stored. Consequences:
check the account's plan and used quota BEFORE a sitting, since the push is the last step and the cheapest moment
to discover a ceiling is the first; and never read a completed `hf` command as a complete backup — the R8
verifier is what settles it. This does not endanger a result: R8 is transport, not evidence, and the home mirror
is what the summarizer reads.
basis: `du -sb ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10 | cut -f1` at 2026-09-10T04:33:44Z ->
  `61937723784`; `grep -o "kept dumps 48 GB" CLAUDE.md` -> `kept dumps 48 GB` and
  `grep -o "89 files / 27.7 GB" docs/handoff/2026-09-09-ruling-b-detached-and-session-close.md` ->
  `89 files / 27.7 GB`, both at HEAD `50bc439`; the 100 GB free private allowance and the $18/TB/mo
  pay-as-you-go rate above PRO's 1 TB are from `https://huggingface.co/docs/hub/storage-limits`, fetched
  2026-09-10.
re-verify: du -sb ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10 | cut -f1   # 61937723784 (~61.9 GB) against a 100 GB free private tier already holding ~75.7 GB of documented backups
