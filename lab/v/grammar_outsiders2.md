# Outsiders' ideas, round 2 (GRAMMAR.md)

Fresh agents, 2026-11-04, unedited. The first three saw only a neutral description of the creature and one lens; the critic read the draft.

## Mathematics

**Computation and learnability**

1. **Counter food.** After n reds, exactly n blues are food, then n resets (the regular rung below it: strict alternation). Forces an analogue counter, and shows how far n goes before noise makes the brain merely finite. Fits the wires.
2. **Purple XOR.** Add a third colour that lights both eyes: either eye alone means food, both together mean poison. Forces a hidden conjunction unit, because no single-layer weighting can do it (Minsky and Papert). Fits the wires.
3. **Parity with noise.** Taste is the XOR of the colours at a secret subset of the last 8 bites, with 10% of tastes flipped. About 15 bites hold the information, yet extracting it is a search problem, so this forces the brain to bound its effort and give up gracefully. Fits the wires.
4. **Combination-lock thruster.** Thrust is unlocked only by a secret 3-letter word of motor firings, re-drawn each life. Forces structured exploration and sequence generation, not firing rates; longer words become exponentially hard. Fits the wires.
5. **Pebble-free maze.** Red blocks become fixed walls near the percolation threshold, with food in the far pockets. Forces wall-following or better, and tests Budach's result that no finite automaton can search every maze. Fits the wires.
6. **The world as tape.** Near-simultaneous firing of both motors drops a persistent marker the eyes can see, and the marker can be eaten to erase it. Forces external memory: writing, reading back and using its own marks, as with Blum and Kozen's pebbles. Fits the wires.

**Information and coding**

7. **Blind unmixing.** Each eye sees a random, life-specific mixture of both colours. Forces source separation by decorrelating the inputs before any value can be learned. Fits the wires.
8. **Same rate, different texture.** Both colours give the same mean pulse rate, but one colour's pulses are Poisson and the other's are regular. Forces a detector of second-order statistics (interval variance), not of rate. Fits the wires.
9. **Rate-limited balance.** Heading diverges as e^(λt) unless corrected, and is sensed only through a fixed beacon seen in the corridor. The data-rate theorem then demands at least λ/ln 2 bits/s through the eyes, which forces efficient, predictive stabilising and measures the brain's real control bandwidth. Fits the wires.
10. **Silent taste.** Taste carries nothing; poison instead weakens the thrusters for a while. Forces the brain to infer value by comparing motor firings with the sensory change they produce, which amounts to a self-model. Fits the wires, though it does change what the taste wire carries and moves the value signal into the body, so it needs your ruling.

**Topology and geometry**

11. **Holonomy of value.** Crossing one torus seam swaps food and poison, so value depends on the path's parity, not on position. Forces inference of a hidden bit from surprises that track distance travelled, not time. A true Klein bottle alone would change nothing, because the creature's vision has no handedness. Fits the wires.
12. **Value as a map.** Red is food in hidden stripes of the torus and poison between them. There is no position sense, so this forces path integration from the brain's own motor firings, correcting drift against taste. Fits the wires.
13. **Scallop body.** Replace the thrusters with two hinges in a drag-dominated fluid, each toggled by one motor. Reciprocal motion goes nowhere (Purcell), and displacement equals the area enclosed in shape space. Forces a phase-locked gait generator, with steering by the cycle's sign. Fits the wires.
14. **Fractal larder.** Blocks lie on Cantor dust and respawn by preferential attachment, so the world has no characteristic scale. Forces search statistics that adapt across scales, and memory with power-law timescales, not a single leak. Fits the wires.

**Dynamical systems**

15. **Chaotic currents.** A standard-map flow kicks the creature, with regular islands inside a chaotic sea, while energy is still charged. Forces small, well-timed control of chaos (OGY) and riding the flow instead of fighting it. Fits the wires.
16. **Living substrate.** Blocks are the live cells of a Rule 110 or Game of Life lattice, updated slowly, and eating one perturbs the pattern. Forces local prediction of gliders where global prediction is irreducible, and perhaps farming still-lifes over a long horizon. Fits the wires.

