# Status — calibration readout precision (D168, 2026-11-20)

**Complete.** All six tasks (A–F) done. Every reproduction and refinement gate passed. No output is missing or
partial.

- **Entry:** D167's `index.json` was verified: 28/28 hashes match. The D168 "Before work" record was appended to
  `discrete/NOTEBOOK.md` before any calculation.
- **Manifest:** `manifest.json` was frozen at 10:16 UTC, before any calculation. It holds 34 inputs and 1151
  dirty files, at revision 5700eaa0d397. `manifest_addendum.json` hashes one further input (D165's per-event
  contributions), added for Task E before its first use.
- **Jobs:** one at a time, with one maths thread (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`).
  No other lab job was running when Task D started.
- **Wall clock:** about 10:13 to 10:40 UTC, well inside the four-hour envelope.

| task | command | compute (ceiling) | validation |
|---|---|---|---|
| manifest | `.venv/bin/python lab/calibration_precision_20261120/manifest.py` | <1 s | — |
| A | `.venv/bin/python lab/calibration_precision_20261120/a_precision_curve.py` | 0.7 s (120 s) | 30 mV row and group values equal D167's exactly (error 0); error regions equal D167's (error 0); D164's 240 rows reproduce (error 0); D167 t1b's zero-error classification matches all 640 saved `all_pass`; 2215 probability 0 |
| A figure | `.venv/bin/python lab/calibration_precision_20261120/a_figure.py` | <1 s | hand-written SVG; Okabe-Ito colours with line style, marker and labels |
| B | `.venv/bin/python lab/calibration_precision_20261120/b_error_arithmetic.py` | <1 s (120 s) | resting levels from the trajectories' own equations; coincidence rest exactly 0 on all 40 draws |
| C | reading only | — | pages and equations read are listed in MIXED_FEEDBACK.md |
| D run | `timeout 960 .venv/bin/python lab/calibration_precision_20261120/d_quiet_reference.py` (background, PID 54691 for `timeout`, start 10:19:10 UTC) | 482 s (900 s) | 40 schedules identical to D163; `w`, `w*w` A/B/W equal D167's 640 records, max error 0.0 (gate 1e-12); refinement at 0.25 ms on 2026112200/2026112227, 32 rows: D167 knob change ≤1.03e-5, self-referenced ≤6.9e-6, classifications identical |
| D analysis | `.venv/bin/python lab/calibration_precision_20261120/d_analyse.py two_separate_readings=42.4264 steered_raw=4.2426 steered_intfb=6.0 steered_ff=8.6268 one_offset=30 intfb_chain=42.4264` | <2 s (120 s) | refuses to run unless the run gate passed; 640/640 records |
| E | `.venv/bin/python lab/calibration_precision_20261120/e_noise_wall.py` | <2 s (120 s) | anchor counts from the generator's schedules; 165 final-third anchors outside 2215 |

## Corrections and notes

- **No corrective attempts were needed.**
- **The Task E script** first contained a dead line (`... if False else None`). It was removed before the
  recorded run, and the outputs are from that run.
- **Task C, first pass incomplete:** the first reading stopped at p. 1595 and skipped p. 1592. The compliance
  review caught this, and the rest of section IV (pp. 1592, 1596–1602) was then read. The review entry was
  updated to match.
- **Reading the papers:** both are scanned PDFs without text, and no PDF, OCR or imaging tool is installed (the
  work order forbids installing). The fax-compressed page images were decoded by a small standard-library
  CCITT G4 decoder written for this purpose (`lab/calibration_precision_20261120/g4_decode.py`). It was run with
  `python3 -I` from a scratch folder, so the downloaded PDFs never sat beside code. The PDFs and page images were
  not kept, and the pages were read as images.
- **Figure, first version:** with no plotting library available, it was SVG written directly by `a_figure.py` and
  not inspected.
- **Follow-up, tools authorised by the user:** a separate tools environment, `~/.venvs/simple-learner-tools`
  (matplotlib 3.11.2, PyMuPDF), was created with pip. The project `.venv` and `requirements.txt` are untouched.
  System packages were not possible: sudo needs a password, so there is no Tesseract or poppler.
  - **Figure:** `~/.venvs/simple-learner-tools/bin/python lab/calibration_precision_20261120/a_figure_mpl.py` writes
    `a/precision_curve_mpl.png` and `.svg`. It was inspected by eye, and one overlapping axis label was fixed.
    It supersedes the hand-written SVG, which is kept.
  - **Reading:** Shieh, Patil & Sheu pp. 279–281 were rendered with PyMuPDF and read. Cauwenberghs (NIPS 5)
    pp. 244–248 were read from its text layer. Both were downloaded to the scratch folder and opened with
    `python -I`.
  - **Index:** `index.json` was regenerated after the follow-up and supersedes the first one.
- **Task D, steered variants:** the SDs passed on the command line are Task B's figures. Mirror mismatch √2 × 10%
  was applied to 30, 42.4 and 61 mV chains; the figure for the feed-forward chain uses 61 mV.
- **README** was not changed. Whether this result changes the direction is the review's decision (work order
  §10).
- **`index.json`** hashes the final outputs, excluding itself, and was written last.

## Open for review (decisions this worker may not make)

1. **Catalogue extension (the user's decision).** Should a connection be specified that reads the difference of
   two node voltages and steers one reading pair's current to two destinations in proportions w and 1 − w? It is
   the only candidate that meets the precision requirement (REPORT, "The single comparison to make next"). If
   not, work order §10 makes the D154 routing limitation the next object of diagnosis, or this capability is
   weighed against others the robot needs.
2. **PROGRAMME.md's top "Current execution entry point" paragraph** still directs the next worker to this work
   order, which is now executed. The work order authorised only this assignment's own status line, so the
   paragraph was left unchanged and needs updating at review.
