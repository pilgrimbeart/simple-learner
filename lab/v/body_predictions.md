# D42: the lopsided body as the acting ladder. Predictions (main session, 2026-11-10), before any life

`lab/bodyladder.py which`: 5 pairs of 300 s lives (judged on the last third). The user's ladder: rungs by how many of the body's numbers
are drawn. Before writing rungs, which numbers cost the starting brain anything? The belief it could move: that the body offers more
than one thing to learn. D5 found, in an older engine and brain, that bodies built differently barely move the best settings, except
unequal thrusters. If that still holds, a ladder of body numbers has one rung, and the acting ladder must be built another way.
1. Unequal thrusters cost the starting brain at least 1 against plain. 85%.
2. Told its balance, it is back within .3 of plain. 70% (D13: nearly everything recovered; but overall strength still varies).
3. Each of the others (both thrusters together, both eyes, one eye, drag) costs under .4. 60% that all four do; drag and strength I am
   least sure of (speed changes how far a hold carries the creature).
4. The bank, with D19's learner inside, is above the starting brain on unequal thrusters but closes under half the gap in 300 s. 65%.

**Scored (`lab/v/body_which.log`).** 1 right: unequal thrusters cost 1.6 (plain 2.52, lopsided .94). 2 right: told its balance, 2.46. 4 right:
the bank 1.02, barely above the starting brain in 300 s. 3 wrong, usefully: strength, both eyes and one eye cost nothing (2.59, 2.48,
2.20), but drag at a half or twice costs 1.0 (1.53). At .7 and 1.4 times it costs nothing; at a half 1.46, at twice 1.61.
**Drag's cure, by hand** (same seeds): speed goes as firing rate over drag, so scale every rate (scan, drive, run) by the drag. At half
drag that gives 2.54, everything back; at twice, 1.98 of 2.52 (the rest is the price of firing twice as often). Single knobs do less
(drive and run alone 2.05 and 1.89). So the body has two numbers worth learning: the balance between the motors, and a tempo for both.

## Rungs 1 and 2. Predictions before their lives
Worlds with the numbers drawn per life (drag written as an extra fading each tick, checked against the constant): thrusters; drag;
both. Arms: the starting brain, the same told its body (balance and tempo), the bank. 5 pairs, 300 s.
5. The drawn-drag world written as extra fading scores as the constant-drag worlds did (1.53 as born), within .3. 75%.
6. Drag drawn between a half and twice costs less than the two extremes: .3 to .8 below plain. 65%. Told its tempo, at least half back. 60%.
7. Both drawn: the starting brain under 1.0; told both, above 2.0. 60%.

**Scored 5-7 (`lab/v/body_rungs.log`).** 5 right: extra fading 1.65 against the constants' 1.53. 7 right: both drawn .86 [.02, 1.65], told
both 2.48 [2.00, 2.98]. 6 half right: drag drawn between a half and twice costs .56 (1.96 against plain's 2.52), but told its tempo the
brain scores 1.92, no better: drag hurts only near the ends of its range (nothing at .7 or 1.4 times), where few of five draws fall.
So as the body stands it has one number that matters much (the balance) and one that matters at the extremes (the tempo); strength and
the eyes' sensitivity don't matter at all. A ladder of body numbers is one sure rung and one weak one.

## Turning the balance knob: trial and error against measurement (D43). Predictions and scores
`lab/body_knob.py`, unequal thrusters, 5 pairs, the last third of lives of 100, 300 and 1000 s. Knob untouched .49, .94, .74; set right
2.42, 2.46, 2.36.
- Trial and error (predicted: over half the gap by 1000 s, 55%; under a quarter at 100 s, 75%): the bank's learner (D19) .33, 1.02, 1.62;
  the self-sizing one (D36) .14, .65, 1.50. Right on both: about half the gap at 1000 s, nothing or worse at 100 s.
- Measurement, D20's sweeps with 192 counters (predicted: over 70% of the gap by 300 s, 65%; over half at 100 s, 35%): 1.78 [.45, 3.04],
  2.08, 2.05. Right at 300 s (75%); at 100 s the point says yes and the interval says nothing.
**The generic unit as the measurer** (`beats`): a register that takes one cell per beat of the brain's own motor during a sweep, and a
comparing unit per look-back, D38's record. The best look-back is the beats in a revolution. Sweeps' timing as D20's.
8. Within .3 of the counters' 2.08 at 300 s. 50%. Above 1.6 (well clear of trial and error's 1.02), 70%.
Least sure of: a revolution is 10 to 40 beats and rarely a whole number; and each sweep is only 3 to 10 revolutions.

**Scored 8 (`lab/v/body_knob_beats.log`).** Right: .89 [.41, 1.41], 2.37 [1.76, 2.81], 2.01 [1.27, 2.48] at 100, 300 and 1000 s, against the
counters' 1.78, 2.08, 2.05 and the knob set right 2.42, 2.46, 2.36. At 300 s it is 94% of the gap. On an ordinary body at 300 s it scores
2.37 [1.68, 3.06] against the starting brain's 2.52: no sure cost (unpredicted; one check).
