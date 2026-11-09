# simple-learner: circuit brains that learn

(Split from [nca-learn](https://github.com/pilgrimbeart/nca-learn) on 2026-11-02, with its history. The sheet brain,
a sheet of identical cells that grows its own nervous system, lives on there as a small self-contained demo; this
repository carries on the circuit brains.)

## The quest

How can useful, complex behaviour emerge in a brain from simple parts acting locally? We explore it by simulation, in
the simplest scenarios we can make: a small creature with two eyes, two thrusters and one sense of taste, in a world
of red and blue blocks, one colour food and the other poison. Its brain must learn, within one short life, which is
which: one bit. Every part acts only on what it can sense locally: nothing places its parts, no unit sees the whole,
and no god decides. And because a theory that can't be built is no use, we keep the brain simple and efficient to
build too, and check that it can be made in real components.

**How we got here.**
1. **The sheet brain** (in [nca-learn](https://github.com/pilgrimbeart/nca-learn)): a sheet of identical cells that
   differentiates and assembles a brain that learns the bit. It worked, and gave us the simplest possible body and
   world, made to run fast. But each cell needed complex circuitry inside, so the parts weren't simple.
2. **The circuit brain** (this repository): a small brain built by hand that learns the bit in a short life. Then built
   in real components (transistors, resistors, capacitors), lived in the circuit simulator SPICE, to check it is
   grounded in reality. It is. But SPICE is far too slow for experiments, so we now work in a fast model of the
   circuit's blocks, each block's numbers measured in SPICE.
3. **Towards a brain that optimises itself.** Now the aim is a general recipe: circuits that (a) notice, by
   themselves, that they are not doing well for the creature, and (b) put it right, from local parts, ideally by
   emergence rather than by our design. So we gave the same small brain many different mismatches with its world
   (unequal thrusters, a noisy eye, food whose colour swaps), cured each by hand, and looked for what the cures have
   in common. One circuit, the *bank of predictors*, does the job of many: it keeps several rival ideas of what taste
   means, scores them all on every taste, and follows the best. We then tested it on worlds drawn at random, so as
   not to mark our own homework.

**Where we are** (`PROGRAMME.md`; a summary in `ABSTRACT.md`). A life offers about 50 bits of evidence, but writing
down a world's rule takes hundreds, so no brain learns a world from nothing in one life: it can only choose among
what its structure already makes cheap. The bank copes with between a fifth and three fifths of the random worlds that
have something to learn, and uses its evidence almost as well as an ideal judge would. Where it fails, it lacks the
idea, mostly an idea about *time* (when the colours swap, how soon after a meal another turns bad). But its ideas
are ones we wrote in. The next step is a bank that makes its own rivals, out of many simple circuits connected in
various ways, so that the ideas come from simple repeated parts rather than from us.

Three lines of work so far:

- **The circuit brains** are small circuits of excitable neurons built from one mixed-feedback element (Ribar and
  Sepulchre). The recruitment series among them grows while it acts: it starts with too little and recruits more in
  the life, where and when a local signal calls for it. A neuron that knows something but can't act on it is
  *frustrated*, and its frustration grows the link that lets the knowledge act. A circuit designed by hand is kept
  for comparison.
- **The minimal circuit search** drops every architectural constraint (no neurons, locality or growth) and asks how
  simple a circuit can be that learns the bit, and how well a circuit can drive the body, searching by hand and by
  optimisation.
- **Discrete circuits** ask the same of common parts (transistors, resistors, capacitors, diodes) on a coin cell,
  living closed loop in SPICE: first the simplest that forages, then one that learns the bit.

## What we've learned

The findings that changed the direction of the work, each told in full in the notebook named.

- **The body must never do the brain's job.** Early on the body was changed to give food or poison only to the
  sensor whose colour was eaten. It looked like a simplification, since four mechanisms in the brain could go, but
  those mechanisms were the brain working out which sensor a taste was about (credit assignment), the hardest part
  of the task. The body was doing it instead. So whenever a change to the body lets the brain drop machinery, we ask
  where that machinery's job went (`NOTEBOOK.md`, Lessons).
- **Rules kept only in prose drift, so the code enforces them.** The sheet brain's central rule (in nca-learn) is
  that a cell sees only the average of what its neighbours show. Earlier experiments quietly broke it (reading one
  neighbour on its own), and nothing stopped them. Now each rule is built into the code's structure and tested, so
  breaking it fails loudly: the circuit brains' circuits, the minimal search's `check` (`NOTEBOOK.md`, Lessons).
- **In a circuit brain, nothing may happen outside the circuit.** The first recruitment rules were small programs
  running beside the circuit (keeping traces, thresholds, writing its settings from outside), so the program, not
  the circuit, did part of the work. The test now is: for every number that affects behaviour, which node holds it
  and which elements move it? If the answer is "the program", it isn't the circuit (`experiments/NOTEBOOK.md`,
  Lessons).
- **Find what the body allows before blaming the brain.** A scripted policy that is told the answer from birth and
  sees only what a brain would see shows the best any brain could do with that body. Twice this showed that the body,
  not the brain, was the limit: an early square body capped every brain, and the best circuits were driving the body
  badly (`NOTEBOOK.md`, The body; `minimal/NOTEBOOK.md`, M11).
- **Match the brain's speed to the body's.** A far block shows up as about one flash as the creature's narrow gaze
  sweeps past it, and the body keeps spinning for a while after a thruster stops. A brain that reacts briefly to each
  flash has lost the block before it can act. What works is a slow memory of the sighting that keeps the creature
  driving towards it for a fraction of a second (a *hold*), plus a timer that sends it off to explore after a long
  spell of seeing nothing (a *roam*). That more than doubled the best energy efficiency (`minimal/NOTEBOOK.md`, M11).
- **An average over lives hides the lives that fail.** The best circuits of one search ate plenty on average, yet in
  a fifth of their lives the creature ate what was near, then spun on the spot for the rest of its life (*stranding*);
  the other lives' meals hid it. It was found only by watching one life. Now each third of each life is charged for
  its own shortfall, the job limits stranded lives to 5%, and a behaviour is watched live before it is reported
  (`minimal/NOTEBOOK.md`, M8).
- **Noise costs no parts, so a search will use it.** Searching for the fewest parts, twice a part's job was handed to
  noise instead: a rhythm or an urge to explore that came from random jitter, not a clock. Such circuits work only
  at the noise level they were tuned at. So every circuit is judged with three noises: silicon's (about 280 times
  quieter than biology's at these currents, where any design that leans on noise fails), biology's, and twice
  biology's (`minimal/NOTEBOOK.md`, M7 and M12).
- **The body must vary from life to life, as the parts do.** Each life's circuit is built from parts with their own
  tolerances, so no design can lean on one exact resistor. The body had no such spread: every creature had the same
  strength, eyes and drag, and its two thrusters were identical to the last digit. An optimiser used that. A tuned
  9-part circuit that ignores its eyes, firing both thrusters 300 times a second, drove dead straight and ate four
  times as fast as any sighted circuit; with the thrusters 1% unequal, as any real pair would be, it drives in
  circles. The other way round, a learning circuit's straight run, pointed by chance along the world's axis, retraced
  one column it had eaten clear for its last 48 s, a stranding no built body would suffer. A circuit tuned on one
  exact body may be tuned to that body's accidents, so the body's dynamics need a spread of their own, like noise;
  and for every perfect symmetry in the simulation, ask whether a real body would have it (`discrete/NOTEBOOK.md`,
  D5, D9).
- **Declining poison isn't avoiding it, and an eaten-out patch needs leaving.** The learning circuit's only defence
  against poison was not to approach it; its mouth still ate whatever lay in its path. And eaten food reappears
  elsewhere, so a creature that eats every food near it and refuses the poison turns its patch into a poison patch,
  then circles there for the rest of its life. Both were found only by recording the nodes of the lives that failed.
  Two small additions cured both: the silenced eye's current, which had gone to ground, now turns the creature
  aside, and a few seconds with nothing seen sends it off straight (`discrete/NOTEBOOK.md`, D8).
- **A scripted policy ranks structures, not a circuit's values.** Rules that see only what a brain sees cost
  seconds a life against a circuit's minutes, and they ranked the ideas correctly: avoid poison, give up on an empty
  patch. Told the answer from birth, they also give a ceiling to measure a brain against. But their best speeds made
  the circuit worse, because a circuit's hold and drive don't behave like the rule's: values have to be found in
  the circuit itself (`discrete/NOTEBOOK.md`, D8).
- **Spinning faster doesn't see more.** The learning circuit scans by firing one thruster 54 times a second, which
  spins it nearly three turns a second. Each firing moves it along the same small circle whatever the rate, so it
  keeps re-sweeping the same view, and blocks flash past too fast for the eyes to fire. It sights food no more often
  than a policy scanning at 16 a second, so a quarter of its firings buy nothing. The circuit learns and approaches as
  well as the best policy; it loses on spending (`discrete/NOTEBOOK.md`, D10).
- **Design in a fast model of the circuit's blocks; use SPICE to check it's real.** A circuit lived in SPICE with
  real chip transistors takes minutes a life. Instead each block of the circuit (a timer, the oscillator, the
  learning node) is measured once on SPICE's bench and copied into a simple model as a few numbers, which lives a
  whole life in about a second, some 300 times faster. Its best design, built in transistors and lived in SPICE
  without retuning, did the job, at 80% of the score the model predicted; the gap was one timing quirk where two blocks
  meet (a thruster firing alone as a drive began), which no single block's bench showed. Close enough: ideas are
  tried, searched and judged in the model, and SPICE checks that a design is physically realisable, retuning it only
  when realism matters (`discrete/NOTEBOOK.md`, D12, D13).
- **Give every simulated life its own flaws, or an optimiser will find a knife-edge.** In the model every copy of a
  circuit was first identical. A search then set the learning threshold a hair below the most the learning node can
  ever reach: perfect in the model, but in real silicon each chip's parts differ a little, and in a quarter of the
  lives the bit could never flip. Now each life draws its own parts' errors (their spread measured in SPICE), and
  that design lost half its score while a sounder one lost nothing (`discrete/NOTEBOOK.md`, D13).
- **The same brain built of neuron-like elements costs 8 times the power of logic gates.** One design (B) was built
  three ways: as abstract blocks (timers, an oscillator, a tally), as Sepulchre's neuron-like elements (leaky nodes
  with fast positive and slow negative feedback), and as logic gates. Both lower levels did what the blocks
  predicted, so designing with blocks loses little and is fastest. But the neuron-like version needed 841 parts and
  31 nW against the gates' 151 and 3.7 nW: each element is an amplifier drawing current all the time, and its slow
  analogue signals are easily disturbed by noise, where gates swing rail to rail. What the elements offer instead is
  knobs a brain could turn to tune itself (`discrete/NOTEBOOK.md`, D14).
- **Within a life, the best tuning is small careful steps; the big search is evolution's.** A brain born with its
  spending settings (how long to chase, when to give up and explore) up to 3 times wrong can nudge each setting and
  keep the nudges that bring more meals per unit of energy, with no coordinator (each setting wiggling at its own
  moments and noticing whether things then went better than usual), and it recovers a third of what was lost in a
  long life. Hoping to find the best possible, we gave an idealised learner the same information (only its meals, what it
  saw and its own effort) and unlimited computing power to explore cleverly. It did no better, and worse where the
  settings matter little: meals come too rarely to tell good settings from bad ones far apart, so it kept exploring
  and paying for it. Exploring wildly early in life (annealing) hurt the simple tuner too. Finding good designs from
  scratch is for a search across many lives (evolution, or this project's searches); a life can only polish what it
  was born with, or rescue itself when something is badly wrong, like a lopsided body. So each problem has its
  solver (the user, 2026-10-30): what is the same in every life (how often meals come, how fast the body turns) is
  best set by evolution or design; what differs between lives but shows clearly in experience (which colour is
  food, a lopsided body) is best learned in the life; and what differs but barely shows (spending near its best) is
  best made not to matter: a design whose best is broad, as B's turned out to be (`discrete/NOTEBOOK.md`, D15).
- **A brain can grow a new reflex in its life, when something hurts that no sense predicts but an action can stop.** In
  an *arena* of robots that eat each other by biting tails, being bitten hurts (a bad taste), and the biter is behind,
  out of sight, so no sense can warn of it (the user's insight). Beside a brain evolution would build (one that steers
  towards tails), a generic *grower*, told nothing of what it is for, notices bad tastes no sense predicted, grows one
  new link from taste to the motors, and tries the simplest responses (fire one motor, the other, both, nothing),
  judging each by the taste of the moment after it. It found a turn, which breaks a bite at once, in 97% of lives, and
  gained three quarters of what the best designed reflex gains, judged on fresh arenas. Two things made it work: judging
  every bite rather than whole trials (lives are short), and a predictor that compares what follows a sense with what
  comes anyway. The obvious answer, speeding away, was worse than nothing: the biter just follows. Nor does it need a
  menu holding the answer: a recruit of two knobs (how hard to fire each motor when bitten), jittered at each bite and
  nudged towards whatever jitter tasted better, reached 86 to 97% of the best designed reflex, depending on where it
  started. (Those figures left out what firing costs. Since 2026-10-31 the robots are discs and firing is charged.
  Escape still grows and nets about as much as the best designed burst against the old tracker, and its control, pain
  no action can stop, now costs; but against a tracker whose fixed habits are tuned for the arena (evolution's part)
  it barely pays, +0.03 meals a 10 s: most of its value was the baseline's waste. A growth case must be judged against
  a well-tuned baseline: `discrete/NOTEBOOK.md`, D18.)
- **Learning which colour is food is a running tally of evidence, and in an unchanging world it shouldn't forget.**
  The learning node ("doubt") adds a step for each poison and takes one away for each food, and flips the creature's
  guess when the tally passes a threshold. Read as probability, each taste adds its evidence (the logarithm of how
  much likelier it is if the guess is wrong than if it's right), and the threshold is a decision. Since which colour
  is food never changes within a life, the tally should keep the trust that meals have built rather than leak it
  away: the version that keeps it was surely best, needed no time constant at all, and costs only 0.15 against being
  told the answer from birth (`discrete/NOTEBOOK.md`, D13).
- **A lopsided body defeats every fixed brain.** With each thruster drawn between half and twice its usual strength,
  every design, from either line, fell from about 2.2 to below 0.8 and stranded up to a quarter of its lives: a drive
  meant to go straight circles past its food. Told its body, the same brain recovers nearly everything by balancing its
  two thrusters, one number; but eight local rules for finding that number fell far short, because both eyes look down
  one corridor and nothing in it shows which way the creature curves (`discrete/NOTEBOOK.md`, D13;
  `minimal/NOTEBOOK.md`, M16). What does work, partly, is judging every drive rather than every meal: jitter the balance
  a little at each drive, and keep moving it the way the drives that kept their block in view longer went. That closes
  over a third of the gap in a short life, surely better than learning from meals (`discrete/NOTEBOOK.md`, D19). Far
  better still is learning a model of the body by prediction: turning with one thruster alone, the creature sees the
  same things come round again once a revolution, and how long a revolution takes says how strong that thruster is. With
  a few minutes of such sweeps, deliberate experiments of its own, it finds its body almost exactly and closes some 90%
  of the gap, surely beating every learner judged by outcomes. Sweeping only when it is eating badly costs an ordinary
  body nothing: it never sweeps, and once a lopsided body's drive is fixed the meals rise and the sweeps stop of
  themselves (`discrete/NOTEBOOK.md`, D20).
- **Behind these eyes, intelligence is worth about twice today's brains; the rest is what the eyes can't see.** A
  brain told every block's place does ten times better than our best. One told only the places of blocks its eyes
  have already seen, and remembering them, does twice as well: that is the most memory and reasoning can buy here.
  The rest is coverage: an eye sees a corridor 2 mm wide, so most blocks are never seen (`discrete/NOTEBOOK.md`, D13).
  And most of that doubling is information the eyes don't deliver: a block anywhere across the corridor gives nearly
  the same pulses, but the mouth eats only within 1 mm of it. Told places only as well as the pulses tell them, the
  remembering brain is barely better than B. The headroom is in sensing where across the corridor a block is, by
  moving, not in remembering (`discrete/NOTEBOOK.md`, D21). With these eyes even moving doesn't get it: wiggling to
  probe makes the side only a little readable, and no wiggling policy used it, so B is already near what this body
  allows for finding food (D22). An eye split into left and right halves would give the side directly: with it, B
  plus a small steering reflex, its wiring learned from its own scan, finds 21% more food, held out (D24, prepared
  for the user's decision; the body is unchanged).
- **What a brain counts as evidence can matter more than how much it remembers.** B, our best forager, kept a running
  tally of poisons to work out which colour is food, and lost about a tenth of its score to being told the answer. It
  raised false alarms and was slow to notice real ones, because it also counted poison merely bumped into while scanning:
  a poison tasted while driving at what it thinks is food says nearly everything, one tasted otherwise says little. Remembering more didn't help. Counting a taste only
  while driving, one small change using a signal B already had, closes the whole gap: the creature finds the colour in a
  second or two, and scores as if told. Measuring the information first is what showed the room was there: its senses
  carry about 3 bits a second about a one-bit question, far more than B was using (`STORIES.md`, 1).
- **One warning signal, and its context says which cure.** Tasting poison while driving at what it thinks is food tells a brain something is wrong, but not what. Given harder worlds (colours that
  must alternate, a pattern, colours that swap), we found small cures for each, such as a counter that every good taste advances, holding a few bits of what to follow next. Applied to the wrong world a cure hurts.
  But how many good meals came before the poison tells a sequence from a swap: one brain reading that picks the right cure itself, surely better than its starting point in five of eight tests, and doing no harm on plain
  (`STORIES.md`).
- **Time is where a small brain computes** (the user's insight, 2026-11-01). Deep networks come from a world without
  time: a mapping from input to output. A small creature's brain is a dynamical system whose computation is its
  timing (oscillators, delays, phase, coincidences), with the loop through its body and the world doing half the
  work. Where a block lies across the eyes' corridor isn't in how many pulses arrive but in when, against the
  creature's own movement: a rat reads where a whisker touched from the phase of its whisk, and B's scan already
  whisks. So the bounds should be reckoned on timing, not counts; credit by meals, slow and averaged, can't judge a
  trick that is right within one sweep; and a tiny circuit with Sepulchre's feedback motifs, evolved in the loop,
  may find sideways sensing for itself, as a dozen neurons evolved to scan and tell shapes apart in Beer's agents
  (`BOUNDS.md`, Time).
- **Check the simulator, not just the circuit.** A circuit simulator chooses its own time steps, within error limits.
  With ngspice's default limits, a transistor sitting right at its switch-on point turned on or not depending on
  where the steps happened to land, so results seemed to change with the step size. With the limits tightened,
  every step size agrees. Check that results converge in both step and error tolerance, on the first design that
  works, and distrust any design whose behaviour hangs on a knife-edge (`discrete/NOTEBOOK.md`, D7).
- **Real units show what abstract ones hide.** Written in seconds, amperes and farads, the circuits turned out to
  have a chip's sizes but biology's noise, a contradiction invisible while the units were abstract. Real units also
  give quick sanity checks (a chip can't make a resistance above about 100 GOhm) and a meaning to every number
  (`NOTEBOOK.md`, Lessons; `units.py`).
- **Count the cost as built.** The simulator first counted a circuit's power as the currents reaching its nodes. Built
  in real transistors, the same circuit drew 150 times as much, because every amplifier's bias and every mirrored copy
  of a current also flows from the supply. An optimiser told the wrong price buys the wrong things, so the price now
  comes from the transistor build, checked against SPICE (`minimal/NOTEBOOK.md`, M15).
- **Compare designs on the same lives, with an interval on the difference.** Lives vary a lot by luck. Two designs are
  compared on the same worlds (the same seeds), and one counts as better only if the 95% interval of their
  difference excludes zero; otherwise they are tied, and no order is claimed (`experiments/NOTEBOOK.md`, E0;
  `minimal/NOTEBOOK.md`, M9).

- **Most mismatches between a brain and its world have a small cure, but one that stays out of the way is harder.** We
  gave the same small learning brain ten different problems, such as unequal thrusters, a noisy eye and food that must be
  eaten in sequence. All have a cure by hand that is surely better, one of them tiny, and judging evidence better was the
  commonest. Eight have an automatic version that helps and costs nothing we can measure when the problem is absent. The trick
  was mostly stopping false alarms from feeding themselves: for instance, acting only once a shortage has lasted two checks running.
  The automatic versions pay in the time they take to notice (`STORIES.md`, the table).
- **Several ideas about the world can be tested at once, without acting on any of them, but not everything can be tested that way.**
  We looked for one circuit that cures all ten problems. Stacking each problem's cure with its own alarm went poorly, because the
  alarms read one another's problems. Trying changes at random and keeping what helped failed too: there is too little signal in a
  life, and it does harm when nothing is wrong. What worked was noticing that once a taste is trusted, it reveals which colour was food,
  whatever the creature was doing at the time. So it can keep several rival ideas of what taste means (it never changes, it changes
  often, it alternates, it repeats in threes), score them all on every taste, and follow whichever predicts best. In a world with nothing
  wrong, no rival ever gets ahead, so nothing changes. One setting of this circuit helps surely in 8 of the 10 problems and in 13 of 14
  combinations it was never tuned on. It is still partly a failure: it is worse than three problems' own cures, it can only choose among
  ideas it already holds, and it can't judge the eyes or the thrusters, since no taste says how to reach a block. Those need other
  evidence, so the honest answer is three loops rather than one (`STORIES.md`, One universal circuit; `discrete/NOTEBOOK.md`, D29).
- **In a clean world the limit is what the brain can imagine, not how much evidence it gets.** We counted what a life can teach. A taste that
  never lies carries nearly a bit, so at our circuit's pace a life offers about 50 bits, and it only needs about one to learn which colour is food. If one taste
  in five lies, the offer falls to about 15, though a creature that eats faster can buy several times more, at the cost of eating more poison. Compared with an ideal
  judge of the same ideas, our circuit is close to right on when to change its mind if rules can change, and we can improve on it, but the largest gaps aren't in
  judging at all. They come from worlds none of its ideas describes. Food that swaps every 10 s is the clearest: a learner told only that swaps happen barely helps,
  while one choosing among hundreds of possible timings, about 14 bits of ideas, closes half the gap. Knowing *when* is what's missing (`discrete/NOTEBOOK.md`, D31, D32).
- **On worlds we didn't choose, the bank covers what its ideas describe, and no more.** To judge whether the bank is
  general rather than tuned to the problems we built it for, a program drew worlds at random from our grammar of
  challenges, fixed before we saw any. Only about a third have anything to learn. Of those, the bank surely copes with
  about a fifth and surely fails two fifths; the rest are too close to call. Where an ideal judge holding
  thousands of ideas succeeds, the bank nearly always does too, and where the bank fails, mostly so does that judge:
  the failures are missing ideas, chiefly about timing (colours that swap at some period, a meal soon after the last
  being bad) and place. A ten times longer life rescues a few of the meal-timing worlds and none of the swaps,
  though in a life that long the ideal judge, which holds ideas about timing, does learn several swaps. One
  part did harm: the eye filter, tuned for the eyes' usual pulse rate, costs a lot when the eyes are more sensitive. So
  the bank's principle (rival predictors judged on every taste) works, but its repertoire is ours, which is why the
  next step is rivals the brain makes itself (`discrete/NOTEBOOK.md`, D35).
- **Trying things out has a price, and in a short life the brain may not be able to see it.** To learn how to balance
  a lopsided body, a part of the brain wobbles its balance a little on each drive and keeps what goes better. We gave
  it rules of its own: a bigger step while its moves agree, a smaller one when they reverse, and a quieter wobble once
  the wobble hurts whichever way it goes (the sign of standing on a peak). In long lives this works well, and it
  rescued much of what long lives had seemed to lose. But on a body whose thrusters are exactly equal, even a tiny
  wobble costs a tenth of the food, and spotting that cost from the drives themselves takes about fifteen times more
  drives than a short life has. The older design was safe in short lives only because it never wobbled while it was
  eating well. When to explore at all is still open (`discrete/NOTEBOOK.md`, D36).
- **Adaptability costs** (the user's insight, 2026-11-09). We keep what is built before a life (evolution, or our
  design) apart from what is learned in it, but the two can't be fully separated: whatever is built in fits some
  range of worlds. And there is a second-order effect: a brain built to cope with very varied worlds must spend
  something (trials, wobbles, evidence) finding out which world it is in, so on a short, easy trial it does worse than
  a brain built for exactly that world, which needs to find out nothing. The balance learner shows it: in long lives
  its exploring pays, but on a body with equal thrusters, in a 100 s life, it costs a fifth to a half of the food,
  where a brain that assumes equal thrusters loses nothing (`discrete/NOTEBOOK.md`, D36). So how well a brain should
  adapt depends on how varied its worlds are and how long it has to live in them.

## The ground rules, for every brain

Every brain keeps the same ground rules, set out in `AGENTS.md`: the body talks to the brain only through two
sensors, two motors and one taste that never says which sensor it is about, and never does the brain's work (credit
assignment, timing, filtering); nor does the simulator, so there is no clock or lockstep, noise is everywhere, and a
result must hold at a finer step and on fresh lives; everything is local, with no god; and in a circuit brain
everything is explicit circuit, with noise modelled on biology's built into the simulator (Terms).

## The creature and its world

A disc whose front point is the mouth, with eyes looking ahead (one sensor for each colour) and a forward thruster on
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

Built from the one element of Ribar and Sepulchre's [Neuromorphic Control](https://arxiv.org/abs/2011.04441)
(`mixed_feedback.py`; the approach and its literature in `MIXED_FEEDBACK.md`): leaky nodes, and elements that each put
a current into a node, a sigmoid of a filtered voltage, with a sign (positive or negative feedback) and a timescale,
perhaps gated by another node. Level 0 is nodes and elements; level 1, the motifs built from them (neurons, synapses,
the states they hold), as the block view draws them. A memory node (a knob) holds its value, noisy only when written.
Every circuit brain shares two sensor neurons, two motor neurons and a taste node (`brains/circuit.py`), is integrated
in steps of 0.125 ms (80 to each 10 ms tick of the world), and has noise and mismatch as a substrate makes them
(Terms). Each eye fires at random moments, at a rate set by what it sees, and each pulse (a taste too) starts at a
moment of its own within the tick. Compiled with numba, with the world, a life of 100 s takes about a second.

**Under biological noise every hand-built circuit brain falls to about 1 food for each poison** (2026-10-20): 10%
mismatch pushes a share of their excitable neurons into firing on their own or missing pulses, and none was built to
survive it (`NOTEBOOK.md`, Noise as biology makes it). The results in this section were measured with the earlier
noise (a fixed noise per node, no mismatch), and stand only for it until these brains are rebuilt on a neuron that
survives mismatch.

### The designed circuit, for comparison

Designed by hand rather than grown (`python creature.py --brain designed-circuit`; its schematic: `s` in the live view,
or `media/designed_circuit.png`), it says what growing costs. Four excitable neurons, alike: two sensors and two motors.
Each sensor excites the motor on its side (a coin toss at birth) through a synapse that relays every spike, and the
other through a plastic synapse whose strength p sets: at p = 1 it relays nearly every spike, at 0 none, in between
noise decides. The sensors hush each other: a sensor's spikes charge a node that for about 0.1 s holds the other
sensor down, so the creature heeds one colour at a time. Its spikes come often and each kick is small. Learning is three
factors, all in the circuit: each sensor's spikes charge its eligibility node, which leaks away over 0.1 s, and empty
the other sensor's (cross-inhibition, so only the sensor that fired last is eligible); one taste node, driven by the
same taste input, charges or empties a capacitor holding p while taste is good or bad, as fast as eligibility allows. p
sets the plastic synapse's strength. Noise on every node makes the odd spontaneous spike, so a creature that sees
nothing still moves.

Under the earlier noise, on the same 32 lives as the sheet brain (nca-learn; `--measure 32`), it learned in 28
(median 36 s) and ate 2.2, 5.9 and 4.6 food for each poison by thirds of life, netting about twice the sheet brain's
food: it moves from the first tick (the sheet spends about 6 s building itself), reacts at once where a pulse takes
about 0.13 s to cross the sheet, and its sensors hush each other. So building costs time, and a big brain is slow.

### Recruitment: growing in the life

The recruitment series (the ideas and plan in `RECRUITMENT.md`; the experiments in `experiments/NOTEBOOK.md`) climbs a
ladder from a brain that can't learn at all, each step measured against the one below:

| brain | what it is |
|---|---|
| baseline circuit (`brains/baseline.py`) | the designed circuit's four neurons alone, each sensor driving both motors, taste going nowhere: drives at every block (the baseline) |
| adjusting circuit (`brains/adjusting.py`) | rung 0: each neuron adjusts its own excitability from taste (a knob); cuts poison by a third, by ignoring rather than avoiding |
| knowing circuit (`brains/knowing.py`) | the starting animal: the baseline circuit plus a taste neuron, T, that learns what predicts pain but has no outputs; it knows, but behaves exactly as the baseline circuit |
| recruiting circuit (`brains/recruiting.py`) | rung 1, guided: T's frustration grows a *bridge* on the poison sensor's pathway that lets the knowledge act |
| healing circuit (`brains/healing.py`) | rung 1 by a generic recruit that knows nothing of the circuit, choosing among actions on what it is attached to |
| healing cascade (the same file) | the first recruit can't reach the cure; frustrated itself, it grows a second, one step further out, which can |

Under the earlier noise (`experiments/LEADERBOARD.md`), a recruit that knows nothing of what the circuit does matched
the guided bridge, and settled better: it found the bridge's function ("gate the poison eye's synapse to a motor") out
of its menu in every life. The cascade found the cure one step further out in about 60% of lives, and nothing grew in
all-food lives.

## The minimal circuit search

How simple can a circuit be that learns the bit, and how well can a circuit drive the body? No neurons, locality or
growth are required: a circuit is any nodes and elements of `mixed_feedback.py`, written as a plain description (a
spec, `minimal/spec.py`), its parts counted as it is built in transistors on a 1.8 V supply (`chip.py`; SPICE checks
the build, `minimal/spice.py`). The task, body, interface and noise
are every brain's, and the rules against cheating the simulator are enforced in code (`AGENTS.md`). Circuits are
designed by hand, tuned (a polish, `minimal/search.py`), pruned part by part (`minimal/prune.py`) and searched by
evolution over topologies (`minimal/evolve.py`), all judged on fresh seeds with the noise of silicon, biology and
twice biology's (Terms: substrate).

What counts, among the circuits that do the job (learn the bit, eat enough, rarely strand): performance first (the
best driver for energy, body efficiency, and the best for speed and accuracy, gain rate, never traded against each
other), then power and area; the simplest brain behind them (Terms: what counts). The league (`minimal/LEAGUE.md`,
generated) names the best at each and how sure that is; the notebook (`minimal/NOTEBOOK.md`) tells how they were
found.

What it has found so far:

- **Built in transistors, a circuit costs what its supply delivers, 150 times what reached its nodes.** Lived closed
  loop in SPICE as SKY130 transistors, HR_31p_pol behaved as in the simulator, but its +-3 V supply delivered 1.76 uW,
  where the simulator had counted 12 nW: thinking cost more than moving. Now the simulator reckons the build's power
  (`chip.py`: element by element within 1% of SPICE, and a closed-loop life at 1.8 V 131 nW in SPICE against 130 in
  the simulator, behaviour tied) on SKY130's own 1.8 V supply, the memory is a SONOS cell that
  holds its bit (a capacitor written by transistors leaked it away in seconds), and parts are counted in transistors
  (`minimal/NOTEBOOK.md`, M15).
- **The simplest circuit that does the job, robustly, had 30 parts (counted as elements, before M15), and it is also among the best drivers.** Judged at
  one noise level, circuits of about 22 parts seemed to do it: the bit a perfect integrator (a floating gate) written
  by a three-factor rule (what was seen, times the taste), the creature spinning until food is in view. But their
  rhythm came from noise: in silicon, about 280 times quieter, they never get moving. Only the hold-and-roam circuit,
  whose scan is an oscillator and whose roam is a timer, does the job in silicon, biology and at twice biology's noise
  (35 parts: HR_si); open searches from it, within a chip's limits, took parts of its motor stage away and retuned the
  rest, and a polish and pruning one more: HR_31p_pol_pruned (30 parts, `media/HR_31p_pol_pruned.svg`, its
  signal-flow graph and schematic), with HR_31p_pol (31) the best driver yet (`minimal/NOTEBOOK.md`, M12-M14).

## Discrete circuits

Before getting clever about food and poison, what is the simplest circuit of common parts (2N3904 and 2N3906
transistors, resistors, capacitors, low-leakage diodes) that drives the body to food, and then the simplest that also
learns the bit? Each circuit is a netlist living closed loop in ngspice beside the body (`discrete/life.py`), each
seed with its own parts' tolerances, judged as the minimal search judges (`discrete/judge.py`, `discrete/poison.py`).
The notebook (`discrete/NOTEBOOK.md`) tells how they were found.

- **All food, 14 parts**: hold and drive (`media/hold_drive_14.svg`): an oscillator of a PNP and an NPN scans with
  one thruster; each pulse from an eye charges a hold capacitor through an emitter follower, and while it is charged
  the second thruster fires too, straight at the block. Efficiency 6.9, 72 nW. Fewer parts cost: 12 parts 6.6, 10
  parts (counter-turning, no hold) 4.3.
- **Blind, 9 parts**: an oscillator firing both thrusters 300 times a second eats four times as fast, as efficiently,
  but only because the simulated thrusters are identical (What we've learned).
- **A circuit doesn't need to tune itself to its body**, as far as tried: across bodies built differently (strength,
  eyes, drag, unequal thrusters) the best settings hardly move, except for unequal thrusters, and a trim for those
  can't be learned from a life's 200 meals more cheaply than it costs. Driving only while the eyes still see the
  block copes with them instead.
- **One bit, 46 parts** (`learn_avoid`, `media/learn_avoid.svg`): the eyes gated by a latch that two poisons in
  quick succession flip; once the eye it follows has seen nothing for a few seconds, both thrusters drive straight
  until the next sighting (giving up on an empty patch); and the eye it silences empties the hold, so poison ahead
  turns the creature aside. Held out (160 lives) it surely does the job: efficiency 1.78, gain 4.7 meals per 10 s,
  food:poison 4.7 in the last third, none stranded, 130 nW. Pruning took it from 48 parts and made it surely better
  on both measures. Its predecessor (`learn_hold`, 49 parts, a roam on a clock) stranded 3 lives in 64 and was
  surely less efficient (1.17). The same rules as policies, told the answer from birth, reach 2.7, and 2.3
  learning: the ceiling for this kind of brain on this body.

## Next

The current programme, its stages and decisions, is in [`PROGRAMME.md`](PROGRAMME.md); the open questions, most
valuable first, in [`QUESTIONS.md`](QUESTIONS.md).

## Terms

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
  food (`oracle`), a policy gives the ceiling for its kind of brain on this body. A rule's own values don't transfer to a
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
- **Off-policy scoring**: judging a model on what happened while something else was in charge, so it can be judged without being
  tried. **On-policy** is the opposite: a change is judged only by acting on it, as jitter is.
- **World** (in the programme): a rule changing the creature's world, written in a small language (`lab/stage2_lang/`),
  for instance "the colours swap every 12 s" or "a meal soon after the last is bad". The language can't touch the
  brain or break the interface. A **generator** draws worlds at random from it, frozen before any draw.
- **Arm**: one brain run on the same lives as the others, so they compare fairly. **Base**: the existing circuit;
  **bank**: base with the bank of predictors; **told**: the bank's own parts told the right colour at every moment, a
  yardstick, not a brain; **reference**: a frozen ideal learner holding 12,591 ideas, the bar's other half.
- **Gap**: how much better the told arm does than base (or than standing still, if base is below that). A world has
  **something to learn** if its gap is at least .1 and surely above 0. **x**: the share of the gap the bank closes;
  **r**: the same for the reference. A world **passes** if x is above a quarter and above half of r (`PROGRAMME.md`).
- **Coverage**: the share of worlds with something to learn that the bank passes. With uncertain worlds it is a range:
  sure passes at the low end, sure passes plus those too close to call at the high end.
- **Doing no harm**: in a world with nothing to learn, the bank is never surely more than .1 below base.
- **Pair**: two lives on one seed, red then blue as poison, so a brain that ignores taste scores 0 on average; intervals
  are taken over pairs.
- **Sampler**: a program that draws random worlds from a grammar with chosen probabilities, and so decides what "most worlds" means (`GRAMMAR.md`).
- **F_novel**: on challenges a circuit's design never saw, its pass rate above the base circuit's, as a share of what the base circuit leaves. The design is fixed; the circuit still learns in each life (`PROGRAMME.md`).
- **Description length**: how many bits it takes to write a thing down in its most compact form, so that repeated motifs cost little (`PROGRAMME.md`).
- **Occam factor** (MacKay): the extra evidence a choice among more models needs, about log2 of their number, which is why a bigger bank picks more slowly and falsely more often.
- **Bits per taste**: how much one taste can tell a brain, 1 - H(e) for a taste that misleads with chance e: 0.83 at 2.5%, 0.25 at 21%. A life's bits are that times its tastes: a ceiling on the evidence, not what was learned.
- **Run detector** (Page's CUSUM): a score that rises on wins, falls on losses and stops at a floor of zero, so it reacts to a recent run and forgets what came before. It is the standard test for a change at an unknown time. The bank's entry rule is one, and its picks resemble those of an exact posterior that expects frequent change.
- **Function-preserving growth**: adding a part with its effect at zero, so the brain is exactly as good as before,
  then tuning it in: trying a part costs nothing (`PARTS.md`).
- **Ideal observer** (Geisler's term, the user's choice, 2026-11-01): a brain of unlimited reasoning but only the
  senses, beats and tastes a real one has; not omniscient. What it could do bounds what any brain could learn
  (`BOUNDS.md`).

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
| `PROGRAMME.md` | the current programme: its question, stages, gates and decisions |
| `ABSTRACT.md` | the programme so far, in one page |
| `GRAMMAR.md` | the grammar of challenges the worlds are drawn from, and how they are judged |
| `QUESTIONS.md` | the open questions, most valuable first: parked mid-quest, removed when answered |
| `NOTEBOOK.md` | the lab notebook of the body and the circuit simulator: what was tried, what failed and why |
| `MIXED_FEEDBACK.md` | the mixed-feedback approach (Sepulchre and colleagues): what is new in it, the literature, and what it suggests here |
| `RECRUITMENT.md` | how a brain might recruit more computational power locally, with no god: the literature, insights and plan |
| `BOUNDS.md` | what limits how well and how fast any brain could learn in a life: the ideal observer, watching against intervening, the walls, MacKay |
| `STORIES.md` | one page per performance issue: the gap, the interventions tried, how a brain could detect it, the simplest circuit that does |
| `PARTS.md` | the ways a working brain could change itself (tune, modulate, rewire, prune, duplicate, add), a catalogue of parts by what they do in time, what triggers each change and what signal judges it; towards a universal circuit |

## Licence

MIT: see `LICENSE`.
