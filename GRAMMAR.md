# A grammar of challenges (fifth draft, for discussion)

The next step after the universal circuit (`STORIES.md`): many more challenges, to see whether the detectors needed grow more slowly
than the challenges. The danger, as the user put it: after much grinding we may only have built detectors for our own grammar. So this
draft has two jobs: to generate worlds, and to measure how far the generator's own limits are shaping the answer. Stages 2 and 3 have since run it
(`discrete/NOTEBOOK.md`, D33-D35): the language and engine are in `lab/stage2_lang/`, and the predictions below are scored where stage 3 tested them.

## The grammar

A world is one or more statements: *at this link, change this, in this way*. Statements compose, so combining mismatches needs nothing new, and a world's length is the one axis of complexity.

**The links**, where the loop can be altered:

| | link | rows of the table there |
|---|---|---|
| L1 | motor to thrust | 2, 8 |
| L2 | the body's dynamics | none |
| L3 | blocks: how many, where, how they behave | 10 (ruled out: scarce, moving) |
| L4 | optics: what reaches an eye | none |
| L5 | eye to pulse | 6, 9 |
| L6 | the mouth: what counts as a meal | none |
| L7 | what a meal is worth | **1, 3, 4a, 4b, 5, 7** |
| L8 | worth to taste pulse | **none** |
| L9 | the score: what counts as doing well, with no wire to the brain | none |
| L0 | the brain's own parts | none |

Six of the table's eleven worlds are at L7, which is what the bank of predictors addresses, so its success is partly a result of what I picked. In all of them taste arrives at once and tells the truth, and the bank rests on exactly that.

**The four questions**, for each link:

| question | kinds of change |
|---|---|
| **How much?** | sign, gain, absence, doubling, saturation |
| **When?** | delay, duration, rhythm |
| **Depends on what?** | another channel (crosstalk), own actions or state, history, place, a block's own features |
| **Does that stay the same?** | fixed, step, drift, cycle, random walk, chance, chance in bursts |

The ten rows in these terms: thrusters L1 gain, fixed; ageing L1 gain, drift; swap L7 sign, cycle; unreliable L7 sign, chance; alternate L7 depends on history; digest L7 depends on time since the last meal; noisy eye L5 doubling, fixed; weak eye L5 absence, fixed; clumps L3 depends on place. So swap and unreliable differ by one word, as do thrusters and ageing.

**The third axis: what it demands of the brain.** The four questions say how a world is built, and they are permissive: nearly anything fits, so they make a checklist and a poor generator. The capabilities below say what a world asks for, and it's a capability we want to see the brain gain.

**What's being measured:** statements are sampled, and how well they cover the space is tested separately (below). A world may also be a *fault* (it hurts a brain) or an *opportunity* (a better way of living is on offer, and the base brain simply misses it).

## The language: making the grammar executable

A person has to interpret "L3, depends on history", so as it stands nothing can be sampled, and "can be written" tests nothing, since nearly anything fits (the critic, round 12). So the links and questions above are a checklist, and the grammar proper is a small language a program can run:

- **State variables**, named, each scoped to the world, the creature or **one block** (so a block can have its own memory and identity), with a drawn start.
- **Reads**: the wires (eye pulses, motor firings, taste), the simulator (position, heading, speed, blocks, meals, time), any state variable.
- **Writes**: the same points, including force on the body, a block's position, existence and kind, a meal's worth, a taste pulse, the score, the end of a life, and a brain's own part (L0).
- **Rules**: on a tick or an event, if a condition on reads holds, write a function of reads and state.
- **Time courses are variables with their own dynamics**, not a fixed list: step, drift, cycle, walk, chance, bursts, and the three I lacked: **scale-free** (1/f, Levy jumps, chaos), **hysteresis or ruin** (you cause a change, and it stays when you stop) and **adapting to you** (it reads what the brain does). Several rules may read and write one hidden variable, so one sickness can dim the eyes and weaken the thrust together, and one can predict the other.
- **Base forms**: the bodily loop; or nothing, any state machine behind the same wires. So other worlds stop being four hand-listed examples.
- **A link was missing, L10 the medium or space**: a wall stops the body, hides things and confines blocks at once, and filing it under L2 alone hid this. Firing could also stir a wake that moves blocks. So "one flat, still medium" was never the real boundary.
- **Field scope**: state over place, for trails, wakes, currents, mud, a moving front, and "where you've been".
- **Buffers and deferred writes** ("write at t + d"), for delay, echo, queues and parity over past bites, and **pulse generators as a write point**, for Poisson against regular firing, with a moment within the tick.
- **A defined pipeline**: named stages, each rule replacing or adding, in a fixed order, since gain then delay differs from delay then gain. Otherwise "statements compose" means nothing.
- **What a block looks like, apart from what it's worth**: emission per eye and worth per block; an occluder and collider primitive; every world constant writable.
- **Quantifiers and a named function set**: "nearest", "count within r", "for each block". This vocabulary sets the sampler's probabilities, so it has to be explicit.
- **A sampler**: a probability over programmes. A world's length becomes its description length, and the test of the grammar is no longer whether a world can be written, but **how probable it is under the sampler**.

