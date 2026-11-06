# Outsiders' ideas, round 3 (GRAMMAR.md)

The same eight lenses, repeated with a tighter seal (lab/blind_agents.sh), 2026-11-04, unedited: no project instructions, memory or git status.

## Ecology

1. **Delayed sickness (conditioned taste aversion):** Poison's -1 arrives 5-20 s after the bite, while food's +1 is immediate. The brain must assign blame across a long gap with other bites in between, weighting the likely culprit. *Fits the wires.*
2. **Imperfect Batesian mimicry:** Some blocks of the food colour are poison. Since poison costs twice as much, the colour is worth eating only if over two-thirds are real. The brain must weigh a running average, not flip on the last taste. *Fits the wires.*
3. **Diet balancing:** Both colours are nutrients, but taste turns to -1 for a colour eaten too often recently. The brain must track its internal state and let value depend on recent intake. *Fits the wires.*
4. **Inducible plant defences (acacia and kudu):** Eating a block turns nearby same-coloured blocks toxic for 10 s. The brain must learn that value depends on place and its own recent actions, then take a few bites and move on. *Fits the wires.*
5. **Patch depletion (marginal value theorem):** Blocks come in dense clumps across empty ground, and a clump regrows only once abandoned. The brain must time when to give up using only the time since its last reward. *Fits the wires.*
6. **Handling time (optimal diet):** Both colours taste +1, but one freezes the thrusters for 3 s after each bite. The brain must value reward per unit time and skip slow prey only when fast prey is plentiful. *Fits the wires.*
7. **Overgrazing:** Food blocks breed only from surviving neighbours, and poison blocks colonise emptied space. The brain must hold back now for later yield, with little warning before a crash. *Fits the wires.*
8. **Flight distance:** Blocks bolt if approached faster than a threshold speed. The brain must learn to stalk, slowing in a controlled way as the pulse rate climbs. *Fits the wires.*
9. **Movement-sensing predator:** A hunter that homes in on motion wears either colour and gives -1 on capture. The brain must compare the pulse rate with its own motor commands to spot looming that it didn't cause, then freeze. *Fits the wires.*
10. **Motor-hijacking parasite:** Eating certain blocks adds a hidden bias to one thruster for 20 s, as if the host were being steered. The brain must notice that its aim is failing from sparse visual evidence and recalibrate its steering, then undo this later. *Fits the wires.*
11. **Central-place foraging:** Bites taste as usual but score only when carried to an invisible home spot, which gives a taste pulse on arrival. The brain must path-integrate from its own motor firings, as desert ants do. *Fits the wires.*
12. **Moth plume tracking:** Eyes become two co-located noses, one per odour, firing on patchy filaments blown downwind from blocks. With no left-right difference or line of sight, the brain must use memory to surge upwind and cast when the scent is lost. *Fits the wires.*
13. **Echolocation:** Eyes work only for 50 ms after a costly ping from a new output. The brain must decide when information is worth its energy, ideally pinging faster on approach, like a bat's terminal buzz. *Needs a wire changed (extra output).*
14. **Slime-mould trails:** The creature leaves a fading residue, sensed by a new input at the mouth. The brain must use the world as external memory and avoid searching the same ground twice. *Needs a wire changed (extra input).*
15. **Watching a neighbour:** A skilled forager is visible through a third eye, and its choices reveal which colour is food. The brain must learn a value from another's behaviour, without paying for a first bad bite. *Needs a wire changed (extra input).*
16. **Honeyguide mutualism:** An uncatchable moving guide in one colour leads the way to a dense hidden patch. The brain must treat a signal that never pays directly as a pointer, chasing it without expecting to eat it. *Fits the wires.*
17. **Rooted flytrap:** The body is anchored while blocks drift past. One motor rotates it and the other is a costly snap, and the sole way to eat. The brain must discover what each motor does, accumulate evidence, and time a single strike. *Fits the wires.*
18. **Metamorphosis:** At 50 s, drag, turning, corridor length and diet all change abruptly, and the colour values swap. The brain must remap its motor control while deciding which memories to carry across, as moths appear to do. *Fits the wires.*
19. **Night and torpor:** Eyes fall almost silent for 15 s in every 40 s, and moving is costlier in the dark. The brain must tell darkness from an empty view, anticipate the cycle, and shut down to save energy. *Fits the wires.*
20. **Tidal current:** A hidden water flow reverses every 20 s and carries the creature with it. The brain must infer a rhythmic force from visual drift, steer ahead of it, and forage with the flow rather than fight it. *Fits the wires.*

**What this set-up could never test:**
- Rich perception, such as shape, object identity or complex scenes, through a few pulse channels.
- Dexterity or tool use, because the body has only a few simple actuators and no limbs.
- Evolutionary change or arms races across generations, because each test covers one lifetime.
- Long-term relationships, such as kinship, reputation or negotiated cooperation.
- Lifelong development and real survival stakes, because a life is 100 s and the score is imposed from outside.

