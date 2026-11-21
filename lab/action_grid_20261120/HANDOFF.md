# Action grid — handoff (D184), 2026-11-21

**Which fixed comparisons support which lever.**
- *Exploration* (explorer threshold, oscillator speed): the strongest support. A higher threshold (the explorer
  holding the motors less) raises informed net (+0.07 within grid); a faster oscillator raises food (+0.13) and path.
- *Sensory authority* over the shared motors: supported indirectly. The single-pulse motor response on the bench ranks
  with informed net (Spearman 0.89 across 54 settings), and the winners pass more pulses into motor events
  (0.70–0.76 within 50 ms against 0.55). Sensory gain itself is not the lever (2×: no gain; 0.5×: harmful).
- *Motor recovery* (decay 2.5 ms): no clear marginal effect, though all three winners have it.

**What remains confounded.** Threshold, oscillator and recovery all change how often the explorer holds the motors
and how far the robot moves, so "less masking" and "more encounters" are not separated; each knob also changes
noise and trajectories. The rail excursions (motors, P1 memory, sensory nodes) are in most lives, so it is unknown
how much of the gain depends on clipping.

**Did a physically eligible informed improvement survive?** An improvement survived fresh seeds at all three steps
(corrected lower bounds > 0), but not the practical margin (+0.10), not step convergence (±0.05), and not physical
eligibility (rail excursions in about 72–77% of candidate lives). It remains diagnostic. No setting meets the job.

**One next question.** With the rail excursions removed under the chip's contracts, does the explorer's masking of
the senses (and not encounter rate) still account for the gain, as judged by the same informed, neutral and
reversed lives?

Reviewer decision needed: whether to pursue that question, and whether the rail excursions are addressed first.
No repair designed, no experiment launched.
