# A brain that takes up new parts (PROGRAMME.md, Next; the user, 2026-11-12). Predictions and scores

The body: the original thrusters, and two more a side at a half and a quarter of their strength, on motor lines 2 to 5 wired at random,
alive from a moment drawn each life, each firing costing in proportion to its strength (sim.WLife.extra; EXTRA=1 in a worker; with the
switch off every life is identical: the fingerprint check, 288 of 288).

## G1, the yardstick (`lab/newparts.py yardstick 10`; seeds 102000+; parts from birth; told the wiring; 300 s, last third)
N1. No design is surely better than the base on a plain body (the starting brain already forages near its best with the big kicks). 55%.
N2. On lopsided bodies (told their balance) no design is surely better either: told already reaches the plain level (D53). 55%.
If both hold, the new thrusters add nothing to learn in these worlds, and G1 must look elsewhere (touching pairs, or a body the big kick
can't serve: a stronger kick, or drag).
**Scored N1-N2** (`lab/v/newparts_yardstick.log`, 10 pairs): both wrong, mildly. Plain: drive on the half or quarter thrusters +.31
[+.03, +.59], +.30 [+.02, +.56] above the base's 2.18; lopsided (told its balance): scan on the quarter thruster +.38 [+.12, +.66], fine
+.35 [+.03, +.65] above 2.09. Finer control buys about 15%: real, below a rung's bar (a gap surely above .25).
N3. Touching pairs (2 mm), where precision should matter more: some design surely at least .4 above the base. 40%.
**Scored N3** (`lab/v/newparts_yardstick_pairs.log`): wrong. Touching pairs: no design helps (best +.11 [-.15, +.36]). The new thrusters
are worth at most about 15% in any world tried: the creature is limited mostly by what its eyes can tell it (D21, D41), not by its kick.

## G1 again: the split eye and the small thrusters together (the user's choice, 2026-11-12)
The split eye in the engine (sim.WLife.split, SPLIT=1): each eye pulse's half of the corridor (by each half's share of that colour's
light, from its own stream) arrives on line 2 or 3, wired at random, alive from a moment drawn each life, delivered only to a brain with
inputs for it (split_lines); off, every life identical (288 of 288). Designs told the map: D24's reflex (while driving, 1 or more food
pulses from one half in .2 s and at most 1 from the other: turn towards it) with the big thruster (a pair's beat on the turning side, its
partner 10 ms later), or one half or quarter kick on that side; and with driving on the halves. Smoke (one life): food 67 base, 84 big,
86 quarter.
N4. On a plain body the split eye with a small kick (splitQ or splitH) is surely at least .4 above the base (D24: +.5 to +.65). 60%.
N5. Steering with a small kick beats steering with the big thruster's timing trick. 50%.
N6. In touching pairs the split eye helps surely (it says which side the poison is on). 50%.
**Scored N4-N6** (`lab/v/newparts_yardstick2.log`, 10 pairs): all right. Plain: splitQ +.94 [+.69, +1.22], splitQ+driveH +.96 [+.79,
+1.14] above the base's 2.18 (splitBig +.69, splitH +.65). Lopsided: splitQ +.72 [+.51, +.92] (big +.60). Touching pairs: splitQ+driveH
+1.07 [+.76, +1.39] above 1.42 (big +.53). The new sense is worth about +.6 with the old kick and up to +1.0 with a small kick to act on
it; the small thrusters alone +.31, +.02, +.04. Sense and fine actuator together: certified gaps for in-life uptake to find.

## G2, uptake in life (`lab/uptake.py`): first tries (smokes) and a longer-life run
Raw material: a reflex arc from each new sensor line to each new motor line (2 x 4), born off; an arc on fires one kick of its motor at
each food pulse on its line while driving. Told the right two arcs (toldarcs), one life: 151 against the base's 103: the arc form
suffices. Learn (each arc tried on and off, 15 s each, judged by joint coupling, Occam off): wrong (one right arc, two wrong): one window
each is noise (1.3 to 7.6 bits a second). Alternating on, off, on, off with evidence per arc and certainty: right in sign sometimes, but
40 s a visit gives about two visits per arc in a life: starved (an hour needed by the sum). learn2 (each kick a probe: one of a line's
arcs or none, in turn; outcome the food pulses in the next .3 s): the right arc on line 2 highest in both lives traced, line 3 not; each
outcome's sd about 2.5 against differences of about .4, so about 150 probes per arc are needed and a 900 s life gives about 80.
N7. (`UPTAKE_SECS=3000 lab/uptake.py 5`, 3000 s lives) learn2 picks both right arcs in at least half of lives, and surely beats base. 35%.
**Scored N7** (`lab/v/uptake_3000.log`, 5 pairs, 3000 s): wrong. Base 2.41, told +.69, told arcs +.39; learn -.03 (right arcs never chosen),
learn2 -.28 (its probing costs and it never decides). Food is too poor a teacher for a steering arc, even over 3000 s.

