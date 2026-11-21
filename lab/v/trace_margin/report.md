# Quiet-trace sensitivity bound — D135

A common nominal threshold of **0.2312 V** limits the predicted resting trace to 3 mV (1% gate opening) on the six previously failed draws. The old threshold was 0.15 V, with resting traces as high as 42.2 mV. Each observed threshold error is preserved in the calculation.

The weakest tested input still leaves the following signal at that bound:

| Measurement | Range across 12 trace branches (mV) |
|---|---:|
| Peak | 123.1–223.2 |
| 60 ms after input onset | 109.1–207.2 |
| 150 ms after input onset | 51.2–118.7 |
| 60 ms after input offset | 78.0–161.8 |
| 150 ms after input offset | 36.6–92.7 |

The original transfer-equation prediction matches the two saved first-confirmation trace branches with RMS errors of 0.058 mV, 0.174 mV. Halving quadrature spacing changes the predicted voltage by at most 0.415 µV.

This is an informed feasibility bound, not a selected repair. The 1% target is diagnostic; it does not replace the frozen order criteria. Equality leaves no stochastic margin, and a measurable trace need not be strong enough for the whole comparison circuit. Threshold and downstream balance require separate treatment. No general offset tolerance or fresh-seed reliability claim.

Protocol, full tradeoff curve, source hashes and approximation checks are retained here. Rail fading and noise are omitted only in this transfer-equation analysis, checked against saved noisy traces. Sources: lab/trace_margin.py; readable report/audit: lab/catalogue_diagnostic_audit.py.
