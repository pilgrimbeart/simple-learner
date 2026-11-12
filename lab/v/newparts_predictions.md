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
