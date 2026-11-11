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
