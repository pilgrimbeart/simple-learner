# Outsiders' ideas, round 1 (GRAMMAR.md)

Five fresh agents, 2026-11-04, each given only a neutral description of the creature and one lens, unedited.

## Ecology

1. **Bait shyness.** Poison's -1 arrives 5 to 15 s after eating, with other meals possibly in between (rats and Garcia). Forces one-shot credit across long, cluttered gaps, and sampling one novel food at a time. Fits the wires.
2. **Complementary nutrients.** Each colour tastes +1 only while its nutrient is short, and -1 once the creature has overeaten it (locust protein and carbohydrate balance). Forces a hidden internal ledger and alternating diet, as value depends on recent intake, not colour. Fits the wires.
3. **Acquired tolerance.** A colour tastes bad at first, but after several doses, gut flora make it the richest food (desert woodrats on creosote). Forces persisting against negative feedback for a later payoff, and rate-limited sampling. Fits the wires.
4. **Depleting patches.** Blocks come in clumps that don't refill until the creature has left (marginal value theorem). Forces estimating local against background intake rate, plus a giving-up time and straight-line travel between patches. Fits the wires.
5. **Prudent predation.** Regrowth is proportional to the blocks left standing, so over-eating crashes the stock for the rest of a much longer life. Forces restraint: passing up food in view, and sensing scarcity from falling encounter rates. Fits the wires.
6. **Habitat mosaic.** Red is food on one half of the torus and blue on the other, with a soft ecotone between. Forces context-dependent memory: inferring "where am I" from recent tastes and switching without erasing the other map. Fits the wires.
7. **Resident forager.** An invisible experienced competitor eats only food, so the world fills up with poison. Forces use of base rates: "the colour left lying about is suspect", which is learning before the first bite, and needs a counterweight when the competitor leaves. Fits the wires.
8. **Indicator species.** Red is tasteless but inedible-neutral (taste 0), and blue food sits just behind red (honeyguides, or fungi under particular trees). Forces second-order conditioning: valuing a cue that never pays directly and using it to steer. Fits the wires.
9. **Twitching lure.** Some food-coloured blocks jiggle, like an anglerfish's lure, and biting one gives repeated -1. Forces discrimination by temporal pattern in the eye's pulses, within one colour, on one wire. Fits the wires.
10. **Evasive prey.** Food blocks dart away when the creature comes within 6 mm at speed, like a startled shrimp. Forces stalking: approaching slowly, then lunging, with thrust graded by eye rate and a learned strike distance. Fits the wires.
11. **The hawk overhead.** In random 10 s bouts, any thrust risks a -1 with no block eaten, which turns taste into pain as well. Forces freezing, the idea that danger comes in bouts, and not blaming the colour last seen. Fits the wires, though the taste wire's meaning widens.
12. **Reward-hijacking parasite.** After eating an infected block, taste is inverted for 20 s and one thruster is driven extra (*Toxoplasma*, zombie snails). Forces guarding long-term memory against its own teaching signal, by checking new evidence against old. Fits the wires.
13. **Metamorphosis.** At 50 s the body remakes itself: motors swap, thrust and mouth size change, and the larval food colour becomes useless. Forces selective retention: relearning the motor map while keeping or discarding values separately, as moths do. Fits the wires.
14. **Sessile trap.** The creature is rooted like an anemone or flytrap, and blocks drift past on a current. Motor 0 opens the mouth at a metabolic cost, and motor 1 sways the mouth sideways. Forces anticipatory timing, withholding and costed decisions with no locomotion. Fits the wires, with new organ meanings.
15. **Sniffing.** Eyes work only for 50 ms after a motor firing, because vision is tied to thrusts, like a bat's cry or a rat's whisk. Forces active sensing: paying to look, raising the look rate on approach, and reading input time-locked to its own output. Fits the wires.
16. **River.** A steady current drifts creature and blocks together or apart, and it varies across the world (drift-feeding trout). Forces station-holding and separating self-motion from world-motion using only changes in eye rate and an efference copy. Fits the wires.
17. **Night and torpor.** For half of each 40 s cycle, the eyes give only noise and blocks can't be eaten. Forces entraining an internal clock, shutting down to save energy, and waking in anticipation of dawn. Fits the wires.
18. **Inherited memory.** Lives run in sequence, and offspring start with a noisy copy of the parent's memories. The food colour persists for a random number of generations. Forces weighing a prior against one's own evidence: maternal effects and bet-hedging on how far to trust ancestors. Fits the wires.
19. **Central-place forager.** Food is carried and tastes +1 only when delivered to one nest, so the creature must return like a bee or an ant. Forces homing, by path integration from motor copies or a beacon, and a carrying or not-carrying state. Needs a wire changed: a nest sense (or a very hard version with none).
20. **Alarm calls.** Several creatures share a world with predators, and each gets a "call" output and a "hear" input (vervet monkeys). Forces signal production, learning what a heard call means, and resisting false alarms by cheats who then take the food. Needs a wire changed: one out, one in.

