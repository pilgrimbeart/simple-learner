# Work order — calibration readout precision (2026-11-20)

**Status: ready for one executing agent; nothing below has been run.**
This is the next bounded phase after [D167](../discrete/NOTEBOOK.md#d167-calibration-next). It is not a new
research programme. Start here when [PROGRAMME.md](../PROGRAMME.md) directs you here. Work without routine
clarification, finish the specified diagnostics, package the results, and leave design decisions for review.

**You are the executing agent.** Do not start another agent. You are not a sealed or blind evaluator.

**Repository rules:**
- Repository: `/home/pilgrim/git/simple-learner`, on `main`.
- The worktree is intentionally dirty and holds valuable uncommitted results. Do not clean, reset, stash, check
  out, commit, push, merge, change remotes or install anything.
- Do not modify or rerun earlier assignments' outputs: `lab/v/overnight_20261119/` and
  `lab/v/calibration_next_20261120/` are read-only inputs.

## 1. Objective and the distinction to preserve

The goal is reusable, local, economical improvement during a robot's life. This phase asks something narrower:
**can the order detector's balance calibration be read precisely enough, by a locally specified operation, to
survive the circuit's own fixed offsets?**

D167 established three things, all in the noise-free analytic approximation:
- **Selectivity.** Weighting by the squared coincidence level separates anchors (simultaneous inputs) from real
  event order.
- **Capacity.** Two independent output gains make all 40 draws feasible, including 2215.
- **Precision blocks.** One fixed readout error at the mismatch scale (SD 30 mV) loses about a quarter of the
  feasible histories, whatever the history length. The median tolerable error is about 30 mV and the narrowest
  2.2 mV.

The error was a probe with an unspecified physical home. Earlier work (D148–D154) found two traps:
- **A second mismatched detector replaces the error rather than removing it** (D149, D151).
- **Same-path reversal cancels offsets exactly**, but only with polarity routing that the catalogue does not yet
  have (D152–D154). That limitation stays parked and is not waived here.

Keep four claims separate:
- (a) a setting exists;
- (b) the observations identify it;
- (c) a physical operation reads them accurately enough;
- (d) robot reward improves.

This phase addresses (c) as specification and arithmetic only: no circuit, no learner, no robot life.

## 2. Authority, boundaries and stopping rules

### Authorised
- Reading the repository and primary literature.
- Arithmetic on saved rows.
- **One** regeneration job over the existing 40 D163 schedules, using the unchanged analytic trajectories (0.5 ms
  step, 0.25 ms refinement on seeds 2026112200 and 2026112227), as specified in Task D.
- Writing new scripts in `lab/calibration_precision_20261120/` and outputs in
  `lab/v/calibration_precision_20261120/`.
- Appending notebook records.
- Updating PROGRAMME's status line for this assignment.

### Not authorised
- New circuits, catalogue primitives or topologies; graph edits.
- Noisy circuit lives, SPICE, robot lives, protected or sealed evaluations.
- New component draws, new schedules or event families.
- Changing any criterion, threshold, metric or stopping rule.
- Fitted thresholds or learned classifiers.
- A third weight beyond `w` and `w*w`.
- Treating the analyst's event labels, the branch derivative B or the ideal baselines as available to the brain.
- Any change to the body, world or interface.

**A favourable result authorises nothing further.**

### Budgets
- **Total envelope:** 4 hours, including reading, implementation and reporting.
- **Compute ceilings:** Task D 900 s; every other computation 120 s. These are ceilings, not targets.
- **Jobs:** one at a time, one maths thread (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`).
  Check for running jobs first and do not interrupt them. Wait on a job by its PID or a log line, never `pgrep -f`.
- **Corrections:** at most two corrective attempts per task. Record each, including assertion failures and how
  they were resolved, without dropping rows.
- **At a limit,** stop that branch, keep its partial output labelled as partial, and continue the independent
  tasks.

### Stopping rules
- **Reproduction gates.** If a gate fails (Task A, D), stop interpreting that task's new numbers and report the
  failure with its log.
- **Mechanism variants.** After two candidate variants without a clearer explanation, return to diagnosis (Task B)
  instead of adding a third.
- **Blocked candidates.** A candidate that needs switching, routing or path isolation the catalogue does not have
  is recorded as *blocked, with requirements*. It is not computed as though free.

## 3. Entry procedure
1. Read AGENTS.md (Working rules, Research discipline, Ground rules). Then read PROGRAMME's current entry point
   and D148–D154, D164 and D165–D167 in `discrete/NOTEBOOK.md`.
2. Read the
   [calibration review](../MIXED_FEEDBACK.md#calibration-identification-review-2026-11-20), D167's
   [REPORT](v/calibration_next_20261120/REPORT.md) and its STATUS.
3. Verify `lab/v/calibration_next_20261120/index.json`: every listed hash must match. Report any mismatch, and do
   not repair it.
4. Append a compact D168 "Before work" record to `discrete/NOTEBOOK.md`, linking this file. It covers the problem,
   competing explanations, discriminating comparisons, predictions with uncertainty, stopping rules and budget.
5. Freeze `lab/v/calibration_precision_20261120/manifest.json` before any calculation. It holds the revision, the
   hashes of every consumed script and data file, and the dirty-file hashes. D167's
   `lab/calibration_next_20261120/manifest.py` is a template.

## 4. Task A — precision requirement curve (mandatory; saved rows only)

**Question.** How precise must the readout be?

**Method.**
- **Inputs:**
  - D167's task 2 rows (`lab/v/calibration_next_20261120/t2/rows.jsonl`, 1920 records with exact error regions);
  - D167's task 1 records (`t1b/records.jsonl`, 640 records with A, B and W for both weights).
- **The `w*w` rows.** Compute their error regions with the same function. This extends D167's task 2 matrix
  deliberately, because Task A is a new task. Note that W for the `w*w` observer is `∫w²`, which the records store
  as `W_s` for weight `w2`.
- **Curve.** For a Gaussian readout error of SD σ, compute the exact expected adequate count over the grid
  σ ∈ {0, 1, 2, 3, 5, 7.5, 10, 15, 20, 30} mV. Do this for every window, mode and weight.
- **Required precision.** Report the largest σ whose expected count reaches 90% and 95% of the zero-error count.
  This is a requirement, not an achievement.
- **Reproduction gate:** the 30 mV points reproduce D167 exactly, and D164's 240 rows still reproduce.
- **Infeasible draw:** 2215 has probability 0 throughout.

**Deliverable.** A table and an accessible, colour-blind-safe figure. Use line style and labels as well as colour,
in Okabe-Ito colours.

## 5. Task B — where the fixed error physically lives (mandatory; reading and small arithmetic)

**Error map.** Write the observer chain as it would have to exist in circuit:
- the order output u;
- baseline subtraction (each of the three timescales) and the coincidence weight (`w`, and `w*w` as a reference);
- the product w·(u − baseline);
- the accumulation of A, B and W;
- the comparison that would set d;
- the stored knob.

For each stage, record from `chip.py`, `PARTS.md` and `units.py`:
- which catalogue part it would need, or "none exists";
- its offset or gain-error scale under `MISMATCH`, derived and not guessed;
- where that error enters the A, B, W algebra;
- whether a constant offset at that stage is cancelled by a later stage. For example, an offset before the
  baseline subtraction cancels once the baseline settles.

**Shared versus independent.** Classify every error as shared with or independent of any second measurement a
rejection scheme would compare it with. Use D149/D151's rule: an independent detector's offset adds its own
error.

**Bounds and gaps.**
- **Combined error:** state the resulting σ, or a bound with stated assumptions.
- **Unanchored scales:** where a stage has no catalogue part, say so plainly instead of assigning a number.
- **Noise:** include the noise model's contribution ([`mixed_feedback.py`](../mixed_feedback.py) docstring) only
  for nodes that would exist. A knob is a memory node, noisy only when written.

**Deliverable.** `error_map.md`, a table plus derivations, with each number traceable to a `units.py` constant or
a cited line of code.

## 6. Task C — primary literature on offset rejection (mandatory; reading)

**Sources.**
- **Enz & Temes (1996).** D166 recorded it as excerpts only. Read sections II–IV in the source, and record exactly
  which pages and equations were read.
- **One further primary source** on correlated double sampling or autozero residuals: charge injection, droop,
  and noise folding.

**What to record.** Write the result into `MIXED_FEEDBACK.md` beneath the existing review. For each scheme
record:
- its standard name;
- the assumptions under which the offset cancels: the same physical path, stationarity between samples, and the
  switches required;
- the residual error terms;
- the closest alternatives;
- what this project would add.

**Rules.**
- Distinguish a paper read from an abstract or excerpt.
- Verify every consequential claim in the source.
- A familiar mechanism is not evidence that it fits here.

## 7. Task D — quiet-period self-reference on the same observation (mandatory if B and C allow)

**The candidate information path.** Use the detector's own reading during low-coincidence time. There the true
weighted residual should be near zero, so the reading carries the offset e but not the order signal. This is the
only new candidate this phase computes.

**Quiet weight.**
- `q = 1 − w`, read only from the coincidence voltage.
- No threshold, no event labels, no future samples.
- If Task B shows that q cannot share a path with the w-weighted accumulation without switching, still compute the
  arithmetic, but label the candidate *blocked, with requirements* (Section 2).

**Arithmetic.** With r = u − baseline (per mode) and the readout error e entering both accumulations:
- Self-referenced residual: `A* = ∫w(r+e) − (W/Q)∫q(r+e)`, where `W = ∫w` and `Q = ∫q`.
- The shared e cancels exactly. What remains is `−(W/Q)∫q·r`, the true residual during quiet time, which is the
  baseline's own error.
- Do the same for B (its quiet term), and for the `w*w` observer with `q2 = 1 − w*w`.

**Run.**
- **Inputs:** regenerate only the 40 D163 schedules with D167's `t1b_weights.py` signal functions (reuse them; do
  not edit them). Use the same windows (full 0–1000 s, final third) and the same four modes.
- **Accumulate:** ∫q, ∫q·r and ∫q·B-integrand for both weights; stream these, without whole-life arrays.
- **Reproduction gate:** `w`, `w*w` A/B/W match D167's 640 records within 1e-12. The refinement on 2200 and 2227
  at 0.25 ms must change knobs by less than .001, with identical classifications.

**Report.**
- **Settings:** the self-referenced settings at zero shared error, scored against all 34 old cases for all 40
  draws, with paired rescues and harms against D167.
- **Independent residual:** each candidate's residual sensitivity to an *independent* error between the two
  accumulations, with σ taken from Task B, in exact Gaussian expectation.
- **Comparison:** set this against the Task A requirement.

**Prediction.** About 70% likely: a scheme without switches only re-labels the error (D149's pattern), because the
two accumulations need distinct parts. An exactly shared path would cancel e but leave the baseline-error term,
which matters most for the slowest baseline.

## 8. Task E — the noise wall for a later noisy calibration pilot (mandatory; arithmetic)

**Purpose.** AGENTS requires these numbers before any noisy learning pilot.

**Quantities.** Using the saved schedules and records, the noise model and units:
- **Evidence rate:** simultaneous anchors per second, which is 4/34 of events at 10 s mean spacing (one about every
  85 s). Also the per-anchor B and W, and their spread over draws.
- **Signal-to-noise:** for the integrated observation per anchor and per second, from the noise of the nodes that
  would carry it. State the assumptions.
- **Settling time:** the time needed to reach the Task A precision on d, setting aside fixed offsets, against
  1000 s lives.
- **Explorers per credit window:** one for the one-knob design, two for the two-gain design.

**Framing.** Report feasible ranges, not information in bits: no learner prior or likelihood is specified.

**Observability of B (analysis only, at most 30 minutes).** State what local signal could supply B, the knob's
own effect on the output, which is a privileged quantity today. Name the precedent, for example a perturbation
(dither) correlated with the output. Give its explorers per credit window and its evidence time. Do not compute
or build it.

## 9. Task F — package (mandatory, even after failures)

Write to `lab/v/calibration_precision_20261120/`:
- **REPORT.md,** in plain language without new shorthand, leading with what was learned. It answers:
  - what precision the calibration needs;
  - where the error lives and whether any specified local operation removes it without new switching;
  - what the noise wall implies for a later pilot;
  - the single comparison to make next.
- **STATUS.md,** with commands, PIDs, elapsed times, validation results, corrections, and any missing or partial
  outputs.
- **Raw rows,** the frozen manifest, and `index.json`. Hash the outputs only once they are final, excluding the
  index itself and any still-running log.

Also:
- **Notebook:** append a D168 result (observation, inference, limitations, changed belief, next branch).
- **PROGRAMME:** update this assignment's status line in PROGRAMME.md.
- **README:** change it only if the direction changes, and then add a plain-language "What we've learned" entry.

## 10. Decision rules for review (not for the executing agent)

- **A candidate's derived residual meets the Task A requirement without unspecified parts:** the next phase may
  freeze a costed circuit protocol for that operation: local state and update equations, removal controls,
  noise and cost accounting, and a live replay.
- **Only blocked candidates meet it:** the parked routing limitation (D154) becomes the next object of diagnosis.
- **Nothing meets it:** precision stands as the order calibration's blocking requirement. The programme should
  then weigh this capability against others the robot needs (PROGRAMME's milestone) before spending more on it.

## 11. Suggested sequence

1. Entry (Section 3).
2. Task A, fast; it sets the target.
3. Tasks B and C, reading.
4. Task D, the only long job.
5. Task E.
6. Task F.

If Task D is blocked or fails its gate, finish A, B, C and E, and package them.
