# Status — D167 diagnostic assignment (2026-11-20)

**Complete.** The three tasks finished within their compute ceilings. Every reproduction and refinement gate passed.
No output is missing or incomplete.

- **Protocol:** written before any calculation as the D167 "Before work" record, 07:47 UTC.
- **Manifest:** `manifest.json` freezes 31 inputs and 222 dirty files, at revision 5700eaa0d397.
- **Jobs:** one at a time, single maths thread (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`).
  No other job was running at the start.

| task | command | compute | validation |
|---|---|---|---|
| manifest | `.venv/bin/python lab/calibration_next_20261120/manifest.py` | <1 s | — |
| 1a | `.venv/bin/python lab/calibration_next_20261120/t1a_reproduce_contamination.py` | ~1 s | D165 event sums vs D163 within 9.1e-15 V s; knobs within 4.3e-13; 2227 anchor-only/all settings exact (0) |
| 1b | `.venv/bin/python lab/calibration_next_20261120/t1b_weights.py` (background, PID 43937, 07:50:04–07:58:18 UTC) | 494 s of 900 | 40 schedules identical to D163; pulses rebuilt exactly; original-weight final third vs D163 A/B error 0.0, knob 0.0; partition ≤5.9e-14 V s; refinement 0.25 ms on 2200/2227, 32 rows, max knob change 1.03e-5, classifications identical |
| 1c | `.venv/bin/python lab/calibration_next_20261120/t1c_analyse.py` | ~2 s | 640/640 records |
| 2 | `.venv/bin/python lab/calibration_next_20261120/t2_readout_error.py` | 0.3 s of 120 | D164's 240 rows exact (error 0); feasible intervals exact; zero-error classification agrees with all 1920 saved `all_pass` |
| 3 | `.venv/bin/python lab/calibration_next_20261120/t3_two_gain.py` | 5.4 s of 120 | fixtures (original line, empty, boundary-only, ± coefficients) pass; 1-D intervals exact (0); 39/40 one-knob feasible reproduced |

## Corrections during the work

- **Task 2:** the first run stopped on an assertion. Three raw-mode settings (first-100 s window) have a negative
  denominator B. The interval mapping handles either sign, so the assertion now requires only B ≠ 0. These rows are
  kept and none is dropped.
- **Task 3:** the `margin_active` field is empty because it is computed on a degenerate bracketing polygon. A
  reporting defect only; the closure's `active` lists are correct.

The wall clock from protocol to report was about 35 minutes. `index.json` hashes the final outputs, excluding itself.