**Games and self-reference**

17. **Matching pennies.** Whichever colour the brain has recently favoured turns poisonous. No deterministic policy survives, so this forces deliberate mixing, with noise used as a resource. Fits the wires.
18. **Newcomb blocks.** Blue is food only if the brain's firing rate was low over the 2 s before the bite, whether or not it steered there. Value depends on disposition, which breaks the assumption that a state and an action fix the payoff. Forces credit assigned to its own policy, and a kind of precommitment. Fits the wires.
19. **Multiplicative ruin.** Food multiplies a store by 1.5, poison halves it, and falling below a floor ends the life. The ensemble average and the time average now disagree. Forces Kelly-like risk sizing, with cautious tasting while uncertain. Fits the wires, though the score changes.
20. **Lewis pair.** Two identical creatures share a world and appear to each other as moving coloured blocks. One's experience is visible only in how it moves. Forces following, deception or a convention, and tests whether signalling can emerge with no channel built for it. Fits the wires.

**What this set-up could never test**

- Open-ended symbolic language or composition: two pulse wires and a few dozen tastes carry too little.
- True separations between computational classes: noise and finite lives give only rungs and rates, never asymptotics.
- Rich perceptual invariance, such as recognising objects: the corridor and two eyes never supply high-dimensional input.
- Goals the creature forms for itself: the score is always imposed from outside.
- Inner states that make no behavioural difference, including experience: only behaviour and circuit are observed.

## Development, disease and the brain's failures

1. **Growing body.** Over the life, the disc grows from 2 to 4 mm, the thrusters strengthen, and the corridor lengthens from 4 to 15 mm. *Forces:* continuous recalibration of its timing and steering, with learned settings that don't assume a fixed body. **Fits the wires.**

2. **Amblyopia patch.** One eye is silent for the first 30 s, then opens with normal pulses. *Forces:* competition for circuit that doesn't lock out an unused input, so the late eye can still be learned about. **Fits the wires.**

3. **Sheltered nursery.** Only the food colour exists for the first 25 s, then poison blocks appear. *Forces:* keeping "never tried" separate from "safe", so that eating everything isn't learned as a rule, and calibrated caution towards novelty. **Fits the wires.**

4. **Worn-out memory.** Each write to a memory cell permanently shrinks its range, as with real cell endurance, and the colours flip once at an unknown time. *Forces:* rationing plasticity, by committing when evidence is strong while saving capacity for a late reversal. **Fits the wires.**

5. **Alzheimer-like leak.** Memory retention falls steadily, from minutes to about 5 s, over the life. *Forces:* rehearsal by re-sampling, or holding the bit in behaviour, such as a sustained motor habit, rather than in a failing node. **Fits the wires.**

6. **Stroke.** At a random moment, a random circuit block dies outright, whether a memory, a mixer or a motor driver. *Forces:* redundancy, noticing its own drop in performance, and moving the function to spare or neighbouring circuit. **Fits the wires.**

7. **Parkinson-like decline.** The bias behind motor drive falls slowly by 80%, so firings thin out and start late. *Forces:* compensation that hides the damage. The useful measures are how long that masks the loss, and whether failure then comes as a cliff. **Fits the wires.**

8. **Epilepsy.** Excitatory gains drift upwards until feedback loops run away into motor bursts that burn energy. *Forces:* detecting its own runaway and damping it locally, without a setpoint supplied by the body. **Fits the wires.**

9. **Learned non-use.** One thruster weakens to 10% for 30 s, then quietly recovers, like hemiparesis followed by rehabilitation. *Forces:* compensating for the weakness while still probing the weak side, so the recovery is noticed and used. **Fits the wires.**

10. **Phantom eye.** An eye is severed, then produces spontaneous bursts that look like a near block, some of them triggered by the creature's own firings. *Forces:* noticing that an input no longer predicts anything, then gating it and stopping learning from it. **Fits the wires.**

