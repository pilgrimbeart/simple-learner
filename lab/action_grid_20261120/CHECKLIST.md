# Action grid — obligation ledger (work order: ../WORK_ORDER_2026-11-20_action_grid.md)

Execution start 2026-11-20T18:28:04Z; hard deadline 2026-11-21T06:28:04Z (12 h). One executor, no delegation.
Status values: done / not triggered (with branch evidence) / incomplete (blocker, remaining work); pending only during work.

| ID | Obligation | Status | Evidence | Expected / actual | Blocker / remaining |
|---|---|---|---|---|---|
| R0 | Freeze inputs, plan, budget | done | PROTOCOL.md, PREDICTIONS.md, lab/v/action_grid_20261120/manifest.json (18:39:48Z; attempt1 superseded, logged), bench_jobs.json, develop_jobs.json, preflight.json | estimate 4.9 h incl. 1.25x vs 11.8 h left: fits | none |
| R1 | Observer/runner, identity checks | done | ag_engine.py, ag_jobs.py, ag_checks.py, run.py; checks.json valid (17 checks incl. D180 seed-8 12-life reproduction of meals, firings, node events, traces, arrays hash, wiring); realised.json | 17/17 pass | none |
| R2 | Every fixed bench | pending | | 31,104 / – | |
| R3 | Every development life | pending | | 31,104 / – | |
| R4 | Historical reconciliation, costs | pending | | | |
| R5 | Development analysis, selection | pending | | 81 rows, 3 selected | |
| R6 | Fresh confirmation, 3 steps | pending | | 18,432 / – | |
| R7 | Uncertainty, physical, convergence | pending | | | |
| R8 | Omission audit, handoff, docs | pending | | | |

## Amendments and routine fixes log
(none yet)
- 2026-11-20T18:40Z (routine interpretation, logged): the realised table (`realised.json`) shows all 27
  oscillator-speed-0.75 settings put `explore_adjust` below I_MIN = 1 pA (nominal 1.125 pA) on 15 of 40 seeds
  (bench+development seeds; the failure depends only on the seed's mismatch draw). Per §3 these are named invalid
  jobs. They are still simulated and saved (status `invalid_realised`, diagnostic only), excluded from every valid
  mean, they make their configuration incomplete (cannot be selected) and stay in denominators. A first manifest,
  checks and preflight (`*_attempt1.json`) were frozen before this change and before any grid job; re-frozen after it.
  Job-buffer overflow likewise sets `invalid_overflow`.
- 2026-11-20T18:58Z budget check: bench took 678 s (est. 533). Development runs at ~1.75 s/life/worker (preflight
  1.06 s single-process; contention), ETA ~21:00Z. Re-estimate of all remaining mandatory work with the same
  slowdown (×1.6) and ×1.25 allowance: develop 2.1 h + confirm 3.9 h + analysis/report 1.5 h ≈ 7.5 h against
  9.5 h remaining: fits; no reduction.
- 2026-11-20T19:10Z (routine, logged): `ag_report.py` (table generation) written after the manifest freeze and before
  any analysis of development results, using the frozen metric/ranking functions. `ag_analysis.contrasts` gained
  descriptive food-rate contrasts (informed − each arm) because, with taste withheld, arms where P has no effect have
  net ≡ 0 by construction; metrics, ranking and required contrasts unchanged. Analysis code is not in the simulation
  hash, so no simulated row is affected.
- 2026-11-20T19:05Z R4 early check: all 384 baseline development lives reproduce D180 exactly (reconciliation.json).
- 2026-11-20T21:58Z (interruption, logged): progress slowed after 20:34Z (one life's wall time 2758 s, consistent with the
  machine suspending) and the machine rebooted before 21:57Z with 18,505/31,104 development rows saved. The ledger
  (18,505 valid JSON rows, sim 5f2066bf58ecb0e5) and the archive (18,505 complete pickles, clean EOF) were checked intact;
  `run.py develop --resume` (pid 1059) runs only the 12,599 missing keys with the same frozen job list and simulation hash,
  then analyse → confirm → report run in sequence. Remaining estimate ≈ 1.4 h develop + 3.9 h confirm + reporting,
  inside the 06:28Z deadline. No result was read before resuming.
- 2026-11-21T08:30Z (interruption, logged): develop completed (31,104 rows, 26,568 ok, 4,536 named invalid), analyse
  completed (R4 reconciliation 384/384 match; R5 tables and selection.json frozen 23:29Z), confirm frozen (seeds
  2027112000–2027112127; realised table 1,536 engines, 0 failed). At 01:47:33Z the kernel OOM killer killed confirm
  worker pid 8214 (1.1 GB resident), breaking the pool with 9,695/18,432 confirm rows saved (all ok). The 12 h
  deadline (06:28Z) has passed. R6/R7/R8 are incomplete; continuing beyond the deadline is the user's decision.
  Confirmation rows were not read. Resume: `cd lab/action_grid_20261120 && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
  MKL_NUM_THREADS=1 ../../.venv/bin/python run.py confirm --resume && ../../.venv/bin/python run.py report`
  (with fewer workers, a routine change, to stay within memory).
- 2026-11-21T08:29Z (user's decision: "Complete all work now"): budget extended past the 12 h deadline to finish R6–R8.
  Routine change: `run.py` WORKERS now read from AG_WORKERS (default 7), run with 4 to stay within 7.8 GB (a confirm
  worker reached 1.1 GB). run.py is not in the simulation hash; the hash (5f2066bf58ecb0e5) is unchanged. Confirm
  archive checked intact (9,695 complete pickles, clean EOF). `run.py confirm --resume` (pid 43592) then `report`.