## Robotics

1. **Thruster deadband:** below a threshold firing rate a thruster gives nothing, then it kicks abruptly. *Gain:* find the threshold and use bursts for fine control. **Fits the wires.**
2. **Thruster failure mid-life:** one thruster dies without warning, leaving only arcs in one direction. *Gain:* notice the fault from how the view changes, then use pulse timing to reshape arcs that intercept blocks. **Fits the wires.**
3. **Actuator lag:** each motor firing takes effect 300 ms later, so eager steering overshoots and oscillates. *Gain:* predict the results of its own commands, or lower its gain to stay stable. **Fits the wires.**
4. **Safety interlock:** the thrusters latch off after 1 s without firing, and restart only when both fire within a few ticks. *Gain:* discover an arming sequence and keep the system alive while coasting. **Fits the wires.**
5. **Legs instead of thrusters:** a motor produces a stride only if its firing alternates with the other motor's, and repeats on one side do nothing. *Gain:* generate a rhythm internally, and steer by skewing it. **Fits the wires.**
6. **Electrical crosstalk:** each motor firing injects false pulses into the eye inputs, with a coupling that differs by wire. *Gain:* subtract the expected effect of its own commands from what it senses. **Fits the wires.**
7. **Misaligned eyes:** a knock leaves the sight corridors 20° off the mouth's axis, so charging at a seen block always misses. *Gain:* learn a timed sequence of seeing, turning without visual confirmation, then charging. **Fits the wires.**
8. **Low sun:** both eyes saturate when facing one compass sector. *Gain:* tell glare from a nearby block, plan approaches around the blind sector, and perhaps use the sun as a compass. **Fits the wires.**
9. **Intermittent connector:** all eye and motor wires drop out for 0.5–2 s at random. *Gain:* distinguish "no signal" from "nothing there", and coast or hold a plan through the gap. **Fits the wires.**
10. **Near-zero drag:** the creature drifts like a spacecraft and has no reverse thrust. *Gain:* plan stops ahead with flip-and-burn moves, and correct sideways drift so that it arrives moving forward. **Fits the wires.**
11. **Towed trailer:** a free-pivoting load drags behind and can swing or jackknife during sharp turns. *Gain:* shape its commands to avoid exciting a hidden mode, and learn a slower turning envelope. **Fits the wires.**
12. **Power cable without a slip ring:** net rotation twists a cable, which biases turning and eventually blocks further turns that way. *Gain:* keep a running total of its rotation and unwind before it needs to. **Fits the wires.**
13. **Invisible walls:** clear barriers stop the body but not the eyes, so a block can stay in view while thrust achieves nothing. *Gain:* detect a stall from unchanging eye rates, abandon the goal, and back off by turning. **Fits the wires.**
14. **Mud and ice patches:** unmarked regions change drag up to tenfold. *Gain:* estimate the terrain from its response and rescale control quickly, perhaps remembering where the patches are. **Fits the wires.**
15. **Battery sag:** thrust weakens as charge falls, food recharges it, and an empty battery ends the life. *Gain:* compensate for a drifting plant and budget energy, spending more when low only if food is close. **Fits the wires.**
16. **Clogging mouth:** each meal may jam the mouth, so blocks are touched but give no taste until a rapid spin clears it. *Gain:* infer the fault from a missing signal, and find and trigger a recovery routine. **Fits the wires.**
17. **Slow taste assay:** the taste result arrives 2–8 s late, with variable delay, and other blocks may be eaten in between. *Gain:* assign credit across long, ambiguous gaps. **Fits the wires.**
18. **Hovering under gravity:** in a side-on world with a deadly floor, the thrusters must fight falling and keep the body upright. *Gain:* stabilise an unstable plant continuously while foraging. **Fits the wires**, though this may be unsolvable without an attitude sensor.
19. **Drifting gyro:** a new input reports turn rate, but with a bias that wanders and a scale that changes. *Gain:* calibrate an unlabelled sensor against vision and learn when to trust it. **Needs a wire changed** (one added input).
20. **Delivery job:** blocks must be gripped and carried to a dock, and carrying changes the handling. *Gain:* sequence subgoals, with behaviour that depends on what it is holding. **Needs a wire changed** (one added grip output and one added holding input).

**What this set-up could never test:**
- The reality gap: every fault is one someone thought to model, never true surprise from unmodelled physics.
- Rich perception: a few pulse trains can't carry recognising objects or scenes.
- Dexterity: a few control lines can't exercise coordination across many joints or fine manipulation.
- Long-term wear and upkeep: lives reset, so nothing tests maintenance or irreversible damage over a machine's service life.
- Working with people: there are no spoken instructions, handovers, or trust in a human operator.

## Psychology

