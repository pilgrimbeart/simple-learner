# Overnight measurement work order — 2026-11-19

**Status: ready for one executing agent; experiments below have not been run.**
This is the bounded overnight assignment requested by the user. It is not a new research programme.
Start here when PROGRAMME.md directs you here. Work without routine clarification. Complete the
specified measurements, package the results, and leave design decisions for the morning review.
Do not start another agent. You are the executing agent, not a sealed or blind evaluator.

Repository: `/home/pilgrim/git/simple-learner`. Work on its existing `main` branch. The worktree is
intentionally dirty and contains valuable uncommitted results. Do not clean, reset, stash, checkout,
commit, push, merge, change remotes or install dependencies. Nothing in this assignment is a request
to push. Do not invoke `lab/overnight.sh`: that is an older unrelated job.

## 1. Objective and the scientific distinction to preserve

The goal is economical, reusable, local improvement during a robot's life. Tonight's question is much
narrower: **what calibration evidence is missing in the remaining order-detector failure, and how
much of the apparent difficulty comes from discarding earlier evidence?** Independently verify the
recent oscillator result so the supervising agent can trust the evidence in the morning.

Current findings and their qualifications live in `discrete/NOTEBOOK.md`, D155–D164. Read those
records and its current-state section, plus PROGRAMME.md and AGENTS.md. Consult the specific scripts
listed below, rather than reading the whole repository. The relevant results are:

- D162 is an actual noisy circuit that adjusts its own bias. Its fresh test has passed the frozen
  requirement, at added material/power cost. It is not a reward-learning robot.
- D155–D164 order-calibration results are **observer-computed analytic references**. They do not
  implement the calibration state, a precise baseline reader, or an online learning rule.
- Longer histories helped that reference obtain simultaneous-event evidence, but two component
  draws still fail. One cannot meet all conditions with a constant balance setting. The other had
  one simultaneous event, whose sufficiency is not established.
- A reported oscillator reliability pass is not proof of population superiority over its comparator.
  A fixed detector offset does not average away when the same detector is read repeatedly.

Do not conflate (a) a useful setting existing, (b) observations identifying it, (c) a physical circuit
implementing the observation/update accurately, and (d) improved robot reward. Tonight addresses
(a) and (b), audits one bounded example of local regulation, and leaves (c)/(d) unclaimed.

## 2. Authority, boundaries and stopping rules

### Authorised work

1. Read the explicitly listed unsealed scripts/data and repository instructions.
2. Create new analysis scripts under `lab/overnight_20261119/` and new outputs under
   `lab/v/overnight_20261119/`.
3. Recompute the specified observer mathematics and run the fixed new **development** schedules
   in `lab/overnight_20261119/matrix.json`. This is not a new physical brain simulation.
4. Append compact before-work/result records to `discrete/NOTEBOOK.md` as described below.
5. Produce a self-contained morning report with raw data, provenance, checks and unresolved questions.

### Not authorised by this work order

- Do not change an existing brain, simulator, units, noise, body, interface, primitive, metric,
  stimulus rule, success threshold, sample window or existing script.
- Do not tune a gain, threshold, time constant, seed set or mechanism to obtain a pass.
- Do not run a robot search, a new oscillator variant, a new physical calibration circuit, SPICE,
  a package installation, or another confirmation test.
- Do not read or search inside `lab/sealed/`, inspect `outside_set*.md`, or open
  `outside_set2_reply.log`. Do not perform broad content searches through all lab artifacts.
  No protected test is needed for this assignment.
- Do not alter credentials, Claude configuration, permissions or the machine's network configuration.
- Do not change README.md, PARTS.md, ABSTRACT.md, QUESTIONS.md, or the scientific decisions in
  PROGRAMME.md. Your observations are provisional until reviewed. The notebook may link your
  provisional report; do not rewrite old predictions or results.
- Do not fabricate an exact Bayesian benchmark or a number of learned bits. No new learner is built.

### Budgets

Overall: **six hours of elapsed work**, including coding, debugging and analysis. Finish earlier if
all tasks are done. This is a ceiling, not a target to fill. One compute job at a time; one maths
thread. No process pools, GPU jobs, other agents or simultaneous simulations. Finish the mandatory
items before optional items. Per-job limits are below. Do not launch work that cannot finish within
the overall remaining budget. An interrupted/incomplete job is not a negative scientific result.

