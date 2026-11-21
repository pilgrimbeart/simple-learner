# Work order — can shared-path calibration operate causally?

**Status: ready for one assigned sub-agent; not executed.** Prepared at the user's request on
2026-11-20 following [D169](../discrete/NOTEBOOK.md#d169-calibration-review).
This document prepares the experiments; it does not itself launch an agent.

## Objective and authority

The goal is reusable, local, economical adaptation during life. The narrow question is whether the
ideal shared-path cancellation in D168 can survive a causal quiet tracker with finite gain and
leakage, while preserving useful temporal-order signals. A positive answer would justify reviewing
a catalogue extension, not claim a working robot learner.

You are the executing agent. Do not delegate. Work directly in the existing dirty main checkout.
Do not clean, reset, stash, commit, push, install packages or overwrite earlier artifacts. No body,
interface, production simulator or catalogue edits; no robot lives, SPICE, protected evaluations,
new oscillator or two-gain variants. A hypothetical connection may be specified and studied in an
explicitly labelled mathematical reference, but must not be silently adopted as an existing part.
No noise-free reference is evidence that the production circuit survives substrate noise.

Use `lab/shared_readout_20261120/` for scripts and `lab/v/shared_readout_20261120/` for results.
The only shared-document edits allowed are a new notebook protocol/results entry, its current-state
summary, and the status of this assignment in PROGRAMME. Put source review in the new output folder.
Do not change historical work orders or indexed reports.

**Budget:** four hours total, including implementation and reporting. Source/specification work
at most 75 minutes; arithmetic 120 seconds per command; replay at most 1800 seconds total including
refinement. One compute job at a time, with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1`. Inspect running processes before compute; do not interrupt another job.
Capture and wait on exact PIDs. At a budget limit, preserve partial output and finish the report.
At most two implementation corrections per task; preserve failed checks and their explanations.
No parameter search or third mechanism variant.

## 1. Entry, protocol and source check

Read AGENTS, README's goal, PROGRAMME's current entry, notebook D154 and D167–D169,
PARTS §2, `units.py`, the relevant `chip.py` and `mixed_feedback.py` contracts, and D168's
REPORT, STATUS and error map. Verify all entries in D168's `index.json`; stop dependent work on
any mismatch without repairing the input. If this assignment already has a completed REPORT,
stop and report that fact rather than rerunning it.

Append a compact notebook protocol before calculation: problem, competing explanations,
predictions, comparisons, uncertainty, stopping rule and this budget. Freeze `manifest.json`
with revision, dirty-file hashes, all consumed scripts/data and this work order. Hash scripts
before their runs; additions get dated manifest addenda, never retrospective replacement.

Check the primary sources linked in MIXED_FEEDBACK's offset-rejection review. Verify only the
claims needed for shared-path cancellation, continuous-time correction and finite-gain residuals.
Record pages actually read, standard mechanism names, assumptions and closest alternatives.
If a source cannot be obtained, mark that limitation; do not substitute a search excerpt for a
read paper. No new literature survey or installing PDF tools; existing tools may be used.

Competing explanations:
- Sharing the read path removes the leading offset and an affordable local tracker suffices.
- Leakage or nonlinear response prevents sufficiently accurate tracking even at rest.
- The quiet signal is contaminated by real events, so static cancellation succeeds but causal
  calibration learns away useful order or depends on an unavailable separation of timescales.

## 2. Specify the candidate and derive its limiting cases

Deliver `CONTRACT.md` and `bounds.json` before trajectory experiments. Specify one candidate:
read the difference between order voltage u and quiet-tracker voltage m once, then steer the
resulting current to the quiet tracker and the retained balance knob with complementary weights.
Use raw order output and the existing coincidence voltage. Use **w**, not w squared, in the main
candidate: an extra squaring operation is not free. D167's squared-weight result remains context.

A starting mathematical contract is

    I = I0 * tanh(s * (u - m - e))
    C_m * dm/dt = -g_m * (m - V_bias) + k_q * (1-w_g) * I
    C_d * dV_d/dt = sign_d * k_w * w_g * I   [retained write law applied here]

All currents, capacitances, conductances, slopes, offsets and voltages have SI units. Derive the
feedback sign from the original order circuit; do not assume it from an arbitrary variable name.
Define how V_d controls the original balance knob using its existing finite range and gate law.
Specify the current mirrors, gate transfer, bias, rails, writer dead band and every internal state.
One shared error e belongs to one physical input pair. The separate-path control has independent
errors e_w and e_q at that same stage. Match marginal error scales and coupling to both arms.

These equations are a hypothesis, not permission to ignore physical constraints. Derive quiet
fixed points, local stability, residual input-referred error, settling time and rail/current
constraints. Include finite leak, nonlinear slope, gate opening at rest and mirror gains. Explain
which gain factors cancel only at equilibrium and which change causal operation. Identify all
unavailable operations; if another new operation is necessary, stop construction and report it.

Tabulate parts, state, resting supply power and writes, mapped to chip.py blocks. A transistor
count may be a justified range where a topology is not fixed; an unknown cost is not zero. Derive
allowable parameters from units.py and the required precision, not from success on particular
histories. Freeze at most **two** parameter points: the least-cost analytically feasible choice
and one explicitly higher-cost sensitivity point. If no affordable feasible region can be
established, finish the arithmetic and report without a replay.

Before replay, estimate silicon noise/evidence rate and explorers per credit window from D168,
updated for this candidate's components. Include gate mismatch missing from the existing model
as an explicit sensitivity assumption, never a purported measured device statistic. No invented
bit count: the unknowns are offsets and the balance setting; no Bayesian prior/likelihood has
been established for this candidate.

## 3. Cheap discriminating tests

Create `checks.py` and run it before the history replay. Required checks:
- Constant input: computed fixed point and residual agree with the analytic finite-leak solution.
- Shared offset cancellation in the ideal linear/leak-free limiting reference, with the expected
  failure for unequal independent offsets. Ideal limits are labelled nonphysical references.
- Feedback sign, bounded states and current conservation through complementary steering.
- Prefix causality: changing future inputs cannot change earlier tracker/knob states.
- Identical read-path errors make shared and separate controls coincide when otherwise matched.
- Reporting a zero bias must not hide lost gain: include known positive and negative order inputs.

Use the 30 mV connection offset scale and the documented resting-output range for static error
budgets. Treat gate error, leak and curvature separately before combining them. Report both mean
bias and scatter; a small SD around a large mean does not meet the precision requirement.

## 4. Conditional causal replay — exploratory mathematical reference only

Run only if tasks 2–3 pass. Regenerate the existing **40 D163 schedules**, 1000 s each, using
unchanged signal-generation functions from `lab/calibration_next_20261120/t1b_weights.py`
and D168's `d_quiet_reference.py` as a reproduction guide. Do not rerun the old script into its
old directory. Stream each generated trajectory through all new arms before discarding it.
Use D168's existing initial-condition convention for upstream states; freeze independent tracker
initialisation in the manifest, never initialise m to the known resting level or the knob to an
analyst's optimum. All draws, including 2215, remain in the denominator.

Compare:
1. Shared differential reading with the causal quiet tracker.
2. Two separate reading paths, otherwise the same tracker and parameters.
3. Fixed initial knob with no adaptation (removal control).
4. D168's whole-history shared reference, explicitly privileged and offline.

The main paired comparison uses one fixed reproducible offset draw per component draw, reusing
that shared error for the active path in arm 2 and an independently drawn quiet-path error there.
Freeze the random seed and error allocation before results; do not select favourable offsets.
This is a deterministic trajectory/ODE feasibility replay with fixed mismatch, not a noisy
physical validation. Quantify the remaining substrate-noise bound separately. If it cannot be
bounded below the error budget, classify the outcome unresolved and leave a noisy pilot for review.

Any use of the affine signal decomposition u(t,d) supplied by the old analytic trajectories belongs
only to the test harness. The candidate sees u, its own states and coincidence voltage; never A,
B, W/Q, event labels, component arrays or future samples. Check whether a moving knob invalidates
that affine approximation through downstream filtering. If it does, either propagate the existing
linear filter state causally from the same branch signals or stop the replay as unsupported; do
not interpret a frozen-knob approximation as online learning.

Check reproduction of the raw-mode A/B/W totals against D168 (absolute error <= 1e-12 in their
stored units) and schedule identity before interpreting new results. Use 0.5 ms integration;
refine seeds 2026112200 and 2026112227 at 0.25 and 0.125 ms. Require successive changes below
1 mV in reported residual readout error and .001 in normalised knob value, with unchanged old-case
classifications. Failure means numerical uncertainty, not mechanism failure; no general simulator
convergence claim follows from these two reused draws.

Add three diagnostic input controls only on those two fixed seeds: no input, ordered events only
(remove simultaneous events offline), and simultaneous events only. Labels construct controls in
the harness; they never enter the update. Keep original event times, do not compress schedules.
These controls test drift, contamination and availability of calibration evidence, respectively.

## 5. Frozen analysis and decisions

Report every arm and parameter point, without choosing a winner after results. Use full life and
last third separately. Save per-draw and per-case outcomes, initial/final states, rail excursions,
write activity, and time histories sufficient to diagnose the first failure.

Report causal tracking error, mean/RMS/SD and maximum error; calibration delay; residual quiet
output; positive/negative order sensitivity; original 34-case scores at the final knob; draw and
case rescues/harms separately. Final-knob isolated scoring is a diagnostic, not proof of online
performance. Also report the order response during adaptation using the original scoring semantics
where applicable; label it unscorable where the old isolated-case criterion does not apply.

The 10 mV conservative target is an engineering screen, not a new population-yield threshold.
Apply saved per-draw feasible regions as well: a global RMS pass may hide narrow-margin failures.
D168's expected adequate count is not literal retention of the same successful histories. Do not
call an interval crossing zero a tie; report paired differences as exploratory, reused-draw evidence.
Do not claim no harm without a separately justified, frozen practical margin.

Decision table:
- Static physical bounds fail: identify the dominant term and required cost/operation; no replay.
- Static bounds pass but causal replay fails: distinguish tracking lag, leakage, contamination,
  dead band, saturation and invalid approximation. No retuning or third variant.
- Causal reference passes: recommend a frozen noisy physical bench, specifying the exact proposed
  catalogue change and its costs. This does not authorise implementation or catalogue adoption.
- Incomplete data/check failure: report incomplete; never convert it into a scientific negative.

## 6. Deliver and stop

Write `REPORT.md`, `STATUS.md`, `CONTRACT.md`, `SOURCE_REVIEW.md`, machine-readable results,
checks/logs, manifests and final `index.json`. STATUS records exact commands, PIDs, elapsed time,
failed attempts, omitted tasks and why. Index final files after reporting, excluding itself and
any live log. Use colour-blind-safe labelled plots if useful; inspect them before delivery.
Append the notebook result and update this assignment's PROGRAMME status. Preserve predictions.

Lead the report with what this changes about local adaptation, not implementation chronology.
Answer: does sharing the path still help causally; what precision, evidence time and material does
it need; what remains privileged/unbuilt; and what one decision should the reviewer make next?
Return to the programme's costed-local-adjustment milestone. Stop here: no automatic noisy bench,
new primitive, robot search or further agent.