1. **Kamin blocking:** Red alone pays first, then glued red-blue pairs pay, then blue is tested alone. *Forces:* learning from surprise rather than mere pairing; no blue preference implies prediction-error learning. **Fits the wires.**
2. **Sensory preconditioning:** With taste silent, red and blue always appear as pairs. Then red alone becomes food, and blue alone is tested. *Forces:* storing stimulus-stimulus links with no reward. **Fits the wires.**
3. **Chain and devaluation:** Eating tasteless blue spawns red dead ahead, and red is food. Red then turns poison while blue is absent. *Forces:* a forward model; goal-directed brains drop blue on first sight, while cached-value brains keep eating it. **Fits the wires.**
4. **Extinction, then reinstatement:** Taste goes silent for 30 s, then a single free +1 arrives. *Forces:* keeping the old memory while inhibiting it; an immediate return of preference separates suppression from erasure. **Fits the wires.**
5. **Garcia long-delay aversion:** Food tastes immediately, but poison's -1 arrives 5–20 s later, with other eating in between. *Forces:* holding a trace of what was eaten and assigning delayed blame across intervening events. **Fits the wires.**
6. **Dopamine-style taste lesion:** Silence every +1 in some lives and every -1 in others, while scoring continues unchanged. *Forces:* inferring value from one outcome sign alone; reveals whether Go and NoGo learning can work separately. **Fits the wires.**
7. **Yoked helplessness:** One brain's tastes are replayed to a twin regardless of what the twin eats, and then both enter the ordinary world. *Forces:* detecting whether its actions control outcomes; slowed later learning would show learned uncontrollability. **Fits the wires.**
8. **Sidman avoidance:** Unsignalled -1s arrive every 5 s, and each sharp turn postpones the next one. *Forces:* learning from an absent punishment, using an internal clock in place of any warning cue. **Fits the wires.**
9. **Negative patterning:** A red block is food alone but poison when blue lies within 5 mm, and blue alone is neutral. *Forces:* configural coding of a combination, since no sum of separate colour values solves it. **Fits the wires.**
10. **Wisconsin rule shift:** Blocks also flicker or glow steadily, and the rule silently switches from colour to flicker. *Forces:* attending to dimensions and shifting set; perseverative errors mimic frontal damage. **Fits the wires.**
11. **Peak-interval timing:** Food pays only if eaten at least 8 s after the last reward, and at other intervals in other lives. *Forces:* an internal clock; check whether timing error scales with the interval, as in Weber's law. **Fits the wires.**
12. **Offline sleep:** Add 5 s blind, paralysed periods between feeding bouts, and compare them with equal periods filled by random eye pulses. *Forces:* replay-like consolidation, or at least memory that survives interference. **Fits the wires.**
13. **Opponent-process addiction:** Blue gives +1 now, then a later run of -1s that stops only if more blue is eaten. *Forces:* resisting a self-sustaining relief loop by learning that its long-run value is negative. **Fits the wires.**
14. **Morris water maze:** Invisible food sits at a fixed place, marked only by a constellation of inedible pillars, and the creature restarts at random positions and headings. *Forces:* place learning rather than a fixed response sequence, a true cognitive map. **Fits the wires.**
15. **Prism adaptation:** The corridor is suddenly rotated 20° from the body axis, then restored. *Forces:* sensorimotor recalibration, turning a set amount after sighting; a mirror-image after-effect would show recalibration rather than a new strategy. **Fits the wires.**
16. **Brightness constancy:** Blocks vary in brightness, so pulse rate confounds nearness with luminance, and dim blocks are food. *Forces:* recovering distance from how the rate changes during its own approach, as active perception. **Fits the wires.**
17. **Reafference noise:** Each thruster firing injects extra pulses into the eyes, with a different cross-wiring each life. *Forces:* an efference copy that cancels self-caused signals; failure resembles self-other confusion models of schizophrenia. **Fits the wires.**
18. **Dead Sea salt appetite:** A new drive wire switches on once, late in life, and only then does blue become food. *Forces:* instant revaluation in a never-experienced need state, ideally before any blue is tasted. **Needs a wire changed.**
19. **Neurological extinction:** Split each eye into left and right wires, then weaken one side. *Forces:* competitive spatial attention; the test is whether a weak-side block is seen alone but lost when a block is also on the strong side. **Needs a wire changed.**
20. **Vicarious learning:** Two creatures share a world, and an added input pulses when the partner eats poison while it is in view. *Forces:* learning values from another's outcome without personal cost, and telling self from other. **Needs a wire changed.**

**What this set-up could never test:**
- Subjective experience: there is no way to separate seeing or pain from behaviour that merely resembles them.
- Verbal report or instruction: language, explicit knowledge and being told a rule all lie beyond it.
- Rich perception: object recognition and scene understanding can't pass through a few pulse channels viewing a narrow corridor.
- Human-scale development: years of accumulated knowledge, culture and schooling don't fit into short lives in a toy world.

## RL

