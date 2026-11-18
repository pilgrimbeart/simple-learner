# D79 work order — active prediction and contribution audit

2026-11-17. The user requested review of D77–D78 and a lower-effort sub-agent for the next step.
This is that authorised, bounded diagnostic. It is not a new allocator experiment.

## Question and purpose

Reusable local components need an economical way to retain useful information. D78 shows that
allocation changes performance, but does not identify the information needed to allocate well.
Its trajectory reader sums every stored stream weight, including sleeping streams. Those shares
are not the weights in the prediction actually issued by the brain. Even an active weight is not
evidence that a prediction helps. Determine whether the asserted early contribution is real,
and whether omitting currently active streams helps or hurts the present prediction.

## Read and inspect

Read AGENTS.md and the current programme; inspect D77–D78 in discrete/NOTEBOOK.md and its current
state. Read lab/alloc_compare.py, lab/alloc_rules.py, lab/alloc_trajectory.py, the prediction and
taste paths in lab/grownet.py, and the timed taste wrapper in lab/stage2_lang/seconds.py.
lab/noisy_path_audit.py contains an existing pre-taste observer and scored-prediction hooks.
lab/noisy_resource_observe.py contains a behaviour/state fingerprint. Inspect these before reuse.
Do not inspect any sealed test or unopened artifact. The ordinary seq rung below is sufficient.

The relevant primary source is Freund, Schapire, Singer and Warmuth (1997),
[Using and combining predictors that specialize](https://cseweb.ucsd.edu/~yfreund/papers/SpecializedExperts.pdf),
section 2: only awake specialists enter the normalized prediction. The lead agent has checked this.
No new literature-dependent mechanism is being selected.

## Scope, budget and files

- Work in lab/active_mixture_audit.py, lab/v/active_mixture_audit.json,
  lab/v/active_mixture_audit.log, and lab/v/active_mixture_audit_report.md only.
  Large raw arrays may use lab/v/active_mixture_audit.pkl (ignored); retain small summaries in JSON.
- Do not edit production code, other experiment scripts, or main documentation. The lead will integrate.
- Effort budget: 25 minutes implementation/analysis; at most 6 minutes wall time for simulation.
  One simulation job at a time, at most four workers, each with
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1.
- Four recorded lives: seq rung 17, seed 177000, red and blue, 300 s, dt=.0025 s;
  unchanged design rule none, P=4480; weight contest W, G=1000, P=560 (cap 3042).
  Use net10kc60SFBLMR and the flags/engine of alloc_compare.one (LB_FINE=LB_LIVE=1).
  Four unobserved repetitions of these same lives are allowed for exact fingerprint checks.
  No further seeds, parameter search, new rule, new family, or confirmatory claim.
- Small analytical checks and a very short smoke run fit within that budget.
- No push, commit, other agent, background campaign, or body/interface change.
- Stop if the observer changes a life or cannot reconstruct the prediction. Record the failure;
  do not reinterpret failed validation as a negative scientific result. Ask the lead for help if needed.

## Required measurement

1. Trace the sequence of prediction, taste delivery, learning and weight update. Record the
   actually issued prediction after each call to b.predict, before any later taste. Cache, by
   stream, its name, weight, probability and awake status at that call. Retain the default.
   Calling says/_pk is permissible only after checking those reads are non-mutating.
   Reconstruct the issued normalized mixture from awake predictors plus default and assert
   it equals b.p1 within 1e-12. Also record the all-stored-weight shares used by D78.
2. At each taste, retain the last issued cache. Obtain acceptance and the actual teaching letter
   from the original learning path (e.g. first N.learn call), without substituting an inferred
   gate. Label cases with no prior prediction separately. Do not use the new label to change
   or choose a forecast. Record any difference between issued and taste-entry forecasts.
3. D73 found a scoring-order defect: one stream's learning may delete a later stream's speaker.
   Reuse/adapt its read-only hooks to count affected accepted tastes and compare simultaneous
   pre-learning forecasts with actually scored forecasts. Respect the seconds wrapper's
   temporary b.t + at adjustment. Keep this separate from the issued prediction analysis.
   Do not repair this behaviour in this diagnostic.
4. On each accepted taste, evaluate the last issued prediction against the actual teaching
   letter. For each family (event, clock, integrator, rhythm), remove only that family's awake
   forecasts and renormalize the remaining weights, retaining the default. Also evaluate
   removal of all three non-event families together. No changes feed back into the life.
   Report delta bits = loss_without - loss_full: positive means that the family's current
   predictions reduced loss. Use -log2(p of observed letter); state any numerical clipping.
   Count changed binary choices using p > .5. These are instantaneous fixed-history
   comparisons, not lives with that memory or family removed.
5. Summarize each life separately and then the paired descriptions, in windows [0,30),
   [30,100), [100,200), [200,300) s and whole life. Give denominators; active versus stored
   weight shares, sleeping weight fraction, accepted tastes, total and mean delta bits,
   and changed choices. Report both predictor-call shares and taste-associated shares if
   practical; do not treat 10-second weight snapshots as outcome-weighted contributions.
6. Compare observed and unobserved fingerprints covering behaviour, learned counts, weights,
   RNG states and allocation, and compare result tuples with the matching alloc_confirm.json
   lives. Preserve any mismatch; no silent tolerances. Record revision, dirty paths, exact
   command, source hashes and runtime. Root revision at handoff is d37dac6.

## Checks and interpretation

Include small checks that sleeping weight cannot affect a mixture, removing an empty family
does nothing, and the sign of delta bits is correct on a hand-computable example. These checks
must test the measurement, not repeat the implementation. Raw observed/unobserved identity
and issued-prediction reconstruction are the main validation.

Competing possibilities: large stored shares are largely dormant; active early predictors help;
active early predictors hurt; effects vary by family or life. No outcome is preferred.
Earlier useful predictions alone do not prove that growing more memory in that family caused
better return. Conversely, a negative current contribution does not prove useless future capacity.
The samples are one previously used seed pair, and each arm's actions generate different histories.
Do not conclude equivalence, a general allocator, or a necessary marginal-utility mechanism.

Deliver a short report: what was measured, validation, observations with denominators, what
interpretation changed, limitations, and the smallest next discriminating check. Return control
after that report; the lead owns the next branch and documentation.
