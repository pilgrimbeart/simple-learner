# change_v1 — pilot

**1/8** seeds pass every condition at all three steps. Wilson95 [0.022, 0.471].
Both refinements pass: True. Pilot control rows: 192; all pass: True.

Core: 4 states, 4 connections; parts {'T': 108, 'R': 18, 'C': 8, 'D': 0, 'sources': 12}. Mean supply power (mean,95% interval): [1.5723974244824538e-08, 1.5195327679892852e-08, 1.6180281055877705e-08] W.
Core only; bench sources/recording excluded. Memory pump sources counted ideally; implementation and energy absent. Activity in raw rows separate from supply power.

Frozen criteria: Every case: signed onset and opposite offset peaks >.025 V; sustained change from baseline <.35 times EACH peak; after return abs residual <.01 V. Zero rail hits. All cases/all steps per seed. Wilson95 lower>=.90 in40 seeds.

Prediction: Linear matched branches: K[(1+s*.02)^-1-(1+s*.2)^-1], with .01s input/output lags; nominal DC rejection. Mismatched DC gains leave a persistent residual. Saturation/offset alternatives may reduce transients. No robust perfect-adaptation theorem claimed.

Component coverage only. No robot learning or general stability guarantee. Each seed counts once across conditions and steps. Raw metrics and failures remain visible; no equivalence claim from an interval overlapping zero.

Exact graph/stimuli: protocol.json; raw rows: pilot.jsonl; code hashes/revision: pilot_provenance.json. Large saved traces at `/home/pilgrim/git/simple-learner/lab/v/motifs/change_v1/*.npz` stay outside git, hashes in trace_manifest.json.

Report: `.venv/bin/python lab/motif_report.py change_v1 --stage pilot --live-seconds 8`. No simulation rerun required.
