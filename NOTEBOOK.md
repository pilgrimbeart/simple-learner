# The body and the circuit simulator: lab notebook

The history, methods and findings of the body and how a creature is scored, and of how the circuit brains are
simulated (their noise above all); the sheet brain's are in nca-learn's notebook. Dead ends are kept because they are
lessons too; the rules they led to are in `AGENTS.md`, the big picture in the README. Older entries keep the names
they were written with: the "mixed-signal brain" is the designed circuit, and the
"minimal" circuit of recruitment (until 2026-10-21) the baseline circuit.

## Where it stands

- **The body** is a disc with its mouth at the front of its rim and two thrusters on its rear rim (`world.py`), in real
  units since 2026-10-22; earlier bodies capped every brain (below: Telling food from poison).
- **The circuit simulator** (`mixed_feedback.py`) carries noise and mismatch as a substrate makes them (silicon,
  biology, twice biology), with no way round them; under biology's, every hand-built circuit brain falls to about 1
  food for each poison (below: Noise as biology makes it).
- Open questions: `QUESTIONS.md`.

## Lessons from these lines, in full

- **Check in a fresh environment.** A push once failed because numba's `@` needs scipy, which `requirements.txt`
  didn't list and the working venv happened to have: so the checks before a push run in a fresh venv built from
  `requirements.txt` alone (`AGENTS.md`, Working).
- **Rules kept only in prose drift, so make the rule the structure.** The golden rule is that each cell sees only the
  mean of each number its neighbours share. Earlier experiments (before this project) quietly broke it, reading each
  neighbour separately (the smallest, one by tag, each one's sums), and nothing in the code stopped them. So each rule
  is enforced in code and tested: the circuit brains' circuits, the minimal search's `check`.
- **When a change lets the brain drop machinery, ask where its job went.** How the body came to assign credit (2026-10-16): The user had described the sensor cell as having "two inputs (what it
  senses and food/poison)". I read "a food/poison input on the sensor" as licence to route the reward to the right
  sensor, and proposed "reward at contact": the body gives food or poison only to the eaten colour's sensor. I
  presented it as removing four mechanisms (chew delay, flavour stimulus, news wave, trace) and one shared number, and
  argued "the body is allowed to know what it ate and what colour it was, just as it knows which eye saw it". What I
  didn't say: those four mechanisms were the brain's credit assignment, which this file had already named the hard
  part ("the old rule did credit assignment for free"). Deleting them didn't simplify the problem; it moved its
  hardest part into the body. The user agreed to a "simplification", not to that. The warning signs were all
  written down and passed over: the README's count of shared numbers said "learning: none (everything a sensor learns
  from is delivered to it by the body)"; the designed circuit was then built on the same `reward(sensor, value)`,
  with four reward terminals beside the sensors; and learning got faster and cleaner just as the brain got simpler.
  The user found it from the schematic, by asking where the reward input was. The lesson: whenever a change lets the
  brain drop machinery, ask where that machinery's job went, and if the answer is the body, say so plainly or don't
  propose it (now in `AGENTS.md`).
- **Find what the body allows before blaming the brain.** An oracle that knows the answer, fed only what a brain
  would see, gives the ceiling: an ideal reflex showed that the square body capped every brain (The body, below:
  Telling food from poison), and scripted policies that the best circuits drove the body badly (next).
- **Real units show what abstract ones hide** (the user's decision, 2026-10-22: real units everywhere, every number
  derived from few axioms, `units.py`). Named in seconds, amperes and farads, the circuits turned out to have silicon's
  sizes (picofarads, gigaohms, nanoamps) and biology's noise (events of 12.5 fC, about 78,000 electrons, where a
  transistor's are single electrons): no contradiction while the units were abstract, plain once they weren't. In
  silicon at these currents the noise is about 280 times smaller in amplitude, and the circuits that leaned on noise
  failed there outright: EF_22p, the "simplest", stranded in every life, while the hold-and-roam circuit, whose roam
  is a timer, did the job as well as in biology. Units also give finger-in-the-air plausibility checks (a resistance
  a chip can set stops at about 100 GOhm, a time constant at a few seconds without a floating gate) and a meaning to
  every display (the live view now says how fast it runs against real time). The conversion was checked by living
  the same lives before and after: every one of 1,280 came out with the same meals.