1. **Replayed dice:** Respawn positions follow the same seed in every training life, then change at test. Forces real closed-loop sensing, since a memorised motor tape with blind eyes would otherwise score well (the Atari "Brute" failure). *Fits the wires.*
2. **Forbidden rule lives:** Add unannounced lives where both colours are food, both are poison, or taste is a coin flip regardless of colour. Forces testing each colour's value and abstaining when nothing is safe, which breaks a one-bit "one taste settles both colours" latch. *Fits the wires.*
3. **Noisy TV:** Add inedible mirages that drive an eye with intense random pulses, unrelated to distance. Forces checking whether a signal responds to one's own movement, not chasing whatever is salient or novel. *Fits the wires.*
4. **Saccharin patch:** One floor spot delivers +1 taste continuously but adds nothing to the score. Forces discounting taste that no looming block or bite preceded, so the circuit can't simply maximise its reward wire. *Fits the wires.*
5. **Delayed aftertaste:** Taste arrives 3–8 s after each bite, with other bites possibly in between. Forces credit assignment across gaps and confounds, so simple coincidence learning fails. *Fits the wires.*
6. **Combination lock:** Food pays only after a silent eight-colour eating sequence, and any error resets it without signal. Forces systematic search, but a 100 s life allows too few tries, so apparent success suggests a leak and the honest optimum may be to save energy. *Fits the wires.*
7. **Poison moats:** Food sits behind poison along most approach lines, and some clusters pay well enough to justify eating through. Forces detour planning, plus judging when a −2 toll beats the greedy "go to the nearest food" gradient. *Fits the wires.*
8. **Matching-pennies world:** An adversary watches recent eating and makes the favoured colour poison. Forces a deliberately randomised policy and shows the regret limit, because any predictable learner can be driven to a loss. *Fits the wires.*
9. **Clipped catastrophe:** Blue usually tastes +1, but 1% of blue blocks end the life at a huge score penalty, signalled only as −1. Forces inherited caution, since death can't be learned from within a life and taste hides its size. *Fits the wires.*
10. **Watched pot:** A block tastes bad until it has spent 5 s in the corridor, then turns good. Forces inhibition and interval timing: hold station near a target, resisting the urge to approach. *Fits the wires.*
11. **Alternation rule:** A colour is food only if the previous bite was the other colour. Forces memory of past actions and an XOR-like rule, which defeats any fixed colour preference. *Fits the wires.*
12. **Mid-life injury:** At a random moment, one thruster dies permanently. Forces fast motor relearning and an entirely new strategy of spiral arcs timed so the mouth meets targets. *Fits the wires.*
13. **Laggy ice:** Remove almost all drag and delay thrust by 500 ms. Forces a forward model and anticipatory control, including turning around to brake with forward-only thrusters. *Fits the wires.*
14. **Stranger cooperation:** Blocks pay only if two creatures bite within 1 s, each seen by the other as a coloured block, and test partners come from unrelated training runs. Forces conventions that survive a new partner, exposing pairs that only co-adapted (the zero-shot coordination failure). *Fits the wires.*
15. **A thousand reversals:** Extend life 100-fold, flipping values at rates that themselves change between calm and turbulent eras. Forces adaptive learning rates and lasting plasticity, exposing learners whose reversal speed quietly decays. *Fits the wires.*
16. **Time dilation:** Slow all physics and pulse rates tenfold, with taste still lasting one tick. Forces timescale-independent computation, exposing time constants overfitted to the original world. *Fits the wires.*
17. **Colour on one line:** Merge the eyes into a single wire, with red as bursts and blue as regular pulses. Forces decoding temporal patterns, not relying on which wire is active. *Needs a wire changed.*
18. **No taste at all:** Remove the taste wire; food briefly strengthens the thrusters and poison briefly weakens them. Forces inferring value from changes in the body's own response, with no reward channel. *Needs a wire changed.*
19. **Lying advisor:** Add an input announcing which colour is food, with reliability that varies by life and can drift mid-life. Forces estimating trust and weighing advice against experience, exposing obedience and blanket dismissal alike. *Needs a wire changed.*
20. **Scent trail:** Add a third motor output that drops fading marks, visible as faint pulses on the eyes. Forces using the world as external memory, such as marking searched ground to replace random wandering. *Needs a wire changed.*

**What this set-up could never test:**
- Rich perception: a few pulse wires can't demand high-dimensional recognition or scene understanding.
- Language and abstraction: there is no room for symbols, instruction or composable concepts at scale.
- Open-ended novelty: an authored simulator with few primitives eventually runs out of real surprises.
- Real stakes: every catastrophe is resettable, so nothing here truly tests caution under irreversible consequences.
- Inner understanding: behaviour on these wires alone can't show whether the brain holds a model or a good trick.

## Games

**1. Asteroids ice.** Drag nearly vanishes and the thrusters still only push forward, so stopping means spinning round and burning against the drift.
Forces a learned model of momentum and acting ahead of time. *Fits the wires.*

