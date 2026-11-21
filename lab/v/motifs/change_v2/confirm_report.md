# change_v2 — confirm

**40/40** seeds pass every condition at all three steps. Wilson95 [0.912, 1.000].
Both refinements pass: True. Pilot control rows: 192; all pass: True.

Core: 3 states, 3 connections; parts {'T': 94, 'R': 14, 'C': 7, 'D': 0, 'sources': 12}. Mean supply power (mean,95% interval): [1.0246961961253792e-08, 1.0059034480110213e-08, 1.043526357892311e-08] W.
Core only; bench sources/recording excluded. Memory pump sources counted ideally; implementation and energy absent. Activity in raw rows separate from supply power.

Frozen criteria: Every case: signed onset and opposite offset peaks >.025 V; sustained change from baseline <.35 times EACH peak; after return abs residual <.01 V. Zero rail hits. All cases/all steps per seed. Wilson95 lower>=.90 in40 seeds.

Prediction: Integral negative feedback: local output/integral Jacobian approximately [[-50,-100],[12.5,0]] per second, stable poles -25 +/-25i. Write dead zone permits approx1.5mV residual relative to writer offset, independent of input within unsaturated authority. Offsets shift the baseline; they do not require exact feedforward cancellation. Same functional criteria as v1.

Component coverage only. No robot learning or general stability guarantee. Each seed counts once across conditions and steps. Raw metrics and failures remain visible; no equivalence claim from an interval overlapping zero.

Exact graph/stimuli: protocol.json; raw rows: confirm.jsonl; code hashes/revision: confirm_provenance.json. Large saved traces at `/home/pilgrim/git/simple-learner/lab/v/motifs/change_v2/*.npz` stay outside git, hashes in trace_manifest.json.

Report: `.venv/bin/python lab/motif_report.py change_v2 --stage confirm --live-seconds 8`. No simulation rerun required.
