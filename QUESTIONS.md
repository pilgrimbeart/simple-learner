# Open questions

Current priorities after the 2026-11-17 investigations. This page owns unresolved questions and candidate discriminating
investigations; [PROGRAMME.md](PROGRAMME.md#conditional-programme) owns their order and hand-offs.
Answers belong in the relevant notebook, with evidence and limitations, and leave this list when resolved.
The [previous question list](lab/v/questions_before_review_2026-11-16.md) preserves origins, abandoned suggestions
and earlier answers; its many “next” instructions are historical, not a second work queue.

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
have been the earlier parent for 4874 words no living unit could build. **Next discriminator:**
[D92](discrete/NOTEBOOK.md#d92-ghost-children) finds those missing children no better a pool than actual
growth. **Next discriminator:** D77's extra-room benefit through selection/readout alternatives (does extra
room mainly change which forecasts are trusted?), not further retention or growth variants. Audit existing traces and
source/theory before defining another bounded observation. Keep alternative readout/knob explanations,
ancestry cost and displaced memory visible; retrospective winners are not a retention rule.
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
