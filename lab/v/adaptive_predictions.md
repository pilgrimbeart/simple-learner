# The adaptive wobble (`lab/adaptive.py`): predictions, written before any of its lives (main session, 2026-11-08)

The bank with its fixed jitter gate replaced by rules 1 and 2 (the module's docstring), its numbers chosen generically before any life
(z 2, a0 1, n_a 100 drives, n_z 200 drives, tau_f 100 s, tau_s 1000 s) and not to be tuned on what follows.
1. Plain, 10,000 s (the scaling test's seeds): within .1 of base (the old bank -.40), the wobble's size below .2 for most of the life.
2. Plain, 100 s: within .1 of the old bank. Being born exploring costs something in the first 100 s; I expect under .1.
3. The worlds of weak or lopsided thrusters (stage 3's L5 weak, L2 push, drag, spinbias, current) at 100 s: within .1 of the old bank,
   none surely worse by more than .1.
4. Stage 3's 55 worlds with something to learn at 100 s: coverage within one world of the old bank's.

**Scored on the diagnosis seeds, then redesigned** (2026-11-08; the scaling test's seeds 81400-81409, which are therefore spent for
judging this block). Prediction 1 failed: plain at 10,000 s, the adaptive bank -.22 [-.29,-.15] (`lab/v/adaptive_plain10k.log`); with
re-arming off -.43; with the wobble never on +.03 (`_rearm0.log`, `_a00.log`). Traced (`lab/adaptive_x.py`, `lab/v/adaptive_x*.log`,
2000 s lives): the balance learner's setting random-walks while it wobbles (|x| .07, up to .19) and freezes when the wobble stops; |x|
against the life's gain, correlation -.79. Not a proxy: the learner's own measure falls too (food pulses a drive 4.76 to 3.72). Polyak
averaging fails (a walk without restoring force averages to a walk). Rule 3' (keep a change only if its evidence is significant, else go
back) gives .405 a second against .421 never wobbling and .352 the old way; no life kept a change.

**Predictions for rules 1, 2 and 3' (avg=2), written before these lives, on fresh seeds:**
5. Plain, 10,000 s (seeds 81600-81609 x red/blue): the adaptive bank within .1 of base, where the old bank is surely below by more.
6. The thrusters world (each thruster's strength 0.5 to 2, where the balance learner was built to help), 100 s, 60 pairs (seeds
   81610-81639): the old bank surely better than a bank that never wobbles (else the balance learner isn't needed at 100 s at all), and
   the adaptive bank within .1 of the old bank.
7. The thrusters world at 1000 s (20 pairs, seeds 81640-81649): the adaptive bank at least as good as the old bank.

**Scored on fresh seeds** (`lab/v/adaptive_fresh.log`):
5. Wrong: in plain at 10,000 s the adaptive bank is surely below base (-.28 [-.44,-.16]) and below the old bank (-.20 [-.42,-.02]). And
   on these seeds the old bank is not surely below base (-.08 [-.19,+.03]), where on the scaling test's seeds it was -.40 [-.60,-.20]:
   the old bank's long-life loss is real on one set of 10 pairs and not shown on another, so its size is not yet known.
6. Premise wrong: at 100 s the old bank equals the bank that never wobbles (+.00 [-.02,+.03]), so the balance learner does nothing at
   100 s in the thrusters world. The adaptive bank, born exploring, is better than both (+.21 [+.01,+.42]).
7. Wrong: at 1000 s the old bank gains 1.17 over base and the adaptive bank only .17; never wobbling gains nothing. The balance learner
   matters in long lives, and rule 3' (or rule 2's quieting) stops it before it has learned.

Sized afterwards (`lab/v/plain_long_size.log`, 50 pairs pooled): the old bank in plain at 10,000 s is -.235 [-.32,-.15] below base.

**The self-sizing learner (`lab/rprop.py`), predictions written before its judged lives** (2026-11-08; one 300 s smoke life on seed 99
only, which reached x -.6 of a right .69 in 50 s). Its numbers are generic and are not to be tuned on what follows. Fresh seeds, the
runner `lab/rprop_fresh.py`:
8. Double thruster (the right |x| .69), 2000 s, seeds 81900-81919: the sized learner's |x| at 200 s at least .5 on average, where the
   old learner's is under .2; by 2000 s within .15 of .69 for most lives.
9. Thrusters, 100 s, seeds 81920-81949: the sized bank surely above the old bank and the never-wobbling bank.
10. Thrusters, 1000 s, seeds 81950-81959: the sized bank at least as good as the old bank (+1.17 over base on other seeds).
11. Plain, 10,000 s, seeds 81960-81969: the sized bank within .1 of base and not surely below it. The risk I see: in plain a
    false-significant move (1 in 20 tries at z 2) can step x off the peak, where the response's sharp peak makes it costly.

**Scored on fresh seeds** (`lab/v/rprop_fresh.log`):
8. Wrong: the sized learner's |x| is .10 at 100 s (the old .01) but stops there: .13 at 200 s, .14 at 2000 s; the old reaches .66.
9. Not shown: at 100 s the sized bank +.12 [-.14,+.38] over the old bank; the old again equals never wobbling (+.02 [-.00,+.05]).
10. Not ruled out, not shown: at 1000 s the sized bank -.16 [-.56,+.15] against the old; both surely above never wobbling.
11. Wrong: plain at 10,000 s, the sized bank -.20 [-.27,-.13] below base, the same as the old bank (-.20 [-.35,-.07]).

**v2 of the sized learner: no give-ups** (the trace: each give-up discarded the evidence and halved the wobble). Its sums run until
significant however long that takes; D shrinks only on a reversal. Predictions written before its lives (`lab/rprop_fresh.py 2`,
fresh seeds 82000-82059); plain not run, its harm control awaiting the user's decision (a nearly-plain world):
12. Double thruster, 2000 s: v2's |x| at 500 s at least the old learner's, and at 2000 s within .1 of .69 in at least 30 of 40 lives.
13. Thrusters, 100 s: v2 not surely worse than the old bank (both near never wobbling at 100 s).
14. Thrusters, 1000 s: v2 at least as good as the old bank, and surely above never wobbling.

**Scored** (`lab/v/rprop_fresh2.log`):
12. Half: |x| at 500 s .54 against the old .55 (equal within noise; v2 well ahead earlier: .14 against .01 at 100 s, .38 against .15 at
    200 s); within .1 of .69 at 2000 s in 36 of 40 lives (the old 32). Four lives stuck far off (0, .22, .40, .50), many pinned at .60.
13. Held: at 100 s v2 +.03 [-.27,+.32] against the old bank (wide).
14. Half: surely above never wobbling (+.78); against the old bank -.19 [-.59,+.18] (with v1's -.16 on other seeds, probably a little worse).

**Traced** (`lab/v/rprop_trace2.log`, `lab/v/peak_far.log`): v2's stuck lives are weak evidence (one life's slope at x 0 .31 pulses a
unit against 1.2 on average, so ~950 drives for a significant sum; a large wobble also raises the total thrust, e^(x/2) + e^(-x/2), which
dilutes the first-order signal) and overshoots (the step doubling to .6-.8 throws x to 1.2-1.4, then a long wait to come back).

**v3: v2 with its step never above its born .3** (one change, against the overshoots). Predictions before its lives (`lab/rprop_fresh.py
3`, fresh seeds 82100-82159):
15. Double thruster, 2000 s: |x| at 300 s above the old learner's surely (v2 .47 against .34, on other seeds) and within .1 of .69 at 2000 s
    in at least 34 of 40 lives.
16. Thrusters, 100 s: not surely worse than the old bank.
17. Thrusters, 1000 s: within .1 of the old bank or better (v1 and v2 were -.16 and -.19).

**Scored** (`lab/v/rprop_fresh3.log`, `_fresh3b.log`; the first run crashed after its track, a variable's name reused, and its other two
tests were rerun unchanged):
15. Held: |x| at 300 s .45 against the old .31, +.13 [+.01,+.26] (at 100 s +.19 [+.10,+.29], 200 s +.19 [+.08,+.31], 500 s +.09
    [-.02,+.18]); within .1 of .69 at 2000 s in 40 of 40 (the old 35).
16. Held: at 100 s -.01 [-.25,+.22] against the old bank; neither above never wobbling.
17. Wrong: at 1000 s -.32 [-.65,+.02] against the old bank (the third version below it there: -.16, -.19, -.32). Being diagnosed
    (`rprop_fresh.py 3f`, on 17's seeds): its floor wobble of .05 never stops, where the old one's gate stops it while meals are easy.

**Diagnosed** (`lab/v/rprop_fresh3f.log`, `lab/rprop_right.py`, `lab/v/rprop_right.log`): not the floor wobble (without it -.37
[-.74,+.03]); not balance accuracy (|x - right| at 1000 s .09 against the old .08). A life born near right never gets a significant sum, so
never reverses, so never quiets: its wobble stays .3 for life (seed 82150, right -.06: x 0 throughout, the last third 22 and 53 meals
against the old learner's 80 and 74).

**v4: v3 with give-ups that keep the evidence** (after 50 drives with nothing significant the step and wobble halve, the sums carry on).
Predictions before its lives (`lab/rprop_fresh.py 4`, fresh seeds 82200-82259):
18. Double thruster, 2000 s: |x| at 300 s surely above the old learner's; within .1 of .69 at 2000 s in at least 34 of 40.
19. Thrusters, 100 s: not surely worse than the old bank.
20. Thrusters, 1000 s: within .1 of the old bank or better.

**Scored** (`lab/v/rprop_fresh4.log`): 18 wrong (|x| .20 at 100 s, then frozen: .22 at 2000 s; the old .66), 19 held (+.14 [-.13,+.37]),
20 wrong (-.81 [-1.44,-.21]). Give-ups halve the step too, so a later significant move is .0125: frozen as v1 was.

**v5: give-ups halve only the wobble** (sums kept; the step changes only on moves; a move restores the wobble to the step). Predictions
before its lives (`lab/rprop_fresh.py 5`, fresh seeds 82300-82359):
21. Double thruster, 2000 s: |x| at 300 s at least the old learner's; within .1 of .69 at 2000 s in at least 30 of 40.
22. Thrusters, 100 s: not surely worse than the old bank.
23. Thrusters, 1000 s: within .15 of the old bank or better.

**Scored** (`lab/v/rprop_fresh5.log`): 21 wrong (|x| .25 at 100 s, then frozen: .31 at 2000 s, the old .67); 22 held (+.20 [-.01,+.42]);
23 held (-.10 [-.43,+.22]). Any rule that quiets for want of significant evidence also quiets the lives far from right whose evidence is
merely slow (v1, v4, v5 alike).

**v6: v3 quieting only on a peak's mark**: the wobble surely hurts whichever way it goes (the sum of d (e^2 - sd^2) two standard
errors below 0), halving the wobble each time; a move restores it. Far from right that sum is not negative (there a large wobble even
helps, by more total thrust), so it keeps exploring. Predictions before its lives (`lab/rprop_fresh.py 6`, fresh seeds 82400-82459):
24. Double thruster, 2000 s: |x| at 300 s surely above the old learner's; within .1 of .69 at 2000 s in at least 34 of 40.
25. Thrusters, 100 s: not surely worse than the old bank.
26. Thrusters, 1000 s: within .1 of the old bank or better.

**Scored** (`lab/v/rprop_fresh6.log`): 24 held (|x| at 300 s .43 against .32, +.11 [+.02,+.19]; 100 s +.19 [+.11,+.28]; within .1 of .69
at 2000 s in 37 of 40, the old 30); 25 held (-.11 [-.34,+.10], leaning worse; against base -.20 [-.41,-.00]); 26 held (+.17 [-.02,+.36]):
the first version not below the old learner at 1000 s.

**v6's long-life harm** (`lab/rprop_fresh.py 6L`, 10,000 s, last third; fresh seeds): plain on 82460-82469, and beside it, not in place of
it (the user's decision pending), a nearly-plain world, each thruster 0.95 to 1.05 (`NEAR`), on 82470-82479. Predictions before the lives:
27. Plain: v6 below base by .1 or more (its floor wobble .05 meets plain's knife-edge, `lab/v/rprop_cost.log`: -.25).
28. Nearly plain: v6 within .1 of base, and not surely below the old bank.

**Scored** (`lab/v/rprop_fresh6L.log`): 27 held (plain -.25 [-.33,-.17] against base; the old bank -.31 [-.55,-.09]); 28 held (nearly
plain -.05 [-.21,+.15] against base, +.01 [-.19,+.25] against the old bank).

**v7: v6 with its wobble's floor .005 instead of .05**, so its own peak test, which halves the wobble only while the wobble surely hurts,
sets how quiet it gets. Predictions before its lives (`lab/rprop_fresh.py 7`, fresh seeds 82500-82549):
29. Double thruster, 2000 s: as v6, |x| at 300 s surely above the old learner's, within .1 of .69 at 2000 s in at least 34 of 40.
30. Thrusters, 1000 s: not surely below the old bank.
31. Plain, 10,000 s: within .1 of base (v6 -.25).
32. Nearly plain, 10,000 s: within .1 of base.

**v8: v7 with an always-valid bar on its quieting test** (Robbins' normal mixture: checked after every drive, a false "the wobble hurts"
ever only 5% likely, where v7's two-standard-error test, checked every drive, eventually fires by chance; three of v7's 40 double-thruster
lives never left 0). Predictions before its lives (`lab/rprop_fresh.py 8`, fresh seeds 82600-82669):
33. Double thruster, 2000 s: no life left within .05 of 0 at 2000 s; within .1 of .69 in at least 35 of 40.
34. Thrusters, 100 s: not surely worse than the old bank.
35. Thrusters, 1000 s: not surely below the old bank.
36. Plain, 10,000 s: within .1 of base (v7 -.06), perhaps a little worse than v7 (it quiets more slowly).

**v7 scored** (`lab/v/rprop_fresh7.log`): 29 wrong (|x| ahead of the old learner surely at 100 s, +.11 [+.04,+.18], and 200 s, +.12
[+.01,+.23], not at 300 s, +.09 [-.04,+.22]; within .1 of .69 at 2000 s in 33 of 40, the old 37; three lives never left 0: chance
quieting far from right, the floor gone); 30 held (thrusters 1000 s -.17 [-.57,+.22]); 31 held, narrowly (plain -.06 [-.12,-.01] against
base, v6 -.25: the floor was most of the harm); 32 held (nearly plain +.10 [-.06,+.28] against base, +.26 [+.16,+.37] against the old
bank, which is surely below base there, -.16 [-.26,-.06]).

**v8 scored** (`lab/v/rprop_fresh8.log`): 33 held (no life near 0; within .1 of .69 in 39 of 40, the old 30; |x| surely ahead at 100, 200,
300 s: +.12 [+.05,+.20], +.18 [+.06,+.29], +.21 [+.12,+.29]); 34 held (+.03 [-.21,+.26]); 35 held (+.17 [-.18,+.54]); 36 wrong (plain
-.19 [-.25,-.11] against base, v7 -.06): the always-valid bar quiets too slowly in plain. v7 and v8 trade: v7 quiets plain but sometimes
falsely far from right, v8 never falsely but too slowly. The night's scaling and stage 3 runs use v7 (the scaling test's confound was
plain's wear-down).

**v7 firmed up** (`lab/rprop_fresh.py 7m`, 20 more pairs each, fresh seeds 82700-82759; predictions before the lives): 37. Double thruster:
v7 leaves 1 to 4 lives of 40 within .05 of 0 at 2000 s (its chance quieting). 38. Plain 10,000 s: v7 within .1 of base, pooled with the
first 10 pairs. 39. Nearly plain 10,000 s: v7 not surely below base, and surely above the old bank pooled with the first 10 pairs.

**v9** (`lab/rprop9.py`, `lab/rprop_fresh9.py`, fresh seeds 82800-82849; written before its lives). Cause found in v7's plain traces: 2 of
20 lives sat at x = +-.3 for 100 s or more in the last third, chance moves of a step nothing had ever halved (v7's move test, two
standard errors checked every drive, fires by chance eventually). v9a: the move test's bar always valid; v9b: v9a, and the peak's mark
halves the step too. Predictions:
40. Plain, 10,000 s: v9a and v9b each within .05 of base, and v9b not surely below v7 on the same seeds.
41. Nearly plain, 10,000 s: neither surely below base.
42. Double thruster, 2000 s: both slower than v7 early (|x| at 300 s not surely above the old learner's), within .1 of .69 at 2000 s in
    at least 32 of 40; v9b leaves no more lives near 0 than v9a.
43. Thrusters, 1000 s: neither surely below the old bank.

**Why v7 costs so much in 100 s lives** (stage 3 with the cure, `lab/v/stage3_cure.log`: bankS - bank -.60 on average over 184 worlds;
the construction checked, the old bank's lives reproduced exactly). `lab/rprop_short.py`, plain, g402 and thrusters, 100 s, fresh seeds
82900-82929; predictions before its lives:
44. Plain: v7 surely below the old bank; never moving (nomove) recovers less than half of v7's loss: its wobble, born .3 and still large
    at 100 s, is most of the cost, not chance moves.
45. Born with the wobble .1 (v7D1) recovers more than half of the loss in plain, and is not surely below v7 in the thrusters.
46. v9a and v9b each recover less than half in plain.

**Scored 44-46** (`lab/v/rprop_short.log`): 44 held (plain: v7 -1.09 [-1.32,-.86] below the old bank, -1.30 below base, about half
base's food; never moving recovers .11 of it); 45 held (v7D1 recovers .77 in plain, .74 in g402; in the thrusters -.11 [-.33,+.11] against
v7, not surely below); 46 held (v9a .11, v9b .29). The wobble is the cost at 100 s, and even .1 costs plain .53. v9a equals nomove
exactly in plain: no move happened in either.
Next (`lab/rprop_wobble_signal.py`, before its lives): 47. The cost grows about linearly with a fixed wobble (plain's cusp), and the
peak test's signal per drive is small (over 50 drives to two standard errors at sd .3): a drive's own pulses see little of what a
wobble costs, most of it falling outside the drive.

**Scored 47** (`lab/v/rprop_wobble_signal.log`): half wrong. The cost is concave, not linear: a fixed wobble of .05 costs -.28 [-.45,-.11]
(11%), .1 -.55, .2 -.84, .3 -1.22. A drive's own pulses do see it (pulses a drive 4.27 at no wobble, 3.81 at .05: the same 11%), but the
peak test's signal per drive is tiny: about 1,400 drives to two standard errors at .05, 200 at .1, 90 at .2-.3; a 100 s life has about
96. So no rule judging its wobble by its drives can make a born-exploring learner safe in short plain lives.
**The old gate kept** (`lab/rprop_gate.py`, a diagnostic; fresh seeds 82960-82989, before its lives): 48. v7 and v9b with the old fixed
gate (v7g, v9bg) within .1 of the old bank in plain, g402 and nearly plain at 100 s, and not surely below v7 in the thrusters.
**Scored 48** (`lab/v/rprop_gate.log`): held, trivially. With the old gate, v7 and v9b are identical to the old bank in plain, g402 and
nearly plain (the gate never opens in a 100 s life eating normally), and within .02 of it in the thrusters. The old bank is safe at 100 s
because it barely wobbles at all; and at 100 s in the thrusters it is surely below base (-.15 [-.27,-.02]): balancing doesn't pay in
100 s anywhere tested.

**Scored 37-38** (`lab/v/rprop_fresh7m.log`, pooled with `_fresh7.log`): 37 held (1 of 40 lives within .05 of 0 at 2000 s; 4 of 80 over
both runs); but at 2000 s v7 is behind the old learner here, |x| .59 against .70, within .1 of .69 in 32 of 40 (old 35). 38 wrong:
plain at 10,000 s, 30 pairs pooled, v7 -.117 [-.157,-.079] against base, the old bank -.111 [-.201,-.029]; v7 minus old -.006
[-.101,+.094]. The first 10 pairs' -.06 was luck; in plain at 10,000 s v7 is no better than the old bank, only steadier.
