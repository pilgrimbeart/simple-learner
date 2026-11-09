# Stage R predictions (main session, 2026-11-07), written before any R2 life

R1 (the written bank rebuilt from parts): 160 of 160 lives identical to the bank's, on 8 worlds and seeds 81200-81209
(`lab/rivals.py identity`). Done before these predictions; the rest are not yet run.

**R2's rule, fixed here before any life.** K rivals, each drawn independently from the rivals' own stream:
- a base part, chosen evenly from: Count(n, src), n uniform on 2..16, src good or taste; Osc(T, bins), T log-uniform on
  1-200 s (from a few tastes to twice a life), bins 2 or 4, its phase random at birth, phase noise .02 a cycle; Timer(tau,
  src), tau log-uniform on 0.25-10 s;
- with chance .3 a hierarchy: either a Count driven by the base part's events (n 2..4), or a conjunction with a second
  base part;
- trust uniform on 0..3.

The ranges come from the life's scale (a taste about every 1.6 s, a 100 s life), not from the generator's constructs, but
I have read the generator, so the choice is contaminated by what I know; R4's fresh draws and the sealed set are the
guard. The bar to adopt a rival rises with the Occam factor: theta = 2 + (log2 K - log2 6) / 1.7 and Emax = 10 + the same
increase (a +1 is worth about 1.7 bits, D31; K = 6 gives the written bank's values). The written rivals are not included.

**Predictions:**
1. K = 100 passes at least 3 of the 8 fresh swap worlds the written bank fails or can't tell; K = 10 passes at most 1.
   (A swap of period T needs an oscillator within a few percent of 2T: about 2% of rivals of that kind, so 1 - .98^33
   = 49% of worlds at K = 100, 7% at K = 10.)
2. Doing no harm in plain holds at every K with the Occam bar (bank - base within -.1); without it (theta fixed at 2),
   K = 1000 is surely below base by more than .1.
3. Sure passes on stage 3's 55 worlds rise from K = 10 to K = 100 and gain little or fall from 100 to 1000.
4. Satiety and region worlds don't change at any K: no context of these parts expresses "a meal soon after the last is
   bad whatever its colour" or "where the creature is".
5. Alternate and nth worlds: random rivals within .1 of the written bank in x at K = 100 (counts are in the library).
6. The written bank stays surely ahead of K = 100 in the worlds it was built for (alternate, fixed swap period handled by
   trust 0), by less than .3 in x.

**Added before any R2 life, on the user's point (2026-11-07) that rules about time may need longer lives.** R2 also runs
K = 10, 100, 1000 on the 30 worlds of stage 3's 1000 s lives (20 pairs, the same seeds; `lab/stageR2.py long`).
7. A swap every T s gives about 100/T chances a 100 s life to tell a matching oscillator from the default, a few wins each,
   so long periods (T above about 30 s: three swaps or fewer) can't be learned in 100 s by any K, and are at 1000 s.
8. The evidence grows with the life and the Occam cost doesn't, so the best K grows with the life: at 1000 s, K = 1000 is
   at least as good as K = 100 in the swap worlds, where at 100 s it is worse.

**The scaling test (`lab/stageR_scale.py`), written before any of its lives, 2026-11-07 evening.** The user approved 10,000 s lives
for it and asked for it to run overnight without waiting for R2's results, so K stays at R2's values (10, 100, 1000) rather than being
chosen from them. 13 timing worlds from stage 3's 1000 s lives (7 swaps, 2 alternates, 4 satieties) and plain, 10 pairs (seeds
81400-81409), last third. No 10,000 s reference: the bar uses the 1000 s r.
9. At 10,000 s, K = 1000 is at least as good as K = 100 in at least 5 of the 7 swap worlds, and surely better in at least 2.
10. Sure passes in the swap and alternate worlds rise with life length for the best K: more at 10,000 s than at 1000 s (R2 long).
11. Doing no harm in plain holds at every K with the Occam bar. K = 1000 with the written bar harms less than at 100 s, but is still
    below base (each false adoption costs less of a long life, and there are just as many of them per second).
12. The satiety worlds don't change at any K or any life length (as prediction 4).
13. The written bank, which has no rival of the right period, stays where it was at 1000 s in the swap worlds, within .15 in x.

**R2 at 100 s, scored** (`lab/v/stageR2.log`, `lab/v/stageR2_trace.log`; after it ran, so not a prediction):
1. Wrong: no K passes any swap world; random rivals are surely worse than the written bank in all eight.
2. Half right: no harm at any K with the Occam bar (no rival adopted where there is nothing to learn); but K = 1000 with the written bar
   doesn't harm either, so at 100 s the bar wasn't needed there.
3. Wrong: sure passes are flat (written 10, K10 9, K100 9, K1000 10 of 55).
4. Wrong: the satiety worlds get worse with rivals (g174, g244 by .3-.4), and region worlds a little worse.
5. Half right: nth worlds within .1 (g360, g185 slightly better); alternates .2-.6 worse.
6. Right that the written bank stays ahead in alternation, wrong that the margin is under .3.
Traced: (a) the written bank holds "it changes often" (the default's table with trust 0), which carries it in the swap worlds; the random
rule can't draw a rival without a context, so it lacks it. (b) In satiety worlds the adopted rivals are right .27 of the time where the
default would be .85: a rival is scored without acting, which assumes acting doesn't change the world, and in satiety it does (when the
creature eats decides what is bad). (c) In alternation the random rivals hold count2 with the wrong trust, and switch more.

