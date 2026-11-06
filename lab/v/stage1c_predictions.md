# Stage 1c: predictions, written before anything was run (2026-11-04)

Not to be edited after the first run. I have read the code, D29-D31 and 1b's logs; I have run no life. Each is a guess to be scored.

## 1. Replication (fresh seeds 62000+, 1b's settings)

- P1.1 Every bank efficiency within 0.08 of D31's table. Bayes arms: BMA one setting surely above the bank in swap10, alternate and pattern, tied elsewhere (same signs as D31).
- P1.2 World's best Bayes will shrink a little from D31 (it was chosen on tuning seeds per world), by at most 0.05, except swap10 where it may shrink by 0.1.
- P1.3 False picks, bank: unreliable .42 +- .04, digest .53 +- .04, patchy .11 +- .03. Budget bits/life within 5% of D31.
- P1.4 The two no-floor arms replicate: +1/-1 no floor surely above the bank in swap10 (about +.07), tied elsewhere; +1/-3 no floor surely below in swap10 and pattern.

## 2a. Change-allowing ideal (fixed share over the seven)

- P2.1 Derived: with a +1 worth u bits, a floor at 0 and threshold theta behave like a hazard per rival per taste of h = 2^(-theta u). At u = 1.7: h about .095 for theta 2 and .029 for theta 3. So the implied expectation is a change every 10-35 tastes for a given rival, in the order of every 15-60 s. That is far higher than any stationary world supports.
- P2.2 Some h in .01-.1 with e about .2 will match the bank's false-pick rate in unreliable within .05, since any threshold family can match one rate. But agreement on tastes where either is on a rival (Jaccard) will be under .7 pooled over the default-right worlds, because the -3 exit has no Bayesian counterpart with equal steps.
- P2.3 False picks of fixed share grow with life length as the bank's do (the stationary learner's saturate). I expect this signature to match better than the picks themselves.
- P2.4 Evidence: all nine worlds' streams favour h below .01 per taste, by several bits a life, over the implied .03-.1.
- P2.5 Verdict: **undecided, leaning to weakly supported in form and refuted in setting**: the floor is the right form of a change-expecting rule, set for far more change than the nine worlds have.
- P2.6 Real lives: the best fixed share one-setting not surely above 1b's BMA in the nine-world recovery score; surely above the bank in swap10.

## 2b. Changing-rule ideal (two-state HMM)

- P2.7 HMM with rate about right in swap10: 1.0 to 1.3, about equal to model 1/0 from birth (1.00), since at low lie rate one bad flips it. It recovers at most +.3 of the +1.77 (told - birth).
- P2.8 Period and phase known (one bit of hypothesis): 2.4 to 2.7, so at least 80% of the +1.77. So nearly all the remainder is bits about *when*, which a memoryless hazard can't hold.
- P2.9 Widening: about 13 bits of period and phase family: 1.6 to 2.2 in swap10. Loss roughly 0.03-0.06 efficiency per bit of prior, not linear: the first few bits free.
- P2.10 The T=10-only learner collapses in swap at another period (below the HMM); the wide family doesn't.
- P2.11 Controls: HMM at swap10's rate loses .1 or less in plain, loses at least .2 in unreliable (it chases lies); HMM with the seven loses less than .05 against BMA in the stationary worlds and is at least HMM-alone in swap10.

## 3. Does the floor pay?

- P3.1 Control: T beyond the life reproduces plain's lives exactly.
- P3.2 After a *plain* prefix there is little to forget: at T=70 the no-floor +1/-1 counters will have sunk to about -2 for 1/0 and about 0 to -2 for sequence rivals. So delay: no floor +1/-1 within +- 1 s of the bank; +1/-3 no floor 1-4 s later than the bank; stationary MAP 1-3 s later.
- P3.3 Efficiency after T: no arm of the counters more than .1 from the bank in most of the nine; the bank's floor doesn't surely pay at T=30; it pays surely against +1/-3 no floor at T=70 in at most half the worlds. Told remains much higher.
- P3.4 Forgetting pays more where the prefix is noisy (an addition to the brief's worlds: unreliable until T): no floor +1/-3 at least 10 s later than the bank, or never, and at least .2 in efficiency after T.
- P3.5 Range: bank 11 levels per rival (3.5 bits). No floor +1/-3 needs about 6 bits per rival in noisy worlds; floor -3 at +1/-1 needs under 4 bits and does about as well as no floor.
- P3.6 Combined tally: +1/-1 with a floor at -3 or -10 slightly above the bank overall, not sure over all worlds together. Nothing dominates the bank in every world.

## 4. The taste limit

- P4.1 There is no firing cap in `world.py` or `creature.Life`. A bound needs one assumed. The only unconditional limit: one pulse a tick, 100 a second.
- P4.2 Per firing a mouth moves at most (PUSH + RADIUS TURN) TICK / (1 - exp(-DRAG TICK)), about 1.45 mm; in pairs about .51 mm a firing.
- P4.3 A rigorous bound in expectation is possible from close-pair counting: about 1.7 mm of mouth path per meal, for any policy. At 100 firings a second: over 80 meals a second, hardly better than the tick's limit. An estimate from nearest-neighbour hops with paired firing: 16 a second.
- P4.4 An oracle told all positions at 50 pairs a second, 6 to 12 meals a second; at 100 pairs, 10 to 20. All below the bound.
- P4.5 Usable evidence for a wire-only eat-more policy: 1.5-2.5 tastes a second, attribution worse (e of .1 to .25 in plain). In plain, .5 to .9 bits/s against the bank's .52; in unreliable .15 to .3 against .15. So eating more buys evidence, but less than in proportion.
- P4.6 Surviving "too short whatever the brain": only those where a difference doesn't show within a life (rho near 0) or lies near one half, each conditional on a firing cap. Everything stated by rate at 0.63 becomes "too short at that rate".

## 5. Synthetic controls

- P5.1 Pass at half the gap to told: at capped share .25 and truly general cures (q .85), yes falls to under half of runs (a false no), and F_novel reads low by about the capped share. At share .5 yes is close to 0.
- P5.2 Pass at half the gap to an honest reference: yes barely moves with capped share; false yes stays at or near 0 on no-sharing populations at planned sizes.
- P5.3 A flattering reference (one reaching half the real achievable closure) raises F_novel, with false yes above 20% at q = .3-.5 and with a "half-working" population.
- P5.4 Recommendation: gap to a frozen, stated reference, with an absolute floor on closure to told (about .25) as a guard, and told reported beside it.
- P5.5 Coin-flip taste: any eating brain scores below zero, about -1 to -2 in efficiency; a still creature scores exactly 0. So do-no-harm can't mean "at the base's score or above" alone; a brain that learns to stop beats the base.
- P5.6 New, from reading the score: in worlds with a very negative base, a creature that never eats scores 0 and so closes much of the gap to told (alternate about .55, digest about .7) with no learning at all. If so, the pass bar needs the still creature in its base.
