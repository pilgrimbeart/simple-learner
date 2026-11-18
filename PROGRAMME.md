# The research programme

Current as of 2026-11-18, including [Jobs 1–3 and their decision, D88–D91](discrete/NOTEBOOK.md#d88-parent-census). The
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

D76 changes the immediate priority: the nominal capacity sets stream allowances rather than a total cap.
[D77](discrete/NOTEBOOK.md#d77-resource-observation) supplies observations that preserve behaviour and an
allowance ablation: extra room in ten event streams recovers much of the sequence improvement. Its remaining
gap to the larger design is unresolved. The sampled all-food lives grow nothing, but still run the broad
predictor repertoire. Counts describe software allocation and activity, not physical costs.

[D78](discrete/NOTEBOOK.md#d78-allocation-rules) shows that allocation matters under a real cap. The weight
contest beats equal allowance on fresh sequence seeds. Its timing comparison excludes harm greater than
the declared .10 margin on that rung; this is not general no-harm evidence. The smaller contest brain fails
the subsequent match to the original design. [D79](discrete/NOTEBOOK.md#d79-active-mixture) independently
reproduces those performance summaries, but corrects the explanation: family sums hid individual streams
that saved bits, and the trajectory reader included sleeping streams that did not enter the prediction.
Neither stored weight nor an active contribution alone establishes the benefit of additional memory.
Allocation, retention, readout learning and selection therefore remain interacting explanations. A new
marginal-contribution signal has not been shown necessary; another allocator is premature. D79's validated
reused pair weakens the early-usefulness explanation: omitting the non-event forecasts jointly reduces
current prediction loss, even though some individual early forecasts help. The learning-time scoring
defect is much more frequent under the contest. [D80–D81](discrete/NOTEBOOK.md#d80-scoring-replay) now separate
its direct prediction effect from feedback through allocation. Corrected scoring barely changes choices
on the frozen history, but changes weaker streams' relative weights. In a small closed-loop intervention,
memory and behaviour change, without demonstrating better performance. Correctness of credit is therefore
a dependency of the allocation comparison; it is not established as the explanation of its average gap.
[D82](discrete/NOTEBOOK.md#d82-issued-credit) now implements a coherent issued-forecast contract in lab
code. Ten reused development pairs demonstrate no improvement; the corrected contest remains below
the original allowances. Issued and taste-entry forecasts agree on these traces, so the remaining credit
comparison has no observed capture-timing confound. [D83](discrete/NOTEBOOK.md#d83-allocation-trace)
now separates two phenomena in one unchanged contest life: removal of current/issued speakers, and
new construction removed within the same taste before issuing any forecast. Some removing learns add
no unit, but most do. Neither current forecast disturbance nor unused-at-prediction construction
establishes lifetime value or zero causal effect. D84 finds many deleted contexts recur. D85 reconstructs their
readout opportunities without another life: some retained tallies beat their surviving stream, but
most recurring candidates lose to uniform prediction. This leaves confidence error as an alternative
to missing structure; neither selected unit comparisons nor their overlapping bit sums measure the
actual weighted mixture or the benefit of retention under a cap. D86 tests halfway confidence reduction
on the four historical D79 mixtures: both probability scores worsen in every full-life and last-third
window. D87 makes that same-history comparison: only 336/3653 recurring retained tallies beat the corrected
combined forecast; a supplied causal deletion-order prior loses 0.593 bits over 163 labels. This weakens
simple readout retention, but does not test whether retained units enable richer descendants to form.
[D88–D90](discrete/NOTEBOOK.md#d88-parent-census) then test that on the same history. Weak parents (one tally,
or not yet spoken) build 638 and 57 of 10236 children; half of all children never forecast at a taste, and
about one in five that do beats the combined forecast. Deleted units would have qualified as the earlier
parent for 5798 new words, 4874 of them with no living duplicate of that parent. The parts account is
weakened, not excluded; [D91](discrete/NOTEBOOK.md#d91-growth-decision) freezes one offline test of the
missing children; [D92](discrete/NOTEBOOK.md#d92-ghost-children) runs it (the user approved): ghosts beat the
combined forecast in 324/3103 scored cases against 716/8309 for actual children scored the same way, and a causal
prior over ghosts is level with native prediction (+0.016 bits). Memory as parts does not explain D77's gain on
present evidence; next is D91's fourth row.

## Next work: three small jobs for cheaper agents

**Status, 2026-11-18: Jobs 1–3 are complete** ([D88](discrete/NOTEBOOK.md#d88-parent-census),
[D89](discrete/NOTEBOOK.md#d89-child-prediction), [D90](discrete/NOTEBOOK.md#d90-missing-partner)); all checks
passed. The decision table was applied in [D91](discrete/NOTEBOOK.md#d91-growth-decision): the second and fourth
rows both partly apply (Job 3's "absent combinations" are absent by construction), so D91 freezes one offline
discriminator, ghost children scored against actual children under the same rule; [D92](discrete/NOTEBOOK.md#d92-ghost-children)
ran it and found no clear ghost advantage, so the fourth row applies. The job texts below are kept as the executed specification.

**Start with Job 1 below. Run Jobs 1 → 2 → 3 in order, then apply the decision table.** These are
bounded exploratory diagnostics, not a new brain design or a search for a higher score. The question is:
**does memory help by serving as parts for later combinations, even when its own predictions are weak?**
The opposite explanation is that extra room mostly preserves/repeats existing distinctions or changes
which predictors get selected. Neither explanation is established. D87 tested retained units with fixed
definitions; it never let them build children.

This section is the immediate work queue, prepared 2026-11-18; the broader conditional programme below supplies context.
The scripts named as **new deliverables do not exist yet**: each job includes writing its small script.
The present request is to prepare hand-offs, not to launch agents or simulations. A user can assign a
job by copying its block below together with the shared instructions. No job grants its worker permission
to spawn another agent. One worker/run at a time on this laptop.

### Shared instructions to paste with any job

> Work in `/home/pilgrim/git/simple-learner` on `main`. Read AGENTS.md, this work queue, and the
> discrete notebook's current state plus D84–D87. Do only the assigned job. Do not alter the brain,
> body, simulator, old scripts, old logs or predictions; do not open sealed tests; do not commit/push.
> Write the new script in `lab/`, JSON and terminal log in `lab/v/`, and append a short dated record
> to `discrete/NOTEBOOK.md` with problem, method, budget before work and findings/limits afterwards.
> Reuse read-only functions from the existing analysis scripts; do not call their simulation entry points.
> State inputs and hashes, current revision/dirty paths, command, seed/world/life length and denominators.
> Never fill a missing observation with an assumed value. If a check fails, preserve the failed log,
> identify the first mismatch, and stop dependent work. A timeout/error is not a negative result.
> Finish with one table, at most five sentences explaining it, and the exact files changed. No mechanism
> proposal, sweep, extra seed or new simulated life. Report counts/activity separately from physical costs.

**Common data, all already available on this machine:**

| file | use |
|---|---|
| `lab/v/future_evidence.pkl` | D84 raw definitions, ordered writes/births/removals/learns/predictions, native living/firing IDs, first-speaking positions and speaking counts |
| `lab/v/future_evidence.json` | identity checks and provenance for that trace |
| `lab/v/retained_mixture.json` | D87 actual combined probability at every prediction-event position; exact same trace identity |
| `lab/v/retained_prediction.pkl` | D85 one-tally candidates and retained counts/losses; not a full log of all native probabilities |
| `lab/v/allocation_trace.pkl` | D83 actual additions, parent IDs, removal reasons and native growth attempts, for cross-checks |
| `lab/future_evidence_analysis.py` | exact word signatures, history reconstruction and firing validation |
| `lab/retained_prediction.py` | native tally/speaker reconstruction, including the write→tidy→index-increment ordering |
| `lab/grownet.py` | actual `Net.learn`, `Net.fires`, `Net.says`, `_add`, `_remove` semantics |

All these detailed traces concern the **same corrected contest life**: sequence rung 17, seed 177000,
red first, 300 s, dt=.0025 s, total cap 3042. D77's historical small/large lives use a different
seed/design/credit protocol: never join their unit IDs or forecasts to this trace. The `.pkl` files
are intentionally untracked local artifacts; if missing on another machine, report the missing paths.
Do not launch replacement lives automatically.

Every new script should accept `--check` for tiny deterministic fixtures and `--run` for the saved-data
analysis. From the repository root, after writing the assigned script, use this command pattern,
substituting its exact basename (e.g. `growth_parent_census`):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/BASENAME.py --check
# Run only after --check passes; BASENAME is a placeholder, not an existing command.
timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/BASENAME.py --run > lab/v/BASENAME.log 2>&1
```

Allow 30 minutes implementation/checks plus 10 minutes reporting per job, and one analysis run of at
most 240 s. Each JSON must contain `success`, `checks`, `provenance`, `summary`, and any `rows_path`;
write `success: false` plus the first error on failure. Inspect the exit status and JSON success field. If over budget, leave a reproducible partial
result and say which step remains; do not silently sample fewer units or relax checks.

### Job 1 — Were weak or silent units actually used to build children?

**Assign:** “Implement the parent census specified here. New deliverables:
`lab/growth_parent_census.py`, `lab/v/growth_parent_census.json`, and its log.”

1. Verify the input identities/hashes. Build each stream's graph from initial definitions and ordered
   births/removals. A child has the two direct parents `u` and `v`; an ancestor is reached recursively.
   Use `(stream ID, unit ID)` as identity, never the unit ID alone.
2. At each actual birth, record both parents, their spans, their tallies at that moment and whether
   each had spoken in an actual prediction **before that birth**. Reconstruct counts in native order:
   the current lesson increments the firing parents before the child is initialized. These birth-time
   counts are structural observations, not forecasts to score against that same label.
3. Count grown parents with no previous speaking, with exactly one tally, and with two or more tallies.
   Keep fixed symbol parents separate. Count births using at least one such grown parent, unique
   parents, direct children and descendant spans. Report all births and each family; distinguish
   parent appearances (two per birth) from unique parents and births.
4. Validate that parents exist at birth, spans add, and every removal/remaining set reconciles.
   Match D84/D83's **10236 births, 9236 removals, 2042 initial and 3042 final units**. Do not remove
   fixed units from the total. Match reconstructed removal tallies as D85 did.
5. Fixtures: repeated parent `u==v`, a parent shared by two children, a cascade removal, and a child
   born before its parent first speaks. Do not count future speaking as prior speaking.

**Output table:** family; births; births using a grown parent that had not yet spoken; births using a
one-tally grown parent; distinct grown parents; median/max child span. Save the complete per-birth
rows in `lab/v/growth_parent_census.pkl` (ignored), keyed by `(stream, child ID)`, with parent IDs,
birth position/time, both parent tally pairs and their prior-speaking flags. Job 2 consumes this file.
The categories overlap; do not add them as disjoint categories.

**Interpretation:** positive counts show that “has not yet spoken” does not mean “unused
as a component.” One tally or silence alone does not establish weak predictive value. Zero counts narrow that explanation on this life. Neither proves the children help,
that deletion prevented them, or that extra capacity is worthwhile. Continue to Job 2 either way.

### Job 2 — Did those actual children ever add predictive evidence?

**Assign:** “Use Job 1's graph and the existing trace to score actual child speakers. New deliverables:
`lab/growth_child_prediction.py`, `lab/v/growth_child_prediction.json`, and its log.”

1. Reconstruct native living tallies and selected speakers at each recorded prediction using D85's
   semantics. Match **5883 predictions**, all native first-speaking/count records and all removal
   checkpoints. Join D87's combined forecast by prediction-event position, not nearest timestamp.
2. For each accepted taste, use the **last prediction before learning**. For every stream whose
   speaker is a grown child, record its issued probability and the combined probability. Score
   `log2(P_child(observed label) / P_combined(observed label))` before any update. Also score the
   uniform 1/2 reference. Each child gets at most one row per accepted taste, even if it has two
   qualifying parents. Do not score an unused child's hypothetical prediction in this job.
3. Group children by the parent state recorded **at birth** in Job 1: any grown parent not previously
   speaking; any one-tally grown parent; neither. The first two overlap. Also retain all children and
   each family as descriptive rows. Include children that never speak at an accepted taste as zero
   opportunities. Report full-life [0,300 s) and last-third [200,300 s) results separately, without
   choosing a winner group. Keep zero-opportunity children separate from scored numerical equalities.
4. Fixtures: an issued speaker deleted during the following taste; two predictions at the same time
   but different call positions; an outcome change that must not change its preceding probability.

**Output table:** group; born children; children scored at least once; child–taste pairs; unique accepted
tastes covered; numbers better/worse/numerically equal to combined; median per-child cumulative saving;
number beating both combined and uniform. State numeric tolerance (1e−10 bits), not a statistical tie.
For all children, report remaining life at birth in the fixed bins [0,30), [30,100), [100,200),
[200,300] seconds, with the number of later accepted tastes and zero-score children in each bin.
Late birth limits exposure; do not claim that it caused zero useful opportunities.

**Interpretation:** this checks actual component use plus actual issued evidence. The combined forecast
already includes the child's contribution; this is a descriptive relative score, not a leave-out causal
effect. A child losing to the mixture can still help it. Repeated tastes across streams and overlapping
ancestry prohibit independent-unit confidence intervals or calling their sum total learned bits.
Proceed to Job 3 to ask what deletion could prevent; do not build protection from this table.

### Job 3 — Could deleted units have supplied a missing parent later?

**Assign:** “Count narrowly defined missing-parent opportunities on the frozen history. New deliverables:
`lab/growth_missing_partner.py`, `lab/v/growth_missing_partner.json`, and its log.”

1. Use the same 5369 one-tally removals as D85. Keep their immutable word definitions offline; they
   never alter native counts, growth, random choices or actions. Exclude their deletion taste.
2. At each later native learning call in that unit's stream, find native deepest firing unit `v`
   from the recorded firing order, using the exact tie rule in `Net.learn`. Reconstruct its tally
   **after** the current label update. Continue only if it contains both labels (the native growth
   trigger) and a deepest unit exists. This is not a claim that capacity permits a birth.
3. Let `s` be `v`'s span and `i` the recorded learning index. Ask whether deleted unit `u` would fire
   at **i−s**, using the current recorded symbol history. That is where native growth looks for its
   earlier partner, not the current position i. Require `span(u)+s <= HIST//2` from the native source.
4. Form the hypothetical concatenated word `word(u)+word(v)`. Separately count whether an exact
   equivalent of `u` is already living and whether the concatenated word is already living. Deduplicate
   by `(stream, taste, concatenated word)` within each taste and by `(stream, word)` over the life.
   Preserve raw candidate counts too. Use the pre-learning living set (tallies just updated, before
   any removal inside this learn) for equivalence checks; label this stage explicitly. It is an
   opportunity reference, not the actual post-recycling partner pool. No random partner is drawn
   and no hypothetical child is born.
5. Report full remaining life and D84's 100 s horizon for deletions by 200 s. Count the deleted grown
   ancestors needed to evaluate each parent; their shared storage cannot be summed blindly.
   Fixtures must catch using i instead of i−s, reversed concatenation, duplicate associations,
   a missing ancestor, the maximum allowed span and same-taste exclusion.

**Output table:** family; eligible native contradiction calls; calls with any qualifying deleted parent;
unique potential child words; potential words absent from living memory; cases also lacking an equivalent
living parent; additional deleted ancestors required (distribution). Include zero cases and denominators.

**Interpretation:** this is only a possible construction path. It does not establish that the native
random draw would choose that parent, that a child would learn/predict well, or that keeping its ancestry
would beat whatever the cap forces out. Zero narrows only this earlier-partner route: a deleted unit
could instead become the deepest unit or enable a different later trajectory.

### After Jobs 1–3: a decision, not an automatic larger run

| observed result | next action |
|---|---|
| Any identity/reconstruction check fails | Diagnose the first discrepant event. Preserve failure output. Do not interpret scores or start another simulation. |
| Children use silent/weak parents, and Job 3 finds absent combinations | Write a bounded follow-up protocol to test those proposed combinations on later observations, scoring before learning and against the actual combined forecast. Freeze proposal/selection/prior rules before reading their future performance. This is the next candidate experiment, not yet an implementation instruction. |
| Children use such parents, but Job 3 finds no absent combinations | Audit the other growth route (deleted unit as deepest parent) and whether exact equivalents are already available. Do not infer that growth has no value from this restricted test. |
| Few/no such parents, or Job 2 shows mostly weak child evidence | Record the weak evidence for this account. Review D77's existing allowance ablation and selection/readout alternatives; do not keep adding retention variants. |
| A proposed combination later proves useful | Before any live retention test, identify a local signal that could select it without future knowledge and specify the same-cap displaced-memory comparator. Neither retrospective utility nor unlimited ghost storage is a design. |

The lead/reviewer owns this decision and any substantial new construction: check the relevant primary
literature and create the next notebook protocol with its own run budget. “Few” and “mostly weak”
are prompts for review, not predeclared statistical thresholds; the worker reports exact counts. The cheap workers deliver
measurements; they must not turn a positive count into a new allocator. **Do not repeat the D87 life,
run a parameter sweep or start a capacity curve as part of Jobs 1–3.**

## Conditional programme

The immediate priority is branch 2: D91's decision above. The numbers below identify the broader
investigation branches; they do not override that work queue. Their detailed questions and existing evidence are in [QUESTIONS.md](QUESTIONS.md).

| investigation | first useful work | decision after that work |
|---|---|---|
| **1. Explain economical use of noisy evidence** | D74 closes the first learned-sharing comparison with a qualified negative result. Before another variant, identify which cheap relation between representations is supplied or learned, its evidence cost, and the counterexamples it excludes. D75 supplies an exact-copy invariance check; approximate redundancy remains unresolved. | Retain a mechanism only with a stated prior and measured learning, state and communication costs. Correct scoring order before a new freeze. Keep inference separate from return on high-noise rungs; use an existing profitable condition for a control claim. Neither a choice vote nor fewer primitives follows from these results. |
| **2. Establish what scales and what it costs — immediate branch** | Jobs 1–3 are done (D88–D90). D92 ran D91's ghost-children test: no clear advantage. Next: review D77's allowance ablation and selection/readout alternatives (D91's fourth row); no further retention or growth variants. | Choose a discriminating observation of reachable representation versus retention/readout alternatives before constructing another allocator. Keep readout priors explicit and account for retained ancestors and displaced memory before a matched-cap intervention; no new rule is implied. Current deletion disturbance and selected correlations do not establish lifetime value. Keep cache/activity and categorical memory separate. |
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

**D87 hand-off.** Separate observing state, learning a readout, scoring a forecast, delivering unit
credit and allocating material. The issued-forecast lab contract is checked; historical production stays
unchanged. It is not a demonstrated performance cure, and the weight contest is not adopted. D84 establishes later activation
opportunities on one exact history. D85 reconstructs counts and forecasts, finding mixed retained-readout
value and a strong uniform control. D86 finds confidence reduction harms the historical combined
forecasts. D87 obtains the exact same-history reference and finds mostly worse retained tallies; a
supplied causal prior over them does not improve sequence prediction. Next examine formation of richer
combinations before another allocator. D83 traces same-taste
construction/removal as well as interrupted issued forecasts; protection is not automatically the cure.
Avoiding a birth and retaining a unit have different future costs. Immediate disturbance alone cannot
show inferior lifetime allocation: freeing a unit has an opportunity value.
The original noisy-readout question remains open. The user explicitly resumed lower-effort delegation
for D82–D83 and asked routine result processing/documentation to stay delegated; this is not standing
permission for new agents. A rule that encodes "event streams for sequences" or "clocks for timing"
would be a feature, not a mechanism. D87 completed its one neutral capture and offline comparison; no retention rule was selected. No new sensor, reward
change, protected-test opening or additional simulation is authorised by this completed phase; the next
bounded observation needs its own record.

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
