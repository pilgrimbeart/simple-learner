# How many ideas must a small brain be born with?

*The programme so far, as an abstract (2026-11-07; its aim restated 2026-11-09). Details and every number's source: `discrete/NOTEBOOK.md`
(D31-D35), `PROGRAMME.md`, `STORIES.md`. Figures marked ? are not yet known.*

**Aim.** The goal is intelligence that scales, in a brain for a robot: generic components such that a brain that isn't
coping improves itself by recruiting raw material, so that to solve a bigger problem you just add more brain, with nothing
central deciding where it goes (`README.md`, The goal, with the test for it). We study it in the simplest setting we
could build. A simulated creature has two eyes, two thrusters and one sense of taste (+1 food,
-1 poison). It lives in a world of red and blue blocks, and must learn within one 100 s life which colour is poison:
one bit. A first brain, a sheet of identical cells that assembles itself, learned the bit, but each cell was complex.
A second, a small circuit built by hand, learned it too, and was built in real transistors and lived in SPICE to
show it could be made. The question now is how such a brain could notice, by itself, that it is doing badly, and put
itself right.

**The budget in bits.** A taste carries at most one bit. At our circuit's pace, about 0.6 usable tastes a second, a
clean life supplies about 50 bits, and a world where one taste in five lies supplies about 15. A creature that eats
faster can buy several times more, paid for in poison. The base task needs one bit. But the worlds we care about
change the rules (colours that swap, meals that turn bad when eaten too soon, tastes that lie), and writing down such
a rule takes 100 to 400 bits or more. (We first concluded that no brain can learn such a world within a life; the review of
2026-11-11 showed that conflates our description of a world with what the creature must resolve, and with what all its senses,
not only taste, can supply: D47's play draws far more from the eyes.) Taste alone can only
choose among possibilities its structure already makes cheap, and choosing among K of them costs about log2 K bits of
evidence (MacKay's Occam factor). Learning in a life is selection within a repertoire. The real question is how
small a repertoire, made of how simple parts, covers how much of what worlds ask.

**What we did.** We gave the brain ten different mismatches with its world and cured each by hand. One circuit, a
*bank of predictors*, does the job of many. It holds 7 rival ideas of what taste means (it never changes, it changes
often, it alternates, it repeats in threes, ...). Every trusted taste reveals which colour was food, whatever the
creature was doing, so each rival is scored on every taste without ever being tried, and the creature follows the
best. Naming one rival costs about 2.8 bits.

To judge generality without marking our own homework, we wrote a language for worlds that can't touch the brain,
and drew 200 worlds at random from it, the generator frozen before any draw. Each world was run on the same paired
lives (one seed, red then blue as poison) with four brains:
- the base circuit;
- the bank;
- the bank's own parts told the right colour at every moment, as the yardstick;
- a frozen ideal learner holding 12,591 hypotheses (2.3 to 15.2 bits each), as the reference.

Everything was timed in seconds, with the step halved until results stopped changing (1.25 ms). Each world was run on
60 to 300 pairs. A world passes if the bank closes more than a quarter of the gap between base and the yardstick, and
more than half of what the reference closes. A separate agent then checked the verdicts from the raw lives, with
code of its own.

**Results.**
- **What there is to learn.** 35% of the 174 distinct random worlds have something to learn [28-42%].
- **Coverage.** Of those 61, the bank surely passes 11 (18%) and surely fails 24 (39%); the other 26 are too close
  to call, mostly worlds with little to gain. So coverage lies between about a fifth and three fifths.
- **Doing no harm.** Where there is nothing to learn (113 worlds), the bank surely does no harm in 79 and surely harms
  in 2; in many it costs a little, about .07 against gains elsewhere of .3 to 2.5.
- **Efficient within its repertoire.** Where the reference learner surely succeeds, the bank surely passes in 7 of 9
  worlds. Where the bank fails, the reference mostly fails too.
- **Failures are missing ideas.** They cluster in a few families: colours that swap at some period, a meal soon
  after the last being bad, a food colour set by place, and some liars. A ten times longer life rescues a few of the
  meal-timing worlds (4 of 16 pass at 1000 s) and none of the seven swaps. In swaps the missing idea is *when*: an
  earlier test found that about 14 bits of hypotheses about timing close half the gap, and at 1000 s the reference,
  which holds such hypotheses, closes most of the gap in several swap worlds the bank fails.
- **One part does harm.** Where the eyes are about twice as sensitive, the bank loses .36 to .59 against base. Switching
  parts off traces most of that loss to its eye filter, whose constants were tuned at the eyes' usual pulse rate:
  built-in knowledge of the body that turns out to be wrong.

**What is unknown.**
- The usable evidence in each world: the information its tastes carry about its rule, and what an ideal learner
  given the world's true prior would make of it (?). Our only measure of the senses counts how different a world's
  signals are from the plain world's, which is not evidence about the rule.
- How many bits and parts the bank itself holds (?), so the bits built in per world covered can't yet be stated.
- Why the told yardstick can be beaten in long lives (?).
- Coverage on the sealed outside set of challenges, on which the final verdict rests (?).

**Conclusion so far.** The bank's principle, rival predictors judged on every taste, works: it learns what it can
imagine almost as well as an ideal judge. Its limit is its repertoire, and the repertoire is ours. So the finding
doesn't yet answer the question. What it does show is the shape of what's missing: mostly ideas about time.

**Next (stage R).** Make the rivals from simple parts rather than writing them: toggles, counters, oscillators and
timers, connected in various ways, hierarchies included (a chain of toggles is a counter; an oscillator driving a
toggle doubles its period). First drawn at random at birth, K of them, with the bar to adopt one rising with log2 K;
then grown within the life where no rival predicts. If a repertoire drawn by a simple rule covers more than the
written one, at a cost in evidence and parts that grows slowly with the worlds covered, then a few general parts are
emerging. If it needs one part per world, then we have hand-designed everything.

**Along the way (stage R, 2026-11-08).** Long lives at first seemed to lose more than they gained. The cause was the bank's balance
learner, which wears the bank down over 10,000 s. A version that sizes its own steps and quiets its own wobble lifts long lives surely
in 12 of 13 worlds, but costs .6 in 100 s lives: exploring a body whose thrusters are equal costs more than a short life's drives can
reveal. When a part should explore at all is now an open question (`discrete/NOTEBOOK.md`, D36).

**Against the goal (2026-11-09).** Nothing here passes the scaling test (`README.md`). This programme measured how far one
fixed design covers new worlds, not what more material buys, and where more was tried it bought nothing: sure passes stayed
at 9, 9 and 10 of 55 with 10, 100 and 1000 random rivals (D36). Since then (D37, D38): a ruler of three ladders, and a first climb
on one of them. A register of the letters the tastes reveal, read by one comparing unit per look-back, learns a hidden word twice as
long for each doubling of its material, and picks for itself which kind of event should move it. Timing is not yet solved: clocks
that lock on to surprises beat the starting brain at every rung but solve none.

**Since (2026-11-10, D39; light rigour, 5 pairs a run).** The three ladders are one problem (the food colour as a function of a context
moved on by some kind of event), and its ideal learner's known local form is a context tree over a register; the record is such a tree
of depth one. Proposed as the one design; not built. On timing, a bank of fixed clocks whose phase is set by the world's changes, no
further than the evidence says, solves the first rung and reaches .63 at the third with 60 clocks, about the level of a designed brain
told the period. And touching pairs of blocks cost the starting brain a quarter of its food, declined rather than poisoned: the first
rung about acting, still without a yardstick.
**The tree built (D40).** One kind of node, recruited where a new context arrives beneath a contradicted node, no setting changed between
ladders: sequences to rung 17; combinations, where nothing climbed before, rungs 1, 3, 5 and 6 at 20 pairs, higher rungs needing more
nodes; with clocks as registers, timing's rung 2 at .94 and rungs 5 and 7 near half; plain exactly 0. Pairs' hand-made yardstick failed.
**Acting, and knobs first (D41 to D43).** Touching pairs are no acting challenge for these eyes: a driver that stops to look judges
well but the looking costs what it earns, the eyes giving too few pulses to say where across its path a block lies. Of the body's
numbers drawn afresh each life, only the balance between the thrusters matters much, and drag at its extremes. The user's rule: turn a
knob before recruiting anything. The balance knob turned by trial and error closes half the gap in 1000 s; set from a measurement (the
creature's own pulses counted through one revolution on one thruster, by the same recording unit that learns sequences) it closes over
three quarters in 300 s.

**Next: a dancing brain** (the user, 2026-11-10; `PROGRAMME.md`). A simple brain's behaviour produces too little
information to find anything new. So start with many movement cycles of different timings, each judged by its own prediction of what
its movement makes the senses do, and let them settle on what works. The first count (D44): of nine movements, only spinning on one
thruster at a time tells the body better than foraging (to about 4% in 100 s, against 27%), and it measures both knobs, the balance and
how far a beat carries; no movement tells where a block lies across the path. A first verdict that driving straight tells nothing was our observer's blindness, not the movement's. Then, in the user's frame of play first and the challenge later (D47): a brain that played at random through a quiet spell, with nothing to taste, starts the challenge surely ahead of one that only foraged (+1.5 at once, about half the way to a brain told its body), by reading each motor's own beat-clocked record and making the two motors' effects equal; taste is best used to choose among play's few guesses.

**The muscle-like body** (the user, 2026-11-11; D53). Thrusters made muscle-like (a pulse raises an activation, thrust a sigmoid of it):
every rule written from the old physics broke (the told yardstick, the measurers, the partners formula), while the coupling principle
carried over untouched and beat the formula there. The ladders certify much as before and the tree still climbs them. The new body
forages at about two thirds of the old one's level and is steeper in its knob; D52's "knife-edge" turned out an over-reading.

**Since 2026-11-10: play, coupling, and taking turns** (`discrete/NOTEBOOK.md`, D44 to D54). (1) *Play pays later*: a brain that moved
at random in a quiet spell, with nothing to taste, started a later challenge ahead of one that only foraged; but the step from what play
measured to how to act was, at first, a formula of ours (D47). (2) *Understanding as coupling* (the user's principle): a brain should
seek the simplest connection between its inputs and its actions in both directions, in bits their mutual information. With no reward,
coupling peaks at the body's right setting, and a search guided by it, keeping its default unless a change clearly wins (MacKay's
Occam factor), beat our designed formula and left normal bodies alone (D51, D52). (3) *A principle survives a change of body, a formula
doesn't*: on muscle-like thrusters every rule written from the old physics broke, while coupling carried over untouched (D53). (4)
*Parts must take turns*: the coupling search split between the two motors works only when they take turns, as in a Sepulchre half-
centre (one tunes while the other holds, tiring hands over, a part that moved wakes its partner), matching the whole-brain search on
fresh creatures; adjusting at once, they can't tell whose change helped (D54). (5) *A limit*: coupling prefers slow, careful movement,
food a faster one; trading speed against care needs taste (D54). Mistakes caught on the way: an observer blind to what it didn't
understand (D44), a "knife-edge" that was ten pairs' noise (D52, corrected in D53).

**Since 2026-11-12: new parts, hunger, and the growing network** (`discrete/NOTEBOOK.md`, D55 to D59). (1) *New parts taken up by
play*: given a split eye and smaller thrusters mid-life, a brain that plays with the new parts, judged by the new sense, wires them and
surely gains; playing only until each new eye line has one sure thruster keeps it short up to two new thrusters a side (D55, D57). (2)
*Knowledge makes skill worth having*: the new steering helps a brain that knows which colour is food and harms one that doesn't (D58,
suggestive). (3) *Hunger* helps in lean worlds but needs a sense of normal that fits the world (D56). (4) *The growing network* (the
user's idea, after Béna & Goodman 2025): detectors grow where guesses fail, built on detectors active together; copies removed, unused
ones fade. It meets the scaling test in miniature: patterns 2 to 17 steps long grow 17 to 48 detectors with nobody told the size, and
more material helps until it has what it needs, then goes unused. It relearns a changed pattern where the hand-built tree stays stuck
(+1.0 to +1.6, two seed sets); removing copies is what keeps room free. Given a stream for every sense instead of one we chose, it picks
the useful one for each kind of lesson and matches ours (confirmed paired). The written clean-up rules can be replaced by the user's local
competition for energy, among siblings only, with a detector's standing including the success of the detectors built on it (trophic
support): no cost in a world that doesn't change, and beats the tree by 1.5 when it does. Still handed to it: that one colour's poison is
the other's food (worth .05 to .15, all in exploring spared), and our rule for which eye was eaten; next, the network on the body's own
pulses.

**The scaling curve (D60).** The most generic growing brain (every sense a stream, cleared by trophic sibling competition) climbs the
sequence ladder as material doubles, longest pattern solved 3, 13, 17 (fresh seeds): the scaling test's first part on one ladder. It
climbs the combination ladder once (rung 1 to 3) and stalls, solves no timing rung (more material slightly worse there), and commits
nothing where there is nothing to learn.

**Overnight, 2026-11-12/13 (D59, D60).** A fault in spotting copies (a detector and its own ancestor taken for copies) had been doing the
clearing credited to copy removal; fixed, the clearing that works is recycling the least used detectors whenever room is needed, which
beats the tree by 2.2 when the pattern changes and loses nothing when it doesn't. The best generic brain (a stream for every kind of
event and sense, recycling on demand) climbs sequences to 17 and combinations to 5 of 6 as material grows (fresh seeds for the
sequences), does no harm where nothing is to be learned, and is surely worse with recruitment switched off. Timing: with clocks of its
own re-phased when the food colour is seen to change, a foothold (rung 2 on development seeds, about .4 on fresh). One design holding
it all comes within .15 of each ladder's specialist. Not told that one colour's poison is the other's food, it pays only the cost of
exploring; the rule for trusting tastes is unnecessary.