**What it could never test**
- Open-ended evolution: goals and scoring are set from outside, so no new body plan or new purpose can emerge.
- Manipulation and materials: tools, building, gripping and 3D mechanics have no footing in a disc on a plane.
- Rich perception: a few pulse wires can't support recognising objects, individuals or scenes.
- Deep sociality: theory of mind, language and accumulating culture need more bandwidth and more generations than this allows.
- Rare, high-stakes events: with a few dozen noisy meals per life, anything met once or fatally can't be learned, only inherited.

## Robotics

**Actuators**

1. **Stiction dead-band.** Thrust is zero below a firing rate, then lurches, and the threshold differs per thruster. The brain must find each thruster's breakaway point and use dither or bursts rather than smooth proportional drive. *Fits the wires.*
2. **Transport delay.** Add 300–800 ms between a firing and its thrust, as with a slow valve or long hose. The brain must lower its loop gain or anticipate, or it will hunt side to side past every target. *Fits the wires.*
3. **Thruster death mid-life.** One thruster fails at a random moment, leaving only turns away from the working side. The brain must notice the lost response and re-plan, turning the long way round and foraging in arcs. *Fits the wires.*
4. **Stuck-on valve.** A thruster sometimes latches on for seconds and ignores commands. The brain must recognise an uncommanded spin and reject it with the other thruster, without learning from those seconds as if it had chosen them. *Fits the wires.*
5. **Stepper rudder.** One motor is the only thruster, and each firing of the other moves a rudder one notch with a hard end stop. The brain must identify an integrating actuator, where the same firing means something different depending on what came before, and keep track of a hidden position. *Fits the wires.*
6. **Legged gait.** Replace thrusters with two legs on a ratchet: only alternating firings at about the right rhythm move it forward, and an uneven rhythm curves it. The brain must generate a rhythm and steer by skewing its phase, not by "see, then fire". *Fits the wires.*

**Sensors**

7. **Motor noise in the signals.** Each thruster firing injects false pulses into the eyes, and occasionally a false taste, like a shared ground on a real robot. The brain must blank or subtract using its own motor commands, and must not credit meals it never ate. *Fits the wires.*
8. **Knocked eye mount.** The corridor is bore-sighted several degrees off the mouth axis, differently each life. The brain must learn the offset and turn a set time after sighting, not simply drive at what it sees. *Fits the wires.*
9. **Sensor foldover.** Eye rate rises with nearness, then falls sharply when very close (blooming). Rate alone no longer gives range, so the brain must read history: "rose, then fell" means nearly there. *Fits the wires.*

**Mechanics and terrain**

10. **Sloshing tank.** An internal liquid mass resonates at about 1–2 Hz, so firing near that rhythm builds a growing yaw wobble. The brain must discover and avoid a resonance in its own output, which works like a learned notch filter. *Fits the wires.*
11. **Ice and mud patches.** Invisible regions change drag tenfold, so on ice it coasts past targets with no brake, and in mud it barely moves. The brain must keep estimating the current response to its thrust and rescale its gains and timing as it crosses. *Fits the wires.*
12. **Non-minimum-phase hull.** A firing first kicks the nose the wrong way for 100 ms before the turn develops. The brain must not "correct" the initial wrong-way response, which is the classic trap for fast feedback. *Fits the wires.*
13. **Walled arena.** Replace the torus with walls painted in a colour that is neither food nor poison, seen on one eye's channel or a shared one. Pushing against a wall means full thrust with an unchanging eye rate, so the brain must detect a stall from the lack of response and turn out of corners. *Fits the wires.*

**Power**

