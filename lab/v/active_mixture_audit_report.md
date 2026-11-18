# D79 active prediction and contribution audit

2026-11-17. Exploratory fixed-history diagnostic of sequence rung 17, seed 177000,
red/blue poison wirings, 300 s, dt=.0025 s. The unchanged design uses P=4480; the weight
contest uses G=1000, P=560, cap 3042. Arm net10kc60SFBLMR; LB_FINE=LB_LIVE=1.

## What changed in our interpretation

Stored weights overstate rhythm's early influence: rhythm holds 24.8521% of all stored
weight throughout the first 200 s but contributes no awake forecast in these four lives.
Clock and integrator forecasts really do dominate early predictions. Their influence
is not evidence of benefit: removing all three non-event families together lowers the
observed teaching-letter code length in every recorded life and every declared window.
Individual early families can nevertheless help. Leave-out effects do not add up.
These observations weaken the asserted early-help explanation; they do not identify
which allocation change would improve return.

## Measurement and validation

The observer captures each stream's actual says output during each original predict
call, its KT probability and current weight, plus the default. It reconstructs the
normalized mixture over awake forecasts only, after predict returns. Every issued
mixture reconstructs within 2.665e-15 (required tolerance 1e-12).

At taste entry it retains that last issued cache, then temporarily sets b.t to b.t+at
for simultaneous read-only forecasts and restores it before calling the existing
seconds wrapper. Acceptance and the teaching letter come from the original first
Net.learn call; they are not inferred from a reconstructed gate. All accepted tastes
call every stream's learn at precisely the temporary taste time. Pre-learning and
actually scored stream forecasts are retained separately. No forecast uses its new
label, and nothing observed feeds back.

The four observed lives exactly match their unobserved controls in behaviour, all
noncallable brain/net data (including histories, counts, unit structure, weights,
clock and learner RNG state), allocation state and closure-held allocator RNG state.
Brain/pool object links are represented by their stable type name, network links by
stream name; their data is separately fingerprinted. Methods are excluded. Every
result tuple matches its control and alloc_confirm.json exactly after JSON container
normalization; only field 5, elapsed runtime, is excluded. No numerical tolerance is
used in these identity comparisons. Small checks validate sleeping-weight invariance,
empty-family removal and the sign of delta bits.

There are no tastes without a prior issued prediction. On every accepted taste the
issued probability equals the stored p1 at entry exactly, and the simultaneous
entry mixture differs only by floating arithmetic (maximum 2.11e-15). Thus the
scoring-order differences below are not being inferred from a timing difference.
Scored-loss reconstruction differs from the actual pbits increment by at most
1.51e-14. Source review established that these arms use read-only Net/Net2.says,
firing, place and _pk; JointNet.says would mutate state and is explicitly rejected.

Numerics: loss = -log2(probability of the actual teaching letter), clipped to
[1e-12,1-1e-12]. Delta = loss_without - loss_full: positive means the family's
current forecasts helped. Binary choices use p>.5. Tiny empty-family residuals
below 1e-12 are floating arithmetic, not a contribution.

## Each life

All denominators are shown. The JSON contains each life/window's complete active and
stored shares at predictor calls and accepted tastes, each family's total/mean delta
bits and changed choices, and scoring-order counts. E/C/I/R denote event, clock,
integrator and rhythm families only in the tables.

| design | poison | issued calls | all/accepted tastes | event delta bits | clock | integrator | rhythm | all non-event | changed choices without non-event |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unchanged | red | 5700 | 206/184 | +76.937 | -1.629 | -1.646 | -0.479 | -5.578 | 8 |
| unchanged | blue | 5722 | 218/187 | +73.193 | -1.443 | -1.754 | -0.493 | -5.992 | 13 |
| weight contest | red | 5920 | 193/163 | +46.595 | -1.306 | -1.576 | -0.544 | -5.527 | 12 |
| weight contest | blue | 5705 | 208/176 | +67.426 | -1.543 | -2.018 | -0.431 | -5.859 | 9 |

