# D180 tables (regenerated from ledgers by report.py)

## bench_A gate

```
{
 "P_drift_max": 0.0,
 "P_drift_ok": true,
 "no_clip": true,
 "motors_min_events": 203,
 "per_seed_motor_ok": true,
 "pass": true
}
```

## bench_B gate

```
{
 "correct_change_min": 0.02865343127628231,
 "correct_change_max": 0.13170230157515217,
 "size_ok": true,
 "unexposed_max": 0.0,
 "controls_max": 0.0,
 "unexposed_ok": true,
 "controls_ok": true,
 "no_clip": false,
 "n_single": 32,
 "pass": false
}
```

## bench_C gate

```
{
 "side_excess_50ms": [
  0.42578125,
  0.3671875,
  0.48828125
 ],
 "plastic_typ_minus_zero": [
  0.42578125,
  0.36328125,
  0.50390625
 ],
 "no_clip": true,
 "side_ok": true,
 "plastic_ok": true
}
```

## action: not triggered — R3/R4 progression gate failed

## action_auth

### action_auth: 384 of 384 expected lives; missing 0

| arm (removal) | lives | net food/10 s, final third | food/10 s | poison/10 s | food−3·poison | pooled food:poison | no-meal lives | seed-any-stranded Wilson upper | never moved | motor events/life | power (nW) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| informed (none) | 64 | +0.06 [+0.00, +0.11] | +0.19 [+0.14, +0.25] | +0.14 [+0.09, +0.19] | -0.22 [-0.34, -0.09] | 1.41 | 4/64 | 0.281 | 0 | 818 | 99.5 |
| neutral (none) | 64 | +0.00 [+0.00, +0.00] | +0.16 [+0.09, +0.24] | +0.16 [+0.09, +0.24] | -0.32 [-0.49, -0.18] | 1.0 | 8/64 | 0.281 | 0 | 792 | 99.5 |
| no_explore (no_explore) | 64 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] | 0:0 | 56/64 | 0.983 | 38 | 8 | 83.8 |
| no_sensory (no_sensory) | 64 | +0.00 [+0.00, +0.00] | +0.13 [+0.06, +0.21] | +0.13 [+0.06, +0.21] | -0.25 [-0.41, -0.11] | 1.0 | 6/64 | 0.242 | 0 | 715 | 63.8 |
| reversed (none) | 64 | -0.06 [-0.11, -0.00] | +0.14 [+0.09, +0.19] | +0.19 [+0.14, +0.25] | -0.44 [-0.60, -0.29] | 0.71 | 4/64 | 0.281 | 0 | 818 | 99.5 |
| informed_allfood (none) | 32 | +0.47 [+0.33, +0.62] | +0.47 [+0.33, +0.62] | +0.00 [+0.00, +0.00] | +0.47 [+0.33, +0.62] | 50:0 | 2/32 | 0.201 | 0 | 839 | 105.9 |
| neutral_allfood (none) | 32 | +0.32 [+0.18, +0.49] | +0.32 [+0.18, +0.49] | +0.00 [+0.00, +0.00] | +0.32 [+0.18, +0.49] | 34:0 | 4/32 | 0.281 | 0 | 792 | 99.5 |

| arm | acquired ever | acquired at end | median first acquisition (s; missing = never) | mean fraction of life acquired | exits | re-entries | right order at end | P min / max (V) | mean s with a P outside [0, V_TYP] |
|---|---|---|---|---|---|---|---|---|---|
| informed | 64 | 64 | 0.0 (missing 0) | 1.000 | 0 | 0 | 64 | -0.005 / +0.323 | 100.0 |
| neutral | 0 | 0 | None (missing 64) | 0.000 | 0 | 0 | 2 | +0.145 / +0.152 | 0.0 |
| no_explore | 64 | 64 | 0.0 (missing 0) | 1.000 | 0 | 0 | 64 | -0.005 / +0.300 | 100.0 |
| no_sensory | 64 | 64 | 0.0 (missing 0) | 1.000 | 0 | 0 | 64 | -0.005 / +0.326 | 100.0 |
| reversed | 0 | 0 | None (missing 64) | 0.000 | 0 | 0 | 0 | -0.005 / +0.323 | 100.0 |

## learn: not triggered — R5 informed-action gate failed or not triggered

## confirm_r1: not triggered — R6 learning gate failed or not triggered

## confirm_r2: not triggered — confirmation not triggered

## confirm_r4: not triggered — confirmation not triggered

