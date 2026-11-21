# Retained memory and controlled writes — D127

Confirm: **40/40** component draws pass both signs at all three timesteps. Wilson 95% interval [0.912, 1.000].
Both refinement checks: True. Pilot controls: 144/144 passed; controls were run on pilot seeds only.

A positive or negative evidence voltage writes the retained state only while a noisy eligibility node opens the write connection. The stored voltage gates a later response. The same probe is repeated before writing, after writing and near 100 s. Opposite evidence alone at 50 s tests gate closure.

This is a component witness with supplied evidence and eligibility, not discovery of a useful reward-credit rule. The gate is nonnegative; signed writes come from the evidence source. The stored range is positive, so signed learned weights are not demonstrated.

Core: 5 states, 2 connections; parts {'T': 60, 'R': 12, 'C': 5, 'D': 0, 'sources': 8}. Mean core power (mean, 95% paired-seed bootstrap): [2.4083721207815702e-09, 2.287051567087923e-09, 2.525416781583065e-09] W.

Activity (gross charge and threshold crossings) is recorded separately per node in the raw JSONL. Bench stimulation/recording are excluded. Two ideal pump supplies enter the source count, but their implementation and energy are absent.

| Metric | Observed minimum | Observed maximum |
|---|---:|---:|
| write_delta_V | -0.12505406 | 0.1236061 |
| hold_span_V | 0 | 0 |
| closed_gate_delta_V | -5.5511151e-17 | 1.110223e-16 |
| readout_change_V | -0.17351722 | 0.16574631 |
| late_readout_delta_V | -7.9143073e-05 | 0.00010889076 |

Exploratory startup audit: baseline minus initial stored voltage ranges from -0.000384509 to 0.000928213 V. Dynamic input/gate states start randomly, so brief startup writing is possible; retention is tested after settling, not from arbitrary birth states.

Seed labels 52000/52100 were used historically in block-model experiments with a different RNG construction. These are new evaluations of this circuit, separate from its pilot; no globally unused seed-label or new-family claim.

The established retained-node model has no idle noise: a quiet hold is an integration check of that assumption, not a measurement of physical retention. No new noise switch or engine change.

Large saved traces stay outside git at `/home/pilgrim/git/simple-learner/lab/v/retained_write/*_v1.npz`; `trace_manifest_v1.json` records their hashes. Small metrics, specifications, reports and replay are retained.

Protocol: `protocol_v1.json`; raw results: `confirm_v1.jsonl`; exact source hashes and dirty revision: `confirm_provenance_v1.json`. Pilot and confirm seeds are fixed in the protocol. Confirmation is separate from pilot. Each seed has paired signs and three timesteps, not six independent observations.

Reproduce with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retained_write_bench.py prepare|pilot|confirm` (choose one stage; existing outputs are protected from overwrite). Report/replay: `.venv/bin/python lab/retained_write_report.py --stage confirm --live-seconds 8`. All paths relative to the repository.