**The compile test, the first thing to do.** Write every idea in the catalogue and the outsiders' lists in the language, then count what fails, and how improbable each is.

## How we got here: the rounds

Each round used a different source. A round counts as changing the plan only if it alters the links, the questions, the capabilities or the experiment. New examples don't count. The rule was to stop after two rounds with no change.

| # | source | changed the plan? | how |
|---|---|---|---|
| 1 | machine-drawn words | yes | "food takes time" showed demands, not only damage; the four questions |
| 2 | my own words | yes | the score as a link; capability as an axis; trade-offs, movement as a skill |
| 3 | capabilities | yes | a list of capabilities to count; risk, recurring contexts, combinations, contingency, evasion |
| 4 | attacking the brain's own tricks | yes | a new class of test: worlds that fool a detector, showing its false alarms |
| 5 | other fields (conditioning, control, comms, ecology, medicine) | yes | chance in bursts as a modifier, second-order cues as a capability |
| 6 | what every list so far has left out | **yes, the largest** | opportunities, which my filter would have thrown away; irreversible outcomes |
| 7 | machine-drawn words | yes, small | sensing as an action with a cost |
| 8 | inverting everything (help instead of harm) | yes, small | a block's own features as a noun: blocks can differ on one wire, by flicker or brightness |
| 9 | colliding pairs of themes | no | only new examples |
| 10 | physics (conservation, symmetry, phase changes, resonance) | no | only new examples |
| 11 | five fresh agents who saw none of this (`lab/v/grammar_outsiders1.md`) | **yes** | whole other worlds on the same wires; every constant redrawn each life; probes of what was learned; four more capabilities |
| 12 | three more fresh agents, and a critic who read the draft (`lab/v/grammar_outsiders2.md`) | **yes, the most** | an executable language; a false claim of mine withdrawn; five flaws in the experiment; ladders within a capability; three more capabilities |
| 13 | a second critic, on the same model despite my asking for another (same file) | yes, in detail and order | what the language still lacks; a pre-registered number; controls first; cuts for cost. Its verdict: stable enough to start building |
| 14 | the same eight lenses, sealed: an empty directory, no project instructions, memory or git status (`lab/blind_agents.sh`, `lab/v/grammar_outsiders3.md`) | **no structural change** | see below |

**The fresh agents weren't fully blind.** The harness starts each with `AGENTS.md`, the memory index and a git status, as the outside set's author reported. They didn't see this document, but they may have seen the rules and the table's existence, so their independence is partial. And all of them, critics included, ran on one model, the same as mine, so their agreement counts for little.

**What the sealed round showed.** The leak made little difference: the sealed lenses converged on the same things (delayed taste in five of eight, a gait, mimics, region-dependent worth, matching pennies, an unstable body, a rooted creature), and by my reading nearly everything can be written in the language, though that's untested until it exists. One exception: worlds that probe a clone of the brain ("what would you do?", in mathematics' Newcomb and self-reference ideas) need a read the language lacks. They also added new examples, and: **no taste at all, value shown only by the body's response** came up twice, and **replaying the seed** tests whether a memorised motor tape scores well, which is a trap for our scoring rather than for the brain. Three sealed agents also say what the user feared: every fault is one someone thought to write. This is one model's view, so it isn't independent confirmation.

**Brainstorming has stopped being the way to change this plan.** Rounds 11-13 never gave two quiet rounds in a row, and a critic can always find more. But the last round changed details, order and cost, not the structure, and what's left will be settled by building. This is my judgement, and the second critic's.

