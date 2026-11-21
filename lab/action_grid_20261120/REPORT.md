# Action grid — report (D184), 2026-11-21

Work order: [../WORK_ORDER_2026-11-20_action_grid.md](../WORK_ORDER_2026-11-20_action_grid.md). Protocol:
[PROTOCOL.md](PROTOCOL.md); predictions frozen before any grid life: [PREDICTIONS.md](PREDICTIONS.md); ledger:
[CHECKLIST.md](CHECKLIST.md); handoff: [HANDOFF.md](HANDOFF.md). Raw rows and tables: `lab/v/action_grid_20261120/`.

## What changed our explanation of poor collection

The catalogue brain (D180) told the right colour at birth ate 0.19 food per 10 s. D181 blamed the explorers'
undirected walk. **This grid says something more specific: the brain collects poorly mainly because the
explorer drowns out the senses.** Turning the existing knobs so that exploration fires less often, and the
motors recover faster and the oscillator runs faster, roughly doubles food and triples net on fresh lives. Halving the
sensory gain is the one clearly harmful change. Stronger sensory gain did not help.

- **Explorer threshold (fires less when higher):** +0.07 [+0.05, +0.09] net per 10 s, within seed, averaged over the
  other knobs (development). It was predicted to *lower* net through fewer encounters (prediction 2, p 0.6): wrong.
  The explorer holds the motors out of action less often, so a body pulse more often drives the motor.
- **Oscillator speed 1.5×:** more food (+0.13 [+0.11, +0.16]) and more distance; on its own no clear net gain.
- **Motor decay 2.5 ms:** no clear marginal effect (+0.02 [−0.02, +0.05]), but all three winners have it, with the
  faster oscillator and the higher threshold (two-factor tables in `dev_tables.md`).
- **Sensory gain 0.5×:** −0.19 [−0.24, −0.15]; 2×: −0.02 [−0.05, +0.01] (inconclusive, not a gain).
- **Bench → life:** across the 54 complete settings, the extra motor events after a *single* sensor pulse rank with
  informed net (Spearman 0.89); the response to sustained input does not (−0.01). Descriptive, predeclared, no others.

So the lever is **sensory authority over a motor the explorer also drives**, helped by movement, rather than sensory gain or
encounter rate alone. That is a within-grid effect, not a unique mechanism: these knobs also change noise and paths.

## Fresh confirmation (128 new seeds, circuit integrated at three step sizes)

All three selected settings improve on the baseline: the Bonferroni-corrected (98.33%) lower bound of the
candidate-minus-baseline informed net is above 0 at every step. None reaches the predeclared practical margin
(+0.10 at every step): at the coarsest step their lower bounds are +0.02, +0.08, +0.08.

| setting (gain, motor decay s, explorer threshold V, oscillator speed) | step DT | DT/2 | DT/4 |
|---|---|---|---|
| g1.0 t0.0025 q0.225 f1.5 | +0.095 [+0.021, +0.170] | +0.179 [+0.105, +0.254] | +0.159 [+0.084, +0.233] |
| g2.0 t0.0025 q0.3 f1.5 | +0.157 [+0.077, +0.240] | +0.246 [+0.177, +0.319] | +0.196 [+0.113, +0.287] |
| g1.0 t0.0025 q0.3 f1.5 | +0.155 [+0.084, +0.224] | +0.217 [+0.141, +0.296] | +0.268 [+0.188, +0.353] |

(Net = (food − poison) per 10 s, final third, informed arm; 98.33% seed-paired bootstrap intervals; full tables in
`lab/v/action_grid_20261120/confirm_tables.md`.)

- **Levels:** the best setting eats 0.45–0.49 food per 10 s told the answer (baseline 0.18–0.22), and about 1.0–1.1
  per 10 s when both colours are food (baseline 0.34). Stranded lives fall from 12–15% to 2–5%.
- **No harm:** all-food collection and stranding pass their no-harm margins for every candidate at every step.
- **The job is not met:** no setting passes D180's absolute gates at any step (food rate ≥ 1/10 s: the
  candidates' upper bounds reach only 0.45–0.57; food − 3·poison and seed-level stranding also fail). Told the answer is not learning.
- **Not physically eligible:** pre-clip rail excursions in 3,295–3,539 of each candidate's 4,608 lives (motors M0/M1,
  the P1 memory, the sensory nodes S0/S1); the baseline has them too (3,038/4,608, P1, S0, S1). The reward evidence is
  diagnostic only. The candidates add motor-node excursions that the baseline lacks.