For an implementation error, preserve the failed script version/log and make at most **two corrective
attempts per task**, each bounded by 20 minutes of debugging. A correction may repair an indexing,
serialization or numerical implementation error; it may not change the scientific comparison. On a
scientific/numerical discrepancy, stop the dependent branch and report it. Continue independent tasks.
Do not erase failed outputs or rerun into the same directory. Use `_retry1` and `_retry2` run names.

If frozen input hashes differ, stop dependent calculations. Record the difference without accepting
new hashes or deciding that the edit is harmless. If an input is missing, do not regenerate the old
experiment or search sealed material; record the missing path. No user reply is needed to complete
an independent audit or prepare a partial report.

## 3. Entry procedure and protected inputs

Run from the repository root, using the existing `.venv/bin/python`:

```bash
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
.venv/bin/python lab/overnight_20261119_preflight.py --output lab/v/overnight_20261119/preflight.json
```

The preflight checks content hashes, expected record counts, dependencies and the supplied numerical
helper. A dirty tree is expected; a matching git revision alone is insufficient. The frozen manifest
is `lab/overnight_20261119_inputs.json`. Do not rewrite it. A successful preparation check by the
supervising agent is recorded separately in `lab/v/overnight_preparation_20261119.json`.

Capture `git status --short` and `git diff --stat` into new `initial_status.txt` and
`initial_diff_stat.txt` files. Record current UTC time and the six-hour deadline in `STATUS.md`.
Use `ps -eo pid,ppid,etimes,comm` if you need to check for another compute job; do not print process
environments or credentials. Existing named jobs in the hand-off are complete. If another user job
is running, wait or do read-only analysis; do not kill it. Never use `pgrep -f` or pattern-based kills.

All task scripts below are to be written by you, in the **new** subdirectory. Their prescribed names
make execution and morning review predictable. Do not invoke an old experiment's `main()`; many old
scripts refuse overwrites, and some older modules execute work on import. Only import the explicitly
listed guarded modules/functions. New scripts can add `ROOT / 'lab'` to `sys.path`, where ROOT is
`Path(__file__).resolve().parents[2]` for a script inside `lab/overnight_20261119/`.

Use the supplied launcher for compute tasks:

```bash
.venv/bin/python lab/overnight_20261119_run.py audit 120 lab/overnight_20261119/01_audit.py
```

It creates a new run directory, captures the exact PID/command, locks against another job launched
through this helper, sets maths threads to one, captures stdout, enforces the deadline, and records
exit status. It only runs a Python file from the new script directory. An existing run directory is
an error, not permission to overwrite it. The lock cannot detect unrelated external jobs. Keep the
launcher as your sole running compute job and wait for its actual PID/tool session. If interrupted,
check its start/finish records and that exact PID before restarting; do not duplicate a running job.

Maintain a status table after every task: `pending / running / complete / blocked / failed`, with
output paths and reason. A completed script with failed scientific checks is not a completed result.

### Input map

Paths below are relative to the repository. All scientific input versions are frozen by the manifest.

| Purpose | Files |
|---|---|
| Original order brain, conditions and noisy observations | `lab/order_bench.py`, `lab/v/motifs/order_v2/confirm.jsonl`, `protocol.json` in that directory |
| Feedforward quadrature | `lab/population_trace_margin.py` (`convolution`, `predict`) |
| Full analytic trajectories | `lab/order_local_calibration.py` (`trajectory`), `lab/order_baseline_stream.py` (`stream_trajectory`) |
| Ideal baseline | `lab/order_continuous_baseline.py` (`lowpass`, `TAUS`) |
| Original static branch responses | `lab/v/order_balance_information/branches.json` (1360 rows), `draws.json` (40 rows) |
| Old short calibration observations | `lab/v/order_local_calibration/observations.json`, `lab/v/order_continuous_baseline/observations.json` |
| Existing 100s streams | `lab/v/order_baseline_stream/streams.json`, `draws.json`, `summary.json` |
| Existing 1000s streams | `lab/v/order_long_calibration/streams.json`, `draws.json`, `summary.json`; `lab/order_long_calibration.py` |
| Detector-precision reference | `lab/order_calibration_precision.py`, `lab/v/order_calibration_precision/rows.json`, `summary.json` |
| Oscillator graph and fresh result | `lab/adaptive_oscillator.py`, `lab/adaptive_oscillator_confirm.py`, `lab/v/adaptive_oscillator_confirm/{rows.jsonl,summary.json,protocol.json,provenance.json,audit.json,trace_manifest.json,report.md}` |
| Oscillator cost/schematic | `lab/v/adaptive_oscillator/{manifest.json,schematic.svg,report.md}` |
| Oscillator measurement functions | `lab/dynamic_parts_bench.py` (`metrics`, `oscillation`, `interval`, `wilson`) |
| Frozen matrix and helpers | `lab/overnight_20261119/matrix.json`, `lab/overnight_20261119_support.py` |

