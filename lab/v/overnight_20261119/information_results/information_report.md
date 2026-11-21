# Task E — information and precision summary

Descriptive counts on deliberately selected, reused component draws. No bit count: no unknown, prior, likelihood and evidence process has been specified tonight.

## Draw with no possible setting

- 2026112215: allowed interval (-0.1622, -0.1945) is empty. It fails in every table below whatever the evidence.

## Existing 40 histories (D163 schedules), final third

| mode | no anchor | anchor present but all-window setting fails | anchor-only setting passes | all-window passes | other-intervals-only passes |
|---|---|---|---|---|---|
| raw | 0/40 | [2026112201, 2026112205, 2026112208, 2026112212, 2026112214, 2026112215, 2026112222, 2026112226, 2026112227, 2026112230, 2026112233, 2026112236] | 29/40 | 28/40 | 14/40 |
| 0.15 | 0/40 | [2026112215, 2026112227] | 39/40 | 38/40 | 12/40 |
| 1.0 | 0/40 | [2026112215, 2026112227] | 39/40 | 38/40 | 11/40 |
| 3.8585074308112732 | 0/40 | [2026112215, 2026112227] | 39/40 | 38/40 | 10/40 |

Opportunities: mean 33.0 event starts in the window (first 0.5 ms sample at or after 666.667 s to 1000 s); observed no-anchor histories 0, generator expectation 0.64.

## 80 new development histories (10 selected components × 8 schedules)

Completed 80/80 histories, 1920/1920 settings.

### 1. Anchors: absent, single, repeated case, several cases (tau 0.15 s; all modes in JSON)

| window | no anchor (pass) | one anchor (fail) | ≥2 anchors, one case (pass) | ≥2 cases (pass) | all pass | failures on 2215 |
|---|---|---|---|---|---|---|
| first_100s_last_third | 58 (0) | 21 (3) | 1 (1) | 0 (0) | 19/80 | 8/8 |
| full_100s | 24 (1) | 39 (3) | 3 (3) | 14 (11) | 51/80 | 8/8 |
| last_third_1000s | 2 (0) | 4 (1) | 3 (2) | 71 (65) | 70/80 | 8/8 |
| full_1000s | 0 (0) | 1 (1) | 0 (0) | 79 (71) | 71/80 | 8/8 |
| prefix_666.6666666666666s | 0 (0) | 2 (0) | 0 (0) | 78 (70) | 72/80 | 8/8 |
| prefix_833.3333333333334s | 0 (0) | 1 (0) | 0 (0) | 79 (71) | 72/80 | 8/8 |

### 2. Keeping earlier observations (paired on the same 80 histories)

Both the frozen reference window and the alternative are shown; the frozen result is not replaced.