**Round 10's apparent stop was false.** Every source up to then was me, and the first outsiders changed the plan at once. By my own judgement, about a third of their 100 ideas weren't already in the catalogue in spirit, and nearly all the rest were, some named independently by several of them: delayed taste by four, a timing code on one wire by four. Almost all 100 can be written in the grammar; the few that can't are the whole other worlds below.

## The catalogue

Tagged with link and question: **H**ow much, **W**hen, **D**epends on what, **T** over time. An idea may demand more than one capability; each is listed once.

| capability | idea | link | Q |
|---|---|---|---|
| **Attribution across a delay** | taste delayed | L8 | W |
| | a good taste, then a bad one 5 s on | L8 | W |
| | tastes queue when busy, so delay grows with load | L8 | W, D |
| | blocks in pairs, so a drive at one eats the other first | L3 | D |
| | taste bundled over several meals | L8 | W |
| **Patience, doing nothing** | food takes time to eat | L6 | W |
| | both colours bad for a while | L7 | T |
| | seasons in which the best move is to rest | L3 | T |
| | sleep pressure: motors stop until rested | L1 | D |
| | blocks ripen: bad until an age | L7 | D |
| **Restraint, trading now for later** | a good taste that makes the next five meals bad | L7 | D |
| | poison eaten now makes food appear later | L3 | D |
| | no food until a poison is eaten, which releases five | L3 | D |
| | poison multiplies unless eaten | L3 | D |
| | food spreads if some is left alone | L3 | D |
| | no respawn: food is finite | L3 | H |
| | patches deplete: when to leave | L3 | D |
| | food beside poison is worth more | L7 | D |
| **Counting** | every twelfth meal is poison | L7 | D |
| | toxin builds up: one harmless, ten lethal | L7 | D |
| | satiety: worth falls with recent meals | L7 | D |
| | balanced diet: too much of either is bad | L7 | D |
| | tolerance: a repeated meal has less effect | L7 | D |
| **Timing and anticipation** | blocks turn bad with age | L7 | D |
| | a tide sweeps the blocks on a cycle | L3 | T |
| | a weather front crosses the world | L7 | D, T |
| | blocks expire if not eaten | L3 | W |
| | food only available on a fixed schedule | L7 | D |
| **Rhythm, movement as a skill** | a gait: thrusters must alternate | L1 | D |
| | stiction: thrust has to build up | L1 | D |
| | an unstable body that spins unless corrected | L2 | H |
| | the right thruster only works if the left fired recently | L1 | D |
| | a hidden gear: the same motor does different things | L1 | D |
| **Calibration** | `DRAG`, `PUSH`, `TURN` changed: the brain's time constants against the body's | L2 | H |
| | heavier with meals, weaker when starved | L2 | D |
| | thrusters tire with use and recover | L1 | D |
| | steering reversed, as with mirror glasses | L1 | H |
| | lag or backlash in a thruster | L1 | W |
| | a sudden new body mid-life | L1, L2 | T |
| | a thruster fails at some moment | L1 | H, T |
| | thrusters fire by themselves | L1 | H |
| | the mouth off-centre from the eyes | L4 | H |
| | food bruises above a speed, or can only be eaten from one side | L6 | D |
| | the mouth's reach changes with speed | L6 | D |
| | the world shrinks or grows | L3 | H |
| **Telling self from world** | a thruster firing blinds or fires the eyes | L5 | D |
| | eating causes a phantom flash | L5 | D |
| | every eye pulse or taste echoes a moment later | L5, L8 | W |
| | a mirage that moves with the creature | L4 | D |
| | sticky food: weak thrust after eating | L1 | D |
| | eating leaves debris | L3 | D |
| | a trail of your own that harms you, as in Snake | L3 | D |
| **Contingency: did I cause it?** | free tastes whatever the creature does | L8 | H |
| | bad tastes for fouls unrelated to food | L8 | D |
| | tastes with no meal, meals with no taste | L8 | H |
| **Place and direction** | a good colour that depends on region | L7 | D |
| | carry each meal home to bank it | L7 | D |
| | walls, narrow gaps, one-way doors | L2 | D |
| | mud, currents, a slope | L2 | D |
| | a tether | L2 | D |
| | a Moebius twist: crossing an edge swaps left and right | L2 | D |
| | a sun: eyes dazzled in one compass direction | L5 | D |
| **Novelty** | food only where you haven't been, or new ground rewarded | L3 | D |
| | blocks respawn where you just ate | L3 | D |
| | whatever you eat most turns bad | L7 | D |
| **Combinations of features** | food only if colour matches context, an exclusive-or | L7 | D |
| | key and lock: red makes blue edible for 5 s | L7 | D |
| | an antidote: red soon after poison undoes it | L7 | D |
| | food hidden behind poison | L3 | D |
| | flicker or brightness says which blocks are good, whatever their colour | L3, L4 | D |
| | blocks of a colour vary in worth | L7 | D |
| **Second-order cues** | seeing lots of blue predicts red turning bad | L7 | D |
| | a guide, a moving block that goes only to food | L3 | D |
| | one cue predicts another, which predicts taste | L7 | D |
| | a pattern of pulses at birth that states the rule | L5 | D |
| | food lies in lines, so a meal says where the next is | L3 | D |
| **Risk** | one colour steady, the other sometimes wonderful | L7 | T |
| | a rare block worth ten | L7 | H |
| | rare catastrophes: one lethal block per 10,000 s | L7 | T |
| | a lethal meal ends the life, so no recovery | L9 | H |
| **Recognising a context again** | world A, B, A, B: is relearning faster? | L7 | T |
| | the rule changes between bank models mid-life | L7 | T |
| | serial reversals: do they get quicker? | L7 | T |
| **Forgetting** | nothing changes for ages, then one change | L7 | T |
| | born confidently wrong | L7 | H |
| | memory wiped periodically | brain | T |
| **Ignoring, filtering** | an eye or thruster that does nothing, or fades after youth | L1, L5 | H, T |
| | one eye masks the other | L5 | D |
| | eye pulses cancel if simultaneous | L5 | D |
| | eyes see a little of the other colour | L4 | D |
| | blocks blink on and off | L4 | T |
| | empty decoys and mimics | L3, L7 | D |
| | eyes ignore anything faint | L5 | H |
| | a lie arrives in bursts, not singly | L7 | T |
| **Active sensing, sensing at a cost** | eyes work only just after a thruster fires | L5 | D |
| | an unused eye decays; an ignored one grows more sensitive | L5 | D |
| | a preview of taste at a distance, like smell | L8 | W |
| **Evasion** | poison chases you, or food flees | L3 | D |
| | firing thrusters draws poison towards you, so stealth pays | L3 | D |
| | a rival eats the food | L3 | D |
| | infected by poison: thrusters occasionally hijacked | L1 | D |
| **Budgeting** | moving costs ten times more, with nothing on the wires | L9 | H |
| | life's length unknown or very short | L9 | H |
| | nothing's poison until learned, then the world gets harder | L7 | D |
| **Knowing there's no cure** | taste inverted for good | L8 | H |
| | coin-toss tastes | L8 | H |

