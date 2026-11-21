# Work order — execute the catalogue-native starting-brain experiment

**Status: prepared, not launched.** User approved the new starting approach and requested design plus
experiments for a cheaper agent. This is the sole work order for that future executor. No delegation.
The starting design is [DESIGN.md](catalogue_brain_20261120/DESIGN.md), with exact graph in
[design.py](catalogue_brain_20261120/design.py). D180 in discrete/NOTEBOOK.md owns the investigation record.
The user chose to retire the historical neuron as the starting point: do not spend this assignment
repairing or re-running D178. Its review informs checks on this new adapter, not an extra work queue.

## 1. Execution discipline and budget

Read AGENTS.md, README goal, PROGRAMME's current entry, D180 and the two design files. Research rationale
is supplied; no independent literature search or new-mechanism study. Questions requiring research go
back to the reviewer, while independent assigned work continues. Do not launch agents, commit or push.

Allowed writes: new files under `lab/catalogue_brain_20261120/` and `lab/v/catalogue_brain_20261120/`,
plus large trace archives named `lab/v/catalogue_brain_20261120_*.pkl` (covered by existing ignore rules),
plus an appended execution record/current-state update in discrete/NOTEBOOK.md, a current status in
PROGRAMME.md, and parked questions in QUESTIONS.md. Preserve design.py and DESIGN.md as v1 inputs;
put any permitted revision in a separately named/versioned spec. Never overwrite raw results or freezes.
No production edits, engine/noise modifications, dependency changes, SPICE, body/interface changes,
new primitive, protected-test access, automatic repair design, recruitment or broader search.

**12 hours hard wall-clock cap** from executor start, including implementation, runs and reporting.
Stage budgets: implementation/preflight 2 h; component/assembly bench 2 h; informed action 1 h; learning
1 h; conditional validation 4 h; report 1 h; contingency 1 h. Reserve reporting before new compute.
One compute job at a time, at most 7 process workers and one maths thread each; record explicit PIDs.
Do not stop somebody else's job or change files an active job may import. Wait/report if the laptop is busy.

Before EACH stage estimate all its required work from the preflight timing, including controls and analysis,
and record the estimate. If it cannot fit its remaining envelope, do independent accounting/reporting and
mark the stage incomplete with the measured runtime estimate. No selective controls or partial success claim.
Unused stage time may move to required later work within 12 h, never to extra variants/seeds/research.
Budget expiry is incomplete, not "not triggered". Runtime failure is not a negative scientific result.

Create CHECKLIST.md first, using exactly R0–R12 below. Each row: status (pending/done/not triggered/incomplete),
trigger, artifact/command, measured gate, unresolved work. Log routine bug fixes, preserve affected outputs,
and rerun affected checks. Substantive changes to design beyond §4, arms, margins, seeds, durations or
analysis go in AMENDMENT_PROPOSED.md and are NOT executed. Finish triggered obligations before optional work.

| ID | Mandatory obligation | Trigger / acceptance artifact |
|---|---|---|
| R0 | Checklist, immutable protocol, predictions, manifest, budget | Always; before data |
| R1 | Adapter, state/noise/identity/interface tests and schematic | Always; checks.json, graph and code hashes |
| R2 | Parts/power/limits and evidence feasibility | Always; cost table, sampled component arrays, estimates |
| R3 | Null/write/retention and oscillator/output benches | R1 valid; all cases, controls and denominators |
| R4 | Isolated sensory effect, overlap, recovery and frozen revision decision | R1 valid; paired state/noise checks and per-case data |
| R5 | Informed action plus causal removal controls | R3/R4 gates pass; complete development matrix |
| R6 | Learned vs writers removed, taste withheld, informed and all-food | R5 gate passes; complete matrix and evidence accounting |
| R7 | Fresh comparison, fixed sample size and exposure audit | R6 gate and runtime feasibility pass |
| R8 | Both integration halvings on required contrasts | Same trigger as R7; must be budgeted with it |
| R9 | Costs, uncertainties, failed lives, acquisition/loss accounting | Every completed experiment |
| R10 | Reproducible live demonstration | Any confirmed working-behaviour claim; viewer command and observation |
| R11 | At most one-page next local-repair question | Always; local signals, ambiguity, costs; proposal only |
| R12 | Independent artifact/obligation reconciliation and handoff | Always; REPORT, CHECKLIST, notebook/programme status |

## 2. Implementation and preflight — R0–R2

