# Phase-dependent response — D133

**8/8** draws pass all phase comparisons, both frequency bands and all three steps. Wilson 95% interval: [0.6755924351161198, 1.0].
Both refinements pass: True. Pilot lag-removal control: 288 rows; pass: True.

Raw zero-phase bias range: [-0.13849446437499333, 0.21421082372231112] V. Minimum near/far phase contrasts: 0.0125522/0.0249535 V. Maximum output ripple: 0.0887892 V.
The observer compares different stimulus conditions; the circuit receives only currents. This demonstrates local phase sensitivity, not a zero-centred error, unique phase over a full cycle, locking or frequency learning. The ideal product formula is approximate for these nonlinear gates.

Core: five states, four connections; {'T': 164, 'R': 29, 'C': 13, 'D': 0, 'sources': 18}. Supply power (mean, 95% interval): [5.8036118173061244e-09, 5.771460556402624e-09, 5.842890930719879e-09] W.
Core circuit only; external bench sources and recording excluded. Activity and gross charge are in raw rows, separately from supply power.

Protocol: protocol.json. All rows: pilot.jsonl. Source hashes/revision: pilot_provenance.json. First saved draw independently remeasured. Large traces remain locally in /home/pilgrim/git/simple-learner/lab/v/phase_v1/*.npz; trace_manifest.json records hashes. Run lab/phase_report.py to reproduce this audit without simulations.