### Added by the outsiders (round 11)

Four capabilities are new: **randomising**, **learning without reward**, **using objects**, **inference without experience**.

| capability | idea | link | Q |
|---|---|---|---|
| **Randomising** | matching pennies: whichever colour you favour flips | L7 | D |
| **Learning without reward** | all blocks tasteless for 50 s, then taste switches on | L8 | T |
| | one colour tasteless at first, then both count (latent inhibition) | L7 | T |
| **Using objects** | blocks are pushed, and eaten only when shoved into another | L6 | D |
| **Inference without experience** | an inert signpost leads to red; red turns bad; does the signpost lose its pull untasted? | L7 | T |
| | a colour that pays alone, then together with another: is the second learned? (blocking) | L7 | T |
| **Combinations of features** | two-colour blocks: each colour alone is food, both together poison | L3, L7 | D |
| | one cue changes what another means | L7 | D |
| | colour decides at first, then only the pulses' regularity does | L7 | T |
| **Restraint** | a colour bad at first, then the richest after several doses | L7 | D |
| | food ringed by poison, so a known cost must be paid to reach it | L3 | D |
| | a tether: reach far blocks by swinging away first | L2 | D |
| | a block flees if you fired recently with it in view | L3 | D |
| **Timing** | anything eaten on a hidden beat is food, off it poison | L7 | D |
| | memory depends on meals being spaced, not massed | L7 | W |
| **Calibration** | a stepper rudder: a firing moves a notch, and the same firing means different things | L1 | D |
| | eye rate rises then falls when very close | L5 | D |
| | a sloshing tank: firing near one rhythm builds a wobble | L2 | D |
| | a firing kicks the nose the wrong way first | L2 | W |
| **Rhythm** | eyes give only noise; food comes only from a firing pattern | L1, L7 | D |
| **Risk** | each meal in a streak raises the chance the next is poison | L7 | D |
| **Second-order cues** | an unseen competitor eats only food, so the colour left lying about is suspect | L3 | D |
| **Contingency** | danger in bouts: any thrust risks a bad taste, no block eaten | L8 | D |
| | taste is silent while turning, though the score still counts (a loophole) | L8, L9 | D |
| **Evasion** | poison creeps towards you, but freezes while in view | L3 | D |
| | tag: the same stimulus means chase or flee, depending on the last taste | L3 | D |
| **Ignoring** | tasteless flicker posts that drive an eye at maximum (a noisy TV) | L4, L5 | D |
| **Forgetting** | all blocks tasteless for 25 s, then the old rule returns: nothing is not the opposite | L8 | T |
| **Place** | a world ten times wider with one tight cluster | L3 | H |
| **Recognising a context** | everything snaps back to the same start every 20 s | L3 | T |
| **The brain's own parts** | positive or negative tastes mostly lost, as in Parkinson's | L0 | H |
| | a deep power sag wipes fast memory | L0 | D |
| (mine, missed) | junk food: tastes good but weakens thrust afterwards | L1, L8 | D |

