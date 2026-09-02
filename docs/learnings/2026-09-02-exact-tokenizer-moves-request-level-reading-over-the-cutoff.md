# Under the exact encoder the request-level cold reading rises from 10.00% to 10.62%; the registered reading reproduces 0022's 0.2210%

kills: (nothing)
ts: 2026-09-02T03:36:48Z
commit: 0732a31568fa5e0a5c286e241654002872d3729d
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: `summarize_e7 --strategy-override composio_swekit=exact,o4-mini*=exact,gpt-4.1*=exact`
(entry 0022's recount as a flag; registered config sha untouched; recon only) reproduces
0022's registered-reading sensitivity exactly -- numerator 565,025, denominator 255,690,850,
0.2210% -- which pins the flag to the deleted append script's arithmetic. Under the same
exact encoder the four 0024 readings become: registered cold 0.2210%, registered warm 1.9618%,
request-level cold 10.6157% (AT OR ABOVE the 10% cutoff, up from 10.0012% calibrated),
request-level warm 9.1319% (below, up from 8.60%). The tau2 agents (o4-mini, gpt-4.1,
gpt-4.1-mini) have no Lane A measurable trajectory, so their override moves per-agent input
totals only (+2.2% to +3.7%) and no reading. 0022's "the miscalibration worked AGAINST the
verdict" holds under the request-level reading too: exact counting pushes it further above
the cutoff, not below. Decides nothing; the figures ship in the 0009 successor (0022), and
until then the paper's four-reading table cites request-level tokenizer sensitivity as
"measured in `recon.json` pending registration".
basis: `results/e7/recon.json` `sensitivity` (config d16cf4659aab, manifest 371fb4bf3cb0, 188
  files verified): `registered_reading.override` -> `recoverable_upper_bound 565025.x,
  input_spend 255690850, ratio 0.002210`; `cache_aware_override.pooled.ratios` ->
  `{'registered_cold': '0.2210%', 'registered_warm': '1.9618%', 'request_cold': '10.6157%',
  'request_warm': '9.1319%'}`; `messages_recounted_per_agent` -> composio_swekit 7781,
  gpt-4.1 4655, gpt-4.1-mini 5180, o4-mini 4040. Pin test
  `tests/test_e7_sensitivity.py::test_pin_composio_exact_reproduces_entry_0022` -> `1 passed`.
re-verify: .venv/Scripts/python.exe -c "import json;s=json.load(open('results/e7/recon.json'))['sensitivity'];print({k:f'{100*v:.4f}%' for k,v in s['cache_aware_override']['pooled']['ratios'].items()}, s['registered_reading']['override']['input_spend'])"