**Never confuse component seed and schedule seed.** Most order analyses reuse component draws
2026112200–2026112239. New schedules below do not make those components or event families held out.
Use JSON numeric types explicitly; NumPy scalar serialization errors must not discard a run.

## 4. Task A — independently audit the completed results (mandatory)

Write `01_audit.py`. Job limit 120 seconds; implementation allowance 40 minutes.

1. Independently verify all manifest hashes and the provenance `files`/`protocol_sha256` entries
   of D155–D164 inputs used. Report absent original metadata instead of backdating it.
2. Check unique key coverage, not merely row counts. Oscillator confirmation must have exactly
   `40 seeds × 3 arms × 3 timesteps = 360` records, all declared combinations. Read allowed arrays
   from frozen protocol rather than assuming JSON ordering.
3. Recompute the per-seed oscillator pass: every timestep must pass. Recompute the Wilson interval
   and paired pass difference using 4000 bootstrap resamples of entire seeds, RNG seed 126 (matching
   the declared function). Keep a seed's arms and timesteps together. Do not count 120 runs as120
   independent draws. Show whether each confidence interval includes zero.
4. Recompute the two step-halving intervals for every normalized metric. Use the frozen ±.05
   margin. Report any mismatch. Independently check every saved finest trace listed by the existing
   trace manifest by remeasuring `metrics('oscillator',[trace],[row['cost']])`. Hash each before use.
   Only a subset of confirmation traces was saved; report checked/available counts, never imply all
   360 traces exist. `cost` contains the required original stimulus shift/rail-hit metadata.
5. Recompute mean power and paired added power at the finest step. Keep activity (charge/crossings),
   power, material and behaviour separate. Confirm core part totals from the recorded component
   counts; do not reinterpret the memory-pump exclusion as included cost.
6. Verify the order1000s data:40 histories,160 settings (four modes), all100s prefixes identical
   to their old schedules, and independent scoring against the34 stored branch conditions per seed.
7. Verify D164 Gaussian interval probabilities with `statistics.NormalDist`, including the zero
   probability assigned to a capacity-infeasible draw. Hypothetical independence is an assumption.

The historical expected values are regression targets, not pass criteria you may force:
oscillator adaptive40/40, original38/40, writer-removed38/40; paired pass difference interval includes
zero. Long-history baseline modes each38/40; raw28/40. Compare tolerances of1e-12 for same-data
arithmetic; allow rounding only in printed prose. Explain larger differences, never edit old results.

Deliver `audit.json`, `audit.md`, checked source/input hashes and a discrepancy list (empty is fine).
If an audit discrepancy invalidates a downstream input, block that branch; independent tasks may proceed.

## 5. Task B — resolve what “the two remaining failures” means (mandatory)

Write `02_failures.py`. Job limit 120 seconds; implementation allowance 35 minutes.
Use stored branch responses and long-history settings only; no new trajectories are needed.

Each row stores `u_V`, `v_V` and `coincidence_adequate`. The order output under balance d is
`u + d*v`. The positive readout gain is scaled by `1+d`, the negative by `1-d`, with d in[−1,1].
All original strict inequalities remain:

- Near pairs, `0 < abs(delay) <= .15 s`: `sign(delay)*(u+d*v) > .03 V`.
- Simultaneous pairs: `abs(u+d*v) < .06 V`.
- Far pairs and single events: `abs(u+d*v) < .03 V`.
- Coincidence adequacy is separately required and unaffected by this readout knob.

For every one of40 component seeds, independently intersect the allowed d intervals for all34
conditions. For each lower/upper active bound record its condition, coefficient, voltage margin
and strict/open status. Handle negative/near-zero v correctly. Do not “repair” an empty interval
by swapping its bounds or clipping the fitted d into it.