- **Not converged in the step:** every halving's change interval reaches beyond ±0.05 (e.g. +0.08 [−0.00, +0.17] from
  DT to DT/2 for the first candidate). Point changes of up to +0.09 suggest a real step dependence at DT, and 128
  seeds cannot resolve ±0.05 anyway. Results at DT should not be read as final levels.
- **Shrinkage:** development (native noise) contrasts of +0.22–0.23 over baseline shrank to +0.10–0.16 at DT
  (coupled noise), as predicted (about half). The baseline itself scores higher under coupled noise (0.13 vs 0.06).

## Predictions scored (frozen 2026-11-20, [PREDICTIONS.md](PREDICTIONS.md))

1 baseline reproduces D180 (0.97): **yes**, 384/384 on 10 checks. 2 gain 2× positive (0.6): **no** (−0.02,
inconclusive); gain 0.5× negative (0.65): **yes**; threshold 0.30 lowers net (0.6): **no, raises it**;
oscillator 1.5 more path (0.7): **yes**. 3 best development net 0.10–0.25: **above** (0.29). 4 shrink by half: **yes**;
at least one improved (0.35): **all three**; practical (0.10): **no**. 5 no absolute food gate (0.95): **yes**.
6 not physically eligible (0.8): **yes**. 7 convergence within ±0.05 (0.6): **no**. 8 no-harm (0.6, 0.5): **yes, both**.

## Denominators and failures

- Benches 31,104/31,104 (1,296 named invalid: oscillator 0.75 puts one part below 1 pA on 15 of 40 seeds).
  Development 31,104/31,104 (4,536 named invalid, same cause): 54 of 81 settings complete; the 27 at oscillator 0.75
  could not be selected. Confirmation 18,432/18,432 valid (realised limits: 0 of 1,536 engines failed).
- Interruptions: a reboot during development (resumed, 18,505 rows kept intact); an out-of-memory kill during
  confirmation (resumed with 4 workers). The 12 h envelope was exceeded at the user's decision ("Complete all work now").
- Audit discrepancy: exact ties in net at ranks 12–13, 31–32, 33–35 are ordered by floating-point rounding, not by
  the food tie-breaker; top three unaffected (CHECKLIST, 2026-11-21T12:30Z).
- Costs: the winners draw 165 nW (229 nW at gain 2) against the baseline's 100 nW, and fire about 1,215 motor pulses
  a life against 818; parts unchanged (770 transistors, 97 resistors, 27 capacitors). Reward, activity, power and
  material are reported separately; equal parts do not mean equal cost.

## Bits

The informed arm is told the colour bit at birth; nothing here learns it from taste, so nothing here measures bits
learned. The grid asks how much of the told bit the body can turn into food: at best about 0.3 net per 10 s on
fresh lives, against the job's ≥ 1 food per 10 s at food:poison ≥ 3.

## Checked independently versus inherited

Independently checked (`ag_audit.py`, without the analysis code): ledger and archive hashes for all three stages; key
sets against freshly generated job lists; every development setting's informed net and food; the selection; all nine
primary point estimates. Inherited: bootstrap intervals and D180 gate arithmetic (`ag_analysis`, D180's `analyse.py`),
the realised physical limits (`ag_jobs.realised_ok`), the simulator itself.

## Reproduce

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 AG_WORKERS=4 .venv/bin/python lab/action_grid_20261120/run.py all`
(code revision 1e70cce plus this report; simulation hash 5f2066bf58ecb0e5; `.venv/bin/python lab/action_grid_20261120/ag_audit.py`
for the audit). Archives (git-ignored): `lab/v/action_grid_20261120_{bench,develop,confirm}.pkl`.

## Obligations

| ID | Obligation | Status |
|---|---|---|
| R0 | Freeze inputs, plan, budget | done |
| R1 | Observer/runner, identity checks | done (17/17) |
| R2 | Every fixed bench | done, 31,104 |
| R3 | Every development life | done, 31,104 |
| R4 | Historical reconciliation, costs | done, 384/384 match |
| R5 | Development analysis, selection | done; tie-ordering discrepancy recorded |
| R6 | Fresh confirmation, 3 steps | done, 18,432 |
| R7 | Uncertainty, physical, convergence | done |
| R8 | Omission audit, handoff, docs | done |
