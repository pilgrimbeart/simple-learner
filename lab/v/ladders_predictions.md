# Stage 0's ruler: predictions (main session, 2026-11-09), written before any life on these ladders

`lab/ladders.py`. A rung is certified if the told arm's gap over the starting brain is surely at least .25, and a brain designed by hand for that rung, told its
structure but not its letters, surely closes half of it. Efficiency over the whole of a 100 s life, the last third of a longer one.

Sums first. A life offers about 0.6 tastes a second, each at most a bit. Seq n needs about n - 2 bits for its word and log2 n to know the length; time n the same,
but only the tastes of the life; combo k about 2^k bits at most, fewer since a creature that eats well may visit only some histories.

1. **Seq, gap.** The starting brain falls well below told at every rung from 2: every rung has a gap surely above .25.
2. **Seq, designed.** Certified at 2, 3, 5, 7 in 100 s and at 11, 13 in 300 s; 17 at 300 s on the edge. The word's bits are far below the tastes on offer at all of these.
3. **Seq, the bank.** Passes half the gap at 2, 3 and 5, which its written rivals hold, and is below half from 7 up.
4. **Time, gap.** Surely above .25 at every rung from 2.
5. **Time, designed.** Certified at every rung, told the slot's length and phase, since a slot of 10 s offers about 6 tastes. This says the ladder can be learned given a clock, not that a clock is easily grown.
6. **Time, the bank.** Below half at every rung from 2 (D35: no swap passes), with x positive but small, from "it changes often".
7. **Combo, gap.** Surely above .25 at 1 to 4, shrinking with k: where a table sends a good eater round a short cycle or says little, the base loses less. Least sure of this.
8. **Combo, designed.** Certified at 1, 2, 3; less clear at 4 and above, since a creature can't always tell what it ate when a taste isn't vouched for, and that corrupts its history.
9. **Size of the ruler.** At least three ladders with five certified rungs each won't be met by combo at first; if not, that says the combo ladder needs rewriting, not that the goal is out of reach.

**Scored so far (40 pairs, 2.5 ms; `lab/v/ladders_certify_*.log`).** 1 right. 2 right, and better than predicted (17 certified too). 3 right. 4 right. 5 wrong: designed x about .5 at every size, none surely above the bar. 6 right. 7 wrong on shrinking: gaps 1.7-3.8 with no trend. 8 wrong in part: 1, 3, 4, 5, 6 certified, 2 not (.42 [.27,.53], 100 s). 9 wrong: combo has five certified rungs.

**Added before the rerun.** 5's x stays near .5 whatever the size, so it looks like a fixed cost per slot, not a limit on learning. Suspect: the designed brain updates which colour to follow only at a taste, so after a slot change it follows the old colour until a taste corrects it. 10. With the colour re-read from its clock at every moment, designed x rises surely above .5 at every timing rung. 11. Combo rung 2 at 300 s, not 100 s, is certified.

**Scored 10, 11.** 10 right on rungs 2 and 5 at 12 pairs (x 1.06, .99), the full ladder rerunning. 11 wrong: .52 [.33,.67], not surely above half. Combo keeps five certified rungs without it.

**The baseline and the ladders' difference, before their lives.** Baseline: the bank with K = 10, 100, 1000 random rivals (`lab/rivals.py`, R2's rule and Occam bar) as today's only "raw material", 20 pairs. 12. The highest rung solved doesn't rise with K on any ladder: flat. On seq it stays at or below 5, on time and combo at the bottom. Cross: each ladder's designed brain, at a middle size, on the others' middle rungs. 13. Each closes under .3 of the other ladders' gaps, so the ladders do differ. Least sure of seq's brain on combo, since a good eater goes round a short cycle of histories that looks like a word.

**Scored 12, 13 so far.** 13 wrong in part: combo's brain closes .40 on seq; time is clearly apart. 12 wrong on seq: more K does climb there with longer lives (rung 13: K10 .22, K100 .65, K1000 .90), until the word's length leaves the menu's counters (2 to 16: rung 17, .35). A ready-made menu holds the answer; that is what K buys.

**The user's catch, 2026-11-09: world and brain shared a clock.** Time's slots began at t = 0, so every brain knew their phase from birth, and the designed brain read the world's own t, exactly: godlike. Fixed: each life draws the slots' phase; the designed brain now has a free-running oscillator of its own (`rivals.Osc`, random phase, phase noise .02 a cycle), told the period, not the phase, with a table of 5 bins a slot, so it needs no lock but pays in evidence and at slot edges. Seq and combo also started at a known place (the word's first two letters forced different; history 0), which a design could use: each life now starts at a drawn place. All earlier ladder numbers are superseded, and rerun.
14. Time, designed: x falls from about 1.0 but stays surely above .5 at rungs 2 to 7; rungs 11 and 13 less sure, since phase noise accumulates over long periods (.02 a cycle against a bin of 1/(5n) of a cycle: about 1 bin at n = 11 after a cycle or two of wander). 15. Seq and combo barely move.

**The user's decision, 2026-11-09: the slot's length drawn per life too**, log-uniform 5 to 20 s, so that a brain must discover the rhythm as well as lock on. The designed brain is told each life's length (a yardstick's privilege: it shows a rung is learnable given the rhythm, and a brain must find it for itself), never the phase. Lives unchanged.
16. Time, designed: as 14, a little worse at long slots' fewer periods and short slots' fewer tastes a bin. 17. Time, random ideas and the bank: no better than with fixed slots; every K stays below half at every rung, since at a given K a right period is rarer now. Least sure at K = 1000, rung 2.

**Scored 14-17 (the rerun on the corrected worlds, 40 pairs certifying, 20 for the baseline; `lab/v/ladders_*.log`).** 14 and 16 right:
time's designed x .82, .71, .69, .61 at rungs 2, 3, 5, 7, all surely above half, and .46, .38 at 11, 13, not: the free-running clock's
drift over long slots. 15 right: seq certifies 2 to 17 again; combo 1, 3, 4, 5, 6 again, 2 not. 17 right: on time no K reaches half
anywhere (best .24 [.11,.35], K = 1000 at rung 2), and from rung 5 every K is at or below 0. Cross: as before, combo's brain closes .39
of seq's gap, everything else under .05 or negative. Seq's baseline as before, with a flaw in the ruler shown up: K = 1000 solves rungs
2, 3, 11, 13 but not 5 and 7, because 5 and 7 get 100 s lives and 11 and 13 get 300 s. A rung isn't harder than the one below it unless
its life grows no faster than what it asks, so "the hardest rung solved" misreads a climb.
18. Time rungs 4 and 6 (added: time had four certified rungs, short of five) certify, designed x between .6 and .72.
**Scored 18.** Right: rung 4 x .72 [.62,.80], rung 6 .69 [.63,.75], both certified (`lab/v/ladders_certify_time46.log`). Time has six.
