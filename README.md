# simple-learner: intelligence that scales

An open-ended research programme on emergent systems operating in real time. We use a small simulated robot
to investigate how a brain could improve its own organisation during life. The [abstract](ABSTRACT.md) gives
the present research position; [PROGRAMME.md](PROGRAMME.md) gives the next investigations.

Split from [nca-learn](https://github.com/pilgrimbeart/nca-learn) on 2026-11-02. That repository retains the sheet
of identical cells; this one carries the circuit and growing-network investigations.

## The goal: intelligence that scales

**To solve a bigger problem, just add more brain.** We seek one reusable component type, or a small repertoire,
from which a simple robot brain can recognise an improvable shortfall and organise additional capacity when
useful. The component design may contain substantial innate structure. The designer must not need to invent
new machinery for each unfamiliar evaluation problem.

The eventual output should be an academic paper that explains the mechanism and its scientific significance
in simple terms, with its relationship to prior work, evidence and limits made explicit. Novel implementation
alone is not the breakthrough; the explanation and demonstrated generality must earn that claim.

Success means that, after launch into an unfamiliar simulated environment, the brain learns during that life
to approach the best brain we can hand-design for that problem, or a tighter information-theoretic performance
limit where one can be justified. It should do so parsimoniously, accounting for evidence, learning time,
energy, material, communication and response speed. A precise near-optimality margin must be declared for a
particular claim; passing an exploratory milestone below is not that claim.

A module acts on its state and signals received through explicit connections. Small brains may be densely
connected; as they grow, communication must remain affordable. A few explicit shared signals may be considered,
but their availability and costs cannot be hidden. Detecting that more capacity would help is itself a central
research question, not an ability we may assume the module already has.

Recruitment can mean creating, activating or reorganising capacity. Tuning existing machinery is the default
comparison, but can cost exploration or overwrite useful knowledge. Compare growth with reuse, recycling and
retention; neither growth nor tuning is always cheaper.

We keep the body and environment simple for fast simulation and clear explanations. Finite evidence and
resources can make some tasks unattainable. A failure under specified constraints, or a discovery about the
trade-off between body and brain, can therefore be valuable progress. Body and interface changes still require
the user's agreement; failure of one learner does not establish that such a change is necessary.

### How we'll know: the scaling test

Freeze one design and measure what increasing resources buys across several challenge families, including
families not seen by its designers. Compare in-life adaptation with appropriate fixed, tuning and recycling
controls. Measure the costs and the retention of simpler skills as well as the hardest challenge passed.

The [2026-11-09 scaling milestone](GRAMMAR.md#scaling-milestone-recorded-on-2026-11-09) retains its original
numbers: three ladders, three resource doublings, three additional rungs, a .25 efficiency gap, at least half
that gap closed with its stated confidence criterion, and under a tenth of spare material committed where
recruitment is unnecessary. These were an operational draft, subsequently used in experiments. They are
preserved for interpreting those experiments, not silently promoted into proof of near-optimal intelligence.

Report each result's scope: exploration, frozen comparison on fresh seeds, transfer to a new family, or a
physical implementation check. Describe what the comparison brain knows. The same sensor interface does not
remove an advantage from a supplied model family, prior or hidden state. An oracle or successful hand design
shows an achievable informed behaviour; an unsuccessful reference does not prove impossibility.

The evidence budget concerns the unknowns needed for good action, not the number of bits in our world-generating
program. [BOUNDS.md](BOUNDS.md) explains conditional information bounds and their limits. Formal protocols and
test exposure are in [GRAMMAR.md](GRAMMAR.md) and [PROGRAMME.md](PROGRAMME.md#sealed).

## How we explore it

Manual solutions are probes: they show an opportunity and help identify the capability it requires. The research
then asks how a reusable mechanism could acquire that capability autonomously, why it works, and where it fails.
An experiment is useful when it distinguishes explanations, checks a premise, reveals a mechanism or opens a
new direction, even if it does not raise a score.

Before substantial construction we diagnose the failure and consult primary literature. Afterwards we state
what changed in our understanding and in the route to the goal. The [working discipline](AGENTS.md#research-discipline)
keeps requirements, preferences, conjectures and observations distinct, and provides for continued useful work
while the user is unavailable.

## What we've learned

The detailed evidence and qualifications are in the notebooks. The [2026-11-16 review](discrete/NOTEBOOK.md#review-2026-11-16)
connects the major experiment families to the goal; it is a review of existing records, not new experimental data.

**A local repair is possible in a restricted setting.** The earlier recruitment experiments grew a link that
allowed learned information to affect action. They also tested a generic recruit's menu of operations. Those
results belong to the earlier noise model and limited repair task; they do not establish general self-improvement.
[Recruitment notebook](experiments/NOTEBOOK.md#where-it-stands).

**Small circuits can learn and act, but their physical accounting matters.** The minimal search found compact
solutions to the food distinction. Later transistor and supply-power accounting changed their apparent size and
cost substantially. A software block count is not a physical resource budget, and a search result is not proof
of minimum possible size. [Minimal notebook](minimal/NOTEBOOK.md#where-it-stands).

**Useful evidence depends on what the robot does.** Body-learning experiments show that movements can expose
information that sparse reward does not reveal quickly. Sensory predictability alone selected unhelpful behaviour;
sensory–motor coupling helped balance but failed to choose the best tempo. Prediction and information need a
specified target and a connection to action value. [Discrete notebook, D44–D54](discrete/NOTEBOOK.md#review-2026-11-16).

**More capacity helps some challenges; general scaling remains unproved.** Frozen sequence comparisons show
substantial gains. Timing gains are less regular, and combined challenges remain below their stated passing
criterion in the latest comparison. The current capacity number controls stream allowances, rather than
total allocated material: fixed units can exceed it at birth, and later allocations exceed it too. Those
curves need an actual resource account before they establish economical material scaling.
[Scaling assessment](discrete/NOTEBOOK.md#review-2026-11-16),
[resource audit, D76](discrete/NOTEBOOK.md#d76-resource-floor).

**Some extra memory has much more apparent value than the rest.** On the hardest tested sequence,
extra room in the ten streams that track colour events recovers much of the larger brain's improvement
with far fewer new units. The remaining performance gap is unresolved. The sampled all-food lives grow
nothing, but still run the fixed machinery. These measurements identify an opportunity to use resources
better; they do not prove that the remaining memory is dispensable.
[Resource observation, D77](discrete/NOTEBOOK.md#d77-resource-observation).

**Extra room helps through a few better forecasts, and the brain already trusts the right ones.** Rebuilding the
brain's combined prediction offline shows where extra room pays on the hardest tested sequence: in the forecasts
of the ten colour-event streams, which with room predict from long remembered contexts. The brain's way of
weighting its streams is already within a few hundredths of a bit per taste of the best single stream chosen
with hindsight, so who it trusts is not the bottleneck; but weighting is necessary, since an equal average of all
streams erases the whole gain. How well the brain predicts accounts for most of how well it eats. Context
length, evidence and age of the speaking units do not explain differences between allocation rules; giving the
event streams a head start, plus one unit for every other stream and the existing market, matches the large
brain at 57% of its material, on fresh seeds too. Without that unit, the other streams speak only from single
remembered symbols, and their weak forecasts make the creature's early choices worse. On the timing family the brain
also trusts the right streams, but there the gain from capacity does not show up in prediction.
[Forecasts and trust, D93–D95](discrete/NOTEBOOK.md#d93-room-prediction),
[what lifts the head start, D96](discrete/NOTEBOOK.md#d96-ruler-ingredients).

**Room earned by bits saved arrives too late.** The brain's market lends a stream more memory once it has saved
bits over a default guess. But a stream needing long contexts cannot save bits until it has the memory, and bits
can be saved only as fast as tastes arrive (about one every two seconds), so most requests from the useful streams
fail and the market moves little room to them. Lowering its price spreads room to streams that saved bits by
chance instead. Any rule that pays for memory with evidence already gathered faces this delay. Longer lives repay most of it:
over 1000 s the market nearly catches the hand-set head start.
[Market diagnosis, D97](discrete/NOTEBOOK.md#d97-market-diagnosis), [price test, D98](discrete/NOTEBOOK.md#d98-market-price),
[longer lives, D99](discrete/NOTEBOOK.md#d99-longer-lives), [weak speakers, D100](discrete/NOTEBOOK.md#d100-silent-others),
[timing, D101](discrete/NOTEBOOK.md#d101-timing-prediction), [fresh seeds, D102](discrete/NOTEBOOK.md#d102-fresh-seeds).

**Allocation matters; its useful signal is still an open question.** Under a real memory cap, letting
streams compete by prediction weight beats an equal split on fresh sequence lives, but the smaller brain
fails to match the original design. The first explanation went beyond the evidence: family totals hid
individual predictors that saved bits, and the weight plots included streams that were not speaking.
We must distinguish a predictor's stored weight, its contribution to the present prediction, and the
future benefit of preserving or enlarging its memory. That distinction matters for a reusable local
module deciding what to keep. The small follow-up weakens the claim that early usefulness explains the
larger brain's advantage and exposes more frequent errors in crediting predictions under the contest.
Replaying corrected credit barely changes immediate choices, but letting it affect the live learner
changes memory allocation and later behaviour. It has not demonstrated a performance improvement.
A checked contract now scores the prediction actually made and delivers unit credit only to its original
surviving memory. On the existing ten-pair development set it does not demonstrate better performance,
and the smaller contest brain's gap remains. Correct credit does not settle which memory to preserve;
the trace now shows that foreign recycling often changes a current prediction, while some new units
disappear within the same feedback event before issuing any forecast. This does not show they had zero
causal effect or would have helped later. Replaying the exact history shows that many would meet later
teaching opportunities, including 821 of the 923 immediately deleted newborns. Recurrence alone does
not establish useful new information or justify keeping them at the expense of other memory.
Reconstructing their forecasts shows: some retained units beat their surviving stream, but most
recurring candidates lose to a uniform 50:50 forecast. Better probability scores can come from reducing
misplaced confidence without recovering useful structure; here retaining units also worsens the
aggregate choice score on overlapping comparisons. Yet reducing confidence in the actual combined
forecast worsens both probability scores in all four historical lives checked. A weak individual readout
does not imply a weak combined prediction. On the same corrected life, only 336 of 3653 recurring
retained units beat the combined forecast, and one supplied rule for combining candidates without
future knowledge fails to improve it. This weakens simple retention as the explanation. Extra memory
could instead enable new combinations to form. Counting actual construction weakens that too: units that
had predicted little or nothing are parents of about 6% of new units, half of all new units never make a
forecast when food is tasted, and about one in five of those that do beat the brain's combined forecast.
Deleted units could have been parents of many combinations nothing living could build, but scored offline
those combinations predict about as poorly as the ones growth did build. So neither keeping old units nor
the combinations they could have formed explains why extra room helps; the next finding says what does.
[Allocation comparison, D78](discrete/NOTEBOOK.md#d78-allocation-rules),
[review and diagnostic, D79](discrete/NOTEBOOK.md#d79-active-mixture),
[scoring replay and feedback, D80–D81](discrete/NOTEBOOK.md#d80-scoring-replay),
[consistent credit comparison, D82](discrete/NOTEBOOK.md#d82-issued-credit),
[allocation and construction trace, D83](discrete/NOTEBOOK.md#d83-allocation-trace),
[future observation opportunities, D84](discrete/NOTEBOOK.md#d84-future-evidence),
[retained prediction and confidence control, D85](discrete/NOTEBOOK.md#d85-retained-prediction),
[whole-mixture counterexample, D86](discrete/NOTEBOOK.md#d86-mixture-confidence),
[same-history combined reference, D87](discrete/NOTEBOOK.md#d87-retained-mixture),
[memory as parts, D88–D92](discrete/NOTEBOOK.md#d88-parent-census).

**Separating failure causes made timing progress possible.** The timing investigations distinguished missing
cycle position, recovery of trust in predictors that improve late, and period estimation. Acquisition and tracking
then supplied a useful literature-informed mechanism, confirmed on fresh seeds. Its range of generality remains
to be established. [Timing assessment](discrete/NOTEBOOK.md#review-2026-11-16).

**Useful evidence can survive; how cheaply its readout can be learned is still open.** In the noisy
changing-world diagnostic, a stored numerical summary retains a useful choice signal. Supplying a grouping of
related values helps its readout learn. Two priors over one family of learned groupings (exact Bayesian
averaging over ordered intervals) did not establish a decision gain. Their uncertainty does not exclude
recovering most of the supplied advantage. A strong sharing assumption can substantially delay learning when
neighbouring values need different answers. This tested two assumptions, not readout learning in general:
it does not show that discovering a useful readout is inherently hard.
[Information-path audit, D73](discrete/NOTEBOOK.md#d73-noisy-evidence),
[learned grouping and counterexample, D74](discrete/NOTEBOOK.md#d74-learned-sharing).

**Copying a predictor can change its influence without adding information.** The present selector gives
each predictor an initial weight and repeatedly redistributes weight among them. Copies receive extra
influence unless both allocations are divided between them. This exposes an accounting requirement for
a growing repertoire; it does not justify discarding partially overlapping predictors.
[Controlled duplication, D75](discrete/NOTEBOOK.md#d75-redundant-selection).

**An informative task need not reward acting.** The drift reference receives actual eaten colours that the brain
must infer. Its hardest noise conditions also randomise the scored meal value, so even choosing the favourable
colour has negative expected gain. These cases remain useful inference tests, but improved colour choice does
not demonstrate economical foraging. [Reference and reward audit, D73](discrete/NOTEBOOK.md#d73-noisy-evidence).

**Simulator checks and negative results change the science.** Tightening numerical integration overturned an
early learning result; later interface checks exposed shortcuts; correcting a duplicate-removal bug changed the
interpretation of growth. These are reasons to trace claims to configurations and logs. [Discrete notebook](discrete/NOTEBOOK.md#review-2026-11-16)
and [body/simulator notebook](NOTEBOOK.md#where-it-stands).

## The ground rules, for every brain

[AGENTS.md](AGENTS.md#ground-rules-for-every-brain) owns the interface, locality, noise, timing, comparison and
physical-validation rules. The body and simulator must not perform the brain's learning or credit assignment.
Exploratory block models and physically validated circuits are different levels of evidence; label them.

## The creature and its world

The creature is our robot, in simulation: a disc whose front point is the mouth, with eyes looking ahead (one sensor for each colour) and a forward thruster on
each side of its rear rim: both thrusters together drive it straight ahead, one alone makes it veer. (It was a triangle
until 2026-10-31; the disc keeps the mouth where the point was, so every life is unchanged.) Red and blue blocks lie
about the world; one colour is poison, alternating from life to life. A brain fires its two motors and is told only what
its sensors see and the taste. In *all-food lives* both colours are food, so there is nothing to learn: the control for
recruitment, which should then grow nothing.

## Quick start

Needs Python 3.10 or later.

```bash
git clone https://github.com/pilgrimbeart/simple-learner.git
cd simple-learner
python3 -m venv .venv              # Windows: python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python creature.py                 # watch a life (the designed circuit; --brain knowing-circuit etc. for the others)
```

Once the environment is active, `python` is its Python. In a new terminal, activate it again first. On Ubuntu, if
`python3 -m venv` says ensurepip is missing: `sudo apt install python3-venv`.

The first run after a brain's code changes pauses for 15-30 s while numba compiles it (the window says so); after
that it starts in about a second, from numba's cache.

In the live view:

| key | |
|---|---|
| `r` | a new life (a new seed, a new wiring; poison alternates red and blue) |
| `b` | the next brain (the circuit brains in turn), in a new world with the same seed |
| `s` | the designed circuit's schematic (wheel: zoom, drag: pan, Esc: close) |
| `i` | the rules the simulation enforces: the interface, noise, limits, seeds, the job, the score, what is measured (wheel or up/down: scroll; numbers read from the code; "copy all" puts them on the clipboard as text, "open as text" opens them in a text viewer; `python creature.py --rules` prints them) |
| space | pause |
| up / down | faster / slower; below a tick a frame, down waits 2, 4 ... 32 frames per tick |
| `a` | automatic speed again (slow until a little after the creature first moves, fast otherwise) |
| Esc | quit |

### What you're seeing

- **Left, the brain:** each neuron's voltage (sky blue), a white line at each spike.
- **Right, the world:** red blocks and blue blocks, lettered R and B, and the creature, a
  disc with its mouth marked by a dot on the rim the way it faces, its thrusters small squares on the rear rim, and what its eyes see: a pale beam ahead, the
  corridor its mouth will sweep, fading with distance, each of its rays stopping at the first block it meets (so a
  near block casts a shadow). A ring round a thruster shows it firing. "yuck!" is a poison meal.
- **Below:** the tick, the stage of life, which colour is poison this life, and the recent meals; and buttons for `b`,
  `i` and `s` (above). The life waits while the rules or the schematic are open. The window can be resized or
  maximised: the panels stay square, centred, and the block view takes the rest.
- **At the bottom, for the circuit brains, the block view** (`blocks.py`): the brain at level 1, found from its
  netlist and drawn live. Neurons are circles (brightness: voltage; white: a spike), synapses arrows (solid excites,
  dashed inhibits, thickness: current), and every other node a meter hung where it belongs (on the synapse it gates,
  or by the neuron it acts on), with the eyes, thrusters and taste at the edges. A unit grown in the life (the
  recruiting circuit's bridge, the healing circuit's recruits) appears as a new circle, outlined for a while. A
  circuit with no neurons to find (the minimal search's) gets the **node view** instead: level 0, every node a circle
  (a memory a square), every element an arrow, a dotted line from the node that gates it, a loop for a node's
  feedback on itself.

## The circuit brains

These use the mixed-feedback elements described in [MIXED_FEEDBACK.md](MIXED_FEEDBACK.md). The designed,
baseline, adjusting, knowing, recruiting and healing variants remain available through `creature.py`.
Their early recruitment results used fixed per-node noise without the later mismatch model. Do not read their
historical scores as current-substrate validation. [Current state and history](experiments/NOTEBOOK.md).

## The minimal circuit search

This line asks how small a circuit can be that learns the basic food distinction and drives effectively, without
requiring growth or a particular neural architecture. Search, pruning and physical accounting are documented in
[its notebook](minimal/NOTEBOOK.md). [The league](minimal/LEAGUE.md) is generated; its historical names and
rankings are interpreted under the notebook's dated scoring and part-count conventions.

## Discrete circuits

This line began with common electronic parts in SPICE and developed the fast block model used by the current
learning experiments. Its notebook contains the control baselines, manual interventions, prediction, exploration,
growth and timing investigations. Read [Where it stands](discrete/NOTEBOOK.md#where-it-stands) before using an
old result or executing an old “next” instruction. A block-model success does not automatically establish a
physical circuit with the same learning, power or noise performance.

## Next

[PROGRAMME.md](PROGRAMME.md#conditional-programme) owns the conditional work plan;
[QUESTIONS.md](QUESTIONS.md) owns the ranked questions and discriminating investigations.

## Terms

**Research and evaluation**

- **Scaling curve**: performance or the hardest challenge passed against available brain resources, with the design fixed.
  A **cost curve** records what those resources cost on simpler tasks.
- **Ladder / rung**: a family of challenges ordered along a declared difficulty dimension / one level in it.
  **Certified** and **solved** are protocol-specific labels; the historical thresholds are in [GRAMMAR.md](GRAMMAR.md#scaling-milestone-recorded-on-2026-11-09).
- **Raw material**: generic spare capacity. **Starting brain**: the declared initial design. **Committed**: affecting
  behaviour in the historical milestone; allocation, activity and retention must also be counted separately.
  **Nominal P** in the growing-network code sets stream allowances; it is not measured total material or
  an enforced total-unit cap ([D76](discrete/NOTEBOOK.md#d76-resource-floor)).
- **Yardstick / reference**: a comparison method whose supplied information must be declared. A **told** controller
  receives information the candidate must infer. Neither is automatically an optimal achievable controller.
- **Catastrophic forgetting**: learning a new task damages an earlier skill. Retaining an old unit is not sufficient
  evidence that its skill can be recalled.
- **Log loss**: minus the base-2 logarithm of the probability assigned to the observed target, measured in bits.
  State the target: a noisy taste is different from the hidden food state. **Calibration**: whether stated
  probabilities agree with observed frequencies. **Proper scoring rule**: one that rewards an honest probability
  forecast in expectation; see [BOUNDS.md](BOUNDS.md#prediction-belief-and-action).
- **Brier score**: squared difference between a predicted probability and the binary outcome (0 or 1).
  Lower is better; here the binary convention is used without also adding the complementary outcome.
- **Phase-locked loop (PLL)**: feedback that adjusts an oscillator to track an observed rhythm. **Acquisition**
  finds a plausible rhythm; **tracking** follows it. A **Kalman filter** estimates a changing state under an explicit
  dynamical and observation model; its optimality is conditional on that model.
- **Issued forecast** (D82): the probability, choice and speaker identity recorded when a prediction is made,
  before feedback. Scoring that record differs from crediting a replacement selected after memory changes.
- **Fixed share**: redistribution of some predictor weight so previously unsuccessful predictors can recover when
  conditions change. It does not itself preserve the knowledge inside those predictors.
- **Hidden Markov model**: a model in which an unobserved state changes probabilistically and generates noisy
  observations. A filter estimates the current state from observations so far; knowing the model is different
  from learning it.
- **Evidence pooling**: using observations from several related cases to learn shared parameters. It can reduce
  the data needed, but can mislead if those cases require different predictions.
- **Context weighting**: averaging predictions over possible groupings of observed contexts, using how well
  each grouping predicted past outcomes. The grouping prior and permitted distinctions must be stated.
- **Model evidence**: the probability a model assigns to the observed sequence after averaging over its
  unknown parameters. Ratios of model evidence update prior odds; they are not counts of learned state bits.

**Mechanisms and historical names**

- **Growing network** (the user, 2026-11-12; D59): a brain of small detectors (*blocks*) with proposed local growth rules. A block is born
  where a guess about the food colour keeps failing, joining two units that were active together, so blocks build on blocks; each
  learns what came next when it fired. *Copies* (two blocks firing alike) and unused blocks are cleared, by written rules or by
  competition for a modelled resource budget. The locality and physical cost of the whole system remain to be audited.
- **Stream**: one of the growing network's records of events, each ticking on one kind of event (every taste, every good meal, every
  bad meal, every red or blue eaten); contexts count events in that stream; elapsed time is always in seconds, never simulator ticks.
- **Stream allowance** (D76, D77): how many memory units a stream may hold before a new one must recycle an old one; the setting P is
  divided equally among the 168 streams of the frozen design, and the market can move allowance between them. It is not a cap on total material.
- **Market** (D67, D97): the growing network's existing rule for moving allowance: a stream whose allowance is full may take one unit
  from a stream that has saved nothing, if it has itself saved more than `POOL_BITS` (1 bit) of prediction over a default guess for
  each unit beyond its share.
- **Event streams** (D77): the ten streams ticking on colour and taste events (every, good, bad, red and blue, each recording colour or
  outcome), as opposed to the clock, integrator and rhythm streams.
- **Head-started ruler** (D96, lab rule R+M+1): a hand-set allocation that gives the event streams a fixed share of growth from birth,
  one grown unit to every other stream, and the market; a ruler for what allocation could achieve, not a design.
- **Weight contest** (D78, lab rule `W`): an allocation rule under a total cap. When the shared supply of units is used up, a stream
  that needs a new unit compares its weight in the prediction mix with one other stream chosen at random, and takes a little-used unit
  from it if that stream's weight is lower; otherwise it recycles one of its own.
- **Prediction leave-out check** (D79): recalculate an already-issued prediction with a chosen family of predictors omitted,
  then score both predictions on the same later observation. It measures that family's immediate contribution on the recorded
  history, not the behaviour of a brain that never had those predictors or the value of adding more memory.
- **Trophic support** (D59, biological analogy): a block receives credit from successful blocks built on it.
  **Siblings** are blocks built on the same parent. Competition for the modelled budget can remove blocks;
  this is not by itself a physical energy measurement or evidence of biological equivalence.
- **Play**: exploratory activity intended to gather useful evidence before or alongside pursuit of food. Its later
  benefit is a hypothesis to test at matched time and energy, not a consequence of calling it play.
- **Boredom** (the user, 2026-11-11): the switch between playing and working, set by whether learning or eating still pays. Bored
  of play, a brain stops when it has stopped learning (D46: play ends by itself when no unit's predictions are improving beyond their
  noise); bored of working, it plays when the world gives nothing (D47); the starting brain's own *bored* timer (running after some
  seconds without food) is the same signal at a smaller scale. The flip side of curiosity (Schmidhuber; Oudeyer and Kaplan).
- **Dancing brain** (historical proposal; D44–D54): a brain whose movement is driven from birth by many cycles of different timings, which
  settle on those that work. A **cycle** is one repeating pattern of movement with a recorder of what the senses did during it.
- **Knob** (D43): a setting the brain already has, such as a rate or threshold. **Balance** controls the relative
  rates of the motors; **tempo** scales their rates together. **Stride** names the movement produced by a beat
  in the body-learning experiments. How those quantities relate to thrust and drag depends on the body model;
  D53 shows why a formula for one body need not transfer to another.
- **Context tree** (D39): a tree of units, each holding which colour was food in one context (say, "the last two letters were red,
  blue"); a unit whose context turns out to hide two cases gets children that look one step further back.
  Related to context-tree methods and prediction by partial matching; the implementation is not thereby
  established to be exact context-tree weighting or an ideal learner.
- **Ledger** (`lab/v/LEDGER.md`): one line per run: its cost, the belief it could move, the prediction, and whether it surprised us.
- **Register, look-back, record** (D38): a register is a row of units each holding one letter (which colour was food at a step),
  moved on one place by some kind of event (a good meal, a taste, a beat of a clock); a look-back k compares each step with the
  one k places back. The record is the brain built from them, following the best register and look-back once it beats a cautious
  default by the **Occam bar**, the historical name for an evidence threshold favouring the default.

**Units** (the axioms: `units.py`)

- **Real units**: everything in SI, every number that can be derived derived from a few axioms (`units.py`).
- **Tick**: the simulation's step. In the live view and the circuit brains, 10 ms for the body, with the circuit
  integrated in steps of 0.125 ms, 80 to a tick. In the programme's engine (`lab/stage2_lang/`) everything happens at
  its own moment in seconds and the step is halved until results stop changing: about 1.25 ms is fine enough for this
  body, whose fastest time constant is 20 ms. The live view shows real time at about 30 ms of a life a frame (it says
  how fast it runs against real time).
- **Supply**: the chip's, 1.8 V across (SKY130's core devices), analogue ground halfway. The **rails** a node stays
  within are the supply's, +-0.9 V; an output's current fades within a few hundredths of a volt of them.
- **Typical voltage**: a third of a rail, 0.3 V: the unit a design's voltages are reckoned in (a gate is open at it, a
  spike resets below minus it). The designs before 2026-10-26 were drawn at 1 V and +-3 V rails, and are converted.
- **Typical sizes**: what circuits are built around, as in subthreshold analogue silicon: a capacitor of 2.5 pF, a
  current of 0.3 nA (which moves it a typical voltage in 2.5 ms, the body's pulse) and a resistor of 1 GOhm. The body's
  pulses are 3 typical currents. The recruitment line's circuits keep a typical voltage of 1 V and a current of 1 nA:
  not yet built in transistors.

**Circuits and noise** (the model: `mixed_feedback.py`'s docstring)

- **Level 0, level 1**: nodes and elements; the motifs built from them.
- **Shot noise**: a current is carried by discrete events (ion channels opening, vesicles released, electrons
  crossing a transistor), so it flickers, with variance in proportion to its size, summed over all the currents on a
  node, not their net. A circuit can drown it by raising its currents only as the square root, for power in proportion.
- **Resting noise**: what a node has even when no net current flows. In biology, membrane noise: a node's capacitance
  is membrane area, whose channels flicker even at rest: noise in proportion to the capacitance, so a node k times
  bigger is quieter only by the square root of k. In silicon, a leak's thermal noise (kT/C). A memory node has none:
  still until written, then rough by the square root of what is written.
- **Mismatch**: no two parts are alike: every part off by about 10% of itself (offsets by a tenth of a typical
  voltage), drawn at birth, so
  no design can lean on exact values or exact cancellations.
- **Substrate**: whose noise a circuit lives with, never none: **biology** (shot noise in events of 12.5 fC, between
  an ion channel's and a vesicle's, and membrane noise), **silicon** (single electrons and a leak's thermal noise:
  about 280 times quieter in amplitude at these currents) and **biology x2** (twice biology's, a margin).

**Recruitment**

- **Recruit**: a unit grown in the life, attached locally. A **bridge** is the recruiting circuit's: a neuron that
  splits a synapse. The healing circuit's recruit is generic: it attaches to the frustrated unit and its one-edge
  neighbours, and has a **menu** (inhibit or excite one of them, or turn down one of their synapses).
- **Frustration**: a unit's slow node that fills when pain it anticipated comes anyway; past a threshold it triggers
  growth.
- **Eye**: in the experiments, a sensor neuron by the colour it sees this life (the *poison eye*): the measurement's
  name, never the brain's.
- **Rung**: a step on recruitment's ladder: rung 0, a unit adjusts itself; rung 1, it recruits a link.
- **Win-stay lose-shift**: how a healing recruit chooses: an option latches on and stays until the tastes that follow
  it tire it out, then another wins. Judged by the **share** of bad tastes after it, not their rate.
- **Healing**: recruitment pictured as an inflammation and healing response: the damage is the frustration, the
  recruit the repair.
- **Wave**: how many hand-offs a recruit is from the first frustrated unit. A wave-1 recruit still frustrated long
  after it came is frustrated itself and grows wave 2, one step further out. A **cascade** is that hand-off.

**The minimal circuit search** (the rules: `AGENTS.md`)

- **Parts**: as the circuit is built in transistors (`chip.py`'s blocks: an element a differential pair, its mirrored
  tail and outputs, a gate, preamplifier, level shifter or filter where it needs one): transistors, resistors,
  capacitors, diodes and bias sources.
- **Power**: what the supply delivers to the transistors: every bias, mirror copy and auxiliary amplifier, not only
  the currents into nodes (before 2026-10-26 only those were counted, 150 times too few).
- **Analogue ground**: 0 V, halfway between the rails: one buffer for the chip, to which every leak's resistor runs.
- **Memory node**: a SONOS cell (SKY130's flash transistor: charge trapped in nitride, held for years), its threshold
  the stored value, written by tunnelling through a pulse driver that fires only above 1% of the write's full current.
  Writing needs 10.5 V across the cell, from charge pumps or extra supplies: not yet in the power (a known anomaly).
- **The job**: learning the bit well enough (food:poison at least 3 in the last third of a life), eating enough (1
  food per 10 s) and rarely stranding (at most 5% of lives), with every substrate judged.
- **Stranding**: a life that eats, then finds nothing more (no food at all in its last third). A creature that
  travels only towards food it sees spins on the spot for ever once it has eaten what is near.
- **Buildable**: within a chip's limits (`units.py`), a rule since 2026-10-23: no resistance above about 77 GOhm, no
  capacitor above 50 pF, no time constant above about 3.9 s without a floating gate, no current below 1 pA.
- **Polish**: tuning a circuit's values (CMA-ES), each generation on fresh lives. **Pruning**: trying every single
  simplification (an element, a filter, a gate, a leak, a clamp taken away) and keeping the best that costs no more
  than a little, until none does.
- **Meals gained**: food, less 2 for each poison (as in the score).
- **Body efficiency**: meals gained per meal's worth of energy spent (a meal being worth 10 uJ): resting (1 uW, a
  meal every 10 s, whatever a creature does), moving (20 nJ a thruster firing) and thinking (the circuit's power, tens
  of nW: for HR_31p_pol about a sixth of what moving costs). Above 1 a creature gains. Haste wastes fuel and dawdling the resting cost,
  so a careful creature has a best speed.
- **Gain rate**: meals gained per 10 s, energy free: speed and accuracy.
- **What counts** (the user's order, 2026-10-27): among brains doing the job, performance (the best driver for
  energy, body efficiency, and the best for speed and accuracy, gain rate, each its own dimension, never traded), then
  power, then area (what it takes to build); simplicity (fewest parts) behind them, to understand a design. Evolution
  pays for power and material and rewards performance; it doesn't pay for elegance. (Until then, 2026-10-22 to 27:
  three objectives, the simplest brain, efficiency and gain rate, which the league still ranks.)
- **Thrift**: food per 1,000 thruster firings (fuel alone, time no object); shown, not ranked.
- **Area**: what a circuit would take on a chip, by analogy with subthreshold analogue CMOS, in unit transistors (15
  square microns each): an element 5 (a transconductance amplifier), a gate 3 more, a leak 2, a clamp 1, a memory
  node's floating gate 5, and each capacitor its own area as a MOS capacitor (5 fF per square micron: 2.5 pF is 33
  unit transistors). Capacitors dominate, as on real neuromorphic chips. Shown, not ranked.
- **Hold**, **roam** (the hold-and-roam circuit, HR): after a sighting of the food colour, a slow node keeps both
  thrusters firing together for a fraction of a second, so the creature goes on to the food instead of reacting for a moment and
  sweeping past it; after a long spell with nothing seen (a *giving-up time*, in foraging theory's terms), it drives
  straight off to look elsewhere. Matching
  the brain's speed to the body's sweep and momentum (impedance matching).
- **Policy**: a brain written as a few rules in code, not a circuit (`discrete/policies.py`): it gets the eyes'
  pulses and the taste and fires the thrusters, as any brain, with no parts, power or noise of its own. A life costs
  about a second against a circuit's minutes in SPICE, so policies rank ideas cheaply; told from birth which colour is
  food (`oracle`), a policy provides an informed comparison, not a proven ceiling. A rule's own values don't transfer to a
  circuit; a **fast model** does: a policy whose every part is a block of the circuit with the numbers measured on
  SPICE's bench, checked against the circuit's own lives (`discrete/NOTEBOOK.md`, D13).
- **Robust judging**: in the fast model, each life draws its own parts' errors (their spread over chips measured in
  SPICE), and its own body where an experiment says, instead of every copy being perfect and identical.
- **Doubt**: the learning node of the discrete circuits, a running tally of evidence that the creature's guess of the
  food colour is wrong; in probability's terms a log-odds, kept as a CUSUM (a tally that can't go below a floor,
  raising an alarm at a threshold: Page's 1954 test for a change).
- **Sepulchre's rules**: an experiment's constraint, every node leaky except memory nodes and no clamps (gates and
  floating-gate memories allowed).
- **Arena**: a world of ten robots and nothing else, each with a red mouth and a blue tail; a robot eats by holding
  its mouth on another's tail (a meal a second), which tastes good to the biter and bad to the bitten; an empty belly
  is death, and a newborn takes its place (`discrete/NOTEBOOK.md`, D18).
- **Grower**: generic machinery beside a brain that notices a gap (a bad outcome nothing predicted), grows a recruit
  where it is, and lets the recruit try the simplest operations, keeping what works; told nothing of what it is for.
- **Story**: one performance issue followed from a brain with no concept of it, through the gap to it solved perfectly,
  manual interventions and how a brain could detect it, to the simplest circuit that does (`STORIES.md`).
- **Bank of predictors**: several rival models of what taste means, all kept up to date and scored on every taste, with the creature
  following whichever has earned the most evidence over the default (`STORIES.md`, One universal circuit).
- **Off-policy scoring**: judging a predictor on observations generated while something else was in charge.
  Estimating the return of a different policy additionally needs appropriate coverage and causal assumptions;
  prediction scoring alone does not do that. **On-policy** evaluation observes the policy's own behaviour.
- **World** (in the programme): a rule changing the creature's world, written in a small language (`lab/stage2_lang/`),
  for instance "the colours swap every 12 s" or "a meal soon after the last is bad". The language can't touch the
  brain or break the interface. A **generator** draws worlds at random from it, frozen before any draw.
- **Arm**: one comparison condition, run on matched seeds and exogenous conditions; actions can still create different histories.
  The following base/bank/reference names describe the historical stage-3 protocol. **Base**: the existing circuit;
  **bank**: base with the bank of predictors; **told**: the bank's own parts told the right colour at every moment, a
  yardstick, not a brain; **reference**: the historical frozen learner holding 12,591 supplied hypotheses, not an unrestricted optimum.
- **Gap** (historical stage-3 definition): how much better the told arm does than base (or than standing still, if base is below that). A world has
  **something to learn** if its gap is at least .1 and surely above 0. **x**: the share of the gap the bank closes;
  **r**: the same for the reference. A world **passes** if x is above a quarter and above half of r ([historical protocol](lab/v/programme_before_review_2026-11-16.md#the-primary-result)).
- **Coverage**: the share of worlds with something to learn that the bank passes. With uncertain worlds it is a range:
  sure passes at the low end, sure passes plus those too close to call at the high end.
- **Doing no harm**: a claim that harm larger than a declared practical margin has been excluded. The historical
  stage-3 rule, “never surely more than .1 below base”, was weaker: failure to detect harm does not exclude it.
- **Pair**: two lives on one seed, red then blue as poison, so a brain that ignores taste scores 0 on average; intervals
  are taken over pairs.
- **Sampler**: a program that draws random worlds from a grammar with chosen probabilities, and so decides what "most worlds" means (`GRAMMAR.md`).
- **F_novel**: on challenges a circuit's design never saw, its pass rate above the base circuit's, as a share of what the base circuit leaves. The design is fixed; the circuit still learns in each life (`PROGRAMME.md`).
- **Description length**: bits under a specified encoding or model class. It depends on the code and prior;
  it is not automatically the evidence the robot must acquire to act well.
- **Occam factor**: the marginal-likelihood penalty arising from averaging a model over its parameter prior.
  Distinguish it from the log2(K) prior cost of one of K equally weighted hypotheses; see [BOUNDS.md](BOUNDS.md#how-long-a-life-must-be).
- **Bits per taste**: target- and model-dependent information, not simply a pulse count. For a binary symmetric
  channel with independent error probability e, capacity is 1 - H2(e) bits per use; correlations and the robot's
  sampling policy matter. Do not equate channel capacity, realised learning and decision value.
- **Run detector** (Page's CUSUM): a score that rises on wins, falls on losses and stops at a floor of zero, so it reacts to a recent run and forgets what came before. It is the standard test for a change at an unknown time. The bank's entry rule is one, and its picks resemble those of an exact posterior that expects frequent change.
- **Function-preserving growth**: preserving the input–output function at insertion under stated assumptions.
  It does not eliminate material, power, communication or subsequent learning costs ([PARTS.md](PARTS.md)).
- **Ideal observer** (Geisler's term, the user's choice, 2026-11-01): a brain of unlimited reasoning but only the
  senses, beats and tastes a real one has; not omniscient. An optimal observer/controller bounds performance only within its stated model, prior,
  information and objective; an implemented approximation is a reference ([BOUNDS.md](BOUNDS.md)).

**Names**: in prose "the designed circuit", "the knowing circuit"; on the command line `designed-circuit`,
`knowing-circuit` and so on. Recruitment's baseline, the **baseline circuit**, was called the
minimal circuit until 2026-10-21; "minimal" now means only the minimal circuit search (`minimal/`). A minimal-search
design is named by its origin and its parts (EF_22p: 22 parts, from the open search EF), with `_pol` once polished and
`_pruned` once pruned.

## Other commands

```bash
python creature.py --seed 3         # a particular life
python creature.py --measure 32     # every brain, 32 lives each with learning and 32 without, headless
                                    # (--brains to choose; --all-food: lives where both colours are food)
python creature.py --brain baseline-circuit   # the baseline for recruitment: drives at every block
python creature.py --brain adjusting-circuit  # rung 0: each neuron adjusts its own excitability
python creature.py --brain knowing-circuit    # the starting animal: knows what predicts pain, acts on nothing
python creature.py --brain recruiting-circuit # rung 1, guided: grows the bridge that lets that knowledge act
python creature.py --brain healing-circuit    # rung 1 by a generic recruit that knows nothing of the circuit
python creature.py --brain healing-cascade    # the first recruit can't help; a second, further out, can
python creature.py --spec minimal/results/N_E1_23p.json --brain N_E1_23p  # a circuit of the minimal search, live
python -m minimal.search RESULTS.json 60   # the minimal search: polish a circuit, then prune it
                                    # (--by efficiency|gain: for one objective; default the score)
python -m minimal.prune RESULTS.json  # prune alone
python -m minimal.evolve 60 --start RESULTS.json ...  # the open search over topologies
                                    # (--name NAME --resume: carry on after a stop, from its last save)
python -m minimal.league            # its league table (minimal/LEAGUE.md)
python -m minimal.check RESULTS.json  # a circuit in the real Life at two integration steps
python -m minimal.physical RESULTS.json  # could it be built? its parts in real units against a chip's limits
python -m minimal.draw RESULTS.json  # draw a circuit (media/NAME.svg): its signal-flow graph and its schematic
python -m minimal.spice RESULTS.json --check  # build it in SKY130 transistors; each element against its formula
python -m minimal.sheets RESULTS.json  # its transistor schematics, sheet by sheet (media/NAME_transistors/)
python -m minimal.spice_life RESULTS.json --seeds 100:116  # live it in SPICE, closed loop, against the simulator
python -m discrete.watch           # discrete circuits live, ngspice beside the body (--circuit learn_avoid --poison)
python -m discrete.life hold_drive  # discrete circuits closed loop in SPICE (--set k=v: other values)
python -m discrete.tune hold_drive 20   # tune a discrete circuit's values (--poison: for one that learns)
python -m discrete.judge discrete/results/hold_drive_tuned.json  # on held-out seeds (--motors X: unequal thrusters)
python -m discrete.poison learn_avoid  # a learning circuit, each seed red then blue as poison
python -m discrete.model            # the fast model: circuit B from its SPICE bench, judged robustly (k=v: change a block)
python -m discrete.blocks 0:32 OUT.json  # bench circuit B's blocks in SPICE on 32 seeds' tolerances
python -m discrete.policies         # rules, not circuits, on the real body (and discrete.variation: bodies that differ)
python -m discrete.draw             # redraw media/hold_drive_14.svg and .png
python -m experiments.e1_oracle     # the rung-1 experiments, E1 to E7 (experiments/NOTEBOOK.md)
python -m experiments.h_run 64 1000 "share*"  # the healing experiments (H series): named rules, on the leaderboard
python measure_recruitment.py 32    # recruitment's local signals, neuron by neuron, watched from outside
python test_compiled.py             # check the compiled circuit and eyes against plain numpy versions
python -m discrete.test_model       # check the fast model and circuit B are as benched and lived in SPICE
python schematic.py                 # redraw media/designed_circuit.svg and .png, the designed circuit's schematic
                                    # (needs pip install schemdraw cairosvg pillow)
python creature.py --record frames  # save a life's frames as PNGs, headless (media/life.gif: --seed 0 --seconds 100,
                                    # 180 frames taken evenly by tick)
```

## Files

| | |
|---|---|
| `creature.py` | a life (a body, a brain and the body's wiring), the live view, and the measurement |
| `world.py` | the world and the body: blocks, eyes, thrusters, mouth |
| `brains/circuit.py` | what every circuit brain shares: two sensor and two motor neurons, a taste node, running and drawing |
| `brains/designed.py` | the designed circuit: four excitable neurons, designed by hand |
| `brains/baseline.py` | the baseline circuit: those neurons alone, driving at every block (the baseline for recruitment) |
| `brains/adjusting.py` | the adjusting circuit: every neuron adjusting its own excitability (rung 0 of recruitment) |
| `brains/knowing.py` | the knowing circuit: the baseline circuit plus a taste neuron that learns what predicts pain but has no outputs (recruitment's starting animal) |
| `brains/recruiting.py` | the recruiting circuit: the knowing circuit growing, in its life, the bridge that lets its knowledge act (rung 1) |
| `brains/healing.py` | the healing circuit and cascade: rung 1 by a generic recruit that knows nothing of the circuit |
| `measure_recruitment.py` | recruitment's local signals, watched from outside a circuit brain |
| `blocks.py` | the block view: a circuit brain at level 1 (neurons, synapses, the states they hold), live; and the node view, level 0, for circuits without neurons |
| `minimal/` | the minimal circuit search: `spec.py` (circuits as descriptions, the rules, scoring), `fastlife.py` (a whole life in one compiled call), `designs.py` (hand designs), `search.py` (polish), `prune.py`, `evolve.py` (open search), `league.py`, `check.py` (the real `Life` at two steps), `spice.py` (a circuit as SKY130 transistors, for ngspice), `sheets.py` (their schematics), `spice_life.py` (lives in SPICE, closed loop), `test_minimal.py`; its notebook `NOTEBOOK.md`, league table `LEAGUE.md`, results in `results/` |
| `discrete/` | discrete circuits: `life.py` (netlists of common parts, lives closed loop in ngspice, the bench), `circuits.py` (the designs), `cmos.py` (circuits in SKY130 CMOS: B), `model.py` (the fast model: B as its blocks' numbers), `blocks.py` (a circuit's blocks benched in SPICE, for the model), `tuner.py` (B tuning its own knobs), `test_model.py`, `policies.py` (rules, not circuits), `bodies.py` (bodies built differently), `variation.py`, `screen.py` (bench screening), `tune.py`, `prune.py` (pruning and the ladder), `judge.py` (held-out, paired), `poison.py` (lives with poison), `draw.py` (the schematic), `watch.py` (live); its notebook `NOTEBOOK.md`, results in `results/` |
| `experiments/` | the recruitment experiments (E series: the recruiting circuit; H series: the healing circuit), their lab notebook (`NOTEBOOK.md`) and leaderboard (`LEADERBOARD.md`) |
| `mixed_feedback.py` | the mixed-feedback element and circuit every circuit brain is built from |
| `chip.py` | how each part of a circuit is built in transistors: the blocks an element takes, and so the power the supply delivers |
| `test_compiled.py` | checks the compiled circuit (`mixed_feedback.py`) and eyes and mouth (`world.py`) against plain numpy versions |
| `schematic.py` | draws `media/designed_circuit.svg` and `.png`, the designed circuit's schematic (by hand: redraw it when it changes) |
| `AGENTS.md` | the rules, for agents and people: principles, honesty, every brain's constraints, how to work here |
| `lab/` | one-off experiment scripts and their logs (`lab/v/`), cited by the notebooks; run from the repository's root. `lab/universal_v.py`: the bank of predictors; `lab/stage2_lang/`: the language for worlds and its engine, in seconds |
| `PROGRAMME.md` | the current programme: its question, hypotheses, conditional investigations and decisions |
| `ABSTRACT.md` | the programme so far, in one page |
| `GRAMMAR.md` | the grammar of challenges the worlds are drawn from, and how they are judged |
| `QUESTIONS.md` | the open questions, most valuable first: parked mid-quest, removed when answered |
| `NOTEBOOK.md` | the lab notebook of the body and the circuit simulator: what was tried, what failed and why |
| `MIXED_FEEDBACK.md` | the mixed-feedback approach (Sepulchre and colleagues): what is new in it, the literature, and what it suggests here |
| `RECRUITMENT.md` | local recruitment: literature leads, hypotheses and the historical plan |
| `BOUNDS.md` | what limits how well and how fast any brain could learn in a life: the ideal observer, watching against intervening, the walls, MacKay |
| `STORIES.md` | one page per performance issue: the gap, the interventions tried, how a brain could detect it, the simplest circuit that does |
| `PARTS.md` | the ways a working brain could change itself (tune, modulate, rewire, prune, duplicate, add), a catalogue of parts by what they do in time, what triggers each change and what signal judges it; towards a universal circuit |

## Licence

MIT: see `LICENSE`.