For each of the160 old long-history settings, list every failed condition and its distance to the
original threshold. Produce a detailed side-by-side account for:

- `2026112215`: known capacity failure. Reproduce the simultaneous(.5,.35)V requirement
  `d > −.1621863170` and long-gap(.5,.5)V requirement `d < −.1944916109`.
- `2026112227`: calibration failure with a nonempty feasible interval. Record the learned-reference
  d for each mode, its distance outside that interval, event counts, and the amplitude/order/time of
  its simultaneous event(s) in the measured third.

Do not generalise from these selected cases alone: include the all40 table. The result must say
which failure is “no setting exists” and which is “available calculation selected a bad setting.”
Do not say why the latter occurs until Task C provides evidence.

Deliver `feasible_intervals.json`, `failed_conditions.json`, `failure_report.md` and validation checks.

## 6. Task C — attribute calibration to recorded events (mandatory)

Write `03_attribution.py`. Job limit900 seconds; implementation allowance60 minutes. This replays
observer equations for the existing40 histories, not the noise engine. Process one history at a time;
do not retain every full voltage array in RAM or save gigabytes of traces. Checkpoint per-seed results
and keep their hashes so a bounded retry need not recompute valid completed seeds.

### Reconstruct the exact existing observations

For each seed load its original finest-step row from `motifs/order_v2/confirm.jsonl` (node/element
arrays are the same across conditions for a seed). Use `make_long_stream(row,10.,2)` from
`order_long_calibration` and verify the entire generated event list matches the saved D163 list.
Do not use a new seed, redraw components or infer pulse amplitudes from output.

Use `stream_trajectory(row,.15,.0005,1000.)` to obtain t and all node voltages. This guarded
function is analytic feedforward quadrature; it omits rail fading and noise. For the second analytic
pass, copy the row and set ONLY `row['elements'][0][6] = 0.0`, as in D163, to obtain `pv`.
This is an observer's branch decomposition, not a proposed circuit intervention.

```
u = v[7]
sensitivity = 2*pv[7] - u
w = clip(v[6] / V_TYP, 0, 1)
initial_baseline = default_rng([seed,157]).uniform(-.075,.075)
```

For raw mode use `fA=w*u`, `fB=w*sensitivity`.
For each existing tau (.15,1,TAU_MAX), use the unchanged `lowpass` helper:

```
fA = w * (u - lowpass(u,tau,dt,initial_baseline))
fB = w * (sensitivity - lowpass(sensitivity,tau,dt,0.0))
```

The derivative estimator starts at0 because the random baseline state is independent of d. Do not
assign its baseline from a quiet window. Do not initialise the baseline with its correct equilibrium.
Reproduce the saved final-third A/B integrals and inferred d before any new analysis. D163 starts
its trapezoidal integral at the first grid point `t >= 2000/3`, not exactly at `2000/3`; preserve
this convention for regression. Require absolute integral discrepancies≤1e-9 V s and knob≤1e-9
for identifiable cases. Abort affected analysis on failure. Record the maximum discrepancy.

### Temporal attribution, with boundaries accounted for

Partition the measured third into non-overlapping intervals whose internal boundaries are event
`first_s` values. Include the initial interval from the effective integration start to the next event
and the final interval to1000s. Label the initial interval `carry_in` (also record its preceding event,
if any). Thereafter associate each interval with the event starting it. Store event id, amplitude,
delay, interval start/end, A, B, W and duration. Tails crossing a boundary belong to the interval in
which they occur: this is a **temporal accounting**, not a causal event-removal experiment.

Use `partition_integrals` from the supplied helper to split boundary-crossing trapezoids exactly.
Its piecewise-linear integral matches trapezoidal quadrature. Do not drop one sample at every event
boundary. Sum all intervals, including carry-in, and require agreement with the original full-window
A/B integrals≤1e-9 V s for every mode/seed. A failure invalidates the attribution.

For each mode/seed calculate these references from the fixed contributions:

1. All intervals, reproducing D163.
2. Only intervals beginning with a simultaneous pair.
3. All other intervals, retaining the carry-in interval.
4. Leave each simultaneous interval out, one at a time.
5. Prefix aggregates up to each successive simultaneous interval's end.

