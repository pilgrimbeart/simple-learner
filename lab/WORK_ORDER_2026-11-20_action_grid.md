# Work order — fixed catalogue action grid after D182

**Status: prepared, not executed.** The user requested an unambiguous plan and then explicitly preferred
many cheap experiments over an executor choosing branches. This supersedes D182's two-hour conditional
proposal. Once execution is commissioned, this file is the sole work order. Preparation does not launch
an agent or simulations. One executor, no delegation; work on main, no commit or push.

## 1. Question, scope and authority

Which EXISTING action settings change useful collection, sensory transfer and motor recovery in the
D180 catalogue brain? Test a fixed factorial grid, all its controls, then fresh confirmation of three
mechanically selected settings. This is informed action and engineering diagnosis, NOT taste learning,
autonomous repair, a generality test, or proof that the selected settings are optimal.

Read AGENTS.md, PROGRAMME's current entry, D182, the original DESIGN.md, and this file. D182 owns the
research rationale (Arthur–Boahen's distinctions among input-to-spike dynamics); no additional reading,
web research, new mechanism design, or programme queue work is assigned. Return research questions to
the reviewer in HANDOFF.md. Existing rules about the unchanged body/interface/noise and physical limits apply.

**Allowed writes:** `lab/action_grid_20261120/`, `lab/v/action_grid_20261120/`, and large ignored
`lab/v/action_grid_20261120_*.pkl` archives. At finish, add one dated entry/current-state update in
`discrete/NOTEBOOK.md` and an execution-status link at the top of PROGRAMME.md. Park tangents in
QUESTIONS.md, at most five bullets. No other files may be edited. Original D180 sources, results and
historical predictions are read-only. Import or wrap them; do not patch production modules, body,
engine, noise, graph topology, thresholds outside the four declared settings, learning rules or pulses.
Do not inspect protected/sealed test contents. No SPICE, learning, writer tuning, new circuit primitive,
shared-reading experiment, recruitment, ideal motor controller or in-life parameter change.

## 2. Obligation ledger and time envelope

Before implementation create CHECKLIST.md with the following rows. For each: status, evidence paths,
expected/actual counts, blocker and remaining work. Status is `done`, `not triggered` with exact named
branch evidence, or `incomplete`; `pending` is allowed only during work. A failed scientific result can
be done. Expiry, missing data, a crash or failed implementation is incomplete, never a negative result.

| ID | Mandatory obligation | Acceptance evidence |
|---|---|---|
| R0 | Freeze inputs, plan and execution budget | Manifest, protocol, predictions, job ledgers, start/deadline |
| R1 | Implement observer/runner and identity checks | Exact baseline reproduction and named fixtures |
| R2 | Run every fixed bench | 31,104 records, or explicit incomplete records |
| R3 | Run every development life | 31,104 records, or explicit incomplete records |
| R4 | Reconcile historical reporting and costs | Original-arm audit and per-setting/arm costs/activity |
| R5 | Produce complete development analysis; select top three by §8 | All 81 rows and selection calculation |
| R6 | Fresh confirmation at all three integration steps | 18,432 lives if three candidates selected; complete ledger |
| R7 | Report uncertainty, physical violations and convergence | §9 tables including every selected candidate |
| R8 | Final omission audit, handoff and documentation | REPORT, CHECKLIST, reproducible commands, links |

**Hard budget: 12 hours elapsed**, measured from execution start, including coding and reports. Suggested
allocation: R0/R1 2 h, R2 2 h, R3/R4/R5 3 h, R6/R7 4 h, R8 1 h. These are planning allowances, not permission
to drop obligations. Reserve the final hour for an honest handoff. The 12 h replaces the superseded 2 h
proposal because the user explicitly chose a larger fixed batch. No automatic extension.

One process pool at a time, at most seven workers, each with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`. Capture parent PID and logs; do not interrupt
another job. If another long job is present, wait by its identified PID within the budget or hand off.
After implementation time trials (§5), estimate ALL remaining mandatory work, including three-step
confirmation and reporting, with 1.25x measured wall-time allowance. If it cannot fit, write the exact estimate
and incomplete ledger; do not silently reduce seeds, arms, settings or steps. Complete independent saved-data
reporting and stop. Checkpoint each completed job so a later authorised continuation resumes without reruns.

Routine bugs restoring this specification are fixed autonomously, logged, and affected checks rerun.
Never change settings, ranking, metrics, sample size or bounds to rescue results. Do not ask which scientific
branch to take: all named experiments run. A scope change is a separately proposed amendment, not execution.

## 3. Exact grid — no executor choices

`variants.py` owns the transformations and `PLAN.json` the 81 configurations. Both are prepared with this
work order; verify their hashes at start. The graph equals D180 v1 at
`g1.0_t0.005_q0.15_f1.0`. In the fixed Cartesian product:

| Factor | Values | Exact change |
|---|---|---|
| Sensory gain multiplier | 0.5, 1, 2 | Multiply side_0/1 and plastic_0/1 gains |
| Motor decay time | 0.0025, 0.005, 0.010 s | Keep motor C; multiply all currents into M and its bias by 0.005/tau; divide its R by that factor |
| Exploration readout threshold | 0.15, 0.225, 0.30 V | Set offsets of explore_motor_0/1 only |
| Oscillator speed multiplier | 0.75, 1, 1.5 | Multiply all gains INTO X/Y/B and their biases; divide non-memory X/Y resistances by multiplier |

Apply all changes symmetrically, in the helper's order. No other quantity changes. Oscillator speed is a
nominal dynamics change, not an exact stochastic time rescaling: noise must continue to follow the engine's
current-dependent law. No world frequency/phase is supplied. The fixed grid is an offline informed search,
not a claim that the brain can tune these knobs itself.

Preparation tested all four side wirings and exact baseline graph equality; all 81 nominal graphs pass
D180 validate(). Static rejected alternatives during preparation: speed 0.5 puts a bias writer below 1 pA;
speed 2 exceeds the self-loop rate limit. No simulations or reward observations informed this grid.
No substitute values may be introduced later.

Build the full graph and draw mismatch before removals, preserve node/edge order and RNG streams. Retain
D180 seeds, initial states and random wiring scheme. Report realised parameters and physical checks;
no redraw or exclusion of inconvenient components. Static/realised safety-check failure is a named invalid
job, not permission to change the circuit. A numerical nonfinite state stops that job with its failure log.
Saved invalid jobs remain in denominators, prevent a complete performance claim and are never scored as zero.
Rail clipping does NOT cancel other experiments: continue measuring unchanged v1-style bounded integration,
but flag the candidate as physically unvalidated. Do not bypass the engine's rails or label clipped action valid.

## 4. Runner and immutable outputs

Implement `run.py` with stages `check`, `bench`, `develop`, `analyse`, `confirm`, `report`, and `all`.
`all` executes that order with no scientific-pass prompts. Every stage accepts `--dry-run` (lists exact
jobs/counts, no simulation). `--resume` runs missing keys only after verifying hashes/configuration of
completed rows; refuse overwrite and incompatible resumes. No invocation of D180's learn stage.

Before scientific runs freeze manifest: HEAD, dirty input/source/dependency hashes, this work order,
variants and PLAN, units, worker count, all job keys, metric code, ranking, seeds, windows and expected
counts. Keep commands, stdout/stderr, failed attempts and amendments. All output keys include
(stage, configuration, arm/schedule, seed, poison/P, channel, integration ratio, noise mode).

Keep compact per-job results in gzip JSONL, all tables JSON+Markdown, plots optional with labels/line styles.
Store large traces only under the allowed ignored archive pattern, checked by `git check-ignore` before
writing; record absolute paths and hashes. No sole copy in /tmp. Do not retain full per-node substep traces
for every life: aggregate online; keep pulse/event records and the D180 ten-node per-body-step traces for
baseline development and confirmation candidates. Do not choose illustrative lives by outcome.

## 5. Implementation, identity and preflight — R0/R1

Use unchanged `creature.Life` and the original Engine/_step; the observer gets hidden body quantities only
after/before stepping, never feeds them back. No copied body integrator or software-generated motor spikes.
Derive life duration/step counts from units.TICK and 100 s, rather than introducing a new timing constant.
Candidate sees only stimulate/taste/step. Birth-time informed P uses the original harness.

Required fixtures: baseline graph equality all four wirings; observer on/off exact meals, body firings,
final state and RNG state; identical-arm reproduction; parameter transforms affect exactly the named
fields; surviving-edge mismatch/noise identity after removal; no event-buffer overflow; no-meal/zero-poison
metrics; duplicate/missing ledger detection; correct final-third boundaries; held-positive motor gives one
event until re-armed; ranking tie-break; coupled noise summation; no hidden labels reach the brain.
Reuse original passing fixtures only when input/source hashes match; test all new observer/transform code.
A changed logging adapter must reproduce the original integration on identical pulses/noise before use.

Preflight: baseline, development seed 8, 1 s informed red, at each ratio 1/2/4 with coupled noise; plus
baseline bench silent seed 0, 10 s. These are timing/check runs, not selection data. Use separate output keys.
Measure native development runtime on baseline seed 8 informed red 100 s; this row may be reused in R3
only if it has the exact frozen job and output schema. Predict total runtime using these measurements,
including observation overhead; do not use reward to change the plan.

R1 validation also reproduces baseline native development seed 8 red, blue and all-food against the saved
D180 ledger/archive: meals, firing counts, P/E/X/M traces, final arrays hash and body wiring. Historical
ledger lacks the full motor-event sequence: do not claim historical event-time identity from counts.
For observer identity, compare the newly run on/off event sequences exactly. If identity fails, diagnose
and fix observer/adapter bugs; dependent new results remain invalid until checks pass. No reinterpretation
of a changed life as a fresh sample.

## 6. Fixed benches — R2

For EACH of 81 settings run exactly: component seeds 0–7 × P={0,0.15,0.30} V (both memories same)
× removal={none,no_explore} × sensor channel={0,1} × schedule={silent,single,train,sustained}.
That is 384 jobs per setting, **31,104 jobs**, each 10 s, native noise and original circuit step.
Taste withheld. No bench pass/fail cancels development or confirmation.

Use one jitter j ~ uniform [0,0.009] s per (seed,channel) from
`default_rng([seed,182,channel])`, shared by schedules, settings, P and removals.
Body-amplitude/duration sensor pulses only:
- silent: none;
- single: 1+j s;
- train: 1+j+0.02*k s for k=0..9;
- sustained: 1+j+0.02*k s for k=0..99.

Record per motor events, re-arms, first-event time, time above zero, time not armed, longest not-armed
interval, and min/max V; P drift, every node's pre-clipping excursions, slew and power. Event/re-arm times
come from the engine; continuous occupancy must be integrated from substep states by a passive observer,
not inferred from body-step samples. Report [0,1), [1,3.25), [3.25,10) s separately.
Compare each active schedule against silent using common draws, and each setting against baseline.
Report both motors by stable ID and as fixed-side/other-side relative to stimulated channel. The quiet
controls are reused arithmetic references, not independent repetitions. Signed event differences can be
negative. Sustained response is descriptive; no invented target firing rate or learned behaviour claim.

## 7. Fixed development lives and observation — R3/R4

For EACH setting run the exact D180 R5 product, seeds 8–39, life 100 s, native noise:
- red and blue poison separately, each with informed, neutral, reversed, no_explore, no_sensory;
- all-food once per seed each with informed and neutral.
Exactly 12 lives/seed, **384/setting; 31,104 total**. Taste withheld in every arm. Correct P is set ONLY at
birth; original false writes remain measured, never silently clamped. The removal arms use informed P.
No learning, no-writer arm or adaptive tuning. All 81 settings run even if baseline or benches fail.

Passive observation, same schema in every arm:
1. Original D180 per-life meals/windows, no-meal/never-moved, motor events, powers, realised draws, P drift,
   clipping/slew. Record source-node engine event counts for every named surviving connection; these are
   labelled event proxies, not the full cost of continuous analogue communication.
2. Per-edge gated duty/mean gate factor from the engine's own gate definition, integrated at circuit step;
   ungated edges labelled ungated. Count actual parts with existing chip/minimal.spice accounting, no SPICE.
   Report power, material, motor energy (existing guessed energy/firing) separately. Memory pump energy
   remains unmeasured. Never call the event proxy communication energy.
3. Per motor high/unarmed durations, longest unarmed interval, actual event/re-arm times; sensory pulses
   with physical onset times. Source events must not be confused with delivered body motor events: Life
   delivers events on its unchanged body step.
4. At each body's pre-step state log its position, heading, speed/spin and `sees()` strengths, using no RNG.
   Integrate time seeing either colour (strength >0), time seeing neither and mean visibility. Record total
   path length with wrapped successive displacements, absolute angular travel with unwrapped headings,
   and meals. Visibility is not a count of distinct encounters; do not introduce block-identity attribution.
5. At body delivery resolution, sum min(left_count,right_count) across steps as simultaneous event pairs;
   report paired fraction 2*pairs/total motor events (missing if zero). Also report the fraction of circuit
   motor events with an opposite-motor event within 0.010 s (nonexclusive, labelled as such).

For each sensory pulse report whether each motor was unarmed immediately before that onset, and counts
in [onset,onset+0.05) and [onset+0.05,onset+0.25) s. These windows may overlap; aggregate per life then seed,
not as independent samples. This is temporal association, not pulse-attributable excess. Branchless benches
supply the controlled input contrasts. Do not claim a specific pulse caused an event from proximity alone.

Baseline R3 must match all original 384 ledger keys/meals/counts; check trace hashes where archived. R4
writes `historical_reconciliation.md`: correct the stale 'no lives' statements by reference, not by editing
the original report. Reconstruct required costs/activity with these reproduced lives. Discrepancies have
explicit rows and prevent an unqualified completion claim.

## 8. Development analysis and deterministic selection — R5

Use D180 metric conventions: [200/3,100) s primary; net=(food-poison)*10/(100/3); food and poison separately;
first two thirds/full life descriptive; no meals in full life means stranded. Pair red/blue within seed,
then use seed as resampling unit. All-food has one life/seed. Bootstrap 10,000 resamples, RNG 182.
Development 95% intervals are exploratory, explicitly subject to selection over 81 settings.

Required tables: all 81 settings × all seven named arm groups (the five poison-paired groups plus two
all-food groups); informed-minus-neutral, informed-minus-reversed, informed-minus-no_explore,
informed-minus-no_sensory, and all-food informed-minus-neutral. Report physical failures and missing rows.
Provide each factor's marginal contrast relative to its baseline level, averaging over the SAME other
factor settings inside each seed before bootstrap, plus all six two-factor mean tables. These are effects
within this grid, not proofs of the unique underlying mechanism; speed also changes noise and trajectories.
Report bench-to-life associations descriptively, no additional correlation fishing or post-hoc subgroups.

Select exactly THREE nonbaseline configurations from those with complete finite development results:
sort by descending mean informed final-third NET, then descending mean informed FOOD, then ascending
configuration ID string. Exclude baseline from selection; do not exclude clipping configurations or select
on confidence intervals. Rail flags follow them into confirmation. This ranks diagnostic action settings,
not physically valid brains. No practical/significance threshold gates confirmation. Save ranked list,
selected IDs, inputs and hash BEFORE fresh results. Fewer than three complete configurations means R5/R6
incomplete: report, do not invent replacements. Numerical/implementation-invalid jobs cannot win.

## 9. Fresh confirmation and refinement — R6/R7

Run baseline plus all three selected configurations on 128 fresh seeds, EVERY arm from §7, at ratios
1,2,4 (DT, DT/2, DT/4), coupled circuit noise at ALL ratios. Exactly
**4 configurations × 128 seeds × 12 lives × 3 ratios = 18,432 lives**.
Do not reuse native baseline as coupled baseline. All three steps run regardless of coarse result or rail
failure. No selection replacement, sample expansion or early stopping on reward. The body tick is unchanged;
this checks circuit integration, not full-body convergence. Preserve all-world paired draws and stable IDs.

Seed allocation is mechanical: first unused 128-seed prefix of blocks starting 2027112000+1000*k, k=0,1,... .
Check nonsealed experiment source/configuration/manifests and seed ledgers for prior exposure (ranges as
well as literal seeds), log paths and conclusions. Do not open protected test contents. If reserved/uncertain,
move to next block. Freeze block before jobs. Fresh seeds are not unfamiliar task families.

Use primary contrast: candidate informed net minus baseline informed net, paired by seed at each ratio.
Report point estimates and ordinary 95% intervals for all metrics. For claims across three selected settings,
also report 98.333333% two-sided bootstrap intervals for each primary contrast (Bonferroni for three,
quantiles 0.008333333 and 0.991666667). State the correction and its limits; no multiplicity-adjusted claim
for unassigned secondary endpoints. No candidate is declared improved unless its corrected primary lower
bound >0 at ALL three ratios. Report +0.10 net/10 s as the predeclared practical-improvement threshold:
call the improvement practically established only if those lower bounds exceed +0.10 at every ratio.

Also report D180 absolute food, ratio and stranding gates using its equations/seed-level Wilson convention.
An action-only success is not a learner. No-harm in all-food collection requires candidate-minus-baseline
food-rate lower 95% bound >-0.05/10 s at every ratio; no-harm in stranding requires upper 95% bound <+0.05.
Do not infer equality from an interval crossing zero. Physical eligibility requires all completed candidate
lives at all ratios within physical contracts, including zero pre-clipping excursions; otherwise label
reward evidence diagnostic only. Never hide a clipped life in a mean.

Numerical convergence: paired-seed 95% interval of the change in candidate-minus-baseline informed-net
contrast for EACH successive halving must be contained in [-0.05,+0.05] net/10 s. Apply the same margin to
all-food food contrasts; stranding contrast changes must lie inside [-0.05,+0.05] proportion. Show levels
as well as differences, all candidates. Failure is a refinement limitation, not a reason to tune or add steps.
These are diagnostic confirmation results; production adoption, live demonstration and learning need a
separate assignment. Do not claim a live-demonstrated working brain from this work order.

## 10. Finish, acceptance and stopping — R8

REPORT.md leads with what changed our explanation of poor collection. Include exact denominators, all
failures, development selection and fresh outcomes, physical/noise/cost limits, and one table of every R0–R8
obligation. An inconclusive result is acceptable; omitted required work is incomplete. Independently
regenerate tables from saved per-job rows, verify expected key sets and hashes, and audit every requirement
before saying complete. Record what was independently checked versus inherited.

HANDOFF.md is at most one page: which fixed comparisons support recovery, sensory authority or exploration
as useful levers; what remains confounded; whether any physically eligible informed improvement survived
fresh seeds and refinement. Propose at most one next question. Do NOT design a repair or launch the next
experiment. If no candidate helps, report the tested limits without declaring the catalogue incapable.
No larger grid, new source search, changed graph, writing fix or autonomous continuation is authorised.

Update notebook current state and add a dated investigation entry linking this protocol, manifest, raw
ledgers and final report. Update PROGRAMME execution status only; do not rewrite predictions/history.
Return the exact resume command if incomplete, or the reviewer decision needed after completion. STOP.

Required executable interface after implementation, from repository root:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/action_grid_20261120/run.py all
```

The runner is to be implemented by the executor; this preparation package currently supplies only the
static variant helper and PLAN. Every stage must support `--dry-run` and safe `--resume` as specified.
