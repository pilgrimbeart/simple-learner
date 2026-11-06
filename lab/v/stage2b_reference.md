# Stage 2b's frozen reference

Written down and frozen before the reference ran on any world (2026-11-06). The code is `lab/stage2b_reference.py` (the arm `ref` in
`lab/stage2_lang/arms.py`), a subclass of `lab/stage1c_arms.py`'s `Mix`, unchanged. Hashes at freezing are at the end. Before this, it was
run only on synthetic calls with no world (3000 ticks of random tastes, to see that it runs). Any change to it is a new reference, judged afresh.

## Where it comes from

Stage 1c's widest learner (`discrete/NOTEBOOK.md`, D32, the swap10 table's last row: "the same, with HMMs and the seven", 15.2 bits on
swap10's truth), at the settings stage 1c ran it with (`lab/stage1c_change.py`, `hmm()`: e .1 chosen on swap10's tuning seeds, shares a third
each, the default's prior .6, eight HMM rates, 393 periods by 16 phases). It is the widest family stage 1c measured, and the only one there
that holds both a fixed rule, a changing rule with unknown rate, and a periodic rule.

**The one adaptation: the tie rule.** `Mix` follows sensor 1 when the vote is above .5, so an exact tie went to sensor 0; D32 found a
Bayesian reference's result can rest on its tie (alternate 1.93 or 2.22 by the tie's direction). Here an exact tie (within 1e-12) keeps
the colour followed before that taste. Nothing else is changed.

**Not adapted, on purpose.** I considered and did not add: a mixture over the lie rate (it would be more Bayesian, but its grid would be
chosen with this stage's worlds in view); a coin hypothesis with a decision to stop eating (a world with nothing to learn has no gap, so
stopping never enters a pass, and D32's stopper stopped wrongly in alternate); hypotheses about place, the body, the eyes or the score.
The language's worlds that the family doesn't hold are judged at the pass rule's floor (.25), which `PROGRAMME.md` says errs towards no.
Hypotheses reading the clock and the brain's own meal history run in every world of the language as they are, since they read only
the brain's own variables.

## Its family of hypotheses, and its prior in bits

Every hypothesis says, at each moment, which of the two sensors is the food colour's. Three groups, a third of the prior each:

| group | hypotheses | prior of one, bits |
|---|---|---|
| the bank's seven models (`universal_v.py`), fixed for the life: 1/3 the default, 1/0, 2/2 ... 6/2 | 7 | default 2.32 (.2); each rival 5.49 |
| two-state hidden Markov chains over which colour is food, switching at rate lam a second, lam in .01, .02, .05, .1, .2, .5, 1, 2; the starting colour at .5 within each | 8 | 4.58, and 1 more for a starting colour |
| periodic swaps: period T = 2 x 1.01^k s, k = 0..392 (2 to 99 s), phase j/16 of a period, j = 0..15, either starting colour | 12,576 | 15.20 |

12,591 hypotheses in all. The prior bits don't count the choice of family itself, which is mine (D32's caveat).

## Its likelihood

Only the bank's scored tastes are evidence (the bank's own body decides which tastes are scored: vouched, out of the open phase, not a
soon taste while pausing; `bits_bank.Recorder.about`). A scored taste says a colour y: the colour followed was food if the taste was good,
the other if bad. A hypothesis predicting colour c at that moment gives P(y = c) = 1 - e, P(y != c) = e, with e = .1, independently of
every other taste. Each hypothesis's prediction depends only on the brain's own past and the clock, so the policy's factor cancels and the
posterior is exact for its family whoever drives. HMMs are filtered exactly between tastes; the first bad taste, ending the open phase,
is a taste too (all seven agree on it). Independence of lies is a stated model, not a fact (D31: disagreements come in runs).

## Its decision and tie rule

It drives with the bank's body and parts (eyes, vouching, pauses, the open phase), its own model choice switched off. After each taste it
follows the colour with the larger posterior predictive probability of being food (the posterior-weighted vote over all 12,591), and
re-reads the clock every 5 ticks so periodic hypotheses can turn without a taste. On an exact tie, within 1e-12, it keeps the colour it
was following before that taste (or tick). It never stops eating.

## What it is not told

The world's rule or which world it is in; the wiring of colour to sensor and motor to thruster; where blocks are; its position, heading
or speed; the lie rate (e is fixed at .1 whatever the world); the life's length; any pause a world states (`told-wait`); anything the bank
isn't told. It is told only what the bank gets on its three wires, and its own clock.

## How r and "nothing to judge" are computed (fixed now)

Per world, on the same seeds and pairs: base (the circuit), bank, told (the bank's parts told the colour; with the stated pause where a
world states one, `vtoldw`), and the reference. Efficiency is a ratio of sums over lives; each bootstrap draw resamples seed pairs, a
seed's two lives together, 2000 draws, the same draws for every arm.

- floor = max(base, 0); gap = told - floor; x = (bank - floor) / gap; r = (ref - floor) / gap.
- **Nothing to judge** if the gap's 95% interval reaches 0 (told and the floor within noise), or the gap is below .1 (the doing-no-harm
  scale, where x's se exceeds about .8 at 60 pairs). Such worlds get no x and no r; they are counted apart (and are doing-no-harm tests).
- **A pass**, for a world with something to judge: x > max(.5 r, .25), on point values, with x's and r's 95% intervals beside it.
- **The reference closes the gap** where r's lower 95% bound is above .25 (it surely does better than the floor's bar); "learnable in
  principle" in part 3 means a gap exists, and "the reference can close it" means this.

## Frozen

SHA-256 at freezing (before any run on a world):

- `lab/stage2b_reference.py`: see `lab/v/stage2b_reference.sha256`
- `lab/stage1c_arms.py` (Mix): see the same file