For each aggregate save A,B and `raw_d=−A/B`, then clip only to[−1,1] as the old reference does.
If `abs(B)<=1e-12 V s`, label it unidentifiable and do not manufacture a calibrated score. Keep
original d=0 as a separately labelled fallback comparator. Report B's sign; positive B is not by
itself proof that an implemented feedback loop would be stable.

Score identifiable settings against all34 old conditions. Report whether including other intervals
moves a previously acceptable anchor-only setting outside its feasible range. Do not call
leave-one-out arithmetic a causal ablation: full state trajectories are held fixed.

For2026112227, compare its actual anchor's amplitude case with the same case's stored D156 isolated
observation. Calculate that case-alone informed setting and compare it with (i) the long-history
anchor-only setting and (ii) D155's four-simultaneous-case reference. This discriminates amplitude
specificity, preceding-state effects and contamination by other events. If the evidence does not
separate them, say exactly what is still confounded.

Report all40 seeds, with a concise detailed narrative for2227 and the capacity failure2215. Do not
choose a convenient passing control after inspecting the results. Use2026112200 as the fixed
comparison example. This task does not choose a new event detector or learning rule.

Deliver `event_contributions.jsonl`, `attribution_checks.json`, `aggregate_settings.jsonl`,
`anchor_cases.json`, `attribution_report.md`. Include at least one labelled plot of cumulative A/B
or inferred d against the feasible interval for2227; use colour plus line styles/labels, not colour
alone. SVG written directly or existing plotting helpers are acceptable; do not install matplotlib.

## 7. Task D — run the fixed development schedules (mandatory if C validates)

Write `04_histories.py`. Job limit2400 seconds; implementation allowance60 minutes.
The authoritative matrix is `lab/overnight_20261119/matrix.json`. No additional seeds, rates,
amplitudes, tau values or repetitions. There are10 reused selected component draws ×8 new schedules
=80 histories, each1000s, all at mean pair spacing10s. The10 draws include the two failures and the
lowest eight original seed labels. This deliberately selected set is not a population sample.

For each component seed and replicate0..7, create a new RNG:

```
rng = numpy.random.default_rng([component_seed,165,1,replicate])
```

Generate the entire schedule before calculating voltages. Follow `make_long_stream` exactly except
for this RNG: case list order from `order_bench.cases()`, near positive/negative case weights1.6/.4,
all other weights1; first start `uniform(0,10)`; each following interval `uniform(8,12)` seconds;
stop first starts at999.36s. Each pulse lasts.04s. A starts at `first+max(-delay,0)` and B at
`first+max(delay,0)`. Current is `CAP*amplitude/.01` A; omit zero-amplitude pulses. Preserve the draw
order (choice of case, then next interval), floating point moments and all original component arrays.
Save every schedule and its hash. No schedule labels may feed the raw/local reference.

Use500microsecond quadrature and the same observation functions as Task C. Compute each full
1000s trajectory once per original/positive-path decomposition, then extract all windows from it.
Maintain baseline state continuously from birth. Do not restart it at100s or at the final third.
This is still an analytic reference, not a call to the original noisy engine.

For each raw/baseline mode compute six windows:

| Name | Start | End | Meaning |
|---|---:|---:|---|
| `first_100s_last_third` | first sample≥200/3 | 100s | short-life reference convention |
| `full_100s` | 0 | 100s | retain all early observations, including startup |
| `last_third_1000s` | first sample≥2000/3 | 1000s | old long-life reference convention |
| `full_1000s` | 0 | 1000s | retain all observations, including startup |
| `prefix_666.6666666666666s` | 0 | last sample≤2000/3 | information available at start of final third |
| `prefix_833.3333333333334s` | 0 | last sample≤2500/3 | information available halfway through final third |

Use trapezoidal integration on the exact included samples, with boundaries saved in metadata. Derive
and score settings as in C. Do not silently subtract a burn-in or a learned prior. Earlier observations
are available to a real learner even though its performance is judged later; this comparison tests
the cost of the old observer discarding them. It does **not** demonstrate that a physical online
controller correctly uses those observations. The settings are computed from a fixed unadjusted
trajectory and scored on isolated cases, not closed-loop lives.

