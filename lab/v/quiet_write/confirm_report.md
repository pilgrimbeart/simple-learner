# Absence-preserving writes — D131

**40/40** component draws pass all5conditions and all3steps. Wilson95 [0.912,1.000].
Refinements pass: True. Pilot removal controls:240rows; all pass: True.

Two thresholded writer paths create an explicit no-write region. Negative evidence reaches its writer through a noisy inverting state. The previous global noise/write-driver model is unchanged. Evidence amplitude +/- .5V is accepted; +/- .05V is intentionally rejected. This sacrifices sensitivity, adds parts and does not learn the threshold or eligibility rule.

Maximum absolute absent/weak write: 5.55112e-17V. Minimum useful signed write: 0.0502716V.
Core:6states,4connections; parts {'T': 142, 'R': 21, 'C': 8, 'D': 0, 'sources': 18}. Mean power (mean,95%interval): [9.199699790335208e-09, 9.046850938862625e-09, 9.348343516581061e-09]W.
Core only. Two ideal pump supplies counted; actual pump implementation/energy and bench sources/readout excluded. Activity separate in raw rows.

The new gate-only test holds eligibility open for1s, versus.25s in D129. This is a capability check, not a paired power/performance comparison between the old and new circuits. All raw null cases remain visible. Hold follows the existing idle-memory-noise assumption. No signed learned-weight, delay-credit, robot-learning or empirical retention claim.

Protocol, full rows, provenance and source hashes are retained. Large traces at /home/pilgrim/git/simple-learner/lab/v/quiet_write/*.npz stay outside git; trace_manifest.json contains hashes. Source:lab/quiet_write_bench.py; audit/report:lab/quiet_write_report.py. Existing results are never overwritten by the runner.
