# Agent notes

The rules, for agents and people alike: how to work here, and the constraints every brain keeps. The quest, the big
picture and what has been learned are in the README; the history behind each rule is in the notebooks. Each fact in
this repository lives in one place (below); other files link to it.

This project was split on 2026-11-02 from [nca-learn](https://github.com/pilgrimbeart/nca-learn) (`../nca-learn`),
which keeps the sheet brain: a sheet of identical cells that grows its own nervous system by local rules. The lessons
common to both are copied here (`NOTEBOOK.md`, Lessons); the sheet's own history (what averages can honestly carry,
the cheats a grid invites) is in nca-learn's `NOTEBOOK.md`, worth reading before a circuit grows units by local rules.

## Working

- **Push only when the user says "Push".** Work directly on `main`. On "Push": commit in the foreground, then in one
  background task run the three checks (`python test_compiled.py`, `python -m minimal.test_minimal`,
  `python -m discrete.test_model`) in a fresh venv built from `requirements.txt` alone, on a
  clean checkout of that commit (a temporary `git worktree`), and push only if they pass. Say nothing if all pass;
  report a failure with its log. (A fresh venv because another may hide a missing dependency. No GitHub CI.)
- **Rip up and rewrite**: prefer a cleaner, smaller design to incremental edits that keep legacy structure.
- **Real units, from few axioms** (the user's decision): every quantity in SI, every number that can be derived
  derived from the axioms in `units.py`; a design's own choices stay with the design, in SI. Rates are per 10 s, a
  life lasts 100 s, or 1000 s in a test that says so (the user, 2026-11-06: some evidence is too scarce for 100 s).
- **Each fact in one place**; link, don't copy:

  | what | where |
  |---|---|
  | the rules | this file |
  | the quest, what has been learned (each finding explained for a newcomer), an overview of each line of work, how to run things, the terms | `README.md` (define a new term in its Terms when it first appears in a user-facing document) |
  | each line of work's current state ("Where it stands", rewritten as it changes), then its dated history, methods, results and dead ends | the body and the circuit simulator: `NOTEBOOK.md`; recruitment: `experiments/NOTEBOOK.md`; the minimal search: `minimal/NOTEBOOK.md`; discrete circuits: `discrete/NOTEBOOK.md` |
  | the axioms: physical constants, scales, units | `units.py` |
  | the noise model | `mixed_feedback.py`'s docstring |
  | how each part is built in transistors, and so its parts and power | `chip.py` (written out for SPICE by `minimal/spice.py`) |
  | rankings | `experiments/LEADERBOARD.md`, `minimal/LEAGUE.md` (generated) |
  | the lab: one-off experiment scripts and their logs, cited by the notebooks (paths absolute to this machine) | `lab/`, `lab/v/` |
  | the interventions phase's results, one page per performance issue | `STORIES.md` |
  | background reading | `MIXED_FEEDBACK.md`, `RECRUITMENT.md`, `BOUNDS.md`, `PARTS.md` |
  | the current programme: its question, stages, how we work, decisions; check work against it before starting | `PROGRAMME.md` |
  | the grammar of challenges and the experiment's detail | `GRAMMAR.md` |
  | open questions, most valuable first | `QUESTIONS.md` |

- **One-off scripts go in `lab/`**, never only in a session's /tmp scratchpad: a notebook may cite only what the
  repository keeps. Logs and small results in `lab/v/`; large ones (pickles, frames) stay out of git, noted where
  they are.
- **Open questions** (the user's idea, 2026-10-28): a question that occurs mid-quest is parked in `QUESTIONS.md`
  rather than chased; one answered leaves it, its answer in its line's notebook. With nothing else to do (the user
  away), take the most valuable one.
- **Where findings go.** Record every finding and dead end in its line's notebook as you go. When one changes the
  direction of the work, add it to the README's "What we've learned": a short heading, then what it means in plain
  terms a newcomer understands, with a link to the notebook. Keep each notebook's "Where it stands" current.
- **Measure, and trace each failure to a cause before fixing it.** **Show a working behaviour live**
  (`python creature.py`, `python -m discrete.watch`) before reporting it.
- **Measure in bits** (the user, 2026-11-04, David MacKay's rigour): for any claim about learning or adapting, say how many bits are needed, how many the wires supply and how many were used, against an ideal Bayesian learner with the same evidence. Stay sceptical: a result a design could achieve by building in its test's description proves nothing.
- **Mind the noise wall** (the user, 2026-11-01): for a learning experiment, estimate its signal to noise per second
  against the life's length, and its explorers per credit window, before reading a result; a negative result where
  learning was impossible (too little signal, or credit colliding as ALOHA's packets do) says nothing about the
  mechanism (`BOUNDS.md`, The walls).
- **The user is colour-blind**: use colour, never as the only cue (pair it with shape, line style or a label), and no
  hues hard to tell apart, such as red and green (Okabe-Ito).
- **The interventions phase** (the user's decisions, 2026-11-02; `PARTS.md`): no SPICE, physical plausibility taken as
  read. Each story (one performance issue X: baseline without X, the gap, manual interventions, detection, the simplest
  automated circuit) runs in the block model (`discrete/model.py`) through to a successful last stage, then is
  re-validated once in the node-and-element simulator (`mixed_feedback.py`). Only silicon's noise need be survived,
  not biology's. The rules below that call for SPICE or for every substrate don't apply to this phase's stories.
- **The interventions table** (the user's decisions, 2026-11-03; `STORIES.md`): the output is about 10 stories, each a row:
  the mismatch between body or world and the base brain; the best manual cure; how it kicks in automatically only when
  needed. Then look for one universal correction circuit. Each row applies one mismatch to story 1's finished circuit. Each
  row tries every class of `PARTS.md`, section 5, tuned, or records why a class can't apply; the row's cure is the simplest
  tied with the best. Its automatic version must tie with the base brain in the unmodified world. Re-validation in
  `mixed_feedback.py` waits until the table is complete, and then covers only the rows or universal circuit we keep.
- **Long runs** share one laptop: one job at a time. **One maths thread per worker**: set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` for anything with a process pool (8 threads per worker made one arm 50 times slower, 2026-11-05). Kill processes only by explicit PID, never by a pattern. To pause
  a run, stop (SIGSTOP) only its pool's workers, never a shell or a process the harness waits on. Don't change code a
  running job will import later.

## Ground rules for every brain

The point is a brain that learns in situ, so the brain must do the work.

- **The interface.** The body (`world.py`) and `Life` (`creature.py`) talk to a brain only through sensors 0 and 1,
  motors 0 and 1, and one taste (`stimulate`, `taste`, `step`). Taste is +1 (food) or -1 (poison) for a tick when a
  block touches the mouth, else 0, and never says which sensor it is about. The body draws its wiring (colour to
  sensor, thruster to motor) at random each life, so the brain doesn't know what its organs are for. Never change
  the task's ground rules (what an organ is, what connects to what) without asking the user first.
- **The body must never become part of the solution.** A change that lets the body or world do a job the brain could
  do (credit assignment, choosing which cells learn, timing, filtering) is not a simplification. Say plainly what job
  moves out of the brain before proposing it, and expect no. Ask before adding or changing any body-to-brain signal.
  If the brain stops needing a mechanism after a body change, ask where its work went (`NOTEBOOK.md`: reward at
  contact). Nor is any property of the body (a pulse's length, a thruster's strength) a reference the brain may tune
  itself against: the body should be as variable as the brain (the user, 2026-10-29); a brain tunes itself towards
  better outcomes, not to a setpoint the body supplies.
- **Nor may the simulator.** An optimiser, an agent included, finds anything a design can exploit. So: random timing
  (no lockstep, no inputs only on tick boundaries), noise on everything, nothing carried below the noise; a result
  must hold on fresh seeds and at a finer step (the fast model, the user's, 2026-11-06: work at the 10 ms tick, then
  halve the step until it stops changing; my refinements: until two successive halvings differ by under .05 within
  their 95% interval, on the reported comparisons, not only levels). **Everything in seconds, never in ticks** (the
  user, 2026-11-06): no delay, rate, window or event counted in ticks, in a body, world or brain. Keep the
  simulator's error control tight enough that the step doesn't matter (`discrete/NOTEBOOK.md`, D7); for an optimised
  circuit, limits on time constants and gains against the step.
- **Circuit noise is a substrate's, and the simulator's alone** (the user's decisions): shot noise, resting noise,
  mismatch and pulses at random moments, for biology or silicon, as `mixed_feedback.py`'s docstring specifies, each
  derived from `units.py`. It lives in the one integration step every simulation calls (`_step`) and in how the
  arrays are built, with no switch to turn it off (`mixed_feedback.SUBSTRATES`). Never add a way round it, and keep
  `test_compiled.py` checking that it is the same at any step and can't be dodged.
- **Local only, no god.** A unit knows only its own state and its neighbours' signals. It may draw from its own noise,
  but a choice among units comes from their local competition, never from outside. No unit knows it is optimally
  tuned: "finished" means its own adjustment has stalled while its own discomfort persists.
- **No magic knowledge, no hidden size** (learned on the sheet brain, nca-learn): a grown unit finds its target by a
  signal the target sends out, never by where it should be; and no fixed wait, cap or threshold is tuned to one size
  of brain: stages hand over when their work is done.
- **Comparisons are fair.** Brains are compared on the same lives (the same worlds and wirings); a refactor of one
  brain leaves the others' lives unchanged. All-food lives (both colours food) are the control for anything that
  should happen only when there is something to learn.

## The circuit brains (README: The circuit brains)

- **Everything that affects behaviour is explicit circuit** (`mixed_feedback.py`'s nodes and elements), so it can be
  drawn as a schematic: for every number that affects behaviour, say which node holds it and which elements move it.
  The one exception (the user's decision) is growth: a recruit appears by a declared primitive, triggered by a node's
  own voltage, attached locally. Watching may compute anything, but never feeds back.
- A knob is a memory node, noisy only when written.
- No knowledge of what a sensor senses or a motor does; continuous time; learning only through the taste.
- `schematic.py` draws the designed circuit: redraw it when the circuit changes.

## The minimal circuit search (README; `minimal/NOTEBOOK.md`)

How simple can a circuit be that learns the bit, and how well can a circuit drive the body, with no architectural
constraints? Every rule here is enforced by `minimal/spec.py`'s `check` and tested by `minimal/test_minimal.py`: add a
rule to both whenever one is added here.

- **On a chip's supply** (the user's decisions): 1.8 V (`units.SUPPLY`), every node within its rails (`units.RAIL`,
  outputs fading near them: `chip.KNEE_P`, `KNEE_N`); a clamp inside them is a part. Designs are drawn at the typical
  voltage (`units.V_TYP`) and converted otherwise (`minimal/designs.py`'s `rescale`).
- **The body's pulses match the technology** (the user's decision): `brains.circuit.PULSES` typical currents of the
  brain's own technology.
- **A memory is non-volatile** (the user's decision): a SONOS cell written by tunnelling through a pulse driver that
  fires only above a threshold (`chip.DEAD`). Known anomaly, uncounted for now (the user's decision): writing needs
  10.5 V across the cell, from pumps or extra supplies that are neither simulated nor in the power.
- **Not faster than the step** (`units.py`): nothing moves a node more than half a typical voltage a step (gain / C,
  or the body's pulse / C); no leak faster than 0.25 ms; an unfiltered element on its own node no faster than 1.25 ms.
- **Buildable on a chip** (the user's decision; `units.py`'s chip limits): no resistance above about 77 GOhm, no
  capacitor above 50 pF, no leak or filter slower than about 3.9 s (slower is a memory node), no element current
  below 1 pA (`python -m minimal.physical`; `minimal.designs.on_chip` refits a leak too large).
- **Judged honestly**: on seeds the search never saw, with mismatch, with the noise of silicon, biology and twice
  biology's, the worst counting and the job required with each (the user's decisions). Lives are paired (red, then
  blue, as poison, on one seed), so a circuit that ignores taste scores below 0. A design must also hold in the real
  `creature.Life` at a finer step (`minimal/check.py`).
- **The job**: at least 1 food per 10 s, food:poison at least 3 in the last third of a 100 s life, at most 5% of lives
  stranded; the score charges shortfalls life by life and third by third (`spec.py`).
- **Moving and thinking cost, in meals** (the user's decision): a meal `spec.MEAL` (10 uJ), resting
  `spec.METABOLISM` (1 uW), a firing `spec.FIRING` (20 nJ), the circuit what its supply delivers. Guesses, to adjust.
- **Counted as built** (the user's decision): parts are the transistors, resistors, capacitors, diodes and bias
  sources of `chip.py`'s blocks in SKY130; power is what the supply delivers; SPICE checks both (`minimal/spice.py
  --check`, `minimal/spice_life.py`).
- **What counts, in order** (the user's, 2026-10-27): among circuits doing the job, performance (the best
  efficiency and the best gain rate, never traded against each other), then power, then area (what it takes to
  build); simplicity (fewest parts) behind them, to understand a design, since evolution pays for power and
  material, not elegance (README, Terms). `search.py` and `prune.py --by efficiency|gain` work for one.
- **Sure, or within noise**: every measure with its 95% interval (bootstrap over seeds, each seed's pair together;
  stranding a Wilson interval); designs compared paired, one above another only if the interval of the difference
  excludes 0; the job done surely only if every interval is within its limits.
- **Every polish ends with pruning** (`minimal/prune.py`).
- **Sepulchre's rules**, for an experiment that declares them (`rules: "mixed"`): every node leaky except memory nodes,
  no clamps; gates and floating gates allowed (the user's decision).
- **Starts matter**: a search only refines what its starts can reach; include designs of every kind that works.

## Discrete circuits (README; `discrete/NOTEBOOK.md`)

Circuits of parts, living closed loop in ngspice beside the body (`discrete/life.py`). The task, body, interface and
judging are every brain's.

- **Parts readily realisable in SKY130** (the user's decision, 2026-10-28): its 1.8 V core nMOS and pMOS
  (`Netlist(chip=True)`, `Netlist.M`), resistors, capacitors, diodes and bias sources, within the chip's limits
  (AGENTS.md, the minimal search: 1.8 V, no capacitor above 50 pF, no resistance above about 77 GOhm, no current below
  1 pA); each seed draws its own tolerances (`life.TOL`, `CHIP_TOL`: a transistor's width standing for its threshold's
  spread). Complementary designs for power, positive feedback for clean decisions. Parts counted one by one; power is
  what the supply delivers. (The circuits before were 2N3904 / 2N3906 bipolars on a 3 V coin cell, resistors 1 MOhm
  to 1 GOhm, capacitors 47 pF to 30 nF, `circuits.BOUNDS`: my choice, never the user's.)
- **No noise in SPICE**, by design (thermal noise is microvolts against swings of volts): the body's random pulses
  and each seed's tolerances are the variation. So a result must hold on held-out seeds (`judge.py`, from seed 50000)
  and at a finer step (`--finer`), with the error control tightened in every netlist (`life.ACCURACY`).
- **The interface** (on a chip, the user's confirmation, 2026-10-28; the rest my choices): on a chip, an eye's and the taste's pulse are the
  technology's (0.9 nA, as the chip brains', `life.CHIP_EYE`) and a motor input an on-chip gate (0.1 pF); in the
  bipolar circuits, an eye a photodiode giving 1 uA for each 2.5 ms pulse, clamped at the supply, and the taste a 1 uA
  pulse into a `taste` node, + for food, - for poison, clamped a diode drop beyond either rail; a motor a CMOS Schmitt
  input (fires rising through 2/3 of the supply, re-arms below 1/3); bodies built differently (`bodies.py`) only in
  experiments that say so.
- **The fast model is the lab; SPICE a check on reality** (the user's decisions, 2026-10-28): a closed-loop life in
  SKY130 takes minutes, a life in the fast model about a second, so ideas are tried, searched and judged in the fast
  model (`policies.py`, and a circuit's blocks as their measured behaviour: `model.py`, benched by `blocks.py`), and
  SPICE is used to ground them: short bench runs measure each block's numbers, and their spread over seeds' tolerances,
  which the model's lives draw from (else it flatters knife-edge designs); a model must reproduce its circuit's own
  closed-loop lives before it is trusted; closed-loop SPICE lives only at milestones, for a design claimed as a result,
  judged held out, to show it is close to something physically realisable, not identical to the model (the user,
  2026-10-29: B lived at 80% of its prediction, close enough); retune in SPICE only when realism matters. The fast model
  is held to "nor may the simulator" too; never re-implement transistors in it.
- **Judged robustly** (the user's decision, 2026-10-29, confirming my proposal): in the
  fast model every life draws its blocks' tolerances (their spread benched in SPICE), and its body where an experiment
  says, for tuning and judging alike; the nominal model only for debugging. Variation is sampled, not swept (a
  Monte Carlo average's error doesn't grow with the factors varied); designs compared on the same draws; each life's
  draws kept, to regress its score on them. A nominal search exploited a knife-edge that tolerances exposed
  (`discrete/NOTEBOOK.md`, D13).
- **Ngspice runs one thread per life** (`life.py`): lives run in parallel processes, and BSIM4's OpenMP threads made
  8 at once 17 times slower.
- **Ngspice run as a library keeps every circuit**: unload each (`destroy all`, `remcirc`). Bench runs and closed-loop
  runs can't share a process.
