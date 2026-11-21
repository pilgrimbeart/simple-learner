# Plan — separate reliable response from exploration

Status: prepared at the user's request after D177; not executed. This is the next proposed bounded
investigation, not permission to launch an agent or begin runs. One executor, no delegation.

## Execution contract — read before starting

This file is the sole assignment. D177 and the programme provide context, not extra tasks. Follow AGENTS.md's
delegated-work rule. Do not take another question from the programme when this assignment ends or blocks.
No independent literature search, academic essay, new mechanism research, or expansion of the experiment.
The assigning reviewer owns any new literature work. Read only the assigned paper sections below; if another
mechanism requires research, record the specific question and stop that branch, continuing independent
assigned requirements. Do not launch another agent.

Create `CHECKLIST.md` before implementation, with one row per obligation below and links to its evidence.
Allowed states: pending, done, not triggered, incomplete. “Done” means the specified artifact/check exists;
it does not mean the scientific hypothesis passed. “Not triggered” requires the named branch and measured
evidence; lack of time is **incomplete**, never not triggered. Keep this ledger current at each stage boundary.

| ID | Obligation | Trigger and acceptance evidence |
|---|---|---|
| R0 | Protocol, manifest, exact arms, predictions and budget estimate | Always; frozen files before runs |
| R1 | Identity, provenance and passive-logging checks | Always; commands, results and wiring/draw records |
| R2 | Historical contract and conditional physical-contract assessment | Always; separate labelled contracts; unresolved operations listed |
| R3 | Assigned reading | Always; paper sections and at most five relevant bullets, no survey |
| R4 | Substrate comparison and all-food controls | R1/historical contract pass; complete per-life ledger, drift and primary metrics |
| R5 | Identical-input replay and evidence/noise budget | Same trigger as R4; matched streams, response evidence and assumptions |
| R6 | Stage-1 branch decision | After R4–R5; numeric criteria below and linked evidence |
| R7 | Transfer, omission and operating-region diagnosis | Stage 2 triggered; response/recovery/imbalance results with frozen windows |
| R8 | Eight-setting informed grid, then single knob family | Stage 2 triggered; both comparisons, or specific measured non-applicability |
| R9 | Candidate contract and informed component comparison | Stage 3 gate passes; diagram, costs, matched controls and result |
| R10 | Learning, frozen and all-food candidate comparisons | Stage-3 informed improvement gate passes; every arm and failed life retained |
| R11 | Fresh confirmation and both integration halvings | Confirmation gate passes; frozen sample size, all contrasts and convergence intervals |
| R12 | Candidate physical/noise checks and live demonstration | Any working physical-behaviour claim; checks and reproducible demonstration evidence |
| R13 | Metrics, uncertainty, costs and reporting | Always, for every completed arm; unavailable measures explicitly labelled |
| R14 | Bounded autonomous-repair handoff | Always; at most one page, no new experiment or mechanism design |
| R15 | Final obligation/artifact audit and document updates | Always; REPORT and CHECKLIST account for every row, with remaining work |

Execute in stage order. R13's metric definitions apply from the first run, not only at stage 4. Complete
triggered requirements before considering optional variants. Log routine bug fixes without asking for
approval, preserve failed logs, and rerun affected checks. A substantive protocol change is a proposed
amendment for the assigning reviewer; do not execute it or rewrite the frozen protocol to match results.
Do not seek routine confirmations already settled here. If time or tools prevent a required step, finish
independent assigned analysis and report exactly what remains; do not replace it with an easier experiment.

## Goal and question