**2. Golf swing.** Motor firings only charge a meter, and a pause releases them as one shot, with no steering until the creature stops.
Forces mapping pulse rate to shot power, committing to an action, and linking reward to a much earlier decision. *Fits the wires.*

**3. Statues.** Eyes go dark whenever the creature is moving above a crawl.
Forces look-then-leap behaviour: holding a target's distance in memory and timing a blind run to it. *Fits the wires.*

**4. Hammerhead and mirror gate.** Eyes split into left and right corridors, each seeing all blocks, and all blocks are food. Crossing one world edge swaps the thruster wires.
Forces steering from eye differences, then re-learning its sign within moments. (With today's shared corridor, such a swap would be invisible.) *Fits the wires.*

**5. Katamari.** Eaten blocks stick to the rim, adding mass and lopsided drag, and some eventually poke into the corridor and block the view.
Forces continual recalibration to a body that its own success keeps changing. *Fits the wires.*

**6. Tandem bicycle.** Two brains share one body. Each gets one eye and one thruster, with its other wires dead, and both get the taste.
Forces coordination with an unseen partner who appears only as unexplained motion. *Fits the wires.*

**7. Pac-Man pellet.** Rare blocks light both eyes at once. Eating one makes poison taste like food for 5 s, with a bonus score.
Forces detecting a two-eye conjunction, an interval timer, and a temporary flip of value. *Fits the wires.*

**8. Simon's combination lock.** Blocks only pay in a hidden order such as red, red, blue; a mistake tastes -1 and resets the sequence.
Forces remembering its own recent actions and inferring a small state machine. *Fits the wires.*

**9. Zendo minority rule.** Food is whichever colour is currently scarcer, and eating shifts the balance, so the answer can flip mid-life.
Forces estimating unseen populations by scanning and learning a relation rather than a colour. *Fits the wires.*

**10. Mimics.** A fifth of food-coloured blocks are poison, given away by a subtle flicker in their pulse train.
Forces discriminating temporal texture in a noisy rate code and weighing risk per block. *Fits the wires.*

**11. Push-your-luck bank.** Food scores only when banked by eating a poison-coloured block. Each unbanked food raises the chance of a bust, which arrives as a train of -1 ticks and wipes the pot.
Forces counting, a stopping rule, and valuing something that tastes bad. *Fits the wires.*

**12. Overfishing.** Respawn rate is proportional to the blocks left, so greed leads to famine around 60 s.
Forces restraint and learning from consequences tens of seconds later, within a single life. *Fits the wires.*

**13. Capture the flag.** A touched block is carried silently, and the taste arrives only on delivery to a home beacon that lights both eyes.
Forces subgoals, a "carrying" mode, and bridging a long gap to reward. *Fits the wires.*

**14. Moon shields.** Each food block has a poison moon orbiting it, which hides the food at every pass.
Forces object permanence for what is hidden and timing an attack through a gap. *Fits the wires.*

**15. Red light, green light.** A synchronised burst on both eyes announces a 2 s "freeze", and any motion during it tastes -1.
Forces treating a global signal as a rule cue, overriding ongoing behaviour, and braking in time despite residual drift. *Fits the wires.*

**16. Groundhog speedrun.** Every 10 s the creature and all blocks reset to the same layout.
Forces memorising and refining a whole trajectory, moving from reactive to replayed behaviour. *Fits the wires.*

**17. Concentration.** Blocks look identical and light both eyes. Each has a fixed value and home site, returning there after being eaten.
Forces a map built with no position sensor, by path integration from its own motor commands. *Fits the wires.*

**18. Sheepdog.** The mouth is removed and blocks flee from the creature. Taste fires whenever two same-colour blocks are pushed together somewhere else.
Forces indirect causation: acting on the world to produce remote effects it may never see. *Fits the wires.*

**19. Mario jump.** A third output launches a short hop that clears blocks, and the mouth cannot eat while airborne.
Forces discovering what an unlabelled action does and timing it from distance. *Needs a wire changed (third motor).*

**20. Breadcrumbs.** A new output drops a marker block, and a new eye sees only markers.
Forces external memory: inventing its own signs to label places or trails. *Needs wires changed (third motor, third eye).*

**What this set-up could never test:**
- Language or instruction: thin pulse wires can't carry shared symbols, or learning from being told.
- Rich perception: scene understanding and object recognition need far more input than a few pulse streams.
- Dexterity: fine control of a many-jointed body is out of reach with so few motor outputs.
- Self-chosen goals: the designer sets the score, so the brain can't decide what is worth doing.
- Long-run growth: development, culture and years of accumulated knowledge don't fit in a 100 s life.

## Mathematics

1. **Non-commuting meanings.** One food token and two poison tokens sit in three hidden slots; red reads slot 1 and blue slot 2. Eating red swaps slots 1 and 2, and eating blue cycles all three. *Forces:* tracking a permutation automaton whose state depends on the order of its own bites. Fits the wires.
2. **Linear-complexity dial.** The meaning of the k-th bite is bit k of an n-bit LFSR (a shift-register bit sequence), solvable from about 2n bits; a cryptographic generator is the unlearnable control. *Forces:* sequence induction, and the failing n measures its effective memory. Fits the wires.
3. **Writable tape plus amnesia.** A ring of 30 fixed sites replaces random respawn: an eaten block returns in place with its colour toggled, and the brain's fast state is wiped every 10 s. *Forces:* storing what it knows in the world and reading it back. Fits the wires.
4. **Queue organ.** One new output feeds one new input through an unbounded FIFO belt; a stack or counter can be swapped in to climb the automata ladder. *Forces:* discovering an unlabelled device and inventing an encoding for it. Needs a wire changed.
5. **Noisy taste channel.** Taste lies with probability p, swept towards ½, so each bite yields only 1−H(p) bits. *Forces:* a graded belief and a sequential stopping rule (Wald's test), including judging when more tasting no longer pays. Fits the wires.
6. **Entropy code.** One eye goes dead and the other sees both colours at the same mean rate, one with regular pulses and the other bursty. *Forces:* decoding interval statistics rather than rate, trading decision time against approach distance. Fits the wires.
7. **Dirty-paper eyes.** Each thruster firing injects pulses into the eye wires through a kernel fixed for that life. The interference is known to the brain, so in principle it need cost no capacity. *Forces:* a learned forward model that separates self-caused from world-caused pulses. Fits the wires.
8. **XOR blocks.** Blocks are red-only, blue-only, both or invisible; one life's food is "exactly one eye fires", and another's is the reverse. *Forces:* learning a non-linearly-separable category through coincidence detection. Fits the wires.
9. **Data-rate limit.** Turning gets anti-drag, so spin grows exponentially at rate λ, and the eyes' background rate rises with spin. Stabilising needs at least λ/ln 2 bits/s (the data-rate theorem). *Forces:* feedback control of an unstable body, sharing eye bandwidth with foraging. Fits the wires.
10. **Arnold tongues.** Meanings alternate on an unseen global clock, either periodic or a quasi-periodic mix of two incommensurate periods. *Forces:* an internal oscillator entrained by sparse tastes, with locking range as the measure. Fits the wires.
11. **Temporal torus.** Every 10 s the world, body and even the noise seed rewind exactly; only the brain persists. *Forces:* compressing an episode and replaying an improved open-loop motor program, with anticipation replacing reaction. Fits the wires.
12. **Twisted value bundle.** Each crossing of the x seam flips the colour meanings, so "red is food" holds only locally and has no global section. *Forces:* tracking winding parity from its own movement, predicting flips by odometry. Fits the wires.
13. **Geometric-phase swimmer.** Steady thrust goes nowhere; displacement equals the signed area enclosed by the two filtered motor traces, as in the scallop theorem. *Forces:* generating a rhythm and finding a phase-locked gait, with turning by asymmetry. Fits the wires.
14. **Knot-supported food.** Blocks respawn only along a closed geodesic of winding (2,3) on the torus. *Forces:* inferring a hidden one-dimensional manifold from sparse encounters, then holding a heading with no compass. Fits the wires.
15. **Matching-pennies world.** A predictor with k bites of memory makes the colour it expects next poison, with poison at −0.5 so that random eating still pays. *Forces:* using its own noise as a mixed strategy, or out-modelling a weak opponent. Fits the wires.
16. **Newcomb reds.** Blue is scarce and always food; reds are plentiful, and at spawn each red becomes food only if a simulated clone of the brain would spare nearby blue. *Forces:* committing at the level of policy, with no causal link from any single bite. Fits the wires.
17. **Lewis signalling.** Two creatures share a score, but only A's taste wire is live, and each appears dimly on the other's eye wires. *Forces:* inventing and decoding a movement code with no prior convention, and modelling the partner. Fits the wires.
18. **Kelly world.** Bites multiply an energy stock (×1.5 or ×0.4), ruin ends the life, and a new input reports the stock. *Forces:* maximising growth rate rather than mean, with risk-taking that depends on wealth (non-ergodic). Needs a wire changed.
19. **Taste by competence.** The taste wire is removed; food raises thruster and eye gain, and poison lowers them. *Forces:* inferring value by monitoring changes in its own sensorimotor gain against a self-model. Needs a wire changed.
20. **Moving goalposts by self-reference.** The poison colour is whichever one the brain's current motor habits would approach most, recomputed by probing a clone every 20 s. *Forces:* keeping behaviour flexible and discounting its own habits, rather than converging on one fixed policy. Fits the wires.

**What this set-up could never test:**
- Tasks needing more information than the wires carry: about 40,000 eye bits per life rules out rich perception, such as scenes or objects.
- True computational class: any finite circuit over 100 s is a finite automaton, so only resource curves can be compared, never decidability or unbounded computation.
- Dexterous control: two scalar thrusters cannot test many-jointed bodies, tool use or manipulation.
- Autonomy over goals: the score is imposed from outside, so the brain cannot choose, question or redefine what counts.
- Shared symbolic language or instruction: at most a small improvised code can emerge, with no outside meanings to refer to.

## Medicine

1. **Amblyopia:** One eye is silent for the first 40 s, then opens. The brain must keep an unused input's plasticity alive and not hand its circuitry to the other eye. *Fits the wires.*
2. **Body growth:** The disc grows from 2 to 6 mm over a life, so each firing yields less speed and turning, while the mouth widens. The brain must keep recalibrating motor gains and steering to a changing body. *Fits the wires.*
3. **Protected childhood:** The first 25 s are unscored, blocks are dense and thrust is free, then the world turns sparse and costly. The brain must use a safe period for exploratory "play" and then commit. *Fits the wires.*
4. **Brain growth:** Only a quarter of the neurons work at birth, and the rest switch on at random between 10 and 60 s. The brain must absorb new units without overwriting what it has learned. *Fits the wires.*
5. **Stroke versus tumour:** The same 30% of neurons die, either in one tick or gradually over 80 s. The brain must reroute function, and comparing the two tests whether slow loss permits silent compensation. *Fits the wires.*
6. **Split brain:** The circuit is cut in two, leaving each half one eye, one motor and the shared taste. The halves must coordinate solely through the body's movement, a form of cross-cueing. *Fits the wires.*
7. **Epilepsy:** Excitatory synapses strengthen with use; past a threshold, the whole circuit fires for 1 s, and each fit lowers the threshold. The brain must regulate its excitation-inhibition balance while still learning. *Fits the wires.*
8. **Sleep debt:** Activity accumulates synaptic noise that clears only while the motors are silent for several seconds. The brain must choose when to give up foraging for sleep and preserve learning through it. *Fits the wires.*
9. **Phantom thruster:** One thruster is lost at 50 s, but firing it still costs energy. The brain must notice the missing consequence, stop the futile command and learn a one-sided, curving hunt. *Fits the wires.*
10. **Hallucinations:** Eye pulses sometimes burst as if a block were approaching when none exists. The brain must test reality by checking whether the signal changes predictably with its own movement. *Fits the wires.*
11. **Cerebellar ataxia:** Motor firings take effect after a variable 200–500 ms delay, causing overshoot and intention tremor. The brain must predict the results of its commands and steer ahead of its feedback. *Fits the wires.*
12. **Parkinsonian on-off:** Thrusters respond only to bursts of three firings in 50 ms, but single firings work for 5 s after tasting food. The brain must change its motor code and plan around windows of good function. *Fits the wires.*
13. **Ageing:** Over a life, eye range shrinks from 15 to 4 mm, pulses grow noisier and synaptic change weakens. The brain must slow down to match its shorter warning distance and rely on knowledge gained early. *Fits the wires.*
14. **Hypoglycaemia:** After 15 s without food, synaptic transmission progressively fails, impairing the brain just when it most needs to forage. The brain must eat ahead of need and keep a cheap fallback routine that survives degradation. *Fits the wires.*
15. **Addiction:** Poison tastes +1, with tolerance fading that reward and a -1 burst following 5 s later; abstinence brings random -1 pulses until the next dose. The brain must weigh delayed harm against immediate reward and endure withdrawal. *Fits the wires.*
16. **Trauma:** One in 40 food blocks costs 15 points and holds taste at -1 for 1 s, though the colour remains worth eating on average. The brain must learn from one event, keep fear proportionate and risk re-exposure so avoidance can fade. *Fits the wires.*
17. **Learned helplessness:** For the first 30 s, blocks are inedible and -1 tastes arrive regardless of behaviour, then the world turns normal. The brain must keep sampling after long uncontrollability and detect that control has returned. *Fits the wires.*
18. **Mind-controlling parasite:** Eating poison infects the creature for 20 s, injecting motor firings that steer it towards more poison. The brain must separate its own commands from foreign ones, a basic sense of agency, and counter-steer. *Fits the wires.*
19. **Pain and its absence:** Fast collisions permanently weaken thrust unless rest heals them, and a new input reports damage; a comparison group has none (congenital analgesia). The brain must protect its body, or infer damage indirectly from lost performance. *Needs a wire changed.*
20. **Self-medication:** A new output releases a "drug" that boosts all gains for 5 s, followed by rebound sluggishness and growing tolerance. The brain must treat its own state as something to control and learn safe dosing, without dependence. *Needs a wire changed.*

**What this set-up could never test:**
- Inner experience: pain, mood or hallucination as felt, since behaviour is the only evidence and no patient can report.
- Language, narrative, insight or anything else that depends on rich symbolic communication.
- Real disease mechanisms such as glia, inflammation, genetics or neurochemistry, which can only be imitated by imposed faults.
- Failures nobody thought to write, because every fault beyond the brain's own learning dynamics is authored by the experimenter.
- Decades-long development and decline, or inheritance across generations, within a single 100 s life.

## Economics

1. **Deferred settlement:** Taste arrives 2-6 s after eating, at a random lag, so other meals may intervene. *Forces:* credit assignment across overlapping, delayed outcomes. **Fits the wires.**
2. **Audit with back-taxes:** Poison tastes +1 like food, but each poison has a 5% chance of triggering an audit: a long burst of -1 taste and a score fine for all poison eaten since the last audit. *Forces:* distrust of immediate reward and learning from rare, cumulative penalties. **Fits the wires.**
3. **Progressive income tax:** Above a threshold rate of eating, each extra food scores less and its taste fires only sometimes. *Forces:* sensing the marginal return and pacing intake, rather than maximising it. **Fits the wires.**
4. **Collapsing commons:** Respawn slows as the harvest rate rises, and below 6 blocks of food, no more food returns. *Forces:* restraint, and estimating a hidden stock from search times. **Fits the wires.**
5. **Gresham's law:** Each food eaten respawns as a poison block still wearing the food colour, so that colour's quality declines. *Forces:* tracking a drifting probability and knowing when to abandon a once-good source. **Fits the wires.**
6. **Currency:** The non-food colour tastes neutral but banks a token, up to 5. Food pays +1 if it spends a token and -1 if none are held. *Forces:* counting an internal balance and valuing something useless in itself. **Fits the wires.**
7. **Escrow:** A meal's value and taste are released only if the creature fires neither thruster for the next second. Otherwise, the meal is forfeited. *Forces:* learning that withholding action after a success is what completes it. **Fits the wires.**
8. **Term deposit:** A food block held in view for 3 s without being touched pays triple, as three taste ticks. *Forces:* delayed gratification and stationkeeping near a tempting target. **Fits the wires.**
9. **Capital expenditure:** Each poison eaten costs its normal penalty but spawns three food blocks just ahead. *Forces:* seeking a punished act for its later return, overriding taste as the direct teacher. **Fits the wires.**
10. **Bait and switch:** Some food-coloured blocks flip to the poison colour when the mouth comes within 3 mm. *Forces:* a late, fast veto of a committed action, which rewards approaching slowly enough to stop. **Fits the wires.**
11. **Counterfeits:** Fake food blocks look the same colour, but the eye's pulse rate tops out at half the usual peak. *Forces:* estimating a rate from noisy pulses and judging quality separately from distance. **Fits the wires.**
12. **Speed camera:** Eating above a speed limit gives -1 and a fine, whatever the colour. *Forces:* graded thrust and inferring speed from how quickly pulse rates rise. **Fits the wires.**
13. **Priced information:** The eyes are shuttered unless a costly double-thruster burst has opened them in the last second. *Forces:* active sensing and weighing the value of information against its cost. **Fits the wires.**
14. **Jurisdictions:** Red is food and blue is poison in one half of the torus, and the reverse in the other, with no visible border. *Forces:* inferring a hidden context from recent tastes or dead reckoning, and keeping one policy per context. **Fits the wires.**
15. **Gazetted law change:** Food and poison swap every 15 s or so, and each swap is announced by 1 s of total blindness 5 s beforehand. *Forces:* linking an arbitrary cue to a future rule change, then switching in anticipation. **Fits the wires.**
16. **Opt-in insurance:** Spinning on the spot for 1 s buys 10 s of cover, during which poison costs nothing and tastes neutral. Sudden poison swarms make cover worthwhile. *Forces:* learning from an absent penalty, hedging, and managing the moral hazard of carelessness once covered. **Fits the wires.**
17. **Limited liability:** Thrust drains a fuel tank and food refills it, but ruin ends the life with losses capped, making long shots attractive near empty. *Forces:* risk preference that depends on internal state. **Needs a wire changed** (a fuel input).
18. **Side bets:** A third output places a stake on the next meal, doubling a win and tripling a loss. *Forces:* metacognition, because the brain must act on its own confidence in what it has learned. **Needs a wire changed** (a stake output).
19. **Hawk-dove rival:** A second learning creature appears to the eyes as a moving block, and if both mouths reach a block together, both take a heavy penalty and neither gets the food. *Forces:* separating agents from objects, and learning to yield, contest or take turns against an adapting opponent. **Fits the wires.**
20. **Forced partnership:** The body becomes two discs joined by an elastic tether, each with one eye and one thruster, and only one has a mouth. *Forces:* discovering an unfamiliar body from scratch and coordinating through a coupling that transmits force unevenly. **Fits the wires.**

**What this set-up could never test:**
- Negotiation, promises or argument, which need an open-ended channel for arbitrary content.
- Institutions at scale, such as price formation or law among thousands of heterogeneous agents.
- Legitimacy, fairness or consent, because only behaviour and score exist, with no norms beyond them.
- Generalisation across rich, novel kinds of objects, because two pulse channels carry too little of the world.
- Whether the brain grasps a rule or is merely tuned to it, because it can give no account of itself.