14. **Sagging battery with brownouts.** Rapid firing draws the rail down so each firing gives less thrust, and deep sag wipes the brain's fast state, like a watchdog reset. The brain must pace its output and either store what it has learned durably or relearn quickly. *Fits the wires.*

**The task**

15. **Fragile payload.** A block hit above a speed limit bursts and tastes -1 whatever its colour. The brain must regulate its approach speed, which means coasting in using the rise in eye rate, and must separate "bad colour" from "bad landing" using the same one taste wire. *Fits the wires.*
16. **Conveyor world.** Blocks drift in slowly changing currents. The brain must lead the target, and a narrow corridor gives it only brief sightings, so it has to hold a prediction after the target leaves view. *Fits the wires.*
17. **Slow lab assay.** Taste arrives 5–20 s after eating, with variable lag and 30% of results lost. The brain must hold credit over long, noisy gaps, with several meals potentially in flight. *Fits the wires.*
18. **Robot fleet.** Several identical creatures share the world, painted one eye's colour and moving, and their thrust wash shoves one another. The brain must tell moving peers from still blocks, avoid congestion and cope with disturbances it did not cause. *Fits the wires.*
19. **Gripper.** Contact no longer eats. A third motor closes the mouth, and a mistimed or empty close costs energy. The brain must time a discrete action to contact, and can now pass through poison rather than having to steer around it. *Needs a wire changed.*
20. **Drifting gyro.** Add a yaw-rate input with a wandering bias and scale, while the eyes stay trustworthy but sparse. The brain must fuse a fast, biased sensor with a slow, sound one, and discount the gyro if it fails. *Needs a wire changed.*

**What this set-up could never test**

- Rich perception, such as recognising objects, scenes or shapes, because a few pulse trains carry too few bits.
- Coordinating many degrees of freedom, as in dexterous manipulation or whole-body balance with a real risk of falling.
- Goals given from outside, whether instructions, language, or explaining or being audited by a human operator.
- Learning across lives, such as inheritance, fleet-shared experience or maintenance over a machine's lifetime.
- True one-shot safety, where one error ends everything: added death can impose the penalty, but too few lives survive it to measure caution at rare, catastrophic risks.

## Psychology

1. **Blocking (Kamin).** Some blocks are bicoloured and fire both eyes. Red alone pays first, then red+blue pays, then blue is tested alone.
   Forces: learning from prediction error rather than from pairing. Fits the wires.

2. **Negative patterning.** Red alone is food, blue alone is food, and a bicoloured block is poison.
   Forces: a configural code, since no sum of separate colour values can solve it (the classic hippocampal test). Fits the wires.

3. **Latent inhibition.** For the first 30 s only one colour is present, and it tastes of nothing. Then both colours appear with consequences, in counterbalanced lives.
   Forces: a per-cue learning rate shaped by history, which separates attention theories from plain error-driven ones. Fits the wires.

4. **Long-delay aversion (Garcia).** Taste arrives 5–20 s after the bite, with other bites possibly in between.
   Forces: lasting traces of what was eaten and credit assignment across a gap, not just a short coincidence window. Fits the wires.

5. **Two-step revaluation (Daw).** Inert blue signposts sit just ahead of red blocks. Red later flips to poison, and only red is ever tasted.
   Forces: an internal model of "blue leads to red", because only a model-based brain drops its approach to blue before tasting anything from it. Fits the wires.

6. **Specific hunger (Richter, Krieckhaus and Wolf).** Each colour tastes +1 when that nutrient is lacking and -1 when sated.
   Forces: tracking separate needs and switching at once to a cue, which separates stimulus-outcome knowledge from a cached value. Fits the wires.

7. **Occasion setting.** One half of the torus has blue blocks and the other has none. Blue is never eaten for value, and red is food only where blue was recently seen.
   Forces: hierarchical gating, where one cue changes what another means, using a memory of seconds. Fits the wires.

8. **The displaced ant (Wehner).** Blocks reappear only in one hidden patch, and colour is irrelevant. At test the creature is teleported.
   Forces: path integration from its own motor firings. Searching at the fictive location proves that, while staying local after displacement means only area-restricted search. Fits the wires.

9. **Prism goggles (Stratton).** The eye corridor is rotated 15° off the heading mid-life, then restored.
   Forces: a learned delay-and-turn mapping from seeing to steering. An aftereffect on removal separates recalibration from a new strategy. Fits the wires.