### Added by the outsiders (round 12)

Three capabilities are new: **monitoring and repairing oneself**, **rationing learning**, **hiding intent**. Mathematics also suggests **ladders**: a capability can be graded by formal difficulty, as alternation, then a counter, then parity with noise, and how far up the brain gets is a sharper measure than pass or fail.

| capability | idea | link | Q |
|---|---|---|---|
| **Monitoring and repairing oneself** | a stroke: a random block dies at a random moment | L0 | T |
| | gains drift until feedback runs away (epilepsy) | L0 | T |
| | recruits keep multiplying, drawing power (a tumour) | L0 | D |
| | motor drive declines slowly: does compensation mask it, then fail at a cliff? | L0 | T |
| | memory's retention falls through the life | L0 | T |
| | waste from firing raises noise until a rest clears it | L0 | D |
| **Rationing learning** | each write permanently shrinks a memory cell's range | L0 | D |
| **Hiding intent** | a scavenger takes any block approached steadily for over 1 s | L3 | D |
| **Ladders** | after n reds, n blues are food | L7 | D |
| | taste is parity over a secret subset of the last 8 bites | L7 | D |
| | thrust unlocked by a secret word of motor firings | L1 | D |
| | heading diverges unless corrected, with a data rate the theorem fixes | L2 | H |
| **Contingency** | every 50th motor firing gives a bad taste, so spending becomes felt | L8 | D |
| | a free meal after 15 s with none, whatever the brain did | L8 | D |
| | worth depends on the firing rate before the bite, not on steering (Newcomb) | L7 | D |
| | an implausibly rare punishment: poison tastes bad on only 10% of bites | L8 | H |
| **Second-order cues** | a tasteless colour banks a token, which decays, and the other colour needs it | L7 | D |
| **Ignoring** | a poison block drives its eye three times as hard | L5 | D |
| | each eye sees a random mixture of both colours | L4 | D |
| **Combinations** | same rate, different texture: Poisson against regular | L5 | D |
| **Calibration** | a block has a hidden reserve speed, and bounces away below it | L6 | D |
| | one thruster weak for 30 s, then quietly recovers: is the recovery noticed? | L1 | T |
| | a growing body, from 2 to 4 mm | L2 | T |
| | hinges rather than thrusters, where reciprocal motion goes nowhere | L2 | H |
| **Place and scale** | blocks on a fractal, with no characteristic scale | L3 | D |
| | blocks as live cells of a cellular automaton | L3 | D |
| | crossing one seam swaps food and poison | L7 | D |
| **Learning without reward** | one eye silent for 30 s, then opens | L5 | T |
| | only the food colour exists for 25 s | L3 | T |
| **Forgetting** | the taste wire dies at 40 s: nothing heard is not nothing happened | L8 | T |
| **Restraint** | insurance: firing above a level halves poison's cost and mutes its taste | L8, L9 | D |
| (the medium, from the critic) | firing stirs a wake that moves nearby blocks | L10 | D |
| (per-object, from the critic) | a nut that needs three strikes | L3 | D |
| (coupled, from the critic) | food and poison in a predator-prey cycle | L3 | D |
| (world as goal, from the critic) | taste arrives when blocks are sorted into a pattern | L9 | D |

