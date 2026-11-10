# The programme

One page to keep us on track. The goal and its test are in `README.md`, The goal. If work can't move the scaling curve, it is parked in `QUESTIONS.md`.

## The next phase: a dancing brain (the user, 2026-11-10; planned, not started)

**The criticism** (the user). We have been designing a simple, clunky brain and expecting something clever to come of it. But a brain that only scans, drives and runs meets a narrow slice of what its body and world can do, so its behaviour doesn't produce enough information to find a new stratagem. Better to start with a brain that is creative from birth: many cycles of different timings driving its movement, erratic to look at, which gives it evidence about what works; the cycles then settle on the ones that do. Rhythms, coupled cycles and knobs that retune them are in the spirit of Sepulchre (`MIXED_FEEDBACK.md`; whether he argues for learning by exploring is to be checked, not assumed).

**What the record says.** For: the weak thruster's knob was set in minutes only once the creature did something unusual on purpose, spinning on one thruster, and watched what came of it (D20, D43). Against, as stated: variety isn't yet evidence. Judged by taste, many things varying at once are noise to each other (one score, under a bit a second): 200 random detectors each nudging a motor cost food and learned little even in very long lives (D16); exploring wildly early in a life hurt (D15); a small wobble cost a tenth of the food and took fifteen times a short life's drives to notice (D36).

**The form to test.** Each cycle is judged by its own prediction, not by taste: "when I move like this, the view should do that". That error is there at every moment, belongs to one cycle alone, and carries far more bits a second than taste. Cycles whose movement makes the senses predictable settle and keep their timing; the rest fade; taste only chooses among the settled. The brain must know what it did (its own beats are the ruler, D43). Dancing costs food, so it belongs to the young and the frustrated.

**Stages**, each with its predictions and how sure written first, about 5 pairs, a ledger line (How we work, below):

| stage | what | ends when | what it decides |
|---|---|---|---|
| **D0. Count the bits** | A handful of movement cycles written by hand (spin on one motor, on the other, alternate, burst and coast, zigzag at a few periods, stop and look), each with its own recorder (a register moved by the brain's own beats, D43). For each, and for ordinary foraging: bits a second an ideal observer gains about each thing worth knowing (the balance, the drag, where across the corridor a block lies), and the food it costs. | A table of bits a second and food lost, per cycle and per thing | Whether dancing yields information that foraging doesn't, and about what. If it doesn't, stop here. |
| **D1. One cycle that settles itself** | The best cycle of D0 starts when a knob's own adjusting has stalled while things go badly, sets the knob from what it measured, and stops when its estimate stops moving. No hand-written gate. | It matches D43's measurer on unequal thrusters and costs nothing on an ordinary body | Whether a cycle can govern itself |
| **D2. Several cycles at once** | Two, four, eight cycles together, each judged by its own prediction. Do they spoil each other's evidence? The many-units question, with prediction as the teacher instead of taste. | A curve: time to set each knob against the number of cycles | Whether prediction escapes the wall taste hits (D16) |
| **D3. Settling** | Cycles that predict nothing fade; those that do keep their timing; taste chooses among them. Born dancing, on plain, lopsided and dragging bodies. | The dance ends by itself where there is nothing to learn, and the brain ties the starting brain there | Whether "erratic, then settled" beats "simple, then patched", on the same lives |

**What would count against it.** The cycles yield no more bits than foraging about the things that matter; or dancing loses more food than the knobs win back within a life; or cycles judged by prediction still interfere as those judged by taste did.

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
- **This is for understanding, so rigour is light until there is a claim** (the user, 2026-11-10: an itch to scratch; it needn't be of academic quality, nor physically realisable yet). Day to day: paired lives, a prediction written first, about 5 pairs, one step (2.5 ms). **A principle worth having shows in about 5 pairs**; an effect that needs 40 to see is parked. Held-out seeds, halved steps, sealed sets, independent checks, `mixed_feedback.py` and SPICE wait for a final claim, if we ever want one. `AGENTS.md`'s ground rules for a brain (the interface, no god, no shared clock, seconds not ticks) are not rigour and always hold.
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