10. **Selective eye loss.** After learning, either the food eye or the poison eye dies.
    Forces: use of absence as evidence. It also reveals whether the brain had learned "approach food", "avoid poison", or both. Fits the wires.

11. **Parkinson's on and off (Frank).** Mid-life, the brain's taste channel loses most positive pulses, or in another condition most negative ones.
    Forces: a choice between separate go and no-go learning and one signed value, since these predict different asymmetries. Fits the wires, as a brain-side lesion.

12. **Fixed-interval schedule.** Food tastes good only if at least 5 s have passed since the last meal, and earlier bites are poison.
    Forces: an internal clock, with predictions testable as scalar timing and a scalloped approach rate. Fits the wires.

13. **Delayed non-match to sample.** Whichever colour was just eaten is poison next, so the other colour is food.
    Forces: working memory that sets current value, because no fixed colour preference can beat chance. Fits the wires.

14. **Attentional set-shifting (Wisconsin, ID/ED).** Each eye's pulses are either regular or random, by block type. First colour decides value, then only regularity does.
    Forces: reading the temporal pattern and attending to a dimension. Compare against a plain reversal, which needs neither shift. Fits the wires.

15. **Spacing effect plus sleep.** The same number of meals comes massed or spaced by dark gaps with the motors disabled, and retention is tested later.
    Forces: two timescales of memory with consolidation rather than one decaying store. Fits the wires, but a 100 s life may be too short, so the life would need lengthening.

16. **Triadic helplessness and truly random control (Seligman, Rescorla).** Taste pulses arrive independently of bites, either escapable by moving or yoked to another creature's. Then the normal world begins.
    Forces: estimating contingency rather than counting pairings, and detecting whether it has control. Fits the wires, but it changes what taste means, so it needs the user's approval.

17. **Omission (Williams and Williams).** A red block flees if a motor fired recently with red in view, and drifts toward a coasting creature.
    Forces: separate Pavlovian approach and instrumental control, because a purely Pavlovian brain keeps chasing and loses. Fits the wires.

18. **Reafference (von Holst).** One eye also carries a faint echo of motor 0, 100 ms late, mixed with real sightings.
    Forces: discovering which input it caused itself and cancelling it, a toy version of self-other confusion. Fits the wires.

19. **Extinction and savings.** All blocks taste of nothing for 25 s mid-life, then the original contingency returns.
    Forces: treating "nothing" differently from "the opposite", and keeping the old memory under new inhibition (fast relearning) rather than erasing it. Fits the wires.

20. **Belongingness (Garcia and Koelling).** Add a third cue input such as a sound at contact, and a second outcome wire for pain alongside taste.
    Forces: a test of equipotentiality, or a brain that must develop or be born with preferred pairings of cue and outcome. Needs a wire changed.

**What this set-up could never test:**
- Rich perception, such as object recognition or invariance, because two pulse trains carry too little.
- Language, symbols, or instructed rules.
- Reported experience, so blindsight or awareness can only be inferred, never asked about.
- Skilled, high-dimensional movement, because there are only two forward thrusters.
- Mind-reading or true communication, because any other creature reaches the brain only as coloured pulses or taste.

## Reinforcement learning

