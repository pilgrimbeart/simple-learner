# Parts and interventions

Once a brain works well enough to learn, many kinds of change could make it better: turning a knob, removing a part
that tuning made redundant, adding a memory, a sequence detector, a rhythm. Each needs something to notice that it is
wanted, to choose it among the others, and to judge whether it helped. This is a map of that space, from the
literature and this project's own results: background for the brain that changes itself (`RECRUITMENT.md` holds how
units are recruited, with the literature of its triggers; `BOUNDS.md` what limits how fast any change can be judged).

The user's observation (2026-11-02): even the simplest body in the simplest world with the simplest brain offers this
rich a set of interventions, and open questions about how to detect that each is needed, choose between them and carry
them out. That suggests a space wide open to map logically, if we are disciplined, and perhaps a universal circuit
that can do all of them (below).

No single canonical taxonomy of interventions on a small dynamical brain is known to me; the pieces exist, each well
studied apart. They fall along four questions about any intervention: **what changes** (the operation), **which part**
(the catalogue), **when** (the trigger) and **how it is judged** (the credit).

## 1. The operation: what changes

From the cheapest and most reversible to the most drastic:

| | operation | example | reversible? |
|---|---|---|---|
| 0 | **State**: not learning; what the circuit holds | B's doubt | yes, fast |
| 1 | **Tune** a knob: a gain, threshold, time constant or bias | D20's balance; D15's tuner | yes |
| 2 | **Modulate**: switch an existing part into another mode | a relay neuron made an oscillator by its conductances [1] | yes |
| 3 | **Rewire**: a connection's target or sign changed, or enabled or disabled | NEAT's disable gene [2] | mostly |
| 4 | **Prune**: remove a part | one that tuning left redundant | no, unless it can regrow |
| 5 | **Duplicate and diverge**: copy a part, then let the copies specialise | gene duplication [3]; Net2Net's widening [4] | yes, at first |
| 6 | **Add** a new part from the catalogue (section 2) | D24's map counter | yes, if it starts silent |

Two ideas from the literature govern growth and pruning:

- **Function-preserving growth** [4, 5]: a part added with its effect at zero leaves the brain exactly as good as it
  was, and is then tuned in. A brain never pays for trying a part; it is the structural form of safe policy
  improvement (`BOUNDS.md`, Watching and intervening). A duplicate is function-preserving if the copies share the
  original's output between them.
- **Constructive or selective.** Grow when needed, or overproduce and keep what is used (selective stabilisation [6];
  neural Darwinism [7]; the lottery ticket [8]). The user's plan for the ideal observer (a strong meta-brain, then
  pruned: `QUESTIONS.md`, step 3) is the selective one. Pruning by what a part's removal would cost is classical in
  networks (Optimal Brain Damage and Surgeon [9, 10]), but needs a global measure; local forms are in section 3.

## 2. The catalogue: parts by what they do in time

A small brain computes in time (`BOUNDS.md`, Time), so its parts are best sorted by what they do with time:

| family | parts | made by (feedback's sign and timescale) | here |
|---|---|---|---|
| **static maps** | gain, threshold or comparator, sum, coincidence (AND), veto (AND-NOT), winner-take-all | fast negative feedback; mutual inhibition | an eye pulse starting the hold |
| **memory** | a leaky level (analogue, fading); a latch or flip-flop (bistable, one bit); a counter or tally (a bounded integrator, a few bits); a non-volatile knob | positive feedback, or slow integration | B's doubt (a tally); the SONOS knobs |
| **change** | adaptation, a differentiator (answers a change, then returns to rest) | slow negative feedback | |
| **time** | a delay; a one-shot (an interval timed); refractoriness | a leak's time constant | B's hold |
| **time's relations** | an interval detector (a delay and a coincidence); an order or sequence detector (one channel delayed against another, then a coincidence [11]); a rate detector (a resonator) | delay and coincidence | D20's interval counters; D24's map |
| **rhythm** | a relaxation oscillator; a half-centre pair [12]; an entraining oscillator; phase reset | fast positive and slow negative feedback | B's scan |
| **selection** | priority (subsumption [13]); a mode switch | mutual inhibition, positive feedback | B's drive, run and scan |
| **for learning itself** | an eligibility trace; a knob's writer (a third factor, such as the taste); a surprise or novelty detector; a homeostat | | doubt's writer; D16's evidence gate |

**The catalogue is a grammar, not a list.** Every part above is made of feedback loops, each with a sign and a
timescale, plus delays and coincidences: fast negative feedback gives stability; positive feedback, memory and
decision; slow negative feedback, adaptation; fast positive with slow negative, rhythm; a delay with a coincidence,
order and interval. That is Tyson, Chen and Novák's sniffers (adaptation), buzzers (oscillators), toggles (switches)
and blinkers [14], the network motifs of cells [15, 16], and Sepulchre's mixed feedback (`MIXED_FEEDBACK.md`), whose
one circuit element with loops of either sign at several timescales makes each of them by its settings. A brain that
grows its own parts needs only the grammar's few elements and a way to set them, not the catalogue built in.

**Neurons themselves sort the same way**: by the bifurcation at which they start firing, into integrators (a rate
that grows from zero with the input: a memory of evidence) and resonators (firing at their own frequency, picking out
inputs at it) [17].

## 3. When: the trigger

What tells a brain that an intervention is wanted:

- **To tune**: outcomes worse than usual (D15's broadcast "better than usual"); a prediction missed (D20: the next
  pulse early or late).
- **To add**: the literature's triggers are in `RECRUITMENT.md` (Ways to recruit): a variable out of bounds
  (ultrastability), a mismatch no part answers (adaptive resonance), adjustment that has stalled while discomfort
  persists (AGENTS.md: "finished"), and structured surprise (a mismatch that repeats in a pattern: `QUESTIONS.md`,
  rhythm by mode locking).
- **To prune**, each a part's own local evidence: its output constant (always silent or always on); its output the
  same as another part's (correlated: one is spare); its effect tuned to about zero downstream; or its removal, tried
  for a while, unnoticed. Homeostatic and structural plasticity are local triggers of this kind [18, 19].
- **To modulate**: a context that changes what is wanted (one circuit, several functions, chosen by a modulator [1]).

**Choosing among interventions** is the open question. A natural order is by cost: tune first, then modulate, then
add, as Ashby's ultrastable system changes its parameters only when its essential variables leave their bounds. But
it is not known which signal says "no setting of these knobs will do; a new kind of part is needed". A tuner that has
stalled with discomfort persisting is a candidate; telling a plateau from a ceiling is the hard part.

## 4. How it is judged: the credit

This decides more than the operation does. What a change did must be judged by some signal, and these differ by
orders of magnitude in how fast they judge (this project's results):

| credit from | how fast | here |
|---|---|---|
| **the brain's own movement**: what its action did to its senses | seconds | D24: which motor turns towards which half of the eye, learned in a median 12 s |
| **a prediction missed**: the next pulse early or late | tens of seconds | D20: the body's balance, 93% of the ceiling |
| **outcomes**: the taste, meals | 10,000 to 100,000 s, against a life of 100 | D16: a steer learned from the taste only in 100,000 s lives; D15's tuner |

So **every part should be classed by the fastest signal that can tune it**, and a part is worth adding only if some
signal faster than meals can judge it, or the noise wall makes it unlearnable in a life (`BOUNDS.md`, The walls).
Exploring cause and effect round the loop (sensors, actuators, the world, sensors) is cheap where the brain reads
the consequences of its own acts, and ruinous where it waits for food. The general form of that exploration is
perturbation: a part varies its own output a little and keeps what an evaluator rewards (node and weight perturbation;
in birdsong, one circuit injects the variation and another judges it [20]). Biology makes variation cheap to explore
by keeping its parts weakly linked, so that a change in one rarely breaks the rest [21, 22].

## A universal circuit?

The user's question (2026-11-02): could one circuit do all of this, if the space is mapped with discipline? What it
would need, from the four axes:

1. **A substrate that is the grammar**: free units, each a node with loops of either sign at several timescales,
   plus delays and coincidences, whose settings make it any part of section 2. Sepulchre's element is close to this,
   and `RECRUITMENT.md`'s insight 6 (richer units need less recruitment) points the same way.
2. **Insertion that preserves function**: a recruit joins with its effect at zero, so trying it costs nothing.
3. **Triggers, local**: per section 3, including those for pruning, each from a unit's own state.
4. **Credit, local and fast**: each unit judged by the fastest signal it has access to (its own efference and the
   senses' reply, then prediction, then outcomes), so that most learning never waits for meals.
5. **A choice among interventions**: by cost, with the plateau-or-ceiling question (section 3) as its open core.

The test of the map's completeness: every working brain in this project (B, D20's balance learner, D24's steer)
should be expressible in it, its parts in the catalogue, the change that made it in the operations, and the signal
that could have tuned it in the credits. Open questions in `QUESTIONS.md`.

## References

Cited from memory, to check before relying on details.

1. E. Marder, "Neuromodulation of neuronal circuits: back to the future", Neuron 76, 2012.
2. K. O. Stanley, R. Miikkulainen, "Evolving neural networks through augmenting topologies", Evolutionary
   Computation 10, 2002.
3. S. Ohno, Evolution by Gene Duplication, Springer, 1970.
4. T. Chen, I. Goodfellow, J. Shlens, "Net2Net: accelerating learning via knowledge transfer", ICLR 2016.
5. T. Wei, C. Wang, Y. Rui, C. W. Chen, "Network morphism", ICML 2016.
6. J.-P. Changeux, A. Danchin, "Selective stabilisation of developing synapses as a mechanism for the specification
   of neuronal networks", Nature 264, 1976.
7. G. M. Edelman, Neural Darwinism, Basic Books, 1987.
8. J. Frankle, M. Carbin, "The lottery ticket hypothesis: finding sparse, trainable neural networks", ICLR 2019.
9. Y. LeCun, J. S. Denker, S. A. Solla, "Optimal brain damage", NIPS 1989 (published 1990).
10. B. Hassibi, D. G. Stork, "Second order derivatives for network pruning: Optimal Brain Surgeon", NIPS 1992 (published
    1993).
11. B. Hassenstein, W. Reichardt, the correlation detector of motion in the beetle's eye, Zeitschrift für
    Naturforschung B 11, 1956.
12. E. Marder, D. Bucher, "Central pattern generators and the control of rhythmic movements", Current Biology 11,
    2001.
13. R. A. Brooks, "A robust layered control system for a mobile robot", IEEE Journal of Robotics and Automation 2,
    1986.
14. J. J. Tyson, K. C. Chen, B. Novák, "Sniffers, buzzers, toggles and blinkers: dynamics of regulatory and
    signaling pathways in the cell", Current Opinion in Cell Biology 15, 2003.
15. R. Milo, S. Shen-Orr, S. Itzkovitz, N. Kashtan, D. Chklovskii, U. Alon, "Network motifs: simple building blocks
    of complex networks", Science 298, 2002.
16. U. Alon, An Introduction to Systems Biology: Design Principles of Biological Circuits, CRC Press, 2006 (2nd
    edition 2019).
17. E. M. Izhikevich, Dynamical Systems in Neuroscience: The Geometry of Excitability and Bursting, MIT Press, 2007.
18. G. G. Turrigiano, "The self-tuning neuron: synaptic scaling of excitatory synapses", Cell 135, 2008.
19. A. Holtmaat, K. Svoboda, "Experience-dependent structural synaptic plasticity in the mammalian brain", Nature
    Reviews Neuroscience 10, 2009.
20. I. R. Fiete, M. S. Fee, H. S. Seung, "Model of birdsong learning based on gradient estimation by dynamic
    perturbation of neural conductances", Journal of Neurophysiology 98, 2007.
21. M. W. Kirschner, J. C. Gerhart, The Plausibility of Life, Yale University Press, 2005 (facilitated variation).
22. A. Wagner, Robustness and Evolvability in Living Systems, Princeton University Press, 2005.

Also: V. Braitenberg, Vehicles: Experiments in Synthetic Psychology, MIT Press, 1984, which builds a creature's
behaviour by adding one kind of part at a time, much as this map would; D. V. Buonomano, W. Maass, "State-dependent
computations: spatiotemporal processing in cortical networks", Nature Reviews Neuroscience 10, 2009, on timing; W.
Zhang, D. J. Linden, "The other side of the engram", Nature Reviews Neuroscience 4, 2003, on intrinsic plasticity; T.
Elsken, J. H. Metzen, F. Hutter, "Neural architecture search: a survey", JMLR 20, 2019.