**Added to the scaling test after (a), before any of its lives** (2026-11-07, 23:30): an arm K1000+, K = 1000's own rivals plus "it
changes often", paired with K = 1000.
14. K1000+ is surely better than K1000 in at least 4 of the 7 swap worlds, and within .1 of it in plain and the satiety worlds.

**R2 at 1000 s, scored** (`lab/v/stageR2_long.log`; 20 pairs, last third, the full bar):
7. Wrong: no K passes any swap world at 1000 s either (written 0, every K 0 of 7).
8. Partly right: K = 1000 is at least as good as K = 100 in 6 of the 7 swap worlds and surely better in 2 (g226, g328), and in the
   alternate cycle g245 (-.07 against -.36); but still below the written bank in 4 swaps. In satiety worlds more K is worse (g174:
   written +.32, K10 .00, K100 -.46, K1000 -.68), cause (b) growing with the number of timer rivals.
Sure passes of 17 judged: written 4, K10 0, K100 1 (g261), K1000 0.

**The scaling test, scored** (`lab/v/stageR_scale.log`; 10 pairs, last third of 10,000 s lives):
9. Partly right: K = 1000 is within noise of or better than K = 100 in 6 of 7 swaps, surely better in 1 (g226, -.28 against -.55),
   perhaps 2 (g328); but every K fails every swap.
10. Wrong: no swap passes at any K or life length; sure passes in swaps and alternates are flat (g261 alone, at every length).
11. Wrong: in plain every bank arm is surely below base by about .4 at 10,000 s, the written bank included and with no rival adopted
    (-.37 to -.40), where at 100 s it is +.08. The bank's own parts wear down over a long life; being traced
    (`lab/stageR_plain_trace*.py`, `lab/stageR_plain_ablate.py`). This loss enters every world, so the x of every bank arm at 10,000 s
    is pulled down by it, most where the gap is small.
12. Wrong: the satiety worlds are worse with random rivals at every length (passive evidence, cause (b)).
13. Right in 3 of 7 swaps; in the other 4 the written bank falls by .2 to 1.7 in x, with the gap shrinking (g227 1.07 to .58) and the
    wear-down above.
14. Wrong: K1000+ equals K1000 within .1 everywhere. "It changes often" doesn't rescue the random bank. Not traced; the obvious
    candidate is the Occam bar, 6.3 for 1001 rivals against 2 for the written bank's, so it is adopted late or never.

**The scaling test with the cure** (`lab/stageR_scale_cure.py`, the sized learner v7 or v8 per `lab/v/cure_choice`, written before its lives,
night of 2026-11-08; the scaling test's seeds 81400-81409, the uncured arms its own lives):
15. Plain: the cured written bank and cured K1000+ within .1 of base (uncured -.40 and -.37).
16. The swap worlds still fail with the cure (their failure was not the wear-down: written fails them at 1000 s too).
17. Where the uncured bank passes (g261, the satieties g352, g174, g244, g192 for written), the cured one passes too or can't be told
    apart: no pass lost.
18. Overall, the cured written bank's sure passes at least the uncured 5 of 13; K1000+ cured at least its 1, its fails no more than 11.

Scored (cure v7, `lab/v/stageR_scale_cure.log`, 2026-11-09):
15. Wrong, narrowly: writtenS -.136 [-.209, -.070], K1000+S -.147 [-.221, -.079]; neither surely beyond -.1 (no harm by the bar), but
    the point estimates miss .1. A third of the loss remains (the cusp: v7's wobble costs ~.06 in plain at 10,000 s on its own, the rest
    unexplained).
16. Wrong, and the night's best news: the three swaps (g227, g361, g335) go from sure fails (x -.9 to -1.8) to can't tell with positive x
    (+.18, +.06, +.26); g380 (swap bursts) to a sure pass. The wear-down was most of their failure at 10,000 s.
17. Right: all five passes kept, each higher (+.04 to +.50 in x).
18. Right: written 5 pass / 8 fail becomes 6 / 4 (3 can't tell); K1000+ 1 / 11 becomes 2 / 11. The cure lifts x surely in 12 of 13 worlds
    for written (+.10 to +.69); one surely lower, g245 (alternate cycle, -.11 [-.19, -.02]).

**Stage 3's 100 s worlds with the cure** (`lab/stage3_cure.py`, 184 distinct fresh worlds, the first pass's 60 pairs, paired with its
bank): 19. Nothing-to-learn worlds: none surely worse than the bank by more than .1, the mean difference within .03 of 0. 20. Worlds with
something to learn: coverage (sure passes) within 2 of the bank's on the same 60 pairs; the lopsided-body worlds (thrusters, drag, push)
more often surely better than surely worse.

Scored (cure v7, `lab/v/stage3_cure.log`, 2026-11-09): 19 wrong, badly: in the 118 nothing-to-learn worlds bankS - bank -.61 on average,
surely worse in 95 (by more than .1 in 93). 20 wrong: in the 66 with something to learn, -.60, surely worse in 57, none surely better;
sure passes 0 against the bank's 10. The construction was checked (the old bank's lives reproduced exactly from the same code path): v7
costs heavily in 100 s lives, invisible to the 10,000 s test, which judges only the last third. Traced in `lab/rprop_short.py`.
