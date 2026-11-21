# Task A — independent audit

Discrepancies: **0** (listed in `discrepancies.json`).

## Inputs
- Manifest: 115 files, 0 mismatches.
- Provenance `order_balance_information`: 9 files, 0 current-hash differences, protocol hash matches: True
- Provenance `order_local_calibration`: 10 files, 0 current-hash differences, protocol hash matches: True
- Provenance `order_continuous_baseline`: 11 files, 0 current-hash differences, protocol hash matches: True
- Provenance `order_baseline_stream`: 13 files, 0 current-hash differences, protocol hash matches: True
- Provenance `order_long_calibration`: 14 files, 0 current-hash differences, protocol hash matches: True
- Provenance `order_calibration_precision`: 9 files, 0 current-hash differences, protocol hash matches: True
- Provenance `adaptive_oscillator`: 8 files, 0 current-hash differences, protocol hash matches: True
- Provenance `adaptive_oscillator_confirm`: 10 files, 0 current-hash differences, protocol hash matches: True

## Oscillator confirmation (D162)
- Records 360, unique keys 360 of 360 declared (40 seeds x 3 arms x 3 steps).
- original: 38/40 all-steps pass, Wilson95 [0.8350, 0.9862]; failed [2026120208, 2026120221]
- adaptive: 40/40 all-steps pass, Wilson95 [0.9124, 1.0000]; failed []
- writer_removed: 38/40 all-steps pass, Wilson95 [0.8350, 0.9862]; failed [2026120204, 2026120225]
- Paired pass difference adaptive minus original: +0.050 [+0.000, +0.125] (seed bootstrap, 4000, RNG 126); includes zero: True. Not evidence of population superiority or of equivalence.
- Paired pass difference adaptive minus writer_removed: +0.050 [+0.000, +0.125] (seed bootstrap, 4000, RNG 126); includes zero: True. Not evidence of population superiority or of equivalence.
- Step halving: 36 intervals recomputed, all inside ±.05: True; mismatches with saved: 0.
- Saved finest traces: 7 remeasured of 7 listed (of 120 finest-step records; most traces were not saved). Max value error 0.
- Mean supply power at finest step, original: 9.948 nW [9.784, 10.108]
- Mean supply power at finest step, adaptive: 16.270 nW [16.041, 16.488]
- Mean supply power at finest step, writer_removed: 15.701 nW [15.472, 15.919]
- Added power adaptive minus original: 6.322 nW [6.180, 6.457]
- Added power adaptive minus writer_removed: 0.569 nW [0.543, 0.597]
- Core parts: {'original': 95, 'adaptive': 196, 'writer_removed': 147} (memory pump implementation and energy excluded, as before).
- Writer-removed memory held exactly in all 120 records: True.

## Order references (D163, D164)
- Branch records 1360 (unique 1360), 34 cases per seed: True.
- 1000 s histories 40, settings 160 (4 modes); 100 s prefixes identical: True.
- raw: 28/40 draws, 1314/1360 cases, rescued 11, harmed 37; failed draws 12 draws
- 0.15: 38/40 draws, 1349/1360 cases, rescued 13, harmed 4; failed draws [2026112215, 2026112227]
- 1.0: 38/40 draws, 1349/1360 cases, rescued 13, harmed 4; failed draws [2026112215, 2026112227]
- 3.8585074308112732: 38/40 draws, 1349/1360 cases, rescued 13, harmed 4; failed draws [2026112215, 2026112227]
- Independent rescoring mismatches: 0.
- D164: 240 rows recomputed with statistics.NormalDist; max probability difference 0; infeasible draws given probability 0: [2026112215]. Independence of a new detector's error is an assumption; 4/16-path rows are hypothetical.