Numerical validation before the full batch: refine only(seed2026112200,rep0) and(seed2026112227,rep0)
to250microseconds, for all modes/windows. For identifiable settings require d change<.001 and
identical classifications of every old case. Also check denominator signs/identifiability status
agree. Save every mismatch. If this fails, block the full batch: do not choose a finer timestep,
exclude a troublesome window, or declare an almost-pass without morning review. The two coarse
histories can count toward the80 if validation passes. Never add a successful replacement history.

Expected full output:80 ×4 modes ×6 windows =1920 setting records; each has all34 condition results
or an explicit unidentifiable status. Preserve raw numerator/denominator even when d clips.
For each history/window count simultaneous events and distinct simultaneous amplitude cases.
These labels are used only in diagnostic reporting. Do not use them to accept, gate or fit a setting.
Report exact pass denominators by component seed, schedule, mode, window and evidence count.

Predictions (not required outcomes): longer/full-history references may reduce scarcity, but startup
and persistent error may make retaining all evidence harmful. A single anchor's amplitude specificity
may explain repeated2227 failures. If predictions fail, report that; do not invent a new experiment.

Deliver per-history schedule/observation checkpoints, `settings.jsonl`, `case_scores.jsonl`,
`refinement_checks.json`, `history_summary.json`, `history_report.md`, and exact elapsed time. A partial
run is reported with completed/expected keys; it must not be summarised as if all80 histories finished.

## 8. Task E — information and precision summary (mandatory; mostly small arithmetic)

Write `05_information.py`. Job limit120 seconds; implementation allowance35 minutes.

Using Tasks C/D, answer these separately:

1. How often is no simultaneous anchor available? How often does one occur but its derived setting
   still fail? How does having multiple *amplitude cases* differ from merely repeating one case?
2. How much does keeping all earlier observations change final settings and old-case adequacy?
   Report paired rescued/harmed counts. Do not replace the frozen last-third result with the more
   favourable window. Present both.
3. Compare opportunity counts with the known simultaneous probability4/34 under the generator.
   Given N event starts, `(1−4/34)**N` is the declared no-anchor probability. This is a generator
   calculation, not the probability a circuit learns or passes. State the effective counting window.
4. Reproduce D164's fixed-detector-error limit. Explain why more time cannot average away a fixed
   manufacturing error. Do not imply that imaginary4/16 independent paths have been built or costed.
5. For2026112215 preserve its infeasible knob interval in every table. More evidence cannot create
   a constant setting that meets contradictory inequalities.

For D results use counts as descriptive results on a selected set. If presenting intervals on paired
mean changes, bootstrap over the10 component seeds, keeping all8 schedules and every arm/window for
one component together. Use4000 resamples, RNG126. Label these descriptive intervals, not fresh
confirmation or a generality result. Do not bootstrap1920 settings as independent samples.
Never call an interval containing zero equivalence or no harm. No new practical margin is authorised.

Deliver `information_summary.json` and `information_report.md`. Distinguish observation, inference,
limitations and unresolved alternatives. Do not make a bit count without a specified unknown, prior,
likelihood and evidence process; none is required tonight.

## 9. Task F — oscillator adaptation review (independent, optional after A/B/C)

Write `06_oscillator_review.py`. Job limit120 seconds; implementation allowance30 minutes.
No new circuit trajectories. Use the saved development and confirmation artifacts only.

- Verify paired original/adaptive builds preserve the first two node arrays and first three element
  arrays for each seed/step, apart from declared extra memory/readout/writer. Do not require starts
  or arrays of a removed edge to exist in the removal arm. If arrays differ unexpectedly, flag it.
- Tabulate the actual memory change, range and final-third drift from records. Confirm the removed
  writer has zero memory motion. Do not interpret oscillatory memory motion as a quiet settled knob.
- Examine saved traces of the old failed development draws51006,51011,51036 and fresh original
  failures2026120208,2026120221 where available. Report availability honestly: corresponding adaptive
  traces were not saved for every successful fresh draw. No replay is authorised merely to fill gaps.
- Show the original thresholds and how the observed changes meet them. Keep component reliability,
  causal removal evidence, added cost and the inconclusive paired population difference separate.
- Ensure the claim excludes new problem families, robot reward, a universal cycle theorem, exact
  physical retention, and uncounted memory-pump energy.