## Paired descriptions by window

These pool the two colour lives with denominator weighting; they are descriptions of
one reused seed pair, with no confidence interval or population claim.

| design | window s | calls / accepted tastes | active E/C/I/R at calls | stored E/C/I/R at calls | sleeping stored fraction | active E/C/I/R at accepted tastes |
|---|---|---:|---|---|---:|---|
| unchanged | 0–30 | 1097/32 | 0.106/0.401/0.456/0.000 | 0.063/0.393/0.294/0.249 | 0.478 | 0.093/0.396/0.442/0.000 |
| unchanged | 30–100 | 2485/62 | 0.409/0.298/0.291/0.000 | 0.291/0.247/0.211/0.249 | 0.300 | 0.387/0.291/0.319/0.000 |
| unchanged | 100–200 | 3510/136 | 0.872/0.065/0.062/0.000 | 0.654/0.049/0.048/0.249 | 0.250 | 0.871/0.066/0.062/0.000 |
| unchanged | 200–300 | 4330/141 | 0.897/0.028/0.021/0.054 | 0.845/0.023/0.018/0.113 | 0.066 | 0.897/0.029/0.019/0.054 |
| unchanged | 0–300 | 11422/371 | 0.707/0.134/0.134/0.020 | 0.591/0.116/0.096/0.197 | 0.213 | 0.733/0.118/0.121/0.021 |
| weight contest | 0–30 | 1097/32 | 0.106/0.401/0.456/0.000 | 0.063/0.393/0.294/0.249 | 0.478 | 0.093/0.396/0.442/0.000 |
| weight contest | 30–100 | 2522/76 | 0.430/0.302/0.266/0.000 | 0.302/0.254/0.193/0.249 | 0.306 | 0.470/0.284/0.243/0.000 |
| weight contest | 100–200 | 3511/102 | 0.944/0.028/0.027/0.000 | 0.673/0.059/0.020/0.249 | 0.288 | 0.941/0.029/0.029/0.000 |
| weight contest | 200–300 | 4495/129 | 0.866/0.046/0.027/0.060 | 0.792/0.060/0.024/0.123 | 0.089 | 0.842/0.061/0.033/0.063 |
| weight contest | 0–300 | 11625/339 | 0.723/0.130/0.119/0.023 | 0.581/0.133/0.085/0.200 | 0.233 | 0.718/0.133/0.117/0.024 |

| design | window s | accepted tastes | event delta bits | clock | integrator | rhythm | all non-event | non-event bits/taste | changed choices without non-event |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unchanged | 0–30 | 32 | +0.180 | +0.293 | -0.422 | +0.000 | -0.890 | -0.0278 | 5 |
| unchanged | 30–100 | 62 | +4.520 | -1.422 | -0.865 | -0.000 | -4.479 | -0.0722 | 11 |
| unchanged | 100–200 | 136 | +62.282 | -1.423 | -1.520 | -0.000 | -3.790 | -0.0279 | 2 |
| unchanged | 200–300 | 141 | +83.149 | -0.520 | -0.593 | -0.972 | -2.411 | -0.0171 | 3 |
| unchanged | 0–300 | 371 | +150.130 | -3.072 | -3.400 | -0.972 | -11.570 | -0.0312 | 21 |
| weight contest | 0–30 | 32 | +0.180 | +0.293 | -0.422 | +0.000 | -0.890 | -0.0278 | 5 |
| weight contest | 30–100 | 76 | +11.442 | -1.823 | -1.752 | -0.000 | -6.306 | -0.0830 | 13 |
| weight contest | 100–200 | 102 | +45.058 | -0.720 | -0.679 | +0.000 | -1.441 | -0.0141 | 0 |
| weight contest | 200–300 | 129 | +57.342 | -0.598 | -0.741 | -0.975 | -2.749 | -0.0213 | 3 |
| weight contest | 0–300 | 339 | +114.021 | -2.849 | -3.594 | -0.975 | -11.386 | -0.0336 | 21 |