- **A view refactored without being looked at breaks unnoticed.** When lengths became metres (the real-units change),
  the live view's eye beams went on stepping in whole units and fading over REACH, so they faded to nothing; no test
  draws the view, and it was noticed only by the user, days later. After a change of units, look at every view.

## Taste: one input, and credit assigned inside the brain (2026-10-16)

- **Why.** Learning had been `reward(sensor, value)`: the body handed the reward to the eaten colour's sensor, so the
  body did the credit assignment. The user's ruling: for every brain, taste is one input, +1 for food and -1 for
  poison at the tick a block touches the mouth, else 0, saying nothing about which sensor. The body must never be part
  of the solution.
- **Designed circuit.** An eligibility node per sensor (charged by its spikes, leaking over ELIGIBLE ticks) gates two
  amplifiers that charge or empty P while taste is good or bad. Each spike also empties the other sensor's E (FORGET,
  cross-inhibition). 64 lives: E 10 with FORGET learned 63/64, median 1,512, net +0.86 (no FORGET: 64/64, 1,830, +0.72;
  the oracle about +0.92).

## The body, and how a creature is scored

### Vision (`world.py`)

- **Shorter, and blocks hide what is behind them.** The eyes cast 25 parallel rays across the strip the mouth sweeps;
  each stops at the first block it meets (a disc of radius 1, its drawn size) within 15 units, and a block counts
  1 / (1 + (d / 5)^2), less where hidden or partly outside. Before: no hiding, out to half the world, half-weight at 10.
  The view draws the rays as a fading beam, with shadows behind blocks.

### Scoring per unit of time

- **Score per tick, not per meal** (the user). Two scores: how soon the sensors learn (ticks after moving until both
  are within 0.2 of right: the rules), and food minus poison per 1,000 ticks (the sheet and the body). Poison's share
  of meals alone hides the rate: a slow creature can eat well and little.
- **Slower or sparser raises the ceiling but costs meals.** Ceiling with p perfect, poison's share by thirds (meals
  per third, 32 lives): thrust 0.5 (now) 48%, 42%, 47% (about 380); 0.25: 43%, 41%, 44% (180); 0.125: 23%, 32%, 30%
  (80). 9 blocks of each colour instead of 18: 41%, 43%, 46% (135); 5: 34%, 36%, 42% (75). For the same meals, slower
  is better than sparser: it gives the 53-tick brain time to act. But per tick the slow creature loses (16 lives
  each, learning on):

  | version | learned (median ticks after moving) | food minus poison per 1,000 ticks, by third |
  |---|---|---|
  | thrust 0.5, p moves 1/4 of the way | 16 of 16, 1,331 | -0.03, +0.38, +1.06 |
  | thrust 0.5, p moves 1/2 of the way (now) | 16 of 16, 997 | -0.20, +2.15, +0.48 |
  | thrust 0.125, 1/2 of the way | 13 of 16, 2,945 | +0.14, +0.41, +0.68 |

  Once learned the thirds differ by noise; 16 lives are too few to rank the net food finely.
- **Angling the thrusters doesn't help** (the user's idea: a lone thruster should mostly turn the body, not drive it
  round a wide circle into the poison). A thruster at angle a from straight back pushes cos a forward and sin a to
  its own side (so its turn adds up: (cos a + sin a) x today's turn); both at once go straight, at cos a of today's
  speed. Ceiling with p perfect, poison's share by thirds (meals, 32 lives): 0 degrees (now) 48%, 42%, 47% (about
  380); 60: 44%, 51%, 39% (about 100); 80: 43%, 45%, 21% (about 23: it hardly reaches a block). Fewer meals, no
  better share: the poison is eaten while the food's sensor drives straight at food behind or beside it, not
  while the poison's sensor veers.

### Telling food from poison: a pointed body and a faster circuit (2026-10-17)

The user's target: at least 2 food for each poison after 10,000 ticks, ideally nearer 10, worked out on the
designed circuit (quicker to learn and to tune). Measured as food:poison over 24-32 lives, with p held perfect by
hand (the ceiling) or learning; "second half" is ticks 5,000-10,000. Before: 1.5 at the ceiling, 1.5 learning, 4.7
meals per 1,000 ticks.