11. **Taste nerve dies.** The taste wire goes silent at 40 s, while eating continues. *Forces:* separating "nothing happened" from "I can't tell". A rising eye rate followed by a sudden vanishing block shows a meal happened with no taste, so the memory should be protected from false extinction. **Fits the wires.**

12. **Hallucinated taste.** Spurious ±1 tastes arrive at a rising rate, with no block touched. *Forces:* reality monitoring, by giving credit only to tastes that follow an approach and rejecting those that come from nowhere. **Fits the wires.**

13. **Addiction with withdrawal.** A third colour tastes +1 but scores as poison. Its taste weakens with repeated use, and spurious -1 pulses grow until it is eaten again. *Forces:* telling relief from real gain, and overriding the only value signal it has, using its long-run yield. **Fits the wires.**

14. **Demyelination.** Taste and eye signals are delayed, by anywhere from 0.1 to 3 s, and the delay lengthens with recent activity, like symptoms worsening with heat. *Forces:* learning its own credit window and timing, then predicting across the delay. **Fits the wires.**

15. **Sleep debt.** Firings build up a waste that raises circuit noise, and only sustained quiet clears it. New learning also fades unless it is consolidated during that quiet. *Forces:* choosing when to sleep, and spontaneous replay with no input to drive it. **Fits the wires.**

16. **Helplessness and famine.** There is a stretch of unavoidable random poison, or 30 s with no blocks at all, then the normal world returns. A resting creature's narrow corridor shows it almost nothing. *Forces:* estimating how much control it has, saving energy, and waking to sample at a low duty cycle rather than giving up. **Fits the wires.**

17. **Split brain.** The circuit is cut into two halves, each with one eye and one motor, sharing only the taste. *Forces:* coordination through the body and world alone, and resolving conflict when one half steers against the other, like alien hand syndrome. **Fits the wires.**

18. **Tumour.** A growth primitive fails, so recruits keep multiplying, drawing power and injecting noise into neighbouring nodes. *Forces:* local growth control and suppression, with no central monitor deciding what to cut. **Fits the wires.**

19. **Lying hunger.** A new internal wire reports energy reserves, then gets stuck on "full" or "starving", like anorexia or obesity. *Forces:* balancing a drive against evidence from behaviour, and distrusting an internal signal when it conflicts with outcomes. **Needs a wire changed.**

20. **Implanted sense.** At 50 s a new input appears, carrying the bearing to the nearest block in an arbitrary code, like a cochlear implant. *Forces:* absorbing an unknown sense late in life, working out what it means from its correlations, and fitting it into an established circuit. **Needs a wire changed.**

**What this set-up could never test**
- Inner experience: pain, mood and phantom sensation can only be inferred from behaviour, because nothing can report them.
- Language, teaching and shared attention: another creature could only ever appear as pulses or competition for blocks.
- Rich perception: two pulse trains can't carry objects, scenes or categories.
- Competing needs that must stay separate: one signed taste merges all value into a single number.
- Actual pathology: genes, chemistry and drug responses appear only as functional analogies, so a cure here predicts no real treatment.

## Economics, law and society

**Twenty mechanisms**

