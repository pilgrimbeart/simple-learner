# CHECKLIST — robot action and exploration (D178)

Work order: [WORK_ORDER_2026-11-20_robot_action.md](../WORK_ORDER_2026-11-20_robot_action.md). Started 2026-11-20 14:23 GMT;
hard cap 20:23 GMT. Results: [lab/v/robot_action_20261120/](../v/robot_action_20261120/). Notebook: [D178](../../discrete/NOTEBOOK.md#d178-robot-action).
States: pending, done, not triggered, incomplete. "Done" = the artifact/check exists, not that a hypothesis passed.

| ID | Obligation | State | Evidence |
|---|---|---|---|
| R0 | Protocol, manifest, arms, predictions, budget | done | [manifest.json](../v/robot_action_20261120/manifest.json) frozen before runs; protocol + predictions in D178; addenda 1–3 before their runs; code_hashes_*.txt; budget below |
| R1 | Identity, provenance, passive logging | done | [checks.json](../v/robot_action_20261120/checks.json): 4×64/64 bit-identical to D176; logging passive; wiring/draws equal across substrates; replay self-identity 252/256 (4 disclosed) |
| R2 | Historical and conditional physical contracts | done | D178 "Contracts": historical (executed) and physical (assessed); unresolved operations listed; measured rail violation recorded at the stage-3 gate |
| R3 | Assigned reading | done | D178 "Assigned reading": Arthur & Boahen II, III A–B, VIII; five implications |
| R4 | Substrate comparison + all-food controls | done | [stage1.json](../v/robot_action_20261120/stage1.json), [ledger/](../v/robot_action_20261120/ledger/): 8 arms incl. all-food per substrate; drift (P_abs_drift_median) and primary metrics |
| R5 | Identical-input replay, evidence/noise budget | done | stage1.json "replay", [stage1_resp.json](../v/robot_action_20261120/stage1_resp.json), [evidence_budget.txt](../v/robot_action_20261120/evidence_budget.txt) |
| R6 | Stage-1 branch decision | done | D178 "R6": job limits fail for informed and learning silicon → stage 2; exploration first |
| R7 | Transfer, omission, operating-region diagnosis | done | transfer_informed_silicon.json, transfer_informed_biology.json (omission, latency, recovery, imbalance, unit variation); windows from [addendum 1](../v/robot_action_20261120/addendum_1_windows.md) |
| R8 | Eight-setting grid, then one knob family | done | grid_silicon/biology.json, grid_eval.json; family: motor_bias_bench.json, 4 replay screens, [family_eval.json](../v/robot_action_20261120/family_eval.json); [addendum 3](../v/robot_action_20261120/addendum_3_knob_family.md) |
| R9 | Candidate contract + informed component comparison | not triggered | stage-3 gate condition 3 false: historical neurons rest −3.5 typ. V (swing −8.2…+5.4), i.e. −1.06 V / −2.5…+1.6 V at chip V_TYP 0.3, beyond ±0.9 V rails (D178 "Stage-3 gate") |
| R10 | Learning/frozen/all-food candidate comparisons | not triggered | depends on R9 (stage-3 informed improvement gate never reached) |
| R11 | Fresh confirmation + two halvings | not triggered | confirmation gate requires R9–R10; not reached |
| R12 | Candidate physical/noise checks + live demo | not triggered | no working physical behaviour claimed (no arm meets the job) |
| R13 | Metrics, uncertainty, costs, reporting | done | metrics.py (frozen definitions from first run); intervals in every json; [costs.json](../v/robot_action_20261120/costs.json): power, firings, material, thruster energy (guess, labelled); unmeasured costs labelled in REPORT |
| R14 | Autonomous-repair handoff (≤ 1 page) | done | [HANDOFF.md](HANDOFF.md) |
| R15 | Final audit + document updates | done | [REPORT.md](REPORT.md); audit below; D178, PROGRAMME.md status, QUESTIONS.md updated |

## Budget estimates (recorded before each stage)

- Stage 0–1 (14:27): closed-loop 100 s lives take ~12 s per 64-life arm on 7 workers (D176 capture.log); 8 arms
  (4 arms × 2 substrates) ≈ 2 min; R1 checks ≈ 2 min; replay ≈ 1.1 s per life, 64 lives × 2 arms × 2 substrates
  ≈ 1 min on 7 workers; analysis/writing ≈ 40 min. Fits the 75 min of stages 0–1.

- Stage 2 (14:39): see [addendum 2](../v/robot_action_20261120/addendum_2_stage2.md): ~7 min compute, ~40 min analysis; fits.
- Stage 3: gate failed before any estimate was needed (no construction).

## Log of routine choices and fixes

- Biology captures: rather than read D176's pickles (which lack position and taste times, both required here), the
  adapter re-captures biology lives and R1 checks them bit-identical to D176's stored `-mem-thr` captures in meals,
  per-tick rows, pulses and movement onset; the identical data is then used as the reused historical capture.
- stage1.py's paired sensor-response contrast returned NaN (lives with no pulses); recomputed by stage1_resp.py.
- stage1.py's tastes per lived second treated movement onset at tick 0 as no movement; corrected in evidence_budget.txt.
- Replay chunked at 1 ms: 4 of 256 self-replays (seed 7, silicon) shift spikes across tick boundaries from ~16 s; disclosed.
- Stage 2 runs in silicon (the intended substrate) with biology as labelled replication for transfer and grid; the knob
  family in silicon only (the exploration failure is silicon's).

## Final audit (R15), against files on disk
Walked R0–R15 against the work order's text and the files listed in [REPORT.md](REPORT.md) (all present, non-empty;
28 per-life ledgers; 35 large files plus draws.npz in `~/nca-scratch-backup/robot_action_20261120/`, 402 MB).
- Stage 0 items: D176 manifest verified ([audit.json](../v/robot_action_20261120/audit.json)); wiring from the graph; body
  wiring identities; passive logging; draws archived; reading bounded to the assigned sections.
- Stage 1: all three arms + all-food in both substrates; drift of informed knobs ~0 (64/64 strong at end in silicon,
  63/64 biology); replay through both substrates including stranded lives; branch applied in the stated order.
- Stage 2: both bounded comparisons, in order; grid screened on 0–7, evaluated on 8–31; one family, baseline + 4 SI
  settings frozen before running, replay screen then one closed-loop finalist; stopped with one causal hypothesis.
- Stage 3 gate written before any construction; failed condition 3 by measurement → R9–R11 not triggered; R12 not
  triggered (no working-behaviour claim, so no live demonstration owed).
- Write scope: only new files in the two lab folders, discrete/NOTEBOOK.md (D178 appended), PROGRAMME.md (status entry),
  QUESTIONS.md (one parked question). No engine/body/brain/catalogue edits (git diff of brains/, creature.py, world.py,
  mixed_feedback.py, units.py, chip.py empty; PARTS.md's diff predates this session). No commit, push or agent.
- Budget: started 14:23, finished about 14:50, within the six-hour cap; one job at a time, one maths thread per worker.
Omissions found: none outstanding. Two analysis bugs were fixed and logged above.