## learn3: play first (the user: an instinct to play with its senses and body first)
Play, still (the base behaviour paused): when something is in view on the new lines, one new motor's kick or none, in turn, then a pause
for its motion to fade; a look-around beat when nothing is in view. Each motor's effect: how it moves activity between the two new
lines. A line's candidates: motors surely moving activity out of its half. learn3: taste then chooses among them; learn3b: the surest
wired at once. Traced in smokes: played while scanning, effects drowned in the scan's own motion (no motor sure with 120 kicks); played
still, sides group correctly and the half thrusters stand out (-3.5, +3.3), and a sure candidate was always the right side.
N8. learn3b wires the right side for both lines in at least 60% of lives, and surely beats base (10 pairs, 900 s). 50%.
N9. learn3 (taste confirming) does no better than learn3b. 60%.
**Scored N8-N9** (`lab/v/uptake_play.log`, 10 pairs, 900 s): N8 half right: learn3b surely above base, +.37 [+.17, +.57] (told arcs +.42,
told reflex +.79), 88% of what the arc form gives told; but the right side for both lines in 40% of lives (others: one line right, or a
half thruster where the told arcs use a quarter). N9 right: taste confirming made it worse (+.14).
N10. Confirmation on fresh seeds (104000+, 10 pairs, frozen): learn3b surely above base. 70%.
**Scored N10** (`lab/v/uptake_play_confirm.log`, fresh seeds 104000+, 10 pairs): wrong. learn3b +.11 [-.12, +.34], not sure; but the told
arcs themselves only +.13 [-.06, +.30] here (+.42 on the development seeds), so the learner still reaches about 85% of its form, right
side on both lines in 50%. The weak link is the arc form (a kick at each food pulse on a line), not the learning: the told split-eye
reflex, which also requires the other half to be quiet, was worth +.79 to +.94.

## Lateral inhibition in the arcs (arms ending I): an arc fires only if its line saw more food pulses than the other in the last .2 s
Smoke (2 lives, told arcs): 125 to 159, 141 to 148.
N11. (dev seeds 103000+, 10 pairs) toldarcsI surely above toldarcs, and learn3bI surely above base by at least .4. 50%.
N12. (fresh seeds 105000+, 10 pairs, frozen) learn3bI surely above base. 60%.
**Scored N11-N12** (`lab/v/uptake_inhib.log`, `uptake_inhib_confirm.log`): N11 wrong in its first half: told arcs with inhibition
below without (-.20 [-.39, -.02]) on the development seeds; learn3bI +.46 [+.30, +.63] above base (not surely .4 or more). N12 right: on
fresh seeds 105000+ learn3bI +.39 [+.22, +.58] surely above base, tied with the told arcs with inhibition (+.39). Right side on both
lines in 35 to 40%; the learner mostly wires half thrusters. The seed sets differ a lot in what these reflexes are worth (told arcs
+.42 on 103000+, +.13 on 104000+), which is why the fresh confirmations mattered.