1. **Random audit:** poison usually tastes 0, and tastes -1 on only 10% of bites, while always scoring -2. The brain must learn from rare punishments set against frequent rewards, weighting a sparse signal by how seldom it arrives. Fits the wires.
2. **Buy now, pay later:** one colour tastes +1 when eaten, then delivers two -1 tastes 8–12 s later, among other bites. The brain must net deferred liabilities against an immediately pleasant payoff, across overlapping debts. Fits the wires.
3. **Insurance with moral hazard:** if motor firing over the last 5 s stays above a set level (the premium), poison costs half and tastes 0. The brain must judge whether cover is worth its cost, and retain or keep learning when insurance mutes its only teacher. Fits the wires.
4. **Metered billing:** every 50th motor firing produces a -1 taste, with no marker separating it from poison. The brain must attribute one signal to two causes (colour or its own spending), and so become able to feel energy cost at all. Fits the wires.
5. **Progressive tax:** beyond 4 foods in a rolling 20 s, further food tastes -1 and scores nothing. The brain must pace itself to a learned quota and not mistake the "bracket" for the colours reversing. Fits the wires.
6. **Commons collapse:** eaten blocks return at a rate proportional to the remaining stock of that colour, so overharvesting ends the supply. The brain must show restraint, sensing stock only through its encounter rate and accepting delayed gain. Fits the wires.
7. **Front-running thief:** an unseen scavenger snatches any block the creature has approached steadily for over 1 s. The brain must hide its intent, using feints, oblique approaches and late bursts rather than simple homing. Fits the wires.
8. **Token money with demurrage:** red tastes 0 but banks a token that decays within about 10 s; blue tastes +1 with a token and -1 without. The brain must learn that a tasteless item has instrumental value (secondary reinforcement), then keep a store and spend it in time. Fits the wires.
9. **Supply and demand:** the chance a colour tastes good falls as its share of recent meals rises. The brain must settle on a stable mixed diet, because no single "the answer is red" bit exists, and tell the world's response apart from noise. Fits the wires.
10. **Jurisdictions:** colour values are swapped in one half of the torus, and that half also has denser blocks. The brain must infer which legal regime it is in from local density or path history, then hold context-dependent values at once. Fits the wires.
11. **Loud advertising:** poison blocks drive their eye three times as hard at a given distance, so strong signals mean bad goods or a false nearness. The brain must decouple intensity from proximity and value, and discount the most salient option. Fits the wires.
12. **Counterfeits with a tell:** 30% of food-coloured blocks are poison and fire irregular bursts at the same mean rate as genuine ones. The brain must inspect pulse timing rather than rate, and learn to authenticate within a colour. Fits the wires.
13. **Toll bundling:** rich clusters of food sit hidden behind a single poison block, which occludes them. The brain must deliberately pay a known harm for a larger payoff beyond it, overriding its own learned aversion. Fits the wires.
14. **Welfare trap:** after 15 s without food, a free +1 meal lands in the mouth, whatever the brain did. The brain must separate earned reward from windfall, and the world tests whether it settles into idling (which may well be rational here). Fits the wires.
15. **Auction by momentum:** each block has a hidden, random reserve speed, and arriving below it bounces the block away with no taste. The brain must bid effort according to expected value and adjust after failures, grading force rather than just steering. Fits the wires.
16. **Foreclosure:** two poison bites within 10 s repossess one thruster for 10 s, and thrust then returns weaker on the other side. The brain must recalibrate steering rapidly while learning, and treat risk as a threat to its own means of acting. Fits the wires.
17. **Joint liability:** two creatures on a 20 mm tether share every taste, but each pays its own energy, and each has one working eye of a different colour. Each brain must detect free-riding and coordinate through tugs, felt only as distorted eye flow. Fits the wires, per creature.
18. **Goodhart's candy:** one colour tastes +1 but scores -2 and halves thrust for 10 s, so the reward signal itself lies. The brain must overrule its own teacher using a slow side effect (fewer encounters), or we find that taste alone cannot do it. Fits the wires.
19. **Bankruptcy:** a fuel store runs down with firing and refills with food, and at zero the thrusters stop, with a fuel gauge reported to the brain. The brain must shift its risk appetite with wealth, cautious when rich or gambling when near ruin. Needs a wire changed (one new input).
20. **Returns policy:** a third output, "spit", fired within 0.5 s of eating, refunds most of a bite's score for a fixed fee, while the taste still arrives. The brain must form a fast decision after the outcome, and judge when a refund pays, including sampling on purpose because returns are cheap. Needs a wire changed (one new output).

**What this set-up could never test**