Implement `brain.py`, `run.py`, `analyse.py`, `checks.py`, `bench.py`, `view.py` in the assigned lab folder.
Use the exact v1 graph, no Circuit.neuron/synapse convenience macros. Use existing `creature.Life` via a
brain factory, and only its existing stimulate/taste/step interface. Report motors using engine spikes;
no harness threshold/reset or computed exploratory events. Viewer may register a lab factory in-process
and invoke creature.watch; no production registry edit. Render an explicit labelled schematic, preferably
using existing schematic.py helpers in a lab renderer; do not leave the old-neuron picture as this design's
schematic. Colour never carries the only distinction.

For circuit refinement use a lab adapter to the unchanged `_step`, with exactly the same per-second
noise law, continuous pulse overlap integration and existing event counting; no local rewrite of dynamics.
At DT the adapter must reproduce Circuit.pulse/run on identical arrays/noise. At DT/2 and DT/4 use coupled
Brownian increments (sum fine independent normals/sqrt(ratio)); retain mismatch and parameters in seconds.
The body's TICK stays unchanged; report this as circuit-integration refinement, not full body convergence.
No missing-noise implicit connection filters (`tau=0` on every edge).

Stable node/edge IDs: build the full graph and draw arrays before removing connections in controls; retain
original IDs for surviving mismatch/noise streams. Removed parts contribute neither current nor power;
recompute cost for actual controls. Do not implement removal by disabling noise, resetting state or zeroing
randomly inconvenient offsets. Different gain variants share draws but scale their nominal parameters.
Archive original index-to-name maps, realised arrays, initial states and RNG seeds/states.

Required checks: identical-arm reproduction; logging on/off identical; null stimuli versus explicitly
empty queue identical; different chunk sizes identical at common output boundaries (resolve differences
before causal estimates); saved-state clone restores V, pending pulses, noise position and spike arming;
paired intervention trajectories identical up to the intervention. Check sensor/motor wiring independent
of graph variant, and no use of hidden world labels in learning. World RNG streams diverge after actions
change observations: paired seeds do not imply identical closed-loop inputs. R1 failures stop dependent
inference, not independent documentation. Include fixtures for midnight/zero movement, zero meals/poison,
loss followed by reacquisition, duplicate/missing rows, and full-period output above zero without re-arming.

Static/physical checks: all nominal and realised C/R/current limits, signed slopes, supply fading,
per-element and aggregate slew at recorded states, no numerical clipping at supply (track pre-clipped
updates, observation only), no invented interior clamps. Calculate transistor/resistor/capacitor/source
counts with chip.py/minimal.spice.count without running SPICE; explain any port/rail/memory-driver cost
not represented. Include all four retained states, oscillator bias writers, gate circuitry, steep-slope
preamplifiers and motor readout boundary. Record memory high-voltage supply energy as unmeasured, not zero.
This is a chip-constrained noisy block-model candidate, not fabricated-chip or SPICE validation.

Freeze manifest.json: HEAD, dirty input hashes (including work order/design), commands, dependencies,
arrays, all schedules/seeds, units, arms, metric code, predictions and expected row counts. Create
PREPARATION.md with exact runnable commands; run.py must have stage choices `check`, `bench`, `action`,
`learn`, `confirm`, `refine`, `report`, and `--dry-run` to list jobs without simulation. One driver may call
separate scripts; tools must refuse overwritten outputs and refuse later stages without saved gate passes.
Preflight compiles on two development seeds for 1 s; never use its reward to select a design.

## 3. Component and assembled-response tests — R3/R4

Use component seeds 0–7, full silicon noise/mismatch, with both sensor-to-side wiring outcomes represented
by the prescribed random draws; also explicitly test all four side combinations on seed 0 as wiring fixtures.
All tests use both motor channels and both sensory channels, retaining failures. Initial states are those
of DESIGN.md, including startup; do not condition on circuits that happened to start correctly.

A. **Quiet/startup/retention, 100 s:** full graph, no inputs, P neutral; record oscillator startup, amplitude,
frequency, duty, B drift, motor firings/re-arming and false P writes. Repeat P initial 0 and V_TYP.
P drift must be <=0.01 V, no pre-clipping rail excursions. Repeat oscillator bias-writer removal as a
labelled comparator; failure of removal is not required, all its counts/costs reported. Both full-design
motors must have at least 10 firings in [10,100] s per seed; no requirement for a body-derived firing rate.