## Play's candidates chosen by coupling (learn3c, learn3cI; smoke, 3 lives, 1200 s)
Two failures, both informative. Play's sure candidates are only ever the half thrusters (the quarters' effects too small to be sure of in
the time), so the quarters never compete. And joint coupling preferred no steering arc to a right one (4.56 with the half arc against
5.79 with none; 3.07 against 4.36), though such arcs surely raise food (D55): a steering kick makes the drive less steady, so seeing and
doing go together less simply. Coupling values steadiness; steering trades a little of it for food: a decision only the outcome can value
(D54's tempo again), and food was too slow a judge here. Stopped at the smoke; play-then-wire-the-surest (learn3b) stays the learner.

# Vigour: how fast to act, set by recent food (the user: hunger; Niv et al. 2007) (`lab/vigour.py 10`, drag drawn, 900 s)
Smoke (2 lives): judged by recent food the tempo moved up towards the right one (.51 against .27; .15 against .51); by coupling it fell
to -.62 in both, eating half as much.
V1. The food-judged tempo correlates with log drag above +.4 and its efficiency is not surely below told. 50%.
V2. The coupling-judged tempo is surely below fixed in efficiency. 70%.
**Scored V1-V2** (`lab/v/vigour.log`, 10 pairs): both wrong. Food-judged tempo +.15 [-.11, +.39] (not sure), correlation with log drag
+.19, unbiased (-.07); coupling-judged +.19 [+.01, +.35] surely above fixed though biased slow (-.38): efficiency charges energy, and
slowness saves it, so coupling's preference costs less here than D54's food-per-second suggested. Told +.43. Recent food over 40 s
windows is too noisy (net about 16 +-5 a window, the right tempo changing it by a few).

# Hunger sets the tempo, in worlds where food regrows after a delay (the user's world; `lab/vigour.py regrowth 10`)
Food eaten is hidden and reappears only after 60 s or 120 s, so richness varies within a life (smoke: 3 to 9 of 18 food blocks alive at
60 s, often 0 to 2 at 120 s). Hunger: two running averages of good meals (20 s, 200 s; each corrected for the share of its window seen:
a first version started the long average at zero, so the creature always felt rich), tempo e^(log recent/long-run), within [-1, .5].
Control: always at e^-.5 (is it just slowness?). Worlds: regrow60, regrow120, plain. 10 pairs, 900 s, efficiency in the last third.
V3. In regrow120, hunger surely above fixed, and above always-slow. 40%.
V4. In the plain world, hunger ties fixed (no harm). 70%.
**Scored V3-V4** (`lab/v/vigour_regrowth.log`): V3 wrong: in lean worlds simply going slower surely helps (+.21 regrow60, +.24 regrow120),
hunger only +.08, +.05 (not sure). V4 right: plain, hunger -.08, slow -.12 (neither sure). Traced in thought: hunger compared recent food
with the creature's own long-run average, which detects changes but not a world lean all along (it comes to feel normal). Niv's vigour
is about the absolute reward rate against effort.
V5. hungerabs (recent food against a fixed inherited normal, the plain world's food rate, R0 .6 a second) at least as good as slow in the
    lean worlds and not surely below fixed in plain. 55%.
**Scored V5** (`lab/v/vigour_regrowth2.log`): right. hungerabs +.33 [+.23, +.43] in regrow60 and +.36 [+.24, +.49] in regrow120, above
always-slow (+.21, +.24); plain -.10 [-.37, +.13], not sure. In the lean worlds it sits at its slowest bound (e^-1) nearly all life, so
part of its gain is simply being slower than the slow control; in the plain world it runs at a median -.22.
V6. Confirmation on fresh seeds (108000+, 10 pairs, frozen): hungerabs surely above fixed in both lean worlds, and not surely below in
    plain. 70%.
**Scored V6** (`lab/v/vigour_regrowth_confirm.log`, fresh seeds 108000+): wrong. hungerabs surely below fixed in the plain world (-.40
[-.71, -.11]; always-slow -.43); in the lean worlds +.18 (not sure) and +.34 (sure). Its fixed "normal" (.6 meals a second) is too high
for many of these creatures, so they feel hungry, slow, and lose food in a world that is fine. Not tuned on these seeds. A fixed normal
must match the world; a normal learned from one's own past fails in a world lean all along. Open: food per unit of effort (the exchange
rate between a meal and a pulse, which evolution knows) as the yardstick.

# Play in the lean spells (the user's world and idea; `UPTAKE_WORLD=regrow60 lab/uptake.py 10 base learn3bI leanlearn3bI s109000`)
Food regrows 60 s after it is eaten; the new eye and thrusters grow at 100 to 300 s. learn3bI plays at once (D55); leanlearn3bI plays
only while recent food (20 s) is below its long-run (200 s), foraging as usual otherwise. Scored in the last third and over the whole life.
Smoke (one life): both wired the same arcs; over the whole life both ate less than base (play costs food).
V7. leanlearn3bI above learn3bI over the whole life (playing when there is little to lose). 50%. Both above base in the last third. 55%.
**Scored V7** (`lab/v/uptake_lean.log`, 10 pairs, regrow60): half right. Both above base in the last third (+.20 [+.09, +.33] at once,
+.14 [+.04, +.24] when lean), both below over the whole life (-.12, -.14): play's time hasn't paid back within 900 s. Playing only when
lean made no difference: after the first minute food is scarce most of the time here, so lean is nearly always true (play done 285 and
315 s after growth). When to play mattered less than how long play takes.

# G3: does taking up new parts scale? (1, 2 or 4 new thrusters a side; EXTRA_N; 1200 s lives, 10 pairs, plain world, seeds 110000+)
Smoke (one life): 1 a side, play done 126 s after growth, both lines wired; 4 a side, 459 s, one line wired.
G1. Play's time grows about in proportion to the new thrusters (it tries each in turn): roughly 1 : 1.7 : 3 for 1, 2, 4 a side. 60%.
G2. learn3bI stays surely above base at 1 and 2 a side; at 4 a side not surely (play takes too long, and more choices spread its kicks). 50%.
**Scored G1-G2** (`lab/v/uptake_scale_*.log`, 10 pairs, 1200 s): G1 right: play done 141, 243, 446 s after growth for 1, 2, 4 a side
(1 : 1.7 : 3.2). G2 wrong in its second half: learn3bI surely above base at every size (+.33 [+.16, +.52], +.33 [+.20, +.45], +.46 [+.10,
+.76]; told arcs +.40, +.59, +.34); but over the whole life below base, more so with more parts (-.15, -.36, -.73).
## Play bored from certainty, per motor (arms ending B; D48's rule inside play): a motor sure at 3 standard errors (after 20 kicks) is
played no more. Smoke (one life each): 2 a side, play 233 s against 234; 4 a side, 575 against 669: the quarters rarely become sure.
G4. (4 a side, 10 pairs, 1200 s) learn3bIB's play surely shorter than learn3bI's, and its whole-life loss smaller by at least .2. 40%.
**Scored G4** (`lab/v/uptake_scale_4B.log`): wrong. Bored play no shorter (median 489 s after growth against 446), whole life the same
(-.74 against -.73), right side on both lines in 10% (35%). Skipping the sure motors only moves the kicks onto the quarters, which never
become sure. Learning more per kick needs another idea (a side's thrusters move the view the same way: one kick could teach about its
neighbours).

## b. Play until you know what you need (arms ending N; the user: try b, then a)
Play ends as soon as each new eye line has a motor surely moving activity out of its half (not when every motor is known); the surest
is wired. Smoke: life 110002 done 74 to 88 s after growth at 1, 2 and 4 a side; life 110001 never sure for one line, so it ran to the
old limit (234, 669 s).
G5. (10 pairs, 1200 s, 1, 2, 4 a side) median play time roughly flat with the number of parts (under 1.5 times from 1 to 4 a side). 45%.
G6. At 4 a side, the whole-life loss surely smaller than learn3bI's (-.73). 50%.
**Scored G5-G6** (`lab/v/uptake_need_*.log`): G5 wrong: median play 121, 110, 373 s after growth for 1, 2, 4 a side (old play 141, 243,
446): flat up to 2 a side, not at 4 (each kick shared across more thrusters, so the strong ones take longer to become sure). G6 right:
whole life surely better than the old play at every size, +.13 [+.05, +.22], +.30 [+.17, +.44], +.21 [+.04, +.37] (whole life against
base -.02, -.06, -.52); right side on both lines 55%, 80%, 50% (old 35%, 50%, 35%).

# a. Body and rule in one life (`lab/mixed.py 10 seq 11`; seeds 111000+, 1200 s): the tree learns a hidden word from taste while play
takes up the new parts (play until needed, lateral inhibition). Smoke (one life): circuit -86, circuit+play -61, tree 51, tree+play 89,
tree+told 102 (efficiency x 30 s units of the last third, raw).
M1. tree+play surely above tree in the last third. 60%.
M2. The two gains add up: the interaction (both together less the sum of each alone) not surely negative. 55%.
**Scored M1-M2** (`lab/v/mixed_seq11.log`, 10 pairs): M1 wrong in letter: tree+play above tree by +.35 [-.15, +.88], not surely. M2 right,
and more: the gains don't merely add, they multiply. Play alone with the starting brain gives nothing (-.06: its new steering reflex
turns it towards what it believes is food, and on this rung it is wrong half the time); with the tree knowing the rule, play adds +.35;
interaction +.40 [+.03, +.80], surely positive. Knowledge makes skill worth having.
M3. Confirmation on fresh seeds (112000+, 10 pairs, frozen): the interaction surely positive. 55%.
**Scored M3** (`lab/v/mixed_seq11_confirm.log`, fresh seeds 112000+): wrong in letter. The interaction holds its size (+.38) but not
surely ([-.15, +.88]). On these seeds play surely harms the starting brain (-.26 [-.47, -.08]: steering better into what it wrongly
believes is food) and adds +.13 to the tree (not sure). Two seed sets, the same estimate (+.40, +.38): suggestive, not established.
