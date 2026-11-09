# Open questions

What we'd like to know and haven't tested, roughly most valuable first. A question raised mid-quest is parked here
rather than chased; one answered leaves, its answer recorded in its line's notebook. Each: the question, who raised it
and when, why it matters, the line it belongs to, and the experiment that would answer it.

## The plan (the user, 2026-10-29)

1. **Which level to think at**: done for B (`discrete/NOTEBOOK.md`, D14): blocks fastest to design in and realised
   faithfully below; gates cheapest (8 times less power than Sepulchre's elements); Sepulchre's elements the knobs.
   The user's choice (2026-10-29): blocks for now, the fastest to iterate in.
2. **Then, at that level: how can a brain know it isn't doing a good job, and compensate**, by tuning itself or by
   recruiting more neurons? Testbeds: adapting to the body, and spending (both below). Tuning towards better
   outcomes (food or sightings per firing), never to a setpoint: no internal clock is better than its parts, and the
   body is no reference (AGENTS.md). First: spending, knobs mistuned at birth, a hill-climb on meals per energy
   spent, lives of 2,000 s, against the floor (fixed, mistuned) and the ceiling (fixed, searched).
   Since (D15): a tuner with no coordinator (each knob wiggling at its own moments against a broadcast "better than
   usual") closes a third of the gap from floor to ceiling in 10,000 s, ties a Bayesian optimiser given the same
   information and unlimited computation on lopsided bodies and beats it on the standard one; annealing hurts.
   Within a life, perfect is local. Slope-following, so it could stall on a plateau or a local peak.
   Shadows that compete (the user's idea) were tried for the hold and failed (D15): off-policy judging needs a choice
   whose alternative leaves what is seen unchanged, and stopping a drive changes it.
   **Layers that learn how to learn** (the user, 2026-10-30): front-line units experimenting (combinations of inputs,
   outputs, timescales), units behind them judging the results and turning knobs, and perhaps more behind, since how
   fast to turn the knobs is itself to be learned (with few signals, slowly). D15 already shows the second order
   matters: a tuner's rate 0.03 was worse than none, 0.01 best, and lopsided bodies (a steep knob) wanted faster than
   spending (flat ones). Known local forms: each knob its own rate, raised while its successive steps agree in sign and
   lowered while they alternate (delta-bar-delta, Jacobs 1988; IDBD, Sutton 1992); the rate as the ratio of uncertainty
   to noise (a Kalman gain; people adjust their learning rate to a world's volatility, Behrens et al. 2007);
   neuromodulators as such meta-parameters (Doya 2002: acetylcholine the rate, noradrenaline the exploration). Each
   layer up needs more experience to judge, so the tower is short: a top layer fixed by evolution. Since (D15):
   delta-bar-delta per knob gained nothing (with a fresh memory every rate ran away; delayed beyond the steps'
   correlation, the rates stayed put). There was no headroom (a faster balance by hand loses), and the rate chosen on
   training seeds is the same, 0.01. In a world with a third of the blocks (D15) no rate recovers much (0.32 against
   the floor's 0.29; B's untuned knobs 0.45), nor do windows three or six times slower (0.34, 0.30): the
   information, not the rate, runs out when meals are sparse; food sightings weighted more don't help (heavily
   weighted they hurt). Open: a proxy for spending, seen every moment, that tracks meals.
3. **Can a brain learn tricks nobody designed?** (the user, 2026-10-29) An omniscient brain's mapping is too godlike;
   instead, a grown network always "wondering about times and sequences" (a hairball of random delays and sequence
   detectors), each part keeping a fading tag of its recent activity, so that when taste reports food or poison the
   still-tagged parts are credited: "THAT's the trick that worked". Known as reward-modulated learning on a
   reservoir: eligibility traces and three-factor rules (Sutton 1988, TD(lambda); Izhikevich 2007, the distal reward
   problem; Fremaux and Gerstner 2016; synaptic tagging, Frey and Morris 1997), random recurrent networks with fading
   memory (Maass 2002; Jaeger 2001; Izhikevich 2006, polychronization), the cerebellum's expansion and error signal
   (Marr 1969, Albus 1971). In blocks: a slow tag node and a write gated by taste per part. Slow (sparse, mostly
   unearned meals: long lives); taste's broadcast is legal in a circuit. Tricks to
   find: a lopsided body's steering (credit the motor patterns before meals), sweeping back for a block just lost,
   and ones we haven't thought of. Phase 2's recruitment route, after self-tuning on spending. Since
   (`discrete/NOTEBOOK.md`, D16 and its continuation, 2026-10-30 to 11-01): random detectors learned by taste rescue
   a lopsided body without steering it; a planted right steer pays and is learned from meals with one exploring coin
   per burst, but among random detectors little is found (50 reach 0.24 against the planted steer's 0.70 in 100,000 s lives). Open: why, against the bounds below.
   **First, the bounds** (the user, 2026-11-01; the theory in `BOUNDS.md`): what could an ideal observer do, granted
   every node of a primitive brain that is failing? From lives: meals' spread per unit time on each body; Delta for
   the planted steer and for a sample of random detectors at fixed odds, learning off; how much each detector's
   natural firing predicts meals with nobody exploring; the bits per second taste carries about the body; explorers
   per credit window. Each kind of trick then sorts into learnable from meals, learnable only with free signals
   (prediction), or not within a life (evolution's), telling steps 3 to 5 where to look. Plan (2026-11-01): an exact
   Bayesian ideal observer over the body's wiring and strengths with B's knobs as its levers first; a strong learner
   (a network, trained across lives as evolution, run within one) only if a large gap remains; then the cheapest
   process reaching most of the best one's gain.
   Since (`discrete/NOTEBOOK.md`, D21): the first yardstick, the seer told places only as well as pulses tell
   them, says a memory of where blocks are adds little over B (2.8 at best against 2.54) because the eyes don't say
   where across their corridor a block lies. Open: is that offset worth getting by moving (active sensing), and what
   would an ideal observer that senses actively reach? Next (the user, 2026-11-01: let it emerge, not forced; time is
   where a small brain computes, `BOUNDS.md`, Time): does a tiny dynamical circuit evolved in the loop (Beer 2003;
   Sepulchre's motifs) scan and steer by the phase of its pulses, and what of that could a life learn? First, whether
   the minimal search's evolved circuits already do. Since (D22): none do; an evolved network didn't either, and these
   eyes and this body don't offer it (the pulses' timing carries little about a block's offset even when probing, and
   no wiggling policy used what there is). **For the user**: the headroom (B 2.5, a perfect
   memory of seen places 4.5) needs information across the corridor; an eye split across it (left and right halves
   for each colour) or finer turning would offer it. A body change, the user's to decide. The yardstick values a
   split eye at 3.95 (the range roughly known) or 3.15 (not), against B's 2.54 (D21). Since (D24, prepared, the body
   unchanged): with a split eye, B plus a reflex of a few parts (steer towards the half that lit, by a beat with its
   partner 10 ms later, 7 degrees; which motor is which learned from its own scan) reaches 3.02 against 2.49 held
   out (+21%), 2.71 against 2.32 on lopsided bodies told their balance. Finer turning needs no body change (timing
   gives it); the split eye does. Yours to decide.
   **Rhythm by mode locking** (the user, 2026-11-01): oscillators entrained to each other, each at half the last (a
   binary count of a signal's period); if the signal's period is 1.5 times one of theirs, can that emerge? Nonlinear
   oscillators lock at simple ratios (3:2 among them; Arnold tongues, widest for the simplest), and a bank of them
   resonates at a rhythm's period, its multiples and simple ratios (Large's neural resonance: Large and Kolen 1994;
   Large, Almonte and Velasco 2010). A repeating mismatch (the signal at phases 0, 2/3, 1/3 of an oscillator) is
   structured surprise, where a grower could recruit an adaptive oscillator that tunes itself to lock; a bank summing
   each period's multiples is D20's subharmonic summation in oscillators. Locking needs many cycles of one rhythm
   (D23), so test on long steady sweeps: does a bank find the period with fewer parts than D20's 192 counters?
   Since (D23): on 60 s spins, 96 resonators with harmonics summed read the period sooner than the histogram but
   plateau lower, for as many parts; entraining limit cycles did worse. Open: a ternary recruit grown on structured
   surprise, and rhythms with one partner over many cycles (a gait, the arena's pursuits).

4. **How can a brain realise it isn't solving the problem, and recruit more neurons to do so?** (the user,
   2026-10-30: the most interesting question; work through several cases until the generic answer shows.) At the
   block level, growth the one declared primitive, judged robustly with all-food lives as the control, no SPICE or
   physical plausibility until a case works. A candidate generic answer, to test case by case: predict (units learn
   what their own signals say about outcomes, through fading tags); notice the gap (frustration: a bad outcome
   predicted and happening anyway; no reference outside the brain); experiment there (grow experimenters attached to
   the predicting signal, not at random as in D16); keep what helps (credit through the tags), prune the rest; stop
   when the predicted bad outcome stops. A case must be one the brain can't solve whatever the tuning of its parts
   (the user, 2026-10-30: the XOR problem for one layer), so that only new structure helps. Cases: (1) taste wired to
   nothing (B without its learning; the recruitment series' rung 1 went one step easier, the prediction already wired:
   `experiments/NOTEBOOK.md`); (2) left and right in the eyes, with no path from side to motor (a body change: the
   user's decision); (3) a conjunction, a colour's meaning depending on another signal (a world change: the user's);
   (4) a memory or timing the brain can't hold. (A lopsided body is not one: one more knob, a gain per motor, solves
   it, D15.) After each: what did the grower need that it didn't have?
   Kinds of growth (the user, 2026-10-30): a path where there was none (case 1), a knob where there was none (a
   lopsided body), a decider where the existing one can't compute the answer (XOR), and perhaps a memory. Worlds that
   demand them (the user's ideas): blocks overlapping is a trade-off a weighted sum solves, but pairs that mean
   something other than their parts (red and blue together food, either alone poison) are XOR; food behind poison
   (the rays stop at the first block, so the food is hidden while faced) needs a detour, so a memory of where the food
   was, which B lacks; then clusters, food that drifts. Certify each world first: B's knobs searched robustly can't
   solve it, and a scripted policy with the extra structure, on the same body and eyes, can.
   Since (D17): case 1 works: grown in every poison life on the poison eye, in no all-food life, tied with B's
   designed learning (1.80 against 2.01) once the recruit tries every operation before keeping the best (win-stay
   alone settled on the first improvement). A menu that doesn't already hold the answer: done in the arena (D18):
   two knobs (each motor's rate in the response) tuned by per-bite perturbation reach 86 to 97% of the best scripted
   reflex.
   Since (D18, the arena): escape from bites works, a path where there was none (taste to motors) for pain no sense
   predicts but an action stops (the user's case): grown in every life, a turn kept in 97%, three quarters of the best
   scripted reflex, judged held out; in the control (pain no response stops) its gain vanishes and its choices fall near
   chance. What it needed: a predictor comparing what follows a sense with what comes anyway, and judging each try at
   once (lives of 96 s leave no room for trials). Steering grown failed to pay (the wrong sign's trial costs what the
   right one gains), and the user judged the colour and the wiring evolution's here. Next case, candidates: (a) the arms
   race in the arena (step 6): escape frustrates the biter (a good taste ended by nothing it did), so the same grower on
   the biter's side, growing pursuit of a turning tail; (b) a decider: some robots' tails bitter (a body trait,
   differing between robots, shown by colour pairs), so whom to chase is a conjunction; (c) a memory: a robot bitten
   recently is likelier bitten again (a hunter nearby), so the right response depends on the recent past. (a) tried
   first and failed its certification: no scripted response to a bite ending pays (D18), so there is nothing for the
   biter to grow. (c) failed too: no response to a recent bite (keep moving, keep still) pays (D18). (b) changes the
   world (the user's to decide). Since (2026-10-31): the robots are discs, and firing is now charged (it wasn't: every
   arena figure before ignored it). Escape still grows and pays against the plain tracker (+0.14 a 10 s), but against a
   tracker with its standing policy tuned for the arena only +0.03; (a) and (c) still fail; the best standing policy
   depends on the population (keeping still pays among escapers, costs among trackers). The arena, as it is, has
   little left for a life to learn. Open (a world change, the user's): inheritance in the arena (newborns taking the
   standing knobs of the best-fed, mutated), to see where the arms race settles and whether in-life growth pays there.

5. **Learn from predicting, not only from taste?** (the user, 2026-10-30, after the neocortex's columns: Mountcastle's
   repeated column; Hawkins' Thousand Brains theory, 2021: some 150,000 alike columns, each modelling the world from
   its own sensory and motor activity, voting on the best.) Every limit found today is information: meals are
   sparse (D15, D16). A column learns from predicting its own next input, a signal all the time, and reward has only to
   choose among models already good. Here: a unit predicting what its eyes do after its own motors' beats (a turn
   moves a block across the gaze) could learn a lopsided body from every beat, not from meals; units with different
   hypotheses (delays, which motor) voting by how well each predicted. Questions: is the repeated unit a neuron or
   something column-sized; does two pulse streams in and two motors out leave enough to predict (the
   body's bandwidth: the body question above). (Steering by a model learned in the life is allowed: the goal, "keep
   what is chased ahead", is the same in every life, so evolution's to supply, and no property of the body is the
   reference; the model of this body is the life's to learn.) Experiment: case 2 of step 4 both ways, from taste
   alone and with prediction.
   Since (D19): a first step, not yet prediction: the lopsided body's balance jittered at each drive and judged by the
   food pulses that drive saw (a fixed proxy, every drive a lesson) closes 40% of the gap in 2,000 s held out, surely
   above D15's meal-judged tuner (+0.26 [+0.07, +0.45]). Its limits: the jitter's own cost on a steep knob, and lives
   that strand before they learn. Then (D20), prediction proper: what it sees comes round again once a revolution
   while one motor turns it, so sweeps of its own and coincidence counters find each thruster's strength: 83% of the
   gap closed held out, surely above every outcome-judged learner; 8 s sweeps cost 0.18 on the standard body, a cost
   gone when it sweeps only while frustrated (fewer than 8 meals in 32 s: 2.47, tied with B; lopsided 1.68), and,
   sweeping from birth and more often until the evidence is in, 93% of the gap (1.81). Open:
   B's own scans made usable; the same idea in the arena; and a circuit for the counters and the period-finder (a
   delay line of coincidence units, the largest winning). Since (D20): 96 log-spaced counters, chance from their
   neighbours and a fixed comb tie the exact histogram held out, so the open part is the delay line holding a
   sweep's pulses for up to 8 s; each stage need hold only up to 3 pulses (tied with the bank held out; one-bit
   stages lose 0.14 on lopsided bodies); 192 counters with such stages tie the exact histogram held out on every body
   (lopsided 1.93, 88% of the gap). Open: those blocks in transistors.

6. **An adversary instead of hand-made worlds** (the user, 2026-10-30, after GANs: food and creature out-thinking each
   other). Known as self-play and arms races (Sims 1994; POET, Wang et al. 2019; PAIRED, Dennis et al. 2020). The
   pitfall is an adversary that makes worlds no brain can solve; PAIRED's fix is to reward it for regret, how much
   better a stronger brain with the same body does than the simple one, which is this plan's certification
   (step 4) automated. Two flavours: across lives, an adversary setting world statistics (guards, clusters,
   pairings, drift) to maximise the regret between B and a richer brain (told the colour; with a memory); within a
   life, blocks with small brains of their own, co-evolved, acting only through the world and sensing only what a
   block could (never the brain's insides). With today's eyes it may mostly find what the eyes can't see: itself an
   answer to the body question. First: the across-lives adversary in the fast model, CMA-ES over a few statistics.
   With the same brain and grower on both sides (the user, 2026-10-30), an adversary that wins is our approach
   winning, and each side's improvement frustrates the other: the arms race as the engine of recruitment. Conditions:
   matched bodies (a win must come from the brain, not speed or eyes); no total wins, which end the race by silencing
   the loser's signal (balance, opponents drawn from past versions); progress measured against a frozen gallery of
   past opponents (self-play can cycle). The roles: food wants not to be eaten (flees), poison wants to be eaten
   (approaches, mimics food), so the creature must tell them by behaviour: a decider, memory, prediction. Smallest
   start: the food a creature (B's brain, the grower, an urge not to be eaten), the poison fixed.
7. **Map every way a brain could change itself, then a universal circuit** (the user, 2026-11-02: even the simplest
   body, world and brain offer a rich set of interventions; map it logically, with discipline, then perhaps one
   circuit that can do them all). The map so far is `PARTS.md`: what changes (state, tune, modulate, rewire, prune,
   duplicate, add), which part (a catalogue by what it does in time, all made of feedback loops of either sign at
   several timescales, delays and coincidences), when (each change's local trigger) and how it is judged (its
   fastest credit signal: the brain's own movement in seconds, a missed prediction in tens, outcomes in 10,000 or
   more). Open: what signal says "no setting of these knobs will do, a new kind of part is needed" (a plateau told
   from a ceiling); which parts can be judged faster than meals (those worth adding); and whether one free unit, a
   node of the grammar's elements inserted at zero effect, can become each part by local rules. First, the map's
   test: express every working brain here (B, D20's balance learner, D24's steer) in it, with each part's
   cost in SKY130 and the signal that could have tuned it; a brain that doesn't fit shows what the map lacks.
   Since (the user, 2026-11-02): done as stories, one per performance issue (`STORIES.md`), general observations after
   several, and the universal circuit only if they earn it. Done: which colour is food (D25); unequal thrusters, block level (D26: 192 counters still far from the simplest);
   the table of rows (D28; `STORIES.md`), judged; a universal circuit, the bank of predictors (D29), judged, partly a success.
   Open from D29, most valuable first: re-validate it in `mixed_feedback.py` once kept; what could add a model to the bank, or say that it holds none that fits (a bank is
   still a menu: taken up as stage R, `PROGRAMME.md`, which also answers part of step 3's hairball of delays and sequence detectors, now scored on every taste rather than credited by meals); swap 50 s, where it costs surely, and the untraced half of swap 10 s's shortfall; a relative shortage in place of the absolute gate; sweeps in place of jitter; the bank's cost in parts, and whether tables can share a counter;
   noisy eye + thrusters at long lengths; whether eye thresholds and balance can share one on-policy loop;
   the ladder of harder tests (D27): swaps, sequences, digest, one brain choosing cures. Open from D27: a clock told the period (is it the estimate or the phase?); undoing a growth that didn't help;
   a brain that knows it has no cure; re-validating the ladder at component level; this patch is empty; how fast to spend (the likely
   honest negative). Open from D25: what would tell a world where nothing can be learned from one merely hard? In it
   the circuit flips 16.5 times a life where doing nothing scores best.

8. **Left over from stage 1c** (`discrete/NOTEBOOK.md`, D32; 2026-11-05). What does the floor's gain consist of: forgetting, or undoing its own -3? Ablate rivals to see. Could a circuit hold a family of periods at about 13 bits, the one thing that closed half of swap's gap? Can a bank learn the lie rate, since every mixture is fixed at one value? Is there a tighter proof of the limit on tastes, and should the body have a firing cap at all? Can q=.7 ever reach a yes?

## The body (`NOTEBOOK.md`, The body)

- **Would evolving the body pay more than evolving the brain?** (the user, 2026-10-30) Every limit found so far is
  information: sparse meals for tuning (D15), a far block one flash as the gaze sweeps past (README, Match the
  brain's speed to the body's), and the ceilings (D13: omniscient about 20, a perfect memory 4.5, B 2.5). Sharper
  or wider eyes might buy more than any brain. A body change that adds information differs from one that does the
  brain's work (credit assignment, filtering, timing: never, AGENTS.md); and the body's organs are the user's ground
  rules, so any such experiment is the user's decision. Experiment: the ceilings and B with eyes of several widths
  and resolutions, each eye's cost (its pulses) counted, against a brain made cleverer.

## Discrete circuits (`discrete/NOTEBOOK.md`)

- **Can a brain adapt its reflexes to its body?** (the user, 2026-10-28; the body left as it is, 2026-10-29: learning a
  lopsided body likely takes more than a life, and better eyes) Open: with each thruster 0.5 to 2 (`bodies.THRUSTERS`),
  the best fixed design (B) falls from 2.38 to 0.32, 11% stranded (D13). First the best fixed design searched on such
  bodies (robust judge); then a brain that tunes itself in its life (its drive's balance between thrusters, its rates),
  each unit from its own signals; the gap between them prices adaptation. Since (D13): the oracle (told its body, the
  drive balanced) gets 1.92 held out (2.15 with the drive started in step, D20), the best fixed design 0.76; tried and
  short of it: extremum seeking (about 0.5), re-find time as a sign, sightings per firing, sweeping back. Next ideas:
  the extremum seeker with a better reward (the pulse rate rising as it nears); given three lives' time it only reaches
  0.8 (D13), so the signal, not the time, is short. A zigzag within the drive failed (an eye's corridor shows nothing of
  a block's place within it). Since (D19, D20): judging each drive by the food it saw closes 37% of the gap; a model
  learned by prediction (sweeps with one motor, the period of what comes round again giving each thruster's strength)
  closes 93% held out, and, sweeping only while it eats badly, costs the standard body nothing.
- **B's drive starts cleanly, in transistors** (D13; only when B's physical realism matters): the second thruster
  fires alone at a drive's first beat in over half the drives, costing about 20% of its score in SPICE; a latch on
  the beat halved it, but motor A still misses some first beats (its starved inverter, which also drives the
  oscillator, is the suspect).
- **What biology's noise costs at Sepulchre's level** (D14; parked by the user, 2026-10-31: a side-quest done, to return to if it matters): no setting of B's knobs survives biology's noise, but
  size does: four times the capacitance (and currents) on the bit's chain does the job with it for 48 nW. Twice
  biology's noise fails at any size: the inputs' noise (taste, eyes), which size can't reach and faster input leaks
  don't fix. Open: B's doubt with the minimal leaders' bit (a perfect integrator written by seen times taste, where
  noise averages out) in place of a thresholded tally, judged at all three noises.
- **Can a memory node take the sized balance learner's small writes?** (the user's question, 2026-11-08, on noise; D36, v6-v7) The
  learner's balance moves in steps down to .0125 and its wobble down to .05 (v6) or .005 (v7), plain numbers in the block model. Silicon's
  noise is far below them (a memory node is still unless written, its write rough by one electron an event), but a write below
  `chip.DEAD` (1% of its full current) doesn't tunnel at all. Whether the smallest steps survive depends on how the write is built: for
  the re-validation in `mixed_feedback.py`.
- **When should a block explore at all?** (main session, night of 2026-11-08; D36, the cure in 100 s lives) In plain a wobble of .05
  costs 11% of the food, and a drive's outcome needs about 1,400 drives to show it; a 100 s life has about 96. The sized learner pays
  back in long lives (judged on their last third, so early exploring is nearly free) but costs .6 at 100 s; the old bank's fixed gate is
  safe at 100 s only by never wobbling, and is a rate the body supplies. What local evidence could tell a block, early, that its balance
  is worth exploring: a sign of lopsidedness that needs no wobble (none found yet: a drive's length is unsigned), or a rule weighing
  the wobble's cost against the life still ahead? Experiment: in the thrusters and plain at 100 s, the information per drive about
  |right| available without wobbling, against the 96 drives a life gives. The thruster line is closed (the user, 2026-11-09); what is
  left is the floor: the least an ideal learner pays to tell plain from lopsided, at 100 s and 10,000 s, solved on a small surrogate
  of the drives (the outcome's mean and noise against the balance, drives a second, the cost spilling into later drives), checked
  against v7's lives, rather than by more lives. And whether "do no harm" is then judged against that floor (the user's decision).
- **Can surprise teach before reward, and is that attention?** (the user and main session, 2026-11-09) A world whose consequences
  come only after a sequence of actions (a block that turns to food after the right moves) shows almost nothing to a first-layer
  learner: one action's correlation with food is near zero. A second-layer unit that notices "this sequence changed what I see",
  before any food, has a much denser signal; attending to what surprised it narrows what to try. Talk the world through first,
  as simple as possible (the user).
- High-value resistors (500 MOhm to 1 GOhm) are rarely better than 5% and leak across a board's surface: the bipolar
  circuits' 1% (`life.TOL`) was optimistic.

## Every brain

- **How much could a clever brain gain?** (the user, 2026-10-28) A ladder of ceilings on the same lives, each a policy
  in Python (a second a life or so): omniscient (knows every block and its own body: the absolute ceiling); a mapping
  brain (legal inputs only, but unlimited memory and thought: it learns its body, integrates its own path from what it
  fired, takes a bearing from its heading and a range from the pulse rate at each sighting, keeps a map and plans);
  short memory (where it last saw food: object persistence, below); the best reactive policy (2.3-2.7); our circuits.
  The gaps price each ability in meals, so they say which are worth a brain's cost, and which small circuit (a ring
  attractor for heading, as in insects' path integration) would capture most of it. Done: the omniscient rung, a
  crude one, about efficiency 20 and 58 food per 10 s (`discrete/NOTEBOOK.md`, D13): ten times B. Next the mapping
  rung. A short memory (the heading where food was last seen) is worse than none: a heading without a range rarely
  points at the block (D13); learning the colour costs B only 0.15 against being told it. The seer (a perfect map of
  what it has seen) gets 4.5: intelligence is worth at most about twice B here, the rest (to 20) is the eyes' coverage.
  Open: a mapper that infers places from pulses (ranging by moving) to see how much of the 2x a real brain reaches.

## The minimal search (`minimal/NOTEBOOK.md`)

- **Object persistence** (the user): a creature that has just lost sight of food sweeps back for it (the body can
  turn both ways); the bottom rung of the ladder above.
- **Reversal**: every minimal circuit learns only from food, so none unlearns when the poison colour swaps. The
  discrete line's B (doubt a bounded tally) reverses well (D13): its doubt could go into a minimal design.
- **A smaller robust circuit still**: the open search again, from HR_31p_pol_pruned.
- **Sepulchre's discipline**: do circuits of mixed-feedback components (every node leaky, events from positive
  feedback) do the job as simply? The first three-arm experiment settled nothing (`MIXED_FEEDBACK.md`): it needs a
  start built of his components.

## Recruitment (`experiments/NOTEBOOK.md`)

- **Recruitment under biological noise**, on a neuron that survives mismatch; de-recruitment (retiring a recruit
  failed in every form, H11); a recruit that walks (`RECRUITMENT.md`).
- **Level 1 has no rules** (the user, 2026-10-20): the parts built from nodes and elements are invented as needed,
  about eight unnamed kinds (`experiments/NOTEBOOK.md`).

## Self-optimisation

- **The project's real goal: self-optimisation from local signals.** Every unit a fast bistable and a slow
  integrator, each slow variable outlasting the loop it closes, each tuning its own time constant from its own signals
  (D13).