1. **Alternation.** Eating the colour you ate last tastes -1, and eating the other colour tastes +1, so each colour averages zero. This forces a working memory that gates behaviour, because any per-colour value learner sees nothing. Fits the wires.
2. **Delayed sickness.** Poison tastes +1 on eating, then -1 arrives 20 s later, with other meals in between. This forces credit assignment across interleaved events (Garcia's taste aversion), and it needs a longer life to clear the noise wall. Fits the wires.
3. **Superstition test.** Taste arrives as random ±1 pulses unrelated to anything, and blocks are tasteless. The right result is to learn nothing and spend no extra energy, so the brain must be able to judge that no contingency exists. It exposes learners that always "converge" on something. Fits the wires.
4. **Numbing loophole.** Taste is silent whenever only one thruster has fired recently, but the score still counts the poison. Eating mid-turn then feels harmless, which is reward tampering. It measures whether the learner drifts into the blind spot, and no brain can fully resist because the true cost is unfelt. Fits the wires.
5. **Noisy TV.** Tasteless flicker posts make an eye fire at maximum rate and then fall silent at random. This forces the brain to separate salience from predictive value, and it traps anything driven by rate or novelty. Fits the wires.
6. **Poison moat.** Dense food pockets are ringed by poison with gaps narrower than the body, and open ground holds little food. The brain must accept a known -2 to reach a larger payoff, escaping the deceptive optimum of "avoid poison". Fits the wires.
7. **Needle in a torus.** The world is 10 times wider, with one tight cluster that never moves and eyes that see only 15 mm. This forces a self-generated search path and some record of where it has been, since random walks fail (Montezuma-style hard exploration). Fits the wires.
8. **Matching pennies.** An adversary flips which colour is food whenever the last five meals favoured one colour. Any deterministic preference is exploited, so the brain must learn to randomise deliberately (the adversarial bandit minimax). Fits the wires.
9. **Ruin.** Each poison permanently removes 20% of one thruster's thrust, and the third poison ends the life. Learning by trial now has a capped budget, which forces cautious sampling and very fast aversion. Fits the wires.
10. **Hunger wire.** Motion burns a finite reserve, and food is worth more when the reserve is low. A reserve signal comes in as a new input. This forces state-dependent value, including learning when to stop and rest rather than maximise. Needs a wire changed.
11. **Commons.** Blocks respawn only near surviving blocks of the same colour, at a rate proportional to their local count. A greedy eater collapses its own food supply, so the brain must learn restraint from a slow, delayed consequence (sustainable yield). Fits the wires.
12. **Blind operant.** The eyes give pure noise, and food appears only if the motor firing pattern holds a certain ratio and rhythm. This forces motor skill learning from taste alone, defeating any mechanism that needs a sensory correlate. Fits the wires.
13. **Silent first half.** All blocks are tasteless for 50 s, and then taste switches on. This tests reward-free learning: can the brain use the silence to learn its own turning and colour wiring, then beat a control that had no such period (Tolman's latent learning)? Fits the wires.
14. **Timing code.** Two kinds of red exist, with identical mean pulse rates but regular versus bursty trains, and only one kind is food. The brain must discover a relevant feature hidden in spike timing on a single wire, rather than being handed it on a labelled line. Fits the wires.
15. **Geography rule.** Red is food in one half of the torus and poison in the other, with no landmark. This forces context inference, by path integration from the brain's own motor firings or by inferring position from recent meals. A global colour value averages to zero. Fits the wires.
16. **Procgen sweep.** Each life redraws block density, drag, eye range, pulse rates and life length (10 to 1000 s) across wide ranges, unannounced. This exposes hidden clocks and constants tuned to the benchmark, and it forces exploration that adapts to the horizon and the event rate. Fits the wires.
17. **Skittish prey.** Blocks drift, and they dart away when the creature's thrust is high nearby. The creature must wait and then lunge at the last moment. This inverts the approach reflex and forces timing and motor inhibition. Fits the wires.
18. **Lewis game.** Two creatures are cross-wired: one sees but can't move, and the other moves but is blind. The first creature's motor outputs feed the second's eye inputs, and they share taste. They must invent a signalling code together while each is non-stationary to the other. Needs a wire changed.
19. **Body removed.** Motor firings pull two levers directly, eye pulses are a cue, and taste is the payout, with a hidden payout probability. This forces nothing new, and that is the point: it scores regret against the Lai-Robbins bound and Thompson sampling, showing how much of apparent learning was really the body and world. Fits the wires.
20. **Gas world.** There are no objects, only drifting diffusing colour fields read as pulse rate, with taste pulses in proportion to local concentration when moving. This forces klinotaxis, comparing now against a moment ago, so object-based tricks like "lunge at the rate peak" have nothing to work on. Fits the wires.

**What it could never test**
- Language, instruction or abstract symbols: a few pulse wires can't carry a task description or compositional meaning.
- Rich perception or high-dimensional generalisation, because the input bandwidth stays tiny.
- Choosing its own goals: the score is always imposed from outside and read by us, so open-ended creativity can't show up.
- Whether anything is understood rather than merely behaved, because we only ever see policies and scores.
- Cumulative culture or large-scale abstraction, because a small circuit's state and any short life cap what can build up.

## Game design

**Timing and sequence**

1. **Track & Field gait.** A thruster only pushes if it isn't the one that fired last, so mashing one motor gets you nowhere. The brain must grow a rhythm generator and find the gait with no thrust sensor. Fits the wires.
2. **Rhythm game.** A hidden 1 Hz beat runs the world: anything eaten on the beat is food, off the beat poison, whatever its colour. The brain must entrain an inner clock from taste alone and time its strikes. Fits the wires.
3. **Combo rule.** Eating alternate colours is food; the same colour twice running is poison. The brain must hold "what I ate last" and flip its preference after each meal. Fits the wires.
4. **Push your luck.** Each meal in a streak raises the chance that the next block of the food colour is poison; a few seconds without eating resets it. The brain must estimate rising risk and stop while ahead. Fits the wires.
5. **Mastermind scoreboard.** Taste comes only every 10 s, as the sign of the net score for that window. The brain must assign credit across several meals from one verdict. Fits the wires, but changes what taste means.

**Bodies that misbehave**

6. **Klein bottle.** One seam of the torus is mirrored, so crossing it swaps left and right until you cross again. The brain must notice from its own steering failures that its motor map has flipped, and switch fast. Fits the wires.
7. **Ice level.** Almost no drag, and thrusters only push forward, so stopping means turning round and burning. The brain must control momentum and act ahead of where it is now. Fits the wires.
8. **Tetherball.** The creature is on an elastic leash to a stake, and far blocks are reachable only with a swinging run-up. The brain must pump energy and accept moving away from a target in order to reach it. Fits the wires.
9. **Katamari.** Each food makes the disc bigger and slower to turn; each poison shrinks it. The brain must keep recalibrating its steering to a changing body. Fits the wires.

**Blocks that play back**

10. **Boo.** Poison blocks creep after you, but freeze while they are in your eye corridor. The brain must sometimes stare at what it wants to avoid, splitting "bad" from "look away". Fits the wires.
11. **Mimics.** A fifth of food-coloured blocks are poison and blink at 2 Hz; true food fires steadily. The brain must discriminate rhythm within one wire, not just which wire is firing. Fits the wires.
12. **Sokoban squash.** Touching a block pushes it; it is eaten only when shoved into another block. The brain must use objects as tools and bridge a gap between its action and the taste. Fits the wires.
13. **Snake.** You shed a trail of poison-coloured blocks that lasts 20 s. The brain must steer so as not to box itself in, reading its own past from the world. Fits the wires.

**Worlds with a memory**

14. **Groundhog Day.** Every 20 s the creature and all blocks snap back to the same start. The brain must memorise and refine an open-loop route, learning across rewinds. Fits the wires.
15. **Cartridge swap.** Unplug the body and plug the same five wires into Pong: motors move a paddle, eyes report the ball left or right, taste is hit or miss. This tests whether the learning was ever general or only about this body. Fits the wires.

**Other players**

16. **Tag.** A rival wears the current food colour. A mouth contact gives the tagger +1 and the tagged -1, and roles swap. The same stimulus must mean chase or flee, depending on the last taste. Fits the wires.
17. **Follow the ghost.** A silent demonstrator wanders, eating only food, and is painted the colour it last ate. The brain must learn a colour's value by watching, before tasting anything. Fits the wires.
18. **Hanabi pair.** Two creatures each have a lamp they can light, and each sees only the other's lamp and one block colour, so neither can judge the other colour alone. They must invent a signalling code together. Needs a wire changed (a lamp output; the lamp is seen through an eye).

**New verbs**

19. **Bite button.** Touching no longer eats; a third output snaps the mouth shut. The brain must separate approach from commitment, and learn a new action whose first uses look pointless. Needs a wire changed.
20. **Harvest Moon.** A third output plants a seed at the tail, which becomes a food block 20 s later, at a cost in energy. The brain must invest now for later, and return to where it planted. Needs a wire changed.

**What this set-up could never test**

- Rich perception: a few pulse wires can't carry objects, scenes or invariance.
- Language, symbols, or being told something rather than finding it out.
- Dexterity: a flat disc with two thrusters has no balance, grasp or many-jointed control.
- Competing needs: one signed taste can't pose thirst against hunger, or let a creature choose its own goals.
- Slow accumulation: a 100 s life leaves no room for years of knowledge, development, sleep or culture.
