# The paired-blocks world: is there a rung here? Predictions (main session, 2026-11-10), before any life

`lab/pairs.py`, 5 pairs of 100 s lives, the starting brain (which learns the colour) and the told arm, plain and at gaps of 10, 6, 4,
3 and 2 mm between a pair's centres (blocks are 1 mm in radius, so 2 mm is touching). The belief it could move: that an acting rung
exists on today's body, where the starting brain falls short through how it drives, not what it knows.

**The sums** (`world.py`; the starting brain's numbers, `table.numbers`).
- The mouth eats within 1 mm; the eyes' corridor is the 2 mm the mouth will sweep, out to 15 mm; a block hides what is behind it.
- A drive beats both thrusters about 57 times a second, each beat adding 40 mm/s that fades at 50 a second: about 45 mm/s. A poison
  pulse ends a drive, and the eye pulses up to 50 times a second, so stopping takes about 20 ms of travel (.9 mm) and .9 mm of coasting.
- Poison beside the food, across the path: in the corridor too when the gap is under 2 mm across, so its pulses end the drive before the
  meal. Poison behind the food: hidden until the food is eaten, then 0 to a gap ahead, against 1.8 mm to stop. Poison in front: eaten first.
- So at 10 and 6 mm the pair is two separate blocks. At 2 to 3 mm a good share of meals should bring the poison with them.
- A second effect, on what the brain knows: a poison eaten just after its food, while still driving at food, is a vouched bad, and the
  starting brain's tally flips on one. The told arm can't be misled, so told minus circuit is the cost of that false evidence.

1. Gaps 10 and 6 mm: both arms within .3 of plain. 75% sure.
2. Gap 2 mm: told at least 1 below plain (poison with at least a quarter of the food). 60%.
3. Gap 2 mm: circuit at least .5 below told (mislearning). 50%.
4. The loss grows steadily as the gap closes from 4 to 2 mm, in both arms. 65%.
If 2 fails, pairs are no rung for driving and only (perhaps) one for evidence; if 2 holds, the yardstick to build is a careful driver.

**Scored (`lab/v/pairs.log`, 5 pairs).** 1 right: at 10, 6 and 4 mm both arms are within .3 of plain (2.34 and 2.28). 2 wrong in size and
in cause: at 2 mm told is 1.56, .7 below plain, and the poison eaten doesn't rise at all (7.8 a life, as plain); what falls is food, 53 to 40.
The poison eye ends the drive, so the brain declines the food beside it. 3 not shown: the circuit is 1.20 against told's 1.56, their intervals
overlapping. 4 wrong in shape: nothing is lost down to 4 mm, a little at 3 (told 1.88), most at 2.
So touching pairs are a rung for driving: about a quarter of the food is given up, by a brain that already keeps the rule "food in
view and no poison in view". What would win it back is how to approach (from the side where the food isn't beside its poison), which
no present brain attempts. Not yet a certified rung: that needs a yardstick, a careful driver showing the food can be had.

## The yardstick: a careful driver. Predictions (2026-11-10) before its lives
`lab/pairs.py careful`: the starting brain's driving with two changes by hand, told the colour so that only driving is judged.
**The sums.** An eye's rays stop on a block within 1 mm of them, so a poison block is seen when its centre is within 2 mm of the
heading line but eaten only within 1 mm. One the mouth would touch covers more than half the corridor's rays; one merely beside the path
covers less than half. So (1) a poison pulse ends a drive only when the poison eye is at least `ratio` as busy as the food eye. And a
partner straight behind the food is hidden until the meal, then 2 mm of travel away against 1.8 mm to stop: so (2) a good taste ends the drive.
Settings: ratio 0 (heed every poison pulse, as now), .3, .6, 1; stop off and on; at 2 mm and in plain; 5 pairs.
5. At 2 mm the best setting is at least .4 above the told arm (1.56), winning back over half of what touching costs. 45%.
6. That setting costs under .15 in plain. 65%.
7. Stopping at a good taste helps at 2 mm (45%), and costs in plain (60%: a meal's momentum often carries the creature on to the next).
If 5 fails with poison eaten rising, what the eyes tell isn't enough to drive between the two, and pairs are a rung for a better eye.

**Scored 5-7 (`lab/v/pairs_careful.log`, 5 pairs, told the colour).** 5 wrong: at 2 mm the best setting (ratio .3, no stop) is 1.72 against
the told arm's 1.56, +.16 where I asked for +.4, inside the intervals. Heeding less poison (ratio .6, 1) wins no food (39 to 43 against 40)
and eats more poison (8 to 11 against 7.8). 6 right for what it's worth: nothing costs in plain. 7 wrong: stopping at a good taste loses food
at 2 mm (36 to 37) and doesn't help.
So how busy the poison eye is doesn't tell a partner beside the path from one in it well enough to drive between them, and by my own
test pairs aren't yet a rung these eyes can climb. Untried: leaving and coming back from another side; a split eye (D24).

## The manoeuvre: look before you leap (D41). Traced first, then predictions before its lives
**Traced** (`lab/pairs_probe.py`, the told arm at 2 mm, 10 lives). A poison pulse ends 45 drives a life with food ahead (40 foods are
eaten). At that moment the food is a median 4 mm ahead, and: in 32% the food is in the mouth's path and its partner isn't (carrying on
would have eaten clean: 14 a life, as many as the 13 foods lost); in 26% the partner is in the path but behind the food; in 24% in the
path and nearer; the rest, the food isn't in the path.
**Why the careful driver failed, by sum.** It compared the eyes over .1 s. At 10 to 25 pulses a second that is one to three pulses an
eye: no comparison at all. Telling less than half the corridor from more than half takes ten or so pulses, about .3 s, and at 45 mm/s
the creature has .09 s before it arrives. The information is there; the time isn't, unless it stops.
**So: stop and look.** A poison pulse during a drive doesn't end it: the brain stands still for `look` s, counting both eyes; if the
poison eye was under `ratio` as busy as the food eye it drives on, heeding no poison, and stops at the good taste (the partner may be
just behind); else it turns away. Told the colour. look .15 or .3 s, ratio .4 or .7; 2 mm and plain; 5 pairs.
**The sum for what it could win.** Up to 58% of 45 stopped drives are winnable (26); looking costs 45 x .3 = 13 s of a 100 s life (about
7 foods); each of the 24% in the way wrongly accepted costs 4. At 80% right: +21 - 7 - 9, about +5 to +10 foods' worth on 40.
8. Best setting at 2 mm: at least 1.75 (told 1.56). 60%. At least 1.92, half of what touching costs. 40%.
9. Costs under .15 in plain. 60%.
10. look .3 beats look .15 at 2 mm. 55%.

**Scored 8-10 (`lab/v/pairs_looker.log`).** 8 wrong: at 2 mm every setting is below the told arm's 1.56 (1.01 to 1.43), food 30 to 35
against 40. 9 right for the short look, not the long (-.10). 10 right but beside the point.
**Traced** (6 lives, look .3, ratio .7). The look does tell: of 30 looks a life it commits 9 times, 7.7 ending in food alone and .8 with
poison; of the stops where the partner was in the way it commits 1 in 20, of the clean ones 6 in 10. But a look of .3 s gathers only 3
food pulses and 5 poison pulses, and the 30 looks and 21 turnings-away take 17 s of the life. The starting brain, which just scans on
and tries again at once, gets most of those foods anyway by flickering through.
**The sum, redone with what was measured.** Looks win at most about 8 foods a life and cost 9 s of standing still, about 4 foods, before
any turning away: a tie at best, whatever is done after a look. So I stop here, at the mechanism's second version. With these eyes,
learning whether the partner is in the way costs about what it earns. That is D21's and D22's wall again (the eyes don't say where
across the corridor a block is, and probing for it doesn't pay), met from another side.
