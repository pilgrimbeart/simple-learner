# Status — shared-readout causal replay (D170, 2026-11-20)

**Complete.** All tasks (1–6) done, every reproduction and refinement gate passed. Executed by one worker directly in
the dirty main checkout. Nothing was delegated, committed, cleaned or installed.

- **Entry.** No earlier REPORT existed for this assignment. D168's `index.json` was verified first: 33/33 hashes match.
  The D170 "Before work" record was appended to `discrete/NOTEBOOK.md` at 11:10 UTC, before any calculation.
- **Manifest.** `manifest.json` was frozen at 11:09 UTC, at revision 5700eaa0d397: 33 inputs and 1186 dirty files.
  `manifest_addendum_pre_replay.json` was written before the replay. It hashes CONTRACT.md, bounds.json,
  SOURCE_REVIEW.md, bounds.py, core.py, checks.py, replay.py, and checks.json and budget_rows.jsonl. Script hashes
  taken before each run are in `script_hashes.log`.
- **Jobs.** One at a time, with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`. No other lab job was
  running; only idle agent processes were present.
- **Wall clock.** About 11:02 to 11:37 UTC, inside the four-hour envelope. Source and specification work took about
  15 minutes (ceiling 75).

| task | command | compute (ceiling) | result |
|---|---|---|---|
| manifest | `.venv/bin/python lab/shared_readout_20261120/manifest.py` | <1 s | frozen |
| sources | PyMuPDF render with `~/.venvs/simple-learner-tools/bin/python -I` in the scratch folder; pages read as images | — | Enz & Temes pp. 1585, 1586, 1598, 1599, 1601, 1602 read; Shieh et al. not re-read (SOURCE_REVIEW) |
| 2 bounds | `.venv/bin/python lab/shared_readout_20261120/bounds.py` | <1 s (120 s) | bounds.json; nominal-gate budget passes, gate-offset sensitivity fails |
| 3 checks, attempt 1 | `timeout 120 .venv/bin/python lab/shared_readout_20261120/checks.py` | 36 s (120 s) | **harness bugs, kept in `checks_attempt1_harness_bug/`** (below) |
| 3 checks, attempt 2 | same command after correction 1 | 35 s (120 s) | 8/8 checks pass; static budget in `checks/` |
| 4 replay | `nohup timeout 1800 .venv/bin/python lab/shared_readout_20261120/replay.py` (background, PID 60985, start 11:19:04 UTC) | 778 s (1800 s) | gates pass (below) |
| 5 analysis | `timeout 120 .venv/bin/python lab/shared_readout_20261120/analyse.py` | <2 s (120 s) | refuses to run unless the replay gates passed; 40/40 draws |
| figure | `~/.venvs/simple-learner-tools/bin/python lab/shared_readout_20261120/figure.py` | <5 s | inspected; one layout fix (label placement and legend overlap) |

## Replay gates

- **Schedules.** All 40 are identical to D163, and the pulses rebuild exactly.
- **Raw-mode A/B/W.** Equal to D168's records for both windows: maximum error 0.0 (gate 1e-12).
- **Node 7.** Propagated causally at the fixed knob, it equals the unchanged `stream_trajectory` output within
  1.1e-16 V, at all three steps.
- **Refinement.** 2026112200 and 2026112227 at 0.25 and 0.125 ms, 28 rows: knob change ≤ 7.4e-5 (gate .001), readout
  error change ≤ 0.012 mV (gate 1 mV), classifications identical.
- **Controls.** No input, ordered only and simultaneous only were run on both seeds, every arm. They were built from
  labels in the harness and kept the original event times.

## Corrections and failed attempts

- **Checks, correction 1 of 2.** The first `checks.py` run failed its ideal-cancellation check. Two harness bugs, not
  results:
  1. `point()` re-applied the write dead band after the linear reference (tanh slope ÷1000, current ×1000) had removed
     it. The band was then 1000 times wider in volts, so the knob never moved and every d stayed 0.
  2. The mirror and gate-offset budget terms were run in that linear reference. Output-stage currents are referred to
     the input by 1/slope, so their effect was inflated 1000-fold (40/40 clipped).

  Both were fixed (comments in `checks.py`) and the script was rerun into a fresh folder. The failed output is kept.
  The other seven checks and the remaining budget rows were identical in both runs.
- **Replay and analysis.** No corrections.
- **CONTRACT.md.** Edited before the replay, after `bounds.json` showed that V_TYP is 0.3 V (RAIL/3), not the 0.2 V
  in units.py's stale comment. Four quoted figures were corrected to bounds.json's values: gate bound, power, transistor
  ranges, drift time. The code always used units.V_TYP. The addendum hashes the corrected file.

## Omitted, and why

- **The gate-offset sensitivity was not replayed.** Its static bound fails in both arms: the knob is pinned on 19–25 of
  40 draws. The decision table says no replay when static bounds fail. It is reported as the open requirement.
- **No noisy pilot, SPICE, robot life, catalogue or engine edit, or third variant.** As the work order requires.
- **README not changed.** Whether this changes direction is the reviewer's decision.
- **Reading order.** README's goal section was read during the final compliance pass (11:36 UTC), not at entry.
  Nothing in it changed the contract or the analysis. The report accounts for evidence, time, power and material,
  as the goal asks.
- **bounds.py's hash.** It was taken before its run but printed only to the terminal. It was added to
  `script_hashes.log` afterwards, with a note; the file is unchanged since.

## Large files

`replay/histories_1s.npz` holds the knob and tracker at 1 s for 40 draws × 4 arms (small). Full-resolution
trajectories were not saved: each was streamed through all arms and then discarded.

## Open for review (decisions this worker may not make)

1. How to specify a steering gate's resting opening: the engine's ideal closed gate, a designed closed-at-rest margin
   (a fourth requirement), or something else.
2. Whether to authorise one frozen noisy bench of the shared-reading connection, as specified in REPORT's last
   decision.
3. PROGRAMME's top entry point: this worker updated only the assignment's status line, as authorised.
