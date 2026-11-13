# The simplest discrete circuit that forages

The user's question (2026-10-26): before getting clever about telling food from poison, what is the simplest analogue
circuit that drives the body to blocks efficiently in an all-food world, built of common parts (resistors, capacitors,
diodes, transistors, FETs, unijunctions)? Their expectation: no more than 20 parts should do a reasonable job.

The body, the world and the interface are every brain's (AGENTS.md); the circuits are netlists of real parts living
closed loop in SPICE (`discrete/life.py`). Judged by `minimal/spec.py`'s measures, all food: efficiency (meals gained
per meal spent resting, moving and thinking), gain rate (meals per 10 s), food, stranding.

## Where it stands

- **Play pays later** (D45 to D47, 2026-11-10, the night's work): with a quiet spell first (meals worth nothing) and the challenge
  (lopsided thrusters, food and poison) from a moment drawn each life, a brain that played at random in the quiet starts the challenge
  surely ahead of one that only foraged: +1.5 at once and +1.2 after, on development and fresh seeds (told +3). What carried it: each
  motor's own record clocked by its beats, pooled over whatever random movements used that motor alone, and a partners link making
  the two motors' effects equal. Taste picking among play's own top hypotheses mends some period slips (+1.6 after, surely). Taste
  alone, searching during the challenge, is surely behind; play by learning progress ends by itself but spreads thin; the steady-view
  link on cheap statistics is close but not sure. Open: a steady-view link as good, without the partners assumption.
- **Taking up new parts** (D55, 2026-11-12; the user's new kind of experiment): new thrusters alone are worth little (about 15%:
  the eyes are the limit); a split eye with small thrusters about +1.0. Given them part-way through life, a brain that plays still with
  them, watching through the new eye what each new thruster does, wires them itself and surely gains on fresh creatures (+.39); food
  as the teacher fails even over 3000 s. Limits: the reflex form, and a preference for the thrusters play sees best.
- **Taking turns** (D54, 2026-11-12; the user: a Sepulchre theme): two motor units in a half-centre (one searches its own gain while
  the other holds; fatigue hands over; a unit that moved wakes the other), each judging by the joint coupling it sees with its
  neighbour, match the global coupling search (90% within .2 on fresh seeds) and are surely better than the same units searching at
  once (+1.76, +1.34). With drag drawn too they find the balance but not the tempo: coupling prefers half the right speed, food the
  right one. Coupling sets what makes behaviour coherent; speed against care needs taste.
- **The muscle-like body** (D53, 2026-11-11, night; the user's paradigm, opt-in): a pulse raises a thruster's activation (30 ms) and
  thrust is a sigmoid of it. The starting brain forages at 63% of the old body's level; the told yardstick and every formula that
  assumed thrust proportional to rate had to be recomputed, and the measurers built on such formulas (D20, D43, partners) fail on it,
  while coupling still peaks at the body's own right knob (95%) and the coupling search surely beats the formula there. The body is
  steeper in the knob, not gentler (a 10% rate error is about 25% in thrust), and D52's knife-edge at 0 doesn't appear in this frame on
  the old body either. The ladders certify much as before and the tree still climbs them; D52's knife-edge was an over-reading (the cost grows smoothly).
- **The knob set by coupling** (D52, 2026-11-11): a generic search over the balance knob judged only by the brain's own sense-action
  coupling, with an Occam preference for no change, beats our formula on fresh seeds (+2.06 against +1.04 after onset; surely, +1.01)
  and leaves normal bodies exactly alone; no food, no formula, no body model. Plain bodies are a knife-edge (equal rates pair every
  kick; corrected in D53: not a knife-edge, the cost grows smoothly and steeply by .1), which the Occam default handles. Precise timing of the kicks gains nothing (told on a lopsided body already equals a
  plain one). Locality, three tries (D52's end): per-unit coupling in fixed bins rewards slowing down (normalising cures that); small
  perturbations are too weak to feel; units' own wide searches spoil each other's judgements. The many-units problem, with coupling as
  teacher.
- **Understanding as coupling** (D51, 2026-11-11; the user's principle): with no reward, the coupling between senses and actions at
  the brain's interface peaks at the right balance knob (95% within .2 on lopsided bodies, 0 on plain ones, correlation +1.00): no
  formula, no model of the body. Next: how fast it tells settings apart, and a knob moved by it in life.
- **P2: three routes to the knob without our formula** (D50, 2026-11-11): taste choosing among nine readouts in life costs more food
  than it wins; evolution judged by food finds the right shape (a difference of the two motors' measures) but its calibration follows
  its fitness proxy, below ours on real lives; steady view over mixed commands, from slow play, fails (32% within .2). By-product: slow
  play makes our partners link the best yet (85% within .2). Abstraction: the link is a homeostatic motif, equalise what your own
  records measure, not physics.
- **The review and P1** (D49, 2026-11-11): an outside review, adopted: D47 is estimation plus a designed rule, P2 removes the rule.
  P1, at equal play time on fresh seeds: steering play towards certainty surely beats random play (+18 points of guesses within 10%,
  surely more food) and ties learning-progress play; D48's edge was mostly playing longer; "sure" is conservative, never wrong.
- **Boredom from certainty** (D48, 2026-11-11): stopping play when the estimate stops moving is fooled by confident slips; stopping
  when play's best guess clearly beats its rival, steering play to what raises that certainty and handing what doubt remains to taste,
  sets the knob to .01 (90% within .2); from 100 s into the challenge it is surely ahead, +2.1 and on fresh seeds +2.2, three quarters of
  the way to a brain told its body; at once +1.1 and +.7 (sure on one seed set), while taste settles the last doubt.
- **Knobs first** (D43, 2026-11-10; the user's rule): compensating for a weak thruster is one knob. Turned by trial and error it takes
  about 1000 s to close half the gap, since nothing tells it which way to turn; set from a measurement (a revolution timed with one
  motor) it closes three quarters or more by 300 s. The measurement can be made by D38's recording unit clocked by the brain's own beats
  (2.37 against 2.46 set right, at 300 s), with no counters in seconds. Next: a measurer for the tempo knob (drag); the tree's trail on
  timing rung 5.
- **The lopsided body as the acting ladder** (D42, 2026-11-10): of the body's numbers drawn per life, only two cost the starting brain
  anything: the balance between the thrusters (.94 against plain's 2.52; told, 2.46) and, at the ends of its range only, drag (cured
  by one tempo for every rate). Strength and the eyes' sensitivity cost nothing. One sure rung and one weak one; the user to decide
  how to get more (wider drag, or body numbers that depend on a context).
- **No acting rung at touching pairs** (D41, 2026-11-10): stopping to look before driving on judges well (9 commits a life, 8 clean) but
  scores below the told arm, since a look gathers 3 to 5 pulses an eye and the starting brain gets most of those foods by trying again.
  The loss at pairs is missing information (where across the corridor a block lies: D21's wall), not skill. The lopsided body is the
  better acting rung: its gap, yardstick and learners exist (D19, D20).
- **A context tree over registers** (D40, 2026-11-10): one kind of node, recruited where a new context arrives beneath a contradicted
  node, with no setting changed between ladders. Sequences: rungs 11 and 17 solved. Combinations, where nothing climbed before: rungs
  1, 3, 5, 6 solved at 20 pairs, higher rungs needing more nodes. With D39's clocks as a third kind of register: timing's rung 2 at .94,
  rungs 5 and 7 near half, the other two ladders unharmed, plain exactly 0. Pairs' yardstick (a careful driver by hand) failed. Next:
  why the tree trails look-backs at time 5; the three doublings read off on each ladder; fewer clocks.
- **The lock, the ideal learner and pairs** (D39, 2026-11-10; light rigour, 5 pairs): the three ladders are one problem, a letter as a
  function of a context moved on by some kind of event, whose ideal learner's known local form is a context tree over a register
  (the record is such a tree of depth one). A bank of fixed clocks, their phase set by the world's changes and no further than the
  evidence says, solves timing's rung 2 and reaches .63 at rung 5 with 60 clocks, about the designed brain's level (D38's lock: .3 to .5).
  Touching pairs of blocks cost the starting brain a quarter of its food, declined rather than poisoned: a rung for driving, with no
  yardstick yet. Next: the context tree over registers on the combination ladder; a careful driver as pairs' yardstick.
- **Stage 0, the ruler** (D37, 2026-11-09): three ladders on today's senses (sequences, timing, combinations), with 7, 6 and 5 certified
  rungs; they test different things; random rivals added to the bank help only on sequences, while the answer is on their menu. Open:
  rung lives must grow smoothly with what each rung asks, or the scaling curve misreads a climb (the user: revisit only if needed).
- **Stage 1, the first climb** (D38, 2026-11-09): a record of the letters each trusted taste reveals, with one comparing unit per
  look-back, climbs the sequence ladder: doubling the material doubles the rung (17 at 320 units). Several registers moved by different
  events (good meals, tastes, the brain's own clocks) pick the right one themselves. On timing, clocks that lock on to surprises beat base
  at every rung but solve none: locking is the limit. Plain now costs nothing (the bank's default and Occam bar). Next: lock better
  (more clocks), then the combination ladder by a growing context tree.
- **The balance learner that sizes itself** (D36, night of 2026-11-08): the old learner's fixed gate (wobble below 15 good tastes per 32 s,
  a rate the body supplies) replaced by rules a block keeps for itself: it moves its balance a step when the sum of its drives' evidence
  is significant, doubles the step while moves agree and halves it when they reverse, and halves its wobble when its wobble surely hurts
  whichever way it goes (the mark of standing on a peak). It balances a lopsided body surely faster than the old learner (|x| ahead at
  100-300 s), and in the 10,000 s scaling test it lifts the written bank surely in 12 of 13 worlds (+.10 to +.69 in x; the swaps from sure
  fails to can't tell). But in 100 s lives it costs .6 on average over stage 3's worlds: a learner born exploring pays for its wobble, in
  plain 11% of the food at a wobble of only .05, and a drive's outcome needs about 1,400 drives to show that cost (a 100 s life has
  about 96). The old bank is safe at 100 s only because its gate never opens there. In plain at 10,000 s the new learner is no better
  than the old on average (-.12 against base, 30 pairs), only steadier. Open: when to explore at all (`QUESTIONS.md`).
- **Stage 3, the bank on fresh random worlds** (D35, checked independently): 35% have something to learn; the bank's coverage of those lies between .18 and .61 (11 sure passes, 24 sure fails, 26 too close to call); its failures are ideas it lacks, mostly about timing, and at 1000 s an ideal judge with timing ideas learns the swaps the bank can't; it does no harm in 79 of 113 nothing-to-learn worlds, harms surely in 2 (its eye filter, where the eyes are more sensitive), and costs a little (about .07) in many. Next, by the user's decision B: stage R, rivals made from simple parts (`PROGRAMME.md`).
- **The budget in bits** (D31, D32): at the bank's rate of tastes a life offers about 50 bits in a clean world and 15 with one lie in five, but a brain may buy several times more by eating faster. The bank's picks resemble a comparison expecting frequent change; its floor pays among counters, though a vote that never forgets does better still. Swap's gap is about when, and a learner holding about 14 bits of periods closes half of it. In clean worlds the wall is the models held, not bits.
- **Worlds as programs** (D33): a small language writes 40 worlds; its engine reproduces the unmodified lives exactly. The fast model's lives move when the tick is halved (plain -.17), whether through the body's tick or the brain model's is untested: the user's to decide.
- **Fine enough** (D34): with everything in seconds, results settle by about 1.25 ms (a sixteenth of the body's fastest time constant); the old tick-locked loop was off by up to .8 at 10 ms. The engine is now about 7x faster, lives unchanged.
- **Random worlds** (D34): of 100 drawn at random, 38 have something to learn, 14 a clear gap, and a frozen ideal learner holding 12,591 hypotheses closes a quarter of the gap in only 3: most of what the worlds ask lies outside every hypothesis our learners hold.
- **Foraging, all food**: hold and drive, 14 parts, efficiency about 7 at 72 nW (D3, D4): an oscillator scans with one
  thruster, and each pulse from an eye charges a hold capacitor that fires the second thruster too while it lasts. A
  9-part blind oscillator is as efficient and four times as fast, but only on a body whose two thrusters are exactly
  equal (D5).
- **Self-tuning to the body**: not found worth it yet. Bodies built differently barely move the best settings, except
  unequal thrusters, and no in-life tuning from meals beat a fixed circuit; driving only while the eyes still see the
  block copes instead (D5). A richer body (an eye on each side for each colour) is held off: the user prefers to
  learn what extreme simplicity gives first.
- **Learning the bit**: `learn_avoid`, 46 parts, surely does the job held out (160 lives): efficiency 1.78, gain
  4.7, food:poison 4.7 in the last third, none stranded, 130 nW (D8, D9). It gives up on an empty patch (both
  thrusters straight once the followed eye has seen nothing for a few seconds) and turns from poison ahead (the
  silenced eye empties the hold). Pruned from 48 parts (D9), and surely better than them. Its predecessor
  `learn_hold` (49 parts, D6) stranded: it circled in patches it had eaten clear of food.
- **The ceiling** for this kind of brain on this body, as policies: 2.7 told the answer from birth, 2.3 learning
  (D8, D10). The circuit's gap isn't in learning or approaching but in spending: it scans at 54 per s for no more
  sightings than at 16, and its giving-up run is fast and runs into poison (D10). Two speeds fight the bipolars'
  collapsing gain at nanoamps (D11).
- **In SKY130 CMOS** (D12): a copy of the best policy, about 130 parts, works at a twelfth of `learn_avoid`'s power
  but is surely worse (gain about 0.8): its drive hold was 63 ms where the policy's is 0.2 s, and its doubt couldn't
  flip back for 3.6 s.
- **The fast model** (D13; `model.py`, its numbers benched by `blocks.py` on `cmos.py`'s circuit B): the circuit's
  blocks as their measured numbers, a life in a second, tied with ngspice on
  the circuit's own lives; judged robustly (each life its own parts' errors), which exposed a knife-edge the nominal
  searches exploited. Its best design, **B**: doubt a bounded tally (+ a poison, - a food, no leak, the bit flipping
  at a threshold and the tally then reset), 2.38 held out with tolerances, learning costing it 0.15 against being told
  the colour. Built in transistors (151 parts, 3.7 nW), benched on 32 seeds, its score predicted before ngspice
  lived it: 2.03 predicted, **1.65 [1.47, 1.84] lived** (held out, 64 lives, the job done, none stranded): 80% of the
  prediction. The gap is one quirk between blocks (the second thruster firing alone as a drive begins); with it in the
  model they tie. **The method is close enough** (the user, 2026-10-29): design in the model, check in SPICE that it
  is realisable, retune there only when realism matters.
- **Which level to think at** (D14): B at three levels. Tuned in its own simulator, B built of Sepulchre's elements
  ties with the block model (2.06 against 2.03) but costs 8 times the power of gates (31 nW, 841 parts, against 3.7 nW,
  151) and fails with biology's noise, which no setting of its knobs survives but size does: four times the capacitance on the bit's chain does the job with it for 48 nW (twice biology's still fails). Blocks are the fastest place to design, and both levels below realise them
  faithfully; gates are cheapest; Sepulchre's elements have the knobs a self-tuning brain would turn.
- **Self-tuning** (D15): B's knobs mistuned at birth (up to 3 times off), tuned from its own outcomes (taste and its
  own firings) in 10,000 s lives. A tuner with no coordinator (each knob wiggling at its own moments, correlating
  its wiggle with a broadcast "better than usual") reaches 1.98 against the floor's 1.74 and the ceiling's 2.47
  (+0.24 [+0.15, +0.34]), and on lopsided bodies, the balance a sixth knob, 0.90 against 0.19 and 1.94. A Bayesian
  optimiser with the same information and unlimited computation does no better (1.61, never converging; 0.92 on
  lopsided bodies), and annealing hurts: within a life, perfect is local; the global search is evolution's.
- **Tricks nobody designed** (D16): 200 random sequence detectors beside B, each adding a beat to a motor, credited
  by taste through fading tags. On lopsided bodies +0.30 [+0.16, +0.44] over B (0.59, stranding 61% to 14%), by
  learning (+0.71 over the same detectors not learning), but not by steering: it prunes the harmful random beats and
  keeps those that unstrand. On the standard body it costs 0.26.
  Taken apart (D16, continued): the right steer, planted, pays (0.68, job done, against B's 0.11), and meals credit
  it only if exploring runs at the outcome's timescale (one coin per burst: 0.67, job done); among random detectors
  50 find a little steering in 100,000 s lives (0.24 against B's 0.11, unpaired), far below the planted steer alone
  (0.70), their exploring spoiling B's colour choices, and credit colliding as they multiply.
- **Recruitment, case 1** (D17): with taste wired to nothing, a generic grower (predict what follows each eye, grow a
  recruit where a bad outcome is predicted and happens anyway, let it try the pathway's operations) grows in every
  poison life on the poison eye, in no all-food life, and, trying every operation once before keeping the best,
  reaches 1.80, tied with B's designed learning (2.01; the unwired -3.35).
- **The arena** (D18): ten robots that eat each other by biting tails, being bitten a bad taste; each robot a disc
  since 2026-10-31 (the triangle's colliding discs hooked each other; the figures below are the triangle's; on the
  disc, with firing charged (uncharged before: every earlier arena figure ignored firing's cost), escape grown nets
  +0.14, matching the best scripted burst, but against a tracker whose standing policy is tuned for the arena only
  +0.03; no pursuit or memory pays; what standing policy pays depends on the population). Beside the tracker
  (a Braitenberg steerer, evolution's design here), a grower told nothing of its purpose grows escape from bites, a
  pain no sense predicts: a recruit of two knobs (each motor's rate when bitten), jittered at each bite and judged by
  the taste just after, reaches 86-97% of the best scripted reflex held out (+0.22 to +0.25 meals a 10 s net, the
  ceiling +0.25); its gain vanishes when no response can stop the pain. Steering, pursuit and a memory of recent
  bites failed to certify as growth cases.
- **A lopsided body learned from every drive** (D19): the drive's balance jittered at each drive and judged by the
  food pulses that drive saw, the jitter shrinking with experience: 0.98 [0.78, 1.17] held out in 2,000 s lives
  (floor 0.36, ceiling 1.92), surely above D15's meal-judged tuner on the same lives (+0.26 [+0.07, +0.45]). On the
  drive started in step (D20): 1.02 against the tuner's 0.80 (+0.21 [+0.02, +0.40]), ceiling 2.15: 37% of the gap.
- **The body learned by prediction** (D20): scanning with one motor turns the body steadily, so what it sees comes round
  once a revolution, and the period gives that thruster's strength. Sweeps of its own (5 s with one motor, every 20 s
  until its estimate stalls) and a bank of coincidence counters find both periods: 1.66 [1.55, 1.76] held out on
  lopsided bodies, 83% of the gap closed, surely above every outcome-judged learner (+0.68 over D19's); with 8 s
  sweeps 1.71 (87%), costing 0.18 on the standard body (2.46 to 2.27), all of it in the first minutes. Sweeping
  only when frustrated (fewer than 8 meals in the last 32 s) removes that cost (2.47, tied with B) and keeps the gain
  (1.68 on lopsided bodies, 85% of the gap, 5 sweeps instead of 12; 1.39 on fully varied ones). A bank of 96
  log-spaced coincidence counters, chance from their neighbours (lateral inhibition) and a fixed comb does as well as
  the exact histogram held out: what is left for a circuit is the delay line holding a sweep's pulses. Sweeping at birth and every 12 s until the evidence is in, gated by the meal rate on a
  clock that stops while sweeping: lopsided 1.81 held out, 93% of the gap; standard 2.48, tied with B. A balanced
  drive used to start out of step (each motor its own oscillator, motor 1's stale from the last drive), costing
  ceilings and learners alike; started in step (`sync=1`): ceiling 2.15, learner **2.03 held out, 93% of the gap**,
  standard body 2.45, tied with B; fully varied: ceiling 1.94, learner 1.59. In counters on the fixed drive, lopsided:
  the bank 1.92 (87% of the gap, a little below the exact histogram, -0.11 [-0.25, -0.01]), its delay line's stages
  holding up to 3 pulses (2 bits) 1.88, tied with the bank; one-bit stages 1.78 (79%), probably below it. Restricted
  to what a circuit could hold (192 counters, 2-bit stages; still blocks, nothing built in transistors): lopsided 1.93 (88%), fully varied 1.68, standard 2.49, each
  tied with the exact histogram.
- **What placing blocks could be worth** (D21): the seer told each block's place only as well as pulses tell it
  falls from 4.5 to 2.8 (offset across unknown, range +-50%) or 2.1 (neither), against B's 2.54: the eyes don't say
  where across their corridor a block is, so a memory of places adds little unless the brain senses across by
  moving.
- **Sideways sensing, evolved?** (D22): a 6-node continuous-time network evolved in the loop, told the colour,
  reaches 2.03 held out (B told the colour 2.54) and forages as B does, eating blocks only within the mouth's 1 mm
  of its path: no sideways sensing emerged. Under B's movements the pulses' timing says almost nothing about a
  block's offset (R2 0.02; the side no better than the sweep's bias); probing by wiggling makes it a little readable
  (the side right in 77% of pulses against 56%), but no dance-like policy uses it (all below B, 0.8-1.9 against
  2.6). These eyes don't offer sideways sensing; B is near what they allow, and the headroom needs a body change
  (the user's; D24 prepares a split eye). (A beat's 18 degree turn, thought too coarse, can be cut to 7 by timing,
  D24.)
- **The dance form** (D23): D20's period found by an entraining oscillator fails (sweeps of 4 revolutions, 5 blocks
  each: it never locks); a bank of 96 resonators with harmonics summed reads a 20 s spin's period better than the
  intervals' histogram (69% against 53%) but plateaus lower (69% against 88% at 40 s), for as many parts.
- **A split eye, prepared for the user's decision** (D24; world.py unchanged, the split made in an experiment's
  wrapper): each eye's pulses tagged by which half of the corridor saw them, the halves wired at random. B told the
  colour, plus a reflex: one food pulse or more from one half and at most one from the other in 0.2 s turns it
  towards that half, by one beat with its partner 10 ms later (7 degrees, not a lone beat's 18: finer turning by
  timing, no body change). Which motor turns towards which half is learned from its own scan in a median 12 s
  (right in 254 of 256 lives by the end). Held out on fresh seeds: **3.02 [2.92, 3.11] against B's 2.49 [2.40,
  2.58]** (+21%; told the map, 3.14); on lopsided bodies told their balance, 2.71 against 2.32 (+17%).
- **The first story** (D25; `STORIES.md`): B's doubt written only while a drive is on closes the whole gap to being told
  the colour (2.50 against 2.49 held out, B 2.21), and stands at component level with silicon's noise (2.15, B 1.84).
- **The second story** (D26): unequal thrusters, its baseline and target measured: immune to 1%, half the score gone by
  x1.25; on the usual bodies 0.21 against 2.56, one number of about 3.7 bits.
- **The interventions table** (D28; `STORIES.md`): ten mismatches against story 1's circuit, judged on fresh seeds. Each has a sure manual cure, though row 9's is tiny and the rest of its gap was never there. Eight have an automatic version that helps and ties with the base brain in the plain world; row 6's costs 0.02.
- **A universal circuit** (D29; `STORIES.md`): a bank of predictors, one setting in every world, block model only. Surely above base in 8 of 10 rows and 13 of 14 combinations, plain tied at 100, 400 and 1,000 s; surely below its row's own version on thrusters, swaps and digest; not watched on screen.
- **The ladder of harder tests** (D27; `STORIES.md`): swaps, sequences, a rule about time. A sequence memory grown when frustrated solves alternate and pattern; one brain reading the run of goods before each poison chooses between cures, surely above the baseline on five tests of eight, tied on three (plain, slow swaps, and digest, which its menu cannot cure).
- **Bodies** (D13): with each thruster 0.5-2, every fixed design collapses (B 0.32, the best searched on such bodies
  0.76); told its balance, B gets 1.92 (2.15 with its drive started in step, D20); eight local rules for finding the balance reach at most 0.8; judging each
  drive does better (D19), and a model learned from its own turning far better (D20).
- **Ceilings** (D13): omniscient about 20, a perfect memory of what it has seen 4.5, B told the colour 2.54.
- Values not yet tuned for `learn_avoid` (its values are learn_hold's and the prototype's). A pruned circuit
  must be judged held out: pruning's last cut, "not surely worse" on 12 seeds, was surely worse held out (D9).
- **The simulator** is checked in both step and tolerance: ngspice's error control is tightened in every netlist
  (D7).
- Queue 7 re-judged every circuit with the tightened control (D7) and re-tuned learn_hold (noise, no trend: its
  output kept as `results/learn_hold_tune_q7.json`, never judged); the foraging circuits' re-tunes were cancelled
  (their results stand, D7).
- Open questions: `QUESTIONS.md`.

## D1: the problem, from above (2026-10-26)

**What the body gives.** Each eye looks straight ahead along a corridor as wide as the mouth's sweep (2 mm), up to
15 mm, and pulses at random (Poisson) at up to 50 per second for a block close up, half that at 5 mm, about 5 at
15 mm. It says how much of its colour is ahead, never where: there is no bearing to steer by. Anything seen is in the
mouth's path already. With both colours food, the two eyes are interchangeable: a circuit may simply add them.

**What the thrusters do.** Each firing adds 20 mm/s forward and 16 rad/s of turn, both fading at 50 per second: 0.4 mm
and 0.32 rad (18 degrees) per firing. Both at once go straight 0.8 mm. One alone drives a circle of about 1.2 mm
radius whatever its rate. So a circuit's whole repertoire is: go straight (both), turn while creeping (one), or rest.

**What it costs.** Resting costs a meal per 10 s whatever the creature does; a firing 1/500 of a meal; the circuit
its power, a meal per 10 s per microwatt. Blocks: 36 in a 60 mm torus, 0.01 per mm^2; about 7 lie within the eyes'
range of any point, and in an all-food world a creature that keeps finding them almost never strands.

**Approaches.**

1. *Blind straight*: fire both thrusters at a steady rate and sweep a 2 mm swath. No sensing; costs about 125
   firings a meal; its efficiency rises with speed, since the resting cost is spread over more meals.
2. *Reflex and scan*: a clock fires one thruster (turning the eyes round the circle), and each pulse fires both
   (approach). Cheap per meal, but the clock keeps turning the creature while it approaches, and a far block's few
   pulses are lost.
3. *Hold and drive* (the hold-and-roam circuits' kind, without the bit): after any pulse, both thrusters fast for a
   short while; otherwise one, to scan. Equivalently, each pulse fires a burst on both thrusters and silences the
   scanner for a moment.
4. *Run and tumble* (bacteria): go straight, turn at random moments, turn less while pulses come. A cousin of 3.
5. *Roam*: drive off after a long spell of nothing; needed with poison, not, it turns out, here.

**Policies first** (`discrete/policies.py`: rules, not circuits, on the real body, 16 seeds, circuit power 0):

| policy | best values | efficiency | gain rate | firings /10 s |
|---|---|---|---|---|
| blind straight | 40 / 120 per s | 4.2 / 5.5 | 10.8 / 31.9 | 800 / 2400 |
| two free clocks, eyes ignored (a wide circle) | | 0.2 | 0.4 | strands |
| reflex and scan | scan 4 per s | 3.3 | 4.1 | 123 |
| reflex, scanner silenced 0.1 s after a pulse | scan 8 | 5.8 | 7.9 | 190 |
| ... each pulse firing both 4-8 times | scan 16-32, silenced 0.05-0.1 s | 8.5-8.9 | 18-27 | 550-1040 |
| hold and drive | scan 16, drive 80 per s, hold 0.1 s | 7.8 | 18.1 | 663 |
| hold and drive, slower drive | scan 16, drive 40, hold 0.1 | 7.2 | 13.0 | 400 |

So: a hold is worth a lot (3.3 to 5.8), a strong approach more (8.5); a long hold hurts (1 s: the creature drives on
past where the block was); stranding is rare without any roam. The target for a circuit: on any pulse, both
thrusters at 40-160 per second for 0.05-0.2 s; otherwise one at 16-32 per second. The blind driver is the baseline to
beat, and it is not weak: speed alone gives 5.5.

## D2: the technology and the bench (2026-10-26)

The interface in discrete parts (`discrete/life.py`, my choices, to confirm or change):

- a 3 V lithium coin cell; its delivered power is the circuit's;
- each eye a photodiode from the supply into its sensor node, 1 uA while it pulses (2.5 ms), unable to lift its node
  above the supply; both eyes may feed one node (a wire);
- each motor a thruster driver's CMOS Schmitt input: a firing each time its node rises through 2/3 of the supply,
  re-armed below 1/3 (the same rule as every brain's spike, in this technology);
- parts from stock: 2N3904 and 2N3906 transistors, 1N4148 diodes, resistors 1 MOhm to 1 GOhm, capacitors 47 pF to 30 nF;
  each seed draws its own tolerances (resistors 1%, capacitors 5%, a transistor's saturation current 20% and gain
  25%: one standard deviation). No noise in SPICE (a discrete circuit's thermal noise is microvolts against volts);
  the body's pulses are random and every seed's parts differ.

**Power decides the oscillator.** At a microwatt a circuit costs as much as resting, so it must run on nanoamps. A
classic astable multivibrator (one transistor always conducting) or a real programmable unijunction (valley currents
of microamps) can't. A PUT built of a PNP and an NPN can: the timing capacitor charges through a large resistor until it
passes the gate's voltage by a diode drop, the pair latches and dumps it into the NPN's base, and lets go once the
timing current alone can't hold it (below about 0.6 V over the NPN's base shunt). Seven parts; on the bench 12-32 Hz
at 80-130 nW, most of it in the gate's divider. The limit that shaped the design: the pair lets go only if its
charging current stays below that holding current, and fires only if it exceeds a peak current about 2.4 times
smaller, so a current can speed the oscillator up only about that much before it latches on. (Found on the bench:
the hold's extra current latched it until the hold drained.)

A closed-loop life of 100 s takes about 15 s of SPICE: tuning in SPICE itself is affordable.

## D3: hold and drive, 14 parts (2026-10-26)

`discrete/circuits.py`, `hold_drive`: both eyes feed one emitter follower (1 transistor), which charges a hold
capacitor at each pulse to about the supply (3.0 V on the bench: a photodiode can push its node a little above
the supply, as a solar cell does); the hold leaks through one resistor (rf) into the
oscillator's timing node, so it rests at that node's mean (below the motors' threshold) and, while charged, can speed
the oscillator up. The oscillator (7 parts) pulls motor A's pull-up low at each beat through an NPN (one thruster:
scanning); motor B's pull-up comes from the hold node, through an NPN of its own, so it fires too only while the hold
is above the motors' threshold (both thrusters: straight ahead).

What the bench and the closed loop taught, in order:

- **Tuning blind fails.** CMA-ES in closed loop from hand-set values: with fresh seeds each generation the scores
  jumped as much as any gain; with the job as a cliff (any stranded life fails the generation) the search followed
  the riskiest of the failing candidates; with a step of 0.15 of a log range (a factor of 2.8 for a resistor, where
  the switch's window is 3) every candidate was worse than the mean. Fixed: the same 16 seeds every generation, a
  smooth objective (efficiency less the shortfall of each third of each life: `tune.robust`), a step of 0.04. Even so
  a life's whole path changes with a tiny change of values, so the landscape is rugged at small scales.
- **So screen on the bench first** (`discrete/screen.py`): rates at rest, in the hold after single pulses, and
  through a burst of pulses, against the policy's best; then closed loop. Each test found a failure the closed loop
  had hidden: (1) with only a burst test, the screen chose a hold of 16 ms (motor B fired twice per pulse, the policy
  wants 0.1-0.2 s); (2) with only single pulses, a hold whose current, held at its top by a near block's frequent
  pulses, latched the oscillator: in a life it fired 7 times a second while a block was in view and 11 while none
  was, stalling exactly when it should drive (efficiency 2.5).
- **The speed-up is not needed.** With both tests the search pushed rf to its bound (1 GOhm): the best circuits
  barely speed up after a pulse; motor B simply joins motor A while the hold lasts (the policy "hold and drive" with
  drive = scan: 6.0 at 32 per s). The hold's current can only add within the switch's window anyway.
- **The best screened start**, scanning at 63 per s (closed loop, 16 seeds x 40 s): **efficiency 6.6, gain rate
  18.4, 114 nW**, none stranded: at the policy's level for its kind (5.5-6.0), four times the hold-and-roam circuits'
  (which face poison too). The hold costs power too: each pulse refills its capacitor from the supply through the
  emitter follower (a 2.25 nF hold drew 270 nW in a life against 87 at rest).
- **The diode must not leak.** A 1N4148 leaks nanoamps reversed, as much as these circuits' currents: in a pared
  variant it drained the hold. The diode is a low-leakage one (BAS416 class, picoamps).
- **The bench undercounts brief firings.** `bench` writes its traces at its step (20 us), and a motor's dip at a beat
  can be shorter: at 5 us the best start scans at 60 per s on the bench where 20 us counted 37, and after one pulse
  motor B fires on 12 beats (0.17 s, h from 3.0 V down through 2 V). The closed loop counts firings at every
  internal step and is unaffected; the screen's rates (and so its fitness) were low, a filter's error, not a
  judge's.
- **The timing node can't be a motor.** Charging it through a resistor from 3 V up past the motor's threshold (2 V)
  and down below 0.8 V needs a current range of about 3, the switch's whole window (it fires above about 0.4 V over
  its base shunt and holds below about 3 times that): it either latched or stalled at the top. A motor needs its own
  buffer.

## D4: paring to the bone (2026-10-26)

`discrete/prune.py`: each part of a circuit taken out in every way it can be (opened; shorted; for a transistor, two
of its terminals joined), every variant living the same 16 closed-loop lives; the most promising few re-screened for
new values on the bench. Two modes: **prune** keeps a cut only if the circuit does as well as the whole within noise;
the **ladder** keeps cutting the least harmful part, however much is lost, while the job is still done, to show what
each part buys.

**Pruned, hold_drive keeps all 14 parts**: the nearest cuts (the hold's leak: 6.1; the eye follower: 5.8, against
6.8) are surely worse. Re-screening values after a cut never rescued one: the bench screen is a filter, not a judge.

**The ladder** (chosen on seeds 30000-30015; judged on 32 held-out seeds, 100 s, `discrete/judge.py`):

| parts | what went | efficiency [95%] | gain rate [95%] | stranded | power |
|---|---|---|---|---|---|
| 14 | (hold and drive, whole) | 6.62 [6.45, 6.80] | 18.2 [17.5, 19.0] | 0% | 113 nW |
| 13 | the hold's leak: the hold drains only through motor B's own firings (its pull-up comes from the hold) | 6.2 (on the ladder's seeds) | 16.8 | | |
| 12 | the eye follower: the eyes charge the hold capacitor directly (for free: the follower refilled it from the supply) | 4.96 [4.58, 5.30] | 13.1 [12.0, 14.2] | 3% | 93 nW |
| 11 | the switch's base shunt: the two motor NPNs' base junctions take its current instead | 2.6 (ladder's seeds) | 4.1 | | |
| 10 | the hold capacitor: each pulse fires motor B directly while motor A scans | 2.94 [2.75, 3.13] | 4.5 [4.1, 4.8] | 0% | 151 nW |
| 9 | no cut still does the job | | | | |

What each part buys:

- **The hold is the whole difference between 3 and 5-7.** Without it the bottom rung is counter-turning (`counter10`):
  motor A scans and each pulse fires motor B, so their turns cancel while a block is in view, and the creature
  zig-zags in. The ladder found it unaided; it is the policy "counter" of D1 (3.5-3.9 there).
- **A hold can drain by doing its job**: with motor B's pull-up taken from it, each of motor B's firings spends a
  little of the hold, so it needs no leak of its own; the longer it drives, the sooner it stops.
- **The eye follower buys about 1.7** (12 to 14 parts with its leak): it lifts the hold to about the supply at once
  however weak the pulse, where the eyes' own charge (2.5 nC a pulse) lifts it only partway. It costs
  power: each refill comes from the supply.
- **The switch's shunt resistor is a part the motor buffers can do without**, at a price: their bases shunt the
  switch's NPN, so the window's edges follow two transistors' gains instead of a resistor.

**Each rung tuned as a circuit of its own** (`discrete/tune.py`, CMA-ES on seeds 20000-20015 x 40 s; then judged on
the 32 held-out seeds x 100 s, `python -m discrete.judge`, compared paired with `--compare`), with the blind straight
driver (9 parts) as the baseline:

| circuit | parts | efficiency [95%] | gain rate [95%] | stranded | firings /10 s | power |
|---|---|---|---|---|---|---|
| hold_drive, tuned | 14 | **7.07** [6.84, 7.27] | 18.6 [17.8, 19.4] | 3% | 771 | 93 nW |
| hold_drive, screened (above) | 14 | 6.62 [6.45, 6.80] | 18.2 [17.5, 19.0] | 0% | 820 | 113 nW |
| hold12, tuned | 12 | 6.50 [6.05, 6.85] | 15.9 [14.5, 16.9] | 3% | 676 | 90 nW |
| straight, tuned (blind) | 9 | 6.30 [5.51, 7.00] | **82.6** [71.5, 92.6] | 0% | 5937 | 229 nW |
| counter10, tuned | 10 | 4.06 [3.86, 4.25] | 6.6 [6.2, 6.9] | 0% | 263 | 87 nW |

Paired: tuned hold_drive is surely the most efficient (+0.45 [+0.18, +0.73] over its screened start, +0.57 over
hold12, +0.77 [+0.02, +1.53] over straight); hold12, straight and the screened hold_drive are tied on efficiency.
Tuning moved hold_drive's gate divider up (rg1 542 M, rg2 116 M), its hold down (814 pF) and rf to its bound again:
it saves power (93 nW) more than it changes behaviour.

**The blind driver found speed.** Tuned, it beats at about 300 per second, both thrusters at once: 240 mm/s, laps of
the 60 mm world four times a second, sweeping a 2 mm swath; 83 meals per 10 s, four times any sighted circuit, and as
efficient as the screened hold_drive, since the resting cost is spread over so many meals. It works only because the
two thrusters are identical: with thrusters unequal by 1% it circles (D5).

**A note on the machinery**: ngspice run as a library keeps every circuit and its results; a worker grew by half a
gigabyte in an hour and the laptop ran out of memory. Each run now unloads its circuit (`destroy all`, `remcirc`): a
worker stays at 150 MB. Bench runs and closed-loop runs can't share a process (ngspice's two modes): two pools.

## D5: can a circuit tune itself to its body? (2026-10-27)

The user's question (2026-10-26): in an all-food world, give each life's creature slightly different
characteristics; the best circuit would be one that tunes itself, in its life, to the body it finds itself in: a
subtle evolution with local learning. Asked first at the level of policies (`discrete/policies.py`, rules on the real
body, power 0), where trying a rule costs seconds.

**Bodies that differ** (`discrete/bodies.py`, my choices, to confirm): each factor on `world.py`'s values, drawn
log-uniform within 1/x to x for each life: both thrusters' strength (x2), one thruster against the other (x1.25),
the eyes' sensitivity (x2), drag (x1.5). `world.py` is unchanged: a life's body is swapped for a `VariedBody` after
`creature.Life` builds it, so the world, wiring and start are the unvaried life's.

**What is there to gain?** (`python -m discrete.variation`: hold and drive's 64 settings of scan, drive and hold on
each of nine bodies, 12 seeds x 60 s; the standard body's best setting on each body against that body's own best):

| body | own best (scan, drive, hold) | efficiency | the standard's best there | lost |
|---|---|---|---|---|
| standard | 16, 160, 0.05 | 8.25 | | 0% |
| weak (x0.5) / strong (x2) | 32, 80, 0.1 / 8, 160, 0.05 | 5.25 / 11.22 | 5.04 / 11.02 | 4% / 2% |
| dim / bright eyes | 8, 160, 0.05 / 16, 80, 0.05 | 6.67 / 9.01 | 6.64 / 8.48 | 0% / 6% |
| slippery / sticky | the standard's | 8.92 / 7.04 | | 0% |
| left / right thruster x1.25 | 32, 160, 0.05 / 32, 80, 0.05 | 5.71 / 6.66 | 5.29 / 4.70 | 7% / 29% |

So scan, drive and hold hardly need tuning: a body's own best gains at most 6% over the standard's (strength and
eyes change what a body *can* do, 5 to 11, not what it should do). The one thing that matters is **unequal thrusters**,
and no setting of these three knobs recovers it. A trim does: each motor at its own drive rate (`balance`: motor 0 at
drive x b, motor 1 at drive / b, the common rate fired together), set to cancel that body's mismatch (an oracle, per
life, from its wiring): on 24 bodies with thrusters unequal by up to x1.25, **fixed 6.78, perfectly trimmed 7.75**;
on two fixed mismatched bodies 5.0 and 4.6 against 7.8 and 8.2 trimmed. A trim error costs fast: 7.65 at 2.5% (log),
6.44 at 5%, 5.62 at 10%.

**Tuning the trim in a life fails** (24 bodies x 100 s, unless said):

| rule (the knob log b) | efficiency |
|---|---|
| fixed b = 1 | 6.78 |
| oracle trim | 7.75 |
| lock-in, rewarded by meals: wobble +-0.1, period 2 s | 5.5-5.7 (3 bodies) |
| lock-in, rewarded by the eyes' pulses while driving: wobble 0.025-0.05, period 0.5-2 s | 6.05-6.94 |
| ... 400 s lives | 5.77-6.90 (fixed 6.51, oracle 7.81) |
| per-approach dither (each approach's sign tossed), pulses or meals | 5.49-6.62 |
| run and tumble (drift; turn back when meals come slower) | 5.53-6.30 |

The lock-in does find the sign (75-100% of lives right by 100 s), but slowly, and the wobble it needs is itself a
mistrim, costing as much as it gains. The numbers say why: about 200 meals in a life, so a difference between two
halves of a wobble shows only if it is above about 14%; the trim's whole gain is 14%. The eyes' pulses are more
frequent but a poor reward: a well-aimed approach eats sooner and so sees *fewer* pulses. Earlier tries on the other
knobs: lock-in of the scan rate drifts the right way (weak bodies up, strong ones not) but the spread across lives
is wider than the difference by 100 s; a homeostat (the more eaten lately, the slower the scan; 2 parts in a circuit)
lowered every body's efficiency (8.29 to 8.12, 7.22, 3.22 as its gain rose).

**What works instead is a loop closed through the eyes.** The structures' loss with thrusters unequal by up to
x1.25 (24 bodies):

| policy | standard | unequal | lost |
|---|---|---|---|
| hold and drive, scan 16, drive 160, hold 0.05 | 8.39 | 6.78 | 19% |
| hold and drive, scan 32, drive 40, hold 0.1 | 6.36 | 6.30 | 1% |
| each pulse fires both 8 times, scanner silenced 0.1 s (`reflex_hold`, scan 32) | **8.56** | **7.37** | 14% |
| counter-turning | 3.16 | 3.22 | -2% |
| blind straight, 300 per s | 5.98 | **0.22** | 96% |

and with smaller mismatches (within x1.01 / x1.03 / x1.1): reflex_hold 8.44 / 8.56 / 8.28; hold and drive 8.45 /
8.12 / 7.77; **blind straight 1.86 / 0.63 / 0.28**. Driving only while the eyes keep pulsing corrects a curve for
free: a block that drifts out of the corridor stops the pulses, the scan finds it again.

**In SPICE** (`python -m discrete.judge ... --motors X`, the tuned circuits on the 32 held-out seeds):

| circuit | equal thrusters | within x1.03 | within x1.25 |
|---|---|---|---|
| hold_drive, tuned (14) | 7.07 [6.84, 7.27] | 6.78 [6.63, 6.94] | 6.02 [5.79, 6.23] |
| hold12, tuned (12) | 6.50 [6.05, 6.85] | 6.80 [6.59, 7.00] | 5.71 [5.44, 5.99] |
| straight, tuned (9) | 6.30 [5.51, 7.00] | **0.73** [0.36, 1.24], 34% stranded | 0.25 [0.08, 0.56], 28% stranded |

**Conclusions.**

- The blind driver's speed was the simulator's gift: two thrusters identical to the last digit. No real pair is; a
  mismatch of 1% makes it circle. *A proposal for the user* (a change to the body, so theirs to make): give every
  life's thrusters a small mismatch (a few %), so that no design can lean on perfect symmetry.
- Self-tuning, as asked, has little to work with here: the knobs a circuit could tune barely matter across bodies,
  and the one that matters (trim) can't be found from about 200 meals in a life with a wobble cheaper than the
  mistrim. The way to cope with a varied body is structural: drive while the eyes say the block is still ahead.
- **The user's lesson** (2026-10-27): the body's dynamics need to vary from life to life, as the parts' tolerances
  do, so that no circuit is tuned to one exact body's accidents (README, What we've learned).
- Untried: a richer local signal for the trim. The eyes give no bearing; what a mistrimmed approach changes is how
  long a block stays in view, which is the pulses' *rate of change*, not their count.

## D6: one bit, learned (2026-10-27)

The user's next question (2026-10-26): take the best circuit and find the simplest way to add the bit, learned in its
life: food against poison, as every brain in this project must.

**Policies first** (`discrete/policies.py`, `judge_poison`: each seed lived twice, red then blue as poison; 12-24
seeds x 100 s). The learning rules are options of any approach (`learn`), as is the roam (`bored`, `roam`):

- `toggle`: only one eye may start an approach; a poison flips which (after `n` poisons with no food between;
  `blame` "held": only poisons eaten while approaching count; `forget`: the count fades);
- `trace`: each eye's pulses leave a fading trace; poison turns off the most traced eye (and on the other), food
  turns it on (`latch`: exactly one on; `poison_only`: food changes nothing).

| rule (with the roam: 3 s with nothing, then 1 s straight at 20 per s) | efficiency | food:poison, last third | stranded | job |
|---|---|---|---|---|
| toggle, n 1 | 0.14-0.46 | 2.0-2.1 | 0% | no |
| toggle, n 1, blame held | 1.18-1.21 | 2.6-2.7 | 0% | no |
| **toggle, n 2** | **1.83-2.00** | 3.8-4.0 | 0% | **yes** |
| toggle, n 2, blame held | 2.12-2.29 | 4.1-4.6 | 0% | yes |
| toggle, n 2, forget 0.5 / 1.5 / 5 / 15 s (hold and drive) | 1.69 / 1.83 / 1.87 / 2.02 | 3.3-3.9 | 0% | yes |
| trace, tau 0.1-1 s (with or without latch) | -1.11-1.12 | 1.6-2.9 | 0% | no |
| trace, latch, poison only, tau 0.1 s | 1.56 | 3.2 | 0% | barely |
| toggle, n 2, no roam | 1.36-1.72 | 3.8-4.2 | 25-33% | no |

What decided it:

- **A roam is needed** (a third of the lives strand without it, now that only half the blocks are worth
  approaching), and it must be **slow**: driving blind eats whatever lies ahead, so a roam at 80 per s lost to one at
  20-40 (1.42 against 2.09-2.29).
- **Two poisons, not one**: a single poison is often eaten by accident (in the way of a food, or during a roam), and
  flipping on it sends the creature after poison until the next mistake. With n = 2, a creature is on the wrong
  colour for only about 1.5 s of a life. The count may fade within a second or two: when the creature follows the
  poison colour, poisons come in quick succession.
- **Trace (which eye saw most just before) misjudges** a quarter of poisons and a tenth of foods: a block of the other
  colour is often closer or more in view at the moment of a meal.
- Most poison is then eaten while scanning (turning in small circles near poison), not while approaching or learning.

**The circuit** (`discrete/circuits.py`, `learn_hold`; 49 parts): hold12 (the oscillator, motor A scanning, motor
B's pull-up from the hold) and

1. *the gate*: each eye's node feeds the hold through a diode, and a Darlington pair shorts it to ground while the
   latch feeds the pair's base (8 parts);
2. *the bit*: a latch of two cross-coupled NPNs, toggled by a falling edge through two steering diodes and capacitors
   (each junction resting at its own collector, so only the transistor that is on gets the edge; 12 parts);
3. *the doubt*: the taste node with a capacitor (each poison pulls it down by about 0.8 V; food lifts it; it recovers
   towards the supply through 1 GOhm over about 1.5 s), and two NPNs that turn its fall below about 0.65 V (the
   second poison in quick succession) into a sharp falling edge for the latch (7 parts);
4. *the roam*: a second, slow oscillator (7 parts, a beat every 2-3 s) whose discharge pulls its gate low and so
   turns on a PNP from the supply into the hold (3 parts): a phantom pulse, so both thrusters drive for a while.

Each piece was found by a failure on the bench (`bench` now takes taste pulses too):

- With the eyes on the latch's own collectors (6 parts fewer), every pulse of the shorted eye flipped the latch:
  the eye's microamp lifted the collector before the nanoamp base could take it, and the cross-coupling carried the
  lift to the other side as a flip. Speed-up capacitors (the textbook latch's) made it worse; 300 pF on each
  collector didn't cure it. Hence separate shunts.
- A 2N3904's gain collapses below a microamp (its base's recombination current, ISE, takes nanoamps at 0.45 V): a
  shunt fed 4.5 nA couldn't sink an eye's 1 uA, and the shorted eye still lifted the hold. With single shunts the
  latch needed tens of nanoamps (50 MOhm loads: on a bench scan of loads, 100 MOhm let the shorted eye lift the hold
  1-2 V, 200 MOhm fully), and the circuit drew about 440 nW, four times hold12. A Darlington pair for each shunt (2
  parts more) needs a hundredth of the base current: loads of 500 MOhm and 1 GOhm, the shorted eye lifting the hold
  0.16 V at most, the free one to 3 V, toggling right on every part draw tried; the circuit draws 180 nW.
- The threshold transistor's base loaded the taste node, holding it at 0.6 V, so that any single poison flipped the
  latch: its base resistor had to be as large as the node's pull-up.
- A resistor from the supply into the hold as the roam had no hysteresis: at 1 GOhm the hold never reached the
  motors' threshold (12% of lives stranded); at 150-300 MOhm it sat there and the creature drove blind without pause
  (efficiency -1.8 to -0.1, food:poison 1-2). Hence the oscillator, which needed its shunt within the switch's window
  (250-400 MOhm at a charging current near 1.4 nA; at 30-150 MOhm it never fired).

**First closed-loop results** (8 seeds x 2 lives x 100 s, values set by hand, `python -m discrete.poison`):

| circuit | efficiency [95%] | food:poison, last third [95%] | stranded | power | job (estimates) |
|---|---|---|---|---|---|
| hold12 (ignores taste) | -2.67 | 1.00 | 0% | 91 nW | no |
| learn_hold, roam by a 1 GOhm resistor | 0.76 [0.39, 1.09] | 3.46 [2.82, 4.15] | 12% | 401 nW | no |
| learn_hold, roam oscillator (ct2 3.3 nF) | 0.71 [0.39, 1.02] | 3.38 [2.62, 4.20] | 0% | 449 nW | yes |
| learn_hold, roam oscillator (ct2 5 nF) | 0.93 [0.67, 1.16] | 3.69 [2.67, 5.15] | 0% | 446 nW | yes |
| ... 16 seeds | 0.89 [0.66, 1.11] | 3.58 [2.98, 4.31] | 0% | 447 nW | yes |
| ... the roam only after the hold has been low a while (16 seeds; 3 parts more) | 0.69-0.85 | 3.3-3.7 | 0-3% | 446 nW | yes |
| ... Darlington shunts (16 seeds; 49 parts) | 1.21 [0.94, 1.47] | 4.16 [3.43, 5.01] | 0% | 179 nW | yes |
| **... held out** (32 seeds from 50000 x 2) | **1.12** [0.95, 1.27] | **3.48** [3.06, 3.92] | 2% [0%, 8%] | 182 nW | yes, sure but for stranding (and so with tight error control: D7) |

It learns: the latch flips 0-5 times in a life and settles on the food colour (seen live, `python -m discrete.watch
--circuit learn_hold --poison`: 13 red to 4 blue by 14 s with blue poison). Held out, it does the job by every
estimate, food:poison surely above 3, its one stranded life in 64 leaving the stranding interval's top at 8%. Against
the minimal search's chip circuits (efficiency 1.4-1.7, about 500 transistors each) it is less efficient, but it is 49
discrete parts.

A roam that waits for the hold to have been low a while (an NPN emptying the roam's timing capacitor while the hold
is above about 2 V), which doubled a policy's efficiency over a free-running roam (1.83 against 0.56-1.03), didn't
help the circuit (0.69-0.85 against 0.89, ties): its roams are short bursts (a phantom pulse, about 0.1 s of driving),
so they rarely interrupt an approach anyway. Left as an option (`rz1`), off.

**Tuned** (`python -m discrete.tune learn_hold 8 --poison --lam 8 --only cq rq ct2 rsh2 rb ch rt rp`: 8 values, 8
generations, poisoned pairs on training seeds): noise ruled it, the generations' means wandering 0.62-1.07 with no
trend. Its best mean (rt 215 MOhm, rp 11 MOhm, ch 460 pF, rb 10 MOhm, cq 3.1 nF, rq 1 GOhm, ct2 6.5 nF, rsh2 466
MOhm), held out: efficiency 1.24 [1.12, 1.36], gain 2.93, last third 4.49 [4.01, 5.10], stranded 5% (3 of 64), 181
nW. Paired with the hand-set values on the same lives, tied (efficiency -0.12 [-0.33, +0.09], gain -0.29 [-0.79,
+0.21]), and it strands more, so the hand-set values stay (the run's output kept as
`results/learn_hold_tune_tied.json`, which `watch` and `draw` don't pick up).

## D7: checking the simulation itself (2026-10-27)

Every result above was lived with SPICE's largest step at a twentieth of a tick (0.5 ms) and ngspice's default error
control. A finer step is the standing check (`--finer F` on `discrete.judge` and `discrete.poison`), and it first
seemed to undo D4 and D6; it was the check that misled.

- **At finer steps with the default error control** (held out): hold_drive went from 7.07 to 6.41 (x8), 6.17
  (x16), 6.21 (x32); learn_hold from 1.12 to 0.69 (x2), 0.05 (x4), -0.69 (x8), food:poison from 3.5 to 1.7. On the
  bench the scanning oscillator fired 462 times in 10 s at 0.5 ms and 526-545 at 62-16 us, so I took 31 us as
  converged and the earlier values as fitted to a slow oscillator.
- **But the roam never converged that way.** On the bench (learn_hold, 30 s, no eyes), motor B, which fires during
  roams, fired 85, 87 and 73 times at 31, 16 and 8 us: a marginal event, the roam's PNP barely turning on, decided by
  each step's rounding. With the error control tightened (`trtol=1 reltol=1e-4`), every step from 0.5 ms to 16 us
  agrees: the scan 1687-1697 firings, motor B 39-47.
- **With tight error control, the results stand** (held out, paired):

  | circuit | 0.5 ms, default control (before) | 0.5 ms, tight (now) | 62 us, tight | 0.5 ms, ten times tighter |
  |---|---|---|---|---|
  | hold_drive tuned, efficiency | 7.07 [6.84, 7.27] | 6.87 [6.63, 7.10] | 7.01 [6.88, 7.14], tied | 7.09 [6.70, 7.36], tied |
  | learn_hold, efficiency | 1.12 [0.95, 1.27] | 1.17 [1.04, 1.31], tied | | |
  | learn_hold, last third food:poison | 3.48 [3.06, 3.92] | 3.44 [3.08, 3.87] | | |
  | learn_hold, stranded | 2% (1 of 64) | 5% (3 of 64) | | |

  So `life.ACCURACY` (those options) is now in every netlist, and `life.STEP` stays 0.5 ms; lives take about 1.5
  times as long. The default control had been close enough at 0.5 ms, by luck, and wrong at finer steps.
- **Every circuit re-judged** with tight error control (held out, all food), against D4's values:

  | circuit | parts | efficiency [95%] | gain rate | power | D4 |
  |---|---|---|---|---|---|
  | hold_drive tuned | 14 | 6.87 [6.63, 7.10] | 19.1 | 72 nW | 7.07 |
  | hold12 tuned | 12 | 6.61 [6.38, 6.84] | 17.3 | 84 nW | 6.50 |
  | hold_drive screened | 14 | 6.39 [6.11, 6.60] | 19.5 | 85 nW | 6.62 |
  | straight tuned | 9 | 6.31 [5.51, 7.01] | 80.2 | 213 nW | 6.30 |
  | counter10 tuned | 10 | 4.33 [4.05, 4.59] | 7.5 | 84 nW | 4.06 |

- **The roam's window is narrow, but its parts stay inside it.** Its PNP turns on as the slow oscillator's gate
  dips, set by the ratio of rbe to rbg: with rbg 300 MOhm instead of 200, or rbe 25 MOhm instead of 50, it never
  fires (the hold peaks at 1.3 V); with rbg 140 MOhm or rbe 70 MOhm it never lets go (motor B fires at every beat).
  Between, across seeds' parts (1% resistors), it roams 8-10 times in 30 s, each dash 0.1 s. (With the default error
  control it had looked erratic, 3 to 11 roams and dashes of 0.01-0.4 s: the same rounding.) A capacitor from the
  gate to the PNP's base instead of rbg, to kick it on for a fixed time whatever the dip's depth, never fired: the
  gate falls too slowly.
- The lives of the misleading runs are kept in `results/coarse_default_tol/`.

## D8: why learn_hold strands, and a simpler circuit that doesn't (2026-10-27)

**The cause.** The three stranded held-out lives (seeds 50012, 50017, 50023, each with red as poison) re-lived with
their nodes recorded: each ate steadily (a meal every second or two), then for its last 50-70 s the latch sat still on
the right colour, the free eye saw nothing (its node never above 1 V), and the poison eye kept seeing blocks. Eaten
blocks reappear elsewhere, so a creature that eats every food near it and refuses the poison turns its patch into a
poison patch. Its roam, a phantom pulse every 2-3 s, fired motor B about twice a second there: dashes of 1-2 mm, a
random walk too slow to leave. So the job is a *giving-up time* (foraging theory's: nothing found here for a while,
go elsewhere), not hunger: the creature had eaten recently (the user's reading).

**Giving up, built** (a prototype on learn_hold's parts: a follower charging a slow node u, cu leaking through ru;
when u has sagged below a PNP's threshold, set by a divider rh1, rh2 from the supply to u, the PNP feeds the hold, so
both thrusters drive straight until u is lifted again). 16 training seeds x 2 lives, paired with learn_hold's 1.17
on the same lives:

| u lifted by | old roam | parts | efficiency [95%] | poison | stranded |
|---|---|---|---|---|---|
| (learn_hold) | yes | 49 | 1.17 [0.98, 1.36] | 1.81 | 2 of 32 |
| food (the taste node), divider too strong: never hungry again | no | 45 | 0.53 | 1.35 | 9 of 32 |
| food, giving up about 4 s after a meal | no | 45 | 0.58, worse | 1.97 | 1 |
| food, about 4 s | yes | 54 | 0.68, worse | 2.33 | 0 |
| food, about 15-40 s | yes | 54 | 1.03, tied | 2.10 | 0 |
| the eyes (a sighting of the followed colour), about 6 s | yes | 55 | 1.26, tied | 2.02 | 0 |
| the eyes, about 6 s | no | 46 | 1.33, tied | 1.77 | 0 |
| **... and the silenced eye empties the hold** | no | **48** | **1.54** [1.40, 1.68], better | **1.23** | 0 |

- The first divider fed u itself: with rh1 + rh2 against ru, u could never sag below about 1.87 V, above the
  threshold. Both now 500 MOhm and 1 GOhm: u floors near 1.2 V.
- Giving up on *food* runs too often, and a blind straight run through the poison patch it leaves eats poison (two in
  quick succession also flip the latch). Giving up on *sightings* (the time since the free eye last saw anything,
  D6's policy roam "3 s with nothing seen") is better and makes the old roam oscillator (10 parts) unneeded.
- **The circuit never avoided poison**, it only declined to approach it: its mouth eats whatever lies in its path,
  and a run covers ground. The silenced eye's current was going to ground through its shunt; moved to a resistor
  (rd, 1 MOhm) on the base of an NPN that empties the hold, it cuts motor B whenever poison is ahead, so the creature
  turns off its line (2 parts).

**Held out** (32 seeds from 50000 x 2, paired with learn_hold on the same lives; `learn_avoid` as it was in commit
5a14076, its netlists identical to the prototype's; pruned to 46 parts in D9; `results/learn_avoid_48_heldout.lives` and `.log`):

| circuit | parts | efficiency [95%] | gain | poison | last third food:poison [95%] | stranded [95%] | power |
|---|---|---|---|---|---|---|---|
| learn_hold | 49 | 1.17 [1.04, 1.31] | 2.95 | 1.90 | 3.44 [3.08, 3.87] | 3 of 64 [2%, 13%] | 174 nW |
| giving up and avoiding | 48 | 1.51 [1.29, 1.70] | 3.71 | 1.41 | 5.26 [4.72, 5.97] | 0 of 64 [0%, 5.7%] | 128 nW |

Surely better: efficiency +0.34 [+0.07, +0.56], gain +0.76 [+0.16, +1.31]. With 8 seeds more (50032-50039), 80
lives: efficiency 1.56 [1.36, 1.72], gain 3.82, food 6.50, poison 1.34, last third 5.56 [5.03, 6.23], **none
stranded [0%, 4.6%]**, 128 nW: every interval within its limit, so **the job surely done**, as learn_hold's never was.
Watched live (`python -m discrete.watch --circuit learn_avoid --poison --seed 50012`, a life learn_hold stranded in).

**Policies, to rank the options** (`discrete/policies.py`, hold and drive with learn toggle n 2, forget 1.5 s, the
circuit's speeds: scan and drive 56 per s, hold 0.08 s; 64 seeds x 2): avoid "drop" (poison ahead drops the hold, as
the circuit does) is best with every roam; turning away actively (two extra firings of one thruster per pulse) is
worst, below no avoidance; with no roam a third of lives strand. But at these speeds even the oracle policy (told
from birth which sensor sees food; `oracle`) reaches only 1.41, below the circuit: the rule's speeds were wrong, so it
is no ceiling. (`until_seen`: a roam lasting until the next sighting, as the circuit's run does.)

**The ceiling** (the same rule over scan 8-56, drive 40-160 per s, hold 0.05-0.2 s, either roam, avoid "drop"; 64
seeds x 2): told the answer from birth, **2.73** (scan 16, drive 40 for 0.2 s after a sighting; drive 80 for 0.1 s or
160 for 0.05 s within 0.05: about 8 straight firings a sighting); learning (toggle, n 2), **2.29** at the same
settings. So, within this family of rules, learning costs about 0.4, and the circuit (1.51) loses another 0.8, mostly
to its speeds: it scans 3.5 times too fast, and its drive can't outrun its scan (both thrusters fire off one
oscillator's beats). The giving-up run and the clock roam tie as rules (2.17 against 2.29), so the run's 10 fewer
parts decide.

**The policy's speeds don't carry over to the circuit.** Tried on the 48-part circuit (16 training seeds x 2):

- *The hold speeding the oscillator* (hold_drive's rf, from the hold to the timing node), with the scan slowed to
  17-21 per s (ct 1-1.3 nF): here the hold rests near 0 V (motor B drains it at every beat), so rf drained the timing
  node and the oscillator nearly stopped (48 firings per 10 s, 75% of lives stranded). Through a diode (1 part more),
  30 MOhm gave a 17-21 per s scan and a 50 per s drive on the bench, but draining the hold through rf left one
  sighting 1 straight firing instead of 5 (100 MOhm stalled the oscillator). Not pursued.
- *Policies with the drive tied to the scan* (one oscillator, as in the circuit; 64 seeds): best 1.76 at 20-24 per s
  and hold 0.2-0.35 s (5-7 firings a sighting), against 0.82-0.96 at 56 per s. The circuit's hold buys about 5
  firings a sighting whatever the rate (it drains by a fixed charge a firing), so slowing its oscillator alone should
  have matched that policy. **It didn't**: ct 1 nF (about 21 per s) 1.04, ct 800 pF 1.14, both surely below 1.54 at
  56 per s (-0.50 [-0.78, -0.21], -0.41 [-0.71, -0.13]); food fell by half (3.3-3.8 against 6.2). The circuit at 56
  per s also beats its own policy at 56 per s (1.54 against about 0.9): what the circuit does (a hold topped up by
  each pulse, motor B's firings draining it, the run at the scan's rate) isn't what the rule does, so the rule's best
  settings don't transfer. A policy ranks *structures* (avoid by dropping the hold; giving up; some roam needed) but
  not a circuit's values.

## D9: pruned to 46 parts, and a stranding from a perfect body (2026-10-27)

**Pruning** (`python -m discrete.prune results/learn_avoid_start.json --poison --seeds 12 --seconds 40`, training
seeds 30000-30011 x 2, about 6 h; `results/learn_avoid_prune.log`). `prune.py --poison` now lives each seed red then
blue as poison and resamples each seed's pair together; a cut must do the job; a cut surely worse than the whole, or
failing the job, is dropped for good (so after the first round of 128 only 4 were retried); `--resume` restarts from
the cuts saved after each one (comparing against the circuit resumed from, not the original). It took 3 parts
(`results/learn_avoid_pruned.json`; its line numbers are the 48-part netlist's, commit 5a14076):

| cut | parts | robust (training) |
|---|---|---|
| (the whole) | 48 | 1.72 |
| rh2 (ub to u) shorted | 47 | 1.89 |
| rh1 (the supply to ub) removed | 46 | 1.78 |
| rs of the latch's side 0 (c0 to j0) removed | 45 | 1.53 |

then nothing more could go. Held out (seeds 50000-50039 x 2, the cuts applied to the 48-part netlists), the last cut
was a fluke of 12 seeds: 45 parts 1.22 [0.72, 1.66], surely below 46 parts (-0.61 [-1.13, -0.10]). So a cut "not
surely worse" on few seeds can still be worse: every pruned circuit is judged held out, cut by cut if need be.

**The divider wasn't needed.** With the PNP's base on u itself, u sags until the PNP's own base current balances ru's
leak (it settles near 2.57 V, the PNP feeding the hold about half a microamp): the threshold sets itself. `learn_avoid`
is now this 46-part circuit (`circuits.py`, `media/learn_avoid.svg`); removing two resistors changes each seed's
tolerance draws for the four parts after them, so it was judged afresh:

| held out | parts | efficiency [95%] | gain | poison | last third food:poison [95%] | stranded [95%] | power |
|---|---|---|---|---|---|---|---|
| learn_avoid, 48 (D8), 50000-50039 | 48 | 1.56 [1.36, 1.72] | 3.82 | 1.34 | 5.56 [5.03, 6.23] | 0 of 80 [0%, 4.6%] | 128 nW |
| learn_avoid, 46, 50000-50079 | 46 | **1.78** [1.62, 1.91] | **4.73** | 1.89 | 4.70 [4.27, 5.16] | **0 of 160** [0%, 2.3%] | 130 nW |

Paired on 50000-50039: efficiency +0.24 [+0.07, +0.38], gain +0.94 [+0.48, +1.33], **surely better on both**, the
job surely done (`results/learn_avoid_46_heldout.lives` and `.log`). It eats more of both: food 8.5 against 6.5, and
poison 1.9 against 1.3 (food:poison in the last third 4.7, still well above 3). Giving up sooner and harder, it
covers more ground.

**A stranding from a perfect body.** The pruning's own netlists stranded one life in 160 (seed 50010, red as poison):
from 52 s on, both thrusters fired equally (a giving-up run), the eyes saw nothing, and a replay of its firings through
the body showed why: its heading was 0.004 rad off the world's y axis and its spin exactly 0 (identical thrusters), so
on the torus the run retraced one column, which it had eaten clear, for 48 s (x drifting 48.1 to 47.2 mm). The world
spawns a block only when one is eaten, so the column stayed empty. A body whose thrusters differ, as any built one
would (D5; README: the body must vary), curves on a straight run. A second reason for varying bodies: an exactly
straight run is an artefact the circuits can be stranded by, and so could come to depend on.

## D10: where the circuit spends, against the best policy (2026-10-28)

The best learning policy (D8's ceiling grid: scan 16 per s, drive 40 per s for 0.2 s after a sighting, giving up
after 3 s at 20 per s, poison dropping the hold) is more efficient than `learn_avoid` (2.08 against 1.78 on seeds
50000-50039 x 2) but slower (gain 3.59 against 4.73). Both lived on those 80 lives, every tick recorded (the circuit's
firings replayed through the body give the same meals; a scratch analysis): what the eyes saw, each sensor's pulses,
the bit, each meal. Modes: *approach* (motor B fired in the last 0.1 s and the followed eye pulsed in the last 1 s),
*run* (B firing, nothing seen), *scan* (B idle).

| per life (100 s), means | circuit | policy | circuit, ct 1 nF (21 per s) | policy, scan = drive = 21 |
|---|---|---|---|---|
| firings per s: approach / run / scan | 27.0 / 20.5 / 28.5 | 23.1 / 5.2 / 8.2 | 12.0 / 11.1 / 8.1 | 15.6 / 6.7 / 9.1 |
| share of time: approach / run / scan | 29% / 19% / 52% | 35% / 13% / 52% | 33% / 28% / 40% | 39% / 17% / 45% |
| food in approach, per life | 78.2 | 57.1 | 28.3 | 42.5 |
| poison: approach / run / scan | 11.6 / 2.75 / 4.65 | 7.0 / 0.11 / 4.56 | 4.6 / 1.6 / 4.3 | 5.8 / 0.1 / 3.6 |
| food sightings per 10 s | 5.2 | 5.3 | 4.7 | 4.9 |
| a block in view: ms, pulses | 20, 0.56 | 62, 1.73 | 47, 1.47 | 46, 2.01 |
| bit right, flips, learned at | 96%, 3.8, 20 s | 94%, 1.2, 24 s | 90%, 2.6, 22 s | 91%, 1.1, 24 s |
| mm per s | 37 | 18 | 16 | 16 |

- **Learning isn't the gap**: both have the bit right about 95% of the time, learned by about 20 s.
- **Approaching isn't either**: the circuit's approaches yield as much food per firing as the policy's (0.029 against
  0.025 food a firing) and, at 54 pairs a second, more food per second: its higher gain.
- **Scanning is wasted**: one thruster at 54 per s spins it 2.7 turns a second, a block crossing its view in 20 ms
  and giving 0.56 pulses; at 16 per s, 62 ms and 1.7. Food is *sighted* equally often either way (5.2 per 10 s): a
  single thruster's firings trace the same 1.25 mm circle at any rate, so spinning faster re-sweeps the same view.
  20 firings per s, 0.4 meals per 10 s, buy nothing.
- **Running is costly and eats poison**: the giving-up run fires both thrusters at the scan's 54 per s (108 a second
  against the policy's 40), for 19% of the life, and runs into poison (2.75 a life against 0.1, each costing 2
  meals): a poison sighting empties the hold for a moment, but u is still low and the PNP refills the hold, so the
  run goes on. In the policy a poison sighting ends the run.
- **Why slowing the oscillator failed (D8)**: it slowed the approach too (the drive is the scan's beat), and its
  approaches then yielded a third of the food (28 against 78), with drive time without sightings up to 28%.

**Policies on the same lives, to rank the structures** (giving up 3 s, poison dropping the hold, learning toggle n 2):

| policy | efficiency | gain | poison |
|---|---|---|---|
| the circuit's speeds (scan, drive and run 54, hold 0.08 s) | 0.92 | 2.18 | 1.84 |
| ... scan 16 | **1.95** | 3.47 | 1.44 |
| scan 16, drive 54 for 0.15 s, run 20 | **2.29** | **4.11** | 1.21 |
| scan 16, drive 40 for 0.2 s, run 20 (the grid's best) | 2.08 | 3.59 | 1.17 |

A slow scan with a fast drive more than doubles the circuit-like policy, and the best mix beats the grid's best on
both measures. (The circuit itself beats its own-speed policy, 1.78 against 0.92: its hold, topped up by each pulse
and drained by each firing, approaches better than a timer; so the values won't transfer, D8, but the structure
should.)

**Suggestions, in order of expected worth** (spending: a firing 0.002 meals; the circuit spends 2.65 meals per 10 s,
1 resting, 1.52 firing, 0.13 its own power):

1. *Two speeds*: the oscillator slow (about 16-20 per s) while the hold is empty, fast while it is up; a switched
   resistor beside rt, its switch driven from h through a high resistance (so as not to drain the hold, as D8's rf
   did). Saves about 20 firings per s in scan: spending 2.65 to about 2.25, efficiency about 2.1 at the same gain,
   if the approach is unchanged. About 3-4 parts.
2. *Poison ends the run*: the silenced eye's current (at k) also lifts u, as a sighting does (an NPN on k pulling a
   PNP from the supply into u, about 3 parts). Removes most of the 2.75 poisons a life eaten in runs: gain about
   +0.5 per 10 s.
3. *A slower run*: the run at the slow speed rather than the fast (with 1, the PNP into h should not also speed the
   oscillator); about 15 firings per s less, but the policies don't say a slower run is better on its own.

Together, if each works as measured: spending about 1.95, gain about 5.2, efficiency about 2.7, above the policy
ceiling found so far on both measures.

## D11: D10's suggestions in bipolars, and why they fight the parts (2026-10-28)

Each tried on `learn_avoid` (scratch prototypes; training seeds 0-15 x 2, where `learn_avoid` scores efficiency 1.70,
gain 4.47, 750 firings per 10 s):

| change | parts | efficiency | gain | firings | why |
|---|---|---|---|---|---|
| the hold speeding the oscillator through a follower and rf | 48 | 0.0, -0.9 | | 460-520 | the oscillator stalls (below) |
| two speeds by capacitance: 1 nF switched in while the hold is empty | 52 | 1.74 | 3.91 | 551 | half works: the diode's drop leaves the capacitor coupled for only part of the swing (32-37 per s, not 18) |
| a second oscillator for the drive, from the hold; the scan suppressed while it runs | 56-58 | 0.4-1.2 | 0.9-2.3 | 365-590 | approaches too short: the drive oscillator drained the hold, or (through a follower) slowed as it sagged, and the half-way states of scan and drive overlapped |
| poison resets the giving-up timer | 49 | 1.41 | 3.42 | 639 | 9% stranded: in a poison patch every sighting resets it |
| **poison lifts the giving-up timer partly** (rpku 300 MOhm) | 50 | **2.01**, surely better | **5.29**, surely better | 744 | |

Held out (seeds 50000-50039 x 2) the last was tied with `learn_avoid` (efficiency 1.89 against 1.78, +0.09 [-0.04,
+0.23]; gain +0.26 [-0.12, +0.63]): not kept.

**Why the bipolar circuits resist two speeds.** At the nanoamps that keep power down, a 2N3904's gain collapses (its
base leakage, the model's ISE, takes most of the base current: about 400 falls to about 20 at 0.39 V). The oscillator's
regenerative pair then has too little loop gain: with too little timing current it settles half on instead of
snapping (a at 0.89 V, b at 0.21 V); with too much it latches. An astable multivibrator at these currents sat in its
DC state, both transistors half on. Every state in between (a hold half drained, a timer half sagged) leaves the
circuit in a half mode. Positive feedback, which makes decisions clean, needs gain the parts don't have at these
currents; complementary parts (CMOS) draw nothing at rest, so they can switch with gain to spare (the user's point).

## D12: the best policy in SKY130 CMOS (2026-10-28)

The user's decisions: parts readily realisable in SKY130 (its 1.8 V core MOSFETs, R, C, diodes, bias sources), for
the power merits of complementary designs and the clean decisions of positive feedback. `Netlist(chip=True)` and
`Netlist.M` (`life.py`); the eye's and taste's pulse 0.9 nA (`CHIP_EYE`), a motor input 0.1 pF.

**A copy of the best policy** (D10: scan 16, drive 40, hold 0.2 s, bored after 3 s, the bit toggled by two poisons
within 1.5 s; a scratch circuit, 126 parts, 116 of them MOSFETs): starved Schmitt triggers read each eye, OAI22 gates
pick food and poison by the bit, a hold and a boredom capacitor each read by a Schmitt, one oscillator with a slow and
a fast pair of starved current sources, a master-slave flip-flop of transmission gates for the bit. Every mode works
on the bench at 2.5 nW. Closed loop (seeds 0-7 x 2):

| version | efficiency | gain | food | last third | firings | power |
|---|---|---|---|---|---|---|
| first | 0.26 [-0.58, 1.06] | 0.39 | 3.1 | 5.6 | 245 | 10 nW |
| the doubt window widened (below) | 0.53 [0.02, 1.08] | 0.79 | 3.1 | 3.0 | 240 | 11 nW |
| `learn_avoid` (bipolar), same lives | | | about 8 | | about 750 | 130 nW |

Both surely worse than `learn_avoid` (gain -3.8, -3.4); power a twelfth of it. Replayed through the body (D10's
analysis): learning failed in 5 of 16 lives (seed 6 red ate 23 poisons, the bit never flipped), the approach succeeded
after half the food sightings (`learn_avoid` 0.86), and the first motor-B firing came 49 ms after a sighting (0).

- **The doubt window was a fraction of a second.** Two poisons flipped the bit only if the second came before the
  taste node recovered, under a second, where the policy's window is 1.5 s; widening it needs about 0.6 pA, below
  the chip's 1 pA. Each poison's charge is fixed by the interface, so it is copied four times over by a pMOS mirror
  into an 8 pF doubt node drained by a 40 um long leak: one poison never flips the bit, two up to 1.5 s apart do (seeds
  0 and 6, on the bench). Food no longer resets doubt.
- **A pMOS's current isn't proportional to its width** at these currents in SKY130 (W 1 to 8 um: 0.93 to 1.28 nA at
  the same gate voltage; the threshold moves with width): a mirror's gain is built from unit copies.
- **A width below the models' range doesn't simulate**: varied by the seed, a 0.42 um pMOS fell below the narrowest
  bin and ngspice refused it, three hours in. Widths are now floored at 0.36 um (nMOS), 0.42 um (pMOS).
- **BSIM4 runs on OpenMP threads**: 8 lives at once ran 17 times slower than one. One thread each (`life.py`) gives
  2.3 times, the laptop's cores sharing its power. A 100 s life alone takes about 5.5 min (3.3 s a second of life);
  the bipolar circuits about 15 s.
- **So design moves to the fast model** (the user's decision, AGENTS.md): blocks measured on the bench, given to the
  policy, the policy checked against the circuit's own lives, SPICE to verify and judge.

## D13: the fast model, and what the hand-design suggests (2026-10-28)

**The model** (`lab/cmodel.py`, to move into `discrete/`): the CMOS policy circuit as its blocks' measured
behaviour, each block a few lines, its numbers from short bench runs (`blocks.py`): eye 1.4 ms delay, 10 ms hold;
drive hold 63 ms after the last food pulse (the policy's: 0.2 s); boredom 2.7 s; scan 12.3, drive 44, run 12.6 per s;
doubt +1.12 V a poison, leaking 0.43 V/s, the bit flipping as doubt rises through about 1.5 V and re-arming only below
0.23 V (3.6 s after a flip, a third poison did nothing). On the same 16 lives as ngspice it is tied with the circuit
(efficiency -0.36 [-0.99, +0.37]; food 3.41 against 3.14, firings 238 against 240), a life in about a second
against 5.5 minutes. With motor B fired on each food pulse it was worse than the circuit (-0.65 [-1.11, -0.19]):
two firings close together count twice in the model, once in the circuit (a motor re-arms between them); both said
the option hurts.

What it showed in minutes (seeds 0-63, efficiency):

| change | efficiency |
|---|---|
| as built | 0.36 |
| drive hold 0.2 s (the policy's) | 1.05 |
| ... and doubt cleared by a flip | 1.72 |
| ... and by food tasted | 1.88 |
| ... but by food *seen* instead | -1.1: while the bit is wrong, "food" seen is poison, so doubt is wiped and it never flips |
| doubt's leak 0.3 V/s instead of 0.43 (no clearing) | about 0 |

A coordinate search (seeds 0-127): no clearing 1.91 (three poisons to flip); cleared by a flip 2.25, about the best
policy's 2.3. Both pushed boredom to the search's limit (8 s): the give-up as built barely helps.

**Doubt is a CUSUM** (the user asked, MacKay's way, whether it is Bayesian). Two hypotheses about the current bit, W
(wrong) and R (right), exhaustive, so one number carries the belief: the log-odds, to which each event adds its log
likelihood ratio. A poison adds log(lambda_W / lambda_R), a fixed step (the mirror's charge); food subtracts a large
step; silence drifts at the difference of the total event rates (a constant leak: the leak is a current, not an RC).
The floor at 0 V (doubt holds evidence against the bit, never confidence in it) makes it Page's CUSUM (1954), the
optimal detector of a change (Lorden 1971); the threshold is Wald's sequential test, a decision (false flips against
delay), not inference; the restart after the alarm is the reset on a flip; food's large step down, floored, is the
reset on food. All three of the model's improvements are the CUSUM's own rules; the trap (clearing on food seen) is
evidence with a likelihood ratio of about 1 taken as strong. Suggestive, not proven: leak / step should be (lambda_W -
lambda_R) / log(lambda_W / lambda_R); the circuit's 0.43 / 1.12 = 0.38 per s, the bipolar's measured poison rates
(0.18 per s right, 0.72 wrong) give 0.39, the CMOS circuit's own rates 0.17, the search chose 0.23 (with clearing on
a flip). Where it isn't Bayesian: evidence comes in bursts (the creature clears food around it, leaving poison; chance
clumps; an approach to food can sweep through a poison beside it), so two poisons close together mean less than two
independent ones; and the data depend on its own actions. Blocks are placed uniformly; food and poison may touch
(about 6% of food blocks touch a poison): kept so, the user's decision.

**But our world never changes in a life**, so the CUSUM's floor, right for a world that changes, throws away
confidence: after 50 meals two poisons flip the bit as at birth. A Bayesian here lets food build confidence (doubt
resting mid-supply, food pulling it down, poison up, bounded against bursts), so its learning rate falls as trust
grows. To test.

**Two variables per unit** (the user's thread). Belief needs one number (the log-odds); acting on it without
dithering adds one more bit of state, which way it last decided (hysteresis is a memory). The same in physics
(position needs momentum to carry the present to the future), excitable media (the sheet brain's ignition and supply;
FitzHugh-Nagumo's fast and slow variables), asynchronous cellular automata (a refractory state where a classic CA has
a global clock): a one-dimensional autonomous system can only settle; keeping time needs two (Poincare-Bendixson).
Every block of the CMOS circuit is that pair, a fast bistable (a Schmitt, the flip-flop) and a slow leaky integrator
(a capacitor and a starved current): Sepulchre's fast positive with slow negative feedback, reached from below. The
building block to design with is that pair; what differs from block to block is what feeds it and how fast it leaks.

**Time constants against delays.** A loop with delay that reacts faster than its delay oscillates, so each slow
variable must outlast the loop it closes: drive hold (about 0.2 s: the gaps in an approach), doubt's window (about
1.5 s: an approach into its taste), boredom (seconds: a search). The circuit's 63 ms hold, shorter than its gaps,
cost two thirds of its efficiency.

**How fast to learn is itself worth knowing** (the user's): the right timescale depends on evidence's noise, the
world's volatility, the loop's delay and how much is already known (a Bayesian's precision sets its learning rate:
the second variable is the learning rate). We set it now from outside (the search); whether the brain should learn it
depends on whether the best timescale differs from life to life in ways a unit can see locally (its input rates, its
reversals, the delay from its outputs to their consequences). A unit tuning its own time constant from its own
signals is self-optimisation without a god: the project's real goal.

**Stigmergy** (the user's): eating writes to the world (food cleared nearby), the eyes read it back, so the world holds
"been here". Poison *seen* with little food seen says "this patch is spent" (leave); poison *tasted* says "the bit is
wrong" (flip): two hypotheses with opposite remedies, told apart by the sense the poison comes through. Charnov's
marginal value theorem (1976): leave when the local rate falls below the habitat's; as circuit, two leaky integrators
of food seen, a fast and a slow, compared. D11's "poison seen lifts the give-up timer" was this, half done.

**Results overnight** (`lab/cmodel2.py`, `msearch2.py`: each variant searched on seeds 0-127 from the best
so far, then judged on 50000-50127, paired; nominal blocks, no tolerances yet):

| variant | efficiency held out | gain |
|---|---|---|
| A: doubt cleared by a flip and by food tasted | 2.15 [2.05, 2.25] | 3.63 |
| **B: confidence** (doubt down to -1.8 V, food -0.75 V, recovering at 0.04 V/s; a poison +1.12 V, threshold 0.8 V, leak 0.30 V/s) | **2.39 [2.30, 2.48]** | **4.05** |
| C: A, and each poison seen ages the boredom timer 0.14 s | 2.18 [2.09, 2.28] | 3.64 |
| D: A, leaving by a Charnov comparator (food seen fading over 2 s against 15 s; leave below 0.15 of it) | 2.20 [2.10, 2.29] | 3.69 |
| E: doubt cleared by a flip only | 2.12 [2.01, 2.22] | 3.58 |

**B is surely better than every other** (against A: efficiency +0.24 [+0.14, +0.36], gain +0.42 [+0.23, +0.61]);
the rest are tied with each other. So confidence pays, as predicted: at birth one poison flips the bit, after a run of
meals three are needed; the learning rate falls as trust grows. Two of B's settings sit at the search's limits (the
threshold at 0.8 V, trust at -1.8 V): it may go further. Leaving by stigmergy (C, D) gains nothing over boredom in
this model (both searches pushed boredom out, to 14 s in C); clearing on food adds nothing once a flip clears (A tied
with E). Not yet with tolerances or varied bodies.

**Judged robustly** (`lab/cmodel3.py`). The blocks benched in ngspice on 32 seeds (`blocks.py`), each
number's spread over the seeds' tolerances (sd of its log): eye hold 0.08, drive hold 0.14, boredom 0.21, scan and run
0.10, drive 0.07, doubt's step 0.05, its leak 0.17; doubt's lower threshold 0.23 V within 0.01 (the upper one, not
measured cleanly, taken as 0.02 V); assumed: a block redesigned keeps its relative spread. Each life then draws its
own blocks; with bodies, its own thrusters (each 0.5 to 2, `bodies.THRUSTERS`). Held out (50000-50127):

| variant | nominal | with tolerances | with tolerances and bodies |
|---|---|---|---|
| A | 2.15 | 1.06 [0.70, 1.37] | -0.27, 15% stranded |
| B (confidence) | 2.39 | **2.38 [2.29, 2.47]** | **0.32 [0.17, 0.49]**, 11% stranded |
| C | 2.18 | 1.03 | -0.09, 14% |
| D | 2.20 | 1.09 | -0.18, 13% |
| E | 2.12 | 0.99 | -0.31, 16% |

- **Every search but B's had exploited a knife-edge.** A, C, D and E set doubt's threshold at 1.79 V, a hair under its
  1.8 V ceiling (three poisons to flip); with tolerances 26% of lives drew it above the ceiling, so their bit could
  never flip. B's threshold, 0.8 V, is nowhere near: B is unmoved by tolerances, and surely better than A by +1.32
  [+0.97, +1.72]. The nominal model let the searches exploit it, "nor may the simulator"; the robust judge caught it.
- **Lopsided bodies defeat every fixed design**: B falls to 0.32, 11% of lives stranded, none does the job (B still
  surely best, +0.60 over A). A thruster at half strength makes the scan slow and the drive curve; a straight run
  becomes a circle. So the question of a brain adapting to its body is now the main one.

**Evidence is barely bursty** (`lab/bursts.py`, B in the fast model with tolerances, 256 lives): with the
bit right, poison is eaten at 0.094 per s; within 0.5, 1, 2, 5 s after a poison at 1.04, 1.11, 1.07, 0.99 times that;
after a food at 1.47, 1.33, 1.13, 0.97 times (blocks lying close together), but a meal has already stepped doubt
down. So poisons are close to independent evidence, and counting each as a full step is sound: the worry about bursts
(above) was small.

**Do the best timescales vary from life to life?** (`lab/timescales.py`: B with tolerances, bodies each
thruster 0.5-2 with the drive balanced by the oracle, seeds 0-127 x 2 grouped by strength, sqrt(left x right), into
thirds; efficiency):

| setting | weak | middling | strong |
|---|---|---|---|
| hold 0.1 / 0.2 / 0.4 s | 1.40 / **1.88** / 1.80 | 1.87 / **2.08** / 1.66 | **2.14** / 1.95 / 1.51 |
| drive 30 / 44 / 65 per s | 1.74 / 1.88 / **1.90** | 2.01 / **2.08** / 1.84 | **2.23** / 1.95 / 1.42 |
| boredom 3 / 6 / 12 s, scan 8 / 12 / 18 per s | flat within noise | | |

Yes, predictably: a strong body wants a slower drive and a shorter hold, a weak one the reverse (what matters is the
body's speed, rate x strength). But adapting them is worth about +0.1 overall (the oracle restoring every firing got
2.00 against balance alone's 1.92), against the balance's +1.6. Doubt in B has no timescale left to learn.

**The ladder's top rung: an omniscient brain** (`lab/omni.py`; QUESTIONS.md). Told every block's place, its
own pose and wiring and which colour is food, it steers to the nearest food whose straight path passes no poison
(turning with the thruster that turns it towards it, allowing for the spin to come; pushing with both while it points
there and goes slower than a cap). Held out (50000-50063 x 2, standard bodies): **efficiency about 20 [19, 22], gain
about 58, food 52-65 per 10 s**, against B's 2.4 and 6. Even so it strands 9-16% of lives (it circles a target it
can't turn tightly enough for): a lower bound. So these organs leave about ten times today's performance to a brain
that knows where things are; the mapping rung (legal inputs only) will say how much of that knowledge can be had.

**A short memory rung** (`lab/memo.py`: B's blocks with tolerances, told which colour is food and its own
heading, as perfect path integration would give; having lost sight of food it turns back to the heading where it last
saw it, within so many s, then drives; held out, 50000-50063 x 2): without memory 2.54 [2.40, 2.66]; with 0.5-4 s of
it about 2.0, worse. A first version was far worse (down to -2.0: it went back for food it had just eaten, ignoring
poison in view); cleared by any taste and by poison seen, still worse: turning back costs firings and time, and a
heading without a range rarely points at the block, lost because the creature moved past it. A memory pays only with
range too: the mapping rung. And a by-product: **told the colour from birth, B gets 2.54; learning it, 2.39** (the
same lives otherwise): learning costs it 0.15. The learning is near ideal; the headroom (to the omniscient 20) is all
in finding food.

**The seer rung, and what a map is worth** (`lab/seer.py`): told the exact place of each block the moment an
eye pulses for it (the nearest of that colour in the corridor), remembering it until eaten, told its pose and which
colour is food; steering (as omni.py) to the nearest remembered food with no remembered poison on its path, scanning
with one thruster when it knows none, and after 2 s of that running straight 0.5 s (without the run it ate what it
had seen and then scanned in place: 70% stranded). Held out (50000-50063 x 2): **efficiency 4.53 [4.34, 4.73], food
9.7 per 10 s**, 2% stranded. The ladder, every rung told the colour:

| rung | efficiency | food per 10 s |
|---|---|---|
| omniscient (knows every block) | about 20 | about 58 |
| seer (a perfect map of what it has seen) | 4.5 | 9.7 |
| B | 2.54 | 6.1 |

A perfect map of what it has seen would nearly double B: that is the most intelligence (remembering and placing
blocks) can buy behind these eyes. The rest, 4.5 to 20, isn't intelligence but coverage: an eye's corridor (2 mm
wide, 15 mm long) never sees most blocks. A first mapper inferring places from pulses (`lab/mapper.py`, an
evidence grid) failed (0.6 food per 10 s): scanning from one spot, an eye can't tell how far a block is, so every
cell of the corridor looks alike; it needs ranging by moving (parallax, the pulse rate as it nears).
Given the seer's exploring run and lower thresholds it still got only about 1 food per 10 s (16 seeds x 2), firing
about 900 times per 10 s: each pulse credited every cell along the corridor as strongly as if the block were in each,
so the map filled with false lines of food. A sound mapper needs a proper sensor model (one nearest block per
corridor, the evidence shared out along it): a substantial build, left open.
A second mapper with that sensor model (`lab/mapper2.py`: an occupancy grid; each tick, per eye, the chance
that the nearest block of its colour lies in each bin along the corridor, or none, weighed by the pulses' Poisson
likelihood; bins nearer than it emptied, it filled, those behind kept): judged cell by cell no cell passed 0.32 (the
evidence spreads over the corridor's width) and it ate blind; judged by a block's chance within a block's size, it
avoids poison well (food:poison 8 in the last third) but finds only 2.0-2.4 food per 10 s, firing about 800 times
(efficiency 0.45-0.65, 16 seeds x 2). Still a poor lower bound: a mapping brain that beats B is possible (the seer's
4.5), but building one is a robotics project of its own.

**Reversal: confidence, bounded, doesn't cost it** (`lab/reversal.py`; an experiment only, the task never
swaps): the poison colour swapped at 50 s, B against E (doubt floored at 0), tolerances, 50000-50127 x 2. Just after
(50-70 s) B eats food 4.87 and poison 2.16 per 10 s (ratio 2.3), E 4.10 and 2.88 (1.4); in the last 20 s B 6.04 and
1.00 (6.0), E 5.62 and 1.46 (3.9). B's trust is bounded (about two and a half meals' worth), so two or three poisons
undo it: the bound is the hedge a Bayesian makes against a world that might change. So B gets both: it keeps trust
where the world is steady and reverses when it isn't.

**Adapting to the body** (`lab/cmodel4.py`; held out, tolerances and bodies each thruster 0.5 to 2):

| brain | efficiency | stranded |
|---|---|---|
| B, fixed | 0.32 | 11% |
| the best fixed design for such bodies (searched on them) | 0.76 [0.65, 0.88] | 7% |
| B, the drive balanced for its body (told it: an oracle) | **1.92 [1.82, 2.02]** | 0% |
| B, every firing restored to the standard body's (oracle) | 2.00 [1.91, 2.09] | 0% |
| B on standard bodies | 2.38 | 0% |

Straightening the drive recovers nearly all of it: one number per life, the ratio of the two motors' drive rates (the
rest is physics: a weak body is slower). So the target for adapting is a single balance, worth up to +1.6.
- **Extremum seeking** (each approach nudged one way, alternately; its food pulses against their running mean move the
  balance the way its nudge went; all local to the drive): 0.15 to 0.53 on training seeds (0-63). It finds the right
  balance in about half the lives, in 40 to 60 s of a 100 s life; others never get there. Slow, because each
  approach's signal is weak and noisy.
- **A dead end: the time to re-find a lost block as the balance's sign.** I reasoned that a drive curving with the
  scan loses its block on the far side, found again late, and one curving against it on the near side, soon. Measured
  (balance set wrong on purpose by -0.6, 0, +0.6, 40 lives each): median re-find 0.75, 0.46, 0.47 s. It is shortest
  near the right balance, an extremum, not a gradient; used as a sign it made things worse (to 30% stranded).
- **Extremum seeking's settings searched** (step 0.02-0.05, nudge 0.15-0.35, averaging over 3 or 8 approaches):
  every one about 0.4-0.5; the signal, not the settings, limits it.
- **A dead end: system identification from the scan.** Scanning alternately with each motor, the world sweeping past
  should show each motor's turn. Sightings begun per firing came out reversed (a slow sweep breaks one block into
  several sightings, a fast one misses some); pulses per firing pointed the right way but compressed to 0.14 of the
  truth (residual sd 0.22: inverted, an error of 1.6), the forward motion each firing also gives drowning the turn.
  The alternating scan alone cost a little (-0.12 against 0.15: it re-covers ground).
- **Sweeping back the other way after a lost block** (a feedback, not a learned number): no help (about 0.0). The
  block isn't lost behind it: a lopsided drive circles past it. Straightening needs steering during the drive, and an
  eye's corridor gives no side.
- **A dead end: a zigzag within each approach** (the balance wobbling every 0.1-0.4 s, the food pulses in its two
  halves compared, lock-in style): no better than not adapting (-0.12 to 0.10, up to 26% stranded). A first try was
  biased (every approach began in the same half, its first moments rich in pulses: the balance ran to its limit on
  every body). The deeper reason: a block wholly inside an eye's corridor pulses the same wherever it lies in it, so a
  small wobble changes nothing the eye sees until the block leaves; the wobble only spoils approaches.
- **Given time, extremum seeking stalls** (`lab/longbody.py`: one body kept 300 s, each 100 s judged, seeds
  0-63 x 2): with small steps (0.01) 0.37, 0.81, 0.83; larger (0.03) 0.38, 0.45, 0.49; not adapting about 0.2; the
  oracle 1.9-2.1. Time doubles it, then it settles at less than half the oracle: its estimate never gets precise, each
  approach's signal too noisy. Weak in itself, not merely slow. A meal ending an approach added to its reward (as 5
  or 20 pulses): 0.49 and 0.11 against 0.37, within noise or worse.
- So far, on such bodies, the best brain is the fixed design searched on them (0.76 held out) or extremum seeking
  (about 0.5 in a life, 0.8 given three), against the oracle's 1.92. The eyes carry little about the balance's sign within an
  approach; open.


**The user's decisions** (2026-10-29): the body stays as it is (learning a lopsided body's balance likely takes more
than a 100 s life, and eyes that show which way it curves); no mapping brain now; robust judging and the log-uniform
thrusters confirmed; B's bench to be rerun four at a time.

**B in transistors, and the model's prediction, written before SPICE lives it** (2026-10-29). The circuit
(`lab/cmos.py`'s `pol` with mirror, counter, runfast; 151 parts): doubt a capacitor split between the rails
(13.8 pF), poison stepping it up through four unit pMOS copies of the taste pulse, food stepping it down through four
unit nMOS copies fed by a pMOS from the taste node (gate held at 1.1 V), no leak, the supply's rail the bound of
trust, the flip pulling it down until its Schmitt lets go; drive hold 16 pF, boredom 45 pF, the run on the fast
oscillator. Two of my own knife-edges found on the bench: the food pMOS's gate at 1.3 V left five seeds of 32 with a
food step of 0.18 V instead of 0.65 (the taste node reached its clamp first); at 1.1 V all are sound. The bench
first kept every node of every step (1.2 GB a run: eight at once ran the laptop out of memory); it now saves only
what it reads (240 MB). Benched on 32 seeds (`blocksB.py`): hold 0.176 s, boredom 6.04 s, scan 12.3, drive 50, run
43.6 per s, steps +0.656 V (poison) and -0.708 V (food), a drift towards trust of 0.020 V/s, threshold 1.476 V, reset
to 0.195 V, 3.7 nW; each with its spread. **The prediction** (`predict.py`, the fast model with those numbers and
spreads), on the seeds SPICE will live (50000-50031 x 2): **efficiency 2.03 [1.85, 2.21], gain 3.54, food 6.06,
poison 1.26 per 10 s, 366 firings per 10 s, 2% stranded**; the mean over 512 other lives 2.28 [2.21, 2.35]. The
method stands if SPICE ties with it, paired on those seeds (the interval of the difference including 0).

**It didn't.** Lived closed loop in ngspice on those seeds (`trypc.py`, 3 h 50 min with 8 at a time): efficiency
**1.65 [1.47, 1.84]**, gain 2.85, food 5.16, poison 1.15 per 10 s, 357 firings, none stranded, the job done; paired
against the prediction, efficiency -0.38 [-0.68, -0.08], gain -0.69 [-1.20, -0.20]: the model surely flatters it.
Poison (1.15 against 1.26) and firings (357 against 366) were as predicted, and food fell short by the same 15% in
each third (15.8, 18.2, 17.7 against 18.6, 21.0, 21.1 per life), so learning is as modelled and foraging isn't: some
block behaves differently in the closed loop than on the bench. (Life by life the two don't correlate, 0.06, as
expected: the model draws its own tolerances, not the seed's.)

*Tracing it.* Not the timers' response to sparse pulses: a lone eye pulse restarts the drive hold and boredom in full,
the same as a train (`bench_lone.py`, 8 seeds). Not the tolerances' spread: the 32 held-out seeds benched
(`benchH/`) and each lived in the model with its own numbers still gives 2.09 [1.91, 2.28], food 6.19
(`predseed.py`). So some closed-loop behaviour is missing from the model. Four lives traced in ngspice (`trace_life.py`:
each tick's mode, firings, sightings) against the model's of the same seeds (`trace_cmp.py`): the time in each mode,
the firing rates and the sightings agree, but the circuit's drives are shorter (0.229 s against 0.278) and more
frequent (10.7 against 9.2 per 10 s). The cause: **in the first tick of 55% of drives the second thruster fires alone**
(its excess over the first: 0.54-0.57 in the first tick, 0.00 ± 0.03 in every other). Motor A fires on each beat's
rising edge; motor B's gate (an AOI21: beat and DRIVE) opens the moment a food pulse starts a drive, and if the slow
oscillator's output is already high (about half its cycle) B fires at once, without A: a lone turn at the very moment
the block is sighted. The model drives with balanced pairs from the first beat.

*It accounts for the miss.* With that firing in the model (`cmodel4`'s `lone`: at a drive's start, not from a run,
B fires alone if the beat's phase is in the first 55% of its cycle), each seed with its own numbers gives 1.46
[1.31, 1.61], and ngspice ties with it: +0.19 [-0.04, +0.43] in efficiency, +0.27 [-0.14, +0.68] in gain; the drives
agree (0.244 s against 0.229, 10.3 against 10.7 per 10 s). Left over: during a drive the model fires 12% faster than
the circuit (97 against 86 per s). This is an explanation after the fact, not a prediction, so the method isn't yet
shown to stand. The lesson for benching: a block's numbers aren't enough, its **edges** (what happens at the moment
one block turns another on) must be benched too; the stray firing lived between blocks, in no block's numbers.

*A fix tried, and stopped.* Motor B latched to the beat (`cmos.pol`'s `edge`: DRIVE-or-RUN through a transmission
gate while the beat's output y is high, held by a weak keeper through the beat, B on nor(y, latched); 12 transistors,
0.4 nW more) only halved the stray firing (B alone in 23-38% of drives' first 10 ms, against 54-57%; four traced lives
ate 50 food against 45): B's first firing waited for the next beat, but A still missed it at times. Not chased
further. **The user's call (2026-10-29): the point of SPICE is to check we're close to something physically
realisable, not to match the model exactly.** B is: it does the job held out in SKY130 at 3.7 nW, at 80% of the
model's score, and the gap is understood. So the method stands as a lab: iterate design questions in the fast model;
check a design in SPICE (and retune it there) only when its physical realism matters. Parked: the drive's first beat
(`QUESTIONS.md`).

*Moved into the repository* (2026-10-29): the fast model, slimmed to B's blocks, as `discrete/model.py` (doubt in the
bench's volts; the failed variants of this entry stay in the scratch files named above, not kept), circuit B as
`cmos.py`'s `cmos_b` (the D12 variants dropped), its bench as `blocks.py`, its 32-seed bench as
`results/cmos_b_bench.json`; `test_model.py` checks the model lives the predicted lives (all 64 identical to the
scratch model's) and B is built part for part as benched and lived. One seed in 32 (23) still has a food step of
0.18 V against 0.70: the knife-edge of the food pMOS is rarer at vbf 1.1, not gone; the model's spread includes it.

The plan, in the model (seeds 0-127 to tune, held out from 50000 to judge), then the best in transistors, its blocks
benched, verified closed loop in ngspice and judged held out:
1. clearing on a flip and on food tasted, searched;
2. confidence (doubt below rest, food building trust) against the floor;
3. leaving by poison seen, and by a Charnov comparator, against boredom;
4. the best leak and threshold life by life and on bodies built differently: do they vary enough to learn?
5. bursts: poison's rate just after a food or a poison, the bit right, against its mean.

## D14: which level to think at (2026-10-29)

The user's plan (QUESTIONS.md): find the best level to think at, then, at that level, ask how a brain can know it
isn't doing a good job and compensate (tuning itself or recruiting). So: one architecture, B, rendered at three
levels, compared on its score, what it costs (parts, power), and what each level makes easy.

| level | built of | B |
|---|---|---|
| below Sepulchre | gates, Schmitt triggers, flip-flops, capacitors | `cmos.py`'s `cmos_b` (D13) |
| Sepulchre | leaky nodes, saturating elements, events from fast positive feedback and slow negative feedback | below |
| above Sepulchre | timers, oscillators, tallies as primitives | `model.py` (D13) |

**B at Sepulchre's level** (`lab/sepb.py`), in the minimal line's language (mixed_feedback's nodes and
elements) under its rules "mixed" (every node leaky but memory nodes, no clamps), lived by its simulator (noise,
mismatch), its parts and power as `chip.py` builds it in SKY130: 13 nodes, 20 elements. The eyes and taste leaky
nodes a pulse holds up for tens of ms; the bit a memory node with a node copying its negative; food and poison routed
by four elements reading the bit, each gated by one eye's pulse; hold and boredom leaky nodes (0.19 s, 3.7 s) read
at thresholds; drive-or-run a node either sets; the beat Sepulchre's relaxation oscillator (fast positive feedback,
slow negative at 0.25 s, a faster negative at 55 ms gated by drive-or-run), motor A the oscillator, motor B following
it through an element gated by drive-or-run; doubt a memory node written by taste through two sigmoids set well
away from rest; the flip a monostable (fast positive and slow negative feedback) that resets doubt to trust and
writes the bit against a slow copy of itself (master-slave).

Getting it to work took four fixes, each a lesson about the level: a tanh reading a node at its rest writes all the
time once mismatch shifts its offset (10% of a typical voltage), so a memory written by taste drifted: read events
through sigmoids set away from rest; a node counts a spike only after it falls below a typical voltage below zero, so
an oscillator that leaks back to zero never fires a motor; an oscillator whose "fast" node is slower than its "slow"
feedback settles at a fixed point instead (Sepulchre's condition: the resting point on the fast I-V curve's
negative slope); a taste node held up for 30 ms wrote doubt 1.2 V per poison.

Benched (`sepbench.py`, as `blocks.py` benches `cmos_b`): hold 0.17 s, boredom 5.8 s, scan 11.3, drive 44, run 44
beats per s, a poison's step 0.72 V (B's: 0.18 s, 6.0 s, 12.3, 50, 44, 0.66 V). Untuned, judged held out (50000-50031
x 2): with silicon's noise it does the job, efficiency 0.83 [0.64, 1.02], food 3.8, poison 1.2 per 10 s; with
biology's noise it eats as much poison as food (-0.85; twice biology's -1.56): its bit flips by itself (4 times in 30
s with no input at biology's noise, 150 at twice), the slow nodes (taste, eyes, hold) moving 0.14-0.27 V by noise,
enough to cross thresholds 0.3-0.6 V away. Built, it is **841 parts (638 transistors) and 29 nW**, against
`cmos_b`'s 151 and 3.7 nW. Rejecting noise costs power at this level: a node's noise falls with a larger capacitor
or a shorter time constant, both needing larger currents, and every element draws twice its gain from rail to rail
all the time, gated or not (`chip.static`). `cmos_b` never meets the problem: its signals swing rail to rail, and
real thermal noise is microvolts. So the levels are compared in silicon, where both would be built.

**Tuned** (`sepsearch.py`: minimal.search's CMA-ES on 17 of its numbers, by efficiency, silicon's noise, fresh seeds
each generation, 30 generations, 20 minutes): held out, **efficiency 2.06 [1.85, 2.27]**, gain 3.30, food 5.21,
poison 0.95 per 10 s, the job done, 31 nW, 841 parts; still failing with biology's noise (-0.90). Paired on the same
worlds: **tied with the block model's prediction for B** (+0.03 [-0.26, +0.35]), and better than `cmos_b` lived in
SPICE (+0.41 [+0.17, +0.67]), though that was never retuned in SPICE and keeps its drive-start quirk. The search
slowed the scan (tau 0.48 s), shortened the hold's leak and set doubt's threshold higher; its power didn't fall
(efficiency barely feels 30 nW against the creature's 1 uW).

**The three levels, for B:**

| | blocks (`model.py`) | Sepulchre (`sepb.py`) | gates (`cmos_b`) |
|---|---|---|---|
| efficiency, held out | 2.03 predicted (2.38 over more lives) | 2.06, its own simulator | 1.65 lived in SPICE (2.0 modelled) |
| parts / power | (none: numbers) | 841 (638 transistors) / 31 nW | **151 / 3.7 nW** |
| noise | each life's tolerances | silicon's yes, biology's no | none in SPICE (rail-to-rail swings) |
| an idea tried in | **a second a life** | about a second a life, an hour to build, 20 min to tune | minutes a life; a day to design (D12-D13) |
| knobs | every block's number | every element's gain, offset and time constant, each settable by another node (a gate) | widths and lengths fixed when built; bias voltages |

What it says:
- **Both lower levels realise the blocks faithfully**: the Sepulchre circuit, tuned, ties with the block model;
  the transistors reach 80% of it untuned, the gap one quirk where blocks meet (D13). So designing at the block level
  loses little, and ideas are tried there fastest.
- **For the same function in silicon, Sepulchre's level costs 8 times the power and 5.6 times the parts of gates.**
  Each of its elements is a biased amplifier drawing twice its gain all the time; a starved CMOS gate draws a
  nanoamp only as it switches. And its slow analogue nodes are easily moved by noise, where gates swing rail to rail.
- **What Sepulchre's level gives instead is knobs**: every gain, offset and time constant is a bias, settable by
  another node through a gate, so a slow loop inside the circuit can tune it. That is the next phase's question
  (tuning towards better outcomes), so the comparison on B, a design of decisions with almost no regulation, is
  biased towards gates (the user agreed, 2026-10-29: regulation means tuning towards outcomes, the next phase).
- What biology's noise costs at Sepulchre's level (2026-10-31): not reachable with B's knobs. The same CMA-ES (30
  generations of 16, fresh seeds each) judged by the worst of silicon's, biology's and twice biology's noise, from
  the hand-built start, never left a score of about -11.6 (each generation's best within noise of the first), while
  its step size grew: a flat landscape. Its final design is worse everywhere held out: silicon 0.63 [0.42, 0.83],
  biology -0.66 [-0.78, -0.53], biology x2 -0.48, 33 nW. Six of its 17 knobs ended on a bound, all towards slower
  and quieter (the scan's and drive's time constants at 0.8 s and 0.15 s, the eyes' resistance at 74 GOhm, near the
  chip's 77; doubt's threshold, the boredom level and the poison eye's gain at their limits): it wants filtering B's
  structure doesn't have. The knobs are gains, offsets and time constants of B's existing elements, not added
  capacitance or structure, so this says B as drawn can't be tuned into robustness; the minimal line's leaders,
  searched over structure too, survive biology at about 500 parts and 130 nW, so robustness can be built, not tuned
  (`lab/sepsearch.py`, `v/sep_search_silicon_biology_biologyx2.json`).
- Robustness built by size (2026-10-31): the silicon-tuned design with every node's capacitance and every current into
  it scaled by K (resistances by 1/K: the same dynamics, a node's noise down about sqrt(K), its power up K), the inputs
  (eyes, taste: the body's pulses are fixed charges) and boredom (already 50 pF, the limit) left alone. Held out:

  | scaled | silicon | biology | biology x2 | power |
  |---|---|---|---|---|
  | nothing (K 1) | 2.06, job | -0.90 | -1.53 | 31 nW |
  | all, K 4 | 1.92, job | **0.86 [0.49, 1.19], job** | -1.24 | 99 nW |
  | all, K 16 | 1.56, job | 0.84, job | -0.91 | 367 nW |
  | the bit's chain (bit, its copy, doubt, flip), K 4 | 2.04, job | **0.67 [0.24, 1.07], job** | -1.29 | 48 nW |
  | the bit's chain, K 16 | 1.97, job | 0.82, job | -1.09 | 113 nW |

  So biology's noise is survived by size, not by tuning, and mostly in one place: the bit flipping by itself. Four
  times the capacitance on the bit's chain alone does the job with biology's noise for 48 nW (half again B's), still
  841 parts (the minimal line's leaders: about 500 parts, 130 nW). Beyond K 4 biology gains nothing and silicon
  slowly loses; twice biology's noise fails at every size, so what remains is in the nodes not scaled, the inputs
  most likely (the taste node's noise stepping doubt, an eye's faking a sighting), which size can't fix: they need
  structure (a filter that waits for a pulse's whole charge). (`lab/sepscale.py`, `ONLY=` for a subset;
  `v/sepscale.log`, `v/sepscale_bit.log`.)
- Why twice biology's noise still fails (2026-10-31, `sepdiag.py`: the brain alone, no input, 60 s). The inputs:
  at twice biology's noise the taste node rests past doubt's step thresholds (+-0.3 V) 15% of the time (biology's 2%)
  and an eye past where its gates open 12% (biology's 0.1%); a taste pulse swings the node about 0.9 V, against
  noise of 0.29 V (biology's 0.15). Scaling an input node can't help (the body's pulse a fixed charge: the signal
  falls as 1/C, the noise as 1/sqrt(C)); a faster leak should (resting noise goes as the square root of the time
  constant, while a pulse that nearly fills the node keeps its peak). Tried by hand, the readers' gains raised to keep
  each pulse's effect (`sepfast.py`), bit's chain at K 4, held out: taste 4 times faster 1.95 / 0.85 / -1.30 (silicon
  / biology / x2), eyes 1.99 / 0.65 / -1.43, both **1.87 / 1.08 [0.62, 1.51] / -1.18**, 65 nW (8 times faster
  breaks a limit). Biology a little better, twice biology no nearer. A search of the same knobs with the inputs'
  leaks free, judged by the worst of the three (`sepsearch2.py`, 30 generations), was flat again and worse
  everywhere (0.77 / -0.16 / -0.73): with one noise hopeless the worst-case gives no slope. One seed (3) is
  pathological at biology's noise: its flip's monostable fires again and again with doubt low (untraced).
  The likely cause is B's structure: doubt is a thresholded tally, so each noise excursion past a threshold is a
  step, and steps random-walk to the flip; the minimal line's hold-and-roam circuits, which survive twice biology
  (README), keep the bit on a perfect integrator written by a three-factor rule (seen times taste), where noise
  averages out unless it coincides with a sighting.

## D15: can a brain tune its own spending? (2026-10-29)

Phase 2 of the plan (QUESTIONS.md), at the block level (the user's choice, D14): a brain that notices it isn't doing
well and compensates, tuning towards better outcomes (never a setpoint, AGENTS.md). Testbed: B's five spending knobs
(hold, boredom, scan, drive and run rates) drawn at birth up to 3 times off its searched values (log-uniform, each
life its own), against the floor (fixed there) and the ceiling (B's values, fixed), on the same lives, robustly judged
(`lab/selftune.py`; 16 held-out seeds x 2).

**The tuner**: simultaneous perturbation (SPSA; node perturbation, as in Fiete and Seung's birdsong model, 2006).
Each epoch, every knob nudges itself by its own random sign for one half and the other way for the other half; the
brain's efficiency in each half (food - 2 poison, against resting and its own firings, all counted from taste and its
own motors) moves each knob along its own nudge by their difference. Each knob knows only its own sign, its own
setting and one broadcast outcome, and the outcome only taste and the brain's own firings (one imperfect timer
serves both halves, so its error cancels). **Not local in one way** (the user asked, 2026-10-29): a shared epoch
clock switches every knob's halves in lockstep, and a central accountant holds the first half's tally, divides and
compares: a controller over the knobs. A broadcast outcome is plausible (as dopamine); a brain-wide metronome for
every unit's experiment is not. The coordinator-free form, continuous-time node perturbation (Fiete and Seung):
each knob wiggles at its own random moments, one leaky integrator turns taste and firings into an outcome rate, its
difference from its own slower average is broadcast, and each knob correlates it with its own recent wiggle through
a trace of its own. And a block model in Python, not a circuit: in one, each knob a memory node setting a block's
bias.

| tuner | life | efficiency | against the floor (paired) |
|---|---|---|---|
| ceiling (B, fixed) | 2,000 s | 2.52 [2.45, 2.59] | |
| floor (mistuned, fixed) | 2,000 s | 1.74 [1.51, 1.97] | |
| meals, nudges 15%, epochs 40 s | 2,000 s | 1.72 [1.51, 1.93] | none |
| + food sightings 0.02 of a meal each | 2,000 s | 1.67 | none |
| + nudges 30% | 2,000 s | 1.86 [1.73, 2.00] | |
| meals, nudges 30%, epochs 80 s | 2,000 s | 1.73 | none |
| sightings 0.02, nudges 30% | **10,000 s** | **1.93 [1.87, 1.99]** (last third 1.95) | **+0.18 [+0.03, +0.32]**; gain tied |

Why so weak: **the landscape is flat near B and steep only far from it** (`landscape.py`, each knob alone scaled,
64 lives): within about x0.7 to x1.4 no knob moves efficiency by more than 0.2; beyond x2 hold, scan and drive cost
0.3 to 1.2; the run rate barely matters anywhere, and boredom is flat but for x1/3. So a nudge has signal only where
a knob is badly off, and there a 30% nudge separates the halves by about 0.36 of efficiency against noise of about
40% (some 12 meals in a 20 s half); five knobs nudging at once add each other's effects to every knob's noise. A
life of 2,000 s holds about 1,200 meals; telling a few per cent apart takes about 1,000 meals per comparison. Given
10,000 s, knobs starting beyond x2 come about halfway back (hold 0.93 to 0.53 in the log, drive 0.95 to 0.54, run
0.90 to 0.46; boredom least, 0.87 to 0.71), and lives' spread narrows (the bad lives rescued); it saves by firing
less (298 firings per 10 s against 405) rather than eating more.

So **knowing it isn't doing well is possible from outcomes alone, but slowly**: a quarter of the gap closed in
10,000 s. The limit is the signal (sparse meals, flat near the optimum), as for the body (D13), not the mechanism.

**A yardstick: the best use of the brain's information** (the user, 2026-10-29: what does "perfect" look like, given
how sparse the feedback is?). Not the ceiling (told the best setting from birth) but the best a learner could do
with only what the brain senses (meals, food sightings, its own firings) and unlimited computation: a Bayesian
optimiser inside the life (`lab/bo2.py`: each 40 s window one setting of the knobs, its efficiency recorded;
a Gaussian process over the knobs, a length scale per knob and the noise fitted from the life's own windows; the next
setting by Thompson sampling, so it explores while unsure and settles as it learns). Godlike in computation, never in
information, and never a brain. Run on the standard body (spending only) and on lopsided bodies (thrusters 0.5-2,
the drive's balance a sixth knob, starting level; the ceiling told its balance, as D13's oracle), against floor and
ceiling on the same lives; 32 held-out seeds x 2, lives of 10,000 s. Efficiency over the whole life (what learning
costs counts), and the last third's gain rate (food less 2 poison per 10 s: where learning ended up), paired:

| body | arm | efficiency | against the floor | last third's gain | against the floor |
|---|---|---|---|---|---|
| standard | floor (mistuned, fixed) | 1.74 [1.58, 1.91] | | 3.16 | |
| standard | local tuner (sightings 0.02, nudges 30%) | **1.90 [1.86, 1.95]** | **+0.17 [+0.04, +0.28]** | 3.06 | -0.10 [-0.35, +0.15] |
| standard | yardstick | 1.61 [1.55, 1.68] | -0.13 [-0.27, +0.01] | 2.66 | -0.50 [-0.78, -0.22] |
| standard | ceiling (B, fixed) | 2.47 [2.39, 2.53] | | 4.21 | +1.05 [+0.79, +1.32] |
| lopsided | floor | 0.19 [0.06, 0.35] (58% stranded) | | 0.49 | |
| lopsided | local tuner (+ a balance knob) | 0.66 [0.55, 0.77] (3% stranded) | +0.48 [+0.34, +0.60] | 1.32 | +0.83 [+0.45, +1.19] |
| lopsided | yardstick | **0.92 [0.85, 0.99]** | **+0.73 [+0.61, +0.84]** | 2.05 | +1.56 [+1.20, +1.90] |
| lopsided | ceiling (told its balance) | 1.94 [1.82, 2.06] | | 3.41 | +2.92 [+2.53, +3.28] |

**The yardstick is no yardstick on the standard body: the local tuner beats it** (+0.30 [+0.21, +0.37] in
efficiency, +0.47 in gain). It never converges: its settings stay a median of about twice off B in every knob in
every third of the life, and almost no window (0.3%) has all five within x1.5. With some 12 meals in a window and
the landscape flat within x1.4 of B (above), 250 windows can't locate an optimum in five dimensions, so it keeps
paying to explore settings far off. Its window (20 s, 80 s) and the sightings' weight (0) change nothing surely.
On lopsided bodies, where the floor is a catastrophe, wandering pays: it closes about 40% of the gap from floor to
ceiling in efficiency and half in the last third's gain.

On lopsided bodies the local tuner, given the balance as a sixth knob, rescues the stranded lives too but reaches
only two thirds of the yardstick's gain (-0.25 [-0.36, -0.14] in efficiency). The difference is the balance: the
yardstick finds each body's almost exactly (its last third's setting against the true balance: correlation 0.98,
slope 0.93), the local tuner moves it only a quarter of the way (0.27; median error 0.29 in the log from 0.38). The
balance is steep, a strong signal, so there the local tuner is limited by its step, not by information; it moves
every knob at one rate, set for the flat spending knobs.

**Without a coordinator** (`discrete/tuner.py`, checked by `test_model.py`; continuous-time node perturbation, Fiete
and Seung): each knob wiggles at its own random moments (on average every 20 s, by up to +-0.3 in the log); one
outcome node, a leaky efficiency rate (gain over spending, each a leaky tally, 20 s), and its own slower average (200
s); the difference broadcast; each knob keeps a trace of its own wiggle (20 s) and moves by rate x broadcast x trace.
No epochs, no shared clock, no accountant; every quantity a node. Same lives (paired):

| body | tuner | efficiency | against the floor | against the epoch tuner |
|---|---|---|---|---|
| standard | rate 0.03 | 1.56 [1.47, 1.65] | -0.18 [-0.32, -0.02] | -0.34 |
| standard | **rate 0.01** | **1.98 [1.89, 2.08]** | **+0.24 [+0.15, +0.34]** | +0.08 [-0.01, +0.16], tied |
| standard | rate 0.03, annealed (wiggles 4 times as wild at birth, calming over 2,000 s) | 1.50 | -0.24 | -0.40 |
| lopsided | rate 0.03 | 0.45 | +0.26 | -0.22 |
| lopsided | **rate 0.01** | **0.90 [0.69, 1.10]** | **+0.71 [+0.56, +0.86]** | **+0.24 [+0.12, +0.35]**; the yardstick's 0.92 tied (-0.01 [-0.17, +0.14]) |
| lopsided | rate 0.03, annealed | 0.33 | +0.14 | -0.33 |

So the coordinator was never needed: the local form ties the epoch tuner on the standard body (a third of the gap
from floor to ceiling closed) and beats it on lopsided bodies, where it ties the Bayesian optimiser. **Annealing
hurts**, as the optimiser's exploring did: wild tries cost more than they find when meals are sparse. Too fast a rate
(0.03) is worse than none, its knobs chasing noise; slower ones (0.005, 0.003) tie 0.01 on the standard body
(-0.02, -0.07) and fall behind on lopsided bodies (-0.08 [-0.14, -0.02], -0.19), so 0.01, broadly. **A fault, mended** (the user's
question, 2026-10-30): the rate was chosen on the held-out seeds it was then judged on. Chosen again on training
seeds 0-31: on the standard body 0.003 to 0.01 tie (1.98, 2.02, 1.95; 0.02 1.78; fixed 1.85), on lopsided bodies
0.01 is best (0.79; 0.003 0.67, 0.005 0.73, 0.02 0.67; fixed 0.16): 0.01 again, so the held-out scores stand. A rate
fixed for every individual, suited to the kind of world, is evolution's knowledge like B's other numbers, and
legitimate; set per individual from its body it would not be (AGENTS.md). Whether one fixed rate survives a world
with sparser signals is open (QUESTIONS.md). Knobs end nearer B than the epoch tuner's (median log error
falling about a third; the scan least), and the balance's median error from 0.38 to 0.14, though its fit to the
true balances is loose (correlation 0.31).

**Each knob its own rate** (the user's layers, 2026-10-30: how fast to turn the knobs is itself to be learned;
`discrete/tuner.py`, meta=1): delta-bar-delta (Jacobs 1988; Sutton's IDBD 1992), each knob's log-rate rising while
its step agrees with its own memory of its steps, falling while it disagrees, within x10 of 0.01. Compared with its
fresh memory, every rate climbed to the ceiling and the knobs chased noise (standard 0.91 to 1.15, -0.83 to -1.08
against one rate; lopsided 0.15, -0.75): the steps come from slow signals (a 20 s trace, a slower outcome), so a step
agrees with its own recent past even in noise. Compared with its memory as it was 100 s ago, beyond that
correlation, the rates stay near 0.01 (the balance's drifting slower, not faster) and gain nothing: standard 1.95,
tied (-0.04 [-0.10, +0.03]); lopsided 0.82, -0.08 [-0.15, -0.02] (meta-rate 0.0005; 0.002 worse, -0.18 and -0.16).
There was no headroom to find: 0.003 to 0.01 tie on the standard body, and the balance made faster by hand loses
(x3: 0.57, -0.34 [-0.46, -0.21]; x10: 0.21, -0.70).

**Shadows that compete** (the user's idea, 2026-10-29; `lab/shadow.py`): sixteen copies of the hold (0.03
to 1.5 s), each judged counterfactually from every drive without driving, its meals kept less the drive's extra
firings at the brain's own price of energy; the hold used the best shadow's (winner takes all), on a random fifth of
drives twice that, so longer shadows are judged too. **A dead end**: 1.28 against the floor's 1.74 (-0.46 [-0.56,
-0.36]), the hold driven to a median of 8.6 times B's. Each way of replaying a drive was biased, and the last bias
can't be removed:
- judged per gap between sightings, short holds won (0.05 s): the sightings after a gap came only because the drive
  went on, so a short hold seemed to keep meals it would have lost;
- judged per drive, a shadow's drive ending at the first gap it wouldn't bridge, long shadows judged also on drives
  poison ended won 1.5 s: a sample that leaves out the drives where a long hold wastes its firings; judged only on
  drives whose hold was drawn before the drive, still long, because a shorter hold is charged with every meal after
  losing the block, when in truth the creature scans and often finds it again; what it would have seen scanning was
  never seen.
So off-policy judging works only for a choice whose alternative leaves what is seen unchanged; hold and boredom both
change it. On the same lives, the hold alone restored to B's is worth +0.17 [+0.08, +0.27]; the coordinator-free
tuner on the hold alone recovers about half of that (+0.09 [+0.01, +0.17]).

So **within a life, perfect is local**: from a life's own sparse outcomes even unlimited computation can't search
the space globally; small careful steps from a decent start do better. The global search belongs to evolution
(searching designs across lives, as this project's searches do), a life's own tuning only to polish, and to rescue
it where something is badly wrong (a lopsided body). This yardstick is a lower bound on "perfect", not an upper one:
an optimiser that explored less would score higher, and the ceiling stays the only true upper bound. Shadows that compete were a dead end (above).

In a world with sparser meals (2026-10-31; QUESTIONS step 2's open: does one fixed rate survive?). Six blocks of
each colour instead of 18 (`world.BLOCKS`, patched for the experiment, `lab/sparse.py`), standard body,
mistuned at birth, 10,000 s, seeds 0-31: food falls to about 1.4 per 10 s and efficiency to 0.29 for the floor; B's
own knobs, untuned, get 0.45, so there is at least 0.16 to gain (B's knobs were chosen for the dense world, so the
true ceiling is higher). The tuner barely moves: rates 0.003 and 0.01 both 0.32 (+0.02 [-0.01, +0.06] over the
floor, tied with each other), 0.03 0.27 (below 0.01, -0.05 [-0.09, -0.00]). So the rate's order holds (0.01 or
slower; 0.03 chases noise), but no rate recovers much: with meals four times sparser, a 20 s wiggle judged on a 20 s
outcome tally holds almost no signal. What fails is the signal, not the rate: a tuner for a sparse world would need
outcome windows scaled to the meals' spacing (which would itself have to be learned), or a proxy available every
moment, as D19 and D20 use for the balance. Windows scaled by hand don't rescue it: wiggles, outcome tally and its
average all 3 times slower (60, 60, 600 s), rate 0.01: 0.34, the first sure gain over the floor (+0.05 [+0.00,
+0.09]) but tied with the 20 s windows (+0.02 [-0.01, +0.06]); 6 times slower 0.30; 3 times slower at rate 0.003,
0.31. A longer window holds more meals but leaves fewer trials in a life (some 170 of 60 s for five knobs in 10,000
s), so the information a life holds, not how it is windowed, is what runs out. In a sparse world, judged by meals
alone, a life can't tune its spending; it needs a proxy seen every moment. Food sightings, the obvious one (far more
frequent than meals), don't serve: weighted 0, 0.1 or 0.3 in the outcome (0.02 normally), 0.31, 0.31 and 0.27, the
heaviest below the usual weight (-0.05 [-0.08, -0.01]): a sighting rewards looking at food, which the knobs can buy
without eating it (a long hold on a block it doesn't reach). Unlike the balance (D19, D20), spending has no proxy that
tracks meals closely; found here, none.

## D16: can a brain learn tricks nobody designed? (2026-10-30)

Phase 3 of the plan (QUESTIONS.md; the user's idea, 2026-10-29): beside B (fixed, its own tolerances), a reservoir
of 200 random sequence detectors over the brain's own events (`lab/trick.py`): each fires when its event b
(an eye, or a motor's beat) comes its own delay (up to 1 s) after its event a, within 50 ms, and may then add a beat
to its own motor, with probability 0.01 + w, w its memory node. Each keeps a fading tag (2 s) of whether it acted
against its odds (+(1 - p) if it did, -p if not, so the tag averages zero whatever the meals: REINFORCE); taste
credits every tag (food +1, poison -2, rate 0.01), and each extra beat is charged its cost at once. Three-factor
learning on a random reservoir (Izhikevich 2007; Fremaux and Gerstner 2016). The trick hoped for: steering a lopsided
body. 32 held-out seeds x 2, lives of 10,000 s, paired:

| body | brain | efficiency | stranded | against plain B |
|---|---|---|---|---|
| lopsided | plain B | 0.29 [0.11, 0.50] | 61% | |
| lopsided | detectors, learning off | -0.12 [-0.35, 0.11] | 0% | -0.41 [-0.56, -0.27] |
| lopsided | **detectors, learning** | **0.59 [0.36, 0.83]** | 14% | **+0.30 [+0.16, +0.44]**; +0.71 [+0.55, +0.88] over learning off |
| standard | plain B | 2.47 [2.39, 2.53] | 0% | |
| standard | detectors, learning | 2.21 [2.07, 2.33] | 0% | -0.26 [-0.37, -0.16] |

Learning is real, but **no steering was learned**: detectors that grew beat the weaker thruster's motor half the
time (51% of 582), and those that survived are mostly keyed to the eyes (rare, so cheap); two thirds died. The
random beats alone unstrand a lopsided creature but spoil its choices (food:poison in the last third 1.9);
learning prunes the harmful ones and keeps most of the rescue. On the standard body nothing needs rescuing, and
exploring is pure cost. Below the coordinator-free tuner with a balance knob (0.90): a designed knob beats an
undesigned trick here, as expected, since a random detector has to be lucky to be the right correction, and its
credit comes only through sparse meals, a thousand of them per life.

### D16, continued: can meals credit a trick at all? (2026-10-31 to 11-01)

D16 asked a random reservoir to find steering and it didn't. Taken apart (`lab/trick2.py`, a `Trick2` over
D16's detectors; runs `lab/night1.sh` to `night13.sh`, logs `lab/v/night*.log`): lopsided bodies,
training seeds 0-15 x 2, lives of 10,000 s unless said. A **planted** detector is the right steer by hand (a beat of
motor 1, then another 2 later: add a beat to the weaker thruster's motor), its **wrong twin** the same to the stronger.

| stage | what | result |
|---|---|---|
| 1 | credit by taste, or by **sight** (each tick, the food eye's pulse less its running mean, 200 s) | plain B 0.14 (69% stranded; food per 1000 s falls 134 to 71 over the life); D16's trick 0.14; sight 0.003-0.1: -0.08 to 0.17, more food but food:poison 2-3. 55-63% of grown detectors on the weak motor: no steering |
| 2 | the planted pair, D16's per-beat REINFORCE | no credit separates right from wrong: each beat's charge, immediate, drives both to zero odds |
| 3 | does the trick exist? fixed odds, learning off, 2000 s | right steer at 0.9: **0.66 [0.24, 1.09], job done**; wrong 0.09; plain B 0.13 |
| 4-5 | **one coin per burst** (a burst begins after 0.3 s without firing, capped at 2 s; uncapped, one endless burst through B's run stuck the coin), the planted pair alone, start 0.5 | learning off -0.06; taste **0.67 [0.34, 1.00], job done**; taste and sight 0.69 (right above wrong in 81%); sight alone 0.58 (84%); food rises over the life |
| 6 | burst coins on random reservoirs | 20 detectors about B (0.05); 50: -0.65; 200: -0.84, 160 grown, ~1800 extra beats per 10 s, food:poison 1.05: sight credit gamed |
| 7 | each beat charged its cost | planted pair 0.65; 20 random 0.17; 200 still -0.83: a floor at w >= 0 (start at the minimum odds) reflects noise upward, a ratchet |
| 8 | forgetting (w fading) | erases the planted signal (0.30); a low start floods (-0.95) |
| 9 | explore only in 10% of bursts (tagged, even coin), else act at the learned odds | planted pair 0.39, job done; the planted among 50: -0.41 to -0.84, the floor (w >= -start) ratcheting again |
| 10 | and act only on clear evidence (w over the root of its summed squared steps above 3), w free | planted pair 0.28; 50: -0.13 to -0.24, ~12 grown, the charge dragging w below 0 |
| 11 | poison worth 4 or 8, charge x0.5 or x2 | all about -0.23, food:poison 1.6 against B's 4: exploring a beat keyed to an eye spoils B's colour choices, and explorers at once confound each other's credit |
| 12 | lives of 100,000 s judged on the last 10,000, exploring 1% of bursts | plain B 0.11 (88% stranded, food per 10,000 s 845 to 417); planted pair 0.10 (right w +0.93, above wrong in 88%); planted among 50 0.02 (right +0.88, 84%), the same not learning 0.02, 50 random 0.03; food:poison about 2.3 against 6 |
| 13 | the fixed right steer (odds 0.9, learning off) in those lives | **0.68 [0.30, 1.07], job done** (per beat 0.68 [0.28, 1.08]); the wrong twin 0.04. So stage 12's learner learned the steer but hardly acted on it (7 extra beats per 10 s against 97): its evidence gate compared w (at most 1) with the root of every step it had ever taken, growing without end, so the gate shut. A flaw of the scheme, not a finding |
| 14 | stage 12 with the gate's evidence fading (over 10,000 s) | planted pair **0.70 [0.40, 1.00]**, as good as the fixed steer (right w +0.88, above wrong in 91%; wrong -0.83); planted among 50 0.30 [-0.02, 0.61] (right w -0.37 on average, above wrong in 72%); 50 random 0.24 [-0.07, 0.54], 15 grown, 64% of them on the weak motor: some steering found, against stage 12's plain B 0.11 on the same seeds (not paired). Food 3.3 per 10 s, but food:poison 2.3 against B's 6: the exploring still spoils B's choices |

So: **the trick exists and pays** (stage 3); **meals can credit it, but only if exploring runs at the timescale
the outcome reveals**: one coin per burst of beats, not per beat (stage 5; Fiete and Seung 2006, the songbird's
perturbation by bursts). **Among random candidates every scheme failed**, and the causes compound with their
number: exploring grows with candidates; any floor on w ratchets credit noise upward; candidates exploring at once
take each other's credit; exploring a beat keyed to an eye spoils the colour choice B makes; sight credit is gamed
by moving more. Even with the right detector learned among 50 (stage 12), the learned odds earn nothing over the
same detectors not learning: the exploring of the other 49 costs what the right one gains. Credit from outcomes
scales badly with candidates: with the gate mended (stage 14), 50 random detectors find some steering (64% of
those grown on the weak motor) and roughly double B's score in long lives, but stay far below the planted steer
alone (0.24 against 0.70), poisoned choices the price of their exploring. So structure has to come from somewhere
cheaper: prediction (phase 5) or growth aimed
where the brain is frustrated (phase 4, D17), not a random reservoir.

## D17: recruitment, case 1: taste wired to nothing (2026-10-30)

The plan's step 4 (QUESTIONS.md; the user: how can a brain realise it isn't solving the problem and recruit more
neurons?), at the block level. The unwired brain is B without its learning: either eye starts a drive, taste goes
nowhere (`lab/grow.py`). Beside it, per eye, a generic grower: **predict** (a fading tag of the eye's pulses,
1 s; at each taste the eye's prediction moves towards it by its tag); **notice the gap** (frustration: a leaky count,
50 s, of poisons tasted while the eye was tagged and predicted bad); **grow** (frustration past 2 grows a recruit on
that eye's pathway, the declared primitive); **experiment** (the recruit knows nothing of the circuit: it tries the
generic operations on its pathway, block and reverse, the eye then ending a drive, 20 s each, judging each by the
taste that follows its own eye, against the pathway as it was, judged by the same running rate before it grew;
win-stay lose-shift). Lives of 100 s, 32 held-out seeds x 2, robust:

| brain | efficiency | last third food:poison | |
|---|---|---|---|
| unwired | -3.35 | 1.00 | eats both colours alike |
| **grower** | **1.43 [1.21, 1.65]** | 4.31 | grew in 64 of 64 lives, always on the poison eye, the food eye kept; in all-food lives, 0 of 64 |
| B (designed learning) | 2.01 [1.83, 2.20] | 5.27 | |

It grows early (a median 7 s into the life) and in the right place every time, and never without cause. It is
-0.58 [-0.86, -0.30] behind B. Its first version re-tested the pathway as it was for 20 s before trying anything
(0.20); judging that from what had already followed the eye mended it. What remains: the recruit settles on block
in 61 lives, reverse in 3; both make the taste after the poison eye vanish, so its own judge can't tell them apart,
but reverse (B's way: the poison eye ends a drive, turning away) also avoids poison bumped into, which only the
whole outcome shows. The menu of operations (drive, block, reverse) is generic for a pathway, but it holds B's
answer; whether a grower finds what no menu holds is case 2's question.

**Mended: try everything once.** Judging by the whole outcome (all taste, the broadcast) changed nothing (1.44,
+0.01): the recruit never tried reverse, since block already beat the pathway as it was and it stayed. Trying every
operation once before keeping the best: **1.80 [1.63, 1.96], tied with B** (-0.21 [-0.50, +0.07]; +0.37 [+0.19,
+0.55] over win-stay), reverse kept in 40 lives and block in 24, and still grown in every poison life and no all-food
life. With the whole-outcome judge as well, 1.73 (tied with the eye's own judge, +0.07 [-0.03, +0.17] for the eye's).
So the judge's reach mattered less than exploring before settling: a recruit has to see every option before win-stay.

**A lopsided body: not a recruitment case** (the user, 2026-10-30: a case must be one no tuning of the brain's
parts can solve; one more knob, a gain per motor, solves this one, D15). Tried anyway (`lab/grow2.py`). B with D16's detectors grown only where the gap is:
frustration, a leaky count of drives that end with the block lost, grows batches of detectors over the events of
driving (the food eye, the motors' beats); a lost drive is also credited as a bad outcome through the tags, as taste
is. 8 seeds x 2, 2,000 s, lopsided bodies: all 200 grown at once (drives fail constantly on such a body), 130 extra
beats per 10 s, 0.30 against D16's random detectors' 0.65; with 40 and less exploration 0.96, B alone 0.79, all
within noise; the lost-drive teacher changes nothing (0.97 without). No steering was learned. The building block is
wrong for the job: a detector adds single beats, while steering a lopsided body means changing one motor's rate by
1.5 to 2 times on every drive, hundreds of coordinated beats, each credited only through rare outcomes. The eyes say only how much of a
colour is in view, not where, so prediction can't read a veer's direction either.

**A world that frustrates: guarded food** (the user's idea, 2026-10-30; `lab/guarded.py`). Still a random
world, one statistic changed: each food block has a poison guard beside it (2.5 mm from its centre, at a random
angle), the pair kept together. The rays stop at the first block, so the food hides behind its guard from one side.
100 s lives, 32 held-out seeds x 2:

| brain | plain world | guarded (2.5 mm) |
|---|---|---|
| B | 2.01 | 1.06 (2.1 mm: 0.46; 4 mm: 2.07, no effect) |
| B told the colour, learning off | 2.54 | 1.38 |
| B's knobs searched in the guarded world (200 random settings, learning steps too; best of 5 held out) | | 1.08 |

Tuning can't recover it (B's own values are as good as any found). The loss is mostly driving (told the colour, B
loses as much), and more from learning: guards eaten while chasing food add doubt, flipping the bit 3.1 times a life
against 1.7. But no extra structure has recovered it either: a scripted detour (poison seen just after food: swing
away on one motor, pass, swing back), told the colour, scores below plain told B on training seeds (0.43 to 0.96
against 1.58): the eyes say how much of a colour is in view, not where, so a detour can't be aimed, and half the
time it swings into the guard. Not yet certified as a recruitment case: the limit may be the eyes, not the brain.

## D18: the arena, robots that eat each other (2026-10-30)

The user's idea (QUESTIONS.md, step 6): no food or poison, only N robots, each the creature's body, trying to eat each
other; the arms race as the engine of frustration, with no hand-made worlds. The user's rules: each robot two-tone,
its mouth half red and its tail half blue (so the eyes, two colours wired at random, say mouth from tail); born with
a full belly; eating takes time (while a mouth touches another's tail, energy flows to the biter, who tastes +1 each
tick; the bitten can pull away); mouth to mouth nothing happens; collisions; an empty belly is death, and a newborn
(a fresh brain, its own wiring) appears at random at once, so N stay alive and newborns are the world's food. My
choices: belly 20 meals, a bite 1 meal a second, soft springs between discs slow against the tick, and no pain for
the bitten (taste is what touches the mouth; a pain sense would be a new body-to-brain signal, the user's decision).
`lab/arena.py`, watched live by `lab/arena_watch.py` (mouth M and tail T lettered, bites drawn).

First look, four robots with B's brain, 16 arenas of 1,000 s (559 robots): robots bite, get bitten, starve and are
replaced (lives of about 115 s), and clump in biting chains. B can't learn the colour here: it learns from poison
alone (doubt rises with each and flips the bit), and nothing tastes bad, so the bit never flips (0 flips in every
life). Belief barely matters: robots believing blue (tails) is food eat 0.57 a 10 s, those believing red 0.65 (and
lose 0.72 against 0.56); all eat far less than they spend (about 1.3), so nearly all starve, their meals mostly
accidental. Chasing a tail at the same speed rarely catches it unless it turns.

Mended after the user watched (2026-10-30): robots drove through each other, since only the two coloured discs
collided; now five discs cover each triangle (mouth, tail, rear corners, centre) and the spring is stiffer (K 3000;
still slow against the tick). Over 300 s, robots touch for 32% of the time, overlapping by a median 0.16 mm, 0.66 mm at
the 99th percentile, 1.3 mm at worst (a disc is 2 mm across). The bitten now taste -1 for each 10 ms bitten (pain as bad taste:
the user's decision); B's doubt now rises with pain whatever its eyes see, flipping its bit 10 to 14 times a life.
The view shows its speed against real time and slows to 1/100 of it.

Robots sprinted blindly (the user, watching): B's own program, made for scattered static blocks. With 8 coloured
discs in the world against 36 blocks, sightings are rare, so B is often bored and runs (17% of the time) or drives at
whatever it believes is food (13%), both at full speed (35 mm/s, nine body lengths a second); robots alike in speed
can't catch a runner. The user's changes: ten robots, and each thruster pushing a third as hard (top speed a third,
turning as before). Now (200 s): driving 37% of the time, running 6%, scanning 57%; speed a median 4 mm/s, 11 at the
90th percentile; still 0.24 meals eaten a robot a 10 s, so all starve (16 deaths in 200 s); collisions overlap a
median 0.17 mm when touching, 1.7 mm at worst.

Two eyes (the user's decision, 2026-10-30: one eye per colour can't track; robots mostly circled each other): each
a fan of 12 rays from the mouth, from 5 degrees across the middle out to 40 degrees on its own side, so four
sensors; the body draws which colour feeds which pair and which of a pair is the left eye. Brains: B adapted (each
colour's pair summed: it can't steer), B told the colour (learning off), and a hand-built Braitenberg tracker (told
its wiring and the colour: while driving, the thruster that turns it towards the eye seeing more tail fires more).
The tracker first spun (a firing turns the body about 18 degrees once settled, and with a third of the push turning
dominates); its gain scanned 0.03, 0.1, 0.25: 0.1 best. 10 robots, arenas of 300 s, meals eaten a robot a 10 s:

| arena | eaten (95%) | |
|---|---|---|
| all B | 0.15 [0.14, 0.16] | believing tails food 41% |
| all told B | 0.33 [0.32, 0.35] | |
| all trackers | 0.40 [0.38, 0.41] | |
| told B with trackers, half each (16 arenas) | told 0.33 [0.32, 0.35], tracker 0.42 [0.40, 0.44] | |
| B with trackers | B 0.21 [0.19, 0.22], tracker 0.39 [0.37, 0.41] | |

So the arena is certified for two kinds of growth: steering (the tracker beats told B in the same arena, by about a
quarter), and learning the colour, which B now learns wrongly: pain comes from behind while it chases a tail ahead,
so it blames the tail and believes it is food only 41% of the time. Eating is zero-sum (all eaten is lost by
another) and every robot spends, so on average every robot starves: success is outliving the others, the newborns
the world's food.

The arena made three times faster (each step's mouths and tails computed once, every robot's eyes in one compiled
call, bites found at once: 1.2 to 0.4 ms a step; the same eyes, shapes and collisions to the bit, only the order of
random draws changed: told 0.33, tracker 0.40 on 16 arenas). The viewer draws every robot's rays.

Steering grown (`grow_arena.py`): told B and a grower; a failed chase (a drive with no bite) is frustration, which
grows one recruit linking the food pair's two sensors' difference to the motors' balance, trying no link, one sign,
the other, each for a timed trial, keeping the best. Catches are too few to judge by (a "chase" lasts 0.08 s, 53 a
10 s, 6% caught; robots live about 96 s), but how much food it sees separates the signs (forced, `steer_probe.py`:
right 28.6 tail pulses a second, eating 0.41; none 25.4, 0.31; wrong 17.4, 0.14). Judged so, it kept the right sign
in 180 of 240 lives (15 s trials; wrong 25), yet ate no more than told B (0.32 vs 0.33; trials of 6 and 3 s the
same, choosing worse): in a life of 96 s the wrong sign's trial costs what the right one gains. The trigger fired in
every life (chases nearly always fail), so it discriminates nothing. The user's verdict: in this world the colour
and the thruster wiring are the same every life, so evolution's: the baseline brain becomes the Braitenberg tracker.

Escape from bites (`escape.py`), certified before a grower looks for it: trackers half, the other half the tracker
with a scripted response to pain (a bad taste: being bitten), for 0.5 s firing 50 a second. Both thrusters (speed
away) is worse: lost 0.46 a 10 s vs 0.29, dying younger (the biter, behind, simply follows). One thruster (a turn)
cuts the loss from 0.37 to 0.14 and nets (eaten minus lost) +0.23 [+0.20, +0.26] a 10 s over the tracker, paired
by arena (16 arenas; either side the same within noise). Eating alone misjudges it: the net is what the belly sees.

The escape grower (`grow_escape.py`), told nothing of what it is for, beside the tracker: each sensor a fading tag and
a running rate of pain onsets while tagged; a bite no tagged sensor predicted (none above twice the rate at any
time) is frustration, which grows one recruit on the taste's pathway to the motors: on a bad taste's onset it fires,
for 0.5 s at 50 a second, one generic operation (nothing, motor 0, motor 1, both), each tried for a timed trial,
judged by the taste summed over it (+ biting, - bitten: what bites move in and out of the belly), the best kept. A
first predictor (towards -1 at each bite, slowly back otherwise) let every sensor "predict" pain, as robots see each
other nearly always, so it grew in 14 lives of 247; compared with the rate at any time, the user's point held: no sense
predicts a bite (40,610 of 40,631 unpredicted) and it grew in every life, about 8 s in. Half the arena growers, half
trackers, net over the tracker: trial 15 s +0.078 [+0.055, +0.103] (16 arenas); 8 s +0.102 [+0.083, +0.122] (48
arenas: kept a turn in 463 of 720, nothing 103, both 154); 30 s +0.127 (16 arenas, but no robot lived through four
trials: the gain of trying turns, not of choosing). The control, one operation drawn and kept without judging: +0.067
[+0.044, +0.092] (48 arenas). Judged minus drawn, paired: +0.035 [+0.012, +0.061]. So escape grows and pays, surely;
of the scripted turn's +0.23 it gets 0.10, most of that because half its operations are turns; judging adds a third
of it, held back by lives of 96 s and a judge as noisy as 8 s of taste (it keeps the harmful "both" in a fifth of
lives). Watch: `arena_watch.py 1 --kinds grow,tracker` (each grower labelled with its operation, "?" while trying,
OUCH while bitten).

Judged bite by bite instead (`bite=1`, now the default): at each bite's onset the four operations compete, each its
running mean plus its own noise (sd / sqrt(1 + tries)), the winner responds, and the taste of the next `win` s is its
outcome. Chosen on arenas 0-15 (net over the tracker): win 1 s, sd 0.3: +0.138; win 0.5: +0.172; 2: +0.128; sd 0.1:
+0.184; 1: +0.090; win 0.5 and sd 0.1: +0.202; **win 0.25, sd 0.1: +0.215** (a turn kept in 230 of 240); win 0.5,
sd 0.03: +0.202. Judged on fresh arenas 100-147: **+0.186 [+0.173, +0.199]**, a turn kept in 696 of 721 lives, its
loss to bites halved (0.37 to 0.18 a 10 s); the scripted turn on the same arenas +0.241 [+0.223, +0.259]: the grower
gets 77% of it. (Motor 0 kept 410 times, motor 1 286: B's drive is not symmetric in its motors, its lone first beat
on motor 1.) Traced (`findbite.py`): bitten, the grower fires its motor and the bite is broken within 10 ms, then
it spins on, 480 degrees in the 0.5 s response; a shorter scripted response does as well (0.1 s +0.241, 0.04 s
+0.244 on arenas 0-15), so the response's length doesn't matter and the scripted ceiling stands.

The control (`phantom=1`): pain no response can stop, the grower's bad tastes replaced by phantom ones at random
(0.6 onsets a second, 0.3 s each; its real bites still drain its belly, unfelt). Arenas 0-15: net over the tracker
+0.011 [-0.008, +0.029], tied (escapable: +0.215); kept nothing 54, motor 0 104, motor 1 45, both 41 (escapable: 4,
146, 84, 6): a turn 61%, near chance's 50%. Motor 0 is favoured here too, as in the real arena (410 to 286): perhaps
firing it disturbs B's drive less (its lone first beat is motor 1's), so fewer of its own bites are lost; untraced.
With no bites at all it can't grow (frustration counts only bad tastes).

The arms race (QUESTIONS.md, the plan, 4, candidate a; `pursuit.py`), certified first: every robot the tracker with
the escape grower; half also respond to a bite ending (good taste stopping) by firing at 50 a second. Net minus the
plain escape growers', arenas 0-15: left 0.2 s -0.027 [-0.040, -0.016], right -0.021 [-0.032, -0.009], both -0.024
[-0.037, -0.013]; 0.04 s: left -0.003 [-0.014, +0.007], both -0.030 [-0.044, -0.016]. No pursuit pays: the victim
turns to its own side, differing between robots, so a fixed response is right half the time, and the tracker already
steers to a tail still in view. So escape leaves the biter nothing simple to grow, and the arms race stops at one
round here. With every robot escaping, each eats less than half as much (0.16 a 10 s against 0.39 among trackers):
the world grows hungrier, which every robot pays for alike.

Candidate (c), a memory of a recent bite (`alert.py`), certified first: half the escape growers, for T s after a bite
ends, unless escaping or chasing, keep moving (both thrusters at B's running rate) or keep still. Net minus the plain
escape growers', arenas 0-15: run 3 s -0.043 [-0.057, -0.034] (lost 0.124 vs 0.133, but ate 0.098 vs 0.150, dying
younger), run 10 s -0.069 [-0.082, -0.056], still 3 s -0.065 [-0.076, -0.055] (losing more). No response to a recent
bite pays, so there is no memory to grow either. In this arena, escape is the one reflex worth growing in the life;
steering pays more but is evolution's (the same every life).

A recruit with no menu (QUESTIONS.md, the plan, 4: "a menu that doesn't already hold the answer"; `grow_escape.py
knob=1`): the recruit two knobs, firing motor k at 50 sigmoid(w_k + e_k) a second for 0.5 s after a bite's onset,
e_k its own noise (sd 1) drawn each bite; the taste of the next 0.25 s against its running mean (10 bites) moves each
knob by (outcome - mean) e_k (node perturbation). Its first form replaced the brain's output while it responded, so a
weak response stopped the robot dead (from w0 = -2: -0.054 [-0.088, -0.020]); a recruit adds beats to its pathway, so
now they are added to the brain's own. With beats added the scripted responses change: a turn +0.241 [+0.214,
+0.274], and both thrusters, harmful when replacing, +0.242 [+0.224, +0.261] (on top of the tracker's own firing,
uneven while it steers, it is a turn and a burst), so the ceiling stays about +0.24. Arenas 0-15, net over the
tracker: from w0 = 0 (both at half rate) +0.236 [+0.216, +0.256], learning off +0.165 (the jitter alone turns it,
one motor firing harder each bite); from w0 = -2 (barely responding) +0.161 [+0.142, +0.182], learning off +0.049.
Held out (arenas 100-147): **from w0 = 0 +0.229 [+0.212, +0.246]** (95% of the scripted turn; the menu grower got
+0.186), ending firing both in 502 of 755 lives, motor 0 harder in 228, motor 1 in 24; **from w0 = -2 +0.152
[+0.136, +0.167]** (63%), ending motor 0 in 443 of 729, motor 1 in 56, both 82, nothing 148. So no menu is needed:
two knobs and per-bite perturbation find the escape; where they start matters (from nothing, in some 75 bites a
life, a fifth of lives haven't left it). Motor 0 is favoured strongly here (443 to 56), as before, untraced.

Why motor 0 (`spincheck.py`): B scanning fires motor 0 alone, so a robot not chasing is always spinning motor 0's
way. At 71% of 9,945 bites' onsets the tracker wasn't chasing, spinning +1.82 rad/s motor 0's way (chasing, -0.01);
two bites in three found it turning so. A motor 0 response adds to that spin, a motor 1 response first cancels it.
Scripted by motor (arenas 0-15): m0 +0.264 [+0.244, +0.282], m1 +0.238 [+0.215, +0.258]; added to the tracker's own
beats, m0 +0.274 [+0.250, +0.306], m1 +0.266 [+0.242, +0.291]. At full strength the difference is small; at the
weak responses a knob recruit starts from it is large, so every jitter towards motor 0 tastes better and the knobs go
that way. So the ceiling was low: the best scripted response, m0 added, held out (arenas 100-147) +0.253 [+0.244,
+0.262]. Against it: the knob recruit from w0 = 0 91%, from w0 = -2 60%, the menu grower 74% (replacing, against m0
replacing, not measured held out).

Why a fifth of lives never leave the low start: near w = -2 the response barely changes with the jitter, so each of
some 75 bites teaches little. Larger steps and jitter (arenas 0-15, from w0 = -2): eta 3 +0.193, jitter sd 2 +0.197,
both +0.217 [+0.195, +0.241], those left responding hardly at all 14 of 253 (42 before); from w0 = 0, both +0.262
[+0.241, +0.282]. Held out (arenas 100-147), now the defaults (eta 3, sd 2): **from w0 = -2 +0.218 [+0.203, +0.232],
86% of the best scripted escape** (38 of 739 left responding hardly at all); **from w0 = 0 +0.245 [+0.230, +0.261],
97%**. So where it starts barely matters once its steps are large enough for a short life.

A disc body (the user's decision, 2026-10-31: the triangle's five colliding discs hooked each other as robots turned
past; then the disc everywhere, `NOTEBOOK.md`, The disc). Each robot is now the creature's disc (radius 2.3 mm, the
triangle's circumradius), its front half red and its rear half blue, its mouth the front point of its rim, its
thrusters on its rear rim (their physics unchanged: a firing adds forward speed and a turn); collisions a spring along
the line of centres, frictionless, so no push spins a robot; the eyes see the colour of the half each ray meets; a
mouth within 0.3 mm of another's rim, on its rear half, bites. The triangle arena is kept as
`lab/arena_triangle.py`. Over 200 s, robots touch for 92% of the time (they clump), overlapping a median 0.07 mm,
0.25 mm at the 99th percentile (rarely far more, 3.9 mm once: probably a newborn placed on another robot, untraced).
A rear half is a far bigger target than a tail disc, so robots eat two to three times as much (16 arenas of 300 s,
meals eaten a robot a 10 s): told B 0.76 [0.73, 0.78] (0.33 on the triangle), the tracker 1.08 [1.06, 1.11] (0.40), so
steering still pays (the arena stays certified for it).

Escape and the failed certifications re-run on the disc; then **a flaw in the arena's accounting** (2026-10-31): the
net every arena script reported (eaten minus lost to bites) never charged firing, though each firing drains the belly
by `spec.THRUST` (0.002 meals; a 0.5 s burst at 50 a second, 0.05). So any response that added firing looked free,
and some looked good: on the disc, firing more seemed to pay whatever triggered it (keeping moving for 10 s after a
bite +0.12, always +0.14; bursts after a bite ends +0.13, at random moments +0.14; escape's control, pain no response
stops, +0.07). Every arena result before this, on the triangle too, was judged so (the escape grower's 86-97% above
included); they stand only as uncharged. Firing now charged (`AR.THRUST * r.firings` in lost), on the disc, net over
the plain tracker or escape grower a 10 s, paired by arena:

| | net, firing charged |
|---|---|
| escape, scripted, beats added, a turn (held out) | +0.088 [+0.061, +0.117] |
| escape, scripted, both thrusters (held out) | +0.123 [+0.101, +0.146] |
| **escape grown, two knobs from w0 = 0 (held out)** | **+0.136 [+0.115, +0.157]** |
| its control, pain no response stops (held out) | -0.094 [-0.118, -0.070] |
| pursuit, both thrusters 0.5 s after a bite ends (0-15) | -0.191 [-0.220, -0.157] |
| the same bursts at random moments (0-15) | -0.321 [-0.344, -0.298] |
| keep moving always (both at B's run rate, not driving or escaping; 0-15) | -0.489 [-0.514, -0.464] |
| **keep still always (no scanning; 0-15)** | **+0.426 [+0.390, +0.460]** |

So: escape grows and pays, surely, and its control now costs, as a control should; the grower matches or beats the
scripted bursts (it learns its rates, so it needn't fire at full rate). No pursuit pays. And the tracker's scanning
is its biggest waste in a crowded arena: robots that never scan net +0.43 a 10 s more, three times escape's gain.
That looked like a standing policy to fix (evolution's), but it isn't one: **what pays depends on who else is in the
arena.** The tracker's standing policy hill-climbed by invasion, firing charged (`arena_tune.py`: B's hold, boredom,
scan, drive and run rates and the tracker's gain, each doubled or halved in turn, kept if surely better than the best
so far, arenas 0-15): scanning twice as fast (+0.14 [+0.11, +0.17]), then holding half as long (+0.06 [+0.01,
+0.10]); held out (arenas 100-147) the tuned tracker nets **+0.139 [+0.114, +0.165]** over the plain one. Never
scanning, among trackers, costs: -0.37 [-0.41, -0.31] (scanning at a quarter rate -0.30; without running too, -0.45).
Decomposed (arenas 0-7, a 10 s): among trackers, a robot that keeps still eats half as much (0.64 against 1.26) and
loses more to bites (1.14 against 0.94); among escape growers it eats as much (0.62 against 0.61) and loses as much
(0.64 against 0.65) while firing far less (0.66 against 1.04). Robots that escape are hard to catch, so chasing and
scanning for them is wasted; robots that don't are worth hunting. So the best standing policy is
frequency-dependent: evolution's answer shifts with the population, as in any arms race, and a growth case must be
certified against the population it will live in. Firing is costly here: about a meal a 10 s, as much as a robot eats.

Escape against the tuned tracker (every robot's standing policy scaled, `grow_escape.py t_scan=2 t_hold=0.5`, held
out, arenas 100-147, firing charged): grown from w0 = 0 **+0.029 [+0.004, +0.054]**, from w0 = -2 +0.018 [-0.011,
+0.044], its control -0.073 [-0.092, -0.054]. Against the plain tracker it was +0.136. So most of escape's value was
the plain tracker's poor standing policy: once evolution's part is tuned (faster scanning, shorter holds: a biter
that re-finds its prey quickly, so a broken bite costs it little), a grown escape barely pays for its firing. The
grower still beats its control by about +0.10 (it does find the response that helps most), but the case no longer
certifies well: a growth case must be certified against a tuned baseline, and in this arena, with firing charged,
there is little left that the life must learn.

## D19: a lopsided body learned from every drive (2026-10-30)

The plan's step 5 (QUESTIONS.md: learn from what happens every moment, not only from meals), its first experiment,
with D18's lesson (judge each try at once, against its own jitter). B (its tolerances drawn, its learning as
designed) on bodies with each thruster 0.5 to 2 (`bodies.THRUSTERS`), lives of 2,000 s, the other knobs B's
(`drivebal.py`, in `lab/`). The drive's balance x (log of motor 0's rate over motor 1's) is jittered afresh
by e at each drive's start; the drive's outcome, the food pulses it saw (a drive lasts while the block stays in view,
so one that curves off loses it sooner), against its running mean (20 drives), moves x by eta (outcome - mean) e.
About 9 drives a 10 s, so some 1,800 lessons a life, against a few hundred meals.

Seeds 0-31 (choosing): floor (balance 0) 0.22 [0.02, 0.43], stranded 38%; ceiling (told its body, the
drive balanced) 2.11 [2.04, 2.20]. Jitter sd 0.3: eta 0.01 0.74 [0.57, 0.89]; 0.03 0.80 [0.63, 0.95] (the balance
within 0.13 of the oracle's by 200 s, 0.08 by 500 s, median; correlation 0.87 at the end); 0.003 0.38. Close to
the right balance, yet far below the ceiling: born at the oracle's balance, learning off, it gets the ceiling (2.11)
with no jitter and 1.07 with jitter 0.3, so the exploring costs half, the score being steep in the balance. Smaller
jitter with the step scaled by 1/sd^2 is unstable (sd 0.1: 0.22; 0.05: 0.06; the outcome's noise swamps it); sd 0.1
with eta 0.1 0.82, last third 4.31 but 19% stranded. Paired opposite jitters (0.77) and outcomes relative to the
usual (0.53, barely learning) don't help. The stranded lives stop driving, so their balance freezes where it was,
often still near 0: learning needs successful drives to learn from (with eta 0.03, 4 of 64 stranded, the most
lopsided: median |oracle| 0.75 against 0.47). Jitter shrinking with experience, sd 0.3 / sqrt(1 + drives / N):
N 200 1.14 [0.96, 1.31]; 500 1.07; 1000 1.09 [0.96, 1.22], stranded 3%, the job done, the balance's correlation with
the oracle's 0.96 (slope 0.92). (In D15, annealing hurt the meal-judged tuner; here the balance converges in a few
hundred drives, so there is time to settle.)

Held out (seeds 50000-50031), N 1000, eta 0.03: **0.98 [0.78, 1.17]**, stranded 8%, last third 4.30; floor 0.36
[0.14, 0.61], 31% stranded; ceiling 1.92 [1.80, 2.04]: 40% of the gap closed in 2,000 s. D15's tuner (`discrete.
tuner body=1 mistune=1`: every knob and the balance, starting at B's, judged by meals and sightings per energy) on
the same lives: 0.72 [0.54, 0.90], none stranded; **per-drive minus it +0.26 [+0.07, +0.45]**, paired. Judging each
drive by what it saw learns the balance far faster than judging by meals (D15's SPSA tuner moved it about 27% of the way
in 10,000 s; this one 54-92% in 2,000 s). What's left: the exploring's cost (even shrinking, a jitter on a steep
knob), and the lives that strand before they learn. Next: is it prediction? Not yet: the outcome is a fixed proxy
(food seen), not a learned model of what a beat does to the eyes; a unit predicting its eyes from its beats is the
next step.

## D20: the body learned by prediction: what comes round again (2026-10-30)

The plan's step 5 proper: a model of this body learned from what its own beats do to its eyes, no outcome and no
jitter. While B scans, one motor alone turns it at a steady rate, so whatever it sees comes round again once a
revolution, and a revolution's period goes as 1 / that thruster's strength. So scanning with each motor in turn and
finding each one's period gives the thrusters' ratio, and the drive's balance x = log(T0 / T1) straightens the drive
(k0 g0 = k1 g1). The goal (keep what is chased ahead) is the same every life, evolution's; the model of this body
is the life's (QUESTIONS.md, step 5). `periodbal.py`, in `lab/`; lopsided bodies (each thruster 0.5 to 2),
lives of 2,000 s, B's other knobs as designed.

Feasibility (`period_probe.py`, 60 s of one-motor scanning): the eye pulses' intervals recur at 0.79 of the period
the body's spin predicts, in every one of 16 scans (the factor, from beats' discrete timing, cancels in the ratio),
once the estimator finds the fundamental rather than a multiple. In a life, though, B's own scans are short (a
median 0.4 to 0.6 s, ended by the first food sighting; 4 to 29% last a revolution), and their intervals gave
nonsense (correlation with the right balance -0.36, then -0.14 with intervals counted against chance per scan, each
scan's pulses placed at random within it). So the brain makes its own experiments: sweeps, every `cal_every` s for
`cal_len` s, ignoring what it sees and turning with one motor alone at its scan rate, the motor alternating; only
the sweeps' pulses counted. Pooled with B's own scans the estimate is worse (47% within 0.2): they aren't a steady
spin, starting from rest or a drive's momentum.

The estimator, in four steps, each traced on lives whose periods are known: the shortest comb within 90% of the best
picked halves; the best comb picked multiples (teeth beyond a 5 s sweep have no data: now only teeth chance expects
data in count); the shortest fraction of the best recurring at its own lag left 3 of 16 wrong (5x, 3x, 1.5x); then
subharmonic summation (Hermes 1988, from pitch detection: each multiple k of a candidate period weighted 0.84^(k-1)
and summed, so a multiple of the period loses the teeth between and a fraction gains empty ones), each tooth's
evidence the excess over chance in units of chance's spread ((observed - expected) / sqrt(expected): a ratio over a
tiny expectation was noisy). Then 16 of 16 lives found both periods, every balance within 0.02 of the right one.

Seeds 0-31 (choosing): sweeps of 5 s every 50 s, 1.50 [1.40, 1.60] (98% of balances within 0.2; the sweeps alone,
balance fixed at 0, 0.23); sweeping stopped once its last 3 estimates agree within 0.03 (its own adjustment stalled:
a body doesn't change within a life) but with too little evidence locks in wrong ones (1.18 to 1.38, 70 to 75%
within 0.2); requiring 2,000 intervals a motor first, 1.74 [1.60, 1.87]; 5,000, sweeps every 20 s: **1.80 [1.72,
1.89]**, every balance within 0.2, none stranded, sweeping stopped after a median of 36 sweeps (some 700 s).

Held out (seeds 50000-50031): **1.66 [1.55, 1.76]**, none stranded, 98% of balances within 0.2 (correlation 0.99);
floor 0.36, ceiling 1.92: 83% of the gap closed. Paired, on the same lives: above D19's per-drive learner by +0.68
[+0.51, +0.86], above D15's meal-judged tuner by +0.93 [+0.73, +1.14], below the ceiling by -0.27 [-0.36, -0.16].
Its price on the standard body, where there is nothing to learn: plain B 2.46 [2.34, 2.54], the period learner 2.15
[2.07, 2.22] (-0.31: the sweeps, about 9% of the life turning blind, and small errors).

So prediction beats outcome here by far: a model of what its own turning does to what it sees, learned from a few
minutes of deliberate experiment, finds the body almost exactly, where learning from outcomes (meals, or food seen
per drive) found it roughly and slowly, and paid for exploring all life long. What it needed that B lacked:
experiments of its own (a sweep is a question asked of the body), a bank of coincidence counters (the intervals'
histogram, with chance's), and a way to tell a period from its multiples.

Cheaper sweeps. On the standard body the cost is all early: in the last third the period learner equals plain B
(6.14 against 6.10, seeds 0-31). Seeds 0-31, standard body (plain B 2.52) and lopsided: 5 s sweeps every 20 s
stopping at 5,000 intervals 2.13 and 1.80; at 3,000 2.14 and 1.83; 3 s every 12 s 1.99 and 1.67 (a short sweep holds
few long intervals); 8 s every 32 s (3,000) 2.29 and 1.83, 13 sweeps; 12 s every 48 s 2.32 and 1.73 (94% within 0.2).
Pairs grow as a sweep's length squared, so longer sweeps gather evidence faster, until too few sweeps leave some
estimates wrong. Held out, **8 s every 32 s, stopping at 3,000 intervals and 0.05**: standard body 2.27 [2.16,
2.36], **-0.18 [-0.31, -0.04] against plain B** (5 s sweeps: -0.31); lopsided **1.71 [1.52, 1.88]**, tied with
5 s sweeps (+0.05 [-0.12, +0.19]), 87% of the gap closed, below the ceiling by -0.21 [-0.39, -0.07]; sweeping ends
after a median 12 to 14 sweeps (about 7 minutes).

Watched (`watch_pb.py`, seed 50001): the panel shows each sweep as it happens and the motor sweeping; run on without
drawing, after 2 sweeps (100 s) both periods match what its thrusters give (1.37 and 1.12 s against 1.37 and 1.13)
and the balance is the one it needs (+0.20); sweeping stopped after 10.

Bodies varied in every factor (`allbody=1`: overall strength, an asymmetry between the thrusters, the eyes'
sensitivity and drag, beside each thruster), held out: floor 0.34 [0.16, 0.56], 31% stranded; ceiling 1.75 [1.48,
2.00]; **the period learner 1.28 [0.99, 1.56]**, 8% stranded, two thirds of the gap, 84% of balances within 0.2.
Each failure is off by log 2 (0.69 to 0.71): one motor's period found at half or double. Traced (seed 50027, a weak
thruster): excess 22 at the true 2.48 s and 13 at twice it, but a real 7 at half it (cause untraced: not a wider
circle, since a one-motor sweep's circle has radius PUSH / TURN, about 1.25 mm, whatever the thruster's strength). The multiples' weight doesn't help (seeds 0-31:
0.84 89% within 0.2, 0.7 88%, 0.6 83%); choosing among the best, its double and its half by the strength of each
one's own first recurrence is much worse (61% and 66%: shorter lags hold more chance pairs, so their excess in chance's
spread is smaller). In one long sweep on that body (`halftrace.py`, 120 s) there are no pulse pairs at half the
period at all, so the half period comes from pooling short sweeps: within a sweep any two blocks give intervals at
their bearings' difference plus whole revolutions, a few times over, and a pass is a burst of pulses, so each
coincidence counts the burst's size squared; such clumps land at random lags, noisier than chance's Poisson spread
allows. Counting a pass, not a pulse (pulses within 0.15 s one event) doesn't help (seeds 0-31: 86% within 0.2 on
fully varied bodies, 97% on lopsided ones, but 23 sweeps against 12, efficiency 1.16 and 1.61). Nor does making each
sweep one vote (its pairs scaled to one before pooling, each lag's excess over the votes' spread: 83% and 91%, against
89% and 98% without), nor more evidence before sweeping stops (6,000 intervals, fully varied: 91%, efficiency 1.30
against 1.34): the errors persist, so they are systematic for some bodies, not noise. Traced (seed 50027, motor 0,
the first 240 s): one sweep gives nearly all the half-period pairs (99 pulses, 279 pairs at half the period, 387 at
the period; the others 0 to 27), the sweep with the nearest block (2.6 to 5.1 mm from the body's centre as it
circles, against 5 to 12 mm in the others): a block that close plausibly crosses the 2 mm corridor twice a
revolution (unproven). Discarding sweeps denser than 8 pulses a second: 91% within 0.2 on fully varied bodies (89%
without), 98% on lopsided ones, but 20 to 22 sweeps against 12, efficiency unchanged (1.35, 1.80); 10 a second, 88%.
So a near block is likely the cause, and none of five remedies is worth its cost; left at 89% on fully varied bodies.

Sweeps only when frustrated (2026-10-31; QUESTIONS.md, step 5's open "cheaper sweeps"). A body that already drives
well needn't be swept, and the brain knows it is doing badly from its own taste: at each slot (every 32 s) it sweeps
only if it has eaten fewer than `gate` meals since the last slot (`gate=8`). Once the balance is right the meals rise
and the sweeps stop of themselves: the bad outcome ends the experiments, as step 4's candidate answer says. The gate
is a meal rate, an outcome, not a property of the body, but it is tied to this world's food (B eats about 20 meals
in 32 s on the standard body, about 5 on a lopsided one before it learns): evolution's, for this world. Seeds 0-31,
standard body (B with no sweeps 2.52) / lopsided / fully varied: gate 6, 2.55 / 1.79 / 1.25 (sweeps 0 / 4 / 5);
gate 8, 2.49 / 1.88 / 1.31 (0 / 5 / 7); gate 10, 2.45 / 1.92 / 1.38 (2 / 7 / 10); ungated, 2.29 / 1.83 / 1.34 (13 /
12 / 12). Held out (seeds 50000-50031), **gate 8**: standard body **2.47 [2.43, 2.51], tied with plain B (+0.01
[-0.06, +0.11])** and surely above ungated sweeps (+0.20 [+0.11, +0.31]): the sweeps' cost is gone; lopsided **1.68
[1.50, 1.84]**, tied with ungated (-0.03 [-0.11, +0.06]), 85% of the gap, with 5 sweeps instead of 12; fully varied
**1.39 [1.11, 1.66]**, against ungated 1.28 (+0.11 [-0.06, +0.30], not sure), 88% of balances within 0.2, three
quarters of the gap. A mildly lopsided body is swept late, since it is frustrated only now and then: seed 50001
(balance +0.20) eats 8 meals in most slots, first sweeps after some 400 s and has its balance (+0.19) by 600 s;
seed 50027 (-0.50) sweeps from the start, a first estimate wrong (+1.21, too little evidence) corrected by 220 s
(-0.49). Standard bodies (seeds 50001, 50005) never sweep. `gatetrace.py`, `gatepair.py`; the viewer
(`watch_pb.py`, now gated, with `--standard` for the standard body) shows the meals counted since the last slot.

What a circuit would have to hold (2026-10-31; QUESTIONS.md, step 5's open "a circuit for the counters and the
period-finder"), before designing one: not a fine histogram (1,700 bins of 10 ms) with chance computed from each
sweep's length and pulse count, but a bank of K coincidence counters at log-spaced lags (0.1 to 17 s), each counting
the intervals within half a spacing of its lag; each candidate period one counter, scored by fixed wiring from the
counters nearest its multiples (weights 0.84^(k-1): evolution's wiring); chance taken from the counters' neighbours
(the mean of those within 25% of a counter's lag, excluding itself: lateral inhibition), not computed
(`fundamental_bank`, `bank=K local=1`). Seeds 0-31, lopsided bodies, gated sweeps (the fine histogram 1.88, 98%
within 0.2), chance computed: K = 32, 1.49 (88% within 0.2, 31% within 0.05); 48, 1.52; 64, 1.69 (91%, 69%); 96,
1.86 (98%, 91%). Chance from the neighbours: 96, **1.87 (100%, 92%)**; 128, 1.90; neighbours within 50%, 1.82; and
the excess as a plain difference, not over chance's spread (no square root), 1.87 again. Held out, 96 counters with
neighbours' chance, paired with the fine histogram on the same lives: standard body 2.48 (+0.01 [-0.00, +0.03]; B
2.46), lopsided 1.66 (-0.02 [-0.17, +0.16], 97% within 0.2), fully varied 1.34 (-0.06 [-0.25, +0.16], 84%): tied
everywhere. So the period-finder needs about 100 counters (a 4% spacing: a period's quantisation then costs the
balance under 0.05), lateral inhibition and a fixed comb, and nothing computed. Left for the circuit: the delay line
that holds a sweep's pulses for up to 17 s (a sweep has some 100), so that each new pulse can be compared with every
earlier one; the counters as memory nodes written by coincidences; the winner-take-all over the candidates.
The natural delay line, a chain of 96 one-bit stages at the counters' lags (a stage marks that some pulse passed
that long ago; pulses within a stage merge, and each new pulse adds at most one to each occupied stage's counter,
`binary=1`), loses: seeds 0-31, lopsided 1.70 [1.54, 1.84] (94% within 0.2) against 1.87 (100%) counting, fully
varied 1.31 against 1.34. Traced (seed 3, motor 0, 600 s): the stages saturate as they widen with lag, keeping 78%
of the coincidences at 0.1 to 1 s, 46% at 1 to 3 s and 32% at 3 to 8 s, so the comb's higher teeth flatten. So the
line's stages must carry how many pulses passed, not whether one did: charge packets, as in a bucket-brigade line,
each coincidence adding its stage's charge to its counter. (A sweep lasts 8 s, so lags beyond 8 s hold nothing;
the line need only be 8 s long, still beyond a chip's slowest leak, 3.9 s, so its stages are memory-like.)

Where the rest of the gap goes (2026-10-31). Held out, gated (gate 8), lopsided: food per 10 s by third 4.30, 5.19,
5.26, against the ceiling's 5.47, 5.45, 5.35: the loss is in the first third, the time to learn (the balance within
0.1 for good after a median 140 s; 380 s for mildly lopsided bodies, swept late), plus 7 of 64 lives whose balance
stays 0.05 or more out and lose a third of the last third's food. So learn sooner: a first sweep at birth and slots
every 12 s until each motor has 1,000 intervals, then every 32 s (`cal_first=0 cal_fast=12`). Seeds 0-31, lopsided:
the first sweep at birth alone 1.87 (gated 1.88); with 12 s slots 2.00, but the standard body falls to 2.36 (8
sweeps), since no body eats 8 meals in a 12 s slot. So the gate became a rate (`gate_rate=1`: frustrated if the
last 32 s hold fewer than 8 meals, or pro rata early in life): standard 2.35, still 7 sweeps, because a sweep is 8 s
of fasting that itself trips the gate. Counted on a foraging clock that stops during sweeps (a sweep's own fast
isn't frustration): standard **2.48**, lopsided **2.02** (100% within 0.2), fully varied 1.37 (seeds 0-31). Held
out (seeds 50000-50031), paired with the plain gate on the same lives: standard **2.48** (+0.01 [-0.06, +0.07]; B
2.46, 2 sweeps); lopsided **1.81 [1.68, 1.93]**, +0.13 [-0.01, +0.31], 98% within 0.2, 8 sweeps, **93% of the gap**,
below the ceiling by -0.12 [-0.22, -0.02] (gated: -0.24); fully varied **1.51**, +0.12 [-0.15, +0.35], 91% within
0.2, 83% of the gap, below the ceiling by -0.23 [-0.45, -0.08]. These are now the period learner's settings
(`watch_pb.py`).

A flaw in the drive whenever it is balanced (2026-10-31), found while trying B's own scans (below). With equal gains
the fast model's drive fires both thrusters on each beat; with any balance at all (g0 != g1) each motor has an
oscillator of its own (`model.Model.step`), and motor 1's only runs while driving or running, so each drive starts
with the two out of step, by whatever its phase was left at and motor 0's moved on during the scan. B with gains
1.0001 and 0.9999 on the standard body: 2.29 against 2.52 (seeds 0-31): unpaired first beats turn the body off the
block it has just seen. Two fixes, as options in `model.py` (off by default, so earlier results stand): `paired=1`,
the slower motor firing beside some of the faster one's beats: 2.51 there, but the lopsided ceiling falls (1.93
against 2.11); `sync=1`, the two oscillators set in step at each drive's start: **2.56** there, and the lopsided
ceiling **2.24** (seeds 0-31). So the cost was the drive's start, not unpaired beats as such. Held out (seeds
50000-50031), with `sync=1`: the ceiling (told its balance) **2.15 [2.03, 2.26]** on lopsided bodies, +0.23 [+0.10,
+0.35] over the old drive's 1.92, and **1.94** on fully varied ones (+0.20 [+0.07, +0.32] over 1.75); the floor
(B, balance 0, so equal gains) unchanged, 0.36. The period learner with it: lopsided **2.03 [1.89, 2.16]**, +0.22
[+0.12, +0.33] over the same learner without, 98% within 0.2, **93% of the new gap**, below the ceiling by -0.12
[-0.25, +0.02] (no longer surely); standard body 2.45, tied with B (-0.01 [-0.15, +0.13]); fully varied 1.59 (+0.08
[-0.08, +0.24]), 78% of the new gap. Every balanced result before this (D13's oracle, D15's tuner, D19, D20 above)
paid this flaw, ceilings and learners alike; the gaps quoted there are on the old drive. Re-judged on the fixed
drive (held out, floor 0.36, ceiling 2.15): D15's tuner (`discrete.tuner body=1 mistune=1`, 2,000 s) 0.80 (+0.08
[+0.02, +0.15] over the old drive), 25% of the gap; D19's per-drive learner 1.02 (+0.04 [-0.09, +0.17]), 37%; the
period learner 2.03, 93%. The order holds: D19 above the tuner by +0.21 [+0.02, +0.40], the period learner above
D19 by +1.01 [+0.83, +1.19]. The flaw cost the learners judged by outcomes little (their balances are rough
anyway) and the ones that find the balance almost exactly most. A circuit's drive would
start both thrusters from one oscillator anyway: this is the fast model being fairer to a balance, not a new
mechanism. (QUESTIONS.md's "B's drive starts cleanly, in transistors" is the same cost in SPICE: a drive's first
beat matters.)

B's own scans again (2026-10-31; step 5's open "B's own scans made usable"). Counting only their steady part (after
0.5 s, scans of 1 s or more) made little difference (seeds 0-31, lopsided, no sweeps: 0.68, 64% within 0.2,
correlation 0.79). The cause was in the model: B's scan rate is its drive oscillator's, so scaled by g0, which moves
as the balance is learned, smearing the periods pooled over the life (the sweeps run at the bare scan rate). With
the scan at its own rate (`scan_rate=1`): 1.38, 92% within 0.2, correlation 0.93, with no sweeps at all; with the
drive also started in step, 1.75 (94%). So B's scans do carry the body; D20's first finding, that they gave
nonsense, was mostly this smear. But they are worse than sweeps: on the standard body scans alone cost 0.24 (2.28
against 2.52, the balance re-estimated all life from evidence a little biased by scans' starts), and added to the
sweeps they lower the lopsided score (2.08 against 2.21). Left out.

How many pulses a delay stage must hold (2026-10-31). Re-tried on the current settings (early, rate-gated sweeps;
the drive started in step), lopsided bodies: on seeds 0-31 one-bit stages tie the bank (2.06 against 2.10, -0.04
[-0.18, +0.09]; stages holding 2 pulses 2.07, any number 2.08). The old deficit (1.70) was mostly the old settings:
one-bit stages with the early sweeps 1.96 (+0.26 [+0.14, +0.39]), with the drive in step 1.88 (+0.19 [-0.02,
+0.38]). Held out (seeds 50000-50031, floor 0.36, ceiling 2.15), paired on the same lives: the bank with counting
stages 1.92, below the exact histogram (2.03) by -0.11 [-0.25, -0.01] (tied before the drive was fixed: a finer
balance now pays); stages holding any number 1.93, the same as the bank (+0.01 [-0.01, +0.04]); stages holding up
to 3 pulses (`cap=3`) **1.88, tied with the bank** (-0.04 [-0.18, +0.08]); one-bit stages 1.78, -0.14 [-0.29,
+0.01] against the bank, -0.25 [-0.43, -0.07] against the exact histogram. On other bodies one-bit stages tie the
exact histogram (fully varied 1.63 against 1.59, standard 2.38 against 2.45, both within noise). So a stage needs to
count to about 3 (two bits, or a charge packet that saturates at three), not to carry exact counts; the remaining
cost of counters over the exact histogram, about 0.1 on lopsided bodies, may be the bank's quantisation (96
counters, 4% apart) now that the drive's balance is finer. Held out, lopsided, against the exact histogram: 128
counters 1.90 (-0.12 [-0.31, +0.02]), 192 counters 2.01 (-0.01 [-0.15, +0.09]), 128 counters with 3-pulse stages
1.97 (-0.05 [-0.16, +0.03]); 128 against 96 -0.01 [-0.22, +0.19], 192 against 96 +0.10 [-0.05, +0.24]. No
ordering is sure: differences of 0.1 are within these 64 lives' noise. So 96 to 192 counters with stages counting
to 3 come within about 0.1 of the exact histogram, and 192 ties it; more lives would be needed to price the spacing.
The period learner restricted to what a circuit could hold (still the block model, not built: 192 counters, chance from neighbours, a fixed comb, a delay line of
stages holding up to 3 pulses; `bank=192 binary=1 cap=3`), held out on all three bodies, paired on the same lives:
lopsided **1.93**, tied with the exact histogram (-0.10 [-0.30, +0.06]), 88% of the gap, below the ceiling (-0.22
[-0.44, -0.01]); fully varied **1.68**, tied with the exact histogram (+0.09 [-0.09, +0.33]), 84% of the gap, below
the ceiling (-0.26 [-0.44, -0.11]); standard **2.49**, tied with B (+0.03 [-0.09, +0.16]). So nothing in it needs
exact counting: some 200 counters and a short delay line of 2-bit stages would do. Building them in SKY130 is not
started.

## D21: the yardstick: what knowing where blocks are is worth behind these eyes (2026-11-01)

The first measure of the bounds (QUESTIONS.md, step 3; `BOUNDS.md`): is there room for a brain to gain by placing
what it has seen (place-like cells, the user's happy medium between a built-in map and none)? D13's seer, told each
block's exact place when an eye pulses for it, reaches 4.5 against B's 2.54 (both told the colour). But a pulse says
only that the nearest block of its colour is somewhere in the corridor ahead (4 mm wide, 15 mm long). So the seer
told places only as well as pulses could tell them (`lab/seer2.py`): each pulse an estimate, its range off by
a factor exp(N(0, rerr)) (inf: anywhere along the corridor), its offset across exact or (lat) anywhere across the
corridor; estimates of one block averaged over its pulses or the first kept; an estimate reached without eating
dropped. Still told its pose (perfect path integration) and the colour: generous. Held out, 50000-50063 x 2:

| range known to | offset across | pulses averaged | efficiency |
|---|---|---|---|
| exactly | exact | | 4.55 [4.33, 4.77] |
| +-25% | exact | yes | 4.40 [4.22, 4.57] |
| +-50% | exact | yes | 4.10 [3.95, 4.25] |
| +-50% | exact | no | 3.78 [3.59, 3.94] |
| a factor e | exact | yes | 3.06 [2.90, 3.21] |
| not at all | exact | yes / no | 3.43 [3.31, 3.55] / 3.09 [2.93, 3.25] |
| +-50% | **not at all** | yes | **2.82 [2.70, 2.95]** |
| not at all | not at all | yes / no | 2.13 [2.01, 2.25] / 1.86 [1.72, 2.01] |
| B, told the colour (D13) | | | 2.54 [2.40, 2.66] |

(Averaging uniform guesses at the range converges on the corridor's middle, a lucky bias: why "not at all" beats
"a factor e".) **The offset across matters most, and the eyes barely give it**: a block anywhere in the 4 mm corridor
gives the same pulses (a little fewer when part of it is outside), while the mouth eats within 1 mm. Known across but
not in range, a memory of places is worth 3.1-3.4, well above B; not known across, even with the range good to
+-50%, 2.8, about 0.3 above B (unpaired), and with neither, below B. So behind these eyes most of the seer's 4.5 is
information the eyes don't deliver: a memory of where blocks are can add little over B's "drive while you see it",
unless the brain gets the offset by moving (sweeping the corridor across a block and timing when it enters and
leaves: active sensing), which this yardstick doesn't try. Not an ideal observer (its policy is the seer's, and it
never senses actively), so a rough bound, but it says where the headroom is: in sensing across, not in remembering.

What an eye split across the corridor would be worth (the same yardstick, `lat=0.5`: told which half a block is in,
not where within it; `lat=0.25`, which quarter; log `lab/v/seer2_split.log`):

| across | range +-50% | range unknown |
|---|---|---|
| nothing (these eyes) | 2.82 [2.70, 2.95] | 2.13 [2.01, 2.25] |
| which half (an eye split in two) | **3.95 [3.78, 4.09]** | 3.15 [3.01, 3.29] |
| which quarter | 4.12 [3.95, 4.28] | 3.54 [3.40, 3.68] |
| exactly | 4.10 [3.95, 4.25] | 3.43 [3.31, 3.55] |

A split eye recovers most of the headroom (to 3.95 against B's 2.54, with the range roughly known); quarters add
little more. A body change, the user's to decide (D22).

## D22: does sideways sensing emerge in an evolved dynamical network? (2026-11-01)

After D21 (the headroom is in sensing where across the corridor a block lies) and the user's insight that time is
where a small brain computes (README; `BOUNDS.md`, Time): a 6-node continuous-time network (Beer 2003;
`lab/ctrnn.py`), evolved by CMA-ES (minimal/search.py's) in the real body's loop, told which eye is food:
leaky nodes fully connected, each its own time constant (20 ms to 5 s), every eye pulse kicking every node, nodes 0
and 1 setting the motors' rates, noise on every node; nothing about scanning, holding or phase designed in. Judged
by `discrete/tune.py`'s robust efficiency on 8 seeds x 2 a generation, 24 a generation, 150 generations from zero,
then 150 more from the best (logs `lab/v/ctrnn_n6*.out`). Held out (50000-50063 x 2):

| | efficiency | food | poison | last third | firings |
|---|---|---|---|---|---|
| after 150 generations | 1.25 [1.17, 1.34] | 7.20 | 2.00 | 3.76 | 777 |
| after 300 | **2.03 [1.96, 2.10]** | 5.43 | 0.58 | 8.87 | 548 |
| B, told the colour (D13) | 2.54 [2.40, 2.66] | 6.1 | | | |

It plateaued about 2.0-2.2 on its training lives. **Sideways sensing**, tested directly (`lab/sideways.py`,
50000-50031 x 2: for each block's first food pulse, its offset across the corridor, and whether that block is eaten
within 1 s):

| offset across | B, told the colour | the network, 150 gens | the network, 300 gens |
|---|---|---|---|
| 0-0.5 mm | 75% | 63% | 67% |
| 0.5-1 mm | 73% | 57% | 57% |
| 1-1.5 mm | 34% | 36% | 36% |
| 1.5-2 mm | 23% | 18% | 21% |

The same cliff past the mouth's 1 mm in all three: blocks in the mouth's path are eaten by going straight, the rest
only when a turn happens to bring them in. **No sideways sensing emerged**: evolution found a B-like forager, a
little worse. Not yet known whether the pulses' timing carries the offset well enough to use (a far block gives
about one pulse a sweep, and the spin runs on 15 ms after a thruster stops: minimal/NOTEBOOK.md, M11), so the
next measure is how much the timing of a block's pulses, against the creature's own beats, tells about its offset
(the bound on timing, `BOUNDS.md`, Time) before evolving bigger.

**The bound on timing, under B's movements** (`lab/timing.py`, log `lab/v/timing.log`; B told the
colour, 50000-50063 x 2, 44,861 food pulses with the block in view): at each food pulse, what the brain could know
(its pulses' exact times: pulses in the burst, time since it began and since the last, pulses in the last 0.05 and
0.2 s; its motors' beats in the last 0.05 and 0.2 s and since the burst began; whether it is driving) against the
offset of the block that pulsed, signed towards the side motor 0 turns to (a life could learn the sign: its wiring
is fixed). Gradient-boosted trees, cross-validated by life:

| while | pulses | offset sd | R2, signed offset | R2, its size | side right, beyond 1 mm | the commoner side alone |
|---|---|---|---|---|---|---|
| scanning | 12,650 | 0.88 mm | 0.02 | 0.01 | 69% | 68% |
| driving | 32,211 | 0.78 mm | 0.03 | 0.04 | 61% | 58% |

**Under B's movements, the timing carries almost nothing about where across the corridor a block is**: beyond the
mouth's reach the side is guessed no better than by always guessing the side the sweep brings blocks in from. B's
scan turns fast (a beat turns the body about 18 degrees, 16 rad/s fading at 50 per s, against a corridor about 30
degrees wide at 7.5 mm), so a block crosses the corridor within 10-20 ms and gives about one pulse. So
sideways sensing would need movements made to probe (slow sweeps across a block seen), and those pay only once the
reading exists, and the reading only once they do: a valley no small step of evolution crosses, which may be why it
didn't emerge. Next: whether a probing movement (on a food pulse, single beats alternating left and right) makes
the offset readable at all; if not, these eyes and this body don't offer it.

**Under probing movements** (the same measure, `timing.py probe=RATE,S`, log `lab/v/probe_runs.log`; 32 seeds
x 2): on a food pulse, B's beats replaced for 0.5 or 1 s by single beats alternating between the motors at 6 to 24
per s. While probing, beyond the mouth's reach the side is right in 72-77% of pulses against 55-56% for the commoner
side (R2 0.10-0.17, the slowest wiggle best), all of it from the conjunction of a pulse with the creature's own last
beat (pulse timing alone: R2 0.00): a pulse just after a motor-1 beat finds the block on the side away from that turn
63-65% of the time; after a motor-0 beat, 50%. Readable, a little. **And usable? No** (`lab/dance.py`, held out
50000-50063 x 2, B told the colour; while driving, beats alternating instead of paired, with a forward pair every
`push` beats, and on each food pulse extra beats turning back, away from the last turn, or on, towards it):

| policy | efficiency |
|---|---|
| B | **2.60 [2.48, 2.72]** |
| zig-zag drive (50 per s, a pair every 2nd) | 1.93 [1.82, 2.05] |
| zig-zag, turning back on each pulse (variants of rate, push, beats) | 0.80 to 1.46 |
| zig-zag, turning on | 1.28 [1.20, 1.37] |

Every turn knocks a block out of the mouth's 1 mm path faster than the thin side information steers it back: a
beat turns the body 18 degrees, too coarse to correct an offset of a millimetre or two. So **these eyes and this
body don't offer sideways sensing**, not from B's movements nor from any probing tried, and B is near what they
allow for finding food: the headroom of D21 (to 4.5) needs information across the corridor these eyes don't give.
Reaching it is a question for the body (an eye split across the corridor, finer turning), the user's to decide.
(Corrected by D24: finer turning was there all along, by timing: a lone beat turns 18 degrees, but its partner a
tick later cancels most of it, leaving 7. What these eyes lack is the side, not the fine turn.)

## D23: D20's period found by entraining instead of counting? (2026-11-01)

The dance (BOUNDS.md, Time; the user: learning to dance, not to solve a chess problem) where the information exists:
D20 finds each motor's revolution period from the eye pulses recurring in its sweeps, with a delay line and 192
counters, never built in transistors. Could an oscillator entraining to the pulses find it with far fewer parts?
Offline (`lab/afo.py`): D20's sweeps (8 s every 32 s, never stopping) from 32 lopsided seeds x 2, 1000 s each
(log `lab/v/afo_sweeps_0-32.pkl`), the histogram's balance within 0.2 of the right one in 95% of lives
(correlation 0.96). Each estimator's balance from the first 8 to 32 sweeps:

| estimator | within 0.2 | correlation |
|---|---|---|
| D20's histogram of intervals, subharmonic summation | **95%** | 0.96 |
| an adaptive-frequency oscillator per motor (each pass pulls its phase to 0 and nudges its frequency; frequency creeping up from too slow, so the first lock is the fundamental; Righetti, Buchli and Ijspeert 2006), several couplings and creep rates | 8-22% | -0.26 to 0.23 |
| a resonator climbing (three per motor, the energy of each sweep's passes at the period and either side, faded over sweeps, moving to the best), from 0.5-4 s | 14-36% | -0.26 to 0.18 |
| a bank of 200 resonators, the most energetic | 22-53% | 0.53-0.62 |

Traced: the periodicity is there (the passes' power pooled over sweeps, phase-free, peaks at the right periods:
seed 0, 2.11 and 1.87 s, balance 0.12, right 0.12). But a sweep lasts about 4 revolutions and each revolution brings
about 5 passes from different blocks: an oscillator must lock its phase before its frequency correction means
anything, and in 4 cycles, kicked by the other blocks' passes, it never does. Without phase, a resonator's energy
over a short sweep is a comb of narrow peaks at the period and its multiples: a climber misses the narrow peaks, a
bank picks multiples; D20 needed subharmonic summation to choose. **So entrainment needs a long dance with one
consistent partner**: many cycles, one rhythm. Here there are several partners at once and few cycles, and the
phase-free statistic (intervals, with chance's) is the efficient one; the dance form isn't a free lunch.

**Where locking has its cycles: a bank of resonators on long steady spins** (the user's idea of oscillators locking at
simple ratios; Large's neural resonance; `lab/bank.py`, log `lab/v/bank.log`). 60 s of one-motor
scanning at B's rate on 32 lopsided seeds, both motors; each motor's period from the first 10 to 60 s, judged by the
balance within 0.1 of the right one. A bank of N oscillators log-spaced 0.1-4 s, each pass kicking all of them, the
most resonant after summing each period's harmonics (subharmonic summation; at first I summed the wrong way, at
multiples, and integrated the rotation by plain Euler steps, which grew the fast oscillators until they swamped
the rest: both traced and fixed):

| estimator | 10 s | 20 s | 40 s | 60 s |
|---|---|---|---|---|
| intervals' histogram, comb (period_probe.py's) | 16% | 53% | **88%** | 81% |
| 96 resonators (damped, 0.1 per s) | **47%** | **69%** | 69% | 66% |
| 48 resonators | 47% | 47% | 59% | 41% |
| 24 resonators | 44% | 34% | 25% | 19% |
| 48 limit-cycle oscillators (entraining, beta -1) | 47% | 19% | 50% | 34% |

Traced on two spins: the bank's spectrum matches the exact one, and its top peaks are the period's harmonics (0.72 s
for 2.16, 0.95 for 1.92: several blocks a revolution spread the power over them), so the harmonics' summation is
essential. A resonator bank with it reads a period sooner than the histogram (within 20 s, 69% against 53%) but
plateaus lower, and needs about as many oscillators (96) as D20's counters; oscillators that entrain (limit
cycles) do worse than plain resonators. No saving in parts here; the oscillator form's advantage, if any, is speed
on short evidence.

## D24: a split eye, prepared for the user's decision (2026-11-01)

The user said go ahead with preparing D22's open body question, without changing the body: what would a brain make
of an eye split across the corridor? `world.py` is unchanged; `lab/split.py` wraps a life. Each eye's
pulses are drawn exactly as `creature.Life` draws them (the world's random stream untouched, so with no steer it is
B's life to the tick: 2.60, as dance.py), and each is tagged by the half of the corridor whose rays saw it (a Poisson
process split by each half's share, from a stream of its own). So the brain has four sensors, 2 x the colour's
sensor + the half's wire, the halves wired at random each life as everything else is.

**The brain**: B told the colour (V_H 99), and a steering reflex while it drives. Which motor turns towards which half
is told (to measure), wrong, or learned: B scans on motor 0 alone, so a block passing through the view is seen first
in the half motor 0 turns towards, then in the other. A saturating counter steps +1 or -1 at each change of half
between pulses less than `gap` s apart while scanning (any colour).

**Tracing the reflex** (`lab/split_diag.py`: at each steer, where the nearest food block in the corridor really
is, and whether it is eaten within 1 s). The first versions all lost to B (1.5-2.6, told the map). Three causes, in
turn:

1. A rule that tested "the other half silent" on a leaky count never fired (a leaky count is never 0 again): 55
   steers in 64 lives. Windowed counts instead.
2. B drives at 50 pairs a second, so while the condition held every pair turned: several 18 degree turns in a row.
   One turn per detection (the counts cleared after a steer).
3. Still a loss: steers at blocks 1-2 mm off the path were eaten 64-74% of the time (unsteered, 11-14%), but at
   blocks within 1 mm, which B eats 80-86% of the time, only 34-48%. The body turns about its centre, 2.3 mm behind
   the mouth, so a beat of 18 degrees swings a block at range r across by about (r + 2.3 mm) x 0.32, near 2 mm:
   past the mouth for any block already within 1.2 mm of its path. The halves split at the middle and the mouth
   eats within 1 mm of it, so many steers were at blocks already on course.

**Finer turning, by timing** (no body change): the partner beat 10 ms late. A beat's turning speed fades at 50 per s,
so its partner 10 ms later cancels all but 1 - e^-0.5 of the turn: about 7 degrees (20 ms later, 12). The swing
becomes about 0.7 mm, which helps a block 1-2 mm off and barely disturbs one on course. D22's conclusion that a
beat's 18 degrees is too coarse was wrong about the body: finer turning was there, in time.

**Results** (efficiency, B told the colour; tuned on seeds 0-63, rule W 0.2 s, N 1, Q 1, cleared after each steer,
lag 1 tick; the map counter's gap 0.1 s chosen on seeds 0-63, after I had first looked at it on held-out seeds
50064-50127, so the final judging is on 50192-50319 x 2, never looked at before; logs `lab/v/split_*.log`):

| brain | held out 50064-50191 | held out 50192-50319 |
|---|---|---|
| B (no steer: the same lives) | 2.58 [2.49, 2.66] | 2.49 [2.40, 2.58] |
| split eye, map told | 3.23 [3.14, 3.32] | **3.14 [3.03, 3.25]** |
| split eye, map learned (gap 0.3; then 0.1) | 2.91 [2.80, 3.02] | **3.02 [2.92, 3.11]** |
| split eye, map wrong | 1.67 [1.60, 1.73] | |

The map learned: right in 254 of 256 lives by the end (gap 0.1), settled right for good in a median 12 s (quartiles
5 and 27 s), wrong 5% of the time over a life and unknown 10% (`lab/split_learn.py`). Counting only changes
after a run of pulses in one half made it worse (block-centred pulses alternate halves at random), as did a much
shorter gap. Food went from 6.4 to 7.2 per 10 s, poison unchanged.

**On lopsided bodies** (each thruster 0.5-2), B collapses without its balance (0.26; with the steer 0.56), as D13
found. Told its balance with its drive started in step (D20's ceiling arm): **2.32 [2.22, 2.42] to 2.71 [2.60,
2.82]** with the map learned (held out 50192-50319 x 2; right in 253 of 256). The steer stacks on the balance;
smaller, since a lopsided pair's late partner cancels more or less than 7 degrees.

Watched (`lab/watch_split.py --seed 50192`, frames recorded): the panel shows each half's food pulses, the
map learned against the truth (right by 24 s) and each steer; by 24 s it had eaten 21 food and 1 poison, where B in
the same life had eaten 17 and 2.

**For the user**: a split eye is worth about +0.5 (+21%) to B with a reflex of a few parts: a window count per half
(two counters), a comparator, a 10 ms delay on one motor, and a saturating counter for the map, against the
seer's yardstick of 3.95 for a perfect memory with a split eye (D21). The map is learned by the brain from its own
movement, as B's balance is in D20: nothing about the body is told. Whether to make the eye split is the user's
decision; until then, world.py stays as it is.

## D25: the first story: which colour is food (2026-11-02)

The interventions phase's pilot (`STORIES.md`, its result; `AGENTS.md`, its rules): block model, standard bodies,
tolerances drawn, no SPICE, re-validated at component level with silicon's noise. `lab/story1.py` holds the arms;
training seeds 0-63 x 2; ladder judged on 50000-50063 x 2; final on 50200-50327 x 2, which chose nothing; logs
`lab/v/story1_*.log`.

**Evidence** (`story1.py stats`, told and told-backwards lives, seeds 0-63 x 2; `lab/v/story1_rates.json`). Each taste
by its sign and which of the followed and other eye pulsed within 0.3 s, per s, with the bit right and wrong:

| taste | followed pulsed | other pulsed | right | wrong | evidence the bit is wrong |
|---|---|---|---|---|---|
| poison | yes | no | 0.008 | 0.487 | +5.94 bits |
| poison | yes | yes | 0.035 | 0.152 | +2.11 |
| poison | no | yes | 0.050 | 0.004 | -3.58 |
| poison | no | no | 0.006 | 0.006 | -0.10 |

(Food mirrors these, the lives being paired.) In all 3.26 bits/s towards the truth, right or wrong. My sum beside
`PARTS.md` the first day, 0.66 bits/s, used poison's rate alone and missed which eye vouched for it. Silence carries
nothing, for the same reason: the total rates are equal.

**The ideal observer** (`Bayes`): the log-odds that the bit is wrong, each taste adding its log ratio, holding the likelier
bit. Exact given those rates, treating tastes as independent; it keeps B's movements, so it bounds learning the bit, not
foraging. It ties with being told. B's "learning costs only 0.15" (D13, on other seeds) understated what a better write
could recover: here B is 0.28 below told, all recoverable.

**Why B falls short.** It counts every poison. A poison bumped into while scanning says little or even speaks for the bit
(the third row above), yet steps doubt up. Tuning that tally only reached 2.27, a fuller count (`count`), a fading count
(`fade`), and a run counter food resets (`run`, which is what the tuned tally turned out to be) no higher. A no-bit
brain judging each eye by its own drives (`path`) reaches 2.12 if the bad eye ends a drive and 1.22 if it is merely
ignored, repeating `learn_avoid`'s lesson (D8) that declining isn't avoiding.

**The circuit** (`Gated`): the tally written only while driving. `use=0` reads B's own drive signal; `use=1`, separate
tags with a window, came no better (2.56 against 2.55 on training seeds), so no new tag is needed. Trust 0 scores 2.32;
1 2.54; 2 to 9 2.55, so one step of trust suffices and a two-state counter would do. It is a three-factor write (taste,
times what was just being done), as the minimal line's bit already is (M10).

**Controls.** The unsolvable world (each meal's taste a coin, `--control random`) is a wrapper in `story1.py`, an experiment
only. Nothing separates it from a hard world yet: the circuit flips 16.5 times a life.

**At component level** (`lab/story1_node.py`): D14's tuned B (`lab/v/sep_search_silicon.json`) with doubt's two writes
gated by the hold node, doubt's four numbers polished 12 generations by efficiency (`lab/v/story1_node.json`,
`story1_node_tune.log`). B itself was not re-polished here, and B's 30 generations had more knobs, so if anything this
favours B. The told arm is a fixed bit's right half of each pair, so it isn't paired with the circuit.

**A run with no end** (the user, watching a long life, 2026-11-02: at about tick 1,200,000 it travels straight almost for
ever). `model.py`'s run ends only at a food pulse: no timer. Traced (`lab/story1_run2.py`, seed 50206, red as poison,
`lab/v/story1_run2.log`): from 11,891 s a run of 4,579 s, no meal, spin exactly 0, 0.0011 degrees off the world's axis, so
0.0011 mm sideways a lap. The user suspected noise; the block model has none on the thrusters (they fire in exact
pairs). With no meal no block respawns, and the drift itself brings a block into the corridor at last. The long runs
lie near the axes and diagonals, closed lines of the torus, the ones that stay clear; D9's stranding again. B and told
have them too (113-199 s in `lab/v/story1_run.log`).
A limit on the run (`Timed`: past `run_max` s boredom restarts, so it scans onto a new heading): training seeds, 0.5 s
2.71, 1 s 2.72, 2 s 2.63, 5 s 2.59, 10 s 2.58, 20 s 2.56, none 2.54 (1 s +0.18 [+0.07, +0.29]). Held out at 1 s
(`lab/v/story1_run3_held.log`): lives of 100 s, seeds 50400-50527 x 2, 2.62 against 2.53, +0.09 [-0.01, +0.21], tied, stranded
1% to 0%; lives of 10,000 s, seeds 50600-50615 x 2, 2.72 against 2.57, **+0.15 [+0.11, +0.18]**, gain +0.16 [+0.10, +0.22].
The results above in this entry have the flaw. The user's decisions: the limit joins the baseline, every arm re-judged
(`lab/story1_final2.py`, `lab/v/story1_final2.log`: `STORIES.md` holds the numbers; settings as chosen without it, rates
recaptured); a thruster mismatch is not a repair for every body, but a flaw to introduce and learn to compensate for:
the next story. At component level (`lab/story1_node.py`, `limited`; `lab/v/story1_node_judge2.log`) a first limit, charged
whenever drive-or-run was up and lifting boredom hard, stranded 19% of lives on training seeds (ordinary drives charged it,
and it pushed boredom past where a drive leaves it, so the scans ran long). Charged only while running, latching past 0 V and
reset once boredom's node is back at 0.1 V, four elements: 2.35 against 2.05 without, on training seeds.

## D26: the second story: unequal thrusters (2026-11-02)

The user's framing: the mismatch is a flaw introduced to discover how to compensate, as its own experiment with a baseline
and an optimum target (`STORIES.md`, 2; `lab/story2.py`; logs `lab/v/story2_gap.log`, `story2_error.log`). B told the
colour, the run's limit, `sync=1`, each flaw's body `factors`. Where the lopsided ceiling of D20 was 2.15, it is 2.56 with
the run's limit on these seeds.

The curve's shape is the finding: nothing to x1.01, a sure cost by x1.03, half the score by x1.25, below zero by x1.5. D5's
blind driver collapsed by 1%; B's eyes correct small curves for free ("drive while you see it"), so it is immune up to about
1%, and then not. x4 scores above x2 only because it strands in 70% of lives and so eats less poison.

Precision: the score against the error e in the log balance is lopsided (e > 0, motor 0 rate too high, costs far more than
e < 0), at x1.25 and x2 alike, measured relative to the balance that makes the drive straight. Untraced. Candidates: `model.py`
scales the scan by g0 too (D20's smear), so e > 0 also speeds the scan; and a curve with the scan's turn against one
across it. The peak may lie just below 0: e = -0.05 is tied with 0 at both sizes, so the told balance is the target only
to within that. Bits to learn are a rough sum: log2(spread / tolerance) = log2(0.63 / 0.05).

Stage 3 (`lab/story2_stage3.py`, logs `lab/v/story2_fixed.log`, `story2_learners.log`): `STORIES.md` holds the table. The curve's lopsidedness
traced: not the scan's speed (`trace`, unscaled, the same; `story2_trace.log`) but its direction (`lab/story2_mirror.py`, the scan on motor 1: the
curve flips, `story2_mirror.log`). A coarse estimate biased to the cheap side (`lab/story2_bias.py`, `story2_bias.log`): nothing, tied at every
bias. The fixed search's training-to-held-out fell little (0.80 to 0.91, within noise), its best below D19 and D20 as ever.

## D27: the ladder of harder tests (night of 2026-11-02)

The user's idea, each test one change to story 1's baseline, none accumulating (`STORIES.md`). `lab/ladder.py` holds the rules and brains; rounds on training
seeds `lab/ladder_try*.py`, `lab/ladder_digest.py`, logs `lab/v/ladder_*.log`; final `lab/ladder_final.py`, `lab/ladder_final2.py` on 52000-52063 x 2,
longer lives on 52100-52131 x 2. Dead ends and bugs, which the story page leaves out:

- `Transition` (flip after a vouched good once a tally passes theta) detected alternate in every life and never in plain, but cured it poorly (1.40); `Detect` kept its tally and cured by
  following the eye that didn't pulse last, 1.63-1.88: that eye is wrong often enough to cost. `Cycle` needs neither: a good taste itself advances the turn.
- `Lengths`, a learned run per eye, collapsed to length 1 on any stray poison; `Lengths2`, believing a length only twice over, never reached the rule (alternate -0.21, pattern -0.78).
- Three clocks for swaps: `Rhythm`, `Rhythm2`, `Rhythm3`. All find the period; none beats removing trust, at 10 s 0.42-0.79 against 1.16. The rough bound for a reactive brain, 1.4 s wrong a swap, is a sum, not measured. A clock told the period isn't tried: it would say whether the estimate or the phase is what fails.
- Digest's first form gave the brain two tastes per meal, and its numbers meant nothing; mended (`Digest.taste`, one meal one taste), W shortened from 2 s to 1 s since at about one meal a second 2 s leaves little to eat.
- `Diagnose` tried at short 2, 3, 4 and tau_v 20, 40, on training seeds: 2 and 40 chosen, little between them. Its 5 s swaps look like sequences (few goods between), as expected. Not tried: undoing growth that didn't help, which might mend both.
- All at block level; none re-validated at component level, as the phase's rule asks once a story succeeds. A sequence memory is a counter and a few memory nodes, and should be buildable.

## Lessons from this line, in full (moved from the old LESSONS.md)

- **An ideal body is also a gift an optimiser takes.** The two thrusters were identical to the last digit, and a
  tuned 9-part blind driver used it: firing both 300 times a second it ate four times as fast as any sighted circuit,
  as efficiently; with the thrusters unequal by 1% it drove in circles (discrete/NOTEBOOK.md, D5). Ask of every
  perfect symmetry in the simulation whether a real body would have it.
- **A finer step alone is not a check: tighten the error control too.** The discrete circuits lived in ngspice at a
  largest step of 0.5 ms. At finer steps their results fell apart, and a night went into tracing it to a slow
  oscillator; but the finer runs were the wrong ones: with the default error control, a marginal event (a transistor
  barely turning on) fired or not by each step's rounding, at any step. Tightened, every step agreed with the first
  results (`discrete/NOTEBOOK.md` D7). Check convergence in both step and tolerance, on the first design that works,
  and distrust a design whose behaviour hangs on a marginal event: a simulator's rounding, or a real part's
  tolerance, decides it.

## D28: the interventions table (2026-11-03)

The user's aim: about 10 rows, then one universal correction circuit (`STORIES.md`, the table and its limits; rules in `AGENTS.md`). `lab/table.py` holds the worlds
and arms, on story 1's circuit; `lab/table_rows.py` the class-by-class trials (each setting on 53000-53015 x 2, the best 3 on 53016-53047 x 2, the best held out on 53100-53163 x 2);
`lab/table_auto.py` the automatic versions, in their world and the plain world; `lab/table_paired.py` the comparisons behind each "tied". Logs `lab/v/table_*.log`.

**Row 2's old baseline was not comparable**: `lab/story2.py`'s brain is told the colour. Rebuilt on the circuit: 0.67 to 2.42 at 1,000 s. `sync=1` changes nothing on a body with equal rates.

**Dead ends and causes.**

- A told scan side (`ScanSide`), one bit from D26's lopsided curve: +0.04 [-0.03, +0.11] on row 2, so the curve's lopsidedness can't be cashed in that way, and learning it (`ScanLearn`) gained nothing.
- Weak eye: hold scaled to the eye (`EyeHold`, `AutoHold`), slowing while following it (`EyeSlow`), nothing above the base brain. Its target, the standard body, holds pulses this body never delivers.
- Clumps: staying near a recent meal (`Local`) -0.02 [-0.11, +0.06]. Being told the colour is tied with the base, so the poison here (3.13 per 10 s) comes from clumps, not from the bit.
- Scarce: resting (`Rest`) -0.01. Its best manual, a search, +0.06 [+0.00, +0.12]; told +0.10. Too small to be a row.
- A coincidence filter on both eyes, not only the noisy one (`Filter`, eye_told 0): 0.96 in the noisy world, 1.05 in plain, -1.67. An unconditional filter ruins a good eye; `AdaptEye`, setting each threshold from its eye's background rate, passes both.
- A bug of mine: settings named `eye_x`, `local_x`, `far_x` were read as scalings of a number, and crashed rows 9 and 10's first run. Renamed; no result was affected.
- Digest's target first ran without its pause (-3.70), corrected to 1.79 before use. Moving blocks and scarce's told arm were added afterwards as checks.

**The automatic versions, traced and fixed.** Scoring on training and validation seeds: the row's efficiency, less 3 x any shortfall against the base brain in the plain world (`lab/table_fix.py`, `lab/table_more.py`, `lab/table_third.py`; logs `table_fix.log`, `table_more.log`, `table_third.log`, `table_fourth.log`, `table_gate.log`).

- *Gated sweeps and jitter paid in the plain world because of false alarms that feed themselves.* With sweeps never allowed the difference from base is exactly 0, and with gate 12 almost all the cost sits in 19 lives of 128 with 4 or more sweeps, -0.48 each, their balance at a mean |x| of 0.12 (`lab/table_diag.py`, `table_diag.log`). A chance shortage lets a sweep run, the balance moves on thin counts, meals fall, and more sweeps follow. Requiring two short checks running (`SweepsG2`) took it to 0. My earlier hypothesis, eating during sweeps corrupting the bit, was wrong or small.
- *Jitter's count was born at its own gate*, so every life's start read as a shortage: on 41% of the time in a plain 100 s life. Born at 1.5 x the gate, over 200 s (`JitterG2`). Gate 15 is the highest tied on tuning seeds (14: 1.39, 15: 1.47, 16: 1.55 but surely below base in plain, 17: 1.66).
- *Volatility had to be the mark of a world that was right and changed*: a flip that ended a run of goods, not any flip (`Volatile2`).
- *The pause*: counting bads soon after a taste false-alarmed in 44 of 128 plain lives at 400 s, since poison at the first wrong bit comes in runs and the 400 s tally accumulated. Counting only meals vouched for as food, a 150 s leak and a late bad counting against, 4 of 128 (`LearnPause3`). Its 100 s number is mostly the cost of learning: 15 s at about -4.7 then 1.75 averages near 0.8.
- *Weak eye: its old target was the fault.* Told the colour with the eye still weak, settings searched per case: 1.83 on earlier seeds against 1.77; told alone 1.88 against 1.79 here, gap not sure. The loss is pulses never delivered.
- *Row 1 in the all-food world.* The harness's first comparison of its circuit with the brain with taste unwired: 4.55 against 6.70. The bit shuts out an eye with nothing to avoid.

**The final judge** (`lab/table_final.py`, `lab/table_settings.json`; `table_final.log`): every entry on 54000-54063 x 2, once. Numbers in `STORIES.md`. Row 6's plain test failed narrowly there (-0.02 [-0.05, -0.01]) having passed on the earlier seeds, and I didn't retune it. Tuning seeds had flattered little: rows 2, 3 and 8's automatic numbers moved by about 0.05 or less against their last look, as did row 7's gain (0.32 to 0.56, base 0.10 to 0.36, the gain about the same).

**Row 1's automatic version**: both eyes followed until the first bad, whose eye is then the poison's (`U` with `open=1`): plain +0.00 [-0.09, +0.11], all food +2.15 [+1.97, +2.33], equal to taste unwired, on 54000-54063 x 2 (`table_watch.log`).

**The cross-test** (`lab/table_final.py cross`; `table_cross.log`; matrix and conclusions in `STORIES.md`).

**Seen without a display, not on screen**: `lab/table_watch.py` lists when each mechanism turns on in 16 lives; none of these arms has been watched running.

## D29: looking for one universal correction circuit (night of 2026-11-03)

The user's plan for the night: step back, conclude, state hypotheses, test comprehensively, explain success or failure. Conclusions, hypotheses and the result, with the final judge's numbers, are in `STORIES.md`. This entry is how it got there.

**H0/H1, the union with one taste node** (`lab/universal.py`, class `U`; `lab/universal_search1.log`, `lab/universal_read.py`). 120 settings across all worlds. The only strong conflict is the trust prior: swap against unreliable and patchy (correlations -0.60, -0.52); other sets of worlds are independent. On the best (`universal_s72.json`, validation seeds), each part alone against the whole (`lab/universal_parts.py`, `universal_parts1.log`): the whole is about equal to the part alone (pattern +0.36, digest -0.22), so parts barely interfere. The losses are in the shared detector: whole against the row's own, swap 0.41 / 0.99, alternate 1.07 / 1.78, pattern -1.12 / 0.82, digest -1.51 / 0.68. The cause in alternate: at trust 2 or more, G, B, G, B moves the tally -1, 0, -1, 0 and never flips, so a detector reading flips goes blind. Plain at 1,000 s -0.14 [-0.23, -0.05], a fail. H1's premise holds where flips occur (`universal_sig.log`: goods before a flip, median, swap 4, alternate 1; share of flips contradicted, digest 0.78, unreliable 0.42, swap 0.06), but a detector built on flips needs them to occur, and the trust it sets stops them.

**H3, generate and test: fails, and why** (`lab/universal_gt.py`; `universal_gt1.log`, `universal_gt2.log`). A first guess at 1,000 s: alternate +3.46, digest +3.70, but plain -0.28 [-0.46, -0.14], patchy -0.55, weak -0.36, unreliable -0.32, swap -0.27. A fair search of 14 settings at 1,000 s on training seeds: alternate +3.02, digest +3.34, unreliable -0.23, weak +0.02, plain -0.02. The noise wall, in the effect and spread of one 32 s window (`snr`): alternate length 2, +32, sd 9.2, one window enough; digest's pause +32; plain pause -7.8 (3 windows); noisy eye level 2 -6.9 (6); swap trust 0 +6.2 (8); unreliable trust 3 +2.3 (83 windows, about 2,650 s); plain trust 3 +0.1. So two costs: trials come one at a time among 6 knobs (each tried about 1/6 x 1/2 of the time, some 400 s to find the right notch), and a single window's noise makes false keeps, which is the plain loss. This is a result about signal, not only about my design: the thin worlds are beyond any on-policy search in a life.

**H4, the bank of predictors** (`lab/universal_v.py`, class `V`). The insight came from H3's two costs: a vouched taste reveals the colour that was food whichever model is driving, so all candidates can be scored off-policy. Eyes and balance stay from `U`, since no taste can score them. First trace (setting 60; `universal_vdbg1.log`): selection right in every world; the cost is delay. Whole against parts: interference small (`universal_vparts1.log`). Whole setting v2 on validation seeds: thrusters 1.52, ageing 1.41, swap 0.80, alternate 1.85, pattern 2.02, digest 0.35, noisy 1.65, plain +0.01, 1,000 s -0.02 (`universal_vparts1.log`; tuning steps in `universal_vfocus1-7.log`).

**Choices and dead ends on the way to the final setting** (`universal_var1-5.log`, settings `universal_v2-v7.json`).

- *Default trust*: 3 is better in patchy, unreliable and digest (v3), where in `U` it blinded the detector. In the bank it doesn't, because detection no longer reads flips.
- *Bank size*: 2, 3 and 6 first. Sequences of 4 and 5 then gained only +1.37, +1.26 (`universal_unseen1.log`), so lengths 2 to 6 (bank 19): +3.69, +3.66. More rivals, more false picks.
- *The pause's staircase*: a fixed window can't fit digest 2 s. The first staircase ratcheted up with no way back, and a wide window starved the table of tastes. It became two-way, with the table's gate at the current length. It costs row 5: on validation seeds, no staircase digest +5.09 / +5.45 and digest 2 s +2.74 / +4.09 (100 / 400 s); staircase 1.25, up 0.03: +4.47 / +4.83 and +3.51 / +5.92. Chose generality.
- *A wrong suspicion of mine*: I blamed false pauses for the loss in thin worlds. Measured (`universal_var4.log`): bank and pause both off, unreliable +0.28 / +0.41; only the pause off, -0.07 / +0.06. So the rivals are the drag: two lies in a row give a trust 0 rival a hit while the default misses, and a threshold of 1 acts on it. Raised to 2.
- *A wrong prediction of mine*: that the higher threshold wouldn't cost swaps. It does: swap at 100 s about +0.7 at 1, +0.54 at 2, +0.33 at 3 (`universal_var5.log`). At 2: unreliable +0.20 / +0.30, patchy 0, weak -0.08 / -0.01, alternate +5.03 / +5.51, pattern +4.22 / +4.76, digest +4.61 / +5.01, plain +0.03 / +0.04.

**Two judges, so one seed set was not clean for the final setting.** I judged v5 (threshold 1, staircase up 0.1) on 55000-55063 x 2 (`universal_judge_first.log`), then changed the threshold and the staircase in response to its numbers and to the measurements above, so those seeds are spent. The final setting v7 was judged once on 55100-55163 x 2 (`universal_judge.log`), and not tuned after. Gain over base, v5 then v7, on different seeds, so roughly: swap +0.71, +0.47; unreliable +0.05, +0.12; patchy -0.09, +0.20; thrusters +0.84, +0.85; digest +4.66, +4.52; alternate +5.23, +4.92; pattern +4.43, +4.23. So v7 traded swaps and some of the sequences' speed for the thin worlds, which is what was meant for the swaps but more than I had looked for in the sequences, and I can't say it is better overall. Which is better depends on how those worlds are weighed.

**Combinations and variants.** Numbers in `STORIES.md`; logs `universal_combo2.log`, `universal_unseen2.log` (v7), `universal_combo1.log`, `universal_unseen1.log` (v3). Both on validation seeds, which chose settings on the single worlds, never on these. Removing each rival (`universal_unseen2.log`): trust 0 swap -2.21; length 2 alternate -0.78; length 3 pattern -0.30, not sure, since length 6 also fits; length 6 no sure loss in these worlds (only in sequences of 6). Removing a rival not needed in a world gains a little: alternate +0.15 to +0.19.

**Final trace** (`universal_vdbg3.log`, 100 s, training and validation seeds): share of time, first pick, in what share of lives. Swaps: trust 0 75%, 14 s, all; alternate: length 2 84%, 13 s, all; pattern: length 3 81%, 11 s, all; digest: default 96%, a rival picked in 44% of lives, first pause 9 s, in all, 89% pausing at the end; unreliable: default 95%, a pick in 42%; patchy 99%, a pick in 16%; weak 99%, 2%; noisy 100%, 1%; plain 100%, none, evidence all 0.0.

**Not traced.** Swap 10 s's shortfall of -0.54 against its row: time on the default explains perhaps half by a rough sum (about 25% of the life at about 0, against 1.05), and swaps paused falsely in 36% of lives, cost unmeasured. Swap 50 s's -0.29 [-0.48, -0.11]: nothing grew in those lives and 20% paused; trust 3 against the base's 1 is my guess, unmeasured. Noisy eye + thrusters at more than 100 s.

**Seen without a display, not on screen.** `lab/watch_universal.py` recorded 30 s of alternate, seed 56000, final setting (`universal_alternate_30s.png`): following length 2 with evidence 10, lengths 4 and 6 at 9 and 8, length 3 at 0, pause off, recent meals mostly alternating with slips. The creature view's "poison: blue" line is the body's own, and means nothing in a world with a rule. A bug on the way: `lab/blocks.py`, a one-off SPICE bench that runs on import, shadowed the project's `blocks` when `creature.watch` imported it, since `table.py` puts `lab/` first; the viewer now imports the project's first. `lab/watch_ladder.py` may share this; unchecked.

## D30: can the programme's analysis tell the truth? (2026-11-04)

Stage 1 of `PROGRAMME.md`, by an agent on invented data with known answers (`lab/synth_controls.py`, `lab/v/synth_controls.log`, seeded, 91 s; I re-ran it, identical but for timings). No creature was simulated. Truth labels are the agent's: K types with one cure each count as "no".

- **The primary result as first written fails.** Under fresh draws the "every world needs its own cure" control stays at the false-positive rate (0-16%), so it never reaches 80% coverage, and half its description is undefined. The computable substitute, 0.8N full-cost cures, gave a false yes in 100% of runs on every no-sharing population with K up to 100 and on Zipf 1.5, and 0% yes on a mix where 70% of worlds share cures; K=100 went from 0% yes at N=100 to 100% at N=300.
- **Coverage curves alone can't settle it.** 30 duplicate types and 30 cures shared across distinct worlds gave identical curves with opposite truths. Only an independent judgement of whether a challenge is new separates them. So the weak point is telling new from duplicate: false yes 0% up to a false-split rate of 0.3, 25-68% at 0.5, about 100% at 0.7; a signature that treats each gain value as new gives 100% false yes, one on the programme's skeleton none. Stage 2 must measure this on planted near-duplicates.
- **Proposed replacement** (not yet adopted): F_novel and R, wording in `PROGRAMME.md`. New cures per new world tracked 1 - F_novel at every mix (q 0: 0.995 / 1.000; 0.5: 0.520 / 0.505; 0.9: 0.107 / 0.103), so the 80% and the half reduce to one condition. At N=300, M=300, se 0.2: no false yes on any no-sharing population; yes in all runs for general cures with m up to 100 and q at least 0.7; in between at q 0.3, 0.5 and m=300. F_novel's apparent saving on no-sharing populations: +3.4% at most, its 97.5th percentile.
- **Saving from arithmetic alone**: written pool control 67-99%; Zipf frequency 33-98%; greedy concavity on the training curve 4-42%, and none on a fresh equal-frequency curve; one noisy look at own-cure worlds 71-98%, none with re-runs; motif plus a tuned parameter per copy 65-96%; compressor start-up without a reference corpus 51%. The critics' concern, concavity, is the smallest. Pool size, frequency and noise are the big ones.
- **Description length**: LZMA size, given a frozen corpus, of a canonical form (flatten, keep what connects to a port, parameters on a 5% log grid, names removed, distinct islands once with a count). Harder to game than a motif count: a huge rule scores 31288 against 23416 for the same 30 cures, where a count says 1 against 30.3. Copies cost 66-130 bits, not almost nothing (about 9 bits of true information), which errs against a yes. The reference must be frozen beforehand: padding "improves" a score relative to the circuit's own cure size. The vocabulary is invented; real circuits are untested.
- **Size**: about 225 worlds in the pool and at least 75 held out, se 0.2 per world; pairs per world (sigma / se)^2, with sigma unknown until stage 2. Lives limit detection more than worlds: noise drags a true q of 0.7 to 0.62 at se 0.2, and 75 to 300 worlds moves yes only from 10% to 22%.
- **A designer rule follows**: one measurement per world per cumulative circuit. Scoring each cure separately and counting a world if any passed gives 46-100% coverage from noise alone.
- **Can't be answered here**: the real sigma; whether real signatures separate new from duplicate; whether a corpus can be built from real cures; cures broader than their group; shifts away from the sampler's population. A "yes" means yes relative to one sampler.

## D31: the budget in bits, and the bank against an ideal selector (2026-11-04)

Stage 1b of `PROGRAMME.md`, by an agent; development seeds only (streams 60000-60399 x 2, tuning 61000-61063 x 2, judging 60000-60199 x 2). Scripts `lab/bits_bank.py`, `bits_record.py`, `bits_analyse.py`, `bits_family.py`, `bits_arms.py`, logs `lab/v/bits_*.log`; streams in `/home/pilgrim/nca-scratch-backup/bits/` (78 MB, out of git). Controls: recording leaves lives identical; the counter arm at the bank's values reproduces the bank exactly; replay reproduces its first picks. I checked the tables here against the logs and redid the limits below. Lives of 100 s only; nothing watched live; the Bayes arms are ceilings, not circuits.

**My premise was wrong: the bank isn't crude Bayesian model comparison.** Its floor at 0 makes entry a run detector (Page's CUSUM): at threshold 2, two straight wins on disagreements pick a rival, whatever came before. In unreliable, 66% of false picks went to a rival level with or behind the default over the whole stream; the median false pick had posterior 0.057 under a uniform prior.

**The budget, measured.** Bits per taste 1-H(e), e the chance a scored taste misstates the rule's food colour. (Digest's channel is lopsided: .53 a taste, 21.5 a life, told right against told wrong. Elsewhere the two agree within .03.)

| world | scored tastes | e | bits/taste | bits/life | first 10 s |
|---|---|---|---|---|---|
| plain | 63 | .025 | .83 | 52.4 [51.7,53.0] | 4.5 |
| swap10 | 60 | .027 | .82 | 49.1 | 4.4 |
| alternate | 60 | .029 | .81 | 48.2 | 4.1 |
| pattern | 60 | .026 | .83 | 49.1 | 4.3 |
| digest | 41 | .207 | .26 (.53) | 10.7 (21.5) | 1.3 |
| unreliable | 60 | .215 | .25 | 15.0 [14.4,15.4] | 1.3 |
| patchy | 69 | .119 | .47 | 32.6 | 3.1 |
| weak | 48 | .062 | .67 | 32.1 | 2.4 |
| noisy | 51 | .050 | .71 | 36.6 | 2.8 |

What limits it: the rate, about 0.6 scored tastes a second; attribution, all of plain's loss (2.5% of meals aren't the followed colour) and 12% in patchy; lies, .20 in unreliable and .19 in digest. Vouching costs almost nothing: all pulses with eye features give no more bits per second than scored signs. This is a ceiling on the evidence, not information gained: plain has about 1 bit to learn out of 52 on offer.

**Selection against the exact posterior over the seven.** Each model's prediction depends only on the past, so the policy's factor cancels and the posterior holds whoever drives. It says nothing of what a driver chosen for information could gain. Lies are stated as independent, which is false (disagreements come in runs). Fixed e and prior enter the MAP (the most probable model) only through k = log2(prior odds) / log2((1-e)/e): a rival must lead by more than k hits. Naming one of seven takes 2.81 bits with a uniform prior; with the default at 0.9, 5.9 bits for a rival.

False picks, bank against MAP k=1.5: unreliable .417 / .212, digest .531 / .383, patchy .114 / .083. At no more false picks, tastes to the right pick, ideal over bank: swap10 1.05 [1.03,1.07], alternate 0.78 [0.77,0.80], pattern 0.83 [0.82,0.84]. So entry wastes 0-22% of tastes; false picks are the larger waste. In swap10 the median evidence is 0 hits at 10 s: before the first swap the two worlds look the same to any brain.

**The rule, derived.** No lie rate gives +1/-3: independent lies give equal steps (±2 bits at e=.2, ±3.17 at .1, ±5.3 at .025). Measured against unreliable: trust 0 +1.97/-2.81, length 2 +1.63/-4.43, length 3 +1.64/-3.65, length 6 +1.73/-3.15 bits. So a +1 is worth about 1.7 bits; -3 is about right for sequence rivals and too harsh for trust 0. Thresholds 2 and 3 are about 3.4 and 5.1 bits, a default's prior of about 0.8, confounded with the loss ratio. **The -3 hardly acts on entry** (unreliable's false picks .422 at -1, .417 at -2 and -3); it works as an exit: pen 3 over pen 1 gains unreliable +.096 and digest +.048 and loses swap -.068, all sure.

**The threshold's trade-off is part floor, part intrinsic.** For trust 0 in unreliable (chance .228 on each of 12.2 disagreements), false picks at thresholds 1, 2, 3: with the floor derived .938, .392, .094, observed .785, .33, .09; without it derived .295, .087, .026. With the floor they grow with the life's length; without it they are bounded by (q/(1-q))^k. The rest is intrinsic: as k rises, swap's right pick comes at 13.1, 15.2, 18.7, 29.0 s while unreliable's false picks fall .449, .212, .119, .068.

**How much of the gap is inference?** Real lives, efficiency, judged on seeds apart from the tuning. Bold is surely above the bank; no Bayes arm is surely below it.

| world | bank | Bayes, one setting | Bayes, world's best | best model from birth | bank's parts, told | row's target | manual |
|---|---|---|---|---|---|---|---|
| plain | 2.62 | 2.63 | 2.62 | 2.63 | 2.76 | 2.77 | 2.64 |
| swap10 | 0.50 | **0.64** | **0.88** | 1.00 | 2.77 | 2.77 | 1.08 |
| alternate | 1.72 | **2.04** | **2.09** | 2.32 | 2.60 | 2.61 | 2.46 |
| pattern | 1.57 | **1.83** | **1.95** | 2.10 | 2.66 | 2.67 | 2.23 |
| digest | -0.31 | -0.29 | **-0.14** | -0.13 | 0.02 | 1.81 | 1.73 |
| unreliable | 0.48 | 0.46 | **0.55** | 0.55 | 0.75 | 0.80 | 0.64 |
| patchy | 0.70 | 0.67 | 0.71 | 0.71 | 0.81 | 0.85 | 0.82 |
| weak | 1.78 | 1.78 | 1.78 | 1.74 | 1.84 | 1.84 | 1.74 |
| noisy | 1.77 | 1.77 | 1.77 | 1.74 | 1.86 | not comparable | 1.80 |

One setting is the posterior-weighted vote (BMA), e=.2, default's prior .5. Losses, as steps along the row:

| world | crude inference (best per world: optimistic) | gathering evidence | model's learning or class | parts |
|---|---|---|---|---|
| swap10 | +.38 | +.13 | +1.77 | 0 |
| alternate | +.37 | +.23 | +.28 | 0 |
| pattern | +.38 | +.15 | +.56 | +.01 |
| digest | +.17 | 0 | +.16 | +1.79 |
| unreliable | +.07 | 0 | +.21 | +.05 |

The largest gaps aren't inference. Swap's +1.77 is measured against being told each swap, and no model in the bank predicts swaps. BMA beats MAP in sequence worlds because equivalent rivals pool their votes. Removing only the floor with +1/-1 is nearly the exact MAP: surely above the bank in swap (+.075), tied elsewhere, never surely below, and simpler. Not adopted: stage 3 tests the present circuit unchanged.

**These aren't yet the standard `AGENTS.md` sets.** The arms are ideal only among these seven models, with a stated likelihood. A Bayesian holding a changing-rule model hasn't been measured, so swap's +1.77 isn't shown to be beyond any learner: only beyond any selector among these seven.

**How wide a family can a life tell apart?** At the bank's rate of tastes, 5% error. Fano's upper bound on log2 N at 10 / 30 / 100 s: plain 5.8 / 16.8 / 56.2, unreliable 2.5 / 5.7 / 16.8, digest (at .53) 3.8 / 8.3 / 23.7, patchy 4.3 / 11.1 / 35.3, weak 3.6 / 10.3 / 34.8, noisy 4.0 / 12.1 / 39.6. It covers brains that experiment, since feedback doesn't raise a memoryless channel's capacity, but not information in timing. A union estimate of what a family reaches, pairs disagreeing on half of tastes: plain +0.2 / 10.8 / 48.5, unreliable -3.6 / -1.8 / +4.2. So each doubling costs about **1.9 s in plain and 11.8 s in unreliable** (`lab/bits_ceiling.py`, an estimate): a clean world can pay for a family of 1000 in about 27 s, a world with one lie in five can't in a life.

**A correction to the agent's report: "provably too short whatever the brain" is not proved.** Its Wald limits count tastes at the bank's 0.63 a second, but an unwired creature eats 145 a life (181 in the best), and more tastes are more evidence, bought with poison. At 1.45 a second (`lab/v/bits_ceiling.log`): the worst lie rate one pair can stand goes from .43 to .45 over a life and from .28 to .35 in the first 10 s, and the agent's rare-disagreement examples (101-121 s) take 44-53 s, inside a life. Even 1.81 isn't a physical ceiling, since a brain could chase blocks. What stands whatever the rate: a difference that doesn't show within the life carries nothing. Anything else needs a measured limit on meals before "provably".

**Corrections, the same day, on the user's asking whether anything needs repeating.**

- **The comparison above assumes the rule never changes.** Every "ideal" arm holds seven fixed hypotheses, so to it old evidence stays good for ever, and the bank's forgetting looks like waste. But a floor at 0 is Page's CUSUM, the standard test for a change at an unknown time, and a Bayesian who allows changes (Adams and MacKay's online changepoint detection, 2007) also discounts old evidence. So "not model comparison" is too strong: the bank may be a rough comparison that expects change. Not measured. None of the nine worlds has a rival that becomes right only part-way through a life, which is where the floor should pay, so "tied elsewhere" for no floor says nothing about such worlds. "False picks are the larger waste" and "crude inference" hold only for a rule that doesn't change.
- **"Simpler" and "removes parts" were my words, and unsupported.** The no-floor arm's counter has no lower limit in the simulation (`floor = -1e9`). A real one needs a range, so more state, not less. It drops a number from the rule's description, nothing more, and no parts were counted.
- **My 1.45 tastes a second is not measured either.** It counts an unwired creature's meals, not tastes it could use, and assumes the bank's lie rate; a creature following no colour may credit tastes worse. It shows only that the bank's rate isn't a limit. The Fano and union figures above are at the bank's rate too.
- **Unlearnable worlds:** I proposed leaving them out of F_novel, which contradicts `GRAMMAR.md` (How worlds are judged): they stay, as a test of doing no harm. Proposal withdrawn.
- **A gap this exposes:** a pass is measured against a policy told the rule, which a learner may be unable to reach. In unreliable the bank closes (.48-.24)/(.80-.24) = 43% of base's gap to told, though the world's best Bayesian arm only reaches .55. Worlds like this could produce a false "no". `lab/synth_controls.py` has no such worlds, so stage 1 didn't test it.

## D32: what stage 1b assumed, repeated (2026-11-05)

Stage 1c of `PROGRAMME.md`, by an agent, predictions written first (`lab/v/stage1c_predictions.md`). Fresh development seeds 62000+, tuning 61000+. Scripts `lab/stage1c_*.py`, logs `lab/v/stage1c_*.log`, large files `/home/pilgrim/nca-scratch-backup/stage1c/`. I checked the tables below against the logs; I did not re-run the lives, though the restart of the `hmm` job reproduced all 52 finished lines exactly. Ceilings and the existing bank only; nothing watched live.

**A run nearly lost to threads.** Each pool worker started 8 BLAS threads on 8 cores (load 55): the same 8 lives took 72.3 s against 1.4 s with one thread, identical results. It cost most of a night (`AGENTS.md`, Long runs, now has the rule).

**Replication.** Signs and budget replicate. Bank: swap10 .50 (.50 in D31), alternate 1.56 (1.72), pattern 1.46 (1.57), unreliable .52 (.48). False picks: unreliable .448, digest .529, patchy .099. Bits a life within 3%. 8 of 45 D31 cells fall outside the new interval, the largest about 2 standard errors of the difference (an estimate). **1b's headline BMA arm rested on a tie:** at prior .5, exact ties are settled by rounding, and alternate gives 1.93 or 2.22 by the tie's direction (2.02 as run). Any Bayesian reference must state its tie rule.

**"The bank is a rough comparison expecting change" fits its picks.** MAP over the seven with fixed share at h=.1 a taste, e=.2, prior .5 matches the bank's false picks within intervals in all six default-right worlds (unreliable .421 [.386,.459]); false picks grow with life alike (33/66/100 s: bank .20/.34/.45, fixed share .23/.34/.42, stationary .18/.21/.22); it picks in 86% of the bank's false-pick lives in unreliable (phi .81), the stationary learner 44% (phi .47). Three parameters against about nine numbers, so a description, not an explanation. The worlds themselves don't favour that hazard: h=.1 costs 3.4-4.7 bits a life in swap10, alternate and pattern, and almost nothing elsewhere, and gains up to 3.3 in mid-life worlds. So D31's "not model comparison" was too strong, as its correction suspected.

**The floor, among counters** (each cell the arm minus the bank, whole-life efficiency, each world equal):

| arm | stationary (9) | after plain (9) | mid-life with lies (6) |
|---|---|---|---|
| +1/-3 no floor | +.002 [-.011,+.015] | -.105 [-.124,-.086] | -.156 [-.188,-.125] |
| +1/-3 floor -3 | +.005 | -.098 | -.123 |
| +1/-1 floor 0 | +.001 | +.014 | -.063 |
| +1/-1 no floor | +.019 | -.050 | -.103 |
| stationary BMA | +.095 [+.072,+.119] | +.074 [+.055,+.093] | -.057 [-.098,-.017] |
| fixed share | +.095 [+.071,+.119] | +.080 [+.062,+.099] | -.031 [-.072,+.007] |

**What this does and doesn't show.** Among counters the floor surely pays once a rule starts mid-life, and it costs nothing measurable in the stationary worlds; D31's "no floor is tied elsewhere and never surely below" held only in stationary worlds. The bank has the smallest state of the counters (3.5 bits a rival, against 4.9 and 6.2 with no floor), and a floor at -3 gives nearly all the gain back. **But it doesn't show that forgetting pays.** A vote that never forgets surely beats the bank after plain, except on one permanent swap (-.091), and allowing change adds only about .006 to it there (.026 with lies), in overlapping intervals (not a paired test). So the floor's gain may be mostly undoing its own -3, and my "the bank's forgetting pays" to the user was too strong. Cause inferred, not measured; ablating rivals would test it. Parked in `QUESTIONS.md`.

**Swap's gap is about when, not whether.** Told minus 1/0 from birth is +1.74 in swap10. Each learner ideal only among its stated family:

| swap10 learner | prior bits on the truth | efficiency | share of the gap |
|---|---|---|---|
| two-state HMM, rate and e tuned here | 1.0 | 1.14 | 4% |
| period and phase known | 1.0 | 2.68 | 93% |
| 4 periods | 3.0 | 2.51 | 83% |
| 64 periods | 7.0 | 2.36 | 75% |
| 64 periods, 16 phases | 11.0 | 2.02 | 55% |
| 393 periods, 16 phases | 13.6 | 1.87 | 46% |
| the same, with HMMs and the seven | 15.2 | 1.70 | 37% |

So D31's "beyond any selector among these seven" stands, and it isn't beyond a learner: about 14 bits of hypothesis buys half the gap, across periods (the widest family: swap7 1.92, swap20 2.00), while one period alone fails off its period (T=10: -1.93 in swap7). Breadth costs elsewhere (widest against the bank: unreliable -.33 and patchy -.09, surely; alternate +.40 and pattern +.12, surely). The prior bits leave out the choice of family. A rate-only HMM's best rate was 5x the true one, since it is misspecified.

**The limit on tastes.** The only unconditional bound is the simulator's: one pulse a tick. **The body has no firing cap.** Proved, in expectation, for still, uniformly respawning blocks, given a cap: at most 1.447 mm of mouth path a firing, at least 1.77 mm a meal, so 82 meals a second at 50 firings a second per thruster (`lab/v/stage1c_limit_bound.log`); it is loose. Measured: oracle 5.8 meals a second at that cap (not optimal: 10.8 at 100, 9.9 at 400), unwired 1.47, bank .77. Through the wires alone an eat-most policy gets 5.5 tastes a second at 395 firings a second, worth 2.44 bits a second in plain against the bank's .58, .74 against .14 in unreliable, and .03 against .28 in digest, where eating faster destroys the signal. The wires' bits are measured by a table decoder assuming independent tastes. **What survives of "too short for any brain":** a difference that doesn't show within the life; a pair below 3.8e-4 bits a taste (lies above .494 on every taste), given the taste is the only wire about the rule, independent lies, and the tick limit; digest's one informative taste a second. **What falls:** every limit at .63 a second now reads "at that rate", including D31's "one lie in five can't afford a family of 1000": at 3.4 s a doubling (estimate), about 49 s.

**The pass rule** (synthetic, ceilings invented; Yes/No at N=225, capped share .25, unlearnable .1, se .2):

| truth | told | reference | reference + floor |
|---|---|---|---|
| q=0, M=75 | 0/1.00 | 0/.92 | 0/.96 |
| q=1, M=75 | .02/0 | .92/0 | .89/0 |
| q=.85, M=75, no capped worlds | .04/0 | .54/0 | .56/0 |
| q=1, M=36 | .04/0 | .58/0 | .54/0 |
| q=.85, M=75, se .1 | 0/0 | .97/0 | .90/0 |

So the bar I feared would give a false no does something else: against a told policy, a yes is nearly unreachable and truly general cures read "in between". Against a reference alone, one cheap half-working cure games it at fine measurement (false yes up to 57% at se .1 and a weak reference); with the floor, at most 4%. Adopted in `PROGRAMME.md`. Remaining weakness: q=.7 never reaches yes under any definition, and at M=36 and se .2 even q=1 reaches yes only about half the time, so the outside set's verdict needs about se .1, four times the lives per world.

**Doing no harm.** In a coin-flip-taste world a meal is worth -.5: never moving scores 0, base -2.27 [-2.37,-2.16], bank -2.08, unwired -3.43, an ideal stopper (among rule or coin) -1.23. The stopper stops in every alternate life (-1.45), since its family lacks sequences, so a brain may not cheaply learn to quit. Standing still would pass a gap measured from base (alternate .55, pattern .50, digest .99 against told parts), so gaps are measured from the larger of base and 0.

**Predictions:** failed P2.4, P3.3, P3.6, P4.5, P5.2, P5.3; the rest held or partly held. **Bugs:** attribute collisions with the base brain, caught by controls; `np.digitize` in `stage1c_limit.py` when an eye never pulsed; a first gaming test where base shared the design's half-working cures (`lab/v/stage1c_synth_gaming.log`, superseded by `gaming2`, `gaming3`). The mid-life onsets are the agent's choice and all start cleanly.

## D33: a language for worlds, and an engine proven against the unmodified one (2026-11-06)

Stage 2a of `PROGRAMME.md`, by an agent, predictions first (`lab/v/stage2a_predictions.md`). Package `lab/stage2_lang/` (a world is an S-expression over a written vocabulary of about 110 words, compiled to Python; description length is LZMA of its canonical form against a frozen corpus, SHA `3f31af44`); scripts `lab/stage2_*.py`; logs `lab/v/stage2_*.log`; lives `/home/pilgrim/nca-scratch-backup/stage2/`. `world.py`, `creature.py`, `discrete/model.py` and `lab/universal_v.py` unchanged. Development seeds 63000+, hand-picked worlds: engine proving, not a result. I checked the numbers below against the logs; I did not re-run them.

- **Identity and reproduction, exact**: with no rule, 100 lives each of base, bank and told match the real `Life` tick by tick (body, blocks, the light at the eyes, every pulse and taste with its moment, the body stream's final state); the nine worlds and seven more (coin, allfood, scarce, moving, three mid-life) match the existing wrappers in all 57 rows of 100 lives (`lab/v/stage2_repro.log`).
- **Each world against its description**: 45 checks, each recomputing the rule from the trace by its own code; strict three-wire brain, same seed same life in any order or process, a taste's moment carries nothing of its sign, pulses uniform within a tick (`stage2_checks_general.log`, `stage2_checks_worlds.log`).
- **Mutation**: 54 of 54 broken world rules and 15 of 15 broken engine parts caught, after the first round's three misses were fixed (`stage2_mutate_first.log`, `stage2_mutate.log`). The checks and the reference loop are the engine author's own, so the "2 to 3" gate's independent check is still owed (stage 2b).
- **Labels in bits** (`stage2_labels.log`): 7 worlds with nothing learnable (A), one scarce (sag, B), 32 ordinary. The evidence measure says a world differs from plain, not that a usable rule exists (bruise reads ordinary at e .46); with each life's real spread instead of Poisson's, drag2 and moving fall below Wald's 3.82 bits. Description lengths run from about 100 to over 400 bits (median), against about 50 bits a life: no world here is learnable from nothing within a life, so every pass relies on what the brain already holds.
- **The bank, 50 pairs** (`stage2_report.log`; x against told only): passes alternate .55, pattern .53, noisy .64, late_alternate_50 .57; not swap10 .22, unreliable .38, digest -.27, parity -.45, region -1.99. x is meaningless where the gap is about 0 (allfood, rarefeast, keylock, word read "pass"): stage 2b's reference must set which worlds have a gap. **Cells** breaks the bank (-41.6, sigma 93): unexplained, kept out until looked at. Doing no harm can't be shown at 50 pairs (coin, rarefeast lower bounds -.12, mirror -.19); it needs about 200. Mirror's bank-base -.17 in one pairing is unexplained.
- **Cost**: rules take 0-6% of a life (moving 57%); a life 0.15 s on one core, 14.7 a second on 7 workers; sigma of a pair median .42 (base), .48 (bank); se .1 in efficiency needs a median 23 pairs, in x 59, so 300 worlds cost a circuit about 0.3-0.7 h. No need for numba.
- **Catalogue**: of `GRAMMAR.md`'s 174 ideas 168 compile and run, 147 plainly; 6 can't be written (a mouth offset; five need writes to a brain's memory). Compiling proves a program runs, not that it means the idea.

**At a finer step the unmodified world moves** (`stage2_finer.log`, 50 pairs): halving the tick to 5 ms shifts plain by -.17 [-.33,-.00] (base) and -.22 (bank); digest +.56 and +.31, bruise -.60 and -.40, keylock -.26 and -.61; swap10, blind, noisy hold. The real `creature.Life` at 5 ms gives the same lives as the engine (60 of 60, `lab/stage2_finer_ref.py`), so the move is the existing body and model's, not the language's. The check halved the tick everywhere: the body's and the brains' alike, since the block model and the bank also step once a tick (the circuit is integrated finer only in `mixed_feedback.py` and ngspice). Possible causes, untested: the body takes motor beats only on tick boundaries (`creature.py`, a tick's beats fired together, so a pair in one tick cancels exactly), and the circuit's turning relies on a partner beat "a tick late" (D24); or the model counts pulses and makes beats only per tick. Halving one tick and not the other would separate them. That would break "nor may the simulator" (no outputs only on tick boundaries) for every result in the fast model, not just this programme's. Fixing it changes the body, so it is the user's (`QUESTIONS.md`). In plain, bank minus base is unchanged (+.03, -.02), so comparisons may hold where levels don't; stage 3's headline is to be repeated at 5 ms.

**Predictions that failed:** P1.1, P1.3, P2.3, P4.3, P5.1, P6.2-P6.5 (see the file); the main surprises were exact reproduction first time, cheap rules, and plain moving at 5 ms.

**The independent check** (a second agent, which didn't read the builder's checks; seeds 64000-64549; predictions first, `lab/v/stage2_indep_predictions.md`; scripts `lab/stage2_indep_*.py`, logs `lab/v/stage2_indep_*.log`). I checked its summary lines against the logs.

- **Identity holds**: with no rule, 100 lives each of the base model, story 1's circuit and the bank are identical to `creature.Life` in every tick and every brain call (about 64,000 pulses, 7,500 tastes and 350,000 firings each), while three planted mutants were caught (`stage2_indep_identity.log`).
- **16 worlds do what they say** (the nine, coin, two mid-life onsets, every5th, blind, crosstalk, region; 200 lives each; `stage2_indep_worlds.log`): no disagreement in a tick with one meal; unreliable lies .199, coin .499, weak passes .251, crosstalk 1.000 of own + .3 of other. Two small ones: with two meals in one tick, both are judged by the rule's state at the tick's start, as the old wrappers did (about 1% of meals in alternate, pattern, every5th); and digest's 1 s edge falls to floating-point rounding (2 of 31 meals at exactly 100 ticks).
- **Fails: the language can reach the brain.** `bp` and `bpget` read and write the brain's own parameters, and nothing refuses a world using them (sag does: the brain's hold halves at 50 s), so a world could write the answer into the brain. Sag is not a world but a change to the brain, and is out until rewritten.
- **Fails: the stage-5 guard goes by marks, not by what a world does.** Unmarked copies of four stage-5 worlds are refused, but not a taste of 0 or of ±.5, a score that contradicts the taste, or a liar without its mark; and two of the three ways to run a life skip the guard (`stage2_indep_attacks.log`).
- **Partly fails: description length isn't invariant to rewrites that keep the meaning.** Renaming, comments and layout change nothing, but reordering `let`s moves parity by 128 bits and an added "+0" costs 40. Two programs with identical lives can differ by 64 bits (halfthrust), and never (a rule that never acts) costs 464 bits against plain's 0. The ranking is sensible (plain 0, costly 104, swap10 280, alternate 296, pattern 520, parity 1152, cells 1800), but as a measure it is an upper bound on a program's length, not on a world's: near-duplicates must be judged by their lives, not by their text (`stage2_indep_dl.log`).
- Call order leaks a little: injected pulses come first in their tick (0.85% of noisy's pulses given away), and in plain the colour-0 eye is always called first, which is `creature.Life`'s own.

So the engine is proven; the language's guard and its description length are not. Stage 2b fixes both before anything is built on them, and the checker re-runs its attacks.

## D34: the reference, random worlds and near-duplicates (2026-11-06)

Stage 2b of `PROGRAMME.md`, by an agent, predictions first (`lab/v/stage2b_predictions.md`); development seeds 65000-66399; scripts `lab/stage2b_*.py` run by `lab/stage2b_queue.sh`; logs `lab/v/stage2b_*.log`; lives and a copy of stage 2a's language in `/home/pilgrim/nca-scratch-backup/stage2b/`. I checked the numbers below against the logs, and re-ran one (never) myself.

**The language mended** (`stage2b_guard.log`, `stage2b_dl.log`, `stage2b_repro.log`). `bp`/`bpget` are gone, and compiled code is checked against a list of what a world may touch, which never includes the brain; sag is retired (the hold is the brain's own number). The guard now goes by what a world can do: statically (a taste other than a literal ±1, a dropped or injected taste, ending a life, rewiring, a score that breaks the meal's sign), and in every tick of every life, however run: the taste must equal that tick's scored meals, clipped to ±1. All 16 of the checker's attacks are handled (12 refused, 4 honest). Not decidable from the text: a see or fire rule that swaps channels from some moment on imitates a rewiring and is accepted. Digest as written in 2a disagreed with its own score in ticks with two meals (refused in 20 of 80 lives) and was rewritten at the meal. Description length now uses a normal form (constants folded, rules that never act within 1000 s removed, single-use variables inlined, lets ordered, commutative operands sorted); every rewrite the checker tried now costs nothing (never 0 bits, swap10 296 however written), and 1560 of 1560 lives are unchanged. Left: two programs with identical lives can still differ (halfthrust 216 against 152 bits). Identity re-run: 300 of 300 lives identical to `creature.Life`.

**The frozen reference** (`lab/v/stage2b_reference.md`, hashed before use): D32's widest learner, 12,591 hypotheses (the seven, 8 HMMs, 393 periods x 16 phases) at 2.3 to 15.2 bits each, independent lies at e .1; ties keep the colour already followed.

**100 random worlds** from a generator frozen and hashed before drawing (`lab/stage2b_gen.py`, `lab/v/stage2b_random.log`; 60 pairs each): 12 nothing learnable (A), 25 too little evidence (B), 63 ordinary. **38 of 100 [.29,.48] have a gap**, but the told arm runs .07 [-.02,.18] above base in plain itself, so most gaps of .1 to .3 are the told arm's own edge: 14 have a gap of .3 or more. **The reference surely closes over .25 of the gap in 3 of the 38** (alternate, drawn twice, and g57); fixed swaps reach r .25-.31; worlds of satiety are negative for both. So most of what random worlds ask is outside every hypothesis a colour-choosing learner holds: what a world asks and what any of our learners can imagine are far apart.

**Cells, traced**: its respawn could put an eaten block back under the mouth, and the body counts a meal at any forward speed; the bank, coasting after a poison, ate the same block every tick, up to 9,513 meals a life. With the respawn kept clear, bank +.37 against base +.49 (`stage2b_cells.log`).

**Near-duplicates** (`stage2b_neardup.log`, 200 pairs): rewritten pairs are identical or within .005 bits a life; a 10% nudge to swap's period separates at .19 bits a life under base (about 20 lives); unreliable .2 against .22 at .069 under the bank (about 55); poison flipped for 0.1 s at 50 s costs the bank -.65 (2.3 bits a life); a swap moved 5 ticks is indistinguishable. A policy ignoring taste can't see a colour rule at all, since a seed's two lives cancel. Proposed rule: two worlds count as one if their normal forms match, or if under base, bank and reference their outcomes differ by under 3.82 bits over the lives a world is judged on.

**Sigma and cost** (`stage2b_random.log`, `stage2b_cost.log`): a pair's sigma median .43; se .1 in efficiency takes a median 18 pairs (28 for bank minus base), but in x about 2,200, because most gaps are small: x is only usable where the gap is large. A life costs about .42 s at 10 ms and 100 s; on 4 lives each, about 6x that at 1 ms and 8x at 1000 s (the reference about twice the bank).

**Doing no harm** (`stage2b_noharm.log`, 200 pairs, seeds 65600-65799): shown for coin, mirror, allfood and costly; not for never (-.13 [-.21,-.06]) or rarefeast (-.17), though never's lives are identical to plain's. Re-run by me on 400 fresh pairs (`lab/stage2b_plain_harm.py`, seeds 66000-66399, prediction written first: plain -.03): **plain +.013 [-.039,+.066], rarefeast +.058 [-.012,+.130], no harm in either**. So the first was seed luck among six tests, and a single 200-pair interval is not enough to call harm: a failing world is repeated on fresh seeds before it counts.

**Counted in ticks, not seconds** (they change meaning at 1 ms): in the engine, motor beats only on tick boundaries, one clipped taste a tick, the mouth's sweep one segment a tick, deferrals rounded to ticks, injected pulses first in their tick; in worlds, `(chance p)` redrawn every tick and rates capped at one event a tick; in the brains, the block model counting pulses and deciding once a tick, its lone beat and partner beat a tick late (D24), the reference re-reading the clock every 5 ticks.

**Predictions that failed:** P1.4, P3.3, P4.2, P4.3, P5.1, P5.2.

**The 1 ms re-validation, tried on plain** (the user's rule, 2026-11-06; mine; the whole tick halved everywhere, as D33; 100 pairs each). On seeds 66400-66499 (`lab/stage2_converge.py`, `lab/v/stage2_converge.log`), base falls from 10 ms by -.16 at 5 ms, -.27 at 2.5 ms and -.25 at 1 ms, so it settles; the bank by -.27, -.31 and -.50, so at 1 ms bank minus base is -.20 [-.29,-.11]: harm, where at 10 ms it was +.05. I predicted a steady fall for both (-.17, -.25, -.30), wrong for the bank. On fresh seeds 66500-66599 (`lab/stage2_converge_bank.py`, `lab/v/stage2_converge_bank.log`) the bank falls -.33 [-.45,-.22] and base -.26 [-.37,-.15], so the bank's extra fall is about -.07 here against -.25 before: real, perhaps, but its size is uncertain to about .1. Switching off each of the bank's parts in turn (the pause, jitter, the eye filter, the bank's rivals, trust) changes neither level nor fall (all -.33 to -.35): in plain those parts hardly act, so the extra fall is not in them; it is in what the bank shares with its base class. My prediction (the pause) was wrong. The told arm falls least (-.19).

So: a 10 ms number for these brains is biased by about -.25 to -.33 in level, the same for all within about .1, and the arm-specific part is not yet traced. That is the size of doing no harm's bar, so a no-harm verdict at 10 ms is provisional until re-validated at 1 ms, as the user's rule requires for final results anyway.

**The language attacked again** (the independent checker, seeds 64550-64713; `lab/stage2_indep2_*.py`, `lab/v/stage2_indep2_*.log`; I checked the summary lines). **Identity holds** (300 of 300 lives on fresh seeds). **No world text reaches the brain** (21 attempts), but the bank arm's `spy` evaluates a `told` that draws inside the brain's taste call, shifting the world's stream: 36 of 40 lives differ from `universal_v.V` with such a world, so an arm's lives depended on its instrumentation. **The guard still fails**: refused now are an inverted taste, lost tastes, a zero-amount meal and a negative COST, but accepted, in 80 of 80 lives each, are rewiring from 50 s (by a see, a look or a fire rule), a life ended (the body frozen after the first poison), a poison block hidden on contact and put back under the mouth 1 s later, verdicts swapped or hidden in ticks with several meals (the clipped taste hides them), worth decoupled from taste (food worth 1e-6), and COST changed at 50 s, which the score applies to the whole life. A rule hitting 1/0 crashes the life instead of refusing it. **Description length**: 12 of 20 new rewrites that keep lives identical still move it, by -40 to +56 bits; and two normalisations are unsound: a variable read from `speed` is inlined past writes to the velocity, and sorting commutative operands merges the order of random draws, so two worlds with different lives can share a normal form.

What this says: policing a language by its text can't work, since whether two programs behave alike is undecidable in general; the honest designs are (1) the interface enforced by construction: each meal its own taste at its own moment, its sign the sign of its worth, the score from meals and a cost fixed at birth; (2) the stage-5 kinds (rewiring, a life ended, delay) detected by instruments on the lives and labelled, not refused by the text; (3) description length an upper bound, its normal form kept only where its lives are identical, its slack (about ±50 bits) stated. Rewiring by a see rule is, to a brain, the same as a colour swap; where it belongs is the user's (GRAMMAR, decision 1).

**Stage 2c, the fixes** (begun by the agent, finished by me after the user stopped sub-agents; `lab/stage2c_*.py`, `lab/v/stage2c_*.log`, predictions `lab/v/stage2c_predictions.md`). The interface is now by construction: a world writes only a meal's worth (its taste is the worth's sign, each meal its own taste at its own moment), COST is fixed at birth, a per-tick draw must be written as a rate; all of the checker's taste, score and brain attacks no longer compile. Instruments on the lives label rewiring (eye: 80 of 80 lives of each see or look attack; motor: 79 of 80), a life frozen, and a block put back under the mouth (80 of 80 of the delayed taste); false labels on the hand worlds: 3 of 3120 lives (mirror 1, fail50 2), and cells, which really does both. With the conversion switched off, every life is still identical to `creature.Life` (`stage2c_identity.log`). The conversion to seconds at 10 ms moves every level, by -.17 to -.39 in most of the nine and up to +1.06 (digest's base), so the 10 ms tick was coarse for the old loop (`stage2c_nine.log`).

The user's decisions (2026-11-06): no in-life change to the brain or the brain-body link yet, so rewiring by any route and fail50 (a thruster failing at 50 s) are out, labelled; and a world's description length judges nothing (near-duplicates by their lives; a world's size reported as the generator's count of blocks), so the normal-form work stops here.

**The engine made faster** (2026-11-06, the user's request; mine). A 100 s life at 1 ms took 3.3 s (base) and 3.7 s (bank) on one core; now 0.45 and 0.49 s, about 7x (10 ms: about 6x), with the instruments off for vetted hand worlds (`sim.WLife.instruments`). How: the per-tick numpy calls on two-element vectors became plain floats; the brains' once-a-tick chain of Python steps is one numba function (`lab/stage2_lang/fast.py`), its state in arrays, the Python taste code unchanged and synced around each taste; the tick's light, draws, beats and motion are compiled (`sim._step_fast`, `_step_fused`), calling numpy's own C draw function so the random streams are numpy's; and the float modulo is skipped where the value is already in range. Proof: every life identical to the uncompiled engine, in both modes, at 10 and 2.5 ms (288 of 288, `lab/speed_fingerprint.py`), and the fast path identical to the ordinary path in all 39 livable hand worlds (624 of 624, `lab/speed_crosscheck.py`). To keep it maintainable, `fast.py` holds a hash of each Python step it copies and refuses to run if any has changed, or if a brain has a step it doesn't copy; `_step_seconds` stays the reference. Scripts `lab/speed_profile.py`, `lab/speed_bench.py`. Also found: the instruments' per-tick record held about 1 GB a worker at 5 ms (the halving's first run died of it), and a pool recycling its workers hung for an hour.

**Halving the step** (`lab/stage2c_steps.py halve`, `lab/v/stage2c_halve.log`; six worlds, base and bank, 10 ms to 0.625 ms, 100 pairs a step on fresh seeds, before and after the conversion to seconds). (1) **Both loops reach the same limit**: at 0.625 ms the tick-locked loop and the loop in seconds agree in every world and arm within noise (plain base 2.45 and 2.44, bank 2.41 and 2.38; alternate bank 1.61 and 1.66; digest base -3.88 and -3.69), which is what a correct conversion must give, since the old loop's coarse parts (beats at the tick's start, one Euler step, one clipped taste a tick) vanish as the tick shrinks. (2) **The conversion bought most of the convergence**: at 10 ms the old loop was off its finest value by up to .8 (digest base -.77, digest bank -.34, plain and swap10 base +.21); in seconds, base is within .15 at 10 ms in all six. (3) **The bank still moves**: in seconds, at 10 ms it is .15 to .38 below its 0.625 ms value (alternate -.38, unreliable -.19), and in alternate it was still rising at the last halving (+.21 [+.06,+.36]). What remains counted once a tick in the bank (seconds.py): its outputs for a tick decided at the tick's start, so a taste acts from the next tick, and its slow nodes decayed per tick. (4) At 100 pairs a step the difference between steps has a 95% half-width of about .1 to .25, so the rule (two halvings within .05) can't be met at this size: my prediction C5.1, right. Being repeated on alternate and plain at 400 pairs, down to 0.3125 ms (`lab/stage2c_converge2.py`).

**It settles** (`lab/stage2c_converge2.py`, `lab/v/stage2c_converge2.log`; seconds mode, 400 pairs a step, seeds 68000-69599). The bank in alternate: 1.44 at 2.5 ms, 1.49 at 1.25, 1.53 at 0.625, 1.52 at 0.3125 (successive differences +.05, +.03, -.01, each about ±.09); bank minus base 4.39, 4.45, 4.50, 4.51. Plain: base 2.42, 2.39, 2.41, 2.41; bank 2.39, 2.36, 2.38, 2.40; bank minus base -.03 throughout. So the earlier rise to 1.66 at 0.625 ms was 100 pairs' noise, and my prediction (still rising) was wrong. In seconds, every quantity here is within about .03 of its finest value from 1.25 ms, and within .08 from 2.5 ms; at 10 ms the bank reads up to .38 low. So the one-tick delay of the bank's reaction (its taste acts from the next tick) matters at 10 ms but not below about 2 ms, and needs no fix for now. Fine enough, for this body (fastest time constant 20 ms) and these brains: about 1.25 ms, a sixteenth of the body's fastest time constant, with results reported at 10 ms read as provisional. The strict rule (two halvings with 95% intervals inside ±.05) would need about 600 pairs a step.

**The third independent check** (an agent, seeds 69600-69999, its own instruments; `lab/stage2_indep3_*.py`, `lab/v/stage2_indep3_*.log`, predictions first). It finished one of its five checks before its speed-up run filled the memory (my design: the instruments' per-tick record at 1.25 ms on seven workers), so checks 1, 2, 4 and 5 rest on its reading of the code, which I then tested. **Holds**: every one of about 1.6 million beats fires its thruster at its stated moment; the body's motion matches the exact exponential solution within 7e-15; every meal with a worth gives exactly one taste, of its sign, at the meal's moment. **Found, and fixed by me** (2026-11-06):
- *A world could reach the brain on the fast path*: `(pulse k)` took any integer, and the compiled brain adds the pulse to its state at 26 + k, so `(pulse -1)` wrote its record of whether it was driving (confirmed: 200 ticks ran, no refusal). Now an eye or thruster named by a rule must be 0 or 1, or the world is refused.
- *Meal moments early*: where the mouth's closest point fell past its segment's end, the engine went back from the clipped point, so a meal's moment (and its taste's) came up to a tick early: mean 3.0 ms at 10 ms, 0.6 ms at 1.25 ms. Now the first point within reach is solved exactly. In the reference engine itself, not only the fast path.
- *Deferrals from a meal broken*: one due in the tick's last stretch was lost (15 of 69 `(after 0.0005 ...)` ran at 10 ms), and one due before the moment already reached ran with time going backwards, the body moved twice over the overlap; and deferrals from the tick stage due later in the tick ran at the next tick's start, or, if pending, all at the tick's start. Now each runs at its own moment, never before the moment reached, nothing added late is lost. Also in the reference engine.
- *The fast path*: it raised an error instead of drawing in Python when a pulse rate was 10 or more a tick (now draws in Python, numpy's own, before any compiled draw); it chose the fused tick by the text "(thrust" or "(after", which "( thrust" passes (now a pattern); and its guard didn't hash the pulse methods it stands in for (now it does).
- *What a firing costs* (the checker queried both cases): the user's decision (2026-11-06): a thruster costs when it fires, whoever made it fire (a world's late or spurious thrust is the creature's own thruster firing), and a command the world drops costs nothing, the break being between brain and thruster. That is what the engine already did; I had briefly changed both (pushes free, drops charged) and changed them back before stage 3's lives.
- *Not fixed, measured*: the mouth's path between events is taken as a straight chord, so when translation and turning cancel a block the true path reaches is missed until the next tick: 2-3% of meals at 10 ms, about 1% at 1.25 ms; it vanishes as the step shrinks, as D34's halving requires.
After the fixes: lives in the tick-locked mode unchanged (144 of 144 of the fingerprint); 24 of 144 in seconds mode changed, as they should; then the fast path identical to the ordinary one again (288 of 288, `lab/speed_fingerprint.py`; 624 of 624 in all 39 hand worlds, `lab/speed_crosscheck.py`). The checker's own seconds test re-run after the fixes (`lab/v/stage2_indep3_seconds_after_fixes.log`), before and after: meal moments' mean error against the true path 3.07 -> 0.81 ms at 10 ms and 0.58 -> 0.01 ms at 1.25 ms (what remains is the chord's: 2.6% and 0.7% of meals a tick late); deferrals run 22,414 of 26,799 -> 26,796 of 26,796 at 10 ms and 6,293 of 7,828 -> 7,871 of 7,871 at 1.25 ms, none early, the latest by at most one tick. D34's halving and settling were measured before these fixes; repeated at 400 pairs after them (`lab/v/stage2c_converge2_after_fixes.log`, the same seeds): every value within .01 of before (the bank in alternate 1.45, 1.49, 1.53, 1.52 from 2.5 to 0.3125 ms; plain flat), so the settling by about 1.25 ms stands.

## D35: stage 3, the present circuit on fresh random worlds (2026-11-07)

`PROGRAMME.md`'s stage 3: the bank (`lab/universal_v.py`, `lab/v/universal_v7.json`), unchanged, on worlds from `lab/stage3_gen.py` (stage 2b's generator in the stage-2c language, the body fixed from birth by the user's rule; frozen, SHA `a24140a7`, before any draw), development world numbers and seeds 80000-89999 only; in seconds at 1.25 ms (the reference at 2.5 ms, on worlds with a gap only, the user's decision). `redo`: stage 2b's 100 draws again; `fresh`: 200 new ones, the coverage set. Scripts `lab/stage3_random.py`, `lab/stage3_summary.py`; logs `lab/v/stage3_*.log`; lives `/home/pilgrim/nca-scratch-backup/stage3/`. Rules fixed before the lives: a world is out (stage 5's kinds) if 3 or more of 16 labelling lives carry a stage-5 label; a world has something to learn if told minus max(base, 0) is at least .1 with its 95% interval above 0; it passes if x > max(.5 r, .25).

**First pass, 60 pairs a world** (`lab/v/stage3_analyse.log`, read with uncertainty in `lab/v/stage3_summary.log`). The generator repeats itself: of 200 fresh draws, 6 repeat another fresh one and 7 a redo draw, leaving 187 distinct; 3 are out (stage 5's kinds); 184 judged. **66 of 184 (.36 [.29,.43]) have something to learn. Of those, the bank surely passes 10, surely fails 19, and 37 can't be told at 60 pairs** (their gaps are small, so x's interval is wide): coverage between .15 and .71. The redo set agrees (29 of 96 with a gap; 3 sure passes, 12 sure fails, 14 can't tell). The analyse log's own count, "30 of 69 pass", took x's point value and counted duplicates: it overstates.
- **Where the failures are** (fresh): colour swaps at a drawn period fail 7 of 8 (none passes), a meal soon after the last being bad (satiety) 5 of 7, the food colour set by where the creature is (region) 3 of 3, lies 3 of 8; fixed alternation is mostly passed (4 of 7). Worlds of the body and the blocks are mostly nothing to learn or can't tell.
- **The bank does what its family allows**: where the frozen reference surely closes over .25 of the gap (9 fresh worlds), the bank surely passes in 7; in the worlds the bank surely fails, the reference mostly fails too (r from -3.9 to +.44). So these failures are outside every hypothesis either learner holds, not a bank that wastes its evidence.
- **Harm**: in 118 fresh worlds with nothing to learn the bank is surely below base in 12, by more than .1 in 4 (and 2 of 67 in redo); surely above base in 19. Five of the six worst raise SENSE (the eyes more sensitive), where the bank loses .44-.60 to base and the told arm too (told below base, so the gap is negative): the loss is in the bank's own parts, not its learning; they assume a rate of pulses (its eye filter and the pause count pulses). That breaks "no fixed threshold tuned to the body". Being repeated on fresh seeds before it counts.
- **In bits** (the wires under base's policy against plain's, 20 pairs at 10 ms, `lab/stage2_label.py`'s rate KL): median evidence a life 77 bits where the bank surely passes, 40 where it surely fails, 28 where it can't tell, 21 where there is nothing to learn. This measures how different a world's wires are from plain's, not usable evidence about a rule (D33's weakness), so it doesn't separate passes from failures. (Corrected by the independent check: with the final groups the medians are 16 bits where the bank passes, 40 where it fails; and since this measure isn't evidence about the rule, it can't say whether failures are for want of evidence, as I first wrote.)

**What the first pass left open** (`lab/stage3_more.py`, worlds chosen from the first pass's verdicts before these lives ran; fresh seeds; 1.25 ms; `lab/v/stage3_more.log`):
- **The harm holds** (200 fresh pairs, seeds 80300-80499): bank minus base in the four SENSE worlds -.36 to -.59, each interval below -.29; told is below base in all four too. REACH raised -.09 [-.16,-.02] and a changed mouth -.11 [-.19,-.02], surely below base but not surely by .1. Plain -.01 [-.07,+.05]. So the bank surely harms where the eyes are more sensitive. **Traced to the eye filter** (`lab/stage3_sense.py`, `lab/v/stage3_sense.log`; g80 and plain, 100 fresh pairs, seeds 81100-81199, the uncompiled path; prediction written first: the eye filter, right). In g80 the bank is -.59 [-.68,-.51] below base and told -.60; with the eye filter off, -.12 [-.21,-.03] and told +.02 [-.05,+.09]. Switching off the pause, jitter, trust or growth changes no life at all, in either world. In plain, removing the filter changes nothing (-.05 against -.05). So the filter, harmless at the eyes' usual rate, costs about .47 when they are 2.8 times more sensitive; the remaining -.12 is the bank's colour choice (bank against told, both unfiltered), not traced. The filter's threshold is max(1, 3 x rate x 50 ms) pulses within 50 ms: relative to the background rate, but bounded by an absolute one pulse, and its constants were tuned at the usual rate, which is the kind of setpoint `AGENTS.md` forbids.
- **Top-up of the 37 can't-tell worlds to 300 pairs** (seeds 80500-80739; reference at 2.5 ms): 2 pass, 5 fail, 19 still can't tell, and 11 turn out to have nothing to judge (gap under .1). **So 55 of 184 (.30 [.24,.37]) have something to learn; the bank surely passes 12, surely fails 24, and 19 can't be told: coverage between .22 [.13,.34] and .56 [.43,.69].** Most still undecided have gaps of .1 to .25, where x's interval stays wide at 300 pairs; two with gaps near 2 (g352 satiety cycle, g384 alternation until) sit on the bar itself (x .29 [.25,.31], .25 [.22,.29]).
- **1000 s lives** (20 pairs, seeds 81000-81019; x over the last third, against the floor .25 only, since the reference wasn't run at 1000 s). Of the 19 sure failures: 2 pass (g192 satiety, .47 [.36,.58]; g261 alternate with satiety, 1.43 [1.26,1.58]), 2 on the edge (g174, g244, satiety), 9 still fail (every swap world, the alternate cycle g245, lies with satiety, region bursts), and 6 have nothing to judge, the told arm falling below base over a long life. Of the 11 can't-tell worlds: 2 pass (g352, g398), 3 can't tell, 6 nothing to judge. So a longer life rescues some satiety worlds (too short at 100 s) and none of the swaps (the idea is missing). x above 1 (g261) and told below base mean the told arm isn't a ceiling in long lives: not traced.

**The independent check** (the gate "3 to B"; an agent that didn't produce the work, the user's approval, 2026-11-07; its own code from the raw lives, `lab/stage3_indep_check.py`, `stage3_indep_rerun.py`, `stage3_indep_bits.py`, logs `lab/v/stage3_indep_*.log`; I read its key lines). **Confirmed**: the counts (187 distinct, 3 out, 184 judged), the generator's hash, the pairing, disjoint seeds, no refused lives, 53 of 53 saved lives re-run identically, the pass rule as written, the harm on fresh seeds, and that the reference's coarser step moves at most two verdicts. **Its coverage**: 56 with something to learn, 13 sure passes, 23 sure fails, 20 can't tell, .23 [.14,.36] to .59 [.46,.71]; every difference from mine is a world on a threshold, decided by the bootstrap's own noise. **Corrected**: g144 and g305 are one world (360 of 360 lives identical), as is g401 with redo g22; collapsing near-copies leaves the range .23 to .56. **Weaknesses**: 21 worlds judged nothing to learn at 60 pairs had gaps of .07 or more and were never re-measured, nor were sure verdicts on small gaps (g337, g344, g383); doing no harm as PROGRAMME words it (lower bound above -.1) fails to be shown in 55 of 128 nothing-to-learn worlds at 60 pairs; the 1000 s verdicts lacked the reference. All four are being run (`lab/stage3_firm.py`: the 26 worlds re-measured to 300 pairs; the other 96 nothing-to-learn worlds to 200 pairs; the reference at 1000 s; a final count with identical worlds once and a 20,000-draw bootstrap).

**The final count** (`lab/stage3_firm.py final`, `lab/v/stage3_firm.log`; every world with lives identical to an earlier one's counted once, which removes 10 more, so 174 judged). **61 of 174 (.35 [.28,.42]) have something to learn. The bank surely passes 11, surely fails 24, and 26 can't be told: coverage between .18 [.10,.30] and .61 [.48,.72].** The re-measured small gaps moved worlds both ways: several judged nothing to learn at 60 pairs have a small sure gap at 300 (g143, g146, g196, g238: flaky or mirrored eyes, gaps .10-.13), mostly can't-tell or failing; g383's sure pass holds (x 7.6, its gap only .17). Most can't-tell worlds have gaps of .1 to .25, where 300 pairs can't place x either side of .25; finer verdicts there would need thousands of pairs for a gap worth little.
- **Doing no harm, on every nothing-to-learn world** (113; 200 or 300 pairs): shown (lower bound above -.1) in 79; surely harmed by more than .1 in only 2, the SENSE worlds g322 (-.44) and g172 (-.38), both the eye filter. Not shown in 32, most of them surely a little below base (25 worlds surely below base, typically by .05-.10). So the bank's cost where there is nothing to learn is small but real and widespread: about .07 of efficiency, against which its gains elsewhere are 0.3 to 2.5. Not traced; the cost of exploring a lie it believes in (a rival adopted on luck) is the obvious candidate.
- **1000 s lives with the reference** (20 pairs, last third, the full bar): of 16 worlds with something to judge, 4 pass (satiety g174, g192, g352; g261 alternate with satiety), 2 can't tell (g244 satiety, g398 bruise bursts), 10 fail: all seven swap worlds, the alternate cycle g245, a lie with satiety (g183), region bursts (g280); 14 have nothing to judge at 1000 s. The reference now closes much of the gap in several swap worlds the bank fails (r .63 g226, .80 g328, 1.07 g397, .31 g227): with ten times the evidence, an ideal judge holding timing hypotheses learns a swap, and the bank, which holds none, doesn't. That is the clearest sign yet that the swaps want an idea, and that the idea pays at 1000 s; stage R tests whether parts drawn at random supply it.


## D36: stage R, rivals made from simple parts (2026-11-07)

`PROGRAMME.md`'s stage R, the user's decision B: the bank's rivals assembled from parts rather than written. `lab/rivals.py` (the parts: Count, Osc, Timer, Prod, on the tastes a brain already has, in seconds; RV, the bank with made contexts, V's taste with the count of goods replaced by the parts, V's compiled step unchanged); predictions and R2's rule written before any R2 life (`lab/v/stageR_predictions.md`).

**R1, the written bank rebuilt from parts: identical.** Each of V7's rivals is a context (the count of good tastes mod n, n 1 to 6) and a table; rebuilt as parts, 4 is a chain of two toggles and 6 a toggle and a 3-counter together (a bijection with the count mod 6). 160 of 160 lives identical to the bank's on 8 worlds (plain and seven of stage 3's fresh worlds where the bank picks rivals; seeds 81200-81209, 1.25 ms; `lab/rivals.py identity`).

**R2, K rivals drawn at birth** (`lab/stageR2.py`, queued after `lab/stage3_firm.py`): K = 10, 100, 1000 with the Occam bar, on stage 3's 55 fresh worlds with something to learn and 26 with nothing, on stage 3's own seeds so every comparison is paired with its base, told, reference and written-bank lives. A first look on 4 lives each: in plain no rival is adopted at K = 100 or 1000 (efficiency 2.58, as the written bank); a life takes 0.6-1.1 s at K = 1000.

**R2 at 100 s: random rivals do no better than the written bank, and worse where it was built to work** (`lab/v/stageR2.log`; 60 pairs, 1.25 ms; predictions scored in `lab/v/stageR_predictions.md`, mostly wrong). Sure passes of 55: written 10, K = 10 9, K = 100 9, K = 1000 10; coverage .16-.18 to .58-.65 for all. Paired against the written bank: better surely in 2-3 worlds (g144 = g305, a lie, x .44 to .61; g185 nth; g254 at K = 1000), worse surely in 13-17: every swap (by .4 to .8 in x), every alternation (.2 to 1.0), both satiety worlds with a fixed gap (g174, g244, by .3 to .45), region. Where there is nothing to learn, no rival is adopted at any K, with or without the Occam bar: every arm equals the written bank (so the harm in the SENSE worlds is the eye filter's, untouched). Three causes, traced (`lab/stageR2_trace.py`, `lab/v/stageR2_trace.log`; 40 lives each, K = 100 against the written bank, recording each taste while a rival is followed):
- **The written bank holds "it changes often"** (the default's table with trust 0, a colour that flips on one bad taste), which is what carries it through swaps: in g361 the written bank follows a rival on 1169 tastes, right .85 where the default would be .75; K = 100 follows one on 128. R2's rule can draw no rival without a context, so it can't hold this idea. My rule's omission, not a property of random repertoires; the 10,000 s test adds it back as one arm (K1000+).
- **Scoring without acting assumes acting doesn't change the world.** In satiety worlds (a meal soon after the last is bad, whatever its colour) the timer rivals adopted are right .27 of the time where the default would be .85 (g244): while scored passively, "soon after a meal, the other colour" looks right; once followed, it changes when the creature eats, and is wrong. The bank's whole economy (every rival judged on every taste, for free) rests on the world not depending on which rival is followed; satiety breaks that. The user's question about testing hypotheses with the world in the loop (2026-11-07) is the general form.
- **Alternation**: the random banks hold count2 rivals, but with trusts drawn at random, adopted later (the Occam bar: 5.4 at K = 100 with the n > 1 increment, against 3) and switched more often (84 adoptions in 40 lives against 62 in g170); right .74 where the written bank's are .82.
So at 100 s, a random repertoire of these parts doesn't find the ideas the written bank lacks, and loses the ones it had. The 1000 s and 10,000 s runs say whether more evidence changes that.

**R2 at 1000 s** (`lab/v/stageR2_long.log`; the 30 worlds of stage 3's 1000 s lives, 20 pairs, seeds 81000-81019, last third, the bar from the 1000 s reference). Of 17 with something to judge, the written bank passes 4, K = 10 none, K = 100 one (g261), K = 1000 none; no swap passes at any K. Two trends with K, both as the traces at 100 s explain: in swaps and the alternate cycle a larger K helps (K = 1000 against K = 100: g226 -.38 against -.53, g328 -.18 against -.43, g245 -.07 against -.36), though it still trails the written bank's "it changes often" in four swaps; in satiety worlds a larger K hurts more (g174: written +.32, K = 10 .00, K = 100 -.46, K = 1000 -.68), more timer rivals adopted on passive evidence that acting falsifies. The 10,000 s test (`lab/stageR_scale.py`, running) has the arm K1000+ for the first; the second needs a rival judged while acted on, which is outside R2's rule.

**The 10,000 s scaling test** (`lab/stageR_scale.py`, `lab/v/stageR_scale.log`; 13 timing worlds and plain, 10 pairs, seeds 81400-81409, 1.25 ms, last third; arms base, told, the written bank, K = 10, 100, 1000, and K1000+ = K = 1000's rivals plus "it changes often"; predictions 9-14 scored in `lab/v/stageR_predictions.md`, mostly wrong). No swap passes at any K. Larger K helps a little in swaps and the alternate cycle (g226 K = 1000 -.28 against K = 100 -.55; g245 -.16 against -.41), still behind or level with the written bank. K1000+ equals K1000 within .1 everywhere (not traced; its Occam bar of 6.3 against the written bank's 2 is the candidate). Satiety worlds worse with more K, at every length. **And in plain every bank arm, the written bank included, is surely below base by about .4** (-.37 to -.40; at 100 s +.08), with no rival adopted.

**Traced: the bank wears down over a long life, through its jitter gate** (`lab/stageR_plain_trace.py`, `_trace2.py`, `_trace3.py`, `lab/stageR_plain_ablate.py`; logs `lab/v/stageR_plain_*.log`). The loss grows with the life (last third, the written bank minus base: -.19 [-.60,+.21] at 300 s, +.01 at 1000 s, -.13 at 3000 s, -.40 [-.60,-.20] at 10,000 s); goods fall 18% from the first 1000 s to the last while base holds near 2.45. The pause never switches on in plain, and the balance learner's setting stays small (|x| under .1 on average). Switching parts off in 10,000 s lives: jitter off +.03 [-.02,+.09], no harm at all; eye filter off -.32, pause off -.36, trust and growth off change nothing. So the cause is the jitter gate (`lab/universal.py`, U.step): the balance learner's random steering (sd .15 a drive) turns on whenever a leaky count of good tastes over 200 s falls below 15 per 32 s. Plain gives about 17.7, so the gate sits just above the creature's usual rate; any dip turns the jitter on, the jitter worsens steering, fewer goods keep it on: the share of time jittering rises from 1% in the first 1000 s to about half by the end. A fixed rate the body happens to supply, used as a setpoint (the kind `AGENTS.md` forbids), with a slow ratchet visible only in long lives; the same class of fault as the eye filter (D35). Base (story 1's circuit) has no jitter or balance learner at all. So every bank arm's x at 10,000 s carries this loss, and the scaling test's verdicts are confounded by it, most where the gap is small.

**A block-level cure for the wobble, tried and not yet working** (`lab/adaptive.py`, the user's direction 2026-11-08: rules a block keeps
for itself, with no knowledge of meals; predictions and their scores in `lab/v/adaptive_predictions.md`; tests `lab/adaptive_test.py`,
`lab/adaptive_x.py`, `lab/adaptive_fresh.py`, logs `lab/v/adaptive_*.log`). Rules: (1) compare the input wire only with its own past (fast
against slow average, beyond counting noise) to re-arm the wobble; (2) keep wobbling only while the wobble's own correlation with the
outcome is significant; (3') keep a learned change only if its evidence is significant, else return to where it began. Found on the
scaling test's seeds, while designing: the long-life loss there comes from the balance setting, which random-walks while the wobble is on
and freezes when it stops (|x| against the life's gain, correlation -.79; the learner's own measure falls too, so not a proxy); averaging
the trials doesn't help (a walk without a restoring force averages to a walk). **Judged on fresh seeds, it fails:** in plain at 10,000 s
it is surely below base (-.28) and below the old bank; in the thrusters world (each thruster 0.5 to 2) at 1000 s the old bank gains 1.17
over base and the new one .17 (it quiets before it has learned); only at 100 s is it better (+.21, born exploring, where the old bank's
balance learner never switches on). **And the old bank's long-life loss in plain is not shown on fresh seeds** (-.08 [-.19,+.03], against
-.40 [-.60,-.20] on the scaling test's seeds): 10 pairs a set is too few to size it, so the jitter-gate diagnosis above stands as the
cause on those seeds, but its size is unknown. So the old gate does a real job in long lives (lopsided thrusters), and any replacement
must learn as fast as it does there; the measure for that is drives taken against an ideal learner's, not yet computed.

**The old bank's long-life loss in plain, sized** (`lab/plain_long_size.py`, `lab/v/plain_long_size.log`; 30 more pairs, seeds
81700-81729, 10,000 s, last third): -.23 [-.35,-.13]; pooled with the two earlier sets of 10 (50 pairs), **-.235 [-.32,-.15]: surely below
base by more than .1.** The two sets of 10 (-.40, -.08) were both draws from this. So the bank surely harms in plain over a long life, by
about a tenth of its efficiency, traced on the first set to its wobble (above); and the same wobble earns 1.17 in the thrusters world at
1000 s. A cure must keep the second and lose the first.

**How fast could the balance learner be?** (`lab/balance_speed.py`, logs `lab/v/balance_speed_*.log`; fresh seeds 81800-81819, 1.25 ms).
- *What a drive tells* (plain, the balance held at offsets d, 40 lives of 300 s each): the food pulses a drive are a sharp peak at d = 0,
  not a parabola: 4.16 at 0, 3.09 and 2.97 at -.15 and +.15, 2.45 and 2.60 at .3, 1.84 and 2.14 at .6; the life's gain .41, .26/.23,
  .05/.12, -.09/.00. So a .15 error costs 40% of the gain, and a drive is very informative near the peak: the slope is about 7.6 pulses
  per unit of x against a spread of about 3 a drive, so a pair of drives either side of the estimate fixes the offset to about .28, and
  an ideal learner reaches .05 in about 60 drives (a minute of life), .1 in about 16. (The script's quadratic fit, which gives 355 to
  3,200, is the wrong shape and is not used.)
- *How fast the learners go* (one thruster twice the other, the right |x| .69, 40 lives of 2000 s): the old learner |x| .03 at 100 s,
  .15 at 200 s, .47 at 500 s, .60 at 1000 s, .66 at 1500 s, about a thousand drives; the adaptive one (rules 1-3') .09 at 100 s, then
  stalls near .1-.15 (its wobble quiets before it arrives).
So the evidence is not the limit: an ideal learner would balance this body in a few hundred drives at most, the old learner takes about
a thousand and only once meals are scarce, the adaptive one never. The waste is in the learner's fixed step (its expected move a drive
is eta sd^2 f', about .004 at full slope) and in its gate, not in the senses.

**A learner that sizes its own step** (`lab/rprop.py`, judged by `lab/rprop_fresh.py`, traced by `lab/rprop_trace.py`, logs
`lab/v/rprop_*.log`; predictions 8-11 in `lab/v/adaptive_predictions.md`, written first; fresh seeds 81900-81969). It moves its balance
by its step D only when the sum of d e since its last move is two standard errors from 0; D doubles when a move agrees with the last,
halves when it reverses, and halves when 50 drives pass with nothing significant; its wobble's size is D's, within [.05, .4]. All four
predictions failed or were not shown:
- One thruster twice the other (right |x| .69), 2000 s: |x| .10 at 100 s (the old learner .01), then stuck: .14 at 2000 s (the old .66).
  Traced: far from right, 50 drives seldom give a significant sum (the slope there is about 2 pulses a unit, not the peak's 7.6, so my
  "few hundred drives at most" was for the last stretch only), each give-up throws the evidence away and halves the wobble, and a smaller
  wobble gathers less: by 200 s it is at the floor. Three lives of ten never moved from 0. The old learner's fixed step never discards.
- Random thrusters, 100 s: +.12 [-.14,+.38] over the old bank (not shown); 1000 s: -.16 [-.56,+.15] (not shown either way).
- Plain, 10,000 s: -.20 [-.27,-.13] below base, as the old bank (-.20 [-.35,-.07]), though its |x| stays under .1.
**The wobble itself is the long-life loss** (`lab/rprop_cost.py`, plain 10,000 s, 5 pairs, the balance held at 0): a fixed wobble of .02
costs .12 [.02,.21] a second against none, one of .05 .25 [.17,.32]; none ties with base (-.05 [-.12,+.02]). A 1% change of each
thruster costs 5% of the gain: the peak is a cusp, the cost of an offset growing with its size, not its square. If so, a probe's cost
and its evidence both grow with its size, so a smaller wobble buys nothing per bit; only probing fewer drives saves.
**The cusp is plain's knife-edge** (`lab/peak_check.py`, `lab/v/peak_check.log`, fresh seeds 81980-81999, 40 lives of 300 s, the
balance held at the right value plus d). Plain: food pulses a drive 4.22 at 0, 3.90-4.05 at ±.02 (5% off), 3.63-3.87 at ±.05, ~3.0 at
±.15; the same at .625 ms (4.23, 3.84-3.97, 3.66-3.86, ~2.99), so not the step. One thruster twice the other: 3.18 at the right value,
3.15-3.16 at ±.02 (under 1%), 3.05-3.06 at ±.05, 2.67-2.69 at ±.15: a rounded peak, as a smooth body should give. So only two exactly
equal thrusters give the sharp peak, and only there does every wobble cost in proportion to its size; a body that differs at all from
perfect symmetry (every real one) has a rounded peak, where a small wobble costs little (its square). The long-life loss of every
wobbling bank in plain (D36's wear-down, the adaptive and sized banks) is at least partly the price of this knife-edge, which the old
learner's random walk adds to.
**v2, no give-ups** (`lab/rprop_fresh.py 2`, `lab/v/rprop_fresh2.log`, seeds 82000-82059): its sums run until significant, D shrinks only
on a reversal. One thruster twice the other: |x| .14 at 100 s, .38 at 200 s (the old .01, .15), level at 500 s (.54, .55); within .1 of
.69 at 2000 s in 36 of 40 lives (the old 32). Random thrusters: +.03 [-.27,+.32] against the old bank at 100 s, -.19 [-.59,+.18] at
1000 s. *How much a drive tells far from right* (`lab/peak_check.py far`, `lab/v/peak_far.log`, 40 lives of 300 s held at each x): food
pulses a drive 1.73 at x 0, 1.91 at .15, 2.16 at .3, 2.50 at .45, 2.92 at .6, 3.16 at .69, 2.66 at .84, spread 1.2 to 2.7; so with a
wobble of .3 a drive's signal against its noise is about .3 everywhere below the peak, a significant step about 40 drives, the trip from 0
about 200 drives on average. *Why v2 still stuck* (`lab/rprop_trace.py 2`, `lab/v/rprop_trace2.log`): lives differ (one's slope at 0 is
.31, a quarter of the average, so ~950 drives a step); a large wobble raises the total thrust (e^(x/2) + e^(-x/2)), diluting the
first-order signal; and doubling overshoots (x thrown to 1.2-1.4, then a long wait back).
**v3-v5** (`lab/rprop_fresh.py 3|3b|4|5`, logs `lab/v/rprop_fresh3*.log`, `_fresh4.log`, `_fresh5.log`; diagnoses `lab/rprop_right.py`,
`lab/v/rprop_right.log`, `lab/v/rprop_fresh3f.log`; each on its own fresh seeds, predictions 15-23 first). Against the old learner:

| version | the change | double thruster, |x| at 300 s / within .1 at 2000 s | thrusters 100 s | thrusters 1000 s |
|---|---|---|---|---|
| v3 | v2, step never above .3 | .45 vs .31, +.13 [+.01,+.26] / 40 of 40 (old 35) | -.01 [-.25,+.22] | -.32 [-.65,+.02] |
| v4 | v3, give-ups (50 drives) halve step and wobble, sums kept | frozen at .21 / - | +.14 [-.13,+.37] | -.81 [-1.44,-.21] |
| v5 | v3, give-ups halve the wobble only, sums kept | frozen at .26 / - | +.20 [-.01,+.42] | -.10 [-.43,+.22] |

v3's loss at 1000 s is not its floor wobble (without it -.37) nor its accuracy (|x - right| .09 against .08): a life born near right
never gets a significant sum, so never reverses and never quiets, its wobble .3 for life (seed 82150: right -.06, x 0 throughout, the last
third 22 and 53 meals against 80 and 74). And any rule that quiets for want of significant evidence (v1, v4, v5) also quiets the lives
far from right whose evidence is only slow. The dilemma: "nothing to learn here" and "learning here is slow" look alike to a test of the
slope alone.
**v6: quieting on a peak's mark** (`lab/rprop_fresh.py 6`, `lab/v/rprop_fresh6.log`, seeds 82400-82459, predictions 24-26 first, all
held). v3 (no give-ups, step at most .3) plus one test: the block also sums d (e^2 - sd^2), whether its drives go worse the larger its
wobble, whichever way; when that sum is two standard errors below 0 (the mark of standing on a peak) it halves its wobble; a move restores
it. Far from right the sum is not negative (a large wobble there even helps, by more total thrust), so lives far off keep exploring: the
dilemma of v1-v5 answered by a second statistic, not by a wait. Against the old learner: double thruster |x| .21, .29, .43, .55 at 100,
200, 300, 500 s (the old .02, .16, .32, .48; surely ahead to 300 s, +.11 [+.02,+.19] there), within .1 of .69 at 2000 s in 37 of 40 (the
old 30); thrusters 100 s -.11 [-.34,+.10]; 1000 s +.17 [-.02,+.36]. The first version as good as the old learner in long lives and
surely faster to balance; its long-life harm in plain is being measured.
**v6's long-life harm, v7 and v8** (`lab/rprop_fresh.py 6L|7|8`, logs `lab/v/rprop_fresh6L.log`, `_fresh7.log`, `_fresh8.log`, fresh seeds,
predictions 27-36 first). v6 in plain at 10,000 s: -.25 [-.33,-.17] against base, its floor wobble .05 meeting plain's knife-edge; in a
nearly-plain world (each thruster 0.95 to 1.05, a world written in the language beside plain, not in place of it) -.05 [-.21,+.15].
v7 lowers the floor to .005, so the peak test alone sets how quiet it gets; v8 also gives that test an always-valid bar (Robbins' normal
mixture: checked every drive, a false alarm ever only 5% likely). Against the old learner and base:

| | double thruster: |x| ahead at 300 s; within .1 at 2000 s | thrusters 100 s | thrusters 1000 s | plain 10,000 s vs base | nearly plain vs base |
|---|---|---|---|---|---|
| v6 | +.11 [+.02,+.19]; 37/40 (old 30) | -.11 [-.34,+.10] | +.17 [-.02,+.36] | -.25 [-.33,-.17] | -.05 [-.21,+.15] |
| v7 | +.09 [-.04,+.22]; 33/40 (old 37), 3 never left 0 | - | -.17 [-.57,+.22] | -.06 [-.12,-.01] | +.10 [-.06,+.28] |
| v8 | +.21 [+.12,+.29]; 39/40 (old 30), none at 0 | +.03 [-.21,+.26] | +.17 [-.18,+.54] | -.19 [-.25,-.11] | - |

The old bank in the nearly-plain world is surely below base (-.16 [-.26,-.06]) and v7 surely above it (+.26 [+.16,+.37]). v7 and v8
trade: v7 quiets plain well but sometimes falsely far from right (a two-standard-error test checked every drive fires by chance in the
end); v8 never falsely, but too slowly for plain's knife-edge. The night's runs use v7.
**The scaling test with the cure** (`lab/stageR_scale_cure.py`, `lab/v/stageR_scale_cure.log`, v7, the scaling test's seeds 81400-81409,
paired with its uncured lives; stage R predictions 15-18 first). The written bank and K1000+ with the sized learner in place of the old
learner and its fixed gate, 10,000 s lives. The cure lifts the written bank's x surely in 12 of 13 worlds, by +.10 to +.69 (one surely
lower: g245, alternate cycle, -.11 [-.19,-.02]); written's verdicts go from 5 pass / 8 fail to 6 / 4 (3 can't tell). The three swap
worlds that failed (g227, g361, g335, x -.9 to -1.8) now sit at x +.06 to +.26, can't tell; g380 (swap bursts) passes. So the wear-down
was most of the long lives' failure, not the swaps themselves. K1000+ gains as much (+.11 to +.59 in 10 worlds) but still fails 11: its
problem is its own (late adoption, the Occam bar). Plain: written -.136 [-.209,-.070] against base (uncured -.397), K1000+ -.147: no
longer surely harmful by the bar, but a third of the loss remains. Cause traced (v7's plain traces, `lab/rprop_fresh.py 7`): chance moves
of a full .3 step, which nothing in plain ever halves (2 of 20 lives at x +-.3 for 100 s or more in the last third). v9 tests two fixes
(`lab/rprop9.py`).
**The cure in 100 s lives: the price of exploring** (`lab/stage3_cure.py`, `lab/v/stage3_cure.log`; traced in `lab/rprop_short.py`,
`lab/rprop_wobble_signal.py`, `lab/rprop_gate.py`, logs of the same names; stage R predictions 19-20, adaptive 44-48 first). Stage 3's 184
fresh worlds at 100 s with v7 in place of the old learner: bankS - bank -.60 on average, surely worse in 152 of 184, surely better in 9;
sure passes 0 against 10. (The construction checked: the same code path reproduces the old bank's lives exactly.) The cause is the
wobble itself, not moves: in plain at 100 s v7 loses 1.30 of base's 2.47; never moving recovers .11; born with its wobble .1 instead of
.3, .77. A fixed wobble with no learning costs plain -.28 at .05 (11% of the food), -.55 at .1, -1.22 at .3: plain's cusp. A drive's own
pulses do show the loss, but faintly: to see at two standard errors that the wobble hurts takes about 1,400 drives at .05, 200 at .1, 90
at .3, and a 100 s life has about 96. So no rule that judges its wobble by its own drives can make a learner born exploring safe in short
plain lives: the bits aren't there. The old bank is safe at 100 s because its gate (wobble only below 15 good tastes per 32 s) never
opens in a life eating normally; kept on v7, it makes v7 identical to the old bank there. And at 100 s balancing pays nowhere tested:
in the thrusters the old bank is surely below base (-.15 [-.27,-.02]), v7 level with base. The cure is a long-life cure; what decides
whether to explore at all needs evidence a drive's outcome doesn't carry in time.
**v7 firmed up, and a caveat on the scaling test** (`lab/rprop_fresh.py 7m`, `lab/v/rprop_fresh7m.log`, seeds 82700-82759; adaptive
predictions 37-39). Plain at 10,000 s, 30 pairs pooled with v7's first 10: v7 -.117 [-.157,-.079] against base, the old bank -.111
[-.201,-.029], v7 minus old -.006 [-.101,+.094]. v7 is steadier than the old bank (a third the spread) but no better on average. The
old bank's long-life loss in plain varies a lot with the seeds: -.40 on the scaling test's 81400-81409, -.19 on v8's, -.11 on these 30
(the same construction, checked). So the scaling test's seeds were hard ones for the old bank: its paired gains with the cure stand,
but their size there may be high. Double thruster, 2000 s: one life of 40 left near 0 (4 of 80 over both runs); |x| .59 at 2000 s
against the old learner's .70.
**v9, dropped** (`lab/rprop9.py`, `lab/rprop_fresh9.py`, `lab/v/rprop_fresh9.log`, seeds 82800-82849; predictions 40-43 first). An
always-valid bar on the move test (v9a), and the peak's mark halving the step too (v9b), against chance moves in plain. Plain at
10,000 s barely moves (v9a -.12, v9b -.10 against base, v7 -.13 on the same seeds), so chance moves were not the residual loss; the trip
far from right is much slower (|x| .10 at 300 s against the old learner's .33; 5 and 6 of 40 lives left near 0). In nearly plain all
three are surely a little below base here (-.07 to -.09).
**Closed: the balance learner** (the user, 2026-11-09: close out the unbalanced thrusters). What it taught:
- Adaptability costs (the user's insight; README). A brain built for varied bodies must spend trials finding out which body it has; on
  a short, easy trial it loses to a brain built for exactly that body. In plain, exploring the balance costs more than a 100 s life's
  drives can reveal (a wobble of .05 costs 11%, and showing that takes about 1,400 drives against 96).
- The self-sizing rules work where there is time: surely faster to balance a lopsided body, and in 10,000 s lives the written bank
  lifted surely in 12 of 13 worlds. The peak's mark (does the wobble hurt both ways?) answers "nothing to learn" versus "learning is
  slow", which a test of the slope alone can't.
- The old learner's safety at 100 s comes from never wobbling while it eats well (its fixed gate), not from judging its wobble.
- Outcomes are not independent draws: about half a wobble's cost falls in later drives, outside the drive that made it.
Decision: the bank keeps the old learner and its gate as the default (safe at 100 s, where stage 3 is judged); the sized learner v7
(`lab/rprop.py`) is kept as the long-life version. Not done, parked in `QUESTIONS.md`: the floor (the least an ideal learner pays to
tell plain from lopsided), best computed on a small surrogate of the drives rather than by more lives, and whether "do no harm" should be
judged against that floor rather than as a tie with base (the user's decision).
## D37: stage 0, the ruler (2026-11-09)

The ladders (`lab/ladders.py`; predictions first, `lab/v/ladders_predictions.md`; logs `lab/v/ladders_certify_*.log`,
`ladders_cross.log`, `ladders_baseline_*.log`, seeds 83000+, 2.5 ms). Three ladders on today's senses: **seq n**, a hidden word of n
colours advanced by good meals; **time n**, the food colour following a hidden word in time slots; **combo k**, a meal's meaning
set by the last k colours eaten. A rung is certified if a brain told the answer beats the starting brain surely by .25 or more, and a
brain designed by hand for the rung, told its structure but not its letters, surely closes half of that gap.

**The user's catch: world and brain shared a clock.** The first version began time's slots at t = 0, and its designed brain read the
world's own clock: godlike. Every periodic thing now draws its phase and its slot length (log-uniform 5 to 20 s) each life, the
designed brain keeps its own drifting oscillator, told the slot length but never the phase, and seq and combo start at a drawn place.
All numbers below are from the corrected worlds; the first run's are superseded (AGENTS.md, Gotcha: no shared clock).

**Certified rungs** (40 pairs). Seq: 2, 3, 5, 7, 11, 13, 17 (designed x .87 to .98). Combo: 1, 3, 4, 5, 6 (x .60 to .81); 2 isn't,
since its gap is small (1.26) and noisy. Time: 2, 3, 5, 7 (x .82 to .61), not 11 and 13 (.46, .38), where the designed brain's own
clock drifts across a long slot. Rungs 4 and 6, added, certify too (x .72, .69; `lab/v/ladders_certify_time46.log`): six.
**The ruler's first bar is met**: three ladders with five or more certified rungs each (7, 5, 6), and a baseline curve.

**Do the ladders differ?** Each designed brain on the others' middle rungs: combo's closes .39 of seq's gap (a good eater goes round a
short cycle of histories, which looks like a word), everything else under .05 or negative. They differ.

**The baseline** (the bank with K = 10, 100, 1000 random rivals, 20 pairs). Time: no K reaches half anywhere, and from rung 5 every K
is at or below 0. Combo: flat in K and below half everywhere. Seq: more K climbs while the answer is on the menu (rung 13: .16, .68,
.91), and fails at 17, where the word outgrows the rivals' counters (2 to 16). A ready-made menu holding the answer is what K buys.

**A flaw in the ruler.** On seq, K = 1000 solves 2, 3, 11, 13 but not 5 and 7: those have 100 s lives and 11 and 13 have 300 s. A
rung is harder than the one below only if its life grows no faster than what it asks, so the scaling curve's "hardest rung solved"
misreads a climb. To fix before stage 1: lives grown smoothly with each rung's bits (as time's already are), or the curve read as
the rungs solved in a row from the bottom.
## D38: stage 1's first experiment, who teaches the raw material? (2026-11-09)

`lab/teach.py`, predictions first (`lab/v/teach_predictions.md`), results `lab/v/teach.log` (20 pairs, seeds 84000+, the sequence
ladder's lives unchanged by the user's decision). Raw material counted in units, one letter each.

**Two of the three planned arms changed by sums before any life.** Units teaching each other can't help on this ladder: the blocks'
colours are random, so the eyes carry nothing about the word. And credit doesn't interfere: a vouched taste says which colour was food, so
every unit can be scored on it at once, counterfactually. The danger of one score for a group effort belongs to ladders where units act
on the body jointly. So the real choice was material against time.

**All at once** (the bank with a ring of every length up to M, P = M(M+1)/2 units): solves up to rung 2, 3, 5, 7, 7 at P = 4, 8, 16, 32,
64. It climbs as the square root of its material.
**A few at a time** (one ring growing a unit when its confirmed letters keep being contradicted): costs nothing in plain (x exactly 0;
it stays at 1 or 2 units with letters copied round) and uses only the material it needs (P 16 to 64 identical), but it is slow: about
n^2/2 tastes to try every length up to n. In the ladder's lives it solves rungs 2 and 3 only; 11 at .38 with final lengths 10 to 12.
**Neither is "add more brain and it climbs".** The bank needs material growing as n^2, growing needs time growing as n^2, where an ideal
learner needs about n + log2 n tastes. The waste is in how a wrong length is found out: a ring must be filled and then contradicted.
**The record arm: the first climb** (the user agreed; `lab/v/teach_record.log`, predictions 5-7). P units hold the last P letters revealed,
each at its good-meal count; one comparing unit per look-back k up to P/2 counts agreements and disagreements; the brain follows the
letter k back for the best k. Solved up to rung 2, 3, 7, 13, 17 at P = 4, 8, 16, 32, 64: doubling the material doubles the rung, in the
ladder's own lives, x .66 to .93. But in plain it costs (x -.11 to -.17, surely): suspected, its lack of a tally of trust (one misread
taste overwrites a letter). The user's observation: this heads towards a time-delay network over a shift register (keep each unit a
plain comparator), and its key is that sparse events move the register, events the circuit could learn to choose, as it learns what to
do with the states: good meals for seq, a clock for time, each colour eaten for combo. Proposed as stage 2's design.
**Stage 2, step A: registers moved by different events** (the user agreed; `lab/teach.py` events; `lab/v/teach_events_*.log`;
predictions 10-12). Five registers moved by good meals, any trusted taste, and the brain's own clocks of 1, 2, 4 s (random phase,
drifting), each P/5 units with look-back comparators; the best register and look-back followed. Seq: it picks the good-meal register
itself and climbs (rung 3, 7, 13, 17 at P 40 to 320). Time: rung 2 .58 at P 320, above the random rivals' .24 but not solved; nothing
from rung 4. A free-running clock can't line up with a slot of unknown length: the pattern is rarely a whole number of beats long, so
copies further back slide out of step, and the chooser prefers "the same as a moment ago". Next: a clock reset by surprises (a trusted
bad after goods), so its beats are set by the world's changes, which is the lock-on problem in another form. Plain costs again (-.11 to
-.15): the three-copy vote that time needed undid the record arm's protection against misreads; both needs to be reconciled.
**Stage 2, step B: clocks that lock on** (the user's idea: phase set by surprises, a PLL; Large & Kolen 1994; `lab/teach.py` lock;
`lab/v/teach_lock_*.log`, predictions 13-15). Four adaptive clocks (3, 6, 12, 24 s to start) pulled in phase and period by each trusted
bad, each moving a register. First, the scoring made fair: every register and look-back scored on what it would have predicted for each
taste, as the bank's rivals are (scoring at recording gave a clock one comparison a beat, the taste register one a taste, so "the same as
a moment ago" always won). Time: x .30 to .51 at every rung from 2 to 13, surely above base, never solved; flat in rung and in material,
so the lock is the limit, and many chosen clocks run to the 60 s cap. Seq at P 240: every rung solved. Plain -.25: a single misread now
flips the colour; to be given the designed brain's two-contradiction trust. Literature for the lock (the user asked): Large & Kolen 1994,
Large & Jones 1999, Righetti, Buchli & Ijspeert 2006 (adaptive-frequency oscillators by a local rule), Scheirer 1998 (a bank of
resonators), Matell & Meck 2004; for sequences, context tree weighting (Willems, Shtarkov & Tjalkens 1995), which the user observed
is a growing tree that "add more brain" could supply: a node recruits children when splitting beats it, by its own Occam test.
**The cost in plain cured, the last full run aborted** (predictions 16, 17). Two causes traced in plain lives: one misread flipping the
colour (a step's own letter overrode the copies), and, early in a life, a candidate followed on a few chance agreements. The record now
has the bank's protections: a default (keep the colour, two contradictions to flip) and the Occam bar for its number of candidates
(`rivals.occam`), choosing among those past the bar by long-run record. Plain on seq, 40 lives at P 240: identical to base (the run
aborted by the user after that rung, `lab/v/teach_lock2_seq.log`). In 6-life smokes: seq 5 and 13 solved at the right look-back; time 2
and 5 above step B (rung 5 about .45). Not yet measured in full: the time ladder with these protections, and seq above rung 1.
**Where stage 1 and 2 stand.** A design that climbs one ladder by adding material exists (the record, and its several-register form,
which picks the good-meal register itself): stage 1's bar of three doublings is met on seq (rung 3, 7, 13, 17 at P 40 to 320, step A).
On time it beats base at every rung but solves none, flat in rung and material: the lock is the limit. Next, in order: the full run
of 17; better locking (more clocks as the material, a period rule that doesn't run to the cap, Righetti's adaptive-frequency rule); the
combo ladder, which needs a register read as a context (the growing context tree); then stage 2's claim across all three.
## D39: the ideal learner written down, the lock by a bank of clocks, and pairs as a rung for driving (2026-11-10)

After a review of the strategy (the user's answers, `PROGRAMME.md`, How we work): light rigour, about 5 pairs a run, predictions with how
sure, a ledger (`lab/v/LEDGER.md`), and designing down from the ideal learner. This whole entry cost 0.4 CPU hours.

**The three ladders are one problem.** Each trusted taste reveals a letter (which colour was food), and every ladder says the letter is a
function of a context the brain could compute from its own history: seq n, the count of good meals mod n; time n, which slot of the
world's rhythm it is, mod n; combo k, the last k colours eaten. They differ only in which events move the context on.
**The ideal learner.** It holds every such rule (ladder, size, and for time a slot length and phase) with a prior of two to the minus its
description's bits, each context's letter unknown and each reading wrong about one time in twenty (plain's trusted bads, D38), and predicts
with the posterior mix. A context with a goods for one letter and b for the other has evidence (1/2)[(1-e)^a e^b + e^a (1-e)^b]. Each
taste carries about .7 bit, so it needs about (contexts + log2 of the rules held) / .7 tastes: 20 or so for seq 11, against the record's
2n good meals and a 300 s life's 200 tastes. Not built: the designed brains, told each rung's structure, already close .87 to .98 of seq's
gap and .60 to .81 of combo's, so on those ladders it would add little as a yardstick; time is where it differs (below).
**Its local forms, already known.** (Hoeffding trees, context tree weighting, Miall and the generate-and-test paper confirmed by search,
2026-11-10; the rest from memory, to check before relying on them.)
- A context tree: Rissanen 1983; prediction by the longest context seen, PPM (Cleary & Witten 1984); context tree weighting (Willems,
  Shtarkov & Tjalkens 1995), where each node mixes its own estimate with its children's, so the whole Bayes mixture over trees is computed
  from node to node.
- A tree that grows on evidence: the Hoeffding tree (Domingos & Hulten 2000). A leaf keeps counts for each feature it might split on and
  splits when the best beats the next by a bound. That is recruitment by a local test; a leaf that keeps being contradicted is frustration.
- Rhythm: a bank of oscillators read by coincidence, their phases reset by events (Miall 1989; Matell & Meck 2004; Scheirer 1998).
- Features proposed at random and kept by usefulness (Mahmood & Sutton 2013): D36's random rivals, which bought only a menu.
- Cascade correlation (Fahlman & Lebiere 1990): one unit recruited at a time, trained on what the rest still gets wrong.
**What that says about our designs.** The record (D38) is a tree of depth one over a register: it picks one feature, the letter k back.
Combo needs depth k (2^k leaves), which is why the bank and the record don't touch it. So one design may serve all three: a register for
each kind of event, a context tree over each, and the bank's scoring to choose among the trees. And it says when to recruit. Growing a
level only after a node has been contradicted (D38's grow, R3) costs about a period of the word per level, 12n to 40n good meals by my
sum against lives of 8n to 12n; giving a contradicted node's new context its node at once, as PPM and CTW do, costs about 6n and n log n
nodes. Recruit on novelty beneath a contradiction, and let evidence weigh the result. Proposed as the next design; not built.

**The lock** (`lab/teach.py clocks`; predictions and their scores `lab/v/clocks_predictions.md`; logs `lab/v/clocks_time*.log`; 5 pairs,
seeds 84000+, 2.5 ms). Sums first: evidence isn't short (3 to 13 tastes a slot); the designed brain fades up the ladder because its one
clock, a whole word long, is never corrected (out by .8n s at the end of a life); and D38's lock ran away because its surprises were the
brain's mispredictions, not the world's changes, each moving the period by a random share of a beat. So: a bank of clocks of fixed
period, only their phase set, by changes in the revealed letter (whatever the brain predicted), each confirmed by the next trusted taste
(a misread sets nothing and is never recorded), and a register's letters written one taste late, in the beat their own moment fell in.
- **First version** (the nearest beat moved to the midpoint of the two tastes either side of a change; 24 clocks, 10% apart): rung 2
  solved (x .69 to .72, where D38's lock had .40 to .50), plain exactly 0, but rung 5 at .02 to .27 and rung 11 at -.10 to .33. My
  prediction that a rung n is solved once a register holds 2n letters was wrong.
- **Traced** (`lab/clocks_probe.py`). The bar is steep: a poison costs 4 meals, so following the wrong colour a share w of the time
  scores about 1 - 5w of told. The starting brain is already right .71 to .85 of the last third (it flips on one vouched bad), the
  designed brain .89 to .97, the clocks .82 to .91. And beats slipped: a clock 1.3% off gained two beats in 71.
- **Second version** (a clock is moved only as far as the evidence says: one with a beat already between the two tastes is left alone,
  any other has its nearest beat moved to the gap's nearer end): rung 2 at .74 and .83, rung 5 at .50 [.40, .60] with registers of 16.
  A clock within 3% of the slot's length now keeps count (71 beats to 71 slots, 99 to 100); one further off doesn't.
- **Spacing** (60 clocks, 4% apart, nothing else changed): rung 5 at .63 [.42, .82], about the designed brain's .69, which is told the
  slot's length. Not surely solved at 5 pairs.
So timing was limited by the lock, as D38 said, and the cure is in what sets the phase (the world's changes, not the brain's surprises)
and how far (no further than the evidence). The rung sets a register's length; the range of rhythms covered sets the number of clocks,
a fixed cost, and a large one: 62 registers. A clock that trimmed its own period within its band would need fewer. Not run: rungs
above 5 with 60 clocks; whether a counting clock's remaining 12% of disagreements are the registers' or the phase's.

**Pairs: a rung for driving** (`lab/pairs.py`; `lab/v/pairs_predictions.md`, `pairs.log`; 5 pairs of 100 s lives, seeds 85000+). Each red
block has a blue partner at a set gap; when either is eaten the pair moves. Down to 4 mm between centres nothing is lost (plain 2.34 for
the starting brain, 2.28 told). At 3 mm a little (told 1.88). Touching, at 2 mm: 1.20 and 1.56. I predicted poison eaten with the food.
Wrong: poison stays at 8 a life, as in plain, and food falls from 53 to 40. The poison eye ends the drive, so the starting brain already
keeps "food in view and no poison in view", and pays for it in food declined. What is left to learn is how to approach, from the side
where the food isn't beside its poison: skill in acting, with nothing new to know. Not yet certified: no yardstick shows the food can be had.

## D40: a context tree over registers, on all three ladders (2026-11-10)

`lab/tree.py`, through `lab/teach.py tree` and `treec`; predictions and scores `lab/v/tree_predictions.md`; logs `lab/v/tree_seq.log`,
`tree_combo.log`, `tree_combo_20.log`, `treec.log`; seeds 84000+, 2.5 ms, 5 pairs unless said. D39's proposal, built in its plainest form.
**The design.** A register per kind of event holds its last 16 symbols: the letter revealed at each good-meal count; the colour eaten
at each taste; and, in `treec`, the letter of each beat of each of D39's 60 clocks. Over each register, a tree of identical nodes. A
node stands for one context (the last d symbols) and counts which colour was food there. A trusted taste adds its letter to every node
on the current context's path. The deepest node on the path, if it has seen both letters and material remains, recruits one child for
the context one symbol longer. The deepest node whose counts lean one way says the letter. Each tree is scored on every trusted taste
against a default (keep the colour, two contradictions to flip) with the Occam bar for the number of trees, as the bank scores rivals.
Raw material is nodes, shared equally among the trees. Nothing is told of the ladder, its size or the life's length, and no setting
changes between ladders.
**Sequences.** Rung 11 solved with 32 nodes a tree (x .90) and rung 17 with 128 (.83, using 43; .36 with 32). Rung 5 at .54: its 100 s
life holds about 43 good meals and the tree takes about 6n to grow. Plain exactly 0, 6 nodes used.
**Combinations**, where nothing of ours climbed (the bank .04 to .28, D37): at 20 pairs, rung 1 solved at every size (.67), rung 3 with
32 nodes a tree (.64 [.50, .72]), rungs 5 and 6 with 128 (.70 [.58, .79], .58 [.50, .65]; .60 and .38 with 32, .45 and .31 with 8).
Rung 4 at .62 [.46, .74], not sure. About the designed brain's level (.60 to .81), which is told k. Two things the sums missed: a tree
too small still earns a good deal (rung 3 at .62 with 8 nodes for a full tree of 15), since a good eater meets only some histories; and
spare nodes cost a little (rungs 3 and 4 fall from .64 and .62 to .56 and .51 with four times the nodes), growing on misreads and on
colours guessed at untrusted tastes.
**With clocks, all three at once** (62 trees, 16 or 32 nodes each): time 2 at .94 [.76, 1.17], above the designed brain's .82; time 5 at
.42 and .45, time 7 at .34 and .51 [.10, .72]; seq 11 still solved (.89) and combo 3 at .74 [.49, .92], each life following its own
ladder's register; plain exactly 0.
**Where that leaves the scaling test.** One description now climbs two ladders with material (seq to 17, combo to 6, each needing more
nodes for a higher rung and using few when the rung is low) and has a foothold on the third (time 2 solved, 5 and 7 near half). It
recruits nothing in plain. Not shown: three doublings on combo and time read off cleanly; why the tree beats look-backs at time 2 and
trails them at time 5 (.45 against .63); the held-out ladder. And the unit is a counter in a tree addressed by context, which is a
known algorithm's node (D39), not something that emerged. Fan-in is one symbol a node. The 60 clocks are a large fixed cost.

**Pairs' yardstick failed** (`lab/pairs.py careful`; `lab/v/pairs_careful.log`): a careful driver by hand, told the colour, that heeds
poison only when the poison eye is at least a set share as busy as the food eye, and may stop at a good taste. Best 1.72 against 1.56
at 2 mm, within the noise; heeding less poison eats more of it and wins no food. So the eyes' pulse rates don't separate a partner beside
the path from one in it, and pairs are not yet a rung these eyes can be shown to climb.

## D41: no acting rung at touching pairs, with these eyes (2026-11-10)

`lab/pairs.py looker`, `lab/pairs_probe.py`; `lab/v/pairs_predictions.md` (the trace, the sums, predictions 8 to 10 and their scores),
`lab/v/pairs_looker.log`; 5 pairs, told the colour. The manoeuvre the user chose after D40's careful driver failed.
**Traced first.** At 2 mm a poison pulse ends 45 drives a life with food ahead. In a third of them carrying on would have eaten clean
(14 a life, as many as the 13 foods lost); in a quarter the partner is hidden behind the food; in a quarter it is in the way. The
careful driver failed because it compared the eyes over .1 s, one to three pulses each.
**Look before you leap.** On a poison pulse during a drive the brain stands still and counts both eyes for .15 or .3 s, then drives on
(heeding no poison, stopping at the good taste) or turns away. Its judgement is good: 9 commits a life, 7.7 ending in food alone, and it
almost never commits with the partner in the way. But it scores 1.01 to 1.43 against the told arm's 1.56. A look gathers only 3 to 5
pulses an eye, the looks and turnings-away take 17 s of a 100 s life, and the starting brain, scanning on and trying again at once,
gets most of those foods anyway. By the sum redone with these numbers, looking wins at most 8 foods and costs 4 before anything else:
a tie at best. Stopped there.
**What it means.** The food of a touching pair is lost to missing information, not missing skill: where across the corridor each block
lies, which these eyes deliver at a few bits a second. That is D21's and D22's wall met again. So touching pairs are not an acting rung
on today's body. Candidates instead: the lopsided body (D19, D20: a certified gap, 2.2 to under .8, a yardstick told its body, and
learners that close 37% and 93% of it), which is a challenge about acting whose evidence comes from the brain's own movement; or the
split eye (D24), a change to the body and so the user's decision.

## D42: the lopsided body as the acting ladder: one sure rung, one weak (2026-11-10)

`lab/bodyladder.py`; `lab/v/body_predictions.md`, `body_which.log`, `body_rungs.log`; 5 pairs of 300 s lives judged on the last third,
seeds 86000+. The user's ladder: rungs by how many of the body's numbers are drawn afresh each life (each between a half and twice).
**Which numbers cost the starting brain anything** (plain 2.52). Each thruster's strength separately: .94, and told its balance 2.46,
everything back. Both thrusters together: 2.59, nothing. Both eyes' sensitivity, or one eye's: 2.48, 2.20, nothing. Drag at a half or
twice: 1.53 (at .7 or 1.4 times, nothing), which D5 hadn't found.
**Drag's cure** is one number too. Speed goes as firing rate over drag, so scaling every rate (scan, drive, run) by the drag gives 2.54 at
half drag and 1.98 at twice (the rest is the price of firing more). Call it the tempo. Single knobs do less.
**As rungs.** Both drawn: .86 against 2.48 told both, a gap of 1.6, nearly all of it the balance's. Drag alone, drawn between a half and
twice: 1.96, and told its tempo 1.92, no better at 5 pairs: only the ends of the range hurt. The bank, with D19's learner inside, closes
almost nothing in 300 s (1.02 against .94 on thrusters, 1.07 against .86 on both).
**So** this body has one number worth learning (the balance), a second at the extremes (the tempo), and nothing else: an acting ladder
of body numbers is one sure rung and one weak one, where the scaling test wants five. And the balance's best learner (D20's sweeps, 93%)
is a mechanism made for it, not generic material. Ways on, for the user: draw drag more widely (a third to three times) to make the
second rung real; make the body's numbers depend on a context (a balance or tempo that follows a hidden word or rhythm, so that a tree's
nodes would hold a setting each, not a letter); or take two rungs as what this body offers and say so.

## D43: knobs first: the balance knob set by trial, by D20's counters, and by the generic register (2026-11-10)

The user's rule (AGENTS.md, Knobs first, recruits last): turning a knob the brain has is the cheap option; recruit only if that fails.
Compensating for a weak thruster is one knob, the balance between the two motors' rates; the brain told its body is the starting brain
with that knob set right. `lab/body_knob.py`; `lab/v/body_predictions.md`, `body_knob*.log`; unequal thrusters (each a half to twice), 5
pairs, seeds 86000+, the last third of each life.

| life | knob untouched | set right | trial: D19's learner (in the bank) | trial: D36's self-sizing | measured: D20's 192 counters | measured: a register in beats |
|---|---|---|---|---|---|---|
| 100 s | .49 | 2.42 | .33 | .14 | 1.78 [.45, 3.04] | .89 [.41, 1.41] |
| 300 s | .94 | 2.46 | 1.02 | .65 | 2.08 [1.71, 2.33] | 2.37 [1.76, 2.81] |
| 1000 s | .74 | 2.36 | 1.62 | 1.50 | 2.05 [1.60, 2.51] | 2.01 [1.27, 2.48] |

**Why trial is slow.** The knob gets no hint of which way to turn: both eyes look down one corridor, so a drive that curves and loses its
block doesn't say which way it curved (D13's dead ends: the time to find the block again is shortest at the right balance, an extremum;
a zigzag within a drive shows nothing until the block is lost). So the learner nudges and compares outcomes that are mostly luck, at
about a drive a second: hundreds of drives. A measurement has the sign and the size at once: turning with one motor alone, what the
eyes see comes round once a revolution, and a revolution's length goes as 1 over that thruster's strength (D20). In bits, a revolution
timed to a beat in 20 is about 4 bits; a drive's outcome is a small fraction of one.
**The generic unit as the measurer.** D20 used a bank of 96 to 192 counters over intervals in seconds. Here: a register that takes one
cell per beat of the brain's own motor during a sweep (did an eye pulse since the last beat?), and a comparing unit per look-back up to
64 that counts coincidences against chance. That is D38's record, moved by a new kind of event, the brain's own beat. The best look-back
is the beats in a revolution (10 to 40); the knob is set to the log of the two motors' ratio. No clock is needed: the beats are the
ruler. Sweeps' timing, gating by frustration and stalling are D20's, unchanged. It does as well as the counters (2.37 against 2.08 at
300 s, 94% of the gap) with no sure cost on an ordinary body (2.37 [1.68, 3.06] against 2.52).
**What it says.** For this shortfall nothing needed recruiting beyond what the sequence ladder already uses: a knob the brain had, and
the recording unit pointed at the brain's own movement. Not shown: the 100 s gap between the two measurers (.89 against 1.78, intervals
overlapping); the same for drag's tempo knob, which has no measurer yet; that the register is recruited only when the knob's own
adjusting has stalled, which here is D20's gate written by hand.


## D44: the dancing brain's D0: what each movement cycle tells, in bits (2026-11-10)

`lab/dance0.py`; `lab/v/dance_predictions.md` (predictions 1-10 and their scores), `dance0_report.log`, `dance0_corridor.log` (the
lives' pickles in `lab/v/`, out of git). The user's new phase (`PROGRAMME.md`, The next phase), its first stage: before building a
dancing brain, does dancing produce evidence that foraging doesn't, and about what? 600 bodies a cycle, each thruster and the drag drawn
(a half to twice), 100 s lives, seeds 87000+. Ten arms: the starting brain foraging, and nine open-loop cycles (still; one motor
spinning at the scan's rate, either; D20's sweeps, 8 s on each motor; both at the drive's rate; 0.1 s bursts each second; zigzags of
.5, 2, 8 s, one motor at the drive's rate and the other at half, swapping).

**The sum first.** A beat moves the body k PUSH / (d DRAG) and turns it k TURN / (d DRAG), so a thruster's strength k and the drag d are
one number to the eyes, except through a coast's time course (10 to 40 ms, against eye pulses at most 50 a second). So the things worth
knowing are the balance log(k0 / k1) and the **stride** log(sqrt(k0 k1) / d), how far a beat carries the body; drag on its own is
nearly unknowable, and needn't be known, since the tempo knob (D42) cures the stride.

**The observer needed mending.** A ridge decoder scored by squared error found almost nothing even on sweeps. Traced: the beat-clocked
register (D43) gives a motor's beats a revolution exactly when right (20.3 against 20.4) but slips to a half, a third or a far multiple
in some lives, and squared error lets the slips swamp everything. Bits are now mutual information with the truth in 12 equal-count bins,
bias-corrected (a lower bound, capped at 3.6), from the better of the ridge decoder and a physical estimator (beats a revolution per
motor, the fundamental chosen by excess summed over all its multiples over their number's square root: 72% of motors within 5% after
50 s of spinning).

| arm (100 s) | balance: bits (median error) | stride | drag | gain a 10 s |
|---|---|---|---|---|
| foraging | .5 (.27) | .5 (.25) | .2 | +.61 |
| still | 0 | 0 | .1 | 0 |
| one motor | .1 | .5 (.25) | .3 | 0 |
| sweeps | 1.1 (**.04**) | 1.1 (**.03**) | .4 | -.03 |
| zigzags | .7 to .8 (.20) | .5 to .6 (.22) | .3 | -.4 to -.7 |
| straight, burst | .1 to .2 | .1 to .2 | 0 to .2 | -.2, -.1 |

At 30 s no arm knows much (sweeps .4 bits, median error .62; foraging .3). **Where across the corridor a block lies** (every .25 s, the
nearest block's side in the brain's frame, from the last .5 s of pulses and beats, a linear decoder): at most .02 bits a second in any
arm, zigzags included. A block crossing the corridor gives one to five pulses: D21's and D41's wall, which movement doesn't breach.

**What it says.** Dancing does yield what foraging doesn't, but only about the body, and only from one kind of cycle: one motor at a
time, long enough for the view to come round several times. That is D20's sweep, already known. The rest of the variety we wrote tells
these observers nothing new (straight, burst) or a little, coarsely (zigzags, which mix both motors and so smear the one clean
recurrence), and costs food (zigzags meet blocks at random, and poison costs double). The same sweep that sets the balance also gives
the stride (the mean of the two motors' beats a revolution), so **the tempo knob already has a measurer** (QUESTIONS.md: what measures
the tempo knob?). Not shown: what an observer that knows a zigzag's physics would get; that the stride's estimate sets the tempo well in a
life. For D2: cycles that mix motors spoil the evidence that matters here, so "many cycles at once" must at least take turns.

**Corrected (same day, D1's smoke):** straight runs do tell the body. A lopsided body driven straight circles, and the recurrence
period of its view, in its own beats, tracks 1 / |k0 - k1|: 76% of bodies within 10%, where the period fits in 127 beats (two thirds
of them). The observer missed it because its physical estimator knew only spins: the observer built from our understanding was the
limit, not the movement. So "variety isn't evidence" overstates D0: other movements carry the body too, in forms our observer
couldn't read. D1's ruler is physics-free for this reason (`lab/play1.py`).

## D45: the playing brain's D1, step 1: a unit's own judgement doesn't find what tells the body (2026-11-10)

`lab/play1.py`; `lab/v/dance_predictions.md` (11-16 and scores), `play1.log`, `dance0_confirm.log`. Also D44 confirmed: its mended
observer, frozen, on fresh seeds (89000+) gives the same (sweeps' median error .05 and .04 at 100 s, foraging .23; every arm's bits
within .3), so D44 stands as more than exploration (PROGRAMME.md, How we work: forking paths).

The question (PROGRAMME.md, D1): can a generic self-judge find informative movement unaided? 40 rhythm units drawn at random (a square
wave of period .2 to 20 s, any duty, rate 5 to 50 a second, random weights onto each motor in each part) and D0's four, each alone on
300 bodies (thrusters and drag drawn), 100 s. Each unit's self-score: bits a second its own beats make the eyes predictable (its
beat-clocked register: how much a cell k beats back tells about this one, the best k; and the same beyond the last beat's). The ruler:
bits about the balance (or its size) and the stride, by an observer that knows no physics (D44's features plus each motor's recurrence
period). Made physics-free after the smoke showed D44's observer blind to straight runs.

**No.** The self-scores' rank correlation with the ruler is -.02 and -.22; none of the ruler's top five is among the self-judge's. The
self-judge ranks highest one motor alone, steady or nearly (.8 to .9 bits a second): the most regular world a movement can make, which
tells one thruster over the drag and nothing about the balance. The ruler ranks highest units that switch between the motors within a
second or two (.7 to .9 bits on the balance) and sweeps for the stride (.95); switching makes each motor's register less regular, so
they score low on the self-judge.

**What it means.** Predictability isn't information about what varies. A unit judging itself rewards the movement that makes its world
most regular, the stereotyped one. What tells the body is a contrast: the balance is the difference between what each motor does to
the view, so no unit that drives one motor can see it, however well it predicts. The knowledge is in the comparison between units,
not in any one. Not tried, and the next candidates (generic, none encodes the body): units judged by learning progress (how fast their
predictions improve, which a stereotyped unit exhausts quickly), not by how predictable their world is; units judged by how much their
predictions differ from their neighbours' (a contrast between units, made locally); the bank judged by how well its units' predictions
let it predict an outcome that matters (D2's link).

## D46: play first, the challenge later: what learning progress chooses (2026-11-10)

`lab/play2.py`; `lab/v/dance_predictions.md` (17-19), `play2.log`. The user's frame: play is an investment, so a life of play first and
the challenge later, judged by what play pays then. This step builds the play and asks what it chooses; no knob is set yet. D45's 40
random units as a bank; each turn of 3 s goes to the unit whose own predictions are improving fastest (learning progress, Oudeyer and
Kaplan 2007), in bits a second of play, its latest turn against its one before; each unit is tried twice first; play ends when no unit
improves beyond twice its noise; then the starting brain forages. 900 s lives, thrusters and drag drawn, 20 pairs.

Two traces before it ran: progress counted in a unit's own cells let units beating once a second hog play for 100 s each (they need
that long to show anything), and "not yet known" read as "no progress" ended play after one turn each. Counted in bits a second of
play, the currency play spends, both went.

**Play ends by itself** in every life, at a median 275 s. **But it doesn't concentrate**: the most played unit gets 9 s, most get 7, and
ruler bits a second as played are .81 against .80 for all units alike. Turn-on-turn progress is mostly noise, so each unit gets two or
three turns and then none improves beyond its noise: learning progress as built samples everything briefly. Last third .41 against the
starting brain's .33, tied, as expected with no knob set. In D44's terms 7 s of any movement tells next to nothing (sweeps needed about
100 s), so play spread this thin gathers little about the body unless the link pools across units.

## D47: play first, the challenge later: three links from play to the knob, and taste's search (night of 2026-11-10)

`lab/play3.py`, `lab/play4.py`; `lab/v/dance_predictions.md` (20-32), `play3.log`, `play4.log`, `play4_confirm.log`,
`play4_untaste.log`. The user asked for all three links (PROGRAMME.md, D2), then any other experiments. D46's play on lopsided bodies;
what play leaves is each steady motor mix it played and the eye pulses during it. Two statistics of a mix: the view's recurrence period
(precise, D44, but needs whole revolutions within one stretch) and new sightings a second (rises with how fast the mix turns the view,
from any stretch; rank correlation .45 to .7 with the true turning rate across a life's mixes).

**Why recurrence starves.** Play spreads over about 70 mixes, a median 3.7 s each in .65 s stretches; a mix that got time had its period
right (2.34 against 2.26 s), but most never show a revolution. Banks of 4 or 10 units with 10 s turns didn't change that: a random bank
rarely holds one motor alone for long.

**The links** (900 s lives, last third; play3, 20 pairs; forage .62, told 2.31):
- steady (gaze stabilisation: a forward model of how fast each mix turns the view, from sightings; the drive set where it predicts no
  turning): knob error .26, gain +.01. Close, but the score is steep in the balance.
- partners (each motor's effect from the mixes that beat it alone, made equal): error .56, -.06.
- taste picks (five balances, 30 s each twice, the best kept; nothing from play): **+1.06 [+.61, +1.53]**, 75% within .2. Trial is
  fast when it compares a few settings outright, not when it nudges (D19, D43: about 1000 s).

**The user's frame: play first, the challenge later** (play4: meals worth nothing until a moment drawn at 400 to 600 s; scored from
then). Taste can't search before the challenge, so it searches during it: **-1.04 and -.82 surely below forage** in the 300 s after
onset on two seed sets, though it ends with a good knob. Steady, set by play before onset: +.76 and +.79 (the latter sure) on the
development seeds, **+.54 and +.39 on fresh seeds, not sure** (knob error .17, then .29). Play's estimate then a short taste search
near it (steadytaste): +.62 and **+.86 surely** in 100-300 s. So play pays later in sign, roughly: it saves taste most of its search.

**Two dead ends.** Practice (the model learning on from foraging's scans and runs) drove the knob off by .4 to .7: a scan ends when
something comes into view, so the scans that run their course saw little; closed-loop behaviour is biased evidence for an open-loop
model. Playing on whenever nothing tastes (through the whole quiet spell) made the estimate worse (.27 against .17): the sightings
model is biased, so more of its evidence doesn't help.

**Where it leaves play.** The head start is real but small, limited by how well a random bank's short stretches can say how each mix
turns the view. The precise statistic (recurrence) needs long single-mix stretches, which random rhythms rarely give; the cheap one is
biased. What would make play pay well is a generic way to get long, clean stretches, or an estimator of turning that works on short
ones. Taste comparing a few settings is the strong mechanism here, and play's best role is narrowing its search.

**Then the precise statistic, from each motor's own record** (same night; `lab/v/play4_beats.log`, `play4_beats_confirm.log`,
`play4_alt.log`, `play4_alt_confirm.log`; dance_predictions 33 to 37). One more cheap statistic failed first: one over a sighting's
length (knob error .46). Then D43's record, generically: for each motor, every run of beats in which it alone beat, whichever random
unit made it, as a record clocked by its own beats (rate changes within a run don't matter: the beats are the ruler), pooled over runs;
each motor's beats a revolution by D44's rule; the partners link makes the two motors' effects equal. Nothing chooses a sweep: the
evidence comes from the random units that happen to use one motor.
- Play first, the challenge later (play4): **+1.55 [+.51, +2.62] at once and +1.23 [+.24, +2.30] after, surely**; on fresh seeds
  **+1.51 [+.59, +2.43] and +1.15 [+.23, +2.00], surely** (told +2.9 to +3.3). Knob median error .07 to .10, but only 53 to 65% within .2:
  19 of 30 bodies within .1, about 6 off by a doubled or halved period in one motor, a few by a factor 3 or 4 (D20's slips).
- **Taste picks among play's own hypotheses** (each motor's best period and its best rival, the comb's runner-up; three candidate
  balances, 30 s each from the first taste): costs the first 100 s (-.14, -.02) and pays after: **+1.97 and, on fresh seeds, +1.60
  [+.76, +2.42] surely**, 70 to 72% within .2. About even with play's best guess over the 300 s; better for anything longer.

**So play pays later.** A life of random rhythmic play, with no goal and nothing to taste, leaves each motor's own record; a generic
partners link turns it into the balance knob before the challenge begins, and the creature starts the challenge with about half the gap
to a brain told its body already closed. Taste's role is to choose among play's few hypotheses. What carried it: the record clocked by
the brain's own beats (rate-free, gap-free), pooled across whatever random movements happened to use one motor; not learning progress
(which only ended play), and not the steady-view model on cheap statistics. The partners link assumes the body comes in matching
pairs; the steady-view link, which doesn't, needs a turning estimator as good as the record (QUESTIONS.md).

## D48: boredom: bored when the estimate stops moving? (2026-11-11)

`lab/play3.py` (stall, mover), `lab/v/play4_bore.log`; dance_predictions 38 to 40. The user: we have met boredom, playing until you stop
learning (README, Terms). D46's boredom was learning progress (prediction improving turn on turn): it ended play well (~280 s) but
couldn't steer it. The alternative tried, AGENTS.md's own "finished means its adjustment has stalled": play is over when the knob's
estimate (D47's partners record) has its last five readings within .05; `stall` plays the units in a shuffled cycle, `mover` gives each
turn to the unit whose last turn moved the estimate most. A first version ended play at 39 to 75 s, because turns that added no
evidence left the estimate still: only turns that added a single-motor run count. 20 pairs, play4's frame.

Mover plays half as long (median 135 s against 285), but its knob is worse (.26, 45% within .2, against .10, 65%) and its head start
smaller and unsure (+.82 against +1.55 at once); stall is worse still (.32). **An estimate that has stopped moving isn't one that is
right**: the comb's best period is sticky, so a slip (a doubled period), once on top, survives five more turns of evidence. Boredom
from stillness is fooled by confident mistakes; learning progress, by playing longer, gathered enough to avoid more of them. What
boredom should read instead is the estimate's uncertainty: how clearly play's best hypothesis beats its rival (the margin D47's taste
choice already uses), bored when the margin is clear, and handing the rivals to taste when it isn't.

**Then boredom from certainty** (same day; `lab/v/play4_certain.log`; dance_predictions 41, 42). Each motor's record gives play's best
period, its strongest rival (another peak of the comb, not within a quarter) and the margin between them, in chance's spread. Bored when
both margins reach 3, or when a taste ends play; a motor still in doubt hands its rival to taste (30 s a candidate). Traced first:
rivals taken from the best's own shoulder gave margins of .1 to .4 always; a mover that found nothing raising certainty replayed one
unit that never eats (ties now go to the least recently played). 20 pairs, development seeds:
- `certainmover` (each turn to the unit whose last turn raised the certainty most): knob median error .01, 90% within .2; **+1.14 [+.26,
  +1.92] at once and +2.05 [+1.27, +2.84] after, surely** (learning progress's partners +1.55, +1.23; told +2.87, +3.01). Certain and done
  before the challenge in 20% of lives; otherwise it played on until food came (median 502 s) and taste settled the last doubt.
- `certain` (units in a shuffled cycle): as accurate (90%) but never certain before the challenge, so taste always had a search to make
  (-.28 at once, +1.78 after).
So boredom should read certainty, not stillness: play on while the best guess doesn't clearly beat its rival, steer play to what raises
that certainty, and hand what doubt remains to taste. One rule now covers when to stop playing and what taste is for. Exploratory
(designed on these seeds): to confirm on fresh ones.

## D49: an outside review, and P1: what steering play buys at equal time (2026-11-11)

**The review** (`lab/v/review_2026-11-11.md`, by another agent at the user's request, of commit d96b215; adopted in full by the user).
Its main points, and what changed: our bits accounting conflated the length of our description of a world with what the creature must
resolve and with what all its senses can supply (README and ABSTRACT corrected: learning is fast when the distinctions that matter are
cheap under the prior and the actions expose them); D47's partners rule is our understanding of the body, so D47 shows estimation from
unrewarded play plus a designed rule, not discovery of the rule (README corrected; P2 removes it); predictability, surprise,
information gain and decision value are different objectives (MacKay 1992, active data selection), and D46's learning progress was a
rough estimator, not a verdict on the principle; D48's certainty is a margin, not a calibrated probability, and its arm played longer;
the work's ingredients have names (Plan2Explore; Martius, Der and Ay) and its own question is doing them locally, compactly and with
growth (adopted as the programme's one line); the tree is not context-tree weighting (parked: compare them); report state, experience,
computation and communication apart; knobs first is a default, not a law (AGENTS.md), with recycling (Dohare et al. 2024) the comparator
to growth. PROGRAMME.md's stages P1 to P4 replace D1 to D3.

**P1** (`lab/p1.py`, `lab/v/p1.log`; dance_predictions 44 to 47; fresh seeds 94000+, 30 pairs, the design frozen before). Four arms each
with exactly 400 s of play (ending before the earliest onset), the same estimator (D47's records) and the same hand-over (D48's: a motor
not yet sure hands its rival to taste), so they differ only in which data play gathered: uniform turns, learning-progress turns, turns
to the unit that last raised certainty most; and no play.

| arm | gain from onset vs forage, 0-100 s | 100-300 s | knob within .2 | motors' best guess within 10% | sure: share; wrong |
|---|---|---|---|---|---|
| uniform | -.51 | +1.43 | 75% | 75% | 3%; 0 |
| learning progress | +.02 | +1.74 | 92% | 88% | 12%; 0 |
| certainty-directed | +.43 | +2.17 | 92% | 93% | 28%; 0 |

Paired: certainty-directed above uniform surely (+.94 [+.35, +1.57], +.74 [+.21, +1.30]; +18 points of motors within 10% [+8, +28]),
above learning progress but not surely (+.41, +.43; +5 points [-5, +15]). Motor beats in play alike (4529, 4942, 4652), so the gain is
per second and per joule. So steering play does gather better evidence than playing at random; learning progress, given the same
time, steers about as well; and D48's edge over learning progress was mostly that it played longer. "Sure" (margin 3) is
conservative: never wrong in 90 motors' claims, but reached by few. The same-observations ablation is built in: every arm used the
same estimator, so the differences are the data.

## D50: P2, three routes from play's records to the knob with no formula of ours (2026-11-11)

`lab/play3.py` (readout, readw), `lab/p2b.py`, `lab/p2c.py`; `lab/v/p2a.log`, `p2b_train.log`, `p2b_train60.log`, `p2b_test.log`,
`p2c.log`; dance_predictions 48 to 56. The user: try all three routes, then abstract, so that we haven't just evolved (designed) the
solution. Play4's frame throughout (a quiet spell, then the challenge); gains against forage, from the challenge's onset.

- **A. Taste discovers the readout in life.** After play, nine readouts (every signed combination of the two motors' measures, ours
  among them), 20 s each by taste: knob within .2 in 48%, and surely worse than no play at once (-1.01): log2 9 = 3.2 bits of choice is
  cheap in bits but dear in food, since 20 s of eating barely tells two readouts apart.
- **B. Evolution learns the readout across lives**, judged only by food (each training body's food at 17 knobs, a readout searched over
  them): it finds the same shape as ours, the difference of the two measures (+1.00 b0 - .70 b1 - .80), on 40 and again on 120 lives,
  tied with ours there. On fresh lives with real play it transfers (surely above forage, +1.40, +1.33) but is surely below ours (-.65,
  -.87). Its fitness, a forager set to the knob from birth, rates our formula at 1.7 a 10 s where real lives give 2.5 to 2.8: evolution
  found what its measure rewarded.
- **C. Slow play feeds a model of mixed commands, and the steady-view goal chooses the drive** (each mix's turning a beat from its own
  record; the minimum over the knob found by a fitted V; taste among it and +- .3): 32% within .2, no sure gain. Mixed records are
  often right (29.2 against 29.4 beats) but ten noisy points don't pin the minimum, and the true curve is no symmetric V.
- **By-product:** with the slow bank (periods 8 to 60 s, 20 s turns), our partners link is the best yet: 85% within .2, +2.43 and +2.32
  (20 pairs; to confirm on fresh seeds).

**The abstraction.** What made partners work wasn't knowledge of thrusters but two generic things: each motor's effect measured by its
own record, in the brain's own currency (beats until the view comes round), and an invariance asked of those measurements: partners
should have equal effect (or, for steady view, a drive should leave the view still). Partners' "formula" is the fixed point of a
comparator loop: nudge the two gains until the two measured effects per second agree; it needs only that a gain moves an effect one
way. So the inherited part is a homeostatic motif (equalise what your own records measure) plus the brain's knowledge of its own
settings, not physics. The three routes show how such a link can be acquired: designed (best), evolved (right shape, calibration only
as good as evolution's measure of fitness), or discovered in life by taste (honest, but too dear in food with these slow tastes). And
the evidence that carries it is the clean, long, single-action record: slow play supplies it, short mixed play starves any model.

## D51: understanding as coupling: the right knob is where senses and actions couple most (2026-11-11)

`lab/couple.py`, `lab/v/couple.log`; dance_predictions 57 to 59. The user's principle (PROGRAMME.md, the guiding principle): a brain
optimises for the simplest connection between its inputs and its actions in both directions; in bits, I(S; A) as small local
predictors capture it, which, unlike predictability alone, has no dark room (standing still or spinning makes the senses predictable
but the actions constant). First, before any mechanism: does it point at the right knob? The starting brain with its balance knob
fixed at 17 settings (-1.6 to 1.6), in play4's quiet spell (no taste at all), 50 to 400 s; at the interface in 50 ms bins, S (which
eyes pulsed) and A (which motors beat), coupling I(A_t; S_t+1) + I(S_t; A_t+1) from 4 x 4 tables, bias-corrected, in bits a second.
Fresh seeds 97000+, 20 lopsided bodies and 10 plain.

**Yes, sharply.** On lopsided bodies the knob of most coupling is within .2 of the right one in 95%, within .4 in all, median error .07,
correlation +1.00; on plain bodies it is 0 in all ten. Coupling against the knob's distance from right: +1.94 bits a second above a
body's mean at 0, +.76 and +.42 at .4 either side, below the mean beyond. Nearly all of it is the policy direction (senses to actions,
3.3 bits a second; actions to senses .2): with the balance right, seeing food starts a drive and the drive keeps the food in view, so the
senses go on governing the actions; with it wrong, the drive loses the block and the link breaks. No reward, no formula, no model of
thrusters: only how tightly the brain's own inputs and outputs go together. Not yet a mechanism: each point is 350 s at a fixed knob.
**How fast** (`lab/v/couple_speed.log`; the same lives, keeping each one's bins): the right knob beats one .4 off in 75% of
comparisons from 10 s of foraging, 88% from 30 s, 98% from 60 s; the best of 17 settings is within .2 of right in 60%, 80% and 95% of
bodies at 10, 30 and 60 s. Taste needed 300 s of trials and paid in food (D47); coupling needs no food, so a brain can search its knob by
coupling in the quiet, before reward exists, and again whenever rewards fall. Next: that search as a mechanism, in life.

## D52: the knob set by the brain's own coupling: no formula, no food, and better than ours (2026-11-11)

`lab/couple_search.py`; `lab/v/couple_search*.log`; dance_predictions 61 to 68. D51 as a mechanism. The starting brain forages from
birth; a counter at its interface (4 x 4 counts of which eyes pulsed and which motors beat, 50 ms bins, both directions) measures its
coupling over each 30 s; a golden-section search moves the balance knob by that alone (generic one-dimensional optimisation over the
brain's own setting), done when the bracket is narrow (bored: certain). No reward, no record of the body, no formula. Play4's frame
(a quiet spell, then the challenge from 400 to 600 s), scored from onset.

Steps, each traced (development seeds 98000+, 20 pairs): **as first built** (done at 180 s) surely above forage on lopsided bodies
(+1.55, +1.71; 80% within .2), but surely below forage on plain bodies (-1.4) though its knob ended .06 from 0. Traced: not an artefact
(a paired drive doesn't help); the score is that steep near 0 (.03 costs .9, .1 costs 1.7), because each beat is a kick of about 18
degrees: at exactly equal rates every kick pairs with the other motor's and cancels, while at a 3% difference an unpaired kick comes
every 30 or so beats and loses the block. Equal rates is a knife-edge, which foraging sits on by construction. **Judging longer near
the end** (bracket to .1, 60 s judgements) tied partners on lopsided bodies but bought no precision; **the top of a parabola through all
judgements** added nothing. **MacKay's Occam factor** did: the default (no adjustment) judged against the search's answer, 60 s each,
the answer kept only if its coupling is 10% higher. The plain body's cost went (-.14 after), at the price of time (done at a median
510 s, before onset in 30 to 50% of lives).

**On fresh seeds** (99000+, 20 pairs, frozen):

| arm | gain from onset vs forage, 0-100 s | 100-300 s | knob |
|---|---|---|---|
| told | +3.12 | +2.86 | |
| partners (play + our formula) | +1.01 | +1.04 | .09, 65% within .2 |
| coupling, finer | +1.61 | +1.63 | .05, 75% |
| **coupling + Occam** | **+1.53** | **+2.06** | .09, 82% |
| plain bodies: coupling + Occam | +.04 | -.04 | exactly 0 in 100% |

Coupling + Occam is surely above our formula in 100-300 s (+1.01 [+.23, +1.85]), and leaves normal bodies exactly as they were.

**What it means.** The knob that our formula set, and that taste and evolution could only roughly find, is set better by a principle
that knows nothing of thrusters, needs no food and no model of the body: make what you sense and what you do go together as tightly as
your small counters can tell, and don't move from your default unless the evidence clearly says so. The pieces are generic: a local
measure of coupling (the user's principle, D51), a generic search over one's own settings, boredom when the bracket is narrow, and an
Occam preference for no change. Not yet local in the strong sense: one counter and one search for the whole brain; and the search runs
from birth, not re-entered on clues (the user's suggestion), which needs something to change mid-life.

**Is precise timing of the kicks worth learning?** (the user, after D52's knife-edge; `lab/kick_timing.py`, `lab/v/kick_timing.log`;
dance_predictions 69.) A yardstick question: the told brain with equal rates and a scheduler that, at each pair of beats, fires both or
drops one, whichever keeps the heading's accumulated turn nearest straight (error diffusion), against the told rate knob. No: the
scheduler is slightly worse (-.35, -.54 surely in 100-300 s; dropped beats lose thrust), and the told rate knob on lopsided bodies
(+3.85, +4.11) already equals foraging on a plain body (+3.98, +4.16): there is no headroom for timing. The kicks are large, but at the
right rates they already spread finely enough; what learners lack is precision in the knob itself (D52). Two bugs traced in the smoke:
the scheduler only ever dropped one motor's beat, and an empty tick reset its account. (The script was first written over lab/timing.py,
D22's; restored from git at once, and this one named kick_timing.py.)

**Locality, first tries** (`lab/couple_local.py`; smokes of 4 to 5 lives; offline checks on D51's saved bins). Each motor a unit with
its own gain and its own counter (its own beats against the eyes). Offline: motor 1's own coupling peaks at the right balance in every
body from 60 s; motor 0's in 40 to 55% (it also does all the scanning). **Weight perturbation** (each unit tries +-.15 on its own gain
each 20 s and moves by the change in its own coupling): both units slowed down (mean log rate -.2 to -.8) instead of balancing.
Traced: in fixed 50 ms bins a unit beating at 50 a second beats in nearly every bin, so its activity carries little information and its
coupling is small; slowing raises it for no good reason. **Normalised** (coupling as a share of the unit's own activity's entropy, the
uncertainty coefficient): the slowing stopped and the normalised coupling still peaks right for motor 1 in every body, but a +-.15
nudge changes it far less than a 20 s window's noise, so 20 windows moved the gains nowhere useful (D16's and D19's wall for
perturbation learning). The global search worked by comparing settings far apart; a local one must too, without units spoiling each
other's comparisons.
**Each unit its own wide search, started at its own random moment** (golden section on its own log rate, judged by its own normalised
coupling; no coordinator): in a smoke of five lives, two lopsided bodies right (-.81 against -.68; .06 against .12), two wrong (0 against
.64; -1.15 against 1.23), and a plain body pushed to -1.85. The searches overlap and spoil each other's judgements, and motor 0's own
signal is weak. Stopped here, before tuning on smokes. **Where locality stands:** the coupling principle works when one search moves one
knob (D52); split across units that each judge by their own activity, it needs (a) a measure that doesn't reward a rate for its own sake
(normalising helps), (b) large comparisons rather than small nudges, and (c) units that don't disturb each other's comparisons. (c) is
the many-units problem again (D16), now with coupling as the teacher instead of taste.

## D53: the muscle-like body, and the experiments repeated on it (2026-11-11, night)

`lab/sigmoid_body.py`, `lab/drive.py`, `lab/retune.py`, `lab/knife.py`; the engine's switch (`lab/stage2_lang/sim.py`, `WLife.muscle`;
`MUSCLE=1` in every worker); `lab/v/muscle_predictions.md` (M1 on, with scores); PROGRAMME.md, Next. The user's paradigm: a pulse raises
a thruster's activation (decaying), and thrust is a sigmoid of it, so a lone pulse nudges and a fast burst builds to strong thrust, as
muscles grade force. Felt by hand first (`lab/drive.py`; keys scanned each tick, "." the left thruster turning right, "," the right).

**Step 0, the engine.** The reference path integrates thrust in sub-steps of .5 ms while an activation lasts; the compiled paths are
off when the body is on. With the switch off every life is identical (`lab/speed_fingerprint.py check`: 288 of 288). About 20% slower.

**Step 1, the body's tuning and the starting brain.** With activation decaying in 60 ms a lone pulse turns 4 degrees (the old body: 23),
but the starting brain, even retuned, lost half its food (efficiency 1.12 against 2.2): thrust builds and lingers about 60 ms, and a
reflex brain (see food, drive at once, stop on poison) overshoots. At 30 ms a lone pulse turns 7 degrees and it does better (1.62); the
user chose 30 ms. The retuning's gains didn't hold on fresh seeds (1.49 retuned, 1.51 old numbers, 30 pairs), so the starting brain is
the same on both bodies; on the new body it scores 1.51 against the old body's 2.41 (63%).

**Step 2, yardsticks and the body ladder** (D42's seeds, 5 pairs, 300 s). The told balance assumed thrust proportional to rate
(log k1/k0); on this body thrust is a sigmoid of rate, so the yardstick was wrong (told did no better than the starting brain). Recomputed
as the knob giving equal mean thrust at the drive's rate (`sigmoid_body.told_balance`: for a strength ratio of 2, .33 instead of .69), and
the tempo likewise. Then: plain 1.74, lopsided 0.23, told 1.60 (old body: 2.52, .94, 2.46): the balance still matters most and a told
brain recovers it. Drag drawn costs .33 (old .56).

**The knife-edge, measured** (`lab/knife.py`, 10 pairs, 300 s, efficiency in the last third against the knob's error from right):

| error | 0 | .03 | .1 | .2 | .4 |
|---|---|---|---|---|---|
| old body, plain | 2.52 | 2.49 | 1.94 | 1.09 | -.12 |
| new body, plain | 1.65 | 1.21 | .27 | -.21 | .06 |
| old body, lopsided | 2.31 | 2.27 | 1.47 | .83 | -.08 |
| new body, lopsided | 1.66 | 1.24 | .32 | -.27 | .14 |

The new body is steeper in the knob, not gentler: the knob sets rates, and its thrust is steep in rate (mean thrust .07, .27, .87 at 25,
50, 100 pulses a second), so a 10% rate error is about a 25% thrust error. In thrust terms the two bodies ask about the same precision.
**A correction to D52:** here the old body shows no knife-edge at 0 (an error of .03 costs nothing; the cost grows smoothly), where D52's
frame had .03 costing .9. The unpaired-kick account of D52 looks overstated: what costs is the drive's curvature, growing smoothly with
the error. The muscle-like body's premise (that coarse kicks make the balance a knife-edge) is therefore weaker than it seemed.

**Step 3, knob learners** (`lab/body_knob.py`, D43's seeds, 5 pairs, efficiency in the last third; `lab/v/muscle_body_knob.log`):

| learner | 100 s | 300 s | 1000 s | (old body, 300 s) |
|---|---|---|---|---|
| starting brain | .34 | .23 | .32 | .94 |
| told | 1.25 | 1.60 | 1.75 | 2.46 |
| trial: the bank (D19) | -.09 | .59 | .48 | 1.02 |
| trial: self-sizing (D36) | -.32 | .09 | .51 | .65 |
| measured: D20's counters | .23 | -.14 | .08 | 2.08 |
| measured: D43's beat register | .24 | -.05 | .24 | 2.37 |

The measurers, the old body's best, fail: they measure each motor's turning correctly, then convert it to a knob with the old body's
linear formula, wrong for this one. Trial by taste needs no formula and closes a little.

**Step 4, coupling.** Coupling's peak (`lab/couple.py`, `lab/v/muscle_couple.log`) is within .2 of the new body's own right knob in 95%
of lopsided bodies (median .10, correlation +.98), at 0 on every plain body: the principle needs no conversion. The coupling search
against partners on fresh seeds (`lab/couple_search.py ... s99000`, `lab/v/muscle_couple_search.log`, 20 pairs, gain from onset vs
forage): told +1.83, +1.85; partners (the old formula) -.16, -.17 (knob error .36); coupling, finer +.46, +.80; coupling + Occam +.32, +.77
(90% within .2), surely above partners in 100-300 s (+.95 [+.43, +1.47]); plain bodies left alone after the search. On the new body
coupling + Occam reaches 42% of told's gap in 100-300 s (old body 72%): the steeper knob asks more precision. **So the formula breaks
when the physics changes, and the principle doesn't.** P1's play arms not rerun (all use the partners formula).

**Step 5, touching pairs** (`lab/pairs.py`, D41's seeds, 5 pairs; `lab/v/muscle_pairs*.log`): touching pairs cost the told arm 44% on
the new body (1.49 to .83; old body 29%), declined rather than poisoned; the best careful driver wins +.24 over told (old +.16), the best
looker +.07 (old: below told); intervals overlap. Finer control helps a little, not surely; the loss is still mostly information.

**Step 6, the ladders and the tree** (`lab/ladders.py certify`, 10 pairs; D40's `teach.py` runs, 5 pairs; `lab/v/muscle_cert_*.log`,
`muscle_tree_*.log`). Rungs certified on the new body: seq 2, 3, 5, 7, 11, 13, 17 (seven, as on the old body); combo 1, 4, 5, 6 (old five);
time 2, 3, 6, 11 (old six). The tree solves seq 11 and 17, combo 1, 3, 5, 6 (4 not), time 2 and 5 (old: time 5 at .45, unsolved); seq 5
unsolved, as before. Its x often exceeds 1: the told arm (told the colour, driving as the starting brain) is weaker on this body, so read
solved rungs against that weaker yardstick. The scaling line's results hold on the new body.

**D52's knife-edge, checked** (`lab/knife_play4.py`, D52's own frame, fresh seeds, 20 pairs, both signs; `lab/v/knife_play4.log`): a
plain body's knob off by .03 costs .19 (not sure), by .1 costs 1.11 (sure). D52's ".03 costs .9" was its 10 pairs and one sign, and the
unpaired-kick account built on it an over-reading: the cost grows smoothly, steeply by .1. The Occam check still earned its place (the
search's errors were .05 to .1). This weakens the premise of the muscle-like body: the old body's sensitivity is steep, not a knife-edge.

**What D53 says.** The muscle-like body changes the physics, and with it every rule we had written from the old physics: the told
yardstick and the formula-based learners. The coupling principle carries over untouched (its peak at the body's own right knob, the
search guided by it beating the formula). Everything else of substance holds: the balance is still the body's one big number, touching
pairs still lose to missing information, the ladders certify much as before and the tree still climbs them. The new body forages at
about two thirds of the old one's level with the same starting brain and is steeper in its knob. Whether to adopt it is the user's call;
on this evidence it teaches mainly the formula-versus-principle lesson.

**Locality, a fourth try** (after D53; `lab/couple_local.py`, `local:drive`; smoke, 5 lives, the old body): each unit's own wide search,
started at its own random moment, counting only the bins while it is driving (a motor unit knows that from its own drive input), so
motor 0's scanning no longer confounds its signal. Still poor: one of four lopsided bodies roughly right, two with the wrong sign, a plain
body pushed to -.91. The units' searches (about 250 s each, within a 400 s quiet spell) overlap, so each judges its own setting while the
other's is moving. What would cure it is units that take turns or don't disturb each other's judgements: a design question, left for the
user rather than tuned at night.

## D54: taking turns: Sepulchre's half-centre makes the local coupling search work (2026-11-12)

`lab/couple_local.py` (`HalfCentre`; arms local:halfj, local:half, local:turnsj), `lab/couple_tempo.py`; `lab/v/half_centre*.log`,
`couple_tempo*.log`; dance_predictions 70 to 77. The user: taking turns is a Sepulchre theme. The locality tries of D52's end failed
because two units changed their settings at once, so neither could tell whose change moved the coupling (D16's credit problem). In a
half-centre two units inhibit each other, and fatigue hands the activity over, with no coordinator. Mapped: a unit's turn is its search
(golden section on its own gain, 20 s a point, an Occam check at the end); while it searches the other holds (inhibition); at the end it
is bored (fatigue: D48's certainty); if it moved, the other's landscape has changed, so the other rebounds and takes the next turn;
play ends when no unit has drive left, or at the first taste.

**The signal matters first.** By its own coupling (its own beats against the eyes, normalised, counted while driving) a unit fails even
taking turns: its own coupling rises with its own rate whatever the balance (traced: unit 1 favoured +.79 where -.64 was right). The
balance is a property of the joint behaviour, so each unit judges by the joint coupling of the eyes with both units' beats, which it
sees from its neighbour: local within the half-centre, D51's measure.

**Then turns are what make it work** (play4's frame, 20 pairs; gain from onset against forage):

| arm | dev seeds: 0-100 s | 100-300 s | within .2 | fresh seeds: 0-100 s | 100-300 s | within .2 |
|---|---|---|---|---|---|---|
| global search + Occam (D52) | +1.32 | +1.32 | 70% | +1.53 | +2.06 | 82% |
| **two units taking turns, joint signal** | **+1.74** | **+1.50** | **80%** | **+2.01** | **+1.71** | **90%** |
| both at once, joint signal | +.54 | +.33 | 40% | +.25 | +.37 | 45% |
| taking turns, own signals | -1.38 | -1.28 | 0% | | | |
| both at once, own signals | -.27 | -.38 | 20% | | | |

Taking turns is surely better than searching at once with the same signal (dev +1.20, +1.18; fresh +1.76, +1.34), ties the global
search, finishes before food in every life (400 s), and leaves plain bodies exactly alone (100%). So the credit problem among units
judged by one shared signal is solved by alternation, as in Sepulchre's circuits, not by a coordinator.

**Two knobs: balance and tempo** (thrusters and drag both drawn; told knows both). The units set their own rates, so between them the
balance (difference) and the tempo (sum). The balance is found (75% within .2; +1.54, +1.72, tied with the global search), the tempo not
(correlation with the drag +.21), and told stays far ahead (+3.78, +3.54). **Why: coupling and food disagree about tempo** (the balance
told, the tempo on a grid, no reward): coupling peaks at about half the right speed (-.8 in log), food at the right one or a little
faster (correlation with log drag +.90). Not the binning (beat counts give the same). A slower creature's seeing and doing go together
more tightly; a faster one eats more. Tempo trades speed against control, and coupling values only control. So the principle sets the
knobs that make behaviour coherent (the balance); a trade-off between speed and care needs the outcome, taste (the review's point:
predictability, information and decision value are different objectives).

## D55: a brain that takes up new parts: first, is there anything to gain? (2026-11-12)

`lab/newparts.py`, the engine's switch (`sim.WLife.extra`, `EXTRA=1`: two more thrusters a side at a half and a quarter of the
original's strength, on motor lines 2 to 5 wired at random, alive from a moment drawn each life, each firing costing in proportion to its
strength; off, every life identical: 288 of 288); `lab/v/newparts_predictions.md` (N1 to N3), `newparts_yardstick*.log`. The user's new
kind of experiment: not mismatches with the world or flaws in the body, but new parts given part-way through life, to be taken up in it.
First the yardstick (as for any rung): hand-designed brains told the wiring, the parts alive from birth, routing the starting brain's
beats to the new thrusters (a finer scan on the quarter at 4 times the rate, a finer drive on the halves or quarters, both), 10 pairs,
300 s, efficiency in the last third:

| world | starting brain | best design | gain |
|---|---|---|---|
| plain | 2.18 | drive on the halves (or quarters) | +.31 [+.03, +.59] |
| lopsided, told its balance | 2.09 | scan on the quarter | +.38 [+.12, +.66] |
| touching pairs (2 mm) | 1.42 | scan on the half | +.11 [-.15, +.36] |

Finer control buys about 15% at most: real, but below a rung's bar (a gap surely above .25), and nothing where precision should matter
most. The same answer as D41 and D53 from a third direction: this creature is limited by what its eyes can tell it (where across the
corridor a block lies, D21), not by the size of its kick. So new thrusters leave little for in-life learning to find; a new sense would
leave much more (D21's yardstick: what knowing where blocks are is worth; D24 prepared a split eye).

**Then a new sense with the new thrusters** (the user's choice: the split eye and the small thrusters; `lab/v/newparts_yardstick2.log`;
N4 to N6). The split eye in the engine (`sim.WLife.split`, `SPLIT=1`): each eye pulse's half of the corridor, drawn by each half's
share of that colour's light from its own stream, arrives on line 2 or 3, wired at random, alive from a moment drawn each life, only to
a brain with inputs for it (off: identical lives, 288 of 288). Designs told the map: D24's reflex (while driving, food pulses from one
half and not the other turn the body towards it) steering with the big thruster (D24's partner beat 10 ms late) or one small kick:

| world | base | steer, big | steer, half kick | steer, quarter kick | quarter steer + drive on the halves |
|---|---|---|---|---|---|
| plain | 2.18 | +.69 | +.65 | +.94 [+.69, +1.22] | +.96 [+.79, +1.14] |
| lopsided (told its balance) | 2.09 | +.60 | +.10 | +.72 [+.51, +.92] | +.68 |
| touching pairs | 1.42 | +.53 | +.58 | +.64 | +1.07 [+.76, +1.39] |

The new sense is worth about +.6 with the old kick and up to +1.0 (45% on a plain body, 75% in touching pairs, where knowing which side
the poison lies on finally pays) with a small kick to act on it; the small thrusters alone almost nothing. Sense and fine actuator are
worth most together: certified gaps for in-life uptake (G2) to find.

**G2, taking up the parts in life: first tries** (`lab/uptake.py`; smokes; N7 running). One growth event: the split eye and the new
thrusters come alive together at a moment drawn between 100 and 300 s; food from birth; 900 s lives. Raw material: a reflex arc from
each new sensor line to each new motor line (2 x 4), born off; an arc that is on fires one kick of its motor at each food pulse on its
line while driving (a new input attached to an existing behaviour; nothing says which line or thruster is which); the clue to start is
the new lines beginning to carry pulses. Told the two right arcs, a life ate 151 against the base's 103: the arc form suffices.
- Each arc tried on and off for 15 s, judged by joint coupling, Occam default off: wrong choices; one window each is noise (1.3 to 7.6
  bits a second).
- On, off, on, off, evidence per arc, decided at two standard errors: about two visits per arc fit in a life; by the sum, an hour needed.
- Each kick a probe (one of a line's arcs or none, in turn; outcome the food pulses in the next .3 s): the right arc highest on one line
  in both lives traced, not on the other; each outcome's spread about 2.5 against differences of about .4, so about 150 probes per arc
  are needed and a life gives about 80. Starved, not wrong.
Food is a poor teacher for a new steering arc: one kick changes whether food stays in view only a little, and the count is noisy.

**Then play first, judged by the new sense** (the user: the brain needs an instinct to play with its senses and body first; learn3,
learn3b in `lab/uptake.py`; `lab/v/uptake_3000.log`, `uptake_play.log`; N7 to N10). First, food as the teacher fails even in 3000 s lives
(learn -.03, learn2 -.28 against base, told +.69): it is not only evidence; a steering kick's effect on food is too small and noisy to
show within a life. Play instead, with the new sense watching the new motors: once the new lines wake, the base behaviour pauses; still,
whenever something is in view on the new lines, one new motor's kick or none, in turn, then a pause for the motion to fade (a
look-around beat of the scanning motor when nothing is in view); each motor's effect is how it moves activity between the two new
lines. A line's candidates are the motors that surely move activity out of its half (towards what is there). Traced first: played while
scanning, the kicks' effects drowned in the scan's own 18-degree beats (none sure in 120 kicks each); played still, the sides group
correctly and the half thrusters stand out (-3.5, +3.3 standard errors), and a sure candidate was always on the right side.

| 10 pairs, 900 s, parts at 100 to 300 s | efficiency | vs base |
|---|---|---|
| base (ignores the new parts) | 2.54 | |
| told: the split-eye reflex | 3.34 | +.79 |
| told arcs (the learner's own form at its best) | 2.96 | +.42 |
| **play, then the surest candidate wired (learn3b)** | **2.91** | **+.37 [+.17, +.57]** |
| play, then taste confirms (learn3) | 2.68 | +.14 |

A brain given a new sense and new thrusters part-way through life wires them up by itself, by playing still with them and watching
what each new motor does through the new eye, and surely gains: 88% of what its reflex form gives told the right arcs. Taste confirming
made it worse: food is the weaker teacher again. Right side on both lines in 40% of lives; elsewhere one line, or a half thruster where
the told arcs use a quarter. Senses and actions calibrated against each other first, food only after: the user's embryology picture.
Fresh-seed confirmation running.
**Fresh seeds** (104000+, 10 pairs; `lab/v/uptake_play_confirm.log`): play-then-wire +.11 [-.12, +.34], not sure; but the told arcs
themselves only +.13 [-.06, +.30] there (+.42 on the development seeds). The learner reaches about 85% of its arc form on both seed sets
(right side on both lines in 50% here); the form's worth varies, and is far below the told split-eye reflex (+.79 to +.94), which steers
only when one half sees food and the other doesn't. The weak link is the arc form, not the learning. Next: lateral inhibition between the
two new sensor lines (an arc fires only while the other line is quiet), a generic local motif, into the arcs.

**With lateral inhibition between the new lines** (an arc fires only if its line saw more food pulses than the other in the last .2 s:
D24's condition as one line suppressing the other; `lab/v/uptake_inhib*.log`; N11, N12). Development seeds (103000+): play-then-wire
+.46 [+.30, +.63] above base (the told arcs +.42; with inhibition, oddly, +.22). **Fresh seeds (105000+): +.39 [+.22, +.58], surely**,
tied with the told arcs with inhibition (+.39). So a brain given a new eye and new thrusters part-way through life, playing still with
them and wiring the motor that moves activity out of each new line's half to that line, surely takes them up, on creatures it never saw,
reaching what the reflex form gives told the wiring. What carried it: play judged by the new sense, not by food (food failed even over
3000 s), with the old behaviour paused so that one kick at a time is the only motion. What limits it: the reflex form (a kick per food
pulse, worth +.13 to +.42 told, against D24's tuned reflex at +.8 to +.9), and a preference for the half thrusters, whose effect play
sees most clearly, where quarters steer better.

**Play's candidates chosen by coupling** (learn3c; smoke, 3 lives). Play's sure candidates are only ever the half thrusters (the
quarters' effects too small to be sure of in the time), and joint coupling preferred no steering arc to a right half one (4.56 against
5.79; 3.07 against 4.36), though such arcs surely raise food. A steering kick makes the drive less steady; coupling values steadiness,
steering trades some for food: the tempo lesson of D54 again, a choice for the outcome, and food was too slow a judge here. Stopped at the
smoke; play-then-wire-the-surest stays the learner. Where it leaves the principle: coupling sets what makes behaviour coherent (the
balance, which motor turns which way); how much to trade steadiness for food (tempo, steering strength) needs a reward signal faster
than whole-life food, which we don't yet have.

## D56: hunger sets how fast to act; a world whose food regrows slowly (2026-11-12)

`lab/vigour.py`; `lab/v/vigour*.log`; newparts_predictions V1 to V5. Coupling settles what makes behaviour coherent but can't settle how
fast to act (D54). The user asked whether we have hunger (only a fixed boredom timer in the starting brain, and a hunger node in the
minimal-circuit line), and proposed a world where eaten food regrows only after a delay, so that rich and lean spells alternate. The
known answer: vigour follows the reward rate against the cost of effort (Niv, Daw, Joel and Dayan 2007); foraging theory's marginal value
theorem (Charnov 1976) likewise turns on intake against its average.

- **Food constant, drag drawn** (the tempo searched over 40 s windows by recent food, or by coupling): neither tracks the drag (correlations
  +.19, +.18); recent food is too noisy a judge there (about 16 +-5 net a window). Coupling's preference for slowness costs less in
  efficiency than in food per second, since slowness saves energy (+.19 surely above fixed).
- **Regrowth delayed** (food hidden for 60 or 120 s once eaten; 3 to 9, or 0 to 2, of 18 food blocks alive): simply going slower surely
  saves (+.21, +.24). Hunger as recent food against the creature's own long-run average helps little (+.08, +.05): it detects changes,
  but a world lean all along comes to feel normal. **Hunger as recent food against a fixed, inherited "normal"** (the plain world's rate)
  surely pays, +.33 and +.36, above always-slow, and costs nothing sure in the plain world (-.10). It sits at its slowest bound nearly
  all life in the lean worlds, so part of the gain is plain slowness.
So the two signals divide the work: coupling, what makes action coherent; hunger, measured against an inherited sense of normal, how
vigorously to act. Not yet: play in the lean spells, or speed varying within a life as food comes and goes (the trace shows hunger pinned).

**Fresh seeds** (108000+, 10 pairs; `lab/v/vigour_regrowth_confirm.log`; V6 wrong): hunger against the fixed normal surely *costs* in
the plain world (-.40 [-.71, -.11]), helps surely only at 120 s regrowth (+.34; at 60 s +.18, not sure). Its normal (.6 meals a second)
is too high for many of these creatures, which feel hungry in a world that is fine. Not tuned on these seeds (forking paths). The
difficulty is real: a fixed normal must match the world; a normal learned from one's own past fails in a world lean all along. Parked:
food per unit of effort (meals per pulse against the exchange rate of a meal for pulses, which evolution knows) as the yardstick.

## D57: play in the lean spells, and whether taking up new parts scales (2026-11-12)

`lab/uptake.py` (`UPTAKE_WORLD=regrow60`, arm leanlearn3bI; `EXTRA_N` for 1, 2 or 4 new thrusters a side); `lab/v/uptake_lean.log`,
`uptake_scale_*.log`; newparts_predictions V7, G1, G2. The user's suggestion, joining D55 and D56: play when food is scarce, when there
is little to lose. In the 60 s regrowth world, with the new eye and thrusters growing at 100 to 300 s (10 pairs, 900 s): playing at once
(D55's learner) +.20 [+.09, +.33] above base in the last third, playing only while recent food is below its long-run average +.14 [+.04,
+.24]; over the whole life both below base (-.12, -.14): play's time has not paid back within 900 s. Playing only when lean changed
nothing, since after the first minute food is scarce most of the time in this world (play finished 285 and 315 s after growth). When to
play mattered less than how long play takes, which is the scaling question below.

**Does it scale?** (G3; 1, 2 or 4 new thrusters a side, at strengths from a half down to .18; 1200 s lives, 10 pairs, plain world):

| new thrusters a side | play done after growth | last third vs base | whole life vs base |
|---|---|---|---|
| 1 | 141 s | +.33 [+.16, +.52] | -.15 |
| 2 | 243 s | +.33 [+.20, +.45] | -.36 |
| 4 | 446 s | +.46 [+.10, +.76] (told arcs +.34) | -.73 |

Play takes up the new parts correctly at every size and surely gains afterwards, but its time grows in proportion to the parts (1 : 1.7 :
3.2): it tries one thruster at a time, as it must, since every new thruster moves the same view and their effects interfere (D54).
Over a whole life its cost grows faster than its gain. So, as built, uptake by play scales in correctness but not in time. It would
scale where parts don't interfere (tried at once, D54's prediction for independent parts) or if play learned more per kick (a side's
thrusters all move the view the same way, so one kick could teach about its neighbours).
**Play bored from certainty, per motor** (`lab/v/uptake_scale_4B.log`; G4): a motor sure at 3 standard errors played no more. No gain at
4 a side (play 489 s after growth against 446; whole life -.74 against -.73; both lines right in 10% against 35%): the kicks only move to
the quarters, which never become sure. Learning more per kick needs another idea.

**b. Play until you know what you need** (the user: try b, then a; arms ending N; `lab/v/uptake_need_*.log`; G5, G6). Play ends as soon
as each new eye line has a thruster surely moving activity out of its half, not when every thruster is known; the surest is wired.

| new thrusters a side | median play after growth (all known) | whole life vs base (all known) | until needed vs all known, paired |
|---|---|---|---|
| 1 | 121 s (141) | -.02 (-.15) | +.13 [+.05, +.22] |
| 2 | 110 s (243) | -.06 (-.36) | +.30 [+.17, +.44] |
| 4 | 373 s (446) | -.52 (-.73) | +.21 [+.04, +.37] |

Learning what the wiring needs, rather than everything about every part, surely helps at every size, makes play flat in time up to two
parts a side (where it now nearly pays for itself within a life, and wires the right sides in 80%), but not at four, where each kick is
spread over more thrusters and the strong ones take longer to become sure. The principle is boredom from certainty applied to the goal
(a usable connection), not to each part.

## D58: body and rule in one life: knowledge makes skill worth having (2026-11-12)

`lab/mixed.py`; `lab/v/mixed_seq11.log`, `mixed_seq11_confirm.log`; newparts_predictions M1 to M3. The user's option a: a challenge where
both matter in one life. A rung of the sequence ladder (a hidden word of 11 letters: the food colour follows it, learned from taste by
D40's tree) and the new parts (split eye, two more thrusters a side, growing at 100 to 300 s, taken up by play until needed, with lateral
inhibition). 1200 s lives, 10 pairs, efficiency in the last third against the starting brain:

| arm | development seeds | fresh seeds |
|---|---|---|
| starting brain + play | -.06 | -.26 [-.47, -.08] |
| tree (the rule) | +2.99 | +3.10 |
| tree + play | +3.34 | +3.22 |
| tree + told arcs | +3.22 | +2.98 |
| interaction: both, less the sum of each alone | **+.40 [+.03, +.80]** | +.38 [-.15, +.88] |

The gains don't simply add. Play's new steering reflex turns the creature towards whatever it believes is food, so for a brain wrong
about food half the time (the starting brain on this rung) better steering is worth nothing, or surely harms (fresh seeds: -.26), while
for the tree, which knows the rule, it helps. The interaction keeps its size on both seed sets (+.40, +.38), sure on one: suggestive, not
established. If it holds, it says something about growing brains: a new skill is worth what the knowledge directing it is worth, so
skills and knowledge should grow together, and taking up a new part is best judged after the brain knows what to use it for.

## D59: the growing network (2026-11-12)

The user's idea, after Dan Goodman's talk and Béna & Goodman 2025 (`PROGRAMME.md`, Now). `lab/grownet.py` (arms in `lab/teach.py`),
`lab/grownet_switch.py`; `lab/v/grownet_seq.log`, `grownet_switch.log`, `grownet_switch_ablate.log`; predictions R1 to R7. Blocks born
beneath contradictions joining any two units active together (senses or blocks: sequences of sequences); a readout on each; use flowing
back from right guesses to the blocks each is made of; blocks unused for 200 s fade, taking their dependants; two blocks firing alike over
30 steps lose the less used. D40's tree is the hand-shaped case (each recruit's partner fixed, nothing pruned).

**On the sequence ladder** (20 pairs, unpaired intervals): it matches the tree on 5 and 11 letters (.57 both; .84 against .73) and is
solved on 17 letters where the tree is not (.62 [.55, .69] against .50 [.42, .58], P 64). With P 16 all fill their material and tie.
Its blocks rise with the word: 8, 27, 30 (material 30 a stream).

**When the hidden word changes mid-life** (11 letters, a new word at 500 to 700 s, 1500 s lives, last third, paired, P 64):

| | development seeds | fresh seeds |
|---|---|---|
| tree | -.46 | -.34 |
| net | **+1.15** (unchanged word: +1.34) | **+1.01** |
| net, no fading | | +.78 (-.24 [-.02, +.49]) |
| net, no duplicate removal | | +.07 (-.94, sure) |
| net, neither | -.44 | |
| net - tree | +1.61 [+1.18, +2.03] | +1.36 [+.94, +1.77] |

The growing network relearns a changed world; the tree and the unpruned network stay stuck on the old word. The work is done by removing
duplicates, not by fading (R7 the wrong way round): births keep remaking blocks already there (about 140 removed a life, 35 faded), and
left alone they fill the material. Recycling the redundant keeps material free for whatever comes next, Dohare's finding in a new form.
With P 32 neither word is learned by anyone.

Why removing copies works (the user asked, 2026-11-12): the same mistake in the same situation makes the same new block again, so
growth by local rules makes copies; copies add nothing but hold material. Redundancy shows at once and locally (two blocks firing alike),
uselessness only over a long time, so clearing copies keeps room free far faster than fading. And it stands in for a check no local
brain can make: a newborn can't search the brain for its twin, but it can be made and pruned when it fires like a neighbour. Grow freely,
prune copies: the local alternative to looking before you grow (as young brains overproduce and prune). The finding depends on this
growth rule making copies; one that never made them would need no removal, but only by a check that isn't local.

**The blood supply, first look** (smoke, 2 pairs; `lab/v/grownet_predictions.md`, stage 2): blocks firing at the same moment share a
supply by their use; a block whose store runs out is recycled; no explicit fading or duplicate removal. It relearns a changed word about
half as well as the full network (212 against 417, summed). The supply's size hardly matters (it rarely runs short); what acts is the
zero-sum split among blocks firing together. Its newborn's store sets turnover against keeping: small, and newborns die before they prove
themselves; large, and copies fill the material as with no removal. Open: a split that protects the young (a newborn's share from its
parents' use, say) without a tuned store.

**Competition for a supply** (the user's blood-supply idea; `lab/v/grownet_predictions.md` R8 to R12; `grownet_supply*.log`,
`grownet_why*.log`). Blocks firing at the same moment share a supply; a block whose store runs out is recycled; no written fading or copy
removal. Version 1, sharing by use with newborns inheriting their weaker parent's standing: ties the written rules when the pattern
changes (+1.19 against +1.15; fresh seeds +.97 against +.80, and +1.77 above the tree) but surely costs when it doesn't (-.35): a block
that looks far back fires only beside its shorter parents, which hold more credit (their descendants' successes pass down to them), so
the specialist starves beside its own parents. Version 2, parents fed by their dependants and the rest sharing by their own record: worse
(turnover collapsed). Its supply from 1 down to .03 a second: best near .3, never tying. In versions 1 and 2 at 1 a second or more the pool
never ran short, so the "competition" was only a zero-sum split of what the firing blocks needed. Parked, with the question: how should a
supply be shared so that rivals compete but parts of one chain don't? (QUESTIONS.md.)

**Does its size follow the problem?** (`lab/grownet_scale.py`; `lab/v/grownet_scale.log`, `grownet_material_*.log`; R13 to R15.) Patterns
2 to 17 steps long (each step red or blue), material plentiful (128 a stream), 1500 s lives: share of the gap closed .91, .95, .89, .88, .88,
.82, .81; blocks alive 17, 20, 28, 40, 44, 43, 48 (about 15 plus 2 a step, far below the material). On the pattern 17 steps long, fresh
seeds, material from 16 to 512: share .32, .31, .60, .86, .85, .85, blocks 6, 14, 30, 45, 49, 49. A bigger problem needs only more raw
material, and the network takes what it needs and no more; nobody tells it the problem's size.

References for the supply question (checked 2026-11-12): van Ooyen & Willshaw 1999, Proc. R. Soc. B 266:883 (competition for neurotrophic
factor; and with Ramakers 2000, inputs spread apart on a target's dendrites compete less and coexist); Baum 1999, "Toward a model of
intelligence as an economy of agents", Machine Learning 35:155 (credit must be conserved, or parasites multiply); Carandini & Heeger 2012,
Nat. Rev. Neurosci. 13:51 (normalisation pools). Version 1's fault in Baum's terms: credit was copied in full to every ancestor, not paid.

**The economy** (the user: competition defined by the graph; R16 to R18; `lab/v/grownet_economy*.log`, `grownet_why3.log`). No written
fading or copy removal: a right guess earns 1; a block keeps half and pays the rest to the two units it is made of, which do the same, so
credit is conserved along a chain (Baum); a parent funds its newborn from its savings, so only blocks that have earned can reproduce; every
block pays rent to exist; a block in debt is recycled with its dependants. A copy never guesses (its older twin does), earns nothing and
is evicted; a specialist pays its parents instead of competing with them. A first version also charged for each firing: it starved the
general blocks (short look-backs fire at nearly every step but earn only shares), whose recycling took their specialists with them
(-.54 when the pattern doesn't change). With rent alone:

| | development seeds | fresh seeds |
|---|---|---|
| pattern changes: economy, written rules, tree | +1.02, +1.15, -.46 | +.91, +.89, -.38 (economy - tree +1.29 [+.92, +1.59]) |
| pattern unchanged: economy, written rules, tree | +1.13, +1.34, (+1.25 elsewhere) | +1.18, +1.50, +1.27 |

So one generic mechanism, a conserved economy along the graph, does what two written rules did when the world changes, at a cost of .2
to .3 when it doesn't (sure on one seed set). The charge for activity, the user's blood-supply idea in its first form, was what hurt: in
this network the most active blocks are the general ones everything rests on. A supply limiting activity may still make sense among rivals
(siblings), not along a chain.

**Stage 5, taking away the streams we chose** (`lab/v/grownet_predictions.md` R19 and after; `grownet_one_*.log`; bench
`lab/grownet_bench.py`). The two streams were our choice, and one, the food colour at each good meal, moves exactly as the pattern
lesson does. One stream of every taste (four symbols: colour eaten, good or bad): ties the two streams on the combination lessons (food
by the last colours eaten) but surely loses on the pattern lessons (.38 against .56 at 5 steps, .50 against .77 at 11): a bad meal doesn't
move the pattern on, so bad tastes break up the run a block must recognise. A version with separate sense lines, where each block keeps
time by a clock of its own (every taste, or one sense line's firings) so it could count good meals by itself, does worse still; on a
bench without a body it reaches 84% where the two-stream net reaches 98%. Most new blocks draw a clock that carries nothing, and the
lineages they start are the ones that grow. Parked: how a network finds which clock matters, by local rules.
On the bench, the clock was not the limit: with the useful clock forced the separate-lines net still reached only 84%. Two senses fire at
each taste (good, and the colour eaten), and growth kept happening beneath "good", a sense right 80% of the time on its own, so blocks
never took in the colour just eaten. Joining units at the same moment, and growing beneath the most specific unit while the surest
speaks, lift it to 70-89% (patterns 5 steps) and 66-73% (11), against the two-stream net's 98% and 91-94%. Open: which unit should grow,
and which speak, when several senses fire at once.

**A stream for every sense line** (`lab/v/grownet_five_*.log`; R20). Five streams, ticking at every taste, good taste, bad taste, red
eaten, blue eaten, each recording the same four symbols (colour eaten, good or bad), with the same network on each and the gate choosing
by record. None is ours. The gate picks the good-meal stream on the pattern lessons and the every-taste stream on the combination
lessons, by itself; with the same material a stream as our two (32), it matches them: .56 and .76 on patterns 5 and 11 steps long (ours
.56, .77), .49 and .70 on the combination lessons (ours .64, .79, intervals overlapping). The price is material for all five streams. So
the scaling result no longer rests on a stream we chose; it rests on our having offered every sense as a clock, which is generic.

**Plan B1: no symmetry told** (`lab/v/grownet_b1_*.log`; R21). Until now every brain read a bad taste of one colour as "the other is
food", which builds in that exactly one colour is food. Without it (each block keeping a table of what each eye led to), the network at
first never steered: the creature always ate the default's choice, so a stream that disagreed could never show it was better. The
told symmetry had hidden an explore-or-exploit problem. With who steers chosen by sampling each source's record (Thompson sampling, from
the brain's own noise) it learns every lesson, at a cost of .1 to .27 of the gap (pattern 11 steps .65 against .76; combination 3 .57
against .70; plain world -.10). As expected in bits: untold, a taste speaks only of the eye eaten, so learning needs about twice the
tastes, some spent trying. Open (QUESTIONS.md): can a network learn the symmetry itself and earn the evidence back?
Then (R22 to R23): each unit learning the symmetry by Bayesian model comparison earned nothing back; an ablation (B1's steering with the
symmetry told) showed that on the pattern lessons the whole price was the change of steering, not the readouts, correcting the
explanation above. Scoring every source whose choice was the eye eaten (not only the one steering) makes told and untold readouts equal;
what remains, .05 to .15 below the told brain with its Occam gate and -.10 in the plain world, is exploring: untold, a brain must
sometimes try the other colour to learn what it gives. B1 closed: the told symmetry was worth that exploring.

**Checked paired** (R24, `lab/v/grownet_17_paired.log`, fresh seeds 91000+, 1500 s, P 64): on the pattern 17 steps long the network
ties the tree (+.40 both; .00 [-.35, +.38]). The first, unpaired reading (solved where the tree was not) does not hold; the network's
advantages that stand are relearning a changed pattern and needing no hand-fixed recruiting rule.

**Plan B2, first step: no vouching** (R25, R26; `lab/v/grownet_v_*.log`, `grownet_cv_*.log`). Every brain so far learned only from
tastes its eyes vouched for (a hand rule: the followed eye pulsed within the hold, the other not since). The growing network learning
from every taste, what was eaten taken as the eye that pulsed last, matches it on the lessons (pattern 5 .58, 11 .70; combinations .52,
.74) at -.10 in the plain world. With the symmetry untold too, the lessons still hold (.50 to .69) but the plain world costs .37: false
poisons (the other colour eaten by accident) enter every source's record and feed the exploring. Each hint alone was worth little; the
two together guard the plain world.

**The user's local competition, made trophic** (R28 to R32; `lab/v/grownet_local*.log`, `grownet_surprise*.log`, `grownet_why4.log`,
`grownet_trophic*.log`). Every unit holds a pool refilled at a fixed rate; the blocks built on it that fire together share it; a block
never competes with its parents nor with blocks under another parent; the starved are recycled with their dependants; no written fading
or copy removal. Sharing by each block's own record ties the written rules when the pattern changes (+1.09 against +1.15; fresh +1.14
against +.89) but costs .2 to .45 when it doesn't; recycling pressure scaled by surprise didn't cure it. Traced: a block in the middle of
a chain seldom speaks (its children do), so on its own record it starves among its siblings and takes its specialists with it (13 to 23
blocks alive of 30). Sharing instead by standing that includes credit passed down from the blocks built on it (support flowing from users
to parts, as in trophic theory), newborns inheriting it:

| supply 3 a second | seeds 90000+ | fresh seeds 93000+ |
|---|---|---|
| unchanged, against the written rules | -.11 [-.23, +.03] | -.06 [-.26, +.18] |
| changed, against the written rules | +.23 [-.17, +.60] (supply 1: +.32, sure) | -.23 [-.59, +.17] |
| changed, against the tree | | +1.47 [+1.09, +1.76] |

Never surely below the written rules on either set: the first generic clearer with no cost in a world that doesn't change. Competition
among siblings, support flowing from users to parts: the two together are the answer to the question parked above (QUESTIONS.md).
With material unlimited (R33, R34), the trophic version's size is set by the competition among siblings, not by its supply (3, 10, 30 a
second the same): it grows with the pattern, 14 to 28 blocks, a little small for the longest (.70 against .81 at 17 steps). Every sense a
stream and cleared this way (R35, paired, fresh seeds 92000+): within noise of the written rules on three lessons, .14 short on one
(combination 3). The generic brain so far: no stream chosen, no rule for what to keep.

**Robustness** (R36, R37). On the muscle-like body, unchanged, the growing networks match or beat the tree (pattern 5 surely above;
others tied): like coupling (D53), the mechanism carries over. On the timing ladder, with no clock among its streams, they still beat
the tree with clocks at rungs 2 and 3 (.33 to .40 and .19 to .25 against .28 and -.08; none solved): bad tastes mark the swaps, so a
stream of tastes stands in for a clock. A clock stream (the brain's own oscillators, phase drifting, never shared with the world) is
the obvious next part to offer it.
**The generic brain on a changing pattern** (R38, fresh seeds 94000+): every sense a stream, cleared by trophic sibling competition,
relearns a changed pattern of 11 steps (+.83, against the tree's -.53: +1.36 [+1.00, +1.70]) and ties the written rules and the tree
when nothing changes. Every property of D59 so far holds with no stream chosen and no clearing rule written.
**Remembering** (R39, A-B-A world: pattern A, then B at 400 to 500 s, then A again at 900 to 1000 s; fresh seeds 95000+). When A returns
the tree and the unpruned net do well (+.78, +.81), having never learned B; the growing net relearns A (+.86, as when a pattern changes
for good); the generic brain (every sense a stream, trophic competition) does best, +1.13, surely above the growing net. Traced
(`lab/grownet_memory.py`, `lab/v/grownet_memory.log`, three lives): not memory. The generic brain keeps none of A's blocks through B
(every block alive at the end was born after A's return); it relearns quickly. The growing net with written rules keeps 10 to 17 of its
30 from A's first spell, yet scores no better than when the change is for good. Clearing out cost nothing here, and bought 1.3 to 1.4 when
the change is for good; real remembering (old blocks kept and reused when their world returns) is not yet shown by any of them.

## D60: the scaling curve of the generic growing brain (2026-11-12)

README's scaling test, its first and fourth parts, for the generic brain (every sense a stream, trophic sibling competition, no rule
written for which stream or which block to keep; arm net5Lu3). `lab/teach.py`; `lab/v/grownet_curve_*.log`; predictions R40 to R44. All
rungs of the three ladders, material 40 to 640, 10 pairs:

| material | 40 | 80 | 160 | 320 | 640 |
|---|---|---|---|---|---|
| sequences, highest rung solved (development seeds) | 3 | 5 | 11 | 17 | 17 |
| sequences, fresh seeds 96000+ | 3 | 3 | 13 | 17 | |
| combinations | 1 | 1 | 3 | 3 | 3 |
| timing | none | | none | | none |

On sequences it climbs over three doublings of material to the ladder's top (17, three rungs above the starting brain's 1 at least),
confirmed on fresh seeds: the first ladder on which the scaling test's first part holds. On combinations it climbs once (1 to 3) and
stalls (rung 4 .61 at 640, not sure; 5 and 6 .1 to .47). On timing it solves nothing, and more material does worse (rung 6: .44 at 40,
.12 to .18 above): the cost of size, measured, where the brain lacks the part the ladder needs (a clock set by the world's changes, D39).
In the plain world its score is exactly 0 at every size: the gate never adopts a stream, so nothing is committed where nothing is to be
learned (part 4). Rungs 5 and 7 of the sequence ladder, with 100 s lives, are solved at no size on fresh seeds (.58, .49): too short a
life for this brain, though shorter patterns.
Why combinations stall (R45, `lab/v/grownet_combo_cap.log`): not the size cap. The written-rules network, growing 45 to 74 blocks, stalls
the same (rung 5 .44, rung 6 .21 at 640). Open: evidence for 64 contexts in a 1000 s life, or the four-symbol stream splitting histories.
On combinations 5 and 6 (R46): two symbols (net's eaten stream) .55 and .35, four (net5) .44 and .21, the never-pruning tree .65
(solved) and .55. Clearing out has a price where many contexts recur rarely: a context unused for longer than the fading horizon is
recycled though it will be needed again. The stability-plasticity trade, here in the open: the tree remembers and can't relearn (D59's
changed pattern), the growing network relearns and forgets the rare.

**Recycling on demand** (R47, R48; `lab/v/grownet_ondemand_*.log`; Dohare et al. 2024's comparator). No fading; copies still removed;
when a block is due and material is full, the least used of four blocks drawn at random (nothing built on them) is recycled: a local
contest, not a search. On the changing pattern (P 64) it surely beats recycling by a timer on both seed sets and in both worlds:

| | seeds 85000+ | fresh seeds 97000+ |
|---|---|---|
| unchanged: on demand, by timer, tree | +1.69, +1.34, +1.13 | +1.67, +1.14, +.94 |
| changed: on demand, by timer, tree | +1.57, +1.15, -.46 | +1.48, +.73, -.82 |

A timer recycles blocks that are still useful but resting; on demand, only when room is needed, and then the least used. It keeps what
works and still frees room for what's new: in the changed world it nearly holds its unchanged score. On combinations (P 320, room
enough) no difference.

**With recycling on demand** (R49, fresh seeds 96000+): the generic brain with every sense a stream and recycling on demand (net5R)
solves 3, 3, 17, 17 at material 40, 80, 160, 320: the sequence ladder's top with half the material that trophic competition needed.

**Streams that record one sense each** (R50 to R52; `lab/v/grownet_split_*.log`). Ten streams (every clock times either the colour
eaten or good-or-bad) instead of five of four symbols: the brain picks "colour at every taste" for combinations and "colour at good
meals" for sequences by itself; on fresh seeds, paired, combination 4 surely better (+.19, .59 against .40), 5 and 6 tied (.36, .26),
sequences no worse. Generic (no choice of what to record), and better.
**Combinations 5 and 6 against the tree** (R53, R54, 3000 s lives, paired, fresh seeds 98000+). Lives three times as long lift the tree
to .76 and .72 (both solved) and the growing network only to .49 and .38. It makes about 9000 blocks a life and keeps 60 to 70; merging
copies (a copy's dependants handed to its twin) keeps 120 to 180, as many as the tree, but scores no better (.38, .36). Suspected: churn,
a block grown beneath every contradiction and others recycled to make room, so rare contexts never count long enough; the tree stops
growing when full. Growth that slows when it stops paying is the candidate.

**A fault in copy removal, and what it changes** (2026-11-13; `lab/v/grownet_bench_combo.log`, `grownet_strict_*.log`; R55 to R57).
Copies were found by firing alike over the last 30 steps. A block and its own ancestor do so whenever the ancestor's other branches
rest, so parents and children were taken for copies and recycled, with their dependants. On a bench without a body, the combination of
6 is learned 99-100% with no pruning (about 100 blocks, no copies) and 93% with the faulty rule (800 born, 450 "copies" removed). Strict
copies (never a block and its ancestor or descendant): 97-99%. Consequences:
- Combinations: with strict copies, ten streams and 256 a stream, the network solves combinations 5 and 6 in 3000 s lives (.67, .62;
  the tree .76, .72).
- The changing pattern: recycling on demand does not depend on the fault (+1.69 with strict copies, +1.70 without, when the pattern
  changes; fresh seeds 99000+). But fading with strict copies is stuck when the pattern changes (.00 against 1.04): the fault, recycling
  parents and children, was doing the clearing credited above (R7) to copy removal. Corrected: what lets the network relearn is
  recycling that keeps room free; a timer is too slow; recycling on demand does it. The earlier results with written rules (net, net5,
  and the scaling curve's comparisons) used the faulty rule; the trophic and on-demand results are the ones that stand.

**The scaling curve again, for the best generic brain so far** (R58; `lab/v/grownet_curve_X_*.log`): ten streams (every clock times
one recorded sense), recycling on demand, strict copies (net10X).

| material | 40 | 80 | 160 | 320 | 640 | 2560 |
|---|---|---|---|---|---|---|
| sequences, highest rung solved (fresh seeds 96000+) | 3 | 3 | 11 | 17 | | |
| combinations (development seeds 84000+) | 1 | | 3 | | 5 | 3 (5 at .58, not sure) |

Two ladders now climb with material: sequences to the top, combinations from 1 to 5 (D60's trophic brain stalled at 3). Rung 4 of the
combinations (a 300 s life) is solved at no size (.60 to .65) while rung 5 (1000 s) is: rung 4's life is short for 16 contexts. Timing
still nothing (no clock set by the world's changes).
Timing with the brain's own clocks restarted at every bad taste (R59): rungs 2 and 3 a little better (.40, .34 against .28, .12), none
solved. Timing stays the ladder the growing brain can't climb.
Doing no harm (R60, 20 pairs): in the plain and all-food worlds the best generic brain's lives are identical to the starting brain's at
every size from 40 to 2560 (the gate never adopts a stream). The material's power is not yet charged.
The best generic brain on the changing pattern (R61, fresh seeds 100000+): +1.77 when the pattern stays, +1.75 when it changes; the
tree +1.25 and -.45. It loses almost nothing to a change, and beats the tree surely in both worlds.
When an old pattern returns (R62, A-B-A, fresh seeds 101000+): the best generic brain +1.55, the never-forgetting tree +.70 (+.86 [+.49,
+1.22]). Whatever it forgets, it gets back faster than the tree, which never learned B, recovers A.
Sequence rungs 5 and 7 in 300 s lives (R63, fresh seeds): solved at 160 and 320 (.84 to .97). The 100 s life was the limit; every
sequence rung is solved by 160 to 320 units given lives of 300 s.
Recruitment switched off (R64; the same brain with only its senses, two units a stream): sequences 11 and 17 surely worse without it
(+.46, +.37 for recruitment), combination 3 not surely (+.17 [-.05, +.35]). The scaling test's third part holds on the sequence rungs.
On the muscle body (R65) the best generic brain ties the tree on sequences 5 and 11 and combination 3.

**Timing with clocks in the growing brain** (R59, R66; `lab/v/grownet_clocks_time.log`). Sixty of the brain's own clocks offered as
streams (periods 3 to 30 s, drawn per life), each re-phased when the food colour a taste reveals differs from the last revealed (D39's
trigger: half a period after the change), a beat recording the colour last revealed, held. Paired against the clocked tree (both about
1000 units): timing rung 2 solved, .64 [.53, .75] (tree .81); rung 5 .41 (.35), rung 7 .31 (.40). Clocks restarted by every bad taste
did worse (.40 at rung 2): mistakes restart them too. Recording "nothing" at beats without a taste split the contexts (rung 2 smoke 75
against 112). Note: the revealed colour uses the told symmetry, as every told brain does.

**One design for all three ladders** (R67, fresh seeds 102000+, paired): ten sense streams and 60 clocks re-phased by revealed changes
(net10kc60, 2240 units) comes within .15 of each ladder's specialist (sequences -.06, -.01; combinations -.09, -.11; timing +.10), solving
sequences 11 and 17 (.83, .65), not combinations 3 and 5 (.50, .48) nor timing 2 (.47). On these fresh seeds the timing specialist
reaches only .37: R66's solved timing rung held on development seeds only.
The one design's scaling curve (R68, fresh seeds 103000+, material 560 to 4480): sequences 3, 11, 17, 17; combinations rung 1 at every
size, rungs 3 and 5 rising (.36 to .63, .16 to .56) without surely passing half; timing rung 2 rising .37 to .54, rung 5 .38 to .48. Every
rung of every ladder improves with material up to 1120 or 2240 and then holds; only the sequences cross the bar. With one design, the
scaling test's first part passes on one ladder, and the other two climb short of it.
