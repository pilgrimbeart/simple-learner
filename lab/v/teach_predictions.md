# Stage 1, the first experiment: who teaches the raw material? Predictions (main session, 2026-11-09), before any life

`lab/teach.py`, on the sequence ladder (`lab/ladders.py`, its lives unchanged, as the user decided: revisit life length only if
needed). Raw material counted in units, a unit being one letter: a one-bit memory and its tally of trust. Material P = 4, 8, 16, 32, 64.

**What the sums say first.**
- **Units teaching each other can't help here.** The blocks' colours are drawn at random, so the eyes carry nothing about the word; only
  taste does. Predicting senses or neighbours would learn nothing about it. That arm is answered by the sum, not run; it belongs on a
  ladder whose answer is partly visible.
- **Credit doesn't interfere here.** A vouched taste says which colour was food, so every unit can be scored on it at once, counterfactually,
  as the bank's rivals are: N units don't make each other's evidence noisy. The danger the programme named (one score for a group effort)
  is a ladder where units act on the body jointly; not this one.
- So the real choice is between material and time. **All at once**: the bank holding one ring of every length from 1 to M, all scored on
  every taste, P = M(M+1)/2 units, so it climbs as the square root of the material, about sqrt(2P). **A few at a time**: one ring that
  grows a unit when its own confirmed letters keep being contradicted, so it climbs up to P, paying in time: trying lengths 1 to n takes
  about n^2/2 tastes or more, about 150 at n = 17, against about 65 tastes in a 100 s life and 200 in 300 s.

**The arms.** `bank` (the bank with rings 2..M as Count(L, good), the Occam bar for M - 1 rivals); `grow` (one ring, frustration F: a
leaky count, 60 s, of vouched bads at positions whose letter a good had confirmed since its last flip; at F >= 2 the ring grows by one
unit, its letters copied round, until it has P). Both are designed by hand, so legal for stage 1 as one design for every rung.

1. **Bank**: solves (closes half surely) the rungs up to M where the life allows: P 4 to rung 2, P 8 to 3, P 16 to 5 (5 at 100 s on the
   edge, as K = 100 random rivals was .49), P 32 to 7, P 64 to 7 again (rung 11 needs M = 11, 66 units).
2. **Grow**: in the plain world (rung 1) it grows past 1 in under one life in ten.
3. **Grow**: solves rungs 2 and 3 at every P that holds them; 5 and 7 in 100 s not surely (the n^2/2 tastes against 65); 11 and 13 in
   300 s not surely either; 17 not. So at today's lives, growing climbs no higher than the bank, and its curve is set by life length.
4. **The shape**: the bank flattens in material (sqrt P); growing is flat in material beyond the rung's n and climbs only as lives grow.
   Neither alone is "add more brain and it climbs": a mix (several rings growing at once, each at its own lengths) would trade one for the
   other. Least sure of 3: growing may skip quickly through wrong lengths, since a wrong ring is contradicted within about one cycle.

**Scored (`lab/v/teach.log`, 20 pairs, seeds 84000+).** 1 right, a little better than predicted: the bank solves up to rung 2 at P 4, 3 at
8, 5 at 16 (.68 [.62,.73], not on the edge), 7 at 32 and at 64. 2 right in effect: in plain the ring's median stays 1 (some lives reach
2, with letters copied round, so behaviour unchanged): x exactly 0 against base, where the bank's is -.09 [-.31,+.15]. 3 right: grow
solves 2 and 3 at every P, then 5 at .30, 7 at .14 (100 s), 11 at .38, 13 at .24, 17 at .24 (300 s), none surely above half. 4 right:
the bank climbs as sqrt of material and stops; grow uses only what it needs (P 16, 32, 64 give identical lives) and is limited by time.
Where grow's time goes: it reaches the right length, but late (rung 11: final lengths 10 to 12 in 300 s; rung 17: 10 to 14), about n^2/2
tastes, since each wrong length must be filled and then contradicted. An ideal learner needs about n + log2 n tastes.

## The record arm (the user agreed, 2026-11-09), predictions before its lives

`record`: P units hold the last P letters revealed, each by its good-meal count (a trusted taste reveals the letter at that count; an
untrusted one leaves it blank). One comparing unit per look-back k up to P/2 counts agreements and disagreements between each newly revealed
letter and the one k back. The brain follows the letter k back for the best k (agreements minus 4 disagreements, the smallest k on ties,
none until some k has agreed); with nothing to follow it holds the colour it has. The user's observation: this leads towards a
time-delay network looking at a shift register; keep each unit a plain comparator.
5. Plain: x not surely below 0 (k = 1 always agrees).
6. Solves every rung n with 2n <= P, in about 2n + a few tastes, well within every life: P 4 to rung 2, P 8 to 3, P 16 to 7, P 32 to
   13, P 64 to 17. Doubling the material doubles the rung: the first climb. x a little below the designed brain's (.87 to .98), as it
   spends about one more pass of the word.
7. Rungs above P/2: not solved (no k fits); x small but possibly positive from partial matches.