The goal remains [reusable, economical in-life adaptation](../README.md#the-goal-intelligence-that-scales):
the brain detects an improvable shortfall and adjusts existing machinery or recruits capacity locally.
This investigation asks which action shortfall is worth repairing before attempting autonomous repair.
A better hand-designed relay is a diagnostic reference, not the final research result.

[D177](../discrete/NOTEBOOK.md#d177-robot-review) owns the evidence, corrections and research rationale.
Do not repeat the calibration investigation. Shared reading, recruitment, scaling, protected families and
production adoption of memory knobs remain outside this plan.

Competing explanations:

| Explanation | Discriminating observation |
|---|---|
| Biological noise disrupts transfer | Lower noise improves stimulus-linked response with otherwise identical circuit and input |
| Noise supplies necessary exploration | Lower noise reduces movement/encounters despite improved response to supplied input |
| Mismatch shifts operating regions | Persistent per-unit failures and selective rescue by an existing bias/gain/time constant |
| The nominal informed setting is poor | Another fixed setting improves action without replacing units |
| A component cannot provide the needed dynamics | Bounded existing settings fail; an existing alternative component improves the matched transfer test |
| Correct action is possible but learning remains inadequate | Informed circuit succeeds while its taste-driven version falls short |

These explanations can coexist. Failure of a bounded parameter set does not prove that no setting works.

## Scope, budget and records

Six hours total once execution is requested, including analysis and reporting. Stages 0–2 get at most two
hours; conditional component work gets two; validation/reporting share the final two. Reserve 30 minutes
for reporting. At most one compute job at a time and one maths thread per worker; record exact job PIDs.
Do not interrupt another job or edit code it may import. Stop at the budget and report unresolved work.

Before a stage starts, estimate its full cost, including controls, analysis and checks, from existing logs
or a short preflight. Record the estimate in CHECKLIST. If it cannot fit, do not start a partial stage and
silently drop controls: mark the stage incomplete and hand back the estimate. The six hours are a hard cap,
not a promise that all conditional branches fit. Always complete the final audit/report within the cap.
Use `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` for every pooled run.

Work in `lab/robot_action_20261120/`, results in `lab/v/robot_action_20261120/`. Keep large traces out of git
at a recorded absolute location with hashes and a compact per-life ledger in the repository. Preserve the
dirty checkout, old reports, predictions and logs. No commit/push, body/interface change, new noise bypass,
SPICE, catalogue extension or production-brain edit. Lab adapters use the common engine's existing noise.
All new state affecting behaviour must be explicit, costed circuit state; implicit filters with missing
independent noise cannot support a physical implementation claim.

Only new files in the two named lab folders and the notebook/current programme status may be written.
QUESTIONS.md may receive a brief parked question. No edits to engine, body, production brains, catalogue,
historical artifacts, dependencies or environment configuration. Needed changes outside this list are
reported as blockers, not implemented. Do not amend this work order during execution.

Before computation append a notebook protocol and freeze `manifest.json`: revision, dirty input hashes,
commands, seeds/worlds, substrate, units, arm definitions, exact parameters, metrics and analysis version.
Hash code before each run; changes receive dated addenda. Record predictions before seeing new results.
Reuse D176 development seeds 0–31, each with red then blue poison, 100 s lives; include one all-food life
per seed per relevant circuit. They are reused development lives, not fresh confirmation.

## Stage 0 — contract and reproducibility (30 minutes)

Read the current programme, D176–D177, relevant brain/engine code and PARTS catalogue. Verify D176's
source manifest and recover actual sensor-side wiring from the built graph, never infer it from firing.
Check stored body wiring/world identities. Verify passive logging leaves a short baseline trajectory
unchanged. Archive exact component identities and mismatch draws; adding a node must not silently remap
existing draws. If common-noise alignment cannot be preserved, retain paired worlds and disclose that limit.

Specify two distinct contracts:

1. Historical diagnostic: D176's circuit, memory knobs and writer thresholds, with original voltages,
   supply model and pulse amplitudes. Compare biology and silicon noise through the supported substrate
   selection only. This isolates noise; it is explicitly **not** an on-chip implementation.
2. Conditional physical candidate: silicon, supply/rails and limits from units.py, existing PARTS blocks,
   explicit state and chip.py cost accounting. Any conversion is a separate arm, not a noise-only change.
   No silent pulse/body-interface change; use an already authorised technology interface. If that cannot
   be done, stop the dependent physical branch and report the exact unresolved contract.

Read Arthur–Boahen sections II–III and VIII, linked in D177, for integration, reset/recovery and
spontaneous oscillation: at most ten minutes within stage 0. Record sections actually read and at most
five implications for this assignment. If unavailable, record that fact and use D177's already checked
rationale; do not substitute an unbounded source hunt. New literature questions go to the assigning reviewer.
Derive thresholds/time scales from circuit operation and
noise margins, not from the body's fixed pulse duration as an adaptation target.

## Stage 1 — does the shortfall survive lower noise? (45 minutes)

Run the historical diagnostic on the same development lives with:

- Repaired memory, taste-driven learning.
- Same circuit, taste withheld, initial knobs unchanged (frozen-learning control).
- Same circuit, taste withheld, food/poison knobs initialised to nominal 1/0 (informed reference).

Run each under biology and silicon; reuse trustworthy existing biology captures instead of repeating them.
Include all-food learning controls. The informed reference knows the hidden valence and sensor wiring;
its observations are not a fair information bound on the learner. Measure drift to verify its setting persists.
Do not clamp nodes or disable noise in a candidate brain.

Save pulse times, taste, local trace/memory state, sensor/motor events, position, movement onset and meals.
After capture, replay the same saved input stream through the two substrate variants outside the
body. This separates changed response to identical input from changed input caused by closed-loop actions.
Replay is not a reward comparison. Preserve timing in seconds and include quiet periods and failed lives.

Branch (apply in this order):
- Contract/check failure: stop affected work, mark dependent obligations incomplete, finish independent
  reporting. An error is not evidence against a mechanism.
- Stop this historical repair branch only if **both** informed and learning silicon arms meet the existing
  job's food-rate, food:poison and stranding limits with their 95% intervals, and learning silicon exceeds
  learning biology by the +0.10 net-food/10 s margin below. Mark stages 2–3 not triggered and report this as
  development evidence; it is not physical validation or fresh confirmation.
- Otherwise proceed to stage 2, including when intervals are inconclusive. If lower noise reduces movement
  and encounters, test the exploration explanation first; otherwise start with the measured transfer loss.
  Record these trends without calling inconclusive differences a demonstrated collapse or rescue.

Prediction, deliberately uncertain: mismatch will leave a downstream shortfall; silicon may also expose
dependence on noise-driven exploration. No numerical reward prediction is justified before the noise-only
comparison. Record which of these predictions survives.

## Stage 2 — locate the operating-region failure (45 minutes)

Measure response conditioned on input, quiet firing, latency distribution, recovery and left/right motor
imbalance. Report their variation across units/lives, not only population means. An event near an input is
an association, not automatically a caused event. Use replay with paired pulse omission on a fixed subset
of captured inputs to estimate incremental response; omitted inputs belong only to the offline harness.
Define observation windows in seconds from the circuit's measured response/recovery before scoring.

Both bounded comparisons are required when stage 2 is triggered, in this order. If the second cannot be
specified from the measured operating region, record the evidence and mark the diagnosis unresolved;
do not replace it with a mechanism build. Budget expiry leaves the unperformed comparison incomplete.

1. Test the nominal informed setting against a small fixed grid: food knob {0.5, 0.75, 1.0}, poison knob
   {0, 0.25, 0.5}, excluding equal settings: eight points total including nominal. These are historical
   diagnostic voltages, not a transferable adaptation rule. Screen on seeds 0–7; evaluate the single selected
   point on 8–31, labelling both as development. Rank by net reward, with food rate and stranding visible.
2. From transfer traces choose **one** existing bias, gain or time-constant family with a predicted direction
   of repair. Freeze baseline plus at most four settings from its measured operating region, in SI, before
   comparison. First screen on identical-input replay, then at most one finalist in closed loop. If two knobs
   appear inseparable, report the identifiability issue instead of expanding the grid.

Keep exploratory motor activity distinct from sensor-triggered action. Do not treat quieter firing as
automatically better, tune to a body-supplied rate target, or equate correct average rate with correct response.
Stop this stage with one causal hypothesis and a discriminating next intervention, or an explicit unresolved
diagnosis. The two-hour diagnosis envelope is a stopping rule, not permission to start blind construction.

## Stage 3 — conditional existing-component comparison (at most two hours)

Proceed only if stages 1–2 identify a persistent shortfall and an existing component contract can test it.
Specifically, R7–R8 must be accounted for without budget omissions, a measured response failure must predict
the effect of changing one component, and R2 must permit a physical candidate without a new primitive or
interface change. Write this gate decision before construction. Otherwise stage 3 is not triggered by
the scientific evidence, or incomplete if prerequisites could not be completed; report which.
Freeze a diagram explaining which local signal each component receives, what state it retains, its dynamics,
SI parameters, material and power. Use existing leaky integration/bounded-pulse or oscillator capabilities
as the diagnosis requires. One primary arrangement. A second is optional only after required analysis of the
first identifies a specific residual cause and predicts the second's effect, and all triggered validation
still fits the budget. No third arrangement. A new primitive or a different body/interface is a separate
decision, not an implementation detail.

For a sensory-response hypothesis, keep the exploratory motor source fixed and replace only the implicated
sensory stage. For an exploration hypothesis, keep sensory processing fixed and test one explicit autonomous
motor source. Do not swap both together. Preserve actual internal wiring and all untouched component draws.
Freeze the action response contract before construction; do not require one spike per body pulse unless
analysis shows that is necessary. The brain must never receive pulse labels or expected output from the harness.

First compare informed fixed settings, baseline versus candidate, paired on development lives. Trigger the
learning comparison only if the primary paired reward improvement's lower 95% bound exceeds +0.10 net food
per 10 s. If not, diagnose the result and stop this branch; an inconclusive result is not mechanism failure.
If the gate passes, compare taste-driven, frozen-learning, informed and
all-food arms. Keep the eligibility mechanism and memory repair fixed to isolate the action change.
Circuit edits occur only in lab copies/adapters; any necessary production change is reported separately.

## Stage 4 — metrics, uncertainty and conditional confirmation

Primary reward metric: (food minus poison) per 10 s during the **fixed final third of the 100 s life**,
including time before movement and zero-meal lives. Also retain D176's after-movement metric as an explicitly
secondary historical comparison. Do not switch between them according to the result. Report food/poison
counts and rate separately; no artificial finite ratio when poison count is zero. Report acquisition,
final ordering, strong learned-state occupancy, subsequent losses, and no-meal stranding separately.

Use paired bootstrap over seeds, carrying each red/blue pair together. For all-food compare the same seed
across arms. Report 95% intervals. Learning's unknown is binary valence with balanced prior; observations are
causal input/taste histories and depend on actions. Estimate informative encounters per second, trace overlap
and competing writers before interpreting results. Accuracy alone is not a whole-history information bound;
do not sum repeated 1-H2 values or assume independence. Cost every memory and exploratory source. Report
energy, material, communication and motor activity alongside reward; no unmeasured cost is zero.

These proposed engineering margins are design choices, not scientific constants or new goal definitions:
- Useful reward improvement: lower 95% bound exceeds +0.10 net food per 10 s (one extra net meal per 100 s).
- All-food no-harm: lower paired bound exceeds -0.05 food per 10 s (5% of the existing one-food/10 s floor).
- Stranding no-harm: upper paired difference bound is below +0.05 (five percentage points). This does not
  replace the stricter existing absolute job criterion. Report absolute stranding with an interval as well.

Fresh confirmation is triggered only after R9–R10 are complete, candidate checks pass, all three development
margins above are met, and the full fresh comparison **plus both refinement checks** fits the remaining
budget. If not, report the failed gate or mark validation incomplete for lack of resources; no confirmed
working-behaviour claim. Freeze one candidate before fresh confirmation. Use development paired variance to choose the smallest
multiple of 32 seed pairs between 64 and 256 expected to give a primary-contrast 95% half-width <=0.05.
Select a disjoint ordinary seed range after auditing previous use; record it before launch. Do not use
protected families or call new seeds a new family. If the target precision exceeds 256 pairs or remaining
budget, report confirmation deferred rather than launch an underpowered pass/fail test. No optional stopping
or sample expansion after examining fresh results. All declared margins must pass for the combined claim.

For R10 and confirmation, the primary reward contrast is candidate learning minus baseline learning;
all-food and stranding contrasts compare those same designs under their stated conditions. Report candidate
learning minus candidate frozen as the separate test of learning, with its paired interval; improvement over
the old design alone is not evidence of learning. Informed arms remain explanatory references. Do not pool
these contrasts or replace one with whichever has the most favourable interval.

Refine the engine step through two successive halvings on the reported paired contrasts, keeping parameters
in seconds fixed. Require the 95% interval for each successive change to lie within [-0.05,+0.05] net food
per 10 s; overlap with zero is insufficient. Record that this checks integration, not full body-step
convergence. Any broader step claim requires an already supported, unchanged-semantics body-step check;
do not silently change the body. If refinement is incomplete, label the result exploratory/unresolved.

Validate all new candidate states/noise paths and physical limits; do not disable substrate noise to pass.
Before claiming working robot behaviour, show the candidate live through the existing viewer with a
reproducible command. No broad simulator test suite is needed for documentation or isolated analysis;
run meaningful adapter/circuit checks and any required checks if shared implementation changes are proposed.

## Handoff to autonomous repair — proposal only

A successful fixed repair supplies a reference, not a mechanism that recognises its own need. In at most
one page based solely on completed evidence, deliver one
candidate **local** shortfall signal and a counterexample: does it distinguish absent input from failed
response, or task-useful exploration from waste? List its prior assumptions, observation time, exploration
cost and required neighbours. If it is unidentifiable from those signals, say so; do not add a body signal.

If no signal is justified, say so without new research or construction. The following investigation would
compare fixed tuned, autonomous adjustment and adjustment-removed controls,
then test the unchanged rule on a second use. Its mechanism, transfer task and budget require a separate
frozen protocol. No autonomous selector, recruitment or capacity-doubling search starts under this plan.

## Deliverables and final decision

Produce manifest/addenda, protocol, checks, per-life ledger, raw-output index, cost/contract table and a short
REPORT.md. Update the notebook's current state and programme status; preserve negative and incomplete cases.
Before finalising, walk R0–R15 against actual files and logs, not recollection. Include the ledger in the
report by link, list every incomplete item first, and distinguish “assigned branch completed” from
“investigation stopped at budget/blocker”. No overall completion claim while triggered requirements are
incomplete. Supply exact next commands where known, not a new research programme. A successful metric
does not excuse missing controls, cost accounting, numerical checks or demonstration.
Lead the report with one of: noise-dependent historical failure; exploration failure; repairable operating
region; bounded component rescue; learning shortfall after action repair; or unresolved diagnosis. Tie each
claim to scripts/configuration/raw output, state changed belief, and name the next conditional branch.
The endpoint is an explanation that selects the next research step, not a promise to obtain a positive score.
