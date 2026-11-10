# D39: a bank of fixed clocks for the timing ladder. Predictions (main session, 2026-11-10), before any life

`lab/teach.py clocks`, on the time ladder (`lab/ladders.py`, its lives unchanged), 5 pairs (PROGRAMME.md, How we work: a principle
worth having shows in about 5 pairs). The belief it could move: timing is limited by how the clocks lock, not by material or evidence.

**The sums first.**
- **Evidence isn't short.** Tastes come at about .67 a second and slots last 5 to 20 s, so a slot holds 3 to 13 tastes and a change is
  placed to within about half a gap between tastes, .75 s. A word of n letters is seen twice in 2n slots, about 24n s of a 150n s life.
- **Why the designed brain fades** (x .82 at rung 2, .38 at 13): it keeps one clock of period n slots, never corrected. A clock drifts
  .02 of its period per root cycle, so after a life of 15 of its cycles it is out by about .02 x 10n x 3.9 = .8n s: at n = 13, a whole
  slot. A clock one slot long, corrected at each change, never drifts further than a few slots' worth: about .5 s.
- **Why D38's lock runs away.** Its surprises are trusted bads, which come whenever the brain mispredicts, not only at the world's
  changes, and stop once it predicts well; and each moves the period by .3 of the phase error, which for a clock far from the slot's
  length is a random number up to half a period. So the period does a random walk to its cap.
- **What a clock must match.** With only its phase set at each change (about every second boundary), a clock whose period is off by a
  share d mis-times about d to 2d of the tastes. So periods about 10% apart (within 5% of any slot) are enough: 24 clocks span 3 to 30 s.
  That number is set by the range of rhythms covered, not by the rung; the rung sets each register's length, 2n letters.

So material P = 26 registers x Pr letters, and a rung n should be solved when Pr >= 2n: P 208 (Pr 8) up to rung 4, P 416 (Pr 16) up to
7, P 832 (Pr 32) up to 13. Run: rungs 2, 5, 11 at P 208, 416, 832; rung 1 (plain) at P 416.

1. Rung 2 solved (surely above .5 at 5 pairs) at every P; x .6 to .85. 75% sure.
2. Rung 5 solved at P 416 and 832, not at 208 (x there under .5). 55% sure of the solving, 80% of the failing at 208.
3. Rung 11 solved at P 832 only. 45% sure: the longest registers have the most look-backs for the Occam bar to hold back.
4. The clock followed is within 10% of the life's slot length (or of a whole multiple of it) in most solved lives. 60%.
5. Plain: x not surely below 0 (no confirmed changes, so the clocks' registers hold one letter). 70%.
Least sure of: the choosing. Neighbouring clocks are each partly right, and the candidates are many (26 registers x Pr/2 look-backs),
so the Occam bar is higher than the lock's; and a register's letters now arrive one taste late.

**Scored (`lab/v/clocks_time_plain.log`, `clocks_time.log`; 5 pairs).** 1 right: rung 2 at x .69, .72, .72 (surely above half at two of the
three sizes). 5 right: plain exactly 0. 2 and 3 wrong: rung 5 at .02, .27, .16 and rung 11 at -.10, -.04, .33: nothing solved above rung 2,
though the look-back followed is often the right one (5 at rung 5, 11 at rung 11).
**Traced** (`lab/clocks_probe.py`, rung 5, four lives). (a) The bar is steeper than my sum allowed. A poison costs 4 meals, so following
the wrong colour a share w of the time scores about 1 - 5w of told. The starting brain is already right .71 to .85 of the last third
(it flips on one vouched bad, and slots last 6 to 10 s), the designed brain .89 to .97, the clocks .82 to .91: half the gap in time
followed is a quarter of it in score. (b) The clocks' excess over the designed brain is deep in a slot (.02 to .08 of the time against 0
to .03), not at the changes (.04 to .08, like the designed brain's). (c) A nearer clock isn't a better one: in one life a clock 1.3% off
gained two beats on the world and disagreed with 20% of tastes, where one 10% off kept count and disagreed with 10%. So beats slip. The
midpoint is the suspect: when the two tastes either side of a change are far apart (a roam), their midpoint can be most of a beat from
the boundary, and it also jitters a clock that was already right.

## The second version: a clock is moved only as far as the evidence says. Predictions before its lives
The two tastes say only that the boundary lies between them. A clock with a beat already in that gap is left alone; any other has its
nearest beat moved to the gap's nearer end. Nothing else changed. Rungs 2 and 5 at P 208 and 416, 5 pairs.
6. Rung 5 at P 416: x above .45. 70%. Solved (surely above half): 40%.
7. Rung 2: x at or above the first version's (.69 to .72). 75%.
8. In the probe's four lives the clock nearest the slot's length keeps count (beats within 1 of the slots passed). 65%.
If 6 fails, the limit isn't the phase rule; look at what the registers hold before touching the clocks again.

**Scored 6-8 (`lab/v/clocks_time_v2.log`).** 6 right as far as it went: rung 5 at P 416 x .50 [.40, .60] (from .27), not surely solved.
7 right: rung 2 at .74 and .83 (from .69, .72), both sure. 8 half right: where a clock lies within 3% of the slot's length it keeps
count (71 beats to 71 slots, 99 to 100) and is followed at the right look-back, but in two of the four lives no clock is within 4% and
none keeps count. A clock that keeps count still disagrees with 12% of tastes.

## Is it only how closely the clocks are spaced? Prediction before its lives
My sum said 10% apart would do; the lives say a clock must be within about 3%. The cheapest test changes nothing but the number: 60
clocks over the same range (4% apart, so one within 2% of any slot), each register 16 letters as before, P = 62 x 16 = 992. Rung 5, 5 pairs.
9. x at or above .6: 60%. Surely solved: 50%. If so, what the timing ladder needs is fine periods, which a clock could also get by
trimming its own period within its band; if not, the 12% a counting clock still gets wrong is the limit, and the registers are next.

**Scored 9 (`lab/v/clocks_time_nc60.log`).** Right, short of sure: rung 5 at x .63 [.42, .82] with 60 clocks, about the designed brain's
.69, which is told the slot's length. So the spacing was most of what was left, and the timing ladder's fixed cost is fine periods.