B. **Writes:** body-amplitude inputs only, not direct state drives in candidate. After 1 s, one S pulse,
then positive or negative T at delays {0.005,0.05,0.2} s; independent schedules for both channels/signs.
Observe 1 s after taste. Repeat no S, no T, and both S simultaneously controls. Repeat a 10-pulse sensor
train at 0.02 s spacing followed 0.005 s later by T, to test overlap/overshoot. Deterministic schedules are
bench stimuli only, continuously jitter their common start uniform [0,0.009] s. Required gate: at 0.005 s
single-S delay, corresponding P changes in correct direction by >=0.001 V and <=0.15 V in all 8 seeds,
both signs/channels; unexposed P and no-S/no-T controls change <=0.01 V. Other delays/train are diagnosis,
not additional pass thresholds; all rail excursions fail. Do not retune learning from these results.

C. **Sensory authority and overlap:** run a 10 s no-input prefix of the full graph with P=0, V_TYP/2 or V_TYP
(both P same for this bench). Test the next 16 input times drawn independently uniform over [10,20] s
per seed/channel. Cache exact prefix snapshots to share the expensive prefix across forks; do not
rerun a 20 s prefix for every short branch. Each individual trial uses an IDENTICAL prefix to just before that pulse and forks
present/omitted trajectories with the same future noise and unchanged other inputs. One pulse differs
per pair; no cumulative pulse thinning. Count excess events on both motors over 0.05 s and report the
next 0.2 s (phase shifts/catch-up), plus voltage extrema, first-event latency and re-arm latency.
Repeat with a second input after {0.005,0.02,0.05,0.2} s from the first, pairing second present/omitted
from the common first-pulse history. Repeat with exploration-to-motor edges removed, retaining oscillator
states. Bin overlap by oscillator phase observed by the analyst, never available to the brain.

R3/R4 progression gate: A/B gates pass, full circuit no rail violations; on isolated single pulses averaged
over times, seeds and channels, side-motor excess in 0.05 s >0.25 and plastic-motor excess(P=V_TYP)
minus excess(P=0) >0.25. Report 95% intervals but these are exploratory mean engineering gates, not
confirmation. Keep all events including negative excess; do not require exact one-spike relaying.
A failed gate does not prove the catalogue incapable. Identify first loss: input, writer, oscillator,
readout saturation/recovery, or sensory authority. Complete independent A/B/C tests even if one fails.

## 4. Exactly one conditional revision, never a sweep

If R3/R4 fail due to **motor event formation/overlap**, and the traces predict a repair, one revision may
change exactly ONE of these families, in both motors symmetrically:
- sensory connection gains (fixed and plastic together): multiplier 0.5 OR 2;
- motor output time constant: 0.0025 OR 0.010 s, keeping C and nominal rest -1.5*V_TYP fixed;
  scale ALL currents into M by old_tau/new_tau so DC levels stay fixed;
- exploration readout threshold: 0.75*V_TYP OR V_TYP, leaving oscillator/source states unchanged.
Choose ONE value from a documented transfer/recovery calculation before running it; no screening all
choices. Preserve v1 and state predicted directional effects. Repeat ALL R3/R4 and checks/costs for v2.
If both pass retain v1 (simpler provenance); v2 is selected only when v1 fails and v2 passes the same gates.
If a different failure, oscillator failure, false writing, inadequate write sensitivity, or a second failure
requires another mechanism, no revision is authorised. Report exact cause and stop dependent stages.
A bug correction that restores the specified graph is not a scientific variant, but must be logged/rechecked.

## 5. Closed-loop informed action — R5

100 s lives, development seeds 8–39, each red/blue poison, fixed final third. SAME chosen graph/draws:

| Arm | Birth-time valence controls | Change |
|---|---|---|
| informed | food P=V_TYP, poison P=0 | taste withheld |
| neutral | both P=V_TYP/2 | taste withheld |
| reversed | food P=0, poison P=V_TYP | taste withheld |
| no exploration | informed | remove only explore_motor edges, taste withheld |
| no sensory steering | informed | remove side/plastic edges, taste withheld |

Also all-food lives, once per seed (poison=None), informed both P=V_TYP and neutral P=V_TYP/2.
Informed initialization is performed by the privileged harness after Life exposes wiring and before any
step; candidate brain never reads colour/hidden valence. All oscillator bias adaptation remains enabled.