- Symbolic contracts, promises, negotiation or anything needing shared language: physical rules can only imitate their incentives.
- Institutions that evolve or are chosen: the rules here are imposed by the designer, never made, voted on or reformed by the agents.
- Legacy or lineage within the wires: a single life can't test inheritance, culture, or learning from the deaths of others, and a brain gets no lesson from its own ruin.
- Large-scale effects: real markets, prices that emerge from thousands of traders, and long-run reputation are out of reach of a few creatures in 100 s.
- True values or abstract goals: taste is one scalar teacher, so there is no way to test conflicting ends the brain must reason about, or caring about anything beyond its own signal.

## Critic, who read GRAMMAR.md's third draft

I ran nothing. I read `GRAMMAR.md`, `world.py` and `Life`.

**1. Can't be written, or only by stretching**

1. **Worlds with no bodily loop:** a random hidden automaton, a market, or balancing a pole. L0-L9 all assume the loop, so these are hand-listed as four examples, which is the very failure you fear. Missing: a base form, "any state machine behind these wires", with its own sampler.
2. **Another learner in the world:** two copies of the brain competing, or a score that depends on a kin creature. The catalogue's rivals are scripted. Missing: an agent with its own memory, and a "does that stay the same?" word for "adapts to you". All seven current words ignore what the brain has learned.
3. **Coupled dynamics or a common cause:** food and poison populations in a predator-prey cycle, or one hidden "sickness" dimming the eyes and weakening thrust together, so one predicts the other. Missing: a hidden variable that several statements read and write. As drafted, statements only stack.
4. **Tipping points you cause:** overgrazing collapses a patch, and it stays collapsed after you stop. "Irreversible" appears in the rounds table but not in the words, and "step" isn't tied to your own actions. Missing: hysteresis or ruin, as a word.
5. **Change at every timescale:** 1/f drift, Levy jumps, deterministic chaos. Each current word has at most one timescale, and that flatters any detector built around a time constant. Missing: a scale-free word.
6. **Objects with their own memory:** a nut needing three strikes, or one particular block that went bad, with nothing visible to mark it. "Features" are static and "history" is the creature's. Missing: per-object state and identity.
7. **A medium or space with its own physics:** firing stirs a wake that moves nearby blocks. Walls show the gap: one wall stops the body (L2), hides things (L4) and confines blocks (L3), yet it's filed under L2 alone. Missing: a space link. I think this exclusion is a mistake, because mud, currents and walls are already in the catalogue, so "one flat, still medium" is not the real boundary.
8. **Two bodies on one brain:** eye 0 and motor 0 on one body, eye 1 and motor 1 on another. It fits the same wires. Missing: how many bodies, and which wire belongs to which.
9. **Goals that aren't meals:** taste arrives when blocks are sorted into a pattern. Missing: a goal defined over the state of the world.
10. **Readable marks:** deliberately leaving something you later see, to offload memory. I think this exclusion is drawn in the wrong place. Trails, debris and "food only where you haven't been" already store marks in the world, and offloading could lower the detector count, so it bears directly on the question.

**2. Flaws in the experiment**

1. **The curve flattens by arithmetic.**
   - With a fixed pool in random order (step 6), a count of distinct types is concave, whatever the true number of types. Near-duplicates such as gain 1.2 and 1.3 flatten it further, and "a challenge" has no defined unit, so "10x" means little.
   - Fix: define the unit by clustering on cures, and run the analysis on a synthetic generator with a known number of types. Report detectors that cover only one world and estimate the unseen (Chao1). The main measure should be a frozen circuit's coverage on fresh draws.
2. **Hard worlds leave the denominator.**
   - The plot counts only challenges covered, so a world nobody could cure disappears. Ceilings are weakest on the hardest worlds, so a failed search reads as "no gap" or "unlearnable".
   - Fix: set a fixed design budget per world and report failures on the same plot. Record how each ceiling was obtained, and repeat the result counting every doubtful world as learnable.
3. **A short life caps what can matter.**
   - The job asks for only about 10 meals in 100 s, so few rules can be learned at all, and "one lethal block per 10,000 s" will rarely appear in a life. A plateau may reflect the life's information budget, not an economical brain.
   - Fix: repeat the sort and the curve at 10x and 100x life length. If the plateau rises, it was the budget.
