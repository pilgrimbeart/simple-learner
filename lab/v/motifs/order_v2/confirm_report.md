# order_v2 — confirm

**34/40** seeds pass every condition at all three steps. Wilson95 [0.709, 0.929].
Both refinements pass: True. Pilot control rows: 816; all pass: True.

Core: 8 states, 7 connections; parts {'T': 267, 'R': 39, 'C': 12, 'D': 0, 'sources': 31}. Mean supply power (mean,95% interval): [2.4273875031917693e-08, 2.4087694569775643e-08, 2.446243822360695e-08] W.
Core only; bench sources/recording excluded. Memory pump sources counted ideally; implementation and energy absent. Activity in raw rows separate from supply power.

Frozen criteria: Each seed/all steps: coincidence peak simultaneous>.15V; every single and +/- .15/.6s separated coincidence<.03V. Order difference signed mean following second event>.03V at +/- .06/.15s. Simultaneous abs order mean<.06V; far-separated abs order mean<.03V. No criterion for near-separated coincidence; finite bandwidth. All rails untouched.

Prediction: Mirrored low-pass-then-gate paths approximate delay-and-correlate. V2 changes only trace leaks: time constant .15s at unchanged capacitance/current. A trace decays with .15s time constant: later second input uses remaining first trace. Reversing order reverses explicit difference node. Fast A/B overlap drives separate coincidence output. Sigmoid thresholds reduce absent-input offset leakage; no exact multiplier or motion-inference claim.

Response metrics use change from prestimulus baseline; that subtraction is an observer measurement, not an additional circuit. Absolute zero-threshold decoding is not demonstrated. Component coverage only. No robot learning or general stability guarantee. Each seed counts once across conditions and steps. Raw metrics and failures remain visible; no equivalence claim from an interval overlapping zero.

Exact graph/stimuli: protocol.json; raw rows: confirm.jsonl; code hashes/revision: confirm_provenance.json. Large saved traces at `/home/pilgrim/git/simple-learner/lab/v/motifs/order_v2/*.npz` stay outside git, hashes in trace_manifest.json.

Report: `.venv/bin/python lab/motif_report.py order_v2 --stage confirm --live-seconds 8`. No simulation rerun required.