Gate to learning: informed-minus-neutral AND informed-minus-reversed lower paired 95% bounds exceed
+0.10 net food per 10 s, informed food-rate lower bound >=1 food/10 s, and informed no-meal fraction
point estimate <=0.20. The last is an exploratory opportunity gate, NOT the <=5% finished-job criterion.
Removal comparisons test mechanism, not mandatory wins: report both signs and intervals, including if
removing exploration helps. If informed fails, finish diagnosis using existing traces only; no more
closed-loop tuning, new grid or learning runs. Do not call its fixed setting an optimal-policy bound.

## 6. Learning and controls — R6

On the SAME development lives, keep all graph parameters and explorer settings fixed:
- learned: neutral birth P, normal taste;
- writers removed: neutral P, taste still delivered, remove only four T-to-P writer edges;
- taste withheld: neutral P, all writers present, Life learning=False (reuse neutral R5 output if hashes match);
- informed: reuse R5 (P correct, taste withheld).
Also all-food learned and writers-removed; reuse informed all-food. No resampled duplicate all-food worlds.

Unknown: one binary colour valence, balanced prior. Evidence: causal sensor/taste histories, acquired
through this arm's own actions. Before reading reward contrasts calculate available tastes/s over fixed
life and after movement, local E distributions at taste, simultaneous eligible writers and signed write
signal versus substrate noise. Count independent exploratory sources as two, credit overlap from E,
not the number of machine workers. Estimate whether predicted write size × available encounters could
move P appreciably within 100 s. Report incorrect credit using observer meal labels only. No fictitious
sum of per-taste bits; informed reference supplies the bit and is an opportunity reference, not a bound.
No exact Bayesian calculation is required: state that the optimal same-senses history model is unknown.

Development gates for confirmation: learned-minus-writers-removed lower paired 95% bound >+0.10 net/10 s;
learned all-food minus writers-removed all-food lower bound >-0.05 food/10 s; learned minus writers-removed
stranding upper bound <+0.05. Also learned meets absolute job confidence criteria in §8. Report learned vs
informed gap and taste-withheld contrast separately; do not substitute a favourable contrast for the primary.
If gates fail or evidence inadequate, stop with cause/uncertainty, not a redesigned learner or longer life.

## 7. Fresh confirmation and circuit refinement — R7/R8

Triggered only by §6 gates, checked code/physical contracts, and budget for the ENTIRE stage including
both halvings. Use development primary seed-paired differences with sample SD s. Choose
N = max(128, 32*ceil((1.96*s/0.05)^2/32)); if N>256, defer as incomplete precision/budget requirement.
No fresh sample expansion or re-selection. Reserve seeds 2027010000..2027010000+N-1; audit all repository
experiment manifests/log indexes for prior use before freeze. If used, choose the first unused complete
256-seed block advancing by 1000, recording the search. These are ordinary fresh seeds, no new family.

At DT, DT/2, DT/4, all N seeds, run learned, writers-removed, informed, each red/blue poison, and all-food
learned/writers-removed once per seed: exactly 8*N*3 lives. Same worlds, parameters, node IDs, draws and
coupled circuit noise. Freeze this Cartesian product in a job ledger before execution. No omitted failed
lives. A failed DT confirmation still completes the assigned finer comparisons if runtime permits: avoid
selecting only successful data for numerical validation.

All §6 margins and absolute job confidence gates must pass at ALL three steps for a confirmed working
learner. For each successive halving, the paired-seed 95% interval of the change in the primary learned-minus-
writers-removed reward contrast AND informed-minus-learned reward gap must lie inside [-0.05,+0.05]
net food/10 s. All-food contrast changes must lie inside the same numeric food-rate margin; stranding
contrast changes inside +/-0.05 proportion. Report levels too. This does not establish full-body-step
convergence; never alter the body's integration or interface silently.

## 8. Analysis, costs and acceptance — R9

Use physical time in seconds throughout. Primary reward is `(food-poison)*10/(100/3)` in [200/3,100) s,
including pre-movement time and zero-meal lives. Preserve food and poison counts/rates separately,
first two thirds and full life as descriptive results; never select a window after seeing results.
Stranded means no meal in the entire life, not merely no movement. Report both separately.

Pair red/blue lives within each seed, average their measure, then bootstrap seeds (10,000 resamples,
analysis RNG 180). Pair contrasts before bootstrap; never bootstrap arms independently. All-food has one
life per seed, paired by that seed. Report 95% percentile intervals. Joint working-learner claim requires
all its gates; no cherry-picking endpoints or treating zero-crossing intervals as equivalence.

