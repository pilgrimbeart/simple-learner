# oneshot_v1 — confirm

**40/40** seeds pass every condition at all three steps. Wilson95 [0.912, 1.000].
Both refinements pass: True. Pilot control rows: 96; all pass: True.

Core: 4 states, 4 connections; parts {'T': 127, 'R': 18, 'C': 8, 'D': 0, 'sources': 16}. Mean supply power (mean,95% interval): [3.0061043633175846e-08, 2.9598046815424136e-08, 3.051578002951181e-08] W.
Core only; bench sources/recording excluded. Memory pump sources counted ideally; implementation and energy absent. Activity in raw rows separate from supply power.

Frozen criteria: Absolute output, no baseline subtraction: exactly2excursions above .25V after .8s, each starts within .15s after its positive input change, peak>.35V, width between .01 and .25s, later returns below .1V. Outside .3s following positive changes output<.05V. No rail hits. This is bounded pulse width, not amplitude-independent fixed width or demonstrated regenerative excitability.

Prediction: Input/output integral feedback provides adaptation. Stronger inhibitory authority bounds integral demands for larger input amplitudes. Approx local adaptive poles -25 +/-46.8i/s. Thresholded readout should emit one finite pulse per positive step and remain quiet during held input. Component offset, short pulse/lag or input saturation can defeat it.

Absolute voltage thresholds; no observer baseline subtraction. Component coverage only. No robot learning or general stability guarantee. Each seed counts once across conditions and steps. Raw metrics and failures remain visible; no equivalence claim from an interval overlapping zero.

Exact graph/stimuli: protocol.json; raw rows: confirm.jsonl; code hashes/revision: confirm_provenance.json. Large saved traces at `/home/pilgrim/git/simple-learner/lab/v/oneshot_v1/*.npz` stay outside git, hashes in trace_manifest.json.

Report: `.venv/bin/python lab/motif_report.py oneshot_v1 --stage confirm --live-seconds 8`. No simulation rerun required.