- **Where poison was eaten.** Every poison meal had been in view for at least 30 ticks. Three causes, each measured:
  the square's mouth was its whole front edge (5 units), and every turn swept it across poison beside the corridor;
  each neuron could spike only about once in 17 circuit ticks, so the creature moved in big lunges that coasted 2-3
  units into whatever lay ahead (the user's "slow brain and momentum"); and the plastic synapse leaked (at p = 1 a
  sensor's spike reached both motors only 74% of the time, so a quarter of food sightings became veers).
- **An ideal reflex first.** A controller with no brain (straight at food, veer from poison, the right thruster at
  once) found what a body allows: on a pointed body with gentler thrust it reached 10-27 (0.5-2.6 meals per 1,000),
  refractory time and blind wandering cost little, and 10% leak in the reflex halved it. So the body had to change,
  and then the brain had to be fast and clean.
- **The body** (ground rules, agreed with the user): an equilateral triangle, point forward, the point the mouth
  (eaten within EAT of it; the eyes' corridor is 2 EAT wide); PUSH 0.5 → 0.2, TURN 0.08 → 0.16, DRAG 0.2 → 0.5
  (small kicks that die quickly, a tighter turn); SENSE 0.21 → 0.5. Triangle alone: ceiling 1.5 → 2.5. Slower thrust
  or more drag alone raised the ceiling but starved the creature (0.1-0.6 meals per 1,000 ticks) while the circuit
  still lunged.
- **The circuit runs 4 of its ticks to each tick of the world** (SPEED). Its refractory time is unchanged in circuit
  ticks, so it spikes four times as often and each kick is a quarter as big relative to the body's motion. Ceiling
  4.6 at SPEED 4 (1.0 meals per 1,000). A shorter recovery (tau 3 instead of 10) broke the neuron: almost no spikes.
- **A clean synapse.** WEAK 0.05 → 0 and STRONG 0.35 → 0.7: a sensor at p = 1 now reaches both motors about 99% of
  the time, at p = 0 never. Ceiling 4.6 → 12.7, meals 1.6.
- **Each sensor hushes the other** (INHIBIT 1.5 over HUSH 10 ticks, a hush node per sensor): while it sees food the
  creature stops answering poison, and the other way round, so it no longer swerves between them into a third block.
  Ceiling 12.7 → 14.2; learning, second half, 4.5 → 8.5. Stronger (3) or longer (25 ticks) did no better.
- **Learning, 10,000 ticks (24 lives): 4.5 over the whole life, 8.5 in the second half, 1.8 meals per 1,000; p at
  the end poison 0.13, food 0.99.** Over 20,000 ticks: 6.1 over the life, 8.2 over ticks 10,000-20,000. 64 lives of
  10,000 ticks: 4.3 over the life, 7.0 in the second half, ceiling 14.8; on `--measure`'s 32 lives the thirds are
  2.2, 5.9, 4.6. Poison meals are few, so the ratio differs a lot between sets of lives: rank variants on 64. p for
  poison settles near 0.1, not 0: poison meals are now rare, and each is a learning event, while food meals now and
  then credit the poison sensor when both were seen.
- **Dead ends.** Fewer blocks (5 or 9 of each colour, on the square: Scoring, above): fewer meals, little better
  share. More spontaneous spikes (a neuron's bias -1.6 → -1.4 or -1.3): blind forward kicks hit poison, and with the
  hush on, its sensor was then silenced (ceiling 0.9-1.9). A lower bias (-2.0): no meals at all. A boredom drive
  (both motors pushed while neither sensor had fired lately): more meals (2.4) but a worse ratio (7.9 in the second
  half). LEARN 0.5 or ELIGIBLE 20: worse (6.2, 7.2). SENSE 1.0: 7.2; TURN 0.24: 6.9.
- **What would go further.** The eyes can't tell left from right, so a veer is always to one side, sometimes into
  poison lying beside the food: one sensor per side would fix it, but that is more sensors, a ground-rule change.

### The disc (2026-10-31)

The user's decision, after the arena's robots, each a triangle covered by five colliding discs, hooked each other as
they turned past: every body a disc, simple to hit-test, its sensors and thrusters placed round it. Its radius is the
triangle's circumradius (`world.RADIUS`, 2.3 mm), so the mouth sits where the point was and the thrusters where the
tail's corners were (120 degrees either side of the mouth, on the rim): the physics, the eyes and eating are unchanged,
and so is every life in this world (the checks pass unchanged). Only the drawing and the arena's collisions changed
(`discrete/NOTEBOOK.md`, D18).

### The second body: a square with two forward thrusters (withdrawn 2026-10-17)

Its mouth was its whole front edge, and its kicks were big (PUSH 0.5, TURN 0.08, DRAG 0.2): the ceiling with p
perfect was 1.5 food per poison (about 45-49% poison), whatever the brain. Replaced by the triangle (above).

### The first body (withdrawn)

The first body had a forward thruster at the tail (A) and one at the side that backed and turned it (V), and the
reward came after a chew delay with eyes shut. Its lessons:

- **The body's ceiling.** With balances fixed perfect from birth, poison was still about a third of meals: the learner
  was at the body's limit. Backing and turning swept the mouth over the poison it was avoiding, so the mouth eats only
  what it moves forward into (perfect balances 33%, 29%, 33% by thirds → 31%, 17%, 28%). Longer pulses, body tweaks
  and a 33 × 33 brain made no clear difference.
- **Results by version** (poison's share of meals by thirds of life after moving, 16 lives with learning; no
  learning about 50%):

  | version | learning on |
  |---|---|
  | 18 shared numbers, distance fields, V near a far corner | 32%, 21%, 26% |
  | 20: names that hold, x and y, V halfway down a side | 38%, 23%, 33% |
  | 16: coordinates as distances (magic knowledge, withdrawn), V at the tail corner, straight paths | 45%, 34%, 34% |
  | 18: A one cell again, A and V send distance fields (the exp cheat, withdrawn) | 35%, 39%, 34% (no learning 43%, 47%, 51%) |
  | 27, honest: flags and gradients, -1..1 at 1% noise | 43%, 39%, 42% (no learning 49%, 48%, 54%); balances poison 0.20, food 0.84 |

  V in the far corner (so R's and B's paths are easier to tell apart) doubles the way to V, and the recoil arrives
  later. The individual-neighbour version before this project had 43%, 27%, 24%.

## Circuits: simulation and noise

### A second brain: the designed circuit (then `brains/mixed_signal.py`, now `brains/designed.py`)

- **Why.** The user, after Sepulchre's work (Ribar and Sepulchre 2021, "Neuromorphic Control"; Huo, Forni and
  Sepulchre 2025, rebound winner-take-all): one mixed-feedback element (a leaky node; elements that put a current into
  a node, a sigmoid of a filtered voltage, with a sign and a timescale) builds both discrete and continuous behaviour.
  A designed circuit for the whole creature, beside the sheet, says what the sheet costs, and is the groundwork
  for rebuilding a cell as such a circuit.
- **The split.** The body and world went to `world.py`; `Life` talks to any brain through sensors 0, 1 and motors 0, 1;
  the sheet became `brains/grown.py` (now `brains/sheet.py`). Four recorded lives matched the old code bit for bit
  (meals, firings and sensors' p), so the refactor changed nothing. Thrusters must fire in the same order as before:
  spin is a float sum.
- **The neuron.** The paper's spiking neuron (fast positive feedback, slow negative; tanh) at the paper's bias was
  bistable, not excitable: one pulse set off firing that never stopped (bias -1.2 to -1.4, recovery 5-20 ticks). At
  bias -1.6 it rests: one spike for any pulse above about 1 (a tick long), and noise 0.2 gives about 6.5 spikes per
  1,000 ticks of its own (the sheet's sensors fire by themselves about 9 per 1,000).
- **Noise grades a synapse.** A sensor's spike crosses a synapse of weight 0.05 almost never, 0.15 half the time, 0.35
  almost always: noise makes the choice, so a plastic weight between them is a chance of firing the other motor too,
  as the sheet's sensor's p is.
- **A/B, the same 16 lives each:** sheet learned in 16 of 16 (median 1,024 ticks after moving), food minus poison per
  1,000 ticks by third -0.20, +1.97, +0.37, poison's share 52%, 38%, 47%; designed circuit 16 of 16 (median 1,090),
  +0.89, +1.13, +1.32, and 40%, 39%, 35%. Learning after moving is about as fast (set by how often it eats); but the
  circuit moves from the first tick and reacts at once, where a pulse takes about 53 ticks to cross the sheet, so it
  steers round more poison than the sheet brain could even with perfect p (about 46%), and nets about twice the food
  in a life.

### Simulating the designed circuit (2026-10-18)

Reviewed with evolving circuit brains in mind (many lives of 10,000 ticks), so it must be fast and must not be
exploitable.

- **Where the time goes.** A life took about 1.5 s per 1,000 ticks, 85% of it in `Circuit._advance`: 80 integration
  steps per world tick, each a dozen numpy calls on 11 nodes and 24 elements, so call overhead swamps the arithmetic.
  The same integration as one numba loop, drawing from the same random generator, matched the original (voltages
  within 2e-12; motor spikes the same over 3,000 ticks, and the meals of 4 lives) and ran the circuit about 45x faster
  (0.28 s per 10,000 ticks). Then the world (`look`, `move`) and the per-tick Python in `Life` dominated (about 3.5 s
  a life), so the eyes and mouth are compiled too (blocks held as arrays). Passing numpy's random generator into
  compiled code costs about 25 us a call, so each tick's noise is drawn beforehand in one call (the same stream). A
  life now takes about 0.5 s (from about 15). `test_compiled.py` checks both against plain numpy versions of the same
  equations (random circuits and scenes; it catches a 0.1% error in the circuit and 1e-15 in the eyes). The whole
  life in one compiled function (`minimal/fastlife.py`) later cut it to about 0.7 s for the minimal search.
- **An exact check needs the same arithmetic on every machine.** The eyes' check once failed on GitHub (1,006 of
  3,000 scenes differing) though nothing had changed: the plain version used numpy's `d @ f` and `norm`, which go
  to OpenBLAS, and OpenBLAS picks its kernel by CPU; on an AVX-512 machine those round differently in the last bit
  from the compiled `dx * f[0] + dy * f[1]`. The plain version now writes the sums out in the same order (it passes
  under `OPENBLAS_CORETYPE=SkylakeX`). The lives use BLAS only where blocks are placed (a `norm` against a
  threshold), so a last bit there could change a life only for a block exactly at the threshold.
- **The integration step doesn't matter.** An input is a current lasting one circuit tick (a quarter of a world
  tick), fixed in model time, not in steps; noise is scaled by sqrt(DT); spikes are found with hysteresis at each
  step. From DT 0.2 to 0.01 (now 0.05) these agreed within sampling noise: spontaneous spikes (10-11 per 1,000
  ticks), spikes per stimulus (0.87-0.91), how often the plastic synapse relays, and one taste's move of p (0.287-0.289,
  noise off). 64 lives at DT 0.05, 0.1 and 0.2: food:poison 4.2, 4.8, 4.2 (poison meals 205, 172, 199, give or take
  14). So DT 0.1 would halve the cost, if checked.
- **Pulse shape: stimulus safe, taste not.** A stimulus works by charge: the same charge over 0.25 to 8 circuit
  ticks gave 0.85-0.86 spikes per pulse. Learning works by how long the taste node stays above 0.5 (a steep sigmoid,
  with LEARN's gain set by hand for "above half about 1.3 ticks"): the same charge over 0.25, 1, 2 and 4 circuit ticks
  moved p by 0.22, 0.29, 0.36 and 0.05. Harmless while the pulse is fixed, but an evolved circuit would tune itself
  to that exact rectangle. An input delivered as a charge at an instant, with the input node's own leak setting how
  long it lasts, leaves no tick in the interface (it changes both input nodes, and LEARN would need recalibrating).
- **The plastic synapse is graded only for p below about 0.4.** Its weight is STRONG x p = 0.35 at p = 1/2, which
  relays about 85% of spikes, not "about half" as the docstring said.
- **Defences, for any circuit brain that is optimised:** each input at a random time within its tick (inputs on the
  tick boundaries make intervals whole ticks, a rhythm a resonator could lock to: the circuit's lockstep; not built
  until 2026-10-20, below: Noise as biology makes it); limits on
  time constants (at least about 5 DT) and on gain x slope / capacitance, and each generation's best re-run at DT/2;
  fresh seeds for every evaluation, and the result judged on lives never trained on; every parameter a few percent
  off at birth (mismatch, as Sepulchre stresses: no knife-edge tuning or exact cancellation between identical parts);
  noise on every node, as now. Each motor spike is a full kick, so a fast oscillator gets the most thrust: the
  minimal search now charges each firing (2026-10-21), and eating is checked along the path a fast creature moves in
  a tick (2026-10-22; it changed EF_22p's meals by about 1%).

### Noise as biology makes it (2026-10-20)

The user asked how noise was decided, where it goes in, and whether it could be cheated. The answers were: 0.2 per
node, picked when the first circuit neuron was built; a fixed current on every node; and yes, in three ways. So the
noise was remodelled on biology's (Faisal, Selen and Wolpert, "Noise in the nervous system", Nat Rev Neurosci 2008),
which subthreshold silicon shares (Sarpeshkar, Delbrueck and Mead 1993), and the user accepted it all.

- **Three holes in the old noise.** (1) *Inputs on tick boundaries*: listed above as a defence (Simulating the
  designed circuit) but never built: every stimulus and taste was a rectangle starting exactly as a world tick began,
  so intervals were whole ticks and the taste's shape fixed, a rhythm and a template an optimiser could lock to.
  (2) *Memory write noise vanished at a finer step*: rough by 10% of each step's change, its variance over a fixed
  time fell in proportion to the step, so the half-step check saw a quieter memory and could flatter a design.
  (3) *Size bought silence for free*: noise was a fixed current per node, so scaling a node's capacitance and every
  current into it by k (the same behaviour; the slew limit, being current over capacitance, can't see it) cut its
  noise k times, for power alone (0.01 per unit in the minimal search's score) and no extra parts. The minimal search
  was heading there: tuned sensors at C 4-6, where they were designed at 1.
- **What biology does.** Noise comes from discrete events: channels opening (relative noise 1/sqrt of their number),
  vesicles released (binomial), photons and receptor events (Poisson, in continuous time). Thermal noise is
  microvolts, negligible. Quiet is bought with more channels, so area and energy (Laughlin, de Ruyter van Steveninck
  and Anderson 1998): reliability costs power. Awake cortex fluctuates by about 2-4 mV against 15-20 mV from rest to
  threshold; the old 0.2 gave the standard neuron about 0.14 V against about 1 V, inside that, so the size was right
  and the scaling wrong. And parts differ: identified neurons of one type by 2-5 times in channel density (Marder and
  Goaillard 2006), held in shape by homeostasis; analogue transistors by 10% or more (Pelgrom 1989).
- **The model** is specified in `mixed_feedback.py`'s docstring (and the rule against dodging it in `AGENTS.md`).
  What closed the holes: noise in proportion to each current and capacitance, so scaling a node by k buys only sqrt(k)
  quiet, for k times the power; a memory rough by the square root of what is written, the same at any step; pulses at
  random moments; and all of it in the one integration step every simulation calls. `test_compiled.py` checks it:
  memory and leaky-node spreads the same at step 0.05 and 0.025 (the old model fails: its memory spread fell by 1.4),
  a node 4 times as big quieter by 2, not 4, every part mismatched by about 10%, a pulse's charge exact wherever it
  falls.
- **Calibration.** SHOT (0.005) and MEMBRANE (0.02) share the old variance equally for the standard neuron at rest
  (its two elements carry 1.87 each, cancelling: gross 3.7, net 0). Without mismatch it fires 4.4 times per 1,000
  ticks on its own, as before (4.6; the 6.5 above was with older parameters), one spike per pulse.
- **The paper's neuron doesn't survive 10% mismatch.** With it, about a third of standard neurons (35% of 200) fire
  on their own at 20-60 per 1,000 ticks (median 2), and a pulse gives 1.46 spikes on average, not 1 (3%: 11.5 per
  1,000, 1.15). Its excitability balances fast positive against slow negative feedback of equal gain and bias -1.6,
  near the bistable range (bias -1.2 to -1.4, above): a 10% shift in bias or in either gain tips it into firing by
  itself. Biology keeps such neurons in shape by homeostasis; these circuits have none, except the adjusting
  circuit's rung 0, which adjusts each neuron's excitability.
- **Every circuit brain collapses** (32 lives of 10,000 ticks, the same lives under the old and the new simulator;
  food:poison in the last third, old -> new): designed circuit 4.6 -> 1.0, recruiting circuit 5.4 -> 1.3, adjusting
  1.7 -> 0.9, healing circuit 1.2 -> 1.2 and healing cascade 0.9 -> 1.2 (these two need longer lives: their
  leaderboard is at 30,000 and 100,000 ticks). Taking mismatch away (a diagnostic only) separates the causes: the
  designed circuit 2.54 with none, 1.63 at 3%, 1.02 at 10%; the recruiting circuit 3.27, 1.81, 1.26; the healing
  circuit 1.52, 1.50, 1.18. So mostly mismatch; the rest of the designed circuit's loss (4.6 to 2.5 with no
  mismatch) is the new noise or the random timing, not yet traced. These brains were built by hand on
  exact parts and never asked to survive mismatch; the minimal circuit search's designs, tuned with mismatch and
  varied noise from the start, do survive it, and polished under the new rules they improve (minimal/NOTEBOOK.md,
  M7). The polish shrank every sensor's capacitance (by a third to two thirds) and raised its resistance, keeping its
  time constant on smaller currents: under a fixed noise per node the search had begun making nodes big to drown it;
  now a big node is noisier in absolute terms, so the cheat is gone and the search goes the other way. The
  recruitment series' results
  (`experiments/LEADERBOARD.md`) stand only for the old simulator until they are re-run.
- **What else cost the designed circuit (the night of 2026-10-20; diagnostics with switches the rules forbid, in
  scratch code only).** With no mismatch it fell from 4.6 to 2.5. Putting the body's pulses back on tick boundaries
  changes nothing (2.41 against 2.54): the hand-built neurons never leaned on lockstep. The noise level does: at half
  the noise the creature never moves (no meal in 32 lives), at 0.75 food:poison 1.54, at 1 2.54, at 1.5 1.64, at 2
  0.88. Noise is both its engine (the spontaneous spikes that make it move and search) and its enemy (it blurs which
  colour was seen), so it was tuned to the old noise's pattern across its nodes, and no level of the new one gives
  that back.
- **Mismatch breaks the neurons, not the learning.** With mismatch in one group of parts at a time (64 lives, last
  third food:poison): none 1.70, the neurons' own parts 0.99, synapses 2.05, learning (E, P and their writers) 1.59,
  hush 2.15, taste 2.02. So the neurons alone do the damage. Of 200 standard neurons under 10% mismatch, half fire
  more than 10 times per 1,000 ticks of their own accord, and those that don't miss pulses; moving them further from
  threshold trades one for the other (bias -2.0: 14% fire on their own, 28% of pulses missed; no margin tried gives
  both under 10%). An excitable neuron sits near the point where it starts to oscillate, and 10% mismatch pushes a
  share of them over it.
- **Rate homeostasis restores the rates, not the function** (an experiment, not kept): each neuron given a knob, a
  memory node charged by a steady current and drained by its own spikes, feeding a current back into it, so that it
  settles at its designed rate (sensors 19, motors 45 per 1,000 ticks; the target mismatched like every part). Under
  10% mismatch the rates come back (sensors from 0.1-179 to 12-37, 10th-90th percentile; motors from 0.3-199 to
  31-74), but food:poison barely moves (1.11 against 0.97; sensors only 0.92). A rate can't tell a spike the eye
  caused from one of the neuron's own, so a dull sensor is woken until noise fills its quota. The minimal search's
  winners escape all of this: their sensors are leaky integrators, not spiking relays, so mismatch only rescales them.