## The experiment

The question is whether the detectors needed grow more slowly than the challenges. Earlier drafts could have answered yes by arithmetic alone, so two critics' findings shape this. Rule-changing worlds come last, by the user's decision, and **the first phase's answer is labelled "taste immediate and truthful"**: those are the conditions the bank rests on, so it mustn't be pooled with or generalised to later worlds.

**Before any code:**

1. **Write down the primary result, and what means no**: `PROGRAMME.md`. Three counts would let whichever looks flat be reported, so detectors, models and capabilities are explanation only.
2. **Seal two sets.** A test set compiled by a fresh agent from outside sources, RL benchmarks and the conditioning literature, from neither this document nor its lists; worlds in it that won't compile stay in the denominator. And a held-out split, frozen before the first cure.

**Then, in order:**

3. **Synthetic controls, which need no language and could kill the analysis cheaply.** A generator with a known number of types, and one where **each world truly needs its own cure**. Coverage from greedily chosen cures is concave for almost any population, so if the second control also looks like a saving, the analysis can't tell us anything. Whatever separates the real data from this control is the measure of "less than 10x".
4. **A minimal language and engine**, driven by the source audit, with about 30 worlds hand-written end to end. One numba-compiled rule interpreter, since a rule in Python would run hundreds of thousands of times a life. `world.py`'s constants are numba compile-time globals, so they must become arguments, in a copy, before anything can be redrawn.
5. **A pilot of about 100 draws**: the share of learnable worlds with a gap, and lives per world. Only then freeze the samplers, **two or three rival ones with different primitives**, since one sampler sets the answer. Report the spread. Keep sampled worlds to about 300.
6. **The present circuit's coverage on fresh draws, with no new cures.** The first real number, and it scores the predictions below.
7. **Does a longer life change what's learnable?** The job asks for about 10 meals in 100 s, so few rules can be learned at all. Check at 10x, on about 30 worlds, whether ceilings rise. 100x is out of reach (about 4 days per circuit, estimated).
8. (Parked at decision B, 2026-11-07, for stage R: rivals made from simple parts, `PROGRAMME.md`.) **Add cures, by a designer who sees only the training worlds, to the largest failure groups, simplifying as we go** (`PROGRAMME.md`). One cumulative circuit, scored by description length, then parts and power, since a new bank model can absorb what would have been a detector. After each addition, re-run earlier worlds and the unmodified world. L0 worlds have a frozen list and their own plot, as new detectors would otherwise create new challenges.
9. **Open the held-out split and the outside set.**
10. **Then the rule-changing worlds**, reported apart.

**How worlds are judged:**

- **Sorted by gap to what's achievable, not by whether they hurt the base brain**; faults and opportunities reported apart.
- **Ceilings:** a policy told the hidden rule first, and a search only where that shows a gap. A world is dropped as "no gap" only if the told policy also ties with base. Otherwise a weak ceiling hides a hard opportunity.
- **Unlearnable worlds** are kept as a test of doing no harm. **Failures stay in the denominator.**
- **L9 worlds** have no signal on the wires, so no automatic cure can respond to them. They are reported apart, as design-time tuning rather than learning.
- **Statistics:** the sampled unit is worlds, so bootstrap over worlds. A margin set in advance on the fraction of the gap closed, since a tie from too few lives would read as "no harm". Control the false discovery rate: at 95%, 300 worlds give about 15 spurious calls. Racing saves lives: about 20 pairs, then more only for borderline worlds.
- **Cost, estimated, nothing run:** 50 pairs across 300 worlds is about an hour per circuit, on 8 lives a second.

**Deferred, once the count exists:** probes of what was learned (remove an eye after learning; restore a changed world; let a rule return), and clustering wire recordings to see whether worlds that look alike share a cure. Neither changes the count, but the second is the direct test of whether types emerge, so it's deferred and not cut.

**Cut:** estimating the unseen by Chao1, as cures overlap and fresh-draw coverage answers the same question. A design budget per world, which is impractical. A leave-one-out build for each fold, replaced by the one held-out split.

**The adversary is demoted, not cut.** A search always finds a hole, so it can't change the conclusion. But it isn't limited by what I'd write, so it's kept for the end as a source of missing words.

## Tests of the grammar itself

No grammar can be shown to span every possible world, so instead we measure where it falls short.