In the first 30 s, clocks help in each colour life (+.028 and +.264 bits); the
integrators help red (+.122) and hurt blue (−.544). Rhythm is asleep. Joint non-event
removal improves loss even here (−.133 and −.757 bits), illustrating the effect of
renormalization and why family leave-outs are not additive.

## Scoring order remains a separate defect

| design | poison | accepted tastes | later-stream removal | pre-learning speaker deleted / scored forecasts differ | simultaneous minus scored loss, total bits |
|---|---|---:|---:|---:|---:|
| unchanged | red | 184 | 55 | 26 | +0.000165 |
| unchanged | blue | 187 | 45 | 15 | -0.001048 |
| weight contest | red | 163 | 139 | 137 | +0.010138 |
| weight contest | blue | 176 | 152 | 152 | +0.054204 |

The weight contest changes a later stream's pre-learning speaker on 289/339 accepted
tastes, compared with 41/371 in the unchanged design. The corresponding signed loss
differences total +.06434 and −.000883 bits. Signed cancellation and low mixture weight
can hide individual changes; these small totals do not establish a negligible causal
effect on later weights, allocation or behaviour. No scoring-order repair was made.

## Failures, provenance and budget

The first smoke failed before observation: I referred to nonexistent N/ClockN classes
rather than Net/Net2. The next smoke reported unequal fingerprints. This was a
measurement defect: canonicalization saw market's brain pointer as a network because
Watched has a kind *method*, and inserted that bound method, including its memory
address, into the digest. It also prevented pickling the dynamic GrowNetS class.
The lead authorized short diagnostic repetitions to trace the mismatch. One repetition
was accidental: a patch used unavailable `python`, and the shell continued with the
unpatched smoke. Two retained-state attempts then failed to pickle. A zero-step
constructor inspection localized all 168 noncanonical leaves to market's brain pointer.
The corrected canonicalizer accepts only string stream names, represents the brain
pointer by type, recurses through array contents and encodes complex state explicitly.
The final clean smoke passes exact state/result identity. Five smoke attempts failed
(including the setup failure), one passed; none supplies a scientific result.

The full authorized eight lives ran once, with four workers and all three maths-thread
variables at 1, in 23.0218 wall seconds. All smoke invocations combined took under 3 s
including imports/setup; total simulation-command wall time is under 27 s, far below
the six-minute envelope. No further simulations were run. Only the four named
diagnostic files and ignored raw pickle were written. No production changes, sealed
artifacts, commit or push.

Root revision is d37dac6; exact revision, dirty paths, executed source SHA256 hashes,
command, per-life runtimes and raw results are in active_mixture_audit.json and the
ignored active_mixture_audit.pkl. The log retains the later failed smokes and full run;
the initial class-name failure and first digest-only failure were printed to the tool
transcript and are described here rather than falsely claimed as retained raw logs.
The final script adds only paired descriptive aggregation/--analyse after the run;
its separate final SHA256 is recorded alongside the executed source hash. The
original runtime source hash remains unchanged in provenance.

Command:
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/active_mixture_audit.py`
Analysis-only regeneration of paired descriptions: same command with `--analyse`.

## Limits and smallest next check

These are instantaneous family removals on fixed, arm-specific histories. They do not
remove memory, rerun learning, or predict return after different choices. One previously
used seed pair cannot show equivalence, a general allocation rule, necessary marginal
utility, or lack of future value from a currently harmful forecast. The measured code
length differences are computational losses against teaching letters, not counts of
new environmental information learned; no ideal Bayesian bound is inferred. No result
here establishes a local physical implementation or cost benefit.

The smallest next discriminating check is a read-only per-stream replay of these same
recorded issued forecasts: ask whether negative family totals hide useful members,
and compare that ranking with stored saved bits and weight. This requires no new lives
and tests aggregation before selecting a new allocation mechanism. A scoring-order
repair is a separate causal comparison before any new frozen performance claim.
The lead owns that decision; this diagnostic stops here.

