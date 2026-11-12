# The muscle-like body: every germane experiment repeated (PROGRAMME.md, Next; the user, 2026-11-11). Predictions and scores

The body: lab/sigmoid_body.py, activation decay 30 ms (the user's choice of the two tried: a lone pulse turns 7 degrees against the old
body's 23; at 60 ms the starting brain lost half its food). Switched on in every worker by MUSCLE=1; the starting brain retuned for it
(lab/retune.py quick search, frozen in lab/v/retune_muscle.json: scan x.82, drive x.89, run x.95, hold x1.13, boredom x1.17), applied by
table.numbers whenever the body is on. The old body stays the default; with the switch off every life is identical (lab/speed_fingerprint
check: 288 of 288). Each step: the same script, the same seeds, analysis frozen; old against new.

## Step 1: the retuned starting brain, judged (`lab/retune.py judge`, fresh seeds 64000+, 30 pairs, 100 s, plain bodies)
M1. On the new body the retuned brain is above the old numbers but not surely (the search found small changes). 55%.
M2. The new body's retuned brain is surely below the old body's (about three quarters of it). 80%.
**Scored M1-M2** (`lab/v/retune_judge.log`): M1 wrong: retuned 1.49 [1.38, 1.60], old numbers 1.51 [1.38, 1.63] on the new body: the
search's gains were its seeds' luck. So the starting brain stays the same on both bodies (retune_muscle.json's factors set to 0, the
searched ones kept as searched_x). M2 right: on the new body it is surely below the old body's 2.41 [2.29, 2.53]: 63% of it.

## Step 2: yardsticks and the body ladder (`lab/bodyladder.py which 5 300`, MUSCLE=1; D42's seeds 86000+, 5 pairs, 300 s, last third)
M3. Unequal thrusters still cost the starting brain at least .8 (the balance still matters). 75%.
M4. Told its balance, the gap closes as before (within .3 of plain). 65%.
M5. Drag at a half or twice costs less than on the old body (fine control copes better with speed changes). 40%.
**Step 2, first run** (`lab/v/muscle_body_which.log`): the told arm did no better than the starting brain on lopsided bodies (.04
against .23). Traced: world.py's told balance log(k1 / k0) assumes thrust proportional to rate; on the muscle-like body thrust is a
sigmoid of rate, so it was the wrong yardstick (for a strength ratio of 2 the right knob is .33, not .69:
`sigmoid_body.told_balance`, equal mean thrust at the drive's rate). Likewise the told tempo (`told_tempo`). Every formula that assumed
a linear body is wrong on this one: the partners link (D47) among them.
**Scored M3-M5** (`lab/v/muscle_body_which2.log`, the yardstick corrected): M3 right: unequal thrusters cost 1.51 (plain 1.74, lopsided
.23). M4 right: told 1.60, within .14 of plain (the old body: 2.52, .94, 2.46). M5 weakly right: drag drawn costs .33 (old .56), at a
half or twice .73 (old .99).

## The knife-edge (`lab/knife.py 10`, both bodies, seeds 86000+, 300 s, last third): efficiency against the knob's error from right
M6. On the old body an error of .1 costs at least a third of plain's score (D52: .1 cost 1.7 of 4.2 in the challenge frame). 70%.
M7. On the new body an error of .1 costs under half as large a share as on the old. 60%.
**Scored M6-M7** (`lab/v/knife_old.log`, `knife_muscle.log`): both wrong, informatively. Old body, plain: error .03 costs nothing (2.49
against 2.52), .1 costs 23%, .2 57%, .4 everything; lopsided alike. New body: .03 costs 27%, .1 84%, .2 everything. The new body is far
steeper in the knob, because the knob sets rates and its thrust is steep in rate (mean thrust .07, .27, .87 at 25, 50, 100 pulses a
second): a 10% rate error is about a 25% thrust error. In thrust terms the two bodies are about equally demanding. And D52's "knife-edge"
(.03 costing .9 in play4's frame) doesn't appear here on the old body: the cost grows smoothly with the error; the unpaired-kick account
looks overstated (to correct in D52).

## Step 3: knob learners (`lab/body_knob.py 5 circuit,toldbody,bank,sized,sweeps,beats`, MUSCLE=1; D43's seeds 86000+, 100/300/1000 s)
M8. The measurers (D20's counters, D43's register) are miscalibrated on the new body (they convert with the old linear formula): neither
    within half of told's gap at 300 s. 65%.
M9. Trial by taste (D19's bank learner, D36's sized) does relatively better than on the old body (it needs no formula). 45%.
**Scored M8-M9** (`lab/v/muscle_body_knob.log`, 5 pairs): M8 right: the measurers fail on the new body (D20's counters -.14, D43's
register -.05 at 300 s, against the starting brain's .23 and told's 1.60; on the old body they were the best, 2.08 and 2.37): they
measure, then convert with the old linear formula. M9 mixed: trial by taste closes 26% of the gap at 300 s (bank .59; old body 5%),
but only 18% at 1000 s (old 59%).
(Reporting fixed for step 4: every script's "right knob" for a learner's error is now the body's own, `sigmoid_body.right_knob`; the
learners' rules untouched.)

## Step 4: coupling (D51, D52) on the new body
M10. Coupling still peaks at the right knob (the body's own) with no reward: within .2 in at least 70% of lopsided bodies. 60%.
M11. The coupling search (with Occam) beats partners (formula, now wrong for this body) surely in 100-300 s. 65%.
**Scored M10** (`lab/v/muscle_couple.log`, 20 lopsided and 10 plain bodies): right. Coupling peaks within .2 of the new body's own right
knob in 95% of lopsided bodies (median .10, correlation +.98), and at 0 on every plain body (old body: 95%, .07, +1.00). The principle
needs no conversion, so the new body's different physics doesn't touch it.
**Scored M11** (`lab/v/muscle_couple_search.log`, fresh seeds 99000+, 20 pairs): right. Partners (the old linear formula) fails on the
new body (-.16, -.17 against forage; knob error .36, 35% within .2); coupling + Occam surely beats it in 100-300 s (+.95 [+.43, +1.47]),
couple:fine in both windows (+.62 [+.02, +1.21], +.98 [+.32, +1.61]); knob within .2 in 90% and 65%; plain bodies left alone after the
search (-.14). Coupling + Occam reaches 42% of told's gap in 100-300 s (old body 72%). P1's play arms not rerun: they all use the
partners formula, wrong on this body, so they would only measure its failure again.

## Step 5: touching pairs (`lab/pairs.py 5`, `careful 5`, `looker 5`, MUSCLE=1; D41's seeds)
M12. Touching pairs still cost the starting brain about as much as on the old body (a quarter of its food, declined not poisoned). 55%.
M13. The careful driver and the looker still win none of the food back (D41: the loss is information, not skill). 65%.
**Scored M12-M13** (`lab/v/muscle_pairs*.log`, D41's seeds 85000+, 5 pairs): M12 half right: touching pairs cost the told arm 44% on the
new body (1.49 to .83) against 29% on the old (2.2 to 1.56); declined, not poisoned, as before. M13 right in substance: the best careful
driver wins +.24 over told (old body +.16), the best looker +.07 (old body: below told); intervals overlap at 5 pairs. Finer control
helps a little, not surely: the loss stays mostly information (where across the corridor a block lies), as D41 found.

## Step 6: the ladders and the tree (`lab/ladders.py certify seq|combo|time 10`, then D40's `teach.py` runs, MUSCLE=1)
M14. Fewer rungs certify on the new body (the starting brain eats less, so a taste-limited life supplies fewer bits). 55%.
M15. The tree still climbs sequences and combinations where rungs certify (x at least .5 on seq 11 and combo 3). 60%.
**Scored M14-M15** (`lab/v/muscle_cert_*.log`, `muscle_tree_*.log`): M14 roughly right: rungs certified on the new body (10 pairs):
seq 2, 3, 5, 7, 11, 13, 17 (seven, as on the old body); combo 1, 4, 5, 6 (old: five); time 2, 3, 6, 11 (old: six). M15 right: the tree
solves seq 11 and 17 (P64 and P256), combo 1, 3, 5, 6 (4 not), time 2 (P1984) and 5 (both sizes); seq 5 unsolved, as on the old body.
Its x often exceeds 1 on this body: the told arm (told the colour, driving as the starting brain) is weaker here, so read solved rungs
against that weaker yardstick.

## Is D52's knife-edge real? (`lab/knife_play4.py 20`: D52's own frame, fresh seeds 100000+, old body, plain)
M16. An error of .03 costs under .3 a 10 s (D52's .9 was its 10 pairs' luck or its seeds). 60%.
**Scored M16** (`lab/v/knife_play4.log`): right. In D52's own frame on fresh seeds (20 pairs, both signs): error .03 costs .19 [-.45,
+.05], not sure; .1 costs 1.11 [-1.33, -.89]. D52's ".03 costs .9" was its 10 pairs and one sign; the cost grows smoothly. The unpaired-
kick account was an over-reading; the Occam check still earned its place, since the search's errors were .05 to .1.