Absolute job gates (each step): food-rate lower bound >=1 food/10 s; lower paired-seed bootstrap bound
of `food_rate - 3*poison_rate` >=0 (also food positive); stranding upper 95% bound <=0.05. Report pooled
food:poison ratio without finite pseudocounts; the linear contrast tests the ratio threshold without
undefined bootstrap ratios. For stranding, red/blue lives are dependent: use Wilson upper bound on
seed indicator "either paired life stranded" as a conservative absolute gate (upper-bounds life rate),
plus life fraction and seed-cluster interval descriptively. Do not use 2N as independent trials. For
paired no-harm contrasts bootstrap seed means. Explain this conservative choice in the report.

Acquisition: P_food >=0.8*V_TYP and P_poison <=0.2*V_TYP. Count first entry time, fraction of life in
state, EVERY subsequent exit and re-entry, and final state separately. Also report weaker right-order
criterion, all P extrema, times outside [0,V_TYP], readout saturation and signed write charge. An end
state is not proof of retention through the life. A no-event acquisition time is missing, never zero.

For every arm report circuit energy/power from unchanged accounting, motor firings/guessed motor energy,
material parts, communication events per named connection source and gate activity. Count all independent
states and bias sources. Do not convert a graph-node count into a transistor count or assign missing pump
energy zero. No equivalence/no-cost claim without a predeclared margin (none is set for cost here).
Physical-contract violations are reported even when reward is good; never allow them to disappear in means.

Save one row per `(stage,version,arm,seed,poison,dt)` with hashes/configuration, counts, costs, flags,
and trace references. Full traces can be large: keep them in the permitted `lab/v/catalogue_brain_20261120_*.pkl`
archives (existing `lab/v/*.pkl` ignore rule), record absolute paths and hashes, and keep compact event/state
ledgers sufficient to regenerate headline tables in the assigned output directory. Check `git check-ignore`
before writing a large archive. No trace may exist only in a session's /tmp folder.

## 9. Finish — R10–R12

A working-behaviour claim requires live observation through the lab viewer/creature.watch, one fixed
first confirmation seed (do not select a pretty seed), and reproducible command. Record what happened,
including failure. If no display is available, report demo incomplete and do not claim demonstrated live
behaviour; offline animation does not silently substitute. Partial diagnostic findings need no demo.

REPORT.md starts with what was learned about exploration, informed action and learning, then the
consequential numbers/intervals and limitations. List incomplete work FIRST if any. Include:
- exact gate ledger R0–R12 and expected/actual job counts for each Cartesian product;
- code/configuration/raw-data links, hashes, analysis commands and saved failure logs;
- physical-contract/cost audit, evidence budget and step-refinement limits;
- v1 and any authorised v2 results, including why the revision was triggered;
- a one-page local-repair handoff: one accessible shortfall signal, its counterexample, observation
  time, required neighbours and costs. Distinguish detecting silence from detecting unprofitable action.
  No new algorithm, learning rule, second use or recruitment experiment is run here.

Before claiming completion, independently regenerate all headline tables from per-life ledgers, verify
source hashes and compare every requirement against files. A narrative of success is not an obligation
check. Update notebook "Where it stands" and PROGRAMME execution status; historical predictions remain.
Return exact next command for remaining implementation/validation work, or the specific reviewer decision
required. At end of this work order, STOP. Do not take another question from the broader programme.

## 10. Required invocation contract for the implemented runner

From repository root, with maths thread env variables all set to 1, the worker must make these work:

```sh
.venv/bin/python lab/catalogue_brain_20261120/run.py check
.venv/bin/python lab/catalogue_brain_20261120/run.py bench
.venv/bin/python lab/catalogue_brain_20261120/run.py action
.venv/bin/python lab/catalogue_brain_20261120/run.py learn
.venv/bin/python lab/catalogue_brain_20261120/run.py confirm --dry-run
.venv/bin/python lab/catalogue_brain_20261120/run.py confirm
.venv/bin/python lab/catalogue_brain_20261120/run.py refine
.venv/bin/python lab/catalogue_brain_20261120/run.py report
```

These commands specify interfaces to IMPLEMENT in R1, not scripts claimed to exist in the preparation
package. `confirm` executes DT; `refine` executes both finer steps from the SAME frozen job ledger and
seed count. Their combined cost must pass the preflight gate. Failed scientific gates produce a saved
not-triggered record for downstream stages, not a crash or a false completion. `report` runs on partial
outputs. Missing required data produce explicit incomplete rows. Worker should execute the full ordered
conditional assignment once commissioned, not ask permission at each routine gate.
