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
a rule takes 100 to 400 bits or more. So no brain can learn such a world from nothing within a life. It can only
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
