# The programme

One page to keep us on track. The goal and its test are in `README.md`, The goal. If work can't move the scaling curve, it is parked in `QUESTIONS.md`.

**Our question, in one line** (adopted from the review of 2026-11-11, `lab/v/review_2026-11-11.md`): can compact, local, reusable mechanisms learn to predict through action, use sparse rewards to select useful behaviour, and grow their capacity without anything allocating it from outside? Its ingredients have names already (learning by exploring before reward: Plan2Explore, Sekar et al. 2020; information-driven, decentralised control of a body: Martius, Der and Ay 2013); what would be ours is doing it locally, compactly and with growth.

## Now: the growing network (the user, 2026-11-12)

The user's idea, after Dan Goodman's talk and Béna & Goodman 2025 (*Nature Communications*, "Dynamics of specialization in neural
modules under resource constraints"): little blocks appear locally, each learns to detect a situation; duplicates are found and one
removed; other blocks build on them, each kept distinct; growth has no goal and is limited only by the resources available; a block whose
output is never used fades, and its fading prunes back everything only it supported. It subsumes the plan to bolt coupling, turns, play
and hunger into one brain: they become things such a network might grow. Built as `lab/grownet.py` (predictions
`lab/v/grownet_predictions.md`), first on the sequence ladder against D40's tree, which is the hand-shaped case (its recruits' partners
fixed, never pruned).

From the paper, three measures: specialisation measured, not assumed (bits each block carries about each feature: separate blocks don't
guarantee separate jobs); it should appear only when the world's features are separable and supply is tight; jobs may shift over time, so
nothing is frozen, and a block whose job moves elsewhere loses its users and is recycled. From the talk (the user): competition for energy,
the blood supply, encourages modularity (one module very active leaves less for others; the sheet brain's idea, nca-learn): a variant in
which the blocks firing at a moment share a fixed supply for learning and growth.

**Plan: the growing network on the body** (the user, 2026-11-12: "build the plan and execute"). Peel away, one at a time, what we
still hand the network, each step judged on the same lessons (patterns 5 and 11 steps long, the last 2 and 3 colours eaten, and the plain
world) against the step before, with the same material:
- B1, no symmetry told. Today a taste is translated for the network: a bad taste of one colour is read as "the other is food", which
  builds in that exactly one colour is food. Instead each block keeps a small table of what each choice led to (which eye it followed,
  good or bad) and prefers the eye with the better record. It must learn from experience what the other eye would have given.
- B2, events in continuous time. Streams tick not only at tastes but at the body's own pulses (each eye's, each motor's), so a block can
  learn what comes before a taste (which eye was firing on the approach), instead of our rule "what was eaten is the eye that pulsed
  last".
- B3, steering grown. The block that wins says which eye to approach today; next, its readouts drive the motors directly, with play to
  explore, replacing the starting brain's fixed approach circuit (the new parts of D55 to D58 come back here).
Each step keeps the previous result if it costs nothing on the lessons, and is recorded (and parked) if it does.
B1 done (D59): untold the symmetry, the network first never steered (an explore-or-exploit problem the hint had hidden); choosing who steers by sampling each source's record cures that; the remaining cost, .1 to .27, is the halved evidence. Parked as a measured price; B2 builds on the told version.
B1 revised (R22-R23): the price was the change of steering, not the readouts; scoring every source whose choice was eaten makes told and untold equal, leaving the price of exploring (.05 to .15; plain world -.10). The user's local competition (R28-R32): siblings share their parent's supply, standing including credit passed down from users (trophic): ties the written clean-up rules in both worlds on two seed sets, the first generic clearer with no stable-world cost. B2's first step (R25-R26): the vouching rule isn't needed (-.10 in the plain world); with both hints gone the lessons hold but the plain world costs .37 (false poisons feed exploring).

**Then**: a stream for every sense line (every taste, good, bad, red eaten, blue eaten): the network picks the right one for each lesson and matches our chosen streams with the same material each (R20). Next: the growing network on the body (senses, taste and thruster pulses), its guesses steering.

**Since**: (4) size follows the problem: blocks 17 to 48 for patterns 2 to 17 steps long, and the share learned rises with material to about 50 blocks, then levels; the economy (conserved credit along the graph, rent, parents funding newborns) does the clearing out the written rules did when the world changes; (5) without our chosen streams: one stream of every taste ties on the combination lessons and loses on the pattern lessons; separate sense lines with clocks lose further: finding which clock matters is the open problem.

**So far** (D59): (1) matches the tree, and is solved on 17 letters where the tree isn't; (3) relearns a changed word (+1.01 against the tree's -.34, fresh seeds), and removing duplicates, not fading, does it. Next: (2) the energy supply.

Stages: (1) the network on the sequence ladder, against the tree, with material plentiful and scarce; (2) the energy supply; (3) the
world changing mid-life (a new hidden word): do the old blocks fade and new ones grow; (4) does block count follow the bits the world
needs, rung by rung; (5) the same blocks over the body's senses and actions (the new parts, D55 to D58).

**Overnight, 2026-11-12/13** (D59, D60): the best generic brain so far is ten streams (every kind of event times one recorded sense), recycling on demand, strict copies (a fault in spotting copies found and fixed; it had been doing the clearing credited to copy removal). It climbs sequences to 17 and combinations to 5 of 6 as material grows, relearns a changed pattern at no loss (beating the tree by 2.2), does no harm where nothing is to be learned, and works on the muscle body; given 60 own clocks re-phased by revealed changes it reached timing rung 2 on development seeds but not on fresh ones (.37 to .47). One design holding every stream and the clocks comes within .15 of each ladder's specialist (R67). With recruitment off it is surely worse on sequences (part 3). Not told the symmetry, it pays only the cost of exploring; the vouching rule is unnecessary.