| mode | reference → alternative | ref pass | alt pass | rescued | harmed | mean change [95% cluster bootstrap, descriptive] |
|---|---|---|---|---|---|---|
| raw | last_third_1000s->full_1000s | 56/80 | 55/80 | 1 | 2 | -0.013 [-0.037, +0.000] |
| 0.15 | last_third_1000s->full_1000s | 70/80 | 71/80 | 1 | 0 | +0.013 [+0.000, +0.037] |
| 1.0 | last_third_1000s->full_1000s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| 3.8585074308112732 | last_third_1000s->full_1000s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| raw | last_third_1000s->prefix_666.6666666666666s | 56/80 | 57/80 | 5 | 4 | +0.013 [-0.025, +0.050] |
| 0.15 | last_third_1000s->prefix_666.6666666666666s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| 1.0 | last_third_1000s->prefix_666.6666666666666s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| 3.8585074308112732 | last_third_1000s->prefix_666.6666666666666s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| raw | last_third_1000s->prefix_833.3333333333334s | 56/80 | 54/80 | 2 | 4 | -0.025 [-0.062, +0.000] |
| 0.15 | last_third_1000s->prefix_833.3333333333334s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| 1.0 | last_third_1000s->prefix_833.3333333333334s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| 3.8585074308112732 | last_third_1000s->prefix_833.3333333333334s | 70/80 | 72/80 | 2 | 0 | +0.025 [+0.000, +0.062] |
| raw | first_100s_last_third->full_100s | 23/80 | 38/80 | 19 | 4 | +0.188 [+0.025, +0.350] |
| 0.15 | first_100s_last_third->full_100s | 19/80 | 51/80 | 32 | 0 | +0.400 [+0.250, +0.550] |
| 1.0 | first_100s_last_third->full_100s | 19/80 | 51/80 | 32 | 0 | +0.400 [+0.250, +0.550] |
| 3.8585074308112732 | first_100s_last_third->full_100s | 19/80 | 51/80 | 32 | 0 | +0.400 [+0.250, +0.550] |
| raw | first_100s_last_third->last_third_1000s | 23/80 | 56/80 | 35 | 2 | +0.412 [+0.237, +0.575] |
| 0.15 | first_100s_last_third->last_third_1000s | 19/80 | 70/80 | 52 | 1 | +0.637 [+0.463, +0.775] |
| 1.0 | first_100s_last_third->last_third_1000s | 19/80 | 70/80 | 52 | 1 | +0.637 [+0.463, +0.775] |
| 3.8585074308112732 | first_100s_last_third->last_third_1000s | 19/80 | 70/80 | 52 | 1 | +0.637 [+0.463, +0.775] |

### 3. Opportunities against the generator

| window | span (s) | mean event starts | no-anchor observed | no-anchor expected (1−4/34)^N | mean anchors observed / expected |
|---|---|---|---|---|---|
| first_100s_last_third | 66.7–100.0 | 3.4 | 58/80 | 52.70 | 0.29 / 0.39 |
| full_100s | 0.0–100.0 | 10.0 | 24/80 | 22.86 | 1.00 / 1.18 |
| last_third_1000s | 666.7–1000.0 | 33.3 | 2/80 | 1.24 | 3.95 / 3.92 |
| full_1000s | 0.0–1000.0 | 99.8 | 0/80 | 0.00 | 11.57 / 11.75 |
| prefix_666.6666666666666s | 0.0–666.7 | 66.5 | 0/80 | 0.02 | 7.62 / 7.83 |
| prefix_833.3333333333334s | 0.0–833.3 | 83.3 | 0/80 | 0.00 | 9.56 / 9.81 |

Generator: P(simultaneous) = 4/34; 24 event starts give ≥95% chance of at least one. (1-4/34)^N is the generator probability of no simultaneous event among N starts; not a probability that a circuit learns or passes.

## 4. Fixed detector error (D164, reproduced in Task A)

- tau .15 s, prior 0.5: zero-error adequate 39/40; expected adequate with a new 30 mV-SD detector 28.44; hypothetical 4 / 16 independent paths 36.63 / 38.43; narrowest positive symmetric tolerance 3.67 mV.
- tau .15 s, prior 0.8: zero-error adequate 39/40; expected adequate with a new 30 mV-SD detector 28.60; hypothetical 4 / 16 independent paths 36.64 / 38.50; narrowest positive symmetric tolerance 6.10 mV.

A fixed manufacturing offset e in the detector adds e*W to the integral A on every reading; d=(e*W-A)/B. Longer observation grows W, A and B together, so the bias -e*W/B converges to a constant, not to zero. Averaging only reduces error that is independent between readings; one detector read repeatedly supplies the same e every time. The 4- and 16-path rows assume independent paths that are neither built nor costed.

## Observation, inference, limitations
- Observations: the tables above, on fixed analytic trajectories without circuit noise or rail fading, scored on isolated old cases.
- Inference is limited to what an observer computing −A/B from these windows would select; a physical calibration state, its update rule and its own offsets are not implemented.
- Ten components were deliberately selected (two known failures, lowest eight labels); schedules are new but event families are reused. Counts are descriptive, not population estimates.
