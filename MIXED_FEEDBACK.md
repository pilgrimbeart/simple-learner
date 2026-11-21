# Mixed feedback

**Status, 2026-11-16.** This is background and a source of candidate mechanisms. The core paper's
[primary record](https://arxiv.org/abs/2011.04441) supports multiscale mixed feedback as a circuit design and
control approach. It does not establish this project's autonomous learning or economical growth goal. The
research priorities live in [PROGRAMME.md](PROGRAMME.md); the suggestions below are historical proposals.
The original reading-depth statement below remains applicable. This review did not reverify every reference
or update the survey into an exhaustive account of the field.

What the "mixed-feedback" approach of Rodolphe Sepulchre and colleagues is, what is new and valuable in it, what is
not, and what it suggests for this project. Written from a literature search in October 2026. The core paper
(Ribar and Sepulchre 2021) was read in full; most others from their abstracts or summaries, so details of those
should be checked against the papers before relying on them. References are numbered at the end.

## In one paragraph

Engineering has kept positive and negative feedback apart: negative feedback for robust, linear, analog regulation
(Black's amplifier), positive feedback for switches, memory and clocks (latches, oscillators, digital logic).
Nervous systems don't separate them: in every neuron, fast positive feedback (sodium) makes a discrete event, a
spike, and slower negative feedback (potassium) ends it and keeps it regulated. Sepulchre's group argues that this
**interlocking of positive and negative feedback at separated timescales** is a control principle in its own right,
and the reason neurons are at once digital (spikes are reliable, countable events) and analog (thresholds, rates and
rhythms are continuously tuned), robust to sloppy parts and easy to modulate. They turn it into a design method: a
circuit is a capacitor in parallel with a few identical elements, each giving positive or negative feedback in one
voltage window and one timescale, and a behaviour (resting, spiking, bursting, rebound, rhythm) is designed by
shaping the circuit's current-voltage curve as seen at each timescale [1, 2, 3].

## The building blocks

The circuit of [1, 3] (their Figure 3), which `mixed_feedback.py` follows:

- **A node**: a capacitor C in parallel with a *passive* resistive element whose current rises with voltage
  everywhere (dI/dV > 0: a leak; the "monotone backbone"), plus any injected current.
- **A feedback element**: a current into the node, a static saturating function of a low-pass filtered voltage,
  `I = ±α tanh(Vx − δ)`, `τx dVx/dt = V − Vx`. α sets its strength, δ the voltage window where it acts, τx its
  timescale, the sign whether it is a negative conductance (positive feedback) or a positive one (negative feedback).
  Every element is **localised in amplitude** (tanh saturates outside its window) and **localised in time** (one τ).
- **A synapse**: the same element reading another neuron's voltage, with a sigmoid: `I = α S(β(Vx − δ))`, excitatory
  or inhibitory by the sign of α [1, eq. 17]. The only difference between an ion channel and a synapse is whose
  voltage it reads. Resistive (gap-junction) couplings between nodes are also allowed.
- **In hardware**, both are standard subthreshold parts of Mead's neuromorphic engineering [4]: the
  transconductance amplifier, whose output current is `ib tanh((v1 − v2)/2v0)` with its gain ib set by a bias
  voltage, and the follower-integrator (the same amplifier driving a capacitor), whose time constant is set by its
  bias [1]. So each element is a voltage-controlled current source with a programmable gain.

Elements are grouped by sign and timescale: fast (as fast as the membrane, often instantaneous), slow, ultra-slow,
with `τ_fast ≪ τ_slow ≪ τ_ultraslow`. A neuron is named by which of `I−f, I+s, I−s, I+us` it has.

## What is new

### 1. Positive feedback is a design element, not a hazard

The historical split [1, sidebar "Positive and negative feedback"]: negative feedback became the basis of robust
design with unreliable parts; positive feedback was confined to bistable switches and oscillators. A static
saturating plant shows the continuum: negative feedback linearises it and lowers its sensitivity; positive feedback
raises sensitivity until, at a critical gain, it becomes ultrasensitive, and beyond it bistable (hysteresis: a bit).
Excitable systems live on this continuum, with positive and negative feedback present together but acting at
different speeds [1, 5]. The claim is that the mix, not either alone, gives robustness and flexibility together.

### 2. Behaviour is read off current-voltage curves at each timescale

Because currents add (the elements are in parallel) and timescales are separated, the circuit can be analysed one
timescale at a time with slower currents frozen. Define the I-V curve at timescale τx as the passive curve plus every
element as fast as τx or faster. Then [1]:

- **Excitable** (one spike per input pulse above threshold): the fast I-V curve is N-shaped (a window of negative
  conductance: fast bistability) and the slow I-V curve is monotone (negative feedback restores it).
- **Spiking**: the same, with the resting point inside the negative-conductance window.
- **Bursting**: the same motif repeated one level slower: an N-shaped slow curve (slow positive feedback, `I−s`) and
  a monotone ultra-slow curve (`I+us`), with the slow threshold below the fast one.
- **The rest-spike transition** (Hopf or saddle-node, so a discontinuous or continuous frequency curve) is set by
  whether the fast and slow curves' turning points line up.

This turns nonlinear design into something like classical loop shaping: each element shapes one curve in one
window, and the conditions are graphical. The Hodgkin-Huxley model, linearised, has exactly this structure (sodium
activation: fast negative conductance; sodium inactivation and potassium: slow positive) [1]. Bursting neurons
repeat it slower (calcium: slow negative; calcium-activated potassium: ultra-slow positive) [1, 6].

### 3. Spikes are mixed signals: physical system and automaton at once

Digital control separates physical systems (continuous) from automata (discrete), joined by clocks and
quantisers. A spike is both: a continuous-time physical trajectory that can also be counted as a discrete event [2,
7]. Fast positive feedback gives the event digital reliability (its timing is precise and survives noise), slow
negative feedback gives analog regulation. Neurons combine analog adaptation with digital reliability, without a
clock, which is what Sarpeshkar argued is the efficient regime for noisy hardware [8]. Recent work extracts
discrete-event (automaton) models from the continuous circuits [9] and adapts describing functions and phase
response curves to excitable systems via an operator from input event trains to output event trains [10].

An early demonstration: the "neuron servo" of DeWeerth, Nielsen, Mead and Åström (1991), a PD controller whose
output drove a motor through two spike generators, acted like pulse-width modulation at high speed and like a
stepper motor at low speed, where each pulse carried enough energy to overcome static friction that defeated the
analog controller [1].

### 4. Robustness through balance, not precise parts

The behaviour depends on the *balance* of positive and negative conductance in each timescale and voltage window,
not on any single parameter, which gives a highly redundant tuning mechanism robust to large uncertainty in each
element [1, 11]. This matches neurophysiology's degeneracy: similar activity from very different conductance mixes
(Prinz, Bucher and Marder 2004 [12]), and firing rates robust and tunable because many channels contribute to the
same feedback [11]. For analog chips, where transistor mismatch has been the field's main hurdle for decades, this is
the selling point: "turn the variability of transistors into a feature rather than a hurdle" [1]. A 180 nm silicon
neuron built on the architecture (three timescales, current mode) reports robustness across currents and temperatures
[13]; earlier, robust switching between spiking modes in resistor-capacitor-transistor circuits [14] and SPICE
simulations of weak-inversion transistor circuits [3].

### 5. Modulation is control

The natural control inputs are the elements' maximal conductances (α), which is exactly what neuromodulators change
in real neurons. So neuromodulation is controller design, "loop shaping" of the feedback balances [1, 3, 15]:

- **One parameter switches the kind of behaviour.** The slow negative conductance (`I−s`) alone moves a neuron
  between slow spiking and bursting (through a pitchfork at the aligned thresholds) [1, 6]. Many textbook bursting
  models lack any slow negative conductance, which is why they cannot reproduce this transition [1].
- **Nodal mode and network mode.** A slow-spiking neuron relays each input spike (nodal mode); a bursting one ignores
  single spikes and joins the network's slow rhythm (network mode) [1]. In a population, a switchable slow cellular
  conductance turns network rhythms on and off largely independently of size and connectivity, decoupling fast
  global state switches from slower tuning by plasticity or homeostasis [16]; positive feedback at the cellular level
  makes circuit rhythms both robust and modulable [17].
- **Functional topology without rewiring.** In a five-neuron network modelled on the crab stomatogastric ganglion,
  switching nodes between modes connects and disconnects whole rhythms, changing the network's functional topology
  while its wiring stays fixed [1, 18].
- **Intrinsic as well as synaptic.** Artificial neural networks control synaptic weights; these papers argue that the
  modulation of each node's intrinsic feedback balance is an equally powerful lever [1].

### 6. Networks from the same motif

Post-inhibitory rebound (a spike or burst on release from inhibition, from a slow negative conductance active at low
voltage) lets two mutually inhibiting neurons make an anti-phase rhythm though neither oscillates alone (the
half-centre oscillator) [1, 17]. Generalised: all-to-all inhibition between rebound-excitable neurons gives
winner-take-all dynamics, a discrete state machine whose transitions are continuously tunable, used to design
central pattern generators with adaptive phase and frequency [19] and proposed as the "rebound winner-take-all"
motif of a scalable event-based control architecture, demonstrated on a snake robot [20]. The same mixed feedback in
space (short-range excitation, longer-range inhibition) as well as time gives a model of excitability across scales,
from cells to population events [21]. A pendulum controlled by event-based actuation and sensing (a rhythmic
automaton plus a regulator of event timing) shows the approach on a physical plant [22].

### 7. A theory to go with it

- **Maximal monotonicity** generalises passivity to nonlinear, incremental behaviour, and links circuit physics,
  convex optimisation and feedback theory. A negative-conductance element is not monotone, but it is the *difference*
  of two monotone operators, so a spiking circuit is a monotone backbone with a few localised, disciplined departures
  from it [2, 23].
- **Dominance theory** (p-dominance, differential dissipativity) generalises stability to systems whose long-run
  behaviour is low-dimensional: 1-dominant systems have equilibria or limit cycles only, giving tools for
  multistability and oscillation [24].
- **Simulation.** Monotonicity also gives algorithms: operator-splitting methods whose structure mirrors the circuit's,
  proposed as better than conventional ODE integration for multiscale neuromorphic events [25].
- **Estimation.** Conductance-based models are linear in their maximal conductances, so adaptive observers can learn
  them online from voltage (recursive least squares, with contraction-based guarantees) [26].

## What is not new

- The parts: subthreshold amplifiers and follower-integrators are Mead's, from the late 1980s [4]; silicon neurons
  date from Mahowald and Douglas 1991.
- Excitability as fast positive and slow negative feedback: FitzHugh-Nagumo (1961-62), and Hodgkin-Huxley before it;
  bursting as a slower copy: Hindmarsh-Rose (1984) and the classic bursting literature.
- Half-centre oscillators (Graham Brown, early 1900s), post-inhibitory rebound, and neuromodulation as the source of
  circuit flexibility (Marder and colleagues over forty years [12, 15]).

What is new is the synthesis: a single element type, localised in voltage and time, as the universal component; the
classification of every current by sign and timescale; I-V curves per timescale as the design tool; modulation of
feedback balance as the control input; and a control theory (monotonicity, dominance) under it. The claim is less "a
new circuit" than "a way to design circuits that are digital and analog at once, and robust because they are
balanced rather than precise".

## How mixed-feedback is different from today's classic deep learning approach

Deep learning [37] and mixed feedback both descend from neurons, but took opposite halves of them.

| | deep learning | mixed feedback |
|---|---|---|
| the unit | a fixed, memoryless nonlinearity (ReLU, sigmoid) | a node with its own dynamics: positive and negative feedback at several timescales |
| signals | numbers, passed in layers or steps | continuous voltages and spikes: events in continuous time, no clock |
| time | discrete steps; memory added as explicit state (recurrence, attention over a context) | intrinsic: every element has a timescale, and memory is held in slow variables and bistability |
| where adaptivity lives | synaptic weights only; the neuron never changes | intrinsic conductances as much as synapses: modulating one changes the *kind* of behaviour (relaying or bursting), not just a gain |
| how it is set | gradient descent on a loss, offline, over huge data | designed by shaping I-V curves, and tuned by modulation; no general learning method yet |
| noise and imprecision | needs precise arithmetic (reduced precision is an engineering trick) | robust through balance, so noisy, mismatched analog parts are acceptable |
| hardware | digital, clocked, energy-hungry (GPUs) | subthreshold analog: currents and charge do the arithmetic, at very low power |
| understanding | behaviour spread over millions of weights | each element has a meaning (positive or negative feedback, in one window, at one timescale) |
| what it does today | vision, language, games, at scale | small circuits: spiking, bursting, rhythms, event-based control of simple plants |

The main differences:

- **Neurons that compute, not just sum.** In deep learning the neuron is a fixed function and everything learned is a
  weight. In mixed feedback the node is itself a small dynamical system that can switch between qualitatively
  different behaviours, so much of the computation and adaptation is inside the nodes [1].
- **Events and analog regulation at once.** Deep learning is digital throughout. Mixed-feedback circuits make
  discrete, reliable events (spikes, bursts, winner-take-all decisions) from continuous physics, and keep the
  continuous tuning of their thresholds and rhythms [2, 20].
- **Robust by construction rather than by precision.** Deep networks rely on exact arithmetic for training and
  inference. Mixed-feedback behaviour depends on a few balances with wide margins, which is what makes noisy analog
  hardware usable at all [1, 13].
- **Time is native.** A deep network sees time only as a sequence of steps or a window of context. A mixed-feedback
  circuit lives in continuous time, and its timescales (fast, slow, ultra-slow) are its structure.

Spiking neural networks sit between the two: they use spikes and are trained by gradient descent (with "surrogate
gradients" smoothing over the spike's discontinuity [38]), but their neurons are usually simple leaky integrate-and-fire
units and adaptation is still in the weights, so the intrinsic, mixed-feedback half is mostly absent.

The honest comparison runs the other way too. Deep learning has a general, scalable learning method and solves real
problems at scale; mixed feedback has a design method and robust small circuits, but no general way for a circuit to
learn. Gradient descent is awkward here: the behaviours that matter (a spike, a switch to bursting) are bifurcations,
where gradients are discontinuous or huge. That gap is what this project's two routes address: a brain that grows and
learns by local rules, and circuits shaped by evolution, which needs no gradients.

## Learning: what the literature covers, and what it doesn't

**Historical October survey; qualified by the [November catalogue review](#minimal-catalogue-review-2026-11-19) below.**

- **Modulation, not learning.** In these papers the conductances are set by a designer or an external controller
  (neuromodulation); the circuits show *what modulation can do*, not how a circuit could find good settings itself.
- **Estimation.** Adaptive observers learn a circuit's conductances from its voltage [26]: system identification,
  not learning a task.
- **Adaptive sensitivity in decisions.** Franci, Leonard and colleagues' nonlinear opinion dynamics use the same
  saturating feedback, with state feedback on an "attention" parameter that adapts sensitivity [27].
- **Bursting and plasticity.** Drion's group finds that switching a network from tonic firing to bursting pulls
  synaptic weights into an attractor set by the plasticity rule, a controllable consolidation stage [28].
- **What I could not find**: a mixed-feedback circuit that learns a task from reward within its lifetime, or any
  evolution or automatic design of Ribar-Sepulchre circuits. This project works in that gap: the designed circuit (a
  three-factor rule built from the same elements, learning from one taste signal, though fragile to mismatch) and the
  minimal circuit search's circuits, found by optimisation, which learn under biological noise and mismatch.

<a id="minimal-catalogue-review-2026-11-19"></a>
## Focused review for the minimal catalogue (2026-11-19)

The [three-part proposal and coverage obligations](PARTS.md#2-the-catalogue-primitives-dynamical-motifs-and-learning)
own the current design recommendation. This section owns the source assessment. We read the indicated
full-text sections, not every paper in full. This is a targeted review, not a systematic review or a priority claim.

| primary source and reading scope | finding that affects the choice | assumptions and limitation for this project |
|---|---|---|
| [Ribar & Sepulchre, *Neuromorphic Control* (2021)](https://arxiv.org/pdf/2011.04441), equations 3–8, excitability/bursting construction, equations 16–19 and modulation section, PDF pp. 5–22 revisited | Filtered saturating currents implement feedback and intercell connections. Changing their strengths changes dynamical regimes. Retain this common connection mechanism. | The graphical construction uses timescale separation. Controllable dynamics do not supply a task-specific reward-learning rule. This is the 2021 framework, not a claim about every later Sepulchre paper. |
| [Mendolia et al., *A Neuromodulable Current-Mode Silicon Neuron…*](https://arxiv.org/pdf/2512.01133), April 2026 version, §3.2 and conclusions | Fabricated circuits demonstrate spiking, bursting and modulation between them. The mixed-feedback basis has hardware evidence. | Different process/circuit from ours. Measured regimes use neuron-specific biases; mismatch yield is assessed by simulation of a revised design. Do not import power numbers or assume identical-bias robustness. |
| [Hasler, Diorio, Minch & Mead, *Single Transistor Learning Synapses*, NIPS 1994 proceedings](https://papers.nips.cc/paper/1994/file/934815ad542a4a7c5e8a2dfa04fea9f5-Paper.pdf), pp. 1–4, array and write/read description | Retained analogue storage, signal weighting and electrical updates are established circuit functions. Memory is not a new invention required by our catalogue. | Particular learning depends on surrounding circuitry; measurements use additional programming voltages. Not a free one-transistor implementation of our whole learner, nor a replacement for the existing SONOS contract. |
| [Righetti, Buchli & Ijspeert, *Dynamic Hebbian learning in adaptive frequency oscillators* (2006)](https://robotcub.org/misc/papers/06_Righetti_Buchli_Ijspeert.pdf), §2.1–2.2 equations and convergence assumptions | An oscillator can adjust a retained frequency variable through a phase-sensitive input interaction. Provides a concrete learned-rhythm comparison. | Hopf example uses oscillator state and an explicit update, with perturbation assumptions; multiple frequencies can select a component. Our mixed-feedback circuit must construct the corresponding signal rather than receiving phase or frequency from outside. |
| [Florian, *Reinforcement Learning Through Modulation of Spike-Timing-Dependent Synaptic Plasticity* (2007)](https://www.florian.io/papers/2007_Florian_Modulated_STDP.pdf), §2.1–2.2 | Eligibility storage and reward-modulated parameter writing are established online-learning mechanisms; distinguish fading eligibility from retained weight. | Derivation uses a stochastic policy, a particular local eligibility estimator, timescale conditions and shared reward. A generic activity trace times taste does not inherit its convergence argument. Delivering feedback locally at scale remains our responsibility. |
| [Mills, National Semiconductor AN-46, *The Phase Locked Loop IC as a Communication System Building Block* (1971)](https://www.ti.com/lit/an/snoa651/snoa651.pdf), basic operation, equations 1–5 | A multiplier followed by low-pass filtering supplies phase comparison; a controlled oscillator closes the loop. No need to make a whole phase-locked loop a primitive. | Sinusoidal operating argument; finite capture range, ambiguity and gain matter. Our nonnegative gate requires a constructive signed-signal implementation. |
| [Burger, Shahhosseini & Sepulchre, *A memristive model of spatio-temporal excitability* (2025 preprint)](https://arxiv.org/pdf/2505.22269), introduction and model motivation | A common history-dependent conductance description for internal currents and connections is an existing research direction. | “Memristive” here refers to state-dependent conductance, not automatically nonvolatile parameter retention or autonomous reward learning. We did not verify all later model results. |
| [Wu & Sepulchre, *A Scale-Space Theory of Memory* (9 Nov 2026 preprint)](https://arxiv.org/html/2611.12316v1), introduction/contribution statements | Distinguishes useful constraints on retained history from the mere existence of state; relates relaxation memory to first-order lags. | Its stated approximation result concerns nonlinear relaxation memory under additional conditions. It is not completeness for all dynamics or a finite noisy circuit-size bound; no proof audit performed here. |
| [Haag et al., *Mixed-signal implementation of feedback-control optimizer…* (2026 preprint)](https://arxiv.org/html/2603.24113v1), methods §II-A–C and conclusion | Feedback-driven local updates are an active hardware research direction and a close alternative to reward-modulated plasticity. | This experiment supplies target spike trains and calculates updates on a host computer. It is not evidence that the chip autonomously learns from our scalar taste signal. Useful comparator, not an admissible shortcut. |

**Choice and closest alternatives.** Recommend mixed-feedback nodes/connections with explicit retained storage.
A fully equipped universal cell is a packaging alternative, not yet a smaller design. Bistable feedback could
replace some retained memories, but analogue retention range, precision and activity would then need comparing.
Adaptive oscillators and eligibility-based learning are benchmark assemblies to express, not additional primitive
types. Supervised feedback-control learning needs a target unavailable at our interface. A general reservoir or
universal-approximation theorem would not by itself demonstrate compact local in-life learning, so neither is
being used as a completeness argument. A memristive formulation may unify notation without eliminating state.

**What this project would add if successful.** A bounded, reproducible construction grammar whose measured
repairs work in the same noisy embodied interface, followed by an explanation of what reusable local changes
produce adaptation. We are not claiming invention of any constituent memory, oscillator, gate or learning rule.

**Correction to the October survey above.** Its “what I could not find” is a historical search result, not a
claim that the literature contains no online mixed-feedback learning. The new review narrows the question to
which published mechanisms can be realised entirely inside this brain, with its actual observations and costs.

<a id="rnn-time-stability-review-2026-11-19"></a>
## RNNs: time, stability and online learning (2026-11-19)

**Conclusion.** The proposed catalogue is closely related to continuous-time recurrent neural networks
(CTRNNs), not a new class of recurrent dynamics. Existing work provides temporal models, stability tools,
gated storage and online learning. The project's open question is how to assemble economical local in-life
adaptation under its actual sensory, feedback and physical constraints. No claim of novelty follows from
combining recurrence, time constants and memory. The [catalogue](PARTS.md#2-the-catalogue-primitives-dynamical-motifs-and-learning)
owns construction choices; [D125](discrete/NOTEBOOK.md#d125-rnn-time-stability) owns this investigation's record.

### How time is represented

- **Ordinary discrete RNN:** the recurrent update is applied once per token, sample or event. In the simple
  form `h_next = tanh(W*h + U*u + b)`, the update index does not itself specify seconds. Two identical event
  sequences with different gaps are indistinguishable unless time enters through sampling, elapsed-time
  inputs or dynamics between events. A fixed sampling interval supplies an implicit time scale.
- **Continuous-time RNN:** state evolves between observations. A familiar leaky form is
  `tau_i * dh_i/dt = -h_i + sum_j W_ij*sigma(h_j + theta_j) + input_i(t)`.
  This is a dimensionless neural notation with `tau_i` measured in seconds. The physical catalogue uses
  capacitor current balance with explicit volts/amperes instead. Source nonlinearities, edge filters and
  gates make the exact topology differ, but do not remove the mathematical connection.
- **Gated recurrence:** LSTM stores an additive state behind write/read gates. The later forget-gate version
  controls retention. For fixed gate value `0<f<1` and interval `dt`, the homogeneous recurrence
  `c_next=f*c` has effective decay time `-dt/log(f)` (our algebraic interpretation). Holding f fixed while
  changing the sampling interval changes its physical memory time. State-dependent gates need not have one
  constant timescale. The original and forget-gate papers are distinct sources below.
- **Variable-time-constant models:** liquid time-constant networks explicitly modulate the effective decay
  rate using state/input-dependent conductances. This is a close alternative for controllable circuit timing,
  not proof that our engine already implements every such conductance. Their published training uses BPTT.

A numerical integration step is an approximation parameter, not the circuit's clock. For a leaky node with
held forcing, the retention factor is `exp(-dt/tau)`. Forward Euler instead uses `1-dt/tau`; even the simple
unforced leak numerically oscillates for `tau<dt<2*tau` and diverges for `dt>2*tau`, although its exact solution
only decays. This is our elementary diagnostic example, not a newly measured failure. Retain all existing
step-refinement requirements. A timestamp or clock supplied in a paper does not authorise a new body signal.

### “Stable” does not mean one thing

**Bounded activity:** signals remain finite. Saturating outputs, restoring currents and physical rails help,
but bounded systems can still oscillate, switch between attractors or behave chaotically. For example,
`h_next=tanh(-2*h)` remains bounded yet has an attracting sign-alternating two-cycle: its magnitude solves
`a=tanh(2*a)` with `a>0`. This is an analytical counterexample to equating saturation with settling.

**Contraction:** two trajectories under the same input approach each other. Miller & Hardt enforce this
for recurrent models; Lohmiller & Slotine provide continuous-time tools. For an autonomous bounded system,
global strict contraction rules out competing persistent memories and autonomous periodic orbits. A contracting
system can still follow a periodic *input*. It can also retain useful transient information; convergence does
not mean immediate forgetting. It is an appropriate candidate property for some filters, not a rule for the
whole brain. A guarantee conditional on fixed weights does not automatically include the learning dynamics.

**Energy descent:** Hopfield's continuous model uses symmetric couplings and monotone responses to make a
Lyapunov function decrease under fixed inputs. This can permit several stable memories while excluding
nonstationary recurrent motion in that model. The energy is a mathematical function, not electrical energy
consumption. Delays, arbitrary asymmetric coupling, changing weights and noise require separate analysis.

**Stable rhythm:** a perturbation away from an attracting cycle can decay while a phase displacement persists.
An autonomous oscillator need not return to the same time-indexed trajectory; that would impose a clock it
does not have. Assess recovery of amplitude and period separately from phase shift/drift. Stable rhythms are
intended behaviours in this project, not instability failures.

**Trainable gradients:** avoiding exploding/vanishing derivatives concerns learning calculations. Gradient
clipping limits an optimiser's update; it does not certify the forward circuit's dynamical stability. Gates or
orthogonal recurrent matrices likewise do not by themselves guarantee convergence to a fixed point.

**Closed-loop behaviour:** even a well-behaved module may participate in an unstable feedback loop when joined
to other modules or to the body. Conversely, useful switching may be induced by input. Stability claims must
name the inputs, parameter range, connected system and whether learning is active. A simulation trace alone
cannot prove a global guarantee; common-noise paired trajectories and independent-noise trials address
sensitivity and repeatability differently. These are proposed diagnostics, not changes to the noise model.

### Reservoirs and stabilising feedback

An echo-state reservoir is designed to lose dependence on its starting state when driven by an admissible
input history. Its transient state retains input information for a learned readout. It is a useful fading-memory
comparator, not a complete recipe for retained learning. The familiar rule “scale the recurrent matrix so its
spectral radius is below one” is not a general nonlinear guarantee: Yildiz, Jaeger & Kiebel provide counterexamples.
A matrix-norm contraction bound is stronger and conservative; the input domain and full transition map matter.

Sussillo & Abbott's FORCE learning is particularly relevant to the oscillation question: trained feedback can
turn chaotic activity into a desired coherent pattern, including oscillation. Their RLS implementation uses a
matrix of activity correlations and a target trajectory, and the paper describes failure conditions. It is an
informed comparator, not a local taste-driven learning rule we can silently import. Stabilising an operating
trajectory is also different from removing every other attractor.

### Learning while running already has a literature

RTRL computes recurrent sensitivities forward in time rather than replaying an entire trajectory backwards.
The original dense algorithm has nonlocal information requirements and roughly cubic storage and quartic
per-update work in neuron count. It establishes online recurrence learning as prior art, but is a poor direct
fit to this project's locality/economy requirement. It is still a possible small-network reference if needed.

Jaeger's 2002 reservoir work explicitly includes online RLS readout adaptation. E-prop instead combines
forward local eligibility traces with learning signals approximating otherwise unavailable credit. The
2019 precursor read here still has task-dependent learning-signal pathways, and some reported experiments
apply accumulated updates after trials; an online-computable formula is not evidence that every experiment
updates continuously. The 2020 paper's primary abstract/figure captions were checked, not its inaccessible
full text. Do not transfer a theorem or an experimental protocol between these versions without checking.

The architecture/training distinction matters throughout: continuous state evolution is not necessarily
parameter learning; fixed-weight state can nevertheless retain acquired information and change behaviour.
BPTT is a training method, not a mandatory property of RNNs. An offline-trained or evolved circuit can learn
within a life through its states; a self-modifying circuit must additionally expose all of its update machinery.
Our requirement is the actual in-life behaviour and information path, not a claim that existing RNNs cannot learn online.

### Sources, reading depth and limits

Primary papers were read at the indicated scope; no exhaustive survey or complete proof audit is claimed.

| source | checked scope and why it matters |
|---|---|
| [Beer (1995), *On the Dynamics of Small Continuous-Time Recurrent Neural Networks*](https://doi.org/10.1177/105971239500300405) | Publisher abstract only this turn: small CTRNN dynamical regimes and bifurcations. Do not claim a full reread. Existing evolutionary-robotics notes below remain relevant. |
| [Funahashi & Nakamura (1993)](https://doi.org/10.1016/S0893-6080(05)80125-X) | Primary abstract: finite-time trajectory approximation with hidden units and suitable initial condition. Not a compact noisy-circuit bound or a learning rule. |
| [Hochreiter & Schmidhuber (1997), *Long Short-Term Memory*](https://deeplearning.cs.cmu.edu/S23/document/readings/LSTM.pdf) | Introduction and §4 memory-cell construction: retained additive state with multiplicative input/output gates; motivation concerns gradient propagation. No universal forward-stability guarantee. |
| [Gers, Schmidhuber & Cummins (2000), *Learning to Forget*](https://doi.org/10.1162/089976600300015015) | Publisher abstract checked: forget gates address continual streams without prescribed resets. Author PDF text extraction was unreadable; no full-text claim. |
| [Hasani et al. (2021), *Liquid Time-constant Networks*](https://arxiv.org/pdf/2006.04439) | Model equation, training description and §4 bounds. State/time-constant boundedness is not a theorem excluding oscillation or chaos. |
| [Miller & Hardt (2019), *Stable Recurrent Models*](https://arxiv.org/pdf/1805.10369) | §2 contractivity definition and RNN/LSTM sufficient conditions; §3 finite-context approximation. Applicable assumptions must survive gating and adaptation. |
| [Lohmiller & Slotine (1998), *On Contraction Analysis for Nonlinear Systems*](https://www.mit.edu/~nsl/preprints/contraction.pdf) | §2 Jacobian symmetric-part bound and contraction-region assumptions. Deterministic convergence result, not automatically a stochastic guarantee. |
| [Hopfield (1984), graded-response neurons](https://redwood.berkeley.edu/wp-content/uploads/2018/08/hopfield84.pdf) | Circuit equation and energy derivative, equations 5–10. Symmetry and fixed inputs are essential to this argument. |
| [Jaeger (2001), echo-state report](https://www.ai.rug.nl/minds/uploads/EchoStatesTechRep.pdf) and [Yildiz, Jaeger & Kiebel (2012)](https://www.ai.rug.nl/minds/uploads/2519_Yildizetal12.pdf) | Original report accessed; rely on the later paper's §2 corrected definition and §3 counterexamples. Separate erratum download failed; its correction is discussed in the later paper. |
| [Jaeger (2002), *Adaptive Nonlinear System Identification with Echo State Networks*](https://papers.nips.cc/paper_files/paper/2002/file/426f990b332ef8193a61cc90516c1245-Paper.pdf) | Reservoir/readout setup and online adaptation discussion. Online output training is established; RLS is not assumed local. |
| [Williams & Zipser (1989), experimental analysis of RTRL](https://gwern.net/doc/ai/nn/rnn/1989-williams.pdf) | Original paper copy: introduction, information/storage requirements and algorithm setup. Reference algorithm, not an economical local implementation. |
| [Sussillo & Abbott (2009), FORCE](https://stuff.mit.edu/afs/athena/course/9/9.49/www/Supplementary/Sussilo%20and%20Abbott%202009.pdf) | Feedback architecture, RLS equations 4–6 and suppression-of-chaos discussion. Target, correlation matrix and learning-rate limits remain explicit. |
| [Bellec et al., 2019 e-prop precursor](https://arxiv.org/pdf/1901.09049), [2020 publication](https://doi.org/10.1038/s41467-020-17236-y) | Precursor eligibility/learning-signal construction and pattern-generation update schedule; final publication abstract/captions only. Do not equate an approximate learning signal with arbitrary scalar reward. |

**Decision for this project.** Keep the three-part proposal, explicitly acknowledging CTRNN and gated-memory
antecedents. Attach a declared dynamical role to each witness: fading response, retained state, excitable event,
or attracting rhythm. Roles describe intended behaviour, not extra part types. Test return to that role after
perturbation, including learning-driven knob changes; do not impose universal contraction or a spectral-radius
cutoff. Use established RNN constructions as references before inventing replacements. This changes the
coverage criteria, not the body/interface or the authorised run budget.

## Related work from evolutionary robotics

Closest in spirit to evolving such circuits:

- **Continuous-time recurrent neural networks (CTRNNs)**, evolved for adaptive behaviour by Beer and colleagues since
  the early 1990s [29]: leaky nodes coupled through sigmoids, which is this project's level 0 without input filters,
  gates or clamps.
- **Learning without plasticity**: CTRNNs with fixed weights evolved to learn within their lifetime, with the learning
  held in their dynamics [30, 31] (a temperature-food association, much like food and poison here).
- **Evolved neuromodulated plasticity**: networks given modulatory neurons that gate plasticity evolved to use them,
  and learned better in reward-based tasks [32, 33]; the gate in `mixed_feedback.py` is that idea in circuit form.
- **NEAT**: evolving topology by starting minimal and growing, with historical markings for crossover and speciation
  to protect new structure [34].
- **The simulator is never part of the solution**: Thompson's FPGA evolved a tone discriminator that depended on
  unconnected cells and the chip's physics [35]; Jakobi's "radical envelope of noise" hid what a simulation models
  badly inside noise, so evolved controllers couldn't exploit it [36]. Both bear on the defences in `AGENTS.md` (the ground rules).

## What it suggested for this project (historical proposals)

Written before the circuit work; what has come of each, as of 2026-10-22:

- **Our element is theirs, with three additions.** `mixed_feedback.py` has their node and element (tanh or sigmoid
  of a filtered voltage) and adds a **gate** (a third node scaling the current, so modulation is a signal inside the
  circuit rather than a parameter set from outside), **clamps** and **perfect integrators** (no leak). The gate is how
  learning lives in our circuit; clamps and integrators are idealisations their framework avoids: every node has a
  passive, monotone resistive element. *Done*: an experiment may declare Sepulchre's rules (every node leaky but
  memory nodes, no clamps; below).
- **Coordinates for evolution.** Describe elements by sign and timescale band (fast, slow, ultra-slow, separated by
  a factor of several) and by voltage window, not as free parameters; behaviour changes kind at known boundaries of
  balance, so the search space has meaningful axes. *Not tried*: the search tunes raw values.
- **Cheap analysis before simulation.** The I-V curves at each timescale are static and quick to compute: a circuit
  whose motor nodes have no N-shaped fast curve can't spike, and need not be simulated. *Not tried.*
- **Learning as modulation.** The designed circuit learns a synaptic gain (P gates a synapse). The literature suggests
  learning could equally shift a node's intrinsic balance, for example a slow negative conductance switching a neuron
  between relaying and ignoring its input: a lever an evolved circuit might find. *Not seen yet*: the searched circuits
  gate their reads by the bit.
- **Robustness as a test.** Their central claim is robustness to mismatch through balance. An evolved circuit should
  keep working with every parameter a few percent off at birth; that is both a defence against overfitting the
  simulator and a check that it has found a mixed-feedback solution rather than a fine-tuned one. *Done*, and harder
  than proposed: 10% mismatch in every part, built into the simulator; the hand-built neurons failed it, the searched
  circuits pass.
- **Our behaviour is events driving kicks**, like the 1991 neuron servo: each motor spike is a fixed kick, so the body
  is driven by event timing and rate, the regime this literature is about.
- **Not yet used here**: slow positive feedback (bursting), rebound, winner-take-all, resistive couplings; and the
  simplest circuits found use no positive feedback at all (below). The hush
  between our sensors is a crude winner-take-all; a rebound winner-take-all [19, 20] is its principled form.

## What the minimal circuit search found, against it (2026-10-21)

The details are `minimal/NOTEBOOK.md`, M10. In brief: the simplest circuits that learn the bit (about 22 parts) contain
**no positive-feedback loop at all**. Everything Sepulchre gets from positive feedback they get elsewhere: their
**events** from the body's spike counter (a comparator with hysteresis, the only positive feedback in the system, in
the interface every brain shares), their **memory** from a perfect integrator (a floating gate), their **rhythm** from
noise. They got that way by pruning, judged at one noise level, a circuit with a true mixed-feedback clock, whose rate
didn't hang on the noise: so a mixed-feedback clock costs 2 parts and buys robustness, which only judging across the
noise range values. A circuit of Sepulchre's components alone was estimated at about 26 parts with gates: not as simple,
but robust where the simplest is not. A memory of his components fails in instructive ways: a leaky node holding the
bit is swamped by its own membrane noise, and a latch sticks on its first guess unless poison can flip it.

**Sepulchre's rules, as we enforce them** (the user's decision, 2026-10-21): his framework is silent on learning and on
non-volatile storage (its gains are set from outside the circuit; its memory is slow variables, which fade, and
latches, which are binary), and real neuromorphic chips pair such neurons with non-volatile weights (floating gates).
So under "Sepulchre's rules" (`rules: "mixed"` in a spec, `AGENTS.md`) the dynamics must be his, every node leaky but
memory nodes and no clamps, while our gates and memory nodes stay allowed. A three-arm experiment (free, his rules
with a floating gate, strict with a latch; `minimal/NOTEBOOK.md`, M12) settled nothing about his discipline: the
circuit both first arms started from already obeyed his rules, so they polished alike, and the strict arm never
learned. A fair test needs a start built of his components, events from positive feedback.

## References

1. L. Ribar, R. Sepulchre, "Neuromorphic control: designing multiscale mixed-feedback systems", IEEE Control
   Systems Magazine 41(6), 2021. [arXiv:2011.04441](https://arxiv.org/abs/2011.04441)
2. R. Sepulchre, "Spiking control systems", Proceedings of the IEEE 110(5), 2022.
   [arXiv:2112.03565](https://arxiv.org/abs/2112.03565)
3. L. Ribar, R. Sepulchre, "Neuromodulation of neuromorphic circuits", IEEE Transactions on Circuits and Systems I,
   2019. [arXiv:1805.05696](https://arxiv.org/abs/1805.05696); code:
   [Circuit-Neuromodulation](https://github.com/lukaribar/Circuit-Neuromodulation); thesis: L. Ribar, *Synthesis of
   neuromorphic circuits with neuromodulatory properties*, Cambridge, 2019.
4. C. Mead, *Analog VLSI and Neural Systems*, Addison-Wesley, 1989; "Neuromorphic electronic systems", Proc. IEEE
   78(10), 1990.
5. R. Sepulchre, G. Drion, A. Franci, "Control across scales by positive and negative feedback", Annual Review of
   Control, Robotics, and Autonomous Systems 2, 2019.
   [Cambridge repository](https://www.repository.cam.ac.uk/handle/1810/305893); and "Excitable behaviors", 2018,
   [arXiv:1704.04989](https://arxiv.org/abs/1704.04989).
6. A. Franci, G. Drion, R. Sepulchre, "Robust and tunable bursting requires slow positive feedback", Journal of
   Neurophysiology 119, 2018; "Modeling the modulation of neuronal bursting: a singularity theory approach", SIAM J.
   Applied Dynamical Systems 13, 2014.
7. ERC Advanced Grant SpikyControl (KU Leuven, 2023-2027), [CORDIS](https://cordis.europa.eu/project/id/101054323);
   its predecessor Switchlet (Cambridge), [CORDIS](https://cordis.europa.eu/project/id/670645).
8. R. Sarpeshkar, "Analog versus digital: extrapolating from electronics to neurobiology", Neural Computation 10,
   1998.
9. K. Scheres, R. Sepulchre, "Discrete event system modeling of neuromorphic circuits", 2025.
   [arXiv:2511.15594](https://arxiv.org/abs/2511.15594)
10. R. Wroblowski, R. Sepulchre, "Describing functions and phase response curves of excitable systems", 2025-2026.
    [arXiv:2511.16235](https://arxiv.org/abs/2511.16235)
11. G. Drion, T. O'Leary, E. Marder, "Ion channel degeneracy enables robust and tunable neuronal firing rates", PNAS
    112, 2015; G. Drion, A. Franci, J. Dethier, R. Sepulchre, "Dynamic input conductances shape neuronal spiking",
    eNeuro 2, 2015.
12. A. A. Prinz, D. Bucher, E. Marder, "Similar network activity from disparate circuit parameters", Nature
    Neuroscience 7, 2004.
13. L. Mendolia et al., "A neuromodulable current-mode silicon neuron for robust and adaptive neuromorphic systems",
    2025. [arXiv:2512.01133](https://arxiv.org/abs/2512.01133)
14. F. Castaños, A. Franci, "Implementing robust neuromodulation in neuromorphic circuits", Neurocomputing 233, 2017.
    [arXiv:1608.03908](https://arxiv.org/abs/1608.03908)
15. R. Sepulchre, T. O'Leary, G. Drion, A. Franci, "Control by neuromodulation: a tutorial", European Control
    Conference, 2019; E. Marder, "Neuromodulation of neuronal circuits: back to the future", Neuron 76, 2012.
16. G. Drion, J. Dethier, A. Franci, R. Sepulchre, "Switchable slow cellular conductances determine robustness and
    tunability of network states", PLoS Computational Biology 14(4), 2018.
    [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5940245/)
17. J. Dethier, G. Drion, A. Franci, R. Sepulchre, "A positive feedback at the cellular level promotes robustness and
    modulation at the circuit level", Journal of Neurophysiology 114, 2015.
    [arXiv:1409.6338](https://arxiv.org/abs/1409.6338)
18. G. Drion, A. Franci, R. Sepulchre, "Cellular switches orchestrate rhythmic circuits", Biological Cybernetics,
    2019.
19. Y. Huo, F. Forni, R. Sepulchre, "A winner-takes-all mechanism for event generation", 2025.
    [arXiv:2504.11374](https://arxiv.org/abs/2504.11374)
20. Y. Huo, F. Forni, R. Sepulchre, "A neuromorphic architecture for scalable event-based control", 2025-2026.
    [arXiv:2511.11924](https://arxiv.org/abs/2511.11924)
21. T. S. J. Burger, R. Sepulchre, "Excitability across scales: a unifying EI model", 2026.
    [arXiv:2610.13275](https://arxiv.org/abs/2610.13275)
22. R. Schmetterling, F. Forni, A. Franci, R. Sepulchre, "Neuromorphic control of a pendulum", 2024.
    [arXiv:2404.05339](https://arxiv.org/abs/2404.05339)
23. T. Chaffey, R. Sepulchre, "Monotone one-port circuits", IEEE Transactions on Automatic Control 69(2), 2024.
    [arXiv:2111.15407](https://arxiv.org/abs/2111.15407)
24. F. Forni, R. Sepulchre, "Differential dissipativity theory for dominance analysis", IEEE Transactions on
    Automatic Control, 2019. [arXiv:1710.01721](https://arxiv.org/abs/1710.01721)
25. A. Shahhosseini, T. Chaffey, R. Sepulchre, "Operator-splitting methods for neuromorphic circuit simulation",
    2025, [arXiv:2505.22363](https://arxiv.org/abs/2505.22363); "An operator-theoretic framework to simulate
    neuromorphic circuits", CDC 2024, [arXiv:2404.06255](https://arxiv.org/abs/2404.06255).
26. T. B. Burghi, R. Sepulchre, "Adaptive observers for biophysical neuronal circuits", IEEE Transactions on
    Automatic Control, 2024. [arXiv:2111.02176](https://arxiv.org/abs/2111.02176)
27. A. Bizyaeva, A. Franci, N. E. Leonard, "Nonlinear opinion dynamics with tunable sensitivity", IEEE Transactions on
    Automatic Control 68(3), 2023. [arXiv:2009.04332](https://arxiv.org/abs/2009.04332)
28. K. Jacquerie, D. Tyulmankov, P. Sacré, G. Drion, "Burst firing creates an attractor in synaptic weight dynamics",
    PLoS Computational Biology, 2026. [ORBi](https://orbi.uliege.be/handle/2268/346004)
29. R. D. Beer, "On the dynamics of small continuous-time recurrent neural networks", Adaptive Behavior 3(4), 1995.
30. B. M. Yamauchi, R. D. Beer, "Sequential behavior and learning in evolved dynamical neural networks", Adaptive
    Behavior 2(3), 1994.
31. E. Izquierdo, I. Harvey, R. D. Beer, "Associative learning on a continuum in evolved dynamical neural networks",
    Adaptive Behavior 16(6), 2008.
32. A. Soltoggio, J. A. Bullinaria, C. Mattiussi, P. Dürr, D. Floreano, "Evolutionary advantages of neuromodulated
    plasticity in dynamic, reward-based scenarios", Artificial Life XI, 2008.
    [EPFL](https://infoscience.epfl.ch/record/121548)
33. A. Soltoggio, K. O. Stanley, S. Risi, "Born to learn: the inspiration, progress, and future of evolved plastic
    artificial neural networks", Neural Networks 108, 2018.
34. K. O. Stanley, R. Miikkulainen, "Evolving neural networks through augmenting topologies", Evolutionary
    Computation 10(2), 2002.
35. A. Thompson, "An evolved circuit, intrinsic in silicon, entwined with physics", Evolvable Systems (ICES 1996),
    LNCS 1259, 1997. [doi:10.1007/3-540-63173-9_61](https://doi.org/10.1007/3-540-63173-9_61)
36. N. Jakobi, "Evolutionary robotics and the radical envelope-of-noise hypothesis", Adaptive Behavior 6(2), 1997.
37. Y. LeCun, Y. Bengio, G. Hinton, "Deep learning", Nature 521, 2015.
38. E. O. Neftci, H. Mostafa, F. Zenke, "Surrogate gradient learning in spiking neural networks", IEEE Signal
    Processing Magazine 36(6), 2019.

## Motif-bench choices after the catalogue (2026-11-19)

The construction records and measured outcomes live in [D128–D133](discrete/NOTEBOOK.md#d128-change-and-order).
These sources informed the mechanism choices; none establishes our noisy circuit's performance.

| primary source | reading scope and design consequence |
|---|---|
| [Ma et al. (2009), *Defining Network Topologies that Can Achieve Biochemical Adaptation*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3068210/) | Adaptation definition, model/search assumptions and feedback-buffer equations 2–4. Sensitivity and return to baseline are separate requirements. Integral feedback is the established alternative to fragile cancellation; biochemical model guarantees do not transfer unchanged. |
| [Haag, Denk & Borst (2004), *Fly motion vision is based on Reichardt detectors regardless of the signal-to-noise ratio*](https://www.pnas.org/doi/10.1073/pnas.0407368101) | Introduction and Fig. 1 mechanism: asymmetric filtering, multiplication and mirrored subtraction. Used as a temporal-comparison precedent; our clipped gates are approximate products and do not imply a fly model or calibrated motion estimate. |
| [TI, *Window comparator circuit*](https://www.ti.com/tool/CIRCUIT060084) | Primary design description. Two thresholds define an inactive region; our split writers instantiate that functional idea using the existing macros, rather than importing a packaged comparator as a new primitive. |
| [TI, *Designing With the SN74LVC1G123 Monostable Multivibrator*](https://www.ti.com/lit/an/slva720a/slva720a.pdf?ts=1794683495401) | Sections 3.1–3.2: RC timing, recovery assumptions and retriggering. A bounded adaptive pulse is weaker than constant-width monostable timing or demonstrated regenerative excitability; the tests keep those claims separate. |

The component benches distinguish measurable information from a usable internal reference. An observer can
compare phase conditions or subtract a baseline, but the brain must carry any reference required for action.
The present tests do not establish that such calibration or useful eligibility follows automatically from the
three macros. The current [coverage ledger](PARTS.md#coverage-ledger-behaviours-are-assemblies-not-additional-parts) and [assignments](PARTS.md#bounded-next-work-after-the-first-witness-batch)
keep those limitations visible.

## Baseline rejection before timing comparison (2026-11-19)

[D141](discrete/NOTEBOOK.md#d141-baseline-rejection) owns the experiment and its limitations.
The following primary-source reading selects an analytic discriminator, not a circuit implementation.

| Method/source | What was read; relevance and assumptions |
|---|---|
| AC coupling: Analog Devices [ADN2811 data sheet, p.17](https://www.analog.com/media/en/technical-documentation/data-sheets/adn2811.pdf) | Coupling-time-constant discussion and Fig.22 describe baseline wander and resulting timing distortion. A high-pass is a simple local constant-baseline rejector, but does not distinguish desired slow signals from drift; startup and long constant intervals matter. The product's particular frequency and capacitor choices are not imported into this project. |
| Integral feedback: Yi, Huang, Simon & Doyle (2000), [primary paper](https://groups.csail.mit.edu/mac/projects/amorphous/6.978/papers/doyle-PNAS-2000.pdf) | Read pp.1–3, especially Fig.2 and the steady-state argument plus biological assumptions. An integral of local error can enforce a stable equilibrium's return to a reference. Stability and the reference's own dependence on input matter. This is constant-input adaptation, not proof that arbitrary drift is removed while phase is preserved. D128 already has a noisy integral-feedback witness, whose resting level follows writer offset. |

A first-order idealisation writes tau × db/dt = x−b, y=x−b, giving H(s)=s tau/(1+s tau).
It supplies a precise reference for baseline rejection, not a claim that our mismatched subtractors implement
it without residual error, or that capacitor state is noise-free. Feedforward cancellation requires matching;
feedback adaptation can remove dependence on input level while retaining a device-dependent equilibrium.
A phase detector following either method must tolerate that equilibrium and differential phase shifts.
D138's auto-zero and chopping precedents remain distinct: they impose an internal comparison, rather than
infer a baseline from an arbitrary signal's time average. No method here supplies a world period for free.

For signed modulation, [Analog Devices MT-079](https://www.analog.com/media/en/training-seminars/tutorials/MT-079.pdf)
pp.1 and 4–5 distinguish two-quadrant control (one input unipolar) from four-quadrant multiplication,
and describe cross-coupled cells plus conversion circuitry. Its offset discussion identifies input
feedthrough and output/gain errors. This manufacturer account is the precedent read, not a claim to
have read Gilbert's original papers. D142–D144 recover analogous limitations in our different macro
model. An explicit pair of complementary gates is a candidate for signed gain control; it is not an
exact Gilbert cell, and no published trimmed-product accuracy is transferred to it. The alternative is
retaining only nonnegative gain and using separate signed signal paths; either needs a counted graph.

### Shared-path reversal review (D152–D153, 2026-11-19)

Re-read [AN-1131](https://www.analog.com/en/resources/app-notes/an-1131.html),
chopping equations and settling sections: opposite input polarity followed by output reversal cancels
an unchanged additive internal offset; successive observations also introduce delay.
Read technique and artifact sections of [Basilico, How to Use Zero-Drift Amplifiers in Wider Bandwidth Applications](https://www.analog.com/en/resources/analog-dialogue/articles/how-to-use-zero-drift-amplifiers-in-wider-bandwidth-applications.html):
input/output switching and filtering are actual operations, with charge-injection error, ripple and
finite bandwidth. Auto-zeroing instead stores an internal-zero measurement and interrupts that path's
signal acquisition. These manufacturer descriptions were read; their cited original papers were not.
[D152–D153](discrete/NOTEBOOK.md#d152-shared-path-reversal) test the narrower question of which error
parities the existing signed-control assembly can reject. Product accuracy does not transfer to it.

### Oscillator operating-point adaptation (D161–D162, 2026-11-19)

Read Che & Forni, [A tunable mixed feedback oscillator](https://api.repository.cam.ac.uk/server/api/core/bitstreams/5fc2227a-cdff-4361-b9f8-38fea84ae28a/content),
model description and SectionV (equilibria/coexistence). Their oscillation guarantee additionally
requires boundedness and2-dominance; an unstable root alone does not transfer that guarantee to our
multiple nonlinear branches and added memory state.
Read Thorsen et al.2014, [Robust Concentration and Frequency Control in Oscillatory Homeostats](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107766),
introduction, controller motifs and average-regulation argument. Integral feedback can regulate an
oscillatory variable's average under their kinetic assumptions; instantaneous constancy is not
required. These biochemical models are a functional precedent, not a physical/noise theorem for
our SONOS writer. Together with the earlier Yi et al. review, this motivates a diagnostic slow
negative-feedback bias loop, rather than an asserted global cycle repair. Fixed bias and changing
feedback gain are the closest existing-knob alternatives; D127/D159–D161 separate their limits.

<a id="calibration-identification-review-2026-11-20"></a>
## Calibration and identification review — 2026-11-20

D165 changes the question from obtaining more simultaneous events to distinguishing useful
calibration evidence from real order. These sources guide the next discriminating measurements,
not a decision to implement a named learning algorithm.

- [Bradtke & Barto (1996), *Linear Least-Squares Algorithms for Temporal Difference Learning*](https://all.cs.umass.edu/pubs/1995_96/bradtke_b_ML96.pdf),
  section 5.1, pp. 38–40, equations 5–8 and lemmas 1–2 **read in the paper**. Their
  instrumental-variable construction requires informative correlations with the quantity being
  estimated and absence of correlation with nuisance errors; more samples do not remove bias
  when those conditions fail. Our inference: coincidence-weighted balancing needs its own
  identification argument, because genuine event order contributes to the proposed error signal.
  This is an analogy at the estimation level, not an application of their convergence theorem.
  Their linear Markov prediction setting differs from our nonlinear noisy circuit. Closest options
  here are selective observations, a supplied simultaneous-event reference, and a separate internal
  reference. None is yet established as a physical solution. We would add a local, costed circuit
  demonstration under its actual observation restrictions, not a new general estimation theorem.
- [Enz & Temes (1996), *Circuit Techniques for Reducing the Effects of Op-Amp Imperfections: Autozeroing, Correlated Double Sampling, and Chopper Stabilization*](https://docenti.ing.unipi.it/~a008309/mat_stud/MIXED/archive/2022/Optional_Materials/articles/Offset_canc_Enz_Temes_96.pdf),
  DOI 10.1109/5.542410. **Source-indexed excerpts of sections II–III read; the PDF opened but its
  full text was not extractable in this review.** The excerpts distinguish sampling an offset
  from modulating/demodulating the signal, and discuss noise folding in sampled cancellation.
  Use this as a literature lead, not a fully checked implementation recipe. Our inference is that
  a fixed reference error needs an error-rejection operation, not just a longer observation.
  Before any construction, read the relevant circuits and assumptions directly and map every
  switch, stored state and noise source to the catalogue. The D154 routing problem remains parked;
  this citation supplies neither a primitive nor an exception to it.

The [next assignment](PROGRAMME.md#next-diagnostic-assignment-2026-11-20) measures selectivity and
precision separately and tests a two-gain capacity reference. It deliberately postpones physical
construction. Our own D164/D165 equations and saved data, rather than an unverified paper claim,
supply the numerical error model used there.

<a id="offset-rejection-review-2026-11-20"></a>
### Offset rejection: primary sources read for D168 (2026-11-20)

[D168](discrete/NOTEBOOK.md#d168-calibration-precision) asks whether the order calibration's readout can reject
its own fixed error. The D166 entry above recorded Enz & Temes as excerpts only. Both sources below are scanned
PDFs with no text layer; their pages were decoded locally from the PDFs' fax-compressed page images and read as
images. Pages and equations read are listed; nothing else in them is claimed.

- **Enz & Temes (1996)**, *Proc. IEEE* 84(11), DOI 10.1109/5.542410,
  [PDF](https://docenti.ing.unipi.it/~a008309/mat_stud/MIXED/archive/2022/Optional_Materials/articles/Offset_canc_Enz_Temes_96.pdf).
  **Read in the paper:** pp. 1584–1602, i.e. the abstract, I and all of sections II–IV (equations 1–40,
  Figs. 1–26 and 28–31 as they fall on those pages), up to the start of V on p. 1602. Not read: sections V–VII
  and the appendix.
  - *Autozero (AZ)* (II A, C): two phases. During a sampling phase the amplifier is **disconnected from the signal
    path, its inputs short-circuited**, and a nulling control x_c drives the output to zero; x_c is stored (analogue
    S/H or digital register) and held during the signal phase. The offset cancels only if it is **unchanged between
    the phases** and the amplifier is used "under the same conditions as during sampling" (p. 1586). Residual
    offset (II C, Fig. 8): an error Δx_c in storing the control (charge injection of the sampling switch, A/D
    quantisation) leaves V_ios-lin or V_ios-NL; a nonlinear nulling characteristic helps only when the initial
    offset is already small.
  - *Noise* (II B): AZ subtracts a recent sample of the same noise, a high-pass with a zero at dc (eqs. 3–4), so it
    removes offset and much 1/f noise; but sampling **aliases wideband noise** into the baseband: the foldover term
    is about (πf_cT_s − 1)·S₀·sinc² (eq. 11), roughly the white noise multiplied by the ratio of noise bandwidth to
    the Nyquist frequency (p. 1589).
  - *Correlated double sampling (CDS)* (II D): AZ followed by a sample-and-hold of the signal; same zero at dc,
    comparable foldover. AZ "may be incompatible with continuous-time applications" because the amplifier is
    unavailable during the sampling phase (p. 1590).
  - *Chopper stabilisation (CHS)* (III): modulation, not sampling: input multiplied by a ±1 square wave, amplified,
    demodulated; offset and 1/f noise modulated once are moved to the odd harmonics and filtered (p. 1591); gain
    depends on matching the demodulator's phase to the amplifier's delay. Residual offset (III C) comes mainly from
    the **input modulator's** nonidealities (clock feedthrough, charge injection): spikes demodulated to dc,
    V_os ≈ (2τ/T)V_spike (eq. 22), reduced to (2τ/T)²V_spike by limiting bandwidth (eq. 23).
  - *Switch errors* (IV A, eq. 24): a sampled voltage on hold capacitor C_h carries
    ΔV = α C_ov/(C_ov+C_h) V_swing + q_inj/C_h + √(kT/C_h) + I_leak T_h/C_h: clock feedthrough, channel-charge
    injection (hard to predict; partly cancelled by dummy switches or fully differential structures, never
    perfectly), sampled kT/C noise, and leakage **droop** over the hold time.
  - *Offset storage and nulling ports* (IV B–E, eqs. 25–35): output storage leaves q_inj/(A·C) (eq. 25); closed-loop
    storage leaves V_os/A + q_inj/C (eq. 27); a cascade stored stage by stage leaves only the last stage's error
    divided by the total gain (eqs. 28–29). A separate **nulling input** (an extra differential pair in parallel
    with the main one, Fig. 24, or an adjustable degenerated mirror, Fig. 25) driven by a stored control leaves
    −V_os/(A₂A₃) − (g_m2/g_m1)·q_inj/C_h (eq. 31): loop gain shrinks the first term, the transconductance ratio
    the second, bounded by the control's range (eqs. 33–35).
  - *Continuous-time autozero* (IV F, eqs. 36–40, Fig. 26): a main amplifier never leaves the signal path; a nulling
    amplifier, itself autozeroed in alternate phases, drives the main amplifier's nulling input. The residual is the
    two amplifiers' offsets divided by the nulling amplifier's gain plus the stored charge errors (eq. 39): the
    corrector's own offset still enters, reduced only by gain. Input signals near multiples of the clock are aliased
    into an apparent offset, so the nulling path low-pass filters the sensed voltage (an OTA loaded by a large
    capacitor) to track its mean (p. 1602).
- **Shieh, Patil & Sheu (1987)**, *Measurement and analysis of charge injection in MOS analog switches*, IEEE JSSC
  SC-22(2) pp. 277–281, [PDF](https://hasler.ece.gatech.edu/Courses/ECE4430/Proj4/Sheu_02.pdf).
  **Read in the paper:** pp. 277–281, the whole paper (II's equations 1–17, III's measurement circuit, IV's
  results). Switch-induced error is
  "usually in the millivolt range"; a fully differential circuit cancels it only "to the first order" (p. 277).
  The injected error depends on the gate's falling rate U, the holding and source capacitances and resistance,
  and V_HT = V_H − V_S − V_TE (eqs. 4–10), so it varies **with the signal level V_S**: it is not a constant offset
  that a later subtraction removes. With slow switching the charge divides towards the larger capacitance;
  fast switching splits it about equally whatever the capacitances (eqs. 14–17, Figs. 3–5); a small source
  resistance drains it. Measurements on 3 µm CMOS agree with the model for gate falling rates of 1.25×10⁶ to
  5×10⁸ V/s (Fig. 9).
- **Cauwenberghs (NIPS 5, 1992, published 1993)**, *A fast stochastic error-descent algorithm for supervised
  learning and optimization*, [PDF](https://papers.nips.cc/paper_files/paper/1992/file/c06d06da9666a219db15cf575aff2824-Paper.pdf).
  **Read in the paper:** pp. 244–248 (sections 1–2 and the start of 3; the PDF has a text layer). Read for D168's
  question of how a circuit could observe a knob's own effect (B) without a model of itself. Perturb every
  parameter at once by a small random ±σ held for an epoch, measure the change in error against the unperturbed
  error, and update Δp = −µ·(E(p+π) − E(p))·π (eqs. 4–5). On average this is gradient descent with rate µσ²
  (2.1). Subtracting the unperturbed reference E(p) is what makes each step a descent and removes the need to
  average (2.2). With P parameters it is √P slower than true gradient descent, against P for sequential weight
  perturbation, because one scalar response channel carries the information (2.3). The motivation is analogue
  hardware whose "unknown process impurities" make computed gradients ill-posed (p. 245).
  For us: one knob means P = 1, two gains P = 2, so √2 slower. The method needs the same "error" to be evaluated with
  and without the perturbation. Anchors differ from one another in amplitude, so successive anchors are not
  repeats, and their differences would add variance that the paper's deterministic setting does not have.
  Extremum-seeking control (Krstić & Wang 2000, Automatica 36:595–601) is the continuous-time control
  counterpart; only its bibliographic record was found, not read.

**What fits here and what does not.** AZ, CDS and CHS all cancel an offset by observing **the same physical path**
in two conditions, and all three create the second condition by **switching** (disconnecting or shorting the
input, or reversing its polarity under a clock). Their residuals are exactly the costs of those switches:
charge injection, feedthrough, kT/C sampling noise with foldover, droop, and demodulator phase. Our catalogue has
no switch, no clock and no input disconnection ([D154](discrete/NOTEBOOK.md#d154-routing-contract)); a body or
world clock is not admissible. D168's quiet self-reference keeps the AZ idea — read the same path while the
wanted signal is absent — but takes the "sampling phase" from the circuit's own quiet time, weighted continuously
by 1 − w, so there is no switch to inject charge and no sample to alias. The paper's assumptions then become our
requirements: the same path must carry both readings (otherwise D149's rule applies: an independent detector adds
its own error), the offset must be unchanged between quiet and coincident moments, and the wanted signal must be
absent in quiet time, which in this circuit holds only after the baseline or resting level is accounted for.
IV E–F is the closest published form: a nulling port driven by a slowly filtered estimate, whose
own offset is suppressed only by loop gain or by being autozeroed in turn, which again needs switches.
Closest alternatives: CHS (needs polarity routing, parked at D154), a second independent detector (rejected,
D149/D151), and accepting the error. What this project would add: a switch-free, locally weighted variant whose
phases are set by the circuit's own signal statistics; it is a candidate specification, not an established
technique, and none of the papers' accuracy figures transfer to it.

<a id="local-adaptation-review-2026-11-20"></a>
### Local adaptation and what supplies its target — D171 review (2026-11-20)

Primary-source update for the programme review. Read the specified methods/results sections in the linked
full-text versions, not just abstracts. These papers inform comparisons; none validates our circuit.

- **Saponati, De Luca, Indiveri & Grewe (2026 preprint), feedback control optimizer**,
  [source](https://arxiv.org/html/2602.13261v1), sections II-A, III-B/C and V-B. Paired positive/negative
  control neurons guide local updates toward supplied target spikes; evaluation here is a single-layer network
  with simulated hardware mismatch. Population redundancy is an alternative to precision correction.
  Relevant lesson: feedback can carry local correction information, but the source and communication cost of
  its target must be counted. Our taste interface does not supply those per-output targets. This supports a
  comparator, not direct adoption or a claim of hardware validation.
- **Putra et al. (October 2026 preprint), ENCL**,
  [source](https://arxiv.org/html/2610.31927v1), Related Work, methodology and Algorithms 1–2.
  Combines local supervised learning (TESS) with task-specific masks and freezing in a fixed network.
  Task identities and boundaries are supplied during training and inference; capacity is allocated in fractions
  of a declared maximum task count. Relevant alternative: protect/reuse existing material before growth.
  It does not solve autonomous detection of when a new capacity is needed. Its reported GPU measurements are
  not transistor costs for this project.
- **Dohare et al., continual backpropagation**, read the
  [April 2024 author preprint](https://arxiv.org/html/2306.13812v3), abstract and Discussion; publication is
  [Nature 2024](https://doi.org/10.1038/s41586-024-07711-7) (publisher full text inaccessible in this review).
  Selective reinitialisation of low-utility units motivates the recycling comparison already required here.
  Retaining an old skill and retaining the ability to learn a new one are different measurements. The method
  uses backpropagation; it is not an explicit local analogue implementation for this robot.

The earlier [offset-rejection source review](#offset-rejection-review-2026-11-20) remains the basis for the
shared-path mechanism. No new claim of novelty for offset cancellation follows from D170. The prospective
contribution is a costed mechanism with locally available reference conditions that transfers between uses,
then demonstrably improves in-life action. Whether that contribution exists remains to be tested.
