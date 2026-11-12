# The dancing brain, D0: count the bits. Predictions (main session, 2026-11-10), before any life

`lab/dance0.py`: 600 bodies per cycle, each thruster and the drag drawn per life (a half to twice), 100 s lives at 2.5 ms, seeds 87000+.
Ten arms: the starting brain foraging, and nine open-loop cycles (still; spin on motor 0; on motor 1; D20's sweeps, 8 s on each; straight,
both at the drive's rate; burst, 0.1 s of drive in each second; zigzags of 0.5, 2 and 8 s). The observer: a ridge decoder fitted across
lives, on generic features of pulses and beats; bits a lower bound, I >= h(prior) - 1/2 log2(2 pi e MSE).

The sum first. A beat moves the body k PUSH / (d DRAG) and turns it k TURN / (d DRAG): strength k and drag d are one number to the eyes,
except through the coast's time course (1 / (d DRAG), 10 to 40 ms, against eye pulses at most 50 a second). So the things are the balance
log(k0 / k1), the stride log(sqrt(k0 k1) / d), and drag on its own. Spinning on motor 0 alone times log k0 - log d = stride + balance / 2;
on its own that tells the balance only about 0.2 bits (prior variances .32 and .24). Knowing the stride exactly tells drag 0.8 bits.

1. **Still** gives 0 bits about everything (a check on the decoder's honesty). 95%.
2. **Sweeps** (both motors timed) give at least 3 bits on the balance and on the stride by 100 s. 70%.
3. **Spin on one motor** gives under 0.6 bits on the balance at 100 s, but at least 2 on the stride. 60%.
4. **Drag beyond the stride**: no arm gets more than 0.3 bits on drag above what its stride bits imply (about 0.8 bits at most). 75%.
5. **Straight** (a lopsided body circles) gives at least 2 bits on the balance by 100 s. 50%.
6. **Burst** gives at least 2 bits on the stride by 100 s. 50%.
7. **Foraging** gives at least 1 bit on the balance by 100 s (D20: the starting brain's scans carry the body). 55%.
8. **The decision**: some cycle gives at least 2 bits more than foraging on the balance at 30 s. 75%. On the stride too. 55%.
9. **Food**: every open-loop cycle gains about nothing (within .3 a 10 s of 0: it eats both colours), foraging about +2 a 10 s on
   these bodies (lopsided ones eat little). 70%.
10. **Where across the corridor a block lies** (added before its lives; `lab/dance0.py 200 ... corridor`: every .25 s, the side of the
    nearest block ahead in the brain's own frame, guessed by a linear decoder from the last .5 s of pulses and beats): a zigzag gives at
    least twice foraging's bits a second. 50%. Still gives 0. 90%.

**The observer, mended before scoring** (`lab/v/dance0.log`, the first table, is void for the bits). A ridge decoder scored by squared
error found almost nothing, even on sweeps, where D20 and D43 set the balance to within .05. Traced: the beat-clocked register's period
is exact when right (20.3 against 20.4 beats a revolution) but slips to a half, a third or a far multiple in some lives, and squared
error lets those slips swamp everything; a nearest-neighbour decoder on the registers did worse (600 lives are too few for 256
numbers). Mended: bits as mutual information with the truth, each cut in 12 equal-count bins and corrected for few lives (a slip costs
a little, not everything; capped at 3.6 bits); the better of the ridge decoder and a physical estimator (each motor's beats a revolution
from its register, fundamental chosen by excess summed over all its multiples over their number's square root, 4 to 90 beats: 72% of
motors within 5% after 50 s of spinning). Both are lower bounds; neither knows the physics of a zigzag, straight run or burst.

**Scored 1-9** (`lab/v/dance0_report.log`; 600 bodies a cycle; bits at 100 s, then the median error in log units):
- 1 right: still 0 to .1 bits on all three (.1 is the measure's floor).
- 2 half right: sweeps pin most bodies, median error .04 on the balance and .03 on the stride, but the slips hold the information to
  1.1 bits on each, not 3. Nothing at 30 s (.4 bits, median error .62): 15 s on each motor is too little.
- 3 wrong in its second half: one motor's spin times that thruster over the drag (balance .1 bits, as the sum said), not the stride
  (.5 to .6). The prediction misread its own sum.
- 4 right: drag on its own at most .4 bits, below the .8 that knowing the stride implies. Strength and drag are one number to the eyes.
- 5, 6 wrong: straight and burst give .1 to .2 bits on everything, to these observers.
- 7 wrong: foraging gives .5 bits on the balance (median error .27), .5 on the stride.
- 8 wrong: at 30 s no cycle beats foraging by 2 bits (sweeps .4, zigzags .5 to .6, foraging .3). By 100 s sweeps are far more precise
  than foraging (.04 against .27) but the information differs by .6 bits, the slips again.
- 9 half right: spins, sweeps, straight and burst gain within .2 a 10 s of 0; zigzags lose .4 to .7 (they meet blocks at random and
  poison costs double); foraging +.61, not +2 (these bodies are lopsided and dragging at once).
- 10 wrong in its first half, right in its second (`lab/v/dance0_corridor.log`, 200 lives a cycle): no arm tells the side of the nearest
  block from the last half-second, zigzags included (0 to .03 bits a look, at most .02 a second; foraging .01; still .00). A linear
  decoder only, but D21 and D41 met the same wall: a block crossing the corridor gives one to five pulses.

# D1, step 1: does a rhythm unit's own judgement rank units as the ruler does? Predictions (main session, 2026-11-10), before the lives

`lab/play1.py 40 300`: 40 rhythm units drawn at random (period .2 to 20 s, duty, rate 5 to 50 a second, random weights onto each motor in
each part), plus D0's spin, sweeps, straight and 2 s zigzag; each alone, open loop, on 300 bodies (thrusters and drag drawn), 100 s,
seeds 88000+. Self-score: bits a second the unit's own beats make the eyes predictable (its beat-clocked register; plain, and beyond the
last beat). Ruler: bits about the balance, its size, and the stride, by a decoder that knows no physics (D0's features plus each motor's
recurrence period), mutual information in 8 bins.

**Found while smoking, before the lives:** D0's "straight runs tell nothing" was its observer's fault. A lopsided body driven straight
circles, and the recurrence period of its view tracks 1 / |k0 - k1| (76% of bodies within 10%, where the period fits in 127 beats).
So the ruler is now physics-free, and scores the imbalance's size as well as its sign.

11. The plain self-score and the beyond-the-last-beat one rank the units alike (rank correlation above .8). 70%.
12. The self-score's rank correlation with the ruler (balance or its size, plus stride) is above .5. 50%. Above .3, 70%.
13. Units that drive neither motor, or very slowly, score lowest on both. 85%.
14. Among the ruler's top 5, at least 2 are in the self-score's top 5. 55%.

# D0 confirmed on fresh seeds (forking paths). Predictions before the lives
`lab/dance0_confirm.py 600`: the mended observer, frozen as committed, on seeds 89000+. The analysis was changed after seeing D0's first
results, so D0's numbers are exploratory until this agrees.
15. Sweeps' median error at 100 s within .03 of D0's (.04 balance, .03 stride), and foraging's above .2. 80%.
16. Every arm's bits at 100 s within .3 of D0's. 75%.

**Scored 11-14** (`lab/v/play1.log`):
- 11 wrong, narrowly: the two self-scores rank alike at .73, not above .8 (the "beyond the last beat" score marks down mixed-motor units).
- 12 wrong: rank correlation with the ruler -.02 (plain) and -.22 (beyond the last beat). The self-judge, as defined, does not find
  informative movement.
- 13 right: the units that drive no motor score 0 on both.
- 14 wrong: none of the ruler's top 5 is in either self-score's top 5.
What it ranks top: one motor alone, steady or nearly (u10, u15, spin0, u0: .8 to .9 bits a second), which the ruler says tell the
stride a little and the balance nothing (one thruster's strength alone). What the ruler ranks top: units that switch between the motors
within a second or two (u14, u17, u8, u29: .7 to .9 bits on the balance), and sweeps for the stride (.95). They score low on the
self-judge, since switching makes each motor's register less regular.

**Scored 15-16** (`lab/v/dance0_confirm.log`, seeds 89000+): both right. Sweeps' median error .05 and .04 at 100 s (D0: .04, .03),
foraging .23 (above .2), every arm's bits within .3 of D0's. D0's mended observer holds on fresh seeds.

# Play first, the challenge later: step A, what learning progress chooses. Predictions (main session, 2026-11-10), before the lives
`lab/play2.py 20`: play1's 40 units as a bank; turns of 3 s to the unit whose predictions improve fastest (bits a second of play, its
latest turn against the one before), each tried twice first; play ends when no unit improves beyond twice its noise; then the starting
brain forages. 900 s lives, thrusters and drag drawn, seeds 90000+, 20 pairs; against the starting brain foraging all life. Analysis
fixed now: the last third's efficiency, paired; when play ends; play time beyond each unit's first two turns, against the unit's ruler
(play1.log), rank correlation; ruler bits a second as played against all units alike. Smoke (3 lives): play ends at 276 to 288 s, most
units getting two to four turns.
17. Play ends by itself in every life, between 200 and 400 s. 85%.
18. Play time beyond the first turns ranks with the ruler, above .3. 30% (D45: what one unit predicts isn't what tells the body).
19. The last third ties the starting brain (no knob is set, so play can't pay yet): the paired difference's interval includes 0. 80%.

**Scored 17-19** (`lab/v/play2.log`, 20 pairs):
- 17 right: play ended by itself in every life, median 275 s (quartiles 258, 289).
- 18 right in letter only: rank correlation .33, but play was spread almost evenly (the most played unit 9 s, against 7 s for most), so
  ruler bits a second as played .81 against .80 for all units alike. Learning progress, measured turn on turn, is mostly noise: each unit
  gets two or three turns, then none improves beyond its noise. It samples everything briefly; it doesn't concentrate.
- 19 right: the last third .41 [.09, .77] against the starting brain's .33 [.01, .70]; no knob is set, so play can't pay yet.

# Play first, then the knob: three links. Predictions (main session, night of 2026-11-10, the user asleep), before the lives
`lab/play3.py 20`: play2's play on lopsided bodies (thrusters drawn), then the starting brain forages with its balance knob set by a
link; 900 s, last third, 20 pairs, seeds 91000+. Arms: forage (no play), told, play (knob untouched), steady (a forward model of how
fast each played mix turns the view, from sightings a second; the drive's knob where it predicts no turning), partners (each motor's
effect from the mixes that beat it alone; made equal), taste (five balances tried 30 s each, twice, the best kept; play proposes
nothing), steadytaste (taste among steady's estimate +- .3); steady:recur and partners:recur (recurrence instead of sightings). Analysis
fixed: last third paired against forage; median |knob error| and share within .2.
Traced before (one life): play spreads over ~70 mixes, 3.7 s each in .65 s stretches, too short for most to show a revolution; a mix
given time had its period right. Sightings a second rank with the true turning rate at .45 to .7 across a life's mixes.
20. Told above forage by at least 1 (D43: 2.46 against .94 at 300 s). 85%.
21. Steady: median knob error under .3, and above forage surely. 45%.
22. Partners: worse than steady (fewer mixes). 70%.
23. Taste: above forage surely (D19, D43: taste is slow but 300 s of trials over five values should find the rough balance). 55%.
24. Steadytaste at least as good as steady. 60%.
25. The recur versions mostly find no estimate (too few mixes count). 75%.

**Scored 20-25** (`lab/v/play3.log`, 20 pairs): 20 right (told +1.69 over forage). 21 wrong: steady's knob error is .26 (40% within .2),
but it gains nothing (+.01 [-.57, +.62]): the score is steep in the balance. 22 right: partners worse (.56). 23 right, strongly: taste
alone, five balances 30 s each twice, +1.06 [+.61, +1.53], knob within .2 in 75% of lives; it uses nothing from play. 24 right in
letter (steadytaste +.89, well above steady) but below taste alone. 25 right: recurrence counts in one mix a life at most.
So play as built pays nothing; taste's plain trial over a coarse grid, in 300 s, recovers 60% of the gap.

# Play pays later? The user's frame. Predictions (main session, night of 2026-11-10), before the lives
`lab/play4.py 20`: lopsided bodies; every meal worth nothing until a moment drawn per life (400 to 600 s), then food and poison; gain a
10 s in the first 100 s from that moment and the 200 s after, paired against forage. Arms: forage, told, play (knob untouched),
steady, taste (trials from the first taste), steadytaste. Smoke (one life): told 4.2 at once, forage -1.2.
Also found, before: play3's concentrated play (4 or 10 units, 10 s turns) still lets almost no mix show a recurrence.
26. Told above forage in both windows, surely. 90%.
27. Taste surely above forage in 100-300 s, not in 0-100 s (its trials are under way). 60%.
28. Steady ties forage in both (its knob error .26 bought nothing in play3). 65%.
29. Steadytaste above taste in 0-100 s (three trials near play's estimate, against five over the whole range). 40%.

**Scored 26-29** (`lab/v/play4.log`, 20 pairs): 26 right (told +2.87, +3.01). 27 wrong, usefully: taste is below forage in both
windows (-.51, -1.04 surely): its ten trials of 30 s run through the whole scored 300 s, so it pays for searching while the challenge is
on, though its final knob is good (93% within .2). 28 wrong, the good way: steady pays, +.76 [-.01, +1.61] at once and +.79 [+.02,
+1.63] after, knob error .17 (55% within .2). 29 right: steadytaste .88 against taste's .32 at once.
**Confirmation** (forking paths: this test was designed tonight): `lab/play4.py 30 ... s93000`, the analysis frozen, fresh seeds.
30. Steady above forage in 100-300 s, surely, on fresh seeds. 60%. Above forage in 0-100 s, surely. 40%.
31. Taste below forage in 100-300 s. 75%.
**Scored 30-31** (`lab/v/play4_confirm.log`, seeds 93000+, 30 pairs): 30 wrong: steady +.54 [-.28, +1.35] at once and +.39 [-.51,
+1.30] after, knob error .29 (33% within .2): positive both times, sure neither. 31 right: taste -.82 [-1.45, -.23]. Steadytaste
+.86 [+.08, +1.66] in 100-300 s, surely, on both seed sets in direction. So play's head start is real in sign and rough in size; the
estimate is the limit.

**Practice, traced and dropped** (smoke, 3 lives): letting the steady model learn after play from the forager's scans and runs drove
the knob away from the truth (+.4 to +.7 off). Traced: a scan ends when something comes into view, so windows that stay scans saw
little (.9 to 1.5 sightings a second against 1.2 to 4 for the same motor in play): selection by the brain's own behaviour; and the
forager hardly runs the other motor alone. Closed-loop behaviour is biased evidence for an open-loop model.
**Play whenever nothing better is on** (`untaste`): forage by default; another round of play whenever 30 s pass with no taste at all;
the first taste ends play; the knob refitted after each round. (First version, play until a taste, trapped a creature spinning on a
unit that never eats.)
32. With 400 to 600 s of play instead of ~280, steady's knob error is no smaller (the sightings statistic, not the evidence, limits
    it). 60%.
**Scored 32** (`lab/v/play4_untaste.log`): right, and more: with play through the whole quiet spell steady's knob error grew (.27, 35%
within .2, against .17, 55%) and its gain went (+.00, +.04). The sightings model is biased, so more of its evidence doesn't help.

**A statistic for short stretches** (traced offline, 4 lives): one over a sighting's median length ranks with a mix's true turning rate
at .45 to .58 in every life; sightings a second at -.03 to .69.
33. `steady:burst` has a smaller knob error than steady (sightings) on the same seeds (play4, 20 pairs). 45%. And surely above forage
    in 100-300 s. 40%.
**Scored 33** (`lab/v/play4_burst.log`): wrong. One over a sighting's length is worse (knob error .46, 20% within .2).

**Partners, each motor's own record** (`partners:beats`): for each motor, every run of beats in which it alone beat (any unit's), as
D43's record clocked by its own beats, pooled over runs; each motor's beats a revolution; the knob makes their effects equal. Smoke,
four lives: estimates .72, .16, -.03, .31 against true .64, .18, -.04, .36. (With 10 s turns play never ended: dropped.)
34. `partners:beats` median knob error under .1. 70%. Surely above forage in both windows. 75%. Within .5 of told in 100-300 s. 55%.
**Scored 34** (`lab/v/play4_beats.log`, 20 pairs): median error .10 (65% within .2): just short of "under .1". Surely above forage in both
windows: right, +1.55 [+.51, +2.62] at once and +1.23 [+.24, +2.30] after. Within .5 of told: wrong (told +2.87, +3.01).
**Confirmation** on fresh seeds (93000+, 30 pairs), the analysis frozen:
35. partners:beats surely above forage in 0-100 s and in 100-300 s. 65%.
**Scored 35** (`lab/v/play4_beats_confirm.log`, seeds 93000+, 30 pairs): right. +1.51 [+.59, +2.43] at once, +1.15 [+.23, +2.00] after,
knob median .07 but 53% within .2. Traced: 19 of 30 bodies within .1; about 6 off by a doubled or halved period in one motor (±.69),
a few by a factor 3 or 4 (1.2 to 1.5). The residual is D20's slips.
**Taste picks among play's hypotheses** (`partnersalt:beats`): each motor's best period and its best rival (the comb's runner-up not
within a quarter of it); three candidate balances; taste tries each 30 s from the first taste and keeps the best.
36. partnersalt more often within .2 than partners (above 75% against ~55-65%). 60%. Below partners in 0-100 s (its trials), above it in
    100-300 s. 55%.
**Scored 36** (`lab/v/play4_alt.log`): half right. Within .2 in 72% (not above 75%), median .06; below partners at once (-.14) and above
after (+1.97 against +1.23): its search costs the first 100 s and pays the next 200, about even over the 300.
37. On fresh seeds (93000+, 30 pairs, frozen): partnersalt surely above forage in 100-300 s, and above partners there. 60%.
**Scored 37** (`lab/v/play4_alt_confirm.log`): right. partnersalt +1.60 [+.76, +2.42] in 100-300 s (partners +1.15), 70% within .2;
at once -.02 (its search).

# Boredom: bored when the estimate stops moving? Predictions (main session, 2026-11-11), before the lives
The user: we've met boredom, playing until you stop learning. Learning progress (prediction improving turn on turn) ended play well but
couldn't steer it (D46). Two rules on the partners record (play4's frame, 20 pairs, seeds 92000+): `stall` (units in a shuffled cycle;
play over when the knob's estimate, re-read after each turn that added a single-motor run, has its last five within .05) and `mover`
(the same end; each turn to the unit whose last fed turn moved the estimate most). A taste ends play in both. First version counted
every turn, so turns that added nothing looked like a stall and play ended at 39 to 75 s: only evidence counts.
Smoke (3 lives): mover plays 126 to 147 s, two of three knobs right; one stalls on a wrong value (-.86 against -.04).
38. Mover plays surely less long than learning progress (median under 200 s against ~280). 80%.
39. Mover's knob error no worse than learning progress's (median within .03), and its gain in 0-100 s within .5 of it. 50%.
40. Stall (no steering) worse than mover in knob error. 60%.
**Scored 38-40** (`lab/v/play4_bore.log`): 38 right: mover plays a median 135 s (quartiles 129, 144) against learning progress's 285;
stall 207. 39 wrong: mover's knob error .26 (45% within .2) against .10 (65%), and its gain +.82 [-.36, +2.05] at once against +1.55,
not sure. 40 right: stall worse still (.32, 35%). An estimate that has stopped moving isn't one that is right: the comb's best period is
sticky, so a slip, once on top, survives five more turns of evidence.

# Boredom from certainty. Predictions (main session, 2026-11-11), before the lives
Each motor's record gives play's best period, its strongest rival (another peak of the comb, not within a quarter) and the margin
between them (in chance's spread). Bored when both margins reach 3 (SURE), or a taste ends play; a motor still in doubt hands its rival
to taste (30 s a candidate, from the first taste). `certain`: units in a shuffled cycle; `certainmover`: each turn to the unit whose last
fed turn raised the certainty most, ties to the least recently played. Traced first: rivals on the best's own shoulder gave margins of
.1 to .4 always (now separate peaks); certainmover trapped on one unit that never eats (now ties go to the least recent). Smoke (8
lives): every knob within .05; certainmover certain and done by itself in 3 of 4, at 288 to 513 s.
41. Both certainty arms more often within .2 than learning progress's partners (65%): above 80%. 60%.
42. certainmover surely above forage in 100-300 s, and above partners (+1.23) there. 55%. In 0-100 s, at least as good as partnersalt
    (-.14). 65%.
**Scored 41-42** (`lab/v/play4_certain.log`, 20 pairs): 41 right: both certainty arms 90% within .2 (median .02 and .01), against 65%.
42 right: certainmover +1.14 [+.26, +1.92] at once and +2.05 [+1.27, +2.84] after, surely, above partners (+1.23) and partnersalt
(-.18) at once; told +2.87, +3.01. certain (no steering) never became certain before the challenge (its doubts went to taste: -.28 at
once, +1.78 after); certainmover did in 20% of lives, and otherwise played until food came (median 502 s). Exploratory: designed on
these seeds; to confirm on fresh ones.
**Confirmation** (`lab/play4.py 30 ... s93000`, frozen):
43. certainmover surely above forage in both windows on fresh seeds, and 80% or more within .2. 65%.
**Scored 43** (`lab/v/play4_certain_confirm.log`, seeds 93000+, 30 pairs): mostly right. 90% within .2 (median .01); +2.24 [+1.40,
+3.06] after, surely (told +2.98: three quarters of the gap); at once +.74 [-.18, +1.68], not sure (taste's last search falls there).

# P1: explain the play result (the review of 2026-11-11). Predictions (main session, 2026-11-11), before the lives
`lab/p1.py 30 s94000` (fresh seeds, the design frozen in its docstring): four arms with 400 s of play each (no other end), the same
estimator and hand-over to taste; play4's world. Measured: gain from onset against forage; knob error after taste; each motor's best
guess at play's end within 10%; calibration (motors that say sure, margin >= 3: how many wrong by >10%, how many by a doubled or halved
period); play's motor beats.
44. With play time equal, certainty-directed play is not surely better than uniform play on knob error or gain (D48's edge was mostly
    longer play and taste's choice). 65%.
45. Learning progress with 400 s of play does at least as well as it did with ~285 s (knob within .2 above 65%). 60%.
46. Of motors that say sure, at least 15% are wrong by more than 10%: the margin is not calibrated. 55%.
47. Every play arm surely above forage in 100-300 s. 80%.
**Scored 44-47** (`lab/v/p1.log`, seeds 94000+, 30 pairs). 44 wrong, the good way: at equal play time and similar motor beats (4529,
4942, 4652), certainty-directed play surely beats uniform play: gain +.94 [+.35, +1.57] at once and +.74 [+.21, +1.30] after, and
motors within 10% +18 points [+8, +28] (93% against 75%). Against learning progress it is ahead but not surely (+.41 [-.16, +1.01], +.43
[-.06, +.93]; +5 points [-5, +15]). 45 right: learning progress with 400 s, knob within .2 in 92%. 46 wrong: of motors that say sure, none
was wrong (0%), but few say sure (3% uniform, 12% lp, 28% certain): the margin is conservative, not overconfident. 47 right: every play
arm surely above forage in 100-300 s (+1.43, +1.74, +2.17).

# P2, route A: taste discovers how to use play's records. Predictions (main session, 2026-11-11), before the lives
The user: try all three routes (taste picks the readout; evolution learns it; play that feeds a mix model), then abstract. Route A:
after play (learning progress, D46), each motor's best period from its own record (D47); nine readouts, every signed combination of
the two measures (ours, the first minus the second, among them); taste tries each 20 s from the first taste and keeps the best. The
discovery costs log2 9 = 3.2 bits of choice, paid in food. Smoke: two lives, both picked ours. play4's frame, 20 pairs, seeds 92000+.
48. readout's knob within .2 in at least 60% of lives (ours, partners, 65%). 60%.
49. readout below partners in 0-100 s (its trials), and in 100-300 s within .5 of partners. 55%.
50. readout above taste alone (five knobs, 30 s twice) in 100-300 s. 60%.
**Scored 48-50** (`lab/v/p2a.log`): 48 wrong: readout's knob within .2 in 48% (median error .60). 49 half right: below partners at once
(-1.01 [-1.67, -.37] against forage, surely worse than no play), but far below partners after (-.11 against +1.23). 50 right in letter:
above taste alone after (-.11 against -1.04), both paying for their search. Nine readouts at 20 s each is too little food to tell them
apart: discovering the link in life by taste costs more than it wins within 300 s.

# P2, route B: evolution learns the readout. Predictions (main session, 2026-11-11), before the lives
`lab/p2b.py train 20`: training bodies 92000+; features from learning-progress play; each body's food from onset at 17 knobs; the
readout w0 b0 + w1 b1 + c searched on a grid, judged only by food.
51. The search finds a readout within .3 of ours in each weight (+1, -1, 0). 70%.
52. Its training food within 10% of our formula's. 75%.
**Scored 51-52** (`lab/v/p2b_train.log`, 40 training lives): the search's readout is +1.00 b0 - .70 b1 - .80: the same shape as ours (a
difference of the two motors' measures), w1 within .3, but an offset of -.8 (51 wrong in c). Training food 68.4 against our formula's 58.0
and each life's best knob 105.8 (52 wrong: 18% above ours, likely fitting the training lives' slips).
53. On fresh seeds (95000+, 30 pairs, real play, the readout frozen), the evolved readout is not surely better than ours in 100-300 s,
    and not surely worse. 60%.
**Scored 53** (`lab/v/p2b_test.log`, fresh seeds 95000+, 30 pairs): wrong. The evolved readout is surely above forage (+1.40 [+.71,
+2.12], +1.33 [+.65, +2.03]) but surely below our formula (-.65 [-1.11, -.17], -.87 [-1.29, -.46]); knob .18 (53% within .2) against
ours .02 (67%). The shape transferred; the offset fitted the 40 training lives.
54. Retrained on 60 bodies (seeds 92000-92059; first void run aside, no other change), the offset shrinks below .4 in size. 55%.
**Scored 54** (`lab/v/p2b_train60.log`, 120 training lives): wrong. The same readout (+1.00, -.70, -.80), training food 52.1 against
our formula's 50.2: the offset is stable, not noise. But on fresh lives with real play it was surely worse than ours (53). Evolution's
fitness (a forager set to the knob from birth, then the challenge) scores our formula at about 1.7 a 10 s, real lives at 2.5 to 2.8: the
proxy disagrees with real use, and evolution found what the proxy rewards. Not chased further.

# P2, route C: play that feeds a model of mixed commands. Predictions (main session, 2026-11-11), before the lives
`lab/p2c.py 20` (seeds 92000+): the slow bank (periods 8 to 60 s, 20 s turns, 400 s of play in a shuffled cycle); each mix's own
record gives its turning a beat; the drive's knob at the minimum of turning against knob (a V fitted, generic minimisation; the
steady-view goal inherited); taste picks among the minimum and +- .3. Traced first: mixed records give the right period (29.2 against
29.4 beats) with small margins; a first rule keyed on margins threw them away. Arms: forage; partners (our formula, on the same slow
play); steady. Smoke (3 lives): two within .2, one off by 2.
55. steady's knob within .2 in at least 50% of lives. 50%. Surely above forage in 100-300 s. 55%.
56. partners on slow play at least as accurate as on the fast bank (within .2 in 65% or more). 65%.
**Scored 55-56** (`lab/v/p2c.log`, 20 pairs): 55 wrong: steady's knob within .2 in 32% (median .81); -.34, +.22 against forage, not
sure. Mixed records are often right but ten noisy points don't pin the minimum, and the true turning against knob is not a symmetric V.
56 right, strongly: partners on the slow bank, 85% within .2 (median .01), +2.43 [+1.33, +3.42] and +2.32 [+1.16, +3.36]: slow rhythms
give long single-motor runs.

# Understanding as coupling (the user's principle, 2026-11-11): does coupling peak at the right knob? Predictions, before the lives
`lab/couple.py 20`: the starting brain with its balance knob fixed at 17 settings; play4's quiet spell (no taste at all), 50 to 400 s;
I(A_t; S_t+1) + I(S_t; A_t+1) at the interface in 50 ms bins (4 states each), bits a second. 20 lopsided bodies, 10 plain. Smoke (one
body, right knob -1.13): 4.7 bits a second at -1.0, 2.3 at 0, 1.3 at +1.2.
57. On lopsided bodies, the knob of most coupling is within .4 of the right one in at least 70% of bodies. 60%.
58. On plain bodies, it is within .4 of 0 in at least 70%. 65%.
59. The policy term (senses to actions) carries most of it. 70%.
**Scored 57-59** (`lab/v/couple.log`, seeds 97000+): all right, more strongly than predicted. Lopsided bodies: the knob of most coupling
within .2 of the right one in 95%, within .4 in 100%, median error .07, correlation +1.00 across 20 bodies. Plain bodies: at 0 in all
10. The peak is sharp (+1.94 bits a second above a body's mean at the right knob, +.76 and +.42 at .4 either side). Policy (senses to
actions) 3.3 bits a second, forward .2.
**How fast coupling tells settings apart** (the same lives re-run keeping each life's bins, windows from 50 s):
60. In 30 s of foraging the right knob beats one .4 off in at least 80% of comparisons. 55%. The best of 17 settings is within .2 of
    right in at least half of bodies by 60 s. 50%.
**Scored 60** (`lab/v/couple_speed.log`): right. The right knob beats one .4 off in 75% of comparisons at 10 s, 88% at 30 s, 98% at 60 s;
the best of 17 settings within .2 of right in 60%, 80%, 95% of bodies at 10, 30, 60 s. (The rerun's totals: `couple_rerun.log`.)

# Coupling as a mechanism: the knob searched by the brain's own coupling. Predictions (main session, 2026-11-11), before the lives
`lab/couple_search.py 20` (fresh seeds 98000+): the starting brain forages from birth; a 4 x 4 counter at its interface; a golden-
section search over the knob, each setting judged by 30 s of coupling, done when the bracket is under .3 (about 180 s, before the
earliest onset). Arms: forage, told, partners (play + our formula), couple; plain bodies: forage, couple. Scored from onset (play4).
Smoke (4 lives): done at 180 s, knob errors .27, .12, .06; plain -.06.
61. couple's knob within .2 in at least 70% of lopsided bodies. 60%.
62. couple surely above forage in both windows, and not surely below partners. 60%.
63. On plain bodies couple ties forage (no sure cost). 75%.
**Scored 61-63** (`lab/v/couple_search.log`, 20 pairs): 61 right: couple's knob within .2 in 80% (median .09), done at 180 s, before
onset in every life. 62 right: surely above forage (+1.55 [+.74, +2.40], +1.71 [+.87, +2.52]); partners +2.13, +1.91. 63 wrong: on plain
bodies couple is surely below forage (-1.38, -1.45) though its knob ends .06 from 0. Traced: not an artefact of the drive's two
oscillators (a paired drive doesn't help: plain body at knob .1, 2.49 unpaired, 2.26 paired, against 4.2 at 0); the score is that
steep in the knob (.03 costs .9, .1 costs 1.7, .3 costs 3.3), and foraging's default 0 is exactly right on a plain body by construction.
The search must be more precise.
64. couple:fine (bracket to .1, 60 s judgements once under .5; exploratory, same seeds) halves plain's cost and is within .5 of partners
    on lopsided bodies in both windows. 50%.
**Scored 64** (`lab/v/couple_search_fine.log`): half right. On lopsided bodies couple:fine ties partners (+2.14, +1.96 against +2.13,
+1.91; 80% within .2): the formula-free search matches our formula. On plain bodies the cost stays (-1.22, -1.40; error .08): longer
judgements didn't buy precision.
65. couple:fit (the parabola's top through all judgements near the bracket) brings the median knob error below .05 on both bodies.
    40%. Plain cost under -.7. 40%.
**Scored 65** (`lab/v/couple_search_fit.log`): wrong. couple:fit median error .09 lopsided, .05 plain; plain cost -1.12, -1.47.
Traced why plain is unforgiving: each beat is a kick of about 18 degrees; at equal rates every beat pairs with the other motor's and
the kicks cancel; at a 3% difference an unpaired kick comes every 30 or so beats and loses the block. So equal rates is a knife-edge
sweet spot, which foraging sits on by construction and no continuous search lands on exactly.
66. couple:occam (the default, no adjustment, kept unless the answer's coupling is 10% higher, 60 s each) removes most of the plain
    cost (better than -.5 in both windows) and costs under .3 on lopsided bodies against couple:fit. 50%.
**Scored 66** (`lab/v/couple_search_occam.log`): half right. Plain: -.56 at once, -.14 [-.82, +.47] after (tied), knob exactly 0 in 95%.
But the search and check take a median 510 s, done before onset in only 30 to 40% of lives, and on lopsided bodies it falls to +1.32,
+1.32 (couple:fit +1.92, +1.86; knob .13, 70%). The Occam check buys the plain body back at the price of time.
**Confirmation on fresh seeds** (99000+, 20 pairs, frozen): forage, told, partners, couple:fine, couple:occam.
67. couple:fine ties partners on lopsided bodies (difference's interval includes 0) in both windows. 60%.
68. couple:occam ties forage on plain bodies in 100-300 s. 60%.
**Scored 67-68** (`lab/v/couple_search_confirm.log`, fresh seeds 99000+, 20 pairs): 67 right: couple:fine ties partners (+.60 [-.60,
+1.80], +.58 [-.74, +1.82]). 68 right: couple:occam ties forage on plain bodies (+.04, -.04; knob exactly 0 in 100%). And more:
couple:occam is surely above partners in 100-300 s (+1.01 [+.23, +1.85]; +.52 [-.28, +1.44] at once), 82% within .2, 72% of told's
gap there (-.81 [-1.19, -.41] against told).

# Is precise timing of the kicks worth learning? (the user, 2026-11-11). Predictions (main session), before the lives
`lab/kick_timing.py 20` (seeds 98000+; play4's frame): the told brain two ways: the rate knob (each motor its own rate) against equal
rates with a scheduler that, at each pair of beats, fires both or drops one, whichever leaves the heading's accumulated turn nearest
straight (error diffusion). Two bugs traced in the smoke (the scheduler only ever dropped one motor; an empty tick reset its account).
69. The scheduler is not surely better than the rate knob on lopsided bodies: the kick's size, not its timing, is the limit. 55%.
**Scored 69** (`lab/v/kick_timing.log`): right. The scheduler is slightly worse than the rate knob (-.35 [-.74, +.03], -.54 [-.83, -.22]);
and the told rate knob on lopsided bodies (+3.85, +4.11) already equals foraging on a plain body (+3.98, +4.16): no headroom for timing.

# Taking turns: Sepulchre's half-centre as two motor units searching in turn (the user, 2026-11-12). Predictions, before the lives
`lab/couple_local.py 20 forage couple:occam local:turns local:turnsj local:half local:halfj` (dev seeds 98000+; play4's frame). Each
motor unit has its own gain; a unit's search (golden section on its own gain, 20 s a point, an Occam check at the end) is its turn;
while it searches the other holds (inhibition); at the end it is bored (fatigue) and, if it moved, the other rebounds. Judged either by
the unit's own coupling (half, turns) or by the joint coupling of the eyes with both units' beats, which each unit sees from its
neighbour (halfj, turnsj). turns/turnsj: both units searching at once, from random starts (no turn-taking). Smoke (5 lives): halfj
within .2 in 4 of 5 lopsided bodies and exact on plain; half (own signal) mostly stuck at 0: a unit's own coupling rises with its own
rate whatever the balance (traced: unit 1 favoured +.79 where -.64 was right).
70. halfj within .2 of right in at least 70% of lopsided bodies, and ties couple:occam (the global search) in 100-300 s. 55%.
71. turnsj (the same joint signal, both at once) surely worse than halfj in 100-300 s: taking turns is what makes the local version work. 60%.
72. half and turns (own signals) fail, whatever the timing. 75%.
**Scored 70-72** (`lab/v/half_centre.log`, `half_centre_merged.log`; turnsj first run void: an edit routed it to the half-centre with own
signals, fixed and rerun on the same lives): 70 right: halfj within .2 in 80% (median .11), +1.74 [+.91, +2.57] and +1.50 [+.75, +2.26],
ahead of the global search (+.42, +.18, not surely), done at 400 s, before onset in every life; plain bodies left exactly alone (100%).
71 right: both units at once by the same joint signal (turnsj) +.54, +.33, 40% within .2, wrecking plain bodies (-3.1); halfj surely
above it (+1.20 [+.33, +2.13], +1.18 [+.29, +2.11]). Taking turns is what makes the local search work. 72 right: by their own signals,
in turns or at once, the units fail (0% and 20% within .2).
73. Confirmation on fresh seeds (99000+, 20 pairs): halfj surely above forage in both windows, and surely above turnsj in 100-300 s. 70%.
**Scored 73** (`lab/v/half_centre_confirm.log`, fresh seeds 99000+, 20 pairs): right. halfj +2.01 [+1.21, +2.82], +1.71 [+.99, +2.45],
90% within .2 (median .07), done at 400 s before onset in every life; surely above turnsj (+1.76 [+.89, +2.63], +1.34 [+.65, +2.02]);
tied with the global search (+.48, -.34); plain bodies alone (-.13, -.24, exact 0 in 100%).

# Two dimensions: the balance and the tempo, by turn-taking units (`lab/couple_local.py 20 forage told couple:occam local:halfj both`)
Thrusters and drag drawn (a half to twice each), play4's quiet spell; told: the balance and the tempo (bodyladder's toldbody). Each unit's
gain is its own rate, so two units set the balance (their difference) and the tempo (their sum); nothing in them knows of drag.
74. halfj's balance within .2 in at least 60% of bodies (drag makes the coupling landscape harder). 55%.
75. halfj's tempo tracks the drag (correlation of the units' mean log rate with log drag above +.3). 35%: the bracket of a unit's later
    turns (+-.5) and the Occam check bias it to stay near 1, and coupling may not care much about speed.
**Scored 74-75** (`lab/v/half_centre_both.log`, 20 pairs): 74 right: halfj's balance within .2 in 75%, +1.54 [+.65, +2.36], +1.72 [+.96,
+2.47], tied with the global search (+1.43, +1.66); told +3.78, +3.54. 75 as doubted: the units' tempo hardly tracks the drag
(correlation +.21, 25% within .2 of the told tempo): the gap to told is the tempo.
76. (`lab/couple_tempo.py 12`) Coupling peaks at the right tempo (log drag) with no reward: correlation of the tempo of most coupling
    with log drag above +.5. 45%. And food peaks there (it must, by the told arm). 80%.
**Scored 76** (`lab/v/couple_tempo.log`): half right. Coupling's tempo correlates +.52 with log drag but sits about .7 below it (peak at
-.8: half the right speed); food peaks at the right tempo or a little above (correlation +.90). Likely the binned yes-or-no measure
(slower beating makes beat-or-not more variable).
77. Coupling from beat counts (0 to 3 a bin) instead of yes-or-no peaks within .3 of the right tempo (median). 40%.
**Scored 77** (`lab/v/couple_tempo2.log`): wrong. Coupling from beat counts sits as far below the right tempo (median error .66, peak at
-.8) as from yes-or-no: not an artefact. Coupling and food genuinely disagree about tempo: a slower creature's seeing and doing go
together more tightly, a faster one eats more. Tempo trades speed against control, and coupling values only control.