Deliver a brief `oscillator_review.md` plus machine-readable checks. Do not turn this optional review
into an oscillator tuning or replication study. Saved live-replay logs already document the demonstration;
no need to open a desktop animation while the user is asleep.

## 10. Task G — package the morning hand-off (mandatory even after failures)

Write `07_pack.py` if helpful. Job limit120 seconds; reserve30 minutes before the overall deadline.
Create `lab/v/overnight_20261119/MORNING_REPORT.md`, `result_index.json` and a final `STATUS.md`.

The report must be understandable without this conversation. Use this outline:

1. **What we learned:** at most five plain-language points, each linking the supporting raw output.
2. **What ran:** exact task statuses, expected/completed denominators and elapsed times.
3. **Audit:** discrepancies, original source hashes, numerical checks and missing artifacts.
4. **Remaining order failure:** capacity vs observation failure, the role of anchor amplitude,
   contamination and available history. Separate causal evidence from fixed-trace arithmetic.
5. **Fixed new histories:** all modes/windows and all failed cases; no selected “best” row.
6. **Oscillator:** verified scope, cost and limits; no new mechanism claim.
7. **What the supervisor must decide:** a short ranked list of unresolved interpretations. Recommend
   a discriminating question only; do not launch a new design or change the programme yourself.
8. **Limitations and failures:** numerical approximations, omitted circuit noise/rail fading in the
   order references, fixed detector error, selected components, reused families, partial jobs and retries.
9. **Reproduction:** exact commands, Python/dependency versions, revision, dirty-file snapshot,
   source hashes, frozen protocol/matrix hashes, schedule hashes, seed namespace and output paths.

Keep small summaries and raw metrics in lab/v. Large arrays/plots need not be produced; if any file
exceeds1MiB, record its absolute path, size and SHA256 in `large_artifacts.json`. Do not delete it or
add it to git. Do not modify `.gitignore` tonight; the supervisor will decide what to retain. Do not
copy raw large outputs into the notebook.

Append one compact D165 notebook investigation record before calculations, linking this work order
and matrix as the frozen protocol. Use subheadings for Tasks A–G, not seven new programme branches.
Record each result/dead end as it occurs. At the end add a clearly labelled provisional overnight
status line to the notebook's current-state section linking MORNING_REPORT. Do not rewrite prior
records, make a new “current programme” elsewhere or present your recommendations as approved.
If D165 is already occupied when you start, record that discrepancy and use a unique dated HTML
anchor `overnight-2026-11-19` instead of renumbering someone else's history.

Re-run the preflight (without overwriting its first output; use `preflight_final.json`) to establish
that frozen inputs stayed unchanged. Run `python -m py_compile` only on your new Python scripts,
then `git diff --check`. Record new/changed files and explain every change outside the two new
work directories (only the notebook append/current-state note should be intentional). Do not run
all three push checks or create a fresh venv: no production code change or Push is authorised.

If everything finishes early, stop. Leave a concise final message pointing to MORNING_REPORT and
state whether any branch is blocked. Do not use spare time for more seeds, another mechanism,
protected tests, messaging someone, committing or pushing.

## 11. Suggested execution sequence

After writing/validating each new script and freezing its source/protocol hash, run:

```bash
.venv/bin/python lab/overnight_20261119_run.py audit 120 lab/overnight_20261119/01_audit.py
.venv/bin/python lab/overnight_20261119_run.py failures 120 lab/overnight_20261119/02_failures.py
.venv/bin/python lab/overnight_20261119_run.py attribution 900 lab/overnight_20261119/03_attribution.py
.venv/bin/python lab/overnight_20261119_run.py histories 2400 lab/overnight_20261119/04_histories.py
.venv/bin/python lab/overnight_20261119_run.py information 120 lab/overnight_20261119/05_information.py
.venv/bin/python lab/overnight_20261119_run.py oscillator_review 120 lab/overnight_20261119/06_oscillator_review.py
.venv/bin/python lab/overnight_20261119_run.py package 120 lab/overnight_20261119/07_pack.py
```

These commands are sequential instructions, not a request to start seven background jobs. Observe
the dependency gates above. On a blocked histories task, information/reporting can use existing data
and must explicitly say the new schedule experiment was not completed. On a timeout, preserve the
partial data and stop that branch. A useful morning hand-off can be a well-localised discrepancy;
it need not be a higher score.
