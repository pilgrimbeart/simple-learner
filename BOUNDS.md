# Bounds

What limits how well, and how fast, any brain could learn in a life, however clever: the information theory and
decision theory behind the ideal observer (the user's line of thought, 2026-11-01, after David MacKay). Gathered
from memory of the literature, not a fresh search; check details against the sources before relying on them. The
question this serves, and the plan, are in `QUESTIONS.md` (step 3, the bounds); measurements will go in
`discrete/NOTEBOOK.md`.

## The ideal observer

A brain of unlimited reasoning that has only what a real brain has: its senses, its own beats and its tastes
(Geisler's ideal observer analysis, from vision science; README, Terms). Not omniscient: it never sees the world or
the body. What it could do bounds what any brain could learn, and comparing a real brain with it says how much of
its shortfall is the brain's fault.

- **Seeing every node adds no information about the world.** Each node is a function of the senses, beats and
  tastes and of its own noise (the data processing inequality). Seeing the nodes tells the observer only where to
  intervene, and lets it read natural variation without exploring.
- **Its value** is a Bayes-adaptive POMDP's: a perfect belief over the unknown body, kept from what it senses, and
  the action best in expectation. It lies between B and the policy told the body (`pb_oracle`).
- **What it learns across lives is a prior, evolution's; what it does within one life is learning.** A network
  trained over many lives and run in one is both, and its result must say which part is which.

## Watching and intervening are one problem

- **Pearl's ladder**: watching gives associations, intervening gives causes. Watching suffices where nothing hidden
  drives both the variation and the outcome (no confounding), and where the brain sometimes does the thing to be
  judged (overlap, or positivity: if it never turns left, no amount of watching says what left would do).
- **The brain's own noise is a free randomised experiment.** Noise inside a brain is independent of the world, so
  behaviour it causes is as good as a coin's: an instrumental variable. An observer that sees the nodes can separate
  it from behaviour the world causes, and read causal effects without touching anything (off-policy evaluation).
  The songbird seems to do this: its LMAN injects variability into song, and learning reads outcomes against it
  (Olveczky et al. 2005; Fiete and Seung 2006).
- **When to stop watching and act**: only when a confidence bound says the change beats the present behaviour (safe
  policy improvement: Thomas et al. 2015, high-confidence off-policy evaluation; Laroche et al. 2019; conservative
  bandits, Wu et al. 2016). Choosing which probe to try is experimental design: the most information per meal risked
  (information-directed sampling, Russo and Van Roy 2014).
- **Dual control** (Feldbaum 1960): every action both steers and probes, and the best controller of an uncertain
  system probes exactly as much as the information is worth. Learning first, then acting, is not optimal in
  general. A Bayes-adaptive observer slides between the two by itself: it watches while natural variation is
  informative enough, and injects change where it isn't (no overlap, or too faint).

## How long a life must be

- **One change.** Telling two behaviours apart, meal rates lambda1 and lambda2 per 10 s, with confidence z (about
  3), takes about z^2 (lambda1 + lambda2) / (lambda1 - lambda2)^2 units of 10 s (Wald's sequential test), more if
  meals cluster (measure their spread, don't assume Poisson). A continuous setting is pinned down at a rate set by
  its Fisher information.
- **The best of K.** About a log K factor more (best-arm identification), and trying each costs meals: regret grows
  at least as the log of time per poor candidate (Lai and Robbins 1985).
- **Information depends on behaviour.** A stranded creature eats nothing and learns nothing, so a time measured under
  B's own behaviour is an upper bound; the observer can do better by keeping meals coming.
- **An example** (D16, continued, stage 13): the planted right steer ate 3.7 food per 10 s and its wrong twin 1.0,
  so about a minute tells them apart. The learners took 10,000 s and more: the limit was the learners, not the
  world. But 200 random candidates take about 12,000 s to try once each, about where those learners failed; and a
  life of 100 s allows about one such test, so within a judged life most of a trick must come from a prior.

## The walls

Learning doesn't degrade gracefully past these; it stops. A negative result beyond one says nothing about the
mechanism (AGENTS.md, Mind the noise wall).

- **Too little signal for the life** (Shannon): taste carries at most so many bits per second about the body. If a
  life ends before enough arrive, no learner finds the change. Track signal to noise per second for each candidate,
  Delta^2 / sigma^2, against the life's length.
- **Credit interfering** (one score for a group effort): a taste reaches every unit at full strength, but it is one
  number about what they all did. To a unit trying a change, the others' changes are noise, so with N varying at once
  each needs about N times as many tastes to see its own effect; taking turns costs the same. This slows learning
  gradually, once their combined variation rivals the world's own luck; it isn't a cliff, as an earlier form of this
  note's comparison with ALOHA's packets implied. It doesn't bind where every unit needs the same fact, and idle units
  add nothing. D16's collapse (20 random detectors about B, 50 and 200 at -0.65 and -0.84) had other causes as well: the
  direct harm of exploring, and a floor on what was learned that turned noise into growth. Track explorers per credit
  window.
- **Too little room to store it** (Cover 1965; MacKay, chapter 40, below): a unit of K weights read by one threshold
  holds about 2K bits, with a sharp edge. For a random reservoir this wall is far off: meals deliver far fewer bits
  than its weights can hold, so the binding wall there is Shannon's.

## Time

(The user's insight, 2026-11-01.) The sums above count meals and pulses per second, averaged: a world without time,
like the deep networks' mappings. But a small brain's computation is its timing, and where a block lies across the
corridor is carried by when a pulse comes against the creature's own movement, not by how many come (`discrete/
NOTEBOOK.md`, D21: across is what the seer's lead needs, and counts barely give it).

- **Active sensing reads phase.** A rat's whisk sweeps its whiskers, and the moment of a touch within the sweep tells
  where the object lies (Szwed, Bagdasarian and Ahissar 2003; Kleinfeld and colleagues). A nematode swings its head
  and reads what it senses against the swing to steer up a gradient (Iino and Yoshida 2009); a moth casts across a
  plume. B's scan is a whisk already: a block's offset across is in the scan's phase when the eye pulses, read by a
  coincidence between the two (the primitive of D16's detectors and D20's counters).
- **The dynamics can be the perception.** Agents of about a dozen continuous-time neurons, evolved, scanned back and
  forth to tell circles from diamonds and catch falling objects, with no representation of the object: the
  perception was in the loop through the world (Beer 2003). Sepulchre's circuits (fast positive and slow negative
  feedback; bursting, half-centre oscillators) are that idea in physical parts, with knobs that move timing.
- **So reckon bounds on timing.** The information about a block's offset is in pulse timing against the creature's own
  beats, at milliseconds; a bound from counts understates it. And credit by meals, slow and averaged, can't judge a
  trick that is right within one sweep; prediction, on the sweep's timescale, can.

- **Learning to dance, not to solve a chess problem** (the user, 2026-11-01). A chess player searches positions and
  chooses; a dancer has a rhythm, couples it to a partner and the music, and practice shapes the coupling (coordination
  dynamics: Kelso's coupled rhythms locking into phase; Thelen and Smith's infants learning to walk; central pattern
  generators reset by what the body senses). So the unit of behaviour is a rhythm, not a choice: a pulse nudges the
  rhythm's phase (its phase response), and learning shapes that response and the coupling. The teacher is timing
  error (the next pulse came early or late), on every sweep, not meals; and probing and reading are learned
  together, by entraining, coarse then fine, which crosses the valley that separate steps can't
  (`discrete/NOTEBOOK.md`, D22). But entrainment needs a long dance with one consistent partner: an oscillator must
  lock its phase before its frequency can learn, and with a few cycles and several partners at once (D20's sweeps:
  4 revolutions, 5 blocks each) it never locks; a phase-free statistic (intervals, against chance) wins there (D23).
- **Timing is also an output's resolution.** A body's actions can be finer than its smallest act: a thruster beat
  turns the body 18 degrees, but its partner beat one tick later cancels all but 7, so a graded turn is made by when
  the beats come, not by a finer motor (D24, where it turned a losing steering reflex into a 21% gain).

## MacKay's chapters that bear on this

From *Information Theory, Inference, and Learning Algorithms* (MacKay 2003, free online).

- **Chapter 40, the capacity of a single neuron: about 2 bits per weight.** A perceptron outputs the sign of w.x.
  Given N inputs in general position with random labels, how many of the 2^N labellings can some choice of its K
  weights produce? Framed as a channel: a sender who knows the labels chooses the weights; a receiver who knows the
  inputs reads the labels off the neuron. Each input is a hyperplane through the origin of weight space (weights on
  one side label it 1), so the realisable labellings are the regions N hyperplanes cut K dimensions into. A new
  hyperplane splits as many regions as it meets, the count one dimension down: T(N, K) = T(N-1, K) + T(N-1, K-1),
  so T(N, K) = 2 sum over k from 0 to K-1 of C(N-1, k) (Cover 1965). For N <= K every labelling is realisable. The
  fraction T / 2^N is the chance of at most K-1 heads in N-1 fair flips: exactly 1/2 at N = 2K, and for large K a
  cliff there. So K weights memorise about 2K random labels: real numbers that could hold endless bits pass about 2
  each through one threshold. What a memory holds is set by how it is read, not how finely it is written: for our
  noisy analogue memory nodes, count the behaviours the reading circuit can tell apart.
- **Chapter 19, why have sex?** How fast evolution can acquire information, in bits per generation (faster with
  sex). The other half of the split between learning and evolution: which tricks are a life's to find, and which
  evolution's, by comparing the bits each needs with those a life delivers and those evolution can supply.
- **Chapter 28, Occam's razor**: Bayesian model comparison penalises a rich hypothesis automatically, how the ideal
  observer should weigh a simple account of the body against a rich one without fitting a few meals.
