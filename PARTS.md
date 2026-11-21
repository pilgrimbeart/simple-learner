# Parts and interventions

**Status, 2026-11-19.** Section 2 is the literature-informed three-part proposal for the user-approved return
to a tiny in-life learner and finite repair search. It is not a complete taxonomy or a frozen search grammar.
Other sections retain the intervention background; none authorises a new run. The current question and work order are in [PROGRAMME.md](PROGRAMME.md).
The intervention results are historical evidence in [STORIES.md](STORIES.md); each retained capability needs
a problem, mechanism, evidence and limits, as recorded in [D72](discrete/NOTEBOOK.md#review-2026-11-16).

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

A useful ordering to investigate, not a universal ranking of cost. Tuning can overwrite a skill or consume
more exploration than a protected new unit; count time, energy, storage and communication as well as parts:

| | operation | example | reversible? |
|---|---|---|---|
| 0 | **State**: what the circuit holds; can support learning if evidence changes later decisions | B's doubt | yes, fast |
| 1 | **Tune** a knob: a gain, threshold, time constant or bias | D20's balance; D15's tuner | yes |
| 2 | **Modulate**: switch an existing part into another mode | a relay neuron made an oscillator by its conductances [1] | yes |
| 3 | **Rewire**: a connection's target or sign changed, or enabled or disabled | NEAT's disable gene [2] | mostly |
| 4 | **Prune**: remove a part | one that tuning left redundant | no, unless it can regrow |
| 5 | **Duplicate and diverge**: copy a part, then let the copies specialise | gene duplication [3]; Net2Net's widening [4] | yes, at first |
| 6 | **Add** a new part from the catalogue (section 2) | D24's map counter | yes, if it starts silent |

Two ideas from the literature govern growth and pruning:

- **Function-preserving growth** [4, 5]: under the transformation's assumptions, insertion preserves the old
  input–output function. Zero initial output can help, but resource sharing, noise or timing can still change
  behaviour in a dynamical circuit. Material and computation cost from allocation, and subsequent exploration
  can reduce reward. This is not a guarantee of safe policy improvement. Sharing a duplicate's output preserves
  a sum only when the rest of the dynamics and accounting permit it. Net2Net's primary-source abstract was
  checked in this review; see [Chen, Goodfellow and Shlens](https://arxiv.org/abs/1511.05641).
- **Constructive or selective.** Grow when needed, or overproduce and keep what is used (selective stabilisation [6];
  neural Darwinism [7]; the lottery ticket [8]). The user's plan for the ideal observer (a strong meta-brain, then
  pruned: `QUESTIONS.md`, step 3) is the selective one. Pruning by what a part's removal would cost is classical in
  networks (Optimal Brain Damage and Surgeon [9, 10]), but needs a global measure; local forms are in section 3.

## 2. The catalogue: primitives, dynamical motifs and learning

**Purpose.** Enumerate a bounded language of possible repairs to a simple robot circuit, not keep adding
hand-designed capabilities to the current growing network. The user prioritises real-time, in-life learning
and dynamical circuits. Real-time means causal operation while the body acts; learning means evidence retained
in state changes later decisions during that life. An oscillator alone supplies dynamics, not necessarily learning.
A volatile or bistable memory can support learning; changing synaptic weights is not the only possible form.

There is no claim to enumerate every possible dynamical circuit or function. Exhaustiveness becomes meaningful
only after fixing a finite set of primitives, legal compositions, parameter values and a size bound. The motifs
below are a vocabulary for describing circuits, not twenty equally priced indivisible modules.

### Recommendation: three circuit-level parts

**Proposal, 2026-11-19; not a demonstrated minimal basis.** Use three kinds of circuit macro with declared
ports and internal state. A macro is a small fixed circuit contract, not an arbitrary software function.
All brain graphs use this level. Transistors implement the macros; oscillators and learning mechanisms are
assemblies above them. Neither transistors nor complete oscillators are alternative entries in this catalogue.

| part | contract | internal state and exposed controls |
|---|---|---|
| **Dynamic node** | Sum incoming currents into a leaky voltage state, with a fixed bias option. Other parts may read the voltage. | One voltage, capacitance and leak. Inputs/outputs obey rails and substrate noise. Feedback arrives through controlled connections. |
| **Controlled connection** | Read a source voltage, optionally filter it, apply a bounded saturating response, and inject signed current into a destination. A local control voltage can gate its strength. | Zero or one filter state; declared sign, current scale, threshold, slope and filter timescale. The modulation port is explicit, with its own cost. Self-connections use the same part. |
| **Retained memory node** | Integrate signed write currents into a retained voltage; expose that voltage for reading or controlling a connection. | One retained voltage plus the declared write-driver interface. Finite range, write threshold and write noise. No external parameter assignment during life. |

The first two parts package the existing mixed-feedback construction. The third exposes retained analogue
settings. The proposal is therefore **Sepulchre-style dynamics and connections, plus retained writable state**.
The extension also requires usable local modulation and write ports; memory alone does not supply a learning
rule. Positive-feedback circuits already supply bistable memory, so retained storage is a practical choice
for analogue knobs, not a theorem that Sepulchre circuits cannot remember.

All three are circuit macros even though they have different roles. A node is not a complete neuron; a
connection is not an uncounted wire. An assembled neuron and a learning synapse must expand into these same
parts. Each part instance and each internal filter state counts. Wiring/load, activity and material are
recorded separately; we postpone transistor minimisation, not the visibility of resources.

### One universal cell, or several parts?

A cell containing all three could be a convenient repeated implementation later. Calling it one primitive
would not remove its internal choices: how many currents, timescales, control ports and memories does it hold?
The three-part description leaves those quantities visible without descending to transistors. We have not
proved that three is the smallest possible vocabulary; fewer names is not an objective worth optimising now.

**Make controls connectable, and allocate memory when a parameter is to be learned.** Do not automatically
put a learner on every physical constant. For an instantiated adjustable parameter, name its controlling
voltage, bounded transfer function and write path. A frozen setting and a learned setting must be visibly
different in the circuit graph. Prefer the same memory/connection mechanism for intrinsic feedback and
between-node coupling. This leaves open a later fully populated identical-cell architecture.

The existing engine directly supports a strength gate. Bias can be changed by another input current;
feedback strength can alter effective thresholds and response times. Direct voltage-controlled changes to
`tau`, `offset` or `slope` are **not** already implemented. They require an explicit circuit construction and
bench check, or a separately reviewed macro extension. Do not mutate Python parameter arrays during a life
and call that circuit learning. Effective timing control is not identical to independent control of every
physical time constant. Whether the existing strength gate suffices is a concrete first question.

### Coverage ledger: behaviours are assemblies, not additional parts

The status column distinguishes completed restricted bench evidence from proposed construction routes. “Source” means
published evidence for a mechanism; “derivation” means the limited analytical argument below; “candidate”
means the topology still needs an instantiated witness. Reading depths and source links live in the
[focused literature review](MIXED_FEEDBACK.md#minimal-catalogue-review-2026-11-19).

| behaviour required | assembly from the three parts | present evidence and discriminating bench | current coverage status |
|---|---|---|---|
| Fading trace / leaky integrator | One dynamic node driven by a connection. | Derivation: exponential decay. Measure response and decay in seconds. | demonstrated within [D126](discrete/NOTEBOOK.md#d126-first-dynamic-witnesses) silicon bench |
| Bounded evidence accumulation | A retained node with positive/negative write paths. | Existing engine contract; demonstrate both write signs, saturation and hold under the declared memory model. | restricted writes/hold in D127; boundary/reversal audit [D129](discrete/NOTEBOOK.md#d129-memory-limits); absence-preserving writes [D131](discrete/NOTEBOOK.md#d131-absence-preserving-writes) |
| Bistable memory / hysteresis | Dynamic node with strong saturating positive self-feedback. | Derivation below. Set/reset with opposite pulses; test retention and switching under noise. | demonstrated within [D126](discrete/NOTEBOOK.md#d126-first-dynamic-witnesses) silicon bench |
| Change detector / adaptation | Fast excitation opposed by slower feedforward or integral-feedback correction. | Fixed cancellation is mismatch-sensitive; test onset, offset and sustained residual. | integral-feedback witness demonstrated in [D128](discrete/NOTEBOOK.md#d128-change-and-order); fixed-path version failed |
| Excitable pulse | Fast regenerative self-feedback opposed by slower restorative feedback. | Mixed-feedback source construction. Isolated perturbation must trigger one bounded excursion and recovery. | unbuilt |
| One-shot | Adaptive response followed by a thresholded output; excitability is a separate possible construction. | Bounded pulse per positive change, quiet under sustained input, repeated responses. Constant width and regenerative excitability are stronger claims. | bounded pulse demonstrated, 40/40 ([D132](discrete/NOTEBOOK.md#d132-one-shot)); recovery envelope measured in [D136](discrete/NOTEBOOK.md#d136-pulse-recovery); not constant-width timing |
| Refractory gate | Recovery voltage inhibits the trigger connection. | Candidate. Probe paired pulses at several separations. | unbuilt |
| Lag / approximate delay | Cascade dynamic nodes or filtered connections. | Derivation below. Measure distortion as well as latency over a declared bandwidth. Exact arbitrary delay is excluded. | unbuilt |
| Coincidence detector | Two convergent inputs into a thresholded response, or one input gating the other. | Candidate; single inputs must stay subthreshold. Sweep overlap and amplitude independently. | demonstrated as a subsystem in [D128](discrete/NOTEBOOK.md#d128-change-and-order), including large single inputs |
| Order / interval detector | Trace from A gates a B-driven path; a mirrored path distinguishes B-then-A. | Candidate. Compare both orders, absent inputs and varied separations. | unresolved:34/40 in D128; offsets and resting trace leakage |
| Resonator | Two dynamic nodes coupled with opposite signs. | Derivation below. Measure decaying oscillation and a nonzero-frequency response peak, not merely a slow filter. | demonstrated within [D126](discrete/NOTEBOOK.md#d126-first-dynamic-witnesses) silicon bench |
| Autonomous oscillator | Mixed feedback with an unstable rest state and a bounded attracting cycle. | Source construction. Persistent rhythm without periodic input; independent initial phase. | original reliability shortfall diagnosed; explicit retained bias adaptation passes fresh confirmation, with added cost ([D162](discrete/NOTEBOOK.md#d162-adaptive-oscillator)) |
| Coupled / entrained oscillator | Oscillator plus an input connection. | Source mechanisms; mapping to this catalogue pending. Measure locking range and recovery after perturbation. | unbuilt |
| Phase detector | Compare two oscillating signals through gated paths, then low-pass the result. | Measure signed local phase sensitivity, bias and phase ambiguity; never supply phase as a privileged input. | local sensitivity demonstrated, 40/40 ([D133](discrete/NOTEBOOK.md#d133-phase-response)); absolute calibration unresolved; mismatch decomposition [D137](discrete/NOTEBOOK.md#d137-phase-bias) |
| Bursting | Oscillatory assembly plus another slower feedback process. | Source construction and silicon examples. Distinguish bursts from missed/noisy spikes. | unbuilt |
| Competitive selection | Two or more driven nodes with mutual inhibition and optional self-excitation. | Candidate. Compare weak/strong/equal inputs and reversals; small local contest first, no global winner routine. | unbuilt |
| Tunable gain / effective threshold / response time | Memory voltage gates a corresponding signal, bias or feedback path. | Engine gate exists; each claimed knob needs its own transfer curve and interaction check. | partial: retained-state nonnegative modulation in D127; explicit signed control 39/40 in [D145](discrete/NOTEBOOK.md#d145-signed-control), below required reliability; threshold/timing untested |
| Adaptive regulation | A measured local response drives signed feedback onto a retained control voltage. | Candidate. Perturb the controlled circuit and measure recovery; a bench-supplied target is not an admissible body-provided learning signal. | partial: integral regulation of a circuit response in D128; no reward-directed tuning |
| Evidence-gated learning | Dynamic trace gates a taste-driven writer into retained state; that state controls a later response. | Established three-factor learning family; our useful credit signal is unproved. Compare no-write, reversed evidence and delay controls. | partial: supplied-eligibility writes in D131; D129 exposes overlap/bias limits; reward credit unresolved |
| Learned rhythm | Phase-sensitive response drives retained state controlling an oscillator. | Adaptive-frequency-oscillator source gives a known example. Our circuit mapping must show retained frequency change after input removal, not just entrainment. | unbuilt |
| Evidence-dependent competition | The learning assembly changes drive/connection strength in a local contest. | Candidate, not demonstrated Bayesian hypothesis selection. Compare learned preference, reversal and equal-evidence cases. | unbuilt |

D126 validates only the three marked rows within its [frozen protocol and results](lab/v/dynamic_parts/report.md).
D127–D133 add restricted write/readout, adaptation, coincidence, bounded-pulse and local phase-sensitivity evidence; see each linked protocol.
Order and oscillator reliability remain unresolved. Baseline-relative response measurements are observer
metrics, not an implicit reference signal supplied to a brain.
The remaining rows have construction routes, not inferred passes. This does **not** establish that a small
fixed graph, finite grid, physical noise level and life length can realise every row. There is no universal
approximation argument being used to hide the size or precision needed. A failed recipe is a gap to diagnose,
not permission to add a bespoke “order detector” or “learning module” to the grammar.

### Short constructive checks

These are our analytical checks on idealised macro equations, not noise-free simulation results. Variables
are voltages and time is in seconds; numerical values must later come from the allowed SI parameter ranges.

- **Trace:** `C dx/dt = -g x + I(t)` has decay time `C/g`. A difference of fast and slow paths with matched
  DC gains has transfer `K[1/(1+s*t_fast) - 1/(1+s*t_slow)]`, hence rejects a constant after settling.
  Mismatch leaves a residual, to be measured rather than assumed away.
- **Bit:** `C dx/dt = -g x + A*tanh(x/V_s)` has an unstable zero and two stable nonzero equilibria when
  `A/V_s > g`, provided those equilibria fit within the rails. This establishes deterministic bistability,
  not a lifetime against random switching. A bias shifts the switching thresholds.
- **Resonance:** `dx/dt = -a*x - b*y + k*u`, `dy/dt = b*x - a*y` has eigenvalues `-a ± i*b` for positive
  rates `a,b` (per second). Reading y gives `k*b/[(s+a)^2+b^2]`, with a nonzero-frequency peak if `b>a`.
  Signed connections approximate these linear dynamics over a declared small-signal range. More feedback
  can generate oscillation, but resonance alone does not prove a stable nonlinear cycle.
- **Delay:** a cascade of n equal lags has transfer `(1+s*T/n)^(-n)`, approaching delay `exp(-s*T)` as n
  grows. At finite n it attenuates and distorts; the bandwidth/accuracy/state-count tradeoff is part of the test.
- **Phase:** averaging the product of `A*cos(w*t)` and `B*sin(w*t+phi)` gives `(A*B/2)*sin(phi)` after
  rejecting the double-frequency component. A nonnegative gate requires rectification/differential paths
  to implement signed multiplication; those paths count and their approximation must be measured. No
  single periodic detector identifies unwrapped phase globally.
- **Retained update:** a trace voltage can gate a signed evidence-driven current into memory, whose voltage
  then gates a readout. This is an explicit evidence-to-memory-to-action route. It does not determine which
  trace is eligible or whether that rule improves reward in a closed loop.

### Existing-engine mapping and exposed gaps

Checked against `mixed_feedback.py` (`Circuit.node`, `Circuit.element`, `_step`) and `chip.py`, at working
revision `5700eaa0d397e1a7dc055ce69ce9ec7e1d32cc7f` on 2026-11-19; documentation was already modified. No
simulation or engine code was changed for this review.

- Dynamic node maps to `node(..., R, C, bias)`. Retained node maps to `node(..., R=None, memory=True)`;
  the write threshold and write noise are applied in `_step`. Physical implementation assumptions remain
  those in `chip.py` and the existing rules, including the already recorded memory-supply omission.
- Controlled connection maps to `element(to, frm, gain, offset, tau, slope, sigmoid, gate)`. It contains
  a filter state when `tau>0`. The gate is nonnegative and clipped, so a signed multiplier is not available
  as one primitive. A negative signal must use explicit signed/differential paths where required.
- The internal filter states currently follow deterministic low-pass updates driven by noisy node voltages.
  [D147](discrete/NOTEBOOK.md#d147-filter-state-audit) confirms missing independent filter noise.
  New witnesses must use explicit noisy nodes until physical state/noise/cost and regression checks agree;
  do not add another noise model or silently change the established substrate. Existing witnesses scanned
  in D147 use tau=0 throughout and are unaffected by this particular omission.
- No direct arbitrary parameter-control ports, arbitrary exact delay, event-history buffer, global clock,
  external winner selection or external learning update is admitted.

### Dynamical role and recovery — RNN review consequence

The [RNN literature review](MIXED_FEEDBACK.md#rnn-time-stability-review-2026-11-19) identifies direct
continuous-time RNN and gated-memory precedents. No additional part is selected. Each coverage witness must
state whether its intended behaviour is a fading response, retained state, excitable event or attracting rhythm.
These are test expectations, not types added to the construction grammar.

Alongside its existing functional test, predeclare perturbations and the appropriate recovery measure:
filters forget perturbations over a measured time; memory preserves the distinction between stored values;
excitable circuits recover after events; oscillators recover amplitude/period while allowing phase displacement.
For learnt controls, check the admissible parameter range and transitions with writes enabled as well as frozen.
Always distinguish bounded voltage, recovery of behaviour and power/activity cost. Neither saturation, gradient
clipping nor a recurrent-matrix spectral radius below one supplies a general nonlinear stability certificate.
Do not require contraction of the entire brain: that would rule out some intended memory and rhythm mechanisms.
An isolated-module result does not establish closed-loop stability after interconnection with the body.

### Bounded next work after the first witness batch

**Current queue, reviewed 2026-11-20:** follow the [programme's next diagnostic assignment](PROGRAMME.md#next-diagnostic-assignment-2026-11-20).
[D166](discrete/NOTEBOOK.md#d166-overnight-review) reviews the overnight evidence; the capability
requirements and construction gates below remain in force.

[D128](discrete/NOTEBOOK.md#d128-change-and-order) adds integral-feedback change detection and coincidence
coverage; order fails its confirmation and has reached its two-variant limit. [D129](discrete/NOTEBOOK.md#d129-memory-limits)
exposes gate-only false writes; [D131](discrete/NOTEBOOK.md#d131-absence-preserving-writes) demonstrates an
explicit no-write region with extra parts and reduced weak-signal sensitivity. [D130](discrete/NOTEBOOK.md#d130-oscillator-starting-states)
finds coexisting rest/cycle on one draw but no general startup-kick repair. [D132–D133](discrete/NOTEBOOK.md#d132-one-shot)
add bounded pulses and local phase sensitivity; phase calibration remains unresolved. Internal filtered connections,
signed learned weights and full coverage remain unvalidated. No robot search is ready.

These are small assignments for sequential work, not authorisation to launch agents. Each new construction
gets a frozen graph, SI settings, stimulus schedule, margins and noise estimate before its pilot; at most two
variants before returning to diagnosis. Budget per witness: 60 minutes construction/analysis, one pilot up to
600 s and confirmation up to 1200 s. Reuse the existing noise engine. Do not stretch budgets after a failure.

The three diagnostics below are completed in [D135–D137](discrete/NOTEBOOK.md#d135-trace-margin).
They support useful event traces despite a quietness constraint, establish a restricted pulse-recovery
envelope, and trace phase bias to mismatch in both upstream and output paths. They select no new topology.

1. **Next: offset handling and representation, not confirmation tuning.**
   [D141–D144](discrete/NOTEBOOK.md#d141-baseline-rejection) establish the signed-interaction need and
   isolate drift feedthrough. [D145–D146](discrete/NOTEBOOK.md#d145-signed-control) test a counted
   complementary-gate composition: 39/40 fresh draws, below the frozen reliability criterion. Source
   offsets and opposing-gate leakage explain its sole magnitude shortfall; large null outputs remain.
   Preserve that result. [D148–D150](discrete/NOTEBOOK.md#d148-local-zero-reference) complete the
   internal-zero reference and detector-error analysis: full cancellation can exchange one uncertain
   offset for another; nominal-prior half correction improves the conditional error model. This is not
   an implemented rule or a universal optimum. [D151](discrete/NOTEBOOK.md#d151-correction-cell-budget)
   counts a local correction kernel: its own offsets erase that nominal advantage.
   [D152–D153](discrete/NOTEBOOK.md#d152-shared-path-reversal) recover useful signal by ideal reversal,
   but show the available active reverser carries source offsets through as signal.
   [D154](discrete/NOTEBOOK.md#d154-routing-contract) finds no direct reciprocal-routing contract;
   economical composite support is unproved. Park this switching cure rather than implicitly adding
   a primitive. The order diagnosis below now identifies the missing resting-output reference. Preserve weak-event
   sensitivity and freeze any new comparison separately.
   Independently, [D147](discrete/NOTEBOOK.md#d147-filter-state-audit) resolves the hidden-filter audit:
   use explicit noisy nodes for new witnesses; specify state/noise/cost lowering and regression checks
   before any general positive-tau connection claim. No automatic engine rewrite or robot search.
2. **Order: quietness is insufficient; retain the measured tradeoff.**
   [D139](discrete/NOTEBOOK.md#d139-population-trace-margin) completes the all-draw analytic comparison
   with manufacturing and pointwise noise allowance. Raising the trace threshold loses downstream
   sensitivity, including at D135's selected-draw bound. Keep the original criteria and branch imbalance
   separate. No third threshold-only variant follows. A future local correction must explain how it
   distinguishes absence from weak events and demonstrate an adequate downstream margin before construction.
   [D155–D156](discrete/NOTEBOOK.md#d155-order-balance-information) find an informed constant balance
   sufficient for39/40 reused draws; raw coincidence-weighted calibration gives27/40, supplied-baseline
   calibration39/40. Next diagnose a continuously maintained baseline with explicit settling, event
   contamination and readout/estimator errors. Budget30 minutes analytic comparison before construction.
   The remaining draw's simultaneous and long-gap requirements conflict; balance alone cannot cure it.
   [D157–D160](discrete/NOTEBOOK.md#d157-continuous-baseline) complete that reference diagnosis:
   an ideal continuous baseline helps, readout error remains costly, and low event rates lack simultaneous
   calibration opportunities. D163 completes the1000s opportunity check: most reference performance recovers; one known capacity failure and one single-anchor calibration failure remain. D165–D166 complete that inspection: ordered events contaminate its reference. The programme now specifies selectivity, precision and existing-gain diagnostics.
   Do not select a physical baseline topology from these ideal references alone.
3. **Pulse branch: retain the measured envelope; no new variant.** D136 passes all tested development
   conditions at input-off gaps of 100 ms or more, with failures at 20/50 ms. Those gaps are not event
   periods. Use the actual durations and recovery states when composing modules. Regenerative excitability,
   an explicit refractory gate and constant-width timing remain separate unproved capabilities; do not
   build them merely to improve this table. Select a discriminating use case before reopening this branch.
4. **Memory and oscillator remaining limits.** D131 rejects weak evidence on purpose; map sensitivity and
   offset tolerance before calling its thresholds generic. Signed learned weights and autonomous eligibility
   remain open. D130 does not support fixing oscillator reliability by initial kicks; examine parameter
   regions and equilibrium structure before another oscillator variant. [D159–D162](discrete/NOTEBOOK.md#d159-oscillator-root-census)
   complete that diagnosis and justify one explicit retained bias controller. Its unchanged design passes fresh confirmation (D162), with costs and limits recorded; retain the bounded repair. No changed success threshold, hidden cost or further tuning.
5. **For each retained witness**, include removal controls, mismatch/noise, perturbed starts, appropriate
   recovery, fresh evaluation and both step halvings. Count a seed once across signs and timesteps. Record
   material, power and activity separately; show live traces. Exact quiet memory follows the established
   idle-noise assumption and must not be advertised as measured hardware retention.
6. **Only after coverage**, test whether a known one-bit repair fits a bounded module. Freeze graphs, ports,
   finite SI settings, seed sets, metrics and budget; count candidates before running the robot search.
   Keep the retuning-only comparator. A module may contain several catalogue parts; its cost stays explicit.

The completed benches establish component operations, not autonomous in-life reward learning.

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
  for a while, unnoticed. These are candidate signals, not proofs of redundancy: a constant output may matter in
  another context, and correlated units may carry distinct future roles. The locality of the complete decision
  still needs checking. Homeostatic and structural plasticity provide related mechanisms [18, 19].
- **To modulate**: a context that changes what is wanted (one circuit, several functions, chosen by a modulator [1]).

**Choosing among interventions** is the open question. A natural order is by cost: tune first, then modulate, then
add, as Ashby's ultrastable system changes its parameters only when its essential variables leave their bounds. But
it is not known which signal says "no setting of these knobs will do; a new kind of part is needed". A tuner that has
stalled with discomfort persisting is a candidate; telling a plateau from a ceiling is the hard part.

## 4. How it is judged: the credit

This decides more than the operation does. What a change did must be judged by some signal, but how fast depends on
the signal *and the question put to it*, in bits to learn over bits per second (rough sums from this project's results;
balance from its median error at birth):

| what was learned | bits | signal | time | bits/s |
|---|---|---|---|---|
| which motor turns towards which half of the eye (D24) | 1 | the brain's own movement | 12 s | 0.08 |
| which colour is food (D25) | 1 | taste, while driving | 1.5 s | 0.7 |
| the body's balance (D20) | ~2 | what comes round again in its sweeps | 140 s | 0.014 |
| the body's balance (D15) | 1.4 | meals | 10,000 s | 0.00014 |
| a spending knob, 8% apart (D15) | | meals | about 4,000 s a comparison | below the wall in a life of 100 s |

This corrects an earlier form of this section, which ranked signals (own movement, prediction, outcomes) and concluded
that a part must be judged faster than meals. Taste settles the colour faster than anything else here, because the
effect is large and one meal can say nearly all of it; D16's 10,000 s was the learners' limit, not the signal's
(`BOUNDS.md`, How long a life must be). So **judge a candidate by its own effect's signal to noise per second**, against
the life and its number of rivals (`BOUNDS.md`, The walls). Exploring cause and effect round the loop (sensors, actuators, the world, sensors) is cheap where the brain reads
the consequences of its own acts, and ruinous where it waits for food. The general form of that exploration is
perturbation: a part varies its own output a little and keeps what an evaluator rewards (node and weight perturbation;
in birdsong, one circuit injects the variation and another judges it [20]). Biology makes variation cheap to explore
by keeping its parts weakly linked, so that a change in one rarely breaks the rest [21, 22].

## 5. Why: what each intervention moves

The operations above say how a brain changes; this says why. A chain runs from hidden facts Z to history H (senses, beats,
tastes), memory M, action A and value V, and an intervention can act on only so many terms. A working hypothesis, tried
on ten rows (`STORIES.md`, the table), where Immunise and Spend never won; each trigger as tested there:

| class | what it changes | example | trigger |
|---|---|---|---|
| **Sense** | I(Z;H), moving in order to learn | D20's sweeps | Z uncertain and worth knowing |
| **Store** | I(Z;M), keeping more of H | B's doubt, the hold | the past predicts outcomes beyond M: I(V;H\|M) > 0 |
| **Use** | what A does with M | rung 1's bridge, the balance | M predicts a bad outcome anyway: I(V;M\|A) > 0 |
| **Immunise** | V's dependence on Z | D5's "drive only while you see it" | V steep in Z, and no signal shows Z |
| **Judge** | how well evidence is credited | D25's write while driving; one coin per burst | evidence counted that says little |
| **Spend** | the same V for less | pruning, power gating | I(part;A\|rest) about 0 |

## A universal circuit?

The user's question (2026-11-02): could one circuit do all of this, if the space is mapped with discipline? What it
would need, from the four axes:

1. **A substrate that is the grammar**: free units, each a node with loops of either sign at several timescales,
   plus delays and coincidences, whose settings make it any part of section 2. Sepulchre's element is close to this,
   and `RECRUITMENT.md`'s insight 6 (richer units need less recruitment) points the same way.
2. **Insertion that preserves function**: a recruit initially changes behaviour as little as possible, with its
   allocation, activity and later exploration costs still counted.
3. **Triggers, local**: per section 3, including those for pruning, each from a unit's own state.
4. **Credit, local and informative**: each unit judged by a signal that distinguishes the alternatives relevant
   to its action. A fast signal is useful only if it supplies that evidence; no fixed ordering of sensory,
   predictive and reward signals is established.
5. **A choice among interventions**: by cost, with the plateau-or-ceiling question (section 3) as its open core.

The test of the map's completeness: every working brain in this project (B, D20's balance learner, D24's steer)
should be expressible in it, its parts in the catalogue, the change that made it in the operations, and the signal
that could have tuned it in the credits. Open questions in `QUESTIONS.md`.

## References

These were originally cited from memory. The 2026-11-16 review checked Net2Net's primary-source abstract and
qualified its use above; it did not verify this entire bibliography. Check the primary text and assumptions of
any other mechanism before relying on it. The catalogue and information-based triggers are this project's
working hypotheses, not results proved by the cited papers.

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