**Scored 5-7 (`lab/v/teach_record.log`).** 6 right, exactly: solved up to rung 2 at P 4, 3 at 8, 7 at 16, 13 at 32, 17 at 64; x .66 to
.93, about the designed brain's at long lives (.90 to .93 at 300 s). Doubling the material doubles the rung. 7 right: above P/2, x about
.3 (following the last revealed letter). 5 wrong: in plain it costs, x -.11 to -.17, surely below 0 at every P. Suspect, untested: it
takes a single trusted bad as the letter, with no tally of trust as the designed brain and grow have, so one misread taste overwrites a
letter and counts four times against k = 1.
**The plain cost traced** (a probe, 10 pairs at P 16): 1 to 9 trusted bads a life in plain, each flipping the colour at once (changes
about equal to bads), and copied forward k steps later. Fix: the letter followed is a vote of every copy of this step's letter in the
record (k, 2k, ... back, and this step's own), ties to the most recent. 8. Plain: x no longer surely below 0. 9. The climb unchanged
(solved up to 2, 3, 7, 13, 17), x at or above before.
**Scored 8, 9 (`lab/v/teach_record_vote.log`).** 8 mostly right: plain x -.02 to -.06, surely below 0 only at P 8 (-.04 [-.08,-.00]).
9 right, and x up: .71 to .98 on the solved rungs.

## Stage 2, step A: registers moved by different events (the user agreed, 2026-11-09), before its lives

`events` (`lab/teach.py`): the record arm's unit, with several registers, each moved by its own kind of event: good meals, any trusted
taste, and the brain's own clocks of 1, 2 and 4 s (random phase, drifting .02 a cycle). Each register holds P / 5 units, with look-back
comparators up to half its length; the best register and look-back is followed, scores compared directly (each taste reveals one letter
to every register). Material P = 40, 80, 160, 320. On the seq and time ladders.
10. Seq: picks the good-meal register; climbs as record did at a fifth of the material per register: solves up to rung 3 at P 40
    (8 a register), 7 at 80, 13 at 160, 17 at 320. Plain costs about as record's.
11. Time: the word repeats every n x tau / T of a clock's beats (tau the slot, 5 to 20 s): at T = 4 s, n = 2, tau 20 s that is 10 beats,
    so a register of 32 (P 160) reaches rung 2 to 3; P 320 (64 a register) about rung 5. Drift blurs long look-backs: x lower than
    designed's. Least sure of all: the vote over copies at k, 2k, ... may be what saves it, or what breaks it.
**Changed before the full run** (smoke lives, seeds 84000-84002): the vote over every copy made the time ladder far worse than base: it
settled on a clock's look-back 1 (persistence: a slot lasts several beats), and a majority over the whole register lags each slot change.
Now: this step's own letter if revealed, else a vote of the three most recent copies. Smoke: time level with base, choosing look-back 1
of the taste register, never a period. 12. (Added) Time doesn't climb: a free-running clock's beat is no whole fraction of an unknown slot,
so copies further back slide out of step; the chooser prefers persistence. Then 11 is wrong.
**Scored 10-12 (`lab/v/teach_events_seq.log`, `teach_events_time.log`).** 10 right on the climb: it picks the good-meal register itself
and solves up to rung 3, 7, 13, 17 at P 40, 80, 160, 320 (x .60 to .96). Wrong on plain: -.11 to -.15, surely below 0, back to the
record arm's cost before its vote (the vote now uses three copies, and five registers give more chances to follow a misread). 11 wrong,
12 right: time rung 2 x .45 (P 160), .58 [.46,.67] (P 320), not surely solved, though above the random rivals' best (.24); rung 3 .21,
.31; from rung 4 within about .1 of base at either P. The chooser mostly prefers persistence (the taste register, look-back 1).

## Stage 2, step B: clocks that lock on (the user agreed, 2026-11-09), before its lives

`lock` (`lab/teach.py`): the free-running clocks replaced by four adaptive ones (Large & Kolen 1994; starting periods 3, 6, 12, 24 s,
each jittered and drifting): a trusted bad pulls each clock's phase .7 of the way to it and its period by .3 of the error. Registers:
good meals, trusted tastes, one per clock, each P/6 units. And a change made to `events` too: every register and look-back is now scored
on what it would have predicted for each taste, before the letter is recorded (the bank's way), since scoring at recording gave a clock's
register one comparison a beat against the taste register's one a taste. A probe (seeds 84000-84003, 100 s) found clocks moving
towards the slot (16.3 against 15.6 s; 13.9 and 15.1 against 14.2) but not reliably. Smoke (4 lives): time rungs 2 and 5 now choose a
clock's register, x about .3 to .4.
13. Time: x surely above base at rungs 2 to 7 at P 240 and 480, about .3 to .5; solved (surely above half) at none, or at most rung 2.
    The designed brain, told the slot, got .82 to .61; the gap is locking, not learning letters.
14. Time: barely moves with P from 240 to 480 (four clocks either way; P only lengthens look-backs, already long enough to rung 7).
    So this is not yet a climb with material: more clocks, not longer registers, would be the material that helps.
15. Seq at P 240 (40 a register): solves to rung 13, as `events` at 160 did (32 a register); plain still costs about .1.
