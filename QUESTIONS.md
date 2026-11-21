# Open questions

**Current assigned question, D183 preparation:** which existing action settings improve collection and
survive fresh seeds and circuit refinement? The [fixed work order](lab/WORK_ORDER_2026-11-20_action_grid.md)
owns the proposed experiments. It supersedes earlier action queues; autonomous selection of a useful
setting remains a later question, not an executor assignment.

**Current priority, D177 review:** under silicon's noise, which limits useful action: sensory transmission,
motor transfer, exploration or the chosen knob operating region? Can existing settings/components repair
it, and what local evidence would let the brain select that repair? [D177](discrete/NOTEBOOK.md#d177-robot-review)
owns the proposed discrimination. Earlier priorities below are historical and qualified by this review.

**Current priority, after D176:** can a relay unit that is reliable under 10% mismatch carry the eyes' evidence
to the thrusters well enough to approach the ideal-relay replay (about 4.7 food:poison, a simplified model, against the held-knob circuit's 1.16–1.29),
and what local signal could tell a unit that its relaying is failing? Answered by
[D176](discrete/NOTEBOOK.md#d176-robot-shortfall): the designed circuit's shortfall is in action and knob
retention, not credit evidence. The D175 priority below is answered. A new build awaits the user's direction.

**Current priority, D175 review:** which documented robot shortfall comes from missing retained evidence,
incorrect taste-driven adjustment, or poor action despite learning? Test existing eligibility traces
and knobs before assuming a calibrated timing front end is necessary. [D175](discrete/NOTEBOOK.md#d175-results-review)
owns the proposed comparison. The earlier front-end proposal below is conditional, not the immediate queue.

**Answered 2026-11-20 (D172–D174):**
- **Answered:** the shared-reading connection can stay quiet under mismatch with a designed gate threshold, keeping
  most anchor evidence. It is confirmed noisy on fresh draws.
- **Not established:** transfer. The catalogue has no second use with a marked reference, and robot lives have few
  coincidences.
- **New first question for this line:** what front-end contract, not tuned to the task, would map the robot's
  signed taste pulse and Poisson sensor trains into a timing detector's input class, so that the coincidence gap
  D172 relies on can be measured on real histories? It awaits the user's direction.
- **Still open:** the two-gain identification question below.

**Review priority, 2026-11-20 ([D171](discrete/NOTEBOOK.md#d171-programme-review)), now historical:** can an explicit shared-reading
connection remain quiet under mismatch without discarding useful calibration evidence? If so, does its unchanged
adjustment rule transfer, and does the robot naturally provide the required reference conditions? Two-gain
feasibility also leaves an identification question: what local observation determines common gain as well as
balance, without prescribing a task-specific output amplitude? Proposed sequencing is in PROGRAMME; no run is
authorised by this list.

Current priorities after the 2026-11-19 reset (D124). This page owns unresolved questions and candidate discriminating
investigations; [PROGRAMME.md](PROGRAMME.md#conditional-programme) owns their order and hand-offs.
Answers belong in the relevant notebook, with evidence and limitations, and leave this list when resolved.
The [previous question list](lab/v/questions_before_review_2026-11-16.md) preserves origins, abandoned suggestions
and earlier answers; its many “next” instructions are historical, not a second work queue.

## Current first question: do three circuit macros cover the useful dynamics?

The [proposed catalogue and bounded witness plan](PARTS.md#2-the-catalogue-primitives-dynamical-motifs-and-learning)
own the specification. Can dynamic nodes, controlled connections and retained memory express the required
behaviours within the existing noise/physical contracts? In particular, can strength gating construct the
needed signed interactions and adjustable timescales, and how are internal filter states physically represented?
After coverage, can a bounded module express a known one-bit repair at an affordable exhaustive-search size?
The [review](discrete/NOTEBOOK.md#d124-minimal-dynamic-parts) records what is established and what is conjecture.
[D128–D131](discrete/NOTEBOOK.md#d128-change-and-order) establish more restricted behaviours and expose
component offsets as a repeated obstacle. D136 bounds pulse recovery on the existing development set;
faster event processing remains unproved. D137 explains phase bias from upstream and output mismatch;
D138 shows the mean alone cannot distinguish internal bias from a persistent true phase lead under the stated unknowns. [D140](discrete/NOTEBOOK.md#d140-input-reversal) finds preserved sensitivity but residual absolute-phase error with unequal baselines, plus finite-window and settling costs. D141–D144 show that centred signals need signed paths and that offset feedthrough survives drift even in a linear signed reference. Can explicit signed control preserve the useful response economically, and what local comparison suppresses feedthrough without erasing a wanted slow signal? D145–D146 test the first question: 39/40, below required reliability, with a traced offset shortfall and substantial null feedthrough. D148 specifies the required internal-zero/path-isolation observation; D149–D150 show that the reference itself is uncertain and partial correction can help under a stated prior. D151 finds that the proposed correction kernel loses the nominal advantage after counting its own offsets. D152–D153 show that ideal reversal helps, but the available active reverser retains source offsets as signal. D154 finds no direct reciprocal-routing contract. Can an economical composite avoid this error, or would it require a reviewed catalogue extension? This switching branch is parked. D155–D156 identify a resting-output reference missing from local temporal-order balancing: can continuous baseline estimation retain useful event evidence under varying event rates and order priors, after its own errors and settling are counted? A separate draw has incompatible constant-balance requirements. Can absence rejection preserve weaker evidence
at reasonable cost? What circuit
supplies useful eligibility, and how are signed learned controls represented? D139 finds that conservative quiet-trace thresholds lose downstream sensitivity. How can a local correction distinguish weak events from offset while balancing paired responses (D134 separates those causes)? D162 confirms the retained bias repair at its recorded material/power cost. D163 recovers most ideal order-calibration performance with longer histories; D165–D166 trace the remaining single-anchor failure to contamination by genuinely ordered events. Can local signals select useful calibration evidence without supplied timing labels, does retaining early evidence still help under fixed readout error, and can two existing output gains cure the incompatible draw? Can a physical reference meet the resulting precision requirement economically?
D147 confirms that implicit connection filters omit independent thermal noise; the current witnesses avoid them. How should the physical filter be lowered to explicit noisy state with consistent cost, and which historical outcomes materially depend on that omission? The [bounded assignments](PARTS.md#bounded-next-work-after-the-first-witness-batch)
own the next tests and stopping rules.

**Parked simulator audit question (D147):** the noise-model prose describes gross device currents,
whereas `_step` adds `abs(I)` for each tanh element after sourcing/sinking branches combine. Does the
intended substrate account require the cancelling internal branch currents here, and what is the effect
on near-zero states? Diagnose against the physical mapping and existing tests before changing the engine;
this was noticed, not answered, in the filter audit.

The numbered questions below remain open background from the earlier growing-brain programme. They are
parked while the circuit catalogue is established; their numbering does not override the current first question.

## 1. Which relations between representations make noisy evidence economical to learn?

**Origin:** D69–D71's noisy-feedback shortfall; narrowed by the
[D73 information-path audit](discrete/NOTEBOOK.md#d73-noisy-evidence), 2026-11-16. Useful evidence remains after
matching inferred colours and the learning gate. Most of the signed sum's choice signal survives its stored
symbols. Supplying a useful grouping improves the learned readout. But
[D74](discrete/NOTEBOOK.md#d74-learned-sharing) tested exact learning of the grouping under two priors of one
model family: no decision gain was established (the interval does not exclude most of the supplied advantage),
and inappropriate sharing delays necessary distinctions. Other readout families and priors are untested. The grouping,
numerical order and memory scale are different kinds of supplied knowledge, with different learning costs.

**Unresolved distinctions:** which useful relations can a generic component exploit from its local inputs;
what must be learned rather than supplied; whether the evidence can pay for discovering that relation
within a life. Exact-copy weighting is explained by [D75](discrete/NOTEBOOK.md#d75-redundant-selection),
but detecting approximate redundancy without erasing complementary information remains open. Neither
fewer primitives nor a choice vote is established as the answer.

**Next discriminator:** question 2 now has software resource observations, but the benefit of allocating
additional memory is unresolved. Then contrast the same relation when supplied, discovered and inappropriate, accounting for
both model-identification evidence and parameter learning. Do not add another partition variant without
a reason the present failure would change. A duplication test must conserve both initial and redistributed
weight if it claims to change only representation. Correct forecast/scoring order before a new design freeze.

**Control boundary:** the original drift filter receives actual eaten colours, and its noisy worlds change
scored reward as well as taste. The highest-noise rungs are useful inference tests with negative expected
gain even for correctly targeted meals. Do not infer profitable adaptation from their colour accuracy or
gap closure. Use an existing profitable condition for the subsequent control test; no interface change is implied.

## 2. What does additional brain material actually buy, and cost?

**Origin:** the user's scaling goal, D59–D62 and D67–D69. Different allocation settings improve sequences;
the other curves differ. [D76](discrete/NOTEBOOK.md#d76-resource-floor) establishes that the current P is
not total material or an enforced allocation cap. The earlier [resource count](lab/v/size_count.log) concerns
an older arm; it omits the later rhythm repertoire.

**Unknowns:** how much comes from additional representation, how much from search or redundancy; whether
communication and selection remain local as size grows; whether quiet behaviour means low activity, low allocated
memory, or neither. No current scalar “material” count settles all of these.

**Partly answered by [D77](discrete/NOTEBOOK.md#d77-resource-observation)** (sequence rung 17 only): room
in the colour-event streams recovers much of the gain; 85% of the larger design's growth goes elsewhere;
sampled all-food lives grow nothing; mixer work remains substantial even at low allowance.
[D78](discrete/NOTEBOOK.md#d78-allocation-rules): under a real cap, a pairwise weight contest beats an equal split
(+.28 on fresh sequences; timing excludes harm larger than .10 on one rung) but fails to match the original
design. [D79's review](discrete/NOTEBOOK.md#d79-active-mixture) rejects the inference that existing signals
cannot rank streams: family sums hid positive individual records, and stored-weight trajectories included
sleepers. The validated diagnostic on one reused pair finds that omitting non-event forecasts together
reduces immediate loss, while some individual early forecasts help. Learning-time deletion changes the
forecasts scored much more often under the contest. [D80–D81](discrete/NOTEBOOK.md#d80-scoring-replay) find
a small direct prediction effect but changes through the allocation feedback path; no performance cure
is established. [D82](discrete/NOTEBOOK.md#d82-issued-credit) supplies and checks a consistent issued-forecast
contract; ten reused development pairs show no improvement and leave the contest's gap.
[D83](discrete/NOTEBOOK.md#d83-allocation-trace) traces one identical corrected contest life and finds
both removal of issued distinctions and construction removed before its first forecast. [D84](discrete/NOTEBOOK.md#d84-future-evidence) now validates the frozen-history reconstruction:
3653/5369 removed one-tally units would fire on later accepted lessons, including 821/923 same-taste
newborn removals. Some firings have exact living equivalents, contexts and lessons are correlated,
and retaining definitions may require deleted ancestors. [D85](discrete/NOTEBOOK.md#d85-retained-prediction) reconstructs missing readout counts and native
speakers exactly. Retained tallies beat their surviving stream for 1678/3653 recurring candidates,
but only 800 beat both that stream and uniform prediction; probability-score gains coexist with
worse hard choices in overlapping sums. These are not whole-brain or independent-unit comparisons.
[D86](discrete/NOTEBOOK.md#d86-mixture-confidence) checks those historical mixtures: halfway reduction
of confidence worsens log loss and squared error in all four lives and both time windows, with choices
unchanged. This rejects that simple transfer, not all calibration approaches. [D87](discrete/NOTEBOOK.md#d87-retained-mixture) now captures that corrected history exactly:
336/3653 recurring retained tallies beat the actual combined forecast, 279 also beat uniform, and
a supplied causal prior over candidates loses 0.593 bits on the full 163-label sequence. This closes
the simple fixed-definition retention comparison without a cure, not all possible retention mechanisms.
[D88–D90](discrete/NOTEBOOK.md#d88-parent-census) test memory as parts on the same life: weak parents build
about 6% of children, most children never forecast or lose to the combined forecast, and deleted units would
have been the earlier parent for 4874 words no living unit could build. **Next discriminators:**
[D92](discrete/NOTEBOOK.md#d92-ghost-children) establishes no clear missing-child advantage, not equivalence.
[D113–D120](discrete/NOTEBOOK.md#d120-hj-review) complete the gate comparison without establishing an
efficiency improvement. Do the new units materially affect the combined issued forecasts, despite cancelling
standalone bit totals? How much work and material does the gate actually change in both arms? Exact event
attribution, mixture weights and matched activity are the next missing measurements. [Completed K/L](discrete/NOTEBOOK.md#d122-contribution-capture) find small/mixed conditional contributions
on one seed pair and extra adapter scan work. Step back before selecting the next causal test; if allocation
remains the priority, inspect preserved/displaced old units at the first divergence. No new retention rule,
price tuning or larger run is selected. Changed observations and preserved ancestors remain alternatives.
Compare allocation, tuning, fixed capacity, recycling and growth on matched lives under the same account
before another sweep. Dohare et al.'s [preprint, section 6](https://arxiv.org/html/2306.13812v3#S6), supplies a
recycling precedent with smoothed activation/weight utility and protection for young units. It is not an
exact loss leave-out measure or evidence that its method meets our locality constraints.

**What changes our view:** an advantage disappearing after fair accounting would weaken the growth explanation;
a reproducible advantage attributable to new representation would strengthen it. Improvements that plateau or
cost more than they return define useful boundaries even without satisfying the scaling milestone.

## 3. Which part of the timing mechanism generalises?

**Origin:** D23 and D65–D68; the user's request to use phase-locked-loop theory, 2026-11-15.

**Unknown:** whether the gain comes from a reusable separation of acquisition and tracking, or depends strongly
on supplied time ranges, event definitions, discretisation and the mixture's ability to select a useful tracker.
D23's unsuccessful entrainment and D68's success used different evidence regimes; they do not rank all counters
against all oscillators.

**First discriminator:** match each stage to its assumptions in estimation and synchronisation theory; inspect
what each controlled intervention already isolated. Choose a development test that varies one such assumption
(period range, drift, missing or false events, or nested rhythms) while keeping an achievable comparator.
Predeclare whether the test is about acquisition, tracking or downstream use. Preserve any unexpected successful
transfer rather than forcing it into the original explanation. New sealed evaluation waits for a frozen claim.

## 4. Why does composition lag, and why is old knowledge not reused?

**Origin:** D59–D60's combination gap and A–B–A experiments; the user's returning-world question, 2026-11-15.

**Competing explanations:** useful combinations never form; duplicate blocks waste evidence; credit fails to
reach useful parents; old counts are overwritten; useful blocks are removed; preserved knowledge is not selected.
The earlier duplicate-removal bug makes code-to-result provenance particularly important here.

**First discriminator:** trace a short recorded case and locate the earliest divergence from a successful
reference. For returning worlds, distinguish retaining a representation, recognising the return and relearning
from scratch. Compare learning cost on first exposure and return, with storage and ongoing activity charged.
A targeted interruption of writing, retention or selection should separate causes before a new memory hierarchy.

## 5. What local signal identifies an improvable shortfall?

**Origin:** the user's core question, recruitment E/H series, D15–D18 and the intervention stories.

Surprise, pain, stalled adjustment and low reward are candidate signals, not certificates that new capacity is
needed. A noisy but well-controlled world, a world with no useful action, a tunable mismatch and a genuine memory
shortfall can all produce persistent errors.

**First discriminator:** construct a matched development comparison of those cases within existing ground rules;
establish each case's opportunity with an explicitly informed comparator. Ask what the proposed local signal
can distinguish before choosing its threshold. Measure unnecessary growth and missed opportunities as well as
reward. A proof of indistinguishability under particular local observations would be a valuable negative result.

## 6. When do prediction and exploration improve control?

**Origin:** D44–D54, D63–D66. Sensory predictability, information about an unknown body, sensory–motor coupling,
and food gained are different quantities. Coupling helped balance but not tempo; a useful satiety count still
bought little improvement; the steering learner missed interacting choices with delayed consequences.

**First discriminator:** state the unknown and the decision it affects. For satiety, compare knowing the relevant
state with being able to act on it on the same lives. For steering, trace which delayed effects are absent from
the learner's evidence or representation; failed searches alone do not rule out their algorithm classes.
For exploration, compare evidence about the unknown at matched time and energy before comparing eventual return.
A richer sensor stream is useful only if it informs the decision; pulse count alone is not information gain.

## Parked questions and boundaries

These remain worthwhile but do not displace the investigations above without new evidence:

| question | why parked / when to return | record |
|---|---|---|
| Can existing eyes and actions support a better spatial model? | Failed observers do not prove sensory impossibility. Revisit when the representation audit identifies a spatial bottleneck; no body change without the user. | discrete notebook D21–D24, D41 |
| How much should a brain spend on learning early in life? | Last-third performance hides some acquisition cost. Report whole-life costs alongside the existing score before inventing a new optimisation objective. | discrete notebook D36, D56–D57 |
| Can a small number of explicit global signals coexist with scalable local operation? | First inventory actual dependencies and communication in question 2; changing the interface requires the user. | AGENTS, ground rules |
| Which retained mechanisms survive circuit implementation and its noise? | Apply physical checks at the relevant claim stage; do not reopen SPICE for every exploratory variant. | minimal notebook M14–M16; discrete notebook D7, D13–D14, D36 |
| Can the earlier recruiting neurons survive the later mismatch model? | That line's old results are scoped to its old simulator. Revisit if it supplies a needed mechanism. | experiments notebook E/H series |
| Can self-play, inheritance or environmental memory expand the challenge set? | These alter the research setting or previously restricted capabilities; they require a specific proposal and user decision. | historical questions and programme decisions |

The question of one rich module versus several simpler types remains open across all six investigations.
A candidate must earn its added functionality through an explanation and a discriminating result; familiarity
from biology, or a working hand-designed cure, does not by itself establish necessity or sufficiency.

- *Parked from D178 (2026-11-20).* Can a motor's own activity be tuned to a slow exploratory rate at all, given that the
  excitable unit's own firing begins at 15–23/s (an onset at a non-zero rate: a bistable or saddle-node-on-cycle type, per
  Arthur and Boahen's classification), or does useful exploration need a separate slow source? Not pursued.

- *Parked from D181 (2026-11-20).* At the neutral birth setting (P = V_TYP/2), the catalogue brain's cross path carries no single sensor pulse at all (a half-open gate leaves the motor short of zero). Does a neutral-born brain then behave like P = 0 until it learns, and does that matter for which tastes it gets? Not pursued.