**The scaling curve** (D60): the generic brain climbs the sequence ladder as material doubles, 3 to 13 to 17 (fresh seeds), the scaling test's first part passing on one ladder; combinations climb once and stall; timing nothing (no clock set by the world's changes). Next: what combinations and timing need (a block joining two streams; clocks whose phase the world's changes set), within the same generic brain.

## Before: a brain that takes up new parts (the user, 2026-11-12)

**The question.** So far the brain has met mismatches with its world or flaws in its body. Now: given a new actuator (later, a new
sensor) part-way through life, can it incorporate it by itself: recruit connections to it, perhaps new blocks, and retune? Evolution
normally adds parts; here in-life learning must (the user: perhaps a rehearsal of embryonic growth). **The body:** the original
thruster (the old body, which limits the brain, D53), and then two more thrusters a side, at a half and a quarter of the original's
strength (the main session's reading of "two more thruster strengths", after muscles' recruitment by size), on four new motor lines
wired at random (the brain isn't told which is which), coming alive at a moment drawn each life, each firing costing in proportion to
its strength (assumptions to confirm with the user).

| step | what | ends when |
|---|---|---|
| G0 | The new parts in the engine, behind a switch (off: lives identical, the fingerprint check) | Built and checked |
| G1 | The yardstick: a hand-designed brain told the wiring, using the new thrusters, against the starting brain, on plain and lopsided bodies and touching pairs | A certified gap somewhere, or a measured reason why none: if none, the parts add nothing to learn |
| G2 | Incorporation in life, from generic mechanisms only: each new motor a unit, connected to the existing rhythms (scan, drive, run) by gains born at zero, tuned by D54's turn-taking units judged by coupling, with an Occam default of "not connected"; taste where speed is traded against care (D54's limit) | It closes half the yardstick's gap surely, and leaves the brain as it was where the parts don't help |
| G3 | Fresh seeds; then more parts, to see whether turn-taking scales | |

**Since** (D56, D57): hunger sets how hard to act, but its sense of normal must fit the world (fresh seeds: a fixed normal cost -.40 in the plain world); play in the lean spells changed nothing in a world lean most of the time; uptake by play scales in correctness (surely above base with 1, 2 or 4 new thrusters a side) but not in time (play 141, 243, 446 s; whole life -.15 to -.73), since interfering parts must take turns. Next: play that learns more per kick, or parts that don't interfere; then one brain with coupling, turns, play and hunger on the ladders.

**Then** (D57, D58): play until it knows what it needs (one sure thruster for each new eye line) surely helps over the whole life at every size and keeps play short up to two new thrusters a side; body and rule in one life: a new skill is worth what the knowledge directing it is worth (the interaction +.40, +.38 on two seed sets, sure on one; play surely harms a brain wrong about food). Next, for the user: whether to make the integrated brain (coupling, turns, play, hunger, the tree) the next stage, on the ladders with an acting component.

**Results so far** (`discrete/NOTEBOOK.md`, D55; `lab/v/newparts_predictions.md`). G0 built (both parts behind switches; off: identical lives). G1: the small thrusters alone are worth about 15% (the eyes are the limit); with the user's choice of a split eye as well, up to +1.0 (+45% plain, +75% touching pairs). G2: arcs judged by food fail, even over 3000 s; play first (still, one new thruster at a time, watched through the new eye) wires the arcs and surely gains on fresh seeds (+.39, with lateral inhibition between the new lines), matching the told arcs. Next: a richer reflex form (the told split-eye reflex is worth twice the arcs), play that values steering over visibility, and more parts (G3).

## Done: the muscle-like body, and every germane experiment repeated on it (the user, 2026-11-11; D53)

**Why.** Each pulse of today's thruster is a fixed kick of about 18 degrees, wider than the eyes' corridor at most distances (4 to 11 degrees), so heading control comes in coarse steps and a balanced drive is a knife-edge (D52). The user's paradigm, as muscles work: each pulse raises a thruster's activation, thrust is a sigmoid of it, so a lone pulse nudges (about 4 degrees) and a fast burst builds to strong thrust (`lab/sigmoid_body.py`; felt by hand in `lab/drive.py`). An opt-in body: world.py's stays the default, so every earlier result stands. Disciplined: the same scripts with a body switch, the same seeds, analyses frozen, old and new side by side, predictions and a ledger line each, headline comparisons confirmed on fresh seeds; one old-against-new table per experiment in `discrete/NOTEBOOK.md` (D53 on), and a line on each README finding saying whether it held.

| step | what | why |
|---|---|---|
| 0 | The body in the engine (`lab/stage2_lang/sim.py`): the reference path first, behind a switch; with it off, lives identical (the fingerprint checks); its speed measured before the fast paths | Everything runs there |
| 1 | Retune the starting brain for the new body (evolution's job, once, before any life): D13's kind of search over scan, drive and run rates, hold and boredom, on plain bodies; frozen as the new starting brain | The old numbers fit the old body (a scan at 12 pulses a second would barely turn the new one): otherwise every comparison measures a mistuned baseline |
| 2 | Yardsticks and the body ladder (D42): plain, told, which body numbers cost anything, and food against knob error | Whether the knife-edge is gone |
| 3 | Knob learners (D43): trial (D19), counters (D20), the beat-clocked register, 100 to 1000 s | |
| 4 | Play and coupling in the quiet-then-challenge frame: P1's arms (D49), partners on fast and slow play (D47, D50), coupling's peak (D51), the coupling search with and without Occam (D52), the locality tries | Occam and small-nudge learning may change most |
| 5 | Touching pairs (D41): looking and the careful driver | Fine control may make the clear side reachable |
| 6 | The ladders and the tree (D37 to D40): rungs recertified, the tree's climb rerun | The scaling test rests on it; the bulk of the CPU |

**Results so far** (`discrete/NOTEBOOK.md`, D53; `lab/v/muscle_predictions.md`): at 30 ms the starting brain forages at 63% of the old body's level (retuning bought nothing on fresh seeds, so the same brain on both). Every formula assuming thrust proportional to rate is wrong on this body: the told yardstick was recomputed (equal mean thrust), and the formula-based learners (D20's counters, D43's register, partners) now fail, while coupling still peaks at the body's own right knob (95% within .2) and the coupling search surely beats the formula (+.95). The body is steeper in the knob, not gentler: the premise that coarse kicks make a knife-edge looks overstated (no knife-edge at 0 on the old body in this frame). Touching pairs: finer control helps a little, not surely.

Not repeated: SPICE, the discrete circuits and the minimal search (the old engine; a separate question about real circuits).

## The guiding principle: understanding as coupling (the user, 2026-11-11)

**A brain optimises for the arrangement that gives the simplest connection between its inputs and its actions, in both directions** (the user). In bits: the mutual information between senses and actions, I(S; A) = H(S) - H(S | A) = H(A) - H(A | S), as the brain's own small, local predictors can capture it (per bit of model, not as an unlimited observer would). Actions make the senses predictable (a forward model); senses make the actions predictable (a policy). Unlike "make the world predictable" it has no dark room: standing still or spinning on one motor makes the senses predictable but the actions constant, so I(S; A) = 0 (which also explains D45: that self-judge measured the senses predicting themselves, not their coupling with action). One currency, three modes: play seeks experiences that grow the coupling the brain's models can capture, and stops when that stalls (bored); knobs are tuned so purposeful behaviour's coupling is high; work watches for coupling or reward falling, and goes back to play. Known relatives, to design down from: empowerment (Klyubin, Polani and Nehaniv 2005), the information theory of the perception-action cycle (Tishby and Polani 2011), predictive-information maximisation on robots (Martius, Der and Ay 2013). What would be ours: each unit measuring its own coupling, locally, in this tiny closed loop. The body and world stay as they are (the user: we learn most by pitting ourselves against this very simple task).

## The current phase: a brain that plays (the user, 2026-11-10; stages rewritten after the review, 2026-11-11)

**The criticism** (the user). We have been designing a simple, clunky brain and expecting something clever to come of it. But a brain that only scans, drives and runs meets a narrow slice of what its body and world can do, so its behaviour doesn't produce enough information to find a new stratagem. Better to start with a brain that is creative from birth: many cycles of different timings driving its movement, erratic to look at, which gives it evidence about what works; the cycles then settle on the ones that do. Rhythms, coupled cycles and knobs that retune them are in the spirit of Sepulchre (`MIXED_FEEDBACK.md`). Checked (2026-11-10): neither we nor a search found any Sepulchre work on learning (his recent papers are rhythm and event-based control: rebound winner-take-all, half-centre and ring oscillators, event phase response curves); learning in his rhythmic parts is an open direction (the user: an obvious one to explore). The nearest known form of the dance is Der and Martius's homeokinesis (*The Playful Machine*, 2012): a controller adapted by its own prediction error in a sensorimotor loop, which keeps it moving in varied, exploratory ways; a start for D2 and D3, designing down from what is known.

**What the record says.** For: the weak thruster's knob was set in minutes only once the creature did something unusual on purpose, spinning on one thruster, and watched what came of it (D20, D43). Against, as stated: variety isn't yet evidence. Judged by taste, many things varying at once are noise to each other (one score, under a bit a second): 200 random detectors each nudging a motor cost food and learned little even in very long lives (D16); exploring wildly early in a life hurt (D15); a small wobble cost a tenth of the food and took fifteen times a short life's drives to notice (D36).

**Play** (the user, 2026-11-10; README, What we've learned). Activity with no goal and no reward, which lets a brain organise itself to its body and world, so that later learning from reward is quick (latent learning, Tolman 1948). The dancing brain is a brain that plays. Play is judged by how much faster it makes later learning, not by the food it costs at the time.

**Mechanisms, not features** (the user, 2026-11-10). We keep falling back to designing in a behaviour we have seen work ("try a sweep"). The aim is a methodology by which a brain tunes and modifies itself with no understanding from us of why a circuit works, one that would carry over unchanged to far bigger brains, bodies and worlds. So stages are written as generic mechanisms (rhythms, randomness, self-judging banks) that could produce such a behaviour, and the test is whether they find it unaided. Hand-written behaviours are rulers only: D0 says what information exists, so we can tell whether a mechanism found it. **The check before every stage:** nothing in the brain may encode our understanding of this body or world: no chosen movement, no formula from a measurement to a knob (as D43's log of two periods), no gate or rate tuned to this world. Anything like that is recast as a mechanism whose job is to find it.

**The form to test.** A bank of generic rhythm units, each an oscillator with its own period, its own random mix onto the two motors and its own phase, drawn at random at birth (ranges in seconds, wide, fixed before any life). Each unit has the same generic predictor, the recording unit clocked by its own beats (D38, D43), predicting what the eyes do next. Each unit judges itself by its own prediction: how many bits its beats tell about the senses, against chance. That signal is local, is there at every moment and belongs to one unit alone, so it carries far more than taste (D16's wall). How active a unit is depends only on its own signal: it plays more while its predictions are improving and fades when they stop improving, either because it has learned what it can or because there was nothing to learn (learning progress, Oudeyer and Kaplan 2007, the known form of curiosity; homeokinesis, Der and Martius 2012, the known form of play by prediction error). Taste only chooses among what play has organised.

**Stages**, each with its predictions and how sure written first, a ledger line, about 5 pairs to inspect a mechanism and frozen comparisons on fresh seeds for anything claimed (How we work, below). Done so far: D0 (what each movement tells: a ruler, D44), D1's self-judge (D45), play by learning progress and three links (D46, D47), boredom (D48). Rewritten after the review of 2026-11-11:

| stage | what | ends when | what it decides |
|---|---|---|---|
| **P1. Explain the play result** | Four frozen arms with equal play time before the challenge and their motor expenditure reported: no play, uniform random play, learning-progress play, certainty-directed play. Measured apart: body error, calibration (when it says sure, how often is it wrong, above all by a doubled or halved period), later food; and an ablation giving every estimator the same observations. | A table on fresh seeds | Whether certainty-directed play gathers better evidence per second or per joule, or only played longer; whether its certainty means anything |
| **P2. Remove the formula** (the main experiment) | Play learns an action-conditioned predictor: given what the eyes saw lately and what each motor is about to do, what will they do next? It keeps several predictions where evidence is ambiguous. Taste then learns which predicted consequences go with food; the knob is chosen by imagining each setting through the model, not by trial in the world, and with no formula from a measurement to a motor gain. A conventional forward model first, as a privileged reference; then how much survives in local parts. Against partners and taste alone, on equal experience. | Unrewarded play still cuts what taste must learn, with no physical formula; or which part failed (the predictor's information, the readout, the action search) | Whether play's knowledge can reach behaviour through a reusable mechanism |
| **P3. Exploration that tells hypotheses apart** | A reference learner chooses moves by expected information gain among its rival models, less the move's cost; then local competition among predictive units approximates it, so locality's cost is measured. Test: the period slips, where rivals predict different observations only for some moves; where none can tell them apart, keep the ambiguity and let taste decide. | Slips resolved by play, or shown unresolvable by any available move | Whether play can seek the evidence that discriminates, not just confidence |
| **P4. Back to recruitment** | A predictive unit can keep adjusting, recruit a child for a persistent leftover error, or retire one; new capacity judged on later predictions, not the data that triggered it. Against fixed small, fixed large and fixed-size recycling models (Dohare et al. 2024), with retention and renewed learning after changes. | The comparison, on the ladders and on play | Whether play and the scaling test share one mechanism |

**Accounting from now on** (the review): performance against stored state, experience, computation and communication, each reported; material and life length varied separately; and play's total lifetime energy return, in a world where food is there from birth, beside the head start measured from the challenge's onset.

**D1 step 1's result** (`discrete/NOTEBOOK.md`, D45): no. A unit judging itself by how predictable its movement makes the eyes prefers one motor alone, the most regular movement, which tells one thruster; the ruler prefers switching between the motors, which tells the balance (rank correlation -.02 to -.22). Predictability isn't information about what varies: the balance is a contrast between what each motor does, which no single unit sees. D0 confirmed on fresh seeds.

**Play pays later** (`discrete/NOTEBOOK.md`, D46, D47; the night of 2026-11-10, at the user's word to try all three links and play). Learning progress ends play by itself but spreads it thin. Of the links: partners, reading each motor's own record clocked by its beats (pooled over whatever random units used that motor alone), sets the knob to a median .07 to .10; in the user's frame (a quiet spell, then the challenge from a moment drawn each life) the brain that played starts surely ahead, +1.5 at once and +1.2 after, on development and fresh seeds (told +3). Taste choosing among play's own top hypotheses mends some slips (+1.6 after, surely). Taste alone, searching during the challenge, is surely behind. Steady view on cheap statistics: close, not sure. Open for D3: a steady-view link without the partners assumption; play that concentrates; whether it scales (more units, more body numbers).

**P1's result** (`discrete/NOTEBOOK.md`, D49; fresh seeds, 30 pairs, 400 s of play each): steering play towards certainty surely gathers better evidence than uniform play at equal time and energy (+18 points of guesses within 10%; +.94 and +.74 in food), and ties learning-progress play (+5 points, not sure). "Sure" is conservative: never wrong, reached by 3 to 28% of motors. D48's edge over learning progress was mostly play length. P2 next.

**P2's first result** (`discrete/NOTEBOOK.md`, D50; the user: try all three routes, then abstract). In life by taste among nine readouts: too dear in food. By evolution judged by food: the right shape, calibration only as good as its fitness proxy. Steady view over mixed commands from slow play: fails. Slow play makes our partners link the best yet (85% within .2). Abstraction: partners is a homeostatic motif (equalise what your own records measure) plus the brain's knowledge of its own settings, not physics; its formula is a comparator loop's fixed point. Next, to the user: whether that motif counts as legitimately inherited, and which test follows.

**P2's answer** (`discrete/NOTEBOOK.md`, D51, D52; the user's principle, understanding as coupling): the knob set with no formula and no food, by a generic search judged only by the brain's own sense-action coupling, with an Occam preference for no change, surely beats our formula on fresh seeds (+2.06 against +1.04 after onset) and leaves normal bodies exactly alone. Open: locality (one counter and one search for the whole brain now); re-entering the search on clues (needs something to change mid-life: the user's decision); whether the same principle sets other knobs (the tempo) and drives play (P3: seek experiences that grow coupling).

**What D47 does and doesn't show** (the review): unrewarded play can *estimate* the body, and a *designed* rule (partners: the log of two recurrence periods sets the two motors' gains) turns that into behaviour. Discovering that rule is P2. D46's failure of learning progress is a verdict on our rough estimator (one 3 s turn against the one before), not on the principle (Hou, An and Du 2026 measure model improvement properly). D48's certainty is a margin between comb scores, not a calibrated probability, and its arm also played twice as long (P1).

**What would count against it.** The self-judge ranks rhythms unlike the ruler, or play never fades; no generic link sets the knobs (P2), so our formula was doing the work; play costs more food than it wins back within a life; or units judged by their own prediction still interfere as those judged by taste did.

**What stays.** The goal and its scaling test (`README.md`); the ground rules (`AGENTS.md`: the interface, no shared clock, seconds, knobs first); the body as it is. The ladders and the tree (D37 to D40) stand as they are, and the dance is tried first where they are weakest: on acting.

## The strategy so far: ruler first, then climb (agreed by the user, 2026-11-09)

Build the ruler first. After that, nothing is worked on unless it can move the scaling curve.

| stage | what | ends when | what it decides |
|---|---|---|---|
| **0. The ruler** | Ladders on today's senses: sequences, timing, combinations (body mismatches last), and a held-out ladder written and sealed by a fresh agent. Rungs certified and counted in bits. Today's brains measured on both curves. | At least three ladders with at least five certified rungs each, or a measured reason why not; a baseline curve exists | Whether the ladders are really different; whether a ladder needs more senses (the user's decision) |
| **1. One climb** | Any frozen design that climbs one ladder by recruiting in its life. A hand-designed recruiter is legal, being one design for every rung. Starts: D27's `GrowSeq`, stage R's R3. First experiment below. | Three doublings climbed, or a measured reason why not | Which kind of unit and teaching to build |
| **2. Generality** | The same frozen design on the other ladders. A search across lifetimes joins, starting from stage 1's design: fitness the climb itself, trained at small sizes, judged at larger ones. | It climbs at least three ladders | Whether one component will do |
| **3. The claim** | The held-out ladder, the cost curve, forgetting, locality at large sizes, under full rigour; then `mixed_feedback.py` and SPICE. | All seven tests pass, or how far it got is reported | Whether the goal is met |

**Raw material is block-level for now** (the user, 2026-11-09; `discrete/NOTEBOOK.md`, D14: fastest to design in). Sepulchre's parts stay parked as a later comparison.

### The first experiment: who teaches the raw material?

**Run** (`discrete/NOTEBOOK.md`, D38): on the sequence ladder, sums replaced arms 1 and 3 (credit doesn't interfere when a taste reveals the answer; the eyes carry nothing about the word). A bank of every ring length climbs as the square root of its material; one ring growing on frustration uses only what it needs but takes about n^2/2 tastes against an ideal n + log2 n.

### Where stages 1 and 2 stand (`discrete/NOTEBOOK.md`, D38)

- **Stage 1's bar is met on the sequence ladder.** A record of the letters each trusted taste reveals, with one comparing unit per look-back, doubles its rung with each doubling of material (rungs 2, 3, 7, 13, 17 at 4 to 64 units).
- **What moves the register is learned** (the user's insight: sparse events shift it, and the circuit can learn which). Several registers moved by good meals, tastes and the brain's own clocks: on seq it picks good meals itself.
- **Timing isn't solved.** Clocks that lock on to surprises (the user's PLL idea; Large & Kolen 1994) beat base at every rung (x .3 to .5) but solve none, flat in rung and material: locking is the limit.
- **Plain costs nothing now**, with the bank's default and Occam bar (40 lives, the last full run aborted after that rung by the user).
- **Timing, since** (D39, 5 pairs): a bank of fixed clocks whose phase is set by the world's changes, and moved no further than the evidence says, solves rung 2 (x .74 to .83) and reaches .63 at rung 5 with 60 clocks, about the designed brain's .69. The number of clocks is a fixed cost set by the range of rhythms; the rung sets a register's length. Not run above rung 5.
- **One problem, one design proposed** (D39): every ladder's letter is a function of a context moved on by some kind of event, and the ideal learner's known local form is a context tree over a register (PPM, context tree weighting, Hoeffding trees). The record is such a tree of depth one; combinations need depth k. Recruit on novelty beneath a contradicted node; growing a level per contradiction is too slow for these lives.
- **An acting rung** (D39): touching pairs of blocks cost the starting brain a quarter of its food, declined rather than poisoned. Needs a yardstick (a careful driver) before it is a certified rung.
- **The tree built** (D40): a context tree over registers, one kind of node, no setting changed between ladders. Seq 11 and 17 solved; combo 1, 3, 5, 6 solved at 20 pairs, higher rungs needing more nodes; with the clocks as registers, time 2 at .94 and 5 and 7 near half, the other ladders unharmed, plain exactly 0. Stage 2's bar (one frozen design climbing three ladders) is met on two and begun on the third.
- **No acting rung at pairs** (D40, D41): a careful driver and a stop-and-look manoeuvre, both by hand and told the colour, win none of the food back. The loss is information these eyes don't give (D21's wall), not skill. The lopsided body (D19, D20) is the acting rung that already has a gap, a yardstick and learners.
- **The body ladder measured** (D42): one sure rung (the balance: .94 against 2.46 told) and one weak (drag, cured by a tempo, hurting only at a half or twice). Strength and eyes cost nothing. How to get more rungs is the user's to decide.
- **Knobs first** (D43): the balance knob, turned by trial, closes half the gap in 1000 s; set from a measurement, three quarters or more in 300 s; and the measurement can be made by the record's own unit, a register moved by the brain's beats (2.37 of 2.46). No new kind of unit was needed.
- **Next:** why the tree trails look-backs at time 5 (.45 against .63); the three doublings read off on each ladder with lives that suit the tree's growing; clocks that trim their own period, so fewer are needed; the lopsided body made the acting ladder (rungs by how many of the body's numbers are drawn, or how far), or the split eye, the user's decision.

As planned:

A taste reaches every unit at full strength, but it is one score for what they all did, and it carries at most a bit. So units varying at once are noise to each other, and N units that must each learn something different need at least N tastes, however they are organised. Three arms on the sequence ladder, doubling the material:

1. **All explore at once, taught by taste.** Expected to collapse, mainly from the direct harm of exploring (`discrete/NOTEBOOK.md`, D16).
2. **A few at a time, taught by taste**: idle until recruited, or only recently active units credited. Expected to scale, with life length growing with what must be learned.
3. **Units also teach each other**, predicting their senses and neighbours. The open question: does it beat taste's bits on today's eyes?

### Where stage 0 stands

Bar met (`discrete/NOTEBOOK.md`, D37): seq 7 certified rungs, combo 5, time 6; the ladders differ (combo's brain closes .39 of seq's gap, the rest nothing); baseline curve measured (random rivals help only on seq, while the answer is on their menu). Open before stage 1: rung lives don't grow smoothly with what a rung asks, so "hardest rung solved" can misread a climb (seq: 11 and 13 solved, 5 and 7 not).

## How we work

- **Every run is a point on a curve, or it's parked.** Say which belief it could move, and do the sum before spending CPU. Stop and rethink at a mechanism's second version. If a confound blocks a test, switch it off rather than curing it.
- **This is for understanding, so rigour is light until there is a claim** (the user, 2026-11-10: an itch to scratch; it needn't be of academic quality, nor physically realisable yet). Day to day: paired lives, a prediction written first, about 5 pairs, one step (2.5 ms). About 5 pairs serve to inspect a mechanism and see large effects; they are not a test of whether a principle matters (the review, 2026-11-11): a few frozen, discriminating comparisons on fresh seeds settle that. Held-out seeds, halved steps, sealed sets, independent checks, `mixed_feedback.py` and SPICE wait for a final claim, if we ever want one. `AGENTS.md`'s ground rules for a brain (the interface, no god, no shared clock, seconds not ticks) are not rigour and always hold.
- **Forking paths** (the user, 2026-11-10; Gelman and Loken's "garden of forking paths"). Every analysis choice made after seeing results (a mended observer, a bin count, the best of several decoders) spends evidence nobody counted, even with no fishing meant. So: write down the analysis before the lives as well as the prediction; a result whose analysis was changed after seeing it is exploratory, and is confirmed by the frozen analysis on fresh seeds before it enters the README's "What we've learned"; the ledger names each fork taken.
- **Predictions are written before lives, each with how sure**, and scored after. Over 90% sure: don't run it, or run a smoke of one or two pairs. A run we could have predicted told us nothing.
- **The ledger** (`lab/ledger.py`, `lab/v/LEDGER.md`): every run adds a line: what it cost in CPU, the belief it could move, the prediction, and afterwards whether it surprised us. Read it weekly: where the CPU went, and what share of runs told us nothing.
- **Design down from the ideal learner** (the user, 2026-11-10: find the answer, whatever it is, even if it is already known). Before a mechanism is invented, write the ideal learner for the problem and look in the literature for its local form; the experiments are for the gap between a known algorithm and a local, noisy, embodied version of it.
- **Measure in bits on both axes**: what a rung asks, what the material can hold, what the life supplies. Efficiency in evidence (tastes used against an ideal learner's) and in storage should stay bounded as material grows; a climb that only stores more is memory, not learning.
- **Knobs first, recruits last** (the user, 2026-11-10; `AGENTS.md`). A brain that isn't coping first adjusts what it has; it recruits only where no setting of its knobs will do. Every challenge is tried with knob-turning before any unit is added, and a climb credited to recruitment is compared with knobs alone. The scaling work of D37 to D40 only ever added units; acting challenges start from the knobs.
- **The body stays** (the user, 2026-11-10: grounded in a tangible, physical world, toy or not), and stays the simplest one until it has taught all it can. So the ladders must include rungs where acting well is the problem, early, not last.
- **The main session** keeps this page, talks with the user, makes judgements and does the work itself. **An agent only where independence is the point** (a gate's check, a sealed set's author), with a written brief, asked of the user first; it reports in under a page.
- **Going off the brief:** an agent stops and reports. New questions go to `QUESTIONS.md`.
- **The existing rules hold** (`AGENTS.md`): one long job at a time; push only on the user's "Push"; show working behaviour live before reporting; record findings in the notebook.

## Sealed

- **The outside test set:** two files. `lab/sealed/outside_set2.md`, the primary, written under the tighter seal on Sonnet (`lab/blind_agents.sh`; reply in `lab/v/outside_set2_reply.log`): SHA-256 `2050ebb03183f0343a6e3c1f94934452aaa1c8d07f001b9f3b36b1b31ae93368`, 45 entries, 36 keeping the current rules; several sources confirmed from search results only. `lab/sealed/outside_set.md`, a second test, by a fresh agent from outside sources. **Nobody building the language, the engine or the cures reads it** until the claim (stage 3 above). SHA-256 `f72a1addf3347b2779b7e2c6e62432fd01bea2254a50d8e39038fcf21c95db13`; 44 entries, 37 keeping the current rules. **The seal isn't perfect:** the agent opened no repository files, but the harness gave it `AGENTS.md`, the memory index and a git status at the start, so it saw the rules and some file names. Many older papers are confirmed by bibliographic record only; each entry says what was checked.
- **The held-out ladder:** `lab/sealed/heldout_ladder.json`, by a fresh agent from the outside sets (2026-11-09), told only the kinds of the other ladders: SHA-256 `8c7ae3373d33385361f2b5da7445b01e09e3073041c859778d77966187d09943`, 6 rungs, all compiled, no lives run. Unread until the design is frozen (stage 3 above). The harness gave the agent `AGENTS.md` and the memory index, as above, and it has read the outside sets, so the sets' seal is as it was for the main session.
- **The held-out worlds:** world number n, from any sampler, is held out if the first byte of SHA-256 of `world:n` is divisible by 4 (a quarter of them). Fixed now, so that it can't be chosen later.
- **Seeds for lives:** development 60000-69999 (spent by stage 2c), then 80000-89999 (opened 2026-11-06 for stage 3); held out 70000-79999. Seeds below 60000 are spent.

## Decisions (add as made)

| date | decision | by |
|---|---|---|
| 2026-11-12 | A new kind of experiment: a brain that takes up new parts (two more thrusters a side, smaller, alive part-way through life, wired at random); the yardstick first | the user |
| 2026-11-11 | The muscle-like body (a pulse raises activation, thrust a sigmoid of it), opt-in; every germane experiment repeated on it, in the order of the table above, starting with the starting brain retuned for it | the user |
| 2026-11-11 | The guiding principle: understanding as coupling, the simplest connection between inputs and actions in both directions, I(S; A) by local predictors; the body and world unchanged; play may be re-entered on clues (rewards falling); playing with links judged by coupling, not taste | the user |
| 2026-11-11 | The review of 2026-11-11 (`lab/v/review_2026-11-11.md`) adopted in full: the one-line question; the bits principle restated (learning is fast when the distinctions that matter are cheap under the prior and the actions expose them); D47 stated as estimation plus a designed rule; stages P1 to P4 replace D1 to D3; accounting by state, experience, computation and communication; knobs first a default, not a law | the user |
| 2026-11-10 | Forking paths: an analysis changed after seeing results makes its result exploratory, confirmed on fresh seeds with the analysis frozen before it enters What we've learned; D0's mended observer to be so confirmed | the user |
| 2026-11-10 | Mechanisms, not features: stages written as generic mechanisms (rhythms, randomness, self-judging banks) whose test is whether they find a behaviour unaided; hand-written behaviours are rulers only. D1 to D3 rewritten so; D0 kept as the ruler. Play named: activity with no goal that organises the brain, judged by how much faster it makes later learning | the user |
| 2026-11-10 | A new phase: a dancing brain, creative from birth, whose many cycles produce the evidence and then settle. Written up as stages D0 to D3 (the form judged by each cycle's own prediction is the main session's, from the record); not started | the user |
| 2026-11-10 | Knobs first, recruits last: turning an existing knob is always the cheap option; recruit only if that fails | the user |
| 2026-11-10 | The acting rung: not touching pairs (the eyes can't tell enough, D41) but the lopsided body (D42) | the user |
| 2026-11-10 | The work is for the user's own understanding: light rigour until a claim (about 5 pairs, predictions with how sure, a ledger of runs); find the answer whatever it is, known algorithms included, designing down from the ideal learner; the body stays, grounded and as simple as it is, so an acting rung comes forward (paired blocks first) | the user (the wording and the rules that follow from it the main session's, after its review of the strategy) |
| 2026-11-09 | The strategy above replaces the earlier stages: four ladders starting with today's senses, body mismatches last; raw material block-level for now; a fresh agent writes the held-out ladder; paired blocks becomes a rung, not a line of its own | the user |
| 2026-11-09 | The goal: intelligence that scales, in a brain for a robot (`README.md`, The goal). Lives may lengthen as challenges grow; more senses eventually, with much still to learn from these; anything may happen before a life, but a solution designed by hand is insight, not the solution; a component may be quite complex, staying parsimonious for fast simulation, clear thinking and some chance of understanding the result; a small brain may have any number of connections, locality coming from scale, since big brains can't have everything broadcasting to everything else; a bigger brain may react more slowly if it is better on balance, and what size costs on simple tasks is explored, perhaps as a scaling law, not barred in advance | the user |
| 2026-11-09 | The scaling test's wording and provisional numbers, drafted for the user's review | main session |
| 2026-11-09 | The balance learner closed; next, the paired-blocks world, pairs before clusters (a U of poison traps a creature with no reverse); written up, not started | the user |
| 2026-11-04 | Rule-changing worlds only after testing within the current constraints | the user |
| 2026-11-04 | Marks left in the world: not yet | the user |
| 2026-11-04 | The brain's own parts are a link | the user |
| 2026-11-04 | Use fresh agents; no blind worlds from the user | the user |
| 2026-11-04 | This page's question and way of working; commit only as far as decision B | the user |
| 2026-11-04 | Boil down as we go, by the four rules; judge by description length, parts second; start (decision A) | the user |
| 2026-11-04 | F_novel and R replace the first wording, judged on the sealed outside set; motifs count only if the circuit retunes them itself; 0.2 is the line for no; bits analysis before stage 2 | the user |
| 2026-11-04 | Hold ourselves to information-theoretic rigour in measuring and judging (MacKay) | the user |
| 2026-11-04 | Measure an ideal learner that holds a changing-rule model | the user |
| 2026-11-04 | Press on without waiting, up to B, each step proven first; stay self-critical, Bayesian, information-theoretic | the user |
| 2026-11-05 | Stage 1c's gate is met; the pass rule, doing no harm and se .1 adopted; stage 2 starts, as 2a then 2b, each with its own gate | main session, under the user's delegation |
| 2026-11-06 | Preliminary work at the 10 ms tick; final results by halving the step until they stop changing (AGENTS.md); lives of 1000 s for the tests that need them | the user (tolerance and details mine) |
| 2026-11-06 | No in-life change to the brain or the brain-body link yet (rewiring by any route is out); every change is in the environment | the user |
| 2026-11-06 | The main session does the work itself, without sub-agents (tokens, cores); an independent check only when a gate needs one, asked first | the user |
| 2026-11-06 | A world's description length judges nothing: near-duplicates are judged by their lives, and a world's size is the count of the generator's blocks it was drawn with, reported only | main session, prompted by the user |
| 2026-11-06 | Stage 3's worlds from lab/stage3_gen.py (2b's generator in the 2c language; body constructs fixed from birth, by the user's rule), frozen before drawing; development seeds 80000-89999 | main session, under the user's delegation |
| 2026-11-06 | A thruster costs when it fires, whoever made it fire; a command the world drops costs nothing (the break is between brain and thruster) | the user |
| 2026-11-06 | Stage 3 keeps a world out if 3 or more of its 16 labelling lives carry a stage-5 label | main session, before stage 3's lives |
| 2026-11-06 | One independent agent checks stage 2c (interface by construction, instruments, seconds, speed) before stage 3; final runs in seconds at about 1.25 ms; the reference only on worlds with a gap, at 2.5 ms | the user (approving the main session's plan) |
| 2026-11-07 | One independent agent checks stage 3's coverage (the gate "3 to B"); the gaps it found are filled before the result is final | the user |
| 2026-11-07 | Decision B: next, the bank makes its own rivals from simple parts connected in various ways, hierarchies included (stage R); stage 4's hand-made cures parked | the user |
| 2026-11-07 | The one-bit question (which colour is food) first, as the simplest case; rivals for how to drive after stage R (Parked) | the user |
| 2026-11-07 | Rules about time may need far longer lives; long lives may be our equivalent of deep learning's scale, so stage R measures coverage against life length as well as K; lives of 10,000 s allowed for that (AGENTS.md) | the user |
| 2026-11-06 | Stage 2a is done (engine identical to the unmodified lives, worlds checked against their descriptions, labelled in bits); stage 2b starts, owing the independent engine check; the finer-step move goes to the user, and stage 3's headline is repeated at 5 ms | main session, under the user's delegation |

## Parked, for later

- A learning adversary, GAN-style (`QUESTIONS.md`, the arms race): after stage 3, as a generator of worlds we couldn't think of.
- Hierarchy beyond rivals' contexts (detectors that learn which detectors to grow): after stage R.
- The eye filter's built-in rate (D35): a cure after stage R.
- Rivals for how to drive, not only which colour is food (the user agreed, 2026-11-07): after stage R, the same recipe (a repertoire of
  simple parts, a bar rising with its size, no harm in plain) applied to adjustments of the driving (turn strength, approach, pacing),
  for the body and world mismatches of the interventions table. Harder: such a rival can be judged only by food per second while it
  is in charge, not on every taste without acting, so its evidence is far scarcer; stage R's long lives say whether it is affordable.
- A richer world: only once this one has taught us everything it can.
- **Clusters of abutting blocks** (the user, 2026-11-09): after pairs, if they teach us something; includes the U of poison, which only a brain able to survey a cluster before committing could handle.
- **Key and lock** (main session, 2026-11-09): blue tastes of nothing but arms the next red, in two versions, with and without a visible clue beforehand: consequences that come later, and whether surprise teaches before reward (`QUESTIONS.md`).
- **Obstacles that hide food** (the user, 2026-11-08): many blocks of a third kind that only block the view of the other two, so that it
  pays to steer round them. Two versions: seen only through occlusion (the interface unchanged: a world of the language, perhaps already
  writable as dark blocks, `bright` 0, if they still occlude and can't be eaten; to check), or sensed in their own right (a change to
  the body and interface, the user's decision). GRAMMAR.md already lists an occluder primitive as missing (L10, the medium or space).
- **Stage R again in Sepulchre's mixed-feedback blocks only** (the user, 2026-11-08): the parts of the snake-robot paper (Huo, Forni,
  Sepulchre, `MIXED_FEEDBACK.md` [20]: rebound-excitable neurons, half-centre oscillators, the rebound winner-take-all motif), wired
  at random with random weights, and above all with mechanisms that tune the weights themselves. Everything stage R measures (coverage
  on stage 3's worlds, no harm in plain, life lengths up to 10,000 s), so the two kinds of part are compared on the same lives. These
  blocks have rhythm, phase reset and entrainment built in, which stage R's free-running oscillators lack.
### Blocks in pairs (a rung of the combinations ladder, once its geometry is checked)

**The world.** Each food block has one poison block beside it, at a set gap; nothing else changes: the same body, eyes, taste and worth of a block, written in the language (an eaten block must reappear beside a partner, or the pairs dissolve). The one setting is the gap: wide (should be as easy as plain), medium (avoidable with care), too close (impossible, a control).

**Why this world.** It asks about space and skill, with no memory or sequence: "food in view" is no longer enough, the right rule being "food in view and no poison in view". That is a combination of two inputs, so perhaps the simplest test of whether a second layer is needed. It also tests attention: `designed-circuit` silences the other eye while it heeds one colour (by its description, untested here; B's and the bank's behaviour unchecked), which would blind it to the poison beside its food. By the code's description the eyes' corridor is what the mouth will sweep, so a silent poison eye should mean a safe drive; a near block's shadow can break that.

**Why pairs and not clusters (the user).** With blocks abutting, a food block with poison to its left, right and behind sits in a U of poison, and the creature has no reverse: it can't eat the food without being trapped. A very competent brain might solve that (drive right round the cluster to judge whether it is viable), but that is far beyond what we have. Pairs have no such trap.

**First steps, before any long runs:**
1. The geometry, from the body's numbers (`world.py`: mouth, corridor, turning, momentum): which gaps can any brain separate, and at what aim? A failure at an impossible gap says nothing.
2. A yardstick: knowing the colours doesn't help here, so the usual told arm won't do. A hand-written cautious policy ("drive only when the poison eye is silent") measures what caution is worth at each gap.
3. Show the world live, for the user to judge, before anything is run at length.

**To score with care.** Eating the poison to clear the way may be the best move where food is worth more than poison costs: that would be a smart answer, not a failure. Predictions and gates to be written before the lives, as always.


## Before the goal: the earlier programme (2026-11-04 to 11-09)

Kept for reference. Its question, stages and primary result judged whether the bank of predictors is a general principle or ten cures glued together; the results are in `discrete/NOTEBOOK.md`, D30-D36, and `ABSTRACT.md`. The pass rule and its terms are still used by the certifying of rungs. Stage R's R2 and R4 are parked; R3 is a start for stage 1.

### The question

**Does a brain facing many more challenges need proportionally more hand-built detectors, or do fewer general ones emerge?**

If it needs one for each, we have just hand-designed everything, and nothing interesting is emerging. If fewer will do, what are they, and why? Then: can hierarchy (detectors that learn about detectors) make the circuit find them itself, rather than us?

**In bits.** A life offers about 50 bits of evidence (D31), but a world's rule takes hundreds to write down (D33), so a brain can only learn what its structure already makes cheap: learning in a life is choosing and tuning within a repertoire. The question becomes how small a repertoire, made of how simple parts, covers how much. A repertoire of K rivals costs about log2 K bits of evidence to choose from (the Occam factor), and its description can be tiny if the rivals are drawn by a simple rule from simple parts, though it still costs parts and power to build.

### Where we are

**Decision B taken (the user, 2026-11-07): the bank makes its own rivals.** Stage 3 is done and checked independently: on fresh random worlds the bank's hand-written repertoire surely covers 11 of the 61 with something to learn and surely fails 24, coverage between .18 and .61; its failures are missing ideas, mostly about timing (at 1000 s an ideal judge with timing ideas learns swaps the bank can't); one part (the eye filter, tuned to the eyes' usual rate) does harm where the eyes are more sensitive, and the bank costs a little (about .07) in many worlds with nothing to learn (`discrete/NOTEBOOK.md`, D35; `ABSTRACT.md`). **Next: stage R**, below, in place of stage 4's hand-made cures.

**Next (the user, 2026-11-09; not started): the paired-blocks world**, below. The balance learner is closed (`discrete/NOTEBOOK.md`, D36). This comes ahead of stage R's remaining steps.

**Gates, fixed before the results.** A gate that fails stops the work there, and it is reported, not argued round.

- **1c to 2:** (a) stage 1b's headline numbers replicate on fresh development seeds, or the differences are recorded and explained; (b) whether the bank's forgetting pays is settled by a measurement either way; (c) the taste limit is an upper bound with a proof, or called an estimate everywhere; (d) a pass definition is chosen on synthetic data, with its false yes and false no rates, before any real world runs.
- **2 to 3:** an independent check of the engine: with every change off, a world reproduces the unmodified lives exactly; each hand-written world behaves as its description says; each world's evidence is measured in bits, and how well planted near-duplicates are told apart is measured.
- **3 to B:** coverage on fresh worlds, in bits and with intervals, checked by an agent that didn't produce it. Held-out seeds and sealed sets stay closed: stage 3 uses neither the sealed sets nor anything but development draws until the user decides at B.

### The stages

Each ends with a result and a decision by the user. **No stage starts without that decision.** We commit only to reaching decision B; the rest is a sketch.

| stage | what | ends when | what it decides |
|---|---|---|---|
| 0 | Settle the primary result; seal an outside test set and a held-out split | all written down | A: start |
| 1 | Synthetic controls: test the analysis on invented data with known answers | it recovers the known answers, or we learn it can't | stop, or change the analysis, or go on |
| 1b | **The budget in bits**: what a life can supply, and the bank against an ideal Bayesian learner | we know how much of each world is learnable in principle, and how much the bank wastes | whether stage 2's worlds need reshaping |
| 1c | **Repeat what 1b assumed**: ideal learners that allow change, the bank's floor where a rule starts mid-life, a proven limit on tastes, synthetic worlds that can't be fully passed | the gate above | the labels and pass bar stage 2 uses |
| 2a | A minimal language and engine; about 30 worlds by hand, each labelled in bits | the engine is proven against the unmodified world | go on to random worlds, or fix the language |
| 2b | The frozen reference; about 100 random worlds; near-duplicates; real sigma and cost per world | we know what share of random worlds are learnable, and the cost per world | whether random worlds are worth using at all |
| 3 | **The present circuit, unchanged, on fresh worlds; then longer lives on about 30** | a coverage number exists | **B: the main decision.** What's uncovered, and is it worth continuing? |
| R | **Rivals made, not written** (decision B): the bank's rivals assembled from many simple parts connected in various ways, hierarchies included (counters of toggles, an oscillator driving a toggle, a timer gating a counter); first drawn at birth, then grown in the life where no rival predicts | below | whether a repertoire from simple parts covers what the written one does and more, at what cost in evidence and parts |
| 4 | (parked at B) Add cures, by a separate designer, to the largest groups of failures | | |
| 5 | The rule-changing worlds; types | to be planned later | |

### Stage R: rivals made, not written

**What a rival is.** Every rival in today's bank is a *context* and a *table*: a signal that takes one of k values (the count of good tastes mod n), and a learned bit for each value saying which colour is food then, with a tally of trust. A made rival keeps the table and builds the context from simple parts, each a block a circuit can hold:
- a **toggle** (flips on each input event), so a chain of toggles is a binary counter (k = 2, 4, 8);
- a **counter that resets** at n (k = n), for counts not a power of two;
- an **oscillator** of period T, read in phase bins (k bins), so a toggle driven by it has period 2T;
- a **timer** since an event (a taste, a good taste), read as before or after its delay;
- a **conjunction** of two contexts (their product: k1 x k2 values), the way hierarchies form.

Inputs are only what a brain already has: tastes, good tastes, its own clock (oscillators and timers in seconds, never ticks), with each part's own mismatch and the oscillators' phase noise. A rival is scored exactly as today's are (evidence where it disagrees with the default), so it is judged on every taste without being acted on.

**Steps, each with its predictions written first and its gate:**
1. **R1, the parts reproduce the bank.** Today's seven rivals rebuilt from these parts give identical lives. Gate: identical.
2. **R2, drawn at birth.** K rivals drawn at random by a fixed rule (parts and depth, periods and delays log-uniform over ranges fixed in seconds before any run), the bar to adopt a rival rising with log2 K as the Occam factor requires, derived, not tuned. Measured on stage 3's worlds (development: base, told and reference lives already exist on the same seeds): coverage, doing no harm, and false picks against K (1, 10, 100, 1000), with the number of matching rivals a world needs worked out first. Gate: a K is found that covers surely more than the written bank with no harm, or the reason none can is measured.
3. **R3, grown in the life.** Start with few parts; where the followed rival keeps being contradicted (frustration), grow a new rival by connecting a part to an existing rival's context (function-preserving: it starts with no evidence). Compared with R2 at equal parts. Gate: grown ties or beats drawn at equal parts, or the reason is measured.
4. **R4, judged on worlds never seen**: a fresh draw from stage 3's generator (development numbers 300-499, fixed now), then, at the user's decision, the sealed outside set and held-out seeds.

**In bits, for every step:** the evidence each world offers about its rule (the told arm's tastes), the Occam cost of K, how many of the K rivals fit each world, and the parts and power of the repertoire. The eye filter's fault (D35) is left as it is in R, so comparisons stay with the written bank; it is the next cure.

### The primary result

This section judged the earlier question; its idea of challenges the design never saw lives on in the test's held-out ladder. Chosen before any data, the one result this programme judges by. Everything else explains it and can't overturn it. Stage 1 showed the first wording couldn't tell the truth (`discrete/NOTEBOOK.md`, D30).

**The design is fixed, and the circuit still learns.** Every life starts fresh and adapts in that life; what's held fixed is only what a designer may change between worlds. To test any level, hold fixed the level above it: a circuit's state adapts with its design fixed; a design adapts with the paradigm fixed.

- **F_novel:** on challenges the design never saw, the pass rate above the base circuit's, as a share of what the base circuit leaves.
- **R:** the description added by the cures, against what one fixed-size cure per challenge would cost.
- **A pass:** a world passes if x > max(.5 r, .25). x is the circuit's fraction of the gap, measured from the larger of base and 0 (so standing still gains nothing) up to a policy told the rule; r is the same for a **reference**, a Bayesian learner frozen before any world it judges runs, its family, prior in bits, likelihood and tie rule all written down. The gap to told is always reported beside it. A told bar alone makes a yes nearly unreachable; a reference alone can be gamed by one cheap half-working cure; hence the .25 (D32). Worlds the reference can't help fail at the floor: this errs towards no.
- **Doing no harm:** in a world with nothing to learn, the lower 95% bound of (circuit - base) stays above -.1 efficiency. The -.1 is a choice, about the interval's half-width at 200 pairs. Scoring above base there isn't counted as learning.
- **Measurement:** the verdict needs about se .1 per world, about four times the lives planned (D32). Real sigma comes from stage 2.
- **The verdict rests on the sealed outside set.** A grammar of K bits can be built into a circuit of about K bits however many worlds it generates, so a yes on our own worlds is guaranteed in principle and proves nothing. Our own worlds are for development, and their numbers are reported as such.
- **Yes:** on the outside set, the 95% lower bound of F_novel is above a half, and the upper bound of R below a half, with at least 30 novel challenges.
- **No:** the upper bound of F_novel is below 0.2.
- **In between:** anything else, reported as measured.
- **Same shape, retuned by hand:** R below a half without F_novel. Not a yes, but a finding of its own: those settings are what a higher level could learn. If the circuit retunes the shape itself, it passes F_novel and counts.

**In bits, for every world**, as the explanation: the evidence available on the wires; how much the circuit used; what an ideal Bayesian learner with the same evidence would do; and bits built in by design against bits gathered in life. A life has a budget: at most a bit a taste, truly 0.25-0.83, about 15-50 bits at the bank's rate of tastes, and several times more for a brain that eats faster, since the body has no firing cap; telling N worlds apart takes at least log2 N bits (D31, D32). Say "too short at this rate", not "for any brain", unless a difference never shows within the life. A world outside a learner's prior costs extra evidence, about log2 of one over its prior probability, so "we built detectors for the grammar" has a graded measure: how many extra bits does an outside world take?

Description length: LZMA size, given a frozen corpus, of a canonical form (D30). The vocabulary is invented so far, and to be fixed before any real world runs.

### Keeping it simple as we go (stage 4)

We boil down during the search, not at the end, when nobody could reason about the result.

1. **Widen first.** Before building a new part, try extending an existing one. A new part must show that widening can't do the job.
2. **Merge at three.** When three cures share a shape, stop and try to merge them. The merged version must tie with the originals. Two may be a coincidence.
3. **Cap the motifs.** A low limit on distinct kinds of mechanism, so adding one means retiring or merging another.
4. **Prune after every addition**, removing anything that costs nothing to remove, then re-run all earlier worlds and the unmodified world.

