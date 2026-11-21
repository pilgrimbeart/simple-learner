# Retained-memory limits — D129

The original gate protects memory when closed, but opening it without evidence can write a substantial false value. The missing control exposes transfer-offset leakage. This does not change the older frozen result.

Gate-only writes below1mV: 0/8. Evidence-only writes below1mV: 8/8.
Analytic gate-only RC/write-driver prediction RMSE: 1.47174e-05 V.
Repeated-write saturation: 16/16; opposite-write release: 16/16.

| Condition | Minimum stored change,V | Maximum stored change,V |
|---|---:|---:|
| overlap_-1_-0.5 | -0.03605 | 0.0397217 |
| overlap_-1_-0.1 | -0.0878596 | -0.0569946 |
| overlap_-1_0.0 | -0.11589 | -0.0791364 |
| overlap_-1_0.1 | -0.0896343 | -0.0568477 |
| overlap_-1_0.3 | -0.0401045 | 0.0303604 |
| overlap_-1_0.6 | -0.03605 | 0.0397218 |
| overlap_1_-0.5 | -0.0360499 | 0.039722 |
| overlap_1_-0.1 | 0.0434348 | 0.0952932 |
| overlap_1_0.0 | 0.07339 | 0.117156 |
| overlap_1_0.1 | 0.0452824 | 0.0924648 |
| overlap_1_0.3 | -0.0269637 | 0.0444913 |
| overlap_1_0.6 | -0.03605 | 0.0397218 |
| gate_only | -0.03605 | 0.0397218 |
| evidence_only | -2.77556e-17 | 5.55112e-17 |
| repeated_-1 | -0.911378 | -0.809609 |
| repeated_1 | 0.524296 | 0.597556 |

Far-separated evidence produces essentially the gate-only bias. Subtracting that bias in analysis reveals the overlap contribution, but such observer subtraction is not a circuit repair. The next mechanism should reject absent evidence explicitly, using existing parts if possible.

Exploratory8draws; RC analytic expectation omits tiny sigmoid noise rectification and rail fade, not a noiseless alternate simulation. Memory saturation and idle hold follow the engine contract.

All384rows retained in rows.jsonl. Protocol, original code hashes and exact component draws are retained. Source: lab/memory_limits.py and lab/memory_limits_report.py. D127 graph/parts are unchanged; per-run supply power and gross-charge activity remain in rows. Large traces are local at /home/pilgrim/git/simple-learner/lab/v/memory_limits/*.npz; hashes in trace_manifest.json.