4. **Counting lets cost hide.**
   - A new bank model can absorb what would have been a detector, so a flat detector count may be a relabelling. Reporting three counts doesn't stop that. L0 worlds also name brain parts, so new detectors create new challenges, and the x-axis depends on the y-axis.
   - Fix: score one cumulative circuit in parts and power, re-running every earlier world and the unmodified world after each addition. Keep a frozen L0 list, or plot L0 separately.
5. **The guards against self-deception are contaminated.**
   - A designer who wrote the grammar can't really hold out a word. Fresh agents, if they are the same model, share priors, so their agreement proves little.
   - The bold claim that worlds matching on the wires are the same challenge fails for closed loops: one fixed policy never tests contingencies it doesn't trigger. It also contradicts L9, where the wires match and the best behaviour differs.
   - The classifier can only find labels the grammar gave it, so it doesn't bound the number of types.
   - Fix: have a designer who sees only the training worlds build the cures. Add a test set compiled from outside sources, such as RL benchmarks and conditioning literature. Take signatures under several policies, including motor babbling, and use unsupervised clustering.

**3. The first change**

Make the grammar an executable language: hidden state variables, typed reads and writes on the wires and the world, and an explicit sampler. Then compile the whole catalogue and count what fails.

Today a person has to interpret "L3, depends on history", so step 1's fixed generator, the long set, the searched set and the leave-out test don't exist yet. "Can be written" also tests nothing, since the document admits nearly anything fits. The real test becomes how probable each world is under the sampler. This would also force items 1, 3 and 4 into the open.

**One small fix to the source audit**

"One meal, one taste" isn't what `Life.step` does: several meals in a tick give one clipped pulse, and food plus poison cancels to no pulse. The audit also omits the eyes' Poisson firing, the birth state and the respawn exclusion zone.

## Second critic, a different model, who read the fourth draft

**1. What the language still can't express**

- **State over place.** Scopes are world, creature and block. Trails, wakes, currents, mud, a moving front and "food only where you haven't been" all need a field over space. Faking it with invisible blocks makes these worlds look artificially long. Missing: a field scope.
- **Time.** State looks scalar, and rules fire only on "a tick or an event".
  - Delay, echo, queued tastes, backlash and parity over the last 8 bites need a buffer or a deferred write.
  - Poisson against regular firing needs a way to replace the draw in `Life.step`, plus a sub-tick moment for each pulse.
  - Missing: a queue type, "write at t + d", and pulse generators as a write point.
- **Interception and order.** "Writes" doesn't say whether a rule adds to a default or replaces it. Vetoing a firing, meal or taste needs a defined pipeline. Gain then delay differs from delay then gain, and two rules can write one point, so "statements compose" is undefined. Missing: named stages, replace or add, and a fixed rule order.
- **What a block looks like, and geometry.**
  - `kind` ties colour to worth, and the ray-cast in `_look` has no write points.
  - Two-colour blocks, flicker, mixed eyes, mirages, occluding walls, collision, an off-centre mouth and hinges therefore don't compile.
  - The world constants aren't listed as writes either.
  - Missing: separate per-eye emission and worth for each block, an occluder/collider primitive, and every constant writable.
- **Quantifiers and the function set.** Guides, rivals, cellular automata and predator-prey need "nearest", "count within r" and "for each block". "A function of reads and state" is also undefined, yet that vocabulary sets the sampler's probabilities. Missing: both, specified.

**2. Flaws that could give a confident wrong answer**

- **Coverage can flatten by construction.**
  - Coverage from greedily chosen cures is concave for almost any population, so diminishing returns are close to guaranteed.
  - A description-length prior also piles weight on short worlds.
  - The detector count also stops rising when designers run out of budget.
  - Step 2's control tests type counting, not this pipeline.
  - Three counts ("Still open") also let whichever one looks flat be reported.
  - Fix: add a synthetic world set where each world truly needs its own cure, and push it through the same coverage analysis. Pre-register one primary number, such as parts needed to reach a fixed coverage of learnable worlds, reported by description-length band. Also state what result means no.
