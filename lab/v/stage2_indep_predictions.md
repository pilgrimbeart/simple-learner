# Independent check of the stage-2 engine: predictions (written before any run, 2026-11-06)

Checker: an agent that did not build the engine and has not read lab/stage2_checks.py, stage2_repro.py,
stage2_finer_ref.py or their logs. Seeds 64000-64999 only. Read so far: AGENTS.md, PROGRAMME.md, D33, lab/stage2_lang/
(lang.py, sim.py, worlds.py, arms.py), world.py, creature.py, discrete/model.py, lab/universal_v.py, lab/table.py,
lab/ladder.py's rules, lab/bits_bank.py's head, lab/stage2_run.py's guard.

## 1. Identity (no rule against creature.Life)
- P1.1 Raw discrete/model.py Model (drawn from its bench), story 1's Circuit (table.Circuit) and the bank
  (universal_v.V with universal_v7.json via table.numbers): every brain call (stimulate with sensor and moment,
  step's motors, taste with value and moment), every body state per tick, meals and firings identical in all 100
  lives each (50 seeds x 2 colours). Confidence 85%.
- P1.2 If anything differs it will be a float-level difference in the ray kernel (bright * share vs SHARE), not a
  draw-order difference. 10%.

## 2. Worlds against their descriptions
- P2.1 swap10: poison flips exactly at 10, 20, ... s (to the tick); every meal's badness follows the formula. 90%.
- P2.2 alternate, pattern, digest: every meal's badness matches my own re-implementation from the description, except
  possibly in ticks with two meals at once, where the description is ambiguous. 75% that no meal in a single-meal
  tick differs.
- P2.3 unreliable: lie rate per meal .2 within its 95% interval; coin .5 likewise. 90%.
- P2.4 weak: the weak eye's pulses / expected (SENSE x seen x dt, from world.py's own ray functions) about .25, the
  other eye's about 1. noisy: the noisy eye's excess about 10 per s, the other 0. 85%.
- P2.5 patchy: blocks within a few sd (3 mm) of 4 fixed centres after birth. 85%.
- P2.6 late_swap_50: P is poison before 50 s, F after, to the tick. 90%.
- P2.7 every5th: "every fifth meal" will not hold exactly when two meals fall in one tick (the count moves at the
  score, after the meals' signs are set). 60% that I find at least one such meal in 100 lives.
- P2.8 crosstalk: each eye's rate equals SENSE x (own + .3 other) from world.py's rays. 85%.
- P2.9 halfthrust_const and halfthrust_gain give identical lives. 80%.

## 3. Sanity attacks
- P3.1 The engine passes a brain nothing but stimulate, step and taste; but the language has `bp` (a world writes the
  brain's parameters; sag uses it) and arms.py hands the bank a `spy` (watching only). I expect `bp` to be a real
  channel that no refusal catches. 80%.
- P3.2 A taste's moment is uniform in its tick and independent of its sign (KS p > .01). 90%. Injected pulses
  (noisy) are delivered before the body's in each tick, so call order carries a little information about which pulses
  are spurious (as in table.py's wrapper too). 70%.
- P3.3 Worlds whose hooks exist but never act (no-op see, fire, meal, taste, score, move; a rule drawing from its
  stream every tick; onset after the life) give lives identical to plain. 85%.
- P3.4 The marked stage-5 worlds are refused by stage2_run.guard. 95%. An unmarked liar (taste inverted, no meta), a
  taste set to 0 or to .5, a score made to disagree with the taste, and a world writing the brain's parameters (bp) are
  not refused. 75%.

## 4. Description length
- P4.1 Invariant to consistent renaming of state variables and of (each) variables, to comments and to meta. 85%.
- P4.2 Not invariant to reordering (let ...) declarations. 60%.
- P4.3 Ranks plain (0) < swap10 ~ swap11 < alternate < pattern < parity, cells. 70%.