1. **The compile test**, on the catalogue and on the sealed outside set. The language was built from the catalogue, so passing there means little; only the sealed set counts. Report non-compilers, and the spread of each idea's probability across the rival samplers, as a single probability has no reference point.
2. **Audit the source.** Every constant and assumption in `world.py` and `Life.step` gets at least one world, or a written reason. Constants: `RADIUS`, `WORLD`, `BLOCKS`, `EAT`, `SENSE`, `REACH`, `RANGE`, `RAYS`, `BLOCK`, `PUSH`, `TURN`, `DRAG`. Assumptions: a torus; blocks still; respawn uniform, outside an exclusion zone; equal colours; occlusion; both eyes on one corridor; each eye one colour, firing Poisson; several meals in a tick giving one clipped pulse, with food and poison cancelling; taste within the tick; eating only moving forward; forces adding; drag the same on speed and spin; thrusters identical in position; the birth state.
3. **Coverage at the wires, under several policies.** I wrote that two worlds looking the same on the wires are the same challenge for any brain. **That's false for a closed loop**: one fixed policy never triggers contingencies it doesn't touch, and at L9 the wires match while the best behaviour differs. So signatures come from several policies, including motor babbling. They are used to remove near-duplicates, and matching on them is only evidence.
4. **Held out**: if cures saturate on the training worlds and fail on the held-out split or the outside set, **we've built detectors for the grammar, and we'll be able to say so with a number**.

## My predictions, written before running anything

Guesses, to be scored. Scored by stage 3 (D35), where it tested them: place-dependent worth stays uncured, right (3 of 3 region worlds fail); bursts of lies fool the bank, partly (3 of 8 lie worlds fail); most random expressions unlearnable in a life, right in effect (about 70% have nothing to learn, not by length alone); the present detectors cover about half the learnable ones, consistent (a quarter to a half). The rest weren't tested (delayed taste, gaits and trade-offs are stage 5's kinds or weren't drawn).

- **Taste delayed by more than about half a second breaks the bank**, since "vouched" assumes the taste belongs to the present drive. A new type.
- **`DRAG`, `PUSH`, `TURN` are a new type**: no loop adjusts the brain's time constants now.
- **A gait gets nowhere**: the circuit can't discover a rhythm, and starves.
- **Trade-offs get nowhere**: nothing in it values the future, and no model in the bank says a bad meal can be good.
- **Bursts of lies fool the bank**: two lies in a row was already its weak spot.
- **Place-dependent worth stays uncured**: it has no sense of place.
- **A sudden swap of eye wiring or thrusters is mostly handled**, as a one-off swap.
- **Most long random expressions are unlearnable in a life.**
- **The base brain misses nearly every opportunity**, so that's where the largest unnoticed gaps are.
- **The present four detectors cover about half the learnable short expressions**, and less of the long ones.

## What this can't reach, in this draft

- New organs, more than two eyes, a third colour, a richer taste, for the richer world later.
- Anything the simulator can't express: its blocks are points in one flat, still medium with one kind of meal.
- Learning across lives (inheritance, repeated lives), for later: it fits the wires, but this project asks for learning in a life.
- The outsiders' agreed limits of the whole set-up: rich perception (all five), language or instruction (four), skilled many-jointed movement, choosing its own goals, and telling understanding from behaviour.

## The user's decisions (2026-11-04)

1. **Rule-changing worlds come later.** Delayed, lost or lying taste, eating that takes time, mid-life rewiring and meals that end a life are allowed, in wrappers, but only once testing within the current constraints is exhausted.
2. **External memory: not yet.** Marks left in the world stay out.
3. **The brain is a link.** The same changes apply to the brain's own parts, such as a slow hold or a stuck node.
4. **Fresh agents, yes; blind worlds from the user, no.**

## Where I differ from the critic

- **Marks in the world** stay out, by the user's decision, though the critic has a point that bears on it: trails, debris and "food only where you haven't been" already store marks, and offloading memory could lower the detector count. Worth reconsidering when the time comes.
- **Fresh agents as a guard**: if they're the same model they share priors, so their agreement proves little. True. Agreement between them isn't treated as evidence, and the outside test set is the better guard.
- **Other learners and two bodies on one brain** can be written once the language exists. They wait until the single-creature, single-body worlds are done, as a matter of order.

## Still open

- The primary result's 80% and half, and the definition of description length, to be fixed after stage 1 (`PROGRAMME.md`).
