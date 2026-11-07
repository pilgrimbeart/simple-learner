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
