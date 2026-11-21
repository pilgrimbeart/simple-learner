# Phase-dependent response — D133

**40/40** draws pass all phase comparisons, both frequency bands and all three steps. Wilson 95% interval: [0.9123783988027135, 1.0000000000000002].
Both refinements pass: True. Pilot lag-removal control: 288 rows; pass: True.

Raw zero-phase bias range: [-0.2375846157728126, 0.22682770853936005] V. Minimum near/far phase contrasts: 0.0121121/0.0241637 V. Maximum output ripple: 0.0831627 V.
The observer compares different stimulus conditions; the circuit receives only currents. This demonstrates local phase sensitivity, not a zero-centred error, unique phase over a full cycle, locking or frequency learning. The ideal product formula is approximate for these nonlinear gates.

Core: five states, four connections; {'T': 164, 'R': 29, 'C': 13, 'D': 0, 'sources': 18}. Supply power (mean, 95% interval): [5.717453495679943e-09, 5.684305507094849e-09, 5.7511936639561435e-09] W.
Core circuit only; external bench sources and recording excluded. Activity and gross charge are in raw rows, separately from supply power.

Protocol: protocol.json. All rows: confirm.jsonl. Source hashes/revision: confirm_provenance.json. First saved draw independently remeasured. Large traces remain locally in /home/pilgrim/git/simple-learner/lab/v/phase_v1/*.npz; trace_manifest.json records hashes. Run lab/phase_report.py to reproduce this audit without simulations.
