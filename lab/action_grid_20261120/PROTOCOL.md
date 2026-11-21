# Action grid — frozen protocol (R0), 2026-11-20

Frozen before any grid simulation. The work order (`../WORK_ORDER_2026-11-20_action_grid.md`, sha256 f0115523…)
owns every decision; this file records how the code implements it and the few executor details it leaves open.
Input hashes at start: variants.py 9484a30d…, PLAN.json d34142ee… (PLAN.json regenerated from variants.py: identical).

**Engine and observer.** `ag_engine.GridEngine` subclasses D180's `Engine` (read-only) with `spec = variants.graph(config)`;
full graph and mismatch drawn before removals, D180 seeds/initial states/wiring. `_loop_obs` calls the unchanged
`mixed_feedback._step` exactly as D180's `_loop` and only reads afterwards: per-tick substep counts of each motor above
zero and not armed; per gated edge, the sum of the engine's gate factor clip(V_gate/V_TYP,0,1) and the steps it is
open; per-node source events; pre-clip rail excursions, extrema, slew; motor event and re-arm steps. Body observation
wraps `body.sees` on the Life instance (Life calls it first in each step, so the record is the pre-step state;
no RNG use). `creature.Life` is unchanged; taste withheld (`learning=False`) in every life.

**Timing conventions (D180's).** A motor event or re-arm at fine step k is timed k·dt. A motor is unarmed from its
event step to its re-arm step; an interval open at the end is censored at the end. Occupancy (above zero, unarmed) is
counted from substep states; the unarmed count is cross-checked against the event/re-arm intervals in every life.
"Unarmed immediately before an onset at t": the state after fine step floor(t/dt)−1.

**Benches (R2).** 81 × seeds 0–7 × P∈{0,0.15,0.30} (both) × removal∈{none,no_explore} × channel∈{0,1} ×
schedule∈{silent,single,train,sustained}; 10 s; native noise; jitter j=default_rng([seed,182,channel]).uniform(0,0.009).
Windows [0,1), [1,3.25), [3.25,10) s. Active-minus-silent contrasts use the same (config, seed, P, removal, channel).
Realised-limit failure ⇒ named invalid job (not simulated, kept in denominators); nonfinite ⇒ job stopped with log.

**Development (R3).** 81 × seeds 8–39 × {red, blue} × {informed, neutral, reversed, no_explore, no_sensory} +
all-food {informed, neutral}: 31,104 lives, 100 s, native. Ten-node traces and body traces archived for baseline only;
event/re-arm/pulse/firing records for all lives (git-ignored pkl).

**Predeclared bench-to-life associations (descriptive, no others).** Per configuration, at P=0.30, removal none,
window [1,3.25) s, seed means: (a) single-minus-silent fixed-side motor events; (b) sustained-minus-silent fixed-side
motor events; (c) sustained fixed-side unarmed fraction. Each reported beside development informed net, with the
Spearman rank correlation across the 81 configurations. Descriptive only.

**Selection (R5).** Exactly as work order §8 (ag_analysis.rank; fixture-tested). "Mean informed food" = mean over
seeds of the final-third food rate (per 10 s) of the informed arm (red/blue averaged within seed).

**Confirmation (R6/R7).** Baseline + 3 selected × 128 fresh seeds × 12 lives × ratios 1, 2, 4, coupled noise;
seed block from `ag_seeds.py` (frozen in confirm_freeze.json before jobs). Primary: candidate-minus-baseline informed
net, paired by seed, 95% and 98.333% (Bonferroni-3) intervals. Improved iff corrected lower > 0 at all ratios;
practically established iff corrected lower > +0.10 at all ratios. No-harm: all-food (informed_allfood) food-rate
contrast lower 95% > −0.05; stranding (informed arm, seed mean of red/blue) contrast upper 95% < +0.05. Physical
eligibility: every completed candidate life at every ratio with zero pre-clip excursions and passing realised limits.
Convergence: the per-seed change of each contrast between ratios 1→2 and 2→4, 95% interval inside ±0.05.

**Stopping.** Hard 12 h from 18:28:04Z. All stages run whatever the results; failures are recorded, not substituted.