- **The compile test is on its training set, and one sampler sets the answer.**
  - The language was built from the very lists it will compile, so passing means little.
  - "How improbable" has no reference point, because adding a primitive raises any idea's probability.
  - The outside set can also shrink quietly if it only keeps what compiles.
  - Fix: seal the outside set before the language is final, and count non-compilers in the denominator. Run 2 or 3 rival samplers with different primitives, and report the spread.
  - Also label the first phase's answer "taste immediate and truthful". Those are the conditions the bank rests on, so that answer must not be pooled with or generalised to later worlds.
- **"No gap: world dropped" hides failures behind weak ceilings.**
  - A weak ceiling turns a hard opportunity into "no gap", so it's never flagged as doubtful.
  - L9 worlds have no signal on the wires, so no automatic cure can respond to them.
  - Fix: drop a world only if a policy that's told the hidden rule also ties with the base brain. Report L9 separately, as design-time tuning rather than learning.
- **Weak statistics can read as success.**
  - A tie from too few lives reads as "no harm", and a noisy gain reads as "covered".
  - At a 95% level, 300 worlds give about 15 spurious calls.
  - Intervals over lives overstate precision when the sampled unit is worlds.
  - Fix: use an equivalence margin set in advance on the fraction of the gap closed, bootstrap over worlds, and control the false discovery rate. Racing (about 20 pairs, then more only for borderline worlds) also saves lives.
- **Cost (my arithmetic, nothing run).** Assuming perfect scaling to 8 lives/s, 50 pairs take 12.5 s per world, so 300 worlds take about 1 hour per circuit.
  - **Step 7:** 100x costs about 21 minutes per world, or 4.4 days per circuit. Cut 100x, and run 10x on about 30 worlds only. As written, step 7 is also confounded: a plateau that doesn't rise could just mean nobody redesigned the cures. So test whether ceilings rise with life length.
  - **Step 6:** a design budget per world is impractical. A 10,000-life ceiling search is about 21 minutes per world, or 4.3 days for 300, before any agent's time. Use the told-the-rule bound first, search only where it shows a gap, and design only for the largest failure groups. Keep sampled worlds to about 300.
  - **Leave-out test 4:** a separate build for each fold multiplies everything. Use one held-out split frozen before the first cure, and test on it as the circuit grows.
  - **Cut Chao1:** cures overlap, which breaks its assumptions, and fresh-draw coverage already answers the same question.
  - **Cut the searched adversary:** it always finds a hole, so it can't change the conclusion. Keep the hand-written traps.
  - **Defer step 10 and the clustering test (test 5):** neither changes the count. Keep wire signatures only to remove near-duplicates.
  - **The engine:** at 10 ms a tick, a life is 10,000 ticks, so one per-block rule in Python runs about 360,000 times a life. Compiling each programme with numba also adds its own delay. Use one numba-compiled rule interpreter. `world.py`'s constants are numba compile-time globals, so they must become arguments before anything can be redrawn each life.

**3. Order of work: yes, I'd change it**

1. Seal the outside set and the held-out split.
2. Run the synthetic controls, including the one-cure-per-world case. They don't need the language, and they could kill the analysis cheaply.
3. Build the minimal language and engine, driven by the source audit, and hand-write about 30 worlds end to end.
4. Pilot about 100 draws to measure the share of learnable worlds with a gap, and lives per world. Only then freeze the samplers.
5. Measure the present circuit's coverage on fresh draws, with no new cures. That's the first real number, and it scores a prediction.
6. Run the 10x ceiling check on about 30 worlds before any cure work, since it may show that few rules can be learned at all.
7. Design cures, re-running earlier worlds as you go, then open the held-out split and the outside set.
8. Move on to rule-changing worlds.

**4. Verdict**

Yes: nothing above changes the first builds (language, engine, controls, pilot), so start, but seal the outside set and write down the primary number and what result means no before any code.
