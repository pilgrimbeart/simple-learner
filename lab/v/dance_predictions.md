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
