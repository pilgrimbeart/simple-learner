# The research programme

Current as of 2026-11-17, following the research review, D73–D76's evidence, selection and resource audits, and D77–D78's resource observation and allocation comparison. The
[goal and success criteria](README.md#the-goal-intelligence-that-scales) belong in the README;
[working rules](AGENTS.md#research-discipline) belong in AGENTS. This page owns the research direction
and conditional plan. The [abstract](ABSTRACT.md) is the short account of our present position.

## The question

Can a small repertoire of reusable components form a real-time robot brain that detects an improvable
shortfall, changes its own organisation using local information, and uses additional resources to learn
unfamiliar challenges economically during life?

The scientific result would explain **why** those components suffice, under which conditions they do not,
and how evidence, time, memory and communication constrain improvement. A working implementation supplies
evidence for that explanation. It does not establish the explanation by itself.

## Requirements, preferences and hypotheses

**Requirements.** In-life improvement, reusable components, explicit information paths, and scalable local
operation are fundamental. The designer may supply substantial innate structure, but must not supply a new
solution for each evaluation problem. The robot acts while learning; learning time and resource costs count.
The existing interface and experimental ground rules remain in [AGENTS.md](AGENTS.md).

**Preferences.** Keep the body and environment simple enough for fast experiments and causal understanding.
Prefer a small, quiet brain. These preferences do not establish that a particular minimal body is adequate,
or that the simplest implementation is the best learner. No body or signal change is authorised by this brief.
Previously authorised alternative bodies remain separate, explicitly identified experimental conditions.

**Open hypotheses, not design laws:**

- One rich component type, or a few simpler types plus local composition, may suffice. Neither has been selected.
- Prediction, exploration and action may share a useful learning mechanism; their objectives need not coincide.
- Coupling between sensory and motor signals may guide some adjustments. It worked for balance in the recorded
  experiments but failed as an objective for tempo. It is not a universal proxy for survival or understanding.
- Growth may resolve a representational shortfall; tuning, recycling or protecting existing memory may be cheaper.
  Persistent surprise alone does not distinguish missing capacity from noise, poor exploration or a bad learner.
- Body and brain complexity may trade off. A failed controller or observer does not prove that the body must change.

A useful negative result identifies the rules, evidence or resources under which a class of mechanisms fails.
An unexpected successful transfer may justify changing our picture of the problem. Neither outcome needs to
produce a new component to constitute progress.

## Where the evidence leaves us

The broad assessment is [D72 in the discrete notebook](discrete/NOTEBOOK.md#review-2026-11-16);
[D73](discrete/NOTEBOOK.md#d73-noisy-evidence) supplies the noisy-feedback information-path audit;
[D74–D76](discrete/NOTEBOOK.md#d74-learned-sharing) examine learning the readout, redundant predictors and resources.
Earlier recruitment demonstrates a restricted local repair under an older simulator. Small circuits demonstrate
specific learning and control abilities. Growing networks show useful capacity gains on some challenge families,
and the timing work shows the value of separating acquisition, tracking and expert selection. These results
motivate the goal; they do not yet establish economical general scaling on unfamiliar families.

Evidence survives the input restrictions and signed representation. Exact Bayesian grouping in D74, under
two priors of one model family, improves noisy-label loss without establishing a decision-accuracy gain
(its interval does not exclude most of the supplied grouping's advantage); a counterexample shows how
sharing can delay learning necessary distinctions. This does not establish that discovering a useful readout
is inherently difficult (dated correction in D74).
Numerical order and priors over structure matter. D75 additionally separates predictor multiplicity from
new evidence: initial and redistributed weights must both be conserved for exact copies to be neutral.
The reference's extra observations and negative expected meal gains on high-noise worlds still separate
inference success from control success.

D76 changes the immediate priority: the current nominal capacity is a stream-allocation setting, not a
total material cap. [D77](discrete/NOTEBOOK.md#d77-resource-observation) supplies the missing observations
with an observer proven not to change behaviour. On sequence rung 17, most of the high setting's gain
comes from room in the ten event streams (+.71 of the gap with 214 grown units, against +.81 with about 2200).
The equal-allowance allocator sends 85% of material, and most per-step work, to streams that save little.
All-food lives grow nothing. Communication with the mixer is fixed by the repertoire's breadth, not by P.
So the next change belongs in **resource allocation**. Neither the representation's content nor the readout's
learning rule is implicated by this evidence.

[D78](discrete/NOTEBOOK.md#d78-allocation-rules) compared allocation rules under an enforced total cap. The
rules matter a great deal: equal growth allowance is far worse than the design's accidental tilt toward
small-alphabet streams. A pairwise contest by mixture weight beats equal allowance on fresh seeds and does
no harm on timing, but it does not match the unchanged design and plateaus with material. The brain's
existing signals cannot rank its streams: mixture weight is winner-take-all (one stream holds about 90%,
the rest sit at the fixed-share floor), and bits saved over the default are negative everywhere. The missing
ingredient is a measure of each stream's *marginal* contribution, integrated over time. Weight trajectories
show clock, integrator and rhythm streams carrying three quarters of the mix for the first 100 s, before one
event stream takes over. A signal read from current weight is myopic. This is a credit-assignment question
for the allocator.

## Conditional programme

Work in this order unless a recorded observation changes the value of the next question. These are conditional
investigation branches. Their detailed questions and existing evidence are in [QUESTIONS.md](QUESTIONS.md).

| investigation | first useful work | decision after that work |
|---|---|---|
| **1. Explain economical use of noisy evidence** | D74 closes the first learned-sharing comparison with a qualified negative result. Before another variant, identify which cheap relation between representations is supplied or learned, its evidence cost, and the counterexamples it excludes. D75 supplies an exact-copy invariance check; approximate redundancy remains unresolved. | Retain a mechanism only with a stated prior and measured learning, state and communication costs. Correct scoring order before a new freeze. Keep inference separate from return on high-noise rungs; use an existing profitable condition for a control claim. Neither a choice vote nor fewer primitives follows from these results. |
| **2. Establish what scales and what it costs — immediate branch after D78** | D77 applied [D76's resource contract](discrete/NOTEBOOK.md#d76-resource-floor); [D78](discrete/NOTEBOOK.md#d78-allocation-rules) compared four allocation rules under an enforced cap (two new, so now diagnosis). Next: what makes a stream marginally useful? Trace mixture weights through life, and replay the mixture with floor-weight streams left out at chosen moments, before proposing a marginal-contribution signal. | Original performance figures have been reconciled; the old records cannot supply missing cost histories. Preserve their results and label P as an allocation setting. Compare growth, tuning, fixed capacity and recycling under an enforceable account before claiming economical scaling. No hardware result follows from a software unit count. |
| **3. Explain the timing transfer** | Map the successful acquisition and tracking stages onto the literature and their assumptions; contrast D23's short, ambiguous observations with D65–D68's longer streams. | Choose a test that separates a transferable timing mechanism from dependence on the designed period range, event detector or readout. Use development worlds; reserve new sealed tests for a frozen claim. |
| **4. Explain composition and retention** | Trace the combination-task gap and the A–B–A return experiments: what information is represented, overwritten, duplicated or discarded? | Distinguish failure to form a useful representation from failure to retain or select it. Test a single causal difference before adding a further layer or memory scheme. |
| **5. Test a generality claim** | Once a mechanism and its limits are understood, freeze the design, analysis, resource budget and claim. Check the evaluation protocol and test-set exposure record. | Evaluate on genuinely unfamiliar families and the relevant controls. Failures and non-compiling challenges remain visible. Opening a test spends its novelty; subsequent work on it is development. |

A branch ends when its question is answered, its present method cannot distinguish the alternatives, or its
predeclared effort limit is reached. Record which applies. Continue with the next useful authorised branch;
do not treat the end of one experiment as the end of the programme. If further work depends on a user decision,
state that decision and continue independent analysis, source checking or another queued question.

Each investigation gets an explicit compute/time envelope before a long run, chosen from its estimated value
and cost. There is no new fixed overnight quota. The one-job rule still applies. More runs are not the default
response to an unclear effect: first check whether the proposed additional evidence can resolve it.

**D78 hand-off.** The causal account now separates observing state, learning a readout, assigning influence
and allocating material. Adaptive grouping is not selected as the cure. Allocation is confirmed as a large
lever; the weight contest is the best capped rule so far but is not adopted (it fails the match to the
unchanged design). The next work is the marginal-usefulness diagnosis above. A rule that encodes "event
streams for sequences" or "clocks for timing" would be a feature, not a mechanism. Fixed-history tests do not establish return after changing actions. No new sensor, reward
change, sealed-test opening or agent is authorised by this hand-off. If changing the body/interface is
proposed, ask the user and continue the independent accounting and analytical branches meanwhile.

## Decisions and historical plans

**2026-11-16, user approved:** preserve the research goal; distinguish requirements, conjectures, observations
and explanations; revisit the top-level question at each investigation; use primary literature before substantial
construction; keep conditional work available during the user's absence; explain terminology inline; qualify
claims and retain negative results. This documentation change introduces no simulator change or experiment.

The previous [programme and decision table](lab/v/programme_before_review_2026-11-16.md#decisions-add-as-made)
are preserved verbatim as history. This brief supersedes their ordering of current phases, not their experiment
records or unrevoked user constraints. In particular:

- The old rule that every run must be a point on a scaling curve is replaced by the research discipline in AGENTS.
  Diagnosis, theory, calibration, replication and checking unexpected observations are legitimate progress.
- A high-confidence prediction is not a reason to forbid a needed check. Record why a predictable experiment is
  valuable, for example validating a simulator or testing the premise of a claimed explanation.
- Existing phase-specific physical-validation exceptions remain in force. Exploratory block-model results must
  be labelled as such; stronger physical claims require the checks applicable to that claim.
- No new independent agent is authorised. The earlier user decision requires asking before such a check.

The [review record](lab/v/review_2026-11-16.md) states what was inspected, what was not independently verified,
and how the research-agent literature informed this workflow. The workflow itself remains a hypothesis about
better research practice: assess whether it changes decisions and yields clearer explanations, not how many
forms, predictions or runs it produces.

## Sealed

This is an exposure register, not an invitation to inspect test contents. The historical hashes and construction
limitations remain in the [previous sealed register](lab/v/programme_before_review_2026-11-16.md#sealed).

| artifact | status at this review | permitted use |
|---|---|---|
| `lab/sealed/outside_set.md`, `lab/sealed/outside_set2.md` and `lab/v/outside_set2_reply.log` | Unopened in this review; reserved for the later claim. Earlier seal limitations are recorded in the historical register. | Do not read while developing the language, engine or cures. Preserve the claim-stage opening condition. |
| `lab/sealed/heldout_ladder.json` | Opened after the earlier freeze; results in D61. | Development evidence now; not a new held-out family. |
| `lab/sealed/heldout_ladder2.json` | Opened after the earlier freeze; results in D62, subsequent development in D66. | Development evidence now; its original seal was not enforced. |
| `lab/sealed/heldout_ladder3.json` | Opened after the 2026-11-15 freeze; results in D69, development in D70–D73 and recordings reused in D74–D76. | Development evidence now; the test author ran inside the enforced sandbox. |

For future tests, preserve the user's requirement for a same-senses reference learner that can close a meaningful
part of the gap, and increasing learnable structure rather than noise alone. State its supplied model family and
priors. Success of that reference demonstrates an opportunity under those assumptions; failure does not certify
impossibility. Certification must not silently discard awkward worlds after the candidate brain has failed them.

The historical stage-3 world split and seed ranges remain properties of that protocol, not a repository-wide
promise that those seeds are still unused. Before a new evaluation, check the logs and record actual exposure,
the frozen design and analysis, and the chosen development and evaluation sets. A seal is enforced through
`lab/sealed_agent.sh`, as required by AGENTS; a request for blindness is not enforcement.
