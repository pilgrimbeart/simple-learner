# Pulse recovery — D136

The unchanged circuit passes all 64 tested conditions at input-off gaps of 100 ms and above. At 50 ms, 44/64 pass; at 20 ms, 18/64 pass. These are eight reused development draws, both signs/amplitudes/durations, at the existing finest step. The 64 original one-second conditions reproduce exactly. No new reliability or maximum-event-rate claim.

| Input-off gap (ms) | Sign | Conditions passing / 32 | Missed first / second response |
|---:|---|---:|---:|
| 20 | -1 | 18 | 10 / 0 |
| 20 | +1 | 0 | 0 / 32 |
| 50 | -1 | 32 | 0 / 0 |
| 50 | +1 | 12 | 0 / 10 |
| 100 | -1 | 32 | 0 / 0 |
| 100 | +1 | 32 | 0 / 0 |
| 200 | -1 | 32 | 0 / 0 |
| 200 | +1 | 32 | 0 / 0 |
| 500 | -1 | 32 | 0 / 0 |
| 500 | +1 | 32 | 0 / 0 |
| 1000 | -1 | 32 | 0 / 0 |
| 1000 | +1 | 32 | 0 / 0 |

**Interpretation.** For positive inputs, short gaps leave the adaptive state insufficiently reset and suppress the second output peak. Negative inputs trigger on their return to zero; a short gap interrupts that first positive excursion when the next negative input begins. This asymmetry matters: the input-off gap is not the positive-event spacing (which also includes a 0.5 or 2 s pulse). No merged or extra events were recorded. Some failures are weak/short pulses rather than missing crossings. These observations do not prove that a regenerative mechanism is required.

Protocol, all 384 raw rows, state snapshots, hashes and detailed summary are retained here. Large saved traces remain locally under /home/pilgrim/git/simple-learner/lab/v/pulse_recovery; trace_manifest.json records hashes. Scripts: lab/pulse_recovery.py and lab/pulse_recovery_report.py. Graph and physical parts are unchanged from D132; raw power is recorded per trajectory, not compared as a hardware saving.
