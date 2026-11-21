# Retained bias adaptation: fresh confirmation

The oscillator adjusts its own bias from its local voltage through one added memory and two connections. No external frequency, phase or parameter assignment is supplied.

| Arm | Complete draws | Wilson95 | Refinement | Parts | Supply power (mean,95%) W |
|---|---|---|---|---|---|
| original | 38/40 | [0.8349612263085903, 0.9861793326138516] | True | 95 | [9.948178135331514e-09, 9.784481867295447e-09, 1.0108129101831939e-08] |
| adaptive | 40/40 | [0.9123783988027135, 1.0000000000000002] | True | 196 | [1.626997019546699e-08, 1.6040658299499175e-08, 1.6488100453340815e-08] |
| writer_removed | 38/40 | [0.8349612263085903, 0.9861793326138516] | True | 147 | [1.5701338961194335e-08, 1.5472269663930405e-08, 1.5919196842085856e-08] |

Frozen reliability and refinement requirement met.
Paired changes: {'original': {'rescued': [2026120208, 2026120221], 'harmed': [], 'pass_difference': [0.05, 0.0, 0.125], 'power_difference_W': [6.321792060135475e-09, 6.180119745321986e-09, 6.456537830184257e-09]}, 'writer_removed': {'rescued': [2026120204, 2026120225], 'harmed': [], 'pass_difference': [0.05, 0.0, 0.125], 'power_difference_W': [5.686312342726551e-10, 5.428764110030256e-10, 5.97290199563665e-10]}}.

This is a bounded operating-point adaptation witness, not reward learning or a universal oscillation guarantee. The nominal write rate and correction authority are design choices. Conditions and the100s life are unchanged from development; these are new component draws, not new problem families. Exact idle retention follows the existing memory model. Core counts exclude the existing pump implementation/energy anomaly; no SPICE or physical chip measurement.

All360 rows audited; 7 saved finest traces remeasured. Activity and memory motion are separate from power in raw records/audit. See ../adaptive_oscillator/schematic.svg for the unchanged complete graph. Provenance and absolute trace hashes accompany the result.
